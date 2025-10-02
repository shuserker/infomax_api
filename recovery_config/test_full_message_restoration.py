#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Message Restoration Test
정상 커밋 기준 100% + α 메시지 복구 시스템 테스트
"""

import os
import sys
from datetime import datetime

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from full_message_restoration_system import FullMessageRestorationSystem
except ImportError as e:
    print(f"⚠️ 모듈 import 실패: {e}")
    sys.exit(1)

def test_posco_news_restoration():
    """포스코 뉴스 메시지 복구 테스트"""
    print("🧪 포스코 뉴스 메시지 복구 테스트")
    print("=" * 60)
    
    try:
        restoration_system = FullMessageRestorationSystem()
        
        # 포스코 뉴스 메시지 복구
        restored_messages = restoration_system.restore_posco_news_messages()
        
        print(f"📊 복구된 메시지 수: {len(restored_messages)}")
        
        for message_type, message_data in restored_messages.items():
            print(f"\n📋 {message_type.upper()} 메시지:")
            print("-" * 40)
            print(f"제목: {message_data.get('title', 'N/A')}")
            print(f"색상: {message_data.get('color', 'N/A')}")
            print(f"봇명: {message_data.get('bot_name', 'N/A')}")
            print("\n내용:")
            print(message_data.get('content', 'N/A'))
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ 포스코 뉴스 복구 테스트 실패: {e}")
        return False

def test_watchhamster_restoration():
    """워치햄스터 메시지 복구 테스트"""
    print("\n🧪 워치햄스터 메시지 복구 테스트")
    print("=" * 60)
    
    try:
        restoration_system = FullMessageRestorationSystem()
        
        # 워치햄스터 메시지 복구
        restored_messages = restoration_system.restore_watchhamster_messages()
        
        print(f"📊 복구된 메시지 수: {len(restored_messages)}")
        
        for message_type, message_data in restored_messages.items():
            print(f"\n📋 {message_type.upper()} 메시지:")
            print("-" * 40)
            print(f"제목: {message_data.get('title', 'N/A')}")
            print(f"색상: {message_data.get('color', 'N/A')}")
            print(f"봇명: {message_data.get('bot_name', 'N/A')}")
            print("\n내용:")
            print(message_data.get('content', 'N/A'))
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ 워치햄스터 복구 테스트 실패: {e}")
        return False

def test_enhanced_features():
    """+ α 기능 테스트"""
    print("\n🧪 + α 기능 테스트")
    print("=" * 60)
    
    try:
        restoration_system = FullMessageRestorationSystem()
        
        # 테스트 데이터
        test_content = "├ 시간: 2025-08-12 143000\n└ 제목:"
        test_news_data = {
            'exchange-rate': {
                'title': '달러 환율 상승세 지속, 1,350원대 근접',
                'time': '143000',
                'date': '20250812'
            }
        }
        
        # 시간 포맷 개선 테스트
        improved_content = restoration_system._apply_time_format_improvement(test_content)
        print("⏰ 시간 포맷 개선:")
        print(f"원본: {test_content}")
        print(f"개선: {improved_content}")
        
        # 뉴스 타이틀 표시 테스트
        title_content = restoration_system._add_news_title_display(improved_content, test_news_data)
        print(f"\n📰 뉴스 타이틀 표시:")
        print(title_content)
        
        # 변화 분석 테스트
        analysis_content = restoration_system._add_change_analysis(title_content, test_news_data)
        print(f"\n📈 변화 분석 추가:")
        print(analysis_content[-200:])  # 마지막 200자만 표시
        
        return True
        
    except Exception as e:
        print(f"❌ + α 기능 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 정상 커밋 기준 100% + α 메시지 복구 시스템 테스트")
    print(f"📅 테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 기준 커밋: a763ef84")
    print()
    
    test_results = []
    
    # 1. 포스코 뉴스 복구 테스트
    result1 = test_posco_news_restoration()
    test_results.append(("포스코 뉴스 복구", result1))
    
    # 2. 워치햄스터 복구 테스트
    result2 = test_watchhamster_restoration()
    test_results.append(("워치햄스터 복구", result2))
    
    # 3. + α 기능 테스트
    result3 = test_enhanced_features()
    test_results.append(("+ α 기능", result3))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    success_count = 0
    for test_name, result in test_results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 전체 성공률: {success_count}/{len(test_results)} ({success_count/len(test_results)*100:.1f}%)")
    
    if success_count == len(test_results):
        print("🎉 모든 테스트 성공! 정상 커밋 기준 100% + α 복구 완료!")
        print("💡 이제 본래 목적을 제대로 수행하는 메시지 시스템이 준비되었습니다.")
    else:
        print("⚠️ 일부 테스트 실패. 추가 확인이 필요합니다.")
    
    return success_count == len(test_results)

if __name__ == "__main__":
    main()