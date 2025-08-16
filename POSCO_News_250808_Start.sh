#!/bin/bash

# POSCO News 250808 모니터링 시작 (Mac)
clear
echo "=========================================="
echo "   POSCO News 250808 모니터링 시작"
echo "=========================================="
echo

echo "뉴스 모니터링 시스템을 시작합니다..."
echo

# API 연결 테스트
echo "[1/4] API 연결 상태 확인 중..."
python3 recovery_config/api_connection_manager.py --test

# 뉴스 파서 초기화
echo "[2/4] 뉴스 파서 초기화 중..."
python3 recovery_config/integrated_news_parser.py --init

# 웹훅 연결 테스트
echo "[3/4] 웹훅 연결 테스트 중..."
python3 recovery_config/webhook_sender.py --test

# 모니터링 시작
echo "[4/4] 모니터링 시작..."
python3 recovery_config/integrated_news_parser.py --monitor

echo
echo "POSCO News 모니터링이 시작되었습니다."
echo "종료하려면 Ctrl+C를 누르거나 별도 터미널에서 중지 스크립트를 실행하세요."
read -p "계속하려면 Enter를 누르세요..."
