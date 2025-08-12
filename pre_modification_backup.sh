#!/bin/bash
# pre_modification_backup.sh
# 웹훅 기능 수정 전 필수 백업 스크립트

echo "=== POSCO 워치햄스터 웹훅 기능 수정 전 백업 생성 ==="

# 현재 날짜와 시간으로 백업명 생성
BACKUP_NAME="pre_modification_$(date +%Y%m%d_%H%M%S)"

echo "백업명: $BACKUP_NAME"
echo "백업 생성 중..."

# 백업 생성
python3 webhook_backup_manager.py --create "$BACKUP_NAME" --description "수정 작업 전 안전 백업"

if [ $? -eq 0 ]; then
    echo "✅ 백업 생성 완료"
    
    # 백업 검증
    echo "백업 무결성 검증 중..."
    python3 webhook_backup_manager.py --verify "$BACKUP_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ 백업 검증 완료"
        echo ""
        echo "🎉 백업 완료: $BACKUP_NAME"
        echo "이제 안전하게 수정 작업을 진행할 수 있습니다."
        echo ""
        echo "📋 수정 작업 시 주의사항:"
        echo "- 웹훅 관련 함수 12개 보존 필수"
        echo "- 메시지 템플릿 및 이모지 보존"
        echo "- 줄바꿈 문자 처리 방식 유지"
        echo "- 제품명 표기 일관성 유지"
        echo ""
        echo "🚨 문제 발생 시 복구 명령:"
        echo "python3 webhook_backup_manager.py --rollback $BACKUP_NAME"
    else
        echo "❌ 백업 검증 실패 - 백업을 다시 생성해주세요"
        exit 1
    fi
else
    echo "❌ 백업 생성 실패 - 시스템 상태를 확인해주세요"
    exit 1
fi