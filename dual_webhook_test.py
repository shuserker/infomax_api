#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이중 웹훅 테스트 스크립트
DOORAY_WEBHOOK_URL과 WATCHHAMSTER_WEBHOOK_URL 각각 테스트
"""

import requests
import json
from datetime import datetime
import sys
import os

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'core', 'monitoring'))

try:
    from core.monitoring.config import DOORAY_WEBHOOK_URL, WATCHHAMSTER_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
    print("✅ 설정 파일 로드 성공")
except ImportError as e:
    print(f"❌ 설정 파일 로드 실패: {e}")
    sys.exit(1)

def send_test_message(webhook_url, webhook_name, test_type):
    """지정된 웹훅 URL로 테스트 메시지 전송"""
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 테스트 메시지 구성
    if test_type == "news":
        # POSCO News 알림용 메시지
        payload = {
            "botName": "POSCO News 알림 🗞️",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": f"📰 **POSCO News 시스템 테스트**\n\n"
                   f"**테스트 시간**: {current_time}\n"
                   f"**웹훅 대상**: {webhook_name}\n"
                   f"**테스트 유형**: 뉴스 알림 테스트\n\n"
                   f"🔍 **테스트 내용**:\n"
                   f"• 뉴욕마켓워치 📈\n"
                   f"• 증시마감 📊\n"
                   f"• 서환마감 💱\n\n"
                   f"✅ POSCO News 알림 시스템이 정상 작동 중입니다.",
            "color": "good"
        }
    else:
        # 워치햄스터 시스템 알림용 메시지
        payload = {
            "botName": "POSCO 워치햄스터 🐹🛡️",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": f"🛡️ **POSCO 워치햄스터 시스템 테스트**\n\n"
                   f"**테스트 시간**: {current_time}\n"
                   f"**웹훅 대상**: {webhook_name}\n"
                   f"**테스트 유형**: 시스템 상태 알림 테스트\n\n"
                   f"📊 **시스템 현황**:\n"
                   f"• 모니터링 상태: 🟢 정상\n"
                   f"• API 연결: ✅ 연결됨\n"
                   f"• 데이터 수집: 🔄 진행 중\n"
                   f"• 웹훅 전송: ✅ 정상\n\n"
                   f"🎯 **복원 완료 기능**:\n"
                   f"• 정기 상태 보고 ✅\n"
                   f"• 오류 알림 ✅\n"
                   f"• 긴급 알림 ✅\n"
                   f"• 복구 성공 알림 ✅\n\n"
                   f"🐹 워치햄스터가 시스템을 안전하게 지키고 있습니다!",
            "color": "good"
        }
    
    try:
        print(f"\n📤 {webhook_name}로 테스트 메시지 전송 중...")
        print(f"🔗 URL: {webhook_url[:50]}...")
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {webhook_name} 테스트 성공!")
            print(f"   HTTP 상태: {response.status_code}")
            print(f"   응답 시간: {response.elapsed.total_seconds():.2f}초")
            return True
        else:
            print(f"❌ {webhook_name} 테스트 실패!")
            print(f"   HTTP 상태: {response.status_code}")
            print(f"   응답 내용: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ {webhook_name} 테스트 타임아웃!")
        return False
    except requests.exceptions.RequestException as e:
        print(f"🚨 {webhook_name} 테스트 중 오류: {e}")
        return False

def main():
    """메인 테스트 실행"""
    
    print("🚀 POSCO 이중 웹훅 시스템 테스트 시작")
    print("=" * 60)
    
    # 웹훅 URL 정보 출력
    print(f"📋 테스트 대상:")
    print(f"1. DOORAY_WEBHOOK_URL (POSCO News 알림용)")
    print(f"   URL: {DOORAY_WEBHOOK_URL[:50]}...")
    print(f"2. WATCHHAMSTER_WEBHOOK_URL (워치햄스터 전용)")
    print(f"   URL: {WATCHHAMSTER_WEBHOOK_URL[:50]}...")
    print()
    
    test_results = []
    
    # 1. DOORAY_WEBHOOK_URL 테스트 (POSCO News 알림용)
    print("🗞️ 1단계: POSCO News 알림 웹훅 테스트")
    print("-" * 40)
    result1 = send_test_message(
        DOORAY_WEBHOOK_URL, 
        "DOORAY_WEBHOOK_URL (POSCO News 알림용)", 
        "news"
    )
    test_results.append(("DOORAY_WEBHOOK_URL", result1))
    
    # 2. WATCHHAMSTER_WEBHOOK_URL 테스트 (워치햄스터 전용)
    print("\n🐹 2단계: 워치햄스터 시스템 웹훅 테스트")
    print("-" * 40)
    result2 = send_test_message(
        WATCHHAMSTER_WEBHOOK_URL, 
        "WATCHHAMSTER_WEBHOOK_URL (워치햄스터 전용)", 
        "watchhamster"
    )
    test_results.append(("WATCHHAMSTER_WEBHOOK_URL", result2))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    success_count = 0
    for webhook_name, result in test_results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{status} {webhook_name}")
        if result:
            success_count += 1
    
    print(f"\n🎯 전체 성공률: {success_count}/{len(test_results)} ({success_count/len(test_results)*100:.1f}%)")
    
    if success_count == len(test_results):
        print("🎉 모든 웹훅 테스트가 성공했습니다!")
        print("✅ 이중 웹훅 시스템이 정상적으로 작동하고 있습니다.")
        return 0
    else:
        print("⚠️ 일부 웹훅 테스트가 실패했습니다.")
        print("🔧 실패한 웹훅의 URL과 네트워크 연결을 확인해주세요.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)