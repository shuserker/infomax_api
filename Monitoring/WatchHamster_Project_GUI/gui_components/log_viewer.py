"""
Log Viewer Component - 완전 독립 실행 로그 뷰어
logs/ 폴더의 모든 로그 파일을 GUI에서 실시간 모니터링
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import json
from datetime import datetime
import threading
import time
import sys

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from core.performance_optimizer import get_performance_optimizer
except ImportError:
    print("⚠️ 성능 최적화 시스템을 사용할 수 없습니다")


class LogViewer:
    """logs/ 폴더 로그 파일 뷰어 - 완전 독립 실행"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        self.window = None
        self.log_files = {}
        self.current_file = None
        self.auto_refresh = True
        self.refresh_thread = None
        self.running = False
        
        # 성능 최적화 시스템 연결
        try:
            self.performance_optimizer = get_performance_optimizer()
            self.use_optimization = True
        except:
            self.performance_optimizer = None
            self.use_optimization = False
            print("⚠️ 로그 뷰어: 성능 최적화 없이 실행")
        
        # 로그 표시 최적화 설정
        self.max_display_lines = 1000  # 한 번에 표시할 최대 라인 수
        self.chunk_size = 100  # 청크 단위 로딩 크기
        
    def create_window(self):
        """로그 뷰어 창 생성"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("WatchHamster Log Viewer - 완전 독립 실행")
        self.window.geometry("900x600")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 로그 파일 선택
        ttk.Label(control_frame, text="로그 파일:").pack(side=tk.LEFT, padx=(0, 5))
        self.file_combo = ttk.Combobox(control_frame, width=30, state="readonly")
        self.file_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_selected)
        
        # 새로고침 버튼
        ttk.Button(control_frame, text="새로고침", command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # 자동 새로고침 체크박스
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="자동 새로고침", 
                       variable=self.auto_refresh_var,
                       command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=(0, 10))
        
        # 로그 지우기 버튼
        ttk.Button(control_frame, text="로그 지우기", command=self.clear_current_log).pack(side=tk.RIGHT)
        
        # 로그 내용 표시 영역
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                                 font=('Consolas', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 하단 상태 바
        self.status_var = tk.StringVar(value="로그 뷰어 준비")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # 초기 로그 파일 로드
        self.load_log_files()
        self.start_auto_refresh()
        
        # 창 닫기 이벤트 처리
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_log_files(self):
        """logs/ 폴더에서 로그 파일 목록 로드"""
        try:
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)
                self.status_var.set("logs/ 폴더가 생성되었습니다.")
                return
                
            log_files = []
            for file in os.listdir(self.logs_dir):
                if file.endswith(('.log', '.json')):
                    log_files.append(file)
                    
            self.file_combo['values'] = sorted(log_files)
            
            if log_files and not self.current_file:
                self.file_combo.current(0)
                self.current_file = log_files[0]
                self.load_current_log()
                
            self.status_var.set(f"로그 파일 {len(log_files)}개 발견")
            
        except Exception as e:
            self.status_var.set(f"로그 파일 로드 오류: {str(e)}")
            
    def on_file_selected(self, event=None):
        """로그 파일 선택 시 처리"""
        selected = self.file_combo.get()
        if selected and selected != self.current_file:
            self.current_file = selected
            self.load_current_log()
            
    def load_current_log(self):
        """현재 선택된 로그 파일 내용 로드 (성능 최적화 적용)"""
        if not self.current_file:
            return
        
        def _load_log_optimized():
            try:
                log_path = os.path.join(self.logs_dir, self.current_file)
                
                if not os.path.exists(log_path):
                    self._update_log_display(f"로그 파일을 찾을 수 없습니다: {self.current_file}")
                    return
                
                # 성능 최적화: 대용량 파일 처리
                if self.use_optimization:
                    if self.current_file.endswith('.json'):
                        content = self._load_json_log_optimized(log_path)
                    else:
                        content = self._load_text_log_optimized(log_path)
                else:
                    # 기존 방식
                    if self.current_file.endswith('.json'):
                        content = self._load_json_log_legacy(log_path)
                    else:
                        content = self._load_text_log_legacy(log_path)
                
                self._update_log_display(content)
                self.status_var.set(f"로그 로드 완료: {self.current_file}")
                
            except Exception as e:
                error_msg = f"로그 로드 오류: {str(e)}"
                self._update_log_display(error_msg)
                self.status_var.set(f"로그 로드 실패: {self.current_file}")
        
        # 성능 최적화: 백그라운드에서 로그 로드
        if self.use_optimization:
            self.performance_optimizer.schedule_background_task(_load_log_optimized)
        else:
            _load_log_optimized()
    
    def _update_log_display(self, content: str):
        """로그 표시 업데이트 (UI 스레드에서 실행)"""
        def _update():
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, content)
            self.log_text.see(tk.END)
        
        if self.use_optimization:
            self.performance_optimizer.schedule_ui_update(_update)
        else:
            _update()
    
    def _load_text_log_optimized(self, log_path: str) -> str:
        """텍스트 로그 파일 최적화 로드"""
        if self.performance_optimizer:
            # 대용량 파일의 경우 tail 방식 사용
            file_size = os.path.getsize(log_path)
            if file_size > 1024 * 1024:  # 1MB 이상
                lines = self.performance_optimizer.get_log_file_tail(log_path, self.max_display_lines)
                return '\n'.join(lines)
            else:
                lines = self.performance_optimizer.process_large_log_file(
                    log_path, lambda x: x, max_lines=self.max_display_lines
                )
                return '\n'.join(lines)
        else:
            return self._load_text_log_legacy(log_path)
    
    def _load_json_log_optimized(self, log_path: str) -> str:
        """JSON 로그 파일 최적화 로드"""
        if self.performance_optimizer:
            data = self.performance_optimizer.optimize_json_loading(log_path)
            if data:
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return "JSON 로드 실패"
        else:
            return self._load_json_log_legacy(log_path)
    
    def _load_text_log_legacy(self, log_path: str) -> str:
        """텍스트 로그 파일 기존 방식 로드"""
        with open(log_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_json_log_legacy(self, log_path: str) -> str:
        """JSON 로그 파일 기존 방식 로드"""
        with open(log_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return json.dumps(data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                f.seek(0)
                return f.read()
            
    def load_text_log(self, log_path):
        """텍스트 로그 파일 로드 (레거시 호환성)"""
        content = self._load_text_log_legacy(log_path)
        self._update_log_display(content)
        
    def load_json_log(self, log_path):
        """JSON 로그 파일 로드 (레거시 호환성)"""
        content = self._load_json_log_legacy(log_path)
        self._update_log_display(content)
        
    def refresh_logs(self):
        """로그 파일 목록 및 내용 새로고침"""
        current_selection = self.current_file
        self.load_log_files()
        
        # 이전 선택 유지
        if current_selection and current_selection in self.file_combo['values']:
            self.file_combo.set(current_selection)
            self.current_file = current_selection
            self.load_current_log()
            
    def toggle_auto_refresh(self):
        """자동 새로고침 토글"""
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
            
    def start_auto_refresh(self):
        """자동 새로고침 시작"""
        if not self.running:
            self.running = True
            self.refresh_thread = threading.Thread(target=self.auto_refresh_worker, daemon=True)
            self.refresh_thread.start()
            
    def stop_auto_refresh(self):
        """자동 새로고침 중지"""
        self.running = False
        
    def auto_refresh_worker(self):
        """자동 새로고침 워커 스레드 (성능 최적화 적용)"""
        while self.running:
            try:
                if self.auto_refresh and self.current_file:
                    # 성능 최적화: 디바운싱 적용
                    if self.use_optimization:
                        debounced_refresh = self.performance_optimizer.debounce_function(
                            self.load_current_log, delay=1.0
                        )
                        debounced_refresh()
                    else:
                        # UI 업데이트는 메인 스레드에서 실행
                        self.window.after(0, self.load_current_log)
                time.sleep(2)  # 2초마다 새로고침
            except Exception as e:
                print(f"자동 새로고침 오류: {e}")
                break
                
    def clear_current_log(self):
        """현재 로그 파일 내용 지우기"""
        if not self.current_file:
            messagebox.showwarning("경고", "선택된 로그 파일이 없습니다.")
            return
            
        result = messagebox.askyesno("확인", 
                                   f"'{self.current_file}' 로그 파일을 지우시겠습니까?")
        if result:
            try:
                log_path = os.path.join(self.logs_dir, self.current_file)
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write("")
                    
                self.load_current_log()
                self.status_var.set(f"로그 파일 지움: {self.current_file}")
                
            except Exception as e:
                messagebox.showerror("오류", f"로그 파일 지우기 실패: {str(e)}")
                
    def on_closing(self):
        """창 닫기 시 처리"""
        self.stop_auto_refresh()
        if self.window:
            self.window.destroy()
            
    def show(self):
        """로그 뷰어 창 표시"""
        if not self.window:
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()


def main():
    """독립 실행 테스트"""
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기
    
    log_viewer = LogViewer()
    log_viewer.show()
    
    root.mainloop()


if __name__ == "__main__":
    main()