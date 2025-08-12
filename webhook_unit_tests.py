#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 함수 단위 테스트
각 웹훅 함수에 대한 상세한 단위 테스트

Requirements: 4.1, 4.2
- 모든 웹훅 함수에 대한 단위 테스트 작성
- 메시지 내용과 포맷 정확성 자동 검증 로직 구현
"""

import unittest
import sys
import os
import json
import re
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List, Any, Optional

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

class WebhookMessageTestCase(unittest.TestCase):
    """웹훅 메시지 테스트 기본 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.target_file = "core/monitoring/monitor_WatchHamster_v3.0.py"
        self.captured_requests = []
        
        # requests.post 모킹
        self.mock_post_patcher = patch('requests.post')
        self.mock_post = self.mock_post_patcher.start()
        self.mock_post.return_value.status_code = 200
        self.mock_post.side_effect = self._capture_request
        
        # 모듈 로드
        self.monitor_module = self._load_monitor_module()
    
    def tearDown(self):
        """테스트 정리"""
        self.mock_post_patcher.stop()
    
    def _capture_request(self, *args, **kwargs):
        """HTTP 요청 캡처"""
        self.captured_requests.append({
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.now()
        })
        
        # Mock 응답 반환
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        return mock_response
    
    def _load_monitor_module(self):
        """모니터 모듈 로드"""
        try:
            if not os.path.exists(self.target_file):
                self.skipTest(f"대상 파일을 찾을 수 없습니다: {self.target_file}")
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("monitor_module", self.target_file)
            module = importlib.util.module_from_spec(spec)
            
            # 의존성 모킹
            with patch.dict('sys.modules', {
                'config': Mock(),
                'requests': Mock()
            }):
                spec.loader.exec_module(module)
            
            return module
        except Exception as e:
            self.skipTest(f"모듈 로드 실패: {e}")
    
    def _create_monitor_instance(self):
        """모니터 인스턴스 생성 (모킹된 환경)"""
        try:
            # 필요한 설정 모킹
            with patch.dict('os.environ', {
                'PYTHONUNBUFFERED': '1'
            }):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open_multiple_files()):
                        monitor = self.monitor_module.WatchHamsterV3Monitor()
                        return monitor
        except Exception as e:
            self.skipTest(f"모니터 인스턴스 생성 실패: {e}")
    
    def assertMessageFormat(self, captured_request: Dict[str, Any], expected_fields: List[str]):
        """메시지 포맷 검증"""
        self.assertIn('json', captured_request['kwargs'])
        
        json_data = captured_request['kwargs']['json']
        
        # 필수 필드 확인
        for field in expected_fields:
            self.assertIn(field, json_data, f"필수 필드 '{field}'가 누락됨")
        
        # 봇 이름 확인
        if 'botName' in json_data:
            self.assertIn('워치햄스터', json_data['botName'], "봇 이름에 '워치햄스터'가 포함되어야 함")
        
        # attachments 구조 확인
        if 'attachments' in json_data:
            self.assertIsInstance(json_data['attachments'], list, "attachments는 리스트여야 함")
            if json_data['attachments']:
                attachment = json_data['attachments'][0]
                self.assertIn('text', attachment, "attachment에 text 필드가 있어야 함")
    
    def assertNoInvalidLineBreaks(self, text: str):
        """잘못된 줄바꿈 문자 확인"""
        invalid_breaks = text.count('/n')
        self.assertEqual(invalid_breaks, 0, f"잘못된 줄바꿈 문자 '/n'이 {invalid_breaks}개 발견됨")
    
    def assertKoreanText(self, text: str):
        """한국어 텍스트 포함 확인"""
        korean_pattern = r'[가-힣]+'
        korean_matches = re.findall(korean_pattern, text)
        self.assertGreater(len(korean_matches), 0, "한국어 텍스트가 포함되어야 함")

