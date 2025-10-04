"""
FastAPI 엔드포인트 단위 테스트
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import (
    assert_response_structure,
    assert_service_info_structure,
    assert_metrics_structure,
    assert_webhook_template_structure
)


class TestHealthEndpoints:
    """헬스 체크 엔드포인트 테스트"""
    
    @pytest.mark.unit
    async def test_health_check(self, async_client: AsyncClient):
        """헬스 체크 엔드포인트 테스트"""
        response = await async_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_response_structure(data, ["status", "service", "version"])
        assert data["status"] == "healthy"
        assert "WatchHamster" in data["service"]
    
    @pytest.mark.unit
    async def test_root_endpoint(self, async_client: AsyncClient):
        """루트 엔드포인트 테스트"""
        response = await async_client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_response_structure(data, ["message", "docs", "health"])
        assert "WatchHamster" in data["message"]


class TestServicesAPI:
    """서비스 관리 API 테스트"""
    
    @pytest.mark.unit
    @patch('api.services.get_service_manager')
    async def test_get_services_list(self, mock_get_manager, async_client: AsyncClient, mock_service_info):
        """서비스 목록 조회 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.get_all_services.return_value = [mock_service_info]
        mock_get_manager.return_value = mock_manager
        
        response = await async_client.get("/api/services/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert_service_info_structure(data[0])
    
    @pytest.mark.unit
    @patch('api.services.get_service_manager')
    async def test_get_service_by_id(self, mock_get_manager, async_client: AsyncClient, mock_service_info):
        """특정 서비스 조회 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.get_service.return_value = mock_service_info
        mock_get_manager.return_value = mock_manager
        
        service_id = "test_service"
        response = await async_client.get(f"/api/services/{service_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_service_info_structure(data)
        assert data["id"] == service_id
    
    @pytest.mark.unit
    @patch('api.services.get_service_manager')
    async def test_get_nonexistent_service(self, mock_get_manager, async_client: AsyncClient):
        """존재하지 않는 서비스 조회 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.get_service.return_value = None
        mock_get_manager.return_value = mock_manager
        
        response = await async_client.get("/api/services/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    @patch('api.services.get_service_manager')
    async def test_start_service(self, mock_get_manager, async_client: AsyncClient):
        """서비스 시작 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.start_service.return_value = {"success": True, "message": "서비스가 시작되었습니다"}
        mock_get_manager.return_value = mock_manager
        
        service_id = "test_service"
        response = await async_client.post(f"/api/services/{service_id}/start")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
    
    @pytest.mark.unit
    @patch('api.services.get_service_manager')
    async def test_stop_service(self, mock_get_manager, async_client: AsyncClient):
        """서비스 중지 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.stop_service.return_value = {"success": True, "message": "서비스가 중지되었습니다"}
        mock_get_manager.return_value = mock_manager
        
        service_id = "test_service"
        response = await async_client.post(f"/api/services/{service_id}/stop")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
    
    @pytest.mark.unit
    @patch('api.services.get_service_manager')
    async def test_restart_service(self, mock_get_manager, async_client: AsyncClient):
        """서비스 재시작 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.restart_service.return_value = {"success": True, "message": "서비스가 재시작되었습니다"}
        mock_get_manager.return_value = mock_manager
        
        service_id = "test_service"
        response = await async_client.post(f"/api/services/{service_id}/restart")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data


class TestMetricsAPI:
    """메트릭 API 테스트"""
    
    @pytest.mark.unit
    @patch('api.metrics.get_performance_optimizer')
    async def test_get_system_metrics(self, mock_get_optimizer, async_client: AsyncClient, mock_system_metrics):
        """시스템 메트릭 조회 테스트"""
        # Mock 설정
        mock_optimizer = AsyncMock()
        mock_optimizer.get_performance_metrics.return_value = mock_system_metrics
        mock_get_optimizer.return_value = mock_optimizer
        
        response = await async_client.get("/api/metrics/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_metrics_structure(data)
    
    @pytest.mark.unit
    @patch('api.metrics.get_performance_optimizer')
    async def test_get_performance_metrics(self, mock_get_optimizer, async_client: AsyncClient):
        """성능 메트릭 조회 테스트"""
        # Mock 설정
        mock_optimizer = AsyncMock()
        mock_optimizer.get_performance_metrics.return_value = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_io": {"read": 1024, "write": 512},
            "network_io": {"sent": 2048, "received": 4096}
        }
        mock_get_optimizer.return_value = mock_optimizer
        
        response = await async_client.get("/api/metrics/performance")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_response_structure(data, ["cpu_usage", "memory_usage"])
    
    @pytest.mark.unit
    @patch('api.metrics.get_stability_manager')
    async def test_get_stability_metrics(self, mock_get_manager, async_client: AsyncClient):
        """안정성 메트릭 조회 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.get_stability_metrics.return_value = MagicMock(
            error_count=0,
            recovery_count=2,
            uptime_hours=24.5,
            system_health=MagicMock(value="healthy")
        )
        mock_get_manager.return_value = mock_manager
        
        response = await async_client.get("/api/metrics/stability")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_response_structure(data, ["error_count", "system_health"])


class TestWebhooksAPI:
    """웹훅 API 테스트"""
    
    @pytest.mark.unit
    @patch('api.webhooks.WebhookSystem')
    async def test_get_webhook_templates(self, mock_webhook_system, async_client: AsyncClient, mock_webhook_template):
        """웹훅 템플릿 목록 조회 테스트"""
        # Mock 설정
        mock_system = MagicMock()
        mock_system.get_all_templates.return_value = [mock_webhook_template]
        mock_webhook_system.return_value = mock_system
        
        response = await async_client.get("/api/webhooks/templates")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert_webhook_template_structure(data[0])
    
    @pytest.mark.unit
    @patch('api.webhooks.WebhookSystem')
    async def test_get_webhook_template_by_id(self, mock_webhook_system, async_client: AsyncClient, mock_webhook_template):
        """특정 웹훅 템플릿 조회 테스트"""
        # Mock 설정
        mock_system = MagicMock()
        mock_system.get_template.return_value = mock_webhook_template
        mock_webhook_system.return_value = mock_system
        
        template_id = "test_template"
        response = await async_client.get(f"/api/webhooks/templates/{template_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_webhook_template_structure(data)
        assert data["id"] == template_id
    
    @pytest.mark.unit
    @patch('api.webhooks.WebhookSystem')
    async def test_send_webhook(self, mock_webhook_system, async_client: AsyncClient):
        """웹훅 전송 테스트"""
        # Mock 설정
        mock_system = MagicMock()
        mock_system.send_webhook.return_value = {
            "success": True,
            "webhook_id": "test_webhook_123",
            "message": "웹훅이 성공적으로 전송되었습니다"
        }
        mock_webhook_system.return_value = mock_system
        
        webhook_data = {
            "url": "https://discord.com/api/webhooks/test",
            "message": "테스트 메시지",
            "webhook_type": "discord"
        }
        
        response = await async_client.post("/api/webhooks/send", json=webhook_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "webhook_id" in data
        assert "message" in data
    
    @pytest.mark.unit
    @patch('api.webhooks.WebhookSystem')
    async def test_get_webhook_history(self, mock_webhook_system, async_client: AsyncClient):
        """웹훅 히스토리 조회 테스트"""
        # Mock 설정
        mock_system = MagicMock()
        mock_system.get_send_history.return_value = [
            {
                "id": "webhook_1",
                "timestamp": "2024-01-01T12:00:00",
                "url": "https://discord.com/api/webhooks/test",
                "status": "success",
                "message": "테스트 메시지"
            }
        ]
        mock_webhook_system.return_value = mock_system
        
        response = await async_client.get("/api/webhooks/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)


class TestLogsAPI:
    """로그 API 테스트"""
    
    @pytest.mark.unit
    @patch('api.logs.LogManager')
    async def test_get_log_files(self, mock_log_manager, async_client: AsyncClient):
        """로그 파일 목록 조회 테스트"""
        # Mock 설정
        mock_manager = MagicMock()
        mock_manager.get_log_files.return_value = [
            {"name": "app.log", "size": 1024, "modified": "2024-01-01T12:00:00"},
            {"name": "error.log", "size": 512, "modified": "2024-01-01T11:00:00"}
        ]
        mock_log_manager.return_value = mock_manager
        
        response = await async_client.get("/api/logs/files")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert_response_structure(data[0], ["name", "size", "modified"])
    
    @pytest.mark.unit
    @patch('api.logs.LogManager')
    async def test_get_logs(self, mock_log_manager, async_client: AsyncClient, mock_log_entries):
        """로그 조회 테스트"""
        # Mock 설정
        mock_manager = MagicMock()
        mock_manager.get_logs.return_value = mock_log_entries
        mock_log_manager.return_value = mock_manager
        
        response = await async_client.get("/api/logs/?limit=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        if data:
            assert_response_structure(data[0], ["timestamp", "level", "message"])
    
    @pytest.mark.unit
    @patch('api.logs.LogManager')
    async def test_get_log_statistics(self, mock_log_manager, async_client: AsyncClient):
        """로그 통계 조회 테스트"""
        # Mock 설정
        mock_manager = MagicMock()
        mock_manager.get_log_statistics.return_value = {
            "total_logs": 1000,
            "level_counts": {
                "INFO": 800,
                "WARNING": 150,
                "ERROR": 50
            },
            "recent_errors": 5
        }
        mock_log_manager.return_value = mock_manager
        
        response = await async_client.get("/api/logs/statistics")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_response_structure(data, ["total_logs", "level_counts"])


class TestPoscoAPI:
    """POSCO API 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.posco
    @patch('api.posco.PoscoManager')
    async def test_get_posco_status(self, mock_posco_manager, async_client: AsyncClient, mock_posco_status):
        """POSCO 상태 조회 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.get_deployment_status.return_value = mock_posco_status
        mock_posco_manager.return_value = mock_manager
        
        response = await async_client.get("/api/posco/status")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_response_structure(data, ["status", "current_branch"])
    
    @pytest.mark.unit
    @pytest.mark.posco
    @patch('api.posco.PoscoManager')
    async def test_switch_branch(self, mock_posco_manager, async_client: AsyncClient):
        """브랜치 전환 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.switch_branch.return_value = {
            "success": True,
            "message": "브랜치가 성공적으로 전환되었습니다",
            "new_branch": "develop"
        }
        mock_posco_manager.return_value = mock_manager
        
        branch_data = {"branch": "develop"}
        response = await async_client.post("/api/posco/branch-switch", json=branch_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
    
    @pytest.mark.unit
    @pytest.mark.posco
    @patch('api.posco.PoscoManager')
    async def test_deploy(self, mock_posco_manager, async_client: AsyncClient):
        """배포 테스트"""
        # Mock 설정
        mock_manager = AsyncMock()
        mock_manager.deploy.return_value = {
            "success": True,
            "message": "배포가 성공적으로 완료되었습니다",
            "deployment_id": "deploy_123"
        }
        mock_posco_manager.return_value = mock_manager
        
        deploy_data = {"environment": "production", "force": False}
        response = await async_client.post("/api/posco/deploy", json=deploy_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "deployment_id" in data


class TestErrorHandling:
    """오류 처리 테스트"""
    
    @pytest.mark.unit
    async def test_404_error(self, async_client: AsyncClient):
        """404 오류 처리 테스트"""
        response = await async_client.get("/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    async def test_method_not_allowed(self, async_client: AsyncClient):
        """405 오류 처리 테스트"""
        response = await async_client.delete("/health")
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    @pytest.mark.unit
    async def test_invalid_json(self, async_client: AsyncClient):
        """잘못된 JSON 요청 처리 테스트"""
        response = await async_client.post(
            "/api/webhooks/send",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY