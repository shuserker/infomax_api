# 🏢 멀티 테넌트 구조 재구성 계획

## 📊 현재 구조 분석

### 문제점
```
❌ POSCO 전용으로 하드코딩됨
   - 웹훅 URL이 POSCO Dooray로 고정
   - 메시지 템플릿에 "POSCO" 하드코딩
   - API 엔드포인트가 /api/posco 전용
   - 서비스 관리가 POSCO 시스템만 지원
   - 설정이 단일 회사 전용

❌ 확장성 부족
   - 새 회사 추가 시 코드 전체 수정 필요
   - 회사별 설정 분리 불가
   - 회사별 로그 분리 불가
```

### 현재 메뉴 구조
```
├── 대시보드 (전체 시스템)
├── 서비스 관리 (POSCO 전용)
├── API 설정 (POSCO API)
├── 웹훅 관리 (POSCO 웹훅)
├── 로그 뷰어 (전체 로그)
└── 설정 (시스템 설정)
```

---

## 🎯 목표 구조

### 멀티 테넌트 아키텍처
```
WatchHamster Platform
├── 회사별 독립 운영
├── 공통 인프라 공유
├── 회사별 설정 분리
└── 통합 대시보드
```

---

## 📋 재구성 계획

### Phase 1: 백엔드 구조 개편 (우선순위: 높음)

#### 1.1 데이터베이스 스키마 설계
```sql
-- 회사 테이블
CREATE TABLE companies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    logo_url VARCHAR(500),
    webhook_url VARCHAR(500),
    api_config JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 웹훅 설정 테이블
CREATE TABLE webhook_configs (
    id VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(id),
    channel_name VARCHAR(100),
    webhook_url VARCHAR(500),
    bot_name VARCHAR(100),
    bot_icon VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE
);

-- 메시지 로그 테이블
CREATE TABLE webhook_logs (
    id VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(id),
    message_type VARCHAR(50),
    bot_type VARCHAR(50),
    priority VARCHAR(20),
    endpoint VARCHAR(50),
    status VARCHAR(20),
    message_id VARCHAR(100),
    full_message TEXT,
    metadata JSON,
    error_message TEXT,
    timestamp TIMESTAMP
);

-- API 설정 테이블
CREATE TABLE api_configs (
    id VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(id),
    api_name VARCHAR(100),
    api_url VARCHAR(500),
    api_token VARCHAR(500),
    config JSON,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 1.2 백엔드 디렉토리 구조 개편
```
python-backend/
├── api/
│   ├── companies.py           # 회사 관리 API (NEW)
│   ├── webhooks.py            # 웹훅 관리 (회사별)
│   ├── services.py            # 서비스 관리 (회사별)
│   ├── news.py                # 뉴스 관리 (회사별)
│   └── ...
│
├── core/
│   ├── companies/             # 회사별 로직 (NEW)
│   │   ├── base/              # 공통 베이스 클래스
│   │   │   ├── base_webhook_sender.py
│   │   │   ├── base_message_generator.py
│   │   │   └── base_monitor.py
│   │   │
│   │   ├── posco/             # POSCO 전용
│   │   │   ├── posco_webhook_sender.py
│   │   │   ├── posco_message_generator.py
│   │   │   ├── posco_monitor.py
│   │   │   └── posco_config.py
│   │   │
│   │   └── company_factory.py # 회사별 인스턴스 생성
│   │
│   ├── watchhamster_original/ # 기존 WatchHamster (공통)
│   └── ...
│
├── models/
│   ├── company.py             # 회사 모델 (NEW)
│   ├── webhook_config.py      # 웹훅 설정 모델 (NEW)
│   └── ...
│
└── database/
    ├── db.py                  # 데이터베이스 연결 (NEW)
    ├── migrations/            # 마이그레이션 (NEW)
    └── repositories/          # 리포지토리 패턴 (NEW)
        ├── company_repository.py
        └── webhook_repository.py
```

#### 1.3 API 엔드포인트 재구성
```
기존:
  POST /api/webhook-manager/send/test
  POST /api/posco/...

