"""
실시간 헬스체크 및 알림 시스템
서비스 상태를 주기적으로 모니터링하고 이상 상황 시 알림 전송
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .services import (
    get_current_services_data, 
    get_service_instance, 
    get_service_metrics,
    set_service_status
)

logger = logging.getLogger(__name__)
router = APIRouter()

# 헬스체크 결과 모델
class HealthCheckResult(BaseModel):
    service_id: str
    service_name: str
    status: str
    is_healthy: bool
    response_time_ms: Optional[float] = None
    last_check: str
    error_message: Optional[str] = None
    metrics: Optional[dict] = None

class HealthAlert(BaseModel):
    service_id: str
    service_name: str
    alert_type: str  # down, slow, recovered
    timestamp: str
    message: str
    severity: str  # critical, warning, info

# 글로벌 헬스체크 상태
_health_status = {}
_health_history = {}
_active_alerts = {}
_monitoring_active = False

# 설정
HEALTH_CHECK_INTERVAL = 30  # 30초마다 체크
SERVICE_TIMEOUT = 10  # 10초 타임아웃
SLOW_RESPONSE_THRESHOLD = 5000  # 5초 이상이면 느림으로 간주

async def perform_service_health_check(service_id: str) -> HealthCheckResult:
    """개별 서비스 헬스체크 수행"""
    start_time = datetime.now()
    
    try:
        services_data = get_current_services_data()
        service_info = services_data.get(service_id)
        
        if not service_info:
            return HealthCheckResult(
                service_id=service_id,
                service_name="Unknown",
                status="unknown",
                is_healthy=False,
                last_check=start_time.isoformat(),
                error_message="서비스 정보를 찾을 수 없습니다"
            )
        
        # 서비스별 헬스체크 로직
        is_healthy = True
        error_message = None
        
        if service_id == "api_server":
            # API 서버는 현재 실행 중이므로 항상 healthy
            is_healthy = True
            
        elif service_id == "watchhamster_monitor":
            # WatchHamster 모니터 상태 확인
            instance = get_service_instance(service_id)
            if instance and hasattr(instance, 'is_running'):
                is_healthy = instance.is_running
            else:
                is_healthy = service_info["status"] == "running"
                
        elif service_id == "infomax_client":
            # INFOMAX API 클라이언트 연결 확인
            instance = get_service_instance(service_id)
            if instance and hasattr(instance, 'health_check'):
                try:
                    # 실제 API 헬스체크 수행
                    is_healthy = await asyncio.wait_for(
                        instance.health_check(), 
                        timeout=SERVICE_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    is_healthy = False
                    error_message = "API 응답 시간 초과"
                except Exception as e:
                    is_healthy = False
                    error_message = f"API 연결 실패: {str(e)}"
            else:
                is_healthy = service_info["status"] == "running"
                
        elif service_id == "webhook_sender":
            # 웹훅 발송자는 데이터베이스 연결 확인
            try:
                from database import get_database_connection
                conn = get_database_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                conn.close()
                is_healthy = True
            except Exception as e:
                is_healthy = False
                error_message = f"데이터베이스 연결 실패: {str(e)}"
                
        elif service_id == "news_parser":
            # 뉴스 파서는 인스턴스 존재 여부로 판단
            instance = get_service_instance(service_id)
            is_healthy = instance is not None
            
        else:
            # 기본적으로 서비스 상태로 판단
            is_healthy = service_info["status"] == "running"
        
        # 응답 시간 계산
        end_time = datetime.now()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # 메트릭 조회
        try:
            metrics = get_service_metrics(service_id)
        except Exception as e:
            logger.warning(f"메트릭 조회 실패 ({service_id}): {e}")
            metrics = None
        
        # 서비스 상태가 변경된 경우 업데이트
        current_status = "running" if is_healthy else "error"
        if service_info["status"] != current_status:
            set_service_status(service_id, current_status, error_message)
        
        return HealthCheckResult(
            service_id=service_id,
            service_name=service_info["name"],
            status=current_status,
            is_healthy=is_healthy,
            response_time_ms=response_time_ms,
            last_check=end_time.isoformat(),
            error_message=error_message,
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"헬스체크 실행 실패 ({service_id}): {e}")
        return HealthCheckResult(
            service_id=service_id,
            service_name=service_info.get("name", "Unknown") if 'service_info' in locals() else "Unknown",
            status="error",
            is_healthy=False,
            last_check=datetime.now().isoformat(),
            error_message=f"헬스체크 실행 오류: {str(e)}"
        )

async def check_and_alert(service_id: str, health_result: HealthCheckResult):
    """헬스체크 결과를 분석하여 필요시 알림 발송"""
    previous_status = _health_status.get(service_id, {}).get("is_healthy")
    current_status = health_result.is_healthy
    
    # 상태 변경 감지
    alert = None
    
    if previous_status is True and current_status is False:
        # 서비스 다운
        alert = HealthAlert(
            service_id=service_id,
            service_name=health_result.service_name,
            alert_type="down",
            timestamp=datetime.now().isoformat(),
            message=f"서비스가 응답하지 않습니다: {health_result.error_message or '상태 불명'}",
            severity="critical"
        )
        
    elif previous_status is False and current_status is True:
        # 서비스 복구
        alert = HealthAlert(
            service_id=service_id,
            service_name=health_result.service_name,
            alert_type="recovered",
            timestamp=datetime.now().isoformat(),
            message="서비스가 정상 복구되었습니다",
            severity="info"
        )
        
    elif current_status and health_result.response_time_ms and health_result.response_time_ms > SLOW_RESPONSE_THRESHOLD:
        # 응답 속도 저하
        alert = HealthAlert(
            service_id=service_id,
            service_name=health_result.service_name,
            alert_type="slow",
            timestamp=datetime.now().isoformat(),
            message=f"서비스 응답 속도가 저하되었습니다 ({health_result.response_time_ms:.0f}ms)",
            severity="warning"
        )
    
    if alert:
        _active_alerts[f"{service_id}_{alert.alert_type}"] = alert
        logger.warning(f"헬스체크 알림: {alert.service_name} - {alert.message}")
        
        # TODO: 실제 알림 시스템 연동 (Dooray 웹훅, 이메일 등)
        await send_health_alert(alert)

async def send_health_alert(alert: HealthAlert):
    """실제 알림 전송 (Dooray 웹훅 사용)"""
    try:
        # 웹훅 발송자를 통해 알림 전송
        webhook_sender = get_service_instance("webhook_sender")
        if webhook_sender and hasattr(webhook_sender, 'send_system_alert'):
            await webhook_sender.send_system_alert(
                title=f"🚨 서비스 알림: {alert.service_name}",
                message=alert.message,
                severity=alert.severity
            )
    except Exception as e:
        logger.error(f"헬스체크 알림 전송 실패: {e}")

async def health_monitor_loop():
    """헬스체크 모니터링 메인 루프"""
    global _monitoring_active
    logger.info("헬스체크 모니터링 시작")
    
    while _monitoring_active:
        try:
            services_data = get_current_services_data()
            
            for service_id in services_data.keys():
                try:
                    # 헬스체크 수행
                    health_result = await perform_service_health_check(service_id)
                    
                    # 결과 저장
                    _health_status[service_id] = health_result.dict()
                    
                    # 이력 저장 (최근 24시간)
                    if service_id not in _health_history:
                        _health_history[service_id] = []
                    
                    _health_history[service_id].append({
                        "timestamp": health_result.last_check,
                        "is_healthy": health_result.is_healthy,
                        "response_time_ms": health_result.response_time_ms
                    })
                    
                    # 24시간 이전 데이터 정리
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    _health_history[service_id] = [
                        h for h in _health_history[service_id]
                        if datetime.fromisoformat(h["timestamp"].replace('Z', '+00:00').replace('+00:00', '')) > cutoff_time
                    ]
                    
                    # 알림 확인 및 전송
                    await check_and_alert(service_id, health_result)
                    
                except Exception as e:
                    logger.error(f"서비스 헬스체크 오류 ({service_id}): {e}")
                
                # 서비스 간 간격
                await asyncio.sleep(1)
            
            # 다음 사이클까지 대기
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"헬스체크 모니터링 루프 오류: {e}")
            await asyncio.sleep(5)  # 오류 발생 시 짧은 대기
    
    logger.info("헬스체크 모니터링 종료")

# API 엔드포인트들
@router.get("/health", response_model=List[HealthCheckResult])
async def get_all_health_status():
    """모든 서비스 헬스체크 상태 조회"""
    try:
        results = []
        for service_id, health_data in _health_status.items():
            results.append(HealthCheckResult(**health_data))
        
        return results
        
    except Exception as e:
        logger.error(f"헬스체크 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="헬스체크 상태 조회 중 오류가 발생했습니다")

@router.get("/health/{service_id}", response_model=HealthCheckResult)
async def get_service_health_status(service_id: str):
    """특정 서비스 헬스체크 상태 조회"""
    try:
        if service_id not in _health_status:
            # 즉시 헬스체크 수행
            health_result = await perform_service_health_check(service_id)
            _health_status[service_id] = health_result.dict()
            return health_result
        
        health_data = _health_status[service_id]
        return HealthCheckResult(**health_data)
        
    except Exception as e:
        logger.error(f"서비스 헬스체크 조회 실패 ({service_id}): {e}")
        raise HTTPException(status_code=500, detail="헬스체크 조회 중 오류가 발생했습니다")

@router.get("/alerts", response_model=List[HealthAlert])
async def get_active_alerts():
    """활성 알림 목록 조회"""
    try:
        return list(_active_alerts.values())
    except Exception as e:
        logger.error(f"활성 알림 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="알림 조회 중 오류가 발생했습니다")

@router.post("/monitoring/start")
async def start_health_monitoring(background_tasks: BackgroundTasks):
    """헬스체크 모니터링 시작"""
    global _monitoring_active
    
    if _monitoring_active:
        return {"message": "헬스체크 모니터링이 이미 실행 중입니다", "status": "running"}
    
    _monitoring_active = True
    background_tasks.add_task(health_monitor_loop)
    
    return {"message": "헬스체크 모니터링을 시작했습니다", "status": "started"}

@router.post("/monitoring/stop")
async def stop_health_monitoring():
    """헬스체크 모니터링 중지"""
    global _monitoring_active
    
    if not _monitoring_active:
        return {"message": "헬스체크 모니터링이 실행되지 않고 있습니다", "status": "stopped"}
    
    _monitoring_active = False
    
    return {"message": "헬스체크 모니터링을 중지했습니다", "status": "stopped"}

@router.get("/monitoring/status")
async def get_monitoring_status():
    """헬스체크 모니터링 상태 조회"""
    return {
        "monitoring_active": _monitoring_active,
        "check_interval_seconds": HEALTH_CHECK_INTERVAL,
        "service_timeout_seconds": SERVICE_TIMEOUT,
        "monitored_services": len(_health_status),
        "active_alerts": len(_active_alerts),
        "last_check": max([h.get("last_check", "") for h in _health_status.values()], default="")
    }
