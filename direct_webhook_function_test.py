#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
복원된 웹훅 함수 직접 테스트
POSCO 워치햄스터 알림 메시지 복원 후 실제 함수 호출 테스트

Task 9: 실제 웹훅 전송 테스트 수행 - 복원된 함수 직접 호출
"""

import os
import sys
import json
from datetime import datetime

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 복원된 모니터링 시스템 import 시도
try:
    sys.path.insert(0, os.path.join(current_dir, 'core', 'monitoring'))
    from monitor_WatchHamster_v3_0 import WatchHamsterV3Monitor
    print("✅ 복원된 WatchHamsterV3Monitor 로드 성공")
    monitor_available = True
except ImportError as e:
    print(f"❌ WatchHamsterV3Monitor 로드 실패: {e}")
    # 다른 경로 시도
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "monitor_WatchHamster_v3_0", 
            os.path.join(current_dir, 'core', 'monitoring', 'monitor_WatchHamster_v3.0.py')
        )
        monitor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(monitor_module)
        WatchHamsterV3Monitor = monitor_module.WatchHamsterV3Monitor
        print("✅ 직접 파일 로드로 WatchHamsterV3Monitor 로드 성공")
        monitor_available = True
    except Exception as e2:
        print(f"❌ 직접 파일 로드도 실패: {e2}")
        monitor_available = False

class DirectWebhookFunctionTester:
    """복원된 웹훅 함수 직접 테스트 클래스"""
    
    def __init__(self):
        self.test_results = []
        self.test_start_time = datetime.now()
        self.monitor = None
        
        if monitor_available:
            try:
                # 복원된 모니터 인스턴스 생성
                self.monitor = WatchHamsterV3Monitor()
                print("✅ WatchHamsterV3Monitor 인스턴스 생성 성공")
            except Exception as e:
                print(f"❌ WatchHamsterV3Monitor 인스턴스 생성 실패: {e}")
                self.monitor = None
    
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def test_send_notification_function(self):
        """복원된 send_notification 함수 테스트"""
        self.log("🔔 복원된 send_notification 함수 테스트 시작...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없어 테스트를 건너뜁니다.")
            return False
        
        try:
            # 일반 알림 테스트
            test_message = f"""🔔 복원된 send_notification 함수 테스트

📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🛡️ 테스트 목적: 웹훅 메시지 복원 후 함수 동작 확인

✅ 이는 복원된 send_notification 함수의 직접 호출 테스트입니다."""

            self.monitor.send_notification(test_message, is_error=False)
            
            # 오류 알림 테스트
            error_message = f"""🚨 복원된 send_notification 오류 알림 테스트

📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⚠️ 테스트 목적: 오류 알림 기능 확인

