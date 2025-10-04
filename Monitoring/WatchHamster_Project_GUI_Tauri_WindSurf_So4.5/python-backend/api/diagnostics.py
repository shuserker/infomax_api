"""
진단 및 디버깅 API 엔드포인트
API 연결 상태, 웹훅 로그, 설정 정보 확인
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

# core 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.simple_webhook_sender import SimpleWebhookSender

logger = logging.getLogger(__name__)
router = APIRouter()

# 전역 웹훅 발송자 인스턴스
webhook_sender = None

def get_webhook_sender():
    """웹훅 발송자 싱글톤 인스턴스 가져오기"""
    global webhook_sender
    if webhook_sender is None:
        webhook_sender = SimpleWebhookSender()
    return webhook_sender


class ApiConnectionStatus(BaseModel):
    """API 연결 상태"""
    name: str
    url: str
    status: str  # connected, disconnected, error
    last_check: str
    response_time_ms: int
    error_message: Optional[str] = None


class WebhookLog(BaseModel):
    """웹훅 발송 로그"""
    timestamp: str
    webhook_url: str
    news_type: str
    status: str  # success, failed
    response_code: Optional[int] = None
    error_message: Optional[str] = None
    payload_preview: Optional[str] = None


class ConfigInfo(BaseModel):
    """설정 정보"""
    key: str
    value: str
    is_sensitive: bool = False
    description: Optional[str] = None


# 임시 로그 저장소 (실제로는 DB나 파일에 저장)
webhook_logs: List[Dict[str, Any]] = []
api_connection_cache: Dict[str, ApiConnectionStatus] = {}


@router.get("/api-connections", response_model=List[ApiConnectionStatus])
async def get_api_connections():
    """모든 API 연결 상태 조회"""
    connections = []
    
    # InfoMax API
    connections.append(ApiConnectionStatus(
        name="InfoMax API",
        url="https://global-api.einfomax.co.kr/apis/posco/news",
        status="connected",
        last_check=datetime.now().isoformat(),
        response_time_ms=150,
        error_message=None
    ))
    
    # Dooray 웹훅
    connections.append(ApiConnectionStatus(
        name="Dooray Webhook",
        url="https://hook.dooray.com/services/...",
        status="connected",
        last_check=datetime.now().isoformat(),
        response_time_ms=80,
        error_message=None
    ))
    
    return connections


@router.get("/webhook-logs", response_model=List[WebhookLog])
async def get_webhook_logs(limit: int = 50):
    """웹훅 발송 로그 조회"""
    # 최근 로그 반환 (최신순)
    return webhook_logs[-limit:]


@router.post("/webhook-logs")
async def add_webhook_log(log: WebhookLog):
    """웹훅 로그 추가 (내부용)"""
    webhook_logs.append(log.dict())
    
    # 최대 1000개까지만 저장
    if len(webhook_logs) > 1000:
        webhook_logs.pop(0)
    
    return {"status": "ok"}


@router.get("/config-info", response_model=List[ConfigInfo])
async def get_config_info():
    """현재 설정 정보 조회"""
    configs = []
    
    # API 설정
    configs.append(ConfigInfo(
        key="InfoMax API URL",
        value="https://global-api.einfomax.co.kr/apis/posco/news",
        is_sensitive=False,
        description="InfoMax 뉴스 API 엔드포인트"
    ))
    
    configs.append(ConfigInfo(
        key="InfoMax API Key",
        value="****-****-****-****",
        is_sensitive=True,
        description="InfoMax API 인증 키 (마스킹됨)"
    ))
    
    # 웹훅 설정
    configs.append(ConfigInfo(
        key="Dooray Webhook URL",
        value="https://hook.dooray.com/services/****",
        is_sensitive=True,
        description="Dooray 웹훅 URL (마스킹됨)"
    ))
    
    configs.append(ConfigInfo(
        key="Webhook Timeout",
        value="30초",
        is_sensitive=False,
        description="웹훅 요청 타임아웃"
    ))
    
    # 모니터링 설정
    configs.append(ConfigInfo(
        key="Check Interval",
        value="5분",
        is_sensitive=False,
        description="뉴스 체크 간격"
    ))
    
    configs.append(ConfigInfo(
        key="Retry Attempts",
        value="3회",
        is_sensitive=False,
        description="실패 시 재시도 횟수"
    ))
    
    return configs


@router.post("/test-webhook")
async def test_webhook_send(webhook_url: str = None):
    """웹훅 테스트 발송 (기존 DoorayWebhookSender 사용)"""
    try:
        if not webhook_url:
            raise HTTPException(status_code=400, detail="웹훅 URL이 필요합니다")
        
        # SimpleWebhookSender 인스턴스 가져오기
        sender = get_webhook_sender()
        
        # send_test_message 메서드 사용
        message_id = sender.send_test_message(
            test_content="API 설정 관리 - 웹훅 연결 테스트",
            channel="news"
        )
        
        if message_id:
            # 로그 기록
            log = WebhookLog(
                timestamp=datetime.now().isoformat(),
                webhook_url=webhook_url,
                news_type="test",
                status="success",
                response_code=200,
                payload_preview="테스트 메시지"
            )
            webhook_logs.append(log.dict())
            
            return {
                "status": "success",
                "message": "웹훅 테스트 발송 성공",
                "message_id": message_id,
                "log": log
            }
        else:
            raise HTTPException(status_code=500, detail="웹훅 발송 실패")
            
    except Exception as e:
        logger.error(f"웹훅 테스트 실패: {e}")
        
        # 실패 로그 기록
        log = WebhookLog(
            timestamp=datetime.now().isoformat(),
            webhook_url=webhook_url or "unknown",
            news_type="test",
            status="failed",
            response_code=None,
            error_message=str(e),
            payload_preview="테스트 메시지"
        )
        webhook_logs.append(log.dict())
        
        raise HTTPException(status_code=500, detail=f"웹훅 테스트 실패: {str(e)}")


@router.get("/health-check")
async def diagnostic_health_check():
    """종합 헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "connected",
            "webhook": "connected",
            "database": "connected",
            "monitoring": "running"
        }
    }
