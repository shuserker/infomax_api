/**
 * WebSocket 서비스 - 실시간 통신 관리
 * 
 * WatchHamster 시스템의 실시간 상태 업데이트를 위한 WebSocket 서비스
 * 뉴스 상태, 시스템 메트릭, 서비스 이벤트 등을 실시간으로 수신
 */

import type { NewsStatus, SystemMetrics, ServiceInfo, LogEntry } from '../types'

export interface WebSocketMessage {
  type: 'news_update' | 'service_event' | 'system_metrics' | 'log_update' | 'alert' | 'ping' | 'pong' | 'connection_established'
  data: any
  timestamp: string
}

// 뉴스 업데이트 메시지
export interface NewsUpdateMessage extends WebSocketMessage {
  type: 'news_update'
  data: {
    news_type: string
    status: string
    last_update: string
    processing_time?: number
  }
}

// 서비스 이벤트 메시지
export interface ServiceEventMessage extends WebSocketMessage {
  type: 'service_event'
  data: {
    service_id: string
    event_type: 'started' | 'stopped' | 'error' | 'restarted'
    message: string
    details?: any
  }
}

// 시스템 메트릭 메시지
export interface SystemMetricsMessage extends WebSocketMessage {
  type: 'system_metrics'
  data: SystemMetrics
}

// 로그 업데이트 메시지
export interface LogUpdateMessage extends WebSocketMessage {
  type: 'log_update'
  data: LogEntry
}

// 알림 메시지
export interface AlertMessage extends WebSocketMessage {
  type: 'alert'
  data: {
    alert_type: string
    message: string
    severity: 'info' | 'warning' | 'error' | 'critical'
    timestamp: string
  }
}

export interface WebSocketConfig {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
  messageQueueSize?: number
  connectionTimeout?: number
  enableHeartbeat?: boolean
  enableReconnect?: boolean
  enableMessageQueue?: boolean
}

export interface WebSocketEventHandlers {
  onOpen?: () => void
  onClose?: (event: CloseEvent) => void
  onError?: (error: Event) => void
  onMessage?: (message: WebSocketMessage) => void
  onNewsUpdate?: (message: NewsUpdateMessage) => void
  onServiceEvent?: (message: ServiceEventMessage) => void
  onSystemMetrics?: (message: SystemMetricsMessage) => void
  onLogUpdate?: (message: LogUpdateMessage) => void
  onAlert?: (message: AlertMessage) => void
  onReconnect?: (attempt: number) => void
  onMaxReconnectReached?: () => void
}

export class WebSocketService {
  private ws: WebSocket | null = null
  private config: Required<WebSocketConfig>
  private handlers: WebSocketEventHandlers
  private reconnectAttempts = 0
  private reconnectTimeoutId: any = null
  private heartbeatIntervalId: any = null
  private messageQueue: WebSocketMessage[] = []
  private isManualClose = false
  private eventSubscriptions: Map<string, Set<(data: any) => void>> = new Map()

