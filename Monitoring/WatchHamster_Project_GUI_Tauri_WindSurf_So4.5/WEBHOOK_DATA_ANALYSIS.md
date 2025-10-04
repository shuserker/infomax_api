# 🔍 웹훅 시스템 데이터 분석 및 더미값 제거 작업

## 📋 작업 개요

**목표**: 모든 더미값 제거 및 실제 데이터 연결
**대상**: 웹훅 관리 시스템 전체
**기준**: WatchHamster_Project 원본 로직

---

## 1️⃣ 원본 프로젝트 분석

### 📁 핵심 파일
```
WatchHamster_Project/Posco_News_Mini_Final/core/
├── webhook_sender.py          # 웹훅 발송 로직
├── news_message_generator.py  # 메시지 생성 로직
└── integrated_api_module.py   # API 통합 모듈
```

### 🎯 메시지 타입 (원본)

#### 1. **영업일 비교 분석** (business_day_comparison)
```python
def generate_business_day_comparison_message(raw_data, historical_data)
```
- **BOT**: NEWS_COMPARISON
- **우선순위**: NORMAL
- **채널**: NEWS_MAIN
- **내용**: 전일 대비 뉴스 발행 시간 비교
- **포맷**: 트리 구조 (├, └)

#### 2. **지연 발행 알림** (delay_notification)
```python
def generate_delay_notification_message(news_type, current_data, delay_minutes)
```
- **BOT**: NEWS_DELAY
- **우선순위**: HIGH
- **채널**: NEWS_MAIN
- **내용**: 예상 시간 대비 지연 감지
- **트리거**: delay_minutes > 임계값

#### 3. **일일 통합 리포트** (daily_report)
```python
def generate_daily_integrated_report_message(raw_data, report_url)
```
- **BOT**: NEWS_REPORT
- **우선순위**: NORMAL
- **채널**: NEWS_MAIN
- **내용**: 3개 뉴스 타입 종합 분석
- **포맷**: 상세 통계 + 링크

#### 4. **정시 발행 알림** (status_notification)
```python
def generate_status_notification_message(raw_data)
```
- **BOT**: NEWS_STATUS
- **우선순위**: NORMAL
- **채널**: NEWS_MAIN
- **내용**: 정시 발행 확인
- **포맷**: 간단한 상태 메시지

#### 5. **데이터 갱신 없음** (no_data_notification)
```python
def generate_no_data_notification_message(raw_data)
```
- **BOT**: NEWS_NO_DATA
- **우선순위**: LOW
- **채널**: NEWS_MAIN
- **내용**: API 응답 없음
- **트리거**: API 실패 또는 빈 응답

#### 6. **워치햄스터 오류** (watchhamster_error)
```python
# WebhookSender 내부
```
- **BOT**: WATCHHAMSTER_ERROR
- **우선순위**: CRITICAL
- **채널**: WATCHHAMSTER
- **내용**: 시스템 오류 알림

#### 7. **워치햄스터 상태** (watchhamster_status)
```python
# WebhookSender 내부
```
- **BOT**: WATCHHAMSTER_STATUS
- **우선순위**: NORMAL
- **채널**: WATCHHAMSTER
- **내용**: 시스템 상태 보고

#### 8. **테스트 메시지** (test)
```python
# WebhookSender 내부
```
- **BOT**: TEST
- **우선순위**: LOW
- **채널**: NEWS_MAIN
- **내용**: 시스템 테스트

---

## 2️⃣ 현재 시스템 분석

### 📁 현재 구조
```
python-backend/api/
├── webhook_manager.py         # 웹훅 관리 API
└── core/
    ├── posco_original/
    │   ├── webhook_sender.py
    │   └── news_message_generator.py
    └── watchhamster_original/
```

### ⚠️ 발견된 더미값

#### A. API 응답 (webhook_manager.py)
```python
# ❌ 더미값
message_types = [
    {
        "id": "test",
        "name": "테스트 메시지",
        "template": "# 하드코딩된 템플릿"  # ← 더미!
    }
]

# ✅ 실제 값 (필요)
- 원본 news_message_generator.py에서 가져오기
- 실제 템플릿 동적 생성
```

