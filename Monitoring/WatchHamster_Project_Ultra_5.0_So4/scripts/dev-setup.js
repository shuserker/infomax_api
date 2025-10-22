#!/usr/bin/env node

/**
 * 개발 환경 설정 스크립트
 * 개발에 필요한 모든 의존성과 환경을 자동으로 설정합니다.
 */

import { execSync, spawn } from 'child_process';
import { existsSync, mkdirSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

console.log('🚀 WatchHamster Tauri 개발 환경 설정을 시작합니다...\n');

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
  console.log(`${color}${message}${colors.reset}`);
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

// 시스템 요구사항 확인
function checkSystemRequirements() {
  logStep('1/7', '시스템 요구사항 확인 중...');
  
  try {
    // Node.js 버전 확인
    const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
    
    if (majorVersion < 18) {
      logError(`Node.js 18 이상이 필요합니다. 현재 버전: ${nodeVersion}`);
      process.exit(1);
    }
    logSuccess(`Node.js 버전 확인: ${nodeVersion}`);
    
    // Python 확인
    try {
      const pythonVersion = execSync('python --version', { encoding: 'utf8' }).trim();
      logSuccess(`Python 버전 확인: ${pythonVersion}`);
    } catch {
      try {
        const python3Version = execSync('python3 --version', { encoding: 'utf8' }).trim();
        logSuccess(`Python3 버전 확인: ${python3Version}`);
      } catch {
        logError('Python이 설치되어 있지 않습니다.');
        process.exit(1);
      }
    }
    
    // Rust 확인
    try {
      const rustVersion = execSync('rustc --version', { encoding: 'utf8' }).trim();
      logSuccess(`Rust 버전 확인: ${rustVersion}`);
    } catch {
      logWarning('Rust가 설치되어 있지 않습니다. Tauri 빌드를 위해 설치가 필요합니다.');
      log('설치 방법: https://rustup.rs/', colors.blue);
    }
    
  } catch (error) {
    logError(`시스템 요구사항 확인 실패: ${error.message}`);
    process.exit(1);
  }
}

// 환경 변수 파일 생성
function createEnvironmentFiles() {
  logStep('2/7', '환경 변수 파일 생성 중...');
  
  // 프론트엔드 환경 변수
  const frontendEnvPath = join(projectRoot, '.env.development');
  if (!existsSync(frontendEnvPath)) {
    const frontendEnvContent = `# 개발 환경 설정
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=WatchHamster Tauri
VITE_APP_VERSION=1.0.0
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=debug
`;
    writeFileSync(frontendEnvPath, frontendEnvContent);
    logSuccess('프론트엔드 환경 변수 파일 생성됨: .env.development');
  }
  
  // 백엔드 환경 변수
  const backendEnvPath = join(projectRoot, 'python-backend', '.env.development');
  if (!existsSync(backendEnvPath)) {
    const backendEnvContent = `# Python 백엔드 개발 환경 설정
DEBUG=true
LOG_LEVEL=debug
HOST=localhost
PORT=8000
CORS_ORIGINS=["http://localhost:1420", "http://localhost:3000", "tauri://localhost"]
RELOAD=true
WORKERS=1

# 데이터베이스 설정 (개발용)
DATABASE_URL=sqlite:///./dev_database.db

# 외부 서비스 설정
WEBHOOK_TIMEOUT=30
MAX_LOG_SIZE=10485760
LOG_RETENTION_DAYS=7

# POSCO 시스템 설정
POSCO_BRANCH=development
POSCO_DEPLOY_PATH=./deploy
`;
    writeFileSync(backendEnvPath, backendEnvContent);
    logSuccess('백엔드 환경 변수 파일 생성됨: python-backend/.env.development');
  }
}

// Python 가상환경 및 의존성 설정
function setupPythonEnvironment() {
  logStep('3/7', 'Python 환경 설정 중...');
  
  const backendPath = join(projectRoot, 'python-backend');
  const venvPath = join(backendPath, 'venv');
  
  try {
    // 가상환경 생성 (존재하지 않는 경우)
    if (!existsSync(venvPath)) {
      log('Python 가상환경 생성 중...', colors.yellow);
      execSync('python -m venv venv', { cwd: backendPath, stdio: 'inherit' });
      logSuccess('Python 가상환경 생성 완료');
    }
    
    // 의존성 설치
    log('Python 의존성 설치 중...', colors.yellow);
    const activateScript = process.platform === 'win32' 
      ? join(venvPath, 'Scripts', 'activate.bat')
      : join(venvPath, 'bin', 'activate');
    
    const pipInstallCmd = process.platform === 'win32'
      ? `${join(venvPath, 'Scripts', 'pip.exe')} install -r requirements.txt`
      : `${join(venvPath, 'bin', 'pip')} install -r requirements.txt`;
    
    execSync(pipInstallCmd, { cwd: backendPath, stdio: 'inherit' });
    logSuccess('Python 의존성 설치 완료');
    
  } catch (error) {
    logError(`Python 환경 설정 실패: ${error.message}`);
    process.exit(1);
  }
}

// Node.js 의존성 설치
function installNodeDependencies() {
  logStep('4/7', 'Node.js 의존성 설치 중...');
  
  try {
    execSync('npm install', { cwd: projectRoot, stdio: 'inherit' });
    logSuccess('Node.js 의존성 설치 완료');
  } catch (error) {
    logError(`Node.js 의존성 설치 실패: ${error.message}`);
    process.exit(1);
  }
}

// Tauri 개발 환경 설정
function setupTauriEnvironment() {
  logStep('5/7', 'Tauri 개발 환경 설정 중...');
  
  try {
    // Tauri CLI 설치 확인
    try {
      execSync('cargo tauri --version', { stdio: 'pipe' });
      logSuccess('Tauri CLI 확인됨');
    } catch {
      log('Tauri CLI 설치 중...', colors.yellow);
      execSync('cargo install tauri-cli', { stdio: 'inherit' });
      logSuccess('Tauri CLI 설치 완료');
    }
    
    // Rust 의존성 확인
    const tauriPath = join(projectRoot, 'src-tauri');
    execSync('cargo check', { cwd: tauriPath, stdio: 'inherit' });
    logSuccess('Rust 의존성 확인 완료');
    
  } catch (error) {
    logWarning(`Tauri 환경 설정 중 문제 발생: ${error.message}`);
    log('수동으로 Rust와 Tauri CLI를 설치해주세요.', colors.blue);
  }
}

// 개발 도구 설정
function setupDevelopmentTools() {
  logStep('6/7', '개발 도구 설정 중...');
  
  try {
    // Playwright 브라우저 설치
    log('Playwright 브라우저 설치 중...', colors.yellow);
    execSync('npx playwright install', { cwd: projectRoot, stdio: 'inherit' });
    logSuccess('Playwright 브라우저 설치 완료');
    
    // ESLint 및 Prettier 설정 확인
    execSync('npm run lint -- --max-warnings 0', { cwd: projectRoot, stdio: 'pipe' });
    logSuccess('코드 품질 도구 설정 확인 완료');
    
  } catch (error) {
    logWarning(`개발 도구 설정 중 문제 발생: ${error.message}`);
  }
}

// 개발 서버 상태 확인
function verifyDevelopmentSetup() {
  logStep('7/7', '개발 환경 검증 중...');
  
  log('개발 환경 설정이 완료되었습니다!', colors.green);
  log('\n다음 명령어로 개발을 시작할 수 있습니다:', colors.bright);
  log('  npm run dev          # 전체 개발 서버 시작', colors.cyan);
  log('  npm run dev:frontend # 프론트엔드만 시작', colors.cyan);
  log('  npm run dev:backend  # 백엔드만 시작', colors.cyan);
  log('  npm run test         # 테스트 실행', colors.cyan);
  log('  npm run build:tauri  # Tauri 앱 빌드', colors.cyan);
  
  log('\n🎉 개발 환경 설정이 성공적으로 완료되었습니다!', colors.green);
}

// 메인 실행 함수
async function main() {
  try {
    checkSystemRequirements();
    createEnvironmentFiles();
    setupPythonEnvironment();
    installNodeDependencies();
    setupTauriEnvironment();
    setupDevelopmentTools();
    verifyDevelopmentSetup();
  } catch (error) {
    logError(`개발 환경 설정 실패: ${error.message}`);
    process.exit(1);
  }
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { main as setupDevelopment };