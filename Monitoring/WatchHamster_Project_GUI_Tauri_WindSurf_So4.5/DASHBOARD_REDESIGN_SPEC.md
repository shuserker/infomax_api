# 🎨 시스템 대시보드 리뉴얼 설계서

## 📋 Task 개요

### 목표
**멀티 테넌트 시스템에 맞는 현대적인 대시보드 구성**

### 현재 문제점
```
❌ POSCO 전용 구성 (단일 회사)
❌ 뉴스 모니터링만 표시
❌ 회사 선택 기능 없음
❌ 멀티 테넌트 정보 없음
❌ 구식 디자인
```

### 목표 상태
```
✅ 회사별 대시보드
✅ 전체 시스템 개요
✅ 회사 선택 드롭다운
✅ 멀티 테넌트 통계
✅ 현대적인 디자인
```

---

## 🎯 새로운 대시보드 구성

### 1. 상단: 전체 시스템 개요 (NEW)
```
┌─────────────────────────────────────────────────────────┐
│ 🏢 전체 시스템 개요                    [회사 선택 ▼]  │
├─────────────────────────────────────────────────────────┤
│  📊 등록된 회사      🔔 총 웹훅 발송      📈 성공률    │
│      3개                 1,234개           98.5%      │
│                                                         │
│  💾 시스템 상태      ⚡ API 응답         🔄 업타임     │
│    정상 (100%)          2ms              3일 5시간    │
└─────────────────────────────────────────────────────────┘
```

### 2. 중단: 회사별 현황 (NEW)
```
┌─────────────────────────────────────────────────────────┐
│ 🏢 회사별 현황                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [POSCO 카드]    [삼성 카드]    [현대 카드]            │
│   활성            활성            비활성                │
│   웹훅: 2개       웹훅: 3개       웹훅: 1개             │
│   발송: 450       발송: 320       발송: 0               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. 하단: 선택된 회사 상세 (기존 개선)
```
┌─────────────────────────────────────────────────────────┐
│ 📊 POSCO 상세 현황                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  뉴스 모니터링 상태                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ 환율 정보 │  │ 뉴욕 증시 │  │ KOSPI 마감│            │
│  │ 정상      │  │ 정상      │  │ 정상      │            │
│  │ 03:37:42 │  │ 03:37:42 │  │ 03:37:42 │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│                                                         │
│  웹훅 발송 이력 (최근 10개)                             │
│  [테이블 형식]                                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 새로운 컴포넌트 구조

### 1. SystemOverview (NEW)
```typescript
// 전체 시스템 개요
interface SystemOverviewProps {
  totalCompanies: number
  totalWebhooks: number
  successRate: number
  systemHealth: string
  apiResponseTime: number
  uptime: number
}
```

### 2. CompanyStatusGrid (NEW)
```typescript
// 회사별 현황 그리드
interface CompanyStatusCardProps {
  company: Company
  webhookCount: number
  totalSent: number
  isActive: boolean
  onClick: () => void
}
```

### 3. CompanyDetailDashboard (개선)
```typescript
// 선택된 회사 상세 대시보드
interface CompanyDetailProps {
  companyId: string
  newsStatus: NewsStatus[]
  webhookLogs: WebhookLog[]
  stats: CompanyStats
}
```

---

## 📊 데이터 구조

### 전체 시스템 통계 (NEW API)
```typescript
GET /api/dashboard/system-overview

Response:
{
  total_companies: 3,
  active_companies: 2,
  total_webhooks_sent: 1234,
  success_rate: 98.5,
  system_health: "healthy",
  api_response_time_ms: 2,
  uptime_seconds: 270000,
  companies: [
    {
      id: "posco",
      name: "POSCO",
      webhook_count: 2,
      total_sent: 450,
      success_rate: 99.1,
      is_active: true,
      last_activity: "2025-10-04T15:30:00"
    },
    // ...
  ]
}
```

