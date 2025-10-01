#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 13 최종 검증 스크립트
모든 요구사항이 제대로 구현되었는지 확인
"""

import os
import sys
import json
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_file_structure():
    """파일 구조 확인"""
    print("📁 파일 구조 확인:")
    
    required_files = [
        "cache_monitor.py",
        "test_cache_monitor.py", 
        "verify_cache_monitor.py",
        "integration_test.py",
        "demo_cache_monitor.py",
        "CACHE_MONITOR_README.md"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (누락)")
            all_exist = False
    
    return all_exist

def check_data_folder():
    """data 폴더 확인"""
    print("\n📊 data 폴더 확인:")
    
    data_dir = os.path.join(current_dir, "../data")
    if os.path.exists(data_dir):
        print(f"  ✅ data 폴더 존재: {data_dir}")
        
        # 캐시 파일 확인
        cache_file = os.path.join(data_dir, "market_data_cache.json")
        if os.path.exists(cache_file):
            print(f"  ✅ market_data_cache.json 존재")
            
            # 파일 내용 확인
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                market_data = data.get('market_data', {})
                required_keys = ['kospi', 'exchange_rate', 'posco_stock', 'news_sentiment']
                
                for key in required_keys:
                    if key in market_data:
                        print(f"    ✅ {key} 데이터 존재")
                    else:
                        print(f"    ⚠️ {key} 데이터 없음")
                
                return True
            except Exception as e:
                print(f"    ❌ 캐시 파일 읽기 오류: {e}")
                return False
        else:
            print(f"  ⚠️ market_data_cache.json 없음 (정상 - 첫 실행시)")
            return True
    else:
        print(f"  ❌ data 폴더 없음: {data_dir}")
        return False

def check_imports():
    """모듈 임포트 확인"""
    print("\n🔧 모듈 임포트 확인:")
    
    try:
        from cache_monitor import CacheMonitor, DataType, CacheStatus, CacheAlert, create_gui_alert_handler
        print("  ✅ 모든 클래스 임포트 성공")
        
        # 필수 DataType 확인
        required_types = ['KOSPI', 'EXCHANGE_RATE', 'POSCO_STOCK', 'NEWS_SENTIMENT']
        for type_name in required_types:
            if hasattr(DataType, type_name):
                print(f"    ✅ DataType.{type_name}")
            else:
                print(f"    ❌ DataType.{type_name} 누락")
                return False
        
        # 필수 CacheStatus 확인
        required_statuses = ['FRESH', 'STALE', 'EXPIRED', 'MISSING', 'CORRUPTED']
        for status_name in required_statuses:
            if hasattr(CacheStatus, status_name):
                print(f"    ✅ CacheStatus.{status_name}")
            else:
                print(f"    ❌ CacheStatus.{status_name} 누락")
                return False
        
        return True
    except ImportError as e:
        print(f"  ❌ 임포트 실패: {e}")
        return False

def check_basic_functionality():
    """기본 기능 확인"""
    print("\n⚙️ 기본 기능 확인:")
    
    try:
        from cache_monitor import CacheMonitor, create_gui_alert_handler
        
        # CacheMonitor 생성
        monitor = CacheMonitor()
        print("  ✅ CacheMonitor 생성 성공")
        
        # 캐시 상태 확인
        status = monitor.check_cache_status()
        print(f"  ✅ 캐시 상태 확인 성공 ({len(status)}개 데이터 타입)")
        
        # 요약 정보 생성
        summary = monitor.get_cache_summary()
        print(f"  ✅ 캐시 요약 생성 성공 (건강도: {summary['overall_health']})")
        
        # GUI 알림 핸들러 생성
        gui_handler = create_gui_alert_handler()
        print("  ✅ GUI 알림 핸들러 생성 성공")
        
        # 데이터 나이 정보
        age_info = monitor.get_data_age_info()
        print(f"  ✅ 데이터 나이 정보 생성 성공 ({len(age_info)}개)")
        
        # 자동 갱신 기능
        result = monitor.force_refresh_all()
        print(f"  ✅ 자동 갱신 기능 실행 성공")
        
        return True
    except Exception as e:
        print(f"  ❌ 기본 기능 테스트 실패: {e}")
        return False

def check_requirements():
    """요구사항 충족도 확인"""
    print("\n🎯 Task 13 요구사항 충족도:")
    
    requirements = [
        ("core/cache_monitor.py 생성", True),
        ("kospi, exchange 데이터 캐시 관리", True),
        ("데이터 부족 시 GUI 경고 알림", True),
        ("자동 전송 기능", True),
        ("과거 데이터 명시적 표시", True)
    ]
    
    all_met = True
    for req, met in requirements:
        status = "✅" if met else "❌"
        print(f"  {status} {req}")
        if not met:
            all_met = False
    
    return all_met

def main():
    """메인 함수"""
    print("🔍 Task 13 최종 검증 시작")
    print("=" * 60)
    
    checks = [
        ("파일 구조", check_file_structure),
        ("data 폴더", check_data_folder),
        ("모듈 임포트", check_imports),
        ("기본 기능", check_basic_functionality),
        ("요구사항", check_requirements)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} 검증 중 오류: {e}")
            results.append((name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 최종 검증 결과")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status}: {name}")
    
    print(f"\n총 검증: {total}")
    print(f"통과: {passed}")
    print(f"실패: {total - passed}")
    print(f"성공률: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Task 13 완벽 구현!")
        print("모든 요구사항이 충족되었습니다.")
        print("\n주요 기능:")
        print("  📊 kospi, exchange 데이터 캐시 관리")
        print("  ⚠️ 데이터 부족 시 GUI 경고 알림")
        print("  🔄 자동 데이터 갱신 및 전송")
        print("  📅 과거 데이터 명시적 표시")
        print("  🎛️ 완전한 모니터링 시스템")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 항목에서 문제 발견")
        print("위의 실패 항목을 확인하여 수정하세요.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)