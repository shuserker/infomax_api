"""
웹훅 관련 데이터 모델
Dooray 웹훅 시스템을 위한 Pydantic 모델들
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum

class WebhookType(str, Enum):
    """웹훅 타입 열거형"""
    DOORAY = "dooray"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    GENERIC = "generic"

class WebhookStatus(str, Enum):
    """웹훅 상태 열거형"""
    PENDING = "pending"
    SENDING = "sending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class AlertLevel(str, Enum):
    """알림 레벨 열거형"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MessageType(str, Enum):
    """메시지 타입 열거형"""
    NEWS_ALERT = "news_alert"
    SYSTEM_STATUS = "system_status"
    SERVICE_ALERT = "service_alert"
    ERROR_REPORT = "error_report"
    CUSTOM = "custom"

class AuthType(str, Enum):
    """인증 타입 열거형"""
    NONE = "none"
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"

# ===== 웹훅 설정 모델 =====

class RateLimit(BaseModel):
    """속도 제한 설정 모델"""
    enabled: bool = Field(default=False, description="속도 제한 활성화")
    max_requests: int = Field(default=60, ge=1, le=1000, description="최대 요청 수")
    time_window: int = Field(default=60, ge=60, le=3600, description="시간 창 (초)")

class WebhookAuth(BaseModel):
    """웹훅 인증 설정 모델"""
    type: AuthType = Field(default=AuthType.NONE, description="인증 타입")
    token: Optional[str] = Field(None, description="토큰")
    username: Optional[str] = Field(None, description="사용자명")
    password: Optional[str] = Field(None, description="비밀번호")
    api_key: Optional[str] = Field(None, description="API 키")
    api_key_header: Optional[str] = Field(None, description="API 키 헤더명")

class WebhookConfig(BaseModel):
    """웹훅 설정 모델"""
    id: str = Field(..., description="웹훅 ID")
    name: str = Field(..., description="웹훅 이름")
    type: WebhookType = Field(..., description="웹훅 타입")
    url: HttpUrl = Field(..., description="웹훅 URL")
    enabled: bool = Field(default=True, description="활성화 여부")
    timeout: int = Field(default=30, ge=5, le=60, description="타임아웃 (초)")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="재시도 횟수")
    retry_delay: int = Field(default=5, ge=1, le=30, description="재시도 지연 (초)")
    rate_limit: RateLimit = Field(default_factory=RateLimit, description="속도 제한")
    headers: Optional[Dict[str, str]] = Field(None, description="추가 헤더")
    auth: Optional[WebhookAuth] = Field(None, description="인증 설정")

# ===== 웹훅 메시지 모델 =====

class WebhookMessage(BaseModel):
    """웹훅 메시지 모델"""
    id: str = Field(..., description="메시지 ID")
    webhook_id: str = Field(..., description="웹훅 ID")
    type: MessageType = Field(..., description="메시지 타입")
    title: str = Field(..., description="메시지 제목")
    message: str = Field(..., min_length=1, description="메시지 내용")
    alert_level: AlertLevel = Field(..., description="알림 레벨")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")
    data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")
    template_id: Optional[str] = Field(None, description="템플릿 ID")
    variables: Optional[Dict[str, Any]] = Field(None, description="템플릿 변수")

class WebhookHistory(BaseModel):
    """웹훅 전송 히스토리 모델"""
    id: str = Field(..., description="히스토리 ID")
    webhook_id: str = Field(..., description="웹훅 ID")
    message_id: str = Field(..., description="메시지 ID")
    status: WebhookStatus = Field(..., description="전송 상태")
    sent_at: datetime = Field(default_factory=datetime.now, description="전송 시간")
    completed_at: Optional[datetime] = Field(None, description="완료 시간")
    response_code: Optional[int] = Field(None, description="HTTP 응답 코드")
    response_body: Optional[str] = Field(None, description="응답 본문")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    retry_count: int = Field(default=0, ge=0, description="재시도 횟수")
    processing_time: Optional[float] = Field(None, ge=0, description="처리 시간 (밀리초)")

class WebhookTemplate(BaseModel):
    """웹훅 템플릿 모델"""
    id: str = Field(..., description="템플릿 ID")
    name: str = Field(..., min_length=1, description="템플릿 이름")
    description: str = Field(..., description="템플릿 설명")
    webhook_type: WebhookType = Field(..., description="웹훅 타입")
    message_type: MessageType = Field(..., description="메시지 타입")
    template: str = Field(..., min_length=1, description="메시지 템플릿")
    variables: List[str] = Field(default_factory=list, description="템플릿 변수 목록")
    default_values: Optional[Dict[str, Any]] = Field(None, description="기본값")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")
    is_system: bool = Field(default=False, description="시스템 기본 템플릿 여부")