❌ 이는 복원된 send_notification 함수의 오류 모드 테스트입니다."""

            self.monitor.send_notification(error_message, is_error=True)
            
            self.test_results.append({
                "function": "send_notification",
                "test_type": "일반 알림 + 오류 알림",
                "success": True,
                "message": "복원된 함수 호출 성공",
                "timestamp": datetime.now().isoformat()
            })
            
            self.log("✅ send_notification 함수 테스트 성공")
            return True
            
        except Exception as e:
            self.test_results.append({
                "function": "send_notification",
                "test_type": "일반 알림 + 오류 알림",
                "success": False,
                "message": f"함수 호출 오류: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            
            self.log(f"❌ send_notification 함수 테스트 실패: {e}")
            return False
    
    def test_send_status_notification_function(self):
        """복원된 send_status_notification 함수 테스트"""
        self.log("📊 복원된 send_status_notification 함수 테스트 시작...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없어 테스트를 건너뜁니다.")
            return False
        
        try:
            # 정기 상태 알림 함수 호출
            result = self.monitor.send_status_notification()
            
            self.test_results.append({
                "function": "send_status_notification",
                "test_type": "정기 상태 보고",
                "success": True,
                "message": "복원된 함수 호출 성공",
                "result": str(result) if result is not None else "None",
                "timestamp": datetime.now().isoformat()
            })
            
            self.log("✅ send_status_notification 함수 테스트 성공")
            return True
            
        except Exception as e:
            self.test_results.append({
                "function": "send_status_notification",
                "test_type": "정기 상태 보고",
                "success": False,
                "message": f"함수 호출 오류: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            
            self.log(f"❌ send_status_notification 함수 테스트 실패: {e}")
            return False
    
    def test_startup_notification_function(self):
        """복원된 시작 알림 함수 테스트"""
        self.log("🚀 복원된 시작 알림 함수 테스트 시작...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없어 테스트를 건너뜁니다.")
            return False
        
        try:
            # 시작 알림 함수 호출 시도
            if hasattr(self.monitor, 'send_startup_notification_v3_0'):
                result = self.monitor.send_startup_notification_v3_0()
                function_name = "send_startup_notification_v3_0"
            elif hasattr(self.monitor, 'send_startup_notification'):
                result = self.monitor.send_startup_notification()
                function_name = "send_startup_notification"
            else:
                raise AttributeError("시작 알림 함수를 찾을 수 없습니다")
            
            self.test_results.append({
                "function": function_name,
                "test_type": "시작 알림",
                "success": True,
                "message": "복원된 함수 호출 성공",
                "result": str(result) if result is not None else "None",
                "timestamp": datetime.now().isoformat()
            })
            
            self.log(f"✅ {function_name} 함수 테스트 성공")
            return True
            
        except Exception as e:
            self.test_results.append({
                "function": "startup_notification",
                "test_type": "시작 알림",
                "success": False,
                "message": f"함수 호출 오류: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            
            self.log(f"❌ 시작 알림 함수 테스트 실패: {e}")
            return False
    
    def check_available_webhook_functions(self):
        """사용 가능한 웹훅 함수들 확인"""
        self.log("🔍 사용 가능한 웹훅 함수들 확인 중...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없습니다.")
            return []
        
        webhook_functions = []
        
        # 웹훅 관련 함수들 확인
        function_candidates = [
            'send_notification',
            'send_status_notification',
            'send_startup_notification',
            'send_startup_notification_v3_0',
            'send_process_error_v2',
            'send_critical_alert_v2',
            'send_enhanced_status_notification',
            '_send_hourly_status_notification'
        ]
        
        for func_name in function_candidates:
            if hasattr(self.monitor, func_name):
                webhook_functions.append(func_name)
                self.log(f"✅ {func_name} 함수 발견")
            else:
                self.log(f"❌ {func_name} 함수 없음")
        
        return webhook_functions
    
    def run_all_function_tests(self):
        """모든 복원된 웹훅 함수 테스트 실행"""
        self.log("🚀 복원된 웹훅 함수 직접 테스트 시작")
        self.log(f"📅 테스트 시작 시간: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 80)
        
        # 사용 가능한 함수들 확인
        available_functions = self.check_available_webhook_functions()
        self.log(f"📋 발견된 웹훅 함수: {len(available_functions)}개")
        self.log("-" * 60)
        
        # 각 함수 테스트 실행
        tests = [
            ("send_notification 함수", self.test_send_notification_function),
            ("send_status_notification 함수", self.test_send_status_notification_function),
            ("startup_notification 함수", self.test_startup_notification_function)
        ]
        
        for test_name, test_func in tests:
            self.log(f"🔄 {test_name} 테스트 실행 중...")
            test_func()
            self.log("-" * 60)
        
        # 결과 요약
        self.log("📊 복원된 웹훅 함수 테스트 결과 요약")
        self.log("=" * 80)
        
        success_count = sum(1 for result in self.test_results if result['success'])
        total_count = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ 성공" if result['success'] else "❌ 실패"
            self.log(f"{status} | {result['function']} ({result['test_type']}) | {result['message']}")
        
        self.log("=" * 80)
        self.log(f"📈 전체 결과: {success_count}/{total_count} 성공")
        
        if success_count == total_count:
            self.log("🎉 모든 복원된 웹훅 함수 테스트가 성공했습니다!")
        else:
            self.log("⚠️ 일부 복원된 웹훅 함수 테스트에 문제가 있습니다.")
        
        # 최종 결과 구성
        final_results = {
            "test_summary": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_tests": total_count,
                "successful_tests": success_count,
                "success_rate": f"{(success_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
                "available_functions": available_functions
            },
            "test_results": self.test_results,
            "monitor_available": monitor_available,
            "monitor_instance_created": self.monitor is not None
        }
        
        return final_results

def main():
    """메인 함수"""
    print("🔔 POSCO 워치햄스터 복원된 웹훅 함수 직접 테스트")
    print("=" * 80)
    print("Task 9: 실제 웹훅 전송 테스트 수행 - 복원된 함수 직접 호출")
    print("=" * 80)
    
    tester = DirectWebhookFunctionTester()
    results = tester.run_all_function_tests()
    
    # 결과를 JSON 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f'direct_webhook_function_test_results_{timestamp}.json'
    
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 테스트 결과가 '{result_filename}'에 저장되었습니다.")

if __name__ == "__main__":
    main()