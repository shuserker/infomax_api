import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useWebSocket } from '../useWebSocket'

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
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    // 비동기적으로 연결 상태 변경
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      this.onopen?.(new Event('open'))
    }, 10)
  }

  send = vi.fn()
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.(new CloseEvent('close'))
  })
  addEventListener = vi.fn()
  removeEventListener = vi.fn()
  dispatchEvent = vi.fn()
}

// 전역 WebSocket을 모킹
global.WebSocket = MockWebSocket as any

describe('useWebSocket', () => {
  const mockUrl = 'ws://localhost:8000/ws'
  
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
      })
    )

    expect(result.current.isConnected).toBe(false)
    expect(result.current.connectionStatus).toBe('disconnected')
    expect(result.current.lastMessage).toBe(null)
    expect(result.current.reconnectCount).toBe(0)
  })

  it('연결 함수가 WebSocket을 생성한다', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
      })
    )

    act(() => {
      result.current.connect()
    })

    expect(result.current.connectionStatus).toBe('connecting')

    // 연결 완료까지 대기
    await act(async () => {
      vi.advanceTimersByTime(20)
    })

    expect(result.current.isConnected).toBe(true)
    expect(result.current.connectionStatus).toBe('connected')
  })

  it('메시지 전송이 작동한다', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
      })
    )

    // 연결
    act(() => {
      result.current.connect()
    })

    await act(async () => {
      vi.advanceTimersByTime(20)
    })

    // 메시지 전송
    const testMessage = {
      type: 'test',
      data: { message: 'hello' },
    }

    act(() => {
      result.current.sendMessage(testMessage)
    })

    // WebSocket의 send 메서드가 호출되었는지 확인
    expect(MockWebSocket.prototype.send).toHaveBeenCalled()
  })

  it('연결되지 않은 상태에서 메시지를 큐에 저장한다', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
      })
    )

    const testMessage = {
      type: 'test',
      data: { message: 'queued' },
    }

    act(() => {
      result.current.sendMessage(testMessage)
    })

    expect(result.current.queuedMessageCount).toBe(1)
  })

  it('연결 해제가 작동한다', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
      })
    )

    // 연결
    act(() => {
      result.current.connect()
    })

    await act(async () => {
      vi.advanceTimersByTime(20)
    })

    expect(result.current.isConnected).toBe(true)

    // 연결 해제
    act(() => {
      result.current.disconnect()
    })

    expect(result.current.isConnected).toBe(false)
    expect(result.current.connectionStatus).toBe('disconnected')
  })

  it('구독 기능이 작동한다', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
      })
    )

    // 연결
    act(() => {
      result.current.connect()
    })

    await act(async () => {
      vi.advanceTimersByTime(20)
    })

    // 구독
    act(() => {
      result.current.subscribe('metrics', { interval: 5000 })
    })

    expect(MockWebSocket.prototype.send).toHaveBeenCalledWith(
      expect.stringContaining('"type":"subscribe"')
    )
  })

  it('상태 요청이 작동한다', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
      })
    )

    // 연결
    act(() => {
      result.current.connect()
    })

    await act(async () => {
      vi.advanceTimersByTime(20)
    })

    // 상태 요청
    act(() => {
      result.current.requestStatus()
    })

    expect(MockWebSocket.prototype.send).toHaveBeenCalledWith(
      expect.stringContaining('"type":"request_status"')
    )
  })

  it('연결 통계를 올바르게 반환한다', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
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

  it('콜백 함수들이 올바르게 호출된다', async () => {
    const onConnect = vi.fn()
    const onMessage = vi.fn()
    const onDisconnect = vi.fn()

    const { result } = renderHook(() =>
      useWebSocket({
        url: mockUrl,
        onConnect,
        onMessage,
        onDisconnect,
      })
    )

    // 연결
    act(() => {
      result.current.connect()
    })

    await act(async () => {
      vi.advanceTimersByTime(20)
    })

    expect(onConnect).toHaveBeenCalled()

    // 연결 해제
    act(() => {
      result.current.disconnect()
    })

    expect(onDisconnect).toHaveBeenCalled()
  })
})