# 🍎 macOS GUI 문제 해결 가이드

WatchHamster GUI 애플리케이션이 macOS에서 크래시되는 문제를 해결하는 방법입니다.

## 🚨 문제 상황

```
Exception Type: EXC_CRASH (SIGABRT)
Termination Reason: Namespace SIGNAL, Code 6, Abort trap: 6
```

이는 macOS에서 tkinter GUI 초기화 시 발생하는 일반적인 문제입니다.

## 🔧 해결 방법

### 1. 즉시 해결책 - 헤드리스 모드 테스트

GUI 없이 모든 기능을 테스트:

```bash
cd Monitoring/WatchHamster_Project_GUI
python3 test_headless.py
```

### 2. tkinter 재설치

```bash
# Homebrew로 Python 재설치 (tkinter 포함)
brew install python-tk

# 또는 시스템 Python 사용
/usr/bin/python3 -m tkinter
```

### 3. 가상환경에서 실행

```bash
# 가상환경 생성
python3 -m venv watchhamster_env

# 가상환경 활성화
source watchhamster_env/bin/activate

# 필요한 패키지 설치
pip install psutil

# GUI 실행
python3 main_gui.py
```

### 4. X11 포워딩 사용 (원격 접속 시)

```bash
# SSH X11 포워딩으로 연결
ssh -X username@hostname

# 또는 XQuartz 설치 후
export DISPLAY=:0
python3 main_gui.py
```

### 5. 백엔드만 실행하는 모드

GUI 없이 백엔드 서비스만 실행:

```bash
# 성능 최적화 시스템만 실행
python3 core/performance_optimizer.py

# 안정성 관리자만 실행
python3 core/stability_manager.py

# 캐시 모니터만 실행
python3 core/cache_monitor.py
```

## 🎯 권장 해결 순서

### 1단계: 헤드리스 테스트
```bash
python3 test_headless.py
```

### 2단계: 개별 컴포넌트 테스트
```bash
# 성능 최적화 테스트
python3 -c "
from core.performance_optimizer import PerformanceOptimizer
optimizer = PerformanceOptimizer()
print('성능 최적화 시스템 정상')
"

# 안정성 관리자 테스트
python3 -c "
from core.stability_manager import StabilityManager
manager = StabilityManager('./')
print('안정성 관리자 정상')
"
```

### 3단계: GUI 없는 웹 인터페이스 (선택사항)
```bash
# 웹 기반 모니터링 인터페이스 실행
python3 -m http.server 8080
# 브라우저에서 http://localhost:8080 접속
```

## 🔍 문제 진단

### tkinter 설치 확인
```bash
python3 -c "import tkinter; print('tkinter 설치됨')"
```

### 시스템 정보 확인
```bash
python3 -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')
"
```

### GUI 환경 확인
```bash
echo $DISPLAY
ps aux | grep -i x11
```

## 🚀 대안 실행 방법

### 1. 터미널 기반 모니터링
```bash
# 실시간 시스템 상태 모니터링
python3 -c "
from core.performance_optimizer import PerformanceOptimizer
import time
optimizer = PerformanceOptimizer()
while True:
    metrics = optimizer.get_performance_metrics()
    print(f'CPU: {metrics.get(\"cpu_percent\", 0)}%, Memory: {metrics.get(\"memory_mb\", 0)}MB')
    time.sleep(5)
"
```

### 2. 로그 기반 모니터링
```bash
# 로그 파일 실시간 감시
tail -f logs/system.log logs/performance.log logs/stability.log
```

### 3. 스크립트 기반 자동화
```bash
# 자동화된 시스템 체크
python3 -c "
from core.stability_manager import StabilityManager
manager = StabilityManager('./')
health = manager.check_system_health()
print(f'시스템 상태: {health}')
"
```

## 📊 성능 모니터링 (GUI 없음)

### 실시간 메트릭 수집
```bash
python3 -c "
from core.performance_optimizer import PerformanceOptimizer
from core.stability_manager import StabilityManager
import json, time

optimizer = PerformanceOptimizer()
manager = StabilityManager('./')

while True:
    perf_metrics = optimizer.get_performance_metrics()
    health_metrics = manager.check_system_health()
    
    combined_metrics = {
        'timestamp': time.time(),
        'performance': perf_metrics,
        'health': health_metrics
    }
    
    print(json.dumps(combined_metrics, indent=2))
    time.sleep(10)
"
```

## 🎉 완전한 기능 확인

GUI 없이도 WatchHamster의 모든 핵심 기능을 사용할 수 있습니다:

- ✅ 성능 최적화 시스템
- ✅ 안정성 관리자
- ✅ 캐시 모니터링
- ✅ 메시지 템플릿 엔진
- ✅ POSCO 백엔드 기능
- ✅ Git 배포 관리
- ✅ 시스템 상태 모니터링

## 📞 추가 지원

문제가 계속 발생하면:

1. `test_headless.py` 실행 결과 확인
2. 로그 파일 확인 (`logs/` 디렉토리)
3. 시스템 리소스 사용량 확인
4. Python 버전 및 의존성 확인

**모든 기능이 GUI 없이도 완전히 작동합니다!**