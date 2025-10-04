# 🏗️ 아키텍처 비교: 현재 vs 제안

## 📊 현재 구조 (POSCO 전용)

### 백엔드
```
python-backend/
├── api/
│   ├── posco.py              # POSCO 전용 API
│   ├── webhook_manager.py    # POSCO 웹훅 하드코딩
│   ├── services.py           # POSCO 서비스만
│   └── ...
│
├── core/
│   ├── posco_original/       # POSCO 전용 로직
│   │   ├── webhook_sender.py (POSCO URL 하드코딩)
│   │   └── news_message_generator.py (POSCO 메시지)
│   │
│   └── watchhamster_original/ # 공통 로직
│
└── 문제점:
    ❌ 새 회사 추가 시 코드 전체 수정 필요
    ❌ 회사별 설정 분리 불가
    ❌ 확장성 제로
```

### 프론트엔드
```
src/
├── pages/
│   ├── Dashboard.tsx         # POSCO 전용
│   ├── Services.tsx          # POSCO 서비스만
│   ├── WebhookManager.tsx    # POSCO 웹훅만
│   └── ...
│
└── 문제점:
    ❌ 회사 선택 불가
    ❌ 회사별 필터링 불가
    ❌ UI가 POSCO에 종속
```

---

## 🎯 제안 구조 (멀티 테넌트)

### 백엔드
```
python-backend/
├── api/
│   ├── companies.py          # 회사 관리 (NEW)
│   ├── webhooks.py           # 회사별 웹훅
│   ├── services.py           # 회사별 서비스
│   └── ...
│
├── core/
│   ├── companies/            # 회사별 로직 (NEW)
│   │   ├── base/             # 추상 베이스 클래스
│   │   │   ├── base_webhook_sender.py
│   │   │   ├── base_message_generator.py
│   │   │   └── base_monitor.py
│   │   │
│   │   ├── posco/            # POSCO 구현
│   │   │   ├── posco_webhook_sender.py
│   │   │   ├── posco_message_generator.py
│   │   │   └── posco_config.json
│   │   │
│   │   ├── company2/         # 회사2 구현
│   │   │   └── ...
│   │   │
│   │   └── factory.py        # 팩토리 패턴
│   │
│   └── watchhamster_original/ # 공통 로직
│
├── database/                 # 데이터베이스 (NEW)
│   ├── models.py
│   ├── repositories.py
│   └── migrations/
│
└── 장점:
    ✅ 회사 추가 시 config만 추가
    ✅ 회사별 독립 운영
    ✅ 무한 확장 가능
```

### 프론트엔드
```
src/
├── components/
│   ├── CompanySelector/      # 회사 선택 (NEW)
│   ├── CompanyManager/       # 회사 관리 (NEW)
│   └── ...
│
├── pages/
│   ├── GlobalDashboard.tsx   # 전체 대시보드 (NEW)
│   ├── CompanyDashboard.tsx  # 회사별 대시보드 (NEW)
│   ├── CompanyManager.tsx    # 회사 관리 (NEW)
│   ├── WebhookManager.tsx    # 회사 선택 추가
│   └── Services.tsx          # 회사 선택 추가
│
└── 장점:
    ✅ 회사 전환 즉시 가능
    ✅ 회사별 필터링
    ✅ 통합 뷰 + 개별 뷰
```

---

## 🔄 API 엔드포인트 비교

### 현재 (POSCO 전용)
```
POST /api/webhook-manager/send/test
POST /api/webhook-manager/send/business-day-comparison
GET  /api/webhook-manager/logs
GET  /api/webhook-manager/stats

POST /api/posco/services/start
GET  /api/posco/services/status

문제점:
❌ POSCO만 지원
❌ 다른 회사 추가 불가
```

### 제안 (멀티 테넌트)
```
# 회사 관리
POST /api/companies                           # 회사 등록
GET  /api/companies                           # 회사 목록
GET  /api/companies/{company_id}              # 회사 상세
PUT  /api/companies/{company_id}              # 회사 수정
DELETE /api/companies/{company_id}            # 회사 삭제

# 회사별 웹훅
POST /api/companies/{company_id}/webhooks/send/test
POST /api/companies/{company_id}/webhooks/send/business-day-comparison
GET  /api/companies/{company_id}/webhooks/logs
GET  /api/companies/{company_id}/webhooks/stats

# 회사별 서비스
POST /api/companies/{company_id}/services/start
POST /api/companies/{company_id}/services/stop
GET  /api/companies/{company_id}/services/status

# 회사별 뉴스
GET  /api/companies/{company_id}/news/latest
GET  /api/companies/{company_id}/news/history

장점:
✅ 무한 회사 추가 가능
✅ 회사별 독립 운영
✅ RESTful 구조
```

---

## 📋 메뉴 구조 비교

### 현재 메뉴
```
🏠 대시보드 (POSCO 전용)
🔧 서비스 관리 (POSCO 전용)
⚙️ API 설정 (POSCO 전용)
📬 웹훅 관리 (POSCO 전용)
📝 로그 뷰어 (전체)
⚙️ 설정 (시스템)

문제점:
❌ 회사 선택 불가
❌ 다른 회사 추가 시 메뉴 복잡해짐
```

