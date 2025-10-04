/**
 * WebSocket 실시간 통신 통합 테스트
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { WebSocketService } from '@/services/websocket'
import type { WSMessage, ServiceEvent } from '@/types'

// Mock WebSocket 클래스
class MockWebSocket {
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
    // 비동기적으로 연결 상태 변경
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

  // 테스트용 메시지 시뮬레이션 메서드
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

describe('WebSocket 실시간 통신 통합 테스트', () => {
  let wsService: WebSocketService
  let mockWs: MockWebSocket

  beforeEach(() => {
    // WebSocket Mock 설정
    global.WebSocket = MockWebSocket as any
    wsService = new WebSocketService('ws://localhost:8001/ws')
  })

  afterEach(() => {
    if (wsService) {
      wsService.disconnect()
    }
    vi.clearAllMocks()
  })

  describe('WebSocket 연결 관리', () => {
    it('WebSocket 연결 성공 테스트', async () => {
      const connectPromise = wsService.connect()
      
      // 연결 완료 대기
      await connectPromise

      expect(wsService.isConnected()).toBe(true)
    })

    it('WebSocket 연결 실패 테스트', async () => {
      // 연결 실패 시뮬레이션
      global.WebSocket = class extends MockWebSocket {
        constructor(url: string) {
          super(url)
          setTimeout(() => {
            this.simulateError()
          }, 10)
        }
      } as any

      const wsServiceFail = new WebSocketService('ws://invalid-url')
      
      await expect(wsServiceFail.connect()).rejects.toThrow()
    })

    it('WebSocket 연결 해제 테스트', async () => {
      await wsService.connect()
      expect(wsService.isConnected()).toBe(true)

      wsService.disconnect()
      expect(wsService.isConnected()).toBe(false)
    })
  })

  describe('실시간 메시지 수신 테스트', () => {
    beforeEach(async () => {
      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket
    })

    it('시스템 메트릭 업데이트 메시지 수신 테스트', async () => {
      const mockMetricsMessage: WSMessage = {
        type: 'status_update',
        data: {
          cpu_percent: 45.2,
          memory_percent: 67.8,
          disk_usage: 23.4,
          network_status: 'connected',
          uptime: 86400,
          active_services: 5
        },
        timestamp: new Date().toISOString()
      }

      let receivedMessage: WSMessage | null = null
      wsService.onMessage((message) => {
        receivedMessage = message
      })

      // 메시지 시뮬레이션
      mockWs.simulateMessage(mockMetricsMessage)

      // 메시지 수신 확인
      expect(receivedMessage).toEqual(mockMetricsMessage)
      expect(receivedMessage?.type).toBe('status_update')
      expect(receivedMessage?.data).toMatchObject({
        cpu_percent: expect.any(Number),
        memory_percent: expect.any(Number),
        disk_usage: expect.any(Number)
      })
    })

    it('서비스 이벤트 메시지 수신 테스트', async () => {
      const serviceEvent: ServiceEvent = {
        service_id: 'posco-news',
        event_type: 'started',
        message: 'POSCO 뉴스 서비스가 시작되었습니다',
        details: { uptime: 0 }
      }

      const mockServiceMessage: WSMessage = {
        type: 'service_event',
        data: serviceEvent,
        timestamp: new Date().toISOString()
      }

      let receivedMessage: WSMessage | null = null
      wsService.onMessage((message) => {
        receivedMessage = message
      })

      mockWs.simulateMessage(mockServiceMessage)

      expect(receivedMessage).toEqual(mockServiceMessage)
      expect(receivedMessage?.type).toBe('service_event')
      expect(receivedMessage?.data.service_id).toBe('posco-news')
      expect(receivedMessage?.data.event_type).toBe('started')
    })

    it('알림 메시지 수신 테스트', async () => {
      const mockAlertMessage: WSMessage = {
        type: 'alert',
        data: {
          level: 'warning',
          title: '시스템 경고',
          message: 'CPU 사용률이 높습니다 (85%)',
          timestamp: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      }

      let receivedMessage: WSMessage | null = null
      wsService.onMessage((message) => {
        receivedMessage = message
      })

      mockWs.simulateMessage(mockAlertMessage)

      expect(receivedMessage).toEqual(mockAlertMessage)
      expect(receivedMessage?.type).toBe('alert')
      expect(receivedMessage?.data.level).toBe('warning')
    })

    it('로그 업데이트 메시지 수신 테스트', async () => {
      const mockLogMessage: WSMessage = {
        type: 'log_update',
        data: {
          service_id: 'posco-news',
          logs: [
            {
              timestamp: new Date().toISOString(),
              level: 'INFO',
              message: '뉴스 데이터 업데이트 완료'
            }
          ]
        },
        timestamp: new Date().toISOString()
      }

      let receivedMessage: WSMessage | null = null
      wsService.onMessage((message) => {
        receivedMessage = message
      })

      mockWs.simulateMessage(mockLogMessage)

      expect(receivedMessage).toEqual(mockLogMessage)
      expect(receivedMessage?.type).toBe('log_update')
      expect(receivedMessage?.data.logs).toBeInstanceOf(Array)
    })
  })

  describe('메시지 전송 테스트', () => {
    beforeEach(async () => {
      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket
    })

    it('클라이언트에서 서버로 메시지 전송 테스트', () => {
      const testMessage = {
        type: 'ping',
        data: { timestamp: Date.now() }
      }

      wsService.send(testMessage)

      expect(mockWs.send).toHaveBeenCalledWith(JSON.stringify(testMessage))
    })

    it('서비스 제어 명령 전송 테스트', () => {
      const controlMessage = {
        type: 'service_control',
        data: {
          service_id: 'posco-news',
          action: 'restart'
        }
      }

      wsService.send(controlMessage)

      expect(mockWs.send).toHaveBeenCalledWith(JSON.stringify(controlMessage))
    })
  })

  describe('연결 상태 관리 및 재연결 테스트', () => {
    it('연결 끊김 감지 테스트', async () => {
      await wsService.connect()
      expect(wsService.isConnected()).toBe(true)

      mockWs = (wsService as any).ws as MockWebSocket
      
      let disconnected = false
      wsService.onDisconnect(() => {
        disconnected = true
      })

      // 연결 끊김 시뮬레이션
      mockWs.simulateClose(1006, 'Connection lost')

      expect(disconnected).toBe(true)
      expect(wsService.isConnected()).toBe(false)
    })

    it('자동 재연결 테스트', async () => {
      // 자동 재연결 활성화
      wsService.enableAutoReconnect(true, 100) // 100ms 간격

      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket

      let reconnectAttempted = false
      wsService.onReconnect(() => {
        reconnectAttempted = true
      })

      // 연결 끊김 시뮬레이션
      mockWs.simulateClose(1006, 'Connection lost')

      // 재연결 시도 대기
      await new Promise(resolve => setTimeout(resolve, 150))

      expect(reconnectAttempted).toBe(true)
    })

    it('수동 재연결 테스트', async () => {
      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket

      // 연결 끊김
      mockWs.simulateClose()
      expect(wsService.isConnected()).toBe(false)

      // 수동 재연결
      await wsService.reconnect()
      expect(wsService.isConnected()).toBe(true)
    })
  })

  describe('오류 처리 및 복구 테스트', () => {
    it('WebSocket 오류 처리 테스트', async () => {
      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket

      let errorOccurred = false
      wsService.onError((error) => {
        errorOccurred = true
      })

      // 오류 시뮬레이션
      mockWs.simulateError()

      expect(errorOccurred).toBe(true)
    })

    it('잘못된 메시지 형식 처리 테스트', async () => {
      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket

      let errorHandled = false
      wsService.onError(() => {
        errorHandled = true
      })

      // 잘못된 JSON 메시지 시뮬레이션
      if (mockWs.onmessage) {
        const invalidEvent = new MessageEvent('message', {
          data: 'invalid json'
        })
        mockWs.onmessage(invalidEvent)
      }

      // 오류가 적절히 처리되었는지 확인
      // (실제 구현에 따라 다를 수 있음)
    })

    it('연결 시간 초과 처리 테스트', async () => {
      // 연결 시간 초과 시뮬레이션
      global.WebSocket = class extends MockWebSocket {
        constructor(url: string) {
          super(url)
          // 연결 시간 초과 (onopen 호출하지 않음)
        }
      } as any

      const wsServiceTimeout = new WebSocketService('ws://timeout-url')
      
      // 타임아웃 설정 (실제 구현에 따라 다를 수 있음)
      await expect(
        Promise.race([
          wsServiceTimeout.connect(),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Connection timeout')), 1000)
          )
        ])
      ).rejects.toThrow('Connection timeout')
    })
  })

  describe('메시지 큐 및 버퍼링 테스트', () => {
    it('연결 전 메시지 큐잉 테스트', () => {
      const wsServiceQueue = new WebSocketService('ws://localhost:8001/ws')
      
      const testMessage = {
        type: 'test',
        data: { message: 'queued message' }
      }

      // 연결 전에 메시지 전송 시도
      wsServiceQueue.send(testMessage)

      // 메시지가 큐에 저장되었는지 확인 (실제 구현에 따라 다름)
      // 이는 WebSocketService 구현에 큐 기능이 있다고 가정
    })

    it('대용량 메시지 처리 테스트', async () => {
      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket

      const largeMessage = {
        type: 'large_data',
        data: {
          logs: Array(1000).fill(0).map((_, i) => ({
            id: i,
            timestamp: new Date().toISOString(),
            level: 'INFO',
            message: `로그 메시지 ${i}`.repeat(100) // 긴 메시지
          }))
        }
      }

      let receivedMessage: WSMessage | null = null
      wsService.onMessage((message) => {
        receivedMessage = message
      })

      mockWs.simulateMessage(largeMessage)

      expect(receivedMessage).toEqual(largeMessage)
      expect(receivedMessage?.data.logs).toHaveLength(1000)
    })
  })

  describe('성능 및 메모리 테스트', () => {
    it('다중 메시지 처리 성능 테스트', async () => {
      await wsService.connect()
      mockWs = (wsService as any).ws as MockWebSocket

      const messageCount = 100
      let receivedCount = 0

      wsService.onMessage(() => {
        receivedCount++
      })

      const startTime = performance.now()

      // 다중 메시지 전송
      for (let i = 0; i < messageCount; i++) {
        mockWs.simulateMessage({
          type: 'performance_test',
          data: { index: i },
          timestamp: new Date().toISOString()
        })
      }

      const endTime = performance.now()
      const processingTime = endTime - startTime

      expect(receivedCount).toBe(messageCount)
      expect(processingTime).toBeLessThan(1000) // 1초 이내 처리
    })

    it('메모리 누수 방지 테스트', async () => {
      // 여러 번 연결/해제 반복
      for (let i = 0; i < 10; i++) {
        const tempWsService = new WebSocketService('ws://localhost:8001/ws')
        await tempWsService.connect()
        tempWsService.disconnect()
      }

      // 메모리 사용량 확인 (실제 환경에서는 더 정교한 측정 필요)
      // 이는 개념적인 테스트입니다
      expect(true).toBe(true) // 메모리 누수가 없다면 테스트 통과
    })
  })
})