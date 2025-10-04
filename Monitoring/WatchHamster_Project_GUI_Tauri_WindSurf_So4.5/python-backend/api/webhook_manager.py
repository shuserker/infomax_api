"""
웹훅 관리 API
모든 웹훅 발송 로직 관리 및 로그 확인
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# core 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "posco_original"))
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "watchhamster_original"))

from webhook_sender import WebhookSender, MessagePriority, BotType
from news_message_generator import NewsMessageGenerator
from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

# 전역 인스턴스 (POSCO 기본값 - 하위 호환성)
webhook_sender = None
message_generator = None

def get_webhook_sender():
    """웹훅 발송자 싱글톤"""
    global webhook_sender
    if webhook_sender is None:
        webhook_sender = WebhookSender(test_mode=False)
    return webhook_sender

def get_message_generator():
    """메시지 생성기 싱글톤"""
    global message_generator
    if message_generator is None:
        message_generator = NewsMessageGenerator(test_mode=False)
    return message_generator


def save_webhook_log(
    company_id: str,
    message_type: str,
    bot_type: str,
    priority: str,
    endpoint: str,
    status: str,
    message_id: str,
    full_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None
) -> str:
    """웹훅 로그를 데이터베이스에 저장"""
    try:
        db = get_db()
        log_data = {
            'id': message_id,
            'company_id': company_id,
            'message_type': message_type,
            'bot_type': bot_type,
            'priority': priority,
            'endpoint': endpoint,
            'status': status,
            'message_id': message_id,
            'full_message': full_message,
            'metadata': metadata,
            'error_message': error_message
        }
        return db.create_webhook_log(log_data)
    except Exception as e:
        logger.error(f"로그 저장 실패: {e}")
        return message_id


# ============= Pydantic Models =============

class WebhookLog(BaseModel):
    """웹훅 로그"""
    id: str
    timestamp: str
    message_type: str
    bot_type: str
    priority: str
    endpoint: str
    status: str  # success, failed, pending
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    full_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WebhookSendRequest(BaseModel):
    """웹훅 발송 요청"""
    message_type: str  # comparison, delay, report, status, no_data, error, watchhamster_status, test
    priority: str = "NORMAL"  # CRITICAL, HIGH, NORMAL, LOW
    data: Dict[str, Any]


class WebhookStats(BaseModel):
    """웹훅 통계"""
    total_sent: int
    successful_sends: int
    failed_sends: int
    retry_attempts: int
    average_response_time: float
    last_send_time: Optional[str]


# ============= API Endpoints =============

@router.get("/stats")
async def get_webhook_stats(company_id: Optional[str] = None):
    """웹훅 발송 통계 - 회사별 필터링 지원"""
    try:
        db = get_db()
        stats = db.get_webhook_stats(company_id=company_id or 'posco')
        
        return WebhookStats(
            total_sent=stats.get('total_sent', 0),
            successful_sends=stats.get('successful_sends', 0),
            failed_sends=stats.get('failed_sends', 0),
            retry_attempts=stats.get('retry_attempts', 0),
            average_response_time=stats.get('average_response_time', 0.0),
            last_send_time=stats.get('last_send_time')
        )
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue-status")
async def get_queue_status():
    """큐 상태 조회"""
    try:
        sender = get_webhook_sender()
        status = sender.get_queue_status()
        return status
    except Exception as e:
        logger.error(f"큐 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_webhook_logs(
    limit: int = 100, 
    message_type: Optional[str] = None,
    company_id: Optional[str] = None
):
    """웹훅 로그 조회 (풀텍스트) - 회사별 필터링 지원"""
    try:
        db = get_db()
        logs = db.get_webhook_logs(
            company_id=company_id or 'posco',  # 기본값: POSCO (하위 호환성)
            limit=limit,
            message_type=message_type
        )
        
        return {
            "total": len(logs),
            "filtered": len(logs),
            "logs": logs
        }
    except Exception as e:
        logger.error(f"로그 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/{log_id}")
async def get_webhook_log_detail(log_id: str):
    """특정 로그 상세 조회"""
    try:
        log = next((l for l in webhook_logs if l.get('id') == log_id), None)
        if not log:
            raise HTTPException(status_code=404, detail="로그를 찾을 수 없습니다")
        return log
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그 상세 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/test")
async def send_test_message(
    test_content: str = "테스트 메시지",
    company_id: str = "posco"
):
    """테스트 메시지 발송 - 회사별 지원"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_test_message(
            test_content=test_content,
            priority=MessagePriority.LOW
        )
        
        full_message = f"🧪 [TEST] POSCO 시스템 테스트\n\n📋 테스트 내용: {test_content}"
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="test",
            bot_type="TEST",
            priority="LOW",
            endpoint="NEWS_MAIN",
            status="success" if message_id else "failed",
            message_id=message_id,
            full_message=full_message,
            metadata={"test_content": test_content}
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "test",
                "bot_type": "TEST",
                "priority": "LOW",
                "endpoint": "NEWS_MAIN",
                "status": "success",
                "message_id": message_id
            }
        }
    except Exception as e:
        logger.error(f"테스트 메시지 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/business-day-comparison")
