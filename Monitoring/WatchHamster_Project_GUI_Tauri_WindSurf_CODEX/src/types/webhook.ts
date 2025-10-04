/**
 * 웹훅 관련 타입 정의
 * Dooray 웹훅 시스템을 위한 타입들
 */

import { z } from 'zod'
import { NewsType, NewsStatusType } from './news'
import { SystemHealthStatus } from './system'

// ===== 웹훅 타입 열거형 =====
export type WebhookType = 'dooray' | 'slack' | 'discord' | 'teams' | 'generic'
export type WebhookStatus = 'pending' | 'sending' | 'success' | 'failed' | 'timeout' | 'cancelled'
export type AlertLevel = 'info' | 'warning' | 'error' | 'critical'

// ===== 웹훅 설정 스키마 =====
export const WebhookConfigSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.enum(['dooray', 'slack', 'discord', 'teams', 'generic']),
  url: z.string().url(),
  enabled: z.boolean(),
  timeout: z.number().min(5).max(60), // seconds
  retry_attempts: z.number().min(0).max(10),
  retry_delay: z.number().min(1).max(30), // seconds
  rate_limit: z.object({
    enabled: z.boolean(),
    max_requests: z.number().min(1).max(100),
    time_window: z.number().min(60).max(3600), // seconds
  }),
  headers: z.record(z.string(), z.string()).optional(),
  auth: z.object({
    type: z.enum(['none', 'bearer', 'basic', 'api_key']),
    token: z.string().optional(),
    username: z.string().optional(),
    password: z.string().optional(),
    api_key: z.string().optional(),
    api_key_header: z.string().optional(),
  }).optional(),
})

// ===== 웹훅 메시지 스키마 =====
export const WebhookMessageSchema = z.object({
  id: z.string(),
  webhook_id: z.string(),
  type: z.enum(['news_alert', 'system_status', 'service_alert', 'error_report', 'custom']),
  title: z.string(),
  message: z.string(),
  alert_level: z.enum(['info', 'warning', 'error', 'critical']),
  timestamp: z.string(),
  data: z.any().optional(),
  template_id: z.string().optional(),
  variables: z.record(z.string(), z.any()).optional(),
})

// ===== 웹훅 전송 기록 스키마 =====
export const WebhookHistorySchema = z.object({
  id: z.string(),
  webhook_id: z.string(),
  message_id: z.string(),
  status: z.enum(['pending', 'sending', 'success', 'failed', 'timeout', 'cancelled']),
  sent_at: z.string(),
  completed_at: z.string().optional(),
  response_code: z.number().optional(),
  response_body: z.string().optional(),
  error_message: z.string().optional(),
  retry_count: z.number().min(0),
  processing_time: z.number().optional(), // milliseconds
})

// ===== 웹훅 템플릿 스키마 =====
export const WebhookTemplateSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  webhook_type: z.enum(['dooray', 'slack', 'discord', 'teams', 'generic']),
  message_type: z.enum(['news_alert', 'system_status', 'service_alert', 'error_report', 'custom']),
  template: z.string(),
  variables: z.array(z.string()),
  default_values: z.record(z.string(), z.any()).optional(),
  created_at: z.string(),
  updated_at: z.string(),
  is_system: z.boolean(), // 시스템 기본 템플릿 여부
})

// ===== 웹훅 통계 스키마 =====
export const WebhookStatisticsSchema = z.object({
  webhook_id: z.string(),
  total_sent: z.number(),
  successful_sent: z.number(),
  failed_sent: z.number(),
  success_rate: z.number(),
  average_response_time: z.number(),
  last_24h: z.object({
    sent: z.number(),
    success_rate: z.number(),
    average_response_time: z.number(),
  }),
  last_7d: z.object({
    sent: z.number(),
    success_rate: z.number(),
    average_response_time: z.number(),
  }),
  last_success: z.string().optional(),
  last_failure: z.string().optional(),
  current_streak: z.object({
    type: z.enum(['success', 'failure']),
    count: z.number(),
    started_at: z.string(),
  }),
})

// ===== 타입 추출 =====
export type WebhookConfig = z.infer<typeof WebhookConfigSchema>
export type WebhookMessage = z.infer<typeof WebhookMessageSchema>
export type WebhookHistory = z.infer<typeof WebhookHistorySchema>
export type WebhookTemplate = z.infer<typeof WebhookTemplateSchema>
export type WebhookStatistics = z.infer<typeof WebhookStatisticsSchema>

// ===== POSCO 전용 웹훅 타입 =====
export interface PoscoNewsWebhookPayload {
  type: NewsType
  status: NewsStatusType
  title: string
  message: string
  data?: any
  timestamp: string
  alert_level: AlertLevel
  delay_minutes?: number
  error_message?: string
}

export interface PoscoSystemWebhookPayload {
  system_status: SystemHealthStatus
  title: string
  message: string
  services_summary: {
    total: number
    running: number
    stopped: number
    error: number
  }
  alerts_count: number
  uptime: number
  timestamp: string
  alert_level: AlertLevel
}

// ===== Dooray 전용 메시지 형식 =====
export interface DoorayMessage {
  botName?: string
  botIconImage?: string
  text: string
  attachments?: DoorayAttachment[]
}

export interface DoorayAttachment {
  title?: string
  titleLink?: string
  text?: string
  color?: 'red' | 'yellow' | 'green' | 'blue' | 'purple' | string
  fields?: DoorayField[]
  imageUrl?: string
  thumbUrl?: string
}

export interface DoorayField {
  title: string
  value: string
  short?: boolean
}

// ===== 웹훅 큐 관리 타입 =====
export interface WebhookQueueItem {
  id: string
  webhook_id: string
  message: WebhookMessage
  priority: 'low' | 'normal' | 'high' | 'critical'
  scheduled_at: string
  max_retries: number
  current_retry: number
  status: WebhookStatus
  created_at: string
}

