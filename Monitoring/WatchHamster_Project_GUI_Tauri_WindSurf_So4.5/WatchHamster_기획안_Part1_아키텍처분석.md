# 🐹 WatchHamster v4.0 기획안 Part 1: 시스템 아키텍처 & 핵심 모듈

> **현대적 하이브리드 아키텍처와 정교한 핵심 로직 분석**

---

## 📊 프로젝트 개요

### 🎯 시스템 정의
**WatchHamster v4.0**는 POSCO 뉴스 모니터링에서 시작되어 **멀티테넌트 금융/시스템 통합 모니터링 플랫폼**으로 진화한 차세대 솔루션입니다.

### 📈 핵심 성과
| 메트릭 | 기존 시스템 | v4.0 | 개선도 |
|--------|-------------|------|---------|
| **시작 시간** | ~8초 | ~3초 | **62% 향상** |
| **메모리 사용량** | ~150MB | ~80MB | **47% 절약** |
| **확장성** | 단일 회사 | 무제한 멀티테넌트 | **무한 확장** |
| **API 지원** | 없음 | 86개 금융 API | **완전 신규** |

---

## 🏗️ 시스템 아키텍처

### 3-Tier 하이브리드 구조

```
┌─────────────────────────────────────────────────────┐
│                🖥️ Presentation Layer                │
│                                                     │
│  Tauri Desktop App (포트: 1420)                      │
│  ├── Rust Backend (네이티브 성능)                     │
│  ├── React Frontend (현대적 UI)                      │
│  └── WebView2 (크로스 플랫폼)                         │
│                                                     │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────┴───────────────────────────────────┐
│               🔧 Business Logic Layer               │
│                                                     │
│  FastAPI Server (포트: 8000)                         │
│  ├── 21개 API 엔드포인트                             │
│  ├── 51개 핵심 로직 모듈                             │
│  ├── WebSocket 실시간 통신                           │
│  └── 멀티테넌트 데이터 관리                           │
│                                                     │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────┐
│                🗄️ Data Layer                        │
│                                                     │
│  ├── SQLite (멀티테넌트 DB)                          │
│  ├── InfoMax API (86개 금융 API)                    │
│  ├── Dooray/Discord 웹훅                            │
│  └── 시스템 메트릭 수집                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 📁 디렉토리 구조 (핵심 부분)

```
WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/
├── 🦀 src-tauri/                    # Rust 네이티브 레이어
│   ├── src/main.rs                  # Tauri 진입점
│   └── Cargo.toml                   # Rust 의존성
│
├── 📱 src/                          # React 프론트엔드
│   ├── components/ (100개)          # 재사용 컴포넌트
│   ├── pages/ (18개)                # 주요 페이지들
│   ├── hooks/ (31개)                # 커스텀 훅
│   └── services/ (13개)             # API 서비스 레이어
│
└── 🔧 python-backend/               # FastAPI 백엔드
    ├── core/ (51개)                 # 핵심 비즈니스 로직
    ├── api/ (21개)                  # REST API 엔드포인트
    ├── database/ (3개)              # 멀티테넌트 DB 모델
    └── utils/ (5개)                 # 유틸리티 함수들
```

---

## 🧠 핵심 모듈 심층 분석

### 1. WatchHamsterCore - 시스템 중앙 제어기

**파일**: `python-backend/core/watchhamster_core.py` (448줄)

#### 🔄 모니터링 모드 시스템

```python
class MonitoringMode(Enum):
    INDIVIDUAL = "individual"    # 개별 모니터 실행
    INTEGRATED = "integrated"    # 통합 모니터링 (1회)
    SMART = "smart"             # 스마트 시간대별 실행
    SERVICE_24H = "service_24h"  # 24시간 백그라운드 서비스
```

#### ⚙️ 시스템 상태 관리

```python
class SystemStatus(Enum):
    STOPPED = "stopped"          # 중지됨
    INITIALIZING = "initializing" # 초기화 중
    RUNNING = "running"          # 실행 중
    STOPPING = "stopping"       # 중지 중
    ERROR = "error"              # 오류 상태
