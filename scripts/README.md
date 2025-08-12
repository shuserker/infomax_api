# 자동화 스크립트 (Automation Scripts)

POSCO 시스템의 다양한 작업을 자동화하는 스크립트들입니다.

## 스크립트 카테고리

### 테스트 실행 스크립트
- `run_comprehensive_tests.py` - 종합 테스트 실행
- `run_comprehensive_test_system.py` - 종합 테스트 시스템 실행
- `run_end_to_end_tests.py` - 엔드투엔드 테스트 실행
- `run_final_integration_tests.py` - 최종 통합 테스트 실행
- `test_runner.sh` - 테스트 러너 셸 스크립트

### 통합 테스트 시스템
- `enhanced_final_integration_test_system.py` - 향상된 최종 통합 테스트 시스템
- `final_integration_test_system.py` - 최종 통합 테스트 시스템
- `comprehensive_test_system.py` - 종합 테스트 시스템
- `simplified_integration_test.py` - 간소화된 통합 테스트
- `final_integration_test_simple.py` - 간단한 최종 통합 테스트
- `comprehensive_system_execution_test.py` - 종합 시스템 실행 테스트

### 마이그레이션 스크립트
- `migrate_to_v2.sh` - v2로 마이그레이션
- `run_migration_verification.sh` - 마이그레이션 검증 실행
- `rollback_migration.sh` - 마이그레이션 롤백
- `check_migration_requirements.sh` - 마이그레이션 요구사항 확인

### 제어 및 관리 스크립트
- `test_control_center_functions.sh` - 제어센터 기능 테스트
- `quality_management_control.sh` - 품질 관리 제어
- `verify_task6_implementation.sh` - Task 6 구현 검증

### 시스템 관리 스크립트
- `cleanup_old_files.sh` - 오래된 파일 정리
- `demo_watchhamster_v3.0_integration.py` - 워치햄스터 v3.0 통합 데모

## 사용법

### 테스트 실행
```bash
# 모든 테스트 실행
bash scripts/test_runner.sh

# 종합 테스트 실행
python scripts/run_comprehensive_tests.py

# 엔드투엔드 테스트 실행
python scripts/run_end_to_end_tests.py

# 최종 통합 테스트 실행
python scripts/run_final_integration_tests.py
```

### 마이그레이션
```bash
# v2로 마이그레이션
bash scripts/migrate_to_v2.sh

# 마이그레이션 검증
bash scripts/run_migration_verification.sh

# 마이그레이션 롤백 (필요시)
bash scripts/rollback_migration.sh
```

### 시스템 관리
```bash
# 오래된 파일 정리
bash scripts/cleanup_old_files.sh

# 품질 관리 제어
bash scripts/quality_management_control.sh

# 제어센터 기능 테스트
bash scripts/test_control_center_functions.sh
```

### 통합 테스트 시스템
```bash
# 향상된 최종 통합 테스트
python scripts/enhanced_final_integration_test_system.py

# 종합 테스트 시스템
python scripts/comprehensive_test_system.py

# 간소화된 통합 테스트
python scripts/simplified_integration_test.py
```

## 스크립트 실행 순서

일반적인 시스템 관리 작업 순서:

1. **마이그레이션 준비**
   ```bash
   bash scripts/check_migration_requirements.sh
   ```

2. **마이그레이션 실행**
   ```bash
   bash scripts/migrate_to_v2.sh
   ```

3. **마이그레이션 검증**
   ```bash
   bash scripts/run_migration_verification.sh
   ```

4. **종합 테스트 실행**
   ```bash
   python scripts/run_comprehensive_tests.py
   ```

5. **최종 통합 테스트**
   ```bash
   python scripts/run_final_integration_tests.py
   ```

6. **시스템 정리**
   ```bash
   bash scripts/cleanup_old_files.sh
   ```

## 로그 및 결과

스크립트 실행 결과는 다음 위치에 저장됩니다:

- 테스트 결과: `test_results.json`
- 실행 로그: 각 스크립트별 `.log` 파일
- 보고서: `reports/` 디렉토리

## 주의사항

- 스크립트 실행 전 백업을 생성하세요
- 운영 환경에서는 신중하게 실행하세요
- 실행 권한을 확인하세요 (`chmod +x script_name.sh`)
- 의존성을 확인하세요 (Python 패키지, 시스템 도구 등)
- 실행 결과를 반드시 확인하세요

## 스크립트 개발 가이드

새로운 스크립트 작성 시:

1. 적절한 shebang 사용 (`#!/bin/bash` 또는 `#!/usr/bin/env python3`)
2. 오류 처리 포함
3. 로깅 기능 추가
4. 도움말 옵션 제공
5. 실행 권한 설정
6. README에 문서화