#!/usr/bin/env node

/**
 * 개발 서버 동시 실행 스크립트
 * 프론트엔드와 백엔드를 동시에 실행하고 상태를 모니터링합니다.
 */

import { spawn } from 'child_process';
import { existsSync } from 'fs';
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

function log(message, color = colors.reset, prefix = '') {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${color}[${timestamp}]${prefix ? ` [${prefix}]` : ''} ${message}${colors.reset}`);
}

class DevServer {
  constructor() {
    this.processes = new Map();
    this.isShuttingDown = false;
    
    // 종료 시그널 처리
    process.on('SIGINT', () => this.shutdown());
    process.on('SIGTERM', () => this.shutdown());
    process.on('exit', () => this.shutdown());
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
      pythonCmd = 'python';
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
        if (code !== 0) {
          log('백엔드 서버를 재시작합니다...', colors.yellow, 'BACKEND');
          setTimeout(() => this.startBackend(), 2000);
        }
      }
    });
    
    this.processes.set('backend', backendProcess);
    log('백엔드 서버가 시작되었습니다 (포트: 8000)', colors.green, 'BACKEND');
  }

  // 프론트엔드 서버 시작
  startFrontend() {
    log('React 프론트엔드 서버를 시작합니다...', colors.blue, 'FRONTEND');
    
    const frontendProcess = spawn('npm', ['run', 'dev:frontend'], {
      cwd: projectRoot,
      stdio: 'pipe',
      shell: true,
      env: {
        ...process.env,
        NODE_ENV: 'development'
      }
    });
    
    frontendProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message) {
        // Vite 로그 필터링
        if (message.includes('Local:') || message.includes('ready in')) {
          log(message, colors.cyan, 'FRONTEND');
        } else if (!message.includes('watching for file changes')) {
          log(message, colors.cyan, 'FRONTEND');
        }
      }
    });
    
    frontendProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('ExperimentalWarning')) {
        log(message, colors.red, 'FRONTEND');
      }
    });
    
    frontendProcess.on('close', (code) => {
      if (!this.isShuttingDown) {
        log(`프론트엔드 서버가 종료되었습니다 (코드: ${code})`, colors.red, 'FRONTEND');
        if (code !== 0) {
          log('프론트엔드 서버를 재시작합니다...', colors.yellow, 'FRONTEND');
          setTimeout(() => this.startFrontend(), 2000);
        }
      }
    });
    
    this.processes.set('frontend', frontendProcess);
    log('프론트엔드 서버가 시작되었습니다', colors.green, 'FRONTEND');
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
        const response = await fetch('http://localhost:8000/health');
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
    log('종료하려면 Ctrl+C를 누르세요', colors.yellow);
    
    // 순차적으로 서버 시작
    this.startBackend();
    
    // 백엔드가 시작될 시간을 기다림
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    this.startFrontend();
    this.startTauri();
    
    // 상태 모니터링 시작
    setTimeout(() => this.startHealthCheck(), 10000);
    
    log('✅ 모든 개발 서버가 시작되었습니다!', colors.green);
    log('📱 프론트엔드: http://localhost:1420', colors.cyan);
    log('🔧 백엔드 API: http://localhost:8000', colors.cyan);
    log('📚 API 문서: http://localhost:8000/docs', colors.cyan);
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
🚀 WatchHamster 개발 서버

사용법:
  node scripts/dev-server.js [옵션]

옵션:
  --tauri    Tauri 개발 서버도 함께 시작
  --help     이 도움말 출력

예시:
  node scripts/dev-server.js           # 프론트엔드 + 백엔드
  node scripts/dev-server.js --tauri   # 프론트엔드 + 백엔드 + Tauri
`);
}

// 메인 실행
async function main() {
  if (process.argv.includes('--help')) {
    printUsage();
    return;
  }
  
  const devServer = new DevServer();
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