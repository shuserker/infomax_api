#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 전송 시스템 테스트

DoorayWebhookSender의 기능을 테스트합니다.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.webhook_sender import DoorayWebhookSender, MessagePriority


async def test_webhook_functionality():
    """웹훅 기능 테스트"""
    print("🚀 웹훅 전송 시스템 테스트 시작")
    print("=" * 50)
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 웹훅 전송자 생성 (테스트 모드)
    webhook_sender = DoorayWebhookSender(test_mode=True)
    
    try:
        # 1. 테스트 메시지 전송
        print("\n1. 테스트 메시지 전송 중...")
        test_message_id = await webhook_sender.send_test_message(
            "WatchHamster Tauri 웹훅 시스템 테스트"
        )
        print(f"   ✅ 테스트 메시지 ID: {test_message_id}")
        
        # 2. POSCO 뉴스 알림 테스트
        print("\n2. POSCO 뉴스 알림 테스트 중...")
        news_data = {
            'news_type': 'exchange-rate',
            'status': 'latest',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'delay_minutes': 0
        }
        news_message_id = await webhook_sender.send_posco_news_alert(news_data)
        print(f"   ✅ 뉴스 알림 메시지 ID: {news_message_id}")
        
        # 3. 시스템 상태 보고서 테스트
        print("\n3. 시스템 상태 보고서 테스트 중...")
        system_status = {
            'status': 'healthy',
            'cpu_usage': 25,
            'memory_usage': 45,
            'disk_usage': 60,
            'uptime': '2일 3시간 15분'
        }
        status_message_id = await webhook_sender.send_system_status_report(system_status)
        print(f"   ✅ 상태 보고서 메시지 ID: {status_message_id}")
        
        # 4. 오류 알림 테스트
        print("\n4. 오류 알림 테스트 중...")
        error_data = {
            'error_type': '연결 오류',
            'error_message': 'API 서버에 연결할 수 없습니다',
            'component': 'INFOMAX API 클라이언트'
        }
        error_message_id = await webhook_sender.send_error_alert(error_data)
        print(f"   ✅ 오류 알림 메시지 ID: {error_message_id}")
        
        # 5. generate_dynamic_alert_message 테스트
        print("\n5. 동적 메시지 생성 테스트 중...")
        
        # 뉴스 알림 메시지 생성 테스트
        news_alert_msg = webhook_sender.generate_dynamic_alert_message(
            {
                'news_type': 'kospi-close',
                'status': 'delayed',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'delay_minutes': 15
            },
            "news_alert"
        )
        print(f"   ✅ 뉴스 알림 메시지 생성 완료 (길이: {len(news_alert_msg)}자)")
        
        # 시스템 상태 메시지 생성 테스트
        system_msg = webhook_sender.generate_dynamic_alert_message(
            {
                'status': 'warning',
                'cpu_usage': 85,
                'memory_usage': 90,
                'disk_usage': 75,
                'uptime': '5일 12시간 30분'
            },
            "system_status"
        )
        print(f"   ✅ 시스템 상태 메시지 생성 완료 (길이: {len(system_msg)}자)")
        
        # 6. 전송 대기 (큐 처리 시간)
        print("\n6. 메시지 전송 대기 중...")
        await asyncio.sleep(3)  # 3초 대기
        
        # 7. 상태 및 통계 확인
        print("\n7. 시스템 상태 확인 중...")
        queue_status = webhook_sender.get_queue_status()
        print(f"   📊 큐 상태:")
        print(f"      - 큐 크기: {queue_status['queue_size']}")
        print(f"      - 실패 메시지: {queue_status['failed_messages_count']}")
        print(f"      - 캐시 크기: {queue_status['cache_size']}")
        print(f"      - 실행 상태: {queue_status['is_running']}")
        
        statistics = webhook_sender.get_send_statistics()
        print(f"   📈 전송 통계:")
        print(f"      - 총 전송: {statistics['total_sent']}")
        print(f"      - 성공: {statistics['successful_sends']}")
        print(f"      - 실패: {statistics['failed_sends']}")
        print(f"      - 재시도: {statistics['retry_attempts']}")
        if statistics['total_sent'] > 0:
            print(f"      - 성공률: {statistics.get('success_rate', 0):.2%}")
        print(f"      - 평균 응답시간: {statistics['average_response_time']:.3f}초")
        
        print("\n✅ 모든 테스트가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 시스템 종료
        print("\n🔄 웹훅 시스템 종료 중...")
        webhook_sender.shutdown(timeout=5)
        print("✅ 웹훅 시스템 종료 완료")


def test_message_generation():
    """메시지 생성 기능만 테스트 (네트워크 없이)"""
    print("🧪 메시지 생성 기능 테스트")
    print("=" * 30)
    
    webhook_sender = DoorayWebhookSender(test_mode=True)
    
    # 다양한 시나리오의 메시지 생성 테스트
    test_cases = [
        {
            'name': '환율 뉴스 정시 발행',
            'data': {
                'news_type': 'exchange-rate',
                'status': 'latest',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'delay_minutes': 0
            },
            'type': 'news_alert'
        },
        {
            'name': '뉴욕증시 지연 발행',
            'data': {
                'news_type': 'newyork-market-watch',
                'status': 'delayed',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'delay_minutes': 25
            },
            'type': 'news_alert'
        },
        {
            'name': '시스템 정상 상태',
            'data': {
                'status': 'healthy',
                'cpu_usage': 30,
                'memory_usage': 50,
                'disk_usage': 40,
                'uptime': '1일 5시간 20분'
            },
            'type': 'system_status'
        },
        {
            'name': '시스템 경고 상태',
            'data': {
                'status': 'warning',
                'cpu_usage': 85,
                'memory_usage': 90,
                'disk_usage': 75,
                'uptime': '7일 2시간 45분'
            },
            'type': 'system_status'
        },
        {
            'name': 'API 연결 오류',
            'data': {
                'error_type': 'ConnectionError',
                'error_message': 'INFOMAX API 서버에 연결할 수 없습니다',
                'component': 'API 클라이언트'
            },
            'type': 'error_alert'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        message = webhook_sender.generate_dynamic_alert_message(
            test_case['data'], 
            test_case['type']
        )
        print(f"   생성된 메시지 (길이: {len(message)}자):")
        print("   " + "─" * 40)
        for line in message.split('\n'):
            print(f"   {line}")
        print("   " + "─" * 40)
    
    webhook_sender.shutdown(timeout=1)
    print("\n✅ 메시지 생성 테스트 완료!")


if __name__ == "__main__":
    print("WatchHamster Tauri 웹훅 시스템 테스트")
    print("=" * 60)
    
    # 사용자 선택
    print("\n테스트 옵션을 선택하세요:")
    print("1. 전체 기능 테스트 (실제 웹훅 전송 포함)")
    print("2. 메시지 생성 기능만 테스트 (네트워크 없이)")
    
    try:
        choice = input("\n선택 (1 또는 2): ").strip()
        
        if choice == "1":
            asyncio.run(test_webhook_functionality())
        elif choice == "2":
            test_message_generation()
        else:
            print("잘못된 선택입니다. 메시지 생성 테스트를 실행합니다.")
            test_message_generation()
            
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n테스트 실행 중 오류: {e}")