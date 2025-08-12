#!/bin/bash
# ============================================================================
# Watchhamster V3.0 Control Panel
# POSCO 시스템 제어센터
# 
# WatchHamster v3.0 및 POSCO News 250808 호환
# Created: 2025-08-08
# ============================================================================

cd "$(dirname "$0")"

echo "============================================================================"
echo "🏭 POSCO 제어 센터 Mac 실행기"
echo "============================================================================"
echo ""

echo "📍 현재 경로: $(pwd)"
echo "📍 Bash 스크립트를 실행합니다..."
echo ""

# 파일 존재 확인
if [[ -f "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/posco_news_250808_control_center.sh" ]]; then
    echo "✅ posco_news_250808_control_center.sh 파일 발견"
else
    echo "❌ posco_news_250808_control_center.sh 파일을 찾을 수 없습니다."
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

if [[ -f "lib_wt_common.sh" ]]; then
    echo "✅ lib_wt_common.sh 파일 발견"
else
    echo "❌ lib_wt_common.sh 파일을 찾을 수 없습니다."
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

echo ""
echo "🚀 POSCO 제어 센터 실행 중..."
echo ""

# 실행 권한 부여
chmod +x posco_news_250808_control_center.sh

# 스크립트 실행
./Monitoring/POSCO_News_250808/posco_news_250808_control_center.sh

echo ""
echo "✅ 스크립트 실행이 완료되었습니다."
read -p "계속하려면 Enter를 누르세요..."