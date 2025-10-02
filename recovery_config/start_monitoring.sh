#!/bin/bash

echo "========================================"
echo "   POSCO 워치햄스터 모니터 시작 (Mac/Linux)"
echo "========================================"
echo

echo "워치햄스터 모니터를 시작합니다..."
echo "중단하려면 Ctrl+C를 누르세요."
echo

python3 start_watchhamster_monitor.py

echo
echo "모니터가 중단되었습니다."
read -p "아무 키나 누르세요..."