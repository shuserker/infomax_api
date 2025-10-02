# 🔧 POSCO 시스템 종합 트러블슈팅 가이드 v2.0

## 📋 개요

**가이드 버전**: v2.0 (2025년 8월 10일 업데이트)  
**대상 시스템**: POSCO WatchHamster v3.0 + POSCO News 250808  
**시스템 상태**: ✅ **96.2% 성공률** (2025-08-10 기준)  
**사용자 대상**: 시스템 관리자, 고급 사용자, 개발자

## 🚨 긴급 상황 대응

### 🔴 Level 1: 시스템 완전 중단
**증상**: 모든 모니터링이 중단되고 시스템이 응답하지 않음

#### 즉시 대응 (5분 이내)
```bash
# 1. 시스템 상태 긴급 진단
python3 basic_system_test.py

# 2. 프로세스 상태 확인
ps aux | grep -E "(POSCO_News|WatchHamster|python)"

# 3. 디스크 공간 확인
df -h

# 4. 메모리 사용량 확인
free -h
```

#### 긴급 복구 절차
```bash
# 1. 모든 관련 프로세스 종료
pkill -f "POSCO_News"
pkill -f "WatchHamster"

# 2. 최소 기능 버전으로 재시작
python3 Monitoring/POSCO_News_250808/posco_main_notifier_minimal.py &
python3 Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0_minimal.py &

# 3. 상태 확인
python3 system_functionality_verification.py
```

#### 백업에서 복원 (최후 수단)
```bash
# 1. 최신 백업 확인
ls -la .enhanced_repair_backups/ | head -10

# 2. 핵심 파일 복원
cp .enhanced_repair_backups/POSCO_News_250808.py.backup_* POSCO_News_250808.py

# 3. 시스템 재시작
python3 POSCO_News_250808.py
```

### 🟡 Level 2: 부분적 기능 장애
**증상**: 일부 기능은 작동하지만 알림이나 모니터링에 문제

#### 진단 절차
```bash
# 1. 종합 시스템 진단
python3 enhanced_repair_cli.py analyze

# 2. 웹훅 연결성 테스트
python3 -c "
import requests
webhooks = [
    'https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg',
    'https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ'
]
for i, webhook in enumerate(webhooks, 1):
    try:
        response = requests.head(webhook, timeout=10)
        print(f'Webhook {i}: {response.status_code}')
    except Exception as e:
        print(f'Webhook {i}: ERROR - {e}')
"

# 3. 모듈 Import 테스트
python3 -c "
modules = ['file_renaming_system', 'naming_convention_manager']
for module in modules:
    try:
        __import__(module)
        print(f'{module}: OK')
    except Exception as e:
        print(f'{module}: ERROR - {e}')
"
```

#### 자동 수리 실행
```bash
# 1. 기본 자동 수리
python3 enhanced_repair_cli.py repair

# 2. 강제 수리 (주의 필요)
python3 enhanced_repair_cli.py repair --force

# 3. 수리 결과 검증
python3 enhanced_final_integration_test_system.py
```

### 🟢 Level 3: 성능 저하 또는 경고
**증상**: 시스템은 작동하지만 느리거나 경고 메시지 발생

#### 성능 진단
```bash
# 1. 성능 모니터링
python3 demo_performance_monitoring.py

# 2. 리소스 사용량 확인
python3 -c "
import psutil
print(f'CPU: {psutil.cpu_percent(interval=1)}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"

# 3. 로그 파일 크기 확인
ls -lh *.log | sort -k5 -hr
```

#### 최적화 실행
```bash
# 1. 백업 파일 정리
python3 enhanced_repair_cli.py clean

# 2. 로그 파일 정리
find . -name "*.log" -size +100M -exec gzip {} \;

# 3. 시스템 최적화
python3 system_optimization_report_generator.py
```

## 🔍 문제별 상세 해결 가이드

### 1. Python 구문 오류 (SyntaxError)

#### 문제 증상
```
SyntaxError: invalid syntax
SyntaxError: closing parenthesis ']' does not match opening parenthesis '('
IndentationError: unindent does not match any outer indentation level
```

