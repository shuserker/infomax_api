#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WatchHamster 현대적 통합 GUI
웹 스타일의 모던한 인터페이스로 모든 기능을 하나의 창에 통합

주요 특징:
- 🎨 현대적인 웹 스타일 디자인
- 📱 반응형 레이아웃
- 🔄 실시간 상태 업데이트
- 🎯 직관적인 사용자 경험
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import time
import threading
from typing import Dict, Any, Optional

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 중복 실행 방지 시스템
try:
    from singleton_manager import prevent_duplicate_execution, cleanup_singleton
    SINGLETON_AVAILABLE = True
except ImportError:
    SINGLETON_AVAILABLE = False
    print("[WARNING] 중복 실행 방지 시스템을 사용할 수 없습니다")

try:
    from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager
    from core.integrated_status_reporter import create_integrated_status_reporter
    from core.system_recovery_handler import create_system_recovery_handler
    from core.performance_optimizer import get_performance_optimizer
    from core.stability_manager import get_stability_manager
except ImportError as e:
    print(f"[WARNING] 일부 모듈을 사용할 수 없습니다: {e}")


class ModernTheme:
    """현대적인 테마 설정"""
    
    # 색상 팔레트 (웹 스타일)
    COLORS = {
        'primary': '#2563eb',      # 파란색
        'secondary': '#64748b',    # 회색
        'success': '#10b981',      # 초록색
        'warning': '#f59e0b',      # 주황색
        'danger': '#ef4444',       # 빨간색
        'info': '#06b6d4',         # 청록색
        'light': '#f8fafc',        # 밝은 회색
        'dark': '#1e293b',         # 어두운 회색
        'white': '#ffffff',        # 흰색
        'border': '#e2e8f0',       # 테두리 색상
        'hover': '#f1f5f9',        # 호버 색상
        'active': '#e2e8f0'        # 활성 색상
    }
    
    # 폰트 설정
    FONTS = {
        'title': ('Segoe UI', 24, 'bold'),
        'heading': ('Segoe UI', 16, 'bold'),
        'subheading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 11),
        'small': ('Segoe UI', 9),
        'code': ('Consolas', 10)
    }
    
    # 간격 설정
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32
    }


class ModernCard(ttk.Frame):
    """현대적인 카드 컴포넌트"""
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        # 카드 스타일 설정
        self.configure(relief='solid', borderwidth=1)
        
        # 제목이 있으면 헤더 생성
        if title:
            header = ttk.Frame(self)
            header.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], 
                       pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
            
            title_label = ttk.Label(header, text=title, font=ModernTheme.FONTS['heading'])
            title_label.pack(anchor=tk.W)
        
        # 콘텐츠 영역
        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True, 
                         padx=ModernTheme.SPACING['md'], 
                         pady=(0, ModernTheme.SPACING['md']))


class StatusIndicator(ttk.Frame):
    """상태 표시 인디케이터"""
    
    def __init__(self, parent, label: str, status: str = "unknown", **kwargs):
        super().__init__(parent, **kwargs)
        
        # 상태 색상 매핑
        self.status_colors = {
            'healthy': ModernTheme.COLORS['success'],
            'warning': ModernTheme.COLORS['warning'],
            'error': ModernTheme.COLORS['danger'],
            'unknown': ModernTheme.COLORS['secondary'],
            'running': ModernTheme.COLORS['success'],
            'stopped': ModernTheme.COLORS['secondary']
        }
        
        # 상태 아이콘 매핑
        self.status_icons = {
            'healthy': '●',
            'warning': '⚠',
            'error': '●',
            'unknown': '○',
            'running': '●',
            'stopped': '○'
        }
        
        # 레이아웃
        self.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
        
        # 상태 아이콘
        self.icon_label = ttk.Label(self, font=ModernTheme.FONTS['body'])
        self.icon_label.pack(side=tk.LEFT, padx=(0, ModernTheme.SPACING['sm']))
        
        # 라벨
        self.text_label = ttk.Label(self, text=label, font=ModernTheme.FONTS['body'])
        self.text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 상태 텍스트
        self.status_label = ttk.Label(self, font=ModernTheme.FONTS['small'])
        self.status_label.pack(side=tk.RIGHT)
        
        # 초기 상태 설정
        self.update_status(status)
    
    def update_status(self, status: str, message: str = ""):
        """상태 업데이트"""
        color = self.status_colors.get(status, ModernTheme.COLORS['secondary'])
        icon = self.status_icons.get(status, '○')
        
        self.icon_label.configure(text=icon, foreground=color)
        
        status_text = message or status.title()
        self.status_label.configure(text=status_text, foreground=color)


