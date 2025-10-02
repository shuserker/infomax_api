"""
실시간 로그 스트리밍을 위한 로그 핸들러
애플리케이션의 모든 로그를 WebSocket을 통해 실시간으로 전송
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Lock
import weakref

class LogStreamHandler(logging.Handler):
    """
    로그를 WebSocket을 통해 실시간으로 스트리밍하는 핸들러
    """
    
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self._stream_managers: List[Any] = []  # WeakSet 대신 리스트 사용
        self._lock = Lock()
        self._buffer: List[Dict[str, Any]] = []
        self._max_buffer_size = 1000
        
    def add_stream_manager(self, manager):
        """스트림 매니저 추가"""
        with self._lock:
            # 약한 참조로 저장하여 메모리 누수 방지
            self._stream_managers.append(weakref.ref(manager))
            # 죽은 참조 정리
            self._stream_managers = [ref for ref in self._stream_managers if ref() is not None]
    
    def remove_stream_manager(self, manager):
        """스트림 매니저 제거"""
        with self._lock:
            self._stream_managers = [
                ref for ref in self._stream_managers 
                if ref() is not None and ref() != manager
            ]
    
    def emit(self, record):
        """로그 레코드를 처리하고 스트림으로 전송"""
        try:
            # 로그 엔트리 생성
            log_entry = self._format_log_entry(record)
            
            # 버퍼에 추가
            with self._lock:
                self._buffer.append(log_entry)
                if len(self._buffer) > self._max_buffer_size:
                    self._buffer.pop(0)
            
            # 활성 스트림 매니저들에게 전송
            self._broadcast_log(log_entry)
            
        except Exception as e:
            # 로그 핸들러에서 예외가 발생하면 무한 루프가 될 수 있으므로 조심스럽게 처리
            print(f"LogStreamHandler 오류: {e}")
    
    def _format_log_entry(self, record: logging.LogRecord) -> Dict[str, Any]:
        """로그 레코드를 딕셔너리로 변환"""
        return {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger_name': record.name,
            'message': record.getMessage(),
            'module': getattr(record, 'module', record.filename) if hasattr(record, 'filename') else None,
            'line_number': getattr(record, 'lineno', None),
            'thread_id': str(record.thread) if hasattr(record, 'thread') else None,
            'process_id': str(record.process) if hasattr(record, 'process') else None,
            'function_name': getattr(record, 'funcName', None),
        }
    
    def _broadcast_log(self, log_entry: Dict[str, Any]):
        """모든 활성 스트림 매니저에게 로그 브로드캐스트"""
        with self._lock:
            active_managers = []
            
            for manager_ref in self._stream_managers:
                manager = manager_ref()
                if manager is not None:
                    active_managers.append(manager)
                    try:
                        # 비동기 브로드캐스트 스케줄링
                        if hasattr(manager, 'schedule_broadcast'):
                            manager.schedule_broadcast(log_entry)
                    except Exception as e:
                        print(f"로그 브로드캐스트 오류: {e}")
            
            # 죽은 참조 정리
            self._stream_managers = [
                weakref.ref(manager) for manager in active_managers
            ]
    
    def get_recent_logs(self, count: int = 50) -> List[Dict[str, Any]]:
        """최근 로그 반환"""
        with self._lock:
            return self._buffer[-count:] if count > 0 else self._buffer.copy()
    
    def clear_buffer(self):
        """버퍼 클리어"""
        with self._lock:
            self._buffer.clear()


class AsyncLogBroadcaster:
    """
    비동기 로그 브로드캐스터
    로그 스트림 매니저와 연동하여 실시간 로그 전송
    """
    
    def __init__(self, stream_manager):
        self.stream_manager = stream_manager
        self.pending_logs: List[Dict[str, Any]] = []
        self.broadcast_lock = asyncio.Lock()
        self.broadcast_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    def schedule_broadcast(self, log_entry: Dict[str, Any]):
        """로그 브로드캐스트 스케줄링"""
        self.pending_logs.append(log_entry)
        
        # 브로드캐스트 태스크가 실행 중이 아니면 시작
        if not self.is_running:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    self.broadcast_task = loop.create_task(self._process_pending_logs())
            except RuntimeError:
                # 이벤트 루프가 없는 경우 무시
                pass
    
    async def _process_pending_logs(self):
        """대기 중인 로그들을 처리"""
        if self.is_running:
            return
        
        self.is_running = True
        
        try:
            async with self.broadcast_lock:
                while self.pending_logs:
                    log_entry = self.pending_logs.pop(0)
                    await self.stream_manager.broadcast_log_entry(log_entry)
                    
                    # CPU 부하 방지를 위한 작은 지연
                    if len(self.pending_logs) > 10:
                        await asyncio.sleep(0.001)
        
        except Exception as e:
            print(f"로그 브로드캐스트 처리 오류: {e}")
        
        finally:
            self.is_running = False


# 전역 로그 스트림 핸들러
_global_log_stream_handler: Optional[LogStreamHandler] = None

def get_log_stream_handler() -> LogStreamHandler:
    """전역 로그 스트림 핸들러 반환"""
    global _global_log_stream_handler
    
    if _global_log_stream_handler is None:
        _global_log_stream_handler = LogStreamHandler()
        
        # 루트 로거에 핸들러 추가
        root_logger = logging.getLogger()
        root_logger.addHandler(_global_log_stream_handler)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        _global_log_stream_handler.setFormatter(formatter)
    
    return _global_log_stream_handler

def setup_log_streaming():
    """로그 스트리밍 설정"""
    handler = get_log_stream_handler()
    
    # 애플리케이션 로거들에 핸들러 추가
    app_loggers = [
        'watchhamster',
        'api',
        'performance',
        'stability',
        'webhook',
        'posco',
        'uvicorn',
        'fastapi',
    ]
    
    for logger_name in app_loggers:
        logger = logging.getLogger(logger_name)
        if handler not in logger.handlers:
            logger.addHandler(handler)
    
    return handler

def add_stream_manager_to_handler(manager):
    """스트림 매니저를 핸들러에 추가"""
    handler = get_log_stream_handler()
    broadcaster = AsyncLogBroadcaster(manager)
    handler.add_stream_manager(broadcaster)
    return broadcaster

def remove_stream_manager_from_handler(broadcaster):
    """스트림 매니저를 핸들러에서 제거"""
    handler = get_log_stream_handler()
    handler.remove_stream_manager(broadcaster)

def get_recent_logs(count: int = 50) -> List[Dict[str, Any]]:
    """최근 로그 반환"""
    handler = get_log_stream_handler()
    return handler.get_recent_logs(count)

def clear_log_buffer():
    """로그 버퍼 클리어"""
    handler = get_log_stream_handler()
    handler.clear_buffer()

# 테스트용 로그 생성 함수
def generate_test_logs():
    """테스트용 로그 생성"""
    import time
    import random
    
    loggers = [
        logging.getLogger('watchhamster.test'),
        logging.getLogger('api.test'),
        logging.getLogger('performance.test'),
    ]
    
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
    messages = [
        "시스템 상태 확인 완료",
        "API 요청 처리 중",
        "성능 메트릭 수집",
        "데이터베이스 연결 확인",
        "캐시 업데이트 완료",
        "웹훅 전송 성공",
        "배포 프로세스 시작",
        "Git 상태 확인",
        "메모리 사용량 체크",
        "네트워크 연결 테스트",
    ]
    
    for i in range(10):
        logger = random.choice(loggers)
        level = random.choice(levels)
        message = f"{random.choice(messages)} #{i+1}"
        
        logger.log(level, message)
        time.sleep(0.1)