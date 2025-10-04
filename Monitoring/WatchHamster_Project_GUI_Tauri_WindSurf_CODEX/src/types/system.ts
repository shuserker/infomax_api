/**
 * 시스템 모니터링 관련 타입 정의
 * WatchHamster 시스템 모니터링을 위한 타입들
 */

import { z } from 'zod'

// ===== 시스템 상태 열거형 =====
export type SystemHealthStatus = 'healthy' | 'warning' | 'critical' | 'unknown'
export type ServiceStatus = 'running' | 'stopped' | 'error' | 'starting' | 'stopping' | 'unknown'
export type ProcessStatus = 'active' | 'inactive' | 'failed' | 'unknown'

// ===== 시스템 정보 스키마 =====
export const SystemInfoSchema = z.object({
  platform: z.string(),
  arch: z.string(),
  version: z.string(),
  hostname: z.string(),
  python_version: z.string(),
  cpu_count: z.number(),
  memory_total: z.number(), // bytes
  disk_total: z.number(), // bytes
  boot_time: z.string(),
  timezone: z.string(),
})

// ===== 시스템 메트릭 스키마 =====
export const SystemMetricsSchema = z.object({
  cpu_percent: z.number().min(0).max(100),
  memory_percent: z.number().min(0).max(100),
  memory_used: z.number().min(0), // bytes
  memory_available: z.number().min(0), // bytes
  disk_usage: z.number().min(0).max(100),
  disk_used: z.number().min(0), // bytes
  disk_free: z.number().min(0), // bytes
  network_status: z.enum(['connected', 'disconnected', 'limited']),
  network_bytes_sent: z.number().min(0),
  network_bytes_recv: z.number().min(0),
  uptime: z.number().min(0), // seconds
  load_average: z.array(z.number()).optional(), // 1, 5, 15분 평균
  active_services: z.number().min(0),
  timestamp: z.string(),
})

// ===== 성능 메트릭 스키마 =====
export const PerformanceMetricsSchema = z.object({
  cpu_usage: z.array(z.number()),
  memory_usage: z.array(z.number()),
  disk_io: z.object({
    read_bytes: z.array(z.number()),
    write_bytes: z.array(z.number()),
    read_count: z.array(z.number()),
    write_count: z.array(z.number()),
  }),
  network_io: z.object({
    bytes_sent: z.array(z.number()),
    bytes_recv: z.array(z.number()),
    packets_sent: z.array(z.number()),
    packets_recv: z.array(z.number()),
  }),
  timestamps: z.array(z.string()),
  interval: z.number(), // seconds
})

// ===== 프로세스 정보 스키마 =====
export const ProcessInfoSchema = z.object({
  pid: z.number(),
  name: z.string(),
  status: z.enum(['active', 'inactive', 'failed', 'unknown']),
  cpu_percent: z.number().min(0),
  memory_percent: z.number().min(0),
  memory_rss: z.number().min(0), // bytes
  memory_vms: z.number().min(0), // bytes
  create_time: z.string(),
  cmdline: z.array(z.string()).optional(),
  cwd: z.string().optional(),
  num_threads: z.number().optional(),
})

// ===== 서비스 정보 스키마 =====
export const ServiceInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  status: z.enum(['running', 'stopped', 'error', 'starting', 'stopping', 'unknown']),
  pid: z.number().nullable().optional(),
  uptime: z.number().nullable().optional(), // seconds
  restart_count: z.number().min(0),
  last_restart: z.string().nullable().optional(),
  last_error: z.string().nullable().optional(),
  error_count: z.number().min(0),
  config: z.record(z.string(), z.any()).optional(),
  dependencies: z.array(z.string()).optional(),
  auto_restart: z.boolean(),
  health_check_url: z.string().optional(),
  log_file: z.string().optional(),
})

// ===== Git 상태 스키마 =====
export const GitStatusSchema = z.object({
  branch: z.string(),
  commit_hash: z.string(),
  commit_message: z.string(),
  commit_author: z.string(),
  commit_date: z.string(),
  has_uncommitted_changes: z.boolean(),
  has_untracked_files: z.boolean(),
  has_conflicts: z.boolean(),
  remote_status: z.enum(['up-to-date', 'ahead', 'behind', 'diverged', 'unknown']),
  remote_url: z.string().optional(),
  ahead_count: z.number().min(0).optional(),
  behind_count: z.number().min(0).optional(),
  last_fetch: z.string().optional(),
  repository_status: z.enum(['clean', 'dirty', 'conflict', 'unknown']),
})

