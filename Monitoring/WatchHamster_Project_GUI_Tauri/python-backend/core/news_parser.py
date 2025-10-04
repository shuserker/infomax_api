# -*- coding: utf-8 -*-
"""
통합 뉴스 데이터 파싱 시스템

기존 WatchHamster_Project의 news_data_parser.py, exchange_rate_parser.py, 
newyork_market_parser.py, kospi_close_parser.py를 통합하여 
3가지 뉴스 타입별 파싱 로직을 제공하는 통합 파서입니다.

주요 기능:
- 3가지 뉴스 타입별 전문 파싱 (exchange-rate, newyork-market-watch, kospi-close)
- 뉴스 상태 판단 알고리즘 (최신/지연/과거)
- 영업일/비영업일 판단 로직
- 실시간 상태 분석 및 메트릭 수집
- 통합된 데이터 모델 및 검증

작성자: AI Assistant
작성 일시: 2025-01-02
기반: WatchHamster_Project/core/news_data_parser.py 및 개별 파서들
"""

import re
import json
from datetime import datetime, timedelta, time
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class NewsStatus(Enum):
    """뉴스 상태 열거형"""
    LATEST = "latest"           # 최신
    DELAYED = "delayed"         # 발행 지연
    EARLY = "early"            # 조기 발행
    OLD = "old"                # 과거 뉴스
    NO_DATA = "no_data"        # 데이터 없음
    INVALID = "invalid"        # 유효하지 않음
    PENDING = "pending"        # 발행 전
    ERROR = "error"            # 오류


@dataclass
class NewsItem:
    """뉴스 아이템 데이터 클래스"""
    news_type: str
    title: str
    content: str
    date: str
    time: str
    status: NewsStatus
    status_description: str
    is_latest: bool
    is_delayed: bool
    delay_minutes: int
    expected_time: str
    display_name: str
    emoji: str
    raw_data: Dict[str, Any]
    parsed_datetime: Optional[datetime] = None
    
    # 타입별 전문 데이터
    specialized_data: Optional[Dict[str, Any]] = None


@dataclass
class NewsTypeConfig:
    """뉴스 타입별 설정"""
    display_name: str
    emoji: str
    expected_publish_time: str
    expected_time_range: Dict[str, str]
    delay_check_times: List[str]
    tolerance_minutes: int
    time_format: str
    business_hours_only: bool = True


@dataclass
class CurrencyRate:
    """통화 환율 데이터"""
    currency_pair: str
    rate: float
    change: float
    change_percent: float
    direction: str
    high: Optional[float] = None
    low: Optional[float] = None


@dataclass
class MarketIndex:
    """시장 지수 데이터"""
    name: str
    value: float
    change: float
    change_percent: float
    direction: str


@dataclass
class TradingFlow:
    """매매 동향 데이터"""
    foreign_net: float
    institution_net: float
    individual_net: float


