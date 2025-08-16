#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워치햄스터 런처 - 메뉴 선택 시스템
POSCO 워치햄스터 프로젝트 통합 실행 메뉴
"""

import os
import sys
import subprocess
import time
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
watchhamster_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if watchhamster_root not in sys.path:
    sys.path.insert(0, watchhamster_root)

class WatchhamsterLauncher:
    """워치햄스터 런처 메인 클래스"""
    
    def __init__(self):
        self.project_root = project_root
        self.watchhamster_root = watchhamster_root
        self.scripts_dir = current_dir
        self.posco_scripts_dir = os.path.join(watchhamster_root, 'Posco_News_Mini_Final', 'scripts')
        
    def clear_screen(self):
        """화면 지우기"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """헤더 출력"""
        print("=" * 60)
        print("🎯🛡️ POSCO 워치햄스터 프로젝트 런처")
        print("=" * 60)
        print(f"📅 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 프로젝트 위치: {self.watchhamster_root}")
        print("=" * 60)
    
    def print_main_menu(self):
        """메인 메뉴 출력"""
        print("\n🚀 메인 메뉴")
        print("-" * 40)
        print("[1] 📰 POSCO 뉴스 모니터링 시작")
        print("[2] 🛡️ 워치햄스터 모니터링 시작")
        print("[3] 📊 시스템 상태 확인")
        print("[4] 🧪 테스트 실행")
        print("[5] 🔧 관리 도구")
        print("[6] 📋 도움말 및 가이드")
        print("[0] 🚪 종료")
        print("-" * 40)
    
    def print_test_menu(self):
        """테스트 메뉴 출력"""
        print("\n🧪 테스트 메뉴")
        print("-" * 40)
        print("[1] 🔗 워치햄스터-포스코 연동 테스트")
        print("[2] 📡 웹훅 전송 테스트")
        print("[3] 🤖 AI 분석 엔진 테스트")
        print("[4] 📊 비즈니스 데이 비교 테스트")
        print("[5] 🏗️ 전체 시스템 통합 테스트")
        print("[6] 📦 모듈 기능 테스트")
        print("[0] ⬅️ 메인 메뉴로 돌아가기")
        print("-" * 40)
    
    def print_management_menu(self):
        """관리 도구 메뉴 출력"""
        print("\n🔧 관리 도구 메뉴")
        print("-" * 40)
        print("[1] 🔍 시스템 안정성 검증")
        print("[2] 📋 최종 검증 보고서")
        print("[3] 🗂️ 파일 구조 최적화")
        print("[4] 🏛️ 레거시 복원 도구")
        print("[5] 🔄 환경 설정 재로드")
        print("[0] ⬅️ 메인 메뉴로 돌아가기")
        print("-" * 40)
    
    def run_python_script(self, script_path, description="스크립트"):
        """Python 스크립트 실행"""
        print(f"\n🚀 {description} 실행 중...")
        print(f"📁 실행 파일: {script_path}")
        print("-" * 50)
        
        try:
            if os.path.exists(script_path):
                result = subprocess.run([sys.executable, script_path], 
                                      capture_output=False, text=True)
                print("-" * 50)
                if result.returncode == 0:
                    print(f"✅ {description} 실행 완료")
                else:
                    print(f"⚠️ {description} 실행 완료 (종료 코드: {result.returncode})")
            else:
                print(f"❌ 파일을 찾을 수 없습니다: {script_path}")
        except Exception as e:
            print(f"❌ 실행 오류: {e}")
        
        input("\n📝 아무 키나 누르면 메뉴로 돌아갑니다...")
    
    def run_python_module(self, module_path, description="모듈"):
        """Python 모듈 실행"""
        print(f"\n🚀 {description} 실행 중...")
        print(f"📦 실행 모듈: {module_path}")
        print("-" * 50)
        
        try:
            result = subprocess.run([sys.executable, '-m', module_path], 
                                  capture_output=False, text=True, 
                                  cwd=self.project_root)
            print("-" * 50)
            if result.returncode == 0:
                print(f"✅ {description} 실행 완료")
            else:
                print(f"⚠️ {description} 실행 완료 (종료 코드: {result.returncode})")
        except Exception as e:
            print(f"❌ 실행 오류: {e}")
        
        input("\n📝 아무 키나 누르면 메뉴로 돌아갑니다...")
    
    def handle_posco_news_monitoring(self):
        """포스코 뉴스 모니터링 시작"""
        system_test_path = os.path.join(self.posco_scripts_dir, 'system_test.py')
        self.run_python_script(system_test_path, "POSCO 뉴스 모니터링 시스템")
    
    def handle_watchhamster_monitoring(self):
        """워치햄스터 모니터링 시작"""
        start_monitoring_path = os.path.join(self.scripts_dir, 'start_monitoring.py')
        self.run_python_script(start_monitoring_path, "워치햄스터 모니터링 서비스")
    
    def handle_system_status(self):
        """시스템 상태 확인"""
        print("\n📊 시스템 상태 확인 중...")
        print("-" * 50)
        
        # 핵심 파일들 존재 확인
        critical_files = [
            ('워치햄스터 모니터', os.path.join(self.watchhamster_root, 'core', 'watchhamster_monitor.py')),
            ('Git 모니터', os.path.join(self.watchhamster_root, 'core', 'git_monitor.py')),
            ('포스코 환경 설정', os.path.join(self.watchhamster_root, 'Posco_News_Mini_Final', 'core', 'environment_setup.py')),
            ('웹훅 전송자', os.path.join(self.watchhamster_root, 'Posco_News_Mini_Final', 'core', 'webhook_sender.py')),
            ('시스템 테스트', os.path.join(self.posco_scripts_dir, 'system_test.py'))
        ]
        
        all_ok = True
        for name, path in critical_files:
            if os.path.exists(path):
                print(f"✅ {name}: 정상")
            else:
                print(f"❌ {name}: 누락 ({path})")
                all_ok = False
        
        print("-" * 50)
        if all_ok:
            print("🎯 전체 시스템 상태: 정상")
        else:
            print("⚠️ 전체 시스템 상태: 일부 파일 누락")
        
        # 프로세스 확인
        print("\n🔍 실행 중인 프로세스 확인...")
        try:
            import psutil
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('watchhamster' in str(cmd).lower() or 'posco' in str(cmd).lower() for cmd in cmdline):
                            python_processes.append(f"PID {proc.info['pid']}: {' '.join(cmdline)}")
                except:
                    continue
            
            if python_processes:
                print("🟢 실행 중인 관련 프로세스:")
                for proc in python_processes:
                    print(f"  • {proc}")
            else:
                print("🔴 실행 중인 관련 프로세스 없음")
        except ImportError:
            print("⚠️ psutil 모듈이 없어 프로세스 확인 불가")
        
        input("\n📝 아무 키나 누르면 메뉴로 돌아갑니다...")
    
    def handle_test_menu(self):
        """테스트 메뉴 처리"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_test_menu()
            
            try:
                choice = input("\n선택하세요 (0-6): ").strip()
                
                if choice == '1':
                    integration_test_path = os.path.join(self.scripts_dir, 'watchhamster_posco_integration_test.py')
                    self.run_python_script(integration_test_path, "워치햄스터-포스코 연동 테스트")
                
                elif choice == '2':
                    webhook_test_path = os.path.join(self.watchhamster_root, 'Posco_News_Mini_Final', 'core', 'webhook_sender.py')
                    if os.path.exists(webhook_test_path):
                        print("\n📡 웹훅 테스트 실행 중...")
                        print("💡 웹훅 전송자 모듈을 테스트 모드로 실행합니다.")
                        self.run_python_script(webhook_test_path, "웹훅 전송 테스트")
                    else:
                        print("❌ 웹훅 전송자 파일을 찾을 수 없습니다.")
                        input("📝 아무 키나 누르세요...")
                
                elif choice == '3':
                    ai_engine_path = os.path.join(self.watchhamster_root, 'core', 'ai_analysis_engine.py')
                    self.run_python_script(ai_engine_path, "AI 분석 엔진 테스트")
                
                elif choice == '4':
                    business_day_path = os.path.join(self.watchhamster_root, 'core', 'business_day_comparison_engine.py')
                    self.run_python_script(business_day_path, "비즈니스 데이 비교 테스트")
                
                elif choice == '5':
                    system_test_path = os.path.join(self.posco_scripts_dir, 'system_test.py')
                    self.run_python_script(system_test_path, "전체 시스템 통합 테스트")
                
                elif choice == '6':
                    module_test_path = os.path.join(self.posco_scripts_dir, 'test_posco_modules.py')
                    self.run_python_script(module_test_path, "모듈 기능 테스트")
                
                elif choice == '0':
                    break
                
                else:
                    print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n🛑 사용자에 의해 중단됨")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                input("📝 아무 키나 누르세요...")
    
    def handle_management_menu(self):
        """관리 도구 메뉴 처리"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_management_menu()
            
            try:
                choice = input("\n선택하세요 (0-5): ").strip()
                
                if choice == '1':
                    stability_test_path = os.path.join(self.project_root, 'final_stability_verification.py')
                    self.run_python_script(stability_test_path, "시스템 안정성 검증")
                
                elif choice == '2':
                    verification_test_path = os.path.join(self.project_root, 'final_verification_system.py')
                    self.run_python_script(verification_test_path, "최종 검증 보고서")
                
                elif choice == '3':
                    optimizer_path = os.path.join(self.project_root, 'file_structure_optimizer.py')
                    if os.path.exists(optimizer_path):
                        self.run_python_script(optimizer_path, "파일 구조 최적화")
                    else:
                        print("❌ 파일 구조 최적화 도구를 찾을 수 없습니다.")
                        input("📝 아무 키나 누르세요...")
                
                elif choice == '4':
                    recovery_path = os.path.join(self.project_root, 'recovery_config', 'apply_full_restoration.py')
                    if os.path.exists(recovery_path):
                        self.run_python_script(recovery_path, "레거시 복원 도구")
                    else:
                        print("❌ 레거시 복원 도구를 찾을 수 없습니다.")
                        input("📝 아무 키나 누르세요...")
                
                elif choice == '5':
                    env_setup_path = os.path.join(self.watchhamster_root, 'Posco_News_Mini_Final', 'core', 'environment_setup.py')
                    self.run_python_script(env_setup_path, "환경 설정 재로드")
                
                elif choice == '0':
                    break
                
                else:
                    print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n🛑 사용자에 의해 중단됨")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                input("📝 아무 키나 누르세요...")
    
    def show_help_and_guides(self):
        """도움말 및 가이드 표시"""
        print("\n📋 도움말 및 가이드")
        print("-" * 50)
        
        guides = [
            ("워치햄스터 가이드", os.path.join(self.watchhamster_root, 'docs', 'WATCHHAMSTER_GUIDE.md')),
            ("포스코 모니터링 가이드", os.path.join(self.watchhamster_root, 'Posco_News_Mini_Final', 'docs', 'MONITORING_GUIDE.md')),
            ("빠른 참조 가이드", os.path.join(self.watchhamster_root, 'Posco_News_Mini_Final', 'docs', 'QUICK_CHEAT_SHEET.md'))
        ]
        
        for name, path in guides:
            if os.path.exists(path):
                print(f"✅ {name}: {path}")
            else:
                print(f"❌ {name}: 파일 없음")
        
        print("\n🎯 주요 실행 명령어:")
        print("  • 워치햄스터 모니터링: python3 -m Monitoring.WatchHamster_Project.scripts.start_monitoring")
        print("  • 포스코 뉴스 테스트: python3 -m Monitoring.WatchHamster_Project.Posco_News_Mini_Final.scripts.system_test")
        print("  • 연동 테스트: python3 -m Monitoring.WatchHamster_Project.scripts.watchhamster_posco_integration_test")
        
        print("\n📁 주요 폴더 구조:")
        print("  • 워치햄스터 공통 모듈: Monitoring/WatchHamster_Project/core/")
        print("  • 포스코 전용 모듈: Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/")
        print("  • 실행 스크립트: Monitoring/WatchHamster_Project/scripts/")
        print("  • 레거시 보존: recovery_config/")
        
        input("\n📝 아무 키나 누르면 메뉴로 돌아갑니다...")
    
    def run(self):
        """메인 실행 루프"""
        while True:
            try:
                self.clear_screen()
                self.print_header()
                self.print_main_menu()
                
                choice = input("\n선택하세요 (0-6): ").strip()
                
                if choice == '1':
                    self.handle_posco_news_monitoring()
                
                elif choice == '2':
                    self.handle_watchhamster_monitoring()
                
                elif choice == '3':
                    self.handle_system_status()
                
                elif choice == '4':
                    self.handle_test_menu()
                
                elif choice == '5':
                    self.handle_management_menu()
                
                elif choice == '6':
                    self.show_help_and_guides()
                
                elif choice == '0':
                    print("\n👋 워치햄스터 런처를 종료합니다.")
                    print("🎯 POSCO 시스템 모니터링을 계속 유지하세요!")
                    break
                
                else:
                    print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n🛑 사용자에 의해 종료됨")
                break
            except Exception as e:
                print(f"\n❌ 예상치 못한 오류 발생: {e}")
                input("📝 아무 키나 누르면 계속합니다...")

def main():
    """메인 함수"""
    launcher = WatchhamsterLauncher()
    launcher.run()

if __name__ == "__main__":
    main()