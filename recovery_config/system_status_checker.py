#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 상태 확인 도구
전체 시스템의 상태를 종합적으로 점검
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

class SystemStatusChecker:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.recovery_config = self.workspace_root / "recovery_config"
        self.platform = platform.system().lower()
        
        # 필수 모듈들
        self.required_modules = [
            "integrated_news_parser.py",
            "watchhamster_monitor.py",
            "webhook_sender.py",
            "api_connection_manager.py",
            "ai_analysis_engine.py",
            "business_day_comparison_engine.py",
            "git_monitor.py"
        ]
        
        # 필수 테스트 파일들
        self.required_tests = [
            "test_api_modules.py",
            "test_news_parsers.py",
            "test_webhook_sender.py",
            "test_watchhamster_monitor.py"
        ]
    
    def check_python_environment(self) -> Dict:
        """Python 환경 상태 확인"""
        print("🐍 Python 환경을 확인하고 있습니다...")
        
        status = {
            "python_version": None,
            "python_available": False,
            "pip_available": False,
            "required_packages": [],
            "missing_packages": [],
            "issues": []
        }
        
        try:
            # Python 버전 확인
            python_cmd = "python3" if self.platform != "windows" else "python"
            result = subprocess.run([python_cmd, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                status["python_version"] = result.stdout.strip()
                status["python_available"] = True
                print(f"   ✅ Python: {status['python_version']}")
            else:
                status["issues"].append("Python을 실행할 수 없습니다")
                print("   ❌ Python 실행 실패")
            
            # pip 확인
            pip_result = subprocess.run([python_cmd, "-m", "pip", "--version"],
                                      capture_output=True, text=True, timeout=10)
            status["pip_available"] = pip_result.returncode == 0
            
            if status["pip_available"]:
                print("   ✅ pip 사용 가능")
            else:
                status["issues"].append("pip를 사용할 수 없습니다")
                print("   ❌ pip 사용 불가")
            
            # 필수 패키지 확인
            required_packages = ["requests", "pathlib", "json", "datetime"]
            for package in required_packages:
                try:
                    __import__(package)
                    status["required_packages"].append(package)
                    print(f"   ✅ 패키지: {package}")
                except ImportError:
                    status["missing_packages"].append(package)
                    print(f"   ❌ 누락 패키지: {package}")
        
        except Exception as e:
            status["issues"].append(f"Python 환경 확인 오류: {e}")
            print(f"   ❌ 환경 확인 오류: {e}")
        
        return status
    
    def check_recovery_modules(self) -> Dict:
        """복구 모듈들 상태 확인"""
        print("🔧 복구 모듈들을 확인하고 있습니다...")
        
        status = {
            "existing_modules": [],
            "missing_modules": [],
            "broken_modules": [],
            "module_details": {}
        }
        
        for module_name in self.required_modules:
            module_path = self.recovery_config / module_name
            
            if module_path.exists():
                try:
                    # 파일 크기 확인
                    size = module_path.stat().st_size
                    
                    # 기본 구문 확인
                    content = module_path.read_text(encoding='utf-8', errors='ignore')
                    
                    if size > 100 and 'def ' in content:  # 최소한의 유효성 검사
                        status["existing_modules"].append(module_name)
                        status["module_details"][module_name] = {
                            "size": size,
                            "functions": len([line for line in content.split('\n') if line.strip().startswith('def ')]),
                            "classes": len([line for line in content.split('\n') if line.strip().startswith('class ')])
                        }
                        print(f"   ✅ 모듈: {module_name} ({size} bytes)")
                    else:
                        status["broken_modules"].append(module_name)
                        print(f"   ⚠️ 손상된 모듈: {module_name}")
                
                except Exception as e:
                    status["broken_modules"].append(module_name)
                    print(f"   ❌ 모듈 읽기 오류: {module_name} - {e}")
            else:
                status["missing_modules"].append(module_name)
                print(f"   ❌ 누락 모듈: {module_name}")
        
        return status
    
    def check_test_files(self) -> Dict:
        """테스트 파일들 상태 확인"""
        print("🧪 테스트 파일들을 확인하고 있습니다...")
        
        status = {
            "existing_tests": [],
            "missing_tests": [],
            "test_results": {}
        }
        
        for test_name in self.required_tests:
            test_path = self.recovery_config / test_name
            
            if test_path.exists():
                status["existing_tests"].append(test_name)
                print(f"   ✅ 테스트: {test_name}")
                
                # 간단한 테스트 실행 (import 테스트)
                try:
                    python_cmd = "python3" if self.platform != "windows" else "python"
                    result = subprocess.run([python_cmd, "-c", f"import sys; sys.path.append('recovery_config'); import {test_name[:-3]}"],
                                          capture_output=True, text=True, timeout=5)
                    
                    status["test_results"][test_name] = {
                        "importable": result.returncode == 0,
                        "error": result.stderr if result.returncode != 0 else None
                    }
                    
                    if result.returncode == 0:
                        print(f"      ✅ Import 성공")
                    else:
                        print(f"      ⚠️ Import 실패: {result.stderr[:50]}...")
                
                except Exception as e:
                    status["test_results"][test_name] = {
                        "importable": False,
                        "error": str(e)
                    }
                    print(f"      ❌ 테스트 오류: {e}")
            else:
                status["missing_tests"].append(test_name)
                print(f"   ❌ 누락 테스트: {test_name}")
        
        return status
    
    def check_execution_files(self) -> Dict:
        """실행 파일들 상태 확인"""
        print("🚀 실행 파일들을 확인하고 있습니다...")
        
        status = {
            "windows_files": [],
            "mac_files": [],
            "missing_files": [],
            "executable_files": []
        }
        
        # Windows 실행 파일들
        windows_files = [
            "POSCO_메인_system.bat",
            "POSCO_watchhamster_v3_control_center.bat",
            "POSCO_News_250808_Start.bat",
            "POSCO_News_250808_Stop.bat",
            "POSCO_test_실행.bat"
        ]
        
        for filename in windows_files:
            file_path = self.workspace_root / filename
            if file_path.exists():
                status["windows_files"].append(filename)
                print(f"   ✅ Windows: {filename}")
            else:
                status["missing_files"].append(filename)
                print(f"   ❌ 누락: {filename}")
        
        # Mac 실행 파일들
        mac_files = [
            "POSCO_watchhamster_v3_control_center.command",
            "POSCO_News_250808_Start.sh",
            "WatchHamster_v3.0_Control_Panel.command"
        ]
        
        for filename in mac_files:
            file_path = self.workspace_root / filename
            if file_path.exists():
                status["mac_files"].append(filename)
                
                # 실행 권한 확인 (Mac/Linux)
                if self.platform != "windows" and os.access(file_path, os.X_OK):
                    status["executable_files"].append(filename)
                    print(f"   ✅ Mac (실행가능): {filename}")
                else:
                    print(f"   ⚠️ Mac (권한없음): {filename}")
            else:
                status["missing_files"].append(filename)
                print(f"   ❌ 누락: {filename}")
        
        return status
    
    def check_system_resources(self) -> Dict:
        """시스템 리소스 상태 확인"""
        print("💻 시스템 리소스를 확인하고 있습니다...")
        
        status = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "disk_space": None,
            "memory_info": None,
            "cpu_info": None
        }
        
        try:
            # 디스크 공간 확인
            disk_usage = os.statvfs(self.workspace_root) if hasattr(os, 'statvfs') else None
            if disk_usage:
                free_space = disk_usage.f_bavail * disk_usage.f_frsize
                status["disk_space"] = f"{free_space // (1024**3)} GB"
                print(f"   ✅ 디스크 여유공간: {status['disk_space']}")
            
            # 플랫폼 정보
            print(f"   ✅ 플랫폼: {status['platform']}")
            print(f"   ✅ Python 버전: {status['python_version']}")
            
        except Exception as e:
            print(f"   ⚠️ 리소스 확인 제한: {e}")
        
        return status
    
    def generate_status_report(self, python_status: Dict, module_status: Dict,
                             test_status: Dict, execution_status: Dict,
                             resource_status: Dict) -> str:
        """상태 보고서 생성"""
        print("📊 시스템 상태 보고서를 생성하고 있습니다...")
        
        # 전체 상태 점수 계산
        total_score = 0
        max_score = 0
        
        # Python 환경 점수
        if python_status["python_available"]:
            total_score += 20
        max_score += 20
        
        # 모듈 점수
        module_score = len(module_status["existing_modules"]) / len(self.required_modules) * 30
        total_score += module_score
        max_score += 30
        
        # 테스트 점수
        test_score = len(test_status["existing_tests"]) / len(self.required_tests) * 25
        total_score += test_score
        max_score += 25
        
        # 실행 파일 점수
        exec_score = (len(execution_status["windows_files"]) + len(execution_status["mac_files"])) / 8 * 25
        total_score += exec_score
        max_score += 25
        
        health_percentage = round(total_score / max_score * 100, 1)
        
        report = f"""# POSCO 시스템 상태 확인 보고서

## 전체 시스템 상태
- **시스템 건강도**: {health_percentage}% ({'🟢 양호' if health_percentage >= 80 else '🟡 주의' if health_percentage >= 60 else '🔴 위험'})
- **확인 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **플랫폼**: {resource_status['platform']}

## Python 환경 상태
- **Python 사용 가능**: {'✅' if python_status['python_available'] else '❌'}
- **Python 버전**: {python_status.get('python_version', 'N/A')}
- **pip 사용 가능**: {'✅' if python_status['pip_available'] else '❌'}
- **필수 패키지**: {len(python_status['required_packages'])}개 설치됨
- **누락 패키지**: {len(python_status['missing_packages'])}개

### Python 환경 문제점
{chr(10).join(f"- {issue}" for issue in python_status['issues']) if python_status['issues'] else "문제점 없음"}

## 복구 모듈 상태
- **존재하는 모듈**: {len(module_status['existing_modules'])}/{len(self.required_modules)}개
- **누락된 모듈**: {len(module_status['missing_modules'])}개
- **손상된 모듈**: {len(module_status['broken_modules'])}개

### 모듈 상세 정보
{chr(10).join(f"- ✅ {module}: {details['functions']}개 함수, {details['classes']}개 클래스" for module, details in module_status['module_details'].items())}

### 누락된 모듈
{chr(10).join(f"- ❌ {module}" for module in module_status['missing_modules']) if module_status['missing_modules'] else "누락된 모듈 없음"}

## 테스트 파일 상태
- **존재하는 테스트**: {len(test_status['existing_tests'])}/{len(self.required_tests)}개
- **누락된 테스트**: {len(test_status['missing_tests'])}개

### 테스트 실행 결과
{chr(10).join(f"- {'✅' if result['importable'] else '❌'} {test}: {'Import 성공' if result['importable'] else f'오류 - {result.get(\"error\", \"알 수 없음\")[:50]}...'}" for test, result in test_status['test_results'].items())}

## 실행 파일 상태
- **Windows 실행 파일**: {len(execution_status['windows_files'])}개
- **Mac 실행 파일**: {len(execution_status['mac_files'])}개
- **실행 권한 있는 파일**: {len(execution_status['executable_files'])}개
- **누락된 파일**: {len(execution_status['missing_files'])}개

### Windows 실행 파일
{chr(10).join(f"- ✅ {file}" for file in execution_status['windows_files'])}

### Mac 실행 파일
{chr(10).join(f"- ✅ {file}" for file in execution_status['mac_files'])}

## 시스템 리소스
- **플랫폼**: {resource_status['platform']}
- **Python 버전**: {resource_status['python_version']}
- **디스크 여유공간**: {resource_status.get('disk_space', 'N/A')}

## 권장 조치사항
{self._generate_recommendations(python_status, module_status, test_status, execution_status)}

## 결론
{'✅ 시스템이 정상적으로 작동하고 있습니다.' if health_percentage >= 80 else '⚠️ 일부 문제가 발견되었습니다. 권장 조치사항을 확인하세요.' if health_percentage >= 60 else '🔴 심각한 문제가 발견되었습니다. 즉시 조치가 필요합니다.'}

시스템 상태 확인이 완료되었습니다!
"""
        
        report_path = self.recovery_config / "system_status_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 상태 보고서 생성: {report_path}")
        return report
    
    def _generate_recommendations(self, python_status: Dict, module_status: Dict,
                                test_status: Dict, execution_status: Dict) -> str:
        """권장 조치사항 생성"""
        recommendations = []
        
        if not python_status["python_available"]:
            recommendations.append("1. Python을 설치하거나 PATH 환경변수를 확인하세요")
        
        if python_status["missing_packages"]:
            recommendations.append(f"2. 누락된 패키지를 설치하세요: {', '.join(python_status['missing_packages'])}")
        
        if module_status["missing_modules"]:
            recommendations.append("3. 누락된 복구 모듈들을 복원하세요")
        
        if module_status["broken_modules"]:
            recommendations.append("4. 손상된 모듈들을 수리하거나 재생성하세요")
        
        if test_status["missing_tests"]:
            recommendations.append("5. 누락된 테스트 파일들을 생성하세요")
        
        if execution_status["missing_files"]:
            recommendations.append("6. 누락된 실행 파일들을 복원하세요")
        
        if not recommendations:
            recommendations.append("현재 시스템 상태가 양호합니다. 정기적인 모니터링을 계속하세요.")
        
        return chr(10).join(recommendations)

def main():
    """메인 실행 함수"""
    print("🔍 POSCO 시스템 상태 확인을 시작합니다...")
    print("=" * 60)
    
    checker = SystemStatusChecker()
    
    try:
        # 1. Python 환경 확인
        python_status = checker.check_python_environment()
        
        # 2. 복구 모듈 확인
        module_status = checker.check_recovery_modules()
        
        # 3. 테스트 파일 확인
        test_status = checker.check_test_files()
        
        # 4. 실행 파일 확인
        execution_status = checker.check_execution_files()
        
        # 5. 시스템 리소스 확인
        resource_status = checker.check_system_resources()
        
        # 6. 상태 보고서 생성
        report = checker.generate_status_report(
            python_status, module_status, test_status,
            execution_status, resource_status
        )
        
        print("=" * 60)
        print("🎉 시스템 상태 확인이 완료되었습니다!")
        print(report)
        
    except Exception as e:
        print(f"❌ 상태 확인 중 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()