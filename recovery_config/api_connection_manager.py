# -*- coding: utf-8 -*-
"""
API 연결 관리자

INFOMAX API 연결 상태를 관리하고 연결 실패 시 재시도 메커니즘을 제공합니다.

주요 기능:
- 연결 상태 모니터링
- 지능형 재시도 메커니즘 (백오프 전략)
- 연결 풀 관리
- 성능 메트릭 수집
- 장애 감지 및 복구

작성자: AI Assistant
복원 일시: 2025-08-12
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
import logging
from dataclasses import dataclass, field
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ConnectionStatus(Enum):
    """연결 상태 열거형"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ConnectionMetrics:
    """연결 메트릭 데이터 클래스"""
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


class APIConnectionManager:
    """
    API 연결 관리자 클래스
    
    INFOMAX API와의 연결을 관리하고 장애 상황에서 자동 복구를 수행합니다.
    """
    
    def __init__(self, api_client, config: Optional[Dict[str, Any]] = None):
        """
        연결 관리자 초기화
        
        Args:
            api_client: API 클라이언트 인스턴스
            config (dict, optional): 연결 관리 설정
        """
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # 기본 설정
        default_config = {
            'max_retries': 5,
            'base_delay': 1.0,
            'max_delay': 60.0,
            'backoff_factor': 2.0,
            'health_check_interval': 300,  # 5분
            'failure_threshold': 3,
            'recovery_threshold': 2,
            'timeout': 30,
            'pool_connections': 10,
            'pool_maxsize': 20
        }
        
        self.config = {**default_config, **(config or {})}
        
        # 상태 관리
        self.status = ConnectionStatus.UNKNOWN
        self.metrics = ConnectionMetrics()
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.RLock()
        
        # 콜백 함수들
        self.on_status_change: Optional[Callable[[ConnectionStatus, ConnectionStatus], None]] = None
        self.on_failure: Optional[Callable[[Exception], None]] = None
        self.on_recovery: Optional[Callable[[], None]] = None
        
        # HTTP 세션 설정
        self._setup_session()
        
        self.logger.info("API 연결 관리자 초기화 완료")
    
    def _setup_session(self):
        """HTTP 세션 설정"""
        self.session = requests.Session()
        
        # 재시도 전략 설정
        retry_strategy = Retry(
            total=self.config['max_retries'],
            backoff_factor=self.config['backoff_factor'],
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.config['pool_connections'],
            pool_maxsize=self.config['pool_maxsize']
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 기본 타임아웃 설정
        self.session.timeout = self.config['timeout']
    
    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """
        재시도 메커니즘을 적용하여 작업 실행
        
        Args:
            operation (callable): 실행할 작업 함수
            *args: 작업 함수의 위치 인자
            **kwargs: 작업 함수의 키워드 인자
        
        Returns:
            Any: 작업 실행 결과
        
        Raises:
            Exception: 모든 재시도 실패 시 마지막 예외
        """
        max_retries = self.config['max_retries']
        base_delay = self.config['base_delay']
        max_delay = self.config['max_delay']
        backoff_factor = self.config['backoff_factor']
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # 작업 실행
                result = operation(*args, **kwargs)
                
                # 성공 메트릭 업데이트
                response_time = time.time() - start_time
                self._update_success_metrics(response_time)
                
                return result
                
            except Exception as e:
                last_exception = e
                self._update_failure_metrics(e)
                
                if attempt < max_retries:
                    # 지수 백오프 계산
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    
                    self.logger.warning(
                        f"API 호출 실패 (시도 {attempt + 1}/{max_retries + 1}): {e}. "
                        f"{delay:.1f}초 후 재시도..."
                    )
                    
                    time.sleep(delay)
                else:
                    self.logger.error(f"API 호출 최종 실패: {e}")
        
        # 모든 재시도 실패
        if last_exception:
            raise last_exception
    
    def _update_success_metrics(self, response_time: float):
        """성공 메트릭 업데이트"""
        with self.lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.total_response_time += response_time
            self.metrics.last_request_time = datetime.now()
            self.metrics.last_success_time = datetime.now()
            self.metrics.consecutive_failures = 0
            self.metrics.consecutive_successes += 1
            
            # 상태 업데이트
            old_status = self.status
            if self.metrics.consecutive_successes >= self.config['recovery_threshold']:
                self.status = ConnectionStatus.HEALTHY
            
            if old_status != self.status:
                self._notify_status_change(old_status, self.status)
    
    def _update_failure_metrics(self, exception: Exception):
        """실패 메트릭 업데이트"""
        with self.lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.last_request_time = datetime.now()
            self.metrics.last_failure_time = datetime.now()
            self.metrics.consecutive_successes = 0
            self.metrics.consecutive_failures += 1
            
            # 상태 업데이트
            old_status = self.status
            if self.metrics.consecutive_failures >= self.config['failure_threshold']:
                self.status = ConnectionStatus.FAILED
            elif self.metrics.consecutive_failures > 0:
                self.status = ConnectionStatus.DEGRADED
            
            if old_status != self.status:
                self._notify_status_change(old_status, self.status)
                
                # 실패 콜백 호출
                if self.on_failure:
                    try:
                        self.on_failure(exception)
                    except Exception as e:
                        self.logger.error(f"실패 콜백 오류: {e}")
    
    def _notify_status_change(self, old_status: ConnectionStatus, new_status: ConnectionStatus):
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
    
    def start_monitoring(self):
        """연결 상태 모니터링 시작"""
        if self.is_monitoring:
            self.logger.warning("이미 모니터링이 실행 중입니다")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("연결 상태 모니터링 시작")
    
    def stop_monitoring(self):
        """연결 상태 모니터링 중지"""
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("연결 상태 모니터링 중지")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        interval = self.config['health_check_interval']
        
        while self.is_monitoring:
            try:
                # 헬스 체크 수행
                self._perform_health_check()
                
                # 다음 체크까지 대기
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(min(interval, 60))  # 오류 시 최대 1분 대기
    
    def _perform_health_check(self):
        """헬스 체크 수행"""
        try:
            # API 클라이언트의 연결 테스트 메서드 호출
            if hasattr(self.api_client, 'test_connection'):
                is_healthy = self.api_client.test_connection()
            else:
                # 기본 헬스 체크 (간단한 API 호출)
                result = self.api_client.get_news_data()
                is_healthy = result is not None
            
            if is_healthy:
                self._update_success_metrics(0.1)  # 헬스 체크는 빠른 응답으로 가정
            else:
                raise Exception("헬스 체크 실패")
                
        except Exception as e:
            self._update_failure_metrics(e)
    
    def get_status(self) -> Dict[str, Any]:
        """현재 연결 상태 정보 반환"""
        with self.lock:
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
                'config': self.config
            }
    
    def reset_metrics(self):
        """메트릭 초기화"""
        with self.lock:
            self.metrics = ConnectionMetrics()
            self.status = ConnectionStatus.UNKNOWN
            self.logger.info("연결 메트릭 초기화 완료")
    
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
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.stop_monitoring()


