# 🏢 신규 회사 추가 가이드

## 🎯 WatchHamster 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│                  🐹 WatchHamster v3.0                   │
│              (최고 관리 시스템)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ 🏭 POSCO │  │ 🏢 회사2 │  │ 🏢 회사3 │  [+ 추가]  │
│  └──────────┘  └──────────┘  └──────────┘            │
│                                                         │
│  각 회사는 독립적으로:                                   │
│  - 웹훅 설정                                            │
│  - API 설정                                             │
│  - 서비스 관리                                          │
│  - 뉴스 모니터링                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 신규 회사 추가 방법

### 방법 1: UI에서 추가 (권장) ⭐

#### 단계
1. **WatchHamster UI 접속**
   ```
   http://localhost:5173/companies
   ```

2. **"+ 회사 추가" 버튼 클릭**

3. **회사 정보 입력 폼**
   ```
   ┌─────────────────────────────────────────┐
   │ 🏢 신규 회사 추가                       │
   ├─────────────────────────────────────────┤
   │                                         │
   │ 회사 ID: [company2]                     │
   │ 회사명: [회사2]                         │
   │ 표시명: [회사2 주식회사]                │
   │ 로고 URL: [https://...]                 │
   │                                         │
   │ ─────────────────────────────────────   │
   │ 📬 웹훅 설정                            │
   │                                         │
   │ 메인 채널 URL: [https://dooray.com/...] │
   │ BOT 이름: [회사2 뉴스 📊]               │
   │ BOT 아이콘: [https://...]               │
   │                                         │
   │ 알림 채널 URL: [https://dooray.com/...] │
   │ BOT 이름: [회사2 워치햄스터 🎯]         │
   │                                         │
   │ ─────────────────────────────────────   │
   │ 🔌 API 설정                             │
   │                                         │
   │ API URL: [https://api.company2.com/...] │
   │ API 토큰: [YOUR_TOKEN]                  │
   │                                         │
   │ 뉴스 타입:                              │
   │ ☑ 뉴욕마켓워치                          │
   │ ☑ 코스피 마감                           │
   │ ☑ 서환마감                              │
   │                                         │
   │ ─────────────────────────────────────   │
   │ 📋 메시지 타입 선택                     │
   │                                         │
   │ ☑ 영업일 비교 분석                      │
   │ ☑ 지연 발행 알림                        │
   │ ☑ 일일 통합 리포트                      │
   │ ☑ 정시 발행 알림                        │
   │ ☑ 데이터 갱신 없음                      │
   │                                         │
   │        [취소]  [저장]                   │
   └─────────────────────────────────────────┘
   ```

4. **저장 → 자동으로 데이터베이스에 저장**

5. **즉시 사용 가능**
   - 회사 선택 드롭다운에 표시
   - 웹훅 발송 가능
   - 서비스 관리 가능

#### 장점
- ✅ **코딩 불필요**
- ✅ **즉시 추가 가능**
- ✅ **실수 방지** (폼 검증)
- ✅ **비개발자도 추가 가능**

---

### 방법 2: API로 추가 (개발자용)

#### cURL 예시
```bash
curl -X POST "http://localhost:8000/api/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "company2",
    "name": "Company2",
    "display_name": "회사2 주식회사",
    "logo_url": "https://company2.com/logo.png",
    "webhooks": {
      "news_main": {
        "url": "https://company2.dooray.com/services/.../...",
        "bot_name": "회사2 뉴스 📊",
        "bot_icon": "https://company2.com/bot_icon.png"
      },
      "watchhamster": {
        "url": "https://company2.dooray.com/services/.../...",
        "bot_name": "회사2 워치햄스터 🎯",
        "bot_icon": "https://company2.com/bot_icon.png"
      }
    },
    "api_config": {
      "news_api": {
        "url": "https://api.company2.com/news",
        "token": "YOUR_API_TOKEN",
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
    "is_active": true
  }'
```

#### Python 예시
```python
import requests

company_data = {
    "id": "company2",
    "name": "Company2",
    "display_name": "회사2 주식회사",
    "logo_url": "https://company2.com/logo.png",
    "webhooks": {...},
    "api_config": {...},
    "message_types": [...],
    "is_active": True
}

response = requests.post(
    "http://localhost:8000/api/companies",
    json=company_data
)

print(f"회사 추가 완료: {response.json()}")
```

#### 장점
- ✅ **자동화 가능**
- ✅ **스크립트로 대량 추가**
- ✅ **CI/CD 통합 가능**

