#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 16 구현 검증 테스트
POSCO 뉴스 전용 GUI 패널 구현 검증

검증 항목:
- 메시지 미리보기 기능
- 수동 전송 기능  
- 배포 진행률 프로그레스 바
- 상태 표시 기능

Requirements: 6.4, 5.1, 5.2 검증
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import time
import threading
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from Posco_News_Mini_Final_GUI.posco_gui_manager import PoscoGUIManager
    print("✅ PoscoGUIManager 임포트 성공")
except ImportError as e:
    print(f"❌ PoscoGUIManager 임포트 실패: {e}")
    sys.exit(1)


class Task16TestGUI:
    """Task 16 구현 검증 테스트 GUI"""
    
    def __init__(self):
        """테스트 GUI 초기화"""
        self.root = tk.Tk()
        self.root.title("🧪 Task 16 구현 검증 - POSCO GUI 패널")
        self.root.geometry("1200x800")
        
        # 테스트 결과 추적
        self.test_results = {
            'message_preview_tab': False,
            'message_type_selection': False,
            'message_data_input': False,
            'preview_update': False,
            'manual_send': False,
            'progress_bars': False,
            'status_display': False
        }
        
        self.setup_test_ui()
        self.run_verification_tests()
    
    def setup_test_ui(self):
        """테스트 UI 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, 
                               text="🧪 Task 16 구현 검증 - POSCO 뉴스 전용 GUI 패널", 
                               font=("TkDefaultFont", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 테스트 상태 프레임
        status_frame = ttk.LabelFrame(main_frame, text="검증 상태", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = tk.Text(status_frame, height=8, font=("Consolas", 9))
        status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # POSCO GUI 매니저 프레임
        posco_frame = ttk.LabelFrame(main_frame, text="POSCO GUI 매니저", padding="10")
        posco_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        try:
            # POSCO GUI 매니저 인스턴스 생성
            self.posco_gui = PoscoGUIManager(posco_frame)
            self.log_status("✅ POSCO GUI 매니저 초기화 성공")
        except Exception as e:
            self.log_status(f"❌ POSCO GUI 매니저 초기화 실패: {e}")
            return
        
        # 테스트 제어 버튼
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(control_frame, text="🔍 기능 검증", 
                  command=self.verify_functionality).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🧪 메시지 미리보기 테스트", 
                  command=self.test_message_preview).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="📊 진행률 테스트", 
                  command=self.test_progress_bars).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="📋 결과 요약", 
                  command=self.show_test_summary).pack(side=tk.RIGHT)
    
    def log_status(self, message):
        """상태 로그 추가"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_verification_tests(self):
        """초기 검증 테스트 실행"""
        self.log_status("🚀 Task 16 구현 검증 시작")
        
        # 1초 후 자동 검증 시작
        self.root.after(1000, self.verify_functionality)
    
    def verify_functionality(self):
        """기능 검증"""
        self.log_status("🔍 POSCO GUI 기능 검증 중...")
        
        try:
            # 1. 메시지 미리보기 탭 존재 확인
            if hasattr(self.posco_gui, 'notebook'):
                tab_count = self.posco_gui.notebook.index("end")
                self.log_status(f"📋 탭 개수: {tab_count}")
                
                # 탭 이름 확인
                for i in range(tab_count):
                    tab_text = self.posco_gui.notebook.tab(i, "text")
                    self.log_status(f"   탭 {i+1}: {tab_text}")
                    
                    if "메시지" in tab_text or "미리보기" in tab_text:
                        self.test_results['message_preview_tab'] = True
                        self.log_status("✅ 메시지 미리보기 탭 발견")
            
            # 2. 메시지 관련 변수 확인
            message_vars = [
                'message_type_var', 'message_priority_var', 
                'kospi_preview_var', 'exchange_preview_var', 
                'posco_stock_preview_var', 'webhook_url_var'
            ]
            
            for var_name in message_vars:
                if hasattr(self.posco_gui, var_name):
                    self.test_results['message_data_input'] = True
                    self.log_status(f"✅ {var_name} 변수 존재")
                else:
                    self.log_status(f"⚠️ {var_name} 변수 없음")
            
            # 3. 진행률 관련 요소 확인
            progress_elements = [
                'overall_progress', 'overall_progress_var',
                'current_step_var', 'branch_progress'
            ]
            
            for element_name in progress_elements:
                if hasattr(self.posco_gui, element_name):
                    self.test_results['progress_bars'] = True
                    self.log_status(f"✅ {element_name} 진행률 요소 존재")
                else:
                    self.log_status(f"⚠️ {element_name} 진행률 요소 없음")
            
            # 4. 메서드 존재 확인
            required_methods = [
                'update_message_preview', 'send_manual_message',
                'update_deployment_progress', 'reset_deployment_progress'
            ]
            
            for method_name in required_methods:
                if hasattr(self.posco_gui, method_name):
                    self.log_status(f"✅ {method_name} 메서드 존재")
                    if 'message' in method_name:
                        self.test_results['manual_send'] = True
                    if 'progress' in method_name:
                        self.test_results['status_display'] = True
                else:
                    self.log_status(f"❌ {method_name} 메서드 없음")
            
            self.log_status("🔍 기능 검증 완료")
            
        except Exception as e:
            self.log_status(f"❌ 기능 검증 중 오류: {e}")
    
    def test_message_preview(self):
        """메시지 미리보기 기능 테스트"""
        self.log_status("🧪 메시지 미리보기 기능 테스트 시작")
        
        try:
            # 메시지 미리보기 업데이트 메서드 테스트
            if hasattr(self.posco_gui, 'update_message_preview'):
                self.posco_gui.update_message_preview()
                self.test_results['preview_update'] = True
                self.log_status("✅ 메시지 미리보기 업데이트 성공")
            else:
                self.log_status("❌ update_message_preview 메서드 없음")
            
            # 샘플 데이터 로드 테스트
            if hasattr(self.posco_gui, 'load_sample_message_data'):
                self.posco_gui.load_sample_message_data()
                self.log_status("✅ 샘플 데이터 로드 성공")
            else:
                self.log_status("⚠️ load_sample_message_data 메서드 없음")
            
            # 메시지 타입 변경 테스트
            if hasattr(self.posco_gui, 'message_type_var'):
                original_type = self.posco_gui.message_type_var.get()
                self.posco_gui.message_type_var.set("deployment_success")
                self.log_status(f"✅ 메시지 타입 변경: {original_type} → deployment_success")
                self.test_results['message_type_selection'] = True
            
            self.log_status("🧪 메시지 미리보기 테스트 완료")
            
        except Exception as e:
            self.log_status(f"❌ 메시지 미리보기 테스트 중 오류: {e}")
    
    def test_progress_bars(self):
        """진행률 바 기능 테스트"""
        self.log_status("📊 진행률 바 기능 테스트 시작")
        
        try:
            # 진행률 초기화 테스트
            if hasattr(self.posco_gui, 'reset_deployment_progress'):
                self.posco_gui.reset_deployment_progress()
                self.log_status("✅ 진행률 초기화 성공")
            
            # 진행률 업데이트 테스트
            if hasattr(self.posco_gui, 'update_deployment_progress'):
                test_steps = [
                    ("초기화", 10, "시스템 준비 중"),
                    ("데이터 수집", 30, "POSCO 데이터 수집 중"),
                    ("HTML 생성", 50, "보고서 생성 중"),
                    ("배포 준비", 70, "GitHub Pages 준비 중"),
                    ("배포 실행", 90, "배포 진행 중")
                ]
                
                def update_progress_sequence():
                    for i, (step_name, progress, status) in enumerate(test_steps):
                        self.root.after(i * 1000, lambda s=step_name, p=progress, st=status: 
                                       self.posco_gui.update_deployment_progress(s, p, st))
                        self.root.after(i * 1000, lambda s=step_name, p=progress: 
                                       self.log_status(f"📊 진행률 업데이트: {s} - {p}%"))
                    
                    # 완료 처리
                    self.root.after(len(test_steps) * 1000, 
                                   lambda: self.posco_gui.complete_deployment_progress(True))
                    self.root.after(len(test_steps) * 1000, 
                                   lambda: self.log_status("✅ 진행률 완료 처리 성공"))
                
                update_progress_sequence()
                self.log_status("📊 진행률 업데이트 시퀀스 시작")
            
        except Exception as e:
            self.log_status(f"❌ 진행률 바 테스트 중 오류: {e}")
    
    def show_test_summary(self):
        """테스트 결과 요약 표시"""
        self.log_status("📋 Task 16 구현 검증 결과 요약")
        self.log_status("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        for test_name, result in self.test_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            self.log_status(f"{test_name}: {status}")
        
        self.log_status("=" * 50)
        self.log_status(f"전체 테스트: {total_tests}")
        self.log_status(f"통과한 테스트: {passed_tests}")
        self.log_status(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            self.log_status("🎉 Task 16 구현 완료! 모든 테스트 통과")
        elif passed_tests >= total_tests * 0.8:
            self.log_status("✅ Task 16 구현 대부분 완료 (80% 이상 통과)")
        else:
            self.log_status("⚠️ Task 16 구현 추가 작업 필요")
    
    def run(self):
        """테스트 GUI 실행"""
        self.root.mainloop()


def main():
    """메인 함수"""
    print("🧪 Task 16 구현 검증 테스트 시작")
    print("=" * 60)
    
    try:
        # 테스트 GUI 생성 및 실행
        test_gui = Task16TestGUI()
        test_gui.run()
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()