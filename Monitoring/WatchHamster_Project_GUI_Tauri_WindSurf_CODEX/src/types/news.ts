/**
 * 뉴스 관련 타입 정의
 * POSCO 뉴스 모니터링 시스템을 위한 타입들
 */

import { z } from 'zod'

// ===== 뉴스 타입 열거형 =====
export type NewsType = 'exchange-rate' | 'newyork-market-watch' | 'kospi-close'

export type NewsStatusType = 'latest' | 'delayed' | 'outdated' | 'error' | 'unknown'

// ===== 뉴스 상태 스키마 =====
export const NewsStatusSchema = z.object({
  type: z.enum(['exchange-rate', 'newyork-market-watch', 'kospi-close']),
  status: z.enum(['latest', 'delayed', 'outdated', 'error', 'unknown']),
  last_update: z.string(),
  expected_time: z.string().optional(),
  delay_minutes: z.number().optional(),
  data: z.any().optional(),
  error_message: z.string().optional(),
  processing_time: z.number().optional(),
  source_url: z.string().optional(),
})

// ===== 뉴스 데이터 스키마 =====
export const ExchangeRateDataSchema = z.object({
  usd_krw: z.number(),
  eur_krw: z.number().optional(),
  jpy_krw: z.number().optional(),
  cny_krw: z.number().optional(),
  rate_change: z.number().optional(),
  rate_change_percent: z.number().optional(),
  last_updated: z.string(),
  market_status: z.enum(['open', 'closed', 'pre_market', 'after_hours']).optional(),
})

export const NewYorkMarketDataSchema = z.object({
  dow_jones: z.number(),
  nasdaq: z.number(),
  sp500: z.number(),
  dow_change: z.number().optional(),
  nasdaq_change: z.number().optional(),
  sp500_change: z.number().optional(),
  dow_change_percent: z.number().optional(),
  nasdaq_change_percent: z.number().optional(),
  sp500_change_percent: z.number().optional(),
  market_status: z.enum(['open', 'closed', 'pre_market', 'after_hours']),
  last_updated: z.string(),
  volume: z.number().optional(),
})

export const KospiCloseDataSchema = z.object({
  kospi_index: z.number(),
  kosdaq_index: z.number().optional(),
  kospi_change: z.number().optional(),
  kosdaq_change: z.number().optional(),
  kospi_change_percent: z.number().optional(),
  kosdaq_change_percent: z.number().optional(),
  trading_volume: z.number().optional(),
  trading_value: z.number().optional(),
  market_cap: z.number().optional(),
  last_updated: z.string(),
  market_status: z.enum(['open', 'closed', 'pre_market', 'after_hours']),
})

// ===== 뉴스 히스토리 스키마 =====
export const NewsHistorySchema = z.object({
  id: z.string(),
  type: z.enum(['exchange-rate', 'newyork-market-watch', 'kospi-close']),
  timestamp: z.string(),
  status: z.enum(['latest', 'delayed', 'outdated', 'error', 'unknown']),
  data: z.any(),
  processing_time: z.number(),
  error_message: z.string().optional(),
  source_url: z.string().optional(),
})

// ===== 뉴스 설정 스키마 =====
export const NewsSettingsSchema = z.object({
  check_interval: z.number().min(60).max(3600), // 1분 ~ 1시간
  timeout: z.number().min(5).max(60), // 5초 ~ 60초
  retry_attempts: z.number().min(1).max(10),
  retry_delay: z.number().min(1).max(30),
  enabled_types: z.array(z.enum(['exchange-rate', 'newyork-market-watch', 'kospi-close'])),
  alert_thresholds: z.object({
    delay_minutes: z.number().min(1).max(120), // 지연 알림 임계값
    error_count: z.number().min(1).max(10), // 연속 오류 알림 임계값
  }),
  business_hours: z.object({
    enabled: z.boolean(),
    start_time: z.string(), // HH:MM 형식
    end_time: z.string(), // HH:MM 형식
    timezone: z.string().default('Asia/Seoul'),
  }),
})

// ===== 뉴스 통계 스키마 =====
export const NewsStatisticsSchema = z.object({
  type: z.enum(['exchange-rate', 'newyork-market-watch', 'kospi-close']),
  total_checks: z.number(),
  successful_checks: z.number(),
  failed_checks: z.number(),
  average_delay: z.number(),
  max_delay: z.number(),
  last_24h_stats: z.object({
    checks: z.number(),
    success_rate: z.number(),
    average_delay: z.number(),
  }),
  uptime_percentage: z.number(),
  last_reset: z.string(),
})

// ===== 타입 추출 =====
export type NewsStatus = z.infer<typeof NewsStatusSchema>
export type ExchangeRateData = z.infer<typeof ExchangeRateDataSchema>
export type NewYorkMarketData = z.infer<typeof NewYorkMarketDataSchema>
export type KospiCloseData = z.infer<typeof KospiCloseDataSchema>
export type NewsHistory = z.infer<typeof NewsHistorySchema>
export type NewsSettings = z.infer<typeof NewsSettingsSchema>
export type NewsStatistics = z.infer<typeof NewsStatisticsSchema>