class WebhookStatistics(BaseModel):
    """웹훅 통계 모델"""
    webhook_id: str = Field(..., description="웹훅 ID")
    total_sent: int = Field(..., ge=0, description="총 전송 횟수")
    successful_sent: int = Field(..., ge=0, description="성공한 전송 횟수")
    failed_sent: int = Field(..., ge=0, description="실패한 전송 횟수")
    success_rate: float = Field(..., ge=0, le=100, description="성공률 (%)")
    average_response_time: float = Field(..., ge=0, description="평균 응답 시간 (밀리초)")
    last_24h: Dict[str, Union[int, float]] = Field(default_factory=dict, description="최근 24시간 통계")
    last_7d: Dict[str, Union[int, float]] = Field(default_factory=dict, description="최근 7일 통계")
    last_success: Optional[datetime] = Field(None, description="마지막 성공 시간")
    last_failure: Optional[datetime] = Field(None, description="마지막 실패 시간")
    current_streak: Dict[str, Any] = Field(default_factory=dict, description="현재 연속 기록")

# ===== POSCO 전용 웹훅 모델 =====

class PoscoNewsWebhookPayload(BaseModel):
    """POSCO 뉴스 웹훅 페이로드 모델"""
    type: str = Field(..., description="뉴스 타입")
    status: str = Field(..., description="뉴스 상태")
    title: str = Field(..., description="제목")
    message: str = Field(..., description="메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="뉴스 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="시간")
    alert_level: AlertLevel = Field(..., description="알림 레벨")
    delay_minutes: Optional[int] = Field(None, ge=0, description="지연 시간 (분)")
    error_message: Optional[str] = Field(None, description="오류 메시지")

