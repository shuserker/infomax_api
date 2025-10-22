# 🎯 여기서 시작하세요!

## 🚀 가장 쉬운 방법 (추천!)

### Windows 사용자
1. `setup.bat` 더블클릭 → 자동 설치
2. `run-dev.bat` 더블클릭 → 실행
3. 브라우저에서 http://localhost:1420 접속

### Mac/Linux 사용자
```bash
# 실행 권한 부여 (한 번만)
chmod +x setup.sh run-dev.sh stop.sh

# 설치
./setup.sh

# 실행
./run-dev.sh
```

## 🔧 수동 설치 (개발자용)

```bash
# 1. 패키지 설치
npm install
cd python-backend && pip install -r requirements.txt && cd ..

# 2. 실행
npm run dev
```

## 📱 접속 주소

- **메인 화면**: http://localhost:1420
- **API 문서**: http://localhost:8000/docs

## 🆘 문제 해결

### ❌ 실행이 안 될 때
1. Node.js 18+ 설치: https://nodejs.org
2. Python 3.9+ 설치: https://python.org
3. `setup.bat` (Windows) 또는 `./setup.sh` (Mac/Linux) 실행

### 🔍 더 자세한 도움말
- [빠른 시작 가이드](QUICK_START.md) - 상세한 설치 방법
- [사용자 가이드](docs/USER_GUIDE.md) - 모든 기능 사용법
- [FAQ](docs/FAQ.md) - 자주 묻는 질문

---

**🎉 5분 만에 시작할 수 있습니다!**