"""
Config Manager Component - 완전 독립 실행 설정 관리자
config/ 폴더의 모든 설정 파일을 GUI에서 관리
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import shutil


class ConfigManager:
    """config/ 폴더 설정 관리 - 완전 독립 실행"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.current_file = None
        self.config_data = {}
        self.modified = False
        
        # GUI 요소
        self.file_combo = None
        self.tree = None
        self.value_entry = None
        self.status_var = None
        self.modified_var = None
        
        # 설정 파일 템플릿
        self.config_templates = {
            'gui_config.json': {
                "window": {
                    "width": 1200,
                    "height": 800,
                    "title": "WatchHamster GUI"
                },
                "theme": {
                    "style": "default",
                    "colors": {
                        "primary": "#007acc",
                        "secondary": "#f0f0f0",
                        "success": "#28a745",
                        "warning": "#ffc107",
                        "error": "#dc3545"
                    }
                },
                "logging": {
                    "level": "INFO",
                    "max_files": 10,
                    "max_size_mb": 10
                }
            },
            'webhook_config.json': {
                "webhook_url": "",
                "timeout": 30,
                "retry_count": 3,
                "retry_delay": 5,
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "WatchHamster/1.0"
                }
            },
            'message_templates.json': {
                "templates": {
                    "deployment_success": {
                        "title": "배포 성공",
                        "message": "GitHub Pages 배포가 성공적으로 완료되었습니다.",
                        "color": "green"
                    },
                    "deployment_failed": {
                        "title": "배포 실패",
                        "message": "GitHub Pages 배포 중 오류가 발생했습니다.",
                        "color": "red"
                    },
                    "data_warning": {
                        "title": "데이터 경고",
                        "message": "데이터가 부족하거나 오래되었습니다.",
                        "color": "orange"
                    }
                }
            }
        }
        
    def create_window(self):
        """설정 관리자 창 생성"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("WatchHamster Config Manager - 완전 독립 실행")
        self.window.geometry("900x700")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 설정 파일 선택
        ttk.Label(control_frame, text="설정 파일:").pack(side=tk.LEFT, padx=(0, 5))
        self.file_combo = ttk.Combobox(control_frame, width=25, state="readonly")
        self.file_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_selected)
        
        # 파일 관리 버튼들
        ttk.Button(control_frame, text="새로고침", command=self.refresh_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="새 파일", command=self.create_new_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="백업", command=self.backup_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="복원", command=self.restore_config).pack(side=tk.LEFT, padx=(0, 5))
        
        # 저장/되돌리기 버튼들
        save_frame = ttk.Frame(control_frame)
        save_frame.pack(side=tk.RIGHT)
        
        ttk.Button(save_frame, text="저장", command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(save_frame, text="되돌리기", command=self.reload_config).pack(side=tk.LEFT)
        
        # 수정 상태 표시
        self.modified_var = tk.StringVar(value="")
        ttk.Label(save_frame, textvariable=self.modified_var, foreground="red").pack(side=tk.LEFT, padx=(10, 0))
        
        # 메인 컨텐츠 프레임
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 좌측: 설정 트리
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(left_frame, text="설정 항목").pack(anchor=tk.W)
        
        # 트리뷰 생성
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.tree = ttk.Treeview(tree_frame, columns=("value",), show="tree headings")
        self.tree.heading("#0", text="키")
        self.tree.heading("value", text="값")
        self.tree.column("#0", width=300)
        self.tree.column("value", width=200)
        
        # 트리 스크롤바
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 트리 이벤트 바인딩
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # 우측: 값 편집
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        ttk.Label(right_frame, text="값 편집").pack(anchor=tk.W)
        
        # 값 편집 영역
        edit_frame = ttk.Frame(right_frame)
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 현재 키 표시
        self.current_key_var = tk.StringVar(value="선택된 항목 없음")
        ttk.Label(edit_frame, textvariable=self.current_key_var, 
                 font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # 값 입력 필드
        ttk.Label(edit_frame, text="값:").pack(anchor=tk.W)
        self.value_entry = tk.Text(edit_frame, width=30, height=10, wrap=tk.WORD)
        self.value_entry.pack(fill=tk.BOTH, expand=True, pady=(2, 5))
        self.value_entry.bind('<KeyRelease>', self.on_value_changed)
        
        # 편집 버튼들
        edit_buttons = ttk.Frame(edit_frame)
        edit_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(edit_buttons, text="적용", command=self.apply_value).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(edit_buttons, text="추가", command=self.add_new_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(edit_buttons, text="삭제", command=self.delete_key).pack(side=tk.LEFT)
        
        # JSON 유효성 검사 결과
        self.validation_var = tk.StringVar(value="")
        ttk.Label(edit_frame, textvariable=self.validation_var, 
                 foreground="red", wraplength=250).pack(anchor=tk.W, pady=(10, 0))
        
        # 하단 상태 바
        self.status_var = tk.StringVar(value="설정 관리자 준비")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # 초기 설정 파일 로드
        self.load_config_files()
        
        # 창 닫기 이벤트 처리
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_config_files(self):
        """config/ 폴더에서 설정 파일 목록 로드"""
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
                self.status_var.set("config/ 폴더가 생성되었습니다.")
                
            config_files = []
            for file in os.listdir(self.config_dir):
                if file.endswith('.json'):
                    config_files.append(file)
                    
            self.file_combo['values'] = sorted(config_files)
            
            if config_files and not self.current_file:
                self.file_combo.current(0)
                self.current_file = config_files[0]
                self.load_current_config()
                
            self.status_var.set(f"설정 파일 {len(config_files)}개 발견")
            
        except Exception as e:
            self.status_var.set(f"설정 파일 로드 오류: {str(e)}")
            
    def on_file_selected(self, event=None):
        """설정 파일 선택 시 처리"""
        if self.modified:
            result = messagebox.askyesnocancel("확인", 
                                             "변경사항이 있습니다. 저장하시겠습니까?")
            if result is True:
                self.save_config()
            elif result is None:
                return  # 취소
                
        selected = self.file_combo.get()
        if selected and selected != self.current_file:
            self.current_file = selected
            self.load_current_config()
            
    def load_current_config(self):
        """현재 선택된 설정 파일 로드"""
        if not self.current_file:
            return
            
        try:
            config_path = os.path.join(self.config_dir, self.current_file)
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                # 파일이 없으면 템플릿 사용
                self.config_data = self.config_templates.get(self.current_file, {})
                
            self.populate_tree()
            self.modified = False
            self.update_modified_status()
            self.status_var.set(f"설정 로드 완료: {self.current_file}")
            
        except Exception as e:
            messagebox.showerror("오류", f"설정 파일 로드 실패: {str(e)}")
            self.config_data = {}
            self.populate_tree()
            
    def populate_tree(self):
        """설정 데이터로 트리 채우기"""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 재귀적으로 트리 항목 추가
        self.add_tree_items("", self.config_data)
        
        # 모든 항목 펼치기
        self.expand_all_items()
        
    def add_tree_items(self, parent, data, prefix=""):
        """재귀적으로 트리 항목 추가"""
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, (dict, list)):
                    # 컨테이너 타입
                    item_id = self.tree.insert(parent, tk.END, text=key, 
                                             values=(f"[{type(value).__name__}]",))
                    self.add_tree_items(item_id, value, full_key)
                else:
                    # 값 타입
                    display_value = str(value)
                    if len(display_value) > 50:
                        display_value = display_value[:47] + "..."
                    self.tree.insert(parent, tk.END, text=key, values=(display_value,))
                    
        elif isinstance(data, list):
            for i, value in enumerate(data):
                full_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
                
                if isinstance(value, (dict, list)):
                    item_id = self.tree.insert(parent, tk.END, text=f"[{i}]", 
                                             values=(f"[{type(value).__name__}]",))
                    self.add_tree_items(item_id, value, full_key)
                else:
                    display_value = str(value)
                    if len(display_value) > 50:
                        display_value = display_value[:47] + "..."
                    self.tree.insert(parent, tk.END, text=f"[{i}]", values=(display_value,))
                    
    def expand_all_items(self):
        """모든 트리 항목 펼치기"""
        def expand_item(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expand_item(child)
                
        for item in self.tree.get_children():
            expand_item(item)
            
    def on_tree_select(self, event=None):
        """트리 항목 선택 시 처리"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        item = selected_items[0]
        key_path = self.get_key_path(item)
        value = self.get_value_by_path(key_path)
        
        self.current_key_var.set(key_path)
        
        # 값 표시
        self.value_entry.delete(1.0, tk.END)
        if value is not None:
            if isinstance(value, (dict, list)):
                display_value = json.dumps(value, indent=2, ensure_ascii=False)
            else:
                display_value = str(value)
            self.value_entry.insert(tk.END, display_value)
            
    def on_tree_double_click(self, event=None):
        """트리 항목 더블클릭 시 편집 모드"""
        self.on_tree_select()
        self.value_entry.focus_set()
        
    def get_key_path(self, item):
        """트리 항목의 전체 키 경로 반환"""
        path_parts = []
        current = item
        
        while current:
            text = self.tree.item(current)["text"]
            path_parts.insert(0, text)
            current = self.tree.parent(current)
            
        return ".".join(path_parts)
        
    def get_value_by_path(self, path):
        """키 경로로 값 찾기"""
        if not path:
            return self.config_data
            
        parts = path.split(".")
        current = self.config_data
        
        try:
            for part in parts:
                if part.startswith("[") and part.endswith("]"):
                    # 배열 인덱스
                    index = int(part[1:-1])
                    current = current[index]
                else:
                    # 객체 키
                    current = current[part]
            return current
        except (KeyError, IndexError, TypeError):
            return None
            
    def set_value_by_path(self, path, value):
        """키 경로로 값 설정"""
        if not path:
            return False
            
        parts = path.split(".")
        current = self.config_data
        
        try:
            # 마지막 키까지 이동
            for part in parts[:-1]:
                if part.startswith("[") and part.endswith("]"):
                    index = int(part[1:-1])
                    current = current[index]
                else:
                    current = current[part]
                    
            # 마지막 키에 값 설정
            last_part = parts[-1]
            if last_part.startswith("[") and last_part.endswith("]"):
                index = int(last_part[1:-1])
                current[index] = value
            else:
                current[last_part] = value
                
            return True
        except (KeyError, IndexError, TypeError, ValueError):
            return False
            
    def on_value_changed(self, event=None):
        """값 변경 시 처리"""
        self.validate_json()
        
    def validate_json(self):
        """JSON 유효성 검사"""
        try:
            content = self.value_entry.get(1.0, tk.END).strip()
            if content:
                json.loads(content)
            self.validation_var.set("")
            return True
        except json.JSONDecodeError as e:
            self.validation_var.set(f"JSON 오류: {str(e)}")
            return False
        except Exception as e:
            self.validation_var.set(f"오류: {str(e)}")
            return False
            
    def apply_value(self):
        """현재 편집 중인 값 적용"""
        key_path = self.current_key_var.get()
        if key_path == "선택된 항목 없음":
            messagebox.showwarning("경고", "편집할 항목을 선택하세요.")
            return
            
        if not self.validate_json():
            messagebox.showerror("오류", "JSON 형식이 올바르지 않습니다.")
            return
            
        try:
            content = self.value_entry.get(1.0, tk.END).strip()
            
            # JSON 파싱 시도
            try:
                value = json.loads(content)
            except json.JSONDecodeError:
                # JSON이 아니면 문자열로 처리
                value = content
                
            if self.set_value_by_path(key_path, value):
                self.populate_tree()
                self.modified = True
                self.update_modified_status()
                self.status_var.set(f"값 적용됨: {key_path}")
            else:
                messagebox.showerror("오류", "값 적용에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"값 적용 실패: {str(e)}")
            
    def add_new_key(self):
        """새 키 추가"""
        dialog = tk.Toplevel(self.window)
        dialog.title("새 키 추가")
        dialog.geometry("400x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 키 이름 입력
        ttk.Label(dialog, text="키 이름:").pack(pady=5)
        key_entry = ttk.Entry(dialog, width=40)
        key_entry.pack(pady=5)
        
        # 값 입력
        ttk.Label(dialog, text="값 (JSON 형식):").pack(pady=5)
        value_text = tk.Text(dialog, width=40, height=5)
        value_text.pack(pady=5)
        
        # 버튼
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def add_key():
            key_name = key_entry.get().strip()
            value_content = value_text.get(1.0, tk.END).strip()
            
            if not key_name:
                messagebox.showwarning("경고", "키 이름을 입력하세요.")
                return
                
            try:
                # JSON 파싱
                try:
                    value = json.loads(value_content) if value_content else ""
                except json.JSONDecodeError:
                    value = value_content
                    
                # 현재 선택된 위치에 추가
                selected_items = self.tree.selection()
                if selected_items:
                    parent_path = self.get_key_path(selected_items[0])
                    parent_value = self.get_value_by_path(parent_path)
                    
                    if isinstance(parent_value, dict):
                        parent_value[key_name] = value
                    else:
                        messagebox.showwarning("경고", "선택된 항목이 객체가 아닙니다.")
                        return
                else:
                    # 루트에 추가
                    self.config_data[key_name] = value
                    
                self.populate_tree()
                self.modified = True
                self.update_modified_status()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("오류", f"키 추가 실패: {str(e)}")
                
        ttk.Button(button_frame, text="추가", command=add_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def delete_key(self):
        """선택된 키 삭제"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("경고", "삭제할 항목을 선택하세요.")
            return
            
        key_path = self.get_key_path(selected_items[0])
        
        result = messagebox.askyesno("확인", f"'{key_path}' 키를 삭제하시겠습니까?")
        if result:
            try:
                # 부모에서 키 삭제
                parts = key_path.split(".")
                if len(parts) == 1:
                    # 루트 키 삭제
                    if parts[0] in self.config_data:
                        del self.config_data[parts[0]]
                else:
                    # 중첩 키 삭제
                    parent_path = ".".join(parts[:-1])
                    parent_value = self.get_value_by_path(parent_path)
                    last_key = parts[-1]
                    
                    if isinstance(parent_value, dict) and last_key in parent_value:
                        del parent_value[last_key]
                    elif isinstance(parent_value, list):
                        index = int(last_key[1:-1])  # [0] -> 0
                        del parent_value[index]
                        
                self.populate_tree()
                self.modified = True
                self.update_modified_status()
                self.status_var.set(f"키 삭제됨: {key_path}")
                
            except Exception as e:
                messagebox.showerror("오류", f"키 삭제 실패: {str(e)}")
                
    def save_config(self):
        """현재 설정 저장"""
        if not self.current_file:
            messagebox.showwarning("경고", "저장할 파일이 선택되지 않았습니다.")
            return
            
        try:
            config_path = os.path.join(self.config_dir, self.current_file)
            
            # 백업 생성
            if os.path.exists(config_path):
                backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(config_path, backup_path)
                
            # 설정 저장
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                
            self.modified = False
            self.update_modified_status()
            self.status_var.set(f"설정 저장 완료: {self.current_file}")
            
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 실패: {str(e)}")
            
    def reload_config(self):
        """설정 다시 로드"""
        if self.modified:
            result = messagebox.askyesno("확인", "변경사항이 손실됩니다. 계속하시겠습니까?")
            if not result:
                return
                
        self.load_current_config()
        
    def refresh_files(self):
        """설정 파일 목록 새로고침"""
        current_selection = self.current_file
        self.load_config_files()
        
        # 이전 선택 유지
        if current_selection and current_selection in self.file_combo['values']:
            self.file_combo.set(current_selection)
            self.current_file = current_selection
            
    def create_new_file(self):
        """새 설정 파일 생성"""
        filename = tk.simpledialog.askstring("새 파일", "파일 이름을 입력하세요 (.json 확장자 포함):")
        if filename:
            if not filename.endswith('.json'):
                filename += '.json'
                
            config_path = os.path.join(self.config_dir, filename)
            
            if os.path.exists(config_path):
                messagebox.showwarning("경고", "이미 존재하는 파일입니다.")
                return
                
            try:
                # 빈 설정 파일 생성
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)
                    
                self.refresh_files()
                
                # 새 파일 선택
                if filename in self.file_combo['values']:
                    self.file_combo.set(filename)
                    self.current_file = filename
                    self.load_current_config()
                    
                self.status_var.set(f"새 파일 생성됨: {filename}")
                
            except Exception as e:
                messagebox.showerror("오류", f"파일 생성 실패: {str(e)}")
                
    def backup_config(self):
        """설정 백업"""
        if not self.current_file:
            messagebox.showwarning("경고", "백업할 파일이 선택되지 않았습니다.")
            return
            
        try:
            source_path = os.path.join(self.config_dir, self.current_file)
            if not os.path.exists(source_path):
                messagebox.showwarning("경고", "백업할 파일이 존재하지 않습니다.")
                return
                
            backup_filename = f"{self.current_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = filedialog.asksaveasfilename(
                title="백업 파일 저장",
                initialfilename=backup_filename,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if backup_path:
                shutil.copy2(source_path, backup_path)
                messagebox.showinfo("성공", f"백업이 완료되었습니다:\n{backup_path}")
                
        except Exception as e:
            messagebox.showerror("오류", f"백업 실패: {str(e)}")
            
    def restore_config(self):
        """설정 복원"""
        backup_path = filedialog.askopenfilename(
            title="복원할 백업 파일 선택",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if backup_path:
            try:
                # 백업 파일 유효성 검사
                with open(backup_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    
                result = messagebox.askyesno("확인", 
                                           f"현재 설정을 백업 파일로 복원하시겠습니까?\n{backup_path}")
                if result:
                    if not self.current_file:
                        messagebox.showwarning("경고", "복원할 대상 파일을 선택하세요.")
                        return
                        
                    target_path = os.path.join(self.config_dir, self.current_file)
                    shutil.copy2(backup_path, target_path)
                    
                    self.load_current_config()
                    messagebox.showinfo("성공", "설정이 복원되었습니다.")
                    
            except Exception as e:
                messagebox.showerror("오류", f"복원 실패: {str(e)}")
                
    def update_modified_status(self):
        """수정 상태 표시 업데이트"""
        if self.modified:
            self.modified_var.set("* 수정됨")
        else:
            self.modified_var.set("")
            
    def on_closing(self):
        """창 닫기 시 처리"""
        if self.modified:
            result = messagebox.askyesnocancel("확인", 
                                             "변경사항이 있습니다. 저장하시겠습니까?")
            if result is True:
                self.save_config()
            elif result is None:
                return  # 취소
                
        if self.window:
            self.window.destroy()
            
    def show(self):
        """설정 관리자 창 표시"""
        if not self.window:
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()


def main():
    """독립 실행 테스트"""
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기
    
    config_manager = ConfigManager()
    config_manager.show()
    
    root.mainloop()


if __name__ == "__main__":
    main()