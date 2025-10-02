#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 포스코 뉴스 메시지 형태 테스트
2025-08-06 19:00 기준 실제 메시지 생성
"""

import sys
import os
import requests
import json
from datetime import datetime

# 프로젝트 루트 추가
sys.path.insert(0, '.')

try:
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.webhook_sender import WebhookSender, MessagePriority, BotType
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

class RealPoscoMessageTester:
    """실제 포스코 메시지 형태 테스트"""
    
    def __init__(self):
        self.webhook_sender = WebhookSender(test_mode=False)
        self.test_datetime = datetime(2025, 8, 6, 19, 0, 0)
        
        # 웹훅 URL 직접 설정
        self.webhook_urls = {
            'news_main': 'https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg',
            'watchhamster': 'https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ'
        }
        
        print(f"🧪 실제 포스코 메시지 테스트 시작")
        print(f"📅 기준 시간: {self.test_datetime.strftime('%Y-%m-%d %H:%M')}")
    
    def send_direct_webhook(self, webhook_url, bot_name, title, content, color="#007bff"):
        """직접 웹훅 전송"""
        try:
            payload = {
                "botName": bot_name,
                "botIconImage": "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg",
                "text": title,
                "attachments": [{
                    "color": color,
                    "text": content
                }]
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 웹훅 전송 성공: {response.status_code}")
                return True
            else:
                print(f"❌ 웹훅 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 웹훅 전송 오류: {e}")
            return False
    
    def test_business_day_comparison_message(self):
        """영업일 비교 분석 메시지 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트: 영업일 비교 분석 (실제 형태)")
        print("="*60)
        
        # 실제 포스코 영업일 비교 분석 메시지 생성
        message_content = f"""🧪 [TEST] {self.test_datetime.strftime('%Y-%m-%d %H:%M')} 기준

📊 영업일 비교 분석

🕐 분석 시간: {self.test_datetime.strftime('%Y-%m-%d %H:%M')}

🔮 시장 동향 예측:
  전반적 발행 지연 우려 | 마감 시간대 - 종가 확정 대기 | 발행 패턴 안정적 유지

[NEWYORK MARKET WATCH]
├ 현재: 06:30 🟢 최신
├ 제목: [뉴욕마켓워치] 미국 증시 상승 마감
├ 변화: 🆕 새로운 내용
└ 직전: 06:30 | [뉴욕마켓워치] 전일 미국 증시 현황...

[KOSPI CLOSE]
├ 현재: 🔴 발행 지연
├ 직전: 🔄 15:40
├ 제목: [코스피마감] 전일 코스피 현황
└ 예상: ⏰ 15:40 (±10분)

[EXCHANGE RATE]
├ 현재: ⏳ 발행 전
├ 직전: 🔄 15:30
├ 제목: [환율] 전일 환율 현황
└ 예상: ⏰ 16:30 (±5분)

📈 종합 분석:
  🚨 전반적 지연 상황 | 📈 시장 동향: 상승 | 🔧 지연 원인 점검 필요 | ⏰ 다음 점검: 16:46"""
        
        # 영업일 비교 분석 BOT으로 전송
        success = self.send_direct_webhook(
            self.webhook_urls['news_main'],
            "POSCO 뉴스 비교알림",
            "📊 영업일 비교 분석",
            message_content,
            "#007bff"
        )
        
        return success
    
    def test_delay_notification_message(self):
        """지연 발행 알림 메시지 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트: 지연 발행 알림 (실제 형태)")
        print("="*60)
        
        message_content = f"""⏰ 증시마감 지연 발행 알림

📅 현재 시간: {self.test_datetime.strftime('%Y-%m-%d %H:%M:%S')}
📊 예상 발행 시간: 15:40 (±10분)
⏱️ 지연 시간: 약 3시간 20분

🔍 현재 상태:
├ KOSPI 지수: 종가 확정 대기 중
├ 거래량: 집계 진행 중
└ 발행 준비: 최종 검토 단계

