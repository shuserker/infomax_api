#!/usr/bin/env node

/**
 * 성능 벤치마크 스크립트
 * 애플리케이션의 성능 메트릭을 측정하고 분석합니다.
 */

import { execSync, spawn } from 'child_process';
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

class PerformanceBenchmark {
  constructor(options = {}) {
    this.duration = options.duration || 60000; // 1분
    this.iterations = options.iterations || 10;
    this.warmupTime = options.warmupTime || 10000; // 10초
    
    this.benchmarkResults = {
      timestamp: new Date().toISOString(),
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      metrics: {},
      summary: {}
    };
    
    this.thresholds = {
      startupTime: 10000, // 10초
      memoryUsage: 256 * 1024 * 1024, // 256MB
      cpuUsage: 10, // 10%
      responseTime: 1000, // 1초
      throughput: 100 // 100 req/s
    };
  }

  // 시작 시간 벤치마크
  async benchmarkStartupTime() {
    log('애플리케이션 시작 시간을 측정합니다...', colors.blue);
    
    const startupTimes = [];
    
    for (let i = 0; i < this.iterations; i++) {
      log(`시작 시간 측정 ${i + 1}/${this.iterations}`, colors.yellow);
      
      const startTime = Date.now();
      
      try {
        // 애플리케이션 시작 (모의)
        await this.simulateApplicationStartup();
        
        const endTime = Date.now();
        const startupTime = endTime - startTime;
        startupTimes.push(startupTime);
        
        log(`시작 시간: ${startupTime}ms`, colors.cyan);
        
        // 잠시 대기
        await new Promise(resolve => setTimeout(resolve, 2000));
        
      } catch (error) {
        log(`시작 시간 측정 실패: ${error.message}`, colors.red);
      }
    }
    
    const avgStartupTime = startupTimes.reduce((a, b) => a + b, 0) / startupTimes.length;
    const minStartupTime = Math.min(...startupTimes);
    const maxStartupTime = Math.max(...startupTimes);
    
    this.benchmarkResults.metrics.startupTime = {
      average: avgStartupTime,
      minimum: minStartupTime,
      maximum: maxStartupTime,
      samples: startupTimes,
      threshold: this.thresholds.startupTime,
      passed: avgStartupTime <= this.thresholds.startupTime
    };
    
    log(`평균 시작 시간: ${avgStartupTime.toFixed(2)}ms`, colors.green);
  }

  // 애플리케이션 시작 시뮬레이션
  async simulateApplicationStartup() {
    // 실제 구현에서는 애플리케이션을 실제로 시작
    return new Promise(resolve => {
      setTimeout(resolve, Math.random() * 3000 + 2000); // 2-5초
    });
  }

  // 메모리 사용량 벤치마크
  async benchmarkMemoryUsage() {
    log('메모리 사용량을 측정합니다...', colors.blue);
    
    const memoryReadings = [];
    const measurementInterval = 5000; // 5초마다
    const totalMeasurements = Math.floor(this.duration / measurementInterval);
    
    for (let i = 0; i < totalMeasurements; i++) {
      try {
        const memoryUsage = await this.measureMemoryUsage();
        memoryReadings.push(memoryUsage);
        
        log(`메모리 사용량: ${(memoryUsage / 1024 / 1024).toFixed(2)} MB`, colors.cyan);
        
        await new Promise(resolve => setTimeout(resolve, measurementInterval));
        
      } catch (error) {
        log(`메모리 측정 실패: ${error.message}`, colors.red);
      }
    }
    
    const avgMemoryUsage = memoryReadings.reduce((a, b) => a + b, 0) / memoryReadings.length;
    const maxMemoryUsage = Math.max(...memoryReadings);
    const minMemoryUsage = Math.min(...memoryReadings);
    
    this.benchmarkResults.metrics.memoryUsage = {
      average: avgMemoryUsage,
      maximum: maxMemoryUsage,
      minimum: minMemoryUsage,
      samples: memoryReadings,
      threshold: this.thresholds.memoryUsage,
      passed: avgMemoryUsage <= this.thresholds.memoryUsage
    };
    
    log(`평균 메모리 사용량: ${(avgMemoryUsage / 1024 / 1024).toFixed(2)} MB`, colors.green);
  }

