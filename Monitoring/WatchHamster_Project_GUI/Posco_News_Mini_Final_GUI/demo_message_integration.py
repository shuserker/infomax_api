#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MessageTemplateEngine 통합 데모
기존 posco_main_notifier.py와 MessageTemplateEngine의 통합 예시

주요 기능:
- 🔗 기존 시스템과의 통합 방법 시연
- 📨 개선된 메시지 형식 비교
- 🎨 POSCO 스타일 메시지 생성 데모
- 📱 GUI 미리보기 연동 테스트
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from message_template_engine import MessageTemplateEngine, MessageType
    from message_preview_gui import MessagePreviewGUI
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class MessageIntegrationDemo:
    """메시지 템플릿 엔진 통합 데모 클래스"""
    
    def __init__(self):
        """데모 초기화"""
        self.engine = MessageTemplateEngine()
        print("🎨 MessageTemplateEngine 통합 데모 시작...")
        print("=" * 60)
    
    def demo_old_vs_new_messages(self):
        """기존 메시지 vs 새로운 메시지 비교 데모"""
        print("\n📊 기존 메시지 vs 새로운 메시지 비교")
        print("-" * 40)
        
        # 샘플 배포 결과 데이터
        deployment_result = {
            'deployment_id': 'deploy_20250902_150400',
            'start_time': '2025-09-02T15:04:00',
            'end_time': '2025-09-02T15:06:23',
            'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 
                              'merge_main', 'commit_changes', 'push_remote', 'pages_verification'],
            'github_pages_accessible': True,
            'success': True
        }
        
        # 기존 메시지 형식 (posco_main_notifier.py에서 사용하던 방식)
        old_message = f"""🎉 POSCO 분석 리포트 배포 성공!
📊 배포 ID: {deployment_result['deployment_id']}
🌐 URL: https://shuserker.github.io/infomax_api
⏱️ 소요 시간: {len(deployment_result['steps_completed'])}단계 완료"""
        
        print("🔸 기존 메시지 형식:")
        print(old_message)
        print()
        
        # 새로운 메시지 형식 (MessageTemplateEngine 사용)
        new_message = self.engine.generate_deployment_success_message(deployment_result)
        
        print("🔹 새로운 메시지 형식:")
        print(f"제목: {new_message['title']}")
        print(f"내용:\n{new_message['body']}")
        print(f"우선순위: {new_message['priority']}")
        print(f"색상: {new_message['color']}")
        
        print("\n✨ 개선 사항:")
        print("• 더 상세하고 구조화된 정보 제공")
        print("• POSCO 브랜딩 일관성 적용")
        print("• 메시지 우선순위 및 색상 지원")
        print("• 고객 친화적인 언어 사용")
        print("• 단계별 진행 상황 상세 표시")
    
    def demo_integration_with_posco_notifier(self):
        """PoscoMainNotifier와의 통합 방법 데모"""
        print("\n🔗 PoscoMainNotifier 통합 방법")
        print("-" * 40)
        
        print("기존 send_direct_webhook 메서드 개선 방법:")
        print()
        
        # 통합 코드 예시
        integration_code = '''
# 기존 PoscoMainNotifier 클래스에 추가할 코드

from message_template_engine import MessageTemplateEngine, MessageType

class PoscoMainNotifier:
    def __init__(self, base_dir: Optional[str] = None):
        # 기존 초기화 코드...
        
        # MessageTemplateEngine 추가
        self.message_engine = MessageTemplateEngine()
    
    def send_enhanced_webhook(self, message_type: MessageType, data: Dict[str, Any]) -> bool:
        """개선된 웹훅 메시지 전송"""
        try:
            # MessageTemplateEngine으로 메시지 생성
            message = self.message_engine.generate_message(message_type, data)
            
            # 웹훅 페이로드 생성
            payload = {
                "text": f"{message['title']}\\n\\n{message['body']}",
                "priority": message['priority'],
                "color": message['color'],
                "timestamp": message['timestamp']
            }
            
            # 기존 웹훅 전송 로직 사용
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            self.log_message(f"❌ 개선된 웹훅 전송 실패: {e}")
            return False
    
    def run_full_deployment_pipeline(self, data: Dict, progress_callback=None):
        """개선된 배포 파이프라인"""
        # 기존 배포 로직...
        
        if deployment_result['success']:
            # 기존 방식 대신 MessageTemplateEngine 사용
            self.send_enhanced_webhook(MessageType.DEPLOYMENT_SUCCESS, deployment_result)
        else:
            self.send_enhanced_webhook(MessageType.DEPLOYMENT_FAILURE, deployment_result)
'''
        
        print(integration_code)
        
        print("\n💡 통합의 장점:")
        print("• 기존 코드 최소 변경으로 메시지 품질 향상")
        print("• 메시지 템플릿 중앙 관리")
        print("• 일관된 브랜딩 및 형식 적용")
        print("• GUI 미리보기 기능 활용 가능")
    
    def demo_different_message_types(self):
        """다양한 메시지 타입 데모"""
        print("\n📱 다양한 메시지 타입 데모")
        print("-" * 40)
        
        # 1. 배포 시작 메시지
        print("1️⃣ 배포 시작 메시지:")
        start_msg = self.engine.generate_deployment_start_message('deploy_demo_001')
        print(f"   제목: {start_msg['title']}")
        print(f"   우선순위: {start_msg['priority']}")
        print()
        
        # 2. 데이터 업데이트 메시지
        print("2️⃣ 데이터 업데이트 메시지:")
        market_data = {
            'kospi': '2,485.67',
            'kospi_change': 15.23,
            'exchange_rate': '1,342.50',
            'exchange_change': -2.80,
            'posco_stock': '285,000',
            'posco_change': 5000
        }
        data_msg = self.engine.generate_data_update_message(market_data)
        print(f"   제목: {data_msg['title']}")
        print(f"   색상: {data_msg['color']}")
        print()
        
        # 3. 시스템 상태 메시지
        print("3️⃣ 시스템 상태 메시지:")
        status_data = {
            'total_deployments': 127,
            'success_rate': 94.5,
            'last_success': '2025-09-02 15:06:23',
            'avg_deployment_time': 2.3
        }
        status_msg = self.engine.generate_system_status_message(status_data)
        print(f"   제목: {status_msg['title']}")
        print(f"   우선순위: {status_msg['priority']}")
        print()
        
        # 4. 오류 알림 메시지
        print("4️⃣ 오류 알림 메시지:")
        error_data = {
            'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error_type': 'Database Connection Error',
            'impact_scope': 'Data Collection Module',
            'error_details': 'Connection timeout after 30 seconds',
            'auto_recovery_status': '시도 중',
            'estimated_recovery_time': '5-10분'
        }
        error_msg = self.engine.generate_message(MessageType.ERROR_ALERT, error_data)
        print(f"   제목: {error_msg['title']}")
        print(f"   우선순위: {error_msg['priority']} (중요!)")
        print()
    
    def demo_customization_features(self):
        """커스터마이징 기능 데모"""
        print("\n🎨 커스터마이징 기능 데모")
        print("-" * 40)
        
        print("📋 사용 가능한 템플릿 목록:")
        templates = self.engine.get_available_templates()
        for i, template in enumerate(templates, 1):
            print(f"   {i}. {template}")
        
        print(f"\n📊 총 {len(templates)}개의 템플릿 사용 가능")
        
        # 템플릿 정보 조회 예시
        print("\n🔍 배포 성공 템플릿 상세 정보:")
        info = self.engine.get_template_info(MessageType.DEPLOYMENT_SUCCESS)
        print(f"   타입: {info['type']}")
        print(f"   우선순위: {info['priority']}")
        print(f"   색상: {info['color']}")
        print(f"   필수 필드: {', '.join(info['required_fields'])}")
        
        print("\n💾 사용자 정의 템플릿:")
        print("   • config/message_templates.json 파일로 템플릿 커스터마이징 가능")
        print("   • 브랜딩, 색상, 우선순위 등 모든 요소 수정 가능")
        print("   • 새로운 메시지 타입 추가 가능")
    
    def demo_gui_preview(self):
        """GUI 미리보기 데모"""
        print("\n👀 GUI 미리보기 기능 데모")
        print("-" * 40)
        
        print("GUI 미리보기 기능:")
        print("• 실시간 메시지 미리보기")
        print("• 다양한 샘플 데이터 테스트")
        print("• 메시지 내용 클립보드 복사")
        print("• 파일로 저장 기능")
        print("• 테스트 전송 시뮬레이션")
        
        try:
            import tkinter as tk
            print("\n🎨 GUI 미리보기 창을 열겠습니까? (y/n): ", end="")
            response = input().strip().lower()
            
            if response in ['y', 'yes', '예']:
                print("🚀 GUI 미리보기 창 실행 중...")
                
                # GUI 미리보기 실행
                root = tk.Tk()
                root.withdraw()  # 메인 창 숨기기
                
                preview_gui = MessagePreviewGUI(root)
                preview_gui.show()
                
                print("✅ GUI 미리보기 완료")
            else:
                print("⏭️ GUI 미리보기 건너뛰기")
                
        except ImportError:
            print("⚠️ tkinter를 사용할 수 없어 GUI 미리보기를 건너뜁니다")
        except Exception as e:
            print(f"❌ GUI 미리보기 실행 실패: {e}")
    
    def run_full_demo(self):
        """전체 데모 실행"""
        try:
            # 1. 기존 vs 새로운 메시지 비교
            self.demo_old_vs_new_messages()
            
            # 2. 통합 방법 설명
            self.demo_integration_with_posco_notifier()
            
            # 3. 다양한 메시지 타입
            self.demo_different_message_types()
            
            # 4. 커스터마이징 기능
            self.demo_customization_features()
            
            # 5. GUI 미리보기 (선택사항)
            self.demo_gui_preview()
            
            print("\n" + "=" * 60)
            print("🎉 MessageTemplateEngine 통합 데모 완료!")
            print("=" * 60)
            
            print("\n📝 다음 단계:")
            print("1. 기존 posco_main_notifier.py에 MessageTemplateEngine 통합")
            print("2. send_direct_webhook 메서드를 send_enhanced_webhook으로 교체")
            print("3. 필요에 따라 메시지 템플릿 커스터마이징")
            print("4. GUI 미리보기로 메시지 형식 확인 및 테스트")
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 사용자에 의해 데모가 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 데모 실행 중 오류 발생: {e}")


def main():
    """메인 함수"""
    print("🎨 POSCO MessageTemplateEngine 통합 데모")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        demo = MessageIntegrationDemo()
        demo.run_full_demo()
        
    except Exception as e:
        print(f"❌ 데모 실행 실패: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)