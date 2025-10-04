/**
 * API 통합 테스트
 * Python 백엔드와 React 프론트엔드 간 통신 테스트
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest'
import axios from 'axios'
import { mainApiClient } from '@/services/apiClient'
import { WebSocketService } from '@/services/websocket'
import type { ServiceInfo, SystemMetrics, WebhookPayload } from '@/types'

// 테스트용 백엔드 서버 설정
const TEST_BASE_URL = 'http://localhost:8001'
const TEST_WS_URL = 'ws://localhost:8001/ws'

// Mock 서버 응답 데이터
const mockServiceInfo: ServiceInfo = {
  id: 'posco-news',
  name: 'POSCO 뉴스 모니터',
  description: 'POSCO 뉴스 시스템 모니터링',
  status: 'running',
  uptime: 3600,
  last_error: null,
  config: {}
}

const mockSystemMetrics: SystemMetrics = {
  cpu_percent: 45.2,
  memory_percent: 67.8,
  disk_usage: 23.4,
  network_status: 'connected',
  uptime: 86400,
  active_services: 5
}

describe('API 통합 테스트', () => {
  let mockServer: any
  let wsService: WebSocketService

  beforeAll(async () => {
    // 테스트용 Mock 서버 설정
    mockServer = {
      isRunning: false,
      start: vi.fn().mockResolvedValue(true),
      stop: vi.fn().mockResolvedValue(true)
    }

    // API 클라이언트 기본 URL 설정
    mainApiClient.defaults.baseURL = TEST_BASE_URL
  })

  afterAll(async () => {
    if (mockServer?.isRunning) {
      await mockServer.stop()
    }
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('서비스 관리 API 통합 테스트', () => {
    it('서비스 목록 조회 API 통합 테스트', async () => {
      // Mock 응답 설정
      const mockResponse = [mockServiceInfo]
      vi.spyOn(axios, 'get').mockResolvedValue({ data: mockResponse })

      // API 호출
      const response = await mainApiClient.get('/api/services')

      // 검증
      expect(response.data).toEqual(mockResponse)
      expect(response.data[0]).toMatchObject({
        id: expect.any(String),
        name: expect.any(String),
        status: expect.stringMatching(/^(running|stopped|error|starting|stopping)$/)
      })
    })

    it('서비스 시작 API 통합 테스트', async () => {
      const serviceId = 'posco-news'
      const mockResponse = { message: '서비스가 시작되었습니다', service_id: serviceId }
      
      vi.spyOn(axios, 'post').mockResolvedValue({ data: mockResponse })

      const response = await mainApiClient.post(`/api/services/${serviceId}/start`)

      expect(response.data).toEqual(mockResponse)
      expect(axios.post).toHaveBeenCalledWith(`/api/services/${serviceId}/start`)
    })

    it('서비스 중지 API 통합 테스트', async () => {
      const serviceId = 'posco-news'
      const mockResponse = { message: '서비스가 중지되었습니다', service_id: serviceId }
      
      vi.spyOn(axios, 'post').mockResolvedValue({ data: mockResponse })

      const response = await mainApiClient.post(`/api/services/${serviceId}/stop`)

      expect(response.data).toEqual(mockResponse)
      expect(axios.post).toHaveBeenCalledWith(`/api/services/${serviceId}/stop`)
    })

    it('서비스 재시작 API 통합 테스트', async () => {
      const serviceId = 'posco-news'
      const mockResponse = { message: '서비스가 재시작되었습니다', service_id: serviceId }
      
      vi.spyOn(axios, 'post').mockResolvedValue({ data: mockResponse })

      const response = await mainApiClient.post(`/api/services/${serviceId}/restart`)

      expect(response.data).toEqual(mockResponse)
      expect(axios.post).toHaveBeenCalledWith(`/api/services/${serviceId}/restart`)
    })
  })

  describe('시스템 메트릭 API 통합 테스트', () => {
    it('시스템 메트릭 조회 API 통합 테스트', async () => {
      vi.spyOn(axios, 'get').mockResolvedValue({ data: mockSystemMetrics })

      const response = await mainApiClient.get('/api/metrics')

      expect(response.data).toEqual(mockSystemMetrics)
      expect(response.data).toMatchObject({
        cpu_percent: expect.any(Number),
        memory_percent: expect.any(Number),
        disk_usage: expect.any(Number),
        network_status: expect.any(String),
        uptime: expect.any(Number),
        active_services: expect.any(Number)
      })
    })

    it('성능 메트릭 조회 API 통합 테스트', async () => {
      const mockPerformanceMetrics = {
        cpu_history: [40, 45, 50, 45, 42],
        memory_history: [60, 65, 70, 68, 67],
        timestamp: Date.now()
      }

      vi.spyOn(axios, 'get').mockResolvedValue({ data: mockPerformanceMetrics })

      const response = await mainApiClient.get('/api/metrics/performance')

      expect(response.data).toEqual(mockPerformanceMetrics)
      expect(response.data.cpu_history).toBeInstanceOf(Array)
      expect(response.data.memory_history).toBeInstanceOf(Array)
    })
  })

  describe('웹훅 API 통합 테스트', () => {
    it('웹훅 전송 API 통합 테스트', async () => {
      const webhookPayload: WebhookPayload = {
        url: 'https://discord.com/api/webhooks/test',
        message: '테스트 메시지',
        type: 'discord'
      }

      const mockResponse = { 
        success: true, 
        message: '웹훅이 성공적으로 전송되었습니다',
        webhook_id: 'webhook_123'
      }

      vi.spyOn(axios, 'post').mockResolvedValue({ data: mockResponse })

      const response = await mainApiClient.post('/api/webhook/send', webhookPayload)

      expect(response.data).toEqual(mockResponse)
      expect(axios.post).toHaveBeenCalledWith('/api/webhook/send', webhookPayload)
    })

    it('메시지 템플릿 조회 API 통합 테스트', async () => {
      const mockTemplates = [
        { id: 'alert', name: '알림 템플릿', content: '{{message}}' },
        { id: 'status', name: '상태 템플릿', content: '시스템 상태: {{status}}' }
      ]

      vi.spyOn(axios, 'get').mockResolvedValue({ data: mockTemplates })

      const response = await mainApiClient.get('/api/webhook/templates')

      expect(response.data).toEqual(mockTemplates)
      expect(response.data).toBeInstanceOf(Array)
      expect(response.data[0]).toMatchObject({
        id: expect.any(String),
        name: expect.any(String),
        content: expect.any(String)
      })
    })
  })

  describe('로그 API 통합 테스트', () => {
    it('로그 조회 API 통합 테스트', async () => {
      const mockLogs = {
        logs: [
          { timestamp: '2024-01-01T10:00:00Z', level: 'INFO', message: '시스템 시작' },
          { timestamp: '2024-01-01T10:01:00Z', level: 'DEBUG', message: '디버그 메시지' }
        ],
        total: 2,
        page: 1,
        per_page: 50
      }

      vi.spyOn(axios, 'get').mockResolvedValue({ data: mockLogs })

      const response = await mainApiClient.get('/api/logs?page=1&per_page=50')

      expect(response.data).toEqual(mockLogs)
      expect(response.data.logs).toBeInstanceOf(Array)
      expect(response.data.logs[0]).toMatchObject({
        timestamp: expect.any(String),
        level: expect.any(String),
        message: expect.any(String)
      })
    })
  })

  describe('POSCO 시스템 API 통합 테스트', () => {
    it('POSCO 시스템 상태 조회 API 통합 테스트', async () => {
      const mockPoscoStatus = {
        current_branch: 'main',
        deployment_status: 'deployed',
        last_deployment: '2024-01-01T10:00:00Z',
        git_status: 'clean'
      }

      vi.spyOn(axios, 'get').mockResolvedValue({ data: mockPoscoStatus })

      const response = await mainApiClient.get('/api/posco/status')

      expect(response.data).toEqual(mockPoscoStatus)
      expect(response.data).toMatchObject({
        current_branch: expect.any(String),
        deployment_status: expect.any(String),
        git_status: expect.any(String)
      })
    })

    it('POSCO 배포 실행 API 통합 테스트', async () => {
      const deployPayload = { branch: 'main', force: false }
      const mockResponse = { 
        success: true, 
        message: '배포가 시작되었습니다',
        deployment_id: 'deploy_123'
      }

      vi.spyOn(axios, 'post').mockResolvedValue({ data: mockResponse })

      const response = await mainApiClient.post('/api/posco/deploy', deployPayload)

      expect(response.data).toEqual(mockResponse)
      expect(axios.post).toHaveBeenCalledWith('/api/posco/deploy', deployPayload)
    })
  })

  describe('오류 시나리오 테스트', () => {
    it('네트워크 오류 처리 테스트', async () => {
      const networkError = new Error('Network Error')
      vi.spyOn(axios, 'get').mockRejectedValue(networkError)

      await expect(mainApiClient.get('/api/services')).rejects.toThrow('Network Error')
    })

    it('서버 오류 응답 처리 테스트', async () => {
      const serverError = {
        response: {
          status: 500,
          data: { detail: '내부 서버 오류' }
        }
      }
      vi.spyOn(axios, 'get').mockRejectedValue(serverError)

      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        response: {
          status: 500,
          data: { detail: '내부 서버 오류' }
        }
      })
    })

    it('인증 오류 처리 테스트', async () => {
      const authError = {
        response: {
          status: 401,
          data: { detail: '인증이 필요합니다' }
        }
      }
      vi.spyOn(axios, 'post').mockRejectedValue(authError)

      await expect(mainApiClient.post('/api/services/test/start')).rejects.toMatchObject({
        response: {
          status: 401
        }
      })
    })

    it('타임아웃 오류 처리 테스트', async () => {
      const timeoutError = {
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded'
      }
      vi.spyOn(axios, 'get').mockRejectedValue(timeoutError)

      await expect(mainApiClient.get('/api/metrics')).rejects.toMatchObject({
        code: 'ECONNABORTED'
      })
    })
  })

  describe('API 재시도 및 복구 테스트', () => {
    it('일시적 오류 후 재시도 성공 테스트', async () => {
      let callCount = 0
      vi.spyOn(axios, 'get').mockImplementation(() => {
        callCount++
        if (callCount === 1) {
          return Promise.reject(new Error('Temporary Error'))
        }
        return Promise.resolve({ data: mockSystemMetrics })
      })

      // 재시도 로직이 있다면 여기서 테스트
      // 현재는 기본 axios 동작만 테스트
      await expect(mainApiClient.get('/api/metrics')).rejects.toThrow('Temporary Error')
      
      // 두 번째 호출은 성공
      const response = await mainApiClient.get('/api/metrics')
      expect(response.data).toEqual(mockSystemMetrics)
    })
  })
})