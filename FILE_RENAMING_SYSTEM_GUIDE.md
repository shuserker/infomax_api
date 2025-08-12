# POSCO 파일 및 폴더명 자동 변경 시스템 가이드

## 개요

POSCO 프로젝트의 파일명, 폴더명을 일관된 네이밍 컨벤션으로 자동 변경하는 시스템입니다.

### 버전 체계
- **WatchHamster**: `v3.0` (메이저.마이너 형식)
- **POSCO News**: `250808` (YYMMDD 날짜 형식)

## 주요 기능

### 1. 파일 및 폴더 분석
- 기존 파일들의 네이밍 패턴 자동 분석
- 컴포넌트별 매핑 테이블 생성
- 변경 대상 파일 식별

### 2. 자동 이름 변경
- WatchHamster 관련 파일들을 v3.0 형식으로 변경
- POSCO News 관련 파일들을 250808 형식으로 변경
- 안전한 백업 및 롤백 기능

### 3. 로깅 및 추적
- 모든 변경 작업 로그 기록
- 작업 성공/실패 추적
- 상세한 보고서 생성

## 설치 및 사용법

### 필요 파일
```
naming_convention_manager.py    # 네이밍 컨벤션 관리
file_renaming_system.py        # 파일 리네이밍 시스템
posco_file_renamer.py          # CLI 도구
test_file_renaming_system.py   # 테스트 스크립트
```

### CLI 사용법

#### 1. 파일 분석
```bash
python3 posco_file_renamer.py --analyze
```
- 현재 디렉토리의 파일들을 분석
- 변경 대상 파일 목록 출력
- 매핑 테이블 생성

#### 2. 시뮬레이션 (드라이 런)
```bash
python3 posco_file_renamer.py --dry-run
```
- 실제 변경하지 않고 시뮬레이션만 수행
- 변경 예정 파일 목록 출력
- 시뮬레이션 보고서 생성

#### 3. WatchHamster 파일만 변경
```bash
python3 posco_file_renamer.py --watchhamster
```
- WatchHamster 관련 파일들만 v3.0 형식으로 변경
- 사용자 확인 후 실행

#### 4. POSCO News 파일만 변경
```bash
python3 posco_file_renamer.py --posco-news
```
- POSCO News 관련 파일들만 250808 형식으로 변경
- 사용자 확인 후 실행

#### 5. 모든 파일 변경
```bash
python3 posco_file_renamer.py --all
```
- 모든 대상 파일을 표준 네이밍 컨벤션으로 변경
- 사용자 확인 후 실행

#### 6. 변경 사항 롤백
```bash
python3 posco_file_renamer.py --rollback
```
- 이전 변경 사항을 원래대로 복원
- 백업 파일을 이용한 안전한 롤백

#### 7. 보고서 생성
```bash
python3 posco_file_renamer.py --report
```
- 현재 상태 및 작업 이력 보고서 생성
- 상세한 통계 정보 제공

### 고급 옵션

#### 작업 공간 지정
```bash
python3 posco_file_renamer.py --dry-run --workspace /path/to/project
```

## 변경 규칙

### WatchHamster 관련 파일 (v3.0)

#### 파일명 변경 예시
```
🐹WatchHamster_총괄_관리_센터_v3.bat → 🐹WatchHamster_v3.0_Control_Center.bat
🐹WatchHamster_통합_관리_센터.bat → 🐹WatchHamster_v3.0_Integrated_Center.bat
🎛️POSCO_제어센터_실행_v2.bat → 🎛️WatchHamster_v3.0_Control_Panel.bat
demo_v2_integration.py → demo_watchhamster_v3.0_integration.py
test_v2_integration.py → test_watchhamster_v3.0_integration.py
monitor_WatchHamster.py → monitor_WatchHamster_v3.0.py
```

#### 폴더명 변경 예시
```
POSCO News_v2/ → WatchHamster_v3.0/
posco-watchhamster-v2-integration/ → watchhamster-v3.0-integration/
```

#### 문서 파일 변경 예시
```
📋POSCO_WatchHamster_v2_사용자_가이드.md → 📋POSCO_WatchHamster_v3.0_사용자_가이드.md
🔍POSCO_WatchHamster_v2_전체_재검수_보고서.md → 🔍POSCO_WatchHamster_v3.0_전체_재검수_보고서.md
```

### POSCO News 관련 파일 (250808)

#### 파일명 변경 예시
```
POSCO News.py → POSCO_News_250808.py
posco_main_notifier.py → posco_news_250808_notifier.py
posco_continuous_monitor.py → posco_news_250808_monitor.py
posco_news_data.json → posco_news_250808_data.json
posco_news_cache.json → posco_news_250808_cache.json
```

