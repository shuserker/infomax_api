#!/bin/bash

echo "========================================"
echo "   POSCO 시스템 일일 점검 (Mac/Linux)"
echo "========================================"
echo

echo "[1/3] 전체 시스템 테스트 실행 중..."
python3 comprehensive_system_integration_test.py
echo

echo "[2/3] 안정성 검증 실행 중..."
python3 practical_stability_verification.py
echo

echo "[3/3] 점검 완료!"
echo
echo "========================================"
echo "결과를 확인하고 문제가 있으면 담당자에게 연락하세요."
echo "담당자: [전화번호]"
echo "========================================"
echo

read -p "아무 키나 누르세요..."