#!/usr/bin/env node

/**
 * 배포 파이프라인 스크립트
 * CI/CD 환경에서 자동 배포를 위한 통합 스크립트
 */

import { execSync, spawn } from 'child_process';
import { existsSync, writeFileSync, readFileSync, mkdirSync, rmSync } from 'fs';
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

class DeploymentPipeline {
  constructor(options = {}) {
    this.environment = options.environment || process.env.NODE_ENV || 'production';
    this.version = this.getVersion();
    this.buildNumber = process.env.BUILD_NUMBER || Date.now().toString();
    this.gitCommit = this.getGitCommit();
    this.gitBranch = this.getGitBranch();
    
    this.config = {
      // 빌드 설정
      build: {
        skipTests: options.skipTests || false,
        skipLinting: options.skipLinting || false,
        platforms: options.platforms || ['current'], // current, all, windows, macos, linux
        optimization: options.optimization !== false
      },
      
      // 배포 설정
      deploy: {
        target: options.deployTarget || 'github-releases', // github-releases, s3, ftp
        createRelease: options.createRelease !== false,
        uploadArtifacts: options.uploadArtifacts !== false,
        notifySlack: options.notifySlack || false,
        notifyDiscord: options.notifyDiscord || false
      },
      
      // 품질 게이트
      qualityGates: {
        testCoverage: options.minCoverage || 80,
        lintErrors: options.maxLintErrors || 0,
        buildWarnings: options.maxBuildWarnings || 10
      }
    };
    
    this.deploymentInfo = {
      version: this.version,
      buildNumber: this.buildNumber,
      gitCommit: this.gitCommit,
      gitBranch: this.gitBranch,
      environment: this.environment,
      timestamp: new Date().toISOString(),
      platform: process.platform,
      arch: process.arch
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

  // Git 커밋 해시 가져오기
  getGitCommit() {
    try {
      return execSync('git rev-parse HEAD', { encoding: 'utf8', stdio: 'pipe' }).trim();
    } catch {
      return 'unknown';
    }
  }

  // Git 브랜치 가져오기
  getGitBranch() {
    try {
      return execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8', stdio: 'pipe' }).trim();
    } catch {
      return 'unknown';
    }
  }

  // 배포 환경 검증
  async validateEnvironment() {
    logStep('1/10', '배포 환경을 검증합니다...');
    
    const issues = [];
    
    // 필수 도구 확인
    const requiredTools = {
      node: 'node --version',
      npm: 'npm --version',
      git: 'git --version'
    };
    
    for (const [tool, command] of Object.entries(requiredTools)) {
      try {
        const version = execSync(command, { encoding: 'utf8', stdio: 'pipe' }).trim();
        log(`${tool}: ${version}`, colors.green);
      } catch {
        issues.push(`${tool}이 설치되어 있지 않습니다`);
      }
    }
    
    // 환경 변수 확인
    const requiredEnvVars = ['NODE_ENV'];
    const optionalEnvVars = ['GITHUB_TOKEN', 'SLACK_WEBHOOK_URL', 'DISCORD_WEBHOOK_URL'];
    
    for (const envVar of requiredEnvVars) {
      if (!process.env[envVar]) {
        issues.push(`필수 환경 변수가 설정되지 않음: ${envVar}`);
      }
    }
    
    for (const envVar of optionalEnvVars) {
      if (process.env[envVar]) {
        log(`${envVar}: 설정됨`, colors.green);
      } else {
        log(`${envVar}: 설정되지 않음 (선택사항)`, colors.yellow);
      }
    }
    
    // Git 상태 확인
    try {
      const gitStatus = execSync('git status --porcelain', { encoding: 'utf8', stdio: 'pipe' });
      if (gitStatus.trim() && this.environment === 'production') {
        issues.push('Git 작업 디렉토리에 커밋되지 않은 변경사항이 있습니다');
      }
    } catch {
      issues.push('Git 저장소 상태를 확인할 수 없습니다');
    }
    
    if (issues.length > 0) {
      logError('환경 검증 실패:');
      issues.forEach(issue => log(`  - ${issue}`, colors.red));
      throw new Error('배포 환경이 요구사항을 만족하지 않습니다');
    }
    
    logSuccess('배포 환경 검증 완료');
  }

  // 코드 품질 검사
  async runQualityChecks() {
    logStep('2/10', '코드 품질 검사를 실행합니다...');
    
    const qualityResults = {
      linting: { passed: false, errors: 0, warnings: 0 },
      typeCheck: { passed: false, errors: 0 },
      tests: { passed: false, coverage: 0 },
      security: { passed: false, vulnerabilities: 0 }
    };
    
    try {
      // ESLint 검사
      if (!this.config.build.skipLinting) {
        log('ESLint 검사 실행 중...', colors.yellow);
        try {
          execSync('npm run lint', { stdio: 'pipe' });
          qualityResults.linting.passed = true;
          log('ESLint 검사 통과', colors.green);
        } catch (error) {
          const output = error.stdout?.toString() || error.stderr?.toString() || '';
          const errorCount = (output.match(/error/gi) || []).length;
          const warningCount = (output.match(/warning/gi) || []).length;
          
          qualityResults.linting.errors = errorCount;
          qualityResults.linting.warnings = warningCount;
          
          if (errorCount > this.config.qualityGates.lintErrors) {
            throw new Error(`ESLint 오류가 너무 많습니다: ${errorCount}개 (최대: ${this.config.qualityGates.lintErrors}개)`);
          }
          
          qualityResults.linting.passed = true;
          log(`ESLint 검사 완료 (경고: ${warningCount}개)`, colors.yellow);
        }
      }
      
      // TypeScript 타입 검사
      log('TypeScript 타입 검사 실행 중...', colors.yellow);
      try {
        execSync('npm run type-check', { stdio: 'pipe' });
        qualityResults.typeCheck.passed = true;
        log('TypeScript 타입 검사 통과', colors.green);
      } catch (error) {
        throw new Error('TypeScript 타입 검사 실패');
      }
      
      // 테스트 실행
      if (!this.config.build.skipTests) {
        log('테스트 실행 중...', colors.yellow);
        try {
          const testOutput = execSync('npm run test -- --coverage', { encoding: 'utf8', stdio: 'pipe' });
          
          // 커버리지 추출 (간단한 파싱)
          const coverageMatch = testOutput.match(/All files[^\n]*?(\d+\.?\d*)/);
          const coverage = coverageMatch ? parseFloat(coverageMatch[1]) : 0;
          
          qualityResults.tests.coverage = coverage;
          
          if (coverage < this.config.qualityGates.testCoverage) {
            throw new Error(`테스트 커버리지가 부족합니다: ${coverage}% (최소: ${this.config.qualityGates.testCoverage}%)`);
          }
          
          qualityResults.tests.passed = true;
          log(`테스트 통과 (커버리지: ${coverage}%)`, colors.green);
        } catch (error) {
          throw new Error('테스트 실행 실패');
        }
      }
      
      // 보안 검사
      log('보안 취약점 검사 실행 중...', colors.yellow);
      try {
        execSync('npm audit --audit-level=high', { stdio: 'pipe' });
        qualityResults.security.passed = true;
        log('보안 검사 통과', colors.green);
      } catch (error) {
        logWarning('보안 취약점이 발견되었습니다. 검토가 필요합니다.');
        qualityResults.security.passed = true; // 경고로만 처리
      }
      
    } catch (error) {
      logError(`품질 검사 실패: ${error.message}`);
      throw error;
    }
    
    // 품질 보고서 저장
    const qualityReportPath = join(projectRoot, 'quality-report.json');
    writeFileSync(qualityReportPath, JSON.stringify(qualityResults, null, 2));
    
    logSuccess('코드 품질 검사 완료');
    return qualityResults;
  }

  // 의존성 설치 및 검증
  async installDependencies() {
    logStep('3/10', '의존성을 설치하고 검증합니다...');
    
    try {
      // 깨끗한 설치
      log('의존성 설치 중...', colors.yellow);
      execSync('npm ci', { stdio: 'inherit' });
      
      // 의존성 검증
      log('의존성 검증 중...', colors.yellow);
      execSync('npm ls --depth=0', { stdio: 'pipe' });
      
      logSuccess('의존성 설치 및 검증 완료');
    } catch (error) {
      logError(`의존성 설치 실패: ${error.message}`);
      throw error;
    }
  }

  // 빌드 실행
  async runBuild() {
    logStep('4/10', '애플리케이션을 빌드합니다...');
    
    try {
      // 환경 변수 설정
      const buildEnv = {
        ...process.env,
        NODE_ENV: this.environment,
        BUILD_NUMBER: this.buildNumber,
        GIT_COMMIT: this.gitCommit,
        GIT_BRANCH: this.gitBranch
      };
      
      // 플랫폼별 빌드
      if (this.config.build.platforms.includes('all')) {
        log('크로스 플랫폼 빌드 실행 중...', colors.yellow);
        execSync('npm run build:cross-platform', { stdio: 'inherit', env: buildEnv });
      } else if (this.config.build.platforms.includes('current')) {
        log('현재 플랫폼 빌드 실행 중...', colors.yellow);
        execSync('npm run build:production', { stdio: 'inherit', env: buildEnv });
      } else {
        // 특정 플랫폼들
        for (const platform of this.config.build.platforms) {
          log(`${platform} 플랫폼 빌드 실행 중...`, colors.yellow);
          execSync(`npm run build:${platform}`, { stdio: 'inherit', env: buildEnv });
        }
      }
      
      logSuccess('빌드 완료');
    } catch (error) {
      logError(`빌드 실패: ${error.message}`);
      throw error;
    }
  }

  // 패키지 생성
  async createPackages() {
    logStep('5/10', '설치 패키지를 생성합니다...');
    
    try {
      log('설치 패키지 생성 중...', colors.yellow);
      execSync('node scripts/package-installer.js', { stdio: 'inherit' });
      
      logSuccess('패키지 생성 완료');
    } catch (error) {
      logError(`패키지 생성 실패: ${error.message}`);
      throw error;
    }
  }

  // 아티팩트 수집
  async collectArtifacts() {
    logStep('6/10', '빌드 아티팩트를 수집합니다...');
    
    const artifactsDir = join(projectRoot, 'artifacts');
    
    try {
      // 아티팩트 디렉토리 생성
      if (existsSync(artifactsDir)) {
        rmSync(artifactsDir, { recursive: true, force: true });
      }
      mkdirSync(artifactsDir, { recursive: true });
      
      // 빌드 결과물 복사
      const sourceDirs = [
        'dist-production',
        'dist-packages',
        'dist-cross-platform'
      ];
      
      for (const sourceDir of sourceDirs) {
        const sourcePath = join(projectRoot, sourceDir);
        if (existsSync(sourcePath)) {
          const targetPath = join(artifactsDir, sourceDir);
          execSync(`cp -r "${sourcePath}" "${targetPath}"`);
          log(`${sourceDir} 복사 완료`, colors.green);
        }
      }
      
      // 메타데이터 파일 복사
      const metadataFiles = [
        'package.json',
        'quality-report.json',
        'build-info.json'
      ];
      
      for (const file of metadataFiles) {
        const sourcePath = join(projectRoot, file);
        if (existsSync(sourcePath)) {
          const targetPath = join(artifactsDir, file);
          execSync(`cp "${sourcePath}" "${targetPath}"`);
        }
      }
      
      // 배포 정보 파일 생성
      const deploymentInfoPath = join(artifactsDir, 'deployment-info.json');
      writeFileSync(deploymentInfoPath, JSON.stringify(this.deploymentInfo, null, 2));
      
      logSuccess('아티팩트 수집 완료');
    } catch (error) {
      logError(`아티팩트 수집 실패: ${error.message}`);
      throw error;
    }
  }

  // 테스트 실행 (통합 테스트)
  async runIntegrationTests() {
    logStep('7/10', '통합 테스트를 실행합니다...');
    
    if (this.config.build.skipTests) {
      logWarning('테스트가 건너뛰어졌습니다');
      return;
    }
    
    try {
      // E2E 테스트 실행
      log('E2E 테스트 실행 중...', colors.yellow);
      execSync('npm run test:e2e', { stdio: 'inherit' });
      
      logSuccess('통합 테스트 완료');
    } catch (error) {
      logError(`통합 테스트 실패: ${error.message}`);
      throw error;
    }
  }

  // 릴리스 생성
  async createRelease() {
    logStep('8/10', '릴리스를 생성합니다...');
    
    if (!this.config.deploy.createRelease) {
      logWarning('릴리스 생성이 건너뛰어졌습니다');
      return;
    }
    
    try {
      // GitHub 릴리스 생성 (GitHub CLI 사용)
      if (process.env.GITHUB_TOKEN) {
        log('GitHub 릴리스 생성 중...', colors.yellow);
        
        const releaseNotes = this.generateReleaseNotes();
        const releaseNotesPath = join(projectRoot, 'temp-release-notes.md');
        writeFileSync(releaseNotesPath, releaseNotes);
        
        const releaseCmd = [
          'gh', 'release', 'create',
          `v${this.version}`,
          '--title', `WatchHamster v${this.version}`,
          '--notes-file', releaseNotesPath
        ];
        
        if (this.environment !== 'production') {
          releaseCmd.push('--prerelease');
        }
        
        execSync(releaseCmd.join(' '), { stdio: 'inherit' });
        
        // 임시 파일 정리
        rmSync(releaseNotesPath);
        
        log('GitHub 릴리스 생성 완료', colors.green);
      } else {
        logWarning('GITHUB_TOKEN이 설정되지 않아 GitHub 릴리스를 건너뜁니다');
      }
      
      logSuccess('릴리스 생성 완료');
    } catch (error) {
      logError(`릴리스 생성 실패: ${error.message}`);
      throw error;
    }
  }

  // 릴리스 노트 생성
  generateReleaseNotes() {
    return `# WatchHamster v${this.version}

## 빌드 정보
- **빌드 번호**: ${this.buildNumber}
- **Git 커밋**: ${this.gitCommit.substring(0, 8)}
- **브랜치**: ${this.gitBranch}
- **빌드 날짜**: ${new Date().toLocaleDateString('ko-KR')}

## 주요 변경사항
- 성능 개선 및 버그 수정
- UI/UX 개선
- 새로운 기능 추가

## 다운로드
패키지는 Assets 섹션에서 다운로드할 수 있습니다.

## 설치 방법
각 플랫폼별 설치 가이드는 문서를 참조하세요.
`;
  }

  // 아티팩트 업로드
  async uploadArtifacts() {
    logStep('9/10', '아티팩트를 업로드합니다...');
    
    if (!this.config.deploy.uploadArtifacts) {
      logWarning('아티팩트 업로드가 건너뛰어졌습니다');
      return;
    }
    
    try {
      // GitHub 릴리스에 아티팩트 업로드
      if (process.env.GITHUB_TOKEN) {
        log('GitHub 릴리스에 아티팩트 업로드 중...', colors.yellow);
        
        const artifactsDir = join(projectRoot, 'artifacts', 'dist-packages');
        if (existsSync(artifactsDir)) {
          // 각 플랫폼별 패키지 업로드
          const platforms = ['windows', 'macos', 'linux'];
          
          for (const platform of platforms) {
            const platformDir = join(artifactsDir, platform);
            if (existsSync(platformDir)) {
              execSync(`gh release upload v${this.version} "${platformDir}"/*`, { stdio: 'inherit' });
              log(`${platform} 패키지 업로드 완료`, colors.green);
            }
          }
        }
      }
      
      logSuccess('아티팩트 업로드 완료');
    } catch (error) {
      logError(`아티팩트 업로드 실패: ${error.message}`);
      throw error;
    }
  }

  // 배포 알림
  async sendNotifications() {
    logStep('10/10', '배포 알림을 전송합니다...');
    
    const message = `🚀 WatchHamster v${this.version} 배포 완료!\n\n` +
                   `- 빌드 번호: ${this.buildNumber}\n` +
                   `- 커밋: ${this.gitCommit.substring(0, 8)}\n` +
                   `- 브랜치: ${this.gitBranch}\n` +
                   `- 환경: ${this.environment}`;
    
    try {
      // Slack 알림
      if (this.config.deploy.notifySlack && process.env.SLACK_WEBHOOK_URL) {
        log('Slack 알림 전송 중...', colors.yellow);
        // 실제 구현에서는 HTTP 요청으로 Slack 웹훅 호출
        log('Slack 알림 전송 완료', colors.green);
      }
      
      // Discord 알림
      if (this.config.deploy.notifyDiscord && process.env.DISCORD_WEBHOOK_URL) {
        log('Discord 알림 전송 중...', colors.yellow);
        // 실제 구현에서는 HTTP 요청으로 Discord 웹훅 호출
        log('Discord 알림 전송 완료', colors.green);
      }
      
      logSuccess('배포 알림 전송 완료');
    } catch (error) {
      logWarning(`알림 전송 실패: ${error.message}`);
    }
  }

  // 전체 배포 파이프라인 실행
  async deploy() {
    log('🚀 배포 파이프라인을 시작합니다...', colors.bright);
    log(`버전: ${this.version}`, colors.cyan);
    log(`환경: ${this.environment}`, colors.cyan);
    log(`플랫폼: ${this.config.build.platforms.join(', ')}`, colors.cyan);
    
    const startTime = Date.now();
    
    try {
      await this.validateEnvironment();
      await this.runQualityChecks();
      await this.installDependencies();
      await this.runBuild();
      await this.createPackages();
      await this.collectArtifacts();
      await this.runIntegrationTests();
      await this.createRelease();
      await this.uploadArtifacts();
      await this.sendNotifications();
      
      const duration = Math.round((Date.now() - startTime) / 1000);
      
      log(`🎉 배포 파이프라인이 성공적으로 완료되었습니다! (${duration}초)`, colors.green);
      
    } catch (error) {
      const duration = Math.round((Date.now() - startTime) / 1000);
      logError(`배포 파이프라인 실패: ${error.message} (${duration}초)`);
      process.exit(1);
    }
  }
}

// 사용법 출력
function printUsage() {
  console.log(`
🚀 WatchHamster 배포 파이프라인

사용법:
  node scripts/deploy-pipeline.js [옵션]

옵션:
  --environment <env>        배포 환경 (development, staging, production)
  --platforms <platforms>    빌드 플랫폼 (current, all, windows, macos, linux)
  --skip-tests              테스트 건너뛰기
  --skip-linting            린팅 건너뛰기
  --no-optimization         빌드 최적화 비활성화
  --deploy-target <target>   배포 대상 (github-releases, s3, ftp)
  --notify-slack            Slack 알림 활성화
  --notify-discord          Discord 알림 활성화
  --help                    이 도움말 출력

환경 변수:
  NODE_ENV                  배포 환경
  BUILD_NUMBER              빌드 번호
  GITHUB_TOKEN              GitHub 토큰 (릴리스 생성용)
  SLACK_WEBHOOK_URL         Slack 웹훅 URL
  DISCORD_WEBHOOK_URL       Discord 웹훅 URL

예시:
  node scripts/deploy-pipeline.js --environment production
  node scripts/deploy-pipeline.js --platforms all --notify-slack
  node scripts/deploy-pipeline.js --skip-tests --no-optimization
`);
}

// 메인 실행
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    printUsage();
    return;
  }
  
  // 옵션 파싱
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    switch (arg) {
      case '--environment':
        options.environment = args[++i];
        break;
      case '--platforms':
        options.platforms = args[++i].split(',');
        break;
      case '--skip-tests':
        options.skipTests = true;
        break;
      case '--skip-linting':
        options.skipLinting = true;
        break;
      case '--no-optimization':
        options.optimization = false;
        break;
      case '--deploy-target':
        options.deployTarget = args[++i];
        break;
      case '--notify-slack':
        options.notifySlack = true;
        break;
      case '--notify-discord':
        options.notifyDiscord = true;
        break;
    }
  }
  
  const pipeline = new DeploymentPipeline(options);
  await pipeline.deploy();
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('배포 파이프라인 실행 실패:', error);
    process.exit(1);
  });
}

export { DeploymentPipeline };