#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MessageTemplateEngine 테스트 스크립트
메시지 템플릿 엔진의 모든 기능을 테스트

테스트 항목:
- 📰 모든 메시지 타입 생성 테스트
- 🎨 메시지 포맷팅 테스트
- 📊 데이터 변환 테스트
- 👀 미리보기 기능 테스트
- 💾 템플릿 저장/로드 테스트
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from message_template_engine import MessageTemplateEngine, MessageType, MessagePriority
    from message_template_engine import (
        create_deployment_success_message,
        create_deployment_failure_message,
        create_data_update_message,
        preview_message_template
    )
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class MessageTemplateEngineTest:
    """MessageTemplateEngine 테스트 클래스"""
    
    def __init__(self):
        """테스트 초기화"""
        self.engine = MessageTemplateEngine()
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
        print("🧪 MessageTemplateEngine 테스트 시작...")
        print("=" * 60)
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        try:
            # 기본 기능 테스트
            self.test_engine_initialization()
            self.test_template_loading()
            self.test_available_templates()
            
            # 메시지 생성 테스트
            self.test_deployment_success_message()
            self.test_deployment_failure_message()
            self.test_deployment_start_message()
            self.test_data_update_message()
            self.test_system_status_message()
            self.test_error_alert_message()
            self.test_maintenance_message()
            
            # 편의 함수 테스트
            self.test_convenience_functions()
            
            # 미리보기 기능 테스트
            self.test_preview_functionality()
            
            # 오류 처리 테스트
            self.test_error_handling()
            
            # 템플릿 정보 테스트
            self.test_template_info()
            
            # 결과 출력
            self.print_test_results()
            
        except Exception as e:
            print(f"❌ 테스트 실행 중 예외 발생: {e}")
            return False
        
        return self.failed_tests == 0
    
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        """테스트 결과 검증"""
        if condition:
            self.passed_tests += 1
            status = "✅ PASS"
            print(f"{status} {test_name}")
            if details:
                print(f"    {details}")
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            print(f"{status} {test_name}")
            if details:
                print(f"    {details}")
        
        self.test_results.append({
            'name': test_name,
            'status': status,
            'details': details,
            'passed': condition
        })
    
    def test_engine_initialization(self):
        """엔진 초기화 테스트"""
        print("\n🔧 엔진 초기화 테스트")
        
        # 엔진 객체 생성 확인
        self.assert_test(
            self.engine is not None,
            "엔진 객체 생성",
            "MessageTemplateEngine 인스턴스가 정상적으로 생성됨"
        )
        
        # 브랜드 설정 확인
        self.assert_test(
            'company_name' in self.engine.brand_config,
            "브랜드 설정 로드",
            f"회사명: {self.engine.brand_config.get('company_name')}"
        )
        
        # 템플릿 로드 확인
        self.assert_test(
            len(self.engine.templates) > 0,
            "기본 템플릿 로드",
            f"로드된 템플릿 수: {len(self.engine.templates)}"
        )
    
    def test_template_loading(self):
        """템플릿 로딩 테스트"""
        print("\n📋 템플릿 로딩 테스트")
        
        # 모든 메시지 타입에 대한 템플릿 존재 확인
        for message_type in MessageType:
            template_exists = message_type.value in self.engine.templates
            self.assert_test(
                template_exists,
                f"{message_type.value} 템플릿 존재",
                f"템플릿 키: {message_type.value}"
            )
    
    def test_available_templates(self):
        """사용 가능한 템플릿 목록 테스트"""
        print("\n📝 사용 가능한 템플릿 테스트")
        
        available_templates = self.engine.get_available_templates()
        
        self.assert_test(
            len(available_templates) > 0,
            "템플릿 목록 조회",
            f"사용 가능한 템플릿: {len(available_templates)}개"
        )
        
        # 각 메시지 타입이 목록에 있는지 확인
        for message_type in MessageType:
            self.assert_test(
                message_type.value in available_templates,
                f"{message_type.value} 템플릿 목록 포함",
                ""
            )
    
    def test_deployment_success_message(self):
        """배포 성공 메시지 테스트"""
        print("\n✅ 배포 성공 메시지 테스트")
        
        test_data = {
            'deployment_id': 'deploy_test_001',
            'start_time': '2025-09-01T14:30:22',
            'end_time': '2025-09-01T14:32:45',
            'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 
                              'merge_main', 'commit_changes', 'push_remote', 'pages_verification'],
            'github_pages_accessible': True
        }
        
        try:
            message = self.engine.generate_deployment_success_message(test_data)
            
            self.assert_test(
                'title' in message and 'body' in message,
                "배포 성공 메시지 생성",
                f"제목 길이: {len(message.get('title', ''))}, 본문 길이: {len(message.get('body', ''))}"
            )
            
            self.assert_test(
                'deploy_test_001' in message.get('body', ''),
                "배포 ID 포함 확인",
                "메시지에 배포 ID가 포함됨"
            )
            
            self.assert_test(
                message.get('priority') == MessagePriority.NORMAL.value,
                "우선순위 설정 확인",
                f"우선순위: {message.get('priority')}"
            )
            
        except Exception as e:
            self.assert_test(False, "배포 성공 메시지 생성", f"예외 발생: {e}")
    
    def test_deployment_failure_message(self):
        """배포 실패 메시지 테스트"""
        print("\n❌ 배포 실패 메시지 테스트")
        
        test_data = {
            'deployment_id': 'deploy_test_002',
            'error_message': 'Git 푸시 중 인증 실패',
            'steps_completed': ['status_check', 'backup_creation'],
            'rollback_performed': True
        }
        
        try:
            message = self.engine.generate_deployment_failure_message(test_data)
            
            self.assert_test(
                'title' in message and 'body' in message,
                "배포 실패 메시지 생성",
                f"제목 길이: {len(message.get('title', ''))}, 본문 길이: {len(message.get('body', ''))}"
            )
            
            self.assert_test(
                'Git 푸시 중 인증 실패' in message.get('body', ''),
                "오류 메시지 포함 확인",
                "메시지에 오류 내용이 포함됨"
            )
            
            self.assert_test(
                message.get('priority') == MessagePriority.HIGH.value,
                "높은 우선순위 설정 확인",
                f"우선순위: {message.get('priority')}"
            )
            
        except Exception as e:
            self.assert_test(False, "배포 실패 메시지 생성", f"예외 발생: {e}")
    
    def test_deployment_start_message(self):
        """배포 시작 메시지 테스트"""
        print("\n🚀 배포 시작 메시지 테스트")
        
        try:
            message = self.engine.generate_deployment_start_message('deploy_test_003')
            
            self.assert_test(
                'title' in message and 'body' in message,
                "배포 시작 메시지 생성",
                f"제목 길이: {len(message.get('title', ''))}, 본문 길이: {len(message.get('body', ''))}"
            )
            
            self.assert_test(
                'deploy_test_003' in message.get('body', ''),
                "배포 ID 포함 확인",
                "메시지에 배포 ID가 포함됨"
            )
            
        except Exception as e:
            self.assert_test(False, "배포 시작 메시지 생성", f"예외 발생: {e}")
    
    def test_data_update_message(self):
        """데이터 업데이트 메시지 테스트"""
        print("\n📊 데이터 업데이트 메시지 테스트")
        
        test_data = {
            'kospi': '2,485.67',
            'kospi_change': 15.23,
            'exchange_rate': '1,342.50',
            'exchange_change': -2.80,
            'posco_stock': '285,000',
            'posco_change': 5000,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            message = self.engine.generate_data_update_message(test_data)
            
            self.assert_test(
                'title' in message and 'body' in message,
                "데이터 업데이트 메시지 생성",
                f"제목 길이: {len(message.get('title', ''))}, 본문 길이: {len(message.get('body', ''))}"
            )
            
            self.assert_test(
                '2,485.67' in message.get('body', ''),
                "KOSPI 데이터 포함 확인",
                "메시지에 KOSPI 데이터가 포함됨"
            )
            
            self.assert_test(
                '▲ +15.23' in message.get('body', ''),
                "변화량 포맷팅 확인",
                "양수 변화량이 올바르게 포맷팅됨"
            )
            
        except Exception as e:
            self.assert_test(False, "데이터 업데이트 메시지 생성", f"예외 발생: {e}")
    
    def test_system_status_message(self):
        """시스템 상태 메시지 테스트"""
        print("\n📈 시스템 상태 메시지 테스트")
        
        test_data = {
            'total_deployments': 127,
            'success_rate': 94.5,
            'last_success': '2025-09-01 14:32:45',
            'avg_deployment_time': 2.3,
            'github_accessible': True,
            'data_collection_active': True,
            'webhook_active': True,
            'next_update': '2025-09-01 16:00:00'
        }
        
        try:
            message = self.engine.generate_system_status_message(test_data)
            
            self.assert_test(
                'title' in message and 'body' in message,
                "시스템 상태 메시지 생성",
                f"제목 길이: {len(message.get('title', ''))}, 본문 길이: {len(message.get('body', ''))}"
            )
            
            self.assert_test(
                '127' in message.get('body', '') and '94.5%' in message.get('body', ''),
                "통계 데이터 포함 확인",
                "메시지에 배포 통계가 포함됨"
            )
            
        except Exception as e:
            self.assert_test(False, "시스템 상태 메시지 생성", f"예외 발생: {e}")
    
    def test_error_alert_message(self):
        """오류 알림 메시지 테스트"""
        print("\n🚨 오류 알림 메시지 테스트")
        
        test_data = {
            'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error_type': 'Database Connection Error',
            'impact_scope': 'Data Collection Module',
            'error_details': 'Connection timeout after 30 seconds',
            'auto_recovery_status': '시도 중',
            'estimated_recovery_time': '5-10분'
        }
        
        try:
            message = self.engine.generate_message(MessageType.ERROR_ALERT, test_data)
            
            self.assert_test(
                'title' in message and 'body' in message,
                "오류 알림 메시지 생성",
                f"제목 길이: {len(message.get('title', ''))}, 본문 길이: {len(message.get('body', ''))}"
            )
            
            self.assert_test(
                message.get('priority') == MessagePriority.CRITICAL.value,
                "중요 우선순위 설정 확인",
                f"우선순위: {message.get('priority')}"
            )
            
        except Exception as e:
            self.assert_test(False, "오류 알림 메시지 생성", f"예외 발생: {e}")
    
    def test_maintenance_message(self):
        """점검 안내 메시지 테스트"""
        print("\n🔧 점검 안내 메시지 테스트")
        
        test_data = {
            'maintenance_start': '2025-09-02 02:00:00',
            'maintenance_end': '2025-09-02 04:00:00',
            'maintenance_duration': '약 2시간',
            'maintenance_details': '시스템 보안 업데이트 및 성능 최적화'
        }
        
        try:
            message = self.engine.generate_message(MessageType.MAINTENANCE, test_data)
            
            self.assert_test(
                'title' in message and 'body' in message,
                "점검 안내 메시지 생성",
                f"제목 길이: {len(message.get('title', ''))}, 본문 길이: {len(message.get('body', ''))}"
            )
            
            self.assert_test(
                '02:00:00' in message.get('body', ''),
                "점검 시간 포함 확인",
                "메시지에 점검 시간이 포함됨"
            )
            
        except Exception as e:
            self.assert_test(False, "점검 안내 메시지 생성", f"예외 발생: {e}")
    
    def test_convenience_functions(self):
        """편의 함수 테스트"""
        print("\n🛠️ 편의 함수 테스트")
        
        # 배포 성공 메시지 편의 함수
        try:
            test_result = {
                'deployment_id': 'convenience_test_001',
                'start_time': '2025-09-01T14:30:22',
                'end_time': '2025-09-01T14:32:45',
                'steps_completed': ['status_check', 'push_remote'],
                'github_pages_accessible': True
            }
            
            message = create_deployment_success_message(test_result)
            self.assert_test(
                'title' in message and 'body' in message,
                "배포 성공 편의 함수",
                "create_deployment_success_message 함수 정상 작동"
            )
            
        except Exception as e:
            self.assert_test(False, "배포 성공 편의 함수", f"예외 발생: {e}")
        
        # 배포 실패 메시지 편의 함수
        try:
            test_result = {
                'deployment_id': 'convenience_test_002',
                'error_message': '테스트 오류',
                'steps_completed': ['status_check'],
                'rollback_performed': False
            }
            
            message = create_deployment_failure_message(test_result)
            self.assert_test(
                'title' in message and 'body' in message,
                "배포 실패 편의 함수",
                "create_deployment_failure_message 함수 정상 작동"
            )
            
        except Exception as e:
            self.assert_test(False, "배포 실패 편의 함수", f"예외 발생: {e}")
        
        # 데이터 업데이트 편의 함수
        try:
            test_data = {
                'kospi': '2,500.00',
                'kospi_change': 10.0,
                'exchange_rate': '1,350.00',
                'exchange_change': 5.0
            }
            
            message = create_data_update_message(test_data)
            self.assert_test(
                'title' in message and 'body' in message,
                "데이터 업데이트 편의 함수",
                "create_data_update_message 함수 정상 작동"
            )
            
        except Exception as e:
            self.assert_test(False, "데이터 업데이트 편의 함수", f"예외 발생: {e}")
    
    def test_preview_functionality(self):
        """미리보기 기능 테스트"""
        print("\n👀 미리보기 기능 테스트")
        
        test_data = {
            'deployment_id': 'preview_test_001',
            'steps_completed': 5,
            'duration': '2.3초'
        }
        
        try:
            preview = self.engine.preview_message(MessageType.DEPLOYMENT_SUCCESS, test_data)
            
            self.assert_test(
                len(preview) > 0,
                "미리보기 생성",
                f"미리보기 길이: {len(preview)} 문자"
            )
            
            self.assert_test(
                '미리보기' in preview,
                "미리보기 헤더 포함",
                "미리보기에 적절한 헤더가 포함됨"
            )
            
        except Exception as e:
            self.assert_test(False, "미리보기 생성", f"예외 발생: {e}")
        
        # 편의 함수 미리보기 테스트
        try:
            preview = preview_message_template('deployment_success', test_data)
            self.assert_test(
                len(preview) > 0,
                "편의 함수 미리보기",
                "preview_message_template 함수 정상 작동"
            )
            
        except Exception as e:
            self.assert_test(False, "편의 함수 미리보기", f"예외 발생: {e}")
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        print("\n🚫 오류 처리 테스트")
        
        # 잘못된 메시지 타입
        try:
            invalid_preview = preview_message_template('invalid_type', {})
            self.assert_test(
                '지원하지 않는' in invalid_preview,
                "잘못된 메시지 타입 처리",
                "잘못된 메시지 타입에 대한 적절한 오류 메시지"
            )
        except Exception as e:
            self.assert_test(False, "잘못된 메시지 타입 처리", f"예외 발생: {e}")
        
        # 누락된 필수 필드
        try:
            incomplete_data = {}  # 필수 필드 누락
            message = self.engine.generate_message(MessageType.DEPLOYMENT_SUCCESS, incomplete_data)
            
            self.assert_test(
                'title' in message and 'body' in message,
                "누락된 필드 처리",
                "누락된 필드가 있어도 메시지 생성됨 (오류 메시지 또는 기본값)"
            )
            
        except Exception as e:
            self.assert_test(False, "누락된 필드 처리", f"예외 발생: {e}")
    
    def test_template_info(self):
        """템플릿 정보 테스트"""
        print("\n📋 템플릿 정보 테스트")
        
        try:
            info = self.engine.get_template_info(MessageType.DEPLOYMENT_SUCCESS)
            
            self.assert_test(
                'type' in info and 'priority' in info,
                "템플릿 정보 조회",
                f"템플릿 타입: {info.get('type')}, 우선순위: {info.get('priority')}"
            )
            
            self.assert_test(
                'required_fields' in info and isinstance(info['required_fields'], list),
                "필수 필드 목록 조회",
                f"필수 필드 수: {len(info.get('required_fields', []))}"
            )
            
        except Exception as e:
            self.assert_test(False, "템플릿 정보 조회", f"예외 발생: {e}")
    
    def print_test_results(self):
        """테스트 결과 출력"""
        print("\n" + "=" * 60)
        print("🧪 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"총 테스트: {total_tests}개")
        print(f"성공: {self.passed_tests}개")
        print(f"실패: {self.failed_tests}개")
        print(f"성공률: {success_rate:.1f}%")
        
        if self.failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  • {result['name']}")
                    if result['details']:
                        print(f"    {result['details']}")
        
        print("\n" + "=" * 60)
        
        if self.failed_tests == 0:
            print("🎉 모든 테스트가 성공했습니다!")
        else:
            print(f"⚠️ {self.failed_tests}개의 테스트가 실패했습니다.")


def main():
    """메인 함수"""
    print("🧪 MessageTemplateEngine 테스트 스크립트")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 테스트 실행
    tester = MessageTemplateEngineTest()
    success = tester.run_all_tests()
    
    # 종료 코드 설정
    exit_code = 0 if success else 1
    
    print(f"\n🏁 테스트 완료 (종료 코드: {exit_code})")
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)