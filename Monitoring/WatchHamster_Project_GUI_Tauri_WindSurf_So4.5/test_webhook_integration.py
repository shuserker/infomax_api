#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 시스템 통합 검증 테스트
원본 로직이 완전히 통합되었는지 확인
"""

import sys
from pathlib import Path

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent / "python-backend" / "core" / "posco_original"))
sys.path.insert(0, str(Path(__file__).parent / "python-backend" / "core" / "watchhamster_original"))

from webhook_sender import WebhookSender, MessagePriority, BotType
from news_message_generator import NewsMessageGenerator
from datetime import datetime

def test_message_generator():
    """메시지 생성기 테스트"""
    print("=" * 80)
    print("📋 메시지 생성기 테스트")
    print("=" * 80)
    
    generator = NewsMessageGenerator(test_mode=True)
    
    # 샘플 데이터
    sample_data = {
        'newyork-market-watch': {
            'title': '뉴욕증시, 연준 금리 인하 기대감에 상승',
            'time': '060000',
            'status': 'latest'
        },
        'kospi-close': {
            'title': 'KOSPI, 외국인 매수세에 2,500선 회복',
            'time': '154000',
            'status': 'latest'
        },
        'exchange-rate': {
            'title': '원/달러 환율, 1,300원대 중반 등락',
            'time': '163000',
            'status': 'latest'
        }
    }
    
    # 1. 영업일 비교 분석 메시지
    print("\n1️⃣ 영업일 비교 분석 메시지:")
    print("-" * 80)
    result1 = generator.generate_business_day_comparison_message(sample_data, sample_data)
    if result1.success:
        print(f"✅ 생성 성공 ({result1.generation_time:.3f}초)")
        print(f"BOT 이름: {result1.bot_name}")
        print(f"색상: {result1.color}")
        print(f"\n메시지 내용:\n{result1.message}\n")
    else:
        print(f"❌ 생성 실패: {result1.errors}")
    
    # 2. 지연 발행 알림 메시지
    print("\n2️⃣ 지연 발행 알림 메시지:")
    print("-" * 80)
    result2 = generator.generate_delay_notification_message(
        'newyork-market-watch',
        sample_data['newyork-market-watch'],
        15
    )
    if result2.success:
        print(f"✅ 생성 성공 ({result2.generation_time:.3f}초)")
        print(f"BOT 이름: {result2.bot_name}")
        print(f"색상: {result2.color}")
        print(f"\n메시지 내용:\n{result2.message}\n")
    else:
        print(f"❌ 생성 실패: {result2.errors}")
    
    # 3. 일일 통합 리포트 메시지
    print("\n3️⃣ 일일 통합 리포트 메시지:")
    print("-" * 80)
    result3 = generator.generate_daily_integrated_report_message(sample_data)
    if result3.success:
        print(f"✅ 생성 성공 ({result3.generation_time:.3f}초)")
        print(f"BOT 이름: {result3.bot_name}")
        print(f"색상: {result3.color}")
        print(f"\n메시지 내용:\n{result3.message}\n")
    else:
        print(f"❌ 생성 실패: {result3.errors}")
    
    # 4. 정시 발행 알림 메시지
    print("\n4️⃣ 정시 발행 알림 메시지:")
    print("-" * 80)
    result4 = generator.generate_status_notification_message(sample_data)
    if result4.success:
        print(f"✅ 생성 성공 ({result4.generation_time:.3f}초)")
        print(f"BOT 이름: {result4.bot_name}")
        print(f"색상: {result4.color}")
        print(f"\n메시지 내용:\n{result4.message}\n")
    else:
        print(f"❌ 생성 실패: {result4.errors}")
    
    # 5. 데이터 갱신 없음 알림 메시지
    print("\n5️⃣ 데이터 갱신 없음 알림 메시지:")
    print("-" * 80)
    result5 = generator.generate_no_data_notification_message(sample_data)
    if result5.success:
        print(f"✅ 생성 성공 ({result5.generation_time:.3f}초)")
        print(f"BOT 이름: {result5.bot_name}")
        print(f"색상: {result5.color}")
        print(f"\n메시지 내용:\n{result5.message}\n")
    else:
        print(f"❌ 생성 실패: {result5.errors}")

def test_webhook_sender():
    """웹훅 전송자 테스트"""
    print("\n" + "=" * 80)
    print("📤 웹훅 전송자 테스트")
    print("=" * 80)
    
    sender = WebhookSender(test_mode=True)
    
    # 1. 테스트 메시지 전송
    print("\n1️⃣ 테스트 메시지 전송:")
    print("-" * 80)
    message_id = sender.send_test_message("원본 로직 통합 검증 테스트")
    if message_id:
        print(f"✅ 전송 성공: {message_id}")
    else:
        print("❌ 전송 실패")
    
    # 2. 워치햄스터 상태 알림
    print("\n2️⃣ 워치햄스터 상태 알림:")
    print("-" * 80)
    message_id = sender.send_watchhamster_status(
        "시스템 정상 작동 중",
        {"모니터링": "활성", "큐 크기": 0, "전송 성공률": "100%"}
    )
    if message_id:
        print(f"✅ 전송 성공: {message_id}")
    else:
        print("❌ 전송 실패")
    
    # 3. 큐 상태 확인
    print("\n3️⃣ 큐 상태 확인:")
    print("-" * 80)
    queue_status = sender.get_queue_status()
    print(f"큐 크기: {queue_status['queue_size']}")
    print(f"실패 메시지: {queue_status['failed_messages_count']}")
    print(f"캐시 크기: {queue_status['cache_size']}")
    print(f"실행 중: {queue_status['is_running']}")
    
    # 4. 전송 통계
    print("\n4️⃣ 전송 통계:")
    print("-" * 80)
    stats = sender.get_send_statistics()
    print(f"총 전송: {stats['total_sent']}")
    print(f"성공: {stats['successful_sends']}")
    print(f"실패: {stats['failed_sends']}")
    print(f"성공률: {stats.get('success_rate', 0) * 100:.1f}%")
    
    # 종료
    sender.shutdown()

def test_bot_configs():
    """BOT 설정 확인"""
    print("\n" + "=" * 80)
    print("🤖 BOT 설정 확인")
    print("=" * 80)
    
    generator = NewsMessageGenerator(test_mode=True)
    
    print("\n📋 BOT 설정:")
    for bot_type, config in generator.bot_configs.items():
        print(f"\n[{bot_type}]")
        print(f"  이름: {config['name']}")
        print(f"  아이콘: {config['icon']}")
        print(f"  색상: {config['color']}")
    
    print("\n📋 뉴스 타입 설정:")
    for news_type, config in generator.news_types.items():
        print(f"\n[{news_type}]")
        print(f"  표시명: {config['display_name']}")
        print(f"  이모지: {config['emoji']}")
        print(f"  예상 시간: {config['expected_time'][0]:02d}:{config['expected_time'][1]:02d}")
        print(f"  허용 시간: {config['tolerance_minutes']}분")

def test_webhook_urls():
    """웹훅 URL 확인"""
    print("\n" + "=" * 80)
    print("🔗 웹훅 URL 확인")
    print("=" * 80)
    
    sender = WebhookSender(test_mode=True)
    
    print("\n📋 웹훅 URL:")
    for endpoint, url in sender.webhook_urls.items():
        print(f"\n[{endpoint.value}]")
        print(f"  URL: {url}")
    
    print(f"\n📋 BOT 프로필 이미지:")
    print(f"  {sender.bot_profile_image}")
    
    sender.shutdown()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎯 웹훅 시스템 통합 검증 테스트")
    print("=" * 80)
    print(f"테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. BOT 설정 확인
        test_bot_configs()
        
        # 2. 웹훅 URL 확인
        test_webhook_urls()
        
        # 3. 메시지 생성기 테스트
        test_message_generator()
        
        # 4. 웹훅 전송자 테스트
        test_webhook_sender()
        
        print("\n" + "=" * 80)
        print("✅ 모든 테스트 완료!")
        print("=" * 80)
        print(f"테스트 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