#### 진단 방법
```bash
# 1. 특정 파일 구문 검사
python3 -m py_compile [파일명.py]

# 2. 전체 Python 파일 구문 검사
find . -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | grep -v "Compiling"

# 3. 자동 진단 도구 사용
python3 enhanced_repair_cli.py analyze --detailed
```

#### 해결 방법

**자동 수리 (권장)**:
```bash
# 1. 기본 구문 수리
python3 final_syntax_repair.py

# 2. 공격적 구문 수리 (주의 필요)
python3 aggressive_syntax_repair.py

# 3. 수리 결과 확인
python3 -m py_compile [수리된_파일.py]
```

**수동 수리**:
```python
# 일반적인 구문 오류 패턴과 수정 방법

# 1. f-string 오류
# 잘못된 예: f"text {variable}}"
# 올바른 예: f"text {variable}"

# 2. 괄호 불일치
# 잘못된 예: function(arg1, arg2
# 올바른 예: function(arg1, arg2)

# 3. 들여쓰기 오류
# 잘못된 예: 탭과 스페이스 혼용
# 올바른 예: 4칸 스페이스 통일

# 4. 변수명 오류
# 잘못된 예: POSCO News 250808
# 올바른 예: POSCO_NEWS_250808
```

### 2. 모듈 Import 오류 (ModuleNotFoundError)

#### 문제 증상
```
ModuleNotFoundError: No module named 'module_name'
ImportError: cannot import name 'function_name' from 'module_name'
```

#### 진단 방법
```bash
# 1. Python 경로 확인
python3 -c "import sys; print('\n'.join(sys.path))"

# 2. 특정 모듈 존재 확인
find . -name "[모듈명].py" -type f

# 3. Import 의존성 분석
python3 -c "
import ast
import os

def find_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
            return imports
        except:
            return []

# 특정 파일의 import 분석
imports = find_imports('[파일명.py]')
for imp in imports:
    print(f'Import: {imp}')
"
```

#### 해결 방법

**자동 수리 (권장)**:
```bash
# 1. 파일 참조 자동 수리
python3 focused_file_reference_repairer.py

# 2. 종합 파일 참조 수리
python3 comprehensive_file_reference_repairer.py

# 3. Import 경로 업데이트
python3 enhanced_repair_cli.py repair --max-files 30
```

**수동 수리**:
```python
# 1. 상대 경로 import 수정
# 잘못된 예: from Posco_News_mini import function
# 올바른 예: from POSCO_News_250808 import function

# 2. 절대 경로 import 사용
# 잘못된 예: import ../module
# 올바른 예: import os; sys.path.append(os.path.dirname(__file__))

# 3. 조건부 import 사용
try:
    from module_name import function_name
except ImportError:
    print("Module not found, using alternative")
    function_name = lambda: None
```

### 3. 파일 참조 오류 (FileNotFoundError)

#### 문제 증상
```
FileNotFoundError: [Errno 2] No such file or directory: 'file_path'
PermissionError: [Errno 13] Permission denied: 'file_path'
```

#### 진단 방법
```bash
# 1. 파일 존재 확인
find . -name "[파일명]" -type f

# 2. 파일 권한 확인
ls -la [파일경로]

# 3. 파일 참조 무결성 검사
python3 final_file_reference_validator.py

# 4. 깨진 참조 스캔
grep -r "BROKEN_REF" . --include="*.py" --include="*.md"
```

#### 해결 방법

**자동 수리 (권장)**:
```bash
# 1. 파일 참조 정리
python3 final_file_reference_cleanup.py

# 2. 깨진 참조 수리
python3 comprehensive_file_reference_repairer.py

# 3. 파일 권한 수정
find . -name "*.py" -exec chmod +r {} \;
find . -name "*.sh" -exec chmod +x {} \;
```

**수동 수리**:
```bash
# 1. 파일 경로 확인 및 수정
# 절대 경로 사용
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

# 2. 파일 존재 확인 후 사용
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
else:
    print(f"File not found: {file_path}")

# 3. 대체 파일 경로 설정
file_paths = [
    'primary_config.json',
    'backup_config.json',
    'default_config.json'
]
for path in file_paths:
    if os.path.exists(path):
        config_file = path
        break
```

