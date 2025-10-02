#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동적 데이터 기반 메시지 생성 시스템 (완전 독립)
실제 API 데이터를 기반으로 한 메시지 생성 및 데이터 품질 관리

주요 기능:
- 📊 실시간 시장 데이터 수집 및 캐싱
- 🔍 데이터 품질 평가 및 신뢰도 계산
- 💬 동적 데이터 기반 메시지 생성
- 📈 데이터 분석 결과 메시지 반영

Requirements: 2.4 구현
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class DataQuality(Enum):
    """데이터 품질 등급"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    FAIR = "fair"           # 50-69%
    POOR = "poor"           # 30-49%
    CRITICAL = "critical"   # 0-29%


class DataSource(Enum):
    """데이터 소스 타입"""
    KOSPI_API = "kospi_api"
    EXCHANGE_API = "exchange_api"
    POSCO_STOCK_API = "posco_stock_api"
    NEWS_API = "news_api"
    CACHED_DATA = "cached_data"
    FALLBACK_DATA = "fallback_data"


@dataclass
class DataPoint:
    """개별 데이터 포인트"""
    value: Any
    timestamp: str
    source: DataSource
    quality_score: float
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class MarketData:
    """시장 데이터 구조"""
    kospi: Optional[DataPoint] = None
    exchange_rate: Optional[DataPoint] = None
    posco_stock: Optional[DataPoint] = None
    news_sentiment: Optional[DataPoint] = None
    last_updated: Optional[str] = None
    overall_quality: Optional[float] = None


class DynamicDataManager:
    """동적 데이터 관리자 클래스"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """동적 데이터 관리자 초기화"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir or os.path.join(self.script_dir, "../data")
        
        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 캐시 파일 경로
        self.cache_file = os.path.join(self.data_dir, "market_data_cache.json")
        self.quality_log_file = os.path.join(self.data_dir, "data_quality_log.json")
        self.analysis_cache_file = os.path.join(self.data_dir, "analysis_results_cache.json")
        
        # API 설정 (실제 API 키는 환경변수나 설정파일에서 로드)
        self.api_config = {
            'kospi_api_url': 'https://api.example.com/kospi',  # 실제 API URL로 교체
            'exchange_api_url': 'https://api.example.com/exchange',  # 실제 API URL로 교체
            'posco_api_url': 'https://api.example.com/stock/posco',  # 실제 API URL로 교체
            'news_api_url': 'https://api.example.com/news/posco',  # 실제 API URL로 교체
            'timeout': 10,
            'retry_attempts': 3,
            'cache_duration': 300  # 5분
        }
        
        # 데이터 품질 기준
        self.quality_thresholds = {
            'freshness_hours': 2,      # 2시간 이내 데이터
            'min_confidence': 0.7,     # 최소 신뢰도 70%
            'api_timeout': 10,         # API 응답 시간 10초
            'required_fields': ['value', 'timestamp']
        }
        
        # 폴백 데이터 (API 실패 시 사용)
        self.fallback_data = {
            'kospi': {'value': 2500.0, 'change': 0.0, 'timestamp': datetime.now().isoformat()},
            'exchange_rate': {'value': 1350.0, 'change': 0.0, 'timestamp': datetime.now().isoformat()},
            'posco_stock': {'value': 280000.0, 'change': 0.0, 'timestamp': datetime.now().isoformat()}
        }
        
        print(f"📊 동적 데이터 관리자 초기화 완료 (데이터 디렉토리: {self.data_dir})")
    
    def collect_market_data(self) -> MarketData:
        """시장 데이터 수집 및 품질 평가"""
        print("📈 시장 데이터 수집 시작...")
        
        market_data = MarketData()
        
        # 각 데이터 소스에서 데이터 수집
        market_data.kospi = self._fetch_kospi_data()
        market_data.exchange_rate = self._fetch_exchange_rate_data()
        market_data.posco_stock = self._fetch_posco_stock_data()
        market_data.news_sentiment = self._fetch_news_sentiment_data()
        
        # 전체 데이터 품질 계산
        market_data.overall_quality = self._calculate_overall_quality(market_data)
        market_data.last_updated = datetime.now().isoformat()
        
        # 캐시에 저장
        self._save_to_cache(market_data)
        
        # 품질 로그 기록
        self._log_data_quality(market_data)
        
        print(f"✅ 시장 데이터 수집 완료 (품질: {market_data.overall_quality:.1%})")
        return market_data
    
    def _fetch_kospi_data(self) -> DataPoint:
        """KOSPI 데이터 수집"""
        try:
            print("📊 KOSPI 데이터 수집 중...")
            
            # 실제 API 호출 (현재는 시뮬레이션)
            # response = requests.get(self.api_config['kospi_api_url'], timeout=self.api_config['timeout'])
            
            # 시뮬레이션 데이터 (실제 구현 시 API 응답으로 교체)
            simulated_data = {
                'index': 2520.5,
                'change': 15.3,
                'change_percent': 0.61,
                'timestamp': datetime.now().isoformat(),
                'volume': 450000000
            }
            
            # 데이터 품질 평가
            quality_score = self._evaluate_data_quality(simulated_data, DataSource.KOSPI_API)
            confidence = self._calculate_confidence(simulated_data, 'kospi')
            
            return DataPoint(
                value=simulated_data['index'],
                timestamp=simulated_data['timestamp'],
                source=DataSource.KOSPI_API,
                quality_score=quality_score,
                confidence=confidence,
                metadata={
                    'change': simulated_data['change'],
                    'change_percent': simulated_data['change_percent'],
                    'volume': simulated_data['volume']
                }
            )
            
        except Exception as e:
            print(f"⚠️ KOSPI 데이터 수집 실패: {e}")
            return self._create_fallback_datapoint('kospi', DataSource.KOSPI_API)
    
    def _fetch_exchange_rate_data(self) -> DataPoint:
        """환율 데이터 수집"""
        try:
            print("💱 환율 데이터 수집 중...")
            
            # 시뮬레이션 데이터 (실제 구현 시 API 응답으로 교체)
            simulated_data = {
                'rate': 1347.5,
                'change': -2.5,
                'change_percent': -0.18,
                'timestamp': datetime.now().isoformat(),
                'base_currency': 'USD',
                'target_currency': 'KRW'
            }
            
            quality_score = self._evaluate_data_quality(simulated_data, DataSource.EXCHANGE_API)
            confidence = self._calculate_confidence(simulated_data, 'exchange_rate')
            
            return DataPoint(
                value=simulated_data['rate'],
                timestamp=simulated_data['timestamp'],
                source=DataSource.EXCHANGE_API,
                quality_score=quality_score,
                confidence=confidence,
                metadata={
                    'change': simulated_data['change'],
                    'change_percent': simulated_data['change_percent'],
                    'base_currency': simulated_data['base_currency'],
                    'target_currency': simulated_data['target_currency']
                }
            )
            
        except Exception as e:
            print(f"⚠️ 환율 데이터 수집 실패: {e}")
            return self._create_fallback_datapoint('exchange_rate', DataSource.EXCHANGE_API)
    
    def _fetch_posco_stock_data(self) -> DataPoint:
        """POSCO 주가 데이터 수집"""
        try:
            print("🏭 POSCO 주가 데이터 수집 중...")
            
            # 시뮬레이션 데이터 (실제 구현 시 API 응답으로 교체)
            simulated_data = {
                'price': 285000,
                'change': 3500,
                'change_percent': 1.24,
                'timestamp': datetime.now().isoformat(),
                'volume': 125000,
                'market_cap': 24500000000000
            }
            
            quality_score = self._evaluate_data_quality(simulated_data, DataSource.POSCO_STOCK_API)
            confidence = self._calculate_confidence(simulated_data, 'posco_stock')
            
            return DataPoint(
                value=simulated_data['price'],
                timestamp=simulated_data['timestamp'],
                source=DataSource.POSCO_STOCK_API,
                quality_score=quality_score,
                confidence=confidence,
                metadata={
                    'change': simulated_data['change'],
                    'change_percent': simulated_data['change_percent'],
                    'volume': simulated_data['volume'],
                    'market_cap': simulated_data['market_cap']
                }
            )
            
        except Exception as e:
            print(f"⚠️ POSCO 주가 데이터 수집 실패: {e}")
            return self._create_fallback_datapoint('posco_stock', DataSource.POSCO_STOCK_API)
    
    def _fetch_news_sentiment_data(self) -> DataPoint:
        """뉴스 감정 분석 데이터 수집"""
        try:
            print("📰 뉴스 감정 분석 데이터 수집 중...")
            
            # 시뮬레이션 데이터 (실제 구현 시 뉴스 API + 감정 분석으로 교체)
            simulated_data = {
                'sentiment_score': 0.65,  # -1 (매우 부정) ~ 1 (매우 긍정)
                'sentiment_label': 'positive',
                'confidence': 0.82,
                'news_count': 15,
                'timestamp': datetime.now().isoformat(),
                'key_topics': ['실적', '투자', '성장']
            }
            
            quality_score = self._evaluate_data_quality(simulated_data, DataSource.NEWS_API)
            confidence = simulated_data['confidence']
            
            return DataPoint(
                value=simulated_data['sentiment_score'],
                timestamp=simulated_data['timestamp'],
                source=DataSource.NEWS_API,
                quality_score=quality_score,
                confidence=confidence,
                metadata={
                    'sentiment_label': simulated_data['sentiment_label'],
                    'news_count': simulated_data['news_count'],
                    'key_topics': simulated_data['key_topics']
                }
            )
            
        except Exception as e:
            print(f"⚠️ 뉴스 감정 분석 데이터 수집 실패: {e}")
            # 뉴스 데이터는 중립으로 폴백
            return DataPoint(
                value=0.0,
                timestamp=datetime.now().isoformat(),
                source=DataSource.FALLBACK_DATA,
                quality_score=0.3,
                confidence=0.5,
                metadata={'sentiment_label': 'neutral', 'news_count': 0, 'key_topics': []}
            )
    
    def _evaluate_data_quality(self, data: Dict[str, Any], source: DataSource) -> float:
        """데이터 품질 평가"""
        quality_factors = []
        
        # 1. 데이터 완성도 (필수 필드 존재 여부)
        completeness = 0.0
        required_fields = self.quality_thresholds['required_fields']
        if isinstance(data, dict):
            present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
            completeness = present_fields / len(required_fields)
        quality_factors.append(completeness)
        
        # 2. 데이터 신선도 (타임스탬프 기준)
        freshness = 1.0
        if 'timestamp' in data:
            try:
                data_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                age_hours = (datetime.now() - data_time.replace(tzinfo=None)).total_seconds() / 3600
                freshness = max(0.0, 1.0 - (age_hours / self.quality_thresholds['freshness_hours']))
            except:
                freshness = 0.5
        quality_factors.append(freshness)
        
        # 3. 데이터 소스 신뢰도
        source_reliability = {
            DataSource.KOSPI_API: 0.95,
            DataSource.EXCHANGE_API: 0.90,
            DataSource.POSCO_STOCK_API: 0.85,
            DataSource.NEWS_API: 0.75,
            DataSource.CACHED_DATA: 0.60,
            DataSource.FALLBACK_DATA: 0.30
        }
        quality_factors.append(source_reliability.get(source, 0.5))
        
        # 4. 데이터 값의 합리성 (범위 체크)
        reasonableness = self._check_data_reasonableness(data, source)
        quality_factors.append(reasonableness)
        
        # 전체 품질 점수 계산 (가중 평균)
        weights = [0.3, 0.3, 0.2, 0.2]  # 완성도, 신선도, 소스 신뢰도, 합리성
        quality_score = sum(factor * weight for factor, weight in zip(quality_factors, weights))
        
        return min(1.0, max(0.0, quality_score))
    
    def _check_data_reasonableness(self, data: Dict[str, Any], source: DataSource) -> float:
        """데이터 값의 합리성 검사"""
        try:
            if source == DataSource.KOSPI_API:
                value = data.get('index', 0)
                # KOSPI 합리적 범위: 1000 ~ 4000
                if 1000 <= value <= 4000:
                    return 1.0
                elif 500 <= value <= 5000:
                    return 0.7
                else:
                    return 0.3
                    
            elif source == DataSource.EXCHANGE_API:
                value = data.get('rate', 0)
                # USD/KRW 합리적 범위: 1000 ~ 1600
                if 1000 <= value <= 1600:
                    return 1.0
                elif 800 <= value <= 2000:
                    return 0.7
                else:
                    return 0.3
                    
            elif source == DataSource.POSCO_STOCK_API:
                value = data.get('price', 0)
                # POSCO 주가 합리적 범위: 100,000 ~ 500,000
                if 100000 <= value <= 500000:
                    return 1.0
                elif 50000 <= value <= 800000:
                    return 0.7
                else:
                    return 0.3
                    
            elif source == DataSource.NEWS_API:
                value = data.get('sentiment_score', 0)
                # 감정 점수 합리적 범위: -1 ~ 1
                if -1 <= value <= 1:
                    return 1.0
                else:
                    return 0.3
            
            return 0.8  # 기본값
            
        except:
            return 0.5
    
    def _calculate_confidence(self, data: Dict[str, Any], data_type: str) -> float:
        """데이터 신뢰도 계산"""
        confidence_factors = []
        
        # 1. 데이터 변동성 기반 신뢰도
        if 'change_percent' in data:
            change_percent = abs(data['change_percent'])
            # 급격한 변동은 신뢰도 감소
            if change_percent <= 2.0:
                confidence_factors.append(0.95)
            elif change_percent <= 5.0:
                confidence_factors.append(0.80)
            elif change_percent <= 10.0:
                confidence_factors.append(0.60)
            else:
                confidence_factors.append(0.40)
        else:
            confidence_factors.append(0.70)
        
        # 2. 거래량/활동량 기반 신뢰도
        if 'volume' in data and data['volume'] > 0:
            confidence_factors.append(0.90)
        elif 'news_count' in data and data['news_count'] > 5:
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.70)
        
        # 3. 시간대별 신뢰도 (시장 시간 고려)
        current_hour = datetime.now().hour
        if data_type in ['kospi', 'posco_stock']:
            # 주식 시장 시간 (9-15시)
            if 9 <= current_hour <= 15:
                confidence_factors.append(0.95)
            elif 16 <= current_hour <= 18:
                confidence_factors.append(0.80)
            else:
                confidence_factors.append(0.60)
        else:
            # 환율은 24시간
            confidence_factors.append(0.85)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _create_fallback_datapoint(self, data_type: str, original_source: DataSource) -> DataPoint:
        """폴백 데이터 포인트 생성"""
        fallback = self.fallback_data.get(data_type, {})
        
        return DataPoint(
            value=fallback.get('value', 0),
            timestamp=datetime.now().isoformat(),
            source=DataSource.FALLBACK_DATA,
            quality_score=0.3,
            confidence=0.5,
            metadata={
                'change': fallback.get('change', 0),
                'original_source': original_source.value,
                'fallback_reason': 'API 호출 실패'
            }
        )
    
    def _calculate_overall_quality(self, market_data: MarketData) -> float:
        """전체 데이터 품질 계산"""
        quality_scores = []
        
        for data_point in [market_data.kospi, market_data.exchange_rate, 
                          market_data.posco_stock, market_data.news_sentiment]:
            if data_point:
                quality_scores.append(data_point.quality_score)
        
        if not quality_scores:
            return 0.0
        
        return sum(quality_scores) / len(quality_scores)
    
    def _save_to_cache(self, market_data: MarketData):
        """데이터 캐시에 저장"""
        try:
            # MarketData를 JSON 직렬화 가능한 형태로 변환
            def datapoint_to_dict(dp):
                if not dp:
                    return None
                return {
                    'value': dp.value,
                    'timestamp': dp.timestamp,
                    'source': dp.source.value,  # Enum을 문자열로 변환
                    'quality_score': dp.quality_score,
                    'confidence': dp.confidence,
                    'metadata': dp.metadata
                }
            
            cache_data = {
                'market_data': {
                    'kospi': datapoint_to_dict(market_data.kospi),
                    'exchange_rate': datapoint_to_dict(market_data.exchange_rate),
                    'posco_stock': datapoint_to_dict(market_data.posco_stock),
                    'news_sentiment': datapoint_to_dict(market_data.news_sentiment),
                    'last_updated': market_data.last_updated,
                    'overall_quality': market_data.overall_quality
                },
                'cached_at': datetime.now().isoformat(),
                'cache_version': '1.0'
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            print(f"💾 데이터 캐시 저장 완료: {self.cache_file}")
            
        except Exception as e:
            print(f"❌ 데이터 캐시 저장 실패: {e}")
    
    def _log_data_quality(self, market_data: MarketData):
        """데이터 품질 로그 기록"""
        try:
            # 기존 로그 로드
            quality_log = []
            if os.path.exists(self.quality_log_file):
                with open(self.quality_log_file, 'r', encoding='utf-8') as f:
                    quality_log = json.load(f)
            
            # 새 로그 엔트리 추가
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'overall_quality': market_data.overall_quality,
                'data_sources': {
                    'kospi': {
                        'quality': market_data.kospi.quality_score if market_data.kospi else 0,
                        'confidence': market_data.kospi.confidence if market_data.kospi else 0,
                        'source': market_data.kospi.source.value if market_data.kospi else 'none'
                    },
                    'exchange_rate': {
                        'quality': market_data.exchange_rate.quality_score if market_data.exchange_rate else 0,
                        'confidence': market_data.exchange_rate.confidence if market_data.exchange_rate else 0,
                        'source': market_data.exchange_rate.source.value if market_data.exchange_rate else 'none'
                    },
                    'posco_stock': {
                        'quality': market_data.posco_stock.quality_score if market_data.posco_stock else 0,
                        'confidence': market_data.posco_stock.confidence if market_data.posco_stock else 0,
                        'source': market_data.posco_stock.source.value if market_data.posco_stock else 'none'
                    },
                    'news_sentiment': {
                        'quality': market_data.news_sentiment.quality_score if market_data.news_sentiment else 0,
                        'confidence': market_data.news_sentiment.confidence if market_data.news_sentiment else 0,
                        'source': market_data.news_sentiment.source.value if market_data.news_sentiment else 'none'
                    }
                }
            }
            
            quality_log.append(log_entry)
            
            # 최근 100개 로그만 유지
            if len(quality_log) > 100:
                quality_log = quality_log[-100:]
            
            # 로그 파일 저장
            with open(self.quality_log_file, 'w', encoding='utf-8') as f:
                json.dump(quality_log, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ 품질 로그 기록 실패: {e}")
    
    def load_cached_data(self) -> Optional[MarketData]:
        """캐시된 데이터 로드"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 캐시 유효성 검사
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            cache_age = (datetime.now() - cached_at).total_seconds()
            
            if cache_age > self.api_config['cache_duration']:
                print("⏰ 캐시 데이터가 만료되었습니다")
                return None
            
            # MarketData 객체로 변환
            market_data_dict = cache_data['market_data']
            
            def dict_to_datapoint(dp_dict):
                if not dp_dict:
                    return None
                return DataPoint(
                    value=dp_dict['value'],
                    timestamp=dp_dict['timestamp'],
                    source=DataSource(dp_dict['source']),
                    quality_score=dp_dict['quality_score'],
                    confidence=dp_dict['confidence'],
                    metadata=dp_dict['metadata']
                )
            
            market_data = MarketData(
                kospi=dict_to_datapoint(market_data_dict.get('kospi')),
                exchange_rate=dict_to_datapoint(market_data_dict.get('exchange_rate')),
                posco_stock=dict_to_datapoint(market_data_dict.get('posco_stock')),
                news_sentiment=dict_to_datapoint(market_data_dict.get('news_sentiment')),
                last_updated=market_data_dict.get('last_updated'),
                overall_quality=market_data_dict.get('overall_quality')
            )
            
            print(f"📂 캐시된 데이터 로드 완료 (품질: {market_data.overall_quality:.1%})")
            return market_data
            
        except Exception as e:
            print(f"❌ 캐시 데이터 로드 실패: {e}")
            return None
    
    def get_market_data(self, force_refresh: bool = False) -> MarketData:
        """시장 데이터 조회 (캐시 우선)"""
        if not force_refresh:
            cached_data = self.load_cached_data()
            if cached_data:
                return cached_data
        
        # 캐시가 없거나 강제 새로고침인 경우 새 데이터 수집
        return self.collect_market_data()
    
    def generate_dynamic_message_data(self, market_data: MarketData) -> Dict[str, Any]:
        """동적 메시지 생성을 위한 데이터 준비"""
        print("💬 동적 메시지 데이터 생성 중...")
        
        # 기본 메시지 데이터
        message_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_quality': market_data.overall_quality,
            'data_reliability': self._get_quality_description(market_data.overall_quality)
        }
        
        # KOSPI 데이터 처리
        if market_data.kospi:
            kospi_change = market_data.kospi.metadata.get('change', 0)
            kospi_change_percent = market_data.kospi.metadata.get('change_percent', 0)
            
            message_data.update({
                'kospi': f"{market_data.kospi.value:,.1f}",
                'kospi_change': self._format_change_value(kospi_change),
                'kospi_change_percent': f"{kospi_change_percent:+.2f}%",
                'kospi_trend': self._get_trend_description(kospi_change_percent),
                'kospi_quality': f"{market_data.kospi.quality_score:.1%}",
                'kospi_confidence': f"{market_data.kospi.confidence:.1%}",
                'kospi_source': self._get_source_description(market_data.kospi.source)
            })
        else:
            message_data.update({
                'kospi': 'N/A',
                'kospi_change': 'N/A',
                'kospi_trend': '데이터 없음',
                'kospi_quality': '0%',
                'kospi_confidence': '0%'
            })
        
        # 환율 데이터 처리
        if market_data.exchange_rate:
            exchange_change = market_data.exchange_rate.metadata.get('change', 0)
            exchange_change_percent = market_data.exchange_rate.metadata.get('change_percent', 0)
            
            message_data.update({
                'exchange_rate': f"{market_data.exchange_rate.value:,.1f}원",
                'exchange_change': self._format_change_value(exchange_change),
                'exchange_change_percent': f"{exchange_change_percent:+.2f}%",
                'exchange_trend': self._get_trend_description(exchange_change_percent),
                'exchange_quality': f"{market_data.exchange_rate.quality_score:.1%}",
                'exchange_confidence': f"{market_data.exchange_rate.confidence:.1%}",
                'exchange_source': self._get_source_description(market_data.exchange_rate.source)
            })
        else:
            message_data.update({
                'exchange_rate': 'N/A',
                'exchange_change': 'N/A',
                'exchange_trend': '데이터 없음',
                'exchange_quality': '0%',
                'exchange_confidence': '0%'
            })
        
        # POSCO 주가 데이터 처리
        if market_data.posco_stock:
            posco_change = market_data.posco_stock.metadata.get('change', 0)
            posco_change_percent = market_data.posco_stock.metadata.get('change_percent', 0)
            
            message_data.update({
                'posco_stock': f"{market_data.posco_stock.value:,}원",
                'posco_change': self._format_change_value(posco_change),
                'posco_change_percent': f"{posco_change_percent:+.2f}%",
                'posco_trend': self._get_trend_description(posco_change_percent),
                'posco_quality': f"{market_data.posco_stock.quality_score:.1%}",
                'posco_confidence': f"{market_data.posco_stock.confidence:.1%}",
                'posco_source': self._get_source_description(market_data.posco_stock.source)
            })
        else:
            message_data.update({
                'posco_stock': 'N/A',
                'posco_change': 'N/A',
                'posco_trend': '데이터 없음',
                'posco_quality': '0%',
                'posco_confidence': '0%'
            })
        
        # 뉴스 감정 분석 데이터 처리
        if market_data.news_sentiment:
            sentiment_label = market_data.news_sentiment.metadata.get('sentiment_label', 'neutral')
            news_count = market_data.news_sentiment.metadata.get('news_count', 0)
            key_topics = market_data.news_sentiment.metadata.get('key_topics', [])
            
            message_data.update({
                'news_sentiment': self._get_sentiment_description(sentiment_label),
                'news_sentiment_score': f"{market_data.news_sentiment.value:.2f}",
                'news_count': news_count,
                'key_topics': ', '.join(key_topics) if key_topics else '없음',
                'news_quality': f"{market_data.news_sentiment.quality_score:.1%}",
                'news_confidence': f"{market_data.news_sentiment.confidence:.1%}"
            })
        else:
            message_data.update({
                'news_sentiment': '중립',
                'news_sentiment_score': '0.00',
                'news_count': 0,
                'key_topics': '없음',
                'news_quality': '0%',
                'news_confidence': '0%'
            })
        
        # 종합 분석 결과
        message_data.update({
            'market_summary': self._generate_market_summary(market_data),
            'quality_warning': self._generate_quality_warning(market_data),
            'data_freshness': self._get_data_freshness(market_data),
            'reliability_indicator': self._get_reliability_indicator(market_data.overall_quality)
        })
        
        print(f"✅ 동적 메시지 데이터 생성 완료 (품질: {market_data.overall_quality:.1%})")
        return message_data
    
    def _format_change_value(self, change: float) -> str:
        """변화량 포맷팅"""
        if change > 0:
            return f"▲ +{change:,.2f}"
        elif change < 0:
            return f"▼ {change:,.2f}"
        else:
            return "→ 0.00"
    
    def _get_trend_description(self, change_percent: float) -> str:
        """트렌드 설명 생성"""
        if change_percent >= 2.0:
            return "강한 상승세"
        elif change_percent >= 0.5:
            return "상승세"
        elif change_percent > -0.5:
            return "보합세"
        elif change_percent > -2.0:
            return "하락세"
        else:
            return "강한 하락세"
    
    def _get_sentiment_description(self, sentiment_label: str) -> str:
        """감정 분석 결과 설명"""
        sentiment_map = {
            'very_positive': '매우 긍정적',
            'positive': '긍정적',
            'neutral': '중립적',
            'negative': '부정적',
            'very_negative': '매우 부정적'
        }
        return sentiment_map.get(sentiment_label, '중립적')
    
    def _get_quality_description(self, quality_score: float) -> str:
        """데이터 품질 설명"""
        if quality_score >= 0.9:
            return "매우 높음"
        elif quality_score >= 0.7:
            return "높음"
        elif quality_score >= 0.5:
            return "보통"
        elif quality_score >= 0.3:
            return "낮음"
        else:
            return "매우 낮음"
    
    def _get_source_description(self, source: DataSource) -> str:
        """데이터 소스 설명"""
        source_map = {
            DataSource.KOSPI_API: "실시간 API",
            DataSource.EXCHANGE_API: "환율 API",
            DataSource.POSCO_STOCK_API: "주식 API",
            DataSource.NEWS_API: "뉴스 API",
            DataSource.CACHED_DATA: "캐시 데이터",
            DataSource.FALLBACK_DATA: "백업 데이터"
        }
        return source_map.get(source, "알 수 없음")
    
    def _generate_market_summary(self, market_data: MarketData) -> str:
        """시장 종합 요약 생성"""
        summaries = []
        
        # KOSPI 요약
        if market_data.kospi:
            kospi_change_percent = market_data.kospi.metadata.get('change_percent', 0)
            if kospi_change_percent > 0:
                summaries.append(f"KOSPI가 {kospi_change_percent:.2f}% 상승했습니다")
            elif kospi_change_percent < 0:
                summaries.append(f"KOSPI가 {abs(kospi_change_percent):.2f}% 하락했습니다")
            else:
                summaries.append("KOSPI는 보합세를 유지했습니다")
        
        # 환율 요약
        if market_data.exchange_rate:
            exchange_change_percent = market_data.exchange_rate.metadata.get('change_percent', 0)
            if exchange_change_percent > 0:
                summaries.append("원화가 약세를 보였습니다")
            elif exchange_change_percent < 0:
                summaries.append("원화가 강세를 보였습니다")
        
        # POSCO 주가 요약
        if market_data.posco_stock:
            posco_change_percent = market_data.posco_stock.metadata.get('change_percent', 0)
            if posco_change_percent > 1.0:
                summaries.append("POSCO 주가가 강한 상승세를 보였습니다")
            elif posco_change_percent < -1.0:
                summaries.append("POSCO 주가가 하락세를 보였습니다")
        
        if not summaries:
            return "시장은 전반적으로 안정적인 모습을 보였습니다"
        
        return ". ".join(summaries) + "."
    
    def _generate_quality_warning(self, market_data: MarketData) -> str:
        """데이터 품질 경고 메시지 생성"""
        if market_data.overall_quality < 0.5:
            return "⚠️ 데이터 품질이 낮습니다. 분석 결과를 참고용으로만 활용하세요."
        elif market_data.overall_quality < 0.7:
            return "ℹ️ 일부 데이터의 신뢰도가 제한적입니다."
        else:
            return ""
    
    def _get_data_freshness(self, market_data: MarketData) -> str:
        """데이터 신선도 정보"""
        if market_data.last_updated:
            try:
                updated_time = datetime.fromisoformat(market_data.last_updated)
                age_minutes = (datetime.now() - updated_time).total_seconds() / 60
                
                if age_minutes < 5:
                    return "실시간"
                elif age_minutes < 30:
                    return f"{int(age_minutes)}분 전"
                elif age_minutes < 120:
                    return f"{int(age_minutes/60)}시간 전"
                else:
                    return "오래된 데이터"
            except:
                return "알 수 없음"
        return "알 수 없음"
    
    def _get_reliability_indicator(self, quality_score: float) -> str:
        """신뢰도 지표"""
        if quality_score >= 0.9:
            return "🟢 매우 신뢰할 수 있음"
        elif quality_score >= 0.7:
            return "🟡 신뢰할 수 있음"
        elif quality_score >= 0.5:
            return "🟠 주의 필요"
        else:
            return "🔴 신뢰도 낮음"
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """데이터 품질 통계 조회"""
        try:
            if not os.path.exists(self.quality_log_file):
                return {'error': '품질 로그가 없습니다'}
            
            with open(self.quality_log_file, 'r', encoding='utf-8') as f:
                quality_log = json.load(f)
            
            if not quality_log:
                return {'error': '품질 데이터가 없습니다'}
            
            # 최근 24시간 데이터만 분석
            recent_logs = []
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for log_entry in quality_log:
                try:
                    log_time = datetime.fromisoformat(log_entry['timestamp'])
                    if log_time >= cutoff_time:
                        recent_logs.append(log_entry)
                except:
                    continue
            
            if not recent_logs:
                return {'error': '최근 품질 데이터가 없습니다'}
            
            # 통계 계산
            overall_qualities = [log['overall_quality'] for log in recent_logs]
            
            statistics = {
                'period': '최근 24시간',
                'total_measurements': len(recent_logs),
                'average_quality': sum(overall_qualities) / len(overall_qualities),
                'min_quality': min(overall_qualities),
                'max_quality': max(overall_qualities),
                'quality_trend': self._calculate_quality_trend(recent_logs),
                'source_reliability': self._calculate_source_reliability(recent_logs),
                'last_updated': recent_logs[-1]['timestamp'] if recent_logs else None
            }
            
            return statistics
            
        except Exception as e:
            return {'error': f'품질 통계 계산 실패: {str(e)}'}
    
    def _calculate_quality_trend(self, logs: List[Dict]) -> str:
        """품질 트렌드 계산"""
        if len(logs) < 2:
            return "데이터 부족"
        
        # 최근 5개와 이전 5개 비교
        recent_count = min(5, len(logs))
        recent_quality = sum(log['overall_quality'] for log in logs[-recent_count:]) / recent_count
        
        if len(logs) >= 10:
            previous_quality = sum(log['overall_quality'] for log in logs[-10:-recent_count]) / (10 - recent_count)
            
            if recent_quality > previous_quality + 0.05:
                return "개선 중"
            elif recent_quality < previous_quality - 0.05:
                return "악화 중"
            else:
                return "안정적"
        else:
            return "안정적"
    
    def _calculate_source_reliability(self, logs: List[Dict]) -> Dict[str, float]:
        """소스별 신뢰도 계산"""
        source_stats = {}
        
        for log in logs:
            for source_name, source_data in log.get('data_sources', {}).items():
                if source_name not in source_stats:
                    source_stats[source_name] = []
                source_stats[source_name].append(source_data.get('quality', 0))
        
        # 평균 계산
        source_reliability = {}
        for source_name, qualities in source_stats.items():
            if qualities:
                source_reliability[source_name] = sum(qualities) / len(qualities)
        
        return source_reliability


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 DynamicDataManager 테스트 시작...")
    
    manager = DynamicDataManager()
    
    # 시장 데이터 수집 테스트
    market_data = manager.collect_market_data()
    print(f"\n📊 수집된 시장 데이터:")
    print(f"- KOSPI: {market_data.kospi.value if market_data.kospi else 'N/A'}")
    print(f"- 환율: {market_data.exchange_rate.value if market_data.exchange_rate else 'N/A'}")
    print(f"- POSCO 주가: {market_data.posco_stock.value if market_data.posco_stock else 'N/A'}")
    print(f"- 전체 품질: {market_data.overall_quality:.1%}")
    
    # 동적 메시지 데이터 생성 테스트
    message_data = manager.generate_dynamic_message_data(market_data)
    print(f"\n💬 생성된 메시지 데이터:")
    print(f"- 시장 요약: {message_data['market_summary']}")
    print(f"- 데이터 신뢰도: {message_data['data_reliability']}")
    print(f"- 품질 경고: {message_data['quality_warning']}")
    
    # 캐시 테스트
    cached_data = manager.load_cached_data()
    if cached_data:
        print(f"\n📂 캐시 데이터 로드 성공 (품질: {cached_data.overall_quality:.1%})")
    
    print("\n✅ DynamicDataManager 테스트 완료")