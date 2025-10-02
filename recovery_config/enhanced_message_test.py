#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 메시지 생성 테스트

뉴스 타이틀, 직전 대비 분석, 예측 기능이 추가된 메시지를 테스트합니다.
"""

import os
import sys
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from news_message_generator import NewsMessageGenerator
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


def test_enhanced_messages():
    """향상된 메시지 생성 테스트"""
    print("🚀 향상된 메시지 생성 테스트 시작")
    print("=" * 60)
    
    # 메시지 생성기 초기화
    generator = NewsMessageGenerator(test_mode=True)
    
    # 테스트 데이터 (현재)
    current_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 강세 지속, 다우 35,200 돌파',
            'content': '다우존스 35,234.56 (+234.56), 나스닥 14,678.90 (+123.45)',
            'time': '063000',
            'publish_time': '06:30'
        },
        'kospi-close': {
            'title': '[코스피마감] 코스피 2,465.75 상승 마감, 외국인 순매수 지속',
            'content': '코스피 지수 2,465.75 (+25.50), 거래량 증가',
            'time': '154000',
            'publish_time': '15:40'
        },
        'exchange-rate': {
            'title': '[환율] 달러/원 1,318.20, 원화 강세 전환',
            'content': '달러/원 1,318.20 (-4.30), 원화 강세 흐름',
            'time': '153000',
            'publish_time': '15:30'
        }
    }
    
    # 테스트 데이터 (과거 - 비교용)
    historical_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 혼조세, 기술주 약세',
            'time': '063000'
        },
        'kospi-close': {
            'title': '[코스피마감] 코스피 2,440.25 하락 마감',
            'time': '154500'  # 5분 지연
        },
        'exchange-rate': {
            'title': '[환율] 달러/원 1,322.50, 달러 강세 지속',
            'time': '153000'
        }
    }
    
    print("📊 1. 향상된 영업일 비교 분석 메시지:")
    print("-" * 50)
    
    comparison_result = generator.generate_business_day_comparison_message(
        current_data, historical_data
    )
    
    if comparison_result.success:
        print("✅ 메시지 생성 성공")
        print("\n메시지 내용:")
        print(comparison_result.message)
        
        # 향상된 기능 확인
        enhancements_found = []
        if "시장 동향 예측" in comparison_result.message:
            enhancements_found.append("✅ 시장 동향 예측")
        if "변화:" in comparison_result.message:
            enhancements_found.append("✅ 직전 대비 변화 분석")
        if "예상:" in comparison_result.message:
            enhancements_found.append("✅ 발행 시간 예측")
        if "종합 분석" in comparison_result.message:
            enhancements_found.append("✅ 종합 분석")
        if any(title[:20] in comparison_result.message for title in [
            current_data['newyork-market-watch']['title'][:20],
            current_data['kospi-close']['title'][:20],
            current_data['exchange-rate']['title'][:20]
        ]):
            enhancements_found.append("✅ 뉴스 타이틀 표시")
        
        print(f"\n🎯 향상된 기능 확인:")
        for enhancement in enhancements_found:
            print(f"  {enhancement}")
        
        if len(enhancements_found) >= 3:
            print("🎉 향상된 기능이 성공적으로 적용되었습니다!")
        else:
            print("⚠️ 일부 향상된 기능이 누락되었습니다.")
    else:
        print("❌ 메시지 생성 실패")
        print(f"오류: {comparison_result.errors}")
    
    print("\n" + "=" * 60)
    print("📊 2. 향상된 정시 발행 알림 메시지:")
    print("-" * 50)
    
    status_result = generator.generate_status_notification_message(current_data)
    
    if status_result.success:
        print("✅ 메시지 생성 성공")
        print("\n메시지 내용:")
        print(status_result.message)
        
        # 뉴스 타이틀 포함 확인
        title_found = any(title[:20] in status_result.message for title in [
            current_data['newyork-market-watch']['title'][:20],
            current_data['kospi-close']['title'][:20],
            current_data['exchange-rate']['title'][:20]
        ])
        
        if title_found:
            print("\n✅ 뉴스 타이틀이 성공적으로 포함되었습니다!")
        else:
            print("\n⚠️ 뉴스 타이틀이 누락되었습니다.")
    else:
        print("❌ 메시지 생성 실패")
        print(f"오류: {status_result.errors}")
    
    print("\n" + "=" * 60)
    print("📊 3. 향상된 일일 통합 분석 리포트:")
    print("-" * 50)
    
    report_result = generator.generate_daily_integrated_report_message(
        current_data, "https://posco-report.example.com/daily"
    )
    
    if report_result.success:
        print("✅ 메시지 생성 성공")
        print("\n메시지 내용:")
        print(report_result.message)
        
        # 향상된 기능 확인
        enhancements_found = []
        if "직전 대비 변화" in report_result.message:
            enhancements_found.append("✅ 직전 대비 변화 분석")
        if "📰" in report_result.message:
            enhancements_found.append("✅ 뉴스 타이틀 표시")
        if "예상:" in report_result.message:
            enhancements_found.append("✅ 발행 시간 예측")
        if "권장사항" in report_result.message:
            enhancements_found.append("✅ 권장사항 제공")
        
        print(f"\n🎯 향상된 기능 확인:")
        for enhancement in enhancements_found:
            print(f"  {enhancement}")
        
        if len(enhancements_found) >= 3:
            print("🎉 향상된 기능이 성공적으로 적용되었습니다!")
        else:
            print("⚠️ 일부 향상된 기능이 누락되었습니다.")
    else:
        print("❌ 메시지 생성 실패")
        print(f"오류: {report_result.errors}")


def test_title_change_analysis():
    """제목 변화 분석 테스트"""
    print("\n" + "=" * 60)
    print("🔍 제목 변화 분석 테스트:")
    print("-" * 50)
    
    generator = NewsMessageGenerator(test_mode=True)
    
    test_cases = [
        (
            "[코스피마감] 코스피 2,465.75 상승 마감",
            "[코스피마감] 코스피 2,440.25 하락 마감",
            "부분 변경 (상승↔하락)"
        ),
        (
            "[뉴욕마켓워치] 미국 증시 강세 지속",
            "[뉴욕마켓워치] 미국 증시 혼조세",
            "부분 변경 (강세↔혼조)"
        ),
        (
            "[환율] 달러/원 1,318.20, 원화 강세",
            "[환율] 달러/원 1,322.50, 달러 강세",
            "부분 변경 (원화↔달러)"
        )
    ]
    
    for current_title, historical_title, expected_type in test_cases:
        result = generator._analyze_title_change(current_title, historical_title)
        print(f"현재: {current_title[:30]}...")
        print(f"직전: {historical_title[:30]}...")
        print(f"분석: {result}")
        print(f"예상: {expected_type}")
        print("-" * 30)


def main():
    """메인 실행 함수"""
    print("🚀 향상된 뉴스 메시지 생성 시스템 테스트")
    print("주요 개선사항:")
    print("  • 뉴스 타이틀 표시")
    print("  • 직전 대비 변화 분석")
    print("  • 시장 동향 예측")
    print("  • 발행 시간 예측")
    print("  • 종합 분석 및 권장사항")
    print()
    
    # 향상된 메시지 생성 테스트
    test_enhanced_messages()
    
    # 제목 변화 분석 테스트
    test_title_change_analysis()
    
    print("\n🎉 향상된 메시지 생성 시스템 테스트 완료!")
    print("모니터링의 핵심 요소인 직전 비교와 예측 기능이 추가되었습니다.")


if __name__ == "__main__":
    main()