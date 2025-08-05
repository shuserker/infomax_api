# 📋 POSCO 뉴스 알림 시스템 유지보수 메뉴얼

## 🎯 시스템 개요

POSCO 뉴스 알림 시스템은 5가지 BOT 타입으로 구성된 통합 알림 시스템입니다.

### 📊 5가지 BOT 타입
1. **🏭 POSCO 뉴스 비교알림 BOT** - 영업일 비교 분석
2. **📊 POSCO 뉴스 📊 BOT** - 일일 통합 분석 리포트
3. **🔔 POSCO 뉴스 🔔 BOT** - 데이터 갱신 상태 (동적 제목)
4. **✅ POSCO 뉴스 ✅ BOT** - 정시 발행 알림
5. **⏰ POSCO 뉴스 ⏰ BOT** - 지연 발행 알림

## 📁 핵심 파일 구조

```
Monitoring/Posco_News_mini/
├── 🚀POSCO_메인_알림_시작.bat          # 메인 시스템 시작
├── 🛑POSCO_메인_알림_중지.bat          # 메인 시스템 중지
├── 🎛️POSCO_메인_시스템.bat            # 통합 관리 센터
├── posco_main_notifier.py             # 메인 알림 시스템 (핵심)
├── historical_data_collector.py       # 과거 데이터 수집기
├── config.py                          # 설정 파일
├── requirements.txt                   # Python 의존성
├── main_notifier_state.json          # 시스템 상태 파일
├── main_notifier.log                  # 시스템 로그
└── docs/                              # 문서 폴더
```

## 🚀 시스템 시작/중지

### ✅ 시스템 시작
```bash
# Windows - 24시간 모니터링
🚀POSCO_메인_알림_시작.bat

# macOS/Linux - 24시간 모니터링
python3 posco_main_notifier.py

# 테스트 모드 (한 번만 실행)
python3 posco_main_notifier.py --test --test-type all
```

### 🧪 테스트 실행
```bash
# Windows - 대화형 테스트 (날짜/시간 입력 가능)
🧪POSCO_테스트_실행.bat

# 개별 테스트 (현재 시간 기준)
python3 posco_main_notifier.py --test --test-type business  # 영업일 비교
python3 posco_main_notifier.py --test --test-type delay     # 지연 발행
python3 posco_main_notifier.py --test --test-type report    # 통합 리포트
python3 posco_main_notifier.py --test --test-type timely    # 정시 발행
python3 posco_main_notifier.py --test --test-type status    # 갱신 상태

# 특정 날짜/시간 기준 테스트 (모든 메시지에 [TEST] 태그 추가)
python3 posco_main_notifier.py --test --test-type all --test-date 2025-07-30 --test-time 17:00
python3 posco_main_notifier.py --test --test-type business --test-date 2025-08-01 --test-time 09:30
```

### 🛑 시스템 중지
```bash
# Windows
🛑POSCO_메인_알림_중지.bat

# 또는 실행 중인 터미널에서 Ctrl+C
```

## ⚙️ 설정 관리

### 📝 config.py 주요 설정
```python
# Dooray 웹훅 URL
DOORAY_WEBHOOK_URL = "https://hook.dooray.com/services/..."

# API 설정
API_CONFIG = {
    "base_url": "https://apis.infomax.co.kr/apis/",
    "exchange-rate": "exchange-rate",
    "kospi-close": "kospi-close", 
    "newyork-market-watch": "newyork-market-watch"
}

# 알림 설정
NOTIFICATION_CONFIG = {
    "check_interval": 300,  # 5분 간격
    "quiet_hours": {
        "start": 18,  # 18시 이후 조용한 시간
        "end": 6      # 6시까지
    }
}
```

## 🔧 일상 유지보수

### 1️⃣ 시스템 상태 확인
```bash
# 로그 파일 확인
tail -f main_notifier.log

# 상태 파일 확인
cat main_notifier_state.json
```

### 2️⃣ 과거 데이터 캐시 갱신
```bash
# 과거 데이터 수집 (필요시)
python3 historical_data_collector.py
```

### 3️⃣ 시스템 재시작
```bash
# 1. 현재 시스템 중지 (Ctrl+C)
# 2. 시스템 재시작
🚀POSCO_메인_알림_시작.bat
```

