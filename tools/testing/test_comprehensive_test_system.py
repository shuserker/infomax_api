#!/usr/bin/env python3
"""
POSCO 시스템 종합 테스트 시스템 단위 테스트
Unit Tests for Comprehensive Test System

이 모듈은 종합 테스트 시스템의 각 컴포넌트를 테스트합니다.
"""

import unittest
import tempfile
import os
import sys
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# 테스트 대상 모듈 import
from comprehensive_test_system import (
    SyntaxVerificationSystem,
    ModuleImportTestSystem,
    FileReferenceIntegritySystem,
    PerformanceMonitoringSystem,
    ComprehensiveTestSystem,
    TestResult,
    SyntaxTestResult,
    ImportTestResult,
    FileReferenceTestResult,
    PerformanceTestResult
)

class TestSyntaxVerificationSystem(unittest.TestCase):
    """구문 검증 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.syntax_system = SyntaxVerificationSystem()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """테스트 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """테스트용 파일 생성"""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_discover_python_files(self):
        """Python 파일 발견 테스트"""
        # 테스트 파일들 생성
        self.create_test_file("test1.py", "print('hello')")
        self.create_test_file("test2.py", "import os")
        self.create_test_file("not_python.txt", "not python")
        
        # 하위 디렉토리 생성
        sub_dir = Path(self.temp_dir) / "subdir"
        sub_dir.mkdir()
        self.create_test_file("subdir/test3.py", "def func(): pass")
        
        # Python 파일 발견
        python_files = self.syntax_system.discover_python_files(Path(self.temp_dir))
        
        # 검증
        self.assertEqual(len(python_files), 3)
        py_names = [f.name for f in python_files]
        self.assertIn("test1.py", py_names)
        self.assertIn("test2.py", py_names)
        self.assertIn("test3.py", py_names)
    
    def test_verify_syntax_success(self):
        """정상 구문 검증 테스트"""
        # 정상적인 Python 파일 생성
        test_file = self.create_test_file("valid.py", """
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
""")
        
        # 구문 검증
        result = self.syntax_system.verify_syntax(test_file)
        
        # 검증
        self.assertIsInstance(result, SyntaxTestResult)
        self.assertTrue(result.success)
        self.assertEqual(result.file_path, str(test_file))
        self.assertGreater(result.execution_time, 0)
    
    def test_verify_syntax_error(self):
        """구문 오류 검증 테스트"""
        # 구문 오류가 있는 Python 파일 생성
        test_file = self.create_test_file("invalid.py", """
def broken_function(
    print("Missing closing parenthesis")
    return False
""")
        
        # 구문 검증
        result = self.syntax_system.verify_syntax(test_file)
        
        # 검증
        self.assertIsInstance(result, SyntaxTestResult)
        self.assertFalse(result.success)
        self.assertEqual(result.file_path, str(test_file))
        self.assertEqual(result.error_type, "syntax_error")
        self.assertGreater(result.line_number, 0)
    
    def test_generate_syntax_report(self):
        """구문 검증 보고서 생성 테스트"""
        # 테스트 결과 설정
        self.syntax_system.results = [
            SyntaxTestResult(
                test_name="test1",
                success=True,
                message="성공",
                file_path="test1.py",
                execution_time=0.1
            ),
            SyntaxTestResult(
                test_name="test2",
                success=False,
                message="실패",
                file_path="test2.py",
                error_type="syntax_error",
                line_number=5,
                execution_time=0.2
            )
        ]
        
        # 보고서 생성
        report = self.syntax_system.generate_syntax_report()
        
        # 검증
        self.assertIn("summary", report)
        self.assertEqual(report["summary"]["total_files"], 2)
        self.assertEqual(report["summary"]["successful_files"], 1)
        self.assertEqual(report["summary"]["failed_files"], 1)
        self.assertEqual(report["summary"]["success_rate"], 50.0)
        
        self.assertIn("failed_files", report)
        self.assertEqual(len(report["failed_files"]), 1)
        self.assertEqual(report["failed_files"][0]["file"], "test2.py")

