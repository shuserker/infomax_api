# WatchHamster UI 복원 프로젝트 실행 계획

## 1. 목표 및 범위
- **목표**: `tasks.md`, `design.md`, `requirements.md`, `audit-report.md`에서 정의된 WatchHamster UI 복원 및 안정화 요구사항을 완전히 충족시키는 코드베이스 구축.
- **범위**: Pydantic 2.x 호환성 확보부터 콘솔 UI 복원, WatchHamster 2.0 기능 통합, 테스트·문서화 및 실행 검증까지 전 단계 포함.

## 2. 현재 진단 요약
- **코드 호환성**: `regex=`/`@validator` 사용 등 Pydantic 1.x 패턴이 전역에서 발견되어 FastAPI 라우터 등록 시 오류 발생.
- **핵심 로직 부재**: `StateManager`, `ProcessManager`, `WatchHamsterCore`, `EnhancedMasterMonitor` 등 설계 문서에 명시된 핵심 클래스 미구현.
- **UI 미구현**: `ColorfulConsoleUI`, `StatusFormatter`, `run_monitor.py`, `monitor_WatchHamster.py` 복원이 필요.
- **테스트·문서화**: 요구사항 기반의 테스트 케이스 및 최신 문서 부재.

## 3. 단계별 실행 계획
### 단계 1. Pydantic 2.x 마이그레이션 및 의존성 정리
- `models/` 하위 모든 파일에서 `regex=` → `pattern`, `@validator` → `@model_validator`/`field_validator` 적용.
- `pydantic>=2.5,<3`, `pydantic-settings==2.0.3` 조합으로 `requirements.txt` 확정.
- FastAPI 라우터 등록 시 경고/오류 제거, `uvicorn` 구동 확인.

### 단계 2. 코어 안정화 계층 구현 및 백엔드 통합
- `core/state_manager.py`를 기반으로 `ProcessManager`, `WatchHamsterCore` 구현.
- 기존 FastAPI 엔드포인트(`api/system.py`, `api/services.py` 등)에 새 매니저 통합.
- NoneType 오류, 프로세스 시작 실패 해결 로직 포함.

### 단계 3. 콘솔 UI 복원 및 CLI 진입점 개선
- `ColorfulConsoleUI`, `StatusFormatter`, 기타 UI 유틸 구현.
- `run_monitor.py`, `monitor_WatchHamster.py` 복원 및 새 코어와 연결.
- 컬러풀 UI, 이모지, 상태 구분 등 `requirements.md` 1.x, 4.x 충족.

### 단계 4. WatchHamster 2.0 통합 및 기능 보강
- `EnhancedMasterMonitor`, 개별 모니터 UI/안정화 개선.
- 옵션 1~8, 24시간 서비스(`monitor_WatchHamster.py`) 정상 작동 확인.
- Dooray 웹훅, 설정 호환성 유지.

### 단계 5. 테스트, 성능, 문서화 및 배포 준비
- Unit/Integration/Performance 테스트 작성 (`tasks.md` 4.x, 5.x 충족).
- 장시간 실행 시나리오 및 자동 복구 테스트.
- 사용자/개발자 문서 업데이트 (`tasks.md` 6.x), 배포 가이드 개선.
- `audit-report.md` 업데이트 및 최종 검수 보고.

## 4. 작업 트래킹
- `tasks.md`와 본 계획 문서를 기준으로 단계 진행 상황을 수시 업데이트.
- 각 단계 완료 시:
  1. 관련 코드/문서 커밋
  2. 체크리스트 업데이트
  3. 검증 결과 캡처 및 기록

## 5. 검증 및 인수 기준
- **기능적**: 요구사항 문서의 Acceptance Criteria 전부 충족.
- **기술적**: FastAPI + Tauri 환경에서 백/프런트 모두 무오류 실행.
- **품질**: 테스트 통과, 장시간 안정성 확인, 콘솔 UI 시연 완료.
- **문서화**: 사용자/개발자/배포 문서 최신화 및 리뷰 완료.

## 6. 향후 일정 가이드
1. **Day 1-2**: Pydantic 마이그레이션 및 의존성 정리.
2. **Day 3-4**: 안정화 계층 구현, 기본 통합 및 오류 처리.
3. **Day 5-6**: 콘솔 UI 복원, CLI 스크립트 적용.
4. **Day 7-8**: WatchHamster 통합, 옵션/24h 서비스 검증.
5. **Day 9-10**: 테스트·성능·문서화, 최종 실행 확인 및 리포트.

(상기 일정은 개발 상황에 따라 조정 가능. 각 단계 종료 시 재평가 예정.)
