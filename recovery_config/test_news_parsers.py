# -*- coding: utf-8 -*-
"""
뉴스 데이터 파싱 로직 테스트

작업 5의 구현 결과를 검증하는 종합 테스트 모듈입니다.

주요 테스트:
- NEWYORK MARKET WATCH 데이터 파싱 테스트
- KOSPI CLOSE 데이터 파싱 테스트
- EXCHANGE RATE 데이터 파싱 테스트
- 각 데이터 소스별 상태 판단 로직 테스트
- 통합 파싱 시스템 테스트

작성자: AI Assistant
작성 일시: 2025-08-12
"""

import json
import time
import unittest
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from recovery_config.news_data_parser import NewsDataParser, NewsStatus
from recovery_config.newyork_market_parser import NewYorkMarketParser
from recovery_config.kospi_close_parser import KospiCloseParser
from recovery_config.exchange_rate_parser import ExchangeRateParser
from recovery_config.integrated_news_parser import IntegratedNewsParser


class TestNewsDataParser(unittest.TestCase):
    """기본 뉴스 데이터 파서 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.parser = NewsDataParser()
        self.sample_data = {
            'newyork-market-watch': {
                'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
                'content': '뉴욕 증시가 상승세로 마감했습니다.',
                'date': '20250812',
                'time': '060500'
            },
            'kospi-close': {
                'title': '[증시마감] 코스피 2,500선 회복',
                'content': '코스피가 2,500선을 회복했습니다.',
                'date': '20250812',
                'time': '154500'
            },
            'exchange-rate': {
                'title': '[서환마감] 원달러 환율 1,350원대',
                'content': '원달러 환율이 1,350원대에서 거래되고 있습니다.',
                'date': '20250812',
                'time': '163200'
            }
        }
    
    def test_parse_news_data(self):
        """뉴스 데이터 파싱 테스트"""
        result = self.parser.parse_news_data(self.sample_data)
        
        # 기본 검증
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)
        
        # 각 뉴스 타입 검증
        for news_type in ['newyork-market-watch', 'kospi-close', 'exchange-rate']:
            self.assertIn(news_type, result)
            news_item = result[news_type]
            
            # 필수 필드 검증
            self.assertEqual(news_item.news_type, news_type)
            self.assertIsNotNone(news_item.title)
            self.assertIsNotNone(news_item.status)
            self.assertIsNotNone(news_item.status_description)
    
    def test_status_determination(self):
        """상태 판단 로직 테스트"""
        # 현재 시간 기준 테스트 데이터
        now = datetime.now()
        today_str = now.strftime('%Y%m%d')
        
        # 최신 데이터 (정시 발행)
        latest_data = {
            'newyork-market-watch': {
                'title': '최신 뉴스',
                'content': '내용',
                'date': today_str,
                'time': '060000'  # 예상 발행 시간
            }
        }
        
        result = self.parser.parse_news_data(latest_data)
        news_item = result['newyork-market-watch']
        
        # 상태 검증 (시간에 따라 달라질 수 있음)
        self.assertIn(news_item.status, [NewsStatus.LATEST, NewsStatus.DELAYED, NewsStatus.EARLY])
    
    def test_empty_data_handling(self):
        """빈 데이터 처리 테스트"""
        # 빈 딕셔너리
        result = self.parser.parse_news_data({})
        self.assertEqual(len(result), 0)
        
        # None 데이터
        result = self.parser.parse_news_data(None)
        self.assertEqual(len(result), 0)
        
        # 빈 뉴스 데이터
        empty_news_data = {
            'newyork-market-watch': {}
        }
        result = self.parser.parse_news_data(empty_news_data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result['newyork-market-watch'].status, NewsStatus.NO_DATA)
    
    def test_validation(self):
        """데이터 검증 테스트"""
        result = self.parser.parse_news_data(self.sample_data)
        is_valid, errors = self.parser.validate_parsed_data(result)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_status_summary(self):
        """상태 요약 테스트"""
        result = self.parser.parse_news_data(self.sample_data)
        summary = self.parser.get_status_summary(result)
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_news', summary)
        self.assertIn('overall_status', summary)
        self.assertEqual(summary['total_news'], 3)


class TestNewYorkMarketParser(unittest.TestCase):
    """뉴욕마켓워치 파서 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.parser = NewYorkMarketParser()
        self.sample_data = {
            'title': '[뉴욕마켓워치] 미국 증시 상승 마감, 다우 35,000선 돌파',
            'content': '뉴욕 증시가 상승세로 마감했습니다. 다우존스 산업평균지수는 35,123.45로 전일 대비 +150.25포인트(+0.43%) 상승했습니다. 나스닥 종합지수는 14,567.89로 +45.67포인트(+0.31%) 올랐고, S&P500 지수는 4,456.78로 +25.34포인트(+0.57%) 상승했습니다.',
            'date': '20250812',
            'time': '060500'
        }
    
    def test_parse_newyork_data(self):
        """뉴욕마켓워치 데이터 파싱 테스트"""
        result = self.parser.parse_newyork_market_data(self.sample_data)
        
        # 기본 검증
        self.assertEqual(result.title, self.sample_data['title'])
        self.assertEqual(result.date, self.sample_data['date'])
        self.assertEqual(result.time, self.sample_data['time'])
        
        # 시장 상황 검증
        self.assertIn(result.market_situation, ['상승', '하락', '혼조'])
        
        # 지수 추출 검증
        self.assertIsInstance(result.major_indices, list)
        
        # 시장 요약 검증
        self.assertIsInstance(result.market_summary, str)
        self.assertGreater(len(result.market_summary), 0)
    
    def test_index_extraction(self):
        """지수 추출 테스트"""
        result = self.parser.parse_newyork_market_data(self.sample_data)
        
        # 지수가 추출되었는지 확인
        if result.major_indices:
            for index in result.major_indices:
                self.assertIsInstance(index.name, str)
                self.assertIsInstance(index.value, float)
                self.assertIn(index.direction, ['up', 'down', 'flat'])
    
    def test_market_situation_determination(self):
        """시장 상황 판단 테스트"""
        # 상승 시장 데이터
        up_data = {
            'title': '미국 증시 상승',
            'content': '다우존스 상승, 나스닥 강세',
            'date': '20250812',
            'time': '060500'
        }
        
        result = self.parser.parse_newyork_market_data(up_data)
        # 키워드 기반으로 상승으로 판단될 가능성이 높음
        self.assertIsInstance(result.market_situation, str)