class TestModuleImportTestSystem(unittest.TestCase):
    """모듈 Import 테스트 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.import_system = ModuleImportTestSystem()
    
    def test_test_module_import_success(self):
        """성공적인 모듈 import 테스트"""
        # 표준 라이브러리 모듈 테스트
        result = self.import_system.test_module_import("os")
        
        # 검증
        self.assertIsInstance(result, ImportTestResult)
        self.assertTrue(result.success)
        self.assertEqual(result.module_name, "os")
        self.assertGreater(result.execution_time, 0)
    
    def test_test_module_import_failure(self):
        """실패하는 모듈 import 테스트"""
        # 존재하지 않는 모듈 테스트
        result = self.import_system.test_module_import("nonexistent_module_12345")
        
        # 검증
        self.assertIsInstance(result, ImportTestResult)
        self.assertFalse(result.success)
        self.assertEqual(result.module_name, "nonexistent_module_12345")
        self.assertIn("Import 오류", result.message)
    
    def test_generate_import_report(self):
        """Import 테스트 보고서 생성 테스트"""
        # 테스트 결과 설정
        self.import_system.results = [
            ImportTestResult(
                test_name="import_os",
                success=True,
                message="성공",
                module_name="os",
                execution_time=0.1
            ),
            ImportTestResult(
                test_name="import_nonexistent",
                success=False,
                message="실패",
                module_name="nonexistent",
                execution_time=0.05
            )
        ]
        
        # 보고서 생성
        report = self.import_system.generate_import_report()
        
        # 검증
        self.assertIn("summary", report)
        self.assertEqual(report["summary"]["total_modules"], 2)
        self.assertEqual(report["summary"]["successful_imports"], 1)
        self.assertEqual(report["summary"]["failed_imports"], 1)
        self.assertEqual(report["summary"]["success_rate"], 50.0)

class TestFileReferenceIntegritySystem(unittest.TestCase):
    """파일 참조 무결성 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.reference_system = FileReferenceIntegritySystem()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """테스트 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """테스트용 파일 생성"""
        file_path = Path(self.temp_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_scan_file_references(self):
        """파일 참조 스캔 테스트"""
        # 테스트 파일들 생성
        self.create_test_file("main.py", """
