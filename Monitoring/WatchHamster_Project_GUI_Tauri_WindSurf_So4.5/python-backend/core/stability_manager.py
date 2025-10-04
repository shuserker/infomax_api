#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안정성 관리자 (포팅)
기존 WatchHamster 안정성 관리 로직을 FastAPI 서비스로 포팅

주요 기능:
- 시스템 안정성 모니터링
- 오류 감지 및 자동 복구
- 시스템 상태 추적 및 보고
"""

import logging
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class SystemHealth(Enum):
    """시스템 건강 상태"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class RecoveryAction(Enum):
    """복구 액션 타입"""
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    RESET_CONFIG = "reset_config"
    MANUAL_INTERVENTION = "manual_intervention"

@dataclass
class SystemError:
    """시스템 오류 정보"""
    error_id: str
    component: str
    error_type: str
    message: str
    severity: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    recovery_actions: List[str] = None
    
    def __post_init__(self):
        if self.recovery_actions is None:
            self.recovery_actions = []

@dataclass
class StabilityMetrics:
    """안정성 메트릭"""
    error_count: int
    recovery_count: int
    uptime_hours: float
    last_error_time: Optional[datetime]
    system_health: SystemHealth
    active_issues: int

class StabilityManager:
    """안정성 관리자"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """안정성 관리자 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.logger = logger
        
        # 오류 추적
        self.errors: List[SystemError] = []
        self.recovery_actions: Dict[str, Callable] = {}
        
        # 모니터링 상태
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.start_time = datetime.now()
        
        # 안정성 임계값
        self.thresholds = {
            'max_errors_per_hour': 10,
            'max_unresolved_errors': 5,
            'critical_error_types': ['system_crash', 'data_corruption', 'security_breach']
        }
        
        # 복구 액션 등록
        self._register_recovery_actions()
        
        self.logger.info("🛡️ StabilityManager 초기화 완료")
    
    def _register_recovery_actions(self):
        """복구 액션 등록"""
        self.recovery_actions = {
            'restart_service': self._restart_service,
            'clear_cache': self._clear_cache,
            'reset_config': self._reset_config,
            'check_dependencies': self._check_dependencies,
            'cleanup_resources': self._cleanup_resources
        }
    
    async def start_monitoring(self):
        """안정성 모니터링 시작"""
        if self.monitoring_active:
            self.logger.warning("안정성 모니터링이 이미 실행 중입니다")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("🛡️ 안정성 모니터링 시작")
    
    async def stop_monitoring(self):
        """안정성 모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("🛡️ 안정성 모니터링 중지")
    
    async def _monitoring_loop(self):
        """모니터링 메인 루프"""
        while self.monitoring_active:
            try:
                # 시스템 상태 체크
                await self._check_system_health()
                
                # 오류 분석
                await self._analyze_errors()
                
                # 자동 복구 시도
                await self._attempt_auto_recovery()
                
                # 5분마다 체크
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"안정성 모니터링 중 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기
    
    async def _check_system_health(self):
        """시스템 건강 상태 체크"""
        try:
            # 기본 시스템 체크
            health_checks = {
                'disk_space': await self._check_disk_space(),
                'memory_usage': await self._check_memory_usage(),
                'process_status': await self._check_process_status(),
                'network_connectivity': await self._check_network_connectivity()
            }
            
            # 전체 건강 상태 평가
            failed_checks = [k for k, v in health_checks.items() if not v]
            
            if not failed_checks:
                current_health = SystemHealth.HEALTHY
            elif len(failed_checks) <= 1:
                current_health = SystemHealth.WARNING
            else:
                current_health = SystemHealth.CRITICAL
            
            # 상태 변화 로깅
            if hasattr(self, '_last_health') and self._last_health != current_health:
                self.logger.info(f"시스템 건강 상태 변화: {self._last_health.value} -> {current_health.value}")
            
            self._last_health = current_health
            
        except Exception as e:
            self.logger.error(f"시스템 건강 상태 체크 실패: {e}")
    
    async def _check_disk_space(self) -> bool:
        """디스크 공간 체크"""
        try:
            import psutil
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            return free_percent > 10  # 10% 이상 여유 공간 필요
        except Exception:
            return False
    
    async def _check_memory_usage(self) -> bool:
        """메모리 사용률 체크"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent < 90  # 90% 미만 사용률
        except Exception:
            return False
    
    async def _check_process_status(self) -> bool:
        """프로세스 상태 체크"""
        try:
            # 중요 프로세스들이 실행 중인지 확인
            # 실제 구현에서는 특정 프로세스 목록을 체크
            return True
        except Exception:
            return False
    
    async def _check_network_connectivity(self) -> bool:
        """네트워크 연결 상태 체크"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False
    
    async def _analyze_errors(self):
        """오류 분석"""
        try:
            # 최근 1시간 내 오류 수 체크
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_errors = [e for e in self.errors if e.timestamp > one_hour_ago and not e.resolved]
            
            if len(recent_errors) > self.thresholds['max_errors_per_hour']:
                await self._report_error(
                    "high_error_rate",
                    "system",
                    f"최근 1시간 내 {len(recent_errors)}개의 오류 발생",
                    "warning"
                )
            
            # 미해결 오류 수 체크
            unresolved_errors = [e for e in self.errors if not e.resolved]
            if len(unresolved_errors) > self.thresholds['max_unresolved_errors']:
                await self._report_error(
                    "too_many_unresolved_errors",
                    "system",
                    f"{len(unresolved_errors)}개의 미해결 오류 존재",
                    "critical"
                )
            
        except Exception as e:
            self.logger.error(f"오류 분석 실패: {e}")
    
    async def _attempt_auto_recovery(self):
        """자동 복구 시도"""
        try:
            unresolved_errors = [e for e in self.errors if not e.resolved]
            
            for error in unresolved_errors:
                # 복구 액션이 있는 오류에 대해 자동 복구 시도
                if error.recovery_actions:
                    for action in error.recovery_actions:
                        if action in self.recovery_actions:
                            success = await self.recovery_actions[action](error)
                            if success:
                                error.resolved = True
                                error.resolution_time = datetime.now()
                                self.logger.info(f"자동 복구 성공: {error.error_id} - {action}")
                                break
                        
        except Exception as e:
            self.logger.error(f"자동 복구 시도 실패: {e}")
    
    async def report_error(self, component: str, error_type: str, message: str, severity: str = "error") -> str:
        """오류 보고"""
        return await self._report_error(error_type, component, message, severity)
    
    async def _report_error(self, error_type: str, component: str, message: str, severity: str) -> str:
        """내부 오류 보고"""
        try:
            error_id = f"{component}_{error_type}_{datetime.now().timestamp()}"
            
            # 복구 액션 결정
            recovery_actions = self._determine_recovery_actions(error_type, severity)
            
            error = SystemError(
                error_id=error_id,
                component=component,
                error_type=error_type,
                message=message,
                severity=severity,
                timestamp=datetime.now(),
                recovery_actions=recovery_actions
            )
            
            self.errors.append(error)
            self.logger.error(f"오류 보고: {error_id} - {message}")
            
            return error_id
            
        except Exception as e:
            self.logger.error(f"오류 보고 실패: {e}")
            return ""
    
    def _determine_recovery_actions(self, error_type: str, severity: str) -> List[str]:
        """복구 액션 결정"""
        actions = []
        
        if error_type in ['service_failure', 'process_crash']:
            actions.append('restart_service')
        
        if error_type in ['cache_corruption', 'data_inconsistency']:
            actions.append('clear_cache')
        
        if error_type in ['config_error', 'invalid_settings']:
            actions.append('reset_config')
        
        if severity == 'critical':
            actions.append('manual_intervention')
        
        return actions
    
    async def get_stability_metrics(self) -> StabilityMetrics:
        """안정성 메트릭 조회"""
        try:
            uptime = (datetime.now() - self.start_time).total_seconds() / 3600
            unresolved_errors = [e for e in self.errors if not e.resolved]
            resolved_errors = [e for e in self.errors if e.resolved]
            
            last_error = max(self.errors, key=lambda x: x.timestamp) if self.errors else None
            
            # 시스템 건강 상태 결정
            if len(unresolved_errors) == 0:
                health = SystemHealth.HEALTHY
            elif len(unresolved_errors) <= 2:
                health = SystemHealth.WARNING
            else:
                health = SystemHealth.CRITICAL
            
            return StabilityMetrics(
                error_count=len(self.errors),
                recovery_count=len(resolved_errors),
                uptime_hours=uptime,
                last_error_time=last_error.timestamp if last_error else None,
                system_health=health,
                active_issues=len(unresolved_errors)
            )
            
        except Exception as e:
            self.logger.error(f"안정성 메트릭 조회 실패: {e}")
            return StabilityMetrics(
                error_count=0,
                recovery_count=0,
                uptime_hours=0,
                last_error_time=None,
                system_health=SystemHealth.UNKNOWN,
                active_issues=0
            )
    
    # 복구 액션 구현
    async def _restart_service(self, error: SystemError) -> bool:
        """서비스 재시작"""
        try:
            self.logger.info(f"서비스 재시작 시도: {error.component}")
            # 실제 서비스 재시작 로직 구현
            await asyncio.sleep(1)  # 시뮬레이션
            return True
        except Exception as e:
            self.logger.error(f"서비스 재시작 실패: {e}")
            return False
    
    async def _clear_cache(self, error: SystemError) -> bool:
        """캐시 정리"""
        try:
            self.logger.info(f"캐시 정리 시도: {error.component}")
            # 실제 캐시 정리 로직 구현
            await asyncio.sleep(1)  # 시뮬레이션
            return True
        except Exception as e:
            self.logger.error(f"캐시 정리 실패: {e}")
            return False
    
    async def _reset_config(self, error: SystemError) -> bool:
        """설정 초기화"""
        try:
            self.logger.info(f"설정 초기화 시도: {error.component}")
            # 실제 설정 초기화 로직 구현
            await asyncio.sleep(1)  # 시뮬레이션
            return True
        except Exception as e:
            self.logger.error(f"설정 초기화 실패: {e}")
            return False
    
    async def _check_dependencies(self, error: SystemError) -> bool:
        """의존성 체크"""
        try:
            self.logger.info(f"의존성 체크: {error.component}")
            # 실제 의존성 체크 로직 구현
            await asyncio.sleep(1)  # 시뮬레이션
            return True
        except Exception as e:
            self.logger.error(f"의존성 체크 실패: {e}")
            return False
    
    async def _cleanup_resources(self, error: SystemError) -> bool:
        """리소스 정리"""
        try:
            self.logger.info(f"리소스 정리: {error.component}")
            # 실제 리소스 정리 로직 구현
            await asyncio.sleep(1)  # 시뮬레이션
            return True
        except Exception as e:
            self.logger.error(f"리소스 정리 실패: {e}")
            return False

# 싱글톤 인스턴스
_stability_manager_instance = None

def get_stability_manager(base_dir: Optional[str] = None) -> StabilityManager:
    """안정성 관리자 싱글톤 인스턴스 반환"""
    global _stability_manager_instance
    if _stability_manager_instance is None:
        _stability_manager_instance = StabilityManager(base_dir)
    return _stability_manager_instance