## 🐛 문제 해결

### ❌ 알림이 전송되지 않는 경우
1. **웹훅 URL 확인**
   ```python
   # config.py에서 DOORAY_WEBHOOK_URL 확인
   ```

2. **네트워크 연결 확인**
   ```bash
   ping apis.infomax.co.kr
   ```

3. **로그 확인**
   ```bash
   tail -100 main_notifier.log | grep "ERROR"
   ```

### ❌ API 데이터를 가져오지 못하는 경우
1. **API 상태 확인**
   ```bash
   curl "https://apis.infomax.co.kr/apis/exchange-rate"
   ```

2. **캐시 파일 확인**
   ```bash
   ls -la ../../posco_news_*.json
   ```

### ❌ 시스템이 자주 중단되는 경우
1. **메모리 사용량 확인**
   ```bash
   # Windows
   tasklist | findstr python
   
   # macOS/Linux  
   ps aux | grep python
   ```

2. **로그에서 오류 패턴 확인**
   ```bash
   grep -i "error\|exception\|failed" main_notifier.log
   ```

## 📊 모니터링 대상

### 🔍 API 엔드포인트
- **서환마감**: `exchange-rate` (15:30 예상)
- **증시마감**: `kospi-close` (15:30 예상)  
- **뉴욕마켓워치**: `newyork-market-watch` (06:00 예상)

### 📅 알림 스케줄
- **06:00**: 아침 현재 상태 체크
- **06:10**: 영업일 비교 분석
- **18:00**: 저녁 일일 요약 리포트
- **18:10**: 저녁 상세 일일 요약
- **18:20**: 저녁 고급 분석

## 🔄 업데이트 절차

### 1️⃣ 코드 업데이트
```bash
# Git에서 최신 코드 가져오기
git pull origin main

# 의존성 업데이트
pip install -r requirements.txt
```

### 2️⃣ 설정 백업
```bash
# 중요 파일 백업
cp config.py config.py.backup
cp main_notifier_state.json main_notifier_state.json.backup
```

### 3️⃣ 시스템 재시작
```bash
# 기존 시스템 중지 후 새 버전으로 시작
🚀POSCO_메인_알림_시작.bat
```

## 📞 긴급 상황 대응

### 🚨 시스템 완전 중단
1. **모든 Python 프로세스 종료**
   ```bash
   # Windows
   taskkill /f /im python.exe
   
   # macOS/Linux
   pkill -f python
   ```

2. **상태 파일 초기화**
   ```bash
   rm main_notifier_state.json
   ```

3. **시스템 재시작**
   ```bash
   🚀POSCO_메인_알림_시작.bat
   ```

### 🚨 알림 폭주 상황
1. **즉시 시스템 중지** (Ctrl+C)
2. **로그 확인으로 원인 파악**
3. **설정 조정 후 재시작**

## 📈 성능 최적화

### 💾 캐시 관리
- **캐시 파일 위치**: `../../posco_news_*.json`
- **캐시 갱신 주기**: 필요시 수동 실행
- **캐시 크기 모니터링**: 정기적으로 파일 크기 확인

### 🔄 메모리 관리
- **정기 재시작**: 주 1회 권장
- **로그 파일 정리**: 월 1회 권장
- **상태 파일 백업**: 일 1회 권장

## 📋 체크리스트

### 🌅 일일 점검
- [ ] 시스템 실행 상태 확인
- [ ] 최근 알림 전송 확인
- [ ] 로그 파일 오류 확인

### 📅 주간 점검  
- [ ] 시스템 재시작
- [ ] 로그 파일 정리
- [ ] 캐시 파일 상태 확인

### 📆 월간 점검
- [ ] 설정 파일 백업
- [ ] 시스템 업데이트 확인
- [ ] 성능 지표 검토

---

## 📞 지원 연락처

**시스템 관리자**: [담당자 정보]
**긴급 연락처**: [긴급 연락처]
**문서 업데이트**: 2025-08-05

---

> 💡 **팁**: 이 메뉴얼은 시스템 변경사항에 따라 정기적으로 업데이트됩니다.