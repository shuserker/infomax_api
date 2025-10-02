#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
캐시 모니터 데모 스크립트
실제 동작 시연
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def demo_cache_monitor():
    """캐시 모니터 데모"""
    print("🔍 캐시 모니터 데모 시작")
    print("=" * 50)
    
    try:
        from cache_monitor import CacheMonitor, DataType, CacheStatus
        
        # 캐시 모니터 생성
        monitor = CacheMonitor()
        print("✅ 캐시 모니터 생성 완료")
        
        # 알림 수집기 설정
        received_alerts = []
        def alert_collector(alert):
            received_alerts.append(alert)
            print(f"📢 [알림] {alert.data_type.value}: {alert.message}")
        
        monitor.add_alert_callback(alert_collector)
        print("✅ 알림 콜백 등록 완료")
        
        # 현재 캐시 상태 확인
        print("\n📊 현재 캐시 상태:")
        status = monitor.check_cache_status()
        
        for data_type, cache_info in status.items():
            print(f"  {data_type.value}:")
            print(f"    상태: {cache_info.status.value}")
            print(f"    품질: {cache_info.quality_score:.1%}")
            print(f"    신뢰도: {cache_info.confidence:.1%}")
            if cache_info.last_updated:
                age_minutes = (datetime.now() - cache_info.last_updated).total_seconds() / 60
                print(f"    나이: {age_minutes:.1f}분")
            if cache_info.warning_message:
                print(f"    ⚠️ {cache_info.warning_message}")
            print()
        
        # 캐시 요약 정보
        print("📋 캐시 요약:")
        summary = monitor.get_cache_summary()
        print(f"  전체 건강도: {summary['overall_health']}")
        print(f"  마지막 확인: {summary['last_check']}")
        
        status_counts = summary['status_counts']
        print("  상태별 카운트:")
        for status_name, count in status_counts.items():
            if count > 0:
                print(f"    {status_name}: {count}개")
        
        if summary['warnings']:
            print("  ⚠️ 경고사항:")
            for warning in summary['warnings']:
                print(f"    - {warning['data_type']}: {warning['message']}")
        
        if summary['recommendations']:
            print("  💡 권장사항:")
            for rec in summary['recommendations']:
                print(f"    - {rec}")
        
        # 모니터링 설정 표시
        print("\n⚙️ 모니터링 설정:")
        config = monitor.monitoring_config
        print(f"  확인 간격: {config['check_interval_seconds']}초")
        print(f"  신선 기준: {config['fresh_threshold_minutes']}분")
        print(f"  오래됨 기준: {config['stale_threshold_minutes']}분")
        print(f"  만료 기준: {config['expired_threshold_minutes']}분")
        print(f"  최소 품질: {config['min_quality_threshold']:.1%}")
        print(f"  최소 신뢰도: {config['min_confidence_threshold']:.1%}")
        
        # 수신된 알림 표시
        if received_alerts:
            print(f"\n📢 수신된 알림 ({len(received_alerts)}개):")
            for i, alert in enumerate(received_alerts, 1):
                print(f"  {i}. [{alert.severity.upper()}] {alert.data_type.value}")
                print(f"     {alert.message}")
                print(f"     시간: {alert.timestamp.strftime('%H:%M:%S')}")
                if alert.auto_action:
                    print(f"     자동 액션: {alert.auto_action}")
                print()
        
        # 상태 보고서 생성
        print("📄 상태 보고서 생성 중...")
        report_path = monitor.export_status_report()
        print(f"✅ 보고서 저장: {os.path.basename(report_path)}")
        
        print("\n🎉 캐시 모니터 데모 완료!")
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 데모 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_cache_files():
    """캐시 파일 정보 표시"""
    print("\n📁 캐시 파일 정보:")
    
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    
    if not os.path.exists(data_dir):
        print(f"  데이터 디렉토리가 없습니다: {data_dir}")
        return
    
    cache_files = [
        "market_data_cache.json",
        "data_quality_log.json"
    ]
    
    for filename in cache_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"  ✅ {filename}")
            print(f"     크기: {size:,} bytes")
            print(f"     수정: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # JSON 파일이면 내용 미리보기
            if filename.endswith('.json') and size > 0:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if filename == "market_data_cache.json":
                        market_data = data.get('market_data', {})
                        print(f"     데이터 타입: {len(market_data)}개")
                        if 'overall_quality' in market_data:
                            print(f"     전체 품질: {market_data['overall_quality']:.1%}")
                    
                    elif filename == "data_quality_log.json":
                        print(f"     로그 엔트리: {len(data)}개")
                        if data:
                            latest = data[-1]
                            print(f"     최신 품질: {latest.get('overall_quality', 0):.1%}")
                
                except Exception as e:
                    print(f"     ⚠️ 파일 읽기 오류: {e}")
        else:
            print(f"  ❌ {filename} (없음)")
        print()

def main():
    """메인 함수"""
    print("🧪 캐시 모니터 데모 및 검증")
    print("=" * 60)
    
    # 캐시 파일 정보 표시
    show_cache_files()
    
    # 캐시 모니터 데모 실행
    success = demo_cache_monitor()
    
    if success:
        print("\n✅ 캐시 모니터가 성공적으로 구현되었습니다!")
        print("\n주요 기능:")
        print("  📊 캐시 데이터 상태 모니터링")
        print("  ⚠️ 데이터 부족 시 GUI 경고 알림")
        print("  📅 과거 데이터 사용 시 명시적 표시")
        print("  🔄 캐시 데이터 자동 갱신 및 품질 관리")
        print("  📄 상태 보고서 생성")
        print("  🔗 GUI 시스템과의 통합")
    else:
        print("\n❌ 캐시 모니터 구현에 문제가 있습니다.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)