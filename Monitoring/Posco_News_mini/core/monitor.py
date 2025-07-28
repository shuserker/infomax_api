# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 리팩토링된 메인 모니터 클래스
"""

import time
from datetime import datetime, timedelta

from core.api_client import PoscoNewsAPIClient
from core.notification import DoorayNotifier
from core.data_processor import NewsDataProcessor
from utils.cache_utils import load_cache, save_cache, get_data_hash
from utils.logging_utils import log_with_timestamp


class PoscoNewsMonitor:
    """
    POSCO 뉴스 모니터링 시스템 메인 클래스 (리팩토링됨)
    
    기존의 거대한 클래스를 여러 모듈로 분리하여 
    단일 책임 원칙을 준수하고 유지보수성을 향상시켰습니다.
    """
    
    def __init__(self, dooray_webhook_url):
        """
        모니터링 시스템 초기화
        
        Args:
            dooray_webhook_url (str): Dooray 웹훅 URL
        """
        # 설정 로드
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from config import API_CONFIG, MONITORING_CONFIG, BOT_PROFILE_IMAGE_URL
        
        # 컴포넌트 초기화
        self.api_client = PoscoNewsAPIClient(API_CONFIG)
        self.notifier = DoorayNotifier(dooray_webhook_url, BOT_PROFILE_IMAGE_URL)
        self.data_processor = NewsDataProcessor()
        
        # 설정값
        self.cache_file = MONITORING_CONFIG["cache_file"]
        self.max_retry_days = MONITORING_CONFIG["max_retry_days"]
        self.last_hash = None
    
    def check_once(self, simple_status=False):
        """
        일회성 뉴스 상태 체크
        
        Args:
            simple_status (bool): True면 간결한 상태 알림 전송
            
        Returns:
            bool: 변경사항 발견 여부
        """
        log_with_timestamp(f"뉴스 데이터 체크 중...", "INFO")
        
        current_data = self.api_client.get_news_data()
        if not current_data:
            self.notifier.send_notification("API 호출 실패", is_error=True)
            return False
        
        current_hash = get_data_hash(current_data)
        cached_data, cached_hash = load_cache(self.cache_file)
        
        if cached_hash != current_hash:
            log_with_timestamp("데이터 변경 감지!", "SUCCESS")
            
            change_result = self.data_processor.detect_changes(cached_data, current_data)
            
            if change_result["changes"]:
                for news_type in change_result["changes"]:
                    old_item = cached_data.get(news_type) if cached_data else None
                    new_item = current_data[news_type]
                    self.notifier.send_change_notification(news_type, old_item, new_item)
            
            save_cache(self.cache_file, current_data, current_hash)
            self.last_hash = current_hash
            return True
        else:
            log_with_timestamp("변경사항 없음", "INFO")
            
            status_info = self.data_processor.get_status_info(current_data)
            if simple_status:
                self._send_simple_status_notification(current_data, status_info)
            else:
                self.notifier.send_status_notification(current_data, status_info)
            return False
    
    def check_silent(self):
        """
        조용한 모드 체크 - 변경사항 있을 때만 알림 전송
        
        Returns:
            bool: 변경사항 발견 여부
        """
        log_with_timestamp("뉴스 데이터 체크 중... (조용한 모드)", "INFO")
        
        current_data = self.api_client.get_news_data()
        if not current_data:
            log_with_timestamp("API 호출 실패 (야간 모드 - 알림 없음)", "ERROR")
            return False
        
        current_hash = get_data_hash(current_data)
        cached_data, cached_hash = load_cache(self.cache_file)
        
        if cached_hash != current_hash:
            log_with_timestamp("데이터 변경 감지! (야간에도 알림 전송)", "SUCCESS")
            
            change_result = self.data_processor.detect_changes(cached_data, current_data)
            
            if change_result["changes"]:
                for news_type in change_result["changes"]:
                    old_item = cached_data.get(news_type) if cached_data else None
                    new_item = current_data[news_type]
                    self.notifier.send_change_notification(news_type, old_item, new_item)
            
            save_cache(self.cache_file, current_data, current_hash)
            self.last_hash = current_hash
            return True
        else:
            log_with_timestamp("변경사항 없음 - 야간 모드로 알림 없음", "INFO")
            return False
    
    def check_extended(self):
        """
        영업일 비교 체크 - 현재 vs 직전 영업일 상세 비교
        """
        log_with_timestamp("영업일 비교 체크 시작", "INFO")
        
        current_data = self.api_client.get_news_data()
        if not current_data:
            self.notifier.send_notification("API 호출 실패", is_error=True)
            return
        
        previous_data = self.data_processor.get_previous_day_data(
            self.api_client, current_data, self.max_retry_days
        )
        
        self._send_comparison_notification(current_data, previous_data)
    
    def send_daily_summary(self):
        """
        일일 요약 리포트 전송
        """
        log_with_timestamp("일일 요약 리포트 생성 중", "INFO")
        
        current_data = self.api_client.get_news_data()
        if not current_data:
            self.notifier.send_notification("API 호출 실패", is_error=True)
            return
        
        # 일일 요약 메시지 생성
        today_kr = datetime.now().strftime('%Y%m%d')
        weekday_name = self.data_processor.get_weekday_display()
        
        message = f"📋 {weekday_name}요일 POSCO 뉴스 일일 요약\n\n"
        
        today_news = []
        for news_type, news_data in current_data.items():
            if news_data.get('date') == today_kr:
                title = news_data.get('title', '제목 없음')[:50]
                time_str = news_data.get('time', '')
                if len(time_str) >= 4:
                    formatted_time = f"{time_str[:2]}:{time_str[2:4]}"
                else:
                    formatted_time = time_str
                
                today_news.append(f"📰 {news_type.upper()}\n⏰ {formatted_time} | {title}")
        
        if today_news:
            message += "\n\n".join(today_news)
        else:
            message += f"오늘({weekday_name}요일)은 새로운 뉴스가 발행되지 않았습니다."
        
        message += f"\n\n📅 요약 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.notifier.send_notification(message, bot_name_suffix=" 📋")
    
    def start_monitoring(self, interval_minutes=60):
        """
        기본 모니터링 시작 (고정 간격)
        
        Args:
            interval_minutes (int): 모니터링 간격 (분)
        """
        log_with_timestamp(f"기본 모니터링 시작 ({interval_minutes}분 간격)", "INFO")
        
        try:
            while True:
                self.check_once(simple_status=True)
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            log_with_timestamp("모니터링 중단됨", "WARNING")
    
    def start_smart_monitoring(self):
        """
        스마트 모니터링 시작 (시간대별 적응형 간격)
        """
        log_with_timestamp("스마트 모니터링 시작", "INFO")
        
        try:
            while True:
                current_hour = datetime.now().hour
                
                # 시간대별 간격 설정
                if 6 <= current_hour <= 8 or 15 <= current_hour <= 17:
                    # 집중 시간대: 20분 간격
                    interval_minutes = 20
                    self.check_once(simple_status=True)
                elif 7 <= current_hour <= 18:
                    # 일반 운영 시간: 2시간 간격
                    interval_minutes = 120
                    self.check_once(simple_status=True)
                else:
                    # 야간 조용한 모드: 1시간 간격, 변경사항만 알림
                    interval_minutes = 60
                    self.check_silent()
                
                # 특별 이벤트 처리
                if current_hour == 8:  # 오전 8시 전일 비교
                    self.check_extended()
                elif current_hour == 18:  # 오후 6시 일일 요약
                    self.send_daily_summary()
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            log_with_timestamp("스마트 모니터링 중단됨", "WARNING")
    
    def _send_simple_status_notification(self, current_data, status_info):
        """
        간결한 상태 알림 전송
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            status_info (str): 상태 정보 문자열
        """
        payload = {
            "botName": f"POSCO 뉴스{status_info}",
            "botIconImage": self.notifier.bot_profile_image_url,
            "text": "갱신 데이터 없음",
            "attachments": []
        }
        
        try:
            import requests
            response = requests.post(
                self.notifier.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                log_with_timestamp("간결 상태 알림 전송 성공", "SUCCESS")
        except Exception as e:
            log_with_timestamp(f"간결 상태 알림 전송 오류: {e}", "ERROR")
    
    def _send_comparison_notification(self, current_data, previous_data):
        """
        현재 vs 직전 영업일 데이터 비교 알림 전송
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            previous_data (dict): 직전 영업일 데이터
        """
        weekday_name = self.data_processor.get_weekday_display()
        expected_today = self.data_processor.get_expected_news_count_today()
        
        message = f"📈 {weekday_name}요일 영업일 비교 분석\n"
        message += f"🎯 예상 뉴스: {expected_today}개\n\n"
        
        for news_type, current_item in current_data.items():
            previous_item = previous_data.get(news_type)
            
            current_title = current_item.get('title', '데이터 없음')[:40]
            current_date = current_item.get('date', '')
            
            message += f"📰 {news_type.upper()}\n"
            message += f"📅 현재: {current_title}\n"
            
            if previous_item:
                prev_title = previous_item.get('title', '데이터 없음')[:40]
                prev_date = previous_item.get('date', '')
                message += f"📅 이전: {prev_title}\n"
                
                if current_title != prev_title:
                    message += "🔄 변경됨\n"
                else:
                    message += "📝 동일함\n"
            else:
                message += "📅 이전: 데이터 없음\n"
            
            message += "\n"
        
        message += f"📊 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.notifier.send_notification(message, bot_name_suffix=" 📈")