### 회사별 상세 (기존 활용)
```typescript
GET /api/companies/{company_id}/stats
GET /api/webhook-manager/logs?company_id={id}
```

---

## 🎨 디자인 개선

### 컬러 스킴
```
주 색상: Blue (신뢰감)
보조 색상: Green (성공), Red (오류), Yellow (경고)
배경: White/Gray.50 (밝음), Gray.800 (다크)
```

### 카드 디자인
```
- 둥근 모서리 (borderRadius: lg)
- 그림자 효과 (shadow: md)
- 호버 효과 (shadow: lg, transform: translateY(-2px))
- 애니메이션 (transition: all 0.2s)
```

### 아이콘
```
🏢 회사: FiBuilding
📊 통계: FiBarChart2
🔔 웹훅: FiBell
✅ 성공: FiCheckCircle
❌ 실패: FiXCircle
⚡ 빠름: FiZap
🔄 업타임: FiClock
```

---

## 📁 파일 구조

### 새로 만들 파일
```
src/components/Dashboard/
├── SystemOverview.tsx           (NEW) - 전체 시스템 개요
├── CompanyStatusGrid.tsx        (NEW) - 회사별 현황 그리드
├── CompanyStatusCard.tsx        (NEW) - 회사 상태 카드
├── CompanyDetailDashboard.tsx   (NEW) - 회사 상세 대시보드
└── DashboardLayout.tsx          (NEW) - 대시보드 레이아웃

src/pages/
└── Dashboard.tsx                (수정) - 메인 대시보드 페이지

python-backend/api/
└── dashboard.py                 (NEW) - 대시보드 전용 API
```

---

## 🚀 구현 계획

### Phase 1: 백엔드 API (30분)
```
1. dashboard.py 생성
   - GET /api/dashboard/system-overview
   - GET /api/dashboard/company-summary
   
2. 기존 API 활용
   - /api/companies
   - /api/webhook-manager/stats
   - /api/webhook-manager/logs
```

### Phase 2: 컴포넌트 개발 (1시간)
```
1. SystemOverview 컴포넌트
2. CompanyStatusGrid 컴포넌트
3. CompanyStatusCard 컴포넌트
4. CompanyDetailDashboard 컴포넌트
```

### Phase 3: 페이지 통합 (30분)
```
1. Dashboard.tsx 리뉴얼
2. 레이아웃 구성
3. 데이터 연동
```

### Phase 4: 테스트 & 최적화 (30분)
```
1. 기능 테스트
2. 반응형 확인
3. 성능 최적화
```

**총 예상 시간: 2.5시간**

---

## 🎯 핵심 기능

### 1. 회사 선택 기능
```
- 드롭다운으로 회사 선택
- 선택한 회사의 상세 정보 표시
- "전체" 선택 시 모든 회사 통계
```

### 2. 실시간 업데이트
```
- 10초마다 자동 새로고침
- WebSocket 연동 (선택적)
- 변경사항 하이라이트
```

### 3. 빠른 액션
```
- 회사 추가 버튼
- 웹훅 발송 버튼
- 설정 바로가기
```

---

## 📊 개선 효과

### Before (현재)
```
❌ POSCO 전용
❌ 단일 회사 정보만
❌ 멀티 테넌트 정보 없음
❌ 구식 디자인
```

### After (목표)
```
✅ 멀티 테넌트 지원
✅ 전체 시스템 개요
✅ 회사별 현황 한눈에
✅ 현대적인 디자인
✅ 실시간 업데이트
```

---

## 🎨 UI 목업 (텍스트)

