# POSCO 네이밍 컨벤션 표준화 설계

## 개요

POSCO 프로젝트의 모든 파일, 폴더, 주석, 변수명을 일관된 네이밍 컨벤션으로 표준화하는 시스템 설계

## 🚨 핵심 설계 원칙

### 내용 및 로직 보존
- **네이밍만 변경**: 파일명, 폴더명, 변수명, 클래스명, 주석만 변경
- **기능 보존**: 모든 코드 로직과 알고리즘은 그대로 유지
- **메시지 보존**: 사용자 인터페이스 텍스트 내용은 변경하지 않음
- **데이터 호환성**: 기존 데이터 파일과의 호환성 완전 보장

## 아키텍처

### 버전 체계 아키텍처

```
POSCO 프로젝트
├── WatchHamster (v3.0 체계)
│   ├── 파일명: *_v3.0_*
│   ├── 폴더명: WatchHamster_v3.0_*
│   ├── 클래스명: *WatchHamsterV30*
│   └── 변수명: watchhamster_v3_0_*
│
└── POSCO_News (날짜 체계)
    ├── 파일명: *_250808_*
    ├── 폴더명: POSCO_News_250808_*
    ├── 클래스명: *PoscoNews250808*
    └── 변수명: posco_news_250808_*
```

## 컴포넌트 및 인터페이스

### 1. 네이밍 컨벤션 매니저

```python
class NamingConventionManager:
    """네이밍 컨벤션 관리 클래스"""
    
    WATCHHAMSTER_VERSION = "v3.0"
    POSCO_NEWS_VERSION = "250808"
    
    def standardize_watchhamster_name(self, name: str) -> str:
        """워치햄스터 관련 이름 표준화"""
        pass
    
    def standardize_posco_news_name(self, name: str) -> str:
        """포스코 뉴스 관련 이름 표준화"""
        pass
```

### 2. 파일 리네이밍 시스템

```python
class FileRenamingSystem:
    """파일 및 폴더 이름 변경 시스템"""
    
    def rename_watchhamster_files(self) -> List[str]:
        """워치햄스터 관련 파일들 이름 변경"""
        pass
    
    def rename_posco_news_files(self) -> List[str]:
        """포스코 뉴스 관련 파일들 이름 변경"""
        pass
```

### 3. 코드 리팩토링 시스템

```python
class CodeRefactoringSystem:
    """코드 내부 네이밍 표준화 시스템"""
    
    def update_comments(self, file_path: str) -> bool:
        """파일 내부 주석 업데이트"""
        pass
    
    def update_variable_names(self, file_path: str) -> bool:
        """변수명 표준화"""
        pass
```

## 데이터 모델

### 네이밍 규칙 정의

```python
@dataclass
class NamingRule:
    """네이밍 규칙 데이터 모델"""
    component: str  # "watchhamster" or "posco_news"
    version: str    # "v3.0" or "250808"
    file_pattern: str
    folder_pattern: str
    class_pattern: str
    variable_pattern: str
    comment_pattern: str
```

### 변경 작업 추적

```python
@dataclass
class RenamingTask:
    """이름 변경 작업 추적"""
    old_name: str
    new_name: str
    file_type: str  # "file", "folder", "class", "variable", "comment"
    status: str     # "pending", "completed", "failed"
    timestamp: datetime
```

## 구현 계획

### Phase 1: 파일 및 폴더명 표준화

#### 워치햄스터 관련 파일들
```
기존 → 새로운 이름

# 제어센터 파일들
🐹워치햄스터_총괄_관리_센터_v3.bat → 🐹WatchHamster_v3.0_Control_Center.bat
🎛️POSCO_제어센터_실행_v2.bat → 🎛️WatchHamster_v3.0_Control_Panel.bat
watchhamster_control_center.sh → watchhamster_v3.0_control_center.sh

# Python 스크립트들
monitor_WatchHamster.py → monitor_WatchHamster_v3.0.py
demo_v2_integration.py → demo_watchhamster_v3.0_integration.py
test_v2_integration.py → test_watchhamster_v3.0_integration.py

# 폴더들
Monitoring/Posco_News_mini_v2/ → Monitoring/WatchHamster_v3.0/
```

#### 포스코 뉴스 관련 파일들
```
기존 → 새로운 이름

# 메인 스크립트들
Posco_News_mini.py → POSCO_News_20250808.py
posco_main_notifier.py → posco_news_20250808_notifier.py

# 데이터 파일들
posco_news_data.json → posco_news_20250808_data.json
posco_news_cache.json → posco_news_20250808_cache.json

# 폴더들
Monitoring/Posco_News_mini/ → Monitoring/POSCO_News_20250808/
```

### Phase 2: 코드 내부 표준화

#### Python 클래스명
```python
# 기존
class PoscoMonitorWatchHamster:
class EnhancedProcessManager:

# 새로운
class WatchHamsterV30Monitor:
class WatchHamsterV30ProcessManager:
```

#### 변수명 및 상수
```python
# 기존
WATCHHAMSTER_VERSION = "v2.0"
posco_news_version = "mini_v2"

# 새로운
WATCHHAMSTER_VERSION = "v3.0"
POSCO_NEWS_VERSION = "250808"
```

#### 주석 표준화
```python
# 기존
"""
POSCO WatchHamster v2.0 Integration
워치햄스터 v2 통합 시스템
"""

# 새로운
"""
POSCO WatchHamster v3.0 Integration
워치햄스터 v3.0 통합 시스템
POSCO News 250808 호환
"""
```

### Phase 3: 문서 및 설정 파일 표준화

#### 마크다운 문서
```markdown
# 기존
# POSCO 워치햄스터 v2.0 가이드

# 새로운
# POSCO WatchHamster v3.0 사용자 가이드
# POSCO News 250808 연동 시스템
```

#### JSON 설정 파일
```json
{
  "system_info": {
    "watchhamster_version": "v3.0",
    "posco_news_version": "250808",
    "last_updated": "2025-08-08"
  }
}
```

## 에러 핸들링

### 파일 이름 변경 실패 처리
- 파일이 사용 중인 경우 대기 후 재시도
- 권한 문제 발생 시 관리자 권한 요청
- 백업 파일 생성 후 변경 작업 수행

### 코드 리팩토링 실패 처리
- 문법 오류 발생 시 원본 복구
- 의존성 문제 발생 시 단계별 롤백
- 변경 사항 로그 기록 및 추적

## 테스트 전략

### 단위 테스트
- 각 네이밍 규칙 함수별 테스트
- 파일 이름 변경 로직 테스트
- 코드 리팩토링 정확성 테스트

### 통합 테스트
- 전체 시스템 네이밍 일관성 검증
- 변경 후 시스템 정상 동작 확인
- 롤백 기능 정상 동작 테스트

### 검증 테스트
- 모든 파일명이 규칙에 맞는지 검증
- 코드 내부 네이밍 일관성 검증
- 문서 및 주석 표준화 검증