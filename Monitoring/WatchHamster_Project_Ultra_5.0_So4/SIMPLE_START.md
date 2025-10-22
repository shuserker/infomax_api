# 🚀 WatchHamster 간단 실행 가이드

## ⚡ 빠른 실행 (3단계)

### 1️⃣ 터미널 열기
- **Windows**: `Win + R` → `cmd` 입력 → Enter
- 또는 프로젝트 폴더에서 우클릭 → "터미널에서 열기"

### 2️⃣ 프로젝트 폴더로 이동
```cmd
cd Monitoring\WatchHamster_Project_GUI_Tauri
```

### 3️⃣ 서버 실행
```cmd
npm run dev
```

## 🌐 접속하기
서버가 시작되면 자동으로 브라우저가 열리거나, 다음 주소로 접속:
- **http://localhost:1420**

## 🛑 서버 중지하기
터미널에서 `Ctrl + C` 누르기

---

## 🔧 문제 해결

### ❌ "npm이 인식되지 않습니다"
→ `setup.bat` 파일을 먼저 실행하세요

### ❌ "포트가 이미 사용 중"
→ 다른 프로그램이 1420 포트를 사용 중입니다
```cmd
netstat -ano | findstr :1420
taskkill /PID [프로세스ID] /F
```

### ❌ "사이트에 연결할 수 없음"
→ 서버가 완전히 시작될 때까지 30초 정도 기다려주세요

---

## 📱 배치 파일로 실행 (대안)

1. **setup.bat** 더블클릭 (처음 한 번만)
2. **run-dev.bat** 더블클릭 (매번 실행할 때)

---

## 💡 개발자 팁

### 백그라운드 실행
```cmd
start /min npm run dev
```

### 로그 확인
```cmd
npm run dev > server.log 2>&1
```

### 포트 변경
`vite.config.ts`에서 포트 번호 변경 가능

---

**🎉 성공하면 WatchHamster 대시보드가 브라우저에서 열립니다!**