# Design Document

## Overview

POSCO 워치햄스터 시스템의 웹훅 관련 기능 완전 복원 프로젝트입니다. Kiro 최적화 과정에서 손상된 모든 웹훅 메시지와 관련 기능을 수동 작업된 최종 버전(커밋 a763ef8)에서 정확히 복원하고, 신규 추가된 시스템 운영 기능과의 호환성을 보장하는 것이 목표입니다.

## Architecture

### 복원 대상 시스템 구조

```
POSCO 워치햄스터 v3.0
├── 웹훅 관련 기능 (복원 대상)
│   ├── send_status_notification()
│   ├── send_notification()
│   ├── send_status_report_v2()
│   └── 모든 Dooray 웹훅 메시지
├── 신규 시스템 운영 기능 (유지)
│   ├── v3.0 아키텍처 컴포넌트
│   ├── 성능 모니터링 시스템
│   └── 통합 리포트 스케줄러
└── 호환성 레이어 (신규 구현)
    ├── 웹훅-신규시스템 인터페이스
    └── 충돌 방지 메커니즘
```

### 복원 전략

1. **선택적 복원**: 웹훅 관련 부분만 정확히 식별하여 복원
2. **호환성 우선**: 신규 기능과 충돌하지 않도록 중간 검증
3. **점진적 적용**: 단계별로 복원하여 문제 발생 시 롤백 가능

## Components and Interfaces

### 1. 웹훅 메시지 복원 컴포넌트

#### WebhookMessageRestorer
```python
class WebhookMessageRestorer:
    """웹훅 메시지 복원 전담 클래스"""
    
    def __init__(self, target_file_path, source_commit):
        self.target_file = target_file_path
        self.source_commit = source_commit
        self.backup_created = False
    
    def extract_webhook_functions(self):
        """원본 커밋에서 웹훅 관련 함수들 추출"""
        pass
    
    def identify_webhook_sections(self):
        """현재 파일에서 웹훅 관련 섹션 식별"""
        pass
    
    def restore_webhook_messages(self):
        """웹훅 메시지들을 원본으로 복원"""
        pass
```

### 2. 호환성 검증 컴포넌트

#### CompatibilityChecker
```python
class CompatibilityChecker:
    """신규 기능과 복원된 웹훅 기능 간 호환성 검증"""
    
    def check_function_conflicts(self):
        """함수명 충돌 검사"""
        pass
    
    def check_variable_conflicts(self):
        """변수명 충돌 검사"""
        pass
    
    def check_import_conflicts(self):
        """import 충돌 검사"""
        pass
    
    def generate_compatibility_report(self):
        """호환성 검사 보고서 생성"""
        pass
```

### 3. 백업 및 롤백 컴포넌트

#### BackupManager
```python
class BackupManager:
    """복원 작업 전 백업 및 롤백 관리"""
    
    def create_backup(self):
        """현재 상태 백업"""
        pass
    
    def validate_backup(self):
        """백업 파일 무결성 검증"""
        pass
    
    def rollback_if_needed(self):
        """문제 발생 시 롤백"""
        pass
```

## Data Models

### 웹훅 메시지 구조
```python
@dataclass
class WebhookMessage:
    """웹훅 메시지 데이터 모델"""
    function_name: str
    message_template: str
    variables: List[str]
    formatting: Dict[str, str]
    line_breaks: str  # \n vs /n 구분
    encoding: str
```

### 복원 작업 상태
```python
@dataclass
class RestorationStatus:
    """복원 작업 진행 상태"""
    current_step: str
    completed_functions: List[str]
    failed_functions: List[str]
    compatibility_issues: List[str]
    backup_path: str
    rollback_available: bool
```

## Error Handling

### 복원 작업 중 오류 처리

1. **함수 추출 실패**
   - 원본 커밋에서 함수를 찾을 수 없는 경우
   - 대안: 수동 확인 후 사용자 입력으로 처리

2. **호환성 충돌**
   - 신규 기능과 복원된 기능 간 충돌
   - 대안: 중간 어댑터 레이어 구현

3. **메시지 포맷 불일치**
   - 복원된 메시지가 현재 시스템과 맞지 않는 경우
   - 대안: 포맷 변환 로직 적용

### 롤백 시나리오

```python
def handle_restoration_failure(error_type, error_details):
    """복원 실패 시 처리 로직"""
    if error_type == "CRITICAL_COMPATIBILITY_ISSUE":
        # 즉시 롤백
        backup_manager.rollback_immediately()
    elif error_type == "PARTIAL_RESTORATION_FAILURE":
        # 부분 롤백 후 수동 개입 요청
        backup_manager.partial_rollback(error_details.failed_functions)
    else:
        # 로그 기록 후 계속 진행
        logger.warning(f"Minor issue: {error_details}")
```

## Testing Strategy

### 1. 단위 테스트
- 각 웹훅 함수별 메시지 포맷 검증
- 줄바꿈 문자 처리 정확성 확인
- 한국어/영어 제품명 표시 검증

### 2. 통합 테스트
- 복원된 웹훅 기능과 신규 시스템 간 상호작용 테스트
- 실제 Dooray 웹훅 전송 테스트
- 전체 워치햄스터 시스템 동작 검증

### 3. 회귀 테스트
- 기존 기능들이 여전히 정상 작동하는지 확인
- 성능 저하가 없는지 검증
- 메모리 누수 등 부작용 검사

### 4. 사용자 승인 테스트
- 실제 알림 메시지가 사용자 요구사항에 맞는지 확인
- 메시지 가독성 및 정보 완성도 검증
- 사용자 피드백 반영

## Implementation Phases

### Phase 1: 분석 및 준비
1. 현재 파일과 원본 커밋 간 차이점 상세 분석
2. 웹훅 관련 함수 및 메시지 목록 작성
3. 백업 시스템 구축

### Phase 2: 선택적 복원
1. 웹훅 메시지 템플릿 복원
2. 관련 함수 로직 복원
3. 설정값 및 상수 복원

### Phase 3: 호환성 검증
1. 신규 기능과의 충돌 검사
2. 중간 체크포인트에서 문제 해결
3. 통합 테스트 수행

### Phase 4: 최종 검증 및 배포
1. 전체 시스템 테스트
2. 실제 웹훅 전송 테스트
3. 사용자 승인 및 문서화

## Security Considerations

1. **백업 파일 보안**: 민감한 웹훅 URL 정보 보호
2. **롤백 안전성**: 롤백 과정에서 데이터 손실 방지
3. **테스트 격리**: 테스트 중 실제 알림 발송 방지

## Performance Impact

- **복원 작업**: 일회성 작업으로 성능 영향 최소
- **런타임 성능**: 복원 후 기존 성능 수준 유지 목표
- **메모리 사용**: 추가 메모리 사용량 최소화