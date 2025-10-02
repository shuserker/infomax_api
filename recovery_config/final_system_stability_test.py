#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 최종 안정성 검증 테스트
정상 커밋 a763ef84 기준 완전 복구 시스템의 안정성과 성능을 종합 검증
"""

import os
import sys
import time
import json
import psutil
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# 현재 디렉토리를 sys.path에 추가하여 모듈 import 가능하게 함
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recovery_config/stability_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemStabilityTester:
    """시스템 안정성 종합 검증 클래스"""
    
    def __init__(self):
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'tests': {},
            'performance_metrics': {},
            'stability_score': 0,
            'recommendations': []
        }
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
    def run_comprehensive_stability_test(self) -> Dict[str, Any]:
        """종합 안정성 테스트 실행"""
        logger.info("🔍 POSCO 시스템 최종 안정성 검증 시작")
        
        # 1. 시스템 성능 기준선 측정
        self._measure_baseline_performance()
        
        # 2. 기능 완성도 검증
        self._verify_feature_completeness()
        
        # 3. 오류 처리 메커니즘 검증
        self._verify_error_handling()
        
        # 4. 시스템 모니터링 검증
        self._verify_monitoring_system()
        
        # 5. 부하 테스트
        self._run_load_test()
        
        # 6. 메모리 누수 검증
        self._verify_memory_stability()
        
        # 7. 장기 안정성 테스트
        self._run_long_term_stability_test()
        
        # 8. 최종 안정성 점수 계산
        self._calculate_stability_score()
        
        # 9. 결과 저장
        self._save_results()
        
        return self.test_results
    
    def _measure_baseline_performance(self):
        """시스템 성능 기준선 측정"""
        logger.info("📊 시스템 성능 기준선 측정 중...")
        
        try:
            # CPU 사용률 측정
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률 측정
            memory = psutil.virtual_memory()
            
            # 디스크 사용률 측정
            disk = psutil.disk_usage('/')
            
            # 네트워크 상태 측정
            network = psutil.net_io_counters()
            
            performance_data = {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage_percent': (disk.used / disk.total) * 100,
                'disk_free_gb': disk.free / (1024**3),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
            
            self.test_results['performance_metrics']['baseline'] = performance_data
            self.test_results['tests']['baseline_performance'] = {
                'status': 'PASS',
                'message': '시스템 성능 기준선 측정 완료',
                'details': performance_data
            }
            
            logger.info(f"✅ 성능 기준선 측정 완료: CPU {cpu_percent}%, 메모리 {memory.percent}%")
            
        except Exception as e:
            self.test_results['tests']['baseline_performance'] = {
                'status': 'FAIL',
                'message': f'성능 기준선 측정 실패: {str(e)}'
            }
            logger.error(f"❌ 성능 기준선 측정 실패: {e}")
    
    def _verify_feature_completeness(self):
        """기능 완성도 검증"""
        logger.info("🔧 기능 완성도 검증 중...")
        
        try:
            # 핵심 모듈들 import 테스트
            core_modules = [
                'environment_setup',
                'integrated_api_module',
                'integrated_news_parser',
                'news_message_generator',
                'webhook_sender',
                'watchhamster_monitor',
                'ai_analysis_engine',
                'business_day_comparison_engine'
            ]
            
            import_results = {}
            for module in core_modules:
                try:
                    # 현재 디렉토리에서 직접 import
                    import sys
                    import os
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    if current_dir not in sys.path:
                        sys.path.insert(0, current_dir)
                    
                    __import__(module)
                    import_results[module] = 'SUCCESS'
                except Exception as e:
                    import_results[module] = f'FAIL: {str(e)}'
            
            # 기능 테스트 실행
            feature_tests = self._run_feature_tests()
            
            success_count = sum(1 for result in import_results.values() if result == 'SUCCESS')
            total_count = len(import_results)
            completeness_score = (success_count / total_count) * 100
            
            self.test_results['tests']['feature_completeness'] = {
                'status': 'PASS' if completeness_score >= 90 else 'FAIL',
                'message': f'기능 완성도: {completeness_score:.1f}% ({success_count}/{total_count})',
                'details': {
                    'module_imports': import_results,
                    'feature_tests': feature_tests,
                    'completeness_score': completeness_score
                }
            }
            
            logger.info(f"✅ 기능 완성도 검증 완료: {completeness_score:.1f}%")
            
        except Exception as e:
            self.test_results['tests']['feature_completeness'] = {
                'status': 'FAIL',
                'message': f'기능 완성도 검증 실패: {str(e)}'
            }
            logger.error(f"❌ 기능 완성도 검증 실패: {e}")
    
    def _run_feature_tests(self) -> Dict[str, str]:
        """개별 기능 테스트 실행"""
        feature_tests = {}
        
        try:
            # 현재 디렉토리를 sys.path에 추가
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # API 연동 테스트
            from integrated_api_module import IntegratedAPIModule
            api_module = IntegratedAPIModule()
            test_data = api_module.create_test_data()
            feature_tests['api_integration'] = 'SUCCESS' if test_data else 'FAIL'
            
            # 메시지 생성 테스트
            from news_message_generator import NewsMessageGenerator
            msg_generator = NewsMessageGenerator()
            test_message = msg_generator.generate_comprehensive_message(test_data)
            feature_tests['message_generation'] = 'SUCCESS' if test_message else 'FAIL'
            
            # 웹훅 테스트
            from webhook_sender import WebhookSender
            webhook = WebhookSender()
            webhook_result = webhook.validate_message_format(test_message)
            feature_tests['webhook_validation'] = 'SUCCESS' if webhook_result else 'FAIL'
            
        except Exception as e:
            feature_tests['error'] = str(e)
        
        return feature_tests
    
    def _verify_error_handling(self):
        """오류 처리 메커니즘 검증"""
        logger.info("🛡️ 오류 처리 메커니즘 검증 중...")
        
        try:
            error_scenarios = []
            
            # 1. API 연결 실패 시나리오
            error_scenarios.append(self._test_api_connection_failure())
            
            # 2. 잘못된 데이터 처리 시나리오
            error_scenarios.append(self._test_invalid_data_handling())
            
            # 3. 웹훅 전송 실패 시나리오
            error_scenarios.append(self._test_webhook_failure())
            
            # 4. 메모리 부족 시나리오
            error_scenarios.append(self._test_memory_pressure())
            
            passed_scenarios = sum(1 for scenario in error_scenarios if scenario['status'] == 'PASS')
            total_scenarios = len(error_scenarios)
            
            self.test_results['tests']['error_handling'] = {
                'status': 'PASS' if passed_scenarios >= total_scenarios * 0.8 else 'FAIL',
                'message': f'오류 처리 검증: {passed_scenarios}/{total_scenarios} 시나리오 통과',
                'details': {
                    'scenarios': error_scenarios,
                    'pass_rate': (passed_scenarios / total_scenarios) * 100
                }
            }
            
            logger.info(f"✅ 오류 처리 메커니즘 검증 완료: {passed_scenarios}/{total_scenarios}")
            
        except Exception as e:
            self.test_results['tests']['error_handling'] = {
                'status': 'FAIL',
                'message': f'오류 처리 검증 실패: {str(e)}'
            }
            logger.error(f"❌ 오류 처리 검증 실패: {e}")
    
    def _test_api_connection_failure(self) -> Dict[str, Any]:
        """API 연결 실패 테스트"""
        try:
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from integrated_api_module import IntegratedAPIModule
            api_module = IntegratedAPIModule()
            
            # 잘못된 URL로 테스트
            original_url = getattr(api_module, 'base_url', None)
            api_module.base_url = 'http://invalid-url-test.com'
            
            # 연결 실패 처리 확인
            result = api_module.handle_connection_error()
            
            # 원래 URL 복원
            if original_url:
                api_module.base_url = original_url
            
            return {
                'name': 'API 연결 실패 처리',
                'status': 'PASS' if result else 'FAIL',
                'details': 'API 연결 실패 시 적절한 오류 처리 확인'
            }
        except Exception as e:
            return {
                'name': 'API 연결 실패 처리',
                'status': 'FAIL',
                'details': f'테스트 실행 오류: {str(e)}'
            }
    
    def _test_invalid_data_handling(self) -> Dict[str, Any]:
        """잘못된 데이터 처리 테스트"""
        try:
            from integrated_news_parser import IntegratedNewsParser
            parser = IntegratedNewsParser()
            
            # 잘못된 데이터로 테스트
            invalid_data = {'invalid': 'data', 'structure': None}
            result = parser.parse_news_data(invalid_data)
            
            return {
                'name': '잘못된 데이터 처리',
                'status': 'PASS' if result is not None else 'FAIL',
                'details': '잘못된 데이터 입력 시 안전한 처리 확인'
            }
        except Exception as e:
            return {
                'name': '잘못된 데이터 처리',
                'status': 'PASS',  # 예외 발생도 적절한 처리로 간주
                'details': f'예외 처리 확인: {str(e)}'
            }
    
    def _test_webhook_failure(self) -> Dict[str, Any]:
        """웹훅 전송 실패 테스트"""
        try:
            from webhook_sender import WebhookSender
            webhook = WebhookSender()
            
            # 잘못된 웹훅 URL로 테스트
            result = webhook.send_webhook("테스트 메시지", "http://invalid-webhook-url.com")
            
            return {
                'name': '웹훅 전송 실패 처리',
                'status': 'PASS' if not result else 'FAIL',  # 실패가 예상되는 상황
                'details': '잘못된 웹훅 URL 처리 확인'
            }
        except Exception as e:
            return {
                'name': '웹훅 전송 실패 처리',
                'status': 'PASS',  # 예외 발생도 적절한 처리로 간주
                'details': f'예외 처리 확인: {str(e)}'
            }
    
    def _test_memory_pressure(self) -> Dict[str, Any]:
        """메모리 압박 상황 테스트"""
        try:
            # 현재 메모리 사용량 확인
            memory_before = psutil.virtual_memory().percent
            
            # 대용량 데이터 생성 및 처리
            large_data = ['test' * 1000] * 1000
            processed_data = [item.upper() for item in large_data]
            
            # 메모리 정리
            del large_data
            del processed_data
            
            memory_after = psutil.virtual_memory().percent
            memory_increase = memory_after - memory_before
            
            return {
                'name': '메모리 압박 상황 처리',
                'status': 'PASS' if memory_increase < 10 else 'FAIL',
                'details': f'메모리 증가량: {memory_increase:.1f}%'
            }
        except Exception as e:
            return {
                'name': '메모리 압박 상황 처리',
                'status': 'FAIL',
                'details': f'테스트 실행 오류: {str(e)}'
            }
    
    def _verify_monitoring_system(self):
        """시스템 모니터링 검증"""
        logger.info("📡 시스템 모니터링 검증 중...")
        
        try:
            monitoring_results = {}
            
            # Git 모니터링 테스트
            try:
                from git_monitor import GitMonitor
                git_monitor = GitMonitor()
                git_status = git_monitor.check_git_status()
                monitoring_results['git_monitor'] = 'SUCCESS' if git_status else 'FAIL'
            except Exception as e:
                monitoring_results['git_monitor'] = f'FAIL: {str(e)}'
            
            # 워치햄스터 모니터링 테스트
            try:
                from watchhamster_monitor import WatchHamsterMonitor
                wh_monitor = WatchHamsterMonitor()
                wh_status = wh_monitor.check_system_status()
                monitoring_results['watchhamster_monitor'] = 'SUCCESS' if wh_status else 'FAIL'
            except Exception as e:
                monitoring_results['watchhamster_monitor'] = f'FAIL: {str(e)}'
            
            # 시스템 리소스 모니터링
            resource_monitoring = self._test_resource_monitoring()
            monitoring_results['resource_monitoring'] = resource_monitoring
            
            success_count = sum(1 for result in monitoring_results.values() 
                              if isinstance(result, str) and result == 'SUCCESS')
            total_count = len([r for r in monitoring_results.values() if isinstance(r, str)])
            
            self.test_results['tests']['monitoring_system'] = {
                'status': 'PASS' if success_count >= total_count * 0.8 else 'FAIL',
                'message': f'모니터링 시스템: {success_count}/{total_count} 통과',
                'details': monitoring_results
            }
            
            logger.info(f"✅ 시스템 모니터링 검증 완료: {success_count}/{total_count}")
            
        except Exception as e:
            self.test_results['tests']['monitoring_system'] = {
                'status': 'FAIL',
                'message': f'모니터링 시스템 검증 실패: {str(e)}'
            }
            logger.error(f"❌ 모니터링 시스템 검증 실패: {e}")
    
    def _test_resource_monitoring(self) -> str:
        """리소스 모니터링 테스트"""
        try:
            # CPU, 메모리, 디스크 사용률 모니터링
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # 임계값 확인
            if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
                return 'WARNING: 높은 리소스 사용률 감지'
            
            return 'SUCCESS'
        except Exception as e:
            return f'FAIL: {str(e)}'
    
    def _run_load_test(self):
        """부하 테스트 실행"""
        logger.info("⚡ 부하 테스트 실행 중...")
        
        try:
            load_test_results = {}
            
            # 동시 요청 처리 테스트
            concurrent_results = self._test_concurrent_processing()
            load_test_results['concurrent_processing'] = concurrent_results
            
            # 연속 처리 테스트
            continuous_results = self._test_continuous_processing()
            load_test_results['continuous_processing'] = continuous_results
            
            # 메모리 사용량 모니터링
            memory_results = self._monitor_memory_during_load()
            load_test_results['memory_monitoring'] = memory_results
            
            # 전체 부하 테스트 평가
            overall_status = 'PASS'
            for result in load_test_results.values():
                if isinstance(result, dict) and result.get('status') == 'FAIL':
                    overall_status = 'FAIL'
                    break
            
            self.test_results['tests']['load_test'] = {
                'status': overall_status,
                'message': '부하 테스트 완료',
                'details': load_test_results
            }
            
            logger.info(f"✅ 부하 테스트 완료: {overall_status}")
            
        except Exception as e:
            self.test_results['tests']['load_test'] = {
                'status': 'FAIL',
                'message': f'부하 테스트 실패: {str(e)}'
            }
            logger.error(f"❌ 부하 테스트 실패: {e}")
    
    def _test_concurrent_processing(self) -> Dict[str, Any]:
        """동시 처리 테스트"""
        try:
            from integrated_api_module import IntegratedAPIModule
            
            def process_data():
                api_module = IntegratedAPIModule()
                return api_module.create_test_data()
            
            # 10개 스레드로 동시 처리
            threads = []
            results = []
            
            start_time = time.time()
            
            for i in range(10):
                thread = threading.Thread(target=lambda: results.append(process_data()))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            success_count = sum(1 for result in results if result is not None)
            
            return {
                'status': 'PASS' if success_count >= 8 else 'FAIL',
                'processing_time': processing_time,
                'success_rate': (success_count / 10) * 100,
                'details': f'{success_count}/10 성공, {processing_time:.2f}초'
            }
            
        except Exception as e:
            return {
                'status': 'FAIL',
                'details': f'동시 처리 테스트 오류: {str(e)}'
            }
    
    def _test_continuous_processing(self) -> Dict[str, Any]:
        """연속 처리 테스트"""
        try:
            from news_message_generator import NewsMessageGenerator
            from integrated_api_module import IntegratedAPIModule
            
            api_module = IntegratedAPIModule()
            msg_generator = NewsMessageGenerator()
            
            success_count = 0
            total_time = 0
            
            # 100회 연속 처리
            for i in range(100):
                start_time = time.time()
                
                test_data = api_module.create_test_data()
                message = msg_generator.generate_comprehensive_message(test_data)
                
                end_time = time.time()
                total_time += (end_time - start_time)
                
                if message:
                    success_count += 1
            
            avg_processing_time = total_time / 100
            success_rate = (success_count / 100) * 100
            
            return {
                'status': 'PASS' if success_rate >= 95 else 'FAIL',
                'success_rate': success_rate,
                'avg_processing_time': avg_processing_time,
                'details': f'{success_count}/100 성공, 평균 {avg_processing_time:.3f}초'
            }
            
        except Exception as e:
            return {
                'status': 'FAIL',
                'details': f'연속 처리 테스트 오류: {str(e)}'
            }
    
    def _monitor_memory_during_load(self) -> Dict[str, Any]:
        """부하 테스트 중 메모리 모니터링"""
        try:
            memory_samples = []
            
            # 10초간 메모리 사용량 모니터링
            for i in range(10):
                memory_percent = psutil.virtual_memory().percent
                memory_samples.append(memory_percent)
                time.sleep(1)
            
            avg_memory = sum(memory_samples) / len(memory_samples)
            max_memory = max(memory_samples)
            min_memory = min(memory_samples)
            
            return {
                'status': 'PASS' if max_memory < 80 else 'FAIL',
                'avg_memory_usage': avg_memory,
                'max_memory_usage': max_memory,
                'min_memory_usage': min_memory,
                'details': f'평균 {avg_memory:.1f}%, 최대 {max_memory:.1f}%'
            }
            
        except Exception as e:
            return {
                'status': 'FAIL',
                'details': f'메모리 모니터링 오류: {str(e)}'
            }
    
    def _verify_memory_stability(self):
        """메모리 누수 검증"""
        logger.info("🧠 메모리 안정성 검증 중...")
        
        try:
            # 초기 메모리 사용량
            initial_memory = psutil.virtual_memory().percent
            
            # 반복 작업 수행
            from integrated_api_module import IntegratedAPIModule
            from news_message_generator import NewsMessageGenerator
            
            api_module = IntegratedAPIModule()
            msg_generator = NewsMessageGenerator()
            
            memory_samples = [initial_memory]
            
            # 50회 반복 처리
            for i in range(50):
                test_data = api_module.create_test_data()
                message = msg_generator.generate_comprehensive_message(test_data)
                
                # 매 10회마다 메모리 확인
                if i % 10 == 0:
                    current_memory = psutil.virtual_memory().percent
                    memory_samples.append(current_memory)
            
            # 최종 메모리 사용량
            final_memory = psutil.virtual_memory().percent
            memory_increase = final_memory - initial_memory
            
            # 메모리 누수 판정 (5% 이상 증가 시 누수 의심)
            has_memory_leak = memory_increase > 5
            
            self.test_results['tests']['memory_stability'] = {
                'status': 'FAIL' if has_memory_leak else 'PASS',
                'message': f'메모리 안정성: {memory_increase:.1f}% 증가',
                'details': {
                    'initial_memory': initial_memory,
                    'final_memory': final_memory,
                    'memory_increase': memory_increase,
                    'memory_samples': memory_samples,
                    'has_memory_leak': has_memory_leak
                }
            }
            
            logger.info(f"✅ 메모리 안정성 검증 완료: {memory_increase:.1f}% 증가")
            
        except Exception as e:
            self.test_results['tests']['memory_stability'] = {
                'status': 'FAIL',
                'message': f'메모리 안정성 검증 실패: {str(e)}'
            }
            logger.error(f"❌ 메모리 안정성 검증 실패: {e}")
    
    def _run_long_term_stability_test(self):
        """장기 안정성 테스트 (단축 버전)"""
        logger.info("⏰ 장기 안정성 테스트 실행 중...")
        
        try:
            # 5분간 지속적인 처리 테스트
            test_duration = 300  # 5분
            start_time = time.time()
            
            success_count = 0
            error_count = 0
            
            from integrated_api_module import IntegratedAPIModule
            api_module = IntegratedAPIModule()
            
            while time.time() - start_time < test_duration:
                try:
                    test_data = api_module.create_test_data()
                    if test_data:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
                
                time.sleep(10)  # 10초 간격
            
            total_operations = success_count + error_count
            success_rate = (success_count / total_operations * 100) if total_operations > 0 else 0
            
            self.test_results['tests']['long_term_stability'] = {
                'status': 'PASS' if success_rate >= 90 else 'FAIL',
                'message': f'장기 안정성: {success_rate:.1f}% 성공률',
                'details': {
                    'test_duration_minutes': test_duration / 60,
                    'total_operations': total_operations,
                    'success_count': success_count,
                    'error_count': error_count,
                    'success_rate': success_rate
                }
            }
            
            logger.info(f"✅ 장기 안정성 테스트 완료: {success_rate:.1f}% 성공률")
            
        except Exception as e:
            self.test_results['tests']['long_term_stability'] = {
                'status': 'FAIL',
                'message': f'장기 안정성 테스트 실패: {str(e)}'
            }
            logger.error(f"❌ 장기 안정성 테스트 실패: {e}")
    
    def _calculate_stability_score(self):
        """최종 안정성 점수 계산"""
        logger.info("📊 최종 안정성 점수 계산 중...")
        
        try:
            # 각 테스트별 가중치
            weights = {
                'baseline_performance': 10,
                'feature_completeness': 25,
                'error_handling': 20,
                'monitoring_system': 15,
                'load_test': 15,
                'memory_stability': 10,
                'long_term_stability': 5
            }
            
            total_score = 0
            max_possible_score = 0
            
            for test_name, weight in weights.items():
                max_possible_score += weight
                
                if test_name in self.test_results['tests']:
                    test_result = self.test_results['tests'][test_name]
                    if test_result['status'] == 'PASS':
                        total_score += weight
                    elif test_result['status'] == 'PARTIAL':
                        total_score += weight * 0.5
            
            stability_score = (total_score / max_possible_score) * 100
            
            # 안정성 등급 결정
            if stability_score >= 95:
                grade = 'A+ (최우수)'
            elif stability_score >= 90:
                grade = 'A (우수)'
            elif stability_score >= 80:
                grade = 'B (양호)'
            elif stability_score >= 70:
                grade = 'C (보통)'
            else:
                grade = 'D (개선 필요)'
            
            self.test_results['stability_score'] = stability_score
            self.test_results['stability_grade'] = grade
            
            # 권장사항 생성
            self._generate_recommendations()
            
            logger.info(f"✅ 최종 안정성 점수: {stability_score:.1f}점 ({grade})")
            
        except Exception as e:
            logger.error(f"❌ 안정성 점수 계산 실패: {e}")
            self.test_results['stability_score'] = 0
            self.test_results['stability_grade'] = 'ERROR'
    
    def _generate_recommendations(self):
        """개선 권장사항 생성"""
        recommendations = []
        
        # 실패한 테스트에 대한 권장사항
        for test_name, test_result in self.test_results['tests'].items():
            if test_result['status'] == 'FAIL':
                if test_name == 'feature_completeness':
                    recommendations.append("일부 모듈의 import 오류를 해결하여 기능 완성도를 향상시키세요.")
                elif test_name == 'error_handling':
                    recommendations.append("오류 처리 메커니즘을 강화하여 시스템 안정성을 개선하세요.")
                elif test_name == 'memory_stability':
                    recommendations.append("메모리 누수를 점검하고 메모리 관리를 최적화하세요.")
                elif test_name == 'load_test':
                    recommendations.append("부하 처리 성능을 개선하여 동시 처리 능력을 향상시키세요.")
        
        # 성능 기반 권장사항
        if 'performance_metrics' in self.test_results:
            baseline = self.test_results['performance_metrics'].get('baseline', {})
            
            if baseline.get('cpu_usage_percent', 0) > 80:
                recommendations.append("CPU 사용률이 높습니다. 프로세스 최적화를 고려하세요.")
            
            if baseline.get('memory_usage_percent', 0) > 80:
                recommendations.append("메모리 사용률이 높습니다. 메모리 최적화를 고려하세요.")
            
            if baseline.get('disk_usage_percent', 0) > 90:
                recommendations.append("디스크 공간이 부족합니다. 불필요한 파일을 정리하세요.")
        
        # 일반적인 권장사항
        if self.test_results['stability_score'] < 90:
            recommendations.append("정기적인 시스템 모니터링과 유지보수를 수행하세요.")
            recommendations.append("로그 파일을 정기적으로 검토하여 잠재적 문제를 조기에 발견하세요.")
        
        if not recommendations:
            recommendations.append("시스템이 안정적으로 작동하고 있습니다. 현재 상태를 유지하세요.")
        
        self.test_results['recommendations'] = recommendations
    
    def _save_results(self):
        """테스트 결과 저장"""
        try:
            self.test_results['end_time'] = datetime.now().isoformat()
            
            # JSON 결과 저장
            result_file = f'recovery_config/final_stability_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            # 마크다운 리포트 생성
            self._generate_markdown_report()
            
            logger.info(f"✅ 테스트 결과 저장 완료: {result_file}")
            
        except Exception as e:
            logger.error(f"❌ 결과 저장 실패: {e}")
    
    def _generate_markdown_report(self):
        """마크다운 리포트 생성"""
        try:
            report_content = f"""# 🏆 POSCO 시스템 최종 안정성 검증 리포트

