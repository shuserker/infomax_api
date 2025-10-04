# WebSocket API 문서

## 개요

WatchHamster Tauri 백엔드는 실시간 양방향 통신을 위한 WebSocket API를 제공합니다. 클라이언트는 WebSocket을 통해 시스템 상태 변화를 실시간으로 수신하고, 서버에 명령을 전송할 수 있습니다.

## 연결 정보

- **WebSocket URL**: `ws://localhost:8000/ws`
- **프로토콜**: WebSocket (RFC 6455)
- **인코딩**: UTF-8 JSON

## 연결 설정

### JavaScript 클라이언트 예시

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('WebSocket 연결 성공');
    
    // 연결 후 클라이언트 정보 전송
    ws.send(JSON.stringify({
        type: 'client_info',
        data: {
            client_id: 'dashboard_client_1',
            user_agent: navigator.userAgent,
            timestamp: new Date().toISOString()
        }
    }));
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    handleWebSocketMessage(message);
};

ws.onclose = function(event) {
    console.log('WebSocket 연결 종료:', event.code, event.reason);
    // 자동 재연결 로직
    setTimeout(() => {
        connectWebSocket();
    }, 5000);
};

ws.onerror = function(error) {
    console.error('WebSocket 오류:', error);
};
```

### Python 클라이언트 예시

```python
import asyncio
import json
import websockets

