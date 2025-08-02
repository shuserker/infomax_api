#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dooray 버튼 기능 조사 스크립트
버튼이 어떤 용도인지 파악하기 위한 테스트
"""

import requests
import json
from config import DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL

def test_button_types():
    """다양한 버튼 타입 테스트"""
    
    # 테스트 1: 일반 HTTP URL
    payload1 = {
        "botName": "POSCO 뉴스 🔍",
        "botIconImage": BOT_PROFILE_IMAGE_URL,
        "text": "버튼 테스트 1: HTTP URL",
        "attachments": [{
            "color": "#28a745",
            "text": "HTTP URL 버튼 테스트",
            "actions": [
                {
                    "type": "button",
                    "text": "🌐 Google",
                    "url": "https://www.google.com",
                    "style": "primary"
                }
            ]
        }]
    }
    
    # 테스트 2: HTTPS URL
    payload2 = {
        "botName": "POSCO 뉴스 🔍",
        "botIconImage": BOT_PROFILE_IMAGE_URL,
        "text": "버튼 테스트 2: HTTPS URL",
        "attachments": [{
            "color": "#28a745",
            "text": "HTTPS URL 버튼 테스트",
            "actions": [
                {
                    "type": "button",
                    "text": "🔒 GitHub",
                    "url": "https://github.com",
                    "style": "primary"
                }
            ]
        }]
    }
    
    # 테스트 3: 로컬호스트 URL
    payload3 = {
        "botName": "POSCO 뉴스 🔍",
        "botIconImage": BOT_PROFILE_IMAGE_URL,
        "text": "버튼 테스트 3: 로컬호스트 URL",
        "attachments": [{
            "color": "#28a745",
            "text": "로컬호스트 URL 버튼 테스트",
            "actions": [
                {
                    "type": "button",
                    "text": "🏠 로컬호스트",
                    "url": "http://localhost:8080",
                    "style": "primary"
                }
            ]
        }]
    }
    
    # 테스트 4: 버튼 없이 (비교용)
    payload4 = {
        "botName": "POSCO 뉴스 🔍",
        "botIconImage": BOT_PROFILE_IMAGE_URL,
        "text": "버튼 테스트 4: 버튼 없음 (비교용)",
        "attachments": [{
            "color": "#28a745",
            "text": "버튼이 없는 일반 메시지"
        }]
    }
    
    # 테스트 5: 다른 타입 시도
    payload5 = {
        "botName": "POSCO 뉴스 🔍",
        "botIconImage": BOT_PROFILE_IMAGE_URL,
        "text": "버튼 테스트 5: 다른 타입",
        "attachments": [{
            "color": "#28a745",
            "text": "다른 타입 버튼 테스트",
            "actions": [
                {
                    "type": "select",  # button 대신 select
                    "text": "선택하세요",
                    "options": [
                        {"text": "옵션 1", "value": "1"},
                        {"text": "옵션 2", "value": "2"}
                    ]
                }
            ]
        }]
    }
    
    payloads = [
        ("HTTP URL 버튼", payload1),
        ("HTTPS URL 버튼", payload2),
        ("로컬호스트 URL 버튼", payload3),
        ("버튼 없음", payload4),
        ("다른 타입 버튼", payload5)
    ]
    
    for name, payload in payloads:
        print(f"\n🧪 테스트: {name}")
        
        try:
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {name} 전송 성공")
            else:
                print(f"❌ {name} 전송 실패: {response.status_code}")
                print(f"응답: {response.text}")
                
        except Exception as e:
            print(f"❌ {name} 전송 오류: {e}")

def investigate_dooray_button_spec():
    """Dooray 버튼 스펙 조사"""
    print("🔍 Dooray 웹훅 버튼 스펙 조사")
    print("=" * 50)
    
    print("📋 알려진 정보:")
    print("- 마크다운 링크: ✅ 작동함")
    print("- 버튼 형식: ❌ 500 오류 발생")
    print("- 버튼은 전송은 성공하지만 클릭 시 500 오류")
    
    print("\n🤔 가능한 원인들:")
    print("1. 버튼이 외부 URL 접근용이 아닐 수 있음")
    print("2. 버튼이 Dooray 내부 기능용일 수 있음")
    print("3. 버튼이 특정 도메인만 허용할 수 있음")
    print("4. 버튼이 인증이 필요한 기능일 수 있음")
    
    print("\n💡 권장 해결책:")
    print("- 마크다운 링크 사용 (이미 작동 확인됨)")
    print("- 버튼은 장식용으로만 사용")
    print("- 실제 링크는 마크다운으로 제공")

if __name__ == "__main__":
    investigate_dooray_button_spec()
    print("\n" + "="*50)
    test_button_types()