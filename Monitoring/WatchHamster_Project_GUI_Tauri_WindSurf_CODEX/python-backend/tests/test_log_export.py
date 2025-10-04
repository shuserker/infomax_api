"""
로그 내보내기 및 보관 정책 API 테스트
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from api.logs import LogEntry, LogRetentionPolicy

client = TestClient(app)

# 테스트용 로그 데이터
test_logs = [
    {
        "timestamp": "2024-01-01T10:00:00.000Z",
        "level": "INFO",
        "logger_name": "test-service",
        "message": "테스트 로그 메시지 1",
        "module": "test_module",
        "line_number": 10
    },
    {
        "timestamp": "2024-01-01T10:01:00.000Z",
        "level": "ERROR",
        "logger_name": "test-service",
        "message": "테스트 에러 메시지",
        "module": "test_module",
        "line_number": 20
    },
    {
        "timestamp": "2024-01-01T10:02:00.000Z",
        "level": "WARN",
        "logger_name": "another-service",
        "message": "테스트 경고 메시지",
        "module": "another_module",
        "line_number": 30
    }
]

class TestLogExport:
    """로그 내보내기 API 테스트"""

    def test_export_logs_txt_format(self):
        """텍스트 형식으로 로그 내보내기 테스트"""
        export_request = {
            "logs": test_logs,
            "format": "txt",
            "include_metadata": False
        }
        
        response = client.post("/api/logs/export", json=export_request)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        content = response.text
        assert "테스트 로그 메시지 1" in content
        assert "테스트 에러 메시지" in content
        assert "테스트 경고 메시지" in content

    def test_export_logs_json_format(self):
        """JSON 형식으로 로그 내보내기 테스트"""
        export_request = {
            "logs": test_logs,
            "format": "json",
            "include_metadata": True
        }
        
        response = client.post("/api/logs/export", json=export_request)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json; charset=utf-8"
        
        content = json.loads(response.text)
        assert "metadata" in content
        assert "logs" in content
        assert len(content["logs"]) == 3
        assert content["metadata"]["total_logs"] == 3

    def test_export_logs_csv_format(self):
        """CSV 형식으로 로그 내보내기 테스트"""
        export_request = {
            "logs": test_logs,
            "format": "csv",
            "include_metadata": False
        }
        
        response = client.post("/api/logs/export", json=export_request)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        content = response.text
        lines = content.strip().split('\n')
        assert len(lines) == 4  # 헤더 + 3개 로그
        assert "Timestamp,Level,Logger,Message" in lines[0]

    def test_export_logs_custom_filename(self):
        """커스텀 파일명으로 로그 내보내기 테스트"""
        export_request = {
            "logs": test_logs,
            "format": "txt",
            "custom_filename": "my-custom-logs"
        }
        
        response = client.post("/api/logs/export", json=export_request)
        
        assert response.status_code == 200
        assert "my-custom-logs.txt" in response.headers["content-disposition"]

    def test_export_logs_empty_list(self):
        """빈 로그 목록 내보내기 테스트"""
        export_request = {
            "logs": [],
            "format": "txt"
        }
        
        response = client.post("/api/logs/export", json=export_request)
        
        assert response.status_code == 200
        assert response.text == ""

    def test_export_logs_invalid_format(self):
        """잘못된 형식으로 내보내기 시도 테스트"""
        export_request = {
            "logs": test_logs,
            "format": "invalid_format"
        }
        
        response = client.post("/api/logs/export", json=export_request)
        
        assert response.status_code == 500

    def test_get_export_formats(self):
        """지원하는 내보내기 형식 목록 조회 테스트"""
        response = client.get("/api/logs/export-formats")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "formats" in data
        assert len(data["formats"]) == 3
        
        format_ids = [fmt["id"] for fmt in data["formats"]]
        assert "txt" in format_ids
        assert "json" in format_ids
        assert "csv" in format_ids


class TestLogRetentionPolicy:
    """로그 보관 정책 API 테스트"""

    @patch("aiofiles.open")
    @patch("pathlib.Path.exists")
    def test_get_retention_policy_default(self, mock_exists, mock_open_file):
        """기본 보관 정책 조회 테스트"""
        mock_exists.return_value = False
        
        response = client.get("/api/logs/retention-policy")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["max_days"] == 30
        assert data["max_size_mb"] == 100
        assert data["max_files"] == 50
        assert data["compression_enabled"] is True
        assert data["auto_cleanup"] is True

    @patch("aiofiles.open")
    @patch("pathlib.Path.exists")
    def test_get_retention_policy_from_file(self, mock_exists, mock_open_file):
        """파일에서 보관 정책 조회 테스트"""
        mock_exists.return_value = True
        
        policy_data = {
            "max_days": 60,
            "max_size_mb": 200,
            "max_files": 100,
            "compression_enabled": False,
            "auto_cleanup": False,
            "cleanup_schedule": "weekly",
            "level_based_retention": {
                "DEBUG": 3,
                "INFO": 30,
                "WARN": 90,
                "ERROR": 180,
                "CRITICAL": 365
            }
        }
        
        mock_file = mock_open(read_data=json.dumps(policy_data))
        mock_open_file.return_value.__aenter__.return_value = mock_file.return_value
        
        response = client.get("/api/logs/retention-policy")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["max_days"] == 60
        assert data["max_size_mb"] == 200
        assert data["compression_enabled"] is False

    @patch("aiofiles.open")
    def test_save_retention_policy(self, mock_open_file):
        """보관 정책 저장 테스트"""
        policy_data = {
            "max_days": 45,
            "max_size_mb": 150,
            "max_files": 75,
            "compression_enabled": True,
            "auto_cleanup": True,
            "cleanup_schedule": "weekly",
            "level_based_retention": {
                "DEBUG": 7,
                "INFO": 30,
                "WARN": 90,
                "ERROR": 180,
                "CRITICAL": 365
            }
        }
        
        mock_file = mock_open()
        mock_open_file.return_value.__aenter__.return_value = mock_file.return_value
        
        response = client.post("/api/logs/retention-policy", json=policy_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "성공적으로 저장" in data["message"]

    def test_save_retention_policy_invalid_days(self):
        """잘못된 보관 일수로 정책 저장 시도 테스트"""
        policy_data = {
            "max_days": 0,  # 잘못된 값
            "max_size_mb": 100,
            "max_files": 50,
            "compression_enabled": True,
            "auto_cleanup": True,
            "cleanup_schedule": "daily",
            "level_based_retention": {}
        }
        
        response = client.post("/api/logs/retention-policy", json=policy_data)
        
        assert response.status_code == 400
        assert "1일 이상이어야 합니다" in response.json()["detail"]

    def test_save_retention_policy_invalid_size(self):
        """잘못된 파일 크기로 정책 저장 시도 테스트"""
        policy_data = {
            "max_days": 30,
            "max_size_mb": 0,  # 잘못된 값
            "max_files": 50,
            "compression_enabled": True,
            "auto_cleanup": True,
            "cleanup_schedule": "daily",
            "level_based_retention": {}
        }
        
        response = client.post("/api/logs/retention-policy", json=policy_data)
        
        assert response.status_code == 400
        assert "1MB 이상이어야 합니다" in response.json()["detail"]

    def test_save_retention_policy_invalid_files(self):
        """잘못된 파일 수로 정책 저장 시도 테스트"""
        policy_data = {
            "max_days": 30,
            "max_size_mb": 100,
            "max_files": 0,  # 잘못된 값
            "compression_enabled": True,
            "auto_cleanup": True,
            "cleanup_schedule": "daily",
            "level_based_retention": {}
        }
        
        response = client.post("/api/logs/retention-policy", json=policy_data)
        
        assert response.status_code == 400
        assert "1개 이상이어야 합니다" in response.json()["detail"]


class TestLogCleanup:
    """로그 정리 API 테스트"""

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists")
    @patch("aiofiles.open")
    def test_cleanup_logs_success(self, mock_open_file, mock_exists, mock_glob):
        """로그 정리 성공 테스트"""
        # 기본 정책 사용
        mock_exists.return_value = False
        
        # 가짜 로그 파일들 생성
        mock_files = []
        for i in range(5):
            mock_file = Path(f"old_log_{i}.log")
            mock_file.is_file = lambda: True
            mock_file.stat = lambda: type('stat', (), {
                'st_mtime': (datetime.now() - timedelta(days=40)).timestamp(),
                'st_size': 1024 * 1024  # 1MB
            })()
            mock_file.unlink = lambda: None
            mock_file.name = f"old_log_{i}.log"
            mock_files.append(mock_file)
        
        mock_glob.return_value = mock_files
        
        response = client.post("/api/logs/cleanup")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "deleted_files" in data
        assert "compressed_files" in data
        assert "total_space_freed" in data
        assert "total_space_freed_mb" in data

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists")
    @patch("aiofiles.open")
    def test_cleanup_logs_with_policy(self, mock_open_file, mock_exists, mock_glob):
        """커스텀 정책으로 로그 정리 테스트"""
        # 커스텀 정책 파일 존재
        mock_exists.return_value = True
        
        policy_data = {
            "max_days": 7,  # 짧은 보관 기간
            "max_size_mb": 50,
            "max_files": 10,
            "compression_enabled": True,
            "auto_cleanup": True,
            "cleanup_schedule": "daily",
            "level_based_retention": {}
        }
        
        mock_file = mock_open(read_data=json.dumps(policy_data))
        mock_open_file.return_value.__aenter__.return_value = mock_file.return_value
        
        # 빈 파일 목록
        mock_glob.return_value = []
        
        response = client.post("/api/logs/cleanup")
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data["deleted_files"], list)
        assert isinstance(data["compressed_files"], list)

    @patch("pathlib.Path.glob")
    def test_cleanup_logs_error(self, mock_glob):
        """로그 정리 중 오류 발생 테스트"""
        mock_glob.side_effect = Exception("파일 시스템 오류")
        
        response = client.post("/api/logs/cleanup")
        
        assert response.status_code == 500
        assert "로그 정리 중 오류가 발생했습니다" in response.json()["detail"]


class TestLogFormatting:
    """로그 포맷팅 함수 테스트"""

    def test_format_logs_as_txt(self):
        """텍스트 형식 포맷팅 테스트"""
        from api.logs import _format_logs_as_txt
        
        log_entries = [
            LogEntry(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                level="INFO",
                logger_name="test",
                message="테스트 메시지"
            )
        ]
        
        result = _format_logs_as_txt(log_entries)
        
        assert "2024-01-01 10:00:00" in result
        assert "INFO" in result
        assert "test" in result
        assert "테스트 메시지" in result

    def test_format_logs_as_json_with_metadata(self):
        """메타데이터 포함 JSON 형식 포맷팅 테스트"""
        from api.logs import _format_logs_as_json
        
        log_entries = [
            LogEntry(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                level="INFO",
                logger_name="test",
                message="테스트 메시지"
            )
        ]
        
        result = _format_logs_as_json(log_entries, include_metadata=True)
        data = json.loads(result)
        
        assert "metadata" in data
        assert "logs" in data
        assert data["metadata"]["total_logs"] == 1
        assert "exported_at" in data["metadata"]

    def test_format_logs_as_json_without_metadata(self):
        """메타데이터 없는 JSON 형식 포맷팅 테스트"""
        from api.logs import _format_logs_as_json
        
        log_entries = [
            LogEntry(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                level="INFO",
                logger_name="test",
                message="테스트 메시지"
            )
        ]
        
        result = _format_logs_as_json(log_entries, include_metadata=False)
        data = json.loads(result)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["level"] == "INFO"

    def test_format_logs_as_csv(self):
        """CSV 형식 포맷팅 테스트"""
        from api.logs import _format_logs_as_csv
        
        log_entries = [
            LogEntry(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                level="INFO",
                logger_name="test",
                message="테스트 메시지",
                module="test_module",
                line_number=10
            )
        ]
        
        result = _format_logs_as_csv(log_entries)
        lines = result.strip().split('\n')
        
        assert len(lines) == 2  # 헤더 + 1개 로그
        assert "Timestamp,Level,Logger,Message" in lines[0]
        assert "INFO" in lines[1]
        assert "test" in lines[1]
        assert "테스트 메시지" in lines[1]