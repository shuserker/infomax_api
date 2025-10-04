"""
설정 관련 데이터 모델
애플리케이션 전체 설정을 위한 Pydantic 모델들
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum

class ThemeMode(str, Enum):
    """테마 모드 열거형"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class Language(str, Enum):
    """언어 열거형"""
    KOREAN = "ko"
    ENGLISH = "en"

class LogLevel(str, Enum):
    """로그 레벨 열거형"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuthType(str, Enum):
    """인증 타입 열거형"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"

class BackupLocation(str, Enum):
    """백업 위치 열거형"""
    LOCAL = "local"
    CLOUD = "cloud"
    NETWORK = "network"

class CompressionAlgorithm(str, Enum):
    """압축 알고리즘 열거형"""
    GZIP = "gzip"
    ZIP = "zip"
    TAR_GZ = "tar.gz"

class EncryptionAlgorithm(str, Enum):
    """암호화 알고리즘 열거형"""
    AES_256 = "AES-256"
    AES_128 = "AES-128"

# ===== API 설정 모델 =====

class InfomaxApiSettings(BaseModel):
    """INFOMAX API 설정 모델"""
    base_url: HttpUrl = Field(..., description="기본 URL")
    timeout: int = Field(default=30, ge=5, le=120, description="타임아웃 (초)")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="재시도 횟수")
    retry_delay: int = Field(default=5, ge=1, le=30, description="재시도 지연 (초)")
    rate_limit: Dict[str, Any] = Field(default_factory=dict, description="속도 제한 설정")
    headers: Optional[Dict[str, str]] = Field(None, description="추가 헤더")
    auth: Dict[str, Any] = Field(default_factory=dict, description="인증 설정")

class BackendApiSettings(BaseModel):
    """백엔드 API 설정 모델"""
    base_url: HttpUrl = Field(..., description="기본 URL")
    timeout: int = Field(default=30, ge=5, le=60, description="타임아웃 (초)")
    retry_attempts: int = Field(default=3, ge=0, le=5, description="재시도 횟수")
    websocket_url: HttpUrl = Field(..., description="WebSocket URL")
    websocket_reconnect: Dict[str, Any] = Field(default_factory=dict, description="WebSocket 재연결 설정")

class ApiSettings(BaseModel):
    """API 설정 모델"""
    infomax_api: InfomaxApiSettings = Field(..., description="INFOMAX API 설정")
    backend_api: BackendApiSettings = Field(..., description="백엔드 API 설정")

# ===== UI 설정 모델 =====

class AutoRefreshSettings(BaseModel):
    """자동 새로고침 설정 모델"""
    enabled: bool = Field(default=True, description="자동 새로고침 활성화")
    interval: int = Field(default=5000, ge=1000, le=300000, description="새로고침 간격 (밀리초)")

class DashboardSettings(BaseModel):
    """대시보드 설정 모델"""
    layout: str = Field(default="grid", regex="^(grid|list|compact)$", description="레이아웃")
    show_charts: bool = Field(default=True, description="차트 표시")
    chart_update_interval: int = Field(default=5000, ge=1000, le=60000, description="차트 업데이트 간격 (밀리초)")
    max_recent_alerts: int = Field(default=10, ge=5, le=100, description="최근 알림 최대 개수")

class TableSettings(BaseModel):
    """테이블 설정 모델"""
    page_size: int = Field(default=20, ge=10, le=100, description="페이지 크기")
    show_pagination: bool = Field(default=True, description="페이지네이션 표시")
    sortable_columns: bool = Field(default=True, description="정렬 가능한 컬럼")
    filterable_columns: bool = Field(default=True, description="필터 가능한 컬럼")

class NotificationUISettings(BaseModel):
    """알림 UI 설정 모델"""
    enabled: bool = Field(default=True, description="알림 활성화")
    position: str = Field(default="top-right", regex="^(top-right|top-left|bottom-right|bottom-left)$", description="알림 위치")
    duration: int = Field(default=5000, ge=1000, le=30000, description="알림 지속 시간 (밀리초)")
    max_visible: int = Field(default=5, ge=1, le=10, description="최대 표시 개수")
    sound: bool = Field(default=False, description="소리 알림")

