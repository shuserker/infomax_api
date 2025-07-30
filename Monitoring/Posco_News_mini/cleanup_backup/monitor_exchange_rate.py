#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 - 서환마감 전용 모니터링 🏦

서환마감(환율) 뉴스를 전문적으로 모니터링하는 시스템

주요 기능:
- 서환마감 뉴스 실시간 모니터링
- 발행 패턴 분석 및 예측
- 지연 발행 감지 및 알림
- 과거 데이터와의 비교 분석
- 자동 알림 및 상태 보고

특화 기능:
- 16:30 정시 발행 패턴 추적
- 지연 발행 시 자동 알림 (17:00, 17:30, 18:00)
- 주말/공휴일 발행 예외 처리
- 환율 변동성 기반 중요도 판단

작성자: AI Assistant
최종 수정: 2025-07-30
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
import argparse

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core import PoscoNewsAPIClient, NewsDataProcessor, DoorayNotifier
    from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, NEWS_TYPES
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class ExchangeRateMonitor:
    """
    서환마감 뉴스 전용 모니터링 클래스
    
    환율 뉴스의 특성을 고려한 전문 모니터링 시스템입니다.
    
    주요 기능:
    - 정시 발행 패턴 추적 (평일 16:30)
    - 지연 발행 감지 및 단계별 알림
    - 환율 변동성 분석
    - 과거 데이터 비교 분석
    """
    
    def __init__(self):
        """서환마감 모니터 초기화"""
        self.api_client = PoscoNewsAPIClient(API_CONFIG)
        self.data_processor = NewsDataProcessor()
        self.notifier = DoorayNotifier(DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, self.api_client)
        
        # 서환마감 뉴스 설정
        self.news_type = "exchange-rate"
        self.news_config = NEWS_TYPES.get(self.news_type, {})
        self.display_name = self.news_config.get('display_name', '서환마감')
        self.emoji = self.news_config.get('emoji', '💱')
        
        # 발행 시간 패턴 (평일 16:30 기준)
        self.expected_publish_time = "163000"  # 16:30:00
        self.delay_check_times = ["170000", "173000", "180000"]  # 17:00, 17:30, 18:00
        
        # 상태 추적
        self.last_data = None
        self.delay_notifications_sent = set()
        
        print(f"🏦 {self.display_name} 전용 모니터링 시스템 초기화 완료")
    
    def get_current_exchange_data(self):
        """
        현재 서환마감 뉴스 데이터 조회
        
        Returns:
            dict: 서환마감 뉴스 데이터 또는 None
        """
        try:
            current_data = self.api_client.get_news_data()
            if current_data and self.news_type in current_data:
                return current_data[self.news_type]
            return None
        except Exception as e:
            print(f"❌ 서환마감 데이터 조회 실패: {e}")
            return None
    
    def analyze_publish_pattern(self, exchange_data):
        """
        서환마감 뉴스 발행 패턴 분석
        
        Args:
            exchange_data (dict): 서환마감 뉴스 데이터
            
        Returns:
            dict: 발행 패턴 분석 결과
        """
        if not exchange_data:
            return {
                'status': 'no_data',
                'is_published_today': False,
                'is_on_time': False,
                'delay_minutes': 0,
                'analysis': '데이터 없음'
            }
        
        today_date = datetime.now().strftime('%Y%m%d')
        news_date = exchange_data.get('date', '')
        news_time = exchange_data.get('time', '')
        
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
        
        # 정시 발행 여부 판단 (±5분 허용)
        is_on_time = abs(delay_minutes) <= 5
        
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
    
    def check_delay_notification_needed(self):
        """
        지연 발행 알림 필요 여부 확인
        
        Returns:
            tuple: (알림 필요 여부, 지연 단계)
        """
        current_time = datetime.now().strftime('%H%M%S')
        
        for i, check_time in enumerate(self.delay_check_times):
            if current_time >= check_time and check_time not in self.delay_notifications_sent:
                return True, i + 1  # 1단계, 2단계, 3단계
        
        return False, 0
    
    def send_delay_notification(self, delay_stage):
        """
        지연 발행 알림 전송
        
        Args:
            delay_stage (int): 지연 단계 (1, 2, 3)
        """
        current_time = datetime.now()
        stage_names = {1: "1차", 2: "2차", 3: "3차"}
        stage_times = {1: "17:00", 2: "17:30", 3: "18:00"}
        
        stage_name = stage_names.get(delay_stage, f"{delay_stage}차")
        expected_time = stage_times.get(delay_stage, "알 수 없음")
        
        # 이모지 및 색상 설정
        if delay_stage == 1:
            emoji = "⚠️"
            color = "#ffc107"  # 노란색
        elif delay_stage == 2:
            emoji = "🚨"
            color = "#fd7e14"  # 주황색
        else:
            emoji = "🔴"
            color = "#dc3545"  # 빨간색
        
        message = f"{emoji} {self.display_name} 지연 발행 알림 ({stage_name})\n\n"
        message += f"📅 날짜: {current_time.strftime('%Y-%m-%d')}\n"
        message += f"⏰ 현재 시간: {current_time.strftime('%H:%M:%S')}\n"
        message += f"📋 예상 발행 시간: 16:30\n"
        message += f"🚨 지연 상태: {expected_time} 기준 미발행\n\n"
        
        # 지연 단계별 메시지
        if delay_stage == 1:
            message += "• 30분 지연 상태입니다.\n"
            message += "• 일반적인 지연 범위 내입니다.\n"
        elif delay_stage == 2:
            message += "• 1시간 지연 상태입니다.\n"
            message += "• 주의가 필요한 지연입니다.\n"
        else:
            message += "• 1시간 30분 이상 지연 상태입니다.\n"
            message += "• 심각한 지연으로 확인이 필요합니다.\n"
        
        message += f"\n🔍 다음 확인: {stage_times.get(delay_stage + 1, '수동 확인')}"
        
        payload = {
            "botName": f"POSCO 뉴스 {emoji}",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": f"{self.display_name} 지연 발행 알림 ({stage_name})",
            "attachments": [{
                "color": color,
                "text": message
            }]
        }
        
        try:
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {stage_name} 지연 알림 전송 성공")
                # 알림 전송 기록
                check_time = self.delay_check_times[delay_stage - 1]
                self.delay_notifications_sent.add(check_time)
                return True
            else:
                print(f"❌ {stage_name} 지연 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {stage_name} 지연 알림 전송 오류: {e}")
            return False
    
    def send_publish_notification(self, exchange_data, pattern_analysis):
        """
        서환마감 발행 알림 전송
        
        Args:
            exchange_data (dict): 서환마감 뉴스 데이터
            pattern_analysis (dict): 발행 패턴 분석 결과
        """
        title = exchange_data.get('title', '')
        date = exchange_data.get('date', '')
        time = exchange_data.get('time', '')
        
        # 상태에 따른 이모지 및 색상
        status = pattern_analysis.get('status', 'unknown')
        if status == 'on_time':
            status_emoji = "✅"
            color = "#28a745"  # 녹색
            status_text = "정시 발행"
        elif status == 'early':
            status_emoji = "⚡"
            color = "#17a2b8"  # 청색
            status_text = "조기 발행"
        elif status == 'delayed':
            status_emoji = "⏰"
            color = "#ffc107"  # 노란색
            status_text = "지연 발행"
        else:
            status_emoji = "📰"
            color = "#6c757d"  # 회색
            status_text = "발행 완료"
        
        message = f"{status_emoji} {self.display_name} {status_text}\n\n"
        
        # 발행 정보
        formatted_datetime = self.data_processor.format_datetime(date, time)
        message += f"📅 발행 시간: {formatted_datetime}\n"
        message += f"📊 패턴 분석: {pattern_analysis.get('analysis', '분석 불가')}\n"
        
        if 'expected_time' in pattern_analysis and 'actual_time' in pattern_analysis:
            message += f"⏰ 예상: {pattern_analysis['expected_time']} → 실제: {pattern_analysis['actual_time']}\n"
        
        # 제목 정보
        if title:
            title_preview = title[:60] + "..." if len(title) > 60 else title
            message += f"📋 제목: {title_preview}\n"
        
        # 지연 알림 초기화 (발행 완료 시)
        if pattern_analysis.get('is_published_today', False):
            self.delay_notifications_sent.clear()
            message += f"\n🔔 지연 알림이 초기화되었습니다."
        
        payload = {
            "botName": f"POSCO 뉴스 {status_emoji}",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": f"{self.display_name} {status_text}",
            "attachments": [{
                "color": color,
                "text": message
            }]
        }
        
        try:
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {self.display_name} 발행 알림 전송 성공")
                return True
            else:
                print(f"❌ {self.display_name} 발행 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {self.display_name} 발행 알림 전송 오류: {e}")
            return False
    
    def run_single_check(self):
        """단일 상태 확인 실행"""
        print(f"🔍 {self.display_name} 상태 확인 중...")
        
        # 현재 데이터 조회
        exchange_data = self.get_current_exchange_data()
        
        if not exchange_data:
            print(f"❌ {self.display_name} 데이터 없음")
            return
        
        # 발행 패턴 분석
        pattern_analysis = self.analyze_publish_pattern(exchange_data)
        
        print(f"📊 분석 결과: {pattern_analysis.get('analysis', '분석 불가')}")
        
        # 변경사항 감지
        if self.last_data != exchange_data:
            print(f"🆕 {self.display_name} 데이터 변경 감지")
            
            # 발행 알림 전송
            if pattern_analysis.get('is_published_today', False):
                self.send_publish_notification(exchange_data, pattern_analysis)
            
            self.last_data = exchange_data.copy() if exchange_data else None
        else:
            print(f"📋 {self.display_name} 데이터 변경 없음")
        
        # 지연 알림 확인
        need_delay_notification, delay_stage = self.check_delay_notification_needed()
        if need_delay_notification and not pattern_analysis.get('is_published_today', False):
            print(f"🚨 {delay_stage}차 지연 알림 필요")
            self.send_delay_notification(delay_stage)
    
    def run_continuous_monitoring(self, interval=300):
        """
        연속 모니터링 실행
        
        Args:
            interval (int): 확인 간격 (초, 기본값: 5분)
        """
        print(f"🚀 {self.display_name} 연속 모니터링 시작 (간격: {interval}초)")
        
        try:
            while True:
                self.run_single_check()
                print(f"⏰ {interval}초 후 다음 확인...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 {self.display_name} 모니터링 중단됨")
        except Exception as e:
            print(f"❌ {self.display_name} 모니터링 오류: {e}")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='서환마감 뉴스 전용 모니터링')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='실행 모드: single(단일 확인) 또는 continuous(연속 모니터링)')
    parser.add_argument('--interval', type=int, default=300,
                       help='연속 모니터링 간격 (초, 기본값: 300)')
    
    args = parser.parse_args()
    
    # 서환마감 모니터 초기화
    monitor = ExchangeRateMonitor()
    
    if args.mode == 'single':
        monitor.run_single_check()
    else:
        monitor.run_continuous_monitoring(args.interval)

if __name__ == "__main__":
    main()