"""
뉴스 관련 데이터 모델
POSCO 뉴스 모니터링 시스템을 위한 Pydantic 모델들
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, model_validator
from enum import Enum

class NewsType(str, Enum):
    """뉴스 타입 열거형"""
    EXCHANGE_RATE = "exchange-rate"
    NEWYORK_MARKET = "newyork-market-watch"
    KOSPI_CLOSE = "kospi-close"

class NewsStatusType(str, Enum):
    """뉴스 상태 타입 열거형"""
    LATEST = "latest"
    DELAYED = "delayed"
    OUTDATED = "outdated"
    ERROR = "error"
    UNKNOWN = "unknown"

class MarketStatus(str, Enum):
    """시장 상태 열거형"""
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    AFTER_HOURS = "after_hours"

class AlertLevel(str, Enum):
    """알림 레벨 열거형"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# ===== 뉴스 데이터 모델 =====

class ExchangeRateData(BaseModel):
    """환율 데이터 모델"""
    usd_krw: float = Field(..., gt=0, description="USD/KRW 환율")
    eur_krw: Optional[float] = Field(None, gt=0, description="EUR/KRW 환율")
    jpy_krw: Optional[float] = Field(None, gt=0, description="JPY/KRW 환율")
    cny_krw: Optional[float] = Field(None, gt=0, description="CNY/KRW 환율")
    rate_change: Optional[float] = Field(None, description="환율 변동")
    rate_change_percent: Optional[float] = Field(None, description="환율 변동률 (%)")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    market_status: Optional[MarketStatus] = Field(None, description="시장 상태")

class NewYorkMarketData(BaseModel):
    """뉴욕 시장 데이터 모델"""
    dow_jones: float = Field(..., description="다우존스 지수")
    nasdaq: float = Field(..., description="나스닥 지수")
    sp500: float = Field(..., description="S&P 500 지수")
    dow_change: Optional[float] = Field(None, description="다우존스 변동")
    nasdaq_change: Optional[float] = Field(None, description="나스닥 변동")
    sp500_change: Optional[float] = Field(None, description="S&P 500 변동")
    dow_change_percent: Optional[float] = Field(None, description="다우존스 변동률 (%)")
    nasdaq_change_percent: Optional[float] = Field(None, description="나스닥 변동률 (%)")
    sp500_change_percent: Optional[float] = Field(None, description="S&P 500 변동률 (%)")
    market_status: MarketStatus = Field(..., description="시장 상태")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    volume: Optional[int] = Field(None, ge=0, description="거래량")

class KospiCloseData(BaseModel):
    """코스피 종가 데이터 모델"""
    kospi_index: float = Field(..., gt=0, description="코스피 지수")
    kosdaq_index: Optional[float] = Field(None, gt=0, description="코스닥 지수")
    kospi_change: Optional[float] = Field(None, description="코스피 변동")
    kosdaq_change: Optional[float] = Field(None, description="코스닥 변동")
    kospi_change_percent: Optional[float] = Field(None, description="코스피 변동률 (%)")
    kosdaq_change_percent: Optional[float] = Field(None, description="코스닥 변동률 (%)")
    trading_volume: Optional[int] = Field(None, ge=0, description="거래량")
    trading_value: Optional[int] = Field(None, ge=0, description="거래대금")
    market_cap: Optional[int] = Field(None, ge=0, description="시가총액")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    market_status: MarketStatus = Field(..., description="시장 상태")

# ===== 뉴스 상태 모델 =====

class NewsStatus(BaseModel):
    """뉴스 상태 모델"""
    type: NewsType = Field(..., description="뉴스 타입")
    status: NewsStatusType = Field(..., description="뉴스 상태")
    last_update: datetime = Field(..., description="마지막 업데이트 시간")
    expected_time: Optional[datetime] = Field(None, description="예상 발행 시간")
    delay_minutes: Optional[int] = Field(None, ge=0, description="지연 시간 (분)")
    data: Optional[Union[ExchangeRateData, NewYorkMarketData, KospiCloseData]] = Field(None, description="뉴스 데이터")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    processing_time: Optional[float] = Field(None, ge=0, description="처리 시간 (초)")
    source_url: Optional[str] = Field(None, description="소스 URL")

    @model_validator(mode="after")
    def validate_data_type(cls, values):
        """데이터 타입 검증"""
        data = values.data
        if data is None:
            return values

        if values.type == NewsType.EXCHANGE_RATE and not isinstance(data, ExchangeRateData):
            raise ValueError("Exchange rate news must have ExchangeRateData")
        if values.type == NewsType.NEWYORK_MARKET and not isinstance(data, NewYorkMarketData):
            raise ValueError("New York market news must have NewYorkMarketData")
        if values.type == NewsType.KOSPI_CLOSE and not isinstance(data, KospiCloseData):
            raise ValueError("KOSPI close news must have KospiCloseData")

        return values

