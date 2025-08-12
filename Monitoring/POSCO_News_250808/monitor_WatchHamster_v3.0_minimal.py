#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Watchhamster V3.0 - Minimal Working Version
POSCO 모니터링 시스템

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import psutil
import time

# 출력 버퍼링 해제 - 실시간 로그 출력을 위해
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 환경 변수로도 출력 버퍼링 비활성화
os.environ['PYTHONUNBUFFERED'] = '1'

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 설정 로드
try:
    from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
    print("[INFO] Configuration loaded successfully")
except ImportError as e:
    print(f"[WARNING] Configuration import failed: {e}")
    # 기본 설정 사용
    API_CONFIG = {}
    DOORAY_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"
    BOT_PROFILE_IMAGE_URL = "https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/POSCO_News_250808/posco_logo_mini.jpg"

class WatchHamsterV3Monitor:
    """WatchHamster v3.0 모니터링 클래스"""
    
    def __init__(self):
        """모니터 초기화"""
        self.script_dir = current_dir
        self.running = True
        self.check_interval = 60  # 1분 간격
        
        print("[INFO] WatchHamster v3.0 Monitor 초기화 완료")
        
    def log_message(self, message):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def send_notification(self, message):
        """알림 전송"""
        try:
            payload = {
                "botName": "WatchHamster v3.0",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": message
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 알림 전송 성공")
            else:
                self.log_message(f"⚠️ 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 알림 전송 오류: {e}")
            
    def check_system_status(self):
        """시스템 상태 확인"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            self.log_message(f"📊 시스템 상태 - CPU: {cpu_percent}%, 메모리: {memory_percent}%, 디스크: {disk_percent}%")
            
            # 임계값 확인
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                self.send_notification(f"⚠️ 시스템 리소스 경고\nCPU: {cpu_percent}%\n메모리: {memory_percent}%\n디스크: {disk_percent}%")
                
        except Exception as e:
            self.log_message(f"❌ 시스템 상태 확인 오류: {e}")
            
    def run_monitoring(self):
        """모니터링 실행"""
        self.log_message("🚀 WatchHamster v3.0 모니터링 시작")
        self.send_notification("🐹 WatchHamster v3.0 모니터링이 시작되었습니다.")
        
        try:
            while self.running:
                self.check_system_status()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.log_message("⏹️ 사용자에 의해 중단됨")
        except Exception as e:
            self.log_message(f"❌ 모니터링 오류: {e}")
        finally:
            self.send_notification("🛑 WatchHamster v3.0 모니터링이 중지되었습니다.")
            self.log_message("🏁 WatchHamster v3.0 모니터링 종료")

def main():
    """메인 실행 함수"""
    monitor = WatchHamsterV3Monitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    main()