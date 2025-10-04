"""
시스템 관련 데이터 모델
WatchHamster 시스템 모니터링을 위한 Pydantic 모델들
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

class SystemHealthStatus(str, Enum):
    """시스템 건강 상태 열거형"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ServiceStatus(str, Enum):
    """서비스 상태 열거형"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

class ProcessStatus(str, Enum):
    """프로세스 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNKNOWN = "unknown"

class NetworkStatus(str, Enum):
    """네트워크 상태 열거형"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    LIMITED = "limited"

class GitRepositoryStatus(str, Enum):
    """Git 저장소 상태 열거형"""
    CLEAN = "clean"
    DIRTY = "dirty"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"

class RemoteStatus(str, Enum):
    """원격 저장소 상태 열거형"""
    UP_TO_DATE = "up-to-date"
    AHEAD = "ahead"
    BEHIND = "behind"
    DIVERGED = "diverged"
    UNKNOWN = "unknown"

# ===== 시스템 정보 모델 =====

class SystemInfo(BaseModel):
    """시스템 정보 모델"""
    platform: str = Field(..., description="운영체제 플랫폼")
    arch: str = Field(..., description="시스템 아키텍처")
    version: str = Field(..., description="애플리케이션 버전")
    hostname: str = Field(..., description="호스트명")
    python_version: str = Field(..., description="Python 버전")
    cpu_count: int = Field(..., ge=1, description="CPU 코어 수")
    memory_total: int = Field(..., ge=0, description="총 메모리 (bytes)")
    disk_total: int = Field(..., ge=0, description="총 디스크 용량 (bytes)")
    boot_time: datetime = Field(..., description="부팅 시간")
    timezone: str = Field(default="Asia/Seoul", description="시간대")

class SystemMetrics(BaseModel):
    """시스템 메트릭 모델"""
    cpu_percent: float = Field(..., ge=0, le=100, description="CPU 사용률 (%)")
    memory_percent: float = Field(..., ge=0, le=100, description="메모리 사용률 (%)")
    memory_used: int = Field(..., ge=0, description="사용 중인 메모리 (bytes)")
    memory_available: int = Field(..., ge=0, description="사용 가능한 메모리 (bytes)")
    disk_usage: float = Field(..., ge=0, le=100, description="디스크 사용률 (%)")
    disk_used: int = Field(..., ge=0, description="사용 중인 디스크 (bytes)")
    disk_free: int = Field(..., ge=0, description="사용 가능한 디스크 (bytes)")
    network_status: NetworkStatus = Field(..., description="네트워크 상태")
    network_bytes_sent: int = Field(default=0, ge=0, description="전송된 네트워크 바이트")
    network_bytes_recv: int = Field(default=0, ge=0, description="수신된 네트워크 바이트")
    uptime: int = Field(..., ge=0, description="시스템 업타임 (초)")
    load_average: Optional[List[float]] = Field(None, description="로드 평균 (1, 5, 15분)")
    active_services: int = Field(..., ge=0, description="활성 서비스 수")
    timestamp: datetime = Field(default_factory=datetime.now, description="측정 시간")

class DiskIOMetrics(BaseModel):
    """디스크 I/O 메트릭 모델"""
    read_bytes: List[int] = Field(default_factory=list, description="읽기 바이트 히스토리")
    write_bytes: List[int] = Field(default_factory=list, description="쓰기 바이트 히스토리")
    read_count: List[int] = Field(default_factory=list, description="읽기 횟수 히스토리")
    write_count: List[int] = Field(default_factory=list, description="쓰기 횟수 히스토리")

class NetworkIOMetrics(BaseModel):
    """네트워크 I/O 메트릭 모델"""
    bytes_sent: List[int] = Field(default_factory=list, description="전송 바이트 히스토리")
    bytes_recv: List[int] = Field(default_factory=list, description="수신 바이트 히스토리")
    packets_sent: List[int] = Field(default_factory=list, description="전송 패킷 히스토리")
    packets_recv: List[int] = Field(default_factory=list, description="수신 패킷 히스토리")

class PerformanceMetrics(BaseModel):
    """성능 메트릭 모델"""
    cpu_usage: List[float] = Field(default_factory=list, description="CPU 사용률 히스토리")
    memory_usage: List[float] = Field(default_factory=list, description="메모리 사용률 히스토리")
    disk_io: DiskIOMetrics = Field(default_factory=DiskIOMetrics, description="디스크 I/O 메트릭")
    network_io: NetworkIOMetrics = Field(default_factory=NetworkIOMetrics, description="네트워크 I/O 메트릭")
    timestamps: List[datetime] = Field(default_factory=list, description="측정 시간 목록")
    interval: int = Field(default=60, ge=1, description="측정 간격 (초)")

# ===== 프로세스 정보 모델 =====

class ProcessInfo(BaseModel):
    """프로세스 정보 모델"""
    pid: int = Field(..., ge=1, description="프로세스 ID")
    name: str = Field(..., description="프로세스 이름")
    status: ProcessStatus = Field(..., description="프로세스 상태")
    cpu_percent: float = Field(..., ge=0, description="CPU 사용률 (%)")
    memory_percent: float = Field(..., ge=0, description="메모리 사용률 (%)")
    memory_rss: int = Field(..., ge=0, description="RSS 메모리 (bytes)")
    memory_vms: int = Field(..., ge=0, description="VMS 메모리 (bytes)")
    create_time: datetime = Field(..., description="생성 시간")
    cmdline: Optional[List[str]] = Field(None, description="명령줄 인수")
    cwd: Optional[str] = Field(None, description="작업 디렉토리")
    num_threads: Optional[int] = Field(None, ge=1, description="스레드 수")

# ===== 서비스 정보 모델 =====

class ServiceInfo(BaseModel):
    """서비스 정보 모델"""
    id: str = Field(..., description="서비스 고유 ID")
    name: str = Field(..., description="서비스 이름")
    description: str = Field(..., description="서비스 설명")
    status: ServiceStatus = Field(..., description="서비스 상태")
    pid: Optional[int] = Field(None, ge=1, description="프로세스 ID")
    uptime: Optional[int] = Field(None, ge=0, description="서비스 업타임 (초)")
    restart_count: int = Field(default=0, ge=0, description="재시작 횟수")
    last_restart: Optional[datetime] = Field(None, description="마지막 재시작 시간")
    last_error: Optional[str] = Field(None, description="마지막 오류 메시지")
    error_count: int = Field(default=0, ge=0, description="오류 횟수")
    config: Optional[Dict[str, Any]] = Field(None, description="서비스 설정")
    dependencies: Optional[List[str]] = Field(None, description="의존성 서비스")
    auto_restart: bool = Field(default=True, description="자동 재시작 여부")
    health_check_url: Optional[str] = Field(None, description="헬스 체크 URL")
    log_file: Optional[str] = Field(None, description="로그 파일 경로")

# ===== Git 상태 모델 =====

class GitStatus(BaseModel):
    """Git 상태 모델"""
    branch: str = Field(..., description="현재 브랜치")
    commit_hash: str = Field(..., description="커밋 해시")
    commit_message: str = Field(..., description="커밋 메시지")
    commit_author: str = Field(..., description="커밋 작성자")
    commit_date: datetime = Field(..., description="커밋 날짜")
    has_uncommitted_changes: bool = Field(..., description="커밋되지 않은 변경사항 존재")
    has_untracked_files: bool = Field(..., description="추적되지 않은 파일 존재")
    has_conflicts: bool = Field(..., description="충돌 존재")
    remote_status: RemoteStatus = Field(..., description="원격 저장소 상태")
    remote_url: Optional[str] = Field(None, description="원격 저장소 URL")
    ahead_count: Optional[int] = Field(None, ge=0, description="앞선 커밋 수")
    behind_count: Optional[int] = Field(None, ge=0, description="뒤처진 커밋 수")
    last_fetch: Optional[datetime] = Field(None, description="마지막 fetch 시간")
    repository_status: GitRepositoryStatus = Field(..., description="저장소 상태")

# ===== 시스템 알림 모델 =====

class SystemAlert(BaseModel):
    """시스템 알림 모델"""
    id: str = Field(..., description="알림 ID")
    type: str = Field(..., description="알림 타입")
    message: str = Field(..., description="알림 메시지")
    severity: str = Field(..., regex="^(info|warning|error|critical)$", description="심각도")
    timestamp: datetime = Field(default_factory=datetime.now, description="알림 시간")
    source: str = Field(..., description="알림 소스")
    details: Optional[Dict[str, Any]] = Field(None, description="추가 세부 정보")
    acknowledged: bool = Field(default=False, description="확인 여부")
    auto_resolve: bool = Field(default=False, description="자동 해결 가능 여부")

# ===== 시스템 상태 모델 =====

class SystemStatus(BaseModel):
    """시스템 상태 모델"""
    overall: SystemHealthStatus = Field(..., description="전체 시스템 상태")
    services: List[ServiceInfo] = Field(default_factory=list, description="서비스 목록")
    metrics: SystemMetrics = Field(..., description="시스템 메트릭")
    git_status: Optional[GitStatus] = Field(None, description="Git 상태")
    processes: Optional[List[ProcessInfo]] = Field(None, description="프로세스 목록")
    last_check: datetime = Field(default_factory=datetime.now, description="마지막 체크 시간")
    uptime: int = Field(..., ge=0, description="시스템 업타임 (초)")
    alerts: List[SystemAlert] = Field(default_factory=list, description="알림 목록")

# ===== 시스템 설정 모델 =====

class MonitoringSettings(BaseModel):
    """모니터링 설정 모델"""
    check_interval: int = Field(default=60, ge=5, le=300, description="체크 간격 (초)")
    metrics_retention: int = Field(default=24, ge=1, le=168, description="메트릭 보존 시간 (시간)")
    alert_thresholds: Dict[str, Union[int, float]] = Field(default_factory=dict, description="알림 임계값")
    auto_restart: Dict[str, Any] = Field(default_factory=dict, description="자동 재시작 설정")

class GitSettings(BaseModel):
    """Git 설정 모델"""
    auto_fetch: bool = Field(default=True, description="자동 fetch")
    fetch_interval: int = Field(default=1800, ge=300, le=3600, description="fetch 간격 (초)")
    auto_resolve_conflicts: bool = Field(default=False, description="자동 충돌 해결")
    branch_protection: List[str] = Field(default_factory=list, description="보호된 브랜치")

class NotificationSettings(BaseModel):
    """알림 설정 모델"""
    enabled: bool = Field(default=True, description="알림 활성화")
    webhook_url: Optional[str] = Field(None, description="웹훅 URL")
    alert_levels: List[str] = Field(default_factory=list, description="알림 레벨")
    quiet_hours: Dict[str, Any] = Field(default_factory=dict, description="조용한 시간 설정")

class SystemSettings(BaseModel):
    """시스템 설정 모델"""
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings, description="모니터링 설정")
    git: GitSettings = Field(default_factory=GitSettings, description="Git 설정")
    notifications: NotificationSettings = Field(default_factory=NotificationSettings, description="알림 설정")

# ===== 시스템 액션 모델 =====

class SystemAction(BaseModel):
    """시스템 액션 모델"""
    type: str = Field(..., description="액션 타입")
    target: str = Field(..., description="대상")
    parameters: Optional[Dict[str, Any]] = Field(None, description="매개변수")

class SystemActionResult(BaseModel):
    """시스템 액션 결과 모델"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")
    timestamp: datetime = Field(default_factory=datetime.now, description="실행 시간")

