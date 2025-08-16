# 🔄 POSCO 네이밍 컨벤션 롤백 가이드

## 📋 개요

이 문서는 POSCO 네이밍 컨벤션 표준화 작업을 이전 상태로 안전하게 되돌리는 방법을 설명합니다.

## 🚨 롤백이 필요한 상황

### 즉시 롤백이 필요한 경우
- 시스템 기능이 정상적으로 작동하지 않는 경우
- 중요한 데이터 파일에 접근할 수 없는 경우
- 사용자 인터페이스가 제대로 표시되지 않는 경우
- 성능이 현저히 저하된 경우

### 부분 롤백을 고려할 경우
- 특정 컴포넌트만 문제가 있는 경우
- 일부 파일명만 문제가 있는 경우
- 특정 기능만 영향을 받는 경우

## 🛠️ 롤백 방법

### 1. 자동 롤백 (권장)

#### 전체 롤백
```bash
# 가장 최근 작업 롤백
python3 posco_file_renamer.py --rollback

# 특정 날짜의 작업 롤백
python3 posco_file_renamer.py --rollback --date 2025-08-08

# 확인 없이 강제 롤백
python3 posco_file_renamer.py --rollback --force
```

#### 컴포넌트별 롤백
```bash
# WatchHamster 관련 파일만 롤백
python3 posco_file_renamer.py --rollback --component watchhamster

# POSCO News 관련 파일만 롤백
python3 posco_file_renamer.py --rollback --component posco_news
```

### 2. 수동 롤백

#### 백업 파일 확인
```bash
# 백업 디렉토리 확인
ls -la .naming_backup/

# 매핑 테이블 확인
cat .naming_backup/mapping_table.json | jq '.'

# 작업 로그 확인
cat .naming_backup/operations_log.json | jq '.'
```

#### 파일별 수동 복원
```bash
# 중요 설정 파일 복원
cp .naming_backup/config_data_backup/posco_news_250808_data.json ./posco_news_data.json
cp .naming_backup/config_data_backup/posco_news_250808_cache.json ./posco_news_cache.json

# 스크립트 파일 복원
cp ".naming_backup/scripts/🐹워치햄스터_총괄_관리_센터_v3.bat" .
cp ".naming_backup/scripts/🎛️POSCO_제어센터_실행_v2.bat" .

# Python 파일 복원
cp .naming_backup/scripts/demo_v2_integration.py .
cp .naming_backup/scripts/test_v2_integration.py .
```

### 3. 프로그래밍 방식 롤백

```python
# BROKEN_REF: from file_renaming_system.py.py import FileRenamingSystem

# 시스템 초기화
system = FileRenamingSystem(".")

# 전체 롤백
success = system.rollback_operations()
if success:
    print("롤백이 성공적으로 완료되었습니다.")
else:
    print("롤백 중 오류가 발생했습니다.")

# 특정 작업 롤백
operation_id = "20250808_143022"
success = system.rollback_operations(operation_id=operation_id)

# 컴포넌트별 롤백
success = system.rollback_component_operations("watchhamster")
```

## 📊 롤백 상태 확인

### 롤백 전 상태 확인
```bash
# 현재 파일 상태 확인
python3 posco_file_renamer.py --status

# 백업 파일 존재 확인
python3 posco_file_renamer.py --check-backup

# 롤백 가능 여부 확인
python3 posco_file_renamer.py --can-rollback
```

### 롤백 후 검증
```bash
# 파일 복원 상태 확인
python3 posco_file_renamer.py --verify-rollback

# 시스템 기능 테스트
python3 test_end_to_end_integration.py

# 네이밍 일관성 확인 (롤백 후에는 이전 네이밍 사용)
python3 naming_standardization_verification_system.py --legacy-mode
```

## 🔧 롤백 시나리오별 대응

### 시나리오 1: WatchHamster 제어센터가 실행되지 않는 경우

