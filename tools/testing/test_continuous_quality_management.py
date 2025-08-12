#!/usr/bin/env python3
"""
POSCO 시스템 지속적 품질 관리 시스템 테스트
Test Suite for Continuous Quality Management System
"""

import unittest
import tempfile
import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# 테스트 대상 모듈 import
from continuous_quality_management_system import (
    ContinuousIntegrationPipeline,
    QualityMonitoringDashboard,
    HealthCheckSystem,
    ContinuousQualityManager,
    QualityMetric,
    PipelineStage
)

class TestContinuousIntegrationPipeline(unittest.TestCase):
    """CI/CD 파이프라인 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_ci_config.yaml")
        
        # 테스트용 설정 파일 생성
        test_config = """
stages:
  - name: syntax_check
    enabled: true
    timeout: 60
  - name: import_test
    enabled: true
    timeout: 60
notifications:
  enabled: false
artifacts:
  retention_days: 1
  storage_path: ./test_artifacts
"""
        with open(self.config_file, 'w') as f:
            f.write(test_config)
        
        self.pipeline = ContinuousIntegrationPipeline(self.config_file)
    
    def tearDown(self):
        """테스트 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_pipeline_initialization(self):
        """파이프라인 초기화 테스트"""
        self.assertIsNotNone(self.pipeline.config)
        self.assertIn('stages', self.pipeline.config)
        self.assertEqual(len(self.pipeline.stages), 0)
    
    @patch('continuous_quality_management_system.SyntaxVerificationSystem')
    def test_syntax_check_stage(self, mock_syntax_system):
        """구문 검사 스테이지 테스트"""
        # Mock 설정
        mock_instance = MagicMock()
        mock_instance.verify_all_python_files.return_value = [
            MagicMock(success=True, file_path="test1.py"),
            MagicMock(success=True, file_path="test2.py")
        ]
        mock_syntax_system.return_value = mock_instance
        
        # 스테이지 생성 및 실행
        stage = PipelineStage(name='syntax_check', status='pending', logs=[], artifacts=[])
        result = self.pipeline._run_syntax_check(stage)
        
        self.assertTrue(result)
        self.assertIn("총 2개 파일 검사", ' '.join(stage.logs))
    
    @patch('continuous_quality_management_system.ModuleImportTestSystem')
    def test_import_test_stage(self, mock_import_system):
        """Import 테스트 스테이지 테스트"""
        # Mock 설정
        mock_instance = MagicMock()
        mock_instance.test_all_imports.return_value = [
            MagicMock(success=True, module_name="module1"),
            MagicMock(success=False, module_name="module2", message="Import failed")
        ]
        mock_import_system.return_value = mock_instance
        
        # 스테이지 생성 및 실행
        stage = PipelineStage(name='import_test', status='pending', logs=[], artifacts=[])
        result = self.pipeline._run_import_test(stage)
        
        self.assertFalse(result)  # 실패한 모듈이 있으므로 False
        self.assertIn("실패: 1개", ' '.join(stage.logs))

class TestQualityMonitoringDashboard(unittest.TestCase):
    """품질 모니터링 대시보드 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_quality.db")
        self.dashboard = QualityMonitoringDashboard(self.db_path)
    
    def tearDown(self):
        """테스트 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True) 
   def test_database_initialization(self):
        """데이터베이스 초기화 테스트"""
        self.assertTrue(os.path.exists(self.db_path))
        
        # 테이블 존재 확인
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('quality_metrics', tables)
        self.assertIn('pipeline_runs', tables)
        
        conn.close()
    
    def test_metric_recording(self):
        """메트릭 기록 테스트"""
        metric = QualityMetric(
            name="test_metric",
            value=75.5,
            threshold=80.0,
            status="pass",
            timestamp=datetime.now(),
            details={"test": "data"}
        )
        
        self.dashboard.record_metric(metric)
        
        # 데이터베이스에서 확인
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM quality_metrics WHERE name = ?", ("test_metric",))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[1], "test_metric")  # name
        self.assertEqual(row[2], 75.5)  # value
        
        conn.close()
    
    def test_current_metrics_retrieval(self):
        """현재 메트릭 조회 테스트"""
        # 테스트 메트릭 추가
        metric1 = QualityMetric(
            name="cpu_usage",
            value=60.0,
            threshold=80.0,
            status="pass",
            timestamp=datetime.now()
        )
        
        metric2 = QualityMetric(
            name="memory_usage",
            value=70.0,
            threshold=85.0,
            status="pass",
            timestamp=datetime.now()
        )
        
        self.dashboard.record_metric(metric1)
        self.dashboard.record_metric(metric2)
        
        # 현재 메트릭 조회
        current_metrics = self.dashboard.get_current_metrics()
        
        self.assertEqual(len(current_metrics), 2)
        self.assertIn("cpu_usage", current_metrics)
        self.assertIn("memory_usage", current_metrics)
    
    def test_dashboard_html_generation(self):
        """대시보드 HTML 생성 테스트"""
        # 테스트 메트릭 추가
        metric = QualityMetric(
            name="test_metric",
            value=85.0,
            threshold=90.0,
            status="pass",
            timestamp=datetime.now()
        )
        
        self.dashboard.record_metric(metric)
        
        # HTML 생성
        html_content = self.dashboard.generate_dashboard_html()
        
        self.assertIn("POSCO 시스템 품질 대시보드", html_content)
        self.assertIn("test_metric", html_content)
        self.assertIn("85.00", html_content)

