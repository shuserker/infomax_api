#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐹 WatchHamster v4.0 통합 모니터링 시스템 터미널 실행기
========================================================
크로스 플랫폼 지원 (Windows, macOS, Linux)
POSCO 뉴스 모니터링 + InfoMax API 테스트 플랫폼 통합
"""

import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path

# ANSI 색상 코드
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color):
    """색상이 있는 텍스트 출력"""
    print(f"{color}{text}{Colors.END}")

def print_logo():
    """WatchHamster 로고 및 시스템 정보 출력"""
    print_colored("=" * 80, Colors.CYAN)
    print_colored("🐹 WatchHamster v4.0 통합 모니터링 시스템 완전체", Colors.WHITE + Colors.BOLD)
    print_colored("=" * 80, Colors.CYAN)
    print_colored("📈 POSCO 뉴스 모니터링 시스템", Colors.GREEN)
    print_colored("📊 InfoMax API 테스트 플랫폼 (58개+ API 지원)", Colors.BLUE)
    print_colored("🤖 28개 자동갱신 로직 & 스마트 스케줄링", Colors.YELLOW)
    print_colored("🌐 웹훅 통합 & 실시간 알림 시스템", Colors.PURPLE)
    print_colored("⚙️  백업, 수리, 품질관리 자동화 도구", Colors.CYAN)
    print_colored("=" * 80, Colors.CYAN)
    print()

def check_system():
    """시스템 환경 체크"""
    print_colored("🔍 시스템 환경 체크 중...", Colors.YELLOW)
    
    # 플랫폼 확인
    system = platform.system()
    print_colored(f"💻 운영체제: {system} {platform.release()}", Colors.BLUE)
    print_colored(f"📍 WatchHamster 본부: {os.getcwd()}", Colors.BLUE)
    
    # Node.js 확인
    try:
        node_version = subprocess.check_output(['node', '--version'], 
                                              stderr=subprocess.DEVNULL, 
                                              text=True).strip()
        print_colored(f"✅ Node.js: {node_version}", Colors.GREEN)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("❌ Node.js가 설치되지 않았습니다!", Colors.RED)
        print_colored("   https://nodejs.org 에서 설치해주세요.", Colors.YELLOW)
        sys.exit(1)
    
    # npm 확인
    try:
        npm_version = subprocess.check_output(['npm', '--version'], 
                                            stderr=subprocess.DEVNULL, 
                                            text=True).strip()
        print_colored(f"✅ npm: v{npm_version}", Colors.GREEN)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("❌ npm이 설치되지 않았습니다!", Colors.RED)
        sys.exit(1)
    
    # Python 확인 (WatchHamster 백엔드용)
    try:
        python_version = subprocess.check_output(['python3', '--version'], 
                                               stderr=subprocess.DEVNULL, 
                                               text=True).strip()
        print_colored(f"✅ Python: {python_version}", Colors.GREEN)
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            python_version = subprocess.check_output(['python', '--version'], 
                                                   stderr=subprocess.DEVNULL, 
                                                   text=True).strip()
            print_colored(f"✅ Python: {python_version}", Colors.GREEN)
        except:
            print_colored("⚠️  Python이 설치되지 않았습니다 (백엔드 기능 제한)", Colors.YELLOW)
    
    # package.json 확인
    if not Path('package.json').exists():
        print_colored("❌ package.json을 찾을 수 없습니다!", Colors.RED)
        print_colored("   올바른 WatchHamster 프로젝트 디렉토리에서 실행하세요.", Colors.YELLOW)
        sys.exit(1)
    
    print_colored("✅ WatchHamster 시스템 구조 정상", Colors.GREEN)
    print()

def run_command(command, description="명령 실행", cwd=None):
    """명령어 실행"""
    print_colored(f"🔄 {description}...", Colors.YELLOW)
    try:
        if cwd:
            result = subprocess.run(command, shell=True, check=True, cwd=cwd,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print_colored(f"✅ {description} 완료!", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ {description} 실패!", Colors.RED)
        print_colored(f"오류: {e.stderr}", Colors.RED)
        return False

def show_menu():
    """메뉴 표시"""
    print_colored("🎯 WatchHamster v4.0 실행 옵션:", Colors.WHITE + Colors.BOLD)
    print_colored("[1] 🚀 WatchHamster 풀스택 실행 (의존성 자동 설치 + 전체 시스템 시작)", Colors.CYAN)
    print_colored("[2] 📦 의존성만 설치", Colors.CYAN)
    print_colored("[3] 🌐 프론트엔드만 시작 (InfoMax API 테스트 플랫폼)", Colors.CYAN)
    print_colored("[4] 🐍 백엔드만 시작 (웹훅 & 모니터링 서비스)", Colors.CYAN)
    print_colored("[5] 🏗️  빌드 및 프로덕션 프리뷰", Colors.CYAN)
    print_colored("[6] 🧹 시스템 초기화 (캐시 정리 + 재설치)", Colors.CYAN)
    print_colored("[7] 📋 WatchHamster 시스템 상태 체크", Colors.CYAN)
    print_colored("[8] 🌐 브라우저에서 열기", Colors.CYAN)
    print_colored("[9] ❌ 종료", Colors.CYAN)
    print()

def open_browser():
    """브라우저에서 URL 열기"""
    url = "http://localhost:1420/api-packages"
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", url])
        elif system == "Windows":
            subprocess.run(["start", url], shell=True)
        else:  # Linux
            subprocess.run(["xdg-open", url])
        
        print_colored(f"🌐 브라우저에서 {url} 을 열었습니다.", Colors.GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ 브라우저 열기 실패: {e}", Colors.RED)
        return False

def show_server_info():
    """서버 시작 정보 표시"""
    print_colored("=" * 80, Colors.CYAN)
    print_colored("🐹 WatchHamster v4.0 Control Center", Colors.WHITE + Colors.BOLD)
    print_colored("📈 POSCO 뉴스 모니터링: 활성화", Colors.GREEN)
    print_colored("📊 InfoMax API 플랫폼: http://localhost:1420/api-packages", Colors.BLUE)
    print_colored("🤖 자동갱신 시스템: 백그라운드 실행", Colors.YELLOW)
    print_colored("🌐 웹훅 통합: 준비완료", Colors.PURPLE)
    print_colored("=" * 80, Colors.CYAN)
    print_colored("🎯 주요 기능:", Colors.WHITE)
    print_colored("  • API 테스트: 58개+ 금융 API 완전 지원", Colors.WHITE)
    print_colored("  • 자동갱신: 28개 스마트 로직 & 스케줄링", Colors.WHITE)
    print_colored("  • 실시간 모니터링: POSCO 뉴스 변경사항 추적", Colors.WHITE)
    print_colored("  • 웹훅 알림: Dooray 통합 실시간 알림", Colors.WHITE)
    print_colored("=" * 80, Colors.CYAN)
    print_colored("시스템 종료: Ctrl+C", Colors.YELLOW)
    print()

def full_stack_start():
    """풀스택 실행 모드"""
    print_colored("🚀 WatchHamster v4.0 풀스택 실행 모드", Colors.PURPLE)
    print()
    
    # 의존성 설치
    if not run_command("npm install", "의존성 설치"):
        return
    
    print()
    print_colored("🌐 WatchHamster 통합 시스템 시작 중...", Colors.BLUE)
    show_server_info()
    
    # 서버 시작 (blocking)
    try:
        subprocess.run("npm run dev", shell=True, check=True)
    except KeyboardInterrupt:
        print_colored("\n👋 WatchHamster 시스템을 종료합니다.", Colors.YELLOW)
    except subprocess.CalledProcessError:
        print_colored("❌ 시스템 시작 실패!", Colors.RED)

def install_only():
    """의존성만 설치"""
    if run_command("npm install", "WatchHamster 의존성 설치"):
        print_colored("💡 이제 'npm run dev' 명령으로 WatchHamster를 시작할 수 있습니다.", Colors.BLUE)

def frontend_only():
    """프론트엔드만 시작"""
    print_colored("🌐 WatchHamster 프론트엔드 시작 중...", Colors.BLUE)
    print_colored("=" * 80, Colors.CYAN)
    print_colored("📍 InfoMax API 테스트 플랫폼: http://localhost:1420/api-packages", Colors.GREEN)
    print_colored("🐹 WatchHamster v4.0 - API 테스트 모듈", Colors.WHITE)
    print_colored("=" * 80, Colors.CYAN)
    print_colored("시스템 종료: Ctrl+C", Colors.YELLOW)
    print()
    
    try:
        subprocess.run("npm run dev", shell=True, check=True)
    except KeyboardInterrupt:
        print_colored("\n👋 프론트엔드를 종료합니다.", Colors.YELLOW)
    except subprocess.CalledProcessError:
        print_colored("❌ 프론트엔드 시작 실패!", Colors.RED)

def backend_only():
    """백엔드만 시작"""
    print_colored("🐍 WatchHamster 백엔드 서비스 시작 중...", Colors.GREEN)
    
    backend_path = Path('python-backend')
    if backend_path.exists():
        # Python 의존성 설치
        requirements_path = backend_path / 'requirements.txt'
        if requirements_path.exists():
            print_colored("Python 의존성 설치 중...", Colors.YELLOW)
            python_cmd = 'python3' if shutil.which('python3') else 'python'
            run_command(f"{python_cmd} -m pip install -r requirements.txt", 
                       "Python 의존성 설치", cwd=str(backend_path))
        
        print_colored("=" * 80, Colors.CYAN)
        print_colored("🐹 WatchHamster 백엔드 서비스 활성화", Colors.WHITE + Colors.BOLD)
        print_colored("📈 POSCO 뉴스 모니터링 활성화", Colors.GREEN)
        print_colored("🌐 웹훅 서비스 대기 중", Colors.PURPLE)
        print_colored("=" * 80, Colors.CYAN)
        
        try:
            python_cmd = 'python3' if shutil.which('python3') else 'python'
            subprocess.run(f"{python_cmd} -m api.webhook_manager", 
                         shell=True, check=True, cwd=str(backend_path))
        except KeyboardInterrupt:
            print_colored("\n👋 백엔드 서비스를 종료합니다.", Colors.YELLOW)
        except subprocess.CalledProcessError:
            print_colored("❌ 백엔드 시작 실패!", Colors.RED)
    else:
        print_colored("⚠️  백엔드 디렉토리를 찾을 수 없습니다.", Colors.YELLOW)
        print_colored("프론트엔드만 실행합니다...", Colors.BLUE)
        frontend_only()

def build_preview():
    """빌드 및 프리뷰"""
    if run_command("npm run build", "WatchHamster 시스템 빌드"):
        print()
        print_colored("🎭 프로덕션 프리뷰 서버 시작 중...", Colors.BLUE)
        try:
            subprocess.run("npm run preview", shell=True, check=True)
        except KeyboardInterrupt:
            print_colored("\n👋 프리뷰 서버를 종료합니다.", Colors.YELLOW)
        except subprocess.CalledProcessError:
            print_colored("❌ 프리뷰 서버 시작 실패!", Colors.RED)

def system_reset():
    """시스템 초기화"""
    print_colored("🧹 WatchHamster 시스템 초기화 중...", Colors.YELLOW)
    
    # node_modules 삭제
    node_modules = Path('node_modules')
    if node_modules.exists():
        shutil.rmtree(node_modules)
        print_colored("✅ node_modules 정리 완료", Colors.GREEN)
    
    # package-lock.json 삭제
    lock_file = Path('package-lock.json')
    if lock_file.exists():
        lock_file.unlink()
        print_colored("✅ package-lock.json 정리 완료", Colors.GREEN)
    
    # npm 캐시 정리
    run_command("npm cache clean --force", "npm 캐시 정리")
    
    # Python 캐시 정리
    for pycache in Path('.').rglob('__pycache__'):
        shutil.rmtree(pycache, ignore_errors=True)
    print_colored("✅ Python 캐시 정리 완료", Colors.GREEN)
    
    print()
    # 새로 설치
    if run_command("npm install", "WatchHamster 시스템 재설치"):
        print()
        start_server = input("🐹 WatchHamster를 시작하시겠습니까? (y/n): ").lower()
        if start_server in ['y', 'yes']:
            full_stack_start()

def system_status():
    """시스템 상태 체크"""
    print_colored("📋 WatchHamster v4.0 시스템 상태 체크", Colors.BLUE)
    print_colored("=" * 80, Colors.CYAN)
    
    # 프로젝트 구조 체크
    print_colored("📁 프로젝트 구조:", Colors.WHITE)
    
    checks = [
        ("package.json", "package.json"),
        ("src", "src/ (프론트엔드)"),
        ("python-backend", "python-backend/ (백엔드)"),
        ("core", "core/ (모니터링)"),
    ]
    
    for path, description in checks:
        if Path(path).exists():
            print_colored(f"✅ {description}", Colors.GREEN)
        else:
            print_colored(f"⚠️  {description}", Colors.YELLOW)
    
    print()
    print_colored("🔧 핵심 모듈:", Colors.WHITE)
    
    modules = [
        ("src/pages/ApiPackageManagement.tsx", "InfoMax API 테스트 모듈"),
        ("src/utils/parameterDefaultManager.ts", "자동갱신 시스템"),
        ("src/utils/apiCrawlingMapper.ts", "API 크롤링 매핑"),
    ]
    
    for path, description in modules:
        if Path(path).exists():
            print_colored(f"✅ {description}", Colors.GREEN)
        else:
            print_colored(f"❌ {description}", Colors.RED)
    
    print()
    print_colored("📊 통계:", Colors.WHITE)
    print_colored("• 지원 API: 58개+", Colors.BLUE)
    print_colored("• 자동갱신 로직: 28개", Colors.BLUE)
    
    print_colored("=" * 80, Colors.CYAN)

def main():
    """메인 함수"""
    try:
        # 로고 출력
        print_logo()
        
        # 시스템 체크
        check_system()
        
        # 메인 루프
        while True:
            show_menu()
            try:
                choice = input("선택 (1-9): ").strip()
            except KeyboardInterrupt:
                print_colored("\n👋 WatchHamster를 종료합니다.", Colors.YELLOW)
                sys.exit(0)
            
            if choice == '1':
                full_stack_start()
                break
            elif choice == '2':
                install_only()
                break
            elif choice == '3':
                frontend_only()
                break
            elif choice == '4':
                backend_only()
                break
            elif choice == '5':
                build_preview()
                break
            elif choice == '6':
                system_reset()
                break
            elif choice == '7':
                system_status()
                continue
            elif choice == '8':
                open_browser()
                continue
            elif choice == '9':
                print_colored("👋 WatchHamster를 종료합니다.", Colors.YELLOW)
                sys.exit(0)
            else:
                print_colored("❌ 잘못된 선택입니다. 1-9 사이의 숫자를 입력하세요.", Colors.RED)
                print()
                continue
        
        print()
        print_colored("🎉 WatchHamster v4.0 작업 완료!", Colors.GREEN)
        print_colored("🐹 최고의 모니터링 시스템과 함께하세요!", Colors.BLUE)
        print_colored("=" * 80, Colors.CYAN)
        
    except KeyboardInterrupt:
        print_colored("\n👋 WatchHamster를 종료합니다.", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_colored(f"❌ 예상치 못한 오류가 발생했습니다: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
