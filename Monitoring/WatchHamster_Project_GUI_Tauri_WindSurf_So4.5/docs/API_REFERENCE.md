# WatchHamster Tauri Backend API 참조 문서

## 개요

WatchHamster Tauri 백엔드는 FastAPI 기반의 REST API 서비스로, 기존 Python 로직을 웹 서비스로 포팅하여 현대적인 UI와 연동할 수 있도록 합니다.

### 서비스 정보
- **Base URL**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc 문서**: `http://localhost:8000/redoc` (ReDoc)
- **WebSocket**: `ws://localhost:8000/ws`
- **버전**: v1.0.0
- **프레임워크**: FastAPI 0.104.1+
- **Python 버전**: 3.8+

### 주요 기능
- 🔧 **서비스 관리**: POSCO 뉴스, GitHub Pages, 캐시 모니터 등 서비스 제어
- 📊 **실시간 모니터링**: 시스템 메트릭 및 성능 데이터 실시간 수집
- 🔔 **웹훅 시스템**: Discord/Slack 알림 및 메시지 템플릿 관리
- 📝 **로그 관리**: 실시간 로그 스트리밍 및 검색 기능
- 🚀 **POSCO 시스템**: 배포, 브랜치 전환, Git 관리 기능
- 🌐 **WebSocket**: 실시간 양방향 통신 지원

### 기술 스택
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **WebSocket**: 실시간 데이터 통신
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버

## 인증 및 보안

### 현재 상태
현재 버전에서는 개발 환경을 위해 인증이 비활성화되어 있습니다.

### 프로덕션 고려사항
프로덕션 환경에서는 다음 보안 메커니즘을 구현해야 합니다:
- JWT 기반 인증
- API 키 관리
- HTTPS 강제 사용
- CORS 정책 강화
- 레이트 리미팅
- 입력 검증 강화

### 보안 헤더
모든 응답에는 다음 보안 헤더가 포함됩니다:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS 환경에서)

## API 엔드포인트

### 1. 헬스 체크

#### GET /health
서비스 상태 확인

**응답**
```json
{
  "status": "healthy",
  "service": "WatchHamster Backend",
  "version": "1.0.0"
}
```

### 2. 서비스 관리 API

#### GET /api/services/
모든 서비스 목록 조회

**응답**
```json
[
  {
    "id": "posco_news",
    "name": "POSCO 뉴스 모니터",
    "description": "POSCO 뉴스 시스템 모니터링 및 알림",
    "status": "running",
    "uptime": 3600,
    "last_error": null,
    "config": {}
  }
]
```

#### GET /api/services/{service_id}
특정 서비스 정보 조회

**매개변수**
- `service_id`: 서비스 ID

**응답**
```json
{
  "id": "posco_news",
  "name": "POSCO 뉴스 모니터",
  "description": "POSCO 뉴스 시스템 모니터링 및 알림",
  "status": "running",
  "uptime": 3600,
  "last_error": null,
  "config": {}
}
```

#### POST /api/services/{service_id}/start
서비스 시작

**매개변수**
- `service_id`: 서비스 ID

**응답**
```json
{
  "message": "서비스 'posco_news' 시작 중..."
}
```

#### POST /api/services/{service_id}/stop
서비스 중지

**매개변수**
- `service_id`: 서비스 ID

**응답**
```json
{
  "message": "서비스 'posco_news' 중지 중..."
}
```

#### POST /api/services/{service_id}/restart
서비스 재시작

**매개변수**
- `service_id`: 서비스 ID

**응답**
```json
{
  "message": "서비스 'posco_news' 재시작 중..."
}
```

### 3. 시스템 메트릭 API

#### GET /api/metrics/
현재 시스템 메트릭 조회

**응답**
```json
{
  "cpu_percent": 45.2,
  "memory_percent": 67.8,
  "disk_usage": 23.4,
  "network_status": "connected",
  "uptime": 86400,
  "active_services": 6,
  "timestamp": "2024-01-01T12:00:00"
}
```

#### GET /api/metrics/performance
성능 메트릭 조회 (히스토리 포함)

**응답**
```json
{
  "cpu_usage": [45.2, 46.1, 44.8],
  "memory_usage": [67.8, 68.2, 67.5],
  "disk_io": {
    "read_bytes": 1024000,
    "write_bytes": 512000
  },
  "network_io": {
    "bytes_sent": 2048000,
    "bytes_recv": 4096000
  },
  "timestamps": ["2024-01-01T12:00:00", "2024-01-01T12:01:00"]
}
```

#### GET /api/metrics/stability
안정성 메트릭 조회