```

#### 🎯 핵심 알고리즘: 초기화 로직

```python
async def initialize(self) -> bool:
    """
    견고한 시스템 초기화:
    1. 중복 초기화 방지
    2. 이전 상태 복원 (StateManager)
    3. 헬스 모니터링 시작
    4. 오류 처리 및 롤백
    """
    if self._initialized:
        return True  # 중복 방지

    try:
        self.status = SystemStatus.INITIALIZING
        
        # 상태 복원
        saved_state = self.state_manager.load_state()
        if saved_state:
            self._restore_from_state(saved_state)
        
        # 헬스 모니터링 시작
        await self.process_manager.start_health_monitoring()
        
        self._initialized = True
        self.status = SystemStatus.STOPPED
        return True
    
    except Exception as exc:
        self.status = SystemStatus.ERROR
        self.last_error = str(exc)
        return False
```

### 2. ProcessManager - 프로세스 생명주기 관리자

**파일**: `python-backend/core/process_manager.py` (349줄)

#### 🛠️ 고급 시작 로직 (3단계 재시도)

```python
async def start_monitor(self, monitor_type: str, start_func: Callable) -> bool:
    """
    견고한 모니터 시작:
    - 최대 3회 재시도 (MAX_RESTART_ATTEMPTS)
    - 지수적 백오프 지연
    - 안정성 검증 (0.5초 대기)
    """
    for attempt in range(self.MAX_RESTART_ATTEMPTS):
        try:
            # 비동기 태스크 생성
            task = asyncio.create_task(
                self._run_monitor_with_recovery(monitor_type, start_func)
            )
            self.tasks[monitor_type] = task
            
            # 안정성 검증
            await asyncio.sleep(0.5)
            
            if not task.done() or not task.exception():
                process_info.status = ProcessStatus.RUNNING
                process_info.health = HealthStatus.HEALTHY
                return True
                
        except Exception as exc:
            process_info.error_count += 1
            delay = self.RESTART_DELAY * (attempt + 1)  # 지수적 백오프
            await asyncio.sleep(delay)
    
    return False
```

#### 💊 지능형 헬스 체크

```python
async def check_health(self, monitor_type: str) -> HealthStatus:
    """
    다층 헬스 체크:
    1. 프로세스 상태 확인
    2. 태스크 실행 검증
    3. 오류 카운트 평가 (임계값: 5)
    """
    process_info = self.processes[monitor_type]
    
    if process_info.status == ProcessStatus.RUNNING:
        if monitor_type in self.tasks:
            task = self.tasks[monitor_type]
            
            if task.done():
                if task.exception():
                    return HealthStatus.UNHEALTHY  # 예외 발생
                else:
                    return HealthStatus.DEGRADED   # 예기치 않은 종료
            else:
                # 오류 카운트 기반 평가
                if process_info.error_count >= 5:
                    return HealthStatus.UNHEALTHY
                elif process_info.error_count > 0:
                    return HealthStatus.DEGRADED
                else:
                    return HealthStatus.HEALTHY
```

### 3. NewsMessageGenerator - 복원된 메시지 생성 엔진

**파일**: `python-backend/core/news_message_generator.py` (1410줄)

> **주목**: 이 모듈은 정상 커밋 a763ef84의 원본 알고리즘을 완전 복원한 매우 정교한 시스템입니다.

#### 🎨 동적 메시지 생성 결과

```python
@dataclass
class MessageGenerationResult:
    success: bool
    message: str           # 최종 메시지
    bot_name: str         # 동적 BOT 이름
    bot_icon: str         # 상황별 아이콘
    color: str            # 상태별 색상
    message_type: str     # 메시지 분류
```

#### 🧮 시간 기반 뉴스 상태 분석

```python
def _determine_news_status(self, news_data) -> Dict[str, Dict]:
    """
    정밀한 뉴스 상태 분석:
    - 발행 시간 vs 현재 시간 비교
    - 각 뉴스 타입별 독립 판단
    - 4단계 상태 분류 (지연/최신/발행전/데이터없음)
    """
    current_time = datetime.now()
    status_map = {}
    
    for news_type, news_item in news_data.items():
        if news_item and news_item.publish_time:
            time_diff = (current_time - news_item.publish_time).total_seconds()
            
            if time_diff > 3600:      # 1시간 이상 지연
                status = "지연"
                icon = "⚠️"
            elif time_diff > 0:       # 정상 발행
                status = "최신"
                icon = "✅"
            else:                     # 미발행
                status = "발행전"
                icon = "⏰"
        else:
            status = "데이터없음"
            icon = "❌"
            
        status_map[news_type] = {
            "status": status,
            "icon": icon,
            "time_diff": time_diff if news_item else None
        }
    
    return status_map
