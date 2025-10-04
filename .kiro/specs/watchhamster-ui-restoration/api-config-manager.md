# API 설정 관리 시스템 구축

## 📋 프로젝트 개요

**목표**: 각 모니터의 API 호출 설정을 GUI에서 관리/수정/테스트할 수 있는 통합 관리 시스템 구축

**배경**: 
- 현재 API 호출 설정이 코드에 하드코딩되어 있음
- 각 모니터(kospi-close, newyork-market-watch, exchange-rate)의 호출 조건, 파라미터, 인증 정보 등을 동적으로 관리 필요
- 실시간 테스트 및 검증 기능 필요

---

## 🎯 주요 기능

### 1. API 설정 관리
- **모니터별 설정**
  - API 엔드포인트 URL
  - HTTP 메서드 (GET, POST)
  - 인증 방식 (Bearer Token, API Key, Basic Auth)
  - 요청 헤더
  - 쿼리 파라미터
  - 요청 바디 (POST인 경우)

### 2. 호출 조건 설정
- **스케줄링**
  - 실행 간격 (분 단위)
  - 실행 시간대 (예: 09:00-18:00)
  - 요일별 실행 여부
  - 공휴일 제외 옵션

- **조건부 실행**
  - 이전 실행 결과에 따른 재시도
  - 실패 시 재시도 횟수
  - 재시도 간격

### 3. 데이터 파싱 설정
- **파싱 규칙**
  - JSON Path 또는 XPath
  - 정규표현식 패턴
  - 데이터 변환 로직
  - 필수 필드 검증

### 4. 웹훅 설정
- **Dooray 웹훅**
  - 웹훅 URL
  - 메시지 템플릿
  - 발송 조건 (변경 감지 시, 항상, 오류 시)
  - 타임아웃 설정

### 5. 실시간 테스트
- **테스트 실행**
  - 설정 검증
  - API 호출 테스트
  - 파싱 결과 미리보기
  - 웹훅 테스트 발송

---

## 🏗️ 시스템 아키텍처

### Backend (Python FastAPI)

```
api/
├── config_manager.py          # 설정 관리 API
│   ├── GET  /api/config/monitors              # 모든 모니터 설정 조회
│   ├── GET  /api/config/monitors/{name}       # 특정 모니터 설정 조회
│   ├── PUT  /api/config/monitors/{name}       # 모니터 설정 수정
│   ├── POST /api/config/monitors/{name}/test  # 설정 테스트
│   └── POST /api/config/monitors/{name}/validate # 설정 검증
│
├── schedule_manager.py        # 스케줄 관리 API
│   ├── GET  /api/schedule/monitors/{name}     # 스케줄 조회
│   ├── PUT  /api/schedule/monitors/{name}     # 스케줄 수정
│   └── POST /api/schedule/monitors/{name}/preview # 다음 실행 시간 미리보기
│
└── template_manager.py        # 템플릿 관리 API
    ├── GET  /api/templates/webhook            # 웹훅 템플릿 목록
    ├── POST /api/templates/webhook            # 템플릿 생성
    └── PUT  /api/templates/webhook/{id}       # 템플릿 수정

config/
├── monitors/
│   ├── kospi-close.json       # 코스피 설정
│   ├── newyork-market-watch.json
│   └── exchange-rate.json
└── templates/
    └── dooray-webhook.json    # 웹훅 템플릿
```

### Frontend (React + TypeScript)

```
src/
├── pages/
│   └── ConfigManager.tsx      # 설정 관리 메인 페이지
│
├── components/
│   └── ConfigManager/
│       ├── MonitorConfigPanel.tsx      # 모니터 설정 패널
│       ├── ApiEndpointEditor.tsx       # API 엔드포인트 편집기
│       ├── ScheduleEditor.tsx          # 스케줄 편집기
│       ├── ParsingRuleEditor.tsx       # 파싱 규칙 편집기
│       ├── WebhookTemplateEditor.tsx   # 웹훅 템플릿 편집기
│       └── ConfigTestPanel.tsx         # 테스트 패널
│
└── services/
    └── configService.ts        # 설정 관리 API 서비스
```

---

## 📊 데이터 모델

### MonitorConfig
```typescript
interface MonitorConfig {
  name: string                    // 모니터 이름
  enabled: boolean                // 활성화 여부
  
  // API 설정
  api: {
    endpoint: string              // API URL
    method: 'GET' | 'POST'
    auth: {
      type: 'bearer' | 'apikey' | 'basic' | 'none'
      token?: string
      apiKey?: string
      username?: string
      password?: string
    }
    headers: Record<string, string>
    params: Record<string, any>
    body?: Record<string, any>
    timeout: number               // 초 단위
  }
  
  // 스케줄 설정
  schedule: {
    interval: number              // 분 단위
    timeRange?: {
      start: string               // HH:mm
      end: string                 // HH:mm
    }
    daysOfWeek?: number[]         // 0-6 (일-토)
    excludeHolidays: boolean
  }
  
  // 재시도 설정
  retry: {
    maxAttempts: number
    delayMs: number
    backoff: 'linear' | 'exponential'
  }
  
  // 파싱 설정
  parsing: {
    type: 'json' | 'html' | 'xml'
    rules: ParsingRule[]
    validation: ValidationRule[]
  }
  
  // 웹훅 설정
  webhook: {
    enabled: boolean
    url: string
    templateId: string
    condition: 'always' | 'on_change' | 'on_error'
    timeout: number
  }
}
```

