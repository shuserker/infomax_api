/**
 * API 관련 타입 정의
 * 모든 API 요청/응답에 대한 타입 안전성 보장
 */

import { z } from 'zod'

// ===== 기본 스키마 =====

// 공통 응답 스키마
export const ApiResponseSchema = z.object({
  data: z.any(),
  message: z.string().optional(),
  status: z.enum(['success', 'error']),
  timestamp: z.string(),
})

// 페이지네이션 스키마
export const PaginationSchema = z.object({
  page: z.number().min(1),
  size: z.number().min(1).max(100),
  total: z.number().min(0),
  pages: z.number().min(0),
  has_next: z.boolean(),
  has_prev: z.boolean(),
})

// 페이지네이션된 응답 스키마
export const PaginatedResponseSchema = <T extends z.ZodType>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    ...PaginationSchema.shape,
  })

// ===== 시스템 메트릭 스키마 =====

export const SystemMetricsSchema = z.object({
  cpu_percent: z.number().min(0).max(100),
  memory_percent: z.number().min(0).max(100),
  disk_usage: z.number().min(0).max(100),
  network_status: z.enum(['connected', 'disconnected', 'limited']),
  uptime: z.number().min(0),
  active_services: z.number().min(0),
  timestamp: z.string(),
})

export const PerformanceMetricsSchema = z.object({
  cpu_usage: z.array(z.number()),
  memory_usage: z.array(z.number()),
  disk_io: z.record(z.string(), z.any()),
  network_io: z.record(z.string(), z.any()),
  timestamps: z.array(z.string()),
})

// ===== 서비스 관련 스키마 =====

export const ServiceStatusSchema = z.enum(['running', 'stopped', 'error', 'starting', 'stopping'])

export const ServiceInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  status: ServiceStatusSchema,
  uptime: z.number().nullable().optional(),
  last_error: z.string().nullable().optional(),
  config: z.record(z.string(), z.any()).optional(),
})

export const ServiceActionSchema = z.object({
  action: z.enum(['start', 'stop', 'restart']),
  service_id: z.string(),
})

// ===== 웹훅 관련 스키마 =====

export const WebhookTypeSchema = z.enum(['discord', 'slack', 'generic'])

export const WebhookPayloadSchema = z.object({
  url: z.string().url(),
  message: z.string().min(1),
  webhook_type: WebhookTypeSchema,
  template_id: z.string().optional(),
  variables: z.record(z.string(), z.any()).optional(),
})

export const WebhookTemplateSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  description: z.string(),
  webhook_type: WebhookTypeSchema,
  template: z.string().min(1),
  variables: z.array(z.string()),
  created_at: z.string(),
  updated_at: z.string(),
})

// ===== 로그 관련 스키마 =====

export const LogLevelSchema = z.enum(['DEBUG', 'INFO', 'WARN', 'ERROR'])

export const LogEntrySchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  level: LogLevelSchema,
  service: z.string(),
  message: z.string(),
  details: z.record(z.string(), z.any()).optional(),
})

export const LogFilterSchema = z.object({
  service: z.string().optional(),
  level: LogLevelSchema.optional(),
  search: z.string().optional(),
  start_time: z.string().optional(),
  end_time: z.string().optional(),
})

// ===== WebSocket 메시지 스키마 =====

export const WSMessageTypeSchema = z.enum([
  'status_update',
  'service_event',
  'alert',
  'log_update',
  'metrics_update',
  'connection_established',
  'ping',
  'pong',
])

export const WSMessageSchema = z.object({
  type: WSMessageTypeSchema,
  data: z.any(),
  timestamp: z.string(),
})

// ===== 설정 관련 스키마 =====

export const AppSettingsSchema = z.object({
  // 일반 설정
  autoRefresh: z.boolean(),
  refreshInterval: z.number().min(1000).max(60000),
  language: z.enum(['ko', 'en']),
  notifications: z.boolean(),

  // 테마 설정
  theme: z.enum(['light', 'dark']),
  poscoTheme: z.boolean(),

  // 알림 설정
  systemAlerts: z.boolean(),
  serviceAlerts: z.boolean(),
  errorAlerts: z.boolean(),
  webhookUrl: z.string().url().optional(),

  // 고급 설정
  logLevel: LogLevelSchema,
  maxLogEntries: z.number().min(100).max(10000),
  backupEnabled: z.boolean(),
  backupInterval: z.number().min(1).max(24),
})

// ===== 헬스 체크 스키마 =====

export const HealthCheckSchema = z.object({
  status: z.enum(['healthy', 'unhealthy', 'degraded']),
  service: z.string(),
  version: z.string(),
  uptime: z.number(),
  timestamp: z.string(),
  checks: z.object({
    database: z.enum(['healthy', 'unhealthy']).optional(),
    redis: z.enum(['healthy', 'unhealthy']).optional(),
    external_apis: z.enum(['healthy', 'unhealthy']).optional(),
    disk_space: z.enum(['healthy', 'unhealthy']).optional(),
    memory: z.enum(['healthy', 'unhealthy']).optional(),
  }),
  details: z.record(z.string(), z.any()).optional(),
})

