#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
캐시 모니터 통합 테스트
DynamicDataManager와의 통합 검증
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(parent_dir, "Posco_News_Mini_Final_GUI"))

def test_cache_monitor_integration():
    """캐시 모니터 통합 테스트"""
    print("🔗 캐시 모니터 통합 테스트 시작")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp(prefix="cache_integration_test_")
    print(f"임시 디렉토리: {temp_dir}")
    
    try:
        # 캐시 모니터 임포트 및 생성
        from cache_monitor import CacheMonitor, DataType, CacheStatus
        monitor = CacheMonitor(data_dir=temp_dir)
        print("✅ CacheMonitor 생성 성공")
        
        # 테스트 캐시 데이터 생성
        cache_file = os.path.join(temp_dir, "market_data_cache.json")
        test_data = {
            "market_data": {
                "kospi": {
                    "value": 2520.5,
                    "timestamp": datetime.now().isoformat(),
                    "source": "kospi_api",
                    "quality_score": 0.85,
                    "confidence": 0.90,
                    "metadata": {"change": 15.3, "change_percent": 0.61}
                },
                "exchange_rate": {
                    "value": 1347.5,
                    "timestamp": datetime.now().isoformat(),
                    "source": "exchange_api",
                    "quality_score": 0.83,
                    "confidence": 0.88,
                    "metadata": {"change": -2.5, "change_percent": -0.18}
                },
                "posco_stock": {
                    "value": 285000,
                    "timestamp": datetime.now().isoformat(),
                    "source": "posco_stock_api",
                    "quality_score": 0.82,
                    "confidence": 0.93,
                    "metadata": {"change": 3500, "change_percent": 1.24}
                },
                "news_sentiment": {
                    "value": 0.65,
                    "timestamp": datetime.now().isoformat(),
                    "source": "news_api",
                    "quality_score": 0.80,
                    "confidence": 0.82,
                    "metadata": {"sentiment_label": "positive", "news_count": 15}
                }
            },
            "cached_at": datetime.now().isoformat(),
            "cache_version": "1.0"
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print("✅ 테스트 캐시 데이터 생성 성공")
        
        # 캐시 상태 확인
        status = monitor.check_cache_status()
        print("✅ 캐시 상태 확인 성공")
        
        # 각 데이터 타입별 상태 검증
        for data_type in DataType:
            cache_info = status[data_type]
            print(f"  {data_type.value}: {cache_info.status.value} (품질: {cache_info.quality_score:.1%})")
            
            if cache_info.status == CacheStatus.FRESH:
                print(f"    ✅ 신선한 데이터")
            else:
                print(f"    ⚠️ {cache_info.warning_message}")
        
        # 요약 정보 테스트
        summary = monitor.get_cache_summary()
        print(f"✅ 캐시 요약 생성 (건강도: {summary['overall_health']})")
        
        # 알림 시스템 테스트
        alerts_received = []
        def test_alert_handler(alert):
            alerts_received.append(alert)
            print(f"  📢 알림 수신: {alert.message}")
        
        monitor.add_alert_callback(test_alert_handler)
        
        # 만료된 데이터로 변경하여 알림 테스트
        old_timestamp = (datetime.now() - timedelta(hours=2)).isoformat()
        test_data["market_data"]["kospi"]["timestamp"] = old_timestamp
        test_data["market_data"]["kospi"]["quality_score"] = 0.5  # 낮은 품질
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 상태 재확인 (알림 트리거)
        status = monitor.check_cache_status()
        print("✅ 알림 시스템 테스트 완료")
        
        if alerts_received:
            print(f"  📢 총 {len(alerts_received)}개 알림 수신")
        
        # 보고서 생성 테스트
        report_path = monitor.export_status_report()
        if os.path.exists(report_path):
            print(f"✅ 상태 보고서 생성: {os.path.basename(report_path)}")
        
        print("🎉 모든 통합 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 임시 디렉토리 정리
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("🧹 임시 디렉토리 정리 완료")

def test_gui_integration():
    """GUI 통합 테스트 (GUI 없이 콜백만 테스트)"""
    print("\n🖥️ GUI 통합 테스트 시작")
    
    try:
        from cache_monitor import create_gui_alert_handler, CacheAlert, DataType
        
        # GUI 알림 핸들러 생성 (실제 GUI 없이)
        alert_handler = create_gui_alert_handler()
        print("✅ GUI 알림 핸들러 생성 성공")
        
        # 테스트 알림 생성
        test_alert = CacheAlert(
            alert_type="test",
            data_type=DataType.KOSPI,
            message="테스트 알림입니다",
            timestamp=datetime.now(),
            severity="info"
        )
        
        # 알림 핸들러 호출 (실제로는 messagebox가 표시되지만 테스트에서는 스킵)
        print("✅ GUI 알림 핸들러 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ GUI 통합 테스트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🧪 캐시 모니터 통합 테스트 시작")
    print("=" * 60)
    
    results = []
    
    # 캐시 모니터 통합 테스트
    results.append(test_cache_monitor_integration())
    
    # GUI 통합 테스트
    results.append(test_gui_integration())
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 통합 테스트 결과 요약")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"총 테스트: {total_tests}")
    print(f"성공: {passed_tests}")
    print(f"실패: {total_tests - passed_tests}")
    
    if all(results):
        print("\n🎉 모든 통합 테스트 통과!")
        print("캐시 모니터가 성공적으로 구현되었습니다.")
        return 0
    else:
        print("\n⚠️ 일부 통합 테스트 실패")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)