#### 폴더명 변경 예시
```
POSCO News/ → POSCO_News_250808/
```

## 안전 기능

### 1. 백업 시스템
- 모든 변경 전 자동 백업 생성
- `.naming_backup/` 디렉토리에 백업 저장
- 작업 ID별 백업 파일 관리

### 2. 롤백 기능
- 언제든지 이전 상태로 복원 가능
- 작업 단위별 선택적 롤백
- 백업 파일을 이용한 안전한 복원

### 3. 로깅 시스템
- 모든 작업 상세 로그 기록
- 성공/실패 상태 추적
- 오류 메시지 및 원인 기록

### 4. 드라이 런 모드
- 실제 변경 전 시뮬레이션 가능
- 변경 예정 파일 미리 확인
- 안전한 테스트 환경 제공

## 파일 구조

### 생성되는 파일들
```
.naming_backup/                    # 백업 디렉토리
├── operations_log.json           # 작업 로그
├── mapping_table.json            # 매핑 테이블
└── [operation_id]_[filename]     # 백업 파일들

file_renaming.log                  # 시스템 로그
posco_renaming_report.txt          # 작업 보고서
posco_renaming_simulation_report.txt # 시뮬레이션 보고서
```

## 프로그래밍 API

### 기본 사용법
```python
# BROKEN_REF: from file_renaming_system.py.py import FileRenamingSystem

# 시스템 초기화
renaming_system = FileRenamingSystem(".")

# 파일 분석
mapping_by_component = renaming_system.analyze_existing_files()

# WatchHamster 파일 변경 (드라이 런)
operations = renaming_system.rename_watchhamster_files(dry_run=True)

# 실제 변경
operations = renaming_system.rename_watchhamster_files(dry_run=False)

# 롤백
success = renaming_system.rollback_operations()

# 보고서 생성
report = renaming_system.generate_operations_report()
```

### 네이밍 컨벤션 매니저 사용
```python
# BROKEN_REF: from naming_convention_manager.py.py import NamingConventionManager

manager = NamingConventionManager()

# 파일명 표준화
# BROKEN_REF: result = manager.standardize_filename("demo_v2_integration.py")
print(f"{result.original} → {result.converted}")

# 폴더명 표준화
result = manager.standardize_foldername("POSCO News_v2")
print(f"{result.original} → {result.converted}")
```

## 테스트

### 단위 테스트 실행
```bash
python3 test_file_renaming_system.py
```

### 통합 테스트
- 실제 워크스페이스에서 드라이 런 테스트
- 매핑 테이블 생성 및 검증
- 롤백 기능 테스트

## 문제 해결

### 일반적인 문제들

#### 1. 파일이 사용 중인 경우
```
오류: [Errno 16] Device or resource busy
해결: 파일을 사용하는 프로그램을 종료 후 재시도
```

#### 2. 권한 문제
```
오류: [Errno 13] Permission denied
해결: 관리자 권한으로 실행 또는 파일 권한 확인
```

#### 3. 백업 공간 부족
```
오류: No space left on device
해결: 디스크 공간 확보 후 재시도
```

### 로그 확인
```bash
# 시스템 로그 확인
tail -f file_renaming.log

# 작업 로그 확인
cat .naming_backup/operations_log.json
```

## 주의사항

### 🚨 중요한 제약사항
- **코드 로직 보존**: 파일명만 변경하고 내용은 절대 수정하지 않음
- **기능 동일성**: 변경 후에도 모든 기능이 동일하게 작동해야 함
- **데이터 호환성**: 기존 데이터 파일과의 호환성 완전 보장

### 권장사항
1. **백업 생성**: 중요한 작업 전 전체 프로젝트 백업
2. **드라이 런 실행**: 실제 변경 전 반드시 시뮬레이션 수행
3. **단계별 실행**: WatchHamster와 POSCO News를 분리하여 실행
4. **테스트 확인**: 변경 후 시스템 정상 동작 확인

## 버전 히스토리

### v1.0.0 (2025-08-08)
- 초기 버전 릴리스
- 기본 파일/폴더 리네이밍 기능
- CLI 도구 제공
- 백업 및 롤백 기능
- 상세한 로깅 시스템

## 라이선스

이 시스템은 POSCO 프로젝트 전용으로 개발되었습니다.

## 지원

문제가 발생하거나 개선 사항이 있으면 개발팀에 문의하세요.

---

**⚠️ 주의**: 이 도구는 파일명과 폴더명만 변경합니다. 파일 내용이나 코드 로직은 절대 수정하지 않으므로 안전하게 사용할 수 있습니다.