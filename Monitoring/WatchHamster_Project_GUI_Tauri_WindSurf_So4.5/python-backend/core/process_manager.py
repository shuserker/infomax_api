#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WatchHamster 프로세스 관리 모듈

`design.md`에서 정의한 `ProcessManager` 사양을 충족하도록 구현했습니다.
- 개별 모니터 프로세스 생명주기 관리
- 시작 실패 시 자동 재시도 (최대 3회)
- 헬스 체크 및 자동 복구
- 프로세스 상태 추적 및 로깅
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ProcessStatus(Enum):
    """프로세스 상태"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    RECOVERING = "recovering"


class HealthStatus(Enum):
    """헬스 상태"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProcessInfo:
    """프로세스 정보"""
    monitor_type: str
    status: ProcessStatus = ProcessStatus.STOPPED
    health: HealthStatus = HealthStatus.UNKNOWN
    start_time: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    restart_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProcessManager:
    """프로세스 관리자 - 모니터 프로세스의 생명주기 관리"""

    MAX_RESTART_ATTEMPTS = 3
    HEALTH_CHECK_INTERVAL = 5.0  # seconds
    RESTART_DELAY = 2.0  # seconds
    ERROR_THRESHOLD = 5  # 연속 오류 임계값

    def __init__(self):
        self.processes: Dict[str, ProcessInfo] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.health_check_task: Optional[asyncio.Task] = None
        self.logger = logger.getChild(self.__class__.__name__)
        self._running = False

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------
    async def start_monitor(
        self,
        monitor_type: str,
        start_func: Callable,
        *args,
        **kwargs
    ) -> bool:
        """모니터 프로세스를 시작합니다.

        Args:
            monitor_type: 모니터 타입 (예: "exchange-rate", "newyork-market")
            start_func: 시작할 비동기 함수
            *args, **kwargs: start_func에 전달할 인자

        Returns:
            시작 성공 여부
        """
        if monitor_type in self.processes:
            current_status = self.processes[monitor_type].status
            if current_status in (ProcessStatus.RUNNING, ProcessStatus.STARTING):
                self.logger.warning(f"Monitor '{monitor_type}' is already {current_status.value}")
                return False

        # 프로세스 정보 초기화
        if monitor_type not in self.processes:
            self.processes[monitor_type] = ProcessInfo(monitor_type=monitor_type)

        process_info = self.processes[monitor_type]
        process_info.status = ProcessStatus.STARTING
        process_info.start_time = datetime.utcnow()

        # 재시도 로직
        for attempt in range(self.MAX_RESTART_ATTEMPTS):
            try:
                self.logger.info(
                    f"Starting monitor '{monitor_type}' (attempt {attempt + 1}/{self.MAX_RESTART_ATTEMPTS})"
                )

                # 비동기 태스크 생성
                task = asyncio.create_task(
                    self._run_monitor_with_recovery(monitor_type, start_func, *args, **kwargs)
                )
                self.tasks[monitor_type] = task

                # 짧은 대기 후 상태 확인
                await asyncio.sleep(0.5)

                if not task.done() or not task.exception():
                    process_info.status = ProcessStatus.RUNNING
                    process_info.health = HealthStatus.HEALTHY
                    process_info.restart_count = attempt
                    self.logger.info(f"Monitor '{monitor_type}' started successfully")
                    return True
                else:
                    error = task.exception()
                    raise error if error else Exception("Task completed unexpectedly")

            except Exception as exc:
                process_info.error_count += 1
                process_info.last_error = str(exc)
                self.logger.error(
                    f"Failed to start monitor '{monitor_type}' (attempt {attempt + 1}): {exc}",
                    exc_info=True
                )

                if attempt < self.MAX_RESTART_ATTEMPTS - 1:
                    await asyncio.sleep(self.RESTART_DELAY * (attempt + 1))
                else:
                    process_info.status = ProcessStatus.ERROR
                    process_info.health = HealthStatus.UNHEALTHY
                    return False

        return False

    async def stop_monitor(self, monitor_type: str) -> bool:
        """모니터 프로세스를 중지합니다.

        Args:
            monitor_type: 모니터 타입

        Returns:
            중지 성공 여부
        """
        if monitor_type not in self.processes:
            self.logger.warning(f"Monitor '{monitor_type}' not found")
            return False

        process_info = self.processes[monitor_type]
        process_info.status = ProcessStatus.STOPPING

        # 태스크 취소
        if monitor_type in self.tasks:
            task = self.tasks[monitor_type]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=5.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass

            del self.tasks[monitor_type]

        process_info.status = ProcessStatus.STOPPED
        process_info.health = HealthStatus.UNKNOWN
        self.logger.info(f"Monitor '{monitor_type}' stopped")
        return True

    async def restart_monitor(
        self,
        monitor_type: str,
        start_func: Callable,
        *args,
        **kwargs
    ) -> bool:
        """모니터 프로세스를 재시작합니다.

        Args:
            monitor_type: 모니터 타입
            start_func: 시작할 비동기 함수
            *args, **kwargs: start_func에 전달할 인자

        Returns:
            재시작 성공 여부
        """
        self.logger.info(f"Restarting monitor '{monitor_type}'")
        await self.stop_monitor(monitor_type)
        await asyncio.sleep(1.0)
        return await self.start_monitor(monitor_type, start_func, *args, **kwargs)

    async def check_health(self, monitor_type: str) -> HealthStatus:
        """모니터의 헬스 상태를 확인합니다.

        Args:
            monitor_type: 모니터 타입

        Returns:
            헬스 상태
        """
        if monitor_type not in self.processes:
            return HealthStatus.UNKNOWN

        process_info = self.processes[monitor_type]
        process_info.last_health_check = datetime.utcnow()

        # 프로세스 상태 기반 헬스 체크
        if process_info.status == ProcessStatus.RUNNING:
            # 태스크가 실행 중인지 확인
            if monitor_type in self.tasks:
                task = self.tasks[monitor_type]
                if task.done():
                    if task.exception():
                        process_info.health = HealthStatus.UNHEALTHY
                        process_info.last_error = str(task.exception())
                    else:
                        process_info.health = HealthStatus.DEGRADED
                else:
                    # 오류 카운트 기반 헬스 판단
                    if process_info.error_count >= self.ERROR_THRESHOLD:
                        process_info.health = HealthStatus.UNHEALTHY
                    elif process_info.error_count > 0:
                        process_info.health = HealthStatus.DEGRADED
                    else:
                        process_info.health = HealthStatus.HEALTHY
            else:
                process_info.health = HealthStatus.UNHEALTHY
        elif process_info.status == ProcessStatus.ERROR:
            process_info.health = HealthStatus.UNHEALTHY
        else:
            process_info.health = HealthStatus.UNKNOWN

        return process_info.health

    async def auto_recover(
        self,
        monitor_type: str,
        start_func: Callable,
        *args,
        **kwargs
    ) -> bool:
        """자동 복구를 시도합니다.

        Args:
            monitor_type: 모니터 타입
            start_func: 시작할 비동기 함수
            *args, **kwargs: start_func에 전달할 인자

        Returns:
            복구 성공 여부
        """
        if monitor_type not in self.processes:
            return False

        process_info = self.processes[monitor_type]
        health = await self.check_health(monitor_type)

        if health == HealthStatus.UNHEALTHY:
            self.logger.warning(f"Auto-recovering monitor '{monitor_type}'")
            process_info.status = ProcessStatus.RECOVERING
            success = await self.restart_monitor(monitor_type, start_func, *args, **kwargs)

            if success:
                process_info.error_count = 0
                self.logger.info(f"Monitor '{monitor_type}' recovered successfully")
            else:
                self.logger.error(f"Failed to recover monitor '{monitor_type}'")

            return success

        return False

    def get_process_info(self, monitor_type: str) -> Optional[ProcessInfo]:
        """프로세스 정보를 반환합니다."""
        return self.processes.get(monitor_type)

    def get_all_processes(self) -> Dict[str, ProcessInfo]:
        """모든 프로세스 정보를 반환합니다."""
        return self.processes.copy()

    async def start_health_monitoring(self):
        """헬스 모니터링을 시작합니다."""
        if self.health_check_task and not self.health_check_task.done():
            self.logger.warning("Health monitoring already running")
            return

        self._running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.logger.info("Health monitoring started")

    async def stop_health_monitoring(self):
        """헬스 모니터링을 중지합니다."""
        self._running = False
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Health monitoring stopped")

    # ------------------------------------------------------------------
    # 내부 도우미
    # ------------------------------------------------------------------
    async def _run_monitor_with_recovery(
        self,
        monitor_type: str,
        start_func: Callable,
        *args,
        **kwargs
    ):
        """모니터를 실행하고 오류 발생 시 복구를 시도합니다."""
        try:
            await start_func(*args, **kwargs)
        except asyncio.CancelledError:
            self.logger.info(f"Monitor '{monitor_type}' cancelled")
            raise
        except Exception as exc:
            self.logger.error(f"Monitor '{monitor_type}' error: {exc}", exc_info=True)
            if monitor_type in self.processes:
                self.processes[monitor_type].error_count += 1
                self.processes[monitor_type].last_error = str(exc)
            raise

    async def _health_check_loop(self):
        """주기적으로 모든 프로세스의 헬스를 체크합니다."""
        while self._running:
            try:
                for monitor_type in list(self.processes.keys()):
                    await self.check_health(monitor_type)

                await asyncio.sleep(self.HEALTH_CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Health check loop error: {exc}", exc_info=True)
                await asyncio.sleep(self.HEALTH_CHECK_INTERVAL)
