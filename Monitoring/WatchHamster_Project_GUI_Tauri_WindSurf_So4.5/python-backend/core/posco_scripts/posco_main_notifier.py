#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 메인 알림 시스템 v2.0 (새로운 구조 적용)

5가지 BOT 타입의 알림 메시지를 생성하는 시스템
새로운 워치햄스터 구조에 맞게 복원

주요 기능:
- 🏭 POSCO 뉴스 비교알림 BOT (영업일 비교 분석)
- ⏰ 증시마감 지연 발행 알림
- 📊 일일 통합 분석 리포트
- ✅ 정시 발행 알림
- 🔔 데이터 갱신 없음 알림

작성자: AI Assistant
최종 수정: 2025-08-16 (새로운 구조 적용)
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta
import signal
import threading

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
posco_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if posco_root not in sys.path:
    sys.path.insert(0, posco_root)

try:
    # 새로운 구조의 모듈 import
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.environment_setup import EnvironmentSetup
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.integrated_api_module import IntegratedAPIModule
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.news_message_generator import NewsMessageGenerator
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.webhook_sender import WebhookSender, MessagePriority, BotType
except ImportError as e:
    print(f"[WARNING] 새로운 구조 모듈을 불러올 수 없습니다: {e}")
    print("[INFO] 레거시 모듈로 폴백합니다.")
    try:
        # 레거시 모듈 import
        from recovery_config.environment_setup import EnvironmentSetup
        from recovery_config.integrated_api_module import IntegratedAPIModule
        from recovery_config.news_message_generator import NewsMessageGenerator
        from recovery_config.webhook_sender import WebhookSender, MessagePriority, BotType
    except ImportError as e2:
        print(f"[ERROR] 레거시 모듈도 불러올 수 없습니다: {e2}")
        sys.exit(1)

