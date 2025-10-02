"""
웹훅 관련 데이터 모델
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, HttpUrl

class WebhookPayload(BaseModel):
    """웹훅 페이로드 모델"""
    url: HttpUrl = Field(..., description="웹훅 URL")
    message: str = Field(..., min_length=1, description="전송할 메시지")
    webhook_type: str = Field(default="discord", regex="^(discord|slack|generic)$", description="웹훅 타입")
    template_id: Optional[str] = Field(None, description="사용할 템플릿 ID")
    variables: Optional[Dict[str, Any]] = Field(None, description="템플릿 변수")

class WebhookTemplate(BaseModel):
    """웹훅 템플릿 모델"""
    id: str = Field(..., description="템플릿 고유 ID")
    name: str = Field(..., min_length=1, description="템플릿 이름")
    description: str = Field(..., description="템플릿 설명")
    webhook_type: str = Field(..., regex="^(discord|slack|generic)$", description="웹훅 타입")
    template: str = Field(..., min_length=1, description="메시지 템플릿")
    variables: List[str] = Field(default_factory=list, description="템플릿 변수 목록")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")

class WebhookHistory(BaseModel):
    """웹훅 전송 히스토리 모델"""
    id: str = Field(..., description="히스토리 고유 ID")
    url: str = Field(..., description="전송된 웹훅 URL")
    message: str = Field(..., description="전송된 메시지")
    webhook_type: str = Field(..., description="웹훅 타입")
    status: str = Field(..., regex="^(success|failed|pending)$", description="전송 상태")
    response_code: Optional[int] = Field(None, description="HTTP 응답 코드")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    sent_at: datetime = Field(default_factory=datetime.now, description="전송 시간")
    template_id: Optional[str] = Field(None, description="사용된 템플릿 ID")
    variables: Optional[Dict[str, Any]] = Field(None, description="사용된 변수")

class WebhookResponse(BaseModel):
    """웹훅 전송 응답 모델"""
    message: str = Field(..., description="응답 메시지")
    webhook_id: str = Field(..., description="웹훅 ID")
    status: str = Field(..., description="전송 상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class WebhookStats(BaseModel):
    """웹훅 통계 모델"""
    total_sent: int = Field(..., ge=0, description="총 전송 횟수")
    successful: int = Field(..., ge=0, description="성공 횟수")
    failed: int = Field(..., ge=0, description="실패 횟수")
    pending: int = Field(..., ge=0, description="대기 중 횟수")
    success_rate: float = Field(..., ge=0, le=100, description="성공률 (%)")
    last_sent: Optional[datetime] = Field(None, description="마지막 전송 시간")