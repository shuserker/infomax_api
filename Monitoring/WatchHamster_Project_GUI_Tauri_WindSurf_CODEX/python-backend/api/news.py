"""
뉴스 모니터링 API 엔드포인트
POSCO 뉴스 데이터 조회, 갱신, 이력 관리 기능
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel

# 핵심 모듈 임포트
from core.infomax_client import InfomaxAPIClient
from core.news_parser import NewsDataParser
from enum import Enum

# 뉴스 상태 열거형 정의
class NewsStatusEnum(str, Enum):
    LATEST = "latest"
    DELAYED = "delayed"
    OUTDATED = "outdated"
    ERROR = "error"

logger = logging.getLogger(__name__)
router = APIRouter()

# 데이터 모델
class NewsStatus(BaseModel):
    type: str  # exchange-rate, newyork-market-watch, kospi-close
    status: str  # latest, delayed, outdated, error
    last_update: datetime
    expected_time: Optional[datetime] = None
    delay_minutes: Optional[int] = None
    data: Optional[Dict] = None
    error_message: Optional[str] = None

class NewsHistory(BaseModel):
    id: str
    type: str
    timestamp: datetime
    status: str
    data: Dict
    processing_time: float

class NewsRefreshRequest(BaseModel):
    news_types: Optional[List[str]] = None  # 특정 뉴스 타입만 갱신
    force: bool = False  # 강제 갱신 여부

# 전역 뉴스 상태 저장소
news_status_store = {
    "exchange-rate": {
        "status": "unknown",
        "last_update": datetime.now() - timedelta(hours=1),
        "expected_time": None,
        "delay_minutes": 0,
        "data": None,
        "error_message": None
    },
    "newyork-market-watch": {
        "status": "unknown", 
        "last_update": datetime.now() - timedelta(hours=2),
        "expected_time": None,
        "delay_minutes": 0,
        "data": None,
        "error_message": None
    },
    "kospi-close": {
        "status": "unknown",
        "last_update": datetime.now() - timedelta(hours=3),
        "expected_time": None,
        "delay_minutes": 0,
        "data": None,
        "error_message": None
    }
}

# 뉴스 이력 저장소 (최근 100개 항목)
news_history_store = []

# API 클라이언트 및 파서 인스턴스
api_client = None
news_parser = None

def get_api_client():
    """API 클라이언트 인스턴스 반환"""
    global api_client
    if not api_client:
        # services.py에서 인스턴스 가져오기 시도
        from api.services import get_service_instance
        api_client = get_service_instance("infomax_client")
        
        # 없으면 새로 생성
        if not api_client:
            api_client = InfomaxAPIClient(
                base_url="https://global-api.einfomax.co.kr/apis/posco/news"
            )
    return api_client

def get_news_parser():
    """뉴스 파서 인스턴스 반환"""
    global news_parser
    if not news_parser:
        # services.py에서 인스턴스 가져오기 시도
        from api.services import get_service_instance
        news_parser = get_service_instance("news_parser")
        
        # 없으면 새로 생성
        if not news_parser:
            news_parser = NewsDataParser()
    return news_parser

@router.get("/status")
async def get_news_status(news_type: Optional[str] = Query(None, description="특정 뉴스 타입 조회")):
    """뉴스 상태 조회"""
    logger.info(f"뉴스 상태 조회 요청: {news_type}")
    
    try:
        if news_type:
            # 특정 뉴스 타입 조회
            if news_type not in news_status_store:
                raise HTTPException(status_code=404, detail=f"뉴스 타입을 찾을 수 없습니다: {news_type}")
            
            status_data = news_status_store[news_type]
            return NewsStatus(
                type=news_type,
                status=status_data["status"],
                last_update=status_data["last_update"],
                expected_time=status_data["expected_time"],
                delay_minutes=status_data["delay_minutes"],
                data=status_data["data"],
                error_message=status_data["error_message"]
            )
        else:
            # 모든 뉴스 타입 조회
            result = []
            for news_type, status_data in news_status_store.items():
                result.append(NewsStatus(
                    type=news_type,
                    status=status_data["status"],
                    last_update=status_data["last_update"],
                    expected_time=status_data["expected_time"],
                    delay_minutes=status_data["delay_minutes"],
                    data=status_data["data"],
                    error_message=status_data["error_message"]
                ))
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"뉴스 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="뉴스 상태 조회 중 오류가 발생했습니다")

@router.post("/refresh")
async def refresh_news_data(
    background_tasks: BackgroundTasks,
    request: NewsRefreshRequest = NewsRefreshRequest()
):
    """뉴스 데이터 수동 갱신"""
    logger.info(f"뉴스 데이터 갱신 요청: {request.news_types}, force={request.force}")
    
    try:
        # 갱신할 뉴스 타입 결정
        news_types_to_refresh = request.news_types or list(news_status_store.keys())
        
        # 유효한 뉴스 타입인지 확인
        invalid_types = [nt for nt in news_types_to_refresh if nt not in news_status_store]
        if invalid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"유효하지 않은 뉴스 타입: {invalid_types}"
            )
        
        # 백그라운드에서 뉴스 데이터 갱신 작업 수행
        background_tasks.add_task(_refresh_news_task, news_types_to_refresh, request.force)
        
        return {
            "message": f"뉴스 데이터 갱신 중...",
            "news_types": news_types_to_refresh,
            "force": request.force
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"뉴스 데이터 갱신 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="뉴스 데이터 갱신 요청 처리 중 오류가 발생했습니다")

@router.get("/history")
async def get_news_history(
    news_type: Optional[str] = Query(None, description="특정 뉴스 타입 필터"),
    limit: int = Query(50, ge=1, le=100, description="조회할 항목 수"),
    offset: int = Query(0, ge=0, description="시작 오프셋")
):
    """뉴스 이력 조회"""
    logger.info(f"뉴스 이력 조회 요청: type={news_type}, limit={limit}, offset={offset}")
    
    try:
        # 필터링된 이력 데이터
        filtered_history = news_history_store
        
        if news_type:
            filtered_history = [h for h in news_history_store if h.get("type") == news_type]
        
        # 최신 순으로 정렬
        filtered_history.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
        
        # 페이징 적용
        total_count = len(filtered_history)
        paginated_history = filtered_history[offset:offset + limit]
        
        # NewsHistory 모델로 변환
        result = []
        for item in paginated_history:
            result.append(NewsHistory(
                id=item.get("id", "unknown"),
                type=item.get("type", "unknown"),
                timestamp=item.get("timestamp", datetime.now()),
                status=item.get("status", "unknown"),
                data=item.get("data", {}),
                processing_time=item.get("processing_time", 0.0)
            ))
        
        return {
            "items": result,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total_count
        }
        
    except Exception as e:
        logger.error(f"뉴스 이력 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="뉴스 이력 조회 중 오류가 발생했습니다")

@router.delete("/history")
async def clear_news_history(news_type: Optional[str] = Query(None, description="특정 뉴스 타입만 삭제")):
    """뉴스 이력 정리"""
    logger.info(f"뉴스 이력 정리 요청: {news_type}")
    
    try:
        global news_history_store
        
        if news_type:
            # 특정 뉴스 타입만 삭제
            original_count = len(news_history_store)
            news_history_store = [h for h in news_history_store if h.get("type") != news_type]
            deleted_count = original_count - len(news_history_store)
            
            return {
                "message": f"'{news_type}' 뉴스 이력이 정리되었습니다",
                "deleted_count": deleted_count
            }
        else:
            # 모든 이력 삭제
            deleted_count = len(news_history_store)
            news_history_store.clear()
            
            return {
                "message": "모든 뉴스 이력이 정리되었습니다",
                "deleted_count": deleted_count
            }
            
    except Exception as e:
        logger.error(f"뉴스 이력 정리 실패: {e}")
        raise HTTPException(status_code=500, detail="뉴스 이력 정리 중 오류가 발생했습니다")

# 백그라운드 작업 함수
async def _refresh_news_task(news_types: List[str], force: bool = False):
    """뉴스 데이터 갱신 백그라운드 작업"""
    logger.info(f"뉴스 데이터 갱신 작업 시작: {news_types}")
    
    client = get_api_client()
    parser = get_news_parser()
    
    for news_type in news_types:
        try:
            start_time = datetime.now()
            
            # API에서 뉴스 데이터 조회
            logger.info(f"뉴스 데이터 조회 중: {news_type}")
            raw_data = await client.fetch_news_data(news_type)
            
            if not raw_data:
                # 데이터가 없는 경우
                news_status_store[news_type].update({
                    "status": "error",
                    "last_update": datetime.now(),
                    "error_message": "API에서 데이터를 가져올 수 없습니다",
                    "data": None
                })
                continue
            
            # 뉴스 데이터 파싱 및 상태 판단
            logger.info(f"뉴스 데이터 파싱 중: {news_type}")
            parsed_news = await parser.parse_news_data(raw_data, news_type)
            
            # 상태 저장소 업데이트
            news_status_store[news_type].update({
                "status": parsed_news.status.value if hasattr(parsed_news, 'status') else "unknown",
                "last_update": datetime.now(),
                "expected_time": getattr(parsed_news, 'expected_time', None),
                "delay_minutes": getattr(parsed_news, 'delay_minutes', 0),
                "data": parsed_news.dict() if hasattr(parsed_news, 'dict') else raw_data,
                "error_message": None
            })
            
            # 처리 시간 계산
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 이력에 추가
            import uuid
            history_entry = {
                "id": str(uuid.uuid4()),
                "type": news_type,
                "timestamp": datetime.now(),
                "status": parsed_news.status.value if hasattr(parsed_news, 'status') else "processed",
                "data": parsed_news.dict() if hasattr(parsed_news, 'dict') else raw_data,
                "processing_time": processing_time
            }
            
            news_history_store.append(history_entry)
            
            # 이력 크기 제한 (최근 100개만 유지)
            if len(news_history_store) > 100:
                news_history_store.pop(0)
            
            logger.info(f"뉴스 데이터 갱신 완료: {news_type} (처리시간: {processing_time:.2f}초)")
            
            # WebSocket으로 실시간 업데이트 전송
            try:
                from api.websocket import manager
                await manager.broadcast_json({
                    "type": "news_update",
                    "data": {
                        "news_type": news_type,
                        "status": news_status_store[news_type]["status"],
                        "last_update": news_status_store[news_type]["last_update"].isoformat(),
                        "processing_time": processing_time
                    },
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"WebSocket 뉴스 업데이트 전송 실패: {e}")
            
        except Exception as e:
            logger.error(f"뉴스 데이터 갱신 실패 ({news_type}): {e}")
            
            # 오류 상태로 업데이트
            news_status_store[news_type].update({
                "status": "error",
                "last_update": datetime.now(),
                "error_message": str(e),
                "data": None
            })
            
            # 오류 이력 추가
            import uuid
            error_entry = {
                "id": str(uuid.uuid4()),
                "type": news_type,
                "timestamp": datetime.now(),
                "status": "error",
                "data": {"error": str(e)},
                "processing_time": 0.0
            }
            
            news_history_store.append(error_entry)
        
        # 각 뉴스 타입 간 잠시 대기
        await asyncio.sleep(1)
    
    logger.info("뉴스 데이터 갱신 작업 완료")

# 주기적 뉴스 갱신 함수 (백그라운드 태스크에서 사용)
async def periodic_news_refresh():
    """주기적 뉴스 데이터 갱신"""
    logger.info("주기적 뉴스 갱신 태스크 시작")
    
    while True:
        try:
            # 5분마다 뉴스 데이터 갱신
            await asyncio.sleep(300)  # 5분
            
            logger.info("주기적 뉴스 데이터 갱신 시작")
            await _refresh_news_task(list(news_status_store.keys()), force=False)
            
        except asyncio.CancelledError:
            logger.info("주기적 뉴스 갱신 태스크가 취소되었습니다")
            break
        except Exception as e:
            logger.error(f"주기적 뉴스 갱신 오류: {e}")
            await asyncio.sleep(60)  # 오류 시 1분 후 재시도

# 뉴스 상태 초기화 함수
async def initialize_news_status():
    """뉴스 상태 초기화"""
    logger.info("뉴스 상태 초기화 시작")
    
    try:
        # 초기 뉴스 데이터 로드
        await _refresh_news_task(list(news_status_store.keys()), force=True)
        
        logger.info("뉴스 상태 초기화 완료")
        
    except Exception as e:
        logger.error(f"뉴스 상태 초기화 실패: {e}")

# 뉴스 타입별 예상 발행 시간 계산 함수
def get_expected_publish_time(news_type: str) -> Optional[datetime]:
    """뉴스 타입별 예상 발행 시간 계산"""
    try:
        now = datetime.now()
        
        if news_type == "exchange-rate":
            # 환율: 평일 오전 9시
            expected = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now.weekday() >= 5:  # 주말
                return None
            if now.hour >= 9:
                expected += timedelta(days=1)
            return expected
            
        elif news_type == "newyork-market-watch":
            # 뉴욕증시: 평일 오전 6시 (한국시간)
            expected = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if now.weekday() >= 5:  # 주말
                return None
            if now.hour >= 6:
                expected += timedelta(days=1)
            return expected
            
        elif news_type == "kospi-close":
            # 코스피 마감: 평일 오후 3시 30분
            expected = now.replace(hour=15, minute=30, second=0, microsecond=0)
            if now.weekday() >= 5:  # 주말
                return None
            if now.hour >= 15 and now.minute >= 30:
                expected += timedelta(days=1)
            return expected
            
        return None
        
    except Exception as e:
        logger.error(f"예상 발행 시간 계산 실패 ({news_type}): {e}")
        return None

# 뉴스 상태 요약 정보 제공
@router.get("/summary")
async def get_news_summary():
    """뉴스 상태 요약 정보"""
    logger.info("뉴스 상태 요약 조회 요청")
    
    try:
        total_news_types = len(news_status_store)
        latest_count = sum(1 for status in news_status_store.values() if status["status"] == "latest")
        delayed_count = sum(1 for status in news_status_store.values() if status["status"] == "delayed")
        error_count = sum(1 for status in news_status_store.values() if status["status"] == "error")
        
        # 최근 업데이트 시간
        last_updates = [status["last_update"] for status in news_status_store.values()]
        most_recent_update = max(last_updates) if last_updates else None
        
        # 전체 상태 판단
        overall_status = "healthy"
        if error_count > 0:
            overall_status = "error"
        elif delayed_count > 0:
            overall_status = "warning"
        
        return {
            "overall_status": overall_status,
            "total_news_types": total_news_types,
            "latest_count": latest_count,
            "delayed_count": delayed_count,
            "error_count": error_count,
            "most_recent_update": most_recent_update,
            "history_count": len(news_history_store)
        }
        
    except Exception as e:
        logger.error(f"뉴스 상태 요약 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="뉴스 상태 요약 조회 중 오류가 발생했습니다")