async def send_business_day_comparison(data: Dict[str, Any]):
    """영업일 비교 분석 메시지 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_business_day_comparison(
            raw_data=data.get('raw_data', {}),
            historical_data=data.get('historical_data'),
            priority=MessagePriority[data.get('priority', 'NORMAL')]
        )
        
        log = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": "business_day_comparison",
            "bot_type": "NEWS_COMPARISON",
            "priority": data.get('priority', 'NORMAL'),
            "endpoint": "NEWS_MAIN",
            "status": "success" if message_id else "failed",
            "message_id": message_id,
            "metadata": {"data_keys": list(data.keys())}
        }
        webhook_logs.append(log)
        
        return {"status": "success", "message_id": message_id, "log": log}
    except Exception as e:
        logger.error(f"영업일 비교 메시지 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/delay-notification")
async def send_delay_notification(news_type: str, delay_minutes: int, data: Dict[str, Any]):
    """지연 발행 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_delay_notification(
            news_type=news_type,
            current_data=data.get('current_data', {}),
            delay_minutes=delay_minutes,
            priority=MessagePriority.HIGH
        )
        
        log = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": "delay_notification",
            "bot_type": "NEWS_DELAY",
            "priority": "HIGH",
            "endpoint": "NEWS_MAIN",
            "status": "success" if message_id else "failed",
            "message_id": message_id,
            "metadata": {"news_type": news_type, "delay_minutes": delay_minutes}
        }
        webhook_logs.append(log)
        
        return {"status": "success", "message_id": message_id, "log": log}
    except Exception as e:
        logger.error(f"지연 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/daily-report")
async def send_daily_integrated_report(data: Dict[str, Any]):
    """일일 통합 리포트 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_daily_integrated_report(
            raw_data=data.get('raw_data', {}),
            report_url=data.get('report_url'),
            priority=MessagePriority.NORMAL
        )
        
        log = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": "daily_report",
            "bot_type": "NEWS_REPORT",
            "priority": "NORMAL",
            "endpoint": "NEWS_MAIN",
            "status": "success" if message_id else "failed",
            "message_id": message_id
        }
        webhook_logs.append(log)
        
        return {"status": "success", "message_id": message_id, "log": log}
    except Exception as e:
        logger.error(f"일일 리포트 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/status-notification")
async def send_status_notification(data: Dict[str, Any]):
    """정시 발행 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_status_notification(
            raw_data=data.get('raw_data', {}),
            priority=MessagePriority.NORMAL
        )
        
        log = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": "status_notification",
            "bot_type": "NEWS_STATUS",
            "priority": "NORMAL",
            "endpoint": "NEWS_MAIN",
            "status": "success" if message_id else "failed",
            "message_id": message_id
        }
        webhook_logs.append(log)
        
        return {"status": "success", "message_id": message_id, "log": log}
    except Exception as e:
        logger.error(f"정시 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/no-data-notification")
