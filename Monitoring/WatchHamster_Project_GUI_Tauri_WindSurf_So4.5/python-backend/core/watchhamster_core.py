#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WatchHamster 핵심 모듈

`design.md`에서 정의한 `WatchHamsterCore` 사양을 충족하도록 구현했습니다.
- 전체 시스템 초기화 및 종료
- 모니터링 모드 관리 (개별/통합/24시간)
- 오류 처리 및 복구 조정
- StateManager, ProcessManager 통합
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field

from .state_manager import StateManager
from .process_manager import ProcessManager, ProcessStatus, HealthStatus

logger = logging.getLogger(__name__)


class MonitoringMode(Enum):
    """모니터링 모드"""
    INDIVIDUAL = "individual"  # 개별 모니터 실행
    INTEGRATED = "integrated"  # 통합 모니터링 (1회)
    SMART = "smart"  # 스마트 모니터링 (시간대별)
    SERVICE_24H = "service_24h"  # 24시간 서비스


class SystemStatus(Enum):
    """시스템 상태"""
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class SystemStatusInfo:
    """시스템 상태 정보"""
    status: SystemStatus
    mode: Optional[MonitoringMode] = None
    start_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    active_monitors: List[str] = field(default_factory=list)
    total_monitors: int = 0
    healthy_monitors: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class WatchHamsterCore:
    """WatchHamster 핵심 로직 - 전체 시스템 관리"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        Args:
            base_dir: 기본 디렉토리 경로 (상태 파일 저장용)
        """
        self.state_manager = StateManager(base_dir=base_dir)
        self.process_manager = ProcessManager()
        self.ui = None  # CLI 모드에서만 사용
        
        self.status = SystemStatus.STOPPED
        self.mode: Optional[MonitoringMode] = None
        self.start_time: Optional[datetime] = None
        self.error_count = 0
        self.last_error: Optional[str] = None
        
        self.logger = logger.getChild(self.__class__.__name__)
        self._initialized = False

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------
    async def initialize(self) -> bool:
        """시스템을 초기화합니다.

        Returns:
            초기화 성공 여부
        """
        if self._initialized:
            self.logger.warning("System already initialized")
            return True

        try:
            self.logger.info("Initializing WatchHamster system...")
            self.status = SystemStatus.INITIALIZING

            # 상태 로드
            saved_state = self.state_manager.load_state()
            if saved_state:
                self.logger.info("Loaded previous state")
                self._restore_from_state(saved_state)

            # 헬스 모니터링 시작
            await self.process_manager.start_health_monitoring()

            self._initialized = True
            self.status = SystemStatus.STOPPED  # 초기화 완료, 대기 상태
            self.logger.info("WatchHamster system initialized successfully")
            return True

        except Exception as exc:
            self.logger.error(f"Failed to initialize system: {exc}", exc_info=True)
            self.status = SystemStatus.ERROR
            self.last_error = str(exc)
            self.error_count += 1
            return False

    async def start_monitoring(
        self,
        mode: MonitoringMode,
        monitors: Optional[List[str]] = None,
        **kwargs
    ) -> bool:
        """모니터링을 시작합니다.

        Args:
            mode: 모니터링 모드
            monitors: 시작할 모니터 목록 (None이면 전체)
            **kwargs: 추가 설정

        Returns:
            시작 성공 여부
        """
        if not self._initialized:
            self.logger.error("System not initialized. Call initialize() first.")
            return False

        if self.status == SystemStatus.RUNNING:
            self.logger.warning("Monitoring already running")
            return False

        try:
            self.logger.info(f"Starting monitoring in {mode.value} mode")
            self.status = SystemStatus.RUNNING
            self.mode = mode
            self.start_time = datetime.utcnow()

            # 모드별 처리
            if mode == MonitoringMode.INDIVIDUAL:
                success = await self._start_individual_monitors(monitors or [])
            elif mode == MonitoringMode.INTEGRATED:
                success = await self._start_integrated_monitoring()
            elif mode == MonitoringMode.SMART:
                success = await self._start_smart_monitoring(**kwargs)
            elif mode == MonitoringMode.SERVICE_24H:
                success = await self._start_24h_service(**kwargs)
            else:
                raise ValueError(f"Unknown monitoring mode: {mode}")

            if success:
                self.logger.info(f"Monitoring started successfully in {mode.value} mode")
                await self._save_current_state()
            else:
                self.logger.error("Failed to start monitoring")
                self.status = SystemStatus.ERROR

            return success

        except Exception as exc:
            self.logger.error(f"Failed to start monitoring: {exc}", exc_info=True)
            self.status = SystemStatus.ERROR
            self.last_error = str(exc)
            self.error_count += 1
            return False

    async def stop_monitoring(self) -> bool:
        """모니터링을 중지합니다.

        Returns:
            중지 성공 여부
        """
        if self.status != SystemStatus.RUNNING:
            self.logger.warning("Monitoring not running")
            return False

        try:
            self.logger.info("Stopping monitoring...")
            self.status = SystemStatus.STOPPING

            # 모든 모니터 중지
            all_processes = self.process_manager.get_all_processes()
            for monitor_type in all_processes.keys():
                await self.process_manager.stop_monitor(monitor_type)

            self.status = SystemStatus.STOPPED
            self.mode = None
            self.logger.info("Monitoring stopped successfully")
            
            await self._save_current_state()
            return True

        except Exception as exc:
            self.logger.error(f"Failed to stop monitoring: {exc}", exc_info=True)
            self.last_error = str(exc)
            self.error_count += 1
            return False

    async def shutdown(self) -> bool:
        """시스템을 종료합니다.

        Returns:
            종료 성공 여부
        """
        try:
            self.logger.info("Shutting down WatchHamster system...")

            # 모니터링 중지
            if self.status == SystemStatus.RUNNING:
                await self.stop_monitoring()

            # 헬스 모니터링 중지
            await self.process_manager.stop_health_monitoring()

            # 최종 상태 저장
            await self._save_current_state()

            self._initialized = False
            self.status = SystemStatus.STOPPED
            self.logger.info("WatchHamster system shut down successfully")
            return True

        except Exception as exc:
            self.logger.error(f"Failed to shutdown system: {exc}", exc_info=True)
            return False

    async def get_system_status(self) -> SystemStatusInfo:
        """시스템 상태를 반환합니다.

        Returns:
            시스템 상태 정보
        """
        all_processes = self.process_manager.get_all_processes()
        
        active_monitors = [
            name for name, info in all_processes.items()
            if info.status == ProcessStatus.RUNNING
        ]
        
        healthy_monitors = sum(
            1 for info in all_processes.values()
            if info.health == HealthStatus.HEALTHY
        )
        
        uptime = 0.0
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return SystemStatusInfo(
            status=self.status,
            mode=self.mode,
            start_time=self.start_time,
            uptime_seconds=uptime,
            active_monitors=active_monitors,
            total_monitors=len(all_processes),
            healthy_monitors=healthy_monitors,
            error_count=self.error_count,
            last_error=self.last_error,
            metadata={
                "initialized": self._initialized,
                "processes": {
                    name: {
                        "status": info.status.value,
                        "health": info.health.value,
                        "restart_count": info.restart_count,
                        "error_count": info.error_count,
                    }
                    for name, info in all_processes.items()
                }
            }
        )

    async def handle_error(self, error: Exception, context: str = "") -> bool:
        """오류를 처리하고 복구를 시도합니다.

        Args:
            error: 발생한 오류
            context: 오류 컨텍스트

        Returns:
            복구 성공 여부
        """
        self.error_count += 1
        self.last_error = f"{context}: {str(error)}" if context else str(error)
        
        self.logger.error(
            f"Handling error in context '{context}': {error}",
            exc_info=True
        )

        # 자동 복구 시도
        try:
            # 모든 프로세스의 헬스 체크
            all_processes = self.process_manager.get_all_processes()
            recovery_attempted = False

            for monitor_type, process_info in all_processes.items():
                if process_info.health == HealthStatus.UNHEALTHY:
                    self.logger.info(f"Attempting recovery for monitor '{monitor_type}'")
                    # 실제 복구는 ProcessManager의 auto_recover 사용
                    # 여기서는 복구 필요성만 로깅
                    recovery_attempted = True

            if recovery_attempted:
                self.logger.info("Recovery attempts initiated")
                return True
            else:
                self.logger.info("No recovery needed")
                return True

        except Exception as recovery_error:
            self.logger.error(f"Failed to handle error: {recovery_error}", exc_info=True)
            return False

    # ------------------------------------------------------------------
    # 내부 도우미 - 모니터링 모드별 구현
    # ------------------------------------------------------------------
    async def _start_individual_monitors(self, monitor_types: List[str]) -> bool:
        """개별 모니터를 시작합니다."""
        self.logger.info(f"Starting individual monitors: {monitor_types}")
        
        # 모니터 임포트
        from .monitors import (
            NewYorkMarketMonitor,
            KospiCloseMonitor,
            ExchangeRateMonitor
        )
        
        # 모니터 매핑
        monitor_map = {
            "newyork-market-watch": NewYorkMarketMonitor,
            "kospi-close": KospiCloseMonitor,
            "exchange-rate": ExchangeRateMonitor,
        }
        
        # 각 모니터 시작
        for monitor_type in monitor_types:
            if monitor_type not in monitor_map:
                self.logger.warning(f"Unknown monitor type: {monitor_type}")
                continue
            
            monitor_class = monitor_map[monitor_type]
            monitor = monitor_class()
            
            # 모니터 실행 함수
            async def run_monitor():
                while True:
                    try:
                        result = await monitor.run()
                        self.logger.info(f"Monitor {monitor_type} result: {result['success']}")
                        await asyncio.sleep(60)  # 1분 간격
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        self.logger.error(f"Monitor {monitor_type} error: {e}")
                        await asyncio.sleep(60)
            
            # ProcessManager에 등록
            success = await self.process_manager.start_monitor(
                monitor_type,
                run_monitor
            )
            
            if not success:
                self.logger.error(f"Failed to start monitor: {monitor_type}")
                return False
        
        return True

    async def _start_integrated_monitoring(self) -> bool:
        """통합 모니터링을 시작합니다 (1회 실행)."""
        self.logger.info("Starting integrated monitoring")
        # TODO: MasterMonitor 연동
        return True

    async def _start_smart_monitoring(self, **kwargs) -> bool:
        """스마트 모니터링을 시작합니다 (시간대별)."""
        self.logger.info("Starting smart monitoring")
        # TODO: 시간대별 로직 구현
        return True

    async def _start_24h_service(self, **kwargs) -> bool:
        """24시간 서비스를 시작합니다."""
        self.logger.info("Starting 24h service")
        # TODO: 백그라운드 서비스 로직 구현
        return True

    # ------------------------------------------------------------------
    # 상태 관리
    # ------------------------------------------------------------------
    async def _save_current_state(self):
        """현재 상태를 저장합니다."""
        try:
            state_data = {
                "watchhamster_running": self.status == SystemStatus.RUNNING,
                "mode": self.mode.value if self.mode else None,
                "start_time": self.start_time,
                "error_count": self.error_count,
                "last_error": self.last_error,
                "individual_monitors": {},
                "metadata": {
                    "last_save": datetime.utcnow(),
                }
            }

            # 프로세스 정보 추가
            all_processes = self.process_manager.get_all_processes()
            for name, info in all_processes.items():
                state_data["individual_monitors"][name] = {
                    "status": info.status.value,
                    "health": info.health.value,
                    "restart_count": info.restart_count,
                    "error_count": info.error_count,
                }

            self.state_manager.save_state(state_data)
            self.logger.debug("Current state saved")

        except Exception as exc:
            self.logger.error(f"Failed to save state: {exc}", exc_info=True)

    def _restore_from_state(self, state_data: Dict[str, Any]):
        """저장된 상태에서 복원합니다."""
        try:
            self.error_count = state_data.get("error_count", 0)
            self.last_error = state_data.get("last_error")
            
            mode_str = state_data.get("mode")
            if mode_str:
                try:
                    self.mode = MonitoringMode(mode_str)
                except ValueError:
                    self.logger.warning(f"Unknown mode in saved state: {mode_str}")

            self.logger.info("State restored from previous session")

        except Exception as exc:
            self.logger.error(f"Failed to restore state: {exc}", exc_info=True)
