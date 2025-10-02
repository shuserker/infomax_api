#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
캡처 이미지 기반 결과 검증 시스템

정상 커밋 a763ef84의 웹훅 메시지와 캡처 이미지를 완전 일치 검증하는 시스템입니다.

주요 기능:
- 생성된 웹훅 메시지와 캡처 이미지 완전 일치 검증
- 메시지 포맷, 이모지, 데이터 정확성 검증
- 시간 정보 및 상태 표시 정확성 확인
- BOT 타입 선택 로직 검증 (뉴스/오류/상태/테스트/비교)

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import os
import sys
import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

try:
    from recovery_config.news_message_generator import NewsMessageGenerator, MessageGenerationResult
    from recovery_config.webhook_sender import WebhookSender, BotType, MessagePriority
    from recovery_config.ai_analysis_engine import AIAnalysisEngine
    from recovery_config.integrated_news_parser import IntegratedNewsParser
except ImportError:
    from news_message_generator import NewsMessageGenerator, MessageGenerationResult
    from webhook_sender import WebhookSender, BotType, MessagePriority
    from ai_analysis_engine import AIAnalysisEngine
    from integrated_news_parser import IntegratedNewsParser


@dataclass
class CaptureReference:
    """캡처 이미지 참조 데이터"""
    capture_id: str
    bot_type: str
    bot_name: str
    title: str
    content_lines: List[str]
    timestamp: str
    color: str
    emojis: List[str]
    data_points: Dict[str, Any]
    format_patterns: List[str]


@dataclass
class VerificationResult:
    """검증 결과"""
    success: bool
    capture_id: str
    message_type: str
    verification_details: Dict[str, Any]
    match_score: float
    errors: List[str]
    warnings: List[str]
    verification_time: float


