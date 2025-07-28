#!/bin/bash

# POSCO 뉴스 AI 분석 시스템 - 일일 분석 스크립트
# 매일 자동으로 실행되어 분석 및 배포를 수행합니다.

echo "🚀 POSCO 뉴스 일일 분석 시작..."
echo "🕐 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"

# 1. 시스템 상태 점검
echo "🏥 시스템 상태 점검 중..."
python3 posco_cli.py health

if [ $? -ne 0 ]; then
    echo "❌ 시스템 상태 점검 실패. 분석을 중단합니다."
    exit 1
fi

# 2. 고급 분석 실행 (30일 데이터)
echo "🧠 고급 분석 실행 중..."
python3 posco_cli.py analyze --advanced --days 30

if [ $? -ne 0 ]; then
    echo "❌ 분석 실행 실패."
    exit 1
fi

# 3. 자동 배포
echo "🚀 자동 배포 실행 중..."
python3 posco_cli.py deploy

if [ $? -ne 0 ]; then
    echo "❌ 배포 실패."
    exit 1
fi

# 4. 오래된 리포트 정리
echo "🧹 오래된 리포트 정리 중..."
python3 posco_cli.py report --clean

# 5. 백업 생성 (주 1회)
DAY_OF_WEEK=$(date '+%u')  # 1=월요일, 7=일요일
if [ "$DAY_OF_WEEK" = "1" ]; then
    echo "💾 주간 백업 생성 중..."
    python3 posco_cli.py backup --create
fi

echo "✅ 일일 분석 완료!"
echo "🕐 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🌐 대시보드: https://shuserker.github.io/infomax_api/" 