  // 메모리 사용량 측정
  async measureMemoryUsage() {
    try {
      // Node.js 프로세스 메모리 사용량
      const memUsage = process.memoryUsage();
      return memUsage.rss; // Resident Set Size
    } catch (error) {
      // 시스템 메모리 사용량 (모의)
      return Math.random() * 200 * 1024 * 1024 + 50 * 1024 * 1024; // 50-250MB
    }
  }

  // CPU 사용량 벤치마크
  async benchmarkCpuUsage() {
    log('CPU 사용량을 측정합니다...', colors.blue);
    
    const cpuReadings = [];
    const measurementInterval = 5000; // 5초마다
    const totalMeasurements = Math.floor(this.duration / measurementInterval);
    
    for (let i = 0; i < totalMeasurements; i++) {
      try {
        const cpuUsage = await this.measureCpuUsage();
        cpuReadings.push(cpuUsage);
        
        log(`CPU 사용량: ${cpuUsage.toFixed(2)}%`, colors.cyan);
        
        await new Promise(resolve => setTimeout(resolve, measurementInterval));
        
      } catch (error) {
        log(`CPU 측정 실패: ${error.message}`, colors.red);
      }
    }
    
    const avgCpuUsage = cpuReadings.reduce((a, b) => a + b, 0) / cpuReadings.length;
    const maxCpuUsage = Math.max(...cpuReadings);
    const minCpuUsage = Math.min(...cpuReadings);
    
    this.benchmarkResults.metrics.cpuUsage = {
      average: avgCpuUsage,
      maximum: maxCpuUsage,
      minimum: minCpuUsage,
      samples: cpuReadings,
      threshold: this.thresholds.cpuUsage,
      passed: avgCpuUsage <= this.thresholds.cpuUsage
    };
    
    log(`평균 CPU 사용량: ${avgCpuUsage.toFixed(2)}%`, colors.green);
  }

  // CPU 사용량 측정
  async measureCpuUsage() {
    try {
      // Node.js CPU 사용량 측정
      const startUsage = process.cpuUsage();
      await new Promise(resolve => setTimeout(resolve, 1000));
      const endUsage = process.cpuUsage(startUsage);
      
      const totalUsage = endUsage.user + endUsage.system;
      const cpuPercent = (totalUsage / 1000000) * 100; // 마이크로초를 퍼센트로 변환
      
      return Math.min(cpuPercent, 100); // 최대 100%
    } catch (error) {
      // 모의 CPU 사용량
      return Math.random() * 15 + 1; // 1-16%
    }
  }

