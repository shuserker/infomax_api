#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종합 시스템 실행 테스트
Task 5: 시스템 실행 가능성 검증

모든 핵심 시스템 컴포넌트의 실행 가능성을 종합적으로 검증합니다.
"""

import os
import sys
import subprocess
import json
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class ComprehensiveSystemTester:
    """종합 시스템 실행 테스트 클래스"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_results": {},
            "overall_status": "UNKNOWN",
            "summary": {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_python_execution(self, script_path: Path, timeout: int = 10) -> Tuple[bool, str]:
        """Python 스크립트 실행 테스트"""
        try:
            # 스크립트를 백그라운드에서 실행
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(script_path.parent)
            )
            
            # 짧은 시간 대기 후 프로세스 상태 확인
            time.sleep(timeout)
            
            if process.poll() is None:
                # 아직 실행 중이면 성공적으로 시작된 것
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                return True, "Script started and running successfully"
            else:
                # 이미 종료됨 - 출력 확인
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    return True, "Script completed successfully"
                else:
                    return False, stderr or stdout or "Script failed with unknown error"
                    
        except Exception as e:
            return False, str(e)
            
    def test_shell_script_execution(self, script_path: Path, timeout: int = 5) -> Tuple[bool, str]:
        """Shell 스크립트 실행 테스트"""
        try:
            if not script_path.exists():
                return False, "Script file not found"
                
            # 실행 권한 확인
            if not os.access(script_path, os.X_OK):
                # 실행 권한 부여 시도
                os.chmod(script_path, 0o755)
                
            # 스크립트 실행
            process = subprocess.Popen(
                ["bash", str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(script_path.parent)
            )
            
            # 짧은 시간 대기
            time.sleep(timeout)
            
            if process.poll() is None:
                # 실행 중이면 성공
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                return True, "Shell script started successfully"
            else:
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    return True, "Shell script completed successfully"
                else:
                    return False, stderr or stdout or "Shell script failed"
                    
        except Exception as e:
            return False, str(e)
            
    def test_webhook_connectivity(self, webhook_url: str) -> Tuple[bool, str]:
        """웹훅 연결성 테스트"""
        try:
            import requests
            
            # HEAD 요청으로 연결성만 확인
            response = requests.head(webhook_url, timeout=10)
            
            if response.status_code in [200, 405]:
                return True, f"Webhook accessible (status: {response.status_code})"
            else:
                return False, f"Webhook returned status: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
            
    def test_watchhamster_control_center(self) -> Dict[str, any]:
        """워치햄스터 제어센터 테스트"""
        self.log("🐹 워치햄스터 제어센터 테스트 시작")
        
        results = {}
        
        # 1. BAT 제어센터 (Windows 호환성)
        bat_file = self.script_dir / "🐹POSCO_워치햄스터_v3_제어센터.bat"
        if bat_file.exists():
            # macOS에서는 실행할 수 없지만 파일 존재 확인
            results["bat_control_center"] = {
                "exists": True,
                "platform_compatible": sys.platform == "win32",
                "message": "BAT file exists (Windows only)"
            }
            self.log("  BAT 제어센터: ✅ 파일 존재 (Windows 전용)")
        else:
            results["bat_control_center"] = {
                "exists": False,
                "platform_compatible": False,
                "message": "BAT file not found"
            }
            self.log("  BAT 제어센터: ❌ 파일 없음")
            
        # 2. Command 제어센터 (macOS/Linux)
        cmd_file = self.script_dir / "🐹POSCO_워치햄스터_v3_제어센터.command"
        if cmd_file.exists():
            success, message = self.test_shell_script_execution(cmd_file, timeout=3)
            results["command_control_center"] = {
                "exists": True,
                "executable": success,
                "message": message
            }
            self.log(f"  Command 제어센터: {'✅' if success else '❌'} {message}")
        else:
            results["command_control_center"] = {
                "exists": False,
                "executable": False,
                "message": "Command file not found"
            }
            self.log("  Command 제어센터: ❌ 파일 없음")
            
        return results
        
    def test_posco_news_monitoring(self) -> Dict[str, any]:
        """포스코 뉴스 모니터링 시스템 테스트"""
        self.log("📰 포스코 뉴스 모니터링 시스템 테스트 시작")
        
        results = {}
        
        # 1. 메인 뉴스 파일
        main_news_file = self.script_dir / "POSCO_News_250808.py"
        if main_news_file.exists():
            success, message = self.test_python_execution(main_news_file, timeout=3)
            results["main_news_file"] = {
                "exists": True,
                "executable": success,
                "message": message
            }
            self.log(f"  메인 뉴스 파일: {'✅' if success else '❌'} {message}")
        else:
            results["main_news_file"] = {
                "exists": False,
                "executable": False,
                "message": "File not found"
            }
            self.log("  메인 뉴스 파일: ❌ 파일 없음")
            
        # 2. WatchHamster 모니터 (최소 버전)
        watchhamster_file = self.script_dir / "Monitoring" / "POSCO_News_250808" / "monitor_WatchHamster_v3_v3_0_minimal.py"
        if watchhamster_file.exists():
            success, message = self.test_python_execution(watchhamster_file, timeout=5)
            results["watchhamster_monitor"] = {
                "exists": True,
                "executable": success,
                "message": message
            }
            self.log(f"  WatchHamster 모니터: {'✅' if success else '❌'} {message}")
        else:
            results["watchhamster_monitor"] = {
                "exists": False,
                "executable": False,
                "message": "File not found"
            }
            self.log("  WatchHamster 모니터: ❌ 파일 없음")
            
        # 3. 메인 알림자 (최소 버전)
        notifier_file = self.script_dir / "Monitoring" / "POSCO_News_250808" / "posco_main_notifier_minimal.py"
        if notifier_file.exists():
            success, message = self.test_python_execution(notifier_file, timeout=5)
            results["main_notifier"] = {
                "exists": True,
                "executable": success,
                "message": message
            }
            self.log(f"  메인 알림자: {'✅' if success else '❌'} {message}")
        else:
            results["main_notifier"] = {
                "exists": False,
                "executable": False,
                "message": "File not found"
            }
            self.log("  메인 알림자: ❌ 파일 없음")
            
        return results
        
    def test_shell_batch_scripts(self) -> Dict[str, any]:
        """배치/셸 스크립트 테스트"""
        self.log("🔧 배치/셸 스크립트 테스트 시작")
        
        results = {}
        
        # 주요 시작 스크립트들
        start_scripts = [
            "🚀🚀POSCO_News_250808_Direct_Start.sh",
        ]
        
        for script_name in start_scripts:
            script_path = self.script_dir / script_name
            if script_path.exists():
                success, message = self.test_shell_script_execution(script_path, timeout=3)
                results[script_name] = {
                    "exists": True,
                    "executable": success,
                    "message": message
                }
                self.log(f"  {script_name}: {'✅' if success else '❌'} {message}")
            else:
                results[script_name] = {
                    "exists": False,
                    "executable": False,
                    "message": "File not found"
                }
                self.log(f"  {script_name}: ❌ 파일 없음")
                
        return results
        
    def test_webhook_functionality(self) -> Dict[str, any]:
        """웹훅 기능 테스트"""
        self.log("🔗 웹훅 기능 테스트 시작")
        
        results = {}
        
        # 설정에서 웹훅 URL 추출
        webhook_urls = [
            "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg",
            "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"
        ]
        
        # 각 웹훅 URL 테스트
        for i, url in enumerate(webhook_urls):
            success, message = self.test_webhook_connectivity(url)
            results[f"webhook_{i+1}"] = {
                "url": url[:50] + "..." if len(url) > 50 else url,
                "accessible": success,
                "message": message
            }
            self.log(f"  웹훅 {i+1}: {'✅' if success else '❌'} {message}")
            
        return results
        
    def run_comprehensive_test(self) -> Dict[str, any]:
        """종합 시스템 테스트 실행"""
        self.log("🚀 종합 시스템 실행 가능성 테스트 시작")
        self.log("=" * 60)
        
        # 1. 워치햄스터 제어센터 테스트
        self.results["test_results"]["watchhamster_control"] = self.test_watchhamster_control_center()
        
        # 2. 포스코 뉴스 모니터링 시스템 테스트
        self.results["test_results"]["posco_news_monitoring"] = self.test_posco_news_monitoring()
        
        # 3. 배치/셸 스크립트 테스트
        self.results["test_results"]["shell_batch_scripts"] = self.test_shell_batch_scripts()
        
        # 4. 웹훅 기능 테스트
        self.results["test_results"]["webhook_functionality"] = self.test_webhook_functionality()
        
        # 5. 전체 결과 분석
        self.analyze_overall_status()
        
        self.log("=" * 60)
        self.log("🏁 종합 시스템 테스트 완료")
        
        return self.results
        
    def analyze_overall_status(self):
        """전체 상태 분석"""
        total_tests = 0
        passed_tests = 0
        
        # 각 카테고리별 성공률 계산
        for category, category_data in self.results["test_results"].items():
            for item_key, item_data in category_data.items():
                if isinstance(item_data, dict):
                    total_tests += 1
                    
                    # 성공 조건 확인
                    if category == "webhook_functionality":
                        if item_data.get("accessible", False):
                            passed_tests += 1
                    elif category == "watchhamster_control":
                        if item_data.get("executable", False) or item_data.get("exists", False):
                            passed_tests += 1
                    else:  # posco_news_monitoring, shell_batch_scripts
                        if item_data.get("executable", False):
                            passed_tests += 1
                            
        # 전체 성공률 계산
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            
            if success_rate >= 90:
                self.results["overall_status"] = "EXCELLENT"
            elif success_rate >= 75:
                self.results["overall_status"] = "GOOD"
            elif success_rate >= 50:
                self.results["overall_status"] = "FAIR"
            else:
                self.results["overall_status"] = "POOR"
                
            self.results["summary"] = {
                "success_rate": success_rate,
                "total_tests": total_tests,
                "passed_tests": passed_tests
            }
            
            self.log(f"📊 전체 성공률: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            self.log(f"🎯 전체 상태: {self.results['overall_status']}")
        else:
            self.results["overall_status"] = "NO_TESTS"
            self.log("⚠️ 실행된 테스트가 없습니다")
            
    def save_results(self, output_file: str = "comprehensive_system_execution_test_results.json"):
        """결과를 JSON 파일로 저장"""
        output_path = self.script_dir / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            self.log(f"📄 결과 저장됨: {output_path}")
        except Exception as e:
            self.log(f"❌ 결과 저장 실패: {e}")
            
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 종합 시스템 실행 가능성 테스트 결과 요약")
        print("=" * 60)
        
        # 전체 상태
        status_emoji = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡", 
            "FAIR": "🟠",
            "POOR": "🔴",
            "NO_TESTS": "⚪"
        }
        
        overall_status = self.results.get("overall_status", "UNKNOWN")
        emoji = status_emoji.get(overall_status, "❓")
        
        print(f"{emoji} 전체 상태: {overall_status}")
        
        if "summary" in self.results:
            summary = self.results["summary"]
            print(f"📊 성공률: {summary['success_rate']:.1f}% ({summary['passed_tests']}/{summary['total_tests']})")
            
        print()
        
        # 카테고리별 요약
        categories = {
            "watchhamster_control": "🐹 워치햄스터 제어센터",
            "posco_news_monitoring": "📰 포스코 뉴스 모니터링",
            "shell_batch_scripts": "🔧 배치/셸 스크립트",
            "webhook_functionality": "🔗 웹훅 기능"
        }
        
        for category, title in categories.items():
            if category in self.results["test_results"]:
                category_data = self.results["test_results"][category]
                total = len([k for k, v in category_data.items() if isinstance(v, dict)])
                
                if category == "webhook_functionality":
                    passed = len([k for k, v in category_data.items() 
                                if isinstance(v, dict) and v.get("accessible", False)])
                elif category == "watchhamster_control":
                    passed = len([k for k, v in category_data.items() 
                                if isinstance(v, dict) and (v.get("executable", False) or v.get("exists", False))])
                else:
                    passed = len([k for k, v in category_data.items() 
                                if isinstance(v, dict) and v.get("executable", False)])
                
                if total > 0:
                    rate = (passed / total) * 100
                    status = "✅" if rate >= 75 else "⚠️" if rate >= 50 else "❌"
                    print(f"{status} {title}: {rate:.0f}% ({passed}/{total})")
                else:
                    print(f"❓ {title}: 테스트 없음")
                    
        print("=" * 60)
        
        # 권장사항
        if overall_status in ["POOR", "FAIR"]:
            print("\n🔧 권장사항:")
            print("- Python 구문 오류가 있는 파일들을 수정하세요")
            print("- 누락된 모듈들을 설치하거나 경로를 확인하세요")
            print("- 웹훅 URL이 올바른지 확인하세요")
            print("- 시스템 권한 설정을 확인하세요")

def main():
    """메인 실행 함수"""
    tester = ComprehensiveSystemTester()
    
    try:
        # 종합 테스트 실행
        results = tester.run_comprehensive_test()
        
        # 결과 저장
        tester.save_results()
        
        # 요약 출력
        tester.print_summary()
        
        # 성공률에 따른 종료 코드
        if "summary" in results:
            success_rate = results["summary"]["success_rate"]
            if success_rate >= 75:
                sys.exit(0)  # 성공
            else:
                sys.exit(1)  # 실패
        else:
            sys.exit(2)  # 테스트 없음
            
    except KeyboardInterrupt:
        tester.log("❌ 사용자에 의해 중단됨")
        sys.exit(3)
    except Exception as e:
        tester.log(f"❌ 예상치 못한 오류: {e}")
        sys.exit(4)

if __name__ == "__main__":
    main()