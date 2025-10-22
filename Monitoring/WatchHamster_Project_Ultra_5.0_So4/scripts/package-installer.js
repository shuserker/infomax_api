#!/usr/bin/env node

/**
 * 설치 패키지 생성 스크립트
 * 플랫폼별 설치 패키지를 생성하고 배포 준비를 합니다.
 */

import { execSync, spawn } from 'child_process';
import { existsSync, mkdirSync, copyFileSync, writeFileSync, readFileSync, rmSync, readdirSync, statSync } from 'fs';
import { join, dirname, basename, extname } from 'path';
import { fileURLToPath } from 'url';
import { createHash } from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

// 색상 출력을 위한 유틸리티
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${color}[${timestamp}] ${message}${colors.reset}`);
}

function logStep(step, message) {
  log(`[${step}] ${message}`, colors.cyan);
}

function logSuccess(message) {
  log(`✅ ${message}`, colors.green);
}

function logError(message) {
  log(`❌ ${message}`, colors.red);
}

function logWarning(message) {
  log(`⚠️  ${message}`, colors.yellow);
}

class PackageInstaller {
  constructor(options = {}) {
    this.version = this.getVersion();
    this.platform = process.platform;
    this.arch = process.arch;
    this.outputDir = join(projectRoot, 'dist-packages');
    this.releaseDir = join(projectRoot, 'src-tauri', 'target', 'release');
    this.bundleDir = join(this.releaseDir, 'bundle');
    
    this.packageInfo = {
      name: 'WatchHamster',
      displayName: 'WatchHamster - POSCO 시스템 모니터링',
      version: this.version,
      description: 'POSCO 시스템의 성능 모니터링, 서비스 관리, 배포 자동화를 위한 현대적인 GUI 도구',
      author: 'POSCO',
      license: 'Proprietary',
      homepage: 'https://github.com/posco/watchhamster',
      repository: 'https://github.com/posco/watchhamster.git'
    };
    
    this.platforms = {
      win32: {
        name: 'Windows',
        extensions: ['.msi', '.exe'],
        installer: 'msi',
        executable: 'watchhamster-tauri.exe'
      },
      darwin: {
        name: 'macOS',
        extensions: ['.dmg', '.app'],
        installer: 'dmg',
        executable: 'WatchHamster.app'
      },
      linux: {
        name: 'Linux',
        extensions: ['.deb', '.AppImage'],
        installer: 'deb',
        executable: 'watchhamster-tauri'
      }
    };
  }

  // 버전 정보 가져오기
  getVersion() {
    try {
      const packageJson = JSON.parse(readFileSync(join(projectRoot, 'package.json'), 'utf8'));
      return packageJson.version;
    } catch {
      return '1.0.0';
    }
  }

  // 패키지 생성 환경 준비
  async preparePackagingEnvironment() {
    logStep('1/7', '패키지 생성 환경을 준비합니다...');
    
    // 출력 디렉토리 생성
    if (existsSync(this.outputDir)) {
      rmSync(this.outputDir, { recursive: true, force: true });
    }
    mkdirSync(this.outputDir, { recursive: true });
    
    // 플랫폼별 디렉토리 생성
    for (const [platform, config] of Object.entries(this.platforms)) {
      const platformDir = join(this.outputDir, platform);
      mkdirSync(platformDir, { recursive: true });
    }
    
    logSuccess('패키지 생성 환경 준비 완료');
  }

  // 빌드 아티팩트 확인
  async verifyBuildArtifacts() {
    logStep('2/7', '빌드 아티팩트를 확인합니다...');
    
    if (!existsSync(this.bundleDir)) {
      throw new Error('빌드 아티팩트를 찾을 수 없습니다. 먼저 빌드를 실행해주세요.');
    }
    
    const artifacts = this.findBuildArtifacts();
    
    if (artifacts.length === 0) {
      throw new Error('유효한 빌드 아티팩트를 찾을 수 없습니다.');
    }
    
    log(`발견된 아티팩트: ${artifacts.length}개`, colors.cyan);
    artifacts.forEach(artifact => {
      log(`  - ${artifact.name} (${(artifact.size / 1024 / 1024).toFixed(2)} MB)`, colors.white);
    });
    
    logSuccess('빌드 아티팩트 확인 완료');
    return artifacts;
  }

  // 빌드 아티팩트 찾기
  findBuildArtifacts() {
    const artifacts = [];
    
    if (!existsSync(this.bundleDir)) {
      return artifacts;
    }
    
    const scanDirectory = (dir) => {
      const items = readdirSync(dir);
      
      for (const item of items) {
        const itemPath = join(dir, item);
        const stat = statSync(itemPath);
        
        if (stat.isDirectory()) {
          scanDirectory(itemPath);
        } else {
          const ext = extname(item).toLowerCase();
          const platformConfig = this.platforms[this.platform];
          
          if (platformConfig && platformConfig.extensions.includes(ext)) {
            artifacts.push({
              name: item,
              path: itemPath,
              size: stat.size,
              platform: this.platform,
              type: ext.slice(1)
            });
          }
        }
      }
    };
    
    scanDirectory(this.bundleDir);
    return artifacts;
  }

  // 설치 패키지 메타데이터 생성
  async generatePackageMetadata() {
    logStep('3/7', '패키지 메타데이터를 생성합니다...');
    
    const metadata = {
      ...this.packageInfo,
      platform: this.platform,
      arch: this.arch,
      buildDate: new Date().toISOString(),
      
      // 시스템 요구사항
      systemRequirements: {
        windows: {
          os: 'Windows 10 이상',
          memory: '4GB RAM',
          disk: '500MB 여유 공간',
          additional: 'Python 3.8 이상 (자동 설치됨)'
        },
        darwin: {
          os: 'macOS 10.13 이상',
          memory: '4GB RAM',
          disk: '500MB 여유 공간',
          additional: 'Python 3.8 이상 (자동 설치됨)'
        },
        linux: {
          os: 'Ubuntu 18.04 이상 또는 동등한 배포판',
          memory: '4GB RAM',
          disk: '500MB 여유 공간',
          additional: 'Python 3.8 이상'
        }
      },
      
      // 기능 목록
      features: [
        '실시간 시스템 성능 모니터링',
        'POSCO 뉴스 시스템 관리',
        'GitHub Pages 배포 자동화',
        '웹훅 기반 알림 시스템',
        '로그 뷰어 및 분석',
        '다크/라이트 테마 지원',
        '크로스 플랫폼 지원'
      ],
      
      // 변경사항 (최신 버전)
      changelog: {
        [this.version]: {
          date: new Date().toISOString().split('T')[0],
          changes: [
            'Tkinter에서 Tauri + React로 완전 재구성',
            '현대적인 UI/UX 디자인 적용',
            '성능 및 메모리 사용량 최적화',
            '실시간 WebSocket 통신 구현',
            '향상된 로그 뷰어 및 필터링',
            '자동 업데이트 시스템 추가'
          ]
        }
      }
    };
    
    // 메타데이터 파일 저장
    const metadataPath = join(this.outputDir, 'package-metadata.json');
    writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    
    logSuccess('패키지 메타데이터 생성 완료');
    return metadata;
  }

  // Windows 설치 패키지 생성
  async createWindowsInstaller(artifacts) {
    if (this.platform !== 'win32') {
      logWarning('Windows 설치 패키지는 Windows에서만 생성 가능합니다');
      return;
    }
    
    logStep('4/7', 'Windows 설치 패키지를 생성합니다...');
    
    const windowsArtifacts = artifacts.filter(a => a.platform === 'win32');
    const platformDir = join(this.outputDir, 'win32');
    
    for (const artifact of windowsArtifacts) {
      // MSI 파일 복사
      if (artifact.type === 'msi') {
        const targetPath = join(platformDir, `WatchHamster-${this.version}-x64.msi`);
        copyFileSync(artifact.path, targetPath);
        
        // 체크섬 생성
        const checksum = this.calculateFileChecksum(targetPath);
        writeFileSync(`${targetPath}.sha256`, checksum);
        
        log(`Windows MSI 패키지 생성: ${basename(targetPath)}`, colors.green);
      }
    }
    
    // 설치 스크립트 생성
    await this.createWindowsInstallScript(platformDir);
    
    logSuccess('Windows 설치 패키지 생성 완료');
  }

  // Windows 설치 스크립트 생성
  async createWindowsInstallScript(platformDir) {
    const installScript = `@echo off
