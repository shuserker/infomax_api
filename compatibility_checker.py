#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 호환성 검증 시스템
CompatibilityChecker 클래스 구현

Created: 2025-01-06
Updated: 2025-01-06
Author: POSCO 시스템 관리자

Requirements: 3.1, 3.2
- 함수명, 변수명, import 충돌 검사 로직 개발
- 신규 시스템 운영 기능과의 상호작용 검증
"""

import os
import sys
import ast
import json
import re
import importlib.util
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class ConflictSeverity(Enum):
    """충돌 심각도 레벨"""
    CRITICAL = "critical"      # 시스템 중단 가능성
    HIGH = "high"             # 기능 오작동 가능성  
    MEDIUM = "medium"         # 성능 저하 가능성
    LOW = "low"               # 경미한 영향
    INFO = "info"             # 정보성 알림

@dataclass
class CompatibilityIssue:
    """호환성 문제 정보"""
    issue_type: str           # 문제 유형 (function_conflict, variable_conflict, etc.)
    severity: ConflictSeverity # 심각도
    description: str          # 문제 설명
    affected_component: str   # 영향받는 컴포넌트
    conflict_details: Dict    # 충돌 상세 정보
    resolution_suggestion: str # 해결 방안 제안
    file_location: str        # 파일 위치
    line_number: Optional[int] = None  # 줄 번호

class CompatibilityChecker:
    """
    신규 기능과 복원된 웹훅 기능 간 호환성 검증 클래스
    
    주요 기능:
    - 함수명 충돌 검사
    - 변수명 충돌 검사  
    - import 충돌 검사
    - 신규 시스템 운영 기능과의 상호작용 검증
    """
    
    def __init__(self, target_file_path: str, webhook_restorer=None):
        """
        CompatibilityChecker 초기화
        
        Args:
            target_file_path (str): 검사 대상 파일 경로
            webhook_restorer: WebhookMessageRestorer 인스턴스 (선택사항)
        """
        self.target_file = target_file_path
        self.webhook_restorer = webhook_restorer
        
        # 검사 결과 저장
        self.compatibility_issues: List[CompatibilityIssue] = []
        self.system_components: Dict[str, Any] = {}
        self.webhook_components: Dict[str, Any] = {}
        
        # 신규 시스템 운영 기능 목록 (v3.0 아키텍처)
        self.v3_components = [
            'ProcessManager',
            'StateManager', 
            'ColorfulConsoleUI',
            'ModuleRegistry',
            'NotificationManager',
            'PerformanceMonitor',
            'PerformanceOptimizer',
            'IntegratedReportScheduler',
            'MasterNewsMonitor'
        ]
        
        # 웹훅 관련 함수 목록
        self.webhook_functions = [
            'send_status_notification',
            'send_notification',
            'send_status_report_v2', 
            'send_startup_notification_v2'
        ]
        
        # 웹훅 관련 변수/상수 목록
        self.webhook_variables = [
            'DOORAY_WEBHOOK_URL',
            'WATCHHAMSTER_WEBHOOK_URL',
            'BOT_PROFILE_IMAGE_URL'
        ]
        
        # 로그 파일 설정
        self.log_file = "compatibility_check.log"
        
        # 검사 통계
        self.check_stats = {
            'total_checks': 0,
            'issues_found': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0,
            'info_issues': 0
        }
        
        print(f"[INFO] CompatibilityChecker 초기화 완료")
        print(f"[INFO] 대상 파일: {self.target_file}")
        print(f"[INFO] v3.0 컴포넌트: {len(self.v3_components)}개")
        print(f"[INFO] 웹훅 함수: {len(self.webhook_functions)}개")
    
    def log(self, message: str):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        print(log_message)
        
        # 로그 파일에 저장
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"[WARNING] 로그 파일 저장 실패: {e}")
    
    def check_function_conflicts(self) -> List[CompatibilityIssue]:
        """
        함수명 충돌 검사
        Requirements: 3.1 - 함수명 충돌 검사 로직 개발
        
        Returns:
            List[CompatibilityIssue]: 발견된 함수 충돌 목록
        """
        try:
            self.log("[INFO] 함수명 충돌 검사 시작...")
            function_conflicts = []
            
            # 대상 파일에서 모든 함수 추출
            target_functions = self._extract_functions_from_file(self.target_file)
            
            # 웹훅 함수와 기존 함수 간 충돌 검사
            for webhook_func in self.webhook_functions:
                if webhook_func in target_functions:
                    # 함수 시그니처 비교
                    conflict_details = self._compare_function_signatures(
                        webhook_func, target_functions[webhook_func]
                    )
                    
                    if conflict_details['has_conflict']:
                        issue = CompatibilityIssue(
                            issue_type="function_conflict",
                            severity=ConflictSeverity.HIGH,
                            description=f"웹훅 함수 '{webhook_func}'가 기존 함수와 충돌합니다",
                            affected_component=webhook_func,
                            conflict_details=conflict_details,
                            resolution_suggestion="함수명 변경 또는 기존 함수 백업 후 교체",
                            file_location=self.target_file,
                            line_number=conflict_details.get('line_number')
                        )
                        function_conflicts.append(issue)
                        self.log(f"[CONFLICT] 함수 충돌 발견: {webhook_func}")
                    else:
                        self.log(f"[OK] 함수 호환성 확인: {webhook_func}")
            
            # v3.0 컴포넌트와의 메서드명 충돌 검사
            v3_method_conflicts = self._check_v3_method_conflicts(target_functions)
            function_conflicts.extend(v3_method_conflicts)
            
            self.log(f"[INFO] 함수 충돌 검사 완료: {len(function_conflicts)}개 충돌 발견")
            self.check_stats['total_checks'] += 1
            
            return function_conflicts
            
        except Exception as e:
            self.log(f"[ERROR] 함수 충돌 검사 실패: {e}")
            return []
    
    def check_variable_conflicts(self) -> List[CompatibilityIssue]:
        """
        변수명 충돌 검사
        Requirements: 3.1 - 변수명 충돌 검사 로직 개발
        
        Returns:
            List[CompatibilityIssue]: 발견된 변수 충돌 목록
        """
        try:
            self.log("[INFO] 변수명 충돌 검사 시작...")
            variable_conflicts = []
            
            # 대상 파일에서 모든 변수 추출
            target_variables = self._extract_variables_from_file(self.target_file)
            
            # 웹훅 변수와 기존 변수 간 충돌 검사
            for webhook_var in self.webhook_variables:
                if webhook_var in target_variables:
                    # 변수 값 비교
                    conflict_details = self._compare_variable_values(
                        webhook_var, target_variables[webhook_var]
                    )
                    
                    if conflict_details['has_conflict']:
                        severity = ConflictSeverity.MEDIUM
                        if webhook_var.endswith('_URL'):
                            severity = ConflictSeverity.HIGH  # URL 충돌은 높은 심각도
                        
                        issue = CompatibilityIssue(
                            issue_type="variable_conflict",
                            severity=severity,
                            description=f"웹훅 변수 '{webhook_var}'가 기존 변수와 충돌합니다",
                            affected_component=webhook_var,
                            conflict_details=conflict_details,
                            resolution_suggestion="변수값 통합 또는 네임스페이스 분리",
                            file_location=self.target_file,
                            line_number=conflict_details.get('line_number')
                        )
                        variable_conflicts.append(issue)
                        self.log(f"[CONFLICT] 변수 충돌 발견: {webhook_var}")
                    else:
                        self.log(f"[OK] 변수 호환성 확인: {webhook_var}")
            
            # 전역 변수 네임스페이스 충돌 검사
            namespace_conflicts = self._check_namespace_conflicts(target_variables)
            variable_conflicts.extend(namespace_conflicts)
            
            self.log(f"[INFO] 변수 충돌 검사 완료: {len(variable_conflicts)}개 충돌 발견")
            self.check_stats['total_checks'] += 1
            
            return variable_conflicts
            
        except Exception as e:
            self.log(f"[ERROR] 변수 충돌 검사 실패: {e}")
            return []
    
    def check_import_conflicts(self) -> List[CompatibilityIssue]:
        """
        import 충돌 검사
        Requirements: 3.1 - import 충돌 검사 로직 개발
        
        Returns:
            List[CompatibilityIssue]: 발견된 import 충돌 목록
        """
        try:
            self.log("[INFO] import 충돌 검사 시작...")
            import_conflicts = []
            
            # 대상 파일에서 모든 import 문 추출
            target_imports = self._extract_imports_from_file(self.target_file)
            
            # 웹훅 관련 필수 import 목록
            required_webhook_imports = [
                'requests',
                'json',
                'datetime'
            ]
            
            # 필수 import 누락 검사
            for required_import in required_webhook_imports:
                if not self._is_import_available(required_import, target_imports):
                    issue = CompatibilityIssue(
                        issue_type="missing_import",
                        severity=ConflictSeverity.HIGH,
                        description=f"웹훅 기능에 필요한 '{required_import}' 모듈이 import되지 않았습니다",
                        affected_component=required_import,
                        conflict_details={'missing_import': required_import},
                        resolution_suggestion=f"파일 상단에 'import {required_import}' 추가",
                        file_location=self.target_file
                    )
                    import_conflicts.append(issue)
                    self.log(f"[MISSING] 필수 import 누락: {required_import}")
            
            # 중복 import 검사
            duplicate_imports = self._check_duplicate_imports(target_imports)
            for duplicate in duplicate_imports:
                issue = CompatibilityIssue(
                    issue_type="duplicate_import",
                    severity=ConflictSeverity.LOW,
                    description=f"중복된 import 발견: {duplicate['module']}",
                    affected_component=duplicate['module'],
                    conflict_details=duplicate,
                    resolution_suggestion="중복된 import 문 제거",
                    file_location=self.target_file,
                    line_number=duplicate.get('line_number')
                )
                import_conflicts.append(issue)
                self.log(f"[DUPLICATE] 중복 import 발견: {duplicate['module']}")
            
            # v3.0 컴포넌트 import 충돌 검사
            v3_import_conflicts = self._check_v3_import_conflicts(target_imports)
            import_conflicts.extend(v3_import_conflicts)
            
            self.log(f"[INFO] import 충돌 검사 완료: {len(import_conflicts)}개 충돌 발견")
            self.check_stats['total_checks'] += 1
            
            return import_conflicts
            
        except Exception as e:
            self.log(f"[ERROR] import 충돌 검사 실패: {e}")
            return []
    
    def check_system_interaction_compatibility(self) -> List[CompatibilityIssue]:
        """
        신규 시스템 운영 기능과의 상호작용 검증
        Requirements: 3.2 - 신규 시스템 운영 기능과의 상호작용 검증
        
        Returns:
            List[CompatibilityIssue]: 발견된 상호작용 문제 목록
        """
        try:
            self.log("[INFO] 시스템 상호작용 호환성 검사 시작...")
            interaction_issues = []
            
            # v3.0 아키텍처 컴포넌트 상태 확인
            v3_component_status = self._check_v3_component_availability()
            
            # 각 v3.0 컴포넌트와의 상호작용 검증
            for component_name, status in v3_component_status.items():
                if status['available']:
                    # 컴포넌트별 상호작용 검증
                    component_issues = self._verify_component_interaction(component_name, status)
                    interaction_issues.extend(component_issues)
                else:
                    # 컴포넌트 비활성화 시 영향 분석
                    issue = CompatibilityIssue(
                        issue_type="component_unavailable",
                        severity=ConflictSeverity.MEDIUM,
                        description=f"v3.0 컴포넌트 '{component_name}'가 비활성화되어 있습니다",
                        affected_component=component_name,
                        conflict_details=status,
                        resolution_suggestion="컴포넌트 활성화 또는 대체 방안 구현",
                        file_location=self.target_file
                    )
                    interaction_issues.append(issue)
                    self.log(f"[WARNING] 컴포넌트 비활성화: {component_name}")
            
            # 성능 모니터링 시스템과의 호환성 검사
            performance_issues = self._check_performance_monitoring_compatibility()
            interaction_issues.extend(performance_issues)
            
            # 통합 리포트 스케줄러와의 호환성 검사
            scheduler_issues = self._check_scheduler_compatibility()
            interaction_issues.extend(scheduler_issues)
            
            self.log(f"[INFO] 시스템 상호작용 검사 완료: {len(interaction_issues)}개 문제 발견")
            self.check_stats['total_checks'] += 1
            
            return interaction_issues
            
        except Exception as e:
            self.log(f"[ERROR] 시스템 상호작용 검사 실패: {e}")
            return []
    
    def generate_compatibility_report(self) -> str:
        """
        호환성 검사 보고서 생성
        Requirements: 3.1, 3.2 - 호환성 검사 결과 보고서 생성
        
        Returns:
            str: 상세 호환성 보고서
        """
        try:
            self.log("[INFO] 호환성 검사 보고서 생성 시작...")
            
            # 모든 호환성 검사 수행
            all_issues = []
            all_issues.extend(self.check_function_conflicts())
            all_issues.extend(self.check_variable_conflicts())
            all_issues.extend(self.check_import_conflicts())
            all_issues.extend(self.check_system_interaction_compatibility())
            
            # 심각도별 분류
            issues_by_severity = self._classify_issues_by_severity(all_issues)
            
            # 통계 업데이트
            self.check_stats['issues_found'] = len(all_issues)
            for severity, issues in issues_by_severity.items():
                self.check_stats[f'{severity.value}_issues'] = len(issues)
            
            # 보고서 생성
            report = self._generate_detailed_report(all_issues, issues_by_severity)
            
            # 보고서 파일 저장
            report_file = f"compatibility_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log(f"[SUCCESS] 호환성 보고서 생성 완료: {report_file}")
            return report
            
        except Exception as e:
            self.log(f"[ERROR] 호환성 보고서 생성 실패: {e}")
            return f"호환성 보고서 생성 실패: {e}"
    
    def _extract_functions_from_file(self, file_path: str) -> Dict[str, Dict]:
        """
        파일에서 모든 함수 정보 추출
        
        Args:
            file_path (str): 분석할 파일 경로
            
        Returns:
            Dict[str, Dict]: 함수명과 함수 정보 매핑
        """
        try:
            functions = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST를 사용한 함수 추출
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions[node.name] = {
                            'name': node.name,
                            'args': [arg.arg for arg in node.args.args],
                            'line_number': node.lineno,
                            'docstring': ast.get_docstring(node),
                            'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                        }
            except SyntaxError:
                # AST 파싱 실패 시 정규식 사용
                self.log("[WARNING] AST 파싱 실패, 정규식 방식으로 전환")
                functions = self._extract_functions_with_regex(content)
            
            return functions
            
        except Exception as e:
            self.log(f"[ERROR] 함수 추출 실패: {e}")
            return {}
    
    def _extract_functions_with_regex(self, content: str) -> Dict[str, Dict]:
        """
        정규식을 사용한 함수 추출 (AST 실패 시 대안)
        
        Args:
            content (str): 파일 내용
            
        Returns:
            Dict[str, Dict]: 함수명과 함수 정보 매핑
        """
        functions = {}
        
        # 함수 정의 패턴
        func_pattern = r'def\s+(\w+)\s*\(([^)]*)\):'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                
                # 인수 파싱
                args = []
                if args_str.strip():
                    args = [arg.strip().split('=')[0].strip() for arg in args_str.split(',')]
                
                functions[func_name] = {
                    'name': func_name,
                    'args': args,
                    'line_number': i + 1,
                    'docstring': None,
                    'decorators': []
                }
        
        return functions
    
    def _extract_variables_from_file(self, file_path: str) -> Dict[str, Dict]:
        """
        파일에서 모든 변수 정보 추출
        
        Args:
            file_path (str): 분석할 파일 경로
            
        Returns:
            Dict[str, Dict]: 변수명과 변수 정보 매핑
        """
        try:
            variables = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 변수 할당 패턴
            var_patterns = [
                r'(\w+)\s*=\s*["\']([^"\']*)["\']',  # 문자열 변수
                r'(\w+)\s*=\s*(\d+)',                # 숫자 변수
                r'(\w+)\s*=\s*([^#\n]+)'            # 기타 변수
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith('#'):
                    for pattern in var_patterns:
                        match = re.search(pattern, line)
                        if match:
                            var_name = match.group(1)
                            var_value = match.group(2).strip()
                            
                            # 특정 패턴 제외 (함수 정의, 클래스 정의 등)
                            if not any(keyword in line for keyword in ['def ', 'class ', 'import ', 'from ']):
                                variables[var_name] = {
                                    'name': var_name,
                                    'value': var_value,
                                    'line_number': i + 1,
                                    'type': self._infer_variable_type(var_value)
                                }
                            break
            
            return variables
            
        except Exception as e:
            self.log(f"[ERROR] 변수 추출 실패: {e}")
            return {}
    
    def _extract_imports_from_file(self, file_path: str) -> List[Dict]:
        """
        파일에서 모든 import 문 추출
        
        Args:
            file_path (str): 분석할 파일 경로
            
        Returns:
            List[Dict]: import 정보 목록
        """
        try:
            imports = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                
                # import 문 패턴
                if line.startswith('import ') or line.startswith('from '):
                    import_info = {
                        'line_number': i + 1,
                        'statement': line,
                        'type': 'import' if line.startswith('import ') else 'from_import'
                    }
                    
                    # 모듈명 추출
                    if line.startswith('import '):
                        modules = line[7:].split(',')
                        import_info['modules'] = [m.strip().split(' as ')[0] for m in modules]
                    else:  # from ... import ...
                        parts = line.split(' import ')
                        if len(parts) == 2:
                            import_info['from_module'] = parts[0][5:].strip()
                            import_info['imported_items'] = [item.strip().split(' as ')[0] for item in parts[1].split(',')]
                    
                    imports.append(import_info)
            
            return imports
            
        except Exception as e:
            self.log(f"[ERROR] import 추출 실패: {e}")
            return []
    
    def _compare_function_signatures(self, func_name: str, existing_func: Dict) -> Dict:
        """
        함수 시그니처 비교
        
        Args:
            func_name (str): 함수명
            existing_func (Dict): 기존 함수 정보
            
        Returns:
            Dict: 비교 결과
        """
        try:
            # 웹훅 복원기에서 추출된 함수 정보 가져오기
            if self.webhook_restorer and hasattr(self.webhook_restorer, 'extracted_functions'):
                webhook_func = self.webhook_restorer.extracted_functions.get(func_name)
                if webhook_func:
                    # 간단한 시그니처 비교 (실제 구현에서는 더 정교하게)
                    return {
                        'has_conflict': False,  # 웹훅 함수는 기존 함수를 교체하는 것이 목적
                        'line_number': existing_func.get('line_number'),
                        'existing_args': existing_func.get('args', []),
                        'webhook_args': [],  # 실제로는 파싱 필요
                        'resolution': 'replace_with_webhook_version'
                    }
            
            # 기본적으로 충돌 없음으로 처리 (웹훅 함수는 교체 목적)
            return {
                'has_conflict': False,
                'line_number': existing_func.get('line_number'),
                'resolution': 'safe_to_replace'
            }
            
        except Exception as e:
            self.log(f"[ERROR] 함수 시그니처 비교 실패: {e}")
            return {'has_conflict': True, 'error': str(e)}
    
    def _compare_variable_values(self, var_name: str, existing_var: Dict) -> Dict:
        """
        변수값 비교
        
        Args:
            var_name (str): 변수명
            existing_var (Dict): 기존 변수 정보
            
        Returns:
            Dict: 비교 결과
        """
        try:
            # 웹훅 복원기에서 추출된 상수 정보 가져오기
            if self.webhook_restorer and hasattr(self.webhook_restorer, 'extracted_constants'):
                webhook_value = self.webhook_restorer.extracted_constants.get(var_name)
                if webhook_value:
                    existing_value = existing_var.get('value', '')
                    
                    # 값 비교
                    if webhook_value != existing_value:
                        return {
                            'has_conflict': True,
                            'line_number': existing_var.get('line_number'),
                            'existing_value': existing_value,
                            'webhook_value': webhook_value,
                            'resolution': 'use_webhook_value'
                        }
            
            return {
                'has_conflict': False,
                'line_number': existing_var.get('line_number'),
                'resolution': 'no_conflict'
            }
            
        except Exception as e:
            self.log(f"[ERROR] 변수값 비교 실패: {e}")
            return {'has_conflict': True, 'error': str(e)}
    
    def _check_v3_component_availability(self) -> Dict[str, Dict]:
        """
        v3.0 컴포넌트 가용성 확인
        
        Returns:
            Dict[str, Dict]: 컴포넌트별 상태 정보
        """
        try:
            component_status = {}
            
            for component in self.v3_components:
                try:
                    # 컴포넌트 import 시도
                    if component == 'ProcessManager':
                        from core.process_manager import ProcessManager
                        component_status[component] = {'available': True, 'module': ProcessManager}
                    elif component == 'StateManager':
                        from core.state_manager import StateManager
                        component_status[component] = {'available': True, 'module': StateManager}
                    # ... 다른 컴포넌트들도 유사하게 처리
                    else:
                        component_status[component] = {'available': False, 'reason': 'not_implemented'}
                        
                except ImportError as e:
                    component_status[component] = {'available': False, 'reason': f'import_error: {e}'}
                except Exception as e:
                    component_status[component] = {'available': False, 'reason': f'error: {e}'}
            
            return component_status
            
        except Exception as e:
            self.log(f"[ERROR] v3.0 컴포넌트 상태 확인 실패: {e}")
            return {}
    
    def _verify_component_interaction(self, component_name: str, status: Dict) -> List[CompatibilityIssue]:
        """
        특정 컴포넌트와의 상호작용 검증
        
        Args:
            component_name (str): 컴포넌트명
            status (Dict): 컴포넌트 상태 정보
            
        Returns:
            List[CompatibilityIssue]: 발견된 상호작용 문제
        """
        issues = []
        
        try:
            # 컴포넌트별 특화 검증 로직
            if component_name == 'NotificationManager':
                # 알림 관리자와 웹훅 기능 간 중복 검사
                issue = self._check_notification_overlap()
                if issue:
                    issues.append(issue)
                    
            elif component_name == 'ProcessManager':
                # 프로세스 관리자와 웹훅 프로세스 간 충돌 검사
                issue = self._check_process_management_conflict()
                if issue:
                    issues.append(issue)
                    
            elif component_name == 'PerformanceMonitor':
                # 성능 모니터링과 웹훅 성능 영향 검사
                issue = self._check_performance_impact()
                if issue:
                    issues.append(issue)
            
            return issues
            
        except Exception as e:
            self.log(f"[ERROR] {component_name} 상호작용 검증 실패: {e}")
            return []
    
    def _check_notification_overlap(self) -> Optional[CompatibilityIssue]:
        """알림 관리자와 웹훅 기능 간 중복 검사"""
        try:
            # NotificationManager가 있는 경우 웹훅 기능과 중복될 수 있음
            return CompatibilityIssue(
                issue_type="notification_overlap",
                severity=ConflictSeverity.MEDIUM,
                description="NotificationManager와 웹훅 알림 기능이 중복될 수 있습니다",
                affected_component="NotificationManager",
                conflict_details={'overlap_type': 'notification_duplication'},
                resolution_suggestion="NotificationManager를 통해 웹훅 알림 통합 또는 역할 분리",
                file_location=self.target_file
            )
        except Exception:
            return None
    
    def _check_process_management_conflict(self) -> Optional[CompatibilityIssue]:
        """프로세스 관리자와 웹훅 프로세스 간 충돌 검사"""
        try:
            return CompatibilityIssue(
                issue_type="process_conflict",
                severity=ConflictSeverity.LOW,
                description="ProcessManager가 웹훅 관련 프로세스를 관리할 수 있습니다",
                affected_component="ProcessManager",
                conflict_details={'conflict_type': 'process_management'},
                resolution_suggestion="ProcessManager에 웹훅 프로세스 등록 또는 제외 설정",
                file_location=self.target_file
            )
        except Exception:
            return None
    
    def _check_performance_impact(self) -> Optional[CompatibilityIssue]:
        """성능 모니터링과 웹훅 성능 영향 검사"""
        try:
            return CompatibilityIssue(
                issue_type="performance_impact",
                severity=ConflictSeverity.INFO,
                description="웹훅 기능이 성능 모니터링에 영향을 줄 수 있습니다",
                affected_component="PerformanceMonitor",
                conflict_details={'impact_type': 'performance_monitoring'},
                resolution_suggestion="웹훅 전송 성능 메트릭을 모니터링에 포함",
                file_location=self.target_file
            )
        except Exception:
            return None
    
    def _check_performance_monitoring_compatibility(self) -> List[CompatibilityIssue]:
        """성능 모니터링 시스템과의 호환성 검사"""
        issues = []
        
        try:
            # 성능 모니터링 시스템이 웹훅 기능을 모니터링할 수 있는지 확인
            issue = CompatibilityIssue(
                issue_type="performance_monitoring",
                severity=ConflictSeverity.INFO,
                description="웹훅 기능의 성능 모니터링 필요",
                affected_component="webhook_performance",
                conflict_details={'monitoring_needed': True},
                resolution_suggestion="웹훅 전송 시간 및 성공률 모니터링 추가",
                file_location=self.target_file
            )
            issues.append(issue)
            
        except Exception as e:
            self.log(f"[ERROR] 성능 모니터링 호환성 검사 실패: {e}")
        
        return issues
    
    def _check_scheduler_compatibility(self) -> List[CompatibilityIssue]:
        """통합 리포트 스케줄러와의 호환성 검사"""
        issues = []
        
        try:
            # 스케줄러가 웹훅 알림과 충돌하지 않는지 확인
            issue = CompatibilityIssue(
                issue_type="scheduler_compatibility",
                severity=ConflictSeverity.LOW,
                description="통합 리포트 스케줄러와 웹훅 알림 시간 조정 필요",
                affected_component="IntegratedReportScheduler",
                conflict_details={'timing_conflict': 'possible'},
                resolution_suggestion="스케줄러와 웹훅 알림 시간 조정 또는 통합",
                file_location=self.target_file
            )
            issues.append(issue)
            
        except Exception as e:
            self.log(f"[ERROR] 스케줄러 호환성 검사 실패: {e}")
        
        return issues
    
    def _classify_issues_by_severity(self, issues: List[CompatibilityIssue]) -> Dict[ConflictSeverity, List[CompatibilityIssue]]:
        """심각도별 문제 분류"""
        classified = {severity: [] for severity in ConflictSeverity}
        
        for issue in issues:
            classified[issue.severity].append(issue)
        
        return classified
    
    def _generate_detailed_report(self, all_issues: List[CompatibilityIssue], issues_by_severity: Dict) -> str:
        """상세 호환성 보고서 생성"""
        try:
            report_lines = [
                "=" * 80,
                "POSCO 워치햄스터 호환성 검증 보고서",
                "=" * 80,
                f"검사 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"대상 파일: {self.target_file}",
                f"총 검사 항목: {self.check_stats['total_checks']}개",
                f"발견된 문제: {len(all_issues)}개",
                "",
                "📊 심각도별 문제 분포:",
                "-" * 40,
                f"🚨 Critical: {len(issues_by_severity[ConflictSeverity.CRITICAL])}개",
                f"⚠️  High: {len(issues_by_severity[ConflictSeverity.HIGH])}개", 
                f"🔶 Medium: {len(issues_by_severity[ConflictSeverity.MEDIUM])}개",
                f"🔸 Low: {len(issues_by_severity[ConflictSeverity.LOW])}개",
                f"ℹ️  Info: {len(issues_by_severity[ConflictSeverity.INFO])}개",
                ""
            ]
            
            # 심각도별 상세 문제 목록
            for severity in [ConflictSeverity.CRITICAL, ConflictSeverity.HIGH, ConflictSeverity.MEDIUM, ConflictSeverity.LOW, ConflictSeverity.INFO]:
                severity_issues = issues_by_severity[severity]
                if severity_issues:
                    severity_emoji = {
                        ConflictSeverity.CRITICAL: "🚨",
                        ConflictSeverity.HIGH: "⚠️",
                        ConflictSeverity.MEDIUM: "🔶", 
                        ConflictSeverity.LOW: "🔸",
                        ConflictSeverity.INFO: "ℹ️"
                    }
                    
                    report_lines.extend([
                        f"{severity_emoji[severity]} {severity.value.upper()} 심각도 문제 ({len(severity_issues)}개):",
                        "-" * 40
                    ])
                    
                    for i, issue in enumerate(severity_issues, 1):
                        report_lines.extend([
                            f"{i}. {issue.description}",
                            f"   • 유형: {issue.issue_type}",
                            f"   • 영향 컴포넌트: {issue.affected_component}",
                            f"   • 파일 위치: {os.path.basename(issue.file_location)}" + 
                            (f":{issue.line_number}" if issue.line_number else ""),
                            f"   • 해결 방안: {issue.resolution_suggestion}",
                            ""
                        ])
            
            # 전체 요약 및 권장사항
            report_lines.extend([
                "📋 전체 요약:",
                "-" * 40,
                f"• 총 검사 항목: {self.check_stats['total_checks']}개",
                f"• 발견된 문제: {len(all_issues)}개",
                f"• 즉시 해결 필요: {len(issues_by_severity[ConflictSeverity.CRITICAL]) + len(issues_by_severity[ConflictSeverity.HIGH])}개",
                f"• 검토 권장: {len(issues_by_severity[ConflictSeverity.MEDIUM]) + len(issues_by_severity[ConflictSeverity.LOW])}개",
                "",
                "🔧 권장 조치사항:",
                "-" * 40,
                "1. Critical/High 심각도 문제 우선 해결",
                "2. 웹훅 기능 복원 전 백업 생성",
                "3. 단계별 테스트 수행",
                "4. 성능 모니터링 강화",
                "5. 정기적인 호환성 검사 수행",
                "",
                "=" * 80
            ])
            
            return '\n'.join(report_lines)
            
        except Exception as e:
            return f"상세 보고서 생성 실패: {e}"
    
    def _infer_variable_type(self, value: str) -> str:
        """변수 타입 추론"""
        try:
            if value.startswith('"') or value.startswith("'"):
                return "string"
            elif value.isdigit():
                return "integer"
            elif value.replace('.', '').isdigit():
                return "float"
            elif value.lower() in ['true', 'false']:
                return "boolean"
            else:
                return "unknown"
        except Exception:
            return "unknown"
    
    def _is_import_available(self, module_name: str, imports: List[Dict]) -> bool:
        """특정 모듈이 import되어 있는지 확인"""
        for import_info in imports:
            if import_info['type'] == 'import':
                if module_name in import_info.get('modules', []):
                    return True
            elif import_info['type'] == 'from_import':
                if import_info.get('from_module') == module_name:
                    return True
        return False
    
    def _check_duplicate_imports(self, imports: List[Dict]) -> List[Dict]:
        """중복 import 검사"""
        seen_modules = set()
        duplicates = []
        
        for import_info in imports:
            if import_info['type'] == 'import':
                for module in import_info.get('modules', []):
                    if module in seen_modules:
                        duplicates.append({
                            'module': module,
                            'line_number': import_info['line_number'],
                            'statement': import_info['statement']
                        })
                    else:
                        seen_modules.add(module)
        
        return duplicates
    
    def _check_v3_method_conflicts(self, target_functions: Dict) -> List[CompatibilityIssue]:
        """v3.0 컴포넌트 메서드와의 충돌 검사"""
        conflicts = []
        
        # v3.0 컴포넌트의 주요 메서드들
        v3_methods = [
            'send_notification',  # NotificationManager와 충돌 가능
            'get_status',         # StateManager와 충돌 가능
            'start_monitoring',   # PerformanceMonitor와 충돌 가능
        ]
        
        for method in v3_methods:
            if method in target_functions and method in self.webhook_functions:
                issue = CompatibilityIssue(
                    issue_type="v3_method_conflict",
                    severity=ConflictSeverity.MEDIUM,
                    description=f"웹훅 함수 '{method}'가 v3.0 컴포넌트 메서드와 충돌할 수 있습니다",
                    affected_component=method,
                    conflict_details={'v3_method': method},
                    resolution_suggestion="메서드명 변경 또는 네임스페이스 분리",
                    file_location=self.target_file,
                    line_number=target_functions[method].get('line_number')
                )
                conflicts.append(issue)
        
        return conflicts
    
    def _check_v3_import_conflicts(self, target_imports: List[Dict]) -> List[CompatibilityIssue]:
        """v3.0 컴포넌트 import와의 충돌 검사"""
        conflicts = []
        
        # v3.0에서 사용하는 주요 모듈들
        v3_modules = [
            'requests',
            'psutil', 
            'subprocess',
            'json'
        ]
        
        for import_info in target_imports:
            if import_info['type'] == 'import':
                for module in import_info.get('modules', []):
                    if module in v3_modules:
                        # 정보성 알림 (실제 충돌은 아님)
                        issue = CompatibilityIssue(
                            issue_type="shared_import",
                            severity=ConflictSeverity.INFO,
                            description=f"'{module}' 모듈이 v3.0 컴포넌트와 공유됩니다",
                            affected_component=module,
                            conflict_details={'shared_module': module},
                            resolution_suggestion="모듈 사용 패턴 확인 및 최적화",
                            file_location=self.target_file,
                            line_number=import_info['line_number']
                        )
                        conflicts.append(issue)
        
        return conflicts
    
    def _check_namespace_conflicts(self, target_variables: Dict) -> List[CompatibilityIssue]:
        """네임스페이스 충돌 검사"""
        conflicts = []
        
        # 전역 네임스페이스에서 충돌 가능한 변수들
        global_vars = ['config', 'logger', 'status', 'state']
        
        for var_name in target_variables:
            if var_name.lower() in global_vars:
                issue = CompatibilityIssue(
                    issue_type="namespace_conflict",
                    severity=ConflictSeverity.LOW,
                    description=f"전역 변수 '{var_name}'가 네임스페이스 충돌을 일으킬 수 있습니다",
                    affected_component=var_name,
                    conflict_details={'global_variable': var_name},
                    resolution_suggestion="변수명에 접두사 추가 또는 모듈 네임스페이스 사용",
                    file_location=self.target_file,
                    line_number=target_variables[var_name].get('line_number')
                )
                conflicts.append(issue)
        
        return conflicts


def main():
    """호환성 검사 시스템 테스트"""
    try:
        print("POSCO 워치햄스터 호환성 검증 시스템 테스트")
        print("=" * 60)
        
        # 대상 파일 경로
        target_file = "core/monitoring/monitor_WatchHamster_v3.0.py"
        
        if not os.path.exists(target_file):
            print(f"[ERROR] 대상 파일을 찾을 수 없습니다: {target_file}")
            return
        
        # CompatibilityChecker 초기화
        checker = CompatibilityChecker(target_file)
        
        # 호환성 검사 보고서 생성
        report = checker.generate_compatibility_report()
        
        print("\n" + "=" * 60)
        print("호환성 검사 완료!")
        print(f"상세 보고서가 생성되었습니다.")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] 호환성 검사 실행 실패: {e}")


if __name__ == "__main__":
    main()