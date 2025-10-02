"""
로그 조회 및 스트리밍 API 엔드포인트
실시간 로그 스트리밍 및 로그 파일 관리 기능 제공
"""

import logging
import os
import asyncio
import json
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, Depends, Body
from fastapi.responses import StreamingResponse, FileResponse, Response
from pydantic import BaseModel
import aiofiles
import re

# 로깅 설정
logger = logging.getLogger(__name__)
router = APIRouter()

# 데이터 모델
class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    logger_name: str
    message: str
    module: Optional[str] = None
    line_number: Optional[int] = None
    thread_id: Optional[str] = None

class LogFilter(BaseModel):
    level: Optional[str] = None
    logger_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    search_text: Optional[str] = None

class LogFile(BaseModel):
    name: str
    path: str
    size: int
    modified_time: datetime
    is_active: bool

class LogExportRequest(BaseModel):
    logs: List[LogEntry]
    format: str = "txt"  # txt, json, csv
    include_metadata: bool = True
    custom_filename: Optional[str] = None

class LogRetentionPolicy(BaseModel):
    max_days: int = 30
    max_size_mb: int = 100
    max_files: int = 50
    compression_enabled: bool = True
    auto_cleanup: bool = True
    cleanup_schedule: str = "daily"  # daily, weekly, monthly
    level_based_retention: Dict[str, int] = {
        "DEBUG": 7,
        "INFO": 30,
        "WARN": 90,
        "ERROR": 180,
        "CRITICAL": 365
    }

# 로그 파일 경로 설정
LOG_BASE_PATH = Path("logs")
ACTIVE_LOG_FILES = [
    "watchhamster.log",
    "api.log", 
    "error.log",
    "performance.log",
    "webhook.log"
]

# WebSocket 연결 관리
class LogStreamManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.log_buffer: List[LogEntry] = []
        self.max_buffer_size = 1000
        self.broadcaster = None
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"로그 스트림 연결: {len(self.active_connections)}개 활성 연결")
        
        # 첫 번째 연결 시 로그 스트리밍 설정
        if len(self.active_connections) == 1:
            self._setup_log_streaming()
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"로그 스트림 연결 해제: {len(self.active_connections)}개 활성 연결")
        
        # 마지막 연결 해제 시 스트리밍 정리
        if len(self.active_connections) == 0:
            self._cleanup_log_streaming()
    
    def _setup_log_streaming(self):
        """로그 스트리밍 설정"""
        try:
            from ..utils.log_streamer import add_stream_manager_to_handler
            self.broadcaster = add_stream_manager_to_handler(self)
            logger.info("로그 스트리밍이 설정되었습니다")
        except Exception as e:
            logger.error(f"로그 스트리밍 설정 실패: {e}")
    
    def _cleanup_log_streaming(self):
        """로그 스트리밍 정리"""
        if self.broadcaster:
            try:
                from ..utils.log_streamer import remove_stream_manager_from_handler
                remove_stream_manager_from_handler(self.broadcaster)
                self.broadcaster = None
                logger.info("로그 스트리밍이 정리되었습니다")
            except Exception as e:
                logger.error(f"로그 스트리밍 정리 실패: {e}")
    
    async def broadcast_log_entry(self, log_entry_dict: Dict[str, Any]):
        """로그 엔트리를 모든 연결된 클라이언트에게 브로드캐스트"""
        if not self.active_connections:
            return
        
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(log_entry_dict)
            except Exception as e:
                logger.warning(f"로그 브로드캐스트 실패: {e}")
                disconnected.append(connection)
        
        # 끊어진 연결 정리
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_log(self, log_entry: LogEntry):
        """LogEntry 객체를 브로드캐스트 (기존 호환성)"""
        await self.broadcast_log_entry(log_entry.dict())
    
    def add_to_buffer(self, log_entry: LogEntry):
        """로그 버퍼에 추가"""
        self.log_buffer.append(log_entry)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)
    
    async def send_recent_logs(self, websocket: WebSocket, count: int = 50):
        """최근 로그를 특정 연결에 전송"""
        try:
            from ..utils.log_streamer import get_recent_logs
            recent_logs = get_recent_logs(count)
            
            for log_dict in recent_logs:
                await websocket.send_json(log_dict)
                
        except Exception as e:
            logger.error(f"최근 로그 전송 실패: {e}")