**응답**
```json
{
  "error_count": 2,
  "recovery_count": 1,
  "last_health_check": "2024-01-01T12:00:00",
  "system_health": "healthy",
  "service_failures": []
}
```

#### GET /api/metrics/history
메트릭 히스토리 조회

**쿼리 매개변수**
- `limit`: 조회할 메트릭 수 (기본값: 50)

**응답**
```json
{
  "metrics": [...],
  "total_count": 100,
  "returned_count": 50
}
```

#### DELETE /api/metrics/history
메트릭 히스토리 초기화

**응답**
```json
{
  "message": "50개의 메트릭 히스토리가 초기화되었습니다",
  "cleared_count": 50
}
```

### 4. 웹훅 관리 API

#### POST /api/webhooks/send
웹훅 전송

**요청 본문**
```json
{
  "url": "https://discord.com/api/webhooks/...",
  "message": "테스트 메시지",
  "webhook_type": "discord",
  "template_id": "posco_news_alert",
  "variables": {
    "title": "뉴스 제목",
    "url": "https://example.com",
    "timestamp": "2024-01-01 12:00:00"
  }
}
```

**응답**
```json
{
  "message": "웹훅 전송이 시작되었습니다",
  "webhook_id": "webhook_1"
}
```

#### GET /api/webhooks/templates
웹훅 템플릿 목록 조회

