"""
서비스 관련 데이터 모델
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ServiceInfo(BaseModel):
    """서비스 정보 모델"""
    id: str = Field(..., description="서비스 고유 ID")
    name: str = Field(..., description="서비스 이름")
    description: str = Field(..., description="서비스 설명")
    status: str = Field(..., regex="^(running|stopped|error|starting|stopping)$", description="서비스 상태")
    uptime: Optional[int] = Field(None, ge=0, description="서비스 업타임 (초)")
    last_error: Optional[str] = Field(None, description="마지막 오류 메시지")
    config: Optional[Dict[str, Any]] = Field(None, description="서비스 설정")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")

class ServiceAction(BaseModel):
    """서비스 액션 모델"""
    action: str = Field(..., regex="^(start|stop|restart)$", description="수행할 액션")
    service_id: str = Field(..., description="대상 서비스 ID")
    parameters: Optional[Dict[str, Any]] = Field(None, description="액션 매개변수")

class ServiceStatus(BaseModel):
    """서비스 상태 응답 모델"""
    service_id: str = Field(..., description="서비스 ID")
    status: str = Field(..., description="현재 상태")
    message: str = Field(..., description="상태 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="상태 확인 시간")

class ServiceLog(BaseModel):
    """서비스 로그 모델"""
    id: str = Field(..., description="로그 ID")
    service_id: str = Field(..., description="서비스 ID")
    level: str = Field(..., regex="^(DEBUG|INFO|WARN|ERROR)$", description="로그 레벨")
    message: str = Field(..., description="로그 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="로그 시간")
    details: Optional[Dict[str, Any]] = Field(None, description="추가 세부 정보")