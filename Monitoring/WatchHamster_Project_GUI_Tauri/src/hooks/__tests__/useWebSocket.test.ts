/**
 * WebSocket 훅 테스트
 * 
 * WebSocket 연결, 메시지 송수신, 재연결 등의 기능을 테스트합니다.
 */

import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useWebSocket, type WebSocketMessage, type SystemMetrics } from '../useWebSocket'

// WebSocket 모킹
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
    // 즉시 연결 시뮬레이션
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      this.onopen?.(new Event('open'))
    }, 0)
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
    setTimeout(() => this.onclose?.(closeEvent), 0)
  }

  simulateMessage(data: any) {
    if (this.readyState === MockWebSocket.OPEN) {
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(data),
      })
      setTimeout(() => this.onmessage?.(messageEvent), 0)
    }
  }

  simulateError() {
    const errorEvent = new Event('error')
    setTimeout(() => this.onerror?.(errorEvent), 0)
  }

  simulateClose(wasClean = false, code = 1006) {
    this.readyState = MockWebSocket.CLOSED
    const closeEvent = new CloseEvent('close', {
      code,
      reason: 'Connection lost',
      wasClean,
    })
    setTimeout(() => this.onclose?.(closeEvent), 0)
  }
}

// 전역 WebSocket을 모킹
global.WebSocket = MockWebSocket as any

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllTimers()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('초기 상태가 올바르게 설정되어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    expect(result.current.isConnected).toBe(false)
    expect(result.current.connectionStatus).toBe('disconnected')
    expect(result.current.reconnectCount).toBe(0)
    expect(result.current.lastMessage).toBeNull()
    expect(result.current.lastError).toBeNull()
  })

  it('연결 함수가 제공되어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    expect(typeof result.current.connect).toBe('function')
    expect(typeof result.current.disconnect).toBe('function')
    expect(typeof result.current.sendMessage).toBe('function')
    expect(typeof result.current.subscribe).toBe('function')
    expect(typeof result.current.unsubscribe).toBe('function')
  })

  it('메시지를 큐에 저장할 수 있어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    // 연결되지 않은 상태에서 메시지 전송
    let success: boolean
    act(() => {
      success = result.current.sendMessage({
        type: 'test',
        data: { message: 'queued' },
      })
    })

    expect(success!).toBe(false)
    expect(result.current.queuedMessageCount).toBe(1)
  })

  it('연결 상태를 확인할 수 있어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    expect(result.current.checkConnection()).toBe(false)
    expect(result.current.isConnecting).toBe(false)
    expect(result.current.isReconnecting).toBe(false)
    expect(result.current.hasError).toBe(false)
  })

  it('연결 통계를 제공해야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    const stats = result.current.getConnectionStats()
    
    expect(stats).toHaveProperty('isConnected')
    expect(stats).toHaveProperty('connectionStatus')
    expect(stats).toHaveProperty('reconnectAttempts')
    expect(stats).toHaveProperty('queuedMessages')
    expect(stats).toHaveProperty('lastHeartbeat')
    expect(stats).toHaveProperty('lastError')
  })

  it('구독 메시지를 생성할 수 있어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    // 구독 시도 (연결되지 않은 상태에서는 큐에 저장됨)
    let success: boolean
    act(() => {
      success = result.current.subscribe('metrics')
    })
    
    expect(success!).toBe(false) // 연결되지 않았으므로 false
    expect(result.current.queuedMessageCount).toBe(1)
  })

  it('구독 해제 메시지를 생성할 수 있어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    // 구독 해제 시도
    let success: boolean
    act(() => {
      success = result.current.unsubscribe('metrics')
    })
    
    expect(success!).toBe(false) // 연결되지 않았으므로 false
    expect(result.current.queuedMessageCount).toBe(1)
  })

  it('상태 요청 메시지를 생성할 수 있어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    // 상태 요청 시도
    let success: boolean
    act(() => {
      success = result.current.requestStatus()
    })
    
    expect(success!).toBe(false) // 연결되지 않았으므로 false
    expect(result.current.queuedMessageCount).toBe(1)
  })

  it('옵션을 올바르게 처리해야 함', () => {
    const onConnect = vi.fn()
    const onDisconnect = vi.fn()
    const onError = vi.fn()
    const onMessage = vi.fn()

    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
        reconnectInterval: 1000,
        maxReconnectAttempts: 5,
        heartbeatInterval: 10000,
        enableHeartbeat: false,
        enableReconnect: false,
        onConnect,
        onDisconnect,
        onError,
        onMessage,
      })
    )

    expect(result.current.canReconnect).toBe(false) // enableReconnect가 false이므로
  })

  it('강제 재연결 함수가 제공되어야 함', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/ws',
      })
    )

    expect(typeof result.current.forceReconnect).toBe('function')
    
    // 강제 재연결 실행 (에러 없이 실행되어야 함)
    act(() => {
      result.current.forceReconnect()
    })
  })
})