**응답**
```json
[
  {
    "id": "posco_news_alert",
    "name": "POSCO 뉴스 알림",
    "description": "POSCO 뉴스 업데이트 알림 템플릿",
    "webhook_type": "discord",
    "template": "🏢 **POSCO 뉴스 업데이트**\n\n📰 **제목**: {title}",
    "variables": ["title", "url", "timestamp"],
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

#### GET /api/webhooks/templates/{template_id}
특정 웹훅 템플릿 조회

#### POST /api/webhooks/templates
새 웹훅 템플릿 생성

#### PUT /api/webhooks/templates/{template_id}
웹훅 템플릿 수정

#### DELETE /api/webhooks/templates/{template_id}
웹훅 템플릿 삭제

#### GET /api/webhooks/history
웹훅 전송 히스토리 조회

**쿼리 매개변수**
- `limit`: 조회할 히스토리 수 (기본값: 50)

**응답**
```json
[
  {
    "id": "webhook_1",
    "url": "https://discord.com/api/webhooks/...",
    "message": "테스트 메시지",
    "webhook_type": "discord",
    "status": "success",
    "response_code": 200,
    "error_message": null,
    "sent_at": "2024-01-01T12:00:00"
  }
]
```

#### GET /api/webhooks/history/{webhook_id}
특정 웹훅 전송 상태 조회

### 5. 향상된 웹훅 API (포팅된 시스템 사용)

#### POST /api/webhooks/enhanced/send
포팅된 메시지 템플릿 엔진을 사용한 웹훅 전송

**요청 본문**
```json
{
  "message_type": "deployment_success",
  "data": {
    "branch": "main",
    "commit_hash": "abc123",
    "timestamp": "2024-01-01 12:00:00"
  },
  "webhook_url": "https://discord.com/api/webhooks/..."
}
```

#### POST /api/webhooks/enhanced/deployment/success
배포 성공 웹훅 전송

#### POST /api/webhooks/enhanced/deployment/failure
배포 실패 웹훅 전송

#### POST /api/webhooks/enhanced/system/status
시스템 상태 웹훅 전송

#### POST /api/webhooks/enhanced/error/alert
오류 알림 웹훅 전송

#### GET /api/webhooks/enhanced/history
향상된 웹훅 전송 히스토리 조회

#### GET /api/webhooks/enhanced/statistics
웹훅 전송 통계 조회

#### POST /api/webhooks/enhanced/test
향상된 웹훅 연결 테스트

#### PUT /api/webhooks/enhanced/config
웹훅 설정 업데이트

### 6. 로그 관리 API

#### GET /api/logs/files
사용 가능한 로그 파일 목록 조회

**응답**
```json
[
  {
    "name": "watchhamster.log",
    "path": "logs/watchhamster.log",
    "size": 1024000,
    "modified_time": "2024-01-01T12:00:00",
    "is_active": true
  }
]
```

#### GET /api/logs/
로그 조회 (페이지네이션 지원)

**쿼리 매개변수**
- `file_name`: 로그 파일명 (기본값: "watchhamster.log")
- `limit`: 조회할 로그 수 (1-1000, 기본값: 100)
- `offset`: 건너뛸 로그 수 (기본값: 0)
- `level`: 로그 레벨 필터
- `search`: 검색어
- `start_time`: 시작 시간
- `end_time`: 종료 시간

**응답**
```json
[
  {
    "timestamp": "2024-01-01T12:00:00",
    "level": "INFO",
    "logger_name": "watchhamster",
    "message": "서비스 시작됨",
    "module": "main.py",
    "line_number": 123,
    "thread_id": "MainThread"
  }
]
```

#### GET /api/logs/stream
로그 스트리밍 (Server-Sent Events)

**쿼리 매개변수**
- `file_name`: 로그 파일명
- `level`: 로그 레벨 필터

#### WebSocket /api/logs/ws
WebSocket을 통한 실시간 로그 스트리밍

**쿼리 매개변수**
- `file_name`: 로그 파일명
- `level`: 로그 레벨 필터

#### GET /api/logs/download/{file_name}
로그 파일 다운로드

#### DELETE /api/logs/{file_name}
로그 파일 내용 삭제

#### GET /api/logs/search
로그 검색

**쿼리 매개변수**
- `query`: 검색어 (필수)
- `file_name`: 로그 파일명
- `limit`: 조회할 로그 수
- `case_sensitive`: 대소문자 구분 여부

**응답**
```json
{
  "query": "error",
  "file_name": "watchhamster.log",
  "total_matches": 5,
  "logs": [...]
}
```

#### GET /api/logs/statistics
로그 통계 조회

**쿼리 매개변수**
- `file_name`: 로그 파일명
- `hours`: 통계 기간 (시간, 1-168, 기본값: 24)

**응답**
```json
{
  "total_logs": 1000,
  "level_counts": {
    "DEBUG": 100,
    "INFO": 700,
    "WARNING": 150,
    "ERROR": 45,
    "CRITICAL": 5
  },
  "hourly_counts": {
    "2024-01-01 12:00": 50,
    "2024-01-01 13:00": 45
  },
  "top_loggers": {
    "watchhamster": 500,
    "api": 300
  },
  "error_messages": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "level": "ERROR",
      "message": "연결 실패..."
    }
  ]
}
```

### 7. POSCO 시스템 API

#### GET /api/posco/status
POSCO 시스템 상태 조회

**응답**
```json
{
  "status": "running",
  "branch": "main",
  "last_deployment": "2024-01-01T12:00:00",
  "services": {
    "news_monitor": "running",
    "deployment": "idle"
  }
}
```

#### POST /api/posco/deploy
배포 실행

#### POST /api/posco/branch-switch
브랜치 전환

### 8. WebSocket API

#### WebSocket /ws
실시간 상태 업데이트

**메시지 형식**
```json
{
  "type": "status_update",
  "data": {
    "service_id": "posco_news",
    "status": "running",
    "timestamp": "2024-01-01T12:00:00"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

**메시지 타입**
- `status_update`: 서비스 상태 업데이트
- `service_event`: 서비스 이벤트 (시작/중지/오류)
- `alert`: 시스템 알림
- `log_update`: 로그 업데이트

## 오류 응답

모든 API 엔드포인트는 오류 발생 시 다음 형식으로 응답합니다:

```json
{
  "detail": "오류 메시지",
  "status_code": 400
}
```

**일반적인 HTTP 상태 코드**
- `200`: 성공
- `400`: 잘못된 요청
- `404`: 리소스를 찾을 수 없음
- `500`: 내부 서버 오류

## 사용 예시

### Python 클라이언트 예시

```python
import httpx
import asyncio

async def get_services():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/services/")
        return response.json()

# 사용
services = asyncio.run(get_services())
print(services)
```

### JavaScript 클라이언트 예시

```javascript
// 서비스 목록 조회
async function getServices() {
    const response = await fetch('http://localhost:8000/api/services/');
    return await response.json();
}

// WebSocket 연결
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('실시간 업데이트:', data);
};
```

## 개발 및 테스트

### API 테스트 실행

```bash
# 백엔드 서버 시작
cd python-backend
python main.py

# API 테스트 실행
python test_api_endpoints.py
```

### API 문서 확인

개발 모드에서 서버를 시작한 후 브라우저에서 다음 URL에 접속:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 보안 고려사항

1. **인증**: 프로덕션 환경에서는 JWT 또는 API 키 기반 인증 구현 필요
2. **CORS**: 허용된 오리진만 접근 가능하도록 설정
3. **레이트 리미팅**: API 호출 빈도 제한 구현 권장
4. **입력 검증**: 모든 입력 데이터에 대한 엄격한 검증
5. **로깅**: 보안 이벤트 로깅 및 모니터링

## 버전 정보

- **API 버전**: 1.0.0
- **FastAPI 버전**: 0.104.1
- **Python 버전**: 3.8+

## 지원 및 문의

기술적 문의사항이나 버그 리포트는 개발팀에 문의하시기 바랍니다.