"""
API 헬스체크 프록시 라우터
외부 API 호출을 프록시하여 CORS 문제 해결
"""

import asyncio
import aiohttp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class HealthCheckRequest(BaseModel):
    """헬스체크 요청 모델"""
    url: str
    method: str = "GET"
    params: Dict[str, str] = {}
    headers: Dict[str, str] = {}
    timeout: int = 5

class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    success: bool
    statusCode: int
    data: Optional[dict] = None
    error: Optional[str] = None
    responseTime: float

@router.post("/", response_model=HealthCheckResponse)
async def check_api_health(request: HealthCheckRequest):
    """
    외부 API 헬스체크를 프록시를 통해 수행
    
    Args:
        request: 헬스체크 요청 정보
        
    Returns:
        HealthCheckResponse: 헬스체크 결과
    """
    import time
    start_time = time.time()
    
    try:
        # SSL 인증 무시 설정 (InfoMax API는 자체 서명 인증서 사용)
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=request.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 쿼리 파라미터 준비
            params = {k: v for k, v in request.params.items() if v is not None}
            
            # 헤더 준비 (빈 Authorization 헤더 제거)
            headers = {k: v for k, v in request.headers.items() if v.strip()}
            
            # API 호출
            async with session.request(
                method=request.method,
                url=request.url,
                params=params,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                
                # 응답 상태에 따른 처리
                if response.status == 200:
                    try:
                        # JSON 응답 시도
                        data = await response.json()
                        
                        # InfoMax API 응답 패턴 확인
                        if isinstance(data, dict):
                            if data.get('success') == True or data.get('data') or data.get('results'):
                                return HealthCheckResponse(
                                    success=True,
                                    statusCode=response.status,
                                    data=data,
                                    responseTime=response_time
                                )
                        
                        # 데이터는 있지만 의심스러운 경우
                        return HealthCheckResponse(
                            success=False,
                            statusCode=response.status,
                            data=data,
                            responseTime=response_time,
                            error="Response format suspicious"
                        )
                        
                    except Exception:
                        # JSON 파싱 실패 시 텍스트 응답
                        text = await response.text()
                        return HealthCheckResponse(
                            success=bool(text.strip()),
                            statusCode=response.status,
                            responseTime=response_time,
                            error="Non-JSON response" if not text.strip() else None
                        )
                else:
                    # HTTP 에러 상태
                    try:
                        error_data = await response.json()
                    except:
                        error_data = await response.text()
                    
                    return HealthCheckResponse(
                        success=False,
                        statusCode=response.status,
                        data=error_data if isinstance(error_data, dict) else None,
                        responseTime=response_time,
                        error=f"HTTP {response.status}: {str(error_data)[:200]}"
                    )
                    
    except asyncio.TimeoutError:
        return HealthCheckResponse(
            success=False,
            statusCode=408,
            responseTime=time.time() - start_time,
            error="Request timeout"
        )
        
    except aiohttp.ClientError as e:
        return HealthCheckResponse(
            success=False,
            statusCode=503,
            responseTime=time.time() - start_time,
            error=f"Network error: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Health check error for {request.url}: {e}")
        return HealthCheckResponse(
            success=False,
            statusCode=500,
            responseTime=time.time() - start_time,
            error=f"Internal error: {str(e)}"
        )
