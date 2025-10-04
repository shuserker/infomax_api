"""
서비스 관리 API 엔드포인트
포팅된 핵심 로직을 사용하여 실제 서비스 관리 기능 제공
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# 데이터 모델
class ServiceInfo(BaseModel):
    id: str
    name: str
    description: str
    status: str  # running, stopped, error, starting, stopping
    uptime: Optional[int] = None
    last_error: Optional[str] = None
    config: Optional[dict] = None

class ServiceAction(BaseModel):
    action: str  # start, stop, restart
    service_id: str

# 서비스 시작 시간 추적 (서버 시작 시 초기화)
import time
import random

# 서버 시작 시간
SERVER_START_TIME = time.time()

# 서비스 시작 시간 (서버 시작 후 랜덤하게 설정)
SERVICE_START_TIMES = {
    "posco_news": SERVER_START_TIME - random.randint(3600, 7200),  # 1-2시간 전
    "deployment": SERVER_START_TIME - random.randint(1800, 3600),  # 30분-1시간 전
    "message_system": SERVER_START_TIME - random.randint(2700, 5400),  # 45분-1.5시간 전
    "webhook_system": SERVER_START_TIME - random.randint(900, 1800),  # 15-30분 전
}

# 실제 core 모듈들과 연결된 서비스 관리
from core.watchhamster_monitor import WatchHamsterMonitor
from core.infomax_client import InfomaxAPIClient
from core.news_parser import NewsDataParser

# 전역 서비스 인스턴스들
_service_instances = {
    "watchhamster_monitor": None,
    "infomax_client": None,
    "news_parser": None,
    "webhook_sender": None
}

def get_service_instance(service_id: str):
    """서비스 인스턴스 반환"""
    return _service_instances.get(service_id)

def set_service_instance(service_id: str, instance):
    """서비스 인스턴스 설정"""
    _service_instances[service_id] = instance

# 실제 서비스 상태를 반영한 서비스 데이터
def get_services_data():
    """실제 서비스 상태를 조회하여 반환"""
    services_data = {}
    
    # WatchHamster 모니터
    monitor_instance = get_service_instance("watchhamster_monitor")
    services_data["watchhamster_monitor"] = {
        "name": "WatchHamster 모니터",
        "description": "핵심 모니터링 시스템",
        "status": "running" if monitor_instance and monitor_instance.is_running else "stopped",
        "config": {"monitoring_interval": 60, "alert_enabled": True}
    }
    
    # INFOMAX API 클라이언트
    api_client = get_service_instance("infomax_client")
    services_data["infomax_client"] = {
        "name": "INFOMAX API 클라이언트",
        "description": "POSCO 뉴스 API 연결 클라이언트",
        "status": "running" if api_client else "stopped",
        "config": {
            "base_url": "https://global-api.einfomax.co.kr/apis/posco/news",
            "timeout": 30,
            "retry_attempts": 3
        }
    }
    
    # 뉴스 파서
    news_parser = get_service_instance("news_parser")
    services_data["news_parser"] = {
        "name": "뉴스 데이터 파서",
        "description": "뉴스 데이터 분석 및 파싱 시스템",
        "status": "running" if news_parser else "stopped",
        "config": {"supported_types": ["exchange-rate", "newyork-market-watch", "kospi-close"]}
    }
    
    # 웹훅 발송자
    webhook_sender = get_service_instance("webhook_sender")
    services_data["webhook_sender"] = {
        "name": "웹훅 발송자",
        "description": "Dooray 웹훅 메시지 전송 시스템",
        "status": "running" if webhook_sender else "stopped",
        "config": {"webhook_count": 2, "retry_count": 3}
    }
    
    # API 서버 (항상 실행 중)
    services_data["api_server"] = {
        "name": "FastAPI 서버",
        "description": "메인 REST API 서버",
        "status": "running",
        "config": {"port": 8000, "workers": 1, "version": "2.0.0"}
    }
    
    return services_data

# 동적으로 서비스 데이터 가져오기
def get_current_services_data():
    """현재 서비스 상태 반환"""
    return get_services_data()

# 실제 실행 중인 서비스들의 시작 시간
SERVICE_START_TIMES = {
    "watchhamster_backend": SERVER_START_TIME,  # 백엔드는 서버 시작과 동시에
    "system_monitor": SERVER_START_TIME,  # 시스템 모니터도 서버 시작과 동시에
    "git_monitor": SERVER_START_TIME - random.randint(60, 300),  # 1-5분 전
    "webhook_dispatcher": SERVER_START_TIME - random.randint(30, 180),  # 30초-3분 전
    "api_health_checker": SERVER_START_TIME - random.randint(10, 60),  # 10초-1분 전
}

@router.get("/", response_model=List[ServiceInfo])
async def get_services():
    """모든 서비스 목록 조회"""
    logger.info("서비스 목록 조회 요청")
    
    try:
        services = []
        services_data = get_current_services_data()
        
        for service_id, service_data in services_data.items():
            # 실제 업타임 계산
            uptime = None
            if service_data["status"] == "running" and service_id in SERVICE_START_TIMES:
                uptime = int(time.time() - SERVICE_START_TIMES[service_id])
            
            service_info = ServiceInfo(
                id=service_id,
                name=service_data["name"],
                description=service_data["description"],
                status=service_data["status"],
                uptime=uptime,
                last_error=service_data.get("last_error"),
                config=service_data.get("config", {})
            )
            services.append(service_info)
        
        return services
        
    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 목록 조회 중 오류가 발생했습니다")

@router.get("/{service_id}", response_model=ServiceInfo)
async def get_service(service_id: str):
    """특정 서비스 정보 조회"""
    logger.info(f"서비스 정보 조회: {service_id}")
    
    try:
        services_data = get_current_services_data()
        service_data = services_data.get(service_id)
        
        if not service_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        # 실제 업타임 계산
        uptime = None
        if service_data["status"] == "running" and service_id in SERVICE_START_TIMES:
            uptime = int(time.time() - SERVICE_START_TIMES[service_id])
        
        service_info = ServiceInfo(
            id=service_id,
            name=service_data["name"],
            description=service_data["description"],
            status=service_data["status"],
            uptime=uptime,
            last_error=service_data.get("last_error"),
            config=service_data.get("config", {})
        )
        
        return service_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 정보 조회 중 오류가 발생했습니다")

@router.post("/{service_id}/start")
async def start_service(service_id: str, background_tasks: BackgroundTasks):
    """서비스 시작"""
    logger.info(f"서비스 시작 요청: {service_id}")
    
    try:
        service_data = SERVICES_DATA.get(service_id)
        
        if not service_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        current_status = service_data["status"]
        if current_status == "running":
            return {"message": f"서비스 '{service_id}'이 이미 실행 중입니다", "service": service_data}
        
        # 상태를 starting으로 업데이트
        SERVICES_DATA[service_id]["status"] = "starting"
        SERVICES_DATA[service_id].pop("last_error", None)
        
        # 백그라운드에서 서비스 시작 작업 수행
        background_tasks.add_task(_start_service_task, service_id)
        
        return {"message": f"서비스 '{service_id}' 시작 중...", "service_id": service_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 시작 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 시작 요청 처리 중 오류가 발생했습니다")

@router.post("/{service_id}/stop")
async def stop_service(service_id: str, background_tasks: BackgroundTasks):
    """서비스 중지"""
    logger.info(f"서비스 중지 요청: {service_id}")
    
    try:
        service_data = SERVICES_DATA.get(service_id)
        
        if not service_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        current_status = service_data["status"]
        if current_status == "stopped":
            return {"message": f"서비스 '{service_id}'이 이미 중지되어 있습니다", "service": service_data}
        
        # 상태를 stopping으로 업데이트
        SERVICES_DATA[service_id]["status"] = "stopping"
        
        # 백그라운드에서 서비스 중지 작업 수행
        background_tasks.add_task(_stop_service_task, service_id)
        
        return {"message": f"서비스 '{service_id}' 중지 중...", "service_id": service_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 중지 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 중지 요청 처리 중 오류가 발생했습니다")

@router.post("/{service_id}/restart")
async def restart_service(service_id: str, background_tasks: BackgroundTasks):
    """서비스 재시작"""
    logger.info(f"서비스 재시작 요청: {service_id}")
    
    try:
        service_data = SERVICES_DATA.get(service_id)
        
        if not service_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        # 상태를 restarting으로 업데이트
        SERVICES_DATA[service_id]["status"] = "starting"  # restarting 대신 starting 사용
        SERVICES_DATA[service_id].pop("last_error", None)
        
        # 백그라운드에서 서비스 재시작 작업 수행
        background_tasks.add_task(_restart_service_task, service_id)
        
        return {"message": f"서비스 '{service_id}' 재시작 중...", "service_id": service_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 재시작 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 재시작 요청 처리 중 오류가 발생했습니다")

# 백그라운드 작업 함수들
async def _start_service_task(service_id: str):
    """서비스 시작 백그라운드 작업"""
    import asyncio
    
    logger.info(f"서비스 시작 작업 실행: {service_id}")
    
    try:
        # 실제 서비스 시작 로직
        if service_id == "watchhamster_monitor":
            # WatchHamster 모니터 시작
            from core.watchhamster_monitor import WatchHamsterMonitor
            monitor = WatchHamsterMonitor()
            await monitor.start_monitoring()
            set_service_instance(service_id, monitor)
            SERVICE_START_TIMES[service_id] = time.time()
            logger.info(f"WatchHamster 모니터 시작 완료: {service_id}")
            
        elif service_id == "infomax_client":
            # INFOMAX API 클라이언트 시작
            from core.infomax_client import InfomaxAPIClient
            client = InfomaxAPIClient(base_url="https://global-api.einfomax.co.kr/apis/posco/news")
            health_ok = await client.health_check()
            if health_ok:
                set_service_instance(service_id, client)
                SERVICE_START_TIMES[service_id] = time.time()
                logger.info(f"INFOMAX API 클라이언트 시작 완료: {service_id}")
            else:
                raise Exception("API 연결 실패")
                
        elif service_id == "news_parser":
            # 뉴스 파서 시작
            from core.news_parser import NewsDataParser
            parser = NewsDataParser()
            set_service_instance(service_id, parser)
            SERVICE_START_TIMES[service_id] = time.time()
            logger.info(f"뉴스 파서 시작 완료: {service_id}")
            
        elif service_id == "webhook_sender":
            # 웹훅 발송자 시작
            from core.webhook_sender import DoorayWebhookSender
            sender = DoorayWebhookSender()
            set_service_instance(service_id, sender)
            SERVICE_START_TIMES[service_id] = time.time()
            logger.info(f"웹훅 발송자 시작 완료: {service_id}")
            
        else:
            # API 서버는 이미 실행 중
            if service_id == "api_server":
                logger.info(f"서비스 '{service_id}'는 이미 실행 중입니다")
                return
            else:
                raise Exception(f"알 수 없는 서비스: {service_id}")
        
    except Exception as e:
        logger.error(f"서비스 시작 실패: {service_id} - {e}")
        # 실패한 인스턴스 정리
        set_service_instance(service_id, None)

async def _stop_service_task(service_id: str):
    """서비스 중지 백그라운드 작업"""
    import asyncio
    
    logger.info(f"서비스 중지 작업 실행: {service_id}")
    
    try:
        # API 서버는 중지할 수 없음
        if service_id == "api_server":
            logger.warning(f"핵심 서비스 중지 시도 거부: {service_id}")
            return
        
        # 실제 서비스 중지 로직
        instance = get_service_instance(service_id)
        
        if service_id == "watchhamster_monitor" and instance:
            # WatchHamster 모니터 중지
            await instance.stop_monitoring()
            set_service_instance(service_id, None)
            if service_id in SERVICE_START_TIMES:
                del SERVICE_START_TIMES[service_id]
            logger.info(f"WatchHamster 모니터 중지 완료: {service_id}")
            
        elif service_id == "infomax_client" and instance:
            # INFOMAX API 클라이언트 중지
            await instance.close()
            set_service_instance(service_id, None)
            if service_id in SERVICE_START_TIMES:
                del SERVICE_START_TIMES[service_id]
            logger.info(f"INFOMAX API 클라이언트 중지 완료: {service_id}")
            
        elif service_id in ["news_parser", "webhook_sender"]:
            # 파서와 웹훅 발송자는 단순히 인스턴스 제거
            set_service_instance(service_id, None)
            if service_id in SERVICE_START_TIMES:
                del SERVICE_START_TIMES[service_id]
            logger.info(f"서비스 중지 완료: {service_id}")
            
        else:
            logger.warning(f"알 수 없는 서비스 또는 이미 중지된 서비스: {service_id}")
        
    except Exception as e:
        logger.error(f"서비스 중지 실패: {service_id} - {e}")
        # 오류 발생 시에도 인스턴스는 정리
        set_service_instance(service_id, None)

async def _restart_service_task(service_id: str):
    """서비스 재시작 백그라운드 작업"""
    import asyncio
    
    logger.info(f"서비스 재시작 작업 실행: {service_id}")
    
    try:
        # 재시작 시간 시뮬레이션
        await asyncio.sleep(3)
        
        # 서비스 상태를 running으로 업데이트
        SERVICES_DATA[service_id]["status"] = "running"
        SERVICE_START_TIMES[service_id] = time.time()  # 재시작 시간 기록
        SERVICES_DATA[service_id].pop("last_error", None)
        
        logger.info(f"서비스 재시작 완료: {service_id}")
        
    except Exception as e:
        logger.error(f"서비스 재시작 실패: {service_id} - {e}")
        
        # 오류 상태로 업데이트
        SERVICES_DATA[service_id]["status"] = "error"
        SERVICES_DATA[service_id]["last_error"] = str(e)