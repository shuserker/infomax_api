# WatchHamster UI 복원 및 안정화 Implementation Plan (WindSurf So4.5)

> **프로젝트 경로**: `/Monitoring/WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/`
> **기반 소스**: `WatchHamster_Project_GUI_Tauri` (Tauri + FastAPI 구조)
> **목표**: GUI 애플리케이션에 콘솔 UI 기능 추가 및 안정성 강화

## 프로젝트 개요

### 현재 상태
- ✅ Tauri GUI 프레임워크 구축됨
- ✅ FastAPI 백엔드 기본 구조 존재
- ⚠️ UI만 뜨고 실제 모니터링 기능 미작동
- ❌ 콘솔 UI 기능 없음
- ❌ 프로세스 관리 및 안정성 로직 미흡

### 구현 방향
1. **Hybrid 접근**: GUI + CLI 모드 모두 지원
2. **점진적 구현**: 백엔드 안정화 → CLI 추가 → GUI 연동
3. **기존 구조 활용**: FastAPI 라우터 및 모델 재사용

---

## Phase 1: 환경 설정 및 의존성 정리

### 1.1 Python 의존성 업데이트
- [ ] `requirements.txt` Pydantic 2.x 마이그레이션
  - `pydantic==1.10.13` → `pydantic>=2.5,<3`
  - 기존 모델 파일들 Pydantic 2.x 문법으로 수정
  - `regex=` → `pattern`, `@validator` → `@field_validator`
  - _Requirements: 기술적 기반 확보_

### 1.2 프로젝트 구조 정리
- [ ] 새 디렉토리 생성
  ```
  python-backend/
  ├── core/
  │   ├── state_manager.py (기존)
  │   ├── process_manager.py (신규)
  │   ├── watchhamster_core.py (신규)
  │   └── stability_manager.py (기존)
  ├── ui/
  │   ├── __init__.py (신규)
  │   ├── console_ui.py (신규)
  │   ├── status_formatter.py (신규)
  │   └── progress_indicator.py (신규)
  └── cli/
      ├── __init__.py (신규)
      ├── run_monitor.py (신규)
      └── monitor_watchhamster.py (신규)
  ```
  - _Requirements: 코드 조직화_

---

## Phase 2: Core Stability 구현 - 시스템 안정성 확보

### 2.1 StateManager 개선 ✅
- [x] 기존 `state_manager.py` 검증
  - None 값 안전 처리 확인
  - datetime 직렬화 로직 확인
  - 상태 저장/로드 테스트
  - _Requirements: 2.4_

### 2.2 ProcessManager 클래스 구현 🔥
- [ ] `core/process_manager.py` 신규 작성
  ```python
  class ProcessManager:
      def __init__(self):
          self.processes: Dict[str, ProcessInfo] = {}
          self.state_manager = StateManager()
      
      async def start_monitor(self, monitor_type: str) -> bool
      async def stop_monitor(self, monitor_type: str) -> bool
      async def restart_monitor(self, monitor_type: str) -> bool
      async def check_health(self, monitor_type: str) -> HealthStatus
      async def auto_recover(self, monitor_type: str) -> bool
  ```
  - 개별 모니터 프로세스 생명주기 관리
  - 시작 실패 시 3회 재시도 로직
  - 헬스 체크 (5초마다)
  - 자동 복구 시나리오
  - _Requirements: 2.1, 2.2, 2.3_

### 2.3 WatchHamsterCore 클래스 구현 🔥
- [ ] `core/watchhamster_core.py` 신규 작성
  ```python
  class WatchHamsterCore:
      def __init__(self):
          self.state_manager = StateManager()
          self.process_manager = ProcessManager()
          self.ui = None  # CLI 모드에서만 사용
      
      async def initialize(self) -> bool
      async def start_monitoring(self, mode: str) -> bool
      async def stop_monitoring(self) -> bool
      async def get_system_status(self) -> SystemStatus
      async def handle_error(self, error: Exception) -> bool
  ```
  - 전체 시스템 초기화 및 종료
  - 모니터링 모드 관리 (개별/통합/24시간)
  - 오류 처리 및 복구 조정
  - _Requirements: 2.1, 2.2, 2.3_

