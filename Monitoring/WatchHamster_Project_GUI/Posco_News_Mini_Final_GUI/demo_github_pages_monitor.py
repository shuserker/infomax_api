#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 모니터링 시스템 데모
POSCO 뉴스 시스템용 GitHub Pages 접근성 확인 시스템 데모

데모 시나리오:
- 🌐 단일 페이지 접근성 확인
- 🚀 배포 후 접근성 검증 시뮬레이션
- 📊 지속적인 모니터링 데모
- 🔄 자동 재배포 요청 시뮬레이션
- 🎨 GUI 모니터링 인터페이스 데모
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
    from github_pages_status_gui import GitHubPagesStatusGUI
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class GitHubPagesMonitorDemo:
    """GitHub Pages 모니터링 시스템 데모 클래스"""
    
    def __init__(self):
        self.monitor = GitHubPagesMonitor()
        
        # 데모용 URL들
        self.demo_urls = {
            "success": "https://httpbin.org/status/200",      # 성공 시뮬레이션
            "not_found": "https://httpbin.org/status/404",    # 404 오류
            "slow": "https://httpbin.org/delay/3",            # 느린 응답
            "timeout": "https://httpbin.org/delay/35",        # 타임아웃
            "invalid": "https://invalid-domain-12345.com"     # 잘못된 도메인
        }
        
        # 콜백 결과 저장
        self.callback_results = []
        
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """데모용 콜백 설정"""
        
        def status_callback(url, status, details):
            result = {
                "type": "status_change",
                "timestamp": datetime.now().strftime('%H:%M:%S'),
                "url": url,
                "status": status.value,
                "details": details
            }
            self.callback_results.append(result)
            print(f"📊 [{result['timestamp']}] 상태 변경: {url} -> {status.value}")
            if details:
                print(f"    세부사항: {details}")
        
        def accessibility_callback(check):
            result = {
                "type": "accessibility_check",
                "timestamp": check.timestamp,
                "url": check.url,
                "accessible": check.accessible,
                "response_time": check.response_time,
                "status_code": check.status_code,
                "error_message": check.error_message
            }
            self.callback_results.append(result)
            
            status_icon = "✅" if check.accessible else "❌"
            print(f"🔍 [{datetime.fromisoformat(check.timestamp).strftime('%H:%M:%S')}] {status_icon} 접근성 확인: {check.url}")
            
            if check.accessible:
                print(f"    응답시간: {check.response_time:.2f}초, 상태코드: {check.status_code}")
                if check.page_title:
                    print(f"    페이지 제목: {check.page_title}")
            else:
                print(f"    오류: {check.error_message}")
        
        def alert_callback(message, details):
            result = {
                "type": "alert",
                "timestamp": datetime.now().strftime('%H:%M:%S'),
                "message": message,
                "details": details
            }
            self.callback_results.append(result)
            print(f"🚨 [{result['timestamp']}] 알림: {message}")
            if details:
                print(f"    세부사항: {details}")
        
        def redeploy_callback(reason):
            result = {
                "type": "redeploy_request",
                "timestamp": datetime.now().strftime('%H:%M:%S'),
                "reason": reason
            }
            self.callback_results.append(result)
            print(f"🔄 [{result['timestamp']}] 재배포 요청: {reason}")
            return True  # 재배포 성공으로 시뮬레이션
        
        # 콜백 등록
        self.monitor.register_status_callback(status_callback)
        self.monitor.register_accessibility_callback(accessibility_callback)
        self.monitor.register_alert_callback(alert_callback)
        self.monitor.register_redeploy_callback(redeploy_callback)
    
    def demo_single_accessibility_check(self):
        """단일 페이지 접근성 확인 데모"""
        print("\n" + "="*60)
        print("🔍 단일 페이지 접근성 확인 데모")
        print("="*60)
        
        for name, url in self.demo_urls.items():
            print(f"\n📍 {name.upper()} 테스트: {url}")
            
            try:
                check = self.monitor.check_page_accessibility(url, timeout=10)
                
                if check.accessible:
                    print(f"✅ 접근 성공 - 응답시간: {check.response_time:.2f}초")
                else:
                    print(f"❌ 접근 실패 - {check.error_message}")
                
            except Exception as e:
                print(f"💥 테스트 중 오류: {str(e)}")
            
            time.sleep(1)  # 각 테스트 간 간격
    
    def demo_deployment_verification(self):
        """배포 후 접근성 검증 데모"""
        print("\n" + "="*60)
        print("🚀 배포 후 접근성 검증 데모")
        print("="*60)
        
        # 성공적인 배포 검증 시뮬레이션
        print(f"\n📍 성공적인 배포 검증 시뮬레이션")
        print(f"URL: {self.demo_urls['success']}")
        
        try:
            result = self.monitor.verify_github_pages_deployment(
                self.demo_urls['success'], 
                max_wait_time=60
            )
            
            if result['deployment_successful']:
                print(f"✅ 배포 검증 성공!")
                print(f"   확인 횟수: {result['checks_performed']}")
                print(f"   총 대기시간: {result['total_wait_time']:.1f}초")
            else:
                print(f"❌ 배포 검증 실패: {result.get('error_message', '알 수 없는 오류')}")
                
        except Exception as e:
            print(f"💥 검증 중 오류: {str(e)}")
        
        # 실패하는 배포 검증 시뮬레이션
        print(f"\n📍 실패하는 배포 검증 시뮬레이션")
        print(f"URL: {self.demo_urls['not_found']}")
        
        try:
            result = self.monitor.verify_github_pages_deployment(
                self.demo_urls['not_found'], 
                max_wait_time=30
            )
            
            if not result['deployment_successful']:
                print(f"❌ 예상대로 배포 검증 실패")
                print(f"   확인 횟수: {result['checks_performed']}")
                print(f"   총 대기시간: {result['total_wait_time']:.1f}초")
                print(f"   오류: {result.get('error_message', '알 수 없는 오류')}")
            else:
                print(f"⚠️ 예상과 다르게 검증 성공")
                
        except Exception as e:
            print(f"💥 검증 중 오류: {str(e)}")
    
    def demo_continuous_monitoring(self):
        """지속적인 모니터링 데모"""
        print("\n" + "="*60)
        print("📊 지속적인 모니터링 데모")
        print("="*60)
        
        print(f"URL: {self.demo_urls['success']}")
        print("모니터링 시작... (30초간 실행)")
        
        try:
            # 모니터링 시작
            session_id = self.monitor.start_continuous_monitoring(
                self.demo_urls['success'], 
                check_interval=5
            )
            
            print(f"📊 모니터링 세션 시작: {session_id}")
            
            # 30초간 모니터링 실행
            for i in range(6):
                time.sleep(5)
                
                # 현재 상태 조회
                status = self.monitor.get_current_status()
                if status and not status.get("error"):
                    print(f"   진행 상황: 확인 {status['total_checks']}회, 성공률 {status['success_rate']:.1f}%")
            
            # 모니터링 중지
            self.monitor.stop_continuous_monitoring()
            print("📊 모니터링 중지")
            
            # 최종 상태 확인
            final_status = self.monitor.get_current_status()
            if final_status and not final_status.get("error"):
                print(f"📈 최종 결과: 총 {final_status['total_checks']}회 확인, 성공률 {final_status['success_rate']:.1f}%")
            
        except Exception as e:
            print(f"💥 모니터링 중 오류: {str(e)}")
    
    def demo_auto_redeploy_request(self):
        """자동 재배포 요청 데모"""
        print("\n" + "="*60)
        print("🔄 자동 재배포 요청 데모")
        print("="*60)
        
        reasons = [
            "GitHub Pages 접근 실패",
            "연속 접근 실패 감지",
            "사용자 수동 요청",
            "배포 검증 타임아웃"
        ]
        
        for reason in reasons:
            print(f"\n📍 재배포 요청: {reason}")
            
            try:
                success = self.monitor.request_auto_redeploy(reason)
                
                if success:
                    print(f"✅ 재배포 요청 성공")
                else:
                    print(f"❌ 재배포 요청 실패")
                    
            except Exception as e:
                print(f"💥 재배포 요청 중 오류: {str(e)}")
            
            time.sleep(1)
    
    def demo_statistics_and_history(self):
        """통계 및 히스토리 조회 데모"""
        print("\n" + "="*60)
        print("📈 통계 및 히스토리 조회 데모")
        print("="*60)
        
        try:
            # 현재 상태 조회
            print("\n📊 현재 상태:")
            status = self.monitor.get_current_status()
            if status and not status.get("error"):
                print(f"   모니터링 활성: {status['monitoring_active']}")
                print(f"   총 확인 횟수: {status['total_checks']}")
                print(f"   성공률: {status['success_rate']:.1f}%")
                print(f"   평균 응답시간: {status['average_response_time']:.2f}초")
            else:
                print("   상태 정보 없음")
            
            # 접근성 히스토리 조회
            print("\n📋 접근성 히스토리:")
            history = self.monitor.get_accessibility_history(5)
            if history:
                for i, record in enumerate(history[:3], 1):
                    print(f"   {i}. 시작시간: {record.get('start_time', 'N/A')}")
                    print(f"      성공: {record.get('deployment_successful', False)}")
                    print(f"      확인횟수: {record.get('checks_performed', 0)}")
            else:
                print("   히스토리 없음")
            
            # 모니터링 통계 조회
            print("\n📈 모니터링 통계:")
            stats = self.monitor.get_monitoring_statistics()
            if stats and not stats.get("error"):
                if "accessibility" in stats:
                    acc_stats = stats["accessibility"]
                    print(f"   총 확인: {acc_stats.get('total_checks', 0)}회")
                    print(f"   성공: {acc_stats.get('successful_checks', 0)}회")
                    print(f"   실패: {acc_stats.get('failed_checks', 0)}회")
                
                print(f"   전체 성공률: {stats.get('success_rate', 0):.1f}%")
            else:
                print("   통계 정보 없음")
                
        except Exception as e:
            print(f"💥 통계 조회 중 오류: {str(e)}")
    
    def demo_callback_results(self):
        """콜백 결과 요약 데모"""
        print("\n" + "="*60)
        print("📞 콜백 결과 요약")
        print("="*60)
        
        # 콜백 타입별 카운트
        callback_counts = {}
        for result in self.callback_results:
            callback_type = result["type"]
            callback_counts[callback_type] = callback_counts.get(callback_type, 0) + 1
        
        print(f"\n📊 콜백 호출 통계:")
        for callback_type, count in callback_counts.items():
            print(f"   {callback_type}: {count}회")
        
        # 최근 콜백 결과 표시
        print(f"\n📋 최근 콜백 결과 (최대 5개):")
        recent_results = self.callback_results[-5:]
        for i, result in enumerate(recent_results, 1):
            print(f"   {i}. [{result['timestamp']}] {result['type']}")
            if result['type'] == 'accessibility_check':
                status = "✅" if result['accessible'] else "❌"
                print(f"      {status} {result['url']}")
            elif result['type'] == 'alert':
                print(f"      🚨 {result['message']}")
            elif result['type'] == 'redeploy_request':
                print(f"      🔄 {result['reason']}")
    
    def run_all_demos(self):
        """모든 데모 실행"""
        print("🎬 GitHub Pages 모니터링 시스템 데모 시작")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # 각 데모 실행
            self.demo_single_accessibility_check()
            self.demo_deployment_verification()
            self.demo_continuous_monitoring()
            self.demo_auto_redeploy_request()
            self.demo_statistics_and_history()
            self.demo_callback_results()
            
            end_time = time.time()
            
            # 데모 완료 요약
            print("\n" + "="*80)
            print("🎉 데모 완료 요약")
            print("="*80)
            print(f"총 실행 시간: {(end_time - start_time):.1f}초")
            print(f"총 콜백 호출: {len(self.callback_results)}회")
            print(f"데모 URL 수: {len(self.demo_urls)}개")
            
            # 시스템 정리
            print(f"\n🧹 시스템 정리 중...")
            if self.monitor.monitoring_active:
                self.monitor.stop_continuous_monitoring()
            
            print("✅ 모든 데모가 성공적으로 완료되었습니다!")
            
        except KeyboardInterrupt:
            print("\n⏹️ 사용자에 의해 데모가 중단되었습니다.")
        except Exception as e:
            print(f"\n💥 데모 실행 중 오류: {str(e)}")
    
    def run_gui_demo(self):
        """GUI 데모 실행"""
        print("\n" + "="*60)
        print("🎨 GUI 모니터링 인터페이스 데모")
        print("="*60)
        print("GUI 창이 열립니다. 창을 닫으면 데모가 종료됩니다.")
        
        try:
            gui = GitHubPagesStatusGUI()
            gui.show()
        except Exception as e:
            print(f"💥 GUI 데모 중 오류: {str(e)}")


def main():
    """메인 함수"""
    print("🚀 GitHub Pages 모니터링 시스템 데모")
    print("선택하세요:")
    print("1. 전체 데모 실행 (콘솔)")
    print("2. GUI 데모 실행")
    print("3. 종료")
    
    while True:
        try:
            choice = input("\n선택 (1-3): ").strip()
            
            if choice == "1":
                demo = GitHubPagesMonitorDemo()
                demo.run_all_demos()
                break
            elif choice == "2":
                demo = GitHubPagesMonitorDemo()
                demo.run_gui_demo()
                break
            elif choice == "3":
                print("👋 데모를 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1, 2, 또는 3을 입력하세요.")
                
        except KeyboardInterrupt:
            print("\n⏹️ 사용자에 의해 프로그램이 중단되었습니다.")
            break
        except Exception as e:
            print(f"💥 입력 처리 중 오류: {str(e)}")


if __name__ == "__main__":
    main()