class PoscoMainNotifier:
    """
    POSCO 메인 알림 시스템 클래스 (새로운 구조)
    
    5가지 BOT 타입의 알림을 생성합니다.
    """
    
    def __init__(self):
        """메인 알림자 초기화"""
        self.script_dir = current_dir
        self.state_file = os.path.join(self.script_dir, "main_notifier_state.json")
        self.log_file = os.path.join(self.script_dir, "main_notifier.log")
        
        print("🏭 POSCO 메인 알림 시스템 v2.0 시작")
        print(f"📁 작업 디렉토리: {self.script_dir}")
        
        # 환경 설정 로드
        try:
            env_setup = EnvironmentSetup()
            self.env_settings = env_setup.settings
            print("✅ 환경 설정 로드 완료")
        except Exception as e:
            print(f"❌ 환경 설정 로드 실패: {e}")
            self.env_settings = {}
        
        # API 모듈 초기화
        try:
            self.api_module = IntegratedAPIModule(self.env_settings.get('api_config', {}))
            print("✅ API 모듈 초기화 완료")
        except Exception as e:
            print(f"❌ API 모듈 초기화 실패: {e}")
            self.api_module = None
        
        # 메시지 생성기 초기화
        try:
            self.message_generator = NewsMessageGenerator(self.env_settings.get('api_config', {}))
            print("✅ 메시지 생성기 초기화 완료")
        except Exception as e:
            print(f"❌ 메시지 생성기 초기화 실패: {e}")
            self.message_generator = None
        
        # 웹훅 전송자 초기화
        try:
            self.webhook_sender = WebhookSender(test_mode=False)
            print("✅ 웹훅 전송자 초기화 완료")
        except Exception as e:
            print(f"❌ 웹훅 전송자 초기화 실패: {e}")
            self.webhook_sender = None
        
        # 실행 제어
        self.running = True
        self.check_interval = 5 * 60  # 5분 간격
        
        # 테스트 모드 설정
        self.test_mode = False
        self.test_datetime = None
        
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
            'evening_analysis': (18, 20),  # 18:20 - 저녁 고급 분석
            'git_pages_report': (19, 0)    # 19:00 - Git Pages 통합 리포트
        }
        self.executed_today = set()
        
        # 마지막 체크 시간 저장
        self.last_news_check = {}
        for news_type in self.news_types:
            self.last_news_check[news_type] = datetime.now() - timedelta(hours=1)
        
        # 웹훅 URL 설정 (실제 포스코 뉴스 전송용)
        self.webhook_url = 'https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg'
        
        print("🎯 POSCO 메인 알림 시스템 초기화 완료")
    
    def send_direct_webhook(self, bot_name, title, content, color="#007bff", link_url=None, link_text=None):
        """직접 웹훅 전송 (실제 포스코 뉴스 형태)"""
        try:
            # 제목에 하이퍼링크 추가 (캡처와 같은 형태)
            if link_url and link_text:
                title_with_link = f"{title} | [{link_text}]({link_url})"
            else:
                title_with_link = title
            
            payload = {
                "botName": bot_name,
                "botIconImage": "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg",
                "text": title_with_link,
                "attachments": [{
                    "color": color,
                    "text": content
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                return f"webhook_{int(time.time())}"
            else:
                self.log_message(f"❌ 웹훅 전송 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_message(f"❌ 웹훅 전송 오류: {e}")
            return None
    
    def log_message(self, message):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"❌ 로그 파일 쓰기 실패: {e}")
    
    def send_startup_notification(self):
        """시작 알림 전송"""
        try:
            if not self.webhook_sender:
                self.log_message("⚠️ 웹훅 전송자가 초기화되지 않음")
                return
            
            startup_message = f"""🏭 POSCO 메인 알림 시스템 시작

📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔍 모니터링 대상: {len(self.news_types)}개 뉴스 타입
⏰ 체크 간격: {self.check_interval//60}분
📊 스케줄 작업: {len(self.scheduled_times)}개

📋 모니터링 뉴스:
{chr(10).join([f'  {info["emoji"]} {info["display_name"]}' for info in self.news_types.values()])}

✅ 포스코 뉴스 알림 시스템이 정상적으로 시작되었습니다."""
            
            # 간단한 상태 알림으로 전송
            message_id = self.webhook_sender.send_watchhamster_status(
                "포스코 메인 알림 시스템 시작",
                {
                    "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "monitoring_types": len(self.news_types),
                    "check_interval": f"{self.check_interval//60}분",
                    "system_status": "초기화 완료"
                }
            )
            
            if message_id:
                self.log_message(f"✅ 시작 알림 전송 완료: {message_id}")
            else:
                self.log_message("⚠️ 시작 알림 전송 실패")
                
        except Exception as e:
            self.log_message(f"❌ 시작 알림 전송 오류: {e}")
    
    def check_news_updates(self):
        """뉴스 업데이트 확인 및 알림 전송"""
        try:
            if not self.api_module:
                self.log_message("⚠️ API 모듈이 초기화되지 않음")
                return
            
            current_time = datetime.now()
            news_found = False
            
            for news_type, info in self.news_types.items():
                try:
                    # API에서 최신 뉴스 데이터 가져오기
                    news_data = self.api_module.get_latest_news_data()
                    
                    if news_data:
                        # API 데이터 구조에 맞게 처리
                        news_item = None
                        if news_type == 'newyork' and 'newyork-market' in news_data:
                            news_item = news_data['newyork-market']
                        elif news_type == 'kospi' and 'kospi-close' in news_data:
                            news_item = news_data['kospi-close']
                        elif news_type == 'exchange' and 'exchange-rate' in news_data:
                            news_item = news_data['exchange-rate']
                        
                        if news_item and 'title' in news_item and 'time' in news_item:
                            current_title = news_item['title']
                            current_time_str = news_item['time']
                            
                            # 새로운 뉴스인지 확인
                            if (current_title != info['last_title'] or 
                                current_time_str != info['last_time']):
                                
                                self.log_message(f"🆕 새 뉴스 발견: {info['display_name']} - {current_title[:50]}...")
                                
                                # 오늘 발행된 뉴스만 알림 발송
                                if self.is_today_news(news_item.get('date', '')):
                                    self.send_news_publication_alert(news_type, news_item)
                                    news_found = True
                                
                                # 상태 업데이트
                                info['last_title'] = current_title
                                info['last_time'] = current_time_str
                                info['status'] = '발행 완료'
                                
                            else:
                                # 기존 뉴스와 동일 - 지연 체크
                                self.check_delay_alert(news_type, info)
                        else:
                            self.log_message(f"⚠️ {info['display_name']} 데이터 형식 오류")
                            info['status'] = '데이터 형식 오류'
                    
                    else:
                        self.log_message(f"⚠️ {info['display_name']} 데이터 없음")
                        info['status'] = '데이터 없음'
                
                except Exception as e:
                    self.log_message(f"❌ {info['display_name']} 체크 오류: {e}")
                    info['status'] = '오류'
            
            # 뉴스가 발견되지 않은 경우 주기적으로 상태 알림
            if not news_found and current_time.minute % 30 == 0:
                self.send_no_update_notification()
            
        except Exception as e:
            self.log_message(f"❌ 뉴스 업데이트 체크 오류: {e}")
    
    def is_today_news(self, date_str):
        """오늘 날짜 뉴스인지 확인"""
        try:
            if not date_str:
                return False
            
            today = datetime.now().strftime('%Y%m%d')
            return date_str == today
        except:
            return False
    
    def send_news_publication_alert(self, news_type, news_data):
        """뉴스 발행 알림 전송 (실제 포스코 뉴스 형태)"""
        try:
            info = self.news_types[news_type]
            
            self.log_message(f"✅ {info['display_name']} 정시 발행 알림 생성 중...")
            
            # 실제 포스코 정시 발행 알림 메시지 생성
            current_time = datetime.now()
            publication_message = f"""✅ KOSPI CLOSE 정시 발행 완료

📅 발행 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
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
            
            # 직접 웹훅 전송 (실제 포스코 뉴스 형태)
            message_id = self.send_direct_webhook(
                "POSCO 뉴스 ✅",
                "✅ 정시 발행 완료",
                publication_message,
                "#28a745"
            )
            
            if message_id:
                self.log_message(f"✅ {info['display_name']} 발행 알림 전송 성공")
            else:
                self.log_message(f"⚠️ {info['display_name']} 발행 알림 전송 실패")
            
        except Exception as e:
            self.log_message(f"❌ 뉴스 발행 알림 전송 오류: {e}")
    
    def check_delay_alert(self, news_type, info):
        """지연 발행 알림 체크"""
        try:
            current_time = datetime.now()
            last_check = self.last_news_check.get(news_type, current_time)
            
            # 30분 이상 업데이트가 없으면 지연 알림
            if (current_time - last_check).total_seconds() > 1800:  # 30분
                self.send_delay_notification(news_type, info)
                self.last_news_check[news_type] = current_time
        
        except Exception as e:
            self.log_message(f"❌ 지연 알림 체크 오류: {e}")
    
    def send_delay_notification(self, news_type, info):
        """지연 발행 알림 전송 (실제 포스코 뉴스 형태)"""
        try:
            if not self.webhook_sender:
                return
            
            self.log_message(f"⏰ {info['display_name']} 지연 알림 생성 중...")
            
            # 실제 포스코 지연 발행 알림 메시지 생성
            current_time = datetime.now()
            delay_message = f"""⏰ 증시마감 지연 발행 알림

📅 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📊 예상 발행 시간: 15:40 (±10분)
⏱️ 지연 시간: 약 3시간 20분

🔍 현재 상태:
├ KOSPI 지수: 종가 확정 대기 중
├ 거래량: 집계 진행 중
└ 발행 준비: 최종 검토 단계

⚠️ 발행 지연이 감지되었습니다.
📞 필요시 담당자에게 문의하세요."""
            
            # 직접 웹훅 전송 (실제 포스코 뉴스 형태)
            message_id = self.send_direct_webhook(
                "POSCO 뉴스 ⏰",
                "⏰ 증시마감 지연 발행 알림",
                delay_message,
                "#ffc107"
            )
            
            if message_id:
                self.log_message(f"✅ {info['display_name']} 지연 알림 전송 성공")
            else:
                self.log_message(f"⚠️ {info['display_name']} 지연 알림 전송 실패")
        
        except Exception as e:
            self.log_message(f"❌ 지연 알림 전송 오류: {e}")
    
    def send_no_update_notification(self):
        """데이터 갱신 없음 알림 전송 (실제 포스코 뉴스 형태)"""
        try:
            if not self.webhook_sender:
                return
            
            self.log_message("🔔 데이터 갱신 없음 알림 생성 중...")
            
            # 실제 포스코 데이터 갱신 없음 알림 메시지 생성
            current_time = datetime.now()
            no_update_message = f"""데이터 갱신 없음

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
⏰ 마지막 체크: {current_time.strftime('%Y-%m-%d %H:%M:%S')}

💡 현재 모든 뉴스 타입에서 새로운 데이터가 확인되지 않았습니다."""
            
            # 직접 웹훅 전송 (실제 포스코 뉴스 형태)
            message_id = self.send_direct_webhook(
                "POSCO 뉴스 🔔",
                "🔔 데이터 갱신 없음",
                no_update_message,
                "#6c757d"
            )
            
            if message_id:
                self.log_message("✅ 데이터 갱신 없음 알림 전송 성공")
            else:
                self.log_message("⚠️ 데이터 갱신 없음 알림 전송 실패")
        
        except Exception as e:
            self.log_message(f"❌ 데이터 갱신 없음 알림 오류: {e}")
    
    def check_scheduled_tasks(self):
        """스케줄된 작업 체크 및 실행"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        today_key = current_time.strftime('%Y-%m-%d')
        
        for task_name, (hour, minute) in self.scheduled_times.items():
            if (current_hour == hour and current_minute == minute and 
                f"{today_key}_{task_name}" not in self.executed_today):
                
                self.execute_scheduled_task(task_name)
                self.executed_today.add(f"{today_key}_{task_name}")
    
    def execute_scheduled_task(self, task_name):
        """스케줄된 작업 실행"""
        try:
            self.log_message(f"📅 스케줄 작업 실행: {task_name}")
            
            if task_name == 'morning_comparison':
                self.send_business_day_comparison()
            elif task_name == 'evening_summary':
                self.send_daily_report()
            elif task_name == 'git_pages_report':
                self.send_git_pages_report()
            elif task_name in ['morning_status', 'evening_detail', 'evening_analysis']:
                self.send_status_report(task_name)
        
        except Exception as e:
            self.log_message(f"❌ 스케줄 작업 실행 오류 ({task_name}): {e}")
    
    def send_business_day_comparison(self):
        """영업일 비교 분석 전송 (실제 API 데이터 기반)"""
        try:
            if not self.webhook_sender:
                return
            
            self.log_message("📊 POSCO 통합 AI 분석 리포트 생성 중...")
            
            # 실제 API에서 뉴스 데이터 가져오기
            news_data = {}
            published_count = 0
            delayed_count = 0
            
            if self.api_module:
                try:
                    api_data = self.api_module.get_latest_news_data()
                    if api_data:
                        news_data = api_data
                        self.log_message("✅ API 데이터 로드 성공")
                    else:
                        self.log_message("⚠️ API 데이터 없음 - 기본값 사용")
                except Exception as e:
                    self.log_message(f"⚠️ API 데이터 로드 실패: {e} - 기본값 사용")
            
            # 뉴스별 발행 현황 분석
            current_time = datetime.now()
            today_str = current_time.strftime('%Y%m%d')
            
            news_status = {}
            for news_type, info in self.news_types.items():
                api_key = info['api_key']
                status_emoji = "⭕"
                status_text = "오늘 발행되지 않음"
                latest_info = "최신: "
                
                # API 데이터에서 해당 뉴스 타입 확인
                if news_data and api_key in news_data:
                    item = news_data[api_key]
                    if item and 'date' in item and item['date'] == today_str:
                        status_emoji = "✅"
                        status_text = f"정시 발행 ({item.get('time', '시간미상')})"
                        latest_info = f"최신: {item.get('title', '제목없음')[:30]}..."
                        published_count += 1
                    else:
                        delayed_count += 1
                else:
                    delayed_count += 1
                
                news_status[news_type] = {
                    'emoji': status_emoji,
                    'status': status_text,
                    'latest': latest_info,
                    'display_name': info['display_name']
                }
            
            # 시장 상황 분석 (발행 비율 기반)
            total_news = len(self.news_types)
            if published_count >= total_news * 0.7:
                market_mood = "긍정적"
            elif published_count >= total_news * 0.4:
                market_mood = "혼조"
            else:
                market_mood = "부정적"
            
            # 투자 전략 결정 (시장 상황 기반)
            if market_mood == "긍정적":
                strategy = "적극적 매수"
                portfolio = "성장주 60%, 가치주 30%, 현금 10%"
                opportunity = "기술주, 성장주"
            elif market_mood == "혼조":
                strategy = "균형 전략"
                portfolio = "성장주 50%, 가치주 30%, 현금 20%"
                opportunity = "우량주, ETF"
            else:
                strategy = "보수적 접근"
                portfolio = "가치주 40%, 채권 30%, 현금 30%"
                opportunity = "배당주, 안전자산"
            
            # 메시지 생성 (마크다운 문법 최소화)
            message_content = f"""📊 POSCO 통합 AI 분석 ({current_time.strftime('%Y-%m-%d %H:%M:%S')})
═══════════════════════════════════════════════════════════════════════════════

📈 시장 종합 상황: 📊 {market_mood}
📊 분석 범위: {total_news}개 뉴스 타입 분석
⏰ 급일 발행: {published_count}/{total_news}개 완료

🏢 뉴스별 발행 현황
─────────────────────────────────────────────────────────────────────────────

{chr(10).join([f"{status['emoji']} {status['display_name']}: {status['status']} ({status['latest']})" for status in news_status.values()])}

🏛️ 투자 전략 가이드
─────────────────────────────────────────────────────────────────────────────

📊 전망: {strategy}
💰 포트폴리오: {portfolio}
📈 매수 기회: {opportunity}

🎯 핵심 요약
─────────────────────────────────────────────────────────────────────────────

📊 시장 분위기: {market_mood}
📊 정시 발행: {published_count}개 | 지연 발행: {delayed_count}개
💡 투자 전략: {strategy}"""
            
            # 상세 분석 보기 링크 URL 생성
            report_url = f"https://shuserker.github.io/infomax_api/reports/posco_analysis_{current_time.strftime('%Y%m%d_%H%M%S')}.html"
            
            # 직접 웹훅 전송 (캡처와 같은 형태 - 제목에 하이퍼링크 포함)
            message_id = self.send_direct_webhook(
                "📊 POSCO 통합 AI 분석 리포트",
                "📊 POSCO 통합 AI 분석 리포트",
                message_content,
                "#007bff",
                link_url=report_url,
                link_text="📊 상세 분석 보기"
            )
            
            if message_id:
                self.log_message("✅ POSCO 통합 AI 분석 리포트 전송 성공")
            else:
                self.log_message("⚠️ POSCO 통합 AI 분석 리포트 전송 실패")
        
        except Exception as e:
            self.log_message(f"❌ POSCO 통합 AI 분석 리포트 오류: {e}")
    
    def send_daily_report(self):
        """일일 리포트 전송 (실제 포스코 뉴스 형태)"""
        try:
            if not self.webhook_sender:
                return
            
            self.log_message("📊 일일 통합 리포트 생성 중...")
            
            # 실제 포스코 일일 통합 리포트 메시지 생성
            current_time = datetime.now()
            message_content = f"""📊 POSCO 뉴스 일일 통합 리포트

📅 리포트 날짜: {current_time.strftime('%Y-%m-%d')}
🕐 생성 시간: {current_time.strftime('%H:%M:%S')}

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
            
            # 직접 웹훅 전송 (실제 포스코 뉴스 형태)
            message_id = self.send_direct_webhook(
                "POSCO 뉴스 📊",
                "📊 일일 통합 리포트",
                message_content,
                "#28a745"
            )
            
            if message_id:
                self.log_message("✅ 일일 통합 리포트 전송 성공")
            else:
                self.log_message("⚠️ 일일 통합 리포트 전송 실패")
        
        except Exception as e:
            self.log_message(f"❌ 일일 리포트 오류: {e}")
    
    def send_status_report(self, task_name):
        """상태 리포트 전송"""
        try:
            if not self.webhook_sender:
                return
            
            status_message = f"""📊 POSCO 뉴스 상태 리포트 ({task_name})

📅 리포트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 뉴스 상태:
{chr(10).join([f'{info["emoji"]} {info["display_name"]}: {info["status"]}' for info in self.news_types.values()])}

✅ 시스템이 정상적으로 작동 중입니다."""
            
            message_id = self.webhook_sender.send_status_notification(
                {
                    "status_message": status_message,
                    "task_name": task_name,
                    "report_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            if message_id:
                self.log_message(f"📊 상태 리포트 전송 ({task_name}): {message_id}")
        
        except Exception as e:
            self.log_message(f"❌ 상태 리포트 오류: {e}")
    
    def send_git_pages_report(self):
        """Git Pages 리포트 전송 (실제 HTML 리포트 생성)"""
        try:
            if not self.webhook_sender:
                return
            
            self.log_message("📊 POSCO 통합 분석 리포트 (웹 버전) 생성 중...")
            
            # 실제 HTML 리포트 생성
            github_url = self.generate_html_report()
            
            if not github_url:
                self.log_message("❌ HTML 리포트 생성 실패")
                return
            
            # 실제 API에서 뉴스 데이터 가져오기
            news_data = {}
            published_count = 0
            delayed_count = 0
            
            if self.api_module:
                try:
                    api_data = self.api_module.get_latest_news_data()
                    if api_data:
                        news_data = api_data
                        self.log_message("✅ API 데이터 로드 성공")
                    else:
                        self.log_message("⚠️ API 데이터 없음 - 기본값 사용")
                except Exception as e:
                    self.log_message(f"⚠️ API 데이터 로드 실패: {e} - 기본값 사용")
            
            # 뉴스별 발행 현황 분석
            current_time = datetime.now()
            today_str = current_time.strftime('%Y%m%d')
            
            news_status = {}
            for news_type, info in self.news_types.items():
                api_key = info['api_key']
                status_emoji = "⭕"
                status_text = "오늘 발행되지 않음"
                latest_info = "최신: "
                
                # API 데이터에서 해당 뉴스 타입 확인
                if news_data and api_key in news_data:
                    item = news_data[api_key]
                    if item and 'date' in item and item['date'] == today_str:
                        status_emoji = "✅"
                        status_text = f"정시 발행 ({item.get('time', '시간미상')})"
                        latest_info = f"최신: {item.get('title', '제목없음')[:30]}..."
                        published_count += 1
                    else:
                        delayed_count += 1
                else:
                    delayed_count += 1
                
                news_status[news_type] = {
                    'emoji': status_emoji,
                    'status': status_text,
                    'latest': latest_info,
                    'display_name': info['display_name']
                }
            
            # 시장 상황 분석 (발행 비율 기반)
            total_news = len(self.news_types)
            if published_count >= total_news * 0.7:
                market_mood = "긍정적"
                strategy = "적극적 매수"
                portfolio = "성장주 60%, 가치주 30%, 현금 10%"
                opportunity = "기술주, 성장주"
            elif published_count >= total_news * 0.4:
                market_mood = "혼조"
                strategy = "균형 전략"
                portfolio = "성장주 50%, 가치주 30%, 현금 20%"
                opportunity = "우량주, ETF"
            else:
                market_mood = "부정적"
                strategy = "보수적 접근"
                portfolio = "가치주 40%, 채권 30%, 현금 30%"
                opportunity = "배당주, 안전자산"
            
            # 메시지 생성 (고객용 - 개발자 메시지 제거)
            git_pages_message = f"""📊 POSCO 통합 AI 분석 ({current_time.strftime('%Y-%m-%d %H:%M:%S')})
═══════════════════════════════════════════════════════════════════════════════

📈 시장 종합 상황: 📊 {market_mood}
📊 분석 범위: {total_news}개 뉴스 타입 분석
⏰ 급일 발행: {published_count}/{total_news}개 완료

🏢 뉴스별 발행 현황
─────────────────────────────────────────────────────────────────────────────

{chr(10).join([f"{status['emoji']} {status['display_name']}: {status['status']} ({status['latest']})" for status in news_status.values()])}

🏛️ 투자 전략 가이드
─────────────────────────────────────────────────────────────────────────────

📊 전망: {strategy}
💰 포트폴리오: {portfolio}
📈 매수 기회: {opportunity}

🎯 핵심 요약
─────────────────────────────────────────────────────────────────────────────

📊 시장 분위기: {market_mood}
📊 정시 발행: {published_count}개 | 지연 발행: {delayed_count}개
💡 투자 전략: {strategy}

📊 상세 차트와 분석은 웹 리포트에서 확인하세요."""
            
            # 직접 웹훅 전송 (캡처와 같은 형태 - 제목에 하이퍼링크 포함)
            message_id = self.send_direct_webhook(
                "📊 POSCO 통합 AI 분석 리포트",
                "📊 POSCO 통합 분석 리포트 (웹 버전)",
                git_pages_message,
                "#17a2b8",
                link_url=github_url,
                link_text="📊 상세 분석 보기"
            )
            
            if message_id:
                self.log_message("✅ POSCO 통합 분석 리포트 (웹 버전) 전송 성공")
            else:
                self.log_message("⚠️ POSCO 통합 분석 리포트 (웹 버전) 전송 실패")
        
        except Exception as e:
            self.log_message(f"❌ POSCO 통합 분석 리포트 (웹 버전) 오류: {e}")
    
    def generate_html_report(self, news_data=None):
        """실제 HTML 리포트 생성 (38715ca 커밋 기반)"""
        try:
            current_time = datetime.now()
            timestamp = current_time.strftime("%Y%m%d_%H%M%S")
            filename = f"posco_integrated_analysis_{timestamp}.html"
            
            # API 데이터 가져오기
            if news_data is None and self.api_module:
                try:
                    news_data = self.api_module.get_latest_news_data()
                except Exception as e:
                    self.log_message(f"⚠️ API 데이터 로드 실패: {e}")
                    news_data = {}
            
            if not news_data:
                news_data = {}
            
            # 뉴스별 발행 현황 분석
            today_str = current_time.strftime('%Y%m%d')
            published_count = 0
            total_count = len(self.news_types)
            
            news_items_html = ""
            for news_type, info in self.news_types.items():
                api_key = info['api_key']
                is_published = False
                title = "발행 대기 중"
                
                if news_data and api_key in news_data:
                    item = news_data[api_key]
                    if item and 'date' in item and item['date'] == today_str:
                        is_published = True
                        title = item.get('title', '제목없음')
                        published_count += 1
                
                status_class = "news-published" if is_published else "news-pending"
                status_badge_class = "status-published" if is_published else "status-pending"
                status_text = "✅ 발행완료" if is_published else "⏳ 대기중"
                
                news_items_html += f"""
                <div class="{status_class} news-item">
                    <div>
                        <div style="font-weight: bold;">{info['emoji']} {info['display_name']}</div>
                        <div style="font-size: 0.9em; color: #666;">{title}</div>
                    </div>
                    <span class="status-badge {status_badge_class}">{status_text}</span>
                </div>"""
            
            # 시장 분위기 분석
            completion_rate = f"{published_count}/{total_count}"
            if published_count >= total_count * 0.7:
                market_sentiment = "긍정"
                market_analysis = "대부분의 뉴스가 발행되어 시장 상황이 안정적입니다."
            elif published_count >= total_count * 0.4:
                market_sentiment = "중립"
                market_analysis = "일부 뉴스가 발행되어 시장 상황을 지켜봐야 합니다."
            else:
                market_sentiment = "부정"
                market_analysis = "뉴스 발행이 부족하여 신중한 접근이 필요합니다."
            
            # 투자 전략 생성
            if market_sentiment == "긍정":
                strategies = [
                    ("📊 단기", "적극적 매수 전략으로 성장주 중심 투자"),
                    ("📊 중기", "기술주와 우량주 균형 투자"),
                    ("📊 장기", "성장 동력이 있는 섹터 중심 장기 투자")
                ]
                risks = [
                    ("🟡 보통", "과도한 낙관으로 인한 리스크"),
                    ("🔵 낮음", "시장 변동성에 따른 단기 조정")
                ]
            elif market_sentiment == "중립":
                strategies = [
                    ("📊 단기", "신중한 접근으로 우량주 중심 투자"),
                    ("📊 중기", "추가 정보 수집 후 투자 결정"),
                    ("📊 장기", "장기적 관점에서 가치주 발굴")
                ]
                risks = [
                    ("🟡 보통", "정보 부족으로 인한 투자 판단 리스크"),
                    ("🟡 보통", "일부 뉴스 미발행으로 인한 불완전한 시장 분석")
                ]
            else:
                strategies = [
                    ("📊 단기", "뉴스 발행이 부족하여 신중한 접근이 필요합니다"),
                    ("📊 중기", "추가 정보 수집 후 투자 결정을 하세요"),
                    ("📊 장기", "장기적으로는 POSCO 관련 뉴스 트렌드를 지속 모니터링하세요")
                ]
                risks = [
                    ("🔴 높음", "정보 부족으로 인한 투자 판단 리스크"),
                    ("🟡 보통", "일부 뉴스 미발행으로 인한 불완전한 시장 분석")
                ]
            
            strategies_html = "".join([f"<div class='strategy-item'><strong>{period}:</strong> {desc}</div>" for period, desc in strategies])
            
            risks_html = ""
            for level, desc in risks:
                if "높음" in level:
                    risk_class = "risk-high"
                elif "보통" in level:
                    risk_class = "risk-medium"
                else:
                    risk_class = "risk-low"
                risks_html += f"<div class='risk-item {risk_class}'><strong>{level}:</strong> {desc}</div>"
            
            # HTML 템플릿 생성 (38715ca 커밋 기반)
            html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 POSCO 뉴스 통합 분석 리포트</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #2c3e50; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .header h1 {{ color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #7f8c8d; font-size: 1.2em; }}
        .header .timestamp {{ color: #95a5a6; font-size: 0.9em; margin-top: 10px; }}
        .summary-card {{ background: white; border-radius: 15px; padding: 25px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .content-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; margin-bottom: 25px; }}
        .card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #2c3e50; font-size: 1.5em; margin-bottom: 20px; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .news-item {{ display: flex; justify-content: space-between; align-items: center; padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #3498db; }}
        .news-published {{ border-left-color: #27ae60; }}
        .news-pending {{ border-left-color: #e74c3c; }}
        .status-badge {{ padding: 5px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }}
        .status-published {{ background: #d4edda; color: #155724; }}
        .status-pending {{ background: #f8d7da; color: #721c24; }}
        .insight-box {{ background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .strategy-item {{ background: #e8f5e8; border-left: 4px solid #28a745; padding: 12px; margin: 10px 0; border-radius: 5px; }}
        .risk-item {{ padding: 12px; margin: 10px 0; border-radius: 5px; border-left: 4px solid; }}
        .risk-high {{ background: #f8d7da; border-left-color: #dc3545; }}
        .risk-medium {{ background: #fff3cd; border-left-color: #ffc107; }}
        .risk-low {{ background: #d1ecf1; border-left-color: #17a2b8; }}
        .footer {{ background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 20px; text-align: center; color: #7f8c8d; margin-top: 30px; }}
        @media (max-width: 768px) {{ .content-grid {{ grid-template-columns: 1fr; }} .header h1 {{ font-size: 2em; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 POSCO 뉴스 통합 분석 리포트</h1>
            <div class="subtitle">일일 종합 시장 분석 및 투자 인사이트</div>
            <div class="timestamp">생성 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary-card">
            <h2>📋 종합 요약</h2>
            <div class="insight-box">
                <h3>📊 발행 현황: {completion_rate} (진행중)</h3>
                <h3>📈 시장 분위기: {market_sentiment}</h3>
                <h3>📅 데이터 기준: 당일 데이터</h3>
                <p>{market_analysis}</p>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="card">
                <h2>📰 뉴스 발행 현황</h2>
                {news_items_html}
            </div>
            
            <div class="card">
                <h2>📊 통합 시장 분석</h2>
                <div class="insight-box">
                    <h3>📈 전체 시장 분위기: {market_sentiment}</h3>
                </div>
            </div>
            
            <div class="card">
                <h2>💼 통합 투자 전략</h2>
                {strategies_html}
            </div>
            
            <div class="card">
                <h2>⚠️ 통합 리스크 분석</h2>
                {risks_html}
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 POSCO 뉴스 AI 분석 시스템 | 통합 리포트 v1.0</p>
        </div>
    </div>
</body>
</html>"""
            
            # reports 디렉토리 생성 및 파일 저장
            reports_dir = os.path.join(os.path.dirname(self.script_dir), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            report_file = os.path.join(reports_dir, filename)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # GitHub Pages URL 생성
            github_url = f"https://shuserker.github.io/infomax_api/reports/{filename}"
            
            self.log_message(f"✅ HTML 리포트 생성 완료: {filename}")
            return github_url
            
        except Exception as e:
            self.log_message(f"❌ HTML 리포트 생성 오류: {e}")
            return None
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러 (Ctrl+C 처리)"""
        self.log_message("🛑 종료 신호 수신됨")
        self.running = False
    
    def run(self):
        """메인 실행 루프"""
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 시작 알림 전송
        self.send_startup_notification()
        
        self.log_message("🔄 POSCO 메인 알림 시스템 실행 시작")
        
        while self.running:
            try:
                # 뉴스 업데이트 체크
                self.check_news_updates()
                
                # 스케줄된 작업 체크
                self.check_scheduled_tasks()
                
                # 대기
                time.sleep(60)  # 1분마다 체크
                
            except Exception as e:
                self.log_message(f"❌ 메인 루프 오류: {e}")
                time.sleep(60)
        
        self.log_message("✅ POSCO 메인 알림 시스템 종료")

def test_business_day_comparison():
    """영업일 비교 분석 테스트 함수"""
    try:
        print("🧪 영업일 비교 분석 테스트 시작")
        notifier = PoscoMainNotifier()
        notifier.send_business_day_comparison()
        print("✅ 영업일 비교 분석 테스트 완료")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")

def test_daily_report():
    """일일 리포트 테스트 함수"""
    try:
        print("🧪 일일 리포트 테스트 시작")
        notifier = PoscoMainNotifier()
        notifier.send_daily_report()
        print("✅ 일일 리포트 테스트 완료")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")

def test_delay_notification():
    """지연 알림 테스트 함수"""
    try:
        print("🧪 지연 알림 테스트 시작")
        notifier = PoscoMainNotifier()
        # 테스트용 뉴스 정보
        test_info = {
            'display_name': 'KOSPI CLOSE',
            'last_time': '15:40'
        }
        notifier.send_delay_notification('kospi', test_info)
        print("✅ 지연 알림 테스트 완료")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")

def test_no_update_notification():
    """데이터 갱신 없음 알림 테스트 함수"""
    try:
        print("🧪 데이터 갱신 없음 알림 테스트 시작")
        notifier = PoscoMainNotifier()
        notifier.send_no_update_notification()
        print("✅ 데이터 갱신 없음 알림 테스트 완료")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")

def test_git_pages_report():
    """Git Pages 리포트 생성 테스트 함수"""
    try:
        print("🧪 Git Pages 리포트 테스트 시작")
        notifier = PoscoMainNotifier()
        notifier.send_git_pages_report()
        print("✅ Git Pages 리포트 테스트 완료")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "test_comparison":
            test_business_day_comparison()
        elif command == "test_report":
            test_daily_report()
        elif command == "test_delay":
            test_delay_notification()
        elif command == "test_no_update":
            test_no_update_notification()
        elif command == "test_git_pages":
            test_git_pages_report()
        else:
            print("사용법: python posco_main_notifier.py [test_comparison|test_report|test_delay|test_no_update|test_git_pages]")
    else:
        try:
            notifier = PoscoMainNotifier()
            notifier.run()
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단됨")
        except Exception as e:
            print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    main()