class UiSettings(BaseModel):
    """UI 설정 모델"""
    theme: ThemeMode = Field(default=ThemeMode.LIGHT, description="테마")
    language: Language = Field(default=Language.KOREAN, description="언어")
    posco_branding: bool = Field(default=True, description="POSCO 브랜딩")
    animations: bool = Field(default=True, description="애니메이션")
    sound_notifications: bool = Field(default=False, description="소리 알림")
    auto_refresh: AutoRefreshSettings = Field(default_factory=AutoRefreshSettings, description="자동 새로고침 설정")
    dashboard: DashboardSettings = Field(default_factory=DashboardSettings, description="대시보드 설정")
    tables: TableSettings = Field(default_factory=TableSettings, description="테이블 설정")
    notifications: NotificationUISettings = Field(default_factory=NotificationUISettings, description="알림 설정")

# ===== 로깅 설정 모델 =====

class FileLoggingSettings(BaseModel):
    """파일 로깅 설정 모델"""
    enabled: bool = Field(default=True, description="파일 로깅 활성화")
    file_path: Optional[str] = Field(None, description="로그 파일 경로")
    max_file_size: int = Field(default=100, ge=1, le=1000, description="최대 파일 크기 (MB)")
    max_files: int = Field(default=10, ge=1, le=50, description="최대 파일 개수")
    rotation: str = Field(default="daily", regex="^(daily|weekly|size-based)$", description="로테이션 방식")

class RemoteLoggingSettings(BaseModel):
    """원격 로깅 설정 모델"""
    enabled: bool = Field(default=False, description="원격 로깅 활성화")
    endpoint: Optional[HttpUrl] = Field(None, description="원격 로깅 엔드포인트")
    api_key: Optional[str] = Field(None, description="API 키")
    batch_size: int = Field(default=100, ge=1, le=1000, description="배치 크기")
    flush_interval: int = Field(default=30000, ge=1000, le=60000, description="플러시 간격 (밀리초)")

class LoggingFilters(BaseModel):
    """로깅 필터 설정 모델"""
    exclude_components: List[str] = Field(default_factory=list, description="제외할 컴포넌트")
    exclude_levels: List[LogLevel] = Field(default_factory=list, description="제외할 로그 레벨")
    include_only: Optional[List[str]] = Field(None, description="포함할 컴포넌트만")

class LoggingSettings(BaseModel):
    """로깅 설정 모델"""
    level: LogLevel = Field(default=LogLevel.INFO, description="로그 레벨")
    max_entries: int = Field(default=10000, ge=100, le=50000, description="최대 엔트리 수")
    retention_days: int = Field(default=30, ge=1, le=365, description="보존 기간 (일)")
    auto_cleanup: bool = Field(default=True, description="자동 정리")
    file_logging: FileLoggingSettings = Field(default_factory=FileLoggingSettings, description="파일 로깅 설정")
    remote_logging: RemoteLoggingSettings = Field(default_factory=RemoteLoggingSettings, description="원격 로깅 설정")
    filters: LoggingFilters = Field(default_factory=LoggingFilters, description="로깅 필터")

# ===== 보안 설정 모델 =====

class EncryptionSettings(BaseModel):
    """암호화 설정 모델"""
    enabled: bool = Field(default=False, description="암호화 활성화")
    algorithm: EncryptionAlgorithm = Field(default=EncryptionAlgorithm.AES_256, description="암호화 알고리즘")
    key_rotation: Dict[str, Any] = Field(default_factory=dict, description="키 로테이션 설정")

class SessionSettings(BaseModel):
    """세션 설정 모델"""
    timeout: int = Field(default=3600, ge=300, le=86400, description="세션 타임아웃 (초)")
    auto_logout: bool = Field(default=True, description="자동 로그아웃")
    concurrent_sessions: int = Field(default=1, ge=1, le=10, description="동시 세션 수")

class ApiSecuritySettings(BaseModel):
    """API 보안 설정 모델"""
    rate_limiting: bool = Field(default=True, description="속도 제한")
    ip_whitelist: Optional[List[str]] = Field(None, description="IP 화이트리스트")
    require_https: bool = Field(default=True, description="HTTPS 필수")
    cors_origins: List[str] = Field(default_factory=list, description="CORS 허용 오리진")

