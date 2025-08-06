#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 간단 뉴스 모니터

제어센터에서 사용하는 간단한 뉴스 모니터링 시스템
복잡한 ProcessManager 없이 기본적인 뉴스 모니터링만 수행

주요 기능:
- 실시간 뉴스 모니터링
- Dooray 알림 전송
- 간단한 상태 체크

작성자: AI Assistant
최종 수정: 2025-08-06
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime, timedelta
import psutil

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config import WATCHHAMSTER_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
    from core import PoscoNewsAPIClient
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class SimpleNewsMonitor:
    """
    간단한 뉴스 모니터 클래스
    """
    
    def __init__(self):
        """
        모니터 초기화
        """
        self.script_dir = current_dir
        self.log_file = os.path.join(self.script_dir, "simple_monitor.log")
        self.realtime_script = os.path.join(self.script_dir, "realtime_news_monitor.py")
        self.realtime_process = None
        self.last_status_check = datetime.now()
        self.status_check_interval = 300  # 5분
        
        print("🐹 POSCO 간단 뉴스 모니터 초기화 완료")
    
    def log(self, message):
        """로그 메시지 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        print(log_message, flush=True)
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def send_notification(self, message, is_error=False):
        """Dooray 알림 전송"""
        try:
            payload = {
                "botName": "POSCO 뉴스 모니터 🐹",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": message
            }
            
            response = requests.post(WATCHHAMSTER_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                self.log(f"✅ 알림 전송 성공: {message[:50]}...")
                return True
            else:
                self.log(f"❌ 알림 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ 알림 전송 오류: {e}")
            return False
    
    def is_realtime_monitor_running(self):
        """실시간 모니터 실행 상태 확인"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] in ['python', 'python3']:
                        cmdline = proc.info['cmdline']
                        if cmdline and 'realtime_news_monitor.py' in ' '.join(cmdline):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            self.log(f"❌ 프로세스 상태 확인 오류: {e}")
            return False
    
    def start_realtime_monitor(self):
        """실시간 뉴스 모니터 시작"""
        try:
            if self.is_realtime_monitor_running():
                self.log("✅ 실시간 뉴스 모니터가 이미 실행 중입니다.")
                return True
            
            self.log("🚀 실시간 뉴스 모니터 시작 중...")
            
            if os.path.exists(self.realtime_script):
                self.realtime_process = subprocess.Popen(
                    [sys.executable, self.realtime_script],
                    cwd=self.script_dir
                )
                
                time.sleep(3)  # 프로세스 시작 대기
                
                if self.is_realtime_monitor_running():
                    self.log("✅ 실시간 뉴스 모니터 시작 성공")
                    return True
                else:
                    self.log("❌ 실시간 뉴스 모니터 시작 실패")
                    return False
            else:
                self.log(f"❌ 실시간 모니터 스크립트를 찾을 수 없습니다: {self.realtime_script}")
                return False
                
        except Exception as e:
            self.log(f"❌ 실시간 모니터 시작 오류: {e}")
            return False
    
    def run(self):
        """메인 실행 루프"""
        self.log("🐹 POSCO 간단 뉴스 모니터 시작")
        
        # 시작 알림
        self.send_notification(
            f"POSCO 뉴스 모니터 시작\n\n"
            f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"모니터링 모드: 간단 모드\n"
            f"상태 체크: {self.status_check_interval//60}분 간격"
        )
        
        # 실시간 모니터 시작 (선택적)
        realtime_started = self.start_realtime_monitor()
        if not realtime_started:
            self.log("⚠️ 실시간 모니터 시작 실패 - 기본 모니터링 모드로 계속 진행")
        
        try:
            while True:
                current_time = datetime.now()
                
                # 정기 상태 체크
                if (current_time - self.last_status_check).total_seconds() >= self.status_check_interval:
                    if self.is_realtime_monitor_running():
                        self.log("✅ 실시간 뉴스 모니터 정상 작동 중")
                    else:
                        self.log("⚠️ 실시간 뉴스 모니터 중단됨")
                        # 재시작 시도는 하지 않고 기본 모니터링 계속
                    
                    # 기본 상태 알림 (2시간마다)
                    if current_time.hour % 2 == 0 and current_time.minute == 0:
                        self.send_notification(
                            f"POSCO 뉴스 모니터 상태 보고\n\n"
                            f"시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"상태: 정상 작동 중\n"
                            f"실시간 모니터: {'작동 중' if self.is_realtime_monitor_running() else '중단됨'}"
                        )
                    
                    self.last_status_check = current_time
                
                # 30초 대기
                time.sleep(30)
                
        except KeyboardInterrupt:
            self.log("🛑 간단 뉴스 모니터 중단 요청 받음")
            self.send_notification(
                f"POSCO 뉴스 모니터 중단\n\n"
                f"중단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception as e:
            self.log(f"❌ 간단 뉴스 모니터 오류: {e}")
            self.send_notification(
                f"POSCO 뉴스 모니터 오류\n\n"
                f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"오류: {str(e)}",
                is_error=True
            )

if __name__ == "__main__":
    monitor = SimpleNewsMonitor()
    monitor.run()