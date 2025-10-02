# 🪟 WatchHamster 윈도우 스탠드얼론 실행 가이드

**완전 독립 실행 - 설치 없이 바로 사용!**

---

## 🚀 즉시 실행 (가장 간단)

### 1. 기본 실행
```cmd
cd Monitoring\WatchHamster_Project_GUI
python main_gui.py
```

### 2. 백엔드만 실행 (GUI 문제 시)
```cmd
python run_without_gui.py
```

### 3. 헤드리스 테스트
```cmd
python test_headless.py
```

---

## 🎯 윈도우 전용 실행 스크립트

### PowerShell 실행
```powershell
# PowerShell에서 실행
cd Monitoring\WatchHamster_Project_GUI
python.exe main_gui.py
```

### CMD 실행
```cmd
REM CMD에서 실행
cd Monitoring\WatchHamster_Project_GUI
python.exe main_gui.py
```

---

## 🔧 윈도우 환경 확인

### Python 설치 확인
```cmd
python --version
python -c "import tkinter; print('tkinter OK')"
python -c "import psutil; print('psutil OK')"
```

### 필요한 패키지 설치 (필요시)
```cmd
pip install psutil
```

---

## 📊 윈도우 전용 기능들

### 1. 윈도우 서비스로 실행
```cmd
REM 백그라운드 서비스로 실행
start /B python run_without_gui.py
```

### 2. 작업 스케줄러 등록
```cmd
REM 시스템 시작 시 자동 실행
schtasks /create /tn "WatchHamster" /tr "python C:\path\to\main_gui.py" /sc onstart
```

### 3. 윈도우 알림 활성화
```cmd
REM 시스템 트레이 알림 사용
python main_gui.py --enable-notifications
```

---

## 🖥️ GUI 실행 방법들

### 방법 1: 더블클릭 실행
1. `main_gui.py` 파일을 더블클릭
2. 또는 `run_without_gui.py` 더블클릭

### 방법 2: 배치 파일 생성
```batch
@echo off
cd /d "%~dp0"
python main_gui.py
pause
```

### 방법 3: 바로가기 생성
- 대상: `python.exe main_gui.py`
- 시작 위치: `C:\path\to\WatchHamster_Project_GUI`

---

## 💻 윈도우 터미널 모니터링

### 실시간 상태 모니터링
```cmd
python -c "
from core.performance_optimizer import PerformanceOptimizer
from core.stability_manager import StabilityManager
import time

optimizer = PerformanceOptimizer()
manager = StabilityManager('.')

print('🐹 WatchHamster 윈도우 모니터링')
print('Ctrl+C로 종료')

while True:
    try:
        perf = optimizer.get_performance_metrics()
        health = manager.check_system_health()
        
        print(f'CPU: {perf.get(\"cpu_percent\", 0)}%% | Memory: {health.get(\"memory_usage_mb\", 0)}MB | Time: {time.strftime(\"%%H:%%M:%%S\")}')
        time.sleep(5)
    except KeyboardInterrupt:
        print('\\n모니터링 종료')
        break
"
```

---

## 🔥 윈도우 최적화 설정

### 1. 윈도우 방화벽 예외 추가
```cmd
netsh advfirewall firewall add rule name="WatchHamster" dir=in action=allow program="python.exe"
```

### 2. 성능 우선순위 설정
```cmd
REM 높은 우선순위로 실행
start /HIGH python main_gui.py
```

### 3. 메모리 최적화
```cmd
REM 메모리 사용량 제한
python -c "
import resource
resource.setrlimit(resource.RLIMIT_AS, (1024*1024*1024, 1024*1024*1024))  # 1GB 제한
exec(open('main_gui.py').read())
"
```

---

## 🛠️ 윈도우 문제 해결

### tkinter 문제 해결
```cmd
REM Python 재설치 (Microsoft Store 버전 권장)
winget install Python.Python.3.11

REM 또는 python.org에서 다운로드
```

### 권한 문제 해결
```cmd
REM 관리자 권한으로 실행
powershell -Command "Start-Process python -ArgumentList 'main_gui.py' -Verb RunAs"
```

### 경로 문제 해결
```cmd
REM 절대 경로로 실행
python "C:\full\path\to\WatchHamster_Project_GUI\main_gui.py"
```

---

## 📁 윈도우 폴더 구조

```
WatchHamster_Project_GUI\
├── main_gui.py                    ← 더블클릭으로 실행
├── run_without_gui.py             ← GUI 문제 시 실행
├── test_headless.py               ← 기능 테스트
├── quick_system_check.py          ← 시스템 체크
├── core\                          ← 핵심 기능들
├── gui_components\                ← GUI 컴포넌트들
├── config\                        ← 설정 파일들
└── Posco_News_Mini_Final_GUI\     ← POSCO 전용 기능들
```

---

## 🎊 윈도우 전용 기능들

### 1. 윈도우 시스템 트레이
- 우측 하단 시스템 트레이에 아이콘 표시
- 우클릭으로 메뉴 접근
- 최소화 시 트레이로 숨김

### 2. 윈도우 알림
- 윈도우 10/11 네이티브 알림 사용
- 시스템 상태 변경 시 자동 알림
- 사용자 정의 알림 설정 가능

### 3. 윈도우 서비스 통합
- 윈도우 서비스로 등록 가능
- 시스템 시작 시 자동 실행
- 백그라운드에서 조용히 실행

---

## 🚀 즉시 시작 명령어

```cmd
REM 1. 기본 GUI 실행
python main_gui.py

REM 2. 백엔드만 실행
python run_without_gui.py

REM 3. 시스템 체크
python quick_system_check.py

REM 4. 전체 기능 테스트
python test_headless.py

REM 5. 성능 최적화만 실행
python core\performance_optimizer.py
```

---

## 💡 윈도우 사용 팁

1. **바탕화면 바로가기**: `main_gui.py`를 바탕화면으로 드래그
2. **시작 메뉴 등록**: 시작 메뉴에 고정
3. **작업 표시줄 고정**: 실행 후 작업 표시줄에 고정
4. **자동 시작**: 시작 프로그램에 추가

---

## 🎯 완전 스탠드얼론!

**설치 없이 바로 실행 가능:**
- ✅ Python만 있으면 OK
- ✅ 추가 설치 불필요
- ✅ 모든 기능 완전 독립
- ✅ 윈도우 네이티브 지원
- ✅ GUI + 백엔드 모두 지원

**지금 바로 실행해보세요!**
```cmd
python main_gui.py
```