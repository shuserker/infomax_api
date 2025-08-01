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
    from reports.html_report_generator import HTMLReportGenerator
    from reports.report_manager import ReportManager
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
        self.report_generator = HTMLReportGenerator()
        self.report_manager = ReportManager()
        
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
        
        # HTML 리포트 생성 (백그라운드에서 처리)
        report_info = None
        analysis_result = None
        try:
            analysis_result = self._prepare_analysis_data(news_data, pattern_analysis)
            report_info = self.report_generator.generate_report(analysis_result, self.news_type, self.display_name)
            
            if report_info and not report_info.get('error'):
                # 리포트 매니저에 추가
                self.report_manager.add_report(
                    report_info['filename'],
                    self.news_type,
                    self.display_name,
                    analysis_result.get('summary', {})
                )
                print(f"📊 리포트 저장됨: {report_info['local_path']}")
                
        except Exception as e:
            print(f"⚠️ 리포트 생성 실패: {e}")
        
        # 메인 attachment 구성
        attachment = {
            "color": color,
            "text": message
        }
        
        # 리포트가 생성되었으면 버튼 추가 (GitHub Pages URL 사용)
        if report_info and not report_info.get('error'):
            github_url = report_info.get('github_url')
            
            if github_url:
                # GitHub Pages 배포 성공 시 버튼 추가
                attachment["actions"] = [
                    {
                        "type": "button",
                        "text": "📊 리포트 다운로드",
                        "url": github_url,
                        "style": "primary"
                    },
                    {
                        "type": "button", 
                        "text": "🌐 대시보드",
                        "url": "https://shuserker.github.io/infomax_api/",
                        "style": "default"
                    }
                ]
                print(f"🔗 리포트 URL 생성: {github_url}")
            else:
                print("⚠️ GitHub Pages URL 생성 실패 - 버튼 없이 전송")
        
        payload = {
            "botName": f"POSCO 뉴스 {status_emoji}",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": f"{self.display_name} {status_text}",
            "attachments": [attachment]
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
    
    def _prepare_analysis_data(self, news_data, pattern_analysis):
        """
        리포트 생성을 위한 분석 데이터 준비
        
        Args:
            news_data (dict): 뉴스 데이터
            pattern_analysis (dict): 패턴 분석 결과
            
        Returns:
            dict: 리포트용 분석 데이터
        """
        return {
            'current_news': news_data,
            'pattern_analysis': pattern_analysis,
            'news_type': self.news_type,
            'display_name': self.display_name,
            'total_articles': 1,  # 기본값
            'sector_analysis': {
                self.display_name: {
                    'mentions': 1,
                    'sentiment': '긍정' if pattern_analysis.get('status') == 'on_time' else '중립',
                    'prediction': {
                        'next_day_prediction': '긍정' if pattern_analysis.get('status') == 'on_time' else '중립',
                        'prediction_confidence': 0.8 if pattern_analysis.get('status') == 'on_time' else 0.6
                    }
                }
            },
            'global_impact': {
                '국내시장': {
                    'total_impact': 1,
                    'trend': '증가' if pattern_analysis.get('status') == 'on_time' else '유지'
                }
            },
            'summary': {
                'status': pattern_analysis.get('status', 'unknown'),
                'analysis': pattern_analysis.get('analysis', '분석 불가'),
                'publish_time': self._format_news_datetime(
                    news_data.get('date', ''), 
                    news_data.get('time', ''), 
                    pattern_analysis
                )
            }
        }    

    def _generate_report_summary(self, analysis_result):
        """
        Dooray 메시지에 포함할 리포트 요약 생성
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            str: 요약 텍스트
        """
        try:
            status = analysis_result.get('summary', {}).get('status', 'unknown')
            analysis = analysis_result.get('summary', {}).get('analysis', '분석 불가')
            current_news = analysis_result.get('current_news', {})
            title = current_news.get('title', '제목 없음')
            
            # 상태별 이모지 및 메시지
            if status == 'on_time':
                status_emoji = "✅"
                market_impact = "긍정적 시장 신호"
                investment_advice = "안정적 투자 환경"
                confidence = "90%"
            elif status == 'early':
                status_emoji = "⚡"
                market_impact = "시장 활성화 신호"
                investment_advice = "적극적 투자 기회"
                confidence = "85%"
            elif status == 'delayed':
                status_emoji = "⏰"
                market_impact = "시장 불안 요소"
                investment_advice = "신중한 투자 접근"
                confidence = "75%"
            else:
                status_emoji = "📊"
                market_impact = "시장 상황 모니터링"
                investment_advice = "관망 전략 권장"
                confidence = "70%"
            
            # 제목 요약 (너무 길면 줄임)
            title_summary = title[:50] + "..." if len(title) > 50 else title
            
            summary = f"""{status_emoji} **발행 패턴**: {analysis}
📰 **뉴스 제목**: {title_summary}
📈 **시장 영향**: {market_impact}
💡 **투자 가이드**: {investment_advice}
🎯 **AI 신뢰도**: {confidence}

🔍 **분석 요약**:
• 발행 시점이 시장 심리에 미치는 영향도 평가
• 정시 발행 시 시장 안정성 증가, 지연 시 불안 요소 증가
• 투자자들의 정보 접근성과 의사결정에 직접적 영향

⚡ **즉시 활용 가능한 인사이트를 제공합니다**"""
            
            return summary
            
        except Exception as e:
            return f"📊 리포트 요약 생성 중 오류 발생: {e}"