// ===== 유니온 타입 =====
export type NewsData = ExchangeRateData | NewYorkMarketData | KospiCloseData

// ===== 뉴스 상태 집계 타입 =====
export interface NewsStatusSummary {
  exchange_rate: NewsStatus
  newyork_market: NewsStatus
  kospi_close: NewsStatus
  overall_status: 'healthy' | 'warning' | 'critical'
  last_check: string
  next_check: string
}

// ===== 뉴스 알림 타입 =====
export interface NewsAlert {
  id: string
  type: NewsType
  alert_type: 'delay' | 'error' | 'recovery' | 'status_change'
  message: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  timestamp: string
  data?: NewsData
  acknowledged: boolean
}

// ===== 뉴스 필터 타입 =====
export interface NewsFilter {
  types?: NewsType[]
  status?: NewsStatusType[]
  date_range?: {
    start: string
    end: string
  }
  search?: string
}

// ===== API 요청/응답 타입 =====
export interface GetNewsStatusRequest {
  types?: NewsType[]
  include_data?: boolean
}

export interface GetNewsStatusResponse {
  data: NewsStatus[]
  summary: NewsStatusSummary
  timestamp: string
}

export interface RefreshNewsRequest {
  type?: NewsType
  force?: boolean
}

export interface RefreshNewsResponse {
  message: string
  updated_types: NewsType[]
  timestamp: string
}

export interface GetNewsHistoryRequest {
  type?: NewsType
  limit?: number
  offset?: number
  start_date?: string
  end_date?: string
}

export interface GetNewsHistoryResponse {
  data: NewsHistory[]
  total: number
  has_more: boolean
}

export interface GetNewsStatisticsRequest {
  type?: NewsType
  period?: '1h' | '24h' | '7d' | '30d'
}

export interface GetNewsStatisticsResponse {
  data: NewsStatistics[]
  period: string
  generated_at: string
}

// ===== 유틸리티 함수 타입 =====
export interface NewsStatusChecker {
  checkNewsStatus(type: NewsType): Promise<NewsStatus>
  checkAllNewsStatus(): Promise<NewsStatus[]>
  getNewsHistory(filter: NewsFilter): Promise<NewsHistory[]>
  refreshNews(type?: NewsType): Promise<void>
}

export interface NewsDataParser {
  parseExchangeRate(rawData: any): ExchangeRateData
  parseNewYorkMarket(rawData: any): NewYorkMarketData
  parseKospiClose(rawData: any): KospiCloseData
  determineStatus(data: NewsData, expectedTime?: string): NewsStatusType
}

// ===== 뉴스 컴포넌트 Props 타입 =====
export interface NewsStatusCardProps {
  newsStatus: NewsStatus
  onRefresh?: () => void
  onViewHistory?: () => void
  compact?: boolean
}

export interface NewsHistoryViewerProps {
  history: NewsHistory[]
  loading?: boolean
  onLoadMore?: () => void
  hasMore?: boolean
  filter?: NewsFilter
  onFilterChange?: (filter: NewsFilter) => void
}

export interface NewsStatisticsWidgetProps {
  statistics: NewsStatistics
  type: NewsType
  period: '1h' | '24h' | '7d' | '30d'
  onPeriodChange?: (period: '1h' | '24h' | '7d' | '30d') => void
}

// ===== 뉴스 설정 컴포넌트 Props 타입 =====
export interface NewsSettingsFormProps {
  settings: NewsSettings
  onSettingsChange: (settings: NewsSettings) => void
  onSave: () => void
  onReset: () => void
  loading?: boolean
}

// ===== 뉴스 알림 관련 타입 =====
export interface NewsAlertConfig {
  enabled: boolean
  delay_threshold: number // 분 단위
  error_threshold: number // 연속 오류 횟수
  recovery_notification: boolean
  quiet_hours: {
    enabled: boolean
    start: string // HH:MM
    end: string // HH:MM
  }
}

export interface NewsWebhookPayload {
  type: NewsType
  status: NewsStatusType
  message: string
  data?: NewsData
  timestamp: string
  alert_level: 'info' | 'warning' | 'error' | 'critical'
}

// ===== 뉴스 모니터링 상태 타입 =====
export interface NewsMonitoringState {
  isRunning: boolean
  lastCheck: string | null
  nextCheck: string | null
  checkInterval: number
  errorCount: number
  consecutiveErrors: number
  uptime: number
  startTime: string | null
}

// ===== 뉴스 대시보드 타입 =====
export interface NewsDashboardData {
  status_summary: NewsStatusSummary
  recent_alerts: NewsAlert[]
  statistics: NewsStatistics[]
  monitoring_state: NewsMonitoringState
  system_health: 'healthy' | 'warning' | 'critical'
}