신규:
  POST /api/companies                           # 회사 등록
  GET  /api/companies                           # 회사 목록
  GET  /api/companies/{company_id}              # 회사 상세
  
  POST /api/companies/{company_id}/webhooks/send/test
  POST /api/companies/{company_id}/webhooks/send/business-day-comparison
  GET  /api/companies/{company_id}/webhooks/logs
  GET  /api/companies/{company_id}/webhooks/stats
  
  POST /api/companies/{company_id}/services/start
  POST /api/companies/{company_id}/services/stop
  GET  /api/companies/{company_id}/services/status
  
  GET  /api/companies/{company_id}/news/latest
  GET  /api/companies/{company_id}/news/history
```

---

### Phase 2: 프론트엔드 구조 개편 (우선순위: 높음)

#### 2.1 새로운 메뉴 구조
```
┌─ 전체 대시보드 (통합)
│  └── 모든 회사의 상태를 한눈에
│
├─ 회사 관리 (NEW) ⭐
│  ├── 회사 목록
│  ├── 회사 추가/수정/삭제
│  └── 회사별 설정
│
├─ 회사별 대시보드 (NEW) ⭐
│  ├── POSCO 대시보드
│  │   ├── 서비스 상태
│  │   ├── 뉴스 모니터링
│  │   ├── 웹훅 통계
│  │   └── 최근 로그
│  │
│  ├── [회사2] 대시보드
│  └── [회사3] 대시보드
│
├─ 웹훅 관리 (회사별) ⭐
│  ├── 회사 선택 드롭다운
│  ├── 메시지 타입 (회사별 커스터마이징)
│  └── 발송 로그 (회사별 필터링)
│
├─ 서비스 관리 (회사별) ⭐
│  ├── 회사 선택 드롭다운
│  └── 서비스 제어
│
├─ 로그 뷰어 (통합)
│  ├── 회사별 필터링
│  └── 전체 로그 검색
│
└─ 시스템 설정
   ├── 전역 설정
   └── 회사별 설정
```

#### 2.2 UI 컴포넌트 구조
```
src/
├── components/
│   ├── CompanySelector/       # 회사 선택 드롭다운 (NEW)
│   │   └── CompanySelector.tsx
│   │
│   ├── CompanyManager/         # 회사 관리 (NEW)
│   │   ├── CompanyList.tsx
│   │   ├── CompanyForm.tsx
│   │   └── CompanyCard.tsx
│   │
│   ├── WebhookManager/         # 웹훅 관리 (개편)
│   │   ├── WebhookManager.tsx  # 회사 선택 추가
│   │   └── MessageTypeCard.tsx
│   │
│   └── Dashboard/              # 대시보드 (개편)
│       ├── GlobalDashboard.tsx # 전체 대시보드
│       └── CompanyDashboard.tsx # 회사별 대시보드
│
└── pages/
    ├── Dashboard.tsx           # 전체 대시보드
    ├── CompanyDashboard.tsx    # 회사별 대시보드 (NEW)
    ├── CompanyManager.tsx      # 회사 관리 (NEW)
    ├── WebhookManager.tsx      # 웹훅 관리 (개편)
    └── ...
