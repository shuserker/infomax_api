#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WatchHamster GUI 없이 실행
macOS tkinter 크래시 문제 해결용
"""

import sys
import os
import time
import threading
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

class WatchHamsterNoGUI:
    """GUI 없는 WatchHamster 실행기"""
    
    def __init__(self):
        self.running = False
        self.services = {}
        
    def start_performance_optimizer(self):
        """성능 최적화 시스템 시작"""
        try:
            from core.performance_optimizer import PerformanceOptimizer
            self.services['performance'] = PerformanceOptimizer()
            self.services['performance'].start()
            print("✅ 성능 최적화 시스템 시작됨")
            return True
        except Exception as e:
            print(f"❌ 성능 최적화 시스템 오류: {e}")
            return False
    
    def start_stability_manager(self):
        """안정성 관리자 시작"""
        try:
            from core.stability_manager import StabilityManager
            self.services['stability'] = StabilityManager(project_root)
            self.services['stability'].start()
            print("✅ 안정성 관리자 시작됨")
            return True
        except Exception as e:
            print(f"❌ 안정성 관리자 오류: {e}")
            return False
    
    def start_cache_monitor(self):
        """캐시 모니터 시작"""
        try:
            from core.cache_monitor import CacheMonitor
            self.services['cache'] = CacheMonitor()
            print("✅ 캐시 모니터 시작됨")
            return True
        except Exception as e:
            print(f"❌ 캐시 모니터 오류: {e}")
            return False
    
    def start_posco_backend(self):
        """POSCO 백엔드 시작"""
        try:
            from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager
            self.services['posco'] = PoscoGUIManager()
            print("✅ POSCO 백엔드 시작됨")
            return True
        except Exception as e:
            print(f"❌ POSCO 백엔드 오류: {e}")
            return False
    
    def get_system_status(self):
        """시스템 상태 조회"""
        status = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'services': {},
            'metrics': {}
        }
        
        # 성능 메트릭
        if 'performance' in self.services:
            try:
                metrics = self.services['performance'].get_performance_metrics()
                status['metrics']['performance'] = metrics
                status['services']['performance'] = 'running'
            except:
                status['services']['performance'] = 'error'
        
        # 안정성 상태
        if 'stability' in self.services:
            try:
                health = self.services['stability'].check_system_health()
                status['metrics']['health'] = health
                status['services']['stability'] = 'running'
            except:
                status['services']['stability'] = 'error'
        
        # 캐시 상태
        if 'cache' in self.services:
            try:
                cache_stats = self.services['cache'].get_stats()
                status['metrics']['cache'] = cache_stats
                status['services']['cache'] = 'running'
            except:
                status['services']['cache'] = 'error'
        
        return status
    
    def print_status(self):
        """상태 출력"""
        status = self.get_system_status()
        
        print(f"\n🐹 WatchHamster 상태 - {status['timestamp']}")
        print("=" * 50)
        
        # 서비스 상태
        print("📊 서비스 상태:")
        for service, state in status['services'].items():
            icon = "✅" if state == "running" else "❌"
            print(f"   {icon} {service}: {state}")
        
        # 메트릭
        if 'performance' in status['metrics']:
            perf = status['metrics']['performance']
            print(f"\n⚡ 성능:")
            print(f"   CPU: {perf.get('cpu_percent', 'N/A')}%")
            print(f"   메모리: {perf.get('memory_mb', 'N/A')}MB")
        
        if 'health' in status['metrics']:
            health = status['metrics']['health']
            print(f"\n🛡️ 시스템 헬스:")
            print(f"   메모리 사용량: {health.get('memory_usage_mb', 'N/A')}MB")
            print(f"   CPU 사용률: {health.get('cpu_usage_percent', 'N/A')}%")
        
        if 'cache' in status['metrics']:
            cache = status['metrics']['cache']
            print(f"\n💾 캐시:")
            print(f"   항목 수: {cache.get('total_items', 'N/A')}")
            print(f"   메모리: {cache.get('memory_usage_mb', 'N/A')}MB")
    
    def monitor_loop(self):
        """모니터링 루프"""
        print("\n🔄 실시간 모니터링 시작 (Ctrl+C로 종료)")
        
        try:
            while self.running:
                self.print_status()
                time.sleep(10)  # 10초마다 업데이트
        except KeyboardInterrupt:
            print("\n\n🛑 모니터링 종료")
            self.stop()
    
    def start(self):
        """전체 시스템 시작"""
        print("🐹 WatchHamster 백엔드 시작")
        print("GUI 없이 모든 기능을 제공합니다!")
        print("=" * 50)
        
        self.running = True
        
        # 각 서비스 시작
        services_started = 0
        
        if self.start_performance_optimizer():
            services_started += 1
        
        if self.start_stability_manager():
            services_started += 1
        
        if self.start_cache_monitor():
            services_started += 1
        
        if self.start_posco_backend():
            services_started += 1
        
        print(f"\n🎯 {services_started}개 서비스가 시작되었습니다!")
        
        # 초기 상태 출력
        time.sleep(2)
        self.print_status()
        
        # 모니터링 시작
        self.monitor_loop()
    
    def stop(self):
        """시스템 종료"""
        self.running = False
        print("🔄 서비스 종료 중...")
        
        # 각 서비스 종료
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'stop'):
                    service.stop()
                print(f"✅ {service_name} 종료됨")
            except:
                print(f"⚠️ {service_name} 종료 중 오류")
        
        print("🎊 WatchHamster 종료 완료!")

def main():
    """메인 실행"""
    print("🍎 macOS GUI 크래시 해결용 - WatchHamster 백엔드 모드")
    print("모든 기능이 GUI 없이 정상 작동합니다!")
    
    # WatchHamster 백엔드 시작
    watchhamster = WatchHamsterNoGUI()
    
    try:
        watchhamster.start()
    except Exception as e:
        print(f"❌ 시작 오류: {e}")
        print("\n🔧 문제 해결:")
        print("1. python3 test_headless.py")
        print("2. python3 quick_system_check.py")
        print("3. 개별 컴포넌트 테스트")

if __name__ == "__main__":
    main()