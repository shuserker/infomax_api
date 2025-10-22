#!/usr/bin/env node

/**
 * 디버깅 도구 스크립트
 * 개발 중 디버깅을 위한 다양한 유틸리티를 제공합니다.
 */

import { execSync, spawn } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
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
  console.log(`${color}${message}${colors.reset}`);
}

class DebugTools {
  constructor() {
    this.logFile = join(projectRoot, 'debug.log');
  }

  // 시스템 정보 수집
  collectSystemInfo() {
    log('🔍 시스템 정보를 수집합니다...', colors.blue);
    
    const info = {
      timestamp: new Date().toISOString(),
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      npmVersion: this.getCommandOutput('npm --version'),
      pythonVersion: this.getCommandOutput('python --version'),
      rustVersion: this.getCommandOutput('rustc --version'),
      gitVersion: this.getCommandOutput('git --version'),
      workingDirectory: process.cwd(),
      environment: process.env.NODE_ENV || 'development'
    };
    
    // 패키지 정보
    try {
      const packageJson = JSON.parse(readFileSync(join(projectRoot, 'package.json'), 'utf8'));
      info.projectVersion = packageJson.version;
      info.dependencies = Object.keys(packageJson.dependencies || {}).length;
      info.devDependencies = Object.keys(packageJson.devDependencies || {}).length;
    } catch (error) {
      info.packageError = error.message;
    }
    
    // Python 백엔드 정보
    try {
      const requirementsPath = join(projectRoot, 'python-backend', 'requirements.txt');
      if (existsSync(requirementsPath)) {
        const requirements = readFileSync(requirementsPath, 'utf8');
        info.pythonDependencies = requirements.split('\n').filter(line => line.trim()).length;
      }
    } catch (error) {
      info.pythonError = error.message;
    }
    
    log('✅ 시스템 정보 수집 완료', colors.green);
    return info;
  }

  // 명령어 출력 가져오기
  getCommandOutput(command) {
    try {
      return execSync(command, { encoding: 'utf8', stdio: 'pipe' }).trim();
    } catch (error) {
      return `Error: ${error.message}`;
    }
  }

  // 포트 사용 상태 확인
  checkPorts() {
    log('🔍 포트 사용 상태를 확인합니다...', colors.blue);
    
    const ports = [1420, 8000, 3000, 5173];
    const portStatus = {};
    
    for (const port of ports) {
      try {
        if (process.platform === 'win32') {
          const output = execSync(`netstat -an | findstr :${port}`, { encoding: 'utf8', stdio: 'pipe' });
          portStatus[port] = output ? 'USED' : 'FREE';
        } else {
          const output = execSync(`lsof -i :${port}`, { encoding: 'utf8', stdio: 'pipe' });
          portStatus[port] = output ? 'USED' : 'FREE';
        }
      } catch (error) {
        portStatus[port] = 'FREE';
      }
    }
    
    log('포트 상태:', colors.cyan);
    for (const [port, status] of Object.entries(portStatus)) {
      const color = status === 'FREE' ? colors.green : colors.red;
      log(`  ${port}: ${status}`, color);
    }
    
    return portStatus;
  }

  // 프로세스 상태 확인
  checkProcesses() {
    log('🔍 관련 프로세스를 확인합니다...', colors.blue);
    
    const processes = [];
    
    try {
      let output;
      if (process.platform === 'win32') {
        output = execSync('tasklist /FI "IMAGENAME eq python.exe" /FO CSV', { encoding: 'utf8' });
      } else {
        output = execSync('ps aux | grep -E "(python|node|rust)" | grep -v grep', { encoding: 'utf8' });
      }
      
      if (output) {
        processes.push(...output.split('\n').filter(line => line.trim()));
      }
    } catch (error) {
      log(`프로세스 확인 실패: ${error.message}`, colors.red);
    }
    
    log(`활성 프로세스: ${processes.length}개`, colors.cyan);
    return processes;
  }

