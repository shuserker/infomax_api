#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 플랫폼별 실행 파일 복원 도구
정상 커밋 기준으로 Windows(.bat)와 Mac(.sh/.command) 실행 파일 복원
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import json
import re

class PlatformExecutionRestorer:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.current_platform = platform.system().lower()
        
        # 정상 커밋 기준 실행 파일 템플릿
        self.execution_templates = {
            "windows": {
                "posco_main_system": {
                    "filename": "POSCO_메인_system.bat",
                    "content": self._get_windows_main_template()
                },
                "posco_control_center": {
                    "filename": "POSCO_watchhamster_v3_control_center.bat",
                    "content": self._get_windows_control_template()
                },
                "posco_news_start": {
                    "filename": "POSCO_News_250808_Start.bat",
                    "content": self._get_windows_news_start_template()
                },
                "posco_news_stop": {
                    "filename": "POSCO_News_250808_Stop.bat",
                    "content": self._get_windows_news_stop_template()
                },
                "posco_test": {
                    "filename": "POSCO_test_실행.bat",
                    "content": self._get_windows_test_template()
                }
            },
            "mac": {
                "posco_control_center": {
                    "filename": "POSCO_watchhamster_v3_control_center.command",
                    "content": self._get_mac_control_template()
                },
                "posco_news_start": {
                    "filename": "POSCO_News_250808_Start.sh",
                    "content": self._get_mac_news_start_template()
                },
                "watchhamster_control": {
                    "filename": "WatchHamster_v3.0_Control_Panel.command",
                    "content": self._get_mac_watchhamster_template()
                }
            }
        }
        
        # 환경 변수 설정
        self.env_configs = {
            "windows": {
                "PYTHON_PATH": "python",
                "PATH_SEPARATOR": "\\",
                "SCRIPT_EXTENSION": ".py",
                "SHELL_ENCODING": "cp949"
            },
            "mac": {
                "PYTHON_PATH": "python3",
                "PATH_SEPARATOR": "/",
                "SCRIPT_EXTENSION": ".py",
                "SHELL_ENCODING": "utf-8"
            }
        }
    
    def _get_windows_main_template(self) -> str:
        """Windows 메인 시스템 실행 파일 템플릿"""
        return '''@echo off
chcp 65001 > nul
title POSCO 메인 시스템 제어센터

echo.
echo ==========================================
echo    POSCO 메인 시스템 제어센터 v3.0
echo ==========================================
echo.

:MENU
echo [1] POSCO 뉴스 모니터링 시작
echo [2] 워치햄스터 모니터링 시작  
echo [3] 전체 시스템 상태 확인
echo [4] 테스트 실행
echo [5] 시스템 종료
echo [0] 종료
echo.
set /p choice="선택하세요 (0-5): "

if "%choice%"=="1" goto NEWS_START
if "%choice%"=="2" goto WATCHHAMSTER_START
if "%choice%"=="3" goto STATUS_CHECK
if "%choice%"=="4" goto TEST_RUN
if "%choice%"=="5" goto SYSTEM_STOP
if "%choice%"=="0" goto EXIT
goto MENU

:NEWS_START
echo.
echo POSCO 뉴스 모니터링을 시작합니다...
python recovery_config/integrated_news_parser.py
goto MENU

:WATCHHAMSTER_START
echo.
echo 워치햄스터 모니터링을 시작합니다...
python recovery_config/watchhamster_monitor.py
goto MENU

:STATUS_CHECK
echo.
echo 시스템 상태를 확인합니다...
python recovery_config/system_status_checker.py
goto MENU

:TEST_RUN
echo.
echo 테스트를 실행합니다...
python -m pytest recovery_config/test_*.py -v
goto MENU

:SYSTEM_STOP
echo.
echo 모든 시스템을 종료합니다...
taskkill /f /im python.exe 2>nul
echo 시스템이 종료되었습니다.
goto MENU

:EXIT
echo.
echo POSCO 시스템을 종료합니다.
pause
exit
'''
    
    def _get_windows_control_template(self) -> str:
        """Windows 워치햄스터 제어센터 템플릿"""
        return '''@echo off
chcp 65001 > nul
title POSCO 워치햄스터 v3.0 제어센터

echo.
echo ==========================================
echo    POSCO 워치햄스터 v3.0 제어센터
echo ==========================================
echo.

:MENU
echo [1] 워치햄스터 모니터링 시작
echo [2] 웹훅 테스트
echo [3] AI 분석 실행
echo [4] 비즈니스 데이 비교
echo [5] 상태 확인
echo [0] 종료
echo.
set /p choice="선택하세요 (0-5): "

if "%choice%"=="1" goto MONITOR_START
if "%choice%"=="2" goto WEBHOOK_TEST
if "%choice%"=="3" goto AI_ANALYSIS
if "%choice%"=="4" goto BUSINESS_DAY
if "%choice%"=="5" goto STATUS
if "%choice%"=="0" goto EXIT
goto MENU

:MONITOR_START
echo.
echo 워치햄스터 모니터링을 시작합니다...
python recovery_config/watchhamster_monitor.py
goto MENU

:WEBHOOK_TEST
echo.
echo 웹훅 테스트를 실행합니다...
python recovery_config/test_webhook_sender.py
goto MENU

:AI_ANALYSIS
echo.
echo AI 분석을 실행합니다...
python recovery_config/ai_analysis_engine.py
goto MENU

:BUSINESS_DAY
echo.
echo 비즈니스 데이 비교를 실행합니다...
python recovery_config/business_day_comparison_engine.py
goto MENU

:STATUS
echo.
echo 시스템 상태를 확인합니다...
python recovery_config/git_monitor.py --status
goto MENU

:EXIT
echo.
echo 워치햄스터 제어센터를 종료합니다.
pause
exit
'''
    
    def _get_windows_news_start_template(self) -> str:
        """Windows 뉴스 시작 템플릿"""
        return '''@echo off
chcp 65001 > nul
title POSCO News 250808 시작

echo.
echo ==========================================
echo    POSCO News 250808 모니터링 시작
echo ==========================================
echo.

echo 뉴스 모니터링 시스템을 시작합니다...
echo.

REM API 연결 테스트
echo [1/4] API 연결 상태 확인 중...
python recovery_config/api_connection_manager.py --test

REM 뉴스 파서 초기화
echo [2/4] 뉴스 파서 초기화 중...
python recovery_config/integrated_news_parser.py --init

REM 웹훅 연결 테스트
echo [3/4] 웹훅 연결 테스트 중...
python recovery_config/webhook_sender.py --test

REM 모니터링 시작
echo [4/4] 모니터링 시작...
python recovery_config/integrated_news_parser.py --monitor

echo.
echo POSCO News 모니터링이 시작되었습니다.
echo 종료하려면 POSCO_News_250808_Stop.bat을 실행하세요.
pause
'''
    
    def _get_windows_news_stop_template(self) -> str:
        """Windows 뉴스 중지 템플릿"""
        return '''@echo off
chcp 65001 > nul
title POSCO News 250808 중지

echo.
echo ==========================================
echo    POSCO News 250808 모니터링 중지
echo ==========================================
echo.

echo 뉴스 모니터링 시스템을 중지합니다...
echo.

REM Python 프로세스 종료
echo [1/2] 모니터링 프로세스 종료 중...
taskkill /f /im python.exe 2>nul

REM 정리 작업
echo [2/2] 정리 작업 수행 중...
python recovery_config/integrated_news_parser.py --cleanup

echo.
echo POSCO News 모니터링이 중지되었습니다.
pause
'''
    
    def _get_windows_test_template(self) -> str:
        """Windows 테스트 실행 템플릿"""
        return '''@echo off
chcp 65001 > nul
title POSCO 테스트 실행

echo.
echo ==========================================
echo    POSCO 시스템 테스트 실행
echo ==========================================
echo.

echo 전체 시스템 테스트를 실행합니다...
echo.

REM 환경 설정 테스트
echo [1/6] 환경 설정 테스트...
python recovery_config/test_environment_setup.py

REM API 모듈 테스트
echo [2/6] API 모듈 테스트...
python recovery_config/test_api_modules.py

REM 뉴스 파서 테스트
echo [3/6] 뉴스 파서 테스트...
python recovery_config/test_news_parsers.py

REM 웹훅 전송 테스트
echo [4/6] 웹훅 전송 테스트...
python recovery_config/test_webhook_sender.py

REM 모니터링 시스템 테스트
echo [5/6] 모니터링 시스템 테스트...
python recovery_config/test_watchhamster_monitor.py

REM 통합 테스트
echo [6/6] 통합 테스트...
python -m pytest recovery_config/ -v

echo.
echo 모든 테스트가 완료되었습니다.
pause
'''
    
    def _get_mac_control_template(self) -> str:
        """Mac 제어센터 템플릿"""
        return '''#!/bin/bash

# POSCO 워치햄스터 v3.0 제어센터 (Mac)
clear
echo "=========================================="
echo "   POSCO 워치햄스터 v3.0 제어센터"
echo "=========================================="
echo

while true; do
    echo "[1] 워치햄스터 모니터링 시작"
    echo "[2] 웹훅 테스트"
    echo "[3] AI 분석 실행"
    echo "[4] 비즈니스 데이 비교"
    echo "[5] 상태 확인"
    echo "[0] 종료"
    echo
    read -p "선택하세요 (0-5): " choice
    
    case $choice in
        1)
            echo
            echo "워치햄스터 모니터링을 시작합니다..."
            python3 recovery_config/watchhamster_monitor.py
            ;;
        2)
            echo
            echo "웹훅 테스트를 실행합니다..."
            python3 recovery_config/test_webhook_sender.py
            ;;
        3)
            echo
            echo "AI 분석을 실행합니다..."
            python3 recovery_config/ai_analysis_engine.py
            ;;
        4)
            echo
            echo "비즈니스 데이 비교를 실행합니다..."
            python3 recovery_config/business_day_comparison_engine.py
            ;;
        5)
            echo
            echo "시스템 상태를 확인합니다..."
            python3 recovery_config/git_monitor.py --status
            ;;
        0)
            echo
            echo "워치햄스터 제어센터를 종료합니다."
            exit 0
            ;;
        *)
            echo "잘못된 선택입니다. 다시 선택해주세요."
            ;;
    esac
    echo
    read -p "계속하려면 Enter를 누르세요..."
    clear
    echo "=========================================="
    echo "   POSCO 워치햄스터 v3.0 제어센터"
    echo "=========================================="
    echo
done
'''
    
    def _get_mac_news_start_template(self) -> str:
        """Mac 뉴스 시작 템플릿"""
        return '''#!/bin/bash

# POSCO News 250808 모니터링 시작 (Mac)
clear
echo "=========================================="
echo "   POSCO News 250808 모니터링 시작"
echo "=========================================="
echo

echo "뉴스 모니터링 시스템을 시작합니다..."
echo

# API 연결 테스트
echo "[1/4] API 연결 상태 확인 중..."
python3 recovery_config/api_connection_manager.py --test

# 뉴스 파서 초기화
echo "[2/4] 뉴스 파서 초기화 중..."
python3 recovery_config/integrated_news_parser.py --init

# 웹훅 연결 테스트
echo "[3/4] 웹훅 연결 테스트 중..."
python3 recovery_config/webhook_sender.py --test

# 모니터링 시작
echo "[4/4] 모니터링 시작..."
python3 recovery_config/integrated_news_parser.py --monitor

echo
echo "POSCO News 모니터링이 시작되었습니다."
echo "종료하려면 Ctrl+C를 누르거나 별도 터미널에서 중지 스크립트를 실행하세요."
read -p "계속하려면 Enter를 누르세요..."
'''
    
    def _get_mac_watchhamster_template(self) -> str:
        """Mac 워치햄스터 템플릿"""
        return '''#!/bin/bash

# WatchHamster v3.0 Control Panel (Mac)
clear
echo "=========================================="
echo "   WatchHamster v3.0 Control Panel"
echo "=========================================="
echo

while true; do
    echo "[1] 통합 모니터링 시작"
    echo "[2] 뉴스 모니터링만 시작"
    echo "[3] 워치햄스터만 시작"
    echo "[4] 전체 테스트 실행"
    echo "[5] 시스템 상태 확인"
    echo "[0] 종료"
    echo
    read -p "선택하세요 (0-5): " choice
    
    case $choice in
        1)
            echo
            echo "통합 모니터링을 시작합니다..."
            python3 recovery_config/integrated_news_parser.py &
            python3 recovery_config/watchhamster_monitor.py &
            echo "통합 모니터링이 백그라운드에서 실행 중입니다."
            ;;
        2)
            echo
            echo "뉴스 모니터링을 시작합니다..."
            python3 recovery_config/integrated_news_parser.py
            ;;
        3)
            echo
            echo "워치햄스터 모니터링을 시작합니다..."
            python3 recovery_config/watchhamster_monitor.py
            ;;
        4)
            echo
            echo "전체 테스트를 실행합니다..."
            python3 -m pytest recovery_config/test_*.py -v
            ;;
        5)
            echo
            echo "시스템 상태를 확인합니다..."
            python3 recovery_config/git_monitor.py --status
            ;;
        0)
            echo
            echo "WatchHamster Control Panel을 종료합니다."
            # 백그라운드 프로세스 종료
            pkill -f "python3 recovery_config"
            exit 0
            ;;
        *)
            echo "잘못된 선택입니다. 다시 선택해주세요."
            ;;
    esac
    echo
    read -p "계속하려면 Enter를 누르세요..."
    clear
    echo "=========================================="
    echo "   WatchHamster v3.0 Control Panel"
    echo "=========================================="
    echo
done
'''
    
    def analyze_current_execution_files(self) -> Dict:
        """현재 실행 파일들 분석"""
        print("🔍 현재 실행 파일들을 분석하고 있습니다...")
        
        analysis = {
            "windows_files": [],
            "mac_files": [],
            "broken_files": [],
            "missing_files": [],
            "platform_issues": []
        }
        
        try:
            # .bat 파일 분석
            for bat_file in self.workspace_root.rglob('*.bat'):
                try:
                    relative_path = bat_file.relative_to(self.workspace_root)
                    analysis["windows_files"].append({
                        "path": str(relative_path),
                        "size": bat_file.stat().st_size,
                        "exists": True
                    })
                    
                    # 파일 내용 검사
                    try:
                        content = bat_file.read_text(encoding='utf-8', errors='ignore')
                        if len(content.strip()) < 50:  # 너무 짧은 파일
                            analysis["broken_files"].append(str(relative_path))
                        elif 'python' not in content.lower():  # Python 실행이 없는 파일
                            analysis["platform_issues"].append(f"{relative_path}: Python 실행 명령 없음")
                    except Exception as e:
                        analysis["broken_files"].append(f"{relative_path}: 읽기 오류 - {e}")
                except Exception as e:
                    print(f"   ⚠️ .bat 파일 처리 오류: {bat_file} - {e}")
            
            # .sh/.command 파일 분석
            for script_file in list(self.workspace_root.rglob('*.sh')) + list(self.workspace_root.rglob('*.command')):
                try:
                    relative_path = script_file.relative_to(self.workspace_root)
                    analysis["mac_files"].append({
                        "path": str(relative_path),
                        "size": script_file.stat().st_size,
                        "exists": True
                    })
                    
                    # 파일 내용 검사
                    try:
                        content = script_file.read_text(encoding='utf-8', errors='ignore')
                        if len(content.strip()) < 50:  # 너무 짧은 파일
                            analysis["broken_files"].append(str(relative_path))
                        elif 'python' not in content.lower():  # Python 실행이 없는 파일
                            analysis["platform_issues"].append(f"{relative_path}: Python 실행 명령 없음")
                    except Exception as e:
                        analysis["broken_files"].append(f"{relative_path}: 읽기 오류 - {e}")
                except Exception as e:
                    print(f"   ⚠️ 스크립트 파일 처리 오류: {script_file} - {e}")
        
        except Exception as e:
            print(f"   ❌ 파일 분석 중 오류: {e}")
        
        print(f"✅ 분석 완료:")
        print(f"   - Windows 파일: {len(analysis['windows_files'])}개")
        print(f"   - Mac 파일: {len(analysis['mac_files'])}개")
        print(f"   - 문제 파일: {len(analysis['broken_files'])}개")
        print(f"   - 플랫폼 이슈: {len(analysis['platform_issues'])}개")
        
        return analysis
    
    def restore_windows_execution_files(self) -> List[str]:
        """Windows 실행 파일들 복원"""
        print("🪟 Windows 실행 파일들을 복원하고 있습니다...")
        
        restored_files = []
        
        for script_name, script_info in self.execution_templates["windows"].items():
            file_path = self.workspace_root / script_info["filename"]
            
            try:
                # 기존 파일 백업
                if file_path.exists():
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    file_path.rename(backup_path)
                    print(f"   📦 백업: {script_info['filename']} → {backup_path.name}")
                
                # 새 파일 생성
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(script_info["content"])
                
                restored_files.append(script_info["filename"])
                print(f"   ✅ 복원: {script_info['filename']}")
                
            except Exception as e:
                print(f"   ❌ 복원 실패: {script_info['filename']} - {e}")
        
        return restored_files
    
    def restore_mac_execution_files(self) -> List[str]:
        """Mac 실행 파일들 복원"""
        print("🍎 Mac 실행 파일들을 복원하고 있습니다...")
        
        restored_files = []
        
        for script_name, script_info in self.execution_templates["mac"].items():
            file_path = self.workspace_root / script_info["filename"]
            
            try:
                # 기존 파일 백업
                if file_path.exists():
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    file_path.rename(backup_path)
                    print(f"   📦 백업: {script_info['filename']} → {backup_path.name}")
                
                # 새 파일 생성
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(script_info["content"])
                
                # 실행 권한 부여
                os.chmod(file_path, 0o755)
                
                restored_files.append(script_info["filename"])
                print(f"   ✅ 복원: {script_info['filename']} (실행 권한 부여)")
                
            except Exception as e:
                print(f"   ❌ 복원 실패: {script_info['filename']} - {e}")
        
        return restored_files
    
    def create_platform_environment_handler(self) -> str:
        """플랫폼별 환경 처리 핸들러 생성"""
        print("⚙️ 플랫폼별 환경 처리 핸들러를 생성하고 있습니다...")
        
        handler_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 플랫폼별 환경 처리 핸들러