class CaptureVerificationSystem:
    """
    캡처 이미지 기반 결과 검증 시스템
    
    정상 커밋의 캡처 이미지와 생성된 메시지를 완전 일치 검증합니다.
    """
    
    def __init__(self, test_mode: bool = True):
        """
        검증 시스템 초기화
        
        Args:
            test_mode (bool): 테스트 모드 활성화 여부
        """
        self.logger = logging.getLogger(__name__)
        self.test_mode = test_mode
        
        # 캡처 참조 데이터 로드
        self.capture_references = self._load_capture_references()
        
        # 시스템 구성 요소 초기화
        self.message_generator = NewsMessageGenerator(test_mode=test_mode)
        self.webhook_sender = WebhookSender(test_mode=test_mode)
        self.ai_engine = AIAnalysisEngine()
        self.news_parser = IntegratedNewsParser()
        
        # 검증 통계
        self.verification_stats = {
            'total_verifications': 0,
            'successful_verifications': 0,
            'failed_verifications': 0,
            'average_match_score': 0.0,
            'last_verification_time': None
        }
        
        self.logger.info("캡처 이미지 기반 결과 검증 시스템 초기화 완료")
    
    def _load_capture_references(self) -> Dict[str, CaptureReference]:
        """캡처 참조 데이터 로드"""
        references = {}
        
        # 캡처 1: 영업일 비교 분석 (comparison)
        references['capture_1_comparison'] = CaptureReference(
            capture_id='capture_1_comparison',
            bot_type='comparison',
            bot_name='POSCO 뉴스 비교알림',
            title='📊 영업일 비교 분석',
            content_lines=[
                '📊 영업일 비교 분석',
                '',
                '[NEWYORK MARKET WATCH]',
                '├ 현재: 🟢 최신',
                '└ 제목: [뉴욕마켓워치] 미국 증시 상승 마감',
                '',
                '[KOSPI CLOSE]',
                '├ 현재: ⏳ 발행 전',
                '├ 직전: 🔄 15:40',
                '└ 제목: [코스피마감] 코스피 2,450.25 (+15.75)',
                '',
                '[EXCHANGE RATE]',
                '├ 현재: 🔴 발행 지연',
                '├ 직전: 🔄 15:30',
                '└ 제목: [환율] 달러/원 1,320.50 (+2.30)'
            ],
            timestamp='2025-08-12 06:10',
            color='#007bff',
            emojis=['📊', '🟢', '⏳', '🔄', '🔴', '├', '└'],
            data_points={
                'news_types': ['NEWYORK MARKET WATCH', 'KOSPI CLOSE', 'EXCHANGE RATE'],
                'status_types': ['최신', '발행 전', '발행 지연'],
                'tree_structure': True
            },
            format_patterns=[
                r'\[.*\]',  # 뉴스 타입 패턴
                r'├.*',     # 트리 구조 패턴
                r'└.*'      # 트리 구조 패턴
            ]
        )
        
        # 캡처 2: 지연 발행 알림 (delay)
        references['capture_2_delay'] = CaptureReference(
            capture_id='capture_2_delay',
            bot_type='delay',
            bot_name='POSCO 뉴스 ⏰',
            title='🟡 kospi-close 지연 발행',
            content_lines=[
                '🟡 kospi-close 지연 발행',
                '',
                '📅 발행 시간: 2025-08-12 16:25:00',
                '📊 패턴 분석: ⏱️ 45분 지연 발행 (16:25)',
                '⏰ 예상: 15:40 → 실제: 16:25',
                '📋 제목: [코스피마감] 코스피 2,450.25 (+15.75)',
                '',
                '🔔 지연 알림이 초기화되었습니다.'
            ],
            timestamp='2025-08-12 16:25',
            color='#ffc107',
            emojis=['🟡', '📅', '📊', '⏱️', '⏰', '📋', '🔔'],
            data_points={
                'news_type': 'kospi-close',
                'delay_minutes': 45,
                'expected_time': '15:40',
                'actual_time': '16:25'
            },
            format_patterns=[
                r'📅 발행 시간: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                r'📊 패턴 분석: ⏱️ \d+분 지연 발행',
                r'⏰ 예상: \d{2}:\d{2} → 실제: \d{2}:\d{2}'
            ]
        )
        
        # 캡처 3: 일일 통합 분석 리포트 (report)
        references['capture_3_report'] = CaptureReference(
            capture_id='capture_3_report',
            bot_type='report',
            bot_name='POSCO 뉴스 📊',
            title='📊 일일 통합 분석 리포트',
            content_lines=[
                '📊 일일 통합 분석 리포트',
                '',
                '📅 분석 일자: 2025년 08월 12일',
                '📊 발행 현황: 2/3개 완료',
                '',
                '📋 뉴스별 발행 현황:',
                '  🌆 NEWYORK MARKET WATCH: ✅ 발행 완료 (06:30)',
                '  📈 KOSPI CLOSE: ✅ 발행 완료 (15:40)',
                '  💱 EXCHANGE RATE: ⏳ 발행 대기 (미발행)',
                '',
                '📈 시장 요약:',
                '  전체적으로 상승세를 보이고 있습니다',
                '',
                '💡 권장사항:',
                '  1. 성장주 비중 확대 검토',
                '  2. 환율 변동 모니터링 강화',
                '  3. 포트폴리오 리밸런싱 검토',
                '',
                '🕐 생성 시간: 18:00:00'
            ],
            timestamp='2025-08-12 18:00',
            color='#28a745',
            emojis=['📊', '📅', '📋', '🌆', '📈', '💱', '✅', '⏳', '💡', '🕐'],
            data_points={
                'completion_rate': '2/3',
                'analysis_date': '2025년 08월 12일',
                'recommendations_count': 3
            },
            format_patterns=[
                r'📅 분석 일자: \d{4}년 \d{2}월 \d{2}일',
                r'📊 발행 현황: \d+/\d+개 완료',
                r'🕐 생성 시간: \d{2}:\d{2}:\d{2}'
            ]
        )
        
        # 캡처 4: 정시 발행 알림 (status)
        references['capture_4_status'] = CaptureReference(
            capture_id='capture_4_status',
            bot_type='status',
            bot_name='POSCO 뉴스 ✅',
            title='✅ 정시 발행 알림',
            content_lines=[
                '✅ 정시 발행 알림',
                '',
                '📅 확인 시간: 2025-08-12 15:00:00',
                '',
                '📊 현재 발행 상태:',
                '  🌆 NEWYORK MARKET WATCH: ✅ 최신 (06:30)',
                '  📈 KOSPI CLOSE: ⏳ 발행 전',
                '  💱 EXCHANGE RATE: ⏳ 발행 전',
                '',
                '🟢 전체 상태: 일부 뉴스 최신 상태',
                '',
                '🔔 정시 상태 확인이 완료되었습니다.'
            ],
            timestamp='2025-08-12 15:00',
            color='#17a2b8',
            emojis=['✅', '📅', '📊', '🌆', '📈', '💱', '⏳', '🟢', '🔔'],
            data_points={
                'check_time': '2025-08-12 15:00:00',
                'status_summary': '일부 뉴스 최신 상태'
            },
            format_patterns=[
                r'📅 확인 시간: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                r'🟢 전체 상태: .*'
            ]
        )
        
        # 캡처 5: 데이터 갱신 없음 알림 (no_data)
        references['capture_5_no_data'] = CaptureReference(
            capture_id='capture_5_no_data',
            bot_type='no_data',
            bot_name='POSCO 뉴스 🔔',
            title='🔔 데이터 갱신 없음',
            content_lines=[
                '🔔 데이터 갱신 없음',
                '',
                '📅 확인 시간: 2025-08-12 12:30:00',
                '',
                '📊 마지막 확인 상태:',
                '  🌆 NEWYORK MARKET WATCH: 마지막 데이터 06:30',
                '  📈 KOSPI CLOSE: 데이터 없음',
                '  💱 EXCHANGE RATE: 데이터 없음',
                '',
                '⏳ 새로운 뉴스 발행을 대기 중입니다.',
                '🔄 다음 확인까지 5분 대기합니다.'
            ],
            timestamp='2025-08-12 12:30',
            color='#6c757d',
            emojis=['🔔', '📅', '📊', '🌆', '📈', '💱', '⏳', '🔄'],
            data_points={
                'check_time': '2025-08-12 12:30:00',
                'wait_minutes': 5
            },
            format_patterns=[
                r'📅 확인 시간: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                r'🔄 다음 확인까지 \d+분 대기합니다'
            ]
        )
        
        self.logger.info(f"캡처 참조 데이터 {len(references)}개 로드 완료")
        return references
    
    def verify_business_day_comparison_message(self, raw_data: Dict[str, Any], 
                                             historical_data: Optional[Dict[str, Any]] = None) -> VerificationResult:
        """영업일 비교 분석 메시지 검증"""
        start_time = time.time()
        capture_ref = self.capture_references['capture_1_comparison']
        
        try:
            self.logger.info("영업일 비교 분석 메시지 검증 시작")
            
            # 메시지 생성
            generation_result = self.message_generator.generate_business_day_comparison_message(
                raw_data, historical_data
            )
            
            if not generation_result.success:
                return self._create_failed_result(
                    capture_ref.capture_id, 'comparison', 
                    ["메시지 생성 실패"] + generation_result.errors, 
                    start_time
                )
            
            # 검증 수행
            verification_details = self._verify_message_against_capture(
                generation_result, capture_ref
            )
            
            # 결과 생성
            return self._create_verification_result(
                capture_ref.capture_id, 'comparison', verification_details, start_time
            )
            
        except Exception as e:
            self.logger.error(f"영업일 비교 분석 메시지 검증 오류: {e}")
            return self._create_failed_result(
                capture_ref.capture_id, 'comparison', [f"검증 오류: {e}"], start_time
            )
    
    def verify_delay_notification_message(self, news_type: str, current_data: Dict[str, Any], 
                                        delay_minutes: int) -> VerificationResult:
        """지연 발행 알림 메시지 검증"""
        start_time = time.time()
        capture_ref = self.capture_references['capture_2_delay']
        
        try:
            self.logger.info(f"{news_type} 지연 발행 알림 메시지 검증 시작")
            
            # 메시지 생성
            generation_result = self.message_generator.generate_delay_notification_message(
                news_type, current_data, delay_minutes
            )
            
            if not generation_result.success:
                return self._create_failed_result(
                    capture_ref.capture_id, 'delay', 
                    ["메시지 생성 실패"] + generation_result.errors, 
                    start_time
                )
            
            # 검증 수행
            verification_details = self._verify_message_against_capture(
                generation_result, capture_ref
            )
            
            # 지연 시간 특별 검증
            verification_details['delay_verification'] = self._verify_delay_specific_content(
                generation_result.message, delay_minutes, news_type
            )
            
            # 결과 생성
            return self._create_verification_result(
                capture_ref.capture_id, 'delay', verification_details, start_time
            )
            
        except Exception as e:
            self.logger.error(f"{news_type} 지연 발행 알림 메시지 검증 오류: {e}")
            return self._create_failed_result(
                capture_ref.capture_id, 'delay', [f"검증 오류: {e}"], start_time
            )
    
    def verify_daily_integrated_report_message(self, raw_data: Dict[str, Any], 
                                             report_url: Optional[str] = None) -> VerificationResult:
        """일일 통합 분석 리포트 메시지 검증"""
        start_time = time.time()
        capture_ref = self.capture_references['capture_3_report']
        
        try:
            self.logger.info("일일 통합 분석 리포트 메시지 검증 시작")
            
            # 메시지 생성
            generation_result = self.message_generator.generate_daily_integrated_report_message(
                raw_data, report_url
            )
            
            if not generation_result.success:
                return self._create_failed_result(
                    capture_ref.capture_id, 'report', 
                    ["메시지 생성 실패"] + generation_result.errors, 
                    start_time
                )
            
            # 검증 수행
            verification_details = self._verify_message_against_capture(
                generation_result, capture_ref
            )
            
            # 리포트 특별 검증
            verification_details['report_verification'] = self._verify_report_specific_content(
                generation_result.message, raw_data
            )
            
            # 결과 생성
            return self._create_verification_result(
                capture_ref.capture_id, 'report', verification_details, start_time
            )
            
        except Exception as e:
            self.logger.error(f"일일 통합 분석 리포트 메시지 검증 오류: {e}")
            return self._create_failed_result(
                capture_ref.capture_id, 'report', [f"검증 오류: {e}"], start_time
            )
    
    def verify_status_notification_message(self, raw_data: Dict[str, Any]) -> VerificationResult:
        """정시 발행 알림 메시지 검증"""
        start_time = time.time()
        capture_ref = self.capture_references['capture_4_status']
        
        try:
            self.logger.info("정시 발행 알림 메시지 검증 시작")
            
            # 메시지 생성
            generation_result = self.message_generator.generate_status_notification_message(raw_data)
            
            if not generation_result.success:
                return self._create_failed_result(
                    capture_ref.capture_id, 'status', 
                    ["메시지 생성 실패"] + generation_result.errors, 
                    start_time
                )
            
            # 검증 수행
            verification_details = self._verify_message_against_capture(
                generation_result, capture_ref
            )
            
            # 상태 특별 검증
            verification_details['status_verification'] = self._verify_status_specific_content(
                generation_result.message, raw_data
            )
            
            # 결과 생성
            return self._create_verification_result(
                capture_ref.capture_id, 'status', verification_details, start_time
            )
            
        except Exception as e:
            self.logger.error(f"정시 발행 알림 메시지 검증 오류: {e}")
            return self._create_failed_result(
                capture_ref.capture_id, 'status', [f"검증 오류: {e}"], start_time
            )
    
    def verify_no_data_notification_message(self, raw_data: Dict[str, Any]) -> VerificationResult:
        """데이터 갱신 없음 알림 메시지 검증"""
        start_time = time.time()
        capture_ref = self.capture_references['capture_5_no_data']
        
        try:
            self.logger.info("데이터 갱신 없음 알림 메시지 검증 시작")
            
            # 메시지 생성
            generation_result = self.message_generator.generate_no_data_notification_message(raw_data)
            
            if not generation_result.success:
                return self._create_failed_result(
                    capture_ref.capture_id, 'no_data', 
                    ["메시지 생성 실패"] + generation_result.errors, 
                    start_time
                )
            
            # 검증 수행
            verification_details = self._verify_message_against_capture(
                generation_result, capture_ref
            )
            
            # 결과 생성
            return self._create_verification_result(
                capture_ref.capture_id, 'no_data', verification_details, start_time
            )
            
        except Exception as e:
            self.logger.error(f"데이터 갱신 없음 알림 메시지 검증 오류: {e}")
            return self._create_failed_result(
                capture_ref.capture_id, 'no_data', [f"검증 오류: {e}"], start_time
            )
    
    def _verify_message_against_capture(self, generation_result: MessageGenerationResult, 
                                      capture_ref: CaptureReference) -> Dict[str, Any]:
        """메시지와 캡처 참조 데이터 비교 검증"""
        verification_details = {
            'bot_verification': {},
            'format_verification': {},
            'content_verification': {},
            'emoji_verification': {},
            'pattern_verification': {},
            'overall_match_score': 0.0
        }
        
        # BOT 정보 검증
        verification_details['bot_verification'] = self._verify_bot_info(
            generation_result, capture_ref
        )
        
        # 메시지 포맷 검증
        verification_details['format_verification'] = self._verify_message_format(
            generation_result.message, capture_ref
        )
        
        # 콘텐츠 검증
        verification_details['content_verification'] = self._verify_content_accuracy(
            generation_result.message, capture_ref
        )
        
        # 이모지 검증
        verification_details['emoji_verification'] = self._verify_emoji_usage(
            generation_result.message, capture_ref
        )
        
        # 패턴 검증
        verification_details['pattern_verification'] = self._verify_format_patterns(
            generation_result.message, capture_ref
        )
        
        # 전체 매치 점수 계산
        verification_details['overall_match_score'] = self._calculate_overall_match_score(
            verification_details
        )
        
        return verification_details
    
    def _verify_bot_info(self, generation_result: MessageGenerationResult, 
                        capture_ref: CaptureReference) -> Dict[str, Any]:
        """BOT 정보 검증"""
        bot_verification = {
            'bot_name_match': False,
            'bot_type_match': False,
            'color_match': False,
            'test_mode_handled': False,
            'score': 0.0
        }
        
        # BOT 이름 검증 (테스트 모드 고려)
        expected_bot_name = capture_ref.bot_name
        if generation_result.test_mode:
            expected_bot_name = f"[TEST] {expected_bot_name}"
        
        bot_verification['bot_name_match'] = generation_result.bot_name == expected_bot_name
        
        # BOT 타입 검증
        bot_verification['bot_type_match'] = generation_result.message_type == capture_ref.bot_type
        
        # 색상 검증
        bot_verification['color_match'] = generation_result.color == capture_ref.color
        
        # 테스트 모드 처리 검증
        bot_verification['test_mode_handled'] = (
            generation_result.test_mode == self.test_mode
        )
        
        # 점수 계산
        matches = sum([
            bot_verification['bot_name_match'],
            bot_verification['bot_type_match'],
            bot_verification['color_match'],
            bot_verification['test_mode_handled']
        ])
        bot_verification['score'] = matches / 4.0
        
        return bot_verification
    
    def _verify_message_format(self, message: str, capture_ref: CaptureReference) -> Dict[str, Any]:
        """메시지 포맷 검증"""
        format_verification = {
            'line_structure_match': False,
            'title_format_match': False,
            'section_structure_match': False,
            'score': 0.0
        }
        
        message_lines = message.split('\n')
        
        # 제목 포맷 검증
        if message_lines and capture_ref.title in message_lines[0]:
            format_verification['title_format_match'] = True
        
        # 섹션 구조 검증 (빈 줄 포함)
        expected_sections = len([line for line in capture_ref.content_lines if line.strip()])
        actual_sections = len([line for line in message_lines if line.strip()])
        
        if abs(expected_sections - actual_sections) <= 2:  # 2줄 이내 차이 허용
            format_verification['section_structure_match'] = True
        
        # 라인 구조 검증
        if len(message_lines) >= len(capture_ref.content_lines) * 0.8:  # 80% 이상 매치
            format_verification['line_structure_match'] = True
        
        # 점수 계산
        matches = sum([
            format_verification['line_structure_match'],
            format_verification['title_format_match'],
            format_verification['section_structure_match']
        ])
        format_verification['score'] = matches / 3.0
        
        return format_verification
    
    def _verify_content_accuracy(self, message: str, capture_ref: CaptureReference) -> Dict[str, Any]:
        """콘텐츠 정확성 검증"""
        content_verification = {
            'key_data_points_match': False,
            'time_format_match': False,
            'data_accuracy_match': False,
            'score': 0.0
        }
        
        # 주요 데이터 포인트 검증
        data_points_found = 0
        total_data_points = len(capture_ref.data_points)
        
        for key, expected_value in capture_ref.data_points.items():
            if isinstance(expected_value, str) and expected_value in message:
                data_points_found += 1
            elif isinstance(expected_value, (int, float)) and str(expected_value) in message:
                data_points_found += 1
            elif isinstance(expected_value, list):
                # 리스트의 경우 일부 요소가 포함되어 있는지 확인
                found_items = sum(1 for item in expected_value if str(item) in message)
                if found_items >= len(expected_value) * 0.5:  # 50% 이상 매치
                    data_points_found += 1
        
        if total_data_points > 0:
            content_verification['key_data_points_match'] = (
                data_points_found / total_data_points >= 0.7  # 70% 이상 매치
            )
        
        # 시간 포맷 검증
        time_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{4}년 \d{2}월 \d{2}일',              # YYYY년 MM월 DD일
            r'\d{2}:\d{2}:\d{2}',                    # HH:MM:SS
            r'\d{2}:\d{2}'                           # HH:MM
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, message):
                content_verification['time_format_match'] = True
                break
        
        # 데이터 정확성 검증 (숫자, 상태 등)
        accuracy_indicators = ['최신', '지연', '발행', '완료', '대기', '오류']
        found_indicators = sum(1 for indicator in accuracy_indicators if indicator in message)
        content_verification['data_accuracy_match'] = found_indicators >= 2
        
        # 점수 계산
        matches = sum([
            content_verification['key_data_points_match'],
            content_verification['time_format_match'],
            content_verification['data_accuracy_match']
        ])
        content_verification['score'] = matches / 3.0
        
        return content_verification
    
    def _verify_emoji_usage(self, message: str, capture_ref: CaptureReference) -> Dict[str, Any]:
        """이모지 사용 검증"""
        emoji_verification = {
            'required_emojis_present': False,
            'emoji_count_appropriate': False,
            'emoji_context_correct': False,
            'score': 0.0
        }
        
        # 필수 이모지 존재 확인
        required_emojis_found = sum(1 for emoji in capture_ref.emojis if emoji in message)
        emoji_verification['required_emojis_present'] = (
            required_emojis_found >= len(capture_ref.emojis) * 0.7  # 70% 이상
        )
        
        # 이모지 개수 적절성 확인
        total_emojis_in_message = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]', message))
        expected_emoji_count = len(capture_ref.emojis)
        
        if abs(total_emojis_in_message - expected_emoji_count) <= expected_emoji_count * 0.3:  # 30% 이내 차이
            emoji_verification['emoji_count_appropriate'] = True
        
        # 이모지 컨텍스트 정확성 (특정 이모지가 적절한 위치에 있는지)
        context_checks = [
            ('📊', '분석'),
            ('✅', '완료'),
            ('⏳', '대기'),
            ('🔔', '알림'),
            ('🟢', '정상'),
            ('🔴', '지연')
        ]
        
        correct_contexts = 0
        for emoji, context in context_checks:
            if emoji in message and context in message:
                correct_contexts += 1
        
        emoji_verification['emoji_context_correct'] = correct_contexts >= len(context_checks) * 0.5
        
        # 점수 계산
        matches = sum([
            emoji_verification['required_emojis_present'],
            emoji_verification['emoji_count_appropriate'],
            emoji_verification['emoji_context_correct']
        ])
        emoji_verification['score'] = matches / 3.0
        
        return emoji_verification
    
    def _verify_format_patterns(self, message: str, capture_ref: CaptureReference) -> Dict[str, Any]:
        """포맷 패턴 검증"""
        pattern_verification = {
            'patterns_matched': 0,
            'total_patterns': len(capture_ref.format_patterns),
            'pattern_match_rate': 0.0,
            'score': 0.0
        }
        
        # 각 패턴 검증
        for pattern in capture_ref.format_patterns:
            if re.search(pattern, message):
                pattern_verification['patterns_matched'] += 1
        
        # 매치율 계산
        if pattern_verification['total_patterns'] > 0:
            pattern_verification['pattern_match_rate'] = (
                pattern_verification['patterns_matched'] / pattern_verification['total_patterns']
            )
        
        # 점수는 매치율과 동일
        pattern_verification['score'] = pattern_verification['pattern_match_rate']
        
        return pattern_verification
    
    def _verify_delay_specific_content(self, message: str, delay_minutes: int, news_type: str) -> Dict[str, Any]:
        """지연 알림 특별 검증"""
        delay_verification = {
            'delay_minutes_correct': False,
            'news_type_correct': False,
            'delay_status_correct': False,
            'score': 0.0
        }
        
        # 지연 시간 검증
        delay_verification['delay_minutes_correct'] = str(delay_minutes) in message
        
        # 뉴스 타입 검증
        delay_verification['news_type_correct'] = news_type in message
        
        # 지연 상태 표시 검증
        delay_status_indicators = ['🟡', '🟠', '🔴', '지연']
        delay_verification['delay_status_correct'] = any(
            indicator in message for indicator in delay_status_indicators
        )
        
        # 점수 계산
        matches = sum([
            delay_verification['delay_minutes_correct'],
            delay_verification['news_type_correct'],
            delay_verification['delay_status_correct']
        ])
        delay_verification['score'] = matches / 3.0
        
        return delay_verification
    
    def _verify_report_specific_content(self, message: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """리포트 특별 검증"""
        report_verification = {
            'completion_rate_present': False,
            'news_status_detailed': False,
            'recommendations_present': False,
            'score': 0.0
        }
        
        # 완료율 정보 검증
        completion_patterns = [r'\d+/\d+개 완료', r'\d+/\d+']
        report_verification['completion_rate_present'] = any(
            re.search(pattern, message) for pattern in completion_patterns
        )
        
        # 뉴스별 상세 상태 검증
        news_types = ['NEWYORK MARKET WATCH', 'KOSPI CLOSE', 'EXCHANGE RATE']
        detailed_status_count = sum(1 for news_type in news_types if news_type in message)
        report_verification['news_status_detailed'] = detailed_status_count >= 2
        
        # 권장사항 존재 검증
        recommendation_indicators = ['권장사항', '💡', '1.', '2.', '3.']
        report_verification['recommendations_present'] = any(
            indicator in message for indicator in recommendation_indicators
        )
        
        # 점수 계산
        matches = sum([
            report_verification['completion_rate_present'],
            report_verification['news_status_detailed'],
            report_verification['recommendations_present']
        ])
        report_verification['score'] = matches / 3.0
        
        return report_verification
    
    def _verify_status_specific_content(self, message: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """상태 알림 특별 검증"""
        status_verification = {
            'current_status_present': False,
            'overall_status_summary': False,
            'confirmation_message': False,
            'score': 0.0
        }
        
        # 현재 상태 정보 검증
        status_indicators = ['현재 발행 상태', '✅', '⏳', '🔴']
        status_verification['current_status_present'] = any(
            indicator in message for indicator in status_indicators
        )
        
        # 전체 상태 요약 검증
        summary_patterns = ['전체 상태:', '🟢', '🟡', '🔴']
        status_verification['overall_status_summary'] = any(
            pattern in message for pattern in summary_patterns
        )
        
        # 확인 완료 메시지 검증
        confirmation_indicators = ['확인이 완료', '🔔']
        status_verification['confirmation_message'] = any(
            indicator in message for indicator in confirmation_indicators
        )
        
        # 점수 계산
        matches = sum([
            status_verification['current_status_present'],
            status_verification['overall_status_summary'],
            status_verification['confirmation_message']
        ])
        status_verification['score'] = matches / 3.0
        
        return status_verification
    
    def _calculate_overall_match_score(self, verification_details: Dict[str, Any]) -> float:
        """전체 매치 점수 계산"""
        # 각 검증 영역별 가중치
        weights = {
            'bot_verification': 0.2,
            'format_verification': 0.2,
            'content_verification': 0.3,
            'emoji_verification': 0.15,
            'pattern_verification': 0.15
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for area, weight in weights.items():
            if area in verification_details and 'score' in verification_details[area]:
                total_score += verification_details[area]['score'] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _create_verification_result(self, capture_id: str, message_type: str, 
                                  verification_details: Dict[str, Any], 
                                  start_time: float) -> VerificationResult:
        """검증 결과 생성"""
        match_score = verification_details.get('overall_match_score', 0.0)
        success = match_score >= 0.8  # 80% 이상 매치 시 성공
        
        # 통계 업데이트
        self.verification_stats['total_verifications'] += 1
        if success:
            self.verification_stats['successful_verifications'] += 1
        else:
            self.verification_stats['failed_verifications'] += 1
        
        # 평균 매치 점수 업데이트
        if self.verification_stats['average_match_score'] == 0.0:
            self.verification_stats['average_match_score'] = match_score
        else:
            self.verification_stats['average_match_score'] = (
                self.verification_stats['average_match_score'] * 0.9 + match_score * 0.1
            )
        
        self.verification_stats['last_verification_time'] = datetime.now()
        
        return VerificationResult(
            success=success,
            capture_id=capture_id,
            message_type=message_type,
            verification_details=verification_details,
            match_score=match_score,
            errors=[],
            warnings=[] if success else ["매치 점수가 기준치(80%) 미만입니다"],
            verification_time=time.time() - start_time
        )
    
    def _create_failed_result(self, capture_id: str, message_type: str, 
                            errors: List[str], start_time: float) -> VerificationResult:
        """실패 결과 생성"""
        self.verification_stats['total_verifications'] += 1
        self.verification_stats['failed_verifications'] += 1
        self.verification_stats['last_verification_time'] = datetime.now()
        
        return VerificationResult(
            success=False,
            capture_id=capture_id,
            message_type=message_type,
            verification_details={},
            match_score=0.0,
            errors=errors,
            warnings=[],
            verification_time=time.time() - start_time
        )
    
    def run_comprehensive_verification(self, test_data: Dict[str, Any]) -> Dict[str, VerificationResult]:
        """종합 검증 실행"""
        self.logger.info("종합 검증 시작")
        
        results = {}
        
        # 1. 영업일 비교 분석 검증
        try:
            results['comparison'] = self.verify_business_day_comparison_message(
                test_data.get('raw_data', {}),
                test_data.get('historical_data')
            )
        except Exception as e:
            self.logger.error(f"영업일 비교 분석 검증 실패: {e}")
        
        # 2. 지연 발행 알림 검증
        try:
            results['delay'] = self.verify_delay_notification_message(
                'kospi-close',
                test_data.get('delay_data', {}),
                45
            )
        except Exception as e:
            self.logger.error(f"지연 발행 알림 검증 실패: {e}")
        
        # 3. 일일 통합 리포트 검증
        try:
            results['report'] = self.verify_daily_integrated_report_message(
                test_data.get('raw_data', {})
            )
        except Exception as e:
            self.logger.error(f"일일 통합 리포트 검증 실패: {e}")
        
        # 4. 정시 발행 알림 검증
        try:
            results['status'] = self.verify_status_notification_message(
                test_data.get('raw_data', {})
            )
        except Exception as e:
            self.logger.error(f"정시 발행 알림 검증 실패: {e}")
        
        # 5. 데이터 갱신 없음 알림 검증
        try:
            results['no_data'] = self.verify_no_data_notification_message(
                test_data.get('empty_data', {})
            )
        except Exception as e:
            self.logger.error(f"데이터 갱신 없음 알림 검증 실패: {e}")
        
        self.logger.info(f"종합 검증 완료: {len(results)}개 검증 수행")
        return results
    
    def get_verification_statistics(self) -> Dict[str, Any]:
        """검증 통계 조회"""
        stats = self.verification_stats.copy()
        
        # 성공률 계산
        if stats['total_verifications'] > 0:
            stats['success_rate'] = stats['successful_verifications'] / stats['total_verifications']
            stats['failure_rate'] = stats['failed_verifications'] / stats['total_verifications']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        return stats
    
    def generate_verification_report(self, results: Dict[str, VerificationResult]) -> str:
        """검증 리포트 생성"""
        report_lines = [
            "📊 캡처 이미지 기반 결과 검증 리포트",
            "=" * 50,
            f"검증 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"총 검증 수: {len(results)}개",
            ""
        ]
        
        # 각 검증 결과 요약
        successful_count = sum(1 for result in results.values() if result.success)
        report_lines.extend([
            f"✅ 성공: {successful_count}개",
            f"❌ 실패: {len(results) - successful_count}개",
            f"📈 전체 성공률: {successful_count / len(results) * 100:.1f}%",
            ""
        ])
        
        # 상세 결과
        report_lines.append("📋 상세 검증 결과:")
        for message_type, result in results.items():
            status_icon = "✅" if result.success else "❌"
            report_lines.extend([
                f"{status_icon} {message_type.upper()}:",
                f"  • 매치 점수: {result.match_score:.3f}",
                f"  • 검증 시간: {result.verification_time:.3f}초",
                f"  • 캡처 ID: {result.capture_id}",
                ""
            ])
        
        # 통계 정보
        stats = self.get_verification_statistics()
        report_lines.extend([
            "📊 전체 통계:",
            f"  • 총 검증 수행: {stats['total_verifications']}회",
            f"  • 평균 매치 점수: {stats['average_match_score']:.3f}",
            f"  • 전체 성공률: {stats['success_rate']:.1%}",
            ""
        ])
        
        return "\n".join(report_lines)


if __name__ == "__main__":
    # 테스트 코드
    import logging
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 검증 시스템 생성
    verification_system = CaptureVerificationSystem(test_mode=True)
    
    # 테스트 데이터
    test_data = {
        'raw_data': {
            'newyork-market-watch': {
                'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
                'content': '다우존스 35,123.45 (+150.25)',
                'time': '06:30'
            },
            'kospi-close': {
                'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
                'content': '코스피 지수 상승 마감',
                'time': '15:40'
            }
        },
        'delay_data': {
            'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
            'time': '16:25'
        },
        'empty_data': {}
    }
    
    # 종합 검증 실행
    results = verification_system.run_comprehensive_verification(test_data)
    
    # 리포트 생성
    report = verification_system.generate_verification_report(results)
    print(report)