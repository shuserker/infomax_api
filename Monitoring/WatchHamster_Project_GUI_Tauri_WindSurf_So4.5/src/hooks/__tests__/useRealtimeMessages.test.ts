import { renderHook, act, waitFor } from '@testing-library/react'
import { useRealtimeMessages } from '../useRealtimeMessages'
import { useWebSocketConnection } from '../useWebSocketConnection'

// useWebSocketConnection 모킹
vi.mock('../useWebSocketConnection', () => ({
  useWebSocketConnection: vi.fn(),
}))

const mockUseWebSocketConnection = vi.mocked(useWebSocketConnection)

describe('useRealtimeMessages 훅', () => {
  const mockWebSocketConnection = {
    isConnected: false,
    connectionStatus: 'disconnected' as const,
    reconnectAttempts: 0,
    sendMessage: vi.fn(),
    subscribe: vi.fn(),
    unsubscribe: vi.fn(),
    requestStatus: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
    reconnect: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseWebSocketConnection.mockReturnValue(mockWebSocketConnection)
  })

  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() => useRealtimeMessages())

    expect(result.current.isConnected).toBe(false)
    expect(result.current.systemMetrics).toBeNull()
    expect(result.current.services).toEqual([])
    expect(result.current.alerts).toEqual([])
    expect(result.current.events).toEqual([])
    expect(result.current.logs).toEqual([])
    expect(result.current.isLoading).toBe(true)
  })

  it('시스템 메트릭 업데이트가 올바르게 처리된다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    const testMetrics = {
      cpu_percent: 45.2,
      memory_percent: 67.8,
      memory_used_gb: 8.5,
      memory_total_gb: 16.0,
      disk_usage: 23.4,
      network_status: 'connected',
      connection_count: 5,
      uptime: 3600,
      timestamp: '2024-01-01T12:00:00Z',
    }

    act(() => {
      onMessageHandler({
        type: 'metrics_update',
        data: testMetrics,
      })
    })

    expect(result.current.systemMetrics).toEqual(testMetrics)
    expect(result.current.isLoading).toBe(false)
  })

  it('서비스 업데이트가 올바르게 처리된다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    const testServices = [
      {
        id: 'service1',
        name: 'POSCO 뉴스',
        status: 'running' as const,
        uptime: 1800,
        description: '뉴스 모니터링 서비스',
      },
      {
        id: 'service2',
        name: 'GitHub Pages',
        status: 'stopped' as const,
        uptime: 0,
        description: 'GitHub Pages 모니터링',
      },
    ]

    act(() => {
      onMessageHandler({
        type: 'services_update',
        data: { services: testServices },
      })
    })

    expect(result.current.services).toEqual(testServices)
    expect(result.current.stats.totalServices).toBe(2)
    expect(result.current.stats.runningServices).toBe(1)
    expect(result.current.stats.stoppedServices).toBe(1)
  })

  it('서비스 이벤트가 올바르게 처리된다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    const testEvent = {
      service_id: 'service1',
      event_type: 'started' as const,
      message: '서비스가 시작되었습니다',
      timestamp: '2024-01-01T12:00:00Z',
    }

    act(() => {
      onMessageHandler({
        type: 'service_event',
        data: testEvent,
      })
    })

    expect(result.current.events).toHaveLength(1)
    expect(result.current.events[0]).toEqual(testEvent)
    expect(result.current.stats.totalEvents).toBe(1)
  })

  it('알림이 올바르게 처리된다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    const testAlert = {
      id: 'alert1',
      type: 'warning' as const,
      title: '경고',
      message: '메모리 사용량이 높습니다',
      timestamp: '2024-01-01T12:00:00Z',
    }

    act(() => {
      onMessageHandler({
        type: 'alert',
        data: testAlert,
      })
    })

    expect(result.current.alerts).toHaveLength(1)
    expect(result.current.alerts[0]).toEqual(testAlert)
    expect(result.current.stats.totalAlerts).toBe(1)
    expect(result.current.stats.warningAlerts).toBe(1)
  })

  it('로그 메시지가 올바르게 처리된다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    const testLog = {
      level: 'info' as const,
      message: '서비스 상태 확인 완료',
      timestamp: '2024-01-01T12:00:00Z',
      source: 'system',
    }

    act(() => {
      onMessageHandler({
        type: 'log_message',
        data: testLog,
      })
    })

    expect(result.current.logs).toHaveLength(1)
    expect(result.current.logs[0]).toEqual(testLog)
    expect(result.current.stats.totalLogs).toBe(1)
  })

  it('최대 항목 수 제한이 올바르게 작동한다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => 
      useRealtimeMessages({
        maxAlerts: 2,
        maxEvents: 2,
        maxLogs: 2,
      })
    )

    // 3개의 알림 추가
    act(() => {
      onMessageHandler({
        type: 'alert',
        data: { id: 'alert1', type: 'info', title: '알림 1', message: '메시지 1', timestamp: '2024-01-01T12:00:00Z' },
      })
      onMessageHandler({
        type: 'alert',
        data: { id: 'alert2', type: 'info', title: '알림 2', message: '메시지 2', timestamp: '2024-01-01T12:01:00Z' },
      })
      onMessageHandler({
        type: 'alert',
        data: { id: 'alert3', type: 'info', title: '알림 3', message: '메시지 3', timestamp: '2024-01-01T12:02:00Z' },
      })
    })

    // 최대 2개만 유지되어야 함 (최신 것부터)
    expect(result.current.alerts).toHaveLength(2)
    expect(result.current.alerts[0].id).toBe('alert3')
    expect(result.current.alerts[1].id).toBe('alert2')
  })

  it('알림을 수동으로 추가할 수 있다', () => {
    const { result } = renderHook(() => useRealtimeMessages())

    act(() => {
      const alertId = result.current.addAlert({
        type: 'success',
        title: '성공',
        message: '작업이 완료되었습니다',
      })

      expect(typeof alertId).toBe('string')
    })

    expect(result.current.alerts).toHaveLength(1)
    expect(result.current.alerts[0].type).toBe('success')
    expect(result.current.alerts[0].title).toBe('성공')
  })

  it('알림을 제거할 수 있다', () => {
    const { result } = renderHook(() => useRealtimeMessages())

    let alertId: string

    act(() => {
      alertId = result.current.addAlert({
        type: 'info',
        title: '정보',
        message: '테스트 알림',
      })
    })

    expect(result.current.alerts).toHaveLength(1)

    act(() => {
      result.current.dismissAlert(alertId)
    })

    expect(result.current.alerts).toHaveLength(0)
  })

  it('모든 알림을 제거할 수 있다', () => {
    const { result } = renderHook(() => useRealtimeMessages())

    act(() => {
      result.current.addAlert({ type: 'info', title: '알림 1', message: '메시지 1' })
      result.current.addAlert({ type: 'info', title: '알림 2', message: '메시지 2' })
    })

    expect(result.current.alerts).toHaveLength(2)

    act(() => {
      result.current.clearAllAlerts()
    })

    expect(result.current.alerts).toHaveLength(0)
  })

  it('서비스를 ID로 조회할 수 있다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    const testServices = [
      { id: 'service1', name: '서비스 1', status: 'running' as const, uptime: 100, description: '설명 1' },
      { id: 'service2', name: '서비스 2', status: 'stopped' as const, uptime: 0, description: '설명 2' },
    ]

    act(() => {
      onMessageHandler({
        type: 'services_update',
        data: { services: testServices },
      })
    })

    const service1 = result.current.getServiceById('service1')
    const service3 = result.current.getServiceById('service3')

    expect(service1).toEqual(testServices[0])
    expect(service3).toBeUndefined()
  })

  it('서비스를 상태별로 필터링할 수 있다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    const testServices = [
      { id: 'service1', name: '서비스 1', status: 'running' as const, uptime: 100, description: '설명 1' },
      { id: 'service2', name: '서비스 2', status: 'running' as const, uptime: 200, description: '설명 2' },
      { id: 'service3', name: '서비스 3', status: 'stopped' as const, uptime: 0, description: '설명 3' },
    ]

    act(() => {
      onMessageHandler({
        type: 'services_update',
        data: { services: testServices },
      })
    })

    const runningServices = result.current.getServicesByStatus('running')
    const stoppedServices = result.current.getServicesByStatus('stopped')

    expect(runningServices).toHaveLength(2)
    expect(stoppedServices).toHaveLength(1)
    expect(runningServices[0].id).toBe('service1')
    expect(stoppedServices[0].id).toBe('service3')
  })

  it('시스템 건강 상태가 올바르게 계산된다', () => {
    let onMessageHandler: (message: any) => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onMessageHandler = options.onMessage
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    // 건강한 상태
    act(() => {
      onMessageHandler({
        type: 'metrics_update',
        data: {
          cpu_percent: 30,
          memory_percent: 50,
          memory_used_gb: 4,
          memory_total_gb: 8,
          disk_usage: 20,
          network_status: 'connected',
          connection_count: 3,
          uptime: 1800,
          timestamp: '2024-01-01T12:00:00Z',
        },
      })
    })

    expect(result.current.systemHealth).toBe('healthy')

    // 경고 상태
    act(() => {
      onMessageHandler({
        type: 'metrics_update',
        data: {
          cpu_percent: 80,
          memory_percent: 90,
          memory_used_gb: 7.2,
          memory_total_gb: 8,
          disk_usage: 70,
          network_status: 'connected',
          connection_count: 3,
          uptime: 1800,
          timestamp: '2024-01-01T12:01:00Z',
        },
      })
    })

    expect(result.current.systemHealth).toBe('warning')

    // 위험 상태
    act(() => {
      onMessageHandler({
        type: 'metrics_update',
        data: {
          cpu_percent: 95,
          memory_percent: 98,
          memory_used_gb: 7.8,
          memory_total_gb: 8,
          disk_usage: 90,
          network_status: 'connected',
          connection_count: 3,
          uptime: 1800,
          timestamp: '2024-01-01T12:02:00Z',
        },
      })
    })

    expect(result.current.systemHealth).toBe('critical')
  })

  it('자동 숨김 알림이 올바르게 작동한다', async () => {
    vi.useFakeTimers()

    const { result } = renderHook(() => useRealtimeMessages())

    act(() => {
      result.current.addAlert({
        type: 'info',
        title: '자동 숨김 알림',
        message: '3초 후 사라집니다',
        autoHide: true,
        duration: 3000,
      })
    })

    expect(result.current.alerts).toHaveLength(1)

    // 3초 경과
    act(() => {
      vi.advanceTimersByTime(3000)
    })

    await waitFor(() => {
      expect(result.current.alerts).toHaveLength(0)
    })

    vi.useRealTimers()
  })

  it('연결 상태 변경이 올바르게 처리된다', () => {
    let onConnectHandler: () => void = () => {}
    let onDisconnectHandler: () => void = () => {}

    mockUseWebSocketConnection.mockImplementation((options) => {
      onConnectHandler = options.onConnect!
      onDisconnectHandler = options.onDisconnect!
      return mockWebSocketConnection
    })

    const { result } = renderHook(() => useRealtimeMessages())

    // 연결됨
    act(() => {
      onConnectHandler()
    })

    expect(result.current.isLoading).toBe(false)

    // 연결 해제됨
    act(() => {
      onDisconnectHandler()
    })

    expect(result.current.isLoading).toBe(true)
  })
})