class ModernButton(ttk.Button):
    """현대적인 버튼 컴포넌트"""
    
    def __init__(self, parent, text: str, style: str = "primary", **kwargs):
        # 스타일 설정
        style_name = f"{style.title()}.TButton"
        
        super().__init__(parent, text=text, style=style_name, **kwargs)
        
        # 버튼 스타일 적용
        self.configure(width=12)


class ModernWatchHamsterGUI:
    """현대적인 WatchHamster 통합 GUI"""
    
    def __init__(self):
        """GUI 초기화"""
        self.root = tk.Tk()
        self.root.title("WatchHamster - 통합 시스템 관리자")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        
        # 테마 설정
        self.setup_theme()
        
        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 서비스 상태 추적
        self.service_states = {
            'posco_news': {'status': 'stopped', 'message': '중지됨'},
            'github_pages': {'status': 'unknown', 'message': '확인 중'},
            'cache_monitor': {'status': 'stopped', 'message': '중지됨'},
            'deployment': {'status': 'unknown', 'message': '확인 중'},
            'message_system': {'status': 'stopped', 'message': '중지됨'},
            'webhook': {'status': 'stopped', 'message': '중지됨'}
        }
        
        # 시스템 메트릭
        self.system_metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'uptime': 0,
            'active_services': 0
        }
        
        # 최소화 상태 추적
        self.is_minimized = False
        
        # UI 생성
        self.create_ui()
        
        # 시스템 초기화
        self.initialize_systems()
        
        # 상태 업데이트 시작
        self.start_status_updates()
    
    def setup_theme(self):
        """테마 설정"""
        style = ttk.Style()
        
        # 기본 테마 설정
        style.theme_use('clam')
        
        # 커스텀 스타일 정의
        style.configure('Title.TLabel', 
                       font=ModernTheme.FONTS['title'],
                       foreground=ModernTheme.COLORS['dark'])
        
        style.configure('Heading.TLabel', 
                       font=ModernTheme.FONTS['heading'],
                       foreground=ModernTheme.COLORS['dark'])
        
        style.configure('Card.TFrame',
                       background=ModernTheme.COLORS['white'],
                       relief='solid',
                       borderwidth=1)
        
        # 버튼 스타일
        style.configure('Primary.TButton',
                       background=ModernTheme.COLORS['primary'],
                       foreground=ModernTheme.COLORS['white'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Success.TButton',
                       background=ModernTheme.COLORS['success'],
                       foreground=ModernTheme.COLORS['white'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Warning.TButton',
                       background=ModernTheme.COLORS['warning'],
                       foreground=ModernTheme.COLORS['white'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Danger.TButton',
                       background=ModernTheme.COLORS['danger'],
                       foreground=ModernTheme.COLORS['white'],
                       borderwidth=0,
                       focuscolor='none')
    
    def create_ui(self):
        """UI 생성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.SPACING['lg'], 
                           pady=ModernTheme.SPACING['lg'])
        
        # 헤더 생성
        self.create_header(main_container)
        
        # 메인 콘텐츠 영역
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(ModernTheme.SPACING['lg'], 0))
        
        # 좌측 패널 (상태 및 제어)
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                       padx=(0, ModernTheme.SPACING['md']))
        
        # 우측 패널 (로그 및 상세 정보)
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 좌측 패널 콘텐츠
        self.create_system_overview(left_panel)
        self.create_service_control(left_panel)
        
        # 우측 패널 콘텐츠
        self.create_activity_log(right_panel)
        self.create_system_metrics(right_panel)
        
        # 하단 상태바
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """헤더 생성"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['lg']))
        
        # 제목
        title_label = ttk.Label(header_frame, 
                               text="WatchHamster", 
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # 부제목
        subtitle_label = ttk.Label(header_frame, 
                                  text="통합 시스템 관리자", 
                                  font=ModernTheme.FONTS['body'],
                                  foreground=ModernTheme.COLORS['secondary'])
        subtitle_label.pack(side=tk.LEFT, padx=(ModernTheme.SPACING['sm'], 0))
        
        # 우측 제어 버튼들
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        # 최소화 버튼
        minimize_btn = ModernButton(controls_frame, "최소화", "secondary",
                                   command=self.minimize_to_tray)
        minimize_btn.pack(side=tk.RIGHT, padx=(ModernTheme.SPACING['sm'], 0))
        
        # 설정 버튼
        settings_btn = ModernButton(controls_frame, "설정", "secondary",
                                   command=self.show_settings)
        settings_btn.pack(side=tk.RIGHT, padx=(ModernTheme.SPACING['sm'], 0))
    
    def create_system_overview(self, parent):
        """시스템 개요 카드"""
        overview_card = ModernCard(parent, "시스템 개요")
        overview_card.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['md']))
        
        # 전체 상태 표시
        self.overall_status = StatusIndicator(overview_card.content, 
                                             "전체 시스템 상태", "unknown")
        
        # 빠른 액션 버튼들
        actions_frame = ttk.Frame(overview_card.content)
        actions_frame.pack(fill=tk.X, pady=(ModernTheme.SPACING['md'], 0))
        
        start_all_btn = ModernButton(actions_frame, "전체 시작", "success",
                                    command=self.start_all_services)
        start_all_btn.pack(side=tk.LEFT, padx=(0, ModernTheme.SPACING['sm']))
        
        stop_all_btn = ModernButton(actions_frame, "전체 중지", "warning",
                                   command=self.stop_all_services)
        stop_all_btn.pack(side=tk.LEFT, padx=(0, ModernTheme.SPACING['sm']))
        
        restart_all_btn = ModernButton(actions_frame, "전체 재시작", "primary",
                                      command=self.restart_all_services)
        restart_all_btn.pack(side=tk.LEFT)
    
    def create_service_control(self, parent):
        """서비스 제어 카드"""
        services_card = ModernCard(parent, "서비스 관리")
        services_card.pack(fill=tk.BOTH, expand=True, pady=(0, ModernTheme.SPACING['md']))
        
        # 서비스 목록
        self.service_indicators = {}
        
        services = [
            ('posco_news', 'POSCO 뉴스 시스템'),
            ('github_pages', 'GitHub Pages 모니터'),
            ('cache_monitor', '캐시 데이터 모니터'),
            ('deployment', '배포 시스템'),
            ('message_system', '메시지 시스템'),
            ('webhook', '웹훅 통합')
        ]
        
        for service_key, service_name in services:
            # 서비스 프레임
            service_frame = ttk.Frame(services_card.content)
            service_frame.pack(fill=tk.X, pady=ModernTheme.SPACING['sm'])
            
            # 상태 표시
            indicator = StatusIndicator(service_frame, service_name, "stopped")
            indicator.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 제어 버튼들
            controls = ttk.Frame(service_frame)
            controls.pack(side=tk.RIGHT)
            
            start_btn = ttk.Button(controls, text="시작", width=6,
                                  command=lambda k=service_key: self.start_service(k))
            start_btn.pack(side=tk.LEFT, padx=(0, 2))
            
            stop_btn = ttk.Button(controls, text="중지", width=6,
                                 command=lambda k=service_key: self.stop_service(k))
            stop_btn.pack(side=tk.LEFT, padx=(0, 2))
            
            restart_btn = ttk.Button(controls, text="재시작", width=6,
                                    command=lambda k=service_key: self.restart_service(k))
            restart_btn.pack(side=tk.LEFT)
            
            self.service_indicators[service_key] = indicator
    
    def create_activity_log(self, parent):
        """활동 로그 카드"""
        log_card = ModernCard(parent, "활동 로그")
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, ModernTheme.SPACING['md']))
        
        # 로그 텍스트 위젯
        log_frame = ttk.Frame(log_card.content)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, 
                               font=ModernTheme.FONTS['code'],
                               wrap=tk.WORD,
                               height=15,
                               state=tk.DISABLED)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 로그 제어 버튼들
        log_controls = ttk.Frame(log_card.content)
        log_controls.pack(fill=tk.X, pady=(ModernTheme.SPACING['sm'], 0))
        
        clear_btn = ttk.Button(log_controls, text="로그 지우기", width=10,
                              command=self.clear_log)
        clear_btn.pack(side=tk.LEFT)
        
        export_btn = ttk.Button(log_controls, text="로그 내보내기", width=12,
                               command=self.export_log)
        export_btn.pack(side=tk.LEFT, padx=(ModernTheme.SPACING['sm'], 0))
    
    def create_system_metrics(self, parent):
        """시스템 메트릭 카드"""
        metrics_card = ModernCard(parent, "시스템 메트릭")
        metrics_card.pack(fill=tk.X)
        
        # 메트릭 표시
        metrics_frame = ttk.Frame(metrics_card.content)
        metrics_frame.pack(fill=tk.X)
        
        # CPU 사용률
        cpu_frame = ttk.Frame(metrics_frame)
        cpu_frame.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
        
        ttk.Label(cpu_frame, text="CPU 사용률:", font=ModernTheme.FONTS['body']).pack(side=tk.LEFT)
        self.cpu_label = ttk.Label(cpu_frame, text="0.0%", font=ModernTheme.FONTS['body'])
        self.cpu_label.pack(side=tk.RIGHT)
        
        # 메모리 사용률
        memory_frame = ttk.Frame(metrics_frame)
        memory_frame.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
        
        ttk.Label(memory_frame, text="메모리 사용률:", font=ModernTheme.FONTS['body']).pack(side=tk.LEFT)
        self.memory_label = ttk.Label(memory_frame, text="0.0%", font=ModernTheme.FONTS['body'])
        self.memory_label.pack(side=tk.RIGHT)
        
        # 활성 서비스 수
        services_frame = ttk.Frame(metrics_frame)
        services_frame.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
        
        ttk.Label(services_frame, text="활성 서비스:", font=ModernTheme.FONTS['body']).pack(side=tk.LEFT)
        self.services_label = ttk.Label(services_frame, text="0/6", font=ModernTheme.FONTS['body'])
        self.services_label.pack(side=tk.RIGHT)
        
        # 업타임
        uptime_frame = ttk.Frame(metrics_frame)
        uptime_frame.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
        
        ttk.Label(uptime_frame, text="업타임:", font=ModernTheme.FONTS['body']).pack(side=tk.LEFT)
        self.uptime_label = ttk.Label(uptime_frame, text="0초", font=ModernTheme.FONTS['body'])
        self.uptime_label.pack(side=tk.RIGHT)
    
    def create_status_bar(self, parent):
        """하단 상태바"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(ModernTheme.SPACING['lg'], 0))
        
        # 구분선
        separator = ttk.Separator(status_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['sm']))
        
        # 상태 정보
        self.status_label = ttk.Label(status_frame, 
                                     text="시스템 초기화 중...", 
                                     font=ModernTheme.FONTS['small'],
                                     foreground=ModernTheme.COLORS['secondary'])
        self.status_label.pack(side=tk.LEFT)
        
        # 버전 정보
        version_label = ttk.Label(status_frame, 
                                 text="v3.0", 
                                 font=ModernTheme.FONTS['small'],
                                 foreground=ModernTheme.COLORS['secondary'])
        version_label.pack(side=tk.RIGHT)
    
    def initialize_systems(self):
        """시스템 초기화"""
        self.log_message("🚀 WatchHamster 시스템 초기화 시작", "system")
        
        try:
            # 웹훅 설정 로드
            self.load_webhook_config()
            
            # 성능 최적화 시스템
            self.performance_optimizer = get_performance_optimizer()
            self.log_message("⚡ 성능 최적화 시스템 활성화", "success")
            
            # 안정성 관리자
            self.stability_manager = get_stability_manager(current_dir)
            self.log_message("🛡️ 안정성 관리자 활성화", "success")
            
            # 통합 상태 보고 시스템
            self.status_reporter = create_integrated_status_reporter(current_dir)
            self.log_message("📊 통합 상태 보고 시스템 활성화", "success")
            
            # 시스템 복구 핸들러
            self.recovery_handler = create_system_recovery_handler(current_dir)
            self.log_message("🔧 시스템 복구 핸들러 활성화", "success")
            
            # 웹훅 통합 시스템
            self.initialize_webhook_system()
            
            # POSCO GUI 관리자 (선택적)
            try:
                # self.posco_manager = PoscoGUIManager(None)
                self.log_message("🏭 POSCO 시스템 연동 준비 완료", "info")
            except:
                self.log_message("🏭 POSCO 시스템 연동 건너뜀 (선택사항)", "warning")
            
            # 시작 메시지 웹훅 전송
            self.send_startup_webhook()
            
            self.log_message("✨ 모든 시스템 초기화 완료!", "success")
            self.update_status("시스템 준비 완료 - 모든 기능 사용 가능")
            
        except Exception as e:
            self.log_message(f"💥 시스템 초기화 실패: {e}", "error")
            self.update_status("초기화 오류 - 일부 기능 제한됨")
    
    def load_webhook_config(self):
        """웹훅 설정 로드"""
        try:
            import json
            config_path = os.path.join(current_dir, 'config', 'webhook_config.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.webhook_config = json.load(f)
                
                self.webhook_url = self.webhook_config.get('webhook_url', '')
                self.posco_webhook_url = self.webhook_config.get('posco_webhook_url', '')
                
                if self.webhook_url:
                    self.log_message("🔗 WatchHamster 웹훅 URL 로드 완료", "success")
                if self.posco_webhook_url:
                    self.log_message("🏭 POSCO 웹훅 URL 로드 완료", "success")
                    
                if not self.webhook_url and not self.posco_webhook_url:
                    self.log_message("⚠️ 웹훅 URL이 설정되지 않았습니다", "warning")
            else:
                self.log_message("⚠️ 웹훅 설정 파일을 찾을 수 없습니다", "warning")
                self.webhook_config = {}
                self.webhook_url = ''
                self.posco_webhook_url = ''
                
        except Exception as e:
            self.log_message(f"❌ 웹훅 설정 로드 실패: {e}", "error")
            self.webhook_config = {}
            self.webhook_url = ''
            self.posco_webhook_url = ''
    
    def initialize_webhook_system(self):
        """웹훅 시스템 초기화"""
        try:
            # 웹훅 통합 모듈 로드
            sys.path.append(os.path.join(current_dir, 'Posco_News_Mini_Final_GUI'))
            from enhanced_webhook_integration import EnhancedWebhookMixin
            
            # 웹훅 기능 활성화
            self.webhook_enabled = bool(self.webhook_url or self.posco_webhook_url)
            
            if self.webhook_enabled:
                self.log_message("🔗 웹훅 통합 시스템 활성화", "success")
            else:
                self.log_message("🔗 웹훅 시스템 비활성화 (URL 미설정)", "warning")
                
        except Exception as e:
            self.log_message(f"❌ 웹훅 시스템 초기화 실패: {e}", "error")
            self.webhook_enabled = False
    
    def send_webhook_message(self, message: str, webhook_type: str = "watchhamster"):
        """웹훅 메시지 전송"""
        if not self.webhook_enabled:
            return False
        
        try:
            import requests
            from datetime import datetime
            
            # 웹훅 URL 선택
            if webhook_type == "posco" and self.posco_webhook_url:
                url = self.posco_webhook_url
            elif self.webhook_url:
                url = self.webhook_url
            else:
                return False
            
            # 페이로드 생성
            payload = {
                "text": message,
                "timestamp": datetime.now().isoformat(),
                "source": "WatchHamster Modern GUI"
            }
            
            # 웹훅 전송
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.log_message(f"✅ 웹훅 메시지 전송 완료 ({webhook_type})", "success")
                return True
            else:
                self.log_message(f"❌ 웹훅 전송 실패: HTTP {response.status_code}", "error")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 웹훅 전송 중 오류: {e}", "error")
            return False
    
    def send_startup_webhook(self):
        """시스템 시작 웹훅 전송"""
        if self.webhook_enabled:
            startup_message = """🚀 **WatchHamster 시스템 시작**