class DataProtectionSettings(BaseModel):
    """데이터 보호 설정 모델"""
    mask_sensitive_data: bool = Field(default=True, description="민감 데이터 마스킹")
    audit_logging: bool = Field(default=True, description="감사 로깅")
    data_retention_days: int = Field(default=365, ge=1, le=2555, description="데이터 보존 기간 (일)")

class SecuritySettings(BaseModel):
    """보안 설정 모델"""
    encryption: EncryptionSettings = Field(default_factory=EncryptionSettings, description="암호화 설정")
    session: SessionSettings = Field(default_factory=SessionSettings, description="세션 설정")
    api_security: ApiSecuritySettings = Field(default_factory=ApiSecuritySettings, description="API 보안 설정")
    data_protection: DataProtectionSettings = Field(default_factory=DataProtectionSettings, description="데이터 보호 설정")

# ===== 백업 설정 모델 =====

class AutoBackupSettings(BaseModel):
    """자동 백업 설정 모델"""
    enabled: bool = Field(default=False, description="자동 백업 활성화")
    interval: str = Field(default="daily", regex="^(daily|weekly|monthly)$", description="백업 간격")
    time: str = Field(default="02:00", regex=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="백업 시간 (HH:MM)")
    max_backups: int = Field(default=7, ge=1, le=100, description="최대 백업 개수")

class BackupLocationSettings(BaseModel):
    """백업 위치 설정 모델"""
    type: BackupLocation = Field(default=BackupLocation.LOCAL, description="백업 위치 타입")
    path: str = Field(..., description="백업 경로")
    credentials: Optional[Dict[str, str]] = Field(None, description="인증 정보")

class BackupContentSettings(BaseModel):
    """백업 내용 설정 모델"""
    settings: bool = Field(default=True, description="설정 백업")
    logs: bool = Field(default=False, description="로그 백업")
    data: bool = Field(default=True, description="데이터 백업")
    git_state: bool = Field(default=True, description="Git 상태 백업")
    user_data: bool = Field(default=True, description="사용자 데이터 백업")

class BackupCompressionSettings(BaseModel):
    """백업 압축 설정 모델"""
    enabled: bool = Field(default=True, description="압축 활성화")
    algorithm: CompressionAlgorithm = Field(default=CompressionAlgorithm.GZIP, description="압축 알고리즘")
    level: int = Field(default=6, ge=1, le=9, description="압축 레벨")

class BackupEncryptionSettings(BaseModel):
    """백업 암호화 설정 모델"""
    enabled: bool = Field(default=False, description="암호화 활성화")
    password_protected: bool = Field(default=False, description="비밀번호 보호")

class BackupSettings(BaseModel):
    """백업 설정 모델"""
    enabled: bool = Field(default=False, description="백업 활성화")
    auto_backup: AutoBackupSettings = Field(default_factory=AutoBackupSettings, description="자동 백업 설정")
    backup_location: BackupLocationSettings = Field(..., description="백업 위치 설정")
    backup_content: BackupContentSettings = Field(default_factory=BackupContentSettings, description="백업 내용 설정")
    compression: BackupCompressionSettings = Field(default_factory=BackupCompressionSettings, description="압축 설정")
    encryption: BackupEncryptionSettings = Field(default_factory=BackupEncryptionSettings, description="암호화 설정")

# ===== 전체 애플리케이션 설정 모델 =====

class AppSettings(BaseModel):
    """애플리케이션 설정 모델"""
    version: str = Field(default="1.0.0", description="설정 버전")
    last_updated: datetime = Field(default_factory=datetime.now, description="마지막 업데이트 시간")
    api: ApiSettings = Field(..., description="API 설정")
    ui: UiSettings = Field(default_factory=UiSettings, description="UI 설정")
    logging: LoggingSettings = Field(default_factory=LoggingSettings, description="로깅 설정")
    security: SecuritySettings = Field(default_factory=SecuritySettings, description="보안 설정")
    backup: BackupSettings = Field(..., description="백업 설정")
    # 다른 모듈의 설정들은 별도 필드로 참조
    news: Optional[Dict[str, Any]] = Field(None, description="뉴스 설정")
    system: Optional[Dict[str, Any]] = Field(None, description="시스템 설정")
    webhook: Optional[Dict[str, Any]] = Field(None, description="웹훅 설정")

