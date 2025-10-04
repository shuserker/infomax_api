# 🐹 WatchHamster Cursor 개발 가이드

## 📋 프로젝트 개요

**WatchHamster_Project_GUI_Tauri_Cursor**는 기존 WatchHamster_Project의 모든 핵심 비즈니스 로직을 Tauri GUI에 완전 통합한 최종 버전입니다.

### 🎯 주요 목표
- ✅ 기존 WatchHamster_Project의 모든 핵심 로직 완전 이식
- ✅ INFOMAX API 실제 연동 (더미 데이터 완전 제거)
- ✅ Dooray 웹훅 실제 전송 (POSCO 뉴스 알림)
- ✅ 실시간 뉴스 모니터링 (exchange-rate, newyork-market-watch, kospi-close)
- ✅ 시스템 리소스 모니터링 (CPU, 메모리, 디스크)
- ✅ Git 상태 모니터링 (브랜치, 커밋, 충돌 상태)

## 🏗️ 프로젝트 구조

```
WatchHamster_Project_GUI_Tauri_Cursor/
├── 📁 src/                          # React + TypeScript 프론트엔드
│   ├── components/                  # UI 컴포넌트들
│   ├── pages/                       # 페이지 컴포넌트들
│   ├── services/                    # API 서비스 레이어
│   └── types/                       # TypeScript 타입 정의
├── 📁 python-backend/               # FastAPI 백엔드
│   ├── core/                        # 핵심 비즈니스 로직 (기존 WatchHamster_Project에서 이식)
│   │   ├── watchhamster_monitor.py  # 메인 모니터링 시스템
│   │   ├── infomax_api_client.py    # INFOMAX API 클라이언트
│   │   ├── news_data_parser.py      # 뉴스 데이터 파싱
│   │   ├── webhook_sender.py        # Dooray 웹훅 전송
│   │   └── ...                      # 기타 핵심 모듈들
│   ├── api/                         # API 엔드포인트들
│   ├── models/                      # Pydantic 모델들
│   └── main.py                      # FastAPI 서버
├── 📁 src-tauri/                    # Tauri 러스트 백엔드
└── 📁 docs/                         # 프로젝트 문서
```

## 🚀 개발 환경 설정

### 1. 필수 요구사항
- **Node.js**: 18.0.0 이상
- **Python**: 3.9 이상
- **Rust**: 최신 안정 버전
- **Tauri CLI**: `npm install -g @tauri-apps/cli`

### 2. 프로젝트 설정

#### 백엔드 설정
```bash
cd python-backend

# 가상환경 생성 및 활성화
python3 -m venv venv_cursor
source venv_cursor/bin/activate  # macOS/Linux
# 또는
venv_cursor\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

#### 프론트엔드 설정
```bash
# 루트 디렉토리에서
npm install
```

### 3. 환경 변수 설정
```bash
# env.example을 .env로 복사
cp env.example .env

# .env 파일을 편집하여 실제 값으로 수정
# - INFOMAX API 인증 정보
# - Dooray 웹훅 URL
# - 기타 설정값들
```

## 🎯 개발 우선순위

### Phase 1: 핵심 로직 완전 이식 (1-2주)
1. **기존 core 모듈들 완전 이식**
   - `watchhamster_monitor.py` → `backend/core/`
   - `news_data_parser.py` → `backend/core/`
   - `infomax_api_client.py` → `backend/core/`
   - `api_connection_manager.py` → `backend/core/`

2. **실제 API 연동 구현**
   - INFOMAX API 실제 호출
   - Dooray 웹훅 실제 전송
   - 하드코딩된 더미값 완전 제거

### Phase 2: 실시간 통신 및 UI 통합 (1주)
1. **WebSocket과 기존 모니터링 로직 통합**
2. **프론트엔드에서 실제 데이터 표시**
3. **실시간 상태 업데이트 구현**

### Phase 3: 안정성 및 최적화 (1주)
1. **오류 처리 및 복구 시스템**
2. **성능 최적화**
3. **설정 관리 완성**

## 🔧 개발 명령어

### 백엔드 개발
```bash
cd python-backend
source venv_cursor/bin/activate
python main.py
```

### 프론트엔드 개발
```bash
npm run dev:frontend
```

### 전체 개발 서버
```bash
npm run dev
```

### Tauri 개발
```bash
npm run dev:tauri
```

## 📊 핵심 모듈 설명

### 1. WatchHamsterMonitor
- **위치**: `python-backend/core/watchhamster_monitor.py`
- **기능**: 전체 시스템 모니터링 및 관리
- **주요 메서드**:
  - `start_monitoring()`: 모니터링 시작
  - `get_system_status()`: 시스템 상태 조회
  - `check_processes()`: 프로세스 상태 체크

### 2. InfomaxAPIClient
- **위치**: `python-backend/core/infomax_api_client.py`
- **기능**: INFOMAX API 연동
- **주요 메서드**:
  - `fetch_news_data()`: 뉴스 데이터 조회
  - `health_check()`: API 연결 상태 확인

### 3. NewsDataParser
- **위치**: `python-backend/core/news_data_parser.py`
- **기능**: 뉴스 데이터 파싱 및 상태 판단
- **주요 메서드**:
  - `parse_news_data()`: 뉴스 데이터 파싱
  - `determine_news_status()`: 뉴스 상태 판단

### 4. DoorayWebhookSender
- **위치**: `python-backend/core/webhook_sender.py`
- **기능**: Dooray 웹훅 전송
- **주요 메서드**:
  - `send_posco_news_alert()`: POSCO 뉴스 알림 전송
  - `send_system_status_report()`: 시스템 상태 보고서 전송

## 🧪 테스트

### 백엔드 테스트
```bash
cd python-backend
source venv_cursor/bin/activate
python -m pytest tests/
```

### 프론트엔드 테스트
```bash
npm test
```

### 통합 테스트
```bash
npm run test:integration
```

## 🚨 주의사항

### 1. 더미 데이터 제거
- 모든 하드코딩된 더미값을 실제 데이터로 교체
- 실제 API 호출 및 웹훅 전송 구현

### 2. 인터페이스 호환성
- 기존 모듈의 생성자 및 메서드 시그니처 유지
- 반환 타입 및 데이터 구조 일치 확인

### 3. 설정 관리
- 환경변수 및 설정 파일을 통한 설정 관리
- 민감한 정보(API 키, 웹훅 URL) 보안 처리

## 📚 참고 자료

- [기존 WatchHamster_Project 문서](../WatchHamster_Project/docs/)
- [요구사항 문서](../.kiro/specs/watchhamster-business-logic-implementation/requirements.md)
- [설계 문서](../.kiro/specs/watchhamster-business-logic-implementation/design.md)
- [작업 계획](../.kiro/specs/watchhamster-business-logic-implementation/tasks.md)

## 🤝 기여 가이드

1. **브랜치 전략**: `main` 브랜치에서 개발, `publish` 브랜치로 배포
2. **커밋 메시지**: 명확하고 구체적인 커밋 메시지 작성
3. **코드 리뷰**: 모든 변경사항에 대한 코드 리뷰 필수
4. **테스트**: 새로운 기능 추가 시 테스트 코드 작성

## 📞 지원 및 문의

- **개발팀**: POSCO WatchHamster 개발팀
- **이메일**: watchhamster@posco.com
- **문서**: [API 참조 문서](docs/API_REFERENCE.md)
