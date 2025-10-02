#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시스템 리소스 모니터링 모듈

시스템의 CPU, 메모리, 디스크, 네트워크 등의 리소스를 모니터링하고
임계값에 따른 경고 레벨을 제공하는 공통 모듈입니다.

Requirements: 3.1, 3.2
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
class CPUInfo:
    """CPU 정보"""
    percent: float
    count: int
    frequency: Optional[float] = None
    level: ResourceLevel = ResourceLevel.NORMAL
    per_cpu: List[float] = None
    
    def __post_init__(self):
        if self.per_cpu is None:
            self.per_cpu = []

@dataclass
class MemoryInfo:
    """메모리 정보"""
    total_gb: float
    available_gb: float
    used_gb: float
    percent: float
    level: ResourceLevel = ResourceLevel.NORMAL
    swap_total_gb: float = 0.0
    swap_used_gb: float = 0.0
    swap_percent: float = 0.0

@dataclass
class DiskInfo:
    """디스크 정보"""
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float
    level: ResourceLevel = ResourceLevel.NORMAL
    mount_point: str = "/"

@dataclass
class NetworkInfo:
    """네트워크 정보"""
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int = 0
    errors_out: int = 0
    drops_in: int = 0
    drops_out: int = 0

@dataclass
class ProcessInfo:
    """프로세스 정보"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    create_time: datetime
    cmdline: List[str] = None
    
    def __post_init__(self):
        if self.cmdline is None:
            self.cmdline = []

@dataclass
class SystemResourceStatus:
    """시스템 리소스 전체 상태"""
    timestamp: datetime
    cpu: CPUInfo
    memory: MemoryInfo
    disk: DiskInfo
    network: NetworkInfo
    overall_level: ResourceLevel
    warnings: List[str]
    critical_issues: List[str]
    top_processes: List[ProcessInfo]

class SystemMonitor:
    """시스템 리소스 모니터링 클래스"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        시스템 모니터 초기화
        
        Args:
            config: 모니터링 설정
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        
        # 임계값 설정
        self.cpu_warning_threshold = self.config.get('cpu_warning_threshold', 70.0)
        self.cpu_critical_threshold = self.config.get('cpu_critical_threshold', 85.0)
        self.cpu_emergency_threshold = self.config.get('cpu_emergency_threshold', 95.0)
        
        self.memory_warning_threshold = self.config.get('memory_warning_threshold', 70.0)
        self.memory_critical_threshold = self.config.get('memory_critical_threshold', 85.0)
        self.memory_emergency_threshold = self.config.get('memory_emergency_threshold', 95.0)
        
        self.disk_warning_threshold = self.config.get('disk_warning_threshold', 80.0)
        self.disk_critical_threshold = self.config.get('disk_critical_threshold', 90.0)
        self.disk_emergency_threshold = self.config.get('disk_emergency_threshold', 98.0)
        
        # 모니터링 히스토리
        self.cpu_history = []
        self.memory_history = []
        self.network_history = []
        
        # 마지막 네트워크 통계
        self.last_network_stats = None
        self.last_network_time = None
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('system_monitor')
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
            emergency_threshold = self.cpu_emergency_threshold
        elif resource_type == 'memory':
            warning_threshold = self.memory_warning_threshold
            critical_threshold = self.memory_critical_threshold
            emergency_threshold = self.memory_emergency_threshold
        elif resource_type == 'disk':
            warning_threshold = self.disk_warning_threshold
            critical_threshold = self.disk_critical_threshold
            emergency_threshold = self.disk_emergency_threshold
        else:
            return ResourceLevel.NORMAL
        
        if percent >= emergency_threshold:
            return ResourceLevel.EMERGENCY
        elif percent >= critical_threshold:
            return ResourceLevel.CRITICAL
        elif percent >= warning_threshold:
            return ResourceLevel.WARNING
        else:
            return ResourceLevel.NORMAL
    
    def get_cpu_info(self) -> CPUInfo:
        """CPU 정보 수집"""
        try:
            # CPU 사용률 (1초 간격으로 측정)
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # CPU 주파수 정보 (가능한 경우)
            try:
                cpu_freq = psutil.cpu_freq()
                frequency = cpu_freq.current if cpu_freq else None
            except (AttributeError, OSError):
                frequency = None
            
            # 코어별 CPU 사용률
            try:
                per_cpu = psutil.cpu_percent(percpu=True)
            except:
                per_cpu = []
            
            # 레벨 결정
            level = self._determine_resource_level(cpu_percent, 'cpu')
            
            cpu_info = CPUInfo(
                percent=cpu_percent,
                count=cpu_count,
                frequency=frequency,
                level=level,
                per_cpu=per_cpu
            )
            
            # 히스토리 업데이트
            self.cpu_history.append({
                'timestamp': datetime.now(),
                'percent': cpu_percent
            })
            
            # 히스토리 크기 제한 (최근 100개)
            if len(self.cpu_history) > 100:
                self.cpu_history = self.cpu_history[-100:]
            
            return cpu_info
            
        except Exception as e:
            self.logger.error(f"CPU 정보 수집 중 오류: {e}")
            return CPUInfo(percent=0.0, count=1, level=ResourceLevel.NORMAL)
    
    def get_memory_info(self) -> MemoryInfo:
        """메모리 정보 수집"""
        try:
            # 가상 메모리 정보
            virtual_memory = psutil.virtual_memory()
            
            # 스왑 메모리 정보
            try:
                swap_memory = psutil.swap_memory()
                swap_total_gb = swap_memory.total / (1024**3)
                swap_used_gb = swap_memory.used / (1024**3)
                swap_percent = swap_memory.percent
            except:
                swap_total_gb = 0.0
                swap_used_gb = 0.0
                swap_percent = 0.0
            
            # 레벨 결정
            level = self._determine_resource_level(virtual_memory.percent, 'memory')
            
            memory_info = MemoryInfo(
                total_gb=virtual_memory.total / (1024**3),
                available_gb=virtual_memory.available / (1024**3),
                used_gb=virtual_memory.used / (1024**3),
                percent=virtual_memory.percent,
                level=level,
                swap_total_gb=swap_total_gb,
                swap_used_gb=swap_used_gb,
                swap_percent=swap_percent
            )
            
            # 히스토리 업데이트
            self.memory_history.append({
                'timestamp': datetime.now(),
                'percent': virtual_memory.percent,
                'available_gb': memory_info.available_gb
            })
            
            # 히스토리 크기 제한
            if len(self.memory_history) > 100:
                self.memory_history = self.memory_history[-100:]
            
            return memory_info
            
        except Exception as e:
            self.logger.error(f"메모리 정보 수집 중 오류: {e}")
            return MemoryInfo(
                total_gb=0.0, available_gb=0.0, used_gb=0.0, 
                percent=0.0, level=ResourceLevel.NORMAL
            )
    
    def get_disk_info(self, mount_point: str = "/") -> DiskInfo:
        """디스크 정보 수집"""
        try:
            disk_usage = psutil.disk_usage(mount_point)
            
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0.0
            
            # 레벨 결정
            level = self._determine_resource_level(percent, 'disk')
            
            return DiskInfo(
                total_gb=total_gb,
                used_gb=used_gb,
                free_gb=free_gb,
                percent=percent,
                level=level,
                mount_point=mount_point
            )
            
        except Exception as e:
            self.logger.error(f"디스크 정보 수집 중 오류: {e}")
            return DiskInfo(
                total_gb=0.0, used_gb=0.0, free_gb=0.0,
                percent=0.0, level=ResourceLevel.NORMAL, mount_point=mount_point
            )
    
    def get_network_info(self) -> NetworkInfo:
        """네트워크 정보 수집"""
        try:
            network_stats = psutil.net_io_counters()
            
            network_info = NetworkInfo(
                bytes_sent=network_stats.bytes_sent,
                bytes_recv=network_stats.bytes_recv,
                packets_sent=network_stats.packets_sent,
                packets_recv=network_stats.packets_recv,
                errors_in=getattr(network_stats, 'errin', 0),
                errors_out=getattr(network_stats, 'errout', 0),
                drops_in=getattr(network_stats, 'dropin', 0),
                drops_out=getattr(network_stats, 'dropout', 0)
            )
            
            # 네트워크 속도 계산을 위한 히스토리 업데이트
            current_time = datetime.now()
            if self.last_network_stats and self.last_network_time:
                time_diff = (current_time - self.last_network_time).total_seconds()
                if time_diff > 0:
                    bytes_sent_per_sec = (network_stats.bytes_sent - self.last_network_stats.bytes_sent) / time_diff
                    bytes_recv_per_sec = (network_stats.bytes_recv - self.last_network_stats.bytes_recv) / time_diff
                    
                    self.network_history.append({
                        'timestamp': current_time,
                        'bytes_sent_per_sec': bytes_sent_per_sec,
                        'bytes_recv_per_sec': bytes_recv_per_sec
                    })
            
            self.last_network_stats = network_stats
            self.last_network_time = current_time
            
            # 히스토리 크기 제한
            if len(self.network_history) > 100:
                self.network_history = self.network_history[-100:]
            
            return network_info
            
        except Exception as e:
            self.logger.error(f"네트워크 정보 수집 중 오류: {e}")
            return NetworkInfo(
                bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0
            )
    
    def get_top_processes(self, limit: int = 10) -> List[ProcessInfo]:
        """CPU 사용률이 높은 상위 프로세스 목록"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time', 'cmdline']):
                try:
                    # CPU 사용률 측정 (짧은 간격)
                    cpu_percent = proc.cpu_percent()
                    
                    # 메모리 사용량 계산
                    memory_info = proc.info.get('memory_info')
                    memory_mb = memory_info.rss / (1024*1024) if memory_info else 0.0
                    
                    # 생성 시간
                    create_time = datetime.fromtimestamp(proc.info['create_time'])
                    
                    process_info = ProcessInfo(
                        pid=proc.info['pid'],
                        name=proc.info['name'] or 'Unknown',
                        cpu_percent=cpu_percent,
                        memory_percent=proc.info.get('memory_percent', 0.0),
                        memory_mb=memory_mb,
                        status=proc.info.get('status', 'unknown'),
                        create_time=create_time,
                        cmdline=proc.info.get('cmdline', [])
                    )
                    
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # CPU 사용률 기준으로 정렬
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            
            return processes[:limit]
            
        except Exception as e:
            self.logger.error(f"프로세스 정보 수집 중 오류: {e}")
            return []
    
    def get_system_resource_status(self) -> SystemResourceStatus:
        """전체 시스템 리소스 상태 수집"""
        try:
            timestamp = datetime.now()
            
            # 각 리소스 정보 수집
            cpu_info = self.get_cpu_info()
            memory_info = self.get_memory_info()
            disk_info = self.get_disk_info()
            network_info = self.get_network_info()
            top_processes = self.get_top_processes()
            
            # 경고 및 중요 이슈 수집
            warnings = []
            critical_issues = []
            
            # CPU 관련 경고
            if cpu_info.level == ResourceLevel.WARNING:
                warnings.append(f"CPU 사용률 주의: {cpu_info.percent:.1f}%")
            elif cpu_info.level == ResourceLevel.CRITICAL:
                critical_issues.append(f"CPU 사용률 높음: {cpu_info.percent:.1f}%")
            elif cpu_info.level == ResourceLevel.EMERGENCY:
                critical_issues.append(f"CPU 사용률 위험: {cpu_info.percent:.1f}%")
            
            # 메모리 관련 경고
            if memory_info.level == ResourceLevel.WARNING:
                warnings.append(f"메모리 사용률 주의: {memory_info.percent:.1f}%")
            elif memory_info.level == ResourceLevel.CRITICAL:
                critical_issues.append(f"메모리 사용률 높음: {memory_info.percent:.1f}%")
            elif memory_info.level == ResourceLevel.EMERGENCY:
                critical_issues.append(f"메모리 사용률 위험: {memory_info.percent:.1f}%")
            
            # 디스크 관련 경고
            if disk_info.level == ResourceLevel.WARNING:
                warnings.append(f"디스크 사용률 주의: {disk_info.percent:.1f}%")
            elif disk_info.level == ResourceLevel.CRITICAL:
                critical_issues.append(f"디스크 사용률 높음: {disk_info.percent:.1f}%")
            elif disk_info.level == ResourceLevel.EMERGENCY:
                critical_issues.append(f"디스크 사용률 위험: {disk_info.percent:.1f}%")
            
            # 전체 레벨 결정
            levels = [cpu_info.level, memory_info.level, disk_info.level]
            
            if ResourceLevel.EMERGENCY in levels:
                overall_level = ResourceLevel.EMERGENCY
            elif ResourceLevel.CRITICAL in levels:
                overall_level = ResourceLevel.CRITICAL
            elif ResourceLevel.WARNING in levels:
                overall_level = ResourceLevel.WARNING
            else:
                overall_level = ResourceLevel.NORMAL
            
            return SystemResourceStatus(
                timestamp=timestamp,
                cpu=cpu_info,
                memory=memory_info,
                disk=disk_info,
                network=network_info,
                overall_level=overall_level,
                warnings=warnings,
                critical_issues=critical_issues,
                top_processes=top_processes
            )
            
        except Exception as e:
            self.logger.error(f"시스템 리소스 상태 수집 중 오류: {e}")
            # 오류 발생 시 기본값 반환
            return SystemResourceStatus(
                timestamp=datetime.now(),
                cpu=CPUInfo(percent=0.0, count=1),
                memory=MemoryInfo(total_gb=0.0, available_gb=0.0, used_gb=0.0, percent=0.0),
                disk=DiskInfo(total_gb=0.0, used_gb=0.0, free_gb=0.0, percent=0.0),
                network=NetworkInfo(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0),
                overall_level=ResourceLevel.CRITICAL,
                warnings=[],
                critical_issues=[f"시스템 모니터링 오류: {str(e)}"],
                top_processes=[]
            )
    
    def generate_resource_alert(self, status: SystemResourceStatus, alert_type: str = "status") -> str:
        """리소스 상태 기반 알림 메시지 생성"""
        try:
            timestamp = status.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # 알림 헤더 결정
            if alert_type == "critical":
                header = "🚨 시스템 리소스 긴급 알림"
            elif alert_type == "warning":
                header = "⚠️ 시스템 리소스 경고"
            else:
                header = "📊 시스템 리소스 상태"
            
            message_parts = [
                f"{header}\n",
                f"⏰ 시간: {timestamp}\n",
                f"🎯 전체 상태: {status.overall_level.value}\n\n"
            ]
            
            # 리소스 상세 정보
            message_parts.append("💻 시스템 리소스:\n")
            message_parts.append(f"  • CPU: {status.cpu.percent:.1f}% ({status.cpu.count}코어)\n")
            message_parts.append(f"  • 메모리: {status.memory.percent:.1f}% ({status.memory.available_gb:.1f}GB 사용가능)\n")
            message_parts.append(f"  • 디스크: {status.disk.percent:.1f}% ({status.disk.free_gb:.1f}GB 여유)\n")
            
            # 경고 사항
            if status.warnings:
                message_parts.append(f"\n⚠️ 경고 사항 ({len(status.warnings)}개):\n")
                for warning in status.warnings:
                    message_parts.append(f"  • {warning}\n")
            
            # 중요 이슈
            if status.critical_issues:
                message_parts.append(f"\n🚨 중요 이슈 ({len(status.critical_issues)}개):\n")
                for issue in status.critical_issues:
                    message_parts.append(f"  • {issue}\n")
            
            # 상위 프로세스 (CPU 사용률 높은 경우만)
            if status.cpu.percent > 50 and status.top_processes:
                message_parts.append(f"\n🔥 상위 프로세스 (CPU 사용률):\n")
                for i, proc in enumerate(status.top_processes[:3], 1):
                    message_parts.append(f"  {i}. {proc.name} ({proc.cpu_percent:.1f}%)\n")
            
            return "".join(message_parts).rstrip()
            
        except Exception as e:
            self.logger.error(f"리소스 알림 메시지 생성 중 오류: {e}")
            return (f"📊 시스템 리소스 상태\n\n"
                   f"⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                   f"❌ 메시지 생성 오류: {str(e)}")
    
    def get_resource_history(self, resource_type: str, minutes: int = 60) -> List[Dict]:
        """리소스 사용 히스토리 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            if resource_type == 'cpu':
                history = self.cpu_history
            elif resource_type == 'memory':
                history = self.memory_history
            elif resource_type == 'network':
                history = self.network_history
            else:
                return []
            
            # 지정된 시간 이후의 데이터만 반환
            filtered_history = [
                entry for entry in history 
                if entry['timestamp'] >= cutoff_time
            ]
            
            return filtered_history
            
        except Exception as e:
            self.logger.error(f"리소스 히스토리 조회 중 오류: {e}")
            return []
    
    def check_resource_trends(self, minutes: int = 30) -> Dict[str, str]:
        """리소스 사용 트렌드 분석"""
        try:
            trends = {}
            
            # CPU 트렌드
            cpu_history = self.get_resource_history('cpu', minutes)
            if len(cpu_history) >= 2:
                recent_avg = sum(entry['percent'] for entry in cpu_history[-5:]) / min(5, len(cpu_history))
                older_avg = sum(entry['percent'] for entry in cpu_history[:5]) / min(5, len(cpu_history))
                
                if recent_avg > older_avg + 10:
                    trends['cpu'] = 'increasing'
                elif recent_avg < older_avg - 10:
                    trends['cpu'] = 'decreasing'
                else:
                    trends['cpu'] = 'stable'
            else:
                trends['cpu'] = 'insufficient_data'
            
            # 메모리 트렌드
            memory_history = self.get_resource_history('memory', minutes)
            if len(memory_history) >= 2:
                recent_avg = sum(entry['percent'] for entry in memory_history[-5:]) / min(5, len(memory_history))
                older_avg = sum(entry['percent'] for entry in memory_history[:5]) / min(5, len(memory_history))
                
                if recent_avg > older_avg + 5:
                    trends['memory'] = 'increasing'
                elif recent_avg < older_avg - 5:
                    trends['memory'] = 'decreasing'
                else:
                    trends['memory'] = 'stable'
            else:
                trends['memory'] = 'insufficient_data'
            
            return trends
            
        except Exception as e:
            self.logger.error(f"리소스 트렌드 분석 중 오류: {e}")
            return {}

