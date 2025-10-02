#!/usr/bin/env python3
"""
WatchHamster Tauri 백엔드 서비스
FastAPI 기반 REST API 및 WebSocket 서버
"""

import asyncio
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# 설정 및 로깅 유틸리티 임포트
from utils.config import get_settings
from utils.logger import get_logger
from utils.middleware import (
    TimingMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)

# 설정 로드
settings = get_settings()
logger = get_logger(__name__)

# 백그라운드 태스크 관리
background_tasks = set()

# 애플리케이션 라이프사이클 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시 실행
    logger.info("WatchHamster 백엔드 서비스 시작")
    logger.info(f"서비스 포트: {settings.api_port}")
    logger.info(f"API 문서: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info(f"디버그 모드: {settings.debug}")
    
    # 기존 시스템과의 호환성 체크
    await check_legacy_compatibility()
    
    # WebSocket 백그라운드 태스크 시작
    await start_background_tasks()
    
    yield
    
    # 종료 시 실행
    logger.info("WatchHamster 백엔드 서비스 종료")
    await stop_background_tasks()
    await cleanup_resources()

# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    description="""
    ## POSCO WatchHamster 시스템의 현대적인 백엔드 API 서비스
    
    기존 Tkinter 기반 GUI를 현대적인 Tauri + React 환경으로 업그레이드하기 위한 백엔드 서비스입니다.
    
    ### 주요 기능
    - 🔧 **서비스 관리**: POSCO 뉴스, GitHub Pages, 캐시 모니터 등 서비스 제어
    - 📊 **실시간 모니터링**: 시스템 메트릭 및 성능 데이터 실시간 수집
    - 🔔 **웹훅 시스템**: Discord/Slack 알림 및 메시지 템플릿 관리
    - 📝 **로그 관리**: 실시간 로그 스트리밍 및 검색 기능
    - 🚀 **POSCO 시스템**: 배포, 브랜치 전환, Git 관리 기능
    - 🌐 **WebSocket**: 실시간 양방향 통신 지원
    
    ### 기술 스택
    - **FastAPI**: 고성능 비동기 웹 프레임워크
    - **WebSocket**: 실시간 데이터 통신
    - **Pydantic**: 데이터 검증 및 직렬화
    - **Uvicorn**: ASGI 서버
    
    ### 인증 및 보안
    현재 버전은 개발 환경용으로 인증이 비활성화되어 있습니다.
    프로덕션 환경에서는 적절한 인증 메커니즘을 구현해야 합니다.
    
    ### 지원 및 문의
    - **개발팀**: POSCO WatchHamster 개발팀
    - **버전**: v1.0.0
    - **문서**: [API 참조 문서](/docs)
    """,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
    contact={
        "name": "POSCO WatchHamster 개발팀",
        "email": "watchhamster@posco.com",
    },
    license_info={
        "name": "POSCO Internal License",
        "url": "https://posco.com/license",
    },
    servers=[
        {
            "url": f"http://{settings.api_host}:{settings.api_port}",
            "description": "개발 서버"
        },
        {
            "url": "http://localhost:8000",
            "description": "로컬 개발 서버"
        }
    ],
    openapi_tags=[
        {
            "name": "services",
            "description": "서비스 관리 API - POSCO 시스템 서비스들의 시작/중지/재시작 제어"
        },
        {
            "name": "metrics",
            "description": "시스템 메트릭 API - CPU, 메모리, 디스크, 네트워크 상태 모니터링"
        },
        {
            "name": "webhooks",
            "description": "웹훅 관리 API - Discord/Slack 알림 전송 및 템플릿 관리"
        },
        {
            "name": "websocket",
            "description": "WebSocket API - 실시간 양방향 통신 및 상태 업데이트"
        },
        {
            "name": "posco",
            "description": "POSCO 시스템 API - 배포, 브랜치 전환, Git 관리 기능"
        },
        {
            "name": "logs",
            "description": "로그 관리 API - 실시간 로그 스트리밍, 검색, 다운로드 기능"
        }
    ]
)

# 보안 미들웨어 설정
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 커스텀 미들웨어 추가
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TimingMiddleware)

# 개발 모드에서만 요청 로깅 활성화
if settings.debug:
    app.add_middleware(RequestLoggingMiddleware, log_body=True)

# API 라우터 임포트 및 등록
try:
    from api.services import router as services_router
    from api.metrics import router as metrics_router
    from api.webhooks import router as webhooks_router
    from api.websocket import router as websocket_router
    from api.posco import router as posco_router
    from api.logs import router as logs_router
    
    app.include_router(services_router, prefix="/api/services", tags=["services"])
    app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])
    app.include_router(webhooks_router, prefix="/api/webhooks", tags=["webhooks"])
    app.include_router(websocket_router, prefix="/ws", tags=["websocket"])
    app.include_router(posco_router, prefix="/api/posco", tags=["posco"])
    app.include_router(logs_router, prefix="/api/logs", tags=["logs"])
    
    logger.info("모든 API 라우터가 성공적으로 등록되었습니다")
except ImportError as e:
    logger.warning(f"일부 API 라우터 임포트 실패: {e}")

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": "WatchHamster Backend",
        "version": "1.0.0"
    }

# 루트 엔드포인트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "WatchHamster Backend API 서비스가 실행 중입니다",
        "docs": "/docs",
        "health": "/health"
    }



# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리기"""
    logger.error(f"전역 예외 발생: {exc}", exc_info=True)
    
    # 개발 모드에서는 상세 오류 정보 제공
    error_detail = {
        "detail": "내부 서버 오류가 발생했습니다",
        "path": str(request.url),
        "method": request.method
    }
    
    if settings.debug:
        error_detail["error"] = str(exc)
        error_detail["type"] = type(exc).__name__
    
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 처리기"""
    logger.warning(f"HTTP 예외: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

async def check_legacy_compatibility():
    """기존 시스템과의 호환성 체크"""
    try:
        # 기존 설정 파일 경로 확인
        legacy_path = Path(settings.legacy_config_path)
        if legacy_path.exists():
            logger.info(f"기존 설정 디렉토리 발견: {legacy_path}")
        else:
            logger.warning(f"기존 설정 디렉토리를 찾을 수 없습니다: {legacy_path}")
        
        # 필요한 디렉토리 생성
        log_dir = Path(settings.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("호환성 체크 완료")
        
    except Exception as e:
        logger.error(f"호환성 체크 중 오류: {e}")

async def start_background_tasks():
    """백그라운드 태스크 시작"""
    try:
        # 로그 스트리밍 설정
        from utils.log_streamer import setup_log_streaming
        setup_log_streaming()
        logger.info("로그 스트리밍이 설정되었습니다")
        
        from api.websocket import periodic_status_broadcast, monitor_connection_health
        
        # WebSocket 주기적 상태 브로드캐스트 태스크 시작
        status_task = asyncio.create_task(periodic_status_broadcast())
        background_tasks.add(status_task)
        status_task.add_done_callback(background_tasks.discard)
        
        # WebSocket 연결 상태 모니터링 태스크 시작
        health_task = asyncio.create_task(monitor_connection_health())
        background_tasks.add(health_task)
        health_task.add_done_callback(background_tasks.discard)
        
        logger.info("WebSocket 백그라운드 태스크가 시작되었습니다")
        logger.info(f"활성 백그라운드 태스크 수: {len(background_tasks)}")
        
    except Exception as e:
        logger.error(f"백그라운드 태스크 시작 중 오류: {e}")

async def stop_background_tasks():
    """백그라운드 태스크 중지"""
    try:
        # 모든 백그라운드 태스크 취소
        for task in background_tasks:
            if not task.done():
                task.cancel()
        
        # 태스크 완료 대기
        if background_tasks:
            await asyncio.gather(*background_tasks, return_exceptions=True)
        
        logger.info("모든 백그라운드 태스크가 중지되었습니다")
        
    except Exception as e:
        logger.error(f"백그라운드 태스크 중지 중 오류: {e}")

async def cleanup_resources():
    """리소스 정리"""
    try:
        # WebSocket 연결 정리
        from api.websocket import manager
        
        # 모든 WebSocket 연결 종료
        for connection in manager.active_connections.copy():
            try:
                await connection.close()
            except Exception:
                pass
        
        manager.active_connections.clear()
        manager.client_info.clear()
        
        # 임시 파일 정리 등
        logger.info("리소스 정리 완료")
        
    except Exception as e:
        logger.error(f"리소스 정리 중 오류: {e}")

def main():
    """메인 함수"""
    try:
        logger.info("WatchHamster 백엔드 서비스를 시작합니다...")
        
        # 명령행 인수 처리
        debug_mode = "--debug" in sys.argv or "--dev" in sys.argv or settings.debug
        reload_mode = "--reload" in sys.argv or debug_mode
        
        # 서버 설정
        server_config = {
            "app": "main:app",
            "host": settings.api_host,
            "port": settings.api_port,
            "reload": reload_mode,
            "log_level": settings.log_level.lower(),
            "access_log": True,
            "server_header": False,  # 보안을 위해 서버 헤더 숨김
            "date_header": False     # 날짜 헤더 숨김
        }
        
        # 개발 모드에서만 자동 리로드 활성화
        if not debug_mode:
            server_config["workers"] = 1
        
        logger.info(f"서버 설정: {server_config}")
        
        # 서버 실행
        uvicorn.run(**server_config)
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 서비스가 중단되었습니다")
    except Exception as e:
        logger.error(f"서비스 시작 중 오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()