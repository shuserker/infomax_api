#!/bin/bash

# POSCO 워치햄스터 v3.0 제어센터 (Mac)
clear
echo "=========================================="
echo "   POSCO 워치햄스터 v3.0 제어센터"
echo "=========================================="
echo

while true; do
    echo "[1] 워치햄스터 모니터링 시작"
    echo "[2] 웹훅 테스트"
    echo "[3] AI 분석 실행"
    echo "[4] 비즈니스 데이 비교"
    echo "[5] 상태 확인"
    echo "[0] 종료"
    echo
    read -p "선택하세요 (0-5): " choice
    
    case $choice in
        1)
            echo
            echo "워치햄스터 모니터링을 시작합니다..."
            python3 recovery_config/watchhamster_monitor.py
            ;;
        2)
            echo
            echo "웹훅 테스트를 실행합니다..."
            python3 recovery_config/test_webhook_sender.py
            ;;
        3)
            echo
            echo "AI 분석을 실행합니다..."
            python3 recovery_config/ai_analysis_engine.py
            ;;
        4)
            echo
            echo "비즈니스 데이 비교를 실행합니다..."
            python3 recovery_config/business_day_comparison_engine.py
            ;;
        5)
            echo
            echo "시스템 상태를 확인합니다..."
            python3 recovery_config/git_monitor.py --status
            ;;
        0)
            echo
            echo "워치햄스터 제어센터를 종료합니다."
            exit 0
            ;;
        *)
            echo "잘못된 선택입니다. 다시 선택해주세요."
            ;;
    esac
    echo
    read -p "계속하려면 Enter를 누르세요..."
    clear
    echo "=========================================="
    echo "   POSCO 워치햄스터 v3.0 제어센터"
    echo "=========================================="
    echo
done
