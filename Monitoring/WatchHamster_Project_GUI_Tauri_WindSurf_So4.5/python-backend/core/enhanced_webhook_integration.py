#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Webhook Integration Example
기존 posco_main_notifier.py에 MessageTemplateEngine을 통합하는 예시

이 파일은 기존 PoscoMainNotifier 클래스에 추가할 수 있는 
개선된 웹훅 메서드들을 보여줍니다.

Requirements: 2.1, 2.2 구현 (메시지 개선)
"""

import requests
from datetime import datetime
from typing import Dict, Any, Optional, Callable

try:
    from .message_template_engine import MessageTemplateEngine, MessageType
except ImportError:
    from message_template_engine import MessageTemplateEngine, MessageType


class EnhancedWebhookMixin:
    """
    기존 PoscoMainNotifier 클래스에 추가할 수 있는 개선된 웹훅 기능
    
    사용법:
    1. 기존 PoscoMainNotifier 클래스에 이 클래스를 상속 추가
    2. __init__ 메서드에 self.message_engine = MessageTemplateEngine() 추가
    3. 기존 send_direct_webhook 대신 send_enhanced_webhook 사용
    """
    
    def __init__(self):
        """Enhanced Webhook Mixin 초기화"""
        # MessageTemplateEngine 초기화
        if not hasattr(self, 'message_engine'):
            self.message_engine = MessageTemplateEngine()
        
        # 기존 속성들이 없으면 기본값 설정
        if not hasattr(self, 'webhook_url'):
            self.webhook_url = None
        if not hasattr(self, 'log_message'):
            self.log_message = print
    
    def send_enhanced_webhook(self, message_type: MessageType, data: Dict[str, Any], 
                            deployment_result: Optional[Dict] = None) -> bool:
        """
        개선된 웹훅 메시지 전송
        
        Args:
            message_type: 메시지 타입 (MessageType enum)
            data: 메시지 생성에 필요한 데이터
            deployment_result: 배포 결과 (선택사항)
        
        Returns:
            bool: 전송 성공 여부
        """
        try:
            if not self.webhook_url:
                self.log_message("⚠️ 웹훅 URL이 설정되지 않았습니다")
                return False
            
            # MessageTemplateEngine으로 메시지 생성
            message = self.message_engine.generate_message(message_type, data)
            
            # 웹훅 페이로드 생성 (기존 형식 유지하면서 개선)
            payload = {
                "text": f"{message['title']}\n\n{message['body']}",
                "timestamp": message['timestamp'],
                "priority": message['priority'],
                "color": message['color'],
                "message_type": message['message_type']
            }
            
            # 배포 결과가 있으면 추가 정보 포함 (기존 로직 유지)
            if deployment_result:
                payload["deployment_info"] = {
                    "deployment_id": deployment_result.get('deployment_id'),
                    "success": deployment_result.get('success'),
                    "steps_completed": len(deployment_result.get('steps_completed', [])),
                    "github_pages_accessible": deployment_result.get('github_pages_accessible')
                }
            
            # 웹훅 전송 (기존 로직 유지)
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.log_message("✅ 개선된 웹훅 메시지 전송 완료")
                return True
            else:
                self.log_message(f"❌ 개선된 웹훅 전송 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 개선된 웹훅 전송 중 오류: {str(e)}")
            return False
    
    def send_deployment_success_webhook(self, deployment_result: Dict[str, Any]) -> bool:
        """배포 성공 웹훅 전송 (편의 메서드)"""
        # MessageTemplateEngine의 전용 메서드 사용
        message = self.message_engine.generate_deployment_success_message(deployment_result)
        
        # 웹훅 페이로드 생성
        payload = {
            "text": f"{message['title']}\n\n{message['body']}",
            "timestamp": message['timestamp'],
            "priority": message['priority'],
            "color": message['color'],
            "message_type": message['message_type']
        }
        
        try:
            if not self.webhook_url:
                self.log_message("⚠️ 웹훅 URL이 설정되지 않았습니다")
                return False
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.log_message("✅ 배포 성공 웹훅 전송 완료")
                return True
            else:
                self.log_message(f"❌ 배포 성공 웹훅 전송 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 배포 성공 웹훅 전송 중 오류: {str(e)}")
            return False
    
    def send_deployment_failure_webhook(self, deployment_result: Dict[str, Any]) -> bool:
        """배포 실패 웹훅 전송 (편의 메서드)"""
        # MessageTemplateEngine의 전용 메서드 사용
        message = self.message_engine.generate_deployment_failure_message(deployment_result)
        
        # 웹훅 페이로드 생성
        payload = {
            "text": f"{message['title']}\n\n{message['body']}",
            "timestamp": message['timestamp'],
            "priority": message['priority'],
            "color": message['color'],
            "message_type": message['message_type']
        }
        
        try:
            if not self.webhook_url:
                self.log_message("⚠️ 웹훅 URL이 설정되지 않았습니다")
                return False
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.log_message("✅ 배포 실패 웹훅 전송 완료")
                return True
            else:
                self.log_message(f"❌ 배포 실패 웹훅 전송 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 배포 실패 웹훅 전송 중 오류: {str(e)}")
            return False
    
    def send_deployment_start_webhook(self, deployment_id: str) -> bool:
        """배포 시작 웹훅 전송 (편의 메서드)"""
        data = {'deployment_id': deployment_id}
        return self.send_enhanced_webhook(MessageType.DEPLOYMENT_START, data)
    
    def send_data_update_webhook(self, market_data: Dict[str, Any]) -> bool:
        """데이터 업데이트 웹훅 전송 (편의 메서드)"""
        # MessageTemplateEngine의 전용 메서드 사용
        message = self.message_engine.generate_data_update_message(market_data)
        
        # 웹훅 페이로드 생성
        payload = {
            "text": f"{message['title']}\n\n{message['body']}",
            "timestamp": message['timestamp'],
            "priority": message['priority'],
            "color": message['color'],
            "message_type": message['message_type']
        }
        
        try:
            if not self.webhook_url:
                self.log_message("⚠️ 웹훅 URL이 설정되지 않았습니다")
                return False
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.log_message("✅ 데이터 업데이트 웹훅 전송 완료")
                return True
            else:
                self.log_message(f"❌ 데이터 업데이트 웹훅 전송 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 데이터 업데이트 웹훅 전송 중 오류: {str(e)}")
            return False
    
    def send_system_status_webhook(self, status_data: Dict[str, Any]) -> bool:
        """시스템 상태 웹훅 전송 (편의 메서드)"""
        return self.send_enhanced_webhook(MessageType.SYSTEM_STATUS, status_data)
    
    def send_error_alert_webhook(self, error_data: Dict[str, Any]) -> bool:
        """오류 알림 웹훅 전송 (편의 메서드)"""
        return self.send_enhanced_webhook(MessageType.ERROR_ALERT, error_data)
    
    def preview_webhook_message(self, message_type: MessageType, data: Dict[str, Any]) -> str:
        """웹훅 메시지 미리보기 (테스트용)"""
        try:
            # 메시지 타입에 따라 적절한 메서드 사용
            if message_type == MessageType.DEPLOYMENT_SUCCESS:
                message = self.message_engine.generate_deployment_success_message(data)
            elif message_type == MessageType.DEPLOYMENT_FAILURE:
                message = self.message_engine.generate_deployment_failure_message(data)
            elif message_type == MessageType.DEPLOYMENT_START:
                deployment_id = data.get('deployment_id', 'unknown')
                message = self.message_engine.generate_deployment_start_message(deployment_id)
            elif message_type == MessageType.DATA_UPDATE:
                message = self.message_engine.generate_data_update_message(data)
            elif message_type == MessageType.SYSTEM_STATUS:
                message = self.message_engine.generate_system_status_message(data)
            else:
                message = self.message_engine.generate_message(message_type, data)
            
            # 미리보기 형식으로 포맷팅
            preview = f"""
