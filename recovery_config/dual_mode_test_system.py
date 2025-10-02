#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이원화된 테스트 시스템

1. 로직 검증 테스트: 2025-08-06 19:00 기준 (모든 데이터 완전 상태)
2. 현행 테스트: 현재 시점 기준 (실시간 상황)
"""

import os
import sys
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from news_message_generator import NewsMessageGenerator
    from capture_verification_system import CaptureVerificationSystem
    from webhook_sender import WebhookSender
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


class DualModeTestSystem:
    """이원화된 테스트 시스템"""
    
    def __init__(self):
        """테스트 시스템 초기화"""
        # 로직 검증용 기준 시간: 2025-08-06 19:00
        self.logic_test_datetime = datetime(2025, 8, 6, 19, 0, 0)
        
        # 현행 테스트용 기준 시간: 현재 시점
        self.current_test_datetime = datetime.now()
        
        print("🚀 이원화된 테스트 시스템 초기화")
        print(f"📅 로직 검증 기준: {self.logic_test_datetime.strftime('%Y-%m-%d %H:%M')}")
        print(f"📅 현행 테스트 기준: {self.current_test_datetime.strftime('%Y-%m-%d %H:%M')}")
    
    def get_complete_test_data(self) -> dict:
        """완전한 테스트 데이터 (2025-08-06 19:00 기준)"""
        return {
            'current_data': {
                'newyork-market-watch': {
                    'title': '[뉴욕마켓워치] 미국 증시 강세 마감, 다우 35,234.56 신고점',
                    'content': '다우존스 35,234.56 (+234.56, +0.67%), 나스닥 14,678.90 (+123.45, +0.85%), S&P500 4,567.89 (+45.67, +1.01%)',
                    'date': '20250806',
                    'time': '063000',
                    'publish_time': '06:30'
                },
                'kospi-close': {
                    'title': '[코스피마감] 코스피 2,465.75 강세 마감, 외국인 대량 순매수',
                    'content': '코스피 지수 2,465.75 (+25.50, +1.05%), 거래량 8,234억원, 외국인 순매수 1,234억원',
                    'date': '20250806',
                    'time': '154000',
                    'publish_time': '15:40'
                },
                'exchange-rate': {
                    'title': '[환율] 달러/원 1,318.20 원화 강세, 수출 호조 영향',
                    'content': '달러/원 1,318.20 (-4.30, -0.33%), 유로/원 1,445.67 (-2.15), 엔/원 8.95 (+0.12)',
                    'date': '20250806',
                    'time': '153000',
                    'publish_time': '15:30'
                }
            },
            'historical_data': {
                'newyork-market-watch': {
                    'title': '[뉴욕마켓워치] 미국 증시 혼조세, 기술주 약세 지속',
                    'time': '063000'
                },
                'kospi-close': {
                    'title': '[코스피마감] 코스피 2,440.25 하락 마감, 외국인 순매도',
                    'time': '154500'  # 5분 지연
                },
                'exchange-rate': {
                    'title': '[환율] 달러/원 1,322.50 달러 강세, 무역수지 악화',
                    'time': '153000'
                }
            },
            'delay_scenario': {
                'news_type': 'kospi-close',
                'delay_minutes': 45,
                'delayed_data': {
                    'title': '[코스피마감] 코스피 2,465.75 강세 마감, 외국인 대량 순매수',
                    'time': '162500'  # 16:25 (45분 지연)
                }
            }
        }
    
    def get_current_test_data(self) -> dict:
        """현행 테스트 데이터 (현재 시점 기준)"""
        current_time = datetime.now()
        return {
            'current_data': {
                'newyork-market-watch': {
                    'title': '[뉴욕마켓워치] 실시간 테스트 데이터',
                    'content': '현재 시점 기준 테스트',
                    'date': current_time.strftime('%Y%m%d'),
                    'time': '063000',
                    'publish_time': '06:30'
                },
                'kospi-close': {
                    'title': '[코스피마감] 실시간 테스트 데이터',
                    'content': '현재 시점 기준 테스트',
                    'date': current_time.strftime('%Y%m%d'),
                    'time': '154000',
                    'publish_time': '15:40'
                },
                'exchange-rate': {
                    'title': '[환율] 실시간 테스트 데이터',
                    'content': '현재 시점 기준 테스트',
                    'date': current_time.strftime('%Y%m%d'),
                    'time': '153000',
                    'publish_time': '15:30'
                }
            },
            'historical_data': {},
            'delay_scenario': {
                'news_type': 'kospi-close',
                'delay_minutes': 30,
                'delayed_data': {
                    'title': '[코스피마감] 실시간 테스트 데이터',
                    'time': '161000'
                }
            }
        }
    
    def run_logic_verification_test(self) -> dict:
        """로직 검증 테스트 실행 (2025-08-06 19:00 기준)"""
        print("\n" + "="*60)
        print("📊 1. 로직 검증 테스트 (2025-08-06 19:00 기준)")
        print("   목적: 모든 데이터가 완전한 상태에서 로직 정확성 검증")
        print("="*60)
        
        # 로직 검증용 시스템 초기화
        generator = NewsMessageGenerator(test_mode=True, test_datetime=self.logic_test_datetime)
        verification_system = CaptureVerificationSystem(test_mode=True)
        webhook_sender = WebhookSender(test_mode=True)
        
        # 완전한 테스트 데이터 사용
        test_data = self.get_complete_test_data()
        
        results = {
            'test_type': 'logic_verification',
            'test_datetime': self.logic_test_datetime,
            'results': {}
        }
        
        # 1. 영업일 비교 분석 (완전한 데이터로 풀 텍스트 확인)
        print("\n📋 1-1. 영업일 비교 분석 메시지 (풀 텍스트):")
        print("-" * 50)
        
        comparison_result = generator.generate_business_day_comparison_message(
            test_data['current_data'], 
            test_data['historical_data']
        )
        
        if comparison_result.success:
            print("✅ 메시지 생성 성공")
            print("\n📄 완전한 메시지 내용:")
            print(comparison_result.message)
            
            # 검증 수행
            verification_result = verification_system.verify_business_day_comparison_message(
                test_data['current_data'],
                test_data['historical_data']
            )
            
            results['results']['comparison'] = {
                'generation_success': True,
                'message': comparison_result.message,
                'verification_score': verification_result.match_score,
                'verification_success': verification_result.success
            }
            
            print(f"\n🎯 검증 결과: {verification_result.match_score:.3f} ({'성공' if verification_result.success else '개선 필요'})")
        else:
            print("❌ 메시지 생성 실패")
            results['results']['comparison'] = {'generation_success': False, 'errors': comparison_result.errors}
        
        # 2. 지연 발행 알림 (완전한 데이터로 풀 텍스트 확인)
        print("\n📋 1-2. 지연 발행 알림 메시지 (풀 텍스트):")
        print("-" * 50)
        
        delay_result = generator.generate_delay_notification_message(
            test_data['delay_scenario']['news_type'],
            test_data['delay_scenario']['delayed_data'],
            test_data['delay_scenario']['delay_minutes']
        )
        
        if delay_result.success:
            print("✅ 메시지 생성 성공")
            print("\n📄 완전한 메시지 내용:")
            print(delay_result.message)
            
            # 검증 수행
            verification_result = verification_system.verify_delay_notification_message(
                test_data['delay_scenario']['news_type'],
                test_data['delay_scenario']['delayed_data'],
                test_data['delay_scenario']['delay_minutes']
            )
            
            results['results']['delay'] = {
                'generation_success': True,
                'message': delay_result.message,
                'verification_score': verification_result.match_score,
                'verification_success': verification_result.success
            }
            
            print(f"\n🎯 검증 결과: {verification_result.match_score:.3f} ({'성공' if verification_result.success else '개선 필요'})")
        else:
            print("❌ 메시지 생성 실패")
            results['results']['delay'] = {'generation_success': False, 'errors': delay_result.errors}
        
        # 3. 일일 통합 리포트 (완전한 데이터로 풀 텍스트 확인)
        print("\n📋 1-3. 일일 통합 분석 리포트 (풀 텍스트):")
        print("-" * 50)
        
        report_result = generator.generate_daily_integrated_report_message(
            test_data['current_data'],
            "https://posco-report.example.com/20250806"
        )
        
        if report_result.success:
            print("✅ 메시지 생성 성공")
            print("\n📄 완전한 메시지 내용:")
            print(report_result.message)
            
            # 검증 수행
            verification_result = verification_system.verify_daily_integrated_report_message(
                test_data['current_data']
            )
            
            results['results']['report'] = {
                'generation_success': True,
                'message': report_result.message,
                'verification_score': verification_result.match_score,
                'verification_success': verification_result.success
            }
            
            print(f"\n🎯 검증 결과: {verification_result.match_score:.3f} ({'성공' if verification_result.success else '개선 필요'})")
        else:
            print("❌ 메시지 생성 실패")
            results['results']['report'] = {'generation_success': False, 'errors': report_result.errors}
        
        return results
    
    def run_current_test(self) -> dict:
        """현행 테스트 실행 (현재 시점 기준)"""
        print("\n" + "="*60)
        print("📊 2. 현행 테스트 (현재 시점 기준)")
        print("   목적: 실시간 상황에서 시스템 동작 확인")
        print("="*60)
        
        # 현행 테스트용 시스템 초기화
        generator = NewsMessageGenerator(test_mode=True, test_datetime=self.current_test_datetime)
        verification_system = CaptureVerificationSystem(test_mode=True)
        webhook_sender = WebhookSender(test_mode=True)
        
        # 현행 테스트 데이터 사용
        test_data = self.get_current_test_data()
        
        results = {
            'test_type': 'current_test',
            'test_datetime': self.current_test_datetime,
            'results': {}
        }
        
        # 1. 정시 발행 알림 (현재 시점 기준)
        print("\n📋 2-1. 정시 발행 알림 메시지:")
        print("-" * 50)
        
        status_result = generator.generate_status_notification_message(test_data['current_data'])
        
        if status_result.success:
            print("✅ 메시지 생성 성공")
            print("\n📄 메시지 내용:")
            print(status_result.message)
            
            # 검증 수행
            verification_result = verification_system.verify_status_notification_message(
                test_data['current_data']
            )
            
            results['results']['status'] = {
                'generation_success': True,
                'message': status_result.message,
                'verification_score': verification_result.match_score,
                'verification_success': verification_result.success
            }
            
            print(f"\n🎯 검증 결과: {verification_result.match_score:.3f} ({'성공' if verification_result.success else '개선 필요'})")
        else:
            print("❌ 메시지 생성 실패")
            results['results']['status'] = {'generation_success': False, 'errors': status_result.errors}
        
        # 2. 데이터 갱신 없음 알림 (현재 시점 기준)
        print("\n📋 2-2. 데이터 갱신 없음 알림 메시지:")
        print("-" * 50)
        
        no_data_result = generator.generate_no_data_notification_message({})
        
        if no_data_result.success:
            print("✅ 메시지 생성 성공")
            print("\n📄 메시지 내용:")
            print(no_data_result.message)
            
            # 검증 수행
            verification_result = verification_system.verify_no_data_notification_message({})
            
            results['results']['no_data'] = {
                'generation_success': True,
                'message': no_data_result.message,
                'verification_score': verification_result.match_score,
                'verification_success': verification_result.success
            }
            
            print(f"\n🎯 검증 결과: {verification_result.match_score:.3f} ({'성공' if verification_result.success else '개선 필요'})")
        else:
            print("❌ 메시지 생성 실패")
            results['results']['no_data'] = {'generation_success': False, 'errors': no_data_result.errors}
        
        return results
    
    def generate_comparison_report(self, logic_results: dict, current_results: dict) -> str:
        """두 테스트 결과 비교 리포트 생성"""
        report_lines = [
            "📊 이원화된 테스트 결과 비교 리포트",
            "=" * 60,
            f"로직 검증 기준: {logic_results['test_datetime'].strftime('%Y-%m-%d %H:%M')}",
            f"현행 테스트 기준: {current_results['test_datetime'].strftime('%Y-%m-%d %H:%M')}",
            ""
        ]
        
        # 로직 검증 테스트 결과
        report_lines.extend([
            "📋 1. 로직 검증 테스트 결과:",
            "-" * 40
        ])
        
        logic_success_count = 0
        logic_total_count = 0
        
        for test_name, result in logic_results['results'].items():
            if result.get('generation_success', False):
                logic_total_count += 1
                verification_success = result.get('verification_success', False)
                if verification_success:
                    logic_success_count += 1
                
                status_icon = "✅" if verification_success else "⚠️"
                score = result.get('verification_score', 0.0)
                report_lines.append(f"  {status_icon} {test_name.upper()}: {score:.3f}")
        
        logic_success_rate = logic_success_count / logic_total_count if logic_total_count > 0 else 0
        report_lines.extend([
            f"  📈 성공률: {logic_success_count}/{logic_total_count} ({logic_success_rate:.1%})",
            ""
        ])
        
        # 현행 테스트 결과
        report_lines.extend([
            "📋 2. 현행 테스트 결과:",
            "-" * 40
        ])
        
        current_success_count = 0
        current_total_count = 0
        
        for test_name, result in current_results['results'].items():
            if result.get('generation_success', False):
                current_total_count += 1
                verification_success = result.get('verification_success', False)
                if verification_success:
                    current_success_count += 1
                
                status_icon = "✅" if verification_success else "⚠️"
                score = result.get('verification_score', 0.0)
                report_lines.append(f"  {status_icon} {test_name.upper()}: {score:.3f}")
        
        current_success_rate = current_success_count / current_total_count if current_total_count > 0 else 0
        report_lines.extend([
            f"  📈 성공률: {current_success_count}/{current_total_count} ({current_success_rate:.1%})",
            ""
        ])
        
        # 종합 결론
        report_lines.extend([
            "🎯 종합 결론:",
            "-" * 40,
            f"• 로직 검증 (완전 데이터): {logic_success_rate:.1%} 성공률",
            f"• 현행 테스트 (실시간): {current_success_rate:.1%} 성공률",
            ""
        ])
        
        if logic_success_rate >= 0.8 and current_success_rate >= 0.6:
            report_lines.append("🎉 두 테스트 모두 양호한 결과를 보입니다!")
        elif logic_success_rate >= 0.8:
            report_lines.append("✅ 로직은 정상, 현행 테스트 개선 필요")
        elif current_success_rate >= 0.6:
            report_lines.append("⚠️ 로직 검증 개선 필요, 현행 테스트는 양호")
        else:
            report_lines.append("🔧 두 테스트 모두 개선이 필요합니다")
        
        return "\n".join(report_lines)
    
    def run_dual_mode_test(self) -> dict:
        """이원화된 테스트 전체 실행"""
        print("🚀 이원화된 테스트 시스템 실행 시작")
        
        # 1. 로직 검증 테스트
        logic_results = self.run_logic_verification_test()
        
        # 2. 현행 테스트
        current_results = self.run_current_test()
        
        # 3. 비교 리포트 생성
        comparison_report = self.generate_comparison_report(logic_results, current_results)
        
        print("\n" + comparison_report)
        
        return {
            'logic_verification': logic_results,
            'current_test': current_results,
            'comparison_report': comparison_report
        }


def main():
    """메인 실행 함수"""
    print("🚀 POSCO 시스템 이원화된 테스트 시작")
    print("테스트 구성:")
    print("  1. 로직 검증 테스트: 2025-08-06 19:00 기준 (완전한 데이터)")
    print("  2. 현행 테스트: 현재 시점 기준 (실시간 상황)")
    print()
    
    # 이원화된 테스트 시스템 실행
    test_system = DualModeTestSystem()
    results = test_system.run_dual_mode_test()
    
    print("\n🎉 이원화된 테스트 완료!")
    return results


if __name__ == "__main__":
    main()