  constructor(config: WebSocketConfig, handlers: WebSocketEventHandlers = {}) {
    this.config = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      messageQueueSize: 100,
      connectionTimeout: 10000,
      enableHeartbeat: true,
      enableReconnect: true,
      enableMessageQueue: true,
      ...config,
    }
    this.handlers = handlers
  }

  /**
   * 특정 이벤트 타입 구독
   */
  subscribe(eventType: string, callback: (data: any) => void): () => void {
    if (!this.eventSubscriptions.has(eventType)) {
      this.eventSubscriptions.set(eventType, new Set())
    }
    
    this.eventSubscriptions.get(eventType)!.add(callback)
    
    // 구독 해제 함수 반환
    return () => {
      this.unsubscribe(eventType, callback)
    }
  }

  /**
   * 특정 이벤트 타입 구독 해제
   */
  unsubscribe(eventType: string, callback: (data: any) => void): void {
    const subscribers = this.eventSubscriptions.get(eventType)
    if (subscribers) {
      subscribers.delete(callback)
      if (subscribers.size === 0) {
        this.eventSubscriptions.delete(eventType)
      }
    }
  }

  /**
   * 모든 구독 해제
   */
  unsubscribeAll(): void {
    this.eventSubscriptions.clear()
  }

  /**
   * 구독자들에게 이벤트 알림
   */
  private notifySubscribers(eventType: string, data: any): void {
    const subscribers = this.eventSubscriptions.get(eventType)
    if (subscribers) {
      subscribers.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`이벤트 구독자 콜백 오류 (${eventType}):`, error)
        }
      })
    }
  }

  /**
   * WebSocket 연결 시작
   */
  connect(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.warn('WebSocket이 이미 연결되어 있습니다.')
      return
    }

    try {
      this.ws = new WebSocket(this.config.url)
      this.setupEventListeners()
    } catch (error) {
      console.error('WebSocket 연결 실패:', error)
      this.handleReconnect()
    }
  }

  /**
   * WebSocket 연결 종료
   */
  disconnect(): void {
    this.isManualClose = true
    this.clearTimeouts()
    
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect')
      this.ws = null
    }
    
    this.reconnectAttempts = 0
    
    // 연결 종료 시 구독자들에게 알림
    this.notifySubscribers('connection_closed', { manual: true })
  }

  /**
   * 강제 재연결
   */
  forceReconnect(): void {
    console.log('강제 재연결 시도')
    this.reconnectAttempts = 0
    this.isManualClose = false
    
    if (this.ws) {
      this.ws.close(1000, 'Force reconnect')
    } else {
      this.connect()
    }
  }

  /**
   * 메시지 전송
   */
  send(message: Omit<WebSocketMessage, 'timestamp'>): boolean {
    const fullMessage: WebSocketMessage = {
      ...message,
      timestamp: new Date().toISOString(),
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(fullMessage))
        return true
      } catch (error) {
        console.error('메시지 전송 실패:', error)
        this.queueMessage(fullMessage)
        return false
      }
    } else {
      this.queueMessage(fullMessage)
      return false
    }
  }

  /**
   * 연결 상태 확인
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  /**
   * 연결 상태 반환
   */
  getReadyState(): number | null {
    return this.ws?.readyState ?? null
  }

  /**
   * 재연결 시도 횟수 반환
   */
  getReconnectAttempts(): number {
    return this.reconnectAttempts
  }

  /**
   * 연결 상태 문자열 반환
   */
  getConnectionStatus(): 'connecting' | 'connected' | 'closing' | 'closed' | 'unknown' {
    switch (this.ws?.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting'
      case WebSocket.OPEN:
        return 'connected'
      case WebSocket.CLOSING:
        return 'closing'
      case WebSocket.CLOSED:
        return 'closed'
      default:
        return 'unknown'
    }
  }

  /**
   * 연결 정보 반환
   */
  getConnectionInfo(): {
    status: string
    url: string
    reconnectAttempts: number
    queuedMessages: number
    subscriptions: number
  } {
    return {
      status: this.getConnectionStatus(),
      url: this.config.url,
      reconnectAttempts: this.reconnectAttempts,
      queuedMessages: this.messageQueue.length,
      subscriptions: Array.from(this.eventSubscriptions.values()).reduce((total, set) => total + set.size, 0)
    }
  }

  /**
   * 이벤트 리스너 설정
   */
  private setupEventListeners(): void {
    if (!this.ws) return

    this.ws.onopen = () => {
      console.log('WebSocket 연결됨:', this.config.url)
      this.reconnectAttempts = 0
      this.isManualClose = false
      this.startHeartbeat()
      this.processMessageQueue()
      this.handlers.onOpen?.()
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket 연결 종료:', event.code, event.reason)
      this.stopHeartbeat()
      this.handlers.onClose?.(event)

      if (!this.isManualClose && !event.wasClean) {
        this.handleReconnect()
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket 오류:', error)
      this.handlers.onError?.(error)
    }

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('메시지 파싱 오류:', error, event.data)
      }
    }
  }

  /**
   * 메시지 처리
   */
  private handleMessage(message: WebSocketMessage): void {
    // 하트비트 응답 처리
    if (message.type === 'pong') {
      console.debug('하트비트 응답 수신')
      return
    }

    // 타입별 메시지 처리
    switch (message.type) {
      case 'news_update':
        console.log('뉴스 업데이트 수신:', message.data)
        this.handlers.onNewsUpdate?.(message as NewsUpdateMessage)
        this.notifySubscribers('news_update', message.data)
        break
        
      case 'service_event':
        console.log('서비스 이벤트 수신:', message.data)
        this.handlers.onServiceEvent?.(message as ServiceEventMessage)
        this.notifySubscribers('service_event', message.data)
        break
        
      case 'system_metrics':
        console.debug('시스템 메트릭 수신')
        this.handlers.onSystemMetrics?.(message as SystemMetricsMessage)
        this.notifySubscribers('system_metrics', message.data)
        break
        
      case 'log_update':
        console.debug('로그 업데이트 수신')
        this.handlers.onLogUpdate?.(message as LogUpdateMessage)
        this.notifySubscribers('log_update', message.data)
        break
        
      case 'alert':
        console.warn('알림 수신:', message.data)
        this.handlers.onAlert?.(message as AlertMessage)
        this.notifySubscribers('alert', message.data)
        break
        
      case 'connection_established':
        console.log('WebSocket 연결 확인됨')
        this.notifySubscribers('connection_established', message.data)
        break
        
      default:
        console.debug('알 수 없는 메시지 타입:', message.type)
        this.notifySubscribers(message.type, message.data)
    }

    // 일반 메시지 핸들러도 호출
    this.handlers.onMessage?.(message)
  }

  /**
   * 재연결 처리
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('최대 재연결 시도 횟수 초과')
      this.handlers.onMaxReconnectReached?.()
      return
    }

    this.reconnectAttempts++
    const delay = this.config.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1)
    
    console.log(`WebSocket 재연결 시도 ${this.reconnectAttempts}/${this.config.maxReconnectAttempts} (${delay}ms 후)`)
    
    this.reconnectTimeoutId = setTimeout(() => {
      this.handlers.onReconnect?.(this.reconnectAttempts)
      this.connect()
    }, delay)
  }

  /**
   * 하트비트 시작
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()
    
    this.heartbeatIntervalId = setInterval(() => {
      if (this.isConnected()) {
        this.send({
          type: 'ping',
          data: { timestamp: new Date().toISOString() },
        })
      }
    }, this.config.heartbeatInterval)
  }

  /**
   * 하트비트 중지
   */
  private stopHeartbeat(): void {
    if (this.heartbeatIntervalId) {
      clearInterval(this.heartbeatIntervalId)
      this.heartbeatIntervalId = null
    }
  }

  /**
   * 메시지 큐에 추가
   */
  private queueMessage(message: WebSocketMessage): void {
    if (!this.config.enableMessageQueue) {
      console.warn('메시지 큐가 비활성화되어 메시지를 삭제합니다:', message)
      return
    }

    // 중복 메시지 방지 (같은 타입의 최근 메시지만 유지)
    if (message.type === 'ping' || message.type === 'heartbeat') {
      // 하트비트 메시지는 큐에 저장하지 않음
      return
    }

    // 우선순위가 높은 메시지 타입 정의
    const highPriorityTypes = ['service_event', 'alert', 'error']
    const isHighPriority = highPriorityTypes.includes(message.type)

    if (isHighPriority) {
      // 우선순위 높은 메시지는 앞쪽에 추가
      this.messageQueue.unshift(message)
    } else {
      // 일반 메시지는 뒤쪽에 추가
      this.messageQueue.push(message)
    }
    
    // 큐 크기 제한 (우선순위 낮은 메시지부터 제거)
    while (this.messageQueue.length > this.config.messageQueueSize) {
      // 우선순위 낮은 메시지 찾아서 제거
      let removedLowPriority = false
      for (let i = this.messageQueue.length - 1; i >= 0; i--) {
        if (!highPriorityTypes.includes(this.messageQueue[i].type)) {
          this.messageQueue.splice(i, 1)
          removedLowPriority = true
          break
        }
      }
      
      // 우선순위 낮은 메시지가 없으면 가장 오래된 메시지 제거
      if (!removedLowPriority) {
        this.messageQueue.shift()
      }
    }

    console.debug(`메시지 큐에 추가됨 (${this.messageQueue.length}/${this.config.messageQueueSize}):`, message.type)
  }

  /**
   * 큐된 메시지 처리
   */
  private processMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift()
      if (message) {
        try {
          this.ws!.send(JSON.stringify(message))
        } catch (error) {
          console.error('큐된 메시지 전송 실패:', error)
          // 실패한 메시지를 다시 큐에 추가
          this.messageQueue.unshift(message)
          break
        }
      }
    }
  }

  /**
   * 타임아웃 정리
   */
  private clearTimeouts(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId)
      this.reconnectTimeoutId = null
    }
    
    this.stopHeartbeat()
  }
}

