# -*- coding: utf-8 -*-
"""
POSCO 뉴스 API 클라이언트
"""

import requests
from requests.auth import HTTPBasicAuth


class PoscoNewsAPIClient:
    """
    POSCO 뉴스 API 클라이언트 클래스
    
    API 호출, 인증, 에러 처리를 담당합니다.
    """
    
    def __init__(self, api_config):
        """
        API 클라이언트 초기화
        
        Args:
            api_config (dict): API 설정 정보
        """
        self.api_url = api_config["url"]
        self.api_user = api_config["user"]
        self.api_pwd = api_config["password"]
        self.api_timeout = api_config["timeout"]
    
    def get_news_data(self, date=None):
        """
        POSCO 뉴스 API에서 데이터 조회
        
        Args:
            date (str, optional): 조회할 날짜 (YYYYMMDD 형식)
                                 None이면 최신 데이터 조회
        
        Returns:
            dict: 뉴스 타입별 데이터 딕셔너리
                  API 호출 실패 시 None 반환
        """
        try:
            params = {}
            if date:
                params['date'] = date
                
            resp = requests.get(
                self.api_url,
                auth=HTTPBasicAuth(self.api_user, self.api_pwd),
                params=params,
                timeout=self.api_timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            print(f"❌ API 호출 타임아웃: {self.api_timeout}초 초과")
            return None
        except requests.exceptions.ConnectionError:
            print(f"❌ API 연결 오류: {self.api_url}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ API HTTP 오류: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"❌ API 호출 오류: {e}")
            return None
    
    def test_connection(self):
        """
        API 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            resp = requests.get(
                self.api_url,
                auth=HTTPBasicAuth(self.api_user, self.api_pwd),
                timeout=5
            )
            return resp.status_code == 200
        except:
            return False