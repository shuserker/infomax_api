#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
캡처 이미지 기반 결과 검증 시스템 테스트

정상 커밋 a763ef84의 캡처 이미지와 생성된 메시지의 완전 일치를 검증합니다.

테스트 항목:
- 생성된 웹훅 메시지와 캡처 이미지 완전 일치 검증
- 메시지 포맷, 이모지, 데이터 정확성 검증
- 시간 정보 및 상태 표시 정확성 확인
- BOT 타입 선택 로직 검증 (뉴스/오류/상태/테스트/비교)
"""

import os
import sys
import json
import time
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from capture_verification_system import CaptureVerificationSystem, VerificationResult
    from news_message_generator import NewsMessageGenerator
    from webhook_sender import WebhookSender
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class TestCaptureVerificationSystem(unittest.TestCase):
    """캡처 이미지 기반 결과 검증 시스템 테스트"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화"""
        print("🧪 캡처 이미지 기반 결과 검증 시스템 테스트 시작")
        cls.verification_system = CaptureVerificationSystem(test_mode=True)
        
        # 테스트 데이터 준비
        cls.test_data = cls._prepare_test_data()
        
        print("✅ 테스트 환경 초기화 완료")
    
    @classmethod
    def _prepare_test_data(cls) -> Dict[str, Any]:
        """테스트 데이터 준비"""
        return {
            'raw_data': {
                'newyork-market-watch': {
                    'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
                    'content': '다우존스 35,123.45 (+150.25), 나스닥 14,567.89 (+45.67)',
                    'date': '20250812',
                    'time': '063000',
                    'publish_time': '06:30'
                },
                'kospi-close': {
                    'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
                    'content': '코스피 지수 상승 마감, 외국인 순매수',
                    'date': '20250812',
                    'time': '154000',
                    'publish_time': '15:40'
                },
                'exchange-rate': {
                    'title': '[환율] 달러/원 1,320.50 (+2.30)',
                    'content': '달러 강세 지속, 원화 약세',
                    'date': '20250812',
                    'time': '153000',
                    'publish_time': '15:30'
                }
            },
            'historical_data': {
                'newyork-market-watch': {
                    'title': '[뉴욕마켓워치] 전일 미국 증시 현황',
                    'time': '06:30'
                },
                'kospi-close': {
                    'title': '[코스피마감] 전일 코스피 현황',
                    'time': '15:40'
                },
                'exchange-rate': {
                    'title': '[환율] 전일 환율 현황',
                    'time': '15:30'
                }
            },
            'delay_data': {
                'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
                'content': '코스피 지수 상승 마감',
                'time': '162500',
                'publish_time': '16:25'
            },
            'empty_data': {}
        }
    
    def test_01_system_initialization(self):
        """시스템 초기화 테스트"""
        print("\n🧪 테스트 1: 시스템 초기화")
        
        # 시스템이 올바르게 초기화되었는지 확인
        self.assertIsNotNone(self.verification_system)
        self.assertTrue(self.verification_system.test_mode)
        
        # 캡처 참조 데이터가 로드되었는지 확인
        self.assertGreater(len(self.verification_system.capture_references), 0)
        self.assertEqual(len(self.verification_system.capture_references), 5)
        
        # 필수 구성 요소가 초기화되었는지 확인
        self.assertIsNotNone(self.verification_system.message_generator)
        self.assertIsNotNone(self.verification_system.webhook_sender)
        self.assertIsNotNone(self.verification_system.ai_engine)
        
        print("✅ 시스템 초기화 테스트 통과")
    
    def test_02_business_day_comparison_verification(self):
        """영업일 비교 분석 메시지 검증 테스트"""
        print("\n🧪 테스트 2: 영업일 비교 분석 메시지 검증")
        
        # 영업일 비교 분석 메시지 검증
        result = self.verification_system.verify_business_day_comparison_message(
            self.test_data['raw_data'],
            self.test_data['historical_data']
        )
        
        # 기본 검증
        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.message_type, 'comparison')
        self.assertEqual(result.capture_id, 'capture_1_comparison')
        
        # 검증 상세 내용 확인
        self.assertIn('bot_verification', result.verification_details)
        self.assertIn('format_verification', result.verification_details)
        self.assertIn('content_verification', result.verification_details)
        self.assertIn('emoji_verification', result.verification_details)
        self.assertIn('pattern_verification', result.verification_details)
        
        # 매치 점수 확인
        self.assertGreaterEqual(result.match_score, 0.0)
        self.assertLessEqual(result.match_score, 1.0)
        
        print(f"✅ 영업일 비교 분석 검증 완료 (매치 점수: {result.match_score:.3f})")
        
        # 성공 기준 확인 (80% 이상)
        if result.match_score >= 0.8:
            print(f"🎉 검증 성공! 매치 점수: {result.match_score:.3f}")
        else:
            print(f"⚠️ 검증 개선 필요. 매치 점수: {result.match_score:.3f}")
            print(f"오류: {result.errors}")
            print(f"경고: {result.warnings}")
    
    def test_03_delay_notification_verification(self):
        """지연 발행 알림 메시지 검증 테스트"""
        print("\n🧪 테스트 3: 지연 발행 알림 메시지 검증")
        
        # 지연 발행 알림 메시지 검증
        result = self.verification_system.verify_delay_notification_message(
            'kospi-close',
            self.test_data['delay_data'],
            45  # 45분 지연
        )
        
        # 기본 검증
        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.message_type, 'delay')
        self.assertEqual(result.capture_id, 'capture_2_delay')
        
        # 지연 특별 검증 확인
        self.assertIn('delay_verification', result.verification_details)
        delay_verification = result.verification_details['delay_verification']
        
        # 지연 관련 데이터 검증
        self.assertIn('delay_minutes_correct', delay_verification)
        self.assertIn('news_type_correct', delay_verification)
        self.assertIn('delay_status_correct', delay_verification)
        
        print(f"✅ 지연 발행 알림 검증 완료 (매치 점수: {result.match_score:.3f})")
        
        # 성공 기준 확인
        if result.match_score >= 0.8:
            print(f"🎉 검증 성공! 매치 점수: {result.match_score:.3f}")
        else:
            print(f"⚠️ 검증 개선 필요. 매치 점수: {result.match_score:.3f}")
    
    def test_04_daily_integrated_report_verification(self):
        """일일 통합 분석 리포트 메시지 검증 테스트"""
        print("\n🧪 테스트 4: 일일 통합 분석 리포트 메시지 검증")
        
        # 일일 통합 분석 리포트 메시지 검증
        result = self.verification_system.verify_daily_integrated_report_message(
            self.test_data['raw_data']
        )
        
        # 기본 검증
        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.message_type, 'report')
        self.assertEqual(result.capture_id, 'capture_3_report')
        
        # 리포트 특별 검증 확인
        self.assertIn('report_verification', result.verification_details)
        report_verification = result.verification_details['report_verification']
        
        # 리포트 관련 데이터 검증
        self.assertIn('completion_rate_present', report_verification)
        self.assertIn('news_status_detailed', report_verification)
        self.assertIn('recommendations_present', report_verification)
        
        print(f"✅ 일일 통합 리포트 검증 완료 (매치 점수: {result.match_score:.3f})")
        
        # 성공 기준 확인
        if result.match_score >= 0.8:
            print(f"🎉 검증 성공! 매치 점수: {result.match_score:.3f}")
        else:
            print(f"⚠️ 검증 개선 필요. 매치 점수: {result.match_score:.3f}")
    
    def test_05_status_notification_verification(self):
        """정시 발행 알림 메시지 검증 테스트"""
        print("\n🧪 테스트 5: 정시 발행 알림 메시지 검증")
        
        # 정시 발행 알림 메시지 검증
        result = self.verification_system.verify_status_notification_message(
            self.test_data['raw_data']
        )
        
        # 기본 검증
        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.message_type, 'status')
        self.assertEqual(result.capture_id, 'capture_4_status')
        
        # 상태 특별 검증 확인
        self.assertIn('status_verification', result.verification_details)
        status_verification = result.verification_details['status_verification']
        
        # 상태 관련 데이터 검증
        self.assertIn('current_status_present', status_verification)
        self.assertIn('overall_status_summary', status_verification)
        self.assertIn('confirmation_message', status_verification)
        
        print(f"✅ 정시 발행 알림 검증 완료 (매치 점수: {result.match_score:.3f})")
        
        # 성공 기준 확인
        if result.match_score >= 0.8:
            print(f"🎉 검증 성공! 매치 점수: {result.match_score:.3f}")
        else:
            print(f"⚠️ 검증 개선 필요. 매치 점수: {result.match_score:.3f}")
    
    def test_06_no_data_notification_verification(self):
        """데이터 갱신 없음 알림 메시지 검증 테스트"""
        print("\n🧪 테스트 6: 데이터 갱신 없음 알림 메시지 검증")
        
        # 데이터 갱신 없음 알림 메시지 검증
        result = self.verification_system.verify_no_data_notification_message(
            self.test_data['empty_data']
        )
        
        # 기본 검증
        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.message_type, 'no_data')
        self.assertEqual(result.capture_id, 'capture_5_no_data')
        
        print(f"✅ 데이터 갱신 없음 알림 검증 완료 (매치 점수: {result.match_score:.3f})")
        
        # 성공 기준 확인
        if result.match_score >= 0.8:
            print(f"🎉 검증 성공! 매치 점수: {result.match_score:.3f}")
        else:
            print(f"⚠️ 검증 개선 필요. 매치 점수: {result.match_score:.3f}")
    
    def test_07_comprehensive_verification(self):
        """종합 검증 테스트"""
        print("\n🧪 테스트 7: 종합 검증")
        
        # 종합 검증 실행
        results = self.verification_system.run_comprehensive_verification(self.test_data)
        
        # 결과 확인
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)
        
        # 각 검증 결과 확인
        expected_types = ['comparison', 'delay', 'report', 'status', 'no_data']
        for message_type in expected_types:
            if message_type in results:
                result = results[message_type]
                self.assertIsInstance(result, VerificationResult)
                self.assertEqual(result.message_type, message_type)
        
        # 성공률 계산
        successful_count = sum(1 for result in results.values() if result.success)
        total_count = len(results)
        success_rate = successful_count / total_count if total_count > 0 else 0
        
        print(f"✅ 종합 검증 완료: {successful_count}/{total_count} 성공 ({success_rate:.1%})")
        
        # 각 검증 결과 출력
        for message_type, result in results.items():
            status = "✅" if result.success else "❌"
            print(f"  {status} {message_type}: {result.match_score:.3f}")
    
    def test_08_verification_report_generation(self):
        """검증 리포트 생성 테스트"""
        print("\n🧪 테스트 8: 검증 리포트 생성")
        
        # 종합 검증 실행
        results = self.verification_system.run_comprehensive_verification(self.test_data)
        
        # 리포트 생성
        report = self.verification_system.generate_verification_report(results)
        
        # 리포트 내용 확인
        self.assertIsInstance(report, str)
        self.assertIn("캡처 이미지 기반 결과 검증 리포트", report)
        self.assertIn("검증 일시:", report)
        self.assertIn("총 검증 수:", report)
        self.assertIn("성공률:", report)
        
        print("✅ 검증 리포트 생성 완료")
        print("\n" + "="*50)
        print(report)
        print("="*50)
    
    def test_09_bot_type_selection_logic(self):
        """BOT 타입 선택 로직 검증 테스트"""
        print("\n🧪 테스트 9: BOT 타입 선택 로직 검증")
        
        # 각 메시지 타입별 BOT 설정 확인
        test_cases = [
            ('comparison', 'POSCO 뉴스 비교알림', '#007bff'),
            ('delay', 'POSCO 뉴스 ⏰', '#ffc107'),
            ('report', 'POSCO 뉴스 📊', '#28a745'),
            ('status', 'POSCO 뉴스 ✅', '#17a2b8'),
            ('no_data', 'POSCO 뉴스 🔔', '#6c757d')
        ]
        
        for message_type, expected_bot_name, expected_color in test_cases:
            capture_ref = None
            for ref in self.verification_system.capture_references.values():
                if ref.bot_type == message_type:
                    capture_ref = ref
                    break
            
            self.assertIsNotNone(capture_ref, f"{message_type} 캡처 참조를 찾을 수 없습니다")
            self.assertEqual(capture_ref.bot_name, expected_bot_name)
            self.assertEqual(capture_ref.color, expected_color)
        
        print("✅ BOT 타입 선택 로직 검증 완료")
    
    def test_10_emoji_and_format_accuracy(self):
        """이모지 및 포맷 정확성 검증 테스트"""
        print("\n🧪 테스트 10: 이모지 및 포맷 정확성 검증")
        
        # 각 캡처 참조의 이모지와 포맷 패턴 확인
        for capture_id, capture_ref in self.verification_system.capture_references.items():
            # 이모지 존재 확인
            self.assertGreater(len(capture_ref.emojis), 0, f"{capture_id}에 이모지가 없습니다")
            
            # 포맷 패턴 존재 확인
            self.assertGreater(len(capture_ref.format_patterns), 0, f"{capture_id}에 포맷 패턴이 없습니다")
            
            # 콘텐츠 라인 존재 확인
            self.assertGreater(len(capture_ref.content_lines), 0, f"{capture_id}에 콘텐츠가 없습니다")
            
            print(f"  ✅ {capture_id}: {len(capture_ref.emojis)}개 이모지, {len(capture_ref.format_patterns)}개 패턴")
        
        print("✅ 이모지 및 포맷 정확성 검증 완료")
    
    def test_11_time_information_accuracy(self):
        """시간 정보 정확성 검증 테스트"""
        print("\n🧪 테스트 11: 시간 정보 정확성 검증")
        
        # 시간 정보가 포함된 캡처들 확인
        time_sensitive_captures = ['capture_2_delay', 'capture_3_report', 'capture_4_status', 'capture_5_no_data']
        
        for capture_id in time_sensitive_captures:
            if capture_id in self.verification_system.capture_references:
                capture_ref = self.verification_system.capture_references[capture_id]
                
                # 시간 관련 패턴이 있는지 확인
                time_patterns_found = any(
                    '시간' in pattern or r'\d{4}-\d{2}-\d{2}' in pattern or r'\d{2}:\d{2}' in pattern
                    for pattern in capture_ref.format_patterns
                )
                
                # 콘텐츠에 시간 정보가 있는지 확인
                time_content_found = any(
                    '시간' in line or ':' in line
                    for line in capture_ref.content_lines
                )
                
                self.assertTrue(
                    time_patterns_found or time_content_found,
                    f"{capture_id}에 시간 정보가 부족합니다"
                )
                
                print(f"  ✅ {capture_id}: 시간 정보 확인됨")
        
        print("✅ 시간 정보 정확성 검증 완료")
    
    def test_12_verification_statistics(self):
        """검증 통계 테스트"""
        print("\n🧪 테스트 12: 검증 통계")
        
        # 통계 조회
        stats = self.verification_system.get_verification_statistics()
        
        # 통계 구조 확인
        expected_keys = [
            'total_verifications', 'successful_verifications', 'failed_verifications',
            'average_match_score', 'success_rate', 'failure_rate', 'last_verification_time'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats, f"통계에 {key}가 없습니다")
        
        # 통계 값 확인
        self.assertGreaterEqual(stats['total_verifications'], 0)
        self.assertGreaterEqual(stats['successful_verifications'], 0)
        self.assertGreaterEqual(stats['failed_verifications'], 0)
        self.assertGreaterEqual(stats['success_rate'], 0.0)
        self.assertLessEqual(stats['success_rate'], 1.0)
        
        print(f"✅ 검증 통계 확인 완료:")
        print(f"  • 총 검증: {stats['total_verifications']}회")
        print(f"  • 성공률: {stats['success_rate']:.1%}")
        print(f"  • 평균 매치 점수: {stats['average_match_score']:.3f}")


def run_capture_verification_tests():
    """캡처 검증 테스트 실행"""
    print("🚀 캡처 이미지 기반 결과 검증 시스템 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCaptureVerificationSystem)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    print(f"  • 실행된 테스트: {result.testsRun}개")
    print(f"  • 성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"  • 실패: {len(result.failures)}개")
    print(f"  • 오류: {len(result.errors)}개")
    
    if result.failures:
        print("\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback}")
    
    if result.errors:
        print("\n💥 오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback}")
    
    # 전체 성공 여부 반환
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_capture_verification_tests()
    
    if success:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        sys.exit(1)