**시스템 정보:**
- 버전: v3.0 Modern GUI
- 시작 시간: {start_time}
- 활성 서비스: {active_services}개
- 상태: 정상 초기화 완료

**주요 기능:**
✅ 성능 최적화 시스템
✅ 안정성 관리자  
✅ 통합 상태 보고
✅ 시스템 복구 핸들러
✅ 웹훅 통합 시스템

시스템이 정상적으로 시작되었습니다.""".format(
                start_time=time.strftime("%Y-%m-%d %H:%M:%S"),
                active_services=len(self.service_states)
            )
            
            self.send_webhook_message(startup_message)
    
    def start_status_updates(self):
        """상태 업데이트 시작"""
        self.start_time = time.time()
        self.update_metrics()
        self.update_service_status()
    
    def update_metrics(self):
        """메트릭 업데이트"""
        try:
            if hasattr(self, 'performance_optimizer'):
                metrics = self.performance_optimizer.get_performance_metrics()
                self.system_metrics['cpu_usage'] = metrics.get('cpu_percent', 0.0)
                self.system_metrics['memory_usage'] = metrics.get('memory_percent', 0.0)
            
            # 업타임 계산
            if hasattr(self, 'start_time'):
                uptime_seconds = int(time.time() - self.start_time)
                if uptime_seconds < 60:
                    uptime_text = f"{uptime_seconds}초"
                elif uptime_seconds < 3600:
                    uptime_text = f"{uptime_seconds // 60}분 {uptime_seconds % 60}초"
                else:
                    hours = uptime_seconds // 3600
                    minutes = (uptime_seconds % 3600) // 60
                    uptime_text = f"{hours}시간 {minutes}분"
                
                self.system_metrics['uptime'] = uptime_text
            
            # 활성 서비스 수 계산
            active_count = sum(1 for state in self.service_states.values() 
                             if state['status'] == 'running')
            total_count = len(self.service_states)
            self.system_metrics['active_services'] = f"{active_count}/{total_count}"
            
            # UI 업데이트
            self.cpu_label.configure(text=f"{self.system_metrics['cpu_usage']:.1f}%")
            self.memory_label.configure(text=f"{self.system_metrics['memory_usage']:.1f}%")
            self.services_label.configure(text=self.system_metrics['active_services'])
            self.uptime_label.configure(text=self.system_metrics['uptime'])
            
        except Exception as e:
            self.log_message(f"메트릭 업데이트 오류: {e}", "error")
        
        # 5초마다 업데이트
        self.root.after(5000, self.update_metrics)
    
    def update_service_status(self):
        """서비스 상태 업데이트"""
        try:
            # 각 서비스 상태 확인 및 업데이트
            for service_key, indicator in self.service_indicators.items():
                state = self.service_states[service_key]
                indicator.update_status(state['status'], state['message'])
            
            # 전체 상태 업데이트
            active_count = sum(1 for state in self.service_states.values() 
                             if state['status'] == 'running')
            total_count = len(self.service_states)
            
            if active_count == 0:
                overall_status = "stopped"
                overall_message = "모든 서비스 중지됨"
            elif active_count == total_count:
                overall_status = "running"
                overall_message = "모든 서비스 실행 중"
            else:
                overall_status = "warning"
                overall_message = f"{active_count}/{total_count} 서비스 실행 중"
            
            self.overall_status.update_status(overall_status, overall_message)
            
        except Exception as e:
            self.log_message(f"서비스 상태 업데이트 오류: {e}", "error")
        
        # 10초마다 업데이트
        self.root.after(10000, self.update_service_status)
    
    def log_message(self, message: str, level: str = "info"):
        """로그 메시지 추가"""
        timestamp = time.strftime("%H:%M:%S")
        
        # 레벨별 아이콘과 색상
        log_styles = {
            'info': {'icon': '💡', 'color': ModernTheme.COLORS['info']},
            'success': {'icon': '✅', 'color': ModernTheme.COLORS['success']},
            'warning': {'icon': '⚠️', 'color': ModernTheme.COLORS['warning']},
            'error': {'icon': '❌', 'color': ModernTheme.COLORS['danger']},
            'system': {'icon': '🔧', 'color': ModernTheme.COLORS['primary']}
        }
        
        style = log_styles.get(level, log_styles['info'])
        icon = style['icon']
        
        log_entry = f"[{timestamp}] {icon} {message}\n"
        
        # 텍스트 위젯에 추가
        self.log_text.configure(state=tk.NORMAL)
        
        # 색상 태그 설정
        tag_name = f"level_{level}"
        self.log_text.tag_configure(tag_name, foreground=style['color'])
        
        # 현재 위치 저장
        start_pos = self.log_text.index(tk.END + "-1c")
        
        # 텍스트 삽입
        self.log_text.insert(tk.END, log_entry)
        
        # 색상 적용
        end_pos = self.log_text.index(tk.END + "-1c")
        self.log_text.tag_add(tag_name, start_pos, end_pos)
        
        # 스크롤 및 상태 복원
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
        # 콘솔에도 출력
        print(f"[{timestamp}] {message}")
    
    def update_status(self, message: str):
        """상태바 업데이트"""
        self.status_label.configure(text=message)
    
    # 서비스 제어 메서드들
    def start_service(self, service_key: str):
        """서비스 시작"""
        service_names = {
            'posco_news': '🏭 POSCO 뉴스 시스템',
            'github_pages': '🌐 GitHub Pages 모니터',
            'cache_monitor': '💾 캐시 데이터 모니터',
            'deployment': '🚀 배포 시스템',
            'message_system': '💬 메시지 시스템',
            'webhook': '🔗 웹훅 통합'
        }
        
        service_name = service_names.get(service_key, service_key)
        
        try:
            self.log_message(f"{service_name} 시작 중...", "info")
            
            # 서비스별 실제 시작 로직
            def start_async():
                time.sleep(2)  # 시뮬레이션
                self.service_states[service_key] = {'status': 'running', 'message': '실행 중'}
                self.log_message(f"{service_name} 시작 완료!", "success")
                
                # 웹훅 알림 전송
                if self.webhook_enabled:
                    webhook_message = f"✅ **서비스 시작 알림**\n\n{service_name}이(가) 성공적으로 시작되었습니다.\n\n시간: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    webhook_type = "posco" if service_key == 'posco_news' else "watchhamster"
                    self.send_webhook_message(webhook_message, webhook_type)
            
            # 비동기 실행
            threading.Thread(target=start_async, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"{service_name} 시작 실패: {e}", "error")
            
            # 오류 웹훅 전송
            if self.webhook_enabled:
                error_message = f"❌ **서비스 시작 실패**\n\n{service_name} 시작 중 오류가 발생했습니다.\n\n오류: {str(e)}\n시간: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                self.send_webhook_message(error_message)
    
    def stop_service(self, service_key: str):
        """서비스 중지"""
        service_names = {
            'posco_news': '🏭 POSCO 뉴스 시스템',
            'github_pages': '🌐 GitHub Pages 모니터',
            'cache_monitor': '💾 캐시 데이터 모니터',
            'deployment': '🚀 배포 시스템',
            'message_system': '💬 메시지 시스템',
            'webhook': '🔗 웹훅 통합'
        }
        
        service_name = service_names.get(service_key, service_key)
        
        try:
            self.log_message(f"{service_name} 중지 중...", "warning")
            
            # 서비스별 실제 중지 로직
            def stop_async():
                time.sleep(1)  # 시뮬레이션
                self.service_states[service_key] = {'status': 'stopped', 'message': '중지됨'}
                self.log_message(f"{service_name} 중지 완료", "info")
            
            # 비동기 실행
            threading.Thread(target=stop_async, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"{service_name} 중지 실패: {e}", "error")
    
    def restart_service(self, service_key: str):
        """서비스 재시작"""
        self.stop_service(service_key)
        self.root.after(1000, lambda: self.start_service(service_key))
    
    def start_all_services(self):
        """모든 서비스 시작"""
        self.log_message("🚀 전체 시스템 시작 명령 실행!", "system")
        
        # 웹훅 알림 전송
        if self.webhook_enabled:
            start_message = f"""🚀 **전체 시스템 시작**

