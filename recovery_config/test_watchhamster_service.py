#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워치햄스터 서비스 테스트

짧은 시간 동안 워치햄스터 서비스를 실행하여 알림이 정상적으로 발송되는지 테스트합니다.
"""

import os
import sys
import time
import threading
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from webhook_sender import WebhookSender, MessagePriority
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


def test_watchhamster_service():
    """워치햄스터 서비스 테스트"""
    print("🎯🛡️ 워치햄스터 서비스 테스트 시작")
    print("=" * 50)
    
    # 웹훅 전송자 초기화 (실제 전송 모드)
    webhook_sender = WebhookSender(test_mode=False)
    
    # 1. 서비스 시작 알림
    print("📤 1. 서비스 시작 알림 전송...")
    start_message_id = webhook_sender.send_watchhamster_status(
        "워치햄스터 테스트 서비스 시작",
        {
            "test_start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "test_duration": "30초",
            "purpose": "웹훅 알림 테스트"
        }
    )
    
    if start_message_id:
        print(f"✅ 시작 알림 전송 성공: {start_message_id}")
    else:
        print("❌ 시작 알림 전송 실패")
    
    # 2. 잠시 대기
    print("⏳ 5초 대기 중...")
    time.sleep(5)
    
    # 3. 모니터링 상태 알림
    print("📤 2. 모니터링 상태 알림 전송...")
    status_message_id = webhook_sender.send_watchhamster_status(
        "워치햄스터 모니터링 정상 작동",
        {
            "monitoring_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "정상 모니터링",
            "checked_processes": ["posco_main_notifier", "realtime_monitor"],
            "all_processes_running": True
        }
    )
    
    if status_message_id:
        print(f"✅ 상태 알림 전송 성공: {status_message_id}")
    else:
        print("❌ 상태 알림 전송 실패")
    
    # 4. 잠시 대기
    print("⏳ 5초 대기 중...")
    time.sleep(5)
    
    # 5. 테스트 오류 알림 (실제 오류가 아닌 테스트용)
    print("📤 3. 테스트 오류 알림 전송...")
    error_message_id = webhook_sender.send_watchhamster_error(
        "테스트용 오류 알림 (실제 오류 아님)",
        {
            "error_type": "테스트 오류",
            "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "severity": "낮음",
            "auto_recovery": "테스트 완료 후 자동 해결"
        }
    )
    
    if error_message_id:
        print(f"✅ 오류 알림 전송 성공: {error_message_id}")
    else:
        print("❌ 오류 알림 전송 실패")
    
    # 6. 잠시 대기
    print("⏳ 5초 대기 중...")
    time.sleep(5)
    
    # 7. 서비스 종료 알림
    print("📤 4. 서비스 종료 알림 전송...")
    end_message_id = webhook_sender.send_watchhamster_status(
        "워치햄스터 테스트 서비스 종료",
        {
            "test_end_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "test_result": "성공",
            "messages_sent": 4,
            "next_action": "실제 서비스 시작 준비"
        }
    )
    
    if end_message_id:
        print(f"✅ 종료 알림 전송 성공: {end_message_id}")
    else:
        print("❌ 종료 알림 전송 실패")
    
    # 8. 전송 통계 확인
    print("\n📊 전송 통계:")
    stats = webhook_sender.get_send_statistics()
    print(f"  • 총 전송 시도: {stats['total_sent']}회")
    print(f"  • 성공한 전송: {stats['successful_sends']}회")
    print(f"  • 실패한 전송: {stats['failed_sends']}회")
    print(f"  • 성공률: {stats.get('success_rate', 0):.1%}")
    print(f"  • 평균 응답 시간: {stats['average_response_time']:.3f}초")
    
    # 9. 웹훅 전송자 정리
    webhook_sender.shutdown(timeout=3)
    
    print("\n🎉 워치햄스터 서비스 테스트 완료!")
    print("📋 결과:")
    
    messages_sent = [start_message_id, status_message_id, error_message_id, end_message_id]
    successful_messages = [msg for msg in messages_sent if msg is not None]
    
    print(f"  • 전송된 메시지: {len(successful_messages)}/4개")
    print(f"  • 성공률: {len(successful_messages)/4*100:.1f}%")
    
    if len(successful_messages) >= 3:
        print("✅ 워치햄스터 알림 시스템이 정상적으로 작동합니다!")
        print("🎯 이제 두레이에서 워치햄스터 알림을 확인할 수 있습니다.")
    else:
        print("⚠️ 일부 알림 전송에 문제가 있습니다.")
    
    return len(successful_messages) >= 3


def main():
    """메인 실행 함수"""
    print("🚀 POSCO 워치햄스터 알림 테스트")
    print("목적: 워치햄스터 알림이 두레이로 정상 전송되는지 확인")
    print()
    
    success = test_watchhamster_service()
    
    if success:
        print("\n🎉 테스트 성공! 워치햄스터 알림이 정상 작동합니다.")
        print("💡 이제 실제 워치햄스터 모니터를 시작할 수 있습니다:")
        print("   python3 recovery_config/start_watchhamster_monitor.py")
    else:
        print("\n❌ 테스트 실패. 워치햄스터 알림 설정을 확인해주세요.")
    
    return success


if __name__ == "__main__":
    main()