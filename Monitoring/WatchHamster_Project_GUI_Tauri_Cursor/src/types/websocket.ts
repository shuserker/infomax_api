/**
 * WebSocket 관련 타입 정의
 * 실시간 통신을 위한 타입들
 */

import { z } from 'zod'
import { NewsStatus, NewsAlert } from './news'
import { SystemStatus, SystemAlert } from './system'
import { WebhookHistory } from './webhook'
import { LogEntry } from './logs'

// ===== WebSocket 메시지 타입 열거형 =====
export type WSMessageType = 
  | 'connection_established'
  | 'connection_lost'
  | 'ping'
  | 'pong'
  | 'status_update'
  | 'news_update'
  | 'system_update'
  | 'service_event'
  | 'alert'
  | 'log_update'
  | 'metrics_update'
  | 'webhook_event'
  | 'error'
  | 'notification'

// ===== WebSocket 메시지 스키마 =====
export const WSMessageSchema = z.object({
  id: z.string(),
  type: z.enum([
    'connection_established',
    'connection_lost',
    'ping',
    'pong',
    'status_update',
    'news_update',
    'system_update',
    'service_event',
    'alert',
    'log_update',
    'metrics_update',
    'webhook_event',
    'error',
    'notification'
  ]),
  data: z.any(),
  timestamp: z.string(),
  source: z.string().optional(),
  correlation_id: z.string().optional(),
})

// ===== 연결 상태 스키마 =====
export const WSConnectionStateSchema = z.object({
  status: z.enum(['connecting', 'connected', 'disconnected', 'reconnecting', 'error']),
  url: z.string(),
  connected_at: z.string().optional(),
  disconnected_at: z.string().optional(),
  reconnect_attempts: z.number().min(0),
  last_error: z.string().optional(),
})

// ===== WebSocket 설정 스키마 =====
export const WSConfigSchema = z.object({
  url: z.string().url(),
  auto_reconnect: z.boolean(),
  max_reconnect_attempts: z.number().min(0).max(100),
  reconnect_delay: z.number().min(1000).max(60000), // milliseconds
  ping_interval: z.number().min(5000).max(300000), // milliseconds
  pong_timeout: z.number().min(1000).max(30000), // milliseconds
  message_queue_size: z.number().min(10).max(10000),
  compression: z.boolean(),
})

// ===== 타입 추출 =====
export type WSMessage = z.infer<typeof WSMessageSchema>
export type WSConnectionState = z.infer<typeof WSConnectionStateSchema>
export type WSConfig = z.infer<typeof WSConfigSchema>

// ===== 특정 메시지 타입들 =====
export interface WSConnectionMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'connection_established'
  data: {
    client_id: string
    server_version: string
    supported_features: string[]
    session_id: string
  }
}

export interface WSPingMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'ping'
  data: {
    timestamp: string
  }
}

export interface WSPongMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'pong'
  data: {
    timestamp: string
    latency?: number
  }
}

export interface WSNewsUpdateMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'news_update'
  data: {
    news_status: NewsStatus[]
    changed_types: string[]
    summary: {
      total: number
      healthy: number
      warning: number
      error: number
    }
  }
}

export interface WSSystemUpdateMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'system_update'
  data: {
    system_status: SystemStatus
    changed_services: string[]
    metrics_updated: boolean
  }
}

export interface WSServiceEventMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'service_event'
  data: {
    service_id: string
    event_type: 'started' | 'stopped' | 'error' | 'restarted' | 'status_changed'
    message: string
    details?: Record<string, any>
    previous_status?: string
    current_status: string
  }
}

export interface WSAlertMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'alert'
  data: {
    alert: SystemAlert | NewsAlert
    alert_type: 'system' | 'news' | 'webhook' | 'custom'
    requires_action: boolean
  }
}

export interface WSLogUpdateMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'log_update'
  data: {
    logs: LogEntry[]
    total_new: number
    source: string
  }
}

export interface WSMetricsUpdateMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'metrics_update'
  data: {
    cpu_percent: number
    memory_percent: number
    disk_usage: number
    network_status: string
    active_services: number
    timestamp: string
  }
}

export interface WSWebhookEventMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'webhook_event'
  data: {
    webhook_id: string
    event_type: 'sent' | 'failed' | 'retry' | 'cancelled'
    message_id: string
    status: string
    details?: Record<string, any>
  }
}

export interface WSErrorMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'error'
  data: {
    error_code: string
    error_message: string
    details?: Record<string, any>
    recoverable: boolean
  }
}

export interface WSNotificationMessage extends Omit<WSMessage, 'type' | 'data'> {
  type: 'notification'
  data: {
    title: string
    message: string
    level: 'info' | 'warning' | 'error' | 'success'
    action?: {
      label: string
      url?: string
      callback?: string
    }
    auto_dismiss: boolean
    duration?: number
  }
}