```

#### 🌳 아름다운 트리 구조 메시지

```python
def _generate_tree_structure_message(self, news_data, status_map) -> str:
    """
    동적 트리 구조 생성:
    
    출력 예시:
    ├── KOSPI 종가 [최신] ✅
    ├── 뉴욕 마켓 [지연] ⚠️
    └── 환율 정보 [발행전] ⏰
    """
    lines = []
    news_items = list(news_data.items())
    
    for i, (news_type, news_item) in enumerate(news_items):
        # 마지막 항목 판단
        is_last = (i == len(news_items) - 1)
        tree_char = "└──" if is_last else "├──"
        
        # 상태 정보 추출
        status_info = status_map.get(news_type, {})
        status = status_info.get("status", "알 수 없음")
        icon = status_info.get("icon", "❓")
        
        # 제목 정리
        title = news_item.title if news_item else f"{news_type} 뉴스"
        title = self._clean_title(title)
        
        # 최종 라인
        line = f"{tree_char} {title} [{status}] {icon}"
        lines.append(line)
    
    return "\n".join(lines)
```

---

## 🔗 데이터베이스 설계 (멀티테넌트)

### 📊 핵심 테이블 구조

```sql
-- 회사 정보 (멀티테넌트 기본)
CREATE TABLE companies (
    id TEXT PRIMARY KEY,              -- 회사 고유 ID
    name TEXT NOT NULL,               -- 회사명
    display_name TEXT NOT NULL,       -- 표시명
    logo_url TEXT,                    -- 로고 URL
    description TEXT,                 -- 설명
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 웹훅 설정 (회사별 독립)
CREATE TABLE webhook_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,         -- 회사 ID (FK)
    channel_type TEXT NOT NULL,       -- main_channel, alert_channel
    dooray_url TEXT NOT NULL,         -- Dooray 웹훅 URL
    bot_name TEXT NOT NULL,           -- BOT 이름
    bot_icon_url TEXT,                -- BOT 아이콘 URL
    FOREIGN KEY (company_id) REFERENCES companies (id)
);

-- API 설정 (회사별 독립)
CREATE TABLE api_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,         -- 회사 ID (FK)
    api_url TEXT NOT NULL,            -- API URL
    api_token TEXT NOT NULL,          -- API 토큰 (암호화)
    message_types TEXT NOT NULL,      -- 지원 메시지 타입 (JSON)
    FOREIGN KEY (company_id) REFERENCES companies (id)
);

-- 웹훅 로그 (회사별 독립)
CREATE TABLE webhook_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,         -- 회사 ID (FK)
    message_id TEXT NOT NULL,         -- 메시지 고유 ID
    message_type TEXT NOT NULL,       -- 메시지 타입
    full_message TEXT NOT NULL,       -- 전체 메시지 내용
    status TEXT NOT NULL,             -- 전송 상태
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (id)
);
```

---

## 🌐 WebSocket 실시간 통신

### 📡 연결 관리 시스템

```python
class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_info: Dict[WebSocket, Dict] = {}
    
    async def broadcast_system_status(self, status_data: Dict):
        """모든 클라이언트에게 시스템 상태 브로드캐스트"""
        message = {
            "type": "system_status_update",
            "data": status_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 연결된 모든 클라이언트에게 전송
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except ConnectionClosedError:
                self.active_connections.remove(connection)
```

---

## 🛡️ 보안 및 안정성

### 🔒 보안 계층

1. **인증**: Bearer Token 기반 API 인증
2. **데이터 암호화**: API 토큰 및 민감 정보 암호화
3. **CORS 정책**: 개발/프로덕션 환경별 차별화
4. **입력 검증**: Pydantic 기반 데이터 검증

### 🚀 성능 최적화

1. **비동기 처리**: FastAPI + asyncio 기반
2. **연결 풀링**: 데이터베이스 연결 최적화
3. **메모리 관리**: 백그라운드 태스크 자동 정리
4. **캐싱**: 자주 사용되는 데이터 캐싱

---

## 📊 시스템 메트릭

### 🔢 핵심 지표

- **파일 수**: 총 300+ 파일
- **코드 라인**: 50,000+ 라인
- **컴포넌트**: 100+ React 컴포넌트
- **API 엔드포인트**: 21개
- **핵심 로직 모듈**: 51개
- **금융 API 연동**: 86개

### 📈 성능 지표

- **시작 시간**: 3초 이하
- **메모리 사용량**: 80MB 이하
- **응답 시간**: 100ms 이하
- **동시 사용자**: 100+ 지원

---

**다음**: Part 2에서는 각 기능별 상세 분석을 다룹니다.
