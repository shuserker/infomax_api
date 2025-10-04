import { useState, useEffect, useRef, useCallback } from 'react'

// 메시지 타입 정의 강화
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
  id?: string
}

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

// 연결 상태 타입 정의
export type ConnectionStatus = 
  | 'connecting' 
  | 'connected' 
  | 'disconnected' 
  | 'reconnecting'
  | 'error' 
  | 'failed'

// 에러 타입 정의
export interface WebSocketError {
  type: 'connection' | 'message' | 'timeout' | 'unknown'
  message: string
  timestamp: string
  details?: any
}

export interface UseWebSocketOptions {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
  connectionTimeout?: number
  enableHeartbeat?: boolean
  enableReconnect?: boolean
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: (event: CloseEvent) => void
  onError?: (error: WebSocketError) => void
  onReconnecting?: (attempt: number) => void
  onMetricsUpdate?: (metrics: SystemMetrics) => void
  onServicesUpdate?: (services: ServiceInfo[]) => void
  onServiceEvent?: (event: any) => void
  onAlert?: (alert: any) => void
}

export const useWebSocket = ({
  url,
  reconnectInterval = 3000,
  maxReconnectAttempts = 10,
  heartbeatInterval = 30000,
  connectionTimeout = 10000,
  enableHeartbeat = true,
  enableReconnect = true,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  onReconnecting,
  onMetricsUpdate,
  onServicesUpdate,
  onServiceEvent,
  onAlert,
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')
  const [reconnectCount, setReconnectCount] = useState(0)
  const [lastHeartbeat, setLastHeartbeat] = useState<Date | null>(null)
  const [lastError, setLastError] = useState<WebSocketError | null>(null)
  const [messageQueue, setMessageQueue] = useState<WebSocketMessage[]>([])

  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeoutId = useRef<NodeJS.Timeout | null>(null)
  const heartbeatTimeoutId = useRef<NodeJS.Timeout | null>(null)
  const connectionTimeoutId = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const isManualDisconnect = useRef(false)
  const mountedRef = useRef(true)

  // 안전한 상태 업데이트 함수
  const safeSetState = useCallback((updater: () => void) => {
    if (mountedRef.current) {
      updater()
    }
  }, [])

  // 에러 생성 헬퍼
  const createError = useCallback((type: WebSocketError['type'], message: string, details?: any): WebSocketError => {
    return {
      type,
      message,
      timestamp: new Date().toISOString(),
      details,
    }
  }, [])

  // 메시지 전송 함수 개선
  const sendMessage = useCallback((message: any) => {
    const fullMessage: WebSocketMessage = {
      ...message,
      timestamp: message.timestamp || new Date().toISOString(),
      id: message.id || `msg_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
    }

    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      // 연결되지 않은 상태에서는 큐에 저장
      safeSetState(() => {
        setMessageQueue(prev => [...prev, fullMessage].slice(-50)) // 최대 50개 유지
      })
      
      if (!ws.current) {
        console.warn('WebSocket이 초기화되지 않았습니다.')
      }
      
      return false
    }

    try {
      ws.current.send(JSON.stringify(fullMessage))
      return true
    } catch (error) {
      const wsError = createError('message', '메시지 전송 실패', error)
      safeSetState(() => setLastError(wsError))
      onError?.(wsError)
      return false
    }
  }, [createError, safeSetState, onError])

  // 큐된 메시지 처리
  const processMessageQueue = useCallback(() => {
    if (messageQueue.length > 0 && ws.current?.readyState === WebSocket.OPEN) {
      const messagesToSend = [...messageQueue]
      safeSetState(() => setMessageQueue([]))
      
      messagesToSend.forEach(message => {
        try {
          ws.current!.send(JSON.stringify(message))
          console.log('큐된 메시지 전송 완료:', message.type)
        } catch (error) {
          console.error('큐된 메시지 전송 실패:', error)
          // 실패한 메시지를 다시 큐에 추가
          safeSetState(() => {
            setMessageQueue(prev => [message, ...prev])
          })
        }
      })
    }
  }, [messageQueue, safeSetState])

  const connect = useCallback(() => {
    // 기존 연결 정리
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }

    // 타이머 정리
    if (connectionTimeoutId.current) {
      clearTimeout(connectionTimeoutId.current)
      connectionTimeoutId.current = null
    }

    try {
      safeSetState(() => {
        setConnectionStatus('connecting')
        setLastError(null)
      })
      
      ws.current = new WebSocket(url)

      // 연결 타임아웃 설정
      connectionTimeoutId.current = setTimeout(() => {
        if (ws.current && ws.current.readyState === WebSocket.CONNECTING) {
          const error = createError('timeout', '연결 타임아웃')
          safeSetState(() => {
            setLastError(error)
            setConnectionStatus('error')
          })
          onError?.(error)
          ws.current.close()
        }
      }, connectionTimeout)

      ws.current.onopen = () => {
        // 연결 타임아웃 해제
        if (connectionTimeoutId.current) {
          clearTimeout(connectionTimeoutId.current)
          connectionTimeoutId.current = null
        }

        safeSetState(() => {
          setIsConnected(true)
          setConnectionStatus('connected')
          setLastHeartbeat(new Date())
          setLastError(null)
        })
        
        reconnectAttempts.current = 0
        setReconnectCount(0)
        isManualDisconnect.current = false

        // 큐된 메시지 처리
        processMessageQueue()

        // 연결 후 초기 상태 요청
        sendMessage({
          type: 'connection_established',
          data: { client_id: `client_${Date.now()}` },
        })

        sendMessage({
          type: 'request_status',
        })

        // 하트비트 시작
        if (enableHeartbeat) {
          startHeartbeat()
        }

        onConnect?.()
      }

      ws.current.onmessage = event => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          
          safeSetState(() => {
            setLastMessage(message)
            setLastHeartbeat(new Date())
            setLastError(null) // 메시지 수신 시 에러 상태 초기화
          })

          // 메시지 타입별 처리
          handleMessageByType(message)

          // 일반 메시지 콜백 호출
          onMessage?.(message)
        } catch (error) {
          const wsError = createError('message', '메시지 파싱 오류', { 
            rawData: event.data,
            parseError: error 
          })
          safeSetState(() => setLastError(wsError))
          onError?.(wsError)
          console.error('WebSocket 메시지 파싱 오류:', error)
        }
      }

      ws.current.onclose = (event: CloseEvent) => {
        // 연결 타임아웃 해제
        if (connectionTimeoutId.current) {
          clearTimeout(connectionTimeoutId.current)
          connectionTimeoutId.current = null
        }

        safeSetState(() => {
          setIsConnected(false)
          setConnectionStatus('disconnected')
          setLastHeartbeat(null)
        })

        // 하트비트 중지
        stopHeartbeat()

        onDisconnect?.(event)

        // 자동 재연결 시도 (수동 종료가 아니고 재연결이 활성화된 경우)
        if (!isManualDisconnect.current && 
            enableReconnect && 
            !event.wasClean && 
            reconnectAttempts.current < maxReconnectAttempts) {
          
          reconnectAttempts.current++
          safeSetState(() => {
            setReconnectCount(reconnectAttempts.current)
            setConnectionStatus('reconnecting')
          })

          console.log(`WebSocket 재연결 시도 ${reconnectAttempts.current}/${maxReconnectAttempts}`)
          
          onReconnecting?.(reconnectAttempts.current)

          // 지수 백오프로 재연결 시도
          const delay = Math.min(
            reconnectInterval * Math.pow(1.5, reconnectAttempts.current - 1),
            30000 // 최대 30초
          )

          reconnectTimeoutId.current = setTimeout(() => {
            if (mountedRef.current && !isManualDisconnect.current) {
              connect()
            }
          }, delay)
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          console.error('WebSocket 최대 재연결 시도 횟수 초과')
          const error = createError('connection', '최대 재연결 시도 횟수 초과')
          safeSetState(() => {
            setConnectionStatus('failed')
            setLastError(error)
          })
          onError?.(error)
        }
      }

      ws.current.onerror = (error: Event) => {
        const wsError = createError('connection', 'WebSocket 연결 오류', error)
        safeSetState(() => {
          setConnectionStatus('error')
          setLastError(wsError)
        })
        onError?.(wsError)
      }
    } catch (error) {
      setConnectionStatus('error')
      console.error('WebSocket 연결 오류:', error)
    }
  }, [url, reconnectInterval, maxReconnectAttempts, onMessage, onConnect, onDisconnect, onError])

  // 메시지 타입별 처리 함수
  const handleMessageByType = useCallback(
    (message: WebSocketMessage) => {
      switch (message.type) {
        case 'metrics_update':
          onMetricsUpdate?.(message.data as SystemMetrics)
          break

        case 'services_update':
          onServicesUpdate?.(message.data.services as ServiceInfo[])
          break

        case 'service_event':
          onServiceEvent?.(message.data)
          break

        case 'alert':
          onAlert?.(message.data)
          break

        case 'ping':
          // Ping에 대한 Pong 응답
          sendMessage({
            type: 'pong',
            timestamp: new Date().toISOString(),
          })
          break

        case 'connection_established':
          console.log('WebSocket 연결 확인:', message.data.message)
          break

        default:
          console.log('알 수 없는 메시지 타입:', message.type)
      }
    },
    [onMetricsUpdate, onServicesUpdate, onServiceEvent, onAlert, sendMessage]
  )

  // 하트비트 관리 개선
  const startHeartbeat = useCallback(() => {
    if (!enableHeartbeat) return
    
    stopHeartbeat() // 기존 하트비트 중지

    heartbeatTimeoutId.current = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        sendMessage({
          type: 'ping',
          data: { 
            client_time: new Date().toISOString(),
            connection_id: `conn_${Date.now()}`
          },
        })
      } else {
        // 연결이 끊어진 경우 하트비트 중지
        stopHeartbeat()
      }
    }, heartbeatInterval)
  }, [heartbeatInterval, enableHeartbeat, sendMessage])

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimeoutId.current) {
      clearInterval(heartbeatTimeoutId.current)
      heartbeatTimeoutId.current = null
    }
  }, [])

  // 모든 타이머 정리
  const clearAllTimers = useCallback(() => {
    if (reconnectTimeoutId.current) {
      clearTimeout(reconnectTimeoutId.current)
      reconnectTimeoutId.current = null
    }

    if (connectionTimeoutId.current) {
      clearTimeout(connectionTimeoutId.current)
      connectionTimeoutId.current = null
    }

    stopHeartbeat()
  }, [stopHeartbeat])

  const disconnect = useCallback(() => {
    isManualDisconnect.current = true
    clearAllTimers()

    if (ws.current) {
      // 정상 종료 코드로 연결 해제
      ws.current.close(1000, 'Manual disconnect')
      ws.current = null
    }

    safeSetState(() => {
      setIsConnected(false)
      setConnectionStatus('disconnected')
      setLastHeartbeat(null)
      setMessageQueue([]) // 큐 초기화
    })
    
    reconnectAttempts.current = 0
    setReconnectCount(0)
  }, [clearAllTimers, safeSetState])

  // 강제 재연결
  const forceReconnect = useCallback(() => {
    disconnect()
    setTimeout(() => {
      isManualDisconnect.current = false
      connect()
    }, 1000)
  }, [disconnect, connect])

  // 컴포넌트 마운트/언마운트 관리
  useEffect(() => {
    mountedRef.current = true
    // 자동 연결은 옵션으로 제어 (테스트에서는 수동 연결)
    // connect()

    return () => {
      mountedRef.current = false
      isManualDisconnect.current = true
      clearAllTimers()
      
      if (ws.current) {
        ws.current.close(1000, 'Component unmount')
        ws.current = null
      }
    }
  }, [clearAllTimers])

  // URL 변경 시 재연결
  useEffect(() => {
    if (isConnected) {
      forceReconnect()
    }
  }, [url, forceReconnect, isConnected])

  // 구독 관리 함수들
  const subscribe = useCallback(
    (subscriptionType: string, options: any = {}) => {
      return sendMessage({
        type: 'subscribe',
        data: {
          subscription: subscriptionType,
          options,
        },
      })
    },
    [sendMessage]
  )

  const unsubscribe = useCallback(
    (subscriptionType: string) => {
      return sendMessage({
        type: 'unsubscribe',
        data: {
          subscription: subscriptionType,
        },
      })
    },
    [sendMessage]
  )

  const requestStatus = useCallback(() => {
    return sendMessage({
      type: 'request_status',
      data: {
        request_time: new Date().toISOString(),
      },
    })
  }, [sendMessage])

  // 연결 상태 확인
  const checkConnection = useCallback(() => {
    return ws.current?.readyState === WebSocket.OPEN
  }, [])

  // 통계 정보
  const getConnectionStats = useCallback(() => {
    return {
      isConnected,
      connectionStatus,
      reconnectAttempts: reconnectAttempts.current,
      queuedMessages: messageQueue.length,
      lastHeartbeat,
      lastError,
    }
  }, [isConnected, connectionStatus, messageQueue.length, lastHeartbeat, lastError])

  return {
    // 연결 상태
    isConnected,
    connectionStatus,
    reconnectCount,
    lastHeartbeat,
    lastError,
    
    // 메시지 관련
    lastMessage,
    messageQueue,
    queuedMessageCount: messageQueue.length,
    
    // 연결 제어
    connect,
    disconnect,
    forceReconnect,
    
    // 메시지 전송
    sendMessage,
    
    // 구독 관리
    subscribe,
    unsubscribe,
    requestStatus,
    
    // 유틸리티
    checkConnection,
    getConnectionStats,
    
    // 상태 확인
    isConnecting: connectionStatus === 'connecting',
    isReconnecting: connectionStatus === 'reconnecting',
    hasError: connectionStatus === 'error' || connectionStatus === 'failed',
    canReconnect: enableReconnect && reconnectAttempts.current < maxReconnectAttempts,
  }
}