class NewsHistory(BaseModel):
    """뉴스 히스토리 모델"""
    id: str = Field(..., description="히스토리 ID")
    type: NewsType = Field(..., description="뉴스 타입")
    timestamp: datetime = Field(..., description="기록 시간")
    status: NewsStatusType = Field(..., description="뉴스 상태")
    data: Optional[Dict[str, Any]] = Field(None, description="뉴스 데이터")
    processing_time: float = Field(..., ge=0, description="처리 시간 (초)")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    source_url: Optional[str] = Field(None, description="소스 URL")

class NewsStatistics(BaseModel):
    """뉴스 통계 모델"""
    type: NewsType = Field(..., description="뉴스 타입")
    total_checks: int = Field(..., ge=0, description="총 체크 횟수")
    successful_checks: int = Field(..., ge=0, description="성공한 체크 횟수")
    failed_checks: int = Field(..., ge=0, description="실패한 체크 횟수")
    average_delay: float = Field(..., ge=0, description="평균 지연 시간 (분)")
    max_delay: float = Field(..., ge=0, description="최대 지연 시간 (분)")
    last_24h_stats: Dict[str, Union[int, float]] = Field(default_factory=dict, description="최근 24시간 통계")
    uptime_percentage: float = Field(..., ge=0, le=100, description="가동률 (%)")
    last_reset: datetime = Field(..., description="마지막 리셋 시간")

# ===== 뉴스 설정 모델 =====

class BusinessHours(BaseModel):
    """영업시간 설정 모델"""
    enabled: bool = Field(default=True, description="영업시간 체크 활성화")
    start_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="시작 시간 (HH:MM)")
    end_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="종료 시간 (HH:MM)")
    timezone: str = Field(default="Asia/Seoul", description="시간대")

class AlertThresholds(BaseModel):
    """알림 임계값 설정 모델"""
    delay_minutes: int = Field(default=30, ge=1, le=120, description="지연 알림 임계값 (분)")
    error_count: int = Field(default=3, ge=1, le=10, description="연속 오류 알림 임계값")

class NewsSettings(BaseModel):
    """뉴스 설정 모델"""
    check_interval: int = Field(default=300, ge=60, le=3600, description="체크 간격 (초)")
    timeout: int = Field(default=30, ge=5, le=60, description="타임아웃 (초)")
    retry_attempts: int = Field(default=3, ge=1, le=10, description="재시도 횟수")
    retry_delay: int = Field(default=5, ge=1, le=30, description="재시도 지연 (초)")
    enabled_types: List[NewsType] = Field(default_factory=lambda: list(NewsType), description="활성화된 뉴스 타입")
    alert_thresholds: AlertThresholds = Field(default_factory=AlertThresholds, description="알림 임계값")
    business_hours: BusinessHours = Field(default_factory=BusinessHours, description="영업시간 설정")

# ===== 뉴스 상태 집계 모델 =====

class NewsStatusSummary(BaseModel):
    """뉴스 상태 요약 모델"""
    exchange_rate: NewsStatus = Field(..., description="환율 뉴스 상태")
    newyork_market: NewsStatus = Field(..., description="뉴욕 시장 뉴스 상태")
    kospi_close: NewsStatus = Field(..., description="코스피 종가 뉴스 상태")
    overall_status: str = Field(..., pattern="^(healthy|warning|critical)$", description="전체 상태")
    last_check: datetime = Field(..., description="마지막 체크 시간")
    next_check: datetime = Field(..., description="다음 체크 시간")

class NewsAlert(BaseModel):
    """뉴스 알림 모델"""
    id: str = Field(..., description="알림 ID")
    type: NewsType = Field(..., description="뉴스 타입")
    alert_type: str = Field(..., pattern="^(delay|error|recovery|status_change)$", description="알림 타입")
    message: str = Field(..., description="알림 메시지")
    severity: AlertLevel = Field(..., description="심각도")
    timestamp: datetime = Field(default_factory=datetime.now, description="알림 시간")
    data: Optional[Dict[str, Any]] = Field(None, description="관련 데이터")
    acknowledged: bool = Field(default=False, description="확인 여부")

# ===== API 요청/응답 모델 =====

class GetNewsStatusRequest(BaseModel):
    """뉴스 상태 조회 요청 모델"""
    types: Optional[List[NewsType]] = Field(None, description="조회할 뉴스 타입")
    include_data: bool = Field(default=True, description="데이터 포함 여부")

