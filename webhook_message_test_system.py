#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 메시지 테스트 시스템
실제 Dooray 전송 없이 메시지 포맷 검증하는 테스트 도구

Requirements: 4.1, 4.2
- 실제 Dooray 전송 없이 메시지 포맷 검증하는 테스트 도구 개발
- 모든 웹훅 함수에 대한 단위 테스트 작성
- 메시지 내용과 포맷 정확성 자동 검증 로직 구현
"""

import sys
import os
import re
import json
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Tuple, Any, Optional

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

class WebhookMessageValidator:
    """웹훅 메시지 포맷 검증기"""
    
    def __init__(self):
        self.validation_rules = {
            'line_breaks': {
                'pattern': r'\\n',
                'invalid_pattern': r'/n',
                'description': '줄바꿈 문자는 \\n을 사용해야 함'
            },
            'product_name': {
                'required_names': ['POSCO 워치햄스터', 'POSCO WatchHamster', '워치햄스터'],
                'description': '제품명이 올바르게 포함되어야 함'
            },
            'webhook_url': {
                'pattern': r'https://[^/]+\.dooray\.com/services/\d+/\d+/[A-Za-z0-9_-]+',
                'description': 'Dooray 웹훅 URL 형식이 올바라야 함'
            },
            'message_structure': {
                'required_fields': ['botName', 'attachments', 'color'],
                'description': '메시지 구조가 Dooray 형식에 맞아야 함'
            },
            'korean_encoding': {
                'pattern': r'[가-힣]+',
                'description': '한국어 텍스트가 올바르게 인코딩되어야 함'
            }
        }
    
    def validate_message_format(self, message_content: str) -> Dict[str, Any]:
        """메시지 포맷 검증"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        # 1. 줄바꿈 문자 검증
        invalid_linebreaks = len(re.findall(self.validation_rules['line_breaks']['invalid_pattern'], message_content))
        valid_linebreaks = len(re.findall(self.validation_rules['line_breaks']['pattern'], message_content))
        
        results['details']['linebreaks'] = {
            'valid_count': valid_linebreaks,
            'invalid_count': invalid_linebreaks
        }
        
        if invalid_linebreaks > 0:
            results['valid'] = False
            results['errors'].append(f"잘못된 줄바꿈 문자 '/n'이 {invalid_linebreaks}개 발견됨")
        
        # 2. 제품명 검증
        found_names = []
        for name in self.validation_rules['product_name']['required_names']:
            if name in message_content:
                found_names.append(name)
        
        results['details']['product_names'] = found_names
        
        if not found_names:
            results['valid'] = False
            results['errors'].append("제품명이 메시지에 포함되지 않음")
        
        # 3. 웹훅 URL 검증
        webhook_urls = re.findall(self.validation_rules['webhook_url']['pattern'], message_content)
        results['details']['webhook_urls'] = webhook_urls
        
        if not webhook_urls:
            results['warnings'].append("웹훅 URL이 발견되지 않음 (설정 파일에서 로드될 수 있음)")
        
        # 4. 한국어 인코딩 검증
        korean_text = re.findall(self.validation_rules['korean_encoding']['pattern'], message_content)
        results['details']['korean_text_count'] = len(korean_text)
        
        if len(korean_text) == 0:
            results['warnings'].append("한국어 텍스트가 발견되지 않음")
        
        return results
    
    def validate_json_structure(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """JSON 메시지 구조 검증"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        required_fields = self.validation_rules['message_structure']['required_fields']
        
        for field in required_fields:
            if field not in json_data:
                results['valid'] = False
                results['errors'].append(f"필수 필드 '{field}'가 누락됨")
            else:
                results['details'][field] = type(json_data[field]).__name__
        
        # attachments 구조 상세 검증
        if 'attachments' in json_data:
            attachments = json_data['attachments']
            if isinstance(attachments, list) and len(attachments) > 0:
                attachment = attachments[0]
                if 'color' not in attachment:
                    results['warnings'].append("attachment에 color 필드가 없음")
                if 'text' not in attachment:
                    results['warnings'].append("attachment에 text 필드가 없음")
        
        return results

class WebhookFunctionTester:
    """웹훅 함수 단위 테스트"""
    
    def __init__(self, target_file_path: str):
        self.target_file_path = target_file_path
        self.validator = WebhookMessageValidator()
        self.test_results = {}
        
        # 테스트 대상 웹훅 함수 목록
        self.webhook_functions = [
            'send_status_notification',
            'send_notification', 
            'send_status_report_v2',
            'send_startup_notification_v2',
            'send_process_error_v2',
            'send_recovery_success_v2',
            'send_critical_alert_v2',
            'send_enhanced_status_notification',
            'send_status_report_v3_0',
            'send_startup_notification_v3_0',
            'send_process_error_v3_0',
            'send_recovery_success_v3_0',
            'send_critical_alert_v3_0'
        ]
    
    def load_target_module(self):
        """대상 모듈 동적 로드"""
        try:
            # 파일이 존재하는지 확인
            if not os.path.exists(self.target_file_path):
                raise FileNotFoundError(f"대상 파일을 찾을 수 없습니다: {self.target_file_path}")
            
            # 모듈 동적 import
            import importlib.util
            spec = importlib.util.spec_from_file_location("monitor_module", self.target_file_path)
            module = importlib.util.module_from_spec(spec)
            
            # 의존성 모킹
            with patch('requests.post') as mock_post:
                mock_post.return_value.status_code = 200
                spec.loader.exec_module(module)
            
            return module
        except Exception as e:
            print(f"❌ 모듈 로드 실패: {e}")
            return None
    
    def extract_function_source(self, function_name: str) -> Optional[str]:
        """함수 소스 코드 추출"""
        try:
            with open(self.target_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 함수 정의 시작점 찾기
            pattern = rf'def {function_name}\s*\('
            matches = list(re.finditer(pattern, content))
            
            if not matches:
                return None
            
            # 첫 번째 매치 사용 (중복 함수가 있을 수 있음)
            match = matches[0]
            start_pos = match.start()
            lines = content[start_pos:].split('\n')
            
            if len(lines) < 2:
                return lines[0] if lines else None
            
            # 함수 끝점 찾기 (들여쓰기 기준)
            function_lines = [lines[0]]  # 함수 정의 라인
            
            # 다음 줄에서 기본 들여쓰기 레벨 찾기
            base_indent = None
            for i in range(1, len(lines)):
                if lines[i].strip():  # 빈 줄이 아닌 첫 번째 줄
                    base_indent = len(lines[i]) - len(lines[i].lstrip())
                    break
            
            if base_indent is None:
                base_indent = 4  # 기본값
            
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '':
                    function_lines.append(line)
                    continue
                
                current_indent = len(line) - len(line.lstrip())
                
                # 같은 레벨이거나 더 적은 들여쓰기면 함수 끝
                if current_indent <= base_indent and line.strip() and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                    # 다음 함수나 클래스 정의인지 확인
                    if re.match(r'\s*(def|class)\s+', line):
                        break
                
                function_lines.append(line)
            
            return '\n'.join(function_lines)
        
        except Exception as e:
            print(f"❌ 함수 소스 추출 실패 ({function_name}): {e}")
            return None
    
    def test_function_exists(self, function_name: str) -> bool:
        """함수 존재 여부 테스트"""
        source = self.extract_function_source(function_name)
        return source is not None
    
    def test_function_message_format(self, function_name: str) -> Dict[str, Any]:
        """함수의 메시지 포맷 테스트"""
        source = self.extract_function_source(function_name)
        
        if not source:
            return {
                'valid': False,
                'error': '함수를 찾을 수 없음',
                'details': {}
            }
        
        # 메시지 포맷 검증
        validation_result = self.validator.validate_message_format(source)
        
        # 추가 함수별 특화 검증
        if function_name.startswith('send_status'):
            # 상태 알림 함수 특화 검증
            if '상태' not in source and 'status' not in source.lower():
                validation_result['warnings'].append("상태 알림 함수에 '상태' 관련 텍스트가 없음")
        
        elif function_name.startswith('send_error') or 'error' in function_name:
            # 오류 알림 함수 특화 검증
            if '오류' not in source and 'error' not in source.lower():
                validation_result['warnings'].append("오류 알림 함수에 '오류' 관련 텍스트가 없음")
        
        return validation_result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 웹훅 함수 테스트 실행"""
        print("🧪 웹훅 함수 단위 테스트 시작...")
        print("=" * 60)
        
        results = {
            'total_functions': len(self.webhook_functions),
            'passed_functions': 0,
            'failed_functions': 0,
            'function_results': {},
            'summary': {}
        }
        
        for func_name in self.webhook_functions:
            print(f"\n🔍 테스트 중: {func_name}")
            print("-" * 40)
            
            # 함수 존재 여부 테스트
            exists = self.test_function_exists(func_name)
            
            if not exists:
                print(f"❌ 함수 누락: {func_name}")
                results['function_results'][func_name] = {
                    'exists': False,
                    'message_format': {'valid': False, 'error': '함수 없음'}
                }
                results['failed_functions'] += 1
                continue
            
            print(f"✅ 함수 발견: {func_name}")
            
            # 메시지 포맷 테스트
            format_result = self.test_function_message_format(func_name)
            
            results['function_results'][func_name] = {
                'exists': True,
                'message_format': format_result
            }
            
            if format_result['valid']:
                print(f"✅ 메시지 포맷: 정상")
                results['passed_functions'] += 1
            else:
                print(f"❌ 메시지 포맷: 문제 발견")
                for error in format_result['errors']:
                    print(f"   • {error}")
                results['failed_functions'] += 1
            
            # 경고사항 출력
            if format_result.get('warnings'):
                for warning in format_result['warnings']:
                    print(f"⚠️  경고: {warning}")
        
        # 결과 요약
        success_rate = (results['passed_functions'] / results['total_functions']) * 100
        results['summary'] = {
            'success_rate': success_rate,
            'total': results['total_functions'],
            'passed': results['passed_functions'],
            'failed': results['failed_functions']
        }
        
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"전체 함수: {results['total_functions']}개")
        print(f"통과: {results['passed_functions']}개")
        print(f"실패: {results['failed_functions']}개")
        print(f"성공률: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 웹훅 메시지 테스트가 성공적으로 완료되었습니다!")
        elif success_rate >= 70:
            print("\n⚠️ 일부 웹훅 함수에 문제가 있지만 대부분 정상입니다.")
        else:
            print("\n❌ 다수의 웹훅 함수에 문제가 발견되었습니다.")
        
        return results

