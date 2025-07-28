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
            return False
        
        current_hash = get_data_hash(current_data)
        cached_data, cached_hash = load_cache(self.cache_file)
        
        if cached_hash != current_hash:
            log_with_timestamp("데이터 변경 감지! (조용한 모드)", "SUCCESS")
            
            change_result = self.data_processor.detect_changes(cached_data, current_data)
            
            if change_result["changes"]:
                for news_type in change_result["changes"]:
                    old_item = cached_data.get(news_type) if cached_data else None
                    new_item = current_data[news_type]
                    self.notifier.send_change_notification(news_type, old_item, new_item)
            
            save_cache(self.cache_file, current_data, current_hash)
            self.last_hash = current_hash
            return True
        
        return False
    
    def check_extended(self):
        """
        확장 체크 - 영업일 비교 분석
        
        Returns:
            bool: 성공 여부
        """
        log_with_timestamp("영업일 비교 분석 중...", "INFO")
        
        current_data = self.api_client.get_news_data()
        if not current_data:
            self.notifier.send_notification("API 호출 실패", is_error=True)
            return False
        
        # 직전 영업일 데이터 조회
        previous_data = self.data_processor.get_previous_day_data(
            self.api_client, current_data, self.max_retry_days
        )
        
        if previous_data:
            self._send_comparison_notification(current_data, previous_data)
        else:
            log_with_timestamp("직전 영업일 데이터를 찾을 수 없음", "WARNING")
        
        return True
    
    def send_daily_summary(self):
        """
        일일 요약 리포트 전송
        
        오늘 발행된 뉴스와 직전 데이터를 비교한 요약 리포트를 전송합니다.
        
        Returns:
            bool: 성공 여부
        """
        log_with_timestamp("일일 요약 리포트 생성 중...", "INFO")
        
        current_data = self.api_client.get_news_data()
        if not current_data:
            self.notifier.send_notification("API 호출 실패", is_error=True)
            return False
        
        today_kr = datetime.now().strftime('%Y%m%d')
        today_weekday = datetime.now().weekday()
        weekday_name = self.data_processor.get_weekday_display()
        
        # 오늘 발행된 뉴스 수집
        today_news = {}
        for news_type, news_data in current_data.items():
            if news_data.get('date') == today_kr:
                today_news[news_type] = news_data
        
        # 직전 영업일 데이터 조회
        previous_data = self.data_processor.get_previous_day_data(
            self.api_client, current_data, self.max_retry_days
        )
        
        # 요약 메시지 생성
        message = f"📋 {weekday_name}요일 일일 요약 리포트\n\n"
        
        if today_news:
            message += f"📅 오늘 발행 뉴스 ({len(today_news)}개)\n"
            message += "━━━━━━━━━━━━━━━━━━━━━\n"
            
            for news_type, news_data in today_news.items():
                from config import NEWS_TYPES
                news_config = NEWS_TYPES.get(news_type, {"display_name": news_type.upper(), "emoji": "📰"})
                emoji = news_config["emoji"]
                type_display = news_config["display_name"]
                
                title = news_data.get('title', '')
                time_str = news_data.get('time', '')
                
                if time_str and len(time_str) >= 4:
                    formatted_time = f"{time_str[:2]}:{time_str[2:4]}"
                else:
                    formatted_time = "시간 없음"
                
                title_preview = title[:50] + "..." if len(title) > 50 else title
                
                message += f"┌ {emoji} {type_display}\n"
                message += f"├ 시간: {formatted_time}\n"
                message += f"└ 제목: {title_preview}\n\n"
        else:
            message += "📅 오늘 발행 뉴스: 없음\n\n"
        
        # 직전 데이터와 비교
        if previous_data:
            message += "📊 직전 영업일과 비교\n"
            message += "━━━━━━━━━━━━━━━━━━━━━\n"
            
            for news_type, current_news in current_data.items():
                from config import NEWS_TYPES
                news_config = NEWS_TYPES.get(news_type, {"display_name": news_type.upper(), "emoji": "📰"})
                emoji = news_config["emoji"]
                type_display = news_config["display_name"]
                
                previous_news = previous_data.get(news_type, {})
                
                current_title = current_news.get('title', '')
                previous_title = previous_news.get('title', '')
                
                if current_title != previous_title:
                    message += f"┌ {emoji} {type_display}\n"
                    message += f"├ 변경: 제목 업데이트\n"
                    
                    if previous_title:
                        prev_preview = previous_title[:40] + "..." if len(previous_title) > 40 else previous_title
                        message += f"├ 이전: {prev_preview}\n"
                    
                    curr_preview = current_title[:40] + "..." if len(current_title) > 40 else current_title
                    message += f"└ 현재: {curr_preview}\n\n"
        
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"📝 리포트 생성: {current_datetime}"
        
        # 요약 리포트 전송
        self.notifier.send_notification(message, bot_name_suffix=" 📋")
        return True
    
    def start_monitoring(self, interval_minutes=60):
        """
        기본 모니터링 시작
        
        Args:
            interval_minutes (int): 체크 간격 (분)
        """
        log_with_timestamp(f"기본 모니터링 시작 (간격: {interval_minutes}분)", "INFO")
        
        try:
            while True:
                self.check_silent()
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            log_with_timestamp("모니터링 중단됨", "INFO")
        except Exception as e:
            log_with_timestamp(f"모니터링 오류: {e}", "ERROR")
            self.notifier.send_notification(f"모니터링 오류 발생: {e}", is_error=True)
    
    def start_smart_monitoring(self):
        """
        스마트 모니터링 시작
        
        시간대별 적응형 간격으로 모니터링합니다.
        """
        log_with_timestamp("스마트 모니터링 시작", "INFO")
        
        try:
            while True:
                current_hour = datetime.now().hour
                interval = self._get_smart_interval(current_hour)
                
                log_with_timestamp(f"스마트 간격: {interval}분 (현재 시간: {current_hour}시)", "INFO")
                
                self.check_silent()
                time.sleep(interval * 60)
                
        except KeyboardInterrupt:
            log_with_timestamp("스마트 모니터링 중단됨", "INFO")
        except Exception as e:
            log_with_timestamp(f"스마트 모니터링 오류: {e}", "ERROR")
            self.notifier.send_notification(f"모니터링 오류 발생: {e}", is_error=True)
    
    def _send_simple_status_notification(self, current_data, status_info):
        """
        간결한 상태 알림 전송
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            status_info (str): 상태 정보 문자열
        """
        self.notifier.send_simple_status_notification(current_data, status_info)
    
    def _send_comparison_notification(self, current_data, previous_data):
        """
        영업일 비교 알림 전송
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            previous_data (dict): 직전 영업일 뉴스 데이터
        """
        self.notifier.send_comparison_notification(current_data, previous_data)
    
    def _get_smart_interval(self, current_hour):
        """
        시간대별 스마트 간격 계산
        
        Args:
            current_hour (int): 현재 시간 (0-23)
            
        Returns:
            int: 모니터링 간격 (분)
        """
        # 업무 시간 (9-18시): 30분 간격
        if 9 <= current_hour <= 18:
            return 30
        # 점심 시간 (12-13시): 15분 간격 (더 자주 체크)
        elif 12 <= current_hour <= 13:
            return 15
        # 저녁 시간 (18-22시): 60분 간격
        elif 18 <= current_hour <= 22:
            return 60
        # 야간 시간 (22-9시): 120분 간격 (조용한 모드)
        else:
            return 120