"""
서비스 관련 데이터 모델
WatchHamster 서비스 관리를 위한 Pydantic 모델들
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class ServiceStatus(str, Enum):
    """서비스 상태 열거형"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

class ServiceAction(str, Enum):
    """서비스 액션 열거형"""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    RELOAD = "reload"
    STATUS = "status"

class LogLevel(str, Enum):
    """로그 레벨 열거형"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ServiceType(str, Enum):
    """서비스 타입 열거형"""
    INFOMAX_MONITOR = "infomax_monitor"
    WEBHOOK_SENDER = "webhook_sender"
    GIT_MONITOR = "git_monitor"
    SYSTEM_MONITOR = "system_monitor"
    NEWS_PARSER = "news_parser"
    CUSTOM = "custom"

# ===== 서비스 정보 모델 =====

class ServiceInfo(BaseModel):
    """서비스 정보 모델"""
    id: str = Field(..., description="서비스 고유 ID")
    name: str = Field(..., description="서비스 이름")
    description: str = Field(..., description="서비스 설명")
    type: ServiceType = Field(default=ServiceType.CUSTOM, description="서비스 타입")
    status: ServiceStatus = Field(..., description="서비스 상태")
    pid: Optional[int] = Field(None, ge=1, description="프로세스 ID")
    uptime: Optional[int] = Field(None, ge=0, description="서비스 업타임 (초)")
    restart_count: int = Field(default=0, ge=0, description="재시작 횟수")
    last_restart: Optional[datetime] = Field(None, description="마지막 재시작 시간")
    last_error: Optional[str] = Field(None, description="마지막 오류 메시지")
    error_count: int = Field(default=0, ge=0, description="오류 횟수")
    config: Optional[Dict[str, Any]] = Field(None, description="서비스 설정")
    dependencies: Optional[List[str]] = Field(None, description="의존성 서비스 목록")
    auto_restart: bool = Field(default=True, description="자동 재시작 여부")
    health_check_url: Optional[str] = Field(None, description="헬스 체크 URL")
    log_file: Optional[str] = Field(None, description="로그 파일 경로")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")

class ServiceMetrics(BaseModel):
    """서비스 메트릭 모델"""
    service_id: str = Field(..., description="서비스 ID")
    cpu_percent: float = Field(..., ge=0, description="CPU 사용률 (%)")
    memory_percent: float = Field(..., ge=0, description="메모리 사용률 (%)")
    memory_rss: int = Field(..., ge=0, description="RSS 메모리 (bytes)")
    memory_vms: int = Field(..., ge=0, description="VMS 메모리 (bytes)")
    num_threads: int = Field(..., ge=1, description="스레드 수")
    num_fds: Optional[int] = Field(None, ge=0, description="파일 디스크립터 수")
    connections: Optional[int] = Field(None, ge=0, description="네트워크 연결 수")
    timestamp: datetime = Field(default_factory=datetime.now, description="측정 시간")

class ServiceHealthCheck(BaseModel):
    """서비스 헬스 체크 모델"""
    service_id: str = Field(..., description="서비스 ID")
    status: str = Field(..., regex="^(healthy|unhealthy|degraded|unknown)$", description="헬스 상태")
    response_time: Optional[float] = Field(None, ge=0, description="응답 시간 (밀리초)")
    last_check: datetime = Field(default_factory=datetime.now, description="마지막 체크 시간")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")

# ===== 서비스 액션 모델 =====

class ServiceActionRequest(BaseModel):
    """서비스 액션 요청 모델"""
    action: ServiceAction = Field(..., description="수행할 액션")
    service_id: str = Field(..., description="대상 서비스 ID")
    force: bool = Field(default=False, description="강제 실행 여부")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="타임아웃 (초)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="액션 매개변수")

class ServiceActionResult(BaseModel):
    """서비스 액션 결과 모델"""
    service_id: str = Field(..., description="서비스 ID")
    action: ServiceAction = Field(..., description="실행된 액션")
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")
    previous_status: Optional[ServiceStatus] = Field(None, description="이전 상태")
    new_status: ServiceStatus = Field(..., description="새로운 상태")
    execution_time: float = Field(..., ge=0, description="실행 시간 (초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="실행 시간")

# ===== 서비스 로그 모델 =====

class ServiceLog(BaseModel):
    """서비스 로그 모델"""
    id: str = Field(..., description="로그 ID")
    service_id: str = Field(..., description="서비스 ID")
    level: LogLevel = Field(..., description="로그 레벨")
    message: str = Field(..., description="로그 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="로그 시간")
    source: Optional[str] = Field(None, description="로그 소스")
    correlation_id: Optional[str] = Field(None, description="상관관계 ID")
    details: Optional[Dict[str, Any]] = Field(None, description="추가 세부 정보")

class ServiceLogFilter(BaseModel):
    """서비스 로그 필터 모델"""
    service_ids: Optional[List[str]] = Field(None, description="서비스 ID 목록")
    levels: Optional[List[LogLevel]] = Field(None, description="로그 레벨 목록")
    search: Optional[str] = Field(None, description="검색어")
    start_time: Optional[datetime] = Field(None, description="시작 시간")
    end_time: Optional[datetime] = Field(None, description="종료 시간")
    correlation_id: Optional[str] = Field(None, description="상관관계 ID")

# ===== 서비스 설정 모델 =====

class ServiceConfig(BaseModel):
    """서비스 설정 모델"""
    service_id: str = Field(..., description="서비스 ID")
    config: Dict[str, Any] = Field(..., description="설정 데이터")
    version: int = Field(default=1, ge=1, description="설정 버전")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")
    created_by: Optional[str] = Field(None, description="생성자")
    updated_by: Optional[str] = Field(None, description="수정자")

class ServiceDependency(BaseModel):
    """서비스 의존성 모델"""
    service_id: str = Field(..., description="서비스 ID")
    depends_on: str = Field(..., description="의존하는 서비스 ID")
    dependency_type: str = Field(default="required", regex="^(required|optional|weak)$", description="의존성 타입")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

# ===== 서비스 이벤트 모델 =====

class ServiceEvent(BaseModel):
    """서비스 이벤트 모델"""
    id: str = Field(..., description="이벤트 ID")
    service_id: str = Field(..., description="서비스 ID")
    event_type: str = Field(..., description="이벤트 타입")
    message: str = Field(..., description="이벤트 메시지")
    severity: str = Field(..., regex="^(info|warning|error|critical)$", description="심각도")
    timestamp: datetime = Field(default_factory=datetime.now, description="이벤트 시간")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")
    acknowledged: bool = Field(default=False, description="확인 여부")

class ServiceAlert(BaseModel):
    """서비스 알림 모델"""
    id: str = Field(..., description="알림 ID")
    service_id: str = Field(..., description="서비스 ID")
    alert_type: str = Field(..., description="알림 타입")
    message: str = Field(..., description="알림 메시지")
    severity: str = Field(..., regex="^(info|warning|error|critical)$", description="심각도")
    threshold: Optional[float] = Field(None, description="임계값")
    current_value: Optional[float] = Field(None, description="현재 값")
    timestamp: datetime = Field(default_factory=datetime.now, description="알림 시간")
    acknowledged: bool = Field(default=False, description="확인 여부")
    auto_resolve: bool = Field(default=False, description="자동 해결 가능 여부")

# ===== 서비스 통계 모델 =====

class ServiceStatistics(BaseModel):
    """서비스 통계 모델"""
    service_id: str = Field(..., description="서비스 ID")
    uptime_percentage: float = Field(..., ge=0, le=100, description="가동률 (%)")
    total_restarts: int = Field(..., ge=0, description="총 재시작 횟수")
    total_errors: int = Field(..., ge=0, description="총 오류 횟수")
    average_cpu_usage: float = Field(..., ge=0, description="평균 CPU 사용률 (%)")
    average_memory_usage: float = Field(..., ge=0, description="평균 메모리 사용률 (%)")
    peak_cpu_usage: float = Field(..., ge=0, description="최대 CPU 사용률 (%)")
    peak_memory_usage: float = Field(..., ge=0, description="최대 메모리 사용률 (%)")
    last_24h_stats: Dict[str, Any] = Field(default_factory=dict, description="최근 24시간 통계")
    period: str = Field(..., description="통계 기간")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

# ===== API 요청/응답 모델 =====

class GetServicesRequest(BaseModel):
    """서비스 목록 조회 요청 모델"""
    include_metrics: bool = Field(default=False, description="메트릭 포함 여부")
    include_health: bool = Field(default=False, description="헬스 체크 포함 여부")
    status_filter: Optional[List[ServiceStatus]] = Field(None, description="상태 필터")
    type_filter: Optional[List[ServiceType]] = Field(None, description="타입 필터")

class GetServicesResponse(BaseModel):
    """서비스 목록 조회 응답 모델"""
    services: List[ServiceInfo] = Field(..., description="서비스 목록")
    total: int = Field(..., ge=0, description="총 서비스 수")
    running: int = Field(..., ge=0, description="실행 중인 서비스 수")
    stopped: int = Field(..., ge=0, description="중지된 서비스 수")
    error: int = Field(..., ge=0, description="오류 상태 서비스 수")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class GetServiceLogsRequest(BaseModel):
    """서비스 로그 조회 요청 모델"""
    service_id: str = Field(..., description="서비스 ID")
    limit: int = Field(default=100, ge=1, le=1000, description="조회 개수")
    offset: int = Field(default=0, ge=0, description="오프셋")
    filter: Optional[ServiceLogFilter] = Field(None, description="로그 필터")

class GetServiceLogsResponse(BaseModel):
    """서비스 로그 조회 응답 모델"""
    logs: List[ServiceLog] = Field(..., description="로그 목록")
    total: int = Field(..., ge=0, description="전체 로그 수")
    has_more: bool = Field(..., description="더 많은 로그 존재 여부")
    service_id: str = Field(..., description="서비스 ID")

class GetServiceMetricsRequest(BaseModel):
    """서비스 메트릭 조회 요청 모델"""
    service_id: str = Field(..., description="서비스 ID")
    period: str = Field(default="1h", regex="^(1h|6h|24h|7d)$", description="조회 기간")
    interval: Optional[int] = Field(None, ge=60, le=3600, description="측정 간격 (초)")

class GetServiceMetricsResponse(BaseModel):
    """서비스 메트릭 조회 응답 모델"""
    metrics: List[ServiceMetrics] = Field(..., description="메트릭 목록")
    service_id: str = Field(..., description="서비스 ID")
    period: str = Field(..., description="조회 기간")
    interval: int = Field(..., description="측정 간격")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class UpdateServiceConfigRequest(BaseModel):
    """서비스 설정 업데이트 요청 모델"""
    service_id: str = Field(..., description="서비스 ID")
    config: Dict[str, Any] = Field(..., description="설정 데이터")
    restart_required: bool = Field(default=False, description="재시작 필요 여부")

class UpdateServiceConfigResponse(BaseModel):
    """서비스 설정 업데이트 응답 모델"""
    service_id: str = Field(..., description="서비스 ID")
    config: ServiceConfig = Field(..., description="업데이트된 설정")
    restart_required: bool = Field(..., description="재시작 필요 여부")
    applied_changes: List[str] = Field(..., description="적용된 변경사항")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

# ===== 서비스 모니터링 모델 =====

class ServiceMonitoringState(BaseModel):
    """서비스 모니터링 상태 모델"""
    service_id: str = Field(..., description="서비스 ID")
    is_monitoring: bool = Field(..., description="모니터링 상태")
    check_interval: int = Field(..., ge=5, description="체크 간격 (초)")
    last_check: Optional[datetime] = Field(None, description="마지막 체크 시간")
    next_check: Optional[datetime] = Field(None, description="다음 체크 시간")
    consecutive_failures: int = Field(default=0, ge=0, description="연속 실패 횟수")
    total_checks: int = Field(default=0, ge=0, description="총 체크 횟수")
    failed_checks: int = Field(default=0, ge=0, description="실패한 체크 횟수")

class ServiceRegistry(BaseModel):
    """서비스 레지스트리 모델"""
    services: Dict[str, ServiceInfo] = Field(default_factory=dict, description="서비스 맵")
    dependencies: List[ServiceDependency] = Field(default_factory=list, description="의존성 목록")
    monitoring_states: Dict[str, ServiceMonitoringState] = Field(default_factory=dict, description="모니터링 상태 맵")
    last_updated: datetime = Field(default_factory=datetime.now, description="마지막 업데이트 시간")

# ===== 서비스 백업/복원 모델 =====

class ServiceBackup(BaseModel):
    """서비스 백업 모델"""
    id: str = Field(..., description="백업 ID")
    service_id: str = Field(..., description="서비스 ID")
    backup_type: str = Field(..., regex="^(config|logs|data|full)$", description="백업 타입")
    file_path: str = Field(..., description="백업 파일 경로")
    size: int = Field(..., ge=0, description="백업 크기 (bytes)")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    expires_at: Optional[datetime] = Field(None, description="만료 시간")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")

class ServiceRestoreRequest(BaseModel):
    """서비스 복원 요청 모델"""
    service_id: str = Field(..., description="서비스 ID")
    backup_id: str = Field(..., description="백업 ID")
    restore_type: str = Field(..., regex="^(config|logs|data|full)$", description="복원 타입")
    force: bool = Field(default=False, description="강제 복원 여부")

class ServiceRestoreResponse(BaseModel):
    """서비스 복원 응답 모델"""
    service_id: str = Field(..., description="서비스 ID")
    backup_id: str = Field(..., description="백업 ID")
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")
    restored_items: List[str] = Field(..., description="복원된 항목 목록")
    timestamp: datetime = Field(default_factory=datetime.now, description="복원 시간")

# ===== 레거시 호환성 모델 =====

class ServiceAction(BaseModel):
    """서비스 액션 모델 (레거시 호환성)"""
    action: str = Field(..., regex="^(start|stop|restart)$", description="수행할 액션")
    service_id: str = Field(..., description="대상 서비스 ID")
    parameters: Optional[Dict[str, Any]] = Field(None, description="액션 매개변수")

class ServiceStatus(BaseModel):
    """서비스 상태 응답 모델 (레거시 호환성)"""
    service_id: str = Field(..., description="서비스 ID")
    status: str = Field(..., description="현재 상태")
    message: str = Field(..., description="상태 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="상태 확인 시간")