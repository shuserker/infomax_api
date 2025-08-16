# -*- coding: utf-8 -*-
"""
통합 API 모듈

INFOMAX API 연동의 모든 기능을 통합하여 제공하는 메인 모듈입니다.

주요 기능:
- API 클라이언트 관리
- 데이터 파싱 및 검증
- 연결 관리 및 재시도
- 상태 모니터링
- 캐싱 및 성능 최적화

작성자: AI Assistant
복원 일시: 2025-08-12
기반 커밋: a763ef84be08b5b1dab0c0ba20594b141baec7ab
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
import logging
from pathlib import Path

from recovery_config.infomax_api_client import InfomaxAPIClient
from recovery_config.api_data_parser import APIDataParser
from recovery_config.api_connection_manager import APIConnectionManager, ConnectionStatus


class IntegratedAPIModule:
    """
    통합 API 모듈 클래스
    
    INFOMAX API와의 모든 상호작용을 관리하는 메인 클래스입니다.
    """
    
    def __init__(self, api_config: Dict[str, Any], cache_config: Optional[Dict[str, Any]] = None):
        """
        통합 API 모듈 초기화
        
        Args:
            api_config (dict): API 설정 정보
            cache_config (dict, optional): 캐시 설정 정보
        """
        self.logger = logging.getLogger(__name__)
        
        # 컴포넌트 초기화
        self.api_client = InfomaxAPIClient(api_config)
        self.data_parser = APIDataParser()
        self.connection_manager = APIConnectionManager(self.api_client)
        
        # 캐시 설정
        default_cache_config = {
            'enabled': True,
            'cache_file': 'posco_news_cache.json',
            'cache_duration': 300,  # 5분
            'max_cache_size': 1000
        }
        self.cache_config = {**default_cache_config, **(cache_config or {})}
        
        # 캐시 데이터
        self.cache_data = {}
        self.cache_timestamps = {}
        self.cache_lock = threading.RLock()
        
        # 콜백 함수들
        self.on_data_update: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_connection_issue: Optional[Callable[[str], None]] = None
        self.on_parsing_error: Optional[Callable[[Exception], None]] = None
        
        # 연결 관리자 콜백 설정
        self.connection_manager.on_status_change = self._on_connection_status_change
        self.connection_manager.on_failure = self._on_connection_failure
        self.connection_manager.on_recovery = self._on_connection_recovery
        
        # 캐시 파일 로드
        self._load_cache()
        
        self.logger.info("통합 API 모듈 초기화 완료")
    
    def get_latest_news_data(self, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        최신 뉴스 데이터 조회
        
        Args:
            use_cache (bool): 캐시 사용 여부
        
        Returns:
            dict: 파싱된 뉴스 데이터
        """
        cache_key = 'latest_news'
        
        # 캐시 확인
        if use_cache and self._is_cache_valid(cache_key):
            self.logger.info("캐시에서 최신 뉴스 데이터 반환")
            return self.cache_data.get(cache_key)
        
        try:
            # API에서 데이터 조회
            self.logger.info("API에서 최신 뉴스 데이터 조회 중...")
            raw_data = self.connection_manager.execute_with_retry(
                self.api_client.get_news_data
            )
            
            if not raw_data:
                self.logger.warning("API에서 데이터를 받지 못함")
                return None
            
            # 데이터 파싱
            parsed_data = self.data_parser.parse_news_data(raw_data)
            
            # 데이터 검증
            is_valid, errors = self.data_parser.validate_parsed_data(parsed_data)
            if not is_valid:
                self.logger.error(f"데이터 검증 실패: {errors}")
                if self.on_parsing_error:
                    self.on_parsing_error(Exception(f"데이터 검증 실패: {errors}"))
                return None
            
            # 캐시 저장
            if use_cache:
                self._update_cache(cache_key, parsed_data)
            
            # 콜백 호출
            if self.on_data_update:
                try:
                    self.on_data_update(parsed_data)
                except Exception as e:
                    self.logger.error(f"데이터 업데이트 콜백 오류: {e}")
            
            self.logger.info(f"최신 뉴스 데이터 조회 성공: {len(parsed_data)}개 타입")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"최신 뉴스 데이터 조회 실패: {e}")
            return None
    
    def get_historical_data(self, start_date: str, end_date: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        기간별 과거 데이터 조회
        
        Args:
            start_date (str): 시작 날짜 (YYYYMMDD)
            end_date (str): 종료 날짜 (YYYYMMDD)
            use_cache (bool): 캐시 사용 여부
        
        Returns:
            dict: 날짜별 파싱된 뉴스 데이터
        """
        cache_key = f'historical_{start_date}_{end_date}'
        
        # 캐시 확인
        if use_cache and self._is_cache_valid(cache_key):
            self.logger.info(f"캐시에서 과거 데이터 반환: {start_date} ~ {end_date}")
            return self.cache_data.get(cache_key, {})
        
        try:
            self.logger.info(f"API에서 과거 데이터 조회 중: {start_date} ~ {end_date}")
            
            # API에서 과거 데이터 조회
            raw_historical_data = self.connection_manager.execute_with_retry(
                self.api_client.get_historical_data,
                start_date,
                end_date
            )
            
            if not raw_historical_data:
                self.logger.warning("과거 데이터를 받지 못함")
                return {}
            
            # 날짜별 데이터 파싱
            parsed_historical_data = {}
            for date_str, raw_data in raw_historical_data.items():
                parsed_data = self.data_parser.parse_news_data(raw_data)
                if parsed_data:
                    parsed_historical_data[date_str] = parsed_data
            
            # 캐시 저장
            if use_cache:
                self._update_cache(cache_key, parsed_historical_data)
            
            self.logger.info(f"과거 데이터 조회 성공: {len(parsed_historical_data)}일치 데이터")
            return parsed_historical_data
            
        except Exception as e:
            self.logger.error(f"과거 데이터 조회 실패: {e}")
            return {}
    
    def get_news_by_date(self, date: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        특정 날짜의 뉴스 데이터 조회
        
        Args:
            date (str): 조회할 날짜 (YYYYMMDD)
            use_cache (bool): 캐시 사용 여부
        
        Returns:
            dict: 파싱된 뉴스 데이터
        """
        cache_key = f'news_{date}'
        
        # 캐시 확인
        if use_cache and self._is_cache_valid(cache_key):
            self.logger.info(f"캐시에서 {date} 뉴스 데이터 반환")
            return self.cache_data.get(cache_key)
        
        try:
            self.logger.info(f"API에서 {date} 뉴스 데이터 조회 중...")
            
            # API에서 데이터 조회
            raw_data = self.connection_manager.execute_with_retry(
                self.api_client.get_news_data,
                date
            )
            
            if not raw_data:
                self.logger.warning(f"{date} 데이터를 받지 못함")
                return None
            
            # 데이터 파싱
            parsed_data = self.data_parser.parse_news_data(raw_data)
            
            # 캐시 저장
            if use_cache:
                self._update_cache(cache_key, parsed_data)
            
            self.logger.info(f"{date} 뉴스 데이터 조회 성공")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"{date} 뉴스 데이터 조회 실패: {e}")
            return None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        전체 시스템 상태 요약 반환
        
        Returns:
            dict: 상태 요약 정보
        """
        # 연결 상태
        connection_status = self.connection_manager.get_status()
        
        # 최신 데이터 상태
        latest_data = self.get_latest_news_data(use_cache=True)
        data_summary = None
        if latest_data:
            data_summary = self.data_parser.get_status_summary(latest_data)
        
        # 캐시 상태
        cache_status = {
            'enabled': self.cache_config['enabled'],
            'cache_entries': len(self.cache_data),
            'cache_size_kb': len(json.dumps(self.cache_data, default=str)) / 1024
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'connection': connection_status,
            'data': data_summary,
            'cache': cache_status,
            'overall_health': self._calculate_overall_health(connection_status, data_summary)
        }
    
    def _calculate_overall_health(self, connection_status: Dict[str, Any], data_summary: Optional[Dict[str, Any]]) -> str:
        """전체 시스템 건강도 계산"""
        if connection_status['status'] == 'failed':
            return 'critical'
        elif connection_status['status'] == 'degraded':
            return 'warning'
        elif data_summary and data_summary.get('overall_status') == 'all_latest':
            return 'healthy'
        elif data_summary and data_summary.get('overall_status') in ['partial_latest', 'has_delayed']:
            return 'warning'
        else:
            return 'unknown'
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        try:
            return self.connection_manager.execute_with_retry(
                self.api_client.test_connection
            )
        except Exception as e:
            self.logger.error(f"연결 테스트 실패: {e}")
            return False
    
    def start_monitoring(self):
        """연결 상태 모니터링 시작"""
        self.connection_manager.start_monitoring()
    
    def stop_monitoring(self):
        """연결 상태 모니터링 중지"""
        self.connection_manager.stop_monitoring()
    
    def clear_cache(self):
        """캐시 데이터 삭제"""
        with self.cache_lock:
            self.cache_data.clear()
            self.cache_timestamps.clear()
            self._save_cache()
            self.logger.info("캐시 데이터 삭제 완료")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 확인"""
        if not self.cache_config['enabled']:
            return False
        
        if cache_key not in self.cache_data:
            return False
        
        if cache_key not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[cache_key]
        cache_duration = self.cache_config['cache_duration']
        
        return (datetime.now() - cache_time).total_seconds() < cache_duration
    
    def _update_cache(self, cache_key: str, data: Any):
        """캐시 데이터 업데이트"""
        if not self.cache_config['enabled']:
            return
        
        with self.cache_lock:
            self.cache_data[cache_key] = data
            self.cache_timestamps[cache_key] = datetime.now()
            
            # 캐시 크기 제한
            max_size = self.cache_config['max_cache_size']
            if len(self.cache_data) > max_size:
                # 가장 오래된 항목 제거
                oldest_key = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
                del self.cache_data[oldest_key]
                del self.cache_timestamps[oldest_key]
            
            self._save_cache()
    
    def _load_cache(self):
        """캐시 파일 로드"""
        if not self.cache_config['enabled']:
            return
        
        cache_file = Path(self.cache_config['cache_file'])
        
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_content = json.load(f)
                    
                self.cache_data = cache_content.get('data', {})
                
                # 타임스탬프 복원
                timestamps = cache_content.get('timestamps', {})
                self.cache_timestamps = {
                    k: datetime.fromisoformat(v) for k, v in timestamps.items()
                }
                
                self.logger.info(f"캐시 파일 로드 완료: {len(self.cache_data)}개 항목")
        except Exception as e:
            self.logger.warning(f"캐시 파일 로드 실패: {e}")
            self.cache_data = {}
            self.cache_timestamps = {}
    
    def _save_cache(self):
        """캐시 파일 저장"""
        if not self.cache_config['enabled']:
            return
        
        cache_file = Path(self.cache_config['cache_file'])
        
        try:
            cache_content = {
                'data': self.cache_data,
                'timestamps': {
                    k: v.isoformat() for k, v in self.cache_timestamps.items()
                }
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_content, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"캐시 파일 저장 실패: {e}")
    
    def _on_connection_status_change(self, old_status: ConnectionStatus, new_status: ConnectionStatus):
        """연결 상태 변경 콜백"""
        self.logger.info(f"API 연결 상태 변경: {old_status.value} → {new_status.value}")
        
        if self.on_connection_issue and new_status == ConnectionStatus.FAILED:
            try:
                self.on_connection_issue(f"API 연결 실패: {old_status.value} → {new_status.value}")
            except Exception as e:
                self.logger.error(f"연결 이슈 콜백 오류: {e}")
    
    def _on_connection_failure(self, exception: Exception):
        """연결 실패 콜백"""
        self.logger.error(f"API 연결 실패: {exception}")
    
    def _on_connection_recovery(self):
        """연결 복구 콜백"""
        self.logger.info("API 연결 복구됨")
    
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
        from recovery_config.environment_settings import load_environment_settings
        
        settings = load_environment_settings()
        api_config = settings.get('API_CONFIG', {})
        
        if api_config:
            # 통합 API 모듈 생성
            api_module = IntegratedAPIModule(api_config)
            
            # 콜백 함수 설정
            def on_data_update(data):
                print(f"📊 데이터 업데이트: {len(data)}개 뉴스 타입")
            
            def on_connection_issue(message):
                print(f"⚠️ 연결 이슈: {message}")
            
            api_module.on_data_update = on_data_update
            api_module.on_connection_issue = on_connection_issue
            
            print("=== 통합 API 모듈 테스트 ===")
            
            # 연결 테스트
            print("1. 연결 테스트...")
            if api_module.test_connection():
                print("✅ 연결 성공")
            else:
                print("❌ 연결 실패")
            
            # 최신 데이터 조회
            print("\n2. 최신 데이터 조회...")
            latest_data = api_module.get_latest_news_data()
            if latest_data:
                print("✅ 최신 데이터 조회 성공")
                for news_type, news_item in latest_data.items():
                    print(f"  - {news_type}: {news_item.get('status_description', 'N/A')}")
            else:
                print("❌ 최신 데이터 조회 실패")
            
            # 상태 요약
            print("\n3. 시스템 상태 요약:")
            status = api_module.get_status_summary()
            print(f"  전체 건강도: {status['overall_health']}")
            print(f"  연결 상태: {status['connection']['status']}")
            if status['data']:
                print(f"  데이터 상태: {status['data']['overall_status']}")
            print(f"  캐시 항목: {status['cache']['cache_entries']}개")
            
            print("\n테스트 완료")
        else:
            print("❌ API 설정을 찾을 수 없습니다.")
            
    except ImportError as e:
        print(f"❌ 모듈 로드 실패: {e}")
        print("필요한 모듈이 없어 테스트를 진행할 수 없습니다.")