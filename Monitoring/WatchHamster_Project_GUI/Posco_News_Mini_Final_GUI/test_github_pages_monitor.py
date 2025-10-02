#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 모니터링 시스템 테스트
POSCO 뉴스 시스템용 GitHub Pages 접근성 확인 시스템 테스트

테스트 항목:
- 🌐 단일 페이지 접근성 확인
- 🚀 배포 후 접근성 검증
- 📊 지속적인 모니터링
- 🔄 자동 재배포 요청
- 📈 상태 및 통계 조회
"""

import os
import sys
import time
import threading
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from github_pages_monitor import GitHubPagesMonitor, PageStatus, MonitoringMode
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class GitHubPagesMonitorTester:
    """GitHub Pages 모니터링 시스템 테스터"""
    
    def __init__(self):
        self.monitor = GitHubPagesMonitor()
        self.test_results = []
        
        # 테스트용 URL들
        self.test_urls = {
            "accessible": "https://httpbin.org/status/200",  # 접근 가능한 URL
            "not_found": "https://httpbin.org/status/404",   # 404 오류 URL
            "timeout": "https://httpbin.org/delay/35",       # 타임아웃 URL
            "invalid": "https://invalid-domain-12345.com"    # 잘못된 도메인
        }
        
        # GUI 콜백 테스트용
        self.callback_results = {
            "status_changes": [],
            "accessibility_checks": [],
            "alerts": [],
            "redeploy_requests": []
        }
        
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """테스트용 콜백 함수 설정"""
        
        def status_callback(url, status, details):
            self.callback_results["status_changes"].append({
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "status": status.value,
                "details": details
            })
            print(f"📊 상태 변경: {url} -> {status.value}")
        
        def accessibility_callback(check):
            self.callback_results["accessibility_checks"].append({
                "timestamp": check.timestamp,
                "url": check.url,
                "accessible": check.accessible,
                "response_time": check.response_time,
                "status_code": check.status_code
            })
            print(f"🔍 접근성 확인: {check.url} -> {'✅' if check.accessible else '❌'}")
        
        def alert_callback(message, details):
            self.callback_results["alerts"].append({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "details": details
            })
            print(f"🚨 알림: {message}")
        
        def redeploy_callback(reason):
            self.callback_results["redeploy_requests"].append({
                "timestamp": datetime.now().isoformat(),
                "reason": reason
            })
            print(f"🔄 재배포 요청: {reason}")
            return True  # 재배포 성공으로 시뮬레이션
        
        # 콜백 등록
        self.monitor.register_status_callback(status_callback)
        self.monitor.register_accessibility_callback(accessibility_callback)
        self.monitor.register_alert_callback(alert_callback)
        self.monitor.register_redeploy_callback(redeploy_callback)
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """테스트 결과 로깅"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {details}")
    
    def test_single_accessibility_check(self):
        """단일 페이지 접근성 확인 테스트"""
        print("\n🔍 단일 페이지 접근성 확인 테스트")
        
        try:
            # 접근 가능한 URL 테스트
            check = self.monitor.check_page_accessibility(self.test_urls["accessible"])
            if check.accessible and check.status_code == 200:
                self.log_test_result(
                    "접근 가능한 URL 확인", 
                    True, 
                    f"응답시간: {check.response_time:.2f}초"
                )
            else:
                self.log_test_result(
                    "접근 가능한 URL 확인", 
                    False, 
                    f"접근 실패: {check.error_message}"
                )
            
            # 404 오류 URL 테스트
            check = self.monitor.check_page_accessibility(self.test_urls["not_found"])
            if not check.accessible and check.status_code == 404:
                self.log_test_result(
                    "404 오류 URL 확인", 
                    True, 
                    f"예상대로 404 오류 발생"
                )
            else:
                self.log_test_result(
                    "404 오류 URL 확인", 
                    False, 
                    f"예상과 다른 결과: {check.status_code}"
                )
            
            # 잘못된 도메인 테스트
            check = self.monitor.check_page_accessibility(self.test_urls["invalid"])
            if not check.accessible and "연결 오류" in str(check.error_message):
                self.log_test_result(
                    "잘못된 도메인 확인", 
                    True, 
                    "예상대로 연결 오류 발생"
                )
            else:
                self.log_test_result(
                    "잘못된 도메인 확인", 
                    False, 
                    f"예상과 다른 결과: {check.error_message}"
                )
            
        except Exception as e:
            self.log_test_result("단일 접근성 확인", False, f"테스트 중 오류: {str(e)}")
    
    def test_deployment_verification(self):
        """배포 후 접근성 검증 테스트"""
        print("\n🚀 배포 후 접근성 검증 테스트")
        
        try:
            # 성공적인 배포 검증 테스트
            result = self.monitor.verify_github_pages_deployment(
                self.test_urls["accessible"], 
                max_wait_time=60
            )
            
            if result["deployment_successful"] and result["final_accessible"]:
                self.log_test_result(
                    "성공적인 배포 검증", 
                    True, 
                    f"확인 횟수: {result['checks_performed']}, 대기시간: {result['total_wait_time']:.1f}초"
                )
            else:
                self.log_test_result(
                    "성공적인 배포 검증", 
                    False, 
                    f"검증 실패: {result.get('error_message', '알 수 없는 오류')}"
                )
            
            # 실패하는 배포 검증 테스트
            result = self.monitor.verify_github_pages_deployment(
                self.test_urls["not_found"], 
                max_wait_time=30
            )
            
            if not result["deployment_successful"] and not result["final_accessible"]:
                self.log_test_result(
                    "실패하는 배포 검증", 
                    True, 
                    f"예상대로 검증 실패: {result.get('error_message', '접근 불가')}"
                )
            else:
                self.log_test_result(
                    "실패하는 배포 검증", 
                    False, 
                    "예상과 다르게 검증 성공"
                )
            
        except Exception as e:
            self.log_test_result("배포 검증", False, f"테스트 중 오류: {str(e)}")
    
    def test_continuous_monitoring(self):
        """지속적인 모니터링 테스트"""
        print("\n📊 지속적인 모니터링 테스트")
        
        try:
            # 모니터링 시작
            session_id = self.monitor.start_continuous_monitoring(
                self.test_urls["accessible"], 
                check_interval=5
            )
            
            if session_id:
                self.log_test_result(
                    "모니터링 시작", 
                    True, 
                    f"세션 ID: {session_id}"
                )
                
                # 10초간 모니터링 실행
                time.sleep(10)
                
                # 현재 상태 확인
                status = self.monitor.get_current_status()
                if status["monitoring_active"] and status["total_checks"] > 0:
                    self.log_test_result(
                        "모니터링 실행", 
                        True, 
                        f"확인 횟수: {status['total_checks']}, 성공률: {status['success_rate']:.1f}%"
                    )
                else:
                    self.log_test_result(
                        "모니터링 실행", 
                        False, 
                        "모니터링이 제대로 실행되지 않음"
                    )
                
                # 모니터링 중지
                self.monitor.stop_continuous_monitoring()
                
                # 중지 확인
                status = self.monitor.get_current_status()
                if not status["monitoring_active"]:
                    self.log_test_result(
                        "모니터링 중지", 
                        True, 
                        "모니터링이 성공적으로 중지됨"
                    )
                else:
                    self.log_test_result(
                        "모니터링 중지", 
                        False, 
                        "모니터링 중지 실패"
                    )
            else:
                self.log_test_result("모니터링 시작", False, "세션 ID 생성 실패")
            
        except Exception as e:
            self.log_test_result("지속적인 모니터링", False, f"테스트 중 오류: {str(e)}")
    
    def test_auto_redeploy_request(self):
        """자동 재배포 요청 테스트"""
        print("\n🔄 자동 재배포 요청 테스트")
        
        try:
            # 재배포 요청
            redeploy_success = self.monitor.request_auto_redeploy("테스트용 재배포 요청")
            
            if redeploy_success:
                self.log_test_result(
                    "자동 재배포 요청", 
                    True, 
                    "재배포 요청이 성공적으로 처리됨"
                )
            else:
                self.log_test_result(
                    "자동 재배포 요청", 
                    False, 
                    "재배포 요청 처리 실패"
                )
            
            # 콜백 결과 확인
            if self.callback_results["redeploy_requests"]:
                self.log_test_result(
                    "재배포 콜백", 
                    True, 
                    f"콜백 호출 횟수: {len(self.callback_results['redeploy_requests'])}"
                )
            else:
                self.log_test_result(
                    "재배포 콜백", 
                    False, 
                    "재배포 콜백이 호출되지 않음"
                )
            
        except Exception as e:
            self.log_test_result("자동 재배포 요청", False, f"테스트 중 오류: {str(e)}")
    
    def test_status_and_statistics(self):
        """상태 및 통계 조회 테스트"""
        print("\n📈 상태 및 통계 조회 테스트")
        
        try:
            # 현재 상태 조회
            status = self.monitor.get_current_status()
            if isinstance(status, dict) and "monitoring_active" in status:
                self.log_test_result(
                    "현재 상태 조회", 
                    True, 
                    f"모니터링 활성: {status['monitoring_active']}"
                )
            else:
                self.log_test_result(
                    "현재 상태 조회", 
                    False, 
                    "상태 조회 결과가 올바르지 않음"
                )
            
            # 접근성 히스토리 조회
            history = self.monitor.get_accessibility_history(10)
            if isinstance(history, list):
                self.log_test_result(
                    "접근성 히스토리 조회", 
                    True, 
                    f"히스토리 항목 수: {len(history)}"
                )
            else:
                self.log_test_result(
                    "접근성 히스토리 조회", 
                    False, 
                    "히스토리 조회 실패"
                )
            
            # 모니터링 통계 조회
            stats = self.monitor.get_monitoring_statistics()
            if isinstance(stats, dict) and "success_rate" in stats:
                self.log_test_result(
                    "모니터링 통계 조회", 
                    True, 
                    f"성공률: {stats['success_rate']:.1f}%"
                )
            else:
                self.log_test_result(
                    "모니터링 통계 조회", 
                    False, 
                    "통계 조회 실패"
                )
            
        except Exception as e:
            self.log_test_result("상태 및 통계 조회", False, f"테스트 중 오류: {str(e)}")
    
    def test_callback_functionality(self):
        """콜백 기능 테스트"""
        print("\n📞 콜백 기능 테스트")
        
        try:
            # 콜백 결과 확인
            callback_types = ["status_changes", "accessibility_checks", "alerts"]
            
            for callback_type in callback_types:
                callback_count = len(self.callback_results[callback_type])
                if callback_count > 0:
                    self.log_test_result(
                        f"{callback_type} 콜백", 
                        True, 
                        f"호출 횟수: {callback_count}"
                    )
                else:
                    self.log_test_result(
                        f"{callback_type} 콜백", 
                        False, 
                        "콜백이 호출되지 않음"
                    )
            
        except Exception as e:
            self.log_test_result("콜백 기능", False, f"테스트 중 오류: {str(e)}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 GitHub Pages 모니터링 시스템 테스트 시작")
        print("=" * 60)
        
        start_time = time.time()
        
        # 각 테스트 실행
        self.test_single_accessibility_check()
        self.test_deployment_verification()
        self.test_continuous_monitoring()
        self.test_auto_redeploy_request()
        self.test_status_and_statistics()
        self.test_callback_functionality()
        
        end_time = time.time()
        
        # 테스트 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {successful_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(successful_tests / total_tests * 100):.1f}%")
        print(f"실행 시간: {(end_time - start_time):.1f}초")
        
        # 실패한 테스트 상세 정보
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        # 콜백 결과 요약
        print(f"\n📞 콜백 호출 요약:")
        for callback_type, results in self.callback_results.items():
            print(f"  - {callback_type}: {len(results)}회")
        
        print("\n✅ 테스트 완료")
        
        return successful_tests == total_tests


def main():
    """메인 함수"""
    try:
        tester = GitHubPagesMonitorTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
            return 0
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"\n💥 테스트 실행 중 예상치 못한 오류: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)