"""
시스템 메트릭 API 엔드포인트
포팅된 성능 최적화 및 안정성 관리 로직 사용
"""

import logging
import psutil
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# 시스템 모니터링을 위한 기본 모듈들 (안정성 우선)
# from core.system_monitor import get_system_monitor, RealSystemMonitor  # 필요시 활성화

logger = logging.getLogger(__name__)
router = APIRouter()

# 데이터 모델
class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_status: str
    network_usage: float  # 네트워크 사용률 (%)
    network_speed_mbps: float  # 네트워크 속도 (Mbps)
    uptime: int
    active_services: int
    timestamp: str

class PerformanceMetrics(BaseModel):
    cpu_usage: List[float]
    memory_usage: List[float]
    disk_io: Dict[str, Any]
    network_io: Dict[str, Any]
    timestamps: List[str]

class StabilityMetrics(BaseModel):
    error_count: int
    recovery_count: int
    last_health_check: str
    system_health: str  # healthy, warning, critical
    service_failures: List[Dict[str, Any]]

# 메트릭 히스토리 저장 (실제로는 데이터베이스 사용)
metrics_history = []

@router.get("/", response_model=SystemMetrics)
async def get_system_metrics():
    """현재 시스템 메트릭 조회 - 직접 psutil 사용으로 안정성 확보"""
    logger.info("시스템 메트릭 조회 요청")
    
    try:
        # 직접 psutil로 시스템 메트릭 수집 (안정성 우선)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # 디스크 사용량 (크로스 플랫폼 호환)
        try:
            disk_usage = psutil.disk_usage('/').percent
        except:
            try:
                disk_usage = psutil.disk_usage('C:\\').percent
            except:
                disk_usage = 0.0
        
        # 네트워크 상태
        network_status = "connected"
        network_usage = 0.0
        try:
            net_io = psutil.net_io_counters()
            if net_io and (net_io.bytes_sent > 0 or net_io.bytes_recv > 0):
                network_status = "active"
                # 간단한 네트워크 사용률 계산 (0-100%)
                network_usage = min(50.0, (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024) % 100)
        except:
            network_status = "unknown"
        
        # 시스템 업타임
        try:
            boot_time = psutil.boot_time()
            uptime = int(time.time() - boot_time)
        except:
            uptime = 0
        
        # 활성 서비스 수 (프로세스 수로 대체)
        try:
            active_services = len(psutil.pids())
        except:
            active_services = 0
        
        metrics = SystemMetrics(
            cpu_percent=round(cpu_percent, 1),
            memory_percent=round(memory.percent, 1),
            disk_usage=round(disk_usage, 1),
            network_status=network_status,
            network_usage=round(network_usage, 1),
            network_speed_mbps=round(network_usage / 10.0, 1),  # 간단한 변환
            uptime=uptime,
            active_services=min(active_services, 999),  # UI 표시 제한
            timestamp=datetime.now().isoformat()
        )
        
        # 히스토리에 추가 (최대 100개 유지)
        metrics_history.append(metrics)
        if len(metrics_history) > 100:
            metrics_history.pop(0)
        
        # 경고 상황 체크
        warnings = []
        if cpu_percent > 80:
            warnings.append(f"높은 CPU 사용률: {cpu_percent:.1f}%")
        if memory.percent > 85:
            warnings.append(f"높은 메모리 사용률: {memory.percent:.1f}%")
        if disk_usage > 90:
            warnings.append(f"높은 디스크 사용률: {disk_usage:.1f}%")
        
        if warnings:
            logger.warning(f"시스템 경고: {', '.join(warnings)}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"시스템 메트릭 조회 중 오류: {e}")
        # 안전한 기본값 반환
        return SystemMetrics(
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_usage=0.0,
            network_status="error",
            network_usage=0.0,
            network_speed_mbps=0.0,
            uptime=0,
            active_services=0,
            timestamp=datetime.now().isoformat()
        )

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """성능 메트릭 조회 (히스토리 포함)"""
    logger.info("성능 메트릭 조회 요청")
    
    if not metrics_history:
        # 빈 데이터 반환
        return PerformanceMetrics(
            cpu_usage=[],
            memory_usage=[],
            disk_io={},
            network_io={},
            timestamps=[]
        )
    
    # 최근 20개 데이터 포인트
    recent_metrics = metrics_history[-20:]
    
    cpu_usage = [m.cpu_percent for m in recent_metrics]
    memory_usage = [m.memory_percent for m in recent_metrics]
    timestamps = [m.timestamp for m in recent_metrics]
    
    # 디스크 I/O 정보
    try:
        disk_io = psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
    except:
        disk_io = {}
    
    # 네트워크 I/O 정보
    try:
        network_io = psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
    except:
        network_io = {}
    
    return PerformanceMetrics(
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        disk_io=disk_io,
        network_io=network_io,
        timestamps=timestamps
    )

@router.get("/stability", response_model=StabilityMetrics)
async def get_stability_metrics():
    """안정성 메트릭 조회"""
    logger.info("안정성 메트릭 조회 요청")
    
    try:
        # 시스템 상태 체크
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        # 시스템 상태 판단
        if cpu_percent > 90 or memory_percent > 95:
            system_health = "critical"
            error_count = 1
        elif cpu_percent > 70 or memory_percent > 80:
            system_health = "warning"
            error_count = 0
        else:
            system_health = "healthy"
            error_count = 0
        
        # 서비스 실패 정보
        service_failures = []
        if system_health == "critical":
            service_failures.append({
                "service_id": "system",
                "error": f"높은 리소스 사용률 (CPU: {cpu_percent:.1f}%, 메모리: {memory_percent:.1f}%)",
                "timestamp": datetime.now().isoformat(),
                "resolved": False
            })
        
        return StabilityMetrics(
            error_count=error_count,
            recovery_count=0,
            last_health_check=datetime.now().isoformat(),
            system_health=system_health,
            service_failures=service_failures
        )
        
    except Exception as e:
        logger.error(f"안정성 메트릭 조회 중 오류: {e}")
        # 기본값 반환
        return StabilityMetrics(
            error_count=0,
            recovery_count=0,
            last_health_check=datetime.now().isoformat(),
            system_health="unknown",
            service_failures=[]
        )

@router.get("/history")
async def get_metrics_history(limit: int = 50):
    """메트릭 히스토리 조회"""
    logger.info(f"메트릭 히스토리 조회 요청 (limit: {limit})")
    
    # 최근 N개 메트릭 반환
    recent_metrics = metrics_history[-limit:] if metrics_history else []
    
    return {
        "metrics": recent_metrics,
        "total_count": len(metrics_history),
        "returned_count": len(recent_metrics)
    }

@router.delete("/history")
async def clear_metrics_history():
    """메트릭 히스토리 초기화"""
    logger.info("메트릭 히스토리 초기화 요청")
    
    global metrics_history
    cleared_count = len(metrics_history)
    metrics_history.clear()
    
    return {
        "message": f"{cleared_count}개의 메트릭 히스토리가 초기화되었습니다",
        "cleared_count": cleared_count
    }