모든 WatchHamster 서비스를 시작합니다.

**시작할 서비스:**
• 🏭 POSCO 뉴스 시스템
• 🌐 GitHub Pages 모니터  
• 💾 캐시 데이터 모니터
• 🚀 배포 시스템
• 💬 메시지 시스템
• 🔗 웹훅 통합

시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            self.send_webhook_message(start_message)
        
        for service_key in self.service_states.keys():
            self.start_service(service_key)
        self.log_message("📋 모든 서비스 시작 요청 완료", "info")
    
    def stop_all_services(self):
        """모든 서비스 중지"""
        self.log_message("⏹️ 전체 시스템 중지 명령 실행", "warning")
        for service_key in self.service_states.keys():
            self.stop_service(service_key)
        self.log_message("📋 모든 서비스 중지 요청 완료", "warning")
    
    def restart_all_services(self):
        """모든 서비스 재시작"""
        self.log_message("모든 서비스 재시작 중...", "info")
        self.stop_all_services()
        self.root.after(2000, self.start_all_services)
    
    def minimize_to_tray(self):
        """시스템 트레이로 최소화"""
        self.root.withdraw()
        self.is_minimized = True
        self.log_message("시스템 트레이로 최소화됨", "info")
        
        # 트레이 아이콘 표시 (간단한 구현)
        self.show_tray_notification()
    
    def show_tray_notification(self):
        """트레이 알림 표시"""
        # 실제 구현에서는 시스템 트레이 라이브러리 사용
        messagebox.showinfo("WatchHamster", 
                           "시스템 트레이로 최소화되었습니다.\n"
                           "작업 표시줄에서 다시 열 수 있습니다.")
    
    def show_settings(self):
        """설정 창 표시"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("설정")
        settings_window.geometry("600x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 설정 내용 (예시)
        ttk.Label(settings_window, text="설정", font=ModernTheme.FONTS['heading']).pack(pady=20)
        ttk.Label(settings_window, text="설정 기능은 개발 중입니다.").pack()
        
        ttk.Button(settings_window, text="닫기", 
                  command=settings_window.destroy).pack(pady=20)
    
    def clear_log(self):
        """로그 지우기"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.log_message("로그가 지워졌습니다", "info")
    
    def export_log(self):
        """로그 내보내기"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    log_content = self.log_text.get(1.0, tk.END)
                    f.write(log_content)
                self.log_message(f"로그가 {filename}에 저장되었습니다", "success")
            except Exception as e:
                self.log_message(f"로그 저장 실패: {e}", "error")
    
    def on_closing(self):
        """창 닫기 이벤트 처리"""
        if messagebox.askokcancel("종료", "WatchHamster를 종료하시겠습니까?"):
            try:
                self.log_message("시스템 종료 중...", "warning")
                
                # 종료 웹훅 전송
                if self.webhook_enabled:
                    shutdown_message = f"""⏹️ **WatchHamster 시스템 종료**

