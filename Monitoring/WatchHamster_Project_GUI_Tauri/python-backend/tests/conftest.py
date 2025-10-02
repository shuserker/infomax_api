"""
pytest 설정 및 공통 픽스처
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 테스트 환경 변수 설정
os.environ["TESTING"] = "true"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["API_HOST"] = "127.0.0.1"
os.environ["API_PORT"] = "8001"  # 테스트용 포트

@pytest.fixture(scope="session")
def event_loop():
    """세션 범위 이벤트 루프"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """임시 디렉토리 픽스처"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def app():
    """FastAPI 앱 픽스처"""
    from main import app
    return app

@pytest.fixture
def client(app):
    """동기 테스트 클라이언트"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_system_metrics():
    """모의 시스템 메트릭 데이터"""
    return {
        "cpu_percent": 45.2,
        "memory_percent": 67.8,
        "disk_usage": 23.4,
        "network_status": "connected",
        "uptime": 86400,
        "active_services": 5
    }

@pytest.fixture
def mock_service_info():
    """모의 서비스 정보 데이터"""
    return {
        "id": "test_service",
        "name": "테스트 서비스",
        "description": "테스트용 서비스입니다",
        "status": "running",
        "uptime": 3600,
        "last_error": None,
        "config": {
            "auto_restart": True,
            "max_retries": 3
        }
    }

@pytest.fixture
def mock_webhook_template():
    """모의 웹훅 템플릿 데이터"""
    return {
        "id": "test_template",
        "name": "테스트 템플릿",
        "description": "테스트용 웹훅 템플릿",
        "template": "테스트 메시지: {message}",
        "webhook_type": "discord",
        "variables": ["message"]
    }

@pytest.fixture
def mock_log_entries():
    """모의 로그 엔트리 데이터"""
    return [
        {
            "timestamp": "2024-01-01T12:00:00",
            "level": "INFO",
            "message": "테스트 로그 메시지 1",
            "source": "test_module"
        },
        {
            "timestamp": "2024-01-01T12:01:00",
            "level": "WARNING",
            "message": "테스트 경고 메시지",
            "source": "test_module"
        },
        {
            "timestamp": "2024-01-01T12:02:00",
            "level": "ERROR",
            "message": "테스트 오류 메시지",
            "source": "test_module"
        }
    ]

@pytest.fixture
def mock_posco_status():
    """모의 POSCO 상태 데이터"""
    return {
        "status": "active",
        "current_branch": "main",
        "branch_switch_status": "idle",
        "deployment_status": "ready",
        "github_pages_status": {
            "is_accessible": True,
            "last_check": "2024-01-01T12:00:00",
            "response_time": 250
        },
        "git_status": {
            "has_changes": False,
            "ahead_commits": 0,
            "behind_commits": 0
        }
    }

# 테스트 유틸리티 함수들
def assert_response_structure(response_data: dict, expected_keys: list):
    """응답 데이터 구조 검증"""
    for key in expected_keys:
        assert key in response_data, f"응답에 '{key}' 키가 없습니다"

def assert_service_info_structure(service_info: dict):
    """서비스 정보 구조 검증"""
    required_keys = ["id", "name", "status"]
    assert_response_structure(service_info, required_keys)
    
    # 상태 값 검증
    valid_statuses = ["running", "stopped", "error", "starting", "stopping"]
    assert service_info["status"] in valid_statuses

def assert_metrics_structure(metrics: dict):
    """메트릭 데이터 구조 검증"""
    required_keys = ["cpu_percent", "memory_percent", "disk_usage", "network_status"]
    assert_response_structure(metrics, required_keys)
    
    # 수치 범위 검증
    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100
    assert 0 <= metrics["disk_usage"] <= 100

def assert_webhook_template_structure(template: dict):
    """웹훅 템플릿 구조 검증"""
    required_keys = ["id", "name", "template", "webhook_type"]
    assert_response_structure(template, required_keys)
    
    # 웹훅 타입 검증
    valid_types = ["discord", "slack", "generic", "teams"]
    assert template["webhook_type"] in valid_types