// ===== 타입 추출 =====

export type ApiResponse<T = any> = z.infer<typeof ApiResponseSchema> & { data: T }
export type PaginatedResponse<T> = {
  items: T[]
  page: number
  size: number
  total: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

export type SystemMetrics = z.infer<typeof SystemMetricsSchema>
export type PerformanceMetrics = z.infer<typeof PerformanceMetricsSchema>

export type ServiceStatus = z.infer<typeof ServiceStatusSchema>
export type ServiceInfo = z.infer<typeof ServiceInfoSchema>
export type ServiceAction = z.infer<typeof ServiceActionSchema>

export type WebhookType = z.infer<typeof WebhookTypeSchema>
export type WebhookPayload = z.infer<typeof WebhookPayloadSchema>
export type WebhookTemplate = z.infer<typeof WebhookTemplateSchema>

export type LogLevel = z.infer<typeof LogLevelSchema>
export type LogEntry = z.infer<typeof LogEntrySchema>
export type LogFilter = z.infer<typeof LogFilterSchema>

export type WSMessageType = z.infer<typeof WSMessageTypeSchema>
export type WSMessage = z.infer<typeof WSMessageSchema>

export type AppSettings = z.infer<typeof AppSettingsSchema>
export type HealthCheck = z.infer<typeof HealthCheckSchema>

// ===== API 엔드포인트 타입 =====

// GET /api/services
export type GetServicesResponse = ApiResponse<ServiceInfo[]>

// POST /api/services/{service_id}/start
export type ServiceControlRequest = ServiceAction
export type ServiceControlResponse = ApiResponse<{ message: string }>

// GET /api/metrics
export type GetMetricsResponse = ApiResponse<SystemMetrics>

// GET /api/metrics/performance
export type GetPerformanceMetricsResponse = ApiResponse<PerformanceMetrics>

// POST /api/webhook/send
export type SendWebhookRequest = WebhookPayload
export type SendWebhookResponse = ApiResponse<{ message: string; webhook_id: string }>

// GET /api/webhook/templates
export type GetWebhookTemplatesResponse = ApiResponse<WebhookTemplate[]>

// GET /api/logs
export type GetLogsRequest = LogFilter & {
  page?: number
  size?: number
}
export type GetLogsResponse = ApiResponse<PaginatedResponse<LogEntry>>

// GET /api/health
export type GetHealthResponse = ApiResponse<HealthCheck>

// GET /api/settings
export type GetSettingsResponse = ApiResponse<AppSettings>

// PUT /api/settings
export type UpdateSettingsRequest = Partial<AppSettings>
export type UpdateSettingsResponse = ApiResponse<AppSettings>

// ===== 유틸리티 함수 =====

/**
 * API 응답 검증
 */
export const validateApiResponse = <T>(
  data: unknown,
  schema: z.ZodType<T>
): { success: true; data: T } | { success: false; error: string } => {
  try {
    const result = schema.parse(data)
    return { success: true, data: result }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: `검증 실패: ${error.issues.map((e: any) => e.message).join(', ')}`,
      }
    }
    return {
      success: false,
      error: '알 수 없는 검증 오류',
    }
  }
}

/**
 * 안전한 API 응답 파싱
 */
export const parseApiResponse = <T>(
  response: unknown,
  dataSchema: z.ZodType<T>
): ApiResponse<T> => {
  const apiResponseResult = validateApiResponse(response, ApiResponseSchema)
  
  if (!apiResponseResult.success) {
    throw new Error(`API 응답 형식 오류: ${apiResponseResult.error}`)
  }

  const dataResult = validateApiResponse(apiResponseResult.data.data, dataSchema)
  
  if (!dataResult.success) {
    throw new Error(`API 데이터 형식 오류: ${dataResult.error}`)
  }

  return {
    ...apiResponseResult.data,
    data: dataResult.data,
  }
}

/**
 * WebSocket 메시지 검증
 */
export const validateWSMessage = (data: unknown): WSMessage => {
  const result = validateApiResponse(data, WSMessageSchema)
  
  if (!result.success) {
    throw new Error(`WebSocket 메시지 형식 오류: ${result.error}`)
  }
  
  return result.data
}

/**
 * 설정 검증 및 기본값 적용
 */
export const validateSettings = (settings: unknown): AppSettings => {
  const result = validateApiResponse(settings, AppSettingsSchema)
  
  if (!result.success) {
    // 기본 설정 반환
    return {
      autoRefresh: true,
      refreshInterval: 5000,
      language: 'ko',
      notifications: true,
      theme: 'light',
      poscoTheme: true,
      systemAlerts: true,
      serviceAlerts: true,
      errorAlerts: true,
      logLevel: 'INFO',
      maxLogEntries: 1000,
      backupEnabled: false,
      backupInterval: 24,
    }
  }
  
  return result.data
}