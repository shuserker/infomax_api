#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 - 증시마감 전용 모니터링 📈

증시마감(KOSPI) 뉴스를 전문적으로 모니터링하는 시스템 (최적화 버전)

주요 기능:
- BaseNewsMonitor 상속으로 코드 중복 제거
- 표준 6자리 시간 형식 처리
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

class KospiCloseMonitor(BaseNewsMonitor):
    """
    증시마감 뉴스 전용 모니터링 클래스 (최적화 버전)
    
    BaseNewsMonitor를 상속받아 증시마감 특수 처리만 구현합니다.
    """
    
    def __init__(self):
        """증시마감 모니터 초기화"""
        super().__init__("kospi-close")
    
    def get_current_news_data(self):
        """
        현재 증시마감 뉴스 데이터 조회
        
        Returns:
            dict: 증시마감 뉴스 데이터 또는 None
        """
        try:
            current_data = self.api_client.get_news_data()
            if current_data and self.news_type in current_data:
                return current_data[self.news_type]
            return None
        except Exception as e:
            print(f"❌ 증시마감 데이터 조회 실패: {e}")
            return None
    
    def analyze_publish_pattern(self, kospi_data):
        """
        증시마감 뉴스 발행 패턴 분석
        
        Args:
            kospi_data (dict): 증시마감 뉴스 데이터
            
        Returns:
            dict: 발행 패턴 분석 결과
        """
        if not kospi_data:
            return {
                'status': 'no_data',
                'is_published_today': False,
                'is_on_time': False,
                'delay_minutes': 0,
                'analysis': '데이터 없음'
            }
        
        today_date = datetime.now().strftime('%Y%m%d')
        news_date = kospi_data.get('date', '')
        news_time = kospi_data.get('time', '')
        
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
        if not news_time or len(news_time) < 6:
            return {
                'status': 'published_no_time',
                'is_published_today': True,
                'is_on_time': False,
                'delay_minutes': 0,
                'analysis': '발행됨 (시간 정보 없음)'
            }
        
        # 예상 발행 시간과 비교
        expected_time = datetime.strptime(self.expected_publish_time, '%H%M%S').time()
        actual_time = datetime.strptime(news_time[:6], '%H%M%S').time()
        
        # 시간 차이 계산 (분 단위)
        expected_datetime = datetime.combine(datetime.now().date(), expected_time)
        actual_datetime = datetime.combine(datetime.now().date(), actual_time)
        delay_minutes = int((actual_datetime - expected_datetime).total_seconds() / 60)
        
        # 정시 발행 여부 판단 (±10분 허용, 증시마감은 변동성이 큼)
        is_on_time = abs(delay_minutes) <= self.tolerance_minutes
        
        if is_on_time:
            status = 'on_time'
            analysis = f'정시 발행 ({actual_time.strftime("%H:%M")})'
        elif delay_minutes > 0:
            status = 'delayed'
            analysis = f'{delay_minutes}분 지연 발행 ({actual_time.strftime("%H:%M")})'
        else:
            status = 'early'
            analysis = f'{abs(delay_minutes)}분 조기 발행 ({actual_time.strftime("%H:%M")})'
        
        return {
            'status': status,
            'is_published_today': True,
            'is_on_time': is_on_time,
            'delay_minutes': delay_minutes,
            'analysis': analysis,
            'expected_time': expected_time.strftime('%H:%M'),
            'actual_time': actual_time.strftime('%H:%M')
        }

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='증시마감 뉴스 전용 모니터링')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='실행 모드: single(단일 확인) 또는 continuous(연속 모니터링)')
    parser.add_argument('--interval', type=int, default=300,
                       help='연속 모니터링 간격 (초, 기본값: 300)')
    
    args = parser.parse_args()
    
    # 증시마감 모니터 초기화
    monitor = KospiCloseMonitor()
    
    if args.mode == 'single':
        monitor.run_single_check()
    else:
        monitor.run_continuous_monitoring(args.interval)

if __name__ == "__main__":
    main()