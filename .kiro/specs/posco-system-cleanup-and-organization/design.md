# POSCO 시스템 정리 및 구조화 설계 문서

## 개요

POSCO 시스템의 누적된 파일들을 체계적으로 정리하고 구조화하여 유지보수성과 사용성을 향상시키는 시스템을 설계합니다. 기존 시스템의 기능과 로직은 절대 변경하지 않으며, 파일 구조와 언어 설정만 최적화합니다.

## 아키텍처

### 전체 시스템 구조

```
POSCO_System_Root/
├── core/                          # 핵심 시스템 파일
│   ├── POSCO_News_250808.py      # 메인 뉴스 모니터링 시스템
│   ├── 🐹POSCO_워치햄스터_v3_제어센터.bat
│   ├── 🐹POSCO_워치햄스터_v3_제어센터.command
│   └── Monitoring/                # 모니터링 시스템
├── tools/                         # 개발 및 유지보수 도구
│   ├── repair/                    # 수리 도구들
│   ├── testing/                   # 테스트 도구들
│   └── quality/                   # 품질 관리 도구들
├── docs/                          # 문서화
│   ├── user_guides/              # 사용자 가이드
│   ├── technical/                # 기술 문서
│   └── troubleshooting/          # 문제 해결 가이드
├── archive/                       # 완료된 작업 보관
│   ├── task_summaries/           # 작업 완료 보고서들
│   ├── migration_logs/           # 마이그레이션 로그
│   └── backups/                  # 백업 파일들
├── config/                        # 설정 파일들
│   ├── language_settings.json    # 언어 설정
│   ├── cleanup_rules.json        # 정리 규칙
│   └── system_config.json        # 시스템 설정
└── scripts/                       # 실행 스크립트들
    ├── cleanup_system.py         # 정리 스크립트
    ├── verify_integrity.py       # 무결성 검증
    └── rollback_system.py        # 롤백 스크립트
```

## 컴포넌트 설계

### 1. 파일 분류 시스템 (FileClassificationSystem)

#### 목적
프로젝트 내 모든 파일을 분석하여 핵심 파일, 도구 파일, 임시 파일, 문서 파일로 분류합니다.

#### 주요 기능
```python
class FileClassificationSystem:
    def __init__(self):
        self.core_patterns = [
            "POSCO_News_250808.py",
            "🐹POSCO_워치햄스터_v3_제어센터.*",
            "Monitoring/**/*.py"
        ]
        self.tool_patterns = [
            "*_repair*.py",
            "*_test*.py", 
            "*_verification*.py"
        ]
        self.temp_patterns = [
            "task*_completion_summary.md",
            "*.backup",
            "*.bak",
            "*_temp*"
        ]
        self.doc_patterns = [
            "*.md",
            "*.txt",
            "*_guide*",
            "*_manual*"
        ]
    
    def classify_file(self, file_path: str) -> FileCategory
    def scan_directory(self, root_path: str) -> Dict[FileCategory, List[str]]
    def generate_classification_report(self) -> str
```

#### 분류 기준
1. **핵심 파일 (Core Files)**
   - POSCO_News_250808.py
   - 워치햄스터 제어센터 파일들
   - Monitoring/ 디렉토리 내 모든 파일
   - 실제 운영에 필요한 Python 모듈들

2. **도구 파일 (Tool Files)**
   - 수리 도구들 (*_repair*.py, *_fixer*.py)
   - 테스트 파일들 (test_*.py, *_test*.py)
   - 검증 도구들 (*_verification*.py, *_validator*.py)
   - 자동화 도구들 (automated_*.py, enhanced_*.py)

3. **임시 파일 (Temporary Files)**
   - 작업 완료 보고서들 (task*_completion_summary.md)
   - 백업 파일들 (*.backup, *.bak)
   - 로그 파일들 (*.log)
   - 임시 설정 파일들

4. **문서 파일 (Documentation Files)**
   - 사용자 가이드 (*_guide*.md, *_manual*.md)
   - 기술 문서 (*_documentation*.md)
   - README 파일들
   - 트러블슈팅 가이드

### 2. 언어 설정 관리 시스템 (LanguageSettingsManager)

#### 목적
모든 시스템 메시지, 상태 표시, 로그 출력을 한글로 통일합니다.

