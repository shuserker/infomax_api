/**
 * API 클라이언트 팩토리
 * 다양한 설정으로 API 클라이언트를 생성하고 관리
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { ApiInterceptorManager } from './interceptors'

// API 클라이언트 설정 타입
export interface ApiClientConfig {
  baseURL?: string
  timeout?: number
  headers?: Record<string, string>
  enableLogging?: boolean
  enableCaching?: boolean
  enableRetry?: boolean
  maxRetries?: number
  retryDelay?: number
  cacheTimeout?: number
}

// 기본 설정
const DEFAULT_CONFIG: Required<ApiClientConfig> = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:9001',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  enableLogging: import.meta.env.DEV,
  enableCaching: false,
  enableRetry: true,
  maxRetries: 3,
  retryDelay: 1000,
  cacheTimeout: 5 * 60 * 1000, // 5분
}

/**
 * API 클라이언트 팩토리 클래스
 */
export class ApiClientFactory {
  private static instances = new Map<string, AxiosInstance>()
  private static interceptorManagers = new Map<string, ApiInterceptorManager>()

  /**
   * API 클라이언트 생성 또는 기존 인스턴스 반환
   */
  static create(name: string = 'default', config: ApiClientConfig = {}): AxiosInstance {
    // 기존 인스턴스가 있으면 반환
    if (this.instances.has(name)) {
      return this.instances.get(name)!
    }

    // 설정 병합
    const finalConfig = { ...DEFAULT_CONFIG, ...config }

    // Axios 인스턴스 생성
    const axiosConfig: AxiosRequestConfig = {
      baseURL: finalConfig.baseURL,
      timeout: finalConfig.timeout,
      headers: finalConfig.headers,
    }

    const instance = axios.create(axiosConfig)

    // 인터셉터 매니저 설정
    const interceptorManager = new ApiInterceptorManager(instance, {
      enableLogging: finalConfig.enableLogging,
      enableCaching: finalConfig.enableCaching,
      enableRetry: finalConfig.enableRetry,
      maxRetries: finalConfig.maxRetries,
      retryDelay: finalConfig.retryDelay,
      cacheTimeout: finalConfig.cacheTimeout,
    })

    // 인스턴스 저장
    this.instances.set(name, instance)
    this.interceptorManagers.set(name, interceptorManager)

    return instance
  }

  /**
   * 특정 API 클라이언트 제거
   */
  static remove(name: string): boolean {
    const removed = this.instances.delete(name)
    this.interceptorManagers.delete(name)
    return removed
  }

  /**
   * 모든 API 클라이언트 제거
   */
  static clear(): void {
    this.instances.clear()
    this.interceptorManagers.clear()
  }

  /**
   * 인터셉터 매니저 조회
   */
  static getInterceptorManager(name: string = 'default'): ApiInterceptorManager | undefined {
    return this.interceptorManagers.get(name)
  }

  /**
   * 캐시 정리
   */
  static clearCache(name?: string, pattern?: string): void {
    if (name) {
      const manager = this.interceptorManagers.get(name)
      manager?.clearCache(pattern)
    } else {
      // 모든 인스턴스의 캐시 정리
      for (const manager of this.interceptorManagers.values()) {
        manager.clearCache(pattern)
      }
    }
  }

  /**
   * 등록된 클라이언트 목록 조회
   */
  static getClientNames(): string[] {
    return Array.from(this.instances.keys())
  }

  /**
   * 클라이언트 상태 조회
   */
  static getClientStats(name: string = 'default'): {
    exists: boolean
    cacheStats?: ReturnType<ApiInterceptorManager['getCacheStats']>
  } {
    const exists = this.instances.has(name)
    const manager = this.interceptorManagers.get(name)
    
    return {
      exists,
      cacheStats: manager?.getCacheStats(),
    }
  }
}

/**
 * 사전 정의된 API 클라이언트들
 */

// 기본 API 클라이언트 (캐싱 비활성화)
export const mainApiClient = ApiClientFactory.create('main', {
  enableCaching: false,
  enableRetry: true,
  maxRetries: 3,
})

// 메트릭 전용 API 클라이언트 (캐싱 활성화, 짧은 타임아웃)
export const metricsApiClient = ApiClientFactory.create('metrics', {
  timeout: 5000,
  enableCaching: true,
  cacheTimeout: 30 * 1000, // 30초
  enableRetry: true,
  maxRetries: 2,
})

// 로그 전용 API 클라이언트 (긴 타임아웃, 재시도 최소화)
export const logsApiClient = ApiClientFactory.create('logs', {
  timeout: 30000, // 30초
  enableCaching: false,
  enableRetry: false,
})

// 웹훅 전용 API 클라이언트 (재시도 강화)
export const webhookApiClient = ApiClientFactory.create('webhook', {
  timeout: 15000,
  enableCaching: false,
  enableRetry: true,
  maxRetries: 5,
  retryDelay: 2000,
})

// POSCO 시스템 전용 API 클라이언트 (긴 타임아웃)
export const poscoApiClient = ApiClientFactory.create('posco', {
  timeout: 60000, // 1분
  enableCaching: false,
  enableRetry: true,
  maxRetries: 2,
})

/**
 * 환경별 설정 적용
 */
export const applyEnvironmentConfig = () => {
  const isDev = import.meta.env.DEV
  const isProd = import.meta.env.PROD

  if (isDev) {
    // 개발 환경: 로깅 활성화, 캐시 비활성화
    ApiClientFactory.create('dev', {
      enableLogging: true,
      enableCaching: false,
      timeout: 30000,
    })
  }

  if (isProd) {
    // 프로덕션 환경: 로깅 비활성화, 캐시 활성화
    ApiClientFactory.create('prod', {
      enableLogging: false,
      enableCaching: true,
      timeout: 10000,
    })
  }
}

/**
 * 클라이언트 헬스 체크
 */
export const performHealthCheck = async (clientName: string = 'main'): Promise<{
  healthy: boolean
  latency?: number
  error?: string
}> => {
  const client = ApiClientFactory.create(clientName)
  const startTime = Date.now()

  try {
    await client.get('/health', { timeout: 5000 })
    const latency = Date.now() - startTime
    
    return {
      healthy: true,
      latency,
    }
  } catch (error) {
    return {
      healthy: false,
      latency: Date.now() - startTime,
      error: error instanceof Error ? error.message : '알 수 없는 오류',
    }
  }
}

/**
 * 모든 클라이언트 헬스 체크
 */
export const performAllHealthChecks = async (): Promise<Record<string, {
  healthy: boolean
  latency?: number
  error?: string
}>> => {
  const clientNames = ApiClientFactory.getClientNames()
  const results: Record<string, any> = {}

  await Promise.all(
    clientNames.map(async (name) => {
      results[name] = await performHealthCheck(name)
    })
  )

  return results
}

// 초기화 시 환경 설정 적용
applyEnvironmentConfig()

// 기본 내보내기
export default mainApiClient