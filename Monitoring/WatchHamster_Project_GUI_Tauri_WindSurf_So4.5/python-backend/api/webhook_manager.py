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
        try:
            message_generator = NewsMessageGenerator(test_mode=False)
            logger.info("메시지 생성기 초기화 성공")
        except Exception as e:
            logger.error(f"메시지 생성기 초기화 실패: {e}")
            message_generator = None
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
async def get_webhook_log_detail(log_id: str, company_id: str = "posco"):
    """특정 로그 상세 조회"""
    try:
        db = get_db()
        logs = db.get_webhook_logs(company_id=company_id, limit=1000)
        log = next((l for l in logs if l.get('id') == log_id), None)
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
async def send_business_day_comparison(data: Dict[str, Any], company_id: str = "posco"):
    """영업일 비교 분석 메시지 발송"""
    try:
        sender = get_webhook_sender()
        result = sender.send_business_day_comparison(
            raw_data=data.get('raw_data', {}),
            historical_data=data.get('historical_data'),
            priority=MessagePriority[data.get('priority', 'NORMAL')]
        )
        
        # 결과에서 message_id와 full_message 추출
        message_id = result.get('message_id') if isinstance(result, dict) else result
        full_message = result.get('full_message') if isinstance(result, dict) else None
        success = result.get('success', False) if isinstance(result, dict) else bool(message_id)
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="business_day_comparison",
            bot_type="NEWS_COMPARISON",
            priority=data.get('priority', 'NORMAL'),
            endpoint="NEWS_MAIN",
            status="success" if success else "failed",
            message_id=message_id,
            full_message=full_message,
            metadata={"raw_data": data}
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "business_day_comparison",
                "bot_type": "NEWS_COMPARISON",
                "priority": data.get('priority', 'NORMAL'),
                "endpoint": "NEWS_MAIN",
                "status": "success" if message_id else "failed",
                "message_id": message_id
            }
        }
    except Exception as e:
        logger.error(f"영업일 비교 메시지 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/delay-notification")
async def send_delay_notification(news_type: str, delay_minutes: int, data: Dict[str, Any], company_id: str = "posco"):
    """지연 발행 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_delay_notification(
            news_type=news_type,
            current_data=data.get('current_data', {}),
            delay_minutes=delay_minutes,
            priority=MessagePriority.HIGH
        )
        
        # 메시지 내용 생성 (표시용)
        full_message = f"⏰ {news_type} 지연 발행\n지연 시간: {delay_minutes}분\n발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="delay_notification",
            bot_type="NEWS_DELAY",
            priority="HIGH",
            endpoint="NEWS_MAIN",
            status="success" if message_id else "failed",
            message_id=message_id,
            full_message=full_message if message_id else None,
            metadata={"news_type": news_type, "delay_minutes": delay_minutes, "current_data": data.get('current_data', {})}
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "delay_notification",
                "bot_type": "NEWS_DELAY",
                "priority": "HIGH",
                "endpoint": "NEWS_MAIN",
                "status": "success" if message_id else "failed",
                "message_id": message_id
            }
        }
    except Exception as e:
        logger.error(f"지연 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/daily-report")
async def send_daily_integrated_report(data: Dict[str, Any], company_id: str = "posco"):
    """일일 통합 리포트 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_daily_integrated_report(
            raw_data=data.get('raw_data', {}),
            report_url=data.get('report_url'),
            priority=MessagePriority.NORMAL
        )
        
        # 메시지 내용 생성 (표시용)
        full_message = f"📊 일일 통합 리포트\n리포트 일자: {datetime.now().strftime('%Y-%m-%d')}\n리포트 URL: {data.get('report_url', '없음')}"
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="daily_report",
            bot_type="NEWS_REPORT",
            priority="NORMAL",
            endpoint="NEWS_MAIN",
            status="success" if message_id else "failed",
            message_id=message_id,
            full_message=full_message if message_id else None,
            metadata={"report_url": data.get('report_url'), "raw_data": data.get('raw_data', {})}
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "daily_report",
                "bot_type": "NEWS_REPORT",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "status": "success" if message_id else "failed",
                "message_id": message_id
            }
        }
    except Exception as e:
        logger.error(f"일일 리포트 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/status-notification")
