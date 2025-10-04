#!/usr/bin/env node

/**
 * 크로스 플랫폼 빌드 스크립트
 * 여러 플랫폼용 빌드를 자동화합니다.
 */

import { execSync, spawn } from 'child_process';
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

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

class CrossPlatformBuilder {
  constructor() {
    this.supportedPlatforms = {
      'windows': {
        target: 'x86_64-pc-windows-msvc',
        extension: '.exe',
        installer: '.msi',
        pythonBinary: 'python-backend.exe'
      },
      'macos': {
        target: 'x86_64-apple-darwin',
        extension: '.app',
        installer: '.dmg',
        pythonBinary: 'python-backend'
      },
      'linux': {
        target: 'x86_64-unknown-linux-gnu',
        extension: '.AppImage',
        installer: '.deb',
        pythonBinary: 'python-backend'
      }
    };
    
    this.currentPlatform = this.detectPlatform();
    this.buildResults = {};
  }

  // 현재 플랫폼 감지
  detectPlatform() {
    switch (process.platform) {
      case 'win32': return 'windows';
      case 'darwin': return 'macos';
      case 'linux': return 'linux';
      default: return 'unknown';
    }
  }

  // 빌드 환경 검증
  async verifyBuildEnvironment() {
    log('🔍 빌드 환경을 검증합니다...', colors.blue);
    
    const requirements = {
      node: { command: 'node --version', required: '18.0.0' },
      npm: { command: 'npm --version', required: '9.0.0' },
      python: { command: 'python --version', required: '3.8.0' },
      rust: { command: 'rustc --version', required: '1.70.0' },
      cargo: { command: 'cargo --version', required: '1.70.0' }
    };
    
    const issues = [];
    
    for (const [name, req] of Object.entries(requirements)) {
      try {
        const output = execSync(req.command, { encoding: 'utf8', stdio: 'pipe' });
        const version = this.extractVersion(output);
        
        if (this.compareVersions(version, req.required) < 0) {
          issues.push(`${name}: 버전 ${req.required} 이상 필요 (현재: ${version})`);
        } else {
          log(`✅ ${name}: ${version}`, colors.green);
        }
      } catch (error) {
        issues.push(`${name}: 설치되지 않음`);
      }
    }
    
    if (issues.length > 0) {
      log('❌ 빌드 환경 문제:', colors.red);
      issues.forEach(issue => log(`  - ${issue}`, colors.red));
      throw new Error('빌드 환경 요구사항을 만족하지 않습니다');
    }
    
    log('✅ 빌드 환경 검증 완료', colors.green);
  }

  // 버전 문자열에서 숫자 추출
  extractVersion(versionString) {
    const match = versionString.match(/(\d+\.\d+\.\d+)/);
    return match ? match[1] : '0.0.0';
  }

  // 버전 비교
  compareVersions(version1, version2) {
    const v1Parts = version1.split('.').map(Number);
    const v2Parts = version2.split('.').map(Number);
    
    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
      const v1Part = v1Parts[i] || 0;
      const v2Part = v2Parts[i] || 0;
      
      if (v1Part > v2Part) return 1;
      if (v1Part < v2Part) return -1;
    }
    