# ===== 리소스 사용량 모델 =====

class ResourceUsage(BaseModel):
    """리소스 사용량 모델"""
    current: float = Field(..., ge=0, description="현재 사용량")
    average: float = Field(..., ge=0, description="평균 사용량")
    peak: float = Field(..., ge=0, description="최대 사용량")
    unit: str = Field(..., description="단위")
    threshold: Optional[float] = Field(None, ge=0, description="임계값")
    status: str = Field(..., regex="^(normal|warning|critical)$", description="상태")

class ResourceSummary(BaseModel):
    """리소스 요약 모델"""
    cpu: ResourceUsage = Field(..., description="CPU 사용량")
    memory: ResourceUsage = Field(..., description="메모리 사용량")
    disk: ResourceUsage = Field(..., description="디스크 사용량")
    network: Dict[str, Any] = Field(default_factory=dict, description="네트워크 정보")

# ===== 서비스 제어 모델 =====

class ServiceControl(BaseModel):
    """서비스 제어 모델"""
    service_id: str = Field(..., description="서비스 ID")
    action: str = Field(..., regex="^(start|stop|restart|reload|status)$", description="액션")
    force: bool = Field(default=False, description="강제 실행")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="타임아웃 (초)")

class ServiceControlResult(BaseModel):
    """서비스 제어 결과 모델"""
    service_id: str = Field(..., description="서비스 ID")
    action: str = Field(..., description="실행된 액션")
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")
    new_status: ServiceStatus = Field(..., description="새로운 상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="실행 시간")

# ===== 모니터링 상태 모델 =====

class MonitoringState(BaseModel):
    """모니터링 상태 모델"""
    is_running: bool = Field(..., description="실행 상태")
    start_time: Optional[datetime] = Field(None, description="시작 시간")
    last_check: Optional[datetime] = Field(None, description="마지막 체크 시간")
    next_check: Optional[datetime] = Field(None, description="다음 체크 시간")
    check_interval: int = Field(..., ge=5, description="체크 간격 (초)")
    total_checks: int = Field(default=0, ge=0, description="총 체크 횟수")
    failed_checks: int = Field(default=0, ge=0, description="실패한 체크 횟수")
    uptime: int = Field(default=0, ge=0, description="가동 시간 (초)")
    error_rate: float = Field(default=0.0, ge=0, le=100, description="오류율 (%)")

# ===== API 요청/응답 모델 =====

class GetSystemStatusRequest(BaseModel):
    """시스템 상태 조회 요청 모델"""
    include_processes: bool = Field(default=False, description="프로세스 정보 포함")
    include_git: bool = Field(default=True, description="Git 상태 포함")
    include_metrics: bool = Field(default=True, description="메트릭 포함")

class GetSystemStatusResponse(BaseModel):
    """시스템 상태 조회 응답 모델"""
    data: SystemStatus = Field(..., description="시스템 상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class GetSystemMetricsRequest(BaseModel):
    """시스템 메트릭 조회 요청 모델"""
    period: str = Field(default="1h", regex="^(1h|6h|24h|7d)$", description="조회 기간")
    interval: Optional[int] = Field(None, ge=60, le=3600, description="측정 간격 (초)")

class GetSystemMetricsResponse(BaseModel):
    """시스템 메트릭 조회 응답 모델"""
    data: PerformanceMetrics = Field(..., description="성능 메트릭")
    period: str = Field(..., description="조회 기간")
    interval: int = Field(..., description="측정 간격")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class ControlServiceRequest(BaseModel):
    """서비스 제어 요청 모델"""
    service_id: str = Field(..., description="서비스 ID")
    action: str = Field(..., regex="^(start|stop|restart)$", description="액션")
    force: bool = Field(default=False, description="강제 실행")

class ControlServiceResponse(BaseModel):
    """서비스 제어 응답 모델"""
    result: ServiceControlResult = Field(..., description="제어 결과")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class UpdateSystemSettingsRequest(BaseModel):
    """시스템 설정 업데이트 요청 모델"""
    settings: Dict[str, Any] = Field(..., description="설정 데이터")

class UpdateSystemSettingsResponse(BaseModel):
    """시스템 설정 업데이트 응답 모델"""
    settings: SystemSettings = Field(..., description="업데이트된 설정")
    applied_changes: List[str] = Field(..., description="적용된 변경사항")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

# ===== 헬스 체크 모델 =====

class HealthCheck(BaseModel):
    """헬스 체크 모델"""
    component: str = Field(..., description="구성요소")
    status: str = Field(..., regex="^(healthy|unhealthy|degraded)$", description="상태")
    message: str = Field(..., description="상태 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="세부 정보")
    last_check: datetime = Field(default_factory=datetime.now, description="마지막 체크 시간")
    response_time: Optional[float] = Field(None, ge=0, description="응답 시간 (초)")

class SystemHealthReport(BaseModel):
    """시스템 건강 보고서 모델"""
    overall_status: SystemHealthStatus = Field(..., description="전체 상태")
    checks: List[HealthCheck] = Field(..., description="헬스 체크 목록")
    uptime: int = Field(..., ge=0, description="가동 시간 (초)")
    last_restart: Optional[datetime] = Field(None, description="마지막 재시작 시간")
    performance_score: float = Field(..., ge=0, le=100, description="성능 점수")
    recommendations: List[str] = Field(default_factory=list, description="권장사항")
    timestamp: datetime = Field(default_factory=datetime.now, description="보고서 생성 시간")

# ===== 시스템 통계 모델 =====

class SystemStatistics(BaseModel):
    """시스템 통계 모델"""
    uptime: int = Field(..., ge=0, description="가동 시간 (초)")
    total_requests: int = Field(..., ge=0, description="총 요청 수")
    successful_requests: int = Field(..., ge=0, description="성공한 요청 수")
    failed_requests: int = Field(..., ge=0, description="실패한 요청 수")
    average_response_time: float = Field(..., ge=0, description="평균 응답 시간 (초)")
    peak_cpu_usage: float = Field(..., ge=0, le=100, description="최대 CPU 사용률 (%)")
    peak_memory_usage: float = Field(..., ge=0, le=100, description="최대 메모리 사용률 (%)")
    service_restarts: int = Field(..., ge=0, description="서비스 재시작 횟수")
    git_commits: int = Field(..., ge=0, description="Git 커밋 수")
    alerts_generated: int = Field(..., ge=0, description="생성된 알림 수")
    period: str = Field(..., description="통계 기간")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

# ===== 레거시 호환성 모델 =====

class ServiceFailure(BaseModel):
    """서비스 실패 정보 모델 (레거시 호환성)"""
    service_id: str = Field(..., description="서비스 ID")
    error: str = Field(..., description="오류 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="발생 시간")
    resolved: bool = Field(default=False, description="해결 여부")

class StabilityMetrics(BaseModel):
    """안정성 메트릭 모델 (레거시 호환성)"""
    error_count: int = Field(..., ge=0, description="오류 발생 횟수")
    recovery_count: int = Field(..., ge=0, description="복구 횟수")
    last_health_check: datetime = Field(default_factory=datetime.now, description="마지막 헬스 체크 시간")
    system_health: str = Field(..., regex="^(healthy|warning|critical)$", description="시스템 상태")
    service_failures: List[ServiceFailure] = Field(default_factory=list, description="서비스 실패 목록")