#### B. 템플릿 데이터
```python
# ❌ 현재: 하드코딩된 마크다운
template = """# 테스트 메시지
**봇 타입**: TEST
...
"""

# ✅ 필요: 실제 메시지 생성기에서 가져오기
generator = NewsMessageGenerator()
result = generator.generate_business_day_comparison_message(data)
template = result.message  # 실제 생성된 메시지
```

#### C. 최근 로그
```python
# ❌ 현재: None 또는 더미
recent_log = None

# ✅ 필요: 실제 데이터베이스에서 조회
db = get_db()
logs = db.get_webhook_logs(company_id, limit=10)
recent_log = logs[0] if logs else None
```

#### D. Input/Output 예시
```python
# ❌ 현재: 정적 예시
input_example = {"bot_type": "TEST", ...}

# ✅ 필요: 실제 발송 데이터 기반
- 마지막 발송 시 사용된 실제 Input
- 마지막 발송 시 받은 실제 Output
```

---

## 3️⃣ 수정 계획

### Phase 1: 메시지 생성기 통합 ✅
```python
# webhook_manager.py에 추가
from core.posco_original.news_message_generator import NewsMessageGenerator

generator = NewsMessageGenerator()
```

### Phase 2: 실제 템플릿 가져오기
```python
# 각 메시지 타입별 실제 생성
result = generator.generate_business_day_comparison_message(sample_data)
template = result.message  # 실제 마크다운
```

### Phase 3: 데이터베이스 로그 연결
```python
# 실제 발송 로그 조회
db = get_db()
logs = db.get_webhook_logs(company_id, message_type=message_type_id)
recent_log = logs[0] if logs else None
```

### Phase 4: Input/Output 실제 데이터
```python
# 마지막 발송 시 사용된 실제 데이터
if recent_log:
    input_example = recent_log.get('request_data')
    output_example = recent_log.get('response_data')
```

---

## 4️⃣ 더미값 목록

### 🔴 제거 대상

#### webhook_manager.py
```python
Line 528-546: ❌ 하드코딩된 템플릿
Line 555-572: ❌ 하드코딩된 템플릿
Line 581-598: ❌ 하드코딩된 템플릿
Line 611-619: ❌ 정적 Input 예시
Line 621-627: ❌ 정적 Output 예시
```

#### WebhookManager.tsx (프론트엔드)
```typescript
# 이미 API 연결로 수정됨 ✅
- messageDetail?.template (API에서 가져옴)
- messageDetail?.recent_log (API에서 가져옴)
- messageDetail?.input_example (API에서 가져옴)
- messageDetail?.output_example (API에서 가져옴)
```

---

## 5️⃣ 작업 순서

### Step 1: 원본 로직 복사 ✅
```bash
✅ webhook_sender.py 확인
✅ news_message_generator.py 확인
```

### Step 2: 메시지 생성기 통합
```python
# webhook_manager.py에 실제 생성 로직 추가
```

### Step 3: 템플릿 동적 생성
```python
# 각 메시지 타입별 실제 템플릿 생성
```

### Step 4: 로그 데이터 연결
```python
# 데이터베이스에서 실제 로그 조회
```

### Step 5: 테스트 & 검증
```bash
# API 테스트
# 프론트엔드 확인
```

---

## 6️⃣ 다음 작업

### 즉시 수행
1. news_message_generator.py 복사 확인
2. webhook_manager.py에 실제 생성 로직 통합
3. 템플릿 동적 생성 구현
4. 로그 데이터 연결

### 검증 필요
- 각 메시지 타입별 실제 생성 테스트
- 데이터베이스 로그 조회 확인
- Input/Output 실제 데이터 확인

---

## 📊 현재 상태

```
✅ 원본 프로젝트 위치 확인
✅ 핵심 파일 식별
✅ 메시지 타입 8개 확인
✅ 더미값 위치 파악
⏳ 실제 로직 통합 (진행 중)
```

**다음: 실제 메시지 생성 로직 통합** 🚀
