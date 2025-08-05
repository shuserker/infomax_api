#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 알림자 v2.0 📰

비활성화된 모듈 의존성을 제거하고 통합 리포트 시스템과 연동하여
새로운 뉴스 발행 시 실시간 알림을 제공하는 시스템

주요 기능:
- 📰 새 뉴스 발행 시 즉시 Dooray 알림
- 🔍 5분 간격 뉴스 업데이트 체크
- 🌙 조용한 시간대 고려 (18시 이후)
- 🚫 중복 알림 방지
- 📊 3개 뉴스 타입 통합 모니터링

작성자: AI Assistant
최종 수정: 2025-08-05
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta
import signal
import threading

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core import PoscoNewsAPIClient
    from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
except ImportError as e:
    print(f"[WARNING] 일부 모듈을 불러올 수 없습니다: {e}")
    print("[INFO] 기본 설정으로 동작합니다.")
    API_CONFIG = {}
    DOORAY_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"
    BOT_PROFILE_IMAGE_URL = "https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg"

class PoscoNewsNotifierV2:
    """
    POSCO 뉴스 알림자 v2.0 클래스
    
    통합 리포트 시스템과 연동하여 새로운 뉴스 발행 시
    실시간 알림을 제공하는 시스템
    """
    
    def __init__(self):
        """알림자 초기화"""
        self.script_dir = current_dir
        self.state_file = os.path.join(self.script_dir, "news_notifier_state.json")
        self.log_file = os.path.join(self.script_dir, "news_notifier.log")
        
        # 실행 제어
        self.running = True
        self.check_interval = 5 * 60  # 5분 간격
        
        # 뉴스 타입별 상태 추적
        self.news_types = {
            'exchange': {
                'name': '💱 서환마감',
                'last_title': '',
                'last_check': None,
                'api_key': 'exchange_rate'
            },
            'kospi': {
                'name': '📈 증시마감', 
                'last_title': '',
                'last_check': None,
                'api_key': 'kospi_close'
            },
            'newyork': {
                'name': '🌆 뉴욕마켓워치',
                'last_title': '',
                'last_check': None,
                'api_key': 'newyork_market'
            }
        }
        
        # API 클라이언트 초기화
        try:
            self.api_client = PoscoNewsAPIClient(API_CONFIG)
        except:
            self.api_client = None
            self.log_message("⚠️ API 클라이언트 초기화 실패, 기본 모드로 동작")
        
        # 신호 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 이전 상태 로드
        self.load_state()
        
        self.log_message("📰 POSCO 뉴스 알림자 v2.0 초기화 완료")
    
    def signal_handler(self, signum, frame):
        """종료 신호 처리"""
        self.log_message(f"🛑 종료 신호 수신 (신호: {signum})")
        self.running = False
    
    def log_message(self, message):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def is_quiet_hours(self):
        """조용한 시간대 확인 (18시 이후)"""
        current_hour = datetime.now().hour
        return current_hour >= 18
    
    def load_state(self):
        """이전 상태 로드"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                for news_type in self.news_types:
                    if news_type in state_data:
                        self.news_types[news_type].update(state_data[news_type])
                
                self.log_message("📋 이전 상태 로드 완료")
            else:
                self.log_message("📋 새로운 상태 파일 생성")
                
        except Exception as e:
            self.log_message(f"❌ 상태 로드 실패: {e}")
    
    def save_state(self):
        """현재 상태 저장"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.news_types, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.log_message(f"❌ 상태 저장 실패: {e}")
    
    def get_news_data_from_api(self, news_type):
        """API에서 뉴스 데이터 가져오기"""
        try:
            if not self.api_client:
                return None
            
            api_key = self.news_types[news_type]['api_key']
            
            # API 호출
            response = self.api_client.get_news_data(api_key)
            
            if response and isinstance(response, dict):
                return {
                    'title': response.get('title', ''),
                    'publish_time': response.get('publish_time', ''),
                    'content': response.get('content', ''),
                    'url': response.get('url', '')
                }
            
            return None
            
        except Exception as e:
            self.log_message(f"❌ {news_type} API 호출 실패: {e}")
            return None
    
    def get_news_data_from_cache(self, news_type):
        """캐시 파일에서 뉴스 데이터 가져오기 (API 실패 시 대안)"""
        try:
            cache_files = {
                'exchange': 'posco_news_cache.json',
                'kospi': 'posco_news_cache.json', 
                'newyork': 'posco_news_cache.json'
            }
            
            cache_file = cache_files.get(news_type)
            if not cache_file or not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 뉴스 타입별 데이터 추출
            if news_type in cache_data:
                data = cache_data[news_type]
                return {
                    'title': data.get('title', ''),
                    'publish_time': data.get('publish_time', ''),
                    'content': data.get('content', ''),
                    'url': data.get('url', '')
                }
            
            return None
            
        except Exception as e:
            self.log_message(f"❌ {news_type} 캐시 읽기 실패: {e}")
            return None
    
    def check_for_new_news(self):
        """새로운 뉴스 확인"""
        new_news_found = False
        current_time = datetime.now()
        
        for news_type, info in self.news_types.items():
            try:
                # API에서 데이터 가져오기 시도
                data = self.get_news_data_from_api(news_type)
                
                # API 실패 시 캐시에서 가져오기
                if not data:
                    data = self.get_news_data_from_cache(news_type)
                
                if data and data.get('title'):
                    current_title = data['title'].strip()
                    
                    # 새로운 뉴스인지 확인
                    if info['last_title'] != current_title and current_title:
                        self.log_message(f"🆕 새 뉴스 발견: {info['name']} - {current_title[:50]}...")
                        
                        # 알림 발송
                        self.send_news_notification(news_type, info['name'], data)
                        
                        # 상태 업��이트
                        info['last_title'] = current_title
                        info['last_check'] = current_time.isoformat()
                        
                        new_news_found = True
                    else:
                        # 동일한 뉴스 - 체크 시간만 업데이트
                        info['last_check'] = current_time.isoformat()
                        
                else:
                    self.log_message(f"⚠️ {info['name']} 데이터 없음")
                    info['last_check'] = current_time.isoformat()
                    
            except Exception as e:
                self.log_message(f"❌ {info['name']} 체크 실패: {e}")
                info['last_check'] = current_time.isoformat()
        
        # 새 뉴스가 있으면 상태 저장
        if new_news_found:
            self.save_state()
        
        return new_news_found
    
    def send_news_notification(self, news_type, news_name, data):
        """뉴스 알림 발송"""
        try:
            # 조용한 시간대 체크
            if self.is_quiet_hours():
                self.log_message(f"🌙 조용한 시간대 - {news_name} 알림 발송 생략")
                return
            
            title = data.get('title', '제목 없음')
            publish_time = data.get('publish_time', '시간 정보 없음')
            url = data.get('url', '')
            
            # 메시지 구성
            message = f"📰 {news_name} 새 뉴스 발행!\n\n"
            message += f"📋 제목: {title}\n"
            message += f"🕐 발행시간: {publish_time}\n"
            message += f"📅 감지시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            if url:
                message += f"\n🔗 링크: {url}"
            
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
                self.log_message(f"✅ {news_name} 알림 전송 성공")
            else:
                self.log_message(f"❌ {news_name} 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ {news_name} 알림 전송 오류: {e}")
    
    def send_status_notification(self):
        """상태 알림 발송"""
        try:
            current_time = datetime.now()
            
            message = f"📊 POSCO 뉴스 알림자 상태 보고\n\n"
            message += f"📅 보고 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"🔍 모니터링 간격: {self.check_interval // 60}분\n\n"
            
            message += "📰 뉴스 타입별 상태:\n"
            for news_type, info in self.news_types.items():
                last_check = info.get('last_check')
                if last_check:
                    check_time = datetime.fromisoformat(last_check)
                    time_diff = (current_time - check_time).total_seconds() / 60
                    message += f"  {info['name']}: {time_diff:.0f}분 전 체크\n"
                else:
                    message += f"  {info['name']}: 아직 체크 안됨\n"
            
            if self.is_quiet_hours():
                message += f"\n🌙 현재 조용한 시간대 (18시 이후)"
            
            # Dooray 페이로드
            payload = {
                "botName": "POSCO 뉴스 알림자 📊",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": "📊 POSCO 뉴스 알림자 상태 보고",
                "attachments": [{
                    "color": "#28a745",
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
                self.log_message("✅ 상태 알림 전송 성공")
            else:
                self.log_message(f"❌ 상태 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 상태 알림 전송 오류: {e}")
    
    def run(self):
        """메인 뉴스 알림 루프"""
        start_time = datetime.now()
        last_status_notification = start_time - timedelta(hours=2)  # 시작 시 상태 알림
        
        self.log_message("📰 POSCO 뉴스 알림자 v2.0 시작")
        self.log_message(f"📅 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message(f"🔍 뉴스 체크 간격: {self.check_interval // 60}분")
        self.log_message("🌙 조용한 시간대: 18시 이후 알림 생략")
        self.log_message("🛑 종료하려면 Ctrl+C를 누르세요")
        
        # 시작 알림
        self.send_status_notification()
        
        # 메인 루프
        while self.running:
            try:
                current_time = datetime.now()
                
                # 뉴스 체크
                self.log_message("🔍 새로운 뉴스 확인 중...")
                new_news = self.check_for_new_news()
                
                if new_news:
                    self.log_message("🎉 새 뉴스 발견 및 알림 완료!")
                else:
                    self.log_message("📋 새 뉴스 없음")
                
                # 2시간마다 상태 알림
                if (current_time - last_status_notification).total_seconds() >= 2 * 60 * 60:
                    self.send_status_notification()
                    last_status_notification = current_time
                
                # 다음 체크까지 대기
                self.log_message(f"⏳ {self.check_interval // 60}분 대기 중...")
                
                for i in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                self.log_message("🛑 사용자에 의한 종료 요청")
                break
            except Exception as e:
                self.log_message(f"❌ 뉴스 알림 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기 후 재시도
        
        # 종료 처리
        self.log_message("🛑 POSCO 뉴스 알림자 종료 중...")
        self.save_state()
        
        # 종료 알림
        try:
            payload = {
                "botName": "POSCO 뉴스 알림자 📰",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": "🛑 POSCO 뉴스 알림자 종료",
                "attachments": [{
                    "color": "#dc3545",
                    "text": f"📅 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }]
            }
            
            requests.post(DOORAY_WEBHOOK_URL, json=payload, timeout=5)
        except:
            pass
        
        self.log_message("✅ POSCO 뉴스 알림자 종료 완료")

def main():
    """메인 함수"""
    print("📰 POSCO 뉴스 알림자 v2.0")
    print("=" * 60)
    
    # 뉴스 알림자 시작
    notifier = PoscoNewsNotifierV2()
    notifier.run()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())