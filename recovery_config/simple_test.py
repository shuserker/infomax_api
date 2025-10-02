#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from watchhamster_monitor import WatchHamsterMonitor
    print("✅ WatchHamsterMonitor 클래스 import 성공")
    
    config = {
        'process_check_interval': 60,
        'managed_processes': ['test_process'],
        'webhook_url': 'https://test.url'
    }
    
    monitor = WatchHamsterMonitor(config)
    print("✅ WatchHamsterMonitor 인스턴스 생성 성공")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()