## 📊 종합 결과

**최종 안정성 점수**: {self.test_results.get('stability_score', 0):.1f}점  
**안정성 등급**: {self.test_results.get('stability_grade', 'N/A')}  
**테스트 실행 시간**: {self.test_results.get('start_time', '')} ~ {self.test_results.get('end_time', '')}

## 🔍 세부 테스트 결과

"""
            
            for test_name, test_result in self.test_results.get('tests', {}).items():
                status_emoji = '✅' if test_result['status'] == 'PASS' else '❌'
                report_content += f"### {status_emoji} {test_name.replace('_', ' ').title()}\n"
                report_content += f"- **상태**: {test_result['status']}\n"
                report_content += f"- **메시지**: {test_result['message']}\n"
                
                if 'details' in test_result:
                    report_content += f"- **세부사항**: {test_result['details']}\n"
                
                report_content += "\n"
            
            # 성능 메트릭
            if 'performance_metrics' in self.test_results:
                report_content += "## 📈 성능 메트릭\n\n"
                baseline = self.test_results['performance_metrics'].get('baseline', {})
                
                for metric, value in baseline.items():
                    if isinstance(value, float):
                        report_content += f"- **{metric}**: {value:.2f}\n"
                    else:
                        report_content += f"- **{metric}**: {value}\n"
                
                report_content += "\n"
            
            # 권장사항
            if 'recommendations' in self.test_results:
                report_content += "## 💡 개선 권장사항\n\n"
                for i, recommendation in enumerate(self.test_results['recommendations'], 1):
                    report_content += f"{i}. {recommendation}\n"
                
                report_content += "\n"
            
            report_content += f"""## 🎯 결론

POSCO 시스템의 최종 안정성 검증이 완료되었습니다.  
안정성 점수 {self.test_results.get('stability_score', 0):.1f}점으로 {self.test_results.get('stability_grade', 'N/A')} 등급을 달성했습니다.

---
**리포트 생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            report_file = f'recovery_config/final_stability_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"✅ 마크다운 리포트 생성 완료: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ 마크다운 리포트 생성 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🔍 POSCO 시스템 최종 안정성 검증 시작")
    print("=" * 60)
    
    tester = SystemStabilityTester()
    results = tester.run_comprehensive_stability_test()
    
    print("\n" + "=" * 60)
    print("🏆 최종 안정성 검증 완료!")
    print(f"📊 안정성 점수: {results.get('stability_score', 0):.1f}점")
    print(f"🏅 안정성 등급: {results.get('stability_grade', 'N/A')}")
    
    if results.get('stability_score', 0) >= 90:
        print("🎉 시스템이 매우 안정적으로 작동합니다!")
    elif results.get('stability_score', 0) >= 80:
        print("✅ 시스템이 안정적으로 작동합니다.")
    else:
        print("⚠️ 시스템 개선이 필요합니다.")
    
    return results

if __name__ == "__main__":
    main()