# 전역 로그 스트림 매니저
log_stream_manager = LogStreamManager()

def get_log_stream_manager():
    """로그 스트림 매니저 인스턴스 반환"""
    return log_stream_manager

@router.get("/files", response_model=List[LogFile])
async def get_log_files():
    """사용 가능한 로그 파일 목록 조회"""
    logger.info("로그 파일 목록 조회 요청")
    
    log_files = []
    
    try:
        # 로그 디렉토리 확인
        if not LOG_BASE_PATH.exists():
            LOG_BASE_PATH.mkdir(parents=True, exist_ok=True)
        
        # 로그 파일 스캔
        for log_file in LOG_BASE_PATH.glob("*.log"):
            if log_file.is_file():
                stat = log_file.stat()
                log_files.append(LogFile(
                    name=log_file.name,
                    path=str(log_file),
                    size=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    is_active=log_file.name in ACTIVE_LOG_FILES
                ))
        
        # 활성 로그 파일이 없으면 기본 파일들 생성
        if not log_files:
            for active_file in ACTIVE_LOG_FILES:
                file_path = LOG_BASE_PATH / active_file
                if not file_path.exists():
                    file_path.touch()
                
                stat = file_path.stat()
                log_files.append(LogFile(
                    name=active_file,
                    path=str(file_path),
                    size=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    is_active=True
                ))
        
        # 수정 시간 기준 내림차순 정렬
        log_files.sort(key=lambda x: x.modified_time, reverse=True)
        
        return log_files
        
    except Exception as e:
        logger.error(f"로그 파일 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 파일 목록 조회 중 오류가 발생했습니다")

