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
        
        # 워치햄스터에서 이관된 뉴스 관련 고정 시간 작업
        self.fixed_time_tasks = {
            "06:00": ("1", "아침 현재 상태 체크"),
            "06:10": ("2", "아침 영업일 비교 분석"), 
            "18:00": ("5", "저녁 일일 요약 리포트"),
            "18:10": ("7", "저녁 상세 일일 요약"),
            "18:20": ("8", "저녁 고급 분석")
        }
        self.executed_fixed_tasks = set()  # 오늘 실행된 고정 작업들
        
        # 이전 상태 로드
        self.load_state()
        
        print("📡 실시간 뉴스 모니터 초기화 완료")
        print(f"🔍 모니터링 대상: {len(self.monitors)}개 뉴스 타입")
        print(f"🕐 고정 시간 작업: {len(self.fixed_time_tasks)}개")
    
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
    
    def check_fixed_time_tasks(self):
        """
        고정 시간 작업들 체크 및 실행 (워치햄스터에서 이관)
        """
        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        current_date = current_time.strftime("%Y-%m-%d")
        
        # 날짜가 바뀌면 실행된 작업 목록 초기화
        if not hasattr(self, '_last_check_date') or self._last_check_date != current_date:
            self.executed_fixed_tasks = set()
            self._last_check_date = current_date
        
        # 고정 시간 작업 체크
        for time_str, (task_type, task_name) in self.fixed_time_tasks.items():
            if current_time_str == time_str:
                task_key = f"{current_date}_{time_str}"
                if task_key not in self.executed_fixed_tasks:
                    print(f"🕐 고정 시간 작업 실행: {time_str} - {task_name}")
                    self.execute_news_task(task_type, task_name)
                    self.executed_fixed_tasks.add(task_key)
    
    def execute_news_task(self, task_type, task_name):
        """
        뉴스 관련 작업 실행 (워치햄스터에서 이관)
        """
        try:
            print(f"📅 뉴스 작업 실행: {task_name}")
            
            if task_type == "1":  # 상태 체크
                self.execute_status_check_task(task_name)
            elif task_type == "2":  # 비교 분석
                self.execute_comparison_task(task_name)
            elif task_type == "5":  # 일일 요약
                self.execute_daily_summary_task(task_name)
            elif task_type == "7":  # 상세 요약
                self.execute_detailed_summary_task(task_name)
            elif task_type == "8":  # 고급 분석
                self.execute_advanced_analysis_task(task_name)
            else:
                print(f"⚠️ 알 수 없는 작업 타입: {task_type}")
                
        except Exception as e:
            print(f"❌ {task_name} 오류: {e}")
    
    def execute_status_check_task(self, task_name):
        """
        상태 체크 작업 실행
        """
        try:
            print(f"🔍 {task_name} 시작")
            
            # 각 뉴스 타입별 현재 상태 체크
            status_results = []
            
            for news_type, info in self.monitors.items():
                try:
                    data = info['monitor'].get_current_news_data()
                    
                    if data and data.get('title'):
                        status = f"✅ {info['name']}: 최신 뉴스 있음"
                        status_results.append(status)
                    else:
                        status = f"⚠️ {info['name']}: 뉴스 없음"
                        status_results.append(status)
                        
                except Exception as e:
                    status = f"❌ {info['name']}: 체크 실패"
                    status_results.append(status)
            
            # 상태 체크 결과 알림 (조용한 시간대 제외)
            if not self.is_quiet_hours():
                self.send_status_notification(task_name, status_results)
            
            print(f"✅ {task_name} 완료")
            
        except Exception as e:
            print(f"❌ 상태 체크 작업 오류: {e}")
    
    def execute_comparison_task(self, task_name):
        """
        비교 분석 작업 실행
        """
        try:
            print(f"📊 {task_name} 시작")
            
            # 각 뉴스별 현재 vs 이전 데이터 비교
            comparison_results = []
            
            for news_type, info in self.monitors.items():
                try:
                    current_data = info['monitor'].get_current_news_data()
                    last_title = info.get('last_title')
                    
                    if current_data and current_data.get('title'):
                        current_title = current_data['title']
                        
                        if last_title and last_title != current_title:
                            result = f"🆕 {info['name']}: 새 뉴스 감지"
                        elif last_title == current_title:
                            result = f"📋 {info['name']}: 동일한 뉴스"
                        else:
                            result = f"🔍 {info['name']}: 첫 번째 체크"
                        
                        comparison_results.append(result)
                    else:
                        comparison_results.append(f"⚠️ {info['name']}: 데이터 없음")
                        
                except Exception as e:
                    comparison_results.append(f"❌ {info['name']}: 분석 실패")
            
            # 비교 분석 결과 알림 (조용한 시간대 제외)
            if not self.is_quiet_hours():
                self.send_comparison_notification(task_name, comparison_results)
            
            print(f"✅ {task_name} 완료")
            
        except Exception as e:
            print(f"❌ 비교 분석 작업 오류: {e}")
    
    def execute_daily_summary_task(self, task_name):
        """
        일일 요약 작업 실행
        """
        try:
            print(f"📋 {task_name} 시작")
            
            # 오늘 발행된 뉴스 요약
            summary_data = []
            published_count = 0
            
            for news_type, info in self.monitors.items():
                try:
                    data = info['monitor'].get_current_news_data()
                    
                    if data and data.get('title'):
                        published_count += 1
                        summary_data.append(f"✅ {info['name']}: 발행 완료")
                    else:
                        summary_data.append(f"❌ {info['name']}: 미발행")
                        
                except Exception as e:
                    summary_data.append(f"⚠️ {info['name']}: 확인 불가")
            
            # 일일 요약 결과 알림 (조용한 시간대 제외)
            if not self.is_quiet_hours():
                self.send_daily_summary_notification(task_name, summary_data, published_count)
            
            print(f"✅ {task_name} 완료 ({published_count}/3 발행)")
            
        except Exception as e:
            print(f"❌ 일일 요약 작업 오류: {e}")
    
    def execute_detailed_summary_task(self, task_name):
        """
        상세 요약 작업 실행
        """
        try:
            print(f"📊 {task_name} 시작")
            
            # 상세한 뉴스 정보 수집
            detailed_info = []
            
            for news_type, info in self.monitors.items():
                try:
                    data = info['monitor'].get_current_news_data()
                    
                    if data and data.get('title'):
                        title = data['title'][:50] + "..." if len(data['title']) > 50 else data['title']
                        publish_time = data.get('publish_time', '시간 정보 없음')
                        
                        detail = f"{info['name']}:\n  📋 {title}\n  🕐 {publish_time}"
                        detailed_info.append(detail)
                    else:
                        detailed_info.append(f"{info['name']}: 뉴스 없음")
                        
                except Exception as e:
                    detailed_info.append(f"{info['name']}: 정보 수집 실패")
            
            # 상세 요약 결과 알림 (조용한 시간대 제외)
            if not self.is_quiet_hours():
                self.send_detailed_summary_notification(task_name, detailed_info)
            
            print(f"✅ {task_name} 완료")
            
        except Exception as e:
            print(f"❌ 상세 요약 작업 오류: {e}")
    
    def execute_advanced_analysis_task(self, task_name):
        """
        고급 분석 작업 실행
        """
        try:
            print(f"🔬 {task_name} 시작")
            
            # 고급 분석 수행
            analysis_results = []
            total_news = 0
            
            for news_type, info in self.monitors.items():
                try:
                    data = info['monitor'].get_current_news_data()
                    
                    if data and data.get('title'):
                        total_news += 1
                        
                        # 간단한 분석 (제목 길이, 키워드 등)
                        title_length = len(data['title'])
                        has_urgent = '긴급' in data['title'] or '속보' in data['title']
                        
                        analysis = f"{info['name']}:\n"
                        analysis += f"  📏 제목 길이: {title_length}자\n"
                        analysis += f"  🚨 긴급성: {'높음' if has_urgent else '보통'}"
                        
                        analysis_results.append(analysis)
                    else:
                        analysis_results.append(f"{info['name']}: 분석할 뉴스 없음")
                        
                except Exception as e:
                    analysis_results.append(f"{info['name']}: 분석 실패")
            
            # 고급 분석 결과 알림 (조용한 시간대 제외)
            if not self.is_quiet_hours():
                self.send_advanced_analysis_notification(task_name, analysis_results, total_news)
            
            print(f"✅ {task_name} 완료 (분석 대상: {total_news}개)")
            
        except Exception as e:
            print(f"❌ 고급 분석 작업 오류: {e}")
    
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
    
    def send_status_notification(self, task_name, status_results):
        """상태 체크 결과 알림"""
        try:
            message = f"🔍 {task_name}\n\n"
            message += "\n".join(status_results)
            message += f"\n\n📅 체크 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            payload = {
                "botName": "POSCO 뉴스 상태 체크 🔍",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"🔍 {task_name}",
                "attachments": [{
                    "color": "#17a2b8",
                    "text": message
                }]
            }
            
            response = requests.post(DOORAY_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ {task_name} 알림 전송 성공")
            
        except Exception as e:
            print(f"❌ {task_name} 알림 전송 오류: {e}")
    
    def send_comparison_notification(self, task_name, comparison_results):
        """비교 분석 결과 알림"""
        try:
            message = f"📊 {task_name}\n\n"
            message += "\n".join(comparison_results)
            message += f"\n\n📅 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            payload = {
                "botName": "POSCO 뉴스 비교 분석 📊",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"📊 {task_name}",
                "attachments": [{
                    "color": "#28a745",
                    "text": message
                }]
            }
            
            response = requests.post(DOORAY_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ {task_name} 알림 전송 성공")
            
        except Exception as e:
            print(f"❌ {task_name} 알림 전송 오류: {e}")
    
    def send_daily_summary_notification(self, task_name, summary_data, published_count):
        """일일 요약 결과 알림"""
        try:
            total_count = len(self.monitors)
            
            if published_count == total_count:
                color = "#28a745"
                status_emoji = "✅"
            elif published_count >= 2:
                color = "#ffc107"
                status_emoji = "⚠️"
            else:
                color = "#dc3545"
                status_emoji = "❌"
            
            message = f"{status_emoji} {task_name}\n\n"
            message += f"📊 발행 현황: {published_count}/{total_count}\n\n"
            message += "\n".join(summary_data)
            message += f"\n\n📅 요약 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            payload = {
                "botName": "POSCO 뉴스 일일 요약 📋",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"{status_emoji} {task_name}",
                "attachments": [{
                    "color": color,
                    "text": message
                }]
            }
            
            response = requests.post(DOORAY_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ {task_name} 알림 전송 성공")
            
        except Exception as e:
            print(f"❌ {task_name} 알림 전송 오류: {e}")
    
    def send_detailed_summary_notification(self, task_name, detailed_info):
        """상세 요약 결과 알림"""
        try:
            message = f"📊 {task_name}\n\n"
            message += "\n\n".join(detailed_info)
            message += f"\n\n📅 상세 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            payload = {
                "botName": "POSCO 뉴스 상세 요약 📊",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"📊 {task_name}",
                "attachments": [{
                    "color": "#6f42c1",
                    "text": message
                }]
            }
            
            response = requests.post(DOORAY_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ {task_name} 알림 전송 성공")
            
        except Exception as e:
            print(f"❌ {task_name} 알림 전송 오류: {e}")
    
    def send_advanced_analysis_notification(self, task_name, analysis_results, total_news):
        """고급 분석 결과 알림"""
        try:
            message = f"🔬 {task_name}\n\n"
            message += f"📊 분석 대상: {total_news}개 뉴스\n\n"
            message += "\n\n".join(analysis_results)
            message += f"\n\n📅 고급 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            payload = {
                "botName": "POSCO 뉴스 고급 분석 🔬",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": f"🔬 {task_name}",
                "attachments": [{
                    "color": "#e83e8c",
                    "text": message
                }]
            }
            
            response = requests.post(DOORAY_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ {task_name} 알림 전송 성공")
            
        except Exception as e:
            print(f"❌ {task_name} 알림 전송 오류: {e}")
    
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
                current_time = datetime.now()
                print(f"\n⏰ {current_time.strftime('%H:%M:%S')} - 뉴스 업데이트 체크 중...")
                
                # 1. 고정 시간 작업 체크 (워치햄스터에서 이관)
                self.check_fixed_time_tasks()
                
                # 2. 뉴스 업데이트 체크
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