class NewsDataParser:
    """
    통합 뉴스 데이터 파싱 및 상태 판단 클래스
    
    INFOMAX API에서 받은 뉴스 데이터를 파싱하고 각 데이터 소스별로
    상태를 판단하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """파서 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 뉴스 타입별 설정
        self.news_configs = {
            'newyork-market-watch': NewsTypeConfig(
                display_name='뉴욕마켓워치',
                emoji='🌆',
                expected_publish_time='060000',
                expected_time_range={'start': '055500', 'end': '061500'},
                delay_check_times=['070000', '073000', '080000', '083000'],
                tolerance_minutes=15,
                time_format='6digit',
                business_hours_only=False  # 24시간 운영
            ),
            'kospi-close': NewsTypeConfig(
                display_name='증시마감',
                emoji='📈',
                expected_publish_time='154000',
                expected_time_range={'start': '153500', 'end': '155000'},
                delay_check_times=['155500', '160000', '163000', '170000'],
                tolerance_minutes=10,
                time_format='6digit',
                business_hours_only=True
            ),
            'exchange-rate': NewsTypeConfig(
                display_name='서환마감',
                emoji='💱',
                expected_publish_time='163000',
                expected_time_range={'start': '162500', 'end': '163500'},
                delay_check_times=['164000', '170000', '173000', '180000'],
                tolerance_minutes=5,
                time_format='6digit',
                business_hours_only=True
            )
        }
        
        # 한국 영업일 설정 (2025년 기준)
        self.korean_holidays = [
            '20250101', '20250128', '20250129', '20250130',  # 신정, 설날
            '20250301', '20250505', '20250506', '20250815',  # 삼일절, 어린이날, 대체휴일, 광복절
            '20250917', '20250918', '20250919',              # 추석
            '20251003', '20251009', '20251225'               # 개천절, 한글날, 성탄절
        ]
        
        # 통화 패턴 (서환마감용)
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
                r'JPY/KRW\s*([0-9,]+\.?[0-9]*)'
            ],
            'eur_krw': [
                r'유로\s*(?:환율)?\s*([0-9,]+\.?[0-9]*)',
                r'EUR/KRW\s*([0-9,]+\.?[0-9]*)'
            ]
        }
        
        # 지수 패턴 (뉴욕마켓워치, 증시마감용)
        self.index_patterns = {
            # 뉴욕 지수
            'dow': [
                r'다우(?:존스)?(?:\s*산업평균지수)?\s*(?:지수)?\s*([0-9,]+\.?[0-9]*)',
                r'DOW\s*([0-9,]+\.?[0-9]*)',
                r'Dow\s*Jones\s*([0-9,]+\.?[0-9]*)'
            ],
            'nasdaq': [
                r'나스닥\s*(?:종합지수)?\s*([0-9,]+\.?[0-9]*)',
                r'NASDAQ\s*([0-9,]+\.?[0-9]*)'
            ],
            'sp500': [
                r'S&P\s*500\s*([0-9,]+\.?[0-9]*)',
                r'스탠더드\s*푸어\s*500\s*([0-9,]+\.?[0-9]*)'
            ],
            # 한국 지수
            'kospi': [
                r'코스피\s*(?:지수)?\s*([0-9,]+\.?[0-9]*)',
                r'KOSPI\s*([0-9,]+\.?[0-9]*)',
                r'종합주가지수\s*([0-9,]+\.?[0-9]*)'
            ],
            'kosdaq': [
                r'코스닥\s*(?:지수)?\s*([0-9,]+\.?[0-9]*)',
                r'KOSDAQ\s*([0-9,]+\.?[0-9]*)'
            ]
        }
        
        # 시장 상황 키워드
        self.market_keywords = {
            'positive': ['상승', '오름', '급등', '강세', '반등', '회복', '증가', '플러스'],
            'negative': ['하락', '내림', '급락', '약세', '하락세', '감소', '마이너스'],
            'mixed': ['혼조', '등락', '보합', '횡보', '혼재', '엇갈림']
        }
        
        self.logger.info("통합 뉴스 데이터 파서 초기화 완료")
    
    async def parse_news_data(self, raw_data: Dict[str, Any]) -> Dict[str, NewsItem]:
        """원시 API 응답 데이터를 파싱하여 NewsItem 객체로 변환"""
        parsed_items = {}
        
        if not isinstance(raw_data, dict):
            self.logger.error("원시 데이터가 딕셔너리가 아님")
            return parsed_items
        
        for news_type, news_data in raw_data.items():
            if news_type in self.news_configs:
                try:
                    parsed_item = await self._parse_single_news_item(news_type, news_data)
                    if parsed_item:
                        parsed_items[news_type] = parsed_item
                        self.logger.debug(f"{news_type} 파싱 성공: {parsed_item.status.value}")
                except Exception as e:
                    self.logger.error(f"{news_type} 파싱 실패: {e}")
                    # 오류 발생 시에도 기본 NewsItem 생성
                    parsed_items[news_type] = self._create_error_news_item(news_type, str(e))
            else:
                self.logger.warning(f"알 수 없는 뉴스 타입: {news_type}")
        
        self.logger.info(f"뉴스 데이터 파싱 완료: {len(parsed_items)}개 타입")
        return parsed_items
    
    async def _parse_single_news_item(self, news_type: str, news_data: Dict[str, Any]) -> Optional[NewsItem]:
        """개별 뉴스 아이템 파싱"""
        config = self.news_configs[news_type]
        
        # 기본 데이터 추출
        title = news_data.get('title', '') if news_data else ''
        content = news_data.get('content', '') if news_data else ''
        date = news_data.get('date', '') if news_data else ''
        time_str = news_data.get('time', '') if news_data else ''
        
        # 데이터가 없는 경우
        if not news_data or not title:
            return NewsItem(
                news_type=news_type,
                title='',
                content='',
                date='',
                time='',
                status=NewsStatus.NO_DATA,
                status_description='데이터 없음',
                is_latest=False,
                is_delayed=False,
                delay_minutes=0,
                expected_time=config.expected_publish_time,
                display_name=config.display_name,
                emoji=config.emoji,
                raw_data=news_data or {},
                specialized_data=None
            )
        
        # 날짜/시간 파싱
        parsed_datetime = self._parse_datetime(date, time_str)
        
        # 상태 판단
        status_info = self._determine_news_status(news_type, date, time_str, parsed_datetime)
        
        # 타입별 전문 데이터 파싱
        specialized_data = await self._parse_specialized_data(news_type, title, content)
        
        return NewsItem(
            news_type=news_type,
            title=title,
            content=content,
            date=date,
            time=time_str,
            status=status_info['status'],
            status_description=status_info['description'],
            is_latest=status_info['is_latest'],
            is_delayed=status_info['is_delayed'],
            delay_minutes=status_info['delay_minutes'],
            expected_time=config.expected_publish_time,
            display_name=config.display_name,
            emoji=config.emoji,
            raw_data=news_data,
            parsed_datetime=parsed_datetime,
            specialized_data=specialized_data
        )
    
    async def _parse_specialized_data(self, news_type: str, title: str, content: str) -> Optional[Dict[str, Any]]:
        """타입별 전문 데이터 파싱"""
        text = f"{title} {content}"
        
        try:
            if news_type == 'exchange-rate':
                return await self._parse_exchange_rate_data(text)
            elif news_type == 'newyork-market-watch':
                return await self._parse_newyork_market_data(text)
            elif news_type == 'kospi-close':
                return await self._parse_kospi_close_data(text)
        except Exception as e:
            self.logger.error(f"{news_type} 전문 데이터 파싱 오류: {e}")
        
        return None
    
    async def _parse_exchange_rate_data(self, text: str) -> Dict[str, Any]:
        """서환마감 전문 데이터 파싱"""
        exchange_data = {
            'market_situation': '보합',
            'usd_krw_rate': None,
            'major_currencies': [],
            'volatility_level': 'medium'
        }
        
        # 원달러 환율 추출
        for pattern in self.currency_patterns['usd_krw']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rate_str = match.group(1).replace(',', '')
                    rate = float(rate_str)
                    
                    # 변화량과 변화율 추출
                    change, change_percent = self._extract_rate_change(text, match.start())
                    
                    exchange_data['usd_krw_rate'] = {
                        'currency_pair': 'USD/KRW',
                        'rate': rate,
                        'change': change,
                        'change_percent': change_percent,
                        'direction': 'up' if change > 0 else 'down' if change < 0 else 'flat'
                    }
                    break
                except (ValueError, IndexError):
                    continue
        
        # 주요 통화 환율 추출
        major_currencies = []
        for currency_name, patterns in self.currency_patterns.items():
            if currency_name == 'usd_krw':
                continue
                
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        rate_str = match.group(1).replace(',', '')
                        rate = float(rate_str)
                        
                        change, change_percent = self._extract_rate_change(text, match.start())
                        
                        major_currencies.append({
                            'currency_pair': currency_name.upper().replace('_', '/'),
                            'rate': rate,
                            'change': change,
                            'change_percent': change_percent,
                            'direction': 'up' if change > 0 else 'down' if change < 0 else 'flat'
                        })
                        break
                    except (ValueError, IndexError):
                        continue
        
        exchange_data['major_currencies'] = major_currencies
        
        # 시장 상황 판단
        exchange_data['market_situation'] = self._determine_market_situation_from_text(text)
        
        return exchange_data
    
    async def _parse_newyork_market_data(self, text: str) -> Dict[str, Any]:
        """뉴욕마켓워치 전문 데이터 파싱"""
        market_data = {
            'market_situation': '혼조',
            'major_indices': [],
            'key_factors': []
        }
        
        # 주요 지수 추출
        major_indices = []
        for index_name in ['dow', 'nasdaq', 'sp500']:
            if index_name in self.index_patterns:
                for pattern in self.index_patterns[index_name]:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        try:
                            value_str = match.group(1).replace(',', '')
                            value = float(value_str)
                            
                            change, change_percent = self._extract_change_info(text, match.start())
                            
                            major_indices.append({
                                'name': self._get_index_display_name(index_name),
                                'value': value,
                                'change': change,
                                'change_percent': change_percent,
                                'direction': 'up' if change > 0 else 'down' if change < 0 else 'flat'
                            })
                            break
                        except (ValueError, IndexError):
                            continue
        
        market_data['major_indices'] = major_indices
        
        # 주요 요인 추출
        factor_patterns = [
            r'(연준|Fed|금리|인플레이션).*?(?:[.。]|$)',
            r'(실적|어닝|earnings).*?(?:[.。]|$)',
            r'(중국|무역|관세).*?(?:[.。]|$)',
            r'(유가|원유|oil).*?(?:[.。]|$)'
        ]
        
        key_factors = []
        for pattern in factor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 10 and len(match) < 100:
                    key_factors.append(match.strip())
        
        market_data['key_factors'] = key_factors[:5]  # 최대 5개
        
        # 시장 상황 판단
        market_data['market_situation'] = self._determine_market_situation_from_text(text)
        
        return market_data
    
    async def _parse_kospi_close_data(self, text: str) -> Dict[str, Any]:
        """증시마감 전문 데이터 파싱"""
        kospi_data = {
            'market_situation': '혼조',
            'main_indices': [],
            'trading_flow': None,
            'sector_analysis': {}
        }
        
        # 주요 지수 추출
        main_indices = []
        for index_name in ['kospi', 'kosdaq']:
            if index_name in self.index_patterns:
                for pattern in self.index_patterns[index_name]:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        try:
                            value_str = match.group(1).replace(',', '')
                            value = float(value_str)
                            
                            change, change_percent = self._extract_change_info(text, match.start())
                            
                            main_indices.append({
                                'name': self._get_index_display_name(index_name),
                                'value': value,
                                'change': change,
                                'change_percent': change_percent,
                                'direction': 'up' if change > 0 else 'down' if change < 0 else 'flat'
                            })
                            break
                        except (ValueError, IndexError):
                            continue
        
        kospi_data['main_indices'] = main_indices
        
        # 매매 동향 추출
        trading_flow = {}
        
        # 외국인 매매
        foreign_pattern = r'외국인.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억'
        foreign_match = re.search(foreign_pattern, text)
        if foreign_match:
            try:
                trading_flow['foreign_net'] = float(foreign_match.group(1).replace(' ', '').replace(',', ''))
            except ValueError:
                pass
        
        # 기관 매매
        institution_pattern = r'기관.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억'
        institution_match = re.search(institution_pattern, text)
        if institution_match:
            try:
                trading_flow['institution_net'] = float(institution_match.group(1).replace(' ', '').replace(',', ''))
            except ValueError:
                pass
        
        if trading_flow:
            kospi_data['trading_flow'] = trading_flow
        
        # 시장 상황 판단
        kospi_data['market_situation'] = self._determine_market_situation_from_text(text)
        
        return kospi_data
    
    def _extract_rate_change(self, text: str, position: int) -> Tuple[float, float]:
        """환율 변화량과 변화율 추출"""
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
    
    def _extract_change_info(self, text: str, position: int) -> Tuple[float, float]:
        """지수 변화량과 변화율 추출"""
        start = max(0, position - 100)
        end = min(len(text), position + 100)
        context = text[start:end]
        
        change = 0.0
        change_percent = 0.0
        
        # 변화량 패턴
        change_patterns = [
            r'([+-]?\s*[0-9,]+\.?[0-9]*)\s*(?:포인트|pt|점)',
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
    
    def _get_index_display_name(self, index_name: str) -> str:
        """지수 표시명 반환"""
        display_names = {
            'dow': '다우존스',
            'nasdaq': '나스닥',
            'sp500': 'S&P500',
            'kospi': '코스피',
            'kosdaq': '코스닥'
        }
        return display_names.get(index_name, index_name.upper())
    
    def _determine_market_situation_from_text(self, text: str) -> str:
        """텍스트에서 시장 상황 판단"""
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.market_keywords['positive'] 
                           if keyword in text_lower)
        negative_count = sum(1 for keyword in self.market_keywords['negative'] 
                           if keyword in text_lower)
        mixed_count = sum(1 for keyword in self.market_keywords['mixed'] 
                         if keyword in text_lower)
        
        if mixed_count > 0:
            return '혼조'
        elif positive_count > negative_count:
            return '상승'
        elif negative_count > positive_count:
            return '하락'
        else:
            return '보합'
    
    def _determine_news_status(self, news_type: str, date: str, time_str: str, 
                             parsed_datetime: Optional[datetime]) -> Dict[str, Any]:
        """뉴스 상태 판단 (최신, 발행 전, 발행 지연)"""
        config = self.news_configs[news_type]
        now = datetime.now()
        today_str = now.strftime('%Y%m%d')
        
        # 기본 상태 정보
        status_info = {
            'status': NewsStatus.INVALID,
            'description': '상태 불명',
            'is_latest': False,
            'is_delayed': False,
            'delay_minutes': 0
        }
        
        # 날짜/시간 정보가 유효하지 않은 경우
        if not date or not time_str or not parsed_datetime:
            status_info.update({
                'status': NewsStatus.INVALID,
                'description': '시간 정보 오류'
            })
            return status_info
        
        # 영업일 확인 (필요한 경우)
        if config.business_hours_only and not self._is_business_day(date):
            status_info.update({
                'status': NewsStatus.OLD,
                'description': '비영업일 뉴스'
            })
            return status_info
        
        # 날짜별 상태 판단
        if date == today_str:
            # 오늘 뉴스 - 시간 기반 상태 판단
            return self._analyze_today_news_status(news_type, parsed_datetime, now)
        elif date < today_str:
            # 과거 뉴스
            days_ago = (now.date() - parsed_datetime.date()).days
            status_info.update({
                'status': NewsStatus.OLD,
                'description': f'{days_ago}일 전 뉴스',
                'is_latest': False
            })
        else:
            # 미래 뉴스 (시스템 시간 오류?)
            status_info.update({
                'status': NewsStatus.INVALID,
                'description': '미래 뉴스 (시간 오류?)',
                'is_latest': False
            })
        
        return status_info
    
    def _analyze_today_news_status(self, news_type: str, news_datetime: datetime, 
                                 now: datetime) -> Dict[str, Any]:
        """오늘 뉴스의 상태 분석"""
        config = self.news_configs[news_type]
        
        # 예상 발행 시간 파싱
        expected_time = self._parse_time_string(config.expected_publish_time)
        if not expected_time:
            return {
                'status': NewsStatus.LATEST,
                'description': '최신',
                'is_latest': True,
                'is_delayed': False,
                'delay_minutes': 0
            }
        
        # 예상 발행 시간을 오늘 날짜로 변환
        expected_datetime = datetime.combine(now.date(), expected_time)
        
        # 시간 차이 계산 (분 단위)
        time_diff_minutes = (news_datetime - expected_datetime).total_seconds() / 60
        
        # 허용 오차 범위 확인
        tolerance = config.tolerance_minutes
        
        if abs(time_diff_minutes) <= tolerance:
            # 정시 발행 (허용 오차 범위 내)
            return {
                'status': NewsStatus.LATEST,
                'description': '최신 (정시 발행)',
                'is_latest': True,
                'is_delayed': False,
                'delay_minutes': 0
            }
        elif time_diff_minutes > tolerance:
            # 지연 발행
            delay_minutes = int(time_diff_minutes)
            delay_level = self._get_delay_level(news_type, delay_minutes)
            
            return {
                'status': NewsStatus.DELAYED,
                'description': f'지연 발행 ({delay_minutes}분 지연, {delay_level})',
                'is_latest': True,
                'is_delayed': True,
                'delay_minutes': delay_minutes
            }
        else:
            # 조기 발행
            early_minutes = int(abs(time_diff_minutes))
            return {
                'status': NewsStatus.EARLY,
                'description': f'조기 발행 ({early_minutes}분 빠름)',
                'is_latest': True,
                'is_delayed': False,
                'delay_minutes': 0
            }
    
    def _get_delay_level(self, news_type: str, delay_minutes: int) -> str:
        """지연 정도 레벨 판단"""
        if delay_minutes <= 15:
            return "경미한 지연"
        elif delay_minutes <= 30:
            return "보통 지연"
        elif delay_minutes <= 60:
            return "심각한 지연"
        else:
            return "매우 심각한 지연"
    
    def _parse_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        """날짜/시간 문자열을 datetime 객체로 변환"""
        try:
            # 날짜 파싱 (YYYYMMDD)
            if len(date_str) == 8 and date_str.isdigit():
                date_obj = datetime.strptime(date_str, '%Y%m%d').date()
            else:
                return None
            
            # 시간 파싱
            time_obj = self._parse_time_string(time_str)
            if not time_obj:
                return None
            
            return datetime.combine(date_obj, time_obj)
            
        except Exception as e:
            self.logger.error(f"날짜/시간 파싱 오류: {date_str} {time_str} - {e}")
            return None
    
    def _parse_time_string(self, time_str: str) -> Optional[time]:
        """시간 문자열을 time 객체로 변환"""
        try:
            # 숫자가 아닌 문자 제거
            clean_time = re.sub(r'[^0-9]', '', time_str)
            
            if len(clean_time) == 6:
                # HHMMSS 형식
                return datetime.strptime(clean_time, '%H%M%S').time()
            elif len(clean_time) == 4:
                # HHMM 형식
                return datetime.strptime(clean_time, '%H%M').time()
            elif len(clean_time) == 5:
                # HMMSS 형식 (앞자리 0 누락)
                return datetime.strptime(clean_time.zfill(6), '%H%M%S').time()
            elif len(clean_time) == 3:
                # HMM 형식 (앞자리 0 누락)
                return datetime.strptime(clean_time.zfill(4), '%H%M').time()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"시간 문자열 파싱 오류: {time_str} - {e}")
            return None
    
    def _is_business_day(self, date_str: str) -> bool:
        """영업일 여부 확인"""
        try:
            # 공휴일 확인
            if date_str in self.korean_holidays:
                return False
            
            # 주말 확인
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            weekday = date_obj.weekday()  # 0=월요일, 6=일요일
            
            # 토요일(5), 일요일(6)은 비영업일
            return weekday < 5
            
        except Exception:
            return True  # 파싱 실패 시 영업일로 간주
    
    def _create_error_news_item(self, news_type: str, error_message: str) -> NewsItem:
        """오류 발생 시 기본 NewsItem 생성"""
        config = self.news_configs.get(news_type)
        if not config:
            config = NewsTypeConfig(
                display_name=news_type.upper(),
                emoji='📰',
                expected_publish_time='120000',
                expected_time_range={'start': '115500', 'end': '120500'},
                delay_check_times=['130000'],
                tolerance_minutes=30,
                time_format='6digit'
            )
        
        return NewsItem(
            news_type=news_type,
            title='',
            content='',
            date='',
            time='',
            status=NewsStatus.ERROR,
            status_description=f'파싱 오류: {error_message}',
            is_latest=False,
            is_delayed=False,
            delay_minutes=0,
            expected_time=config.expected_publish_time,
            display_name=config.display_name,
            emoji=config.emoji,
            raw_data={},
            specialized_data=None
        )
    
    def get_status_summary(self, parsed_items: Dict[str, NewsItem]) -> Dict[str, Any]:
        """파싱된 뉴스 아이템들의 상태 요약 생성"""
        summary = {
            'total_news': len(parsed_items),
            'latest_count': 0,
            'delayed_count': 0,
            'old_count': 0,
            'no_data_count': 0,
            'error_count': 0,
            'overall_status': 'unknown',
            'news_status': {},
            'delay_analysis': {
                'max_delay_minutes': 0,
                'avg_delay_minutes': 0,
                'delayed_news_types': []
            }
        }
        
        total_delay = 0
        delayed_count = 0
        
        for news_type, news_item in parsed_items.items():
            status = news_item.status
            
            # 개별 뉴스 상태 정보
            summary['news_status'][news_type] = {
                'status': status.value,
                'description': news_item.status_description,
                'is_latest': news_item.is_latest,
                'is_delayed': news_item.is_delayed,
                'delay_minutes': news_item.delay_minutes,
                'display_name': news_item.display_name,
                'emoji': news_item.emoji
            }
            
            # 카운트 업데이트
            if status == NewsStatus.LATEST:
                summary['latest_count'] += 1
            elif status == NewsStatus.DELAYED:
                summary['delayed_count'] += 1
                total_delay += news_item.delay_minutes
                delayed_count += 1
                summary['delay_analysis']['delayed_news_types'].append(news_type)
                summary['delay_analysis']['max_delay_minutes'] = max(
                    summary['delay_analysis']['max_delay_minutes'],
                    news_item.delay_minutes
                )
            elif status == NewsStatus.OLD:
                summary['old_count'] += 1
            elif status == NewsStatus.NO_DATA:
                summary['no_data_count'] += 1
            elif status == NewsStatus.ERROR:
                summary['error_count'] += 1
        
        # 평균 지연 시간 계산
        if delayed_count > 0:
            summary['delay_analysis']['avg_delay_minutes'] = total_delay / delayed_count
        
        # 전체 상태 판단
        if summary['error_count'] > 0:
            summary['overall_status'] = 'error'
        elif summary['latest_count'] == summary['total_news']:
            summary['overall_status'] = 'all_latest'
        elif summary['latest_count'] > 0:
            summary['overall_status'] = 'partial_latest'
        elif summary['delayed_count'] > 0:
            summary['overall_status'] = 'has_delayed'
        elif summary['no_data_count'] > 0:
            summary['overall_status'] = 'no_data'
        else:
            summary['overall_status'] = 'all_old'
        
        return summary
    
    def validate_parsed_data(self, parsed_items: Dict[str, NewsItem]) -> Tuple[bool, List[str]]:
        """파싱된 데이터 유효성 검증"""
        errors = []
        
        if not isinstance(parsed_items, dict):
            errors.append("파싱된 데이터가 딕셔너리가 아님")
            return False, errors
        
        if not parsed_items:
            errors.append("파싱된 데이터가 비어있음")
            return False, errors
        
        # 각 뉴스 아이템 검증
        for news_type, news_item in parsed_items.items():
            if not isinstance(news_item, NewsItem):
                errors.append(f"{news_type}: NewsItem 객체가 아님")
                continue
            
            # 필수 필드 검증
            if not news_item.news_type:
                errors.append(f"{news_type}: news_type 필드 누락")
            
            if news_item.status == NewsStatus.ERROR:
                errors.append(f"{news_type}: 파싱 오류 상태")
            
            # 뉴스 타입 설정 확인
            if news_type not in self.news_configs:
                errors.append(f"{news_type}: 알 수 없는 뉴스 타입")
        
        is_valid = len(errors) == 0
        return is_valid, errors


