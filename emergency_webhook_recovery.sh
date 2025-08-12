#!/bin/bash
# emergency_webhook_recovery.sh
# 웹훅 시스템 비상 복구 스크립트

echo "🚨🚨🚨 POSCO 워치햄스터 웹훅 시스템 비상 복구 시작 🚨🚨🚨"
echo "복구 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 복구 로그 파일
RECOVERY_LOG="emergency_recovery_$(date +%Y%m%d_%H%M%S).log"
echo "복구 로그: $RECOVERY_LOG"

# 로그 함수
log_message() {
    echo "$1" | tee -a "$RECOVERY_LOG"
}

# 1. 현재 상태 비상 백업
log_message "1. 현재 상태 비상 백업 생성..."
EMERGENCY_BACKUP="emergency_backup_$(date +%Y%m%d_%H%M%S)"

python3 webhook_backup_manager.py --create "$EMERGENCY_BACKUP" --description "비상 복구 전 현재 상태 백업"

if [ $? -eq 0 ]; then
    log_message "✅ 비상 백업 생성 완료: $EMERGENCY_BACKUP"
else
    log_message "❌ 비상 백업 생성 실패 - 계속 진행"
fi

# 2. 시스템 상태 진단
log_message ""
log_message "2. 시스템 상태 진단..."

# 웹훅 함수 상태 확인
python3 webhook_function_analysis_test.py --quiet > /dev/null 2>&1
WEBHOOK_FUNCTIONS_OK=$?

# 메시지 포맷 상태 확인
python3 webhook_format_validator.py --daily-check > /dev/null 2>&1
MESSAGE_FORMAT_OK=$?

# 백업 시스템 상태 확인
python3 webhook_backup_manager.py --status --quiet > /dev/null 2>&1
BACKUP_SYSTEM_OK=$?

log_message "진단 결과:"
log_message "- 웹훅 함수: $([ $WEBHOOK_FUNCTIONS_OK -eq 0 ] && echo '정상' || echo '문제 있음')"
log_message "- 메시지 포맷: $([ $MESSAGE_FORMAT_OK -eq 0 ] && echo '정상' || echo '문제 있음')"
log_message "- 백업 시스템: $([ $BACKUP_SYSTEM_OK -eq 0 ] && echo '정상' || echo '문제 있음')"

# 3. 자동 롤백 실행
log_message ""
log_message "3. 자동 롤백 실행..."

python3 webhook_backup_manager.py --auto-rollback "Emergency recovery - $(date)"

if [ $? -eq 0 ]; then
    log_message "✅ 자동 롤백 성공"
    ROLLBACK_SUCCESS=true
else
    log_message "❌ 자동 롤백 실패"
    ROLLBACK_SUCCESS=false
fi

# 4. 복구 후 검증
log_message ""
log_message "4. 복구 후 시스템 검증..."

if [ "$ROLLBACK_SUCCESS" = true ]; then
    # 웹훅 함수 재확인
    python3 webhook_function_analysis_test.py --quiet > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_message "✅ 웹훅 함수 복구 확인"
        
        # 메시지 포맷 재확인
        python3 webhook_format_validator.py --daily-check > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log_message "✅ 메시지 포맷 복구 확인"
            
            # 5. 테스트 메시지 전송
            log_message ""
            log_message "5. 복구 확인 테스트 메시지 전송..."
            
            if [ -f "real_webhook_transmission_test.py" ]; then
                python3 real_webhook_transmission_test.py --test-mode --single-test > /dev/null 2>&1
                if [ $? -eq 0 ]; then
                    log_message "✅ 테스트 메시지 전송 성공"
                    
                    log_message ""
                    log_message "🎉🎉🎉 비상 복구 완료! 🎉🎉🎉"
                    log_message "복구 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
                    log_message ""
                    log_message "📊 복구 결과:"
                    log_message "- 웹훅 함수: 복구됨"
                    log_message "- 메시지 포맷: 복구됨"
                    log_message "- 테스트 전송: 성공"
                    log_message "- 비상 백업: $EMERGENCY_BACKUP"
                    log_message ""
                    log_message "✅ 시스템이 정상 상태로 복구되었습니다."
                    
                    # 성공 알림 전송 (가능한 경우)
                    if [ -f "webhook_alert_system.py" ]; then
                        python3 -c "
from webhook_alert_system import send_webhook_alert
send_webhook_alert('SUCCESS', '웹훅 시스템 비상 복구 완료', '시스템이 정상 상태로 복구되었습니다.')
"
                    fi
                    
                    exit 0
                else
                    log_message "❌ 테스트 메시지 전송 실패"
                fi
            else
                log_message "⚠️ 테스트 스크립트 없음 - 수동 테스트 필요"
            fi
        else
            log_message "❌ 메시지 포맷 복구 실패"
        fi
    else
        log_message "❌ 웹훅 함수 복구 실패"
    fi
fi

# 복구 실패 시 처리
log_message ""
log_message "🚨 비상 복구 실패 - 수동 개입 필요 🚨"
log_message "실패 시간: $(date '+%Y-%m-%d %H:%M:%S')"
log_message ""
log_message "📋 수동 복구 절차:"
log_message "1. 백업 목록 확인: python3 webhook_backup_manager.py --list"
log_message "2. 적절한 백업 선택하여 수동 롤백"
log_message "3. 핵심 파일 수동 점검:"
log_message "   - core/monitoring/monitor_WatchHamster_v3.0.py"
log_message "   - webhook_message_restorer.py"
log_message "   - config.py"
log_message "4. 웹훅 함수 12개 존재 확인"
log_message "5. 메시지 포맷 수동 검증"
log_message ""
log_message "🆘 긴급 연락처:"
log_message "- 시스템 관리자: [연락처]"
log_message "- 개발팀 리더: [연락처]"
log_message "- 24시간 대응팀: [연락처]"

# 실패 알림 전송 (가능한 경우)
if [ -f "webhook_alert_system.py" ]; then
    python3 -c "
from webhook_alert_system import send_webhook_alert
send_webhook_alert('ERROR', '웹훅 시스템 비상 복구 실패', '수동 개입이 필요합니다. 복구 로그: $RECOVERY_LOG')
"
fi

exit 1