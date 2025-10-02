#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WatchHamster 빠른 시스템 체크
GUI 없이 모든 핵심 기능의 상태를 확인합니다.
"""

import sys
import os
import platform
import time
from datetime import datetime

def check_python_environment():
    """Python 환경 확인"""
    print("🐍 Python 환경 체크")
    print(f"   Python 버전: {sys.version}")
    print(f"   플랫폼: {platform.platform()}")
    print(f"   아키텍처: {platform.architecture()[0]}")
    
    # tkinter 확인
    try:
        import tkinter
        print("   ✅ tkinter 사용 가능")
    except ImportError:
        print("   ❌ tkinter 사용 불가 (GUI 기능 제한)")
    
    # 필수 패키지 확인
    required_packages = ['psutil', 'threading', 'json', 'datetime']
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} 사용 가능")
        except ImportError:
            print(f"   ❌ {package} 사용 불가")

def check_project_structure():
    """프로젝트 구조 확인"""
    print("\n📁 프로젝트 구조 체크")
    
    required_dirs = [
        'core',
        'gui_components', 
        'config',
        'Posco_News_Mini_Final_GUI'
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/ 디렉토리 존재")
        else:
            print(f"   ❌ {dir_name}/ 디렉토리 없음")
    
    # 주요 파일 확인
    required_files = [
        'main_gui.py',
        'core/performance_optimizer.py',
        'core/stability_manager.py',
        'core/cache_monitor.py'
    ]
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"   ✅ {file_name} 파일 존재")
        else:
            print(f"   ❌ {file_name} 파일 없음")

def check_core_functionality():
    """핵심 기능 확인"""
    print("\n⚡ 핵심 기능 체크")
    
    # 성능 최적화 시스템
    try:
        sys.path.insert(0, '.')
        from core.performance_optimizer import PerformanceOptimizer
        optimizer = PerformanceOptimizer()
        print("   ✅ 성능 최적화 시스템 로드 성공")
        
        # 간단한 기능 테스트
        optimizer.set_cached_data("test", "data")
        if optimizer.get_cached_data("test") == "data":
            print("   ✅ 캐시 시스템 정상 작동")
        
    except Exception as e:
        print(f"   ❌ 성능 최적화 시스템 오류: {e}")
    
    # 안정성 관리자
    try:
        from core.stability_manager import StabilityManager
        manager = StabilityManager(".")
        print("   ✅ 안정성 관리자 로드 성공")
        
        # 시스템 헬스 체크
        health = manager.check_system_health()
        if health:
            print(f"   ✅ 시스템 헬스 체크 성공 (메모리: {health.get('memory_usage_mb', 'N/A')}MB)")
        
    except Exception as e:
        print(f"   ❌ 안정성 관리자 오류: {e}")
    
    # 캐시 모니터
    try:
        from core.cache_monitor import CacheMonitor
        cache_monitor = CacheMonitor()
        print("   ✅ 캐시 모니터 로드 성공")
        
        # 캐시 기능 테스트
        cache_monitor.set("test_key", "test_value")
        stats = cache_monitor.get_stats()
        if stats:
            print(f"   ✅ 캐시 모니터 정상 작동 (항목: {stats.get('total_items', 0)}개)")
        
    except Exception as e:
        print(f"   ❌ 캐시 모니터 오류: {e}")

def check_posco_functionality():
    """POSCO 기능 확인"""
    print("\n🏭 POSCO 기능 체크")
    
    try:
        from Posco_News_Mini_Final_GUI.message_template_engine import MessageTemplateEngine
        template_engine = MessageTemplateEngine()
        print("   ✅ 메시지 템플릿 엔진 로드 성공")
        
    except Exception as e:
        print(f"   ❌ 메시지 템플릿 엔진 오류: {e}")
    
    try:
        from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager
        gui_manager = PoscoGUIManager()
        print("   ✅ POSCO GUI 관리자 로드 성공")
        
    except Exception as e:
        print(f"   ❌ POSCO GUI 관리자 오류: {e}")

def check_system_resources():
    """시스템 리소스 확인"""
    print("\n💻 시스템 리소스 체크")
    
    try:
        import psutil
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"   📊 CPU 사용률: {cpu_percent}%")
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = memory.used / 1024 / 1024
        print(f"   💾 메모리 사용률: {memory_percent}% ({memory_mb:.0f}MB)")
        
        # 디스크 사용률
        disk = psutil.disk_usage('.')
        disk_percent = (disk.used / disk.total) * 100
        print(f"   💿 디스크 사용률: {disk_percent:.1f}%")
        
        # 시스템 상태 평가
        if cpu_percent < 80 and memory_percent < 80 and disk_percent < 90:
            print("   ✅ 시스템 리소스 상태 양호")
        else:
            print("   ⚠️  시스템 리소스 사용률 높음")
            
    except Exception as e:
        print(f"   ❌ 시스템 리소스 체크 오류: {e}")

def provide_recommendations():
    """권장사항 제공"""
    print("\n💡 권장사항")
    
    # GUI 크래시 문제 해결
    print("   🔧 GUI 크래시 문제 해결:")
    print("      - python3 test_headless.py (GUI 없이 테스트)")
    print("      - python3 core/performance_optimizer.py (개별 컴포넌트 테스트)")
    print("      - brew install python-tk (tkinter 재설치)")
    
    # 백엔드 실행
    print("   🚀 백엔드만 실행:")
    print("      - python3 core/performance_optimizer.py")
    print("      - python3 core/stability_manager.py")
    print("      - python3 core/cache_monitor.py")
    
    # 모니터링
    print("   📊 모니터링:")
    print("      - tail -f logs/*.log (로그 실시간 확인)")
    print("      - python3 TASK20_REAL_100_PERCENT_PROOF.py (전체 검증)")

def main():
    """메인 시스템 체크 실행"""
    print("🐹 WatchHamster 시스템 체크")
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 각종 체크 실행
    check_python_environment()
    check_project_structure()
    check_core_functionality()
    check_posco_functionality()
    check_system_resources()
    provide_recommendations()
    
    print("\n" + "="*60)
    print("🎉 시스템 체크 완료!")
    print("📖 자세한 해결 방법은 MACOS_GUI_FIX.md를 참고하세요.")

if __name__ == "__main__":
    main()