class PoscoSystemWebhookPayload(BaseModel):
    """POSCO 시스템 웹훅 페이로드 모델"""
    system_status: str = Field(..., description="시스템 상태")
    title: str = Field(..., description="제목")
    message: str = Field(..., description="메시지")
    services_summary: Dict[str, int] = Field(..., description="서비스 요약")
    alerts_count: int = Field(..., ge=0, description="알림 개수")
    uptime: int = Field(..., ge=0, description="가동 시간 (초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="시간")
    alert_level: AlertLevel = Field(..., description="알림 레벨")

# ===== Dooray 메시지 형식 모델 =====

class DoorayField(BaseModel):
    """Dooray 필드 모델"""
    title: str = Field(..., description="필드 제목")
    value: str = Field(..., description="필드 값")
    short: bool = Field(default=False, description="짧은 형식 여부")

class DoorayAttachment(BaseModel):
    """Dooray 첨부 모델"""
    title: Optional[str] = Field(None, description="첨부 제목")
    title_link: Optional[str] = Field(None, description="제목 링크")
    text: Optional[str] = Field(None, description="첨부 텍스트")
    color: Optional[str] = Field(None, description="색상")
    fields: Optional[List[DoorayField]] = Field(None, description="필드 목록")
    image_url: Optional[str] = Field(None, description="이미지 URL")
    thumb_url: Optional[str] = Field(None, description="썸네일 URL")

class DoorayMessage(BaseModel):
    """Dooray 메시지 모델"""
    bot_name: Optional[str] = Field(None, description="봇 이름")
    bot_icon_image: Optional[str] = Field(None, description="봇 아이콘 이미지")
    text: str = Field(..., description="메시지 텍스트")
    attachments: Optional[List[DoorayAttachment]] = Field(None, description="첨부 목록")

# ===== 웹훅 큐 관리 모델 =====

class WebhookQueueItem(BaseModel):
    """웹훅 큐 아이템 모델"""
    id: str = Field(..., description="큐 아이템 ID")
    webhook_id: str = Field(..., description="웹훅 ID")
    message: WebhookMessage = Field(..., description="메시지")
    priority: str = Field(default="normal", regex="^(low|normal|high|critical)$", description="우선순위")
    scheduled_at: datetime = Field(default_factory=datetime.now, description="예약 시간")
    max_retries: int = Field(default=3, ge=0, description="최대 재시도 횟수")
    current_retry: int = Field(default=0, ge=0, description="현재 재시도 횟수")
    status: WebhookStatus = Field(default=WebhookStatus.PENDING, description="상태")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

class WebhookQueue(BaseModel):
    """웹훅 큐 모델"""
    items: List[WebhookQueueItem] = Field(default_factory=list, description="큐 아이템 목록")
    total_pending: int = Field(default=0, ge=0, description="대기 중인 총 개수")
    total_processing: int = Field(default=0, ge=0, description="처리 중인 총 개수")
    total_failed: int = Field(default=0, ge=0, description="실패한 총 개수")
    is_processing: bool = Field(default=False, description="처리 중 여부")
    last_processed: Optional[datetime] = Field(None, description="마지막 처리 시간")

# ===== 웹훅 설정 그룹 모델 =====

class GlobalWebhookSettings(BaseModel):
    """전역 웹훅 설정 모델"""
    enabled: bool = Field(default=True, description="웹훅 활성화")
    default_timeout: int = Field(default=30, ge=5, le=60, description="기본 타임아웃 (초)")
    default_retry_attempts: int = Field(default=3, ge=0, le=10, description="기본 재시도 횟수")
    rate_limiting: Dict[str, Any] = Field(default_factory=dict, description="속도 제한 설정")
    quiet_hours: Dict[str, Any] = Field(default_factory=dict, description="조용한 시간 설정")
    alert_filtering: Dict[str, Any] = Field(default_factory=dict, description="알림 필터링 설정")

class WebhookSettings(BaseModel):
    """웹훅 설정 모델"""
    posco_news: WebhookConfig = Field(..., description="POSCO 뉴스 웹훅 설정")
    watchhamster_system: WebhookConfig = Field(..., description="WatchHamster 시스템 웹훅 설정")
    global_settings: GlobalWebhookSettings = Field(default_factory=GlobalWebhookSettings, description="전역 설정")

# ===== API 요청/응답 모델 =====

class SendWebhookRequest(BaseModel):
    """웹훅 전송 요청 모델"""
    webhook_id: str = Field(..., description="웹훅 ID")
    title: str = Field(..., description="메시지 제목")
    message: str = Field(..., min_length=1, description="메시지 내용")
    alert_level: AlertLevel = Field(default=AlertLevel.INFO, description="알림 레벨")
    data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")
    priority: str = Field(default="normal", regex="^(low|normal|high|critical)$", description="우선순위")
    scheduled_at: Optional[datetime] = Field(None, description="예약 시간")

class SendWebhookResponse(BaseModel):
    """웹훅 전송 응답 모델"""
    message_id: str = Field(..., description="메시지 ID")
    queue_position: int = Field(..., ge=0, description="큐 위치")
    estimated_send_time: datetime = Field(..., description="예상 전송 시간")

class GetWebhookHistoryRequest(BaseModel):
    """웹훅 히스토리 조회 요청 모델"""
    webhook_id: Optional[str] = Field(None, description="웹훅 ID")
    limit: int = Field(default=100, ge=1, le=1000, description="조회 개수")
    offset: int = Field(default=0, ge=0, description="오프셋")
    status_filter: Optional[List[WebhookStatus]] = Field(None, description="상태 필터")
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")

class GetWebhookHistoryResponse(BaseModel):
    """웹훅 히스토리 조회 응답 모델"""
    data: List[WebhookHistory] = Field(..., description="히스토리 목록")
    total: int = Field(..., ge=0, description="전체 개수")
    has_more: bool = Field(..., description="더 많은 데이터 존재 여부")

class TestWebhookRequest(BaseModel):
    """웹훅 테스트 요청 모델"""
    webhook_id: str = Field(..., description="웹훅 ID")
    test_message: str = Field(default="테스트 메시지입니다.", description="테스트 메시지")

class TestWebhookResponse(BaseModel):
    """웹훅 테스트 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    response_code: Optional[int] = Field(None, description="HTTP 응답 코드")
    response_time: float = Field(..., ge=0, description="응답 시간 (밀리초)")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="테스트 시간")

class GetWebhookStatisticsRequest(BaseModel):
    """웹훅 통계 조회 요청 모델"""
    webhook_id: Optional[str] = Field(None, description="웹훅 ID")
    period: str = Field(default="24h", regex="^(1h|24h|7d|30d)$", description="통계 기간")

class GetWebhookStatisticsResponse(BaseModel):
    """웹훅 통계 조회 응답 모델"""
    data: List[WebhookStatistics] = Field(..., description="통계 목록")
    period: str = Field(..., description="통계 기간")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

# ===== 웹훅 이벤트 모델 =====

class WebhookEvent(BaseModel):
    """웹훅 이벤트 모델"""
    type: str = Field(..., regex="^(webhook_sent|webhook_failed|webhook_retry|webhook_cancelled)$", description="이벤트 타입")
    webhook_id: str = Field(..., description="웹훅 ID")
    message_id: str = Field(..., description="메시지 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="이벤트 시간")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")

# ===== 웹훅 알림 규칙 모델 =====

class WebhookAlertRule(BaseModel):
    """웹훅 알림 규칙 모델"""
    id: str = Field(..., description="규칙 ID")
    name: str = Field(..., description="규칙 이름")
    description: str = Field(..., description="규칙 설명")
    enabled: bool = Field(default=True, description="활성화 여부")
    conditions: Dict[str, Any] = Field(..., description="조건")
    webhook_ids: List[str] = Field(..., description="웹훅 ID 목록")
    template_id: Optional[str] = Field(None, description="템플릿 ID")
    rate_limit: Optional[Dict[str, Any]] = Field(None, description="속도 제한")
    schedule: Optional[Dict[str, Any]] = Field(None, description="스케줄")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")

# ===== 웹훅 배치 작업 모델 =====

class WebhookBatchOperation(BaseModel):
    """웹훅 배치 작업 모델"""
    id: str = Field(..., description="배치 작업 ID")
    type: str = Field(..., regex="^(send_multiple|retry_failed|cancel_pending)$", description="작업 타입")
    webhook_ids: List[str] = Field(..., description="웹훅 ID 목록")
    message_ids: Optional[List[str]] = Field(None, description="메시지 ID 목록")
    status: str = Field(..., regex="^(pending|running|completed|failed)$", description="작업 상태")
    progress: float = Field(default=0.0, ge=0, le=100, description="진행률 (%)")
    total_items: int = Field(..., ge=0, description="총 아이템 수")
    processed_items: int = Field(default=0, ge=0, description="처리된 아이템 수")
    failed_items: int = Field(default=0, ge=0, description="실패한 아이템 수")
    started_at: datetime = Field(default_factory=datetime.now, description="시작 시간")
    completed_at: Optional[datetime] = Field(None, description="완료 시간")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="결과 목록")

# ===== 웹훅 모니터링 모델 =====

class WebhookMonitoringState(BaseModel):
    """웹훅 모니터링 상태 모델"""
    is_running: bool = Field(..., description="실행 상태")
    queue_size: int = Field(..., ge=0, description="큐 크기")
    processing_rate: float = Field(..., ge=0, description="처리 속도 (메시지/분)")
    success_rate: float = Field(..., ge=0, le=100, description="성공률 (%)")
    average_response_time: float = Field(..., ge=0, description="평균 응답 시간 (밀리초)")
    last_processed: Optional[datetime] = Field(None, description="마지막 처리 시간")
    errors_last_hour: int = Field(..., ge=0, description="최근 1시간 오류 수")
    rate_limit_hits: int = Field(..., ge=0, description="속도 제한 적중 횟수")

# ===== 레거시 호환성 모델 =====

class WebhookPayload(BaseModel):
    """웹훅 페이로드 모델 (레거시 호환성)"""
    url: HttpUrl = Field(..., description="웹훅 URL")
    message: str = Field(..., min_length=1, description="전송할 메시지")
    webhook_type: str = Field(default="dooray", regex="^(dooray|discord|slack|generic)$", description="웹훅 타입")
    template_id: Optional[str] = Field(None, description="사용할 템플릿 ID")
    variables: Optional[Dict[str, Any]] = Field(None, description="템플릿 변수")

class WebhookResponse(BaseModel):
    """웹훅 전송 응답 모델 (레거시 호환성)"""
    message: str = Field(..., description="응답 메시지")
    webhook_id: str = Field(..., description="웹훅 ID")
    status: str = Field(..., description="전송 상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class WebhookStats(BaseModel):
    """웹훅 통계 모델 (레거시 호환성)"""
    total_sent: int = Field(..., ge=0, description="총 전송 횟수")
    successful: int = Field(..., ge=0, description="성공 횟수")
    failed: int = Field(..., ge=0, description="실패 횟수")
    pending: int = Field(..., ge=0, description="대기 중 횟수")
    success_rate: float = Field(..., ge=0, le=100, description="성공률 (%)")
    last_sent: Optional[datetime] = Field(None, description="마지막 전송 시간")