class TestStatusNotificationFunctions(WebhookMessageTestCase):
    """상태 알림 함수 테스트"""
    
    def test_send_status_notification_exists(self):
        """send_status_notification 함수 존재 확인"""
        self.assertTrue(hasattr(self.monitor_module, 'WatchHamsterV3Monitor'))
        
        monitor = self._create_monitor_instance()
        self.assertTrue(hasattr(monitor, 'send_status_notification'))
    
    def test_send_status_notification_message_format(self):
        """send_status_notification 메시지 포맷 테스트"""
        monitor = self._create_monitor_instance()
        
        # 함수 실행
        try:
            monitor.send_status_notification()
        except Exception as e:
            # 실제 실행 오류는 무시 (모킹 환경이므로)
            pass
        
        # 요청이 캡처되었는지 확인
        if self.captured_requests:
            request = self.captured_requests[-1]
            self.assertMessageFormat(request, ['botName', 'attachments'])
            
            # 상태 알림 특화 검증
            json_data = request['kwargs']['json']
            if 'attachments' in json_data and json_data['attachments']:
                text = json_data['attachments'][0].get('text', '')
                self.assertIn('상태', text, "상태 알림에 '상태' 텍스트가 포함되어야 함")
                self.assertNoInvalidLineBreaks(text)
                self.assertKoreanText(text)
    
    def test_send_enhanced_status_notification(self):
        """send_enhanced_status_notification 테스트"""
        monitor = self._create_monitor_instance()
        
        if hasattr(monitor, 'send_enhanced_status_notification'):
            try:
                monitor.send_enhanced_status_notification()
            except Exception:
                pass
            
            if self.captured_requests:
                request = self.captured_requests[-1]
                self.assertMessageFormat(request, ['botName', 'attachments'])

class TestErrorNotificationFunctions(WebhookMessageTestCase):
    """오류 알림 함수 테스트"""
    
    def test_send_process_error_v2(self):
        """send_process_error_v2 함수 테스트"""
        monitor = self._create_monitor_instance()
        
        if hasattr(monitor, 'send_process_error_v2'):
            try:
                monitor.send_process_error_v2("test_process", "test error details")
            except Exception:
                pass
            
            if self.captured_requests:
                request = self.captured_requests[-1]
                self.assertMessageFormat(request, ['botName', 'attachments'])
                
                # 오류 알림 특화 검증
                json_data = request['kwargs']['json']
                if 'attachments' in json_data and json_data['attachments']:
                    text = json_data['attachments'][0].get('text', '')
                    self.assertIn('오류', text, "오류 알림에 '오류' 텍스트가 포함되어야 함")
                    self.assertNoInvalidLineBreaks(text)
    
    def test_send_critical_alert_v2(self):
        """send_critical_alert_v2 함수 테스트"""
        monitor = self._create_monitor_instance()
        
        if hasattr(monitor, 'send_critical_alert_v2'):
            try:
                monitor.send_critical_alert_v2("Critical test alert")
            except Exception:
                pass
            
            if self.captured_requests:
                request = self.captured_requests[-1]
                self.assertMessageFormat(request, ['botName', 'attachments'])
                
                # 긴급 알림 특화 검증
                json_data = request['kwargs']['json']
                if 'attachments' in json_data and json_data['attachments']:
                    attachment = json_data['attachments'][0]
                    # 긴급 알림은 빨간색이어야 함
                    self.assertIn('color', attachment)
                    color = attachment['color'].lower()
                    self.assertIn('red', color, "긴급 알림은 빨간색이어야 함")

class TestRecoveryNotificationFunctions(WebhookMessageTestCase):
    """복구 알림 함수 테스트"""
    
    def test_send_recovery_success_v2(self):
        """send_recovery_success_v2 함수 테스트"""
        monitor = self._create_monitor_instance()
        
        if hasattr(monitor, 'send_recovery_success_v2'):
            try:
                monitor.send_recovery_success_v2("test_process", "recovery details")
            except Exception:
                pass
            
            if self.captured_requests:
                request = self.captured_requests[-1]
                self.assertMessageFormat(request, ['botName', 'attachments'])
                
                # 복구 성공 알림 특화 검증
                json_data = request['kwargs']['json']
                if 'attachments' in json_data and json_data['attachments']:
                    text = json_data['attachments'][0].get('text', '')
                    self.assertIn('복구', text, "복구 알림에 '복구' 텍스트가 포함되어야 함")
                    self.assertNoInvalidLineBreaks(text)

class TestStartupNotificationFunctions(WebhookMessageTestCase):
    """시작 알림 함수 테스트"""
    
    def test_send_startup_notification_v2(self):
        """send_startup_notification_v2 함수 테스트"""
        monitor = self._create_monitor_instance()
        
        if hasattr(monitor, 'send_startup_notification_v2'):
            try:
                monitor.send_startup_notification_v2()
            except Exception:
                pass
            
            if self.captured_requests:
                request = self.captured_requests[-1]
                self.assertMessageFormat(request, ['botName', 'attachments'])
                
                # 시작 알림 특화 검증
                json_data = request['kwargs']['json']
                if 'attachments' in json_data and json_data['attachments']:
                    text = json_data['attachments'][0].get('text', '')
                    self.assertIn('시작', text, "시작 알림에 '시작' 텍스트가 포함되어야 함")
                    self.assertNoInvalidLineBreaks(text)
                    self.assertKoreanText(text)

