# 📰 POSCO 뉴스 모니터링 시스템


## 버전 정보

- **WatchHamster**: v3.0
- **POSCO News**: 250808
- **최종 업데이트**: 2025-08-08
## 🚀 주요 기능

- **실시간 모니터링**: 뉴스 데이터 변경사항 자동 감지
- **Dooray 알림**: 변경사항을 Dooray 웹훅으로 즉시 전송
- **상태 표시**: 🟢(모든 데이터 최신) / 🟡(일부 최신) / 🔴(모든 과거)
- **영업일 비교**: 현재 vs 직전 영업일 데이터 상세 비교
- **캐시 시스템**: 효율적인 변경사항 감지

## 📁 프로젝트 구조

```
📁 Monitoring/POSCO News/
├── posco_news_monitor.py    # 핵심 모니터링 로직
├── run_monitor.py           # 실행 스크립트
├── config.py               # 설정 파일 (통합 관리)
├── 사용메뉴얼.md            # 상세 사용법
└── posco_news_cache.json   # 데이터 캐시 (자동 생성)
```

## ⚙️ 설정

`config.py`에서 모든 설정을 관리합니다:

- **API_CONFIG**: API 연결 정보
- **DOORAY_WEBHOOK_URL**: Dooray 웹훅 URL
- **MONITORING_CONFIG**: 모니터링 간격, 재시도 횟수 등
- **STATUS_CONFIG**: 상태 표시 방식 및 색상
- **NEWS_TYPES**: 뉴스 타입별 표시명 및 이모지

## 🎯 사용법

### 1. 📊 현재 상태 체크 (기본값)
```bash
python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py 1
# 또는 그냥
python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py
```

### 2. 📈 영업일 비교 체크
```bash
python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py 2
```

### 3. 🧠 스마트 모니터링 ⭐ 추천
```bash
python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py 3
```
**뉴스 발행 패턴 기반 적응형 간격**
- 집중시간: 06:00-08:00, 15:00-17:00 (20분 간격)
- 일반시간: 07:00-18:00 (2시간 간격)
- 야간 조용한 모드: 18:00-07:00 (변경사항 있을 때만 알림)
- 특별이벤트: 08:00 전일비교, 18:00 일일요약

### 4. 🔄 기본 모니터링 (60분 간격)
```bash
python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py 4
```

### 5. 📋 일일 요약 리포트
```bash
python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py 5
```

### 6. 🧪 테스트 알림
```bash
python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py 6
```

## 📊 상태 표시 시스템

### 엄격한 기준 (기본값)
- 🟢 **모든 최신**: 3개 뉴스 타입 모두 오늘 날짜
- 🟡 **일부 최신**: 일부만 오늘 날짜, 나머지는 과거
- 🔴 **모든 과거**: 모든 뉴스 타입이 과거 날짜

### 알림 예시
- `POSCO 뉴스 🟢3/3`: 모든 데이터가 최신
- `POSCO 뉴스 🟡1/3`: 3개 중 1개만 최신
- `POSCO 뉴스 🔴3개 과거`: 모든 데이터가 과거

## 🔧 최적화 완료 사항

### ✅ Phase 1: 상태표시 통일
- 모든 알림에서 동일한 엄격한 기준 적용
- 일관된 색상 표시로 사용자 혼란 방지

### ✅ Phase 2: 설정 통합
- `config.py`에 모든 설정 집중 관리
- 하드코딩된 값들 제거

### ✅ Phase 3: 코드 중복 제거
- 상태 계산 로직 통합 (`_get_status_info()`)
- 뉴스 타입 처리 통합 (NEWS_TYPES 활용)

### ✅ Phase 4: 유틸리티 함수 분리
- 공통 기능들을 재사용 가능한 메서드로 분리
- 코드 가독성 및 유지보수성 향상

## 📱 지원하는 뉴스 타입

1. **EXCHANGE RATE**: 환율 뉴스
2. **NEWYORK MARKET WATCH**: 뉴욕시장 뉴스
3. **KOSPI CLOSE**: 코스피 뉴스

## 🛠️ 요구사항

- Python 3.7+
- requests 라이브러리
- Dooray 웹훅 URL

## 📞 문제 해결

1. **웹훅 테스트**: `python Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py 4`
2. **캐시 초기화**: `posco_news_cache.json` 파일 삭제
3. **설정 확인**: `config.py` 파일의 URL 및 인증 정보 확인

---

**🎉 최적화된 POSCO 뉴스 모니터링 시스템으로 효율적인 뉴스 추적을 경험하세요!**