if __name__ == "__main__":
    # 테스트 코드
    import sys
    import os
    
    # 설정 로드
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    try:
        from recovery_config.infomax_api_client import InfomaxAPIClient
        from recovery_config.environment_settings import load_environment_settings
        
        settings = load_environment_settings()
        api_config = settings.get('API_CONFIG', {})
        
        if api_config:
            # API 클라이언트 생성
            client = InfomaxAPIClient(api_config)
            
            # 연결 관리자 생성
            manager = APIConnectionManager(client)
            
            # 콜백 함수 설정
            def on_status_change(old_status, new_status):
                print(f"🔄 상태 변경: {old_status.value} → {new_status.value}")
            
            def on_failure(exception):
                print(f"❌ 연결 실패: {exception}")
            
            def on_recovery():
                print("✅ 연결 복구됨")
            
            manager.on_status_change = on_status_change
            manager.on_failure = on_failure
            manager.on_recovery = on_recovery
            
            print("=== API 연결 관리자 테스트 ===")
            
            # 재시도 메커니즘 테스트
            print("1. 재시도 메커니즘 테스트...")
            try:
                result = manager.execute_with_retry(client.get_news_data)
                if result:
                    print("✅ API 호출 성공")
                else:
                    print("❌ API 호출 실패 (데이터 없음)")
            except Exception as e:
                print(f"❌ API 호출 최종 실패: {e}")
            
            # 상태 정보 출력
            print("\n2. 연결 상태 정보:")
            status_info = manager.get_status()
            print(f"  상태: {status_info['status']}")
            print(f"  성공률: {status_info['metrics']['success_rate']:.2%}")
            print(f"  총 요청: {status_info['metrics']['total_requests']}")
            print(f"  권장 조치: {manager.get_recommended_action()}")
            
            # 모니터링 테스트 (짧은 시간)
            print("\n3. 모니터링 테스트 (10초)...")
            manager.start_monitoring()
            time.sleep(10)
            manager.stop_monitoring()
            
            print("테스트 완료")
        else:
            print("❌ API 설정을 찾을 수 없습니다.")
            
    except ImportError as e:
        print(f"❌ 모듈 로드 실패: {e}")
        print("필요한 모듈이 없어 테스트를 진행할 수 없습니다.")