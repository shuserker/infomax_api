#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Log Viewer Component - 성능 최적화된 로그 뷰어
대용량 로그 파일 처리 및 실시간 모니터링 최적화

주요 기능:
- 📊 대용량 로그 표시 성능 최적화
- ⚡ 청크 단위 로그 로딩
- 🔄 실시간 모니터링 데이터 업데이트 최적화
- 💾 메모리 효율적 로그 캐싱

Requirements: 6.4, 5.1, 5.2 구현
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import json
from datetime import datetime
import threading
import time
import sys
from typing import List, Optional, Callable, Dict, Any

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from core.performance_optimizer import get_performance_optimizer
except ImportError:
    print("⚠️ 성능 최적화 시스템을 사용할 수 없습니다")


class OptimizedLogViewer:
    """성능 최적화된 로그 뷰어 - 대용량 로그 처리 특화"""
    
    def __init__(self, parent=None, logs_dir: Optional[str] = None):
        self.parent = parent
        self.logs_dir = logs_dir or os.path.join(os.path.dirname(parent_dir), 'logs')
        self.window = None
        
        # 성능 최적화 시스템
        try:
            self.performance_optimizer = get_performance_optimizer()
            self.use_optimization = True
        except:
            self.performance_optimizer = None
            self.use_optimization = False
            print("⚠️ 최적화된 로그 뷰어: 성능 최적화 없이 실행")
        
        # 로그 표시 최적화 설정
        self.max_display_lines = 2000  # 한 번에 표시할 최대 라인 수
        self.chunk_size = 500  # 청크 단위 로딩 크기
        self.virtual_scroll_threshold = 5000  # 가상 스크롤 임계값
        
        # 현재 상태
        self.current_file = None
        self.current_lines = []
        self.displayed_lines = []
        self.scroll_position = 0
        self.total_lines = 0
        
        # 자동 새로고침
        self.auto_refresh = True
        self.refresh_interval = 2.0  # 초
        self.refresh_thread = None
        self.running = False
        
        # 필터링
        self.filter_text = ""
        self.filter_case_sensitive = False
        self.filtered_lines = []
        
        # 성능 메트릭
        self.load_time = 0
        self.filter_time = 0
        self.display_time = 0
        
    def create_window(self):
        """최적화된 로그 뷰어 창 생성 (완전 구현)"""
        try:
            print("🚀 최적화된 로그 뷰어 창 생성 시작")
            
            # 창 생성 및 기본 설정
            self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
            self.window.title("🚀 Optimized Log Viewer - 성능 최적화")
            self.window.geometry("1200x800")
            self.window.minsize(800, 600)
            
            # 창 아이콘 설정 (가능한 경우)
            try:
                # 기본 아이콘 설정 시도
                self.window.iconname("LogViewer")
            except:
                pass
            
            print("✅ 기본 창 설정 완료")
            
            # 메인 프레임 생성
            main_frame = ttk.Frame(self.window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            print("✅ 메인 프레임 생성 완료")
            
            # 상단 컨트롤 프레임 생성
            print("📊 컨트롤 패널 생성 중...")
            self.create_control_panel(main_frame)
            print("✅ 컨트롤 패널 생성 완료")
            
            # 로그 표시 영역 생성
            print("📝 로그 표시 영역 생성 중...")
            self.create_log_display(main_frame)
            print("✅ 로그 표시 영역 생성 완료")
            
            # 하단 상태 바 생성
            print("📊 상태 바 생성 중...")
            self.create_status_bar(main_frame)
            print("✅ 상태 바 생성 완료")
            
            # 키보드 단축키 설정
            print("⌨️ 키보드 단축키 설정 중...")
            self._setup_keyboard_shortcuts()
            print("✅ 키보드 단축키 설정 완료")
            
            # 초기 로그 파일 로드
            print("📂 초기 로그 파일 로드 중...")
            self.load_log_files()
            print("✅ 로그 파일 로드 완료")
            
            # 자동 새로고침 시작
            print("🔄 자동 새로고침 시작 중...")
            self.start_auto_refresh()
            print("✅ 자동 새로고침 시작 완료")
            
            # 창 닫기 이벤트 처리
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # 창 상태 확인
            window_info = {
                'size': self.window.geometry(),
                'title': self.window.title(),
                'state': self.window.state()
            }
            print(f"📊 창 정보: {window_info}")
            
            print("🎉 최적화된 로그 뷰어 초기화 완료")
            
        except Exception as e:
            print(f"❌ 로그 뷰어 창 생성 오류: {e}")
            if hasattr(self, 'window') and self.window:
                try:
                    self.window.destroy()
                except:
                    pass
            raise
    
    def _setup_keyboard_shortcuts(self):
        """키보드 단축키 설정"""
        try:
            # 전역 키보드 바인딩
            self.window.bind('<Control-f>', lambda e: self.filter_entry.focus() if hasattr(self, 'filter_entry') else None)
            self.window.bind('<Control-r>', lambda e: self.refresh_logs() if hasattr(self, 'refresh_logs') else None)
            self.window.bind('<F5>', lambda e: self.refresh_logs() if hasattr(self, 'refresh_logs') else None)
            self.window.bind('<Control-l>', lambda e: self.clear_filter() if hasattr(self, 'clear_filter') else None)
            self.window.bind('<Escape>', lambda e: self.clear_filter() if hasattr(self, 'clear_filter') else None)
            
            print("✅ 키보드 단축키 등록: Ctrl+F, Ctrl+R, F5, Ctrl+L, Esc")
            
        except Exception as e:
            print(f"❌ 키보드 단축키 설정 오류: {e}")
    
    def create_control_panel(self, parent):
        """컨트롤 패널 생성"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 첫 번째 행: 파일 선택 및 기본 컨트롤
        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        # 로그 파일 선택
        ttk.Label(row1, text="로그 파일:").pack(side=tk.LEFT, padx=(0, 5))
        self.file_combo = ttk.Combobox(row1, width=30, state="readonly")
        self.file_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_selected)
        
        # 기본 컨트롤 버튼들
        ttk.Button(row1, text="새로고침", command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="맨 아래로", command=self.scroll_to_bottom).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="맨 위로", command=self.scroll_to_top).pack(side=tk.LEFT, padx=(0, 5))
        
        # 자동 새로고침 체크박스
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row1, text="자동 새로고침", 
                       variable=self.auto_refresh_var,
                       command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=(10, 0))
        
        # 두 번째 행: 필터링 및 고급 옵션
        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=(0, 5))
        
        # 필터링
        ttk.Label(row2, text="필터:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_entry = ttk.Entry(row2, width=30)
        self.filter_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.filter_entry.bind('<KeyRelease>', self.on_filter_changed)
        
        ttk.Button(row2, text="필터 적용", command=self.apply_filter).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row2, text="필터 지우기", command=self.clear_filter).pack(side=tk.LEFT, padx=(0, 10))
        
        # 대소문자 구분
        self.case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2, text="대소문자 구분", 
                       variable=self.case_sensitive_var,
                       command=self.apply_filter).pack(side=tk.LEFT, padx=(0, 10))
        
        # 표시 옵션
        ttk.Label(row2, text="표시 라인:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_lines_var = tk.StringVar(value=str(self.max_display_lines))
        max_lines_spinbox = ttk.Spinbox(row2, from_=100, to=10000, width=8, 
                                       textvariable=self.max_lines_var,
                                       command=self.update_display_settings)
        max_lines_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        
        # 세 번째 행: 성능 정보
        row3 = ttk.Frame(control_frame)
        row3.pack(fill=tk.X)
        
        self.performance_label = ttk.Label(row3, text="성능: 로드 0ms | 필터 0ms | 표시 0ms", 
                                         font=("TkDefaultFont", 8), foreground="gray")
        self.performance_label.pack(side=tk.LEFT)
        
        # 메모리 사용량
        self.memory_label = ttk.Label(row3, text="메모리: 0MB", 
                                    font=("TkDefaultFont", 8), foreground="gray")
        self.memory_label.pack(side=tk.RIGHT)
    
    def create_log_display(self, parent):
        """로그 표시 영역 생성"""
        display_frame = ttk.Frame(parent)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # 로그 텍스트 영역 (최적화된 설정)
        self.log_text = scrolledtext.ScrolledText(
            display_frame, 
            wrap=tk.NONE,  # 가로 스크롤 허용
            font=('Consolas', 9),
            state=tk.DISABLED,  # 편집 방지
            cursor="arrow"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤 이벤트 바인딩
        self.log_text.bind('<MouseWheel>', self.on_mouse_wheel)
        self.log_text.bind('<Button-4>', self.on_mouse_wheel)
        self.log_text.bind('<Button-5>', self.on_mouse_wheel)
        
        # 키보드 단축키
        self.log_text.bind('<Control-f>', lambda e: self.filter_entry.focus())
        self.log_text.bind('<Control-r>', lambda e: self.refresh_logs())
        self.log_text.bind('<End>', lambda e: self.scroll_to_bottom())
        self.log_text.bind('<Home>', lambda e: self.scroll_to_top())
    
    def create_status_bar(self, parent):
        """상태 바 생성"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 상태 정보
        self.status_var = tk.StringVar(value="로그 뷰어 준비")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 라인 정보
        self.line_info_var = tk.StringVar(value="라인: 0/0")
        line_info_label = ttk.Label(status_frame, textvariable=self.line_info_var, 
                                  relief=tk.SUNKEN, anchor=tk.E, width=15)
        line_info_label.pack(side=tk.RIGHT)
    
    def load_log_files(self):
        """로그 파일 목록 로드"""
        try:
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)
                self.status_var.set("logs/ 폴더가 생성되었습니다.")
                return
            
            log_files = []
            for file in os.listdir(self.logs_dir):
                if file.endswith(('.log', '.json', '.txt')):
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
        """현재 선택된 로그 파일 로드 (완전 최적화 구현)"""
        if not self.current_file:
            print("⚠️ 선택된 로그 파일이 없습니다")
            return
        
        def _load_optimized():
            start_time = time.time()
            
            try:
                log_path = os.path.join(self.logs_dir, self.current_file)
                print(f"📂 로그 파일 로드 시작: {self.current_file}")
                
                # 파일 존재 확인
                if not os.path.exists(log_path):
                    error_msg = f"로그 파일을 찾을 수 없습니다: {self.current_file}"
                    print(f"❌ {error_msg}")
                    self._update_display([error_msg])
                    self.status_var.set(error_msg)
                    return
                
                # 파일 크기 및 정보 확인
                file_size = os.path.getsize(log_path)
                file_modified = os.path.getmtime(log_path)
                print(f"📊 파일 정보: 크기 {file_size:,}bytes, 수정시간 {time.ctime(file_modified)}")
                
                # 파일 접근 권한 확인
                if not os.access(log_path, os.R_OK):
                    error_msg = f"로그 파일 읽기 권한이 없습니다: {self.current_file}"
                    print(f"❌ {error_msg}")
                    self._update_display([error_msg])
                    self.status_var.set(error_msg)
                    return
                
                # 성능 최적화된 로딩
                if self.use_optimization:
                    print("⚡ 성능 최적화 로딩 사용")
                    lines = self._load_with_optimization(log_path)
                else:
                    print("📊 기본 로딩 방식 사용")
                    lines = self._load_without_optimization(log_path)
                
                # 로드 결과 검증
                if not lines:
                    print("⚠️ 빈 파일이거나 로드 실패")
                    lines = ["파일이 비어있거나 읽을 수 없습니다."]
                
                self.current_lines = lines
                self.total_lines = len(lines)
                
                print(f"✅ 로그 로드 완료: {self.total_lines:,}라인")
                
                # 필터 적용
                print("🔍 필터 적용 시작")
                self.apply_filter()
                print("✅ 필터 적용 완료")
                
                # 로드 시간 기록 및 성능 메트릭 업데이트
                self.load_time = (time.time() - start_time) * 1000
                print(f"⏱️ 로드 시간: {self.load_time:.1f}ms")
                
                if hasattr(self, '_update_performance_display'):
                    self._update_performance_display()
                
                # 상태 업데이트
                status_msg = f"로그 로드 완료: {self.current_file} ({self.total_lines:,}라인, {self.load_time:.1f}ms)"
                self.status_var.set(status_msg)
                print(f"✅ {status_msg}")
                
                # 메모리 사용량 확인
                try:
                    import psutil
                    memory_usage = psutil.virtual_memory().percent
                    print(f"📊 메모리 사용률: {memory_usage:.1f}%")
                except:
                    pass
                
            except Exception as e:
                error_msg = f"로그 로드 오류: {str(e)}"
                print(f"❌ {error_msg}")
                self._update_display([error_msg])
                self.status_var.set(f"로그 로드 실패: {self.current_file}")
                
                # 상세 오류 로깅
                import traceback
                print(f"📋 상세 오류 정보:\n{traceback.format_exc()}")
        
        # 백그라운드에서 로드
        try:
            if self.use_optimization and hasattr(self, 'performance_optimizer'):
                print("🚀 백그라운드 작업으로 스케줄링")
                self.performance_optimizer.schedule_background_task(_load_optimized)
            else:
                print("🔄 별도 스레드에서 실행")
                threading.Thread(target=_load_optimized, daemon=True).start()
        except Exception as e:
            print(f"❌ 백그라운드 로드 스케줄링 실패: {e}")
            # 폴백: 직접 실행
            _load_optimized()
    
    def _load_with_optimization(self, log_path: str) -> List[str]:
        """성능 최적화를 사용한 로그 로드 (완전 구현)"""
        try:
            file_size = os.path.getsize(log_path)
            print(f"📁 파일 크기: {file_size / 1024 / 1024:.1f}MB")
            
            if file_size > 10 * 1024 * 1024:  # 10MB 이상
                print(f"🚀 대용량 파일 tail 방식 로드")
                # 대용량 파일: tail 방식 사용
                lines = self.performance_optimizer.get_log_file_tail(log_path, self.max_display_lines * 2)
                print(f"✅ Tail 로드 완료: {len(lines):,} 라인")
                return lines
            elif file_size > 1024 * 1024:  # 1MB 이상
                print(f"📊 중간 크기 파일 청크 로드")
                # 중간 크기: 청크 단위 로드
                lines = self.performance_optimizer.process_large_log_file(
                    log_path, lambda x: x, max_lines=self.max_display_lines * 2
                )
                print(f"✅ 청크 로드 완료: {len(lines):,} 라인")
                return lines
            else:
                print(f"⚡ 소용량 파일 전체 로드")
                # 작은 파일: 전체 로드
                lines = self._load_without_optimization(log_path)
                print(f"✅ 전체 로드 완료: {len(lines):,} 라인")
                return lines
                
        except Exception as e:
            print(f"❌ 최적화 로드 실패: {e}")
            # 폴백: 기본 방식으로 로드
            try:
                return self._load_without_optimization(log_path)
            except Exception as fallback_error:
                print(f"❌ 폴백 로드도 실패: {fallback_error}")
                return [f"로그 로드 실패: {str(e)}"]
    
    def _load_without_optimization(self, log_path: str) -> List[str]:
        """기본 방식으로 로그 로드"""
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            if self.current_file.endswith('.json'):
                try:
                    data = json.load(f)
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                    return content.split('\n')
                except json.JSONDecodeError:
                    f.seek(0)
                    return f.read().split('\n')
            else:
                return f.read().split('\n')
    
    def apply_filter(self):
        """필터 적용 (완전 구현)"""
        try:
            start_time = time.time()
            
            filter_text = self.filter_entry.get().strip()
            case_sensitive = self.case_sensitive_var.get()
            
            print(f"🔍 필터 적용: '{filter_text}' (대소문자 구분: {case_sensitive})")
            
            if not filter_text:
                self.filtered_lines = self.current_lines[:]
                print(f"📄 필터 없음: {len(self.filtered_lines):,} 라인")
            else:
                self.filtered_lines = []
                search_text = filter_text if case_sensitive else filter_text.lower()
                
                # 정규식 지원
                import re
                try:
                    if filter_text.startswith('regex:'):
                        pattern = re.compile(filter_text[6:], 0 if case_sensitive else re.IGNORECASE)
                        for line in self.current_lines:
                            if pattern.search(line):
                                self.filtered_lines.append(line)
                    else:
                        # 일반 텍스트 검색
                        for line in self.current_lines:
                            line_to_search = line if case_sensitive else line.lower()
                            if search_text in line_to_search:
                                self.filtered_lines.append(line)
                except re.error as e:
                    print(f"⚠️ 정규식 오류: {e}")
                    # 일반 텍스트 검색으로 폴백
                    for line in self.current_lines:
                        line_to_search = line if case_sensitive else line.lower()
                        if search_text in line_to_search:
                            self.filtered_lines.append(line)
                
                print(f"🎯 필터 결과: {len(self.filtered_lines):,}/{len(self.current_lines):,} 라인")
            
            # 표시할 라인 수 제한
            max_lines = int(self.max_lines_var.get())
            if len(self.filtered_lines) > max_lines:
                self.displayed_lines = self.filtered_lines[-max_lines:]  # 최근 라인들
                print(f"📊 표시 제한: {len(self.displayed_lines):,}/{len(self.filtered_lines):,} 라인")
            else:
                self.displayed_lines = self.filtered_lines[:]
            
            # 필터 시간 기록
            self.filter_time = (time.time() - start_time) * 1000
            
            # 화면 업데이트
            self._update_display(self.displayed_lines)
            self._update_performance_display()
            
            # 라인 정보 업데이트
            self.line_info_var.set(f"라인: {len(self.displayed_lines):,}/{len(self.filtered_lines):,}")
            
        except Exception as e:
            print(f"❌ 필터 적용 오류: {e}")
            # 오류 시 전체 라인 표시
            self.filtered_lines = self.current_lines[:]
            self.displayed_lines = self.filtered_lines[:int(self.max_lines_var.get())]
            self._update_display(self.displayed_lines)
        
        # 라인 정보 업데이트
        self.line_info_var.set(f"라인: {len(self.displayed_lines):,}/{len(self.filtered_lines):,}")
    
    def _update_display(self, lines: List[str]):
        """화면 표시 업데이트 (완전 구현)"""
        def _update():
            try:
                start_time = time.time()
                
                print(f"🖥️ 화면 업데이트 시작: {len(lines):,} 라인")
                
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete(1.0, tk.END)
                
                # 대용량 텍스트 효율적 삽입
                if len(lines) > 1000:
                    print(f"📊 대용량 텍스트 청크 처리 모드")
                    # 청크 단위로 삽입
                    chunk_size = 100
                    total_chunks = (len(lines) + chunk_size - 1) // chunk_size
                    
                    for i in range(0, len(lines), chunk_size):
                        chunk = lines[i:i+chunk_size]
                        text_chunk = '\n'.join(chunk) + '\n'
                        self.log_text.insert(tk.END, text_chunk)
                        
                        # UI 응답성 유지
                        if i % 500 == 0:
                            progress = (i // chunk_size + 1) / total_chunks * 100
                            print(f"📈 처리 진행률: {progress:.1f}%")
                            self.log_text.update_idletasks()
                else:
                    print(f"⚡ 일괄 텍스트 삽입 모드")
                    # 한 번에 삽입
                    text_content = '\n'.join(lines)
                    self.log_text.insert(tk.END, text_content)
                
                self.log_text.config(state=tk.DISABLED)
                self.log_text.see(tk.END)
                
                # 표시 시간 기록
                self.display_time = (time.time() - start_time) * 1000
                print(f"✅ 화면 업데이트 완료: {self.display_time:.1f}ms")
                self._update_performance_display()
                
            except Exception as e:
                print(f"❌ 화면 업데이트 오류: {e}")
                # 오류 시 기본 메시지 표시
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, f"화면 업데이트 오류: {str(e)}")
                self.log_text.config(state=tk.DISABLED)
        
        # UI 업데이트 스케줄링
        if self.use_optimization:
            self.performance_optimizer.schedule_ui_update(_update)
        else:
            self.window.after(0, _update)
    
    def _update_performance_display(self):
        """성능 정보 표시 업데이트"""
        perf_text = f"성능: 로드 {self.load_time:.0f}ms | 필터 {self.filter_time:.0f}ms | 표시 {self.display_time:.0f}ms"
        self.performance_label.config(text=perf_text)
        
        # 메모리 사용량 (성능 최적화 시스템에서 가져오기)
        if self.use_optimization:
            metrics = self.performance_optimizer.get_performance_metrics()
            memory_mb = metrics.get('memory_usage_mb', 0)
            self.memory_label.config(text=f"메모리: {memory_mb:.1f}MB")
    
    def on_filter_changed(self, event=None):
        """필터 텍스트 변경 시 처리 (디바운싱 적용, 완전 구현)"""
        try:
            filter_text = self.filter_entry.get().strip()
            print(f"🔍 필터 변경 감지: '{filter_text}'")
            
            if self.use_optimization:
                # 디바운싱 적용 (연속 입력 시 마지막 입력만 처리)
                print(f"⏱️ 디바운싱 적용 (0.5초 지연)")
                debounced_filter = self.performance_optimizer.debounce_function(
                    self.apply_filter, delay=0.5
                )
                debounced_filter()
            else:
                print(f"⚡ 즉시 필터 적용")
                # 즉시 적용
                self.apply_filter()
                
            # 필터 히스토리 관리 (최근 10개)
            if not hasattr(self, 'filter_history'):
                self.filter_history = []
            
            if filter_text and filter_text not in self.filter_history:
                self.filter_history.insert(0, filter_text)
                if len(self.filter_history) > 10:
                    self.filter_history = self.filter_history[:10]
                print(f"📝 필터 히스토리 업데이트: {len(self.filter_history)}개")
                
        except Exception as e:
            print(f"❌ 필터 변경 처리 오류: {e}")
    
    def clear_filter(self):
        """필터 지우기"""
        self.filter_entry.delete(0, tk.END)
        self.apply_filter()
    
    def scroll_to_bottom(self):
        """맨 아래로 스크롤"""
        self.log_text.see(tk.END)
    
    def scroll_to_top(self):
        """맨 위로 스크롤"""
        self.log_text.see(1.0)
    
    def on_mouse_wheel(self, event):
        """마우스 휠 이벤트 처리"""
        # 기본 스크롤 동작 유지
        return "break"
    
    def update_display_settings(self):
        """표시 설정 업데이트"""
        try:
            self.max_display_lines = int(self.max_lines_var.get())
            self.apply_filter()  # 설정 변경 후 다시 적용
        except ValueError:
            pass
    
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
            self.refresh_thread = threading.Thread(target=self._auto_refresh_worker, daemon=True)
            self.refresh_thread.start()
    
    def stop_auto_refresh(self):
        """자동 새로고침 중지"""
        self.running = False
    
    def _auto_refresh_worker(self):
        """자동 새로고침 워커 스레드"""
        while self.running:
            try:
                if self.auto_refresh and self.current_file:
                    # 성능 최적화: 스로틀링 적용
                    if self.use_optimization:
                        throttled_refresh = self.performance_optimizer.throttle_function(
                            self.load_current_log, interval=self.refresh_interval
                        )
                        throttled_refresh()
                    else:
                        self.load_current_log()
                
                time.sleep(self.refresh_interval)
            except Exception as e:
                print(f"자동 새로고침 오류: {e}")
                break
    
    def refresh_logs(self):
        """로그 파일 목록 및 내용 새로고침"""
        current_selection = self.current_file
        self.load_log_files()
        
        # 이전 선택 유지
        if current_selection and current_selection in self.file_combo['values']:
            self.file_combo.set(current_selection)
            self.current_file = current_selection
            self.load_current_log()
    
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
    
    log_viewer = OptimizedLogViewer()
    log_viewer.show()
    
    root.mainloop()


if __name__ == "__main__":
    main()