export interface WebhookQueue {
  items: WebhookQueueItem[]
  total_pending: number
  total_processing: number
  total_failed: number
  is_processing: boolean
  last_processed: string | null
}

// ===== 웹훅 필터 타입 =====
export interface WebhookFilter {
  webhook_ids?: string[]
  message_types?: string[]
  status?: WebhookStatus[]
  alert_levels?: AlertLevel[]
  date_range?: {
    start: string
    end: string
  }
  search?: string
}

// ===== 웹훅 설정 그룹 타입 =====
export interface WebhookSettings {
  posco_news: WebhookConfig
  watchhamster_system: WebhookConfig
  global_settings: {
    enabled: boolean
    default_timeout: number
    default_retry_attempts: number
    rate_limiting: {
      enabled: boolean
      global_limit: number
      time_window: number
    }
    quiet_hours: {
      enabled: boolean
      start: string // HH:MM
      end: string // HH:MM
      timezone: string
    }
    alert_filtering: {
      min_level: AlertLevel
      duplicate_suppression: boolean
      suppression_window: number // minutes
    }
  }
}

// ===== API 요청/응답 타입 =====
export interface SendWebhookRequest {
  webhook_id: string
  message: Omit<WebhookMessage, 'id' | 'webhook_id'>
  priority?: 'low' | 'normal' | 'high' | 'critical'
  scheduled_at?: string
}

export interface SendWebhookResponse {
  message_id: string
  queue_position: number
  estimated_send_time: string
}

export interface GetWebhookHistoryRequest {
  webhook_id?: string
  limit?: number
  offset?: number
  filter?: WebhookFilter
}

export interface GetWebhookHistoryResponse {
  data: WebhookHistory[]
  total: number
  has_more: boolean
}

export interface TestWebhookRequest {
  webhook_id: string
  test_message?: string
}

export interface TestWebhookResponse {
  success: boolean
  response_code?: number
  response_time: number
  error_message?: string
  timestamp: string
}

export interface GetWebhookStatisticsRequest {
  webhook_id?: string
  period?: '1h' | '24h' | '7d' | '30d'
}

export interface GetWebhookStatisticsResponse {
  data: WebhookStatistics[]
  period: string
  generated_at: string
}

// ===== 웹훅 이벤트 타입 =====
export interface WebhookEvent {
  type: 'webhook_sent' | 'webhook_failed' | 'webhook_retry' | 'webhook_cancelled'
  webhook_id: string
  message_id: string
  timestamp: string
  details?: Record<string, any>
}

// ===== 웹훅 컴포넌트 Props 타입 =====
export interface WebhookConfigFormProps {
  config: WebhookConfig
  onConfigChange: (config: WebhookConfig) => void
  onSave: () => void
  onTest: () => void
  onDelete?: () => void
  loading?: boolean
}

export interface WebhookHistoryViewerProps {
  history: WebhookHistory[]
  loading?: boolean
  onLoadMore?: () => void
  hasMore?: boolean
  filter?: WebhookFilter
  onFilterChange?: (filter: WebhookFilter) => void
  onRetry?: (historyId: string) => void
}

export interface WebhookStatisticsWidgetProps {
  statistics: WebhookStatistics
  webhook: WebhookConfig
  period: '1h' | '24h' | '7d' | '30d'
  onPeriodChange?: (period: '1h' | '24h' | '7d' | '30d') => void
}

export interface WebhookTemplateEditorProps {
  template: WebhookTemplate
  onTemplateChange: (template: WebhookTemplate) => void
  onSave: () => void
  onPreview: () => void
  variables?: Record<string, any>
  loading?: boolean
}

// ===== 웹훅 알림 규칙 타입 =====
export interface WebhookAlertRule {
  id: string
  name: string
  description: string
  enabled: boolean
  conditions: {
    news_types?: NewsType[]
    news_status?: NewsStatusType[]
    system_status?: SystemHealthStatus[]
    alert_levels?: AlertLevel[]
    service_ids?: string[]
  }
  webhook_ids: string[]
  template_id?: string
  rate_limit?: {
    max_per_hour: number
    suppress_duplicates: boolean
  }
  schedule?: {
    enabled: boolean
    cron_expression: string
    timezone: string
  }
  created_at: string
  updated_at: string
}

// ===== 웹훅 메시지 빌더 타입 =====
export interface WebhookMessageBuilder {
  buildNewsAlert(payload: PoscoNewsWebhookPayload): DoorayMessage
  buildSystemStatus(payload: PoscoSystemWebhookPayload): DoorayMessage
  buildCustomMessage(title: string, message: string, level: AlertLevel): DoorayMessage
  applyTemplate(template: WebhookTemplate, variables: Record<string, any>): string
}

// ===== 웹훅 전송 결과 타입 =====
export interface WebhookSendResult {
  success: boolean
  message_id: string
  webhook_id: string
  response_code?: number
  response_time: number
  error_message?: string
  retry_count: number
  timestamp: string
}

// ===== 웹훅 배치 작업 타입 =====
export interface WebhookBatchOperation {
  id: string
  type: 'send_multiple' | 'retry_failed' | 'cancel_pending'
  webhook_ids: string[]
  message_ids?: string[]
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  total_items: number
  processed_items: number
  failed_items: number
  started_at: string
  completed_at?: string
  results?: WebhookSendResult[]
}

// ===== 웹훅 모니터링 타입 =====
export interface WebhookMonitoringState {
  is_running: boolean
  queue_size: number
  processing_rate: number // messages per minute
  success_rate: number
  average_response_time: number
  last_processed: string | null
  errors_last_hour: number
  rate_limit_hits: number
}