# 팩토리 함수
def create_news_parser() -> NewsDataParser:
    """뉴스 파서 팩토리 함수"""
    return NewsDataParser()


if __name__ == "__main__":
    # 테스트 코드
    import asyncio
    
    async def test_news_parser():
        """뉴스 파서 테스트"""
        parser = NewsDataParser()
        
        # 테스트 데이터
        test_data = {
            'exchange-rate': {
                'title': '원달러 환율 1,350원 마감',
                'content': '원달러 환율이 전일 대비 5원 상승한 1,350원에 마감했습니다.',
                'date': '20250102',
                'time': '163000'
            },
            'newyork-market-watch': {
                'title': '뉴욕증시 상승 마감',
                'content': '다우존스 35,000포인트, 나스닥 14,000포인트로 상승 마감',
                'date': '20250102',
                'time': '060000'
            },
            'kospi-close': {
                'title': '코스피 2,500포인트 상승 마감',
                'content': '코스피가 전일 대비 20포인트 상승한 2,500포인트에 마감',
                'date': '20250102',
                'time': '154000'
            }
        }
        
        print("=== 통합 뉴스 파서 테스트 ===")
        
        # 파싱 테스트
        parsed_items = await parser.parse_news_data(test_data)
        
        print(f"파싱된 뉴스 아이템: {len(parsed_items)}개")
        
        for news_type, news_item in parsed_items.items():
            print(f"\n{news_item.emoji} {news_item.display_name}")
            print(f"  상태: {news_item.status.value}")
            print(f"  설명: {news_item.status_description}")
            print(f"  최신 여부: {news_item.is_latest}")
            print(f"  지연 여부: {news_item.is_delayed}")
            if news_item.specialized_data:
                print(f"  전문 데이터: {len(news_item.specialized_data)}개 필드")
        
        # 상태 요약 테스트
        summary = parser.get_status_summary(parsed_items)
        print(f"\n전체 상태: {summary['overall_status']}")
        print(f"최신 뉴스: {summary['latest_count']}개")
        print(f"지연 뉴스: {summary['delayed_count']}개")
        
        # 검증 테스트
        is_valid, errors = parser.validate_parsed_data(parsed_items)
        print(f"\n데이터 유효성: {'유효' if is_valid else '오류'}")
        if errors:
            for error in errors:
                print(f"  - {error}")
    
    # 테스트 실행
    asyncio.run(test_news_parser())