REM WatchHamster 자동 설치 스크립트

echo ========================================
echo WatchHamster ${this.version} 설치
echo ========================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 관리자 권한이 확인되었습니다.
) else (
    echo 이 스크립트는 관리자 권한이 필요합니다.
    echo 마우스 우클릭으로 "관리자 권한으로 실행"을 선택해주세요.
    pause
    exit /b 1
)

REM Python 설치 확인
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python이 이미 설치되어 있습니다.
) else (
    echo Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요: https://python.org
    pause
    exit /b 1
)

REM MSI 설치 실행
echo WatchHamster를 설치합니다...
for %%f in (WatchHamster-*.msi) do (
    msiexec /i "%%f" /quiet /norestart
    if %errorLevel% == 0 (
        echo 설치가 완료되었습니다!
    ) else (
        echo 설치 중 오류가 발생했습니다.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 설치 완료!
echo ========================================
echo WatchHamster가 성공적으로 설치되었습니다.
echo 시작 메뉴에서 WatchHamster를 실행할 수 있습니다.
echo.
pause
`;

    writeFileSync(join(platformDir, 'install.bat'), installScript);
  }

  // macOS 설치 패키지 생성
  async createMacOSInstaller(artifacts) {
    if (this.platform !== 'darwin') {
      logWarning('macOS 설치 패키지는 macOS에서만 생성 가능합니다');
      return;
    }
    
    logStep('5/7', 'macOS 설치 패키지를 생성합니다...');
    
    const macosArtifacts = artifacts.filter(a => a.platform === 'darwin');
    const platformDir = join(this.outputDir, 'darwin');
    
    for (const artifact of macosArtifacts) {
      // DMG 파일 복사
      if (artifact.type === 'dmg') {
        const targetPath = join(platformDir, `WatchHamster-${this.version}-universal.dmg`);
        copyFileSync(artifact.path, targetPath);
        
        // 체크섬 생성
        const checksum = this.calculateFileChecksum(targetPath);
        writeFileSync(`${targetPath}.sha256`, checksum);
        
        log(`macOS DMG 패키지 생성: ${basename(targetPath)}`, colors.green);
      }
    }
    
    // 설치 스크립트 생성
    await this.createMacOSInstallScript(platformDir);
    
    logSuccess('macOS 설치 패키지 생성 완료');
  }

  // macOS 설치 스크립트 생성
  async createMacOSInstallScript(platformDir) {
    const installScript = `#!/bin/bash

# WatchHamster 자동 설치 스크립트

echo "========================================"
echo "WatchHamster ${this.version} 설치"
echo "========================================"
echo

# Python 설치 확인
if command -v python3 &> /dev/null; then
    echo "Python3이 이미 설치되어 있습니다."
else
    echo "Python3이 설치되어 있지 않습니다."
    echo "Homebrew를 통해 Python을 설치하거나 python.org에서 다운로드해주세요."
    exit 1
fi

# DMG 마운트 및 설치
echo "WatchHamster를 설치합니다..."
for dmg_file in WatchHamster-*.dmg; do
    if [ -f "$dmg_file" ]; then
        echo "DMG 파일을 마운트합니다: $dmg_file"
        
        # DMG 마운트
        mount_point=$(hdiutil attach "$dmg_file" | grep "/Volumes" | awk '{print $3}')
        
        if [ -n "$mount_point" ]; then
            echo "애플리케이션을 복사합니다..."
            cp -R "$mount_point/WatchHamster.app" /Applications/
            
            # DMG 언마운트
            hdiutil detach "$mount_point"
            
            echo "설치가 완료되었습니다!"
            echo "Applications 폴더에서 WatchHamster를 실행할 수 있습니다."
        else
            echo "DMG 마운트에 실패했습니다."
            exit 1
        fi
    fi
done

echo
echo "========================================"
echo "설치 완료!"
echo "========================================"
echo "WatchHamster가 성공적으로 설치되었습니다."
echo "Launchpad 또는 Applications 폴더에서 실행할 수 있습니다."
echo
`;

    const scriptPath = join(platformDir, 'install.sh');
    writeFileSync(scriptPath, installScript);
    
    // 실행 권한 부여
    try {
      execSync(`chmod +x "${scriptPath}"`);
    } catch (error) {
      logWarning('설치 스크립트 권한 설정 실패');
    }
  }

  // Linux 설치 패키지 생성
  async createLinuxInstaller(artifacts) {
    if (this.platform !== 'linux') {
      logWarning('Linux 설치 패키지는 Linux에서만 생성 가능합니다');
      return;
    }
    
    logStep('6/7', 'Linux 설치 패키지를 생성합니다...');
    
    const linuxArtifacts = artifacts.filter(a => a.platform === 'linux');
    const platformDir = join(this.outputDir, 'linux');
    
    for (const artifact of linuxArtifacts) {
      // DEB 또는 AppImage 파일 복사
      if (artifact.type === 'deb' || artifact.type === 'appimage') {
        const extension = artifact.type === 'appimage' ? 'AppImage' : 'deb';
        const targetPath = join(platformDir, `watchhamster-${this.version}-amd64.${extension}`);
        copyFileSync(artifact.path, targetPath);
        
        // 체크섬 생성
        const checksum = this.calculateFileChecksum(targetPath);
        writeFileSync(`${targetPath}.sha256`, checksum);
        
        log(`Linux ${extension.toUpperCase()} 패키지 생성: ${basename(targetPath)}`, colors.green);
      }
    }
    
    // 설치 스크립트 생성
    await this.createLinuxInstallScript(platformDir);
    
    logSuccess('Linux 설치 패키지 생성 완료');
  }

  // Linux 설치 스크립트 생성
  async createLinuxInstallScript(platformDir) {
    const installScript = `#!/bin/bash

# WatchHamster 자동 설치 스크립트

echo "========================================"
echo "WatchHamster ${this.version} 설치"
echo "========================================"
echo

# 루트 권한 확인
if [ "$EUID" -ne 0 ]; then
    echo "이 스크립트는 루트 권한이 필요합니다."
    echo "sudo ./install.sh 로 실행해주세요."
    exit 1
fi

# Python 설치 확인
if command -v python3 &> /dev/null; then
    echo "Python3이 이미 설치되어 있습니다."
else
    echo "Python3을 설치합니다..."
    apt-get update
    apt-get install -y python3 python3-pip
fi

# DEB 패키지 설치
echo "WatchHamster를 설치합니다..."
for deb_file in watchhamster-*.deb; do
    if [ -f "$deb_file" ]; then
        echo "DEB 패키지를 설치합니다: $deb_file"
        dpkg -i "$deb_file"
        
        # 의존성 문제 해결
        apt-get install -f -y
        
        echo "설치가 완료되었습니다!"
    fi
done

# AppImage 설치
for appimage_file in watchhamster-*.AppImage; do
    if [ -f "$appimage_file" ]; then
        echo "AppImage를 설치합니다: $appimage_file"
        
        # AppImage를 /opt로 복사
        cp "$appimage_file" /opt/watchhamster.AppImage
        chmod +x /opt/watchhamster.AppImage
        
        # 데스크톱 엔트리 생성
        cat > /usr/share/applications/watchhamster.desktop << EOF
[Desktop Entry]
Name=WatchHamster
Comment=POSCO 시스템 모니터링 도구
Exec=/opt/watchhamster.AppImage
Icon=watchhamster
Terminal=false
Type=Application
Categories=Development;System;
EOF
        
        echo "AppImage 설치가 완료되었습니다!"
    fi
done

echo
echo "========================================"
echo "설치 완료!"
echo "========================================"
echo "WatchHamster가 성공적으로 설치되었습니다."
echo "애플리케이션 메뉴에서 실행할 수 있습니다."
echo
`;

    const scriptPath = join(platformDir, 'install.sh');
    writeFileSync(scriptPath, installScript);
    
    // 실행 권한 부여
    try {
      execSync(`chmod +x "${scriptPath}"`);
    } catch (error) {
      logWarning('설치 스크립트 권한 설정 실패');
    }
  }

  // 파일 체크섬 계산
  calculateFileChecksum(filePath) {
    try {
      const content = readFileSync(filePath);
      return createHash('sha256').update(content).digest('hex');
    } catch (error) {
      logWarning(`체크섬 계산 실패: ${error.message}`);
      return null;
    }
  }

  // 배포 매니페스트 생성
  async generateReleaseManifest() {
    logStep('7/7', '배포 매니페스트를 생성합니다...');
    
    const manifest = {
      version: this.version,
      releaseDate: new Date().toISOString(),
      packages: {},
      checksums: {},
      downloadUrls: {},
      systemRequirements: {
        windows: 'Windows 10 이상',
        macos: 'macOS 10.13 이상',
        linux: 'Ubuntu 18.04 이상'
      }
    };
    
    // 각 플랫폼별 패키지 정보 수집
    for (const platform of Object.keys(this.platforms)) {
      const platformDir = join(this.outputDir, platform);
      
      if (existsSync(platformDir)) {
        const packages = [];
        const files = readdirSync(platformDir);
        
        for (const file of files) {
          const filePath = join(platformDir, file);
          const stat = statSync(filePath);
          
          if (stat.isFile() && !file.endsWith('.sha256')) {
            const checksumFile = `${filePath}.sha256`;
            const checksum = existsSync(checksumFile) 
              ? readFileSync(checksumFile, 'utf8').trim()
              : this.calculateFileChecksum(filePath);
            
            packages.push({
              name: file,
              size: stat.size,
              checksum: checksum,
              downloadUrl: `https://releases.example.com/watchhamster/${this.version}/${platform}/${file}`
            });
          }
        }
        
        if (packages.length > 0) {
          manifest.packages[platform] = packages;
        }
      }
    }
    
    // 매니페스트 파일 저장
    const manifestPath = join(this.outputDir, 'release-manifest.json');
    writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
    
    // 사람이 읽기 쉬운 릴리스 노트 생성
    await this.generateReleaseNotes(manifest);
    
    logSuccess('배포 매니페스트 생성 완료');
    return manifest;
  }

  // 릴리스 노트 생성
  async generateReleaseNotes(manifest) {
    const releaseNotes = `# WatchHamster ${this.version} 릴리스

## 📅 릴리스 날짜
${new Date().toLocaleDateString('ko-KR')}

## 📋 주요 변경사항
- Tkinter에서 Tauri + React로 완전 재구성
- 현대적인 UI/UX 디자인 적용  
- 성능 및 메모리 사용량 최적화
- 실시간 WebSocket 통신 구현
- 향상된 로그 뷰어 및 필터링
- 자동 업데이트 시스템 추가

## 💾 다운로드

### Windows
${manifest.packages.win32 ? manifest.packages.win32.map(pkg => 
  `- [${pkg.name}](${pkg.downloadUrl}) (${(pkg.size / 1024 / 1024).toFixed(2)} MB)`
).join('\n') : '- Windows 패키지 없음'}

### macOS  
${manifest.packages.darwin ? manifest.packages.darwin.map(pkg => 
  `- [${pkg.name}](${pkg.downloadUrl}) (${(pkg.size / 1024 / 1024).toFixed(2)} MB)`
).join('\n') : '- macOS 패키지 없음'}

### Linux
${manifest.packages.linux ? manifest.packages.linux.map(pkg => 
  `- [${pkg.name}](${pkg.downloadUrl}) (${(pkg.size / 1024 / 1024).toFixed(2)} MB)`
).join('\n') : '- Linux 패키지 없음'}

## 🔧 시스템 요구사항
- **Windows**: Windows 10 이상, 4GB RAM, 500MB 여유 공간
- **macOS**: macOS 10.13 이상, 4GB RAM, 500MB 여유 공간  
- **Linux**: Ubuntu 18.04 이상, 4GB RAM, 500MB 여유 공간
- **공통**: Python 3.8 이상 (자동 설치됨)

## 📦 설치 방법

### Windows
1. \`WatchHamster-${this.version}-x64.msi\` 다운로드
2. 관리자 권한으로 실행
3. 설치 마법사 따라 진행

### macOS
1. \`WatchHamster-${this.version}-universal.dmg\` 다운로드
2. DMG 파일 마운트
3. WatchHamster.app을 Applications 폴더로 드래그

### Linux
1. DEB 패키지: \`sudo dpkg -i watchhamster-${this.version}-amd64.deb\`
2. AppImage: 다운로드 후 실행 권한 부여하여 실행

## 🔐 체크섬 검증
다운로드한 파일의 무결성을 확인하려면 SHA256 체크섬을 비교하세요.
각 패키지와 함께 제공되는 .sha256 파일을 참조하세요.

## 🐛 알려진 문제
- 첫 실행 시 방화벽 경고가 표시될 수 있습니다 (정상)
- macOS에서 "개발자를 확인할 수 없음" 경고 시 시스템 환경설정에서 허용 필요

## 📞 지원
문제가 발생하면 GitHub Issues에 보고해주세요.
`;

    writeFileSync(join(this.outputDir, 'RELEASE_NOTES.md'), releaseNotes);
  }

  // 패키지 생성 요약 출력
  printPackagingSummary() {
    log('\n📦 패키지 생성 요약:', colors.bright);
    log(`버전: ${this.version}`, colors.cyan);
    log(`플랫폼: ${this.platforms[this.platform]?.name || this.platform}`, colors.cyan);
    
    // 생성된 패키지 목록
    const platforms = readdirSync(this.outputDir).filter(item => {
      const itemPath = join(this.outputDir, item);
      return statSync(itemPath).isDirectory();
    });
    
    log(`생성된 플랫폼 패키지: ${platforms.length}개`, colors.cyan);
    
    for (const platform of platforms) {
      const platformDir = join(this.outputDir, platform);
      const files = readdirSync(platformDir).filter(file => 
        !file.endsWith('.sha256') && statSync(join(platformDir, file)).isFile()
      );
      
      log(`  ${platform}: ${files.length}개 파일`, colors.green);
      files.forEach(file => {
        const filePath = join(platformDir, file);
        const size = statSync(filePath).size;
        log(`    - ${file} (${(size / 1024 / 1024).toFixed(2)} MB)`, colors.white);
      });
    }
    
    log(`\n출력 디렉토리: ${this.outputDir}`, colors.green);
  }

  // 전체 패키지 생성 프로세스 실행
  async createPackages() {
    log('📦 설치 패키지 생성을 시작합니다...', colors.bright);
    
    try {
      await this.preparePackagingEnvironment();
      const artifacts = await this.verifyBuildArtifacts();
      await this.generatePackageMetadata();
      
      // 플랫폼별 패키지 생성
      await this.createWindowsInstaller(artifacts);
      await this.createMacOSInstaller(artifacts);
      await this.createLinuxInstaller(artifacts);
      
      await this.generateReleaseManifest();
      
      this.printPackagingSummary();
      
      log('🎉 설치 패키지 생성이 완료되었습니다!', colors.green);
      
    } catch (error) {
      logError(`패키지 생성 실패: ${error.message}`);
      process.exit(1);
    }
  }
}

// 사용법 출력
function printUsage() {
  console.log(`
📦 WatchHamster 설치 패키지 생성

사용법:
  node scripts/package-installer.js [옵션]

옵션:
  --help    이 도움말 출력

참고:
  - 먼저 빌드를 완료해야 합니다: npm run build:tauri
  - 각 플랫폼에서 해당 플랫폼용 패키지만 생성됩니다
  - 크로스 플랫폼 패키지 생성은 지원되지 않습니다

예시:
  npm run build:tauri                    # 먼저 빌드 실행
  node scripts/package-installer.js     # 패키지 생성
`);
}

// 메인 실행
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    printUsage();
    return;
  }
  
  const packager = new PackageInstaller();
  await packager.createPackages();
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('패키지 생성 스크립트 실행 실패:', error);
    process.exit(1);
  });
}

export { PackageInstaller };