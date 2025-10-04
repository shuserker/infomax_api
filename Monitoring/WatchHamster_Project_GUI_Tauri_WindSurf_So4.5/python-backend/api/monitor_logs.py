"""
모니터 실행 로그 API
각 모니터의 실행 내역, Input/Output 데이터 추적
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class MonitorExecutionLog(BaseModel):
    """모니터 실행 로그"""
    id: str
    monitor_name: str  # newyork-market-watch, kospi-close, exchange-rate
    timestamp: str
    duration_ms: int
    status: str  # success, failed, timeout
    
    # API 호출 정보
    api_endpoint: str
    api_method: str  # GET, POST
    
    # Input 데이터
    input_params: Dict[str, Any]
    input_headers: Dict[str, str]
    
    # Output 데이터
    output_status_code: int
    output_data: Dict[str, Any]
    output_size_bytes: int
    
    # 파싱 결과
    parsed_data: Optional[Dict[str, Any]] = None
    parsing_errors: Optional[List[str]] = None
    
    # 웹훅 발송 여부
    webhook_sent: bool = False
    webhook_response: Optional[Dict[str, Any]] = None
    
    # 에러 정보
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None


class MonitorStats(BaseModel):
    """모니터 통계"""
    monitor_name: str
    total_executions: int
    success_count: int
    failed_count: int
    avg_duration_ms: float
    last_execution: str
    last_success: str
    last_failure: Optional[str] = None


# 임시 로그 저장소 (실제로는 DB 사용)
execution_logs: List[Dict[str, Any]] = []


@router.get("/recent")
async def get_recent_logs(limit: int = Query(10, ge=1, le=100)):
    """최근 모니터 실행 로그 조회 (간단 버전)"""
    logs = execution_logs.copy()
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs[:limit]


@router.get("/executions", response_model=List[MonitorExecutionLog])
async def get_monitor_executions(
    monitor_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500)
):
    """모니터 실행 로그 조회"""
    logs = execution_logs.copy()
    
    # 필터링
    if monitor_name:
        logs = [log for log in logs if log.get("monitor_name") == monitor_name]
    if status:
        logs = [log for log in logs if log.get("status") == status]
    
    # 최신순 정렬
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return logs[:limit]


@router.get("/stats", response_model=List[MonitorStats])
async def get_monitor_stats():
    """모니터별 통계"""
    stats = []
    
    monitors = ["newyork-market-watch", "kospi-close", "exchange-rate"]
    
    for monitor in monitors:
        monitor_logs = [log for log in execution_logs if log.get("monitor_name") == monitor]
        
        if not monitor_logs:
            stats.append(MonitorStats(
                monitor_name=monitor,
                total_executions=0,
                success_count=0,
                failed_count=0,
                avg_duration_ms=0,
                last_execution="N/A",
                last_success="N/A",
                last_failure=None
            ))
            continue
        
        success_logs = [log for log in monitor_logs if log.get("status") == "success"]
        failed_logs = [log for log in monitor_logs if log.get("status") == "failed"]
        
        durations = [log.get("duration_ms", 0) for log in monitor_logs]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        last_execution = max(monitor_logs, key=lambda x: x.get("timestamp", ""))
        last_success_log = max(success_logs, key=lambda x: x.get("timestamp", "")) if success_logs else None
        last_failure_log = max(failed_logs, key=lambda x: x.get("timestamp", "")) if failed_logs else None
        
        stats.append(MonitorStats(
            monitor_name=monitor,
            total_executions=len(monitor_logs),
            success_count=len(success_logs),
            failed_count=len(failed_logs),
            avg_duration_ms=round(avg_duration, 2),
            last_execution=last_execution.get("timestamp", "N/A"),
            last_success=last_success_log.get("timestamp", "N/A") if last_success_log else "N/A",
            last_failure=last_failure_log.get("timestamp") if last_failure_log else None
        ))
    
    return stats


@router.post("/log")
async def add_monitor_log(log: MonitorExecutionLog):
    """모니터 실행 로그 추가 (내부용)"""
    execution_logs.append(log.dict())
    
    # 최대 1000개까지만 저장
    if len(execution_logs) > 1000:
        execution_logs.pop(0)
    
    logger.info(f"Monitor log added: {log.monitor_name} - {log.status}")
    return {"status": "ok", "log_id": log.id}


@router.get("/latest/{monitor_name}", response_model=Optional[MonitorExecutionLog])
async def get_latest_execution(monitor_name: str):
    """특정 모니터의 최신 실행 로그"""
    monitor_logs = [log for log in execution_logs if log.get("monitor_name") == monitor_name]
    
    if not monitor_logs:
        return None
    
    latest = max(monitor_logs, key=lambda x: x.get("timestamp", ""))
    return latest


# 데모 데이터 추가
def init_demo_data():
    """데모 데이터 초기화"""
    demo_logs = [
        MonitorExecutionLog(
            id="log-001",
            monitor_name="kospi-close",
            timestamp=datetime.now().isoformat(),
            duration_ms=1250,
            status="success",
            api_endpoint="https://global-api.einfomax.co.kr/apis/posco/news/kospi-close",
            api_method="GET",
            input_params={
                "date": "2025-10-04",
                "market": "kospi",
                "format": "json"
            },
            input_headers={
                "Authorization": "Bearer ****",
                "Content-Type": "application/json"
            },
            output_status_code=200,
            output_data={
                "title": "코스피, 외국인 매수에 2,600선 회복",
                "content": "코스피가 외국인 순매수에 힘입어...",
                "indices": [
                    {"name": "코스피", "value": 2650, "change": 0.8},
                    {"name": "코스닥", "value": 900, "change": 1.2}
                ]
            },
            output_size_bytes=1024,
            parsed_data={
                "market_situation": "상승",
                "main_indices_count": 2,
                "top_gainers_count": 5,
                "summary": "외국인 매수세로 상승 마감"
            },
            parsing_errors=None,
            webhook_sent=True,
            webhook_response={
                "status": 200,
                "message": "Dooray 웹훅 발송 성공"
            }
        ),
        MonitorExecutionLog(
            id="log-002",
            monitor_name="newyork-market-watch",
            timestamp=datetime.now().isoformat(),
            duration_ms=980,
            status="success",
            api_endpoint="https://global-api.einfomax.co.kr/apis/posco/news/newyork",
            api_method="GET",
            input_params={
                "date": "2025-10-04",
                "market": "nyse",
                "indices": ["dow", "nasdaq", "sp500"]
            },
            input_headers={
                "Authorization": "Bearer ****",
                "Content-Type": "application/json"
            },
            output_status_code=200,
            output_data={
                "title": "뉴욕증시, 기술주 강세에 상승 마감",
                "indices": [
                    {"name": "다우", "value": 35000, "change": 0.5},
                    {"name": "나스닥", "value": 14500, "change": 0.8}
                ]
            },
            output_size_bytes=856,
            parsed_data={
                "market_situation": "상승",
                "major_indices_count": 3,
                "summary": "기술주 강세로 상승 마감"
            },
            webhook_sent=True,
            webhook_response={
                "status": 200,
                "message": "Dooray 웹훅 발송 성공"
            }
        ),
        MonitorExecutionLog(
            id="log-003",
            monitor_name="exchange-rate",
            timestamp=datetime.now().isoformat(),
            duration_ms=750,
            status="failed",
            api_endpoint="https://global-api.einfomax.co.kr/apis/posco/news/exchange",
            api_method="GET",
            input_params={
                "date": "2025-10-04",
                "currencies": ["USD", "JPY", "EUR"]
            },
            input_headers={
                "Authorization": "Bearer ****",
                "Content-Type": "application/json"
            },
            output_status_code=500,
            output_data={},
            output_size_bytes=0,
            parsed_data=None,
            parsing_errors=["API 응답 오류: 500 Internal Server Error"],
            webhook_sent=False,
            webhook_response=None,
            error_message="API 호출 실패: 500 Internal Server Error",
            error_traceback="Traceback: ..."
        )
    ]
    
    for log in demo_logs:
        execution_logs.append(log.dict())


# 서버 시작 시 데모 데이터 로드
init_demo_data()


@router.post("/execute/{monitor_name}")
async def execute_monitor_manually(monitor_name: str):
    """모니터 수동 실행"""
    logger.info(f"Manual execution requested for: {monitor_name}")
    
    try:
        # 실제 모니터 실행 (여기서는 데모)
        import uuid
        from datetime import datetime
        
        log_id = f"log-{uuid.uuid4().hex[:8]}"
        
        # 모니터별 데모 실행
        if monitor_name == "kospi-close":
            log = MonitorExecutionLog(
                id=log_id,
                monitor_name=monitor_name,
                timestamp=datetime.now().isoformat(),
                duration_ms=1150,
                status="success",
                api_endpoint="https://global-api.einfomax.co.kr/apis/posco/news/kospi-close",
                api_method="GET",
                input_params={
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "market": "kospi"
                },
                input_headers={
                    "Authorization": "Bearer ****",
                    "Content-Type": "application/json"
                },
                output_status_code=200,
                output_data={
                    "title": "코스피 실시간 데이터",
                    "indices": [{"name": "코스피", "value": 2650}]
                },
                output_size_bytes=512,
                parsed_data={
                    "market_situation": "상승",
                    "summary": "수동 실행 테스트"
                },
                webhook_sent=True,
                webhook_response={"status": 200}
            )
        elif monitor_name == "newyork-market-watch":
            log = MonitorExecutionLog(
                id=log_id,
                monitor_name=monitor_name,
                timestamp=datetime.now().isoformat(),
                duration_ms=980,
                status="success",
                api_endpoint="https://global-api.einfomax.co.kr/apis/posco/news/newyork",
                api_method="GET",
                input_params={
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "market": "nyse"
                },
                input_headers={
                    "Authorization": "Bearer ****"
                },
                output_status_code=200,
                output_data={
                    "title": "뉴욕증시 실시간 데이터",
                    "indices": [{"name": "다우", "value": 35000}]
                },
                output_size_bytes=450,
                parsed_data={
                    "market_situation": "상승",
                    "summary": "수동 실행 테스트"
                },
                webhook_sent=True,
                webhook_response={"status": 200}
            )
        else:  # exchange-rate
            log = MonitorExecutionLog(
                id=log_id,
                monitor_name=monitor_name,
                timestamp=datetime.now().isoformat(),
                duration_ms=750,
                status="success",
                api_endpoint="https://global-api.einfomax.co.kr/apis/posco/news/exchange",
                api_method="GET",
                input_params={
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "currencies": ["USD", "JPY"]
                },
                input_headers={
                    "Authorization": "Bearer ****"
                },
                output_status_code=200,
                output_data={
                    "title": "환율 실시간 데이터",
                    "usd_krw": 1330.5
                },
                output_size_bytes=320,
                parsed_data={
                    "market_situation": "안정",
                    "summary": "수동 실행 테스트"
                },
                webhook_sent=True,
                webhook_response={"status": 200}
            )
        
        # 로그 저장
        execution_logs.append(log.dict())
        
        return {
            "status": "success",
            "message": f"{monitor_name} 모니터 실행 완료",
            "log": log
        }
        
    except Exception as e:
        logger.error(f"Monitor execution failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
