"""
WebSocket 실시간 통신 API
실제 core 모듈과 연동하여 실시간 상태 업데이트 제공
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime
from typing import Dict, Set, Optional, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Core 모듈 임포트 (안전한 방식)
try:
    from core.watchhamster_monitor import WatchHamsterMonitor
    from core.news_parser import NewsDataParser
    from core.infomax_client import InfomaxAPIClient
    from core.webhook_sender import DoorayWebhookSender
except ImportError as e:
    logger.warning(f"일부 core 모듈 임포트 실패: {e}")
    WatchHamsterMonitor = None
    NewsDataParser = None
    InfomaxAPIClient = None
    DoorayWebhookSender = None

logger = logging.getLogger(__name__)
router = APIRouter()

# 전역 core 인스턴스들
watchhamster_monitor = None
news_parser = None
infomax_client = None
webhook_sender = None

# 데이터 모델
class WSMessage(BaseModel):
    type: str  # status_update, service_event, alert, log_update, news_update, system_metrics
    data: dict
    timestamp: datetime

class NewsStatusUpdate(BaseModel):
    news_type: str  # exchange-rate, newyork-market-watch, kospi-close
    status: str     # latest, delayed, outdated, error
    last_update: datetime
    expected_time: Optional[datetime] = None
    delay_minutes: Optional[int] = None
    data: Optional[dict] = None
    error_message: Optional[str] = None

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage: float
    network_status: str
    uptime: int
    timestamp: datetime

class ServiceStatus(BaseModel):
    id: str
    name: str
    status: str  # running, stopped, error
    pid: Optional[int] = None
    uptime: int
    restart_count: int
    description: str

# 연결된 WebSocket 클라이언트 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.client_info: Dict[WebSocket, dict] = {}
        self.subscriptions: Dict[WebSocket, Set[str]] = {}  # 클라이언트별 구독 정보
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """클라이언트 연결"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.client_info[websocket] = {
            "client_id": client_id or f"client_{len(self.active_connections)}",
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        self.subscriptions[websocket] = {"all"}  # 기본적으로 모든 이벤트 구독
        logger.info(f"WebSocket 클라이언트 연결: {self.client_info[websocket]['client_id']}")
    
    def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제"""
        if websocket in self.active_connections:
            client_info = self.client_info.get(websocket, {})
            client_id = client_info.get("client_id", "unknown")
            
            self.active_connections.remove(websocket)
            if websocket in self.client_info:
                del self.client_info[websocket]
            if websocket in self.subscriptions:
                del self.subscriptions[websocket]
            
            logger.info(f"WebSocket 클라이언트 연결 해제: {client_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """특정 클라이언트에게 메시지 전송"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"개인 메시지 전송 실패: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str, event_type: str = "all"):
        """모든 연결된 클라이언트에게 브로드캐스트 (구독 필터링 적용)"""
        if not self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections.copy():
            try:
                # 구독 확인
                client_subscriptions = self.subscriptions.get(connection, {"all"})
                if "all" in client_subscriptions or event_type in client_subscriptions:
                    await connection.send_text(message)
            except Exception as e:
                logger.error(f"브로드캐스트 전송 실패: {e}")
                disconnected.add(connection)
        
        # 연결이 끊어진 클라이언트 정리
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: dict, event_type: str = "all"):
        """JSON 데이터 브로드캐스트"""
        message = json.dumps(data, default=str, ensure_ascii=False)
        await self.broadcast(message, event_type)
    
    def subscribe(self, websocket: WebSocket, event_types: List[str]):
        """클라이언트 구독 설정"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket] = set(event_types)
    
    def get_connection_count(self) -> int:
        """연결된 클라이언트 수 반환"""
        return len(self.active_connections)
    
    def get_client_info(self) -> list:
        """클라이언트 정보 목록 반환"""
        return [
            {
                "client_id": info["client_id"],
                "connected_at": info["connected_at"],
                "last_ping": info["last_ping"],
                "subscriptions": list(self.subscriptions.get(ws, {"all"}))
            }
            for ws, info in self.client_info.items()
        ]

# 전역 연결 매니저
manager = ConnectionManager()

async def initialize_core_modules():
    """Core 모듈들 초기화"""
    global watchhamster_monitor, news_parser, infomax_client, webhook_sender
    
    try:
        if not watchhamster_monitor:
            watchhamster_monitor = WatchHamsterMonitor()
            logger.info("WatchHamster 모니터 초기화 완료")
        
        if not news_parser:
            news_parser = NewsDataParser()
            logger.info("뉴스 파서 초기화 완료")
        
        if not infomax_client:
            infomax_client = InfomaxAPIClient(
                base_url="https://global-api.einfomax.co.kr/apis/posco/news",
                timeout=30
            )
            logger.info("INFOMAX API 클라이언트 초기화 완료")
        
        if not webhook_sender:
            webhook_sender = DoorayWebhookSender()
            logger.info("Dooray 웹훅 발송자 초기화 완료")
            
    except Exception as e:
        logger.error(f"Core 모듈 초기화 오류: {e}")

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """메인 WebSocket 엔드포인트 - 실제 core 모듈과 연동"""
    await manager.connect(websocket, client_id)
    
    # Core 모듈 초기화
    await initialize_core_modules()
    
    try:
        # 연결 확인 메시지 전송
        welcome_message = WSMessage(
            type="connection_established",
            data={
                "message": "WebSocket 연결이 성공적으로 설정되었습니다",
                "client_id": manager.client_info[websocket]["client_id"],
                "server_time": datetime.now(),
                "available_subscriptions": [
                    "news_updates", "system_metrics", "service_events", 
                    "git_updates", "webhook_events", "all"
                ]
            },
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            welcome_message.model_dump_json(default=str), 
            websocket
        )
        
        # 초기 상태 전송
        await send_initial_status(websocket)
        
        # 클라이언트 메시지 수신 루프
        while True:
            try:
                # 메시지 수신 (타임아웃 설정)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # 클라이언트 메시지 처리
                await handle_client_message(websocket, data)
                
            except asyncio.TimeoutError:
                # 타임아웃 시 ping 메시지 전송
                ping_message = WSMessage(
                    type="ping",
                    data={"message": "서버에서 연결 상태를 확인합니다"},
                    timestamp=datetime.now()
                )
                await manager.send_personal_message(
                    ping_message.model_dump_json(default=str), 
                    websocket
                )
                
    except WebSocketDisconnect:
        logger.info("클라이언트가 연결을 종료했습니다")
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
    finally:
        manager.disconnect(websocket)

@router.websocket("/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """실시간 로그 스트리밍 WebSocket 엔드포인트"""
    await websocket.accept()
    logger.info("실시간 로그 스트리밍 WebSocket 연결이 설정되었습니다")
    
    try:
        # 연결 확인 메시지 전송
        await websocket.send_json({
            "type": "log_stream_connected",
            "data": {"message": "실시간 로그 스트리밍이 시작되었습니다"},
            "timestamp": datetime.now().isoformat()
        })
        
        # 실제 로그 파일 모니터링 및 스트리밍
        await stream_real_logs(websocket)
                
    except WebSocketDisconnect:
        logger.info("로그 스트리밍 WebSocket 연결이 종료되었습니다")
    except Exception as e:
        logger.error(f"로그 스트리밍 WebSocket 연결 중 오류 발생: {e}")
    finally:
        logger.info("로그 스트리밍 WebSocket 연결 정리 완료")

async def stream_real_logs(websocket: WebSocket):
    """실제 로그 파일을 모니터링하여 실시간 스트리밍"""
    import os
    import uuid
    from pathlib import Path
    
    # 로그 파일 경로들
    log_paths = [
        "logs/watchhamster.log",
        "logs/news_monitor.log", 
        "logs/webhook.log",
        "logs/system.log"
    ]
    
    # 로그 파일 상태 추적
    log_file_positions = {}
    
    # 기존 로그 파일들의 마지막 위치 저장
    for log_path in log_paths:
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                f.seek(0, 2)  # 파일 끝으로 이동
                log_file_positions[log_path] = f.tell()
        else:
            log_file_positions[log_path] = 0
    
    # Core 모듈에서 실시간 로그 생성
    log_counter = 0
    
    while True:
        try:
            # 실제 로그 파일 변화 확인
            new_logs = []
            
            for log_path in log_paths:
                if os.path.exists(log_path):
                    current_size = os.path.getsize(log_path)
                    last_position = log_file_positions.get(log_path, 0)
                    
                    if current_size > last_position:
                        # 새로운 로그 내용 읽기
                        with open(log_path, 'r', encoding='utf-8') as f:
                            f.seek(last_position)
                            new_content = f.read()
                            log_file_positions[log_path] = f.tell()
                            
                            # 새 로그 라인들 처리
                            for line in new_content.strip().split('\n'):
                                if line.strip():
                                    new_logs.append(parse_log_line(line, log_path))
            
            # Core 모듈에서 실시간 로그 생성 (실제 시스템 활동 기반)
            if watchhamster_monitor or news_parser or infomax_client or webhook_sender:
                system_logs = await generate_system_activity_logs()
                new_logs.extend(system_logs)
            
            # 새 로그가 없으면 시뮬레이션 로그 생성 (개발용)
            if not new_logs:
                new_logs = await generate_simulation_logs(log_counter)
                log_counter += len(new_logs)
            
            # 로그 전송
            for log_entry in new_logs:
                await websocket.send_json({
                    "type": "log_entry",
                    "data": log_entry,
                    "timestamp": datetime.now().isoformat()
                })
            
            # 2초마다 체크
            await asyncio.sleep(2)
            
        except WebSocketDisconnect:
            break
        except Exception as e:
            logger.error(f"로그 스트리밍 중 오류: {e}")
            await asyncio.sleep(2)

def parse_log_line(line: str, log_path: str) -> dict:
    """로그 라인을 파싱하여 구조화된 데이터로 변환"""
    import uuid
    import re
    
    # 로그 레벨 추출
    level_match = re.search(r'\b(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)\b', line.upper())
    level = level_match.group(1) if level_match else "INFO"
    
    # 타임스탬프 추출 시도
    timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}[\s\T]\d{2}:\d{2}:\d{2}', line)
    timestamp = timestamp_match.group(0) if timestamp_match else datetime.now().isoformat()
    
    # 소스 결정
    source = Path(log_path).stem
    
    return {
        "id": str(uuid.uuid4()),
        "timestamp": timestamp,
        "level": level,
        "source": source,
        "message": line.strip(),
        "metadata": {
            "log_file": log_path,
            "parsed_at": datetime.now().isoformat()
        }
    }

async def generate_system_activity_logs() -> List[dict]:
    """실제 시스템 활동 기반 로그 생성"""
    import uuid
    
    logs = []
    
    try:
        # 뉴스 모니터링 활동 로그
        if news_parser and infomax_client:
            news_types = ["exchange-rate", "newyork-market-watch", "kospi-close"]
            for news_type in news_types:
                try:
                    # API 상태 확인
                    health_status = await infomax_client.health_check()
                    
                    if health_status:
                        logs.append({
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "source": "news_monitor",
                            "message": f"[{news_type}] API 연결 상태 정상 확인",
                            "metadata": {
                                "news_type": news_type,
                                "api_status": "healthy"
                            }
                        })
                    else:
                        logs.append({
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.now().isoformat(),
                            "level": "WARN",
                            "source": "news_monitor", 
                            "message": f"[{news_type}] API 연결 상태 확인 실패",
                            "metadata": {
                                "news_type": news_type,
                                "api_status": "unhealthy"
                            }
                        })
                except Exception as e:
                    logs.append({
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "source": "news_monitor",
                        "message": f"[{news_type}] 모니터링 중 오류: {str(e)}",
                        "metadata": {
                            "news_type": news_type,
                            "error": str(e)
                        }
                    })
        
        # 시스템 모니터링 활동 로그
        if watchhamster_monitor:
            try:
                system_status = await watchhamster_monitor.get_system_status()
                
                if system_status:
                    logs.append({
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "source": "system_monitor",
                        "message": f"시스템 상태 확인 완료: {system_status.overall}",
                        "metadata": {
                            "overall_status": system_status.overall,
                            "services_count": len(system_status.services) if hasattr(system_status, 'services') else 0
                        }
                    })
            except Exception as e:
                logs.append({
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "source": "system_monitor",
                    "message": f"시스템 상태 확인 중 오류: {str(e)}",
                    "metadata": {
                        "error": str(e)
                    }
                })
        
        # 웹훅 활동 로그
        if webhook_sender:
            # 최근 웹훅 이벤트가 있다면 로그 생성
            recent_events = getattr(webhook_sender, 'recent_events', [])
            
            if recent_events:
                latest_event = recent_events[-1]
                logs.append({
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "source": "webhook_sender",
                    "message": f"웹훅 전송 완료: {latest_event.get('type', 'unknown')}",
                    "metadata": {
                        "webhook_type": latest_event.get('type'),
                        "status": latest_event.get('status', 'unknown')
                    }
                })
    
    except Exception as e:
        logger.error(f"시스템 활동 로그 생성 오류: {e}")
    
    return logs

async def generate_simulation_logs(counter: int) -> List[dict]:
    """시뮬레이션 로그 생성 (개발/테스트용)"""
    import uuid
    import random
    
    log_levels = ["DEBUG", "INFO", "WARN", "ERROR"]
    log_sources = ["news_monitor", "system_monitor", "webhook_sender", "git_monitor"]
    
    logs = []
    
    # 1-3개의 로그 엔트리 생성
    num_logs = random.randint(1, 3)
    
    for i in range(num_logs):
        level = random.choice(log_levels)
        source = random.choice(log_sources)
        
        # 소스별 메시지 생성
        if source == "news_monitor":
            messages = [
                "POSCO 뉴스 데이터 수집 완료",
                "환율 정보 업데이트 확인",
                "뉴욕 증시 데이터 파싱 중",
                "KOSPI 종가 정보 처리 완료"
            ]
        elif source == "system_monitor":
            messages = [
                "시스템 리소스 사용률 정상",
                "프로세스 상태 모니터링 완료",
                "메모리 사용량 체크",
                "디스크 공간 확인 완료"
            ]
        elif source == "webhook_sender":
            messages = [
                "Dooray 웹훅 전송 성공",
                "알림 메시지 생성 완료",
                "웹훅 연결 상태 확인",
                "메시지 템플릿 처리 완료"
            ]
        else:  # git_monitor
            messages = [
                "Git 상태 확인 완료",
                "브랜치 동기화 상태 체크",
                "커밋 이력 업데이트",
                "원격 저장소 연결 확인"
            ]
        
        message = random.choice(messages)
        
        # 레벨에 따른 메시지 수정
        if level == "ERROR":
            message = f"오류: {message} 실패"
        elif level == "WARN":
            message = f"경고: {message} 지연"
        elif level == "DEBUG":
            message = f"디버그: {message} 상세 정보"
        
        logs.append({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "metadata": {
                "simulation": True,
                "entry_number": counter + i + 1,
                "process_id": random.randint(1000, 9999)
            }
        })
    
    return logs

# WebSocket 엔드포인트는 위에서 이미 정의됨 (중복 제거)

async def handle_client_message(websocket: WebSocket, message: str):
    """클라이언트 메시지 처리"""
    try:
        data = json.loads(message)
        message_type = data.get("type", "unknown")
        
        logger.info(f"클라이언트 메시지 수신: {message_type}")
        
        # 메시지 타입별 처리
        if message_type == "pong":
            # Pong 응답 처리
            if websocket in manager.client_info:
                manager.client_info[websocket]["last_ping"] = datetime.now()
        
        elif message_type == "subscribe":
            # 구독 요청 처리
            subscriptions = data.get("subscriptions", ["all"])
            manager.subscribe(websocket, subscriptions)
            
            response = WSMessage(
                type="subscription_confirmed",
                data={
                    "subscriptions": subscriptions,
                    "message": f"구독이 설정되었습니다: {', '.join(subscriptions)}"
                },
                timestamp=datetime.now()
            )
            await manager.send_personal_message(
                response.model_dump_json(default=str), 
                websocket
            )
        
        elif message_type == "request_status":
            # 상태 요청 처리
            await send_current_status(websocket)
        
        elif message_type == "request_news_update":
            # 뉴스 상태 업데이트 요청
            await send_news_status(websocket)
        
        elif message_type == "request_system_metrics":
            # 시스템 메트릭 요청
            await send_system_metrics(websocket)
        
        elif message_type == "force_news_refresh":
            # 강제 뉴스 갱신 요청
            news_type = data.get("news_type", "all")
            await force_news_refresh(websocket, news_type)
        
        else:
            logger.warning(f"알 수 없는 메시지 타입: {message_type}")
            
    except json.JSONDecodeError:
        logger.error(f"잘못된 JSON 메시지: {message}")
    except Exception as e:
        logger.error(f"클라이언트 메시지 처리 오류: {e}")

async def send_initial_status(websocket: WebSocket):
    """연결 시 초기 상태 전송"""
    try:
        # 시스템 메트릭 전송
        await send_system_metrics(websocket)
        
        # 뉴스 상태 전송
        await send_news_status(websocket)
        
        # 서비스 상태 전송
        await send_service_status(websocket)
        
        # Git 상태 전송
        await send_git_status(websocket)
        
    except Exception as e:
        logger.error(f"초기 상태 전송 오류: {e}")

async def send_current_status(websocket: WebSocket):
    """현재 시스템 전체 상태 전송"""
    try:
        # 실제 시스템 상태 수집
        system_status = await get_comprehensive_system_status()
        
        status_message = WSMessage(
            type="comprehensive_status",
            data=system_status,
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            status_message.model_dump_json(default=str), 
            websocket
        )
        
    except Exception as e:
        logger.error(f"종합 상태 전송 오류: {e}")

async def send_news_status(websocket: WebSocket):
    """뉴스 상태 전송"""
    try:
        if not news_parser or not infomax_client:
            await initialize_core_modules()
        
        news_types = ["exchange-rate", "newyork-market-watch", "kospi-close"]
        news_statuses = []
        
        for news_type in news_types:
            try:
                # 실제 뉴스 데이터 조회
                raw_data = await infomax_client.fetch_news_data(news_type)
                
                if raw_data:
                    # 뉴스 데이터 파싱
                    parsed_data = await news_parser.parse_news_data(raw_data, news_type)
                    status = news_parser.determine_news_status(parsed_data)
                    
                    news_status = NewsStatusUpdate(
                        news_type=news_type,
                        status=status,
                        last_update=datetime.now(),
                        data=parsed_data
                    )
                else:
                    news_status = NewsStatusUpdate(
                        news_type=news_type,
                        status="error",
                        last_update=datetime.now(),
                        error_message="데이터 조회 실패"
                    )
                
                news_statuses.append(news_status.model_dump())
                
            except Exception as e:
                logger.error(f"{news_type} 뉴스 상태 조회 오류: {e}")
                news_status = NewsStatusUpdate(
                    news_type=news_type,
                    status="error",
                    last_update=datetime.now(),
                    error_message=str(e)
                )
                news_statuses.append(news_status.model_dump())
        
        # 뉴스 상태 전송
        news_message = WSMessage(
            type="news_status_update",
            data={"news_statuses": news_statuses},
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            news_message.model_dump_json(default=str),
            websocket
        )
        
    except Exception as e:
        logger.error(f"뉴스 상태 전송 오류: {e}")

async def send_system_metrics(websocket: WebSocket):
    """시스템 메트릭 전송"""
    try:
        # 실제 시스템 메트릭 수집
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # 디스크 사용량 (크로스 플랫폼 호환)
        try:
            disk_usage = psutil.disk_usage('/').percent
        except:
            try:
                disk_usage = psutil.disk_usage('C:\\').percent
            except:
                disk_usage = 0
        
        # 네트워크 상태
        network_status = "connected"
        try:
            net_io = psutil.net_io_counters()
            if net_io and (net_io.bytes_sent > 0 or net_io.bytes_recv > 0):
                network_status = "active"
        except:
            network_status = "unknown"
        
        # 시스템 업타임
        boot_time = psutil.boot_time()
        uptime = int(time.time() - boot_time)
        
        metrics = SystemMetrics(
            cpu_percent=round(cpu_percent, 1),
            memory_percent=round(memory.percent, 1),
            memory_used_gb=round(memory.used / (1024**3), 2),
            memory_total_gb=round(memory.total / (1024**3), 2),
            disk_usage=round(disk_usage, 1),
            network_status=network_status,
            uptime=uptime,
            timestamp=datetime.now()
        )
        
        metrics_message = WSMessage(
            type="system_metrics_update",
            data=metrics.model_dump(),
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            metrics_message.model_dump_json(default=str),
            websocket
        )
        
    except Exception as e:
        logger.error(f"시스템 메트릭 전송 오류: {e}")

async def send_service_status(websocket: WebSocket):
    """서비스 상태 전송"""
    try:
        if not watchhamster_monitor:
            await initialize_core_modules()
        
        # 실제 서비스 상태 조회
        system_status = await watchhamster_monitor.get_system_status()
        
        services = []
        if system_status and hasattr(system_status, 'services'):
            for service_id, service_data in system_status.services.items():
                service_status = ServiceStatus(
                    id=service_id,
                    name=service_data.get('name', service_id),
                    status=service_data.get('status', 'unknown'),
                    pid=service_data.get('pid'),
                    uptime=service_data.get('uptime', 0),
                    restart_count=service_data.get('restart_count', 0),
                    description=service_data.get('description', '')
                )
                services.append(service_status.model_dump())
        
        service_message = WSMessage(
            type="service_status_update",
            data={"services": services},
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            service_message.model_dump_json(default=str),
            websocket
        )
        
    except Exception as e:
        logger.error(f"서비스 상태 전송 오류: {e}")

async def send_git_status(websocket: WebSocket):
    """Git 상태 전송"""
    try:
        if not watchhamster_monitor:
            await initialize_core_modules()
        
        # Git 상태 조회
        git_status = await watchhamster_monitor.get_git_status()
        
        git_message = WSMessage(
            type="git_status_update",
            data=git_status or {"status": "unknown", "message": "Git 상태를 확인할 수 없습니다"},
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            git_message.model_dump_json(default=str),
            websocket
        )
        
    except Exception as e:
        logger.error(f"Git 상태 전송 오류: {e}")

async def force_news_refresh(websocket: WebSocket, news_type: str):
    """강제 뉴스 갱신"""
    try:
        if not news_parser or not infomax_client:
            await initialize_core_modules()
        
        if news_type == "all":
            news_types = ["exchange-rate", "newyork-market-watch", "kospi-close"]
        else:
            news_types = [news_type]
        
        for nt in news_types:
            try:
                # 강제 데이터 갱신
                raw_data = await infomax_client.fetch_news_data(nt)
                
                if raw_data:
                    parsed_data = await news_parser.parse_news_data(raw_data, nt)
                    
                    # 갱신 완료 알림
                    refresh_message = WSMessage(
                        type="news_refresh_completed",
                        data={
                            "news_type": nt,
                            "status": "success",
                            "data": parsed_data,
                            "timestamp": datetime.now()
                        },
                        timestamp=datetime.now()
                    )
                else:
                    refresh_message = WSMessage(
                        type="news_refresh_completed",
                        data={
                            "news_type": nt,
                            "status": "failed",
                            "error": "데이터 조회 실패"
                        },
                        timestamp=datetime.now()
                    )
                
                await manager.send_personal_message(
                    refresh_message.model_dump_json(default=str),
                    websocket
                )
                
            except Exception as e:
                logger.error(f"{nt} 뉴스 갱신 오류: {e}")
                
                error_message = WSMessage(
                    type="news_refresh_completed",
                    data={
                        "news_type": nt,
                        "status": "error",
                        "error": str(e)
                    },
                    timestamp=datetime.now()
                )
                
                await manager.send_personal_message(
                    error_message.model_dump_json(default=str),
                    websocket
                )
        
    except Exception as e:
        logger.error(f"뉴스 강제 갱신 오류: {e}")

async def get_comprehensive_system_status():
    """종합 시스템 상태 조회"""
    try:
        if not watchhamster_monitor:
            await initialize_core_modules()
        
        # 시스템 전체 상태 조회
        system_status = await watchhamster_monitor.get_system_status()
        
        # 추가 메트릭 수집
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            "overall_status": system_status.overall if system_status else "unknown",
            "services": system_status.services if system_status else {},
            "system_metrics": {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2)
            },
            "connection_count": manager.get_connection_count(),
            "last_check": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"종합 시스템 상태 조회 오류: {e}")
        return {
            "overall_status": "error",
            "error": str(e),
            "connection_count": manager.get_connection_count(),
            "last_check": datetime.now()
        }

# 외부에서 호출할 수 있는 브로드캐스트 함수들
async def broadcast_service_event(service_id: str, event_type: str, message: str):
    """서비스 이벤트 브로드캐스트"""
    event_message = WSMessage(
        type="service_event",
        data={
            "service_id": service_id,
            "event_type": event_type,
            "message": message
        },
        timestamp=datetime.now()
    )
    
    await manager.broadcast_json(event_message.model_dump(default=str))

async def broadcast_system_alert(alert_type: str, message: str, severity: str = "info"):
    """시스템 알림 브로드캐스트"""
    alert_message = WSMessage(
        type="alert",
        data={
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        },
        timestamp=datetime.now()
    )
    
    await manager.broadcast_json(alert_message.model_dump(default=str))

async def broadcast_log_update(log_entry: dict):
    """로그 업데이트 브로드캐스트"""
    log_message = WSMessage(
        type="log_update",
        data=log_entry,
        timestamp=datetime.now()
    )
    
    await manager.broadcast_json(log_message.model_dump(default=str))

# 실시간 상태 업데이트 시스템
class RealTimeUpdateSystem:
    """실시간 상태 업데이트 시스템"""
    
    def __init__(self):
        self.last_news_status = {}
        self.last_system_metrics = {}
        self.last_service_status = {}
        self.last_git_status = {}
        self.update_intervals = {
            "system_metrics": 5,    # 5초마다 시스템 메트릭
            "news_status": 30,      # 30초마다 뉴스 상태
            "service_status": 10,   # 10초마다 서비스 상태
            "git_status": 60        # 60초마다 Git 상태
        }
        self.last_update_times = {}
    
    async def start_monitoring(self):
        """실시간 모니터링 시작"""
        logger.info("실시간 상태 업데이트 시스템 시작")
        
        # Core 모듈 초기화
        await initialize_core_modules()
        
        # 각 모니터링 태스크 시작
        tasks = [
            asyncio.create_task(self.monitor_system_metrics()),
            asyncio.create_task(self.monitor_news_status()),
            asyncio.create_task(self.monitor_service_status()),
            asyncio.create_task(self.monitor_git_status()),
            asyncio.create_task(self.monitor_webhook_events())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("실시간 모니터링 태스크들이 취소되었습니다")
            for task in tasks:
                if not task.done():
                    task.cancel()
    
    async def monitor_system_metrics(self):
        """시스템 메트릭 실시간 모니터링"""
        while True:
            try:
                if manager.get_connection_count() > 0:
                    # 현재 시스템 메트릭 수집
                    current_metrics = await self.get_current_system_metrics()
                    
                    # 변화 감지 및 브로드캐스트
                    if self.has_metrics_changed(current_metrics):
                        await self.broadcast_system_metrics_update(current_metrics)
                        self.last_system_metrics = current_metrics
                
                await asyncio.sleep(self.update_intervals["system_metrics"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"시스템 메트릭 모니터링 오류: {e}")
                await asyncio.sleep(5)
    
    async def monitor_news_status(self):
        """뉴스 상태 실시간 모니터링"""
        while True:
            try:
                if manager.get_connection_count() > 0:
                    # 뉴스 상태 확인
                    current_news_status = await self.get_current_news_status()
                    
                    # 변화 감지 및 브로드캐스트
                    if self.has_news_status_changed(current_news_status):
                        await self.broadcast_news_status_update(current_news_status)
                        self.last_news_status = current_news_status
                        
                        # 중요한 변화 시 웹훅 전송
                        await self.handle_news_status_webhook(current_news_status)
                
                await asyncio.sleep(self.update_intervals["news_status"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"뉴스 상태 모니터링 오류: {e}")
                await asyncio.sleep(10)
    
    async def monitor_service_status(self):
        """서비스 상태 실시간 모니터링"""
        while True:
            try:
                if manager.get_connection_count() > 0:
                    # 서비스 상태 확인
                    current_service_status = await self.get_current_service_status()
                    
                    # 변화 감지 및 브로드캐스트
                    if self.has_service_status_changed(current_service_status):
                        await self.broadcast_service_status_update(current_service_status)
                        self.last_service_status = current_service_status
                        
                        # 서비스 중단/시작 시 알림
                        await self.handle_service_status_alerts(current_service_status)
                
                await asyncio.sleep(self.update_intervals["service_status"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"서비스 상태 모니터링 오류: {e}")
                await asyncio.sleep(10)
    
    async def monitor_git_status(self):
        """Git 상태 실시간 모니터링"""
        while True:
            try:
                if manager.get_connection_count() > 0:
                    # Git 상태 확인
                    current_git_status = await self.get_current_git_status()
                    
                    # 변화 감지 및 브로드캐스트
                    if self.has_git_status_changed(current_git_status):
                        await self.broadcast_git_status_update(current_git_status)
                        self.last_git_status = current_git_status
                
                await asyncio.sleep(self.update_intervals["git_status"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Git 상태 모니터링 오류: {e}")
                await asyncio.sleep(30)
    
    async def monitor_webhook_events(self):
        """웹훅 이벤트 모니터링"""
        while True:
            try:
                if manager.get_connection_count() > 0 and webhook_sender:
                    # 웹훅 전송 상태 확인
                    webhook_status = await self.get_webhook_status()
                    
                    if webhook_status.get("recent_events"):
                        await self.broadcast_webhook_events(webhook_status["recent_events"])
                
                await asyncio.sleep(15)  # 15초마다 웹훅 이벤트 확인
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"웹훅 이벤트 모니터링 오류: {e}")
                await asyncio.sleep(15)
    
    # 데이터 수집 메서드들
    async def get_current_system_metrics(self):
        """현재 시스템 메트릭 수집"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # 디스크 사용량
            try:
                disk_usage = psutil.disk_usage('/').percent
            except:
                try:
                    disk_usage = psutil.disk_usage('C:\\').percent
                except:
                    disk_usage = 0
            
            # 네트워크 상태
            network_status = "connected"
            try:
                net_io = psutil.net_io_counters()
                if net_io and (net_io.bytes_sent > 0 or net_io.bytes_recv > 0):
                    network_status = "active"
            except:
                network_status = "unknown"
            
            return {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_usage": round(disk_usage, 1),
                "network_status": network_status,
                "uptime": int(time.time() - psutil.boot_time()),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 오류: {e}")
            return {}
    
    async def get_current_news_status(self):
        """현재 뉴스 상태 수집"""
        try:
            if not news_parser or not infomax_client:
                return {}
            
            news_types = ["exchange-rate", "newyork-market-watch", "kospi-close"]
            news_statuses = {}
            
            for news_type in news_types:
                try:
                    raw_data = await infomax_client.fetch_news_data(news_type)
                    
                    if raw_data:
                        parsed_data = await news_parser.parse_news_data(raw_data, news_type)
                        status = news_parser.determine_news_status(parsed_data)
                        
                        news_statuses[news_type] = {
                            "status": status,
                            "last_update": datetime.now(),
                            "data": parsed_data
                        }
                    else:
                        news_statuses[news_type] = {
                            "status": "error",
                            "last_update": datetime.now(),
                            "error": "데이터 조회 실패"
                        }
                        
                except Exception as e:
                    news_statuses[news_type] = {
                        "status": "error",
                        "last_update": datetime.now(),
                        "error": str(e)
                    }
            
            return news_statuses
            
        except Exception as e:
            logger.error(f"뉴스 상태 수집 오류: {e}")
            return {}
    
    async def get_current_service_status(self):
        """현재 서비스 상태 수집"""
        try:
            if not watchhamster_monitor:
                return {}
            
            system_status = await watchhamster_monitor.get_system_status()
            
            if system_status and hasattr(system_status, 'services'):
                return system_status.services
            else:
                return {}
                
        except Exception as e:
            logger.error(f"서비스 상태 수집 오류: {e}")
            return {}
    
    async def get_current_git_status(self):
        """현재 Git 상태 수집"""
        try:
            if not watchhamster_monitor:
                return {}
            
            git_status = await watchhamster_monitor.get_git_status()
            return git_status or {}
            
        except Exception as e:
            logger.error(f"Git 상태 수집 오류: {e}")
            return {}
    
    async def get_webhook_status(self):
        """웹훅 상태 수집"""
        try:
            if not webhook_sender:
                return {}
            
            # 웹훅 발송자에서 최근 이벤트 조회
            recent_events = getattr(webhook_sender, 'recent_events', [])
            
            return {
                "recent_events": recent_events[-10:],  # 최근 10개 이벤트
                "last_check": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"웹훅 상태 수집 오류: {e}")
            return {}
    
    # 변화 감지 메서드들
    def has_metrics_changed(self, current_metrics):
        """시스템 메트릭 변화 감지"""
        if not self.last_system_metrics:
            return True
        
        # 임계값 기반 변화 감지
        thresholds = {
            "cpu_percent": 5.0,      # 5% 이상 변화
            "memory_percent": 3.0,   # 3% 이상 변화
            "disk_usage": 1.0        # 1% 이상 변화
        }
        
        for key, threshold in thresholds.items():
            if key in current_metrics and key in self.last_system_metrics:
                diff = abs(current_metrics[key] - self.last_system_metrics[key])
                if diff >= threshold:
                    return True
        
        # 네트워크 상태 변화
        if (current_metrics.get("network_status") != 
            self.last_system_metrics.get("network_status")):
            return True
        
        return False
    
    def has_news_status_changed(self, current_news_status):
        """뉴스 상태 변화 감지"""
        if not self.last_news_status:
            return True
        
        for news_type, status_data in current_news_status.items():
            last_status = self.last_news_status.get(news_type, {})
            
            # 상태 변화 확인
            if status_data.get("status") != last_status.get("status"):
                return True
            
            # 데이터 변화 확인 (해시 비교)
            current_data_hash = hash(str(status_data.get("data", {})))
            last_data_hash = hash(str(last_status.get("data", {})))
            
            if current_data_hash != last_data_hash:
                return True
        
        return False
    
    def has_service_status_changed(self, current_service_status):
        """서비스 상태 변화 감지"""
        if not self.last_service_status:
            return True
        
        for service_id, service_data in current_service_status.items():
            last_service = self.last_service_status.get(service_id, {})
            
            # 서비스 상태 변화 확인
            if service_data.get("status") != last_service.get("status"):
                return True
            
            # PID 변화 확인 (재시작 감지)
            if service_data.get("pid") != last_service.get("pid"):
                return True
        
        return False
    
    def has_git_status_changed(self, current_git_status):
        """Git 상태 변화 감지"""
        if not self.last_git_status:
            return True
        
        # 주요 Git 상태 변화 확인
        important_keys = ["branch", "last_commit", "has_conflicts", "remote_status"]
        
        for key in important_keys:
            if current_git_status.get(key) != self.last_git_status.get(key):
                return True
        
        return False
    
    # 브로드캐스트 메서드들
    async def broadcast_system_metrics_update(self, metrics_data):
        """시스템 메트릭 업데이트 브로드캐스트"""
        message = WSMessage(
            type="system_metrics_update",
            data=metrics_data,
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            message.model_dump(default=str),
            event_type="system_metrics"
        )
    
    async def broadcast_news_status_update(self, news_status_data):
        """뉴스 상태 업데이트 브로드캐스트"""
        message = WSMessage(
            type="news_status_update",
            data={"news_statuses": news_status_data},
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            message.model_dump(default=str),
            event_type="news_updates"
        )
    
    async def broadcast_service_status_update(self, service_status_data):
        """서비스 상태 업데이트 브로드캐스트"""
        message = WSMessage(
            type="service_status_update",
            data={"services": service_status_data},
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            message.model_dump(default=str),
            event_type="service_events"
        )
    
    async def broadcast_git_status_update(self, git_status_data):
        """Git 상태 업데이트 브로드캐스트"""
        message = WSMessage(
            type="git_status_update",
            data=git_status_data,
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            message.model_dump(default=str),
            event_type="git_updates"
        )
    
    async def broadcast_webhook_events(self, webhook_events):
        """웹훅 이벤트 브로드캐스트"""
        message = WSMessage(
            type="webhook_events_update",
            data={"events": webhook_events},
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            message.model_dump(default=str),
            event_type="webhook_events"
        )
    
    # 알림 처리 메서드들
    async def handle_news_status_webhook(self, news_status_data):
        """뉴스 상태 변화 시 웹훅 전송"""
        try:
            if not webhook_sender:
                return
            
            for news_type, status_data in news_status_data.items():
                # 중요한 상태 변화만 웹훅 전송
                if status_data.get("status") in ["delayed", "error"]:
                    await webhook_sender.send_posco_news_alert(status_data)
                    
        except Exception as e:
            logger.error(f"뉴스 상태 웹훅 전송 오류: {e}")
    
    async def handle_service_status_alerts(self, service_status_data):
        """서비스 상태 변화 시 알림 처리"""
        try:
            for service_id, service_data in service_status_data.items():
                last_service = self.last_service_status.get(service_id, {})
                
                # 서비스 중단 감지
                if (service_data.get("status") == "stopped" and 
                    last_service.get("status") == "running"):
                    
                    alert_message = WSMessage(
                        type="service_alert",
                        data={
                            "alert_type": "service_stopped",
                            "service_id": service_id,
                            "service_name": service_data.get("name", service_id),
                            "message": f"서비스 '{service_data.get('name', service_id)}'가 중단되었습니다",
                            "severity": "warning"
                        },
                        timestamp=datetime.now()
                    )
                    
                    await manager.broadcast_json(
                        alert_message.model_dump(default=str),
                        event_type="service_events"
                    )
                
                # 서비스 시작 감지
                elif (service_data.get("status") == "running" and 
                      last_service.get("status") in ["stopped", "error"]):
                    
                    alert_message = WSMessage(
                        type="service_alert",
                        data={
                            "alert_type": "service_started",
                            "service_id": service_id,
                            "service_name": service_data.get("name", service_id),
                            "message": f"서비스 '{service_data.get('name', service_id)}'가 시작되었습니다",
                            "severity": "info"
                        },
                        timestamp=datetime.now()
                    )
                    
                    await manager.broadcast_json(
                        alert_message.model_dump(default=str),
                        event_type="service_events"
                    )
                    
        except Exception as e:
            logger.error(f"서비스 상태 알림 처리 오류: {e}")

# 전역 실시간 업데이트 시스템 인스턴스
realtime_system = RealTimeUpdateSystem()

# 주기적인 상태 업데이트 태스크 (기존 함수를 새 시스템으로 대체)
async def periodic_status_broadcast():
    """주기적인 상태 업데이트 브로드캐스트 (실시간 시스템 사용)"""
    logger.info("실시간 상태 업데이트 시스템 시작")
    
    try:
        await realtime_system.start_monitoring()
    except asyncio.CancelledError:
        logger.info("실시간 상태 업데이트 시스템이 취소되었습니다")
    except Exception as e:
        logger.error(f"실시간 상태 업데이트 시스템 오류: {e}")
        raise

# 외부에서 호출할 수 있는 브로드캐스트 함수들 (실제 core 모듈 연동)
async def broadcast_service_event(service_id: str, event_type: str, message: str):
    """서비스 이벤트 브로드캐스트"""
    try:
        event_message = WSMessage(
            type="service_event",
            data={
                "service_id": service_id,
                "event_type": event_type,
                "message": message,
                "timestamp": datetime.now()
            },
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            event_message.model_dump(default=str),
            event_type="service_events"
        )
        
        logger.info(f"서비스 이벤트 브로드캐스트: {service_id} - {event_type}")
        
    except Exception as e:
        logger.error(f"서비스 이벤트 브로드캐스트 오류: {e}")

async def broadcast_system_alert(alert_type: str, message: str, severity: str = "info"):
    """시스템 알림 브로드캐스트"""
    try:
        alert_message = WSMessage(
            type="system_alert",
            data={
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": datetime.now()
            },
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            alert_message.model_dump(default=str),
            event_type="system_alerts"
        )
        
        logger.info(f"시스템 알림 브로드캐스트: {alert_type} - {severity}")
        
    except Exception as e:
        logger.error(f"시스템 알림 브로드캐스트 오류: {e}")

async def broadcast_news_update(news_type: str, status: str, data: dict = None):
    """뉴스 업데이트 브로드캐스트"""
    try:
        news_update = NewsStatusUpdate(
            news_type=news_type,
            status=status,
            last_update=datetime.now(),
            data=data
        )
        
        update_message = WSMessage(
            type="news_update",
            data=news_update.model_dump(),
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            update_message.model_dump(default=str),
            event_type="news_updates"
        )
        
        logger.info(f"뉴스 업데이트 브로드캐스트: {news_type} - {status}")
        
    except Exception as e:
        logger.error(f"뉴스 업데이트 브로드캐스트 오류: {e}")

async def broadcast_git_update(git_status: dict):
    """Git 상태 업데이트 브로드캐스트"""
    try:
        git_message = WSMessage(
            type="git_update",
            data=git_status,
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            git_message.model_dump(default=str),
            event_type="git_updates"
        )
        
        logger.info(f"Git 상태 업데이트 브로드캐스트: {git_status.get('branch', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Git 상태 업데이트 브로드캐스트 오류: {e}")

async def broadcast_webhook_event(webhook_type: str, status: str, message: str):
    """웹훅 이벤트 브로드캐스트"""
    try:
        webhook_message = WSMessage(
            type="webhook_event",
            data={
                "webhook_type": webhook_type,
                "status": status,
                "message": message,
                "timestamp": datetime.now()
            },
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(
            webhook_message.model_dump(default=str),
            event_type="webhook_events"
        )
        
        logger.info(f"웹훅 이벤트 브로드캐스트: {webhook_type} - {status}")
        
    except Exception as e:
        logger.error(f"웹훅 이벤트 브로드캐스트 오류: {e}")

# 실시간 업데이트 트리거 함수들 (다른 모듈에서 호출)
async def trigger_news_status_update(news_type: str = None):
    """뉴스 상태 업데이트 트리거"""
    try:
        if news_type:
            # 특정 뉴스 타입만 업데이트
            current_status = await realtime_system.get_current_news_status()
            if news_type in current_status:
                await broadcast_news_update(
                    news_type, 
                    current_status[news_type].get("status", "unknown"),
                    current_status[news_type].get("data")
                )
        else:
            # 모든 뉴스 상태 업데이트
            current_status = await realtime_system.get_current_news_status()
            await realtime_system.broadcast_news_status_update(current_status)
            
    except Exception as e:
        logger.error(f"뉴스 상태 업데이트 트리거 오류: {e}")

async def trigger_service_status_update(service_id: str = None):
    """서비스 상태 업데이트 트리거"""
    try:
        current_status = await realtime_system.get_current_service_status()
        
        if service_id and service_id in current_status:
            # 특정 서비스 상태 업데이트
            await broadcast_service_event(
                service_id,
                "status_update",
                f"서비스 상태가 업데이트되었습니다: {current_status[service_id].get('status', 'unknown')}"
            )
        else:
            # 모든 서비스 상태 업데이트
            await realtime_system.broadcast_service_status_update(current_status)
            
    except Exception as e:
        logger.error(f"서비스 상태 업데이트 트리거 오류: {e}")

async def trigger_system_metrics_update():
    """시스템 메트릭 업데이트 트리거"""
    try:
        current_metrics = await realtime_system.get_current_system_metrics()
        await realtime_system.broadcast_system_metrics_update(current_metrics)
        
    except Exception as e:
        logger.error(f"시스템 메트릭 업데이트 트리거 오류: {e}")

async def trigger_git_status_update():
    """Git 상태 업데이트 트리거"""
    try:
        current_git_status = await realtime_system.get_current_git_status()
        await broadcast_git_update(current_git_status)
        
    except Exception as e:
        logger.error(f"Git 상태 업데이트 트리거 오류: {e}")

# 연결 상태 모니터링 함수 (개선된 버전)
async def monitor_connection_health():
    """WebSocket 연결 상태 모니터링 및 자동 정리"""
    logger.info("WebSocket 연결 상태 모니터링 시작")
    
    while True:
        try:
            current_time = datetime.now()
            disconnected_clients = []
            
            # 비활성 연결 감지 (60초 이상 응답 없음)
            for websocket, info in manager.client_info.items():
                last_ping = info.get("last_ping", info.get("connected_at"))
                inactive_seconds = (current_time - last_ping).total_seconds()
                
                if inactive_seconds > 60:
                    disconnected_clients.append(websocket)
                    logger.warning(
                        f"비활성 WebSocket 연결 감지: {info.get('client_id', 'unknown')} "
                        f"(비활성 시간: {int(inactive_seconds)}초)"
                    )
            
            # 비활성 연결 정리
            for websocket in disconnected_clients:
                try:
                    # 연결 종료 메시지 전송 시도
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "connection_timeout",
                            "data": {"message": "비활성으로 인한 연결 종료"},
                            "timestamp": datetime.now().isoformat()
                        }, ensure_ascii=False),
                        websocket
                    )
                    
                    # WebSocket 연결 종료
                    await websocket.close()
                    
                except Exception:
                    pass  # 이미 연결이 끊어진 경우 무시
                finally:
                    manager.disconnect(websocket)
            
            # 연결 상태 로깅 (5분마다)
            if int(current_time.timestamp()) % 300 == 0:  # 5분마다
                active_connections = manager.get_connection_count()
                if active_connections > 0:
                    logger.info(f"활성 WebSocket 연결 수: {active_connections}")
            
            await asyncio.sleep(30)  # 30초마다 체크
            
        except asyncio.CancelledError:
            logger.info("WebSocket 연결 상태 모니터링이 취소되었습니다")
            break
        except Exception as e:
            logger.error(f"연결 상태 모니터링 오류: {e}")
            await asyncio.sleep(30)