#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 메시지 테스트 통합 실행기
모든 웹훅 메시지 테스트를 통합 실행하는 메인 스크립트

Requirements: 4.1, 4.2
- 실제 Dooray 전송 없이 메시지 포맷 검증하는 테스트 도구 개발
- 모든 웹훅 함수에 대한 단위 테스트 작성
- 메시지 내용과 포맷 정확성 자동 검증 로직 구현
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 테스트 모듈들 import
try:
    from webhook_message_test_system import run_comprehensive_webhook_tests
    from webhook_unit_tests import run_webhook_unit_tests
    from webhook_format_validator import run_webhook_format_validation
except ImportError as e:
    print(f"❌ 테스트 모듈 import 실패: {e}")
    sys.exit(1)

class WebhookTestIntegrator:
    """웹훅 테스트 통합 관리자"""
    
    def __init__(self, target_file: str = "core/monitoring/monitor_WatchHamster_v3.0.py"):
        self.target_file = target_file
        self.test_results = {}
        self.start_time = datetime.now()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 웹훅 테스트 실행"""
        print("🚀 웹훅 메시지 테스트 시스템 통합 실행")
        print("=" * 80)
        print(f"대상 파일: {self.target_file}")
        print(f"테스트 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 파일 존재 확인
        if not os.path.exists(self.target_file):
            error_msg = f"대상 파일을 찾을 수 없습니다: {self.target_file}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'timestamp': self.start_time.isoformat()
            }
        
        overall_results = {
            'target_file': self.target_file,
            'start_time': self.start_time.isoformat(),
            'test_phases': {},
            'summary': {},
            'success': True
        }
        
        # 1단계: 포괄적인 웹훅 테스트
        print("\n🧪 1단계: 포괄적인 웹훅 함수 테스트")
        print("-" * 60)
        
        try:
            comprehensive_success = run_comprehensive_webhook_tests(self.target_file)
            overall_results['test_phases']['comprehensive_tests'] = {
                'success': comprehensive_success,
                'description': '웹훅 함수 존재 여부 및 기본 포맷 검증'
            }
            
            if not comprehensive_success:
                overall_results['success'] = False
                print("⚠️ 1단계 테스트에서 문제가 발견되었습니다.")
            else:
                print("✅ 1단계 테스트 완료")
                
        except Exception as e:
            print(f"❌ 1단계 테스트 실행 중 오류: {e}")
            overall_results['test_phases']['comprehensive_tests'] = {
                'success': False,
                'error': str(e),
                'description': '웹훅 함수 존재 여부 및 기본 포맷 검증'
            }
            overall_results['success'] = False
        
        # 2단계: 단위 테스트
        print("\n🔬 2단계: 웹훅 함수 단위 테스트")
        print("-" * 60)
        
        try:
            unit_test_success = run_webhook_unit_tests()
            overall_results['test_phases']['unit_tests'] = {
                'success': unit_test_success,
                'description': '개별 웹훅 함수의 상세 동작 검증'
            }
            
            if not unit_test_success:
                overall_results['success'] = False
                print("⚠️ 2단계 테스트에서 문제가 발견되었습니다.")
            else:
                print("✅ 2단계 테스트 완료")
                
        except Exception as e:
            print(f"❌ 2단계 테스트 실행 중 오류: {e}")
            overall_results['test_phases']['unit_tests'] = {
                'success': False,
                'error': str(e),
                'description': '개별 웹훅 함수의 상세 동작 검증'
            }
            overall_results['success'] = False
        
        # 3단계: 포맷 자동 검증
        print("\n🔍 3단계: 메시지 포맷 자동 검증")
        print("-" * 60)
        
        try:
            format_validation_success = run_webhook_format_validation(self.target_file)
            overall_results['test_phases']['format_validation'] = {
                'success': format_validation_success,
                'description': '메시지 포맷 및 내용 정확성 자동 검증'
            }
            
            if not format_validation_success:
                overall_results['success'] = False
                print("⚠️ 3단계 테스트에서 문제가 발견되었습니다.")
            else:
                print("✅ 3단계 테스트 완료")
                
        except Exception as e:
            print(f"❌ 3단계 테스트 실행 중 오류: {e}")
            overall_results['test_phases']['format_validation'] = {
                'success': False,
                'error': str(e),
                'description': '메시지 포맷 및 내용 정확성 자동 검증'
            }
            overall_results['success'] = False
        
        # 테스트 완료 시간 기록
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        overall_results['end_time'] = end_time.isoformat()
        overall_results['duration_seconds'] = duration
        
        # 요약 생성
        overall_results['summary'] = self._generate_test_summary(overall_results)
        
        # 결과 출력
        self._print_final_summary(overall_results)
        
        # 결과 저장
        self._save_integrated_results(overall_results)
        
        return overall_results
    
    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 요약 생성"""
        phases = results['test_phases']
        
        total_phases = len(phases)
        passed_phases = sum(1 for phase in phases.values() if phase.get('success', False))
        failed_phases = total_phases - passed_phases
        
        success_rate = (passed_phases / total_phases * 100) if total_phases > 0 else 0
        
        # 각 단계별 상태
        phase_status = {}
        for phase_name, phase_data in phases.items():
            if phase_data.get('success', False):
                phase_status[phase_name] = "✅ 통과"
            elif 'error' in phase_data:
                phase_status[phase_name] = f"❌ 오류: {phase_data['error']}"
            else:
                phase_status[phase_name] = "❌ 실패"
        
        # 전체 상태 결정
        if results['success'] and passed_phases == total_phases:
            overall_status = "🎉 전체 성공"
        elif passed_phases >= total_phases * 0.7:  # 70% 이상
            overall_status = "⚠️ 부분 성공"
        else:
            overall_status = "❌ 실패"
        
        return {
            'overall_status': overall_status,
            'total_phases': total_phases,
            'passed_phases': passed_phases,
            'failed_phases': failed_phases,
            'success_rate': success_rate,
            'phase_status': phase_status,
            'duration_minutes': results['duration_seconds'] / 60,
            'recommendations': self._generate_recommendations(results)
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        phases = results['test_phases']
        
        # 성공률 계산
        total_phases = len(phases)
        passed_phases = sum(1 for phase in phases.values() if phase.get('success', False))
        success_rate = (passed_phases / total_phases * 100) if total_phases > 0 else 0
        
        # 실패한 단계별 권장사항
        if not phases.get('comprehensive_tests', {}).get('success', True):
            recommendations.append(
                "🔧 포괄적인 웹훅 테스트 실패: 웹훅 함수들이 누락되었거나 기본 포맷에 문제가 있습니다. "
                "webhook_message_restorer.py를 사용하여 함수들을 복원하세요."
            )
        
        if not phases.get('unit_tests', {}).get('success', True):
            recommendations.append(
                "🧪 단위 테스트 실패: 개별 웹훅 함수들의 동작에 문제가 있습니다. "
                "각 함수의 메시지 생성 로직을 점검하고 수정하세요."
            )
        
        if not phases.get('format_validation', {}).get('success', True):
            recommendations.append(
                "📝 포맷 검증 실패: 메시지 포맷이나 내용에 문제가 있습니다. "
                "줄바꿈 문자, 제품명, JSON 구조 등을 확인하고 수정하세요."
            )
        
        # 전체적인 권장사항
        if results['success']:
            recommendations.append(
                "✅ 모든 테스트가 성공했습니다! 이제 실제 Dooray 전송 테스트를 진행할 수 있습니다."
            )
        elif success_rate >= 70:
            recommendations.append(
                "⚠️ 대부분의 테스트가 성공했지만 일부 개선이 필요합니다. "
                "실패한 부분을 수정한 후 다시 테스트하세요."
            )
        else:
            recommendations.append(
                "❌ 다수의 테스트가 실패했습니다. 웹훅 복원 작업을 다시 검토하고 "
                "기본적인 함수 구조부터 확인하세요."
            )
        
        return recommendations
    
    def _print_final_summary(self, results: Dict[str, Any]):
        """최종 결과 요약 출력"""
        summary = results['summary']
        
        print("\n" + "=" * 80)
        print("🏁 웹훅 메시지 테스트 시스템 최종 결과")
        print("=" * 80)
        
        print(f"전체 상태: {summary['overall_status']}")
        print(f"테스트 단계: {summary['passed_phases']}/{summary['total_phases']}개 통과")
        print(f"성공률: {summary['success_rate']:.1f}%")
        print(f"소요 시간: {summary['duration_minutes']:.1f}분")
        
        print("\n📋 단계별 결과:")
        for phase_name, status in summary['phase_status'].items():
            phase_desc = results['test_phases'][phase_name].get('description', '')
            print(f"  {status} {phase_name}: {phase_desc}")
        
        if summary['recommendations']:
            print("\n💡 권장사항:")
            for i, rec in enumerate(summary['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "=" * 80)
        
        if results['success']:
            print("🎉 웹훅 메시지 테스트 시스템이 성공적으로 완료되었습니다!")
            print("✅ 모든 웹훅 함수가 올바르게 복원되었으며 메시지 포맷이 정상입니다.")
            print("🚀 이제 실제 Dooray 웹훅 전송 테스트를 진행할 수 있습니다.")
        else:
            print("⚠️ 일부 테스트에서 문제가 발견되었습니다.")
            print("📋 상세한 결과는 저장된 테스트 결과 파일을 확인하세요.")
            print("🔧 권장사항을 참고하여 문제를 해결한 후 다시 테스트하세요.")
    
    def _save_integrated_results(self, results: Dict[str, Any]):
        """통합 테스트 결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"webhook_integrated_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 통합 테스트 결과 저장: {filename}")
        except Exception as e:
            print(f"⚠️ 결과 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    # 명령행 인자 처리
    target_file = "core/monitoring/monitor_WatchHamster_v3.0.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # 통합 테스트 실행
    integrator = WebhookTestIntegrator(target_file)
    results = integrator.run_all_tests()
    
    # 종료 코드 결정
    if results.get('success', False):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()