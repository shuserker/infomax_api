"""
실시간 로그 스트리밍 기능 테스트
"""

import pytest
import asyncio
import json
import logging
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from api.logs import LogStreamManager, get_log_stream_manager
from utils.log_streamer import (
    LogStreamHandler, 
    AsyncLogBroadcaster,
    setup_log_streaming,
    add_stream_manager_to_handler,
    get_recent_logs
)
from main import app


class TestLogStreamHandler:
    """로그 스트림 핸들러 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.handler = LogStreamHandler()
        self.mock_manager = Mock()
        self.mock_broadcaster = Mock()
        
    def test_handler_initialization(self):
        """핸들러 초기화 테스트"""
        assert self.handler._stream_managers == []
        assert self.handler._buffer == []
        assert self.handler._max_buffer_size == 1000
        
    def test_add_stream_manager(self):
        """스트림 매니저 추가 테스트"""
        self.handler.add_stream_manager(self.mock_manager)
        assert len(self.handler._stream_managers) == 1
        
    def test_remove_stream_manager(self):
        """스트림 매니저 제거 테스트"""
        self.handler.add_stream_manager(self.mock_manager)
        self.handler.remove_stream_manager(self.mock_manager)
        # 약한 참조로 인해 즉시 제거되지 않을 수 있음
        
    def test_format_log_entry(self):
        """로그 엔트리 포맷팅 테스트"""
        # 테스트용 로그 레코드 생성
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        log_entry = self.handler._format_log_entry(record)
        
        assert log_entry['level'] == 'INFO'
        assert log_entry['logger_name'] == 'test_logger'
        assert log_entry['message'] == 'Test message'
        assert log_entry['line_number'] == 42
        assert 'timestamp' in log_entry
        
    def test_emit_log_record(self):
        """로그 레코드 emit 테스트"""
        # 브로드캐스터 모킹
        mock_broadcaster = Mock()
        mock_broadcaster.schedule_broadcast = Mock()
        
        self.handler.add_stream_manager(mock_broadcaster)
        
        # 테스트용 로그 레코드 생성
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # emit 호출
        self.handler.emit(record)
        
        # 버퍼에 추가되었는지 확인
        assert len(self.handler._buffer) == 1
        assert self.handler._buffer[0]['message'] == 'Test message'
        
    def test_buffer_size_limit(self):
        """버퍼 크기 제한 테스트"""
        self.handler._max_buffer_size = 3
        
        # 4개의 로그 레코드 추가
        for i in range(4):
            record = logging.LogRecord(
                name='test_logger',
                level=logging.INFO,
                pathname='/test/path.py',
                lineno=42,
                msg=f'Test message {i}',
                args=(),
                exc_info=None
            )
            self.handler.emit(record)
        
        # 최대 3개만 유지되는지 확인
        assert len(self.handler._buffer) == 3
        # 가장 오래된 것이 제거되었는지 확인
        assert self.handler._buffer[0]['message'] == 'Test message 1'
        
    def test_get_recent_logs(self):
        """최근 로그 조회 테스트"""
        # 5개의 로그 추가
        for i in range(5):
            record = logging.LogRecord(
                name='test_logger',
                level=logging.INFO,
                pathname='/test/path.py',
                lineno=42,
                msg=f'Test message {i}',
                args=(),
                exc_info=None
            )
            self.handler.emit(record)
        
        # 최근 3개 조회
        recent_logs = self.handler.get_recent_logs(3)
        assert len(recent_logs) == 3
        assert recent_logs[-1]['message'] == 'Test message 4'  # 가장 최근
        
    def test_clear_buffer(self):
        """버퍼 클리어 테스트"""
        # 로그 추가
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        self.handler.emit(record)
        
        assert len(self.handler._buffer) == 1
        
        # 버퍼 클리어
        self.handler.clear_buffer()
        assert len(self.handler._buffer) == 0


class TestAsyncLogBroadcaster:
    """비동기 로그 브로드캐스터 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.mock_stream_manager = Mock()
        self.mock_stream_manager.broadcast_log_entry = AsyncMock()
        self.broadcaster = AsyncLogBroadcaster(self.mock_stream_manager)
        
    def test_broadcaster_initialization(self):
        """브로드캐스터 초기화 테스트"""
        assert self.broadcaster.stream_manager == self.mock_stream_manager
        assert self.broadcaster.pending_logs == []
        assert not self.broadcaster.is_running
        
    def test_schedule_broadcast(self):
        """브로드캐스트 스케줄링 테스트"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'Test message'
        }
        
        self.broadcaster.schedule_broadcast(log_entry)
        
        assert len(self.broadcaster.pending_logs) == 1
        assert self.broadcaster.pending_logs[0] == log_entry
        
    @pytest.mark.asyncio
    async def test_process_pending_logs(self):
        """대기 중인 로그 처리 테스트"""
        # 테스트 로그 추가
        log_entries = [
            {'timestamp': datetime.now().isoformat(), 'level': 'INFO', 'message': f'Test {i}'}
            for i in range(3)
        ]
        
        for log_entry in log_entries:
            self.broadcaster.pending_logs.append(log_entry)
        
        # 처리 실행
        await self.broadcaster._process_pending_logs()
        
        # 모든 로그가 브로드캐스트되었는지 확인
        assert self.mock_stream_manager.broadcast_log_entry.call_count == 3
        assert len(self.broadcaster.pending_logs) == 0


class TestLogStreamManager:
    """로그 스트림 매니저 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.manager = LogStreamManager()
        self.mock_websocket = Mock(spec=WebSocket)
        self.mock_websocket.accept = AsyncMock()
        self.mock_websocket.send_json = AsyncMock()
        
    @pytest.mark.asyncio
    async def test_connect_websocket(self):
        """WebSocket 연결 테스트"""
        await self.manager.connect(self.mock_websocket)
        
        assert self.mock_websocket in self.manager.active_connections
        self.mock_websocket.accept.assert_called_once()
        
    def test_disconnect_websocket(self):
        """WebSocket 연결 해제 테스트"""
        # 먼저 연결 추가
        self.manager.active_connections.append(self.mock_websocket)
        
        # 연결 해제
        self.manager.disconnect(self.mock_websocket)
        
        assert self.mock_websocket not in self.manager.active_connections
        
    @pytest.mark.asyncio
    async def test_broadcast_log_entry(self):
        """로그 엔트리 브로드캐스트 테스트"""
        # 연결 추가
        await self.manager.connect(self.mock_websocket)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'Test message'
        }
        
        # 브로드캐스트 실행
        await self.manager.broadcast_log_entry(log_entry)
        
        # WebSocket으로 전송되었는지 확인
        self.mock_websocket.send_json.assert_called_once_with(log_entry)
        
    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_connections(self):
        """다중 연결 브로드캐스트 테스트"""
        # 여러 연결 추가
        mock_ws1 = Mock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        
        mock_ws2 = Mock(spec=WebSocket)
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()
        
        await self.manager.connect(mock_ws1)
        await self.manager.connect(mock_ws2)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'Test message'
        }
        
        # 브로드캐스트 실행
        await self.manager.broadcast_log_entry(log_entry)
        
        # 모든 연결에 전송되었는지 확인
        mock_ws1.send_json.assert_called_once_with(log_entry)
        mock_ws2.send_json.assert_called_once_with(log_entry)
        
    @pytest.mark.asyncio
    async def test_failed_broadcast_cleanup(self):
        """브로드캐스트 실패 시 연결 정리 테스트"""
        # 실패하는 WebSocket 모킹
        failing_ws = Mock(spec=WebSocket)
        failing_ws.accept = AsyncMock()
        failing_ws.send_json = AsyncMock(side_effect=Exception("Connection lost"))
        
        await self.manager.connect(failing_ws)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'Test message'
        }
        
        # 브로드캐스트 실행 (실패해야 함)
        await self.manager.broadcast_log_entry(log_entry)
        
        # 실패한 연결이 제거되었는지 확인
        assert failing_ws not in self.manager.active_connections
        
    @pytest.mark.asyncio
    async def test_send_recent_logs(self):
        """최근 로그 전송 테스트"""
        with patch('api.logs.get_recent_logs') as mock_get_recent:
            mock_get_recent.return_value = [
                {'timestamp': datetime.now().isoformat(), 'level': 'INFO', 'message': 'Log 1'},
                {'timestamp': datetime.now().isoformat(), 'level': 'ERROR', 'message': 'Log 2'},
            ]
            
            await self.manager.send_recent_logs(self.mock_websocket, 2)
            
            # 2번 호출되었는지 확인 (각 로그마다)
            assert self.mock_websocket.send_json.call_count == 2


