"""
WebSocket 관련 데이터 모델
실시간 통신을 위한 Pydantic 모델들
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, HttpUrl
from enum import Enum

class WSMessageType(str, Enum):
    """WebSocket 메시지 타입 열거형"""
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_LOST = "connection_lost"
    PING = "ping"
    PONG = "pong"
    STATUS_UPDATE = "status_update"
    NEWS_UPDATE = "news_update"
    SYSTEM_UPDATE = "system_update"
    SERVICE_EVENT = "service_event"
    ALERT = "alert"
    LOG_UPDATE = "log_update"
    METRICS_UPDATE = "metrics_update"
    WEBHOOK_EVENT = "webhook_event"
    ERROR = "error"
    NOTIFICATION = "notification"

class WSConnectionStatus(str, Enum):
    """WebSocket 연결 상태 열거형"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

class NotificationLevel(str, Enum):
    """알림 레벨 열거형"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class ServiceEventType(str, Enum):
    """서비스 이벤트 타입 열거형"""
    STARTED = "started"
    STOPPED = "stopped"
    ERROR = "error"
    RESTARTED = "restarted"
    STATUS_CHANGED = "status_changed"

class WebhookEventType(str, Enum):
    """웹훅 이벤트 타입 열거형"""
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"

# ===== 기본 WebSocket 메시지 모델 =====

class WSMessage(BaseModel):
    """WebSocket 메시지 기본 모델"""
    id: str = Field(..., description="메시지 ID")
    type: WSMessageType = Field(..., description="메시지 타입")
    data: Dict[str, Any] = Field(..., description="메시지 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")
    source: Optional[str] = Field(None, description="메시지 소스")
    correlation_id: Optional[str] = Field(None, description="상관관계 ID")

# ===== 연결 상태 모델 =====

class WSConnectionState(BaseModel):
    """WebSocket 연결 상태 모델"""
    status: WSConnectionStatus = Field(..., description="연결 상태")
    url: HttpUrl = Field(..., description="WebSocket URL")
    connected_at: Optional[datetime] = Field(None, description="연결 시간")
    disconnected_at: Optional[datetime] = Field(None, description="연결 해제 시간")
    reconnect_attempts: int = Field(default=0, ge=0, description="재연결 시도 횟수")
    last_error: Optional[str] = Field(None, description="마지막 오류")

class WSConfig(BaseModel):
    """WebSocket 설정 모델"""
    url: HttpUrl = Field(..., description="WebSocket URL")
    auto_reconnect: bool = Field(default=True, description="자동 재연결")
    max_reconnect_attempts: int = Field(default=10, ge=0, le=100, description="최대 재연결 시도 횟수")
    reconnect_delay: int = Field(default=5000, ge=1000, le=60000, description="재연결 지연 (밀리초)")
    ping_interval: int = Field(default=30000, ge=5000, le=300000, description="핑 간격 (밀리초)")
    pong_timeout: int = Field(default=10000, ge=1000, le=30000, description="퐁 타임아웃 (밀리초)")
    message_queue_size: int = Field(default=1000, ge=10, le=10000, description="메시지 큐 크기")
    compression: bool = Field(default=False, description="압축 사용")

# ===== 특정 메시지 타입 모델 =====

class WSConnectionData(BaseModel):
    """연결 확립 메시지 데이터 모델"""
    client_id: str = Field(..., description="클라이언트 ID")
    server_version: str = Field(..., description="서버 버전")
    supported_features: List[str] = Field(..., description="지원 기능 목록")
    session_id: str = Field(..., description="세션 ID")

class WSConnectionMessage(WSMessage):
    """연결 확립 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.CONNECTION_ESTABLISHED, description="메시지 타입")
    data: WSConnectionData = Field(..., description="연결 데이터")

class WSPingData(BaseModel):
    """핑 메시지 데이터 모델"""
    timestamp: datetime = Field(default_factory=datetime.now, description="핑 시간")

class WSPingMessage(WSMessage):
    """핑 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.PING, description="메시지 타입")
    data: WSPingData = Field(..., description="핑 데이터")

class WSPongData(BaseModel):
    """퐁 메시지 데이터 모델"""
    timestamp: datetime = Field(..., description="퐁 시간")
    latency: Optional[float] = Field(None, ge=0, description="지연 시간 (밀리초)")

class WSPongMessage(WSMessage):
    """퐁 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.PONG, description="메시지 타입")
    data: WSPongData = Field(..., description="퐁 데이터")

class WSNewsUpdateData(BaseModel):
    """뉴스 업데이트 메시지 데이터 모델"""
    news_status: List[Dict[str, Any]] = Field(..., description="뉴스 상태 목록")
    changed_types: List[str] = Field(..., description="변경된 뉴스 타입")
    summary: Dict[str, int] = Field(..., description="상태 요약")

