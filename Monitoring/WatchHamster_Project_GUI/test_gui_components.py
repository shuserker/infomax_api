#!/usr/bin/env python3
"""
GUI Components Test Script - 완전 독립 실행 테스트
모든 GUI 컴포넌트의 기본 기능을 테스트
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 현재 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from gui_components.log_viewer import LogViewer
    from gui_components.notification_center import NotificationCenter, notify_info, notify_warning, notify_error, notify_success
    from gui_components.system_tray import SystemTray
    from gui_components.config_manager import ConfigManager
except ImportError as e:
    print(f"GUI 컴포넌트 임포트 오류: {e}")
    sys.exit(1)


class GUIComponentTester:
    """GUI 컴포넌트 테스터"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WatchHamster GUI Components Tester")
        self.root.geometry("500x400")
        
        # 컴포넌트 인스턴스
        self.log_viewer = None
        self.notification_center = None
        self.system_tray = None
        self.config_manager = None
        
        self.create_ui()
        
    def create_ui(self):
        """테스터 UI 생성"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ttk.Label(main_frame, text="WatchHamster GUI Components Tester", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 설명
        desc_label = ttk.Label(main_frame, 
                              text="각 GUI 컴포넌트를 개별적으로 테스트할 수 있습니다.",
                              font=('Arial', 10))
        desc_label.pack(pady=(0, 20))
        
        # 컴포넌트 테스트 버튼들
        self.create_component_buttons(main_frame)
        
        # 통합 테스트 버튼들
        self.create_integration_buttons(main_frame)
        
        # 상태 표시
        self.status_var = tk.StringVar(value="테스터 준비 완료")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, pady=(20, 0))
        
    def create_component_buttons(self, parent):
        """개별 컴포넌트 테스트 버튼 생성"""
        components_frame = ttk.LabelFrame(parent, text="개별 컴포넌트 테스트")
        components_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Log Viewer 테스트
        ttk.Button(components_frame, text="Log Viewer 테스트", 
                  command=self.test_log_viewer).pack(fill=tk.X, pady=2, padx=10)
        
        # Notification Center 테스트
        ttk.Button(components_frame, text="Notification Center 테스트", 
                  command=self.test_notification_center).pack(fill=tk.X, pady=2, padx=10)
        
        # System Tray 테스트
        ttk.Button(components_frame, text="System Tray 테스트", 
                  command=self.test_system_tray).pack(fill=tk.X, pady=2, padx=10)
        
        # Config Manager 테스트
        ttk.Button(components_frame, text="Config Manager 테스트", 
                  command=self.test_config_manager).pack(fill=tk.X, pady=2, padx=10)
        
    def create_integration_buttons(self, parent):
        """통합 테스트 버튼 생성"""
        integration_frame = ttk.LabelFrame(parent, text="통합 테스트")
        integration_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 모든 컴포넌트 테스트
        ttk.Button(integration_frame, text="모든 컴포넌트 실행", 
                  command=self.test_all_components).pack(fill=tk.X, pady=2, padx=10)
        
        # 테스트 데이터 생성
        ttk.Button(integration_frame, text="테스트 데이터 생성", 
                  command=self.create_test_data).pack(fill=tk.X, pady=2, padx=10)
        
        # 테스트 알림 전송
        ttk.Button(integration_frame, text="테스트 알림 전송", 
                  command=self.send_test_notifications).pack(fill=tk.X, pady=2, padx=10)
        
    def test_log_viewer(self):
        """Log Viewer 테스트"""
        try:
            self.status_var.set("Log Viewer 테스트 중...")
            
            if not self.log_viewer:
                self.log_viewer = LogViewer(self.root)
                
            self.log_viewer.show()
            self.status_var.set("Log Viewer 테스트 완료")
            
        except Exception as e:
            messagebox.showerror("오류", f"Log Viewer 테스트 실패: {str(e)}")
            self.status_var.set("Log Viewer 테스트 실패")
            
    def test_notification_center(self):
        """Notification Center 테스트"""
        try:
            self.status_var.set("Notification Center 테스트 중...")
            
            if not self.notification_center:
                self.notification_center = NotificationCenter(self.root)
                
            self.notification_center.show()
            self.status_var.set("Notification Center 테스트 완료")
            
        except Exception as e:
            messagebox.showerror("오류", f"Notification Center 테스트 실패: {str(e)}")
            self.status_var.set("Notification Center 테스트 실패")
            
    def test_system_tray(self):
        """System Tray 테스트"""
        try:
            self.status_var.set("System Tray 테스트 중...")
            
            if not self.system_tray:
                self.system_tray = SystemTray(self)
                
            self.system_tray.start_tray()
            self.status_var.set("System Tray 테스트 완료 (백그라운드 실행)")
            
            messagebox.showinfo("알림", 
                              "System Tray가 백그라운드에서 실행 중입니다.\n"
                              "시스템 트레이 또는 대체 창을 확인하세요.")
            
        except Exception as e:
            messagebox.showerror("오류", f"System Tray 테스트 실패: {str(e)}")
            self.status_var.set("System Tray 테스트 실패")
            
    def test_config_manager(self):
        """Config Manager 테스트"""
        try:
            self.status_var.set("Config Manager 테스트 중...")
            
            if not self.config_manager:
                self.config_manager = ConfigManager(self.root)
                
            self.config_manager.show()
            self.status_var.set("Config Manager 테스트 완료")
            
        except Exception as e:
            messagebox.showerror("오류", f"Config Manager 테스트 실패: {str(e)}")
            self.status_var.set("Config Manager 테스트 실패")
            
    def test_all_components(self):
        """모든 컴포넌트 테스트"""
        try:
            self.status_var.set("모든 컴포넌트 테스트 중...")
            
            # 순차적으로 모든 컴포넌트 실행
            self.test_log_viewer()
            self.test_notification_center()
            self.test_config_manager()
            self.test_system_tray()
            
            self.status_var.set("모든 컴포넌트 테스트 완료")
            messagebox.showinfo("완료", "모든 GUI 컴포넌트가 성공적으로 실행되었습니다!")
            
        except Exception as e:
            messagebox.showerror("오류", f"통합 테스트 실패: {str(e)}")
            self.status_var.set("통합 테스트 실패")
            
    def create_test_data(self):
        """테스트 데이터 생성"""
        try:
            self.status_var.set("테스트 데이터 생성 중...")
            
            # 테스트 로그 파일 생성
            logs_dir = os.path.join(current_dir, 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
                
            # 테스트 로그 작성
            test_log_path = os.path.join(logs_dir, 'test_gui_components.log')
            with open(test_log_path, 'w', encoding='utf-8') as f:
                f.write("=== WatchHamster GUI Components Test Log ===\n")
                f.write("2024-01-01 12:00:00 - INFO - GUI 컴포넌트 테스트 시작\n")
                f.write("2024-01-01 12:00:01 - INFO - Log Viewer 컴포넌트 로드\n")
                f.write("2024-01-01 12:00:02 - INFO - Notification Center 컴포넌트 로드\n")
                f.write("2024-01-01 12:00:03 - INFO - System Tray 컴포넌트 로드\n")
                f.write("2024-01-01 12:00:04 - INFO - Config Manager 컴포넌트 로드\n")
                f.write("2024-01-01 12:00:05 - SUCCESS - 모든 컴포넌트 로드 완료\n")
                
            # 테스트 설정 파일 생성
            config_dir = os.path.join(current_dir, 'config')
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            test_config_path = os.path.join(config_dir, 'test_config.json')
            test_config = {
                "test_mode": True,
                "components": {
                    "log_viewer": {"enabled": True},
                    "notification_center": {"enabled": True},
                    "system_tray": {"enabled": True},
                    "config_manager": {"enabled": True}
                },
                "test_data": {
                    "created_at": "2024-01-01T12:00:00",
                    "version": "1.0.0"
                }
            }
            
            import json
            with open(test_config_path, 'w', encoding='utf-8') as f:
                json.dump(test_config, f, indent=2, ensure_ascii=False)
                
            self.status_var.set("테스트 데이터 생성 완료")
            messagebox.showinfo("완료", 
                              f"테스트 데이터가 생성되었습니다:\n"
                              f"- 로그: {test_log_path}\n"
                              f"- 설정: {test_config_path}")
            
        except Exception as e:
            messagebox.showerror("오류", f"테스트 데이터 생성 실패: {str(e)}")
            self.status_var.set("테스트 데이터 생성 실패")
            
    def send_test_notifications(self):
        """테스트 알림 전송"""
        try:
            self.status_var.set("테스트 알림 전송 중...")
            
            # 다양한 레벨의 테스트 알림 전송
            notify_info("테스트 정보", "GUI 컴포넌트 테스트 정보 알림입니다.", "GUI Tester")
            notify_success("테스트 성공", "GUI 컴포넌트 테스트가 성공했습니다.", "GUI Tester")
            notify_warning("테스트 경고", "GUI 컴포넌트 테스트 경고 알림입니다.", "GUI Tester")
            notify_error("테스트 오류", "GUI 컴포넌트 테스트 오류 알림입니다.", "GUI Tester")
            
            self.status_var.set("테스트 알림 전송 완료")
            messagebox.showinfo("완료", "테스트 알림이 전송되었습니다. Notification Center를 확인하세요.")
            
        except Exception as e:
            messagebox.showerror("오류", f"테스트 알림 전송 실패: {str(e)}")
            self.status_var.set("테스트 알림 전송 실패")
            
    def run(self):
        """테스터 실행"""
        self.root.mainloop()
        
    def quit(self):
        """테스터 종료"""
        # 모든 컴포넌트 정리
        if self.system_tray:
            self.system_tray.stop()
            
        self.root.quit()


def main():
    """메인 함수"""
    print("WatchHamster GUI Components Tester 시작...")
    
    try:
        tester = GUIComponentTester()
        tester.run()
    except Exception as e:
        print(f"테스터 실행 오류: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())