#### 문제 진단
```bash
# 파일 존재 확인
ls -la 🐹WatchHamster_v3.0_Control_Center.bat
ls -la 🎛️WatchHamster_v3.0_Control_Panel.bat

# 원본 파일 확인
ls -la .naming_backup/scripts/🐹워치햄스터_총괄_관리_센터_v3.bat
```

#### 해결 방법
```bash
# 1. 백업에서 원본 파일 복원
cp ".naming_backup/scripts/🐹워치햄스터_총괄_관리_센터_v3.bat" .
cp ".naming_backup/scripts/🎛️POSCO_제어센터_실행_v2.bat" .

# 2. 실행 권한 확인 및 설정
chmod +x *.bat

# 3. 테스트 실행
./.naming_backup/scripts/.naming_backup/scripts/🐹워치햄스터_총괄_관리_센터_v3.bat
```

### 시나리오 2: POSCO News 데이터에 접근할 수 없는 경우

#### 문제 진단
```bash
# 데이터 파일 확인
ls -la posco_news_250808_*.json
ls -la POSCO_News_250808.py

# 원본 데이터 파일 확인
ls -la .naming_backup/config_data_backup/
```

#### 해결 방법
```bash
# 1. 데이터 파일 복원
cp .naming_backup/config_data_backup/posco_news_250808_data.json ./posco_news_data.json
cp .naming_backup/config_data_backup/posco_news_250808_cache.json ./posco_news_cache.json
cp .naming_backup/config_data_backup/posco_news_250808_historical.json ./posco_news_historical_cache.json

# 2. 메인 스크립트 복원
cp .naming_backup/config_data_backup/Posco_News_mini.py .

# 3. 폴더 구조 복원
mv Monitoring/POSCO_News_250808 Monitoring/Posco_News_mini
```

### 시나리오 3: Python 스크립트 import 오류

#### 문제 진단
```bash
# Python 스크립트 실행 테스트
python3 -c "import WatchHamster_v3.0.log
python3 -c "import WatchHamster_v3.0.log
```

#### 해결 방법
```bash
# 1. Python 파일 복원
cp .naming_backup/scripts/demo_v2_integration.py .
cp .naming_backup/scripts/test_v2_integration.py .
cp .naming_backup/scripts/test_v2_notification_integration.py .

# 2. 모듈 경로 확인
# BROKEN_REF: python3 -c "import sys; print('\n'.join(sys.path))"

# 3. 테스트 실행
# BROKEN_REF: python3 demo_v2_integration.py
```

### 시나리오 4: 폴더 구조 문제

#### 문제 진단
```bash
# 폴더 구조 확인
find Monitoring/ -type d -name "*WatchHamster*" -o -name "*POSCO_News*"
find .kiro/specs/ -type d -name "*watchhamster*" -o -name "*posco*"
```

#### 해결 방법
```bash
# 1. 폴더명 복원
mv Monitoring/WatchHamster_v3.0 Monitoring/Posco_News_mini_v2
mv Monitoring/POSCO_News_250808 Monitoring/Posco_News_mini
mv .kiro/specs/watchhamster-v3.0-integration .kiro/specs/posco-watchhamster-v2-integration

# 2. 내부 파일 경로 참조 확인
grep -r "WatchHamster_v3.0" . --include="*.py" --include="*.sh" --include="*.bat"
grep -r "POSCO_News_250808" . --include="*.py" --include="*.sh" --include="*.bat"
```

## 🚨 응급 복구 절차

### 완전 시스템 복구
시스템이 완전히 작동하지 않는 경우:

```bash
# 1. 전체 백업에서 복구 (사전에 생성한 백업 사용)
rm -rf ./*
cp -r ../posco_project_backup_20250808_140000/* .

# 2. 또는 Git에서 복구 (Git 사용 시)
git reset --hard HEAD~1
git clean -fd

# 3. 권한 복구
chmod +x *.sh *.bat *.command
chmod 644 *.py *.json *.md
```

### 선택적 복구
특정 부분만 문제가 있는 경우:

