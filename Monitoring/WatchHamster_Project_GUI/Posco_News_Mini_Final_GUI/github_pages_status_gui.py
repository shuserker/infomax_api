#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 상태 모니터링 GUI
POSCO 뉴스 시스템용 GitHub Pages 접근성 실시간 모니터링 GUI

주요 기능:
- 🌐 GitHub Pages 상태 실시간 표시
- 📊 접근성 확인 결과 시각화
- 🚨 접근 실패 시 알림 및 재배포 옵션
- 📈 모니터링 통계 대시보드

Requirements: 1.2, 5.4 구현 (GUI 부분)
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from github_pages_monitor import GitHubPagesMonitor, PageStatus, MonitoringMode
except ImportError as e:
    print(f"❌ GitHub Pages 모니터 모듈 임포트 실패: {e}")
    sys.exit(1)


class GitHubPagesStatusGUI:
    """GitHub Pages 상태 모니터링 GUI 클래스"""
    
    def __init__(self, parent=None):
        """GUI 초기화"""
        self.parent = parent
        self.monitor = GitHubPagesMonitor()
        
        # GUI 상태 변수
        self.monitoring_active = tk.BooleanVar(value=False)
        self.current_url = tk.StringVar(value="https://username.github.io/repository")
        self.current_status = tk.StringVar(value="대기 중")
        self.last_check_time = tk.StringVar(value="없음")
        self.response_time = tk.StringVar(value="0.00초")
        self.success_rate = tk.StringVar(value="0.0%")
        self.total_checks = tk.StringVar(value="0")
        
        # GUI 업데이트 스레드 제어
        self.gui_update_active = False
        self.gui_update_thread = None
        
        # 모니터링 콜백 설정
        self._setup_monitor_callbacks()
        
        # GUI 생성
        self._create_gui()
        
        # 초기 상태 업데이트
        self._update_status_display()
    
    def _setup_monitor_callbacks(self):
        """모니터링 콜백 설정"""
        
        def status_callback(url, status, details):
            """상태 변경 콜백"""
            self.root.after(0, self._handle_status_change, url, status, details)
        
        def accessibility_callback(check):
            """접근성 확인 콜백"""
            self.root.after(0, self._handle_accessibility_check, check)
        
        def alert_callback(message, details):
            """알림 콜백"""
            self.root.after(0, self._handle_alert, message, details)
        
        def redeploy_callback(reason):
            """재배포 콜백"""
            return self.root.after(0, self._handle_redeploy_request, reason)
        
        # 콜백 등록
        self.monitor.register_status_callback(status_callback)
        self.monitor.register_accessibility_callback(accessibility_callback)
        self.monitor.register_alert_callback(alert_callback)
        self.monitor.register_redeploy_callback(redeploy_callback)
    
    def _create_gui(self):
        """GUI 생성"""
        if self.parent:
            self.root = tk.Toplevel(self.parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("GitHub Pages 상태 모니터링")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 1. URL 설정 섹션
        self._create_url_section(main_frame, 0)
        
        # 2. 현재 상태 섹션
        self._create_status_section(main_frame, 1)
        
        # 3. 모니터링 제어 섹션
        self._create_control_section(main_frame, 2)
        
        # 4. 통계 섹션
        self._create_statistics_section(main_frame, 3)
        
        # 5. 로그 섹션
        self._create_log_section(main_frame, 4)
        
        # 6. 버튼 섹션
        self._create_button_section(main_frame, 5)
        
        # GUI 업데이트 스레드 시작
        self._start_gui_update_thread()
    
    def _create_url_section(self, parent, row):
        """URL 설정 섹션 생성"""
        # 섹션 프레임
        url_frame = ttk.LabelFrame(parent, text="🌐 GitHub Pages URL", padding="5")
        url_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        # URL 입력
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        url_entry = ttk.Entry(url_frame, textvariable=self.current_url, width=60)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # URL 테스트 버튼
        test_button = ttk.Button(url_frame, text="테스트", command=self._test_url)
        test_button.grid(row=0, column=2, padx=(5, 0))
    
    def _create_status_section(self, parent, row):
        """현재 상태 섹션 생성"""
        # 섹션 프레임
        status_frame = ttk.LabelFrame(parent, text="📊 현재 상태", padding="5")
        status_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # 상태 정보 표시
        status_info = [
            ("상태:", self.current_status),
            ("마지막 확인:", self.last_check_time),
            ("응답 시간:", self.response_time),
            ("총 확인 횟수:", self.total_checks),
            ("성공률:", self.success_rate)
        ]
        
        for i, (label, var) in enumerate(status_info):
            ttk.Label(status_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            status_label = ttk.Label(status_frame, textvariable=var, font=("TkDefaultFont", 9, "bold"))
            status_label.grid(row=i, column=1, sticky=tk.W)
        
        # 상태 표시등
        self.status_indicator = tk.Canvas(status_frame, width=20, height=20)
        self.status_indicator.grid(row=0, column=2, padx=(10, 0))
        self._update_status_indicator("gray")
    
    def _create_control_section(self, parent, row):
        """모니터링 제어 섹션 생성"""
        # 섹션 프레임
        control_frame = ttk.LabelFrame(parent, text="🎛️ 모니터링 제어", padding="5")
        control_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 모니터링 상태 체크박스
        monitoring_check = ttk.Checkbutton(
            control_frame, 
            text="지속적인 모니터링 활성화", 
            variable=self.monitoring_active,
            command=self._toggle_monitoring
        )
        monitoring_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 간격 설정
        ttk.Label(control_frame, text="확인 간격:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.interval_var = tk.StringVar(value="30")
        interval_spinbox = ttk.Spinbox(
            control_frame, 
            from_=10, 
            to=300, 
            textvariable=self.interval_var, 
            width=10
        )
        interval_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(5, 5))
        ttk.Label(control_frame, text="초").grid(row=1, column=2, sticky=tk.W)
    
    def _create_statistics_section(self, parent, row):
        """통계 섹션 생성"""
        # 섹션 프레임
        stats_frame = ttk.LabelFrame(parent, text="📈 통계", padding="5")
        stats_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        stats_frame.columnconfigure(0, weight=1)
        
        # 통계 트리뷰
        columns = ("항목", "값")
        self.stats_tree = ttk.Treeview(stats_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=150)
        
        self.stats_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_tree.configure(yscrollcommand=stats_scrollbar.set)
    
    def _create_log_section(self, parent, row):
        """로그 섹션 생성"""
        # 섹션 프레임
        log_frame = ttk.LabelFrame(parent, text="📝 로그", padding="5")
        log_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 지우기 버튼
        clear_log_button = ttk.Button(log_frame, text="로그 지우기", command=self._clear_log)
        clear_log_button.grid(row=1, column=0, pady=(5, 0))
    
    def _create_button_section(self, parent, row):
        """버튼 섹션 생성"""
        # 버튼 프레임
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))
        
        # 버튼들
        buttons = [
            ("단일 확인", self._single_check),
            ("배포 검증", self._deployment_verification),
            ("재배포 요청", self._request_redeploy),
            ("통계 새로고침", self._refresh_statistics),
            ("닫기", self._close_window)
        ]
        
        for i, (text, command) in enumerate(buttons):
            button = ttk.Button(button_frame, text=text, command=command)
            button.grid(row=0, column=i, padx=(0, 10) if i < len(buttons) - 1 else (0, 0))
    
    def _update_status_indicator(self, color):
        """상태 표시등 업데이트"""
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline="black")
    
    def _log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 로그 크기 제한 (최대 1000줄)
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", f"{len(lines) - 1000}.0")
    
    def _handle_status_change(self, url, status, details):
        """상태 변경 처리"""
        status_text = {
            PageStatus.UNKNOWN: "알 수 없음",
            PageStatus.CHECKING: "확인 중",
            PageStatus.ACCESSIBLE: "접근 가능",
            PageStatus.INACCESSIBLE: "접근 불가",
            PageStatus.ERROR: "오류",
            PageStatus.TIMEOUT: "타임아웃"
        }.get(status, "알 수 없음")
        
        self.current_status.set(status_text)
        
        # 상태 표시등 색상 변경
        color_map = {
            PageStatus.ACCESSIBLE: "green",
            PageStatus.INACCESSIBLE: "red",
            PageStatus.CHECKING: "yellow",
            PageStatus.ERROR: "red",
            PageStatus.TIMEOUT: "orange",
            PageStatus.UNKNOWN: "gray"
        }
        self._update_status_indicator(color_map.get(status, "gray"))
        
        # 로그 메시지
        self._log_message(f"상태 변경: {url} -> {status_text}")
        
        if details:
            if "response_time" in details:
                self.response_time.set(f"{details['response_time']:.2f}초")
            if "error" in details:
                self._log_message(f"오류: {details['error']}")
    
    def _handle_accessibility_check(self, check):
        """접근성 확인 처리"""
        self.last_check_time.set(datetime.now().strftime('%H:%M:%S'))
        
        if check.response_time:
            self.response_time.set(f"{check.response_time:.2f}초")
        
        status_text = "✅ 접근 가능" if check.accessible else "❌ 접근 불가"
        self._log_message(f"접근성 확인: {check.url} -> {status_text}")
        
        if not check.accessible and check.error_message:
            self._log_message(f"오류 상세: {check.error_message}")
    
    def _handle_alert(self, message, details):
        """알림 처리"""
        self._log_message(f"🚨 알림: {message}")
        
        # 중요한 알림은 메시지박스로 표시
        if "접근 실패" in message or "연속" in message:
            response = messagebox.askyesno(
                "GitHub Pages 접근 실패",
                f"{message}\n\n자동 재배포를 시도하시겠습니까?",
                icon="warning"
            )
            
            if response:
                self._request_redeploy()
    
    def _handle_redeploy_request(self, reason):
        """재배포 요청 처리"""
        self._log_message(f"🔄 재배포 요청: {reason}")
        
        # 실제 재배포 로직은 여기에 구현
        # 현재는 시뮬레이션만 수행
        messagebox.showinfo("재배포 요청", f"재배포가 요청되었습니다.\n사유: {reason}")
        return True
    
    def _test_url(self):
        """URL 테스트"""
        url = self.current_url.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요.")
            return
        
        self._log_message(f"URL 테스트 시작: {url}")
        
        # 별도 스레드에서 테스트 실행
        def test_thread():
            try:
                check = self.monitor.check_page_accessibility(url)
                self.root.after(0, self._show_test_result, check)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("테스트 오류", f"테스트 중 오류 발생: {str(e)}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _show_test_result(self, check):
        """테스트 결과 표시"""
        if check.accessible:
            messagebox.showinfo(
                "테스트 성공",
                f"URL 접근 성공!\n\n"
                f"응답 시간: {check.response_time:.2f}초\n"
                f"상태 코드: {check.status_code}\n"
                f"페이지 제목: {check.page_title or '없음'}"
            )
        else:
            messagebox.showerror(
                "테스트 실패",
                f"URL 접근 실패\n\n"
                f"오류: {check.error_message}\n"
                f"상태 코드: {check.status_code or '없음'}"
            )
    
    def _toggle_monitoring(self):
        """모니터링 토글"""
        if self.monitoring_active.get():
            # 모니터링 시작
            url = self.current_url.get().strip()
            if not url:
                messagebox.showerror("오류", "URL을 입력해주세요.")
                self.monitoring_active.set(False)
                return
            
            try:
                interval = int(self.interval_var.get())
                session_id = self.monitor.start_continuous_monitoring(url, interval)
                self._log_message(f"지속적인 모니터링 시작: {session_id}")
            except Exception as e:
                messagebox.showerror("모니터링 시작 오류", f"모니터링 시작 실패: {str(e)}")
                self.monitoring_active.set(False)
        else:
            # 모니터링 중지
            self.monitor.stop_continuous_monitoring()
            self._log_message("지속적인 모니터링 중지")
    
    def _single_check(self):
        """단일 확인"""
        url = self.current_url.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요.")
            return
        
        self._log_message(f"단일 접근성 확인 시작: {url}")
        
        # 별도 스레드에서 확인 실행
        def check_thread():
            try:
                check = self.monitor.check_page_accessibility(url)
                self.root.after(0, self._show_test_result, check)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("확인 오류", f"확인 중 오류 발생: {str(e)}"))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def _deployment_verification(self):
        """배포 검증"""
        url = self.current_url.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요.")
            return
        
        self._log_message(f"배포 검증 시작: {url}")
        
        # 별도 스레드에서 검증 실행
        def verify_thread():
            try:
                result = self.monitor.verify_github_pages_deployment(url, max_wait_time=300)
                self.root.after(0, self._show_verification_result, result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("검증 오류", f"검증 중 오류 발생: {str(e)}"))
        
        threading.Thread(target=verify_thread, daemon=True).start()
    
    def _show_verification_result(self, result):
        """검증 결과 표시"""
        if result["deployment_successful"]:
            messagebox.showinfo(
                "배포 검증 성공",
                f"GitHub Pages 배포 검증 성공!\n\n"
                f"확인 횟수: {result['checks_performed']}\n"
                f"총 대기 시간: {result['total_wait_time']:.1f}초"
            )
        else:
            messagebox.showerror(
                "배포 검증 실패",
                f"GitHub Pages 배포 검증 실패\n\n"
                f"확인 횟수: {result['checks_performed']}\n"
                f"총 대기 시간: {result['total_wait_time']:.1f}초\n"
                f"오류: {result.get('error_message', '알 수 없는 오류')}"
            )
    
    def _request_redeploy(self):
        """재배포 요청"""
        response = messagebox.askyesno(
            "재배포 확인",
            "GitHub Pages 재배포를 요청하시겠습니까?\n\n"
            "이 작업은 전체 배포 프로세스를 다시 실행합니다."
        )
        
        if response:
            success = self.monitor.request_auto_redeploy("사용자 수동 요청")
            if success:
                messagebox.showinfo("재배포 요청", "재배포가 성공적으로 요청되었습니다.")
            else:
                messagebox.showerror("재배포 실패", "재배포 요청에 실패했습니다.")
    
    def _refresh_statistics(self):
        """통계 새로고침"""
        try:
            stats = self.monitor.get_monitoring_statistics()
            
            # 통계 트리뷰 업데이트
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            # 통계 데이터 추가
            if "accessibility" in stats:
                acc_stats = stats["accessibility"]
                self.stats_tree.insert("", "end", values=("총 확인 횟수", acc_stats.get("total_checks", 0)))
                self.stats_tree.insert("", "end", values=("성공한 확인", acc_stats.get("successful_checks", 0)))
                self.stats_tree.insert("", "end", values=("실패한 확인", acc_stats.get("failed_checks", 0)))
            
            if "sessions" in stats:
                sess_stats = stats["sessions"]
                self.stats_tree.insert("", "end", values=("총 세션 수", sess_stats.get("total_sessions", 0)))
                self.stats_tree.insert("", "end", values=("활성 세션", sess_stats.get("active_sessions", 0)))
            
            self.stats_tree.insert("", "end", values=("전체 성공률", f"{stats.get('success_rate', 0):.1f}%"))
            
            self._log_message("통계 새로고침 완료")
            
        except Exception as e:
            messagebox.showerror("통계 오류", f"통계 조회 실패: {str(e)}")
    
    def _update_status_display(self):
        """상태 표시 업데이트"""
        try:
            status = self.monitor.get_current_status()
            
            if status and not status.get("error"):
                self.total_checks.set(str(status.get("total_checks", 0)))
                self.success_rate.set(f"{status.get('success_rate', 0):.1f}%")
                
                if status.get("monitoring_active"):
                    self.monitoring_active.set(True)
                
        except Exception as e:
            self._log_message(f"상태 업데이트 오류: {str(e)}")
    
    def _start_gui_update_thread(self):
        """GUI 업데이트 스레드 시작"""
        self.gui_update_active = True
        
        def update_loop():
            while self.gui_update_active:
                try:
                    self.root.after(0, self._update_status_display)
                    time.sleep(5)  # 5초마다 업데이트
                except Exception as e:
                    print(f"GUI 업데이트 오류: {e}")
                    break
        
        self.gui_update_thread = threading.Thread(target=update_loop, daemon=True)
        self.gui_update_thread.start()
    
    def _clear_log(self):
        """로그 지우기"""
        self.log_text.delete("1.0", tk.END)
        self._log_message("로그가 지워졌습니다.")
    
    def _close_window(self):
        """창 닫기"""
        # 모니터링 중지
        if self.monitoring_active.get():
            self.monitor.stop_continuous_monitoring()
        
        # GUI 업데이트 스레드 중지
        self.gui_update_active = False
        
        # 창 닫기
        self.root.destroy()
    
    def show(self):
        """GUI 표시"""
        self.root.mainloop()


def main():
    """메인 함수"""
    try:
        app = GitHubPagesStatusGUI()
        app.show()
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"💥 프로그램 실행 중 오류: {str(e)}")


if __name__ == "__main__":
    main()