=== 웹훅 메시지 미리보기 ===
제목: {message['title']}
우선순위: {message['priority']}
색상: {message['color']}
생성 시간: {message['timestamp']}

--- 메시지 내용 ---
{message['body']}

=== 미리보기 끝 ===
"""
            return preview.strip()
            
        except Exception as e:
            return f"❌ 미리보기 생성 실패: {str(e)}"


# 기존 PoscoMainNotifier 클래스 확장 예시
class EnhancedPoscoMainNotifier(EnhancedWebhookMixin):
    """
    기존 PoscoMainNotifier에 MessageTemplateEngine을 통합한 예시 클래스
    
    실제 통합 시에는 기존 PoscoMainNotifier 클래스에 
    EnhancedWebhookMixin을 상속 추가하면 됩니다.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """Enhanced POSCO Main Notifier 초기화"""
        # 기존 초기화 로직 (예시)
        self.base_dir = base_dir or "."
        self.webhook_url = None  # 실제로는 설정에서 로드
        
        # Enhanced Webhook Mixin 초기화
        super().__init__()
        
        self.log_message("🚀 Enhanced POSCO Main Notifier 초기화 완료")
    
    def log_message(self, message: str):
        """로그 메시지 출력 (기존 로직 시뮬레이션)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def run_enhanced_deployment_pipeline(self, data: Dict, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        개선된 배포 파이프라인 (기존 로직에 개선된 메시지 적용)
        
        이 메서드는 기존 run_full_deployment_pipeline을 개선한 예시입니다.
        """
        self.log_message("🚀 Enhanced POSCO 배포 파이프라인 시작...")
        
        pipeline_result = {
            'success': False,
            'pipeline_id': f"enhanced_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'deployment_result': None,
            'webhook_sent': False,
            'error_message': None
        }
        
        try:
            # 배포 시작 알림 (새로운 기능)
            if progress_callback:
                progress_callback("배포 시작 알림 전송 중...", 5)
            
            deployment_id = pipeline_result['pipeline_id']
            start_webhook_sent = self.send_deployment_start_webhook(deployment_id)
            
            if start_webhook_sent:
                self.log_message("✅ 배포 시작 알림 전송 완료")
            
            # 실제 배포 로직 (기존 로직 시뮬레이션)
            if progress_callback:
                progress_callback("배포 실행 중...", 50)
            
            # 시뮬레이션된 배포 결과
            deployment_result = {
                'deployment_id': deployment_id,
                'start_time': pipeline_result['start_time'],
                'end_time': datetime.now().isoformat(),
                'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 
                                  'merge_main', 'commit_changes', 'push_remote', 'pages_verification'],
                'github_pages_accessible': True,
                'success': True  # 시뮬레이션에서는 항상 성공
            }
            
            pipeline_result['deployment_result'] = deployment_result
            
            # 배포 결과에 따른 개선된 웹훅 전송
            if progress_callback:
                progress_callback("배포 결과 알림 전송 중...", 90)
            
            if deployment_result['success']:
                webhook_sent = self.send_deployment_success_webhook(deployment_result)
                pipeline_result['success'] = True
                self.log_message("✅ Enhanced 배포 파이프라인 성공 완료")
            else:
                webhook_sent = self.send_deployment_failure_webhook(deployment_result)
                pipeline_result['error_message'] = deployment_result.get('error_message')
                self.log_message(f"❌ Enhanced 배포 파이프라인 실패: {pipeline_result['error_message']}")
            
            pipeline_result['webhook_sent'] = webhook_sent
            pipeline_result['end_time'] = datetime.now().isoformat()
            
            if progress_callback:
                status = "성공" if pipeline_result['success'] else "실패"
                progress_callback(f"Enhanced 파이프라인 {status} 완료", 100)
            
            return pipeline_result
            
        except Exception as e:
            error_msg = f"Enhanced 배포 파이프라인 중 예외 발생: {str(e)}"
            pipeline_result['error_message'] = error_msg
            pipeline_result['end_time'] = datetime.now().isoformat()
            self.log_message(f"❌ {error_msg}")
            
            # 예외 발생 시 오류 알림 전송
            error_data = {
                'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error_type': 'Pipeline Exception',
                'impact_scope': 'Deployment Pipeline',
                'error_details': str(e),
                'auto_recovery_status': '시도 중',
                'estimated_recovery_time': '5-10분'
            }
            
            self.send_error_alert_webhook(error_data)
            
            return pipeline_result


