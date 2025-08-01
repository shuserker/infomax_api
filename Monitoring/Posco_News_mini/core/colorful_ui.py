# -*- coding: utf-8 -*-
"""
컬러풀한 콘솔 UI (ColorfulConsoleUI)

사용자가 원하는 예전 스타일의 컬러풀하고 이쁜 UI를 제공하는 클래스

주요 기능:
- 컬러풀한 헤더, 상태, 메뉴 출력
- 이모지와 색상을 활용한 시각적 구분
- Windows 콘솔 호환성 및 UTF-8 인코딩 보장
- 예전 스타일의 구분선과 포맷팅

작성자: AI Assistant
최종 수정: 2025-07-31 (워치햄스터 UI 복원)
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import colorama
from colorama import Fore, Back, Style

# Windows 환경에서 colorama 초기화
if sys.platform == "win32":
    colorama.init(autoreset=True)

class ColorfulConsoleUI:
    """
    컬러풀한 콘솔 UI 클래스
    
    예전 스타일의 컬러풀하고 시각적으로 구분되는 인터페이스를 제공합니다.
    """
    
    def __init__(self):
        """ColorfulConsoleUI 초기화"""
        self.setup_console()
        
        # 색상 테마 정의
        self.colors = {
            'header': Fore.GREEN + Style.BRIGHT,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED + Style.BRIGHT,
            'info': Fore.CYAN,
            'highlight': Fore.MAGENTA + Style.BRIGHT,
            'normal': Fore.WHITE,
            'dim': Fore.WHITE + Style.DIM,
            'reset': Style.RESET_ALL
        }
        
        # 이모지 정의
        self.emojis = {
            'start': '🐹',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️',
            'monitor': '🔍',
            'time': '⏰',
            'status': '📊',
            'process': '🚀',
            'git': '🔄',
            'notification': '📢',
            'quiet': '💤',
            'active': '🟢',
            'inactive': '🔴',
            'partial': '🟡'
        }
    
    def setup_console(self):
        """콘솔 환경 설정"""
        if sys.platform == "win32":
            try:
                # Windows 콘솔 코드페이지를 UTF-8로 설정
                import subprocess
                subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
                
                # 표준 출력/오류를 UTF-8로 설정
                import codecs
                sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
                sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
                
                # 환경 변수 설정
                os.environ['PYTHONIOENCODING'] = 'utf-8'
            except:
                pass  # 설정 실패 시 무시
    
    def print_header(self, title: str, style: str = "default"):
        """
        간소화된 헤더 출력 - 기존 스타일 복원
        
        Args:
            title (str): 헤더 제목
            style (str): 헤더 스타일 ("default", "start", "status")
        """
        if style == "start":
            # 워치햄스터 시작 헤더
            separator = "=" * 50
            print(separator, flush=True)
            print(title, flush=True)
            print(separator, flush=True)
        elif style == "status":
            # 상태 체크 헤더
            separator = "=" * 50
            print(separator, flush=True)
            print(title, flush=True)
            print(separator, flush=True)
        else:
            # 기본 헤더
            separator = "=" * 50
            print(separator, flush=True)
            print(title, flush=True)
            print(separator, flush=True)
    
    def print_status(self, status: Dict[str, Any], highlight: bool = False):
        """
        상태 정보를 컬러풀하게 출력
        
        Args:
            status (Dict[str, Any]): 상태 정보
            highlight (bool): 강조 표시 여부
        """
        color = self.colors['highlight'] if highlight else self.colors['info']
        
        for key, value in status.items():
            if isinstance(value, bool):
                emoji = self.emojis['active'] if value else self.emojis['inactive']
                status_text = "정상 작동" if value else "중단됨"
                print(f"{color}{emoji} {key}: {status_text}{self.colors['reset']}", flush=True)
            elif isinstance(value, str):
                print(f"{color}{self.emojis['info']} {key}: {value}{self.colors['reset']}", flush=True)
            else:
                print(f"{color}{self.emojis['info']} {key}: {str(value)}{self.colors['reset']}", flush=True)
    
    def print_progress(self, current: int, total: int, description: str):
        """
        진행 상황을 시각적으로 표시
        
        Args:
            current (int): 현재 진행 수
            total (int): 전체 수
            description (str): 설명
        """
        percentage = (current / total) * 100 if total > 0 else 0
        
        # 진행률에 따른 색상 선택
        if percentage >= 80:
            color = self.colors['success']
            emoji = self.emojis['success']
        elif percentage >= 50:
            color = self.colors['warning']
            emoji = self.emojis['partial']
        else:
            color = self.colors['error']
            emoji = self.emojis['error']
        
        # 진행 바 생성
        bar_length = 20
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"{color}{emoji} {description}: [{bar}] {current}/{total} ({percentage:.1f}%){self.colors['reset']}", flush=True)
    
    def print_separator(self, char: str = "=", length: int = 50, color: str = "normal"):
        """
        구분선 출력
        
        Args:
            char (str): 구분선 문자
            length (int): 구분선 길이
            color (str): 색상
        """
        separator = char * length
        print(f"{self.colors.get(color, self.colors['normal'])}{separator}{self.colors['reset']}", flush=True)
    
    def print_menu(self, options: List[str], current_selection: Optional[int] = None):
        """
        간소화된 메뉴 출력 - 기존 스타일 복원
        
        Args:
            options (List[str]): 메뉴 옵션 리스트
            current_selection (Optional[int]): 현재 선택된 옵션 번호
        """
        print(f"실행 모드: {current_selection if current_selection else '3'}", flush=True)
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}", flush=True)
    
    def print_monitoring_info(self, mode: str, details: Dict[str, str]):
        """
        모니터링 정보를 기존 스타일로 출력
        
        Args:
            mode (str): 모니터링 모드
            details (Dict[str, str]): 상세 정보
        """
        print(f"[{mode}] {details.get('title', '모니터링 시작')}", flush=True)
        
        # 운영시간 정보
        if 'operating_hours' in details:
            print(f"📅 운영시간: {details['operating_hours']}", flush=True)
        
        # 집중시간 정보
        if 'focus_hours' in details:
            print(f"⚡ 집중시간: {details['focus_hours']}", flush=True)
        
        # 일반시간 정보
        if 'normal_hours' in details:
            print(f"📊 일반시간: {details['normal_hours']}", flush=True)
        
        # 조용한 모드 정보
        if 'quiet_hours' in details:
            print(f"💤 야간 조용한 모드: {details['quiet_hours']}", flush=True)
        
        # 특별 이벤트 정보
        if 'special_events' in details:
            print(f"🎯 특별이벤트: {details['special_events']}", flush=True)
        
        # 중단 안내
        print("중단하려면 Ctrl+C를 누르세요", flush=True)
        print(flush=True)  # 빈 줄 추가
    
    def print_monitor_status(self, monitors: Dict[str, Dict]):
        """
        개별 모니터 상태를 간소화하여 출력
        
        Args:
            monitors (Dict[str, Dict]): 모니터별 상태 정보
        """
        for monitor_name, status in monitors.items():
            is_running = status.get('is_running', False)
            description = status.get('description', monitor_name)
            
            if is_running:
                print(f"   {description}: 준비 완료", flush=True)
            else:
                print(f"   {description}: 중단됨", flush=True)
    
    def print_time_info(self, current_time: datetime, next_time: Optional[datetime] = None):
        """
        시간 정보를 컬러풀하게 출력
        
        Args:
            current_time (datetime): 현재 시간
            next_time (Optional[datetime]): 다음 작업 시간
        """
        time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{self.colors['info']}{self.emojis['time']} 현재 시간: {time_str}{self.colors['reset']}", flush=True)
        
        if next_time:
            next_str = next_time.strftime('%H:%M:%S')
            print(f"{self.colors['dim']}{self.emojis['time']} 다음 확인: {next_str}{self.colors['reset']}", flush=True)
    
    def print_error_message(self, error: Exception, context: str = ""):
        """
        오류 메시지를 명확하게 출력
        
        Args:
            error (Exception): 오류 객체
            context (str): 오류 발생 컨텍스트
        """
        print(f"{self.colors['error']}{self.emojis['error']} 오류 발생{self.colors['reset']}", flush=True)
        if context:
            print(f"{self.colors['dim']}컨텍스트: {context}{self.colors['reset']}", flush=True)
        print(f"{self.colors['error']}오류 내용: {str(error)}{self.colors['reset']}", flush=True)
    
    def print_success_message(self, action: str, details: Optional[str] = None):
        """
        간소화된 성공 메시지 출력
        
        Args:
            action (str): 수행된 작업
            details (Optional[str]): 상세 정보
        """
        print(f"✅ {action}", flush=True)
        if details:
            print(f"{details}", flush=True)
    
    def print_warning_message(self, message: str, details: Optional[str] = None):
        """
        경고 메시지를 출력
        
        Args:
            message (str): 경고 메시지
            details (Optional[str]): 상세 정보
        """
        print(f"{self.colors['warning']}{self.emojis['warning']} {message}{self.colors['reset']}", flush=True)
        if details:
            print(f"{self.colors['dim']}{details}{self.colors['reset']}", flush=True)
    
    def print_info_message(self, message: str, emoji_key: str = "info"):
        """
        간소화된 정보 메시지 출력
        
        Args:
            message (str): 정보 메시지
            emoji_key (str): 사용할 이모지 키
        """
        if emoji_key == "process":
            print(f"🚀 {message}", flush=True)
        else:
            print(f"ℹ️ {message}", flush=True)
    
    def clear_screen(self):
        """화면 지우기"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_startup_banner(self):
        """워치햄스터 시작 배너 출력 - 기존 스타일 복원"""
        print("[START] POSCO 뉴스 모니터 시작", flush=True)
        print("=" * 50, flush=True)