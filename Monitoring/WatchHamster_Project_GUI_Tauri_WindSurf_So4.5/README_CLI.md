# WatchHamster v3.0 - CLI 모드 가이드

> **프로젝트**: WatchHamster_Project_GUI_Tauri_WindSurf_So4.5  
> **버전**: 3.0 (CLI Enhanced)  
> **날짜**: 2025-10-04  
> **플랫폼**: macOS (Python 3.11+)

## 📋 개요

WatchHamster v3.0은 POSCO 뉴스 모니터링 시스템으로, **GUI**와 **CLI** 두 가지 모드를 모두 지원합니다.

### 주요 기능

- ✅ **컬러풀한 터미널 UI** (Rich 라이브러리 기반)
- ✅ **8가지 모니터링 옵션** (개별/통합/스마트/24시간)
- ✅ **자동 복구 시스템** (프로세스 재시작, 헬스 체크)
- ✅ **실시간 상태 표시** (이모지, 테이블, 프로그레스 바)
- ✅ **24시간 백그라운드 서비스**

---

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd python-backend
pip3 install -r requirements.txt
```

**필수 패키지:**
- `pydantic>=2.5,<3`
- `rich==13.7.0`
- `colorama==0.4.6`
- `pytz==2025.2`

### 2. CLI 데모 실행

```bash
python3 test_cli_demo.py
```

### 3. 대화형 모니터링 시작

```bash
python3 cli/run_monitor.py
```

---

## 📖 사용 방법

### 대화형 모드 (run_monitor.py)

메뉴 기반 CLI 인터페이스로 모니터링을 실행합니다.

```bash
python3 cli/run_monitor.py
```

**메뉴 옵션:**

1. **🌐 뉴욕마켓워치 모니터링** - 뉴욕 시장 뉴스 모니터링
2. **📈 증시마감 모니터링** - 코스피 종가 뉴스 모니터링
3. **💱 서환마감 모니터링** - 환율 뉴스 모니터링
4. **🔄 통합 모니터링** - 모든 뉴스 1회 실행
5. **🤖 스마트 모니터링** - 시간대별 자동 실행
6. **🚀 24시간 서비스** - 백그라운드 지속 실행
7. **⚙️ 설정 관리** - 시스템 설정 확인
8. **🚪 종료** - 프로그램 종료

### 24시간 서비스 모드 (monitor_watchhamster.py)

백그라운드에서 지속적으로 실행되는 서비스입니다.

```bash
# 서비스 시작
python3 cli/monitor_watchhamster.py start

# 상태 확인
python3 cli/monitor_watchhamster.py status

# 서비스 중지
python3 cli/monitor_watchhamster.py stop

# 재시작
python3 cli/monitor_watchhamster.py restart
```

---

## 🎨 UI 스크린샷

### 메인 메뉴
```
╔═══════════════════════════════════════════════════════════╗
║           🐹 POSCO WatchHamster v3.0                      ║
╚═══════════════════════════════════════════════════════════╝

메뉴 옵션:
→ 1. 🌐 뉴욕마켓워치 모니터링
  2. 📈 증시마감 모니터링
  3. 💱 서환마감 모니터링
  ...
