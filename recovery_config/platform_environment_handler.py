#!/usr/bin/env python3
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
                'path_separator': '\\',
                'line_ending': '\r\n',
                'encoding': 'cp949',
                'shell': True,
                'executable': None
            }
        else:  # Mac/Linux
            return {
                'python_cmd': 'python3',
                'path_separator': '/',
                'line_ending': '\n',
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
