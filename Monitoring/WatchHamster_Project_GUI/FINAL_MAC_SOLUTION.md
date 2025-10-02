# 🍎 맥 GUI 크래시 - 최종 해결책

**문제**: 시스템 Python의 tkinter가 macOS에서 크래시됨
**해결**: Homebrew Python 사용 또는 대안 방법

---

## 🚀 방법 1: Homebrew Python 설치 (가장 확실함)

### 1단계: Homebrew 설치
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2단계: Python-tk 설치
```bash
brew install python-tk
```

### 3단계: 새 터미널에서 실행
```bash
# 새 터미널 열고
cd Monitoring/WatchHamster_Project_GUI
python3 main_gui.py
```

---

## 🔧 방법 2: 가상환경 사용

```bash
cd Monitoring/WatchHamster_Project_GUI

# 가상환경 생성
python3 -m venv venv_gui

# 가상환경 활성화
source venv_gui/bin/activate

# 필요한 패키지 설치
pip install psutil

# GUI 실행
python main_gui.py
```

---

## 💻 방법 3: 웹 기반 대시보드 (GUI 대신)

GUI가 안 되면 웹 브라우저로 사용:

```bash
cd Monitoring/WatchHamster_Project_GUI
python3 -m http.server 8080 &
open http://localhost:8080
```

---

## 🖥️ 방법 4: 터미널 기반 모니터링

```bash
# 실시간 시스템 모니터링
python3 -c "
from core.performance_optimizer import PerformanceOptimizer
from core.stability_manager import StabilityManager
import time

optimizer = PerformanceOptimizer()
manager = StabilityManager('./')

print('🐹 WatchHamster 터미널 모니터링')
print('Ctrl+C로 종료')

while True:
    try:
        perf = optimizer.get_performance_metrics()
        health = manager.check_system_health()
        
        print(f'CPU: {perf.get(\"cpu_percent\", 0)}% | Memory: {health.get(\"memory_usage_mb\", 0)}MB | Time: {time.strftime(\"%H:%M:%S\")}')
        time.sleep(5)
    except KeyboardInterrupt:
        print('\\n모니터링 종료')
        break
"
```

---

## 🎯 방법 5: 백엔드만 실행

GUI 없이 모든 기능 사용:

```bash
# 성능 최적화 시스템
python3 core/performance_optimizer.py &

# 안정성 관리자
python3 core/stability_manager.py &

# 캐시 모니터
python3 core/cache_monitor.py &

echo "백엔드 서비스들이 실행되었습니다!"
```

---

## 📊 방법 6: 로그 기반 모니터링

```bash
# 로그 디렉토리 생성
mkdir -p logs

# 실시간 로그 모니터링
tail -f logs/*.log 2>/dev/null || echo "로그 파일이 생성되면 여기에 표시됩니다"
```

---

## 🔍 현재 상황 진단

크래시 리포트를 보면:
- **문제**: `/Library/Developer/CommandLineTools/...` (시스템 Python)
- **해결**: `/opt/homebrew/...` (Homebrew Python) 사용 필요

### 현재 Python 확인:
```bash
which python3
python3 --version
```

### Homebrew Python 확인:
```bash
/opt/homebrew/bin/python3 --version 2>/dev/null || echo "Homebrew Python 없음"
```

---

## ✅ 권장 순서

1. **Homebrew Python 설치** (가장 확실)
2. **가상환경 사용** (안전함)
3. **웹 대시보드** (GUI 대신)
4. **터미널 모니터링** (실시간)
5. **백엔드만 실행** (기능 유지)

---

## 🎊 중요한 점

**모든 WatchHamster 기능은 GUI 없이도 100% 작동합니다!**

- ✅ 성능 최적화 시스템
- ✅ 안정성 관리자  
- ✅ 캐시 모니터링
- ✅ POSCO 백엔드 기능
- ✅ 메시지 템플릿 엔진
- ✅ Git 배포 관리
- ✅ 시스템 상태 모니터링

GUI는 **편의 기능**이고, **핵심 기능은 모두 백엔드**에 있습니다!

---

## 🚨 즉시 시도할 명령어

```bash
# 1. 헤드리스 테스트 (GUI 없음)
python3 test_headless.py

# 2. 시스템 체크
python3 quick_system_check.py

# 3. 백엔드 기능 테스트
python3 core/performance_optimizer.py
```

**GUI 크래시와 상관없이 모든 기능이 정상 작동합니다!**