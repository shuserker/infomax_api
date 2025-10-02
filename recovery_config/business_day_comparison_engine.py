#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 영업일 비교 분석 엔진 완전 복원

정상 커밋 a763ef84의 영업일 계산 알고리즘을 역추적하여 복원한 시스템입니다.

주요 기능:
- 정상 커밋의 영업일 계산 알고리즘 역추적 및 복원
- 과거 데이터 검색 및 비교 로직 (최대 10일 범위 자동 검색)
- 현재/직전 데이터 상태 비교 분석 알고리즘
- 영업일 기준 데이터 유효성 판단 로직 (주말/공휴일 처리)
- 뉴스 타입별 개별 비교 분석 (발행 패턴, 지연 여부 등)
- 동적 비교 리포트 생성 엔진 (데이터 존재 여부에 따른 메시지 변화)

Requirements: 4.4
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import calendar

# 기존 모듈들 import
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from integrated_api_module import IntegratedAPIModule
    from integrated_news_parser import IntegratedNewsParser, IntegratedNewsData
    from ai_analysis_engine import AIAnalysisEngine
except ImportError as e:
    print(f"⚠️ 모듈 import 실패: {e}")
    # 테스트용 더미 클래스들
    class IntegratedAPIModule:
        def get_historical_data(self, start_date, end_date):
            return {}
    
    class IntegratedNewsParser:
        def parse_all_news_data(self, raw_data):
            from types import SimpleNamespace
            result = SimpleNamespace()
            result.success = True
            result.data = SimpleNamespace()
            result.data.news_items = {}
            return result
    
    class IntegratedNewsData:
        def __init__(self):
            self.timestamp = datetime.now().isoformat()
            self.news_items = {}
    
    class AIAnalysisEngine:
        pass


@dataclass
class BusinessDayInfo:
    """영업일 정보"""
    date: str
    is_business_day: bool
    is_weekend: bool
    is_holiday: bool
    day_of_week: str
    previous_business_day: Optional[str]
    next_business_day: Optional[str]


@dataclass
class ComparisonResult:
    """비교 분석 결과"""
    current_date: str
    comparison_date: str
    news_type: str
    current_data: Optional[Dict[str, Any]]
    comparison_data: Optional[Dict[str, Any]]
    comparison_type: str  # 'previous_day', 'same_day_last_week', 'same_date_last_month'
    has_improvement: bool
    has_degradation: bool
    change_summary: str
    detailed_changes: List[str]


@dataclass
class BusinessDayComparisonReport:
    """영업일 비교 분석 리포트"""
    timestamp: str
    analysis_date: str
    business_day_info: BusinessDayInfo
    comparison_results: List[ComparisonResult]
    overall_trend: str
    pattern_insights: List[str]
    recommendations: List[str]
    data_availability_score: float


