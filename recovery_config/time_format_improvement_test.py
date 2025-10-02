#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시간 포맷 개선 테스트

시간 포맷 변환 기능이 제대로 작동하는지 확인합니다.
"""

import os
import sys

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from news_message_generator import NewsMessageGenerator
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


def test_time_format_conversion():
    """시간 포맷 변환 테스트"""
    print("🧪 시간 포맷 변환 테스트")
    print("=" * 40)
    
    # 테스트 케이스
    test_cases = [
        ("063000", "06:30"),  # HHMMSS
        ("154000", "15:40"),  # HHMMSS
        ("1530", "15:30"),    # HHMM
        ("630", "06:30"),     # HMM
        ("06:30", "06:30"),   # 이미 올바른 형태
        ("15:40", "15:40"),   # 이미 올바른 형태
        ("", "시간 정보 없음"),  # 빈 문자열
        ("invalid", "invalid") # 잘못된 형태
    ]
    
    for input_time, expected in test_cases:
        result = NewsMessageGenerator.format_time_string(input_time)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_time}' → '{result}' (예상: '{expected}')")
    
    print()


def test_message_generation_with_time_format():
    """시간 포맷이 적용된 메시지 생성 테스트"""
    print("🧪 시간 포맷이 적용된 메시지 생성 테스트")
    print("=" * 50)
    
    # 메시지 생성기 초기화
    generator = NewsMessageGenerator(test_mode=True)
    
    # 테스트 데이터 (HHMMSS 형태의 시간)
    test_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
            'content': '다우존스 35,123.45 (+150.25)',
            'time': '063000',  # HHMMSS 형태
            'publish_time': '06:30'
        },
        'kospi-close': {
            'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
            'content': '코스피 지수 상승 마감',
            'time': '154000',  # HHMMSS 형태
            'publish_time': '15:40'
        },
        'exchange-rate': {
            'title': '[환율] 달러/원 1,320.50 (+2.30)',
            'content': '달러 강세 지속',
            'time': '153000',  # HHMMSS 형태
            'publish_time': '15:30'
        }
    }
    
    # 1. 지연 발행 알림 테스트
    print("1. 지연 발행 알림 메시지:")
    delay_result = generator.generate_delay_notification_message(
        'kospi-close',
        {
            'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
            'time': '162500'  # 16:25:00 → 16:25로 변환되어야 함
        },
        45
    )
    
    if delay_result.success:
        print("✅ 메시지 생성 성공")
        print("메시지 내용:")
        print(delay_result.message)
        print()
        
        # 시간 포맷이 올바르게 변환되었는지 확인
        if "16:25" in delay_result.message:
            print("✅ 시간 포맷 변환 성공: 162500 → 16:25")
        else:
            print("❌ 시간 포맷 변환 실패")
    else:
        print("❌ 메시지 생성 실패")
        print(f"오류: {delay_result.errors}")
    
    print("-" * 50)
    
    # 2. 일일 통합 리포트 테스트
    print("2. 일일 통합 분석 리포트 메시지:")
    report_result = generator.generate_daily_integrated_report_message(test_data)
    
    if report_result.success:
        print("✅ 메시지 생성 성공")
        print("메시지 내용:")
        print(report_result.message)
        print()
        
        # 시간 포맷이 올바르게 변환되었는지 확인
        time_formats_found = []
        if "06:30" in report_result.message:
            time_formats_found.append("063000 → 06:30")
        if "15:40" in report_result.message:
            time_formats_found.append("154000 → 15:40")
        if "15:30" in report_result.message:
            time_formats_found.append("153000 → 15:30")
        
        if time_formats_found:
            print("✅ 시간 포맷 변환 성공:")
            for fmt in time_formats_found:
                print(f"  • {fmt}")
        else:
            print("❌ 시간 포맷 변환 실패")
    else:
        print("❌ 메시지 생성 실패")
        print(f"오류: {report_result.errors}")
    
    print("-" * 50)
    
    # 3. 데이터 갱신 없음 알림 테스트
    print("3. 데이터 갱신 없음 알림 메시지:")
    no_data_result = generator.generate_no_data_notification_message(test_data)
    
    if no_data_result.success:
        print("✅ 메시지 생성 성공")
        print("메시지 내용:")
        print(no_data_result.message)
        print()
        
        # 시간 포맷이 올바르게 변환되었는지 확인
        time_formats_found = []
        if "06:30" in no_data_result.message:
            time_formats_found.append("063000 → 06:30")
        if "15:40" in no_data_result.message:
            time_formats_found.append("154000 → 15:40")
        if "15:30" in no_data_result.message:
            time_formats_found.append("153000 → 15:30")
        
        if time_formats_found:
            print("✅ 시간 포맷 변환 성공:")
            for fmt in time_formats_found:
                print(f"  • {fmt}")
        else:
            print("❌ 시간 포맷 변환 실패")
    else:
        print("❌ 메시지 생성 실패")
        print(f"오류: {no_data_result.errors}")


def main():
    """메인 실행 함수"""
    print("🚀 시간 포맷 개선 테스트 시작")
    print()
    
    # 1. 시간 포맷 변환 함수 테스트
    test_time_format_conversion()
    
    # 2. 메시지 생성에서 시간 포맷 적용 테스트
    test_message_generation_with_time_format()
    
    print("🎉 시간 포맷 개선 테스트 완료!")


if __name__ == "__main__":
    main()