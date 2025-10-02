#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 통합 테스트 - Task 9 완료 검증
MessageTemplateEngine 통합 및 고객 친화적 메시지 변환 종합 테스트

Requirements: 2.1, 2.2 완전 구현 검증
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from posco_main_notifier import PoscoMainNotifier
    from message_template_engine import MessageType, MessageTemplateEngine
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class WebhookIntegrationTester:
    """웹훅 통합 테스트 클래스"""
    
    def __init__(self):
        self.notifier = PoscoMainNotifier()
        self.message_engine = MessageTemplateEngine()
        self.test_results = []
        
        # 테스트용 웹훅 URL 설정
        self.notifier.webhook_url = "https://httpbin.org/post"
        
        print("🧪 웹훅 통합 테스트 시스템 초기화 완료")
    
    def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        print("🚀 웹훅 통합 테스트 시작...")
        print("=" * 60)
        
        test_methods = [
            ("MessageTemplateEngine 통합 테스트", self.test_template_engine_integration),
            ("고객 친화적 메시지 변환 테스트", self.test_customer_friendly_conversion),
            ("GUI 상태 모니터링 콜백 테스트", self.test_gui_status_callback),
            ("배포 알림 자동화 테스트", self.test_deployment_notification_automation),
            ("오류 처리 및 복구 테스트", self.test_error_handling),
            ("웹훅 설정 파일 통합 테스트", self.test_webhook_config_integration),
            ("메시지 미리보기 기능 테스트", self.test_message_preview),
            ("실시간 로깅 시스템 테스트", self.test_realtime_logging),
            ("전체 파이프라인 통합 테스트", self.test_full_pipeline_integration)
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n📋 {test_name}")
            print("-" * 50)
            
            try:
                result = test_method()
                if result:
                    print(f"✅ {test_name} 통과")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name} 실패")
                
                self.test_results.append({
                    'name': test_name,
                    'passed': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"💥 {test_name} 예외 발생: {e}")
                self.test_results.append({
                    'name': test_name,
                    'passed': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # 최종 결과
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"총 테스트: {total_tests}")
        print(f"통과: {passed_tests}")
        print(f"실패: {total_tests - passed_tests}")
        print(f"성공률: {(passed_tests / total_tests) * 100:.1f}%")
        
        # Requirements 검증
        self.verify_requirements()
        
        return passed_tests == total_tests
    
    def test_template_engine_integration(self) -> bool:
        """MessageTemplateEngine 통합 테스트"""
        try:
            # 배포 성공 메시지 테스트
            deployment_result = {
                'deployment_id': 'integration_test_001',
                'start_time': '2025-09-23T14:00:00',
                'end_time': '2025-09-23T14:02:30',
                'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 'merge_main', 'commit_changes', 'push_remote'],
                'success': True,
                'github_pages_accessible': True
            }
            
            webhook_result = self.notifier.send_direct_webhook(
                deployment_result=deployment_result,
                message_type=MessageType.DEPLOYMENT_SUCCESS
            )
            
            # 검증
            assert webhook_result['success'], "웹훅 전송 실패"
            assert webhook_result.get('template_used'), "템플릿 사용 정보 없음"
            assert webhook_result['template_used']['type'] == 'deployment_success', "잘못된 템플릿 타입"
            assert webhook_result.get('message_sent'), "전송된 메시지 없음"
            
            print("  ✓ 배포 성공 메시지 템플릿 적용 완료")
            
            # 배포 실패 메시지 테스트
            deployment_result['success'] = False
            deployment_result['error_message'] = '테스트 오류'
            
            webhook_result = self.notifier.send_direct_webhook(
                deployment_result=deployment_result,
                message_type=MessageType.DEPLOYMENT_FAILURE
            )
            
            assert webhook_result['success'], "실패 메시지 웹훅 전송 실패"
            assert webhook_result['template_used']['type'] == 'deployment_failure', "실패 템플릿 타입 오류"
            
            print("  ✓ 배포 실패 메시지 템플릿 적용 완료")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 템플릿 엔진 통합 테스트 실패: {e}")
            return False
    
    def test_customer_friendly_conversion(self) -> bool:
        """고객 친화적 메시지 변환 테스트"""
        try:
            # 기술적 용어가 포함된 메시지
            technical_message = """
            Git 저장소에서 commit을 push하는 중 오류가 발생했습니다.
            GitHub Pages 배포 pipeline에서 rollback을 수행했습니다.
            webhook API 호출이 실패했습니다.
            """
            
            # 변환 테스트
            friendly_message = self.notifier._convert_to_customer_friendly(technical_message)
            
            # 변환 확인
            conversions = [
                ('Git 저장소', '시스템 데이터'),
                ('commit', '저장'),
                ('push', '업로드'),
                ('GitHub Pages', 'POSCO 분석 웹사이트'),
                ('pipeline', '처리 과정'),
                ('rollback', '이전 상태 복구'),
                ('webhook', '알림 시스템'),
                ('API', '데이터 연결')
            ]
            
            conversion_count = 0
            for original, converted in conversions:
                if original in technical_message and converted in friendly_message:
                    conversion_count += 1
                    print(f"  ✓ '{original}' → '{converted}' 변환 완료")
            
            # 최소 80% 변환 성공 요구
            success_rate = (conversion_count / len(conversions)) * 100
            assert success_rate >= 80, f"변환 성공률 부족: {success_rate}%"
            
            print(f"  ✓ 고객 친화적 변환 성공률: {success_rate}%")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 고객 친화적 변환 테스트 실패: {e}")
            return False
    
    def test_gui_status_callback(self) -> bool:
        """GUI 상태 모니터링 콜백 테스트"""
        try:
            callback_calls = []
            
            def test_callback(message: str, progress: int):
                callback_calls.append({
                    'message': message,
                    'progress': progress,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"  📊 콜백: {progress}% - {message}")
            
            # 콜백과 함께 웹훅 전송
            deployment_result = {
                'deployment_id': 'callback_test_001',
                'success': True,
                'steps_completed': ['status_check', 'backup_creation']
            }
            
            webhook_result = self.notifier.send_direct_webhook(
                deployment_result=deployment_result,
                message_type=MessageType.DEPLOYMENT_SUCCESS,
                status_callback=test_callback
            )
            
            # 콜백 호출 검증
            assert len(callback_calls) > 0, "콜백이 호출되지 않음"
            assert any(call['progress'] == 100 for call in callback_calls), "완료 콜백 없음"
            assert webhook_result['success'], "웹훅 전송 실패"
            
            print(f"  ✓ 총 {len(callback_calls)}개 콜백 호출 완료")
            print(f"  ✓ 진행률 범위: {min(call['progress'] for call in callback_calls)}% - {max(call['progress'] for call in callback_calls)}%")
            
            return True
            
        except Exception as e:
            print(f"  ❌ GUI 상태 콜백 테스트 실패: {e}")
            return False
    
    def test_deployment_notification_automation(self) -> bool:
        """배포 알림 자동화 테스트"""
        try:
            # 성공 알림 테스트
            success_result = {
                'deployment_id': 'auto_test_success',
                'success': True,
                'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 'merge_main'],
                'github_pages_accessible': True
            }
            
            notification_result = self.notifier.send_deployment_notification(success_result)
            assert notification_result['success'], "성공 알림 전송 실패"
            assert notification_result.get('template_used'), "성공 알림 템플릿 미사용"
            
            print("  ✓ 배포 성공 자동 알림 완료")
            
            # 실패 알림 테스트
            failure_result = {
                'deployment_id': 'auto_test_failure',
                'success': False,
                'error_message': '자동화 테스트 오류',
                'rollback_performed': True
            }
            
            notification_result = self.notifier.send_deployment_notification(failure_result)
            assert notification_result['success'], "실패 알림 전송 실패"
            assert notification_result['template_used']['type'] == 'deployment_failure', "실패 알림 템플릿 오류"
            
            print("  ✓ 배포 실패 자동 알림 완료")
            
            # 시작 알림 테스트
            start_result = self.notifier.send_deployment_start_notification('auto_test_start')
            assert start_result['success'], "시작 알림 전송 실패"
            
            print("  ✓ 배포 시작 자동 알림 완료")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 배포 알림 자동화 테스트 실패: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """오류 처리 및 복구 테스트"""
        try:
            # 잘못된 웹훅 URL 테스트
            original_url = self.notifier.webhook_url
            self.notifier.webhook_url = "https://invalid-webhook-url-test.com/nonexistent"
            
            webhook_result = self.notifier.send_direct_webhook(
                message="오류 처리 테스트 메시지"
            )
            
            # 오류 처리 검증
            assert not webhook_result['success'], "잘못된 URL에서 성공 응답"
            assert webhook_result.get('error_message'), "오류 메시지 없음"
            
            print("  ✓ 잘못된 웹훅 URL 오류 처리 완료")
            
            # URL 복구
            self.notifier.webhook_url = original_url
            
            # 템플릿 오류 처리 테스트
            invalid_data = {'invalid_field': 'test'}
            webhook_result = self.notifier.send_direct_webhook(
                deployment_result=invalid_data,
                message_type=MessageType.DEPLOYMENT_SUCCESS
            )
            
            # 템플릿 오류 시에도 메시지 전송 성공해야 함 (폴백 메커니즘)
            assert webhook_result['success'], "템플릿 오류 시 폴백 실패"
            
            print("  ✓ 템플릿 오류 폴백 메커니즘 완료")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 오류 처리 테스트 실패: {e}")
            return False
    
    def test_webhook_config_integration(self) -> bool:
        """웹훅 설정 파일 통합 테스트"""
        try:
            # 설정 파일 존재 확인
            config_file = os.path.join(self.notifier.script_dir, "../config/webhook_config.json")
            assert os.path.exists(config_file), "웹훅 설정 파일이 없음"
            
            # 설정 로드 확인
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_sections = ['webhook_settings', 'message_settings', 'notification_types', 'gui_integration']
            for section in required_sections:
                assert section in config, f"설정 섹션 누락: {section}"
            
            print("  ✓ 웹훅 설정 파일 구조 검증 완료")
            
            # 설정 적용 확인
            assert hasattr(self.notifier, 'webhook_timeout'), "웹훅 타임아웃 설정 미적용"
            assert hasattr(self.notifier, 'customer_friendly_mode'), "고객 친화적 모드 설정 미적용"
            assert hasattr(self.notifier, 'enable_templates'), "템플릿 활성화 설정 미적용"
            
            print("  ✓ 웹훅 설정 적용 확인 완료")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 웹훅 설정 통합 테스트 실패: {e}")
            return False
    
    def test_message_preview(self) -> bool:
        """메시지 미리보기 기능 테스트"""
        try:
            test_data = {
                'deployment_id': 'preview_test_001',
                'success': True,
                'steps_completed': ['status_check', 'backup_creation']
            }
            
            # 성공 메시지 미리보기
            success_preview = self.message_engine.preview_message(
                MessageType.DEPLOYMENT_SUCCESS, 
                test_data
            )
            
            assert success_preview, "성공 메시지 미리보기 생성 실패"
            assert "미리보기" in success_preview, "미리보기 형식 오류"
            assert "POSCO" in success_preview, "브랜딩 정보 누락"
            
            print("  ✓ 배포 성공 메시지 미리보기 생성 완료")
            
            # 실패 메시지 미리보기
            test_data['success'] = False
            test_data['error_message'] = '미리보기 테스트 오류'
            
            failure_preview = self.message_engine.preview_message(
                MessageType.DEPLOYMENT_FAILURE,
                test_data
            )
            
            assert failure_preview, "실패 메시지 미리보기 생성 실패"
            assert "실패" in failure_preview, "실패 메시지 내용 누락"
            
            print("  ✓ 배포 실패 메시지 미리보기 생성 완료")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 메시지 미리보기 테스트 실패: {e}")
            return False
    
    def test_realtime_logging(self) -> bool:
        """실시간 로깅 시스템 테스트"""
        try:
            # 로그 파일 확인
            log_file = self.notifier.log_file
            initial_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
            
            # 웹훅 전송으로 로그 생성
            webhook_result = self.notifier.send_direct_webhook(
                message="로깅 테스트 메시지",
                deployment_result={'test': 'logging'}
            )
            
            # 로그 파일 크기 증가 확인
            if os.path.exists(log_file):
                final_size = os.path.getsize(log_file)
                assert final_size > initial_size, "로그 파일 크기 증가 없음"
                
                # 로그 내용 확인
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    assert "웹훅 전송" in log_content, "웹훅 로그 내용 누락"
                
                print("  ✓ 로그 파일 기록 확인 완료")
            
            # 성공/실패 로그 구조 확인
            assert webhook_result.get('success') is not None, "전송 결과 로그 누락"
            
            print("  ✓ 실시간 로깅 시스템 검증 완료")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 실시간 로깅 테스트 실패: {e}")
            return False
    
    def test_full_pipeline_integration(self) -> bool:
        """전체 파이프라인 통합 테스트"""
        try:
            # 전체 배포 파이프라인 시뮬레이션
            test_data = {
                'kospi': '2,450.32',
                'exchange_rate': '1,340.50',
                'posco_stock': '285,000',
                'analysis': '시장 상황이 안정적입니다.'
            }
            
            callback_calls = []
            
            def pipeline_callback(message: str, progress: int):
                callback_calls.append({'message': message, 'progress': progress})
                print(f"  📊 파이프라인: {progress}% - {message}")
            
            # 파이프라인 실행 (HTML 생성 제외하고 웹훅 부분만 테스트)
            deployment_result = {
                'deployment_id': 'pipeline_test_001',
                'start_time': '2025-09-23T14:00:00',
                'end_time': '2025-09-23T14:02:30',
                'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 'merge_main', 'commit_changes', 'push_remote', 'pages_verification'],
                'success': True,
                'github_pages_accessible': True,
                'backup_created': True
            }
            
            # 성공 알림 전송
            webhook_result = self.notifier.send_deployment_notification(
                deployment_result, 
                pipeline_callback
            )
            
            # 파이프라인 통합 검증
            assert webhook_result['success'], "파이프라인 웹훅 전송 실패"
            assert len(callback_calls) > 0, "파이프라인 콜백 호출 없음"
            assert webhook_result.get('template_used'), "파이프라인 템플릿 미사용"
            
            print("  ✓ 전체 파이프라인 웹훅 통합 완료")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 전체 파이프라인 통합 테스트 실패: {e}")
            return False
    
    def verify_requirements(self):
        """Requirements 2.1, 2.2 검증"""
        print("\n🎯 Requirements 검증")
        print("-" * 30)
        
        # Requirement 2.1: MessageTemplateEngine과 연동하여 포스코 스타일 메시지 형식 적용
        req_2_1_tests = [
            "MessageTemplateEngine 통합 테스트",
            "메시지 미리보기 기능 테스트",
            "배포 알림 자동화 테스트"
        ]
        
        req_2_1_passed = all(
            result['passed'] for result in self.test_results 
            if result['name'] in req_2_1_tests
        )
        
        print(f"📋 Requirement 2.1 (MessageTemplateEngine 연동): {'✅ 통과' if req_2_1_passed else '❌ 실패'}")
        
        # Requirement 2.2: 개발자용 메시지를 고객 친화적 내용으로 변경
        req_2_2_tests = [
            "고객 친화적 메시지 변환 테스트",
            "GUI 상태 모니터링 콜백 테스트",
            "실시간 로깅 시스템 테스트"
        ]
        
        req_2_2_passed = all(
            result['passed'] for result in self.test_results 
            if result['name'] in req_2_2_tests
        )
        
        print(f"📋 Requirement 2.2 (고객 친화적 메시지 & GUI 모니터링): {'✅ 통과' if req_2_2_passed else '❌ 실패'}")
        
        # 전체 요구사항 충족 여부
        all_requirements_met = req_2_1_passed and req_2_2_passed
        print(f"\n🏆 Task 9 완료 상태: {'✅ 완료' if all_requirements_met else '❌ 미완료'}")
        
        if all_requirements_met:
            print("\n🎉 Task 9 '내장된 send_direct_webhook 메서드 개선' 성공적으로 완료!")
            print("   • MessageTemplateEngine과 연동하여 포스코 스타일 메시지 형식 적용 ✓")
            print("   • 개발자용 메시지를 고객 친화적 내용으로 변경 ✓")
            print("   • GUI에서 메시지 전송 상태 실시간 모니터링 ✓")


def main():
    """메인 테스트 실행"""
    print("🚀 웹훅 통합 테스트 시작 - Task 9 완료 검증")
    print("=" * 80)
    
    tester = WebhookIntegrationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 모든 테스트 통과! Task 9 구현 완료 확인")
            return True
        else:
            print("\n⚠️ 일부 테스트 실패. 구현 검토 필요")
            return False
            
    except Exception as e:
        print(f"\n💥 테스트 실행 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)