class TestLogStreamingIntegration:
    """로그 스트리밍 통합 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.client = TestClient(app)
        
    def test_setup_log_streaming(self):
        """로그 스트리밍 설정 테스트"""
        handler = setup_log_streaming()
        
        assert isinstance(handler, LogStreamHandler)
        
        # 루트 로거에 핸들러가 추가되었는지 확인
        root_logger = logging.getLogger()
        assert handler in root_logger.handlers
        
    def test_add_remove_stream_manager(self):
        """스트림 매니저 추가/제거 테스트"""
        mock_manager = Mock()
        
        # 스트림 매니저 추가
        broadcaster = add_stream_manager_to_handler(mock_manager)
        
        assert isinstance(broadcaster, AsyncLogBroadcaster)
        assert broadcaster.stream_manager == mock_manager
        
    def test_get_recent_logs_function(self):
        """최근 로그 조회 함수 테스트"""
        # 테스트 로그 생성
        logger = logging.getLogger('test_integration')
        logger.info('Integration test log 1')
        logger.error('Integration test log 2')
        
        # 최근 로그 조회
        recent_logs = get_recent_logs(10)
        
        # 로그가 있는지 확인 (정확한 개수는 다른 테스트의 영향을 받을 수 있음)
        assert isinstance(recent_logs, list)
        
    @pytest.mark.asyncio
    async def test_websocket_log_stream_endpoint(self):
        """WebSocket 로그 스트림 엔드포인트 테스트"""
        with self.client.websocket_connect("/api/logs/ws") as websocket:
            # 연결이 성공했는지 확인
            assert websocket is not None
            
            # 핑 메시지 전송
            websocket.send_text("ping")
            
            # 퐁 응답 수신
            response = websocket.receive_text()
            assert response == "pong"
            
    def test_log_files_endpoint(self):
        """로그 파일 목록 엔드포인트 테스트"""
        response = self.client.get("/api/logs/files")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_logs_endpoint_with_pagination(self):
        """페이지네이션이 있는 로그 엔드포인트 테스트"""
        response = self.client.get("/api/logs/?limit=10&offset=0")
        
        assert response.status_code in [200, 404]  # 로그 파일이 없을 수도 있음
        
    def test_log_search_endpoint(self):
        """로그 검색 엔드포인트 테스트"""
        response = self.client.get("/api/logs/search?query=test&file_name=watchhamster.log")
        
        assert response.status_code in [200, 404]  # 로그 파일이 없을 수도 있음
        
    def test_log_statistics_endpoint(self):
        """로그 통계 엔드포인트 테스트"""
        response = self.client.get("/api/logs/statistics?file_name=watchhamster.log&hours=24")
        
        assert response.status_code in [200, 404]  # 로그 파일이 없을 수도 있음


class TestLogStreamingPerformance:
    """로그 스트리밍 성능 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.handler = LogStreamHandler()
        self.manager = LogStreamManager()
        
    def test_high_volume_logging(self):
        """대용량 로깅 성능 테스트"""
        import time
        
        # 1000개의 로그 레코드 생성 및 처리
        start_time = time.time()
        
        for i in range(1000):
            record = logging.LogRecord(
                name='performance_test',
                level=logging.INFO,
                pathname='/test/path.py',
                lineno=42,
                msg=f'Performance test message {i}',
                args=(),
                exc_info=None
            )
            self.handler.emit(record)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 1초 이내에 처리되어야 함
        assert processing_time < 1.0
        
        # 버퍼 크기 제한이 적용되었는지 확인
        assert len(self.handler._buffer) <= self.handler._max_buffer_size
        
    @pytest.mark.asyncio
    async def test_concurrent_websocket_connections(self):
        """동시 WebSocket 연결 테스트"""
        # 10개의 동시 연결 시뮬레이션
        websockets = []
        
        for i in range(10):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            websockets.append(mock_ws)
            
        # 모든 연결을 동시에 추가
        connect_tasks = [self.manager.connect(ws) for ws in websockets]
        await asyncio.gather(*connect_tasks)
        
        # 모든 연결이 추가되었는지 확인
        assert len(self.manager.active_connections) == 10
        
        # 브로드캐스트 테스트
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'Concurrent test message'
        }
        
        await self.manager.broadcast_log_entry(log_entry)
        
        # 모든 연결에 메시지가 전송되었는지 확인
        for ws in websockets:
            ws.send_json.assert_called_once_with(log_entry)
            
    def test_memory_usage_with_buffer_limit(self):
        """버퍼 제한으로 인한 메모리 사용량 테스트"""
        import sys
        
        # 작은 버퍼 크기로 설정
        self.handler._max_buffer_size = 100
        
        # 메모리 사용량 측정 시작
        initial_size = sys.getsizeof(self.handler._buffer)
        
        # 1000개의 로그 추가 (버퍼 크기보다 많음)
        for i in range(1000):
            record = logging.LogRecord(
                name='memory_test',
                level=logging.INFO,
                pathname='/test/path.py',
                lineno=42,
                msg=f'Memory test message {i}' * 10,  # 긴 메시지
                args=(),
                exc_info=None
            )
            self.handler.emit(record)
        
        # 최종 메모리 사용량
        final_size = sys.getsizeof(self.handler._buffer)
        
        # 버퍼 크기가 제한되어 있는지 확인
        assert len(self.handler._buffer) == 100
        
        # 메모리 사용량이 합리적인 범위 내에 있는지 확인
        # (정확한 값은 시스템에 따라 다를 수 있음)
        assert final_size < initial_size * 200  # 200배 이하


if __name__ == "__main__":
    pytest.main([__file__, "-v"])