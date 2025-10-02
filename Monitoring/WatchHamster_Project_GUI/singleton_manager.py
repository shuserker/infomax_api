#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Singleton Manager - 중복 실행 방지 시스템
WatchHamster GUI의 중복 실행을 방지합니다.

주요 기능:
- 🔒 단일 인스턴스 보장
- 🚫 중복 실행 방지
- 📡 기존 인스턴스와 통신
"""

import os
import sys
import time
import socket
import threading
import json
from typing import Optional, Dict, Any


class SingletonManager:
    """단일 인스턴스 관리자"""
    
    def __init__(self, app_name: str = "WatchHamster", port: int = 12345):
        self.app_name = app_name
        self.port = port
        self.lock_file = os.path.join(os.path.expanduser("~"), f".{app_name.lower()}_lock")
        self.socket_server = None
        self.is_primary = False
        self.running = False
        
    def is_already_running(self) -> bool:
        """다른 인스턴스가 실행 중인지 확인"""
        try:
            # 소켓으로 기존 인스턴스 확인
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            result = test_socket.connect_ex(('localhost', self.port))
            test_socket.close()
            
            if result == 0:
                print(f"[INFO] 기존 {self.app_name} 인스턴스가 실행 중입니다.")
                return True
            
            return False
            
        except Exception as e:
            print(f"[WARNING] 인스턴스 확인 오류: {e}")
            return False
    
    def acquire_lock(self) -> bool:
        """락 획득 시도"""
        try:
            if self.is_already_running():
                return False
            
            # 소켓 서버 시작
            self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_server.bind(('localhost', self.port))
            self.socket_server.listen(1)
            
            # 락 파일 생성
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            
            self.is_primary = True
            self.running = True
            
            # 통신 서버 시작
            self.start_communication_server()
            
            print(f"[LOCK] {self.app_name} 단일 인스턴스 락 획득 성공")
            return True
            
        except Exception as e:
            print(f"[ERROR] 락 획득 실패: {e}")
            return False
    
    def release_lock(self):
        """락 해제"""
        try:
            self.running = False
            
            if self.socket_server:
                self.socket_server.close()
                self.socket_server = None
            
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            
            self.is_primary = False
            print(f"[UNLOCK] {self.app_name} 단일 인스턴스 락 해제")
            
        except Exception as e:
            print(f"[WARNING] 락 해제 오류: {e}")
    
    def start_communication_server(self):
        """통신 서버 시작"""
        def server_loop():
            while self.running:
                try:
                    if not self.socket_server:
                        break
                    
                    self.socket_server.settimeout(1)
                    conn, addr = self.socket_server.accept()
                    
                    # 클라이언트 요청 처리
                    data = conn.recv(1024).decode('utf-8')
                    if data:
                        response = self.handle_client_request(data)
                        conn.send(response.encode('utf-8'))
                    
                    conn.close()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[WARNING] 통신 서버 오류: {e}")
                    break
        
        server_thread = threading.Thread(target=server_loop, daemon=True)
        server_thread.start()
    
    def handle_client_request(self, request: str) -> str:
        """클라이언트 요청 처리"""
        try:
            req_data = json.loads(request)
            action = req_data.get('action', '')
            
            if action == 'show_window':
                return json.dumps({'status': 'success', 'message': 'Window shown'})
            elif action == 'get_status':
                return json.dumps({'status': 'success', 'running': True})
            else:
                return json.dumps({'status': 'error', 'message': 'Unknown action'})
                
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def send_to_existing_instance(self, action: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """기존 인스턴스에 메시지 전송"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(('localhost', self.port))
            
            request = {
                'action': action,
                'data': data or {}
            }
            
            client_socket.send(json.dumps(request).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            client_socket.close()
            
            resp_data = json.loads(response)
            return resp_data.get('status') == 'success'
            
        except Exception as e:
            print(f"[WARNING] 기존 인스턴스 통신 실패: {e}")
            return False
    
    def show_existing_window(self) -> bool:
        """기존 창 표시 요청"""
        return self.send_to_existing_instance('show_window')
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.release_lock()


def prevent_duplicate_execution(app_name: str = "WatchHamster") -> bool:
    """중복 실행 방지 데코레이터용 함수"""
    singleton = SingletonManager(app_name)
    
    if singleton.is_already_running():
        print(f"[WARNING] {app_name}이 이미 실행 중입니다.")
        print("기존 창을 표시합니다...")
        
        # 기존 창 표시 시도
        if singleton.show_existing_window():
            print("[SUCCESS] 기존 창이 표시되었습니다.")
        else:
            print("[ERROR] 기존 창 표시에 실패했습니다.")
        
        return False
    
    # 락 획득 시도
    if not singleton.acquire_lock():
        print(f"[ERROR] {app_name} 락 획득에 실패했습니다.")
        return False
    
    # 전역 변수로 저장 (종료 시 해제용)
    globals()['_singleton_manager'] = singleton
    
    return True


def cleanup_singleton():
    """싱글톤 정리"""
    if '_singleton_manager' in globals():
        globals()['_singleton_manager'].release_lock()
        del globals()['_singleton_manager']


# 프로그램 종료 시 자동 정리
import atexit
atexit.register(cleanup_singleton)


if __name__ == "__main__":
    # 테스트
    print("[TEST] Singleton Manager 테스트")
    
    with SingletonManager("TestApp") as singleton:
        if singleton.acquire_lock():
            print("[SUCCESS] 첫 번째 인스턴스 - 락 획득 성공")
            
            # 두 번째 인스턴스 시뮬레이션
            second_singleton = SingletonManager("TestApp")
            if second_singleton.is_already_running():
                print("[SUCCESS] 두 번째 인스턴스 - 중복 실행 감지됨")
            
            time.sleep(2)
        else:
            print("[ERROR] 락 획득 실패")