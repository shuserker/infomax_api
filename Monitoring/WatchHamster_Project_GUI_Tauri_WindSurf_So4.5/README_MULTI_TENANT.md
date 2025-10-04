# 🐹 WatchHamster v3.0 - 멀티 테넌트 플랫폼

## 🎯 개요

WatchHamster가 **POSCO 전용 시스템**에서 **멀티 테넌트 플랫폼**으로 완전히 재구성되었습니다.

이제 **코딩 없이 UI에서 클릭만으로** 새로운 회사를 추가하고 독립적으로 운영할 수 있습니다.

---

## 🚀 빠른 시작

### 1. 서버 실행
```bash
# 백엔드 (포트 8000)
cd python-backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 프론트엔드 (포트 1420)
npm run dev
```

### 2. 접속
```
회사 관리: http://localhost:1420/companies
웹훅 관리: http://localhost:1420/webhooks
API 문서:  http://localhost:8000/docs
```

---

## 🏢 신규 회사 추가 (코딩 불필요!)

### UI에서 추가 ⭐
```
1. http://localhost:1420/companies 접속
2. "회사 추가" 버튼 클릭
3. 4단계 폼 작성:
   ① 기본 정보 (ID, 이름, 로고)
   ② 웹훅 설정 (Dooray URL 2개)
   ③ API 설정 (URL, 토큰)
   ④ 완료 (확인)
4. 저장 → 즉시 사용 가능!
```

### 필요한 정보
- **회사 ID**: 영문 소문자 (예: company2)
- **회사명**: 영문 (예: Company2)
- **표시명**: 한글 (예: 회사2)
- **Dooray 웹훅 URL**: 2개 (메인 채널, 알림 채널)
- **API URL**: 뉴스 API 주소
- **API 토큰**: (선택사항)

---

## 📊 시스템 구조

### 멀티 테넌트 아키텍처
```
🐹 WatchHamster v3.0 (최고 관리 시스템)
│
├── 🏭 POSCO
│   ├── 웹훅 설정: 2개
│   │   ├─ news_main (뉴스 알림)
│   │   └─ watchhamster (시스템 알림)
│   ├── API 설정: 1개
│   │   └─ news_api
│   ├── 메시지 타입: 8개
│   └── 로그: 독립 저장
│
├── 🏢 회사2 (추가 가능)
│   ├── 웹훅 설정: UI에서 입력
│   ├── API 설정: UI에서 입력
│   ├── 메시지 타입: 선택 가능
│   └── 로그: 독립 저장
│
└── 🏢 회사3 (추가 가능)
    └── ...
```

---

## 🎯 주요 기능

### 1. 회사 관리 (`/companies`)
- ✅ 회사 목록 카드 표시
- ✅ 회사 추가 (4단계 위저드)
- ✅ 회사 상세 보기
- ✅ 회사 삭제
- ✅ 웹훅/API 설정 확인
- ✅ 통계 확인

### 2. 웹훅 관리 (`/webhooks`)
- ✅ 회사 선택 드롭다운
- ✅ 8가지 메시지 타입
- ✅ 테스트 발송
- ✅ 회사별 통계
- ✅ 회사별 로그

### 3. 사이드바 메뉴
```
🏠 전체 대시보드
🏢 회사 관리 ⭐
🔧 서비스 관리
⚙️ API 설정
📬 웹훅 관리 ⭐
📝 로그 뷰어
⚙️ 설정
```

---

## 📁 파일 구조

### 백엔드
```
python-backend/
├── database/
│   ├── __init__.py          # 데이터베이스 모듈
│   ├── models.py            # Pydantic 모델 (7개)
│   └── db.py                # SQLite 클래스
│
├── api/
│   ├── companies.py         # 회사 관리 API (NEW)
│   └── webhook_manager.py   # 웹훅 관리 (회사별 지원)
│
├── scripts/
│   └── migrate_posco.py     # POSCO 마이그레이션
│
└── watchhamster.db          # SQLite 데이터베이스
```

### 프론트엔드
```
src/
├── components/
│   ├── CompanySelector/     # 회사 선택 드롭다운 (NEW)
│   ├── CompanyForm/         # 회사 추가 폼 (NEW)
│   └── WebhookManager/      # 웹훅 관리 (회사별 지원)
│
└── pages/
    ├── CompanyManager.tsx   # 회사 관리 페이지 (NEW)
    └── Services.tsx         # 서비스 관리 (수정)
```

---

## 🔌 API 엔드포인트

