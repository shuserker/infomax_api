/**
 * API 응답 런타임 타입 검증 유틸리티
 * Zod를 사용한 타입 안전성 강화
 */

import { z } from 'zod'

// ===================
// 기본 스키마 정의
// ===================

// 서비스 상태 스키마
const ServiceStatusSchema = z.enum(['running', 'stopped', 'error', 'starting', 'stopping'])

// 서비스 정보 스키마
export const ServiceInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  status: ServiceStatusSchema,
  uptime: z.number().optional(),
  last_error: z.string().optional(),
  config: z.record(z.string(), z.any()).optional(),
})

// 시스템 메트릭 스키마
export const SystemMetricsSchema = z.object({
  cpu_percent: z.number().min(0).max(100),
  memory_percent: z.number().min(0).max(100),
  disk_usage: z.number().min(0).max(100),
  network_status: z.enum(['connected', 'disconnected', 'limited']),
  uptime: z.number().min(0),
  active_services: z.number().min(0),
  timestamp: z.string(),
})

// 성능 메트릭 스키마
export const PerformanceMetricsSchema = z.object({
  cpu_usage: z.array(z.number()),
  memory_usage: z.array(z.number()),
  disk_io: z.record(z.string(), z.any()),
  network_io: z.record(z.string(), z.any()),
  timestamps: z.array(z.string()),
})

// 안정성 메트릭 스키마
export const StabilityMetricsSchema = z.object({
  error_count: z.number().min(0),
  recovery_count: z.number().min(0),
  last_health_check: z.string(),
  system_health: z.enum(['healthy', 'warning', 'critical']),
  service_failures: z.array(z.object({
    service_id: z.string(),
    error: z.string(),
    timestamp: z.string(),
    resolved: z.boolean(),
  })),
})

// 웹훅 페이로드 스키마
export const WebhookPayloadSchema = z.object({
  url: z.string().url('유효한 URL을 입력해주세요'),
  message: z.string().min(1, '메시지는 필수입니다'),
  webhook_type: z.enum(['discord', 'slack', 'generic']),
  template_id: z.string().optional(),
  variables: z.record(z.string(), z.any()).optional(),
})

// 웹훅 템플릿 스키마
export const WebhookTemplateSchema = z.object({
  id: z.string(),
  name: z.string().min(1, '템플릿 이름은 필수입니다'),
  description: z.string(),
  webhook_type: z.enum(['discord', 'slack', 'generic']),
  template: z.string().min(1, '템플릿 내용은 필수입니다'),
  variables: z.array(z.string()),
  created_at: z.string(),
  updated_at: z.string(),
})

// 로그 엔트리 스키마
export const LogEntrySchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  level: z.enum(['DEBUG', 'INFO', 'WARN', 'ERROR']),
  service: z.string(),
  message: z.string(),
  details: z.record(z.string(), z.any()).optional(),
})

// 페이지네이션 응답 스키마
export const PaginatedResponseSchema = <T>(itemSchema: z.ZodSchema<T>) =>
  z.object({
    items: z.array(itemSchema),
    total: z.number().min(0),
    page: z.number().min(1),
    size: z.number().min(1),
    pages: z.number().min(0),
    has_next: z.boolean(),
    has_prev: z.boolean(),
  })

