#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 디버그 테스트

프로필 이미지 사라짐과 워치햄스터 알림 문제를 진단합니다.
"""

import os
import sys
import time
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from webhook_sender import WebhookSender, MessagePriority
    from watchhamster_monitor import WatchHamsterMonitor
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


def test_webhook_configuration():
    """웹훅 설정 테스트"""
    print("🔍 웹훅 설정 진단")
    print("=" * 50)
    
    webhook_sender = WebhookSender(test_mode=False)  # 실제 전송 모드
    
    # 웹훅 URL 확인
    print("📡 웹훅 URL 설정:")
    for endpoint, url in webhook_sender.webhook_urls.items():
        print(f"  • {endpoint.value}: {url[:50]}...")
    
    print(f"\n🖼️ BOT 프로필 이미지: {webhook_sender.bot_profile_image}")
    
    # BOT 라우팅 확인
    print("\n🤖 BOT 라우팅 설정:")
    for bot_type, endpoint in webhook_sender.bot_routing.items():
        print(f"  • {bot_type.value} → {endpoint.value}")
    
    return webhook_sender


def test_news_webhook():
    """뉴스 웹훅 테스트"""
    print("\n📰 뉴스 웹훅 테스트")
    print("=" * 50)
    
    webhook_sender = WebhookSender(test_mode=False)
    
    # 테스트 메시지 전송
    message_id = webhook_sender.send_test_message(
        "웹훅 설정 테스트 - 프로필 이미지 확인"
    )
    
    if message_id:
        print(f"✅ 뉴스 테스트 메시지 전송됨: {message_id}")
        
        # 잠시 대기 후 전송 결과 확인
        time.sleep(2)
        
        stats = webhook_sender.get_send_statistics()
        print(f"📊 전송 통계: {stats['successful_sends']}/{stats['total_sent']} 성공")
        
        return True
    else:
        print("❌ 뉴스 테스트 메시지 전송 실패")
        return False


def test_watchhamster_webhook():
    """워치햄스터 웹훅 테스트"""
    print("\n🎯🛡️ 워치햄스터 웹훅 테스트")
    print("=" * 50)
    
    webhook_sender = WebhookSender(test_mode=False)
    
    # 워치햄스터 상태 알림 테스트
    status_message_id = webhook_sender.send_watchhamster_status(
        "워치햄스터 웹훅 테스트",
        {
            "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "system_status": "정상",
            "monitoring_active": True
        }
    )
    
    if status_message_id:
        print(f"✅ 워치햄스터 상태 알림 전송됨: {status_message_id}")
    else:
        print("❌ 워치햄스터 상태 알림 전송 실패")
    
    # 워치햄스터 오류 알림 테스트
    error_message_id = webhook_sender.send_watchhamster_error(
        "워치햄스터 오류 알림 테스트",
        {
            "error_type": "테스트 오류",
            "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "recovery_status": "테스트 중"
        }
    )
    
    if error_message_id:
        print(f"✅ 워치햄스터 오류 알림 전송됨: {error_message_id}")
    else:
        print("❌ 워치햄스터 오류 알림 전송 실패")
    
    # 잠시 대기 후 전송 결과 확인
    time.sleep(3)
    
    stats = webhook_sender.get_send_statistics()
    print(f"📊 전송 통계: {stats['successful_sends']}/{stats['total_sent']} 성공")
    
    return status_message_id is not None or error_message_id is not None


def test_profile_image_url():
    """프로필 이미지 URL 테스트"""
    print("\n🖼️ 프로필 이미지 URL 테스트")
    print("=" * 50)
    
    webhook_sender = WebhookSender(test_mode=False)
    profile_url = webhook_sender.bot_profile_image
    
    print(f"프로필 이미지 URL: {profile_url}")
    
    try:
        import requests
        response = requests.get(profile_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 프로필 이미지 URL 접근 가능")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ 프로필 이미지 URL 접근 실패: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 프로필 이미지 URL 테스트 오류: {e}")
        return False


def test_watchhamster_monitor_status():
    """워치햄스터 모니터 상태 확인"""
    print("\n🔍 워치햄스터 모니터 상태 확인")
    print("=" * 50)
    
    try:
        monitor = WatchHamsterMonitor()
        
        # 모니터 상태 확인
        status = monitor.get_system_status()
        print(f"📊 시스템 상태: {status}")
        
        # 모니터링 대상 프로세스 확인
        if hasattr(monitor, 'monitored_processes'):
            print(f"🎯 모니터링 대상: {list(monitor.monitored_processes.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 워치햄스터 모니터 상태 확인 실패: {e}")
        return False


def run_comprehensive_webhook_diagnosis():
    """종합 웹훅 진단"""
    print("🚀 POSCO 웹훅 시스템 종합 진단")
    print("=" * 60)
    print("문제 상황:")
    print("  • 두레이 웹훅 프로필 이미지 사라짐")
    print("  • 워치햄스터 알림이 오지 않음")
    print("  • 포스코 뉴스만 오는 상황")
    print()
    
    results = {}
    
    # 1. 웹훅 설정 확인
    webhook_sender = test_webhook_configuration()
    
    # 2. 프로필 이미지 URL 테스트
    results['profile_image'] = test_profile_image_url()
    
    # 3. 뉴스 웹훅 테스트
    results['news_webhook'] = test_news_webhook()
    
    # 4. 워치햄스터 웹훅 테스트
    results['watchhamster_webhook'] = test_watchhamster_webhook()
    
    # 5. 워치햄스터 모니터 상태 확인
    results['watchhamster_monitor'] = test_watchhamster_monitor_status()
    
    # 진단 결과 요약
    print("\n" + "=" * 60)
    print("🎯 진단 결과 요약:")
    print("-" * 40)
    
    for test_name, result in results.items():
        status_icon = "✅" if result else "❌"
        test_display = test_name.replace('_', ' ').title()
        print(f"{status_icon} {test_display}: {'정상' if result else '문제 있음'}")
    
    # 문제 해결 방안 제시
    print("\n🔧 문제 해결 방안:")
    print("-" * 40)
    
    if not results['profile_image']:
        print("• 프로필 이미지 URL 문제:")
        print("  - GitHub 이미지 URL 확인 필요")
        print("  - 대체 이미지 URL 사용 고려")
    
    if not results['watchhamster_webhook']:
        print("• 워치햄스터 웹훅 문제:")
        print("  - 워치햄스터 채널 웹훅 URL 확인")
        print("  - 워치햄스터 모니터 실행 상태 확인")
    
    if not results['watchhamster_monitor']:
        print("• 워치햄스터 모니터 문제:")
        print("  - 모니터 프로세스 시작 필요")
        print("  - 모니터링 설정 확인 필요")
    
    # 전체 성공률
    success_count = sum(results.values())
    total_count = len(results)
    success_rate = success_count / total_count * 100
    
    print(f"\n📊 전체 진단 결과: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 대부분의 기능이 정상 작동합니다!")
    elif success_rate >= 60:
        print("⚠️ 일부 기능에 문제가 있습니다.")
    else:
        print("🚨 여러 기능에 문제가 발생했습니다.")
    
    return results


def main():
    """메인 실행 함수"""
    results = run_comprehensive_webhook_diagnosis()
    
    print("\n🎯 다음 단계:")
    print("1. 문제가 발견된 부분을 우선 수정")
    print("2. 워치햄스터 모니터 실행 상태 확인")
    print("3. 웹훅 URL 및 프로필 이미지 URL 업데이트")
    print("4. 실제 알림 발송 테스트")
    
    return results


if __name__ == "__main__":
    main()