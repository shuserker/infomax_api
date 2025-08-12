#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
복원된 웹훅 함수 직접 테스트
실제 복원된 monitor_WatchHamster_v3.0.py의 웹훅 함수들을 직접 호출하여 테스트

Created: 2025-08-11
"""

import os
import sys
import json
from datetime import datetime

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'core', 'monitoring'))

# 복원된 모니터링 시스템 import 시도
try:
    # 파일명에서 점을 언더스코어로 변경하여 import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "monitor_watchhamster", 
        os.path.join(current_dir, 'core', 'monitoring', 'monitor_WatchHamster_v3.0.py')
    )
    monitor_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor_module)
    
    WatchHamsterV3Monitor = monitor_module.WatchHamsterV3Monitor
    print("✅ 복원된 WatchHamsterV3Monitor 모듈 로드 성공")
except Exception as e:
    print(f"❌ WatchHamsterV3Monitor 모듈 로드 실패: {e}")
    WatchHamsterV3Monitor = None

class RestoredWebhookFunctionTester:
    """복원된 웹훅 함수 직접 테스터"""
    
    def __init__(self):
        self.test_results = []
        self.test_start_time = datetime.now()
        self.monitor = None
        
        # 복원된 모니터 인스턴스 생성 시도
        if WatchHamsterV3Monitor:
            try:
                self.monitor = WatchHamsterV3Monitor()
                print("✅ WatchHamsterV3Monitor 인스턴스 생성 성공")
            except Exception as e:
                print(f"❌ WatchHamsterV3Monitor 인스턴스 생성 실패: {e}")
                self.monitor = None
    
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def test_restored_send_status_notification(self):
        """복원된 send_status_notification 함수 테스트"""
        self.log("📊 복원된 send_status_notification 함수 테스트 시작...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없어 테스트 불가")
            return False
        
        try:
            # 복원된 send_status_notification 함수 직접 호출
            result = self.monitor.send_status_notification()
            success = True
            message = f"복원된 함수 호출 성공 - 반환값: {result}"
            
        except Exception as e:
            success = False
            message = f"복원된 함수 호출 오류: {str(e)}"
        
        self.test_results.append({
            "test_type": "복원된 send_status_notification",
            "function_name": "send_status_notification",
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.log("✅ 복원된 send_status_notification 함수 테스트 성공")
        else:
            self.log(f"❌ 복원된 send_status_notification 함수 테스트 실패: {message}")
        
        return success
    
    def test_restored_send_notification(self):
        """복원된 send_notification 함수 테스트"""
        self.log("🔔 복원된 send_notification 함수 테스트 시작...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없어 테스트 불가")
            return False
        
        try:
            # 복원된 send_notification 함수 직접 호출
            test_message = "🧪 복원된 웹훅 함수 테스트 메시지입니다."
            result = self.monitor.send_notification(test_message, is_error=False)
            success = True
            message = f"복원된 함수 호출 성공 - 반환값: {result}"
            
        except Exception as e:
            success = False
            message = f"복원된 함수 호출 오류: {str(e)}"
        
        self.test_results.append({
            "test_type": "복원된 send_notification",
            "function_name": "send_notification",
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.log("✅ 복원된 send_notification 함수 테스트 성공")
        else:
            self.log(f"❌ 복원된 send_notification 함수 테스트 실패: {message}")
        
        return success
    
    def test_restored_send_enhanced_status_notification(self):
        """복원된 send_enhanced_status_notification 함수 테스트"""
        self.log("🚀 복원된 send_enhanced_status_notification 함수 테스트 시작...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없어 테스트 불가")
            return False
        
        try:
            # 복원된 send_enhanced_status_notification 함수 직접 호출
            result = self.monitor.send_enhanced_status_notification()
            success = True
            message = f"복원된 함수 호출 성공 - 반환값: {result}"
            
        except Exception as e:
            success = False
            message = f"복원된 함수 호출 오류: {str(e)}"
        
        self.test_results.append({
            "test_type": "복원된 send_enhanced_status_notification",
            "function_name": "send_enhanced_status_notification",
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.log("✅ 복원된 send_enhanced_status_notification 함수 테스트 성공")
        else:
            self.log(f"❌ 복원된 send_enhanced_status_notification 함수 테스트 실패: {message}")
        
        return success
    
    def check_restored_functions_exist(self):
        """복원된 함수들이 존재하는지 확인"""
        self.log("🔍 복원된 웹훅 함수들 존재 여부 확인...")
        
        if not self.monitor:
            self.log("❌ 모니터 인스턴스가 없어 확인 불가")
            return False
        
        expected_functions = [
            'send_status_notification',
            'send_notification', 
            'send_enhanced_status_notification',
            'send_startup_notification_v2',
            'send_process_error_v2',
            'send_recovery_success_v2',
            'send_critical_alert_v2',
            '_send_hourly_status_notification',
            'should_send_status_notification'
        ]
        
        existing_functions = []
        missing_functions = []
        
        for func_name in expected_functions:
            if hasattr(self.monitor, func_name):
                existing_functions.append(func_name)
                self.log(f"✅ {func_name} 함수 존재 확인")
            else:
                missing_functions.append(func_name)
                self.log(f"❌ {func_name} 함수 누락")
        
        function_check_result = {
            "total_expected": len(expected_functions),
            "existing_count": len(existing_functions),
            "missing_count": len(missing_functions),
            "existing_functions": existing_functions,
            "missing_functions": missing_functions,
            "success_rate": f"{(len(existing_functions)/len(expected_functions))*100:.1f}%"
        }
        
        self.test_results.append({
            "test_type": "복원된 함수 존재 여부 확인",
            "function_name": "function_existence_check",
            "success": len(missing_functions) == 0,
            "message": f"{len(existing_functions)}/{len(expected_functions)} 함수 존재",
            "details": function_check_result,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(missing_functions) == 0:
            self.log("✅ 모든 복원된 웹훅 함수가 존재합니다")
        else:
            self.log(f"⚠️ {len(missing_functions)}개 함수가 누락되었습니다")
        
        return len(missing_functions) == 0
    
    def run_all_tests(self):
        """모든 복원된 웹훅 함수 테스트 실행"""
        self.log("🚀 복원된 웹훅 함수 직접 테스트 시작")
        self.log(f"📅 테스트 시작 시간: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 80)
        
        # 함수 존재 여부 확인
        self.check_restored_functions_exist()
        self.log("-" * 60)
        
        # 개별 함수 테스트
        if self.monitor:
            tests = [
                ("복원된 send_status_notification", self.test_restored_send_status_notification),
                ("복원된 send_notification", self.test_restored_send_notification),
                ("복원된 send_enhanced_status_notification", self.test_restored_send_enhanced_status_notification)
            ]
            
            for test_name, test_func in tests:
                self.log(f"🔄 {test_name} 테스트 실행 중...")
                test_func()
                self.log("-" * 60)
        else:
            self.log("❌ 모니터 인스턴스가 없어 개별 함수 테스트 불가")
        
        # 결과 요약
        self.log("📊 복원된 웹훅 함수 테스트 결과 요약")
        self.log("=" * 80)
        
        success_count = sum(1 for result in self.test_results if result['success'])
        total_count = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ 성공" if result['success'] else "❌ 실패"
            self.log(f"{status} | {result['test_type']} | {result['message']}")
        
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
                "success_rate": f"{(success_count/total_count)*100:.1f}%"
            },
            "test_results": self.test_results,
            "monitor_instance_available": self.monitor is not None
        }
        
        return final_results

def main():
    """메인 함수"""
    print("🔧 POSCO 워치햄스터 복원된 웹훅 함수 직접 테스트")
    print("=" * 80)
    print("복원된 monitor_WatchHamster_v3.0.py의 웹훅 함수들을 직접 호출하여 테스트")
    print("=" * 80)
    
    tester = RestoredWebhookFunctionTester()
    results = tester.run_all_tests()
    
    # 결과를 JSON 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f'restored_webhook_function_test_results_{timestamp}.json'
    
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 테스트 결과가 '{result_filename}'에 저장되었습니다.")

if __name__ == "__main__":
    main()