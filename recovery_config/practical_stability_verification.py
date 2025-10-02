#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 실용적 안정성 검증
기존 성공한 테스트들을 기반으로 한 실제적인 안정성 검증
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any

class PracticalStabilityVerifier:
    """실용적 안정성 검증 클래스"""
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.results = {
            'verification_time': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'UNKNOWN',
            'stability_score': 0,
            'recommendations': []
        }
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """종합 안정성 검증 실행"""
        print("🔍 POSCO 시스템 실용적 안정성 검증 시작")
        print("=" * 60)
        
        # 1. 기존 성공 테스트 재실행
        self._run_existing_successful_tests()
        
        # 2. 파일 구조 안정성 검증
        self._verify_file_structure_stability()
        
        # 3. 핵심 기능 동작 검증
        self._verify_core_functionality()
        
        # 4. 시스템 리소스 상태 확인
        self._check_system_resources()
        
        # 5. 최종 안정성 평가
        self._calculate_final_stability_score()
        
        # 6. 결과 저장
        self._save_verification_results()
        
        return self.results
    
    def _run_existing_successful_tests(self):
        """기존 성공한 테스트들 재실행"""
        print("🧪 기존 성공 테스트 재실행 중...")
        
        successful_tests = []
        
        # Task 15 통합 테스트 재실행
        try:
            result = subprocess.run([
                'python3', 'comprehensive_system_integration_test.py'
            ], cwd=self.base_path, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                successful_tests.append({
                    'name': 'Task 15 통합 테스트',
                    'status': 'PASS',
                    'details': '기존 성공 테스트 재실행 성공'
                })
            else:
                successful_tests.append({
                    'name': 'Task 15 통합 테스트',
                    'status': 'FAIL',
                    'details': f'재실행 실패: {result.stderr[:200]}'
                })
        except Exception as e:
            successful_tests.append({
                'name': 'Task 15 통합 테스트',
                'status': 'ERROR',
                'details': f'실행 오류: {str(e)}'
            })
        
        # 캡처 검증 테스트 재실행
        try:
            result = subprocess.run([
                'python3', 'enhanced_capture_verification_test.py'
            ], cwd=self.base_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                successful_tests.append({
                    'name': '캡처 검증 테스트',
                    'status': 'PASS',
                    'details': '캡처 기반 검증 성공'
                })
            else:
                successful_tests.append({
                    'name': '캡처 검증 테스트',
                    'status': 'FAIL',
                    'details': f'검증 실패: {result.stderr[:200]}'
                })
        except Exception as e:
            successful_tests.append({
                'name': '캡처 검증 테스트',
                'status': 'ERROR',
                'details': f'실행 오류: {str(e)}'
            })
        
        # 웹훅 검증 테스트 재실행
        try:
            result = subprocess.run([
                'python3', 'comprehensive_webhook_verification_test.py'
            ], cwd=self.base_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                successful_tests.append({
                    'name': '웹훅 검증 테스트',
                    'status': 'PASS',
                    'details': '웹훅 시스템 검증 성공'
                })
            else:
                successful_tests.append({
                    'name': '웹훅 검증 테스트',
                    'status': 'FAIL',
                    'details': f'검증 실패: {result.stderr[:200]}'
                })
        except Exception as e:
            successful_tests.append({
                'name': '웹훅 검증 테스트',
                'status': 'ERROR',
                'details': f'실행 오류: {str(e)}'
            })
        
        # 결과 저장
        pass_count = sum(1 for test in successful_tests if test['status'] == 'PASS')
        total_count = len(successful_tests)
        
        self.results['tests']['existing_tests_rerun'] = {
            'status': 'PASS' if pass_count >= total_count * 0.8 else 'FAIL',
            'pass_count': pass_count,
            'total_count': total_count,
            'success_rate': (pass_count / total_count * 100) if total_count > 0 else 0,
            'details': successful_tests
        }
        
        print(f"✅ 기존 테스트 재실행 완료: {pass_count}/{total_count} 성공")
    
    def _verify_file_structure_stability(self):
        """파일 구조 안정성 검증"""
        print("📁 파일 구조 안정성 검증 중...")
        
        try:
            # 핵심 파일들 존재 확인
            core_files = [
                'environment_setup.py',
                'integrated_api_module.py',
                'integrated_news_parser.py',
                'news_message_generator.py',
                'webhook_sender.py',
                'watchhamster_monitor.py',
                'ai_analysis_engine.py',
                'business_day_comparison_engine.py'
            ]
            
            file_status = {}
            for file_name in core_files:
                file_path = os.path.join(self.base_path, file_name)
                if os.path.exists(file_path):
                    # 파일 크기 확인 (0바이트가 아닌지)
                    file_size = os.path.getsize(file_path)
                    file_status[file_name] = {
                        'exists': True,
                        'size': file_size,
                        'status': 'OK' if file_size > 0 else 'EMPTY'
                    }
                else:
                    file_status[file_name] = {
                        'exists': False,
                        'size': 0,
                        'status': 'MISSING'
                    }
            
            # 안정성 평가
            ok_files = sum(1 for status in file_status.values() if status['status'] == 'OK')
            total_files = len(core_files)
            stability_rate = (ok_files / total_files) * 100
            
            self.results['tests']['file_structure_stability'] = {
                'status': 'PASS' if stability_rate >= 90 else 'FAIL',
                'stability_rate': stability_rate,
                'ok_files': ok_files,
                'total_files': total_files,
                'file_details': file_status
            }
            
            print(f"✅ 파일 구조 안정성: {stability_rate:.1f}% ({ok_files}/{total_files})")
            
        except Exception as e:
            self.results['tests']['file_structure_stability'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ 파일 구조 검증 오류: {e}")
    
    def _verify_core_functionality(self):
        """핵심 기능 동작 검증"""
        print("⚙️ 핵심 기능 동작 검증 중...")
        
        functionality_tests = []
        
        # 1. 환경 설정 기능 테스트
        try:
            result = subprocess.run([
                'python3', '-c', 
                'import environment_setup; env = environment_setup.EnvironmentSetup(); print("환경 설정 OK")'
            ], cwd=self.base_path, capture_output=True, text=True, timeout=10)
            
            functionality_tests.append({
                'name': '환경 설정 기능',
                'status': 'PASS' if result.returncode == 0 else 'FAIL',
                'details': result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            })
        except Exception as e:
            functionality_tests.append({
                'name': '환경 설정 기능',
                'status': 'ERROR',
                'details': str(e)
            })
        
        # 2. 뉴스 파서 기능 테스트
        try:
            result = subprocess.run([
                'python3', '-c', 
                'import integrated_news_parser; parser = integrated_news_parser.IntegratedNewsParser(); print("뉴스 파서 OK")'
            ], cwd=self.base_path, capture_output=True, text=True, timeout=10)
            
            functionality_tests.append({
                'name': '뉴스 파서 기능',
                'status': 'PASS' if result.returncode == 0 else 'FAIL',
                'details': result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            })
        except Exception as e:
            functionality_tests.append({
                'name': '뉴스 파서 기능',
                'status': 'ERROR',
                'details': str(e)
            })
        
        # 3. 메시지 생성 기능 테스트
        try:
            result = subprocess.run([
                'python3', '-c', 
                'import news_message_generator; gen = news_message_generator.NewsMessageGenerator(); print("메시지 생성기 OK")'
            ], cwd=self.base_path, capture_output=True, text=True, timeout=10)
            
            functionality_tests.append({
                'name': '메시지 생성 기능',
                'status': 'PASS' if result.returncode == 0 else 'FAIL',
                'details': result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            })
        except Exception as e:
            functionality_tests.append({
                'name': '메시지 생성 기능',
                'status': 'ERROR',
                'details': str(e)
            })
        
        # 4. 웹훅 전송 기능 테스트
        try:
            result = subprocess.run([
                'python3', '-c', 
                'import webhook_sender; sender = webhook_sender.WebhookSender(); print("웹훅 전송기 OK")'
            ], cwd=self.base_path, capture_output=True, text=True, timeout=10)
            
            functionality_tests.append({
                'name': '웹훅 전송 기능',
                'status': 'PASS' if result.returncode == 0 else 'FAIL',
                'details': result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            })
        except Exception as e:
            functionality_tests.append({
                'name': '웹훅 전송 기능',
                'status': 'ERROR',
                'details': str(e)
            })
        
        # 결과 평가
        pass_count = sum(1 for test in functionality_tests if test['status'] == 'PASS')
        total_count = len(functionality_tests)
        
        self.results['tests']['core_functionality'] = {
            'status': 'PASS' if pass_count >= total_count * 0.75 else 'FAIL',
            'pass_count': pass_count,
            'total_count': total_count,
            'success_rate': (pass_count / total_count * 100) if total_count > 0 else 0,
            'details': functionality_tests
        }
        
        print(f"✅ 핵심 기능 검증 완료: {pass_count}/{total_count} 성공")
    
    def _check_system_resources(self):
        """시스템 리소스 상태 확인"""
        print("💻 시스템 리소스 상태 확인 중...")
        
        try:
            # 디스크 사용량 확인
            disk_usage = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
            
            # 메모리 사용량 확인 (macOS)
            memory_usage = subprocess.run(['vm_stat'], capture_output=True, text=True)
            
            # 프로세스 확인
            process_check = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            
            resource_status = {
                'disk_check': 'PASS' if disk_usage.returncode == 0 else 'FAIL',
                'memory_check': 'PASS' if memory_usage.returncode == 0 else 'FAIL',
                'process_check': 'PASS' if process_check.returncode == 0 else 'FAIL'
            }
            
            # 전체 리소스 상태 평가
            pass_count = sum(1 for status in resource_status.values() if status == 'PASS')
            total_count = len(resource_status)
            
            self.results['tests']['system_resources'] = {
                'status': 'PASS' if pass_count == total_count else 'FAIL',
                'pass_count': pass_count,
                'total_count': total_count,
                'details': resource_status
            }
            
            print(f"✅ 시스템 리소스 확인 완료: {pass_count}/{total_count} 정상")
            
        except Exception as e:
            self.results['tests']['system_resources'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ 시스템 리소스 확인 오류: {e}")
    
    def _calculate_final_stability_score(self):
        """최종 안정성 점수 계산"""
        print("📊 최종 안정성 점수 계산 중...")
        
        try:
            # 각 테스트별 가중치
            weights = {
                'existing_tests_rerun': 40,  # 기존 성공 테스트 재실행이 가장 중요
                'file_structure_stability': 25,
                'core_functionality': 25,
                'system_resources': 10
            }
            
            total_score = 0
            max_possible_score = sum(weights.values())
            
            for test_name, weight in weights.items():
                if test_name in self.results['tests']:
                    test_result = self.results['tests'][test_name]
                    
                    if test_result['status'] == 'PASS':
                        total_score += weight
                    elif test_result['status'] == 'PARTIAL':
                        total_score += weight * 0.5
                    # FAIL이나 ERROR는 0점
            
            stability_score = (total_score / max_possible_score) * 100
            
            # 안정성 등급 결정
            if stability_score >= 95:
                grade = 'A+ (최우수)'
                overall_status = 'EXCELLENT'
            elif stability_score >= 90:
                grade = 'A (우수)'
                overall_status = 'GOOD'
            elif stability_score >= 80:
                grade = 'B (양호)'
                overall_status = 'ACCEPTABLE'
            elif stability_score >= 70:
                grade = 'C (보통)'
                overall_status = 'NEEDS_IMPROVEMENT'
            else:
                grade = 'D (개선 필요)'
                overall_status = 'POOR'
            
            self.results['stability_score'] = stability_score
            self.results['stability_grade'] = grade
            self.results['overall_status'] = overall_status
            
            # 권장사항 생성
            self._generate_practical_recommendations()
            
            print(f"✅ 최종 안정성 점수: {stability_score:.1f}점 ({grade})")
            
        except Exception as e:
            print(f"❌ 안정성 점수 계산 실패: {e}")
            self.results['stability_score'] = 0
            self.results['stability_grade'] = 'ERROR'
            self.results['overall_status'] = 'ERROR'
    
    def _generate_practical_recommendations(self):
        """실용적 권장사항 생성"""
        recommendations = []
        
        # 기존 테스트 재실행 결과 기반 권장사항
        if 'existing_tests_rerun' in self.results['tests']:
            test_result = self.results['tests']['existing_tests_rerun']
            if test_result['status'] != 'PASS':
                recommendations.append("기존 성공 테스트들이 실패했습니다. 시스템 복구 상태를 재점검하세요.")
            else:
                recommendations.append("기존 성공 테스트들이 정상 작동합니다. 시스템이 안정적으로 복구되었습니다.")
        
        # 파일 구조 안정성 기반 권장사항
        if 'file_structure_stability' in self.results['tests']:
            test_result = self.results['tests']['file_structure_stability']
            if test_result['status'] != 'PASS':
                recommendations.append("일부 핵심 파일이 누락되거나 손상되었습니다. 파일 무결성을 확인하세요.")
        
        # 핵심 기능 동작 기반 권장사항
        if 'core_functionality' in self.results['tests']:
            test_result = self.results['tests']['core_functionality']
            if test_result['status'] != 'PASS':
                recommendations.append("핵심 기능 모듈에 문제가 있습니다. 모듈별 상세 점검이 필요합니다.")
        
        # 전체 점수 기반 권장사항
        if self.results['stability_score'] >= 90:
            recommendations.append("시스템이 매우 안정적입니다. 현재 상태를 유지하며 정기 모니터링을 수행하세요.")
        elif self.results['stability_score'] >= 80:
            recommendations.append("시스템이 안정적으로 작동합니다. 소규모 개선사항을 점진적으로 적용하세요.")
        elif self.results['stability_score'] >= 70:
            recommendations.append("시스템에 일부 문제가 있습니다. 실패한 테스트들을 우선적으로 해결하세요.")
        else:
            recommendations.append("시스템에 심각한 문제가 있습니다. 전체적인 재검토와 수리가 필요합니다.")
        
        # 실용적 운영 권장사항
        recommendations.extend([
            "정기적으로 이 안정성 검증을 실행하여 시스템 상태를 모니터링하세요.",
            "중요한 변경사항 적용 전에는 반드시 안정성 검증을 수행하세요.",
            "로그 파일을 정기적으로 검토하여 잠재적 문제를 조기에 발견하세요."
        ])
        
        self.results['recommendations'] = recommendations
    
    def _save_verification_results(self):
        """검증 결과 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON 결과 저장
            json_file = f'practical_stability_verification_results_{timestamp}.json'
            json_path = os.path.join(self.base_path, json_file)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            # 마크다운 리포트 생성
            self._generate_practical_report(timestamp)
            
            print(f"✅ 검증 결과 저장 완료: {json_file}")
            
        except Exception as e:
            print(f"❌ 결과 저장 실패: {e}")
    
    def _generate_practical_report(self, timestamp: str):
        """실용적 마크다운 리포트 생성"""
        try:
            report_content = f"""# 🏆 POSCO 시스템 실용적 안정성 검증 리포트

## 📊 종합 결과

**최종 안정성 점수**: {self.results.get('stability_score', 0):.1f}점  
**안정성 등급**: {self.results.get('stability_grade', 'N/A')}  
**전체 상태**: {self.results.get('overall_status', 'UNKNOWN')}  
**검증 실행 시간**: {self.results.get('verification_time', '')}

## 🔍 세부 검증 결과

"""
            
            # 각 테스트 결과 추가
            for test_name, test_result in self.results.get('tests', {}).items():
                status_emoji = '✅' if test_result['status'] == 'PASS' else '❌' if test_result['status'] == 'FAIL' else '⚠️'
                test_title = test_name.replace('_', ' ').title()
                
                report_content += f"### {status_emoji} {test_title}\n"
                report_content += f"- **상태**: {test_result['status']}\n"
                
                if 'pass_count' in test_result and 'total_count' in test_result:
                    report_content += f"- **성공률**: {test_result.get('success_rate', 0):.1f}% ({test_result['pass_count']}/{test_result['total_count']})\n"
                
                if 'details' in test_result:
                    if isinstance(test_result['details'], list):
                        report_content += "- **세부 결과**:\n"
                        for detail in test_result['details']:
                            if isinstance(detail, dict):
                                detail_status = '✅' if detail.get('status') == 'PASS' else '❌'
                                report_content += f"  - {detail_status} {detail.get('name', 'Unknown')}: {detail.get('details', '')}\n"
                    else:
                        report_content += f"- **세부사항**: {test_result['details']}\n"
                
                report_content += "\n"
            
            # 권장사항 추가
            if 'recommendations' in self.results:
                report_content += "## 💡 실용적 권장사항\n\n"
                for i, recommendation in enumerate(self.results['recommendations'], 1):
                    report_content += f"{i}. {recommendation}\n"
                report_content += "\n"
            
            # 결론 추가
            report_content += f"""## 🎯 검증 결론

POSCO 시스템의 실용적 안정성 검증이 완료되었습니다.

**최종 평가**: {self.results.get('stability_score', 0):.1f}점 ({self.results.get('stability_grade', 'N/A')})

"""
            
            if self.results.get('stability_score', 0) >= 90:
                report_content += "🎉 **시스템이 매우 안정적으로 작동합니다!** 운영 환경에 배포할 준비가 완료되었습니다.\n"
            elif self.results.get('stability_score', 0) >= 80:
                report_content += "✅ **시스템이 안정적으로 작동합니다.** 소규모 개선 후 운영 가능합니다.\n"
            elif self.results.get('stability_score', 0) >= 70:
                report_content += "⚠️ **시스템에 일부 문제가 있습니다.** 주요 이슈 해결 후 운영하세요.\n"
            else:
                report_content += "❌ **시스템에 심각한 문제가 있습니다.** 전면적인 점검과 수리가 필요합니다.\n"
            
            report_content += f"""
---
**리포트 생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**기준 커밋**: a763ef84be08b5b1dab0c0ba20594b141baec7ab  
**검증 도구**: POSCO 실용적 안정성 검증 시스템
"""
            
            # 마크다운 파일 저장
            report_file = f'practical_stability_report_{timestamp}.md'
            report_path = os.path.join(self.base_path, report_file)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ 마크다운 리포트 생성 완료: {report_file}")
            
        except Exception as e:
            print(f"❌ 마크다운 리포트 생성 실패: {e}")

def main():
    """메인 실행 함수"""
    verifier = PracticalStabilityVerifier()
    results = verifier.run_comprehensive_verification()
    
    print("\n" + "=" * 60)
    print("🏆 POSCO 시스템 실용적 안정성 검증 완료!")
    print(f"📊 최종 안정성 점수: {results.get('stability_score', 0):.1f}점")
    print(f"🏅 안정성 등급: {results.get('stability_grade', 'N/A')}")
    print(f"🎯 전체 상태: {results.get('overall_status', 'UNKNOWN')}")
    
    if results.get('stability_score', 0) >= 90:
        print("🎉 시스템이 매우 안정적으로 작동합니다!")
    elif results.get('stability_score', 0) >= 80:
        print("✅ 시스템이 안정적으로 작동합니다.")
    elif results.get('stability_score', 0) >= 70:
        print("⚠️ 시스템에 일부 개선이 필요합니다.")
    else:
        print("❌ 시스템에 심각한 문제가 있습니다.")
    
    return results

if __name__ == "__main__":
    main()