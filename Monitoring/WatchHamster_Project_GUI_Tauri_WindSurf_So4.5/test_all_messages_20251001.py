#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 메시지 타입 실제 작동 테스트 (20251001 데이터)
"""

import sys
from pathlib import Path
from datetime import datetime

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent / "python-backend" / "core" / "posco_original"))
sys.path.insert(0, str(Path(__file__).parent / "python-backend" / "core" / "watchhamster_original"))

from webhook_sender import WebhookSender, MessagePriority
from news_message_generator import NewsMessageGenerator

def create_sample_data_20251001():
    """2025-10-01 샘플 데이터 생성"""
    return {
        'newyork-market-watch': {
            'title': '[20251001] 뉴욕증시, 9월 고용지표 호조에 상승 마감',
            'time': '060500',
            'date': '20251001',
            'status': 'latest',
            'content': '다우 +0.8%, S&P500 +1.2%, 나스닥 +1.5% 상승'
        },
        'kospi-close': {
            'title': '[20251001] KOSPI, 외국인 순매수에 2,550선 돌파',
            'time': '154200',
            'date': '20251001',
            'status': 'latest',
            'content': 'KOSPI 2,555.32 (+1.2%), KOSDAQ 850.45 (+0.8%)'
        },
        'exchange-rate': {
            'title': '[20251001] 원/달러 환율, 1,320원대 중반 등락',
            'time': '163200',
            'date': '20251001',
            'status': 'latest',
            'content': '종가 1,325.50원 (-2.30원)'
        }
    }

def create_historical_data_20250930():
    """2025-09-30 과거 데이터 (비교용)"""
    return {
        'newyork-market-watch': {
            'title': '[20250930] 뉴욕증시, 연준 금리 동결에 혼조 마감',
            'time': '060000',
            'date': '20250930',
            'status': 'latest'
        },
        'kospi-close': {
            'title': '[20250930] KOSPI, 기관 매도에 2,520선 하락',
            'time': '154000',
            'date': '20250930',
            'status': 'latest'
        },
        'exchange-rate': {
            'title': '[20250930] 원/달러 환율, 1,327원대 마감',
            'time': '163000',
            'date': '20250930',
            'status': 'latest'
        }
    }

def test_all_messages():
    """모든 메시지 타입 테스트"""
    print("=" * 100)
    print("🎯 모든 메시지 타입 실제 작동 테스트 (20251001 데이터)")
    print("=" * 100)
    print(f"테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 데이터 준비
    current_data = create_sample_data_20251001()
    historical_data = create_historical_data_20250930()
    
    # 메시지 생성기 초기화
    generator = NewsMessageGenerator(test_mode=False)
    sender = WebhookSender(test_mode=False)
    
    results = []
    
    # 1. 영업일 비교 분석 메시지
    print("\n" + "=" * 100)
    print("1️⃣ 영업일 비교 분석 메시지 (20251001 vs 20250930)")
    print("=" * 100)
    try:
        result = generator.generate_business_day_comparison_message(
            raw_data=current_data,
            historical_data=historical_data
        )
        if result.success:
            print(f"✅ 생성 성공 ({result.generation_time:.3f}초)")
            print(f"BOT: {result.bot_name}")
            print(f"색상: {result.color}")
            print(f"\n{'─' * 100}")
            print(result.message)
            print(f"{'─' * 100}\n")
            
            # 실제 전송
            message_id = sender.send_business_day_comparison(
                raw_data=current_data,
                historical_data=historical_data,
                priority=MessagePriority.NORMAL
            )
            print(f"📤 전송 결과: {message_id if message_id else '실패'}")
            results.append(("영업일 비교 분석", message_id, True))
        else:
            print(f"❌ 생성 실패: {result.errors}")
            results.append(("영업일 비교 분석", None, False))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("영업일 비교 분석", None, False))
    
    # 2. 지연 발행 알림 메시지 (NEWYORK)
    print("\n" + "=" * 100)
    print("2️⃣ 지연 발행 알림 메시지 - NEWYORK MARKET WATCH (20251001)")
    print("=" * 100)
    try:
        result = generator.generate_delay_notification_message(
            news_type='newyork-market-watch',
            current_data=current_data['newyork-market-watch'],
            delay_minutes=5
        )
        if result.success:
            print(f"✅ 생성 성공 ({result.generation_time:.3f}초)")
            print(f"BOT: {result.bot_name}")
            print(f"색상: {result.color}")
            print(f"\n{'─' * 100}")
            print(result.message)
            print(f"{'─' * 100}\n")
            
            # 실제 전송
            message_id = sender.send_delay_notification(
                news_type='newyork-market-watch',
                current_data=current_data['newyork-market-watch'],
                delay_minutes=5,
                priority=MessagePriority.HIGH
            )
            print(f"📤 전송 결과: {message_id if message_id else '실패'}")
            results.append(("지연 발행 알림 (NEWYORK)", message_id, True))
        else:
            print(f"❌ 생성 실패: {result.errors}")
            results.append(("지연 발행 알림 (NEWYORK)", None, False))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("지연 발행 알림 (NEWYORK)", None, False))
    
    # 3. 지연 발행 알림 메시지 (KOSPI)
    print("\n" + "=" * 100)
    print("3️⃣ 지연 발행 알림 메시지 - KOSPI CLOSE (20251001)")
    print("=" * 100)
    try:
        result = generator.generate_delay_notification_message(
            news_type='kospi-close',
            current_data=current_data['kospi-close'],
            delay_minutes=2
        )
        if result.success:
            print(f"✅ 생성 성공 ({result.generation_time:.3f}초)")
            print(f"BOT: {result.bot_name}")
            print(f"색상: {result.color}")
            print(f"\n{'─' * 100}")
            print(result.message)
            print(f"{'─' * 100}\n")
            
            # 실제 전송
            message_id = sender.send_delay_notification(
                news_type='kospi-close',
                current_data=current_data['kospi-close'],
                delay_minutes=2,
                priority=MessagePriority.HIGH
            )
            print(f"📤 전송 결과: {message_id if message_id else '실패'}")
            results.append(("지연 발행 알림 (KOSPI)", message_id, True))
        else:
            print(f"❌ 생성 실패: {result.errors}")
            results.append(("지연 발행 알림 (KOSPI)", None, False))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("지연 발행 알림 (KOSPI)", None, False))
    
    # 4. 일일 통합 리포트 메시지
    print("\n" + "=" * 100)
    print("4️⃣ 일일 통합 리포트 메시지 (20251001)")
    print("=" * 100)
    try:
        result = generator.generate_daily_integrated_report_message(
            raw_data=current_data,
            report_url="http://127.0.0.1:8000/reports/20251001"
        )
        if result.success:
            print(f"✅ 생성 성공 ({result.generation_time:.3f}초)")
            print(f"BOT: {result.bot_name}")
            print(f"색상: {result.color}")
            print(f"\n{'─' * 100}")
            print(result.message)
            print(f"{'─' * 100}\n")
            
            # 실제 전송
            message_id = sender.send_daily_integrated_report(
                raw_data=current_data,
                report_url="http://127.0.0.1:8000/reports/20251001",
                priority=MessagePriority.NORMAL
            )
            print(f"📤 전송 결과: {message_id if message_id else '실패'}")
            results.append(("일일 통합 리포트", message_id, True))
        else:
            print(f"❌ 생성 실패: {result.errors}")
            results.append(("일일 통합 리포트", None, False))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("일일 통합 리포트", None, False))
    
    # 5. 정시 발행 알림 메시지
    print("\n" + "=" * 100)
    print("5️⃣ 정시 발행 알림 메시지 (20251001)")
    print("=" * 100)
    try:
        result = generator.generate_status_notification_message(
            raw_data=current_data
        )
        if result.success:
            print(f"✅ 생성 성공 ({result.generation_time:.3f}초)")
            print(f"BOT: {result.bot_name}")
            print(f"색상: {result.color}")
            print(f"\n{'─' * 100}")
            print(result.message)
            print(f"{'─' * 100}\n")
            
            # 실제 전송
            message_id = sender.send_status_notification(
                raw_data=current_data,
                priority=MessagePriority.NORMAL
            )
            print(f"📤 전송 결과: {message_id if message_id else '실패'}")
            results.append(("정시 발행 알림", message_id, True))
        else:
            print(f"❌ 생성 실패: {result.errors}")
            results.append(("정시 발행 알림", None, False))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("정시 발행 알림", None, False))
    
    # 6. 데이터 갱신 없음 알림 메시지
    print("\n" + "=" * 100)
    print("6️⃣ 데이터 갱신 없음 알림 메시지 (20251001)")
    print("=" * 100)
    try:
        result = generator.generate_no_data_notification_message(
            raw_data=current_data
        )
        if result.success:
            print(f"✅ 생성 성공 ({result.generation_time:.3f}초)")
            print(f"BOT: {result.bot_name}")
            print(f"색상: {result.color}")
            print(f"\n{'─' * 100}")
            print(result.message)
            print(f"{'─' * 100}\n")
            
            # 실제 전송
            message_id = sender.send_no_data_notification(
                raw_data=current_data,
                priority=MessagePriority.LOW
            )
            print(f"📤 전송 결과: {message_id if message_id else '실패'}")
            results.append(("데이터 갱신 없음", message_id, True))
        else:
            print(f"❌ 생성 실패: {result.errors}")
            results.append(("데이터 갱신 없음", None, False))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("데이터 갱신 없음", None, False))
    
    # 7. 워치햄스터 오류 알림
    print("\n" + "=" * 100)
    print("7️⃣ 워치햄스터 오류 알림 (20251001)")
    print("=" * 100)
    try:
        message_id = sender.send_watchhamster_error(
            error_message="[20251001] API 연결 타임아웃 발생",
            error_details={
                "날짜": "2025-10-01",
                "오류 코드": "TIMEOUT_001",
                "재시도 횟수": "3회",
                "마지막 시도": "16:51:00"
            },
            priority=MessagePriority.CRITICAL
        )
        print(f"✅ 생성 및 전송 성공")
        print(f"📤 전송 결과: {message_id if message_id else '실패'}")
        results.append(("워치햄스터 오류", message_id, True))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("워치햄스터 오류", None, False))
    
    # 8. 워치햄스터 상태 알림
    print("\n" + "=" * 100)
    print("8️⃣ 워치햄스터 상태 알림 (20251001)")
    print("=" * 100)
    try:
        message_id = sender.send_watchhamster_status(
            status_message="[20251001] 시스템 정상 작동 중",
            status_details={
                "날짜": "2025-10-01",
                "모니터링 상태": "활성",
                "처리된 뉴스": "3건",
                "전송 성공률": "100%",
                "마지막 체크": "16:51:00"
            },
            priority=MessagePriority.NORMAL
        )
        print(f"✅ 생성 및 전송 성공")
        print(f"📤 전송 결과: {message_id if message_id else '실패'}")
        results.append(("워치햄스터 상태", message_id, True))
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        results.append(("워치햄스터 상태", None, False))
    
    # 큐 처리 대기
    print("\n" + "=" * 100)
    print("⏳ 메시지 큐 처리 중...")
    print("=" * 100)
    import time
    time.sleep(3)
    
    # 최종 결과 요약
    print("\n" + "=" * 100)
    print("📊 최종 결과 요약")
    print("=" * 100)
    
    success_count = sum(1 for _, mid, _ in results if mid)
    total_count = len(results)
    
    print(f"\n총 테스트: {total_count}개")
    print(f"성공: {success_count}개")
    print(f"실패: {total_count - success_count}개")
    print(f"성공률: {success_count / total_count * 100:.1f}%\n")
    
    print("상세 결과:")
    for i, (name, message_id, success) in enumerate(results, 1):
        status = "✅" if message_id else "❌"
        print(f"{i}. {status} {name}: {message_id if message_id else '전송 실패'}")
    
    # 큐 상태 확인
    print("\n" + "=" * 100)
    print("📋 웹훅 큐 상태")
    print("=" * 100)
    queue_status = sender.get_queue_status()
    print(f"큐 크기: {queue_status['queue_size']}")
    print(f"실패 메시지: {queue_status['failed_messages_count']}")
    print(f"캐시 크기: {queue_status['cache_size']}")
    print(f"실행 중: {queue_status['is_running']}")
    
    # 전송 통계
    print("\n" + "=" * 100)
    print("📈 전송 통계")
    print("=" * 100)
    stats = sender.get_send_statistics()
    print(f"총 전송: {stats['total_sent']}")
    print(f"성공: {stats['successful_sends']}")
    print(f"실패: {stats['failed_sends']}")
    if stats['total_sent'] > 0:
        print(f"성공률: {stats['successful_sends'] / stats['total_sent'] * 100:.1f}%")
    
    # 종료
    print("\n" + "=" * 100)
    print("🏁 테스트 완료")
    print("=" * 100)
    print(f"테스트 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sender.shutdown()

if __name__ == "__main__":
    test_all_messages()
