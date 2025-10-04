# WatchHamster 웹훅 로직 완전 재이식

## 📋 프로젝트 개요

**목표**: 기존 WatchHamster_Project의 실제 작동하는 웹훅 발송 로직을 분석하고 새 GUI 프로젝트에 완전히 재이식

**배경**: 
- 현재 새 GUI 프로젝트에서 웹훅이 전혀 발송되지 않음
- 기존 WatchHamster_Project에는 실제로 작동하는 웹훅 로직이 존재
- 해당 로직을 면밀히 분석하여 동일하게 재구현 필요

**소스 프로젝트**: `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/WatchHamster_Project`

---

## 🔍 Phase 1: 기존 로직 완전 분석

### 1.1 핵심 파일 분석
- [ ] `Posco_News_Mini_Final/core/webhook_sender.py` - 웹훅 발송 엔진
- [ ] `Posco_News_Mini_Final/scripts/posco_main_notifier.py` - 메인 알림 시스템
- [ ] `Posco_News_Mini_Final/core/news_message_generator.py` - 메시지 생성기
- [ ] `core/watchhamster_monitor.py` - 모니터링 로직

### 1.2 분석 항목
- **웹훅 URL 관리**
  - 하드코딩된 URL 위치
  - 환경 변수 사용 여부
  - URL 검증 로직

- **메시지 페이로드 구조**
  - botName, botIconImage 설정
  - text, attachments 포맷
  - color 코드 사용

- **발송 조건 및 타이밍**
  - 언제 웹훅을 발송하는가?
  - 중복 발송 방지 로직
  - 재시도 메커니즘

- **에러 처리**
  - 타임아웃 처리
  - 연결 오류 처리
  - 로그 기록 방식

---

## 🏗️ Phase 2: 로직 재이식

### 2.1 WebhookSender 클래스 이식
```python
# python-backend/core/webhook_sender.py
class WebhookSender:
    """기존 로직 그대로 이식"""
    - __init__() - 초기화
    - send_message() - 메시지 발송
    - _build_payload() - 페이로드 구성
    - _handle_retry() - 재시도 처리
```

### 2.2 메시지 생성 로직 이식
```python
# python-backend/core/message_generator.py
- generate_news_message() - 뉴스 메시지 생성
- generate_report_message() - 리포트 메시지 생성
- generate_status_message() - 상태 메시지 생성
```

### 2.3 API 통합
```python
# python-backend/api/webhooks.py
- POST /api/webhooks/send - 웹훅 발송
- POST /api/webhooks/test - 테스트 발송
- GET /api/webhooks/history - 발송 이력
```

---

## 📊 Phase 3: 검증 및 테스트

### 3.1 단위 테스트
- [ ] WebhookSender 클래스 테스트
- [ ] 메시지 생성 테스트
- [ ] 페이로드 포맷 검증

### 3.2 통합 테스트
- [ ] 실제 Dooray 웹훅 발송 테스트
- [ ] 에러 시나리오 테스트
- [ ] 재시도 로직 테스트

### 3.3 검증 항목
- [ ] 기존 프로젝트와 동일한 메시지 포맷
- [ ] 동일한 botName, botIconImage
- [ ] 동일한 color 코드
- [ ] 동일한 타임아웃 설정

---

## 🎯 Phase 4: GUI 통합

### 4.1 설정 페이지 연동
- [ ] 웹훅 URL 설정 저장
- [ ] 테스트 발송 버튼 연동
- [ ] 발송 이력 표시

### 4.2 모니터 실행 로그 연동
- [ ] 실제 웹훅 발송 시 로그 기록
- [ ] Input/Output 데이터 저장
- [ ] 성공/실패 상태 표시

---

## 📝 분석 결과

### 복사된 핵심 파일
```
python-backend/core/posco_original/
├── webhook_sender.py (34KB) - 웹훅 발송 엔진
├── news_message_generator.py (59KB) - 메시지 생성 로직
├── integrated_api_module.py (18KB) - API 연동 모듈
├── environment_setup.py (7KB) - 환경 설정
└── __init__.py
```

### 메시지 생성 로직 (5가지 타입)
1. **영업일 비교 분석** - `generate_business_day_comparison_message()`
   - 전일 대비 뉴스 발행 시간 비교
   - 트리 구조 메시지 (├, └)
   
2. **지연 발행 알림** - `generate_delay_notification_message()`
   - 예상 발행 시간 대비 지연 감지
   - 지연 시간 계산 및 알림

3. **일일 통합 리포트** - `generate_daily_integrated_report_message()`
   - 3개 뉴스 타입 종합 리포트
   - 발행 현황 및 통계

4. **정시 발행 알림** - `generate_status_notification_message()`
   - 정시 발행 확인 메시지
   - 뉴스 타입별 상태 표시

5. **데이터 갱신 없음** - `generate_no_data_notification_message()`
   - API 응답 없음 알림
   - 마지막 업데이트 시간 표시

### 발견된 웹훅 URL
```
NEWS_MAIN: https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg
WATCHHAMSTER: https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ
```

### 메시지 포맷
```python
payload = {
    "botName": "POSCO 뉴스 📊",
    "botIconImage": "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg",
    "text": "제목",
    "attachments": [{
        "color": "#28a745",
        "text": "내용"
    }]
}
```

### 발송 조건
- 뉴스 변경 감지 시
- 일일 리포트 (18:00)
- 영업일 비교 (06:10)
- 정시 상태 확인 (매시간 정각)

---

## 🚀 실행 계획

### Step 1: 기존 로직 완전 분석 (30분)
- webhook_sender.py 전체 코드 리뷰
- posco_main_notifier.py 메시지 생성 로직 분석
- 실제 작동 흐름 파악

### Step 2: 핵심 로직 추출 (1시간)
- WebhookSender 클래스 복사
- 의존성 제거 및 단순화
- 새 프로젝트 구조에 맞게 조정

### Step 3: API 통합 (30분)
- 웹훅 발송 API 구현
- 테스트 엔드포인트 구현
- 에러 처리 추가

### Step 4: 테스트 및 검증 (30분)
- 실제 Dooray 발송 테스트
- 기존 프로젝트와 메시지 포맷 비교
- 모든 시나리오 검증

---

## ✅ 성공 기준

1. **웹훅 테스트 발송** 버튼 클릭 시 Dooray에 메시지 도착
2. **메시지 포맷**이 기존 프로젝트와 100% 동일
3. **에러 처리** 및 재시도 로직 정상 작동
4. **발송 이력** 로그에 정확히 기록

---

## 🎯 다음 단계

**즉시 시작**: Phase 1 - 기존 로직 완전 분석

준비되었습니다. 시작하겠습니다!
