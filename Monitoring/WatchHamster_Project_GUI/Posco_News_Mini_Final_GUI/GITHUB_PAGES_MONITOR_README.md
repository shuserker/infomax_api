# GitHub Pages 접근성 확인 시스템

POSCO 뉴스 시스템용 완전 독립 GitHub Pages 모니터링 시스템

## 📋 개요

이 시스템은 **Requirements 1.2, 5.4**를 구현하여 GitHub Pages 배포 후 실제 URL 접근 가능성을 검증하고, 접근 실패 시 GUI 알림 및 자동 재배포 옵션을 제공합니다.

## 🎯 주요 기능

### 1. 배포 완료 후 실제 URL 접근 가능성 검증
- ✅ HTTP 상태 코드 확인 (200, 404, 500 등)
- ✅ 응답 시간 측정 및 성능 모니터링
- ✅ 페이지 내용 검증 (제목 추출, 콘텐츠 길이 확인)
- ✅ 다양한 오류 상황 처리 (타임아웃, 연결 오류, DNS 오류)

### 2. HTTP 상태 코드 확인 및 응답 시간 측정
- 📊 실시간 응답 시간 측정 (밀리초 단위)
- 📈 성능 임계값 모니터링 (5초 경고, 10초 심각)
- 🔍 HTTP 헤더 분석 및 저장
- 📋 상세한 접근성 로그 기록

### 3. 접근 실패 시 GUI 알림 및 자동 재배포 옵션 제공
- 🚨 실시간 GUI 알림 시스템
- 🔄 자동 재배포 요청 기능
- ⚠️ 연속 실패 감지 및 알림
- 📱 사용자 친화적 알림 메시지

### 4. GUI에서 GitHub Pages 상태 실시간 모니터링
- 🖥️ 실시간 상태 대시보드
- 📊 모니터링 통계 시각화
- 📝 실시간 로그 뷰어
- 🎛️ 모니터링 제어 패널

## 🏗️ 시스템 구조

```
github_pages_monitor.py          # 핵심 모니터링 엔진
├── GitHubPagesMonitor          # 메인 모니터링 클래스
├── AccessibilityCheck          # 접근성 확인 결과 데이터
├── MonitoringSession           # 모니터링 세션 관리
└── PageStatus/MonitoringMode   # 상태 및 모드 열거형

github_pages_status_gui.py       # GUI 인터페이스
├── GitHubPagesStatusGUI        # 메인 GUI 클래스
├── 실시간 상태 표시           # 상태 표시등, 통계 등
├── 모니터링 제어              # 시작/중지, 설정
└── 알림 및 재배포 요청        # 사용자 인터랙션

test_github_pages_monitor.py     # 종합 테스트 시스템
demo_github_pages_monitor.py     # 데모 및 시연 시스템
```

## 🚀 사용 방법

### 1. 기본 사용법

```python
from github_pages_monitor import GitHubPagesMonitor

# 모니터 인스턴스 생성
monitor = GitHubPagesMonitor()

# 단일 페이지 접근성 확인
check = monitor.check_page_accessibility("https://username.github.io/repository")
print(f"접근 가능: {check.accessible}")
print(f"응답 시간: {check.response_time:.2f}초")
```

### 2. 배포 후 검증

```python
# 배포 후 접근성 검증 (최대 5분 대기)
result = monitor.verify_github_pages_deployment(
    "https://username.github.io/repository", 
    max_wait_time=300
)

if result['deployment_successful']:
    print("✅ 배포 검증 성공!")
else:
    print(f"❌ 배포 검증 실패: {result['error_message']}")
```

### 3. 지속적인 모니터링

```python
# 지속적인 모니터링 시작 (30초 간격)
session_id = monitor.start_continuous_monitoring(
    "https://username.github.io/repository", 
    check_interval=30
)

# 모니터링 중지
monitor.stop_continuous_monitoring()
```

### 4. GUI 모니터링

```python
from github_pages_status_gui import GitHubPagesStatusGUI

# GUI 실행
gui = GitHubPagesStatusGUI()
gui.show()
```

## 🔧 콜백 시스템

시스템은 실시간 알림을 위한 콜백 시스템을 제공합니다:

```python
def status_callback(url, status, details):
    print(f"상태 변경: {url} -> {status.value}")

def alert_callback(message, details):
    print(f"알림: {message}")

def redeploy_callback(reason):
    print(f"재배포 요청: {reason}")
    return True  # 재배포 실행

# 콜백 등록
monitor.register_status_callback(status_callback)
monitor.register_alert_callback(alert_callback)
monitor.register_redeploy_callback(redeploy_callback)
```

## 📊 모니터링 데이터

### 접근성 확인 결과 (AccessibilityCheck)
```python
{
    "timestamp": "2025-09-23T13:41:18.123456",
    "url": "https://username.github.io/repository",
    "status_code": 200,
    "response_time": 1.46,
    "accessible": True,
    "content_length": 12345,
    "page_title": "POSCO News Dashboard",
    "headers": {"content-type": "text/html", ...}
}
```

