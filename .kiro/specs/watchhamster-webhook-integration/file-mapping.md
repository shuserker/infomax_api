# 웹훅 시스템 통합 파일 매핑

## 📁 파일 복사 매핑표

### Core 모듈 파일

| # | 원본 파일 | 대상 파일 | 크기 | 상태 |
|---|----------|----------|------|------|
| 1 | `/Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/webhook_sender.py` | `/Monitoring/WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/core/posco_original/webhook_sender.py` | 34,427 bytes | ✅ 이미 존재 |
| 2 | `/Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/news_message_generator.py` | `/Monitoring/WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/core/posco_original/news_message_generator.py` | 59,170 bytes | ⚠️ 확인 필요 |
| 3 | `/Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/integrated_api_module.py` | `/Monitoring/WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/core/posco_original/integrated_api_module.py` | 18,525 bytes | ⚠️ 확인 필요 |
| 4 | `/Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/environment_setup.py` | `/Monitoring/WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/core/posco_original/environment_setup.py` | 7,617 bytes | ⚠️ 확인 필요 |

### 의존성 파일 (확인 필요)

| # | 파일명 | 위치 확인 | 비고 |
|---|--------|----------|------|
| 1 | `integrated_news_parser.py` | 🔍 확인 필요 | `news_message_generator.py`에서 import |
| 2 | `news_data_parser.py` | 🔍 확인 필요 | `news_message_generator.py`에서 import |
| 3 | `ai_analysis_engine.py` | 🔍 확인 필요 | `webhook_sender.py`에서 import |

---

## 🔧 수정 필요 파일

### API 엔드포인트

| 파일 | 경로 | 수정 내용 | 우선순위 |
|------|------|----------|----------|
| `webhook_manager.py` | `/python-backend/api/` | 더미 데이터 제거, 실제 로직 연결 | 🔴 HIGH |
| `webhooks.py` | `/python-backend/api/` | 템플릿 시스템 개선 | 🟡 MEDIUM |

### 데이터베이스

| 파일 | 경로 | 수정 내용 | 우선순위 |
|------|------|----------|----------|
| `database/__init__.py` | `/python-backend/database/` | 웹훅 로그 CRUD 구현 | 🔴 HIGH |

---

## 📋 Import 경로 수정 가이드

### `news_message_generator.py` Import 수정

**원본 (WatchHamster_Project)**:
```python
try:
    from ...core.integrated_news_parser import IntegratedNewsParser, IntegratedNewsData
    from ...core.news_data_parser import NewsItem, NewsStatus
except ImportError:
    # fallback
```

**수정 후 (WatchHamster_Project_GUI_Tauri_WindSurf_So4.5)**:
```python
try:
    # 같은 posco_original 디렉토리 내에서 import
    from .integrated_news_parser import IntegratedNewsParser, IntegratedNewsData
    from .news_data_parser import NewsItem, NewsStatus
except ImportError:
    # 상위 core 디렉토리에서 import
    from ..integrated_news_parser import IntegratedNewsParser, IntegratedNewsData
    from ..news_data_parser import NewsItem, NewsStatus
```

### `webhook_sender.py` Import 수정

**원본**:
```python
try:
    from .news_message_generator import NewsMessageGenerator, MessageGenerationResult
    from ...core.ai_analysis_engine import AIAnalysisEngine
except ImportError:
    # fallback
```

**수정 후**:
```python
try:
    # 같은 디렉토리에서 import
    from .news_message_generator import NewsMessageGenerator, MessageGenerationResult
    # 상위 core 디렉토리에서 import
    from ..ai_analysis_engine import AIAnalysisEngine
except ImportError:
    # fallback
```

---

## 🔗 API 엔드포인트 연결 매핑

### webhook_manager.py 엔드포인트