class WSNewsUpdateMessage(WSMessage):
    """뉴스 업데이트 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.NEWS_UPDATE, description="메시지 타입")
    data: WSNewsUpdateData = Field(..., description="뉴스 업데이트 데이터")

class WSSystemUpdateData(BaseModel):
    """시스템 업데이트 메시지 데이터 모델"""
    system_status: Dict[str, Any] = Field(..., description="시스템 상태")
    changed_services: List[str] = Field(..., description="변경된 서비스")
    metrics_updated: bool = Field(..., description="메트릭 업데이트 여부")

class WSSystemUpdateMessage(WSMessage):
    """시스템 업데이트 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.SYSTEM_UPDATE, description="메시지 타입")
    data: WSSystemUpdateData = Field(..., description="시스템 업데이트 데이터")

class WSServiceEventData(BaseModel):
    """서비스 이벤트 메시지 데이터 모델"""
    service_id: str = Field(..., description="서비스 ID")
    event_type: ServiceEventType = Field(..., description="이벤트 타입")
    message: str = Field(..., description="이벤트 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")
    previous_status: Optional[str] = Field(None, description="이전 상태")
    current_status: str = Field(..., description="현재 상태")

class WSServiceEventMessage(WSMessage):
    """서비스 이벤트 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.SERVICE_EVENT, description="메시지 타입")
    data: WSServiceEventData = Field(..., description="서비스 이벤트 데이터")

class WSAlertData(BaseModel):
    """알림 메시지 데이터 모델"""
    alert: Dict[str, Any] = Field(..., description="알림 데이터")
    alert_type: str = Field(..., description="알림 타입")
    requires_action: bool = Field(..., description="액션 필요 여부")

class WSAlertMessage(WSMessage):
    """알림 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.ALERT, description="메시지 타입")
    data: WSAlertData = Field(..., description="알림 데이터")

class WSLogUpdateData(BaseModel):
    """로그 업데이트 메시지 데이터 모델"""
    logs: List[Dict[str, Any]] = Field(..., description="로그 목록")
    total_new: int = Field(..., ge=0, description="새로운 로그 수")
    source: str = Field(..., description="로그 소스")

class WSLogUpdateMessage(WSMessage):
    """로그 업데이트 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.LOG_UPDATE, description="메시지 타입")
    data: WSLogUpdateData = Field(..., description="로그 업데이트 데이터")

class WSMetricsUpdateData(BaseModel):
    """메트릭 업데이트 메시지 데이터 모델"""
    cpu_percent: float = Field(..., ge=0, le=100, description="CPU 사용률 (%)")
    memory_percent: float = Field(..., ge=0, le=100, description="메모리 사용률 (%)")
    disk_usage: float = Field(..., ge=0, le=100, description="디스크 사용률 (%)")
    network_status: str = Field(..., description="네트워크 상태")
    active_services: int = Field(..., ge=0, description="활성 서비스 수")
    timestamp: datetime = Field(default_factory=datetime.now, description="측정 시간")

class WSMetricsUpdateMessage(WSMessage):
    """메트릭 업데이트 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.METRICS_UPDATE, description="메시지 타입")
    data: WSMetricsUpdateData = Field(..., description="메트릭 업데이트 데이터")

class WSWebhookEventData(BaseModel):
    """웹훅 이벤트 메시지 데이터 모델"""
    webhook_id: str = Field(..., description="웹훅 ID")
    event_type: WebhookEventType = Field(..., description="이벤트 타입")
    message_id: str = Field(..., description="메시지 ID")
    status: str = Field(..., description="상태")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")

class WSWebhookEventMessage(WSMessage):
    """웹훅 이벤트 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.WEBHOOK_EVENT, description="메시지 타입")
    data: WSWebhookEventData = Field(..., description="웹훅 이벤트 데이터")

class WSErrorData(BaseModel):
    """오류 메시지 데이터 모델"""
    error_code: str = Field(..., description="오류 코드")
    error_message: str = Field(..., description="오류 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")
    recoverable: bool = Field(..., description="복구 가능 여부")

class WSErrorMessage(WSMessage):
    """오류 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.ERROR, description="메시지 타입")
    data: WSErrorData = Field(..., description="오류 데이터")

class WSNotificationAction(BaseModel):
    """알림 액션 모델"""
    label: str = Field(..., description="액션 라벨")
    url: Optional[HttpUrl] = Field(None, description="액션 URL")
    callback: Optional[str] = Field(None, description="콜백 함수")