# ===== 설정 변경 이력 모델 =====

class SettingsChange(BaseModel):
    """설정 변경 이력 모델"""
    id: str = Field(..., description="변경 ID")
    field_path: str = Field(..., description="필드 경로")
    old_value: Optional[Any] = Field(None, description="이전 값")
    new_value: Any = Field(..., description="새로운 값")
    changed_by: str = Field(..., description="변경자")
    changed_at: datetime = Field(default_factory=datetime.now, description="변경 시간")
    reason: Optional[str] = Field(None, description="변경 사유")
    auto_applied: bool = Field(default=False, description="자동 적용 여부")

class SettingsChangeHistory(BaseModel):
    """설정 변경 이력 모델"""
    changes: List[SettingsChange] = Field(..., description="변경 목록")
    total: int = Field(..., ge=0, description="전체 변경 수")
    page: int = Field(..., ge=1, description="페이지 번호")
    size: int = Field(..., ge=1, description="페이지 크기")

# ===== 설정 검증 모델 =====

class SettingsValidationError(BaseModel):
    """설정 검증 오류 모델"""
    field_path: str = Field(..., description="필드 경로")
    message: str = Field(..., description="오류 메시지")
    severity: str = Field(..., regex="^(error|warning)$", description="심각도")

class SettingsValidationWarning(BaseModel):
    """설정 검증 경고 모델"""
    field_path: str = Field(..., description="필드 경로")
    message: str = Field(..., description="경고 메시지")

class SettingsValidationResult(BaseModel):
    """설정 검증 결과 모델"""
    valid: bool = Field(..., description="유효성 여부")
    errors: List[SettingsValidationError] = Field(default_factory=list, description="오류 목록")
    warnings: List[SettingsValidationWarning] = Field(default_factory=list, description="경고 목록")

# ===== 설정 내보내기/가져오기 모델 =====

class SettingsExportMetadata(BaseModel):
    """설정 내보내기 메타데이터 모델"""
    app_version: str = Field(..., description="앱 버전")
    platform: str = Field(..., description="플랫폼")
    hostname: str = Field(..., description="호스트명")

class SettingsExport(BaseModel):
    """설정 내보내기 모델"""
    version: str = Field(..., description="내보내기 버전")
    exported_at: datetime = Field(default_factory=datetime.now, description="내보내기 시간")
    exported_by: str = Field(..., description="내보내기 실행자")
    settings: Dict[str, Any] = Field(..., description="설정 데이터")
    metadata: SettingsExportMetadata = Field(..., description="메타데이터")

class SettingsImportOptions(BaseModel):
    """설정 가져오기 옵션 모델"""
    merge: bool = Field(default=True, description="기존 설정과 병합")
    validate: bool = Field(default=True, description="검증 수행")
    backup_before_import: bool = Field(default=True, description="가져오기 전 백업")
    sections: List[str] = Field(default_factory=list, description="가져올 섹션")

class SettingsImportResult(BaseModel):
    """설정 가져오기 결과 모델"""
    success: bool = Field(..., description="성공 여부")
    imported_sections: List[str] = Field(..., description="가져온 섹션")
    skipped_sections: List[str] = Field(..., description="건너뛴 섹션")
    errors: List[str] = Field(default_factory=list, description="오류 목록")
    warnings: List[str] = Field(default_factory=list, description="경고 목록")
    backup_id: Optional[str] = Field(None, description="백업 ID")

# ===== API 요청/응답 모델 =====

class GetSettingsRequest(BaseModel):
    """설정 조회 요청 모델"""
    sections: Optional[List[str]] = Field(None, description="조회할 섹션")
    include_sensitive: bool = Field(default=False, description="민감 정보 포함")

class GetSettingsResponse(BaseModel):
    """설정 조회 응답 모델"""
    settings: AppSettings = Field(..., description="설정 데이터")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    version: str = Field(..., description="설정 버전")

class UpdateSettingsRequest(BaseModel):
    """설정 업데이트 요청 모델"""
    settings: Dict[str, Any] = Field(..., description="설정 데이터")
    reason: Optional[str] = Field(None, description="변경 사유")
    validate_only: bool = Field(default=False, description="검증만 수행")

