# -*- coding: utf-8 -*-
"""
NEWYORK MARKET WATCH 데이터 파싱 모듈

정상 커밋 a763ef84의 원본 로직을 기반으로 복원된 뉴욕마켓워치 전용 파싱 모듈입니다.

주요 기능:
- 뉴욕마켓워치 데이터 구조 분석
- 시장 상황 판단 (상승/하락/혼조)
- 주요 지수 추출 (다우, 나스닥, S&P500)
- 시간대별 상태 판단 (한국시간 기준)
- 뉴욕 시장 특성 반영

작성자: AI Assistant
복원 일시: 2025-08-12
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import re
from datetime import datetime, time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging


@dataclass
class MarketIndex:
    """시장 지수 데이터"""
    name: str
    value: float
    change: float
    change_percent: float
    direction: str  # 'up', 'down', 'flat'


@dataclass
class NewYorkMarketData:
    """뉴욕마켓워치 파싱 결과"""
    title: str
    content: str
    date: str
    time: str
    market_situation: str  # '상승', '하락', '혼조'
    major_indices: List[MarketIndex]
    key_factors: List[str]
    market_summary: str
    is_after_hours: bool
    trading_volume: Optional[str]
    raw_data: Dict[str, Any]


class NewYorkMarketParser:
    """
    뉴욕마켓워치 전용 파싱 클래스
    
    뉴욕 증시 데이터의 특성을 반영한 전문 파싱 기능을 제공합니다.
    """
    
    def __init__(self):
        """파서 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 뉴욕 시장 운영 시간 (한국시간 기준)
        self.market_hours = {
            'regular_start': time(22, 30),  # 22:30 (서머타임 21:30)
            'regular_end': time(5, 0),      # 05:00 (서머타임 04:00)
            'pre_market_start': time(17, 0), # 17:00
            'after_hours_end': time(9, 0)   # 09:00
        }
        
        # 주요 지수 패턴
        self.index_patterns = {
            'dow': [
                r'다우(?:존스)?(?:\s*산업평균지수)?\s*(?:지수)?\s*([0-9,]+\.?[0-9]*)',
                r'DOW\s*([0-9,]+\.?[0-9]*)',
                r'Dow\s*Jones\s*([0-9,]+\.?[0-9]*)'
            ],
            'nasdaq': [
                r'나스닥\s*(?:종합지수)?\s*([0-9,]+\.?[0-9]*)',
                r'NASDAQ\s*([0-9,]+\.?[0-9]*)',
                r'Nasdaq\s*([0-9,]+\.?[0-9]*)'
            ],
            'sp500': [
                r'S&P\s*500\s*([0-9,]+\.?[0-9]*)',
                r'스탠더드\s*푸어\s*500\s*([0-9,]+\.?[0-9]*)',
                r'SP500\s*([0-9,]+\.?[0-9]*)'
            ]
        }
        
        # 시장 상황 키워드
        self.market_keywords = {
            'positive': ['상승', '오름', '급등', '강세', '반등', '회복', '증가', '플러스'],
            'negative': ['하락', '내림', '급락', '약세', '하락세', '감소', '마이너스'],
            'mixed': ['혼조', '등락', '보합', '횡보', '혼재', '엇갈림']
        }
    
    def parse_newyork_market_data(self, raw_data: Dict[str, Any]) -> NewYorkMarketData:
        """
        뉴욕마켓워치 데이터 파싱
        
        Args:
            raw_data (dict): 원시 뉴욕마켓워치 데이터
        
        Returns:
            NewYorkMarketData: 파싱된 뉴욕마켓워치 데이터
        """
        if not raw_data:
            return self._create_empty_market_data()
        
        try:
            # 기본 정보 추출
            title = raw_data.get('title', '')
            content = raw_data.get('content', '')
            date = raw_data.get('date', '')
            time_str = raw_data.get('time', '')
            
            # 주요 지수 추출
            major_indices = self._extract_major_indices(title, content)
            
            # 시장 상황 판단
            market_situation = self._determine_market_situation(title, content, major_indices)
            
            # 주요 요인 추출
            key_factors = self._extract_key_factors(content)
            
            # 시장 요약 생성
            market_summary = self._generate_market_summary(market_situation, major_indices, key_factors)
            
            # 시간대 분석
            is_after_hours = self._is_after_hours_trading(time_str)
            
            # 거래량 정보 추출
            trading_volume = self._extract_trading_volume(content)
            
            self.logger.info(f"뉴욕마켓워치 파싱 완료: {market_situation}, 지수 {len(major_indices)}개")
            
            return NewYorkMarketData(
                title=title,
                content=content,
                date=date,
                time=time_str,
                market_situation=market_situation,
                major_indices=major_indices,
                key_factors=key_factors,
                market_summary=market_summary,
                is_after_hours=is_after_hours,
                trading_volume=trading_volume,
                raw_data=raw_data
            )
            
        except Exception as e:
            self.logger.error(f"뉴욕마켓워치 파싱 오류: {e}")
            return self._create_empty_market_data()
    
    def _extract_major_indices(self, title: str, content: str) -> List[MarketIndex]:
        """
        주요 지수 정보 추출
        
        Args:
            title (str): 제목
            content (str): 내용
        
        Returns:
            List[MarketIndex]: 추출된 지수 리스트
        """
        indices = []
        text = f"{title} {content}"
        
        for index_name, patterns in self.index_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value_str = match.group(1).replace(',', '')
                        value = float(value_str)
                        
                        # 변화량과 변화율 추출 시도
                        change, change_percent = self._extract_change_info(text, match.start())
                        
                        # 방향 판단
                        direction = 'flat'
                        if change > 0:
                            direction = 'up'
                        elif change < 0:
                            direction = 'down'
                        
                        index = MarketIndex(
                            name=self._get_index_display_name(index_name),
                            value=value,
                            change=change,
                            change_percent=change_percent,
                            direction=direction
                        )
                        
                        indices.append(index)
                        break  # 첫 번째 매치만 사용
                        
                    except (ValueError, IndexError):
                        continue
        
        return indices
    
    def _extract_change_info(self, text: str, position: int) -> Tuple[float, float]:
        """
        지수 변화량과 변화율 추출
        
        Args:
            text (str): 텍스트
            position (int): 지수 위치
        
        Returns:
            Tuple[float, float]: (변화량, 변화율)
        """
        # 지수 위치 주변 텍스트 추출 (앞뒤 100자)
        start = max(0, position - 100)
        end = min(len(text), position + 100)
        context = text[start:end]
        
        change = 0.0
        change_percent = 0.0
        
        # 변화량 패턴 (예: +50.25, -30.15)
        change_pattern = r'([+-]?\s*[0-9,]+\.?[0-9]*)\s*(?:포인트|pt|점)?'
        change_matches = re.findall(change_pattern, context)
        
        if change_matches:
            try:
                change_str = change_matches[0].replace(' ', '').replace(',', '')
                change = float(change_str)
            except ValueError:
                pass
        
        # 변화율 패턴 (예: +2.5%, -1.8%)
        percent_pattern = r'([+-]?\s*[0-9]+\.?[0-9]*)\s*%'
        percent_matches = re.findall(percent_pattern, context)
        
        if percent_matches:
            try:
                percent_str = percent_matches[0].replace(' ', '')
                change_percent = float(percent_str)
            except ValueError:
                pass
        
        return change, change_percent
    
    def _get_index_display_name(self, index_name: str) -> str:
        """지수 표시명 반환"""
        display_names = {
            'dow': '다우존스',
            'nasdaq': '나스닥',
            'sp500': 'S&P500'
        }
        return display_names.get(index_name, index_name.upper())
    
    def _determine_market_situation(self, title: str, content: str, 
                                  indices: List[MarketIndex]) -> str:
        """
        시장 상황 판단
        
        Args:
            title (str): 제목
            content (str): 내용
            indices (List[MarketIndex]): 주요 지수들
        
        Returns:
            str: 시장 상황 ('상승', '하락', '혼조')
        """
        text = f"{title} {content}".lower()
        
        # 키워드 기반 판단
        positive_count = sum(1 for keyword in self.market_keywords['positive'] 
                           if keyword in text)
        negative_count = sum(1 for keyword in self.market_keywords['negative'] 
                           if keyword in text)
        mixed_count = sum(1 for keyword in self.market_keywords['mixed'] 
                         if keyword in text)
        
        # 지수 기반 판단
        if indices:
            up_count = sum(1 for idx in indices if idx.direction == 'up')
            down_count = sum(1 for idx in indices if idx.direction == 'down')
            
            if up_count > down_count:
                index_sentiment = 'positive'
            elif down_count > up_count:
                index_sentiment = 'negative'
            else:
                index_sentiment = 'mixed'
        else:
            index_sentiment = 'unknown'
        
        # 종합 판단
        if mixed_count > 0 or index_sentiment == 'mixed':
            return '혼조'
        elif positive_count > negative_count or index_sentiment == 'positive':
            return '상승'
        elif negative_count > positive_count or index_sentiment == 'negative':
            return '하락'
        else:
            return '혼조'
    
    def _extract_key_factors(self, content: str) -> List[str]:
        """
        주요 요인 추출
        
        Args:
            content (str): 내용
        
        Returns:
            List[str]: 주요 요인 리스트
        """
        factors = []
        
        # 주요 키워드 패턴
        factor_patterns = [
            r'(연준|Fed|금리|인플레이션|물가).*?(?:[.。]|$)',
            r'(실적|어닝|earnings).*?(?:[.。]|$)',
            r'(중국|무역|관세).*?(?:[.。]|$)',
            r'(유가|원유|oil).*?(?:[.。]|$)',
            r'(기술주|테크|tech).*?(?:[.。]|$)',
            r'(경제지표|GDP|고용).*?(?:[.。]|$)'
        ]
        
        for pattern in factor_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) > 10 and len(match) < 100:  # 적절한 길이
                    factors.append(match.strip())
        
        # 중복 제거 및 최대 5개로 제한
        unique_factors = list(dict.fromkeys(factors))[:5]
        
        return unique_factors
    
    def _generate_market_summary(self, situation: str, indices: List[MarketIndex], 
                               factors: List[str]) -> str:
        """
        시장 요약 생성
        
        Args:
            situation (str): 시장 상황
            indices (List[MarketIndex]): 주요 지수들
            factors (List[str]): 주요 요인들
        
        Returns:
            str: 시장 요약
        """
        summary_parts = []
        
        # 시장 상황
        summary_parts.append(f"뉴욕 증시 {situation} 마감")
        
        # 주요 지수
        if indices:
            index_info = []
            for idx in indices:
                direction_symbol = "📈" if idx.direction == "up" else "📉" if idx.direction == "down" else "➡️"
                if idx.change != 0:
                    index_info.append(f"{idx.name} {idx.value:,.0f} ({idx.change:+.1f})")
                else:
                    index_info.append(f"{idx.name} {idx.value:,.0f}")
            
            if index_info:
                summary_parts.append(", ".join(index_info))
        
        # 주요 요인 (간단히)
        if factors:
            summary_parts.append(f"주요 요인: {factors[0][:30]}...")
        
        return " | ".join(summary_parts)
    
    def _is_after_hours_trading(self, time_str: str) -> bool:
        """
        시간외 거래 시간 여부 판단
        
        Args:
            time_str (str): 시간 문자열
        
        Returns:
            bool: 시간외 거래 시간 여부
        """
        try:
            if len(time_str) >= 4:
                hour = int(time_str[:2])
                minute = int(time_str[2:4])
                current_time = time(hour, minute)
                
                # 정규 거래시간 (22:30-05:00) 외의 시간
                regular_start = self.market_hours['regular_start']
                regular_end = self.market_hours['regular_end']
                
                # 시간 비교 (자정을 넘나드는 경우 고려)
                if regular_start > regular_end:  # 자정을 넘는 경우
                    return not (current_time >= regular_start or current_time <= regular_end)
                else:
                    return not (regular_start <= current_time <= regular_end)
                    
        except (ValueError, IndexError):
            pass
        
        return False
    
    def _extract_trading_volume(self, content: str) -> Optional[str]:
        """
        거래량 정보 추출
        
        Args:
            content (str): 내용
        
        Returns:
            Optional[str]: 거래량 정보
        """
        volume_patterns = [
            r'거래량\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?',
            r'volume\s*([0-9,]+(?:\.[0-9]+)?)',
            r'([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?\s*주'
        ]
        
        for pattern in volume_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _create_empty_market_data(self) -> NewYorkMarketData:
        """빈 마켓 데이터 생성"""
        return NewYorkMarketData(
            title='',
            content='',
            date='',
            time='',
            market_situation='혼조',
            major_indices=[],
            key_factors=[],
            market_summary='데이터 없음',
            is_after_hours=False,
            trading_volume=None,
            raw_data={}
        )


