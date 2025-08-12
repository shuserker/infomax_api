#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시스템 실행 가능성 검증 도구
POSCO 시스템 수리 및 완성 - Task 5

모든 핵심 시스템 컴포넌트의 실행 가능성을 체계적으로 검증합니다.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class SystemExecutionVerifier:
    """시스템 실행 가능성 검증 클래스"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "python_scripts": {},
            "shell_scripts": {},
            "batch_scripts": {},
            "webhook_tests": {},
            "module_imports": {},
            "overall_status": "UNKNOWN"
        }
        
    def log(self, message: str, level: str = "INFO"):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def verify_python_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Python 파일 구문 검증"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout"
        except Exception as e:
            return False, str(e)
            
    def test_module_import(self, module_path: Path) -> Tuple[bool, str]:
        """모듈 import 테스트"""
        try:
            # 상대 경로를 모듈명으로 변환
            relative_path = module_path.relative_to(self.script_dir)
            module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            
            result = subprocess.run(
                [sys.executable, "-c", f"import {module_name}; print('SUCCESS')"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.script_dir)
            )
            
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                return True, "Import successful"
            else:
                return False, result.stderr or result.stdout
                
        except subprocess.TimeoutExpired:
            return False, "Import timeout"
        except Exception as e:
            return False, str(e)
            
    def test_script_execution(self, script_path: Path, timeout: int = 10) -> Tuple[bool, str]:
        """스크립트 실행 테스트 (짧은 시간)"""
        try:
            if script_path.suffix == ".py":
                cmd = [sys.executable, str(script_path)]
            elif script_path.suffix == ".sh":
                cmd = ["bash", str(script_path)]
            elif script_path.suffix == ".bat":
                cmd = ["cmd", "/c", str(script_path)]
            else:
                return False, "Unsupported script type"
                
            # 스크립트를 짧은 시간만 실행하여 시작 가능성 확인
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(script_path.parent)
            )
            
            # 짧은 시간 대기 후 프로세스 종료
            time.sleep(timeout)
            
            if process.poll() is None:
                # 아직 실행 중이면 성공적으로 시작된 것
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                return True, "Script started successfully"
            else:
                # 이미 종료됨 - 출력 확인
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    return True, "Script completed successfully"
                else:
                    return False, stderr or stdout or "Script failed"
                    
        except Exception as e:
            return False, str(e)
            
    def test_webhook_connectivity(self, webhook_url: str) -> Tuple[bool, str]:
        """웹훅 연결성 테스트 (실제 메시지 전송 없이)"""
        try:
            import requests
            
            # HEAD 요청으로 연결성만 확인
            response = requests.head(webhook_url, timeout=10)
            
            if response.status_code in [200, 405]:  # 405는 HEAD 메서드 미지원이지만 연결은 됨
                return True, f"Webhook accessible (status: {response.status_code})"
            else:
                return False, f"Webhook returned status: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
            
    def verify_watchhamster_control_center(self) -> Dict[str, any]:
        """워치햄스터 제어센터 검증"""
        self.log("🐹 워치햄스터 제어센터 검증 시작")
        
        results = {}
        
        # BAT 파일 검증
        bat_file = self.script_dir / "🐹POSCO_워치햄스터_v3_제어센터.bat"
        if bat_file.exists():
            success, message = self.test_script_execution(bat_file, timeout=5)
            results["bat_control_center"] = {
                "exists": True,
                "executable": success,
                "message": message
            }
            self.log(f"  BAT 제어센터: {'✅' if success else '❌'} {message}")
        else:
            results["bat_control_center"] = {
                "exists": False,
                "executable": False,
                "message": "File not found"
            }
            self.log("  BAT 제어센터: ❌ 파일 없음")
            
        # Command 파일 검증
        cmd_file = self.script_dir / "🐹POSCO_워치햄스터_v3_제어센터.command"
        if cmd_file.exists():
            success, message = self.test_script_execution(cmd_file, timeout=5)
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
                "message": "File not found"
            }
            self.log("  Command 제어센터: ❌ 파일 없음")
            
        return results
        
    def verify_posco_news_monitoring(self) -> Dict[str, any]:
        """포스코 뉴스 모니터링 시스템 검증"""
        self.log("📰 포스코 뉴스 모니터링 시스템 검증 시작")
        
        results = {}
        
        # 메인 뉴스 파일 검증
        main_news_file = self.script_dir / "POSCO_News_250808.py"
        if main_news_file.exists():
            syntax_ok, syntax_msg = self.verify_python_syntax(main_news_file)
            results["main_news_file"] = {
                "exists": True,
                "syntax_valid": syntax_ok,
                "message": syntax_msg
            }
            self.log(f"  메인 뉴스 파일: {'✅' if syntax_ok else '❌'} {syntax_msg}")
        else:
            results["main_news_file"] = {
                "exists": False,
                "syntax_valid": False,
                "message": "File not found"
            }
            self.log("  메인 뉴스 파일: ❌ 파일 없음")
            
        # 모니터링 디렉토리 내 파일들 검증
        monitoring_dir = self.script_dir / "Monitoring" / "POSCO_News_250808"
        if monitoring_dir.exists():
            # WatchHamster 모니터 검증
            watchhamster_file = monitoring_dir / "monitor_WatchHamster_v3.0.py"
            if watchhamster_file.exists():
                syntax_ok, syntax_msg = self.verify_python_syntax(watchhamster_file)
                results["watchhamster_monitor"] = {
                    "exists": True,
                    "syntax_valid": syntax_ok,
                    "message": syntax_msg
                }
                self.log(f"  WatchHamster 모니터: {'✅' if syntax_ok else '❌'} {syntax_msg}")
            else:
                results["watchhamster_monitor"] = {
                    "exists": False,
                    "syntax_valid": False,
                    "message": "File not found"
                }
                self.log("  WatchHamster 모니터: ❌ 파일 없음")
                
            # 메인 알림자 검증
            notifier_file = monitoring_dir / "posco_main_notifier.py"
            if notifier_file.exists():
                syntax_ok, syntax_msg = self.verify_python_syntax(notifier_file)
                results["main_notifier"] = {
                    "exists": True,
                    "syntax_valid": syntax_ok,
                    "message": syntax_msg
                }
                self.log(f"  메인 알림자: {'✅' if syntax_ok else '❌'} {syntax_msg}")
            else:
                results["main_notifier"] = {
                    "exists": False,
                    "syntax_valid": False,
                    "message": "File not found"
                }
                self.log("  메인 알림자: ❌ 파일 없음")
                
        return results
        
    def verify_shell_batch_scripts(self) -> Dict[str, any]:
        """배치/셸 스크립트 검증"""
        self.log("🔧 배치/셸 스크립트 검증 시작")
        
        results = {}
        
        # 주요 시작 스크립트들
        start_scripts = [
            "🚀🚀POSCO_News_250808_Direct_Start.sh",
            "🚀🚀POSCO_News_250808_Direct_Start.bat",
        ]
        
        for script_name in start_scripts:
            script_path = self.script_dir / script_name
            if script_path.exists():
                success, message = self.test_script_execution(script_path, timeout=3)
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
        
    def verify_webhook_functionality(self) -> Dict[str, any]:
        """웹훅 기능 검증 (내용 변경 없이)"""
        self.log("🔗 웹훅 기능 검증 시작")
        
        results = {}
        
        # config.py에서 웹훅 URL 추출
        config_file = self.script_dir / "Monitoring" / "POSCO_News_250808" / "config.py"
        webhook_urls = []
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 웹훅 URL 패턴 찾기
                import re
                url_pattern = r'https://[^"\']*dooray\.com[^"\']*'
                urls = re.findall(url_pattern, content)
                webhook_urls.extend(urls)
                
            except Exception as e:
                self.log(f"  Config 파일 읽기 실패: {e}")
                
        # 각 웹훅 URL 테스트
        for i, url in enumerate(webhook_urls):
            success, message = self.test_webhook_connectivity(url)
            results[f"webhook_{i+1}"] = {
                "url": url[:50] + "..." if len(url) > 50 else url,
                "accessible": success,
                "message": message
            }
            self.log(f"  웹훅 {i+1}: {'✅' if success else '❌'} {message}")
            
        if not webhook_urls:
            results["no_webhooks"] = {
                "message": "No webhook URLs found in config"
            }
            self.log("  웹훅: ⚠️ 설정에서 웹훅 URL을 찾을 수 없음")
            
        return results
        
    def run_comprehensive_verification(self) -> Dict[str, any]:
        """종합 시스템 검증 실행"""
        self.log("🚀 시스템 실행 가능성 종합 검증 시작")
        self.log("=" * 60)
        
        # 1. 워치햄스터 제어센터 검증
        self.results["watchhamster_control"] = self.verify_watchhamster_control_center()
        
        # 2. 포스코 뉴스 모니터링 시스템 검증
        self.results["posco_news_monitoring"] = self.verify_posco_news_monitoring()
        
        # 3. 배치/셸 스크립트 검증
        self.results["shell_batch_scripts"] = self.verify_shell_batch_scripts()
        
        # 4. 웹훅 기능 검증
        self.results["webhook_functionality"] = self.verify_webhook_functionality()
        
        # 5. 전체 결과 분석
        self.analyze_overall_status()
        
        self.log("=" * 60)
        self.log("🏁 시스템 검증 완료")
        
        return self.results
        
    def analyze_overall_status(self):
        """전체 상태 분석"""
        total_tests = 0
        passed_tests = 0
        
        # 각 카테고리별 성공률 계산
        categories = {
            "watchhamster_control": ["executable"],
            "posco_news_monitoring": ["syntax_valid"],
            "shell_batch_scripts": ["executable"],
            "webhook_functionality": ["accessible"]
        }
        
        for category, success_keys in categories.items():
            if category in self.results:
                for item_key, item_data in self.results[category].items():
                    if isinstance(item_data, dict):
                        total_tests += 1
                        # 성공 조건 확인
                        if any(item_data.get(key, False) for key in success_keys):
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
                
            self.results["success_rate"] = success_rate
            self.results["total_tests"] = total_tests
            self.results["passed_tests"] = passed_tests
            
            self.log(f"📊 전체 성공률: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            self.log(f"🎯 전체 상태: {self.results['overall_status']}")
        else:
            self.results["overall_status"] = "NO_TESTS"
            self.log("⚠️ 실행된 테스트가 없습니다")
            
    def save_results(self, output_file: str = "system_execution_verification_results.json"):
        """결과를 JSON 파일로 저장"""
        output_path = self.script_dir / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            self.log(f"📄 결과 저장됨: {output_path}")
        except Exception as e:
            self.log(f"❌ 결과 저장 실패: {e}")
            
    def print_summary(self):
        """검증 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 시스템 실행 가능성 검증 결과 요약")
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
        
        if "success_rate" in self.results:
            print(f"📊 성공률: {self.results['success_rate']:.1f}% ({self.results['passed_tests']}/{self.results['total_tests']})")
            
        print()
        
        # 카테고리별 요약
        categories = {
            "watchhamster_control": "🐹 워치햄스터 제어센터",
            "posco_news_monitoring": "📰 포스코 뉴스 모니터링",
            "shell_batch_scripts": "🔧 배치/셸 스크립트",
            "webhook_functionality": "🔗 웹훅 기능"
        }
        
        for category, title in categories.items():
            if category in self.results:
                category_data = self.results[category]
                total = len([k for k, v in category_data.items() if isinstance(v, dict)])
                
                if category == "webhook_functionality":
                    passed = len([k for k, v in category_data.items() 
                                if isinstance(v, dict) and v.get("accessible", False)])
                elif category in ["watchhamster_control", "shell_batch_scripts"]:
                    passed = len([k for k, v in category_data.items() 
                                if isinstance(v, dict) and v.get("executable", False)])
                else:  # posco_news_monitoring
                    passed = len([k for k, v in category_data.items() 
                                if isinstance(v, dict) and v.get("syntax_valid", False)])
                
                if total > 0:
                    rate = (passed / total) * 100
                    status = "✅" if rate >= 75 else "⚠️" if rate >= 50 else "❌"
                    print(f"{status} {title}: {rate:.0f}% ({passed}/{total})")
                else:
                    print(f"❓ {title}: 테스트 없음")
                    
        print("=" * 60)

def main():
    """메인 실행 함수"""
    verifier = SystemExecutionVerifier()
    
    try:
        # 종합 검증 실행
        results = verifier.run_comprehensive_verification()
        
        # 결과 저장
        verifier.save_results()
        
        # 요약 출력
        verifier.print_summary()
        
        # 성공률에 따른 종료 코드
        success_rate = results.get("success_rate", 0)
        if success_rate >= 75:
            sys.exit(0)  # 성공
        else:
            sys.exit(1)  # 실패
            
    except KeyboardInterrupt:
        verifier.log("❌ 사용자에 의해 중단됨")
        sys.exit(2)
    except Exception as e:
        verifier.log(f"❌ 예상치 못한 오류: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()