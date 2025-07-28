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
        
        # 예상 뉴스 수 기준으로 상태 판단
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
            str: 요일 문자열
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
            return {"type": "new", "changes": list(new_data.keys()) if new_data else []}
        
        changes = []
        for news_type in new_data:
            if news_type not in old_data:
                changes.append(news_type)
            else:
                old_item = old_data[news_type]
                new_item = new_data[news_type]
                
                # 주요 필드 변경 확인
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
        
        Args:
            api_client: API 클라이언트 인스턴스
            current_data (dict): 현재 뉴스 데이터
            max_retry_days (int): 최대 검색 일수
            
        Returns:
            dict: 뉴스 타입별 직전 영업일 데이터
        """
        previous_data = {}
        
        for news_type, news_data in current_data.items():
            current_date = news_data.get('date', '')
            current_title = news_data.get('title', '')
            
            if not current_date or not current_title:
                print(f"📅 {news_type}: 현재 데이터 없음")
                previous_data[news_type] = None
                continue
            
            print(f"📅 {news_type}: 직전 영업일 데이터 검색 중...")
            
            # 최대 설정된 일수까지 역순으로 검색
            found_different_data = False
            for days_back in range(1, max_retry_days + 1):
                try:
                    check_date_obj = datetime.strptime(current_date, "%Y%m%d") - timedelta(days=days_back)
                    check_date = check_date_obj.strftime("%Y%m%d")
                    
                    prev_api_data = api_client.get_news_data(date=check_date)
                    
                    if prev_api_data and news_type in prev_api_data:
                        prev_item = prev_api_data[news_type]
                        prev_title = prev_item.get('title', '')
                        prev_date = prev_item.get('date', '')
                        
                        # 실제 다른 데이터인지 확인
                        if prev_title and (prev_title != current_title or prev_date != current_date):
                            previous_data[news_type] = prev_item
                            print(f"📅 {news_type}: 직전 데이터 발견 ({days_back}일 전)")
                            found_different_data = True
                            break
                        
                except Exception as e:
                    print(f"❌ {news_type}: {days_back}일 전 데이터 조회 오류 - {e}")
                    continue
            
            if not found_different_data:
                print(f"📅 {news_type}: {max_retry_days}일 내 직전 데이터를 찾을 수 없음")
                previous_data[news_type] = None
        
        return previous_data