async def send_no_data_notification(data: Dict[str, Any]):
    """데이터 갱신 없음 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_no_data_notification(
            raw_data=data.get('raw_data', {}),
            priority=MessagePriority.LOW
        )
        
        log = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": "no_data_notification",
            "bot_type": "NEWS_NO_DATA",
            "priority": "LOW",
            "endpoint": "NEWS_MAIN",
            "status": "success" if message_id else "failed",
            "message_id": message_id
        }
        webhook_logs.append(log)
        
        return {"status": "success", "message_id": message_id, "log": log}
    except Exception as e:
        logger.error(f"데이터 없음 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/watchhamster-error")
async def send_watchhamster_error(error_message: str, error_details: Optional[Dict] = None):
    """워치햄스터 오류 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_watchhamster_error(
            error_message=error_message,
            error_details=error_details,
            priority=MessagePriority.CRITICAL
        )
        
        log = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": "watchhamster_error",
            "bot_type": "WATCHHAMSTER_ERROR",
            "priority": "CRITICAL",
            "endpoint": "WATCHHAMSTER",
            "status": "success" if message_id else "failed",
            "message_id": message_id,
            "error_message": error_message,
            "metadata": error_details
        }
        webhook_logs.append(log)
        
        return {"status": "success", "message_id": message_id, "log": log}
    except Exception as e:
        logger.error(f"오류 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/watchhamster-status")
async def send_watchhamster_status(status_message: str, status_details: Optional[Dict] = None):
    """워치햄스터 상태 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_watchhamster_status(
            status_message=status_message,
            status_details=status_details,
            priority=MessagePriority.NORMAL
        )
        
        log = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": "watchhamster_status",
            "bot_type": "WATCHHAMSTER_STATUS",
            "priority": "NORMAL",
            "endpoint": "WATCHHAMSTER",
            "status": "success" if message_id else "failed",
            "message_id": message_id,
            "metadata": status_details
        }
        webhook_logs.append(log)
        
        return {"status": "success", "message_id": message_id, "log": log}
    except Exception as e:
        logger.error(f"상태 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/message-types")
async def get_message_types():
    """사용 가능한 메시지 타입 목록"""
    return {
        "message_types": [
            {
                "id": "test",
                "name": "테스트 메시지",
                "bot_type": "TEST",
                "priority": "LOW",
                "endpoint": "NEWS_MAIN",
                "description": "웹훅 시스템 테스트용 메시지"
            },
            {
                "id": "business_day_comparison",
                "name": "영업일 비교 분석",
                "bot_type": "NEWS_COMPARISON",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "description": "전일 대비 뉴스 발행 시간 비교 분석"
            },
            {
                "id": "delay_notification",
                "name": "지연 발행 알림",
                "bot_type": "NEWS_DELAY",
                "priority": "HIGH",
                "endpoint": "NEWS_MAIN",
                "description": "예상 발행 시간 대비 지연 감지 알림"
            },
            {
                "id": "daily_report",
                "name": "일일 통합 리포트",
                "bot_type": "NEWS_REPORT",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "description": "3개 뉴스 타입 종합 리포트"
            },
            {
                "id": "status_notification",
                "name": "정시 발행 알림",
                "bot_type": "NEWS_STATUS",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "description": "정시 발행 확인 메시지"
            },
            {
                "id": "no_data_notification",
                "name": "데이터 갱신 없음",
                "bot_type": "NEWS_NO_DATA",
                "priority": "LOW",
                "endpoint": "NEWS_MAIN",
                "description": "API 응답 없음 알림"
            },
            {
                "id": "watchhamster_error",
                "name": "워치햄스터 오류",
                "bot_type": "WATCHHAMSTER_ERROR",
                "priority": "CRITICAL",
                "endpoint": "WATCHHAMSTER",
                "description": "시스템 오류 알림"
            },
            {
                "id": "watchhamster_status",
                "name": "워치햄스터 상태",
                "bot_type": "WATCHHAMSTER_STATUS",
                "priority": "NORMAL",
                "endpoint": "WATCHHAMSTER",
                "description": "시스템 상태 보고"
            }
        ]
    }


@router.delete("/logs")
async def clear_logs():
    """로그 전체 삭제"""
    try:
        global webhook_logs
        count = len(webhook_logs)
        webhook_logs = []
        return {"status": "success", "deleted_count": count}
    except Exception as e:
        logger.error(f"로그 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
