#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 상태 보고 시스템 (포팅)
기존 WatchHamster 상태 보고 로직을 FastAPI 서비스로 포팅

주요 기능:
- 모든 시스템 컴포넌트 상태 통합 관리
- 실시간 상태 업데이트 및 알림
- 배포 통계 및 성능 메트릭 추적
"""

import logging
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

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
    """통합 상태 보고 시스템"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """통합 상태 보고 시스템 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.logger = logger
        
        # 시스템 컴포넌트들
        self.components: Dict[str, SystemComponent] = {}
        self.alerts: List[StatusAlert] = []
        
        # 모니터링 상태
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.update_interval = 5  # 5초마다 업데이트
        
        # 콜백 함수들 (WebSocket 브로드캐스트용)
        self.status_callbacks: List[Callable[[Dict[str, SystemComponent]], None]] = []
        self.alert_callbacks: List[Callable[[StatusAlert], None]] = []
        self.statistics_callbacks: List[Callable[[DeploymentStatistics], None]] = []
        
        # 통계 데이터
        self.deployment_stats: Optional[DeploymentStatistics] = None
        
        # 시스템 컴포넌트 초기화
        self._initialize_components()
        
        self.logger.info("📊 IntegratedStatusReporter 초기화 완료")
    
    def _initialize_components(self):
        """시스템 컴포넌트 초기화"""
        default_components = [
            "posco_news",
            "github_pages", 
            "cache_monitor",
            "deployment",
            "message_system",
            "webhook_system"
        ]
        
        for component_name in default_components:
            self.components[component_name] = SystemComponent(
                name=component_name,
                status=SystemStatus.UNKNOWN,
                last_updated=datetime.now(),
                details={}
            )
    
    async def start_monitoring(self):
        """상태 모니터링 시작"""
        if self.monitoring_active:
            self.logger.warning("상태 모니터링이 이미 실행 중입니다")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("📊 상태 모니터링 시작")
    
    async def stop_monitoring(self):
        """상태 모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("📊 상태 모니터링 중지")
    
    async def _monitoring_loop(self):
        """모니터링 메인 루프"""
        while self.monitoring_active:
            try:
                # 컴포넌트 상태 업데이트
                await self._update_component_status()
                
                # 상태 변화 감지 및 알림
                await self._check_status_changes()
                
                # 콜백 호출 (WebSocket 브로드캐스트)
                await self._notify_status_callbacks()
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"상태 모니터링 중 오류: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def _update_component_status(self):
        """컴포넌트 상태 업데이트"""
        try:
            for component_name, component in self.components.items():
                # 실제 컴포넌트 상태 체크 로직
                new_status = await self._check_component_health(component_name)
                
                if component.status != new_status:
                    old_status = component.status
                    component.status = new_status
                    component.last_updated = datetime.now()
                    
                    # 상태 변화 로깅
                    self.logger.info(f"컴포넌트 상태 변화: {component_name} {old_status.value} -> {new_status.value}")
                    
                    # 알림 생성
                    await self._create_status_alert(component_name, old_status, new_status)
                
        except Exception as e:
            self.logger.error(f"컴포넌트 상태 업데이트 실패: {e}")
    
    async def _check_component_health(self, component_name: str) -> SystemStatus:
        """컴포넌트 건강 상태 체크"""
        try:
            # 실제 구현에서는 각 컴포넌트별 상태 체크 로직
            # 여기서는 시뮬레이션
            
            if component_name == "posco_news":
                # POSCO 뉴스 시스템 상태 체크
                return SystemStatus.HEALTHY
            elif component_name == "github_pages":
                # GitHub Pages 상태 체크
                return SystemStatus.HEALTHY
            elif component_name == "cache_monitor":
                # 캐시 모니터 상태 체크
                return SystemStatus.HEALTHY
            elif component_name == "deployment":
                # 배포 시스템 상태 체크
                return SystemStatus.HEALTHY
            elif component_name == "message_system":
                # 메시지 시스템 상태 체크
                return SystemStatus.HEALTHY
            elif component_name == "webhook_system":
                # 웹훅 시스템 상태 체크
                return SystemStatus.HEALTHY
            else:
                return SystemStatus.UNKNOWN
                
        except Exception as e:
            self.logger.error(f"컴포넌트 상태 체크 실패 ({component_name}): {e}")
            return SystemStatus.ERROR
    
    async def _create_status_alert(self, component_name: str, old_status: SystemStatus, new_status: SystemStatus):
        """상태 변화 알림 생성"""
        try:
            # 알림 레벨 결정
            if new_status == SystemStatus.CRITICAL:
                level = AlertLevel.CRITICAL
            elif new_status == SystemStatus.ERROR:
                level = AlertLevel.ERROR
            elif new_status == SystemStatus.WARNING:
                level = AlertLevel.WARNING
            else:
                level = AlertLevel.INFO
            
            alert = StatusAlert(
                component=component_name,
                level=level,
                message=f"{component_name} 상태가 {old_status.value}에서 {new_status.value}로 변경되었습니다",
                timestamp=datetime.now(),
                details={
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "component": component_name
                }
            )
            
            self.alerts.append(alert)
            
            # 알림 콜백 호출
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"알림 콜백 실행 실패: {e}")
                    
        except Exception as e:
            self.logger.error(f"상태 알림 생성 실패: {e}")
    
    async def _check_status_changes(self):
        """상태 변화 감지"""
        try:
            # 전체 시스템 상태 평가
            healthy_count = sum(1 for c in self.components.values() if c.status == SystemStatus.HEALTHY)
            total_count = len(self.components)
            
            # 시스템 전체 상태 결정
            if healthy_count == total_count:
                overall_status = SystemStatus.HEALTHY
            elif healthy_count >= total_count * 0.7:
                overall_status = SystemStatus.WARNING
            else:
                overall_status = SystemStatus.ERROR
            
            # 전체 상태 변화 체크
            if not hasattr(self, '_last_overall_status'):
                self._last_overall_status = overall_status
            elif self._last_overall_status != overall_status:
                self.logger.info(f"전체 시스템 상태 변화: {self._last_overall_status.value} -> {overall_status.value}")
                self._last_overall_status = overall_status
                
        except Exception as e:
            self.logger.error(f"상태 변화 감지 실패: {e}")
    
    async def _notify_status_callbacks(self):
        """상태 콜백 알림"""
        try:
            for callback in self.status_callbacks:
                try:
                    callback(self.components)
                except Exception as e:
                    self.logger.error(f"상태 콜백 실행 실패: {e}")
        except Exception as e:
            self.logger.error(f"상태 콜백 알림 실패: {e}")
    
    async def update_component_status(self, component_name: str, status: SystemStatus, 
                                    details: Optional[Dict[str, Any]] = None, 
                                    error_message: Optional[str] = None):
        """컴포넌트 상태 수동 업데이트"""
        try:
            if component_name not in self.components:
                self.components[component_name] = SystemComponent(
                    name=component_name,
                    status=status,
                    last_updated=datetime.now(),
                    details=details or {}
                )
            else:
                component = self.components[component_name]
                old_status = component.status
                component.status = status
                component.last_updated = datetime.now()
                component.details.update(details or {})
                component.error_message = error_message
                
                # 상태 변화 시 알림 생성
                if old_status != status:
                    await self._create_status_alert(component_name, old_status, status)
            
            self.logger.info(f"컴포넌트 상태 업데이트: {component_name} -> {status.value}")
            
        except Exception as e:
            self.logger.error(f"컴포넌트 상태 업데이트 실패: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """전체 시스템 상태 조회"""
        try:
            healthy_count = sum(1 for c in self.components.values() if c.status == SystemStatus.HEALTHY)
            warning_count = sum(1 for c in self.components.values() if c.status == SystemStatus.WARNING)
            error_count = sum(1 for c in self.components.values() if c.status in [SystemStatus.ERROR, SystemStatus.CRITICAL])
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_components': len(self.components),
                'healthy_components': healthy_count,
                'warning_components': warning_count,
                'error_components': error_count,
                'components': {name: {
                    'status': comp.status.value,
                    'last_updated': comp.last_updated.isoformat(),
                    'details': comp.details,
                    'error_message': comp.error_message
                } for name, comp in self.components.items()},
                'recent_alerts': [asdict(alert) for alert in self.alerts[-10:]]  # 최근 10개 알림
            }
            
        except Exception as e:
            self.logger.error(f"시스템 상태 조회 실패: {e}")
            return {}
    
    async def get_deployment_statistics(self) -> Optional[DeploymentStatistics]:
        """배포 통계 조회"""
        try:
            # 실제 구현에서는 배포 데이터베이스에서 조회
            # 여기서는 시뮬레이션 데이터
            return DeploymentStatistics(
                total_deployments=50,
                successful_deployments=47,
                failed_deployments=3,
                average_duration=120.5,
                success_rate=94.0,
                last_deployment=datetime.now() - timedelta(hours=2),
                recent_deployments=[
                    {
                        'id': 'deploy_001',
                        'status': 'success',
                        'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                        'duration': 115.2
                    },
                    {
                        'id': 'deploy_002', 
                        'status': 'success',
                        'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                        'duration': 98.7
                    }
                ]
            )
            
        except Exception as e:
            self.logger.error(f"배포 통계 조회 실패: {e}")
            return None
    
    def add_status_callback(self, callback: Callable[[Dict[str, SystemComponent]], None]):
        """상태 콜백 추가"""
        self.status_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable[[StatusAlert], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def add_statistics_callback(self, callback: Callable[[DeploymentStatistics], None]):
        """통계 콜백 추가"""
        self.statistics_callbacks.append(callback)

# 싱글톤 인스턴스
_status_reporter_instance = None

def create_integrated_status_reporter(base_dir: Optional[str] = None) -> IntegratedStatusReporter:
    """통합 상태 보고 시스템 싱글톤 인스턴스 반환"""
    global _status_reporter_instance
    if _status_reporter_instance is None:
        _status_reporter_instance = IntegratedStatusReporter(base_dir)
    return _status_reporter_instance