async def send_status_notification(data: Dict[str, Any], company_id: str = "posco"):
    """정시 발행 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_status_notification(
            raw_data=data.get('raw_data', {}),
            priority=MessagePriority.NORMAL
        )
        
        # 메시지 내용 생성 (표시용)
        full_message = f"✅ 정시 발행 알림\n확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n상태: 정상 발행 확인"
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="status_notification",
            bot_type="NEWS_STATUS",
            priority="NORMAL",
            endpoint="NEWS_MAIN",
            status="success" if message_id else "failed",
            message_id=message_id,
            full_message=full_message if message_id else None,
            metadata={"raw_data": data.get('raw_data', {})}
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "status_notification",
                "bot_type": "NEWS_STATUS",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "status": "success" if message_id else "failed",
                "message_id": message_id
            }
        }
    except Exception as e:
        logger.error(f"정시 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/no-data-notification")
async def send_no_data_notification(data: Dict[str, Any], company_id: str = "posco"):
    """데이터 갱신 없음 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_no_data_notification(
            raw_data=data.get('raw_data', {}),
            priority=MessagePriority.LOW
        )
        
        # 메시지 내용 생성 (표시용)
        full_message = f"🔴 데이터 갱신 없음 알림\n확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n상황: API 응답 없음"
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="no_data_notification",
            bot_type="NEWS_NO_DATA",
            priority="LOW",
            endpoint="NEWS_MAIN",
            status="success" if message_id else "failed",
            message_id=message_id,
            full_message=full_message if message_id else None,
            metadata={"raw_data": data.get('raw_data', {})}
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "no_data_notification",
                "bot_type": "NEWS_NO_DATA",
                "priority": "LOW",
                "endpoint": "NEWS_MAIN",
                "status": "success" if message_id else "failed",
                "message_id": message_id
            }
        }
    except Exception as e:
        logger.error(f"데이터 없음 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/watchhamster-error")
async def send_watchhamster_error(error_message: str, error_details: Optional[Dict] = None, company_id: str = "posco"):
    """워치햄스터 오류 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_watchhamster_error(
            error_message=error_message,
            error_details=error_details,
            priority=MessagePriority.CRITICAL
        )
        
        # 메시지 내용 생성 (표시용)
        full_message = f"❌ POSCO 워치햄스터 오류 발생\n발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n오류 내용: {error_message}"
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="watchhamster_error",
            bot_type="WATCHHAMSTER_ERROR",
            priority="CRITICAL",
            endpoint="WATCHHAMSTER",
            status="success" if message_id else "failed",
            message_id=message_id,
            full_message=full_message if message_id else None,
            error_message=error_message,
            metadata=error_details
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "watchhamster_error",
                "bot_type": "WATCHHAMSTER_ERROR",
                "priority": "CRITICAL",
                "endpoint": "WATCHHAMSTER",
                "status": "success" if message_id else "failed",
                "message_id": message_id
            }
        }
    except Exception as e:
        logger.error(f"오류 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/watchhamster-status")
async def send_watchhamster_status(status_message: str, status_details: Optional[Dict] = None, company_id: str = "posco"):
    """워치햄스터 상태 알림 발송"""
    try:
        sender = get_webhook_sender()
        message_id = sender.send_watchhamster_status(
            status_message=status_message,
            status_details=status_details,
            priority=MessagePriority.NORMAL
        )
        
        # 메시지 내용 생성 (표시용)
        full_message = f"🎯🛡️ POSCO 워치햄스터 상태 보고\n보고 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n상태 메시지: {status_message}"
        
        # 데이터베이스에 로그 저장
        save_webhook_log(
            company_id=company_id,
            message_type="watchhamster_status",
            bot_type="WATCHHAMSTER_STATUS",
            priority="NORMAL",
            endpoint="WATCHHAMSTER",
            status="success" if message_id else "failed",
            message_id=message_id,
            full_message=full_message if message_id else None,
            metadata=status_details
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "log": {
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "message_type": "watchhamster_status",
                "bot_type": "WATCHHAMSTER_STATUS",
                "priority": "NORMAL",
                "endpoint": "WATCHHAMSTER",
                "status": "success" if message_id else "failed",
                "message_id": message_id
            }
        }
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


@router.get("/message-types/{message_type_id}/detail")
async def get_message_type_detail(message_type_id: str, company_id: str = "posco"):
    """메시지 타입 상세 정보 조회 (실제 템플릿, 최근 로그, Input/Output)"""
    try:
        db = get_db()
        generator = get_message_generator()
        
        # 메시지 타입 기본 정보
        message_info_map = {
            "test": {
                "id": "test",
                "name": "테스트 메시지",
                "bot_type": "TEST",
                "priority": "LOW",
                "endpoint": "NEWS_MAIN",
                "description": "웹훅 시스템 테스트용 메시지"
            },
            "business_day_comparison": {
                "id": "business_day_comparison",
                "name": "영업일 비교 분석",
                "bot_type": "NEWS_COMPARISON",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "description": "전일 대비 뉴스 발행 시간 비교 분석"
            },
            "delay_notification": {
                "id": "delay_notification",
                "name": "지연 발행 알림",
                "bot_type": "NEWS_DELAY",
                "priority": "HIGH",
                "endpoint": "NEWS_MAIN",
                "description": "예상 발행 시간 대비 지연 감지 알림"
            },
            "daily_report": {
                "id": "daily_report",
                "name": "일일 통합 리포트",
                "bot_type": "NEWS_REPORT",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "description": "3개 뉴스 타입 종합 리포트"
            },
            "status_notification": {
                "id": "status_notification",
                "name": "정시 발행 알림",
                "bot_type": "NEWS_STATUS",
                "priority": "NORMAL",
                "endpoint": "NEWS_MAIN",
                "description": "정시 발행 확인 메시지"
            },
            "no_data_notification": {
                "id": "no_data_notification",
                "name": "데이터 갱신 없음",
                "bot_type": "NEWS_NO_DATA",
                "priority": "LOW",
                "endpoint": "NEWS_MAIN",
                "description": "API 응답 없음 알림"
            },
            "watchhamster_error": {
                "id": "watchhamster_error",
                "name": "워치햄스터 오류",
                "bot_type": "WATCHHAMSTER_ERROR",
                "priority": "CRITICAL",
                "endpoint": "WATCHHAMSTER",
                "description": "시스템 오류 알림"
            },
            "watchhamster_status": {
                "id": "watchhamster_status",
                "name": "워치햄스터 상태",
                "bot_type": "WATCHHAMSTER_STATUS",
                "priority": "NORMAL",
                "endpoint": "WATCHHAMSTER",
                "description": "시스템 상태 보고"
            }
        }
        
        message_info = message_info_map.get(message_type_id)
        if not message_info:
            raise HTTPException(status_code=404, detail="메시지 타입을 찾을 수 없습니다")
        
        # 실제 템플릿 생성 (메시지 생성기 사용)
        template = ""
        
        # 실제 템플릿 구조를 보여주기 위해 변수 형태로 표시
        template_structures = {
            "business_day_comparison": """# 📊 영업일 비교 분석

