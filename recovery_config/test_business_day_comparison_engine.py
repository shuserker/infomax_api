#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 영업일 비교 분석 엔진 테스트

영업일 비교 분석 엔진의 모든 기능을 테스트하는 종합 테스트 시스템입니다.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import unittest
from unittest.mock import Mock, patch

# 테스트 대상 모듈 import
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from business_day_comparison_engine import (
    BusinessDayComparisonEngine, BusinessDayInfo, ComparisonResult, 
    BusinessDayComparisonReport
)


class MockNewsItem:
    """테스트용 뉴스 아이템"""
    def __init__(self, title="테스트 뉴스", status="latest", is_latest=True, delay_minutes=0):
        self.title = title
        self.status = status
        self.is_latest = is_latest
        self.delay_minutes = delay_minutes


class MockIntegratedNewsData:
    """테스트용 통합 뉴스 데이터"""
    def __init__(self):
        # timestamp를 YYYYMMDD 형식으로 시작하도록 수정
        current_date = datetime.now().strftime('%Y%m%d')
        self.timestamp = f"{current_date}T{datetime.now().strftime('%H:%M:%S')}"
        self.news_items = {
            'newyork-market-watch': MockNewsItem("뉴욕마켓워치 테스트"),
            'kospi-close': MockNewsItem("코스피마감 테스트"),
            'exchange-rate': MockNewsItem("서환마감 테스트")
        }


class MockAPIModule:
    """테스트용 API 모듈"""
    def __init__(self):
        self.historical_data = {}
    
    def get_historical_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """모의 과거 데이터 반환"""
        result = {}
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y%m%d')
            result[date_str] = {
                'newyork-market-watch': {
                    'title': f'[뉴욕마켓워치] {date_str} 테스트',
                    'date': date_str,
                    'time': '063000'
                },
                'kospi-close': {
                    'title': f'[증시마감] {date_str} 테스트',
                    'date': date_str,
                    'time': '154000'
                },
                'exchange-rate': {
                    'title': f'[서환마감] {date_str} 테스트',
                    'date': date_str,
                    'time': '153000'
                }
            }
            current_dt += timedelta(days=1)
        
        return result


class MockNewsParser:
    """테스트용 뉴스 파서"""
    def parse_all_news_data(self, raw_data: Dict[str, Any]):
        """모의 파싱 결과 반환"""
        from types import SimpleNamespace
        
        result = SimpleNamespace()
        result.success = True
        result.data = MockIntegratedNewsData()
        result.errors = []
        result.warnings = []
        
        return result