```

---

### Phase 3: 설정 시스템 개편 (우선순위: 중간)

#### 3.1 회사 설정 구조
```json
{
  "companies": [
    {
      "id": "posco",
      "name": "POSCO",
      "display_name": "포스코",
      "logo_url": "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg",
      "webhooks": {
        "news_main": {
          "url": "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg",
          "bot_name": "POSCO 뉴스 📊",
          "bot_icon": "https://..."
        },
        "watchhamster": {
          "url": "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ",
          "bot_name": "POSCO 워치햄스터 🎯🛡️",
          "bot_icon": "https://..."
        }
      },
      "api_config": {
        "news_api": {
          "url": "https://global-api.einfomax.co.kr/apis/posco/news",
          "token": "YOUR_TOKEN",
          "endpoints": {
            "newyork": "/newyork-market-watch",
            "kospi": "/kospi-close",
            "exchange": "/exchange-rate"
          }
        }
      },
      "message_types": [
        "business_day_comparison",
        "delay_notification",
        "daily_report",
        "status_notification",
        "no_data_notification"
      ],
      "services": [
        {
          "id": "posco_news_monitor",
          "name": "POSCO 뉴스 모니터",
          "command": "python core/posco_scripts/posco_main_notifier.py"
        }
      ]
    },
    {
      "id": "company2",
      "name": "Company2",
      "display_name": "회사2",
      "webhooks": {...},
      "api_config": {...},
      "message_types": [...],
      "services": [...]
    }
  ]
}
```

---

## 🔧 구현 단계

### Step 1: 데이터베이스 설계 및 구현
- [ ] SQLite/PostgreSQL 스키마 생성
- [ ] 회사 테이블 생성
- [ ] 웹훅 설정 테이블 생성
- [ ] 로그 테이블에 company_id 추가
- [ ] 마이그레이션 스크립트 작성

### Step 2: 백엔드 리팩토링
- [ ] BaseWebhookSender 추상 클래스 생성
- [ ] BaseMessageGenerator 추상 클래스 생성
- [ ] CompanyFactory 패턴 구현
- [ ] 회사별 설정 로더 구현
- [ ] API 엔드포인트 재구성 (/api/companies/{id}/...)

### Step 3: 프론트엔드 리팩토링
- [ ] CompanySelector 컴포넌트 생성
- [ ] CompanyManager 페이지 생성
- [ ] CompanyDashboard 페이지 생성
- [ ] WebhookManager에 회사 선택 추가
- [ ] Services에 회사 선택 추가
- [ ] 사이드바 메뉴 재구성

### Step 4: 마이그레이션
- [ ] 기존 POSCO 데이터를 새 구조로 마이그레이션
- [ ] 기존 로그 데이터에 company_id 추가
- [ ] 기존 설정 파일 변환

### Step 5: 테스트 및 검증
- [ ] 회사 추가/수정/삭제 테스트
- [ ] 회사별 웹훅 발송 테스트
- [ ] 회사별 서비스 제어 테스트
- [ ] 로그 필터링 테스트

---

## 🎨 새로운 UI 구조

### 1. 사이드바 메뉴 (개편안)
```
┌─────────────────────────────┐
│ 🏠 전체 대시보드            │ ← 모든 회사 통합 뷰
├─────────────────────────────┤
│ 🏢 회사 관리 (NEW)          │ ← 회사 추가/수정/삭제
├─────────────────────────────┤
│ 📊 회사별 대시보드 (NEW)    │
│   ├─ 🏭 POSCO               │
│   ├─ 🏢 회사2               │
│   └─ 🏢 회사3               │
├─────────────────────────────┤
│ 📬 웹훅 관리                │ ← 회사 선택 드롭다운 추가
├─────────────────────────────┤
│ 🔧 서비스 관리              │ ← 회사 선택 드롭다운 추가
├─────────────────────────────┤
│ 📝 로그 뷰어                │ ← 회사별 필터링 추가
├─────────────────────────────┤
│ ⚙️ 설정                     │
└─────────────────────────────┘
```

### 2. 전체 대시보드 (개편안)
```
┌────────────────────────────────────────────────────────────┐
│ 🏠 전체 대시보드                                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 📊 회사별 상태 요약                                        │
│ ┌──────────────┬──────────────┬──────────────┐           │
│ │ 🏭 POSCO     │ 🏢 회사2     │ 🏢 회사3     │           │
│ │ ✅ 정상 작동 │ ✅ 정상 작동 │ ⚠️ 지연 감지 │           │
│ │ 서비스: 3/3  │ 서비스: 2/2  │ 서비스: 1/2  │           │
│ │ 웹훅: 15건   │ 웹훅: 8건    │ 웹훅: 3건    │           │
│ └──────────────┴──────────────┴──────────────┘           │
│                                                            │
│ 📈 통합 통계                                               │
│ ┌──────────┬──────────┬──────────┬──────────┐            │
│ │ 총 회사  │ 총 서비스│ 총 웹훅  │ 평균 응답│            │
│ │ 3개      │ 7개      │ 26건     │ 0.15s    │            │
│ └──────────┴──────────┴──────────┴──────────┘            │
│                                                            │
│ 🔔 최근 알림 (전체)                                        │
│ ┌────────┬──────────┬────────────────────────┐           │
│ │ 시간   │ 회사     │ 내용                   │           │
│ ├────────┼──────────┼────────────────────────┤           │
│ │ 14:10  │ POSCO    │ 영업일 비교 분석 발송  │           │
│ │ 14:08  │ 회사2    │ 정시 발행 알림         │           │
│ │ 14:05  │ POSCO    │ 테스트 메시지 발송     │           │
│ └────────┴──────────┴────────────────────────┘           │
└────────────────────────────────────────────────────────────┘
```

### 3. 회사 관리 페이지 (NEW)
```
┌────────────────────────────────────────────────────────────┐
│ 🏢 회사 관리                                [+ 회사 추가]  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 🏭 POSCO                                   [수정][삭제]│  │
│ │ ─────────────────────────────────────────────────────│  │
│ │ 상태: ✅ 활성                                        │  │
│ │ 웹훅: 2개 설정됨                                     │  │
│ │ API: 1개 설정됨                                      │  │
│ │ 서비스: 3개 실행 중                                  │  │
│ │ 마지막 활동: 2분 전                                  │  │
│ │                                                      │  │
│ │ [대시보드 보기] [웹훅 관리] [서비스 관리]            │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 🏢 회사2                                   [수정][삭제]│  │
│ │ ─────────────────────────────────────────────────────│  │
│ │ 상태: ✅ 활성                                        │  │
│ │ 웹훅: 1개 설정됨                                     │  │
│ │ API: 1개 설정됨                                      │  │
│ │ 서비스: 2개 실행 중                                  │  │
│ │                                                      │  │
│ │ [대시보드 보기] [웹훅 관리] [서비스 관리]            │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### 4. 회사별 대시보드 (NEW)
```
┌────────────────────────────────────────────────────────────┐
│ 🏭 POSCO 대시보드                                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 📊 서비스 상태                                             │
│ ┌──────────────┬──────────────┬──────────────┐           │
│ │ 뉴스 모니터  │ GitHub Pages │ 캐시 모니터  │           │
│ │ ✅ 실행 중   │ ✅ 실행 중   │ ⚠️ 중지됨   │           │
│ └──────────────┴──────────────┴──────────────┘           │
│                                                            │
│ 📬 웹훅 통계 (오늘)                                        │
│ ┌──────────┬──────────┬──────────┬──────────┐            │
│ │ 총 발송  │ 성공     │ 실패     │ 평균 시간│            │
│ │ 15건     │ 15건     │ 0건      │ 0.12s    │            │
│ └──────────┴──────────┴──────────┴──────────┘            │
│                                                            │
│ 📰 최근 뉴스 활동                                          │
│ ┌────────┬────────────────┬──────────────────┐           │
│ │ 시간   │ 타입           │ 상태             │           │
│ ├────────┼────────────────┼──────────────────┤           │
│ │ 14:10  │ 영업일 비교    │ ✅ 발송 완료     │           │
│ │ 14:08  │ 지연 알림      │ ✅ 발송 완료     │           │
│ └────────┴────────────────┴──────────────────┘           │
│                                                            │
│ [웹훅 관리] [서비스 관리] [로그 보기]                      │
└────────────────────────────────────────────────────────────┘
```