**🕐 분석 시간**: {today} {current_time}

**🔮 시장 동향 예측**:
  {market_prediction}

**📊 뉴스별 발행 비교**:
```
[NEWYORK MARKET WATCH]
├ 현재: {newyork_status} {newyork_time}
├ 직전: {newyork_historical_status} {newyork_historical_time}
└ 예상: {newyork_expected_time} (±{tolerance_minutes}분)

[KOSPI CLOSE]
├ 현재: {kospi_status} {kospi_time}
├ 직전: {kospi_historical_status} {kospi_historical_time}
└ 예상: {kospi_expected_time} (±{tolerance_minutes}분)

[EXCHANGE RATE]
├ 현재: {exchange_status} {exchange_time}
├ 직전: {exchange_historical_status} {exchange_historical_time}
└ 예상: {exchange_expected_time} (±{tolerance_minutes}분)
```

**📈 종합 분석**: {comprehensive_analysis}""",
            
            "delay_notification": """# 🟡 {news_type} 지연 발행

**📅 발행 시간**: {today} {publish_time}
**📊 패턴 분석**: ⏱️ {delay_minutes}분 지연 발행 ({actual_time})
**⏰ 예상**: {expected_time} → **실제**: {actual_time}
**📋 제목**: {news_title}

**🔍 지연 원인 분석**: {delay_analysis}""",
            
            "daily_report": """# 📊 일일 통합 분석 리포트

**📅 분석 일자**: {today}
**📊 발행 현황**: {published_count}/{total_count}개 완료

**📋 뉴스별 발행 현황**:
  🌆 **NEWYORK MARKET WATCH**: {newyork_status} ({newyork_time})
  📈 **KOSPI CLOSE**: {kospi_status} ({kospi_time})
  💱 **EXCHANGE RATE**: {exchange_status} ({exchange_time})

**📈 상세 리포트**: [{report_url}]({report_url})
**🎯 전체 성과**: {overall_performance}""",
            
            "status_notification": """# ✅ 정시 발행 알림

**📅 확인 시간**: {today} {check_time}
**📊 현재 발행 상태**: {current_status}

**📋 발행 현황**:
  🌆 **NEWYORK**: {newyork_status} ({newyork_time})
  📈 **KOSPI**: {kospi_status} ({kospi_time})
  💱 **EXCHANGE**: {exchange_status} ({exchange_time})