```bash
# 1. 중요 실행 파일만 복구
cp ".naming_backup/scripts/🐹워치햄스터_총괄_관리_센터_v3.bat" .
cp .naming_backup/scripts/posco_main_notifier.py ./Monitoring/Posco_News_mini/

# 2. 데이터 파일만 복구
cp .naming_backup/config_data_backup/*.json .

# 3. 특정 폴더만 복구
rm -rf Monitoring/POSCO_News_250808
cp -r .naming_backup/Monitoring/Posco_News_mini Monitoring/
```

## 📋 롤백 후 확인 사항

### 필수 확인 항목
```bash
# 1. 주요 실행 파일 존재 확인
ls -la 🐹워치햄스터_총괄_관리_센터_v3.bat
ls -la 🎛️POSCO_제어센터_실행_v2.bat
ls -la Posco_News_mini.py

# 2. 데이터 파일 존재 확인
ls -la posco_news_data.json
ls -la posco_news_cache.json
ls -la posco_news_historical_cache.json

# 3. 폴더 구조 확인
ls -la Monitoring/Posco_News_mini/
ls -la Monitoring/Posco_News_mini_v2/

# 4. 실행 권한 확인
ls -la *.bat *.sh *.command
```

### 기능 테스트
```bash
# 1. WatchHamster 제어센터 테스트
./.naming_backup/scripts/.naming_backup/scripts/🐹워치햄스터_총괄_관리_센터_v3.bat

# 2. POSCO News 시스템 테스트
python3 .filename_standardization_backup/.filename_standardization_backup/Posco_News_mini.py.backup_20250809_182505.backup_20250809_182505 --test

# 3. 통합 테스트
# BROKEN_REF: python3 test_v2_integration.py
```

### 성능 확인
```bash
# 1. 시스템 리소스 사용량 확인
python3 test_performance_monitoring.py

# 2. 응답 시간 확인
# BROKEN_REF: python3 demo_v2_integration.py --benchmark

# 3. 메모리 사용량 확인
ps aux | grep python | grep posco
```

## 🔄 롤백 후 재시도 가이드

### 문제 분석 후 재시도
롤백 후 문제를 분석하고 다시 마이그레이션을 시도하는 경우:

```bash
# 1. 문제 원인 분석
python3 posco_file_renamer.py --analyze-failure

# 2. 부분적 마이그레이션 시도
python3 posco_file_renamer.py --watchhamster --dry-run
python3 posco_file_renamer.py --posco-news --dry-run

# 3. 단계별 마이그레이션
python3 posco_file_renamer.py --watchhamster --step-by-step
```

### 점진적 마이그레이션
```bash
# 1. 파일명만 먼저 변경
python3 posco_file_renamer.py --files-only

# 2. 폴더명 변경
python3 posco_file_renamer.py --folders-only

# 3. 코드 내부 변경
python3 python_naming_standardizer.py
```

## 📞 지원 및 문의

### 롤백 실패 시 연락처
- **긴급 지원**: POSCO WatchHamster Emergency Support
- **기술 지원**: POSCO Development Team
- **문서 버전**: v3.0

### 로그 수집 (롤백 실패 시)
```bash
# 롤백 관련 로그 수집
tar -czf rollback_debug.tar.gz \
    file_renaming.log \
    .naming_backup/operations_log.json \
    .naming_backup/mapping_table.json \
    rollback_*.log
```

---

## ⚠️ 중요 주의사항

1. **백업 확인**: 롤백 전에 반드시 백업 파일 존재를 확인하세요
2. **프로세스 종료**: 롤백 전에 모든 관련 프로세스를 종료하세요
3. **권한 확인**: 롤백 후 파일 권한을 확인하고 필요시 수정하세요
4. **테스트 실행**: 롤백 후 반드시 기능 테스트를 수행하세요
5. **문서 업데이트**: 롤백 후 관련 문서를 이전 버전으로 업데이트하세요

**🔄 롤백은 안전한 작업이지만, 신중하게 수행하고 완료 후 반드시 시스템 전체를 테스트하세요.**