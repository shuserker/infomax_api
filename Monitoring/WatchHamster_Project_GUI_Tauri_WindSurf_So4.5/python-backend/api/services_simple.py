"""
서비스 관리 API (간단 버전)
aiohttp 의존성 없이 작동
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class Service(BaseModel):
    id: str
    name: str
    display_name: str
    status: str
    description: str
    port: int = None
    url: str = None
    last_check: str = None


# 서비스 데이터 (메모리 기반)
SERVICES_DATA = {
    "posco_news": {
        "id": "posco_news",
        "name": "posco_news",
        "display_name": "POSCO 뉴스 모니터링",
        "status": "running",
        "description": "POSCO 뉴스 실시간 모니터링 서비스",
        "port": 8000,
        "url": "http://localhost:8000",
        "last_check": datetime.now().isoformat()
    },
    "webhook_sender": {
        "id": "webhook_sender",
        "name": "webhook_sender",
        "display_name": "웹훅 발송 서비스",
        "status": "running",
        "description": "Dooray 웹훅 메시지 발송",
        "port": None,
        "url": None,
        "last_check": datetime.now().isoformat()
    },
    "api_monitor": {
        "id": "api_monitor",
        "name": "api_monitor",
        "display_name": "API 모니터링",
        "status": "running",
        "description": "InfoMax API 상태 모니터링",
        "port": None,
        "url": None,
        "last_check": datetime.now().isoformat()
    }
}


@router.get("/")
async def get_services() -> List[Dict[str, Any]]:
    """서비스 목록 조회"""
    try:
        services = list(SERVICES_DATA.values())
        return services
    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}")
async def get_service(service_id: str) -> Dict[str, Any]:
    """서비스 상세 조회"""
    try:
        if service_id not in SERVICES_DATA:
            raise HTTPException(status_code=404, detail="서비스를 찾을 수 없습니다")
        
        return SERVICES_DATA[service_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{service_id}/start")
async def start_service(service_id: str):
    """서비스 시작"""
    try:
        if service_id not in SERVICES_DATA:
            raise HTTPException(status_code=404, detail="서비스를 찾을 수 없습니다")
        
        SERVICES_DATA[service_id]["status"] = "running"
        SERVICES_DATA[service_id]["last_check"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": f"{SERVICES_DATA[service_id]['display_name']} 시작됨"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{service_id}/stop")
async def stop_service(service_id: str):
    """서비스 중지"""
    try:
        if service_id not in SERVICES_DATA:
            raise HTTPException(status_code=404, detail="서비스를 찾을 수 없습니다")
        
        SERVICES_DATA[service_id]["status"] = "stopped"
        SERVICES_DATA[service_id]["last_check"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": f"{SERVICES_DATA[service_id]['display_name']} 중지됨"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 중지 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{service_id}/restart")
async def restart_service(service_id: str):
    """서비스 재시작"""
    try:
        if service_id not in SERVICES_DATA:
            raise HTTPException(status_code=404, detail="서비스를 찾을 수 없습니다")
        
        SERVICES_DATA[service_id]["status"] = "restarting"
        SERVICES_DATA[service_id]["last_check"] = datetime.now().isoformat()
        
        # 잠시 후 running으로 변경 (실제로는 비동기 처리)
        import asyncio
        async def set_running():
            await asyncio.sleep(2)
            SERVICES_DATA[service_id]["status"] = "running"
        
        asyncio.create_task(set_running())
        
        return {
            "status": "success",
            "message": f"{SERVICES_DATA[service_id]['display_name']} 재시작 중"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 재시작 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}/logs")
async def get_service_logs(service_id: str, limit: int = 100):
    """서비스 로그 조회"""
    try:
        if service_id not in SERVICES_DATA:
            raise HTTPException(status_code=404, detail="서비스를 찾을 수 없습니다")
        
        # 데모 로그
        return {
            "service_id": service_id,
            "logs": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"{SERVICES_DATA[service_id]['display_name']} 정상 작동 중"
                }
            ],
            "total": 1
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}/status")
async def get_service_status(service_id: str):
    """서비스 상태 조회"""
    try:
        if service_id not in SERVICES_DATA:
            raise HTTPException(status_code=404, detail="서비스를 찾을 수 없습니다")
        
        return {
            "status": SERVICES_DATA[service_id]["status"],
            "last_check": SERVICES_DATA[service_id]["last_check"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
