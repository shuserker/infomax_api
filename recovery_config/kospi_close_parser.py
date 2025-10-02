# -*- coding: utf-8 -*-
"""
KOSPI CLOSE 데이터 파싱 모듈

정상 커밋 a763ef84의 원본 로직을 기반으로 복원된 증시마감 전용 파싱 모듈입니다.

주요 기능:
- 코스피/코스닥 지수 분석
- 시가총액 상위 종목 추출
- 외국인/기관 매매 동향 분석
- 섹터별 등락 현황 파악
- 한국 증시 특성 반영

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
class KoreanIndex:
    """한국 지수 데이터"""
    name: str
    value: float
    change: float
    change_percent: float
    direction: str  # 'up', 'down', 'flat'
    volume: Optional[str] = None
    market_cap: Optional[str] = None


@dataclass
class TopStock:
    """상위 종목 데이터"""
    name: str
    price: float
    change_percent: float
    direction: str
    volume: Optional[str] = None


@dataclass
class TradingFlow:
    """매매 동향 데이터"""
    foreign_net: float  # 외국인 순매수 (억원)
    institution_net: float  # 기관 순매수 (억원)
    individual_net: float  # 개인 순매수 (억원)


@dataclass
class KospiCloseData:
    """증시마감 파싱 결과"""
    title: str
    content: str
    date: str
    time: str
    market_situation: str  # '상승', '하락', '혼조'
    main_indices: List[KoreanIndex]
    top_gainers: List[TopStock]
    top_losers: List[TopStock]
    trading_flow: Optional[TradingFlow]
    sector_analysis: Dict[str, str]
    market_summary: str
    total_volume: Optional[str]
    market_cap_change: Optional[str]
    raw_data: Dict[str, Any]


class KospiCloseParser:
    """
    증시마감 전용 파싱 클래스
    
    한국 증시 데이터의 특성을 반영한 전문 파싱 기능을 제공합니다.
    """
    
    def __init__(self):
        """파서 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 한국 증시 운영 시간
        self.market_hours = {
            'regular_start': time(9, 0),    # 09:00
            'regular_end': time(15, 30),    # 15:30
            'after_hours_end': time(16, 0)  # 16:00 (시간외 단일가)
        }
        
        # 주요 지수 패턴
        self.index_patterns = {
            'kospi': [
                r'코스피\s*(?:지수)?\s*([0-9,]+\.?[0-9]*)',
                r'KOSPI\s*([0-9,]+\.?[0-9]*)',
                r'종합주가지수\s*([0-9,]+\.?[0-9]*)'
            ],
            'kosdaq': [
                r'코스닥\s*(?:지수)?\s*([0-9,]+\.?[0-9]*)',
                r'KOSDAQ\s*([0-9,]+\.?[0-9]*)',
                r'코스닥\s*종합지수\s*([0-9,]+\.?[0-9]*)'
            ],
            'kospi200': [
                r'코스피\s*200\s*([0-9,]+\.?[0-9]*)',
                r'KOSPI\s*200\s*([0-9,]+\.?[0-9]*)'
            ]
        }
        
        # 시장 상황 키워드
        self.market_keywords = {
            'positive': ['상승', '오름', '급등', '강세', '반등', '회복', '증가', '플러스', '상승세'],
            'negative': ['하락', '내림', '급락', '약세', '하락세', '감소', '마이너스', '하락세'],
            'mixed': ['혼조', '등락', '보합', '횡보', '혼재', '엇갈림', '혼조세']
        }
        
        # 섹터 키워드
        self.sector_keywords = {
            '반도체': ['반도체', '삼성전자', 'SK하이닉스', '메모리'],
            '바이오': ['바이오', '제약', '의료', '헬스케어'],
            '자동차': ['자동차', '현대차', '기아', '모빌리티'],
            '화학': ['화학', '석유화학', 'LG화학', '롯데케미칼'],
            '금융': ['은행', '증권', '보험', '금융'],
            '조선': ['조선', '해운', '현대중공업'],
            '철강': ['철강', '포스코', '현대제철'],
            '건설': ['건설', '부동산', '건설사'],
            '유통': ['유통', '백화점', '마트', '이커머스'],
            '통신': ['통신', 'KT', 'SKT', 'LGU+']
        }
    
    def parse_kospi_close_data(self, raw_data: Dict[str, Any]) -> KospiCloseData:
        """
        증시마감 데이터 파싱
        
        Args:
            raw_data (dict): 원시 증시마감 데이터
        
        Returns:
            KospiCloseData: 파싱된 증시마감 데이터
        """
        if not raw_data:
            return self._create_empty_kospi_data()
        
        try:
            # 기본 정보 추출
            title = raw_data.get('title', '')
            content = raw_data.get('content', '')
            date = raw_data.get('date', '')
            time_str = raw_data.get('time', '')
            
            # 주요 지수 추출
            main_indices = self._extract_main_indices(title, content)
            
            # 시장 상황 판단
            market_situation = self._determine_market_situation(title, content, main_indices)
            
            # 상위/하위 종목 추출
            top_gainers = self._extract_top_stocks(content, 'gainers')
            top_losers = self._extract_top_stocks(content, 'losers')
            
            # 매매 동향 추출
            trading_flow = self._extract_trading_flow(content)
            
            # 섹터 분석
            sector_analysis = self._analyze_sectors(content)
            
            # 거래량 및 시가총액 정보
            total_volume = self._extract_total_volume(content)
            market_cap_change = self._extract_market_cap_change(content)
            
            # 시장 요약 생성
            market_summary = self._generate_market_summary(
                market_situation, main_indices, trading_flow, sector_analysis
            )
            
            self.logger.info(f"증시마감 파싱 완료: {market_situation}, 지수 {len(main_indices)}개")
            
            return KospiCloseData(
                title=title,
                content=content,
                date=date,
                time=time_str,
                market_situation=market_situation,
                main_indices=main_indices,
                top_gainers=top_gainers,
                top_losers=top_losers,
                trading_flow=trading_flow,
                sector_analysis=sector_analysis,
                market_summary=market_summary,
                total_volume=total_volume,
                market_cap_change=market_cap_change,
                raw_data=raw_data
            )
            
        except Exception as e:
            self.logger.error(f"증시마감 파싱 오류: {e}")
            return self._create_empty_kospi_data()
    
    def _extract_main_indices(self, title: str, content: str) -> List[KoreanIndex]:
        """
        주요 지수 정보 추출
        
        Args:
            title (str): 제목
            content (str): 내용
        
        Returns:
            List[KoreanIndex]: 추출된 지수 리스트
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
                        
                        # 변화량과 변화율 추출
                        change, change_percent = self._extract_change_info(text, match.start())
                        
                        # 방향 판단
                        direction = 'flat'
                        if change > 0:
                            direction = 'up'
                        elif change < 0:
                            direction = 'down'
                        
                        # 거래량 및 시가총액 추출 시도
                        volume = self._extract_index_volume(text, match.start())
                        market_cap = self._extract_index_market_cap(text, match.start())
                        
                        index = KoreanIndex(
                            name=self._get_index_display_name(index_name),
                            value=value,
                            change=change,
                            change_percent=change_percent,
                            direction=direction,
                            volume=volume,
                            market_cap=market_cap
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
        # 지수 위치 주변 텍스트 추출
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
    
    def _extract_index_volume(self, text: str, position: int) -> Optional[str]:
        """지수 관련 거래량 추출"""
        start = max(0, position - 200)
        end = min(len(text), position + 200)
        context = text[start:end]
        
        volume_patterns = [
            r'거래량\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?',
            r'([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?\s*주'
        ]
        
        for pattern in volume_patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_index_market_cap(self, text: str, position: int) -> Optional[str]:
        """지수 관련 시가총액 추출"""
        start = max(0, position - 200)
        end = min(len(text), position + 200)
        context = text[start:end]
        
        cap_patterns = [
            r'시가총액\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:조|억|만)?',
            r'시총\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:조|억|만)?'
        ]
        
        for pattern in cap_patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1)
        
        return None
    
    def _get_index_display_name(self, index_name: str) -> str:
        """지수 표시명 반환"""
        display_names = {
            'kospi': '코스피',
            'kosdaq': '코스닥',
            'kospi200': '코스피200'
        }
        return display_names.get(index_name, index_name.upper())
    
    def _determine_market_situation(self, title: str, content: str, 
                                  indices: List[KoreanIndex]) -> str:
        """
        시장 상황 판단
        
        Args:
            title (str): 제목
            content (str): 내용
            indices (List[KoreanIndex]): 주요 지수들
        
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
            
            # 코스피가 있으면 가중치 부여
            kospi_direction = None
            for idx in indices:
                if idx.name == '코스피':
                    kospi_direction = idx.direction
                    break
            
            if kospi_direction == 'up':
                index_sentiment = 'positive'
            elif kospi_direction == 'down':
                index_sentiment = 'negative'
            elif up_count > down_count:
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
    
    def _extract_top_stocks(self, content: str, stock_type: str) -> List[TopStock]:
        """
        상위/하위 종목 추출
        
        Args:
            content (str): 내용
            stock_type (str): 'gainers' 또는 'losers'
        
        Returns:
            List[TopStock]: 종목 리스트
        """
        stocks = []
        
        # 상승/하락 종목 패턴
        if stock_type == 'gainers':
            patterns = [
                r'상승.*?([가-힣A-Za-z0-9]+)\s*([0-9,]+)\s*원.*?([+-]?[0-9.]+)%',
                r'급등.*?([가-힣A-Za-z0-9]+)\s*([0-9,]+)\s*원.*?([+-]?[0-9.]+)%'
            ]
        else:  # losers
            patterns = [
                r'하락.*?([가-힣A-Za-z0-9]+)\s*([0-9,]+)\s*원.*?([+-]?[0-9.]+)%',
                r'급락.*?([가-힣A-Za-z0-9]+)\s*([0-9,]+)\s*원.*?([+-]?[0-9.]+)%'
            ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    name = match[0].strip()
                    price = float(match[1].replace(',', ''))
                    change_percent = float(match[2])
                    
                    direction = 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'flat'
                    
                    stock = TopStock(
                        name=name,
                        price=price,
                        change_percent=change_percent,
                        direction=direction
                    )
                    
                    stocks.append(stock)
                    
                except (ValueError, IndexError):
                    continue
        
        # 중복 제거 및 최대 5개로 제한
        unique_stocks = []
        seen_names = set()
        for stock in stocks:
            if stock.name not in seen_names and len(unique_stocks) < 5:
                unique_stocks.append(stock)
                seen_names.add(stock.name)
        
        return unique_stocks
    
    def _extract_trading_flow(self, content: str) -> Optional[TradingFlow]:
        """
        매매 동향 추출
        
        Args:
            content (str): 내용
        
        Returns:
            Optional[TradingFlow]: 매매 동향 데이터
        """
        foreign_net = 0.0
        institution_net = 0.0
        individual_net = 0.0
        
        # 외국인 매매 패턴
        foreign_patterns = [
            r'외국인.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억',
            r'외인.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억'
        ]
        
        for pattern in foreign_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    foreign_net = float(match.group(1).replace(' ', '').replace(',', ''))
                    break
                except ValueError:
                    continue
        
        # 기관 매매 패턴
        institution_patterns = [
            r'기관.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억',
            r'기관투자자.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억'
        ]
        
        for pattern in institution_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    institution_net = float(match.group(1).replace(' ', '').replace(',', ''))
                    break
                except ValueError:
                    continue
        
        # 개인 매매 패턴
        individual_patterns = [
            r'개인.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억',
            r'개인투자자.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*억'
        ]
        
        for pattern in individual_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    individual_net = float(match.group(1).replace(' ', '').replace(',', ''))
                    break
                except ValueError:
                    continue
        
        # 데이터가 있으면 TradingFlow 객체 반환
        if foreign_net != 0 or institution_net != 0 or individual_net != 0:
            return TradingFlow(
                foreign_net=foreign_net,
                institution_net=institution_net,
                individual_net=individual_net
            )
        
        return None
    
    def _analyze_sectors(self, content: str) -> Dict[str, str]:
        """
        섹터별 분석
        
        Args:
            content (str): 내용
        
        Returns:
            Dict[str, str]: 섹터별 상황
        """
        sector_analysis = {}
        
        for sector, keywords in self.sector_keywords.items():
            sector_text = ""
            for keyword in keywords:
                if keyword in content:
                    # 키워드 주변 텍스트 추출
                    start = content.find(keyword)
                    if start != -1:
                        sector_context = content[max(0, start-50):start+100]
                        sector_text += sector_context + " "
            
            if sector_text:
                # 섹터 상황 판단
                if any(pos_word in sector_text for pos_word in self.market_keywords['positive']):
                    sector_analysis[sector] = '상승'
                elif any(neg_word in sector_text for neg_word in self.market_keywords['negative']):
                    sector_analysis[sector] = '하락'
                else:
                    sector_analysis[sector] = '보합'
        
        return sector_analysis
    
    def _extract_total_volume(self, content: str) -> Optional[str]:
        """총 거래량 추출"""
        volume_patterns = [
            r'총\s*거래량\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:억|만|천)?',
            r'거래대금\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:조|억|만)?'
        ]
        
        for pattern in volume_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_market_cap_change(self, content: str) -> Optional[str]:
        """시가총액 변화 추출"""
        cap_patterns = [
            r'시가총액.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*(?:조|억)',
            r'시총.*?([+-]?\s*[0-9,]+(?:\.[0-9]+)?)\s*(?:조|억)'
        ]
        
        for pattern in cap_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_market_summary(self, situation: str, indices: List[KoreanIndex], 
                               trading_flow: Optional[TradingFlow], 
                               sector_analysis: Dict[str, str]) -> str:
        """
        시장 요약 생성
        
        Args:
            situation (str): 시장 상황
            indices (List[KoreanIndex]): 주요 지수들
            trading_flow (Optional[TradingFlow]): 매매 동향
            sector_analysis (Dict[str, str]): 섹터 분석
        
        Returns:
            str: 시장 요약
        """
        summary_parts = []
        
        # 시장 상황
        summary_parts.append(f"한국 증시 {situation} 마감")
        
        # 주요 지수
        if indices:
            index_info = []
            for idx in indices:
                if idx.change != 0:
                    index_info.append(f"{idx.name} {idx.value:,.2f} ({idx.change:+.2f})")
                else:
                    index_info.append(f"{idx.name} {idx.value:,.2f}")
            
            if index_info:
                summary_parts.append(", ".join(index_info))
        
        # 매매 동향
        if trading_flow:
            flow_info = []
            if trading_flow.foreign_net != 0:
                flow_info.append(f"외국인 {trading_flow.foreign_net:+.0f}억")
            if trading_flow.institution_net != 0:
                flow_info.append(f"기관 {trading_flow.institution_net:+.0f}억")
            
            if flow_info:
                summary_parts.append(" | ".join(flow_info))
        
        # 주요 섹터
        if sector_analysis:
            rising_sectors = [sector for sector, status in sector_analysis.items() if status == '상승']
            if rising_sectors:
                summary_parts.append(f"상승 섹터: {', '.join(rising_sectors[:3])}")
        
        return " | ".join(summary_parts)
    
    def _create_empty_kospi_data(self) -> KospiCloseData:
        """빈 코스피 데이터 생성"""
        return KospiCloseData(
            title='',
            content='',
            date='',
            time='',
            market_situation='혼조',
            main_indices=[],
            top_gainers=[],
            top_losers=[],
            trading_flow=None,
            sector_analysis={},
            market_summary='데이터 없음',
            total_volume=None,
            market_cap_change=None,
            raw_data={}
        )


if __name__ == "__main__":
    # 테스트 코드
    import json
    
    # 샘플 데이터
    sample_data = {
        'title': '[증시마감] 코스피 2,500선 회복, 외국인 순매수 전환',
        'content': '코스피가 2,523.45로 전일 대비 +25.67포인트(+1.03%) 상승 마감했습니다. 코스닥은 756.89로 +8.45포인트(+1.13%) 올랐습니다. 외국인이 1,250억원 순매수했고, 기관은 -850억원 순매도했습니다. 반도체 업종이 강세를 보였으며, 삼성전자가 +2.5% 상승했습니다. 총 거래대금은 8.5조원을 기록했습니다.',
        'date': '20250812',
        'time': '154500'
    }
    
    parser = KospiCloseParser()
    
    print("=== 증시마감 파서 테스트 ===")
    print("원시 데이터:")
    print(json.dumps(sample_data, indent=2, ensure_ascii=False))
    print()
    
    # 데이터 파싱
    parsed_data = parser.parse_kospi_close_data(sample_data)
    
    print("파싱 결과:")
    print(f"제목: {parsed_data.title}")
    print(f"시장 상황: {parsed_data.market_situation}")
    print(f"시장 요약: {parsed_data.market_summary}")
    print()
    
    print("주요 지수:")
    for idx in parsed_data.main_indices:
        direction = "📈" if idx.direction == "up" else "📉" if idx.direction == "down" else "➡️"
        print(f"  {direction} {idx.name}: {idx.value:,.2f} ({idx.change:+.2f}, {idx.change_percent:+.2f}%)")
    print()
    
    if parsed_data.trading_flow:
        print("매매 동향:")
        print(f"  외국인: {parsed_data.trading_flow.foreign_net:+.0f}억원")
        print(f"  기관: {parsed_data.trading_flow.institution_net:+.0f}억원")
        print(f"  개인: {parsed_data.trading_flow.individual_net:+.0f}억원")
        print()
    
    if parsed_data.sector_analysis:
        print("섹터 분석:")
        for sector, status in parsed_data.sector_analysis.items():
            print(f"  {sector}: {status}")