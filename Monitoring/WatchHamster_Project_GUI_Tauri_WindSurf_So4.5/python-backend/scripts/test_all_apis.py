"""
전체 API 엔드포인트 검증 스크립트
"""

import requests
import json
from typing import Dict, Any, List
from datetime import datetime

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, data: Dict = None):
        """API 엔드포인트 테스트"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=5)
            elif method == "DELETE":
                response = requests.delete(url, timeout=5)
            
            success = response.status_code == expected_status
            
            result = {
                'method': method,
                'endpoint': endpoint,
                'status_code': response.status_code,
                'expected': expected_status,
                'success': success,
                'response_time': response.elapsed.total_seconds()
            }
            
            if success:
                self.passed += 1
                print(f"✅ {method:6} {endpoint:50} ({response.status_code}) - {response.elapsed.total_seconds():.3f}s")
            else:
                self.failed += 1
                print(f"❌ {method:6} {endpoint:50} ({response.status_code}) - Expected {expected_status}")
            
            self.results.append(result)
            return success
            
        except Exception as e:
            self.failed += 1
            print(f"❌ {method:6} {endpoint:50} - Error: {str(e)}")
            self.results.append({
                'method': method,
                'endpoint': endpoint,
                'success': False,
                'error': str(e)
            })
            return False
    
    def print_summary(self):
        """결과 요약 출력"""
        print("\n" + "=" * 80)
        print("📊 API 테스트 결과 요약")
        print("=" * 80)
        print(f"총 테스트: {self.passed + self.failed}개")
        print(f"✅ 성공: {self.passed}개")
        print(f"❌ 실패: {self.failed}개")
        print(f"성공률: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("=" * 80)
        
        # 느린 API 식별
        slow_apis = [r for r in self.results if r.get('response_time', 0) > 0.5]
        if slow_apis:
            print("\n⚠️ 느린 API (>0.5초):")
            for api in slow_apis:
                print(f"  {api['method']:6} {api['endpoint']:50} - {api['response_time']:.3f}s")


def main():
    print("🔍 WatchHamster API 전수검사 시작")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    tester = APITester()
    
    # ============= 회사 관리 API =============
    print("\n📁 회사 관리 API")
    print("-" * 80)
    tester.test_endpoint("GET", "/api/companies")
    tester.test_endpoint("GET", "/api/companies/posco")
    tester.test_endpoint("GET", "/api/companies/posco/stats")
    tester.test_endpoint("GET", "/api/companies/posco/webhooks")
    tester.test_endpoint("GET", "/api/companies/posco/api-configs")
    
    # ============= 웹훅 관리 API =============
    print("\n📬 웹훅 관리 API")
    print("-" * 80)
    tester.test_endpoint("GET", "/api/webhook-manager/stats?company_id=posco")
    tester.test_endpoint("GET", "/api/webhook-manager/logs?company_id=posco&limit=10")
    tester.test_endpoint("GET", "/api/webhook-manager/message-types")
    tester.test_endpoint("GET", "/api/webhook-manager/queue-status")
    
    # ============= 시스템 API =============
    print("\n🖥️ 시스템 API")
    print("-" * 80)
    tester.test_endpoint("GET", "/health")
    tester.test_endpoint("GET", "/api/system/status")
    tester.test_endpoint("GET", "/api/system/health")
    
    # ============= 로그 API =============
    print("\n📝 로그 API")
    print("-" * 80)
    tester.test_endpoint("GET", "/api/logs/")
    tester.test_endpoint("GET", "/api/monitor-logs/recent?limit=10")
    
    # ============= 설정 API =============
    print("\n⚙️ 설정 API")
    print("-" * 80)
    tester.test_endpoint("GET", "/api/config/monitors")
    tester.test_endpoint("GET", "/api/settings/all")
    
    # ============= 진단 API =============
    print("\n🔧 진단 API")
    print("-" * 80)
    tester.test_endpoint("GET", "/api/diagnostics/health-check")
    tester.test_endpoint("GET", "/api/diagnostics/config-info")
    
    # ============= 메트릭 API =============
    print("\n📊 메트릭 API")
    print("-" * 80)
    tester.test_endpoint("GET", "/api/metrics/summary")
    
    # 결과 요약
    tester.print_summary()
    
    # 결과 저장
    with open('api_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': tester.passed + tester.failed,
            'passed': tester.passed,
            'failed': tester.failed,
            'results': tester.results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 결과 저장: api_test_results.json")
    
    return tester.failed == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