#### 주요 기능
```python
class LanguageSettingsManager:
    def __init__(self):
        self.language_mappings = {
            "completed": "완료",
            "in_progress": "진행중", 
            "not_started": "시작안함",
            "failed": "실패",
            "success": "성공",
            "error": "오류",
            "warning": "경고",
            "info": "정보"
        }
        self.message_templates = {
            "file_moved": "파일이 {source}에서 {destination}으로 이동되었습니다",
            "backup_created": "백업이 {path}에 생성되었습니다",
            "cleanup_completed": "정리 작업이 완료되었습니다"
        }
    
    def translate_status(self, status: str) -> str
    def format_message(self, template_key: str, **kwargs) -> str
    def update_system_messages(self, file_path: str) -> None
    def create_language_config(self) -> None
```

#### 언어 설정 파일 구조
```json
{
    "default_language": "ko",
    "status_translations": {
        "completed": "완료",
        "in_progress": "진행중",
        "not_started": "시작안함",
        "failed": "실패",
        "success": "성공"
    },
    "message_templates": {
        "ko": {
            "file_operation": {
                "moved": "파일이 {source}에서 {destination}으로 이동되었습니다",
                "copied": "파일이 {source}에서 {destination}으로 복사되었습니다",
                "deleted": "파일 {path}가 삭제되었습니다"
            },
            "system_status": {
                "starting": "시스템을 시작하는 중입니다",
                "stopping": "시스템을 중지하는 중입니다",
                "ready": "시스템이 준비되었습니다"
            }
        }
    }
}
```

### 3. 파일 이동 및 정리 시스템 (FileOrganizationSystem)

#### 목적
분류된 파일들을 적절한 디렉토리로 이동하고 구조화합니다.

#### 주요 기능
```python
class FileOrganizationSystem:
    def __init__(self, classification_system: FileClassificationSystem):
        self.classifier = classification_system
        self.move_rules = {
            FileCategory.CORE: "core/",
            FileCategory.TOOLS: "tools/",
            FileCategory.DOCS: "docs/",
            FileCategory.TEMP: "archive/temp/",
            FileCategory.ARCHIVE: "archive/"
        }
    
    def create_directory_structure(self) -> None
    def move_files_by_category(self, category: FileCategory) -> MoveResult
    def update_file_references(self, old_path: str, new_path: str) -> None
    def generate_move_report(self) -> str
```

#### 이동 규칙
1. **핵심 파일들** → `core/` 디렉토리
   - 기존 기능과 경로 참조 유지
   - 심볼릭 링크로 하위 호환성 보장

2. **도구 파일들** → `tools/` 디렉토리
   - 기능별 하위 디렉토리 생성
   - 실행 권한 유지

3. **문서 파일들** → `docs/` 디렉토리
   - 유형별 분류 (user_guides/, technical/, troubleshooting/)
   - 인덱스 파일 자동 생성

4. **임시/완료 파일들** → `archive/` 디렉토리
   - 날짜별 하위 디렉토리
   - 압축 보관 옵션

### 4. 무결성 검증 시스템 (IntegrityVerificationSystem)

#### 목적
파일 이동 후 모든 시스템 기능이 정상 작동하는지 검증합니다.

#### 주요 기능
```python
class IntegrityVerificationSystem:
    def __init__(self):
        self.core_tests = [
            self.test_posco_news_import,
            self.test_watchhamster_execution,
            self.test_monitoring_system,
            self.test_webhook_functionality
        ]
    
    def verify_core_functionality(self) -> VerificationResult
    def test_file_imports(self) -> ImportTestResult
    def test_script_execution(self) -> ExecutionTestResult
    def test_webhook_connectivity(self) -> WebhookTestResult
    def generate_verification_report(self) -> str
```

#### 검증 항목
1. **Python 모듈 Import 테스트**
   - 모든 핵심 모듈이 정상 import되는지 확인
   - 의존성 관계 검증

2. **스크립트 실행 테스트**
   - 배치 파일들이 정상 실행되는지 확인
   - 명령행 인터페이스 테스트

3. **웹훅 기능 테스트**
   - 웹훅 URL 접근성 확인
   - 메시지 전송 기능 테스트

4. **모니터링 시스템 테스트**
   - 모니터링 프로세스 시작/중지 테스트
   - 데이터 수집 기능 확인

### 5. 백업 및 롤백 시스템 (BackupRollbackSystem)

#### 목적
정리 작업 전 백업을 생성하고, 문제 발생 시 롤백 기능을 제공합니다.

#### 주요 기능
```python
class BackupRollbackSystem:
    def __init__(self):
        self.backup_dir = "archive/backups/"
        self.backup_metadata = {}
    
    def create_full_backup(self) -> BackupResult
    def create_incremental_backup(self, changed_files: List[str]) -> BackupResult
    def rollback_to_backup(self, backup_id: str) -> RollbackResult
    def verify_backup_integrity(self, backup_id: str) -> bool
    def cleanup_old_backups(self, retention_days: int = 30) -> None
```