### 2.4 FastAPI 라우터 통합
- [ ] `api/system.py` 업데이트
  - WatchHamsterCore 인스턴스 통합
  - `/api/system/start`, `/api/system/stop` 엔드포인트 개선
  - `/api/system/health` 헬스 체크 추가
  - _Requirements: 2.1, 2.2_

---

## Phase 3: UI Enhancement 구현 - 콘솔 인터페이스

### 3.1 ColorfulConsoleUI 클래스 구현 🔥
- [ ] `ui/console_ui.py` 신규 작성
  ```python
  class ColorfulConsoleUI:
      def __init__(self, enable_colors: bool = True):
          self.colors_enabled = enable_colors
          self.emoji_enabled = True
      
      def print_header(self, title: str, style: str = "default")
      def print_status(self, status: dict, highlight: bool = False)
      def print_menu(self, options: List[str], current: int = 0)
      def print_separator(self, char: str = "=", length: int = 60)
      def print_error(self, message: str, details: str = None)
      def print_success(self, message: str, details: str = None)
  ```
  - ANSI 색상 코드 활용
  - 이모지 지원 (✅ ❌ ⚠️ 🔄 📊 등)
  - Windows/Mac/Linux 호환성
  - _Requirements: 1.1, 1.3, 4.1, 4.4_

### 3.2 StatusFormatter 클래스 구현 🔥
- [ ] `ui/status_formatter.py` 신규 작성
  ```python
  class StatusFormatter:
      def format_monitor_status(self, monitors: Dict) -> str
      def format_time_info(self, current: datetime, next: datetime) -> str
      def format_system_resources(self, resources: dict) -> str
      def format_error_message(self, error: Exception) -> str
      def format_table(self, headers: List[str], rows: List[List]) -> str
  ```
  - 테이블 형식 출력
  - 시간 정보 포맷팅 (한국 시간)
  - 리소스 사용률 시각화
  - _Requirements: 1.2, 1.4, 4.2, 4.4_

### 3.3 ProgressIndicator 구현
- [ ] `ui/progress_indicator.py` 신규 작성
  - 스피너 애니메이션 (⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏)
  - 프로그레스 바 (진행률 표시)
  - 비동기 작업 상태 표시
  - _Requirements: 4.2_

---

## Phase 4: CLI 스크립트 구현

### 4.1 run_monitor.py 구현 🔥
- [ ] `cli/run_monitor.py` 신규 작성
  ```python
  # 일회성 모니터링 실행 스크립트
  # 옵션 1-8 지원:
  # 1. 뉴욕마켓워치 모니터링
  # 2. 증시마감 모니터링
  # 3. 서환마감 모니터링
  # 4. 통합 모니터링 (1회)
  # 5. 스마트 모니터링 (시간대별)
  # 6. 24시간 서비스 시작
  # 7. 설정 관리
  # 8. 종료
  ```
  - 컬러풀한 메뉴 UI
  - 각 옵션별 실행 로직
  - WatchHamsterCore 연동
  - _Requirements: 1.2, 1.4, 3.3, 4.1, 4.2_

### 4.2 monitor_watchhamster.py 구현 🔥
- [ ] `cli/monitor_watchhamster.py` 신규 작성
  ```python
  # 24시간 백그라운드 서비스
  # - 자동 시작/재시작
  # - 로그 파일 관리
  # - 시스템 트레이 통합 (선택)
  ```
  - 데몬 모드 실행
  - 자동 복구 로직
  - 상태 모니터링 및 알림
  - _Requirements: 3.4, 2.1, 2.2_

### 4.3 CLI 진입점 설정
- [ ] `python-backend/main.py` 업데이트
  - CLI 모드 감지 (`--cli` 플래그)
  - GUI 모드와 CLI 모드 분기
  - 환경 변수 기반 설정

---

## Phase 5: Integration & Compatibility

### 5.1 개별 모니터 통합
- [ ] 뉴욕마켓워치 모니터 연동
  - `core/monitors/nymarket_monitor.py` 작성
  - ProcessManager에 등록
  - UI 출력 연동
  - _Requirements: 3.1_

- [ ] 증시마감 모니터 연동
  - `core/monitors/stock_close_monitor.py` 작성
  - _Requirements: 3.1_

- [ ] 서환마감 모니터 연동
  - `core/monitors/forex_close_monitor.py` 작성
  - _Requirements: 3.1_

