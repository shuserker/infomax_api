#!/bin/bash

# WatchHamster v3.0 Control Panel (Mac)
clear
echo "=========================================="
echo "   WatchHamster v3.0 Control Panel"
echo "=========================================="
echo

while true; do
    echo "[1] 통합 모니터링 시작"
    echo "[2] 뉴스 모니터링만 시작"
    echo "[3] 워치햄스터만 시작"
    echo "[4] 전체 테스트 실행"
    echo "[5] 시스템 상태 확인"
    echo "[0] 종료"
    echo
    read -p "선택하세요 (0-5): " choice
    
    case $choice in
        1)
            echo
            echo "통합 모니터링을 시작합니다..."
            python3 recovery_config/integrated_news_parser.py &
            python3 recovery_config/watchhamster_monitor.py &
            echo "통합 모니터링이 백그라운드에서 실행 중입니다."
            ;;
        2)
            echo
            echo "뉴스 모니터링을 시작합니다..."
            python3 recovery_config/integrated_news_parser.py
            ;;
        3)
            echo
            echo "워치햄스터 모니터링을 시작합니다..."
            python3 recovery_config/watchhamster_monitor.py
            ;;
        4)
            echo
            echo "전체 테스트를 실행합니다..."
            python3 -m pytest recovery_config/test_*.py -v
            ;;
        5)
            echo
            echo "시스템 상태를 확인합니다..."
            python3 recovery_config/git_monitor.py --status
            ;;
        0)
            echo
            echo "WatchHamster Control Panel을 종료합니다."
            # 백그라운드 프로세스 종료
            pkill -f "python3 recovery_config"
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
    echo "   WatchHamster v3.0 Control Panel"
    echo "=========================================="
    echo
done