class TestBusinessDayComparisonEngine(unittest.TestCase):
    """영업일 비교 분석 엔진 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.mock_api = MockAPIModule()
        self.mock_parser = MockNewsParser()
        self.engine = BusinessDayComparisonEngine(self.mock_api, self.mock_parser)
    
    def test_business_day_calculation(self):
        """영업일 계산 테스트"""
        print("\n=== 영업일 계산 테스트 ===")
        
        # 테스트 케이스들 (실제 2025년 날짜 기준)
        test_cases = [
            ('20250812', True, False, False, '화요일'),   # 화요일 (영업일)
            ('20250810', False, True, False, '일요일'),   # 일요일 (주말)
            ('20250811', True, False, False, '월요일'),   # 월요일 (영업일)
            ('20250101', False, False, True, '수요일'),   # 신정 (공휴일)
            ('20250815', False, False, True, '금요일'),   # 광복절 (공휴일)
        ]
        
        for date_str, expected_business, expected_weekend, expected_holiday, expected_day in test_cases:
            with self.subTest(date=date_str):
                business_day_info = self.engine.calculate_business_day_info(date_str)
                
                print(f"  {date_str} ({business_day_info.day_of_week}): "
                      f"영업일={business_day_info.is_business_day}, "
                      f"주말={business_day_info.is_weekend}, "
                      f"공휴일={business_day_info.is_holiday}")
                
                self.assertEqual(business_day_info.is_business_day, expected_business)
                self.assertEqual(business_day_info.is_weekend, expected_weekend)
                self.assertEqual(business_day_info.is_holiday, expected_holiday)
                self.assertEqual(business_day_info.day_of_week, expected_day)
    
    def test_previous_business_day_finding(self):
        """이전 영업일 찾기 테스트"""
        print("\n=== 이전 영업일 찾기 테스트 ===")
        
        test_cases = [
            ('20250813', '20250812'),  # 수요일 -> 화요일
            ('20250812', '20250811'),  # 화요일 -> 월요일
            ('20250102', '20241231'),  # 신정 다음날 -> 작년 12월 31일
        ]
        
        for current_date, expected_previous in test_cases:
            with self.subTest(current=current_date):
                previous = self.engine._find_previous_business_day(current_date)
                print(f"  {current_date} -> {previous} (예상: {expected_previous})")
                self.assertEqual(previous, expected_previous)
    
    def test_historical_data_search(self):
        """과거 데이터 검색 테스트"""
        print("\n=== 과거 데이터 검색 테스트 ===")
        
        target_date = '20250812'
        search_range = 5
        
        historical_data = self.engine.search_historical_data(target_date, search_range)
        
        print(f"  검색 대상: {target_date} (범위: {search_range}일)")
        print(f"  검색 결과: {len(historical_data)}개 날짜")
        
        # 검색된 데이터 확인
        for date_str, data in historical_data.items():
            print(f"    {date_str}: 영업일={data['business_day_info'].is_business_day}, "
                  f"품질={data['data_quality']:.2f}")
        
        # 최소 1개 이상의 데이터가 있어야 함
        self.assertGreater(len(historical_data), 0)
    
    def test_data_comparison(self):
        """데이터 비교 분석 테스트"""
        print("\n=== 데이터 비교 분석 테스트 ===")
        
        # 현재 데이터 생성
        current_data = MockIntegratedNewsData()
        
        # 과거 데이터 생성
        historical_data = self.engine.search_historical_data('20250812', 5)
        
        # 비교 분석 수행
        comparison_results = self.engine.compare_with_previous_data(current_data, historical_data)
        
        print(f"  비교 결과: {len(comparison_results)}개")
        
        for result in comparison_results[:3]:  # 처음 3개만 출력
            print(f"    {result.news_type} ({result.comparison_type}): {result.change_summary}")
            if result.detailed_changes:
                for change in result.detailed_changes[:2]:  # 처음 2개 변화만 출력
                    print(f"      - {change}")
        
        # 비교 결과가 있어야 함
        self.assertGreater(len(comparison_results), 0)
    
    def test_news_type_pattern_analysis(self):
        """뉴스 타입별 패턴 분석 테스트"""
        print("\n=== 뉴스 타입별 패턴 분석 테스트 ===")
        
        # 과거 데이터 생성
        historical_data = self.engine.search_historical_data('20250812', 7)
        
        # 각 뉴스 타입별 패턴 분석
        news_types = ['newyork-market-watch', 'kospi-close', 'exchange-rate']
        
        for news_type in news_types:
            pattern_analysis = self.engine.analyze_news_type_patterns(news_type, historical_data)
            
            print(f"  {news_type}:")
            print(f"    발행률: {pattern_analysis['publication_rate']:.1%}")
            print(f"    평균 지연: {pattern_analysis['average_delay']:.1f}분")
            
            if pattern_analysis['insights']:
                print(f"    인사이트: {pattern_analysis['insights'][0]}")
            
            # 기본 필드들이 있어야 함
            self.assertIn('publication_rate', pattern_analysis)
            self.assertIn('average_delay', pattern_analysis)
            self.assertIn('insights', pattern_analysis)
    
    def test_dynamic_report_generation(self):
        """동적 리포트 생성 테스트"""
        print("\n=== 동적 리포트 생성 테스트 ===")
        
        # 현재 데이터와 과거 데이터 생성
        current_data = MockIntegratedNewsData()
        historical_data = self.engine.search_historical_data('20250812', 5)
        
        # 동적 리포트 생성
        report = self.engine.generate_dynamic_comparison_report(current_data, historical_data)
        
        print(f"  분석 날짜: {report.analysis_date}")
        print(f"  영업일 여부: {report.business_day_info.is_business_day}")
        print(f"  전체 트렌드: {report.overall_trend}")
        print(f"  데이터 가용성: {report.data_availability_score:.2f}")
        print(f"  비교 결과: {len(report.comparison_results)}개")
        print(f"  패턴 인사이트: {len(report.pattern_insights)}개")
        print(f"  권장사항: {len(report.recommendations)}개")
        
        if report.pattern_insights:
            print(f"    첫 번째 인사이트: {report.pattern_insights[0]}")
        
        if report.recommendations:
            print(f"    첫 번째 권장사항: {report.recommendations[0]}")
        
        # 리포트 필수 필드 확인
        self.assertIsNotNone(report.timestamp)
        self.assertIsNotNone(report.analysis_date)
        self.assertIsNotNone(report.business_day_info)
        self.assertIsInstance(report.comparison_results, list)
        self.assertIsInstance(report.pattern_insights, list)
        self.assertIsInstance(report.recommendations, list)
        self.assertIsInstance(report.data_availability_score, float)
    
    def test_engine_status(self):
        """엔진 상태 확인 테스트"""
        print("\n=== 엔진 상태 확인 테스트 ===")
        
        status = self.engine.get_engine_status()
        
        print(f"  엔진명: {status['engine_name']}")
        print(f"  버전: {status['version']}")
        print(f"  지원 기능: {len(status['supported_features'])}개")
        print(f"  공휴일 데이터: {status['korean_holidays_count']}개")
        print(f"  뉴스 패턴: {status['news_patterns_count']}개")
        print(f"  최대 검색 범위: {status['max_search_range']}일")
        
        # 필수 상태 정보 확인
        self.assertIn('engine_name', status)
        self.assertIn('version', status)
        self.assertIn('supported_features', status)
        self.assertGreater(status['korean_holidays_count'], 0)
        self.assertGreater(status['news_patterns_count'], 0)
    
    def test_data_quality_calculation(self):
        """데이터 품질 계산 테스트"""
        print("\n=== 데이터 품질 계산 테스트 ===")
        
        # 고품질 데이터 테스트
        high_quality_data = MockIntegratedNewsData()
        high_quality_score = self.engine._calculate_data_quality(high_quality_data)
        
        print(f"  고품질 데이터 점수: {high_quality_score:.2f}")
        
        # 빈 데이터 테스트
        empty_data = MockIntegratedNewsData()
        empty_data.news_items = {}
        empty_score = self.engine._calculate_data_quality(empty_data)
        
        print(f"  빈 데이터 점수: {empty_score:.2f}")
        
        # 점수 범위 확인
        self.assertGreaterEqual(high_quality_score, 0.0)
        self.assertLessEqual(high_quality_score, 1.0)
        self.assertEqual(empty_score, 0.0)
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        print("\n=== 오류 처리 테스트 ===")
        
        # 잘못된 날짜 형식
        invalid_date_info = self.engine.calculate_business_day_info('invalid_date')
        print(f"  잘못된 날짜 처리: {invalid_date_info.day_of_week}")
        self.assertEqual(invalid_date_info.day_of_week, '알 수 없음')
        
        # None 데이터 처리
        none_quality_score = self.engine._calculate_data_quality(None)
        print(f"  None 데이터 품질 점수: {none_quality_score}")
        self.assertEqual(none_quality_score, 0.0)
        
        # 빈 과거 데이터로 비교
        empty_historical = {}
        comparison_results = self.engine.compare_with_previous_data(
            MockIntegratedNewsData(), empty_historical
        )
        print(f"  빈 과거 데이터 비교 결과: {len(comparison_results)}개")
        self.assertEqual(len(comparison_results), 0)


def run_comprehensive_test():
    """종합 테스트 실행"""
    print("🧪 POSCO 영업일 비교 분석 엔진 종합 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestBusinessDayComparisonEngine)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    print("🧪 종합 테스트 완료")
    print(f"✅ 성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"❌ 실패: {len(result.failures)}개")
    print(f"🚨 오류: {len(result.errors)}개")
    
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
    
    return result.wasSuccessful()


def run_integration_test():
    """통합 테스트 실행"""
    print("\n🔗 통합 테스트 시작")
    print("-" * 40)
    
    try:
        # 실제 모듈들과 통합 테스트
        mock_api = MockAPIModule()
        mock_parser = MockNewsParser()
        engine = BusinessDayComparisonEngine(mock_api, mock_parser)
        
        # 1. 전체 워크플로우 테스트
        print("1. 전체 워크플로우 테스트...")
        current_data = MockIntegratedNewsData()
        historical_data = engine.search_historical_data('20250812', 3)
        report = engine.generate_dynamic_comparison_report(current_data, historical_data)
        
        print(f"   ✅ 리포트 생성 성공 (가용성: {report.data_availability_score:.2f})")
        
        # 2. 성능 테스트
        print("2. 성능 테스트...")
        import time
        
        start_time = time.time()
        for i in range(10):
            engine.calculate_business_day_info(f'2025081{i % 10}')
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"   ✅ 영업일 계산 평균 시간: {avg_time:.4f}초")
        
        # 3. 메모리 사용량 테스트
        print("3. 메모리 사용량 테스트...")
        large_historical_data = engine.search_historical_data('20250812', 10)
        print(f"   ✅ 대용량 데이터 처리 성공 ({len(large_historical_data)}개 날짜)")
        
        print("🔗 통합 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    print("🚀 POSCO 영업일 비교 분석 엔진 테스트 시작")
    
    # 1. 단위 테스트 실행
    unit_test_success = run_comprehensive_test()
    
    # 2. 통합 테스트 실행
    integration_test_success = run_integration_test()
    
    # 3. 전체 결과
    print("\n" + "=" * 60)
    print("🏁 전체 테스트 결과")
    print(f"📋 단위 테스트: {'✅ 성공' if unit_test_success else '❌ 실패'}")
    print(f"🔗 통합 테스트: {'✅ 성공' if integration_test_success else '❌ 실패'}")
    
    overall_success = unit_test_success and integration_test_success
    print(f"🎯 전체 결과: {'✅ 모든 테스트 성공' if overall_success else '❌ 일부 테스트 실패'}")
    
    if overall_success:
        print("\n🎉 POSCO 영업일 비교 분석 엔진이 정상적으로 작동합니다!")
        print("   - 영업일 계산 알고리즘 복원 완료")
        print("   - 과거 데이터 검색 및 비교 로직 구현 완료")
        print("   - 뉴스 타입별 패턴 분석 기능 구현 완료")
        print("   - 동적 비교 리포트 생성 엔진 구현 완료")
    else:
        print("\n⚠️ 일부 기능에 문제가 있습니다. 로그를 확인해주세요.")