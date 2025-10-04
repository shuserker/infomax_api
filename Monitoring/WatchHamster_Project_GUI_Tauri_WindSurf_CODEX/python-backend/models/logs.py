"""
로그 관련 데이터 모델
로깅 시스템을 위한 Pydantic 모델들
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

class LogLevel(str, Enum):
    """로그 레벨 열거형"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogSource(str, Enum):
    """로그 소스 열거형"""
    SYSTEM = "system"
    SERVICE = "service"
    API = "api"
    WEBSOCKET = "websocket"
    NEWS = "news"
    WEBHOOK = "webhook"
    GIT = "git"
    CUSTOM = "custom"

class LogFormat(str, Enum):
    """로그 형식 열거형"""
    TEXT = "txt"
    JSON = "json"
    CSV = "csv"

class LogRotation(str, Enum):
    """로그 로테이션 열거형"""
    DAILY = "daily"
    WEEKLY = "weekly"
    SIZE_BASED = "size-based"

# ===== 로그 엔트리 모델 =====

class LogEntry(BaseModel):
    """로그 엔트리 모델"""
    id: str = Field(..., description="로그 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="로그 시간")
    level: LogLevel = Field(..., description="로그 레벨")
    message: str = Field(..., description="로그 메시지")
    source: LogSource = Field(default=LogSource.SYSTEM, description="로그 소스")
    component: Optional[str] = Field(None, description="컴포넌트")
    service_id: Optional[str] = Field(None, description="서비스 ID")
    correlation_id: Optional[str] = Field(None, description="상관관계 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    session_id: Optional[str] = Field(None, description="세션 ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")
    stack_trace: Optional[str] = Field(None, description="스택 트레이스")
    tags: Optional[List[str]] = Field(None, description="태그")

class LogContext(BaseModel):
    """로그 컨텍스트 모델"""
    request_id: Optional[str] = Field(None, description="요청 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    session_id: Optional[str] = Field(None, description="세션 ID")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")

class StructuredLogEntry(LogEntry):
    """구조화된 로그 엔트리 모델"""
    context: Optional[LogContext] = Field(None, description="로그 컨텍스트")
    duration: Optional[float] = Field(None, ge=0, description="실행 시간 (밀리초)")
    status_code: Optional[int] = Field(None, description="상태 코드")
    error_code: Optional[str] = Field(None, description="오류 코드")
    performance_metrics: Optional[Dict[str, float]] = Field(None, description="성능 메트릭")

# ===== 로그 필터 모델 =====

class LogFilter(BaseModel):
    """로그 필터 모델"""
    levels: Optional[List[LogLevel]] = Field(None, description="로그 레벨 필터")
    sources: Optional[List[LogSource]] = Field(None, description="소스 필터")
    components: Optional[List[str]] = Field(None, description="컴포넌트 필터")
    service_ids: Optional[List[str]] = Field(None, description="서비스 ID 필터")
    search: Optional[str] = Field(None, description="검색어")
    start_time: Optional[datetime] = Field(None, description="시작 시간")
    end_time: Optional[datetime] = Field(None, description="종료 시간")
    correlation_id: Optional[str] = Field(None, description="상관관계 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    tags: Optional[List[str]] = Field(None, description="태그 필터")
    has_error: Optional[bool] = Field(None, description="오류 포함 여부")

class LogAggregation(BaseModel):
    """로그 집계 모델"""
    group_by: List[str] = Field(..., description="그룹화 필드")
    time_interval: Optional[str] = Field(None, pattern="^(1m|5m|15m|1h|6h|24h)$", description="시간 간격")
    metrics: List[str] = Field(default_factory=list, description="집계 메트릭")

# ===== 로그 통계 모델 =====

class LogStatistics(BaseModel):
    """로그 통계 모델"""
    total_logs: int = Field(..., ge=0, description="총 로그 수")
    by_level: Dict[LogLevel, int] = Field(..., description="레벨별 로그 수")
    by_source: Dict[LogSource, int] = Field(..., description="소스별 로그 수")
    by_component: Dict[str, int] = Field(default_factory=dict, description="컴포넌트별 로그 수")
    error_rate: float = Field(..., ge=0, le=100, description="오류율 (%)")
    warning_rate: float = Field(..., ge=0, le=100, description="경고율 (%)")
    average_logs_per_minute: float = Field(..., ge=0, description="분당 평균 로그 수")
    peak_logs_per_minute: float = Field(..., ge=0, description="분당 최대 로그 수")
    period: str = Field(..., description="통계 기간")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

class LogTrend(BaseModel):
    """로그 트렌드 모델"""
    timestamp: datetime = Field(..., description="시간")
    total_count: int = Field(..., ge=0, description="총 로그 수")
    error_count: int = Field(..., ge=0, description="오류 로그 수")
    warning_count: int = Field(..., ge=0, description="경고 로그 수")
    info_count: int = Field(..., ge=0, description="정보 로그 수")
    debug_count: int = Field(..., ge=0, description="디버그 로그 수")

class LogAnalytics(BaseModel):
    """로그 분석 모델"""
    statistics: LogStatistics = Field(..., description="로그 통계")
    trends: List[LogTrend] = Field(..., description="로그 트렌드")
    top_errors: List[Dict[str, Any]] = Field(default_factory=list, description="상위 오류")
    top_components: List[Dict[str, Any]] = Field(default_factory=list, description="상위 컴포넌트")
    anomalies: List[Dict[str, Any]] = Field(default_factory=list, description="이상 징후")

# ===== 로그 설정 모델 =====

class LogRetentionPolicy(BaseModel):
    """로그 보존 정책 모델"""
    max_age_days: int = Field(default=30, ge=1, le=365, description="최대 보존 기간 (일)")
    max_size_mb: int = Field(default=1000, ge=100, le=10000, description="최대 크기 (MB)")
    max_entries: int = Field(default=1000000, ge=1000, le=10000000, description="최대 엔트리 수")
    auto_cleanup: bool = Field(default=True, description="자동 정리")
    cleanup_interval_hours: int = Field(default=24, ge=1, le=168, description="정리 간격 (시간)")

class LogRotationConfig(BaseModel):
    """로그 로테이션 설정 모델"""
    enabled: bool = Field(default=True, description="로테이션 활성화")
    rotation_type: LogRotation = Field(default=LogRotation.DAILY, description="로테이션 타입")
    max_file_size_mb: int = Field(default=100, ge=1, le=1000, description="최대 파일 크기 (MB)")
    max_files: int = Field(default=10, ge=1, le=100, description="최대 파일 수")
    compress_old_files: bool = Field(default=True, description="오래된 파일 압축")

class LogOutputConfig(BaseModel):
    """로그 출력 설정 모델"""
    console_enabled: bool = Field(default=True, description="콘솔 출력 활성화")
    file_enabled: bool = Field(default=True, description="파일 출력 활성화")
    remote_enabled: bool = Field(default=False, description="원격 출력 활성화")
    file_path: Optional[str] = Field(None, description="로그 파일 경로")
    remote_endpoint: Optional[str] = Field(None, description="원격 엔드포인트")
    format: LogFormat = Field(default=LogFormat.JSON, description="로그 형식")

class LoggingConfig(BaseModel):
    """로깅 설정 모델"""
    level: LogLevel = Field(default=LogLevel.INFO, description="로그 레벨")
    sources: List[LogSource] = Field(default_factory=lambda: list(LogSource), description="활성 소스")
    retention_policy: LogRetentionPolicy = Field(default_factory=LogRetentionPolicy, description="보존 정책")
    rotation_config: LogRotationConfig = Field(default_factory=LogRotationConfig, description="로테이션 설정")
    output_config: LogOutputConfig = Field(default_factory=LogOutputConfig, description="출력 설정")
    structured_logging: bool = Field(default=True, description="구조화된 로깅")
    include_stack_trace: bool = Field(default=True, description="스택 트레이스 포함")
    mask_sensitive_data: bool = Field(default=True, description="민감 데이터 마스킹")

# ===== 로그 알림 모델 =====

class LogAlert(BaseModel):
    """로그 알림 모델"""
    id: str = Field(..., description="알림 ID")
    name: str = Field(..., description="알림 이름")
    description: str = Field(..., description="알림 설명")
    enabled: bool = Field(default=True, description="활성화 여부")
    conditions: Dict[str, Any] = Field(..., description="알림 조건")
    threshold: Union[int, float] = Field(..., description="임계값")
    time_window_minutes: int = Field(default=5, ge=1, le=60, description="시간 창 (분)")
    notification_channels: List[str] = Field(..., description="알림 채널")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    last_triggered: Optional[datetime] = Field(None, description="마지막 트리거 시간")

class LogAlertRule(BaseModel):
    """로그 알림 규칙 모델"""
    field: str = Field(..., description="필드명")
    operator: str = Field(..., pattern="^(equals|contains|greater_than|less_than|regex)$", description="연산자")
    value: Union[str, int, float] = Field(..., description="비교값")
    case_sensitive: bool = Field(default=False, description="대소문자 구분")

class LogAlertCondition(BaseModel):
    """로그 알림 조건 모델"""
    rules: List[LogAlertRule] = Field(..., description="규칙 목록")
    logic: str = Field(default="AND", pattern="^(AND|OR)$", description="논리 연산자")
    count_threshold: Optional[int] = Field(None, ge=1, description="개수 임계값")
    rate_threshold: Optional[float] = Field(None, ge=0, description="비율 임계값")

# ===== 로그 내보내기 모델 =====

class LogExportOptions(BaseModel):
    """로그 내보내기 옵션 모델"""
    format: LogFormat = Field(default=LogFormat.JSON, description="내보내기 형식")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="날짜 범위")
    levels: Optional[List[LogLevel]] = Field(None, description="로그 레벨")
    sources: Optional[List[LogSource]] = Field(None, description="로그 소스")
    max_entries: int = Field(default=10000, ge=1, le=1000000, description="최대 엔트리 수")
    include_metadata: bool = Field(default=True, description="메타데이터 포함")
    compress: bool = Field(default=False, description="압축 여부")

class LogExportJob(BaseModel):
    """로그 내보내기 작업 모델"""
    id: str = Field(..., description="작업 ID")
    status: str = Field(..., pattern="^(pending|running|completed|failed|cancelled)$", description="작업 상태")
    options: LogExportOptions = Field(..., description="내보내기 옵션")
    progress: float = Field(default=0.0, ge=0, le=100, description="진행률 (%)")
    total_entries: Optional[int] = Field(None, ge=0, description="총 엔트리 수")
    processed_entries: int = Field(default=0, ge=0, description="처리된 엔트리 수")
    file_path: Optional[str] = Field(None, description="내보내기 파일 경로")
    file_size: Optional[int] = Field(None, ge=0, description="파일 크기 (bytes)")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    started_at: Optional[datetime] = Field(None, description="시작 시간")
    completed_at: Optional[datetime] = Field(None, description="완료 시간")
    error_message: Optional[str] = Field(None, description="오류 메시지")

# ===== API 요청/응답 모델 =====

class GetLogsRequest(BaseModel):
    """로그 조회 요청 모델"""
    filter: Optional[LogFilter] = Field(None, description="로그 필터")
    limit: int = Field(default=100, ge=1, le=10000, description="조회 개수")
    offset: int = Field(default=0, ge=0, description="오프셋")
    sort_by: str = Field(default="timestamp", description="정렬 필드")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="정렬 순서")
    include_metadata: bool = Field(default=True, description="메타데이터 포함")

class GetLogsResponse(BaseModel):
    """로그 조회 응답 모델"""
    logs: List[LogEntry] = Field(..., description="로그 목록")
    total: int = Field(..., ge=0, description="전체 로그 수")
    filtered: int = Field(..., ge=0, description="필터링된 로그 수")
    has_more: bool = Field(..., description="더 많은 로그 존재 여부")
    next_offset: Optional[int] = Field(None, description="다음 오프셋")

class GetLogStatisticsRequest(BaseModel):
    """로그 통계 조회 요청 모델"""
    filter: Optional[LogFilter] = Field(None, description="로그 필터")
    period: str = Field(default="24h", pattern="^(1h|6h|24h|7d|30d)$", description="통계 기간")
    aggregation: Optional[LogAggregation] = Field(None, description="집계 설정")

class GetLogStatisticsResponse(BaseModel):
    """로그 통계 조회 응답 모델"""
    analytics: LogAnalytics = Field(..., description="로그 분석")
    period: str = Field(..., description="통계 기간")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

class CreateLogExportRequest(BaseModel):
    """로그 내보내기 생성 요청 모델"""
    options: LogExportOptions = Field(..., description="내보내기 옵션")
    filter: Optional[LogFilter] = Field(None, description="로그 필터")

class CreateLogExportResponse(BaseModel):
    """로그 내보내기 생성 응답 모델"""
    job: LogExportJob = Field(..., description="내보내기 작업")

class GetLogExportStatusRequest(BaseModel):
    """로그 내보내기 상태 조회 요청 모델"""
    job_id: str = Field(..., description="작업 ID")

class GetLogExportStatusResponse(BaseModel):
    """로그 내보내기 상태 조회 응답 모델"""
    job: LogExportJob = Field(..., description="내보내기 작업")
    download_url: Optional[str] = Field(None, description="다운로드 URL")
    expires_at: Optional[datetime] = Field(None, description="만료 시간")

class UpdateLoggingConfigRequest(BaseModel):
    """로깅 설정 업데이트 요청 모델"""
    config: LoggingConfig = Field(..., description="로깅 설정")

class UpdateLoggingConfigResponse(BaseModel):
    """로깅 설정 업데이트 응답 모델"""
    config: LoggingConfig = Field(..., description="업데이트된 로깅 설정")
    restart_required: bool = Field(..., description="재시작 필요 여부")

# ===== 로그 스트리밍 모델 =====

class LogStreamConfig(BaseModel):
    """로그 스트림 설정 모델"""
    filter: Optional[LogFilter] = Field(None, description="스트림 필터")
    buffer_size: int = Field(default=100, ge=1, le=1000, description="버퍼 크기")
    flush_interval_ms: int = Field(default=1000, ge=100, le=10000, description="플러시 간격 (밀리초)")
    include_historical: bool = Field(default=False, description="과거 로그 포함")
    historical_limit: int = Field(default=100, ge=1, le=10000, description="과거 로그 제한")

class LogStreamMessage(BaseModel):
    """로그 스트림 메시지 모델"""
    type: str = Field(..., pattern="^(logs|status|error)$", description="메시지 타입")
    data: Union[List[LogEntry], Dict[str, Any]] = Field(..., description="메시지 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")
    stream_id: str = Field(..., description="스트림 ID")

class LogStreamStatus(BaseModel):
    """로그 스트림 상태 모델"""
    stream_id: str = Field(..., description="스트림 ID")
    is_active: bool = Field(..., description="활성 상태")
    connected_clients: int = Field(..., ge=0, description="연결된 클라이언트 수")
    messages_sent: int = Field(..., ge=0, description="전송된 메시지 수")
    last_activity: datetime = Field(..., description="마지막 활동 시간")
    buffer_usage: float = Field(..., ge=0, le=100, description="버퍼 사용률 (%)")

# ===== 로그 검색 모델 =====

class LogSearchQuery(BaseModel):
    """로그 검색 쿼리 모델"""
    query: str = Field(..., description="검색 쿼리")
    fields: Optional[List[str]] = Field(None, description="검색 대상 필드")
    fuzzy: bool = Field(default=False, description="퍼지 검색")
    case_sensitive: bool = Field(default=False, description="대소문자 구분")
    regex: bool = Field(default=False, description="정규식 사용")

class LogSearchResult(BaseModel):
    """로그 검색 결과 모델"""
    log: LogEntry = Field(..., description="로그 엔트리")
    score: float = Field(..., ge=0, le=1, description="검색 점수")
    highlights: Dict[str, List[str]] = Field(default_factory=dict, description="하이라이트")
    matched_fields: List[str] = Field(default_factory=list, description="매칭된 필드")

class LogSearchResponse(BaseModel):
    """로그 검색 응답 모델"""
    results: List[LogSearchResult] = Field(..., description="검색 결과")
    total_hits: int = Field(..., ge=0, description="총 히트 수")
    search_time_ms: float = Field(..., ge=0, description="검색 시간 (밀리초)")
    query: LogSearchQuery = Field(..., description="검색 쿼리")

# ===== 로그 백업 모델 =====

class LogBackupConfig(BaseModel):
    """로그 백업 설정 모델"""
    enabled: bool = Field(default=False, description="백업 활성화")
    schedule: str = Field(default="0 2 * * *", description="백업 스케줄 (cron)")
    retention_days: int = Field(default=90, ge=1, le=365, description="백업 보존 기간 (일)")
    compression: bool = Field(default=True, description="압축 사용")
    encryption: bool = Field(default=False, description="암호화 사용")
    storage_path: str = Field(..., description="저장 경로")
    max_backup_size_gb: int = Field(default=10, ge=1, le=100, description="최대 백업 크기 (GB)")

class LogBackupJob(BaseModel):
    """로그 백업 작업 모델"""
    id: str = Field(..., description="백업 작업 ID")
    status: str = Field(..., pattern="^(pending|running|completed|failed)$", description="작업 상태")
    config: LogBackupConfig = Field(..., description="백업 설정")
    start_date: datetime = Field(..., description="백업 시작 날짜")
    end_date: datetime = Field(..., description="백업 종료 날짜")
    total_logs: Optional[int] = Field(None, ge=0, description="총 로그 수")
    processed_logs: int = Field(default=0, ge=0, description="처리된 로그 수")
    backup_file_path: Optional[str] = Field(None, description="백업 파일 경로")
    backup_file_size: Optional[int] = Field(None, ge=0, description="백업 파일 크기 (bytes)")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    started_at: Optional[datetime] = Field(None, description="시작 시간")
    completed_at: Optional[datetime] = Field(None, description="완료 시간")
    error_message: Optional[str] = Field(None, description="오류 메시지")