// ===== 시스템 상태 스키마 =====
export const SystemStatusSchema = z.object({
  overall: z.enum(['healthy', 'warning', 'critical', 'unknown']),
  services: z.array(ServiceInfoSchema),
  metrics: SystemMetricsSchema,
  git_status: GitStatusSchema.optional(),
  processes: z.array(ProcessInfoSchema).optional(),
  last_check: z.string(),
  uptime: z.number(),
  alerts: z.array(z.object({
    id: z.string(),
    type: z.string(),
    message: z.string(),
    severity: z.enum(['info', 'warning', 'error', 'critical']),
    timestamp: z.string(),
    acknowledged: z.boolean(),
  })),
})

// ===== 시스템 설정 스키마 =====
export const SystemSettingsSchema = z.object({
  monitoring: z.object({
    check_interval: z.number().min(5).max(300), // 5초 ~ 5분
    metrics_retention: z.number().min(1).max(168), // 1시간 ~ 1주일
    alert_thresholds: z.object({
      cpu_percent: z.number().min(50).max(95),
      memory_percent: z.number().min(50).max(95),
      disk_percent: z.number().min(70).max(95),
      service_restart_count: z.number().min(3).max(20),
    }),
    auto_restart: z.object({
      enabled: z.boolean(),
      max_attempts: z.number().min(1).max(10),
      restart_delay: z.number().min(5).max(300), // seconds
      services: z.array(z.string()),
    }),
  }),
  git: z.object({
    auto_fetch: z.boolean(),
    fetch_interval: z.number().min(300).max(3600), // 5분 ~ 1시간
    auto_resolve_conflicts: z.boolean(),
    branch_protection: z.array(z.string()),
  }),
  notifications: z.object({
    enabled: z.boolean(),
    webhook_url: z.string().optional(),
    alert_levels: z.array(z.enum(['info', 'warning', 'error', 'critical'])),
    quiet_hours: z.object({
      enabled: z.boolean(),
      start: z.string(), // HH:MM
      end: z.string(), // HH:MM
      timezone: z.string(),
    }),
  }),
})

// ===== 타입 추출 =====
export type SystemInfo = z.infer<typeof SystemInfoSchema>
export type SystemMetrics = z.infer<typeof SystemMetricsSchema>
export type PerformanceMetrics = z.infer<typeof PerformanceMetricsSchema>
export type ProcessInfo = z.infer<typeof ProcessInfoSchema>
export type ServiceInfo = z.infer<typeof ServiceInfoSchema>
export type GitStatus = z.infer<typeof GitStatusSchema>
export type SystemStatus = z.infer<typeof SystemStatusSchema>
export type SystemSettings = z.infer<typeof SystemSettingsSchema>

// ===== 시스템 알림 타입 =====
export interface SystemAlert {
  id: string
  type: 'cpu' | 'memory' | 'disk' | 'service' | 'git' | 'process' | 'network'
  message: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  timestamp: string
  source: string
  details?: Record<string, any>
  acknowledged: boolean
  auto_resolve: boolean
}

// ===== 시스템 액션 타입 =====
export interface SystemAction {
  type: 'start_service' | 'stop_service' | 'restart_service' | 'kill_process' | 'git_pull' | 'git_reset'
  target: string
  parameters?: Record<string, any>
}

export interface SystemActionResult {
  success: boolean
  message: string
  details?: Record<string, any>
  timestamp: string
}

// ===== 리소스 사용량 타입 =====
export interface ResourceUsage {
  current: number
  average: number
  peak: number
  unit: string
  threshold?: number
  status: 'normal' | 'warning' | 'critical'
}

export interface ResourceSummary {
  cpu: ResourceUsage
  memory: ResourceUsage
  disk: ResourceUsage
  network: {
    bytes_sent: number
    bytes_recv: number
    status: 'connected' | 'disconnected' | 'limited'
  }
}