class BusinessDayComparisonEngine:
    """POSCO 영업일 비교 분석 엔진"""
    
    def __init__(self, api_module: IntegratedAPIModule, news_parser: IntegratedNewsParser):
        """
        영업일 비교 분석 엔진 초기화
        
        Args:
            api_module: 통합 API 모듈
            news_parser: 통합 뉴스 파서
        """
        self.api_module = api_module
        self.news_parser = news_parser
        self.ai_engine = AIAnalysisEngine()
        
        # 한국 공휴일 (2025년 기준)
        self.korean_holidays = {
            '20250101': '신정',
            '20250127': '설날 연휴',
            '20250128': '설날',
            '20250129': '설날 연휴',
            '20250301': '삼일절',
            '20250505': '어린이날',
            '20250506': '어린이날 대체공휴일',
            '20250515': '부처님오신날',
            '20250606': '현충일',
            '20250815': '광복절',
            '20250929': '추석 연휴',
            '20250930': '추석',
            '20251001': '추석 연휴',
            '20251003': '개천절',
            '20251009': '한글날',
            '20251225': '크리스마스'
        }
        
        # 뉴스 타입별 발행 패턴 (정상 커밋 기반)
        self.news_patterns = {
            'newyork-market-watch': {
                'expected_time': '06:30',
                'tolerance_minutes': 30,
                'business_days_only': True,
                'weekend_behavior': 'skip'
            },
            'kospi-close': {
                'expected_time': '15:40',
                'tolerance_minutes': 60,
                'business_days_only': True,
                'weekend_behavior': 'skip'
            },
            'exchange-rate': {
                'expected_time': '15:30',
                'tolerance_minutes': 45,
                'business_days_only': True,
                'weekend_behavior': 'skip'
            }
        }
        
        print("📅 POSCO 영업일 비교 분석 엔진 초기화 완료")
    
    def calculate_business_day_info(self, date_str: str) -> BusinessDayInfo:
        """영업일 계산 알고리즘 (정상 커밋 기반 복원)"""
        try:
            # 날짜 파싱
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            
            # 요일 확인 (0=월요일, 6=일요일)
            weekday = date_obj.weekday()
            day_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
            
            # 주말 여부
            is_weekend = weekday >= 5  # 토요일(5), 일요일(6)
            
            # 공휴일 여부
            is_holiday = date_str in self.korean_holidays
            
            # 영업일 여부 (주말이 아니고 공휴일이 아님)
            is_business_day = not is_weekend and not is_holiday
            
            # 이전/다음 영업일 계산
            previous_business_day = self._find_previous_business_day(date_str)
            next_business_day = self._find_next_business_day(date_str)
            
            return BusinessDayInfo(
                date=date_str,
                is_business_day=is_business_day,
                is_weekend=is_weekend,
                is_holiday=is_holiday,
                day_of_week=day_names[weekday],
                previous_business_day=previous_business_day,
                next_business_day=next_business_day
            )
            
        except Exception as e:
            print(f"❌ 영업일 계산 중 오류: {e}")
            return BusinessDayInfo(
                date=date_str,
                is_business_day=False,
                is_weekend=False,
                is_holiday=False,
                day_of_week='알 수 없음',
                previous_business_day=None,
                next_business_day=None
            )
    
    def _find_previous_business_day(self, date_str: str, max_days: int = 10) -> Optional[str]:
        """이전 영업일 찾기 (최대 10일 범위)"""
        try:
            current_date = datetime.strptime(date_str, '%Y%m%d')
            
            for i in range(1, max_days + 1):
                check_date = current_date - timedelta(days=i)
                check_date_str = check_date.strftime('%Y%m%d')
                
                # 주말이 아니고 공휴일이 아니면 영업일
                if check_date.weekday() < 5 and check_date_str not in self.korean_holidays:
                    return check_date_str
            
            return None
            
        except Exception as e:
            print(f"⚠️ 이전 영업일 찾기 중 오류: {e}")
            return None
    
    def _find_next_business_day(self, date_str: str, max_days: int = 10) -> Optional[str]:
        """다음 영업일 찾기 (최대 10일 범위)"""
        try:
            current_date = datetime.strptime(date_str, '%Y%m%d')
            
            for i in range(1, max_days + 1):
                check_date = current_date + timedelta(days=i)
                check_date_str = check_date.strftime('%Y%m%d')
                
                # 주말이 아니고 공휴일이 아니면 영업일
                if check_date.weekday() < 5 and check_date_str not in self.korean_holidays:
                    return check_date_str
            
            return None
            
        except Exception as e:
            print(f"⚠️ 다음 영업일 찾기 중 오류: {e}")
            return None
    
    def search_historical_data(self, target_date: str, search_range: int = 10) -> Dict[str, Any]:
        """과거 데이터 검색 및 비교 로직 (최대 10일 범위 자동 검색)"""
        historical_data = {}
        
        try:
            print(f"🔍 과거 데이터 검색 시작: {target_date} (범위: {search_range}일)")
            
            target_date_obj = datetime.strptime(target_date, '%Y%m%d')
            search_dates = []
            
            # 검색할 날짜들 생성
            for i in range(1, search_range + 1):
                search_date = target_date_obj - timedelta(days=i)
                search_date_str = search_date.strftime('%Y%m%d')
                search_dates.append(search_date_str)
            
            # 날짜 범위로 과거 데이터 조회
            start_date = search_dates[-1]  # 가장 오래된 날짜
            end_date = search_dates[0]     # 가장 최근 날짜
            
            raw_historical_data = self.api_module.get_historical_data(start_date, end_date)
            
            # 각 날짜별로 데이터 파싱 및 분석
            for date_str in search_dates:
                if date_str in raw_historical_data:
                    # 원시 데이터 파싱
                    parsing_result = self.news_parser.parse_all_news_data(raw_historical_data[date_str])
                    
                    if parsing_result.success and parsing_result.data:
                        # 영업일 정보 추가
                        business_day_info = self.calculate_business_day_info(date_str)
                        
                        historical_data[date_str] = {
                            'raw_data': raw_historical_data[date_str],
                            'parsed_data': parsing_result.data,
                            'business_day_info': business_day_info,
                            'data_quality': self._calculate_data_quality(parsing_result.data)
                        }
                        
                        print(f"✅ {date_str} 데이터 수집 완료 (영업일: {business_day_info.is_business_day})")
                    else:
                        print(f"⚠️ {date_str} 데이터 파싱 실패")
                else:
                    print(f"❌ {date_str} 데이터 없음")
            
            print(f"🔍 과거 데이터 검색 완료: {len(historical_data)}개 날짜")
            return historical_data
            
        except Exception as e:
            print(f"❌ 과거 데이터 검색 중 오류: {e}")
            return {}
    
    def compare_with_previous_data(self, current_data: IntegratedNewsData, 
                                 historical_data: Dict[str, Any]) -> List[ComparisonResult]:
        """현재/직전 데이터 상태 비교 분석 알고리즘"""
        comparison_results = []
        
        try:
            print("📊 현재/직전 데이터 비교 분석 시작")
            
            # timestamp에서 날짜 부분 추출 (YYYYMMDD 형식)
            if hasattr(current_data, 'timestamp') and current_data.timestamp:
                timestamp_str = str(current_data.timestamp)
                if len(timestamp_str) >= 8 and timestamp_str[:8].isdigit():
                    current_date = timestamp_str[:8]
                else:
                    current_date = datetime.now().strftime('%Y%m%d')
            else:
                current_date = datetime.now().strftime('%Y%m%d')
            current_business_day = self.calculate_business_day_info(current_date)
            
            # 비교 대상 날짜들 결정
            comparison_dates = self._determine_comparison_dates(current_date, historical_data)
            
            # 각 뉴스 타입별로 비교 분석
            for news_type in current_data.news_items.keys():
                current_news_data = current_data.news_items[news_type]
                
                for comparison_type, comparison_date in comparison_dates.items():
                    if comparison_date and comparison_date in historical_data:
                        historical_news_data = historical_data[comparison_date]['parsed_data'].news_items.get(news_type)
                        
                        comparison_result = self._compare_news_data(
                            current_date, comparison_date, news_type,
                            current_news_data, historical_news_data, comparison_type
                        )
                        
                        comparison_results.append(comparison_result)
            
            print(f"📊 비교 분석 완료: {len(comparison_results)}개 비교 결과")
            return comparison_results
            
        except Exception as e:
            print(f"❌ 데이터 비교 분석 중 오류: {e}")
            return []
    
    def _determine_comparison_dates(self, current_date: str, historical_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """비교 대상 날짜들 결정"""
        comparison_dates = {
            'previous_business_day': None,
            'same_day_last_week': None,
            'same_date_last_month': None
        }
        
        try:
            current_date_obj = datetime.strptime(current_date, '%Y%m%d')
            current_business_day = self.calculate_business_day_info(current_date)
            
            # 1. 이전 영업일
            if current_business_day.previous_business_day:
                comparison_dates['previous_business_day'] = current_business_day.previous_business_day
            
            # 2. 지난주 같은 요일
            last_week_date = current_date_obj - timedelta(days=7)
            last_week_date_str = last_week_date.strftime('%Y%m%d')
            if last_week_date_str in historical_data:
                comparison_dates['same_day_last_week'] = last_week_date_str
            
            # 3. 지난달 같은 날
            try:
                if current_date_obj.month == 1:
                    last_month_date = current_date_obj.replace(year=current_date_obj.year - 1, month=12)
                else:
                    last_month_date = current_date_obj.replace(month=current_date_obj.month - 1)
                
                last_month_date_str = last_month_date.strftime('%Y%m%d')
                if last_month_date_str in historical_data:
                    comparison_dates['same_date_last_month'] = last_month_date_str
            except ValueError:
                # 날짜가 유효하지 않은 경우 (예: 3월 31일 -> 2월 31일)
                pass
            
        except Exception as e:
            print(f"⚠️ 비교 날짜 결정 중 오류: {e}")
        
        return comparison_dates
    
    def _compare_news_data(self, current_date: str, comparison_date: str, news_type: str,
                          current_data: Any, comparison_data: Any, comparison_type: str) -> ComparisonResult:
        """개별 뉴스 데이터 비교"""
        detailed_changes = []
        has_improvement = False
        has_degradation = False
        
        try:
            # 데이터 존재 여부 비교
            current_exists = current_data is not None and hasattr(current_data, 'title')
            comparison_exists = comparison_data is not None and hasattr(comparison_data, 'title')
            
            if current_exists and not comparison_exists:
                detailed_changes.append("현재 데이터 있음, 비교 데이터 없음")
                has_improvement = True
            elif not current_exists and comparison_exists:
                detailed_changes.append("현재 데이터 없음, 비교 데이터 있음")
                has_degradation = True
            elif not current_exists and not comparison_exists:
                detailed_changes.append("양쪽 모두 데이터 없음")
            else:
                # 양쪽 모두 데이터가 있는 경우 상세 비교
                detailed_changes.extend(self._detailed_news_comparison(current_data, comparison_data))
                
                # 개선/악화 판단
                if hasattr(current_data, 'is_latest') and hasattr(comparison_data, 'is_latest'):
                    if current_data.is_latest and not comparison_data.is_latest:
                        has_improvement = True
                    elif not current_data.is_latest and comparison_data.is_latest:
                        has_degradation = True
            
            # 변화 요약 생성
            change_summary = self._generate_change_summary(
                current_exists, comparison_exists, has_improvement, has_degradation
            )
            
        except Exception as e:
            detailed_changes.append(f"비교 중 오류: {e}")
            change_summary = "비교 불가"
        
        return ComparisonResult(
            current_date=current_date,
            comparison_date=comparison_date,
            news_type=news_type,
            current_data=current_data.__dict__ if current_data and hasattr(current_data, '__dict__') else None,
            comparison_data=comparison_data.__dict__ if comparison_data and hasattr(comparison_data, '__dict__') else None,
            comparison_type=comparison_type,
            has_improvement=has_improvement,
            has_degradation=has_degradation,
            change_summary=change_summary,
            detailed_changes=detailed_changes
        )
    
    def _detailed_news_comparison(self, current_data: Any, comparison_data: Any) -> List[str]:
        """상세 뉴스 데이터 비교"""
        changes = []
        
        try:
            # 상태 비교
            if hasattr(current_data, 'status') and hasattr(comparison_data, 'status'):
                if current_data.status != comparison_data.status:
                    changes.append(f"상태 변화: {comparison_data.status} → {current_data.status}")
            
            # 지연 시간 비교
            if hasattr(current_data, 'delay_minutes') and hasattr(comparison_data, 'delay_minutes'):
                current_delay = getattr(current_data, 'delay_minutes', 0)
                comparison_delay = getattr(comparison_data, 'delay_minutes', 0)
                
                if current_delay != comparison_delay:
                    changes.append(f"지연 시간 변화: {comparison_delay}분 → {current_delay}분")
            
            # 제목 변화 (간단히)
            if hasattr(current_data, 'title') and hasattr(comparison_data, 'title'):
                if current_data.title != comparison_data.title:
                    changes.append("제목 변경됨")
            
        except Exception as e:
            changes.append(f"상세 비교 중 오류: {e}")
        
        return changes
    
    def _generate_change_summary(self, current_exists: bool, comparison_exists: bool,
                               has_improvement: bool, has_degradation: bool) -> str:
        """변화 요약 생성"""
        if not current_exists and not comparison_exists:
            return "데이터 없음"
        elif current_exists and not comparison_exists:
            return "신규 데이터 발행"
        elif not current_exists and comparison_exists:
            return "데이터 발행 중단"
        elif has_improvement:
            return "상태 개선"
        elif has_degradation:
            return "상태 악화"
        else:
            return "상태 유지"
    
    def analyze_news_type_patterns(self, news_type: str, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """뉴스 타입별 개별 비교 분석 (발행 패턴, 지연 여부 등)"""
        pattern_analysis = {
            'news_type': news_type,
            'analysis_period': f"{len(historical_data)}일",
            'publication_rate': 0.0,
            'average_delay': 0.0,
            'delay_trend': 'stable',
            'business_day_pattern': {},
            'weekend_pattern': {},
            'insights': []
        }
        
        try:
            print(f"📈 {news_type} 발행 패턴 분석 시작")
            
            total_days = 0
            published_days = 0
            total_delay = 0
            delay_count = 0
            business_day_stats = {'published': 0, 'total': 0}
            weekend_stats = {'published': 0, 'total': 0}
            
            # 각 날짜별 데이터 분석
            for date_str, day_data in historical_data.items():
                total_days += 1
                business_day_info = day_data['business_day_info']
                parsed_data = day_data['parsed_data']
                
                # 해당 뉴스 타입 데이터 확인
                news_data = parsed_data.news_items.get(news_type)
                
                if business_day_info.is_business_day:
                    business_day_stats['total'] += 1
                    if news_data and hasattr(news_data, 'title'):
                        business_day_stats['published'] += 1
                        published_days += 1
                        
                        # 지연 시간 분석
                        if hasattr(news_data, 'delay_minutes'):
                            delay_minutes = getattr(news_data, 'delay_minutes', 0)
                            if delay_minutes > 0:
                                total_delay += delay_minutes
                                delay_count += 1
                else:
                    weekend_stats['total'] += 1
                    if news_data and hasattr(news_data, 'title'):
                        weekend_stats['published'] += 1
            
            # 발행률 계산
            if total_days > 0:
                pattern_analysis['publication_rate'] = published_days / total_days
            
            # 평균 지연 시간 계산
            if delay_count > 0:
                pattern_analysis['average_delay'] = total_delay / delay_count
            
            # 영업일/주말 패턴
            if business_day_stats['total'] > 0:
                pattern_analysis['business_day_pattern'] = {
                    'publication_rate': business_day_stats['published'] / business_day_stats['total'],
                    'published_days': business_day_stats['published'],
                    'total_days': business_day_stats['total']
                }
            
            if weekend_stats['total'] > 0:
                pattern_analysis['weekend_pattern'] = {
                    'publication_rate': weekend_stats['published'] / weekend_stats['total'],
                    'published_days': weekend_stats['published'],
                    'total_days': weekend_stats['total']
                }
            
            # 인사이트 생성
            pattern_analysis['insights'] = self._generate_pattern_insights(
                news_type, pattern_analysis
            )
            
            print(f"📈 {news_type} 패턴 분석 완료 (발행률: {pattern_analysis['publication_rate']:.1%})")
            return pattern_analysis
            
        except Exception as e:
            print(f"❌ {news_type} 패턴 분석 중 오류: {e}")
            pattern_analysis['error'] = str(e)
            return pattern_analysis
    
    def _generate_pattern_insights(self, news_type: str, pattern_analysis: Dict[str, Any]) -> List[str]:
        """패턴 분석 인사이트 생성"""
        insights = []
        
        try:
            publication_rate = pattern_analysis.get('publication_rate', 0.0)
            average_delay = pattern_analysis.get('average_delay', 0.0)
            
            # 발행률 기반 인사이트
            if publication_rate >= 0.9:
                insights.append(f"{news_type}: 매우 안정적인 발행 패턴 (발행률 {publication_rate:.1%})")
            elif publication_rate >= 0.7:
                insights.append(f"{news_type}: 양호한 발행 패턴 (발행률 {publication_rate:.1%})")
            elif publication_rate >= 0.5:
                insights.append(f"{news_type}: 불안정한 발행 패턴 (발행률 {publication_rate:.1%})")
            else:
                insights.append(f"{news_type}: 심각한 발행 문제 (발행률 {publication_rate:.1%})")
            
            # 지연 시간 기반 인사이트
            if average_delay > 60:
                insights.append(f"{news_type}: 심각한 지연 발생 (평균 {average_delay:.0f}분)")
            elif average_delay > 30:
                insights.append(f"{news_type}: 지연 발생 (평균 {average_delay:.0f}분)")
            elif average_delay > 0:
                insights.append(f"{news_type}: 경미한 지연 (평균 {average_delay:.0f}분)")
            else:
                insights.append(f"{news_type}: 정시 발행")
            
            # 영업일 패턴 인사이트
            business_pattern = pattern_analysis.get('business_day_pattern', {})
            if business_pattern:
                business_rate = business_pattern.get('publication_rate', 0.0)
                if business_rate >= 0.9:
                    insights.append(f"{news_type}: 영업일 발행 매우 안정적")
                elif business_rate < 0.7:
                    insights.append(f"{news_type}: 영업일 발행 불안정")
            
            # 주말 패턴 인사이트
            weekend_pattern = pattern_analysis.get('weekend_pattern', {})
            if weekend_pattern and weekend_pattern.get('total_days', 0) > 0:
                weekend_rate = weekend_pattern.get('publication_rate', 0.0)
                if weekend_rate > 0.1:
                    insights.append(f"{news_type}: 주말에도 간헐적 발행")
                else:
                    insights.append(f"{news_type}: 주말 발행 없음 (정상)")
            
        except Exception as e:
            insights.append(f"인사이트 생성 중 오류: {e}")
        
        return insights
    
    def generate_dynamic_comparison_report(self, current_data: IntegratedNewsData,
                                         historical_data: Dict[str, Any]) -> BusinessDayComparisonReport:
        """동적 비교 리포트 생성 엔진 (데이터 존재 여부에 따른 메시지 변화)"""
        try:
            print("📋 동적 비교 리포트 생성 시작")
            
            current_date = datetime.now().strftime('%Y%m%d')
            business_day_info = self.calculate_business_day_info(current_date)
            
            # 비교 분석 수행
            comparison_results = self.compare_with_previous_data(current_data, historical_data)
            
            # 전체 트렌드 분석
            overall_trend = self._analyze_overall_trend(comparison_results)
            
            # 패턴 인사이트 생성
            pattern_insights = []
            for news_type in current_data.news_items.keys():
                pattern_analysis = self.analyze_news_type_patterns(news_type, historical_data)
                pattern_insights.extend(pattern_analysis.get('insights', []))
            
            # 권장사항 생성
            recommendations = self._generate_comparison_recommendations(
                comparison_results, business_day_info, historical_data
            )
            
            # 데이터 가용성 점수 계산
            data_availability_score = self._calculate_data_availability_score(
                current_data, historical_data
            )
            
            report = BusinessDayComparisonReport(
                timestamp=datetime.now().isoformat(),
                analysis_date=current_date,
                business_day_info=business_day_info,
                comparison_results=comparison_results,
                overall_trend=overall_trend,
                pattern_insights=pattern_insights,
                recommendations=recommendations,
                data_availability_score=data_availability_score
            )
            
            print(f"📋 동적 비교 리포트 생성 완료 (가용성 점수: {data_availability_score:.2f})")
            return report
            
        except Exception as e:
            print(f"❌ 동적 비교 리포트 생성 중 오류: {e}")
            # 오류 시 기본 리포트 반환
            return BusinessDayComparisonReport(
                timestamp=datetime.now().isoformat(),
                analysis_date=datetime.now().strftime('%Y%m%d'),
                business_day_info=self.calculate_business_day_info(datetime.now().strftime('%Y%m%d')),
                comparison_results=[],
                overall_trend='분석 불가',
                pattern_insights=[f"리포트 생성 중 오류: {e}"],
                recommendations=["시스템 점검 필요"],
                data_availability_score=0.0
            )
    
    def _analyze_overall_trend(self, comparison_results: List[ComparisonResult]) -> str:
        """전체 트렌드 분석"""
        if not comparison_results:
            return "데이터 부족"
        
        improvement_count = sum(1 for result in comparison_results if result.has_improvement)
        degradation_count = sum(1 for result in comparison_results if result.has_degradation)
        
        if improvement_count > degradation_count:
            return "개선 추세"
        elif degradation_count > improvement_count:
            return "악화 추세"
        else:
            return "안정 추세"
    
    def _generate_comparison_recommendations(self, comparison_results: List[ComparisonResult],
                                           business_day_info: BusinessDayInfo,
                                           historical_data: Dict[str, Any]) -> List[str]:
        """비교 분석 기반 권장사항 생성"""
        recommendations = []
        
        try:
            # 영업일 기반 권장사항
            if not business_day_info.is_business_day:
                if business_day_info.is_weekend:
                    recommendations.append("주말로 인해 뉴스 발행이 제한적일 수 있습니다")
                elif business_day_info.is_holiday:
                    recommendations.append("공휴일로 인해 뉴스 발행이 없을 수 있습니다")
            
            # 비교 결과 기반 권장사항
            degradation_count = sum(1 for result in comparison_results if result.has_degradation)
            if degradation_count > len(comparison_results) * 0.5:
                recommendations.append("전반적인 뉴스 발행 상태가 악화되었습니다 - 시스템 점검 필요")
            
            improvement_count = sum(1 for result in comparison_results if result.has_improvement)
            if improvement_count > len(comparison_results) * 0.7:
                recommendations.append("뉴스 발행 상태가 개선되었습니다 - 현재 상태 유지")
            
            # 데이터 가용성 기반 권장사항
            if len(historical_data) < 5:
                recommendations.append("과거 데이터가 부족합니다 - 더 많은 데이터 수집 필요")
            
            # 기본 권장사항
            if not recommendations:
                recommendations.append("정상적인 모니터링 상태를 유지하세요")
            
        except Exception as e:
            recommendations.append(f"권장사항 생성 중 오류: {e}")
        
        return recommendations
    
    def _calculate_data_availability_score(self, current_data: IntegratedNewsData,
                                         historical_data: Dict[str, Any]) -> float:
        """데이터 가용성 점수 계산"""
        try:
            # 현재 데이터 점수 (0.5 가중치)
            current_score = 0.0
            if current_data and current_data.news_items:
                available_news = sum(1 for item in current_data.news_items.values() 
                                   if item and hasattr(item, 'title'))
                current_score = available_news / len(current_data.news_items)
            
            # 과거 데이터 점수 (0.5 가중치)
            historical_score = 0.0
            if historical_data:
                total_days = len(historical_data)
                available_days = sum(1 for day_data in historical_data.values()
                                   if day_data.get('parsed_data') and day_data['parsed_data'].news_items)
                historical_score = available_days / total_days if total_days > 0 else 0.0
            
            # 가중 평균
            final_score = (current_score * 0.5) + (historical_score * 0.5)
            return min(final_score, 1.0)
            
        except Exception as e:
            print(f"⚠️ 데이터 가용성 점수 계산 중 오류: {e}")
            return 0.0
    
    def _calculate_data_quality(self, parsed_data: IntegratedNewsData) -> float:
        """데이터 품질 점수 계산"""
        try:
            if not parsed_data or not parsed_data.news_items:
                return 0.0
            
            total_items = len(parsed_data.news_items)
            quality_score = 0.0
            
            for news_item in parsed_data.news_items.values():
                if news_item and hasattr(news_item, 'title'):
                    item_score = 0.5  # 기본 점수
                    
                    # 최신 데이터인 경우 추가 점수
                    if hasattr(news_item, 'is_latest') and news_item.is_latest:
                        item_score += 0.3
                    
                    # 지연이 적은 경우 추가 점수
                    if hasattr(news_item, 'delay_minutes'):
                        delay = getattr(news_item, 'delay_minutes', 0)
                        if delay <= 30:
                            item_score += 0.2
                    
                    quality_score += min(item_score, 1.0)
            
            return quality_score / total_items if total_items > 0 else 0.0
            
        except Exception as e:
            print(f"⚠️ 데이터 품질 점수 계산 중 오류: {e}")
            return 0.0
    
    def get_engine_status(self) -> Dict[str, Any]:
        """엔진 상태 정보 반환"""
        return {
            'timestamp': datetime.now().isoformat(),
            'engine_name': 'BusinessDayComparisonEngine',
            'version': '1.0.0',
            'supported_features': [
                'business_day_calculation',
                'historical_data_search',
                'data_comparison_analysis',
                'pattern_analysis',
                'dynamic_report_generation'
            ],
            'korean_holidays_count': len(self.korean_holidays),
            'news_patterns_count': len(self.news_patterns),
            'max_search_range': 10
        }


if __name__ == "__main__":
    # 테스트 코드
    print("=== POSCO 영업일 비교 분석 엔진 테스트 ===")
    
    # 임시 API 모듈과 파서 (테스트용)
    class MockAPIModule:
        def get_historical_data(self, start_date, end_date):
            return {}
    
    class MockNewsParser:
        def parse_all_news_data(self, raw_data):
            from types import SimpleNamespace
            result = SimpleNamespace()
            result.success = True
            result.data = SimpleNamespace()
            result.data.news_items = {}
            return result
    
    # 엔진 초기화
    mock_api = MockAPIModule()
    mock_parser = MockNewsParser()
    engine = BusinessDayComparisonEngine(mock_api, mock_parser)
    
    # 영업일 계산 테스트
    test_dates = ['20250812', '20250810', '20250811']  # 월요일, 토요일, 일요일
    
    print("\n1. 영업일 계산 테스트:")
    for date_str in test_dates:
        business_day_info = engine.calculate_business_day_info(date_str)
        print(f"  {date_str} ({business_day_info.day_of_week}): "
              f"영업일={business_day_info.is_business_day}, "
              f"주말={business_day_info.is_weekend}, "
              f"공휴일={business_day_info.is_holiday}")
        
        if business_day_info.previous_business_day:
            print(f"    이전 영업일: {business_day_info.previous_business_day}")
        if business_day_info.next_business_day:
            print(f"    다음 영업일: {business_day_info.next_business_day}")
    
    # 엔진 상태 확인
    print("\n2. 엔진 상태:")
    status = engine.get_engine_status()
    print(f"  엔진명: {status['engine_name']}")
    print(f"  버전: {status['version']}")
    print(f"  지원 기능: {len(status['supported_features'])}개")
    print(f"  공휴일 데이터: {status['korean_holidays_count']}개")
    
    print("\n테스트 완료")