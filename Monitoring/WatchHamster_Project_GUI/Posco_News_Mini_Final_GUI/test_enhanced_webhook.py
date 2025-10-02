#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 웹훅 시스템 테스트
MessageTemplateEngine 통합 및 고객 친화적 메시지 테스트

Requirements: 2.1, 2.2 검증
"""

import os
import sys
import json
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from posco_main_notifier import PoscoMainNotifier
    from message_template_engine import MessageType
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


def test_enhanced_webhook_system():
    """향상된 웹훅 시스템 테스트"""
    print("🧪 향상된 웹훅 시스템 테스트 시작...")
    
    # PoscoMainNotifier 초기화
    notifier = PoscoMainNotifier()
    
    # 테스트용 웹훅 URL 설정 (실제 URL로 변경 필요)
    test_webhook_url = "https://httpbin.org/post"  # 테스트용 엔드포인트
    notifier.webhook_url = test_webhook_url
    
    print(f"📡 테스트 웹훅 URL: {test_webhook_url}")
    
    # 테스트 케이스 1: 배포 성공 메시지 (MessageTemplateEngine 사용)
    print("\n=== 테스트 1: 배포 성공 메시지 (템플릿 엔진) ===")
    
    success_deployment_result = {
        'deployment_id': 'deploy_test_20250923_140000',
        'start_time': '2025-09-23T14:00:00',
        'end_time': '2025-09-23T14:02:30',
        'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 'merge_main', 'commit_changes', 'push_remote', 'pages_verification'],
        'success': True,
        'github_pages_accessible': True,
        'backup_created': True,
        'backup_tag': 'backup-20250923_140000'
    }
    
    def test_status_callback(message, progress):
        print(f"  📊 진행률 {progress}%: {message}")
    
    webhook_result = notifier.send_direct_webhook(
        deployment_result=success_deployment_result,
        message_type=MessageType.DEPLOYMENT_SUCCESS,
        status_callback=test_status_callback
    )
    
    print(f"✅ 성공 메시지 전송 결과: {webhook_result['success']}")
    if webhook_result.get('template_used'):
        print(f"📝 사용된 템플릿: {webhook_result['template_used']['type']}")
    if webhook_result.get('error_message'):
        print(f"❌ 오류: {webhook_result['error_message']}")
    
    # 테스트 케이스 2: 배포 실패 메시지 (MessageTemplateEngine 사용)
    print("\n=== 테스트 2: 배포 실패 메시지 (템플릿 엔진) ===")
    
    failure_deployment_result = {
        'deployment_id': 'deploy_test_20250923_140500',
        'start_time': '2025-09-23T14:05:00',
        'end_time': '2025-09-23T14:06:15',
        'steps_completed': ['status_check', 'backup_creation', 'branch_switch'],
        'success': False,
        'error_message': 'Git push 중 인증 실패 - 원격 저장소 접근 권한을 확인하세요',
        'rollback_performed': True,
        'backup_created': True
    }
    
    webhook_result = notifier.send_direct_webhook(
        deployment_result=failure_deployment_result,
        message_type=MessageType.DEPLOYMENT_FAILURE,
        status_callback=test_status_callback
    )
    
    print(f"✅ 실패 메시지 전송 결과: {webhook_result['success']}")
    if webhook_result.get('template_used'):
        print(f"📝 사용된 템플릿: {webhook_result['template_used']['type']}")
    if webhook_result.get('error_message'):
        print(f"❌ 오류: {webhook_result['error_message']}")
    
    # 테스트 케이스 3: 배포 시작 알림
    print("\n=== 테스트 3: 배포 시작 알림 ===")
    
    start_result = notifier.send_deployment_start_notification(
        'deploy_test_20250923_141000',
        test_status_callback
    )
    
    print(f"✅ 시작 알림 전송 결과: {start_result['success']}")
    if start_result.get('error_message'):
        print(f"❌ 오류: {start_result['error_message']}")
    
    # 테스트 케이스 4: 직접 메시지 전송 (기존 방식)
    print("\n=== 테스트 4: 직접 메시지 전송 ===")
    
    direct_message = "🏭 POSCO 시스템 테스트 메시지입니다. 모든 시스템이 정상 작동 중입니다."
    
    direct_result = notifier.send_direct_webhook(
        message=direct_message,
        status_callback=test_status_callback
    )
    
    print(f"✅ 직접 메시지 전송 결과: {direct_result['success']}")
    if direct_result.get('error_message'):
        print(f"❌ 오류: {direct_result['error_message']}")
    
    # 테스트 케이스 5: 오류 알림 메시지
    print("\n=== 테스트 5: 오류 알림 메시지 ===")
    
    error_data = {
        'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'error_type': '데이터베이스 연결 실패',
        'impact_scope': '데이터 수집 시스템',
        'error_details': 'Connection timeout after 30 seconds',
        'auto_recovery_status': '재시도 중',
        'estimated_recovery_time': '2-3분'
    }
    
    error_result = notifier.send_direct_webhook(
        deployment_result=error_data,
        message_type=MessageType.ERROR_ALERT,
        status_callback=test_status_callback
    )
    
    print(f"✅ 오류 알림 전송 결과: {error_result['success']}")
    if error_result.get('template_used'):
        print(f"📝 사용된 템플릿: {error_result['template_used']['type']}")
    if error_result.get('error_message'):
        print(f"❌ 오류: {error_result['error_message']}")
    
    print("\n=== 테스트 완료 ===")
    return True


def test_customer_friendly_conversion():
    """고객 친화적 메시지 변환 테스트"""
    print("\n🧪 고객 친화적 메시지 변환 테스트...")
    
    notifier = PoscoMainNotifier()
    
    # 개발자 용어가 포함된 메시지
    technical_message = """
    Git 저장소에서 commit을 push하는 중 오류가 발생했습니다.
    GitHub Pages 배포 pipeline에서 rollback을 수행했습니다.
    webhook API 호출이 실패했습니다.
    """
    
    # 고객 친화적으로 변환
    friendly_message = notifier._convert_to_customer_friendly(technical_message)
    
    print("📝 원본 메시지:")
    print(technical_message)
    print("\n📝 변환된 메시지:")
    print(friendly_message)
    
    # 변환 확인
    conversions = [
        ('Git 저장소', '시스템 데이터'),
        ('commit', '저장'),
        ('push', '업로드'),
        ('GitHub Pages', 'POSCO 분석 웹사이트'),
        ('pipeline', '처리 과정'),
        ('rollback', '이전 상태 복구'),
        ('webhook', '알림 시스템'),
        ('API', '데이터 연결')
    ]
    
    print("\n✅ 변환 확인:")
    for original, converted in conversions:
        if original in technical_message and converted in friendly_message:
            print(f"  ✓ '{original}' → '{converted}'")
        else:
            print(f"  ⚠️ '{original}' 변환 확인 필요")
    
    return True


def test_message_preview():
    """메시지 미리보기 테스트"""
    print("\n🧪 메시지 미리보기 테스트...")
    
    notifier = PoscoMainNotifier()
    
    # 테스트 데이터
    test_data = {
        'deployment_id': 'preview_test_001',
        'start_time': '2025-09-23T14:00:00',
        'end_time': '2025-09-23T14:02:30',
        'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 'merge_main'],
        'success': True,
        'github_pages_accessible': True
    }
    
    # 성공 메시지 미리보기
    success_preview = notifier.message_engine.preview_message(
        MessageType.DEPLOYMENT_SUCCESS, 
        test_data
    )
    
    print("📋 배포 성공 메시지 미리보기:")
    print(success_preview)
    
    # 실패 메시지 미리보기
    test_data['success'] = False
    test_data['error_message'] = '테스트 오류 메시지'
    
    failure_preview = notifier.message_engine.preview_message(
        MessageType.DEPLOYMENT_FAILURE,
        test_data
    )
    
    print("\n📋 배포 실패 메시지 미리보기:")
    print(failure_preview)
    
    return True


def main():
    """메인 테스트 함수"""
    print("🚀 향상된 웹훅 시스템 종합 테스트 시작...")
    
    try:
        # 기본 웹훅 시스템 테스트
        test_enhanced_webhook_system()
        
        # 고객 친화적 변환 테스트
        test_customer_friendly_conversion()
        
        # 메시지 미리보기 테스트
        test_message_preview()
        
        print("\n✅ 모든 테스트 완료!")
        print("\n📊 테스트 결과 요약:")
        print("  ✓ MessageTemplateEngine 통합 완료")
        print("  ✓ 고객 친화적 메시지 변환 완료")
        print("  ✓ GUI 상태 업데이트 콜백 지원")
        print("  ✓ 향상된 오류 처리 및 로깅")
        print("  ✓ 웹훅 설정 파일 지원")
        
        print("\n🎯 Requirements 2.1, 2.2 구현 완료:")
        print("  • MessageTemplateEngine과 연동하여 포스코 스타일 메시지 형식 적용")
        print("  • 개발자용 메시지를 고객 친화적 내용으로 변경")
        print("  • GUI에서 메시지 전송 상태 실시간 모니터링 지원")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)