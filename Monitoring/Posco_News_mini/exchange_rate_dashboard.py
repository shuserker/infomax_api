#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서환마감 뉴스 분석 대시보드 📊

서환마감 뉴스의 발행 패턴, 지연 현황, 과거 데이터를 분석하여
시각적으로 표시하는 대시보드

주요 기능:
- 실시간 발행 상태 표시
- 발행 시간 패턴 분석
- 지연 발행 통계
- 주간/월간 발행 현황
- 환율 변동성 분석

실행 방법:
python exchange_rate_dashboard.py

작성자: AI Assistant
최종 수정: 2025-07-30
"""

import sys
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core import PoscoNewsAPIClient, NewsDataProcessor
    from config import API_CONFIG, NEWS_TYPES
    from monitor_exchange_rate import ExchangeRateMonitor
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class ExchangeRateDashboard:
    """
    서환마감 뉴스 분석 대시보드 클래스
    
    서환마감 뉴스의 다양한 통계와 분석 정보를 제공합니다.
    """
    
    def __init__(self):
        """대시보드 초기화"""
        self.api_client = PoscoNewsAPIClient(API_CONFIG)
        self.data_processor = NewsDataProcessor()
        self.monitor = ExchangeRateMonitor()
        
        self.news_type = "exchange-rate"
        self.display_name = "서환마감"
        
        print(f"📊 {self.display_name} 분석 대시보드 초기화 완료")
    
    def get_current_status(self):
        """현재 서환마감 상태 조회"""
        print(f"\n🔍 {self.display_name} 현재 상태")
        print("=" * 40)
        
        # 현재 데이터 조회
        exchange_data = self.monitor.get_current_exchange_data()
        
        if not exchange_data:
            print("❌ 데이터 없음")
            return
        
        # 기본 정보 표시
        date = exchange_data.get('date', '없음')
        time = exchange_data.get('time', '없음')
        title = exchange_data.get('title', '없음')
        
        print(f"📅 날짜: {date}")
        print(f"⏰ 시간: {time}")
        print(f"📋 제목: {title[:60]}{'...' if len(title) > 60 else ''}")
        
        # 발행 패턴 분석
        pattern_analysis = self.monitor.analyze_publish_pattern(exchange_data)
        print(f"📊 상태: {pattern_analysis.get('analysis', '분석 불가')}")
        
        if pattern_analysis.get('is_published_today', False):
            print(f"✅ 오늘 발행: 완료")
            if 'expected_time' in pattern_analysis and 'actual_time' in pattern_analysis:
                print(f"⏰ 예상 시간: {pattern_analysis['expected_time']}")
                print(f"⏰ 실제 시간: {pattern_analysis['actual_time']}")
                
                delay_minutes = pattern_analysis.get('delay_minutes', 0)
                if delay_minutes > 0:
                    print(f"⏳ 지연: {delay_minutes}분")
                elif delay_minutes < 0:
                    print(f"⚡ 조기: {abs(delay_minutes)}분")
                else:
                    print(f"✅ 정시: 정확한 발행")
        else:
            print(f"❌ 오늘 발행: 미완료")
            
            # 현재 시간 기준 지연 상태 확인
            current_time = datetime.now()
            if current_time.hour >= 16:  # 16시 이후
                expected_time = current_time.replace(hour=16, minute=30, second=0, microsecond=0)
                delay_minutes = int((current_time - expected_time).total_seconds() / 60)
                if delay_minutes > 0:
                    print(f"⏳ 현재 지연: {delay_minutes}분")
    
    def analyze_weekly_pattern(self):
        """주간 발행 패턴 분석"""
        print(f"\n📈 {self.display_name} 주간 발행 패턴")
        print("=" * 40)
        
        # 최근 7일간 데이터 수집
        today = datetime.now()
        weekly_data = []
        
        for i in range(7):
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime('%Y%m%d')
            
            # 주말 제외
            if check_date.weekday() >= 5:
                continue
            
            try:
                data = self.api_client.get_news_data(date_str)
                exchange_data = data.get(self.news_type, {}) if data else {}
                
                weekly_data.append({
                    'date': check_date,
                    'date_str': date_str,
                    'weekday': check_date.strftime('%A'),
                    'weekday_kr': ['월', '화', '수', '목', '금', '토', '일'][check_date.weekday()],
                    'data': exchange_data,
                    'published': bool(exchange_data.get('date') == date_str)
                })
            except:
                weekly_data.append({
                    'date': check_date,
                    'date_str': date_str,
                    'weekday': check_date.strftime('%A'),
                    'weekday_kr': ['월', '화', '수', '목', '금', '토', '일'][check_date.weekday()],
                    'data': {},
                    'published': False
                })
        
        # 주간 통계 계산
        total_days = len(weekly_data)
        published_days = sum(1 for item in weekly_data if item['published'])
        publish_rate = (published_days / total_days * 100) if total_days > 0 else 0
        
        print(f"📊 주간 통계 (최근 {total_days}일)")
        print(f"   • 발행 완료: {published_days}일")
        print(f"   • 발행률: {publish_rate:.1f}%")
        print()
        
        # 일별 상세 정보
        print("📅 일별 발행 현황:")
        for item in reversed(weekly_data):  # 최신순으로 표시
            date_display = item['date'].strftime('%m/%d')
            weekday = item['weekday_kr']
            
            if item['published']:
                time_info = item['data'].get('time', '')
                if time_info and len(time_info) >= 4:
                    time_display = f"{time_info[:2]}:{time_info[2:4]}"
                else:
                    time_display = "시간정보없음"
                print(f"   {date_display}({weekday}): ✅ 발행완료 ({time_display})")
            else:
                print(f"   {date_display}({weekday}): ❌ 미발행")
    
    def analyze_publish_time_pattern(self):
        """발행 시간 패턴 분석"""
        print(f"\n⏰ {self.display_name} 발행 시간 패턴")
        print("=" * 40)
        
        # 최근 30일간 발행 시간 수집
        today = datetime.now()
        time_data = []
        
        for i in range(30):
            check_date = today - timedelta(days=i)
            
            # 주말 제외
            if check_date.weekday() >= 5:
                continue
            
            date_str = check_date.strftime('%Y%m%d')
            
            try:
                data = self.api_client.get_news_data(date_str)
                exchange_data = data.get(self.news_type, {}) if data else {}
                
                if exchange_data.get('date') == date_str:
                    time_str = exchange_data.get('time', '')
                    if time_str and len(time_str) >= 6:
                        time_data.append({
                            'date': check_date,
                            'time_str': time_str,
                            'hour': int(time_str[:2]),
                            'minute': int(time_str[2:4]),
                            'total_minutes': int(time_str[:2]) * 60 + int(time_str[2:4])
                        })
            except:
                continue
        
        if not time_data:
            print("❌ 분석할 발행 시간 데이터가 없습니다.")
            return
        
        # 시간 통계 계산
        total_count = len(time_data)
        hour_counter = Counter(item['hour'] for item in time_data)
        minute_counter = Counter(item['minute'] for item in time_data)
        
        # 평균 발행 시간 계산
        avg_minutes = sum(item['total_minutes'] for item in time_data) / total_count
        avg_hour = int(avg_minutes // 60)
        avg_minute = int(avg_minutes % 60)
        
        print(f"📊 발행 시간 통계 (최근 {total_count}일)")
        print(f"   • 평균 발행 시간: {avg_hour:02d}:{avg_minute:02d}")
        print()
        
        # 시간대별 발행 빈도
        print("📈 시간대별 발행 빈도:")
        for hour in sorted(hour_counter.keys()):
            count = hour_counter[hour]
            percentage = (count / total_count * 100)
            bar = "█" * int(percentage / 5)  # 5%당 1개 블록
            print(f"   {hour:02d}시: {count:2d}회 ({percentage:4.1f}%) {bar}")
        
        # 정시 발행 분석 (16:30 기준)
        on_time_count = sum(1 for item in time_data 
                           if 16 <= item['hour'] <= 16 and 25 <= item['minute'] <= 35)
        on_time_rate = (on_time_count / total_count * 100) if total_count > 0 else 0
        
        print()
        print(f"⏰ 정시 발행 분석 (16:25-16:35 범위):")
        print(f"   • 정시 발행: {on_time_count}회 ({on_time_rate:.1f}%)")
        print(f"   • 지연/조기: {total_count - on_time_count}회 ({100 - on_time_rate:.1f}%)")
    
    def show_today_timeline(self):
        """오늘의 서환마감 타임라인"""
        print(f"\n📅 오늘의 {self.display_name} 타임라인")
        print("=" * 40)
        
        current_time = datetime.now()
        today_str = current_time.strftime('%Y-%m-%d %A')
        
        print(f"📅 날짜: {today_str}")
        print(f"⏰ 현재 시간: {current_time.strftime('%H:%M:%S')}")
        print()
        
        # 주요 시간대 표시
        timeline_events = [
            ("16:00", "📢 서환마감 발행 예상 시간대 시작"),
            ("16:30", "🎯 정상 발행 예상 시간"),
            ("17:00", "⚠️ 1차 지연 알림 시점"),
            ("17:30", "🚨 2차 지연 알림 시점"),
            ("18:00", "🔴 3차 지연 알림 시점"),
            ("18:30", "📋 일반 모니터링 전환 시점")
        ]
        
        for time_str, description in timeline_events:
            event_time = datetime.strptime(time_str, "%H:%M").time()
            event_datetime = datetime.combine(current_time.date(), event_time)
            
            if current_time.time() > event_time:
                status = "✅ 완료"
            elif current_time.time() == event_time:
                status = "🔄 진행중"
            else:
                status = "⏳ 대기중"
            
            print(f"   {time_str}: {description} ({status})")
        
        # 현재 서환마감 상태
        exchange_data = self.monitor.get_current_exchange_data()
        pattern_analysis = self.monitor.analyze_publish_pattern(exchange_data)
        
        print()
        print(f"📊 현재 상태: {pattern_analysis.get('analysis', '분석 불가')}")
        
        if pattern_analysis.get('is_published_today', False):
            print("🎉 오늘 서환마감 뉴스가 발행되었습니다!")
        else:
            if current_time.hour >= 16:
                expected_time = current_time.replace(hour=16, minute=30, second=0, microsecond=0)
                if current_time > expected_time:
                    delay_minutes = int((current_time - expected_time).total_seconds() / 60)
                    print(f"⏳ 현재 {delay_minutes}분 지연 상태입니다.")
                else:
                    remaining_minutes = int((expected_time - current_time).total_seconds() / 60)
                    print(f"⏰ 발행까지 약 {remaining_minutes}분 남았습니다.")
            else:
                expected_time = current_time.replace(hour=16, minute=30, second=0, microsecond=0)
                remaining_minutes = int((expected_time - current_time).total_seconds() / 60)
                print(f"⏰ 발행까지 약 {remaining_minutes}분 남았습니다.")
    
    def show_full_dashboard(self):
        """전체 대시보드 표시"""
        print("🏦 서환마감 뉴스 분석 대시보드")
        print("=" * 50)
        print(f"📅 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 각 섹션 표시
        self.get_current_status()
        self.show_today_timeline()
        self.analyze_weekly_pattern()
        self.analyze_publish_time_pattern()
        
        print("\n" + "=" * 50)
        print("📊 대시보드 생성 완료")
        print("🔄 실시간 모니터링: python start_exchange_monitoring.py")
        print("📋 단일 확인: python monitor_exchange_rate.py --mode single")

def main():
    """메인 실행 함수"""
    dashboard = ExchangeRateDashboard()
    dashboard.show_full_dashboard()

if __name__ == "__main__":
    main()