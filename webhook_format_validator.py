#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 메시지 포맷 자동 검증 로직
메시지 내용과 포맷 정확성을 자동으로 검증하는 시스템

Requirements: 4.1, 4.2
- 메시지 내용과 포맷 정확성 자동 검증 로직 구현
"""

import re
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    """검증 수준"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationRule:
    """검증 규칙"""
    name: str
    description: str
    pattern: Optional[str] = None
    validator_func: Optional[callable] = None
    level: ValidationLevel = ValidationLevel.WARNING
    required: bool = False

@dataclass
class ValidationResult:
    """검증 결과"""
    rule_name: str
    passed: bool
    level: ValidationLevel
    message: str
    details: Dict[str, Any] = None

class WebhookMessageFormatValidator:
    """웹훅 메시지 포맷 검증기"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.validation_history = []
    
    def _initialize_validation_rules(self) -> List[ValidationRule]:
        """검증 규칙 초기화"""
        return [
            # 1. 줄바꿈 문자 검증
            ValidationRule(
                name="line_breaks",
                description="줄바꿈 문자는 \\n을 사용해야 하며 /n은 사용하면 안됨",
                validator_func=self._validate_line_breaks,
                level=ValidationLevel.CRITICAL,
                required=True
            ),
            
            # 2. 제품명 검증
            ValidationRule(
                name="product_name",
                description="POSCO 워치햄스터 제품명이 올바르게 포함되어야 함",
                validator_func=self._validate_product_name,
                level=ValidationLevel.CRITICAL,
                required=True
            ),
            
            # 3. 한국어 인코딩 검증
            ValidationRule(
                name="korean_encoding",
                description="한국어 텍스트가 올바르게 인코딩되어야 함",
                pattern=r'[가-힣]+',
                level=ValidationLevel.WARNING,
                required=False
            ),
            
            # 4. JSON 구조 검증
            ValidationRule(
                name="json_structure",
                description="Dooray 웹훅 JSON 구조가 올바라야 함",
                validator_func=self._validate_json_structure,
                level=ValidationLevel.CRITICAL,
                required=True
            ),
            
            # 5. 웹훅 URL 검증
            ValidationRule(
                name="webhook_url",
                description="Dooray 웹훅 URL 형식이 올바라야 함",
                pattern=r'https://[^/]+\.dooray\.com/services/\d+/\d+/[A-Za-z0-9_-]+',
                level=ValidationLevel.WARNING,
                required=False
            ),
            
            # 6. 메시지 길이 검증
            ValidationRule(
                name="message_length",
                description="메시지 길이가 적절해야 함 (너무 길거나 짧으면 안됨)",
                validator_func=self._validate_message_length,
                level=ValidationLevel.WARNING,
                required=False
            ),
            
            # 7. 색상 코드 검증
            ValidationRule(
                name="color_code",
                description="메시지 색상 코드가 올바른 형식이어야 함",
                pattern=r'#[0-9A-Fa-f]{6}',
                level=ValidationLevel.INFO,
                required=False
            ),
            
            # 8. 타임스탬프 형식 검증
            ValidationRule(
                name="timestamp_format",
                description="타임스탬프가 올바른 형식이어야 함",
                validator_func=self._validate_timestamp_format,
                level=ValidationLevel.INFO,
                required=False
            ),
            
            # 9. 특수문자 검증
            ValidationRule(
                name="special_characters",
                description="특수문자가 올바르게 이스케이프되어야 함",
                validator_func=self._validate_special_characters,
                level=ValidationLevel.WARNING,
                required=False
            ),
            
            # 10. 메시지 일관성 검증
            ValidationRule(
                name="message_consistency",
                description="메시지 스타일과 용어가 일관되어야 함",
                validator_func=self._validate_message_consistency,
                level=ValidationLevel.INFO,
                required=False
            )
        ]
    
    def _validate_line_breaks(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """줄바꿈 문자 검증"""
        invalid_breaks = content.count('/n')
        valid_breaks = content.count('\\n')
        
        details = {
            'invalid_count': invalid_breaks,
            'valid_count': valid_breaks,
            'total_breaks': invalid_breaks + valid_breaks
        }
        
        if invalid_breaks > 0:
            return False, f"잘못된 줄바꿈 문자 '/n'이 {invalid_breaks}개 발견됨", details
        
        return True, f"줄바꿈 문자 검증 통과 (\\n {valid_breaks}개 사용)", details
    
    def _validate_product_name(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """제품명 검증"""
        product_names = ['POSCO 워치햄스터', 'POSCO WatchHamster', '워치햄스터']
        found_names = []
        
        for name in product_names:
            if name in content:
                found_names.append(name)
        
        details = {
            'found_names': found_names,
            'searched_names': product_names
        }
        
        if not found_names:
            return False, "제품명이 메시지에 포함되지 않음", details
        
        return True, f"제품명 검증 통과 ({', '.join(found_names)})", details
    
    def _validate_json_structure(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """JSON 구조 검증"""
        required_fields = ['botName', 'attachments']
        optional_fields = ['color', 'text', 'title']
        
        found_fields = []
        missing_fields = []
        
        for field in required_fields:
            if f'"{field}"' in content or f"'{field}'" in content:
                found_fields.append(field)
            else:
                missing_fields.append(field)
        
        details = {
            'found_fields': found_fields,
            'missing_fields': missing_fields,
            'required_fields': required_fields
        }
        
        if missing_fields:
            return False, f"필수 JSON 필드 누락: {', '.join(missing_fields)}", details
        
        return True, f"JSON 구조 검증 통과 ({len(found_fields)}개 필드 확인)", details
    
    def _validate_message_length(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """메시지 길이 검증"""
        min_length = 10
        max_length = 4000  # Dooray 메시지 길이 제한
        
        length = len(content)
        details = {
            'length': length,
            'min_length': min_length,
            'max_length': max_length
        }
        
        if length < min_length:
            return False, f"메시지가 너무 짧음 ({length}자, 최소 {min_length}자)", details
        
        if length > max_length:
            return False, f"메시지가 너무 김 ({length}자, 최대 {max_length}자)", details
        
        return True, f"메시지 길이 적절 ({length}자)", details
    
    def _validate_timestamp_format(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """타임스탬프 형식 검증"""
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',  # YYYY/MM/DD HH:MM:SS
            r'\d{2}:\d{2}:\d{2}',                     # HH:MM:SS
        ]
        
        found_timestamps = []
        for pattern in timestamp_patterns:
            matches = re.findall(pattern, content)
            found_timestamps.extend(matches)
        
        details = {
            'found_timestamps': found_timestamps,
            'patterns_checked': len(timestamp_patterns)
        }
        
        if not found_timestamps:
            return True, "타임스탬프 없음 (선택사항)", details  # 타임스탬프는 선택사항
        
        return True, f"타임스탬프 형식 검증 통과 ({len(found_timestamps)}개 발견)", details
    
    def _validate_special_characters(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """특수문자 검증"""
        problematic_chars = {
            '"': 'JSON에서 이스케이프되지 않은 따옴표',
            '\\': '이스케이프되지 않은 백슬래시',
            '\t': '탭 문자 (공백으로 대체 권장)',
            '\r': '캐리지 리턴 (제거 권장)'
        }
        
        found_issues = []
        for char, description in problematic_chars.items():
            if char in content:
                count = content.count(char)
                found_issues.append({
                    'character': char,
                    'count': count,
                    'description': description
                })
        
        details = {
            'found_issues': found_issues,
            'checked_characters': list(problematic_chars.keys())
        }
        
        if found_issues:
            issue_summary = ', '.join([f"{issue['character']}({issue['count']}개)" for issue in found_issues])
            return False, f"특수문자 문제 발견: {issue_summary}", details
        
        return True, "특수문자 검증 통과", details
    
    def _validate_message_consistency(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """메시지 일관성 검증"""
        consistency_checks = {
            'formal_tone': {
                'patterns': [r'습니다', r'입니다', r'됩니다'],
                'description': '정중한 존댓말 사용'
            },
            'technical_terms': {
                'patterns': [r'시스템', r'프로세스', r'모니터링', r'상태'],
                'description': '기술 용어 사용'
            },
            'time_expressions': {
                'patterns': [r'\d+시', r'\d+분', r'시간', r'분간'],
                'description': '시간 표현 사용'
            }
        }
        
        consistency_results = {}
        for check_name, check_info in consistency_checks.items():
            found_patterns = []
            for pattern in check_info['patterns']:
                matches = re.findall(pattern, content)
                found_patterns.extend(matches)
            
            consistency_results[check_name] = {
                'found': len(found_patterns) > 0,
                'count': len(found_patterns),
                'patterns': found_patterns
            }
        
        details = {
            'consistency_results': consistency_results
        }
        
        # 일관성 점수 계산
        consistency_score = sum(1 for result in consistency_results.values() if result['found'])
        total_checks = len(consistency_checks)
        
        if consistency_score >= total_checks * 0.7:  # 70% 이상
            return True, f"메시지 일관성 양호 ({consistency_score}/{total_checks})", details
        
        return False, f"메시지 일관성 부족 ({consistency_score}/{total_checks})", details
    
    def validate_content(self, content: str, rule_names: List[str] = None) -> List[ValidationResult]:
        """콘텐츠 검증 실행"""
        results = []
        
        # 검증할 규칙 선택
        rules_to_check = self.validation_rules
        if rule_names:
            rules_to_check = [rule for rule in self.validation_rules if rule.name in rule_names]
        
        for rule in rules_to_check:
            try:
                if rule.validator_func:
                    # 커스텀 검증 함수 사용
                    passed, message, details = rule.validator_func(content)
                elif rule.pattern:
                    # 정규식 패턴 사용
                    matches = re.findall(rule.pattern, content)
                    passed = len(matches) > 0
                    message = f"패턴 매칭: {len(matches)}개 발견" if passed else "패턴 매칭 실패"
                    details = {'matches': matches, 'pattern': rule.pattern}
                else:
                    # 기본 검증 (항상 통과)
                    passed = True
                    message = "기본 검증 통과"
                    details = {}
                
                result = ValidationResult(
                    rule_name=rule.name,
                    passed=passed,
                    level=rule.level,
                    message=message,
                    details=details
                )
                
                results.append(result)
                
            except Exception as e:
                # 검증 중 오류 발생
                error_result = ValidationResult(
                    rule_name=rule.name,
                    passed=False,
                    level=ValidationLevel.CRITICAL,
                    message=f"검증 중 오류 발생: {str(e)}",
                    details={'error': str(e)}
                )
                results.append(error_result)
        
        # 검증 기록 저장
        self.validation_history.append({
            'timestamp': datetime.now(),
            'content_length': len(content),
            'rules_checked': len(rules_to_check),
            'results': results
        })
        
        return results
    
    def validate_json_message(self, json_data: Dict[str, Any]) -> List[ValidationResult]:
        """JSON 메시지 검증"""
        # JSON을 문자열로 변환하여 검증
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        return self.validate_content(json_str)
    
    def generate_validation_report(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """검증 보고서 생성"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_rules': len(results),
            'passed_rules': sum(1 for r in results if r.passed),
            'failed_rules': sum(1 for r in results if not r.passed),
            'critical_issues': sum(1 for r in results if not r.passed and r.level == ValidationLevel.CRITICAL),
            'warnings': sum(1 for r in results if not r.passed and r.level == ValidationLevel.WARNING),
            'info_issues': sum(1 for r in results if not r.passed and r.level == ValidationLevel.INFO),
            'success_rate': 0,
            'overall_status': 'UNKNOWN',
            'results_by_level': {
                'critical': [],
                'warning': [],
                'info': []
            },
            'detailed_results': []
        }
        
        # 성공률 계산
        if report['total_rules'] > 0:
            report['success_rate'] = (report['passed_rules'] / report['total_rules']) * 100
        
        # 전체 상태 결정
        if report['critical_issues'] > 0:
            report['overall_status'] = 'CRITICAL'
        elif report['warnings'] > 0:
            report['overall_status'] = 'WARNING'
        elif report['failed_rules'] > 0:
            report['overall_status'] = 'INFO'
        else:
            report['overall_status'] = 'PASS'
        
        # 결과 분류
        for result in results:
            level_key = result.level.value
            report['results_by_level'][level_key].append({
                'rule_name': result.rule_name,
                'passed': result.passed,
                'message': result.message
            })
            
            report['detailed_results'].append({
                'rule_name': result.rule_name,
                'passed': result.passed,
                'level': result.level.value,
                'message': result.message,
                'details': result.details
            })
        
        return report
    
    def save_validation_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """검증 보고서 저장"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"webhook_validation_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return filename
        except Exception as e:
            print(f"❌ 보고서 저장 실패: {e}")
            return None

class WebhookFormatTestSuite:
    """웹훅 포맷 테스트 스위트"""
    
    def __init__(self, target_file: str):
        self.target_file = target_file
        self.validator = WebhookMessageFormatValidator()
        self.test_results = []
    
    def run_format_validation_tests(self) -> Dict[str, Any]:
        """포맷 검증 테스트 실행"""
        print("🔍 웹훅 메시지 포맷 자동 검증 시작...")
        print("=" * 60)
        
        if not os.path.exists(self.target_file):
            return {
                'error': f'대상 파일을 찾을 수 없습니다: {self.target_file}',
                'success': False
            }
        
        # 파일 내용 읽기
        try:
            with open(self.target_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'error': f'파일 읽기 실패: {e}',
                'success': False
            }
        
        # 전체 파일 검증
        print("📋 전체 파일 포맷 검증...")
        full_validation_results = self.validator.validate_content(content)
        full_report = self.validator.generate_validation_report(full_validation_results)
        
        # 개별 함수 검증
        print("\n🔍 개별 웹훅 함수 검증...")
        function_results = self._validate_individual_functions(content)
        
        # 종합 결과
        overall_results = {
            'target_file': self.target_file,
            'validation_timestamp': datetime.now().isoformat(),
            'full_file_validation': full_report,
            'function_validations': function_results,
            'summary': self._generate_summary(full_report, function_results)
        }
        
        # 결과 출력
        self._print_validation_summary(overall_results)
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"webhook_format_validation_{timestamp}.json"
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(overall_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 검증 결과 저장: {results_file}")
        except Exception as e:
            print(f"⚠️ 결과 저장 실패: {e}")
        
        return overall_results
    
    def _validate_individual_functions(self, content: str) -> Dict[str, Any]:
        """개별 함수 검증"""
        webhook_functions = [
            'send_status_notification',
            'send_notification',
            'send_status_report_v2',
            'send_startup_notification_v2',
            'send_process_error_v2',
            'send_recovery_success_v2',
            'send_critical_alert_v2'
        ]
        
        function_results = {}
        
        for func_name in webhook_functions:
            print(f"  🔍 {func_name} 검증 중...")
            
            # 함수 소스 추출
            func_source = self._extract_function_source(content, func_name)
            
            if func_source:
                # 함수별 검증 실행
                validation_results = self.validator.validate_content(func_source)
                report = self.validator.generate_validation_report(validation_results)
                
                function_results[func_name] = {
                    'found': True,
                    'validation_report': report,
                    'source_length': len(func_source)
                }
                
                status = "✅" if report['overall_status'] == 'PASS' else "⚠️" if report['overall_status'] in ['WARNING', 'INFO'] else "❌"
                print(f"    {status} 상태: {report['overall_status']}, 성공률: {report['success_rate']:.1f}%")
            else:
                function_results[func_name] = {
                    'found': False,
                    'validation_report': None,
                    'source_length': 0
                }
                print(f"    ❌ 함수를 찾을 수 없음")
        
        return function_results
    
    def _extract_function_source(self, content: str, function_name: str) -> Optional[str]:
        """함수 소스 코드 추출"""
        try:
            pattern = rf'def {function_name}\s*\('
            matches = list(re.finditer(pattern, content))
            
            if not matches:
                return None
            
            # 첫 번째 매치 사용
            match = matches[0]
            start_pos = match.start()
            lines = content[start_pos:].split('\n')
            
            if len(lines) < 2:
                return lines[0] if lines else None
            
            function_lines = [lines[0]]
            
            # 다음 줄에서 기본 들여쓰기 레벨 찾기
            base_indent = None
            for i in range(1, len(lines)):
                if lines[i].strip():  # 빈 줄이 아닌 첫 번째 줄
                    base_indent = len(lines[i]) - len(lines[i].lstrip())
                    break
            
            if base_indent is None:
                base_indent = 4  # 기본값
            
            for line in lines[1:]:
                if line.strip() == '':
                    function_lines.append(line)
                    continue
                
                current_indent = len(line) - len(line.lstrip())
                
                # 같은 레벨이거나 더 적은 들여쓰기면 함수 끝
                if current_indent <= base_indent and line.strip() and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                    # 다음 함수나 클래스 정의인지 확인
                    if re.match(r'\s*(def|class)\s+', line):
                        break
                
                function_lines.append(line)
            
            return '\n'.join(function_lines)
        
        except Exception:
            return None
    
    def _generate_summary(self, full_report: Dict[str, Any], function_results: Dict[str, Any]) -> Dict[str, Any]:
        """종합 요약 생성"""
        total_functions = len(function_results)
        found_functions = sum(1 for result in function_results.values() if result['found'])
        
        function_pass_count = 0
        for result in function_results.values():
            if result['found'] and result['validation_report']:
                if result['validation_report']['overall_status'] == 'PASS':
                    function_pass_count += 1
        
        return {
            'overall_status': full_report['overall_status'],
            'full_file_success_rate': full_report['success_rate'],
            'total_functions': total_functions,
            'found_functions': found_functions,
            'passed_functions': function_pass_count,
            'function_success_rate': (function_pass_count / found_functions * 100) if found_functions > 0 else 0,
            'critical_issues': full_report['critical_issues'],
            'warnings': full_report['warnings'],
            'recommendations': self._generate_recommendations(full_report, function_results)
        }
    
    def _generate_recommendations(self, full_report: Dict[str, Any], function_results: Dict[str, Any]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        if full_report['critical_issues'] > 0:
            recommendations.append("🚨 중요한 포맷 문제가 발견되었습니다. 즉시 수정이 필요합니다.")
        
        if full_report['warnings'] > 0:
            recommendations.append("⚠️ 경고 수준의 문제가 있습니다. 검토 후 수정을 권장합니다.")
        
        missing_functions = [name for name, result in function_results.items() if not result['found']]
        if missing_functions:
            recommendations.append(f"❌ 누락된 함수들을 복원해야 합니다: {', '.join(missing_functions)}")
        
        if full_report['success_rate'] < 90:
            recommendations.append("📈 전체 성공률이 90% 미만입니다. 추가 검토가 필요합니다.")
        
        return recommendations
    
    def _print_validation_summary(self, results: Dict[str, Any]):
        """검증 결과 요약 출력"""
        summary = results['summary']
        
        print("\n" + "=" * 60)
        print("📊 웹훅 메시지 포맷 검증 결과 요약")
        print("=" * 60)
        
        print(f"전체 파일 상태: {results['full_file_validation']['overall_status']}")
        print(f"전체 파일 성공률: {summary['full_file_success_rate']:.1f}%")
        print(f"함수 발견: {summary['found_functions']}/{summary['total_functions']}개")
        print(f"함수 검증 성공률: {summary['function_success_rate']:.1f}%")
        print(f"중요 문제: {summary['critical_issues']}개")
        print(f"경고: {summary['warnings']}개")
        
        if summary['recommendations']:
            print("\n💡 권장사항:")
            for rec in summary['recommendations']:
                print(f"  {rec}")
        
        if summary['overall_status'] == 'PASS' and summary['function_success_rate'] >= 90:
            print("\n🎉 웹훅 메시지 포맷 검증이 성공적으로 완료되었습니다!")
        elif summary['critical_issues'] == 0:
            print("\n⚠️ 일부 개선사항이 있지만 전반적으로 양호합니다.")
        else:
            print("\n❌ 중요한 문제가 발견되었습니다. 수정이 필요합니다.")

def run_webhook_format_validation(target_file: str = "core/monitoring/monitor_WatchHamster_v3.0.py"):
    """웹훅 포맷 검증 실행 메인 함수"""
    print("🚀 웹훅 메시지 포맷 자동 검증 시작")
    print("=" * 80)
    print(f"대상 파일: {target_file}")
    print(f"검증 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_suite = WebhookFormatTestSuite(target_file)
    results = test_suite.run_format_validation_tests()
    
    if 'error' in results:
        print(f"❌ 검증 실패: {results['error']}")
        return False
    
    # 성공 여부 판단
    summary = results.get('summary', {})
    success = (
        summary.get('critical_issues', 1) == 0 and
        summary.get('function_success_rate', 0) >= 70
    )
    
    return success

if __name__ == "__main__":
    success = run_webhook_format_validation()
    sys.exit(0 if success else 1)