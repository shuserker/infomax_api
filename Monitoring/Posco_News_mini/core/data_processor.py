# -*- coding: utf-8 -*-
"""
데이터 처리 관련 모듈
"""

from datetime import datetime, timedelta
from config import NEWS_TYPES, STATUS_CONFIG


class NewsDataProcessor:
    """
    뉴스 데이터 처리 클래스
    
    데이터 분석, 상태 판단, 변경사항 감지 등을 담당합니다.
    """
    
    def __init__(self):
        self._today_cache = None
    
    def _get_today_info(self):
        """
        오늘 날짜 정보 캐싱 (성능 최적화)
        
        Returns:
            dict: 오늘 날짜 정보
        """
        if not self._today_cache or self._today_cache['date'] != datetime.now().date():
            now = datetime.now()
            self._today_cache = {
                'date': now.date(),
                'kr_format': now.strftime('%Y%m%d'),
                'weekday': now.weekday(),
                'weekday_name': ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
            }
        return self._today_cache
    
    def get_status_info(self, current_data):
        """
        상태 정보 계산 (요일별 예상 뉴스 수 고려)
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            
        Returns:
            str: 상태 표시 문자열 (예: " 🟢1 of 1", " 🔵휴일")
        """
        if not current_data:
            return " 🔴데이터 없음"
            
        today_info = self._get_today_info()
        today_kr = today_info['kr_format']
        today_weekday = today_info['weekday']
        
        # 오늘 발행된 뉴스 수
        today_count = 0
        expected_today = 0
        
        for news_type, news_data in current_data.items():
            # 오늘 발행 여부 확인
            if news_data.get('date') == today_kr:
                today_count += 1
            
            # 오늘 요일에 발행 예상 여부 확인
            news_config = NEWS_TYPES.get(news_type, {})
            if today_weekday in news_config.get('publish_days', []):
                expected_today += 1
        
        colors = STATUS_CONFIG["colors"]
        
        # 예상 뉴스 수 기준으로 상태 판단 (간결한 표기)
        if today_count == expected_today and expected_today > 0:
            return f" {colors['all_latest']}{today_count} of {expected_today}"
        elif today_count > 0:
            return f" {colors['partial_latest']}{today_count} of {expected_today}"
        else:
            if expected_today == 0:
                return f" 🔵휴일"
            else:
                return f" {colors['all_old']}{expected_today}개 대기"
    
    def get_expected_news_count_today(self):
        """
        오늘 요일에 예상되는 뉴스 수 계산
        
        NEWS_TYPES 설정의 publish_days를 기반으로 
        오늘 요일에 발행 예상되는 뉴스 개수를 계산합니다.
        
        Returns:
            int: 예상 뉴스 개수
        """
        today_info = self._get_today_info()
        expected_count = 0
        
        for news_type, config in NEWS_TYPES.items():
            if today_info['weekday'] in config.get('publish_days', []):
                expected_count += 1
        
        return expected_count
    
    def get_weekday_display(self):
        """
        현재 요일을 한글로 반환
        
        Returns:
            str: 요일 문자열 ('월', '화', '수', '목', '금', '토', '일')
        """
        return self._get_today_info()['weekday_name']
    
    def detect_changes(self, old_data, new_data):
        """
        이전 데이터와 현재 데이터 간의 변경사항 감지
        
        Args:
            old_data (dict): 이전 뉴스 데이터
            new_data (dict): 현재 뉴스 데이터
            
        Returns:
            dict: 변경사항 정보
                  - type: "new", "update", "none"
                  - changes: 변경된 뉴스 타입 리스트
        """
        if not old_data:
            return {"type": "new", "changes": []}
        
        changes = []
        for news_type in new_data:
            if news_type not in old_data:
                changes.append(news_type)
            else:
                old_item = old_data[news_type]
                new_item = new_data[news_type]
                
                if (old_item.get('title') != new_item.get('title') or 
                    old_item.get('content') != new_item.get('content') or
                    old_item.get('date') != new_item.get('date') or 
                    old_item.get('time') != new_item.get('time')):
                    changes.append(news_type)
        
        return {
            "type": "update" if changes else "none",
            "changes": changes
        }
    
    def get_previous_day_data(self, api_client, current_data, max_retry_days=10):
        """
        직전 영업일 데이터 조회
        
        현재 데이터와 비교할 직전 영업일 데이터를 조회합니다.
        주말과 공휴일을 고려하여 실제 영업일을 찾습니다.
        
        Args:
            api_client: API 클라이언트 인스턴스
            current_data (dict): 현재 뉴스 데이터
            max_retry_days (int): 최대 조회 시도 일수
            
        Returns:
            dict: 직전 영업일 뉴스 데이터
        """
        today = datetime.now()
        
        for i in range(1, max_retry_days + 1):
            check_date = today - timedelta(days=i)
            check_date_str = check_date.strftime('%Y%m%d')
            
            # 주말 제외 (토요일=5, 일요일=6)
            if check_date.weekday() >= 5:
                continue
            
            # 해당 날짜 데이터 조회
            previous_data = api_client.get_news_data(check_date_str)
            
            if previous_data:
                # 데이터가 있는지 확인
                has_data = False
                for news_type, news_data in previous_data.items():
                    if news_data.get('date') == check_date_str:
                        has_data = True
                        break
                
                if has_data:
                    return previous_data
        
        return None
    
    def format_datetime(self, date_str, time_str):
        """
        날짜와 시간을 포맷팅
        
        Args:
            date_str (str): 날짜 문자열 (YYYYMMDD)
            time_str (str): 시간 문자열 (HHMMSS)
            
        Returns:
            str: 포맷팅된 날짜시간 문자열
        """
        if not date_str:
            return "날짜 없음"
        
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        if not time_str:
            return formatted_date
        
        if len(time_str) >= 6:
            formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
        elif len(time_str) == 5:
            if time_str.startswith('6'):
                time_str = '0' + time_str
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            else:
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:5]}"
        elif len(time_str) >= 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:4]}"
        else:
            formatted_time = time_str
        
        return f"{formatted_date} {formatted_time}"