/**
 * WebSocket 서비스 팩토리 함수
 */
export const createWebSocketService = (
  config: WebSocketConfig,
  handlers: WebSocketEventHandlers = {}
): WebSocketService => {
  return new WebSocketService(config, handlers)
}

/**
 * WatchHamster 전용 WebSocket 서비스 생성
 */
export const createWatchHamsterWebSocket = (
  handlers: WebSocketEventHandlers = {}
): WebSocketService => {
  const config: WebSocketConfig = {
    url: getWebSocketUrl('/ws'),
    reconnectInterval: 3000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,
    messageQueueSize: 100,
    enableHeartbeat: true,
    enableReconnect: true,
    enableMessageQueue: true
  }
  
  return new WebSocketService(config, handlers)
}

/**
 * 기본 WebSocket URL 생성
 */
export const getWebSocketUrl = (path: string = '/ws', secure: boolean = false): string => {
  const protocol = secure ? 'wss:' : 'ws:'
  const host = window.location.hostname
  const port = import.meta.env.VITE_BACKEND_PORT || '8000'
  
  return `${protocol}//${host}:${port}${path}`
}

/**
 * WebSocket 연결 상태 문자열 변환
 */
export const getReadyStateString = (readyState: number | null): string => {
  switch (readyState) {
    case WebSocket.CONNECTING:
      return 'connecting'
    case WebSocket.OPEN:
      return 'connected'
    case WebSocket.CLOSING:
      return 'closing'
    case WebSocket.CLOSED:
      return 'closed'
    default:
      return 'unknown'
  }
}

/**
 * WebSocket 메시지 검증
 */
export const validateWebSocketMessage = (data: any): WebSocketMessage | null => {
  try {
    if (typeof data === 'string') {
      data = JSON.parse(data)
    }
    
    if (!data || typeof data !== 'object') {
      return null
    }
    
    if (!data.type || !data.timestamp) {
      return null
    }
    
    return data as WebSocketMessage
  } catch (error) {
    console.error('WebSocket 메시지 검증 실패:', error)
    return null
  }
}

export default WebSocketService