### 5.2 MasterMonitor 개선
- [ ] `core/master_monitor.py` 구현
  ```python
  class EnhancedMasterMonitor:
      def __init__(self):
          self.ui = ColorfulConsoleUI()
          self.formatter = StatusFormatter()
          self.monitors = []
      
      async def run_integrated_monitoring(self)
      async def display_status(self)
      async def handle_errors(self)
  ```
  - 통합 모니터링 로직
  - 컬러풀 상태 출력
  - _Requirements: 3.2, 4.3_

### 5.3 Dooray 웹훅 통합
- [ ] 기존 `webhook_sender.py` 활용
  - CLI 모드에서도 알림 전송
  - 오류 발생 시 즉시 알림
  - 일일 리포트 전송
  - _Requirements: 3.2_

---

## Phase 6: Testing & Validation

### 6.1 Unit Tests
- [ ] `tests/test_process_manager.py`
  - 프로세스 시작/중지/재시작 테스트
  - 헬스 체크 테스트
  - 자동 복구 시나리오 테스트
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] `tests/test_console_ui.py`
  - 색상 출력 테스트
  - 포맷팅 테스트
  - 크로스 플랫폼 호환성 테스트
  - _Requirements: 1.1, 1.2, 1.3_

### 6.2 Integration Tests
- [ ] `tests/test_cli_integration.py`
  - run_monitor.py 옵션 1-8 전체 테스트
  - 24시간 서비스 안정성 테스트
  - GUI ↔ CLI 모드 전환 테스트
  - _Requirements: 3.3, 3.4_

### 6.3 Performance Tests
- [ ] 장시간 실행 테스트 (24시간)
  - 메모리 누수 확인
  - CPU 사용률 모니터링
  - 로그 파일 크기 관리
  - _Requirements: 4.1, 4.2_

---

## Phase 7: Documentation & Deployment

### 7.1 사용자 문서
- [ ] `docs/CLI_USER_GUIDE.md` 작성
  - CLI 모드 사용법
  - 옵션별 설명
  - 트러블슈팅 가이드
  - _Requirements: 4.1, 4.4_

### 7.2 개발자 문서
- [ ] `docs/ARCHITECTURE_WIND.md` 작성
  - 새로운 아키텍처 설명
  - 클래스 다이어그램
  - API 레퍼런스
  - _Requirements: 4.2, 4.3_

### 7.3 배포 스크립트
- [ ] `scripts/deploy_cli.sh` 작성
  - CLI 모드 배포 자동화
  - 의존성 설치
  - 서비스 등록 (systemd/launchd)

---

## 우선순위 및 일정

### Week 1: Core Foundation
- Day 1-2: Phase 1 (환경 설정)
- Day 3-5: Phase 2 (Core Stability)

### Week 2: UI & CLI
- Day 6-8: Phase 3 (UI Enhancement)
- Day 9-10: Phase 4 (CLI Scripts)

### Week 3: Integration & Testing
- Day 11-13: Phase 5 (Integration)
- Day 14-15: Phase 6 (Testing)

### Week 4: Finalization
- Day 16-18: Phase 7 (Documentation)
- Day 19-20: 최종 검증 및 배포

---

## 검증 기준

### 기능적 요구사항
- ✅ CLI 모드에서 컬러풀한 UI 출력
- ✅ 8가지 모니터링 옵션 모두 작동
- ✅ 24시간 서비스 안정적 실행
- ✅ 프로세스 자동 복구 기능
- ✅ NoneType 오류 제거

### 기술적 요구사항
- ✅ Pydantic 2.x 호환
- ✅ FastAPI 정상 구동
- ✅ GUI 모드 유지 (기존 기능)
- ✅ CLI 모드 추가 (신규 기능)
- ✅ 크로스 플랫폼 지원

### 품질 요구사항
- ✅ 테스트 커버리지 80% 이상
- ✅ 24시간 무중단 실행
- ✅ 메모리 사용량 500MB 이하
- ✅ 문서화 완료

---

## 참고 문서
- `requirements.md`: 사용자 스토리 및 수용 기준
- `design.md`: 아키텍처 및 컴포넌트 설계
- `audit-report.md`: 현재 상태 진단
- `implementation-plan.md`: 전체 실행 계획

---

## 변경 이력
- 2025-10-04: 초안 작성 (WindSurf So4.5 프로젝트용)