// ===== 서비스 제어 타입 =====
export interface ServiceControl {
  service_id: string
  action: 'start' | 'stop' | 'restart' | 'reload' | 'status'
  force?: boolean
  timeout?: number
}

export interface ServiceControlResult {
  service_id: string
  action: string
  success: boolean
  message: string
  new_status: ServiceStatus
  timestamp: string
}

// ===== 시스템 모니터링 상태 타입 =====
export interface MonitoringState {
  is_running: boolean
  start_time: string | null
  last_check: string | null
  next_check: string | null
  check_interval: number
  total_checks: number
  failed_checks: number
  uptime: number
  error_rate: number
}

// ===== API 요청/응답 타입 =====
export interface GetSystemStatusRequest {
  include_processes?: boolean
  include_git?: boolean
  include_metrics?: boolean
}

export interface GetSystemStatusResponse {
  data: SystemStatus
  timestamp: string
}

export interface GetSystemMetricsRequest {
  period?: '1h' | '6h' | '24h' | '7d'
  interval?: number
}

export interface GetSystemMetricsResponse {
  data: PerformanceMetrics
  period: string
  interval: number
  timestamp: string
}

export interface ControlServiceRequest {
  service_id: string
  action: 'start' | 'stop' | 'restart'
  force?: boolean
}

export interface ControlServiceResponse {
  result: ServiceControlResult
  timestamp: string
}

export interface UpdateSystemSettingsRequest {
  settings: Partial<SystemSettings>
}

export interface UpdateSystemSettingsResponse {
  settings: SystemSettings
  applied_changes: string[]
  timestamp: string
}

// ===== 컴포넌트 Props 타입 =====
export interface SystemMetricsWidgetProps {
  metrics: SystemMetrics
  showDetails?: boolean
  onAlert?: (alert: SystemAlert) => void
}

export interface ServiceCardProps {
  service: ServiceInfo
  onControl: (action: ServiceControl) => void
  onViewLogs?: () => void
  compact?: boolean
}

export interface GitStatusWidgetProps {
  gitStatus: GitStatus
  onAction?: (action: SystemAction) => void
  showDetails?: boolean
}

export interface SystemAlertsProps {
  alerts: SystemAlert[]
  onAcknowledge: (alertId: string) => void
  onDismiss: (alertId: string) => void
  maxVisible?: number
}

export interface PerformanceChartProps {
  metrics: PerformanceMetrics
  type: 'cpu' | 'memory' | 'disk' | 'network'
  height?: number
  showLegend?: boolean
}

// ===== 시스템 헬스 체크 타입 =====
export interface HealthCheck {
  component: string
  status: 'healthy' | 'unhealthy' | 'degraded'
  message: string
  details?: Record<string, any>
  last_check: string
  response_time?: number
}

export interface SystemHealthReport {
  overall_status: SystemHealthStatus
  checks: HealthCheck[]
  uptime: number
  last_restart: string | null
  performance_score: number
  recommendations: string[]
  timestamp: string
}

// ===== 시스템 백업/복원 타입 =====
export interface SystemBackup {
  id: string
  name: string
  description?: string
  created_at: string
  size: number
  includes: {
    settings: boolean
    logs: boolean
    data: boolean
    git_state: boolean
  }
  status: 'creating' | 'completed' | 'failed'
}

export interface BackupRestoreOperation {
  backup_id: string
  operation: 'backup' | 'restore'
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  message: string
  started_at: string
  completed_at?: string
}

// ===== 시스템 로그 타입 =====
export interface SystemLogEntry {
  id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
  component: string
  message: string
  details?: Record<string, any>
  correlation_id?: string
}

export interface SystemLogFilter {
  components?: string[]
  levels?: string[]
  search?: string
  start_time?: string
  end_time?: string
  correlation_id?: string
}

// ===== 시스템 통계 타입 =====
export interface SystemStatistics {
  uptime: number
  total_requests: number
  successful_requests: number
  failed_requests: number
  average_response_time: number
  peak_cpu_usage: number
  peak_memory_usage: number
  service_restarts: number
  git_commits: number
  alerts_generated: number
  period: string
  generated_at: string
}