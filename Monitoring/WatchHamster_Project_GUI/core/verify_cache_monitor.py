#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
캐시 모니터 검증 스크립트
간단한 기능 검증
"""

import os
import sys
import json
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from cache_monitor import CacheMonitor, CacheStatus, DataType, CacheAlert
    print("✅ 캐시 모니터 모듈 임포트 성공")
except ImportError as e:
    print(f"❌ 캐시 모니터 모듈 임포트 실패: {e}")
    sys.exit(1)

def verify_basic_functionality():
    """기본 기능 검증"""
    print("\n🔍 기본 기능 검증 시작")
    
    try:
        # 캐시 모니터 생성
        monitor = CacheMonitor()
        print("✅ CacheMonitor 인스턴스 생성 성공")
        
        # 캐시 상태 확인
        status = monitor.check_cache_status()
        print(f"✅ 캐시 상태 확인 성공 ({len(status)}개 데이터 타입)")
        
        # 각 데이터 타입별 상태 출력
        for data_type, cache_info in status.items():
            print(f"  {data_type.value}: {cache_info.status.value}")
            if cache_info.warning_message:
                print(f"    ⚠️ {cache_info.warning_message}")
        
        # 요약 정보 생성
        summary = monitor.get_cache_summary()
        print(f"✅ 캐시 요약 생성 성공 (건강도: {summary['overall_health']})")
        
        # 상세 상태 조회
        detailed = monitor.get_detailed_status()
        print(f"✅ 상세 상태 조회 성공 ({len(detailed)}개 항목)")
        
        # 알림 콜백 테스트
        alerts_received = []
        def test_callback(alert):
            alerts_received.append(alert)
        
        monitor.add_alert_callback(test_callback)
        print("✅ 알림 콜백 등록 성공")
        
        # 설정 업데이트 테스트
        monitor.update_config({'check_interval_seconds': 60})
        print("✅ 설정 업데이트 성공")
        
        print("🎉 모든 기본 기능 검증 완료")
        return True
        
    except Exception as e:
        print(f"❌ 기본 기능 검증 실패: {e}")
        return False

def verify_data_structures():
    """데이터 구조 검증"""
    print("\n📊 데이터 구조 검증 시작")
    
    try:
        # Enum 클래스 검증
        print(f"✅ CacheStatus: {[s.value for s in CacheStatus]}")
        print(f"✅ DataType: {[d.value for d in DataType]}")
        
        # CacheAlert 생성 테스트
        alert = CacheAlert(
            alert_type="test",
            data_type=DataType.KOSPI,
            message="테스트 알림",
            timestamp=datetime.now(),
            severity="info"
        )
        print("✅ CacheAlert 생성 성공")
        
        print("🎉 모든 데이터 구조 검증 완료")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 구조 검증 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🧪 캐시 모니터 검증 시작")
    print("=" * 50)
    
    results = []
    
    # 기본 기능 검증
    results.append(verify_basic_functionality())
    
    # 데이터 구조 검증
    results.append(verify_data_structures())
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📋 검증 결과 요약")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"총 검증: {total_tests}")
    print(f"성공: {passed_tests}")
    print(f"실패: {total_tests - passed_tests}")
    
    if all(results):
        print("\n🎉 모든 검증 통과! 캐시 모니터가 정상적으로 구현되었습니다.")
        return 0
    else:
        print("\n⚠️ 일부 검증 실패")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)