"""
데이터 모델 정의
Pydantic 모델을 사용한 데이터 검증 및 직렬화
"""

# 뉴스 관련 모델
from .news import (
    NewsType, NewsStatusType, NewsStatus, NewsHistory, NewsStatistics,
    NewsSettings, NewsStatusSummary, NewsAlert, NewsMonitoringState,
    ExchangeRateData, NewYorkMarketData, KospiCloseData,
    GetNewsStatusRequest, GetNewsStatusResponse,
    RefreshNewsRequest, RefreshNewsResponse,
    GetNewsHistoryRequest, GetNewsHistoryResponse,
    GetNewsStatisticsRequest, GetNewsStatisticsResponse,
    PoscoNewsWebhookPayload, NewsWebhookPayload
)

# 시스템 관련 모델
from .system import (
    SystemHealthStatus, ServiceStatus, ProcessStatus,
    SystemInfo, SystemMetrics, PerformanceMetrics, ProcessInfo,
    ServiceInfo, GitStatus, SystemStatus, SystemSettings,
    SystemAlert, SystemAction, SystemActionResult,
    ResourceUsage, ResourceSummary, ServiceControl, ServiceControlResult,
    MonitoringState, HealthCheck, SystemHealthReport, SystemStatistics,
    GetSystemStatusRequest, GetSystemStatusResponse,
    GetSystemMetricsRequest, GetSystemMetricsResponse,
    ControlServiceRequest, ControlServiceResponse,
    UpdateSystemSettingsRequest, UpdateSystemSettingsResponse
)

# 웹훅 관련 모델
from .webhooks import (
    WebhookType, WebhookStatus, AlertLevel, MessageType,
    WebhookConfig, WebhookMessage, WebhookHistory, WebhookTemplate,
    WebhookStatistics, WebhookSettings, WebhookQueue, WebhookQueueItem,
    PoscoNewsWebhookPayload, PoscoSystemWebhookPayload,
    DoorayMessage, DoorayAttachment, DoorayField,
    SendWebhookRequest, SendWebhookResponse,
    GetWebhookHistoryRequest, GetWebhookHistoryResponse,
    TestWebhookRequest, TestWebhookResponse,
    GetWebhookStatisticsRequest, GetWebhookStatisticsResponse,
    WebhookEvent, WebhookAlertRule, WebhookBatchOperation,
    WebhookMonitoringState
)

# 서비스 관련 모델
from .services import (
    ServiceStatus, ServiceAction, ServiceType,
    ServiceInfo, ServiceMetrics, ServiceHealthCheck,
    ServiceActionRequest, ServiceActionResult,
    ServiceLog, ServiceLogFilter, ServiceConfig, ServiceDependency,
    ServiceEvent, ServiceAlert, ServiceStatistics,
    GetServicesRequest, GetServicesResponse,
    GetServiceLogsRequest, GetServiceLogsResponse,
    GetServiceMetricsRequest, GetServiceMetricsResponse,
    UpdateServiceConfigRequest, UpdateServiceConfigResponse,
    ServiceMonitoringState, ServiceRegistry, ServiceBackup,
    ServiceRestoreRequest, ServiceRestoreResponse
)

# 설정 관련 모델
from .settings import (
    ThemeMode, Language, LogLevel, AuthType,
    ApiSettings, UiSettings, LoggingSettings, SecuritySettings, BackupSettings,
    AppSettings, SettingsChange, SettingsChangeHistory,
    SettingsValidationResult, SettingsExport, SettingsImportOptions,
    SettingsImportResult, SettingsTemplate,
    GetSettingsRequest, GetSettingsResponse,
    UpdateSettingsRequest, UpdateSettingsResponse,
    ResetSettingsRequest, ResetSettingsResponse,
    ExportSettingsRequest, ExportSettingsResponse,
    ImportSettingsRequest, ImportSettingsResponse,
    ApplyTemplateRequest, ApplyTemplateResponse,
    SettingsSync, SettingsConflict
)

