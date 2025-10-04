// 새로운 타입 모듈들을 re-export
export * from './news'
export * from './system'
export * from './webhook'
export * from './settings'
export * from './websocket'
export * from './api'
export * from './logs'

// 기존 호환성을 위한 타입 별칭들
export type { SystemInfo, SystemMetrics, PerformanceMetrics } from './system'
export type { ServiceInfo, ServiceStatus } from './system'
export type { NewsStatus, NewsHistory } from './news'
export type { WebhookConfig as WebhookPayload, WebhookTemplate, WebhookHistory } from './webhook'

// 레거시 타입들 (하위 호환성)
export interface StabilityMetrics {
  error_count: number
  recovery_count: number
  last_health_check: string
  system_health: 'healthy' | 'warning' | 'critical'
  service_failures: ServiceFailure[]
}

export interface HealthCheckResponse {
  status: string
  service: string
  version: string
  timestamp?: string
  uptime?: number
}

export interface ServiceFailure {
  service_id: string
  error: string
  timestamp: string
  resolved: boolean
}

export interface ServiceAction {
  action: 'start' | 'stop' | 'restart'
  service_id: string
}

export interface ServiceEvent {
  service_id: string
  event_type: 'started' | 'stopped' | 'error' | 'restarted'
  message: string
  details?: Record<string, any>
}

export interface SystemAlert {
  alert_type: string
  message: string
  severity: 'info' | 'warning' | 'error' | 'critical'
}

// 로그 관련 타입 (레거시 호환성)
export interface LogEntry {
  id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
  service: string
  message: string
  details?: Record<string, any>
}

// UI 관련 타입
export interface NavigationItem {
  name: string
  path: string
  icon: React.ComponentType
}

export interface ToastMessage {
  title: string
  description?: string
  status: 'success' | 'error' | 'warning' | 'info'
  duration?: number
  isClosable?: boolean
}

// Tauri 관련 타입
export interface TauriCommand<T = any> {
  command: string
  payload?: any
  response?: T
}

export interface BackendStatus {
  running: boolean
  port: number
  uptime?: number
  last_error?: string
}

// 차트 관련 타입
export interface ChartDataPoint {
  timestamp: string
  value: number
  label?: string
}

export interface ChartConfig {
  title: string
  color: string
  unit?: string
  min?: number
  max?: number
}

// 테이블 관련 타입
export interface TableColumn<T = any> {
  key: keyof T
  label: string
  sortable?: boolean
  render?: (value: any, row: T) => React.ReactNode
}

export interface TableProps<T = any> {
  data: T[]
  columns: TableColumn<T>[]
  loading?: boolean
  pagination?: boolean
  pageSize?: number
}

// 폼 관련 타입
export interface FormField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'textarea' | 'switch' | 'checkbox'
  required?: boolean
  options?: { value: string; label: string }[]
  placeholder?: string
  helperText?: string
}

// 유틸리티 타입
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

// 상태 관리 타입 (레거시 호환성)
export interface AppState {
  services: ServiceInfo[]
  systemMetrics: SystemMetrics | null
  isConnected: boolean
  settings: AppSettings
  notifications: ToastMessage[]
}

export interface AppActions {
  updateServices: (services: ServiceInfo[]) => void
  updateSystemMetrics: (metrics: SystemMetrics) => void
  setConnectionStatus: (connected: boolean) => void
  updateSettings: (settings: Partial<AppSettings>) => void
  addNotification: (notification: ToastMessage) => void
  removeNotification: (id: string) => void
}
