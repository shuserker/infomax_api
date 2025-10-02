"""
WebSocket 실시간 통신 API
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# 데이터 모델
class WSMessage(BaseModel):
    type: str  # status_update, service_event, alert, log_update
    data: dict
    timestamp: datetime

# 연결된 WebSocket 클라이언트 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.client_info: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """클라이언트 연결"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.client_info[websocket] = {
            "client_id": client_id or f"client_{len(self.active_connections)}",
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        logger.info(f"WebSocket 클라이언트 연결: {self.client_info[websocket]['client_id']}")
    
    def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제"""
        if websocket in self.active_connections:
            client_info = self.client_info.get(websocket, {})
            client_id = client_info.get("client_id", "unknown")
            
            self.active_connections.remove(websocket)
            if websocket in self.client_info:
                del self.client_info[websocket]
            
            logger.info(f"WebSocket 클라이언트 연결 해제: {client_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """특정 클라이언트에게 메시지 전송"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"개인 메시지 전송 실패: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """모든 연결된 클라이언트에게 브로드캐스트"""
        if not self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"브로드캐스트 전송 실패: {e}")
                disconnected.add(connection)
        
        # 연결이 끊어진 클라이언트 정리
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: dict):
        """JSON 데이터 브로드캐스트"""
        message = json.dumps(data, default=str, ensure_ascii=False)
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """연결된 클라이언트 수 반환"""
        return len(self.active_connections)
    
    def get_client_info(self) -> list:
        """클라이언트 정보 목록 반환"""
        return [
            {
                "client_id": info["client_id"],
                "connected_at": info["connected_at"],
                "last_ping": info["last_ping"]
            }
            for info in self.client_info.values()
        ]

# 전역 연결 매니저
manager = ConnectionManager()

