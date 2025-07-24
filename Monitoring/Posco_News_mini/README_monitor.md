# 📰 POSCO 뉴스 모니터

POSCO 뉴스 API 데이터 변경을 감지하고 Dooray 웹훅으로 알림을 보내는 시스템입니다.

## 🚀 설정 방법

### 1. Dooray 웹훅 설정
1. Dooray에 로그인
2. 프로젝트 > 설정 > 서비스 연동 > Incoming Webhook
3. 새 웹훅 생성 후 URL 복사
4. `config.py` 파일에서 `DOORAY_WEBHOOK_URL` 수정

### 2. 실행
```bash
python run_monitor.py
```

## 📋 기능

### ✅ 데이터 변경 감지
- 뉴스 제목, 내용, 날짜 변경 감지
- 새로운 뉴스 타입 추가 감지
- MD5 해시를 이용한 정확한 변경 감지

### 📤 Dooray 알림
- 변경사항 상세 정보
- 뉴스 요약 (제목, 날짜, 작성자, 카테고리)
- 오류 발생시 알림
- 시작/중단 알림

### 💾 캐시 시스템
- 이전 데이터 캐시 저장
- 불필요한 API 호출 방지
- 변경사항 비교 분석

## 🔧 설정 옵션

`config.py`에서 다음 설정을 변경할 수 있습니다:

- `check_interval_minutes`: 체크 간격 (기본: 5분)
- `enable_startup_notification`: 시작 알림 여부
- `enable_error_notification`: 오류 알림 여부

## 📱 실행 모드

### 1. 한 번만 체크
현재 데이터를 한 번 체크하고 변경사항이 있으면 알림

### 2. 지속적 모니터링
설정된 간격으로 계속 모니터링 (Ctrl+C로 중단)

### 3. 테스트 알림
Dooray 웹훅 설정이 정상인지 테스트

## 📊 알림 예시

```
🔔 POSCO 뉴스 알림

변경사항:
exchange-rate 내용 업데이트
newyork-market-watch 제목 변경

📰 POSCO 뉴스 업데이트

🔹 EXCHANGE-RATE
   제목: [서환-마감] 무역 긴장 완화로 하락…8.00원↓
   날짜: 20250723 164406
   작성자: 신윤우
   카테고리: 외환, 금융, 경제

⏰ 업데이트 시간: 2025-01-24 10:30:15
```

## 🛠️ 파일 구조

- `posco_news_monitor.py`: 메인 모니터링 클래스
- `run_monitor.py`: 실행 스크립트
- `config.py`: 설정 파일
- `posco_news_cache.json`: 캐시 파일 (자동 생성)

## ⚠️ 주의사항

- Dooray 웹훅 URL을 반드시 설정해야 합니다
- 네트워크 연결이 필요합니다
- API 호출 제한이 있을 수 있습니다