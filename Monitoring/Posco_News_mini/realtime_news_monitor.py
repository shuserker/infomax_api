#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 실시간 뉴스 모니터

실시간으로 뉴스 발행을 감지하고 즉시 Dooray 알림을 발송하는 시스템

주요 기능:
- 3개 뉴스 타입 실시간 모니터링 (환율/증시/뉴욕)
- 새 뉴스 발행 시 즉시 알림 발송
- 중복 알림 방지
- 조용한 시간대 고려

작성자: AI Assistant
최종 수정: 2025-08-04
"""

import os
import sys
import time
import requests
from datetime import datetime, timedelta
import json

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core import PoscoNewsAPIClient
    from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
    from newyork_monitor import NewYorkMarketMonitor
    from kospi_monitor import KospiCloseMonitor
    from exchange_monitor import ExchangeRateMonitor
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class RealtimeNewsMonitor:
    """
    실시간 뉴스 모니터링 클래스
    """
    
    def __init__(self):
        """
        실시간 모니터 초기화
        """
        self.api_client = PoscoNewsAPIClient(API_CONFIG)
        
        # 각 뉴스 모니터 초기화
        self.monitors = {
            'exchange-rate': {
                'monitor': ExchangeRateMonitor(),
                'name': '💱 서환마감',
                'last_title': None,
                'last_check': None
            },
            'kospi-close': {
                'monitor': KospiCloseMonitor(),
                'name': '📈 증시마감',
                'last_title': None,
                'last_check': None
            },
            'newyork-market-watch': {
                'monitor': NewYorkMarketMonitor(),
                'name': '🌆 뉴욕마켓워치',
                'last_title': None,
                'last_check': None
            }
        }
        
        # 상태 파일 경로
        self.state_file = os.path.join(current_dir, "realtime_monitor_state.json")
        
        # 이전 상태 로드
        self.load_state()
        
        print("📡 실시간 뉴스 모니터 초기화 완료")
        print(f"🔍 모니터링 대상: {len(self.monitors)}개 뉴스 타입")
    
    def load_state(self):
        """
        이전 상태 로드
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                for news_type, data in state.items():
                    if news_type in self.monitors:
                        self.monitors[news_type]['last_title'] = data.get('last_title')
                        self.monitors[news_type]['last_check'] = data.get('last_check')
                
                print("📋 이전 상태 로드 완료")
            else:
                print("📋 새로운 상태 파일 생성")
                
        except Exception as e:
            print(f"⚠️ 상태 로드 실패: {e}")
    
    def save_state(self):
        """
        현재 상태 저장
        """
        try:
            state = {}
            for news_type, info in self.monitors.items():
                state[news_type] = {
                    'last_title': info['last_title'],
                    'last_check': info['last_check']
                }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 상태 저장 실패: {e}")
    
    def is_quiet_hours(self):
        """
        조용한 시간대 체크 (19:01~05:59)
        
        Returns:
            bool: 조용한 시간대면 True
        """
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # 19:01~23:59 또는 00:00~05:59
        return (current_hour == 19 and current_minute >= 1) or current_hour >= 20 or current_hour <= 5
    
    def check_news_updates(self):
        """
        모든 뉴스 타입의 업데이트 체크
        """
        current_time = datetime.now()
        new_news_found = False
        
        for news_type, info in self.monitors.items():
            try:
                # 현재 뉴스 데이터 가져오기
                data = info['monitor'].get_current_news_data()
                
                if data and data.get('title'):
                    current_title = data['title']
                    
                    # 새로운 뉴스인지 확인
                    if info['last_title'] != current_title:
                        print(f"🆕 새 뉴스 발견: {info['name']} - {current_title[:50]}...")
                        
                        # 알림 발송
                        self.send_news_notification(news_type, info['name'], data)
                        
                        # 상태 업데이트
                        info['last_title'] = current_title
                        info['last_check'] = current_time.isoformat()
                        
                        new_news_found = True
                    else:
                        # 동일한 뉴스 - 체크 시간만 업데이트
                        info['last_check'] = current_time.isoformat()
                else:
                    print(f"⚠️ {info['name']} 데이터 없음")
                    info['last_check'] = current_time.isoformat()
                    
            except Exception as e:
                print(f"❌ {info['name']} 체크 실패: {e}")
                info['last_check'] = current_time.isoformat()
        
        # 새 뉴스가 있으면 상태 저장
        if new_news_found:
            self.save_state()
        
        return new_news_found
    
    def send_news_notification(self, news_type, news_name, data):
        """
        뉴스 알림 발송
        
        Args:
            news_type (str): 뉴스 타입
            news_name (str): 뉴스 이름
            data (dict): 뉴스 데이터
        """
        try:
            # 조용한 시간대 체크
            if self.is_quiet_hours():
                print(f"🌙 조용한 시간대 - {news_name} 알림 발송 생략")
                return
            
            title = data.get('title', '제목 없음')
            publish_time = data.get('publish_time', '시간 정보 없음')
            
            # 메시지 구성
            message = f"📰 {news_name} 새 뉴스 발행!\n\n"
            message += f"📋 제목: {title}\n"
            message += f"🕐 발행시간: {publish_time}\n"
            message += f"📅 감지시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Dooray 페이로드
            payload = {
                "botName": "POSCO 뉴스 알리미 📰",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"📰 {news_name} 새 뉴스 발행!",
                "attachments": [{
                    "color": "#007bff",
                    "text": message
                }]
            }
            
            # 알림 전송
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {news_name} 알림 전송 성공")
            else:
                print(f"❌ {news_name} 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {news_name} 알림 전송 오류: {e}")
    
    def run_monitor(self):
        """
        실시간 모니터링 실행
        """
        print(f"\n🚀 실시간 뉴스 모니터링 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔍 5분마다 뉴스 업데이트 체크")
        print("⏹️ Ctrl+C로 중단")
        
        check_interval = 5 * 60  # 5분
        
        while True:
            try:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - 뉴스 업데이트 체크 중...")
                
                # 뉴스 업데이트 체크
                new_news = self.check_news_updates()
                
                if new_news:
                    print("🎉 새 뉴스 발견 및 알림 완료!")
                else:
                    print("📋 새 뉴스 없음")
                
                # 다음 체크까지 대기
                print(f"⏳ {check_interval//60}분 후 다시 체크...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ 실시간 모니터링 중단됨")
                break
            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                print("🔄 1분 후 재시도...")
                time.sleep(60)
    
    def test_notifications(self):
        """
        테스트용 알림 발송
        """
        print("\n🧪 테스트 모드: 현재 뉴스 상태 확인 및 알림 테스트")
        
        for news_type, info in self.monitors.items():
            try:
                data = info['monitor'].get_current_news_data()
                
                if data and data.get('title'):
                    print(f"✅ {info['name']}: {data['title'][:50]}...")
                    
                    # 테스트 알림 발송
                    self.send_news_notification(news_type, info['name'], data)
                else:
                    print(f"⚠️ {info['name']}: 데이터 없음")
                    
            except Exception as e:
                print(f"❌ {info['name']} 테스트 실패: {e}")

def main():
    """
    메인 실행 함수
    """
    monitor = RealtimeNewsMonitor()
    
    # 명령행 인수 확인
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 테스트 모드
        monitor.test_notifications()
    else:
        # 정상 모니터링 모드
        monitor.run_monitor()

if __name__ == "__main__":
    main()