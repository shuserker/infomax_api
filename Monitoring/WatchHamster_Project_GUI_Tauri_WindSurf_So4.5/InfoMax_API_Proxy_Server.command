#!/bin/bash
# InfoMax API 프록시 서버 자동 실행 스크립트 (Mac)

echo "🚀 InfoMax API 프록시 서버 시작 중..."
echo "================================================"

# 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")"

# Python 백엔드 디렉토리로 이동
cd python-backend

# 가상환경이 있는지 확인하고 활성화
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
else
    echo "⚠️  가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다."
fi

# 의존성 설치 확인
echo "🔧 의존성 확인 중..."
python -m pip install -r requirements.txt > /dev/null 2>&1

# 서버 시작
echo "🌟 InfoMax API 프록시 서버 실행 중..."
echo "   - 주소: http://localhost:8000"
echo "   - API 문서: http://localhost:8000/docs"
echo "   - InfoMax 프록시: /api/infomax/*"
echo ""
echo "❤️  워치햄스터와 함께 InfoMax API를 안전하게 사용하세요!"
echo "================================================"

python start_infomax_proxy.py

echo ""
echo "👋 서버가 종료되었습니다. 창을 닫으셔도 됩니다."
read -p "Press Enter to continue..."