### 5. 웹훅 관리 (개편안)
```
┌────────────────────────────────────────────────────────────┐
│ 📬 웹훅 관리 시스템                                        │
│                                                            │
│ 회사 선택: [🏭 POSCO ▼]  [새로고침]                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ [메시지 타입] [발송 로그]                                  │
│                                                            │
│ 8개 메시지 타입 카드...                                    │
│ (각 카드는 선택된 회사의 설정 사용)                        │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 마이그레이션 전략

### 1. 기존 POSCO 데이터 보존
```python
# 마이그레이션 스크립트
def migrate_posco_to_multi_tenant():
    # 1. POSCO 회사 레코드 생성
    posco = Company(
        id="posco",
        name="POSCO",
        display_name="포스코",
        logo_url="https://...",
        is_active=True
    )
    
    # 2. 기존 웹훅 설정 이전
    posco_webhooks = [
        WebhookConfig(
            company_id="posco",
            channel_name="news_main",
            webhook_url="https://infomax.dooray.com/...",
            bot_name="POSCO 뉴스 📊"
        ),
        WebhookConfig(
            company_id="posco",
            channel_name="watchhamster",
            webhook_url="https://infomax.dooray.com/...",
            bot_name="POSCO 워치햄스터 🎯🛡️"
        )
    ]
    
    # 3. 기존 로그에 company_id 추가
    update_logs_with_company_id("posco")
    
    # 4. 기존 서비스 설정 이전
    posco_services = [...]