### 배포 검증 결과
```python
{
    "url": "https://username.github.io/repository",
    "deployment_successful": True,
    "final_accessible": True,
    "checks_performed": 3,
    "total_wait_time": 45.2,
    "checks": [...]  # 각 확인 결과 배열
}
```

## 📁 로그 파일 구조

```
logs/
├── github_pages_monitor.log      # 일반 로그
├── pages_accessibility.json      # 접근성 확인 결과
└── monitoring_sessions.json      # 모니터링 세션 기록
```

## ⚙️ 설정 옵션

### 모니터링 설정
```python
monitor = GitHubPagesMonitor()

# 확인 간격 설정 (기본: 30초)
monitor.check_interval = 60

# 타임아웃 설정 (기본: 30초)
monitor.timeout = 45

# 재시도 설정
monitor.max_retries = 5
monitor.retry_delay = 15

# 성능 임계값 설정
monitor.response_time_warning = 3.0    # 3초 이상 시 경고
monitor.response_time_critical = 8.0   # 8초 이상 시 심각
```

### GUI 설정
GUI는 `config/gui_config.json`에서 기본 GitHub Pages URL을 로드합니다:

```json
{
    "github_pages_url": "https://username.github.io/repository"
}
```

## 🧪 테스트 실행

### 전체 테스트 실행
```bash
python3 test_github_pages_monitor.py
```

### 데모 실행
```bash
python3 demo_github_pages_monitor.py
```

## 📈 성능 특징

### 응답 시간 측정
- ✅ 밀리초 단위 정확도
- ✅ 네트워크 지연 시간 포함
- ✅ DNS 조회 시간 포함
- ✅ SSL 핸드셰이크 시간 포함

### 메모리 효율성
- ✅ HTTP 연결 재사용 (Session 객체)
- ✅ 로그 파일 크기 제한 (최대 1000줄)
- ✅ 메트릭 데이터 자동 정리 (최대 100개 기록)

### 안정성
- ✅ 예외 처리 및 복구
- ✅ 스레드 안전성
- ✅ 리소스 자동 정리
- ✅ 그레이스풀 셧다운

## 🔗 통합 시스템 연동

### 배포 모니터와 연동
```python
# deployment_monitor.py에서 사용
from github_pages_monitor import GitHubPagesMonitor

def _execute_verify_pages(self, session):
    pages_monitor = GitHubPagesMonitor()
    result = pages_monitor.verify_github_pages_deployment(url, max_wait_time=300)
    # 결과 처리...
```

### 통합 배포 시스템과 연동
```python
# integrated_deployment_system.py에서 사용
def _execute_verify_pages(self, session):
    # GitHub Pages 모니터링 시스템 사용
    pages_monitor = GitHubPagesMonitor()
    verification_result = pages_monitor.verify_github_pages_deployment(pages_url)
    # 검증 결과에 따른 처리...
```

## 🚨 오류 처리

### 네트워크 오류
- `ConnectionError`: 연결 실패
- `Timeout`: 응답 시간 초과
- `DNSError`: 도메인 이름 해석 실패

### HTTP 오류
- `404 Not Found`: 페이지 없음
- `500 Internal Server Error`: 서버 오류
- `503 Service Unavailable`: 서비스 이용 불가

### 시스템 오류
- `ImportError`: 모듈 로드 실패
- `FileNotFoundError`: 설정 파일 없음
- `PermissionError`: 로그 파일 쓰기 권한 없음

## 🔄 자동 재배포 시나리오

1. **단일 접근 실패**: 즉시 알림, 수동 재배포 옵션
2. **연속 접근 실패**: 자동 재배포 요청 제안
3. **배포 검증 타임아웃**: 자동 재배포 옵션 제공
4. **성능 저하 감지**: 경고 알림, 모니터링 강화

## 📋 Requirements 구현 상태

### ✅ Requirements 1.2: 배포 완료 후 실제 URL 접근 가능성 검증
- HTTP 상태 코드 확인
- 응답 시간 측정
- 페이지 내용 검증
- 다양한 오류 상황 처리

### ✅ Requirements 5.4: GUI에서 GitHub Pages 상태 실시간 모니터링
- 실시간 상태 대시보드
- 모니터링 통계 시각화
- 사용자 친화적 제어 패널
- 알림 및 재배포 요청 기능

## 🎉 완성된 기능

1. ✅ **완전 독립 실행**: 외부 의존성 없는 스탠드얼론 시스템
2. ✅ **실시간 모니터링**: 지속적인 접근성 확인 및 상태 추적
3. ✅ **GUI 인터페이스**: 사용자 친화적 모니터링 대시보드
4. ✅ **자동 재배포**: 접근 실패 시 자동 재배포 요청 시스템
5. ✅ **성능 분석**: 응답 시간 측정 및 성능 임계값 모니터링
6. ✅ **로그 관리**: 상세한 로그 기록 및 자동 정리
7. ✅ **콜백 시스템**: 실시간 알림 및 이벤트 처리
8. ✅ **테스트 시스템**: 종합적인 테스트 및 데모 시스템

이 시스템은 POSCO 뉴스 시스템의 GitHub Pages 배포 안정성을 크게 향상시키며, 사용자에게 실시간 모니터링과 자동 복구 기능을 제공합니다.