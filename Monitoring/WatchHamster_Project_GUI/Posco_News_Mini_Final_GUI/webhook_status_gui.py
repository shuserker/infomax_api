#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 메시지 전송 상태 GUI 모니터링
실시간 메시지 전송 상태 표시 및 미리보기

Requirements: 2.1, 2.2 - GUI에서 메시지 전송 상태 실시간 모니터링
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Callable
import json

try:
    from posco_main_notifier import PoscoMainNotifier
    from message_template_engine import MessageType, MessageTemplateEngine
except ImportError:
    print("❌ 필요한 모듈을 찾을 수 없습니다. posco_main_notifier.py와 message_template_engine.py가 필요합니다.")
    exit(1)


class WebhookStatusGUI:
    """웹훅 메시지 전송 상태 GUI 클래스"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("POSCO 웹훅 메시지 전송 모니터")
        self.root.geometry("900x700")
        
        # POSCO 알림 시스템 초기화
        self.notifier = PoscoMainNotifier()
        self.message_engine = MessageTemplateEngine()
        
        # GUI 상태 변수
        self.is_sending = False
        self.current_progress = 0
        self.status_text = tk.StringVar(value="준비")
        self.progress_text = tk.StringVar(value="0%")
        
        # GUI 구성
        self.setup_gui()
        
        # 테스트용 웹훅 URL 설정
        self.notifier.webhook_url = "https://httpbin.org/post"
        
        print("🎨 웹훅 상태 GUI 초기화 완료")
    
    def setup_gui(self):
        """GUI 구성 요소 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🏭 POSCO 웹훅 메시지 전송 모니터", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 왼쪽 패널: 메시지 타입 선택
        left_frame = ttk.LabelFrame(main_frame, text="메시지 타입 선택", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.message_type_var = tk.StringVar(value="deployment_success")
        
        message_types = [
            ("배포 성공", "deployment_success"),
            ("배포 실패", "deployment_failure"),
            ("배포 시작", "deployment_start"),
            ("시스템 상태", "system_status"),
            ("데이터 업데이트", "data_update"),
            ("오류 알림", "error_alert")
        ]
        
        for i, (text, value) in enumerate(message_types):
            rb = ttk.Radiobutton(left_frame, text=text, variable=self.message_type_var, 
                                value=value, command=self.on_message_type_change)
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # 웹훅 URL 설정
        url_frame = ttk.Frame(left_frame)
        url_frame.grid(row=len(message_types), column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(url_frame, text="웹훅 URL:").grid(row=0, column=0, sticky=tk.W)
        self.webhook_url_var = tk.StringVar(value="https://httpbin.org/post")
        url_entry = ttk.Entry(url_frame, textvariable=self.webhook_url_var, width=30)
        url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 전송 버튼
        send_button = ttk.Button(left_frame, text="📤 메시지 전송", 
                                command=self.send_webhook_message)
        send_button.grid(row=len(message_types)+2, column=0, pady=(20, 0))
        
        # 중앙 패널: 진행 상태
        center_frame = ttk.LabelFrame(main_frame, text="전송 상태", padding="10")
        center_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 상태 표시
        ttk.Label(center_frame, text="현재 상태:").grid(row=0, column=0, sticky=tk.W)
        status_label = ttk.Label(center_frame, textvariable=self.status_text, 
                                font=('Arial', 10, 'bold'))
        status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 진행률 바
        ttk.Label(center_frame, text="진행률:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(center_frame, length=200, mode='determinate')
        self.progress_bar.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        # 진행률 텍스트
        progress_label = ttk.Label(center_frame, textvariable=self.progress_text)
        progress_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # 전송 결과
        ttk.Label(center_frame, text="전송 결과:").grid(row=3, column=0, sticky=tk.W, pady=(20, 0))
        self.result_text = scrolledtext.ScrolledText(center_frame, width=40, height=8)
        self.result_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 오른쪽 패널: 메시지 미리보기
        right_frame = ttk.LabelFrame(main_frame, text="메시지 미리보기", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        self.preview_text = scrolledtext.ScrolledText(right_frame, width=50, height=25)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 미리보기 업데이트 버튼
        preview_button = ttk.Button(right_frame, text="🔄 미리보기 업데이트", 
                                   command=self.update_preview)
        preview_button.grid(row=1, column=0, pady=(10, 0))
        
        # 로그 패널
        log_frame = ttk.LabelFrame(main_frame, text="실시간 로그", padding="10")
        log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=100, height=8)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 초기 미리보기 업데이트
        self.update_preview()
    
    def log_message(self, message: str):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, status: str, progress: int):
        """상태 업데이트 (콜백 함수)"""
        self.status_text.set(status)
        self.progress_text.set(f"{progress}%")
        self.progress_bar['value'] = progress
        self.current_progress = progress
        
        self.log_message(f"📊 {progress}%: {status}")
        self.root.update_idletasks()
    
    def on_message_type_change(self):
        """메시지 타입 변경 시 미리보기 업데이트"""
        self.update_preview()
    
    def update_preview(self):
        """메시지 미리보기 업데이트"""
        try:
            message_type_str = self.message_type_var.get()
            message_type = MessageType(message_type_str)
            
            # 테스트 데이터 생성
            test_data = self.generate_test_data(message_type_str)
            
            # 미리보기 생성
            preview = self.message_engine.preview_message(message_type, test_data)
            
            # 미리보기 텍스트 업데이트
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview)
            
            self.log_message(f"🔄 미리보기 업데이트: {message_type_str}")
            
        except Exception as e:
            self.log_message(f"❌ 미리보기 업데이트 실패: {e}")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"미리보기 생성 실패: {e}")
    
    def generate_test_data(self, message_type: str) -> Dict:
        """메시지 타입별 테스트 데이터 생성"""
        base_data = {
            'deployment_id': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'start_time': '2025-09-23T14:00:00',
            'end_time': '2025-09-23T14:02:30',
            'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 'merge_main'],
        }
        
        if message_type == "deployment_success":
            base_data.update({
                'success': True,
                'github_pages_accessible': True,
                'backup_created': True
            })
        elif message_type == "deployment_failure":
            base_data.update({
                'success': False,
                'error_message': '테스트 오류: Git 푸시 실패',
                'rollback_performed': True
            })
        elif message_type == "data_update":
            base_data.update({
                'kospi': '2,450.32',
                'kospi_change': '+15.20',
                'exchange_rate': '1,340.50',
                'exchange_change': '-2.30',
                'posco_stock': '285,000',
                'posco_change': '+5,000',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        elif message_type == "system_status":
            base_data.update({
                'total_deployments': 156,
                'success_rate': 94.2,
                'last_success': '2025-09-23 13:45:00',
                'avg_deployment_time': 2.3,
                'github_accessible': True,
                'data_collection_active': True,
                'webhook_active': True,
                'next_update': '2025-09-23 15:00:00'
            })
        elif message_type == "error_alert":
            base_data.update({
                'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error_type': '데이터베이스 연결 실패',
                'impact_scope': '데이터 수집 시스템',
                'error_details': 'Connection timeout after 30 seconds',
                'auto_recovery_status': '재시도 중',
                'estimated_recovery_time': '2-3분'
            })
        
        return base_data
    
    def send_webhook_message(self):
        """웹훅 메시지 전송 (별도 스레드에서 실행)"""
        if self.is_sending:
            messagebox.showwarning("경고", "이미 메시지 전송 중입니다.")
            return
        
        # 웹훅 URL 업데이트
        self.notifier.webhook_url = self.webhook_url_var.get()
        
        if not self.notifier.webhook_url:
            messagebox.showerror("오류", "웹훅 URL을 입력하세요.")
            return
        
        # 별도 스레드에서 전송
        threading.Thread(target=self._send_webhook_thread, daemon=True).start()
    
    def _send_webhook_thread(self):
        """웹훅 전송 스레드"""
        try:
            self.is_sending = True
            
            # 초기화
            self.result_text.delete(1.0, tk.END)
            self.update_status("전송 준비 중...", 0)
            
            # 메시지 타입 및 테스트 데이터
            message_type_str = self.message_type_var.get()
            message_type = MessageType(message_type_str)
            test_data = self.generate_test_data(message_type_str)
            
            self.log_message(f"🚀 웹훅 메시지 전송 시작: {message_type_str}")
            
            # 웹훅 전송
            webhook_result = self.notifier.send_direct_webhook(
                deployment_result=test_data,
                message_type=message_type,
                status_callback=self.update_status
            )
            
            # 결과 표시
            self._display_result(webhook_result)
            
            if webhook_result['success']:
                self.log_message("✅ 웹훅 메시지 전송 완료")
                self.update_status("전송 완료", 100)
            else:
                self.log_message(f"❌ 웹훅 메시지 전송 실패: {webhook_result.get('error_message', '알 수 없는 오류')}")
                self.update_status("전송 실패", 100)
            
        except Exception as e:
            self.log_message(f"❌ 전송 중 예외 발생: {e}")
            self.update_status("오류 발생", 0)
            self.result_text.insert(tk.END, f"오류 발생: {e}\n")
        
        finally:
            self.is_sending = False
    
    def _display_result(self, webhook_result: Dict):
        """전송 결과 표시"""
        result_info = f"""전송 결과: {'성공' if webhook_result['success'] else '실패'}
전송 시간: {webhook_result['timestamp']}
응답 코드: {webhook_result.get('webhook_response_code', 'N/A')}

"""
        
        if webhook_result.get('template_used'):
            template_info = webhook_result['template_used']
            result_info += f"""템플릿 정보:
- 타입: {template_info.get('type', 'N/A')}
- 우선순위: {template_info.get('priority', 'N/A')}
- 색상: {template_info.get('color', 'N/A')}

"""
        
        if webhook_result.get('message_sent'):
            result_info += f"""전송된 메시지:
{webhook_result['message_sent'][:500]}{'...' if len(webhook_result['message_sent']) > 500 else ''}

"""
        
        if webhook_result.get('error_message'):
            result_info += f"""오류 메시지:
{webhook_result['error_message']}
"""
        
        self.result_text.insert(tk.END, result_info)


def main():
    """메인 함수"""
    print("🎨 POSCO 웹훅 상태 GUI 시작...")
    
    root = tk.Tk()
    app = WebhookStatusGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 GUI 종료")
    except Exception as e:
        print(f"❌ GUI 실행 중 오류: {e}")


if __name__ == "__main__":
    main()