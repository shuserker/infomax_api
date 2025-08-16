# -*- coding: utf-8 -*-
"""
뉴스 알림 메시지 생성 로직 테스트

정상 커밋 a763ef84의 원본 메시지 생성 알고리즘 복원 테스트입니다.

작성자: AI Assistant
작성일: 2025-08-12
"""

import json
import time
import unittest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news_message_generator import NewsMessageGenerator, MessageGenerationResult


class TestNewsMessageGenerator(unittest.TestCase):
    """뉴스 메시지 생성기 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트용 시간 설정 (2025-08-12 10:30:00)
        self.test_time = datetime(2025, 8, 12, 10, 30, 0)
        
        # 테스트 모드로 생성기 초기화
        self.generator = NewsMessageGenerator(
            test_mode=True, 
            test_datetime=self.test_time
        )
        
        # 샘플 뉴스 데이터
        self.sample_data = {
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
                'title': '[환율] 달러/원 환율 하락',
                'content': '달러/원 1,320.50 (-5.25), 엔/원 8.95 (+0.12)',
                'date': '20250812',
                'time': '163000'
            }
        }
        
        # 과거 데이터 (영업일 비교용)
        self.historical_data = {
            'newyork-market-watch': {
                'title': '[뉴욕마켓워치] 미국 증시 혼조 마감',
                'time': '061845',
                'date': '20250811'
            },
            'kospi-close': {
                'title': '[증시마감] 코스피 2,480선 마감',
                'time': '154200',
                'date': '20250811'
            }
        }
    
    def test_business_day_comparison_message(self):
        """영업일 비교 분석 메시지 생성 테스트"""
        print("\n=== 영업일 비교 분석 메시지 테스트 ===")
        
        result = self.generator.generate_business_day_comparison_message(
            self.sample_data, 
            self.historical_data
        )
        
        # 기본 검증
        self.assertTrue(result.success, f"메시지 생성 실패: {result.errors}")
        self.assertEqual(result.message_type, 'comparison')
        self.assertTrue(result.test_mode)
        self.assertIn('📊 영업일 비교 분석', result.message)
        self.assertIn('[TEST]', result.bot_name)
        
        # 트리 구조 검증
        self.assertIn('├', result.message)  # 트리 구조 확인
        self.assertIn('└', result.message)  # 트리 구조 확인
        
        # 각 뉴스 타입 포함 확인
        self.assertIn('[NEWYORK MARKET WATCH]', result.message)
        self.assertIn('[KOSPI CLOSE]', result.message)
        self.assertIn('[EXCHANGE RATE]', result.message)
        
        print(f"✅ 성공: {result.success}")
        print(f"BOT: {result.bot_name}")
        print(f"메시지 길이: {len(result.message)} 문자")
        print(f"처리 시간: {result.generation_time:.3f}초")
        print(f"메시지 미리보기:\n{result.message[:200]}...")
    
    def test_delay_notification_message(self):
        """지연 발행 알림 메시지 생성 테스트"""
        print("\n=== 지연 발행 알림 메시지 테스트 ===")
        
        # 25분 지연 시나리오
        result = self.generator.generate_delay_notification_message(
            'newyork-market-watch',
            self.sample_data['newyork-market-watch'],
            25
        )
        
        # 기본 검증
        self.assertTrue(result.success, f"메시지 생성 실패: {result.errors}")
        self.assertEqual(result.message_type, 'delay')
        self.assertTrue(result.test_mode)
        self.assertIn('지연 발행', result.message)
        self.assertIn('🟠', result.message)  # 25분 지연은 주황불
        self.assertIn('25분 지연', result.message)
        
        print(f"✅ 성공: {result.success}")
        print(f"BOT: {result.bot_name}")
        print(f"지연 시간: 25분")
        print(f"처리 시간: {result.generation_time:.3f}초")
        print(f"메시지:\n{result.message}")
    
    def test_daily_integrated_report_message(self):
        """일일 통합 분석 리포트 메시지 생성 테스트"""
        print("\n=== 일일 통합 분석 리포트 메시지 테스트 ===")
        
        result = self.generator.generate_daily_integrated_report_message(
            self.sample_data,
            "https://example.com/report.html"
        )
        
        # 기본 검증
        self.assertTrue(result.success, f"메시지 생성 실패: {result.errors}")
        self.assertEqual(result.message_type, 'report')
        self.assertTrue(result.test_mode)
        self.assertIn('📊 일일 통합 분석 리포트', result.message)
        self.assertIn('발행 현황:', result.message)
        self.assertIn('뉴스별 발행 현황:', result.message)
        self.assertIn('https://example.com/report.html', result.message)
        
        print(f"✅ 성공: {result.success}")
        print(f"BOT: {result.bot_name}")
        print(f"처리 시간: {result.generation_time:.3f}초")
        print(f"메시지 미리보기:\n{result.message[:300]}...")
    
    def test_status_notification_message(self):
        """정시 발행 알림 메시지 생성 테스트"""
        print("\n=== 정시 발행 알림 메시지 테스트 ===")
        
        result = self.generator.generate_status_notification_message(self.sample_data)
        
        # 기본 검증
        self.assertTrue(result.success, f"메시지 생성 실패: {result.errors}")
        self.assertEqual(result.message_type, 'status')
        self.assertTrue(result.test_mode)
        self.assertIn('✅ 정시 발행 알림', result.message)
        self.assertIn('현재 발행 상태:', result.message)
        self.assertIn('전체 상태:', result.message)
        
        print(f"✅ 성공: {result.success}")
        print(f"BOT: {result.bot_name}")
        print(f"처리 시간: {result.generation_time:.3f}초")
        print(f"메시지:\n{result.message}")
    
    def test_no_data_notification_message(self):
        """데이터 갱신 없음 알림 메시지 생성 테스트"""
        print("\n=== 데이터 갱신 없음 알림 메시지 테스트 ===")
        
        # 빈 데이터로 테스트
        result = self.generator.generate_no_data_notification_message({})
        
        # 기본 검증
        self.assertTrue(result.success, f"메시지 생성 실패: {result.errors}")
        self.assertEqual(result.message_type, 'no_data')
        self.assertTrue(result.test_mode)
        self.assertIn('🔔 데이터 갱신 없음', result.message)
        self.assertIn('마지막 확인 상태:', result.message)
        self.assertIn('새로운 뉴스 발행을 대기', result.message)
        
        print(f"✅ 성공: {result.success}")
        print(f"BOT: {result.bot_name}")
        print(f"처리 시간: {result.generation_time:.3f}초")
        print(f"메시지:\n{result.message}")
    
    def test_message_type_determination(self):
        """메시지 타입 자동 결정 테스트"""
        print("\n=== 메시지 타입 자동 결정 테스트 ===")
        
        # 다양한 시간대별 테스트
        test_scenarios = [
            (datetime(2025, 8, 12, 6, 10, 0), 'comparison'),  # 06:10 - 영업일 비교
            (datetime(2025, 8, 12, 18, 0, 0), 'report'),      # 18:00 - 일일 리포트
            (datetime(2025, 8, 12, 12, 0, 0), 'status'),      # 12:00 - 정시 상태
            (datetime(2025, 8, 12, 10, 30, 0), 'status'),     # 10:30 - 일반 시간
        ]
        
        for test_time, expected_type in test_scenarios:
            # 테스트용 생성기 생성
            test_generator = NewsMessageGenerator(
                test_mode=True, 
                test_datetime=test_time
            )
            
            # 메시지 타입 결정
            determined_type = test_generator.determine_message_type(self.sample_data, test_time)
            
            print(f"시간: {test_time.strftime('%H:%M')} -> 예상: {expected_type}, 결정: {determined_type}")
            
            # 특정 시간대는 정확히 매칭되어야 함
            if test_time.hour == 6 and test_time.minute == 10:
                self.assertEqual(determined_type, expected_type)
            elif test_time.hour == 18 and test_time.minute == 0:
                self.assertEqual(determined_type, expected_type)
    
    def test_tree_structure_formatting(self):
        """트리 구조 메시지 포맷팅 테스트"""
        print("\n=== 트리 구조 포맷팅 테스트 ===")
        
        result = self.generator.generate_business_day_comparison_message(
            self.sample_data, 
            self.historical_data
        )
        
        # 트리 구조 문자 확인
        tree_chars = ['├', '└']
        for char in tree_chars:
            self.assertIn(char, result.message, f"트리 구조 문자 '{char}' 누락")
        
        # 각 뉴스 타입별 트리 구조 확인
        lines = result.message.split('\n')
        tree_lines = [line for line in lines if any(char in line for char in tree_chars)]
        
        self.assertGreater(len(tree_lines), 0, "트리 구조 라인이 없음")
        
        print(f"✅ 트리 구조 라인 수: {len(tree_lines)}")
        print("트리 구조 예시:")
        for line in tree_lines[:5]:  # 처음 5개 라인만 출력
            print(f"  {line}")
    
    def test_test_mode_formatting(self):
        """테스트 모드 포맷팅 테스트"""
        print("\n=== 테스트 모드 포맷팅 테스트 ===")
        
        # 테스트 모드 생성기
        test_generator = NewsMessageGenerator(test_mode=True, test_datetime=self.test_time)
        result_test = test_generator.generate_status_notification_message(self.sample_data)
        
        # 실제 모드 생성기
        real_generator = NewsMessageGenerator(test_mode=False)
        result_real = real_generator.generate_status_notification_message(self.sample_data)
        
        # 테스트 모드 검증
        self.assertTrue(result_test.test_mode)
        self.assertIn('[TEST]', result_test.message)
        self.assertIn('[TEST]', result_test.bot_name)
        self.assertIn('2025-08-12 10:30', result_test.message)
        
        # 실제 모드 검증
        self.assertFalse(result_real.test_mode)
        self.assertNotIn('[TEST]', result_real.message)
        self.assertNotIn('[TEST]', result_real.bot_name)
        
        print(f"✅ 테스트 모드 메시지에 [TEST] 포함: {'[TEST]' in result_test.message}")
        print(f"✅ 실제 모드 메시지에 [TEST] 미포함: {'[TEST]' not in result_real.message}")
    
    def test_time_based_status_determination(self):
        """시간 기반 상태 판단 테스트"""
        print("\n=== 시간 기반 상태 판단 테스트 ===")
        
        # 다양한 시간대별 상태 판단 테스트
        test_times = [
            (datetime(2025, 8, 12, 5, 30, 0), "뉴욕마켓워치 발행 전"),  # 06:00 이전
            (datetime(2025, 8, 12, 6, 5, 0), "뉴욕마켓워치 정시 발행"),   # 06:00 근처
            (datetime(2025, 8, 12, 6, 20, 0), "뉴욕마켓워치 지연 발행"),  # 06:00 + 20분
            (datetime(2025, 8, 12, 15, 30, 0), "코스피 발행 전"),        # 15:40 이전
            (datetime(2025, 8, 12, 15, 45, 0), "코스피 정시 발행"),       # 15:40 근처
            (datetime(2025, 8, 12, 16, 0, 0), "코스피 지연 발행"),        # 15:40 + 20분
        ]
        
        for test_time, description in test_times:
            test_generator = NewsMessageGenerator(
                test_mode=True, 
                test_datetime=test_time
            )
            
            # 빈 데이터로 상태 판단 테스트 (발행 전/지연 상태 확인)
            result = test_generator.generate_status_notification_message({})
            
            print(f"{description}: {test_time.strftime('%H:%M')} - 메시지 생성 {'성공' if result.success else '실패'}")
    
    def test_bot_configuration(self):
        """BOT 설정 테스트"""
        print("\n=== BOT 설정 테스트 ===")
        
        # 각 메시지 타입별 BOT 설정 확인
        message_types = [
            ('comparison', self.generator.generate_business_day_comparison_message, (self.sample_data, self.historical_data)),
            ('delay', self.generator.generate_delay_notification_message, ('newyork-market-watch', self.sample_data['newyork-market-watch'], 25)),
            ('report', self.generator.generate_daily_integrated_report_message, (self.sample_data, "https://example.com/report.html")),
            ('status', self.generator.generate_status_notification_message, (self.sample_data,)),
            ('no_data', self.generator.generate_no_data_notification_message, ({},))
        ]
        
        for msg_type, method, args in message_types:
            result = method(*args)
            
            # BOT 설정 검증
            self.assertTrue(result.success, f"{msg_type} 메시지 생성 실패")
            self.assertEqual(result.message_type, msg_type)
            self.assertIsNotNone(result.bot_name)
            self.assertIsNotNone(result.bot_icon)
            self.assertIsNotNone(result.color)
            self.assertIn('[TEST]', result.bot_name)  # 테스트 모드
            
            print(f"{msg_type}: {result.bot_name} - {result.color}")


def run_comprehensive_test():
    """종합 테스트 실행"""
    print("=" * 60)
    print("뉴스 알림 메시지 생성 로직 완전 복원 테스트")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestNewsMessageGenerator)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"총 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)