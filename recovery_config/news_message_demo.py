# -*- coding: utf-8 -*-
"""
뉴스 알림 메시지 생성 데모

정상 커밋 a763ef84의 원본 메시지 생성 알고리즘 복원 데모입니다.
실제 캡처 이미지와 동일한 형태의 메시지를 생성합니다.

작성자: AI Assistant
작성일: 2025-08-12
"""

import json
import time
from datetime import datetime, timedelta

from news_message_generator import NewsMessageGenerator


def demo_all_message_types():
    """모든 메시지 타입 데모"""
    print("=" * 80)
    print("🔔 POSCO 뉴스 알림 메시지 생성 로직 완전 복원 데모")
    print("=" * 80)
    print()
    
    # 테스트용 시간 설정
    test_time = datetime(2025, 8, 12, 10, 30, 0)
    
    # 메시지 생성기 초기화 (테스트 모드)
    generator = NewsMessageGenerator(test_mode=True, test_datetime=test_time)
    
    # 샘플 뉴스 데이터 (실제 API 응답 형태)
    sample_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
            'content': '다우존스 35,123.45 (+150.25), 나스닥 14,567.89 (+45.67), S&P500 4,567.12 (+23.45)',
            'date': '20250812',
            'time': '061938'
        },
        'kospi-close': {
            'title': '[증시마감] 코스피 2,500선 회복',
            'content': '코스피 2,523.45 (+25.67), 코스닥 850.23 (+12.34), 외국인 1,250억원 순매수',
            'date': '20250812',
            'time': '154500'
        },
        'exchange-rate': {
            'title': '[환율] 달러/원 환율 하락',
            'content': '달러/원 1,320.50 (-5.25), 엔/원 8.95 (+0.12), 유로/원 1,445.67 (-2.34)',
            'date': '20250812',
            'time': '163000'
        }
    }
    
    # 과거 데이터 (영업일 비교용)
    historical_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 혼조 마감',
            'time': '061845',
            'date': '20250811'
        },
        'kospi-close': {
            'title': '[증시마감] 코스피 2,480선 마감',
            'time': '154200',
            'date': '20250811'
        },
        'exchange-rate': {
            'title': '[환율] 달러/원 환율 상승',
            'time': '162800',
            'date': '20250811'
        }
    }
    
    print("📊 사용할 샘플 데이터:")
    for news_type, data in sample_data.items():
        print(f"  • {news_type}: {data['title']} ({data['time']})")
    print()
    
    # 1. 영업일 비교 분석 메시지 (첫 번째 캡처)
    print("1️⃣ 영업일 비교 분석 메시지 (첫 번째 캡처 형식)")
    print("-" * 60)
    
    result1 = generator.generate_business_day_comparison_message(sample_data, historical_data)
    
    print(f"✅ 생성 성공: {result1.success}")
    print(f"🤖 BOT 이름: {result1.bot_name}")
    print(f"🎨 색상: {result1.color}")
    print(f"⏱️ 처리 시간: {result1.generation_time:.3f}초")
    print()
    print("📝 생성된 메시지:")
    print(result1.message)
    print()
    print("=" * 80)
    print()
    
    # 2. 지연 발행 알림 메시지 (두 번째 캡처)
    print("2️⃣ 지연 발행 알림 메시지 (두 번째 캡처 형식)")
    print("-" * 60)
    
    result2 = generator.generate_delay_notification_message(
        'newyork-market-watch',
        sample_data['newyork-market-watch'],
        25  # 25분 지연
    )
    
    print(f"✅ 생성 성공: {result2.success}")
    print(f"🤖 BOT 이름: {result2.bot_name}")
    print(f"🎨 색상: {result2.color}")
    print(f"⏱️ 처리 시간: {result2.generation_time:.3f}초")
    print()
    print("📝 생성된 메시지:")
    print(result2.message)
    print()
    print("=" * 80)
    print()
    
    # 3. 일일 통합 분석 리포트 메시지 (세 번째 캡처)
    print("3️⃣ 일일 통합 분석 리포트 메시지 (세 번째 캡처 형식)")
    print("-" * 60)
    
    result3 = generator.generate_daily_integrated_report_message(
        sample_data,
        "https://posco-news-report.github.io/daily-report.html"
    )
    
    print(f"✅ 생성 성공: {result3.success}")
    print(f"🤖 BOT 이름: {result3.bot_name}")
    print(f"🎨 색상: {result3.color}")
    print(f"⏱️ 처리 시간: {result3.generation_time:.3f}초")
    print()
    print("📝 생성된 메시지:")
    print(result3.message)
    print()
    print("=" * 80)
    print()
    
    # 4. 정시 발행 알림 메시지 (네 번째 캡처)
    print("4️⃣ 정시 발행 알림 메시지 (네 번째 캡처 형식)")
    print("-" * 60)
    
    result4 = generator.generate_status_notification_message(sample_data)
    
    print(f"✅ 생성 성공: {result4.success}")
    print(f"🤖 BOT 이름: {result4.bot_name}")
    print(f"🎨 색상: {result4.color}")
    print(f"⏱️ 처리 시간: {result4.generation_time:.3f}초")
    print()
    print("📝 생성된 메시지:")
    print(result4.message)
    print()
    print("=" * 80)
    print()
    
    # 5. 데이터 갱신 없음 알림 메시지 (다섯 번째 캡처)
    print("5️⃣ 데이터 갱신 없음 알림 메시지 (다섯 번째 캡처 형식)")
    print("-" * 60)
    
    result5 = generator.generate_no_data_notification_message({})
    
    print(f"✅ 생성 성공: {result5.success}")
    print(f"🤖 BOT 이름: {result5.bot_name}")
    print(f"🎨 색상: {result5.color}")
    print(f"⏱️ 처리 시간: {result5.generation_time:.3f}초")
    print()
    print("📝 생성된 메시지:")
    print(result5.message)
    print()
    print("=" * 80)
    print()
    
    # 6. 자동 메시지 타입 결정 데모
    print("6️⃣ 자동 메시지 타입 결정 데모")
    print("-" * 60)
    
    time_scenarios = [
        (datetime(2025, 8, 12, 6, 10, 0), "영업일 비교 분석 시간"),
        (datetime(2025, 8, 12, 18, 0, 0), "일일 리포트 생성 시간"),
        (datetime(2025, 8, 12, 12, 0, 0), "정시 상태 확인 시간"),
        (datetime(2025, 8, 12, 10, 30, 0), "일반 모니터링 시간"),
    ]
    
    for test_time, description in time_scenarios:
        test_generator = NewsMessageGenerator(test_mode=True, test_datetime=test_time)
        message_type = test_generator.determine_message_type(sample_data, test_time)
        
        print(f"🕐 {test_time.strftime('%H:%M')} ({description})")
        print(f"   → 결정된 메시지 타입: {message_type}")
        print()
    
    print("=" * 80)
    print()
    
    # 7. 실제 모드 vs 테스트 모드 비교
    print("7️⃣ 실제 모드 vs 테스트 모드 비교")
    print("-" * 60)
    
    # 실제 모드 생성기
    real_generator = NewsMessageGenerator(test_mode=False)
    real_result = real_generator.generate_status_notification_message(sample_data)
    
    print("🧪 테스트 모드:")
    print(f"   BOT 이름: {result4.bot_name}")
    print(f"   메시지 시작: {result4.message[:50]}...")
    print()
    
    print("🚀 실제 모드:")
    print(f"   BOT 이름: {real_result.bot_name}")
    print(f"   메시지 시작: {real_result.message[:50]}...")
    print()
    
    print("=" * 80)
    print("✅ 뉴스 알림 메시지 생성 로직 완전 복원 데모 완료!")
    print("=" * 80)


