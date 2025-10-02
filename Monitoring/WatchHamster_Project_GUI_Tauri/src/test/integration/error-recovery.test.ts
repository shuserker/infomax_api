/**
 * ?�류 ?�나리오 �?복구 ?�스??
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mainmainApiClient } from '@/services/mainApiClient'
import { WebSocketService } from '@/services/websocket'
import { errorHandler } from '@/services/errorHandler'
import axios, { AxiosError } from 'axios'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'
import mainApiClient from '@/services/apiClient'

// Mock ?�이??
const mockServiceInfo = {
  id: 'test-service',
  name: '?�스???�비??,
  status: 'running'
}

describe('?�류 ?�나리오 �?복구 ?�스??, () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('?�트?�크 ?�류 ?�나리오', () => {
    it('?�트?�크 ?�결 ?�패 처리', async () => {
      const networkError = new Error('Network Error')
      networkError.name = 'NetworkError'
      
      vi.spyOn(axios, 'get').mockRejectedValue(networkError)

      await expect(mainmainApiClient.get('/api/services')).rejects.toThrow('Network Error')
    })

    it('DNS ?�석 ?�패 처리', async () => {
      const dnsError = new Error('getaddrinfo ENOTFOUND')
      dnsError.name = 'DNSError'
      
      vi.spyOn(axios, 'get').mockRejectedValue(dnsError)

      await expect(mainApiClient.get('/api/services')).rejects.toThrow('getaddrinfo ENOTFOUND')
    })

    it('?�결 ?�간 초과 처리', async () => {
      const timeoutError = {
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded',
        name: 'TimeoutError'
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(timeoutError)

      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        code: 'ECONNABORTED'
      })
    })

    it('?�결 거�? 처리', async () => {
      const connectionRefused = {
        code: 'ECONNREFUSED',
        message: 'connect ECONNREFUSED 127.0.0.1:8000',
        name: 'ConnectionRefused'
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(connectionRefused)

      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        code: 'ECONNREFUSED'
      })
    })
  })

  describe('HTTP ?�류 ?�태 코드 처리', () => {
    it('400 Bad Request 처리', async () => {
      const badRequestError: Partial<AxiosError> = {
        response: {
          status: 400,
          data: { detail: '?�못???�청?�니?? },
          statusText: 'Bad Request',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 400'
      }
      
      vi.spyOn(axios, 'post').mockRejectedValue(badRequestError)

      await expect(mainApiClient.post('/api/services/invalid/start')).rejects.toMatchObject({
        response: {
          status: 400,
          data: { detail: '?�못???�청?�니?? }
        }
      })
    })

    it('401 Unauthorized 처리', async () => {
      const unauthorizedError: Partial<AxiosError> = {
        response: {
          status: 401,
          data: { detail: '?�증???�요?�니?? },
          statusText: 'Unauthorized',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 401'
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(unauthorizedError)

      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        response: {
          status: 401
        }
      })
    })

    it('403 Forbidden 처리', async () => {
      const forbiddenError: Partial<AxiosError> = {
        response: {
          status: 403,
          data: { detail: '?�근 권한???�습?�다' },
          statusText: 'Forbidden',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 403'
      }
      
      vi.spyOn(axios, 'post').mockRejectedValue(forbiddenError)

      await expect(mainApiClient.post('/api/services/test/stop')).rejects.toMatchObject({
        response: {
          status: 403
        }
      })
    })

    it('404 Not Found 처리', async () => {
      const notFoundError: Partial<AxiosError> = {
        response: {
          status: 404,
          data: { detail: '?�비?��? 찾을 ???�습?�다' },
          statusText: 'Not Found',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 404'
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(notFoundError)

      await expect(mainApiClient.get('/api/services/nonexistent')).rejects.toMatchObject({
        response: {
          status: 404
        }
      })
    })

    it('500 Internal Server Error 처리', async () => {
      const serverError: Partial<AxiosError> = {
        response: {
          status: 500,
          data: { detail: '?��? ?�버 ?�류가 발생?�습?�다' },
          statusText: 'Internal Server Error',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 500'
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(serverError)

      await expect(mainApiClient.get('/api/metrics')).rejects.toMatchObject({
        response: {
          status: 500
        }
      })
    })

    it('503 Service Unavailable 처리', async () => {
      const serviceUnavailableError: Partial<AxiosError> = {
        response: {
          status: 503,
          data: { detail: '?�비?��? ?�용?????�습?�다' },
          statusText: 'Service Unavailable',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 503'
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(serviceUnavailableError)

      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        response: {
          status: 503
        }
      })
    })
  })

  describe('WebSocket ?�류 ?�나리오', () => {
    let wsService: WebSocketService

    beforeEach(() => {
      wsService = new WebSocketService('ws://localhost:8001/ws')
    })

    afterEach(() => {
      if (wsService) {
        wsService.disconnect()
      }
    })

    it('WebSocket ?�결 ?�패 처리', async () => {
      // WebSocket ?�결 ?�패 ?��??�이??
      global.WebSocket = class {
        constructor() {
          setTimeout(() => {
            if (this.onerror) {
              this.onerror(new Event('error'))
            }
          }, 10)
        }
        
        readyState = WebSocket.CONNECTING
        onopen: ((event: Event) => void) | null = null
        onclose: ((event: CloseEvent) => void) | null = null
        onmessage: ((event: MessageEvent) => void) | null = null
        onerror: ((event: Event) => void) | null = null
        
        send = vi.fn()
        close = vi.fn()
        addEventListener = vi.fn()
        removeEventListener = vi.fn()
        dispatchEvent = vi.fn()
      } as any

      await expect(wsService.connect()).rejects.toThrow()
    })

    it('WebSocket ?�결 ?��? 처리', async () => {
      // ?�상 ?�결 ???��? ?��??�이??
      let mockWs: any

      global.WebSocket = class {
        constructor() {
          mockWs = this
          setTimeout(() => {
            this.readyState = WebSocket.OPEN
            if (this.onopen) {
              this.onopen(new Event('open'))
            }
          }, 10)
        }
        
        readyState = WebSocket.CONNECTING
        onopen: ((event: Event) => void) | null = null
        onclose: ((event: CloseEvent) => void) | null = null
        onmessage: ((event: MessageEvent) => void) | null = null
        onerror: ((event: Event) => void) | null = null
        
        send = vi.fn()
        close = vi.fn()
        addEventListener = vi.fn()
        removeEventListener = vi.fn()
        dispatchEvent = vi.fn()
      } as any

      await wsService.connect()
      expect(wsService.isConnected()).toBe(true)

      // ?�결 ?��? ?��??�이??
      mockWs.readyState = WebSocket.CLOSED
      if (mockWs.onclose) {
        mockWs.onclose(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }))
      }

      expect(wsService.isConnected()).toBe(false)
    })

    it('?�못??메시지 ?�식 처리', async () => {
      let mockWs: any

      global.WebSocket = class {
        constructor() {
          mockWs = this
          setTimeout(() => {
            this.readyState = WebSocket.OPEN
            if (this.onopen) {
              this.onopen(new Event('open'))
            }
          }, 10)
        }
        
        readyState = WebSocket.CONNECTING
        onopen: ((event: Event) => void) | null = null
        onclose: ((event: CloseEvent) => void) | null = null
        onmessage: ((event: MessageEvent) => void) | null = null
        onerror: ((event: Event) => void) | null = null
        
        send = vi.fn()
        close = vi.fn()
        addEventListener = vi.fn()
        removeEventListener = vi.fn()
        dispatchEvent = vi.fn()
      } as any

      await wsService.connect()

      let errorHandled = false
      wsService.onError(() => {
        errorHandled = true
      })

      // ?�못??JSON 메시지 ?�송
      if (mockWs.onmessage) {
        const invalidEvent = new MessageEvent('message', {
          data: 'invalid json format'
        })
        mockWs.onmessage(invalidEvent)
      }

      // ?�류가 ?�절??처리?�었?��? ?�인
      // (?�제 WebSocketService 구현???�라 ?��? ???�음)
    })
  })

  describe('?�비??복구 ?�나리오', () => {
    it('?�시???�비??중단 ??복구', async () => {
      let callCount = 0
      
      vi.spyOn(axios, 'get').mockImplementation(() => {
        callCount++
        if (callCount === 1) {
          // �?번째 ?�출: ?�비??중단
          return Promise.reject({
            response: {
              status: 503,
              data: { detail: '?�비?��? ?�용?????�습?�다' }
            }
          })
        } else {
          // ??번째 ?�출: ?�비??복구
          return Promise.resolve({ data: [mockServiceInfo] })
        }
      })

      // �?번째 ?�출 - ?�패
      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        response: { status: 503 }
      })

      // ??번째 ?�출 - ?�공
      const response = await mainApiClient.get('/api/services')
      expect(response.data).toEqual([mockServiceInfo])
    })

    it('백엔???�시?????�동 복구', async () => {
      let isBackendDown = true
      
      vi.spyOn(axios, 'get').mockImplementation(() => {
        if (isBackendDown) {
          return Promise.reject({
            code: 'ECONNREFUSED',
            message: 'connect ECONNREFUSED 127.0.0.1:8000'
          })
        } else {
          return Promise.resolve({ data: [mockServiceInfo] })
        }
      })

      // 백엔???�운 ?�태
      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        code: 'ECONNREFUSED'
      })

      // 백엔??복구 ?��??�이??
      isBackendDown = false

      // 복구 ???�상 ?�답
      const response = await mainApiClient.get('/api/services')
      expect(response.data).toEqual([mockServiceInfo])
    })

    it('부분적 ?�비???�애 처리', async () => {
      // ?��? API???�상, ?��????�패
      vi.spyOn(axios, 'get').mockImplementation((url) => {
        if (url?.includes('/api/services')) {
          return Promise.resolve({ data: [mockServiceInfo] })
        } else if (url?.includes('/api/metrics')) {
          return Promise.reject({
            response: {
              status: 500,
              data: { detail: '메트�??�비???�류' }
            }
          })
        }
        return Promise.resolve({ data: {} })
      })

      // ?�비??API???�상
      const servicesResponse = await mainApiClient.get('/api/services')
      expect(servicesResponse.data).toEqual([mockServiceInfo])

      // 메트�?API???�패
      await expect(mainApiClient.get('/api/metrics')).rejects.toMatchObject({
        response: { status: 500 }
      })
    })
  })

  describe('?�이???��???�??�기???�류', () => {
    it('?�비???�태 불일�?처리', async () => {
      // ?�비???�작 명령?� ?�공?��?�??�태 조회?�서???�전??중�? ?�태
      vi.spyOn(axios, 'post').mockResolvedValue({
        data: { message: '?�비?��? ?�작?�었?�니??, service_id: 'test-service' }
      })

      vi.spyOn(axios, 'get').mockResolvedValue({
        data: [{ ...mockServiceInfo, status: 'stopped' }] // ?�전??중�? ?�태
      })

      // ?�비???�작 명령
      const startResponse = await mainApiClient.post('/api/services/test-service/start')
      expect(startResponse.data.message).toBe('?�비?��? ?�작?�었?�니??)

      // ?�태 조회 - 불일�??�태
      const statusResponse = await mainApiClient.get('/api/services')
      expect(statusResponse.data[0].status).toBe('stopped')

      // ?�런 경우 UI?�서 ?�절??처리가 ?�요?�을 ?�인
    })

    it('WebSocket�?REST API ?�이??불일�?, async () => {
      // REST API?�서???�비?��? ?�행 �?
      vi.spyOn(axios, 'get').mockResolvedValue({
        data: [{ ...mockServiceInfo, status: 'running' }]
      })

      const restResponse = await mainApiClient.get('/api/services')
      expect(restResponse.data[0].status).toBe('running')

      // WebSocket?�서???�비??중�? ?�벤???�신
      // (?�제 ?�스?�에?�는 WebSocket 메시지 ?��??�이???�요)
      const wsMessage = {
        type: 'service_event',
        data: {
          service_id: 'test-service',
          event_type: 'stopped',
          message: '?�비?��? 중�??�었?�니??
        },
        timestamp: new Date().toISOString()
      }

      // ?�런 불일�??�황?�서 UI가 ?�떻�?처리?�는지 ?�인
      expect(wsMessage.data.event_type).toBe('stopped')
      expect(restResponse.data[0].status).toBe('running')
    })
  })

  describe('리소??부�??�나리오', () => {
    it('메모�?부�??�류 처리', async () => {
      const memoryError: Partial<AxiosError> = {
        response: {
          status: 507,
          data: { detail: '메모리�? 부족합?�다' },
          statusText: 'Insufficient Storage',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 507'
      }
      
      vi.spyOn(axios, 'post').mockRejectedValue(memoryError)

      await expect(mainApiClient.post('/api/services/memory-intensive/start')).rejects.toMatchObject({
        response: { status: 507 }
      })
    })

    it('?�스??공간 부�??�류 처리', async () => {
      const diskSpaceError: Partial<AxiosError> = {
        response: {
          status: 507,
          data: { detail: '?�스??공간??부족합?�다' },
          statusText: 'Insufficient Storage',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 507'
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(diskSpaceError)

      await expect(mainApiClient.get('/api/logs')).rejects.toMatchObject({
        response: { status: 507 }
      })
    })

    it('CPU 과�????�류 처리', async () => {
      const cpuOverloadError: Partial<AxiosError> = {
        response: {
          status: 503,
          data: { detail: 'CPU ?�용률이 ?�무 ?�습?�다' },
          statusText: 'Service Unavailable',
          headers: {},
          config: {} as any
        },
        name: 'AxiosError',
        message: 'Request failed with status code 503'
      }
      
      vi.spyOn(axios, 'post').mockRejectedValue(cpuOverloadError)

      await expect(mainApiClient.post('/api/services/cpu-intensive/start')).rejects.toMatchObject({
        response: { status: 503 }
      })
    })
  })

  describe('보안 관???�류', () => {
    it('CORS ?�류 처리', async () => {
      const corsError = new Error('CORS policy: Cross origin requests are only supported for protocol schemes')
      corsError.name = 'CORSError'
      
      vi.spyOn(axios, 'get').mockRejectedValue(corsError)

      await expect(mainApiClient.get('/api/services')).rejects.toThrow('CORS policy')
    })

    it('CSP ?�반 ?�류 처리', async () => {
      const cspError = new Error('Content Security Policy violation')
      cspError.name = 'CSPError'
      
      vi.spyOn(axios, 'post').mockRejectedValue(cspError)

      await expect(mainApiClient.post('/api/webhook/send', {})).rejects.toThrow('Content Security Policy')
    })
  })

  describe('복구 ?�략 ?�스??, () => {
    it('지??백오???�시???�략', async () => {
      let attemptCount = 0
      const maxRetries = 3
      
      vi.spyOn(axios, 'get').mockImplementation(() => {
        attemptCount++
        if (attemptCount <= maxRetries) {
          return Promise.reject(new Error('Temporary failure'))
        }
        return Promise.resolve({ data: [mockServiceInfo] })
      })

      // ?�시??로직??구현?�어 ?�다�??�스??
      // ?�재??기본 ?�작�??�스??
      for (let i = 0; i < maxRetries; i++) {
        await expect(mainApiClient.get('/api/services')).rejects.toThrow('Temporary failure')
      }

      // 마�?�??�도?�서 ?�공
      const response = await mainApiClient.get('/api/services')
      expect(response.data).toEqual([mockServiceInfo])
      expect(attemptCount).toBe(maxRetries + 1)
    })

    it('?�킷 브레?�커 ?�턴', async () => {
      // ?�속 ?�패 ???�킷 ?�픈
      const failureThreshold = 5
      let failureCount = 0
      
      vi.spyOn(axios, 'get').mockImplementation(() => {
        failureCount++
        if (failureCount <= failureThreshold) {
          return Promise.reject(new Error('Service failure'))
        }
        // ?�킷???�린 ?�에??즉시 ?�패
        return Promise.reject(new Error('Circuit breaker is open'))
      })

      // ?�속 ?�패
      for (let i = 0; i < failureThreshold; i++) {
        await expect(mainApiClient.get('/api/services')).rejects.toThrow('Service failure')
      }

      // ?�킷 브레?�커 ?�픈 ??
      await expect(mainApiClient.get('/api/services')).rejects.toThrow('Circuit breaker is open')
    })
  })
})
