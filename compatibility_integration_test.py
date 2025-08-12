#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 호환성 검증 통합 테스트
WebhookMessageRestorer와 CompatibilityChecker 연동 테스트

Created: 2025-01-06
Updated: 2025-01-06
Author: POSCO 시스템 관리자

Requirements: 3.1, 3.2
- WebhookMessageRestorer와 CompatibilityChecker 통합 테스트
- 실제 복원 시나리오에서의 호환성 검증
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# 로컬 모듈 import
try:
    from webhook_message_restorer import WebhookMessageRestorer
    from compatibility_checker import CompatibilityChecker, ConflictSeverity
except ImportError as e:
    print(f"[ERROR] 필수 모듈 import 실패: {e}")
    sys.exit(1)

class CompatibilityIntegrationTest:
    """
    WebhookMessageRestorer와 CompatibilityChecker 통합 테스트 클래스
    
    실제 웹훅 복원 시나리오에서 호환성 문제를 사전에 검증하고
    복원 작업의 안전성을 보장합니다.
    """
    
    def __init__(self, target_file_path: str, source_commit: str = "a763ef8"):
        """
        통합 테스트 초기화
        
        Args:
            target_file_path (str): 대상 파일 경로
            source_commit (str): 원본 커밋 해시
        """
        self.target_file = target_file_path
        self.source_commit = source_commit
        
        # 컴포넌트 초기화
        self.webhook_restorer = None
        self.compatibility_checker = None
        
        # 테스트 결과 저장
        self.test_results = {
            'pre_restoration_check': {},
            'post_restoration_check': {},
            'integration_issues': [],
            'recommendations': []
        }
        
        # 로그 파일 설정
        self.log_file = "compatibility_integration_test.log"
        
        print(f"[INFO] CompatibilityIntegrationTest 초기화 완료")
        print(f"[INFO] 대상 파일: {self.target_file}")
        print(f"[INFO] 원본 커밋: {self.source_commit}")
    
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
    
    def run_comprehensive_compatibility_test(self) -> Dict:
        """
        종합적인 호환성 테스트 실행
        
        Returns:
            Dict: 테스트 결과 종합 보고서
        """
        try:
            self.log("[INFO] 종합 호환성 테스트 시작...")
            
            # 1단계: 복원 전 호환성 검사
            self.log("[STEP 1] 복원 전 호환성 검사 수행...")
            pre_check_results = self._run_pre_restoration_check()
            self.test_results['pre_restoration_check'] = pre_check_results
            
            # 2단계: WebhookMessageRestorer 초기화 및 함수 추출
            self.log("[STEP 2] WebhookMessageRestorer 초기화...")
            self.webhook_restorer = WebhookMessageRestorer(self.target_file, self.source_commit)
            
            # 백업 생성
            if not self.webhook_restorer.create_backup():
                self.log("[ERROR] 백업 생성 실패 - 테스트 중단")
                return self._generate_error_report("백업 생성 실패")
            
            # 웹훅 함수 추출
            if not self.webhook_restorer.extract_webhook_functions():
                self.log("[ERROR] 웹훅 함수 추출 실패 - 테스트 중단")
                return self._generate_error_report("웹훅 함수 추출 실패")
            
            # 3단계: 추출된 함수와 현재 시스템 간 호환성 검사
            self.log("[STEP 3] 추출된 함수 호환성 검사...")
            self.compatibility_checker = CompatibilityChecker(self.target_file, self.webhook_restorer)
            
            # 상세 호환성 검사 수행
            compatibility_report = self.compatibility_checker.generate_compatibility_report()
            
            # 4단계: 통합 문제 분석
            self.log("[STEP 4] 통합 문제 분석...")
            integration_issues = self._analyze_integration_issues()
            self.test_results['integration_issues'] = integration_issues
            
            # 5단계: 권장사항 생성
            self.log("[STEP 5] 권장사항 생성...")
            recommendations = self._generate_recommendations()
            self.test_results['recommendations'] = recommendations
            
            # 6단계: 종합 보고서 생성
            self.log("[STEP 6] 종합 보고서 생성...")
            comprehensive_report = self._generate_comprehensive_report()
            
            self.log("[SUCCESS] 종합 호환성 테스트 완료!")
            return comprehensive_report
            
        except Exception as e:
            self.log(f"[ERROR] 종합 호환성 테스트 실패: {e}")
            return self._generate_error_report(f"테스트 실행 실패: {str(e)}")
    
    def _run_pre_restoration_check(self) -> Dict:
        """
        복원 전 기본 호환성 검사
        
        Returns:
            Dict: 복원 전 검사 결과
        """
        try:
            # 기본 CompatibilityChecker로 현재 상태 검사
            basic_checker = CompatibilityChecker(self.target_file)
            
            # 각 검사 항목별 실행
            function_conflicts = basic_checker.check_function_conflicts()
            variable_conflicts = basic_checker.check_variable_conflicts()
            import_conflicts = basic_checker.check_import_conflicts()
            system_conflicts = basic_checker.check_system_interaction_compatibility()
            
            return {
                'function_conflicts': len(function_conflicts),
                'variable_conflicts': len(variable_conflicts),
                'import_conflicts': len(import_conflicts),
                'system_conflicts': len(system_conflicts),
                'total_issues': len(function_conflicts) + len(variable_conflicts) + 
                              len(import_conflicts) + len(system_conflicts),
                'details': {
                    'functions': function_conflicts,
                    'variables': variable_conflicts,
                    'imports': import_conflicts,
                    'system': system_conflicts
                }
            }
            
        except Exception as e:
            self.log(f"[ERROR] 복원 전 검사 실패: {e}")
            return {'error': str(e)}
    
    def _analyze_integration_issues(self) -> List[Dict]:
        """
        WebhookMessageRestorer와 CompatibilityChecker 통합 시 발생할 수 있는 문제 분석
        
        Returns:
            List[Dict]: 통합 문제 목록
        """
        integration_issues = []
        
        try:
            # 1. 추출된 웹훅 함수와 기존 함수 간 시그니처 차이 분석
            if hasattr(self.webhook_restorer, 'extracted_functions'):
                for func_name, func_content in self.webhook_restorer.extracted_functions.items():
                    issue = self._analyze_function_signature_compatibility(func_name, func_content)
                    if issue:
                        integration_issues.append(issue)
            
            # 2. 추출된 웹훅 상수와 기존 상수 간 값 차이 분석
            if hasattr(self.webhook_restorer, 'extracted_constants'):
                for const_name, const_value in self.webhook_restorer.extracted_constants.items():
                    issue = self._analyze_constant_value_compatibility(const_name, const_value)
                    if issue:
                        integration_issues.append(issue)
            
            # 3. v3.0 아키텍처와의 통합 호환성 분석
            v3_integration_issues = self._analyze_v3_integration_compatibility()
            integration_issues.extend(v3_integration_issues)
            
            # 4. 성능 영향 분석
            performance_issues = self._analyze_performance_impact()
            integration_issues.extend(performance_issues)
            
            self.log(f"[INFO] 통합 문제 분석 완료: {len(integration_issues)}개 문제 발견")
            return integration_issues
            
        except Exception as e:
            self.log(f"[ERROR] 통합 문제 분석 실패: {e}")
            return [{'error': f'통합 문제 분석 실패: {str(e)}'}]
    
    def _analyze_function_signature_compatibility(self, func_name: str, func_content: str) -> Optional[Dict]:
        """
        함수 시그니처 호환성 분석
        
        Args:
            func_name (str): 함수명
            func_content (str): 함수 내용
            
        Returns:
            Optional[Dict]: 호환성 문제 (없으면 None)
        """
        try:
            # 함수 시그니처 추출
            lines = func_content.split('\n')
            signature_line = None
            
            for line in lines:
                if f"def {func_name}(" in line:
                    signature_line = line.strip()
                    break
            
            if not signature_line:
                return {
                    'type': 'signature_analysis_failed',
                    'function': func_name,
                    'severity': 'medium',
                    'description': f'{func_name} 함수의 시그니처를 분석할 수 없습니다',
                    'recommendation': '수동으로 함수 시그니처 확인 필요'
                }
            
            # 간단한 시그니처 분석 (실제로는 더 정교한 분석 필요)
            if 'self' not in signature_line:
                return {
                    'type': 'signature_compatibility',
                    'function': func_name,
                    'severity': 'low',
                    'description': f'{func_name} 함수가 클래스 메서드가 아닐 수 있습니다',
                    'signature': signature_line,
                    'recommendation': '함수가 올바른 클래스 컨텍스트에서 호출되는지 확인'
                }
            
            return None
            
        except Exception as e:
            return {
                'type': 'signature_analysis_error',
                'function': func_name,
                'severity': 'high',
                'description': f'{func_name} 함수 시그니처 분석 중 오류 발생: {str(e)}',
                'recommendation': '수동 검토 필요'
            }
    
    def _analyze_constant_value_compatibility(self, const_name: str, const_value: str) -> Optional[Dict]:
        """
        상수값 호환성 분석
        
        Args:
            const_name (str): 상수명
            const_value (str): 상수값
            
        Returns:
            Optional[Dict]: 호환성 문제 (없으면 None)
        """
        try:
            # URL 형식 검증
            if const_name.endswith('_URL'):
                if not const_value.startswith('https://'):
                    return {
                        'type': 'url_format_issue',
                        'constant': const_name,
                        'severity': 'high',
                        'description': f'{const_name}이 올바른 HTTPS URL 형식이 아닙니다',
                        'value': const_value[:50] + "..." if len(const_value) > 50 else const_value,
                        'recommendation': 'URL 형식 확인 및 수정'
                    }
                
                # Dooray 웹훅 URL 특화 검증
                if 'dooray.com' in const_value and '/services/' not in const_value:
                    return {
                        'type': 'dooray_webhook_format',
                        'constant': const_name,
                        'severity': 'medium',
                        'description': f'{const_name}이 올바른 Dooray 웹훅 URL 형식이 아닐 수 있습니다',
                        'recommendation': 'Dooray 웹훅 URL 형식 확인'
                    }
            
            return None
            
        except Exception as e:
            return {
                'type': 'constant_analysis_error',
                'constant': const_name,
                'severity': 'medium',
                'description': f'{const_name} 상수 분석 중 오류 발생: {str(e)}',
                'recommendation': '수동 검토 필요'
            }
    
    def _analyze_v3_integration_compatibility(self) -> List[Dict]:
        """
        v3.0 아키텍처와의 통합 호환성 분석
        
        Returns:
            List[Dict]: v3.0 통합 문제 목록
        """
        issues = []
        
        try:
            # v3.0 컴포넌트 활성화 상태 확인
            v3_components = [
                'ProcessManager', 'StateManager', 'ColorfulConsoleUI',
                'ModuleRegistry', 'NotificationManager', 'PerformanceMonitor'
            ]
            
            inactive_components = []
            for component in v3_components:
                try:
                    # 간단한 import 테스트
                    if component == 'ProcessManager':
                        from core.process_manager import ProcessManager
                    elif component == 'StateManager':
                        from core.state_manager import StateManager
                    # ... 다른 컴포넌트들
                except ImportError:
                    inactive_components.append(component)
            
            if inactive_components:
                issues.append({
                    'type': 'v3_components_inactive',
                    'severity': 'medium',
                    'description': f'v3.0 컴포넌트 {len(inactive_components)}개가 비활성화되어 있습니다',
                    'inactive_components': inactive_components,
                    'recommendation': '비활성화된 컴포넌트 활성화 또는 대체 방안 구현'
                })
            
            # NotificationManager와 웹훅 기능 중복 검사
            if 'NotificationManager' not in inactive_components:
                issues.append({
                    'type': 'notification_duplication',
                    'severity': 'medium',
                    'description': 'NotificationManager와 웹훅 알림 기능이 중복될 수 있습니다',
                    'recommendation': '알림 기능 통합 또는 역할 분리 필요'
                })
            
            return issues
            
        except Exception as e:
            return [{
                'type': 'v3_integration_analysis_error',
                'severity': 'high',
                'description': f'v3.0 통합 분석 중 오류 발생: {str(e)}',
                'recommendation': '수동 검토 필요'
            }]
    
    def _analyze_performance_impact(self) -> List[Dict]:
        """
        성능 영향 분석
        
        Returns:
            List[Dict]: 성능 영향 문제 목록
        """
        issues = []
        
        try:
            # 웹훅 함수 수에 따른 성능 영향 분석
            if hasattr(self.webhook_restorer, 'extracted_functions'):
                func_count = len(self.webhook_restorer.extracted_functions)
                
                if func_count > 5:
                    issues.append({
                        'type': 'performance_impact_high',
                        'severity': 'low',
                        'description': f'복원될 웹훅 함수가 {func_count}개로 많아 성능에 영향을 줄 수 있습니다',
                        'recommendation': '웹훅 함수 호출 빈도 최적화 고려'
                    })
            
            # 웹훅 URL 수에 따른 네트워크 부하 분석
            if hasattr(self.webhook_restorer, 'extracted_constants'):
                url_count = sum(1 for name in self.webhook_restorer.extracted_constants.keys() 
                              if name.endswith('_URL'))
                
                if url_count > 2:
                    issues.append({
                        'type': 'network_load_impact',
                        'severity': 'info',
                        'description': f'웹훅 URL이 {url_count}개로 네트워크 부하가 증가할 수 있습니다',
                        'recommendation': '웹훅 전송 빈도 및 배치 처리 고려'
                    })
            
            return issues
            
        except Exception as e:
            return [{
                'type': 'performance_analysis_error',
                'severity': 'medium',
                'description': f'성능 영향 분석 중 오류 발생: {str(e)}',
                'recommendation': '수동 성능 테스트 수행'
            }]
    
    def _generate_recommendations(self) -> List[Dict]:
        """
        종합 권장사항 생성
        
        Returns:
            List[Dict]: 권장사항 목록
        """
        recommendations = []
        
        try:
            # 1. 복원 전 필수 조치사항
            recommendations.append({
                'category': 'pre_restoration',
                'priority': 'high',
                'title': '복원 전 백업 및 테스트 환경 구성',
                'description': '웹훅 기능 복원 전 현재 시스템의 완전한 백업을 생성하고 테스트 환경에서 먼저 검증',
                'actions': [
                    '현재 시스템 전체 백업 생성',
                    '테스트 환경 구성',
                    '복원 작업 단계별 계획 수립'
                ]
            })
            
            # 2. 호환성 문제 해결
            if self.test_results.get('integration_issues'):
                high_severity_issues = [
                    issue for issue in self.test_results['integration_issues'] 
                    if issue.get('severity') == 'high'
                ]
                
                if high_severity_issues:
                    recommendations.append({
                        'category': 'compatibility_fix',
                        'priority': 'critical',
                        'title': '높은 심각도 호환성 문제 해결',
                        'description': f'{len(high_severity_issues)}개의 높은 심각도 문제를 우선 해결',
                        'actions': [issue.get('recommendation', '수동 검토 필요') 
                                  for issue in high_severity_issues]
                    })
            
            # 3. v3.0 아키텍처 통합
            recommendations.append({
                'category': 'v3_integration',
                'priority': 'medium',
                'title': 'v3.0 아키텍처와의 통합 최적화',
                'description': '웹훅 기능을 v3.0 아키텍처 컴포넌트와 효율적으로 통합',
                'actions': [
                    'NotificationManager와 웹훅 기능 통합 검토',
                    'ProcessManager에 웹훅 프로세스 등록',
                    'PerformanceMonitor에 웹훅 성능 메트릭 추가'
                ]
            })
            
            # 4. 복원 후 검증
            recommendations.append({
                'category': 'post_restoration',
                'priority': 'high',
                'title': '복원 후 종합 검증',
                'description': '웹훅 기능 복원 후 전체 시스템의 정상 동작 확인',
                'actions': [
                    '웹훅 메시지 전송 테스트',
                    'Dooray 알림 수신 확인',
                    '기존 기능 회귀 테스트',
                    '성능 영향 모니터링'
                ]
            })
            
            # 5. 지속적인 모니터링
            recommendations.append({
                'category': 'monitoring',
                'priority': 'medium',
                'title': '지속적인 호환성 모니터링',
                'description': '복원 후 지속적인 호환성 및 성능 모니터링 체계 구축',
                'actions': [
                    '정기적인 호환성 검사 스케줄링',
                    '웹훅 성능 메트릭 수집',
                    '알림 전송 성공률 모니터링',
                    '시스템 업데이트 시 호환성 재검증'
                ]
            })
            
            return recommendations
            
        except Exception as e:
            self.log(f"[ERROR] 권장사항 생성 실패: {e}")
            return [{
                'category': 'error',
                'priority': 'high',
                'title': '권장사항 생성 실패',
                'description': f'권장사항 생성 중 오류 발생: {str(e)}',
                'actions': ['수동으로 복원 계획 수립']
            }]
    
    def _generate_comprehensive_report(self) -> Dict:
        """
        종합 보고서 생성
        
        Returns:
            Dict: 종합 테스트 결과 보고서
        """
        try:
            report = {
                'test_summary': {
                    'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'target_file': self.target_file,
                    'source_commit': self.source_commit,
                    'test_status': 'completed'
                },
                'pre_restoration_check': self.test_results.get('pre_restoration_check', {}),
                'webhook_extraction': {
                    'functions_extracted': len(self.webhook_restorer.extracted_functions) if self.webhook_restorer else 0,
                    'constants_extracted': len(self.webhook_restorer.extracted_constants) if self.webhook_restorer else 0,
                    'extraction_success': bool(self.webhook_restorer and self.webhook_restorer.extracted_functions)
                },
                'compatibility_analysis': {
                    'total_issues': len(self.test_results.get('integration_issues', [])),
                    'critical_issues': len([i for i in self.test_results.get('integration_issues', []) if i.get('severity') == 'high']),
                    'medium_issues': len([i for i in self.test_results.get('integration_issues', []) if i.get('severity') == 'medium']),
                    'low_issues': len([i for i in self.test_results.get('integration_issues', []) if i.get('severity') == 'low'])
                },
                'integration_issues': self.test_results.get('integration_issues', []),
                'recommendations': self.test_results.get('recommendations', []),
                'overall_assessment': self._generate_overall_assessment()
            }
            
            # 보고서 파일 저장 (JSON 직렬화 가능한 형태로 변환)
            serializable_report = self._make_json_serializable(report)
            report_file = f"compatibility_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_report, f, ensure_ascii=False, indent=2)
            
            self.log(f"[SUCCESS] 종합 보고서 저장: {report_file}")
            return report
            
        except Exception as e:
            self.log(f"[ERROR] 종합 보고서 생성 실패: {e}")
            return self._generate_error_report(f"보고서 생성 실패: {str(e)}")
    
    def _generate_overall_assessment(self) -> Dict:
        """
        전체 평가 생성
        
        Returns:
            Dict: 전체 평가 결과
        """
        try:
            issues = self.test_results.get('integration_issues', [])
            critical_count = len([i for i in issues if i.get('severity') == 'high'])
            medium_count = len([i for i in issues if i.get('severity') == 'medium'])
            
            # 위험도 평가
            if critical_count > 0:
                risk_level = 'high'
                recommendation = '복원 작업 전 Critical 문제 해결 필수'
            elif medium_count > 3:
                risk_level = 'medium'
                recommendation = '복원 작업 시 주의 깊은 모니터링 필요'
            else:
                risk_level = 'low'
                recommendation = '복원 작업 진행 가능, 기본 검증 수행'
            
            # 복원 가능성 평가
            extraction_success = bool(self.webhook_restorer and self.webhook_restorer.extracted_functions)
            
            if extraction_success and critical_count == 0:
                restoration_feasibility = 'high'
            elif extraction_success and critical_count <= 2:
                restoration_feasibility = 'medium'
            else:
                restoration_feasibility = 'low'
            
            return {
                'risk_level': risk_level,
                'restoration_feasibility': restoration_feasibility,
                'critical_issues_count': critical_count,
                'medium_issues_count': medium_count,
                'recommendation': recommendation,
                'next_steps': self._generate_next_steps(risk_level, restoration_feasibility)
            }
            
        except Exception as e:
            return {
                'risk_level': 'unknown',
                'restoration_feasibility': 'unknown',
                'error': f'평가 생성 실패: {str(e)}',
                'recommendation': '수동 평가 필요'
            }
    
    def _make_json_serializable(self, obj):
        """객체를 JSON 직렬화 가능한 형태로 변환"""
        try:
            # 기본 타입은 그대로 반환
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            elif hasattr(obj, 'value'):  # Enum 처리
                return obj.value
            elif isinstance(obj, dict):
                return {str(key): self._make_json_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [self._make_json_serializable(item) for item in obj]
            elif hasattr(obj, '__dict__'):
                return {key: self._make_json_serializable(value) for key, value in obj.__dict__.items() if not key.startswith('_')}
            else:
                return str(obj)
        except:
            return str(obj)
    
    def _generate_next_steps(self, risk_level: str, feasibility: str) -> List[str]:
        """
        다음 단계 권장사항 생성
        
        Args:
            risk_level (str): 위험도 수준
            feasibility (str): 복원 가능성
            
        Returns:
            List[str]: 다음 단계 목록
        """
        if risk_level == 'high':
            return [
                '1. Critical 문제 우선 해결',
                '2. 테스트 환경에서 복원 작업 시뮬레이션',
                '3. 문제 해결 후 재검증',
                '4. 단계별 복원 작업 수행'
            ]
        elif risk_level == 'medium':
            return [
                '1. Medium 문제 검토 및 해결 계획 수립',
                '2. 백업 생성 및 롤백 계획 준비',
                '3. 모니터링 강화하여 복원 작업 수행',
                '4. 복원 후 즉시 검증'
            ]
        else:
            return [
                '1. 백업 생성',
                '2. 복원 작업 수행',
                '3. 기본 검증 테스트',
                '4. 정상 동작 확인'
            ]
    
    def _generate_error_report(self, error_message: str) -> Dict:
        """
        오류 보고서 생성
        
        Args:
            error_message (str): 오류 메시지
            
        Returns:
            Dict: 오류 보고서
        """
        return {
            'test_summary': {
                'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'target_file': self.target_file,
                'source_commit': self.source_commit,
                'test_status': 'failed'
            },
            'error': error_message,
            'recommendations': [{
                'category': 'error_recovery',
                'priority': 'critical',
                'title': '테스트 실패 복구',
                'description': '호환성 테스트 실행 중 오류가 발생했습니다',
                'actions': [
                    '오류 원인 분석',
                    '필요한 모듈 및 파일 확인',
                    '수동 호환성 검사 수행'
                ]
            }]
        }


def main():
    """통합 호환성 테스트 실행"""
    try:
        print("POSCO 워치햄스터 호환성 검증 통합 테스트")
        print("=" * 60)
        
        # 대상 파일 경로
        target_file = "core/monitoring/monitor_WatchHamster_v3.0.py"
        
        if not os.path.exists(target_file):
            print(f"[ERROR] 대상 파일을 찾을 수 없습니다: {target_file}")
            return
        
        # 통합 테스트 실행
        integration_test = CompatibilityIntegrationTest(target_file)
        test_results = integration_test.run_comprehensive_compatibility_test()
        
        # 결과 요약 출력
        print("\n" + "=" * 60)
        print("통합 호환성 테스트 완료!")
        print("=" * 60)
        
        if 'error' in test_results:
            print(f"❌ 테스트 실패: {test_results['error']}")
        else:
            assessment = test_results.get('overall_assessment', {})
            print(f"🎯 위험도 수준: {assessment.get('risk_level', 'unknown')}")
            print(f"🔧 복원 가능성: {assessment.get('restoration_feasibility', 'unknown')}")
            print(f"⚠️ Critical 문제: {assessment.get('critical_issues_count', 0)}개")
            print(f"🔶 Medium 문제: {assessment.get('medium_issues_count', 0)}개")
            print(f"💡 권장사항: {assessment.get('recommendation', 'N/A')}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] 통합 테스트 실행 실패: {e}")


if __name__ == "__main__":
    main()