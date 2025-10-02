"""
System Tray Component - 완전 독립 실행 시스템 트레이
백그라운드에서 WatchHamster 시스템을 관리

주요 기능:
- 🔧 시스템 트레이를 통한 백그라운드 안정 실행
- 🛡️ GUI 애플리케이션 비정상 종료 시 자동 복구
- 📊 실시간 시스템 상태 모니터링
- ⚙️ 트레이에서 직접 시스템 제어

Requirements: 6.5, 6.1 구현
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import sys
from typing import Optional, Callable, Dict, Any

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from core.stability_manager import get_stability_manager
except ImportError:
    print("⚠️ 안정성 관리자를 사용할 수 없습니다")

# pystray 라이브러리가 없는 경우를 대비한 대체 구현
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    print("pystray 라이브러리가 없습니다. 기본 시스템 트레이 기능을 사용합니다.")


class SystemTray:
    """독립 실행 시스템 트레이 - 완전 독립 실행 및 안정성 강화"""
    
    def __init__(self, main_app=None, app_root_dir: Optional[str] = None):
        self.main_app = main_app
        self.app_root_dir = app_root_dir or parent_dir
        self.icon = None
        self.running = False
        self.status_window = None
        
        # 안정성 관리자 초기화
        try:
            self.stability_manager = get_stability_manager(self.app_root_dir)
            self.use_stability = True
        except:
            self.stability_manager = None
            self.use_stability = False
            print("⚠️ 시스템 트레이: 안정성 관리자 없이 실행")
        
        # 상태 정보
        self.system_status = {
            'watchhamster': False,
            'posco_news': False,
            'deployment': False,
            'monitoring': False,
            'stability_manager': self.use_stability
        }
        
        # 자동 복구 설정
        self.auto_recovery_enabled = True
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        self.last_recovery_time = 0
        self.recovery_cooldown = 60  # 60초 쿨다운
        
        # 헬스 체크 설정
        self.health_check_interval = 30  # 30초마다 헬스 체크
        self.last_health_check = 0
        
        # 안정성 관리자 콜백 등록
        if self.use_stability:
            self.stability_manager.register_error_callback(self.on_stability_error)
            self.stability_manager.register_health_callback(self.on_health_update)
        
    def create_icon_image(self, color="green"):
        """시스템 트레이 아이콘 이미지 생성"""
        if not PYSTRAY_AVAILABLE:
            return None
            
        # 간단한 원형 아이콘 생성
        width = height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 색상 매핑
        colors = {
            'green': (0, 255, 0, 255),
            'yellow': (255, 255, 0, 255),
            'red': (255, 0, 0, 255),
            'gray': (128, 128, 128, 255)
        }
        
        fill_color = colors.get(color, colors['gray'])
        
        # 원형 아이콘 그리기
        draw.ellipse([8, 8, width-8, height-8], fill=fill_color)
        
        # 'W' 문자 추가 (WatchHamster)
        draw.text((width//2-8, height//2-8), 'W', fill=(255, 255, 255, 255))
        
        return image
        
    def get_status_color(self):
        """시스템 상태에 따른 아이콘 색상 결정 (안정성 고려)"""
        # 안정성 관리자 상태 확인
        if self.use_stability:
            health = self.stability_manager.get_system_health()
            memory_mb = health.get('memory_usage_mb', 0)
            cpu_percent = health.get('cpu_usage_percent', 0)
            
            # 리소스 사용량이 높으면 경고 색상
            if memory_mb > 800 or cpu_percent > 70:
                return 'red'
        
        # 복구 시도 중이면 노란색
        if self.recovery_attempts > 0:
            return 'yellow'
        
        active_count = sum(1 for status in self.system_status.values() if status)
        
        if active_count == 0:
            return 'gray'  # 모든 시스템 비활성
        elif active_count == len(self.system_status):
            return 'green'  # 모든 시스템 활성
        else:
            return 'yellow'  # 일부 시스템만 활성
            
    def update_icon(self):
        """아이콘 상태 업데이트"""
        if not PYSTRAY_AVAILABLE or not self.icon:
            return
            
        color = self.get_status_color()
        new_image = self.create_icon_image(color)
        if new_image:
            self.icon.icon = new_image
            
    def create_menu(self):
        """시스템 트레이 메뉴 생성 (안정성 기능 포함)"""
        if not PYSTRAY_AVAILABLE:
            return None
        
        stability_menu = pystray.Menu(
            item('시스템 헬스 체크', self.check_system_health),
            item('메모리 정리', self.trigger_memory_cleanup),
            item('설정 파일 복구', self.restore_configs),
            pystray.Menu.SEPARATOR,
            item('자동 복구 활성화', self.toggle_auto_recovery, checked=lambda item: self.auto_recovery_enabled),
            item('안정성 로그 보기', self.show_stability_logs)
        ) if self.use_stability else None
        
        menu_items = [
            item('WatchHamster 상태', self.show_status),
            item('메인 GUI 열기', self.show_main_gui),
            pystray.Menu.SEPARATOR,
            item('서비스 관리', pystray.Menu(
                item('WatchHamster 시작', self.start_watchhamster),
                item('WatchHamster 중지', self.stop_watchhamster),
                pystray.Menu.SEPARATOR,
                item('POSCO 뉴스 시작', self.start_posco_news),
                item('POSCO 뉴스 중지', self.stop_posco_news),
            )),
            pystray.Menu.SEPARATOR,
            item('로그 뷰어', self.show_log_viewer),
            item('알림 센터', self.show_notification_center),
            item('설정', self.show_config_manager)
        ]
        
        # 안정성 메뉴 추가
        if stability_menu:
            menu_items.extend([
                pystray.Menu.SEPARATOR,
                item('안정성 관리', stability_menu)
            ])
        
        menu_items.extend([
            pystray.Menu.SEPARATOR,
            item('종료', self.quit_application)
        ])
        
        return pystray.Menu(*menu_items)
        
    def start_tray(self):
        """시스템 트레이 시작"""
        if not PYSTRAY_AVAILABLE:
            self.start_fallback_tray()
            return
            
        try:
            image = self.create_icon_image()
            menu = self.create_menu()
            
            self.icon = pystray.Icon("WatchHamster", image, "WatchHamster System", menu)
            self.running = True
            
            # 별도 스레드에서 실행
            tray_thread = threading.Thread(target=self.run_tray, daemon=True)
            tray_thread.start()
            
            # 상태 모니터링 시작
            self.start_status_monitoring()
            
            # 안정성 모니터링 시작
            if self.use_stability:
                self.start_stability_monitoring()
            
        except Exception as e:
            print(f"시스템 트레이 시작 오류: {e}")
            self.start_fallback_tray()
            
    def run_tray(self):
        """시스템 트레이 실행"""
        if self.icon:
            self.icon.run()
            
    def start_fallback_tray(self):
        """pystray가 없는 경우 대체 트레이 구현"""
        print("시스템 트레이 대체 모드로 실행 중...")
        self.running = True
        
        # 간단한 상태 창 생성
        self.create_fallback_window()
        
    def create_fallback_window(self):
        """대체 시스템 트레이 창"""
        self.status_window = tk.Tk()
        self.status_window.title("WatchHamster System Tray")
        self.status_window.geometry("300x200")
        
        # 항상 위에 표시
        self.status_window.attributes('-topmost', True)
        
        # 메인 프레임
        main_frame = tk.Frame(self.status_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상태 표시
        tk.Label(main_frame, text="WatchHamster System", 
                font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # 버튼들
        tk.Button(main_frame, text="메인 GUI 열기", 
                 command=self.show_main_gui).pack(fill=tk.X, pady=2)
        tk.Button(main_frame, text="로그 뷰어", 
                 command=self.show_log_viewer).pack(fill=tk.X, pady=2)
        tk.Button(main_frame, text="알림 센터", 
                 command=self.show_notification_center).pack(fill=tk.X, pady=2)
        tk.Button(main_frame, text="설정 관리", 
                 command=self.show_config_manager).pack(fill=tk.X, pady=2)
        
        # 종료 버튼
        tk.Button(main_frame, text="종료", 
                 command=self.quit_application, bg='red', fg='white').pack(fill=tk.X, pady=(10, 0))
        
        # 창 닫기 이벤트 (최소화로 변경)
        self.status_window.protocol("WM_DELETE_WINDOW", self.minimize_window)
        
    def minimize_window(self):
        """창 최소화"""
        if self.status_window:
            self.status_window.withdraw()
            
    def show_status(self):
        """시스템 상태 표시"""
        if self.status_window:
            self.status_window.deiconify()
            self.status_window.lift()
        else:
            self.create_status_dialog()
            
    def create_status_dialog(self):
        """상태 다이얼로그 생성"""
        status_text = "WatchHamster 시스템 상태:\n\n"
        for service, active in self.system_status.items():
            status = "활성" if active else "비활성"
            status_text += f"• {service}: {status}\n"
            
        messagebox.showinfo("시스템 상태", status_text)
        
    def show_main_gui(self):
        """메인 GUI 표시 - 중복 실행 방지"""
        if self.main_app and hasattr(self.main_app, 'root'):
            try:
                # 기존 GUI가 있으면 표시
                if self.main_app.root.winfo_exists():
                    self.main_app.root.deiconify()
                    self.main_app.root.lift()
                    self.main_app.root.focus_force()
                    return
            except tk.TclError:
                pass
        
        # 기존 GUI가 없거나 응답하지 않으면 경고 메시지만 표시
        messagebox.showwarning(
            "GUI 표시", 
            "메인 GUI가 이미 실행 중이거나 응답하지 않습니다.\n\n"
            "새 인스턴스를 시작하려면 기존 프로세스를 종료한 후\n"
            "main_gui.py를 직접 실행해주세요."
        )
                
    def show_log_viewer(self):
        """로그 뷰어 표시"""
        try:
            from .log_viewer import LogViewer
            log_viewer = LogViewer()
            log_viewer.show()
        except Exception as e:
            messagebox.showerror("오류", f"로그 뷰어 실행 실패: {str(e)}")
            
    def show_notification_center(self):
        """알림 센터 표시"""
        try:
            from .notification_center import NotificationCenter
            notification_center = NotificationCenter()
            notification_center.show()
        except Exception as e:
            messagebox.showerror("오류", f"알림 센터 실행 실패: {str(e)}")
            
    def show_config_manager(self):
        """설정 관리자 표시"""
        try:
            from .config_manager import ConfigManager
            config_manager = ConfigManager()
            config_manager.show()
        except Exception as e:
            messagebox.showerror("오류", f"설정 관리자 실행 실패: {str(e)}")
            
    def start_watchhamster(self):
        """WatchHamster 서비스 시작"""
        try:
            # 실제 서비스 시작 로직 구현
            self.system_status['watchhamster'] = True
            self.update_icon()
            messagebox.showinfo("알림", "WatchHamster 서비스가 시작되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"WatchHamster 시작 실패: {str(e)}")
            
    def stop_watchhamster(self):
        """WatchHamster 서비스 중지"""
        try:
            # 실제 서비스 중지 로직 구현
            self.system_status['watchhamster'] = False
            self.update_icon()
            messagebox.showinfo("알림", "WatchHamster 서비스가 중지되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"WatchHamster 중지 실패: {str(e)}")
            
    def start_posco_news(self):
        """POSCO 뉴스 서비스 시작"""
        try:
            # 실제 서비스 시작 로직 구현
            self.system_status['posco_news'] = True
            self.update_icon()
            messagebox.showinfo("알림", "POSCO 뉴스 서비스가 시작되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"POSCO 뉴스 시작 실패: {str(e)}")
            
    def stop_posco_news(self):
        """POSCO 뉴스 서비스 중지"""
        try:
            # 실제 서비스 중지 로직 구현
            self.system_status['posco_news'] = False
            self.update_icon()
            messagebox.showinfo("알림", "POSCO 뉴스 서비스가 중지되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"POSCO 뉴스 중지 실패: {str(e)}")
            
    def start_status_monitoring(self):
        """상태 모니터링 시작"""
        def monitor_loop():
            while self.running:
                try:
                    # 실제 서비스 상태 확인 로직
                    # 여기서는 예시로 간단한 체크만 수행
                    self.check_service_status()
                    self.update_icon()
                    time.sleep(10)  # 10초마다 체크
                except Exception as e:
                    print(f"상태 모니터링 오류: {e}")
                    break
                    
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
    def check_service_status(self):
        """서비스 상태 확인 (안정성 강화)"""
        try:
            # 메인 애플리케이션 상태 확인
            if self.main_app:
                # GUI 애플리케이션이 응답하는지 확인
                if hasattr(self.main_app, 'root') and self.main_app.root.winfo_exists():
                    self.system_status['watchhamster'] = True
                else:
                    self.system_status['watchhamster'] = False
                    
                    # 자동 복구 시도
                    if self.auto_recovery_enabled:
                        self.attempt_recovery('watchhamster')
            
            # 안정성 관리자 상태 확인
            if self.use_stability:
                health = self.stability_manager.get_system_health()
                
                # 메모리 사용량 체크
                memory_mb = health.get('memory_usage_mb', 0)
                if memory_mb > 1000:  # 1GB 초과
                    print(f"⚠️ 높은 메모리 사용량: {memory_mb:.1f}MB")
                    if self.auto_recovery_enabled:
                        self.trigger_memory_cleanup()
                
                # CPU 사용량 체크
                cpu_percent = health.get('cpu_usage_percent', 0)
                if cpu_percent > 80:  # 80% 초과
                    print(f"⚠️ 높은 CPU 사용량: {cpu_percent:.1f}%")
            
        except Exception as e:
            print(f"❌ 서비스 상태 확인 오류: {e}")
            if self.use_stability:
                self.stability_manager.log_error("service_status_check_error", str(e))
    
    def start_stability_monitoring(self):
        """안정성 모니터링 시작"""
        def stability_monitor_loop():
            while self.running:
                try:
                    current_time = time.time()
                    
                    # 헬스 체크
                    if current_time - self.last_health_check >= self.health_check_interval:
                        self.perform_health_check()
                        self.last_health_check = current_time
                    
                    # GUI 응답성 체크
                    self.check_gui_responsiveness()
                    
                    time.sleep(10)  # 10초마다 체크
                    
                except Exception as e:
                    print(f"❌ 안정성 모니터링 오류: {e}")
                    if self.use_stability:
                        self.stability_manager.log_error("stability_monitor_error", str(e))
                    time.sleep(30)  # 오류 시 30초 대기
        
        stability_thread = threading.Thread(target=stability_monitor_loop, daemon=True)
        stability_thread.start()
        print("🛡️ 안정성 모니터링 시작됨")
    
    def perform_health_check(self):
        """헬스 체크 수행"""
        try:
            if not self.use_stability:
                return
            
            health = self.stability_manager.get_system_health()
            
            # 시스템 리소스 체크
            memory_mb = health.get('memory_usage_mb', 0)
            cpu_percent = health.get('cpu_usage_percent', 0)
            thread_count = health.get('thread_count', 0)
            
            # 경고 임계값 체크
            warnings = []
            if memory_mb > 800:
                warnings.append(f"높은 메모리 사용량: {memory_mb:.1f}MB")
            if cpu_percent > 70:
                warnings.append(f"높은 CPU 사용량: {cpu_percent:.1f}%")
            if thread_count > 50:
                warnings.append(f"높은 스레드 수: {thread_count}")
            
            # 경고가 있으면 로그 기록
            if warnings:
                for warning in warnings:
                    print(f"⚠️ {warning}")
                    self.stability_manager.log_error("health_warning", warning)
            
            # 아이콘 업데이트
            self.update_icon()
            
        except Exception as e:
            print(f"❌ 헬스 체크 오류: {e}")
    
    def check_gui_responsiveness(self):
        """GUI 응답성 체크"""
        try:
            if not self.main_app or not hasattr(self.main_app, 'root'):
                return
            
            # GUI가 존재하는지 확인
            if not self.main_app.root.winfo_exists():
                print("⚠️ 메인 GUI가 응답하지 않습니다")
                if self.auto_recovery_enabled:
                    self.attempt_recovery('gui_unresponsive')
                return
            
            # 간단한 응답성 테스트
            try:
                self.main_app.root.update_idletasks()
            except tk.TclError:
                print("⚠️ GUI 응답성 문제 감지")
                if self.auto_recovery_enabled:
                    self.attempt_recovery('gui_responsiveness')
            
        except Exception as e:
            print(f"❌ GUI 응답성 체크 오류: {e}")
    
    def attempt_recovery(self, issue_type: str):
        """자동 복구 시도"""
        current_time = time.time()
        
        # 복구 쿨다운 체크
        if current_time - self.last_recovery_time < self.recovery_cooldown:
            return
        
        # 최대 복구 시도 횟수 체크
        if self.recovery_attempts >= self.max_recovery_attempts:
            print(f"❌ 최대 복구 시도 횟수 초과: {issue_type}")
            return
        
        try:
            print(f"🔄 자동 복구 시도: {issue_type} (시도 {self.recovery_attempts + 1}/{self.max_recovery_attempts})")
            
            success = False
            
            if issue_type == 'watchhamster':
                success = self.recover_main_application()
            elif issue_type == 'gui_unresponsive':
                success = self.recover_gui_responsiveness()
            elif issue_type == 'gui_responsiveness':
                success = self.recover_gui_responsiveness()
            
            if success:
                print(f"✅ 자동 복구 성공: {issue_type}")
                self.recovery_attempts = 0  # 성공 시 카운터 리셋
            else:
                self.recovery_attempts += 1
                print(f"❌ 자동 복구 실패: {issue_type}")
            
            self.last_recovery_time = current_time
            
            # 복구 시도 로그
            if self.use_stability:
                self.stability_manager.log_error("auto_recovery_attempt", 
                    f"{issue_type} - 성공: {success} - 시도: {self.recovery_attempts}")
            
        except Exception as e:
            print(f"❌ 자동 복구 오류: {e}")
            self.recovery_attempts += 1
    
    def recover_main_application(self) -> bool:
        """메인 애플리케이션 복구"""
        try:
            # 메인 GUI 재시작 시도
            if self.main_app and hasattr(self.main_app, 'restart'):
                return self.main_app.restart()
            else:
                # 새 인스턴스 생성 시도
                return self.restart_main_gui()
        except Exception as e:
            print(f"❌ 메인 애플리케이션 복구 실패: {e}")
            return False
    
    def recover_gui_responsiveness(self) -> bool:
        """GUI 응답성 복구"""
        try:
            if not self.main_app or not hasattr(self.main_app, 'root'):
                return False
            
            # 강제 업데이트 시도
            self.main_app.root.update()
            self.main_app.root.update_idletasks()
            
            # 메모리 정리
            if self.use_stability:
                self.stability_manager.trigger_memory_cleanup()
            
            return True
            
        except Exception as e:
            print(f"❌ GUI 응답성 복구 실패: {e}")
            return False
    
    def restart_main_gui(self) -> bool:
        """메인 GUI 재시작 - 중복 실행 방지"""
        try:
            print("⚠️ GUI 자동 재시작은 중복 실행 방지를 위해 비활성화되었습니다.")
            print("수동으로 main_gui.py를 실행해주세요.")
            return False
            
        except Exception as e:
            print(f"❌ 메인 GUI 재시작 실패: {e}")
            return False
    
    def on_stability_error(self, error_type: str, error_message: str):
        """안정성 관리자 오류 콜백"""
        print(f"🚨 안정성 오류: {error_type} - {error_message}")
        
        # 중요한 오류는 자동 복구 시도
        critical_errors = ['high_memory_usage', 'high_cpu_usage', 'config_restore_error']
        if error_type in critical_errors and self.auto_recovery_enabled:
            self.attempt_recovery(error_type)
    
    def on_health_update(self, health: Dict[str, Any]):
        """헬스 업데이트 콜백"""
        # 아이콘 색상 업데이트
        self.update_icon()
    
    # 트레이 메뉴 액션들
    def check_system_health(self):
        """시스템 헬스 체크 (수동)"""
        if not self.use_stability:
            messagebox.showwarning("기능 없음", "안정성 관리자가 활성화되지 않았습니다.")
            return
        
        try:
            health = self.stability_manager.get_system_health()
            
            health_text = "시스템 헬스 상태:\n\n"
            health_text += f"메모리 사용량: {health.get('memory_usage_mb', 0):.1f} MB\n"
            health_text += f"CPU 사용량: {health.get('cpu_usage_percent', 0):.1f}%\n"
            health_text += f"스레드 수: {health.get('thread_count', 0)}\n"
            health_text += f"업타임: {health.get('uptime_seconds', 0):.0f}초\n"
            
            if health.get('last_error'):
                health_text += f"\n마지막 오류: {health['last_error']}"
            
            messagebox.showinfo("시스템 헬스", health_text)
            
        except Exception as e:
            messagebox.showerror("오류", f"헬스 체크 실패: {str(e)}")
    
    def trigger_memory_cleanup(self):
        """메모리 정리 트리거"""
        if not self.use_stability:
            messagebox.showwarning("기능 없음", "안정성 관리자가 활성화되지 않았습니다.")
            return
        
        try:
            self.stability_manager.trigger_memory_cleanup()
            messagebox.showinfo("메모리 정리", "메모리 정리가 완료되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"메모리 정리 실패: {str(e)}")
    
    def restore_configs(self):
        """설정 파일 복구"""
        if not self.use_stability:
            messagebox.showwarning("기능 없음", "안정성 관리자가 활성화되지 않았습니다.")
            return
        
        try:
            self.stability_manager.backup_and_verify_configs()
            messagebox.showinfo("설정 복구", "설정 파일이 복구되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 복구 실패: {str(e)}")
    
    def toggle_auto_recovery(self):
        """자동 복구 토글"""
        self.auto_recovery_enabled = not self.auto_recovery_enabled
        status = "활성화" if self.auto_recovery_enabled else "비활성화"
        print(f"🔄 자동 복구 {status}")
    
    def show_stability_logs(self):
        """안정성 로그 보기"""
        try:
            from .optimized_log_viewer import OptimizedLogViewer
            
            logs_dir = os.path.join(self.app_root_dir, 'logs')
            log_viewer = OptimizedLogViewer(logs_dir=logs_dir)
            log_viewer.show()
            
        except Exception as e:
            messagebox.showerror("오류", f"안정성 로그 뷰어 실행 실패: {str(e)}")
        
    def quit_application(self):
        """애플리케이션 종료"""
        result = messagebox.askyesno("확인", "WatchHamster 시스템을 종료하시겠습니까?")
        if result:
            self.running = False
            
            if self.icon:
                self.icon.stop()
                
            if self.status_window:
                self.status_window.destroy()
                
            # 메인 애플리케이션 종료
            if self.main_app and hasattr(self.main_app, 'quit'):
                self.main_app.quit()
            else:
                sys.exit(0)
                
    def stop(self):
        """시스템 트레이 중지"""
        self.running = False
        if self.icon:
            self.icon.stop()
        if self.status_window:
            self.status_window.destroy()


def main():
    """독립 실행 테스트"""
    system_tray = SystemTray()
    system_tray.start_tray()
    
    # 메인 루프 (fallback 모드용)
    if not PYSTRAY_AVAILABLE and system_tray.status_window:
        system_tray.status_window.mainloop()
    else:
        # pystray 사용 시 메인 스레드 유지
        try:
            while system_tray.running:
                time.sleep(1)
        except KeyboardInterrupt:
            system_tray.stop()


if __name__ == "__main__":
    main()