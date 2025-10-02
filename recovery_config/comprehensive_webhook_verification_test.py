#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종합 웹훅 검증 테스트

캡처 이미지 기반 결과 검증과 실제 웹훅 전송을 통합 테스트합니다.

주요 기능:
- 5가지 BOT 타입별 메시지 생성 및 검증
- 실제 웹훅 전송 테스트 (테스트 모드)
- 캡처 이미지와 완전 일치 검증
- 전체 시스템 통합 테스트
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from capture_verification_system import CaptureVerificationSystem
    from webhook_sender import WebhookSender, MessagePriority
    from news_message_generator import NewsMessageGenerator
    from ai_analysis_engine import AIAnalysisEngine
    from integrated_news_parser import IntegratedNewsParser
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class ComprehensiveWebhookVerificationTest:
    """종합 웹훅 검증 테스트"""
    
    def __init__(self):
        """테스트 시스템 초기화"""
        print("🚀 종합 웹훅 검증 테스트 시스템 초기화")
        
        # 테스트 모드로 시스템 구성 요소 초기화
        self.verification_system = CaptureVerificationSystem(test_mode=True)
        self.webhook_sender = WebhookSender(test_mode=True)
        self.message_generator = NewsMessageGenerator(test_mode=True)
        self.ai_engine = AIAnalysisEngine()
        self.news_parser = IntegratedNewsParser()
        
        # 테스트 데이터 준비
        self.test_data = self._prepare_comprehensive_test_data()
        
        # 테스트 결과 저장
        self.test_results = {}
        
        print("✅ 종합 웹훅 검증 테스트 시스템 초기화 완료")
    
    def _prepare_comprehensive_test_data(self) -> Dict[str, Any]:
        """종합 테스트 데이터 준비"""
        return {
            'current_news_data': {
                'newyork-market-watch': {
                    'title': '[뉴욕마켓워치] 미국 증시 상승 마감',
                    'content': '다우존스 35,123.45 (+150.25), 나스닥 14,567.89 (+45.67)',
                    'date': '20250815',
                    'time': '063000',
                    'publish_time': '06:30'
                },
                'kospi-close': {
                    'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
                    'content': '코스피 지수 상승 마감, 외국인 순매수 지속',
                    'date': '20250815',
                    'time': '154000',
                    'publish_time': '15:40'
                },
                'exchange-rate': {
                    'title': '[환율] 달러/원 1,320.50 (+2.30)',
                    'content': '달러 강세 지속, 원화 약세 흐름',
                    'date': '20250815',
                    'time': '153000',
                    'publish_time': '15:30'
                }
            },
            'historical_data': {
                'newyork-market-watch': {
                    'title': '[뉴욕마켓워치] 전일 미국 증시 현황',
                    'time': '06:30'
                },
                'kospi-close': {
                    'title': '[코스피마감] 전일 코스피 현황',
                    'time': '15:40'
                },
                'exchange-rate': {
                    'title': '[환율] 전일 환율 현황',
                    'time': '15:30'
                }
            },
            'delay_scenario': {
                'news_type': 'kospi-close',
                'delay_minutes': 45,
                'delayed_data': {
                    'title': '[코스피마감] 코스피 2,450.25 (+15.75)',
                    'content': '코스피 지수 상승 마감',
                    'time': '162500',
                    'publish_time': '16:25'
                }
            },
            'empty_data': {},
            'test_scenarios': [
                {
                    'name': '영업일_비교_분석',
                    'type': 'comparison',
                    'description': '영업일 비교 분석 메시지 테스트'
                },
                {
                    'name': '지연_발행_알림',
                    'type': 'delay',
                    'description': '지연 발행 알림 메시지 테스트'
                },
                {
                    'name': '일일_통합_리포트',
                    'type': 'report',
                    'description': '일일 통합 분석 리포트 테스트'
                },
                {
                    'name': '정시_발행_알림',
                    'type': 'status',
                    'description': '정시 발행 알림 메시지 테스트'
                },
                {
                    'name': '데이터_갱신_없음',
                    'type': 'no_data',
                    'description': '데이터 갱신 없음 알림 테스트'
                }
            ]
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 테스트 실행"""
        print("\n🧪 종합 웹훅 검증 테스트 시작")
        print("=" * 60)
        
        overall_results = {
            'test_start_time': datetime.now(),
            'scenario_results': {},
            'verification_results': {},
            'webhook_results': {},
            'summary': {}
        }
        
        # 각 시나리오별 테스트 실행
        for scenario in self.test_data['test_scenarios']:
            scenario_name = scenario['name']
            scenario_type = scenario['type']
            
            print(f"\n📋 시나리오: {scenario['description']}")
            print("-" * 40)
            
            try:
                # 1. 메시지 생성 및 검증
                verification_result = self._run_verification_test(scenario_type)
                overall_results['verification_results'][scenario_name] = verification_result
                
                # 2. 웹훅 전송 테스트
                webhook_result = self._run_webhook_test(scenario_type)
                overall_results['webhook_results'][scenario_name] = webhook_result
                
                # 3. 시나리오 결과 종합
                scenario_success = (
                    verification_result.get('success', False) and 
                    webhook_result.get('success', False)
                )
                
                overall_results['scenario_results'][scenario_name] = {
                    'success': scenario_success,
                    'verification_score': verification_result.get('match_score', 0.0),
                    'webhook_success': webhook_result.get('success', False),
                    'description': scenario['description']
                }
                
                status_icon = "✅" if scenario_success else "❌"
                print(f"{status_icon} {scenario_name}: {'성공' if scenario_success else '실패'}")
                
            except Exception as e:
                print(f"❌ {scenario_name} 테스트 중 오류: {e}")
                overall_results['scenario_results'][scenario_name] = {
                    'success': False,
                    'error': str(e),
                    'description': scenario['description']
                }
        
        # 전체 결과 요약
        overall_results['summary'] = self._generate_test_summary(overall_results)
        overall_results['test_end_time'] = datetime.now()
        
        return overall_results
    
    def _run_verification_test(self, scenario_type: str) -> Dict[str, Any]:
        """검증 테스트 실행"""
        try:
            if scenario_type == 'comparison':
                result = self.verification_system.verify_business_day_comparison_message(
                    self.test_data['current_news_data'],
                    self.test_data['historical_data']
                )
            elif scenario_type == 'delay':
                delay_info = self.test_data['delay_scenario']
                result = self.verification_system.verify_delay_notification_message(
                    delay_info['news_type'],
                    delay_info['delayed_data'],
                    delay_info['delay_minutes']
                )
            elif scenario_type == 'report':
                result = self.verification_system.verify_daily_integrated_report_message(
                    self.test_data['current_news_data']
                )
            elif scenario_type == 'status':
                result = self.verification_system.verify_status_notification_message(
                    self.test_data['current_news_data']
                )
            elif scenario_type == 'no_data':
                result = self.verification_system.verify_no_data_notification_message(
                    self.test_data['empty_data']
                )
            else:
                return {'success': False, 'error': f'알 수 없는 시나리오 타입: {scenario_type}'}
            
            return {
                'success': result.success,
                'match_score': result.match_score,
                'verification_details': result.verification_details,
                'errors': result.errors,
                'warnings': result.warnings
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _run_webhook_test(self, scenario_type: str) -> Dict[str, Any]:
        """웹훅 전송 테스트 실행"""
        try:
            message_id = None
            
            if scenario_type == 'comparison':
                message_id = self.webhook_sender.send_business_day_comparison(
                    self.test_data['current_news_data'],
                    self.test_data['historical_data'],
                    MessagePriority.NORMAL
                )
            elif scenario_type == 'delay':
                delay_info = self.test_data['delay_scenario']
                message_id = self.webhook_sender.send_delay_notification(
                    delay_info['news_type'],
                    delay_info['delayed_data'],
                    delay_info['delay_minutes'],
                    MessagePriority.HIGH
                )
            elif scenario_type == 'report':
                message_id = self.webhook_sender.send_daily_integrated_report(
                    self.test_data['current_news_data'],
                    None,  # report_url
                    MessagePriority.NORMAL
                )
            elif scenario_type == 'status':
                message_id = self.webhook_sender.send_status_notification(
                    self.test_data['current_news_data'],
                    MessagePriority.NORMAL
                )
            elif scenario_type == 'no_data':
                message_id = self.webhook_sender.send_no_data_notification(
                    self.test_data['empty_data'],
                    MessagePriority.LOW
                )
            
            # 전송 결과 확인
            if message_id:
                # 잠시 대기 (전송 완료 대기)
                time.sleep(0.5)
                
                # 큐 상태 확인
                queue_status = self.webhook_sender.get_queue_status()
                send_stats = self.webhook_sender.get_send_statistics()
                
                return {
                    'success': True,
                    'message_id': message_id,
                    'queue_status': queue_status,
                    'send_statistics': send_stats
                }
            else:
                return {'success': False, 'error': '메시지 ID가 반환되지 않음'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 결과 요약 생성"""
        scenario_results = results['scenario_results']
        
        total_scenarios = len(scenario_results)
        successful_scenarios = sum(1 for result in scenario_results.values() if result.get('success', False))
        
        # 검증 점수 통계
        verification_scores = [
            result.get('verification_score', 0.0) 
            for result in scenario_results.values() 
            if 'verification_score' in result
        ]
        
        avg_verification_score = sum(verification_scores) / len(verification_scores) if verification_scores else 0.0
        
        # 웹훅 성공률
        webhook_successes = sum(1 for result in scenario_results.values() if result.get('webhook_success', False))
        webhook_success_rate = webhook_successes / total_scenarios if total_scenarios > 0 else 0.0
        
        return {
            'total_scenarios': total_scenarios,
            'successful_scenarios': successful_scenarios,
            'success_rate': successful_scenarios / total_scenarios if total_scenarios > 0 else 0.0,
            'average_verification_score': avg_verification_score,
            'webhook_success_rate': webhook_success_rate,
            'overall_success': successful_scenarios == total_scenarios
        }
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """종합 테스트 리포트 생성"""
        summary = results['summary']
        
        report_lines = [
            "🚀 종합 웹훅 검증 테스트 리포트",
            "=" * 60,
            f"테스트 시작: {results['test_start_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"테스트 종료: {results['test_end_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"소요 시간: {(results['test_end_time'] - results['test_start_time']).total_seconds():.1f}초",
            "",
            "📊 전체 결과 요약:",
            f"  • 총 시나리오: {summary['total_scenarios']}개",
            f"  • 성공 시나리오: {summary['successful_scenarios']}개",
            f"  • 전체 성공률: {summary['success_rate']:.1%}",
            f"  • 평균 검증 점수: {summary['average_verification_score']:.3f}",
            f"  • 웹훅 성공률: {summary['webhook_success_rate']:.1%}",
            ""
        ]
        
        # 시나리오별 상세 결과
        report_lines.append("📋 시나리오별 상세 결과:")
        for scenario_name, result in results['scenario_results'].items():
            status_icon = "✅" if result.get('success', False) else "❌"
            verification_score = result.get('verification_score', 0.0)
            webhook_success = result.get('webhook_success', False)
            
            report_lines.extend([
                f"{status_icon} {scenario_name}:",
                f"  • 설명: {result.get('description', '설명 없음')}",
                f"  • 검증 점수: {verification_score:.3f}",
                f"  • 웹훅 전송: {'성공' if webhook_success else '실패'}",
                ""
            ])
        
        # 검증 시스템 통계
        verification_stats = self.verification_system.get_verification_statistics()
        report_lines.extend([
            "📊 검증 시스템 통계:",
            f"  • 총 검증 수행: {verification_stats['total_verifications']}회",
            f"  • 검증 성공률: {verification_stats['success_rate']:.1%}",
            f"  • 평균 매치 점수: {verification_stats['average_match_score']:.3f}",
            ""
        ])
        
        # 웹훅 전송 통계
        webhook_stats = self.webhook_sender.get_send_statistics()
        report_lines.extend([
            "📡 웹훅 전송 통계:",
            f"  • 총 전송 시도: {webhook_stats['total_sent']}회",
            f"  • 전송 성공률: {webhook_stats.get('success_rate', 0.0):.1%}",
            f"  • 평균 응답 시간: {webhook_stats['average_response_time']:.3f}초",
            ""
        ])
        
        # 최종 결론
        if summary['overall_success']:
            report_lines.extend([
                "🎉 최종 결론: 모든 테스트가 성공적으로 완료되었습니다!",
                "   캡처 이미지 기반 결과 검증 시스템이 정상적으로 작동합니다."
            ])
        else:
            report_lines.extend([
                "⚠️ 최종 결론: 일부 테스트에서 개선이 필요합니다.",
                f"   성공률: {summary['success_rate']:.1%}",
                "   상세 결과를 확인하여 문제점을 개선해주세요."
            ])
        
        return "\n".join(report_lines)
    
    def save_test_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """테스트 결과를 JSON 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"comprehensive_webhook_verification_results_{timestamp}.json"
        
        # datetime 객체를 문자열로 변환
        serializable_results = self._make_serializable(results)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
            
            print(f"📁 테스트 결과가 저장되었습니다: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 테스트 결과 저장 실패: {e}")
            return None
    
    def _make_serializable(self, obj: Any) -> Any:
        """JSON 직렬화 가능한 형태로 변환"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj
    
    def cleanup(self):
        """테스트 시스템 정리"""
        print("\n🧹 테스트 시스템 정리 중...")
        
        # 웹훅 전송자 종료
        self.webhook_sender.shutdown(timeout=5)
        
        print("✅ 테스트 시스템 정리 완료")


def main():
    """메인 실행 함수"""
    print("🚀 종합 웹훅 검증 테스트 시작")
    
    # 테스트 시스템 생성
    test_system = ComprehensiveWebhookVerificationTest()
    
    try:
        # 종합 테스트 실행
        results = test_system.run_comprehensive_test()
        
        # 리포트 생성 및 출력
        report = test_system.generate_comprehensive_report(results)
        print("\n" + report)
        
        # 결과 저장
        saved_file = test_system.save_test_results(results)
        
        # 성공 여부 반환
        return results['summary']['overall_success']
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        return False
        
    finally:
        # 정리
        test_system.cleanup()


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        sys.exit(1)