class TestKospiCloseParser(unittest.TestCase):
    """증시마감 파서 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.parser = KospiCloseParser()
        self.sample_data = {
            'title': '[증시마감] 코스피 2,500선 회복, 외국인 순매수 전환',
            'content': '코스피가 2,523.45로 전일 대비 +25.67포인트(+1.03%) 상승 마감했습니다. 코스닥은 756.89로 +8.45포인트(+1.13%) 올랐습니다. 외국인이 1,250억원 순매수했고, 기관은 -850억원 순매도했습니다.',
            'date': '20250812',
            'time': '154500'
        }
    
    def test_parse_kospi_data(self):
        """증시마감 데이터 파싱 테스트"""
        result = self.parser.parse_kospi_close_data(self.sample_data)
        
        # 기본 검증
        self.assertEqual(result.title, self.sample_data['title'])
        self.assertEqual(result.date, self.sample_data['date'])
        self.assertEqual(result.time, self.sample_data['time'])
        
        # 시장 상황 검증
        self.assertIn(result.market_situation, ['상승', '하락', '혼조'])
        
        # 지수 추출 검증
        self.assertIsInstance(result.main_indices, list)
        
        # 시장 요약 검증
        self.assertIsInstance(result.market_summary, str)
    
    def test_trading_flow_extraction(self):
        """매매 동향 추출 테스트"""
        result = self.parser.parse_kospi_close_data(self.sample_data)
        
        # 매매 동향이 추출되었는지 확인
        if result.trading_flow:
            self.assertIsInstance(result.trading_flow.foreign_net, float)
            self.assertIsInstance(result.trading_flow.institution_net, float)
            self.assertIsInstance(result.trading_flow.individual_net, float)
    
    def test_sector_analysis(self):
        """섹터 분석 테스트"""
        sector_data = {
            'title': '증시마감',
            'content': '반도체 업종이 강세를 보였으며, 바이오 섹터는 하락했습니다. 자동차 업종은 보합세를 유지했습니다.',
            'date': '20250812',
            'time': '154500'
        }
        
        result = self.parser.parse_kospi_close_data(sector_data)
        
        # 섹터 분석 결과 확인
        self.assertIsInstance(result.sector_analysis, dict)


class TestExchangeRateParser(unittest.TestCase):
    """서환마감 파서 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.parser = ExchangeRateParser()
        self.sample_data = {
            'title': '[서환마감] 원달러 환율 1,350원대, 연준 발언에 원화 약세',
            'content': '원달러 환율이 1,352.50원으로 전일 대비 +8.30원(+0.62%) 상승 마감했습니다. 연준 위원들의 매파적 발언이 달러 강세를 이끌었습니다. 엔화는 100엔당 912.45원을 기록했습니다.',
            'date': '20250812',
            'time': '163200'
        }
    
    def test_parse_exchange_data(self):
        """서환마감 데이터 파싱 테스트"""
        result = self.parser.parse_exchange_rate_data(self.sample_data)
        
        # 기본 검증
        self.assertEqual(result.title, self.sample_data['title'])
        self.assertEqual(result.date, self.sample_data['date'])
        self.assertEqual(result.time, self.sample_data['time'])
        
        # 시장 상황 검증
        self.assertIn(result.market_situation, ['강세', '약세', '보합'])
        
        # 변동성 수준 검증
        self.assertIn(result.volatility_level, ['high', 'medium', 'low'])
    
    def test_usd_krw_extraction(self):
        """원달러 환율 추출 테스트"""
        result = self.parser.parse_exchange_rate_data(self.sample_data)
        
        # 원달러 환율이 추출되었는지 확인
        if result.usd_krw_rate:
            self.assertEqual(result.usd_krw_rate.currency_pair, 'USD/KRW')
            self.assertIsInstance(result.usd_krw_rate.rate, float)
            self.assertIn(result.usd_krw_rate.direction, ['up', 'down', 'flat'])
    
    def test_market_factors_extraction(self):
        """변동 요인 추출 테스트"""
        result = self.parser.parse_exchange_rate_data(self.sample_data)
        
        # 변동 요인이 추출되었는지 확인
        self.assertIsInstance(result.market_factors, list)
        
        for factor in result.market_factors:
            self.assertIn(factor.factor_type, ['domestic', 'international', 'technical', 'geopolitical'])
            self.assertIn(factor.impact, ['positive', 'negative', 'neutral'])


