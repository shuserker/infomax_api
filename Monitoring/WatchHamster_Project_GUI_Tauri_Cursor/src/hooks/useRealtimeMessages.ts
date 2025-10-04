/**
 * 실시간 메시지 처리 훅
 * 
 * 이 훅은 WebSocket을 통해 수신되는 다양한 타입의 메시지를
 * 처리하고 상태를 관리합니다.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { useWebSocketConnection } from './useWebSocketConnection'

// 메시지 타입 정의
export interface SystemMetrics {
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

export interface ServiceInfo {
  id: string
  name: string
  status: 'running' | 'stopped' | 'error' | 'idle' | 'starting' | 'stopping'
  uptime: number
  description: string
  last_error?: string
  config?: Record<string, any>
}

export interface AlertMessage {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  timestamp: string
  dismissible?: boolean
  autoHide?: boolean
  duration?: number
}

export interface ServiceEvent {
  service_id: string
  event_type: 'started' | 'stopped' | 'error' | 'restarted' | 'status_changed'
  message: string
  timestamp: string
  details?: Record<string, any>
}

export interface LogMessage {
  level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  timestamp: string
  source?: string
  details?: Record<string, any>
}

// 훅 옵션
export interface UseRealtimeMessagesOptions {
  maxAlerts?: number
  maxEvents?: number
  maxLogs?: number
  autoSubscribe?: boolean
  subscriptions?: string[]
}

export const useRealtimeMessages = (options: UseRealtimeMessagesOptions = {}) => {
  const {
    maxAlerts = 50,
    maxEvents = 100,
    maxLogs = 500,
    autoSubscribe = true,
    subscriptions = ['all'],
  } = options

  // 상태 관리
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [services, setServices] = useState<ServiceInfo[]>([])
  const [alerts, setAlerts] = useState<AlertMessage[]>([])
  const [events, setEvents] = useState<ServiceEvent[]>([])
  const [logs, setLogs] = useState<LogMessage[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // 자동 숨김 타이머 관리
  const alertTimers = useRef<Map<string, NodeJS.Timeout>>(new Map())

  // 메시지 처리 함수
  const handleMessage = useCallback((message: any) => {
    const { type, data } = message

    switch (type) {
      case 'metrics_update':
        setSystemMetrics(data as SystemMetrics)
        setIsLoading(false)
        break

      case 'services_update':
        setServices(data.services as ServiceInfo[])
        setIsLoading(false)
        break

      case 'service_event': {
        const event = data as ServiceEvent
        setEvents(prev => {
          const newEvents = [event, ...prev]
          return newEvents.slice(0, maxEvents)
        })
        
        // 서비스 상태 업데이트
        if (event.event_type === 'status_changed') {
          setServices(prev => 
            prev.map(service => 
              service.id === event.service_id 
                ? { ...service, ...event.details }
                : service
            )
          )
        }
        break
      }

      case 'alert': {
        const alert = data as AlertMessage
        setAlerts(prev => {
          const newAlerts = [alert, ...prev]
          
          // 자동 숨김 설정
          if (alert.autoHide && alert.duration) {
            const timer = setTimeout(() => {
              dismissAlert(alert.id)
            }, alert.duration)
            alertTimers.current.set(alert.id, timer)
          }
          
          return newAlerts.slice(0, maxAlerts)
        })
        break
      }

      case 'log_message': {
        const log = data as LogMessage
        setLogs(prev => {
          const newLogs = [log, ...prev]
          return newLogs.slice(0, maxLogs)
        })
        break
      }

      case 'connection_established':
        console.log('실시간 메시지 연결 확인:', data.message)
        setIsLoading(false)
        break

      case 'error':
        console.error('서버 오류:', data)
        addAlert({
          type: 'error',
          title: '서버 오류',
          message: data.message || '알 수 없는 오류가 발생했습니다.',
        })
        break

      default:
        console.log('알 수 없는 메시지 타입:', type, data)
    }
  }, [maxAlerts, maxEvents, maxLogs])

  // WebSocket 연결
  const {
    isConnected,
    connectionStatus,
    reconnectAttempts,
    sendMessage,
    subscribe,
    unsubscribe,
    requestStatus,
    connect,
    disconnect,
    reconnect,
  } = useWebSocketConnection({
    onMessage: handleMessage,
    onConnect: () => {
      console.log('실시간 메시지 시스템 연결됨')
      setIsLoading(false)
      
      // 자동 구독
      if (autoSubscribe) {
        subscriptions.forEach(sub => subscribe(sub))
      }
      
      // 초기 상태 요청
      requestStatus()
    },
    onDisconnect: () => {
      console.log('실시간 메시지 시스템 연결 해제됨')
      setIsLoading(true)
    },
    onError: (error) => {
      console.error('실시간 메시지 시스템 오류:', error)
      setIsLoading(true)
    },
  })

  // 알림 추가 함수
  const addAlert = useCallback((alert: Omit<AlertMessage, 'id' | 'timestamp'>) => {
    const newAlert: AlertMessage = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
      timestamp: new Date().toISOString(),
      dismissible: true,
      ...alert,
    }

    setAlerts(prev => {
      const newAlerts = [newAlert, ...prev]
      
      // 자동 숨김 설정
      if (newAlert.autoHide && newAlert.duration) {
        const timer = setTimeout(() => {
          dismissAlert(newAlert.id)
        }, newAlert.duration)
        alertTimers.current.set(newAlert.id, timer)
      }
      
      return newAlerts.slice(0, maxAlerts)
    })

    return newAlert.id
  }, [maxAlerts])

  // 알림 제거 함수
  const dismissAlert = useCallback((alertId: string) => {
    // 타이머 정리
    const timer = alertTimers.current.get(alertId)
    if (timer) {
      clearTimeout(timer)
      alertTimers.current.delete(alertId)
    }

    setAlerts(prev => prev.filter(alert => alert.id !== alertId))
  }, [])

  // 모든 알림 제거
  const clearAllAlerts = useCallback(() => {
    // 모든 타이머 정리
    alertTimers.current.forEach(timer => clearTimeout(timer))
    alertTimers.current.clear()
    
    setAlerts([])
  }, [])

  // 이벤트 기록 제거
  const clearEvents = useCallback(() => {
    setEvents([])
  }, [])

  // 로그 기록 제거
  const clearLogs = useCallback(() => {
    setLogs([])
  }, [])

  // 서비스 상태 조회
  const getServiceById = useCallback((serviceId: string) => {
    return services.find(service => service.id === serviceId)
  }, [services])

  // 서비스 상태별 필터링
  const getServicesByStatus = useCallback((status: ServiceInfo['status']) => {
    return services.filter(service => service.status === status)
  }, [services])

  // 통계 계산
  const stats = {
    totalServices: services.length,
    runningServices: services.filter(s => s.status === 'running').length,
    stoppedServices: services.filter(s => s.status === 'stopped').length,
    errorServices: services.filter(s => s.status === 'error').length,
    totalAlerts: alerts.length,
    errorAlerts: alerts.filter(a => a.type === 'error').length,
    warningAlerts: alerts.filter(a => a.type === 'warning').length,
    totalEvents: events.length,
    totalLogs: logs.length,
    errorLogs: logs.filter(l => l.level === 'error').length,
  }

  // 시스템 건강 상태
  const systemHealth = systemMetrics ? (
    systemMetrics.cpu_percent > 90 || systemMetrics.memory_percent > 95 ? 'critical' :
    systemMetrics.cpu_percent > 75 || systemMetrics.memory_percent > 85 ? 'warning' :
    'healthy'
  ) : 'unknown'

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      // 모든 타이머 정리
      alertTimers.current.forEach(timer => clearTimeout(timer))
      alertTimers.current.clear()
    }
  }, [])

  return {
    // 연결 상태
    isConnected,
    connectionStatus,
    reconnectAttempts,
    isLoading,

    // 데이터
    systemMetrics,
    services,
    alerts,
    events,
    logs,

    // 통계
    stats,
    systemHealth,

    // 데이터 조회
    getServiceById,
    getServicesByStatus,

    // 알림 관리
    addAlert,
    dismissAlert,
    clearAllAlerts,

    // 데이터 관리
    clearEvents,
    clearLogs,

    // WebSocket 제어
    sendMessage,
    subscribe,
    unsubscribe,
    requestStatus,
    connect,
    disconnect,
    reconnect,
  }
}

export default useRealtimeMessages