---

### 방법 3: 설정 파일로 추가 (초기 설정용)

#### companies.json
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
          "bot_icon": "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg"
        },
        "watchhamster": {
          "url": "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ",
          "bot_name": "POSCO 워치햄스터 🎯🛡️",
          "bot_icon": "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg"
        }
      },
      "api_config": {
        "news_api": {
          "url": "https://global-api.einfomax.co.kr/apis/posco/news",
          "token": "YOUR_TOKEN"
        }
      },
      "message_types": [
        "business_day_comparison",
        "delay_notification",
        "daily_report",
        "status_notification",
        "no_data_notification"
      ],
      "is_active": true
    },
    {
      "id": "company2",
      "name": "Company2",
      "display_name": "회사2",
      "webhooks": {...},
      "api_config": {...},
      "message_types": [...],
      "is_active": true
    }
  ]
}
```

#### 로드 스크립트
```bash
# 설정 파일에서 회사 일괄 등록
python scripts/load_companies.py --config companies.json
```

#### 장점
- ✅ **초기 설정 편리**
- ✅ **버전 관리 가능** (Git)
- ✅ **백업/복원 쉬움**

---

## 🎯 권장 방식

### 일반 사용자 (비개발자)
→ **방법 1: UI에서 추가** ⭐
- 가장 직관적
- 실수 방지
- 즉시 확인 가능

### 개발자/관리자
→ **방법 2: API로 추가**
- 자동화 가능
- 스크립트 작성

### 초기 설정/대량 추가
→ **방법 3: 설정 파일**
- 한 번에 여러 회사 추가
- 백업/복원 용이

---

## 📋 신규 회사 추가 시 필요한 정보

### 필수 정보
1. **회사 기본 정보**
   - ID (영문, 소문자, 하이픈만)
   - 회사명
   - 표시명 (한글)
   - 로고 URL

2. **웹훅 설정**
   - Dooray 웹훅 URL (메인 채널)
   - Dooray 웹훅 URL (알림 채널)
   - BOT 이름
   - BOT 아이콘 URL

3. **API 설정**
   - API URL
   - API 토큰
   - 엔드포인트 경로

4. **메시지 타입 선택**
   - 사용할 메시지 타입 체크

### 선택 정보
- 서비스 설정 (모니터링 스크립트)
- 커스텀 메시지 템플릿
- 알림 규칙

---

## 🔧 구현 예시

### UI 폼 (CompanyForm.tsx)
```typescript
interface CompanyFormData {
  id: string;
  name: string;
  display_name: string;
  logo_url: string;
  webhooks: {
    news_main: {
      url: string;
      bot_name: string;
      bot_icon: string;
    };
    watchhamster: {
      url: string;
      bot_name: string;
      bot_icon: string;
    };
  };
  api_config: {
    news_api: {
      url: string;
      token: string;
    };
  };
  message_types: string[];
  is_active: boolean;
}