import os
from pathlib import Path
import custom_module

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)
""")
        
        self.create_test_file("config.json", '{"test": "value"}')
        
        # 파일 참조 스캔
        references = self.reference_system.scan_file_references(Path(self.temp_dir))
        
        # 검증
        self.assertGreater(len(references), 0)
        
        # import 참조 확인
        import_refs = [r for r in references if r['reference_type'] == 'import']
        self.assertGreater(len(import_refs), 0)
        
        # 파일 경로 참조 확인
        file_refs = [r for r in references if r['reference_type'] == 'file_path']
        self.assertGreater(len(file_refs), 0)
    
    def test_verify_reference_valid_file(self):
        """유효한 파일 참조 검증 테스트"""
        # 실제 파일 생성
        test_file = self.create_test_file("existing.txt", "test content")
        
        # 참조 정보 생성
        reference = {
            'source_file': str(Path(self.temp_dir) / "main.py"),
            'referenced_file': "existing.txt",
            'reference_type': 'file_path'
        }
        
        # 참조 검증
        result = self.reference_system.verify_reference(reference)
        
        # 검증
        self.assertIsInstance(result, FileReferenceTestResult)
        self.assertTrue(result.success)
        self.assertEqual(result.referenced_file, "existing.txt")
    
    def test_verify_reference_missing_file(self):
        """존재하지 않는 파일 참조 검증 테스트"""
        # 참조 정보 생성 (존재하지 않는 파일)
        reference = {
            'source_file': str(Path(self.temp_dir) / "main.py"),
            'referenced_file': "nonexistent.txt",
            'reference_type': 'file_path'
        }
        
        # 참조 검증
        result = self.reference_system.verify_reference(reference)
        
        # 검증
        self.assertIsInstance(result, FileReferenceTestResult)
        self.assertFalse(result.success)
        self.assertIn("파일을 찾을 수 없음", result.message)

class TestPerformanceMonitoringSystem(unittest.TestCase):
    """성능 모니터링 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.performance_system = PerformanceMonitoringSystem()
    
    def test_run_performance_test(self):
        """성능 테스트 실행 테스트"""
        def simple_test():
            """간단한 테스트 함수"""
            time.sleep(0.1)
            return "test completed"
        
        # 성능 테스트 실행
        result = self.performance_system.run_performance_test(simple_test, "simple_test")
        
        # 검증
        self.assertIsInstance(result, PerformanceTestResult)
        self.assertTrue(result.success)
        self.assertEqual(result.test_name, "simple_test")
        self.assertGreaterEqual(result.execution_time, 0.1)
        self.assertGreaterEqual(result.cpu_usage, 0)
        self.assertGreaterEqual(result.memory_usage, 0)
        self.assertIsInstance(result.details, dict)
    
    def test_run_performance_test_with_exception(self):
        """예외가 발생하는 성능 테스트"""
        def failing_test():
            """실패하는 테스트 함수"""
            raise ValueError("Test exception")
        
        # 성능 테스트 실행
        result = self.performance_system.run_performance_test(failing_test, "failing_test")
        
        # 검증
        self.assertIsInstance(result, PerformanceTestResult)
        self.assertFalse(result.success)
        self.assertIn("테스트 실행 실패", result.message)
    
    def test_generate_performance_report(self):
        """성능 테스트 보고서 생성 테스트"""
        # 테스트 결과 설정
        self.performance_system.results = [
            PerformanceTestResult(
                test_name="test1",
                success=True,
                message="성공",
                cpu_usage=25.0,
                memory_usage=30.0,
                execution_time=1.0
            ),
            PerformanceTestResult(
                test_name="test2",
                success=True,
                message="성공",
                cpu_usage=35.0,
                memory_usage=40.0,
                execution_time=2.0
            )
        ]
        
        # 보고서 생성
        report = self.performance_system.generate_performance_report()
        
        # 검증
        self.assertIn("summary", report)
        self.assertEqual(report["summary"]["total_tests"], 2)
        self.assertEqual(report["summary"]["successful_tests"], 2)
        self.assertEqual(report["summary"]["average_cpu_usage"], 30.0)
        self.assertEqual(report["summary"]["average_memory_usage"], 35.0)
        self.assertEqual(report["summary"]["total_execution_time"], 3.0)

