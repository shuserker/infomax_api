#!/bin/bash

# WatchHamster Cursor 프로젝트 시작 스크립트
# 기존 WatchHamster_Project의 모든 핵심 로직을 Tauri GUI에 완전 통합한 버전

echo "🐹 WatchHamster Cursor 프로젝트를 시작합니다..."
echo "================================================"

# 현재 디렉토리 확인
if [ ! -f "package.json" ]; then
    echo "❌ 오류: package.json 파일을 찾을 수 없습니다."
    echo "   WatchHamster_Project_GUI_Tauri_Cursor 디렉토리에서 실행해주세요."
    exit 1
fi

# Python 가상환경 확인 및 생성
if [ ! -d "python-backend/venv_cursor" ]; then
    echo "📦 Python 가상환경을 생성합니다..."
    cd python-backend
    python3 -m venv venv_cursor
    cd ..
fi

# Python 의존성 설치
echo "📦 Python 의존성을 설치합니다..."
cd python-backend
source venv_cursor/bin/activate
pip install -r requirements.txt
cd ..

# Node.js 의존성 설치
echo "📦 Node.js 의존성을 설치합니다..."
npm install

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚙️  환경 변수 파일을 설정합니다..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ .env 파일이 생성되었습니다. 실제 값으로 수정해주세요."
    else
        echo "⚠️  env.example 파일을 찾을 수 없습니다."
    fi
fi

echo ""
echo "🎉 설정이 완료되었습니다!"
echo "================================================"
echo ""
echo "🚀 다음 명령어로 개발 서버를 시작할 수 있습니다:"
echo ""
echo "  백엔드만 시작:"
echo "    cd python-backend && source venv_cursor/bin/activate && python main.py"
echo ""
echo "  프론트엔드만 시작:"
echo "    npm run dev:frontend"
echo ""
echo "  전체 개발 서버 시작:"
echo "    npm run dev"
echo ""
echo "  Tauri 앱 시작:"
echo "    npm run dev:tauri"
echo ""
echo "📚 자세한 내용은 CURSOR_DEVELOPMENT_GUIDE.md를 참고하세요."
echo ""
echo "🔗 접속 URL:"
echo "  - 프론트엔드: http://localhost:1420"
echo "  - 백엔드 API: http://localhost:8000"
echo "  - API 문서: http://localhost:8000/docs"
echo ""