def main():
    """테스트 실행"""
    monitor = SystemMonitor()
    
    print("=== 시스템 리소스 모니터링 테스트 ===")
    
    # 전체 시스템 상태 확인
    status = monitor.get_system_resource_status()
    
    print(f"\n📊 시스템 상태: {status.overall_level.value}")
    print(f"💻 CPU: {status.cpu.percent:.1f}% ({status.cpu.count}코어)")
    print(f"🧠 메모리: {status.memory.percent:.1f}% ({status.memory.available_gb:.1f}GB 사용가능)")
    print(f"💾 디스크: {status.disk.percent:.1f}% ({status.disk.free_gb:.1f}GB 여유)")
    
    if status.warnings:
        print(f"\n⚠️ 경고: {', '.join(status.warnings)}")
    
    if status.critical_issues:
        print(f"\n🚨 중요 이슈: {', '.join(status.critical_issues)}")
    
    # 상위 프로세스
    if status.top_processes:
        print(f"\n🔥 상위 프로세스 (CPU 사용률):")
        for i, proc in enumerate(status.top_processes[:5], 1):
            print(f"  {i}. {proc.name} (PID: {proc.pid}, CPU: {proc.cpu_percent:.1f}%, 메모리: {proc.memory_mb:.1f}MB)")
    
    # 알림 메시지 생성
    alert_message = monitor.generate_resource_alert(status)
    print(f"\n📨 알림 메시지:\n{alert_message}")

if __name__ == "__main__":
    main()