#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 메시지 미리보기 GUI (스탠드얼론)
메시지 템플릿 미리보기 및 테스트 인터페이스

주요 기능:
- 📱 메시지 템플릿 실시간 미리보기
- 🎨 다양한 메시지 타입 테스트
- 📝 사용자 정의 데이터 입력
- 💾 미리보기 결과 저장

Requirements: 2.1, 2.3 구현 (GUI 미리보기 기능)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from .message_template_engine import MessageTemplateEngine, MessageType, MessagePriority
except ImportError:
    from message_template_engine import MessageTemplateEngine, MessageType, MessagePriority


class MessagePreviewGUI:
    """메시지 미리보기 GUI 클래스"""
    
    def __init__(self, parent: Optional[tk.Widget] = None):
        """메시지 미리보기 GUI 초기화"""
        self.parent = parent
        self.engine = MessageTemplateEngine()
        
        # GUI 창 생성
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("🎨 POSCO 메시지 템플릿 미리보기")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # 현재 선택된 메시지 타입
        self.current_message_type = MessageType.DEPLOYMENT_SUCCESS
        
        # 샘플 데이터
        self.sample_data = self._get_default_sample_data()
        
        self._create_widgets()
        self._update_preview()
        
        print("🎨 메시지 미리보기 GUI 초기화 완료")
    
    def _create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 창 크기 조절 설정
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 제목
        title_label = ttk.Label(main_frame, text="🏭 POSCO 메시지 템플릿 미리보기", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 왼쪽 패널: 설정
        settings_frame = ttk.LabelFrame(main_frame, text="📋 설정", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 메시지 타입 선택
        ttk.Label(settings_frame, text="메시지 타입:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.message_type_var = tk.StringVar(value=self.current_message_type.value)
        message_type_combo = ttk.Combobox(settings_frame, textvariable=self.message_type_var,
                                         values=[mt.value for mt in MessageType],
                                         state="readonly", width=25)
        message_type_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        message_type_combo.bind('<<ComboboxSelected>>', self._on_message_type_changed)
        
        # 샘플 데이터 편집
        ttk.Label(settings_frame, text="샘플 데이터:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.data_text = scrolledtext.ScrolledText(settings_frame, width=40, height=15,
                                                  font=('Consolas', 9))
        self.data_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 버튼 프레임
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(button_frame, text="🔄 미리보기 새로고침", 
                  command=self._update_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📁 데이터 로드", 
                  command=self._load_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="💾 데이터 저장", 
                  command=self._save_data).pack(side=tk.LEFT)
        
        # 기본 샘플 버튼들
        sample_frame = ttk.Frame(settings_frame)
        sample_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(sample_frame, text="✅ 성공 샘플", 
                  command=lambda: self._load_sample('success')).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(sample_frame, text="❌ 실패 샘플", 
                  command=lambda: self._load_sample('failure')).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(sample_frame, text="📊 데이터 샘플", 
                  command=lambda: self._load_sample('data')).pack(side=tk.LEFT)
        
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.rowconfigure(3, weight=1)
        
        # 오른쪽 패널: 미리보기
        preview_frame = ttk.LabelFrame(main_frame, text="👀 미리보기", padding="10")
        preview_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 미리보기 텍스트
        self.preview_text = scrolledtext.ScrolledText(preview_frame, width=50, height=25,
                                                     font=('Arial', 10), wrap=tk.WORD)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 미리보기 버튼들
        preview_button_frame = ttk.Frame(preview_frame)
        preview_button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(preview_button_frame, text="📋 클립보드 복사", 
                  command=self._copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preview_button_frame, text="📄 파일로 저장", 
                  command=self._save_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preview_button_frame, text="📨 테스트 전송", 
                  command=self._test_send).pack(side=tk.LEFT)
        
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # 상태바
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 초기 데이터 로드
        self._load_sample_data()
    
    def _get_default_sample_data(self) -> Dict[str, Dict[str, Any]]:
        """기본 샘플 데이터 반환"""
        return {
            'success': {
                'deployment_id': 'deploy_20250901_143022',
                'start_time': '2025-09-01T14:30:22',
                'end_time': '2025-09-01T14:32:45',
                'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 
                                  'merge_main', 'commit_changes', 'push_remote', 'pages_verification'],
                'github_pages_accessible': True
            },
            'failure': {
                'deployment_id': 'deploy_20250901_143022',
                'error_message': 'Git 푸시 중 인증 실패',
                'steps_completed': ['status_check', 'backup_creation', 'branch_switch'],
                'rollback_performed': True
            },
            'data': {
                'kospi': '2,485.67',
                'kospi_change': 15.23,
                'exchange_rate': '1,342.50',
                'exchange_change': -2.80,
                'posco_stock': '285,000',
                'posco_change': 5000,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'status': {
                'total_deployments': 127,
                'success_rate': 94.5,
                'last_success': '2025-09-01 14:32:45',
                'avg_deployment_time': 2.3,
                'github_accessible': True,
                'data_collection_active': True,
                'webhook_active': True,
                'next_update': '2025-09-01 16:00:00'
            }
        }
    
    def _on_message_type_changed(self, event=None):
        """메시지 타입 변경 시 처리"""
        try:
            self.current_message_type = MessageType(self.message_type_var.get())
            self._load_appropriate_sample()
            self._update_preview()
            self.status_var.set(f"메시지 타입 변경: {self.current_message_type.value}")
        except ValueError:
            messagebox.showerror("오류", "잘못된 메시지 타입입니다.")
    
    def _load_appropriate_sample(self):
        """메시지 타입에 맞는 샘플 데이터 로드"""
        if self.current_message_type == MessageType.DEPLOYMENT_SUCCESS:
            self._load_sample('success')
        elif self.current_message_type == MessageType.DEPLOYMENT_FAILURE:
            self._load_sample('failure')
        elif self.current_message_type == MessageType.DATA_UPDATE:
            self._load_sample('data')
        elif self.current_message_type == MessageType.SYSTEM_STATUS:
            self._load_sample('status')
        else:
            # 기본 데이터
            self._load_sample('success')
    
    def _load_sample(self, sample_type: str):
        """샘플 데이터 로드"""
        if sample_type in self.sample_data:
            data_json = json.dumps(self.sample_data[sample_type], 
                                 ensure_ascii=False, indent=2)
            self.data_text.delete(1.0, tk.END)
            self.data_text.insert(1.0, data_json)
            self._update_preview()
            self.status_var.set(f"{sample_type} 샘플 데이터 로드됨")
    
    def _load_sample_data(self):
        """초기 샘플 데이터 로드"""
        self._load_appropriate_sample()
    
    def _update_preview(self):
        """미리보기 업데이트"""
        try:
            # 현재 데이터 파싱
            data_json = self.data_text.get(1.0, tk.END).strip()
            if not data_json:
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, "❌ 데이터가 없습니다.")
                return
            
            data = json.loads(data_json)
            
            # 메시지 생성
            message = self.engine.generate_message(self.current_message_type, data)
            
            # 미리보기 텍스트 생성
            preview_content = f"""📱 메시지 미리보기
{'='*50}

🏷️ 제목: {message['title']}

📝 내용:
{message['body']}

{'='*50}
📊 메타데이터:
• 메시지 타입: {message['message_type']}
• 우선순위: {message['priority']}
• 색상: {message['color']}
• 생성 시간: {message['timestamp']}

{'='*50}
💡 이 미리보기는 실제 웹훅 메시지와 동일한 형식입니다.
"""
            
            # 미리보기 표시
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_content)
            
            self.status_var.set("미리보기 업데이트 완료")
            
        except json.JSONDecodeError as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"❌ JSON 파싱 오류:\n{str(e)}\n\n올바른 JSON 형식으로 입력해주세요.")
            self.status_var.set("JSON 파싱 오류")
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"❌ 미리보기 생성 오류:\n{str(e)}")
            self.status_var.set(f"오류: {str(e)}")
    
    def _load_data(self):
        """파일에서 데이터 로드"""
        try:
            file_path = filedialog.askopenfilename(
                title="샘플 데이터 파일 선택",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data_json = json.dumps(data, ensure_ascii=False, indent=2)
                self.data_text.delete(1.0, tk.END)
                self.data_text.insert(1.0, data_json)
                self._update_preview()
                self.status_var.set(f"데이터 로드 완료: {file_path}")
                
        except Exception as e:
            messagebox.showerror("오류", f"데이터 로드 실패:\n{str(e)}")
            self.status_var.set("데이터 로드 실패")
    
    def _save_data(self):
        """현재 데이터를 파일로 저장"""
        try:
            data_json = self.data_text.get(1.0, tk.END).strip()
            if not data_json:
                messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
                return
            
            # JSON 유효성 검사
            json.loads(data_json)
            
            file_path = filedialog.asksaveasfilename(
                title="샘플 데이터 저장",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(data_json)
                
                self.status_var.set(f"데이터 저장 완료: {file_path}")
                messagebox.showinfo("완료", "데이터가 성공적으로 저장되었습니다.")
                
        except json.JSONDecodeError:
            messagebox.showerror("오류", "올바른 JSON 형식이 아닙니다.")
        except Exception as e:
            messagebox.showerror("오류", f"데이터 저장 실패:\n{str(e)}")
            self.status_var.set("데이터 저장 실패")
    
    def _copy_to_clipboard(self):
        """미리보기 내용을 클립보드에 복사"""
        try:
            preview_content = self.preview_text.get(1.0, tk.END).strip()
            if preview_content:
                self.window.clipboard_clear()
                self.window.clipboard_append(preview_content)
                self.status_var.set("클립보드에 복사됨")
                messagebox.showinfo("완료", "미리보기 내용이 클립보드에 복사되었습니다.")
            else:
                messagebox.showwarning("경고", "복사할 내용이 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"클립보드 복사 실패:\n{str(e)}")
    
    def _save_preview(self):
        """미리보기 내용을 파일로 저장"""
        try:
            preview_content = self.preview_text.get(1.0, tk.END).strip()
            if not preview_content:
                messagebox.showwarning("경고", "저장할 내용이 없습니다.")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="미리보기 저장",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(preview_content)
                
                self.status_var.set(f"미리보기 저장 완료: {file_path}")
                messagebox.showinfo("완료", "미리보기가 성공적으로 저장되었습니다.")
                
        except Exception as e:
            messagebox.showerror("오료", f"미리보기 저장 실패:\n{str(e)}")
            self.status_var.set("미리보기 저장 실패")
    
    def _test_send(self):
        """테스트 메시지 전송 (시뮬레이션)"""
        try:
            data_json = self.data_text.get(1.0, tk.END).strip()
            if not data_json:
                messagebox.showwarning("경고", "전송할 데이터가 없습니다.")
                return
            
            data = json.loads(data_json)
            message = self.engine.generate_message(self.current_message_type, data)
            
            # 실제로는 웹훅 전송을 시뮬레이션
            result = messagebox.askyesno(
                "테스트 전송 확인",
                f"다음 메시지를 테스트 전송하시겠습니까?\n\n"
                f"제목: {message['title']}\n"
                f"타입: {message['message_type']}\n"
                f"우선순위: {message['priority']}\n\n"
                f"※ 실제 웹훅은 전송되지 않습니다."
            )
            
            if result:
                # 테스트 전송 시뮬레이션
                self.status_var.set("테스트 전송 완료 (시뮬레이션)")
                messagebox.showinfo("완료", 
                    "테스트 전송이 완료되었습니다.\n"
                    "실제 환경에서는 웹훅으로 메시지가 전송됩니다.")
            
        except json.JSONDecodeError:
            messagebox.showerror("오류", "올바른 JSON 형식이 아닙니다.")
        except Exception as e:
            messagebox.showerror("오류", f"테스트 전송 실패:\n{str(e)}")
    
    def show(self):
        """GUI 표시"""
        self.window.mainloop()
    
    def destroy(self):
        """GUI 종료"""
        self.window.destroy()


def main():
    """메인 함수 - 독립 실행용"""
    print("🎨 POSCO 메시지 미리보기 GUI 시작...")
    
    app = MessagePreviewGUI()
    app.show()
    
    print("👋 POSCO 메시지 미리보기 GUI 종료")


if __name__ == "__main__":
    main()