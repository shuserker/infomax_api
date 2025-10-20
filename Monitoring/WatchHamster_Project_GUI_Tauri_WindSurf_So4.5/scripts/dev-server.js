#!/usr/bin/env node

/**
 * 개발 서버 동시 실행 스크립트
 * 프론트엔드와 백엔드를 동시에 실행하고 상태를 모니터링합니다.
 */

import { spawn, exec } from 'child_process';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { promisify } from 'util';

const execAsync = promisify(exec);

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

function log(message, color = colors.reset, prefix = '') {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${color}[${timestamp}]${prefix ? ` [${prefix}]` : ''} ${message}${colors.reset}`);
}

class DevServer {
  constructor() {
    this.processes = new Map();
    this.isShuttingDown = false;
    this.isKillingProcesses = false; // 프로세스 정리 중 플래그
    this.targetPorts = [9001, 1420]; // 백엔드(9001) + 프론트엔드(1420)
    
    // 종료 시그널 처리
    process.on('SIGINT', () => this.shutdown());
    process.on('SIGTERM', () => this.shutdown());
    process.on('exit', () => this.shutdown());
  }

  // 특정 포트를 사용하는 프로세스 찾기
  async findProcessByPort(port) {
    try {
      const platform = process.platform;
      let command;
      
      if (platform === 'win32') {
        command = `netstat -ano | findstr :${port}`;
      } else if (platform === 'darwin') {
        command = `lsof -ti:${port}`;
      } else {
        command = `lsof -ti:${port}`;
      }
      
      const { stdout } = await execAsync(command);
      
      if (platform === 'win32') {
        // Windows: netstat 결과에서 PID 추출
        const lines = stdout.split('\n').filter(line => line.includes('LISTENING'));
        const pids = lines.map(line => {
          const parts = line.trim().split(/\s+/);
          return parts[parts.length - 1];
        }).filter(pid => pid && pid !== '0');
        return [...new Set(pids)];
      } else {
        // macOS/Linux: lsof 결과에서 PID 추출
        return stdout.trim().split('\n').filter(pid => pid && pid !== '');
      }
    } catch (error) {
      // 포트를 사용하는 프로세스가 없으면 빈 배열 반환
      return [];
    }
  }

  // 프로세스 강제 종료
  async killProcess(pid) {
    try {
      const platform = process.platform;
      let command;
      
      if (platform === 'win32') {
        command = `taskkill /F /PID ${pid}`;
      } else {
        command = `kill -9 ${pid}`;
      }
      
      await execAsync(command);
      return true;
    } catch (error) {
      log(`PID ${pid} 종료 실패: ${error.message}`, colors.yellow);
      return false;
    }
  }

  // 기존 프로세스들 강제 종료
  async killExistingProcesses() {
    this.isKillingProcesses = true; // 프로세스 정리 시작
    log('🔍 기존 프로세스 검색 및 종료 중...', colors.yellow);
    
    for (const port of this.targetPorts) {
      const pids = await this.findProcessByPort(port);
      
      if (pids.length > 0) {
        log(`포트 ${port}을 사용하는 프로세스 발견: ${pids.join(', ')}`, colors.yellow);
        
        for (const pid of pids) {
          log(`PID ${pid} 강제 종료 중...`, colors.red);
          const success = await this.killProcess(pid);
          if (success) {
            log(`✅ PID ${pid} 종료 완료`, colors.green);
          }
        }
      } else {
        log(`포트 ${port}: 사용 중인 프로세스 없음`, colors.green);
      }
    }
    
    // 프로세스 종료 후 잠시 대기
    log('프로세스 종료 완료 대기 중...', colors.yellow);
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    this.isKillingProcesses = false; // 프로세스 정리 완료
    log('✅ 기존 프로세스 정리 완료!', colors.green);
  }

  // 백엔드 서버 시작
  startBackend() {
    log('Python 백엔드 서버를 시작합니다...', colors.blue, 'BACKEND');
    
    const backendPath = join(projectRoot, 'python-backend');
    const venvPath = join(backendPath, 'venv');
    
    // 가상환경 활성화 명령어 설정
    let pythonCmd, pythonArgs;
    
    if (process.platform === 'win32') {
      pythonCmd = join(venvPath, 'Scripts', 'python.exe');
      pythonArgs = ['main.py'];
    } else {
      pythonCmd = join(venvPath, 'bin', 'python');
      pythonArgs = ['main.py'];
    }
    
    // 가상환경이 없으면 시스템 Python 사용
    if (!existsSync(pythonCmd)) {
      log('가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.', colors.yellow, 'BACKEND');
      // macOS에서는 python3.11 사용
      pythonCmd = process.platform === 'darwin' ? 'python3.11' : 'python';
    }
    
    const backendProcess = spawn(pythonCmd, pythonArgs, {
      cwd: backendPath,
      stdio: 'pipe',
      env: {
        ...process.env,
        PYTHONPATH: backendPath,
        ENV: 'development'
      }
    });
    
    backendProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message) {
        log(message, colors.green, 'BACKEND');
      }
    });
    
    backendProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('WARNING')) {
        log(message, colors.red, 'BACKEND');
      }
    });
    
    backendProcess.on('close', (code) => {
      if (!this.isShuttingDown) {
        log(`백엔드 서버가 종료되었습니다 (코드: ${code})`, colors.red, 'BACKEND');
        // 포트 충돌로 인한 종료면 재시작하지 않음
        if (code !== 0 && !this.isKillingProcesses) {
          log('백엔드 서버를 재시작합니다...', colors.yellow, 'BACKEND');
          setTimeout(() => this.startBackend(), 3000);
        } else if (this.isKillingProcesses) {
          log('프로세스 정리 중이므로 재시작하지 않습니다', colors.blue, 'BACKEND');
        }
      }
    });
    
    this.processes.set('backend', backendProcess);
    log('백엔드 서버가 시작되었습니다 (포트: 9001)', colors.green, 'BACKEND');
  }

  // 프론트엔드 개발 서버 시작 (빌드 대신 dev 서버 사용)
  async startFrontend() {
    log('React 개발 서버를 시작합니다...', colors.blue, 'FRONTEND');
    
    // 개발 모드에서는 빌드하지 않고 Vite dev 서버 시작
    const frontendProcess = spawn('npm', ['run', 'dev:frontend'], {
      cwd: projectRoot,
      stdio: 'pipe',
      env: {
        ...process.env,
        NODE_ENV: 'development',
        PORT: '1420' // 프론트엔드 전용 포트
      }
    });
    
    frontendProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('watching for file changes')) {
        log(message, colors.cyan, 'FRONTEND');
      }
    });
    
    frontendProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('warning')) {
        log(message, colors.red, 'FRONTEND');
      }
    });
    
    frontendProcess.on('close', (code) => {
      if (!this.isShuttingDown) {
        log(`프론트엔드 서버가 종료되었습니다 (코드: ${code})`, colors.red, 'FRONTEND');
        if (code !== 0 && !this.isKillingProcesses) {
          log('프론트엔드 서버를 재시작합니다...', colors.yellow, 'FRONTEND');
          setTimeout(() => this.startFrontend(), 3000);
        }
      }
    });
    
    this.processes.set('frontend', frontendProcess);
    log('✅ 프론트엔드 개발 서버가 시작되었습니다! (포트: 1420)', colors.green, 'FRONTEND');
    return true;
  }

  // 파일 변경 감지 및 자동 빌드 (선택적)
  startFileWatcher() {
    log('파일 변경 감지를 시작합니다...', colors.blue, 'WATCHER');
    
    const watcherProcess = spawn('vite', ['build', '--watch'], {
      cwd: projectRoot,
      stdio: 'pipe',
      shell: true,
      env: {
        ...process.env,
        NODE_ENV: 'development'
      }
    });
    
    watcherProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message && (message.includes('built in') || message.includes('watching for file changes'))) {
        log('🔄 프론트엔드 자동 빌드 완료', colors.cyan, 'WATCHER');
      }
    });
    
    watcherProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('ExperimentalWarning') && !message.includes('DeprecationWarning')) {
        log(message, colors.yellow, 'WATCHER');
      }
    });
    
    watcherProcess.on('close', (code) => {
      if (!this.isShuttingDown && code !== 0) {
        log('파일 감시 프로세스를 재시작합니다...', colors.yellow, 'WATCHER');
        setTimeout(() => this.startFileWatcher(), 3000);
      }
    });
    
    this.processes.set('watcher', watcherProcess);
    log('✅ 파일 변경 감지 시작됨 (자동 빌드)', colors.green, 'WATCHER');
  }

  // Tauri 개발 서버 시작 (선택적)
  startTauri() {
    if (process.argv.includes('--tauri')) {
      log('Tauri 개발 서버를 시작합니다...', colors.blue, 'TAURI');
      
      const tauriProcess = spawn('npm', ['run', 'tauri', 'dev'], {
        cwd: projectRoot,
        stdio: 'pipe',
        shell: true
      });
      
      tauriProcess.stdout.on('data', (data) => {
        const message = data.toString().trim();
        if (message) {
          log(message, colors.magenta, 'TAURI');
        }
      });
      
      tauriProcess.stderr.on('data', (data) => {
        const message = data.toString().trim();
        if (message) {
          log(message, colors.red, 'TAURI');
        }
      });
      
      tauriProcess.on('close', (code) => {
        if (!this.isShuttingDown) {
          log(`Tauri 서버가 종료되었습니다 (코드: ${code})`, colors.red, 'TAURI');
        }
      });
      
      this.processes.set('tauri', tauriProcess);
      log('Tauri 개발 서버가 시작되었습니다', colors.green, 'TAURI');
    }
  }

  // 서버 상태 모니터링
  startHealthCheck() {
    const checkInterval = setInterval(async () => {
      if (this.isShuttingDown) {
        clearInterval(checkInterval);
        return;
      }
      
      try {
        // 백엔드 상태 확인
        const response = await fetch('http://localhost:9001/health');
        if (response.ok) {
          // 정상 상태일 때는 로그 출력하지 않음
        } else {
          log('백엔드 서버 응답 이상', colors.yellow, 'HEALTH');
        }
      } catch (error) {
        // 연결 실패 시에도 로그 출력하지 않음 (시작 시 정상)
      }
    }, 30000); // 30초마다 확인
  }

  // 모든 서버 시작
  async start() {
    log('🚀 WatchHamster 개발 서버를 시작합니다...', colors.bright);
    log('🌐 프론트엔드: http://localhost:1420', colors.cyan);
    log('🔧 백엔드 API: http://localhost:9001', colors.cyan);
    log('종료하려면 Ctrl+C를 누르세요', colors.yellow);
    
    // 🔥 기존 프로세스 강제 종료
    await this.killExistingProcesses();
    
    // 1. 프론트엔드 개발 서버 시작
    await this.startFrontend();
    
    // 2. 백엔드 시작 (API만)
    this.startBackend();
    
    // 백엔드가 완전히 시작될 시간을 기다림
    await new Promise(resolve => setTimeout(resolve, 4000));
    
    // 3. 파일 변경 감지 시작 (선택적)
    if (!process.argv.includes('--no-watch')) {
      this.startFileWatcher();
    }
    
    // 4. Tauri (선택적)
    this.startTauri();
    
    // 상태 모니터링 시작
    setTimeout(() => this.startHealthCheck(), 10000);
    
    log('✅ 개발 서버가 시작되었습니다!', colors.green);
    log('', colors.reset);
    log('🌐 ===== 접속 주소 =====', colors.bright);
    log('📱 프론트엔드: http://localhost:1420', colors.cyan);
    log('🔧 백엔드 API: http://localhost:9001/api/*', colors.cyan);
    log('📚 API 문서: http://localhost:9001/docs', colors.cyan);
    log('🔌 WebSocket: ws://localhost:9001/ws', colors.cyan);
    log('=====================', colors.bright);
  }

  // 서버 종료
  shutdown() {
    if (this.isShuttingDown) return;
    
    this.isShuttingDown = true;
    log('🛑 개발 서버를 종료합니다...', colors.yellow);
    
    for (const [name, process] of this.processes) {
      try {
        log(`${name} 서버를 종료합니다...`, colors.yellow);
        
        if (process.pid) {
          if (process.platform === 'win32') {
            spawn('taskkill', ['/pid', process.pid, '/f', '/t'], { stdio: 'ignore' });
          } else {
            process.kill('SIGTERM');
          }
        }
      } catch (error) {
        log(`${name} 서버 종료 중 오류: ${error.message}`, colors.red);
      }
    }
    
    setTimeout(() => {
      log('👋 개발 서버가 종료되었습니다', colors.green);
      process.exit(0);
    }, 2000);
  }
}

// 사용법 출력
function printUsage() {
  console.log(`
🚀 WatchHamster 통합 개발 서버 (9001 포트 완전 통합!)

✨ 특징:
  • 한 개 포트로 모든 기능: http://localhost:9001
  • 프론트엔드 + 백엔드 + WebSocket 통합
  • 자동 프로세스 종료 및 재시작
  • 파일 변경 감지 및 자동 빌드

사용법:
  npm run start                        # 권장 방법 (통합 서버)
  npm run dev                          # 동일한 기능
  npm run kill                         # 기존 프로세스만 종료

옵션:
  --tauri       Tauri 개발 서버도 함께 시작
  --no-watch    파일 변경 감지 비활성화  
  --kill-only   기존 프로세스만 종료하고 종료
  --help        이 도움말 출력

접속 주소:
  🌐 메인 페이지: http://localhost:9001
  🔧 API 문서: http://localhost:9001/docs  
  🔌 WebSocket: ws://localhost:9001/ws

예시:
  npm run start                        # 통합 개발 서버 시작
  npm run start -- --tauri             # Tauri도 함께 시작  
  npm run start -- --no-watch          # 파일 감시 없이 시작
  npm run kill                         # 실행 중인 서버만 종료
`);
}

// 메인 실행
async function main() {
  if (process.argv.includes('--help')) {
    printUsage();
    return;
  }
  
  const devServer = new DevServer();
  
  // 기존 프로세스만 종료하고 끝내기
  if (process.argv.includes('--kill-only')) {
    log('🔥 기존 프로세스만 종료합니다...', colors.red);
    await devServer.killExistingProcesses();
    log('✅ 종료 완료!', colors.green);
    process.exit(0);
    return;
  }
  
  // 정상 시작 (기존 프로세스 종료 + 새로 시작)
  await devServer.start();
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('개발 서버 시작 실패:', error);
    process.exit(1);
  });
}

export { DevServer };