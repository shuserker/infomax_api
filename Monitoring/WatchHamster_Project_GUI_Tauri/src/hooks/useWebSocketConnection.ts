/**
 * WebSocket 연결 관리 훅
 * 
 * 이 훅은 WebSocket 연결의 생명주기를 관리하고
 * 연결 상태, 재연결, 메시지 전송 등의 기능을 제공합니다.
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { WebSocketService, WebSocketMessage, getWebSocketUrl, getReadyStateString } from '../services/websocket'

export interface UseWebSocketConnectionOptions {
  url?: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
  autoConnect?: boolean
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: (event: CloseEvent) => void
  onError?: (error: Event) => void
  onReconnecting?: (attempt: number) => void
}

export interface WebSocketConnectionState {
  isConnected: boolean
  connectionStatus: string
  reconnectAttempts: number
  lastError: Event | null
  lastMessage: WebSocketMessage | null
}

export const useWebSocketConnection = (options: UseWebSocketConnectionOptions = {}) => {
  const {
    url = getWebSocketUrl(),
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    heartbeatInterval = 30000,
    autoConnect = true,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    onReconnecting,
  } = options

  // 상태 관리
  const [state, setState] = useState<WebSocketConnectionState>({
    isConnected: false,
    connectionStatus: 'disconnected',
    reconnectAttempts: 0,
    lastError: null,
    lastMessage: null,
  })

  // WebSocket 서비스 인스턴스
  const wsService = useRef<WebSocketService | null>(null)
  const mountedRef = useRef(true)

  // 상태 업데이트 헬퍼
  const updateState = useCallback((updates: Partial<WebSocketConnectionState>) => {
    if (mountedRef.current) {
      setState(prev => ({ ...prev, ...updates }))
    }
  }, [])

  // WebSocket 서비스 초기화
  const initializeWebSocket = useCallback(() => {
    if (wsService.current) {
      wsService.current.disconnect()
    }

    wsService.current = new WebSocketService(
      {
        url,
        reconnectInterval,
        maxReconnectAttempts,
        heartbeatInterval,
      },
      {
        onOpen: () => {
          updateState({
            isConnected: true,
            connectionStatus: 'connected',
            reconnectAttempts: 0,
            lastError: null,
          })
          onConnect?.()
        },

        onClose: (event) => {
          updateState({
            isConnected: false,
            connectionStatus: event.wasClean ? 'disconnected' : 'error',
          })
          onDisconnect?.(event)
        },

        onError: (error) => {
          updateState({
            lastError: error,
            connectionStatus: 'error',
          })
          onError?.(error)
        },

        onMessage: (message) => {
          updateState({
            lastMessage: message,
          })
          onMessage?.(message)
        },

        onReconnect: (attempt) => {
          updateState({
            reconnectAttempts: attempt,
            connectionStatus: 'reconnecting',
          })
          onReconnecting?.(attempt)
        },

        onMaxReconnectReached: () => {
          updateState({
            connectionStatus: 'failed',
          })
        },
      }
    )
  }, [
    url,
    reconnectInterval,
    maxReconnectAttempts,
    heartbeatInterval,
    updateState,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
    onReconnecting,
  ])

  // 연결 함수
  const connect = useCallback(() => {
    if (!wsService.current) {
      initializeWebSocket()
    }
    
    updateState({ connectionStatus: 'connecting' })
    wsService.current?.connect()
  }, [initializeWebSocket, updateState])

  // 연결 해제 함수
  const disconnect = useCallback(() => {
    wsService.current?.disconnect()
    updateState({
      isConnected: false,
      connectionStatus: 'disconnected',
      reconnectAttempts: 0,
    })
  }, [updateState])

  // 메시지 전송 함수
  const sendMessage = useCallback((type: string, data: any = {}) => {
    if (!wsService.current) {
      console.warn('WebSocket 서비스가 초기화되지 않았습니다.')
      return false
    }

    return wsService.current.send({ type, data })
  }, [])

  // 연결 상태 확인 함수
  const checkConnection = useCallback(() => {
    if (!wsService.current) return false
    
    const isConnected = wsService.current.isConnected()
    const readyState = wsService.current.getReadyState()
    const connectionStatus = getReadyStateString(readyState)
    
    updateState({
      isConnected,
      connectionStatus,
    })
    
    return isConnected
  }, [updateState])

  // 재연결 함수
  const reconnect = useCallback(() => {
    disconnect()
    setTimeout(() => {
      connect()
    }, 1000)
  }, [connect, disconnect])

  // 구독 함수
  const subscribe = useCallback((subscriptionType: string, options: any = {}) => {
    return sendMessage('subscribe', {
      subscription: subscriptionType,
      options,
    })
  }, [sendMessage])

  // 구독 해제 함수
  const unsubscribe = useCallback((subscriptionType: string) => {
    return sendMessage('unsubscribe', {
      subscription: subscriptionType,
    })
  }, [sendMessage])

  // 상태 요청 함수
  const requestStatus = useCallback(() => {
    return sendMessage('request_status')
  }, [sendMessage])

  // 자동 연결
  useEffect(() => {
    if (autoConnect) {
      initializeWebSocket()
      connect()
    }

    return () => {
      mountedRef.current = false
      wsService.current?.disconnect()
    }
  }, [autoConnect, initializeWebSocket, connect])

  // URL 변경 시 재연결
  useEffect(() => {
    if (wsService.current && state.isConnected) {
      reconnect()
    }
  }, [url, reconnect, state.isConnected])

  return {
    // 상태
    ...state,
    
    // 연결 제어
    connect,
    disconnect,
    reconnect,
    checkConnection,
    
    // 메시지 전송
    sendMessage,
    
    // 구독 관리
    subscribe,
    unsubscribe,
    requestStatus,
    
    // 유틸리티
    isReconnecting: state.connectionStatus === 'reconnecting',
    isConnecting: state.connectionStatus === 'connecting',
    hasError: state.connectionStatus === 'error' || state.connectionStatus === 'failed',
  }
}

export default useWebSocketConnection