---

## 🎨 UI 디자인

### 메인 화면
```
┌─────────────────────────────────────────────────────────┐
│  ⚙️ API 설정 관리                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [모니터 목록]                    [+ 새 모니터 추가]   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📊 kospi-close              [활성화] [편집] [테스트]│
│  │   API: https://...kospi-close                    │
│  │   스케줄: 5분마다 (09:00-18:00)                  │
│  │   마지막 실행: 2025-10-04 13:00:00              │
│  │   상태: ✅ 정상                                  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📈 newyork-market-watch     [활성화] [편집] [테스트]│
│  │   API: https://...newyork                        │
│  │   스케줄: 10분마다 (22:00-05:00)                │
│  │   마지막 실행: 2025-10-04 12:50:00              │
│  │   상태: ✅ 정상                                  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 편집 화면
```
┌─────────────────────────────────────────────────────────┐
│  ⚙️ kospi-close 설정                        [저장] [취소]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [기본 정보] [API 설정] [스케줄] [파싱] [웹훅]         │
│                                                         │
│  ┌─ API 설정 ─────────────────────────────────────┐   │
│  │                                                 │   │
│  │  엔드포인트 URL                                 │   │
│  │  [https://global-api.einfomax.co.kr/...]       │   │
│  │                                                 │   │
│  │  HTTP 메서드                                    │   │
│  │  ( ) GET  (•) POST                             │   │
│  │                                                 │   │
│  │  인증 방식                                      │   │
│  │  [Bearer Token ▼]                              │   │
│  │                                                 │   │
│  │  토큰                                           │   │
│  │  [****-****-****-****]           [표시] [테스트]│   │
│  │                                                 │   │
│  │  요청 헤더                                      │   │
│  │  ┌───────────────────────────────────────────┐ │   │
│  │  │ Content-Type: application/json           │ │   │
│  │  │ Accept: application/json                 │ │   │
│  │  │ [+ 헤더 추가]                            │ │   │
│  │  └───────────────────────────────────────────┘ │   │
│  │                                                 │   │
│  │  쿼리 파라미터                                  │   │
│  │  ┌───────────────────────────────────────────┐ │   │
│  │  │ date: {today}                            │ │   │
│  │  │ market: kospi                            │ │   │
│  │  │ [+ 파라미터 추가]                        │ │   │
│  │  └───────────────────────────────────────────┘ │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [API 호출 테스트]                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 구현 계획

### Phase 1: Backend API 구축 (2-3일)
- [ ] 설정 파일 구조 설계
- [ ] Config Manager API 구현
- [ ] Schedule Manager API 구현
- [ ] Template Manager API 구현
- [ ] 설정 검증 로직 구현

### Phase 2: Frontend UI 구축 (3-4일)
- [ ] ConfigManager 페이지 생성
- [ ] MonitorConfigPanel 컴포넌트
- [ ] ApiEndpointEditor 컴포넌트
- [ ] ScheduleEditor 컴포넌트
- [ ] ParsingRuleEditor 컴포넌트
- [ ] WebhookTemplateEditor 컴포넌트

### Phase 3: 테스트 기능 구현 (1-2일)
- [ ] API 호출 테스트
- [ ] 파싱 결과 미리보기
- [ ] 웹훅 테스트 발송
- [ ] 설정 검증

### Phase 4: 통합 및 테스트 (1-2일)
- [ ] 기존 모니터 시스템과 통합
- [ ] 설정 마이그레이션
- [ ] 전체 시스템 테스트
- [ ] 문서화

---

## 💡 주요 기능 상세

### 1. 동적 파라미터 지원
```json
{
  "params": {
    "date": "{today}",           // 오늘 날짜
    "yesterday": "{yesterday}",  // 어제 날짜
    "timestamp": "{timestamp}",  // 현재 타임스탬프
    "custom": "{env.API_KEY}"    // 환경 변수
  }
}
```

### 2. 조건부 실행
```json
{
  "conditions": [
    {
      "type": "time_range",
      "start": "09:00",
      "end": "18:00"
    },
    {
      "type": "day_of_week",
      "days": [1, 2, 3, 4, 5]  // 월-금
    },
    {
      "type": "previous_result",
      "status": "failed",
      "action": "retry"
    }
  ]
}
```

### 3. 파싱 규칙
```json
{
  "parsing": {
    "type": "json",
    "rules": [
      {
        "field": "title",
        "path": "$.data.title",
        "required": true
      },
      {
        "field": "indices",
        "path": "$.data.indices[*]",
        "transform": "array"
      }
    ]
  }
}
```

---

## 🔒 보안 고려사항

1. **인증 정보 암호화**
   - API 토큰, 비밀번호 암호화 저장
   - 환경 변수 또는 Secrets Manager 사용

2. **접근 제어**
   - 설정 수정 권한 관리
   - 감사 로그 기록

3. **검증**
   - 입력 값 검증
   - SQL Injection, XSS 방지

---

## 📈 성공 지표

- ✅ 모든 모니터 설정을 GUI에서 관리 가능
- ✅ 코드 수정 없이 새 모니터 추가 가능
- ✅ 실시간 테스트 및 검증 가능
- ✅ 설정 변경 이력 추적 가능
- ✅ 평균 설정 변경 시간 < 5분

---

## 🎯 다음 단계

1. **Phase 1 시작**: Backend API 구축
2. **설정 파일 스키마 정의**
3. **Config Manager API 구현**

준비되면 시작하시겠습니까?