#### 백업 전략
1. **전체 백업**
   - 정리 작업 시작 전 전체 시스템 백업
   - 압축 및 체크섬 생성

2. **단계별 백업**
   - 각 정리 단계마다 증분 백업
   - 변경된 파일만 백업

3. **메타데이터 관리**
   - 백업 시점, 변경 내역, 파일 목록 기록
   - 롤백 시 참조 정보 제공

## 데이터 모델

### 파일 분류 모델
```python
@dataclass
class FileInfo:
    path: str
    size: int
    modified_time: datetime
    category: FileCategory
    importance: ImportanceLevel
    dependencies: List[str]
    
@dataclass
class MoveOperation:
    source_path: str
    destination_path: str
    operation_type: str  # move, copy, symlink
    status: str
    timestamp: datetime
    
@dataclass
class VerificationResult:
    test_name: str
    success: bool
    message: str
    details: Dict[str, Any]
    execution_time: float
```

### 언어 설정 모델
```python
@dataclass
class LanguageConfig:
    default_language: str
    status_translations: Dict[str, str]
    message_templates: Dict[str, Dict[str, str]]
    date_format: str
    number_format: str

@dataclass
class MessageTemplate:
    key: str
    template: str
    parameters: List[str]
    category: str
```

## 인터페이스 설계

### 1. 명령행 인터페이스 (CLI)

```bash
# 전체 정리 실행
python cleanup_system.py --full-cleanup

# 특정 카테고리만 정리
python cleanup_system.py --category tools

# 언어 설정 변경
python cleanup_system.py --set-language ko

# 백업 생성
python cleanup_system.py --create-backup

# 롤백 실행
python cleanup_system.py --rollback backup_20250810_123456

# 무결성 검증
python cleanup_system.py --verify-integrity

# 정리 상태 확인
python cleanup_system.py --status
```

### 2. 설정 파일 인터페이스

#### cleanup_rules.json
```json
{
    "rules": {
        "core_files": {
            "preserve": true,
            "patterns": ["POSCO_News_250808.py", "🐹POSCO_워치햄스터_v3_*"]
        },
        "temp_files": {
            "action": "archive",
            "patterns": ["task*_completion_summary.md", "*.backup"]
        },
        "tool_files": {
            "action": "organize",
            "destination": "tools/"
        }
    },
    "backup": {
        "enabled": true,
        "retention_days": 30,
        "compression": true
    },
    "verification": {
        "enabled": true,
        "tests": ["import", "execution", "webhook"]
    }
}
```

## 오류 처리

### 오류 유형 및 처리 방안

1. **파일 이동 실패**
   - 권한 부족: 관리자 권한 요청
   - 파일 사용 중: 프로세스 종료 후 재시도
   - 디스크 공간 부족: 정리 작업 일시 중단

2. **참조 업데이트 실패**
   - 파일 내용 파싱 오류: 수동 검토 목록에 추가
   - 순환 참조: 경고 메시지 출력 후 계속 진행

3. **검증 실패**
   - Import 오류: 롤백 후 수동 수정 안내
   - 실행 오류: 상세 오류 로그 제공

4. **백업 실패**
   - 저장 공간 부족: 임시 파일 정리 후 재시도
   - 권한 문제: 백업 위치 변경

## 테스트 전략

### 단위 테스트
- 각 컴포넌트별 독립적 테스트
- Mock 객체를 사용한 의존성 격리
- 경계값 및 예외 상황 테스트

### 통합 테스트
- 전체 정리 프로세스 시뮬레이션
- 실제 파일 시스템을 사용한 테스트
- 롤백 기능 검증

### 성능 테스트
- 대용량 파일 처리 성능
- 메모리 사용량 모니터링
- 정리 작업 소요 시간 측정

## 보안 고려사항

### 민감 정보 보호
- 웹훅 URL 및 API 키 식별 및 보호
- 로그 파일에서 민감 정보 마스킹
- 백업 파일 암호화 옵션

### 접근 권한 관리
- 파일 권한 보존
- 실행 권한 유지
- 디렉토리 접근 권한 설정

### 감사 로그
- 모든 파일 이동 작업 기록
- 사용자 작업 추적
- 시스템 변경 이력 보관

---

이 설계를 통해 POSCO 시스템의 기능과 로직을 완전히 보존하면서도 체계적이고 유지보수 가능한 파일 구조를 구축할 수 있습니다.