class WSNotificationData(BaseModel):
    """알림 메시지 데이터 모델"""
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 메시지")
    level: NotificationLevel = Field(..., description="알림 레벨")
    action: Optional[WSNotificationAction] = Field(None, description="액션")
    auto_dismiss: bool = Field(default=True, description="자동 해제")
    duration: Optional[int] = Field(None, ge=1000, description="지속 시간 (밀리초)")

class WSNotificationMessage(WSMessage):
    """알림 메시지 모델"""
    type: WSMessageType = Field(default=WSMessageType.NOTIFICATION, description="메시지 타입")
    data: WSNotificationData = Field(..., description="알림 데이터")

# ===== WebSocket 상태 관리 모델 =====

class WSStatistics(BaseModel):
    """WebSocket 통계 모델"""
    messages_sent: int = Field(default=0, ge=0, description="전송된 메시지 수")
    messages_received: int = Field(default=0, ge=0, description="수신된 메시지 수")
    reconnect_count: int = Field(default=0, ge=0, description="재연결 횟수")
    average_latency: float = Field(default=0.0, ge=0, description="평균 지연 시간 (밀리초)")
    last_ping: float = Field(default=0.0, ge=0, description="마지막 핑 지연 시간 (밀리초)")
    uptime: int = Field(default=0, ge=0, description="연결 유지 시간 (초)")

class WSState(BaseModel):
    """WebSocket 상태 모델"""
    connection: WSConnectionState = Field(..., description="연결 상태")
    config: WSConfig = Field(..., description="설정")
    message_queue: List[WSMessage] = Field(default_factory=list, description="메시지 큐")
    statistics: WSStatistics = Field(default_factory=WSStatistics, description="통계")

# ===== WebSocket 메시지 필터 모델 =====

class WSMessageFilter(BaseModel):
    """WebSocket 메시지 필터 모델"""
    types: Optional[List[WSMessageType]] = Field(None, description="메시지 타입 필터")
    sources: Optional[List[str]] = Field(None, description="소스 필터")
    correlation_ids: Optional[List[str]] = Field(None, description="상관관계 ID 필터")
    since: Optional[datetime] = Field(None, description="시작 시간")
    limit: Optional[int] = Field(None, ge=1, le=10000, description="최대 개수")

class WSMessageHistory(BaseModel):
    """WebSocket 메시지 히스토리 모델"""
    messages: List[WSMessage] = Field(..., description="메시지 목록")
    total: int = Field(..., ge=0, description="전체 메시지 수")
    filtered: int = Field(..., ge=0, description="필터링된 메시지 수")
    oldest: Optional[datetime] = Field(None, description="가장 오래된 메시지 시간")
    newest: Optional[datetime] = Field(None, description="가장 최신 메시지 시간")

# ===== WebSocket 연결 통계 모델 =====

class WSConnectionStats(BaseModel):
    """WebSocket 연결 통계 모델"""
    total_connections: int = Field(..., ge=0, description="총 연결 수")
    successful_connections: int = Field(..., ge=0, description="성공한 연결 수")
    failed_connections: int = Field(..., ge=0, description="실패한 연결 수")
    total_disconnections: int = Field(..., ge=0, description="총 연결 해제 수")
    average_connection_duration: float = Field(..., ge=0, description="평균 연결 지속 시간 (초)")
    longest_connection_duration: float = Field(..., ge=0, description="최장 연결 지속 시간 (초)")
    reconnect_success_rate: float = Field(..., ge=0, le=100, description="재연결 성공률 (%)")
    message_throughput: Dict[str, float] = Field(default_factory=dict, description="메시지 처리량")
    error_rate: float = Field(..., ge=0, le=100, description="오류율 (%)")
    last_24h: Dict[str, int] = Field(default_factory=dict, description="최근 24시간 통계")

# ===== WebSocket 보안 모델 =====

class WSSecurityConfig(BaseModel):
    """WebSocket 보안 설정 모델"""
    origin_whitelist: List[str] = Field(default_factory=list, description="허용된 오리진 목록")
    max_message_size: int = Field(default=1048576, ge=1024, le=10485760, description="최대 메시지 크기 (bytes)")
    rate_limit: Dict[str, int] = Field(default_factory=dict, description="속도 제한 설정")
    authentication: Dict[str, Any] = Field(default_factory=dict, description="인증 설정")

# ===== WebSocket 모니터링 모델 =====