⚠️ 발행 지연이 감지되었습니다.
📞 필요시 담당자에게 문의하세요."""
        
        success = self.send_direct_webhook(
            self.webhook_urls['news_main'],
            "POSCO 뉴스 ⏰",
            "⏰ 증시마감 지연 발행 알림",
            message_content,
            "#ffc107"
        )
        
        return success
    
    def test_daily_report_message(self):
        """일일 통합 리포트 메시지 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트: 일일 통합 리포트 (실제 형태)")
        print("="*60)
        
        message_content = f"""📊 POSCO 뉴스 일일 통합 리포트

📅 리포트 날짜: {self.test_datetime.strftime('%Y-%m-%d')}
🕐 생성 시간: {self.test_datetime.strftime('%H:%M:%S')}

📈 오늘의 발행 현황:
┌─ NEWYORK MARKET WATCH
├─ 발행 시간: 06:30 ✅
├─ 상태: 정상 발행
└─ 제목: [뉴욕마켓워치] 미국 증시 상승 마감

┌─ KOSPI CLOSE  
├─ 발행 시간: 15:40 ✅
├─ 상태: 정상 발행
└─ 제목: [증시마감] 코스피 2,650선 회복

┌─ EXCHANGE RATE
├─ 발행 시간: 15:30 ✅
├─ 상태: 정상 발행
└─ 제목: [서환마감] 원/달러 환율 1,320원대

📊 종합 통계:
• 총 발행: 3/3 (100%)
• 지연 발행: 0건
• 평균 발행 시간: 정시 대비 +2분

🎯 내일 예상:
• 뉴욕마켓워치: 06:30 예정
• 증시마감: 15:40 예정  
• 서환마감: 15:30 예정

✅ 모든 뉴스가 정상적으로 발행되었습니다."""
        
        success = self.send_direct_webhook(
            self.webhook_urls['news_main'],
            "POSCO 뉴스 📊",
            "📊 일일 통합 리포트",
            message_content,
            "#28a745"
        )
        
        return success
    
    def test_status_notification_message(self):
        """정시 발행 알림 메시지 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트: 정시 발행 알림 (실제 형태)")
        print("="*60)
        
        message_content = f"""✅ KOSPI CLOSE 정시 발행 완료

📅 발행 시간: {self.test_datetime.strftime('%Y-%m-%d %H:%M:%S')}
📊 예상 시간: 15:40 (정시)
⏱️ 지연 시간: 없음

📈 주요 내용:
├ KOSPI 지수: 2,650.45 (+15.23, +0.58%)
├ 거래대금: 8조 2,450억원
├ 외국인: 1,250억원 순매수
└ 기관: 850억원 순매도

🔍 시장 분석:
• 외국인 순매수세 지속
• 기술주 중심 상승
• 거래량 평균 수준 유지

✅ 증시마감 뉴스가 정상적으로 발행되었습니다."""
        
        success = self.send_direct_webhook(
            self.webhook_urls['news_main'],
            "POSCO 뉴스 ✅",
            "✅ 정시 발행 완료",
            message_content,
            "#28a745"
        )
        
        return success
    
    def test_no_data_notification_message(self):
        """데이터 갱신 없음 알림 메시지 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트: 데이터 갱신 없음 알림 (실제 형태)")
        print("="*60)
        
        message_content = f"""데이터 갱신 없음

┌  EXCHANGE RATE
├ 상태: 🔴 데이터 없음
├ 시간: 데이터 없음
└ 제목:

┌  NEWYORK MARKET WATCH  
├ 상태: 🔴 데이터 없음
├ 시간: 데이터 없음
└ 제목:

┌  KOSPI CLOSE
├ 상태: 🔴 데이터 없음
├ 시간: 데이터 없음
└ 제목:

📊 전체 현황: 0/3 업데이트됨
⏰ 마지막 체크: {self.test_datetime.strftime('%Y-%m-%d %H:%M:%S')}

💡 현재 모든 뉴스 타입에서 새로운 데이터가 확인되지 않았습니다."""
        
        success = self.send_direct_webhook(
            self.webhook_urls['news_main'],
            "POSCO 뉴스 🔔",
            "🔔 데이터 갱신 없음",
            message_content,
            "#6c757d"
        )
        
        return success
    
    def run_all_real_message_tests(self):
        """모든 실제 메시지 형태 테스트"""
        print("🎯 실제 POSCO 뉴스 메시지 형태 테스트 시작")
        print("="*80)
        
        results = []
        
        # 1. 영업일 비교 분석
        results.append(self.test_business_day_comparison_message())
        
        # 2. 지연 발행 알림
        results.append(self.test_delay_notification_message())
        
        # 3. 일일 통합 리포트
        results.append(self.test_daily_report_message())
        
        # 4. 정시 발행 알림
        results.append(self.test_status_notification_message())
        
        # 5. 데이터 갱신 없음 알림
        results.append(self.test_no_data_notification_message())
        
        print("\n" + "="*80)
        print(f"🎉 실제 메시지 형태 테스트 완료!")
        print(f"✅ 성공: {sum(results)}/{len(results)}")
        print("📱 두레이에서 실제 포스코 뉴스 형태의 메시지들을 확인해보세요!")
        print("="*80)

def main():
    """메인 함수"""
    try:
        tester = RealPoscoMessageTester()
        tester.run_all_real_message_tests()
    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()