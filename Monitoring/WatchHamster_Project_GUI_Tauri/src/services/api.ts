import { AxiosRequestConfig } from 'axios'

// 커스텀 에러 클래스
export class ApiServiceError extends Error {
  public readonly status?: number
  public readonly code?: string
  public readonly details?: any

  constructor(message: string, status?: number, code?: string, details?: any) {
    super(message)
    this.name = 'ApiServiceError'
    this.status = status
    this.code = code
    this.details = details
  }
}

// 사용하지 않는 함수들 제거됨 (interceptors.ts에서 관리)

// API 클라이언트 팩토리에서 클라이언트 가져오기
import { mainApiClient, metricsApiClient, logsApiClient, webhookApiClient, poscoApiClient } from './apiClient'

// 기본 API 클라이언트
const apiClient = mainApiClient

// 인터셉터는 apiClient.ts에서 관리됨

// 타입 정의 및 검증 스키마
import type {
  ServiceInfo,
  SystemMetrics,
  PerformanceMetrics,
  StabilityMetrics,
  WebhookPayload,
  WebhookTemplate,
  WebhookHistory,
  LogEntry,
  LogFilter,
  ServiceAction,
  HealthCheckResponse
} from '../types'

// 런타임 검증을 위한 스키마 import
import {
  ServiceInfoSchema,
  SystemMetricsSchema,
  PerformanceMetricsSchema,
  StabilityMetricsSchema,
  WebhookTemplateSchema,
  LogEntrySchema,
  HealthCheckResponseSchema,
  validateApiResponse,
  validateArrayResponse,
  validatePaginatedResponse
} from './validators'

// API 응답 래퍼 타입 (향후 사용 예정)
// interface ApiResponseWrapper<T> {
//   data: T
//   message?: string
//   status: 'success' | 'error'
//   timestamp?: string
// }

// 페이지네이션 응답 타입
interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 헬스 체크 응답 타입은 types/index.ts에서 import

// API 서비스 클래스
export class ApiService {
  private readonly baseClient = apiClient
  private readonly metricsClient = metricsApiClient
  private readonly logsClient = logsApiClient
  private readonly webhookClient = webhookApiClient
  private readonly poscoClient = poscoApiClient