async def websocket_client():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # 클라이언트 정보 전송
        client_info = {
            "type": "client_info",
            "data": {
                "client_id": "python_client_1",
                "user_agent": "Python WebSocket Client",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
        await websocket.send(json.dumps(client_info))
        
        # 메시지 수신 루프
        async for message in websocket:
            data = json.loads(message)
            print(f"수신된 메시지: {data}")

# 실행
asyncio.run(websocket_client())
```

## 메시지 포맷

모든 WebSocket 메시지는 다음 기본 구조를 따릅니다:

```json
{
    "type": "메시지_타입",
    "data": {
        // 메시지별 데이터
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "client_id": "클라이언트_식별자"
}
```

### 필수 필드

- **type** (string): 메시지 타입 식별자
- **data** (object): 메시지별 데이터 페이로드
- **timestamp** (string): ISO 8601 형식의 타임스탬프

### 선택적 필드

- **client_id** (string): 클라이언트 식별자 (클라이언트 → 서버)
- **broadcast_id** (string): 브로드캐스트 메시지 식별자 (서버 → 클라이언트)

## 서버 → 클라이언트 메시지

### 1. 시스템 상태 업데이트 (status_update)

시스템 메트릭이나 서비스 상태가 변경될 때 전송됩니다.

```json
{
    "type": "status_update",
    "data": {
        "cpu_percent": 45.2,
        "memory_percent": 67.8,
        "disk_usage": 23.4,
        "network_status": "connected",
        "uptime": 86400,
        "active_services": 6
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "broadcast_id": "status_001"
}
```

### 2. 서비스 이벤트 (service_event)

서비스 시작, 중지, 오류 등의 이벤트가 발생할 때 전송됩니다.

```json
{
    "type": "service_event",
    "data": {
        "service_id": "posco_news",
        "service_name": "POSCO 뉴스 모니터",
        "event_type": "started",
        "status": "running",
        "message": "서비스가 성공적으로 시작되었습니다",
        "details": {
            "pid": 12345,
            "port": 8080,
            "config_file": "/path/to/config.json"
        }
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "broadcast_id": "service_001"
}
```

**event_type 값:**
- `started`: 서비스 시작
- `stopped`: 서비스 중지
- `restarted`: 서비스 재시작
- `error`: 서비스 오류
- `recovered`: 서비스 복구
- `config_changed`: 설정 변경

### 3. 시스템 알림 (alert)

중요한 시스템 이벤트나 경고가 발생할 때 전송됩니다.

```json
{
    "type": "alert",
    "data": {
        "level": "warning",
        "title": "높은 CPU 사용률 감지",
        "message": "CPU 사용률이 90%를 초과했습니다",
        "category": "performance",
        "source": "system_monitor",
        "actions": [
            {
                "label": "프로세스 확인",
                "action": "view_processes"
            },
            {
                "label": "알림 끄기",
                "action": "dismiss_alert"
            }
        ],
        "metadata": {
            "cpu_percent": 92.5,
            "threshold": 90.0,
            "duration": 300
        }
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "broadcast_id": "alert_001"
}
```

**alert level 값:**
- `info`: 정보성 알림
- `warning`: 경고
- `error`: 오류
- `critical`: 심각한 오류

### 4. 로그 업데이트 (log_update)

새로운 로그 엔트리가 생성될 때 전송됩니다.

```json
{
    "type": "log_update",
    "data": {
        "file_name": "watchhamster.log",
        "entries": [
            {
                "timestamp": "2024-01-01T12:00:00Z",
                "level": "INFO",
                "logger_name": "watchhamster.services",
                "message": "POSCO 뉴스 서비스 시작됨",
                "module": "posco_news.py",
                "line_number": 45,
                "thread_id": "MainThread"
            }
        ],
        "total_new_entries": 1
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "broadcast_id": "log_001"
}
```

### 5. 웹훅 이벤트 (webhook_event)

웹훅 전송 결과나 상태가 업데이트될 때 전송됩니다.

```json
{
    "type": "webhook_event",
    "data": {
        "webhook_id": "webhook_001",
        "event_type": "sent",
        "webhook_type": "discord",
        "url": "https://discord.com/api/webhooks/...",
        "status": "success",
        "response_code": 200,
        "message": "웹훅이 성공적으로 전송되었습니다",
        "sent_at": "2024-01-01T12:00:00Z",
        "response_time_ms": 245
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "broadcast_id": "webhook_001"
}
```

### 6. POSCO 시스템 이벤트 (posco_event)

POSCO 시스템 관련 이벤트가 발생할 때 전송됩니다.

```json
{
    "type": "posco_event",
    "data": {
        "event_type": "deployment_started",
        "branch": "main",
        "commit_hash": "abc123def456",
        "deployment_id": "deploy_001",
        "status": "in_progress",
        "progress": 25,
        "message": "배포가 시작되었습니다",
        "steps": [
            {
                "name": "코드 체크아웃",
                "status": "completed",
                "duration_ms": 1500
            },
            {
                "name": "의존성 설치",
                "status": "in_progress",
                "progress": 60
            },
            {
                "name": "빌드",
                "status": "pending"
            }
        ]
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "broadcast_id": "posco_001"
}
```

### 7. 연결 상태 (connection_status)

WebSocket 연결 상태나 서버 정보를 전송합니다.

```json
{
    "type": "connection_status",
    "data": {
        "status": "connected",
        "server_version": "1.0.0",
        "server_time": "2024-01-01T12:00:00Z",
        "client_count": 3,
        "uptime_seconds": 86400,
        "features": [
            "real_time_metrics",
            "log_streaming",
            "webhook_notifications",
            "posco_integration"
        ]
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "broadcast_id": "connection_001"
}
```

## 클라이언트 → 서버 메시지

### 1. 클라이언트 정보 (client_info)

클라이언트가 연결 후 자신의 정보를 서버에 전송합니다.

```json
{
    "type": "client_info",
    "data": {
        "client_id": "dashboard_client_1",
        "client_type": "web_dashboard",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "screen_resolution": "1920x1080",
        "timezone": "Asia/Seoul",
        "language": "ko-KR",
        "features": [
            "real_time_updates",
            "log_streaming",
            "service_control"
        ]
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 구독 요청 (subscribe)

특정 이벤트 타입에 대한 구독을 요청합니다.

```json
{
    "type": "subscribe",
    "data": {
        "event_types": [
            "status_update",
            "service_event",
            "alert"
        ],
        "filters": {
            "service_ids": ["posco_news", "github_pages"],
            "alert_levels": ["warning", "error", "critical"],
            "log_levels": ["INFO", "WARNING", "ERROR"]
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3. 구독 해제 (unsubscribe)

특정 이벤트 타입에 대한 구독을 해제합니다.

```json
{
    "type": "unsubscribe",
    "data": {
        "event_types": [
            "log_update"
        ]
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. 서비스 제어 (service_control)

서비스 시작/중지/재시작을 요청합니다.

```json
{
    "type": "service_control",
    "data": {
        "service_id": "posco_news",
        "action": "restart",
        "options": {
            "force": false,
            "timeout": 30
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**action 값:**
- `start`: 서비스 시작
- `stop`: 서비스 중지
- `restart`: 서비스 재시작
- `status`: 서비스 상태 조회

### 5. 웹훅 전송 (send_webhook)

웹훅 전송을 요청합니다.

```json
{
    "type": "send_webhook",
    "data": {
        "webhook_type": "discord",
        "url": "https://discord.com/api/webhooks/...",
        "message": "테스트 메시지",
        "template_id": "posco_news_alert",
        "variables": {
            "title": "뉴스 제목",
            "url": "https://example.com",
            "timestamp": "2024-01-01 12:00:00"
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 6. 핑 (ping)

연결 상태 확인을 위한 핑 메시지입니다.

```json
{
    "type": "ping",
    "data": {
        "client_time": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

서버는 다음과 같이 응답합니다:

```json
{
    "type": "pong",
    "data": {
        "client_time": "2024-01-01T12:00:00Z",
        "server_time": "2024-01-01T12:00:00.123Z",
        "latency_ms": 123
    },
    "timestamp": "2024-01-01T12:00:00.123Z"
}
```

## 오류 처리

### 오류 메시지 포맷

```json
{
    "type": "error",
    "data": {
        "error_code": "INVALID_MESSAGE_FORMAT",
        "error_message": "메시지 형식이 올바르지 않습니다",
        "details": {
            "expected_fields": ["type", "data"],
            "received_message": "원본 메시지 내용"
        },
        "timestamp": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 일반적인 오류 코드

- `INVALID_MESSAGE_FORMAT`: 메시지 형식 오류
- `UNKNOWN_MESSAGE_TYPE`: 알 수 없는 메시지 타입
- `AUTHENTICATION_REQUIRED`: 인증 필요
- `PERMISSION_DENIED`: 권한 부족
- `SERVICE_NOT_FOUND`: 서비스를 찾을 수 없음
- `INTERNAL_SERVER_ERROR`: 내부 서버 오류
- `RATE_LIMIT_EXCEEDED`: 요청 빈도 제한 초과

## 연결 관리

### 자동 재연결

클라이언트는 연결이 끊어졌을 때 자동으로 재연결을 시도해야 합니다:

```javascript
class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
        this.connect();
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('WebSocket 연결 성공');
            this.reconnectAttempts = 0;
            this.sendClientInfo();
        };
        
        this.ws.onclose = (event) => {
            console.log('WebSocket 연결 종료:', event.code);
            this.handleReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket 오류:', error);
        };
        
        this.ws.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };
    }
    
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('최대 재연결 시도 횟수 초과');
        }
    }
    
    sendClientInfo() {
        const clientInfo = {
            type: 'client_info',
            data: {
                client_id: 'dashboard_client_1',
                client_type: 'web_dashboard',
                user_agent: navigator.userAgent,
                timestamp: new Date().toISOString()
            }
        };
        
        this.send(clientInfo);
    }
    
    send(message) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket이 연결되지 않음');
        }
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'status_update':
                this.handleStatusUpdate(message.data);
                break;
            case 'service_event':
                this.handleServiceEvent(message.data);
                break;
            case 'alert':
                this.handleAlert(message.data);
                break;
            case 'pong':
                this.handlePong(message.data);
                break;
            default:
                console.log('알 수 없는 메시지 타입:', message.type);
        }
    }
}

// 사용 예시
const wsManager = new WebSocketManager('ws://localhost:8000/ws');
```

### 하트비트

연결 상태를 유지하기 위해 주기적으로 핑을 전송합니다:

```javascript
setInterval(() => {
    wsManager.send({
        type: 'ping',
        data: {
            client_time: new Date().toISOString()
        }
    });
}, 30000); // 30초마다 핑 전송
```

## 성능 고려사항

### 메시지 크기 제한

- 최대 메시지 크기: 1MB
- 권장 메시지 크기: 64KB 이하
- 대용량 데이터는 HTTP API 사용 권장

### 연결 제한

- 클라이언트당 최대 연결 수: 5개
- 서버 전체 최대 연결 수: 1000개
- 비활성 연결 타임아웃: 5분

### 메시지 빈도 제한

- 클라이언트당 초당 최대 메시지 수: 10개
- 서버 브로드캐스트 빈도: 초당 5회

## 보안 고려사항

### 메시지 검증

모든 수신 메시지는 다음과 같이 검증됩니다:

1. JSON 형식 유효성 검사
2. 필수 필드 존재 확인
3. 데이터 타입 검증
4. 메시지 크기 제한 확인
5. 권한 검사 (해당하는 경우)

### 연결 보안

- 프로덕션 환경에서는 WSS (WebSocket Secure) 사용 권장
- 적절한 인증 메커니즘 구현 필요
- CORS 정책 적용
- 레이트 리미팅 구현

## 디버깅 및 모니터링

### 로깅

WebSocket 관련 모든 이벤트는 로그에 기록됩니다:

```
2024-01-01 12:00:00 [INFO] WebSocket 클라이언트 연결: 192.168.1.100
2024-01-01 12:00:01 [INFO] 클라이언트 정보 수신: dashboard_client_1
2024-01-01 12:00:02 [INFO] 구독 요청: status_update, service_event
2024-01-01 12:00:03 [INFO] 상태 업데이트 브로드캐스트: 3개 클라이언트
```

### 모니터링 메트릭

- 활성 연결 수
- 메시지 전송/수신 통계
- 오류 발생 빈도
- 평균 응답 시간
- 연결 지속 시간

### 디버그 도구

개발 모드에서는 WebSocket 디버그 정보를 제공합니다:

```javascript
// 디버그 모드 활성화
wsManager.enableDebug = true;

// 연결 상태 확인
console.log(wsManager.getConnectionStatus());

// 메시지 히스토리 확인
console.log(wsManager.getMessageHistory());
```

## 예제 및 사용 사례

### React 컴포넌트에서 WebSocket 사용

```jsx
import { useEffect, useState } from 'react';

function useWebSocket(url) {
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    
    useEffect(() => {
        const ws = new WebSocket(url);
        
        ws.onopen = () => {
            setIsConnected(true);
            setSocket(ws);
            
            // 클라이언트 정보 전송
            ws.send(JSON.stringify({
                type: 'client_info',
                data: {
                    client_id: 'react_dashboard',
                    client_type: 'web_dashboard',
                    timestamp: new Date().toISOString()
                }
            }));
        };
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            setLastMessage(message);
        };
        
        ws.onclose = () => {
            setIsConnected(false);
            setSocket(null);
        };
        
        return () => {
            ws.close();
        };
    }, [url]);
    
    const sendMessage = (message) => {
        if (socket && isConnected) {
            socket.send(JSON.stringify(message));
        }
    };
    
    return { socket, isConnected, lastMessage, sendMessage };
}

// 사용 예시
function Dashboard() {
    const { isConnected, lastMessage, sendMessage } = useWebSocket('ws://localhost:8000/ws');
    const [systemMetrics, setSystemMetrics] = useState({});
    
    useEffect(() => {
        if (lastMessage?.type === 'status_update') {
            setSystemMetrics(lastMessage.data);
        }
    }, [lastMessage]);
    
    const restartService = (serviceId) => {
        sendMessage({
            type: 'service_control',
            data: {
                service_id: serviceId,
                action: 'restart'
            }
        });
    };
    
    return (
        <div>
            <div>연결 상태: {isConnected ? '연결됨' : '연결 안됨'}</div>
            <div>CPU: {systemMetrics.cpu_percent}%</div>
            <div>메모리: {systemMetrics.memory_percent}%</div>
            <button onClick={() => restartService('posco_news')}>
                POSCO 뉴스 재시작
            </button>
        </div>
    );
}
```

이 문서는 WatchHamster Tauri 백엔드의 WebSocket API에 대한 완전한 참조 가이드입니다. 추가 질문이나 기능 요청이 있으시면 개발팀에 문의하시기 바랍니다.