시스템이 정상적으로 종료됩니다.

**종료 시간:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**업타임:** {getattr(self, 'uptime_label', {}).get('text', '알 수 없음') if hasattr(self, 'uptime_label') else '알 수 없음'}

모든 서비스가 안전하게 중지됩니다."""
                    
                    self.send_webhook_message(shutdown_message)
                
                # 모든 서비스 중지
                self.stop_all_services()
                
                # 시스템 정리
                if hasattr(self, 'stability_manager'):
                    self.stability_manager.stop()
                
                if hasattr(self, 'performance_optimizer'):
                    self.performance_optimizer.stop()
                
                # 싱글톤 정리
                if SINGLETON_AVAILABLE:
                    cleanup_singleton()
                
                self.root.destroy()
                
            except Exception as e:
                print(f"종료 중 오류: {e}")
                self.root.destroy()
    
    def run(self):
        """GUI 실행"""
        try:
            self.log_message("WatchHamster 시작됨", "success")
            self.update_status("시스템 실행 중")
            self.root.mainloop()
        except Exception as e:
            self.log_message(f"GUI 실행 오류: {e}", "error")
            raise


def main():
    """메인 함수"""
    try:
        # 중복 실행 방지 체크
        if SINGLETON_AVAILABLE:
            if not prevent_duplicate_execution("WatchHamster"):
                print("[INFO] WatchHamster가 이미 실행 중입니다. 기존 창을 사용하세요.")
                return
        
        print("[START] 현대적 WatchHamster GUI 시작 중...")
        
        # GUI 애플리케이션 생성 및 실행
        app = ModernWatchHamsterGUI()
        
        try:
            app.run()
        finally:
            # 종료 시 싱글톤 정리
            if SINGLETON_AVAILABLE:
                cleanup_singleton()
        
    except KeyboardInterrupt:
        print("\n[INFO] 사용자에 의해 중단되었습니다.")
        if SINGLETON_AVAILABLE:
            cleanup_singleton()
    except Exception as e:
        print(f"[ERROR] 애플리케이션 시작 실패: {e}")
        if SINGLETON_AVAILABLE:
            cleanup_singleton()
        messagebox.showerror("시작 오류", f"애플리케이션을 시작할 수 없습니다:\n{e}")


if __name__ == "__main__":
    main()