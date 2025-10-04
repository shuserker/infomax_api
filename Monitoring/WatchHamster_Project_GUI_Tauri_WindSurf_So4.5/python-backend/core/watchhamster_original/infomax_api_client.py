# -*- coding: utf-8 -*-
"""
INFOMAX API 연동 모듈 복원

정상 커밋 a763ef84의 PoscoNewsAPIClient를 기반으로 복원된 API 연동 모듈입니다.

주요 기능:
- INFOMAX API 호출 및 응답 처리
- 연결 실패 시 재시도 메커니즘
- API 응답 데이터 검증 및 파싱
- 인증 및 타임아웃 처리

작성자: AI Assistant
복원 일시: 2025-08-12
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, Any


class InfomaxAPIClient:
    """
    INFOMAX API 클라이언트 클래스
    
    POSCO 뉴스 API와의 통신을 담당하며, 인증, 요청, 응답 처리를 수행합니다.
    
    주요 기능:
    - API 인증 (Basic Auth)
    - 뉴스 데이터 조회
    - 연결 상태 테스트
    - 오류 처리 및 재시도
    
    Attributes:
        api_url (str): API 엔드포인트 URL
        api_user (str): API 사용자명
        api_pwd (str): API 비밀번호
        api_timeout (int): 요청 타임아웃 (초)
        max_retries (int): 최대 재시도 횟수
        retry_delay (float): 재시도 간격 (초)
    """
    
    def __init__(self, api_config: Dict[str, Any]):
        """
        API 클라이언트 초기화
        
        Args:
            api_config (dict): API 설정 정보
                - url (str): API 엔드포인트 URL
                - user (str): API 사용자명
                - password (str): API 비밀번호
                - timeout (int): 요청 타임아웃 (초)
        """
        self.api_url = api_config["url"]
        self.api_user = api_config["user"]
        self.api_pwd = api_config["password"]
        self.api_timeout = api_config.get("timeout", 10)
        self.max_retries = api_config.get("max_retries", 3)
        self.retry_delay = api_config.get("retry_delay", 1.0)
        
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        
    def get_news_data(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        POSCO 뉴스 API에서 데이터 조회
        
        지정된 날짜의 뉴스 데이터를 조회합니다. 날짜가 지정되지 않으면
        최신 데이터를 조회합니다.
        
        Args:
            date (str, optional): 조회할 날짜 (YYYYMMDD 형식)
                                 None이면 최신 데이터 조회
        
        Returns:
            dict: 뉴스 타입별 데이터 딕셔너리
                  {
                      "exchange-rate": {"date": "20250728", "time": "090000", "title": "..."},
                      "newyork-market-watch": {...},
                      "kospi-close": {...}
                  }
                  API 호출 실패 시 None 반환
        
        Raises:
            requests.exceptions.Timeout: 요청 타임아웃
            requests.exceptions.ConnectionError: 연결 오류
            requests.exceptions.HTTPError: HTTP 오류
        """
        for attempt in range(self.max_retries):
            try:
                params = {}
                if date:
                    params['date'] = date
                    
                self.logger.info(f"API 호출 시도 {attempt + 1}/{self.max_retries}: {self.api_url}")
                
                resp = requests.get(
                    self.api_url,
                    auth=HTTPBasicAuth(self.api_user, self.api_pwd),
                    params=params,
                    timeout=self.api_timeout
                )
                resp.raise_for_status()
                
                # 응답 데이터 검증
                data = resp.json()
                if self._validate_response_data(data):
                    self.logger.info("API 호출 성공")
                    return data
                else:
                    self.logger.warning("API 응답 데이터 검증 실패")
                    return None
                    
            except requests.exceptions.Timeout:
                self.logger.error(f"API 호출 타임아웃: {self.api_timeout}초 초과 (시도 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
                
            except requests.exceptions.ConnectionError:
                self.logger.error(f"API 연결 오류: {self.api_url} (시도 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
                
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"API HTTP 오류: {e.response.status_code} (시도 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
                
            except json.JSONDecodeError as e:
                self.logger.error(f"API 응답 JSON 파싱 오류: {e} (시도 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
                
            except Exception as e:
                self.logger.error(f"API 호출 예상치 못한 오류: {e} (시도 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
        
        self.logger.error(f"API 호출 최종 실패: {self.max_retries}회 시도 후 포기")
        return None
    
    def test_connection(self) -> bool:
        """
        API 연결 상태 테스트
        
        API 서버와의 연결 상태를 확인합니다.
        
        Returns:
            bool: 연결 성공 시 True, 실패 시 False
        """
        try:
            self.logger.info("API 연결 테스트 시작")
            
            resp = requests.get(
                self.api_url,
                auth=HTTPBasicAuth(self.api_user, self.api_pwd),
                timeout=5
            )
            
            success = resp.status_code == 200
            if success:
                self.logger.info("API 연결 테스트 성공")
            else:
                self.logger.warning(f"API 연결 테스트 실패: HTTP {resp.status_code}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"API 연결 테스트 오류: {e}")
            return False
    
    def get_historical_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        기간별 과거 데이터 조회
        
        Args:
            start_date (str): 시작 날짜 (YYYYMMDD)
            end_date (str): 종료 날짜 (YYYYMMDD)
        
        Returns:
            dict: 날짜별 뉴스 데이터
        """
        historical_data = {}
        
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y%m%d')
            
            # 주말 제외 (영업일만)
            if current_dt.weekday() < 5:  # 0=월요일, 4=금요일
                data = self.get_news_data(date_str)
                if data:
                    historical_data[date_str] = data
                    self.logger.info(f"과거 데이터 조회 성공: {date_str}")
                else:
                    self.logger.warning(f"과거 데이터 조회 실패: {date_str}")
                
                # API 부하 방지를 위한 지연
                time.sleep(0.5)
            
            current_dt += timedelta(days=1)
        
        self.logger.info(f"과거 데이터 조회 완료: {len(historical_data)}일치 데이터")
        return historical_data
    
    def _validate_response_data(self, data: Any) -> bool:
        """
        API 응답 데이터 검증
        
        Args:
            data: API 응답 데이터
        
        Returns:
            bool: 유효한 데이터인지 여부
        """
        if not isinstance(data, dict):
            self.logger.warning("응답 데이터가 딕셔너리가 아님")
            return False
        
        # 예상되는 뉴스 타입들
        expected_types = ['newyork-market-watch', 'kospi-close', 'exchange-rate']
        
        # 최소 하나의 뉴스 타입이 있는지 확인
        has_valid_type = False
        for news_type in expected_types:
            if news_type in data:
                news_data = data[news_type]
                if isinstance(news_data, dict) and news_data.get('title'):
                    has_valid_type = True
                    break
        
        if not has_valid_type:
            self.logger.warning("유효한 뉴스 데이터가 없음")
            return False
        
        return True
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        연결 정보 반환
        
        Returns:
            dict: 연결 설정 정보 (비밀번호 제외)
        """
        return {
            'api_url': self.api_url,
            'api_user': self.api_user,
            'api_timeout': self.api_timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }


# 하위 호환성을 위한 별칭
PoscoNewsAPIClient = InfomaxAPIClient


if __name__ == "__main__":
    # 테스트 코드
    import sys
    import os
    
    # 설정 로드
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    try:
        # 설정 파일은 recovery_config에서 로드 (공통 설정)
        from recovery_config.environment_settings import load_environment_settings
        settings = load_environment_settings()
        api_config = settings.get('API_CONFIG', {})
        
        if api_config:
            client = InfomaxAPIClient(api_config)
            
            print("=== INFOMAX API 클라이언트 테스트 ===")
            print(f"API URL: {client.api_url}")
            print(f"사용자: {client.api_user}")
            print(f"타임아웃: {client.api_timeout}초")
            print()
            
            # 연결 테스트
            print("1. 연결 테스트...")
            if client.test_connection():
                print("✅ 연결 성공")
            else:
                print("❌ 연결 실패")
            print()
            
            # 데이터 조회 테스트
            print("2. 최신 데이터 조회...")
            data = client.get_news_data()
            if data:
                print("✅ 데이터 조회 성공")
                for news_type, news_data in data.items():
                    if news_data and news_data.get('title'):
                        print(f"  - {news_type}: {news_data.get('title', 'N/A')}")
            else:
                print("❌ 데이터 조회 실패")
        else:
            print("❌ API 설정을 찾을 수 없습니다.")
            
    except ImportError as e:
        print(f"❌ 설정 로드 실패: {e}")
        print("기본 설정으로 테스트를 진행할 수 없습니다.")