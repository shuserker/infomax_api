#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 상태 보고 시스템 (스탠드얼론)
모든 내장 시스템의 상태를 메인 GUI에 실시간 보고

주요 기능:
- 📊 모든 내장 시스템의 상태를 메인 GUI에 실시간 보고
- 📈 배포 성공/실패 통계를 대시보드에 시각화
- 🚨 시스템 오류 발생 시 즉시 알림 및 복구 옵션 제공
- 🔄 실시간 상태 업데이트 및 모니터링

Requirements: 5.1, 5.2 구현
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox
import logging


class SystemStatus(Enum):
    """시스템 상태"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class AlertLevel(Enum):
    """알림 레벨"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemComponent:
    """시스템 컴포넌트 정보"""
    name: str
    status: SystemStatus
    last_updated: datetime
    details: Dict[str, Any]
    error_message: Optional[str] = None
    recovery_actions: List[str] = None
    
    def __post_init__(self):
        if self.recovery_actions is None:
            self.recovery_actions = []


@dataclass
class StatusAlert:
    """상태 알림"""
    component: str
    level: AlertLevel
    message: str
    timestamp: datetime
    details: Dict[str, Any]
    auto_recovery: bool = False
    recovery_action: Optional[str] = None


@dataclass
class DeploymentStatistics:
    """배포 통계"""
    total_deployments: int
    successful_deployments: int
    failed_deployments: int
    average_duration: float
    success_rate: float
    last_deployment: Optional[datetime]
    recent_deployments: List[Dict[str, Any]]