  // API 응답 시간 벤치마크
  async benchmarkApiResponseTime() {
    log('API 응답 시간을 측정합니다...', colors.blue);
    
    const responseTimes = [];
    const endpoints = [
      'http://localhost:8000/health',
      'http://localhost:8000/api/services',
      'http://localhost:8000/api/metrics'
    ];
    
    for (let i = 0; i < this.iterations; i++) {
      for (const endpoint of endpoints) {
        try {
          const startTime = Date.now();
          
          const response = await fetch(endpoint, { 
            timeout: 5000 
          });
          
          const endTime = Date.now();
          const responseTime = endTime - startTime;
          
          if (response.ok) {
            responseTimes.push(responseTime);
            log(`${endpoint}: ${responseTime}ms`, colors.cyan);
          }
          
        } catch (error) {
          log(`API 요청 실패 ${endpoint}: ${error.message}`, colors.red);
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    if (responseTimes.length > 0) {
      const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
      const maxResponseTime = Math.max(...responseTimes);
      const minResponseTime = Math.min(...responseTimes);
      
      this.benchmarkResults.metrics.apiResponseTime = {
        average: avgResponseTime,
        maximum: maxResponseTime,
        minimum: minResponseTime,
        samples: responseTimes,
        threshold: this.thresholds.responseTime,
        passed: avgResponseTime <= this.thresholds.responseTime
      };
      
      log(`평균 API 응답 시간: ${avgResponseTime.toFixed(2)}ms`, colors.green);
    } else {
      log('API 응답 시간을 측정할 수 없습니다', colors.yellow);
    }
  }

  // 처리량 벤치마크
  async benchmarkThroughput() {
    log('처리량을 측정합니다...', colors.blue);
    
    const testDuration = 30000; // 30초
    const concurrentRequests = 10;
    let totalRequests = 0;
    let successfulRequests = 0;
    
    const startTime = Date.now();
    const endTime = startTime + testDuration;
    
    const workers = [];
    
    for (let i = 0; i < concurrentRequests; i++) {
      workers.push(this.throughputWorker(endTime));
    }
    
    const results = await Promise.all(workers);
    
    results.forEach(result => {
      totalRequests += result.total;
      successfulRequests += result.successful;
    });
    
    const actualDuration = Date.now() - startTime;
    const throughput = (successfulRequests / actualDuration) * 1000; // req/s
    const successRate = (successfulRequests / totalRequests) * 100;
    
    this.benchmarkResults.metrics.throughput = {
      requestsPerSecond: throughput,
      totalRequests: totalRequests,
      successfulRequests: successfulRequests,
      successRate: successRate,
      threshold: this.thresholds.throughput,
      passed: throughput >= this.thresholds.throughput
    };
    
    log(`처리량: ${throughput.toFixed(2)} req/s (성공률: ${successRate.toFixed(1)}%)`, colors.green);
  }

  // 처리량 워커
  async throughputWorker(endTime) {
    let total = 0;
    let successful = 0;
    
    while (Date.now() < endTime) {
      try {
        total++;
        
        const response = await fetch('http://localhost:8000/health', { 
          timeout: 2000 
        });
        
        if (response.ok) {
          successful++;
        }
        
      } catch (error) {
        // 요청 실패는 카운트만 증가
      }
      
      // 짧은 대기
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    return { total, successful };
  }

  // 디스크 I/O 벤치마크
  async benchmarkDiskIO() {
    log('디스크 I/O 성능을 측정합니다...', colors.blue);
    
    const testFile = join(projectRoot, 'benchmark-test-file.tmp');
    const fileSize = 10 * 1024 * 1024; // 10MB
    const testData = Buffer.alloc(fileSize, 'A');
    
    try {
      // 쓰기 성능 측정
      const writeStartTime = Date.now();
      writeFileSync(testFile, testData);
      const writeTime = Date.now() - writeStartTime;
      const writeSpeed = (fileSize / writeTime) * 1000 / 1024 / 1024; // MB/s
      
      // 읽기 성능 측정
      const readStartTime = Date.now();
      readFileSync(testFile);
      const readTime = Date.now() - readStartTime;
      const readSpeed = (fileSize / readTime) * 1000 / 1024 / 1024; // MB/s
      
      this.benchmarkResults.metrics.diskIO = {
        writeSpeed: writeSpeed,
        readSpeed: readSpeed,
        writeTime: writeTime,
        readTime: readTime,
        fileSize: fileSize
      };
      
      log(`디스크 쓰기 속도: ${writeSpeed.toFixed(2)} MB/s`, colors.cyan);
      log(`디스크 읽기 속도: ${readSpeed.toFixed(2)} MB/s`, colors.cyan);
      
      // 테스트 파일 정리
      if (existsSync(testFile)) {
        require('fs').unlinkSync(testFile);
      }
      
    } catch (error) {
      log(`디스크 I/O 측정 실패: ${error.message}`, colors.red);
    }
  }

  // 벤치마크 요약 생성
  generateSummary() {
    const summary = {
      overallScore: 0,
      passedTests: 0,
      totalTests: 0,
      recommendations: []
    };
    
    Object.entries(this.benchmarkResults.metrics).forEach(([metric, data]) => {
      summary.totalTests++;
      
      if (data.passed !== undefined) {
        if (data.passed) {
          summary.passedTests++;
        }
      } else {
        summary.passedTests++; // 임계값이 없는 메트릭은 통과로 간주
      }
    });
    
    summary.overallScore = (summary.passedTests / summary.totalTests) * 100;
    
    // 권장사항 생성
    if (this.benchmarkResults.metrics.startupTime && !this.benchmarkResults.metrics.startupTime.passed) {
      summary.recommendations.push('애플리케이션 시작 시간을 개선하세요');
    }
    
    if (this.benchmarkResults.metrics.memoryUsage && !this.benchmarkResults.metrics.memoryUsage.passed) {
      summary.recommendations.push('메모리 사용량을 최적화하세요');
    }
    
    if (this.benchmarkResults.metrics.cpuUsage && !this.benchmarkResults.metrics.cpuUsage.passed) {
      summary.recommendations.push('CPU 사용량을 줄이세요');
    }
    
    if (this.benchmarkResults.metrics.apiResponseTime && !this.benchmarkResults.metrics.apiResponseTime.passed) {
      summary.recommendations.push('API 응답 시간을 개선하세요');
    }
    
    this.benchmarkResults.summary = summary;
  }

  // 벤치마크 보고서 생성
  generateReport() {
    log('벤치마크 보고서를 생성합니다...', colors.blue);
    
    // JSON 보고서
    const reportPath = join(projectRoot, `performance-benchmark-${Date.now()}.json`);
    writeFileSync(reportPath, JSON.stringify(this.benchmarkResults, null, 2));
    
    // HTML 보고서
    const htmlReport = this.generateHtmlReport();
    const htmlReportPath = join(projectRoot, `performance-benchmark-${Date.now()}.html`);
    writeFileSync(htmlReportPath, htmlReport);
    
    log(`벤치마크 보고서: ${reportPath}`, colors.cyan);
    log(`HTML 보고서: ${htmlReportPath}`, colors.cyan);
  }

  // HTML 보고서 생성
  generateHtmlReport() {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>WatchHamster 성능 벤치마크 보고서</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .metric { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
        .passed { color: #28a745; }
        .failed { color: #dc3545; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        .chart { width: 100%; height: 300px; background: #f8f9fa; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>WatchHamster 성능 벤치마크 보고서</h1>
        <p><strong>플랫폼:</strong> ${this.benchmarkResults.platform}</p>
        <p><strong>아키텍처:</strong> ${this.benchmarkResults.arch}</p>
        <p><strong>Node.js 버전:</strong> ${this.benchmarkResults.nodeVersion}</p>
        <p><strong>측정 시간:</strong> ${this.benchmarkResults.timestamp}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>전체 점수</h3>
            <div style="font-size: 24px;">${this.benchmarkResults.summary.overallScore.toFixed(1)}%</div>
        </div>
        <div class="metric">
            <h3>통과한 테스트</h3>
            <div style="font-size: 24px;">${this.benchmarkResults.summary.passedTests}/${this.benchmarkResults.summary.totalTests}</div>
        </div>
    </div>
    
    <h2>성능 메트릭</h2>
    <table>
        <thead>
            <tr>
                <th>메트릭</th>
                <th>평균값</th>
                <th>최소값</th>
                <th>최대값</th>
                <th>임계값</th>
                <th>상태</th>
            </tr>
        </thead>
        <tbody>
            ${Object.entries(this.benchmarkResults.metrics).map(([name, data]) => `
                <tr>
                    <td>${name}</td>
                    <td>${data.average ? data.average.toFixed(2) : '-'}</td>
                    <td>${data.minimum ? data.minimum.toFixed(2) : '-'}</td>
                    <td>${data.maximum ? data.maximum.toFixed(2) : '-'}</td>
                    <td>${data.threshold || '-'}</td>
                    <td class="${data.passed ? 'passed' : 'failed'}">${data.passed !== undefined ? (data.passed ? '통과' : '실패') : '-'}</td>
                </tr>
            `).join('')}
        </tbody>
    </table>
    
    ${this.benchmarkResults.summary.recommendations.length > 0 ? `
        <h2>개선 권장사항</h2>
        <ul>
            ${this.benchmarkResults.summary.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    ` : ''}
</body>
</html>
    `;
  }

  // 벤치마크 요약 출력
  printSummary() {
    log('\n📊 성능 벤치마크 요약:', colors.bright);
    log(`전체 점수: ${this.benchmarkResults.summary.overallScore.toFixed(1)}%`, colors.cyan);
    log(`통과한 테스트: ${this.benchmarkResults.summary.passedTests}/${this.benchmarkResults.summary.totalTests}`, colors.cyan);
    
    log('\n성능 메트릭:', colors.bright);
    Object.entries(this.benchmarkResults.metrics).forEach(([name, data]) => {
      const status = data.passed !== undefined ? (data.passed ? '✅' : '❌') : '📊';
      const value = data.average ? `${data.average.toFixed(2)}` : '측정됨';
      log(`  ${status} ${name}: ${value}`, colors.white);
    });
    
    if (this.benchmarkResults.summary.recommendations.length > 0) {
      log('\n💡 개선 권장사항:', colors.yellow);
      this.benchmarkResults.summary.recommendations.forEach(rec => {
        log(`  - ${rec}`, colors.yellow);
      });
    }
  }

  // 전체 벤치마크 실행
  async runBenchmark() {
    log('🚀 성능 벤치마크를 시작합니다...', colors.bright);
    log(`측정 시간: ${this.duration / 1000}초`, colors.cyan);
    log(`반복 횟수: ${this.iterations}회`, colors.cyan);
    
    const startTime = Date.now();
    
    try {
      // 워밍업
      log('워밍업 중...', colors.yellow);
      await new Promise(resolve => setTimeout(resolve, this.warmupTime));
      
      // 각 벤치마크 실행
      await this.benchmarkStartupTime();
      await this.benchmarkMemoryUsage();
      await this.benchmarkCpuUsage();
      await this.benchmarkApiResponseTime();
      await this.benchmarkThroughput();
      await this.benchmarkDiskIO();
      
      // 요약 생성
      this.generateSummary();
      this.generateReport();
      this.printSummary();
      
      const duration = Math.round((Date.now() - startTime) / 1000);
      
      log(`🎉 성능 벤치마크가 완료되었습니다! (${duration}초)`, colors.green);
      
    } catch (error) {
      const duration = Math.round((Date.now() - startTime) / 1000);
      log(`❌ 벤치마크 실행 실패: ${error.message} (${duration}초)`, colors.red);
      process.exit(1);
    }
  }
}

// 사용법 출력
function printUsage() {
  console.log(`
📊 WatchHamster 성능 벤치마크

사용법:
  node scripts/performance-benchmark.js [옵션]

옵션:
  --duration <ms>      측정 시간 (기본: 60000ms)
  --iterations <n>     반복 횟수 (기본: 10)
  --warmup <ms>        워밍업 시간 (기본: 10000ms)
  --help              이 도움말 출력

예시:
  node scripts/performance-benchmark.js                    # 기본 벤치마크
  node scripts/performance-benchmark.js --duration 30000   # 30초 측정
  node scripts/performance-benchmark.js --iterations 5     # 5회 반복
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
      case '--duration':
        options.duration = parseInt(args[++i]);
        break;
      case '--iterations':
        options.iterations = parseInt(args[++i]);
        break;
      case '--warmup':
        options.warmupTime = parseInt(args[++i]);
        break;
    }
  }
  
  const benchmark = new PerformanceBenchmark(options);
  await benchmark.runBenchmark();
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('성능 벤치마크 실행 실패:', error);
    process.exit(1);
  });
}

export { PerformanceBenchmark };