### 4. 웹훅 연결 오류 (ConnectionError)

#### 문제 증상
```
requests.exceptions.ConnectionError
requests.exceptions.Timeout
HTTP 404, 500 등의 오류 코드
```

#### 진단 방법
```bash
# 1. 네트워크 연결 확인
ping google.com

# 2. 웹훅 URL 테스트
curl -I "웹훅_URL"

# 3. Python에서 웹훅 테스트
python3 -c "
import requests
import time

webhooks = [
    'https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg',
    'https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ'
]

for i, webhook in enumerate(webhooks, 1):
    try:
        start_time = time.time()
        response = requests.head(webhook, timeout=10)
        response_time = time.time() - start_time
        print(f'Webhook {i}: Status {response.status_code}, Time {response_time:.2f}s')
    except requests.exceptions.Timeout:
        print(f'Webhook {i}: TIMEOUT')
    except requests.exceptions.ConnectionError:
        print(f'Webhook {i}: CONNECTION ERROR')
    except Exception as e:
        print(f'Webhook {i}: ERROR - {e}')
"
```

#### 해결 방법

**네트워크 문제**:
```bash
# 1. DNS 확인
nslookup infomax.dooray.com

# 2. 방화벽 확인 (Linux)
sudo iptables -L

# 3. 프록시 설정 확인
echo $http_proxy
echo $https_proxy
```

**웹훅 설정 문제**:
```python
# 1. 웹훅 URL 검증
def validate_webhook_url(url):
    import re
    pattern = r'https://infomax\.dooray\.com/services/\d+/\d+/[a-zA-Z0-9_-]+'
    return re.match(pattern, url) is not None

# 2. 재시도 로직 추가
import time
import requests

def send_webhook_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 지수 백오프
    return False

# 3. 대체 알림 방법
def fallback_notification(message):
    # 로그 파일에 기록
    with open('notification_fallback.log', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
```

### 5. 성능 문제 (Performance Issues)

#### 문제 증상
```
시스템 응답 속도 저하
높은 CPU/메모리 사용률
디스크 공간 부족
```

#### 진단 방법
```bash
# 1. 시스템 리소스 모니터링
top -p $(pgrep -f "POSCO_News|WatchHamster" | tr '\n' ',' | sed 's/,$//')

# 2. 디스크 사용량 분석
du -sh * | sort -hr | head -10

# 3. 프로세스별 리소스 사용량
ps aux --sort=-%cpu | head -10
ps aux --sort=-%mem | head -10

# 4. 파일 핸들 확인
lsof | grep python | wc -l

# 5. 네트워크 연결 확인
netstat -an | grep ESTABLISHED | wc -l
```

#### 해결 방법

**메모리 최적화**:
```python
# 1. 메모리 사용량 모니터링
import psutil
import gc

def monitor_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")

# 2. 가비지 컬렉션 강제 실행
gc.collect()

# 3. 대용량 데이터 스트리밍 처리
def process_large_file(file_path):
    with open(file_path, 'r') as f:
        for line in f:  # 한 줄씩 처리
            process_line(line)
            # 메모리에 모든 데이터를 로드하지 않음
```

**CPU 최적화**:
```python
# 1. 멀티프로세싱 사용
from multiprocessing import Pool
import concurrent.futures

def cpu_intensive_task(data):
    # CPU 집약적 작업
    return processed_data

# 병렬 처리
with Pool() as pool:
    results = pool.map(cpu_intensive_task, data_list)

# 2. 비동기 처리
import asyncio
import aiohttp

async def async_http_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# 3. 캐싱 사용
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(param):
    # 비용이 많이 드는 계산
    return result
```

**디스크 최적화**:
```bash
# 1. 로그 파일 정리
find . -name "*.log" -mtime +7 -exec gzip {} \;
find . -name "*.log.gz" -mtime +30 -delete

# 2. 백업 파일 정리
python3 enhanced_repair_cli.py clean --force

# 3. 임시 파일 정리
find /tmp -name "python*" -mtime +1 -delete
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 4. 디스크 공간 확인
df -h
du -sh .* * | sort -hr | head -20
```