### 회사 관리
```
POST   /api/companies                    # 회사 추가
GET    /api/companies                    # 회사 목록
GET    /api/companies/{id}               # 회사 상세
PUT    /api/companies/{id}               # 회사 수정
DELETE /api/companies/{id}               # 회사 삭제
GET    /api/companies/{id}/webhooks      # 웹훅 설정
GET    /api/companies/{id}/api-configs   # API 설정
GET    /api/companies/{id}/stats         # 통계
```

### 웹훅 관리 (회사별 지원)
```
GET    /api/webhook-manager/stats?company_id=posco
GET    /api/webhook-manager/logs?company_id=posco
POST   /api/webhook-manager/send/test?company_id=posco
```

---

## 🗄️ 데이터베이스

### SQLite 테이블
```sql
-- 회사
companies (id, name, display_name, logo_url, is_active, created_at, updated_at)

-- 웹훅 설정
webhook_configs (id, company_id, channel_name, webhook_url, bot_name, bot_icon, is_active)

-- API 설정
api_configs (id, company_id, api_name, api_url, api_token, config, is_active)

-- 웹훅 로그
webhook_logs (id, company_id, timestamp, message_type, bot_type, priority, endpoint, status, ...)
```

### 데이터베이스 파일
```
python-backend/watchhamster.db
```

---

## 🧪 테스트

### 회사 추가 테스트
```bash
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-company",
    "name": "TestCompany",
    "display_name": "테스트회사",
    "webhooks": {
      "news_main": {
        "url": "https://dooray.com/...",
        "bot_name": "테스트 뉴스 📊",
        "bot_icon": "https://..."
      }
    },
    "api_config": {
      "news_api": {
        "url": "https://api.test.com/news",
        "token": "YOUR_TOKEN"
      }
    },
    "message_types": ["business_day_comparison", "daily_report"]
  }'
```

### 회사 목록 조회
```bash
curl http://localhost:8000/api/companies
```

### 회사 상세 조회
```bash
curl http://localhost:8000/api/companies/posco
```

---

## 📊 마이그레이션

### POSCO 데이터
```bash
# POSCO 데이터 마이그레이션 (이미 완료)
cd python-backend
python scripts/migrate_posco.py
```

### 결과
```
✅ 회사: POSCO (포스코)
✅ 웹훅 설정: 2개
   - news_main (POSCO 뉴스 📊)
   - watchhamster (POSCO 워치햄스터 🎯🛡️)
✅ API 설정: 1개
   - news_api (https://global-api.einfomax.co.kr/apis/posco/news)
```

---

## 🎨 UI 스크린샷

### 회사 관리 페이지
```
┌────────────────────────────────────────────────────────────┐
│ 🏢 회사 관리                    [새로고침] [+ 회사 추가]   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 🏭 포스코 (POSCO)                            ✅ 활성 │  │
│ │ ─────────────────────────────────────────────────────│  │
│ │ 등록일: 2025-10-04                                   │  │
│ │ 마지막 수정: 2025-10-04                              │  │
│ │                                                      │  │
│ │ [웹훅 관리] [대시보드]                               │  │
│ │ [수정] [삭제]                                        │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### 웹훅 관리 페이지
```
┌────────────────────────────────────────────────────────────┐
│ 📬 웹훅 관리 시스템                            [새로고침]  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 회사 선택: [🏭 포스코 (POSCO) ▼]                          │
│                                                            │
│ ┌──────────┬──────────┬──────────┬──────────┐            │
│ │ 총 발송  │ 성공     │ 실패     │ 평균 응답│            │
│ │ 0건      │ 0건      │ 0건      │ 0.00s    │            │
│ └──────────┴──────────┴──────────┴──────────┘            │
│                                                            │
│ 📋 메시지 타입 (8개)                                       │
│ [영업일 비교] [지연 알림] [일일 리포트] ...               │
└────────────────────────────────────────────────────────────┘
```

---

## 🎉 완료!

### 구현 완료
- ✅ 멀티 테넌트 아키텍처
- ✅ 회사 관리 시스템
- ✅ 회사별 웹훅 발송
- ✅ 회사별 로그 관리
- ✅ UI 기반 회사 추가

### 시스템 상태
- ✅ 백엔드: 실행 중 (포트 8000)
- ✅ 프론트엔드: 실행 중 (포트 1420)
- ✅ 데이터베이스: watchhamster.db
- ✅ POSCO: 마이그레이션 완료

**지금 바로 사용 가능합니다!** 🚀

---

## 📞 문의

문제가 발생하면 다음 문서를 참고하세요:
- `COMPANY_ONBOARDING_GUIDE.md` - 회사 추가 가이드
- `ARCHITECTURE_COMPARISON.md` - 아키텍처 비교
- `FINAL_SUMMARY.md` - 최종 요약
