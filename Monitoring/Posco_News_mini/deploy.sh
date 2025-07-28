#!/bin/bash

# POSCO 뉴스 AI 분석 시스템 배포 스크립트

echo "🚀 POSCO 뉴스 AI 분석 시스템 배포 시작..."

# 1. 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt

# 2. 분석 리포트 생성
echo "📊 분석 리포트 생성 중..."
python run_monitor.py 8

# 3. Git 상태 확인
echo "🔍 Git 상태 확인 중..."
git status

# 4. 변경사항 커밋
echo "💾 변경사항 커밋 중..."
git add .
git commit -m "🚀 자동 배포: $(date '+%Y-%m-%d %H:%M:%S')"

# 5. GitHub에 푸시
echo "📤 GitHub에 푸시 중..."
git push origin main

echo "✅ 배포 완료!"
echo "🌐 대시보드 URL: https://shuserker.github.io/infomax_api/"
echo "📱 PWA 설치 가능"
echo "🔄 자동 업데이트 활성화됨" 