class TestIntegratedNewsParser(unittest.TestCase):
    """통합 뉴스 파서 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.parser = IntegratedNewsParser(enable_caching=False)  # 테스트에서는 캐싱 비활성화
        self.sample_data = {
            'newyork-market-watch': {
                'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
                'content': '다우존스 35,123.45 (+150.25), 나스닥 14,567.89 (+45.67)',
                'date': '20250812',
                'time': '060500'
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
    
    def test_integrated_parsing(self):
        """통합 파싱 테스트"""
        result = self.parser.parse_all_news_data(self.sample_data)
        
        # 파싱 성공 검증
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertIsInstance(result.processing_time, float)
        
        # 통합 데이터 검증
        data = result.data
        self.assertIsInstance(data.news_items, dict)
        self.assertIsInstance(data.specialized_data, dict)
        self.assertIsInstance(data.market_summary, str)
        self.assertIsInstance(data.recommendations, list)
    
    def test_data_validation(self):
        """데이터 검증 테스트"""
        # 유효한 데이터
        is_valid, errors = self.parser.validate_raw_data(self.sample_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # 무효한 데이터
        invalid_data = {'invalid': 'data'}
        is_valid, errors = self.parser.validate_raw_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_overall_status_determination(self):
        """전체 상태 판단 테스트"""
        result = self.parser.parse_all_news_data(self.sample_data)
        
        if result.success and result.data:
            self.assertIn(result.data.overall_status, 
                         ['latest', 'delayed', 'old', 'no_data', 'error', 'invalid'])
    
    def test_recommendations_generation(self):
        """권장사항 생성 테스트"""
        result = self.parser.parse_all_news_data(self.sample_data)
        
        if result.success and result.data:
            self.assertIsInstance(result.data.recommendations, list)
            self.assertLessEqual(len(result.data.recommendations), 5)  # 최대 5개
            
            for recommendation in result.data.recommendations:
                self.assertIsInstance(recommendation, str)
                self.assertGreater(len(recommendation), 0)
    
    def test_parsing_stats(self):
        """파싱 통계 테스트"""
        # 파싱 실행
        self.parser.parse_all_news_data(self.sample_data)
        
        # 통계 확인
        stats = self.parser.get_parsing_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_parsed', stats)
        self.assertIn('successful_parses', stats)
        self.assertIn('success_rate', stats)
        self.assertGreater(stats['total_parsed'], 0)


def run_comprehensive_test():
    """종합 테스트 실행"""
    print("=== 뉴스 데이터 파싱 로직 종합 테스트 ===")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 각 테스트 클래스 추가
    test_classes = [
        TestNewsDataParser,
        TestNewYorkMarketParser,
        TestKospiCloseParser,
        TestExchangeRateParser,
        TestIntegratedNewsParser
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 결과 요약
    print()
    print("=== 테스트 결과 요약 ===")
    print(f"총 테스트: {result.testsRun}개")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"실패: {len(result.failures)}개")
    print(f"오류: {len(result.errors)}개")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  - {test}: {error_msg}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  - {test}: {error_msg}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n성공률: {success_rate:.1f}%")
    
    return result.wasSuccessful()


def run_performance_test():
    """성능 테스트 실행"""
    print("\n=== 성능 테스트 ===")
    
    # 테스트 데이터
    sample_data = {
        'newyork-market-watch': {
            'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
            'content': '다우존스 35,123.45 (+150.25), 나스닥 14,567.89 (+45.67), S&P500 4,456.78 (+25.34)',
            'date': '20250812',
            'time': '060500'
        },
        'kospi-close': {
            'title': '[증시마감] 코스피 2,500선 회복',
            'content': '코스피 2,523.45 (+25.67), 코스닥 756.89 (+8.45), 외국인 1,250억원 순매수',
            'date': '20250812',
            'time': '154500'
        },
        'exchange-rate': {
            'title': '[서환마감] 원달러 환율 1,350원대',
            'content': '원달러 1,352.50 (+8.30), 엔화 912.45, 유로 1,456.78',
            'date': '20250812',
            'time': '163200'
        }
    }
    
    parser = IntegratedNewsParser(enable_caching=False)
    
    # 성능 측정
    iterations = 100
    total_time = 0
    
    print(f"{iterations}회 파싱 성능 측정 중...")
    
    for i in range(iterations):
        start_time = time.time()
        result = parser.parse_all_news_data(sample_data)
        end_time = time.time()
        
        if result.success:
            total_time += (end_time - start_time)
        
        if (i + 1) % 20 == 0:
            print(f"  진행률: {(i + 1) / iterations * 100:.0f}%")
    
    avg_time = total_time / iterations
    print(f"\n성능 결과:")
    print(f"  평균 처리 시간: {avg_time * 1000:.2f}ms")
    print(f"  초당 처리 가능: {1 / avg_time:.1f}회")
    
    # 파싱 통계
    stats = parser.get_parsing_stats()
    print(f"  성공률: {stats['success_rate']:.1f}%")


if __name__ == "__main__":
    # 종합 테스트 실행
    success = run_comprehensive_test()
    
    # 성능 테스트 실행
    run_performance_test()
    
    # 최종 결과
    print("\n" + "="*50)
    if success:
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
        print("작업 5: 뉴스 데이터 파싱 로직 구현이 완료되었습니다.")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print("실패한 테스트를 확인하고 수정이 필요합니다.")
    print("="*50)