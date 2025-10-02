#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 모니터링 시스템 빠른 검증
실제 동작 확인용 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def quick_verify():
    """빠른 검증 실행"""
    print("🔍 GitHub Pages 모니터링 시스템 빠른 검증")
    print("=" * 50)
    
    try:
        # 1. 모듈 임포트 테스트
        print("1️⃣ 모듈 임포트 테스트...")
        from github_pages_monitor import GitHubPagesMonitor, PageStatus
        print("   ✅ github_pages_monitor 임포트 성공")
        
        from github_pages_status_gui import GitHubPagesStatusGUI
        print("   ✅ github_pages_status_gui 임포트 성공")
        
        # 2. 인스턴스 생성 테스트
        print("\n2️⃣ 인스턴스 생성 테스트...")
        monitor = GitHubPagesMonitor()
        print("   ✅ GitHubPagesMonitor 인스턴스 생성 성공")
        
        # 3. 실제 HTTP 요청 테스트
        print("\n3️⃣ 실제 HTTP 요청 테스트...")
        test_url = "https://httpbin.org/status/200"
        check = monitor.check_page_accessibility(test_url, timeout=10)
        
        print(f"   URL: {test_url}")
        print(f"   접근 가능: {check.accessible}")
        print(f"   상태 코드: {check.status_code}")
        print(f"   응답 시간: {check.response_time:.2f}초")
        
        if check.accessible and check.status_code == 200:
            print("   ✅ HTTP 요청 테스트 성공")
        else:
            print("   ❌ HTTP 요청 테스트 실패")
            return False
        
        # 4. 콜백 시스템 테스트
        print("\n4️⃣ 콜백 시스템 테스트...")
        callback_called = False
        
        def test_callback(check_result):
            nonlocal callback_called
            callback_called = True
            print(f"   콜백 호출됨: {check_result.url} -> {check_result.accessible}")
        
        monitor.register_accessibility_callback(test_callback)
        
        # 콜백 테스트용 요청
        monitor.check_page_accessibility("https://httpbin.org/status/404", timeout=5)
        
        if callback_called:
            print("   ✅ 콜백 시스템 테스트 성공")
        else:
            print("   ❌ 콜백 시스템 테스트 실패")
            return False
        
        # 5. 상태 조회 테스트
        print("\n5️⃣ 상태 조회 테스트...")
        status = monitor.get_current_status()
        
        if isinstance(status, dict) and "monitoring_active" in status:
            print("   ✅ 상태 조회 테스트 성공")
            print(f"   모니터링 활성: {status['monitoring_active']}")
            print(f"   총 확인 횟수: {status['total_checks']}")
        else:
            print("   ❌ 상태 조회 테스트 실패")
            return False
        
        # 6. 통계 조회 테스트
        print("\n6️⃣ 통계 조회 테스트...")
        stats = monitor.get_monitoring_statistics()
        
        if isinstance(stats, dict) and "success_rate" in stats:
            print("   ✅ 통계 조회 테스트 성공")
            print(f"   성공률: {stats['success_rate']:.1f}%")
        else:
            print("   ❌ 통계 조회 테스트 실패")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 모든 테스트 성공! GitHub Pages 모니터링 시스템이 완벽하게 작동합니다!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 검증 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_verify()
    sys.exit(0 if success else 1)