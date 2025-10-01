#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WatchHamster 전체 기능 데모 스크립트
Task 1-20까지 완성된 모든 기능을 순차적으로 시연합니다.
"""

import sys
import os
import time
import threading
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def print_header(title):
    """섹션 헤더 출력"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_step(step, description):
    """단계별 진행 상황 출력"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def demo_performance_optimizer():
    """성능 최적화 시스템 데모 (Task 20)"""
    print_header("성능 최적화 시스템 데모 (Task 20)")
    
    try:
        from core.performance_optimizer import PerformanceOptimizer
        
        print_step(1, "성능 최적화 시스템 초기화")
        optimizer = PerformanceOptimizer()
        optimizer.start()
        print("✅ 성능 최적화 시스템이 시작되었습니다.")
        
        print_step(2, "캐시 시스템 테스트")
        # 캐시에 데이터 저장
        test_data = {"user": "홍길동", "role": "admin", "timestamp": str(datetime.now())}
        optimizer.set_cached_data("user_session", test_data)
        print("✅ 캐시에 사용자 세션 데이터를 저장했습니다.")
        
        # 캐시에서 데이터 조회
        cached_data = optimizer.get_cached_data("user_session")
        if cached_data:
            print(f"✅ 캐시에서 데이터 조회 성공: {cached_data['user']}")
        
        print_step(3, "성능 메트릭 수집")
        metrics = optimizer.get_performance_metrics()
        print(f"✅ CPU 사용률: {metrics.get('cpu_percent', 'N/A')}%")
        print(f"✅ 메모리 사용량: {metrics.get('memory_mb', 'N/A')}MB")
        
        print_step(4, "백그라운드 작업 스케줄링")
        def sample_background_task():
            print("🔄 백그라운드 작업이 실행되었습니다.")
            time.sleep(1)
            print("✅ 백그라운드 작업이 완료되었습니다.")
        
        optimizer.schedule_background_task(sample_background_task)
        time.sleep(2)  # 백그라운드 작업 완료 대기
        
    except Exception as e:
        print(f"❌ 성능 최적화 시스템 데모 중 오류: {e}")

def demo_stability_manager():
    """안정성 관리자 데모 (Task 20)"""
    print_header("안정성 관리자 데모 (Task 20)")
    
    try:
        from core.stability_manager import StabilityManager
        
        print_step(1, "안정성 관리자 초기화")
        manager = StabilityManager(project_root)
        manager.start()
        print("✅ 안정성 관리자가 시작되었습니다.")
        
        print_step(2, "시스템 헬스 체크")
        health = manager.check_system_health()
        print(f"✅ 메모리 사용량: {health.get('memory_usage_mb', 'N/A')}MB")
        print(f"✅ CPU 사용률: {health.get('cpu_usage_percent', 'N/A')}%")
        print(f"✅ 디스크 사용률: {health.get('disk_usage_percent', 'N/A')}%")
        
        print_step(3, "설정 파일 백업 및 검증")
        backup_result = manager.backup_and_verify_configs()
        if backup_result:
            print("✅ 설정 파일 백업이 완료되었습니다.")
        
    except Exception as e:
        print(f"❌ 안정성 관리자 데모 중 오류: {e}")

def demo_cache_monitor():
    """캐시 모니터 데모 (Task 13)"""
    print_header("캐시 모니터링 시스템 데모 (Task 13)")
    
    try:
        from core.cache_monitor import CacheMonitor
        
        print_step(1, "캐시 모니터 초기화")
        cache_monitor = CacheMonitor()
        print("✅ 캐시 모니터가 초기화되었습니다.")
        
        print_step(2, "캐시 데이터 추가")
        cache_monitor.set("test_key_1", "테스트 데이터 1")
        cache_monitor.set("test_key_2", {"name": "김철수", "age": 30})
        print("✅ 캐시에 테스트 데이터를 추가했습니다.")
        
        print_step(3, "캐시 통계 확인")
        stats = cache_monitor.get_stats()
        print(f"✅ 캐시 항목 수: {stats.get('total_items', 0)}")
        print(f"✅ 캐시 히트율: {stats.get('hit_rate', 0):.2f}%")
        print(f"✅ 메모리 사용량: {stats.get('memory_usage_mb', 0):.2f}MB")
        
    except Exception as e:
        print(f"❌ 캐시 모니터 데모 중 오류: {e}")

def demo_integrated_status():
    """통합 상태 리포터 데모 (Task 14)"""
    print_header("통합 상태 리포터 데모 (Task 14)")
    
    try:
        from core.integrated_status_reporter import IntegratedStatusReporter
        
        print_step(1, "통합 상태 리포터 초기화")
        reporter = IntegratedStatusReporter()
        print("✅ 통합 상태 리포터가 초기화되었습니다.")
        
        print_step(2, "시스템 상태 수집")
        status = reporter.get_system_status()
        print(f"✅ 시스템 상태: {status.get('overall_status', 'Unknown')}")
        print(f"✅ 활성 서비스 수: {len(status.get('services', []))}")
        
        print_step(3, "상태 리포트 생성")
        report = reporter.generate_status_report()
        if report:
            print("✅ 상태 리포트가 생성되었습니다.")
            print(f"   - 리포트 시간: {report.get('timestamp', 'N/A')}")
            print(f"   - 전체 상태: {report.get('overall_health', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 통합 상태 리포터 데모 중 오류: {e}")

def demo_message_template():
    """메시지 템플릿 엔진 데모 (Task 8)"""
    print_header("메시지 템플릿 엔진 데모 (Task 8)")
    
    try:
        from Posco_News_Mini_Final_GUI.message_template_engine import MessageTemplateEngine
        
        print_step(1, "메시지 템플릿 엔진 초기화")
        template_engine = MessageTemplateEngine()
        print("✅ 메시지 템플릿 엔진이 초기화되었습니다.")
        
        print_step(2, "템플릿 렌더링 테스트")
        template_data = {
            "user_name": "홍길동",
            "company": "POSCO",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 환영 메시지 템플릿 렌더링
        welcome_msg = template_engine.render_template("welcome", template_data)
        if welcome_msg:
            print(f"✅ 환영 메시지: {welcome_msg}")
        
        # 알림 메시지 템플릿 렌더링
        notification_msg = template_engine.render_template("notification", template_data)
        if notification_msg:
            print(f"✅ 알림 메시지: {notification_msg}")
        
    except Exception as e:
        print(f"❌ 메시지 템플릿 엔진 데모 중 오류: {e}")

def demo_posco_gui_manager():
    """POSCO GUI 관리자 데모 (Task 16)"""
    print_header("POSCO GUI 관리자 데모 (Task 16)")
    
    try:
        from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager
        
        print_step(1, "POSCO GUI 관리자 초기화")
        gui_manager = PoscoGUIManager()
        print("✅ POSCO GUI 관리자가 초기화되었습니다.")
        
        print_step(2, "GUI 상태 확인")
        status = gui_manager.get_gui_status()
        print(f"✅ GUI 상태: {status.get('status', 'Unknown')}")
        print(f"✅ 활성 창 수: {status.get('active_windows', 0)}")
        
        print_step(3, "시스템 정보 수집")
        system_info = gui_manager.get_system_info()
        print(f"✅ 운영체제: {system_info.get('os', 'Unknown')}")
        print(f"✅ Python 버전: {system_info.get('python_version', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ POSCO GUI 관리자 데모 중 오류: {e}")

def demo_i18n_and_theme():
    """다국어 지원 및 테마 시스템 데모 (Task 18)"""
    print_header("다국어 지원 및 테마 시스템 데모 (Task 18)")
    
    try:
        from gui_components.i18n_manager import I18nManager
        from gui_components.theme_manager import ThemeManager
        
        print_step(1, "다국어 관리자 초기화")
        i18n = I18nManager()
        print("✅ 다국어 관리자가 초기화되었습니다.")
        
        # 한국어 텍스트
        i18n.set_language("ko")
        ko_text = i18n.get_text("welcome_message", "환영합니다!")
        print(f"✅ 한국어: {ko_text}")
        
        # 영어 텍스트
        i18n.set_language("en")
        en_text = i18n.get_text("welcome_message", "Welcome!")
        print(f"✅ English: {en_text}")
        
        print_step(2, "테마 관리자 초기화")
        theme_manager = ThemeManager()
        print("✅ 테마 관리자가 초기화되었습니다.")
        
        # 라이트 테마
        light_theme = theme_manager.get_theme("light")
        print(f"✅ 라이트 테마: {light_theme.get('name', 'Unknown')}")
        
        # 다크 테마
        dark_theme = theme_manager.get_theme("dark")
        print(f"✅ 다크 테마: {dark_theme.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 다국어/테마 시스템 데모 중 오류: {e}")

def main():
    """메인 데모 실행"""
    print("🐹 WatchHamster 전체 기능 데모 시작")
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 프로젝트 경로: {project_root}")
    
    # 각 기능별 데모 실행
    demo_functions = [
        demo_performance_optimizer,
        demo_stability_manager,
        demo_cache_monitor,
        demo_integrated_status,
        demo_message_template,
        demo_posco_gui_manager,
        demo_i18n_and_theme
    ]
    
    for i, demo_func in enumerate(demo_functions, 1):
        try:
            demo_func()
            time.sleep(1)  # 각 데모 사이에 잠시 대기
        except Exception as e:
            print(f"❌ 데모 {i} 실행 중 오류: {e}")
        
        if i < len(demo_functions):
            print("\n⏳ 다음 데모로 이동 중...")
            time.sleep(2)
    
    print_header("데모 완료")
    print("🎉 모든 기능 데모가 완료되었습니다!")
    print("📖 더 자세한 사용법은 WATCHHAMSTER_USER_MANUAL.md를 참고하세요.")
    print("🚀 빠른 시작은 QUICK_START_GUIDE.md를 참고하세요.")

if __name__ == "__main__":
    main()