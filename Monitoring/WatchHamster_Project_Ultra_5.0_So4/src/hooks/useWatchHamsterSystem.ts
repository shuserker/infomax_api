/**
 * WatchHamster 시스템 통합 훅
 * API 서비스와 WebSocket을 통합하여 실시간 상태 관리
 */

import { useEffect, useCallback, useRef } from 'react'
import { useAppStore } from '../stores/useAppStore'
import { apiService } from '../services/api'
import { createWatchHamsterWebSocket } from '../services/websocket'
import type { 
  NewsUpdateMessage, 
  ServiceEventMessage, 
  SystemMetricsMessage, 
  LogUpdateMessage, 
  AlertMessage 
} from '../services/websocket'

export const useWatchHamsterSystem = () => {
  const wsRef = useRef<ReturnType<typeof createWatchHamsterWebSocket> | null>(null)
  const {
    // 상태
    isConnected,
    connectionStatus,
    systemMetrics,
    services,
    newsStatus,
    settings,
    loading,
    errors,

    // 액션
    setConnectionStatus,
    setConnected,
    setLastHeartbeat,
    updateSystemMetrics,
    updateServices,
    updateService,
    updateNewsStatus,
    updateSingleNewsStatus,
    addLogEntry,
    addAlert,
    addNotification,
    setLoading,
    setError,
    clearErrors
  } = useAppStore()

  // API 호출 래퍼 (에러 처리 포함)
  const apiCall = useCallback(async <T>(
    apiFunction: () => Promise<T>,
    loadingKey?: keyof typeof loading,
    errorKey?: keyof typeof errors
  ): Promise<T | null> => {
    try {
      if (loadingKey) setLoading(loadingKey, true)
      if (errorKey) setError(errorKey, null)
      
      const result = await apiFunction()
      return result
    } catch (error) {
      console.error('API 호출 실패:', error)
      
      if (errorKey) {
        setError(errorKey, error instanceof Error ? error.message : '알 수 없는 오류')
      }
      
      addNotification({
        title: 'API 오류',
        message: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다',
        type: 'error'
      })
      
      return null
    } finally {
      if (loadingKey) setLoading(loadingKey, false)
    }
  }, [setLoading, setError, addNotification])

  // 시스템 상태 조회
  const fetchSystemStatus = useCallback(async () => {
    const result = await apiCall(
      () => apiService.getSystemStatus(),
      'metrics',
      'api'
    )
    
    if (result) {
      // 시스템 메트릭이 있으면 업데이트
      if (result.metrics) {
        updateSystemMetrics(result.metrics)
      }
    }
    
    return result
  }, [apiCall, updateSystemMetrics])

  // 서비스 목록 조회
  const fetchServices = useCallback(async () => {
    const result = await apiCall(
      () => apiService.getServices(),
      'services',
      'api'
    )
    
    if (result) {
      updateServices(result)
    }
    
    return result
  }, [apiCall, updateServices])

  // 뉴스 상태 조회
  const fetchNewsStatus = useCallback(async () => {
    const result = await apiCall(
      () => apiService.getNewsStatus(),
      'news',
      'api'
    )
    
    if (result) {
      const newsArray = Array.isArray(result) ? result : [result]
      updateNewsStatus(newsArray)
    }
    
    return result
  }, [apiCall, updateNewsStatus])

  // 시스템 제어 함수들
  const startSystem = useCallback(async () => {
    const result = await apiCall(() => apiService.startSystem())
    
    if (result) {
      addNotification({
        title: '시스템 시작',
        message: result.message,
        type: 'success'
      })
      
      // 상태 새로고침
      setTimeout(() => {
        fetchSystemStatus()
        fetchServices()
      }, 2000)
    }
    
    return result
  }, [apiCall, addNotification, fetchSystemStatus, fetchServices])

  const stopSystem = useCallback(async () => {
    const result = await apiCall(() => apiService.stopSystem())
    
    if (result) {
      addNotification({
        title: '시스템 중지',
        message: result.message,
        type: 'info'
      })
      
      // 상태 새로고침
      setTimeout(() => {
        fetchSystemStatus()
        fetchServices()
      }, 2000)
    }
    
    return result
  }, [apiCall, addNotification, fetchSystemStatus, fetchServices])

  const restartSystem = useCallback(async () => {
    const result = await apiCall(() => apiService.restartSystem())
    
    if (result) {
      addNotification({
        title: '시스템 재시작',
        message: result.message,
        type: 'info'
      })
      
      // 상태 새로고침
      setTimeout(() => {
        fetchSystemStatus()
        fetchServices()
      }, 5000)
    }
    
    return result
  }, [apiCall, addNotification, fetchSystemStatus, fetchServices])

  // 서비스 제어 함수들
  const startService = useCallback(async (serviceId: string) => {
    const result = await apiCall(() => apiService.startService(serviceId))
    
    if (result) {
      addNotification({
        title: '서비스 시작',
        message: result.message,
        type: 'success'
      })
      
      // 해당 서비스 상태 업데이트
      updateService(serviceId, { status: 'starting' })
    }
    
    return result
  }, [apiCall, addNotification, updateService])

  const stopService = useCallback(async (serviceId: string) => {
    const result = await apiCall(() => apiService.stopService(serviceId))
    
    if (result) {
      addNotification({
        title: '서비스 중지',
        message: result.message,
        type: 'info'
      })
      
      // 해당 서비스 상태 업데이트
      updateService(serviceId, { status: 'stopping' })
    }
    
    return result
  }, [apiCall, addNotification, updateService])

  const restartService = useCallback(async (serviceId: string) => {
    const result = await apiCall(() => apiService.restartService(serviceId))
    
    if (result) {
      addNotification({
        title: '서비스 재시작',
        message: result.message,
        type: 'info'
      })
      
      // 해당 서비스 상태 업데이트
      updateService(serviceId, { status: 'starting' })
    }
    
    return result
  }, [apiCall, addNotification, updateService])

  // 뉴스 데이터 갱신
  const refreshNewsData = useCallback(async (newsTypes?: string[], force: boolean = false) => {
    const result = await apiCall(() => apiService.refreshNewsData(newsTypes, force))
    
    if (result) {
      addNotification({
        title: '뉴스 데이터 갱신',
        message: result.message,
        type: 'info'
      })
    }
    
    return result
  }, [apiCall, addNotification])

  // WebSocket 이벤트 핸들러들
  const handleNewsUpdate = useCallback((message: NewsUpdateMessage) => {
    const { news_type, status, last_update, processing_time } = message.data
    
    updateSingleNewsStatus(news_type, {
      status,
      last_update
    })
    
    if (settings.notifications && settings.serviceAlerts) {
      addNotification({
        title: '뉴스 업데이트',
        message: `${news_type} 뉴스가 업데이트되었습니다 (${status})`,
        type: status === 'error' ? 'error' : 'info'
      })
    }
  }, [updateSingleNewsStatus, settings, addNotification])

  const handleServiceEvent = useCallback((message: ServiceEventMessage) => {
    const { service_id, event_type, message: eventMessage } = message.data
    
    // 서비스 상태 업데이트
    let newStatus: any = 'idle'
    switch (event_type) {
      case 'started':
      case 'restarted':
        newStatus = 'running'
        break
      case 'stopped':
        newStatus = 'stopped'
        break
      case 'error':
        newStatus = 'error'
        break
    }
    
    updateService(service_id, { status: newStatus })
    
    if (settings.notifications && settings.serviceAlerts) {
      addNotification({
        title: '서비스 이벤트',
        message: eventMessage,
        type: event_type === 'error' ? 'error' : 'info'
      })
    }
  }, [updateService, settings, addNotification])

  const handleSystemMetrics = useCallback((message: SystemMetricsMessage) => {
    updateSystemMetrics(message.data)
  }, [updateSystemMetrics])

  const handleLogUpdate = useCallback((message: LogUpdateMessage) => {
    addLogEntry(message.data)
    
    // 에러 로그인 경우 알림 생성
    if (message.data.level === 'ERROR' && settings.notifications && settings.errorAlerts) {
      addNotification({
        title: '시스템 오류',
        message: message.data.message,
        type: 'error'
      })
    }
  }, [addLogEntry, settings, addNotification])

  const handleAlert = useCallback((message: AlertMessage) => {
    addAlert(message)
    
    if (settings.notifications && settings.systemAlerts) {
      addNotification({
        title: '시스템 알림',
        message: message.data.message,
        type: message.data.severity === 'critical' || message.data.severity === 'error' ? 'error' : 
              message.data.severity === 'warning' ? 'warning' : 'info'
      })
    }
  }, [addAlert, settings, addNotification])

  // WebSocket 연결 초기화
  const initializeWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect()
    }

    wsRef.current = createWatchHamsterWebSocket({
      onOpen: () => {
        console.log('WatchHamster WebSocket 연결됨')
        setConnected(true)
        setConnectionStatus('connected')
        setLastHeartbeat(new Date())
        clearErrors()
        
        addNotification({
          title: '연결됨',
          message: 'WatchHamster 시스템에 연결되었습니다',
          type: 'success'
        })
      },

      onClose: () => {
        console.log('WatchHamster WebSocket 연결 해제됨')
        setConnected(false)
        setConnectionStatus('disconnected')
        setLastHeartbeat(null)
      },

      onError: (error) => {
        console.error('WatchHamster WebSocket 오류:', error)
        setError('websocket', '웹소켓 연결 오류')
        setConnectionStatus('error')
        
        addNotification({
          title: '연결 오류',
          message: 'WatchHamster 시스템과의 연결에 문제가 발생했습니다',
          type: 'error'
        })
      },

      onReconnect: (attempt) => {
        console.log(`WatchHamster WebSocket 재연결 시도: ${attempt}`)
        setConnectionStatus('reconnecting')
        
        addNotification({
          title: '재연결 중',
          message: `연결을 복구하고 있습니다... (${attempt}번째 시도)`,
          type: 'info'
        })
      },

      onNewsUpdate: handleNewsUpdate,
      onServiceEvent: handleServiceEvent,
      onSystemMetrics: handleSystemMetrics,
      onLogUpdate: handleLogUpdate,
      onAlert: handleAlert
    })

    wsRef.current.connect()
  }, [
    setConnected,
    setConnectionStatus,
    setLastHeartbeat,
    setError,
    clearErrors,
    addNotification,
    handleNewsUpdate,
    handleServiceEvent,
    handleSystemMetrics,
    handleLogUpdate,
    handleAlert
  ])

  // 전체 데이터 새로고침
  const refreshAllData = useCallback(async () => {
    await Promise.all([
      fetchSystemStatus(),
      fetchServices(),
      fetchNewsStatus()
    ])
  }, [fetchSystemStatus, fetchServices, fetchNewsStatus])

  // 자동 새로고침 설정
  useEffect(() => {
    if (!settings.autoRefresh) return

    const interval = setInterval(() => {
      if (isConnected) {
        refreshAllData()
      }
    }, settings.refreshInterval)

    return () => clearInterval(interval)
  }, [settings.autoRefresh, settings.refreshInterval, isConnected, refreshAllData])

  // 컴포넌트 마운트 시 초기화
  useEffect(() => {
    // 초기 데이터 로드
    refreshAllData()
    
    // WebSocket 연결
    initializeWebSocket()

    return () => {
      // 정리
      if (wsRef.current) {
        wsRef.current.disconnect()
      }
    }
  }, []) // 의존성 배열을 비워서 마운트 시에만 실행

  // WebSocket 재연결
  const reconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.forceReconnect()
    } else {
      initializeWebSocket()
    }
  }, [initializeWebSocket])

  return {
    // 상태
    isConnected,
    connectionStatus,
    systemMetrics,
    services,
    newsStatus,
    loading,
    errors,

    // 시스템 제어
    startSystem,
    stopSystem,
    restartSystem,

    // 서비스 제어
    startService,
    stopService,
    restartService,

    // 뉴스 관리
    refreshNewsData,

    // 데이터 새로고침
    refreshAllData,
    fetchSystemStatus,
    fetchServices,
    fetchNewsStatus,

    // WebSocket 제어
    reconnectWebSocket,

    // WebSocket 인스턴스 (고급 사용)
    webSocket: wsRef.current
  }
}

export default useWatchHamsterSystem