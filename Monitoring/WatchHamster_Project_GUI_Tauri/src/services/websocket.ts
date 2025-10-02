/**
 * WebSocket 서비스 - 실시간 통신 관리
 * 
 * 이 파일은 WebSocket 연결을 관리하고 메시지 처리를 담당합니다.
 * 자동 재연결, 하트비트, 메시지 큐 등의 기능을 제공합니다.
 */

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
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

    // 일반 메시지 처리
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
    this.messageQueue.push(message)
    
    // 큐 크기 제한
    if (this.messageQueue.length > this.config.messageQueueSize) {
      this.messageQueue.shift()
    }
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

export default WebSocketService