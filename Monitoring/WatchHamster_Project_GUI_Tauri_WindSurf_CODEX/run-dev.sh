#!/bin/bash

# WatchHamster 통합 개발 서버 실행 스크립트
echo "🚀 WatchHamster 개발 서버를 시작합니다..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Python 의존성 확인 및 설치
echo "🔍 Python 의존성을 확인합니다..."
cd python-backend

if [ ! -d "venv" ]; then
    echo "⚠️  Python 가상환경이 없습니다. 빠른 설정을 실행합니다..."
    cd ..
    ./quick-setup.sh
    cd python-backend
fi

# 가상환경 활성화
source venv/bin/activate

# 누락된 패키지 설치
echo "📦 누락된 패키지를 설치합니다..."
pip install pydantic-settings==2.0.3 requests==2.31.0 --quiet

# 프로젝트 루트로 돌아가기
cd "$PROJECT_DIR"

# Node.js 의존성 확인
if [ ! -d "node_modules" ]; then
    echo "📦 Node.js 의존성을 설치합니다..."
    npm install
fi

# 개발 서버 시작
echo "🎯 통합 개발 서버를 시작합니다..."
npm run dev