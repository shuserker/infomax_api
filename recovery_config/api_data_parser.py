# -*- coding: utf-8 -*-
"""
API 응답 데이터 파싱 및 검증 모듈

INFOMAX API에서 받은 응답 데이터를 파싱하고 검증하는 기능을 제공합니다.

주요 기능:
- 뉴스 데이터 파싱 (NEWYORK MARKET WATCH, KOSPI CLOSE, EXCHANGE RATE)
- 데이터 상태 판단 (최신, 발행 전, 발행 지연)
- 시간 기반 상태 분석
- 데이터 유효성 검증

작성자: AI Assistant
복원 일시: 2025-08-12
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging


class APIDataParser:
    """
    API 응답 데이터 파싱 및 검증 클래스
    
    INFOMAX API에서 받은 뉴스 데이터를 파싱하고 상태를 판단합니다.
    """
    
    def __init__(self):
        """파서 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 뉴스 타입별 설정 (정상 커밋에서 추출)
        self.news_types_config = {
            'newyork-market-watch': {
                'display_name': '뉴욕마켓워치',
                'emoji': '🌆',
                'expected_publish_time': '060000',
                'expected_time_range': {'start': '060000', 'end': '070000'},
                'delay_check_times': ['073000', '080000', '083000'],
                'tolerance_minutes': 60,
                'time_format': '5digit'
            },
            'kospi-close': {
                'display_name': '증시마감',
                'emoji': '📈',
                'expected_publish_time': '154000',
                'expected_time_range': {'start': '153000', 'end': '155000'},
                'delay_check_times': ['160000', '163000', '170000'],
                'tolerance_minutes': 10,
                'time_format': '6digit'
            },
            'exchange-rate': {
                'display_name': '서환마감',
                'emoji': '💱',
                'expected_publish_time': '163000',
                'expected_time_range': {'start': '162500', 'end': '163500'},
                'delay_check_times': ['170000', '173000', '180000'],
                'tolerance_minutes': 5,
                'time_format': '6digit'
            }
        }
    
    def parse_news_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        원시 API 응답 데이터를 파싱
        
        Args:
            raw_data (dict): API에서 받은 원시 데이터
        
        Returns:
            dict: 파싱된 뉴스 데이터
        """
        parsed_data = {}
        
        for news_type, news_data in raw_data.items():
            if news_type in self.news_types_config:
                parsed_item = self._parse_single_news_item(news_type, news_data)
                if parsed_item:
                    parsed_data[news_type] = parsed_item
                    
        self.logger.info(f"뉴스 데이터 파싱 완료: {len(parsed_data)}개 타입")
        return parsed_data
    
    def _parse_single_news_item(self, news_type: str, news_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        개별 뉴스 아이템 파싱
        
        Args:
            news_type (str): 뉴스 타입
            news_data (dict): 뉴스 데이터
        
        Returns:
            dict: 파싱된 뉴스 아이템
        """
        if not news_data or not isinstance(news_data, dict):
            return None
        
        try:
            parsed_item = {
                'news_type': news_type,
                'title': news_data.get('title', ''),
                'content': news_data.get('content', ''),
                'date': news_data.get('date', ''),
                'time': news_data.get('time', ''),
                'raw_data': news_data
            }
            
            # 상태 판단
            status_info = self._determine_news_status(news_type, parsed_item)
            parsed_item.update(status_info)
            
            return parsed_item
            
        except Exception as e:
            self.logger.error(f"뉴스 아이템 파싱 오류 ({news_type}): {e}")
            return None
    
    def _determine_news_status(self, news_type: str, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        뉴스 상태 판단 (최신, 발행 전, 발행 지연)
        
        Args:
            news_type (str): 뉴스 타입
            news_item (dict): 뉴스 아이템
        
        Returns:
            dict: 상태 정보
        """
        config = self.news_types_config.get(news_type, {})
        
        # 기본 상태 정보
        status_info = {
            'status': 'unknown',
            'status_description': '상태 불명',
            'is_latest': False,
            'is_delayed': False,
            'delay_minutes': 0,
            'expected_time': config.get('expected_publish_time', ''),
            'display_name': config.get('display_name', news_type.upper()),
            'emoji': config.get('emoji', '📰')
        }
        
        # 날짜/시간 정보가 없으면 상태 판단 불가
        if not news_item.get('date') or not news_item.get('time'):
            status_info['status'] = 'no_data'
            status_info['status_description'] = '데이터 없음'
            return status_info
        
        try:
            # 뉴스 발행 시간
            news_datetime = self._parse_datetime(news_item['date'], news_item['time'])
            if not news_datetime:
                status_info['status'] = 'invalid_time'
                status_info['status_description'] = '시간 정보 오류'
                return status_info
            
            # 현재 시간
            now = datetime.now()
            today_str = now.strftime('%Y%m%d')
            
            # 오늘 뉴스인지 확인
            if news_item['date'] == today_str:
                # 오늘 뉴스 - 발행 시간 기준으로 상태 판단
                status_info.update(self._analyze_today_news_status(news_type, news_datetime, now))
            elif news_item['date'] < today_str:
                # 과거 뉴스
                days_ago = (now.date() - news_datetime.date()).days
                status_info['status'] = 'old'
                status_info['status_description'] = f'{days_ago}일 전 뉴스'
                status_info['is_latest'] = False
            else:
                # 미래 뉴스 (시스템 시간 오류?)
                status_info['status'] = 'future'
                status_info['status_description'] = '미래 뉴스 (시간 오류?)'
                status_info['is_latest'] = False
            
            return status_info
            
        except Exception as e:
            self.logger.error(f"뉴스 상태 판단 오류 ({news_type}): {e}")
            status_info['status'] = 'error'
            status_info['status_description'] = f'상태 판단 오류: {str(e)}'
            return status_info
    
    def _analyze_today_news_status(self, news_type: str, news_datetime: datetime, now: datetime) -> Dict[str, Any]:
        """
        오늘 뉴스의 상태 분석
        
        Args:
            news_type (str): 뉴스 타입
            news_datetime (datetime): 뉴스 발행 시간
            now (datetime): 현재 시간
        
        Returns:
            dict: 상태 분석 결과
        """
        config = self.news_types_config.get(news_type, {})
        
        # 예상 발행 시간
        expected_time_str = config.get('expected_publish_time', '120000')
        expected_time = self._parse_time_string(expected_time_str)
        
        if not expected_time:
            return {
                'status': 'latest',
                'status_description': '최신',
                'is_latest': True,
                'is_delayed': False,
                'delay_minutes': 0
            }
        
        # 예상 발행 시간을 오늘 날짜로 변환
        expected_datetime = datetime.combine(now.date(), expected_time)
        
        # 허용 오차 (분)
        tolerance_minutes = config.get('tolerance_minutes', 30)
        
        # 시간 차이 계산
        time_diff = (news_datetime - expected_datetime).total_seconds() / 60
        
        if abs(time_diff) <= tolerance_minutes:
            # 정시 발행
            return {
                'status': 'latest',
                'status_description': '최신 (정시 발행)',
                'is_latest': True,
                'is_delayed': False,
                'delay_minutes': 0
            }
        elif time_diff > tolerance_minutes:
            # 지연 발행
            delay_minutes = int(time_diff)
            return {
                'status': 'delayed',
                'status_description': f'지연 발행 ({delay_minutes}분 지연)',
                'is_latest': True,
                'is_delayed': True,
                'delay_minutes': delay_minutes
            }
        else:
            # 조기 발행 (드문 경우)
            early_minutes = int(abs(time_diff))
            return {
                'status': 'early',
                'status_description': f'조기 발행 ({early_minutes}분 빠름)',
                'is_latest': True,
                'is_delayed': False,
                'delay_minutes': 0
            }
    
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
            # 날짜 파싱
            if len(date_str) == 8:
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
    
    def _parse_time_string(self, time_str: str) -> Optional[datetime.time]:
        """
        시간 문자열을 time 객체로 변환
        
        Args:
            time_str (str): 시간 문자열 (HHMMSS 또는 HHMM)
        
        Returns:
            time: 변환된 time 객체
        """
        try:
            if len(time_str) == 6:
                # HHMMSS 형식
                return datetime.strptime(time_str, '%H%M%S').time()
            elif len(time_str) == 4:
                # HHMM 형식
                return datetime.strptime(time_str, '%H%M').time()
            elif len(time_str) == 5:
                # HHMM 형식 (앞에 0이 없는 경우)
                return datetime.strptime(time_str.zfill(6), '%H%M%S').time()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"시간 문자열 파싱 오류: {time_str} - {e}")
            return None
    
    def validate_parsed_data(self, parsed_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        파싱된 데이터 유효성 검증
        
        Args:
            parsed_data (dict): 파싱된 뉴스 데이터
        
        Returns:
            tuple: (유효성 여부, 오류 메시지 리스트)
        """
        errors = []
        
        if not isinstance(parsed_data, dict):
            errors.append("파싱된 데이터가 딕셔너리가 아님")
            return False, errors
        
        if not parsed_data:
            errors.append("파싱된 데이터가 비어있음")
            return False, errors
        
        # 각 뉴스 타입별 검증
        for news_type, news_item in parsed_data.items():
            if news_type not in self.news_types_config:
                errors.append(f"알 수 없는 뉴스 타입: {news_type}")
                continue
            
            if not isinstance(news_item, dict):
                errors.append(f"{news_type}: 뉴스 아이템이 딕셔너리가 아님")
                continue
            
            # 필수 필드 검증
            required_fields = ['title', 'date', 'time', 'status']
            for field in required_fields:
                if field not in news_item:
                    errors.append(f"{news_type}: 필수 필드 누락 - {field}")
                elif not news_item[field]:
                    errors.append(f"{news_type}: 필수 필드 값 없음 - {field}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def get_status_summary(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        파싱된 데이터의 상태 요약 생성
        
        Args:
            parsed_data (dict): 파싱된 뉴스 데이터
        
        Returns:
            dict: 상태 요약 정보
        """
        summary = {
            'total_news': len(parsed_data),
            'latest_count': 0,
            'delayed_count': 0,
            'old_count': 0,
            'no_data_count': 0,
            'overall_status': 'unknown',
            'news_status': {}
        }
        
        for news_type, news_item in parsed_data.items():
            status = news_item.get('status', 'unknown')
            summary['news_status'][news_type] = {
                'status': status,
                'description': news_item.get('status_description', ''),
                'is_latest': news_item.get('is_latest', False),
                'is_delayed': news_item.get('is_delayed', False)
            }
            
            # 카운트 업데이트
            if status == 'latest':
                summary['latest_count'] += 1
            elif status == 'delayed':
                summary['delayed_count'] += 1
            elif status == 'old':
                summary['old_count'] += 1
            elif status in ['no_data', 'invalid_time']:
                summary['no_data_count'] += 1
        
        # 전체 상태 판단
        if summary['latest_count'] == summary['total_news']:
            summary['overall_status'] = 'all_latest'
        elif summary['latest_count'] > 0:
            summary['overall_status'] = 'partial_latest'
        elif summary['delayed_count'] > 0:
            summary['overall_status'] = 'has_delayed'
        else:
            summary['overall_status'] = 'all_old'
        
        return summary


if __name__ == "__main__":
    # 테스트 코드
    import json
    
    # 샘플 데이터
    sample_data = {
        'newyork-market-watch': {
            'title': '뉴욕마켓워치 테스트',
            'content': '테스트 내용',
            'date': '20250812',
            'time': '060500'
        },
        'kospi-close': {
            'title': '증시마감 테스트',
            'content': '테스트 내용',
            'date': '20250812',
            'time': '154500'
        }
    }
    
    parser = APIDataParser()
    
    print("=== API 데이터 파서 테스트 ===")
    print("원시 데이터:")
    print(json.dumps(sample_data, indent=2, ensure_ascii=False))
    print()
    
    # 데이터 파싱
    parsed_data = parser.parse_news_data(sample_data)
    print("파싱된 데이터:")
    print(json.dumps(parsed_data, indent=2, ensure_ascii=False, default=str))
    print()
    
    # 유효성 검증
    is_valid, errors = parser.validate_parsed_data(parsed_data)
    print(f"유효성 검증: {'✅ 통과' if is_valid else '❌ 실패'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    print()
    
    # 상태 요약
    summary = parser.get_status_summary(parsed_data)
    print("상태 요약:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))