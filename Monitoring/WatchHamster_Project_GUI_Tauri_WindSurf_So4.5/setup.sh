#!/bin/bash

# WatchHamster 프로젝트 초기 설정 스크립트
echo "🔧 WatchHamster 프로젝트 초기 설정을 시작합니다..."

# 현재 디렉토리 확인
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 프로젝트 디렉토리: $PROJECT_DIR"

# Node.js 버전 확인
echo "🔍 Node.js 버전 확인 중..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js 버전: $NODE_VERSION"
else
    echo "❌ Node.js가 설치되어 있지 않습니다."
    echo "🔗 Node.js를 설치하세요: https://nodejs.org/"
    exit 1
fi

# Python 버전 확인
echo "🔍 Python 버전 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python 버전: $PYTHON_VERSION"
else
    echo "❌ Python3가 설치되어 있지 않습니다."
    echo "🔗 Python을 설치하세요: https://python.org/"
    exit 1
fi

# Node.js 의존성 설치
echo "📦 Node.js 의존성을 설치합니다..."
cd "$PROJECT_DIR"
npm install
if [ $? -eq 0 ]; then
    echo "✅ Node.js 의존성 설치 완료"
else
    echo "❌ Node.js 의존성 설치 실패"
    exit 1
fi

# Python 가상환경 설정
echo "🐍 Python 가상환경을 설정합니다..."
cd "$PROJECT_DIR/python-backend"

# 기존 가상환경 제거 (있다면)
if [ -d "venv" ]; then
    echo "🗑️  기존 가상환경을 제거합니다..."
    rm -rf venv
fi

# 새 가상환경 생성
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo "✅ Python 가상환경 생성 완료"
else
    echo "❌ Python 가상환경 생성 실패"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate
echo "✅ Python 가상환경 활성화됨"

# Python 의존성 설치
echo "📦 Python 의존성을 설치합니다..."

# pip 업그레이드
pip install --upgrade pip

# 호환성 문제 해결을 위한 단계별 설치
echo "🔧 호환성 문제 해결을 위해 단계별로 설치합니다..."

# 1단계: 기본 패키지 설치
echo "1️⃣ 기본 패키지 설치 중..."
pip install wheel setuptools

# 2단계: 안정적인 버전의 pydantic 설치
echo "2️⃣ Pydantic 설치 중..."
pip install "pydantic==1.10.13"

# 3단계: FastAPI 관련 패키지 설치
echo "3️⃣ FastAPI 관련 패키지 설치 중..."
pip install "fastapi==0.104.1"
pip install "uvicorn[standard]==0.24.0"

# 4단계: 기타 필수 패키지 설치
echo "4️⃣ 기타 필수 패키지 설치 중..."
pip install psutil==5.9.6
pip install python-multipart==0.0.6
pip install aiofiles==23.2.1
pip install python-dotenv==1.0.0
pip install httpx==0.25.2
pip install websockets==12.0

# 설치 확인
if python -c "import fastapi, uvicorn, psutil" 2>/dev/null; then
    echo "✅ Python 의존성 설치 완료"
else
    echo "❌ Python 의존성 설치 실패"
    echo "🔧 대안 방법을 시도합니다..."
    
    # 대안: 최소한의 패키지만 설치
    pip install fastapi uvicorn psutil python-multipart aiofiles --no-deps --force-reinstall
    echo "⚠️  최소한의 패키지만 설치되었습니다. 일부 기능이 제한될 수 있습니다."
fi

# 스크립트 실행 권한 부여
echo "🔐 스크립트 실행 권한을 설정합니다..."
cd "$PROJECT_DIR"
chmod +x start.sh
chmod +x setup.sh
echo "✅ 스크립트 실행 권한 설정 완료"

# 설정 완료
echo ""
echo "🎉 WatchHamster 프로젝트 초기 설정이 완료되었습니다!"
echo ""
echo "📋 다음 명령어로 프로젝트를 시작할 수 있습니다:"
echo "   ./start.sh"
echo ""
echo "또는 수동으로 시작하려면:"
echo "1. 백엔드: cd python-backend && source venv/bin/activate && python main.py"
echo "2. 프론트엔드: npm run dev:frontend"
echo ""
echo "🌐 브라우저에서 http://localhost:1420 으로 접속하세요"