class GetNewsStatusResponse(BaseModel):
    """뉴스 상태 조회 응답 모델"""
    data: List[NewsStatus] = Field(..., description="뉴스 상태 목록")
    summary: NewsStatusSummary = Field(..., description="상태 요약")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class RefreshNewsRequest(BaseModel):
    """뉴스 갱신 요청 모델"""
    type: Optional[NewsType] = Field(None, description="갱신할 뉴스 타입")
    force: bool = Field(default=False, description="강제 갱신 여부")

class RefreshNewsResponse(BaseModel):
    """뉴스 갱신 응답 모델"""
    message: str = Field(..., description="응답 메시지")
    updated_types: List[NewsType] = Field(..., description="갱신된 뉴스 타입")
    timestamp: datetime = Field(default_factory=datetime.now, description="갱신 시간")

class GetNewsHistoryRequest(BaseModel):
    """뉴스 히스토리 조회 요청 모델"""
    type: Optional[NewsType] = Field(None, description="뉴스 타입")
    limit: int = Field(default=100, ge=1, le=1000, description="조회 개수")
    offset: int = Field(default=0, ge=0, description="오프셋")
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")

class GetNewsHistoryResponse(BaseModel):
    """뉴스 히스토리 조회 응답 모델"""
    data: List[NewsHistory] = Field(..., description="히스토리 목록")
    total: int = Field(..., ge=0, description="전체 개수")
    has_more: bool = Field(..., description="더 많은 데이터 존재 여부")

class GetNewsStatisticsRequest(BaseModel):
    """뉴스 통계 조회 요청 모델"""
    type: Optional[NewsType] = Field(None, description="뉴스 타입")
    period: str = Field(default="24h", pattern="^(1h|24h|7d|30d)$", description="통계 기간")

class GetNewsStatisticsResponse(BaseModel):
    """뉴스 통계 조회 응답 모델"""
    data: List[NewsStatistics] = Field(..., description="통계 목록")
    period: str = Field(..., description="통계 기간")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

# ===== 뉴스 모니터링 상태 모델 =====

class NewsMonitoringState(BaseModel):
    """뉴스 모니터링 상태 모델"""
    is_running: bool = Field(..., description="실행 상태")
    last_check: Optional[datetime] = Field(None, description="마지막 체크 시간")
    next_check: Optional[datetime] = Field(None, description="다음 체크 시간")
    check_interval: int = Field(..., ge=60, description="체크 간격 (초)")
    error_count: int = Field(default=0, ge=0, description="오류 횟수")
    consecutive_errors: int = Field(default=0, ge=0, description="연속 오류 횟수")
    uptime: int = Field(default=0, ge=0, description="가동 시간 (초)")
    start_time: Optional[datetime] = Field(None, description="시작 시간")

class NewsDashboardData(BaseModel):
    """뉴스 대시보드 데이터 모델"""
    status_summary: NewsStatusSummary = Field(..., description="상태 요약")
    recent_alerts: List[NewsAlert] = Field(default_factory=list, description="최근 알림")
    statistics: List[NewsStatistics] = Field(default_factory=list, description="통계")
    monitoring_state: NewsMonitoringState = Field(..., description="모니터링 상태")
    system_health: str = Field(..., regex="^(healthy|warning|critical)$", description="시스템 건강 상태")

# ===== 뉴스 필터 모델 =====

class NewsFilter(BaseModel):
    """뉴스 필터 모델"""
    types: Optional[List[NewsType]] = Field(None, description="뉴스 타입 필터")
    status: Optional[List[NewsStatusType]] = Field(None, description="상태 필터")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="날짜 범위 필터")
    search: Optional[str] = Field(None, description="검색어")

# ===== 뉴스 알림 설정 모델 =====

class NewsAlertConfig(BaseModel):
    """뉴스 알림 설정 모델"""
    enabled: bool = Field(default=True, description="알림 활성화")
    delay_threshold: int = Field(default=30, ge=1, le=120, description="지연 임계값 (분)")
    error_threshold: int = Field(default=3, ge=1, le=10, description="오류 임계값")
    recovery_notification: bool = Field(default=True, description="복구 알림")
    quiet_hours: Dict[str, Union[bool, str]] = Field(default_factory=dict, description="조용한 시간 설정")

class NewsWebhookPayload(BaseModel):
    """뉴스 웹훅 페이로드 모델"""
    type: NewsType = Field(..., description="뉴스 타입")
    status: NewsStatusType = Field(..., description="뉴스 상태")
    message: str = Field(..., description="메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="뉴스 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="시간")
    alert_level: AlertLevel = Field(..., description="알림 레벨")