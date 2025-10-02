/**
 * WebSocket 서비스 테스트
 * 
 * WebSocketService 클래스의 기능을 테스트합니다.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { WebSocketService, getWebSocketUrl, getReadyStateString } from '../websocket'

// WebSocket 모킹 (useWebSocket.test.ts와 동일)
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  url: string
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null

  constructor(url: string) {
    this.url = url
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      this.onopen?.(new Event('open'))
    }, 10)
  }

  send(_data: string) {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open')
    }
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED
    const closeEvent = new CloseEvent('close', {
      code: code || 1000,
      reason: reason || '',
      wasClean: true,
    })
    this.onclose?.(closeEvent)
  }

  simulateMessage(data: any) {
    if (this.readyState === MockWebSocket.OPEN) {
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(data),
      })
      this.onmessage?.(messageEvent)
    }
  }

  simulateError() {
    const errorEvent = new Event('error')
    this.onerror?.(errorEvent)
  }

  simulateClose(wasClean = false, code = 1006) {
    this.readyState = MockWebSocket.CLOSED
    const closeEvent = new CloseEvent('close', {
      code,
      reason: 'Connection lost',
      wasClean,
    })
    this.onclose?.(closeEvent)
  }
}

global.WebSocket = MockWebSocket as any

describe('WebSocketService', () => {
  let service: WebSocketService

  beforeEach(() => {
    vi.clearAllTimers()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    service?.disconnect()
  })

  it('WebSocket 서비스를 생성할 수 있어야 함', () => {
    service = new WebSocketService({
      url: 'ws://localhost:8000/ws',
    })

    expect(service).toBeInstanceOf(WebSocketService)
    expect(service.isConnected()).toBe(false)
  })

  it('WebSocket에 연결할 수 있어야 함', async () => {
    const onOpen = vi.fn()
    
    service = new WebSocketService(
      { url: 'ws://localhost:8000/ws' },
      { onOpen }
    )

    service.connect()

    // 연결 완료 대기
    vi.advanceTimersByTime(20)

    expect(onOpen).toHaveBeenCalled()
    expect(service.isConnected()).toBe(true)
    expect(service.getReadyState()).toBe(MockWebSocket.OPEN)
  })

  it('메시지를 전송할 수 있어야 함', () => {
    service = new WebSocketService({
      url: 'ws://localhost:8000/ws',
    })

    service.connect()
    vi.advanceTimersByTime(20)

    const success = service.send({
      type: 'test',
      data: { message: 'hello' },
    })

    expect(success).toBe(true)
  })

  it('연결되지 않은 상태에서 메시지를 큐에 저장해야 함', () => {
    service = new WebSocketService({
      url: 'ws://localhost:8000/ws',
      messageQueueSize: 10,
    })

    // 연결하지 않은 상태에서 메시지 전송
    const success = service.send({
      type: 'test',
      data: { message: 'queued' },
    })

    expect(success).toBe(false) // 전송 실패하지만 큐에 저장됨
  })

  it('메시지를 수신하고 처리해야 함', () => {
    const onMessage = vi.fn()
    
    service = new WebSocketService(
      { url: 'ws://localhost:8000/ws' },
      { onMessage }
    )

    service.connect()
    vi.advanceTimersByTime(20)

    // WebSocket 인스턴스 가져오기
    const wsInstance = (global.WebSocket as any).mock.instances[0] as MockWebSocket

    // 메시지 수신 시뮬레이션
    wsInstance.simulateMessage({
      type: 'test_message',
      data: { content: 'hello' },
      timestamp: new Date().toISOString(),
    })

    expect(onMessage).toHaveBeenCalledWith({
      type: 'test_message',
      data: { content: 'hello' },
      timestamp: expect.any(String),
    })
  })

  it('하트비트를 정기적으로 전송해야 함', () => {
    service = new WebSocketService({
      url: 'ws://localhost:8000/ws',
      heartbeatInterval: 1000,
    })

    service.connect()
    vi.advanceTimersByTime(20)

    // WebSocket 인스턴스의 send 메서드 모킹
    const wsInstance = (global.WebSocket as any).mock.instances[0] as MockWebSocket
    const sendSpy = vi.spyOn(wsInstance, 'send')

    // 하트비트 간격만큼 시간 진행
    vi.advanceTimersByTime(1000)

    expect(sendSpy).toHaveBeenCalledWith(
      expect.stringContaining('"type":"ping"')
    )
  })

  it('연결 오류 시 재연결을 시도해야 함', () => {
    const onReconnect = vi.fn()
    
    service = new WebSocketService(
      {
        url: 'ws://localhost:8000/ws',
        reconnectInterval: 500,
        maxReconnectAttempts: 3,
      },
      { onReconnect }
    )

    service.connect()
    vi.advanceTimersByTime(20)

    // WebSocket 인스턴스 가져오기
    const wsInstance = (global.WebSocket as any).mock.instances[0] as MockWebSocket

    // 비정상 연결 종료 시뮬레이션
    wsInstance.simulateClose(false, 1006)

    expect(service.isConnected()).toBe(false)

    // 재연결 시도 대기
    vi.advanceTimersByTime(600)

    expect(onReconnect).toHaveBeenCalledWith(1)
    expect(service.getReconnectAttempts()).toBe(1)
  })

  it('최대 재연결 시도 횟수를 초과하면 재연결을 중단해야 함', () => {
    const onMaxReconnectReached = vi.fn()
    
    service = new WebSocketService(
      {
        url: 'ws://localhost:8000/ws',
        reconnectInterval: 100,
        maxReconnectAttempts: 2,
      },
      { onMaxReconnectReached }
    )

    service.connect()
    vi.advanceTimersByTime(20)

    // 연속으로 연결 실패 시뮬레이션
    for (let i = 0; i < 3; i++) {
      const wsInstance = (global.WebSocket as any).mock.instances[i] as MockWebSocket
      wsInstance.simulateClose(false, 1006)
      vi.advanceTimersByTime(200)
    }

    expect(onMaxReconnectReached).toHaveBeenCalled()
    expect(service.getReconnectAttempts()).toBe(2)
  })

  it('수동으로 연결을 해제할 수 있어야 함', () => {
    const onClose = vi.fn()
    
    service = new WebSocketService(
      { url: 'ws://localhost:8000/ws' },
      { onClose }
    )

    service.connect()
    vi.advanceTimersByTime(20)

    expect(service.isConnected()).toBe(true)

    service.disconnect()

    expect(service.isConnected()).toBe(false)
    expect(onClose).toHaveBeenCalled()
  })

  it('큐된 메시지를 연결 후 처리해야 함', () => {
    service = new WebSocketService({
      url: 'ws://localhost:8000/ws',
      messageQueueSize: 5,
    })

    // 연결하지 않은 상태에서 메시지들을 큐에 추가
    service.send({ type: 'msg1', data: {} })
    service.send({ type: 'msg2', data: {} })
    service.send({ type: 'msg3', data: {} })

    // 연결
    service.connect()
    vi.advanceTimersByTime(20)

    // WebSocket 인스턴스의 send 메서드 모킹
    const wsInstance = (global.WebSocket as any).mock.instances[0] as MockWebSocket
    const sendSpy = vi.spyOn(wsInstance, 'send')

    // 큐된 메시지들이 전송되었는지 확인
    expect(sendSpy).toHaveBeenCalledTimes(3)
    expect(sendSpy).toHaveBeenCalledWith(expect.stringContaining('"type":"msg1"'))
    expect(sendSpy).toHaveBeenCalledWith(expect.stringContaining('"type":"msg2"'))
    expect(sendSpy).toHaveBeenCalledWith(expect.stringContaining('"type":"msg3"'))
  })
})

describe('WebSocket 유틸리티 함수', () => {
  it('WebSocket URL을 올바르게 생성해야 함', () => {
    // window.location.hostname 모킹
    Object.defineProperty(window, 'location', {
      value: {
        hostname: 'localhost',
      },
      writable: true,
    })

    const url = getWebSocketUrl('/ws', false)
    expect(url).toBe('ws://localhost:8000/ws')

    const secureUrl = getWebSocketUrl('/ws', true)
    expect(secureUrl).toBe('wss://localhost:8000/ws')
  })

  it('WebSocket 상태를 문자열로 변환해야 함', () => {
    expect(getReadyStateString(WebSocket.CONNECTING)).toBe('connecting')
    expect(getReadyStateString(WebSocket.OPEN)).toBe('connected')
    expect(getReadyStateString(WebSocket.CLOSING)).toBe('closing')
    expect(getReadyStateString(WebSocket.CLOSED)).toBe('closed')
    expect(getReadyStateString(null)).toBe('unknown')
  })
})