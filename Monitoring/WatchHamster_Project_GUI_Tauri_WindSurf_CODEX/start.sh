#!/bin/bash

# WatchHamster 프로젝트 시작 스크립트
echo "🚀 WatchHamster 프로젝트를 시작합니다..."

# 현재 디렉토리 확인
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 프로젝트 디렉토리: $PROJECT_DIR"

# 백엔드 서버 시작 함수
start_backend() {
    echo "🔧 백엔드 서버를 시작합니다..."
    cd "$PROJECT_DIR/python-backend"
    
    # 가상환경 활성화
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Python 가상환경 활성화됨"
    else
        echo "❌ Python 가상환경을 찾을 수 없습니다. 먼저 setup.sh를 실행하세요."
        exit 1
    fi
    
    # 백엔드 서버 시작
    echo "🚀 백엔드 서버 시작 중... (포트: 8000)"
    python main.py &
    BACKEND_PID=$!
    echo "✅ 백엔드 서버 시작됨 (PID: $BACKEND_PID)"
}

# 프론트엔드 서버 시작 함수
start_frontend() {
    echo "📱 프론트엔드 서버를 시작합니다..."
    cd "$PROJECT_DIR"
    
    # Node.js 의존성 확인
    if [ ! -d "node_modules" ]; then
        echo "📦 Node.js 의존성을 설치합니다..."
        npm install
    fi
    
    # 프론트엔드 서버 시작
    echo "🚀 프론트엔드 서버 시작 중... (포트: 1420)"
    npm run dev:frontend &
    FRONTEND_PID=$!
    echo "✅ 프론트엔드 서버 시작됨 (PID: $FRONTEND_PID)"
}

# 서버 상태 확인 함수
check_servers() {
    echo "🔍 서버 상태를 확인합니다..."
    
    # 백엔드 서버 확인
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ 백엔드 서버: 정상 작동 중"
    else
        echo "❌ 백엔드 서버: 응답 없음"
    fi
    
    # 프론트엔드 서버 확인
    if curl -s http://localhost:1420 > /dev/null; then
        echo "✅ 프론트엔드 서버: 정상 작동 중"
    else
        echo "❌ 프론트엔드 서버: 응답 없음"
    fi
}

# 정리 함수
cleanup() {
    echo "🛑 서버를 종료합니다..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 백엔드 서버 종료됨"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 프론트엔드 서버 종료됨"
    fi
    exit 0
}

# 시그널 핸들러 설정
trap cleanup SIGINT SIGTERM

# 메인 실행
echo "🎯 서버들을 시작합니다..."
start_backend
sleep 3
start_frontend
sleep 5

# 서버 상태 확인
check_servers

echo ""
echo "🎉 모든 서버가 시작되었습니다!"
echo "📱 프론트엔드: http://localhost:1420"
echo "🔧 백엔드 API: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo ""
echo "🌐 브라우저를 자동으로 엽니다..."
sleep 2
open http://localhost:1420

echo "⏹️  종료하려면 Ctrl+C를 누르세요"

# 무한 대기
while true; do
    sleep 1
done