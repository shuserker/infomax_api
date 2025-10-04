# -*- coding: utf-8 -*-
"""
EXCHANGE RATE 데이터 파싱 모듈

정상 커밋 a763ef84의 원본 로직을 기반으로 복원된 서환마감 전용 파싱 모듈입니다.

주요 기능:
- 원달러 환율 분석
- 주요 통화 환율 추출 (엔화, 유로, 위안 등)
- 환율 변동 요인 분석
- 국제 금융시장 동향 파악
- 한국 외환시장 특성 반영

작성자: AI Assistant
복원 일시: 2025-08-12
수정일: 2025-08-16 (워치햄스터 공통 모듈로 복사)
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import re
from datetime import datetime, time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging


@dataclass
class CurrencyRate:
    """통화 환율 데이터"""
    currency_pair: str  # 'USD/KRW', 'JPY/KRW' 등
    rate: float
    change: float
    change_percent: float
    direction: str  # 'up', 'down', 'flat'
    high: Optional[float] = None
    low: Optional[float] = None


@dataclass
class MarketFactor:
    """환율 변동 요인"""
    factor_type: str  # 'domestic', 'international', 'technical'
    description: str
    impact: str  # 'positive', 'negative', 'neutral'


@dataclass
class ExchangeRateData:
    """서환마감 파싱 결과"""
    title: str
    content: str
    date: str
    time: str
    market_situation: str  # '강세', '약세', '보합'
    usd_krw_rate: Optional[CurrencyRate]
    major_currencies: List[CurrencyRate]
    market_factors: List[MarketFactor]
    volatility_level: str  # 'high', 'medium', 'low'
    trading_volume: Optional[str]
    market_summary: str
    next_day_outlook: Optional[str]
    raw_data: Dict[str, Any]


class ExchangeRateParser:
    """
    서환마감 전용 파싱 클래스
    
    한국 외환시장 데이터의 특성을 반영한 전문 파싱 기능을 제공합니다.
    """
    
    def __init__(self):
        """파서 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 외환시장 운영 시간
        self.market_hours = {
            'regular_start': time(9, 0),    # 09:00
            'regular_end': time(15, 30),    # 15:30
            'extended_end': time(16, 30)    # 16:30 (연장거래)
        }
        
        # 주요 통화 패턴
        self.currency_patterns = {
            'usd_krw': [
                r'원달러\s*(?:환율)?\s*([0-9,]+\.?[0-9]*)',
                r'달러원\s*(?:환율)?\s*([0-9,]+\.?[0-9]*)',
                r'USD/KRW\s*([0-9,]+\.?[0-9]*)',
                r'미국\s*달러\s*([0-9,]+\.?[0-9]*)'
            ],
            'jpy_krw': [
                r'엔화\s*(?:환율)?\s*([0-9,]+\.?[0-9]*)',
                r'일본\s*엔\s*([0-9,]+\.?[0-9]*)',
                r'JPY/KRW\s*([0-9,]+\.?[0-9]*)',
                r'100엔당\s*([0-9,]+\.?[0-9]*)'
            ],
            'eur_krw': [
                r'유로\s*(?:환율)?\s*([0-9,]+\.?[0-9]*)',
                r'EUR/KRW\s*([0-9,]+\.?[0-9]*)',
                r'유럽\s*유로\s*([0-9,]+\.?[0-9]*)'
            ],
            'cny_krw': [
                r'위안\s*(?:환율)?\s*([0-9,]+\.?[0-9]*)',
                r'중국\s*위안\s*([0-9,]+\.?[0-9]*)',
                r'CNY/KRW\s*([0-9,]+\.?[0-9]*)'
            ],
            'gbp_krw': [
                r'파운드\s*(?:환율)?\s*([0-9,]+\.?[0-9]*)',
                r'영국\s*파운드\s*([0-9,]+\.?[0-9]*)',
                r'GBP/KRW\s*([0-9,]+\.?[0-9]*)'
            ]
        }
        
        # 환율 방향 키워드
        self.direction_keywords = {
            'strong_won': ['원화 강세', '원고', '달러 약세', '환율 하락', '원화 상승'],
            'weak_won': ['원화 약세', '원저', '달러 강세', '환율 상승', '원화 하락'],
            'stable': ['보합', '횡보', '안정', '변동 없음', '등락 없음']
        }
        
        # 변동 요인 키워드
        self.factor_keywords = {
            'domestic': {
                'keywords': ['한국은행', '기준금리', '무역수지', '경상수지', '국내', '한국'],
                'type': 'domestic'
            },
            'international': {
                'keywords': ['연준', 'Fed', '미국', '중국', '일본', '유럽', '국제', '글로벌'],
                'type': 'international'
            },
            'technical': {
                'keywords': ['기술적', '차트', '저항선', '지지선', '매매', '거래량'],
                'type': 'technical'
            },
            'geopolitical': {
                'keywords': ['지정학', '전쟁', '분쟁', '제재', '정치', '선거'],
                'type': 'geopolitical'
            }
        }
    
    def parse_exchange_rate_data(self, raw_data: Dict[str, Any]) -> ExchangeRateData:
        """서환마감 데이터 파싱"""
        if not raw_data:
            return self._create_empty_exchange_data()
        
        try:
            # 기본 정보 추출
            title = raw_data.get('title', '')
            content = raw_data.get('content', '')
            date = raw_data.get('date', '')
            time_str = raw_data.get('time', '')
            
            # 원달러 환율 추출
            usd_krw_rate = self._extract_usd_krw_rate(title, content)
            
            # 주요 통화 환율 추출
            major_currencies = self._extract_major_currencies(title, content)
            
            # 시장 상황 판단
            market_situation = self._determine_market_situation(title, content, usd_krw_rate)
            
            # 변동 요인 추출
            market_factors = self._extract_market_factors(content)
            
            # 변동성 수준 판단
            volatility_level = self._assess_volatility_level(content, usd_krw_rate)
            
            # 거래량 정보 추출
            trading_volume = self._extract_trading_volume(content)
            
            # 다음날 전망 추출
            next_day_outlook = self._extract_outlook(content)
            
            # 시장 요약 생성
            market_summary = self._generate_market_summary(
                market_situation, usd_krw_rate, market_factors, volatility_level
            )
            
            self.logger.info(f"서환마감 파싱 완료: {market_situation}, 통화 {len(major_currencies)}개")
            
            return ExchangeRateData(
                title=title,
                content=content,
                date=date,
                time=time_str,
                market_situation=market_situation,
                usd_krw_rate=usd_krw_rate,
                major_currencies=major_currencies,
                market_factors=market_factors,
                volatility_level=volatility_level,
                trading_volume=trading_volume,
                market_summary=market_summary,
                next_day_outlook=next_day_outlook,
                raw_data=raw_data
            )
            
        except Exception as e:
            self.logger.error(f"서환마감 파싱 오류: {e}")
            return self._create_empty_exchange_data()
    
    def _extract_usd_krw_rate(self, title: str, content: str) -> Optional[CurrencyRate]:
        """원달러 환율 추출"""
        text = f"{title} {content}"
        
        for pattern in self.currency_patterns['usd_krw']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rate_str = match.group(1).replace(',', '')
                    rate = float(rate_str)
                    
                    # 변화량과 변화율 추출
                    change, change_percent = self._extract_rate_change(text, match.start())
                    
                    # 방향 판단
                    direction = 'flat'
                    if change > 0:
                        direction = 'up'  # 환율 상승 = 원화 약세
                    elif change < 0:
                        direction = 'down'  # 환율 하락 = 원화 강세
                    
                    # 고가/저가 추출
                    high, low = self._extract_high_low(text, match.start())
                    
                    return CurrencyRate(
                        currency_pair='USD/KRW',
                        rate=rate,
                        change=change,
                        change_percent=change_percent,
                        direction=direction,
                        high=high,
                        low=low
                    )
                    
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_major_currencies(self, title: str, content: str) -> List[CurrencyRate]:
        """주요 통화 환율 추출"""
        currencies = []
        text = f"{title} {content}"
        
        for currency_name, patterns in self.currency_patterns.items():
            if currency_name == 'usd_krw':  # 이미 별도로 처리
                continue
                
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        rate_str = match.group(1).replace(',', '')
                        rate = float(rate_str)
                        
                        # 변화량과 변화율 추출
                        change, change_percent = self._extract_rate_change(text, match.start())
                        
                        # 방향 판단
                        direction = 'flat'
                        if change > 0:
                            direction = 'up'
                        elif change < 0:
                            direction = 'down'
                        
                        currency = CurrencyRate(
                            currency_pair=self._get_currency_pair_name(currency_name),
                            rate=rate,
                            change=change,
                            change_percent=change_percent,
                            direction=direction
                        )
                        
                        currencies.append(currency)
                        break  # 첫 번째 매치만 사용
                        
                    except (ValueError, IndexError):
                        continue
        
        return currencies
    
    def _extract_rate_change(self, text: str, position: int) -> Tuple[float, float]:
        """환율 변화량과 변화율 추출"""
        # 환율 위치 주변 텍스트 추출
        start = max(0, position - 100)
        end = min(len(text), position + 100)
        context = text[start:end]
        
        change = 0.0
        change_percent = 0.0
        
        # 변화량 패턴
        change_patterns = [
            r'([+-]?\s*[0-9,]+\.?[0-9]*)\s*(?:원|won)',
            r'전일\s*대비\s*([+-]?\s*[0-9,]+\.?[0-9]*)',
            r'([+-]\s*[0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in change_patterns:
            matches = re.findall(pattern, context)
            if matches:
                try:
                    change_str = matches[0].replace(' ', '').replace(',', '')
                    change = float(change_str)
                    break
                except ValueError:
                    continue
        
        # 변화율 패턴
        percent_patterns = [
            r'([+-]?\s*[0-9]+\.?[0-9]*)\s*%',
            r'([+-]?\s*[0-9]+\.?[0-9]*)\s*퍼센트'
        ]
        
        for pattern in percent_patterns:
            matches = re.findall(pattern, context)
            if matches:
                try:
                    percent_str = matches[0].replace(' ', '')
                    change_percent = float(percent_str)
                    break
                except ValueError:
                    continue
        
        return change, change_percent
    
    def _extract_high_low(self, text: str, position: int) -> Tuple[Optional[float], Optional[float]]:
        """고가/저가 추출"""
        start = max(0, position - 200)
        end = min(len(text), position + 200)
        context = text[start:end]
        
        high = None
        low = None
        
        # 고가 패턴
        high_patterns = [
            r'고가\s*([0-9,]+\.?[0-9]*)',
            r'최고\s*([0-9,]+\.?[0-9]*)',
            r'high\s*([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in high_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                try:
                    high = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue
        
        # 저가 패턴
        low_patterns = [
            r'저가\s*([0-9,]+\.?[0-9]*)',
            r'최저\s*([0-9,]+\.?[0-9]*)',
            r'low\s*([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in low_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                try:
                    low = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue
        
        return high, low
    
    def _get_currency_pair_name(self, currency_name: str) -> str:
        """통화쌍 표시명 반환"""
        pair_names = {
            'jpy_krw': 'JPY/KRW',
            'eur_krw': 'EUR/KRW',
            'cny_krw': 'CNY/KRW',
            'gbp_krw': 'GBP/KRW'
        }
        return pair_names.get(currency_name, currency_name.upper())
    
    def _determine_market_situation(self, title: str, content: str, 
                                  usd_krw_rate: Optional[CurrencyRate]) -> str:
        """시장 상황 판단 (원화 기준)"""
        text = f"{title} {content}".lower()
        
        # 키워드 기반 판단
        strong_won_count = sum(1 for keyword in self.direction_keywords['strong_won'] 
                              if keyword in text)
        weak_won_count = sum(1 for keyword in self.direction_keywords['weak_won'] 
                            if keyword in text)
        stable_count = sum(1 for keyword in self.direction_keywords['stable'] 
                          if keyword in text)
        
        # 환율 데이터 기반 판단
        rate_sentiment = 'neutral'
        if usd_krw_rate:
            if usd_krw_rate.direction == 'down':  # 환율 하락 = 원화 강세
                rate_sentiment = 'strong'
            elif usd_krw_rate.direction == 'up':  # 환율 상승 = 원화 약세
                rate_sentiment = 'weak'
        
        # 종합 판단
        if stable_count > 0 or rate_sentiment == 'neutral':
            return '보합'
        elif strong_won_count > weak_won_count or rate_sentiment == 'strong':
            return '강세'  # 원화 강세
        elif weak_won_count > strong_won_count or rate_sentiment == 'weak':
            return '약세'  # 원화 약세
        else:
            return '보합'
    
    def _extract_market_factors(self, content: str) -> List[MarketFactor]:
        """시장 변동 요인 추출"""
        factors = []
        
        for factor_category, config in self.factor_keywords.items():
            keywords = config['keywords']
            factor_type = config['type']
            
            for keyword in keywords:
                if keyword in content:
                    # 키워드 주변 텍스트 추출
                    start = content.find(keyword)
                    if start != -1:
                        context_start = max(0, start - 50)
                        context_end = min(len(content), start + 150)
                        context = content[context_start:context_end]
                        
                        # 영향 판단
                        impact = 'neutral'
                        if any(pos_word in context for pos_word in ['상승', '증가', '강세', '호재']):
                            impact = 'positive'
                        elif any(neg_word in context for neg_word in ['하락', '감소', '약세', '악재']):
                            impact = 'negative'
                        
                        factor = MarketFactor(
                            factor_type=factor_type,
                            description=context.strip(),
                            impact=impact
                        )
                        
                        factors.append(factor)
                        break  # 카테고리당 하나만
        
        # 중복 제거 및 최대 5개로 제한
        unique_factors = []
        seen_descriptions = set()
        for factor in factors:
            if factor.description not in seen_descriptions and len(unique_factors) < 5:
                unique_factors.append(factor)
                seen_descriptions.add(factor.description)
        
        return unique_factors
    
    def _assess_volatility_level(self, content: str, 
                               usd_krw_rate: Optional[CurrencyRate]) -> str:
        """변동성 수준 평가"""
        # 변동성 키워드 확인
        high_volatility_keywords = ['급등', '급락', '폭등', '폭락', '큰 폭', '대폭', '변동성 확대']
        medium_volatility_keywords = ['상승', '하락', '등락', '변동']
        low_volatility_keywords = ['보합', '횡보', '안정', '소폭', '변동성 축소']
        
        content_lower = content.lower()
        
        high_count = sum(1 for keyword in high_volatility_keywords if keyword in content_lower)
        medium_count = sum(1 for keyword in medium_volatility_keywords if keyword in content_lower)
        low_count = sum(1 for keyword in low_volatility_keywords if keyword in content_lower)
        
        # 환율 변화율 기반 판단
        rate_volatility = 'medium'
        if usd_krw_rate and abs(usd_krw_rate.change_percent) > 0:
            if abs(usd_krw_rate.change_percent) > 1.0:
                rate_volatility = 'high'
            elif abs(usd_krw_rate.change_percent) > 0.3:
                rate_volatility = 'medium'
            else:
                rate_volatility = 'low'
        
        # 종합 판단
        if high_count > 0 or rate_volatility == 'high':
            return 'high'
        elif low_count > medium_count and rate_volatility == 'low':
            return 'low'
        else:
            return 'medium'
    
    def _extract_trading_volume(self, content: str) -> Optional[str]:
        """거래량 정보 추출"""
        volume_patterns = [
            r'거래량\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?',
            r'거래대금\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?',
            r'([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?\s*달러'
        ]
        
        for pattern in volume_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_outlook(self, content: str) -> Optional[str]:
        """다음날 전망 추출"""
        outlook_patterns = [
            r'내일.*?전망.*?([^.。]{20,100})',
            r'다음.*?거래.*?([^.。]{20,100})',
            r'향후.*?전망.*?([^.。]{20,100})',
            r'전망.*?([^.。]{20,100})'
        ]
        
        for pattern in outlook_patterns:
            match = re.search(pattern, content)
            if match:
                outlook = match.group(1).strip()
                if len(outlook) > 10:  # 의미있는 길이
                    return outlook
        
        return None
    
    def _generate_market_summary(self, situation: str, usd_krw_rate: Optional[CurrencyRate], 
                               factors: List[MarketFactor], volatility: str) -> str:
        """시장 요약 생성"""
        summary_parts = []
        
        # 시장 상황
        summary_parts.append(f"원화 {situation}")
        
        # 원달러 환율
        if usd_krw_rate:
            direction_symbol = "📈" if usd_krw_rate.direction == "up" else "📉" if usd_krw_rate.direction == "down" else "➡️"
            if usd_krw_rate.change != 0:
                summary_parts.append(f"USD/KRW {usd_krw_rate.rate:,.2f} ({usd_krw_rate.change:+.2f})")
            else:
                summary_parts.append(f"USD/KRW {usd_krw_rate.rate:,.2f}")
        
        # 변동성
        volatility_desc = {
            'high': '높은 변동성',
            'medium': '보통 변동성',
            'low': '낮은 변동성'
        }
        summary_parts.append(volatility_desc.get(volatility, '변동성 불명'))
        
        # 주요 요인 (간단히)
        if factors:
            domestic_factors = [f for f in factors if f.factor_type == 'domestic']
            international_factors = [f for f in factors if f.factor_type == 'international']
            
            if international_factors:
                summary_parts.append(f"해외 요인: {international_factors[0].description[:20]}...")
            elif domestic_factors:
                summary_parts.append(f"국내 요인: {domestic_factors[0].description[:20]}...")
        
        return " | ".join(summary_parts) if summary_parts else "데이터 부족"
    
    def _create_empty_exchange_data(self) -> ExchangeRateData:
        """빈 환율 데이터 생성"""
        return ExchangeRateData(
            title='',
            content='',
            date='',
            time='',
            market_situation='보합',
            usd_krw_rate=None,
            major_currencies=[],
            market_factors=[],
            volatility_level='medium',
            trading_volume=None,
            market_summary='데이터 없음',
            next_day_outlook=None,
            raw_data={}
        )