```

### 2. 하위 호환성 유지
```python
# 기존 API 엔드포인트 유지 (deprecated)
@router.post("/api/webhook-manager/send/test")
async def legacy_send_test():
    """레거시 엔드포인트 (POSCO 기본값 사용)"""
    return await send_test_for_company("posco", ...)

# 새 API 엔드포인트
@router.post("/api/companies/{company_id}/webhooks/send/test")
async def send_test_for_company(company_id: str, ...):
    """회사별 웹훅 발송"""
    ...
```

---

## 📊 예상 작업량

### 백엔드 (약 3-5일)
- 데이터베이스 설계: 0.5일
- 모델 및 리포지토리: 1일
- 베이스 클래스 리팩토링: 1일
- API 엔드포인트 재구성: 1일
- 마이그레이션 스크립트: 0.5일
- 테스트: 1일

### 프론트엔드 (약 2-3일)
- CompanySelector 컴포넌트: 0.5일
- CompanyManager 페이지: 1일
- CompanyDashboard 페이지: 0.5일
- 기존 페이지 개편: 1일
- 테스트: 0.5일

### 총 예상: 5-8일

---

## 🎯 우선순위

### 높음 (즉시 시작)
1. **데이터베이스 스키마 설계**
2. **회사 관리 API 구현**
3. **CompanySelector 컴포넌트**
4. **사이드바 메뉴 재구성**

### 중간 (1주 내)
5. **베이스 클래스 리팩토링**
6. **회사별 대시보드**
7. **웹훅 관리 개편**

### 낮음 (2주 내)
8. **마이그레이션 자동화**
9. **문서화**
10. **성능 최적화**

---

## 🚨 주의사항

### 1. 기존 POSCO 시스템 중단 없이 진행
- 마이그레이션 중에도 기존 시스템 정상 작동
- 레거시 API 엔드포인트 유지
- 점진적 마이그레이션 (단계별 전환)

### 2. 데이터 손실 방지
- 마이그레이션 전 전체 백업
- 롤백 계획 수립
- 마이그레이션 검증 스크립트

### 3. 보안 고려사항
- 회사별 데이터 격리
- API 토큰 암호화
- 회사별 접근 권한 관리

---

## 📝 다음 단계

### 즉시 결정 필요
1. **데이터베이스 선택**: SQLite vs PostgreSQL?
2. **마이그레이션 시점**: 언제 시작할까?
3. **회사 추가 계획**: 어떤 회사들을 추가할 예정인가?
4. **우선순위 조정**: 어떤 기능을 먼저 구현할까?

### 제안
- **Phase 1 먼저 시작**: 데이터베이스 + 회사 관리 API
- **POSCO 유지하면서 점진적 전환**
- **새 회사 추가 시 새 구조 사용**
- **기존 POSCO는 나중에 마이그레이션**

---

## ✅ 체크리스트

- [ ] 데이터베이스 스키마 승인
- [ ] 새 메뉴 구조 승인
- [ ] API 엔드포인트 구조 승인
- [ ] 마이그레이션 전략 승인
- [ ] 우선순위 확정
- [ ] 작업 시작 일정 확정
