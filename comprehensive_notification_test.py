#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종합 알림 시스템 테스트
모든 POSCO 알림 시스템 테스트 (2025-08-06 18:00 기준)

Created: 2025-08-11
"""

import os
import sys
import requests
import json
from datetime import datetime

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'Monitoring', 'POSCO_News_250808'))

try:
    from Monitoring.POSCO_News_250808.config import (
        DOORAY_WEBHOOK_URL, 
        WATCHHAMSTER_WEBHOOK_URL, 
        BOT_PROFILE_IMAGE_URL
    )
    print("✅ 설정 파일 로드 성공")
except ImportError as e:
    print(f"❌ 설정 파일 로드 실패: {e}")
    sys.exit(1)

class ComprehensiveNotificationTester:
    """종합 알림 시스템 테스터"""
    
    def __init__(self):
        self.test_time = "2025-08-06 18:00:00"
        self.results = []
        
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def send_notification(self, webhook_url, bot_name, message, color="#28a745"):
        """알림 전송"""
        if webhook_url is None:
            return False, "웹훅 URL이 None으로 설정됨"
            
        payload = {
            "botName": bot_name,
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": message.split('\n')[0],
            "attachments": [{
                "color": color,
                "text": message
            }]
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "전송 성공"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"전송 오류: {str(e)}"
    
    def test_posco_news_notification(self):
        """POSCO 뉴스 알림 테스트"""
        self.log("🏭 POSCO 뉴스 알림 테스트 시작...")
        
        message = f"""🏭 POSCO 뉴스 시스템 테스트 알림

📅 테스트 시간: {self.test_time}
🔍 테스트 항목: POSCO News 250808 알림 시스템
📊 상태: 정상 작동 확인

📈 뉴스 현황:
• 뉴욕마켓워치: 🌆 최신
• 증시마감: 📈 최신  
• 서환마감: 💱 최신

✅ 모든 시스템이 정상 작동 중입니다."""

        success, result = self.send_notification(
            DOORAY_WEBHOOK_URL,
            "POSCO News Bot 🏭",
            message,
            "#007bff"
        )
        
        self.results.append({
            "test": "POSCO 뉴스 알림",
            "success": success,
            "result": result,
            "webhook": "DOORAY_WEBHOOK_URL"
        })
        
        if success:
            self.log("✅ POSCO 뉴스 알림 전송 성공")
        else:
            self.log(f"❌ POSCO 뉴스 알림 전송 실패: {result}")
            
        return success
    
    def test_watchhamster_notification(self):
        """워치햄스터 알림 테스트"""
        self.log("🐹 워치햄스터 알림 테스트 시작...")
        
        message = f"""🐹 WatchHamster v3.0 시스템 테스트 알림

📅 테스트 시간: {self.test_time}
🛡️ 모니터링 상태: 활성화
🔍 감시 대상: POSCO 뉴스 시스템

📊 모니터링 현황:
• API 연결: ✅ 정상
• 데이터 수집: ✅ 정상
• 알림 시스템: ✅ 정상
• 오류 감지: 🟢 없음

🎯 WatchHamster v3.0이 정상 작동 중입니다."""

        success, result = self.send_notification(
            WATCHHAMSTER_WEBHOOK_URL,
            "WatchHamster v3.0 🐹🛡️",
            message,
            "#28a745"
        )
        
        self.results.append({
            "test": "워치햄스터 알림",
            "success": success,
            "result": result,
            "webhook": "WATCHHAMSTER_WEBHOOK_URL"
        })
        
        if success:
            self.log("✅ 워치햄스터 알림 전송 성공")
        else:
            self.log(f"❌ 워치햄스터 알림 전송 실패: {result}")
            
        return success
    
    def test_system_status_notification(self):
        """시스템 상태 알림 테스트"""
        self.log("📊 시스템 상태 알림 테스트 시작...")
        
        message = f"""📊 POSCO 통합 시스템 상태 보고

📅 보고 시간: {self.test_time}
🖥️ 시스템 상태: 전체 정상

🔧 주요 구성요소:
• POSCO News API: 🟢 정상
• 데이터베이스: 🟢 정상
• 웹훅 시스템: 🟢 정상
• 모니터링: 🟢 정상

📈 성능 지표:
• 응답 시간: < 2초
• 가용성: 99.9%
• 오류율: 0.1%

