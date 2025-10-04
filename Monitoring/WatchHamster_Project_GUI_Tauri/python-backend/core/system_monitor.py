#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 시스템 리소스 모니터링 모듈
기존 WatchHamster 프로젝트에서 가져온 실제 모니터링 로직
"""

import psutil
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ResourceLevel(Enum):
    """리소스 사용량 레벨"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class SystemResourceStatus:
    """시스템 리소스 전체 상태"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_status: str
    network_usage: float
    uptime: int
    active_services: int
    overall_level: ResourceLevel
    warnings: List[str]
    critical_issues: List[str]

class RealSystemMonitor:
    """실제 시스템 리소스 모니터링 클래스"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """시스템 모니터 초기화"""
        self.config = config or {}
        self.logger = self._setup_logger()
        
        # 임계값 설정
        self.cpu_warning_threshold = self.config.get('cpu_warning_threshold', 70.0)
        self.cpu_critical_threshold = self.config.get('cpu_critical_threshold', 85.0)
        
        self.memory_warning_threshold = self.config.get('memory_warning_threshold', 70.0)
        self.memory_critical_threshold = self.config.get('memory_critical_threshold', 85.0)
        
        self.disk_warning_threshold = self.config.get('disk_warning_threshold', 80.0)
        self.disk_critical_threshold = self.config.get('disk_critical_threshold', 90.0)
        
        # 모니터링 히스토리
        self.cpu_history = []
        self.memory_history = []
        self.network_history = []
        
        # 마지막 네트워크 통계
        self.last_network_stats = None
        self.last_network_time = None
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('real_system_monitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _determine_resource_level(self, percent: float, resource_type: str) -> ResourceLevel:
        """리소스 사용률에 따른 레벨 결정"""
        if resource_type == 'cpu':
            warning_threshold = self.cpu_warning_threshold
            critical_threshold = self.cpu_critical_threshold
        elif resource_type == 'memory':
            warning_threshold = self.memory_warning_threshold
            critical_threshold = self.memory_critical_threshold
        elif resource_type == 'disk':
            warning_threshold = self.disk_warning_threshold
            critical_threshold = self.disk_critical_threshold
        else:
            return ResourceLevel.NORMAL
        
        if percent >= critical_threshold:
            return ResourceLevel.CRITICAL
        elif percent >= warning_threshold:
            return ResourceLevel.WARNING
        else:
            return ResourceLevel.NORMAL
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """실제 CPU 정보 수집"""
        try:
            # CPU 사용률 (0.1초 간격으로 빠르게 측정)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # 레벨 결정
            level = self._determine_resource_level(cpu_percent, 'cpu')
            
            # 히스토리 업데이트
            self.cpu_history.append({
                'timestamp': datetime.now(),
                'percent': cpu_percent
            })
            
            # 히스토리 크기 제한 (최근 50개)
            if len(self.cpu_history) > 50:
                self.cpu_history = self.cpu_history[-50:]
            
            return {
                'percent': cpu_percent,
                'count': cpu_count,
                'level': level.value,
                'history': [h['percent'] for h in self.cpu_history[-10:]]  # 최근 10개
            }
            
        except Exception as e:
            self.logger.error(f"CPU 정보 수집 중 오류: {e}")
            return {'percent': 0.0, 'count': 1, 'level': 'normal', 'history': []}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """실제 메모리 정보 수집"""
        try:
            # 가상 메모리 정보
            virtual_memory = psutil.virtual_memory()
            
            # 레벨 결정
            level = self._determine_resource_level(virtual_memory.percent, 'memory')
            
            # 히스토리 업데이트
            self.memory_history.append({
                'timestamp': datetime.now(),
                'percent': virtual_memory.percent
            })
            
            # 히스토리 크기 제한
            if len(self.memory_history) > 50:
                self.memory_history = self.memory_history[-50:]
            
            return {
                'total_gb': virtual_memory.total / (1024**3),
                'available_gb': virtual_memory.available / (1024**3),
                'used_gb': virtual_memory.used / (1024**3),
                'percent': virtual_memory.percent,
                'level': level.value,
                'history': [h['percent'] for h in self.memory_history[-10:]]
            }
            
        except Exception as e:
            self.logger.error(f"메모리 정보 수집 중 오류: {e}")
            return {'percent': 0.0, 'level': 'normal', 'history': []}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """실제 디스크 정보 수집"""
        try:
            # 홈 디렉토리 기준으로 디스크 사용량 확인
            import os
            home_path = os.path.expanduser('~')
            
            try:
                disk_usage = psutil.disk_usage(home_path)
            except:
                # 홈 디렉토리 접근 실패 시 루트 사용
                disk_usage = psutil.disk_usage('/')
            
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            # 레벨 결정
            level = self._determine_resource_level(disk_percent, 'disk')
            
            return {
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'percent': disk_percent,
                'level': level.value
            }
            
        except Exception as e:
            self.logger.error(f"디스크 정보 수집 중 오류: {e}")
            return {'percent': 0.0, 'level': 'normal'}
    
    def get_network_info(self) -> Dict[str, Any]:
        """실제 네트워크 정보 수집"""
        try:
            import socket
            
            # 인터넷 연결 확인
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                network_status = "connected"
            except:
                network_status = "disconnected"
            
            # 네트워크 I/O 통계
            network_io = psutil.net_io_counters()
            current_time = time.time()
            
            # 네트워크 사용률 계산 (이전 측정값과 비교)
            network_usage_percent = 0.0
            
            if self.last_network_stats and self.last_network_time:
                time_diff = current_time - self.last_network_time
                bytes_diff = (network_io.bytes_sent + network_io.bytes_recv) - \
                           (self.last_network_stats.bytes_sent + self.last_network_stats.bytes_recv)
                
                if time_diff > 0:
                    # bytes/sec 계산
                    bytes_per_sec = bytes_diff / time_diff
                    # 100Mbps 기준으로 퍼센트 계산 (대략적)
                    max_bandwidth = 100 * 1024 * 1024 / 8  # 100Mbps in bytes/sec
                    network_usage_percent = min((bytes_per_sec / max_bandwidth) * 100, 100)
            
            # 현재 통계 저장
            self.last_network_stats = network_io
            self.last_network_time = current_time
            
            return {
                'status': network_status,
                'usage_percent': network_usage_percent,
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
            
        except Exception as e:
            self.logger.error(f"네트워크 정보 수집 중 오류: {e}")
            return {'status': 'unknown', 'usage_percent': 0.0}
    
    def get_system_uptime(self) -> int:
        """시스템 업타임 반환 (초 단위)"""
        try:
            boot_time = psutil.boot_time()
            current_time = time.time()
            return int(current_time - boot_time)
        except:
            return 0
    
    def get_active_services_count(self) -> int:
        """활성 프로세스 수 반환"""
        try:
            return len([p for p in psutil.process_iter() if p.is_running()])
        except:
            return 0
    
    def get_system_status(self) -> SystemResourceStatus:
        """전체 시스템 상태 수집"""
        try:
            cpu_info = self.get_cpu_info()
            memory_info = self.get_memory_info()
            disk_info = self.get_disk_info()
            network_info = self.get_network_info()
            
            # 전체 레벨 결정 (가장 높은 경고 레벨 사용)
            levels = [
                ResourceLevel(cpu_info['level']),
                ResourceLevel(memory_info['level']),
                ResourceLevel(disk_info['level'])
            ]
            
            overall_level = max(levels, key=lambda x: ['normal', 'warning', 'critical', 'emergency'].index(x.value))
            
            # 경고 및 중요 이슈 수집
            warnings = []
            critical_issues = []
            
            if cpu_info['level'] == 'warning':
                warnings.append(f"CPU 사용률 높음: {cpu_info['percent']:.1f}%")
            elif cpu_info['level'] == 'critical':
                critical_issues.append(f"CPU 사용률 위험: {cpu_info['percent']:.1f}%")
            
            if memory_info['level'] == 'warning':
                warnings.append(f"메모리 사용률 높음: {memory_info['percent']:.1f}%")
            elif memory_info['level'] == 'critical':
                critical_issues.append(f"메모리 사용률 위험: {memory_info['percent']:.1f}%")
            
            if disk_info['level'] == 'warning':
                warnings.append(f"디스크 사용률 높음: {disk_info['percent']:.1f}%")
            elif disk_info['level'] == 'critical':
                critical_issues.append(f"디스크 사용률 위험: {disk_info['percent']:.1f}%")
            
            if network_info['status'] != 'connected':
                critical_issues.append("네트워크 연결 끊김")
            
            return SystemResourceStatus(
                timestamp=datetime.now(),
                cpu_percent=cpu_info['percent'],
                memory_percent=memory_info['percent'],
                disk_usage=disk_info['percent'],
                network_status=network_info['status'],
                network_usage=network_info['usage_percent'],
                uptime=self.get_system_uptime(),
                active_services=self.get_active_services_count(),
                overall_level=overall_level,
                warnings=warnings,
                critical_issues=critical_issues
            )
            
        except Exception as e:
            self.logger.error(f"시스템 상태 수집 중 오류: {e}")
            return SystemResourceStatus(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage=0.0,
                network_status="unknown",
                network_usage=0.0,
                uptime=0,
                active_services=0,
                overall_level=ResourceLevel.NORMAL,
                warnings=[],
                critical_issues=["시스템 모니터링 오류"]
            )

# 전역 모니터 인스턴스
_system_monitor = None

def get_system_monitor() -> RealSystemMonitor:
    """시스템 모니터 싱글톤 인스턴스 반환"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = RealSystemMonitor()
    return _system_monitor