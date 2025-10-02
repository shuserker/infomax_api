#!/usr/bin/env python3
"""
Isolated Test - 완전 격리된 테스트
"""

import os

def test_files_only():
    """파일 존재만 테스트"""
    print("=== Isolated File Test ===")
    
    current_dir = os.path.dirname(__file__)
    
    files_to_check = [
        "gui_components/log_viewer.py",
        "gui_components/notification_center.py", 
        "gui_components/system_tray.py",
        "gui_components/config_manager.py"
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - 없음")
    
    print("테스트 완료")

if __name__ == "__main__":
    test_files_only()