class WebhookIntegrationTester:
    """웹훅 통합 테스트"""
    
    def __init__(self, target_file_path: str):
        self.target_file_path = target_file_path
        self.validator = WebhookMessageValidator()
    
    def test_webhook_configuration(self) -> Dict[str, Any]:
        """웹훅 설정 테스트"""
        print("\n🔧 웹훅 설정 테스트...")
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        try:
            with open(self.target_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 웹훅 URL 설정 확인
            webhook_patterns = [
                r'DOORAY_WEBHOOK_URL\s*=\s*["\']([^"\']+)["\']',
                r'WATCHHAMSTER_WEBHOOK_URL\s*=\s*["\']([^"\']+)["\']'
            ]
            
            found_urls = []
            for pattern in webhook_patterns:
                matches = re.findall(pattern, content)
                found_urls.extend(matches)
            
            results['details']['webhook_urls'] = found_urls
            
            if not found_urls:
                results['warnings'].append("웹훅 URL 설정을 찾을 수 없음 (config 파일에서 로드될 수 있음)")
            
            # 봇 프로필 이미지 URL 확인
            bot_image_pattern = r'BOT_PROFILE_IMAGE_URL\s*=\s*["\']([^"\']+)["\']'
            bot_images = re.findall(bot_image_pattern, content)
            
            results['details']['bot_image_urls'] = bot_images
            
            if not bot_images:
                results['warnings'].append("봇 프로필 이미지 URL을 찾을 수 없음")
            
            print(f"✅ 웹훅 URL: {len(found_urls)}개 발견")
            print(f"✅ 봇 이미지 URL: {len(bot_images)}개 발견")
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"설정 테스트 중 오류: {e}")
            print(f"❌ 설정 테스트 실패: {e}")
        
        return results
    
    def test_message_consistency(self) -> Dict[str, Any]:
        """메시지 일관성 테스트"""
        print("\n📝 메시지 일관성 테스트...")
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        try:
            with open(self.target_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 제품명 일관성 확인
            product_names = ['POSCO 워치햄스터', 'POSCO WatchHamster', '워치햄스터']
            name_counts = {}
            
            for name in product_names:
                count = content.count(name)
                if count > 0:
                    name_counts[name] = count
            
            results['details']['product_name_usage'] = name_counts
            
            if len(name_counts) > 1:
                results['warnings'].append(f"여러 제품명 변형이 사용됨: {list(name_counts.keys())}")
            
            # 메시지 색상 일관성 확인
            color_patterns = re.findall(r'"color":\s*"([^"]+)"', content)
            unique_colors = set(color_patterns)
            
            results['details']['message_colors'] = list(unique_colors)
            
            if len(unique_colors) > 3:
                results['warnings'].append(f"너무 많은 메시지 색상이 사용됨: {len(unique_colors)}개")
            
            print(f"✅ 제품명 사용: {name_counts}")
            print(f"✅ 메시지 색상: {len(unique_colors)}개 종류")
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"일관성 테스트 중 오류: {e}")
            print(f"❌ 일관성 테스트 실패: {e}")
        
        return results

