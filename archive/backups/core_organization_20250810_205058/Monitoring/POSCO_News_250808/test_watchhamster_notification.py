#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Watchhamster Notification
POSCO 시스템 테스트

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import requests
import system_functionality_verification.py
import posco_news_250808_monitor.log

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from .git/config import .naming_backup/config_data_backup/watchhamster.log, BOT_PROFILE_IMAGE_URL
    
    def test_watchhamster_notification():
        """WatchHamster v3.0 알림 테스트"""
        message = "🧪 WatchHamster v3.0 알림 테스트/n/n테스트 시간: 2025-08-06 13:20:00/n상태: 정상 작동 테스트"
        
        payload = {
            "botName": "POSCO WatchHamster v3.0 🐹🛡️",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": message.split('/n')[0],
            "attachments": [{
                "color": "#28a745",
                "text": message
            }]
        }
        
        print("🧪 WatchHamster v3.0 알림 테스트 시작...")
        print(f"📡 웹훅 URL: {WATCHHAMSTER_WEBHOOK_URL}")
        print(f"🤖 봇 이름: {payload['botName']}")
        print(f"📝 메시지: {message.split(chr(10))[0]}")
        
        try:
            response = requests.post(
                WATCHHAMSTER_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ 알림 전송 성공!")
                print("📱 Dooray에서 알림을 확인하세요.")
            else:
                print(f"❌ 알림 전송 실패: HTTP {response.status_code}")
                print(f"📄 응답: {response.text}")
                
        except Exception as e:
            print(f"❌ 알림 전송 오류: {e}")
    
    if __name__ == "__main__":
        test_watchhamster_notification()
        
except ImportError as e:
# REMOVED:     print(f"❌ 모듈 import 오류: {e}")