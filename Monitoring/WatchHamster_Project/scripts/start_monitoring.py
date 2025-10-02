#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워치햄스터 모니터 시작 스크립트

워치햄스터 모니터를 실행하여 실제 알림이 발송되도록 합니다.
"""

import os
import sys
import time
import threading
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # 3단계 상위 (프로젝트 루트)
watchhamster_root = os.path.dirname(current_dir)  # WatchHamster_Project 루트

# Python 경로에 프로젝트 루트와 워치햄스터 루트 추가
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if watchhamster_root not in sys.path:
    sys.path.insert(0, watchhamster_root)

# 현재 디렉토리도 추가 (로컬 모듈용)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # 절대 경로로 모듈 import
    from Monitoring.WatchHamster_Project.core.watchhamster_monitor import WatchHamsterMonitor
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.webhook_sender import WebhookSender, MessagePriority
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.environment_setup import EnvironmentSetup
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    print("💡 새로운 폴더 구조에서 모듈을 찾을 수 없습니다.")
    print("   - 워치햄스터 모듈: Monitoring/WatchHamster_Project/core/")
    print("   - 포스코 모듈: Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/")
    
    # 대안: 직접 경로로 모듈 로드 시도
    try:
        print("🔄 대안 방법으로 모듈 로드 시도 중...")
        
        # 워치햄스터 모니터 모듈 직접 로드
        watchhamster_monitor_path = os.path.join(watchhamster_root, 'core', 'watchhamster_monitor.py')
        webhook_sender_path = os.path.join(watchhamster_root, 'Posco_News_Mini_Final', 'core', 'webhook_sender.py')
        env_setup_path = os.path.join(watchhamster_root, 'Posco_News_Mini_Final', 'core', 'environment_setup.py')
        
        import importlib.util
        
        # WatchHamsterMonitor 로드
        spec = importlib.util.spec_from_file_location("watchhamster_monitor", watchhamster_monitor_path)
        watchhamster_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(watchhamster_module)
        WatchHamsterMonitor = watchhamster_module.WatchHamsterMonitor
        
        # WebhookSender 로드
        spec = importlib.util.spec_from_file_location("webhook_sender", webhook_sender_path)
        webhook_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(webhook_module)
        WebhookSender = webhook_module.WebhookSender
        MessagePriority = webhook_module.MessagePriority
        
        # EnvironmentSetup 로드
        spec = importlib.util.spec_from_file_location("environment_setup", env_setup_path)
        env_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(env_module)
        EnvironmentSetup = env_module.EnvironmentSetup
        
        print("✅ 대안 방법으로 모듈 로드 성공")
        
    except Exception as e2:
        print(f"❌ 대안 방법도 실패: {e2}")
        sys.exit(1)


class WatchhamsterService:
    """워치햄스터 서비스 관리자"""
    
    def __init__(self):
        """서비스 초기화"""
        self.start_time = datetime.now()
        
        # 환경 설정 로드
        try:
            env_setup = EnvironmentSetup()
            self.env_settings = env_setup.settings
        except:
            self.env_settings = {}
        
        # 웹훅 전송자 초기화
        self.webhook_sender = WebhookSender(test_mode=False)
        
        # 모니터링 설정
        self.process_check_interval = 300  # 5분
        self.git_check_interval = 3600     # 60분
        self.status_notification_interval = 7200  # 120분
        
        # 스케줄 작업 시간
        self.schedule_times = ["06:00", "06:10", "18:00", "18:10", "18:20"]
        self.hourly_schedule = "07-17시 매시간"
        
        # 워치햄스터 모니터 초기화 (설정 제공)
        try:
            monitor_config = {
                'process_check_interval': self.process_check_interval,
                'git_check_interval': self.git_check_interval,
                'status_notification_interval': self.status_notification_interval,
                'webhook_sender': self.webhook_sender,
                'managed_processes': [
                    'posco_main_notifier.py',
                    'realtime_news_monitor.py',
                    'system_test.py'
                ],
                'max_restart_attempts': 3,
                'restart_cooldown': 60,
                'webhook_url': self.env_settings.get('webhook_url', ''),
                'bot_profile_image': self.env_settings.get('bot_profile_image', '')
            }
            self.monitor = WatchHamsterMonitor(monitor_config)
        except Exception as e:
            print(f"⚠️ 워치햄스터 모니터 초기화 실패: {e}")
            print(f"🔧 기본 설정으로 계속 진행합니다.")
            self.monitor = None
        
        self.is_running = False
        self.monitor_thread = None
        
        # 초기화 완료 후 상태 대시보드 표시
        self.display_status_dashboard()
    
    def get_system_status(self):
        """시스템 상태 정보 수집"""
        try:
            import psutil
            
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            return {
                'cpu': cpu_percent,
                'memory': memory_percent,
                'disk': disk_percent
            }
        except ImportError:
            return {
                'cpu': 0.0,
                'memory': 0.0,
                'disk': 0.0
            }
        except Exception:
            return {
                'cpu': 0.0,
                'memory': 0.0,
                'disk': 0.0
            }
    
    def get_running_time(self):
        """실행 시간 계산"""
        running_time = datetime.now() - self.start_time
        hours = running_time.total_seconds() / 3600
        return round(hours, 1)
    
    def display_status_dashboard(self):
        """워치햄스터 상태 대시보드 표시"""
        print("\n" + "="*60)
        print("🐹 POSCO 모니터 워치햄스터 🛡️ 상태 알림")
        print("="*60)
        
        # 시간 정보
        print(f"📅 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 실행 시간: {self.get_running_time()}시간")
        
        # 모니터링 설정
        print(f"🔍 프로세스 감시: {self.process_check_interval//60}분 간격")
        print(f"🔄 Git 업데이트 체크: {self.git_check_interval//60}분 간격")
        print(f"📊 정기 상태 알림: {self.status_notification_interval//60}분 간격")
        
        # 스케줄 정보
        schedule_str = ", ".join(self.schedule_times)
        print(f"📅 스케줄 작업: {schedule_str}, {self.hourly_schedule}")
        
        # 자동 복구 기능
        print("🚀 자동 복구 기능 활성화")
        print()
        
        # 시스템 상태
        system_status = self.get_system_status()
        print("📊 시스템 상태:")
        print(f"🖥️ CPU: {system_status['cpu']:.1f}%")
        print(f"💾 메모리: {system_status['memory']:.1f}%")
        print(f"💿 디스크: {system_status['disk']:.1f}%")
        
        print("="*60)
        print("✅ 워치햄스터 모니터링 시스템 준비 완료")
        print("="*60)
    
    def update_status_dashboard(self):
        """상태 대시보드 업데이트 (주기적)"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_status_dashboard()
        
        # 추가 실시간 정보
        print(f"\n🔄 마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
        if self.is_running:
            print("🟢 모니터링 활성 상태")
        else:
            print("🔴 모니터링 비활성 상태")
    
    def send_startup_notification(self):
        """시작 알림 전송 (상세 상태 포함)"""
        try:
            # 시작 시에도 상세 상태 보고서 전송
            success = self.send_detailed_status_report()
            
            if success:
                print(f"✅ 워치햄스터 시작 알림 전송됨: {datetime.now().strftime('%H:%M:%S')}")
            else:
                print("⚠️ 워치햄스터 시작 알림 전송 실패")
                
        except Exception as e:
            print(f"❌ 시작 알림 전송 오류: {e}")
    
    def get_news_status_info(self):
        """뉴스 상태 정보 수집 (원래 로직 기반)"""
        try:
            # 포스코 뉴스 시스템 테스트 실행하여 현재 상태 확인
            import subprocess
            import json
            
            system_test_path = os.path.join(
                self.env_settings.get('project_root', '.'),
                'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final', 'scripts', 'system_test.py'
            )
            
            if os.path.exists(system_test_path):
                # 시스템 테스트 실행하여 뉴스 상태 확인
                result = subprocess.run([
                    sys.executable, system_test_path
                ], capture_output=True, text=True, timeout=30)
                
                # 결과에서 뉴스 상태 정보 추출
                if result.returncode == 0:
                    # 성공적으로 실행된 경우 - 뉴스 시스템 정상
                    return {
                        'status': '정상 작동',
                        'news_system_running': True,
                        'api_status': '정상',
                        'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    # 실행 실패 - 뉴스 시스템 문제
                    return {
                        'status': '시스템 점검 필요',
                        'news_system_running': False,
                        'api_status': '확인 필요',
                        'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'error': result.stderr[:200] if result.stderr else '알 수 없는 오류'
                    }
            else:
                return {
                    'status': '뉴스 시스템 파일 없음',
                    'news_system_running': False,
                    'api_status': '파일 없음',
                    'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': '뉴스 시스템 응답 없음',
                'news_system_running': False,
                'api_status': '타임아웃',
                'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                'status': '뉴스 상태 확인 오류',
                'news_system_running': False,
                'api_status': '오류',
                'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)[:200]
            }
    
    def send_detailed_status_report(self):
        """상세 상태 보고서 전송 (원래 로직 기반)"""
        try:
            # 시스템 상태 수집
            system_status = self.get_system_status()
            running_time = self.get_running_time()
            current_time = datetime.now()
            
            # 뉴스 상태 정보 수집 (원래 로직)
            news_status = self.get_news_status_info()
            
            # 상세 상태 메시지 생성 (원래 형태)
            status_message = f"""🐹 POSCO 모니터 워치햄스터 🛡️ 상태 알림

📅 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
⏱️ 실행 시간: {running_time}시간
🔍 프로세스 감시: {self.process_check_interval//60}분 간격
🔄 Git 업데이트 체크: {self.git_check_interval//60}분 간격
📊 정기 상태 알림: {self.status_notification_interval//60}분 간격
📅 스케줄 작업: {', '.join(self.schedule_times)}, {self.hourly_schedule}
🚀 자동 복구 기능 활성화

📊 시스템 상태:
🖥️ CPU: {system_status['cpu']:.1f}%
💾 메모리: {system_status['memory']:.1f}%
💿 디스크: {system_status['disk']:.1f}%

📰 뉴스 시스템 상태:
🔍 상태: {news_status['status']}
📡 API: {news_status['api_status']}
⏰ 마지막 확인: {news_status['last_check']}"""
            
            # 웹훅으로 전송
            message_id = self.webhook_sender.send_watchhamster_status(
                "정상 작동 중",
                {
                    "detailed_status": status_message,
                    "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "running_time": f"{running_time}시간",
                    "process_check": f"{self.process_check_interval//60}분 간격",
                    "git_check": f"{self.git_check_interval//60}분 간격",
                    "status_notification": f"{self.status_notification_interval//60}분 간격",
                    "schedule": f"{', '.join(self.schedule_times)}, {self.hourly_schedule}",
                    "auto_recovery": "활성화",
                    "cpu_usage": f"{system_status['cpu']:.1f}%",
                    "memory_usage": f"{system_status['memory']:.1f}%",
                    "disk_usage": f"{system_status['disk']:.1f}%"
                }
            )
            
            if message_id:
                print(f"📊 상세 상태 보고서 전송됨: {message_id}")
                return True
            else:
                print("⚠️ 상세 상태 보고서 전송 실패")
                return False
                
        except Exception as e:
            print(f"❌ 상세 상태 보고서 전송 오류: {e}")
            return False
    
    def send_periodic_status(self):
        """주기적 상태 알림 (120분마다 상세 보고서)"""
        while self.is_running:
            try:
                time.sleep(self.status_notification_interval)  # 120분 대기
                
                if not self.is_running:
                    break
                
                # 상세 상태 보고서 전송
                success = self.send_detailed_status_report()
                
                if success:
                    print(f"📊 정기 상태 알림 전송 완료: {datetime.now().strftime('%H:%M:%S')}")
                
            except Exception as e:
                print(f"❌ 주기적 상태 알림 오류: {e}")
    
    def run_posco_news_monitoring(self):
        """포스코 뉴스 모니터링 실행 (별도 터미널)"""
        try:
            # 실제 포스코 메인 알림 시스템 실행
            posco_main_notifier_path = os.path.join(
                os.path.dirname(current_dir),  # WatchHamster_Project
                'Posco_News_Mini_Final', 'scripts', 'posco_main_notifier.py'
            )
            
            if os.path.exists(posco_main_notifier_path):
                print(f"📰 포스코 메인 알림 시스템을 별도 터미널에서 시작합니다...")
                print(f"📁 실행 파일: {posco_main_notifier_path}")
                
                # 운영체제별 터미널 실행 명령어
                import platform
                system = platform.system()
                
                if system == "Darwin":  # macOS
                    # macOS Terminal.app에서 새 탭으로 실행
                    terminal_cmd = [
                        'osascript', '-e',
                        f'''tell application "Terminal"
                            do script "cd '{os.path.dirname(posco_main_notifier_path)}' && python3 '{posco_main_notifier_path}'"
                            set custom title of front window to "🏭 POSCO 뉴스 알림 시스템"
                        end tell'''
                    ]
                elif system == "Windows":  # Windows
                    # Windows에서 새 cmd 창으로 실행
                    terminal_cmd = [
                        'cmd', '/c', 'start', 
                        'cmd', '/k', 
                        f'cd /d "{os.path.dirname(posco_main_notifier_path)}" && python "{posco_main_notifier_path}"'
                    ]
                else:  # Linux
                    # Linux에서 gnome-terminal로 실행
                    terminal_cmd = [
                        'gnome-terminal', '--',
                        'bash', '-c',
                        f'cd "{os.path.dirname(posco_main_notifier_path)}" && python3 "{posco_main_notifier_path}"; exec bash'
                    ]
                
                # 별도 터미널에서 실행
                import subprocess
                self.posco_process = subprocess.Popen(terminal_cmd)
                
                print(f"✅ 포스코 메인 알림 시스템이 별도 터미널에서 시작됨")
                print(f"🖥️ 터미널 제목: '🏭 POSCO 뉴스 알림 시스템'")
                print("📡 포스코 뉴스 알림 (발행, 지연, 비교 등)이 활성화됨")
                print("📋 포스코 로그는 별도 터미널에서 확인 가능")
                
                # 잠시 대기 후 프로세스 상태 확인
                time.sleep(2)
                return True
                
            else:
                print(f"❌ 포스코 메인 알림 시스템 파일 없음: {posco_main_notifier_path}")
                return False
                
        except Exception as e:
            print(f"❌ 포스코 뉴스 시스템 시작 오류: {e}")
            return False
    
    def check_posco_news_status(self):
        """포스코 뉴스 시스템 상태 확인 (별도 터미널 프로세스)"""
        try:
            # 별도 터미널로 실행된 경우 프로세스 이름으로 확인
            import psutil
            
            # python으로 실행 중인 posco_main_notifier.py 프로세스 찾기
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'posco_main_notifier.py' in cmdline:
                            # 포스코 메인 알림 시스템이 실행 중
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 프로세스를 찾지 못한 경우
            return False
            
        except ImportError:
            # psutil이 없는 경우 기본 방식으로 확인
            if hasattr(self, 'posco_process') and self.posco_process:
                poll_result = self.posco_process.poll()
                return poll_result is None
            return False
        except Exception as e:
            print(f"❌ 포스코 뉴스 상태 확인 오류: {e}")
            return False
    
    def restart_posco_news_if_needed(self):
        """필요시 포스코 뉴스 시스템 재시작"""
        if not self.check_posco_news_status():
            print("🔄 포스코 메인 알림 시스템 재시작 중...")
            success = self.run_posco_news_monitoring()
            if success:
                print("✅ 포스코 메인 알림 시스템 재시작 완료")
                print("📡 포스코 뉴스 알림 기능 복구됨")
                
                # 재시작 알림 전송
                self.webhook_sender.send_watchhamster_status(
                    "포스코 메인 알림 시스템 자동 재시작",
                    {
                        "restart_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "reason": "프로세스 중단 감지",
                        "status": "재시작 완료",
                        "restored_functions": "뉴스 발행 알림, 지연 알림, 비교 분석"
                    }
                )
            else:
                print("❌ 포스코 메인 알림 시스템 재시작 실패")
                
                # 재시작 실패 알림
                self.webhook_sender.send_watchhamster_error(
                    "포스코 메인 알림 시스템 재시작 실패",
                    {
                        "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "error": "프로세스 재시작 실패",
                        "impact": "포스코 뉴스 알림 기능 중단"
                    }
                )
    
    def simulate_monitoring_activity(self):
        """실제 모니터링 활동 (포스코 뉴스 포함)"""
        print("🔍 워치햄스터 모니터링 활동 시작")
        print("📰 포스코 뉴스 시스템 관리 포함")
        
        activity_count = 0
        
        while self.is_running:
            try:
                time.sleep(300)  # 5분마다 체크
                
                if not self.is_running:
                    break
                
                activity_count += 1
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"🎯 모니터링 체크 #{activity_count}: {current_time}")
                
                # 포스코 뉴스 시스템 상태 확인 및 필요시 재시작
                self.restart_posco_news_if_needed()
                
                # 10번째 체크마다 상태 알림 (50분마다)
                if activity_count % 10 == 0:
                    success = self.send_detailed_status_report()
                    if success:
                        print(f"📊 정기 상태 보고서 전송됨: {current_time}")
                
            except Exception as e:
                print(f"❌ 모니터링 활동 오류: {e}")
                
                # 오류 알림 전송
                try:
                    error_message_id = self.webhook_sender.send_watchhamster_error(
                        f"워치햄스터 모니터링 오류",
                        {
                            "error": str(e),
                            "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "activity_count": activity_count,
                            "posco_news_status": "확인 중" if self.check_posco_news_status() else "중단됨"
                        }
                    )
                    
                    if error_message_id:
                        print(f"🚨 오류 알림 전송됨: {error_message_id}")
                except Exception as e2:
                    print(f"❌ 오류 알림 전송 실패: {e2}")
    
    def start(self):
        """서비스 시작"""
        if self.is_running:
            print("⚠️ 워치햄스터 서비스가 이미 실행 중입니다")
            return
        
        print("🚀 워치햄스터 서비스 시작 중...")
        self.is_running = True
        
        # 포스코 뉴스 시스템 시작
        posco_started = self.run_posco_news_monitoring()
        if posco_started:
            print("✅ 포스코 뉴스 시스템 연동 완료")
        else:
            print("⚠️ 포스코 뉴스 시스템 연동 실패 - 워치햄스터만 실행")
        
        # 시작 알림 전송
        self.send_startup_notification()
        
        # 주기적 상태 알림 스레드 시작 (120분마다)
        status_thread = threading.Thread(target=self.send_periodic_status, daemon=True)
        status_thread.start()
        
        # 모니터링 활동 스레드 시작 (5분마다 체크)
        self.monitor_thread = threading.Thread(target=self.simulate_monitoring_activity, daemon=True)
        self.monitor_thread.start()
        
        print("✅ POSCO 워치햄스터 전체 시스템이 시작되었습니다")
        print("📊 실행 중인 서비스:")
        print("  🐹 워치햄스터 모니터링 (현재 터미널 - 상위 관리자)")
        print("  📰 포스코 뉴스 모니터링 (별도 터미널 - 하위 서비스)")
        print("  📡 정기 상태 알림 (120분마다)")
        print("  🔍 프로세스 감시 (5분마다)")
        print("  🚀 자동 복구 시스템")
        print()
        print("🖥️ 터미널 구성:")
        print("  • 현재 터미널: 워치햄스터 총괄 관리 로그")
        print("  • 별도 터미널: 포스코 뉴스 알림 로그")
        print()
        print("🔧 전체 시스템을 중지하려면 Ctrl+C를 누르세요")
        
        try:
            # 메인 루프
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중지 요청됨")
            self.stop()
    
    def stop(self):
        """서비스 중지"""
        if not self.is_running:
            return
        
        print("🛑 POSCO 워치햄스터 전체 시스템 중지 중...")
        self.is_running = False
        
        # 포스코 뉴스 시스템 중지 (별도 터미널 프로세스)
        try:
            print("📰 포스코 뉴스 시스템 중지 중...")
            
            # 별도 터미널로 실행된 포스코 프로세스 찾아서 종료
            import psutil
            terminated_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'posco_main_notifier.py' in cmdline:
                            print(f"🔍 포스코 프로세스 발견 (PID: {proc.info['pid']})")
                            proc.terminate()
                            terminated_processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if terminated_processes:
                print(f"✅ 포스코 뉴스 시스템 중지 완료 (PID: {', '.join(map(str, terminated_processes))})")
                print("🖥️ 포스코 터미널은 수동으로 닫아주세요")
            else:
                print("⚠️ 실행 중인 포스코 프로세스를 찾을 수 없음")
                
        except ImportError:
            print("⚠️ psutil 모듈이 없어 포스코 프로세스 자동 종료 불가")
            print("🖥️ 포스코 터미널에서 Ctrl+C로 수동 종료해주세요")
        except Exception as e:
            print(f"❌ 포스코 뉴스 시스템 중지 오류: {e}")
            print("🖥️ 포스코 터미널에서 Ctrl+C로 수동 종료해주세요")
        
        # 중지 알림 전송
        try:
            message_id = self.webhook_sender.send_watchhamster_status(
                "POSCO 워치햄스터 전체 시스템 중지됨",
                {
                    "stop_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "정상 중지",
                    "reason": "사용자 요청",
                    "posco_news_status": "함께 중지됨"
                }
            )
            
            if message_id:
                print(f"📤 중지 알림 전송됨: {message_id}")
                
        except Exception as e:
            print(f"❌ 중지 알림 전송 오류: {e}")
        
        # 웹훅 전송자 정리
        if hasattr(self.webhook_sender, 'shutdown'):
            self.webhook_sender.shutdown(timeout=5)
        
        print("✅ POSCO 워치햄스터 전체 시스템이 중지되었습니다")


def main():
    """메인 실행 함수"""
    print("🎯🛡️ POSCO 워치햄스터 모니터 서비스")
    print("=" * 50)
    print("기능:")
    print("  • 시스템 모니터링")
    print("  • 주기적 상태 알림")
    print("  • 오류 감지 및 알림")
    print("  • 두레이 웹훅 알림 전송")
    print()
    
    # 서비스 시작
    service = WatchhamsterService()
    service.start()


if __name__ == "__main__":
    main()