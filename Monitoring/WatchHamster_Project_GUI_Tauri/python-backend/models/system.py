"""
시스템 관련 데이터 모델
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SystemInfo(BaseModel):
    """시스템 정보 모델"""
    platform: str = Field(..., description="운영체제 플랫폼")
    arch: str = Field(..., description="시스템 아키텍처")
    version: str = Field(..., description="애플리케이션 버전")
    hostname: str = Field(..., description="호스트명")

class SystemMetrics(BaseModel):
    """시스템 메트릭 모델"""
    cpu_percent: float = Field(..., ge=0, le=100, description="CPU 사용률 (%)")
    memory_percent: float = Field(..., ge=0, le=100, description="메모리 사용률 (%)")
    disk_usage: float = Field(..., ge=0, le=100, description="디스크 사용률 (%)")
    network_status: str = Field(..., description="네트워크 상태")
    uptime: int = Field(..., ge=0, description="시스템 업타임 (초)")
    active_services: int = Field(..., ge=0, description="활성 서비스 수")
    timestamp: datetime = Field(default_factory=datetime.now, description="측정 시간")

class PerformanceMetrics(BaseModel):
    """성능 메트릭 모델"""
    cpu_usage: List[float] = Field(default_factory=list, description="CPU 사용률 히스토리")
    memory_usage: List[float] = Field(default_factory=list, description="메모리 사용률 히스토리")
    disk_io: Dict[str, Any] = Field(default_factory=dict, description="디스크 I/O 정보")
    network_io: Dict[str, Any] = Field(default_factory=dict, description="네트워크 I/O 정보")
    timestamps: List[datetime] = Field(default_factory=list, description="측정 시간 목록")

class ServiceFailure(BaseModel):
    """서비스 실패 정보 모델"""
    service_id: str = Field(..., description="서비스 ID")
    error: str = Field(..., description="오류 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="발생 시간")
    resolved: bool = Field(default=False, description="해결 여부")

class StabilityMetrics(BaseModel):
    """안정성 메트릭 모델"""
    error_count: int = Field(..., ge=0, description="오류 발생 횟수")
    recovery_count: int = Field(..., ge=0, description="복구 횟수")
    last_health_check: datetime = Field(default_factory=datetime.now, description="마지막 헬스 체크 시간")
    system_health: str = Field(..., regex="^(healthy|warning|critical)$", description="시스템 상태")
    service_failures: List[ServiceFailure] = Field(default_factory=list, description="서비스 실패 목록")