class IntegratedStatusReporter:
    """통합 상태 보고 시스템 클래스"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """통합 상태 보고 시스템 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # logs 폴더 설정
        self.logs_dir = os.path.join(os.path.dirname(self.script_dir), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 로그 파일들
        self.status_log = os.path.join(self.logs_dir, "integrated_status.log")
        self.statistics_log = os.path.join(self.logs_dir, "deployment_statistics.json")
        self.alerts_log = os.path.join(self.logs_dir, "system_alerts.json")
        
        # 시스템 컴포넌트들
        self.components: Dict[str, SystemComponent] = {}
        self.alerts: List[StatusAlert] = []
        
        # 모니터링 상태
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_lock = threading.Lock()
        self.update_interval = 5  # 5초마다 업데이트
        
        # GUI 콜백 함수들
        self.status_callbacks: List[Callable[[Dict[str, SystemComponent]], None]] = []
        self.alert_callbacks: List[Callable[[StatusAlert], None]] = []
        self.statistics_callbacks: List[Callable[[DeploymentStatistics], None]] = []
        self.recovery_callbacks: List[Callable[[str, str], bool]] = []
        
        # 통계 데이터
        self.deployment_stats: Optional[DeploymentStatistics] = None
        
        # 로깅 설정
        self.setup_logging()
        
        # 시스템 컴포넌트 초기화
        self.initialize_components()
        
        self.log_message("🔧 통합 상태 보고 시스템 초기화 완료 (스탠드얼론)")
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.status_log, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IntegratedStatusReporter')
    
    def log_message(self, message: str, level: str = "INFO"):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        try:
            with open(self.status_log, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"❌ 로그 파일 쓰기 실패: {e}")
    
    def initialize_components(self):
        """시스템 컴포넌트 초기화"""
        # 기본 컴포넌트들 등록
        component_configs = [
            {
                "name": "deployment_monitor",
                "display_name": "배포 모니터링",
                "recovery_actions": ["restart_monitoring", "clear_session"]
            },
            {
                "name": "github_pages_monitor",
                "display_name": "GitHub Pages 모니터링",
                "recovery_actions": ["verify_pages", "restart_monitoring"]
            },
            {
                "name": "cache_monitor",
                "display_name": "캐시 데이터 모니터링",
                "recovery_actions": ["refresh_cache", "clear_cache"]
            },
            {
                "name": "git_deployment",
                "display_name": "Git 배포 시스템",
                "recovery_actions": ["reset_branch", "force_push"]
            },
            {
                "name": "message_system",
                "display_name": "메시지 시스템",
                "recovery_actions": ["reset_templates", "test_webhook"]
            },
            {
                "name": "webhook_integration",
                "display_name": "웹훅 통합",
                "recovery_actions": ["test_connection", "reset_config"]
            }
        ]
        
        for config in component_configs:
            self.components[config["name"]] = SystemComponent(
                name=config["display_name"],
                status=SystemStatus.UNKNOWN,
                last_updated=datetime.now(),
                details={},
                recovery_actions=config["recovery_actions"]
            )
    
    def register_status_callback(self, callback: Callable[[Dict[str, SystemComponent]], None]):
        """상태 업데이트 콜백 등록"""
        self.status_callbacks.append(callback)
    
    def register_alert_callback(self, callback: Callable[[StatusAlert], None]):
        """알림 콜백 등록"""
        self.alert_callbacks.append(callback)
    
    def register_statistics_callback(self, callback: Callable[[DeploymentStatistics], None]):
        """통계 콜백 등록"""
        self.statistics_callbacks.append(callback)
    
    def register_recovery_callback(self, callback: Callable[[str, str], bool]):
        """복구 액션 콜백 등록"""
        self.recovery_callbacks.append(callback)
    
    def start_monitoring(self):
        """통합 모니터링 시작"""
        with self.monitoring_lock:
            if self.monitoring_active:
                self.log_message("⚠️ 통합 모니터링이 이미 실행 중입니다", "WARNING")
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.log_message("📊 통합 상태 모니터링 시작")
    
    def stop_monitoring(self):
        """통합 모니터링 중지"""
        with self.monitoring_lock:
            if not self.monitoring_active:
                return
            
            self.monitoring_active = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            self.log_message("📊 통합 상태 모니터링 중지")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        try:
            while self.monitoring_active:
                # 모든 컴포넌트 상태 업데이트
                self.update_all_component_status()
                
                # 배포 통계 업데이트
                self.update_deployment_statistics()
                
                # 상태 콜백 호출
                self._notify_status_update()
                
                # 통계 콜백 호출
                if self.deployment_stats:
                    self._notify_statistics_update()
                
                time.sleep(self.update_interval)
                
        except Exception as e:
            self.log_message(f"❌ 모니터링 루프 오류: {str(e)}", "ERROR")
        finally:
            self.monitoring_active = False
    
    def update_all_component_status(self):
        """모든 컴포넌트 상태 업데이트"""
        try:
            # 배포 모니터 상태 확인
            self.update_deployment_monitor_status()
            
            # GitHub Pages 모니터 상태 확인
            self.update_github_pages_monitor_status()
            
            # 캐시 모니터 상태 확인
            self.update_cache_monitor_status()
            
            # Git 배포 시스템 상태 확인
            self.update_git_deployment_status()
            
            # 메시지 시스템 상태 확인
            self.update_message_system_status()
            
            # 웹훅 통합 상태 확인
            self.update_webhook_integration_status()
            
        except Exception as e:
            self.log_message(f"❌ 컴포넌트 상태 업데이트 오류: {str(e)}", "ERROR")
    
    def update_deployment_monitor_status(self):
        """배포 모니터 상태 업데이트"""
        try:
            # 배포 모니터 로그 파일 확인
            deployment_log = os.path.join(self.logs_dir, "deployment_monitor.log")
            metrics_log = os.path.join(self.logs_dir, "deployment_metrics.json")
            
            status = SystemStatus.HEALTHY
            details = {"active_sessions": 0, "recent_deployments": 0}
            error_message = None
            
            # 메트릭 파일 확인
            if os.path.exists(metrics_log):
                try:
                    with open(metrics_log, 'r', encoding='utf-8') as f:
                        metrics_data = json.load(f)
                    
                    # 최근 24시간 배포 수 계산
                    recent_count = 0
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    
                    for deployment in metrics_data:
                        if deployment.get('start_time'):
                            deploy_time = datetime.fromtimestamp(deployment['start_time'])
                            if deploy_time > cutoff_time:
                                recent_count += 1
                    
                    details["recent_deployments"] = recent_count
                    details["total_deployments"] = len(metrics_data)
                    
                    # 최근 실패 확인
                    recent_failures = [
                        d for d in metrics_data[-10:] 
                        if not d.get('overall_success', True)
                    ]
                    
                    if len(recent_failures) > 3:
                        status = SystemStatus.WARNING
                        error_message = f"최근 {len(recent_failures)}개 배포 실패"
                    
                except Exception as e:
                    status = SystemStatus.ERROR
                    error_message = f"메트릭 파일 읽기 오류: {str(e)}"
            else:
                status = SystemStatus.WARNING
                error_message = "배포 메트릭 파일이 없습니다"
            
            self._update_component_status("deployment_monitor", status, details, error_message)
            
        except Exception as e:
            self._update_component_status(
                "deployment_monitor", 
                SystemStatus.ERROR, 
                {}, 
                f"상태 확인 오류: {str(e)}"
            )
    
    def update_github_pages_monitor_status(self):
        """GitHub Pages 모니터 상태 업데이트"""
        try:
            # GitHub Pages 모니터 로그 파일 확인
            pages_log = os.path.join(self.logs_dir, "github_pages_monitor.log")
            accessibility_log = os.path.join(self.logs_dir, "pages_accessibility.json")
            
            status = SystemStatus.HEALTHY
            details = {"accessibility_checks": 0, "success_rate": 0.0}
            error_message = None
            
            # 접근성 로그 확인
            if os.path.exists(accessibility_log):
                try:
                    with open(accessibility_log, 'r', encoding='utf-8') as f:
                        accessibility_data = json.load(f)
                    
                    if accessibility_data:
                        # 최근 10개 확인 결과 분석
                        recent_checks = accessibility_data[-10:]
                        successful_checks = sum(
                            1 for check in recent_checks 
                            if check.get('final_accessible', False)
                        )
                        
                        success_rate = (successful_checks / len(recent_checks)) * 100
                        details["accessibility_checks"] = len(accessibility_data)
                        details["success_rate"] = success_rate
                        
                        if success_rate < 50:
                            status = SystemStatus.ERROR
                            error_message = f"접근성 성공률 낮음: {success_rate:.1f}%"
                        elif success_rate < 80:
                            status = SystemStatus.WARNING
                            error_message = f"접근성 성공률 주의: {success_rate:.1f}%"
                    
                except Exception as e:
                    status = SystemStatus.ERROR
                    error_message = f"접근성 로그 읽기 오류: {str(e)}"
            else:
                status = SystemStatus.WARNING
                error_message = "접근성 로그 파일이 없습니다"
            
            self._update_component_status("github_pages_monitor", status, details, error_message)
            
        except Exception as e:
            self._update_component_status(
                "github_pages_monitor", 
                SystemStatus.ERROR, 
                {}, 
                f"상태 확인 오류: {str(e)}"
            )
    
    def update_cache_monitor_status(self):
        """캐시 모니터 상태 업데이트"""
        try:
            # 캐시 데이터 파일 확인
            cache_file = os.path.join(os.path.dirname(self.script_dir), "data", "market_data_cache.json")
            data_quality_log = os.path.join(os.path.dirname(self.script_dir), "data", "data_quality_log.json")
            
            status = SystemStatus.HEALTHY
            details = {"cache_age_minutes": 0, "data_quality": 0.0}
            error_message = None
            
            # 캐시 파일 확인
            if os.path.exists(cache_file):
                try:
                    file_stat = os.stat(cache_file)
                    cache_age = (time.time() - file_stat.st_mtime) / 60  # 분 단위
                    details["cache_age_minutes"] = cache_age
                    
                    # 캐시 나이에 따른 상태 결정
                    if cache_age > 60:  # 1시간 이상
                        status = SystemStatus.ERROR
                        error_message = f"캐시 데이터 만료: {cache_age:.0f}분 전"
                    elif cache_age > 15:  # 15분 이상
                        status = SystemStatus.WARNING
                        error_message = f"캐시 데이터 오래됨: {cache_age:.0f}분 전"
                    
                    # 데이터 품질 확인
                    if os.path.exists(data_quality_log):
                        with open(data_quality_log, 'r', encoding='utf-8') as f:
                            quality_data = json.load(f)
                        
                        if quality_data:
                            latest_quality = quality_data[-1].get('overall_quality', 0.0)
                            details["data_quality"] = latest_quality
                            
                            if latest_quality < 0.6:
                                status = SystemStatus.ERROR
                                error_message = f"데이터 품질 낮음: {latest_quality:.1%}"
                            elif latest_quality < 0.8:
                                status = SystemStatus.WARNING
                                error_message = f"데이터 품질 주의: {latest_quality:.1%}"
                    
                except Exception as e:
                    status = SystemStatus.ERROR
                    error_message = f"캐시 파일 분석 오류: {str(e)}"
            else:
                status = SystemStatus.ERROR
                error_message = "캐시 파일이 없습니다"
            
            self._update_component_status("cache_monitor", status, details, error_message)
            
        except Exception as e:
            self._update_component_status(
                "cache_monitor", 
                SystemStatus.ERROR, 
                {}, 
                f"상태 확인 오류: {str(e)}"
            )
    
    def update_git_deployment_status(self):
        """Git 배포 시스템 상태 업데이트"""
        try:
            # Git 배포 로그 확인
            git_log = os.path.join(os.path.dirname(self.script_dir), "Posco_News_Mini_Final_GUI", "git_deployment.log")
            
            status = SystemStatus.HEALTHY
            details = {"last_deployment": None, "branch_status": "unknown"}
            error_message = None
            
            # Git 상태 확인 (간단한 체크)
            try:
                import subprocess
                
                # 현재 브랜치 확인
                result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True,
                    text=True,
                    cwd=self.base_dir
                )
                
                if result.returncode == 0:
                    current_branch = result.stdout.strip()
                    details["branch_status"] = current_branch
                    
                    # publish 브랜치가 아니면 경고
                    if current_branch != "publish":
                        status = SystemStatus.WARNING
                        error_message = f"현재 브랜치: {current_branch} (publish 아님)"
                else:
                    status = SystemStatus.ERROR
                    error_message = "Git 상태 확인 실패"
                
            except Exception as e:
                status = SystemStatus.WARNING
                error_message = f"Git 명령 실행 오류: {str(e)}"
            
            # 배포 로그 확인
            if os.path.exists(git_log):
                try:
                    file_stat = os.stat(git_log)
                    last_modified = datetime.fromtimestamp(file_stat.st_mtime)
                    details["last_deployment"] = last_modified.isoformat()
                    
                    # 최근 배포가 너무 오래되었으면 경고
                    if datetime.now() - last_modified > timedelta(days=1):
                        if status == SystemStatus.HEALTHY:
                            status = SystemStatus.WARNING
                            error_message = "최근 배포가 1일 이상 전입니다"
                
                except Exception as e:
                    if status == SystemStatus.HEALTHY:
                        status = SystemStatus.WARNING
                        error_message = f"배포 로그 분석 오류: {str(e)}"
            
            self._update_component_status("git_deployment", status, details, error_message)
            
        except Exception as e:
            self._update_component_status(
                "git_deployment", 
                SystemStatus.ERROR, 
                {}, 
                f"상태 확인 오류: {str(e)}"
            )
    
    def update_message_system_status(self):
        """메시지 시스템 상태 업데이트"""
        try:
            # 메시지 템플릿 파일 확인
            templates_file = os.path.join(os.path.dirname(self.script_dir), "config", "message_templates.json")
            
            status = SystemStatus.HEALTHY
            details = {"templates_count": 0, "last_updated": None}
            error_message = None
            
            if os.path.exists(templates_file):
                try:
                    with open(templates_file, 'r', encoding='utf-8') as f:
                        templates_data = json.load(f)
                    
                    details["templates_count"] = len(templates_data.get('templates', {}))
                    
                    file_stat = os.stat(templates_file)
                    last_modified = datetime.fromtimestamp(file_stat.st_mtime)
                    details["last_updated"] = last_modified.isoformat()
                    
                    # 템플릿이 없으면 오류
                    if details["templates_count"] == 0:
                        status = SystemStatus.ERROR
                        error_message = "메시지 템플릿이 없습니다"
                    
                except Exception as e:
                    status = SystemStatus.ERROR
                    error_message = f"템플릿 파일 읽기 오류: {str(e)}"
            else:
                status = SystemStatus.ERROR
                error_message = "메시지 템플릿 파일이 없습니다"
            
            self._update_component_status("message_system", status, details, error_message)
            
        except Exception as e:
            self._update_component_status(
                "message_system", 
                SystemStatus.ERROR, 
                {}, 
                f"상태 확인 오류: {str(e)}"
            )
    
    def update_webhook_integration_status(self):
        """웹훅 통합 상태 업데이트"""
        try:
            # 웹훅 설정 파일 확인
            webhook_config = os.path.join(os.path.dirname(self.script_dir), "config", "webhook_config.json")
            
            status = SystemStatus.HEALTHY
            details = {"webhooks_count": 0, "last_test": None}
            error_message = None
            
            if os.path.exists(webhook_config):
                try:
                    with open(webhook_config, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    webhooks = config_data.get('webhooks', {})
                    details["webhooks_count"] = len(webhooks)
                    
                    # 웹훅이 없으면 경고
                    if details["webhooks_count"] == 0:
                        status = SystemStatus.WARNING
                        error_message = "설정된 웹훅이 없습니다"
                    
                    # 마지막 테스트 시간 확인 (있다면)
                    if 'last_test' in config_data:
                        details["last_test"] = config_data['last_test']
                    
                except Exception as e:
                    status = SystemStatus.ERROR
                    error_message = f"웹훅 설정 읽기 오류: {str(e)}"
            else:
                status = SystemStatus.WARNING
                error_message = "웹훅 설정 파일이 없습니다"
            
            self._update_component_status("webhook_integration", status, details, error_message)
            
        except Exception as e:
            self._update_component_status(
                "webhook_integration", 
                SystemStatus.ERROR, 
                {}, 
                f"상태 확인 오류: {str(e)}"
            )
    
    def _update_component_status(self, component_name: str, status: SystemStatus, 
                               details: Dict[str, Any], error_message: Optional[str] = None):
        """컴포넌트 상태 업데이트"""
        if component_name in self.components:
            old_status = self.components[component_name].status
            
            self.components[component_name].status = status
            self.components[component_name].last_updated = datetime.now()
            self.components[component_name].details = details
            self.components[component_name].error_message = error_message
            
            # 상태 변화 시 알림 생성
            if old_status != status:
                self._create_status_change_alert(component_name, old_status, status, error_message)
    
    def _create_status_change_alert(self, component_name: str, old_status: SystemStatus, 
                                  new_status: SystemStatus, error_message: Optional[str]):
        """상태 변화 알림 생성"""
        component = self.components[component_name]
        
        # 알림 레벨 결정
        alert_level = AlertLevel.INFO
        if new_status == SystemStatus.ERROR:
            alert_level = AlertLevel.ERROR
        elif new_status == SystemStatus.CRITICAL:
            alert_level = AlertLevel.CRITICAL
        elif new_status == SystemStatus.WARNING:
            alert_level = AlertLevel.WARNING
        
        # 알림 메시지 생성
        message = f"{component.name} 상태가 {old_status.value}에서 {new_status.value}로 변경되었습니다"
        if error_message:
            message += f": {error_message}"
        
        # 자동 복구 가능 여부 확인
        auto_recovery = (
            new_status in [SystemStatus.WARNING, SystemStatus.ERROR] and 
            component.recovery_actions
        )
        
        recovery_action = component.recovery_actions[0] if auto_recovery else None
        
        alert = StatusAlert(
            component=component_name,
            level=alert_level,
            message=message,
            timestamp=datetime.now(),
            details={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "component_details": component.details
            },
            auto_recovery=auto_recovery,
            recovery_action=recovery_action
        )
        
        self._send_alert(alert)
    
    def _send_alert(self, alert: StatusAlert):
        """알림 전송"""
        # 알림 히스토리에 추가
        self.alerts.append(alert)
        
        # 최근 100개 알림만 유지
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # 로그 기록
        self.log_message(f"[{alert.level.value.upper()}] {alert.component}: {alert.message}")
        
        # 알림 콜백 호출
        self._notify_alert(alert)
        
        # 알림 파일에 저장
        self._save_alert_to_file(alert)
        
        # 자동 복구 시도
        if alert.auto_recovery and alert.recovery_action:
            self._attempt_auto_recovery(alert.component, alert.recovery_action)
    
    def _save_alert_to_file(self, alert: StatusAlert):
        """알림을 파일에 저장"""
        try:
            # 기존 알림들 로드
            existing_alerts = []
            if os.path.exists(self.alerts_log):
                with open(self.alerts_log, 'r', encoding='utf-8') as f:
                    existing_alerts = json.load(f)
            
            # 새 알림 추가
            alert_dict = {
                "component": alert.component,
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "details": alert.details,
                "auto_recovery": alert.auto_recovery,
                "recovery_action": alert.recovery_action
            }
            
            existing_alerts.append(alert_dict)
            
            # 최근 500개 알림만 유지
            if len(existing_alerts) > 500:
                existing_alerts = existing_alerts[-500:]
            
            # 파일에 저장
            with open(self.alerts_log, 'w', encoding='utf-8') as f:
                json.dump(existing_alerts, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.log_message(f"❌ 알림 파일 저장 실패: {str(e)}", "ERROR")
    
    def _attempt_auto_recovery(self, component_name: str, recovery_action: str):
        """자동 복구 시도"""
        try:
            self.log_message(f"🔄 자동 복구 시도: {component_name} - {recovery_action}")
            
            # 복구 콜백 호출
            recovery_success = False
            for callback in self.recovery_callbacks:
                try:
                    recovery_success = callback(component_name, recovery_action)
                    if recovery_success:
                        break
                except Exception as e:
                    self.log_message(f"❌ 복구 콜백 오류: {str(e)}", "ERROR")
            
            if recovery_success:
                self.log_message(f"✅ 자동 복구 성공: {component_name}")
                
                # 복구 성공 알림
                recovery_alert = StatusAlert(
                    component=component_name,
                    level=AlertLevel.INFO,
                    message=f"{self.components[component_name].name} 자동 복구 성공",
                    timestamp=datetime.now(),
                    details={"recovery_action": recovery_action}
                )
                self._notify_alert(recovery_alert)
            else:
                self.log_message(f"❌ 자동 복구 실패: {component_name}")
                
        except Exception as e:
            self.log_message(f"❌ 자동 복구 중 오류: {str(e)}", "ERROR")
    
    def update_deployment_statistics(self):
        """배포 통계 업데이트"""
        try:
            metrics_log = os.path.join(self.logs_dir, "deployment_metrics.json")
            
            if not os.path.exists(metrics_log):
                self.deployment_stats = DeploymentStatistics(
                    total_deployments=0,
                    successful_deployments=0,
                    failed_deployments=0,
                    average_duration=0.0,
                    success_rate=0.0,
                    last_deployment=None,
                    recent_deployments=[]
                )
                return
            
            with open(metrics_log, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            
            if not metrics_data:
                self.deployment_stats = DeploymentStatistics(
                    total_deployments=0,
                    successful_deployments=0,
                    failed_deployments=0,
                    average_duration=0.0,
                    success_rate=0.0,
                    last_deployment=None,
                    recent_deployments=[]
                )
                return
            
            # 통계 계산
            total_deployments = len(metrics_data)
            successful_deployments = sum(1 for d in metrics_data if d.get('overall_success', False))
            failed_deployments = total_deployments - successful_deployments
            
            # 성공률 계산
            success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0.0
            
            # 평균 소요 시간 계산
            durations = [d.get('total_duration', 0) for d in metrics_data if d.get('total_duration')]
            average_duration = sum(durations) / len(durations) if durations else 0.0
            
            # 마지막 배포 시간
            last_deployment = None
            if metrics_data:
                last_deploy_data = max(metrics_data, key=lambda x: x.get('start_time', 0))
                if last_deploy_data.get('start_time'):
                    last_deployment = datetime.fromtimestamp(last_deploy_data['start_time'])
            
            # 최근 배포들 (최근 10개)
            recent_deployments = sorted(
                metrics_data, 
                key=lambda x: x.get('start_time', 0), 
                reverse=True
            )[:10]
            
            self.deployment_stats = DeploymentStatistics(
                total_deployments=total_deployments,
                successful_deployments=successful_deployments,
                failed_deployments=failed_deployments,
                average_duration=average_duration,
                success_rate=success_rate,
                last_deployment=last_deployment,
                recent_deployments=recent_deployments
            )
            
        except Exception as e:
            self.log_message(f"❌ 배포 통계 업데이트 오류: {str(e)}", "ERROR")
    
    def _notify_status_update(self):
        """상태 업데이트 알림"""
        for callback in self.status_callbacks:
            try:
                callback(self.components.copy())
            except Exception as e:
                self.log_message(f"❌ 상태 콜백 오류: {str(e)}", "ERROR")
    
    def _notify_alert(self, alert: StatusAlert):
        """알림 전송"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.log_message(f"❌ 알림 콜백 오류: {str(e)}", "ERROR")
    
    def _notify_statistics_update(self):
        """통계 업데이트 알림"""
        for callback in self.statistics_callbacks:
            try:
                callback(self.deployment_stats)
            except Exception as e:
                self.log_message(f"❌ 통계 콜백 오류: {str(e)}", "ERROR")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """시스템 전체 개요 조회"""
        try:
            # 상태별 컴포넌트 수 계산
            status_counts = {}
            for status in SystemStatus:
                status_counts[status.value] = 0
            
            for component in self.components.values():
                status_counts[component.status.value] += 1
            
            # 전체 시스템 건강도 계산
            total_components = len(self.components)
            healthy_components = status_counts[SystemStatus.HEALTHY.value]
            
            if total_components == 0:
                overall_health = "unknown"
            elif healthy_components == total_components:
                overall_health = "excellent"
            elif healthy_components >= total_components * 0.8:
                overall_health = "good"
            elif healthy_components >= total_components * 0.6:
                overall_health = "fair"
            else:
                overall_health = "poor"
            
            # 최근 알림 수
            recent_alerts = len([
                alert for alert in self.alerts 
                if alert.timestamp > datetime.now() - timedelta(hours=1)
            ])
            
            return {
                "overall_health": overall_health,
                "total_components": total_components,
                "status_counts": status_counts,
                "recent_alerts": recent_alerts,
                "monitoring_active": self.monitoring_active,
                "last_updated": datetime.now().isoformat(),
                "deployment_stats": asdict(self.deployment_stats) if self.deployment_stats else None
            }
            
        except Exception as e:
            self.log_message(f"❌ 시스템 개요 조회 오류: {str(e)}", "ERROR")
            return {"error": str(e)}
    
    def get_component_details(self, component_name: str) -> Optional[Dict[str, Any]]:
        """특정 컴포넌트 상세 정보 조회"""
        if component_name not in self.components:
            return None
        
        component = self.components[component_name]
        return {
            "name": component.name,
            "status": component.status.value,
            "last_updated": component.last_updated.isoformat(),
            "details": component.details,
            "error_message": component.error_message,
            "recovery_actions": component.recovery_actions
        }
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """최근 알림 조회"""
        recent_alerts = sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [
            {
                "component": alert.component,
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "details": alert.details,
                "auto_recovery": alert.auto_recovery,
                "recovery_action": alert.recovery_action
            }
            for alert in recent_alerts
        ]
    
    def trigger_manual_recovery(self, component_name: str, recovery_action: str) -> bool:
        """수동 복구 트리거"""
        try:
            self.log_message(f"🔧 수동 복구 실행: {component_name} - {recovery_action}")
            
            # 복구 콜백 호출
            recovery_success = False
            for callback in self.recovery_callbacks:
                try:
                    recovery_success = callback(component_name, recovery_action)
                    if recovery_success:
                        break
                except Exception as e:
                    self.log_message(f"❌ 복구 콜백 오류: {str(e)}", "ERROR")
            
            if recovery_success:
                self.log_message(f"✅ 수동 복구 성공: {component_name}")
                
                # 복구 성공 알림
                recovery_alert = StatusAlert(
                    component=component_name,
                    level=AlertLevel.INFO,
                    message=f"{self.components[component_name].name} 수동 복구 성공",
                    timestamp=datetime.now(),
                    details={"recovery_action": recovery_action, "manual": True}
                )
                self._send_alert(recovery_alert)
                
                # 상태 즉시 업데이트
                self.update_all_component_status()
                
                return True
            else:
                self.log_message(f"❌ 수동 복구 실패: {component_name}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 수동 복구 중 오류: {str(e)}", "ERROR")
            return False
    
    def export_status_report(self, file_path: Optional[str] = None) -> str:
        """상태 보고서 내보내기"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.logs_dir, f"integrated_status_report_{timestamp}.json")
        
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "system_overview": self.get_system_overview(),
                "components": {
                    name: self.get_component_details(name)
                    for name in self.components.keys()
                },
                "recent_alerts": self.get_recent_alerts(50),
                "deployment_statistics": asdict(self.deployment_stats) if self.deployment_stats else None
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"📄 상태 보고서 생성: {file_path}")
            return file_path
            
        except Exception as e:
            self.log_message(f"❌ 상태 보고서 생성 실패: {str(e)}", "ERROR")
            raise


# 편의 함수들
def create_integrated_status_reporter(base_dir: Optional[str] = None) -> IntegratedStatusReporter:
    """통합 상태 보고 시스템 인스턴스 생성"""
    return IntegratedStatusReporter(base_dir)


if __name__ == "__main__":
    # 테스트 코드
    print("🔧 통합 상태 보고 시스템 테스트")
    
    reporter = create_integrated_status_reporter()
    
    # 콜백 등록 (테스트용)
    def test_status_callback(components):
        print(f"📊 상태 업데이트: {len(components)}개 컴포넌트")
        for name, component in components.items():
            print(f"  {component.name}: {component.status.value}")
    
    def test_alert_callback(alert):
        print(f"🚨 알림: [{alert.level.value}] {alert.component} - {alert.message}")
    
    def test_statistics_callback(stats):
        print(f"📈 통계: 총 {stats.total_deployments}개 배포, 성공률 {stats.success_rate:.1f}%")
    
    def test_recovery_callback(component, action):
        print(f"🔧 복구 시도: {component} - {action}")
        return True  # 테스트에서는 항상 성공
    
    reporter.register_status_callback(test_status_callback)
    reporter.register_alert_callback(test_alert_callback)
    reporter.register_statistics_callback(test_statistics_callback)
    reporter.register_recovery_callback(test_recovery_callback)
    
    # 모니터링 시작
    reporter.start_monitoring()
    
    print("📊 10초간 모니터링 실행...")
    time.sleep(10)
    
    # 시스템 개요 출력
    overview = reporter.get_system_overview()
    print(f"\n📋 시스템 개요:")
    print(f"  전체 건강도: {overview['overall_health']}")
    print(f"  총 컴포넌트: {overview['total_components']}")
    print(f"  최근 알림: {overview['recent_alerts']}")
    
    # 보고서 생성
    report_path = reporter.export_status_report()
    print(f"\n📄 상태 보고서 생성: {report_path}")
    
    # 모니터링 중지
    reporter.stop_monitoring()
    
    print("✅ 통합 상태 보고 시스템 테스트 완료")