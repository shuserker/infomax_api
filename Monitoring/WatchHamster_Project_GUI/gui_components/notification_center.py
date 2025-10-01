"""
Notification Center Component - 완전 독립 실행 알림 센터
시스템 전체의 알림을 중앙 집중식으로 관리
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import queue
import json
import os


class NotificationCenter:
    """내장 알림 센터 - 완전 독립 실행"""
    
    # 알림 레벨 정의
    LEVEL_INFO = "INFO"
    LEVEL_WARNING = "WARNING"
    LEVEL_ERROR = "ERROR"
    LEVEL_SUCCESS = "SUCCESS"
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.notifications = []
        self.notification_queue = queue.Queue()
        self.max_notifications = 100
        self.auto_clear_hours = 24
        
        # 알림 저장 파일
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.notifications_file = os.path.join(self.data_dir, 'notifications.json')
        
        # GUI 요소
        self.tree = None
        self.status_var = None
        self.filter_var = None
        
        # 스레드 관리
        self.running = False
        self.worker_thread = None
        
        # 알림 로드
        self.load_notifications()
        
    def create_window(self):
        """알림 센터 창 생성"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("WatchHamster Notification Center - 완전 독립 실행")
        self.window.geometry("800x500")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 필터 옵션
        ttk.Label(control_frame, text="필터:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_var = tk.StringVar(value="ALL")
        filter_combo = ttk.Combobox(control_frame, textvariable=self.filter_var,
                                   values=["ALL", "INFO", "WARNING", "ERROR", "SUCCESS"],
                                   width=10, state="readonly")
        filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
        # 컨트롤 버튼들
        ttk.Button(control_frame, text="새로고침", command=self.refresh_display).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="모두 지우기", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="선택 삭제", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        # 테스트 알림 버튼 (개발용)
        ttk.Button(control_frame, text="테스트 알림", command=self.add_test_notification).pack(side=tk.RIGHT)
        
        # 알림 목록 트리뷰
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 트리뷰 생성
        columns = ("시간", "레벨", "제목", "내용")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # 컬럼 설정
        self.tree.heading("시간", text="시간")
        self.tree.heading("레벨", text="레벨")
        self.tree.heading("제목", text="제목")
        self.tree.heading("내용", text="내용")
        
        self.tree.column("시간", width=150, minwidth=100)
        self.tree.column("레벨", width=80, minwidth=60)
        self.tree.column("제목", width=200, minwidth=150)
        self.tree.column("내용", width=350, minwidth=200)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 더블클릭 이벤트
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        # 하단 상태 바
        self.status_var = tk.StringVar(value=f"알림 {len(self.notifications)}개")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # 초기 표시
        self.refresh_display()
        
        # 워커 스레드 시작
        self.start_worker()
        
        # 창 닫기 이벤트 처리
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def add_notification(self, level, title, message, source="System"):
        """새 알림 추가"""
        notification = {
            "id": len(self.notifications) + 1,
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "title": title,
            "message": message,
            "source": source,
            "read": False
        }
        
        # 큐에 추가 (스레드 안전)
        self.notification_queue.put(notification)
        
    def process_notifications(self):
        """큐에서 알림 처리"""
        try:
            while not self.notification_queue.empty():
                notification = self.notification_queue.get_nowait()
                self.notifications.insert(0, notification)  # 최신 알림을 맨 위에
                
                # 최대 개수 제한
                if len(self.notifications) > self.max_notifications:
                    self.notifications = self.notifications[:self.max_notifications]
                    
                # 파일에 저장
                self.save_notifications()
                
                # GUI 업데이트 (메인 스레드에서)
                if self.window:
                    self.window.after(0, self.refresh_display)
                    
        except queue.Empty:
            pass
        except Exception as e:
            print(f"알림 처리 오류: {e}")
            
    def refresh_display(self):
        """알림 목록 표시 새로고침"""
        if not self.tree:
            return
            
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 필터 적용
        filtered_notifications = self.get_filtered_notifications()
        
        # 알림 표시
        for notification in filtered_notifications:
            timestamp = datetime.fromisoformat(notification["timestamp"])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # 레벨에 따른 태그 설정
            tags = (notification["level"].lower(),)
            
            self.tree.insert("", tk.END, 
                           values=(time_str, notification["level"], 
                                 notification["title"], notification["message"]),
                           tags=tags)
                           
        # 레벨별 색상 설정
        self.tree.tag_configure("info", foreground="blue")
        self.tree.tag_configure("warning", foreground="orange")
        self.tree.tag_configure("error", foreground="red")
        self.tree.tag_configure("success", foreground="green")
        
        # 상태 업데이트
        if self.status_var:
            total = len(self.notifications)
            filtered = len(filtered_notifications)
            self.status_var.set(f"알림 {filtered}/{total}개 표시")
            
    def get_filtered_notifications(self):
        """필터 조건에 맞는 알림 반환"""
        if not self.filter_var or self.filter_var.get() == "ALL":
            return self.notifications
            
        filter_level = self.filter_var.get()
        return [n for n in self.notifications if n["level"] == filter_level]
        
    def apply_filter(self, event=None):
        """필터 적용"""
        self.refresh_display()
        
    def clear_all(self):
        """모든 알림 지우기"""
        if tk.messagebox.askyesno("확인", "모든 알림을 삭제하시겠습니까?"):
            self.notifications.clear()
            self.save_notifications()
            self.refresh_display()
            
    def delete_selected(self):
        """선택된 알림 삭제"""
        selected_items = self.tree.selection()
        if not selected_items:
            tk.messagebox.showwarning("경고", "삭제할 알림을 선택하세요.")
            return
            
        # 선택된 항목의 인덱스 찾기
        indices_to_remove = []
        for item in selected_items:
            values = self.tree.item(item)["values"]
            if values:
                timestamp_str = values[0]
                # 타임스탬프로 알림 찾기
                for i, notification in enumerate(self.notifications):
                    notif_time = datetime.fromisoformat(notification["timestamp"])
                    if notif_time.strftime("%Y-%m-%d %H:%M:%S") == timestamp_str:
                        indices_to_remove.append(i)
                        break
                        
        # 인덱스 역순으로 삭제
        for i in sorted(indices_to_remove, reverse=True):
            del self.notifications[i]
            
        self.save_notifications()
        self.refresh_display()
        
    def on_item_double_click(self, event):
        """알림 항목 더블클릭 시 상세 정보 표시"""
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if not selected_item:
            return
            
        values = self.tree.item(selected_item)["values"]
        if values:
            detail_window = tk.Toplevel(self.window)
            detail_window.title("알림 상세 정보")
            detail_window.geometry("500x300")
            
            # 상세 정보 표시
            text_widget = tk.Text(detail_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            detail_text = f"시간: {values[0]}\n"
            detail_text += f"레벨: {values[1]}\n"
            detail_text += f"제목: {values[2]}\n\n"
            detail_text += f"내용:\n{values[3]}"
            
            text_widget.insert(tk.END, detail_text)
            text_widget.config(state=tk.DISABLED)
            
    def add_test_notification(self):
        """테스트 알림 추가 (개발용)"""
        import random
        levels = [self.LEVEL_INFO, self.LEVEL_WARNING, self.LEVEL_ERROR, self.LEVEL_SUCCESS]
        level = random.choice(levels)
        
        test_messages = {
            self.LEVEL_INFO: ("정보", "시스템 정보 메시지입니다."),
            self.LEVEL_WARNING: ("경고", "주의가 필요한 상황입니다."),
            self.LEVEL_ERROR: ("오류", "오류가 발생했습니다."),
            self.LEVEL_SUCCESS: ("성공", "작업이 성공적으로 완료되었습니다.")
        }
        
        title, message = test_messages[level]
        self.add_notification(level, title, message, "테스트")
        
    def save_notifications(self):
        """알림을 파일에 저장"""
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump(self.notifications, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"알림 저장 오류: {e}")
            
    def load_notifications(self):
        """파일에서 알림 로드"""
        try:
            if os.path.exists(self.notifications_file):
                with open(self.notifications_file, 'r', encoding='utf-8') as f:
                    self.notifications = json.load(f)
            else:
                self.notifications = []
                
        except Exception as e:
            print(f"알림 로드 오류: {e}")
            self.notifications = []
            
    def start_worker(self):
        """워커 스레드 시작"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self.worker_loop, daemon=True)
            self.worker_thread.start()
            
    def worker_loop(self):
        """워커 스레드 루프"""
        while self.running:
            try:
                self.process_notifications()
                threading.Event().wait(1)  # 1초 대기
            except Exception as e:
                print(f"워커 스레드 오류: {e}")
                break
                
    def on_closing(self):
        """창 닫기 시 처리"""
        self.running = False
        if self.window:
            self.window.destroy()
            
    def show(self):
        """알림 센터 창 표시"""
        if not self.window:
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()


# 전역 알림 센터 인스턴스
_notification_center = None

def get_notification_center():
    """전역 알림 센터 인스턴스 반환"""
    global _notification_center
    if _notification_center is None:
        _notification_center = NotificationCenter()
    return _notification_center

def notify_info(title, message, source="System"):
    """정보 알림 추가"""
    get_notification_center().add_notification(
        NotificationCenter.LEVEL_INFO, title, message, source)

def notify_warning(title, message, source="System"):
    """경고 알림 추가"""
    get_notification_center().add_notification(
        NotificationCenter.LEVEL_WARNING, title, message, source)

def notify_error(title, message, source="System"):
    """오류 알림 추가"""
    get_notification_center().add_notification(
        NotificationCenter.LEVEL_ERROR, title, message, source)

def notify_success(title, message, source="System"):
    """성공 알림 추가"""
    get_notification_center().add_notification(
        NotificationCenter.LEVEL_SUCCESS, title, message, source)


def main():
    """독립 실행 테스트"""
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기
    
    notification_center = NotificationCenter()
    notification_center.show()
    
    # 테스트 알림 추가
    notification_center.add_notification("INFO", "시스템 시작", "WatchHamster 시스템이 시작되었습니다.")
    notification_center.add_notification("SUCCESS", "배포 완료", "GitHub Pages 배포가 성공했습니다.")
    notification_center.add_notification("WARNING", "데이터 부족", "kospi 데이터가 부족합니다.")
    
    root.mainloop()


if __name__ == "__main__":
    main()