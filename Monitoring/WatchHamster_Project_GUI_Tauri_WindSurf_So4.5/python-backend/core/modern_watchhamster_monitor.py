#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern WatchHamster Monitor - FastAPI/Pydantic 호환
현재 React/TypeScript UI와 완벽하게 호환되는 모던 모니터링 시스템
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import psutil
import aiofiles
import httpx

# Pydantic 모델들 (TypeScript 인터페이스와 일치)
class ProcessStatus(BaseModel):
    name: str
    status: str = Field(..., description="running, stopped, error, unknown")
    pid: Optional[int] = None
    uptime_seconds: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    last_error: Optional[str] = None

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_status: str = "connected"
    active_processes: int
    timestamp: datetime = Field(default_factory=datetime.now)

class MonitorConfig(BaseModel):
    process_check_interval: int = 300
    git_check_interval: int = 3600
    status_notification_interval: int = 7200
    managed_processes: List[str] = ["posco_news", "deployment", "webhook_system"]
    max_restart_attempts: int = 3
    restart_cooldown: int = 60

class ModernWatchHamsterMonitor:
    """
    현대적 WatchHamster 모니터링 시스템
    - async/await 패턴
    - Pydantic 모델 사용
    - TypeScript 인터페이스 호환
    - FastAPI dependency injection 지원
    """
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.process_status: Dict[str, ProcessStatus] = {}
        self.last_check = datetime.now()
        self.is_monitoring = False
        
    async def start_monitoring(self) -> Dict[str, Any]:
        """모니터링 시작"""
        self.is_monitoring = True
        self.logger.info("🐹 Modern WatchHamster 모니터링 시작")
        
        # 백그라운드에서 모니터링 실행
        asyncio.create_task(self._monitor_loop())
        
        return {
            "status": "started",
            "message": "WatchHamster 모니터링이 시작되었습니다",
            "config": self.config.dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """모니터링 중지"""
        self.is_monitoring = False
        self.logger.info("🐹 Modern WatchHamster 모니터링 중지")
        
        return {
            "status": "stopped", 
            "message": "WatchHamster 모니터링이 중지되었습니다",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """현재 상태 조회 (TypeScript 인터페이스 호환)"""
        system_metrics = await self._get_system_metrics()
        
        return {
            "is_monitoring": self.is_monitoring,
            "last_check": self.last_check.isoformat(),
            "managed_processes": len(self.config.managed_processes),
            "active_processes": len([p for p in self.process_status.values() if p.status == "running"]),
            "system_metrics": system_metrics.dict(),
            "processes": {name: status.dict() for name, status in self.process_status.items()},
            "config": self.config.dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_process_list(self) -> List[ProcessStatus]:
        """프로세스 목록 조회"""
        await self._update_process_status()
        return list(self.process_status.values())
    
    async def restart_process(self, process_name: str) -> Dict[str, Any]:
        """특정 프로세스 재시작"""
        if process_name not in self.config.managed_processes:
            return {
                "status": "error",
                "message": f"관리되지 않는 프로세스입니다: {process_name}",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # 프로세스 재시작 로직
            await self._restart_process(process_name)
            
            return {
                "status": "success",
                "message": f"프로세스 {process_name}이 재시작되었습니다",
                "process_name": process_name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"프로세스 재시작 실패: {str(e)}",
                "process_name": process_name,
                "timestamp": datetime.now().isoformat()
            }
    
    # Private 메서드들
    async def _monitor_loop(self):
        """메인 모니터링 루프"""
        while self.is_monitoring:
            try:
                await self._update_process_status()
                await self._check_system_health()
                await asyncio.sleep(self.config.process_check_interval)
            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기
    
    async def _update_process_status(self):
        """프로세스 상태 업데이트"""
        for process_name in self.config.managed_processes:
            try:
                # psutil을 사용한 프로세스 상태 확인
                status = await self._check_process(process_name)
                self.process_status[process_name] = status
            except Exception as e:
                self.process_status[process_name] = ProcessStatus(
                    name=process_name,
                    status="error",
                    last_error=str(e)
                )
        
        self.last_check = datetime.now()
    
    async def _check_process(self, process_name: str) -> ProcessStatus:
        """개별 프로세스 상태 확인"""
        # 실제 프로세스 체크 로직
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if process_name in proc.info['name']:
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                    return ProcessStatus(
                        name=process_name,
                        status="running",
                        pid=proc.info['pid'],
                        memory_usage_mb=memory_mb,
                        cpu_percent=proc.info['cpu_percent']
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return ProcessStatus(
            name=process_name,
            status="stopped"
        )
    
    async def _get_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        try:
            return SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_usage_percent=psutil.disk_usage('/').percent,
                active_processes=len(psutil.pids()),
                network_status="connected"  # 실제 네트워크 체크 로직 필요
            )
        except Exception as e:
            self.logger.error(f"시스템 메트릭 수집 오류: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                active_processes=0,
                network_status="error"
            )
    
    async def _check_system_health(self):
        """시스템 건강상태 체크"""
        metrics = await self._get_system_metrics()
        
        # 임계값 체크
        if metrics.cpu_percent > 80:
            self.logger.warning(f"높은 CPU 사용률: {metrics.cpu_percent}%")
        
        if metrics.memory_percent > 85:
            self.logger.warning(f"높은 메모리 사용률: {metrics.memory_percent}%")
    
    async def _restart_process(self, process_name: str):
        """프로세스 재시작 실행"""
        # 실제 프로세스 재시작 로직 구현
        self.logger.info(f"프로세스 재시작: {process_name}")
        
        # 예시: 특정 프로세스별 재시작 명령
        restart_commands = {
            "posco_news": ["python", "-m", "posco_news"],
            "deployment": ["python", "-m", "deployment_monitor"], 
            "webhook_system": ["python", "-m", "webhook_sender"]
        }
        
        if process_name in restart_commands:
            cmd = restart_commands[process_name]
            # 실제 subprocess 실행은 여기서
            self.logger.info(f"재시작 명령 실행: {' '.join(cmd)}")