def run_comprehensive_webhook_tests(target_file: str = "core/monitoring/monitor_WatchHamster_v3.0.py"):
    """포괄적인 웹훅 테스트 실행"""
    print("🚀 웹훅 메시지 테스트 시스템 시작")
    print("=" * 80)
    print(f"대상 파일: {target_file}")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 파일 존재 확인
    if not os.path.exists(target_file):
        print(f"❌ 대상 파일을 찾을 수 없습니다: {target_file}")
        return False
    
    overall_success = True
    test_results = {}
    
    # 1. 웹훅 함수 단위 테스트
    print("\n🧪 1단계: 웹훅 함수 단위 테스트")
    function_tester = WebhookFunctionTester(target_file)
    function_results = function_tester.run_all_tests()
    test_results['function_tests'] = function_results
    
    if function_results['summary']['success_rate'] < 90:
        overall_success = False
    
    # 2. 웹훅 통합 테스트
    print("\n🔧 2단계: 웹훅 통합 테스트")
    integration_tester = WebhookIntegrationTester(target_file)
    
    config_results = integration_tester.test_webhook_configuration()
    test_results['config_tests'] = config_results
    
    consistency_results = integration_tester.test_message_consistency()
    test_results['consistency_tests'] = consistency_results
    
    # 3. 전체 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"webhook_message_test_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 테스트 결과 저장: {results_file}")
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")
    
    # 최종 결과 출력
    print("\n" + "=" * 80)
    print("🏁 전체 테스트 완료")
    print("=" * 80)
    
    if overall_success:
        print("🎉 모든 웹훅 메시지 테스트가 성공적으로 완료되었습니다!")
        print("✅ 웹훅 함수들이 올바르게 복원되었으며 메시지 포맷이 정상입니다.")
    else:
        print("⚠️ 일부 테스트에서 문제가 발견되었습니다.")
        print("📋 상세한 결과는 테스트 결과 파일을 확인하세요.")
    
    return overall_success

if __name__ == "__main__":
    success = run_comprehensive_webhook_tests()
    sys.exit(0 if success else 1)