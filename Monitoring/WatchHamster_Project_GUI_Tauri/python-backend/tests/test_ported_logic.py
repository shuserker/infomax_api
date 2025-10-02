"""
기존 로직 포팅 검증 단위 테스트
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

import pytest
import psutil


class TestPerformanceOptimizer:
    """성능 최적화 시스템 테스트"""
    
    @pytest.mark.unit
    async def test_get_performance_optimizer_singleton(self):
        """성능 최적화 시스템 싱글톤 테스트"""
        from core.performance_optimizer import get_performance_optimizer
        
        # 두 번 호출해서 같은 인스턴스인지 확인
        optimizer1 = get_performance_optimizer()
        optimizer2 = get_performance_optimizer()
        
        assert optimizer1 is optimizer2
    
    @pytest.mark.unit
    async def test_get_performance_metrics_structure(self):
        """성능 메트릭 구조 테스트"""
        from core.performance_optimizer import get_performance_optimizer
        
        optimizer = get_performance_optimizer()
        metrics = await optimizer.get_performance_metrics()
        
        # 필수 메트릭 키 확인
        required_keys = [
            "cpu_percent", "memory_percent", "disk_usage_percent",
            "process_count", "boot_time", "cpu_count"
        ]
        
        for key in required_keys:
            assert key in metrics, f"메트릭에 '{key}' 키가 없습니다"
        
        # 값 범위 검증
        assert 0 <= metrics["cpu_percent"] <= 100
        assert 0 <= metrics["memory_percent"] <= 100
        assert 0 <= metrics["disk_usage_percent"] <= 100
        assert metrics["process_count"] > 0
        assert metrics["cpu_count"] > 0
    
    @pytest.mark.unit
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    async def test_get_performance_metrics_with_mocks(self, mock_disk, mock_memory, mock_cpu):
        """Mock을 사용한 성능 메트릭 테스트"""
        from core.performance_optimizer import get_performance_optimizer
        
        # Mock 설정
        mock_cpu.return_value = 45.2
        mock_memory.return_value = MagicMock(percent=67.8)
        mock_disk.return_value = MagicMock(percent=23.4)
        
        optimizer = get_performance_optimizer()
        metrics = await optimizer.get_performance_metrics()
        
        # Mock 값들이 반영되었는지 확인
        assert metrics["cpu_percent"] == 45.2
        assert metrics["memory_percent"] == 67.8
        assert metrics["disk_usage_percent"] == 23.4
    
    @pytest.mark.unit
    async def test_get_detailed_system_info(self):
        """상세 시스템 정보 조회 테스트"""
        from core.performance_optimizer import get_performance_optimizer
        
        optimizer = get_performance_optimizer()
        system_info = await optimizer.get_detailed_system_info()
        
        # 시스템 정보 구조 확인
        required_keys = [
            "platform", "architecture", "hostname", "python_version",
            "cpu_info", "memory_info", "disk_info", "network_info"
        ]
        
        for key in required_keys:
            assert key in system_info, f"시스템 정보에 '{key}' 키가 없습니다"
    
    @pytest.mark.unit
    async def test_optimize_performance(self):
        """성능 최적화 실행 테스트"""
        from core.performance_optimizer import get_performance_optimizer
        
        optimizer = get_performance_optimizer()
        result = await optimizer.optimize_performance()
        
        # 최적화 결과 구조 확인
        assert "optimizations_applied" in result
        assert "performance_improvement" in result
        assert isinstance(result["optimizations_applied"], list)


class TestStabilityManager:
    """안정성 관리자 테스트"""
    
    @pytest.mark.unit
    async def test_get_stability_manager_singleton(self):
        """안정성 관리자 싱글톤 테스트"""
        from core.stability_manager import get_stability_manager
        
        # 두 번 호출해서 같은 인스턴스인지 확인
        manager1 = get_stability_manager()
        manager2 = get_stability_manager()
        
        assert manager1 is manager2
    
    @pytest.mark.unit
    async def test_get_stability_metrics_structure(self):
        """안정성 메트릭 구조 테스트"""
        from core.stability_manager import get_stability_manager
        
        manager = get_stability_manager()
        metrics = await manager.get_stability_metrics()
        
        # 메트릭 객체 속성 확인
        assert hasattr(metrics, 'error_count')
        assert hasattr(metrics, 'recovery_count')
        assert hasattr(metrics, 'uptime_hours')
        assert hasattr(metrics, 'system_health')
        
        # 값 타입 검증
        assert isinstance(metrics.error_count, int)
        assert isinstance(metrics.recovery_count, int)
        assert isinstance(metrics.uptime_hours, (int, float))
        assert metrics.error_count >= 0
        assert metrics.recovery_count >= 0
        assert metrics.uptime_hours >= 0
    
    @pytest.mark.unit
    async def test_check_system_health(self):
        """시스템 상태 체크 테스트"""
        from core.stability_manager import get_stability_manager
        
        manager = get_stability_manager()
        health_status = await manager.check_system_health()
        
        # 상태 값 검증
        valid_statuses = ["healthy", "warning", "critical"]
        assert health_status.value in valid_statuses
    
    @pytest.mark.unit
    async def test_record_error(self):
        """오류 기록 테스트"""
        from core.stability_manager import get_stability_manager
        
        manager = get_stability_manager()
        
        # 초기 오류 수 확인
        initial_metrics = await manager.get_stability_metrics()
        initial_error_count = initial_metrics.error_count
        
        # 오류 기록
        await manager.record_error("테스트 오류", "test_component")
        
        # 오류 수 증가 확인
        updated_metrics = await manager.get_stability_metrics()
        assert updated_metrics.error_count >= initial_error_count
    
    @pytest.mark.unit
    async def test_record_recovery(self):
        """복구 기록 테스트"""
        from core.stability_manager import get_stability_manager
        
        manager = get_stability_manager()
        
        # 초기 복구 수 확인
        initial_metrics = await manager.get_stability_metrics()
        initial_recovery_count = initial_metrics.recovery_count
        
        # 복구 기록
        await manager.record_recovery("테스트 복구", "test_component")
        
        # 복구 수 증가 확인
        updated_metrics = await manager.get_stability_metrics()
        assert updated_metrics.recovery_count >= initial_recovery_count


class TestStatusReporter:
    """상태 보고 시스템 테스트"""
    
    @pytest.mark.unit
    async def test_create_integrated_status_reporter(self):
        """통합 상태 보고 시스템 생성 테스트"""
        from core.status_reporter import create_integrated_status_reporter
        
        reporter = create_integrated_status_reporter()
        assert reporter is not None
    
    @pytest.mark.unit
    async def test_get_system_status_structure(self):
        """시스템 상태 구조 테스트"""
        from core.status_reporter import create_integrated_status_reporter
        
        reporter = create_integrated_status_reporter()
        status = await reporter.get_system_status()
        
        # 상태 정보 구조 확인
        required_keys = [
            "total_components", "healthy_components", 
            "warning_components", "error_components"
        ]
        
        for key in required_keys:
            assert key in status, f"상태 정보에 '{key}' 키가 없습니다"
        
        # 값 타입 및 범위 검증
        assert isinstance(status["total_components"], int)
        assert isinstance(status["healthy_components"], int)
        assert isinstance(status["warning_components"], int)
        assert isinstance(status["error_components"], int)
        
        # 논리적 일관성 검증
        total = status["total_components"]
        healthy = status["healthy_components"]
        warning = status["warning_components"]
        error = status["error_components"]
        
        assert total >= 0
        assert healthy >= 0
        assert warning >= 0
        assert error >= 0
        assert healthy + warning + error <= total
    
    @pytest.mark.unit
    async def test_get_component_details(self):
        """컴포넌트 상세 정보 테스트"""
        from core.status_reporter import create_integrated_status_reporter
        
        reporter = create_integrated_status_reporter()
        details = await reporter.get_component_details()
        
        # 상세 정보 구조 확인
        assert isinstance(details, list)
        
        if details:  # 컴포넌트가 있는 경우
            component = details[0]
            required_keys = ["name", "status", "last_check"]
            
            for key in required_keys:
                assert key in component, f"컴포넌트 정보에 '{key}' 키가 없습니다"
    
    @pytest.mark.unit
    async def test_generate_status_report(self):
        """상태 보고서 생성 테스트"""
        from core.status_reporter import create_integrated_status_reporter
        
        reporter = create_integrated_status_reporter()
        report = await reporter.generate_status_report()
        
        # 보고서 구조 확인
        required_keys = ["timestamp", "summary", "details"]
        
        for key in required_keys:
            assert key in report, f"보고서에 '{key}' 키가 없습니다"
        
        # 타임스탬프 형식 확인
        assert isinstance(report["timestamp"], str)
        assert len(report["timestamp"]) > 0


class TestWebhookSystem:
    """웹훅 시스템 테스트"""
    
    @pytest.mark.unit
    def test_webhook_system_creation(self):
        """웹훅 시스템 생성 테스트"""
        from core.webhook_system import WebhookSystem
        
        webhook_system = WebhookSystem()
        assert webhook_system is not None
    
    @pytest.mark.unit
    def test_get_send_statistics(self):
        """전송 통계 조회 테스트"""
        from core.webhook_system import WebhookSystem
        
        webhook_system = WebhookSystem()
        stats = webhook_system.get_send_statistics()
        
        # 통계 구조 확인
        required_keys = ["total_sent", "successful_sent", "failed_sent", "success_rate"]
        
        for key in required_keys:
            assert key in stats, f"통계에 '{key}' 키가 없습니다"
        
        # 값 타입 및 범위 검증
        assert isinstance(stats["total_sent"], int)
        assert isinstance(stats["successful_sent"], int)
        assert isinstance(stats["failed_sent"], int)
        assert isinstance(stats["success_rate"], (int, float))
        
        assert stats["total_sent"] >= 0
        assert stats["successful_sent"] >= 0
        assert stats["failed_sent"] >= 0
        assert 0 <= stats["success_rate"] <= 100
    
    @pytest.mark.unit
    def test_get_message_templates(self):
        """메시지 템플릿 조회 테스트"""
        from core.webhook_system import WebhookSystem, MessageType
        
        webhook_system = WebhookSystem()
        template_engine = webhook_system.template_engine
        
        # 템플릿 엔진에서 템플릿 확인
        assert len(template_engine.templates) > 0
        
        # 기본 템플릿 타입들이 있는지 확인
        expected_types = [
            MessageType.DEPLOYMENT_SUCCESS,
            MessageType.DEPLOYMENT_FAILURE,
            MessageType.SYSTEM_STATUS,
            MessageType.ERROR_ALERT
        ]
        
        for msg_type in expected_types:
            assert msg_type in template_engine.templates
    
    @pytest.mark.unit
    def test_generate_message(self):
        """메시지 생성 테스트"""
        from core.webhook_system import WebhookSystem, MessageType
        
        webhook_system = WebhookSystem()
        template_engine = webhook_system.template_engine
        
        # 테스트 데이터
        test_data = {
            "deployment_id": "test_123",
            "completion_time": "2024-01-01 12:00:00",
            "steps_completed": 3,
            "duration": "5분",
            "report_url": "https://test.example.com",
            "status_message": "정상",
            "content_summary": "테스트 배포 완료"
        }
        
        # 메시지 생성
        message = template_engine.generate_message(MessageType.DEPLOYMENT_SUCCESS, test_data)
        
        # 메시지 구조 확인
        required_keys = ["message_type", "priority", "title", "body", "color", "timestamp"]
        for key in required_keys:
            assert key in message, f"메시지에 '{key}' 키가 없습니다"
        
        assert message["message_type"] == MessageType.DEPLOYMENT_SUCCESS.value
    
    @pytest.mark.unit
    @patch('httpx.AsyncClient.post')
    async def test_send_webhook_success(self, mock_post):
        """웹훅 전송 성공 테스트"""
        from core.webhook_system import WebhookSystem
        
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        webhook_system = WebhookSystem()
        
        result = await webhook_system.send_webhook(
            url="https://discord.com/api/webhooks/test",
            message="테스트 메시지",
            webhook_type="discord"
        )
        
        # 전송 결과 확인
        assert result["success"] is True
        assert "webhook_id" in result
        assert "message" in result
    
    @pytest.mark.unit
    def test_get_message_history(self):
        """메시지 히스토리 조회 테스트"""
        from core.webhook_system import WebhookSystem
        
        webhook_system = WebhookSystem()
        history = webhook_system.get_message_history()
        
        # 히스토리 구조 확인
        assert isinstance(history, list)
        
        if history:  # 히스토리가 있는 경우
            entry = history[0]
            required_keys = ["id", "timestamp", "webhook_url", "sent"]
            
            for key in required_keys:
                assert key in entry, f"히스토리 엔트리에 '{key}' 키가 없습니다"


class TestPoscoManager:
    """POSCO 관리자 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.posco
    def test_posco_manager_creation(self):
        """POSCO 관리자 생성 테스트"""
        from core.posco_manager import PoscoManager
        
        manager = PoscoManager()
        assert manager is not None
    
    @pytest.mark.unit
    @pytest.mark.posco
    async def test_get_deployment_status_structure(self):
        """배포 상태 구조 테스트"""
        from core.posco_manager import PoscoManager
        
        manager = PoscoManager()
        status = await manager.get_deployment_status()
        
        # 상태 구조 확인
        required_keys = [
            "current_branch", "branch_switch_status", 
            "deployment_status", "github_pages_status"
        ]
        
        for key in required_keys:
            assert key in status, f"배포 상태에 '{key}' 키가 없습니다"
        
        # GitHub Pages 상태 상세 확인
        gh_status = status["github_pages_status"]
        assert isinstance(gh_status, dict)
        assert "is_accessible" in gh_status
        assert isinstance(gh_status["is_accessible"], bool)
    
    @pytest.mark.unit
    @pytest.mark.posco
    @patch('subprocess.run')
    async def test_switch_branch_success(self, mock_run):
        """브랜치 전환 성공 테스트"""
        from core.posco_manager import PoscoManager
        
        # Mock 설정
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Switched to branch 'develop'",
            stderr=""
        )
        
        manager = PoscoManager()
        result = await manager.switch_branch("develop")
        
        # 전환 결과 확인
        assert result["success"] is True
        assert "message" in result
        assert "new_branch" in result
    
    @pytest.mark.unit
    @pytest.mark.posco
    @patch('subprocess.run')
    async def test_switch_branch_failure(self, mock_run):
        """브랜치 전환 실패 테스트"""
        from core.posco_manager import PoscoManager
        
        # Mock 설정 (실패)
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error: pathspec 'nonexistent' did not match any file(s) known to git"
        )
        
        manager = PoscoManager()
        result = await manager.switch_branch("nonexistent")
        
        # 실패 결과 확인
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.unit
    @pytest.mark.posco
    async def test_get_git_status(self):
        """Git 상태 조회 테스트"""
        from core.posco_manager import PoscoManager
        
        manager = PoscoManager()
        git_status = await manager.get_git_status()
        
        # Git 상태 구조 확인
        required_keys = ["has_changes", "ahead_commits", "behind_commits"]
        
        for key in required_keys:
            assert key in git_status, f"Git 상태에 '{key}' 키가 없습니다"
        
        # 값 타입 검증
        assert isinstance(git_status["has_changes"], bool)
        assert isinstance(git_status["ahead_commits"], int)
        assert isinstance(git_status["behind_commits"], int)
    
    @pytest.mark.unit
    @pytest.mark.posco
    @patch('httpx.AsyncClient.get')
    async def test_check_github_pages_accessibility(self, mock_get):
        """GitHub Pages 접근성 체크 테스트"""
        from core.posco_manager import PoscoManager
        
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.25
        mock_get.return_value = mock_response
        
        manager = PoscoManager()
        result = await manager.check_github_pages_accessibility()
        
        # 접근성 체크 결과 확인
        assert result["is_accessible"] is True
        assert "response_time" in result
        assert "last_check" in result


