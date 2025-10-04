"""
미들웨어 유틸리티
"""

import time
from typing import Callable
from fastapi import Request, Response
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    # FastAPI 0.104.1에서는 다른 경로에 있을 수 있음
    from starlette.middleware.base import BaseHTTPMiddleware

from .logger import get_logger

logger = get_logger(__name__)

class TimingMiddleware(BaseHTTPMiddleware):
    """요청 처리 시간 측정 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 요청 처리
        response = await call_next(request)
        
        # 처리 시간 계산
        process_time = time.time() - start_time
        
        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)
        
        # 느린 요청 로깅 (1초 이상)
        if process_time > 1.0:
            logger.warning(
                f"느린 요청 감지: {request.method} {request.url} - "
                f"처리시간: {process_time:.3f}초"
            )
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 추가 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS 헤더 (HTTPS에서만)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """요청 로깅 미들웨어"""
    
    def __init__(self, app, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 요청 정보 로깅
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            f"요청: {request.method} {request.url} - "
            f"클라이언트: {client_ip} - "
            f"User-Agent: {user_agent}"
        )
        
        # 요청 본문 로깅 (개발 모드에서만)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    logger.debug(f"요청 본문: {body.decode('utf-8')[:500]}...")
            except Exception as e:
                logger.warning(f"요청 본문 로깅 실패: {e}")
        
        # 응답 처리
        response = await call_next(request)
        
        # 응답 로깅
        logger.info(
            f"응답: {request.method} {request.url} - "
            f"상태: {response.status_code}"
        )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """간단한 레이트 리미팅 미들웨어"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 클라이언트별 요청 기록 관리
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # 오래된 요청 기록 제거
        self.clients[client_ip] = [
            req_time for req_time in self.clients[client_ip]
            if current_time - req_time < self.period
        ]
        
        # 레이트 리미트 체크
        if len(self.clients[client_ip]) >= self.calls:
            logger.warning(f"레이트 리미트 초과: {client_ip}")
            return Response(
                content="Too Many Requests",
                status_code=429,
                headers={"Retry-After": str(self.period)}
            )
        
        # 현재 요청 기록
        self.clients[client_ip].append(current_time)
        
        return await call_next(request)