@router.websocket("/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """로그 스트리밍 전용 WebSocket 엔드포인트"""
    await websocket.accept()
    logger.info("로그 스트리밍 WebSocket 연결이 설정되었습니다")
    
    try:
        # 연결 확인 메시지 전송
        await websocket.send_json({
            "type": "log_stream_connected",
            "data": {"message": "로그 스트리밍이 시작되었습니다"},
            "timestamp": datetime.now().isoformat()
        })
        
        # 실시간 로그 생성 및 전송 (데모용)
        log_counter = 0
        log_levels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
        log_sources = ["posco_news", "github_pages", "deployment", "webhook_system", "cache_monitor", "message_system"]
        
        while True:
            try:
                # 데모 로그 엔트리 생성
                import random
                import uuid
                
                level = random.choice(log_levels)
                source = random.choice(log_sources)
                log_counter += 1
                
                # 레벨에 따른 메시지 생성
                if level == "ERROR":
                    message = f"[{source}] 오류 발생: 연결 실패 또는 처리 오류 #{log_counter}"
                elif level == "WARN":
                    message = f"[{source}] 경고: 성능 저하 또는 리소스 부족 감지 #{log_counter}"
                elif level == "CRITICAL":
                    message = f"[{source}] 심각한 오류: 시스템 중단 위험 #{log_counter}"
                elif level == "DEBUG":
                    message = f"[{source}] 디버그: 상세 실행 정보 #{log_counter}"
                else:
                    message = f"[{source}] 정보: 정상 작업 수행 중 #{log_counter}"
                
                log_entry = {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat() + "Z",
                    "level": level,
                    "source": source,
                    "message": message,
                    "metadata": {
                        "entry_number": log_counter,
                        "source_version": "1.0.0",
                        "process_id": 1234 + (log_counter % 10)
                    }
                }
                
                # WebSocket으로 로그 전송
                await websocket.send_json({
                    "type": "log_entry",
                    "data": log_entry,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 1-3초 랜덤 대기 (실제 로그 생성 패턴 시뮬레이션)
                await asyncio.sleep(random.uniform(1, 3))
                
            except WebSocketDisconnect:
                logger.info("로그 스트리밍 WebSocket 연결이 종료되었습니다")
                break
            except Exception as e:
                logger.error(f"로그 스트리밍 중 오류: {e}")
                await asyncio.sleep(2)
                
    except WebSocketDisconnect:
        logger.info("로그 스트리밍 WebSocket 연결이 종료되었습니다")
    except Exception as e:
        logger.error(f"로그 스트리밍 WebSocket 연결 중 오류 발생: {e}")
    finally:
        logger.info("로그 스트리밍 WebSocket 연결 정리 완료")

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """WebSocket 연결 엔드포인트"""
    await manager.connect(websocket, client_id)
    
    try:
        # 연결 확인 메시지 전송
        welcome_message = WSMessage(
            type="connection_established",
            data={
                "message": "WebSocket 연결이 성공적으로 설정되었습니다",
                "client_id": manager.client_info[websocket]["client_id"],
                "server_time": datetime.now()
            },
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            welcome_message.model_dump_json(default=str), 
            websocket
        )
        
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
                    data={"message": "ping"},
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
            subscription_type = data.get("subscription", "all")
            response = WSMessage(
                type="subscription_confirmed",
                data={
                    "subscription": subscription_type,
                    "message": f"{subscription_type} 구독이 확인되었습니다"
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
        
        else:
            logger.warning(f"알 수 없는 메시지 타입: {message_type}")
            
    except json.JSONDecodeError:
        logger.error(f"잘못된 JSON 메시지: {message}")
    except Exception as e:
        logger.error(f"클라이언트 메시지 처리 오류: {e}")

async def send_current_status(websocket: WebSocket):
    """현재 시스템 상태 전송"""
    try:
        # 현재 시스템 상태 수집 (실제로는 metrics API에서 가져옴)
        status_data = {
            "services": [
                {"id": "posco_news", "status": "running"},
                {"id": "github_pages", "status": "stopped"},
                {"id": "cache_monitor", "status": "running"},
            ],
            "system_metrics": {
                "cpu_percent": 25.5,
                "memory_percent": 68.2,
                "disk_usage": 45.8
            },
            "connection_count": manager.get_connection_count()
        }
        
        status_message = WSMessage(
            type="status_update",
            data=status_data,
            timestamp=datetime.now()
        )
        
        await manager.send_personal_message(
            status_message.model_dump_json(default=str), 
            websocket
        )
        
    except Exception as e:
        logger.error(f"상태 전송 오류: {e}")

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

# 주기적인 상태 업데이트 태스크
async def periodic_status_broadcast():
    """주기적인 상태 업데이트 브로드캐스트"""
    logger.info("WebSocket 주기적 상태 브로드캐스트 태스크 시작")
    
    while True:
        try:
            if manager.get_connection_count() > 0:
                # 5초마다 시스템 메트릭 브로드캐스트
                await broadcast_system_metrics()
                
                # 10초마다 서비스 상태 브로드캐스트
                if asyncio.get_event_loop().time() % 10 < 5:
                    await broadcast_service_status()
            
            await asyncio.sleep(5)
            
        except asyncio.CancelledError:
            logger.info("주기적 상태 브로드캐스트 태스크가 취소되었습니다")
            break
        except Exception as e:
            logger.error(f"주기적 상태 브로드캐스트 오류: {e}")
            await asyncio.sleep(5)

async def broadcast_system_metrics():
    """시스템 메트릭 브로드캐스트"""
    try:
        # 실제로는 metrics API에서 데이터를 가져와야 함
        import psutil
        
        # 시스템 메트릭 수집
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        
        # 디스크 사용량 (Windows/Linux 호환)
        try:
            disk_usage = psutil.disk_usage('/').percent
        except:
            try:
                disk_usage = psutil.disk_usage('C:\\').percent
            except:
                disk_usage = 0
        
        # 네트워크 상태 확인
        network_status = "connected"
        try:
            net_io = psutil.net_io_counters()
            if net_io.bytes_sent == 0 and net_io.bytes_recv == 0:
                network_status = "disconnected"
        except:
            network_status = "unknown"
        
        metrics_data = {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory.percent, 1),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_usage": round(disk_usage, 1),
            "network_status": network_status,
            "connection_count": manager.get_connection_count(),
            "uptime": get_system_uptime(),
            "timestamp": datetime.now()
        }
        
        metrics_message = WSMessage(
            type="metrics_update",
            data=metrics_data,
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(metrics_message.model_dump(default=str))
        
    except Exception as e:
        logger.error(f"시스템 메트릭 브로드캐스트 오류: {e}")

async def broadcast_service_status():
    """서비스 상태 브로드캐스트"""
    try:
        # 서비스 상태 수집 (실제로는 services API에서 가져와야 함)
        services_data = await get_current_services_status()
        
        status_message = WSMessage(
            type="services_update",
            data={
                "services": services_data,
                "total_services": len(services_data),
                "running_services": len([s for s in services_data if s.get("status") == "running"]),
                "timestamp": datetime.now()
            },
            timestamp=datetime.now()
        )
        
        await manager.broadcast_json(status_message.model_dump(default=str))
        
    except Exception as e:
        logger.error(f"서비스 상태 브로드캐스트 오류: {e}")

def get_system_uptime():
    """시스템 업타임 반환 (초 단위)"""
    try:
        import psutil
        boot_time = psutil.boot_time()
        current_time = datetime.now().timestamp()
        return int(current_time - boot_time)
    except:
        return 0

async def get_current_services_status():
    """현재 서비스 상태 조회"""
    try:
        # 실제로는 services API에서 데이터를 가져와야 함
        # 여기서는 임시 데이터 반환
        services = [
            {
                "id": "posco_news",
                "name": "POSCO 뉴스 모니터",
                "status": "running",
                "uptime": 3600,
                "description": "POSCO 뉴스 시스템 모니터링"
            },
            {
                "id": "github_pages",
                "name": "GitHub Pages 모니터",
                "status": "stopped",
                "uptime": 0,
                "description": "GitHub Pages 상태 모니터링"
            },
            {
                "id": "cache_monitor",
                "name": "캐시 모니터",
                "status": "running",
                "uptime": 1800,
                "description": "데이터 캐시 상태 모니터링"
            },
            {
                "id": "deployment",
                "name": "배포 시스템",
                "status": "idle",
                "uptime": 0,
                "description": "자동 배포 시스템"
            },
            {
                "id": "webhook",
                "name": "웹훅 시스템",
                "status": "running",
                "uptime": 2400,
                "description": "Discord/Slack 웹훅 전송"
            }
        ]
        
        return services
        
    except Exception as e:
        logger.error(f"서비스 상태 조회 오류: {e}")
        return []

# 연결 상태 모니터링 함수
async def monitor_connection_health():
    """WebSocket 연결 상태 모니터링"""
    while True:
        try:
            current_time = datetime.now()
            disconnected_clients = []
            
            # 비활성 연결 감지 (30초 이상 응답 없음)
            for websocket, info in manager.client_info.items():
                last_ping = info.get("last_ping", info.get("connected_at"))
                if (current_time - last_ping).total_seconds() > 30:
                    disconnected_clients.append(websocket)
            
            # 비활성 연결 정리
            for websocket in disconnected_clients:
                logger.warning(f"비활성 WebSocket 연결 정리: {manager.client_info.get(websocket, {}).get('client_id', 'unknown')}")
                manager.disconnect(websocket)
            
            await asyncio.sleep(10)  # 10초마다 체크
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"연결 상태 모니터링 오류: {e}")
            await asyncio.sleep(10)