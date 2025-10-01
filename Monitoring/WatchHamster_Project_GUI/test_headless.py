#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WatchHamster 헤드리스 테스트 스크립트
GUI 없이 모든 기능을 테스트합니다.
"""

import sys
import os
import time
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def print_header(title):
    """섹션 헤더 출력"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def test_performance_optimizer():
    """성능 최적화 시스템 테스트 (GUI 없음)"""
    print_header("성능 최적화 시스템 테스트")
    
    try:
        from core.performance_optimizer import PerformanceOptimizer
        
        print("📋 성능 최적화 시스템 초기화 중...")
        optimizer = PerformanceOptimizer()
        
        # GUI 없이 백엔드만 시작
        optimizer.start_backend_only()
        print("✅ 성능 최적화 백엔드가 시작되었습니다.")
        
        # 캐시 테스트
        test_data = {"user": "홍길동", "timestamp": str(datetime.now())}
        optimizer.set_cached_data("test_session", test_data)
        cached = optimizer.get_cached_data("test_session")
        
        if cached:
            print(f"✅ 캐시 시스템 정상 작동: {cached['user']}")
        
        # 성능 메트릭 수집
        metrics = optimizer.get_performance_metrics()
        print(f"✅ CPU 사용률: {metrics.get('cpu_percent', 'N/A')}%")
        print(f"✅ 메모리 사용량: {metrics.get('memory_mb', 'N/A')}MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 성능 최적화 시스템 테스트 실패: {e}")
        return False

def test_stability_manager():
    """안정성 관리자 테스트 (GUI 없음)"""
    print_header("안정성 관리자 테스트")
    
    try:
        from core.stability_manager import StabilityManager
        
        print("📋 안정성 관리자 초기화 중...")
        manager = StabilityManager(project_root)
        
        # GUI 없이 백엔드만 시작
        manager.start_headless()
        print("✅ 안정성 관리자 백엔드가 시작되었습니다.")
        
        # 시스템 헬스 체크
        health = manager.check_system_health()
        print(f"✅ 메모리 사용량: {health.get('memory_usage_mb', 'N/A')}MB")
        print(f"✅ CPU 사용률: {health.get('cpu_usage_percent', 'N/A')}%")
        
        # 설정 파일 백업 테스트
        backup_result = manager.backup_and_verify_configs()
        if backup_result:
            print("✅ 설정 파일 백업 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 안정성 관리자 테스트 실패: {e}")
        return False

def test_cache_monitor():
    """캐시 모니터 테스트 (GUI 없음)"""
    print_header("캐시 모니터 테스트")
    
    try:
        from core.cache_monitor import CacheMonitor
        
        print("📋 캐시 모니터 초기화 중...")
        cache_monitor = CacheMonitor()
        print("✅ 캐시 모니터 초기화 완료")
        
        # 캐시 데이터 추가
        cache_monitor.set("test_key_1", "테스트 데이터 1")
        cache_monitor.set("test_key_2", {"name": "김철수", "age": 30})
        print("✅ 캐시 데이터 추가 완료")
        
        # 캐시 통계 확인
        stats = cache_monitor.get_stats()
        print(f"✅ 캐시 항목 수: {stats.get('total_items', 0)}")
        print(f"✅ 메모리 사용량: {stats.get('memory_usage_mb', 0):.2f}MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 캐시 모니터 테스트 실패: {e}")
        return False

def test_message_template():
    """메시지 템플릿 엔진 테스트 (GUI 없음)"""
    print_header("메시지 템플릿 엔진 테스트")
    
    try:
        from Posco_News_Mini_Final_GUI.message_template_engine import MessageTemplateEngine
        
        print("📋 메시지 템플릿 엔진 초기화 중...")
        template_engine = MessageTemplateEngine()
        print("✅ 메시지 템플릿 엔진 초기화 완료")
        
        # 템플릿 데이터
        template_data = {
            "user_name": "홍길동",
            "company": "POSCO",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 템플릿 렌더링 테스트
        welcome_msg = template_engine.render_template("welcome", template_data)
        if welcome_msg:
            print(f"✅ 환영 메시지 렌더링 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 메시지 템플릿 엔진 테스트 실패: {e}")
        return False

def test_posco_backend():
    """POSCO 백엔드 기능 테스트 (GUI 없음)"""
    print_header("POSCO 백엔드 기능 테스트")
    
    try:
        from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager
        
        print("📋 POSCO 백엔드 초기화 중...")
        gui_manager = PoscoGUIManager()
        
        # 시스템 정보 수집 (GUI 없음)
        system_info = gui_manager.get_system_info()
        print(f"✅ 운영체제: {system_info.get('os', 'Unknown')}")
        print(f"✅ Python 버전: {system_info.get('python_version', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ POSCO 백엔드 테스트 실패: {e}")
        return False

def main():
    """메인 헤드리스 테스트 실행"""
    print("🐹 WatchHamster 헤드리스 테스트 시작")
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 프로젝트 경로: {project_root}")
    print("🚫 GUI 없이 백엔드 기능만 테스트합니다.")
    
    # 테스트 함수들
    tests = [
        ("성능 최적화 시스템", test_performance_optimizer),
        ("안정성 관리자", test_stability_manager),
        ("캐시 모니터", test_cache_monitor),
        ("메시지 템플릿 엔진", test_message_template),
        ("POSCO 백엔드", test_posco_backend)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔄 {test_name} 테스트 실행 중...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과")
            else:
                failed += 1
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 테스트 오류: {e}")
        
        time.sleep(1)  # 테스트 간 대기
    
    print_header("테스트 결과 요약")
    print(f"✅ 통과: {passed}개")
    print(f"❌ 실패: {failed}개")
    print(f"📊 성공률: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 모든 백엔드 기능이 정상 작동합니다!")
    else:
        print("⚠️  일부 기능에 문제가 있습니다. 로그를 확인해주세요.")

if __name__ == "__main__":
    main()