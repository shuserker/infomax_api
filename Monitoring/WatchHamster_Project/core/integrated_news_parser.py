# -*- coding: utf-8 -*-
"""
통합 뉴스 데이터 파싱 시스템

정상 커밋 a763ef84의 원본 로직을 기반으로 복원된 통합 뉴스 파싱 모듈입니다.

주요 기능:
- 모든 뉴스 타입 통합 파싱
- 각 데이터 소스별 전문 파서 연동
- 상태 판단 로직 통합
- 종합 분석 및 요약 생성
- 캐싱 및 성능 최적화

작성자: AI Assistant
복원 일시: 2025-08-12
수정일: 2025-08-16 (워치햄스터 공통 모듈로 복사)
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
import logging

try:
    from .news_data_parser import NewsDataParser, NewsItem, NewsStatus
    from .newyork_market_parser import NewYorkMarketParser, NewYorkMarketData
    from .kospi_close_parser import KospiCloseParser, KospiCloseData
    from .exchange_rate_parser import ExchangeRateParser, ExchangeRateData
except ImportError:
    from news_data_parser import NewsDataParser, NewsItem, NewsStatus
    from newyork_market_parser import NewYorkMarketParser, NewYorkMarketData
    from kospi_close_parser import KospiCloseParser, KospiCloseData
    from exchange_rate_parser import ExchangeRateParser, ExchangeRateData


@dataclass
class IntegratedNewsData:
    """통합 뉴스 데이터"""
    timestamp: str
    overall_status: str
    news_items: Dict[str, NewsItem]
    specialized_data: Dict[str, Any]
    market_summary: str
    status_counts: Dict[str, int]
    delay_analysis: Dict[str, Any]
    recommendations: List[str]


@dataclass
class ParsingResult:
    """파싱 결과"""
    success: bool
    data: Optional[IntegratedNewsData]
    errors: List[str]
    warnings: List[str]
    processing_time: float


class IntegratedNewsParser:
    """
    통합 뉴스 데이터 파싱 시스템
    
    모든 뉴스 타입을 통합하여 파싱하고 분석하는 메인 클래스입니다.
    """
    
    def __init__(self, enable_caching: bool = True):
        """통합 파서 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 개별 파서들 초기화
        self.base_parser = NewsDataParser()
        self.newyork_parser = NewYorkMarketParser()
        self.kospi_parser = KospiCloseParser()
        self.exchange_parser = ExchangeRateParser()
        
        # 캐싱 설정
        self.enable_caching = enable_caching
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 300  # 5분
        
        # 파싱 통계
        self.parsing_stats = {
            'total_parsed': 0,
            'successful_parses': 0,
            'failed_parses': 0,
            'cache_hits': 0,
            'avg_processing_time': 0.0
        }
        
        self.logger.info("통합 뉴스 파서 초기화 완료")
    
    def parse_all_news_data(self, raw_data: Dict[str, Any]) -> ParsingResult:
        """모든 뉴스 데이터 통합 파싱"""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # 캐시 확인
            cache_key = self._generate_cache_key(raw_data)
            if self.enable_caching and self._is_cache_valid(cache_key):
                self.parsing_stats['cache_hits'] += 1
                self.logger.info("캐시에서 파싱 결과 반환")
                return ParsingResult(
                    success=True,
                    data=self.cache[cache_key],
                    errors=[],
                    warnings=["캐시에서 로드됨"],
                    processing_time=time.time() - start_time
                )
            
            self.logger.info("뉴스 데이터 통합 파싱 시작")
            
            # 1. 기본 뉴스 파싱
            news_items = self.base_parser.parse_news_data(raw_data)
            if not news_items:
                errors.append("기본 뉴스 파싱 실패")
                return self._create_error_result(errors, warnings, start_time)
            
            # 2. 전문 파서로 상세 분석
            specialized_data = {}
            
            # 뉴욕마켓워치 전문 파싱
            if 'newyork-market-watch' in raw_data:
                try:
                    ny_data = self.newyork_parser.parse_newyork_market_data(
                        raw_data['newyork-market-watch']
                    )
                    specialized_data['newyork-market-watch'] = asdict(ny_data)
                except Exception as e:
                    warnings.append(f"뉴욕마켓워치 전문 파싱 실패: {e}")
            
            # 증시마감 전문 파싱
            if 'kospi-close' in raw_data:
                try:
                    kospi_data = self.kospi_parser.parse_kospi_close_data(
                        raw_data['kospi-close']
                    )
                    specialized_data['kospi-close'] = asdict(kospi_data)
                except Exception as e:
                    warnings.append(f"증시마감 전문 파싱 실패: {e}")
            
            # 서환마감 전문 파싱
            if 'exchange-rate' in raw_data:
                try:
                    exchange_data = self.exchange_parser.parse_exchange_rate_data(
                        raw_data['exchange-rate']
                    )
                    specialized_data['exchange-rate'] = asdict(exchange_data)
                except Exception as e:
                    warnings.append(f"서환마감 전문 파싱 실패: {e}")
            
            # 3. 통합 분석
            integrated_data = self._create_integrated_analysis(
                news_items, specialized_data
            )
            
            # 4. 캐시 저장
            if self.enable_caching:
                self._update_cache(cache_key, integrated_data)
            
            # 5. 통계 업데이트
            processing_time = time.time() - start_time
            self._update_parsing_stats(True, processing_time)
            
            self.logger.info(f"뉴스 데이터 통합 파싱 완료: {processing_time:.2f}초")
            
            return ParsingResult(
                success=True,
                data=integrated_data,
                errors=errors,
                warnings=warnings,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"통합 파싱 오류: {e}")
            errors.append(f"통합 파싱 오류: {e}")
            self._update_parsing_stats(False, time.time() - start_time)
            return self._create_error_result(errors, warnings, start_time)
    
    def _create_integrated_analysis(self, news_items: Dict[str, NewsItem], 
                                  specialized_data: Dict[str, Any]) -> IntegratedNewsData:
        """통합 분석 데이터 생성"""
        # 전체 상태 판단
        overall_status = self._determine_overall_status(news_items)
        
        # 상태별 카운트
        status_counts = self._count_status(news_items)
        
        # 지연 분석
        delay_analysis = self._analyze_delays(news_items)
        
        # 시장 요약 생성
        market_summary = self._generate_market_summary(news_items, specialized_data)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(news_items, specialized_data)
        
        return IntegratedNewsData(
            timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            news_items=news_items,
            specialized_data=specialized_data,
            market_summary=market_summary,
            status_counts=status_counts,
            delay_analysis=delay_analysis,
            recommendations=recommendations
        )
    
    def _determine_overall_status(self, news_items: Dict[str, NewsItem]) -> str:
        """전체 상태 판단"""
        if not news_items:
            return 'no_data'
        
        status_priority = {
            NewsStatus.ERROR: 5,
            NewsStatus.DELAYED: 4,
            NewsStatus.NO_DATA: 3,
            NewsStatus.INVALID: 2,
            NewsStatus.LATEST: 1,
            NewsStatus.EARLY: 1,
            NewsStatus.OLD: 0
        }
        
        max_priority = 0
        dominant_status = NewsStatus.OLD
        
        for news_item in news_items.values():
            priority = status_priority.get(news_item.status, 0)
            if priority > max_priority:
                max_priority = priority
                dominant_status = news_item.status
        
        # 상태별 매핑
        status_mapping = {
            NewsStatus.ERROR: 'error',
            NewsStatus.DELAYED: 'delayed',
            NewsStatus.NO_DATA: 'no_data',
            NewsStatus.INVALID: 'invalid',
            NewsStatus.LATEST: 'latest',
            NewsStatus.EARLY: 'latest',
            NewsStatus.OLD: 'old'
        }
        
        return status_mapping.get(dominant_status, 'unknown')
    
    def _count_status(self, news_items: Dict[str, NewsItem]) -> Dict[str, int]:
        """상태별 카운트"""
        counts = {
            'latest': 0,
            'delayed': 0,
            'old': 0,
            'no_data': 0,
            'error': 0,
            'total': len(news_items)
        }
        
        for news_item in news_items.values():
            if news_item.status in [NewsStatus.LATEST, NewsStatus.EARLY]:
                counts['latest'] += 1
            elif news_item.status == NewsStatus.DELAYED:
                counts['delayed'] += 1
            elif news_item.status == NewsStatus.OLD:
                counts['old'] += 1
            elif news_item.status == NewsStatus.NO_DATA:
                counts['no_data'] += 1
            elif news_item.status == NewsStatus.ERROR:
                counts['error'] += 1
        
        return counts
    
    def _analyze_delays(self, news_items: Dict[str, NewsItem]) -> Dict[str, Any]:
        """지연 분석"""
        delayed_items = [item for item in news_items.values() if item.is_delayed]
        
        if not delayed_items:
            return {
                'has_delays': False,
                'delayed_count': 0,
                'max_delay_minutes': 0,
                'avg_delay_minutes': 0,
                'delayed_news_types': []
            }
        
        delay_minutes = [item.delay_minutes for item in delayed_items]
        
        return {
            'has_delays': True,
            'delayed_count': len(delayed_items),
            'max_delay_minutes': max(delay_minutes),
            'avg_delay_minutes': sum(delay_minutes) / len(delay_minutes),
            'delayed_news_types': [item.news_type for item in delayed_items]
        }
    
    def _generate_market_summary(self, news_items: Dict[str, NewsItem], 
                               specialized_data: Dict[str, Any]) -> str:
        """시장 요약 생성"""
        summary_parts = []
        
        # 뉴스 상태 요약
        latest_count = sum(1 for item in news_items.values() if item.is_latest)
        delayed_count = sum(1 for item in news_items.values() if item.is_delayed)
        
        if latest_count == len(news_items):
            summary_parts.append("모든 뉴스 최신 상태")
        elif delayed_count > 0:
            summary_parts.append(f"{delayed_count}개 뉴스 지연")
        else:
            summary_parts.append("뉴스 상태 혼재")
        
        # 전문 분석 요약
        if 'newyork-market-watch' in specialized_data:
            ny_data = specialized_data['newyork-market-watch']
            summary_parts.append(f"뉴욕증시 {ny_data.get('market_situation', '혼조')}")
        
        if 'kospi-close' in specialized_data:
            kospi_data = specialized_data['kospi-close']
            summary_parts.append(f"한국증시 {kospi_data.get('market_situation', '혼조')}")
        
        if 'exchange-rate' in specialized_data:
            exchange_data = specialized_data['exchange-rate']
            summary_parts.append(f"원화 {exchange_data.get('market_situation', '보합')}")
        
        return " | ".join(summary_parts) if summary_parts else "데이터 부족"
    
    def _generate_recommendations(self, news_items: Dict[str, NewsItem], 
                                specialized_data: Dict[str, Any]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 지연 관련 권장사항
        delayed_items = [item for item in news_items.values() if item.is_delayed]
        if delayed_items:
            max_delay = max(item.delay_minutes for item in delayed_items)
            if max_delay > 60:
                recommendations.append("심각한 지연 발생 - 시스템 점검 필요")
            elif max_delay > 30:
                recommendations.append("지연 발생 - 모니터링 강화 필요")
            else:
                recommendations.append("경미한 지연 - 정상 범위")
        
        # 데이터 품질 관련 권장사항
        error_items = [item for item in news_items.values() if item.status == NewsStatus.ERROR]
        if error_items:
            recommendations.append(f"{len(error_items)}개 뉴스 파싱 오류 - 데이터 소스 확인 필요")
        
        no_data_items = [item for item in news_items.values() if item.status == NewsStatus.NO_DATA]
        if no_data_items:
            recommendations.append(f"{len(no_data_items)}개 뉴스 데이터 없음 - API 연결 확인 필요")
        
        # 기본 권장사항
        if not recommendations:
            recommendations.append("정상 운영 중 - 지속적인 모니터링 유지")
        
        return recommendations[:5]  # 최대 5개로 제한
    
    def _generate_cache_key(self, raw_data: Dict[str, Any]) -> str:
        """캐시 키 생성"""
        # 데이터의 해시값을 기반으로 캐시 키 생성
        data_str = json.dumps(raw_data, sort_keys=True, default=str)
        return f"news_parse_{hash(data_str)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 확인"""
        if cache_key not in self.cache:
            return False
        
        if cache_key not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[cache_key]
        return (datetime.now() - cache_time).total_seconds() < self.cache_duration
    
    def _update_cache(self, cache_key: str, data: IntegratedNewsData):
        """캐시 업데이트"""
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = datetime.now()
        
        # 캐시 크기 제한 (최대 100개)
        if len(self.cache) > 100:
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]
    
    def _update_parsing_stats(self, success: bool, processing_time: float):
        """파싱 통계 업데이트"""
        self.parsing_stats['total_parsed'] += 1
        
        if success:
            self.parsing_stats['successful_parses'] += 1
        else:
            self.parsing_stats['failed_parses'] += 1
        
        # 평균 처리 시간 업데이트
        total_time = (self.parsing_stats['avg_processing_time'] * 
                     (self.parsing_stats['total_parsed'] - 1) + processing_time)
        self.parsing_stats['avg_processing_time'] = total_time / self.parsing_stats['total_parsed']
    
    def _create_error_result(self, errors: List[str], warnings: List[str], 
                           start_time: float) -> ParsingResult:
        """오류 결과 생성"""
        return ParsingResult(
            success=False,
            data=None,
            errors=errors,
            warnings=warnings,
            processing_time=time.time() - start_time
        )
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """파싱 통계 반환"""
        stats = self.parsing_stats.copy()
        stats['cache_size'] = len(self.cache)
        stats['success_rate'] = (
            stats['successful_parses'] / max(stats['total_parsed'], 1) * 100
        )
        return stats
    
    def clear_cache(self):
        """캐시 삭제"""
        self.cache.clear()
        self.cache_timestamps.clear()
        self.logger.info("파싱 캐시 삭제 완료")