  // 로그 파일 분석
  analyzeLogs() {
    log('🔍 로그 파일을 분석합니다...', colors.blue);
    
    const logPaths = [
      join(projectRoot, 'debug.log'),
      join(projectRoot, 'python-backend', 'app.log'),
      join(projectRoot, 'src-tauri', 'target', 'debug.log')
    ];
    
    const logAnalysis = {};
    
    for (const logPath of logPaths) {
      if (existsSync(logPath)) {
        try {
          const content = readFileSync(logPath, 'utf8');
          const lines = content.split('\n');
          
          logAnalysis[logPath] = {
            totalLines: lines.length,
            errorLines: lines.filter(line => line.toLowerCase().includes('error')).length,
            warningLines: lines.filter(line => line.toLowerCase().includes('warning')).length,
            lastModified: new Date().toISOString()
          };
        } catch (error) {
          logAnalysis[logPath] = { error: error.message };
        }
      }
    }
    
    log('로그 분석 결과:', colors.cyan);
    for (const [path, analysis] of Object.entries(logAnalysis)) {
      log(`  ${path}:`, colors.yellow);
      if (analysis.error) {
        log(`    오류: ${analysis.error}`, colors.red);
      } else {
        log(`    총 라인: ${analysis.totalLines}`, colors.white);
        log(`    에러: ${analysis.errorLines}`, colors.red);
        log(`    경고: ${analysis.warningLines}`, colors.yellow);
      }
    }
    
    return logAnalysis;
  }

  // 의존성 상태 확인
  checkDependencies() {
    log('🔍 의존성 상태를 확인합니다...', colors.blue);
    
    const dependencyStatus = {
      npm: { status: 'unknown', issues: [] },
      python: { status: 'unknown', issues: [] },
      rust: { status: 'unknown', issues: [] }
    };
    
    // NPM 의존성 확인
    try {
      execSync('npm ls --depth=0', { cwd: projectRoot, stdio: 'pipe' });
      dependencyStatus.npm.status = 'ok';
    } catch (error) {
      dependencyStatus.npm.status = 'error';
      dependencyStatus.npm.issues.push(error.message);
    }
    
    // Python 의존성 확인
    try {
      const backendPath = join(projectRoot, 'python-backend');
      execSync('pip check', { cwd: backendPath, stdio: 'pipe' });
      dependencyStatus.python.status = 'ok';
    } catch (error) {
      dependencyStatus.python.status = 'error';
      dependencyStatus.python.issues.push(error.message);
    }
    
    // Rust 의존성 확인
    try {
      const tauriPath = join(projectRoot, 'src-tauri');
      execSync('cargo check', { cwd: tauriPath, stdio: 'pipe' });
      dependencyStatus.rust.status = 'ok';
    } catch (error) {
      dependencyStatus.rust.status = 'error';
      dependencyStatus.rust.issues.push(error.message);
    }
    
    log('의존성 상태:', colors.cyan);
    for (const [name, status] of Object.entries(dependencyStatus)) {
      const color = status.status === 'ok' ? colors.green : colors.red;
      log(`  ${name}: ${status.status}`, color);
      if (status.issues.length > 0) {
        status.issues.forEach(issue => log(`    - ${issue}`, colors.red));
      }
    }
    
    return dependencyStatus;
  }

  // 네트워크 연결 테스트
  async testNetworkConnections() {
    log('🔍 네트워크 연결을 테스트합니다...', colors.blue);
    
    const endpoints = [
      { name: 'Backend Health', url: 'http://localhost:8000/health' },
      { name: 'Backend API', url: 'http://localhost:8000/api/services' },
      { name: 'WebSocket', url: 'ws://localhost:8000/ws' }
    ];
    
    const results = {};
    
    for (const endpoint of endpoints) {
      try {
        if (endpoint.url.startsWith('ws://')) {
          // WebSocket 테스트는 간단히 스킵
          results[endpoint.name] = { status: 'skipped', message: 'WebSocket test not implemented' };
        } else {
          const response = await fetch(endpoint.url, { 
            method: 'GET',
            timeout: 5000 
          });
          results[endpoint.name] = { 
            status: response.ok ? 'ok' : 'error', 
            statusCode: response.status 
          };
        }
      } catch (error) {
        results[endpoint.name] = { 
          status: 'error', 
          message: error.message 
        };
      }
    }
    
    log('네트워크 테스트 결과:', colors.cyan);
    for (const [name, result] of Object.entries(results)) {
      const color = result.status === 'ok' ? colors.green : 
                   result.status === 'skipped' ? colors.yellow : colors.red;
      log(`  ${name}: ${result.status}`, color);
      if (result.message) {
        log(`    ${result.message}`, colors.white);
      }
    }
    
    return results;
  }

  // 전체 진단 실행
  async runFullDiagnostics() {
    log('🚀 전체 시스템 진단을 시작합니다...', colors.bright);
    
    const diagnostics = {
      timestamp: new Date().toISOString(),
      systemInfo: this.collectSystemInfo(),
      portStatus: this.checkPorts(),
      processes: this.checkProcesses(),
      logAnalysis: this.analyzeLogs(),
      dependencies: this.checkDependencies(),
      networkTests: await this.testNetworkConnections()
    };
    
    // 진단 결과를 파일로 저장
    const reportPath = join(projectRoot, `debug-report-${Date.now()}.json`);
    writeFileSync(reportPath, JSON.stringify(diagnostics, null, 2));
    
    log(`✅ 진단 완료! 보고서가 저장되었습니다: ${reportPath}`, colors.green);
    
    // 요약 출력
    this.printDiagnosticsSummary(diagnostics);
    
    return diagnostics;
  }

