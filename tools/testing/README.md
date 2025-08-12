# 테스트 도구 (Testing Tools)

POSCO 시스템의 다양한 기능을 테스트하는 도구들입니다.

## 테스트 카테고리

### 자동화 및 수리 테스트
- `test_automated_repair_system.py` - 자동 수리 시스템 테스트
- `test_comprehensive_test_system.py` - 종합 테스트 시스템 테스트

### 설정 및 표준화 테스트
- `test_config_data_standardization.py` - 설정 데이터 표준화 테스트
- `test_documentation_standardization.py` - 문서 표준화 테스트
- `test_shell_batch_standardization.py` - 셸/배치 표준화 테스트
- `test_system_output_message_standardization.py` - 시스템 출력 메시지 표준화 테스트

### 파일 및 네이밍 테스트
- `test_file_renaming_system.py` - 파일 이름 변경 시스템 테스트
- `test_naming_convention_manager.py` - 네이밍 규칙 관리자 테스트
- `test_naming_standardization_verification.py` - 네이밍 표준화 검증 테스트

### 통합 및 엔드투엔드 테스트
- `test_end_to_end_integration.py` - 엔드투엔드 통합 테스트
- `test_control_center_integration.py` - 제어센터 통합 테스트
- `test_module_registry_integration.py` - 모듈 레지스트리 통합 테스트
- `test_watchhamster_v3.0_integration.py` - 워치햄스터 v3.0 통합 테스트
- `test_watchhamster_v3.0_notification.py` - 워치햄스터 v3.0 알림 테스트

### 마이그레이션 및 검증 테스트
- `test_migration_verification_system.py` - 마이그레이션 검증 시스템 테스트
- `test_rollback_functionality.py` - 롤백 기능 테스트
- `test_process_lifecycle.py` - 프로세스 생명주기 테스트

### 성능 및 품질 테스트
- `test_performance_monitoring.py` - 성능 모니터링 테스트
- `test_continuous_quality_management.py` - 지속적 품질 관리 테스트
- `test_webhook_integrity.py` - 웹훅 무결성 테스트

## 사용법

### 개별 테스트 실행
```bash
# 특정 테스트 실행
python tools/testing/test_automated_repair_system.py

# 모든 테스트 실행 (scripts 디렉토리의 test_runner.sh 사용)
bash scripts/test_runner.sh
```

### 테스트 결과 확인
테스트 실행 후 생성되는 로그 파일과 보고서를 확인하세요.

## 테스트 작성 가이드

새로운 테스트를 작성할 때는 다음 규칙을 따르세요:

1. 파일명: `test_[기능명].py` 형식
2. 클래스명: `Test[기능명]` 형식  
3. 메서드명: `test_[테스트내용]` 형식
4. 적절한 assert 문 사용
5. 테스트 전후 정리 코드 포함

## 주의사항

- 테스트는 독립적으로 실행 가능해야 합니다
- 외부 의존성을 최소화하세요
- 테스트 데이터는 임시로 생성하고 정리하세요
- 실제 운영 데이터를 사용하지 마세요