# WebSocket 관련 모델
from .websocket import (
    WSMessageType, WSConnectionStatus, NotificationLevel,
    WSMessage, WSConnectionState, WSConfig,
    WSConnectionMessage, WSPingMessage, WSPongMessage,
    WSNewsUpdateMessage, WSSystemUpdateMessage, WSServiceEventMessage,
    WSAlertMessage, WSLogUpdateMessage, WSMetricsUpdateMessage,
    WSWebhookEventMessage, WSErrorMessage, WSNotificationMessage,
    WSStatistics, WSState, WSMessageFilter, WSMessageHistory,
    WSConnectionStats, WSSecurityConfig, WSMonitoringData,
    WSHealthCheck, WSEvent, WSEventLog, WSClient, WSClientRegistry,
    WSConnectRequest, WSConnectResponse,
    WSSubscribeRequest, WSSubscribeResponse,
    WSUnsubscribeRequest, WSUnsubscribeResponse,
    GetWSStatsRequest, GetWSStatsResponse
)

# 로그 관련 모델
from .logs import (
    LogLevel, LogSource, LogFormat, LogRotation,
    LogEntry, LogContext, StructuredLogEntry,
    LogFilter, LogAggregation, LogStatistics, LogTrend, LogAnalytics,
    LogRetentionPolicy, LogRotationConfig, LogOutputConfig, LoggingConfig,
    LogAlert, LogAlertRule, LogAlertCondition,
    LogExportOptions, LogExportJob,
    GetLogsRequest, GetLogsResponse,
    GetLogStatisticsRequest, GetLogStatisticsResponse,
    CreateLogExportRequest, CreateLogExportResponse,
    GetLogExportStatusRequest, GetLogExportStatusResponse,
    UpdateLoggingConfigRequest, UpdateLoggingConfigResponse,
    LogStreamConfig, LogStreamMessage, LogStreamStatus,
    LogSearchQuery, LogSearchResult, LogSearchResponse,
    LogBackupConfig, LogBackupJob
)

# 레거시 호환성을 위한 별칭
from .system import ServiceFailure, StabilityMetrics
from .webhooks import WebhookPayload, WebhookResponse, WebhookStats
from .services import ServiceAction as LegacyServiceAction, ServiceStatus as LegacyServiceStatus