@router.get("/", response_model=List[LogEntry])
async def get_logs(
    file_name: str = Query("watchhamster.log", description="로그 파일명"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 로그 수"),
    offset: int = Query(0, ge=0, description="건너뛸 로그 수"),
    level: Optional[str] = Query(None, description="로그 레벨 필터"),
    search: Optional[str] = Query(None, description="검색어"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간")
):
    """로그 조회 (페이지네이션 지원)"""
    logger.info(f"로그 조회 요청: {file_name} (limit: {limit}, offset: {offset})")
    
    try:
        log_file_path = LOG_BASE_PATH / file_name
        
        if not log_file_path.exists():
            raise HTTPException(status_code=404, detail=f"로그 파일을 찾을 수 없습니다: {file_name}")
        
        logs = []
        
        # 로그 파일 읽기
        async with aiofiles.open(log_file_path, 'r', encoding='utf-8') as f:
            lines = await f.readlines()
        
        # 로그 파싱 및 필터링
        for line in lines:
            log_entry = _parse_log_line(line.strip())
            if log_entry and _matches_filter(log_entry, level, search, start_time, end_time):
                logs.append(log_entry)
        
        # 최신 로그부터 정렬
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 페이지네이션 적용
        paginated_logs = logs[offset:offset + limit]
        
        return paginated_logs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 조회 중 오류가 발생했습니다")

@router.get("/stream")
async def stream_logs(
    file_name: str = Query("watchhamster.log", description="로그 파일명"),
    level: Optional[str] = Query(None, description="로그 레벨 필터")
):
    """로그 스트리밍 (Server-Sent Events)"""
    logger.info(f"로그 스트리밍 시작: {file_name}")
    
    async def log_generator() -> AsyncGenerator[str, None]:
        log_file_path = LOG_BASE_PATH / file_name
        
        if not log_file_path.exists():
            yield f"data: {json.dumps({'error': f'로그 파일을 찾을 수 없습니다: {file_name}'})}\n\n"
            return
        
        # 파일 끝에서 시작
        try:
            async with aiofiles.open(log_file_path, 'r', encoding='utf-8') as f:
                # 파일 끝으로 이동
                await f.seek(0, 2)
                
                while True:
                    line = await f.readline()
                    if line:
                        log_entry = _parse_log_line(line.strip())
                        if log_entry and (not level or log_entry.level.upper() == level.upper()):
                            yield f"data: {json.dumps(log_entry.dict(), default=str)}\n\n"
                    else:
                        # 새 로그가 없으면 잠시 대기
                        await asyncio.sleep(1)
                        
        except Exception as e:
            logger.error(f"로그 스트리밍 오류: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        log_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.websocket("/ws")
async def websocket_log_stream(websocket: WebSocket, 
                              file_name: str = "watchhamster.log",
                              level: Optional[str] = None):
    """WebSocket을 통한 실시간 로그 스트리밍"""
    stream_manager = get_log_stream_manager()
    await stream_manager.connect(websocket)
    
    try:
        # 최근 로그 전송
        await stream_manager.send_recent_logs(websocket, 50)
        
        # 연결 유지 및 새 로그 대기
        while True:
            try:
                # 클라이언트로부터 메시지 수신 (연결 유지용)
                message = await websocket.receive_text()
                
                # 핑-퐁 처리
                if message == "ping":
                    await websocket.send_text("pong")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.warning(f"WebSocket 오류: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        stream_manager.disconnect(websocket)

@router.get("/download/{file_name}")
async def download_log_file(file_name: str):
    """로그 파일 다운로드"""
    logger.info(f"로그 파일 다운로드 요청: {file_name}")
    
    log_file_path = LOG_BASE_PATH / file_name
    
    if not log_file_path.exists():
        raise HTTPException(status_code=404, detail=f"로그 파일을 찾을 수 없습니다: {file_name}")
    
    return FileResponse(
        path=log_file_path,
        filename=file_name,
        media_type='text/plain'
    )

@router.delete("/{file_name}")
async def clear_log_file(file_name: str):
    """로그 파일 내용 삭제"""
    logger.info(f"로그 파일 삭제 요청: {file_name}")
    
    log_file_path = LOG_BASE_PATH / file_name
    
    if not log_file_path.exists():
        raise HTTPException(status_code=404, detail=f"로그 파일을 찾을 수 없습니다: {file_name}")
    
    try:
        # 파일 내용만 삭제 (파일은 유지)
        async with aiofiles.open(log_file_path, 'w', encoding='utf-8') as f:
            await f.write("")
        
        return {"message": f"로그 파일 '{file_name}'의 내용이 삭제되었습니다"}
        
    except Exception as e:
        logger.error(f"로그 파일 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 파일 삭제 중 오류가 발생했습니다")

@router.get("/search")
async def search_logs(
    query: str = Query(..., description="검색어"),
    file_name: str = Query("watchhamster.log", description="로그 파일명"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 로그 수"),
    case_sensitive: bool = Query(False, description="대소문자 구분")
):
    """로그 검색"""
    logger.info(f"로그 검색 요청: '{query}' in {file_name}")
    
    try:
        log_file_path = LOG_BASE_PATH / file_name
        
        if not log_file_path.exists():
            raise HTTPException(status_code=404, detail=f"로그 파일을 찾을 수 없습니다: {file_name}")
        
        matching_logs = []
        search_pattern = re.compile(query if case_sensitive else query, re.IGNORECASE if not case_sensitive else 0)
        
        # 로그 파일 읽기 및 검색
        async with aiofiles.open(log_file_path, 'r', encoding='utf-8') as f:
            lines = await f.readlines()
        
        for line in lines:
            if search_pattern.search(line):
                log_entry = _parse_log_line(line.strip())
                if log_entry:
                    matching_logs.append(log_entry)
                    
                    if len(matching_logs) >= limit:
                        break
        
        # 최신 로그부터 정렬
        matching_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return {
            "query": query,
            "file_name": file_name,
            "total_matches": len(matching_logs),
            "logs": matching_logs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그 검색 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 검색 중 오류가 발생했습니다")

@router.get("/statistics")
async def get_log_statistics(
    file_name: str = Query("watchhamster.log", description="로그 파일명"),
    hours: int = Query(24, ge=1, le=168, description="통계 기간 (시간)")
):
    """로그 통계 조회"""
    logger.info(f"로그 통계 조회 요청: {file_name} (최근 {hours}시간)")
    
    try:
        log_file_path = LOG_BASE_PATH / file_name
        
        if not log_file_path.exists():
            raise HTTPException(status_code=404, detail=f"로그 파일을 찾을 수 없습니다: {file_name}")
        
        # 통계 데이터 초기화
        stats = {
            "total_logs": 0,
            "level_counts": {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0},
            "hourly_counts": {},
            "top_loggers": {},
            "error_messages": []
        }
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 로그 파일 읽기 및 분석
        async with aiofiles.open(log_file_path, 'r', encoding='utf-8') as f:
            lines = await f.readlines()
        
        for line in lines:
            log_entry = _parse_log_line(line.strip())
            if log_entry and log_entry.timestamp >= cutoff_time:
                stats["total_logs"] += 1
                
                # 레벨별 카운트
                if log_entry.level in stats["level_counts"]:
                    stats["level_counts"][log_entry.level] += 1
                
                # 시간별 카운트
                hour_key = log_entry.timestamp.strftime("%Y-%m-%d %H:00")
                stats["hourly_counts"][hour_key] = stats["hourly_counts"].get(hour_key, 0) + 1
                
                # 로거별 카운트
                stats["top_loggers"][log_entry.logger_name] = stats["top_loggers"].get(log_entry.logger_name, 0) + 1
                
                # 에러 메시지 수집
                if log_entry.level in ["ERROR", "CRITICAL"]:
                    stats["error_messages"].append({
                        "timestamp": log_entry.timestamp,
                        "level": log_entry.level,
                        "message": log_entry.message[:200]  # 처음 200자만
                    })
        
        # 상위 로거 정렬
        stats["top_loggers"] = dict(sorted(stats["top_loggers"].items(), key=lambda x: x[1], reverse=True)[:10])
        
        # 최근 에러 메시지만 유지
        stats["error_messages"] = sorted(stats["error_messages"], key=lambda x: x["timestamp"], reverse=True)[:20]
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 통계 조회 중 오류가 발생했습니다")

@router.post("/export")
async def export_logs(export_request: LogExportRequest):
    """로그 내보내기"""
    logger.info(f"로그 내보내기 요청: {len(export_request.logs)}개 로그, 형식: {export_request.format}")
    
    try:
        # 파일명 생성
        if export_request.custom_filename:
            filename = f"{export_request.custom_filename}.{export_request.format}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"watchhamster_logs_{timestamp}.{export_request.format}"
        
        # 형식에 따른 데이터 생성
        if export_request.format == "json":
            content = _format_logs_as_json(export_request.logs, export_request.include_metadata)
            media_type = "application/json"
        elif export_request.format == "csv":
            content = _format_logs_as_csv(export_request.logs)
            media_type = "text/csv"
        else:  # txt
            content = _format_logs_as_txt(export_request.logs)
            media_type = "text/plain"
        
        # 응답 생성
        response = Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(content.encode('utf-8')))
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"로그 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 내보내기 중 오류가 발생했습니다")

@router.get("/retention-policy")
async def get_retention_policy():
    """로그 보관 정책 조회"""
    logger.info("로그 보관 정책 조회 요청")
    
    try:
        # 설정 파일에서 정책 로드 (실제 구현에서는 데이터베이스나 설정 파일 사용)
        policy_file = LOG_BASE_PATH / "retention_policy.json"
        
        if policy_file.exists():
            async with aiofiles.open(policy_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                policy_data = json.loads(content)
                return LogRetentionPolicy(**policy_data)
        else:
            # 기본 정책 반환
            return LogRetentionPolicy()
            
    except Exception as e:
        logger.error(f"로그 보관 정책 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 보관 정책 조회 중 오류가 발생했습니다")

@router.post("/retention-policy")
async def save_retention_policy(policy: LogRetentionPolicy):
    """로그 보관 정책 저장"""
    logger.info("로그 보관 정책 저장 요청")
    
    try:
        # 정책 유효성 검사
        if policy.max_days < 1:
            raise HTTPException(status_code=400, detail="최대 보관 일수는 1일 이상이어야 합니다")
        
        if policy.max_size_mb < 1:
            raise HTTPException(status_code=400, detail="최대 파일 크기는 1MB 이상이어야 합니다")
        
        if policy.max_files < 1:
            raise HTTPException(status_code=400, detail="최대 파일 수는 1개 이상이어야 합니다")
        
        # 정책 저장
        policy_file = LOG_BASE_PATH / "retention_policy.json"
        
        async with aiofiles.open(policy_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(policy.dict(), indent=2, default=str))
        
        # 자동 정리가 활성화된 경우 스케줄 설정 (실제 구현에서는 백그라운드 태스크 사용)
        if policy.auto_cleanup:
            logger.info(f"자동 정리 스케줄 설정: {policy.cleanup_schedule}")
            # TODO: 백그라운드 태스크로 자동 정리 스케줄 설정
        
        return {"message": "로그 보관 정책이 성공적으로 저장되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그 보관 정책 저장 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 보관 정책 저장 중 오류가 발생했습니다")

@router.post("/cleanup")
async def cleanup_logs():
    """로그 정리 실행"""
    logger.info("로그 정리 실행 요청")
    
    try:
        # 보관 정책 로드
        policy_file = LOG_BASE_PATH / "retention_policy.json"
        
        if policy_file.exists():
            async with aiofiles.open(policy_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                policy_data = json.loads(content)
                policy = LogRetentionPolicy(**policy_data)
        else:
            policy = LogRetentionPolicy()
        
        cleanup_results = {
            "deleted_files": [],
            "compressed_files": [],
            "total_space_freed": 0
        }
        
        cutoff_date = datetime.now() - timedelta(days=policy.max_days)
        
        # 로그 파일 정리
        for log_file in LOG_BASE_PATH.glob("*.log*"):
            if log_file.is_file():
                stat = log_file.stat()
                file_date = datetime.fromtimestamp(stat.st_mtime)
                
                # 오래된 파일 삭제
                if file_date < cutoff_date and log_file.name not in ACTIVE_LOG_FILES:
                    file_size = stat.st_size
                    log_file.unlink()
                    cleanup_results["deleted_files"].append(log_file.name)
                    cleanup_results["total_space_freed"] += file_size
                    logger.info(f"오래된 로그 파일 삭제: {log_file.name}")
                
                # 큰 파일 압축 (실제 구현에서는 gzip 등 사용)
                elif stat.st_size > policy.max_size_mb * 1024 * 1024 and policy.compression_enabled:
                    # TODO: 파일 압축 구현
                    cleanup_results["compressed_files"].append(log_file.name)
                    logger.info(f"로그 파일 압축 대상: {log_file.name}")
        
        # 파일 수 제한 적용
        log_files = sorted(
            [f for f in LOG_BASE_PATH.glob("*.log") if f.name not in ACTIVE_LOG_FILES],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(log_files) > policy.max_files:
            files_to_delete = log_files[policy.max_files:]
            for file_to_delete in files_to_delete:
                file_size = file_to_delete.stat().st_size
                file_to_delete.unlink()
                cleanup_results["deleted_files"].append(file_to_delete.name)
                cleanup_results["total_space_freed"] += file_size
                logger.info(f"파일 수 제한으로 삭제: {file_to_delete.name}")
        
        cleanup_results["total_space_freed_mb"] = cleanup_results["total_space_freed"] / (1024 * 1024)
        
        return cleanup_results
        
    except Exception as e:
        logger.error(f"로그 정리 실패: {e}")
        raise HTTPException(status_code=500, detail="로그 정리 중 오류가 발생했습니다")

@router.get("/export-formats")
async def get_export_formats():
    """지원하는 내보내기 형식 목록"""
    return {
        "formats": [
            {
                "id": "txt",
                "name": "텍스트 파일",
                "extension": "txt",
                "description": "사람이 읽기 쉬운 텍스트 형식"
            },
            {
                "id": "json",
                "name": "JSON 파일",
                "extension": "json",
                "description": "구조화된 JSON 형식 (메타데이터 포함 가능)"
            },
            {
                "id": "csv",
                "name": "CSV 파일",
                "extension": "csv",
                "description": "스프레드시트에서 열 수 있는 CSV 형식"
            }
        ]
    }

# 헬퍼 함수들
def _parse_log_line(line: str) -> Optional[LogEntry]:
    """로그 라인을 파싱하여 LogEntry 객체로 변환"""
    if not line.strip():
        return None
    
    try:
        # 기본 로그 포맷: 2024-01-01 12:00:00,123 - logger_name - LEVEL - message
        # 정규식을 사용한 파싱
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d{3}) - ([^-]+) - (\w+) - (.+)'
        match = re.match(pattern, line)
        
        if match:
            timestamp_str = f"{match.group(1)}.{match.group(2)}"
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
            
            return LogEntry(
                timestamp=timestamp,
                level=match.group(4).strip(),
                logger_name=match.group(3).strip(),
                message=match.group(5).strip()
            )
        else:
            # 파싱 실패 시 기본 엔트리 생성
            return LogEntry(
                timestamp=datetime.now(),
                level="INFO",
                logger_name="unknown",
                message=line
            )
            
    except Exception as e:
        logger.warning(f"로그 라인 파싱 실패: {e}")
        return None

def _matches_filter(log_entry: LogEntry, level: Optional[str], search: Optional[str], 
                   start_time: Optional[datetime], end_time: Optional[datetime]) -> bool:
    """로그 엔트리가 필터 조건에 맞는지 확인"""
    
    # 레벨 필터
    if level and log_entry.level.upper() != level.upper():
        return False
    
    # 검색어 필터
    if search and search.lower() not in log_entry.message.lower():
        return False
    
    # 시간 범위 필터
    if start_time and log_entry.timestamp < start_time:
        return False
    
    if end_time and log_entry.timestamp > end_time:
        return False
    
    return True

# 로그 포맷팅 헬퍼 함수들
def _format_logs_as_txt(logs: List[LogEntry]) -> str:
    """로그를 텍스트 형식으로 포맷팅"""
    lines = []
    for log in logs:
        timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f"{timestamp} {log.level.ljust(8)} [{log.logger_name}] {log.message}"
        lines.append(line)
    return "\n".join(lines)

def _format_logs_as_json(logs: List[LogEntry], include_metadata: bool = True) -> str:
    """로그를 JSON 형식으로 포맷팅"""
    log_data = [log.dict() for log in logs]
    
    if include_metadata:
        metadata = {
            "exported_at": datetime.now().isoformat(),
            "total_logs": len(logs),
            "exported_by": "WatchHamster Tauri Backend",
            "version": "1.0.0"
        }
        
        if logs:
            metadata["time_range"] = {
                "start": min(log.timestamp for log in logs).isoformat(),
                "end": max(log.timestamp for log in logs).isoformat()
            }
            
            # 레벨별 통계
            level_counts = {}
            for log in logs:
                level_counts[log.level] = level_counts.get(log.level, 0) + 1
            metadata["level_distribution"] = level_counts
        
        return json.dumps({
            "metadata": metadata,
            "logs": log_data
        }, indent=2, default=str)
    else:
        return json.dumps(log_data, indent=2, default=str)

def _format_logs_as_csv(logs: List[LogEntry]) -> str:
    """로그를 CSV 형식으로 포맷팅"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 헤더 작성
    writer.writerow(["Timestamp", "Level", "Logger", "Message", "Module", "Line"])
    
    # 데이터 작성
    for log in logs:
        writer.writerow([
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            log.level,
            log.logger_name,
            log.message,
            log.module or "",
            log.line_number or ""
        ])
    
    return output.getvalue()

# 로그 스트림 매니저에 새 로그 추가하는 함수 (다른 모듈에서 호출)
async def add_log_to_stream(level: str, logger_name: str, message: str, 
                           module: Optional[str] = None, line_number: Optional[int] = None):
    """새 로그를 스트림에 추가"""
    log_entry = LogEntry(
        timestamp=datetime.now(),
        level=level,
        logger_name=logger_name,
        message=message,
        module=module,
        line_number=line_number
    )
    
    # 버퍼에 추가
    log_stream_manager.add_to_buffer(log_entry)
    
    # 연결된 클라이언트들에게 브로드캐스트
    await log_stream_manager.broadcast_log(log_entry)