### 전체 레이아웃
```
┌─────────────────────────────────────────────────────────┐
│ 🏢 WatchHamster 시스템 대시보드      [회사: POSCO ▼]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 📊 전체 시스템 개요                              │   │
│ │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │   │
│ │ │회사 3│ │웹훅  │ │성공률│ │응답  │ │업타임│ │   │
│ │ │개    │ │1234 │ │98.5%│ │2ms  │ │3일  │ │   │
│ │ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 🏢 회사별 현황                                   │   │
│ │ ┌─────────┐ ┌─────────┐ ┌─────────┐          │   │
│ │ │ POSCO   │ │ 삼성    │ │ 현대    │          │   │
│ │ │ ✅ 활성  │ │ ✅ 활성  │ │ ⭕ 비활성│          │   │
│ │ │ 웹훅: 2 │ │ 웹훅: 3 │ │ 웹훅: 1 │          │   │
│ │ │ 450건   │ │ 320건   │ │ 0건     │          │   │
│ │ └─────────┘ └─────────┘ └─────────┘          │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 📊 POSCO 상세 현황                               │   │
│ │                                                  │   │
│ │ 뉴스 모니터링 (3개)                              │   │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│ │ │환율 정보  │ │뉴욕 증시  │ │KOSPI 마감│        │   │
│ │ │✅ 정상   │ │✅ 정상   │ │✅ 정상   │        │   │
│ │ │03:37:42 │ │03:37:42 │ │03:37:42 │        │   │
│ │ └──────────┘ └──────────┘ └──────────┘        │   │
│ │                                                  │   │
│ │ 웹훅 발송 이력                                   │   │
│ │ [최근 10개 테이블]                               │   │
│ └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 구현 상세

### 1. SystemOverview 컴포넌트

#### 표시 항목
```typescript
interface SystemOverviewData {
  // 회사 정보
  totalCompanies: number        // 등록된 회사 수
  activeCompanies: number       // 활성 회사 수
  
  // 웹훅 통계
  totalWebhooksSent: number     // 총 발송 건수
  successRate: number           // 성공률 (%)
  failedToday: number           // 오늘 실패 건수
  
  // 시스템 상태
  systemHealth: 'healthy' | 'warning' | 'critical'
  apiResponseTime: number       // API 응답 시간 (ms)
  uptime: number                // 업타임 (초)
  
  // 성능 지표
  cpuUsage: number              // CPU 사용률
  memoryUsage: number           // 메모리 사용률
  diskUsage: number             // 디스크 사용률
}
```

#### UI 구성
```
┌────────────────────────────────────────────────────┐
│ 📊 전체 시스템 개요                                │
├────────────────────────────────────────────────────┤
│                                                    │
│  [회사 3개]  [웹훅 1.2K]  [성공 98%]  [응답 2ms]  │
│                                                    │
│  시스템 상태: ✅ 정상                              │
│  업타임: 3일 5시간 23분                            │
│                                                    │
│  [CPU 45%] [메모리 68%] [디스크 88%]              │
│                                                    │
└────────────────────────────────────────────────────┘
```

### 2. CompanyStatusGrid 컴포넌트

#### 표시 항목
```typescript
interface CompanyStatusCard {
  id: string
  name: string
  displayName: string
  isActive: boolean
  
  // 웹훅 정보
  webhookCount: number
  totalSent: number
  successRate: number
  lastActivity: string
  
  // 뉴스 모니터링
  newsMonitors: number
  newsStatus: 'all_ok' | 'some_delayed' | 'error'
  
  // 빠른 액션
  quickActions: ['웹훅 발송', '설정', '로그']
}
```

#### UI 구성
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 🏢 POSCO    │ │ 🏢 삼성     │ │ 🏢 현대     │
├─────────────┤ ├─────────────┤ ├─────────────┤
│ ✅ 활성      │ │ ✅ 활성      │ │ ⭕ 비활성    │
│             │ │             │ │             │
│ 웹훅: 2개   │ │ 웹훅: 3개   │ │ 웹훅: 1개   │
│ 발송: 450건 │ │ 발송: 320건 │ │ 발송: 0건   │
│ 성공: 99.1% │ │ 성공: 98.2% │ │ 성공: -     │
│             │ │             │ │             │
│ 뉴스: 3개   │ │ 뉴스: 2개   │ │ 뉴스: 0개   │
│ ✅ 모두정상  │ │ ⚠️ 1개지연  │ │ -           │
│             │ │             │ │             │
│ [상세보기]  │ │ [상세보기]  │ │ [활성화]    │
└─────────────┘ └─────────────┘ └─────────────┘
```

