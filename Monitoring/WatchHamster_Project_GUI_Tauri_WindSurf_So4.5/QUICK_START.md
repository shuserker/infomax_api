# 🚀 WatchHamster 5분 만에 시작하기

> **💡 이 가이드를 따라하면 5분 안에 WatchHamster를 실행할 수 있습니다!**

## 🎯 시작하기 전에

### ✅ 필수 프로그램 설치 (한 번만 하면 됩니다)

| 프로그램 | 용도 | 다운로드 링크 | 확인 방법 |
|---------|------|---------------|-----------|
| **Node.js 18+** | 프론트엔드 실행 | [다운로드](https://nodejs.org/) | `node --version` |
| **Python 3.9+** | 백엔드 실행 | [다운로드](https://www.python.org/) | `python --version` |

> **🔧 개발자가 아니라면?** Rust는 설치하지 않아도 됩니다. 이미 빌드된 실행 파일을 사용하세요!

### 🔍 설치 확인하기
터미널(명령 프롬프트)을 열고 다음 명령어를 입력해보세요:

```bash
node --version    # v18.0.0 이상이어야 합니다
python --version  # Python 3.9.0 이상이어야 합니다
```

**❌ 명령어가 인식되지 않는다면?**
- Node.js나 Python이 제대로 설치되지 않았습니다
- 설치 후 터미널을 다시 열어보세요

## 🚀 3단계로 시작하기

### 1️⃣ 프로젝트 폴더로 이동

**Windows 사용자:**
```cmd
cd Monitoring\WatchHamster_Project_GUI_Tauri
```

**Mac/Linux 사용자:**
```bash
cd Monitoring/WatchHamster_Project_GUI_Tauri
```

### 2️⃣ 필요한 파일들 설치 (처음 한 번만)

**한 번에 모든 것 설치:**
```bash
npm install
```

**Python 백엔드 설치:**
```bash
cd python-backend
pip install -r requirements.txt
cd ..
```

> **⏱️ 시간이 걸려요!** 처음 설치할 때는 2-3분 정도 걸릴 수 있습니다. 커피 한 잔 하고 오세요! ☕

### 3️⃣ WatchHamster 실행하기

**🎉 이제 실행만 하면 됩니다!**
```bash
npm run dev
```

> **✨ 성공!** 터미널에 "Local: http://localhost:1420" 메시지가 보이면 성공입니다!

## 🌟 더 쉬운 방법 (Windows 사용자)

**배치 파일 사용하기:**
1. `setup.bat` 더블클릭 → 자동 설치
2. `run-dev.bat` 더블클릭 → 실행

> **💡 팁:** 바탕화면에 `run-dev.bat` 바로가기를 만들어두면 더 편해요!

## 🌐 WatchHamster 사용하기

### 🎯 접속 방법

실행 후 자동으로 브라우저가 열리지만, 수동으로 접속하려면:

| 서비스 | 주소 | 설명 |
|--------|------|------|
| **🏠 메인 화면** | http://localhost:1420 | **← 여기로 접속하세요!** |
| 🔧 API 문서 | http://localhost:8000/docs | 개발자용 |

### 🖥️ 화면 구성

WatchHamster를 처음 실행하면 다음과 같은 화면을 볼 수 있습니다:

1. **📊 대시보드**: 시스템 상태를 한눈에 확인
2. **⚙️ 서비스 관리**: POSCO 시스템 서비스 제어
3. **📝 로그 뷰어**: 실시간 로그 모니터링
4. **🔧 설정**: 테마, 알림 등 개인화 설정

### 🎨 첫 설정하기

1. **테마 선택**: 우상단 ⚙️ → 테마 → 다크/라이트 모드 선택
2. **알림 설정**: Discord/Slack 웹훅 URL 입력 (선택사항)
3. **언어 설정**: 한국어/English 선택

## 🆘 문제가 생겼나요?

### 😰 자주 발생하는 문제들

#### ❌ "실행이 안 돼요!"

**1. 포트가 이미 사용 중인 경우**
```bash
# 다른 프로그램이 포트를 사용하고 있는지 확인
netstat -an | findstr :1420
```
**해결법**: 다른 프로그램을 종료하거나 컴퓨터를 재시작하세요.

**2. "npm이 인식되지 않습니다"**
- Node.js가 제대로 설치되지 않았습니다
- [Node.js 다시 다운로드](https://nodejs.org/) 후 설치

**3. "python이 인식되지 않습니다"**
- Python이 제대로 설치되지 않았습니다
- [Python 다시 다운로드](https://www.python.org/) 후 설치

#### 🐛 "설치 중 오류가 나요!"

**Python 패키지 설치 오류:**
```bash
# 가상환경을 만들어서 깔끔하게 설치
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 다시 설치
pip install -r python-backend/requirements.txt
```

**Node.js 패키지 설치 오류:**
```bash
# 캐시 정리 후 재설치
npm cache clean --force
npm install
```

#### 🔧 "화면이 이상해요!"

**브라우저 캐시 문제:**
1. `Ctrl + F5` (강제 새로고침)
2. 브라우저 개발자 도구 (F12) → Network 탭 → "Disable cache" 체크

### 🔍 로그 확인하는 법

**문제가 계속 발생한다면:**

1. **터미널 메시지 확인**: `npm run dev` 실행한 터미널 창 확인
2. **브라우저 콘솔 확인**: F12 → Console 탭에서 빨간 오류 메시지 확인
3. **백엔드 로그 확인**: `python-backend/watchhamster-backend.log` 파일 열어보기

## 🎁 실행 파일로 사용하기 (더 쉬운 방법!)

### 💻 설치형 프로그램 원한다면

**개발자가 아니라면 이 방법을 추천합니다:**

1. **릴리스 페이지**에서 운영체제에 맞는 설치 파일 다운로드
   - `WatchHamster-Setup.exe` (Windows)
   - `WatchHamster.dmg` (Mac)
   - `WatchHamster.AppImage` (Linux)

2. **설치 후 바로 사용** - 복잡한 설정 없이 바로 실행!

### 🔨 개발자용 빌드

**직접 실행 파일을 만들고 싶다면:**
```bash
# 데스크톱 앱으로 빌드
npm run build:tauri
```

빌드된 파일 위치: `src-tauri/target/release/`

## 📚 더 자세히 알고 싶다면

| 문서 | 내용 | 대상 |
|------|------|------|
| [사용자 가이드](docs/USER_GUIDE.md) | 모든 기능 사용법 | 👥 모든 사용자 |
| [FAQ](docs/FAQ.md) | 자주 묻는 질문 | ❓ 궁금한 점이 있을 때 |
| [마이그레이션 가이드](docs/MIGRATION_GUIDE.md) | 기존 버전에서 업그레이드 | 🔄 기존 사용자 |
| [개발 가이드](docs/DEVELOPMENT.md) | 코드 수정 및 기여 | 👨‍💻 개발자 |

## 🤝 도움이 필요하다면

### 🔧 빠른 체크

문제가 생기면 먼저 이것부터 해보세요:
```bash
# 백엔드 상태 확인
cd python-backend
python test_backend.py
```

### 📞 연락처

1. **🐛 버그 발견**: GitHub Issues에 신고
2. **💡 기능 제안**: GitHub Discussions에 제안
3. **❓ 사용법 질문**: FAQ 문서 먼저 확인
4. **🚨 긴급 문제**: 개발팀 직접 연락

---

## 🎉 축하합니다!

**WatchHamster 설정이 완료되었습니다!**

이제 다음을 경험해보세요:
- ⚡ **3초 만에 시작**되는 빠른 속도
- 🎨 **현대적인 UI**와 다크/라이트 테마
- 📊 **실시간 모니터링**과 알림
- 🔧 **직관적인 서비스 관리**

**즐거운 모니터링 되세요!** 🚀