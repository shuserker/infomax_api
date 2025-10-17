import { useState, useEffect, useCallback } from 'react'
import { useWebSocket } from './useWebSocket'

interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  memory_used_gb: number
  memory_total_gb: number
  disk_usage: number
  network_status: string
  connection_count: number
  uptime: number
  timestamp: string
}

interface ServiceInfo {
  id: string
  name: string
  status: 'running' | 'stopped' | 'error' | 'idle' | 'starting' | 'stopping'
  uptime: number
  description: string
  last_error?: string
  config?: Record<string, any>
}

interface AlertInfo {
  alert_type: string
  message: string
  severity: 'info' | 'warning' | 'error'
  timestamp: string
}

interface ServiceEvent {
  service_id: string
  event_type: 'started' | 'stopped' | 'error' | 'restarted'
  message: string
  timestamp: string
}

export const useRealtimeStatus = () => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [services, setServices] = useState<ServiceInfo[]>([])
  const [alerts, setAlerts] = useState<AlertInfo[]>([])
  const [recentEvents, setRecentEvents] = useState<ServiceEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // WebSocket 연결 설정
  const {
    isConnected,
    connectionStatus,
    reconnectCount,
    lastHeartbeat,
    sendMessage,
    connect,
    disconnect,
    subscribe,
    requestStatus,
  } = useWebSocket({
    url: `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`,
    reconnectInterval: 3000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,

    onConnect: () => {
      console.log('실시간 상태 모니터링 연결됨')
      setIsLoading(false)
      // 모든 업데이트 구독
      subscribe('all')
    },

    onDisconnect: () => {
      console.log('실시간 상태 모니터링 연결 해제됨')
      setIsLoading(true)
    },

    onError: error => {
      console.error('실시간 상태 모니터링 오류:', error)
      setIsLoading(true)
    },

    onMetricsUpdate: (metrics: SystemMetrics) => {
      setSystemMetrics(metrics)
    },

    onServicesUpdate: (servicesData: ServiceInfo[]) => {
      setServices(servicesData)
    },

    onServiceEvent: (event: ServiceEvent) => {
      // 최근 이벤트 목록에 추가 (최대 50개 유지)
      setRecentEvents((prev: ServiceEvent[]) => [event, ...prev.slice(0, 49)])

      // 서비스 상태 업데이트
      setServices((prev: ServiceInfo[]) =>
        prev.map((service: ServiceInfo) =>
          service.id === event.service_id
            ? { ...service, status: getStatusFromEvent(event.event_type) }
            : service
        )
      )
    },

    onAlert: (alert: AlertInfo) => {
      // 알림 목록에 추가 (최대 20개 유지)
      setAlerts((prev: AlertInfo[]) => [alert, ...prev.slice(0, 19)])
    },
  })

  // 이벤트 타입에서 서비스 상태 추출
  const getStatusFromEvent = (eventType: string): ServiceInfo['status'] => {
    switch (eventType) {
      case 'started':
      case 'restarted':
        return 'running'
      case 'stopped':
        return 'stopped'
      case 'error':
        return 'error'
      default:
        return 'idle'
    }
  }

  // 서비스별 상태 조회
  const getServiceStatus = useCallback(
    (serviceId: string) => {
      return services.find((service: ServiceInfo) => service.id === serviceId)
    },
    [services]
  )

  // 실행 중인 서비스 수
  const runningServicesCount = services.filter((s: ServiceInfo) => s.status === 'running').length

  // 오류 상태 서비스 수
  const errorServicesCount = services.filter((s: ServiceInfo) => s.status === 'error').length

  // 시스템 전체 상태
  const systemHealth = systemMetrics
    ? systemMetrics.cpu_percent > 80 || systemMetrics.memory_percent > 90
      ? 'critical'
      : systemMetrics.cpu_percent > 60 || systemMetrics.memory_percent > 75
        ? 'warning'
        : 'healthy'
    : 'unknown'

  // 알림 제거
  const dismissAlert = useCallback((index: number) => {
    setAlerts((prev: AlertInfo[]) => prev.filter((_: AlertInfo, i: number) => i !== index))
  }, [])

  // 모든 알림 제거
  const clearAllAlerts = useCallback(() => {
    setAlerts([])
  }, [])

  // 이벤트 기록 제거
  const clearEvents = useCallback(() => {
    setRecentEvents([])
  }, [])

  // 수동 상태 새로고침
  const refreshStatus = useCallback(() => {
    if (isConnected) {
      requestStatus()
    }
  }, [isConnected, requestStatus])

  // 연결 재시도
  const reconnect = useCallback(() => {
    disconnect()
    setTimeout(() => {
      connect()
    }, 1000)
  }, [connect, disconnect])

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    // 연결 상태
    isConnected,
    connectionStatus,
    reconnectCount,
    lastHeartbeat,
    isLoading,

    // 시스템 데이터
    systemMetrics,
    services,
    alerts,
    recentEvents,

    // 계산된 상태
    runningServicesCount,
    errorServicesCount,
    systemHealth,

    // 유틸리티 함수
    getServiceStatus,
    dismissAlert,
    clearAllAlerts,
    clearEvents,
    refreshStatus,
    reconnect,

    // WebSocket 제어
    sendMessage,
    subscribe,
  }
}

export type { SystemMetrics, ServiceInfo, AlertInfo, ServiceEvent }