### 제안 메뉴 (옵션 A: 회사 선택 방식)
```
🏠 전체 대시보드 (모든 회사 통합)
🏢 회사 관리 (회사 추가/수정/삭제)
─────────────────────────────────
회사 선택: [🏭 POSCO ▼]
─────────────────────────────────
📊 대시보드 (선택된 회사)
🔧 서비스 관리 (선택된 회사)
📬 웹훅 관리 (선택된 회사)
📰 뉴스 모니터 (선택된 회사)
─────────────────────────────────
📝 로그 뷰어 (전체, 회사별 필터)
⚙️ 설정 (시스템)

장점:
✅ 깔끔한 메뉴
✅ 회사 전환 쉬움
✅ 컨텍스트 명확
```

### 제안 메뉴 (옵션 B: 회사별 서브메뉴)
```
🏠 전체 대시보드
🏢 회사 관리
─────────────────────────────────
📊 회사별 대시보드
  ├─ 🏭 POSCO
  ├─ 🏢 회사2
  └─ 🏢 회사3
─────────────────────────────────
📬 웹훅 관리 (회사 선택 드롭다운)
🔧 서비스 관리 (회사 선택 드롭다운)
📝 로그 뷰어 (회사별 필터)
⚙️ 설정

장점:
✅ 회사별 빠른 접근
✅ 시각적으로 명확
단점:
⚠️ 회사 많아지면 메뉴 길어짐
```

### 제안 메뉴 (옵션 C: 탭 방식)
```
🏠 대시보드
  [전체] [POSCO] [회사2] [회사3]
  
🏢 회사 관리

📬 웹훅 관리
  [POSCO] [회사2] [회사3]
  
🔧 서비스 관리
  [POSCO] [회사2] [회사3]

📝 로그 뷰어
⚙️ 설정

장점:
✅ 페이지 내에서 회사 전환
✅ 메뉴 간결
단점:
⚠️ 페이지마다 탭 반복
```

---

## 💡 권장 구조 (옵션 A + 개선)

### 최종 권장 메뉴
```
┌─────────────────────────────────┐
│ 🏠 전체 대시보드                │ ← 모든 회사 통합 뷰
├─────────────────────────────────┤
│ 🏢 회사 관리                    │ ← 회사 추가/수정/삭제
├─────────────────────────────────┤
│ 회사 선택: [🏭 POSCO ▼]        │ ← 전역 회사 선택
├─────────────────────────────────┤
│ 📊 대시보드                     │ ← 선택된 회사 대시보드
│ 📬 웹훅 관리                    │ ← 선택된 회사 웹훅
│ 🔧 서비스 관리                  │ ← 선택된 회사 서비스
│ 📰 뉴스 모니터                  │ ← 선택된 회사 뉴스
├─────────────────────────────────┤
│ 📝 로그 뷰어 (전체)             │ ← 회사별 필터링 가능
│ ⚙️ 설정                        │ ← 시스템 + 회사별 설정
└─────────────────────────────────┘
```

### 특징
1. **전역 회사 선택기**: 한 번 선택하면 모든 페이지에 적용
2. **전체 대시보드**: 모든 회사 한눈에
3. **회사별 페이지**: 선택된 회사만 표시
4. **로그는 통합**: 하지만 회사별 필터링 가능

---

## 🎯 구현 우선순위 제안

### Week 1: 기반 구축
1. 데이터베이스 스키마 생성
2. Company 모델 및 API 구현
3. CompanySelector 컴포넌트
4. 회사 관리 페이지

### Week 2: 웹훅 시스템 개편
5. BaseWebhookSender 추상화
6. 회사별 웹훅 설정
7. 웹훅 관리 페이지 개편
8. 로그 시스템에 company_id 추가

### Week 3: 서비스 시스템 개편
9. 회사별 서비스 관리
10. 서비스 관리 페이지 개편
11. 대시보드 개편

### Week 4: 마이그레이션 및 테스트
12. POSCO 데이터 마이그레이션
13. 전체 테스트
14. 문서화

---

## ❓ 결정 필요 사항

### 1. 데이터베이스
- [ ] SQLite (간단, 파일 기반)
- [ ] PostgreSQL (강력, 프로덕션 권장)
- [ ] MongoDB (NoSQL, 유연)

### 2. 메뉴 구조
- [ ] 옵션 A: 전역 회사 선택 (권장)
- [ ] 옵션 B: 회사별 서브메뉴
- [ ] 옵션 C: 탭 방식

### 3. 마이그레이션 전략
- [ ] 즉시 시작 (기존 시스템 중단 없이)
- [ ] 새 회사 추가 후 시작
- [ ] 단계적 마이그레이션

### 4. 회사 추가 계획
- [ ] 회사 이름 목록
- [ ] 각 회사별 요구사항
- [ ] 우선순위

---

## 📌 다음 액션

1. **이 계획 검토 및 승인**
2. **데이터베이스 선택**
3. **메뉴 구조 선택**
4. **구현 시작 일정 확정**
5. **첫 번째 추가할 회사 확정**
