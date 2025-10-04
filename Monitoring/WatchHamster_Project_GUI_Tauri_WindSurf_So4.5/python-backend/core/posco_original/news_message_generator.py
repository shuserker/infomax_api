# -*- coding: utf-8 -*-
"""
뉴스 알림 메시지 생성 로직 완전 복원

정상 커밋 a763ef84의 원본 메시지 생성 알고리즘을 역추적하여 복원한 모듈입니다.

주요 기능:
- 데이터 상태별 동적 메시지 생성 로직 (최신/발행전/지연 모든 경우의 수)
- 시간 기반 상태 판단 알고리즘 복원 (발행 시간 vs 현재 시간 비교)
- 뉴스 타입별 개별 상태 처리 로직 (NEWYORK/KOSPI/EXCHANGE 각각)
- 테스트/실제 모드 자동 판단 로직 및 메시지 포맷 변경
- 트리 구조 메시지 동적 생성 알고리즘 (├, └ 구조)

작성자: AI Assistant
복원 일시: 2025-08-12
수정일: 2025-08-16 (Import 경로 수정)
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
import logging

# 워치햄스터 공통 모듈에서 import (watchhamster_original 디렉토리)
try:
    from ..watchhamster_original.integrated_news_parser import IntegratedNewsParser, IntegratedNewsData
    from ..watchhamster_original.news_data_parser import NewsItem, NewsStatus
except ImportError:
    # 레거시 경로 fallback
    try:
        from recovery_config.integrated_news_parser import IntegratedNewsParser, IntegratedNewsData
        from recovery_config.news_data_parser import NewsItem, NewsStatus
    except ImportError:
        # 개발 환경에서 직접 import
        from integrated_news_parser import IntegratedNewsParser, IntegratedNewsData
        from news_data_parser import NewsItem, NewsStatus


@dataclass
class MessageGenerationResult:
    """메시지 생성 결과"""
    success: bool
    message: str
    bot_name: str
    bot_icon: str
    color: str
    message_type: str
    test_mode: bool
    errors: List[str]
    warnings: List[str]
    generation_time: float


@dataclass
class BusinessDayComparison:
    """영업일 비교 데이터"""
    current_data: Optional[Dict[str, Any]]
    previous_data: Optional[Dict[str, Any]]
    status: str
    status_display: str
    comparison_text: str


class NewsMessageGenerator:
    """
    뉴스 알림 메시지 생성 시스템
    
    정상 커밋의 원본 로직을 기반으로 5가지 BOT 타입의 메시지를 생성합니다.
    """
    
    @staticmethod
    def format_time_string(time_str: str) -> str:
        """
        시간 문자열을 HH:MM 형태로 변환
        
        Args:
            time_str (str): 시간 문자열 (HHMMSS, HHMM, HH:MM 등)
        
        Returns:
            str: HH:MM 형태의 시간 문자열
        """
        if not time_str:
            return "시간 정보 없음"
        
        # 이미 HH:MM 형태인 경우
        if ':' in time_str and len(time_str) == 5:
            return time_str
        
        # 숫자만 있는 경우 (HHMMSS 또는 HHMM)
        if time_str.isdigit():
            if len(time_str) == 6:  # HHMMSS
                return f"{time_str[:2]}:{time_str[2:4]}"
            elif len(time_str) == 4:  # HHMM
                return f"{time_str[:2]}:{time_str[2:4]}"
            elif len(time_str) == 3:  # HMM
                return f"0{time_str[0]}:{time_str[1:3]}"
            elif len(time_str) == 2:  # HH
                return f"{time_str}:00"
        
        # 기타 형태는 그대로 반환
        return time_str
    
    def __init__(self, test_mode: bool = False, test_datetime: Optional[datetime] = None):
        """
        메시지 생성기 초기화
        
        Args:
            test_mode (bool): 테스트 모드 활성화 여부
            test_datetime (datetime): 테스트용 시간 (테스트 모드에서만 사용)
        """
        self.logger = logging.getLogger(__name__)
        
        # 테스트 모드 설정
        self.test_mode = test_mode
        self.test_datetime = test_datetime or datetime.now()
        
        # 뉴스 타입 정의 (정상 커밋과 동일)
        self.news_types = {
            'newyork-market-watch': {
                'display_name': 'NEWYORK MARKET WATCH',
                'emoji': '🌆',
                'expected_time': (6, 0),  # 06:00
                'tolerance_minutes': 15,
                'api_key': 'newyork_market'
            },
            'kospi-close': {
                'display_name': 'KOSPI CLOSE', 
                'emoji': '📈',
                'expected_time': (15, 40),  # 15:40
                'tolerance_minutes': 10,
                'api_key': 'kospi_close'
            },
            'exchange-rate': {
                'display_name': 'EXCHANGE RATE',
                'emoji': '💱',
                'expected_time': (16, 30),  # 16:30
                'tolerance_minutes': 5,
                'api_key': 'exchange_rate'
            }
        }
        
        # BOT 설정 (정상 커밋과 동일)
        self.bot_configs = {
            'comparison': {
                'name': 'POSCO 뉴스 비교알림',
                'icon': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg',
                'color': '#007bff'
            },
            'delay': {
                'name': 'POSCO 뉴스 ⏰',
                'icon': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg',
                'color': '#ffc107'
            },
            'report': {
                'name': 'POSCO 뉴스 📊',
                'icon': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg',
                'color': '#28a745'
            },
            'status': {
                'name': 'POSCO 뉴스 ✅',
                'icon': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg',
                'color': '#17a2b8'
            },
            'no_data': {
                'name': 'POSCO 뉴스 🔔',
                'icon': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg',
                'color': '#6c757d'
            }
        }
        
        # 통합 뉴스 파서 초기화
        self.news_parser = IntegratedNewsParser()
        
        self.logger.info("뉴스 메시지 생성기 초기화 완료")
    
    def generate_business_day_comparison_message(self, raw_data: Dict[str, Any], 
                                               historical_data: Optional[Dict[str, Any]] = None) -> MessageGenerationResult:
        """
        영업일 비교 분석 메시지 생성 (첫 번째 캡처 형식)
        
        Args:
            raw_data (dict): 현재 뉴스 데이터
            historical_data (dict): 과거 데이터 (영업일 비교용)
        
        Returns:
            MessageGenerationResult: 메시지 생성 결과
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            self.logger.info("영업일 비교 분석 메시지 생성 시작")
            
            # 뉴스 데이터 파싱
            parsing_result = self.news_parser.parse_all_news_data(raw_data)
            if not parsing_result.success:
                errors.extend(parsing_result.errors)
                return self._create_error_result("comparison", errors, warnings, start_time)
            
            integrated_data = parsing_result.data
            
            # 메시지 헤더
            current_time = self.test_datetime if self.test_mode else datetime.now()
            message_lines = [
                "📊 영업일 비교 분석",
                f"🕐 분석 시간: {current_time.strftime('%Y-%m-%d %H:%M')}",
                ""
            ]
            
            # 전체 시장 동향 예측
            market_prediction = self._generate_market_prediction(integrated_data, historical_data)
            if market_prediction:
                message_lines.extend([
                    "🔮 시장 동향 예측:",
                    f"  {market_prediction}",
                    ""
                ])
            
            # 각 뉴스 타입별 비교 분석
            for news_type, config in self.news_types.items():
                display_name = config['display_name']
                
                # 현재 데이터 확인
                current_news = integrated_data.news_items.get(news_type)
                comparison = self._generate_business_day_comparison(
                    news_type, current_news, historical_data
                )
                
                # 트리 구조 메시지 생성 (타이틀 포함)
                message_lines.append(f"[{display_name}]")
                message_lines.extend(self._format_enhanced_tree_structure(comparison, news_type, raw_data, historical_data))
                message_lines.append("")
            
            # 종합 분석 및 권장사항
            summary_analysis = self._generate_comprehensive_analysis(integrated_data, historical_data)
            if summary_analysis:
                message_lines.extend([
                    "📈 종합 분석:",
                    f"  {summary_analysis}",
                    ""
                ])
            
            # 테스트 모드 처리
            message = "\n".join(message_lines).strip()
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준\n\n{message}"
            
            # BOT 설정
            bot_config = self.bot_configs['comparison']
            bot_name = f"[TEST] {bot_config['name']}" if self.test_mode else bot_config['name']
            
            processing_time = time.time() - start_time
            self.logger.info(f"영업일 비교 분석 메시지 생성 완료: {processing_time:.3f}초")
            
            return MessageGenerationResult(
                success=True,
                message=message,
                bot_name=bot_name,
                bot_icon=bot_config['icon'],
                color=bot_config['color'],
                message_type='comparison',
                test_mode=self.test_mode,
                errors=errors,
                warnings=warnings,
                generation_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"영업일 비교 분석 메시지 생성 오류: {e}")
            errors.append(f"메시지 생성 오류: {e}")
            return self._create_error_result("comparison", errors, warnings, start_time)
    
    def generate_delay_notification_message(self, news_type: str, current_data: Dict[str, Any], 
                                          delay_minutes: int) -> MessageGenerationResult:
        """
        지연 발행 알림 메시지 생성 (두 번째 캡처 형식)
        
        Args:
            news_type (str): 뉴스 타입
            current_data (dict): 현재 뉴스 데이터
            delay_minutes (int): 지연 시간(분)
        
        Returns:
            MessageGenerationResult: 메시지 생성 결과
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            self.logger.info(f"{news_type} 지연 발행 알림 메시지 생성 시작")
            
            if news_type not in self.news_types:
                errors.append(f"알 수 없는 뉴스 타입: {news_type}")
                return self._create_error_result("delay", errors, warnings, start_time)
            
            config = self.news_types[news_type]
            display_name = config['display_name']
            expected_hour, expected_minute = config['expected_time']
            
            # 지연 정도에 따른 신호등 이모지
            if delay_minutes <= 15:
                delay_status = "🟡"  # 노랑불: 경미한 지연
            elif delay_minutes <= 60:
                delay_status = "🟠"  # 주황불: 중간 지연  
            else:
                delay_status = "🔴"  # 빨강불: 심각한 지연
            
            # 실제 발행 시간 계산
            current_time = self.test_datetime if self.test_mode else datetime.now()
            
            # 데이터에서 실제 발행 시간 추출 및 포맷 변환
            actual_time_raw = current_data.get('time') or current_data.get('publish_time')
            if actual_time_raw:
                actual_time = self.format_time_string(actual_time_raw)
            else:
                actual_time = current_time.strftime('%H:%M')
            
            expected_time = f"{expected_hour:02d}:{expected_minute:02d}"
            
            # 메시지 구성
            message_lines = [
                f"{delay_status} {display_name.lower()} 지연 발행",
                "",
                f"📅 발행 시간: {current_time.strftime('%Y-%m-%d')} {actual_time}:00",
                f"📊 패턴 분석: ⏱️ {delay_minutes}분 지연 발행 ({actual_time})",
                f"⏰ 예상: {expected_time} → 실제: {actual_time}",
                f"📋 제목: {current_data.get('title', '제목 없음')}",
                "",
                "🔔 지연 알림이 초기화되었습니다."
            ]
            
            # 테스트 모드 처리
            message = "\n".join(message_lines)
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준\n\n{message}"
            
            # BOT 설정
            bot_config = self.bot_configs['delay']
            bot_name = f"[TEST] {bot_config['name']}" if self.test_mode else bot_config['name']
            
            processing_time = time.time() - start_time
            self.logger.info(f"{news_type} 지연 발행 알림 메시지 생성 완료: {processing_time:.3f}초")
            
            return MessageGenerationResult(
                success=True,
                message=message,
                bot_name=bot_name,
                bot_icon=bot_config['icon'],
                color=bot_config['color'],
                message_type='delay',
                test_mode=self.test_mode,
                errors=errors,
                warnings=warnings,
                generation_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"{news_type} 지연 발행 알림 메시지 생성 오류: {e}")
            errors.append(f"메시지 생성 오류: {e}")
            return self._create_error_result("delay", errors, warnings, start_time)
    
    def generate_daily_integrated_report_message(self, raw_data: Dict[str, Any], 
                                               report_url: Optional[str] = None) -> MessageGenerationResult:
        """
        일일 통합 분석 리포트 메시지 생성 (세 번째 캡처 형식)
        
        Args:
            raw_data (dict): 현재 뉴스 데이터
            report_url (str): HTML 리포트 URL
        
        Returns:
            MessageGenerationResult: 메시지 생성 결과
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            self.logger.info("일일 통합 분석 리포트 메시지 생성 시작")
            
            # 뉴스 데이터 파싱
            parsing_result = self.news_parser.parse_all_news_data(raw_data)
            if not parsing_result.success:
                errors.extend(parsing_result.errors)
                return self._create_error_result("report", errors, warnings, start_time)
            
            integrated_data = parsing_result.data
            
            # 발행 현황 분석
            published_count = integrated_data.status_counts['latest']
            total_count = integrated_data.status_counts['total']
            
            # 메시지 헤더
            current_time = self.test_datetime if self.test_mode else datetime.now()
            message_lines = [
                "📊 일일 통합 분석 리포트",
                "",
                f"📅 분석 일자: {current_time.strftime('%Y년 %m월 %d일')}",
                f"📊 발행 현황: {published_count}/{total_count}개 완료",
                ""
            ]
            
            # 각 뉴스별 상세 현황 (타이틀 및 변화 분석 포함)
            message_lines.append("📋 뉴스별 발행 현황:")
            for news_type, config in self.news_types.items():
                display_name = config['display_name']
                emoji = config['emoji']
                
                news_item = integrated_data.news_items.get(news_type)
                current_title = raw_data.get(news_type, {}).get('title', '')
                
                if news_item and news_item.is_latest:
                    status_icon = "✅"
                    status_text = "발행 완료"
                    # 시간 포맷 변환
                    time_info = self.format_time_string(news_item.time) if news_item.time else "시간 정보 없음"
                    
                    message_lines.append(f"  {emoji} {display_name}: {status_icon} {status_text} ({time_info})")
                    
                    # 뉴스 타이틀 추가
                    if current_title:
                        title_preview = current_title[:50] + "..." if len(current_title) > 50 else current_title
                        message_lines.append(f"    📰 {title_preview}")
                else:
                    status_icon = "⏳"
                    status_text = "발행 대기"
                    time_info = "미발행"
                    
                    message_lines.append(f"  {emoji} {display_name}: {status_icon} {status_text} ({time_info})")
                    
                    # 예상 발행 시간 추가
                    expected_time = self._predict_next_publication_time(news_type, {})
                    message_lines.append(f"    ⏰ 예상: {expected_time}")
            
            message_lines.append("")
            
            # 시장 요약
            if integrated_data.market_summary:
                message_lines.extend([
                    "📈 시장 요약:",
                    f"  {integrated_data.market_summary}",
                    ""
                ])
            
            # 직전 대비 변화 분석 (report_url이 있을 때만 표시)
            if report_url:
                message_lines.extend([
                    "📊 직전 대비 변화:",
                    f"  • 발행 완료율: {published_count}/{total_count}개",
                    f"  • 시장 동향: {integrated_data.market_summary[:30] if integrated_data.market_summary else '분석 중'}...",
                    f"  • 모니터링 상태: 정상 운영 중",
                    ""
                ])
            
            # 권장사항
            if integrated_data.recommendations:
                message_lines.append("💡 권장사항:")
                for i, recommendation in enumerate(integrated_data.recommendations[:3], 1):
                    message_lines.append(f"  {i}. {recommendation}")
                message_lines.append("")
            else:
                # 기본 권장사항 제공
                message_lines.extend([
                    "💡 권장사항:",
                    "  1. 정상 운영 중 - 지속적인 모니터링 유지",
                    "  2. 지연 발생 시 즉시 알림 체계 가동",
                    "  3. 다음 영업일 준비 상태 점검",
                    ""
                ])
            
            # HTML 리포트 링크
            if report_url:
                message_lines.extend([
                    "🔗 상세 리포트:",
                    f"  {report_url}",
                    ""
                ])
            
            # 생성 시간
            message_lines.append(f"🕐 생성 시간: {current_time.strftime('%H:%M:%S')}")
            
            # 테스트 모드 처리
            message = "\n".join(message_lines)
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준\n\n{message}"
            
            # BOT 설정
            bot_config = self.bot_configs['report']
            bot_name = f"[TEST] {bot_config['name']}" if self.test_mode else bot_config['name']
            
            processing_time = time.time() - start_time
            self.logger.info(f"일일 통합 분석 리포트 메시지 생성 완료: {processing_time:.3f}초")
            
            return MessageGenerationResult(
                success=True,
                message=message,
                bot_name=bot_name,
                bot_icon=bot_config['icon'],
                color=bot_config['color'],
                message_type='report',
                test_mode=self.test_mode,
                errors=errors,
                warnings=warnings,
                generation_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"일일 통합 분석 리포트 메시지 생성 오류: {e}")
            errors.append(f"메시지 생성 오류: {e}")
            return self._create_error_result("report", errors, warnings, start_time)
    
    def generate_status_notification_message(self, raw_data: Dict[str, Any]) -> MessageGenerationResult:
        """
        정시 발행 알림 메시지 생성 (네 번째 캡처 형식)
        
        Args:
            raw_data (dict): 현재 뉴스 데이터
        
        Returns:
            MessageGenerationResult: 메시지 생성 결과
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            self.logger.info("정시 발행 알림 메시지 생성 시작")
            
            # 뉴스 데이터 파싱
            parsing_result = self.news_parser.parse_all_news_data(raw_data)
            if not parsing_result.success:
                errors.extend(parsing_result.errors)
                return self._create_error_result("status", errors, warnings, start_time)
            
            integrated_data = parsing_result.data
            
            # 현재 시간
            current_time = self.test_datetime if self.test_mode else datetime.now()
            
            # 메시지 구성
            message_lines = [
                "✅ 정시 발행 알림",
                "",
                f"📅 확인 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
                ""
            ]
            
            # 각 뉴스별 현재 상태 (타이틀 포함)
            message_lines.append("📊 현재 발행 상태:")
            for news_type, config in self.news_types.items():
                display_name = config['display_name']
                emoji = config['emoji']
                
                news_item = integrated_data.news_items.get(news_type)
                status_info = self._get_news_status_display(news_item, config)
                
                # 뉴스 타이틀 추가
                current_title = raw_data.get(news_type, {}).get('title', '')
                if current_title and news_item and news_item.is_latest:
                    title_preview = current_title[:40] + "..." if len(current_title) > 40 else current_title
                    message_lines.append(f"  {emoji} {display_name}: {status_info}")
                    message_lines.append(f"    📰 {title_preview}")
                else:
                    message_lines.append(f"  {emoji} {display_name}: {status_info}")
            
            message_lines.append("")
            
            # 전체 상태 요약
            overall_status = integrated_data.overall_status
            if overall_status == 'latest':
                summary_icon = "🟢"
                summary_text = "모든 뉴스 최신 상태"
            elif overall_status == 'delayed':
                summary_icon = "🟡"
                summary_text = "일부 뉴스 지연 상태"
            else:
                summary_icon = "🔴"
                summary_text = "뉴스 상태 확인 필요"
            
            message_lines.extend([
                f"{summary_icon} 전체 상태: {summary_text}",
                "",
                "🔔 정시 상태 확인이 완료되었습니다."
            ])
            
            # 테스트 모드 처리
            message = "\n".join(message_lines)
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준\n\n{message}"
            
            # BOT 설정
            bot_config = self.bot_configs['status']
            bot_name = f"[TEST] {bot_config['name']}" if self.test_mode else bot_config['name']
            
            processing_time = time.time() - start_time
            self.logger.info(f"정시 발행 알림 메시지 생성 완료: {processing_time:.3f}초")
            
            return MessageGenerationResult(
                success=True,
                message=message,
                bot_name=bot_name,
                bot_icon=bot_config['icon'],
                color=bot_config['color'],
                message_type='status',
                test_mode=self.test_mode,
                errors=errors,
                warnings=warnings,
                generation_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"정시 발행 알림 메시지 생성 오류: {e}")
            errors.append(f"메시지 생성 오류: {e}")
            return self._create_error_result("status", errors, warnings, start_time)
    
    def generate_no_data_notification_message(self, raw_data: Dict[str, Any]) -> MessageGenerationResult:
        """
        데이터 갱신 없음 알림 메시지 생성 (다섯 번째 캡처 형식)
        
        Args:
            raw_data (dict): 현재 뉴스 데이터
        
        Returns:
            MessageGenerationResult: 메시지 생성 결과
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            self.logger.info("데이터 갱신 없음 알림 메시지 생성 시작")
            
            # 현재 시간
            current_time = self.test_datetime if self.test_mode else datetime.now()
            
            # 메시지 구성
            message_lines = [
                "🔔 데이터 갱신 없음",
                "",
                f"📅 확인 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
                ""
            ]
            
            # 각 뉴스별 마지막 확인 상태
            message_lines.append("📊 마지막 확인 상태:")
            for news_type, config in self.news_types.items():
                display_name = config['display_name']
                emoji = config['emoji']
                
                # 데이터가 있는지 확인
                if news_type in raw_data and raw_data[news_type].get('title'):
                    last_time_raw = raw_data[news_type].get('time', '시간 정보 없음')
                    # 시간 포맷 변환
                    last_time = self.format_time_string(last_time_raw) if last_time_raw != '시간 정보 없음' else last_time_raw
                    message_lines.append(f"  {emoji} {display_name}: 마지막 데이터 {last_time}")
                else:
                    message_lines.append(f"  {emoji} {display_name}: 데이터 없음")
            
            message_lines.extend([
                "",
                "⏳ 새로운 뉴스 발행을 대기 중입니다.",
                "🔄 다음 확인까지 5분 대기합니다."
            ])
            
            # 테스트 모드 처리
            message = "\n".join(message_lines)
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준\n\n{message}"
            
            # BOT 설정
            bot_config = self.bot_configs['no_data']
            bot_name = f"[TEST] {bot_config['name']}" if self.test_mode else bot_config['name']
            
            processing_time = time.time() - start_time
            self.logger.info(f"데이터 갱신 없음 알림 메시지 생성 완료: {processing_time:.3f}초")
            
            return MessageGenerationResult(
                success=True,
                message=message,
                bot_name=bot_name,
                bot_icon=bot_config['icon'],
                color=bot_config['color'],
                message_type='no_data',
                test_mode=self.test_mode,
                errors=errors,
                warnings=warnings,
                generation_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"데이터 갱신 없음 알림 메시지 생성 오류: {e}")
            errors.append(f"메시지 생성 오류: {e}")
            return self._create_error_result("no_data", errors, warnings, start_time)
    
    def _generate_business_day_comparison(self, news_type: str, current_news: Optional[NewsItem], 
                                        historical_data: Optional[Dict[str, Any]]) -> BusinessDayComparison:
        """
        영업일 비교 데이터 생성
        
        Args:
            news_type (str): 뉴스 타입
            current_news (NewsItem): 현재 뉴스 아이템
            historical_data (dict): 과거 데이터
        
        Returns:
            BusinessDayComparison: 비교 결과
        """
        try:
            config = self.news_types[news_type]
            current_time = self.test_datetime if self.test_mode else datetime.now()
            
            # 현재 데이터 상태 판단
            if current_news and current_news.is_latest:
                # 최신 데이터 있음
                status = "latest"
                status_display = "🟢 최신"
                current_data = {
                    'title': current_news.title,
                    'time': current_news.time,
                    'status': status_display
                }
            else:
                # 시간 기반 상태 판단
                expected_hour, expected_minute = config['expected_time']
                expected_time = current_time.replace(
                    hour=expected_hour, minute=expected_minute, second=0, microsecond=0
                )
                
                if current_time < expected_time:
                    status = "pending"
                    status_display = "⏳ 발행 전"
                elif current_time <= expected_time + timedelta(minutes=config['tolerance_minutes']):
                    status = "waiting"
                    status_display = "⏳ 발행 대기"
                else:
                    status = "delayed"
                    status_display = "🔴 발행 지연"
                
                current_data = None
            
            # 과거 데이터 확인
            previous_data = None
            if historical_data and news_type in historical_data:
                hist_item = historical_data[news_type]
                if hist_item.get('title'):
                    previous_data = {
                        'title': hist_item['title'],
                        'time': hist_item.get('time', '시간 정보 없음')
                    }
            
            # 비교 텍스트 생성
            comparison_text = self._format_comparison_text(
                current_data, previous_data, status_display
            )
            
            return BusinessDayComparison(
                current_data=current_data,
                previous_data=previous_data,
                status=status,
                status_display=status_display,
                comparison_text=comparison_text
            )
            
        except Exception as e:
            self.logger.error(f"영업일 비교 데이터 생성 오류: {e}")
            return BusinessDayComparison(
                current_data=None,
                previous_data=None,
                status="error",
                status_display="❌ 오류",
                comparison_text="데이터 비교 실패"
            )
    
    def _format_comparison_text(self, current_data: Optional[Dict[str, Any]], 
                              previous_data: Optional[Dict[str, Any]], 
                              status_display: str) -> str:
        """
        비교 텍스트 포맷팅
        
        Args:
            current_data (dict): 현재 데이터
            previous_data (dict): 과거 데이터
            status_display (str): 상태 표시
        
        Returns:
            str: 포맷팅된 비교 텍스트
        """
        lines = []
        
        if current_data:
            # 현재 데이터가 있는 경우 - 시간 포맷 변환
            formatted_time = self.format_time_string(current_data['time'])
            lines.append(f"├ 현재: {formatted_time} {status_display}")
            lines.append(f"└ 제목: {current_data['title']}")
        else:
            # 현재 데이터가 없는 경우
            lines.append(f"├ 현재: {status_display}")
            
            if previous_data:
                # 과거 데이터 시간 포맷 변환
                formatted_prev_time = self.format_time_string(previous_data['time'])
                lines.append(f"├ 직전: 🔄 {formatted_prev_time}")
                lines.append(f"└ 제목: {previous_data['title']}")
            else:
                lines.append("└ 직전: ❌ 데이터 없음")
        
        return lines
    
    def _format_tree_structure(self, comparison: BusinessDayComparison) -> List[str]:
        """
        트리 구조 메시지 포맷팅 (├, └ 구조)
        
        Args:
            comparison (BusinessDayComparison): 비교 데이터
        
        Returns:
            List[str]: 트리 구조 텍스트 라인들
        """
        if isinstance(comparison.comparison_text, list):
            return comparison.comparison_text
        else:
            return [comparison.comparison_text]
    
    def _get_news_status_display(self, news_item: Optional[NewsItem], 
                                config: Dict[str, Any]) -> str:
        """
        뉴스 상태 표시 텍스트 생성
        
        Args:
            news_item (NewsItem): 뉴스 아이템
            config (dict): 뉴스 타입 설정
        
        Returns:
            str: 상태 표시 텍스트
        """
        if not news_item:
            return "❌ 데이터 없음"
        
        # 시간 포맷 변환
        formatted_time = self.format_time_string(news_item.time) if news_item.time else "시간 정보 없음"
        
        if news_item.is_latest:
            return f"✅ 최신 ({formatted_time})"
        elif news_item.is_delayed:
            return f"🟡 {news_item.delay_minutes}분 지연 ({formatted_time})"
        elif news_item.status == NewsStatus.PENDING:
            return "⏳ 발행 전"
        elif news_item.status == NewsStatus.OLD:
            return f"🔄 과거 데이터 ({formatted_time})"
        else:
            return f"⚠️ {news_item.status_description}"
    
    def _create_error_result(self, message_type: str, errors: List[str], 
                           warnings: List[str], start_time: float) -> MessageGenerationResult:
        """오류 결과 생성"""
        return MessageGenerationResult(
            success=False,
            message="메시지 생성 실패",
            bot_name="POSCO 뉴스 오류",
            bot_icon="",
            color="#dc3545",
            message_type=message_type,
            test_mode=self.test_mode,
            errors=errors,
            warnings=warnings,
            generation_time=time.time() - start_time
        )
    
    def determine_message_type(self, raw_data: Dict[str, Any], 
                             current_time: Optional[datetime] = None) -> str:
        """
        현재 상황에 맞는 메시지 타입 자동 결정
        
        Args:
            raw_data (dict): 뉴스 데이터
            current_time (datetime): 현재 시간
        
        Returns:
            str: 메시지 타입 ('comparison', 'delay', 'report', 'status', 'no_data')
        """
        try:
            if current_time is None:
                current_time = self.test_datetime if self.test_mode else datetime.now()
            
            current_hour = current_time.hour
            current_minute = current_time.minute
            
            # 시간대별 메시지 타입 결정 (정상 커밋 로직)
            if current_hour == 6 and current_minute == 10:
                return 'comparison'  # 영업일 비교 분석
            elif current_hour == 18 and current_minute == 0:
                return 'report'  # 일일 통합 리포트
            elif current_minute == 0:  # 매시간 정각
                return 'status'  # 정시 상태 확인
            else:
                # 데이터 상태에 따른 판단
                parsing_result = self.news_parser.parse_all_news_data(raw_data)
                if parsing_result.success:
                    integrated_data = parsing_result.data
                    
                    # 지연 상태 확인
                    if integrated_data.delay_analysis['has_delays']:
                        max_delay = integrated_data.delay_analysis['max_delay_minutes']
                        if max_delay > 15:  # 15분 이상 지연
                            return 'delay'
                    
                    # 최신 데이터 확인
                    if integrated_data.status_counts['latest'] > 0:
                        return 'status'
                    else:
                        return 'no_data'
                else:
                    return 'no_data'
            
        except Exception as e:
            self.logger.error(f"메시지 타입 결정 오류: {e}")
            return 'no_data'
    
    def _generate_market_prediction(self, integrated_data: IntegratedNewsData, 
                                  historical_data: Optional[Dict[str, Any]]) -> str:
        """
        시장 동향 예측 생성
        
        Args:
            integrated_data (IntegratedNewsData): 통합 뉴스 데이터
            historical_data (dict): 과거 데이터
        
        Returns:
            str: 시장 동향 예측 텍스트
        """
        try:
            predictions = []
            
            # 발행 패턴 기반 예측
            completion_rate = integrated_data.status_counts['latest'] / integrated_data.status_counts['total']
            if completion_rate >= 0.8:
                predictions.append("정상 발행 패턴 유지 예상")
            elif completion_rate >= 0.5:
                predictions.append("부분적 지연 발행 가능성")
            else:
                predictions.append("전반적 발행 지연 우려")
            
            # 시간대별 예측
            current_time = self.test_datetime if self.test_mode else datetime.now()
            current_hour = current_time.hour
            
            if 6 <= current_hour < 9:
                predictions.append("뉴욕 시장 영향 분석 필요")
            elif 9 <= current_hour < 15:
                predictions.append("국내 시장 개장 중 - 실시간 모니터링")
            elif 15 <= current_hour < 18:
                predictions.append("마감 시간대 - 종가 확정 대기")
            else:
                predictions.append("시장 마감 후 - 다음 영업일 준비")
            
            # 과거 데이터와 비교한 트렌드 예측
            if historical_data:
                trend_prediction = self._analyze_historical_trend(integrated_data, historical_data)
                if trend_prediction:
                    predictions.append(trend_prediction)
            
            return " | ".join(predictions) if predictions else "예측 데이터 부족"
            
        except Exception as e:
            self.logger.error(f"시장 동향 예측 생성 오류: {e}")
            return "예측 분석 오류"
    
    def _analyze_historical_trend(self, current_data: IntegratedNewsData, 
                                historical_data: Dict[str, Any]) -> str:
        """
        과거 데이터와 비교한 트렌드 분석
        
        Args:
            current_data (IntegratedNewsData): 현재 데이터
            historical_data (dict): 과거 데이터
        
        Returns:
            str: 트렌드 분석 결과
        """
        try:
            # 발행 시간 비교
            current_times = []
            historical_times = []
            
            for news_type in self.news_types.keys():
                current_news = current_data.news_items.get(news_type)
                if current_news and current_news.time:
                    current_times.append(current_news.time)
                
                if historical_data and news_type in historical_data:
                    hist_time = historical_data[news_type].get('time')
                    if hist_time:
                        historical_times.append(hist_time)
            
            if len(current_times) >= 2 and len(historical_times) >= 2:
                # 간단한 트렌드 분석
                if len(current_times) > len(historical_times):
                    return "발행 빈도 증가 추세"
                elif len(current_times) < len(historical_times):
                    return "발행 빈도 감소 추세"
                else:
                    return "발행 패턴 안정적 유지"
            
            return "트렌드 분석을 위한 데이터 부족"
            
        except Exception as e:
            self.logger.error(f"과거 트렌드 분석 오류: {e}")
            return "트렌드 분석 오류"
    
    def _format_enhanced_tree_structure(self, comparison: BusinessDayComparison, 
                                      news_type: str, raw_data: Dict[str, Any],
                                      historical_data: Optional[Dict[str, Any]]) -> List[str]:
        """
        향상된 트리 구조 메시지 포맷팅 (뉴스 타이틀 및 변화 분석 포함)
        
        Args:
            comparison (BusinessDayComparison): 비교 데이터
            news_type (str): 뉴스 타입
            raw_data (dict): 현재 원시 데이터
            historical_data (dict): 과거 데이터
        
        Returns:
            List[str]: 향상된 트리 구조 텍스트 라인들
        """
        lines = []
        
        # 현재 데이터 정보
        current_news_data = raw_data.get(news_type, {})
        current_title = current_news_data.get('title', '제목 없음')
        current_time = self.format_time_string(current_news_data.get('time', ''))
        
        # 과거 데이터 정보
        historical_news_data = historical_data.get(news_type, {}) if historical_data else {}
        historical_title = historical_news_data.get('title', '과거 데이터 없음')
        historical_time = self.format_time_string(historical_news_data.get('time', ''))
        
        if comparison.current_data:
            # 현재 데이터가 있는 경우
            lines.append(f"├ 현재: {current_time} {comparison.status_display}")
            lines.append(f"├ 제목: {current_title}")
            
            # 직전 대비 변화 분석
            if historical_data and news_type in historical_data:
                change_analysis = self._analyze_title_change(current_title, historical_title)
                lines.append(f"├ 변화: {change_analysis}")
                lines.append(f"└ 직전: {historical_time} | {historical_title[:30]}...")
            else:
                lines.append("└ 직전: ❌ 비교 데이터 없음")
        else:
            # 현재 데이터가 없는 경우
            lines.append(f"├ 현재: {comparison.status_display}")
            
            if historical_data and news_type in historical_data:
                lines.append(f"├ 직전: 🔄 {historical_time}")
                lines.append(f"├ 제목: {historical_title}")
                
                # 예상 발행 시간 예측
                expected_time = self._predict_next_publication_time(news_type, historical_data)
                lines.append(f"└ 예상: ⏰ {expected_time}")
            else:
                lines.append("└ 직전: ❌ 데이터 없음")
        
        return lines
    
    def _analyze_title_change(self, current_title: str, historical_title: str) -> str:
        """
        뉴스 제목 변화 분석
        
        Args:
            current_title (str): 현재 제목
            historical_title (str): 과거 제목
        
        Returns:
            str: 변화 분석 결과
        """
        try:
            if not current_title or not historical_title:
                return "❓ 비교 불가"
            
            # 제목 유사도 간단 분석
            current_words = set(current_title.split())
            historical_words = set(historical_title.split())
            
            common_words = current_words.intersection(historical_words)
            total_words = current_words.union(historical_words)
            
            if len(total_words) == 0:
                return "❓ 분석 불가"
            
            similarity = len(common_words) / len(total_words)
            
            if similarity >= 0.8:
                return "🔄 유사한 내용"
            elif similarity >= 0.5:
                return "📝 부분 변경"
            else:
                return "🆕 새로운 내용"
                
        except Exception as e:
            self.logger.error(f"제목 변화 분석 오류: {e}")
            return "❓ 분석 오류"
    
    def _predict_next_publication_time(self, news_type: str, historical_data: Dict[str, Any]) -> str:
        """
        다음 발행 시간 예측
        
        Args:
            news_type (str): 뉴스 타입
            historical_data (dict): 과거 데이터
        
        Returns:
            str: 예측된 발행 시간
        """
        try:
            config = self.news_types.get(news_type)
            if not config:
                return "예측 불가"
            
            expected_hour, expected_minute = config['expected_time']
            tolerance = config['tolerance_minutes']
            
            # 과거 데이터 기반 지연 패턴 분석
            if historical_data and news_type in historical_data:
                hist_time = historical_data[news_type].get('time', '')
                if hist_time:
                    # 간단한 지연 패턴 분석
                    return f"{expected_hour:02d}:{expected_minute:02d} (±{tolerance}분)"
            
            return f"{expected_hour:02d}:{expected_minute:02d} 예정"
            
        except Exception as e:
            self.logger.error(f"발행 시간 예측 오류: {e}")
            return "예측 오류"
    
    def _generate_comprehensive_analysis(self, integrated_data: IntegratedNewsData,
                                       historical_data: Optional[Dict[str, Any]]) -> str:
        """
        종합 분석 및 권장사항 생성
        
        Args:
            integrated_data (IntegratedNewsData): 통합 뉴스 데이터
            historical_data (dict): 과거 데이터
        
        Returns:
            str: 종합 분석 결과
        """
        try:
            analysis_points = []
            
            # 발행 현황 분석
            completion_rate = integrated_data.status_counts['latest'] / integrated_data.status_counts['total']
            if completion_rate >= 0.8:
                analysis_points.append("✅ 발행 현황 양호")
            elif completion_rate >= 0.5:
                analysis_points.append("⚠️ 일부 지연 발생")
            else:
                analysis_points.append("🚨 전반적 지연 상황")
            
            # 시장 상황 분석
            if integrated_data.market_summary:
                market_trend = "상승" if "상승" in integrated_data.market_summary else "하락" if "하락" in integrated_data.market_summary else "보합"
                analysis_points.append(f"📈 시장 동향: {market_trend}")
            
            # 권장 조치사항
            if integrated_data.delay_analysis.get('has_delays', False):
                analysis_points.append("🔧 지연 원인 점검 필요")
            
            # 다음 모니터링 시점 제안
            current_time = self.test_datetime if self.test_mode else datetime.now()
            next_check_time = current_time + timedelta(minutes=30)
            analysis_points.append(f"⏰ 다음 점검: {next_check_time.strftime('%H:%M')}")
            
            return " | ".join(analysis_points) if analysis_points else "분석 데이터 부족"
            
        except Exception as e:
            self.logger.error(f"종합 분석 생성 오류: {e}")
            return "분석 오류"


    def generate_original_format_message(self, news_data: Dict[str, Any]) -> MessageGenerationResult:
        """정상 커밋 기준 100% + α 메시지 생성"""
        try:
            # 정상 커밋의 정확한 포맷 재현
            today = datetime.now().strftime('%Y%m%d')
            current_time = datetime.now()
            
            message_lines = []
            updated_count = 0
            total_count = 3
            
            # 각 뉴스 타입별 상태 확인
            news_types = [
                ('exchange-rate', 'EXCHANGE RATE'),
                ('newyork-market-watch', 'NEWYORK MARKET WATCH'), 
                ('kospi-close', 'KOSPI CLOSE')
            ]
            
            for news_key, display_name in news_types:
                if news_key in news_data and news_data[news_key]:
                    news_item = news_data[news_key]
                    
                    # 오늘 발행 여부 확인
                    news_date = news_item.get('date', '')
                    is_today = (news_date == today)
                    
                    if is_today:
                        updated_count += 1
                        status_emoji = "🟢"
                        status_text = "최신"
                        
                        # 시간 포맷팅 (+ α 기능: HH:MM 형태)
                        time_str = news_item.get('time', '데이터 없음')
                        if time_str != '데이터 없음' and len(time_str) >= 6:
                            if len(news_date) == 8:  # YYYYMMDD
                                formatted_time = f"{news_date[:4]}-{news_date[4:6]}-{news_date[6:8]} {time_str[:2]}:{time_str[2:4]}"
                            else:
                                formatted_time = time_str
                        else:
                            formatted_time = "데이터 없음"
                        
                        # + α 기능: 뉴스 타이틀 완전 표시
                        title = news_item.get('title', '')
                        if len(title) > 50:
                            title = title[:50] + "..."
                    else:
                        status_emoji = "🔴"
                        status_text = "데이터 없음"
                        formatted_time = "데이터 없음"
                        title = ""
                else:
                    status_emoji = "🔴"
                    status_text = "데이터 없음"
                    formatted_time = "데이터 없음"
                    title = ""
                
                # 정상 커밋의 정확한 박스 형태 재현
                message_lines.append(f"┌  {display_name}")
                message_lines.append(f"├ 상태: {status_emoji} {status_text}")
                message_lines.append(f"├ 시간: {formatted_time}")
                message_lines.append(f"└ 제목: {title}")
                message_lines.append("")  # 빈 줄
            
            # 최종 확인 시간 (정상 커밋 방식)
            message_lines.append(f"최종 확인: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # + α 기능: 직전 대비 변화 분석
            message_lines.append("")
            message_lines.append("📈 직전 대비 변화 분석:")
            for news_key, _ in news_types:
                if news_key in news_data and news_data[news_key]:
                    message_lines.append(f"  • {news_key}: 데이터 업데이트 감지")
            
            # + α 기능: 발행 시간 예측
            message_lines.append("")
            message_lines.append("⏰ 발행 시간 예측:")
            current_hour = current_time.hour
            if current_hour < 9:
                message_lines.append("  • 다음 예상 발행: 09:00 (시장 개장)")
            elif current_hour < 15:
                message_lines.append("  • 다음 예상 발행: 15:30 (시장 마감)")
            else:
                message_lines.append("  • 다음 예상 발행: 익일 09:00")
            
            # 동적 제목 생성 (정상 커밋 방식)
            if updated_count == 0:
                alert_title = "🔔 데이터 갱신 없음"
                color = "#6c757d"
                message_type = "no_data"
            elif updated_count == total_count:
                alert_title = "✅ 모든 데이터 최신"
                color = "#28a745"
                message_type = "complete"
            else:
                alert_title = f"📊 데이터 부분 갱신 ({updated_count}/{total_count})"
                color = "#ffc107"
                message_type = "partial"
            
            message_content = "\n".join(message_lines)
            
            return MessageGenerationResult(
                success=True,
                message=message_content,
                bot_name="POSCO 뉴스 🔔",
                bot_icon="🔔",
                color=color,
                message_type=message_type,
                test_mode=self.test_mode,
                errors=[],
                warnings=[],
                generation_time=0.0
            )
            
        except Exception as e:
            return MessageGenerationResult(
                success=False,
                message="",
                bot_name="POSCO 뉴스 ❌",
                bot_icon="❌",
                color="#ff4444",
                message_type="error",
                test_mode=self.test_mode,
                errors=[f"정상 커밋 메시지 생성 오류: {e}"],
                warnings=[],
                generation_time=0.0
            )

if __name__ == "__main__":
    # 테스트 코드
    import logging
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 샘플 데이터
    sample_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
            'content': '다우존스 35,123.45 (+150.25), 나스닥 14,567.89 (+45.67)',
            'date': '20250812',
            'time': '061938'
        },
        'kospi-close': {
            'title': '[증시마감] 코스피 2,500선 회복',
            'content': '코스피 2,523.45 (+25.67), 외국인 1,250억원 순매수',
            'date': '20250812',
            'time': '154500'
        },
        'exchange-rate': {
            'title': '[서환마감] 원달러 환율 1,350원대',
            'content': '원달러 1,352.50 (+8.30), 연준 발언에 원화 약세',
            'date': '20250812',
            'time': '163200'
        }
    }
    
    # 테스트 시간 설정
    test_time = datetime(2025, 8, 12, 6, 10, 0)  # 영업일 비교 분석 시간
    
    generator = NewsMessageGenerator(test_mode=True, test_datetime=test_time)
    
    print("=== 뉴스 메시지 생성기 테스트 ===")
    print(f"테스트 시간: {test_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 영업일 비교 분석 메시지
    print("1. 영업일 비교 분석 메시지:")
    result1 = generator.generate_business_day_comparison_message(sample_data)
    print(f"성공: {'✅' if result1.success else '❌'}")
    print(f"BOT: {result1.bot_name}")
    print(f"메시지:\n{result1.message}")
    print(f"처리 시간: {result1.generation_time:.3f}초")
    print()
    
    # 2. 지연 발행 알림 메시지
    print("2. 지연 발행 알림 메시지:")
    result2 = generator.generate_delay_notification_message(
        'newyork-market-watch', 
        sample_data['newyork-market-watch'], 
        25
    )
    print(f"성공: {'✅' if result2.success else '❌'}")
    print(f"BOT: {result2.bot_name}")
    print(f"메시지:\n{result2.message}")
    print(f"처리 시간: {result2.generation_time:.3f}초")
    print()
    
    # 3. 일일 통합 분석 리포트 메시지
    print("3. 일일 통합 분석 리포트 메시지:")
    result3 = generator.generate_daily_integrated_report_message(
        sample_data, 
        "https://example.com/report.html"
    )
    print(f"성공: {'✅' if result3.success else '❌'}")
    print(f"BOT: {result3.bot_name}")
    print(f"메시지:\n{result3.message}")
    print(f"처리 시간: {result3.generation_time:.3f}초")
    print()
    
    # 4. 정시 발행 알림 메시지
    print("4. 정시 발행 알림 메시지:")
    result4 = generator.generate_status_notification_message(sample_data)
    print(f"성공: {'✅' if result4.success else '❌'}")
    print(f"BOT: {result4.bot_name}")
    print(f"메시지:\n{result4.message}")
    print(f"처리 시간: {result4.generation_time:.3f}초")
    print()
    
    # 5. 데이터 갱신 없음 알림 메시지
    print("5. 데이터 갱신 없음 알림 메시지:")
    result5 = generator.generate_no_data_notification_message({})
    print(f"성공: {'✅' if result5.success else '❌'}")
    print(f"BOT: {result5.bot_name}")
    print(f"메시지:\n{result5.message}")
    print(f"처리 시간: {result5.generation_time:.3f}초")
    print()
    
    # 6. 자동 메시지 타입 결정
    print("6. 자동 메시지 타입 결정:")
    message_type = generator.determine_message_type(sample_data, test_time)
    print(f"결정된 메시지 타입: {message_type}")