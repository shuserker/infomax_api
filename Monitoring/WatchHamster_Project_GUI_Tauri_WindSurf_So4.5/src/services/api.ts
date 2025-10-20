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

// API 클라이언트 팩토리에서 클라이언트 가져오기
import { mainApiClient, metricsApiClient, logsApiClient, webhookApiClient, poscoApiClient } from './apiClient'

// 기본 API 클라이언트
const apiClient = mainApiClient

// 타입 정의 및 검증 스키마
import type {
  ServiceInfo,
  SystemMetrics,
  PerformanceMetrics,
  StabilityMetrics,
  WebhookTemplate,
  WebhookHistory,
  LogEntry,
  ServiceAction,
  HealthCheckResponse,
  NewsStatus,
  NewsHistory,
  AppSettings
} from '../types'

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
  // 시스템 제어 API
  // ===================

  /**
   * 전체 시스템 시작
   */
  async startSystem(): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>('post', '/api/system/start')
  }

  /**
   * 전체 시스템 중지
   */
  async stopSystem(): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>('post', '/api/system/stop')
  }

  /**
   * 전체 시스템 재시작
   */
  async restartSystem(): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>('post', '/api/system/restart')
  }

  /**
   * 시스템 상태 조회
   */
  async getSystemStatus(): Promise<{
    overall_status: string
    services_running: number
    services_total: number
    uptime: number
    last_check: string
    components: Record<string, string>
    metrics?: any
  }> {
    return this.request<{
      overall_status: string
      services_running: number
      services_total: number
      uptime: number
      last_check: string
      components: Record<string, string>
      metrics?: any
    }>('get', '/api/system/status')
  }

  // ===================
  // 서비스 관리 API
  // ===================

  /**
   * 모든 서비스 목록 조회
   */
  async getServices(): Promise<ServiceInfo[]> {
    const response = await this.request<any[]>('get', '/api/services/')
    return response as ServiceInfo[]
  }

  /**
   * 특정 서비스 정보 조회
   */
  async getService(serviceId: string): Promise<ServiceInfo> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    const response = await this.request<any>('get', `/api/services/${encodeURIComponent(serviceId)}`)
    return response as ServiceInfo
  }

  /**
   * 서비스 시작
   */
  async startService(serviceId: string): Promise<{ message: string; service_id: string }> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    return this.request<{ message: string; service_id: string }>(
      'post', 
      `/api/services/${encodeURIComponent(serviceId)}/start`
    )
  }

  /**
   * 서비스 중지
   */
  async stopService(serviceId: string): Promise<{ message: string; service_id: string }> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    return this.request<{ message: string; service_id: string }>(
      'post', 
      `/api/services/${encodeURIComponent(serviceId)}/stop`
    )
  }

  /**
   * 서비스 재시작
   */
  async restartService(serviceId: string): Promise<{ message: string; service_id: string }> {
    if (!serviceId?.trim()) {
      throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
    }
    return this.request<{ message: string; service_id: string }>(
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
  // 뉴스 모니터링 API
  // ===================

  /**
   * 뉴스 상태 조회
   */
  async getNewsStatus(newsType?: string): Promise<NewsStatus | NewsStatus[]> {
    const params = newsType ? { news_type: newsType } : {}
    const queryString = this.buildQueryParams(params)
    return this.request<NewsStatus | NewsStatus[]>('get', `/api/news/status${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * 뉴스 데이터 수동 갱신
   */
  async refreshNewsData(newsTypes?: string[], force: boolean = false): Promise<{ message: string; news_types: string[]; force: boolean }> {
    const payload = {
      news_types: newsTypes,
      force
    }
    return this.request<{ message: string; news_types: string[]; force: boolean }>('post', '/api/news/refresh', payload)
  }

  /**
   * 뉴스 이력 조회
   */
  async getNewsHistory(params?: {
    news_type?: string
    limit?: number
    offset?: number
  }): Promise<{
    items: NewsHistory[]
    total_count: number
    offset: number
    limit: number
    has_more: boolean
  }> {
    const queryString = this.buildQueryParams(params || {})
    return this.request<{
      items: NewsHistory[]
      total_count: number
      offset: number
      limit: number
      has_more: boolean
    }>('get', `/api/news/history${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * 뉴스 이력 정리
   */
  async clearNewsHistory(newsType?: string): Promise<{ message: string; deleted_count: number }> {
    const params = newsType ? { news_type: newsType } : {}
    const queryString = this.buildQueryParams(params)
    return this.request<{ message: string; deleted_count: number }>('delete', `/api/news/history${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * 뉴스 상태 요약 정보
   */
  async getNewsSummary(): Promise<{
    overall_status: string
    total_news_types: number
    latest_count: number
    delayed_count: number
    error_count: number
    most_recent_update: string | null
    history_count: number
  }> {
    return this.request<{
      overall_status: string
      total_news_types: number
      latest_count: number
      delayed_count: number
      error_count: number
      most_recent_update: string | null
      history_count: number
    }>('get', '/api/news/summary')
  }

  // ===================
  // 시스템 메트릭 API
  // ===================

  /**
   * 현재 시스템 메트릭 조회
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await this.metricsClient.get('/api/metrics/')
    return response.data as SystemMetrics
  }

  /**
   * 성능 메트릭 조회
   */
  async getPerformanceMetrics(timeRange?: '1h' | '6h' | '24h' | '7d'): Promise<PerformanceMetrics> {
    const params = timeRange ? { time_range: timeRange } : {}
    const queryString = this.buildQueryParams(params)
    const response = await this.metricsClient.get(`/api/metrics/performance${queryString ? `?${queryString}` : ''}`)
    return response.data as PerformanceMetrics
  }

  /**
   * 안정성 메트릭 조회
   */
  async getStabilityMetrics(): Promise<StabilityMetrics> {
    const response = await this.metricsClient.get('/api/metrics/stability')
    return response.data as StabilityMetrics
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
  async sendWebhook(payload: { url: string; message: string; webhook_type?: string; template_id?: string; variables?: Record<string, any> }): Promise<{ message: string; webhook_id: string; status: 'success' | 'failed' }> {
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
    const response = await this.request<any[]>('get', `/api/webhook/templates${queryString ? `?${queryString}` : ''}`)
    return response as WebhookTemplate[]
  }

  /**
   * 특정 웹훅 템플릿 조회
   */
  async getWebhookTemplate(templateId: string): Promise<WebhookTemplate> {
    if (!templateId?.trim()) {
      throw new ApiServiceError('템플릿 ID가 필요합니다', 400, 'INVALID_TEMPLATE_ID')
    }
    const response = await this.request<any>('get', `/api/webhook/templates/${encodeURIComponent(templateId)}`)
    return response as WebhookTemplate
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
   * 로그 조회 (페이지네이션 지원)
   */
  async getLogs(params: {
    page?: string
    limit?: string
    levels?: string
    sources?: string
    search?: string
    start_time?: string
    end_time?: string
    file_name?: string
  } = {}): Promise<{ logs: LogEntry[]; total: number; hasMore: boolean }> {
    const queryString = this.buildQueryParams(params)
    const response = await this.request<{ logs: LogEntry[]; total: number; hasMore: boolean }>(
      'get', 
      `/api/logs${queryString ? `?${queryString}` : ''}`
    )
    
    // 로그 엔트리는 그대로 반환
    
    return response
  }

  /**
   * 로그 내보내기
   */
  async exportLogs(exportRequest: {
    logs: LogEntry[]
    format: 'txt' | 'json' | 'csv'
    include_metadata?: boolean
    custom_filename?: string
  }): Promise<Blob> {
    const response = await this.baseClient.post('/api/logs/export', exportRequest, {
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
    return this.request<{
      max_days: number
      max_size_mb: number
      max_files: number
      compression_enabled: boolean
      auto_cleanup: boolean
      cleanup_schedule: string
      level_based_retention: Record<string, number>
    }>('get', '/api/logs/retention-policy')
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
    return this.request<{ message: string }>('post', '/api/logs/retention-policy', policy)
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
    return this.request<{
      deleted_files: string[]
      compressed_files: string[]
      total_space_freed: number
      total_space_freed_mb: number
    }>('post', '/api/logs/cleanup')
  }

  /**
   * 지원하는 로그 내보내기 형식 목록
   */
  async getLogExportFormats(): Promise<{
    formats: Array<{
      id: string
      name: string
      extension: string
      description: string
    }>
  }> {
    return this.request<{
      formats: Array<{
        id: string
        name: string
        extension: string
        description: string
      }>
    }>('get', '/api/logs/export-formats')
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
    const response = await this.request<any>('get', '/health')
    return response as HealthCheckResponse
  }

  /**
   * API 연결 테스트
   */
  async testConnection(): Promise<{ connected: boolean; latency: number; version: string }> {
    const startTime = Date.now()
    try {
      const response = await this.request<{ status: string; service?: string; version?: string }>('get', '/health')
      const latency = Date.now() - startTime
      return {
        connected: response.status === 'healthy',
        latency,
        version: response.version || '1.0.0'
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
  async getSettings(sections?: string[], includeSensitive: boolean = false): Promise<{
    settings: AppSettings
    last_updated: string
    version: string
  }> {
    const params: Record<string, any> = {}
    if (sections && sections.length > 0) {
      params.sections = sections.join(',')
    }
    if (includeSensitive) {
      params.include_sensitive = true
    }
    
    const queryString = this.buildQueryParams(params)
    return this.request<{
      settings: AppSettings
      last_updated: string
      version: string
    }>('get', `/api/settings${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * 애플리케이션 설정 업데이트
   */
  async updateSettings(
    settings: Partial<AppSettings>,
    reason?: string,
    validateOnly: boolean = false
  ): Promise<{
    settings: AppSettings
    validation_result: {
      valid: boolean
      errors: Array<{ field_path: string; message: string; severity: string }>
      warnings: Array<{ field_path: string; message: string }>
    }
    applied_changes: Array<{
      id: string
      field_path: string
      old_value: any
      new_value: any
      changed_by: string
      changed_at: string
      reason?: string
      auto_applied: boolean
    }>
    restart_required: boolean
  }> {
    const payload = {
      settings,
      reason,
      validate_only: validateOnly
    }
    
    return this.request<{
      settings: AppSettings
      validation_result: {
        valid: boolean
        errors: Array<{ field_path: string; message: string; severity: string }>
        warnings: Array<{ field_path: string; message: string }>
      }
      applied_changes: Array<{
        id: string
        field_path: string
        old_value: any
        new_value: any
        changed_by: string
        changed_at: string
        reason?: string
        auto_applied: boolean
      }>
      restart_required: boolean
    }>('put', '/api/settings', payload)
  }

  /**
   * 설정 유효성 검증
   */
  async validateSettings(): Promise<{
    valid: boolean
    errors: Array<{ field_path: string; message: string; severity: string }>
    warnings: Array<{ field_path: string; message: string }>
  }> {
    return this.request<{
      valid: boolean
      errors: Array<{ field_path: string; message: string; severity: string }>
      warnings: Array<{ field_path: string; message: string }>
    }>('get', '/api/settings/validate')
  }

  /**
   * 설정 초기화
   */
  async resetSettings(sections?: string[], confirm: boolean = true): Promise<{
    reset_sections: string[]
    backup_id: string
    restart_required: boolean
  }> {
    const payload = {
      sections,
      confirm
    }
    
    return this.request<{
      reset_sections: string[]
      backup_id: string
      restart_required: boolean
    }>('post', '/api/settings/reset', payload)
  }

  /**
   * 설정 내보내기
   */
  async exportSettings(
    sections?: string[],
    includeSensitive: boolean = false,
    format: 'json' | 'yaml' = 'json'
  ): Promise<{
    export_data: {
      version: string
      exported_at: string
      exported_by: string
      settings: Partial<AppSettings>
      metadata: {
        app_version: string
        platform: string
        hostname: string
      }
    }
    download_url: string
    expires_at: string
  }> {
    const payload = {
      sections,
      include_sensitive: includeSensitive,
      format
    }
    
    return this.request<{
      export_data: {
        version: string
        exported_at: string
        exported_by: string
        settings: Partial<AppSettings>
        metadata: {
          app_version: string
          platform: string
          hostname: string
        }
      }
      download_url: string
      expires_at: string
    }>('post', '/api/settings/export', payload)
  }

  /**
   * 내보내기 파일 다운로드
   */
  async downloadExportFile(filename: string): Promise<Blob> {
    if (!filename?.trim()) {
      throw new ApiServiceError('파일명이 필요합니다', 400, 'INVALID_FILENAME')
    }
    
    const response = await this.baseClient.get(`/api/settings/download/${encodeURIComponent(filename)}`, {
      responseType: 'blob'
    })
    
    return response.data
  }

  /**
   * 설정 가져오기
   */
  async importSettings(
    file: File,
    options: {
      merge?: boolean
      validate?: boolean
      backup_before_import?: boolean
      sections?: string[]
    } = {}
  ): Promise<{
    result: {
      success: boolean
      imported_sections: string[]
      skipped_sections: string[]
      errors: string[]
      warnings: string[]
      backup_id?: string
    }
    restart_required: boolean
  }> {
    const formData = new FormData()
    formData.append('file', file)
    
    // 옵션을 쿼리 파라미터로 전달
    const params: Record<string, any> = {
      merge: options.merge ?? true,
      validate: options.validate ?? true,
      backup_before_import: options.backup_before_import ?? true
    }
    
    if (options.sections && options.sections.length > 0) {
      params.sections = options.sections.join(',')
    }
    
    const queryString = this.buildQueryParams(params)
    
    const response = await this.baseClient.post(
      `/api/settings/import${queryString ? `?${queryString}` : ''}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    return response.data
  }

  /**
   * 설정 백업 목록 조회
   */
  async getSettingsBackups(): Promise<{
    backups: Array<{
      filename: string
      path: string
      type: 'regular_backup' | 'import_backup' | 'corrupted_backup'
      size: number
      created_at: string
      modified_at: string
    }>
    total_count: number
  }> {
    return this.request<{
      backups: Array<{
        filename: string
        path: string
        type: 'regular_backup' | 'import_backup' | 'corrupted_backup'
        size: number
        created_at: string
        modified_at: string
      }>
      total_count: number
    }>('get', '/api/settings/backups')
  }

  /**
   * 백업 파일 다운로드
   */
  async downloadBackupFile(filename: string): Promise<Blob> {
    if (!filename?.trim()) {
      throw new ApiServiceError('파일명이 필요합니다', 400, 'INVALID_FILENAME')
    }
    
    const response = await this.baseClient.get(`/api/settings/backups/${encodeURIComponent(filename)}`, {
      responseType: 'blob'
    })
    
    return response.data
  }

  /**
   * 백업에서 설정 복원
   */
  async restoreFromBackup(filename: string): Promise<{
    message: string
    backup_filename: string
  }> {
    if (!filename?.trim()) {
      throw new ApiServiceError('파일명이 필요합니다', 400, 'INVALID_FILENAME')
    }
    
    return this.request<{
      message: string
      backup_filename: string
    }>('post', `/api/settings/backups/${encodeURIComponent(filename)}/restore`)
  }

  /**
   * 설정 파일 정보 조회
   */
  async getSettingsInfo(): Promise<{
    settings_file: string
    exists: boolean
    size: number
    last_modified?: string
    backup_count: number
    is_valid: boolean
  }> {
    return this.request<{
      settings_file: string
      exists: boolean
      size: number
      last_modified?: string
      backup_count: number
      is_valid: boolean
    }>('get', '/api/settings/info')
  }

  /**
   * 오래된 백업 파일 정리
   */
  async cleanupOldBackups(
    maxBackups: number = 50,
    maxAgeDays: number = 90
  ): Promise<{
    message: string
    max_backups: number
    max_age_days: number
  }> {
    const params = {
      max_backups: maxBackups,
      max_age_days: maxAgeDays
    }
    
    return this.request<{
      message: string
      max_backups: number
      max_age_days: number
    }>('post', '/api/settings/cleanup', params)
  }

  /**
   * 웹훅 테스트
   */
  async testWebhook(payload: { url: string; message: string }): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('post', '/api/webhook/test', payload)
  }

  // ===================
  // 로그 관리 API (확장)
  // ===================

  /**
   * 로그 파일 목록 조회
   */
  async getLogFiles(): Promise<Array<{
    name: string
    path: string
    size: number
    modified_time: string
    is_active: boolean
  }>> {
    return this.request<Array<{
      name: string
      path: string
      size: number
      modified_time: string
      is_active: boolean
    }>>('get', '/api/logs/files')
  }

  /**
   * 로그 검색
   */
  async searchLogs(params: {
    query: string
    file_name?: string
    limit?: number
    case_sensitive?: boolean
  }): Promise<{
    query: string
    file_name: string
    total_matches: number
    logs: LogEntry[]
  }> {
    const queryString = this.buildQueryParams(params)
    const response = await this.request<{
      query: string
      file_name: string
      total_matches: number
      logs: LogEntry[]
    }>('get', `/api/logs/search?${queryString}`)
    
    // 로그 엔트리는 그대로 반환
    
    return response
  }

  /**
   * 로그 통계 조회
   */
  async getLogStatistics(params: {
    file_name?: string
    hours?: number
  } = {}): Promise<{
    total_logs: number
    level_counts: Record<string, number>
    hourly_counts: Record<string, number>
    top_loggers: Record<string, number>
    error_messages: Array<{
      timestamp: string
      level: string
      message: string
    }>
  }> {
    const queryString = this.buildQueryParams(params)
    return this.request<{
      total_logs: number
      level_counts: Record<string, number>
      hourly_counts: Record<string, number>
      top_loggers: Record<string, number>
      error_messages: Array<{
        timestamp: string
        level: string
        message: string
      }>
    }>('get', `/api/logs/statistics${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * 로그 파일 다운로드
   */
  async downloadLogFile(fileName: string): Promise<Blob> {
    if (!fileName?.trim()) {
      throw new ApiServiceError('파일명이 필요합니다', 400, 'INVALID_FILE_NAME')
    }
    
    const response = await this.baseClient.get(`/api/logs/download/${encodeURIComponent(fileName)}`, {
      responseType: 'blob'
    })
    
    return response.data
  }

  /**
   * 로그 파일 내용 삭제
   */
  async clearLogFile(fileName: string): Promise<{ message: string }> {
    if (!fileName?.trim()) {
      throw new ApiServiceError('파일명이 필요합니다', 400, 'INVALID_FILE_NAME')
    }
    
    return this.request<{ message: string }>('delete', `/api/logs/${encodeURIComponent(fileName)}`)
  }
}

// 싱글톤 인스턴스 생성
export const apiService = new ApiService()

// 기본 내보내기
export default apiService
