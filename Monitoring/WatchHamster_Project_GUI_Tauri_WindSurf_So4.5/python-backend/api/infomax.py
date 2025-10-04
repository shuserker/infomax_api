#!/usr/bin/env python3
"""
InfoMax API 프록시 서버
브라우저 CORS 제한을 우회하여 InfoMax API 호출을 프록시
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# InfoMax API 설정
INFOMAX_BASE_URL = "https://infomaxy.einfomax.co.kr/api"
REQUEST_TIMEOUT = 30.0

router = APIRouter(prefix="/infomax", tags=["InfoMax API Proxy"])


class InfoMaxResponse(BaseModel):
    success: bool
    data: Any
    status: int
    url: str
    timestamp: str
    execution_time: float


class InfoMaxError(BaseModel):
    success: bool = False
    error: str
    status: int
    timestamp: str


@router.get("/test")
async def test_proxy():
    """프록시 서버 테스트 엔드포인트"""
    return {
        "success": True,
        "message": "InfoMax API 프록시 서버가 정상 작동 중입니다! 🚀",
        "timestamp": datetime.now().isoformat(),
        "base_url": INFOMAX_BASE_URL
    }


@router.get("/bond/market/mn_hist")
async def get_bond_market_hist(
    authorization: str = Header(..., description="Bearer 토큰"),
    stdcd: str = Query("", description="표준코드"),
    market: str = Query("", description="시장구분"),
    startDate: str = Query("", description="시작일자"),
    endDate: str = Query("", description="종료일자"),
    aclassnm: str = Query("", description="대분류"),
    volume: str = Query("", description="거래량"),
    allcrdtrate: str = Query("", description="신용등급"),
    yld: str = Query("", description="거래수익률"),
    estyld: str = Query("", description="민평수익률")
):
    """채권 체결정보 API 프록시"""
    
    start_time = datetime.now()
    
    # 파라미터 구성 (모든 파라미터 포함)
    params = {
        "stdcd": stdcd,
        "market": market,
        "startDate": startDate,
        "endDate": endDate,
        "aclassnm": aclassnm,
        "volume": volume,
        "allcrdtrate": allcrdtrate,
        "yld": yld,
        "estyld": estyld
    }
    
    return await _make_infomax_request(
        endpoint="bond/market/mn_hist",
        params=params,
        authorization=authorization,
        start_time=start_time
    )


@router.get("/bond/marketvaluation")
async def get_bond_marketvaluation(
    authorization: str = Header(..., description="Bearer 토큰"),
    stdcd: str = Query(..., description="표준코드 (필수)"),
    bonddate: str = Query("", description="일자 (선택)")
):
    """채권 시가평가 API 프록시"""
    
    start_time = datetime.now()
    
    params = {
        "stdcd": stdcd,
        "bonddate": bonddate
    }
    
    return await _make_infomax_request(
        endpoint="bond/marketvaluation",
        params=params,
        authorization=authorization,
        start_time=start_time
    )


@router.get("/stock/hist")
async def get_stock_hist(
    authorization: str = Header(..., description="Bearer 토큰"),
    code: str = Query(..., description="종목코드 (필수)"),
    endDate: str = Query("", description="종료일자"),
    startDate: str = Query("", description="시작일자")
):
    """주식 일별정보 API 프록시"""
    
    start_time = datetime.now()
    
    params = {
        "code": code,
        "endDate": endDate,
        "startDate": startDate
    }
    
    # 빈 값 제거 (주식 API는 빈 값 제외)
    params = {k: v for k, v in params.items() if v.strip()}
    
    return await _make_infomax_request(
        endpoint="stock/hist",
        params=params,
        authorization=authorization,
        start_time=start_time
    )


@router.get("/stock/code")
async def get_stock_code(
    authorization: str = Header(..., description="Bearer 토큰"),
    search: str = Query("", description="통합검색"),
    code: str = Query("", description="종목코드 검색"),
    name: str = Query("", description="종목명 검색"),
    isin: str = Query("", description="ISIN코드 검색"),
    market: str = Query("", description="시장 구분"),
    type: str = Query("", description="종목 구분")
):
    """주식 코드검색 API 프록시"""
    
    start_time = datetime.now()
    
    params = {
        "search": search,
        "code": code,
        "name": name,
        "isin": isin,
        "market": market,
        "type": type
    }
    
    return await _make_infomax_request(
        endpoint="stock/code",
        params=params,
        authorization=authorization,
        start_time=start_time
    )


@router.get("/{endpoint_path:path}")
async def generic_infomax_proxy(
    endpoint_path: str,
    authorization: str = Header(..., description="Bearer 토큰"),
    request_params: Dict[str, Any] = None
):
    """범용 InfoMax API 프록시 (다른 모든 API 경로)"""
    
    start_time = datetime.now()
    
    return await _make_infomax_request(
        endpoint=endpoint_path,
        params=request_params or {},
        authorization=authorization,
        start_time=start_time
    )


async def _make_infomax_request(
    endpoint: str,
    params: Dict[str, Any],
    authorization: str,
    start_time: datetime
) -> JSONResponse:
    """InfoMax API 실제 호출 및 응답 처리"""
    
    # Bearer 토큰 처리
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization 헤더는 'Bearer TOKEN' 형식이어야 합니다."
        )
    
    token = authorization.split(" ", 1)[1]
    url = f"{INFOMAX_BASE_URL}/{endpoint}"
    
    # 요청 로그
    logger.info(f"🚀 InfoMax API 호출: {url}")
    logger.info(f"📤 파라미터: {json.dumps(params, ensure_ascii=False)}")
    
    try:
        async with httpx.AsyncClient(verify=False, timeout=REQUEST_TIMEOUT) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "WatchHamster-InfoMax-Proxy/1.0"
            }
            
            response = await client.get(url, params=params, headers=headers)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"📊 응답 상태: {response.status_code} {response.reason_phrase}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"✅ API 호출 성공 ({execution_time:.3f}초)")
                    
                    return JSONResponse(
                        content={
                            "success": True,
                            "data": data,
                            "status": response.status_code,
                            "url": str(response.url),
                            "timestamp": datetime.now().isoformat(),
                            "execution_time": execution_time
                        }
                    )
                except json.JSONDecodeError as e:
                    logger.error(f"📄 JSON 파싱 오류: {e}")
                    raise HTTPException(
                        status_code=502,
                        detail="InfoMax API 응답을 JSON으로 파싱할 수 없습니다."
                    )
            else:
                # 오류 응답 처리
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', f'HTTP {response.status_code}')
                except:
                    error_message = f"HTTP {response.status_code}: {response.reason_phrase}"
                
                logger.error(f"❌ API 호출 실패: {error_message}")
                
                return JSONResponse(
                    status_code=response.status_code,
                    content={
                        "success": False,
                        "error": error_message,
                        "status": response.status_code,
                        "timestamp": datetime.now().isoformat(),
                        "execution_time": execution_time
                    }
                )
                
    except httpx.TimeoutException:
        logger.error("⏰ 요청 시간 초과")
        raise HTTPException(
            status_code=504,
            detail=f"InfoMax API 요청이 {REQUEST_TIMEOUT}초 내에 응답하지 않았습니다."
        )
    except httpx.ConnectError:
        logger.error("🔌 연결 오류")
        raise HTTPException(
            status_code=502,
            detail="InfoMax API 서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요."
        )
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"🔥 예상치 못한 오류: {e}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"서버 내부 오류: {str(e)}",
                "status": 500,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time
            }
        )
