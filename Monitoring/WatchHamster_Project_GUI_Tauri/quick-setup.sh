#!/bin/bash

# WatchHamster 빠른 설정 스크립트 (Python 3.13 호환성 문제 해결)
echo "⚡ WatchHamster 빠른 설정을 시작합니다..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 프로젝트 디렉토리: $PROJECT_DIR"

# 기존 가상환경 제거
echo "🗑️  기존 Python 가상환경을 정리합니다..."
cd "$PROJECT_DIR/python-backend"
rm -rf venv

# Python 3.11 또는 3.12 사용 권장
echo "🐍 Python 버전을 확인합니다..."
PYTHON_CMD=""

# Python 3.12 확인
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "✅ Python 3.12 발견"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✅ Python 3.11 발견"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "✅ Python 3.10 발견"
else
    PYTHON_CMD="python3"
    echo "⚠️  Python 3.13을 사용합니다 (호환성 문제가 있을 수 있음)"
fi

# 가상환경 생성
echo "🔧 Python 가상환경을 생성합니다..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

# pip 업그레이드
echo "📦 pip을 업그레이드합니다..."
pip install --upgrade pip setuptools wheel

# 최소한의 패키지만 설치 (호환성 우선)
echo "🚀 필수 패키지를 설치합니다..."

# 1. FastAPI와 Uvicorn (안정 버전)
pip install fastapi==0.104.1 uvicorn==0.24.0

# 2. 시스템 모니터링
pip install psutil==5.9.6

# 3. 파일 처리
pip install python-multipart==0.0.6 aiofiles==23.2.1

# 4. 환경 설정
pip install python-dotenv==1.0.0

# 5. HTTP 클라이언트 (requests 대신 httpx 사용)
pip install httpx==0.25.2

# 6. Pydantic Settings (누락된 모듈)
pip install pydantic-settings==2.0.3

# 설치 확인
echo "🔍 설치된 패키지를 확인합니다..."
if python -c "import fastapi, uvicorn, psutil; print('✅ 모든 필수 패키지가 설치되었습니다.')" 2>/dev/null; then
    echo "✅ Python 환경 설정 완료!"
else
    echo "❌ 패키지 설치에 문제가 있습니다."
    exit 1
fi

# Node.js 의존성 설치
echo "📦 Node.js 의존성을 설치합니다..."
cd "$PROJECT_DIR"
npm install

# 실행 권한 부여
chmod +x start.sh setup.sh quick-setup.sh

echo ""
echo "🎉 빠른 설정이 완료되었습니다!"
echo ""
echo "🚀 다음 명령어로 프로젝트를 시작하세요:"
echo "   ./start.sh"
echo ""
echo "또는 수동으로:"
echo "1. 백엔드: cd python-backend && source venv/bin/activate && python main.py"
echo "2. 프론트엔드: npm run dev:frontend"