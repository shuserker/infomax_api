#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 - 기본 추상 클래스

모든 뉴스 모니터링 클래스의 공통 기능을 제공하는 추상 기본 클래스입니다.

주요 기능:
- 공통 초기화 로직
- 표준화된 알림 전송
- 공통 모니터링 루프
- 설정 기반 동작

작성자: AI Assistant
최종 수정: 2025-07-30 (최적화)
"""

import sys
import os
import time
import requests
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core import PoscoNewsAPIClient, NewsDataProcessor, DoorayNotifier
    from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, NEWS_MONITOR_CONFIG
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class BaseNewsMonitor(ABC):
    """
    뉴스 모니터링 기본 추상 클래스
    
    모든 뉴스 모니터링 클래스가 상속받아야 하는 기본 클래스입니다.
    공통 기능을 제공하고 각 뉴스별 특수 처리는 하위 클래스에서 구현합니다.
    """
    
    def __init__(self, news_type):
        """
        기본 모니터 초기화
        
        Args:
            news_type (str): 뉴스 타입 (예: "exchange-rate")
        """
        self.news_type = news_type
        self.config = NEWS_MONITOR_CONFIG.get(news_type, {})
        
        if not self.config:
            raise ValueError(f"뉴스 타입 '{news_type}'에 대한 설정을 찾을 수 없습니다.")
        
        # 공통 컴포넌트 초기화
        self.api_client = PoscoNewsAPIClient(API_CONFIG)
        self.data_processor = NewsDataProcessor()
        self.notifier = DoorayNotifier(DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, self.api_client)
        
        # 설정에서 값 추출
        self.display_name = self.config.get('display_name', news_type.upper())
        self.emoji = self.config.get('emoji', '📰')
        self.expected_publish_time = self.config.get('expected_publish_time', '120000')
        self.delay_check_times = self.config.get('delay_check_times', [])
        self.tolerance_minutes = self.config.get('tolerance_minutes', 10)
        self.time_format = self.config.get('time_format', '6digit')
        self.delay_messages = self.config.get('delay_messages', {})
        
        # 상태 추적
        self.last_data = None
        self.delay_notifications_sent = set()
        
        print(f"{self.emoji} {self.display_name} 전용 모니터링 시스템 초기화 완료")
    
    @abstractmethod
    def get_current_news_data(self):
        """
        현재 뉴스 데이터 조회 (하위 클래스에서 구현)
        
        Returns:
            dict: 뉴스 데이터 또는 None
        """
        pass
    
    @abstractmethod
    def analyze_publish_pattern(self, news_data):
        """
        발행 패턴 분석 (하위 클래스에서 구현)
        
        Args:
            news_data (dict): 뉴스 데이터
            
        Returns:
            dict: 발행 패턴 분석 결과
        """
        pass
    
    def _format_news_datetime(self, date, time, pattern_analysis):
        """
        뉴스 날짜시간 포맷팅
        
        Args:
            date (str): 날짜 문자열 (YYYYMMDD)
            time (str): 시간 문자열
            pattern_analysis (dict): 패턴 분석 결과
            
        Returns:
            str: 포맷팅된 날짜시간
        """
        if not date:
            return "날짜 정보 없음"
        
        try:
            # 날짜 포맷팅 (YYYYMMDD → YYYY-MM-DD)
            if len(date) >= 8:
                formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
            else:
                formatted_date = date
            
            # 시간 포맷팅
            if not time:
                return f"{formatted_date} 시간 정보 없음"
            
            # 패턴 분석에서 포맷팅된 시간 사용
            if 'formatted_time' in pattern_analysis:
                formatted_time = pattern_analysis['formatted_time']
            elif 'actual_time' in pattern_analysis:
                formatted_time = pattern_analysis['actual_time']
            else:
                # 기본 시간 포맷팅
                if self.time_format == '5digit' and len(time) == 5:
                    # 5자리 형식: 61831 → 06:18:31
                    hour = int(time[0])
                    minute = int(time[1:3])
                    second = int(time[3:5])
                    formatted_time = f"{hour:02d}:{minute:02d}:{second:02d}"
                elif len(time) >= 6:
                    # 6자리 형식: 154000 → 15:40:00
                    formatted_time = f"{time[:2]}:{time[2:4]}:{time[4:6]}"
                elif len(time) >= 4:
                    # 4자리 형식: 1540 → 15:40:00
                    formatted_time = f"{time[:2]}:{time[2:4]}:00"
                else:
                    formatted_time = f"시간오류({time})"
            
            return f"{formatted_date} {formatted_time}"
            
        except (ValueError, IndexError) as e:
            return f"날짜시간 오류({date} {time})"
    
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
        stage_times = {1: self.delay_check_times[0][:2] + ":" + self.delay_check_times[0][2:4] if len(self.delay_check_times) > 0 else "알 수 없음",
                      2: self.delay_check_times[1][:2] + ":" + self.delay_check_times[1][2:4] if len(self.delay_check_times) > 1 else "알 수 없음",
                      3: self.delay_check_times[2][:2] + ":" + self.delay_check_times[2][2:4] if len(self.delay_check_times) > 2 else "알 수 없음"}
        
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
        
        # 예상 발행 시간 포맷팅
        expected_publish = self.expected_publish_time
        if len(expected_publish) >= 4:
            expected_display = f"{expected_publish[:2]}:{expected_publish[2:4]}"
        else:
            expected_display = "알 수 없음"
        
        message = f"{emoji} {self.display_name} 지연 발행 알림 ({stage_name})\n\n"
        message += f"📅 날짜: {current_time.strftime('%Y-%m-%d')}\n"
        message += f"⏰ 현재 시간: {current_time.strftime('%H:%M:%S')}\n"
        message += f"📋 예상 발행 시간: {expected_display}\n"
        message += f"🚨 지연 상태: {expected_time} 기준 미발행\n\n"
        
        # 설정에서 지연 메시지 가져오기
        delay_message = self.delay_messages.get(delay_stage, f"• {delay_stage}차 지연 상태입니다.")
        message += delay_message + "\n"
        
        next_stage_time = stage_times.get(delay_stage + 1, '수동 확인')
        message += f"\n🔍 다음 확인: {next_stage_time}"
        
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
    
    def send_publish_notification(self, news_data, pattern_analysis):
        """
        발행 알림 전송
        
        Args:
            news_data (dict): 뉴스 데이터
            pattern_analysis (dict): 발행 패턴 분석 결과
        """
        title = news_data.get('title', '')
        date = news_data.get('date', '')
        time = news_data.get('time', '')
        
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
            status_emoji = self.emoji
            color = "#6c757d"  # 회색
            status_text = "발행 완료"
        
        message = f"{status_emoji} {self.display_name} {status_text}\n\n"
        
        # 발행 정보
        formatted_datetime = self._format_news_datetime(date, time, pattern_analysis)
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
    
    def _format_news_datetime(self, date, time, pattern_analysis):
        """
        뉴스 날짜시간 포맷팅 (각 뉴스별 특수 처리 가능)
        
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
        
        # 패턴 분석에서 포맷팅된 시간이 있으면 사용
        if 'formatted_time' in pattern_analysis:
            formatted_time = pattern_analysis['formatted_time']
        else:
            # 기본 시간 포맷팅
            formatted_time = self.data_processor.format_datetime(date, time).split(' ')[-1] if time else "시간 정보 없음"
        
        return f"{formatted_date} {formatted_time}"
    
    def run_single_check(self):
        """단일 상태 확인 실행"""
        print(f"🔍 {self.display_name} 상태 확인 중...")
        
        # 현재 데이터 조회
        news_data = self.get_current_news_data()
        
        if not news_data:
            print(f"❌ {self.display_name} 데이터 없음")
            return
        
        # 발행 패턴 분석
        pattern_analysis = self.analyze_publish_pattern(news_data)
        
        print(f"📊 분석 결과: {pattern_analysis.get('analysis', '분석 불가')}")
        
        # 변경사항 감지
        if self.last_data != news_data:
            print(f"🆕 {self.display_name} 데이터 변경 감지")
            
            # 발행 알림 전송
            if pattern_analysis.get('is_published_today', False):
                self.send_publish_notification(news_data, pattern_analysis)
            
            self.last_data = news_data.copy() if news_data else None
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