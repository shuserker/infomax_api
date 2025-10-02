# -*- coding: utf-8 -*-
"""
POSCO GUI 관리자 (완전 독립)
POSCO 뉴스 시스템을 위한 전용 GUI 인터페이스
브랜치 전환 상태 실시간 표시 기능 구현
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import threading
from datetime import datetime
from typing import Dict
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from .git_deployment_manager import GitDeploymentManager
    from .integrated_deployment_system import IntegratedDeploymentSystem, DeploymentSession, DeploymentStatus
    from .github_pages_monitor import GitHubPagesMonitor
    from .github_pages_status_gui import GitHubPagesStatusGUI
except ImportError:
    try:
        from git_deployment_manager import GitDeploymentManager
        from integrated_deployment_system import IntegratedDeploymentSystem, DeploymentSession, DeploymentStatus
        from github_pages_monitor import GitHubPagesMonitor
        from github_pages_status_gui import GitHubPagesStatusGUI
    except ImportError as e:
        print(f"Deployment system import 오류: {e}")
        GitDeploymentManager = None
        IntegratedDeploymentSystem = None
        GitHubPagesMonitor = None
        GitHubPagesStatusGUI = None


class PoscoGUIManager:
    """POSCO GUI 관리자 클래스"""
    
    def __init__(self, parent_frame):
        """POSCO GUI 관리자 초기화"""
        self.parent_frame = parent_frame
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # 서비스 인스턴스들
        self.deployment_manager = None
        self.integrated_deployment = None
        self.github_pages_monitor = None
        self.github_pages_gui = None
        
        # GUI 상태
        self.is_monitoring = False
        self.monitor_thread = None
        self.current_deployment_session = None
        
        self.setup_ui()
        self.initialize_services()
    
    def setup_ui(self):
        """POSCO GUI 인터페이스 설정"""
        # 메인 프레임
        main_frame = ttk.LabelFrame(self.parent_frame, text="POSCO 뉴스 시스템", padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 상단 제어 패널
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 시스템 상태
        status_frame = ttk.LabelFrame(control_frame, text="시스템 상태", padding="5")
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.status_var = tk.StringVar(value="시스템 준비 중...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack()
        
        # 제어 버튼들
        button_frame = ttk.LabelFrame(control_frame, text="시스템 제어", padding="5")
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="상태 새로고침", 
                  command=self.refresh_status).pack(side=tk.LEFT, padx=2)
        
        # 탭 컨테이너
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 탭 1: 배포 관리 (핵심 기능)
        self.setup_deployment_tab()
        
        # 탭 2: 통합 배포 시스템
        self.setup_integrated_deployment_tab()
        
        # 탭 3: 모니터링
        self.setup_monitoring_tab()
        
        # 탭 4: 메시지 미리보기 및 수동 전송 (Requirements 6.4, 2.1, 2.3)
        self.setup_message_preview_tab()
    
    def setup_deployment_tab(self):
        """배포 관리 탭 설정 - 브랜치 전환 상태 실시간 표시"""
        deploy_frame = ttk.Frame(self.notebook)
        self.notebook.add(deploy_frame, text="배포 관리")
        
        # 배포 상태
        status_frame = ttk.LabelFrame(deploy_frame, text="배포 상태", padding="10")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.deploy_status_var = tk.StringVar(value="배포 상태 확인 중...")
        deploy_status_label = ttk.Label(status_frame, textvariable=self.deploy_status_var)
        deploy_status_label.pack()
        
        # Git 브랜치 상태 표시 (Requirements 1.3 - GUI에서 브랜치 전환 상태 실시간 표시)
        branch_status_frame = ttk.LabelFrame(deploy_frame, text="Git 브랜치 상태", padding="10")
        branch_status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 현재 브랜치 표시
        current_branch_frame = ttk.Frame(branch_status_frame)
        current_branch_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(current_branch_frame, text="현재 브랜치:").pack(side=tk.LEFT)
        self.current_branch_var = tk.StringVar(value="확인 중...")
        current_branch_label = ttk.Label(current_branch_frame, textvariable=self.current_branch_var, 
                                       foreground="blue", font=("TkDefaultFont", 9, "bold"))
        current_branch_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 브랜치 전환 상태 표시
        switch_status_frame = ttk.Frame(branch_status_frame)
        switch_status_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(switch_status_frame, text="전환 상태:").pack(side=tk.LEFT)
        self.branch_switch_status_var = tk.StringVar(value="대기 중")
        switch_status_label = ttk.Label(switch_status_frame, textvariable=self.branch_switch_status_var)
        switch_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 브랜치 전환 진행률 (실시간 표시)
        progress_frame = ttk.Frame(branch_status_frame)
        progress_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.branch_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.branch_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 진행 단계 표시 (실시간)
        self.progress_step_var = tk.StringVar(value="")
        progress_step_label = ttk.Label(progress_frame, textvariable=self.progress_step_var, 
                                      font=("TkDefaultFont", 8))
        progress_step_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 배포 제어 (안전한 브랜치 전환)
        deploy_control_frame = ttk.LabelFrame(deploy_frame, text="배포 제어", padding="10")
        deploy_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(deploy_control_frame, text="Git 상태 확인", 
                  command=self.check_git_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(deploy_control_frame, text="main → publish", 
                  command=lambda: self.switch_branch("publish")).pack(side=tk.LEFT, padx=5)
        ttk.Button(deploy_control_frame, text="publish → main", 
                  command=lambda: self.switch_branch("main")).pack(side=tk.LEFT, padx=5)
        
        # 배포 로그 (실시간 표시)
        log_frame = ttk.LabelFrame(deploy_frame, text="배포 로그", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.deploy_log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.deploy_log_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_integrated_deployment_tab(self):
        """통합 배포 시스템 탭 설정 (Requirements 1.1, 1.4, 4.1)"""
        integrated_frame = ttk.Frame(self.notebook)
        self.notebook.add(integrated_frame, text="통합 배포")
        
        # 배포 상태 대시보드
        dashboard_frame = ttk.LabelFrame(integrated_frame, text="배포 대시보드", padding="10")
        dashboard_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 현재 배포 세션 정보
        session_info_frame = ttk.Frame(dashboard_frame)
        session_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(session_info_frame, text="현재 세션:").pack(side=tk.LEFT)
        self.current_session_var = tk.StringVar(value="없음")
        ttk.Label(session_info_frame, textvariable=self.current_session_var, 
                 font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # 배포 통계
        stats_frame = ttk.Frame(dashboard_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.total_deployments_var = tk.StringVar(value="총 배포: 0")
        self.success_rate_var = tk.StringVar(value="성공률: 0%")
        self.recent_deployments_var = tk.StringVar(value="최근 24시간: 0")
        
        ttk.Label(stats_frame, textvariable=self.total_deployments_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(stats_frame, textvariable=self.success_rate_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(stats_frame, textvariable=self.recent_deployments_var).pack(side=tk.LEFT)
        
        # 배포 제어 패널
        control_panel_frame = ttk.LabelFrame(integrated_frame, text="배포 제어", padding="10")
        control_panel_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 데이터 입력 영역
        data_frame = ttk.Frame(control_panel_frame)
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(data_frame, text="POSCO 데이터:").pack(anchor=tk.W)
        
        # 간단한 데이터 입력 필드들
        input_frame = ttk.Frame(data_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(input_frame, text="KOSPI:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.kospi_var = tk.StringVar(value="2,450.32")
        ttk.Entry(input_frame, textvariable=self.kospi_var, width=15).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(input_frame, text="환율:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.exchange_var = tk.StringVar(value="1,320.50")
        ttk.Entry(input_frame, textvariable=self.exchange_var, width=15).grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(input_frame, text="POSCO 주가:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.posco_stock_var = tk.StringVar(value="285,000")
        ttk.Entry(input_frame, textvariable=self.posco_stock_var, width=15).grid(row=0, column=5)
        
        # 배포 버튼들
        button_frame = ttk.Frame(control_panel_frame)
        button_frame.pack(fill=tk.X)
        
        self.deploy_button = ttk.Button(button_frame, text="🚀 통합 배포 시작", 
                                       command=self.start_integrated_deployment)
        self.deploy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.rollback_button = ttk.Button(button_frame, text="🔄 롤백 실행", 
                                         command=self.execute_rollback, state=tk.DISABLED)
        self.rollback_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📊 통계 새로고침", 
                  command=self.refresh_deployment_stats).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📜 배포 히스토리", 
                  command=self.show_deployment_history).pack(side=tk.LEFT)
        
        # 실시간 진행 상황 표시
        progress_frame = ttk.LabelFrame(integrated_frame, text="배포 진행 상황", padding="10")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 전체 진행률
        overall_progress_frame = ttk.Frame(progress_frame)
        overall_progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(overall_progress_frame, text="전체 진행률:").pack(side=tk.LEFT)
        self.overall_progress = ttk.Progressbar(overall_progress_frame, mode='determinate')
        self.overall_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.overall_progress_var = tk.StringVar(value="0%")
        ttk.Label(overall_progress_frame, textvariable=self.overall_progress_var).pack(side=tk.RIGHT)
        
        # 현재 단계 표시
        current_step_frame = ttk.Frame(progress_frame)
        current_step_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(current_step_frame, text="현재 단계:").pack(side=tk.LEFT)
        self.current_step_var = tk.StringVar(value="대기 중")
        ttk.Label(current_step_frame, textvariable=self.current_step_var, 
                 font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # 단계별 진행 상황
        steps_frame = ttk.Frame(progress_frame)
        steps_frame.pack(fill=tk.X)
        
        # 단계 목록 (스크롤 가능)
        steps_canvas = tk.Canvas(steps_frame, height=150)
        steps_scrollbar = ttk.Scrollbar(steps_frame, orient="vertical", command=steps_canvas.yview)
        self.steps_scrollable_frame = ttk.Frame(steps_canvas)
        
        self.steps_scrollable_frame.bind(
            "<Configure>",
            lambda e: steps_canvas.configure(scrollregion=steps_canvas.bbox("all"))
        )
        
        steps_canvas.create_window((0, 0), window=self.steps_scrollable_frame, anchor="nw")
        steps_canvas.configure(yscrollcommand=steps_scrollbar.set)
        
        steps_canvas.pack(side="left", fill="both", expand=True)
        steps_scrollbar.pack(side="right", fill="y")
        
        # 단계 상태 표시용 변수들
        self.step_status_vars = {}
        self.step_progress_bars = {}
        
        # 통합 배포 로그
        integrated_log_frame = ttk.LabelFrame(integrated_frame, text="통합 배포 로그", padding="10")
        integrated_log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.integrated_log_text = scrolledtext.ScrolledText(integrated_log_frame, height=12)
        self.integrated_log_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_monitoring_tab(self):
        """모니터링 탭 설정"""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="모니터링")
        
        # 모니터링 제어
        control_frame = ttk.LabelFrame(monitor_frame, text="모니터링 제어", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.monitor_status_var = tk.StringVar(value="모니터링 중지됨")
        monitor_status_label = ttk.Label(control_frame, textvariable=self.monitor_status_var)
        monitor_status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(control_frame, text="모니터링 시작", 
                  command=self.start_monitoring).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="모니터링 중지", 
                  command=self.stop_monitoring).pack(side=tk.LEFT, padx=2)
        
        # GitHub Pages 모니터링 버튼 추가 (Requirements 1.2, 5.4)
        ttk.Separator(control_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(control_frame, text="GitHub Pages 모니터", 
                  command=self.open_github_pages_monitor).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Pages 검증", 
                  command=lambda: self.verify_github_pages_after_deployment()).pack(side=tk.LEFT, padx=2)
        
        # 실시간 로그
        realtime_frame = ttk.LabelFrame(monitor_frame, text="실시간 로그", padding="10")
        realtime_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.realtime_log_text = scrolledtext.ScrolledText(realtime_frame, height=12)
        self.realtime_log_text.pack(fill=tk.BOTH, expand=True)
    
    def initialize_services(self):
        """서비스 인스턴스 초기화"""
        try:
            if GitDeploymentManager:
                self.deployment_manager = GitDeploymentManager()
            
            if IntegratedDeploymentSystem:
                self.integrated_deployment = IntegratedDeploymentSystem()
                # GUI 콜백 등록
                self.integrated_deployment.register_progress_callback(self._on_deployment_progress)
                self.integrated_deployment.register_status_callback(self._on_deployment_status_change)
                self.integrated_deployment.register_error_callback(self._on_deployment_error)
            
            # GitHub Pages 모니터 초기화 (Requirements 1.2, 5.4)
            github_pages_initialized = self.initialize_github_pages_monitor()
            
            if github_pages_initialized:
                self.status_var.set("POSCO 시스템 준비 완료 (GitHub Pages 모니터 포함)")
            else:
                self.status_var.set("POSCO 시스템 준비 완료 (GitHub Pages 모니터 제외)")
            
            # 초기 Git 상태 확인
            self.parent_frame.after(1000, self.check_git_status)
            
            # 배포 통계 초기 로드
            self.parent_frame.after(2000, self.refresh_deployment_stats)
            
        except Exception as e:
            self.status_var.set(f"서비스 초기화 오류: {e}")
    
    def check_git_status(self):
        """Git 상태 확인 (Requirements 3.1)"""
        try:
            if not self.deployment_manager:
                self.log_to_deploy("❌ Git 배포 관리자가 초기화되지 않았습니다.")
                return
            
            self.log_to_deploy("🔍 Git 상태 확인 중...")
            
            # 백그라운드에서 Git 상태 확인
            def check_status():
                try:
                    status_info = self.deployment_manager.check_git_status()
                    
                    # GUI 업데이트 (메인 스레드에서 실행)
                    self.parent_frame.after(0, self._update_git_status_display, status_info)
                    
                except Exception as e:
                    error_msg = f"Git 상태 확인 중 오류: {str(e)}"
                    self.parent_frame.after(0, self.log_to_deploy, f"❌ {error_msg}")
            
            # 백그라운드 스레드에서 실행
            threading.Thread(target=check_status, daemon=True).start()
            
        except Exception as e:
            self.log_to_deploy(f"❌ Git 상태 확인 오류: {e}")
    
    def _update_git_status_display(self, status_info):
        """Git 상태 표시 업데이트 (메인 스레드에서 실행) - 실시간 표시"""
        try:
            if status_info.get('is_git_repo', False):
                current_branch = status_info.get('current_branch', 'unknown')
                
                # 상태에 따른 브랜치 표시
                if current_branch == 'main':
                    self.current_branch_var.set(f"{current_branch} (개발용)")
                elif current_branch == 'publish':
                    self.current_branch_var.set(f"{current_branch} (배포용)")
                else:
                    self.current_branch_var.set(current_branch)
                
                # 상태 메시지 구성
                status_messages = []
                if status_info.get('has_uncommitted_changes', False):
                    status_messages.append("변경사항 있음")
                if status_info.get('has_untracked_files', False):
                    status_messages.append("추적되지 않은 파일 있음")
                if status_info.get('has_conflicts', False):
                    status_messages.append("충돌 상태")
                
                if status_messages:
                    status_text = ", ".join(status_messages)
                    self.branch_switch_status_var.set(f"⚠️ {status_text}")
                else:
                    self.branch_switch_status_var.set("✅ 정상 상태")
                
                # 로그 출력
                self.log_to_deploy(f"✅ Git 상태 확인 완료 - 현재 브랜치: {current_branch}")
                if status_info.get('error_message'):
                    self.log_to_deploy(f"⚠️ 주의사항: {status_info['error_message']}")
                    
            else:
                self.current_branch_var.set("Git 저장소 아님")
                self.branch_switch_status_var.set("❌ Git 저장소가 아닙니다")
                self.log_to_deploy("❌ Git 저장소가 아닙니다")
                
        except Exception as e:
            self.log_to_deploy(f"❌ Git 상태 표시 업데이트 오류: {e}")
    
    def switch_branch(self, target_branch):
        """브랜치 전환 (실시간 상태 표시) - Requirements 1.3"""
        try:
            if not self.deployment_manager:
                messagebox.showerror("오류", "Git 배포 관리자가 초기화되지 않았습니다.")
                return
            
            # 브랜치 전환 시작 표시
            self.branch_switch_status_var.set(f"🔄 {target_branch} 브랜치로 전환 중...")
            self.branch_progress.start(10)  # 진행률 표시 시작
            self.progress_step_var.set("초기화 중...")
            
            self.log_to_deploy(f"🔄 {target_branch} 브랜치로 전환 시작...")
            
            # 백그라운드에서 브랜치 전환 실행
            def perform_switch():
                try:
                    # 진행 상태 콜백 함수 (실시간 표시)
                    def progress_callback(step_message):
                        self.parent_frame.after(0, self._update_progress_step, step_message)
                    
                    # 브랜치 전환 실행 (상세한 결과 정보 반환)
                    switch_result = self.deployment_manager.safe_branch_switch(target_branch, progress_callback)
                    
                    # GUI 업데이트 (메인 스레드에서 실행)
                    self.parent_frame.after(0, self._handle_branch_switch_result, switch_result, target_branch)
                    
                except Exception as e:
                    error_msg = f"브랜치 전환 중 오류: {str(e)}"
                    self.parent_frame.after(0, self._handle_branch_switch_error, error_msg)
            
            # 백그라운드 스레드에서 실행
            threading.Thread(target=perform_switch, daemon=True).start()
            
        except Exception as e:
            self.branch_progress.stop()
            self.branch_switch_status_var.set("❌ 브랜치 전환 오류")
            messagebox.showerror("오류", f"브랜치 전환 오류: {e}")
    
    def _handle_branch_switch_result(self, switch_result, target_branch):
        """브랜치 전환 결과 처리 (메인 스레드에서 실행) - 실시간 표시"""
        try:
            self.branch_progress.stop()  # 진행률 표시 중지
            self.progress_step_var.set("")  # 진행 단계 표시 초기화
            
            if switch_result['success']:
                self.current_branch_var.set(f"{target_branch} ({'개발용' if target_branch == 'main' else '배포용'})")
                self.branch_switch_status_var.set(f"✅ {target_branch} 브랜치 전환 완료")
                
                # 상세 로그 출력
                self.log_to_deploy(f"✅ {target_branch} 브랜치 전환 성공")
                
                # 수행된 단계들 로그
                steps = switch_result.get('steps_completed', [])
                if steps:
                    self.log_to_deploy(f"📋 완료된 단계: {', '.join(steps)}")
                
                # stash 생성 정보
                if switch_result.get('stash_created', False):
                    stash_msg = switch_result.get('stash_message', '')
                    self.log_to_deploy(f"💾 변경사항 stash 생성: {stash_msg}")
                
                # 브랜치 생성 정보
                if switch_result.get('branch_created', False):
                    self.log_to_deploy(f"🆕 새 브랜치 생성: {target_branch}")
                
                # 충돌 해결 정보
                if switch_result.get('conflicts_resolved', False):
                    self.log_to_deploy(f"🔧 Git 충돌 자동 해결 완료")
                    if 'conflict_resolution_summary' in switch_result:
                        summary = switch_result['conflict_resolution_summary']
                        self.log_to_deploy(f"📊 충돌 해결 요약: 총 {summary.get('total_conflicts', 0)}개 중 {summary.get('auto_resolved', 0)}개 자동 해결")
                
                # 성공 알림
                success_msg = f"{target_branch} 브랜치로 성공적으로 전환되었습니다."
                if switch_result.get('stash_created', False):
                    success_msg += "\n\n변경사항이 자동으로 stash되었습니다."
                if switch_result.get('branch_created', False):
                    success_msg += f"\n\n새로운 {target_branch} 브랜치가 생성되었습니다."
                if switch_result.get('conflicts_resolved', False):
                    success_msg += "\n\nGit 충돌이 자동으로 해결되었습니다."
                
                messagebox.showinfo("브랜치 전환 완료", success_msg)
                
                # Git 상태 자동 새로고침
                self.parent_frame.after(1000, self.check_git_status)
                
            else:
                error_msg = switch_result.get('error_message', '알 수 없는 오류')
                
                # 수동 충돌 해결이 필요한 경우 (Requirements 3.3)
                if switch_result.get('manual_conflicts'):
                    self.branch_switch_status_var.set(f"👤 {target_branch} 브랜치 전환 - 수동 해결 필요")
                    self.log_to_deploy(f"👤 수동 충돌 해결 필요: {len(switch_result['manual_conflicts'])}개 파일")
                    
                    # 수동 충돌 해결 GUI 호출
                    self._show_manual_conflict_resolution(switch_result['manual_conflicts'], 
                                                        switch_result.get('conflict_details', {}),
                                                        target_branch)
                else:
                    self.branch_switch_status_var.set(f"❌ {target_branch} 브랜치 전환 실패")
                    
                    # 상세 오류 로그
                    self.log_to_deploy(f"❌ {target_branch} 브랜치 전환 실패: {error_msg}")
                    
                    # 완료된 단계들 로그
                    steps = switch_result.get('steps_completed', [])
                    if steps:
                        self.log_to_deploy(f"📋 완료된 단계: {', '.join(steps)}")
                    
                    # 오류 알림
                    messagebox.showerror("브랜치 전환 실패", 
                                       f"{target_branch} 브랜치 전환에 실패했습니다.\n\n오류: {error_msg}")
                
        except Exception as e:
            self.log_to_deploy(f"❌ 브랜치 전환 결과 처리 오류: {e}")
    
    def _show_manual_conflict_resolution(self, conflict_files, conflict_details, target_branch):
        """수동 충돌 해결 GUI 인터페이스 표시 (Requirements 3.3)"""
        try:
            # 수동 충돌 해결 창 생성
            conflict_window = tk.Toplevel(self.parent_frame)
            conflict_window.title(f"Git 충돌 해결 - {target_branch} 브랜치 전환")
            conflict_window.geometry("800x600")
            conflict_window.transient(self.parent_frame)
            conflict_window.grab_set()
            
            # 메인 프레임
            main_frame = ttk.Frame(conflict_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 제목 및 설명
            title_frame = ttk.Frame(main_frame)
            title_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(title_frame, text="Git 충돌 해결", 
                     font=("TkDefaultFont", 12, "bold")).pack(anchor=tk.W)
            ttk.Label(title_frame, 
                     text=f"{target_branch} 브랜치로 전환하는 중 충돌이 발생했습니다. 아래 파일들을 수동으로 해결해주세요.",
                     wraplength=750).pack(anchor=tk.W, pady=(5, 0))
            
            # 충돌 파일 목록
            files_frame = ttk.LabelFrame(main_frame, text=f"충돌 파일 ({len(conflict_files)}개)", padding="10")
            files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 트리뷰로 파일 목록 표시
            columns = ('파일', '상태', '해결 방법')
            tree = ttk.Treeview(files_frame, columns=columns, show='headings', height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=200)
            
            # 스크롤바
            scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 충돌 파일 정보 추가
            file_items = {}
            for file_path in conflict_files:
                item_id = tree.insert('', tk.END, values=(file_path, '해결 대기', '선택 필요'))
                file_items[item_id] = file_path
            
            # 해결 옵션 프레임
            options_frame = ttk.LabelFrame(main_frame, text="해결 옵션", padding="10")
            options_frame.pack(fill=tk.X, pady=(0, 10))
            
            selected_file_var = tk.StringVar(value="파일을 선택하세요")
            ttk.Label(options_frame, text="선택된 파일:").pack(anchor=tk.W)
            ttk.Label(options_frame, textvariable=selected_file_var, 
                     font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, pady=(0, 10))
            
            # 해결 방법 버튼들
            button_frame = ttk.Frame(options_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(button_frame, text="우리 버전 사용", 
                      command=lambda: self._resolve_selected_conflict(tree, file_items, 'ours', target_branch)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="그들 버전 사용", 
                      command=lambda: self._resolve_selected_conflict(tree, file_items, 'theirs', target_branch)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="파일 열기 (수동 편집)", 
                      command=lambda: self._open_conflict_file(tree, file_items)).pack(side=tk.LEFT, padx=5)
            
            # 하단 제어 버튼
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(control_frame, text="모든 충돌 해결 완료", 
                      command=lambda: self._complete_manual_resolution(conflict_window, target_branch)).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(control_frame, text="취소", 
                      command=conflict_window.destroy).pack(side=tk.RIGHT)
            
            # 파일 선택 이벤트
            def on_file_select(event):
                selection = tree.selection()
                if selection:
                    item_id = selection[0]
                    file_path = file_items[item_id]
                    selected_file_var.set(file_path)
            
            tree.bind('<<TreeviewSelect>>', on_file_select)
            
            # 창을 중앙에 배치
            conflict_window.update_idletasks()
            x = (conflict_window.winfo_screenwidth() // 2) - (conflict_window.winfo_width() // 2)
            y = (conflict_window.winfo_screenheight() // 2) - (conflict_window.winfo_height() // 2)
            conflict_window.geometry(f"+{x}+{y}")
            
            self.log_to_deploy(f"🖥️ 수동 충돌 해결 GUI 표시: {len(conflict_files)}개 파일")
            
        except Exception as e:
            self.log_to_deploy(f"❌ 수동 충돌 해결 GUI 생성 오류: {e}")
            messagebox.showerror("오류", f"충돌 해결 인터페이스 생성 실패: {e}")
    
    def _resolve_selected_conflict(self, tree, file_items, resolution_option, target_branch):
        """선택된 충돌 파일 해결"""
        try:
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("경고", "해결할 파일을 선택하세요.")
                return
            
            item_id = selection[0]
            file_path = file_items[item_id]
            
            if not self.deployment_manager:
                messagebox.showerror("오류", "Git 배포 관리자가 초기화되지 않았습니다.")
                return
            
            # 충돌 해결 실행
            success = self.deployment_manager.resolve_conflict_with_option(file_path, resolution_option)
            
            if success:
                # 트리뷰 업데이트
                resolution_text = {
                    'ours': '우리 버전 사용',
                    'theirs': '그들 버전 사용',
                    'manual': '수동 편집 완료'
                }.get(resolution_option, resolution_option)
                
                tree.item(item_id, values=(file_path, '✅ 해결 완료', resolution_text))
                self.log_to_deploy(f"✅ 충돌 해결 완료: {file_path} ({resolution_text})")
                
                messagebox.showinfo("해결 완료", f"{file_path} 파일의 충돌이 해결되었습니다.")
            else:
                messagebox.showerror("해결 실패", f"{file_path} 파일의 충돌 해결에 실패했습니다.")
                
        except Exception as e:
            self.log_to_deploy(f"❌ 충돌 해결 중 오류: {e}")
            messagebox.showerror("오류", f"충돌 해결 중 오류가 발생했습니다: {e}")
    
    def _open_conflict_file(self, tree, file_items):
        """충돌 파일을 외부 편집기로 열기"""
        try:
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("경고", "열 파일을 선택하세요.")
                return
            
            item_id = selection[0]
            file_path = file_items[item_id]
            
            if not self.deployment_manager:
                messagebox.showerror("오류", "Git 배포 관리자가 초기화되지 않았습니다.")
                return
            
            full_path = os.path.join(self.deployment_manager.base_dir, file_path)
            
            if not os.path.exists(full_path):
                messagebox.showerror("오류", f"파일을 찾을 수 없습니다: {file_path}")
                return
            
            # 시스템 기본 편집기로 파일 열기
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", full_path])
            elif system == "Windows":
                subprocess.run(["notepad", full_path])
            else:  # Linux
                subprocess.run(["xdg-open", full_path])
            
            self.log_to_deploy(f"📝 파일 열기: {file_path}")
            
            # 수동 편집 완료 확인
            result = messagebox.askyesno("수동 편집", 
                                       f"{file_path} 파일을 편집기에서 열었습니다.\n\n"
                                       f"충돌 마커(<<<<<<, ======, >>>>>>)를 제거하고 파일을 저장한 후 "
                                       f"'예'를 클릭하세요.")
            
            if result:
                # 수동 해결 완료로 처리
                success = self.deployment_manager.resolve_conflict_with_option(file_path, 'manual')
                if success:
                    tree.item(item_id, values=(file_path, '✅ 해결 완료', '수동 편집 완료'))
                    self.log_to_deploy(f"✅ 수동 충돌 해결 완료: {file_path}")
                else:
                    messagebox.showerror("해결 실패", f"{file_path} 파일의 수동 해결에 실패했습니다.")
                    
        except Exception as e:
            self.log_to_deploy(f"❌ 파일 열기 중 오류: {e}")
            messagebox.showerror("오류", f"파일 열기 중 오류가 발생했습니다: {e}")
    
    def _complete_manual_resolution(self, conflict_window, target_branch):
        """수동 충돌 해결 완료"""
        try:
            if not self.deployment_manager:
                messagebox.showerror("오류", "Git 배포 관리자가 초기화되지 않았습니다.")
                return
            
            # 남은 충돌이 있는지 확인
            conflict_info = self.deployment_manager.detect_conflict_files()
            
            if conflict_info['has_conflicts']:
                remaining_files = conflict_info['conflict_files']
                messagebox.showwarning("미완료", 
                                     f"아직 해결되지 않은 충돌이 있습니다:\n\n" + 
                                     "\n".join(remaining_files) + 
                                     "\n\n모든 충돌을 해결한 후 다시 시도하세요.")
                return
            
            # 병합 커밋 완료
            if self.deployment_manager._complete_merge_commit():
                self.log_to_deploy("✅ 모든 충돌 해결 및 병합 커밋 완료")
                
                # 브랜치 전환 재시도
                self.log_to_deploy(f"🔄 {target_branch} 브랜치 전환 재시도...")
                
                # 창 닫기
                conflict_window.destroy()
                
                # 브랜치 전환 상태 업데이트
                self.branch_switch_status_var.set(f"✅ {target_branch} 브랜치 전환 완료")
                self.current_branch_var.set(f"{target_branch} ({'개발용' if target_branch == 'main' else '배포용'})")
                
                messagebox.showinfo("완료", f"{target_branch} 브랜치로 성공적으로 전환되었습니다.\n\n모든 충돌이 해결되었습니다.")
                
                # Git 상태 새로고침
                self.parent_frame.after(1000, self.check_git_status)
                
            else:
                messagebox.showerror("실패", "병합 커밋에 실패했습니다. 로그를 확인하세요.")
                
        except Exception as e:
            self.log_to_deploy(f"❌ 수동 충돌 해결 완료 처리 중 오류: {e}")
            messagebox.showerror("오류", f"충돌 해결 완료 처리 중 오류가 발생했습니다: {e}")
    
    def _handle_branch_switch_error(self, error_msg):
        """브랜치 전환 오류 처리 (메인 스레드에서 실행)"""
        try:
            self.branch_progress.stop()
            self.progress_step_var.set("")
            self.branch_switch_status_var.set("❌ 브랜치 전환 오류")
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("브랜치 전환 오류", error_msg)
            
        except Exception as e:
            print(f"브랜치 전환 오류 처리 중 예외: {e}")
    
    def _update_progress_step(self, step_message):
        """진행 단계 표시 업데이트 (메인 스레드에서 실행) - 실시간 표시"""
        try:
            self.progress_step_var.set(step_message)
            self.log_to_deploy(f"📋 진행 단계: {step_message}")
        except Exception as e:
            print(f"진행 단계 업데이트 중 오류: {e}")
    
    def update_deployment_progress(self, step_name, progress_percent, status_message=""):
        """배포 진행률 업데이트 (Requirements 5.1, 5.2)"""
        try:
            # 전체 진행률 업데이트
            if hasattr(self, 'overall_progress'):
                self.overall_progress['value'] = progress_percent
                
            # 진행률 퍼센트 표시 업데이트
            if hasattr(self, 'overall_progress_var'):
                self.overall_progress_var.set(f"{progress_percent:.1f}%")
            
            # 현재 단계 표시 업데이트
            if hasattr(self, 'current_step_var'):
                display_message = f"{step_name}"
                if status_message:
                    display_message += f" - {status_message}"
                self.current_step_var.set(display_message)
            
            # 개별 단계 진행률 업데이트
            if hasattr(self, 'step_progress_bars') and step_name in self.step_progress_bars:
                self.step_progress_bars[step_name]['value'] = progress_percent
            
            # 로그에 진행 상황 기록
            self.log_to_deploy(f"📊 배포 진행률: {progress_percent:.1f}% - {step_name}")
            if status_message:
                self.log_to_deploy(f"   상태: {status_message}")
                
        except Exception as e:
            self.log_to_deploy(f"❌ 배포 진행률 업데이트 오류: {str(e)}")
    
    def reset_deployment_progress(self):
        """배포 진행률 초기화"""
        try:
            if hasattr(self, 'overall_progress'):
                self.overall_progress['value'] = 0
                
            if hasattr(self, 'overall_progress_var'):
                self.overall_progress_var.set("0%")
            
            if hasattr(self, 'current_step_var'):
                self.current_step_var.set("대기 중")
            
            # 모든 단계 진행률 초기화
            if hasattr(self, 'step_progress_bars'):
                for progress_bar in self.step_progress_bars.values():
                    progress_bar['value'] = 0
            
            # 단계 상태 초기화
            if hasattr(self, 'step_status_vars'):
                for status_var in self.step_status_vars.values():
                    status_var.set("대기 중")
                    
            self.log_to_deploy("🔄 배포 진행률 초기화 완료")
            
        except Exception as e:
            self.log_to_deploy(f"❌ 배포 진행률 초기화 오류: {str(e)}")
    
    def complete_deployment_progress(self, success=True):
        """배포 진행률 완료 처리"""
        try:
            if success:
                if hasattr(self, 'overall_progress'):
                    self.overall_progress['value'] = 100
                    
                if hasattr(self, 'overall_progress_var'):
                    self.overall_progress_var.set("100%")
                
                if hasattr(self, 'current_step_var'):
                    self.current_step_var.set("✅ 배포 완료")
                
                # 모든 단계를 완료로 표시
                if hasattr(self, 'step_progress_bars'):
                    for progress_bar in self.step_progress_bars.values():
                        progress_bar['value'] = 100
                
                if hasattr(self, 'step_status_vars'):
                    for status_var in self.step_status_vars.values():
                        status_var.set("✅ 완료")
                        
                self.log_to_deploy("✅ 배포 진행률 완료 처리")
                
            else:
                if hasattr(self, 'current_step_var'):
                    self.current_step_var.set("❌ 배포 실패")
                
                self.log_to_deploy("❌ 배포 진행률 실패 처리")
                
        except Exception as e:
            self.log_to_deploy(f"❌ 배포 진행률 완료 처리 오류: {str(e)}")
    
    def log_to_deploy(self, message):
        """배포 로그에 메시지 추가 - 실시간 로그 표시"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_entry = f"[{timestamp}] {message}\n"
            
            self.deploy_log_text.insert(tk.END, log_entry)
            self.deploy_log_text.see(tk.END)
            
            # 로그가 너무 많이 쌓이면 앞부분 삭제
            lines = self.deploy_log_text.get(1.0, tk.END).count('\n')
            if lines > 1000:
                self.deploy_log_text.delete(1.0, "200.0")
                
        except Exception as e:
            print(f"배포 로그 추가 중 오류: {e}")
    
    def start_integrated_deployment(self):
        """통합 배포 시스템 시작 (Requirements 1.1, 1.4, 4.1)"""
        try:
            if not self.integrated_deployment:
                messagebox.showerror("오류", "통합 배포 시스템이 초기화되지 않았습니다.")
                return
            
            # 배포 중인지 확인
            if self.current_deployment_session and self.current_deployment_session.status == DeploymentStatus.RUNNING:
                messagebox.showwarning("경고", "이미 배포가 진행 중입니다.")
                return
            
            # 데이터 수집
            data = {
                'kospi': self.kospi_var.get(),
                'exchange_rate': self.exchange_var.get(),
                'posco_stock': self.posco_stock_var.get(),
                'analysis': f'POSCO 통합 분석 리포트 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'news': [
                    {
                        'title': 'POSCO 자동 배포 시스템',
                        'summary': '통합 배포 시스템을 통한 자동 리포트 생성',
                        'date': datetime.now().strftime("%Y-%m-%d")
                    }
                ]
            }
            
            # 배포 버튼 비활성화
            self.deploy_button.config(state=tk.DISABLED)
            
            # 진행 상황 초기화
            self.overall_progress['value'] = 0
            self.overall_progress_var.set("0%")
            self.current_step_var.set("배포 시작...")
            
            # 단계별 진행 상황 초기화
            self._initialize_deployment_steps()
            
            self.log_to_integrated("🚀 통합 배포 시스템 시작...")
            
            # 백그라운드에서 배포 실행
            def run_deployment():
                try:
                    session = self.integrated_deployment.execute_integrated_deployment(data)
                    self.current_deployment_session = session
                    
                    # GUI 업데이트 (메인 스레드에서 실행)
                    self.parent_frame.after(0, self._on_deployment_complete, session)
                    
                except Exception as e:
                    error_msg = f"배포 실행 중 오류: {str(e)}"
                    self.parent_frame.after(0, self._on_deployment_error, error_msg, {})
            
            # 백그라운드 스레드에서 실행
            threading.Thread(target=run_deployment, daemon=True).start()
            
        except Exception as e:
            self.log_to_integrated(f"❌ 통합 배포 시작 오류: {e}")
            messagebox.showerror("오류", f"통합 배포 시작 중 오류가 발생했습니다: {e}")
            self.deploy_button.config(state=tk.NORMAL)
    
    def execute_rollback(self):
        """롤백 실행"""
        try:
            if not self.integrated_deployment:
                messagebox.showerror("오류", "통합 배포 시스템이 초기화되지 않았습니다.")
                return
            
            if not self.current_deployment_session or not self.current_deployment_session.rollback_available:
                messagebox.showwarning("경고", "롤백할 수 있는 배포가 없습니다.")
                return
            
            # 롤백 확인
            result = messagebox.askyesno("롤백 확인", 
                                       f"배포 세션 {self.current_deployment_session.session_id}을(를) 롤백하시겠습니까?\n\n"
                                       f"이 작업은 되돌릴 수 없습니다.")
            
            if not result:
                return
            
            self.log_to_integrated("🔄 롤백 실행 시작...")
            
            # 백그라운드에서 롤백 실행
            def run_rollback():
                try:
                    success = self.integrated_deployment.execute_rollback(self.current_deployment_session)
                    self.parent_frame.after(0, self._on_rollback_complete, success)
                    
                except Exception as e:
                    error_msg = f"롤백 실행 중 오류: {str(e)}"
                    self.parent_frame.after(0, self._on_deployment_error, error_msg, {})
            
            threading.Thread(target=run_rollback, daemon=True).start()
            
        except Exception as e:
            self.log_to_integrated(f"❌ 롤백 실행 오류: {e}")
            messagebox.showerror("오류", f"롤백 실행 중 오류가 발생했습니다: {e}")
    
    def refresh_deployment_stats(self):
        """배포 통계 새로고침"""
        try:
            if not self.integrated_deployment:
                return
            
            stats = self.integrated_deployment.get_deployment_statistics()
            
            self.total_deployments_var.set(f"총 배포: {stats.get('total_deployments', 0)}")
            self.success_rate_var.set(f"성공률: {stats.get('success_rate', 0)}%")
            self.recent_deployments_var.set(f"최근 24시간: {stats.get('recent_deployments_24h', 0)}")
            
            # 롤백 버튼 상태 업데이트
            if stats.get('rollback_available', False):
                self.rollback_button.config(state=tk.NORMAL)
            else:
                self.rollback_button.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log_to_integrated(f"❌ 배포 통계 새로고침 오류: {e}")
    
    def show_deployment_history(self):
        """배포 히스토리 표시"""
        try:
            if not self.integrated_deployment:
                messagebox.showerror("오류", "통합 배포 시스템이 초기화되지 않았습니다.")
                return
            
            history = self.integrated_deployment.get_deployment_history(20)
            
            # 히스토리 창 생성
            history_window = tk.Toplevel(self.parent_frame)
            history_window.title("배포 히스토리")
            history_window.geometry("900x600")
            history_window.transient(self.parent_frame)
            
            # 메인 프레임
            main_frame = ttk.Frame(history_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 제목
            ttk.Label(main_frame, text="배포 히스토리", 
                     font=("TkDefaultFont", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
            
            # 트리뷰로 히스토리 표시
            columns = ('세션 ID', '시작 시간', '상태', '성공 단계', '총 단계', '소요 시간')
            tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=140)
            
            # 스크롤바
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 히스토리 데이터 추가
            for session in history:
                try:
                    # 소요 시간 계산
                    if session.end_time:
                        start_dt = datetime.fromisoformat(session.start_time)
                        end_dt = datetime.fromisoformat(session.end_time)
                        duration = str(end_dt - start_dt).split('.')[0]  # 마이크로초 제거
                    else:
                        duration = "진행 중"
                    
                    # 상태 표시
                    status_text = {
                        DeploymentStatus.SUCCESS: "✅ 성공",
                        DeploymentStatus.FAILED: "❌ 실패",
                        DeploymentStatus.RUNNING: "🔄 진행 중",
                        DeploymentStatus.ROLLED_BACK: "🔄 롤백됨"
                    }.get(session.status, str(session.status))
                    
                    tree.insert('', tk.END, values=(
                        session.session_id,
                        session.start_time.split('T')[0] + ' ' + session.start_time.split('T')[1][:8],
                        status_text,
                        session.success_count,
                        len(session.steps),
                        duration
                    ))
                    
                except Exception as e:
                    self.log_to_integrated(f"❌ 히스토리 항목 처리 오류: {e}")
            
            # 닫기 버튼
            ttk.Button(main_frame, text="닫기", 
                      command=history_window.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            self.log_to_integrated(f"❌ 배포 히스토리 표시 오류: {e}")
            messagebox.showerror("오류", f"배포 히스토리 표시 중 오류가 발생했습니다: {e}")
    
    def _initialize_deployment_steps(self):
        """배포 단계 초기화"""
        try:
            # 기존 단계 위젯들 제거
            for widget in self.steps_scrollable_frame.winfo_children():
                widget.destroy()
            
            self.step_status_vars.clear()
            self.step_progress_bars.clear()
            
            # 배포 단계 정의
            steps = [
                ("pre_check", "배포 전 상태 확인"),
                ("backup", "백업 생성"),
                ("html_generation", "HTML 리포트 생성"),
                ("branch_switch", "브랜치 전환"),
                ("merge_changes", "변경사항 병합"),
                ("commit_changes", "변경사항 커밋"),
                ("push_remote", "원격 저장소 푸시"),
                ("verify_pages", "GitHub Pages 확인"),
                ("send_notification", "알림 전송"),
                ("cleanup", "정리 작업")
            ]
            
            # 각 단계별 위젯 생성
            for i, (step_id, step_name) in enumerate(steps):
                step_frame = ttk.Frame(self.steps_scrollable_frame)
                step_frame.pack(fill=tk.X, pady=2)
                
                # 단계 이름
                ttk.Label(step_frame, text=f"{i+1}. {step_name}", width=25).pack(side=tk.LEFT)
                
                # 상태 표시
                status_var = tk.StringVar(value="⏳ 대기")
                self.step_status_vars[step_id] = status_var
                ttk.Label(step_frame, textvariable=status_var, width=15).pack(side=tk.LEFT, padx=(10, 0))
                
                # 진행률 바
                progress_bar = ttk.Progressbar(step_frame, mode='determinate', length=100)
                progress_bar.pack(side=tk.LEFT, padx=(10, 0))
                self.step_progress_bars[step_id] = progress_bar
            
        except Exception as e:
            self.log_to_integrated(f"❌ 배포 단계 초기화 오류: {e}")
    
    def _on_deployment_progress(self, message: str, progress: int):
        """배포 진행 상황 콜백 (실시간 모니터링)"""
        try:
            # 메인 스레드에서 실행되도록 보장
            def update_gui():
                self.overall_progress['value'] = progress
                self.overall_progress_var.set(f"{progress}%")
                self.current_step_var.set(message)
                self.log_to_integrated(f"📊 {message} ({progress}%)")
            
            if threading.current_thread() == threading.main_thread():
                update_gui()
            else:
                self.parent_frame.after(0, update_gui)
                
        except Exception as e:
            print(f"배포 진행 상황 콜백 오류: {e}")
    
    def _on_deployment_status_change(self, session: DeploymentSession):
        """배포 상태 변경 콜백"""
        try:
            def update_gui():
                self.current_session_var.set(session.session_id)
                
                # 단계별 상태 업데이트
                for step in session.steps:
                    if step.step_id in self.step_status_vars:
                        status_text = {
                            DeploymentStatus.PENDING: "⏳ 대기",
                            DeploymentStatus.RUNNING: "🔄 진행 중",
                            DeploymentStatus.SUCCESS: "✅ 완료",
                            DeploymentStatus.FAILED: "❌ 실패"
                        }.get(step.status, str(step.status))
                        
                        self.step_status_vars[step.step_id].set(status_text)
                        
                        if step.step_id in self.step_progress_bars:
                            self.step_progress_bars[step.step_id]['value'] = step.progress
                
                # 전체 진행률 업데이트
                self.overall_progress['value'] = session.total_progress
                self.overall_progress_var.set(f"{session.total_progress}%")
                
                # 배포 통계 새로고침
                self.refresh_deployment_stats()
            
            if threading.current_thread() == threading.main_thread():
                update_gui()
            else:
                self.parent_frame.after(0, update_gui)
                
        except Exception as e:
            print(f"배포 상태 변경 콜백 오류: {e}")
    
    def _on_deployment_error(self, error_message: str, error_details: Dict):
        """배포 오류 콜백"""
        try:
            def update_gui():
                self.log_to_integrated(f"❌ 배포 오류: {error_message}")
                self.current_step_var.set("오류 발생")
                self.deploy_button.config(state=tk.NORMAL)
                
                messagebox.showerror("배포 오류", f"배포 중 오류가 발생했습니다:\n\n{error_message}")
            
            if threading.current_thread() == threading.main_thread():
                update_gui()
            else:
                self.parent_frame.after(0, update_gui)
                
        except Exception as e:
            print(f"배포 오류 콜백 오류: {e}")
    
    def _on_deployment_complete(self, session: DeploymentSession):
        """배포 완료 처리"""
        try:
            self.current_deployment_session = session
            
            if session.status == DeploymentStatus.SUCCESS:
                self.log_to_integrated(f"✅ 통합 배포 성공 완료: {session.session_id}")
                self.current_step_var.set("배포 완료")
                
                # 배포 성공 후 GitHub Pages 접근성 검증 자동 실행 (Requirements 1.2, 5.4)
                self.log_to_integrated("🌐 GitHub Pages 접근성 검증 시작...")
                self.verify_github_pages_after_deployment()
                
                messagebox.showinfo("배포 완료", 
                                  f"통합 배포가 성공적으로 완료되었습니다!\n\n"
                                  f"세션 ID: {session.session_id}\n"
                                  f"완료 단계: {session.success_count}/{len(session.steps)}\n\n"
                                  f"GitHub Pages 접근성 검증이 진행 중입니다.")
            else:
                self.log_to_integrated(f"❌ 통합 배포 실패: {session.session_id}")
                self.current_step_var.set("배포 실패")
                
                error_msg = session.error_message or "알 수 없는 오류"
                messagebox.showerror("배포 실패", 
                                   f"통합 배포가 실패했습니다.\n\n"
                                   f"세션 ID: {session.session_id}\n"
                                   f"오류: {error_msg}")
            
            # 배포 버튼 다시 활성화
            self.deploy_button.config(state=tk.NORMAL)
            
            # 통계 새로고침
            self.refresh_deployment_stats()
            
        except Exception as e:
            self.log_to_integrated(f"❌ 배포 완료 처리 오류: {e}")
    
    def _on_rollback_complete(self, success: bool):
        """롤백 완료 처리"""
        try:
            if success:
                self.log_to_integrated("✅ 롤백 완료")
                messagebox.showinfo("롤백 완료", "롤백이 성공적으로 완료되었습니다.")
            else:
                self.log_to_integrated("❌ 롤백 실패")
                messagebox.showerror("롤백 실패", "롤백 실행에 실패했습니다.")
            
            # 통계 새로고침
            self.refresh_deployment_stats()
            
        except Exception as e:
            self.log_to_integrated(f"❌ 롤백 완료 처리 오료: {e}")
    
    def log_to_integrated(self, message):
        """통합 배포 로그에 메시지 추가"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_entry = f"[{timestamp}] {message}\n"
            
            self.integrated_log_text.insert(tk.END, log_entry)
            self.integrated_log_text.see(tk.END)
            
            # 로그가 너무 많이 쌓이면 앞부분 삭제
            lines = self.integrated_log_text.get(1.0, tk.END).count('\n')
            if lines > 1000:
                self.integrated_log_text.delete(1.0, "200.0")
                
        except Exception as e:
            print(f"통합 배포 로그 추가 중 오류: {e}")
    
    def refresh_status(self):
        """상태 새로고침"""
        try:
            self.status_var.set("상태 새로고침 중...")
            self.check_git_status()
            self.refresh_deployment_stats()
            self.status_var.set("상태 새로고침 완료")
        except Exception as e:
            self.status_var.set(f"상태 새로고침 오류: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        try:
            if not self.is_monitoring:
                self.is_monitoring = True
                self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
                self.monitor_thread.start()
                
                self.monitor_status_var.set("모니터링 실행 중")
                
        except Exception as e:
            messagebox.showerror("오류", f"모니터링 시작 오류: {e}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        try:
            self.is_monitoring = False
            self.monitor_status_var.set("모니터링 중지됨")
            
        except Exception as e:
            messagebox.showerror("오류", f"모니터링 중지 오류: {e}")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                # Git 상태 주기적 확인
                current_time = datetime.now().strftime("%H:%M:%S")
                log_message = f"[{current_time}] Git 상태 모니터링 중...\n"
                
                # GUI 업데이트 (메인 스레드에서 실행)
                self.realtime_log_text.after(0, self._append_log, log_message)
                
                # 30초 대기
                import time
                time.sleep(30)
                
                # Git 상태 확인
                if self.deployment_manager:
                    self.parent_frame.after(0, self.check_git_status)
                
            except Exception as e:
                error_message = f"[{datetime.now()}] 모니터링 오류: {e}\n"
                self.realtime_log_text.after(0, self._append_log, error_message)
                break
    
    def _append_log(self, message):
        """로그 메시지 추가 (메인 스레드에서 실행)"""
        self.realtime_log_text.insert(tk.END, message)
        self.realtime_log_text.see(tk.END)
        
        # 로그가 너무 많이 쌓이면 앞부분 삭제
        lines = self.realtime_log_text.get(1.0, tk.END).count('\n')
        if lines > 500:
            self.realtime_log_text.delete(1.0, "100.0")
    
    def get_status(self):
        """현재 상태 반환"""
        return {
            'is_monitoring': self.is_monitoring,
            'services_initialized': bool(self.deployment_manager),
            'github_pages_monitor_available': bool(self.github_pages_monitor),
            'last_check': datetime.now().isoformat()
        }
    
    def open_github_pages_monitor(self):
        """GitHub Pages 모니터링 GUI 열기 (Requirements 1.2, 5.4)"""
        try:
            if not GitHubPagesStatusGUI:
                messagebox.showerror("오류", "GitHub Pages 모니터링 시스템을 사용할 수 없습니다.")
                return
            
            # 이미 열려있는 창이 있으면 포커스만 이동
            if self.github_pages_gui and hasattr(self.github_pages_gui, 'root'):
                try:
                    self.github_pages_gui.root.lift()
                    self.github_pages_gui.root.focus_force()
                    return
                except:
                    # 창이 닫혔으면 새로 생성
                    pass
            
            # 새 GitHub Pages 모니터링 GUI 생성
            self.github_pages_gui = GitHubPagesStatusGUI(parent=self.parent_frame)
            
            self.log_to_deploy("🌐 GitHub Pages 모니터링 GUI 열림")
            
        except Exception as e:
            error_msg = f"GitHub Pages 모니터링 GUI 열기 실패: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)
    
    def initialize_github_pages_monitor(self):
        """GitHub Pages 모니터 초기화 (Requirements 1.2, 5.4)"""
        try:
            if GitHubPagesMonitor:
                self.github_pages_monitor = GitHubPagesMonitor()
                
                # 콜백 등록
                def status_callback(url, status, details):
                    self.log_to_deploy(f"🌐 GitHub Pages 상태: {url} -> {status.value}")
                
                def alert_callback(message, details):
                    self.log_to_deploy(f"🚨 GitHub Pages 알림: {message}")
                    # GUI에서 알림 표시
                    self.parent_frame.after(0, lambda: messagebox.showwarning("GitHub Pages 알림", message))
                
                def redeploy_callback(reason):
                    self.log_to_deploy(f"🔄 GitHub Pages 재배포 요청: {reason}")
                    # 자동 재배포 실행
                    response = messagebox.askyesno(
                        "자동 재배포", 
                        f"GitHub Pages 접근 실패로 인한 재배포 요청:\n{reason}\n\n자동 재배포를 실행하시겠습니까?"
                    )
                    if response:
                        self.start_integrated_deployment()
                    return response
                
                # 콜백 등록
                self.github_pages_monitor.register_status_callback(status_callback)
                self.github_pages_monitor.register_alert_callback(alert_callback)
                self.github_pages_monitor.register_redeploy_callback(redeploy_callback)
                
                self.log_to_deploy("✅ GitHub Pages 모니터 초기화 완료")
                return True
            else:
                self.log_to_deploy("⚠️ GitHub Pages 모니터 모듈을 사용할 수 없습니다")
                return False
                
        except Exception as e:
            error_msg = f"GitHub Pages 모니터 초기화 실패: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            return False
    
    def verify_github_pages_after_deployment(self, pages_url: str = None):
        """배포 후 GitHub Pages 접근성 검증 (Requirements 1.2, 5.4)"""
        try:
            if not self.github_pages_monitor:
                self.log_to_deploy("⚠️ GitHub Pages 모니터가 초기화되지 않았습니다")
                return False
            
            if not pages_url:
                # 기본 URL 사용 (설정에서 로드)
                config_file = os.path.join(self.config_dir, "gui_config.json")
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        pages_url = config.get('github_pages_url', 'https://username.github.io/repository')
                except:
                    pages_url = 'https://username.github.io/repository'
            
            self.log_to_deploy(f"🌐 GitHub Pages 접근성 검증 시작: {pages_url}")
            
            # 백그라운드에서 검증 실행
            def run_verification():
                try:
                    result = self.github_pages_monitor.verify_github_pages_deployment(pages_url, max_wait_time=300)
                    
                    # 결과 처리 (메인 스레드에서)
                    self.parent_frame.after(0, self._handle_pages_verification_result, result)
                    
                except Exception as e:
                    error_msg = f"GitHub Pages 검증 중 오류: {str(e)}"
                    self.parent_frame.after(0, lambda: self.log_to_deploy(f"❌ {error_msg}"))
            
            threading.Thread(target=run_verification, daemon=True).start()
            return True
            
        except Exception as e:
            error_msg = f"GitHub Pages 검증 시작 실패: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            return False
    
    def _handle_pages_verification_result(self, result):
        """GitHub Pages 검증 결과 처리 (메인 스레드에서 실행)"""
        try:
            if result['deployment_successful'] and result['final_accessible']:
                self.log_to_deploy(f"✅ GitHub Pages 접근 성공: {result['url']}")
                self.log_to_deploy(f"   확인 횟수: {result['checks_performed']}, 대기시간: {result['total_wait_time']:.1f}초")
                
                messagebox.showinfo(
                    "GitHub Pages 검증 성공",
                    f"GitHub Pages 접근 성공!\n\nURL: {result['url']}\n확인 횟수: {result['checks_performed']}\n대기시간: {result['total_wait_time']:.1f}초"
                )
            else:
                self.log_to_deploy(f"❌ GitHub Pages 접근 실패: {result['url']}")
                self.log_to_deploy(f"   확인 횟수: {result['checks_performed']}, 대기시간: {result['total_wait_time']:.1f}초")
                self.log_to_deploy(f"   오류: {result.get('error_message', '알 수 없는 오류')}")
                
                # 재배포 옵션 제공
                response = messagebox.askyesno(
                    "GitHub Pages 접근 실패",
                    f"GitHub Pages 접근에 실패했습니다.\n\nURL: {result['url']}\n오류: {result.get('error_message', '알 수 없는 오류')}\n\n자동 재배포를 시도하시겠습니까?"
                )
                
                if response:
                    self.start_integrated_deployment()
                    
        except Exception as e:
            self.log_to_deploy(f"❌ GitHub Pages 검증 결과 처리 오류: {str(e)}")
    
    def start_github_pages_monitoring(self, url: str = None, interval: int = 30):
        """GitHub Pages 지속적인 모니터링 시작 (Requirements 5.4)"""
        try:
            if not self.github_pages_monitor:
                self.log_to_deploy("⚠️ GitHub Pages 모니터가 초기화되지 않았습니다")
                return False
            
            if not url:
                # 기본 URL 사용
                config_file = os.path.join(self.config_dir, "gui_config.json")
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        url = config.get('github_pages_url', 'https://username.github.io/repository')
                except:
                    url = 'https://username.github.io/repository'
            
            session_id = self.github_pages_monitor.start_continuous_monitoring(url, interval)
            
            if session_id:
                self.log_to_deploy(f"📊 GitHub Pages 지속적인 모니터링 시작: {session_id}")
                self.log_to_deploy(f"   URL: {url}, 간격: {interval}초")
                return True
            else:
                self.log_to_deploy("❌ GitHub Pages 모니터링 시작 실패")
                return False
                
        except Exception as e:
            error_msg = f"GitHub Pages 모니터링 시작 실패: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            return False
    
    def stop_github_pages_monitoring(self):
        """GitHub Pages 지속적인 모니터링 중지"""
        try:
            if self.github_pages_monitor:
                self.github_pages_monitor.stop_continuous_monitoring()
                self.log_to_deploy("📊 GitHub Pages 지속적인 모니터링 중지")
                return True
            else:
                self.log_to_deploy("⚠️ GitHub Pages 모니터가 초기화되지 않았습니다")
                return False
                
        except Exception as e:
            error_msg = f"GitHub Pages 모니터링 중지 실패: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            return False
    
    def setup_message_preview_tab(self):
        """메시지 미리보기 탭 설정 (Requirements 6.4, 2.1, 2.3)"""
        message_frame = ttk.Frame(self.notebook)
        self.notebook.add(message_frame, text="메시지 미리보기")
        
        # 상단 제어 패널
        control_frame = ttk.LabelFrame(message_frame, text="메시지 제어", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 메시지 타입 선택
        type_frame = ttk.Frame(control_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="메시지 타입:").pack(side=tk.LEFT)
        self.message_type_var = tk.StringVar(value="deployment_success")
        message_type_combo = ttk.Combobox(type_frame, textvariable=self.message_type_var,
                                         values=["deployment_success", "deployment_failure", "deployment_start", 
                                                "system_status", "data_update", "error_alert"],
                                         state="readonly", width=20)
        message_type_combo.pack(side=tk.LEFT, padx=(10, 20))
        message_type_combo.bind('<<ComboboxSelected>>', self._on_message_type_changed)
        
        # 우선순위 선택
        ttk.Label(type_frame, text="우선순위:").pack(side=tk.LEFT)
        self.message_priority_var = tk.StringVar(value="normal")
        priority_combo = ttk.Combobox(type_frame, textvariable=self.message_priority_var,
                                     values=["low", "normal", "high", "critical"],
                                     state="readonly", width=15)
        priority_combo.pack(side=tk.LEFT, padx=(10, 0))
        priority_combo.bind('<<ComboboxSelected>>', self._on_message_priority_changed)
        
        # 메시지 데이터 입력 영역
        data_frame = ttk.LabelFrame(message_frame, text="메시지 데이터", padding="10")
        data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 동적 데이터 입력 필드들
        input_grid_frame = ttk.Frame(data_frame)
        input_grid_frame.pack(fill=tk.X, pady=(0, 10))
        
        # KOSPI 데이터
        ttk.Label(input_grid_frame, text="KOSPI:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.kospi_preview_var = tk.StringVar(value="2,450.32")
        ttk.Entry(input_grid_frame, textvariable=self.kospi_preview_var, width=15).grid(row=0, column=1, padx=(0, 20))
        
        # 환율 데이터
        ttk.Label(input_grid_frame, text="환율(USD):").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.exchange_preview_var = tk.StringVar(value="1,320.50")
        ttk.Entry(input_grid_frame, textvariable=self.exchange_preview_var, width=15).grid(row=0, column=3, padx=(0, 20))
        
        # POSCO 주가
        ttk.Label(input_grid_frame, text="POSCO 주가:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.posco_stock_preview_var = tk.StringVar(value="285,000")
        ttk.Entry(input_grid_frame, textvariable=self.posco_stock_preview_var, width=15).grid(row=0, column=5)
        
        # 배포 정보
        ttk.Label(input_grid_frame, text="배포 상태:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.deployment_status_var = tk.StringVar(value="성공")
        status_combo = ttk.Combobox(input_grid_frame, textvariable=self.deployment_status_var,
                                   values=["성공", "실패", "진행중", "대기중"],
                                   state="readonly", width=12)
        status_combo.grid(row=1, column=1, padx=(0, 20), pady=(10, 0))
        
        # 배포 시간
        ttk.Label(input_grid_frame, text="배포 시간:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.deployment_time_var = tk.StringVar(value="45")
        ttk.Entry(input_grid_frame, textvariable=self.deployment_time_var, width=15).grid(row=1, column=3, padx=(0, 20), pady=(10, 0))
        ttk.Label(input_grid_frame, text="초").grid(row=1, column=4, sticky=tk.W, pady=(10, 0))
        
        # 미리보기 업데이트 버튼
        update_frame = ttk.Frame(data_frame)
        update_frame.pack(fill=tk.X)
        
        ttk.Button(update_frame, text="🔄 미리보기 새로고침", 
                  command=self.update_message_preview).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(update_frame, text="📋 샘플 데이터 로드", 
                  command=self.load_sample_message_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(update_frame, text="💾 데이터 저장", 
                  command=self.save_message_data).pack(side=tk.LEFT)
        
        # 메시지 미리보기 영역
        preview_frame = ttk.LabelFrame(message_frame, text="메시지 미리보기", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 미리보기 텍스트 영역
        self.message_preview_text = scrolledtext.ScrolledText(preview_frame, height=12, 
                                                             font=('Consolas', 10),
                                                             wrap=tk.WORD)
        self.message_preview_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 수동 전송 제어 패널
        send_frame = ttk.LabelFrame(message_frame, text="수동 전송", padding="10")
        send_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 웹훅 URL 입력
        webhook_frame = ttk.Frame(send_frame)
        webhook_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(webhook_frame, text="웹훅 URL:").pack(side=tk.LEFT)
        self.webhook_url_var = tk.StringVar(value="https://hooks.slack.com/services/...")
        webhook_entry = ttk.Entry(webhook_frame, textvariable=self.webhook_url_var, width=60)
        webhook_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        ttk.Button(webhook_frame, text="📋 클립보드에서", 
                  command=self.paste_webhook_url).pack(side=tk.RIGHT)
        
        # 전송 버튼들
        button_frame = ttk.Frame(send_frame)
        button_frame.pack(fill=tk.X)
        
        self.send_test_button = ttk.Button(button_frame, text="🧪 테스트 전송", 
                                          command=self.send_test_message)
        self.send_test_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.send_manual_button = ttk.Button(button_frame, text="📤 수동 전송", 
                                            command=self.send_manual_message)
        self.send_manual_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📊 전송 히스토리", 
                  command=self.show_send_history).pack(side=tk.LEFT, padx=(0, 10))
        
        # 전송 상태 표시
        self.send_status_var = tk.StringVar(value="전송 대기 중")
        send_status_label = ttk.Label(button_frame, textvariable=self.send_status_var,
                                     font=("TkDefaultFont", 9))
        send_status_label.pack(side=tk.RIGHT)
        
        # 초기 미리보기 업데이트
        self.parent_frame.after(500, self.update_message_preview)
    
    def _on_message_type_changed(self, event=None):
        """메시지 타입 변경 이벤트 처리"""
        self.update_message_preview()
    
    def _on_message_priority_changed(self, event=None):
        """메시지 우선순위 변경 이벤트 처리"""
        self.update_message_preview()
    
    def update_message_preview(self):
        """메시지 미리보기 업데이트 (Requirements 2.1, 2.3)"""
        try:
            # 메시지 템플릿 엔진이 없으면 초기화
            if not hasattr(self, 'message_engine'):
                try:
                    from .message_template_engine import MessageTemplateEngine, MessageType, MessagePriority
                    self.message_engine = MessageTemplateEngine()
                except ImportError:
                    self.message_preview_text.delete(1.0, tk.END)
                    self.message_preview_text.insert(tk.END, "❌ 메시지 템플릿 엔진을 로드할 수 없습니다.")
                    return
            
            # 현재 입력된 데이터 수집
            message_data = {
                'kospi': self.kospi_preview_var.get(),
                'exchange_rate': self.exchange_preview_var.get(),
                'posco_stock': self.posco_stock_preview_var.get(),
                'deployment_status': self.deployment_status_var.get(),
                'deployment_time': self.deployment_time_var.get(),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'deployment_url': 'https://username.github.io/repository'
            }
            
            # 메시지 타입 변환
            message_type_map = {
                'deployment_success': 'DEPLOYMENT_SUCCESS',
                'deployment_failure': 'DEPLOYMENT_FAILURE', 
                'deployment_start': 'DEPLOYMENT_START',
                'system_status': 'SYSTEM_STATUS',
                'data_update': 'DATA_UPDATE',
                'error_alert': 'ERROR_ALERT'
            }
            
            message_type_str = message_type_map.get(self.message_type_var.get(), 'DEPLOYMENT_SUCCESS')
            
            # 우선순위 변환
            priority_map = {
                'low': 'LOW',
                'normal': 'NORMAL',
                'high': 'HIGH',
                'critical': 'CRITICAL'
            }
            
            priority_str = priority_map.get(self.message_priority_var.get(), 'NORMAL')
            
            # 메시지 생성
            try:
                from .message_template_engine import MessageType, MessagePriority
                message_type_enum = getattr(MessageType, message_type_str)
                priority_enum = getattr(MessagePriority, priority_str)
                
                generated_message = self.message_engine.generate_message(
                    message_type_enum, 
                    message_data, 
                    priority_enum
                )
                
                # 미리보기 텍스트 업데이트
                self.message_preview_text.delete(1.0, tk.END)
                
                # 메시지 헤더 정보
                header = f"📋 메시지 타입: {self.message_type_var.get()}\n"
                header += f"⚡ 우선순위: {self.message_priority_var.get()}\n"
                header += f"🕒 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                header += "=" * 60 + "\n\n"
                
                self.message_preview_text.insert(tk.END, header)
                
                # 생성된 메시지 내용
                if isinstance(generated_message, dict):
                    # JSON 형태로 표시
                    import json
                    formatted_message = json.dumps(generated_message, ensure_ascii=False, indent=2)
                    self.message_preview_text.insert(tk.END, formatted_message)
                else:
                    # 텍스트 형태로 표시
                    self.message_preview_text.insert(tk.END, str(generated_message))
                
                self.log_to_deploy("✅ 메시지 미리보기 업데이트 완료")
                
            except Exception as e:
                error_msg = f"메시지 생성 오류: {str(e)}"
                self.message_preview_text.delete(1.0, tk.END)
                self.message_preview_text.insert(tk.END, f"❌ {error_msg}")
                self.log_to_deploy(f"❌ {error_msg}")
                
        except Exception as e:
            error_msg = f"미리보기 업데이트 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            if hasattr(self, 'message_preview_text'):
                self.message_preview_text.delete(1.0, tk.END)
                self.message_preview_text.insert(tk.END, f"❌ {error_msg}")
    
    def load_sample_message_data(self):
        """샘플 메시지 데이터 로드"""
        try:
            # 메시지 타입별 샘플 데이터
            sample_data_map = {
                'deployment_success': {
                    'kospi': '2,485.67',
                    'exchange_rate': '1,315.20',
                    'posco_stock': '287,500',
                    'deployment_status': '성공',
                    'deployment_time': '42'
                },
                'deployment_failure': {
                    'kospi': '2,445.32',
                    'exchange_rate': '1,325.80',
                    'posco_stock': '283,000',
                    'deployment_status': '실패',
                    'deployment_time': '15'
                },
                'data_update': {
                    'kospi': '2,467.89',
                    'exchange_rate': '1,318.45',
                    'posco_stock': '285,500',
                    'deployment_status': '진행중',
                    'deployment_time': '28'
                }
            }
            
            current_type = self.message_type_var.get()
            sample_data = sample_data_map.get(current_type, sample_data_map['deployment_success'])
            
            # 입력 필드에 샘플 데이터 설정
            self.kospi_preview_var.set(sample_data['kospi'])
            self.exchange_preview_var.set(sample_data['exchange_rate'])
            self.posco_stock_preview_var.set(sample_data['posco_stock'])
            self.deployment_status_var.set(sample_data['deployment_status'])
            self.deployment_time_var.set(sample_data['deployment_time'])
            
            # 미리보기 업데이트
            self.update_message_preview()
            
            self.log_to_deploy(f"✅ {current_type} 타입 샘플 데이터 로드 완료")
            
        except Exception as e:
            error_msg = f"샘플 데이터 로드 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)
    
    def save_message_data(self):
        """현재 메시지 데이터 저장"""
        try:
            # 현재 데이터 수집
            current_data = {
                'message_type': self.message_type_var.get(),
                'priority': self.message_priority_var.get(),
                'kospi': self.kospi_preview_var.get(),
                'exchange_rate': self.exchange_preview_var.get(),
                'posco_stock': self.posco_stock_preview_var.get(),
                'deployment_status': self.deployment_status_var.get(),
                'deployment_time': self.deployment_time_var.get(),
                'webhook_url': self.webhook_url_var.get(),
                'saved_at': datetime.now().isoformat()
            }
            
            # 데이터 디렉토리에 저장
            data_file = os.path.join(self.data_dir, 'saved_message_data.json')
            
            # 기존 데이터 로드 (있다면)
            saved_data_list = []
            if os.path.exists(data_file):
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        saved_data_list = json.load(f)
                except:
                    saved_data_list = []
            
            # 새 데이터 추가
            saved_data_list.append(current_data)
            
            # 최근 10개만 유지
            if len(saved_data_list) > 10:
                saved_data_list = saved_data_list[-10:]
            
            # 파일에 저장
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(saved_data_list, f, ensure_ascii=False, indent=2)
            
            self.log_to_deploy(f"✅ 메시지 데이터 저장 완료: {data_file}")
            messagebox.showinfo("저장 완료", "메시지 데이터가 성공적으로 저장되었습니다.")
            
        except Exception as e:
            error_msg = f"메시지 데이터 저장 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("저장 오류", error_msg)
    
    def paste_webhook_url(self):
        """클립보드에서 웹훅 URL 붙여넣기"""
        try:
            # 클립보드에서 텍스트 가져오기
            clipboard_text = self.parent_frame.clipboard_get()
            
            # URL 형식 간단 검증
            if clipboard_text.startswith(('http://', 'https://')):
                self.webhook_url_var.set(clipboard_text)
                self.log_to_deploy("✅ 클립보드에서 웹훅 URL 붙여넣기 완료")
            else:
                messagebox.showwarning("경고", "클립보드의 내용이 유효한 URL 형식이 아닙니다.")
                
        except Exception as e:
            error_msg = f"클립보드 붙여넣기 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)
    
    def send_test_message(self):
        """테스트 메시지 전송 (Requirements 6.4)"""
        try:
            webhook_url = self.webhook_url_var.get().strip()
            if not webhook_url or not webhook_url.startswith(('http://', 'https://')):
                messagebox.showwarning("경고", "유효한 웹훅 URL을 입력하세요.")
                return
            
            self.send_status_var.set("🧪 테스트 전송 중...")
            self.send_test_button.config(state=tk.DISABLED)
            
            # 백그라운드에서 테스트 전송
            def send_test():
                try:
                    # 간단한 테스트 메시지 생성
                    test_message = {
                        "text": "🧪 POSCO GUI 테스트 메시지",
                        "attachments": [{
                            "color": "good",
                            "title": "테스트 전송",
                            "text": f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                            "footer": "POSCO WatchHamster GUI"
                        }]
                    }
                    
                    # HTTP 요청 전송
                    import requests
                    response = requests.post(webhook_url, json=test_message, timeout=10)
                    
                    # 결과 처리 (메인 스레드에서)
                    if response.status_code == 200:
                        self.parent_frame.after(0, self._handle_test_send_success)
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        self.parent_frame.after(0, self._handle_test_send_error, error_msg)
                        
                except Exception as e:
                    error_msg = str(e)
                    self.parent_frame.after(0, self._handle_test_send_error, error_msg)
            
            # 백그라운드 스레드에서 실행
            threading.Thread(target=send_test, daemon=True).start()
            
        except Exception as e:
            self.send_status_var.set("❌ 테스트 전송 오류")
            self.send_test_button.config(state=tk.NORMAL)
            error_msg = f"테스트 전송 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)
    
    def _handle_test_send_success(self):
        """테스트 전송 성공 처리 (메인 스레드)"""
        self.send_status_var.set("✅ 테스트 전송 성공")
        self.send_test_button.config(state=tk.NORMAL)
        self.log_to_deploy("✅ 테스트 메시지 전송 성공")
        messagebox.showinfo("전송 성공", "테스트 메시지가 성공적으로 전송되었습니다.")
    
    def _handle_test_send_error(self, error_msg):
        """테스트 전송 실패 처리 (메인 스레드)"""
        self.send_status_var.set("❌ 테스트 전송 실패")
        self.send_test_button.config(state=tk.NORMAL)
        self.log_to_deploy(f"❌ 테스트 메시지 전송 실패: {error_msg}")
        messagebox.showerror("전송 실패", f"테스트 메시지 전송에 실패했습니다.\n\n오류: {error_msg}")
    
    def send_manual_message(self):
        """수동 메시지 전송 (Requirements 6.4)"""
        try:
            webhook_url = self.webhook_url_var.get().strip()
            if not webhook_url or not webhook_url.startswith(('http://', 'https://')):
                messagebox.showwarning("경고", "유효한 웹훅 URL을 입력하세요.")
                return
            
            # 전송 확인
            confirm = messagebox.askyesno(
                "전송 확인", 
                f"현재 미리보기의 메시지를 전송하시겠습니까?\n\n타입: {self.message_type_var.get()}\n우선순위: {self.message_priority_var.get()}"
            )
            
            if not confirm:
                return
            
            self.send_status_var.set("📤 수동 전송 중...")
            self.send_manual_button.config(state=tk.DISABLED)
            
            # 백그라운드에서 메시지 전송
            def send_manual():
                try:
                    # 현재 미리보기 메시지 데이터 수집
                    message_data = {
                        'kospi': self.kospi_preview_var.get(),
                        'exchange_rate': self.exchange_preview_var.get(),
                        'posco_stock': self.posco_stock_preview_var.get(),
                        'deployment_status': self.deployment_status_var.get(),
                        'deployment_time': self.deployment_time_var.get(),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'deployment_url': 'https://username.github.io/repository'
                    }
                    
                    # 메시지 템플릿 엔진으로 메시지 생성
                    if hasattr(self, 'message_engine'):
                        try:
                            from .message_template_engine import MessageType, MessagePriority
                            
                            # 메시지 타입 변환
                            message_type_map = {
                                'deployment_success': MessageType.DEPLOYMENT_SUCCESS,
                                'deployment_failure': MessageType.DEPLOYMENT_FAILURE,
                                'deployment_start': MessageType.DEPLOYMENT_START,
                                'system_status': MessageType.SYSTEM_STATUS,
                                'data_update': MessageType.DATA_UPDATE,
                                'error_alert': MessageType.ERROR_ALERT
                            }
                            
                            priority_map = {
                                'low': MessagePriority.LOW,
                                'normal': MessagePriority.NORMAL,
                                'high': MessagePriority.HIGH,
                                'critical': MessagePriority.CRITICAL
                            }
                            
                            message_type = message_type_map.get(self.message_type_var.get(), MessageType.DEPLOYMENT_SUCCESS)
                            priority = priority_map.get(self.message_priority_var.get(), MessagePriority.NORMAL)
                            
                            generated_message = self.message_engine.generate_message(message_type, message_data, priority)
                            
                        except Exception as e:
                            # 템플릿 엔진 실패 시 기본 메시지 생성
                            generated_message = {
                                "text": f"🏭 POSCO 시스템 알림 - {self.message_type_var.get()}",
                                "attachments": [{
                                    "color": "good" if self.deployment_status_var.get() == "성공" else "danger",
                                    "title": f"배포 상태: {self.deployment_status_var.get()}",
                                    "fields": [
                                        {"title": "KOSPI", "value": self.kospi_preview_var.get(), "short": True},
                                        {"title": "환율", "value": self.exchange_preview_var.get(), "short": True},
                                        {"title": "POSCO 주가", "value": self.posco_stock_preview_var.get(), "short": True},
                                        {"title": "배포 시간", "value": f"{self.deployment_time_var.get()}초", "short": True}
                                    ],
                                    "footer": "POSCO WatchHamster GUI",
                                    "ts": int(datetime.now().timestamp())
                                }]
                            }
                    else:
                        # 기본 메시지 생성
                        generated_message = {
                            "text": f"🏭 POSCO 시스템 알림 - {self.message_type_var.get()}",
                            "attachments": [{
                                "color": "good" if self.deployment_status_var.get() == "성공" else "danger",
                                "title": f"배포 상태: {self.deployment_status_var.get()}",
                                "text": f"배포 시간: {self.deployment_time_var.get()}초\nKOSPI: {self.kospi_preview_var.get()}\n환율: {self.exchange_preview_var.get()}\nPOSCO: {self.posco_stock_preview_var.get()}",
                                "footer": "POSCO WatchHamster GUI"
                            }]
                        }
                    
                    # HTTP 요청 전송
                    import requests
                    response = requests.post(webhook_url, json=generated_message, timeout=15)
                    
                    # 결과 처리 (메인 스레드에서)
                    if response.status_code == 200:
                        self.parent_frame.after(0, self._handle_manual_send_success, message_data)
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        self.parent_frame.after(0, self._handle_manual_send_error, error_msg)
                        
                except Exception as e:
                    error_msg = str(e)
                    self.parent_frame.after(0, self._handle_manual_send_error, error_msg)
            
            # 백그라운드 스레드에서 실행
            threading.Thread(target=send_manual, daemon=True).start()
            
        except Exception as e:
            self.send_status_var.set("❌ 수동 전송 오류")
            self.send_manual_button.config(state=tk.NORMAL)
            error_msg = f"수동 전송 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)
    
    def _handle_manual_send_success(self, message_data):
        """수동 전송 성공 처리 (메인 스레드)"""
        self.send_status_var.set("✅ 수동 전송 성공")
        self.send_manual_button.config(state=tk.NORMAL)
        
        # 전송 히스토리에 기록
        self._save_send_history(message_data, True)
        
        self.log_to_deploy("✅ 수동 메시지 전송 성공")
        messagebox.showinfo("전송 성공", "메시지가 성공적으로 전송되었습니다.")
    
    def _handle_manual_send_error(self, error_msg):
        """수동 전송 실패 처리 (메인 스레드)"""
        self.send_status_var.set("❌ 수동 전송 실패")
        self.send_manual_button.config(state=tk.NORMAL)
        
        # 전송 히스토리에 실패 기록
        self._save_send_history({}, False, error_msg)
        
        self.log_to_deploy(f"❌ 수동 메시지 전송 실패: {error_msg}")
        messagebox.showerror("전송 실패", f"메시지 전송에 실패했습니다.\n\n오류: {error_msg}")
    
    def _save_send_history(self, message_data, success, error_msg=None):
        """전송 히스토리 저장"""
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'message_type': self.message_type_var.get(),
                'priority': self.message_priority_var.get(),
                'success': success,
                'error_message': error_msg,
                'message_data': message_data,
                'webhook_url': self.webhook_url_var.get()[:50] + "..." if len(self.webhook_url_var.get()) > 50 else self.webhook_url_var.get()
            }
            
            # 히스토리 파일 경로
            history_file = os.path.join(self.data_dir, 'send_history.json')
            
            # 기존 히스토리 로드
            history_list = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_list = json.load(f)
                except:
                    history_list = []
            
            # 새 항목 추가
            history_list.append(history_entry)
            
            # 최근 50개만 유지
            if len(history_list) > 50:
                history_list = history_list[-50:]
            
            # 파일에 저장
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_list, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.log_to_deploy(f"❌ 전송 히스토리 저장 오류: {str(e)}")
    
    def show_send_history(self):
        """전송 히스토리 표시"""
        try:
            # 히스토리 파일 로드
            history_file = os.path.join(self.data_dir, 'send_history.json')
            history_list = []
            
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_list = json.load(f)
                except:
                    history_list = []
            
            # 히스토리 창 생성
            history_window = tk.Toplevel(self.parent_frame)
            history_window.title("📊 메시지 전송 히스토리")
            history_window.geometry("800x600")
            history_window.transient(self.parent_frame)
            
            # 메인 프레임
            main_frame = ttk.Frame(history_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 제목
            ttk.Label(main_frame, text="📊 메시지 전송 히스토리", 
                     font=("TkDefaultFont", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
            
            # 트리뷰로 히스토리 표시
            columns = ('시간', '타입', '우선순위', '상태', '오류')
            tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
            
            for col in columns:
                tree.heading(col, text=col)
                if col == '시간':
                    tree.column(col, width=150)
                elif col == '오류':
                    tree.column(col, width=200)
                else:
                    tree.column(col, width=100)
            
            # 스크롤바
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 히스토리 데이터 추가 (최신 순)
            for entry in reversed(history_list):
                timestamp = entry.get('timestamp', '')
                if 'T' in timestamp:
                    timestamp = timestamp.split('T')[0] + ' ' + timestamp.split('T')[1][:8]
                
                status = "✅ 성공" if entry.get('success', False) else "❌ 실패"
                error_msg = entry.get('error_message', '')[:50] + "..." if len(entry.get('error_message', '')) > 50 else entry.get('error_message', '')
                
                tree.insert('', tk.END, values=(
                    timestamp,
                    entry.get('message_type', ''),
                    entry.get('priority', ''),
                    status,
                    error_msg
                ))
            
            # 하단 버튼
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(button_frame, text="🔄 새로고침", 
                      command=lambda: self.show_send_history()).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="🗑️ 히스토리 삭제", 
                      command=lambda: self._clear_send_history(history_window)).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="닫기", 
                      command=history_window.destroy).pack(side=tk.RIGHT)
            
            # 창을 중앙에 배치
            history_window.update_idletasks()
            x = (history_window.winfo_screenwidth() // 2) - (history_window.winfo_width() // 2)
            y = (history_window.winfo_screenheight() // 2) - (history_window.winfo_height() // 2)
            history_window.geometry(f"+{x}+{y}")
            
            self.log_to_deploy(f"📊 전송 히스토리 표시: {len(history_list)}개 항목")
            
        except Exception as e:
            error_msg = f"전송 히스토리 표시 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)
    
    def _clear_send_history(self, history_window):
        """전송 히스토리 삭제"""
        try:
            confirm = messagebox.askyesno("확인", "전송 히스토리를 모두 삭제하시겠습니까?")
            if not confirm:
                return
            
            history_file = os.path.join(self.data_dir, 'send_history.json')
            if os.path.exists(history_file):
                os.remove(history_file)
            
            self.log_to_deploy("🗑️ 전송 히스토리 삭제 완료")
            messagebox.showinfo("삭제 완료", "전송 히스토리가 삭제되었습니다.")
            
            # 히스토리 창 닫기
            history_window.destroy()
            
        except Exception as e:
            error_msg = f"히스토리 삭제 오류: {str(e)}"
            self.log_to_deploy(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)