**✅ 정상 발행이 확인되었습니다**.""",
            
            "no_data_notification": """# 🔴 데이터 갱신 없음 알림

**📅 확인 시간**: {today} {check_time}
**🚨 상황**: {alert_status}

**📋 미갱신 항목**:
{no_data_items}

**⏰ 마지막 갱신**: {last_update_time}
**🔧 권장사항**: {recommendation}""",
            
            "test": """# 🧪 [TEST] POSCO 시스템 테스트

**📅 테스트 시간**: {today} {test_time}
**📋 테스트 내용**: {test_content}
**🎯 테스트 대상**: {test_target}

**✅ 결과**: {test_result}
**📊 응답 시간**: {response_time}ms""",
            
            "watchhamster_error": """# ❌ POSCO 워치햄스터 오류 발생

**📅 발생 시간**: {today} {error_time}
**🚨 오류 내용**: {error_message}
**🔍 오류 타입**: {error_type}

**📋 상세 정보**:
  • **오류 코드**: {error_code}
  • **재시도 횟수**: {retry_count}회
  • **마지막 시도**: {last_attempt}
  • **영향 범위**: {impact_scope}

**🔧 복구 상태**: {recovery_status}""",
            
            "watchhamster_status": """# 🎯🛡️ POSCO 워치햄스터 상태 보고

**📅 보고 시간**: {today} {report_time}
**📊 시스템 상태**: {system_status}
**🔋 가동률**: {uptime_percentage}%

**📋 상세 정보**:
  • **모니터링 상태**: {monitoring_status}
  • **처리된 뉴스**: {processed_news_count}건
  • **전송 성공률**: {success_rate}%
  • **마지막 체크**: {last_check_time}
  • **메모리 사용량**: {memory_usage}%
  • **CPU 사용량**: {cpu_usage}%

**✅ 시스템 종합 상태**: {overall_status}"""
        }
        
        # 해당 메시지 타입의 템플릿 구조 가져오기
        template = template_structures.get(message_type_id)
        
        # 템플릿이 없으면 기본 설명 제공
        if not template:
            template = f"""# {message_info['name']}

**설명**: {message_info['description']}
**봇 타입**: {message_info['bot_type']}
**채널**: {message_info['endpoint']}
**우선순위**: {message_info['priority']}

**템플릿 변수**:
- `{{today}}`: 오늘 날짜
- `{{current_time}}`: 현재 시간
- `{{raw_data}}`: 입력 데이터
- `{{company_id}}`: 회사 ID
- `{{priority}}`: 메시지 우선순위

