// 시스템 관련 타입
export interface SystemInfo {
  platform: string
  arch: string
  version: string
  hostname: string
}

export interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  disk_usage: number
  network_status: 'connected' | 'disconnected' | 'limited'
  uptime: number
  active_services: number
  timestamp: string
}

export interface PerformanceMetrics {
  cpu_usage: number[]
  memory_usage: number[]
  disk_io: Record<string, any>
  network_io: Record<string, any>
  timestamps: string[]
}

export interface StabilityMetrics {
  error_count: number
  recovery_count: number
  last_health_check: string
  system_health: 'healthy' | 'warning' | 'critical'
  service_failures: ServiceFailure[]
}

export interface ServiceFailure {
  service_id: string
  error: string
  timestamp: string
  resolved: boolean
}

// 서비스 관련 타입
export interface ServiceInfo {
  id: string
  name: string
  description: string
  status: ServiceStatus
  uptime?: number
  last_error?: string
  config?: Record<string, any>
}

export type ServiceStatus = 'running' | 'stopped' | 'error' | 'starting' | 'stopping'

export interface ServiceAction {
  action: 'start' | 'stop' | 'restart'
  service_id: string
}

// 웹훅 관련 타입
export interface WebhookPayload {
  url: string
  message: string
  webhook_type: 'discord' | 'slack' | 'generic'
  template_id?: string
  variables?: Record<string, any>
}

export interface WebhookTemplate {
  id: string
  name: string
  description: string
  webhook_type: 'discord' | 'slack' | 'generic'
  template: string
  variables: string[]
  created_at: string
  updated_at: string
}

export interface WebhookHistory {
  id: string
  url: string
  message: string
  webhook_type: string
  status: 'success' | 'failed' | 'pending'
  response_code?: number
  error_message?: string
  sent_at: string
}

// WebSocket 관련 타입
export interface WSMessage {
  type:
    | 'status_update'
    | 'service_event'
    | 'alert'
    | 'log_update'
    | 'metrics_update'
    | 'connection_established'
    | 'ping'
    | 'pong'
  data: any
  timestamp: string
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

// 로그 관련 타입
export interface LogEntry {
  id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  service: string
  message: string
  details?: Record<string, any>
}

export interface LogFilter {
  service?: string
  level?: string
  search?: string
  start_time?: string
  end_time?: string
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

// 설정 관련 타입
export interface AppSettings {
  // 일반 설정
  autoRefresh: boolean
  refreshInterval: number
  language: 'ko' | 'en'
  notifications: boolean

  // 테마 설정
  theme: 'light' | 'dark'
  poscoTheme: boolean

  // 알림 설정
  systemAlerts: boolean
  serviceAlerts: boolean
  errorAlerts: boolean
  webhookUrl: string

  // 고급 설정
  logLevel: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  maxLogEntries: number
  backupEnabled: boolean
  backupInterval: number
}

// API 응답 타입
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

export interface ApiError {
  detail: string
  error?: string
  status_code: number
}

// 페이지네이션 응답 타입
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

// API 요청 옵션 타입
export interface ApiRequestOptions {
  timeout?: number
  retries?: number
  retryDelay?: number
  showErrorToast?: boolean
  showSuccessToast?: boolean
  loadingKey?: string
}

// 배치 작업 결과 타입
export interface BatchOperationResult<T = any> {
  success_count: number
  error_count: number
  total_count: number
  results: Array<{
    id: string
    success: boolean
    data?: T
    error?: string
  }>
}

// 헬스 체크 응답 타입
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy' | 'degraded'
  service: string
  version: string
  uptime: number
  timestamp: string
  checks: {
    database?: 'healthy' | 'unhealthy'
    redis?: 'healthy' | 'unhealthy'
    external_apis?: 'healthy' | 'unhealthy'
    disk_space?: 'healthy' | 'unhealthy'
    memory?: 'healthy' | 'unhealthy'
  }
  details?: Record<string, any>
}

// 연결 테스트 응답 타입
export interface ConnectionTestResponse {
  connected: boolean
  latency: number
  version: string
  server_time: string
  features: string[]
}

// 서버 정보 응답 타입
export interface ServerInfoResponse {
  name: string
  version: string
  uptime: number
  environment: 'development' | 'staging' | 'production'
  features: string[]
  system_info: {
    platform: string
    python_version: string
    cpu_count: number
    memory_total: number
  }
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

// 상태 관리 타입
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
