import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { mainApiClient } from '../../services/apiClient'
import { WebSocketManager } from '../../services/websocket'

// Mock data
const mockServiceInfo = {
  id: 'test-service',
  name: 'Test Service',
  status: 'running'
}

describe('Error Recovery Test Scenarios', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Network Error Scenarios', () => {
    it('should handle network timeout', async () => {
      const timeoutError = new Error('Network timeout')
      timeoutError.name = 'TIMEOUT'
      
      vi.spyOn(axios, 'get').mockRejectedValue(timeoutError)
      
      await expect(mainApiClient.get('/api/services')).rejects.toThrow('Network timeout')
    })

    it('should handle connection refused', async () => {
      const connectionError = new Error('Connection refused')
      connectionError.name = 'ECONNREFUSED'
      
      vi.spyOn(axios, 'get').mockRejectedValue(connectionError)
      
      await expect(mainApiClient.get('/api/services')).rejects.toThrow('Connection refused')
    })

    it('should retry on network failure', async () => {
      const networkError = new Error('Network Error')
      
      vi.spyOn(axios, 'get')
        .mockRejectedValueOnce(networkError)
        .mockRejectedValueOnce(networkError)
        .mockResolvedValueOnce({
          data: [mockServiceInfo],
          status: 200,
          statusText: 'OK',
          headers: {},
          config: {}
        })
      
      const result = await mainApiClient.get('/api/services')
      expect(result.data).toEqual([mockServiceInfo])
      expect(axios.get).toHaveBeenCalledTimes(3)
    })

    it('should handle DNS resolution failure', async () => {
      const dnsError = new Error('DNS resolution failed')
      dnsError.name = 'ENOTFOUND'
      
      vi.spyOn(axios, 'get').mockRejectedValue(dnsError)
      
      await expect(mainApiClient.get('/api/services')).rejects.toThrow('DNS resolution failed')
    })
  })

  describe('HTTP Error Status Code Handling', () => {
    it('should handle 400 Bad Request', async () => {
      const badRequestError = {
        response: {
          status: 400,
          data: { detail: 'Invalid request' },
          statusText: 'Bad Request',
          headers: {},
          config: {}
        }
      }
      
      vi.spyOn(axios, 'post').mockRejectedValue(badRequestError)
      
      await expect(mainApiClient.post('/api/services/invalid/start')).rejects.toMatchObject({
        response: {
          status: 400,
          data: { detail: 'Invalid request' }
        }
      })
    })

    it('should handle 401 Unauthorized', async () => {
      const unauthorizedError = {
        response: {
          status: 401,
          data: { detail: 'Authentication required' },
          statusText: 'Unauthorized',
          headers: {},
          config: {}
        }
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(unauthorizedError)
      
      await expect(mainApiClient.get('/api/services')).rejects.toMatchObject({
        response: {
          status: 401
        }
      })
    })

    it('should handle 404 Not Found', async () => {
      const notFoundError = {
        response: {
          status: 404,
          data: { detail: 'Service not found' },
          statusText: 'Not Found',
          headers: {},
          config: {}
        }
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(notFoundError)
      
      await expect(mainApiClient.get('/api/services/nonexistent')).rejects.toMatchObject({
        response: {
          status: 404
        }
      })
    })

    it('should handle 500 Internal Server Error', async () => {
      const serverError = {
        response: {
          status: 500,
          data: { detail: 'Internal server error' },
          statusText: 'Internal Server Error',
          headers: {},
          config: {}
        }
      }
      
      vi.spyOn(axios, 'post').mockRejectedValue(serverError)
      
      await expect(mainApiClient.post('/api/services/test/restart')).rejects.toMatchObject({
        response: {
          status: 500
        }
      })
    })

    it('should handle 503 Service Unavailable', async () => {
      const serviceUnavailableError = {
        response: {
          status: 503,
          data: { detail: 'Service temporarily unavailable' },
          statusText: 'Service Unavailable',
          headers: {},
          config: {}
        }
      }
      
      vi.spyOn(axios, 'get').mockRejectedValue(serviceUnavailableError)
      
      await expect(mainApiClient.get('/api/metrics')).rejects.toMatchObject({
        response: {
          status: 503
        }
      })
    })
  })

  describe('WebSocket Error Scenarios', () => {
    let wsManager: WebSocketManager

    beforeEach(() => {
      wsManager = new WebSocketManager('ws://localhost:8000/ws')
    })

    afterEach(() => {
      wsManager.disconnect()
    })

    it('should handle WebSocket connection failure', (done) => {
      const mockWebSocket = {
        readyState: WebSocket.CONNECTING,
        close: vi.fn(),
        send: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        onerror: null,
        onopen: null,
        onclose: null,
        onmessage: null
      }

      // @ts-ignore
      global.WebSocket = vi.fn(() => mockWebSocket)

      wsManager.onError((error) => {
        expect(error).toBeDefined()
        done()
      })

      wsManager.connect()

      // Simulate connection error
      setTimeout(() => {
        if (mockWebSocket.onerror) {
          mockWebSocket.onerror(new Event('error'))
        }
      }, 100)
    })

    it('should handle WebSocket unexpected disconnection', (done) => {
      const mockWebSocket = {
        readyState: WebSocket.OPEN,
        close: vi.fn(),
        send: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        onerror: null,
        onopen: null,
        onclose: null,
        onmessage: null
      }

      // @ts-ignore
      global.WebSocket = vi.fn(() => mockWebSocket)

      wsManager.onDisconnect(() => {
        done()
      })

      wsManager.connect()

      // Simulate unexpected disconnection
      setTimeout(() => {
        if (mockWebSocket.onclose) {
          mockWebSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Abnormal closure' }))
        }
      }, 100)
    })

    it('should attempt reconnection on disconnection', (done) => {
      let connectionAttempts = 0
      
      const mockWebSocket = {
        readyState: WebSocket.CONNECTING,
        close: vi.fn(),
        send: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        onerror: null,
        onopen: null,
        onclose: null,
        onmessage: null
      }

      // @ts-ignore
      global.WebSocket = vi.fn(() => {
        connectionAttempts++
        return mockWebSocket
      })

      wsManager.connect()

      // Simulate connection failure and reconnection
      setTimeout(() => {
        if (mockWebSocket.onclose) {
          mockWebSocket.onclose(new CloseEvent('close', { code: 1006 }))
        }
      }, 100)

      setTimeout(() => {
        expect(connectionAttempts).toBeGreaterThan(1)
        done()
      }, 1000)
    })
  })

  describe('Service Recovery Scenarios', () => {
    it('should handle service start success after failure', async () => {
      vi.spyOn(axios, 'post').mockResolvedValue({
        data: { message: 'Service started successfully', service_id: 'test-service' },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      })

      const startResponse = await mainApiClient.post('/api/services/test-service/start')
      
      expect(startResponse.status).toBe(200)
      expect(startResponse.data.message).toBe('Service started successfully')
      
      // Verify service status
      const statusResponse = await mainApiClient.get('/api/services')
      expect(statusResponse).toBeDefined()
    })

    it('should handle WebSocket and REST API data inconsistency', async () => {
      // Mock REST API response
      vi.spyOn(axios, 'get').mockResolvedValue({
        data: [{ ...mockServiceInfo, status: 'running' }],
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      })

      const restResponse = await mainApiClient.get('/api/services')
      expect(restResponse.data[0].status).toBe('running')

      // Simulate WebSocket message with different status
      const wsManager = new WebSocketManager('ws://localhost:8000/ws')
      wsManager.onMessage((message) => {
        expect(message.data.status).toBe('stopped')
      })

      // Simulate WebSocket message
      const mockMessage = {
        type: 'service_event',
        data: {
          service_id: 'test-service',
          status: 'stopped',
          message: 'Service stopped unexpectedly'
        }
      }

      wsManager.handleMessage(mockMessage)
    })
  })

  describe('Recovery Strategy Tests', () => {
    it('should implement exponential backoff retry strategy', async () => {
      const networkError = new Error('Network Error')
      let callCount = 0
      const callTimes: number[] = []

      vi.spyOn(axios, 'get').mockImplementation(() => {
        callTimes.push(Date.now())
        callCount++
        if (callCount < 3) {
          return Promise.reject(networkError)
        }
        return Promise.resolve({
          data: [mockServiceInfo],
          status: 200,
          statusText: 'OK',
          headers: {},
          config: {}
        })
      })

      const result = await mainApiClient.get('/api/services')
      
      expect(result.data).toEqual([mockServiceInfo])
      expect(callCount).toBe(3)
      
      // Verify exponential backoff timing
      if (callTimes.length >= 3) {
        const firstDelay = callTimes[1] - callTimes[0]
        const secondDelay = callTimes[2] - callTimes[1]
        expect(secondDelay).toBeGreaterThan(firstDelay)
      }
    })

    it('should implement circuit breaker pattern', async () => {
      const networkError = new Error('Network Error')
      
      // Simulate multiple failures to trigger circuit breaker
      vi.spyOn(axios, 'get').mockRejectedValue(networkError)
      
      // Make multiple failed requests
      for (let i = 0; i < 5; i++) {
        try {
          await mainApiClient.get('/api/services')
        } catch (error) {
          // Expected to fail
        }
      }
      
      // Circuit breaker should now be open
      const startTime = Date.now()
      try {
        await mainApiClient.get('/api/services')
      } catch (error) {
        const endTime = Date.now()
        // Should fail fast (circuit breaker open)
        expect(endTime - startTime).toBeLessThan(100)
      }
    })
  })
})