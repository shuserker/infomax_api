# -*- coding: utf-8 -*-
"""
INFOMAX API 클라이언트 모듈

기존 WatchHamster_Project의 infomax_api_client.py와 api_connection_manager.py를 
통합하여 비동기 처리 및 연결 풀 관리를 지원하는 모던한 API 클라이언트입니다.

주요 기능:
- 비동기 API 호출 및 응답 처리
- 지능형 재시도 메커니즘 (지수 백오프)
- 연결 풀 관리 및 성능 최적화
- API 상태 체크 및 헬스 모니터링
- 실시간 메트릭 수집 및 상태 관리

작성자: AI Assistant
작성 일시: 2025-01-02
기반: WatchHamster_Project/core/infomax_api_client.py, api_connection_manager.py
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable, List
import logging
from dataclasses import dataclass, field
from enum import Enum
import ssl
from urllib.parse import urljoin


class ConnectionStatus(Enum):
    """연결 상태 열거형"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class APIMetrics:
    """API 메트릭 데이터 클래스"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    @property
    def success_rate(self) -> float:
        """성공률 계산"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_response_time(self) -> float:
        """평균 응답 시간 계산"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests


class InfomaxAPIClient:
    """
    INFOMAX API 클라이언트 클래스
    
    비동기 HTTP 클라이언트를 사용하여 POSCO 뉴스 API와 통신하며,
    연결 관리, 재시도 메커니즘, 성능 모니터링을 제공합니다.
    """
    
    def __init__(self, base_url: str = "https://global-api.einfomax.co.kr/apis/posco/news", 
                 user: str = "", password: str = "", **kwargs):
        """
        API 클라이언트 초기화
        
        Args:
            config (dict): API 설정 정보
                - url (str): API 엔드포인트 URL
                - user (str): API 사용자명  
                - password (str): API 비밀번호
                - timeout (int): 요청 타임아웃 (초)
                - max_retries (int): 최대 재시도 횟수
                - retry_delay (float): 재시도 기본 지연 시간
                - max_delay (float): 최대 지연 시간
                - backoff_factor (float): 백오프 배수
                - pool_size (int): 연결 풀 크기
        """
        # 기본 설정
        self.api_url = base_url
        self.api_user = user
        self.api_password = password
        self.timeout = kwargs.get("timeout", 30)
        self.max_retries = kwargs.get("max_retries", 5)
        self.retry_delay = kwargs.get("retry_delay", 1.0)
        self.max_delay = kwargs.get("max_delay", 60.0)
        self.backoff_factor = kwargs.get("backoff_factor", 2.0)
        self.pool_size = kwargs.get("pool_size", 10)
        
        # 상태 관리
        self.status = ConnectionStatus.UNKNOWN
        self.metrics = APIMetrics()
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
        
        # 콜백 함수들
        self.on_status_change: Optional[Callable[[ConnectionStatus, ConnectionStatus], None]] = None
        self.on_failure: Optional[Callable[[Exception], None]] = None
        self.on_recovery: Optional[Callable[[], None]] = None
        
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("INFOMAX API 클라이언트 초기화 완료")
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self._close_session()
    
    async def _create_session(self):
        """HTTP 세션 생성"""
        if self.session and not self.session.closed:
            return
        
        # SSL 컨텍스트 설정
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 연결 설정
        connector = aiohttp.TCPConnector(
            limit=self.pool_size,
            limit_per_host=self.pool_size,
            ssl=ssl_context,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        # 타임아웃 설정
        timeout = aiohttp.ClientTimeout(
            total=self.timeout,
            connect=10,
            sock_read=self.timeout
        )
        
        # 기본 인증 설정
        auth = aiohttp.BasicAuth(self.api_user, self.api_password)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            auth=auth,
            headers={
                'User-Agent': 'WatchHamster-Tauri/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        
        self.logger.info("HTTP 세션 생성 완료")
    
    async def _close_session(self):
        """HTTP 세션 종료"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("HTTP 세션 종료 완료")
    
    async def fetch_news_data(self, news_type: Optional[str] = None, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        뉴스 데이터 비동기 조회
        
        Args:
            news_type (str, optional): 뉴스 타입 ('exchange-rate', 'newyork-market-watch', 'kospi-close')
            date (str, optional): 조회할 날짜 (YYYYMMDD 형식)
        
        Returns:
            dict: 뉴스 데이터 또는 None (실패 시)
        """
        if not self.session:
            await self._create_session()
        
        return await self._execute_with_retry(self._fetch_news_data_internal, news_type, date)
    
    async def _fetch_news_data_internal(self, news_type: Optional[str] = None, date: Optional[str] = None) -> Dict[str, Any]:
        """내부 뉴스 데이터 조회 메서드"""
        params = {}
        if date:
            params['date'] = date
        if news_type:
            params['type'] = news_type
        
        start_time = time.time()
        
        async with self.session.get(self.api_url, params=params) as response:
            response.raise_for_status()
            
            data = await response.json()
            
            # 응답 데이터 검증
            if not self._validate_response_data(data):
                raise ValueError("유효하지 않은 응답 데이터")
            
            response_time = time.time() - start_time
            await self._update_success_metrics(response_time)
            
            return data
    
    async def health_check(self) -> bool:
        """
        API 연결 상태 확인
        
        Returns:
            bool: 연결 성공 시 True, 실패 시 False
        """
        try:
            if not self.session:
                await self._create_session()
            
            self.logger.info("API 헬스 체크 시작")
            
            start_time = time.time()
            async with self.session.get(self.api_url, params={'health': 'check'}) as response:
                success = response.status == 200
                
                if success:
                    response_time = time.time() - start_time
                    await self._update_success_metrics(response_time)
                    self.logger.info("API 헬스 체크 성공")
                else:
                    await self._update_failure_metrics(Exception(f"HTTP {response.status}"))
                    self.logger.warning(f"API 헬스 체크 실패: HTTP {response.status}")
                
                return success
                
        except Exception as e:
            await self._update_failure_metrics(e)
            self.logger.error(f"API 헬스 체크 오류: {e}")
            return False
    
    async def get_historical_data(self, start_date: str, end_date: str, news_type: Optional[str] = None) -> Dict[str, Any]:
        """
        기간별 과거 데이터 조회
        
        Args:
            start_date (str): 시작 날짜 (YYYYMMDD)
            end_date (str): 종료 날짜 (YYYYMMDD)
            news_type (str, optional): 뉴스 타입
        
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
                try:
                    data = await self.fetch_news_data(news_type, date_str)
                    if data:
                        historical_data[date_str] = data
                        self.logger.info(f"과거 데이터 조회 성공: {date_str}")
                    else:
                        self.logger.warning(f"과거 데이터 조회 실패: {date_str}")
                    
                    # API 부하 방지를 위한 지연
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"과거 데이터 조회 오류 ({date_str}): {e}")
            
            current_dt += timedelta(days=1)
        
        self.logger.info(f"과거 데이터 조회 완료: {len(historical_data)}일치 데이터")
        return historical_data
    
    async def _execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """
        재시도 메커니즘을 적용하여 작업 실행
        
        Args:
            operation (callable): 실행할 비동기 작업 함수
            *args: 작업 함수의 위치 인자
            **kwargs: 작업 함수의 키워드 인자
        
        Returns:
            Any: 작업 실행 결과
        
        Raises:
            Exception: 모든 재시도 실패 시 마지막 예외
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await operation(*args, **kwargs)
                return result
                
            except Exception as e:
                last_exception = e
                await self._update_failure_metrics(e)
                
                if attempt < self.max_retries:
                    # 지수 백오프 계산
                    delay = min(self.retry_delay * (self.backoff_factor ** attempt), self.max_delay)
                    
                    self.logger.warning(
                        f"API 호출 실패 (시도 {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"{delay:.1f}초 후 재시도..."
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"API 호출 최종 실패: {e}")
        
        # 모든 재시도 실패
        if last_exception:
            raise last_exception
    
    async def _update_success_metrics(self, response_time: float):
        """성공 메트릭 업데이트"""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.total_response_time += response_time
            self.metrics.last_request_time = datetime.now()
            self.metrics.last_success_time = datetime.now()
            self.metrics.consecutive_failures = 0
            self.metrics.consecutive_successes += 1
            
            # 상태 업데이트
            old_status = self.status
            if self.metrics.consecutive_successes >= 2:  # 연속 2회 성공 시 건강 상태
                self.status = ConnectionStatus.HEALTHY
            
            if old_status != self.status:
                await self._notify_status_change(old_status, self.status)
    
    async def _update_failure_metrics(self, exception: Exception):
        """실패 메트릭 업데이트"""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.last_request_time = datetime.now()
            self.metrics.last_failure_time = datetime.now()
            self.metrics.consecutive_successes = 0
            self.metrics.consecutive_failures += 1
            
            # 상태 업데이트
            old_status = self.status
            if self.metrics.consecutive_failures >= 3:  # 연속 3회 실패 시 실패 상태
                self.status = ConnectionStatus.FAILED
            elif self.metrics.consecutive_failures > 0:
                self.status = ConnectionStatus.DEGRADED
            
            if old_status != self.status:
                await self._notify_status_change(old_status, self.status)
                
                # 실패 콜백 호출
                if self.on_failure:
                    try:
                        self.on_failure(exception)
                    except Exception as e:
                        self.logger.error(f"실패 콜백 오류: {e}")
    
    async def _notify_status_change(self, old_status: ConnectionStatus, new_status: ConnectionStatus):
        """상태 변경 알림"""
        self.logger.info(f"연결 상태 변경: {old_status.value} → {new_status.value}")
        
        if self.on_status_change:
            try:
                self.on_status_change(old_status, new_status)
            except Exception as e:
                self.logger.error(f"상태 변경 콜백 오류: {e}")
        
        # 복구 콜백 호출
        if old_status == ConnectionStatus.FAILED and new_status in [ConnectionStatus.HEALTHY, ConnectionStatus.DEGRADED]:
            if self.on_recovery:
                try:
                    self.on_recovery()
                except Exception as e:
                    self.logger.error(f"복구 콜백 오류: {e}")
    
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
    
    def get_status(self) -> Dict[str, Any]:
        """현재 연결 상태 정보 반환"""
        return {
            'status': self.status.value,
            'metrics': {
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'success_rate': self.metrics.success_rate,
                'average_response_time': self.metrics.average_response_time,
                'consecutive_failures': self.metrics.consecutive_failures,
                'consecutive_successes': self.metrics.consecutive_successes,
                'last_request_time': self.metrics.last_request_time.isoformat() if self.metrics.last_request_time else None,
                'last_success_time': self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None,
                'last_failure_time': self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None
            },
            'config': {
                'api_url': self.api_url,
                'api_user': self.api_user,
                'timeout': self.timeout,
                'max_retries': self.max_retries,
                'retry_delay': self.retry_delay,
                'max_delay': self.max_delay,
                'backoff_factor': self.backoff_factor,
                'pool_size': self.pool_size
            }
        }
    
    def get_connection_info(self) -> Dict[str, Any]:
        """연결 정보 반환 (비밀번호 제외)"""
        return {
            'api_url': self.api_url,
            'api_user': self.api_user,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'max_delay': self.max_delay,
            'backoff_factor': self.backoff_factor,
            'pool_size': self.pool_size
        }
    
    def is_healthy(self) -> bool:
        """연결 상태가 건강한지 확인"""
        return self.status == ConnectionStatus.HEALTHY
    
    def is_available(self) -> bool:
        """연결이 사용 가능한지 확인 (건강하거나 성능 저하 상태)"""
        return self.status in [ConnectionStatus.HEALTHY, ConnectionStatus.DEGRADED]
    
    def get_recommended_action(self) -> str:
        """현재 상태에 따른 권장 조치 반환"""
        if self.status == ConnectionStatus.HEALTHY:
            return "정상 작동 중"
        elif self.status == ConnectionStatus.DEGRADED:
            return "성능 저하 - 모니터링 강화 권장"
        elif self.status == ConnectionStatus.FAILED:
            return "연결 실패 - 즉시 확인 필요"
        else:
            return "상태 불명 - 연결 테스트 필요"


# 하위 호환성을 위한 별칭
PoscoNewsAPIClient = InfomaxAPIClient


async def create_api_client(base_url: str = "https://global-api.einfomax.co.kr/apis/posco/news", 
                           **kwargs) -> InfomaxAPIClient:
    """
    API 클라이언트 팩토리 함수
    
    Args:
        config (dict): API 설정 정보
    
    Returns:
        InfomaxAPIClient: 초기화된 API 클라이언트
    """
    client = InfomaxAPIClient(base_url, **kwargs)
    await client._create_session()
    return client


if __name__ == "__main__":
    # 테스트 코드
    import asyncio
    
    async def test_api_client():
        """API 클라이언트 테스트"""
        # 테스트 설정
        test_config = {
            "url": "https://global-api.einfomax.co.kr/apis/posco/news",
            "user": "test_user",
            "password": "test_password",
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1.0,
            "max_delay": 30.0,
            "backoff_factor": 2.0,
            "pool_size": 5
        }
        
        print("=== INFOMAX API 클라이언트 테스트 ===")
        
        async with InfomaxAPIClient(test_config) as client:
            print(f"API URL: {client.api_url}")
            print(f"사용자: {client.api_user}")
            print(f"타임아웃: {client.timeout}초")
            print()
            
            # 헬스 체크 테스트
            print("1. 헬스 체크 테스트...")
            is_healthy = await client.health_check()
            if is_healthy:
                print("✅ 헬스 체크 성공")
            else:
                print("❌ 헬스 체크 실패")
            print()
            
            # 뉴스 데이터 조회 테스트
            print("2. 뉴스 데이터 조회 테스트...")
            try:
                data = await client.fetch_news_data()
                if data:
                    print("✅ 뉴스 데이터 조회 성공")
                    for news_type, news_data in data.items():
                        if news_data and news_data.get('title'):
                            print(f"  - {news_type}: {news_data.get('title', 'N/A')}")
                else:
                    print("❌ 뉴스 데이터 조회 실패")
            except Exception as e:
                print(f"❌ 뉴스 데이터 조회 오류: {e}")
            print()
            
            # 상태 정보 출력
            print("3. 상태 정보:")
            status_info = client.get_status()
            print(f"  상태: {status_info['status']}")
            print(f"  성공률: {status_info['metrics']['success_rate']:.2%}")
            print(f"  총 요청: {status_info['metrics']['total_requests']}")
            print(f"  권장 조치: {client.get_recommended_action()}")
    
    # 테스트 실행
    asyncio.run(test_api_client())