*실제 메시지는 발송 시 이 템플릿에 데이터를 대입하여 동적으로 생성됩니다.*"""
        
        # 최근 로그 조회 (실제 데이터베이스에서)
        logs = db.get_webhook_logs(company_id, limit=100)
        recent_log = next((log for log in logs if log.get('message_type') == message_type_id), None)
        
        # Input/Output - 실제 로그가 있으면 사용, 없으면 실제 예시
        if recent_log and recent_log.get('metadata'):
            input_data = recent_log.get('metadata', {})
            output_data = {
                "message_id": recent_log.get('message_id'),
                "status": recent_log.get('status'),
                "timestamp": recent_log.get('timestamp'),
                "full_message": recent_log.get('full_message', '메시지 내용 없음')
            }
        else:
            # 메시지 타입별 실제 예시 데이터
            if message_type_id == "business_day_comparison":
                input_data = {
                    "raw_data": {
                        "newyork-market-watch": {
                            "title": "[20251001] 뉴욕증시, 9월 고용지표 호조에 상승 마감",
                            "time": "060500",
                            "status": "latest"
                        },
                        "kospi-close": {
                            "title": "[20251001] KOSPI, 외국인 순매수에 2,550선 돌파",
                            "time": "154200",
                            "status": "latest"
                        }
                    },
                    "historical_data": {
                        "newyork-market-watch": {
                            "title": "[20250930] 뉴욕증시, 연준 금리 동결에 혼조 마감",
                            "time": "060000"
                        }
                    },
                    "priority": "NORMAL"
                }
                output_data = {
                    "message_id": "20251004_165238_b723452c",
                    "status": "success",
                    "timestamp": "2025-10-04T16:52:38",
                    "full_message": "📊 영업일 비교 분석\n🕐 분석 시간: 2025-10-04 16:52\n\n🔮 시장 동향 예측:\n  전반적 발행 지연 우려 | 마감 시간대 - 종가 확정 대기\n\n[NEWYORK MARKET WATCH]\n├ 현재: 🔴 발행 지연\n├ 직전: 🔄 06:00\n└ 예상: ⏰ 06:00 (±15분)"
                }
            elif message_type_id == "delay_notification":
                input_data = {
                    "news_type": "newyork-market-watch",
                    "delay_minutes": 5,
                    "current_data": {
                        "title": "[20251001] 뉴욕증시, 9월 고용지표 호조에 상승 마감",
                        "time": "060500"
                    },
                    "priority": "HIGH"
                }
                output_data = {
                    "message_id": "20251004_165238_49ded0cf",
                    "status": "success",
                    "timestamp": "2025-10-04T16:52:38",
                    "full_message": "🟡 newyork market watch 지연 발행\n\n📅 발행 시간: 2025-10-04 06:05:00\n📊 패턴 분석: ⏱️ 5분 지연 발행 (06:05)\n⏰ 예상: 06:00 → 실제: 06:05\n📋 제목: [20251001] 뉴욕증시, 9월 고용지표 호조에 상승 마감"
                }
            elif message_type_id == "daily_report":
                input_data = {
                    "raw_data": {
                        "newyork-market-watch": {"title": "[20251001] 뉴욕증시 상승", "time": "060500"},
                        "kospi-close": {"title": "[20251001] KOSPI 상승", "time": "154200"},
                        "exchange-rate": {"title": "[20251001] 원/달러 환율", "time": "163200"}
                    },
                    "report_url": "http://127.0.0.1:8000/reports/20251001",
                    "priority": "NORMAL"
                }
                output_data = {
                    "message_id": "20251004_165238_bc4876ae",
                    "status": "success",
                    "timestamp": "2025-10-04T16:52:38",
                    "full_message": "📊 일일 통합 분석 리포트\n\n📅 분석 일자: 2025년 10월 04일\n📊 발행 현황: 3/3개 완료\n\n📋 뉴스별 발행 현황:\n  🌆 NEWYORK MARKET WATCH: ✅ 발행 완료 (06:05)\n  📈 KOSPI CLOSE: ✅ 발행 완료 (15:42)\n  💱 EXCHANGE RATE: ✅ 발행 완료 (16:32)"
                }
            elif message_type_id == "test":
                input_data = {
                    "test_content": "웹훅 시스템 연결 테스트",
                    "priority": "LOW"
                }
                output_data = {
                    "message_id": "20251004_165238_test123",
                    "status": "success",
                    "timestamp": "2025-10-04T16:52:38",
                    "full_message": "🧪 [TEST] POSCO 시스템 테스트\n\n📋 테스트 내용: 웹훅 시스템 연결 테스트\n\n✅ 웹훅 전송 시스템이 정상적으로 작동합니다."
                }
            else:
                input_data = {
                    "raw_data": {"sample": "data"},
                    "priority": "NORMAL"
                }
                output_data = {
                    "message_id": "20251004_165238_sample",
                    "status": "success",
                    "timestamp": "2025-10-04T16:52:38",
                    "full_message": "샘플 메시지 내용"
                }
        
        return {
            "message_type": message_info,
            "template": template,
            "recent_log": {
                "id": recent_log.get('id') if recent_log else None,
                "timestamp": recent_log.get('timestamp') if recent_log else "발송 내역 없음",
                "status": recent_log.get('status') if recent_log else "N/A",
                "message_id": recent_log.get('message_id') if recent_log else "N/A",
                "bot_type": recent_log.get('bot_type') if recent_log else message_info['bot_type'],
                "priority": recent_log.get('priority') if recent_log else message_info['priority'],
                "endpoint": recent_log.get('endpoint') if recent_log else message_info['endpoint'],
                "full_message": recent_log.get('full_message') if recent_log else "발송 내역 없음"
            },
            "input_example": input_data,
            "output_example": output_data,
            "variables": ["raw_data", "historical_data", "priority", "company_id"],
            "usage_count": len([log for log in logs if log.get('message_type') == message_type_id]),
            "last_sent": recent_log.get('timestamp') if recent_log else None,
            "success_rate": "100%" if recent_log and recent_log.get('status') == 'success' else "N/A",
            "webhook_url": "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg" if message_info['endpoint'] == 'NEWS_MAIN' else "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메시지 상세 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/logs")
async def clear_logs(company_id: str = "posco"):
    """로그 전체 삭제"""
    try:
        db = get_db()
        count = db.clear_webhook_logs(company_id=company_id)
        return {"status": "success", "deleted_count": count}
    except Exception as e:
        logger.error(f"로그 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