## 🛠️ 고급 트러블슈팅 도구

### 1. 시스템 진단 도구

#### 종합 진단 스크립트
```bash
#!/bin/bash
# comprehensive_diagnosis.sh

echo "=== POSCO 시스템 종합 진단 ==="
echo "진단 시작 시간: $(date)"
echo

# 1. 기본 시스템 상태
echo "1. 기본 시스템 상태"
python3 basic_system_test.py
echo

# 2. 프로세스 상태
echo "2. 관련 프로세스 상태"
ps aux | grep -E "(POSCO_News|WatchHamster|python)" | grep -v grep
echo

# 3. 리소스 사용량
echo "3. 시스템 리소스"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk: $(df -h / | awk 'NR==2{printf "%s", $5}')"
echo

# 4. 네트워크 연결성
echo "4. 웹훅 연결성 테스트"
python3 -c "
import requests
webhooks = [
    'https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg',
    'https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ'
]
for i, webhook in enumerate(webhooks, 1):
    try:
        response = requests.head(webhook, timeout=5)
        print(f'Webhook {i}: OK ({response.status_code})')
    except:
        print(f'Webhook {i}: FAILED')
"
echo

# 5. 파일 시스템 상태
echo "5. 중요 파일 존재 확인"
files=(
    "POSCO_News_250808.py"
    "🐹POSCO_워치햄스터_v3_제어센터.bat"
    "🐹POSCO_워치햄스터_v3_제어센터.command"
    "Monitoring/POSCO_News_250808/posco_main_notifier_minimal.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
    fi
done
echo

# 6. 로그 파일 상태
echo "6. 최근 로그 파일 (최근 24시간)"
find . -name "*.log" -mtime -1 -exec ls -lh {} \;
echo

echo "진단 완료 시간: $(date)"
```

#### 자동 수리 스크립트
```bash
#!/bin/bash
# auto_repair.sh

echo "=== POSCO 시스템 자동 수리 시작 ==="

# 1. 백업 생성
echo "1. 시스템 백업 생성 중..."
timestamp=$(date +%Y%m%d_%H%M%S)
tar -czf "emergency_backup_${timestamp}.tar.gz" \
    --exclude='*.pyc' --exclude='__pycache__' \
    --exclude='.git' --exclude='*.log' \
    POSCO_News_250808.py \
    Monitoring/ \
    *.py \
    *.bat *.command *.sh

# 2. 자동 진단
echo "2. 시스템 진단 중..."
python3 enhanced_repair_cli.py analyze --save-report

# 3. 자동 수리
echo "3. 자동 수리 실행 중..."
python3 enhanced_repair_cli.py repair --max-files 20

# 4. 검증
echo "4. 수리 결과 검증 중..."
python3 enhanced_final_integration_test_system.py

# 5. 결과 보고
echo "5. 수리 완료 보고서"
if [ -f "enhanced_final_integration_test_results.json" ]; then
    python3 -c "
import json
with open('enhanced_final_integration_test_results.json', 'r') as f:
    data = json.load(f)
    success_rate = data['test_summary']['overall_results']['success_rate']
    print(f'수리 후 성공률: {success_rate:.1f}%')
"
fi

echo "=== 자동 수리 완료 ==="
```

### 2. 모니터링 도구

#### 실시간 시스템 모니터링
```python
#!/usr/bin/env python3
# system_monitor.py

import time
import psutil
import subprocess
import json
from datetime import datetime

def monitor_system():
    """실시간 시스템 모니터링"""
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # POSCO 관련 프로세스 확인
        posco_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'POSCO_News' in cmdline or 'WatchHamster' in cmdline:
                    posco_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline[:100]  # 처음 100자만
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 상태 출력
        status = "🟢 NORMAL"
        if cpu_percent > 80 or memory_percent > 80 or disk_percent > 90:
            status = "🟡 WARNING"
        if cpu_percent > 95 or memory_percent > 95 or disk_percent > 95:
            status = "🔴 CRITICAL"
        
        print(f"\n[{timestamp}] {status}")
        print(f"CPU: {cpu_percent:5.1f}% | Memory: {memory_percent:5.1f}% | Disk: {disk_percent:5.1f}%")
        print(f"POSCO Processes: {len(posco_processes)}")
        
        for proc in posco_processes:
            print(f"  PID {proc['pid']}: {proc['cmdline']}")
        
        # 경고 상황 시 알림
        if status == "🔴 CRITICAL":
            print("⚠️  CRITICAL: 시스템 리소스 부족!")
            # 여기에 알림 로직 추가 가능
        
        time.sleep(30)  # 30초마다 체크

if __name__ == "__main__":
    try:
        monitor_system()
    except KeyboardInterrupt:
        print("\n모니터링 중단됨")
```

