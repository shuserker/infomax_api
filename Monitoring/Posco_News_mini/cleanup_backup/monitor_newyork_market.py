#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 - 뉴욕마켓워치 전용 모니터링 🌆

뉴욕마켓워치 뉴스를 전문적으로 모니터링하는 시스템

주요 기능:
- 뉴욕마켓워치 뉴스 실시간 모니터링
- 발행 패턴 분석 및 예측 (06:00-07:00 기준)
- 지연 발행 감지 및 알림
- 과거 데이터와의 비교 분석
- 자동 알림 및 상태 보고

특화 기능:
- 06:00-07:00 발행 패턴 추적
- 지연 발행 시 자동 알림 (07:30, 08:00, 08:30)
- 주말 발행 포함 (뉴욕 시장 특성)
- 5자리 시간 형식 처리 (61831 → 06:18:31)

작성자: AI Assistant
최종 수정: 2025-07-30
"""

import sys
import os
import time
import json
import requests
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

class NewYorkMarketMonitor:
    """
    뉴욕마켓워치 뉴스 전용 모니터링 클래스
    
    뉴욕마켓워치 뉴스의 특성을 고려한 전문 모니터링 시스템입니다.
    
    주요 기능:
    - 발행 패턴 추적 (06:00-07:00 시간대)
    - 지연 발행 감지 및 단계별 알림
    - 5자리 시간 형식 처리
    - 과거 데이터 비교 분석
    """
    
    def __init__(self):
        """뉴욕마켓워치 모니터 초기화"""
        self.api_client = PoscoNewsAPIClient(API_CONFIG)
        self.data_processor = NewsDataProcessor()
        self.notifier = DoorayNotifier(DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, self.api_client)
        
        # 뉴욕마켓워치 뉴스 설정
        self.news_type = "newyork-market-watch"
        self.news_config = NEWS_TYPES.get(self.news_type, {})
        self.display_name = self.news_config.get('display_name', '뉴욕마켓워치')
        self.emoji = self.news_config.get('emoji', '🌆')
        
        # 발행 시간 패턴 (06:00-07:00 기준)
        self.expected_publish_time = "060000"  # 06:00:00
        self.delay_check_times = ["073000", "080000", "083000"]  # 07:30, 08:00, 08:30
        
        # 상태 추적
        self.last_data = None
        self.delay_notifications_sent = set()
        
        print(f"🌆 {self.display_name} 전용 모니터링 시스템 초기화 완료")
    
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
    
    def get_current_ny_data(self):
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
                'analysis': f'발행됨 (시간 파싱 실패: {news_time})'
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
        stage_times = {1: "07:30", 2: "08:00", 3: "08:30"}
        
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
        message += f"📋 예상 발행 시간: 06:00-07:00\n"
        message += f"🚨 지연 상태: {expected_time} 기준 미발행\n\n"
        
        # 지연 단계별 메시지
        if delay_stage == 1:
            message += "• 30분 지연 상태입니다.\n"
            message += "• 뉴욕 시장 상황에 따른 지연일 수 있습니다.\n"
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
    
    def send_publish_notification(self, ny_data, pattern_analysis):
        """
        뉴욕마켓워치 발행 알림 전송
        
        Args:
            ny_data (dict): 뉴욕마켓워치 뉴스 데이터
            pattern_analysis (dict): 발행 패턴 분석 결과
        """
        title = ny_data.get('title', '')
        date = ny_data.get('date', '')
        time = ny_data.get('time', '')
        
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
            status_emoji = "🌆"
            color = "#6c757d"  # 회색
            status_text = "발행 완료"
        
        message = f"{status_emoji} {self.display_name} {status_text}\n\n"
        
        # 발행 정보 (뉴욕마켓워치 전용 시간 포맷팅)
        if date:
            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
            formatted_time = pattern_analysis.get('formatted_time', self.format_ny_time(time))
            formatted_datetime = f"{formatted_date} {formatted_time}"
        else:
            formatted_datetime = "날짜 정보 없음"
        
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
        ny_data = self.get_current_ny_data()
        
        if not ny_data:
            print(f"❌ {self.display_name} 데이터 없음")
            return
        
        # 발행 패턴 분석
        pattern_analysis = self.analyze_publish_pattern(ny_data)
        
        print(f"📊 분석 결과: {pattern_analysis.get('analysis', '분석 불가')}")
        
        # 변경사항 감지
        if self.last_data != ny_data:
            print(f"🆕 {self.display_name} 데이터 변경 감지")
            
            # 발행 알림 전송
            if pattern_analysis.get('is_published_today', False):
                self.send_publish_notification(ny_data, pattern_analysis)
            
            self.last_data = ny_data.copy() if ny_data else None
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