// 헬스 체크 응답 스키마
export const HealthCheckResponseSchema = z.object({
  status: z.enum(['healthy', 'unhealthy', 'degraded']),
  service: z.string(),
  version: z.string(),
  uptime: z.number().min(0),
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

// ===================
// 검증 유틸리티 함수
// ===================

/**
 * 안전한 JSON 파싱 및 스키마 검증
 */
export const safeParseWithSchema = <T>(
  data: unknown,
  schema: z.ZodSchema<T>
): { success: true; data: T } | { success: false; error: string } => {
  try {
    const result = schema.safeParse(data)
    
    if (result.success) {
      return { success: true, data: result.data }
    } else {
      const errorMessages = result.error.issues.map(err => 
        `${err.path.join('.')}: ${err.message}`
      ).join(', ')
      
      return { 
        success: false, 
        error: `데이터 검증 실패: ${errorMessages}` 
      }
    }
  } catch (error) {
    return { 
      success: false, 
      error: `스키마 검증 중 오류 발생: ${error instanceof Error ? error.message : '알 수 없는 오류'}` 
    }
  }
}

/**
 * API 응답 검증 래퍼
 */
export const validateApiResponse = <T>(
  response: unknown,
  schema: z.ZodSchema<T>,
  context: string = 'API 응답'
): T => {
  const result = safeParseWithSchema(response, schema)
  
  if (!result.success) {
    console.error(`${context} 검증 실패:`, result.error)
    throw new Error(`${context} 형식이 올바르지 않습니다: ${result.error}`)
  }
  
  return result.data
}

/**
 * 배열 응답 검증
 */
export const validateArrayResponse = <T>(
  response: unknown,
  itemSchema: z.ZodSchema<T>,
  context: string = 'API 배열 응답'
): T[] => {
  const arraySchema = z.array(itemSchema)
  return validateApiResponse(response, arraySchema, context)
}

/**
 * 페이지네이션 응답 검증
 */
export const validatePaginatedResponse = <T>(
  response: unknown,
  itemSchema: z.ZodSchema<T>,
  context: string = 'API 페이지네이션 응답'
): z.infer<ReturnType<typeof PaginatedResponseSchema<T>>> => {
  const paginatedSchema = PaginatedResponseSchema(itemSchema)
  return validateApiResponse(response, paginatedSchema, context)
}

// ===================
// 폼 검증 스키마
// ===================

// 서비스 제어 폼 스키마
export const ServiceControlFormSchema = z.object({
  serviceId: z.string().min(1, '서비스 ID는 필수입니다'),
  action: z.enum(['start', 'stop', 'restart']),
})

// 웹훅 전송 폼 스키마
export const WebhookSendFormSchema = z.object({
  url: z.string().url('유효한 웹훅 URL을 입력해주세요'),
  message: z.string().min(1, '메시지는 필수입니다').max(2000, '메시지는 2000자를 초과할 수 없습니다'),
  webhook_type: z.enum(['discord', 'slack', 'generic']),
  template_id: z.string().optional(),
  variables: z.record(z.string(), z.string()).optional(),
})

// 웹훅 템플릿 생성/수정 폼 스키마
export const WebhookTemplateFormSchema = z.object({
  name: z.string().min(1, '템플릿 이름은 필수입니다').max(100, '템플릿 이름은 100자를 초과할 수 없습니다'),
  description: z.string().max(500, '설명은 500자를 초과할 수 없습니다'),
  webhook_type: z.enum(['discord', 'slack', 'generic']),
  template: z.string().min(1, '템플릿 내용은 필수입니다').max(5000, '템플릿 내용은 5000자를 초과할 수 없습니다'),
  variables: z.array(z.string()).default([]),
})

// 로그 필터 폼 스키마
export const LogFilterFormSchema = z.object({
  service: z.string().optional(),
  level: z.enum(['DEBUG', 'INFO', 'WARN', 'ERROR']).optional(),
  search: z.string().max(200, '검색어는 200자를 초과할 수 없습니다').optional(),
  start_time: z.string().optional(),
  end_time: z.string().optional(),
  limit: z.number().min(1).max(1000).default(100),
  page: z.number().min(1).default(1),
})

// POSCO 브랜치 전환 폼 스키마
export const PoscoBranchSwitchFormSchema = z.object({
  branch: z.string().min(1, '브랜치 이름은 필수입니다').regex(
    /^[a-zA-Z0-9_\-/]+$/,
    '브랜치 이름에는 영문, 숫자, _, -, /만 사용할 수 있습니다'
  ),
})

// POSCO 배포 옵션 폼 스키마
export const PoscoDeployFormSchema = z.object({
  force: z.boolean().default(false),
  backup: z.boolean().default(true),
})

// ===================
// 타입 추론 헬퍼
// ===================

// 스키마에서 타입 추론
export type ServiceInfo = z.infer<typeof ServiceInfoSchema>
export type SystemMetrics = z.infer<typeof SystemMetricsSchema>
export type PerformanceMetrics = z.infer<typeof PerformanceMetricsSchema>
export type StabilityMetrics = z.infer<typeof StabilityMetricsSchema>
export type WebhookPayload = z.infer<typeof WebhookPayloadSchema>
export type WebhookTemplate = z.infer<typeof WebhookTemplateSchema>
export type LogEntry = z.infer<typeof LogEntrySchema>
export type HealthCheckResponse = z.infer<typeof HealthCheckResponseSchema>

// 폼 타입 추론
export type ServiceControlForm = z.infer<typeof ServiceControlFormSchema>
export type WebhookSendForm = z.infer<typeof WebhookSendFormSchema>
export type WebhookTemplateForm = z.infer<typeof WebhookTemplateFormSchema>
export type LogFilterForm = z.infer<typeof LogFilterFormSchema>
export type PoscoBranchSwitchForm = z.infer<typeof PoscoBranchSwitchFormSchema>
export type PoscoDeployForm = z.infer<typeof PoscoDeployFormSchema>

// ===================
// 검증 결과 타입
// ===================

export interface ValidationResult<T> {
  success: boolean
  data?: T
  errors?: string[]
}

/**
 * 폼 데이터 검증 헬퍼
 */
export const validateFormData = <T>(
  data: unknown,
  schema: z.ZodSchema<T>
): ValidationResult<T> => {
  const result = schema.safeParse(data)
  
  if (result.success) {
    return {
      success: true,
      data: result.data,
    }
  } else {
    return {
      success: false,
      errors: result.error.issues.map(err => 
        `${err.path.join('.')}: ${err.message}`
      ),
    }
  }
}

/**
 * 실시간 필드 검증 헬퍼
 */
export const validateField = <T>(
  value: unknown,
  schema: z.ZodSchema<T>,
  fieldName: string
): { isValid: boolean; error?: string } => {
  const result = schema.safeParse(value)
  
  if (result.success) {
    return { isValid: true }
  } else {
    const fieldError = result.error.issues.find(err => 
      err.path.length === 0 || err.path[0] === fieldName
    )
    
    return {
      isValid: false,
      error: fieldError?.message || '유효하지 않은 값입니다',
    }
  }
}