class UpdateSettingsResponse(BaseModel):
    """설정 업데이트 응답 모델"""
    settings: AppSettings = Field(..., description="업데이트된 설정")
    validation_result: SettingsValidationResult = Field(..., description="검증 결과")
    applied_changes: List[SettingsChange] = Field(..., description="적용된 변경사항")
    restart_required: bool = Field(..., description="재시작 필요 여부")

class ResetSettingsRequest(BaseModel):
    """설정 리셋 요청 모델"""
    sections: Optional[List[str]] = Field(None, description="리셋할 섹션")
    confirm: bool = Field(..., description="확인 여부")

class ResetSettingsResponse(BaseModel):
    """설정 리셋 응답 모델"""
    reset_sections: List[str] = Field(..., description="리셋된 섹션")
    backup_id: str = Field(..., description="백업 ID")
    restart_required: bool = Field(..., description="재시작 필요 여부")

class ExportSettingsRequest(BaseModel):
    """설정 내보내기 요청 모델"""
    sections: Optional[List[str]] = Field(None, description="내보낼 섹션")
    include_sensitive: bool = Field(default=False, description="민감 정보 포함")
    format: str = Field(default="json", regex="^(json|yaml)$", description="내보내기 형식")

class ExportSettingsResponse(BaseModel):
    """설정 내보내기 응답 모델"""
    export_data: SettingsExport = Field(..., description="내보내기 데이터")
    download_url: str = Field(..., description="다운로드 URL")
    expires_at: datetime = Field(..., description="만료 시간")

class ImportSettingsRequest(BaseModel):
    """설정 가져오기 요청 모델"""
    import_data: SettingsExport = Field(..., description="가져오기 데이터")
    options: SettingsImportOptions = Field(default_factory=SettingsImportOptions, description="가져오기 옵션")

class ImportSettingsResponse(BaseModel):
    """설정 가져오기 응답 모델"""
    result: SettingsImportResult = Field(..., description="가져오기 결과")
    restart_required: bool = Field(..., description="재시작 필요 여부")

# ===== 설정 템플릿 모델 =====

class SettingsTemplate(BaseModel):
    """설정 템플릿 모델"""
    id: str = Field(..., description="템플릿 ID")
    name: str = Field(..., description="템플릿 이름")
    description: str = Field(..., description="템플릿 설명")
    category: str = Field(..., regex="^(development|production|testing|custom)$", description="카테고리")
    settings: Dict[str, Any] = Field(..., description="설정 데이터")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    created_by: str = Field(..., description="생성자")
    is_system: bool = Field(default=False, description="시스템 템플릿 여부")

class ApplyTemplateRequest(BaseModel):
    """템플릿 적용 요청 모델"""
    template_id: str = Field(..., description="템플릿 ID")
    sections: Optional[List[str]] = Field(None, description="적용할 섹션")
    merge: bool = Field(default=True, description="기존 설정과 병합")

class ApplyTemplateResponse(BaseModel):
    """템플릿 적용 응답 모델"""
    applied_sections: List[str] = Field(..., description="적용된 섹션")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="충돌 목록")
    backup_id: str = Field(..., description="백업 ID")
    restart_required: bool = Field(..., description="재시작 필요 여부")

# ===== 설정 동기화 모델 =====

class SettingsConflict(BaseModel):
    """설정 충돌 모델"""
    field_path: str = Field(..., description="필드 경로")
    local_value: Any = Field(..., description="로컬 값")
    remote_value: Any = Field(..., description="원격 값")
    last_modified_local: datetime = Field(..., description="로컬 마지막 수정 시간")
    last_modified_remote: datetime = Field(..., description="원격 마지막 수정 시간")
    resolution: str = Field(..., regex="^(local|remote|manual|pending)$", description="해결 방법")

class SettingsSync(BaseModel):
    """설정 동기화 모델"""
    enabled: bool = Field(default=False, description="동기화 활성화")
    remote_url: Optional[HttpUrl] = Field(None, description="원격 URL")
    sync_interval: int = Field(default=60, ge=5, le=1440, description="동기화 간격 (분)")
    last_sync: Optional[datetime] = Field(None, description="마지막 동기화 시간")
    conflicts: List[SettingsConflict] = Field(default_factory=list, description="충돌 목록")