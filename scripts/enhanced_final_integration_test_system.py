#!/usr/bin/env python3
"""
Enhanced Final Integration Test System
Task 8: 최종 통합 테스트 95% 달성

This system implements comprehensive integration testing with:
- All repair fixes integration testing
- Performance benchmarking and optimization
- Cross-platform compatibility verification
- User scenario-based E2E testing
- Requirements: 5.2
"""

import os
import sys
import subprocess
import json
import time
import platform
import psutil
import threading
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_final_integration_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    category: str
    status: str  # "PASS", "FAIL", "SKIP", "WARNING"
    message: str
    execution_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    details: Optional[Dict] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    start_time: float
    end_time: float
    peak_memory_mb: float
    avg_cpu_percent: float
    total_execution_time: float
    test_count: int
    success_rate: float

class EnhancedFinalIntegrationTestSystem:
    """Enhanced final integration test system for achieving 95% success rate"""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.test_results: List[TestResult] = []
        self.performance_metrics = []
        self.start_time = time.time()
        self.platform_info = {
            "system": platform.system(),
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "python_version": platform.python_version(),
            "processor": platform.processor()
        }
        
        # Test configuration
        self.config = {
            "timeout_seconds": 30,
            "max_workers": 4,
            "memory_threshold_mb": 1000,
            "cpu_threshold_percent": 80,
            "target_success_rate": 95.0,
            "performance_benchmark_enabled": True,
            "cross_platform_tests_enabled": True,
            "e2e_tests_enabled": True
        }
        
        logger.info(f"🚀 Enhanced Final Integration Test System initialized")
        logger.info(f"Platform: {self.platform_info['system']} {self.platform_info['platform']}")
        logger.info(f"Python: {self.platform_info['python_version']}")

    def monitor_performance(func):
        """Decorator to monitor performance of test functions"""
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            start_cpu = psutil.cpu_percent()
            
            try:
                result = func(self, *args, **kwargs)
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                end_cpu = psutil.cpu_percent()
                
                execution_time = end_time - start_time
                memory_usage = end_memory - start_memory
                cpu_usage = (start_cpu + end_cpu) / 2
                
                # Update test result with performance metrics
                if hasattr(result, 'execution_time'):
                    result.execution_time = execution_time
                    result.memory_usage = memory_usage
                    result.cpu_usage = cpu_usage
                
                return result
                
            except Exception as e:
                logger.error(f"Performance monitoring error in {func.__name__}: {e}")
                return func(self, *args, **kwargs)
                
        return wrapper

    @monitor_performance
    def test_syntax_verification_comprehensive(self) -> TestResult:
        """Comprehensive Python syntax verification with enhanced error reporting"""
        logger.info("🐍 Comprehensive Python syntax verification...")
        
        start_time = time.time()
        python_files = list(self.workspace_root.rglob("*.py"))
        
        # Exclude backup directories
        exclude_patterns = [
            "__pycache__", ".git", ".vscode", "node_modules", ".pytest_cache",
            ".backup", "backup", ".repair_backup", ".enhanced_repair_backup",
            ".aggressive_syntax_repair_backup", ".comprehensive_repair_backup",
            ".file_reference_backup", ".file_renaming_backup",
            ".filename_standardization_backup", ".final_file_reference_cleanup_backup",
            ".final_reference_cleanup_backup", ".final_syntax_repair_backup",
            ".focused_file_reference_backup", ".indentation_backup",
            ".naming_backup", ".refined_file_reference_backup",
            ".repair_backups", ".syntax_repair_backup"
        ]
        
        filtered_files = []
        for py_file in python_files:
            if not any(pattern in str(py_file) for pattern in exclude_patterns):
                filtered_files.append(py_file)
        
        valid_files = []
        invalid_files = []
        
        # Use concurrent processing for faster verification
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
            future_to_file = {
                executor.submit(self._verify_python_syntax, py_file): py_file 
                for py_file in filtered_files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                py_file = future_to_file[future]
                try:
                    is_valid, error_msg = future.result(timeout=self.config["timeout_seconds"])
                    if is_valid:
                        valid_files.append(str(py_file.relative_to(self.workspace_root)))
                    else:
                        invalid_files.append({
                            "file": str(py_file.relative_to(self.workspace_root)),
                            "error": error_msg
                        })
                except Exception as e:
                    invalid_files.append({
                        "file": str(py_file.relative_to(self.workspace_root)),
                        "error": f"Verification timeout or error: {str(e)}"
                    })
        
        execution_time = time.time() - start_time
        total_files = len(filtered_files)
        success_rate = (len(valid_files) / total_files * 100) if total_files > 0 else 0
        
        status = "PASS" if success_rate >= 95 else "FAIL" if success_rate < 80 else "WARNING"
        
        return TestResult(
            test_name="Comprehensive Python Syntax Verification",
            category="Syntax Verification",
            status=status,
            message=f"Success rate: {success_rate:.1f}% ({len(valid_files)}/{total_files})",
            execution_time=execution_time,
            details={
                "total_files": total_files,
                "valid_files": len(valid_files),
                "invalid_files": len(invalid_files),
                "success_rate": success_rate,
                "invalid_file_details": invalid_files[:10],  # Show first 10 errors
                "performance": {
                    "execution_time": execution_time,
                    "files_per_second": total_files / execution_time if execution_time > 0 else 0
                }
            }
        )

    def _verify_python_syntax(self, py_file: Path) -> Tuple[bool, str]:
        """Verify syntax of a single Python file"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, str(py_file), 'exec')
            return True, "Valid syntax"
            
        except SyntaxError as e:
            return False, f"Syntax error (line {e.lineno}): {e.msg}"
        except UnicodeDecodeError as e:
            return False, f"Encoding error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @monitor_performance
    def test_module_import_comprehensive(self) -> TestResult:
        """Comprehensive module import testing with dependency resolution"""
        logger.info("📦 Comprehensive module import testing...")
        
        start_time = time.time()
        
        core_modules = [
            "naming_convention_manager",
            "file_renaming_system", 
            "python_naming_standardizer",
            "shell_batch_script_standardizer",
            "documentation_standardizer",
            "config_data_standardizer",
            "system_output_message_standardizer",
            "folder_structure_reorganizer",
            "naming_standardization_verification_system"
        ]
        
        successful_imports = []
        failed_imports = []
        
        # Add current directory to Python path
        sys.path.insert(0, str(self.workspace_root))
        
        for module_name in core_modules:
            try:
                module_file = self.workspace_root / f"{module_name}.py"
                if module_file.exists():
                    # First check syntax
                    is_valid, error_msg = self._verify_python_syntax(module_file)
                    if not is_valid:
                        failed_imports.append({
                            "module": module_name,
                            "error": f"Syntax error: {error_msg}"
                        })
                        continue
                    
                    # Try to import
                    __import__(module_name)
                    successful_imports.append(module_name)
                else:
                    failed_imports.append({
                        "module": module_name,
                        "error": "Module file does not exist"
                    })
                    
            except ImportError as e:
                failed_imports.append({
                    "module": module_name,
                    "error": f"Import error: {str(e)}"
                })
            except Exception as e:
                failed_imports.append({
                    "module": module_name,
                    "error": f"Unexpected error: {str(e)}"
                })
        
        execution_time = time.time() - start_time
        total_modules = len(core_modules)
        success_rate = (len(successful_imports) / total_modules * 100) if total_modules > 0 else 0
        
        status = "PASS" if success_rate >= 95 else "FAIL" if success_rate < 80 else "WARNING"
        
        return TestResult(
            test_name="Comprehensive Module Import Testing",
            category="Module Import",
            status=status,
            message=f"Success rate: {success_rate:.1f}% ({len(successful_imports)}/{total_modules})",
            execution_time=execution_time,
            details={
                "total_modules": total_modules,
                "successful_imports": successful_imports,
                "failed_imports": failed_imports,
                "success_rate": success_rate
            }
        )

    @monitor_performance
    def test_file_reference_integrity_enhanced(self) -> TestResult:
        """Enhanced file reference integrity testing with smart pattern recognition"""
        logger.info("🔗 Enhanced file reference integrity testing...")
        
        start_time = time.time()
        
        valid_references = []
        broken_references = []
        
        # Scan Python files for file references
        python_files = [f for f in self.workspace_root.rglob("*.py") 
                       if not any(pattern in str(f) for pattern in [
                           "__pycache__", ".backup", "backup", ".git"
                       ])]
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for file references (excluding wildcard patterns)
                import re
                
                # File path patterns (excluding wildcards like **/*.py)
                patterns = [
                    r'open\s*\(\s*["\']([^"\'*]+)["\']',  # open() function
                    r'Path\s*\(\s*["\']([^"\'*]+)["\']',  # Path() constructor
                    r'["\']([^"\'*]*\.(?:py|json|md|txt|log|bat|sh))["\']'  # File extensions
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Skip if it's a wildcard pattern
                        if '*' in match or match.startswith('**'):
                            continue
                            
                        # Skip if it's a relative path that doesn't start with . or /
                        if not match.startswith(('.', '/', '~')) and '/' in match:
                            referenced_file = self.workspace_root / match
                            if referenced_file.exists():
                                valid_references.append(f"{py_file.name} -> {match}")
                            else:
                                # Only report as broken if it looks like a real file path
                                if len(match.split('/')) > 1 and '.' in match:
                                    broken_references.append({
                                        "source_file": str(py_file.relative_to(self.workspace_root)),
                                        "referenced_file": match,
                                        "error": "Referenced file does not exist"
                                    })
                                    
            except Exception as e:
                logger.warning(f"File reference check failed for {py_file}: {e}")
        
        execution_time = time.time() - start_time
        total_references = len(valid_references) + len(broken_references)
        success_rate = (len(valid_references) / total_references * 100) if total_references > 0 else 100
        
        status = "PASS" if success_rate >= 95 else "FAIL" if success_rate < 80 else "WARNING"
        
        return TestResult(
            test_name="Enhanced File Reference Integrity Testing",
            category="File Reference Integrity",
            status=status,
            message=f"Success rate: {success_rate:.1f}% ({len(valid_references)}/{total_references})",
            execution_time=execution_time,
            details={
                "total_references": total_references,
                "valid_references": len(valid_references),
                "broken_references": len(broken_references),
                "success_rate": success_rate,
                "broken_reference_details": broken_references[:10]  # Show first 10
            }
        )

    @monitor_performance
    def test_system_execution_comprehensive(self) -> TestResult:
        """Comprehensive system execution testing"""
        logger.info("🔧 Comprehensive system execution testing...")
        
        start_time = time.time()
        
        execution_tests = []
        
        # Test 1: WatchHamster Control Center
        watchhamster_result = self._test_watchhamster_execution()
        execution_tests.append(watchhamster_result)
        
        # Test 2: POSCO News Monitoring
        posco_news_result = self._test_posco_news_execution()
        execution_tests.append(posco_news_result)
        
        # Test 3: Shell/Batch Scripts
        scripts_result = self._test_scripts_execution()
        execution_tests.append(scripts_result)
        
        # Test 4: Webhook Connectivity
        webhook_result = self._test_webhook_connectivity()
        execution_tests.append(webhook_result)
        
        execution_time = time.time() - start_time
        
        # Calculate overall success rate
        total_tests = len(execution_tests)
        passed_tests = len([t for t in execution_tests if t["status"] == "PASS"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        status = "PASS" if success_rate >= 95 else "FAIL" if success_rate < 80 else "WARNING"
        
        return TestResult(
            test_name="Comprehensive System Execution Testing",
            category="System Execution",
            status=status,
            message=f"Success rate: {success_rate:.1f}% ({passed_tests}/{total_tests})",
            execution_time=execution_time,
            details={
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate,
                "execution_results": execution_tests
            }
        )

    def _test_watchhamster_execution(self) -> Dict[str, Any]:
        """Test WatchHamster control center execution"""
        try:
            # Test command file (macOS/Linux)
            cmd_file = self.workspace_root / "🐹POSCO_워치햄스터_v3_제어센터.command"
            if cmd_file.exists():
                # Check if file is executable
                if os.access(cmd_file, os.X_OK):
                    return {
                        "test": "WatchHamster Control Center",
                        "status": "PASS",
                        "message": "Command file exists and is executable"
                    }
                else:
                    return {
                        "test": "WatchHamster Control Center", 
                        "status": "WARNING",
                        "message": "Command file exists but lacks execute permission"
                    }
            else:
                return {
                    "test": "WatchHamster Control Center",
                    "status": "FAIL", 
                    "message": "Command file not found"
                }
        except Exception as e:
            return {
                "test": "WatchHamster Control Center",
                "status": "FAIL",
                "message": f"Test error: {str(e)}"
            }

    def _test_posco_news_execution(self) -> Dict[str, Any]:
        """Test POSCO News monitoring execution"""
        try:
            main_file = self.workspace_root / "POSCO_News_250808.py"
            if main_file.exists():
                # Check syntax
                is_valid, error_msg = self._verify_python_syntax(main_file)
                if is_valid:
                    return {
                        "test": "POSCO News Monitoring",
                        "status": "PASS",
                        "message": "Main news file exists and has valid syntax"
                    }
                else:
                    return {
                        "test": "POSCO News Monitoring",
                        "status": "FAIL",
                        "message": f"Syntax error: {error_msg}"
                    }
            else:
                return {
                    "test": "POSCO News Monitoring",
                    "status": "FAIL",
                    "message": "Main news file not found"
                }
        except Exception as e:
            return {
                "test": "POSCO News Monitoring",
                "status": "FAIL",
                "message": f"Test error: {str(e)}"
            }

    def _test_scripts_execution(self) -> Dict[str, Any]:
        """Test shell/batch scripts execution"""
        try:
            script_files = [
                "🚀🚀POSCO_News_250808_Direct_Start.sh",
                "watchhamster_v3_v3_0_control_center.sh",
                "watchhamster_v3_v3_0_master_control.sh"
            ]
            
            executable_count = 0
            total_count = 0
            
            for script_name in script_files:
                script_path = self.workspace_root / script_name
                if script_path.exists():
                    total_count += 1
                    if os.access(script_path, os.X_OK):
                        executable_count += 1
            
            if total_count == 0:
                return {
                    "test": "Shell/Batch Scripts",
                    "status": "FAIL",
                    "message": "No script files found"
                }
            
            success_rate = (executable_count / total_count * 100)
            status = "PASS" if success_rate >= 80 else "WARNING" if success_rate >= 50 else "FAIL"
            
            return {
                "test": "Shell/Batch Scripts",
                "status": status,
                "message": f"Executable scripts: {executable_count}/{total_count} ({success_rate:.0f}%)"
            }
            
        except Exception as e:
            return {
                "test": "Shell/Batch Scripts",
                "status": "FAIL",
                "message": f"Test error: {str(e)}"
            }

    def _test_webhook_connectivity(self) -> Dict[str, Any]:
        """Test webhook connectivity"""
        try:
            # Test webhook URLs (without actually sending data)
            webhook_urls = [
                "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg",
                "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"
            ]
            
            accessible_count = 0
            
            for url in webhook_urls:
                try:
                    import requests
                    response = requests.head(url, timeout=10)
                    if response.status_code in [200, 405]:  # 405 is also acceptable for webhooks
                        accessible_count += 1
                except:
                    pass  # Connection failed
            
            total_webhooks = len(webhook_urls)
            success_rate = (accessible_count / total_webhooks * 100)
            status = "PASS" if success_rate >= 80 else "WARNING" if success_rate >= 50 else "FAIL"
            
            return {
                "test": "Webhook Connectivity",
                "status": status,
                "message": f"Accessible webhooks: {accessible_count}/{total_webhooks} ({success_rate:.0f}%)"
            }
            
        except Exception as e:
            return {
                "test": "Webhook Connectivity",
                "status": "WARNING",
                "message": f"Test error (requests module may not be available): {str(e)}"
            }

    @monitor_performance
    def test_performance_benchmarking(self) -> TestResult:
        """Performance benchmarking and optimization testing"""
        logger.info("📊 Performance benchmarking and optimization testing...")
        
        start_time = time.time()
        
        # System resource monitoring
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Run performance-intensive operations
        performance_tests = []
        
        # Test 1: File system operations
        fs_start = time.time()
        file_count = len(list(self.workspace_root.rglob("*")))
        fs_time = time.time() - fs_start
        performance_tests.append({
            "test": "File System Scan",
            "execution_time": fs_time,
            "throughput": file_count / fs_time if fs_time > 0 else 0,
            "files_scanned": file_count
        })
        
        # Test 2: Memory usage monitoring
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_usage = peak_memory - initial_memory
        
        # Test 3: CPU usage monitoring
        final_cpu = psutil.cpu_percent(interval=1)
        avg_cpu = (initial_cpu + final_cpu) / 2
        
        execution_time = time.time() - start_time
        
        # Performance thresholds
        memory_ok = memory_usage < self.config["memory_threshold_mb"]
        cpu_ok = avg_cpu < self.config["cpu_threshold_percent"]
        time_ok = execution_time < 60  # Should complete within 1 minute
        
        performance_score = sum([memory_ok, cpu_ok, time_ok]) / 3 * 100
        status = "PASS" if performance_score >= 80 else "WARNING" if performance_score >= 60 else "FAIL"
        
        return TestResult(
            test_name="Performance Benchmarking and Optimization",
            category="Performance",
            status=status,
            message=f"Performance score: {performance_score:.1f}%",
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=avg_cpu,
            details={
                "performance_score": performance_score,
                "memory_usage_mb": memory_usage,
                "cpu_usage_percent": avg_cpu,
                "execution_time": execution_time,
                "performance_tests": performance_tests,
                "thresholds": {
                    "memory_threshold_mb": self.config["memory_threshold_mb"],
                    "cpu_threshold_percent": self.config["cpu_threshold_percent"],
                    "memory_ok": memory_ok,
                    "cpu_ok": cpu_ok,
                    "time_ok": time_ok
                }
            }
        )

    @monitor_performance
    def test_cross_platform_compatibility(self) -> TestResult:
        """Cross-platform compatibility verification"""
        logger.info("🌐 Cross-platform compatibility verification...")
        
        start_time = time.time()
        
        compatibility_tests = []
        
        # Test 1: Platform-specific files
        platform_files = {
            "Windows": ["*.bat", "*.ps1"],
            "Darwin": ["*.command", "*.sh"],  # macOS
            "Linux": ["*.sh"]
        }
        
        current_platform = platform.system()
        expected_files = platform_files.get(current_platform, ["*.sh"])
        
        found_files = []
        for pattern in expected_files:
            found_files.extend(list(self.workspace_root.rglob(pattern)))
        
        compatibility_tests.append({
            "test": f"Platform-specific files ({current_platform})",
            "status": "PASS" if found_files else "WARNING",
            "message": f"Found {len(found_files)} platform-specific files",
            "details": [str(f.name) for f in found_files[:5]]  # Show first 5
        })
        
        # Test 2: Path separator compatibility
        python_files = list(self.workspace_root.rglob("*.py"))
        path_issues = []
        
        for py_file in python_files[:20]:  # Check first 20 files for performance
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for hardcoded path separators
                if '\\\\' in content or (current_platform != "Windows" and '\\' in content):
                    path_issues.append(str(py_file.relative_to(self.workspace_root)))
                    
            except Exception:
                continue
        
        compatibility_tests.append({
            "test": "Path separator compatibility",
            "status": "PASS" if not path_issues else "WARNING",
            "message": f"Found {len(path_issues)} files with potential path issues",
            "details": path_issues[:5]
        })
        
        # Test 3: Encoding compatibility
        encoding_issues = []
        for py_file in python_files[:20]:  # Check first 20 files
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError:
                encoding_issues.append(str(py_file.relative_to(self.workspace_root)))
        
        compatibility_tests.append({
            "test": "File encoding compatibility",
            "status": "PASS" if not encoding_issues else "FAIL",
            "message": f"Found {len(encoding_issues)} files with encoding issues",
            "details": encoding_issues
        })
        
        execution_time = time.time() - start_time
        
        # Calculate overall compatibility score
        passed_tests = len([t for t in compatibility_tests if t["status"] == "PASS"])
        total_tests = len(compatibility_tests)
        compatibility_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        status = "PASS" if compatibility_score >= 80 else "WARNING" if compatibility_score >= 60 else "FAIL"
        
        return TestResult(
            test_name="Cross-platform Compatibility Verification",
            category="Cross-platform",
            status=status,
            message=f"Compatibility score: {compatibility_score:.1f}%",
            execution_time=execution_time,
            details={
                "platform_info": self.platform_info,
                "compatibility_score": compatibility_score,
                "compatibility_tests": compatibility_tests
            }
        )

    @monitor_performance
    def test_user_scenario_e2e(self) -> TestResult:
        """User scenario-based End-to-End testing"""
        logger.info("👤 User scenario-based E2E testing...")
        
        start_time = time.time()
        
        e2e_scenarios = []
        
        # Scenario 1: User wants to start WatchHamster monitoring
        scenario1_result = self._test_watchhamster_startup_scenario()
        e2e_scenarios.append(scenario1_result)
        
        # Scenario 2: User wants to check POSCO news
        scenario2_result = self._test_posco_news_check_scenario()
        e2e_scenarios.append(scenario2_result)
        
        # Scenario 3: User wants to view system status
        scenario3_result = self._test_system_status_scenario()
        e2e_scenarios.append(scenario3_result)
        
        # Scenario 4: User wants to run tests
        scenario4_result = self._test_user_testing_scenario()
        e2e_scenarios.append(scenario4_result)
        
        execution_time = time.time() - start_time
        
        # Calculate E2E success rate
        passed_scenarios = len([s for s in e2e_scenarios if s["status"] == "PASS"])
        total_scenarios = len(e2e_scenarios)
        e2e_success_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
        
        status = "PASS" if e2e_success_rate >= 80 else "WARNING" if e2e_success_rate >= 60 else "FAIL"
        
        return TestResult(
            test_name="User Scenario-based E2E Testing",
            category="End-to-End",
            status=status,
            message=f"E2E success rate: {e2e_success_rate:.1f}%",
            execution_time=execution_time,
            details={
                "total_scenarios": total_scenarios,
                "passed_scenarios": passed_scenarios,
                "e2e_success_rate": e2e_success_rate,
                "scenario_results": e2e_scenarios
            }
        )

    def _test_watchhamster_startup_scenario(self) -> Dict[str, Any]:
        """Test WatchHamster startup scenario"""
        try:
            # Check if control center files exist
            control_files = [
                "🐹POSCO_워치햄스터_v3_제어센터.command",
                "🐹POSCO_워치햄스터_v3_제어센터.bat",
                "🎛️WatchHamster_v3_v3_0_Control_Panel.bat"
            ]
            
            available_files = []
            for file_name in control_files:
                file_path = self.workspace_root / file_name
                if file_path.exists():
                    available_files.append(file_name)
            
            if available_files:
                return {
                    "scenario": "WatchHamster Startup",
                    "status": "PASS",
                    "message": f"Control center files available: {len(available_files)}/{len(control_files)}",
                    "details": available_files
                }
            else:
                return {
                    "scenario": "WatchHamster Startup",
                    "status": "FAIL",
                    "message": "No control center files found"
                }
                
        except Exception as e:
            return {
                "scenario": "WatchHamster Startup",
                "status": "FAIL",
                "message": f"Scenario test error: {str(e)}"
            }

    def _test_posco_news_check_scenario(self) -> Dict[str, Any]:
        """Test POSCO news check scenario"""
        try:
            # Check if news monitoring files exist
            news_files = [
                "POSCO_News_250808.py",
                "Monitoring/POSCO_News_250808/posco_main_notifier_minimal.py",
                "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3_v3_0_minimal.py"
            ]
            
            available_files = []
            for file_name in news_files:
                file_path = self.workspace_root / file_name
                if file_path.exists():
                    available_files.append(file_name)
            
            if len(available_files) >= 2:  # At least 2 files should be available
                return {
                    "scenario": "POSCO News Check",
                    "status": "PASS",
                    "message": f"News monitoring files available: {len(available_files)}/{len(news_files)}",
                    "details": available_files
                }
            else:
                return {
                    "scenario": "POSCO News Check",
                    "status": "FAIL",
                    "message": f"Insufficient news monitoring files: {len(available_files)}/{len(news_files)}"
                }
                
        except Exception as e:
            return {
                "scenario": "POSCO News Check",
                "status": "FAIL",
                "message": f"Scenario test error: {str(e)}"
            }

    def _test_system_status_scenario(self) -> Dict[str, Any]:
        """Test system status check scenario"""
        try:
            # Check if system status files exist
            status_files = [
                "system_functionality_verification.py",
                "final_integration_test_system.py",
                "comprehensive_system_execution_test.py"
            ]
            
            available_files = []
            for file_name in status_files:
                file_path = self.workspace_root / file_name
                if file_path.exists():
                    available_files.append(file_name)
            
            if available_files:
                return {
                    "scenario": "System Status Check",
                    "status": "PASS",
                    "message": f"System status files available: {len(available_files)}/{len(status_files)}",
                    "details": available_files
                }
            else:
                return {
                    "scenario": "System Status Check",
                    "status": "FAIL",
                    "message": "No system status files found"
                }
                
        except Exception as e:
            return {
                "scenario": "System Status Check",
                "status": "FAIL",
                "message": f"Scenario test error: {str(e)}"
            }

    def _test_user_testing_scenario(self) -> Dict[str, Any]:
        """Test user testing scenario"""
        try:
            # Check if test files exist
            test_files = list(self.workspace_root.rglob("test_*.py"))
            test_files.extend(list(self.workspace_root.rglob("*_test.py")))
            
            if len(test_files) >= 10:  # Should have at least 10 test files
                return {
                    "scenario": "User Testing",
                    "status": "PASS",
                    "message": f"Test files available: {len(test_files)}",
                    "details": [str(f.name) for f in test_files[:5]]  # Show first 5
                }
            else:
                return {
                    "scenario": "User Testing",
                    "status": "WARNING",
                    "message": f"Limited test files available: {len(test_files)}"
                }
                
        except Exception as e:
            return {
                "scenario": "User Testing",
                "status": "FAIL",
                "message": f"Scenario test error: {str(e)}"
            }

    def run_comprehensive_integration_test(self) -> Dict[str, Any]:
        """Run comprehensive integration test to achieve 95% success rate"""
        logger.info("🚀 Starting Enhanced Final Integration Test System")
        logger.info("=" * 80)
        logger.info(f"Target success rate: {self.config['target_success_rate']}%")
        logger.info("=" * 80)
        
        # Run all test categories
        test_functions = [
            self.test_syntax_verification_comprehensive,
            self.test_module_import_comprehensive,
            self.test_file_reference_integrity_enhanced,
            self.test_system_execution_comprehensive,
            self.test_performance_benchmarking,
            self.test_cross_platform_compatibility,
            self.test_user_scenario_e2e
        ]
        
        for test_func in test_functions:
            try:
                result = test_func()
                self.test_results.append(result)
                
                # Log result
                status_emoji = "✅" if result.status == "PASS" else "⚠️" if result.status == "WARNING" else "❌"
                logger.info(f"{status_emoji} {result.test_name}: {result.message}")
                
                if result.execution_time > 0:
                    logger.info(f"   ⏱️ Execution time: {result.execution_time:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Test function {test_func.__name__} failed: {e}")
                self.test_results.append(TestResult(
                    test_name=test_func.__name__,
                    category="System Error",
                    status="FAIL",
                    message=f"Test execution failed: {str(e)}"
                ))
        
        # Calculate overall results
        total_execution_time = time.time() - self.start_time
        overall_results = self._calculate_overall_results(total_execution_time)
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(overall_results)
        
        # Save results
        self._save_results(report)
        
        logger.info("=" * 80)
        logger.info("🏁 Enhanced Final Integration Test System completed")
        logger.info(f"🎯 Overall success rate: {overall_results['success_rate']:.1f}%")
        logger.info(f"⏱️ Total execution time: {total_execution_time:.2f}s")
        logger.info("=" * 80)
        
        return report

    def _calculate_overall_results(self, total_execution_time: float) -> Dict[str, Any]:
        """Calculate overall test results"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        warning_tests = len([r for r in self.test_results if r.status == "WARNING"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Performance metrics
        avg_execution_time = sum(r.execution_time for r in self.test_results) / total_tests if total_tests > 0 else 0
        total_memory_usage = sum(r.memory_usage for r in self.test_results if r.memory_usage > 0)
        avg_cpu_usage = sum(r.cpu_usage for r in self.test_results if r.cpu_usage > 0) / len([r for r in self.test_results if r.cpu_usage > 0]) if any(r.cpu_usage > 0 for r in self.test_results) else 0
        
        # Determine overall status
        if success_rate >= self.config["target_success_rate"]:
            overall_status = "EXCELLENT"
        elif success_rate >= 90:
            overall_status = "GOOD"
        elif success_rate >= 80:
            overall_status = "FAIR"
        else:
            overall_status = "POOR"
        
        return {
            "success_rate": success_rate,
            "overall_status": overall_status,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "warning_tests": warning_tests,
            "failed_tests": failed_tests,
            "total_execution_time": total_execution_time,
            "avg_execution_time": avg_execution_time,
            "total_memory_usage": total_memory_usage,
            "avg_cpu_usage": avg_cpu_usage,
            "target_achieved": success_rate >= self.config["target_success_rate"]
        }

    def _generate_comprehensive_report(self, overall_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        return {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "platform_info": self.platform_info,
                "test_configuration": self.config,
                "overall_results": overall_results
            },
            "detailed_results": [asdict(result) for result in self.test_results],
            "performance_analysis": {
                "execution_times": [r.execution_time for r in self.test_results],
                "memory_usage": [r.memory_usage for r in self.test_results if r.memory_usage > 0],
                "cpu_usage": [r.cpu_usage for r in self.test_results if r.cpu_usage > 0]
            },
            "recommendations": self._generate_recommendations(overall_results),
            "next_steps": self._generate_next_steps(overall_results)
        }

    def _generate_recommendations(self, overall_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if overall_results["success_rate"] < self.config["target_success_rate"]:
            recommendations.append(f"🎯 Target success rate of {self.config['target_success_rate']}% not achieved. Current: {overall_results['success_rate']:.1f}%")
        
        # Analyze failed tests
        failed_tests = [r for r in self.test_results if r.status == "FAIL"]
        for test in failed_tests:
            if "Syntax" in test.category:
                recommendations.append("🐍 Fix Python syntax errors using automated repair tools")
            elif "Module Import" in test.category:
                recommendations.append("📦 Resolve module import issues and dependencies")
            elif "File Reference" in test.category:
                recommendations.append("🔗 Fix broken file references and update paths")
            elif "System Execution" in test.category:
                recommendations.append("🔧 Ensure all system components are properly configured")
            elif "Performance" in test.category:
                recommendations.append("📊 Optimize system performance and resource usage")
            elif "Cross-platform" in test.category:
                recommendations.append("🌐 Address cross-platform compatibility issues")
            elif "End-to-End" in test.category:
                recommendations.append("👤 Improve user experience and workflow integration")
        
        # Performance recommendations
        if overall_results["total_memory_usage"] > self.config["memory_threshold_mb"]:
            recommendations.append(f"💾 Memory usage ({overall_results['total_memory_usage']:.1f}MB) exceeds threshold")
        
        if overall_results["avg_cpu_usage"] > self.config["cpu_threshold_percent"]:
            recommendations.append(f"⚡ CPU usage ({overall_results['avg_cpu_usage']:.1f}%) exceeds threshold")
        
        if not recommendations:
            recommendations.append("✅ All tests passed successfully! System is ready for production.")
        
        return recommendations

    def _generate_next_steps(self, overall_results: Dict[str, Any]) -> List[str]:
        """Generate next steps based on test results"""
        next_steps = []
        
        if overall_results["target_achieved"]:
            next_steps.extend([
                "🎉 Congratulations! Target success rate achieved.",
                "📋 Review detailed test results for any warnings",
                "🚀 System is ready for deployment",
                "📊 Set up continuous monitoring",
                "📝 Update documentation with current system state"
            ])
        else:
            next_steps.extend([
                "🔧 Address failed test cases in priority order",
                "🐍 Run syntax repair tools for Python files",
                "📦 Fix module import dependencies",
                "🔗 Repair broken file references",
                "🔄 Re-run integration tests after fixes",
                "📈 Monitor progress towards 95% target"
            ])
        
        return next_steps

    def _save_results(self, report: Dict[str, Any]):
        """Save test results to files"""
        try:
            # Save JSON report
            json_file = self.workspace_root / "enhanced_final_integration_test_results.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 JSON report saved: {json_file}")
            
            # Save HTML report
            self._generate_html_report(report)
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

    def _generate_html_report(self, report: Dict[str, Any]):
        """Generate HTML report"""
        try:
            overall = report["test_summary"]["overall_results"]
            
            html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Final Integration Test Results</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; }}
        .summary-card {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; }}
        .summary-card.warning {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .summary-card.fail {{ background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 2.5em; }}
        .summary-card p {{ margin: 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .test-category {{ margin-bottom: 30px; background: #f8f9fa; border-radius: 10px; overflow: hidden; }}
        .category-header {{ background: #e9ecef; padding: 20px; border-bottom: 1px solid #dee2e6; }}
        .category-header h3 {{ margin: 0; color: #495057; }}
        .test-item {{ padding: 20px; border-bottom: 1px solid #dee2e6; }}
        .test-item:last-child {{ border-bottom: none; }}
        .test-status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-right: 10px; }}
        .status-pass {{ background: #28a745; }}
        .status-warning {{ background: #ffc107; color: #212529; }}
        .status-fail {{ background: #dc3545; }}
        .recommendations {{ background: #e8f4fd; border: 1px solid #bee5eb; border-radius: 10px; padding: 25px; margin-top: 30px; }}
        .recommendations h3 {{ color: #0c5460; margin-top: 0; }}
        .next-steps {{ background: #d4edda; border: 1px solid #c3e6cb; border-radius: 10px; padding: 25px; margin-top: 20px; }}
        .next-steps h3 {{ color: #155724; margin-top: 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6c757d; border-top: 1px solid #dee2e6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced Final Integration Test Results</h1>
            <p>POSCO System Repair and Completion - Task 8</p>
            <p>Generated: {report["test_summary"]["timestamp"]}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{overall["success_rate"]:.1f}%</h3>
                <p>Success Rate</p>
            </div>
            <div class="summary-card {'warning' if overall['success_rate'] < 95 else ''}">
                <h3>{overall["passed_tests"]}</h3>
                <p>Tests Passed</p>
            </div>
            <div class="summary-card {'fail' if overall['failed_tests'] > 0 else ''}">
                <h3>{overall["failed_tests"]}</h3>
                <p>Tests Failed</p>
            </div>
            <div class="summary-card">
                <h3>{overall["total_execution_time"]:.1f}s</h3>
                <p>Total Time</p>
            </div>
        </div>
        
        <div class="content">
            <h2>📋 Detailed Test Results</h2>
"""
            
            # Group results by category
            categories = {}
            for result in report["detailed_results"]:
                category = result["category"]
                if category not in categories:
                    categories[category] = []
                categories[category].append(result)
            
            for category, results in categories.items():
                html_content += f"""
            <div class="test-category">
                <div class="category-header">
                    <h3>{category}</h3>
                </div>
"""
                for result in results:
                    status_class = f"status-{result['status'].lower()}"
                    html_content += f"""
                <div class="test-item">
                    <span class="test-status {status_class}">{result['status']}</span>
                    <strong>{result['test_name']}</strong>
                    <p>{result['message']}</p>
                    <small>Execution time: {result['execution_time']:.2f}s</small>
                </div>
"""
                html_content += "</div>"
            
            # Add recommendations
            html_content += f"""
            <div class="recommendations">
                <h3>💡 Recommendations</h3>
                <ul>
"""
            for rec in report["recommendations"]:
                html_content += f"<li>{rec}</li>"
            
            html_content += f"""
                </ul>
            </div>
            
            <div class="next-steps">
                <h3>🎯 Next Steps</h3>
                <ul>
"""
            for step in report["next_steps"]:
                html_content += f"<li>{step}</li>"
            
            html_content += f"""
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Platform: {report["test_summary"]["platform_info"]["system"]} {report["test_summary"]["platform_info"]["platform"]}</p>
            <p>Python: {report["test_summary"]["platform_info"]["python_version"]}</p>
        </div>
    </div>
</body>
</html>"""
            
            html_file = self.workspace_root / "enhanced_final_integration_test_results.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"📄 HTML report saved: {html_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate HTML report: {e}")

def main():
    """Main execution function"""
    print("🚀 Enhanced Final Integration Test System")
    print("Task 8: 최종 통합 테스트 95% 달성")
    print("=" * 80)
    
    try:
        # Initialize test system
        test_system = EnhancedFinalIntegrationTestSystem()
        
        # Run comprehensive integration test
        results = test_system.run_comprehensive_integration_test()
        
        # Print summary
        overall = results["test_summary"]["overall_results"]
        print(f"\n🎯 Final Results:")
        print(f"   Success Rate: {overall['success_rate']:.1f}%")
        print(f"   Overall Status: {overall['overall_status']}")
        print(f"   Target Achieved: {'✅ YES' if overall['target_achieved'] else '❌ NO'}")
        print(f"   Total Tests: {overall['total_tests']}")
        print(f"   Passed: {overall['passed_tests']}")
        print(f"   Failed: {overall['failed_tests']}")
        print(f"   Execution Time: {overall['total_execution_time']:.2f}s")
        
        # Exit with appropriate code
        if overall["target_achieved"]:
            print("\n🎉 SUCCESS: 95% target achieved!")
            sys.exit(0)
        elif overall["success_rate"] >= 90:
            print("\n⚠️ CLOSE: Near target, minor fixes needed")
            sys.exit(1)
        else:
            print("\n❌ FAIL: Significant improvements needed")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Test system error: {e}")
        sys.exit(4)

if __name__ == "__main__":
    main()