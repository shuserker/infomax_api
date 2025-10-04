"""
시스템 제어 API 엔드포인트
전체 시스템 시작/중지/재시작 및 상태 조회 기능
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# 핵심 모듈 임포트
try:
    from core.watchhamster_monitor import WatchHamsterMonitor
    from core.infomax_client import InfomaxAPIClient
    from core.news_parser import NewsDataParser
    from core.webhook_sender import DoorayWebhookSender
except ImportError as e:
    logger.warning(f"일부 core 모듈 임포트 실패: {e}")
    # 임포트 실패 시 더미 클래스 사용
    class WatchHamsterMonitor:
        async def start_monitoring(self): pass
        async def stop_monitoring(self): pass
        @property
        def is_running(self): return False
    
    class InfomaxAPIClient:
        def __init__(self, base_url): pass
        async def health_check(self): return False
        async def close(self): pass
    
    class NewsDataParser:
        pass
    
    class DoorayWebhookSender:
        async def send_system_status_report(self, data): pass

# 데이터 모델
class SystemStatus(BaseModel):
    overall_status: str  # healthy, warning, critical, starting, stopping
    services_running: int
    services_total: int
    uptime: int
    last_check: datetime
    components: Dict[str, str]  # 각 컴포넌트별 상태
    metrics: Optional[Dict] = None

class SystemAction(BaseModel):
    action: str  # start, stop, restart
    force: bool = False
    components: Optional[List[str]] = None  # 특정 컴포넌트만 제어

# 전역 시스템 상태
system_state = {
    "status": "running",
    "start_time": datetime.now(),
    "components": {
        "watchhamster_monitor": "running",
        "infomax_client": "running", 
        "news_parser": "running",
        "webhook_sender": "running",
        "api_server": "running"
    },
    "is_starting": False,
    "is_stopping": False
}

# 핵심 컴포넌트 인스턴스
monitor_instance = None
api_client_instance = None
news_parser_instance = None
webhook_sender_instance = None

@router.get("/status")
async def get_system_status():
    """시스템 전체 상태 조회"""
    logger.info("시스템 상태 조회 요청")
    
    try:
        # 서비스 상태 수집
        try:
            from api.services import SERVICES_DATA
            running_services = sum(1 for service in SERVICES_DATA.values() if service["status"] == "running")
            total_services = len(SERVICES_DATA)
        except (ImportError, AttributeError):
            # SERVICES_DATA가 없으면 기본값 사용
            running_services = 1
            total_services = 1
        
        # 업타임 계산
        uptime = int((datetime.now() - system_state["start_time"]).total_seconds())
        
        # 전체 상태 판단
        overall_status = "healthy"
        if system_state["is_starting"]:
            overall_status = "starting"
        elif system_state["is_stopping"]:
            overall_status = "stopping"
        elif running_services < total_services * 0.5:
            overall_status = "critical"
        elif running_services < total_services * 0.8:
            overall_status = "warning"
        
        # 시스템 메트릭 수집
        try:
            from api.metrics import get_system_metrics
            metrics_data = await get_system_metrics()
            metrics = metrics_data.dict() if hasattr(metrics_data, 'dict') else metrics_data
        except Exception as e:
            logger.warning(f"메트릭 수집 실패: {e}")
            metrics = None
        
        status = SystemStatus(
            overall_status=overall_status,
            services_running=running_services,
            services_total=total_services,
            uptime=uptime,
            last_check=datetime.now(),
            components=system_state["components"].copy(),
            metrics=metrics
        )
        
        return status
        
    except Exception as e:
        logger.error(f"시스템 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="시스템 상태 조회 중 오류가 발생했습니다")

@router.post("/start")
async def start_system(background_tasks: BackgroundTasks, action: SystemAction = None):
    """전체 시스템 시작"""
    logger.info("전체 시스템 시작 요청")
    
    try:
        if system_state["is_starting"]:
            return {"message": "시스템이 이미 시작 중입니다", "status": "starting"}
        
        if system_state["status"] == "running":
            return {"message": "시스템이 이미 실행 중입니다", "status": "running"}
        
        # 시작 상태로 변경
        system_state["is_starting"] = True
        system_state["status"] = "starting"
        
        # 백그라운드에서 시스템 시작 작업 수행
        background_tasks.add_task(_start_system_task, action)
        
        return {"message": "전체 시스템 시작 중...", "status": "starting"}
        
    except Exception as e:
        logger.error(f"시스템 시작 요청 실패: {e}")
        system_state["is_starting"] = False
        raise HTTPException(status_code=500, detail="시스템 시작 요청 처리 중 오류가 발생했습니다")

@router.post("/stop")
async def stop_system(background_tasks: BackgroundTasks, action: SystemAction = None):
    """전체 시스템 중지"""
    logger.info("전체 시스템 중지 요청")
    
    try:
        if system_state["is_stopping"]:
            return {"message": "시스템이 이미 중지 중입니다", "status": "stopping"}
        
        if system_state["status"] == "stopped":
            return {"message": "시스템이 이미 중지되어 있습니다", "status": "stopped"}
        
        # 중지 상태로 변경
        system_state["is_stopping"] = True
        system_state["status"] = "stopping"
        
        # 백그라운드에서 시스템 중지 작업 수행
        background_tasks.add_task(_stop_system_task, action)
        
        return {"message": "전체 시스템 중지 중...", "status": "stopping"}
        
    except Exception as e:
        logger.error(f"시스템 중지 요청 실패: {e}")
        system_state["is_stopping"] = False
        raise HTTPException(status_code=500, detail="시스템 중지 요청 처리 중 오류가 발생했습니다")

@router.post("/restart")
async def restart_system(background_tasks: BackgroundTasks, action: SystemAction = None):
    """전체 시스템 재시작"""
    logger.info("전체 시스템 재시작 요청")
    
    try:
        if system_state["is_starting"] or system_state["is_stopping"]:
            return {"message": "시스템이 이미 작업 중입니다", "status": system_state["status"]}
        
        # 재시작 상태로 변경
        system_state["is_stopping"] = True
        system_state["status"] = "restarting"
        
        # 백그라운드에서 시스템 재시작 작업 수행
        background_tasks.add_task(_restart_system_task, action)
        
        return {"message": "전체 시스템 재시작 중...", "status": "restarting"}
        
    except Exception as e:
        logger.error(f"시스템 재시작 요청 실패: {e}")
        system_state["is_stopping"] = False
        system_state["is_starting"] = False
        raise HTTPException(status_code=500, detail="시스템 재시작 요청 처리 중 오류가 발생했습니다")

# 백그라운드 작업 함수들
async def _start_system_task(action: SystemAction = None):
    """시스템 시작 백그라운드 작업"""
    global monitor_instance, api_client_instance, news_parser_instance, webhook_sender_instance
    
    logger.info("시스템 시작 작업 실행")
    
    try:
        # 1. 핵심 컴포넌트 초기화
        logger.info("핵심 컴포넌트 초기화 중...")
        
        # WatchHamster 모니터 시작
        if not monitor_instance:
            monitor_instance = WatchHamsterMonitor()
            await monitor_instance.start_monitoring()
            system_state["components"]["watchhamster_monitor"] = "running"
            
            # services.py에 인스턴스 등록
            from api.services import set_service_instance
            set_service_instance("watchhamster_monitor", monitor_instance)
            logger.info("WatchHamster 모니터 시작 완료")
        
        await asyncio.sleep(1)
        
        # INFOMAX API 클라이언트 초기화
        if not api_client_instance:
            api_client_instance = InfomaxAPIClient(
                base_url="https://global-api.einfomax.co.kr/apis/posco/news"
            )
            # 연결 테스트
            health_ok = await api_client_instance.health_check()
            system_state["components"]["infomax_client"] = "running" if health_ok else "error"
            
            # services.py에 인스턴스 등록
            from api.services import set_service_instance
            set_service_instance("infomax_client", api_client_instance)
            logger.info(f"INFOMAX API 클라이언트 초기화 완료: {health_ok}")
        
        await asyncio.sleep(1)
        
        # 뉴스 파서 초기화
        if not news_parser_instance:
            news_parser_instance = NewsDataParser()
            system_state["components"]["news_parser"] = "running"
            
            # services.py에 인스턴스 등록
            from api.services import set_service_instance
            set_service_instance("news_parser", news_parser_instance)
            logger.info("뉴스 파서 초기화 완료")
        
        await asyncio.sleep(1)
        
        # 웹훅 발송자 초기화
        if not webhook_sender_instance:
            webhook_sender_instance = DoorayWebhookSender()
            system_state["components"]["webhook_sender"] = "running"
            
            # services.py에 인스턴스 등록
            from api.services import set_service_instance
            set_service_instance("webhook_sender", webhook_sender_instance)
            logger.info("웹훅 발송자 초기화 완료")
        
        # 2. 서비스들 시작
        logger.info("서비스들 시작 중...")
        from api.services import SERVICES_DATA, SERVICE_START_TIMES
        import time
        
        # 중요한 서비스들 먼저 시작
        priority_services = ["posco_news_monitor", "git_monitor", "webhook_dispatcher"]
        
        for service_id in priority_services:
            if service_id in SERVICES_DATA and SERVICES_DATA[service_id]["status"] != "running":
                SERVICES_DATA[service_id]["status"] = "running"
                SERVICE_START_TIMES[service_id] = time.time()
                SERVICES_DATA[service_id].pop("last_error", None)
                logger.info(f"서비스 시작: {service_id}")
                await asyncio.sleep(0.5)
        
        # 3. 시스템 상태 업데이트
        system_state["status"] = "running"
        system_state["is_starting"] = False
        system_state["start_time"] = datetime.now()
        
        logger.info("전체 시스템 시작 완료")
        
        # 4. 웹훅으로 시스템 시작 알림 전송
        if webhook_sender_instance:
            try:
                await webhook_sender_instance.send_system_status_report({
                    "event": "system_started",
                    "message": "WatchHamster 시스템이 성공적으로 시작되었습니다",
                    "timestamp": datetime.now(),
                    "components": system_state["components"]
                })
            except Exception as e:
                logger.warning(f"시스템 시작 알림 전송 실패: {e}")
        
    except Exception as e:
        logger.error(f"시스템 시작 실패: {e}")
        
        # 오류 상태로 업데이트
        system_state["status"] = "error"
        system_state["is_starting"] = False
        
        # 실패한 컴포넌트 상태 업데이트
        for component in system_state["components"]:
            if system_state["components"][component] != "running":
                system_state["components"][component] = "error"

async def _stop_system_task(action: SystemAction = None):
    """시스템 중지 백그라운드 작업"""
    global monitor_instance, api_client_instance, news_parser_instance, webhook_sender_instance
    
    logger.info("시스템 중지 작업 실행")
    
    try:
        # 1. 웹훅으로 시스템 중지 알림 전송 (중지 전에)
        if webhook_sender_instance:
            try:
                await webhook_sender_instance.send_system_status_report({
                    "event": "system_stopping",
                    "message": "WatchHamster 시스템이 중지되고 있습니다",
                    "timestamp": datetime.now(),
                    "components": system_state["components"]
                })
            except Exception as e:
                logger.warning(f"시스템 중지 알림 전송 실패: {e}")
        
        # 2. 서비스들 중지
        logger.info("서비스들 중지 중...")
        from api.services import SERVICES_DATA, SERVICE_START_TIMES
        
        # 중요하지 않은 서비스들 먼저 중지
        non_critical_services = ["posco_news_monitor", "git_monitor", "webhook_dispatcher", "api_health_checker"]
        
        for service_id in non_critical_services:
            if service_id in SERVICES_DATA and SERVICES_DATA[service_id]["status"] == "running":
                SERVICES_DATA[service_id]["status"] = "stopped"
                SERVICES_DATA[service_id]["last_error"] = "시스템 중지로 인한 서비스 중지"
                if service_id in SERVICE_START_TIMES:
                    del SERVICE_START_TIMES[service_id]
                logger.info(f"서비스 중지: {service_id}")
                await asyncio.sleep(0.5)
        
        # 3. 핵심 컴포넌트 중지
        logger.info("핵심 컴포넌트 중지 중...")
        
        # WatchHamster 모니터 중지
        if monitor_instance:
            try:
                await monitor_instance.stop_monitoring()
                system_state["components"]["watchhamster_monitor"] = "stopped"
                monitor_instance = None
                logger.info("WatchHamster 모니터 중지 완료")
            except Exception as e:
                logger.error(f"WatchHamster 모니터 중지 실패: {e}")
        
        await asyncio.sleep(1)
        
        # API 클라이언트 정리
        if api_client_instance:
            try:
                await api_client_instance.close()
                system_state["components"]["infomax_client"] = "stopped"
                api_client_instance = None
                logger.info("INFOMAX API 클라이언트 정리 완료")
            except Exception as e:
                logger.error(f"API 클라이언트 정리 실패: {e}")
        
        # 뉴스 파서 정리
        if news_parser_instance:
            system_state["components"]["news_parser"] = "stopped"
            news_parser_instance = None
            logger.info("뉴스 파서 정리 완료")
        
        # 웹훅 발송자 정리
        if webhook_sender_instance:
            system_state["components"]["webhook_sender"] = "stopped"
            webhook_sender_instance = None
            logger.info("웹훅 발송자 정리 완료")
        
        # 4. 시스템 상태 업데이트
        system_state["status"] = "stopped"
        system_state["is_stopping"] = False
        
        logger.info("전체 시스템 중지 완료")
        
    except Exception as e:
        logger.error(f"시스템 중지 실패: {e}")
        
        # 오류 상태로 업데이트
        system_state["status"] = "error"
        system_state["is_stopping"] = False

async def _restart_system_task(action: SystemAction = None):
    """시스템 재시작 백그라운드 작업"""
    logger.info("시스템 재시작 작업 실행")
    
    try:
        # 1. 시스템 중지
        logger.info("시스템 중지 단계...")
        await _stop_system_task(action)
        
        # 잠시 대기
        await asyncio.sleep(2)
        
        # 2. 시스템 시작
        logger.info("시스템 시작 단계...")
        system_state["is_starting"] = True
        system_state["is_stopping"] = False
        await _start_system_task(action)
        
        logger.info("전체 시스템 재시작 완료")
        
    except Exception as e:
        logger.error(f"시스템 재시작 실패: {e}")
        
        # 오류 상태로 업데이트
        system_state["status"] = "error"
        system_state["is_starting"] = False
        system_state["is_stopping"] = False

# 시스템 상태 조회 헬퍼 함수들
async def get_component_status(component_name: str) -> str:
    """특정 컴포넌트 상태 조회"""
    try:
        if component_name == "watchhamster_monitor":
            return "running" if monitor_instance else "stopped"
        elif component_name == "infomax_client":
            if api_client_instance:
                health_ok = await api_client_instance.health_check()
                return "running" if health_ok else "error"
            return "stopped"
        elif component_name == "news_parser":
            return "running" if news_parser_instance else "stopped"
        elif component_name == "webhook_sender":
            return "running" if webhook_sender_instance else "stopped"
        else:
            return "unknown"
    except Exception as e:
        logger.error(f"컴포넌트 상태 조회 실패 ({component_name}): {e}")
        return "error"

async def update_component_statuses():
    """모든 컴포넌트 상태 업데이트"""
    try:
        for component in system_state["components"]:
            status = await get_component_status(component)
            system_state["components"][component] = status
    except Exception as e:
        logger.error(f"컴포넌트 상태 업데이트 실패: {e}")

# 시스템 초기화 함수 (서버 시작 시 호출)
async def initialize_system():
    """시스템 초기화"""
    logger.info("시스템 초기화 시작")
    
    try:
        # 컴포넌트 상태 업데이트
        await update_component_statuses()
        
        # 시스템 상태를 running으로 설정
        system_state["status"] = "running"
        system_state["start_time"] = datetime.now()
        
        logger.info("시스템 초기화 완료")
        
    except Exception as e:
        logger.error(f"시스템 초기화 실패: {e}")
        system_state["status"] = "error"


@router.get("/health")
async def get_system_health():
    """시스템 헬스 체크 (간단 버전)"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": int((datetime.now() - system_state["start_time"]).total_seconds()),
            "components": system_state["components"]
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))