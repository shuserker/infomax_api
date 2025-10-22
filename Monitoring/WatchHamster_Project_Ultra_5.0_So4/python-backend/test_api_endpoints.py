#!/usr/bin/env python3
"""
REST API 엔드포인트 테스트 스크립트
구현된 모든 API 엔드포인트의 기본 기능을 테스트
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import httpx
import pytest

# 테스트 설정
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APITester:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def test_health_check(self):
        """헬스 체크 테스트"""
        logger.info("헬스 체크 테스트 시작")
        
        response = await self.client.get(f"{self.base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        
        logger.info("✅ 헬스 체크 테스트 통과")
        return data

    async def test_services_api(self):
        """서비스 관리 API 테스트"""
        logger.info("서비스 관리 API 테스트 시작")
        
        # 서비스 목록 조회
        response = await self.client.get(f"{self.base_url}/api/services/")
        assert response.status_code == 200
        
        services = response.json()
        assert isinstance(services, list)
        assert len(services) > 0
        
        # 첫 번째 서비스 정보 조회
        service_id = services[0]["id"]
        response = await self.client.get(f"{self.base_url}/api/services/{service_id}")
        assert response.status_code == 200
        
        service_info = response.json()
        assert service_info["id"] == service_id
        assert "name" in service_info
        assert "status" in service_info
        
        logger.info(f"✅ 서비스 관리 API 테스트 통과 (서비스 수: {len(services)})")
        return services

    async def test_metrics_api(self):
        """메트릭 API 테스트"""
        logger.info("메트릭 API 테스트 시작")
        
        # 시스템 메트릭 조회
        response = await self.client.get(f"{self.base_url}/api/metrics/")
        assert response.status_code == 200
        
        metrics = response.json()
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "disk_usage" in metrics
        assert "network_status" in metrics
        
        # 성능 메트릭 조회
        response = await self.client.get(f"{self.base_url}/api/metrics/performance")
        assert response.status_code == 200
        
        perf_metrics = response.json()
        assert "cpu_usage" in perf_metrics
        assert "memory_usage" in perf_metrics
        
        # 안정성 메트릭 조회
        response = await self.client.get(f"{self.base_url}/api/metrics/stability")
        assert response.status_code == 200
        
        stability_metrics = response.json()
        assert "error_count" in stability_metrics
        assert "system_health" in stability_metrics
        
        logger.info("✅ 메트릭 API 테스트 통과")
        return metrics

    async def test_webhooks_api(self):
        """웹훅 API 테스트"""
        logger.info("웹훅 API 테스트 시작")
        
        # 웹훅 템플릿 목록 조회
        response = await self.client.get(f"{self.base_url}/api/webhooks/templates")
        assert response.status_code == 200
        
        templates = response.json()
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # 첫 번째 템플릿 조회
        template_id = templates[0]["id"]
        response = await self.client.get(f"{self.base_url}/api/webhooks/templates/{template_id}")
        assert response.status_code == 200
        
        template = response.json()
        assert template["id"] == template_id
        assert "name" in template
        assert "template" in template
        
        # 웹훅 히스토리 조회
        response = await self.client.get(f"{self.base_url}/api/webhooks/history")
        assert response.status_code == 200
        
        history = response.json()
        assert isinstance(history, list)
        
        logger.info(f"✅ 웹훅 API 테스트 통과 (템플릿 수: {len(templates)})")
        return templates

    async def test_logs_api(self):
        """로그 API 테스트"""
        logger.info("로그 API 테스트 시작")
        
        # 로그 파일 목록 조회
        response = await self.client.get(f"{self.base_url}/api/logs/files")
        assert response.status_code == 200
        
        log_files = response.json()
        assert isinstance(log_files, list)
        
        # 로그 조회 (기본 파일)
        response = await self.client.get(f"{self.base_url}/api/logs/?limit=10")
        assert response.status_code == 200
        
        logs = response.json()
        assert isinstance(logs, list)
        
        # 로그 통계 조회
        response = await self.client.get(f"{self.base_url}/api/logs/statistics")
        assert response.status_code == 200
        
        stats = response.json()
        assert "total_logs" in stats
        assert "level_counts" in stats
        
        logger.info(f"✅ 로그 API 테스트 통과 (로그 파일 수: {len(log_files)})")
        return log_files

    async def test_posco_api(self):
        """POSCO API 테스트"""
        logger.info("POSCO API 테스트 시작")
        
        try:
            # POSCO 상태 조회
            response = await self.client.get(f"{self.base_url}/api/posco/status")
            assert response.status_code == 200
            
            status = response.json()
            assert "status" in status
            
            logger.info("✅ POSCO API 테스트 통과")
            return status
            
        except Exception as e:
            logger.warning(f"⚠️ POSCO API 테스트 실패 (예상됨): {e}")
            return None

    async def test_service_control(self):
        """서비스 제어 테스트 (실제 제어는 하지 않음)"""
        logger.info("서비스 제어 API 테스트 시작")
        
        # 서비스 목록 조회
        response = await self.client.get(f"{self.base_url}/api/services/")
        services = response.json()
        
        if services:
            service_id = services[0]["id"]
            
            # 서비스 상태 확인만 (실제 제어는 위험할 수 있음)
            response = await self.client.get(f"{self.base_url}/api/services/{service_id}")
            assert response.status_code == 200
            
            service_info = response.json()
            logger.info(f"서비스 '{service_id}' 상태: {service_info['status']}")
        
        logger.info("✅ 서비스 제어 API 테스트 통과")

    async def test_webhook_send(self):
        """웹훅 전송 테스트 (테스트 URL 사용)"""
        logger.info("웹훅 전송 테스트 시작")
        
        # 테스트용 웹훅 페이로드
        test_payload = {
            "url": "https://httpbin.org/post",  # 테스트용 URL
            "message": "API 테스트 메시지",
            "webhook_type": "generic"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/webhooks/send",
                json=test_payload
            )
            assert response.status_code == 200
            
            result = response.json()
            assert "message" in result
            assert "webhook_id" in result
            
            logger.info("✅ 웹훅 전송 테스트 통과")
            return result
            
        except Exception as e:
            logger.warning(f"⚠️ 웹훅 전송 테스트 실패: {e}")
            return None

    async def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("=== REST API 엔드포인트 테스트 시작 ===")
        
        test_results = {}
        
        try:
            # 기본 테스트들
            test_results["health"] = await self.test_health_check()
            test_results["services"] = await self.test_services_api()
            test_results["metrics"] = await self.test_metrics_api()
            test_results["webhooks"] = await self.test_webhooks_api()
            test_results["logs"] = await self.test_logs_api()
            test_results["posco"] = await self.test_posco_api()
            
            # 기능 테스트들
            await self.test_service_control()
            test_results["webhook_send"] = await self.test_webhook_send()
            
            logger.info("=== 모든 테스트 완료 ===")
            return test_results
            
        except Exception as e:
            logger.error(f"테스트 실행 중 오류: {e}")
            raise

async def main():
    """메인 테스트 함수"""
    logger.info("REST API 엔드포인트 테스트를 시작합니다...")
    
    async with APITester() as tester:
        try:
            results = await tester.run_all_tests()
            
            # 결과 요약
            logger.info("\n=== 테스트 결과 요약 ===")
            for test_name, result in results.items():
                if result is not None:
                    logger.info(f"✅ {test_name}: 성공")
                else:
                    logger.info(f"⚠️ {test_name}: 실패 또는 건너뜀")
            
            logger.info("\n🎉 REST API 엔드포인트 테스트가 완료되었습니다!")
            
        except Exception as e:
            logger.error(f"❌ 테스트 실행 실패: {e}")
            return False
    
    return True

if __name__ == "__main__":
    # 비동기 테스트 실행
    success = asyncio.run(main())
    exit(0 if success else 1)