class TestHealthCheckSystem(unittest.TestCase):
    """건강성 체크 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_health.db")
        self.dashboard = QualityMonitoringDashboard(self.db_path)
        self.health_system = HealthCheckSystem(self.dashboard)
    
    def tearDown(self):
        """테스트 정리"""
        self.health_system.stop_scheduler()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_health_check_registration(self):
        """건강성 체크 등록 테스트"""
        def dummy_check():
            return {'healthy': True, 'message': 'OK'}
        
        self.health_system.register_health_check("test_check", dummy_check, 5)
        
        self.assertEqual(len(self.health_system.health_checks), 1)
        self.assertEqual(self.health_system.health_checks[0]['name'], "test_check")
    
    def test_health_check_execution(self):
        """건강성 체크 실행 테스트"""
        def test_check():
            return {
                'healthy': True,
                'message': 'Test passed',
                'details': {'test_data': 'value'}
            }
        
        # 건강성 체크 실행
        self.health_system._run_health_check("test_check", test_check)
        
        # 메트릭이 기록되었는지 확인
        current_metrics = self.dashboard.get_current_metrics()
        self.assertIn("health_check_test_check", current_metrics)
    
    def test_health_status_retrieval(self):
        """건강성 상태 조회 테스트"""
        def dummy_check():
            return {'healthy': True, 'message': 'OK'}
        
        self.health_system.register_health_check("test_check", dummy_check, 5)
        
        # 건강성 체크 실행
        self.health_system._run_health_check("test_check", dummy_check)
        
        # 상태 조회
        status = self.health_system.get_health_status()
        
        self.assertIn('overall_healthy', status)
        self.assertIn('checks', status)
        self.assertEqual(len(status['checks']), 1)

class TestContinuousQualityManager(unittest.TestCase):
    """지속적 품질 관리자 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 임시 설정 파일 생성
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        with open(self.config_file, 'w') as f:
            f.write("stages:\n  - name: syntax_check\n    enabled: true\n    timeout: 60\n")
        
        # 환경 변수 설정
        os.environ['CI_CONFIG_PATH'] = self.config_file
        
        self.quality_manager = ContinuousQualityManager()
    
    def tearDown(self):
        """테스트 정리"""
        self.quality_manager.stop_continuous_monitoring()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # 환경 변수 정리
        if 'CI_CONFIG_PATH' in os.environ:
            del os.environ['CI_CONFIG_PATH']
    
    def test_quality_manager_initialization(self):
        """품질 관리자 초기화 테스트"""
        self.assertIsNotNone(self.quality_manager.pipeline)
        self.assertIsNotNone(self.quality_manager.dashboard)
        self.assertIsNotNone(self.quality_manager.health_system)
    
    def test_initial_metrics_collection(self):
        """초기 메트릭 수집 테스트"""
        self.quality_manager._collect_initial_metrics()
        
        # 메트릭이 수집되었는지 확인
        current_metrics = self.quality_manager.dashboard.get_current_metrics()
        
        # 시스템 메트릭이 있어야 함
        metric_names = list(current_metrics.keys())
        self.assertTrue(any('cpu' in name for name in metric_names) or 
                       any('memory' in name for name in metric_names))
    
    def test_quality_report_generation(self):
        """품질 보고서 생성 테스트"""
        # 초기 메트릭 수집
        self.quality_manager._collect_initial_metrics()
        
        # 보고서 생성
        report = self.quality_manager.generate_quality_report()
        
        self.assertIn("POSCO 시스템 품질 보고서", report)
        self.assertIn("현재 품질 메트릭", report)
        self.assertIn("시스템 건강성 상태", report)

def run_tests():
    """테스트 실행"""
    print("🧪 지속적 품질 관리 시스템 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 테스트 케이스 추가
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestContinuousIntegrationPipeline))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQualityMonitoringDashboard))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHealthCheckSystem))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestContinuousQualityManager))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 결과 출력
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 모든 테스트 통과!")
    else:
        print(f"❌ 테스트 실패: {len(result.failures)} 실패, {len(result.errors)} 오류")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)