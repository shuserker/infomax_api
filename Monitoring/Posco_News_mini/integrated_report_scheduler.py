#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 통합 리포트 스케줄러

매일 17:59에 통합 리포트를 생성하고
18:00에 Dooray로 알림을 발송하는 스케줄러

주요 기능:
- 17:59: 3개 뉴스 타입 데이터 수집 및 통합 리포트 생성
- 18:00: 통합 리포트 알림 발송
- 자동 스케줄링 및 오류 처리

작성자: AI Assistant
최종 수정: 2025-08-02
"""

import os
import sys
import time
import schedule
import requests
from datetime import datetime, timedelta
import threading

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core import PoscoNewsAPIClient
    from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
    from reports.integrated_report_generator import IntegratedReportGenerator
    from newyork_monitor import NewYorkMarketMonitor
    from kospi_monitor import KospiCloseMonitor
    from exchange_monitor import ExchangeRateMonitor
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class IntegratedReportScheduler:
    """
    통합 리포트 스케줄러 클래스
    """
    
    def __init__(self):
        """
        스케줄러 초기화
        """
        self.api_client = PoscoNewsAPIClient(API_CONFIG)
        self.report_generator = IntegratedReportGenerator()
        
        # 각 뉴스 모니터 초기화
        self.monitors = {
            'exchange-rate': ExchangeRateMonitor(),
            'kospi-close': KospiCloseMonitor(),
            'newyork-market-watch': NewYorkMarketMonitor()
        }
        
        self.last_report_info = None
        
        print("📊 통합 리포트 스케줄러 초기화 완료")
    
    def collect_all_news_data(self):
        """
        모든 뉴스 타입의 현재 데이터 수집
        
        Returns:
            dict: 각 뉴스 타입별 데이터
        """
        news_data = {}
        
        for news_type, monitor in self.monitors.items():
            try:
                data = monitor.get_current_news_data()
                news_data[news_type] = data
                
                if data and data.get('title'):
                    print(f"✅ {news_type} 데이터 수집 완료: {data.get('title')[:50]}...")
                else:
                    print(f"⚠️ {news_type} 데이터 없음")
                    
            except Exception as e:
                print(f"❌ {news_type} 데이터 수집 실패: {e}")
                news_data[news_type] = None
        
        return news_data
    
    def generate_daily_report(self):
        """
        일일 통합 리포트 생성 (17:59 실행)
        """
        print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - 일일 통합 리포트 생성 시작")
        
        try:
            # 통합 리포트 생성 (영업일 헬퍼 사용)
            self.last_report_info = self.report_generator.generate_integrated_report()
            
            print(f"✅ 통합 리포트 생성 완료: {self.last_report_info['filename']}")
            print(f"🔗 리포트 URL: {self.last_report_info['github_url']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 통합 리포트 생성 실패: {e}")
            return False
    
    def send_daily_report_notification(self):
        """
        일일 통합 리포트 알림 발송 (18:00 실행)
        """
        print(f"\n🕕 {datetime.now().strftime('%H:%M:%S')} - 일일 통합 리포트 알림 발송 시작")
        
        # 조용한 시간대 체크 (19:01~05:59)
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        is_quiet = (current_hour == 19 and current_minute >= 1) or current_hour >= 20 or current_hour <= 5
        
        if is_quiet:
            print("🌙 조용한 시간대 - 통합 리포트 알림 발송 생략")
            return True
        
        if not self.last_report_info:
            print("❌ 발송할 리포트가 없습니다. 리포트를 먼저 생성하세요.")
            return False
        
        try:
            # 발행 현황 확인
            news_data = self.collect_all_news_data()
            published_count = sum(1 for data in news_data.values() if data and data.get('title'))
            total_count = len(news_data)
            
            # 메시지 구성
            if published_count == total_count:
                status_emoji = "✅"
                status_text = "모든 뉴스 발행 완료"
                color = "#28a745"
            elif published_count >= 2:
                status_emoji = "⚠️"
                status_text = f"{published_count}/{total_count} 뉴스 발행"
                color = "#ffc107"
            else:
                status_emoji = "❌"
                status_text = f"뉴스 발행 부족 ({published_count}/{total_count})"
                color = "#dc3545"
            
            # 뉴스별 상태 메시지
            news_status_lines = []
            news_names = {
                'exchange-rate': '💱 서환마감',
                'kospi-close': '📈 증시마감',
                'newyork-market-watch': '🌆 뉴욕마켓워치'
            }
            
            for news_type, data in news_data.items():
                name = news_names.get(news_type, news_type)
                if data and data.get('title'):
                    news_status_lines.append(f"✅ {name}: 발행완료")
                else:
                    news_status_lines.append(f"⏳ {name}: 발행대기")
            
            news_status_text = "\n".join(news_status_lines)
            
            # Dooray 웹훅 메시지 구성
            main_text = f"📊 POSCO 뉴스 일일 통합 분석 리포트 | [📊 통합 리포트 보기]({self.last_report_info['github_url']})"
            
            payload = {
                "botName": "POSCO 뉴스 📊",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": main_text,
                "mrkdwn": True,
                "attachments": [{
                    "color": color,
                    "title": f"{status_emoji} 오늘의 뉴스 발행 현황",
                    "text": f"📊 {status_text}\n\n{news_status_text}\n\n🎯 통합 분석 완료\n모든 발행된 뉴스를 종합하여 시장 분석, 투자 전략, 리스크 분석을 제공합니다.",
                    "mrkdwn_in": ["text"]
                }]
            }
            
            # 웹훅 전송
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ 통합 리포트 알림 발송 완료")
                return True
            else:
                print(f"❌ 알림 발송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 알림 발송 오류: {e}")
            return False
    
    def setup_schedule(self):
        """
        스케줄 설정
        """
        # 17:59에 리포트 생성
        schedule.every().day.at("17:59").do(self.generate_daily_report)
        
        # 18:00에 알림 발송
        schedule.every().day.at("18:00").do(self.send_daily_report_notification)
        
        print("📅 스케줄 설정 완료:")
        print("  - 17:59: 통합 리포트 생성")
        print("  - 18:00: 통합 리포트 알림 발송")
    
    def run_scheduler(self):
        """
        스케줄러 실행
        """
        print(f"\n🚀 통합 리포트 스케줄러 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.setup_schedule()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # 30초마다 체크
                
                # 현재 시간 표시 (매 10분마다)
                now = datetime.now()
                if now.minute % 10 == 0 and now.second < 30:
                    print(f"⏰ 현재 시간: {now.strftime('%H:%M:%S')} - 다음 실행 대기중...")
                    
            except KeyboardInterrupt:
                print("\n⏹️ 스케줄러 중단됨")
                break
            except Exception as e:
                print(f"❌ 스케줄러 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def test_report_generation(self):
        """
        테스트용 리포트 생성 및 발송
        """
        print("\n🧪 테스트 모드: 통합 리포트 생성 및 발송")
        
        # 리포트 생성
        if self.generate_daily_report():
            # 알림 발송
            self.send_daily_report_notification()
        else:
            print("❌ 테스트 실패: 리포트 생성 불가")

def main():
    """
    메인 실행 함수
    """
    scheduler = IntegratedReportScheduler()
    
    # 명령행 인수 확인
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 테스트 모드
        scheduler.test_report_generation()
    else:
        # 정상 스케줄러 모드
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()