Windows와 Mac 환경에서의 차이점을 자동으로 처리
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

class PlatformEnvironmentHandler:
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_mac = self.system == 'darwin'
        self.is_linux = self.system == 'linux'
        
        # 플랫폼별 설정
        self.config = self._get_platform_config()
    
    def _get_platform_config(self) -> dict:
        """플랫폼별 설정 반환"""
        if self.is_windows:
            return {
                'python_cmd': 'python',
                'path_separator': '\\\\',
                'line_ending': '\\r\\n',
                'encoding': 'cp949',
                'shell': True,
                'executable': None
            }
        else:  # Mac/Linux
            return {
                'python_cmd': 'python3',
                'path_separator': '/',
                'line_ending': '\\n',
                'encoding': 'utf-8',
                'shell': False,
                'executable': '/bin/bash'
            }
    
    def get_python_command(self) -> str:
        """플랫폼에 맞는 Python 명령어 반환"""
        return self.config['python_cmd']
    
    def get_path_separator(self) -> str:
        """플랫폼에 맞는 경로 구분자 반환"""
        return self.config['path_separator']
    
    def normalize_path(self, path: str) -> str:
        """플랫폼에 맞게 경로 정규화"""
        return str(Path(path))
    
    def run_command(self, command: list, cwd: str = None) -> subprocess.CompletedProcess:
        """플랫폼에 맞게 명령어 실행"""
        try:
            if self.is_windows:
                # Windows에서는 shell=True 사용
                result = subprocess.run(
                    ' '.join(command),
                    shell=True,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                # Mac/Linux에서는 shell=False 사용
                result = subprocess.run(
                    command,
                    shell=False,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
            return result
        except Exception as e:
            print(f"명령어 실행 오류: {e}")
            return None
    
    def run_python_script(self, script_path: str, args: list = None) -> subprocess.CompletedProcess:
        """플랫폼에 맞게 Python 스크립트 실행"""
        command = [self.get_python_command(), script_path]
        if args:
            command.extend(args)
        
        return self.run_command(command)
    
    def check_python_availability(self) -> bool:
        """Python 사용 가능 여부 확인"""
        try:
            result = self.run_command([self.get_python_command(), '--version'])
            return result and result.returncode == 0
        except:
            return False
    
    def get_environment_info(self) -> dict:
        """환경 정보 반환"""
        return {
            'platform': self.system,
            'python_cmd': self.get_python_command(),
            'python_available': self.check_python_availability(),
            'path_separator': self.get_path_separator(),
            'encoding': self.config['encoding'],
            'cwd': os.getcwd()
        }

# 전역 핸들러 인스턴스
platform_handler = PlatformEnvironmentHandler()

def get_platform_handler():
    """플랫폼 핸들러 인스턴스 반환"""
    return platform_handler

if __name__ == "__main__":
    handler = get_platform_handler()
    info = handler.get_environment_info()
    
    print("플랫폼 환경 정보:")
    for key, value in info.items():
        print(f"  {key}: {value}")
'''
        
        handler_path = self.workspace_root / "recovery_config" / "platform_environment_handler.py"
        with open(handler_path, 'w', encoding='utf-8') as f:
            f.write(handler_content)
        
        print(f"   ✅ 생성: {handler_path}")
        return str(handler_path)
    
    def verify_cross_platform_compatibility(self) -> Dict:
        """크로스 플랫폼 호환성 검증"""
        print("🔄 크로스 플랫폼 호환성을 검증하고 있습니다...")
        
        verification = {
            "python_availability": False,
            "path_handling": False,
            "encoding_support": False,
            "execution_permissions": False,
            "environment_variables": False,
            "issues": []
        }
        
        try:
            # Python 사용 가능성 확인
            python_cmd = "python3" if self.current_platform != "windows" else "python"
            result = subprocess.run([python_cmd, "--version"], capture_output=True, text=True)
            verification["python_availability"] = result.returncode == 0
            
            if not verification["python_availability"]:
                verification["issues"].append(f"{python_cmd} 명령어를 사용할 수 없습니다")
            
            # 경로 처리 확인
            test_path = self.workspace_root / "recovery_config"
            verification["path_handling"] = test_path.exists()
            
            if not verification["path_handling"]:
                verification["issues"].append("경로 처리에 문제가 있습니다")
            
            # 인코딩 지원 확인
            try:
                test_content = "테스트 한글 내용"
                test_file = self.workspace_root / "test_encoding.tmp"
                test_file.write_text(test_content, encoding='utf-8')
                read_content = test_file.read_text(encoding='utf-8')
                verification["encoding_support"] = test_content == read_content
                test_file.unlink()  # 테스트 파일 삭제
            except Exception as e:
                verification["issues"].append(f"인코딩 지원 문제: {e}")
            
            # 실행 권한 확인 (Mac/Linux)
            if self.current_platform != "windows":
                try:
                    test_script = self.workspace_root / "test_exec.sh"
                    test_script.write_text("#!/bin/bash\necho 'test'")
                    os.chmod(test_script, 0o755)
                    verification["execution_permissions"] = True
                    test_script.unlink()  # 테스트 파일 삭제
                except Exception as e:
                    verification["issues"].append(f"실행 권한 설정 문제: {e}")
            else:
                verification["execution_permissions"] = True  # Windows는 기본적으로 실행 가능
            
            # 환경 변수 확인
            verification["environment_variables"] = "PATH" in os.environ
            
            if not verification["environment_variables"]:
                verification["issues"].append("환경 변수 설정에 문제가 있습니다")
            
        except Exception as e:
            verification["issues"].append(f"호환성 검증 중 오류: {e}")
        
        # 결과 출력
        total_checks = 5
        passed_checks = sum(1 for v in verification.values() if isinstance(v, bool) and v)
        
        print(f"   ✅ 호환성 검증 완료: {passed_checks}/{total_checks} 통과")
        
        if verification["issues"]:
            print("   ⚠️ 발견된 문제들:")
            for issue in verification["issues"]:
                print(f"      - {issue}")
        
        return verification
    
    def generate_restoration_report(self, windows_files: List[str], mac_files: List[str], 
                                  compatibility: Dict) -> str:
        """복원 보고서 생성"""
        print("📊 복원 보고서를 생성하고 있습니다...")
        
        report = f"""# 플랫폼별 실행 파일 복원 완료 보고서

## 복원 결과 요약
- **Windows 실행 파일**: {len(windows_files)}개 복원
- **Mac 실행 파일**: {len(mac_files)}개 복원
- **플랫폼 환경 핸들러**: 생성 완료
- **호환성 검증**: {'✅ 통과' if not compatibility['issues'] else '⚠️ 일부 문제'}

## 복원된 Windows 실행 파일
{chr(10).join(f"- {file}" for file in windows_files)}

## 복원된 Mac 실행 파일
{chr(10).join(f"- {file}" for file in mac_files)}

## 플랫폼별 환경 설정
### Windows 환경
- Python 명령어: `python`
- 경로 구분자: `\\`
- 인코딩: `cp949`
- 셸: `cmd.exe`

### Mac 환경
- Python 명령어: `python3`
- 경로 구분자: `/`
- 인코딩: `utf-8`
- 셸: `/bin/bash`

## 호환성 검증 결과
- Python 사용 가능: {'✅' if compatibility['python_availability'] else '❌'}
- 경로 처리: {'✅' if compatibility['path_handling'] else '❌'}
- 인코딩 지원: {'✅' if compatibility['encoding_support'] else '❌'}
- 실행 권한: {'✅' if compatibility['execution_permissions'] else '❌'}
- 환경 변수: {'✅' if compatibility['environment_variables'] else '❌'}

## 발견된 문제점
{chr(10).join(f"- {issue}" for issue in compatibility['issues']) if compatibility['issues'] else "문제점 없음"}

## 사용 방법
### Windows에서
1. `POSCO_메인_system.bat` - 메인 시스템 제어센터
2. `POSCO_watchhamster_v3_control_center.bat` - 워치햄스터 제어센터
3. `POSCO_News_250808_Start.bat` - 뉴스 모니터링 시작
4. `POSCO_test_실행.bat` - 테스트 실행

### Mac에서
1. `POSCO_watchhamster_v3_control_center.command` - 워치햄스터 제어센터
2. `POSCO_News_250808_Start.sh` - 뉴스 모니터링 시작
3. `WatchHamster_v3.0_Control_Panel.command` - 통합 제어판

## 주의사항
- Mac에서 .command 파일 실행 시 터미널에서 실행하거나 더블클릭으로 실행 가능
- Windows에서 한글 출력이 깨질 경우 `chcp 65001` 명령어가 자동 실행됨
- 모든 실행 파일은 recovery_config/ 폴더의 모듈들을 참조함

플랫폼별 실행 파일 복원이 성공적으로 완료되었습니다! 🎉
"""
        
        report_path = self.workspace_root / "recovery_config" / "task13_completion_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 복원 보고서 생성: {report_path}")
        return report

def main():
    """메인 실행 함수"""
    print("🚀 POSCO 시스템 플랫폼별 실행 파일 복원을 시작합니다...")
    print("=" * 60)
    
    restorer = PlatformExecutionRestorer()
    
    try:
        # 1. 현재 실행 파일 분석
        analysis = restorer.analyze_current_execution_files()
        
        # 2. Windows 실행 파일 복원
        windows_files = restorer.restore_windows_execution_files()
        
        # 3. Mac 실행 파일 복원
        mac_files = restorer.restore_mac_execution_files()
        
        # 4. 플랫폼 환경 핸들러 생성
        handler_path = restorer.create_platform_environment_handler()
        
        # 5. 크로스 플랫폼 호환성 검증
        compatibility = restorer.verify_cross_platform_compatibility()
        
        # 6. 복원 보고서 생성
        report = restorer.generate_restoration_report(windows_files, mac_files, compatibility)
        
        print("=" * 60)
        print("🎉 플랫폼별 실행 파일 복원이 완료되었습니다!")
        print(report)
        
    except Exception as e:
        print(f"❌ 복원 중 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()