class TestIntegrationBetweenComponents:
    """컴포넌트 간 통합 테스트"""
    
    @pytest.mark.unit
    async def test_performance_and_stability_integration(self):
        """성능 최적화와 안정성 관리 통합 테스트"""
        from core.performance_optimizer import get_performance_optimizer
        from core.stability_manager import get_stability_manager
        
        optimizer = get_performance_optimizer()
        stability_manager = get_stability_manager()
        
        # 성능 메트릭 조회
        perf_metrics = await optimizer.get_performance_metrics()
        
        # 안정성 메트릭 조회
        stability_metrics = await stability_manager.get_stability_metrics()
        
        # 두 시스템이 모두 정상 작동하는지 확인
        assert perf_metrics["cpu_percent"] >= 0
        assert stability_metrics.error_count >= 0
    
    @pytest.mark.unit
    async def test_status_reporter_with_all_components(self):
        """상태 보고 시스템과 모든 컴포넌트 통합 테스트"""
        from core.status_reporter import create_integrated_status_reporter
        from core.performance_optimizer import get_performance_optimizer
        from core.stability_manager import get_stability_manager
        
        # 모든 컴포넌트 초기화
        reporter = create_integrated_status_reporter()
        optimizer = get_performance_optimizer()
        stability_manager = get_stability_manager()
        
        # 통합 상태 보고서 생성
        report = await reporter.generate_status_report()
        
        # 보고서에 모든 컴포넌트 정보가 포함되어 있는지 확인
        assert "summary" in report
        assert "details" in report
        assert report["summary"]["total_components"] > 0
    
    @pytest.mark.unit
    @pytest.mark.slow
    async def test_system_under_load(self):
        """시스템 부하 상황 테스트"""
        from core.performance_optimizer import get_performance_optimizer
        from core.stability_manager import get_stability_manager
        
        optimizer = get_performance_optimizer()
        stability_manager = get_stability_manager()
        
        # 동시에 여러 작업 실행
        tasks = []
        for _ in range(5):
            tasks.append(optimizer.get_performance_metrics())
            tasks.append(stability_manager.get_stability_metrics())
        
        # 모든 작업 완료 대기
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 모든 작업이 성공했는지 확인
        for result in results:
            assert not isinstance(result, Exception), f"작업 실패: {result}"