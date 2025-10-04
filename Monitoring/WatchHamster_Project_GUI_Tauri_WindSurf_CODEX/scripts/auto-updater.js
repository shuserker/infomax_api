#!/usr/bin/env node

/**
 * 자동 업데이트 시스템
 * 애플리케이션의 자동 업데이트 기능을 관리합니다.
 */

import { execSync } from 'child_process';
import { existsSync, writeFileSync, readFileSync, mkdirSync } from 'fs';
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

class AutoUpdater {
  constructor() {
    this.currentVersion = this.getCurrentVersion();
    this.updateServerUrl = 'https://releases.example.com/watchhamster';
    this.updateConfigPath = join(projectRoot, 'update-config.json');
    this.updateCachePath = join(projectRoot, '.update-cache');
    
    this.updateConfig = {
      enabled: true,
      checkInterval: 24 * 60 * 60 * 1000, // 24시간
      autoDownload: true,
      autoInstall: false, // 사용자 확인 필요
      channel: 'stable', // stable, beta, alpha
      allowPrerelease: false,
      updateServerUrl: this.updateServerUrl,
      lastCheck: null,
      skipVersion: null
    };
  }

  // 현재 버전 가져오기
  getCurrentVersion() {
    try {
      const packageJson = JSON.parse(readFileSync(join(projectRoot, 'package.json'), 'utf8'));
      return packageJson.version;
    } catch {
      return '1.0.0';
    }
  }

  // 업데이트 설정 로드
  loadUpdateConfig() {
    if (existsSync(this.updateConfigPath)) {
      try {
        const config = JSON.parse(readFileSync(this.updateConfigPath, 'utf8'));
        this.updateConfig = { ...this.updateConfig, ...config };
      } catch (error) {
        log(`업데이트 설정 로드 실패: ${error.message}`, colors.yellow);
      }
    }
  }

  // 업데이트 설정 저장
  saveUpdateConfig() {
    try {
      writeFileSync(this.updateConfigPath, JSON.stringify(this.updateConfig, null, 2));
    } catch (error) {
      log(`업데이트 설정 저장 실패: ${error.message}`, colors.red);
    }
  }

  // 업데이트 서버에서 최신 버전 정보 확인
  async checkForUpdates() {
    log('업데이트를 확인합니다...', colors.blue);
    
    try {
      // 실제 구현에서는 HTTP 요청을 사용
      const updateInfo = await this.fetchUpdateInfo();
      
      if (!updateInfo) {
        log('업데이트 정보를 가져올 수 없습니다', colors.yellow);
        return null;
      }
      
      const latestVersion = updateInfo.version;
      const isNewer = this.compareVersions(latestVersion, this.currentVersion) > 0;
      
      if (isNewer && latestVersion !== this.updateConfig.skipVersion) {
        log(`새로운 버전이 있습니다: ${latestVersion} (현재: ${this.currentVersion})`, colors.green);
        return updateInfo;
      } else {
        log('최신 버전을 사용 중입니다', colors.green);
        return null;
      }
      
    } catch (error) {
      log(`업데이트 확인 실패: ${error.message}`, colors.red);
      return null;
    } finally {
      this.updateConfig.lastCheck = new Date().toISOString();
      this.saveUpdateConfig();
    }
  }

  // 업데이트 정보 가져오기 (모의 구현)
  async fetchUpdateInfo() {
    // 실제 구현에서는 fetch 또는 axios 사용
    const mockUpdateInfo = {
      version: '1.1.0',
      releaseDate: '2024-01-15T10:00:00Z',
      channel: 'stable',
      mandatory: false,
      changelog: [
        '성능 개선 및 버그 수정',
        '새로운 모니터링 기능 추가',
        'UI/UX 개선'
      ],
      downloads: {
        windows: {
          url: `${this.updateServerUrl}/1.1.0/windows/WatchHamster-1.1.0-x64.msi`,
          size: 52428800,
          checksum: 'sha256:abcd1234...'
        },
        macos: {
          url: `${this.updateServerUrl}/1.1.0/macos/WatchHamster-1.1.0-universal.dmg`,
          size: 48234567,
          checksum: 'sha256:efgh5678...'
        },
        linux: {
          url: `${this.updateServerUrl}/1.1.0/linux/watchhamster-1.1.0-amd64.deb`,
          size: 45123456,
          checksum: 'sha256:ijkl9012...'
        }
      },
      systemRequirements: {
        windows: 'Windows 10 이상',
        macos: 'macOS 10.13 이상',
        linux: 'Ubuntu 18.04 이상'
      }
    };
    
    // 현재 버전보다 높은 경우에만 반환
    if (this.compareVersions(mockUpdateInfo.version, this.currentVersion) > 0) {
      return mockUpdateInfo;
    }
    
    return null;
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

  // 업데이트 다운로드
  async downloadUpdate(updateInfo) {
    log(`업데이트를 다운로드합니다: ${updateInfo.version}`, colors.blue);
    
    const platform = this.getCurrentPlatform();
    const downloadInfo = updateInfo.downloads[platform];
    
    if (!downloadInfo) {
      throw new Error(`${platform} 플랫폼용 업데이트를 찾을 수 없습니다`);
    }
    
    // 캐시 디렉토리 생성
    if (!existsSync(this.updateCachePath)) {
      mkdirSync(this.updateCachePath, { recursive: true });
    }
    
    const fileName = downloadInfo.url.split('/').pop();
    const downloadPath = join(this.updateCachePath, fileName);
    
    try {
      // 실제 구현에서는 HTTP 다운로드 구현
      log(`다운로드 중: ${downloadInfo.url}`, colors.yellow);
      log(`저장 위치: ${downloadPath}`, colors.cyan);
      
      // 모의 다운로드 (실제로는 파일을 다운로드)
      await this.simulateDownload(downloadInfo, downloadPath);
      
      // 체크섬 검증
      if (downloadInfo.checksum) {
        const isValid = await this.verifyChecksum(downloadPath, downloadInfo.checksum);
        if (!isValid) {
          throw new Error('다운로드한 파일의 체크섬이 일치하지 않습니다');
        }
      }
      
      log('업데이트 다운로드 완료', colors.green);
      return downloadPath;
      
    } catch (error) {
      log(`업데이트 다운로드 실패: ${error.message}`, colors.red);
      throw error;
    }
  }

  // 현재 플랫폼 감지
  getCurrentPlatform() {
    switch (process.platform) {
      case 'win32': return 'windows';
      case 'darwin': return 'macos';
      case 'linux': return 'linux';
      default: return 'unknown';
    }
  }

  // 다운로드 시뮬레이션
  async simulateDownload(downloadInfo, downloadPath) {
    // 실제 구현에서는 fetch 또는 axios로 파일 다운로드
    return new Promise((resolve) => {
      setTimeout(() => {
        // 모의 파일 생성
        writeFileSync(downloadPath, `Mock update file for ${downloadInfo.url}`);
        resolve();
      }, 2000);
    });
  }

  // 체크섬 검증
  async verifyChecksum(filePath, expectedChecksum) {
    try {
      // 실제 구현에서는 파일의 실제 체크섬 계산
      log('체크섬을 검증합니다...', colors.yellow);
      
      // 모의 검증 (항상 성공)
      return true;
    } catch (error) {
      log(`체크섬 검증 실패: ${error.message}`, colors.red);
      return false;
    }
  }

  // 업데이트 설치
  async installUpdate(updatePath, updateInfo) {
    log(`업데이트를 설치합니다: ${updateInfo.version}`, colors.blue);
    
    const platform = this.getCurrentPlatform();
    
    try {
      switch (platform) {
        case 'windows':
          await this.installWindowsUpdate(updatePath);
          break;
        case 'macos':
          await this.installMacOSUpdate(updatePath);
          break;
        case 'linux':
          await this.installLinuxUpdate(updatePath);
          break;
        default:
          throw new Error(`지원되지 않는 플랫폼: ${platform}`);
      }
      
      log('업데이트 설치 완료', colors.green);
      log('애플리케이션을 재시작해주세요', colors.yellow);
      
    } catch (error) {
      log(`업데이트 설치 실패: ${error.message}`, colors.red);
      throw error;
    }
  }

  // Windows 업데이트 설치
  async installWindowsUpdate(updatePath) {
    log('Windows 업데이트를 설치합니다...', colors.yellow);
    
    // MSI 파일 설치
    const installCmd = `msiexec /i "${updatePath}" /quiet /norestart`;
    
    try {
      execSync(installCmd, { stdio: 'inherit' });
    } catch (error) {
      throw new Error(`Windows 업데이트 설치 실패: ${error.message}`);
    }
  }

  // macOS 업데이트 설치
  async installMacOSUpdate(updatePath) {
    log('macOS 업데이트를 설치합니다...', colors.yellow);
    
    // DMG 마운트 및 앱 교체
    try {
      // DMG 마운트
      const mountOutput = execSync(`hdiutil attach "${updatePath}"`, { encoding: 'utf8' });
      const mountPoint = mountOutput.match(/\/Volumes\/[^\s]+/)?.[0];
      
      if (mountPoint) {
        // 기존 앱 백업
        execSync('mv /Applications/WatchHamster.app /Applications/WatchHamster.app.backup');
        
        // 새 앱 복사
        execSync(`cp -R "${mountPoint}/WatchHamster.app" /Applications/`);
        
        // DMG 언마운트
        execSync(`hdiutil detach "${mountPoint}"`);
        
        // 백업 제거
        execSync('rm -rf /Applications/WatchHamster.app.backup');
      }
    } catch (error) {
      throw new Error(`macOS 업데이트 설치 실패: ${error.message}`);
    }
  }

  // Linux 업데이트 설치
  async installLinuxUpdate(updatePath) {
    log('Linux 업데이트를 설치합니다...', colors.yellow);
    
    try {
      if (updatePath.endsWith('.deb')) {
        // DEB 패키지 설치
        execSync(`sudo dpkg -i "${updatePath}"`, { stdio: 'inherit' });
        execSync('sudo apt-get install -f -y', { stdio: 'inherit' });
      } else if (updatePath.endsWith('.AppImage')) {
        // AppImage 교체
        execSync(`sudo cp "${updatePath}" /opt/watchhamster.AppImage`);
        execSync('sudo chmod +x /opt/watchhamster.AppImage');
      }
    } catch (error) {
      throw new Error(`Linux 업데이트 설치 실패: ${error.message}`);
    }
  }

  // 업데이트 프로세스 실행
  async performUpdate() {
    log('자동 업데이트 프로세스를 시작합니다...', colors.bright);
    
    this.loadUpdateConfig();
    
    if (!this.updateConfig.enabled) {
      log('자동 업데이트가 비활성화되어 있습니다', colors.yellow);
      return;
    }
    
    try {
      // 업데이트 확인
      const updateInfo = await this.checkForUpdates();
      
      if (!updateInfo) {
        log('사용 가능한 업데이트가 없습니다', colors.green);
        return;
      }
      
      // 사용자 확인 (실제 구현에서는 GUI 대화상자)
      const shouldUpdate = await this.promptUserForUpdate(updateInfo);
      
      if (!shouldUpdate) {
        log('사용자가 업데이트를 취소했습니다', colors.yellow);
        return;
      }
      
      // 업데이트 다운로드
      let updatePath;
      if (this.updateConfig.autoDownload) {
        updatePath = await this.downloadUpdate(updateInfo);
      } else {
        log('자동 다운로드가 비활성화되어 있습니다', colors.yellow);
        return;
      }
      
      // 업데이트 설치
      if (this.updateConfig.autoInstall) {
        await this.installUpdate(updatePath, updateInfo);
      } else {
        log('업데이트가 다운로드되었습니다. 수동으로 설치해주세요:', colors.yellow);
        log(updatePath, colors.cyan);
      }
      
    } catch (error) {
      log(`업데이트 프로세스 실패: ${error.message}`, colors.red);
    }
  }

  // 사용자 업데이트 확인 (모의 구현)
  async promptUserForUpdate(updateInfo) {
    log('\n📦 새로운 업데이트가 있습니다!', colors.bright);
    log(`현재 버전: ${this.currentVersion}`, colors.cyan);
    log(`새 버전: ${updateInfo.version}`, colors.green);
    log(`릴리스 날짜: ${new Date(updateInfo.releaseDate).toLocaleDateString('ko-KR')}`, colors.cyan);
    
    log('\n변경사항:', colors.bright);
    updateInfo.changelog.forEach(change => {
      log(`  - ${change}`, colors.white);
    });
    
    // 실제 구현에서는 GUI 대화상자 또는 사용자 입력
    log('\n자동으로 업데이트를 진행합니다...', colors.yellow);
    return true;
  }

  // 업데이트 설정 관리
  async configureUpdates(options = {}) {
    log('업데이트 설정을 구성합니다...', colors.blue);
    
    this.loadUpdateConfig();
    
    // 설정 업데이트
    Object.assign(this.updateConfig, options);
    
    this.saveUpdateConfig();
    
    log('업데이트 설정이 저장되었습니다:', colors.green);
    log(JSON.stringify(this.updateConfig, null, 2), colors.cyan);
  }

  // 업데이트 상태 확인
  getUpdateStatus() {
    this.loadUpdateConfig();
    
    return {
      currentVersion: this.currentVersion,
      updateEnabled: this.updateConfig.enabled,
      lastCheck: this.updateConfig.lastCheck,
      channel: this.updateConfig.channel,
      autoDownload: this.updateConfig.autoDownload,
      autoInstall: this.updateConfig.autoInstall
    };
  }
}

// 사용법 출력
function printUsage() {
  console.log(`
🔄 WatchHamster 자동 업데이터

사용법:
  node scripts/auto-updater.js <명령어> [옵션]

명령어:
  check       업데이트 확인
  update      업데이트 실행
  config      업데이트 설정 구성
  status      업데이트 상태 확인
  help        이 도움말 출력

설정 옵션 (config 명령어와 함께 사용):
  --enabled <true|false>      자동 업데이트 활성화/비활성화
  --channel <stable|beta>     업데이트 채널 설정
  --auto-download <true|false> 자동 다운로드 설정
  --auto-install <true|false>  자동 설치 설정

예시:
  node scripts/auto-updater.js check                    # 업데이트 확인
  node scripts/auto-updater.js update                   # 업데이트 실행
  node scripts/auto-updater.js config --enabled true    # 자동 업데이트 활성화
  node scripts/auto-updater.js status                   # 상태 확인
`);
}

// 메인 실행
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'help') {
    printUsage();
    return;
  }
  
  const updater = new AutoUpdater();
  
  switch (command) {
    case 'check':
      await updater.checkForUpdates();
      break;
      
    case 'update':
      await updater.performUpdate();
      break;
      
    case 'config':
      const configOptions = {};
      
      for (let i = 1; i < args.length; i += 2) {
        const option = args[i];
        const value = args[i + 1];
        
        switch (option) {
          case '--enabled':
            configOptions.enabled = value === 'true';
            break;
          case '--channel':
            configOptions.channel = value;
            break;
          case '--auto-download':
            configOptions.autoDownload = value === 'true';
            break;
          case '--auto-install':
            configOptions.autoInstall = value === 'true';
            break;
        }
      }
      
      await updater.configureUpdates(configOptions);
      break;
      
    case 'status':
      const status = updater.getUpdateStatus();
      console.log('업데이트 상태:', JSON.stringify(status, null, 2));
      break;
      
    default:
      console.error(`알 수 없는 명령어: ${command}`);
      printUsage();
      process.exit(1);
  }
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('자동 업데이터 실행 실패:', error);
    process.exit(1);
  });
}

export { AutoUpdater };