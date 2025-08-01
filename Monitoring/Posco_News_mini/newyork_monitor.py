#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 - 뉴욕마켓워치 전용 모니터링 🌆

뉴욕마켓워치 뉴스를 전문적으로 모니터링하는 시스템 (최적화 버전)

주요 기능:
- BaseNewsMonitor 상속으로 코드 중복 제거
- 5자리 시간 형식 전용 처리 (61831 → 06:18:31)
- 설정 기반 동작으로 유지보수성 향상

작성자: AI Assistant
최종 수정: 2025-07-30 (최적화)
"""

import sys
import os
import argparse
from datetime import datetime

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from base_monitor import BaseNewsMonitor
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class NewYorkMarketMonitor(BaseNewsMonitor):
    """
    뉴욕마켓워치 뉴스 전용 모니터링 클래스 (최적화 버전)
    
    BaseNewsMonitor를 상속받아 뉴욕마켓워치 특수 처리만 구현합니다.
    """
    
    def __init__(self):
        """뉴욕마켓워치 모니터 초기화"""
        super().__init__("newyork-market-watch")
    
    def parse_ny_time(self, time_str):
        """
        뉴욕마켓워치 5자리 시간 형식 파싱
        
        Args:
            time_str (str): 5자리 시간 문자열 (예: "61831")
            
        Returns:
            tuple: (hour, minute, second) 또는 None
        """
        if not time_str:
            return None
        
        try:
            # 5자리 형식: 61831 → 06:18:31 (첫 자리는 시간의 한 자리, 0이 생략됨)
            if len(time_str) == 5:
                hour = int(time_str[0])  # 첫 번째 자리 (0-9, 실제로는 06시의 6)
                minute = int(time_str[1:3])  # 2-3번째 자리
                second = int(time_str[3:5])  # 4-5번째 자리
                
                # 시간 유효성 검사 (5자리 형식에서는 시간이 0-9만 가능)
                if 0 <= hour <= 9 and 0 <= minute <= 59 and 0 <= second <= 59:
                    return (hour, minute, second)
            
            # 6자리 형식: 061831 → 06:18:31
            elif len(time_str) == 6:
                hour = int(time_str[:2])
                minute = int(time_str[2:4])
                second = int(time_str[4:6])
                
                if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                    return (hour, minute, second)
            
            # 4자리 형식: 0618 → 06:18:00
            elif len(time_str) == 4:
                hour = int(time_str[:2])
                minute = int(time_str[2:4])
                second = 0
                
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return (hour, minute, second)
            
            return None
            
        except (ValueError, IndexError):
            return None
    
    def format_ny_time(self, time_str):
        """
        뉴욕마켓워치 시간 포맷팅
        
        Args:
            time_str (str): 원본 시간 문자열
            
        Returns:
            str: 포맷팅된 시간 문자열
        """
        parsed_time = self.parse_ny_time(time_str)
        if parsed_time:
            hour, minute, second = parsed_time
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        else:
            return f"시간오류({time_str})"
    
    def get_current_news_data(self):
        """
        현재 뉴욕마켓워치 뉴스 데이터 조회
        
        Returns:
            dict: 뉴욕마켓워치 뉴스 데이터 또는 None
        """
        try:
            current_data = self.api_client.get_news_data()
            if current_data and self.news_type in current_data:
                return current_data[self.news_type]
            return None
        except Exception as e:
            print(f"❌ 뉴욕마켓워치 데이터 조회 실패: {e}")
            return None
    
    def analyze_publish_pattern(self, ny_data):
        """
        뉴욕마켓워치 뉴스 발행 패턴 분석
        
        Args:
            ny_data (dict): 뉴욕마켓워치 뉴스 데이터
            
        Returns:
            dict: 발행 패턴 분석 결과
        """
        if not ny_data:
            return {
                'status': 'no_data',
                'is_published_today': False,
                'is_on_time': False,
                'delay_minutes': 0,
                'analysis': '데이터 없음'
            }
        
        today_date = datetime.now().strftime('%Y%m%d')
        news_date = ny_data.get('date', '')
        news_time = ny_data.get('time', '')
        
        is_published_today = (news_date == today_date)
        
        if not is_published_today:
            return {
                'status': 'not_published',
                'is_published_today': False,
                'is_on_time': False,
                'delay_minutes': 0,
                'analysis': f'오늘 발행되지 않음 (최신: {news_date})'
            }
        
        # 발행 시간 분석
        parsed_time = self.parse_ny_time(news_time)
        if not parsed_time:
            return {
                'status': 'published_no_time',
                'is_published_today': True,
                'is_on_time': False,
                'delay_minutes': 0,
                'analysis': f'발행됨 (시간 파싱 실패: {news_time})',
                'formatted_time': f'시간오류({news_time})'
            }
        
        hour, minute, second = parsed_time
        
        # 예상 발행 시간과 비교 (06:00-07:00 범위)
        expected_start = 6 * 60  # 06:00 in minutes
        expected_end = 7 * 60    # 07:00 in minutes
        actual_minutes = hour * 60 + minute
        
        # 정시 발행 여부 판단 (06:00-07:00 범위 내)
        is_on_time = expected_start <= actual_minutes <= expected_end
        
        # 지연 시간 계산 (07:00 기준)
        delay_minutes = actual_minutes - expected_end if actual_minutes > expected_end else 0
        
        if is_on_time:
            status = 'on_time'
            analysis = f'정시 발행 ({hour:02d}:{minute:02d})'
        elif actual_minutes < expected_start:
            status = 'early'
            early_minutes = expected_start - actual_minutes
            analysis = f'{early_minutes}분 조기 발행 ({hour:02d}:{minute:02d})'
        else:
            status = 'delayed'
            analysis = f'{delay_minutes}분 지연 발행 ({hour:02d}:{minute:02d})'
        
        return {
            'status': status,
            'is_published_today': True,
            'is_on_time': is_on_time,
            'delay_minutes': delay_minutes,
            'analysis': analysis,
            'expected_time': '06:00-07:00',
            'actual_time': f'{hour:02d}:{minute:02d}',
            'formatted_time': self.format_ny_time(news_time)
        }
    
    def _format_news_datetime(self, date, time, pattern_analysis):
        """
        뉴욕마켓워치 전용 날짜시간 포맷팅
        
        Args:
            date (str): 날짜 문자열
            time (str): 시간 문자열
            pattern_analysis (dict): 패턴 분석 결과
            
        Returns:
            str: 포맷팅된 날짜시간
        """
        if not date:
            return "날짜 정보 없음"
        
        formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        formatted_time = pattern_analysis.get('formatted_time', self.format_ny_time(time))
        
        return f"{formatted_date} {formatted_time}"

    def send_test_notification(self):
        """테스트 알림 전송"""
        print("🧪 뉴욕마켓워치 테스트 알림 전송 중...")
        test_message = f"🧪 뉴욕마켓워치 테스트\n\n📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ 시스템 정상 작동 중"
        
        try:
            success = self.notifier.send_notification(test_message, is_error=False)
            if success:
                print("✅ 뉴욕마켓워치 테스트 알림 전송 성공")
            else:
                print("❌ 뉴욕마켓워치 테스트 알림 전송 실패")
        except Exception as e:
            print(f"❌ 뉴욕마켓워치 테스트 알림 전송 오류: {e}")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='뉴욕마켓워치 뉴스 전용 모니터링')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='실행 모드: single(단일 확인) 또는 continuous(연속 모니터링)')
    parser.add_argument('--interval', type=int, default=300,
                       help='연속 모니터링 간격 (초, 기본값: 300)')
    
    args = parser.parse_args()
    
    # 뉴욕마켓워치 모니터 초기화
    monitor = NewYorkMarketMonitor()
    
    if args.mode == 'single':
        monitor.run_single_check()
    else:
        monitor.run_continuous_monitoring(args.interval)

if __name__ == "__main__":
    main()