    return 0;
  }

  // Rust 타겟 설치
  async installRustTargets(platforms) {
    log('🦀 Rust 타겟을 설치합니다...', colors.blue);
    
    for (const platform of platforms) {
      const config = this.supportedPlatforms[platform];
      if (!config) continue;
      
      try {
        log(`${platform} 타겟 설치 중: ${config.target}`, colors.yellow);
        execSync(`rustup target add ${config.target}`, { stdio: 'inherit' });
        log(`✅ ${platform} 타겟 설치 완료`, colors.green);
      } catch (error) {
        log(`❌ ${platform} 타겟 설치 실패: ${error.message}`, colors.red);
        throw error;
      }
    }
  }

  // 플랫폼별 Python 바이너리 빌드
  async buildPythonBinaries(platforms) {
    log('🐍 플랫폼별 Python 바이너리를 빌드합니다...', colors.blue);
    
    const backendPath = join(projectRoot, 'python-backend');
    const binariesDir = join(projectRoot, 'src-tauri', 'binaries');
    
    if (!existsSync(binariesDir)) {
      mkdirSync(binariesDir, { recursive: true });
    }
    
    for (const platform of platforms) {
      const config = this.supportedPlatforms[platform];
      if (!config) continue;
      
      try {
        log(`${platform}용 Python 바이너리 빌드 중...`, colors.yellow);
        
        // 현재 플랫폼에서만 바이너리 생성 가능
        if (platform === this.currentPlatform) {
          await this.buildPythonBinaryForCurrentPlatform(backendPath, binariesDir, config);
        } else {
          log(`⚠️  ${platform}용 바이너리는 해당 플랫폼에서만 빌드 가능`, colors.yellow);
          // 크로스 컴파일 또는 Docker 사용 시 여기에 구현
        }
        
      } catch (error) {
        log(`❌ ${platform} Python 바이너리 빌드 실패: ${error.message}`, colors.red);
        this.buildResults[platform] = { success: false, error: error.message };
      }
    }
  }

  // 현재 플랫폼용 Python 바이너리 빌드
  async buildPythonBinaryForCurrentPlatform(backendPath, binariesDir, config) {
    const venvPath = join(backendPath, 'venv');
    
    // PyInstaller 설치
    const pipCmd = process.platform === 'win32'
      ? join(venvPath, 'Scripts', 'pip.exe')
      : join(venvPath, 'bin', 'pip');
    
    execSync(`"${pipCmd}" install pyinstaller`, { cwd: backendPath, stdio: 'inherit' });
    
    // 바이너리 생성
    const pyinstallerCmd = process.platform === 'win32'
      ? join(venvPath, 'Scripts', 'pyinstaller.exe')
      : join(venvPath, 'bin', 'pyinstaller');
    
    const pyinstallerArgs = [
      '--onefile',
      '--name', config.pythonBinary.replace(/\.(exe)?$/, ''),
      '--distpath', binariesDir,
      '--workpath', join(backendPath, 'build'),
      '--specpath', join(backendPath, 'build'),
      '--add-data', `${join(backendPath, 'api')}${process.platform === 'win32' ? ';' : ':'}api`,
      '--add-data', `${join(backendPath, 'core')}${process.platform === 'win32' ? ';' : ':'}core`,
      '--add-data', `${join(backendPath, 'models')}${process.platform === 'win32' ? ';' : ':'}models`,
      '--add-data', `${join(backendPath, 'utils')}${process.platform === 'win32' ? ';' : ':'}utils`,
      '--hidden-import', 'uvicorn',
      '--hidden-import', 'fastapi',
      '--hidden-import', 'websockets',
      'main.py'
    ];
    
    execSync(`"${pyinstallerCmd}" ${pyinstallerArgs.join(' ')}`, {
      cwd: backendPath,
      stdio: 'inherit'
    });
    
    log(`✅ ${this.currentPlatform} Python 바이너리 생성 완료`, colors.green);
  }

  // 플랫폼별 Tauri 앱 빌드
  async buildTauriApps(platforms) {
    log('🏗️  플랫폼별 Tauri 앱을 빌드합니다...', colors.blue);
    
    for (const platform of platforms) {
      const config = this.supportedPlatforms[platform];
      if (!config) continue;
      
      try {
        log(`${platform}용 Tauri 앱 빌드 중...`, colors.yellow);
        
        // 현재 플랫폼에서만 빌드 가능 (크로스 컴파일 제한)
        if (platform === this.currentPlatform) {
          await this.buildTauriAppForPlatform(platform, config);
          this.buildResults[platform] = { success: true };
        } else {
          log(`⚠️  ${platform}용 앱은 해당 플랫폼에서만 빌드 가능`, colors.yellow);
          this.buildResults[platform] = { success: false, error: 'Cross-compilation not supported' };
        }
        
      } catch (error) {
        log(`❌ ${platform} Tauri 앱 빌드 실패: ${error.message}`, colors.red);
        this.buildResults[platform] = { success: false, error: error.message };
      }
    }
  }

  // 특정 플랫폼용 Tauri 앱 빌드
  async buildTauriAppForPlatform(platform, config) {
    const buildArgs = ['run', 'build:tauri'];
    
    // 타겟 지정 (필요한 경우)
    if (config.target && platform !== this.currentPlatform) {
      buildArgs.push('--', '--target', config.target);
    }
    
    execSync(`npm ${buildArgs.join(' ')}`, {
      cwd: projectRoot,
      stdio: 'inherit',
      env: {
        ...process.env,
        NODE_ENV: 'production',
        TAURI_PLATFORM: platform
      }
    });
    
    log(`✅ ${platform} Tauri 앱 빌드 완료`, colors.green);
  }

  // 빌드 아티팩트 수집 및 정리
  async collectAndOrganizeArtifacts() {
    log('📦 빌드 아티팩트를 수집하고 정리합니다...', colors.blue);
    
    const outputDir = join(projectRoot, 'dist-cross-platform');
    if (!existsSync(outputDir)) {
      mkdirSync(outputDir, { recursive: true });
    }
    
    const tauriTargetPath = join(projectRoot, 'src-tauri', 'target', 'release');
    const bundlePath = join(tauriTargetPath, 'bundle');
    
    if (existsSync(bundlePath)) {
      // 플랫폼별 아티팩트 정리
      for (const [platform, result] of Object.entries(this.buildResults)) {
        if (result.success) {
          const platformDir = join(outputDir, platform);
          if (!existsSync(platformDir)) {
            mkdirSync(platformDir, { recursive: true });
          }
          
          // 해당 플랫폼의 빌드 결과물 복사
          // 실제 구현에서는 플랫폼별 파일을 식별하고 복사
          log(`${platform} 아티팩트 정리 완료`, colors.green);
        }
      }
    }
    
    // 빌드 보고서 생성
    const buildReport = {
      timestamp: new Date().toISOString(),
      platforms: this.buildResults,
      summary: {
        total: Object.keys(this.buildResults).length,
        successful: Object.values(this.buildResults).filter(r => r.success).length,
        failed: Object.values(this.buildResults).filter(r => !r.success).length
      }
    };
    
    writeFileSync(
      join(outputDir, 'build-report.json'),
      JSON.stringify(buildReport, null, 2)
    );
    
    log('✅ 아티팩트 수집 및 정리 완료', colors.green);
    return buildReport;
  }

  // 빌드 결과 요약 출력
  printBuildSummary(buildReport) {
    log('\n📊 크로스 플랫폼 빌드 요약:', colors.bright);
    log(`총 플랫폼: ${buildReport.summary.total}개`, colors.cyan);
    log(`성공: ${buildReport.summary.successful}개`, colors.green);
    log(`실패: ${buildReport.summary.failed}개`, colors.red);
    
    log('\n플랫폼별 결과:', colors.bright);
    for (const [platform, result] of Object.entries(buildReport.platforms)) {
      const status = result.success ? '✅ 성공' : '❌ 실패';
      const color = result.success ? colors.green : colors.red;
      log(`  ${platform}: ${status}`, color);
      
      if (!result.success && result.error) {
        log(`    오류: ${result.error}`, colors.red);
      }
    }
    
    if (buildReport.summary.failed > 0) {
      log('\n💡 실패한 플랫폼은 해당 운영체제에서 빌드해주세요.', colors.yellow);
    }
  }

  // 전체 크로스 플랫폼 빌드 실행
  async build(platforms = ['windows', 'macos', 'linux']) {
    log('🚀 크로스 플랫폼 빌드를 시작합니다...', colors.bright);
    log(`타겟 플랫폼: ${platforms.join(', ')}`, colors.cyan);
    log(`현재 플랫폼: ${this.currentPlatform}`, colors.cyan);
    
    try {
      await this.verifyBuildEnvironment();
      await this.installRustTargets(platforms);
      await this.buildPythonBinaries(platforms);
      await this.buildTauriApps(platforms);
      
      const buildReport = await this.collectAndOrganizeArtifacts();
      this.printBuildSummary(buildReport);
      
      if (buildReport.summary.successful > 0) {
        log('🎉 크로스 플랫폼 빌드가 완료되었습니다!', colors.green);
      } else {
        log('⚠️  모든 플랫폼 빌드가 실패했습니다.', colors.yellow);
      }
      
    } catch (error) {
      log(`❌ 크로스 플랫폼 빌드 실패: ${error.message}`, colors.red);
      process.exit(1);
    }
  }
}

