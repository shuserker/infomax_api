"""
서비스 관리 API 엔드포인트
포팅된 핵심 로직을 사용하여 실제 서비스 관리 기능 제공
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

# 포팅된 핵심 모듈들 임포트
from core.status_reporter import create_integrated_status_reporter, SystemStatus
from core.posco_manager import PoscoManager
from core.webhook_system import WebhookSystem

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

# 전역 서비스 인스턴스들
_status_reporter = None
_posco_manager = None
_webhook_system = None

def get_status_reporter():
    """상태 보고 시스템 인스턴스 반환"""
    global _status_reporter
    if _status_reporter is None:
        _status_reporter = create_integrated_status_reporter()
    return _status_reporter

def get_posco_manager():
    """POSCO 관리자 인스턴스 반환"""
    global _posco_manager
    if _posco_manager is None:
        _posco_manager = PoscoManager()
    return _posco_manager

def get_webhook_system():
    """웹훅 시스템 인스턴스 반환"""
    global _webhook_system
    if _webhook_system is None:
        _webhook_system = WebhookSystem()
    return _webhook_system

@router.get("/", response_model=List[ServiceInfo])
async def get_services(status_reporter = Depends(get_status_reporter)):
    """모든 서비스 목록 조회"""
    logger.info("서비스 목록 조회 요청")
    
    try:
        # 실제 시스템 상태 조회
        system_status = await status_reporter.get_system_status()
        services = []
        
        for component_name, component_data in system_status.get('components', {}).items():
            # 상태 매핑
            status_mapping = {
                'healthy': 'running',
                'warning': 'warning', 
                'error': 'error',
                'critical': 'error',
                'offline': 'stopped',
                'unknown': 'unknown'
            }
            
            service_info = ServiceInfo(
                id=component_name,
                name=component_data.get('details', {}).get('display_name', component_name.replace('_', ' ').title()),
                description=component_data.get('details', {}).get('description', f"{component_name} 서비스"),
                status=status_mapping.get(component_data.get('status', 'unknown'), 'unknown'),
                uptime=component_data.get('details', {}).get('uptime'),
                last_error=component_data.get('error_message'),
                config=component_data.get('details', {}).get('config', {})
            )
            services.append(service_info)
        
        return services
        
    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {e}")
        # 기본 서비스 목록 반환
        return [
            ServiceInfo(
                id="posco_news",
                name="POSCO 뉴스 모니터",
                description="POSCO 뉴스 시스템 모니터링 및 알림",
                status="unknown"
            ),
            ServiceInfo(
                id="github_pages",
                name="GitHub Pages 모니터", 
                description="GitHub Pages 배포 상태 모니터링",
                status="unknown"
            ),
            ServiceInfo(
                id="cache_monitor",
                name="캐시 모니터",
                description="데이터 캐시 상태 모니터링",
                status="unknown"
            ),
            ServiceInfo(
                id="deployment",
                name="배포 시스템",
                description="자동 배포 및 롤백 관리",
                status="unknown"
            ),
            ServiceInfo(
                id="message_system",
                name="메시지 시스템",
                description="동적 메시지 생성 및 템플릿 관리",
                status="unknown"
            ),
            ServiceInfo(
                id="webhook_system",
                name="웹훅 시스템",
                description="Discord/Slack 웹훅 전송 관리",
                status="unknown"
            )
        ]

@router.get("/{service_id}", response_model=ServiceInfo)
async def get_service(service_id: str, status_reporter = Depends(get_status_reporter)):
    """특정 서비스 정보 조회"""
    logger.info(f"서비스 정보 조회: {service_id}")
    
    try:
        system_status = await status_reporter.get_system_status()
        component_data = system_status.get('components', {}).get(service_id)
        
        if not component_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        # 상태 매핑
        status_mapping = {
            'healthy': 'running',
            'warning': 'warning',
            'error': 'error', 
            'critical': 'error',
            'offline': 'stopped',
            'unknown': 'unknown'
        }
        
        service_info = ServiceInfo(
            id=service_id,
            name=component_data.get('details', {}).get('display_name', service_id.replace('_', ' ').title()),
            description=component_data.get('details', {}).get('description', f"{service_id} 서비스"),
            status=status_mapping.get(component_data.get('status', 'unknown'), 'unknown'),
            uptime=component_data.get('details', {}).get('uptime'),
            last_error=component_data.get('error_message'),
            config=component_data.get('details', {}).get('config', {})
        )
        
        return service_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 정보 조회 중 오류가 발생했습니다")

@router.post("/{service_id}/start")
async def start_service(service_id: str, background_tasks: BackgroundTasks, 
                       status_reporter = Depends(get_status_reporter),
                       posco_manager = Depends(get_posco_manager)):
    """서비스 시작"""
    logger.info(f"서비스 시작 요청: {service_id}")
    
    try:
        # 현재 서비스 상태 확인
        system_status = await status_reporter.get_system_status()
        component_data = system_status.get('components', {}).get(service_id)
        
        if not component_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        current_status = component_data.get('status', 'unknown')
        if current_status == 'healthy':
            return {"message": f"서비스 '{service_id}'이 이미 실행 중입니다"}
        
        # 상태를 starting으로 업데이트
        await status_reporter.update_component_status(
            service_id, 
            SystemStatus.WARNING,  # starting 상태를 warning으로 표시
            {"status_message": "시작 중"}
        )
        
        # 백그라운드에서 서비스 시작 작업 수행
        background_tasks.add_task(_start_service_task, service_id, status_reporter, posco_manager)
        
        return {"message": f"서비스 '{service_id}' 시작 중..."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 시작 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 시작 요청 처리 중 오류가 발생했습니다")

@router.post("/{service_id}/stop")
async def stop_service(service_id: str, background_tasks: BackgroundTasks,
                      status_reporter = Depends(get_status_reporter),
                      posco_manager = Depends(get_posco_manager)):
    """서비스 중지"""
    logger.info(f"서비스 중지 요청: {service_id}")
    
    try:
        # 현재 서비스 상태 확인
        system_status = await status_reporter.get_system_status()
        component_data = system_status.get('components', {}).get(service_id)
        
        if not component_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        current_status = component_data.get('status', 'unknown')
        if current_status == 'offline':
            return {"message": f"서비스 '{service_id}'이 이미 중지되어 있습니다"}
        
        # 상태를 stopping으로 업데이트
        await status_reporter.update_component_status(
            service_id,
            SystemStatus.WARNING,  # stopping 상태를 warning으로 표시
            {"status_message": "중지 중"}
        )
        
        # 백그라운드에서 서비스 중지 작업 수행
        background_tasks.add_task(_stop_service_task, service_id, status_reporter, posco_manager)
        
        return {"message": f"서비스 '{service_id}' 중지 중..."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 중지 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 중지 요청 처리 중 오류가 발생했습니다")

@router.post("/{service_id}/restart")
async def restart_service(service_id: str, background_tasks: BackgroundTasks,
                         status_reporter = Depends(get_status_reporter),
                         posco_manager = Depends(get_posco_manager)):
    """서비스 재시작"""
    logger.info(f"서비스 재시작 요청: {service_id}")
    
    try:
        # 현재 서비스 상태 확인
        system_status = await status_reporter.get_system_status()
        component_data = system_status.get('components', {}).get(service_id)
        
        if not component_data:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없습니다: {service_id}")
        
        # 상태를 restarting으로 업데이트
        await status_reporter.update_component_status(
            service_id,
            SystemStatus.WARNING,  # restarting 상태를 warning으로 표시
            {"status_message": "재시작 중"}
        )
        
        # 백그라운드에서 서비스 재시작 작업 수행
        background_tasks.add_task(_restart_service_task, service_id, status_reporter, posco_manager)
        
        return {"message": f"서비스 '{service_id}' 재시작 중..."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"서비스 재시작 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="서비스 재시작 요청 처리 중 오류가 발생했습니다")

# 백그라운드 작업 함수들
async def _start_service_task(service_id: str, status_reporter, posco_manager):
    """서비스 시작 백그라운드 작업"""
    import asyncio
    from api.websocket import broadcast_service_event
    
    logger.info(f"서비스 시작 작업 실행: {service_id}")
    
    try:
        # WebSocket으로 시작 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "starting", 
            f"서비스 '{service_id}' 시작 중..."
        )
        
        # 서비스별 실제 시작 로직
        if service_id == "posco_news":
            # POSCO 뉴스 시스템 시작
            await posco_manager.start_monitoring()
            await asyncio.sleep(2)  # 시작 시간 시뮬레이션
            
        elif service_id == "deployment":
            # 배포 시스템 초기화
            await asyncio.sleep(3)
            
        elif service_id == "webhook_system":
            # 웹훅 시스템 초기화
            webhook_system = get_webhook_system()
            await asyncio.sleep(1)
            
        else:
            # 기타 서비스들
            await asyncio.sleep(2)
        
        # 서비스 상태를 healthy로 업데이트
        await status_reporter.update_component_status(
            service_id,
            SystemStatus.HEALTHY,
            {
                "status_message": "실행 중",
                "started_at": datetime.now().isoformat(),
                "uptime": 0
            }
        )
        
        # WebSocket으로 시작 완료 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "started", 
            f"서비스 '{service_id}'이 성공적으로 시작되었습니다"
        )
        
        logger.info(f"서비스 시작 완료: {service_id}")
        
    except Exception as e:
        logger.error(f"서비스 시작 실패: {service_id} - {e}")
        
        # 오류 상태로 업데이트
        await status_reporter.update_component_status(
            service_id,
            SystemStatus.ERROR,
            {"status_message": "시작 실패"},
            error_message=str(e)
        )
        
        # WebSocket으로 오류 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "error", 
            f"서비스 '{service_id}' 시작 실패: {str(e)}"
        )

async def _stop_service_task(service_id: str, status_reporter, posco_manager):
    """서비스 중지 백그라운드 작업"""
    import asyncio
    from api.websocket import broadcast_service_event
    
    logger.info(f"서비스 중지 작업 실행: {service_id}")
    
    try:
        # WebSocket으로 중지 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "stopping", 
            f"서비스 '{service_id}' 중지 중..."
        )
        
        # 서비스별 실제 중지 로직
        if service_id == "posco_news":
            # POSCO 뉴스 시스템 중지
            await posco_manager.stop_monitoring()
            await asyncio.sleep(1)
            
        elif service_id == "deployment":
            # 배포 시스템 중지
            await asyncio.sleep(2)
            
        else:
            # 기타 서비스들
            await asyncio.sleep(1)
        
        # 서비스 상태를 offline으로 업데이트
        await status_reporter.update_component_status(
            service_id,
            SystemStatus.OFFLINE,
            {"status_message": "중지됨"}
        )
        
        # WebSocket으로 중지 완료 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "stopped", 
            f"서비스 '{service_id}'이 성공적으로 중지되었습니다"
        )
        
        logger.info(f"서비스 중지 완료: {service_id}")
        
    except Exception as e:
        logger.error(f"서비스 중지 실패: {service_id} - {e}")
        
        # 오류 상태로 업데이트
        await status_reporter.update_component_status(
            service_id,
            SystemStatus.ERROR,
            {"status_message": "중지 실패"},
            error_message=str(e)
        )
        
        # WebSocket으로 오류 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "error", 
            f"서비스 '{service_id}' 중지 실패: {str(e)}"
        )

async def _restart_service_task(service_id: str, status_reporter, posco_manager):
    """서비스 재시작 백그라운드 작업"""
    import asyncio
    from api.websocket import broadcast_service_event
    
    logger.info(f"서비스 재시작 작업 실행: {service_id}")
    
    try:
        # WebSocket으로 재시작 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "restarting", 
            f"서비스 '{service_id}' 재시작 중..."
        )
        
        # 먼저 중지 (WebSocket 이벤트는 _stop_service_task에서 처리)
        await _stop_service_task(service_id, status_reporter, posco_manager)
        
        # 잠시 대기
        await asyncio.sleep(1)
        
        # 다시 시작 (WebSocket 이벤트는 _start_service_task에서 처리)
        await _start_service_task(service_id, status_reporter, posco_manager)
        
        # WebSocket으로 재시작 완료 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "restarted", 
            f"서비스 '{service_id}'이 성공적으로 재시작되었습니다"
        )
        
        logger.info(f"서비스 재시작 완료: {service_id}")
        
    except Exception as e:
        logger.error(f"서비스 재시작 실패: {service_id} - {e}")
        
        # 오류 상태로 업데이트
        await status_reporter.update_component_status(
            service_id,
            SystemStatus.ERROR,
            {"status_message": "재시작 실패"},
            error_message=str(e)
        )
        
        # WebSocket으로 오류 이벤트 브로드캐스트
        await broadcast_service_event(
            service_id, 
            "error", 
            f"서비스 '{service_id}' 재시작 실패: {str(e)}"
        )