### 3. CompanyDetailDashboard 컴포넌트

#### 탭 구성
```
┌────────────────────────────────────────────────────┐
│ 📊 POSCO 상세 현황                                 │
├────────────────────────────────────────────────────┤
│ [개요] [뉴스 모니터링] [웹훅 이력] [설정]          │
├────────────────────────────────────────────────────┤
│                                                    │
│ (선택된 탭 내용)                                   │
│                                                    │
└────────────────────────────────────────────────────┘
```

#### 탭 1: 개요
```
- 회사 기본 정보
- 웹훅 통계 (그래프)
- 최근 활동
- 빠른 액션
```

#### 탭 2: 뉴스 모니터링
```
- 환율 정보 상태
- 뉴욕 증시 상태
- KOSPI 마감 상태
- 각 모니터별 상세 정보
```

#### 탭 3: 웹훅 이력
```
- 최근 발송 이력 (테이블)
- 필터링 (성공/실패/전체)
- 검색 기능
- 재발송 버튼
```

#### 탭 4: 설정
```
- 웹훅 설정 관리
- API 설정 관리
- 회사 정보 수정
- 회사 삭제
```

---

## 🎯 구현 우선순위

### High (필수)
1. ✅ SystemOverview - 전체 시스템 개요
2. ✅ CompanyStatusGrid - 회사별 현황
3. ✅ 회사 선택 드롭다운
4. ✅ 기본 통계 표시

### Medium (중요)
5. ⭕ CompanyDetailDashboard - 상세 정보
6. ⭕ 탭 구성 (개요/모니터링/이력/설정)
7. ⭕ 실시간 업데이트

### Low (선택)
8. ⭕ 그래프/차트
9. ⭕ 애니메이션 효과
10. ⭕ 다크 모드 최적화

---

## 📊 API 요구사항

### 새로 필요한 API
```python
# dashboard.py

@router.get("/system-overview")
async def get_system_overview():
    """전체 시스템 개요"""
    return {
        "total_companies": 3,
        "active_companies": 2,
        "total_webhooks_sent": 1234,
        "success_rate": 98.5,
        "system_health": "healthy",
        "api_response_time_ms": 2,
        "uptime_seconds": 270000
    }

@router.get("/company-summary")
async def get_company_summary():
    """회사별 요약 정보"""
    return [
        {
            "id": "posco",
            "name": "POSCO",
            "webhook_count": 2,
            "total_sent": 450,
            "success_rate": 99.1,
            "is_active": True
        }
    ]
```

---

## 🎨 디자인 가이드

### 색상 팔레트
```css
/* 주 색상 */
--primary: #3182CE (blue.500)
--primary-hover: #2C5282 (blue.700)

/* 상태 색상 */
--success: #38A169 (green.500)
--warning: #D69E2E (yellow.500)
--error: #E53E3E (red.500)
--info: #3182CE (blue.500)

/* 배경 */
--bg-light: #FFFFFF
--bg-dark: #1A202C
--card-bg: #F7FAFC (gray.50)
```

### 간격
```css
--spacing-xs: 8px
--spacing-sm: 12px
--spacing-md: 16px
--spacing-lg: 24px
--spacing-xl: 32px
```

### 그림자
```css
--shadow-sm: 0 1px 3px rgba(0,0,0,0.1)
--shadow-md: 0 4px 6px rgba(0,0,0,0.1)
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1)
```

---

## 🚀 시작할까요?

### 다음 단계
1. dashboard.py API 생성
2. SystemOverview 컴포넌트 개발
3. CompanyStatusGrid 컴포넌트 개발
4. Dashboard.tsx 리뉴얼

**시작하시겠습니까?** 🎯