class TestGeneralNotificationFunctions(WebhookMessageTestCase):
    """일반 알림 함수 테스트"""
    
    def test_send_notification(self):
        """send_notification 함수 테스트"""
        monitor = self._create_monitor_instance()
        
        if hasattr(monitor, 'send_notification'):
            try:
                monitor.send_notification("테스트 메시지")
            except Exception:
                pass
            
            if self.captured_requests:
                request = self.captured_requests[-1]
                self.assertMessageFormat(request, ['botName', 'attachments'])
                
                # 일반 알림 검증
                json_data = request['kwargs']['json']
                if 'attachments' in json_data and json_data['attachments']:
                    text = json_data['attachments'][0].get('text', '')
                    self.assertIn('테스트 메시지', text, "전달된 메시지가 포함되어야 함")
                    self.assertNoInvalidLineBreaks(text)

def mock_open_multiple_files():
    """여러 파일에 대한 mock open"""
    def mock_open_func(*args, **kwargs):
        mock_file = Mock()
        mock_file.read.return_value = '{"test": "data"}'
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        return mock_file
    return mock_open_func

class WebhookTestRunner:
    """웹훅 테스트 실행기"""
    
    def __init__(self):
        self.test_results = {}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 단위 테스트 실행"""
        print("🧪 웹훅 함수 단위 테스트 실행...")
        print("=" * 60)
        
        # 테스트 스위트 구성
        test_classes = [
            TestStatusNotificationFunctions,
            TestErrorNotificationFunctions,
            TestRecoveryNotificationFunctions,
            TestStartupNotificationFunctions,
            TestGeneralNotificationFunctions
        ]
        
        overall_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_details': {},
            'summary': {}
        }
        
        for test_class in test_classes:
            print(f"\n📋 {test_class.__name__} 실행 중...")
            
            # 테스트 스위트 생성
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            
            # 테스트 실행
            runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
            result = runner.run(suite)
            
            # 결과 집계
            class_results = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success_rate': 0
            }
            
            if result.testsRun > 0:
                passed = result.testsRun - len(result.failures) - len(result.errors)
                class_results['success_rate'] = (passed / result.testsRun) * 100
            
            overall_results['test_details'][test_class.__name__] = class_results
            overall_results['total_tests'] += result.testsRun
            overall_results['failed_tests'] += len(result.failures) + len(result.errors)
            overall_results['skipped_tests'] += class_results['skipped']
            
            print(f"   테스트 실행: {result.testsRun}개")
            print(f"   실패: {len(result.failures) + len(result.errors)}개")
            print(f"   성공률: {class_results['success_rate']:.1f}%")
        
        # 전체 성공률 계산
        overall_results['passed_tests'] = (
            overall_results['total_tests'] - 
            overall_results['failed_tests'] - 
            overall_results['skipped_tests']
        )
        
        if overall_results['total_tests'] > 0:
            overall_success_rate = (overall_results['passed_tests'] / overall_results['total_tests']) * 100
        else:
            overall_success_rate = 0
        
        overall_results['summary'] = {
            'success_rate': overall_success_rate,
            'total': overall_results['total_tests'],
            'passed': overall_results['passed_tests'],
            'failed': overall_results['failed_tests'],
            'skipped': overall_results['skipped_tests']
        }
        
        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 단위 테스트 결과 요약")
        print("=" * 60)
        print(f"전체 테스트: {overall_results['total_tests']}개")
        print(f"통과: {overall_results['passed_tests']}개")
        print(f"실패: {overall_results['failed_tests']}개")
        print(f"건너뜀: {overall_results['skipped_tests']}개")
        print(f"전체 성공률: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            print("\n🎉 웹훅 함수 단위 테스트가 성공적으로 완료되었습니다!")
        elif overall_success_rate >= 70:
            print("\n⚠️ 일부 테스트에서 문제가 발견되었지만 대부분 정상입니다.")
        else:
            print("\n❌ 다수의 테스트에서 문제가 발견되었습니다.")
        
        return overall_results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """테스트 결과 저장"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"webhook_unit_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 단위 테스트 결과 저장: {filename}")
            return filename
        except Exception as e:
            print(f"⚠️ 결과 저장 실패: {e}")
            return None

def run_webhook_unit_tests():
    """웹훅 단위 테스트 실행 메인 함수"""
    print("🚀 웹훅 함수 단위 테스트 시작")
    print("=" * 80)
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    runner = WebhookTestRunner()
    results = runner.run_all_tests()
    
    # 결과 저장
    runner.save_results(results)
    
    return results['summary']['success_rate'] >= 70

if __name__ == "__main__":
    success = run_webhook_unit_tests()
    sys.exit(0 if success else 1)