def demo_enhanced_integration():
    """Enhanced Integration 데모"""
    print("🎨 Enhanced POSCO Main Notifier 통합 데모")
    print("=" * 50)
    
    # Enhanced Notifier 인스턴스 생성
    notifier = EnhancedPoscoMainNotifier()
    
    # 웹훅 URL 설정 (테스트용)
    notifier.webhook_url = "https://hooks.slack.com/test"  # 실제로는 유효한 URL 사용
    
    print("\n1️⃣ 배포 성공 메시지 미리보기:")
    success_data = {
        'deployment_id': 'demo_deploy_001',
        'start_time': '2025-09-02T15:00:00',
        'end_time': '2025-09-02T15:02:30',
        'steps_completed': ['status_check', 'push_remote', 'pages_verification'],
        'github_pages_accessible': True
    }
    
    preview = notifier.preview_webhook_message(MessageType.DEPLOYMENT_SUCCESS, success_data)
    print(preview)
    
    print("\n2️⃣ 데이터 업데이트 메시지 미리보기:")
    market_data = {
        'kospi': '2,485.67',
        'kospi_change': 15.23,
        'exchange_rate': '1,342.50',
        'exchange_change': -2.80,
        'posco_stock': '285,000',
        'posco_change': 5000
    }
    
    preview = notifier.preview_webhook_message(MessageType.DATA_UPDATE, market_data)
    print(preview)
    
    print("\n3️⃣ Enhanced 배포 파이프라인 시뮬레이션:")
    
    def progress_callback(message, progress):
        print(f"   [{progress:3d}%] {message}")
    
    # 실제로는 웹훅을 전송하지 않고 시뮬레이션만 실행
    notifier.webhook_url = None  # 실제 전송 방지
    
    result = notifier.run_enhanced_deployment_pipeline({}, progress_callback)
    
    print(f"\n✅ 파이프라인 결과:")
    print(f"   성공: {result['success']}")
    print(f"   파이프라인 ID: {result['pipeline_id']}")
    print(f"   웹훅 전송: {result['webhook_sent']}")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced Integration 데모 완료!")


if __name__ == "__main__":
    demo_enhanced_integration()