#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 상태 대시보드 GUI 컴포넌트
실시간 시스템 상태 표시 및 배포 통계 시각화

주요 기능:
- 📊 실시간 시스템 상태 대시보드
- 📈 배포 성공/실패 통계 시각화
- 🚨 시스템 알림 및 복구 옵션 제공
- 🔄 자동 새로고침 및 수동 제어

Requirements: 5.1, 5.2 구현
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from core.integrated_status_reporter import IntegratedStatusReporter, SystemComponent, StatusAlert, DeploymentStatistics, SystemStatus, AlertLevel
    from core.performance_optimizer import get_performance_optimizer
except ImportError as e:
    print(f"통합 상태 보고 시스템 import 오류: {e}")

# 성능 최적화 시스템 전역 접근
try:
    performance_optimizer = get_performance_optimizer()
except:
    performance_optimizer = None


class StatusDashboard:
    """통합 상태 대시보드 GUI 클래스"""
    
    def __init__(self, parent_frame: tk.Widget, status_reporter: Optional[IntegratedStatusReporter] = None):
        """상태 대시보드 초기화"""
        self.parent_frame = parent_frame
        self.status_reporter = status_reporter
        
        # GUI 요소들
        self.main_frame = None
        self.status_frame = None
        self.stats_frame = None
        self.alerts_frame = None
        self.control_frame = None
        
        # 상태 표시 위젯들
        self.status_labels = {}
        self.status_indicators = {}
        self.stats_labels = {}
        self.alerts_tree = None
        
        # 업데이트 관련
        self.auto_refresh = True
        self.refresh_interval = 5000  # 5초
        self.refresh_job = None
        
        # 현재 데이터
        self.current_components = {}
        self.current_stats = None
        self.current_alerts = []
        
        # 성능 최적화 시스템 연결
        try:
            self.performance_optimizer = get_performance_optimizer()
            self.use_optimization = True
        except:
            self.performance_optimizer = None
            self.use_optimization = False
            print("⚠️ 상태 대시보드: 성능 최적화 없이 실행")
        
        # GUI 생성
        self.create_gui()
        
        # 상태 보고 시스템 연결
        if self.status_reporter:
            self.connect_status_reporter()
        
        # 초기 데이터 로드
        self.refresh_all_data()
        
        print("📊 통합 상태 대시보드 초기화 완료")
    
    def create_gui(self):
        """GUI 생성"""
        # 메인 프레임
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 제목
        title_label = ttk.Label(self.main_frame, 
                               text="📊 통합 시스템 상태 대시보드", 
                               font=("TkDefaultFont", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 노트북 (탭) 위젯
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 시스템 상태 탭
        self.create_status_tab(notebook)
        
        # 배포 통계 탭
        self.create_statistics_tab(notebook)
        
        # 알림 및 로그 탭
        self.create_alerts_tab(notebook)
        
        # 제어 패널 탭
        self.create_control_tab(notebook)
    
    def create_status_tab(self, notebook: ttk.Notebook):
        """시스템 상태 탭 생성"""
        self.status_frame = ttk.Frame(notebook)
        notebook.add(self.status_frame, text="시스템 상태")
        
        # 전체 상태 요약
        summary_frame = ttk.LabelFrame(self.status_frame, text="전체 상태 요약")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 전체 건강도 표시
        self.overall_health_label = ttk.Label(summary_frame, 
                                            text="전체 건강도: 확인 중...", 
                                            font=("TkDefaultFont", 10, "bold"))
        self.overall_health_label.pack(pady=5)
        
        # 상태 통계
        stats_frame = ttk.Frame(summary_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_stats_labels = {}
        status_names = ["healthy", "warning", "error", "critical", "offline"]
        status_colors = ["green", "orange", "red", "purple", "gray"]
        
        for i, (status, color) in enumerate(zip(status_names, status_colors)):
            label = ttk.Label(stats_frame, text=f"{status.title()}: 0")
            label.grid(row=0, column=i, padx=10, pady=2)
            self.status_stats_labels[status] = label
        
        # 컴포넌트별 상태
        components_frame = ttk.LabelFrame(self.status_frame, text="컴포넌트별 상태")
        components_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(components_frame)
        scrollbar = ttk.Scrollbar(components_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.components_frame = scrollable_frame
        
        # 마지막 업데이트 시간
        self.last_update_label = ttk.Label(self.status_frame, 
                                         text="마지막 업데이트: -", 
                                         font=("TkDefaultFont", 8))
        self.last_update_label.pack(pady=5)
    
    def create_statistics_tab(self, notebook: ttk.Notebook):
        """배포 통계 탭 생성"""
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text="배포 통계")
        
        # 배포 요약 통계
        summary_stats_frame = ttk.LabelFrame(self.stats_frame, text="배포 요약")
        summary_stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 통계 라벨들
        stats_grid = ttk.Frame(summary_stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # 첫 번째 행
        ttk.Label(stats_grid, text="총 배포:").grid(row=0, column=0, sticky="w", padx=5)
        self.total_deployments_label = ttk.Label(stats_grid, text="0", font=("TkDefaultFont", 10, "bold"))
        self.total_deployments_label.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="성공:").grid(row=0, column=2, sticky="w", padx=5)
        self.successful_deployments_label = ttk.Label(stats_grid, text="0", foreground="green", font=("TkDefaultFont", 10, "bold"))
        self.successful_deployments_label.grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="실패:").grid(row=0, column=4, sticky="w", padx=5)
        self.failed_deployments_label = ttk.Label(stats_grid, text="0", foreground="red", font=("TkDefaultFont", 10, "bold"))
        self.failed_deployments_label.grid(row=0, column=5, sticky="w", padx=5)
        
        # 두 번째 행
        ttk.Label(stats_grid, text="성공률:").grid(row=1, column=0, sticky="w", padx=5)
        self.success_rate_label = ttk.Label(stats_grid, text="0%", font=("TkDefaultFont", 10, "bold"))
        self.success_rate_label.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="평균 소요시간:").grid(row=1, column=2, sticky="w", padx=5)
        self.average_duration_label = ttk.Label(stats_grid, text="0초", font=("TkDefaultFont", 10, "bold"))
        self.average_duration_label.grid(row=1, column=3, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="마지막 배포:").grid(row=1, column=4, sticky="w", padx=5)
        self.last_deployment_label = ttk.Label(stats_grid, text="-", font=("TkDefaultFont", 10, "bold"))
        self.last_deployment_label.grid(row=1, column=5, sticky="w", padx=5)
        
        # 성공률 프로그레스 바
        progress_frame = ttk.Frame(summary_stats_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(progress_frame, text="성공률:").pack(side=tk.LEFT)
        self.success_rate_progress = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.success_rate_progress.pack(side=tk.LEFT, padx=10)
        
        # 최근 배포 목록
        recent_frame = ttk.LabelFrame(self.stats_frame, text="최근 배포 (최근 10개)")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 트리뷰 생성
        columns = ("시간", "세션ID", "상태", "소요시간", "단계")
        self.deployments_tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=8)
        
        # 컬럼 설정
        self.deployments_tree.heading("시간", text="시간")
        self.deployments_tree.heading("세션ID", text="세션 ID")
        self.deployments_tree.heading("상태", text="상태")
        self.deployments_tree.heading("소요시간", text="소요시간")
        self.deployments_tree.heading("단계", text="완료 단계")
        
        self.deployments_tree.column("시간", width=120)
        self.deployments_tree.column("세션ID", width=150)
        self.deployments_tree.column("상태", width=80)
        self.deployments_tree.column("소요시간", width=100)
        self.deployments_tree.column("단계", width=100)
        
        # 스크롤바
        deployments_scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.deployments_tree.yview)
        self.deployments_tree.configure(yscrollcommand=deployments_scrollbar.set)
        
        self.deployments_tree.pack(side="left", fill="both", expand=True)
        deployments_scrollbar.pack(side="right", fill="y")
    
    def create_alerts_tab(self, notebook: ttk.Notebook):
        """알림 및 로그 탭 생성"""
        self.alerts_frame = ttk.Frame(notebook)
        notebook.add(self.alerts_frame, text="알림 및 로그")
        
        # 알림 필터
        filter_frame = ttk.Frame(self.alerts_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="필터:").pack(side=tk.LEFT)
        
        self.alert_filter_var = tk.StringVar(value="all")
        filter_options = [("전체", "all"), ("오류", "error"), ("경고", "warning"), ("정보", "info")]
        
        for text, value in filter_options:
            ttk.Radiobutton(filter_frame, text=text, variable=self.alert_filter_var, 
                          value=value, command=self.filter_alerts).pack(side=tk.LEFT, padx=5)
        
        # 알림 목록
        alerts_list_frame = ttk.LabelFrame(self.alerts_frame, text="시스템 알림")
        alerts_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 트리뷰 생성
        alert_columns = ("시간", "컴포넌트", "레벨", "메시지", "복구")
        self.alerts_tree = ttk.Treeview(alerts_list_frame, columns=alert_columns, show="headings", height=12)
        
        # 컬럼 설정
        self.alerts_tree.heading("시간", text="시간")
        self.alerts_tree.heading("컴포넌트", text="컴포넌트")
        self.alerts_tree.heading("레벨", text="레벨")
        self.alerts_tree.heading("메시지", text="메시지")
        self.alerts_tree.heading("복구", text="자동복구")
        
        self.alerts_tree.column("시간", width=120)
        self.alerts_tree.column("컴포넌트", width=120)
        self.alerts_tree.column("레벨", width=80)
        self.alerts_tree.column("메시지", width=300)
        self.alerts_tree.column("복구", width=80)
        
        # 스크롤바
        alerts_scrollbar = ttk.Scrollbar(alerts_list_frame, orient="vertical", command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=alerts_scrollbar.set)
        
        self.alerts_tree.pack(side="left", fill="both", expand=True)
        alerts_scrollbar.pack(side="right", fill="y")
        
        # 더블클릭 이벤트
        self.alerts_tree.bind("<Double-1>", self.on_alert_double_click)
        
        # 알림 제어 버튼
        alert_control_frame = ttk.Frame(self.alerts_frame)
        alert_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(alert_control_frame, text="알림 새로고침", command=self.refresh_alerts).pack(side=tk.LEFT, padx=5)
        ttk.Button(alert_control_frame, text="알림 지우기", command=self.clear_alerts).pack(side=tk.LEFT, padx=5)
        ttk.Button(alert_control_frame, text="보고서 내보내기", command=self.export_report).pack(side=tk.LEFT, padx=5)
    
    def create_control_tab(self, notebook: ttk.Notebook):
        """제어 패널 탭 생성"""
        self.control_frame = ttk.Frame(notebook)
        notebook.add(self.control_frame, text="제어 패널")
        
        # 모니터링 제어
        monitoring_frame = ttk.LabelFrame(self.control_frame, text="모니터링 제어")
        monitoring_frame.pack(fill=tk.X, padx=5, pady=5)
        
        control_buttons_frame = ttk.Frame(monitoring_frame)
        control_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_buttons_frame, text="모니터링 시작", command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_buttons_frame, text="모니터링 중지", command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_buttons_frame, text="즉시 새로고침", command=self.refresh_all_data).pack(side=tk.LEFT, padx=5)
        
        # 자동 새로고침 설정
        auto_refresh_frame = ttk.Frame(monitoring_frame)
        auto_refresh_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=self.auto_refresh)
        ttk.Checkbutton(auto_refresh_frame, text="자동 새로고침", 
                       variable=self.auto_refresh_var, 
                       command=self.toggle_auto_refresh).pack(side=tk.LEFT)
        
        ttk.Label(auto_refresh_frame, text="간격(초):").pack(side=tk.LEFT, padx=(20, 5))
        self.refresh_interval_var = tk.StringVar(value=str(self.refresh_interval // 1000))
        interval_spinbox = ttk.Spinbox(auto_refresh_frame, from_=1, to=60, width=5, 
                                     textvariable=self.refresh_interval_var,
                                     command=self.update_refresh_interval)
        interval_spinbox.pack(side=tk.LEFT)
        
        # 시스템 복구 제어
        recovery_frame = ttk.LabelFrame(self.control_frame, text="시스템 복구")
        recovery_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 컴포넌트 선택
        component_frame = ttk.Frame(recovery_frame)
        component_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(component_frame, text="컴포넌트:").pack(side=tk.LEFT)
        self.recovery_component_var = tk.StringVar()
        self.recovery_component_combo = ttk.Combobox(component_frame, textvariable=self.recovery_component_var, 
                                                   state="readonly", width=20)
        self.recovery_component_combo.pack(side=tk.LEFT, padx=5)
        self.recovery_component_combo.bind("<<ComboboxSelected>>", self.on_component_selected)
        
        # 복구 액션 선택
        action_frame = ttk.Frame(recovery_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(action_frame, text="복구 액션:").pack(side=tk.LEFT)
        self.recovery_action_var = tk.StringVar()
        self.recovery_action_combo = ttk.Combobox(action_frame, textvariable=self.recovery_action_var, 
                                                state="readonly", width=20)
        self.recovery_action_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="복구 실행", command=self.execute_recovery).pack(side=tk.LEFT, padx=10)
        
        # 상태 정보
        info_frame = ttk.LabelFrame(self.control_frame, text="시스템 정보")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")
    
    def connect_status_reporter(self):
        """상태 보고 시스템 연결"""
        if not self.status_reporter:
            return
        
        # 콜백 등록
        self.status_reporter.register_status_callback(self.on_status_update)
        self.status_reporter.register_alert_callback(self.on_alert_received)
        self.status_reporter.register_statistics_callback(self.on_statistics_update)
        self.status_reporter.register_recovery_callback(self.on_recovery_request)
        
        print("📡 상태 보고 시스템 콜백 등록 완료")
    
    def on_status_update(self, components: Dict[str, SystemComponent]):
        """상태 업데이트 콜백 (성능 최적화 적용)"""
        self.current_components = components
        
        # 성능 최적화: UI 업데이트 스케줄링
        if self.use_optimization:
            self.performance_optimizer.schedule_ui_update(self.update_status_display)
        else:
            # GUI 업데이트는 메인 스레드에서 실행
            self.parent_frame.after(0, self.update_status_display)
    
    def on_alert_received(self, alert: StatusAlert):
        """알림 수신 콜백 (성능 최적화 적용)"""
        self.current_alerts.insert(0, alert)  # 최신 알림을 맨 앞에
        
        # 최근 100개 알림만 유지
        if len(self.current_alerts) > 100:
            self.current_alerts = self.current_alerts[:100]
        
        # 성능 최적화: UI 업데이트 스케줄링
        if self.use_optimization:
            self.performance_optimizer.schedule_ui_update(self.update_alerts_display)
        else:
            self.parent_frame.after(0, self.update_alerts_display)
        
        # 중요한 알림은 팝업으로 표시
        if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            if self.use_optimization:
                self.performance_optimizer.schedule_ui_update(lambda: self.show_alert_popup(alert))
            else:
                self.parent_frame.after(0, lambda: self.show_alert_popup(alert))
    
    def on_statistics_update(self, stats: DeploymentStatistics):
        """통계 업데이트 콜백 (성능 최적화 적용)"""
        self.current_stats = stats
        
        # 성능 최적화: UI 업데이트 스케줄링
        if self.use_optimization:
            self.performance_optimizer.schedule_ui_update(self.update_statistics_display)
        else:
            self.parent_frame.after(0, self.update_statistics_display)
    
    def on_recovery_request(self, component: str, action: str) -> bool:
        """복구 요청 콜백"""
        # 실제 복구 로직은 여기서 구현하거나 다른 시스템에 위임
        print(f"🔧 복구 요청: {component} - {action}")
        
        # 테스트용으로 항상 성공 반환
        return True
    
    def update_status_display(self):
        """상태 표시 업데이트"""
        try:
            if not self.current_components:
                return
            
            # 전체 건강도 계산
            total_components = len(self.current_components)
            healthy_count = sum(1 for c in self.current_components.values() if c.status == SystemStatus.HEALTHY)
            
            if total_components == 0:
                health_text = "시스템 상태: 알 수 없음"
                health_color = "gray"
            elif healthy_count == total_components:
                health_text = "시스템 상태: 우수 ✅"
                health_color = "green"
            elif healthy_count >= total_components * 0.8:
                health_text = "시스템 상태: 양호 ✅"
                health_color = "green"
            elif healthy_count >= total_components * 0.6:
                health_text = "시스템 상태: 보통 ⚠️"
                health_color = "orange"
            else:
                health_text = "시스템 상태: 주의 필요 ❌"
                health_color = "red"
            
            self.overall_health_label.config(text=health_text, foreground=health_color)
            
            # 상태별 통계 업데이트
            status_counts = {}
            for status in SystemStatus:
                status_counts[status.value] = 0
            
            for component in self.current_components.values():
                status_counts[component.status.value] += 1
            
            for status_name, label in self.status_stats_labels.items():
                count = status_counts.get(status_name, 0)
                label.config(text=f"{status_name.title()}: {count}")
            
            # 컴포넌트별 상태 표시 업데이트
            self.update_components_display()
            
            # 복구 제어 콤보박스 업데이트
            self.update_recovery_controls()
            
            # 마지막 업데이트 시간
            self.last_update_label.config(text=f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ 상태 표시 업데이트 오류: {e}")
    
    def update_components_display(self):
        """컴포넌트별 상태 표시 업데이트"""
        try:
            # 기존 위젯들 제거
            for widget in self.components_frame.winfo_children():
                widget.destroy()
            
            # 컴포넌트별 상태 표시
            for i, (comp_name, component) in enumerate(self.current_components.items()):
                comp_frame = ttk.Frame(self.components_frame)
                comp_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # 상태 아이콘
                status_icon = self.get_status_icon(component.status)
                status_color = self.get_status_color(component.status)
                
                # 컴포넌트 이름과 상태
                name_label = ttk.Label(comp_frame, text=f"{status_icon} {component.name}", 
                                     font=("TkDefaultFont", 9, "bold"))
                name_label.pack(side=tk.LEFT)
                
                status_label = ttk.Label(comp_frame, text=component.status.value.upper(), 
                                       foreground=status_color, font=("TkDefaultFont", 8))
                status_label.pack(side=tk.LEFT, padx=(10, 0))
                
                # 마지막 업데이트 시간
                time_str = component.last_updated.strftime('%H:%M:%S')
                time_label = ttk.Label(comp_frame, text=f"({time_str})", 
                                     font=("TkDefaultFont", 8), foreground="gray")
                time_label.pack(side=tk.RIGHT)
                
                # 오류 메시지 (있는 경우)
                if component.error_message:
                    error_frame = ttk.Frame(self.components_frame)
                    error_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
                    
                    error_label = ttk.Label(error_frame, text=f"⚠️ {component.error_message}", 
                                          foreground="red", font=("TkDefaultFont", 8))
                    error_label.pack(side=tk.LEFT)
                
                # 구분선
                if i < len(self.current_components) - 1:
                    separator = ttk.Separator(self.components_frame, orient='horizontal')
                    separator.pack(fill=tk.X, padx=5, pady=2)
            
        except Exception as e:
            print(f"❌ 컴포넌트 표시 업데이트 오류: {e}")
    
    def update_statistics_display(self):
        """통계 표시 업데이트"""
        try:
            if not self.current_stats:
                return
            
            # 기본 통계 업데이트
            self.total_deployments_label.config(text=str(self.current_stats.total_deployments))
            self.successful_deployments_label.config(text=str(self.current_stats.successful_deployments))
            self.failed_deployments_label.config(text=str(self.current_stats.failed_deployments))
            
            # 성공률 업데이트
            success_rate = self.current_stats.success_rate
            self.success_rate_label.config(text=f"{success_rate:.1f}%")
            self.success_rate_progress['value'] = success_rate
            
            # 성공률에 따른 색상 변경
            if success_rate >= 90:
                color = "green"
            elif success_rate >= 70:
                color = "orange"
            else:
                color = "red"
            self.success_rate_label.config(foreground=color)
            
            # 평균 소요시간
            avg_duration = self.current_stats.average_duration
            if avg_duration >= 3600:  # 1시간 이상
                duration_text = f"{avg_duration/3600:.1f}시간"
            elif avg_duration >= 60:  # 1분 이상
                duration_text = f"{avg_duration/60:.1f}분"
            else:
                duration_text = f"{avg_duration:.1f}초"
            
            self.average_duration_label.config(text=duration_text)
            
            # 마지막 배포 시간
            if self.current_stats.last_deployment:
                last_deploy_text = self.current_stats.last_deployment.strftime('%m/%d %H:%M')
            else:
                last_deploy_text = "-"
            self.last_deployment_label.config(text=last_deploy_text)
            
            # 최근 배포 목록 업데이트
            self.update_recent_deployments()
            
        except Exception as e:
            print(f"❌ 통계 표시 업데이트 오류: {e}")
    
    def update_recent_deployments(self):
        """최근 배포 목록 업데이트"""
        try:
            # 기존 항목들 제거
            for item in self.deployments_tree.get_children():
                self.deployments_tree.delete(item)
            
            if not self.current_stats or not self.current_stats.recent_deployments:
                return
            
            # 최근 배포들 추가
            for deployment in self.current_stats.recent_deployments:
                # 시간 포맷
                if deployment.get('start_time'):
                    deploy_time = datetime.fromtimestamp(deployment['start_time'])
                    time_str = deploy_time.strftime('%m/%d %H:%M')
                else:
                    time_str = "-"
                
                # 세션 ID (짧게)
                session_id = deployment.get('session_id', '-')
                if len(session_id) > 20:
                    session_id = session_id[:17] + "..."
                
                # 상태
                success = deployment.get('overall_success', False)
                status = "성공" if success else "실패"
                
                # 소요시간
                duration = deployment.get('total_duration', 0)
                if duration >= 60:
                    duration_str = f"{duration/60:.1f}분"
                else:
                    duration_str = f"{duration:.1f}초"
                
                # 완료 단계
                completed_phases = deployment.get('completed_phases', 0)
                total_phases = deployment.get('total_phases', 0)
                phases_str = f"{completed_phases}/{total_phases}"
                
                # 트리에 추가
                item_id = self.deployments_tree.insert("", "end", values=(
                    time_str, session_id, status, duration_str, phases_str
                ))
                
                # 실패한 배포는 빨간색으로 표시
                if not success:
                    self.deployments_tree.set(item_id, "상태", "❌ 실패")
                else:
                    self.deployments_tree.set(item_id, "상태", "✅ 성공")
            
        except Exception as e:
            print(f"❌ 최근 배포 목록 업데이트 오류: {e}")
    
    def update_alerts_display(self):
        """알림 표시 업데이트"""
        try:
            # 기존 항목들 제거
            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)
            
            # 필터링된 알림들 표시
            filtered_alerts = self.get_filtered_alerts()
            
            for alert in filtered_alerts:
                # 시간 포맷
                time_str = alert.timestamp.strftime('%m/%d %H:%M:%S')
                
                # 컴포넌트 이름 (짧게)
                component = self.current_components.get(alert.component, None)
                comp_name = component.name if component else alert.component
                if len(comp_name) > 15:
                    comp_name = comp_name[:12] + "..."
                
                # 레벨 아이콘
                level_icon = self.get_alert_level_icon(alert.level)
                level_text = f"{level_icon} {alert.level.value.upper()}"
                
                # 메시지 (짧게)
                message = alert.message
                if len(message) > 50:
                    message = message[:47] + "..."
                
                # 자동 복구 여부
                auto_recovery = "예" if alert.auto_recovery else "아니오"
                
                # 트리에 추가
                item_id = self.alerts_tree.insert("", "end", values=(
                    time_str, comp_name, level_text, message, auto_recovery
                ))
                
                # 레벨에 따른 색상 설정
                if alert.level == AlertLevel.CRITICAL:
                    self.alerts_tree.set(item_id, "레벨", "🚨 CRITICAL")
                elif alert.level == AlertLevel.ERROR:
                    self.alerts_tree.set(item_id, "레벨", "❌ ERROR")
                elif alert.level == AlertLevel.WARNING:
                    self.alerts_tree.set(item_id, "레벨", "⚠️ WARNING")
                else:
                    self.alerts_tree.set(item_id, "레벨", "ℹ️ INFO")
            
        except Exception as e:
            print(f"❌ 알림 표시 업데이트 오류: {e}")
    
    def update_recovery_controls(self):
        """복구 제어 콤보박스 업데이트"""
        try:
            # 컴포넌트 목록 업데이트
            component_names = []
            for comp_name, component in self.current_components.items():
                if component.recovery_actions:
                    component_names.append(component.name)
            
            self.recovery_component_combo['values'] = component_names
            
            # 현재 선택된 컴포넌트의 복구 액션 업데이트
            self.on_component_selected(None)
            
        except Exception as e:
            print(f"❌ 복구 제어 업데이트 오류: {e}")
    
    def get_filtered_alerts(self) -> List[StatusAlert]:
        """필터링된 알림 목록 반환"""
        filter_value = self.alert_filter_var.get()
        
        if filter_value == "all":
            return self.current_alerts
        else:
            return [alert for alert in self.current_alerts if alert.level.value == filter_value]
    
    def get_status_icon(self, status: SystemStatus) -> str:
        """상태 아이콘 반환"""
        icons = {
            SystemStatus.HEALTHY: "✅",
            SystemStatus.WARNING: "⚠️",
            SystemStatus.ERROR: "❌",
            SystemStatus.CRITICAL: "🚨",
            SystemStatus.OFFLINE: "⚫",
            SystemStatus.UNKNOWN: "❓"
        }
        return icons.get(status, "❓")
    
    def get_status_color(self, status: SystemStatus) -> str:
        """상태 색상 반환"""
        colors = {
            SystemStatus.HEALTHY: "green",
            SystemStatus.WARNING: "orange",
            SystemStatus.ERROR: "red",
            SystemStatus.CRITICAL: "purple",
            SystemStatus.OFFLINE: "gray",
            SystemStatus.UNKNOWN: "gray"
        }
        return colors.get(status, "gray")
    
    def get_alert_level_icon(self, level: AlertLevel) -> str:
        """알림 레벨 아이콘 반환"""
        icons = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        return icons.get(level, "ℹ️")
    
    def show_alert_popup(self, alert: StatusAlert):
        """중요한 알림 팝업 표시"""
        try:
            component = self.current_components.get(alert.component, None)
            comp_name = component.name if component else alert.component
            
            title = f"시스템 알림 - {comp_name}"
            message = f"레벨: {alert.level.value.upper()}\n\n{alert.message}"
            
            if alert.auto_recovery:
                message += f"\n\n자동 복구가 시도됩니다: {alert.recovery_action}"
            
            if alert.level == AlertLevel.CRITICAL:
                messagebox.showerror(title, message)
            elif alert.level == AlertLevel.ERROR:
                messagebox.showerror(title, message)
            else:
                messagebox.showwarning(title, message)
                
        except Exception as e:
            print(f"❌ 알림 팝업 표시 오류: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        try:
            if self.status_reporter:
                self.status_reporter.start_monitoring()
                messagebox.showinfo("모니터링 시작", "통합 상태 모니터링이 시작되었습니다.")
            else:
                messagebox.showwarning("오류", "상태 보고 시스템이 연결되지 않았습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"모니터링 시작 실패:\n{e}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        try:
            if self.status_reporter:
                self.status_reporter.stop_monitoring()
                messagebox.showinfo("모니터링 중지", "통합 상태 모니터링이 중지되었습니다.")
            else:
                messagebox.showwarning("오류", "상태 보고 시스템이 연결되지 않았습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"모니터링 중지 실패:\n{e}")
    
    def refresh_all_data(self):
        """모든 데이터 새로고침"""
        try:
            if self.status_reporter:
                # 상태 업데이트 강제 실행
                self.status_reporter.update_all_component_status()
                self.status_reporter.update_deployment_statistics()
                
                messagebox.showinfo("새로고침", "모든 데이터가 새로고침되었습니다.")
            else:
                messagebox.showwarning("오류", "상태 보고 시스템이 연결되지 않았습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"데이터 새로고침 실패:\n{e}")
    
    def toggle_auto_refresh(self):
        """자동 새로고침 토글"""
        self.auto_refresh = self.auto_refresh_var.get()
        
        if self.auto_refresh:
            self.schedule_refresh()
        else:
            if self.refresh_job:
                self.parent_frame.after_cancel(self.refresh_job)
                self.refresh_job = None
    
    def update_refresh_interval(self):
        """새로고침 간격 업데이트"""
        try:
            new_interval = int(self.refresh_interval_var.get()) * 1000
            self.refresh_interval = new_interval
            
            # 자동 새로고침이 활성화되어 있으면 다시 스케줄링
            if self.auto_refresh:
                if self.refresh_job:
                    self.parent_frame.after_cancel(self.refresh_job)
                self.schedule_refresh()
                
        except ValueError:
            pass  # 잘못된 값은 무시
    
    def schedule_refresh(self):
        """새로고침 스케줄링"""
        if self.auto_refresh:
            self.refresh_job = self.parent_frame.after(self.refresh_interval, self.auto_refresh_callback)
    
    def auto_refresh_callback(self):
        """자동 새로고침 콜백"""
        try:
            self.refresh_all_data()
        except Exception as e:
            print(f"❌ 자동 새로고침 오류: {e}")
        finally:
            # 다음 새로고침 스케줄링
            self.schedule_refresh()
    
    def on_component_selected(self, event):
        """컴포넌트 선택 이벤트"""
        try:
            selected_name = self.recovery_component_var.get()
            
            # 선택된 컴포넌트의 복구 액션 찾기
            recovery_actions = []
            for comp_name, component in self.current_components.items():
                if component.name == selected_name:
                    recovery_actions = component.recovery_actions
                    break
            
            self.recovery_action_combo['values'] = recovery_actions
            if recovery_actions:
                self.recovery_action_var.set(recovery_actions[0])
            else:
                self.recovery_action_var.set("")
                
        except Exception as e:
            print(f"❌ 컴포넌트 선택 처리 오류: {e}")
    
    def execute_recovery(self):
        """복구 실행"""
        try:
            component_name = self.recovery_component_var.get()
            recovery_action = self.recovery_action_var.get()
            
            if not component_name or not recovery_action:
                messagebox.showwarning("입력 오류", "컴포넌트와 복구 액션을 선택해주세요.")
                return
            
            # 컴포넌트 내부 이름 찾기
            internal_name = None
            for comp_name, component in self.current_components.items():
                if component.name == component_name:
                    internal_name = comp_name
                    break
            
            if not internal_name:
                messagebox.showerror("오류", "선택된 컴포넌트를 찾을 수 없습니다.")
                return
            
            # 확인 대화상자
            if not messagebox.askyesno("복구 확인", 
                                     f"{component_name}에 대해 '{recovery_action}' 복구를 실행하시겠습니까?"):
                return
            
            # 복구 실행
            if self.status_reporter:
                success = self.status_reporter.trigger_manual_recovery(internal_name, recovery_action)
                
                if success:
                    messagebox.showinfo("복구 성공", f"{component_name} 복구가 성공적으로 실행되었습니다.")
                else:
                    messagebox.showerror("복구 실패", f"{component_name} 복구 실행에 실패했습니다.")
            else:
                messagebox.showerror("오류", "상태 보고 시스템이 연결되지 않았습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"복구 실행 중 오류:\n{e}")
    
    def filter_alerts(self):
        """알림 필터링"""
        self.update_alerts_display()
    
    def refresh_alerts(self):
        """알림 새로고침"""
        try:
            if self.status_reporter:
                # 최근 알림 다시 로드
                recent_alerts = self.status_reporter.get_recent_alerts(50)
                self.current_alerts = [
                    StatusAlert(
                        component=alert['component'],
                        level=AlertLevel(alert['level']),
                        message=alert['message'],
                        timestamp=datetime.fromisoformat(alert['timestamp']),
                        details=alert['details'],
                        auto_recovery=alert['auto_recovery'],
                        recovery_action=alert['recovery_action']
                    )
                    for alert in recent_alerts
                ]
                
                self.update_alerts_display()
                messagebox.showinfo("새로고침", "알림 목록이 새로고침되었습니다.")
            else:
                messagebox.showwarning("오류", "상태 보고 시스템이 연결되지 않았습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"알림 새로고침 실패:\n{e}")
    
    def clear_alerts(self):
        """알림 지우기"""
        if messagebox.askyesno("알림 지우기", "모든 알림을 지우시겠습니까?"):
            self.current_alerts.clear()
            self.update_alerts_display()
            messagebox.showinfo("완료", "모든 알림이 지워졌습니다.")
    
    def export_report(self):
        """보고서 내보내기"""
        try:
            if self.status_reporter:
                report_path = self.status_reporter.export_status_report()
                messagebox.showinfo("보고서 내보내기", f"상태 보고서가 생성되었습니다:\n{report_path}")
            else:
                messagebox.showwarning("오류", "상태 보고 시스템이 연결되지 않았습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"보고서 내보내기 실패:\n{e}")
    
    def on_alert_double_click(self, event):
        """알림 더블클릭 이벤트"""
        try:
            selection = self.alerts_tree.selection()
            if not selection:
                return
            
            item = selection[0]
            values = self.alerts_tree.item(item, 'values')
            
            if len(values) >= 4:
                # 알림 상세 정보 표시
                detail_window = tk.Toplevel(self.parent_frame)
                detail_window.title("알림 상세 정보")
                detail_window.geometry("500x300")
                
                detail_text = tk.Text(detail_window, wrap=tk.WORD)
                detail_scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=detail_text.yview)
                detail_text.configure(yscrollcommand=detail_scrollbar.set)
                
                # 상세 정보 텍스트 구성
                detail_info = f"시간: {values[0]}\n"
                detail_info += f"컴포넌트: {values[1]}\n"
                detail_info += f"레벨: {values[2]}\n"
                detail_info += f"메시지: {values[3]}\n"
                detail_info += f"자동복구: {values[4]}\n"
                
                detail_text.insert(tk.END, detail_info)
                detail_text.config(state=tk.DISABLED)
                
                detail_text.pack(side="left", fill="both", expand=True)
                detail_scrollbar.pack(side="right", fill="y")
                
        except Exception as e:
            print(f"❌ 알림 상세 정보 표시 오류: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        try:
            if performance_optimizer:
                return performance_optimizer.get_performance_metrics()
            else:
                return {
                    'memory_usage_mb': 0,
                    'thread_count': 0,
                    'ui_updates_per_second': 0,
                    'background_tasks_completed': 0
                }
        except Exception as e:
            print(f"❌ 성능 메트릭 조회 오류: {e}")
            return {}
    
    def get_memory_usage_mb(self) -> float:
        """메모리 사용량 조회 (MB)"""
        try:
            metrics = self.get_performance_metrics()
            return metrics.get('memory_usage_mb', 0)
        except:
            return 0
    
    def get_thread_count(self) -> int:
        """스레드 수 조회"""
        try:
            metrics = self.get_performance_metrics()
            return metrics.get('thread_count', 0)
        except:
            return 0
    
    def destroy(self):
        """대시보드 정리"""
        try:
            # 자동 새로고침 중지
            if self.refresh_job:
                self.parent_frame.after_cancel(self.refresh_job)
            
            # 모니터링 중지
            if self.status_reporter:
                self.status_reporter.stop_monitoring()
            
            print("📊 통합 상태 대시보드 정리 완료")
            
        except Exception as e:
            print(f"❌ 대시보드 정리 오류: {e}")


# 편의 함수
def create_status_dashboard(parent_frame: tk.Widget, 
                          status_reporter: Optional[IntegratedStatusReporter] = None) -> StatusDashboard:
    """상태 대시보드 인스턴스 생성"""
    return StatusDashboard(parent_frame, status_reporter)


if __name__ == "__main__":
    # 테스트 코드
    print("🔧 통합 상태 대시보드 테스트")
    
    # 테스트용 GUI 생성
    root = tk.Tk()
    root.title("통합 상태 대시보드 테스트")
    root.geometry("1000x700")
    
    # 상태 보고 시스템 생성
    from core.integrated_status_reporter import create_integrated_status_reporter
    reporter = create_integrated_status_reporter()
    
    # 대시보드 생성
    dashboard = create_status_dashboard(root, reporter)
    
    # 모니터링 시작
    reporter.start_monitoring()
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n⚠️ 테스트 중단")
    finally:
        dashboard.destroy()
        print("✅ 통합 상태 대시보드 테스트 완료")