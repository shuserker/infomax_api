# -*- coding: utf-8 -*-
"""
뉴스 데이터 파싱 로직 구현

정상 커밋 a763ef84의 원본 로직을 기반으로 복원된 뉴스 데이터 파싱 모듈입니다.

주요 기능:
- NEWYORK MARKET WATCH 데이터 파싱
- KOSPI CLOSE 데이터 파싱  
- EXCHANGE RATE 데이터 파싱
- 각 데이터 소스별 상태 판단 (최신, 발행 전, 발행 지연)
- 시간 기반 상태 분석 및 메시지 생성

작성자: AI Assistant
복원 일시: 2025-08-12
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import re
import json
from datetime import datetime, timedelta, time
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
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


class NewsDataParser:
    """
    뉴스 데이터 파싱 및 상태 판단 클래스
    
    INFOMAX API에서 받은 뉴스 데이터를 파싱하고 각 데이터 소스별로
    상태를 판단하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """파서 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 뉴스 타입별 설정 (정상 커밋에서 추출한 원본 로직 기반)
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
        
        # 한국 영업일 설정
        self.korean_holidays = [
            '20250101', '20250128', '20250129', '20250130',  # 신정, 설날
            '20250301', '20250505', '20250506', '20250815',  # 삼일절, 어린이날, 대체휴일, 광복절
            '20250917', '20250918', '20250919',              # 추석
            '20251003', '20251009', '20251225'               # 개천절, 한글날, 성탄절
        ]
    
    def parse_news_data(self, raw_data: Dict[str, Any]) -> Dict[str, NewsItem]:
        """
        원시 API 응답 데이터를 파싱하여 NewsItem 객체로 변환
        
        Args:
            raw_data (dict): API에서 받은 원시 데이터
        
        Returns:
            dict: 뉴스 타입별 NewsItem 객체 딕셔너리
        """
        parsed_items = {}
        
        if not isinstance(raw_data, dict):
            self.logger.error("원시 데이터가 딕셔너리가 아님")
            return parsed_items
        
        for news_type, news_data in raw_data.items():
            if news_type in self.news_configs:
                try:
                    parsed_item = self._parse_single_news_item(news_type, news_data)
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
    
    def _parse_single_news_item(self, news_type: str, news_data: Dict[str, Any]) -> Optional[NewsItem]:
        """
        개별 뉴스 아이템 파싱
        
        Args:
            news_type (str): 뉴스 타입
            news_data (dict): 뉴스 데이터
        
        Returns:
            NewsItem: 파싱된 뉴스 아이템
        """
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
                raw_data=news_data or {}
            )
        
        # 날짜/시간 파싱
        parsed_datetime = self._parse_datetime(date, time_str)
        
        # 상태 판단
        status_info = self._determine_news_status(news_type, date, time_str, parsed_datetime)
        
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
            parsed_datetime=parsed_datetime
        )
    
    def _determine_news_status(self, news_type: str, date: str, time_str: str, 
                             parsed_datetime: Optional[datetime]) -> Dict[str, Any]:
        """
        뉴스 상태 판단 (최신, 발행 전, 발행 지연)
        
        Args:
            news_type (str): 뉴스 타입
            date (str): 날짜 문자열
            time_str (str): 시간 문자열
            parsed_datetime (datetime): 파싱된 날짜시간
        
        Returns:
            dict: 상태 정보
        """
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
        """
        오늘 뉴스의 상태 분석 (정상 커밋의 원본 로직 복원)
        
        Args:
            news_type (str): 뉴스 타입
            news_datetime (datetime): 뉴스 발행 시간
            now (datetime): 현재 시간
        
        Returns:
            dict: 상태 분석 결과
        """
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
        """
        지연 정도 레벨 판단
        
        Args:
            news_type (str): 뉴스 타입
            delay_minutes (int): 지연 시간 (분)
        
        Returns:
            str: 지연 레벨 설명
        """
        config = self.news_configs[news_type]
        
        if delay_minutes <= 15:
            return "경미한 지연"
        elif delay_minutes <= 30:
            return "보통 지연"
        elif delay_minutes <= 60:
            return "심각한 지연"
        else:
            return "매우 심각한 지연"
    
    def _parse_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        """
        날짜/시간 문자열을 datetime 객체로 변환
        
        Args:
            date_str (str): 날짜 문자열 (YYYYMMDD)
            time_str (str): 시간 문자열 (HHMMSS 또는 HHMM)
        
        Returns:
            datetime: 변환된 datetime 객체
        """
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
        """
        시간 문자열을 time 객체로 변환
        
        Args:
            time_str (str): 시간 문자열 (HHMMSS 또는 HHMM)
        
        Returns:
            time: 변환된 time 객체
        """
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
        """
        영업일 여부 확인
        
        Args:
            date_str (str): 날짜 문자열 (YYYYMMDD)
        
        Returns:
            bool: 영업일 여부
        """
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
        """
        오류 발생 시 기본 NewsItem 생성
        
        Args:
            news_type (str): 뉴스 타입
            error_message (str): 오류 메시지
        
        Returns:
            NewsItem: 오류 상태의 NewsItem
        """
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
            raw_data={}
        )
    
    def get_status_summary(self, parsed_items: Dict[str, NewsItem]) -> Dict[str, Any]:
        """
        파싱된 뉴스 아이템들의 상태 요약 생성
        
        Args:
            parsed_items (dict): 파싱된 뉴스 아이템들
        
        Returns:
            dict: 상태 요약 정보
        """
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
        """
        파싱된 데이터 유효성 검증
        
        Args:
            parsed_items (dict): 파싱된 뉴스 아이템들
        
        Returns:
            tuple: (유효성 여부, 오류 메시지 리스트)
        """
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


if __name__ == "__main__":
    # 테스트 코드
    import logging
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 샘플 데이터
    sample_data = {
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
    
    parser = NewsDataParser()
    
    print("=== 뉴스 데이터 파서 테스트 ===")
    print("원시 데이터:")
    print(json.dumps(sample_data, indent=2, ensure_ascii=False))
    print()
    
    # 데이터 파싱
    parsed_items = parser.parse_news_data(sample_data)
    print("파싱된 데이터:")
    for news_type, news_item in parsed_items.items():
        print(f"  {news_type}:")
        print(f"    제목: {news_item.title}")
        print(f"    상태: {news_item.status.value} - {news_item.status_description}")
        print(f"    최신 여부: {news_item.is_latest}")
        print(f"    지연 여부: {news_item.is_delayed}")
        if news_item.is_delayed:
            print(f"    지연 시간: {news_item.delay_minutes}분")
        print()
    
    # 유효성 검증
    is_valid, errors = parser.validate_parsed_data(parsed_items)
    print(f"유효성 검증: {'✅ 통과' if is_valid else '❌ 실패'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    print()
    
    # 상태 요약
    summary = parser.get_status_summary(parsed_items)
    print("상태 요약:")
    print(f"  전체 뉴스: {summary['total_news']}개")
    print(f"  최신 뉴스: {summary['latest_count']}개")
    print(f"  지연 뉴스: {summary['delayed_count']}개")
    print(f"  전체 상태: {summary['overall_status']}")
    
    if summary['delayed_count'] > 0:
        print(f"  최대 지연: {summary['delay_analysis']['max_delay_minutes']}분")
        print(f"  평균 지연: {summary['delay_analysis']['avg_delay_minutes']:.1f}분")