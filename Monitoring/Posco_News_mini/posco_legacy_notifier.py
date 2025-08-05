#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 레거시 알림 시스템 복원 v1.0

기존 캡쳐와 동일한 알림 메시지를 생성하는 시스템
비활성화된 모듈 의존성 없이 기존 알림 형식을 완벽 재현

주요 기능:
- 🏭 POSCO 뉴스 비교알림 BOT (영업일 비교 분석)
- ⏰ 증시마감 지연 발행 알림
- 📊 일일 통합 분석 리포트
- ✅ 정시 발행 알림
- 🔔 데이터 갱신 없음 알림

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

class PoscoLegacyNotifier:
    """
    POSCO 레거시 알림 시스템 클래스
    
    기존 캡쳐와 동일한 형식의 알림을 생성합니다.
    """
    
    def __init__(self):
        """레거시 알림자 초기화"""
        self.script_dir = current_dir
        self.state_file = os.path.join(self.script_dir, "legacy_notifier_state.json")
        self.log_file = os.path.join(self.script_dir, "legacy_notifier.log")
        
        # 실행 제어
        self.running = True
        self.check_interval = 5 * 60  # 5분 간격
        
        # 뉴스 타입 정의 (기존 형식과 동일)
        self.news_types = {
            'newyork': {
                'display_name': 'NEWYORK MARKET WATCH',
                'emoji': '🌆',
                'last_title': '',
                'last_time': '',
                'status': '발행 대기',
                'api_key': 'newyork_market'
            },
            'kospi': {
                'display_name': 'KOSPI CLOSE', 
                'emoji': '📈',
                'last_title': '',
                'last_time': '',
                'status': '발행 대기',
                'api_key': 'kospi_close'
            },
            'exchange': {
                'display_name': 'EXCHANGE RATE',
                'emoji': '💱',
                'last_title': '',
                'last_time': '',
                'status': '발행 대기',
                'api_key': 'exchange_rate'
            }
        }
        
        # 스케줄 작업 시간
        self.scheduled_times = {
            'morning_status': (6, 0),      # 06:00 - 아침 현재 상태 체크
            'morning_comparison': (6, 10), # 06:10 - 영업일 비교 분석
            'evening_summary': (18, 0),    # 18:00 - 저녁 일일 요약 리포트
            'evening_detail': (18, 10),    # 18:10 - 저녁 상세 일일 요약
            'evening_analysis': (18, 20)   # 18:20 - 저녁 고급 분석
        }
        self.executed_today = set()
        
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
        
        self.log_message("🏭 POSCO 레거시 알림 시스템 초기화 완료")
    
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
    
    def get_news_data(self, news_type):
        """뉴스 데이터 가져오기"""
        try:
            # API에서 데이터 가져오기 시도
            if self.api_client:
                api_key = self.news_types[news_type]['api_key']
                response = self.api_client.get_news_data(api_key)
                
                if response and isinstance(response, dict):
                    return {
                        'title': response.get('title', ''),
                        'publish_time': response.get('publish_time', ''),
                        'content': response.get('content', ''),
                        'url': response.get('url', '')
                    }
            
            # API 실패 시 캐시에서 가져오기
            cache_file = 'posco_news_cache.json'
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
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
            self.log_message(f"❌ {news_type} 데이터 가져오기 실패: {e}")
            return None
    
    def send_business_day_comparison(self):
        """영업일 비교 분석 알림 (첫 번째 캡쳐 형식)"""
        try:
            self.log_message("📊 영업일 비교 분석 알림 생성 중...")
            
            # 각 뉴스 타입별 데이터 수집
            comparison_data = {}
            for news_type, info in self.news_types.items():
                data = self.get_news_data(news_type)
                comparison_data[news_type] = {
                    'current_data': data,
                    'display_name': info['display_name'],
                    'last_title': info['last_title'],
                    'last_time': info['last_time']
                }
            
            # 메시지 구성
            message = "📊 영업일 비교 분석\n\n"
            
            for news_type, data in comparison_data.items():
                display_name = data['display_name']
                current = data['current_data']
                
                message += f"[{display_name}]\n"
                
                if current and current.get('title'):
                    # 현재 데이터가 있는 경우
                    publish_time = current.get('publish_time', '시간 정보 없음')
                    title = current.get('title', '제목 없음')
                    
                    message += f"├ 현재: {publish_time} (최신)\n"
                    message += f"└ 제목: {title}\n\n"
                    
                    # 상태 업데이트
                    self.news_types[news_type]['last_title'] = title
                    self.news_types[news_type]['last_time'] = publish_time
                    self.news_types[news_type]['status'] = '최신'
                    
                else:
                    # 현재 데이터가 없는 경우
                    message += f"├ 현재: 데이터 없음\n"
                    
                    if data['last_time']:
                        message += f"├ 직전: {data['last_time']}\n"
                        message += f"└ 제목: {data['last_title']}\n\n"
                    else:
                        message += f"└ 직전: 데이터 없음\n\n"
                    
                    self.news_types[news_type]['status'] = '발행 대기'
            
            # Dooray 알림 전송
            payload = {
                "botName": "POSCO 뉴스 비교알림",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": "📊 영업일 비교 분석",
                "attachments": [{
                    "color": "#007bff",
                    "text": message.strip()
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 영업일 비교 분석 알림 전송 성공")
                self.save_state()
            else:
                self.log_message(f"❌ 영업일 비교 분석 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 영업일 비교 분석 알림 오류: {e}")
    
    def send_delay_notification(self, news_type, expected_time, actual_time, title):
        """지연 발행 알림 (두 번째 캡쳐 형식)"""
        try:
            display_name = self.news_types[news_type]['display_name']
            emoji = self.news_types[news_type]['emoji']
            
            # 지연 시간 계산
            expected_dt = datetime.strptime(expected_time, "%H:%M")
            actual_dt = datetime.strptime(actual_time, "%H:%M")
            delay_minutes = int((actual_dt - expected_dt).total_seconds() / 60)
            
            message = f"⏰ {display_name.lower()} 지연 발행\n\n"
            message += f"📅 발행 시간: {datetime.now().strftime('%Y-%m-%d')} {actual_time}:00\n"
            message += f"📊 패턴 분석: {delay_minutes}분 지연 발행 ({actual_time})\n"
            message += f"⏰ 예상: {expected_time} → 실제: {actual_time}\n"
            message += f"📋 제목: {title}\n\n"
            message += f"🔔 지연 알림이 초기화되었습니다."
            
            # Dooray 알림 전송
            payload = {
                "botName": "POSCO 뉴스 ⏰",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"⏰ {display_name.lower()} 지연 발행",
                "attachments": [{
                    "color": "#ffc107",
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message(f"✅ {display_name} 지연 발행 알림 전송 성공")
            else:
                self.log_message(f"❌ {display_name} 지연 발행 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 지연 발행 알림 오류: {e}")
    
    def send_daily_integrated_report(self):
        """일일 통합 분석 리포트 (세 번째 캡쳐 형식)"""
        try:
            self.log_message("📊 일일 통합 분석 리포트 생성 중...")
            
            # 발행 현황 확인
            published_count = 0
            total_count = 3
            
            message = "📊 POSCO 뉴스 일일 통합 분석 리포트 | 📊 통합 리포트 보기\n\n"
            
            # 발행 현황 체크
            for news_type, info in self.news_types.items():
                if info['status'] == '최신':
                    published_count += 1
            
            if published_count == 0:
                message += f"❌ 오늘의 뉴스 발행 현황\n"
                message += f"📊 뉴스 발행 부족 ({published_count}/{total_count})\n\n"
            else:
                message += f"✅ 오늘의 뉴스 발행 현황\n"
                message += f"📊 뉴스 발행 현황 ({published_count}/{total_count})\n\n"
            
            # 각 뉴스별 상태
            message += f"💱 $₩ 서환마감: {self.news_types['exchange']['status']}\n"
            message += f"📈 📊 증시마감: {self.news_types['kospi']['status']}\n"
            message += f"🏙️ 뉴욕마켓워치: {self.news_types['newyork']['status']}\n\n"
            
            message += f"🎯 통합 분석 완료\n"
            message += f"모든 발행된 뉴스를 종합하여 시장 분석, 투자 전략, 리스크 분석을 제공합니다."
            
            # Dooray 알림 전송
            payload = {
                "botName": "POSCO 뉴스 📊",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": "📊 POSCO 뉴스 일일 통합 분석 리포트 | 📊 통합 리포트 보기",
                "attachments": [{
                    "color": "#28a745" if published_count > 0 else "#dc3545",
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 일일 통합 분석 리포트 알림 전송 성공")
            else:
                self.log_message(f"❌ 일일 통합 분석 리포트 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 일일 통합 분석 리포트 알림 오류: {e}")
    
    def send_timely_publication_notification(self, news_type, publish_time, title):
        """정시 발행 알림 (네 번째 캡쳐 형식)"""
        try:
            display_name = self.news_types[news_type]['display_name']
            
            message = f"✅ {display_name.lower()} 정시 발행\n\n"
            message += f"📅 발행 시간: {publish_time}\n"
            message += f"📊 패턴 분석: 정시 발행 ({publish_time.split()[1][:5]})\n"
            message += f"⏰ 예상: 06:00-07:00 → 실제: {publish_time.split()[1][:5]}\n"
            message += f"📋 제목: {title}\n\n"
            message += f"🔔 지연 알림이 초기화되었습니다."
            
            # Dooray 알림 전송
            payload = {
                "botName": "POSCO 뉴스 ✅",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"✅ {display_name.lower()} 정시 발행",
                "attachments": [{
                    "color": "#28a745",
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message(f"✅ {display_name} 정시 발행 알림 전송 성공")
            else:
                self.log_message(f"❌ {display_name} 정시 발행 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 정시 발행 알림 오류: {e}")
    
    def send_data_update_status(self):
        """데이터 갱신 없음 알림 (다섯 번째 캡쳐 형식)"""
        try:
            self.log_message("🔔 데이터 갱신 상태 알림 생성 중...")
            
            message = "🔔 데이터 갱신 없음\n\n"
            
            for news_type, info in self.news_types.items():
                display_name = info['display_name']
                status = info['status']
                last_time = info['last_time']
                last_title = info['last_title']
                
                message += f"├ {display_name}\n"
                
                if status == '최신':
                    message += f"├ 상태: 🟢 최신\n"
                    message += f"├ 시간: {last_time}\n"
                    message += f"└ 제목: {last_title}\n\n"
                else:
                    message += f"├ 상태: ⏳ 발행 대기\n"
                    message += f"├ 시간: 날짜 정보 없음\n"
                    message += f"└ 제목:\n\n"
            
            message += f"최종 확인: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Dooray 알림 전송
            payload = {
                "botName": "POSCO 뉴스 🔔",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": "🔔 데이터 갱신 없음",
                "attachments": [{
                    "color": "#6c757d",
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 데이터 갱신 상태 알림 전송 성공")
            else:
                self.log_message(f"❌ 데이터 갱신 상태 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 데이터 갱신 상태 알림 오류: {e}")
    
    def check_scheduled_tasks(self):
        """스케줄 작업 확인 및 실행"""
        now = datetime.now()
        current_time = (now.hour, now.minute)
        today_key = now.strftime("%Y-%m-%d")
        
        # 매일 자정에 실행된 작업 목록 초기화
        if now.hour == 0 and now.minute == 0:
            self.executed_today.clear()
            self.log_message("🔄 일일 스케줄 작업 목록 초기화")
        
        for task_name, scheduled_time in self.scheduled_times.items():
            task_key = f"{today_key}_{task_name}"
            
            if (current_time == scheduled_time and 
                task_key not in self.executed_today):
                
                self.log_message(f"⏰ 스케줄 작업 실행: {task_name} ({scheduled_time[0]:02d}:{scheduled_time[1]:02d})")
                self.execute_scheduled_task(task_name)
                self.executed_today.add(task_key)
    
    def execute_scheduled_task(self, task_name):
        """스케줄 작업 실행"""
        try:
            if task_name == 'morning_status':
                self.send_data_update_status()
            elif task_name == 'morning_comparison':
                self.send_business_day_comparison()
            elif task_name == 'evening_summary':
                self.send_daily_integrated_report()
            elif task_name == 'evening_detail':
                self.send_data_update_status()
            elif task_name == 'evening_analysis':
                self.send_business_day_comparison()
                
        except Exception as e:
            self.log_message(f"❌ 스케줄 작업 실행 오류 ({task_name}): {e}")
    
    def run(self):
        """메인 레거시 알림 루프"""
        start_time = datetime.now()
        
        self.log_message("🏭 POSCO 레거시 알림 시스템 시작")
        self.log_message(f"📅 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message("📊 기존 캡쳐와 동일한 알림 형식 제공")
        self.log_message("🛑 종료하려면 Ctrl+C를 누르세요")
        
        # 메인 루프
        while self.running:
            try:
                current_time = datetime.now()
                
                # 스케줄 작업 확인
                self.check_scheduled_tasks()
                
                # 1분 대기
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.log_message("🛑 사용자에 의한 종료 요청")
                break
            except Exception as e:
                self.log_message(f"❌ 레거시 알림 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기 후 재시도
        
        # 종료 처리
        self.log_message("🛑 POSCO 레거시 알림 시스템 종료 중...")
        self.save_state()
        self.log_message("✅ POSCO 레거시 알림 시스템 종료 완료")

def main():
    """메인 함수"""
    print("🏭 POSCO 레거시 알림 시스템 v1.0")
    print("=" * 60)
    
    # 레거시 알림자 시작
    notifier = PoscoLegacyNotifier()
    notifier.run()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())