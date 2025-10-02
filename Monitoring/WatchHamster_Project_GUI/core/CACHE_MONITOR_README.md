# 내장형 캐시 데이터 모니터링 시스템

## 📋 개요

내장형 캐시 데이터 모니터링 시스템은 kospi, exchange 데이터를 `data/` 폴더에서 캐시 관리하며, 데이터 부족 시 GUI 경고 알림 및 자동 전송, 과거 데이터 사용 시 GUI에서 명시적 표시 기능을 제공합니다.

**Requirements: 5.3 구현**

## 🎯 주요 기능

### 📊 캐시 데이터 상태 모니터링
- KOSPI, 환율, POSCO 주가, 뉴스 감정 데이터 실시간 모니터링
- 데이터 신선도, 품질, 신뢰도 평가
- 캐시 파일 무결성 검사

### ⚠️ 데이터 부족 시 GUI 경고 알림 및 자동 전송
- 데이터 누락, 만료, 손상 시 즉시 알림
- 자동 데이터 갱신 시도
- 심각도별 알림 분류 (info, warning, error, critical)

### 📅 과거 데이터 사용 시 GUI에서 명시적 표시
- 오래된 데이터 사용 시 명확한 경고 표시
- 데이터 나이 및 품질 정보 제공
- 사용자에게 데이터 상태 투명하게 공개

### 🔄 캐시 데이터 자동 갱신 및 품질 관리
- 백그라운드 모니터링 스레드
- 설정 가능한 모니터링 간격
- 품질 기준에 따른 자동 액션

## 🏗️ 시스템 구조

### 핵심 클래스

#### `CacheMonitor`
- 메인 캐시 모니터링 클래스
- 백그라운드 모니터링 스레드 관리
- 알림 시스템 통합

#### `CacheInfo`
- 개별 캐시 정보 데이터 클래스
- 상태, 품질, 신뢰도, 나이 정보 포함

#### `CacheAlert`
- 캐시 알림 데이터 클래스
- 알림 타입, 심각도, 자동 액션 정보

### 열거형 (Enums)

#### `CacheStatus`
- `FRESH`: 신선한 데이터 (5분 이내)
- `STALE`: 오래된 데이터 (5-15분)
- `EXPIRED`: 만료된 데이터 (15-60분)
- `MISSING`: 데이터 없음
- `CORRUPTED`: 손상된 데이터

#### `DataType`
- `KOSPI`: 코스피 지수
- `EXCHANGE_RATE`: 환율 (USD/KRW)
- `POSCO_STOCK`: POSCO 주가
- `NEWS_SENTIMENT`: 뉴스 감정 분석

## 🚀 사용법

### 기본 사용

```python
from cache_monitor import CacheMonitor

# 캐시 모니터 생성
monitor = CacheMonitor()

# 현재 캐시 상태 확인
status = monitor.check_cache_status()

# 요약 정보 조회
summary = monitor.get_cache_summary()

# 모니터링 시작
monitor.start_monitoring()
```

### GUI 통합

```python
from cache_monitor import CacheMonitor, create_gui_alert_handler

# GUI 알림 핸들러 생성
gui_handler = create_gui_alert_handler(parent_window)

# 캐시 모니터에 GUI 콜백 등록
monitor = CacheMonitor(gui_callback=gui_handler)

# 또는 별도로 콜백 추가
monitor.add_alert_callback(gui_handler)
```

### 커스텀 알림 처리

```python
def custom_alert_handler(alert):
    print(f"[{alert.severity}] {alert.data_type.value}: {alert.message}")
    
    if alert.auto_action == "refresh_data":
        # 데이터 갱신 로직 실행
        refresh_market_data()

monitor.add_alert_callback(custom_alert_handler)
```

## ⚙️ 설정

### 모니터링 설정

```python
monitor.update_config({
    'check_interval_seconds': 30,      # 확인 간격 (초)
    'fresh_threshold_minutes': 5,      # 신선 기준 (분)
    'stale_threshold_minutes': 15,     # 오래됨 기준 (분)
    'expired_threshold_minutes': 60,   # 만료 기준 (분)
    'min_quality_threshold': 0.7,      # 최소 품질 기준
    'min_confidence_threshold': 0.6,   # 최소 신뢰도 기준
    'auto_refresh_enabled': True,      # 자동 갱신 활성화
    'gui_alerts_enabled': True         # GUI 알림 활성화
})
```

