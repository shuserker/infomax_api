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

# 포팅된 핵심 모듈들 임포트
from core.performance_optimizer import get_performance_optimizer
from core.stability_manager import get_stability_manager
from core.status_reporter import create_integrated_status_reporter

logger = logging.getLogger(__name__)
router = APIRouter()

# 의존성 함수들
def get_performance_optimizer_instance():
    """성능 최적화 시스템 인스턴스 반환"""
    return get_performance_optimizer()

def get_stability_manager_instance():
    """안정성 관리자 인스턴스 반환"""
    return get_stability_manager()

def get_status_reporter_instance():
    """상태 보고 시스템 인스턴스 반환"""
    return create_integrated_status_reporter()

# 데이터 모델
class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_status: str
    uptime: int
    active_services: int
    timestamp: datetime

class PerformanceMetrics(BaseModel):
    cpu_usage: List[float]
    memory_usage: List[float]
    disk_io: Dict[str, Any]
    network_io: Dict[str, Any]
    timestamps: List[datetime]

class StabilityMetrics(BaseModel):
    error_count: int
    recovery_count: int
    last_health_check: datetime
    system_health: str  # healthy, warning, critical
    service_failures: List[Dict[str, Any]]

# 메트릭 히스토리 저장 (실제로는 데이터베이스 사용)
metrics_history = []

@router.get("/", response_model=SystemMetrics)
async def get_system_metrics(performance_optimizer = Depends(get_performance_optimizer_instance),
                           status_reporter = Depends(get_status_reporter_instance)):
    """현재 시스템 메트릭 조회"""
    logger.info("시스템 메트릭 조회 요청")
    
    try:
        # 포팅된 성능 최적화 시스템에서 메트릭 조회
        performance_metrics = await performance_optimizer.get_performance_metrics()
        
        # 상태 보고 시스템에서 서비스 상태 조회
        system_status = await status_reporter.get_system_status()
        
        # 시스템 업타임
        boot_time = psutil.boot_time()
        uptime = int(time.time() - boot_time)
        
        # 네트워크 상태 판단
        network_status = "connected"
        if performance_metrics.get('network_io', {}).get('bytes_recv', 0) > 0:
            network_status = "connected"
        else:
            network_status = "disconnected"
        
        metrics = SystemMetrics(
            cpu_percent=performance_metrics.get('cpu_percent', 0.0),
            memory_percent=performance_metrics.get('memory_percent', 0.0),
            disk_usage=performance_metrics.get('disk_usage_percent', 0.0),
            network_status=network_status,
            uptime=uptime,
            active_services=system_status.get('healthy_components', 0),
            timestamp=datetime.now()
        )
        
        # 히스토리에 추가 (최대 100개 유지)
        metrics_history.append(metrics)
        if len(metrics_history) > 100:
            metrics_history.pop(0)
        
        return metrics
        
    except Exception as e:
        logger.error(f"시스템 메트릭 조회 중 오류: {e}")
        # 기본값 반환
        return SystemMetrics(
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_usage=0.0,
            network_status="unknown",
            uptime=0,
            active_services=0,
            timestamp=datetime.now()
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
async def get_stability_metrics(stability_manager = Depends(get_stability_manager_instance)):
    """안정성 메트릭 조회"""
    logger.info("안정성 메트릭 조회 요청")
    
    try:
        # 포팅된 안정성 관리자에서 메트릭 조회
        stability_metrics = await stability_manager.get_stability_metrics()
        
        # 시스템 상태 매핑
        health_mapping = {
            'healthy': 'healthy',
            'warning': 'warning', 
            'critical': 'critical',
            'unknown': 'warning'
        }
        
        # 서비스 실패 정보 (실제로는 오류 로그에서 가져옴)
        service_failures = []
        if stability_metrics.active_issues > 0:
            service_failures.append({
                "service_id": "system",
                "error": f"{stability_metrics.active_issues}개의 활성 이슈",
                "timestamp": stability_metrics.last_error_time or datetime.now(),
                "resolved": False
            })
        
        return StabilityMetrics(
            error_count=stability_metrics.error_count,
            recovery_count=stability_metrics.recovery_count,
            last_health_check=datetime.now(),
            system_health=health_mapping.get(stability_metrics.system_health.value, 'warning'),
            service_failures=service_failures
        )
        
    except Exception as e:
        logger.error(f"안정성 메트릭 조회 중 오류: {e}")
        # 기본값 반환
        return StabilityMetrics(
            error_count=0,
            recovery_count=0,
            last_health_check=datetime.now(),
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