if __name__ == "__main__":
    # 테스트 코드
    import json
    
    # 샘플 데이터
    sample_data = {
        'title': '[뉴욕마켓워치] 미국 증시 상승 마감, 다우 35,000선 돌파',
        'content': '뉴욕 증시가 상승세로 마감했습니다. 다우존스 산업평균지수는 35,123.45로 전일 대비 +150.25포인트(+0.43%) 상승했습니다. 나스닥 종합지수는 14,567.89로 +45.67포인트(+0.31%) 올랐고, S&P500 지수는 4,456.78로 +25.34포인트(+0.57%) 상승했습니다. 연준의 금리 정책에 대한 기대감이 시장을 끌어올렸습니다.',
        'date': '20250812',
        'time': '060500'
    }
    
    parser = NewYorkMarketParser()
    
    print("=== 뉴욕마켓워치 파서 테스트 ===")
    print("원시 데이터:")
    print(json.dumps(sample_data, indent=2, ensure_ascii=False))
    print()
    
    # 데이터 파싱
    parsed_data = parser.parse_newyork_market_data(sample_data)
    
    print("파싱 결과:")
    print(f"제목: {parsed_data.title}")
    print(f"시장 상황: {parsed_data.market_situation}")
    print(f"시간외 거래: {parsed_data.is_after_hours}")
    print(f"시장 요약: {parsed_data.market_summary}")
    print()
    
    print("주요 지수:")
    for idx in parsed_data.major_indices:
        direction = "📈" if idx.direction == "up" else "📉" if idx.direction == "down" else "➡️"
        print(f"  {direction} {idx.name}: {idx.value:,.2f} ({idx.change:+.2f}, {idx.change_percent:+.2f}%)")
    print()
    
    print("주요 요인:")
    for factor in parsed_data.key_factors:
        print(f"  - {factor}")