| 엔드포인트 | 메서드 | 연결할 함수 | 상태 |
|-----------|--------|------------|------|
| `/send/test` | POST | `WebhookSender.send_test_message()` | ✅ 구현됨 |
| `/send/business-day-comparison` | POST | `WebhookSender.send_business_day_comparison()` | ❌ 미구현 |
| `/send/delay-notification` | POST | `WebhookSender.send_delay_notification()` | ❌ 미구현 |
| `/send/daily-report` | POST | `WebhookSender.send_daily_integrated_report()` | ❌ 미구현 |
| `/send/status-notification` | POST | `WebhookSender.send_status_notification()` | ❌ 미구현 |
| `/send/no-data-notification` | POST | `WebhookSender.send_no_data_notification()` | ❌ 미구현 |
| `/send/watchhamster-error` | POST | `WebhookSender.send_watchhamster_error()` | ❌ 미구현 |
| `/send/watchhamster-status` | POST | `WebhookSender.send_watchhamster_status()` | ❌ 미구현 |
| `/stats` | GET | `WebhookSender.get_send_statistics()` | ⚠️ 부분 구현 |
| `/queue-status` | GET | `WebhookSender.get_queue_status()` | ✅ 구현됨 |
| `/logs` | GET | DB 조회 | ⚠️ 더미 데이터 |
| `/logs/{log_id}` | GET | DB 조회 | ⚠️ 더미 데이터 |
| `/message-types` | GET | 정적 데이터 | ✅ 구현됨 |
| `/message-types/{id}/detail` | GET | `NewsMessageGenerator` 사용 | ⚠️ 부분 구현 |

---

## 🗄️ 데이터베이스 스키마

### webhook_logs 테이블 (필요한 컬럼)

```sql
CREATE TABLE webhook_logs (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_type TEXT NOT NULL,
    bot_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    status TEXT NOT NULL,  -- success, failed, pending
    message_id TEXT,
    full_message TEXT,
    error_message TEXT,
    metadata JSON
);
```

### webhook_stats 테이블 (집계용)

```sql
CREATE TABLE webhook_stats (
    company_id TEXT PRIMARY KEY,
    total_sent INTEGER DEFAULT 0,
    successful_sends INTEGER DEFAULT 0,
    failed_sends INTEGER DEFAULT 0,
    retry_attempts INTEGER DEFAULT 0,
    average_response_time REAL DEFAULT 0.0,
    last_send_time DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 메시지 타입별 템플릿 매핑

| 메시지 타입 | 생성 함수 | BOT 이름 | 색상 | 우선순위 |
|------------|----------|---------|------|---------|
| test | `send_test_message()` | `[TEST] POSCO 시스템` | `#6c757d` | LOW |
| business_day_comparison | `generate_business_day_comparison_message()` | `POSCO 뉴스 비교알림` | `#007bff` | NORMAL |
| delay_notification | `generate_delay_notification_message()` | `POSCO 뉴스 ⏰` | `#ffc107` | HIGH |
| daily_report | `generate_daily_integrated_report_message()` | `POSCO 뉴스 📊` | `#28a745` | NORMAL |
| status_notification | `generate_status_notification_message()` | `POSCO 뉴스 ✅` | `#17a2b8` | NORMAL |
| no_data_notification | `generate_no_data_notification_message()` | `POSCO 뉴스 🔔` | `#6c757d` | LOW |
| watchhamster_error | `send_watchhamster_error()` | `POSCO 워치햄스터 🚨` | `#dc3545` | CRITICAL |
| watchhamster_status | `send_watchhamster_status()` | `POSCO 워치햄스터 🎯🛡️` | `#28a745` | NORMAL |

---

## 🔐 환경 변수 매핑

### 웹훅 URL

```bash
# .env 파일
DOORAY_WEBHOOK_NEWS_MAIN=https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg
DOORAY_WEBHOOK_WATCHHAMSTER=https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ
DOORAY_WEBHOOK_TEST=https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg
```

### BOT 프로필 이미지

```bash
POSCO_BOT_ICON_URL=https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg
```

---

## 📝 작업 순서

1. ✅ **파일 존재 확인**
   - [ ] `news_message_generator.py` 확인
   - [ ] `integrated_api_module.py` 확인
   - [ ] `environment_setup.py` 확인
   - [ ] 의존성 파일 확인

2. ✅ **파일 복사**
   - [ ] 누락된 파일 복사
   - [ ] Import 경로 수정
   - [ ] 테스트 실행

3. ✅ **API 연결**
   - [ ] `webhook_manager.py` 수정
   - [ ] 각 엔드포인트 구현
   - [ ] 에러 처리 추가

4. ✅ **데이터베이스 통합**
   - [ ] 스키마 확인/생성
   - [ ] CRUD 함수 구현
   - [ ] 통계 집계 구현

5. ✅ **테스트**
   - [ ] 단위 테스트
   - [ ] 통합 테스트
   - [ ] UI 연동 테스트

---

**작성일**: 2025-10-04  
**작성자**: Cascade AI
