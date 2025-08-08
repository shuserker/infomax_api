# POSCO WatchHamster v2 - New Architecture

새로운 아키텍처를 적용한 POSCO 워치햄스터 시스템 v2

## 📁 폴더 구조

```
Posco_News_mini_v2/
├── core/                                    # 핵심 컴포넌트들
│   ├── enhanced_process_manager.py         # 향상된 프로세스 관리자
│   ├── module_registry.py                  # 모듈 레지스트리 시스템
│   ├── notification_manager.py             # 통합 알림 관리자
│   └── watchhamster_integration.py         # 통합 인터페이스
├── modules.json                             # 모듈 설정 파일
└── README.md                               # 이 파일
```

## 🔧 핵심 컴포넌트

### 1. ProcessManager (enhanced_process_manager.py)
- **목적**: 하위 프로세스의 생명주기 관리
- **주요 기능**:
  - 프로세스 시작/중지/재시작
  - 헬스체크 및 상태 모니터링
  - 3단계 자동 복구 로직
  - 시스템 리소스 모니터링

### 2. ModuleRegistry (module_registry.py)
- **목적**: JSON 기반 모듈 설정 관리
- **주요 기능**:
  - 동적 모듈 등록/해제
  - 의존성 관리 및 시작 순서 결정
  - 설정 유효성 검사
  - 모듈 상태 추적

### 3. NotificationManager (notification_manager.py)
- **목적**: 통합 알림 시스템
- **주요 기능**:
  - 기존 알림 텍스트 완전 보존
  - 알림 타입별 메서드 분리
  - 템플릿 기반 알림 시스템
  - 알림 통계 및 성공률 추적

### 4. WatchHamster Integration (watchhamster_integration.py)
- **목적**: 모든 컴포넌트를 통합하는 메인 인터페이스
- **주요 기능**:
  - 기존 워치햄스터와의 호환성 보장
  - 새로운 아키텍처 적용
  - 통합된 시스템 관리 인터페이스

## 📋 모듈 설정 (modules.json)

기본 등록된 모듈들:
- `posco_main_notifier`: POSCO 메인 뉴스 알림 시스템
- `realtime_news_monitor`: 실시간 뉴스 모니터링 시스템
- `integrated_report_scheduler`: 통합 리포트 스케줄러
- `historical_data_collector`: 히스토리 데이터 수집기

## 🚀 사용 방법

```python
from core.watchhamster_integration import EnhancedWatchHamster

# 초기화
watchhamster = EnhancedWatchHamster(
    script_dir="/path/to/scripts",
    webhook_url="https://dooray.webhook.url",
    bot_profile_url="https://profile.image.url"
)

# 모든 프로세스 시작
watchhamster.start_all_processes()

# 헬스체크 수행
health_results = watchhamster.perform_health_check()

# 상태 보고 전송
watchhamster.send_status_report()

# 모든 프로세스 중지
watchhamster.stop_all_processes()
```

## 🎯 주요 개선사항

1. **모듈화**: 기존 단일 클래스에서 역할별 컴포넌트로 분리
2. **확장성**: 새로운 모듈을 쉽게 추가할 수 있는 레지스트리 시스템
3. **안정성**: 3단계 자동 복구 로직과 지능적 헬스체크
4. **호환성**: 기존 알림 텍스트와 기능 완전 보존
5. **관리성**: JSON 기반 설정 관리 및 동적 모듈 관리

## 📊 Requirements 매핑

- **Requirement 1.1, 2.1, 4.1**: 워치햄스터 핵심 컴포넌트 구현 ✅
- **Requirement 1.2, 2.2**: ProcessManager 클래스 구현 ✅
- **Requirement 5.1, 5.2**: ModuleRegistry 클래스 구현 ✅
- **Requirement 4.2, 4.3, 4.4**: NotificationManager 클래스 구현 ✅

## 🔄 다음 단계

2단계: 워치햄스터 메인 클래스 리팩토링
- 기존 `monitor_WatchHamster.py`를 새로운 아키텍처로 전환
- 기존 기능 보존하면서 새로운 컴포넌트들 통합