  // 공통 요청 래퍼 - 타입 안전성과 에러 처리 강화
  private async request<T>(
    method: 'get' | 'post' | 'put' | 'delete' | 'patch',
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.baseClient[method](url, ...(data ? [data] : []), config)
      return response.data
    } catch (error) {
      if (error instanceof ApiServiceError) {
        throw error
      }
      throw new ApiServiceError('예상치 못한 오류가 발생했습니다', undefined, 'UNEXPECTED_ERROR', error)
    }
  }

  // 쿼리 파라미터 빌더
  private buildQueryParams(params: Record<string, any>): string {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value))
      }
    })
    return searchParams.toString()
  }

  // ===================
  // 서비스 관리 API
  // ===================

  /**
   * 모든 서비스 목록 조회
   */
  async getServices(): Promise<ServiceInfo[]> {
    const response = await this.request<ServiceInfo[]>('get', '/api/services')
    return validateArrayResponse(response, ServiceInfoSchema, '서비스 목록')
  }

  /**
   * 특정 서비스 정보 조회
   */
  async getService(serviceId: string): Promise<ServiceInfo> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    const response = await this.request<ServiceInfo>('get', `/api/services/${encodeURIComponent(serviceId)}`)
    return validateApiResponse(response, ServiceInfoSchema, '서비스 정보')
  }

  /**
   * 서비스 시작
   */
  async startService(serviceId: string): Promise<{ message: string; service: ServiceInfo }> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    return this.request<{ message: string; service: ServiceInfo }>(
      'post', 
      `/api/services/${encodeURIComponent(serviceId)}/start`
    )
  }

  /**
   * 서비스 중지
   */
  async stopService(serviceId: string): Promise<{ message: string; service: ServiceInfo }> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    return this.request<{ message: string; service: ServiceInfo }>(
      'post', 
      `/api/services/${encodeURIComponent(serviceId)}/stop`
    )
  }

  /**
   * 서비스 재시작
   */
  async restartService(serviceId: string): Promise<{ message: string; service: ServiceInfo }> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    return this.request<{ message: string; service: ServiceInfo }>(
      'post', 
      `/api/services/${encodeURIComponent(serviceId)}/restart`
    )
  }

  /**
   * 여러 서비스 일괄 제어
   */
  async controlServices(actions: ServiceAction[]): Promise<{ results: Array<{ service_id: string; success: boolean; message: string }> }> {
    if (!Array.isArray(actions) || actions.length === 0) {
      throw new ApiServiceError('서비스 액션 목록이 필요합니다', 400, 'INVALID_ACTIONS')
    }
    return this.request<{ results: Array<{ service_id: string; success: boolean; message: string }> }>(
      'post', 
      '/api/services/batch', 
      { actions }
    )
  }

  // ===================
  // 시스템 메트릭 API
  // ===================

  /**
   * 현재 시스템 메트릭 조회
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await this.metricsClient.get('/api/metrics')
    return validateApiResponse(response.data, SystemMetricsSchema, '시스템 메트릭')
  }

  /**
   * 성능 메트릭 조회
   */
  async getPerformanceMetrics(timeRange?: '1h' | '6h' | '24h' | '7d'): Promise<PerformanceMetrics> {
    const params = timeRange ? { time_range: timeRange } : {}
    const queryString = this.buildQueryParams(params)
    const response = await this.metricsClient.get(`/api/metrics/performance${queryString ? `?${queryString}` : ''}`)
    return validateApiResponse(response.data, PerformanceMetricsSchema, '성능 메트릭')
  }

  /**
   * 안정성 메트릭 조회
   */
  async getStabilityMetrics(): Promise<StabilityMetrics> {
    const response = await this.metricsClient.get('/api/metrics/stability')
    return validateApiResponse(response.data, StabilityMetricsSchema, '안정성 메트릭')
  }

  /**
   * 메트릭 히스토리 조회
   */
  async getMetricsHistory(params?: {
    limit?: number
    start_time?: string
    end_time?: string
    metrics?: string[]
  }): Promise<PaginatedResponse<SystemMetrics>> {
    const queryString = this.buildQueryParams(params || {})
    return this.request<PaginatedResponse<SystemMetrics>>('get', `/api/metrics/history${queryString ? `?${queryString}` : ''}`)
  }

  // ===================
  // 웹훅 API
  // ===================

  /**
   * 웹훅 전송
   */
  async sendWebhook(payload: WebhookPayload): Promise<{ message: string; webhook_id: string; status: 'success' | 'failed' }> {
    if (!payload.url?.trim()) {
      throw new ApiServiceError('웹훅 URL이 필요합니다', 400, 'INVALID_WEBHOOK_URL')
    }
    if (!payload.message?.trim()) {
      throw new ApiServiceError('메시지가 필요합니다', 400, 'INVALID_MESSAGE')
    }
    const response = await this.webhookClient.post('/api/webhook/send', payload)
    return response.data
  }

  /**
   * 웹훅 템플릿 목록 조회
   */
  async getWebhookTemplates(webhookType?: string): Promise<WebhookTemplate[]> {
    const params = webhookType ? { webhook_type: webhookType } : {}
    const queryString = this.buildQueryParams(params)
    const response = await this.request<WebhookTemplate[]>('get', `/api/webhook/templates${queryString ? `?${queryString}` : ''}`)
    return validateArrayResponse(response, WebhookTemplateSchema, '웹훅 템플릿 목록')
  }

  /**
   * 특정 웹훅 템플릿 조회
   */
  async getWebhookTemplate(templateId: string): Promise<WebhookTemplate> {
    if (!templateId?.trim()) {
      throw new ApiServiceError('템플릿 ID가 필요합니다', 400, 'INVALID_TEMPLATE_ID')
    }
    const response = await this.request<WebhookTemplate>('get', `/api/webhook/templates/${encodeURIComponent(templateId)}`)
    return validateApiResponse(response, WebhookTemplateSchema, '웹훅 템플릿')
  }

  /**
   * 웹훅 템플릿 생성
   */
  async createWebhookTemplate(template: Omit<WebhookTemplate, 'id' | 'created_at' | 'updated_at'>): Promise<WebhookTemplate> {
    if (!template.name?.trim()) {
      throw new ApiServiceError('템플릿 이름이 필요합니다', 400, 'INVALID_TEMPLATE_NAME')
    }
    if (!template.template?.trim()) {
      throw new ApiServiceError('템플릿 내용이 필요합니다', 400, 'INVALID_TEMPLATE_CONTENT')
    }
    return this.request<WebhookTemplate>('post', '/api/webhook/templates', template)
  }

  /**
   * 웹훅 템플릿 수정
   */
  async updateWebhookTemplate(
    templateId: string,
    template: Partial<Omit<WebhookTemplate, 'id' | 'created_at' | 'updated_at'>>
  ): Promise<WebhookTemplate> {
    if (!templateId?.trim()) {
      throw new ApiServiceError('템플릿 ID가 필요합니다', 400, 'INVALID_TEMPLATE_ID')
    }
    return this.request<WebhookTemplate>('put', `/api/webhook/templates/${encodeURIComponent(templateId)}`, template)
  }

  /**
   * 웹훅 템플릿 삭제
   */
  async deleteWebhookTemplate(templateId: string): Promise<{ message: string }> {
    if (!templateId?.trim()) {
      throw new ApiServiceError('템플릿 ID가 필요합니다', 400, 'INVALID_TEMPLATE_ID')
    }
    return this.request<{ message: string }>('delete', `/api/webhook/templates/${encodeURIComponent(templateId)}`)
  }

  /**
   * 웹훅 전송 히스토리 조회
   */
  async getWebhookHistory(params?: {
    limit?: number
    page?: number
    webhook_type?: string
    status?: 'success' | 'failed' | 'pending'
    start_date?: string
    end_date?: string
  }): Promise<WebhookHistory[]> {
    const queryString = this.buildQueryParams(params || {})
    return this.request<WebhookHistory[]>('get', `/api/webhook/history${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * 특정 웹훅 전송 상태 조회
   */
  async getWebhookStatus(webhookId: string): Promise<WebhookHistory> {
    if (!webhookId?.trim()) {
      throw new ApiServiceError('웹훅 ID가 필요합니다', 400, 'INVALID_WEBHOOK_ID')
    }
    return this.request<WebhookHistory>('get', `/api/webhook/history/${encodeURIComponent(webhookId)}`)
  }

  // ===================
  // 로그 API
  // ===================

  /**
   * 로그 조회
   */
  async getLogs(filter?: LogFilter & { limit?: number; page?: number }): Promise<PaginatedResponse<LogEntry>> {
    const queryString = this.buildQueryParams(filter || {})
    const response = await this.logsClient.get(`/api/logs${queryString ? `?${queryString}` : ''}`)
    return validatePaginatedResponse(response.data, LogEntrySchema, '로그 목록')
  }

  /**
   * 로그 내보내기 (POST 방식으로 로그 데이터 전송)
   */
  async exportLogs(exportRequest: {
    logs: LogEntry[]
    format: 'txt' | 'json' | 'csv'
    include_metadata?: boolean
    custom_filename?: string
  }): Promise<Blob> {
    const response = await this.logsClient.post('/api/logs/export', exportRequest, {
      responseType: 'blob'
    })
    return response.data
  }

  /**
   * 로그 보관 정책 조회
   */
  async getLogRetentionPolicy(): Promise<{
    max_days: number
    max_size_mb: number
    max_files: number
    compression_enabled: boolean
    auto_cleanup: boolean
    cleanup_schedule: string
    level_based_retention: Record<string, number>
  }> {
    const response = await this.logsClient.get('/api/logs/retention-policy')
    return response.data
  }

  /**
   * 로그 보관 정책 저장
   */
  async saveLogRetentionPolicy(policy: {
    max_days: number
    max_size_mb: number
    max_files: number
    compression_enabled: boolean
    auto_cleanup: boolean
    cleanup_schedule: string
    level_based_retention: Record<string, number>
  }): Promise<{ message: string }> {
    const response = await this.logsClient.post('/api/logs/retention-policy', policy)
    return response.data
  }

  /**
   * 로그 정리 실행
   */
  async cleanupLogs(): Promise<{
    deleted_files: string[]
    compressed_files: string[]
    total_space_freed: number
    total_space_freed_mb: number
  }> {
    const response = await this.logsClient.post('/api/logs/cleanup')
    return response.data
  }

  /**
   * 지원하는 내보내기 형식 목록 조회
   */
  async getLogExportFormats(): Promise<{
    formats: Array<{
      id: string
      name: string
      extension: string
      description: string
    }>
  }> {
    const response = await this.logsClient.get('/api/logs/export-formats')
    return response.data
  }

  // ===================
  // POSCO 시스템 API
  // ===================

  /**
   * POSCO 시스템 상태 조회
   */
  async getPoscoStatus(): Promise<{
    current_branch: string
    deployment_status: string
    last_deployment: string
    git_status: any
  }> {
    const response = await this.poscoClient.get('/api/posco/status')
    return response.data
  }

  /**
   * POSCO 브랜치 전환
   */
  async switchPoscoBranch(branch: string): Promise<{ message: string; current_branch: string }> {
    if (!branch?.trim()) {
      throw new ApiServiceError('브랜치 이름이 필요합니다', 400, 'INVALID_BRANCH_NAME')
    }
    const response = await this.poscoClient.post('/api/posco/branch-switch', { branch })
    return response.data
  }

  /**
   * POSCO 배포 실행
   */
  async deployPosco(options?: { force?: boolean; backup?: boolean }): Promise<{ message: string; deployment_id: string }> {
    const response = await this.poscoClient.post('/api/posco/deploy', options || {})
    return response.data
  }

  // ===================
  // 헬스 체크 및 유틸리티
  // ===================

  /**
   * 서비스 헬스 체크
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.request<HealthCheckResponse>('get', '/health')
    return validateApiResponse(response, HealthCheckResponseSchema, '헬스 체크')
  }

  /**
   * API 연결 테스트
   */
  async testConnection(): Promise<{ connected: boolean; latency: number; version: string }> {
    const startTime = Date.now()
    try {
      const response = await this.request<{ status: string; version: string }>('get', '/api/ping')
      const latency = Date.now() - startTime
      return {
        connected: true,
        latency,
        version: response.version
      }
    } catch (error) {
      return {
        connected: false,
        latency: Date.now() - startTime,
        version: 'unknown'
      }
    }
  }

  /**
   * 서버 정보 조회
   */
  async getServerInfo(): Promise<{
    version: string
    uptime: number
    environment: string
    features: string[]
  }> {
    return this.request<{
      version: string
      uptime: number
      environment: string
      features: string[]
    }>('get', '/api/info')
  }

  // ===================
  // 설정 관리 API
  // ===================

  /**
   * 애플리케이션 설정 조회
   */
  async getSettings(): Promise<any> {
    return this.request<any>('get', '/api/settings')
  }

  /**
   * 애플리케이션 설정 저장
   */
  async saveSettings(settings: any): Promise<{ message: string }> {
    return this.request<{ message: string }>('post', '/api/settings', settings)
  }

  /**
   * 애플리케이션 설정 초기화
   */
  async resetSettings(): Promise<{ message: string }> {
    return this.request<{ message: string }>('delete', '/api/settings')
  }

  /**
   * 웹훅 테스트
   */
  async testWebhook(payload: { url: string; message: string }): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('post', '/api/webhook/test', payload)
  }
}

// 싱글톤 인스턴스 생성
export const apiService = new ApiService()

// 기본 내보내기
export default apiService