## 📊 모니터링 지표

### 데이터 품질 평가 요소
1. **완성도**: 필수 필드 존재 여부
2. **신선도**: 데이터 생성 시간 기준
3. **소스 신뢰도**: 데이터 소스별 신뢰도
4. **합리성**: 데이터 값의 합리적 범위 검사

### 신뢰도 계산 요소
1. **변동성**: 급격한 변동 시 신뢰도 감소
2. **활동량**: 거래량/뉴스 수 기반
3. **시간대**: 시장 시간 고려

## 🔔 알림 시스템

### 알림 타입
- `status_change`: 상태 변화 알림
- `data_shortage`: 데이터 부족 알림
- `quality_degradation`: 품질 저하 알림
- `stale_data`: 과거 데이터 사용 알림

### 심각도 레벨
- `info`: 정보성 알림
- `warning`: 경고 알림
- `error`: 오류 알림
- `critical`: 치명적 알림

### 자동 액션
- `refresh_data`: 데이터 자동 갱신

## 📄 보고서 생성

```python
# 상태 보고서 생성
report_path = monitor.export_status_report()

# 보고서 내용
# - 생성 시간
# - 캐시 요약 정보
# - 상세 상태 정보
# - 최근 알림 히스토리
# - 모니터링 설정
```

## 🧪 테스트 및 검증

### 테스트 스크립트 실행

```bash
# 기본 기능 검증
python core/verify_cache_monitor.py

# 통합 테스트
python core/integration_test.py

# 데모 실행
python core/demo_cache_monitor.py

# 전체 테스트 (GUI 환경에서)
python core/test_cache_monitor.py
```

### 테스트 커버리지
- ✅ 캐시 상태 감지
- ✅ 알림 시스템
- ✅ 모니터링 루프
- ✅ GUI 통합
- ✅ 보고서 생성
- ✅ 설정 관리

## 📁 파일 구조

```
core/
├── cache_monitor.py              # 메인 캐시 모니터 클래스
├── test_cache_monitor.py         # 전체 테스트 스위트
├── verify_cache_monitor.py       # 기본 기능 검증
├── integration_test.py           # 통합 테스트
├── demo_cache_monitor.py         # 데모 스크립트
└── CACHE_MONITOR_README.md       # 이 문서
```

## 🔗 통합 포인트

### DynamicDataManager와의 통합
- 캐시 파일 공유 (`data/market_data_cache.json`)
- 품질 로그 공유 (`data/data_quality_log.json`)
- 데이터 구조 호환성

### GUI 시스템과의 통합
- tkinter messagebox를 통한 알림 표시
- 실시간 상태 업데이트
- 사용자 인터랙션 지원

### 로깅 시스템
- 구조화된 로그 기록
- 파일 및 콘솔 출력
- 디버깅 정보 제공

## 🎯 Requirements 5.3 구현 완료

✅ **kospi, exchange 데이터를 data/ 폴더에서 캐시 관리**
- 모든 시장 데이터 타입 지원
- JSON 기반 캐시 파일 관리
- 캐시 무결성 검사

✅ **데이터 부족 시 GUI 경고 알림 및 자동 전송**
- 실시간 데이터 부족 감지
- GUI messagebox 알림
- 자동 데이터 갱신 시도

✅ **과거 데이터 사용 시 GUI에서 명시적 표시**
- 데이터 나이 계산 및 표시
- 상태별 명확한 구분
- 사용자에게 투명한 정보 제공

✅ **완전 독립 실행 시스템**
- 외부 의존성 최소화
- 스탠드얼론 모듈 구조
- 이식성 보장

## 🚀 향후 확장 가능성

- 웹 대시보드 통합
- 메트릭 수집 및 분석
- 알림 채널 확장 (이메일, 슬랙 등)
- 머신러닝 기반 이상 감지
- 클러스터 환경 지원