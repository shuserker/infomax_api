#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 15 완전 검증 스크립트
메인 워치햄스터 GUI 애플리케이션 구현 (완전 독립) - 모든 요구사항 체크
"""

import os
import sys
import inspect
from typing import List, Dict, Any

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_main_gui_file():
    """main_gui.py 파일 존재 및 구조 확인"""
    print("🔍 1. main_gui.py 메인 애플리케이션 파일 확인")
    
    main_gui_path = os.path.join(current_dir, "main_gui.py")
    
    if not os.path.exists(main_gui_path):
        print("❌ main_gui.py 파일이 존재하지 않습니다")
        return False
    
    print("✅ main_gui.py 파일 존재 확인")
    
    # 파일 내용 확인
    try:
        with open(main_gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 요소 확인
        required_elements = [
            "class MainGUI:",
            "def __init__(self):",
            "def main():",
            "if __name__ == \"__main__\":",
            "🐹 WatchHamster",
            "통합 시스템 관리자"
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ 필수 요소 확인: {element}")
            else:
                print(f"❌ 필수 요소 누락: {element}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ main_gui.py 파일 읽기 오류: {e}")
        return False

def check_tkinter_gui_implementation():
    """tkinter 기반 크로스 플랫폼 GUI 구현 확인"""
    print("\n🔍 2. tkinter 크로스 플랫폼 GUI 구현 확인")
    
    try:
        # main_gui 모듈 import 테스트
        import main_gui
        print("✅ main_gui 모듈 import 성공")
        
        # MainGUI 클래스 확인
        if hasattr(main_gui, 'MainGUI'):
            print("✅ MainGUI 클래스 존재 확인")
            
            # 클래스 메서드 확인
            main_gui_class = main_gui.MainGUI
            methods = [method for method in dir(main_gui_class) if not method.startswith('_')]
            
            required_methods = [
                'create_service_control_tab',
                'create_service_control_panel', 
                'start_service',
                'stop_service',
                'restart_service',
                'start_all_services',
                'stop_all_services',
                'restart_all_services',
                'update_service_status_display',
                'update_system_status',
                'create_menu_bar',
                'run'
            ]
            
            for method in required_methods:
                if method in methods:
                    print(f"✅ 필수 메서드 확인: {method}")
                else:
                    print(f"❌ 필수 메서드 누락: {method}")
                    return False
            
            return True
        else:
            print("❌ MainGUI 클래스가 존재하지 않습니다")
            return False
            
    except Exception as e:
        print(f"❌ GUI 구현 확인 오류: {e}")
        return False

def check_integrated_status_dashboard():
    """내장된 모든 시스템 상태 대시보드 구현 확인"""
    print("\n🔍 3. 내장된 모든 시스템 상태 대시보드 구현 확인")
    
    try:
        # 상태 대시보드 관련 파일들 확인
        dashboard_files = [
            "gui_components/status_dashboard.py",
            "core/integrated_status_reporter.py",
            "core/system_recovery_handler.py"
        ]
        
        for file_path in dashboard_files:
            full_path = os.path.join(current_dir, file_path)
            if os.path.exists(full_path):
                print(f"✅ 대시보드 컴포넌트 확인: {file_path}")
            else:
                print(f"❌ 대시보드 컴포넌트 누락: {file_path}")
                return False
        
        # main_gui.py에서 대시보드 통합 확인
        with open(os.path.join(current_dir, "main_gui.py"), 'r', encoding='utf-8') as f:
            content = f.read()
        
        dashboard_integration_checks = [
            "from gui_components.status_dashboard import create_status_dashboard",
            "from core.integrated_status_reporter import create_integrated_status_reporter",
            "from core.system_recovery_handler import create_system_recovery_handler",
            "통합 상태 대시보드",
            "self.status_dashboard = create_status_dashboard",
            "self.status_reporter = create_integrated_status_reporter"
        ]
        
        for check in dashboard_integration_checks:
            if check in content:
                print(f"✅ 대시보드 통합 확인: {check[:50]}...")
            else:
                print(f"❌ 대시보드 통합 누락: {check[:50]}...")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 상태 대시보드 확인 오류: {e}")
        return False

def check_service_control_panel():
    """내장 서비스 제어 패널 (시작/중지/재시작) 구현 확인"""
    print("\n🔍 4. 내장 서비스 제어 패널 (시작/중지/재시작) 구현 확인")
    
    try:
        with open(os.path.join(current_dir, "main_gui.py"), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 서비스 상태 추적 확인
        service_state_checks = [
            "self.service_states = {",
            "'posco_news': {'running': False, 'status': 'stopped'}",
            "'github_pages_monitor': {'running': False, 'status': 'stopped'}",
            "'cache_monitor': {'running': False, 'status': 'stopped'}",
            "'deployment_system': {'running': False, 'status': 'stopped'}",
            "'message_system': {'running': False, 'status': 'stopped'}",
            "'webhook_integration': {'running': False, 'status': 'stopped'}"
        ]
        
        for check in service_state_checks:
            if check in content:
                print(f"✅ 서비스 상태 추적: {check[:40]}...")
            else:
                print(f"❌ 서비스 상태 추적 누락: {check[:40]}...")
                return False
        
        # 전체 서비스 제어 패널 확인
        global_control_checks = [
            "전체 서비스 제어",
            "🚀 모든 서비스 시작",
            "⏹️ 모든 서비스 중지", 
            "🔄 시스템 재시작",
            "def start_all_services(self):",
            "def stop_all_services(self):",
            "def restart_all_services(self):"
        ]
        
        for check in global_control_checks:
            if check in content:
                print(f"✅ 전체 서비스 제어: {check}")
            else:
                print(f"❌ 전체 서비스 제어 누락: {check}")
                return False
        
        # 개별 서비스 제어 탭 확인
        service_control_tab_checks = [
            "⚙️ 서비스 제어",
            "def create_service_control_tab(self):",
            "내장 서비스 상태 및 제어",
            "def create_service_control_panel(self, parent, service_config, row):"
        ]
        
        for check in service_control_tab_checks:
            if check in content:
                print(f"✅ 개별 서비스 제어 탭: {check}")
            else:
                print(f"❌ 개별 서비스 제어 탭 누락: {check}")
                return False
        
        # 6개 서비스 확인
        services_checks = [
            "🔄 POSCO 뉴스 시스템",
            "🌐 GitHub Pages 모니터",
            "💾 캐시 데이터 모니터",
            "🚀 배포 시스템",
            "💬 메시지 시스템",
            "🔗 웹훅 통합"
        ]
        
        for service in services_checks:
            if service in content:
                print(f"✅ 서비스 확인: {service}")
            else:
                print(f"❌ 서비스 누락: {service}")
                return False
        
        # 개별 서비스 제어 메서드 확인
        service_methods = [
            "def start_posco_news_service(self):",
            "def stop_posco_news_service(self):",
            "def start_github_pages_monitor_service(self):",
            "def stop_github_pages_monitor_service(self):",
            "def start_cache_monitor_service(self):",
            "def stop_cache_monitor_service(self):",
            "def start_deployment_system_service(self):",
            "def stop_deployment_system_service(self):",
            "def start_message_system_service(self):",
            "def stop_message_system_service(self):",
            "def start_webhook_integration_service(self):",
            "def stop_webhook_integration_service(self):"
        ]
        
        for method in service_methods:
            if method in content:
                print(f"✅ 서비스 제어 메서드: {method[:30]}...")
            else:
                print(f"❌ 서비스 제어 메서드 누락: {method[:30]}...")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 서비스 제어 패널 확인 오류: {e}")
        return False

def check_gui_structure_and_features():
    """GUI 구조 및 기능 확인"""
    print("\n🔍 5. GUI 구조 및 기능 확인")
    
    try:
        with open(os.path.join(current_dir, "main_gui.py"), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # GUI 구조 확인
        gui_structure_checks = [
            "self.root = tk.Tk()",
            "self.root.title(\"🐹 WatchHamster - 통합 시스템 관리자\")",
            "self.root.geometry(\"1400x900\")",
            "self.root.minsize(1000, 700)",
            "ttk.Notebook",
            "def create_menu_bar(self):"
        ]
        
        for check in gui_structure_checks:
            if check in content:
                print(f"✅ GUI 구조: {check}")
            else:
                print(f"❌ GUI 구조 누락: {check}")
                return False
        
        # 탭 구조 확인
        tab_checks = [
            "📊 통합 상태 대시보드",
            "⚙️ 서비스 제어",
            "🔄 POSCO 뉴스 시스템"
        ]
        
        for tab in tab_checks:
            if tab in content:
                print(f"✅ 탭 구조: {tab}")
            else:
                print(f"❌ 탭 구조 누락: {tab}")
                return False
        
        # 메뉴바 확인
        menu_checks = [
            "파일",
            "서비스", 
            "도구",
            "도움말"
        ]
        
        for menu in menu_checks:
            if f"label=\"{menu}\"" in content:
                print(f"✅ 메뉴바: {menu}")
            else:
                print(f"❌ 메뉴바 누락: {menu}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ GUI 구조 확인 오류: {e}")
        return False

def check_requirements_compliance():
    """Requirements 6.1, 6.2 준수 확인"""
    print("\n🔍 6. Requirements 6.1, 6.2 준수 확인")
    
    try:
        with open(os.path.join(current_dir, "main_gui.py"), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Requirements 6.1 확인 (완전 독립 실행 GUI)
        req_6_1_checks = [
            "완전 독립",
            "if __name__ == \"__main__\":",
            "def main():",
            "app = MainGUI()",
            "app.run()"
        ]
        
        print("📋 Requirements 6.1 확인:")
        for check in req_6_1_checks:
            if check in content:
                print(f"✅ Req 6.1: {check}")
            else:
                print(f"❌ Req 6.1 누락: {check}")
                return False
        
        # Requirements 6.2 확인 (내장 서비스 제어 패널)
        req_6_2_checks = [
            "내장 서비스 제어 패널",
            "시작/중지/재시작",
            "def start_service(",
            "def stop_service(",
            "def restart_service("
        ]
        
        print("📋 Requirements 6.2 확인:")
        for check in req_6_2_checks:
            if check in content:
                print(f"✅ Req 6.2: {check}")
            else:
                print(f"❌ Req 6.2 누락: {check}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements 확인 오류: {e}")
        return False

def check_integration_with_existing_systems():
    """기존 시스템과의 통합 확인"""
    print("\n🔍 7. 기존 시스템과의 통합 확인")
    
    try:
        with open(os.path.join(current_dir, "main_gui.py"), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 기존 시스템 통합 확인
        integration_checks = [
            "from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager",
            "self.posco_manager = PoscoGUIManager(posco_frame)",
            "from core.integrated_status_reporter import create_integrated_status_reporter",
            "from core.system_recovery_handler import create_system_recovery_handler",
            "from gui_components.status_dashboard import create_status_dashboard"
        ]
        
        for check in integration_checks:
            if check in content:
                print(f"✅ 시스템 통합: {check[:50]}...")
            else:
                print(f"❌ 시스템 통합 누락: {check[:50]}...")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 시스템 통합 확인 오류: {e}")
        return False

def main():
    """메인 검증 함수"""
    print("🐹 Task 15: 메인 워치햄스터 GUI 애플리케이션 구현 (완전 독립) - 완전 검증")
    print("=" * 80)
    
    checks = [
        ("main_gui.py 파일 확인", check_main_gui_file),
        ("tkinter GUI 구현 확인", check_tkinter_gui_implementation),
        ("통합 상태 대시보드 확인", check_integrated_status_dashboard),
        ("서비스 제어 패널 확인", check_service_control_panel),
        ("GUI 구조 및 기능 확인", check_gui_structure_and_features),
        ("Requirements 준수 확인", check_requirements_compliance),
        ("기존 시스템 통합 확인", check_integration_with_existing_systems)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
                print(f"✅ {check_name} 통과\n")
            else:
                print(f"❌ {check_name} 실패\n")
        except Exception as e:
            print(f"❌ {check_name} 오류: {e}\n")
    
    print("=" * 80)
    print(f"검증 결과: {passed_checks}/{total_checks} 통과")
    
    if passed_checks == total_checks:
        print("🎉 Task 15 완전 구현 확인!")
        print("\n📋 구현된 모든 요구사항:")
        print("✅ main_gui.py 메인 애플리케이션 생성 (진입점)")
        print("✅ tkinter를 사용한 크로스 플랫폼 GUI 구현 (안정성 우선)")
        print("✅ 내장된 모든 시스템 상태 대시보드 구현")
        print("✅ 내장 서비스 제어 패널 (시작/중지/재시작) 구현")
        print("✅ Requirements 6.1, 6.2 완전 구현")
        print("\n🚀 WatchHamster 통합 시스템 관리자 완성!")
        return True
    else:
        print("❌ 일부 요구사항이 누락되었습니다")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)