✅ 모든 시스템이 안정적으로 운영 중입니다."""

        success, result = self.send_notification(
            DOORAY_WEBHOOK_URL,
            "POSCO System Monitor 🖥️",
            message,
            "#17a2b8"
        )
        
        self.results.append({
            "test": "시스템 상태 알림",
            "success": success,
            "result": result,
            "webhook": "DOORAY_WEBHOOK_URL"
        })
        
        if success:
            self.log("✅ 시스템 상태 알림 전송 성공")
        else:
            self.log(f"❌ 시스템 상태 알림 전송 실패: {result}")
            
        return success
    
    def test_emergency_notification(self):
        """긴급 알림 테스트"""
        self.log("🚨 긴급 알림 테스트 시작...")
        
        message = f"""🚨 POSCO 시스템 긴급 알림 테스트

📅 테스트 시간: {self.test_time}
⚠️ 알림 유형: 긴급 테스트 (실제 문제 아님)
🔍 테스트 목적: 긴급 상황 대응 체계 점검

📋 테스트 시나리오:
• 시스템 장애 감지 ✅
• 알림 전송 시스템 ✅
• 담당자 호출 시스템 ✅
• 복구 절차 확인 ✅

💡 참고사항:
이는 정기 테스트이며 실제 장애가 아닙니다.
모든 시스템이 정상 작동 중입니다.

✅ 긴급 알림 시스템 테스트 완료"""

        success, result = self.send_notification(
            DOORAY_WEBHOOK_URL,
            "POSCO Emergency Alert 🚨",
            message,
            "#dc3545"
        )
        
        self.results.append({
            "test": "긴급 알림",
            "success": success,
            "result": result,
            "webhook": "DOORAY_WEBHOOK_URL"
        })
        
        if success:
            self.log("✅ 긴급 알림 전송 성공")
        else:
            self.log(f"❌ 긴급 알림 전송 실패: {result}")
            
        return success
    
    def test_maintenance_notification(self):
        """유지보수 알림 테스트"""
        self.log("🔧 유지보수 알림 테스트 시작...")
        
        message = f"""🔧 POSCO 시스템 유지보수 알림

📅 테스트 시간: {self.test_time}
🛠️ 유지보수 유형: 정기 점검 (테스트)
⏰ 예상 소요 시간: 테스트용 (실제 작업 없음)

📋 점검 항목:
• 데이터베이스 최적화 ✅
• 로그 파일 정리 ✅
• 보안 패치 적용 ✅
• 성능 튜닝 ✅

📊 점검 결과:
• 시스템 성능: 향상됨
• 보안 수준: 강화됨
• 안정성: 개선됨

✅ 유지보수 테스트 완료 - 모든 시스템 정상"""

        success, result = self.send_notification(
            DOORAY_WEBHOOK_URL,
            "POSCO Maintenance 🔧",
            message,
            "#ffc107"
        )
        
        self.results.append({
            "test": "유지보수 알림",
            "success": success,
            "result": result,
            "webhook": "DOORAY_WEBHOOK_URL"
        })
        
        if success:
            self.log("✅ 유지보수 알림 전송 성공")
        else:
            self.log(f"❌ 유지보수 알림 전송 실패: {result}")
            
        return success
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.log("🚀 종합 알림 시스템 테스트 시작")
        self.log(f"📅 테스트 기준 시간: {self.test_time}")
        self.log("=" * 60)
        
        # 모든 테스트 실행
        tests = [
            self.test_posco_news_notification,
            self.test_watchhamster_notification,
            self.test_system_status_notification,
            self.test_emergency_notification,
            self.test_maintenance_notification
        ]
        
        for test in tests:
            test()
            self.log("-" * 40)
        
        # 결과 요약
        self.log("📊 테스트 결과 요약")
        self.log("=" * 60)
        
        success_count = sum(1 for result in self.results if result['success'])
        total_count = len(self.results)
        
        for result in self.results:
            status = "✅ 성공" if result['success'] else "❌ 실패"
            self.log(f"{status} | {result['test']} | {result['result']}")
        
        self.log("=" * 60)
        self.log(f"📈 전체 결과: {success_count}/{total_count} 성공")
        
        if success_count == total_count:
            self.log("🎉 모든 알림 시스템이 정상 작동합니다!")
        else:
            self.log("⚠️ 일부 알림 시스템에 문제가 있습니다.")
        
        return self.results

def main():
    """메인 함수"""
    print("🔔 POSCO 종합 알림 시스템 테스트")
    print("=" * 60)
    
    tester = ComprehensiveNotificationTester()
    results = tester.run_all_tests()
    
    # 결과를 JSON 파일로 저장
    with open('notification_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'test_time': tester.test_time,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n📄 테스트 결과가 'notification_test_results.json'에 저장되었습니다.")

if __name__ == "__main__":
    main()