class TestComprehensiveTestSystem(unittest.TestCase):
    """종합 테스트 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.comprehensive_system = ComprehensiveTestSystem()
    
    @patch('comprehensive_test_system.SyntaxVerificationSystem')
    @patch('comprehensive_test_system.ModuleImportTestSystem')
    @patch('comprehensive_test_system.FileReferenceIntegritySystem')
    @patch('comprehensive_test_system.PerformanceMonitoringSystem')
    def test_run_all_tests(self, mock_perf, mock_ref, mock_import, mock_syntax):
        """모든 테스트 실행 테스트"""
        # Mock 설정
        mock_syntax_instance = mock_syntax.return_value
        mock_syntax_instance.verify_all_files.return_value = []
        mock_syntax_instance.generate_syntax_report.return_value = {
            'summary': {'success_rate': 100, 'total_files': 10, 'successful_files': 10, 'failed_files': 0}
        }
        
        mock_import_instance = mock_import.return_value
        mock_import_instance.test_all_core_modules.return_value = []
        mock_import_instance.generate_import_report.return_value = {
            'summary': {'success_rate': 100, 'total_modules': 5, 'successful_imports': 5, 'failed_imports': 0}
        }
        
        mock_ref_instance = mock_ref.return_value
        mock_ref_instance.verify_all_references.return_value = []
        mock_ref_instance.generate_integrity_report.return_value = {
            'summary': {'integrity_rate': 100, 'total_references': 20, 'valid_references': 20, 'broken_references': 0}
        }
        
        mock_perf_instance = mock_perf.return_value
        mock_perf_instance.run_performance_test.return_value = PerformanceTestResult(
            test_name="test", success=True, message="성공", cpu_usage=25.0, memory_usage=30.0
        )
        mock_perf_instance.generate_performance_report.return_value = {
            'summary': {'total_tests': 1, 'successful_tests': 1}
        }
        
        # 종합 테스트 실행
        report = self.comprehensive_system.run_all_tests(include_performance=True)
        
        # 검증
        self.assertIn("test_summary", report)
        self.assertIn("detailed_results", report)
        self.assertIn("syntax_verification", report["detailed_results"])
        self.assertIn("module_import", report["detailed_results"])
        self.assertIn("file_reference_integrity", report["detailed_results"])
        self.assertIn("performance_monitoring", report["detailed_results"])
        
        self.assertTrue(report["test_summary"]["overall_success"])
        self.assertGreater(report["test_summary"]["execution_time"], 0)
    
    def test_save_report(self):
        """보고서 저장 테스트"""
        # 테스트 보고서 생성
        test_report = {
            "test_summary": {
                "execution_time": 10.5,
                "timestamp": "2025-01-01T00:00:00",
                "tests_run": 4,
                "overall_success": True
            },
            "detailed_results": {
                "syntax_verification": {"summary": {"success_rate": 100}}
            }
        }
        
        # 임시 파일명으로 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            # 보고서 저장
            saved_filename = self.comprehensive_system.save_report(test_report, temp_filename)
            
            # 검증
            self.assertEqual(saved_filename, temp_filename)
            self.assertTrue(os.path.exists(temp_filename))
            
            # 저장된 내용 확인
            with open(temp_filename, 'r', encoding='utf-8') as f:
                loaded_report = json.load(f)
            
            self.assertEqual(loaded_report["test_summary"]["execution_time"], 10.5)
            self.assertTrue(loaded_report["test_summary"]["overall_success"])
            
        finally:
            # 임시 파일 정리
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

class TestDataModels(unittest.TestCase):
    """데이터 모델 테스트"""
    
    def test_test_result_creation(self):
        """TestResult 생성 테스트"""
        result = TestResult(
            test_name="test",
            success=True,
            message="성공",
            execution_time=1.5
        )
        
        self.assertEqual(result.test_name, "test")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "성공")
        self.assertEqual(result.execution_time, 1.5)
    
    def test_syntax_test_result_creation(self):
        """SyntaxTestResult 생성 테스트"""
        result = SyntaxTestResult(
            test_name="syntax_test",
            success=False,
            message="구문 오류",
            file_path="test.py",
            line_number=10,
            error_type="syntax_error"
        )
        
        self.assertEqual(result.test_name, "syntax_test")
        self.assertFalse(result.success)
        self.assertEqual(result.file_path, "test.py")
        self.assertEqual(result.line_number, 10)
        self.assertEqual(result.error_type, "syntax_error")

def run_test_suite():
    """테스트 스위트 실행"""
    print("🧪 종합 테스트 시스템 단위 테스트 실행")
    print("=" * 50)
    
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스들 추가
    test_classes = [
        TestSyntaxVerificationSystem,
        TestModuleImportTestSystem,
        TestFileReferenceIntegritySystem,
        TestPerformanceMonitoringSystem,
        TestComprehensiveTestSystem,
        TestDataModels
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 50)
    print(f"테스트 실행 완료:")
    print(f"  총 테스트: {result.testsRun}")
    print(f"  성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  실패: {len(result.failures)}")
    print(f"  오류: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ 실패한 테스트들:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n💥 오류가 발생한 테스트들:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ 모든 테스트 통과!' if success else '❌ 일부 테스트 실패'}")
    
    return success

if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)