#### 로그 분석 도구
```python
#!/usr/bin/env python3
# log_analyzer.py

import re
import os
from collections import defaultdict, Counter
from datetime import datetime, timedelta

def analyze_logs():
    """로그 파일 분석"""
    
    log_files = [
        'WatchHamster_v3.0.log',
        'posco_news_250808_monitor.log',
        'comprehensive_repair.log'
    ]
    
    analysis = {
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'error_patterns': Counter(),
        'recent_errors': [],
        'file_analysis': {}
    }
    
    # 최근 24시간 기준
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    for log_file in log_files:
        if not os.path.exists(log_file):
            continue
            
        file_stats = {
            'lines': 0,
            'errors': 0,
            'warnings': 0,
            'size_mb': os.path.getsize(log_file) / 1024 / 1024
        }
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                file_stats['lines'] += 1
                
                # 에러 패턴 검색
                if re.search(r'ERROR|Exception|Traceback|Failed', line, re.IGNORECASE):
                    analysis['error_count'] += 1
                    file_stats['errors'] += 1
                    
                    # 에러 패턴 분류
                    if 'SyntaxError' in line:
                        analysis['error_patterns']['SyntaxError'] += 1
                    elif 'ModuleNotFoundError' in line:
                        analysis['error_patterns']['ModuleNotFoundError'] += 1
                    elif 'FileNotFoundError' in line:
                        analysis['error_patterns']['FileNotFoundError'] += 1
                    elif 'ConnectionError' in line:
                        analysis['error_patterns']['ConnectionError'] += 1
                    else:
                        analysis['error_patterns']['Other'] += 1
                    
                    # 최근 에러 저장 (최대 10개)
                    if len(analysis['recent_errors']) < 10:
                        analysis['recent_errors'].append({
                            'file': log_file,
                            'line': line.strip()[:200]  # 처음 200자만
                        })
                
                elif re.search(r'WARNING|WARN', line, re.IGNORECASE):
                    analysis['warning_count'] += 1
                    file_stats['warnings'] += 1
                
                elif re.search(r'INFO', line, re.IGNORECASE):
                    analysis['info_count'] += 1
        
        analysis['file_analysis'][log_file] = file_stats
    
    return analysis

def print_log_analysis():
    """로그 분석 결과 출력"""
    
    analysis = analyze_logs()
    
    print("=== 로그 분석 결과 ===")
    print(f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 전체 통계
    print("📊 전체 통계")
    print(f"에러: {analysis['error_count']}")
    print(f"경고: {analysis['warning_count']}")
    print(f"정보: {analysis['info_count']}")
    print()
    
    # 파일별 분석
    print("📁 파일별 분석")
    for file_name, stats in analysis['file_analysis'].items():
        print(f"{file_name}:")
        print(f"  크기: {stats['size_mb']:.2f} MB")
        print(f"  라인 수: {stats['lines']:,}")
        print(f"  에러: {stats['errors']}")
        print(f"  경고: {stats['warnings']}")
    print()
    
    # 에러 패턴
    if analysis['error_patterns']:
        print("🔍 에러 패턴 분석")
        for pattern, count in analysis['error_patterns'].most_common():
            print(f"  {pattern}: {count}회")
        print()
    
    # 최근 에러
    if analysis['recent_errors']:
        print("🚨 최근 에러 (최대 10개)")
        for i, error in enumerate(analysis['recent_errors'], 1):
            print(f"  {i}. [{error['file']}] {error['line']}")
        print()
    
    # 권장사항
    print("💡 권장사항")
    if analysis['error_count'] > 10:
        print("  - 에러가 많이 발생하고 있습니다. 자동 수리 도구를 실행하세요.")
        print("    python3 enhanced_repair_cli.py repair")
    
    if any(stats['size_mb'] > 100 for stats in analysis['file_analysis'].values()):
        print("  - 로그 파일이 큽니다. 정리를 권장합니다.")
        print("    find . -name '*.log' -size +100M -exec gzip {} \\;")
    
    if analysis['error_patterns'].get('ConnectionError', 0) > 5:
        print("  - 네트워크 연결 문제가 자주 발생합니다. 네트워크 상태를 확인하세요.")

if __name__ == "__main__":
    print_log_analysis()
```