// ===== WebSocket 이벤트 리스너 타입 =====
export interface WSEventListeners {
  onConnect?: (event: WSConnectionMessage) => void
  onDisconnect?: (event: { code: number; reason: string }) => void
  onMessage?: (message: WSMessage) => void
  onError?: (error: WSErrorMessage) => void
  onNewsUpdate?: (message: WSNewsUpdateMessage) => void
  onSystemUpdate?: (message: WSSystemUpdateMessage) => void
  onServiceEvent?: (message: WSServiceEventMessage) => void
  onAlert?: (message: WSAlertMessage) => void
  onLogUpdate?: (message: WSLogUpdateMessage) => void
  onMetricsUpdate?: (message: WSMetricsUpdateMessage) => void
  onWebhookEvent?: (message: WSWebhookEventMessage) => void
  onNotification?: (message: WSNotificationMessage) => void
}

// ===== WebSocket 클라이언트 인터페이스 =====
export interface WSClient {
  connect(): Promise<void>
  disconnect(): void
  send(message: Omit<WSMessage, 'id' | 'timestamp'>): void
  subscribe(eventType: WSMessageType, callback: (message: WSMessage) => void): () => void
  unsubscribe(eventType: WSMessageType, callback?: (message: WSMessage) => void): void
  getConnectionState(): WSConnectionState
  isConnected(): boolean
  ping(): Promise<number> // returns latency in ms
}

// ===== WebSocket 상태 관리 타입 =====
export interface WSState {
  connection: WSConnectionState
  config: WSConfig
  listeners: Map<WSMessageType, Set<(message: WSMessage) => void>>
  messageQueue: WSMessage[]
  statistics: {
    messages_sent: number
    messages_received: number
    reconnect_count: number
    average_latency: number
    last_ping: number
    uptime: number
  }
}

// ===== WebSocket 메시지 필터 타입 =====
export interface WSMessageFilter {
  types?: WSMessageType[]
  sources?: string[]
  correlation_ids?: string[]
  since?: string
  limit?: number
}

// ===== WebSocket 메시지 히스토리 타입 =====
export interface WSMessageHistory {
  messages: WSMessage[]
  total: number
  filtered: number
  oldest: string
  newest: string
}

// ===== WebSocket 연결 통계 타입 =====
export interface WSConnectionStats {
  total_connections: number
  successful_connections: number
  failed_connections: number
  total_disconnections: number
  average_connection_duration: number
  longest_connection_duration: number
  reconnect_success_rate: number
  message_throughput: {
    sent_per_minute: number
    received_per_minute: number
  }
  error_rate: number
  last_24h: {
    connections: number
    messages_sent: number
    messages_received: number
    errors: number
  }
}

// ===== WebSocket 설정 컴포넌트 Props 타입 =====
export interface WSConfigFormProps {
  config: WSConfig
  onConfigChange: (config: WSConfig) => void
  onSave: () => void
  onTest: () => void
  loading?: boolean
  connectionState: WSConnectionState
}

export interface WSConnectionStatusProps {
  state: WSConnectionState
  stats?: WSConnectionStats
  onReconnect?: () => void
  onDisconnect?: () => void
  showDetails?: boolean
}

export interface WSMessageViewerProps {
  messages: WSMessage[]
  filter?: WSMessageFilter
  onFilterChange?: (filter: WSMessageFilter) => void
  onMessageClick?: (message: WSMessage) => void
  maxMessages?: number
  autoScroll?: boolean
}

// ===== WebSocket 유틸리티 타입 =====
export interface WSMessageBuilder {
  createPing(): WSPingMessage
  createPong(pingTimestamp: string): WSPongMessage
  createStatusUpdate(data: any): WSMessage
  createAlert(alert: SystemAlert | NewsAlert): WSAlertMessage
  createNotification(title: string, message: string, level: 'info' | 'warning' | 'error' | 'success'): WSNotificationMessage
}

export interface WSMessageValidator {
  validate(message: unknown): { valid: boolean; error?: string }
  validateType(type: string): boolean
  sanitizeMessage(message: WSMessage): WSMessage
}

// ===== WebSocket 보안 타입 =====
export interface WSSecurityConfig {
  origin_whitelist: string[]
  max_message_size: number
  rate_limit: {
    messages_per_minute: number
    burst_limit: number
  }
  authentication: {
    required: boolean
    token_header: string
    token_validation_url?: string
  }
}

// ===== WebSocket 모니터링 타입 =====
export interface WSMonitoringData {
  connection_state: WSConnectionState
  message_stats: {
    total_sent: number
    total_received: number
    errors: number
    last_message: string | null
  }
  performance: {
    average_latency: number
    message_throughput: number
    connection_uptime: number
  }
  health: {
    status: 'healthy' | 'degraded' | 'unhealthy'
    issues: string[]
    last_check: string
  }
}