  // 진단 요약 출력
  printDiagnosticsSummary(diagnostics) {
    log('\n📊 진단 요약:', colors.bright);
    
    // 시스템 상태
    const systemOk = !diagnostics.systemInfo.packageError && !diagnostics.systemInfo.pythonError;
    log(`시스템 상태: ${systemOk ? '정상' : '문제 있음'}`, systemOk ? colors.green : colors.red);
    
    // 포트 상태
    const portsInUse = Object.values(diagnostics.portStatus).filter(status => status === 'USED').length;
    log(`포트 사용: ${portsInUse}/4개 포트 사용 중`, portsInUse > 0 ? colors.yellow : colors.green);
    
    // 의존성 상태
    const depsOk = Object.values(diagnostics.dependencies).every(dep => dep.status === 'ok');
    log(`의존성 상태: ${depsOk ? '정상' : '문제 있음'}`, depsOk ? colors.green : colors.red);
    
    // 네트워크 상태
    const networkOk = Object.values(diagnostics.networkTests).some(test => test.status === 'ok');
    log(`네트워크 상태: ${networkOk ? '일부 연결됨' : '연결 안됨'}`, networkOk ? colors.yellow : colors.red);
    
    log('\n💡 문제가 있다면 다음을 시도해보세요:', colors.blue);
    log('  1. npm run setup     # 개발 환경 재설정', colors.cyan);
    log('  2. npm run dev       # 개발 서버 시작', colors.cyan);
    log('  3. npm run test      # 테스트 실행', colors.cyan);
  }

  // 실시간 로그 모니터링
  startLogMonitoring() {
    log('📡 실시간 로그 모니터링을 시작합니다...', colors.blue);
    log('종료하려면 Ctrl+C를 누르세요', colors.yellow);
    
    const logPaths = [
      join(projectRoot, 'python-backend', 'app.log'),
      join(projectRoot, 'debug.log')
    ];
    
    // 각 로그 파일에 대해 tail 명령어 실행
    logPaths.forEach(logPath => {
      if (existsSync(logPath)) {
        const tailCmd = process.platform === 'win32' ? 'powershell' : 'tail';
        const tailArgs = process.platform === 'win32' 
          ? ['-Command', `Get-Content "${logPath}" -Wait -Tail 10`]
          : ['-f', logPath];
        
        const tailProcess = spawn(tailCmd, tailArgs, { stdio: 'pipe' });
        
        tailProcess.stdout.on('data', (data) => {
          const lines = data.toString().split('\n').filter(line => line.trim());
          lines.forEach(line => {
            const color = line.toLowerCase().includes('error') ? colors.red :
                         line.toLowerCase().includes('warning') ? colors.yellow :
                         colors.white;
            log(`[${logPath}] ${line}`, color);
          });
        });
      }
    });
  }
}

// 사용법 출력
function printUsage() {
  console.log(`
🔧 WatchHamster 디버깅 도구

사용법:
  node scripts/debug-tools.js <명령어>

명령어:
  system      시스템 정보 수집
  ports       포트 사용 상태 확인
  processes   프로세스 상태 확인
  logs        로그 파일 분석
  deps        의존성 상태 확인
  network     네트워크 연결 테스트
  full        전체 진단 실행
  monitor     실시간 로그 모니터링
  help        이 도움말 출력

예시:
  node scripts/debug-tools.js full      # 전체 진단
  node scripts/debug-tools.js monitor   # 로그 모니터링
`);
}

// 메인 실행
async function main() {
  const command = process.argv[2];
  const debugTools = new DebugTools();
  
  switch (command) {
    case 'system':
      debugTools.collectSystemInfo();
      break;
    case 'ports':
      debugTools.checkPorts();
      break;
    case 'processes':
      debugTools.checkProcesses();
      break;
    case 'logs':
      debugTools.analyzeLogs();
      break;
    case 'deps':
      debugTools.checkDependencies();
      break;
    case 'network':
      await debugTools.testNetworkConnections();
      break;
    case 'full':
      await debugTools.runFullDiagnostics();
      break;
    case 'monitor':
      debugTools.startLogMonitoring();
      break;
    case 'help':
    default:
      printUsage();
      break;
  }
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('디버깅 도구 실행 실패:', error);
    process.exit(1);
  });
}

export { DebugTools };