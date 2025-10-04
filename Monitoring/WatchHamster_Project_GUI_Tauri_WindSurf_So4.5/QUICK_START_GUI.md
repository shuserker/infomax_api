# 🚀 WatchHamster GUI 빠른 시작 가이드

> **두 가지 모드**: CLI 모드와 GUI 모드를 모두 지원합니다!

## 📋 목차
1. [CLI 모드 (터미널)](#cli-모드-터미널)
2. [GUI 모드 (웹 인터페이스)](#gui-모드-웹-인터페이스)
3. [동시 실행](#동시-실행)

---

## 🖥️ CLI 모드 (터미널)

### 빠른 시작
```bash
cd python-backend

# 대화형 CLI
python3 cli/run_monitor.py

# 24시간 서비스
python3 cli/monitor_watchhamster.py start
```

### 데모 실행
```bash
python3 test_cli_demo.py
```

**특징:**
- ✅ 컬러풀한 터미널 UI
- ✅ 이모지 및 테이블 지원
- ✅ 8가지 모니터링 옵션
- ✅ 백그라운드 서비스

---

## 🌐 GUI 모드 (웹 인터페이스)

### 1단계: 의존성 설치

#### Node.js 의존성
```bash
# 프로젝트 루트에서
npm install
```

#### Python 의존성
```bash
cd python-backend
pip3 install -r requirements.txt
cd ..
```

### 2단계: 개발 서버 실행

#### 방법 1: 자동 실행 (권장)
```bash
npm run dev
```

이 명령은 자동으로:
- ✅ Python FastAPI 백엔드 시작 (포트 8000)
- ✅ React 프론트엔드 시작 (포트 1420)
- ✅ 브라우저 자동 오픈

#### 방법 2: 수동 실행
```bash
# 터미널 1: 백엔드
cd python-backend
python3 main.py

# 터미널 2: 프론트엔드
npm run dev:frontend
```

### 3단계: 브라우저 접속

```
🏠 메인 화면: http://localhost:1420
📚 API 문서: http://localhost:8000/docs
```

### GUI 화면 구성

```
┌─────────────────────────────────────────┐
│  🐹 WatchHamster v3.0                   │
├─────────────────────────────────────────┤
│  📊 Dashboard  │  📈 Services           │
│  📋 Logs       │  ⚙️  Settings          │
├─────────────────────────────────────────┤
│                                         │
│  [실시간 모니터링 상태]                 │
│  ┌───────────────────────────────────┐ │
│  │ 뉴욕마켓워치    ✅ Running        │ │
│  │ 증시마감        ✅ Running        │ │
│  │ 서환마감        ⏹️  Stopped       │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [시스템 리소스]                        │
│  CPU:    [████████░░] 45%              │
│  Memory: [██████████] 62%              │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔄 동시 실행

CLI와 GUI를 동시에 사용할 수 있습니다!

### 시나리오 1: GUI로 모니터링, CLI로 제어
```bash
# 터미널 1: GUI 실행
npm run dev

# 터미널 2: CLI 명령 실행
cd python-backend
python3 cli/monitor_watchhamster.py status
```

### 시나리오 2: 백그라운드 서비스 + GUI 모니터링
```bash
# 1. 24시간 서비스 시작
cd python-backend
python3 cli/monitor_watchhamster.py start

# 2. GUI로 상태 확인
cd ..
npm run dev
```

---

## 🛠️ 개발 모드 옵션

### 프론트엔드만 실행
```bash
npm run dev:frontend
```

### 백엔드만 실행
```bash
npm run dev:backend
# 또는
cd python-backend && python3 main.py
```

### Tauri 데스크톱 앱으로 실행
```bash
npm run dev:tauri
```

---

## 🧪 테스트

### 전체 테스트
```bash
# CLI 테스트
cd python-backend
python3 test_core_components.py
python3 test_ui_components.py
python3 test_monitors_integration.py

# GUI 테스트
cd ..
npm test
npm run test:e2e
```

---

## 📊 포트 정보

| 서비스 | 포트 | URL |
|--------|------|-----|
| React Frontend | 1420 | http://localhost:1420 |
| FastAPI Backend | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| WebSocket | 8000 | ws://localhost:8000/ws |

---

## 🐛 트러블슈팅

### 문제: 포트가 이미 사용 중
```bash
# 포트 확인
lsof -i :1420
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 문제: Node 모듈 오류
```bash
rm -rf node_modules package-lock.json
npm install
```

### 문제: Python 의존성 오류
```bash
cd python-backend
pip3 install --upgrade -r requirements.txt
```

### 문제: 백엔드 연결 실패
```bash
# 백엔드가 실행 중인지 확인
curl http://localhost:8000/health

# 로그 확인
cd python-backend
tail -f logs/watchhamster.log
```

---

## 🎯 추천 워크플로우

### 개발 시
```bash
# 1. GUI 개발 서버 시작
npm run dev

# 2. 브라우저에서 http://localhost:1420 접속

# 3. 코드 수정 시 자동 리로드
```

### 운영 시
```bash
# 1. 백그라운드 서비스 시작
cd python-backend
python3 cli/monitor_watchhamster.py start

# 2. 필요시 GUI로 모니터링
npm run dev

# 3. CLI로 상태 확인
python3 cli/monitor_watchhamster.py status
```

---

## 📚 추가 문서

- **CLI 가이드**: [README_CLI.md](README_CLI.md)
- **API 문서**: http://localhost:8000/docs
- **개발 가이드**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **마이그레이션**: [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)

---

## 🎨 UI 스크린샷

### CLI 모드
```
╔═══════════════════════════════════════════════════════════╗
║           🐹 POSCO WatchHamster v3.0                      ║
╚═══════════════════════════════════════════════════════════╝

메뉴 옵션:
→ 1. 🌐 뉴욕마켓워치 모니터링
  2. 📈 증시마감 모니터링
  3. 💱 서환마감 모니터링
```

### GUI 모드
- 현대적인 웹 인터페이스
- 실시간 차트 및 그래프
- 반응형 디자인
- 다크/라이트 테마

---

## 💡 팁

1. **개발 중**: `npm run dev` 사용 (핫 리로드)
2. **테스트**: CLI 데모로 빠른 확인
3. **운영**: 백그라운드 서비스 + GUI 모니터링
4. **디버깅**: 브라우저 개발자 도구 활용

---

## 🚀 다음 단계

1. ✅ GUI 실행 확인
2. ✅ CLI 모드 테스트
3. ✅ 실제 모니터 연동
4. ✅ Dooray 웹훅 설정
5. ✅ 24시간 안정성 테스트

---

**문제가 있으신가요?** 
- GitHub Issues: [링크]
- 문서: [docs/](docs/)
- 로그: `python-backend/logs/`