class WSHealthStatus(str, Enum):
    """WebSocket 건강 상태 열거형"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class WSMonitoringData(BaseModel):
    """WebSocket 모니터링 데이터 모델"""
    connection_state: WSConnectionState = Field(..., description="연결 상태")
    message_stats: Dict[str, Union[int, str]] = Field(..., description="메시지 통계")
    performance: Dict[str, float] = Field(..., description="성능 지표")
    health: Dict[str, Any] = Field(..., description="건강 상태")

class WSHealthCheck(BaseModel):
    """WebSocket 헬스 체크 모델"""
    status: WSHealthStatus = Field(..., description="건강 상태")
    issues: List[str] = Field(default_factory=list, description="문제점 목록")
    last_check: datetime = Field(default_factory=datetime.now, description="마지막 체크 시간")
    response_time: Optional[float] = Field(None, ge=0, description="응답 시간 (밀리초)")

# ===== API 요청/응답 모델 =====

class WSConnectRequest(BaseModel):
    """WebSocket 연결 요청 모델"""
    client_id: Optional[str] = Field(None, description="클라이언트 ID")
    features: Optional[List[str]] = Field(None, description="요청 기능 목록")

class WSConnectResponse(BaseModel):
    """WebSocket 연결 응답 모델"""
    session_id: str = Field(..., description="세션 ID")
    server_version: str = Field(..., description="서버 버전")
    supported_features: List[str] = Field(..., description="지원 기능 목록")
    config: WSConfig = Field(..., description="연결 설정")

class WSSubscribeRequest(BaseModel):
    """WebSocket 구독 요청 모델"""
    message_types: List[WSMessageType] = Field(..., description="구독할 메시지 타입")
    filters: Optional[WSMessageFilter] = Field(None, description="메시지 필터")

class WSSubscribeResponse(BaseModel):
    """WebSocket 구독 응답 모델"""
    subscribed_types: List[WSMessageType] = Field(..., description="구독된 메시지 타입")
    subscription_id: str = Field(..., description="구독 ID")

class WSUnsubscribeRequest(BaseModel):
    """WebSocket 구독 해제 요청 모델"""
    subscription_id: str = Field(..., description="구독 ID")
    message_types: Optional[List[WSMessageType]] = Field(None, description="해제할 메시지 타입")

class WSUnsubscribeResponse(BaseModel):
    """WebSocket 구독 해제 응답 모델"""
    unsubscribed_types: List[WSMessageType] = Field(..., description="구독 해제된 메시지 타입")
    remaining_subscriptions: List[WSMessageType] = Field(..., description="남은 구독")

class GetWSStatsRequest(BaseModel):
    """WebSocket 통계 조회 요청 모델"""
    period: str = Field(default="1h", pattern="^(1h|6h|24h|7d)$", description="조회 기간")
    include_history: bool = Field(default=False, description="히스토리 포함")

class GetWSStatsResponse(BaseModel):
    """WebSocket 통계 조회 응답 모델"""
    stats: WSConnectionStats = Field(..., description="연결 통계")
    monitoring_data: WSMonitoringData = Field(..., description="모니터링 데이터")
    health_check: WSHealthCheck = Field(..., description="헬스 체크")
    period: str = Field(..., description="조회 기간")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

# ===== WebSocket 이벤트 모델 =====

class WSEvent(BaseModel):
    """WebSocket 이벤트 모델"""
    id: str = Field(..., description="이벤트 ID")
    type: str = Field(..., description="이벤트 타입")
    session_id: str = Field(..., description="세션 ID")
    client_id: Optional[str] = Field(None, description="클라이언트 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="이벤트 시간")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")

class WSEventLog(BaseModel):
    """WebSocket 이벤트 로그 모델"""
    events: List[WSEvent] = Field(..., description="이벤트 목록")
    total: int = Field(..., ge=0, description="전체 이벤트 수")
    session_id: str = Field(..., description="세션 ID")
    start_time: datetime = Field(..., description="시작 시간")
    end_time: datetime = Field(..., description="종료 시간")

# ===== WebSocket 클라이언트 관리 모델 =====

class WSClient(BaseModel):
    """WebSocket 클라이언트 모델"""
    id: str = Field(..., description="클라이언트 ID")
    session_id: str = Field(..., description="세션 ID")
    connected_at: datetime = Field(..., description="연결 시간")
    last_activity: datetime = Field(..., description="마지막 활동 시간")
    subscriptions: List[WSMessageType] = Field(default_factory=list, description="구독 목록")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    is_active: bool = Field(default=True, description="활성 상태")

class WSClientRegistry(BaseModel):
    """WebSocket 클라이언트 레지스트리 모델"""
    clients: Dict[str, WSClient] = Field(default_factory=dict, description="클라이언트 맵")
    total_clients: int = Field(default=0, ge=0, description="총 클라이언트 수")
    active_clients: int = Field(default=0, ge=0, description="활성 클라이언트 수")
    last_updated: datetime = Field(default_factory=datetime.now, description="마지막 업데이트 시간")