const handleSubmit = async (data: CompanyFormData) => {
  const response = await fetch('http://localhost:8000/api/companies', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (response.ok) {
    toast({ title: '회사 추가 완료!', status: 'success' });
    navigate('/companies');
  }
};
```

### 백엔드 API (companies.py)
```python
@router.post("/companies")
async def create_company(company: CompanyCreate):
    """신규 회사 추가"""
    try:
        # 1. 데이터 검증
        validate_company_data(company)
        
        # 2. 데이터베이스에 저장
        company_id = await db.companies.insert(company.dict())
        
        # 3. 웹훅 설정 저장
        for channel, config in company.webhooks.items():
            await db.webhook_configs.insert({
                "company_id": company_id,
                "channel_name": channel,
                **config
            })
        
        # 4. API 설정 저장
        await db.api_configs.insert({
            "company_id": company_id,
            **company.api_config
        })
        
        # 5. 회사별 인스턴스 생성
        company_instance = CompanyFactory.create(company_id)
        
        return {
            "status": "success",
            "company_id": company_id,
            "message": f"{company.name} 추가 완료"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 🎨 UI 플로우

### 1. 회사 관리 페이지
```
┌────────────────────────────────────────────────────────────┐
│ 🏢 회사 관리                          [+ 회사 추가]        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 🏭 POSCO                                   [수정][삭제]│  │
│ │ ─────────────────────────────────────────────────────│  │
│ │ 상태: ✅ 활성                                        │  │
│ │ 웹훅: 2개 | API: 1개 | 서비스: 3개                   │  │
│ │ 마지막 활동: 2분 전                                  │  │
│ │                                                      │  │
│ │ [대시보드] [웹훅 관리] [서비스 관리]                 │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 🏢 회사2                                   [수정][삭제]│  │
│ │ ─────────────────────────────────────────────────────│  │
│ │ 상태: ✅ 활성                                        │  │
│ │ 웹훅: 1개 | API: 1개 | 서비스: 2개                   │  │
│ │                                                      │  │
│ │ [대시보드] [웹훅 관리] [서비스 관리]                 │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### 2. 회사 추가 폼 (클릭 시)
```
┌────────────────────────────────────────────────────────────┐
│ 🏢 신규 회사 추가                                    [X]   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ [1. 기본 정보] [2. 웹훅 설정] [3. API 설정] [4. 완료]    │
│                                                            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                            │
│ 📋 기본 정보                                               │
│                                                            │
│ 회사 ID *                                                  │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ company2                                             │  │
│ └──────────────────────────────────────────────────────┘  │
│ ℹ️ 영문 소문자, 숫자, 하이픈만 사용 (예: posco, company2) │
│                                                            │
│ 회사명 *                                                   │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Company2                                             │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ 표시명 (한글)                                              │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 회사2 주식회사                                       │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ 로고 URL                                                   │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ https://company2.com/logo.png                        │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│                              [이전]  [다음: 웹훅 설정 →]  │
└────────────────────────────────────────────────────────────┘
```

### 3. 웹훅 설정 단계
```
┌────────────────────────────────────────────────────────────┐
│ 🏢 신규 회사 추가 - 웹훅 설정                        [X]   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ [1. 기본 정보] [2. 웹훅 설정] [3. API 설정] [4. 완료]    │
│                                                            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                            │
│ 📬 메인 채널 웹훅 (뉴스 알림용)                            │
│                                                            │
│ Dooray 웹훅 URL *                                          │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ https://company2.dooray.com/services/.../...         │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ BOT 이름                                                   │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 회사2 뉴스 📊                                        │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ BOT 아이콘 URL                                             │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ https://company2.com/bot_icon.png                    │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ [테스트 발송]  ← 웹훅 URL 검증                             │
│                                                            │
│ ─────────────────────────────────────────────────────────  │
│                                                            │
│ 📬 알림 채널 웹훅 (워치햄스터 알림용)                      │
│                                                            │
│ Dooray 웹훅 URL                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ https://company2.dooray.com/services/.../...         │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ BOT 이름                                                   │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 회사2 워치햄스터 🎯                                  │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│                    [← 이전]  [다음: API 설정 →]           │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 회사 추가 후 자동 처리

### 백엔드에서 자동으로:
1. ✅ 데이터베이스에 저장
2. ✅ 회사별 WebhookSender 인스턴스 생성
3. ✅ 회사별 MessageGenerator 인스턴스 생성
4. ✅ 회사별 Monitor 인스턴스 생성 (선택 시)
5. ✅ 로그 테이블에 company_id 컬럼 자동 사용

### 프론트엔드에서 자동으로:
1. ✅ 회사 선택 드롭다운에 추가
2. ✅ 회사별 대시보드 생성
3. ✅ 사이드바에 회사 표시 (옵션 B 선택 시)
4. ✅ 로그 필터에 회사 추가

---

## 💡 핵심 포인트

### ❌ 코딩 불필요!
```
신규 회사 추가 = UI 폼 작성 + 저장 버튼 클릭
```

### ✅ 필요한 것
1. **Dooray 웹훅 URL** (2개)
   - 메인 채널 (뉴스 알림용)
   - 알림 채널 (워치햄스터 알림용)

2. **API 정보**
   - API URL
   - API 토큰

3. **회사 정보**
   - 회사명, 로고

### 🎯 추가 후 즉시 가능
- ✅ 웹훅 발송 (8가지 메시지 타입)
- ✅ 서비스 관리
- ✅ 뉴스 모니터링
- ✅ 로그 확인

---

## 🚀 다음 단계

1. **데이터베이스 선택** (SQLite 권장)
2. **회사 관리 UI 구현** (CompanyManager.tsx)
3. **회사 추가 폼 구현** (CompanyForm.tsx)
4. **회사 관리 API 구현** (api/companies.py)
5. **테스트 회사 추가** (UI로 직접 추가)

**코딩 없이 UI에서 클릭만으로 회사 추가 가능!** 🎉
