/**
 * Axios 인터셉터 확장 유틸리티
 * 요청/응답 처리, 로깅, 캐싱, 재시도 로직 등을 관리
 */

import { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { ApiServiceError } from './api'

// 요청 메타데이터 타입
interface RequestMetadata {
  startTime: number
  requestId: string
  retryCount: number
  cacheKey?: string
}

// 캐시 엔트리 타입
interface CacheEntry {
  data: any
  timestamp: number
  ttl: number
}

// 인터셉터 옵션 타입
interface InterceptorOptions {
  enableLogging?: boolean
  enableCaching?: boolean
  enableRetry?: boolean
  maxRetries?: number
  retryDelay?: number
  cacheTimeout?: number
}

/**
 * 고급 인터셉터 관리 클래스
 */
export class ApiInterceptorManager {
  private cache = new Map<string, CacheEntry>()
  private requestIdCounter = 0
  private options: Required<InterceptorOptions>

  constructor(
    private axiosInstance: AxiosInstance,
    options: InterceptorOptions = {}
  ) {
    this.options = {
      enableLogging: options.enableLogging ?? true,
      enableCaching: options.enableCaching ?? false,
      enableRetry: options.enableRetry ?? true,
      maxRetries: options.maxRetries ?? 3,
      retryDelay: options.retryDelay ?? 1000,
      cacheTimeout: options.cacheTimeout ?? 5 * 60 * 1000, // 5분
    }

    this.setupInterceptors()
    this.startCacheCleanup()
  }

  /**
   * 인터셉터 설정
   */
  private setupInterceptors() {
    // 요청 인터셉터
    this.axiosInstance.interceptors.request.use(
      this.handleRequest.bind(this),
      this.handleRequestError.bind(this)
    )

    // 응답 인터셉터
    this.axiosInstance.interceptors.response.use(
      this.handleResponse.bind(this),
      this.handleResponseError.bind(this)
    )
  }

  /**
   * 요청 처리
   */
  private handleRequest(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
    const requestId = `req_${++this.requestIdCounter}_${Date.now()}`
    const startTime = Date.now()

    // 메타데이터 추가
    config.metadata = {
      startTime,
      requestId,
      retryCount: 0,
    } as RequestMetadata

    // 캐시 키 생성
    if (this.options.enableCaching && config.method === 'get') {
      const cacheKey = this.generateCacheKey(config)
      config.metadata.cacheKey = cacheKey

      // 캐시된 응답 확인
      const cachedResponse = this.getCachedResponse(cacheKey)
      if (cachedResponse) {
        // 캐시된 응답을 Promise로 반환하기 위해 특별한 마커 추가
        config.headers = config.headers || {}
        config.headers['X-Cache-Hit'] = 'true'
      }
    }

    // 로깅
    if (this.options.enableLogging) {
      console.log(`🚀 [${requestId}] ${config.method?.toUpperCase()} ${config.url}`)
    }

    return config
  }

  /**
   * 요청 에러 처리
   */
  private handleRequestError(error: any): Promise<never> {
    if (this.options.enableLogging) {
      console.error('❌ 요청 설정 오류:', error)
    }
    return Promise.reject(new ApiServiceError(
      '요청 설정 중 오류가 발생했습니다',
      undefined,
      'REQUEST_CONFIG_ERROR',
      error
    ))
  }

  /**
   * 응답 처리
   */
  private handleResponse(response: AxiosResponse): AxiosResponse {
    const metadata = response.config.metadata as RequestMetadata
    const duration = Date.now() - metadata.startTime

    // 캐시 저장
    if (this.options.enableCaching && metadata.cacheKey && response.config.method === 'get') {
      this.setCachedResponse(metadata.cacheKey, response.data)
    }

    // 로깅
    if (this.options.enableLogging) {
      const cacheHit = response.config.headers?.['X-Cache-Hit'] === 'true'
      console.log(
        `✅ [${metadata.requestId}] ${response.status} ${response.config.url} (${duration}ms)${cacheHit ? ' [CACHED]' : ''}`
      )
    }

    return response
  }

  /**
   * 응답 에러 처리 (재시도 로직 포함)
   */
  private async handleResponseError(error: AxiosError): Promise<any> {
    const config = error.config as AxiosRequestConfig & { metadata?: RequestMetadata }
    const metadata = config?.metadata

    if (metadata) {
      const duration = Date.now() - metadata.startTime
      
      if (this.options.enableLogging) {
        console.error(
          `❌ [${metadata.requestId}] ${error.response?.status || 'Network Error'} ${config?.url} (${duration}ms)`
        )
      }

      // 재시도 로직
      if (this.options.enableRetry && this.shouldRetry(error, metadata)) {
        return this.retryRequest(config, metadata)
      }
    }

    // 에러 변환 및 전파
    throw this.transformError(error)
  }

  /**
   * 재시도 여부 결정
   */
  private shouldRetry(error: AxiosError, metadata: RequestMetadata): boolean {
    if (metadata.retryCount >= this.options.maxRetries) {
      return false
    }

    // 네트워크 에러
    if (!error.response) {
      return true
    }

    // 재시도 가능한 HTTP 상태 코드
    const retryableStatusCodes = [408, 429, 500, 502, 503, 504]
    return retryableStatusCodes.includes(error.response.status)
  }

  /**
   * 요청 재시도
   */
  private async retryRequest(config: AxiosRequestConfig, metadata: RequestMetadata): Promise<any> {
    metadata.retryCount++
    
    const backoffDelay = this.calculateBackoffDelay(metadata.retryCount)
    
    if (this.options.enableLogging) {
      console.log(
        `🔄 [${metadata.requestId}] 재시도 ${metadata.retryCount}/${this.options.maxRetries} (${backoffDelay}ms 후)`
      )
    }

    await this.delay(backoffDelay)
    
    // 새로운 요청 ID 생성
    metadata.requestId = `${metadata.requestId}_retry_${metadata.retryCount}`
    metadata.startTime = Date.now()

    return this.axiosInstance(config)
  }

  /**
   * 지수 백오프 지연 계산
   */
  private calculateBackoffDelay(attempt: number): number {
    const baseDelay = this.options.retryDelay
    const jitter = Math.random() * 1000
    return baseDelay * Math.pow(2, attempt - 1) + jitter
  }

  /**
   * 지연 함수
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * 에러 변환
   */
  private transformError(error: AxiosError): ApiServiceError {
    let message = '알 수 없는 오류가 발생했습니다'
    let code = 'UNKNOWN_ERROR'

    if (!error.response) {
      message = '네트워크 연결을 확인해주세요'
      code = 'NETWORK_ERROR'
    } else {
      const status = error.response.status
      const data = error.response.data as any

      switch (status) {
        case 400:
          message = data?.detail || '잘못된 요청입니다'
          code = 'BAD_REQUEST'
          break
        case 401:
          message = '인증이 필요합니다'
          code = 'UNAUTHORIZED'
          break
        case 403:
          message = '접근 권한이 없습니다'
          code = 'FORBIDDEN'
          break
        case 404:
          message = '요청한 리소스를 찾을 수 없습니다'
          code = 'NOT_FOUND'
          break
        case 422:
          message = data?.detail || '입력 데이터가 올바르지 않습니다'
          code = 'VALIDATION_ERROR'
          break
        case 429:
          message = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요'
          code = 'RATE_LIMITED'
          break
        case 500:
          message = '서버 내부 오류가 발생했습니다'
          code = 'INTERNAL_SERVER_ERROR'
          break
        default:
          message = `서버 오류가 발생했습니다 (${status})`
          code = `HTTP_${status}`
      }
    }

    return new ApiServiceError(message, error.response?.status, code, error.response?.data)
  }

  /**
   * 캐시 키 생성
   */
  private generateCacheKey(config: AxiosRequestConfig): string {
    const url = config.url || ''
    const params = JSON.stringify(config.params || {})
    const headers = JSON.stringify(config.headers || {})
    return `${config.method}:${url}:${params}:${headers}`
  }

  /**
   * 캐시된 응답 조회
   */
  private getCachedResponse(cacheKey: string): any | null {
    const entry = this.cache.get(cacheKey)
    
    if (!entry) {
      return null
    }

    const now = Date.now()
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(cacheKey)
      return null
    }

    return entry.data
  }

  /**
   * 응답 캐시 저장
   */
  private setCachedResponse(cacheKey: string, data: any): void {
    const entry: CacheEntry = {
      data,
      timestamp: Date.now(),
      ttl: this.options.cacheTimeout,
    }
    
    this.cache.set(cacheKey, entry)
  }

  /**
   * 캐시 정리 작업 시작
   */
  private startCacheCleanup(): void {
    setInterval(() => {
      const now = Date.now()
      
      for (const [key, entry] of this.cache.entries()) {
        if (now - entry.timestamp > entry.ttl) {
          this.cache.delete(key)
        }
      }
    }, 60 * 1000) // 1분마다 정리
  }

  /**
   * 캐시 수동 정리
   */
  public clearCache(pattern?: string): void {
    if (!pattern) {
      this.cache.clear()
      return
    }

    const regex = new RegExp(pattern)
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * 캐시 통계 조회
   */
  public getCacheStats(): {
    size: number
    keys: string[]
    hitRate?: number
  } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    }
  }

  /**
   * 인터셉터 옵션 업데이트
   */
  public updateOptions(newOptions: Partial<InterceptorOptions>): void {
    this.options = { ...this.options, ...newOptions }
  }
}

// 타입 확장
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: RequestMetadata
  }
}