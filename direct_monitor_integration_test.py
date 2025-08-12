#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
직접 모니터 통합 테스트
실제 모니터 파일을 직접 import하여 웹훅 기능 테스트

Created: 2025-08-12
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime

def test_direct_monitor_integration():
    """직접 모니터 통합 테스트"""
    print("🔧 직접 모니터 통합 테스트 시작")
    print("=" * 60)
    
    test_results = []
    
    # 1. 모니터 파일 직접 실행 테스트
    print("📁 모니터 파일 직접 실행 테스트...")
    
    try:
        # 현재 디렉토리와 core/monitoring 디렉토리를 Python 경로에 추가
        current_dir = os.path.dirname(os.path.abspath(__file__))
        monitoring_dir = os.path.join(current_dir, 'core', 'monitoring')
        
        if monitoring_dir not in sys.path:
            sys.path.insert(0, monitoring_dir)
        
        # 모니터 파일을 직접 import
        import importlib.util
        monitor_file = os.path.join(monitoring_dir, 'monitor_WatchHamster_v3.0.py')
        
        if os.path.exists(monitor_file):
            spec = importlib.util.spec_from_file_location("monitor_module", monitor_file)
            monitor_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(monitor_module)
            
            print("✅ 모니터 파일 import 성공")
            
            # 클래스 확인
            if hasattr(monitor_module, 'WatchHamsterV3Monitor'):
                monitor_class = getattr(monitor_module, 'WatchHamsterV3Monitor')
                print("✅ WatchHamsterV3Monitor 클래스 발견")
                
                # 인스턴스 생성 시도
                try:
                    monitor = monitor_class()
                    print("✅ 모니터 인스턴스 생성 성공")
                    
                    # 웹훅 함수들 확인
                    webhook_functions = [
                        'send_status_notification',
                        'send_notification',
                        'send_enhanced_status_notification',
                        'send_startup_notification_v2'
                    ]
                    
                    found_functions = []
                    for func_name in webhook_functions:
                        if hasattr(monitor, func_name):
                            func = getattr(monitor, func_name)
                            if callable(func):
                                found_functions.append(func_name)
                                print(f"✅ {func_name} 함수 발견 및 호출 가능")
                            else:
                                print(f"⚠️ {func_name} 속성 존재하지만 호출 불가")
                        else:
                            print(f"❌ {func_name} 함수 없음")
                    
                    test_results.append({
                        'test': '모니터 클래스 및 웹훅 함수 확인',
                        'success': len(found_functions) > 0,
                        'found_functions': found_functions,
                        'total_functions': len(webhook_functions)
                    })
                    
                    # 웹훅 URL 설정 확인
                    webhook_urls = []
                    if hasattr(monitor_module, 'DOORAY_WEBHOOK_URL'):
                        dooray_url = getattr(monitor_module, 'DOORAY_WEBHOOK_URL')
                        webhook_urls.append(('DOORAY_WEBHOOK_URL', dooray_url))
                        print(f"✅ DOORAY_WEBHOOK_URL 설정됨: {dooray_url[:50]}...")
                    
                    if hasattr(monitor_module, 'WATCHHAMSTER_WEBHOOK_URL'):
                        watchhamster_url = getattr(monitor_module, 'WATCHHAMSTER_WEBHOOK_URL')
                        webhook_urls.append(('WATCHHAMSTER_WEBHOOK_URL', watchhamster_url))
                        print(f"✅ WATCHHAMSTER_WEBHOOK_URL 설정됨: {watchhamster_url[:50]}...")
                    
                    test_results.append({
                        'test': '웹훅 URL 설정 확인',
                        'success': len(webhook_urls) > 0,
                        'webhook_urls': webhook_urls
                    })
                    
                except Exception as e:
                    print(f"❌ 모니터 인스턴스 생성 실패: {e}")
                    test_results.append({
                        'test': '모니터 인스턴스 생성',
                        'success': False,
                        'error': str(e)
                    })
            else:
                print("❌ WatchHamsterV3Monitor 클래스 없음")
                # 다른 클래스들 확인
                classes = [name for name in dir(monitor_module) if name.endswith('Monitor')]
                print(f"발견된 Monitor 클래스들: {classes}")
                
        else:
            print(f"❌ 모니터 파일 없음: {monitor_file}")
            test_results.append({
                'test': '모니터 파일 존재',
                'success': False,
                'error': f'파일 없음: {monitor_file}'
            })
            
    except Exception as e:
        print(f"❌ 모니터 파일 import 실패: {e}")
        print(f"상세 오류: {traceback.format_exc()}")
        test_results.append({
            'test': '모니터 파일 import',
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })
    
    # 2. 실제 웹훅 함수 코드 확인
    print("\n📝 웹훅 함수 코드 확인...")
    
    try:
        monitor_file = os.path.join('core', 'monitoring', 'monitor_WatchHamster_v3.0.py')
        if os.path.exists(monitor_file):
            with open(monitor_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 웹훅 함수 정의 확인
            webhook_function_patterns = [
                'def send_status_notification',
                'def send_notification',
                'def send_enhanced_status_notification',
                'def send_startup_notification_v2'
            ]
            
            found_patterns = []
            for pattern in webhook_function_patterns:
                if pattern in content:
                    found_patterns.append(pattern)
                    print(f"✅ {pattern} 코드 발견")
                else:
                    print(f"❌ {pattern} 코드 없음")
            
            test_results.append({
                'test': '웹훅 함수 코드 존재 확인',
                'success': len(found_patterns) > 0,
                'found_patterns': found_patterns,
                'total_patterns': len(webhook_function_patterns)
            })
            
            # 웹훅 URL 설정 확인
            url_patterns = ['DOORAY_WEBHOOK_URL', 'WATCHHAMSTER_WEBHOOK_URL']
            found_urls = []
            for pattern in url_patterns:
                if pattern in content:
                    found_urls.append(pattern)
                    print(f"✅ {pattern} 설정 발견")
                else:
                    print(f"❌ {pattern} 설정 없음")
            
            test_results.append({
                'test': '웹훅 URL 설정 코드 확인',
                'success': len(found_urls) > 0,
                'found_urls': found_urls
            })
            
        else:
            print(f"❌ 모니터 파일 없음: {monitor_file}")
            
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {e}")
        test_results.append({
            'test': '파일 읽기',
            'success': False,
            'error': str(e)
        })
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("🎯 직접 모니터 통합 테스트 결과")
    print("=" * 60)
    
    total_tests = len(test_results)
    successful_tests = sum(1 for r in test_results if r['success'])
    
    print(f"총 테스트: {total_tests}")
    print(f"성공한 테스트: {successful_tests}")
    print(f"실패한 테스트: {total_tests - successful_tests}")
    print(f"성공률: {(successful_tests / total_tests * 100):.1f}%")
    
    # 상세 결과 저장
    report = {
        'test_summary': {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'timestamp': datetime.now().isoformat()
        },
        'detailed_results': test_results
    }
    
    report_filename = f'direct_monitor_integration_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 상세 결과 저장: {report_filename}")
    
    if successful_tests == total_tests:
        print("🎉 모든 테스트 성공!")
        return True
    else:
        print("⚠️ 일부 테스트 실패")
        return False

if __name__ == "__main__":
    success = test_direct_monitor_integration()
    exit(0 if success else 1)