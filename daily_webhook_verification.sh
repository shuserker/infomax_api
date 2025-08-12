#!/bin/bash
# daily_webhook_verification.sh
# POSCO 워치햄스터 웹훅 시스템 일일 검증 스크립트

echo "=== POSCO 워치햄스터 웹훅 시스템 일일 검증 ==="
echo "검증 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 검증 결과 저장 변수
VERIFICATION_PASSED=true
ISSUES_FOUND=()

# 1. 웹훅 함수 존재 확인
echo "1. 웹훅 함수 존재 확인..."
python3 webhook_function_analysis_test.py --quiet

if [ $? -eq 0 ]; then
    echo "✅ 웹훅 함수 확인 완료 (12개 함수 정상)"
else
    echo "❌ 웹훅 함수 문제 발견!"
    VERIFICATION_PASSED=false
    ISSUES_FOUND+=("웹훅 함수 누락 또는 손상")
fi

# 2. 메시지 포맷 검증
echo "2. 메시지 포맷 검증..."
python3 webhook_format_validator.py --daily-check

if [ $? -eq 0 ]; then
    echo "✅ 메시지 포맷 검증 완료"
else
    echo "❌ 메시지 포맷 문제 발견!"
    VERIFICATION_PASSED=false
    ISSUES_FOUND+=("메시지 포맷 오류")
fi

# 3. 웹훅 URL 유효성 확인
echo "3. 웹훅 URL 유효성 확인..."
python3 -c "
import sys
try:
    from config import DOORAY_WEBHOOK_URL, WATCHHAMSTER_WEBHOOK_URL
    
    urls = [
        ('DOORAY_WEBHOOK_URL', DOORAY_WEBHOOK_URL),
        ('WATCHHAMSTER_WEBHOOK_URL', WATCHHAMSTER_WEBHOOK_URL)
    ]
    
    for name, url in urls:
        if 'dooray.com' in url and 'services' in url:
            print(f'✅ {name} 형식 유효')
        else:
            print(f'❌ {name} 형식 오류: {url}')
            sys.exit(1)
    
    print('✅ 모든 웹훅 URL 유효성 확인 완료')
except ImportError as e:
    print(f'❌ 설정 파일 로드 실패: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ URL 검증 중 오류: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ 웹훅 URL 유효성 확인 완료"
else
    echo "❌ 웹훅 URL 문제 발견!"
    VERIFICATION_PASSED=false
    ISSUES_FOUND+=("웹훅 URL 설정 오류")
fi

# 4. 백업 시스템 상태 확인
echo "4. 백업 시스템 상태 확인..."
python3 webhook_backup_manager.py --status --quiet

if [ $? -eq 0 ]; then
    echo "✅ 백업 시스템 정상 동작"
else
    echo "❌ 백업 시스템 문제 발견!"
    VERIFICATION_PASSED=false
    ISSUES_FOUND+=("백업 시스템 오류")
fi

# 5. 핵심 파일 존재 확인
echo "5. 핵심 파일 존재 확인..."
CORE_FILES=(
    "core/monitoring/monitor_WatchHamster_v3.0.py"
    "webhook_message_restorer.py"
    "webhook_backup_manager.py"
    "webhook_format_validator.py"
    "config.py"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 존재 확인"
    else
        echo "❌ $file 누락!"
        VERIFICATION_PASSED=false
        ISSUES_FOUND+=("핵심 파일 누락: $file")
    fi
done

echo ""
echo "=== 검증 결과 요약 ==="
echo "검증 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"

if [ "$VERIFICATION_PASSED" = true ]; then
    echo "🎉 모든 검증 통과 - 웹훅 시스템 정상 동작"
    echo ""
    echo "📊 시스템 상태:"
    echo "- 웹훅 함수: 12개 정상"
    echo "- 메시지 포맷: 정상"
    echo "- 웹훅 URL: 2개 유효"
    echo "- 백업 시스템: 정상"
    echo "- 핵심 파일: 모두 존재"
    
    # 성공 로그 기록
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 일일 검증 성공" >> webhook_verification.log
    
    exit 0
else
    echo "🚨 검증 실패 - 즉시 조치 필요!"
    echo ""
    echo "❌ 발견된 문제:"
    for issue in "${ISSUES_FOUND[@]}"; do
        echo "  - $issue"
    done
    
    echo ""
    echo "🔧 권장 조치사항:"
    echo "1. 비상 복구 스크립트 실행: ./emergency_webhook_recovery.sh"
    echo "2. 수동 점검 및 문제 해결"
    echo "3. 해결 후 재검증 실행"
    
    # 실패 로그 기록
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 일일 검증 실패: ${ISSUES_FOUND[*]}" >> webhook_verification.log
    
    # 알림 전송 (가능한 경우)
    if [ -f "webhook_alert_system.py" ]; then
        echo "📢 시스템 관리자에게 알림 전송 중..."
        python3 webhook_alert_system.py
    fi
    
    exit 1
fi