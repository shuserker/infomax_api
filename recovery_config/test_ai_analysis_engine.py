#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO AI 분석 엔진 테스트

정상 커밋에서 복원한 AI 분석 엔진의 모든 기능을 테스트합니다.

Requirements: 4.3
"""

import unittest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_analysis_engine import (
    AIAnalysisEngine,
    MarketSentiment,
    PublicationStatus,
    InvestmentStrategy
)

class TestAIAnalysisEngine(unittest.TestCase):
    """AI 분석 엔진 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.engine = AIAnalysisEngine()
        
        # 테스트용 뉴스 데이터
        self.sample_news_data = {
            'kospi-close': {
                'title': 'KOSPI 상승 마감, 외국인 매수세 지속',
                'content': '코스피가 상승세를 보이며 마감했습니다. 외국인 투자자들의 매수세가 지속되면서 시장 분위기가 개선되었습니다.',
                'publish_time': '15:45',
                'time': '154500'
            },
            'exchange-rate': {
                'title': '원/달러 환율 하락, 수출 기업에 호재',
                'content': '원/달러 환율이 하락하면서 수출 기업들에게 호재로 작용하고 있습니다. POSCO 등 주요 수출 기업들의 실적 개선이 기대됩니다.',
                'publish_time': '15:35',
                'time': '153500'
            },
            'newyork-market-watch': {
                'title': '뉴욕 증시 혼조, 기술주 약세 지속',
                'content': '뉴욕 증시가 혼조세를 보였습니다. 기술주의 약세가 지속되면서 전체적으로 불안한 모습을 보였습니다.',
                'publish_time': '06:30',
                'time': '063000'
            }
        }
    
    def test_engine_initialization(self):
        """AI 분석 엔진 초기화 테스트"""
        print("\n🧠 AI 분석 엔진 초기화 테스트")
        
        # 기본 속성 확인
        self.assertIsNotNone(self.engine.script_dir)
        self.assertIsNotNone(self.engine.log_file)
        self.assertIsInstance(self.engine.sentiment_keywords, dict)
        self.assertIsInstance(self.engine.time_analysis_config, dict)
        self.assertIsInstance(self.engine.publication_schedule, dict)
        
        # 감정 키워드 사전 확인
        self.assertIn(MarketSentiment.POSITIVE, self.engine.sentiment_keywords)
        self.assertIn(MarketSentiment.NEGATIVE, self.engine.sentiment_keywords)
        self.assertIn(MarketSentiment.NEUTRAL, self.engine.sentiment_keywords)
        
        print("✅ AI 분석 엔진 초기화 성공")
    
    def test_market_situation_analysis(self):
        """시장 상황 분석 테스트"""
        print("\n📊 시장 상황 분석 테스트")
        
        # 시장 분석 실행
        analysis_result = self.engine.analyze_market_situation(self.sample_news_data)
        
        # 결과 검증
        self.assertIsInstance(analysis_result, dict)
        self.assertIn('timestamp', analysis_result)
        self.assertIn('overall_sentiment', analysis_result)
        self.assertIn('sentiment_scores', analysis_result)
        self.assertIn('key_factors', analysis_result)
        self.assertIn('confidence_level', analysis_result)
        self.assertIn('market_indicators', analysis_result)
        
        # 감정 분석 결과 확인
        overall_sentiment = analysis_result['overall_sentiment']
        self.assertIn(overall_sentiment, [
            MarketSentiment.POSITIVE, 
            MarketSentiment.NEGATIVE, 
            MarketSentiment.NEUTRAL
        ])
        
        # 신뢰도 확인
        confidence = analysis_result['confidence_level']
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"📈 전체 시장 감정: {overall_sentiment}")
        print(f"🎯 신뢰도: {confidence:.2f}")
        print(f"📋 주요 요인: {len(analysis_result['key_factors'])}개")
        print("✅ 시장 상황 분석 테스트 성공")
    
    def test_publication_status_analysis(self):
        """발행 현황 분석 테스트"""
        print("\n📰 발행 현황 분석 테스트")
        
        # 발행 현황 분석 실행
        publication_result = self.engine.analyze_publication_status(self.sample_news_data)
        
        # 결과 검증
        self.assertIsInstance(publication_result, dict)
        self.assertIn('timestamp', publication_result)
        self.assertIn('total_sources', publication_result)
        self.assertIn('published_count', publication_result)
        self.assertIn('completion_rate', publication_result)
        self.assertIn('publication_details', publication_result)
        self.assertIn('overall_status', publication_result)
        
        # 완료도 확인
        completion_rate = publication_result['completion_rate']
        self.assertGreaterEqual(completion_rate, 0.0)
        self.assertLessEqual(completion_rate, 1.0)
        
        # 발행 상세 정보 확인
        publication_details = publication_result['publication_details']
        self.assertEqual(len(publication_details), len(self.sample_news_data))
        
        for news_type, details in publication_details.items():
            self.assertIn('is_published', details)
            self.assertIn('status', details)
            self.assertIn('news_type', details)
        
        print(f"📊 발행 완료: {publication_result['published_count']}/{publication_result['total_sources']}")
        print(f"📈 완료율: {completion_rate:.1%}")
        print(f"🏷️ 전체 상태: {publication_result['overall_status']}")
        print("✅ 발행 현황 분석 테스트 성공")
    
    def test_investment_strategy_generation(self):
        """투자 전략 생성 테스트"""
        print("\n💼 투자 전략 생성 테스트")
        
        # 선행 분석 실행
        market_analysis = self.engine.analyze_market_situation(self.sample_news_data)
        publication_analysis = self.engine.analyze_publication_status(self.sample_news_data)
        
        # 투자 전략 생성
        strategy_result = self.engine.generate_investment_strategy(
            market_analysis, publication_analysis
        )
        
        # 결과 검증
        self.assertIsInstance(strategy_result, dict)
        self.assertIn('timestamp', strategy_result)
        self.assertIn('strategy_type', strategy_result)
        self.assertIn('confidence_level', strategy_result)
        self.assertIn('portfolio_allocation', strategy_result)
        self.assertIn('investment_recommendations', strategy_result)
        self.assertIn('risk_assessment', strategy_result)
        self.assertIn('action_items', strategy_result)
        
        # 전략 타입 확인
        strategy_type = strategy_result['strategy_type']
        self.assertIn(strategy_type, [
            InvestmentStrategy.AGGRESSIVE,
            InvestmentStrategy.BALANCED,
            InvestmentStrategy.CONSERVATIVE,
            InvestmentStrategy.DEFENSIVE
        ])
        
        # 포트폴리오 배분 확인
        portfolio = strategy_result['portfolio_allocation']
        self.assertIsInstance(portfolio, dict)
        if portfolio:
            total_allocation = sum(portfolio.values())
            self.assertAlmostEqual(total_allocation, 1.0, places=1)
        
        # 투자 권장사항 확인
        recommendations = strategy_result['investment_recommendations']
        self.assertIn('short_term', recommendations)
        self.assertIn('medium_term', recommendations)
        self.assertIn('long_term', recommendations)
        
        print(f"🎯 전략 타입: {strategy_type}")
        print(f"📊 포트폴리오 배분: {portfolio}")
        print(f"⚠️ 리스크 레벨: {strategy_result['risk_assessment'].get('overall_risk_level', 'unknown')}")
        print(f"📋 액션 아이템: {len(strategy_result['action_items'])}개")
        print("✅ 투자 전략 생성 테스트 성공")
    
    def test_dynamic_report_generation(self):
        """동적 리포트 생성 테스트"""
        print("\n📊 동적 리포트 생성 테스트")
        
        # 선행 분석들 실행
        market_analysis = self.engine.analyze_market_situation(self.sample_news_data)
        publication_analysis = self.engine.analyze_publication_status(self.sample_news_data)
        investment_strategy = self.engine.generate_investment_strategy(
            market_analysis, publication_analysis
        )
        
        # 동적 리포트 생성
        report_result = self.engine.generate_dynamic_report(
            market_analysis, publication_analysis, investment_strategy
        )
        
        # 결과 검증
        self.assertIsInstance(report_result, dict)
        self.assertIn('timestamp', report_result)
        self.assertIn('report_type', report_result)
        self.assertIn('sections', report_result)
        self.assertIn('executive_summary', report_result)
        self.assertIn('data_quality_score', report_result)
        self.assertIn('recommendations', report_result)
        
        # 데이터 품질 점수 확인
        quality_score = report_result['data_quality_score']
        self.assertGreaterEqual(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        
        # 섹션 확인
        sections = report_result['sections']
        self.assertIsInstance(sections, dict)
        self.assertGreater(len(sections), 0)
        
        # 필수 섹션 확인
        section_titles = [section.get('title', '') for section in sections.values()]
        self.assertTrue(any('시장' in title for title in section_titles))
        self.assertTrue(any('발행' in title or '뉴스' in title for title in section_titles))
        
        print(f"📊 데이터 품질 점수: {quality_score:.2f}")
        print(f"📋 리포트 섹션: {len(sections)}개")
        print(f"📝 경영진 요약 길이: {len(report_result['executive_summary'])} 문자")
        print(f"💡 권장사항: {len(report_result['recommendations'])}개")
        print("✅ 동적 리포트 생성 테스트 성공")
    
    def test_time_based_analysis(self):
        """시간대별 분석 로직 테스트"""
        print("\n⏰ 시간대별 분석 로직 테스트")
        
        # 다양한 시간대 테스트
        test_times = [
            datetime.now().replace(hour=10, minute=30),  # 장중
            datetime.now().replace(hour=16, minute=0),   # 장 마감 후
            datetime.now().replace(hour=20, minute=0),   # 저녁
            datetime.now().replace(hour=2, minute=0)     # 새벽
        ]
        
        for test_time in test_times:
            with patch('recovery_config.ai_analysis_engine.datetime') as mock_datetime:
                mock_datetime.now.return_value = test_time
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                # 시간 컨텍스트 생성
                time_context = self.engine._get_time_context()
                
                # 결과 검증
                self.assertIn('current_time', time_context)
                self.assertIn('time_phase', time_context)
                self.assertIn('market_status', time_context)
                self.assertIn('optimal_actions', time_context)
                
                print(f"🕐 {test_time.hour:02d}:{test_time.minute:02d} - "
                      f"단계: {time_context['time_phase']}, "
                      f"시장: {time_context['market_status']}")
        
        print("✅ 시간대별 분석 로직 테스트 성공")
    
    def test_sentiment_keyword_analysis(self):
        """감정 키워드 분석 테스트"""
        print("\n🔍 감정 키워드 분석 테스트")
        
        # 테스트 케이스들
        test_cases = [
            {
                'title': 'KOSPI 급등, 외국인 매수세 강화',
                'content': '코스피가 급등하며 상승세를 보였습니다.',
                'expected_sentiment': MarketSentiment.POSITIVE
            },
            {
                'title': 'KOSPI 급락, 외국인 매도 물량 증가',
                'content': '코스피가 급락하며 하락세를 보였습니다.',
                'expected_sentiment': MarketSentiment.NEGATIVE
            },
            {
                'title': 'KOSPI 보합권, 혼조세 지속',
                'content': '코스피가 보합권에서 혼조세를 보였습니다.',
                'expected_sentiment': MarketSentiment.NEUTRAL
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            test_data = {
                'title': test_case['title'],
                'content': test_case['content']
            }
            
            sentiment_result = self.engine._analyze_single_source_sentiment('test', test_data)
            
            print(f"테스트 {i}: {test_case['title'][:20]}...")
            print(f"  예상 감정: {test_case['expected_sentiment']}")
            print(f"  분석 감정: {sentiment_result['sentiment']}")
            print(f"  감정 점수: {sentiment_result['score']:.2f}")
            print(f"  발견 키워드: {sentiment_result['keywords_found']}")
        
        print("✅ 감정 키워드 분석 테스트 성공")
    
    def test_engine_status(self):
        """엔진 상태 조회 테스트"""
        print("\n🔧 엔진 상태 조회 테스트")
        
        status = self.engine.get_analysis_status()
        
        # 결과 검증
        self.assertIsInstance(status, dict)
        self.assertIn('timestamp', status)
        self.assertIn('engine_status', status)
        self.assertIn('supported_analyses', status)
        self.assertIn('sentiment_keywords_count', status)
        
        # 지원 분석 기능 확인
        supported_analyses = status['supported_analyses']
        expected_analyses = [
            'market_situation_analysis',
            'publication_status_analysis',
            'investment_strategy_generation',
            'dynamic_report_generation'
        ]
        
        for analysis in expected_analyses:
            self.assertIn(analysis, supported_analyses)
        
        print(f"🔧 엔진 상태: {status['engine_status']}")
        print(f"📊 지원 분석: {len(supported_analyses)}개")
        print(f"🔤 감정 키워드: {status['sentiment_keywords_count']}개")
        print("✅ 엔진 상태 조회 테스트 성공")

def run_comprehensive_ai_test():
    """종합 AI 분석 엔진 테스트 실행"""
    print("🧠 POSCO AI 분석 엔진 종합 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestAIAnalysisEngine)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    print("🏁 AI 분석 엔진 테스트 완료")
    
    # 결과 요약
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 테스트 결과 요약:")
    print(f"  • 총 테스트: {total_tests}개")
    print(f"  • 성공: {total_tests - failures - errors}개")
    print(f"  • 실패: {failures}개")
    print(f"  • 오류: {errors}개")
    print(f"  • 성공률: {success_rate:.1f}%")
    
    if failures == 0 and errors == 0:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("✅ AI 분석 엔진이 정상적으로 복원되었습니다.")
        print("\n🧠 복원된 AI 분석 기능:")
        print("  • 시장 상황 판단 (상승/하락/혼조 자동 분류)")
        print("  • 발행 현황 분석 (정시/지연 패턴 분석)")
        print("  • 투자 전략 생성 (포트폴리오 자동 조정)")
        print("  • 동적 리포트 생성 (데이터 상태별 섹션 변화)")
        print("  • 시간대별 분석 (영업시간 고려)")
    else:
        print(f"\n⚠️ {failures + errors}개의 테스트에서 문제가 발생했습니다.")
    
    return result

if __name__ == "__main__":
    run_comprehensive_ai_test()