#!/usr/bin/env python3
"""
POSCO 시스템 배포 준비 및 최종 검증 시스템
Production deployment preparation and final verification system
"""

import os
import sys
import json
import time
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

@dataclass
class DeploymentCheck:
    """배포 검증 항목"""
    name: str
    description: str
    status: str  # 'pending', 'passed', 'failed', 'warning'
    details: str
    timestamp: str
    
@dataclass
class SecurityCheck:
    """보안 검증 항목"""
    check_type: str
    file_path: str
    issue_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    recommendation: str

@dataclass
class PerformanceMetric:
    """성능 측정 항목"""
    metric_name: str
    value: float
    unit: str
    threshold: float
    status: str  # 'good', 'warning', 'critical'

class DeploymentPreparationSystem:
    """배포 준비 시스템"""
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.deployment_checks = []
        self.security_checks = []
        self.performance_metrics = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def run_full_deployment_preparation(self) -> Dict[str, Any]:
        """전체 배포 준비 프로세스 실행"""
        print("🚀 POSCO 시스템 배포 준비 시작...")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'timestamp': self.timestamp,
            'deployment_checks': [],
            'security_checks': [],
            'performance_metrics': [],
            'overall_status': 'pending'
        }
        
        try:
            # 1. 프로덕션 환경 배포 준비
            print("\n📦 1. 프로덕션 환경 배포 준비...")
            self._prepare_production_environment()
            
            # 2. 최종 성능 테스트 및 최적화
            print("\n⚡ 2. 최종 성능 테스트 및 최적화...")
            self._run_performance_tests()
            
            # 3. 보안 검토 및 취약점 점검
            print("\n🔒 3. 보안 검토 및 취약점 점검...")
            self._run_security_audit()    
        
            # 4. 운영 매뉴얼 및 체크리스트 완성
            print("\n📋 4. 운영 매뉴얼 및 체크리스트 완성...")
            self._generate_operational_documentation()
            
            # 결과 수집 및 보고서 생성
            results['deployment_checks'] = [asdict(check) for check in self.deployment_checks]
            results['security_checks'] = [asdict(check) for check in self.security_checks]
            results['performance_metrics'] = [asdict(metric) for metric in self.performance_metrics]
            
            # 전체 상태 결정
            results['overall_status'] = self._determine_overall_status()
            
            # 보고서 생성
            self._generate_deployment_report(results)
            
            print(f"\n✅ 배포 준비 완료! 전체 상태: {results['overall_status']}")
            return results
            
        except Exception as e:
            print(f"❌ 배포 준비 중 오류 발생: {str(e)}")
            results['overall_status'] = 'failed'
            results['error'] = str(e)
            return results
    
    def _prepare_production_environment(self):
        """프로덕션 환경 배포 준비"""
        
        # 1. 시스템 파일 무결성 검증
        self._check_system_integrity()
        
        # 2. 의존성 검증
        self._verify_dependencies()
        
        # 3. 설정 파일 검증
        self._verify_configuration_files()
        
        # 4. 실행 권한 검증
        self._verify_execution_permissions()
        
        # 5. 백업 시스템 준비
        self._prepare_backup_system()
    
    def _check_system_integrity(self):
        """시스템 파일 무결성 검증"""
        try:
            # 핵심 Python 파일들 구문 검증
            python_files = list(self.base_path.glob("*.py"))
            failed_files = []
            
            for py_file in python_files:
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', str(py_file)
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode != 0:
                        failed_files.append(str(py_file))
                except subprocess.TimeoutExpired:
                    failed_files.append(f"{py_file} (timeout)")
            
            if failed_files:
                self.deployment_checks.append(DeploymentCheck(
                    name="Python 파일 구문 검증",
                    description="Python 파일들의 구문 오류 검사",
                    status="failed",
                    details=f"구문 오류 파일: {', '.join(failed_files)}",
                    timestamp=datetime.now().isoformat()
                ))
            else:
                self.deployment_checks.append(DeploymentCheck(
                    name="Python 파일 구문 검증",
                    description="Python 파일들의 구문 오류 검사",
                    status="passed",
                    details=f"검증된 파일 수: {len(python_files)}",
                    timestamp=datetime.now().isoformat()
                ))
                
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="시스템 무결성 검증",
                description="시스템 파일 무결성 검사",
                status="failed",
                details=f"검증 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            ))
    
    def _verify_dependencies(self):
        """의존성 검증"""
        try:
            # 핵심 모듈 import 테스트
            critical_modules = [
                'naming_convention_manager',
                'file_renaming_system',
                'python_naming_standardizer',
                'shell_batch_script_standardizer',
                'documentation_standardizer'
            ]
            
            failed_imports = []
            for module in critical_modules:
                module_file = self.base_path / f"{module}.py"
                if module_file.exists():
                    try:
                        result = subprocess.run([
                            sys.executable, '-c', f'import {module}'
                        ], capture_output=True, text=True, timeout=10, cwd=self.base_path)
                        
                        if result.returncode != 0:
                            failed_imports.append(f"{module}: {result.stderr.strip()}")
                    except subprocess.TimeoutExpired:
                        failed_imports.append(f"{module}: timeout")
                else:
                    failed_imports.append(f"{module}: file not found")
            
            if failed_imports:
                self.deployment_checks.append(DeploymentCheck(
                    name="모듈 의존성 검증",
                    description="핵심 모듈들의 import 가능성 검사",
                    status="failed",
                    details=f"실패한 모듈: {'; '.join(failed_imports)}",
                    timestamp=datetime.now().isoformat()
                ))
            else:
                self.deployment_checks.append(DeploymentCheck(
                    name="모듈 의존성 검증",
                    description="핵심 모듈들의 import 가능성 검사",
                    status="passed",
                    details=f"검증된 모듈 수: {len(critical_modules)}",
                    timestamp=datetime.now().isoformat()
                ))
                
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="의존성 검증",
                description="시스템 의존성 검사",
                status="failed",
                details=f"검증 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            ))    

    def _verify_configuration_files(self):
        """설정 파일 검증"""
        try:
            config_files = [
                'config.py',
                'comprehensive_test_config.json',
                'repair_config.json'
            ]
            
            missing_configs = []
            invalid_configs = []
            
            for config_file in config_files:
                config_path = self.base_path / config_file
                if not config_path.exists():
                    missing_configs.append(config_file)
                    continue
                
                # JSON 파일 유효성 검증
                if config_file.endswith('.json'):
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                    except json.JSONDecodeError as e:
                        invalid_configs.append(f"{config_file}: {str(e)}")
            
            status = "passed"
            details = f"검증된 설정 파일 수: {len(config_files) - len(missing_configs) - len(invalid_configs)}"
            
            if missing_configs or invalid_configs:
                status = "warning"
                issues = []
                if missing_configs:
                    issues.append(f"누락된 파일: {', '.join(missing_configs)}")
                if invalid_configs:
                    issues.append(f"잘못된 파일: {', '.join(invalid_configs)}")
                details = "; ".join(issues)
            
            self.deployment_checks.append(DeploymentCheck(
                name="설정 파일 검증",
                description="시스템 설정 파일들의 유효성 검사",
                status=status,
                details=details,
                timestamp=datetime.now().isoformat()
            ))
            
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="설정 파일 검증",
                description="시스템 설정 파일들의 유효성 검사",
                status="failed",
                details=f"검증 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            ))
    
    def _verify_execution_permissions(self):
        """실행 권한 검증"""
        try:
            executable_files = [
                '🐹POSCO_워치햄스터_v3_제어센터.bat',
                '🐹POSCO_워치햄스터_v3_제어센터.command',
                '🚀🚀POSCO_News_250808_Direct_Start.bat',
                '🚀🚀POSCO_News_250808_Direct_Start.sh',
                'watchhamster_v3_v3_0_control_center.sh',
                'watchhamster_v3_v3_0_master_control.sh'
            ]
            
            permission_issues = []
            
            for exec_file in executable_files:
                file_path = self.base_path / exec_file
                if file_path.exists():
                    if not os.access(file_path, os.X_OK):
                        permission_issues.append(f"{exec_file}: 실행 권한 없음")
                else:
                    permission_issues.append(f"{exec_file}: 파일 없음")
            
            if permission_issues:
                self.deployment_checks.append(DeploymentCheck(
                    name="실행 권한 검증",
                    description="실행 파일들의 권한 검사",
                    status="warning",
                    details=f"권한 문제: {'; '.join(permission_issues)}",
                    timestamp=datetime.now().isoformat()
                ))
            else:
                self.deployment_checks.append(DeploymentCheck(
                    name="실행 권한 검증",
                    description="실행 파일들의 권한 검사",
                    status="passed",
                    details=f"검증된 실행 파일 수: {len([f for f in executable_files if (self.base_path / f).exists()])}",
                    timestamp=datetime.now().isoformat()
                ))
                
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="실행 권한 검증",
                description="실행 파일들의 권한 검사",
                status="failed",
                details=f"검증 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            ))
    
    def _prepare_backup_system(self):
        """백업 시스템 준비"""
        try:
            backup_dir = self.base_path / f"deployment_backup_{self.timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # 핵심 파일들 백업
            critical_files = [
                'POSCO_News_250808.py',
                'naming_convention_manager.py',
                'file_renaming_system.py',
                'system_functionality_verification.py',
                'final_integration_test_system.py'
            ]
            
            backed_up_files = []
            for file_name in critical_files:
                source_file = self.base_path / file_name
                if source_file.exists():
                    backup_file = backup_dir / file_name
                    shutil.copy2(source_file, backup_file)
                    backed_up_files.append(file_name)
            
            self.deployment_checks.append(DeploymentCheck(
                name="백업 시스템 준비",
                description="배포 전 핵심 파일 백업",
                status="passed",
                details=f"백업된 파일 수: {len(backed_up_files)}, 백업 위치: {backup_dir}",
                timestamp=datetime.now().isoformat()
            ))
            
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="백업 시스템 준비",
                description="배포 전 핵심 파일 백업",
                status="failed",
                details=f"백업 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            )) 
   
    def _run_performance_tests(self):
        """최종 성능 테스트 및 최적화"""
        
        # 1. 시스템 실행 성능 테스트
        self._test_system_execution_performance()
        
        # 2. 메모리 사용량 테스트
        self._test_memory_usage()
        
        # 3. 파일 I/O 성능 테스트
        self._test_file_io_performance()
        
        # 4. 네트워크 연결 테스트
        self._test_network_connectivity()
    
    def _test_system_execution_performance(self):
        """시스템 실행 성능 테스트"""
        try:
            # 핵심 시스템 실행 시간 측정
            test_script = self.base_path / 'system_functionality_verification.py'
            if not test_script.exists():
                self.performance_metrics.append(PerformanceMetric(
                    metric_name="시스템 실행 성능",
                    value=0,
                    unit="seconds",
                    threshold=60,
                    status="warning"
                ))
                return
            
            start_time = time.time()
            result = subprocess.run([
                sys.executable, str(test_script)
            ], capture_output=True, text=True, timeout=120)
            execution_time = time.time() - start_time
            
            status = "good" if execution_time < 60 else "warning" if execution_time < 120 else "critical"
            
            self.performance_metrics.append(PerformanceMetric(
                metric_name="시스템 실행 성능",
                value=round(execution_time, 2),
                unit="seconds",
                threshold=60,
                status=status
            ))
            
        except subprocess.TimeoutExpired:
            self.performance_metrics.append(PerformanceMetric(
                metric_name="시스템 실행 성능",
                value=120,
                unit="seconds",
                threshold=60,
                status="critical"
            ))
        except Exception as e:
            print(f"성능 테스트 오류: {str(e)}")
    
    def _test_memory_usage(self):
        """메모리 사용량 테스트"""
        try:
            import psutil
            
            # 현재 프로세스 메모리 사용량
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # 시스템 메모리 사용률
            system_memory = psutil.virtual_memory()
            memory_percent = system_memory.percent
            
            status = "good" if memory_mb < 100 else "warning" if memory_mb < 200 else "critical"
            
            self.performance_metrics.append(PerformanceMetric(
                metric_name="메모리 사용량",
                value=round(memory_mb, 2),
                unit="MB",
                threshold=100,
                status=status
            ))
            
            system_status = "good" if memory_percent < 80 else "warning" if memory_percent < 90 else "critical"
            
            self.performance_metrics.append(PerformanceMetric(
                metric_name="시스템 메모리 사용률",
                value=round(memory_percent, 2),
                unit="%",
                threshold=80,
                status=system_status
            ))
            
        except ImportError:
            self.performance_metrics.append(PerformanceMetric(
                metric_name="메모리 사용량",
                value=0,
                unit="MB",
                threshold=100,
                status="warning"
            ))
        except Exception as e:
            print(f"메모리 테스트 오류: {str(e)}")
    
    def _test_file_io_performance(self):
        """파일 I/O 성능 테스트"""
        try:
            # 테스트 파일 생성 및 읽기/쓰기 성능 측정
            test_file = self.base_path / f"performance_test_{self.timestamp}.tmp"
            test_data = "Performance test data\n" * 1000
            
            # 쓰기 성능 테스트
            start_time = time.time()
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_data)
            write_time = time.time() - start_time
            
            # 읽기 성능 테스트
            start_time = time.time()
            with open(test_file, 'r', encoding='utf-8') as f:
                _ = f.read()
            read_time = time.time() - start_time
            
            # 정리
            test_file.unlink()
            
            write_status = "good" if write_time < 1 else "warning" if write_time < 3 else "critical"
            read_status = "good" if read_time < 0.5 else "warning" if read_time < 1 else "critical"
            
            self.performance_metrics.append(PerformanceMetric(
                metric_name="파일 쓰기 성능",
                value=round(write_time * 1000, 2),
                unit="ms",
                threshold=1000,
                status=write_status
            ))
            
            self.performance_metrics.append(PerformanceMetric(
                metric_name="파일 읽기 성능",
                value=round(read_time * 1000, 2),
                unit="ms",
                threshold=500,
                status=read_status
            ))
            
        except Exception as e:
            print(f"파일 I/O 테스트 오류: {str(e)}")
    
    def _test_network_connectivity(self):
        """네트워크 연결 테스트"""
        try:
            import urllib.request
            import socket
            
            # 기본 인터넷 연결 테스트
            start_time = time.time()
            try:
                response = urllib.request.urlopen('https://www.google.com', timeout=10)
                response_time = time.time() - start_time
                
                status = "good" if response_time < 2 else "warning" if response_time < 5 else "critical"
                
                self.performance_metrics.append(PerformanceMetric(
                    metric_name="네트워크 응답 시간",
                    value=round(response_time * 1000, 2),
                    unit="ms",
                    threshold=2000,
                    status=status
                ))
                
            except (urllib.error.URLError, socket.timeout):
                self.performance_metrics.append(PerformanceMetric(
                    metric_name="네트워크 응답 시간",
                    value=10000,
                    unit="ms",
                    threshold=2000,
                    status="critical"
                ))
                
        except Exception as e:
            print(f"네트워크 테스트 오류: {str(e)}")    

    def _run_security_audit(self):
        """보안 검토 및 취약점 점검"""
        
        # 1. 하드코딩된 민감 정보 검사
        self._check_hardcoded_secrets()
        
        # 2. 파일 권한 검사
        self._check_file_permissions()
        
        # 3. 웹훅 URL 보안 검사
        self._check_webhook_security()
        
        # 4. 로그 파일 민감 정보 검사
        self._check_log_security()
    
    def _check_hardcoded_secrets(self):
        """하드코딩된 민감 정보 검사"""
        try:
            sensitive_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'webhook.*https?://[^\s"\']+',
            ]
            
            import re
            
            python_files = list(self.base_path.glob("*.py"))
            security_issues = []
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern in sensitive_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            security_issues.append(f"{py_file.name}:{line_num}")
                            
                except Exception as e:
                    continue
            
            if security_issues:
                self.security_checks.append(SecurityCheck(
                    check_type="하드코딩된 민감 정보",
                    file_path=", ".join(security_issues),
                    issue_type="sensitive_data",
                    severity="medium",
                    description="소스 코드에 하드코딩된 민감 정보 발견",
                    recommendation="환경 변수나 설정 파일로 분리 필요"
                ))
            else:
                print("✅ 하드코딩된 민감 정보 없음")
                
        except Exception as e:
            print(f"민감 정보 검사 오류: {str(e)}")
    
    def _check_file_permissions(self):
        """파일 권한 검사"""
        try:
            sensitive_files = [
                'config.py',
                'POSCO_News_250808.py',
                '*.json'
            ]
            
            permission_issues = []
            
            for pattern in sensitive_files:
                if '*' in pattern:
                    files = list(self.base_path.glob(pattern))
                else:
                    files = [self.base_path / pattern] if (self.base_path / pattern).exists() else []
                
                for file_path in files:
                    if file_path.exists():
                        # 파일 권한 확인 (Unix 시스템에서)
                        if hasattr(os, 'stat'):
                            stat_info = os.stat(file_path)
                            # 다른 사용자가 쓰기 권한을 가지고 있는지 확인
                            if stat_info.st_mode & 0o002:  # world writable
                                permission_issues.append(f"{file_path.name}: 전체 쓰기 권한")
            
            if permission_issues:
                self.security_checks.append(SecurityCheck(
                    check_type="파일 권한",
                    file_path=", ".join(permission_issues),
                    issue_type="file_permissions",
                    severity="low",
                    description="부적절한 파일 권한 설정",
                    recommendation="파일 권한을 적절히 제한 필요"
                ))
            else:
                print("✅ 파일 권한 적절함")
                
        except Exception as e:
            print(f"파일 권한 검사 오류: {str(e)}")
    
    def _check_webhook_security(self):
        """웹훅 URL 보안 검사"""
        try:
            # 웹훅 URL이 포함된 파일들 검사
            webhook_files = ['POSCO_News_250808.py']
            webhook_issues = []
            
            for file_name in webhook_files:
                file_path = self.base_path / file_name
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # HTTP URL 사용 검사 (HTTPS가 아닌)
                        import re
                        http_matches = re.findall(r'http://\[^\s"\'\]+', content)
                        if http_matches:
                            webhook_issues.append(f"{file_name}: HTTP URL 사용")
                            
                    except Exception as e:
                        continue
            
            if webhook_issues:
                self.security_checks.append(SecurityCheck(
                    check_type="웹훅 보안",
                    file_path=", ".join(webhook_issues),
                    issue_type="insecure_connection",
                    severity="medium",
                    description="안전하지 않은 HTTP 연결 사용",
                    recommendation="HTTPS 사용 권장"
                ))
            else:
                print("✅ 웹훅 보안 적절함")
                
        except Exception as e:
            print(f"웹훅 보안 검사 오류: {str(e)}")
    
    def _check_log_security(self):
        """로그 파일 민감 정보 검사"""
        try:
            log_files = list(self.base_path.glob("*.log"))
            log_issues = []
            
            sensitive_keywords = ['password', 'token', 'secret', 'api_key']
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    for keyword in sensitive_keywords:
                        if keyword in content:
                            log_issues.append(f"{log_file.name}: {keyword}")
                            
                except Exception as e:
                    continue
            
            if log_issues:
                self.security_checks.append(SecurityCheck(
                    check_type="로그 보안",
                    file_path=", ".join(log_issues),
                    issue_type="sensitive_logging",
                    severity="low",
                    description="로그 파일에 민감 정보 포함 가능성",
                    recommendation="로그 출력 시 민감 정보 마스킹 필요"
                ))
            else:
                print("✅ 로그 보안 적절함")
                
        except Exception as e:
            print(f"로그 보안 검사 오류: {str(e)}") 
   
    def _generate_operational_documentation(self):
        """운영 매뉴얼 및 체크리스트 완성"""
        
        # 1. 배포 체크리스트 생성
        self._create_deployment_checklist()
        
        # 2. 운영 매뉴얼 업데이트
        self._update_operational_manual()
        
        # 3. 트러블슈팅 가이드 완성
        self._complete_troubleshooting_guide()
        
        # 4. 모니터링 가이드 생성
        self._create_monitoring_guide()
    
    def _create_deployment_checklist(self):
        """배포 체크리스트 생성"""
        try:
            checklist_content = f"""# POSCO 시스템 배포 체크리스트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 배포 전 확인사항

### 1. 시스템 준비
- [ ] Python 파일 구문 검증 완료
- [ ] 핵심 모듈 import 테스트 통과
- [ ] 설정 파일 유효성 검증 완료
- [ ] 실행 권한 설정 확인
- [ ] 백업 시스템 준비 완료

### 2. 성능 검증
- [ ] 시스템 실행 성능 테스트 (< 60초)
- [ ] 메모리 사용량 확인 (< 100MB)
- [ ] 파일 I/O 성능 테스트 통과
- [ ] 네트워크 연결 테스트 통과

### 3. 보안 검증
- [ ] 하드코딩된 민감 정보 제거
- [ ] 파일 권한 적절히 설정
- [ ] 웹훅 보안 설정 확인
- [ ] 로그 파일 민감 정보 제거

### 4. 기능 검증
- [ ] 워치햄스터 제어센터 실행 테스트
- [ ] POSCO 뉴스 모니터링 실행 테스트
- [ ] 웹훅 알림 기능 테스트
- [ ] 에러 처리 및 복구 기능 테스트

## 배포 후 확인사항

### 1. 즉시 확인 (배포 후 5분 내)
- [ ] 시스템 정상 시작 확인
- [ ] 로그 파일 에러 메시지 확인
- [ ] 메모리 사용량 모니터링
- [ ] 네트워크 연결 상태 확인

### 2. 단기 모니터링 (배포 후 1시간 내)
- [ ] 웹훅 알림 정상 작동 확인
- [ ] 뉴스 수집 기능 정상 작동 확인
- [ ] 시스템 성능 지표 모니터링
- [ ] 사용자 피드백 수집

### 3. 장기 모니터링 (배포 후 24시간 내)
- [ ] 시스템 안정성 확인
- [ ] 성능 저하 없음 확인
- [ ] 메모리 누수 없음 확인
- [ ] 로그 파일 크기 모니터링

## 롤백 절차

### 롤백 조건
- 시스템 시작 실패
- 핵심 기능 작동 불가
- 심각한 성능 저하
- 보안 문제 발견

### 롤백 단계
1. 즉시 시스템 중지
2. 백업에서 파일 복원
3. 시스템 재시작
4. 기능 검증
5. 문제 원인 분석

## 연락처
- 시스템 관리자: [관리자 연락처]
- 기술 지원: [기술지원 연락처]
- 긴급 상황: [긴급 연락처]
"""
            
            checklist_file = self.base_path / f"deployment_checklist_{self.timestamp}.md"
            with open(checklist_file, 'w', encoding='utf-8') as f:
                f.write(checklist_content)
            
            self.deployment_checks.append(DeploymentCheck(
                name="배포 체크리스트 생성",
                description="배포 전후 확인사항 체크리스트 생성",
                status="passed",
                details=f"체크리스트 파일: {checklist_file.name}",
                timestamp=datetime.now().isoformat()
            ))
            
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="배포 체크리스트 생성",
                description="배포 전후 확인사항 체크리스트 생성",
                status="failed",
                details=f"생성 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            ))
    
    def _update_operational_manual(self):
        """운영 매뉴얼 업데이트"""
        try:
            manual_content = f"""# POSCO 시스템 운영 매뉴얼 v2.1
업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 시스템 개요
POSCO 워치햄스터 v3.0 뉴스 모니터링 시스템

## 주요 구성 요소

### 1. 핵심 실행 파일
- `POSCO_News_250808.py`: 메인 뉴스 모니터링 시스템
- `🐹POSCO_워치햄스터_v3_제어센터.bat`: Windows 제어센터
- `🐹POSCO_워치햄스터_v3_제어센터.command`: macOS 제어센터
- `watchhamster_v3_v3_0_control_center.sh`: Linux 제어센터

### 2. 관리 도구
- `system_functionality_verification.py`: 시스템 기능 검증
- `final_integration_test_system.py`: 통합 테스트
- `deployment_preparation_system.py`: 배포 준비 시스템

## 시스템 시작 방법

### Windows 환경
```cmd
🐹POSCO_워치햄스터_v3_제어센터.bat
```

### macOS 환경
```bash
./🐹POSCO_워치햄스터_v3_제어센터.command
```

### Linux 환경
```bash
./watchhamster_v3_v3_0_control_center.sh
```

## 시스템 모니터링

### 1. 로그 파일 확인
- `WatchHamster_v3.0.log`: 메인 시스템 로그
- `posco_news_250808_monitor.log`: 뉴스 모니터링 로그

### 2. 성능 모니터링
```python
python3 system_functionality_verification.py
```

### 3. 상태 확인
```python
python3 -c "
import POSCO_News_250808
print('시스템 상태: 정상')
"
```

## 문제 해결

### 1. 시스템 시작 실패
1. Python 버전 확인 (3.8+ 필요)
2. 의존성 모듈 설치 확인
3. 파일 권한 확인
4. 로그 파일 확인

### 2. 웹훅 알림 실패
1. 네트워크 연결 확인
2. 웹훅 URL 유효성 확인
3. 방화벽 설정 확인

### 3. 성능 저하
1. 메모리 사용량 확인
2. CPU 사용률 확인
3. 디스크 공간 확인
4. 네트워크 대역폭 확인

## 정기 유지보수

### 일일 점검
- [ ] 시스템 상태 확인
- [ ] 로그 파일 확인
- [ ] 웹훅 알림 테스트

### 주간 점검
- [ ] 성능 지표 분석
- [ ] 로그 파일 정리
- [ ] 백업 상태 확인

### 월간 점검
- [ ] 시스템 업데이트 확인
- [ ] 보안 패치 적용
- [ ] 성능 최적화 검토

## 비상 연락처
- 시스템 관리자: [연락처]
- 기술 지원팀: [연락처]
- 긴급 상황: [연락처]
"""
            
            manual_file = self.base_path / f"operational_manual_v2.1_{self.timestamp}.md"
            with open(manual_file, 'w', encoding='utf-8') as f:
                f.write(manual_content)
            
            self.deployment_checks.append(DeploymentCheck(
                name="운영 매뉴얼 업데이트",
                description="시스템 운영 매뉴얼 최신화",
                status="passed",
                details=f"매뉴얼 파일: {manual_file.name}",
                timestamp=datetime.now().isoformat()
            ))
            
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="운영 매뉴얼 업데이트",
                description="시스템 운영 매뉴얼 최신화",
                status="failed",
                details=f"업데이트 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            )) 
   
    def _complete_troubleshooting_guide(self):
        """트러블슈팅 가이드 완성"""
        try:
            troubleshooting_content = f"""# POSCO 시스템 트러블슈팅 가이드 v2.1
업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 일반적인 문제 및 해결방법

### 1. Python 구문 오류
**증상**: 시스템 시작 시 SyntaxError 발생
**원인**: Python 파일의 구문 오류
**해결방법**:
```bash
# 구문 검증
python3 -m py_compile [파일명].py

# 자동 수리 도구 사용
python3 syntax_error_repairer.py
```

### 2. 모듈 Import 실패
**증상**: ImportError 또는 ModuleNotFoundError 발생
**원인**: 모듈 경로 문제 또는 누락된 의존성
**해결방법**:
```bash
# 모듈 경로 확인
python3 -c "import sys; print(sys.path)"

# 의존성 설치
pip3 install -r requirements.txt
```

### 3. 파일 참조 오류
**증상**: FileNotFoundError 발생
**원인**: 잘못된 파일 경로 참조
**해결방법**:
```bash
# 파일 참조 복구 도구 사용
python3 file_reference_repairer.py
```

### 4. 웹훅 알림 실패
**증상**: 알림이 전송되지 않음
**원인**: 네트워크 연결 문제 또는 잘못된 웹훅 URL
**해결방법**:
1. 네트워크 연결 확인
2. 웹훅 URL 유효성 검증
3. 방화벽 설정 확인

### 5. 성능 저하
**증상**: 시스템 응답 속도 느림
**원인**: 메모리 부족, CPU 과부하, 네트워크 지연
**해결방법**:
```bash
# 성능 모니터링
python3 demo_performance_monitoring.py

# 시스템 리소스 확인
top
free -h
df -h
```

## 고급 문제 해결

### 1. 시스템 완전 복구
```bash
# 전체 시스템 수리
python3 comprehensive_error_repairer.py

# 통합 테스트 실행
python3 final_integration_test_system.py
```

### 2. 백업에서 복원
```bash
# 백업 파일 확인
ls -la deployment_backup_*

# 파일 복원
cp deployment_backup_*/[파일명] ./
```

### 3. 로그 분석
```bash
# 에러 로그 확인
grep -i error *.log

# 최근 로그 확인
tail -f WatchHamster_v3.0.log
```

## 예방 조치

### 1. 정기 점검
- 매일: 시스템 상태 확인
- 매주: 성능 지표 분석
- 매월: 전체 시스템 검증

### 2. 백업 관리
- 중요 파일 자동 백업
- 백업 파일 정기 검증
- 복원 절차 테스트

### 3. 모니터링 설정
- 시스템 리소스 모니터링
- 에러 로그 자동 알림
- 성능 임계값 설정

## 긴급 상황 대응

### 1. 시스템 중단 시
1. 즉시 시스템 중지
2. 로그 파일 백업
3. 문제 원인 분석
4. 백업에서 복원
5. 시스템 재시작

### 2. 데이터 손실 시
1. 시스템 즉시 중지
2. 데이터 복구 시도
3. 백업 데이터 확인
4. 필요시 전문가 지원 요청

### 3. 보안 문제 발견 시
1. 시스템 격리
2. 보안 패치 적용
3. 로그 분석
4. 시스템 재검증

## 연락처 및 지원
- 기술 지원: [기술지원팀 연락처]
- 긴급 상황: [긴급 연락처]
- 문서 업데이트: [문서 관리자 연락처]
"""
            
            guide_file = self.base_path / f"troubleshooting_guide_v2.1_{self.timestamp}.md"
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(troubleshooting_content)
            
            self.deployment_checks.append(DeploymentCheck(
                name="트러블슈팅 가이드 완성",
                description="문제 해결 가이드 업데이트",
                status="passed",
                details=f"가이드 파일: {guide_file.name}",
                timestamp=datetime.now().isoformat()
            ))
            
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="트러블슈팅 가이드 완성",
                description="문제 해결 가이드 업데이트",
                status="failed",
                details=f"생성 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            ))
    
    def _create_monitoring_guide(self):
        """모니터링 가이드 생성"""
        try:
            monitoring_content = f"""# POSCO 시스템 모니터링 가이드
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 모니터링 개요
POSCO 워치햄스터 v3.0 시스템의 상태를 지속적으로 모니터링하여 안정적인 운영을 보장합니다.

## 핵심 모니터링 지표

### 1. 시스템 상태 지표
- **CPU 사용률**: < 80%
- **메모리 사용률**: < 80%
- **디스크 사용률**: < 90%
- **네트워크 응답시간**: < 2초

### 2. 애플리케이션 지표
- **시스템 시작 시간**: < 60초
- **뉴스 수집 주기**: 정상 작동
- **웹훅 응답률**: > 95%
- **에러 발생률**: < 1%

## 모니터링 도구

### 1. 자동 모니터링 스크립트
```bash
# 시스템 상태 확인
python3 system_functionality_verification.py

# 성능 모니터링
python3 demo_performance_monitoring.py

# 통합 테스트
python3 final_integration_test_system.py
```

### 2. 수동 점검 명령어
```bash
# 프로세스 확인
ps aux | grep python

# 메모리 사용량
free -h

# 디스크 사용량
df -h

# 네트워크 연결
netstat -an | grep LISTEN
```

## 알림 설정

### 1. 임계값 설정
- CPU 사용률 > 80%: 경고
- 메모리 사용률 > 80%: 경고
- 에러 발생: 즉시 알림
- 시스템 중단: 긴급 알림

### 2. 알림 채널
- 이메일 알림
- 웹훅 알림
- 로그 파일 기록

## 로그 관리

### 1. 로그 파일 위치
- `WatchHamster_v3.0.log`: 메인 시스템 로그
- `posco_news_250808_monitor.log`: 뉴스 모니터링 로그
- `*.log`: 기타 컴포넌트 로그

### 2. 로그 분석
```bash
# 에러 로그 확인
grep -i error *.log

# 경고 로그 확인
grep -i warning *.log

# 최근 로그 실시간 확인
tail -f WatchHamster_v3.0.log
```

## 정기 점검 일정

### 일일 점검 (매일 09:00)
- [ ] 시스템 상태 확인
- [ ] 로그 파일 점검
- [ ] 웹훅 알림 테스트
- [ ] 성능 지표 확인

### 주간 점검 (매주 월요일)
- [ ] 전체 시스템 검증
- [ ] 성능 트렌드 분석
- [ ] 로그 파일 정리
- [ ] 백업 상태 확인

### 월간 점검 (매월 1일)
- [ ] 시스템 업데이트 검토
- [ ] 보안 패치 적용
- [ ] 성능 최적화 검토
- [ ] 문서 업데이트

## 대시보드 구성

### 1. 실시간 모니터링
- 시스템 상태 표시등
- 성능 지표 그래프
- 최근 알림 목록
- 로그 실시간 스트림

### 2. 히스토리 분석
- 성능 트렌드 차트
- 에러 발생 통계
- 사용량 패턴 분석
- 가용성 리포트

## 문제 대응 절차

### 1. 경고 수준 (Warning)
1. 로그 확인
2. 원인 분석
3. 필요시 조치
4. 모니터링 지속

### 2. 위험 수준 (Critical)
1. 즉시 알림 발송
2. 시스템 상태 점검
3. 긴급 조치 실행
4. 관리자 연락

### 3. 긴급 수준 (Emergency)
1. 시스템 중단 고려
2. 백업 시스템 활성화
3. 복구 절차 실행
4. 사후 분석 실시

## 연락처
- 모니터링 담당자: [담당자 연락처]
- 시스템 관리자: [관리자 연락처]
- 긴급 상황: [긴급 연락처]
"""
            
            monitoring_file = self.base_path / f"monitoring_guide_{self.timestamp}.md"
            with open(monitoring_file, 'w', encoding='utf-8') as f:
                f.write(monitoring_content)
            
            self.deployment_checks.append(DeploymentCheck(
                name="모니터링 가이드 생성",
                description="시스템 모니터링 가이드 생성",
                status="passed",
                details=f"가이드 파일: {monitoring_file.name}",
                timestamp=datetime.now().isoformat()
            ))
            
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="모니터링 가이드 생성",
                description="시스템 모니터링 가이드 생성",
                status="failed",
                details=f"생성 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            ))  
  
    def _determine_overall_status(self) -> str:
        """전체 상태 결정"""
        failed_checks = [check for check in self.deployment_checks if check.status == 'failed']
        critical_security = [check for check in self.security_checks if check.severity == 'critical']
        critical_performance = [metric for metric in self.performance_metrics if metric.status == 'critical']
        
        if failed_checks or critical_security or critical_performance:
            return 'failed'
        
        warning_checks = [check for check in self.deployment_checks if check.status == 'warning']
        warning_performance = [metric for metric in self.performance_metrics if metric.status == 'warning']
        
        if warning_checks or warning_performance:
            return 'warning'
        
        return 'passed'
    
    def _generate_deployment_report(self, results: Dict[str, Any]):
        """배포 준비 보고서 생성"""
        try:
            report_content = f"""# POSCO 시스템 배포 준비 보고서
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
전체 상태: {results['overall_status'].upper()}

## 요약
- 배포 검증 항목: {len(self.deployment_checks)}개
- 보안 검사 항목: {len(self.security_checks)}개  
- 성능 측정 항목: {len(self.performance_metrics)}개

## 배포 검증 결과

"""
            
            # 배포 검증 결과
            for check in self.deployment_checks:
                status_emoji = "✅" if check.status == "passed" else "⚠️" if check.status == "warning" else "❌"
                report_content += f"### {status_emoji} {check.name}\n"
                report_content += f"- **상태**: {check.status}\n"
                report_content += f"- **설명**: {check.description}\n"
                report_content += f"- **세부사항**: {check.details}\n"
                report_content += f"- **시간**: {check.timestamp}\n\n"
            
            # 보안 검사 결과
            if self.security_checks:
                report_content += "## 보안 검사 결과\n\n"
                for security_check in self.security_checks:
                    severity_emoji = "🔴" if security_check.severity == "critical" else "🟡" if security_check.severity == "medium" else "🟢"
                    report_content += f"### {severity_emoji} {security_check.check_type}\n"
                    report_content += f"- **심각도**: {security_check.severity}\n"
                    report_content += f"- **파일**: {security_check.file_path}\n"
                    report_content += f"- **설명**: {security_check.description}\n"
                    report_content += f"- **권장사항**: {security_check.recommendation}\n\n"
            
            # 성능 측정 결과
            if self.performance_metrics:
                report_content += "## 성능 측정 결과\n\n"
                for metric in self.performance_metrics:
                    status_emoji = "✅" if metric.status == "good" else "⚠️" if metric.status == "warning" else "❌"
                    report_content += f"### {status_emoji} {metric.metric_name}\n"
                    report_content += f"- **측정값**: {metric.value} {metric.unit}\n"
                    report_content += f"- **임계값**: {metric.threshold} {metric.unit}\n"
                    report_content += f"- **상태**: {metric.status}\n\n"
            
            # 권장사항
            report_content += "## 권장사항\n\n"
            
            if results['overall_status'] == 'passed':
                report_content += "🎉 **배포 준비 완료!**\n"
                report_content += "- 모든 검증 항목이 통과되었습니다.\n"
                report_content += "- 프로덕션 환경 배포를 진행할 수 있습니다.\n"
                report_content += "- 배포 후 모니터링을 지속해주세요.\n\n"
            elif results['overall_status'] == 'warning':
                report_content += "⚠️ **주의사항 있음**\n"
                report_content += "- 일부 경고 사항이 있지만 배포 가능합니다.\n"
                report_content += "- 경고 사항을 검토하고 필요시 조치하세요.\n"
                report_content += "- 배포 후 면밀한 모니터링이 필요합니다.\n\n"
            else:
                report_content += "❌ **배포 불가**\n"
                report_content += "- 심각한 문제가 발견되었습니다.\n"
                report_content += "- 문제를 해결한 후 다시 검증하세요.\n"
                report_content += "- 필요시 기술 지원팀에 문의하세요.\n\n"
            
            # 다음 단계
            report_content += "## 다음 단계\n\n"
            if results['overall_status'] == 'passed':
                report_content += "1. 배포 체크리스트 확인\n"
                report_content += "2. 프로덕션 환경 배포 실행\n"
                report_content += "3. 배포 후 모니터링 시작\n"
                report_content += "4. 사용자 피드백 수집\n"
            else:
                report_content += "1. 실패/경고 항목 검토\n"
                report_content += "2. 문제 해결 조치 실행\n"
                report_content += "3. 재검증 실시\n"
                report_content += "4. 배포 준비 완료 후 배포 진행\n"
            
            # 보고서 파일 저장
            report_file = self.base_path / f"deployment_preparation_report_{self.timestamp}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # JSON 형태로도 저장
            json_file = self.base_path / f"deployment_preparation_report_{self.timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 배포 준비 보고서 생성 완료:")
            print(f"   - Markdown: {report_file.name}")
            print(f"   - JSON: {json_file.name}")
            
        except Exception as e:
            print(f"보고서 생성 오류: {str(e)}")

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 POSCO 시스템 배포 준비 및 최종 검증 시스템")
    print("=" * 60)
    
    deployment_system = DeploymentPreparationSystem()
    results = deployment_system.run_full_deployment_preparation()
    
    print("\n" + "=" * 60)
    print(f"🏁 배포 준비 완료! 최종 상태: {results['overall_status'].upper()}")
    print("=" * 60)
    
    # 결과에 따른 종료 코드 설정
    if results['overall_status'] == 'failed':
        sys.exit(1)
    elif results['overall_status'] == 'warning':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()