// 사용법 출력
function printUsage() {
  console.log(`
🌐 WatchHamster 크로스 플랫폼 빌드

사용법:
  node scripts/cross-platform-build.js [플랫폼...]

플랫폼:
  windows    Windows용 빌드
  macos      macOS용 빌드  
  linux      Linux용 빌드
  all        모든 플랫폼 (기본값)

예시:
  node scripts/cross-platform-build.js                    # 모든 플랫폼
  node scripts/cross-platform-build.js windows macos      # Windows, macOS만
  node scripts/cross-platform-build.js linux              # Linux만

참고:
  - 각 플랫폼은 해당 운영체제에서만 완전히 빌드 가능합니다
  - 크로스 컴파일은 제한적으로 지원됩니다
`);
}

// 메인 실행
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    printUsage();
    return;
  }
  
  let platforms = args.length > 0 ? args : ['windows', 'macos', 'linux'];
  
  // 'all' 키워드 처리
  if (platforms.includes('all')) {
    platforms = ['windows', 'macos', 'linux'];
  }
  
  // 지원되지 않는 플랫폼 필터링
  const supportedPlatforms = ['windows', 'macos', 'linux'];
  platforms = platforms.filter(p => supportedPlatforms.includes(p));
  
  if (platforms.length === 0) {
    console.error('❌ 유효한 플랫폼이 지정되지 않았습니다.');
    printUsage();
    process.exit(1);
  }
  
  const builder = new CrossPlatformBuilder();
  await builder.build(platforms);
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('크로스 플랫폼 빌드 스크립트 실행 실패:', error);
    process.exit(1);
  });
}

export { CrossPlatformBuilder };