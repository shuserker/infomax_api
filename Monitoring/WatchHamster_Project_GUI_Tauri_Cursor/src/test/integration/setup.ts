/**
 * 통합 테스트 설정
 */

import { beforeAll, afterAll, vi } from 'vitest'

// 통합 테스트용 환경 변수 설정
export const TEST_CONFIG = {
  API_BASE_URL: 'http://localhost:8001',
  WS_URL: 'ws://localhost:8001/ws',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

// Mock 서버 상태
let mockServerRunning = false

// 통합 테스트 전역 설정
export const setupIntegrationTests = () => {
  beforeAll(async () => {
    // 테스트 환경 초기화
    console.log('🚀 통합 테스트 환경 초기화 중...')
    
    // 환경 변수 설정
    process.env.VITE_API_BASE_URL = TEST_CONFIG.API_BASE_URL
    process.env.VITE_WS_URL = TEST_CONFIG.WS_URL
    
    // Mock 서버 시작 (실제 환경에서는 테스트 서버 시작)
    mockServerRunning = true
    console.log('✅ Mock 서버 시작됨')
    
    // 전역 fetch Mock 설정
    global.fetch = vi.fn()
    
    console.log('✅ 통합 테스트 환경 준비 완료')
  })

  afterAll(async () => {
    // 테스트 환경 정리
    console.log('🧹 통합 테스트 환경 정리 중...')
    
    if (mockServerRunning) {
      mockServerRunning = false
      console.log('✅ Mock 서버 중지됨')
    }
    
    // Mock 정리
    vi.restoreAllMocks()
    
    console.log('✅ 통합 테스트 환경 정리 완료')
  })
}

// 테스트용 유틸리티 함수들
export const testUtils = {
  // 비동기 대기 유틸리티
  wait: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),
  
  // Mock 응답 생성기
  createMockResponse: (data: any, status = 200) => ({
    data,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: {},
    config: {} as any
  }),
  
  // Mock 오류 생성기
  createMockError: (status: number, message: string) => ({
    response: {
      status,
      data: { detail: message },
      statusText: status === 500 ? 'Internal Server Error' : 'Error',
      headers: {},
      config: {} as any
    },
    name: 'AxiosError',
    message: `Request failed with status code ${status}`
  }),
  
  // WebSocket Mock 생성기
  createMockWebSocket: () => {
    return class MockWebSocket {
      url: string
      readyState: number = WebSocket.CONNECTING
      onopen: ((event: Event) => void) | null = null
      onclose: ((event: CloseEvent) => void) | null = null
      onmessage: ((event: MessageEvent) => void) | null = null
      onerror: ((event: Event) => void) | null = null

      static CONNECTING = 0
      static OPEN = 1
      static CLOSING = 2
      static CLOSED = 3

      constructor(url: string) {
        this.url = url
        setTimeout(() => {
          this.readyState = WebSocket.OPEN
          if (this.onopen) {
            this.onopen(new Event('open'))
          }
        }, 10)
      }

      send = vi.fn()
      close = vi.fn(() => {
        this.readyState = WebSocket.CLOSED
        if (this.onclose) {
          this.onclose(new CloseEvent('close'))
        }
      })
      addEventListener = vi.fn()
      removeEventListener = vi.fn()
      dispatchEvent = vi.fn()

      // 테스트용 메서드
      simulateMessage(data: any) {
        if (this.onmessage) {
          const event = new MessageEvent('message', {
            data: JSON.stringify(data)
          })
          this.onmessage(event)
        }
      }

      simulateError() {
        if (this.onerror) {
          this.onerror(new Event('error'))
        }
      }

      simulateClose(code = 1000, reason = 'Normal closure') {
        this.readyState = WebSocket.CLOSED
        if (this.onclose) {
          const event = new CloseEvent('close', { code, reason })
          this.onclose(event)
        }
      }
    }
  }
}

// 테스트 데이터 팩토리
export const testDataFactory = {
  createServiceInfo: (overrides = {}) => ({
    id: 'test-service',
    name: '테스트 서비스',
    description: '테스트용 서비스입니다',
    status: 'running' as const,
    uptime: 3600,
    last_error: null,
    config: {},
    ...overrides
  }),

  createSystemMetrics: (overrides = {}) => ({
    cpu_percent: 45.2,
    memory_percent: 67.8,
    disk_usage: 23.4,
    network_status: 'connected' as const,
    uptime: 86400,
    active_services: 5,
    ...overrides
  }),

  createWebhookPayload: (overrides = {}) => ({
    url: 'https://discord.com/api/webhooks/test',
    message: '테스트 메시지',
    type: 'discord' as const,
    ...overrides
  }),

  createWSMessage: (type: string, data: any, overrides = {}) => ({
    type,
    data,
    timestamp: new Date().toISOString(),
    ...overrides
  }),

  createServiceEvent: (overrides = {}) => ({
    service_id: 'test-service',
    event_type: 'started' as const,
    message: '서비스가 시작되었습니다',
    details: {},
    ...overrides
  }),

  createLogEntry: (overrides = {}) => ({
    timestamp: new Date().toISOString(),
    level: 'INFO' as const,
    message: '테스트 로그 메시지',
    service_id: 'test-service',
    ...overrides
  })
}

// 성능 측정 유틸리티
export const performanceUtils = {
  measureExecutionTime: async <T>(fn: () => Promise<T>): Promise<{ result: T; duration: number }> => {
    const startTime = performance.now()
    const result = await fn()
    const endTime = performance.now()
    const duration = endTime - startTime
    
    return { result, duration }
  },

  measureMemoryUsage: () => {
    if (typeof performance !== 'undefined' && 'memory' in performance) {
      return (performance as any).memory
    }
    return null
  }
}

// 테스트 환경 검증
export const validateTestEnvironment = () => {
  const requiredGlobals = ['WebSocket', 'fetch', 'localStorage', 'sessionStorage']
  const missing = requiredGlobals.filter(global => !(global in globalThis))
  
  if (missing.length > 0) {
    throw new Error(`테스트 환경에 필요한 전역 객체가 없습니다: ${missing.join(', ')}`)
  }
  
  console.log('✅ 테스트 환경 검증 완료')
}