__all__ = [
    # 뉴스 모델
    "NewsType", "NewsStatusType", "NewsStatus", "NewsHistory", "NewsStatistics",
    "NewsSettings", "NewsStatusSummary", "NewsAlert", "NewsMonitoringState",
    "ExchangeRateData", "NewYorkMarketData", "KospiCloseData",
    "GetNewsStatusRequest", "GetNewsStatusResponse",
    "RefreshNewsRequest", "RefreshNewsResponse",
    "GetNewsHistoryRequest", "GetNewsHistoryResponse",
    "GetNewsStatisticsRequest", "GetNewsStatisticsResponse",
    "PoscoNewsWebhookPayload", "NewsWebhookPayload",
    
    # 시스템 모델
    "SystemHealthStatus", "ServiceStatus", "ProcessStatus",
    "SystemInfo", "SystemMetrics", "PerformanceMetrics", "ProcessInfo",
    "ServiceInfo", "GitStatus", "SystemStatus", "SystemSettings",
    "SystemAlert", "SystemAction", "SystemActionResult",
    "ResourceUsage", "ResourceSummary", "ServiceControl", "ServiceControlResult",
    "MonitoringState", "HealthCheck", "SystemHealthReport", "SystemStatistics",
    "GetSystemStatusRequest", "GetSystemStatusResponse",
    "GetSystemMetricsRequest", "GetSystemMetricsResponse",
    "ControlServiceRequest", "ControlServiceResponse",
    "UpdateSystemSettingsRequest", "UpdateSystemSettingsResponse",
    
    # 웹훅 모델
    "WebhookType", "WebhookStatus", "AlertLevel", "MessageType",
    "WebhookConfig", "WebhookMessage", "WebhookHistory", "WebhookTemplate",
    "WebhookStatistics", "WebhookSettings", "WebhookQueue", "WebhookQueueItem",
    "PoscoSystemWebhookPayload", "DoorayMessage", "DoorayAttachment", "DoorayField",
    "SendWebhookRequest", "SendWebhookResponse",
    "GetWebhookHistoryRequest", "GetWebhookHistoryResponse",
    "TestWebhookRequest", "TestWebhookResponse",
    "GetWebhookStatisticsRequest", "GetWebhookStatisticsResponse",
    "WebhookEvent", "WebhookAlertRule", "WebhookBatchOperation",
    "WebhookMonitoringState",
    
    # 서비스 모델
    "ServiceType", "ServiceMetrics", "ServiceHealthCheck",
    "ServiceActionRequest", "ServiceActionResult",
    "ServiceLog", "ServiceLogFilter", "ServiceConfig", "ServiceDependency",
    "ServiceEvent", "ServiceAlert", "ServiceStatistics",
    "GetServicesRequest", "GetServicesResponse",
    "GetServiceLogsRequest", "GetServiceLogsResponse",
    "GetServiceMetricsRequest", "GetServiceMetricsResponse",
    "UpdateServiceConfigRequest", "UpdateServiceConfigResponse",
    "ServiceMonitoringState", "ServiceRegistry", "ServiceBackup",
    "ServiceRestoreRequest", "ServiceRestoreResponse",
    
    # 설정 모델
    "ThemeMode", "Language", "LogLevel", "AuthType",
    "ApiSettings", "UiSettings", "LoggingSettings", "SecuritySettings", "BackupSettings",
    "AppSettings", "SettingsChange", "SettingsChangeHistory",
    "SettingsValidationResult", "SettingsExport", "SettingsImportOptions",
    "SettingsImportResult", "SettingsTemplate",
    "GetSettingsRequest", "GetSettingsResponse",
    "UpdateSettingsRequest", "UpdateSettingsResponse",
    "ResetSettingsRequest", "ResetSettingsResponse",
    "ExportSettingsRequest", "ExportSettingsResponse",
    "ImportSettingsRequest", "ImportSettingsResponse",
    "ApplyTemplateRequest", "ApplyTemplateResponse",
    "SettingsSync", "SettingsConflict",
    
    # WebSocket 모델
    "WSMessageType", "WSConnectionStatus", "NotificationLevel",
    "WSMessage", "WSConnectionState", "WSConfig",
    "WSConnectionMessage", "WSPingMessage", "WSPongMessage",
    "WSNewsUpdateMessage", "WSSystemUpdateMessage", "WSServiceEventMessage",
    "WSAlertMessage", "WSLogUpdateMessage", "WSMetricsUpdateMessage",
    "WSWebhookEventMessage", "WSErrorMessage", "WSNotificationMessage",
    "WSStatistics", "WSState", "WSMessageFilter", "WSMessageHistory",
    "WSConnectionStats", "WSSecurityConfig", "WSMonitoringData",
    "WSHealthCheck", "WSEvent", "WSEventLog", "WSClient", "WSClientRegistry",
    "WSConnectRequest", "WSConnectResponse",
    "WSSubscribeRequest", "WSSubscribeResponse",
    "WSUnsubscribeRequest", "WSUnsubscribeResponse",
    "GetWSStatsRequest", "GetWSStatsResponse",
    
    # 로그 모델
    "LogSource", "LogFormat", "LogRotation",
    "LogEntry", "LogContext", "StructuredLogEntry",
    "LogFilter", "LogAggregation", "LogStatistics", "LogTrend", "LogAnalytics",
    "LogRetentionPolicy", "LogRotationConfig", "LogOutputConfig", "LoggingConfig",
    "LogAlert", "LogAlertRule", "LogAlertCondition",
    "LogExportOptions", "LogExportJob",
    "GetLogsRequest", "GetLogsResponse",
    "GetLogStatisticsRequest", "GetLogStatisticsResponse",
    "CreateLogExportRequest", "CreateLogExportResponse",
    "GetLogExportStatusRequest", "GetLogExportStatusResponse",
    "UpdateLoggingConfigRequest", "UpdateLoggingConfigResponse",
    "LogStreamConfig", "LogStreamMessage", "LogStreamStatus",
    "LogSearchQuery", "LogSearchResult", "LogSearchResponse",
    "LogBackupConfig", "LogBackupJob",
    
    # 레거시 호환성
    "ServiceFailure", "StabilityMetrics",
    "WebhookPayload", "WebhookResponse", "WebhookStats",
    "LegacyServiceAction", "LegacyServiceStatus"
]