#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Business Day Helper
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import system_functionality_verification.py
from datetime import datetime, timedelta
import test_config.json

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(current_dir))

try:
from core import posco_news_250808_monitor.log News 250808APIClient
    from .git/config import .git/config
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")

class BusinessDayHelper:
    """
    영업일 계산 및 데이터 조회 헬퍼 클래스
    """
    
    def __init__(self):
        """
        영업일 헬퍼 초기화
        """
        self.api_client = POSCO News 250808APIClient(API_CONFIG)
        
        # 한국 공휴일 (간단한 버전 - 필요시 확장)
        self.holidays = {
            '2025-01-01',  # 신정
            '2025-01-28', '2025-01-29', '2025-01-30',  # 설날
            '2025-03-01',  # 삼일절
            '2025-05-05',  # 어린이날
            '2025-05-13',  # 부처님오신날
            '2025-06-06',  # 현충일
            '2025-08-15',  # 광복절
            '2025-09-16', '2025-09-17', '2025-09-18',  # 추석
            '2025-10-03',  # 개천절
            '2025-10-09',  # 한글날
            '2025-12-25',  # 크리스마스
        }
    
    def is_business_day(self, date):
        """
        영업일 여부 확인
        
        Args:
            date (datetime): 확인할 날짜
            
        Returns:
            bool: 영업일 여부
        """
#_주말_체크_(토요일 = 5, 일요일=6)
        if date.weekday() >= 5:
            return False
        
        # 공휴일 체크
        date_str = date.strftime('%Y-%m-%d')
        if date_str in self.holidays:
            return False
        
        return True
    
    def get_previous_business_day(self, from_date=None):
        """
        직전 영업일 조회
        
        Args:
            from_date (datetime, optional): 기준 날짜 (기본값: 오늘)
            
        Returns:
            datetime: 직전 영업일
        """
        if from_date is None:
            from_date = datetime.now()
        
        # 하루씩 거슬러 올라가면서 영업일 찾기
        check_date = from_date - timedelta(days=1)
        
        while not self.is_business_day(check_date):
check_date_- =  timedelta(days=1)
            
            # 무한 루프 방지 (최대 10일)
            if (from_date - check_date).days > 10:
                break
        
        return check_date
    
    def get_news_data_for_date(self, target_date, news_types=None):
        """
        특정 날짜의 뉴스 데이터 조회
        
        Args:
            target_date (datetime): 조회할 날짜
            news_types (list, optional): 조회할 뉴스 타입 목록
            
        Returns:
            dict: 뉴스 타입별 데이터
        """
        if news_types is None:
            news_types = ['exchange-rate', 'kospi-close', 'newyork-market-watch']
        
        date_str = target_date.strftime('%Y%m%d')
        news_data = {}
        
        try:
            # API에서 해당 날짜 데이터 조회
            all_data = self.api_client.get_news_data(date_str)
            
            for news_type in news_types:
                if news_type in all_data:
                    type_data = all_data[news_type]
                    
                    # 해당 날짜 데이터 필터링
                    if isinstance(type_data, dict) and 'publish_time' in type_data:
                        publish_time = type_data.get('publish_time', '')
                        
                        # 날짜 매칭 (간단한 방식)
                        if date_str in str(publish_time) or self._is_same_date(type_data, target_date):
                            news_data[news_type] = type_data
                        else:
                            news_data[news_type] = None
                    else:
                        news_data[news_type] = None
                else:
                    news_data[news_type] = None
                    
        except Exception as e:
            print(f"❌ {target_date.strftime('%Y-%m-%d')} 데이터 조회 실패: {e}")
            for news_type in news_types:
                news_data[news_type] = None
        
        return news_data
    
    def _is_same_date(self, news_data, target_date):
        """
        뉴스 데이터가 목표 날짜와 같은지 확인
        
        Args:
            news_data (dict): 뉴스 데이터
            target_date (datetime): 목표 날짜
            
        Returns:
            bool: 같은 날짜 여부
        """
        try:
            # 뉴스 데이터에서 날짜 정보 추출 시도
            title = news_data.get('title', '')
            content = news_data.get('content', '')
            
            target_date_str = target_date.strftime('%Y-%m-%d')
            target_date_str2 = target_date.strftime('%m-%d')
            target_date_str3 = target_date.strftime('%m월 %d일')
            
            # 제목이나 내용에 날짜가 포함되어 있는지 확인
            if any(date_str in title or date_str in content 
                   for date_str in [target_date_str, target_date_str2, target_date_str3]):
                return True
                
        except Exception:
            pass
        
        return False
    
    def get_complete_news_data(self, max_days_back=5):
        """
        완전한 3개 뉴스 데이터를 찾을 때까지 과거로 거슬러 올라가며 조회
        
        Args:
            max_days_back (int): 최대 몇 일 전까지 조회할지
            
        Returns:
            dict: {
                'date': datetime,
                'news_data': {news_type: data},
                'completion_rate': int,
                'is_current_day': bool
            }
        """
        current_date = datetime.now()
        
        for days_back in range(max_days_back + 1):
            if days_back == 0:
                check_date = current_date
                is_current = True
            else:
                check_date = self.get_previous_business_day(current_date - timedelta(days=days_back-1))
                is_current = False
            
            print(f"📅 {check_date.strftime('%Y-%m-%d')} 데이터 조회 중...")
            
            news_data = self.get_news_data_for_date(check_date)
            completed_count = sum(1 for data in news_data.values() if data and data.get('title'))
            
            print(f"   완료율: {completed_count}/3")
            
            # 3개 모두 완료되었거나, 현재일이고 2개 이상 완료된 경우
            if completed_count == 3 or (is_current and completed_count >= 2):
                return {
                    'date': check_date,
                    'news_data': news_data,
                    'completion_rate': completed_count,
                    'is_current_day': is_current
                }
        
        # 완전한 데이터를 찾지 못한 경우 현재 데이터 반환
        print("⚠️ 완전한 데이터를 찾지 못했습니다. 현재 데이터를 사용합니다.")
        current_news_data = self.get_news_data_for_date(current_date)
        current_completed = sum(1 for data in current_news_data.values() if data and data.get('title'))
        
        return {
            'date': current_date,
            'news_data': current_news_data,
            'completion_rate': current_completed,
            'is_current_day': True
        }

if __name__ == "__main__":
    # 테스트 실행
    helper = BusinessDayHelper()
    
    print("📅 영업일 헬퍼 테스트")
    print("=" * 50)
    
    # 직전 영업일 조회
    prev_business_day = helper.get_previous_business_day()
    print(f"직전 영업일: {prev_business_day.strftime('%Y-%m-%d (%A)')}")
    
    # 완전한 뉴스 데이터 조회
    complete_data = helper.get_complete_news_data()
    print(f"/n완전한 데이터 날짜: {complete_data['date'].strftime('%Y-%m-%d')}")
    print(f"완료율: {complete_data['completion_rate']}/3")
    print(f"현재일 여부: {complete_data['is_current_day']}")