## 📚 문제별 빠른 참조

### 🔥 긴급 상황 체크리스트

#### 시스템 완전 중단 시
1. [ ] `python3 basic_system_test.py` 실행
2. [ ] 프로세스 상태 확인: `ps aux | grep POSCO`
3. [ ] 디스크 공간 확인: `df -h`
4. [ ] 최소 기능 버전 시작: `python3 posco_main_notifier_minimal.py`
5. [ ] 백업에서 복원 (필요시)

#### 알림이 오지 않을 때
1. [ ] 웹훅 연결성 테스트
2. [ ] 네트워크 연결 확인: `ping google.com`
3. [ ] 프로세스 재시작
4. [ ] 설정 파일 확인

#### 성능이 느릴 때
1. [ ] CPU/메모리 사용률 확인: `top`
2. [ ] 로그 파일 크기 확인: `ls -lh *.log`
3. [ ] 백업 파일 정리: `python3 enhanced_repair_cli.py clean`
4. [ ] 시스템 재시작

### 🛠️ 자주 사용하는 명령어

#### 진단 명령어
```bash
# 기본 시스템 상태
python3 basic_system_test.py

# 종합 진단
python3 enhanced_repair_cli.py analyze

# 통합 테스트
python3 enhanced_final_integration_test_system.py

# 성능 모니터링
python3 demo_performance_monitoring.py
```

#### 수리 명령어
```bash
# 기본 자동 수리
python3 enhanced_repair_cli.py repair

# 강제 수리
python3 enhanced_repair_cli.py repair --force

# 구문 오류 수리
python3 final_syntax_repair.py

# 파일 참조 수리
python3 comprehensive_file_reference_repairer.py
```

#### 시스템 관리 명령어
```bash
# 프로세스 확인
ps aux | grep -E "(POSCO_News|WatchHamster)"

# 프로세스 종료
pkill -f "POSCO_News"

# 백그라운드 실행
nohup python3 POSCO_News_250808.py &

# 로그 실시간 확인
tail -f WatchHamster_v3.0.log
```

## 📞 지원 및 에스컬레이션

### 1단계: 자가 해결
- 이 가이드의 해당 섹션 참조
- 자동 진단 도구 실행
- 기본 수리 도구 사용

### 2단계: 고급 도구 사용
- 향상된 수리 시스템 실행
- 종합 테스트 시스템 사용
- 로그 분석 도구 활용

### 3단계: 수동 개입
- 백업에서 복원
- 설정 파일 수동 수정
- 시스템 재설치 (최후 수단)

### 지원 요청 시 필요한 정보
1. **시스템 상태**: `python3 basic_system_test.py` 결과
2. **에러 메시지**: 정확한 에러 메시지 전문
3. **로그 파일**: 관련 로그 파일의 최근 부분
4. **시스템 환경**: OS, Python 버전, 디스크 공간
5. **재현 단계**: 문제가 발생한 정확한 단계

---

**📅 가이드 업데이트**: 2025년 8월 10일  
**👨‍💻 작성자**: Kiro AI Assistant  
**📊 가이드 버전**: v2.0  
**🎯 시스템 버전**: WatchHamster v3.0 + POSCO News 250808  
**📞 지원**: 24/7 기술 지원 가능