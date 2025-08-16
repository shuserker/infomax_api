#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 모듈 테스트 스크립트

INFOMAX API 연동 모듈들의 기능을 종합적으로 테스트합니다.

테스트 항목:
- API 클라이언트 기본 기능
- 데이터 파싱 및 검증
- 연결 관리 및 재시도
- 통합 모듈 기능
- 성능 및 안정성

작성자: AI Assistant
복원 일시: 2025-08-12
"""

import sys
import os
import time
import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from recovery_config.infomax_api_client import InfomaxAPIClient
    from recovery_config.api_data_parser import APIDataParser
    from recovery_config.api_connection_manager import APIConnectionManager, ConnectionStatus
    from recovery_config.integrated_api_module import IntegratedAPIModule
    from recovery_config.environment_settings import load_environment_settings
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class TestInfomaxAPIClient(unittest.TestCase):
    """INFOMAX API 클라이언트 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.api_config = {
            'url': 'https://dev-global-api.einfomax.co.kr/apis/posco/news',
            'user': 'infomax',
            'password': 'infomax!',
            'timeout': 10,
            'max_retries': 3,
            'retry_delay': 0.1
        }
        self.client = InfomaxAPIClient(self.api_config)
    
    def test_client_initialization(self):
        """클라이언트 초기화 테스트"""
        self.assertEqual(self.client.api_url, self.api_config['url'])
        self.assertEqual(self.client.api_user, self.api_config['user'])
        self.assertEqual(self.client.api_timeout, self.api_config['timeout'])
        self.assertEqual(self.client.max_retries, self.api_config['max_retries'])
    
    def test_connection_info(self):
        """연결 정보 반환 테스트"""
        info = self.client.get_connection_info()
        self.assertIn('api_url', info)
        self.assertIn('api_user', info)
        self.assertNotIn('api_pwd', info)  # 비밀번호는 포함되지 않아야 함
    
    @patch('requests.get')
    def test_successful_api_call(self, mock_get):
        """성공적인 API 호출 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'newyork-market-watch': {
                'title': 'Test News',
                'date': '20250812',
                'time': '060000'
            }
        }
        mock_get.return_value = mock_response
        
        # API 호출
        result = self.client.get_news_data()
        
        # 검증
        self.assertIsNotNone(result)
        self.assertIn('newyork-market-watch', result)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_api_retry_mechanism(self, mock_get):
        """API 재시도 메커니즘 테스트"""
        # 처음 두 번은 실패, 세 번째는 성공
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = Exception("Server Error")
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'test': 'data'}
        
        mock_get.side_effect = [Exception("Connection Error"), Exception("Timeout"), mock_response_success]
        
        # API 호출
        result = self.client.get_news_data()
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(mock_get.call_count, 3)


class TestAPIDataParser(unittest.TestCase):
    """API 데이터 파서 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.parser = APIDataParser()
        self.sample_data = {
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
    
    def test_parse_news_data(self):
        """뉴스 데이터 파싱 테스트"""
        parsed_data = self.parser.parse_news_data(self.sample_data)
        
        self.assertIsInstance(parsed_data, dict)
        self.assertIn('newyork-market-watch', parsed_data)
        self.assertIn('kospi-close', parsed_data)
        
        # 파싱된 데이터 구조 확인
        for news_type, news_item in parsed_data.items():
            self.assertIn('title', news_item)
            self.assertIn('status', news_item)
            self.assertIn('status_description', news_item)
            self.assertIn('display_name', news_item)
    
    def test_validate_parsed_data(self):
        """파싱된 데이터 검증 테스트"""
        parsed_data = self.parser.parse_news_data(self.sample_data)
        is_valid, errors = self.parser.validate_parsed_data(parsed_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_status_summary(self):
        """상태 요약 생성 테스트"""
        parsed_data = self.parser.parse_news_data(self.sample_data)
        summary = self.parser.get_status_summary(parsed_data)
        
        self.assertIn('total_news', summary)
        self.assertIn('overall_status', summary)
        self.assertIn('news_status', summary)
        self.assertEqual(summary['total_news'], 2)
    
    def test_invalid_data_handling(self):
        """잘못된 데이터 처리 테스트"""
        invalid_data = {
            'invalid-type': {
                'title': '',  # 빈 제목
                'date': 'invalid',  # 잘못된 날짜
                'time': 'invalid'   # 잘못된 시간
            }
        }
        
        parsed_data = self.parser.parse_news_data(invalid_data)
        is_valid, errors = self.parser.validate_parsed_data(parsed_data)
        
        # 잘못된 데이터는 파싱되지 않아야 함
        self.assertNotIn('invalid-type', parsed_data)


class TestAPIConnectionManager(unittest.TestCase):
    """API 연결 관리자 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.api_client = Mock()
        self.manager = APIConnectionManager(self.api_client, {
            'max_retries': 2,
            'base_delay': 0.1,
            'health_check_interval': 1
        })
    
    def test_manager_initialization(self):
        """관리자 초기화 테스트"""
        self.assertEqual(self.manager.status, ConnectionStatus.UNKNOWN)
        self.assertIsNotNone(self.manager.metrics)
    
    def test_successful_operation(self):
        """성공적인 작업 실행 테스트"""
        # Mock 함수 설정
        mock_operation = Mock(return_value="success")
        
        # 작업 실행
        result = self.manager.execute_with_retry(mock_operation, "arg1", key="value")
        
        # 검증
        self.assertEqual(result, "success")
        mock_operation.assert_called_once_with("arg1", key="value")
        self.assertEqual(self.manager.metrics.successful_requests, 1)
    
    def test_retry_mechanism(self):
        """재시도 메커니즘 테스트"""
        # Mock 함수 설정 (처음에는 실패, 나중에 성공)
        mock_operation = Mock(side_effect=[Exception("Error"), "success"])
        
        # 작업 실행
        result = self.manager.execute_with_retry(mock_operation)
        
        # 검증
        self.assertEqual(result, "success")
        self.assertEqual(mock_operation.call_count, 2)
        self.assertEqual(self.manager.metrics.successful_requests, 1)
        self.assertEqual(self.manager.metrics.failed_requests, 1)
    
    def test_status_tracking(self):
        """상태 추적 테스트"""
        status_info = self.manager.get_status()
        
        self.assertIn('status', status_info)
        self.assertIn('metrics', status_info)
        self.assertIn('config', status_info)
    
    def test_health_methods(self):
        """건강도 확인 메서드 테스트"""
        # 초기 상태
        self.assertFalse(self.manager.is_healthy())
        self.assertFalse(self.manager.is_available())
        
        # 상태 변경
        self.manager.status = ConnectionStatus.HEALTHY
        self.assertTrue(self.manager.is_healthy())
        self.assertTrue(self.manager.is_available())
        
        self.manager.status = ConnectionStatus.DEGRADED
        self.assertFalse(self.manager.is_healthy())
        self.assertTrue(self.manager.is_available())


class TestIntegratedAPIModule(unittest.TestCase):
    """통합 API 모듈 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.api_config = {
            'url': 'https://test-api.example.com',
            'user': 'test',
            'password': 'test',
            'timeout': 5
        }
        self.cache_config = {
            'enabled': True,
            'cache_file': 'test_cache.json',
            'cache_duration': 60
        }
        
        # Mock 객체들 생성
        with patch('recovery_config.integrated_api_module.InfomaxAPIClient'), \
             patch('recovery_config.integrated_api_module.APIDataParser'), \
             patch('recovery_config.integrated_api_module.APIConnectionManager'):
            
            self.module = IntegratedAPIModule(self.api_config, self.cache_config)
    
    def test_module_initialization(self):
        """모듈 초기화 테스트"""
        self.assertIsNotNone(self.module.api_client)
        self.assertIsNotNone(self.module.data_parser)
        self.assertIsNotNone(self.module.connection_manager)
        self.assertEqual(self.module.cache_config['enabled'], True)
    
    def test_cache_operations(self):
        """캐시 작업 테스트"""
        # 캐시 업데이트
        test_data = {'test': 'data'}
        self.module._update_cache('test_key', test_data)
        
        # 캐시 유효성 확인
        self.assertTrue(self.module._is_cache_valid('test_key'))
        self.assertEqual(self.module.cache_data['test_key'], test_data)
        
        # 캐시 삭제
        self.module.clear_cache()
        self.assertEqual(len(self.module.cache_data), 0)
    
    def test_status_summary(self):
        """상태 요약 테스트"""
        # Mock 설정
        self.module.connection_manager.get_status = Mock(return_value={
            'status': 'healthy',
            'metrics': {'success_rate': 0.95}
        })
        
        summary = self.module.get_status_summary()
        
        self.assertIn('timestamp', summary)
        self.assertIn('connection', summary)
        self.assertIn('cache', summary)
        self.assertIn('overall_health', summary)


class APIModuleIntegrationTest:
    """통합 테스트 클래스"""
    
    def __init__(self):
        """통합 테스트 초기화"""
        self.settings = None
        self.api_module = None
        self.test_results = []
    
    def load_settings(self):
        """설정 로드"""
        try:
            self.settings = load_environment_settings()
            api_config = self.settings.get('API_CONFIG', {})
            
            if not api_config:
                raise Exception("API 설정을 찾을 수 없습니다")
            
            self.api_module = IntegratedAPIModule(api_config)
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ 설정 로드 실패: {e}")
            return False
    
    def test_connection(self):
        """연결 테스트"""
        try:
            if self.api_module.test_connection():
                self.test_results.append("✅ API 연결 테스트 성공")
                return True
            else:
                self.test_results.append("❌ API 연결 테스트 실패")
                return False
        except Exception as e:
            self.test_results.append(f"❌ 연결 테스트 오류: {e}")
            return False
    
    def test_data_retrieval(self):
        """데이터 조회 테스트"""
        try:
            # 최신 데이터 조회
            latest_data = self.api_module.get_latest_news_data()
            if latest_data:
                self.test_results.append(f"✅ 최신 데이터 조회 성공: {len(latest_data)}개 타입")
                
                # 각 뉴스 타입별 상태 확인
                for news_type, news_item in latest_data.items():
                    status = news_item.get('status_description', 'N/A')
                    self.test_results.append(f"  - {news_type}: {status}")
                
                return True
            else:
                self.test_results.append("❌ 최신 데이터 조회 실패")
                return False
                
        except Exception as e:
            self.test_results.append(f"❌ 데이터 조회 오류: {e}")
            return False
    
    def test_historical_data(self):
        """과거 데이터 조회 테스트"""
        try:
            # 최근 3일간 데이터 조회
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')
            
            historical_data = self.api_module.get_historical_data(start_date, end_date)
            if historical_data:
                self.test_results.append(f"✅ 과거 데이터 조회 성공: {len(historical_data)}일치 데이터")
                return True
            else:
                self.test_results.append("⚠️ 과거 데이터 없음 (정상일 수 있음)")
                return True
                
        except Exception as e:
            self.test_results.append(f"❌ 과거 데이터 조회 오류: {e}")
            return False
    
    def test_system_status(self):
        """시스템 상태 테스트"""
        try:
            status = self.api_module.get_status_summary()
            
            self.test_results.append("📊 시스템 상태 요약:")
            self.test_results.append(f"  전체 건강도: {status['overall_health']}")
            self.test_results.append(f"  연결 상태: {status['connection']['status']}")
            
            if status['data']:
                self.test_results.append(f"  데이터 상태: {status['data']['overall_status']}")
                self.test_results.append(f"  뉴스 개수: {status['data']['total_news']}")
            
            self.test_results.append(f"  캐시 항목: {status['cache']['cache_entries']}개")
            
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ 시스템 상태 확인 오류: {e}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=== INFOMAX API 모듈 통합 테스트 ===")
        print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 테스트 실행
        tests = [
            ("설정 로드", self.load_settings),
            ("연결 테스트", self.test_connection),
            ("데이터 조회", self.test_data_retrieval),
            ("과거 데이터", self.test_historical_data),
            ("시스템 상태", self.test_system_status)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"🔍 {test_name} 테스트 중...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.test_results.append(f"❌ {test_name} 테스트 예외: {e}")
            print()
        
        # 결과 출력
        print("=== 테스트 결과 ===")
        for result in self.test_results:
            print(result)
        
        print()
        print(f"📈 테스트 요약: {passed}/{total} 통과")
        print(f"테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed == total


def main():
    """메인 함수"""
    print("INFOMAX API 연동 모듈 테스트 시작")
    print("=" * 50)
    
    # 단위 테스트 실행
    print("\n1. 단위 테스트 실행...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 50)
    
    # 통합 테스트 실행
    print("\n2. 통합 테스트 실행...")
    integration_test = APIModuleIntegrationTest()
    success = integration_test.run_all_tests()
    
    print("\n" + "=" * 50)
    print(f"전체 테스트 결과: {'✅ 성공' if success else '❌ 실패'}")


if __name__ == "__main__":
    main()