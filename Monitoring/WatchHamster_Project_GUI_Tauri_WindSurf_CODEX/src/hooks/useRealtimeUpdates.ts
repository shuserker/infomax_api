/**
 * 실시간 업데이트 관리 훅
 * WebSocket을 통한 실시간 데이터 업데이트 처리
 */

import { useEffect, useCallback, useRef } from 'react'
import { useAppStore } from '../stores/useAppStore'
import { createWatchHamsterWebSocket } from '../services/websocket'
import type { WebSocketService } from '../services/websocket'

interface UseRealtimeUpdatesOptions {
  autoConnect?: boolean
  enableHeartbeat?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onConnectionChange?: (connected: boolean) => void
  onError?: (error: any) => void
}

export const useRealtimeUpdates = (options: UseRealtimeUpdatesOptions = {}) => {
  const {
    autoConnect = true,
    enableHeartbeat = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    onConnectionChange,
    onError
  } = options

  const wsRef = useRef<WebSocketService | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const {
    isConnected,
    setConnected,
    setConnectionStatus,
    setLastHeartbeat,
    updateSystemMetrics,
    updateServices,
    updateService,
    updateSingleNewsStatus,
    addLogEntry,
    addAlert,
    addNotification,
    setError,
    clearErrors
  } = useAppStore()

  // WebSocket 메시지 핸들러들
  const handleNewsUpdate = useCallback((data: any) => {
    const { news_type, status, last_update, processing_time } = data
    
    updateSingleNewsStatus(news_type, {
      status,
      last_update,
      ...(processing_time && { processing_time })
    })

    console.log(`뉴스 업데이트: ${news_type} - ${status}`)
  }, [updateSingleNewsStatus])

  const handleServiceEvent = useCallback((data: any) => {
    const { service_id, event_type, message } = data
    
    // 이벤트 타입에 따른 상태 매핑
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
    
    updateService(service_id, { 
      status: newStatus,
      ...(event_type === 'error' && { last_error: message })
    })

    console.log(`서비스 이벤트: ${service_id} - ${event_type}`)
  }, [updateService])

  const handleSystemMetrics = useCallback((data: any) => {
    updateSystemMetrics(data)
  }, [updateSystemMetrics])

  const handleLogUpdate = useCallback((data: any) => {
    addLogEntry(data)
    
    // 에러 로그인 경우 알림 생성
    if (data.level === 'ERROR') {
      addNotification({
        title: '시스템 오류',
        message: data.message,
        type: 'error'
      })
    }
  }, [addLogEntry, addNotification])

  const handleAlert = useCallback((data: any) => {
    addAlert({
      type: 'alert',
      data,
      timestamp: new Date().toISOString()
    })
    
    // 심각한 알림인 경우 브라우저 알림도 표시
    if (data.severity === 'critical' || data.severity === 'error') {
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('WatchHamster 시스템 알림', {
          body: data.message,
          icon: '/favicon.ico'
        })
      }
    }
  }, [addAlert])

  // WebSocket 연결 초기화
  const initializeWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect()
    }

    wsRef.current = createWatchHamsterWebSocket({
      onOpen: () => {
        console.log('실시간 업데이트 WebSocket 연결됨')
        setConnected(true)
        setConnectionStatus('connected')
        setLastHeartbeat(new Date())
        clearErrors()
        
        onConnectionChange?.(true)
        
        // 연결 후 모든 이벤트 구독
        wsRef.current?.subscribe('news_update', handleNewsUpdate)
        wsRef.current?.subscribe('service_event', handleServiceEvent)
        wsRef.current?.subscribe('system_metrics', handleSystemMetrics)
        wsRef.current?.subscribe('log_update', handleLogUpdate)
        wsRef.current?.subscribe('alert', handleAlert)
      },

      onClose: () => {
        console.log('실시간 업데이트 WebSocket 연결 해제됨')
        setConnected(false)
        setConnectionStatus('disconnected')
        setLastHeartbeat(null)
        
        onConnectionChange?.(false)
      },

      onError: (error) => {
        console.error('실시간 업데이트 WebSocket 오류:', error)
        setError('websocket', '실시간 연결 오류')
        setConnectionStatus('error')
        
        onError?.(error)
      },

      onReconnect: (attempt) => {
        console.log(`실시간 업데이트 재연결 시도: ${attempt}`)
        setConnectionStatus('reconnecting')
      },

      onMaxReconnectReached: () => {
        console.error('실시간 업데이트 최대 재연결 시도 횟수 초과')
        setError('websocket', '연결 복구 실패')
        setConnectionStatus('error')
      }
    })

    wsRef.current.connect()
  }, [
    setConnected,
    setConnectionStatus,
    setLastHeartbeat,
    setError,
    clearErrors,
    onConnectionChange,
    onError,
    handleNewsUpdate,
    handleServiceEvent,
    handleSystemMetrics,
    handleLogUpdate,
    handleAlert
  ])

  // WebSocket 연결
  const connect = useCallback(() => {
    if (wsRef.current?.isConnected()) {
      console.log('이미 연결되어 있습니다')
      return
    }
    
    initializeWebSocket()
  }, [initializeWebSocket])

  // WebSocket 연결 해제
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (wsRef.current) {
      wsRef.current.disconnect()
      wsRef.current = null
    }
    
    setConnected(false)
    setConnectionStatus('disconnected')
  }, [setConnected, setConnectionStatus])

  // 강제 재연결
  const forceReconnect = useCallback(() => {
    disconnect()
    setTimeout(() => {
      connect()
    }, 1000)
  }, [disconnect, connect])

  // 메시지 전송
  const sendMessage = useCallback((type: string, data: any) => {
    if (wsRef.current?.isConnected()) {
      return wsRef.current.send({ type, data })
    }
    
    console.warn('WebSocket이 연결되지 않았습니다')
    return false
  }, [])

  // 특정 이벤트 구독
  const subscribe = useCallback((eventType: string, callback: (data: any) => void) => {
    return wsRef.current?.subscribe(eventType, callback)
  }, [])

  // 특정 이벤트 구독 해제
  const unsubscribe = useCallback((eventType: string, callback: (data: any) => void) => {
    wsRef.current?.unsubscribe(eventType, callback)
  }, [])

  // 연결 상태 정보
  const getConnectionInfo = useCallback(() => {
    return wsRef.current?.getConnectionInfo() || {
      status: 'unknown',
      url: '',
      reconnectAttempts: 0,
      queuedMessages: 0,
      subscriptions: 0
    }
  }, [])

  // 컴포넌트 마운트 시 자동 연결
  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  return {
    // 상태
    isConnected,
    connectionInfo: getConnectionInfo(),

    // 연결 제어
    connect,
    disconnect,
    forceReconnect,

    // 메시지 및 구독
    sendMessage,
    subscribe,
    unsubscribe,

    // WebSocket 인스턴스 (고급 사용)
    webSocket: wsRef.current
  }
}

export default useRealtimeUpdates