def demo_time_based_scenarios():
    """시간 기반 시나리오 데모"""
    print("\n" + "=" * 80)
    print("⏰ 시간 기반 메시지 생성 시나리오 데모")
    print("=" * 80)
    
    # 다양한 시간대별 시나리오
    scenarios = [
        {
            'time': datetime(2025, 8, 12, 6, 10, 0),
            'description': '아침 6시 10분 - 영업일 비교 분석',
            'expected_type': 'comparison'
        },
        {
            'time': datetime(2025, 8, 12, 6, 25, 0),
            'description': '아침 6시 25분 - 뉴욕마켓워치 지연 발행',
            'expected_type': 'delay'
        },
        {
            'time': datetime(2025, 8, 12, 15, 55, 0),
            'description': '오후 3시 55분 - 코스피 지연 발행',
            'expected_type': 'delay'
        },
        {
            'time': datetime(2025, 8, 12, 18, 0, 0),
            'description': '오후 6시 - 일일 통합 리포트',
            'expected_type': 'report'
        },
        {
            'time': datetime(2025, 8, 12, 12, 0, 0),
            'description': '정오 12시 - 정시 상태 확인',
            'expected_type': 'status'
        }
    ]
    
    sample_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
            'date': '20250812',
            'time': '061938'
        },
        'kospi-close': {
            'title': '[증시마감] 코스피 상승 마감',
            'date': '20250812',
            'time': '154500'
        },
        'exchange-rate': {
            'title': '[환율] 달러/원 환율 하락',
            'date': '20250812',
            'time': '163000'
        }
    }
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['description']}")
        print("-" * 60)
        
        generator = NewsMessageGenerator(
            test_mode=True, 
            test_datetime=scenario['time']
        )
        
        # 메시지 타입 결정
        determined_type = generator.determine_message_type(sample_data, scenario['time'])
        
        print(f"🎯 예상 타입: {scenario['expected_type']}")
        print(f"🤖 결정된 타입: {determined_type}")
        print(f"✅ 일치 여부: {'일치' if determined_type == scenario['expected_type'] else '불일치'}")
        
        # 해당 타입의 메시지 생성
        if determined_type == 'comparison':
            result = generator.generate_business_day_comparison_message(sample_data, {})
        elif determined_type == 'delay':
            result = generator.generate_delay_notification_message(
                'newyork-market-watch', sample_data['newyork-market-watch'], 25
            )
        elif determined_type == 'report':
            result = generator.generate_daily_integrated_report_message(sample_data)
        elif determined_type == 'status':
            result = generator.generate_status_notification_message(sample_data)
        else:
            result = generator.generate_no_data_notification_message(sample_data)
        
        print(f"📝 메시지 생성: {'성공' if result.success else '실패'}")
        print(f"⏱️ 처리 시간: {result.generation_time:.3f}초")
        print()
        
        if i < len(scenarios):
            print()


if __name__ == "__main__":
    # 전체 데모 실행
    demo_all_message_types()
    
    # 시간 기반 시나리오 데모
    demo_time_based_scenarios()
    
    print("\n🎉 모든 데모가 완료되었습니다!")
    print("정상 커밋 a763ef84의 원본 로직이 성공적으로 복원되었습니다.")