```

### 시스템 상태
```
╭─────────────┬────────────┬──────╮
│ 항목        │ 값         │ 상태 │
├─────────────┼────────────┼──────┤
│ 시스템 상태 │ running    │  🔄  │
│ 활성 모니터 │ 3          │  ℹ️   │
│ 정상 모니터 │ 3          │  ✅  │
╰─────────────┴────────────┴──────╯
```

### 시스템 리소스
```
💻 CPU: 22.8% [████░░░░░░░░░░░░░░░░]
🧠 메모리: 78.9% [███████████████░░░░░]
💾 디스크: 29.4% [█████░░░░░░░░░░░░░░░]
```

---

## 🏗️ 아키텍처

### 프로젝트 구조

```
python-backend/
├── core/
│   ├── state_manager.py          # 상태 저장/로드
│   ├── process_manager.py        # 프로세스 관리
│   ├── watchhamster_core.py      # 핵심 로직
│   └── monitors/                 # 개별 모니터
├── ui/
│   ├── console_ui.py             # 콘솔 UI
│   ├── status_formatter.py       # 상태 포맷팅
│   └── progress_indicator.py     # 진행 표시
├── cli/
│   ├── run_monitor.py            # 대화형 CLI
│   └── monitor_watchhamster.py   # 24시간 서비스
└── models/                       # Pydantic 모델
```

### 핵심 컴포넌트

#### 1. StateManager
- 상태 저장/로드
- None 값 안전 처리
- datetime 직렬화

#### 2. ProcessManager
- 프로세스 생명주기 관리
- 자동 재시도 (최대 3회)
- 헬스 체크 (5초 간격)
- 자동 복구

#### 3. WatchHamsterCore
- 시스템 초기화/종료
- 4가지 모니터링 모드
- 오류 처리 및 복구

#### 4. ColorfulConsoleUI
- Rich 기반 터미널 UI
- 컬러풀한 출력
- 이모지 지원
- 테이블, 패널, 프로그레스 바

---

## 🧪 테스트

### Core 컴포넌트 테스트

```bash
python3 test_core_components.py
```

**테스트 항목:**
- StateManager (상태 저장/로드)
- ProcessManager (프로세스 관리)
- WatchHamsterCore (시스템 통합)

### UI 컴포넌트 테스트

```bash
python3 test_ui_components.py
```

**테스트 항목:**
- ColorfulConsoleUI (콘솔 출력)
- StatusFormatter (상태 포맷팅)
- ProgressIndicator (진행 표시)

### CLI 데모

```bash
python3 test_cli_demo.py
```

---

## 📊 모니터링 모드

### 1. INDIVIDUAL (개별)
특정 뉴스 소스만 모니터링합니다.

```python
await core.start_monitoring(
    MonitoringMode.INDIVIDUAL,
    monitors=["newyork-market-watch"]
)
```

### 2. INTEGRATED (통합)
모든 뉴스 소스를 1회 실행합니다.

```python
await core.start_monitoring(MonitoringMode.INTEGRATED)
```

### 3. SMART (스마트)
시간대별로 자동 실행합니다.
- 운영시간: 09:00-18:00
- 집중시간: 14:00-16:00

```python
await core.start_monitoring(MonitoringMode.SMART)
```

### 4. SERVICE_24H (24시간)
백그라운드에서 지속 실행합니다.

```python
await core.start_monitoring(MonitoringMode.SERVICE_24H)
```

---

## 🔧 설정

### 상태 파일 위치
```
python-backend/data/watchhamster_state.json
```

### 로그 파일 위치
```
python-backend/logs/watchhamster_24h.log
```

### PID 파일 위치
```
python-backend/data/watchhamster.pid
```

---

## 🐛 트러블슈팅

### 문제: 모듈을 찾을 수 없음

```bash
ModuleNotFoundError: No module named 'rich'
```

**해결:**
```bash
pip3 install rich colorama pytz
```

### 문제: 서비스가 시작되지 않음

```bash
python3 cli/monitor_watchhamster.py status
```

PID 파일을 확인하고 필요시 삭제:
```bash
rm python-backend/data/watchhamster.pid
```

### 문제: 권한 오류

```bash
chmod +x cli/run_monitor.py
chmod +x cli/monitor_watchhamster.py
```

---

## 📝 개발 가이드

### 새 모니터 추가

1. `core/monitors/` 에 모니터 파일 생성
2. `WatchHamsterCore`에 모니터 등록
3. `run_monitor.py` 메뉴에 추가

### UI 커스터마이징

`ui/console_ui.py`에서 색상, 이모지, 스타일 수정:

```python
EMOJI = {
    "success": "✅",
    "error": "❌",
    # ...
}

STYLES = {
    UIStyle.SUCCESS: Style(color="green", bold=True),
    # ...
}
```

---

## 🎯 다음 단계

### Phase 5: 개별 모니터 통합 (예정)

- [ ] 뉴욕마켓워치 모니터 구현
- [ ] 증시마감 모니터 구현
- [ ] 서환마감 모니터 구현
- [ ] MasterMonitor 통합
- [ ] Dooray 웹훅 연동

### Phase 6: 테스트 및 최적화 (예정)

- [ ] 통합 테스트
- [ ] 24시간 안정성 테스트
- [ ] 성능 최적화
- [ ] 메모리 누수 방지

---

## 📚 참고 문서

- `tasks_wind.md` - 구현 계획
- `design.md` - 아키텍처 설계
- `requirements.md` - 요구사항
- `audit-report.md` - 검수 보고서

---

## 👥 기여

**개발**: AI Assistant  
**프로젝트**: POSCO WatchHamster v3.0  
**날짜**: 2025-10-04

---

## 📄 라이선스

내부 프로젝트 - POSCO 전용
