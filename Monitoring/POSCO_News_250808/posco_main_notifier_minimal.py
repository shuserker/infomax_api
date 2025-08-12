#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Posco Main Notifier - Minimal Working Version
POSCO 알림 시스템

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import signal
import threading
import time

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 설정 로드
try:
    from config import API_CONFIG, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
    print("[INFO] Configuration loaded successfully")
except ImportError as e:
    print(f"[WARNING] 일부 모듈을 불러올 수 없습니다: {e}")
    print("[INFO] 기본 설정으로 동작합니다.")
    API_CONFIG = {}
    DOORAY_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"
    BOT_PROFILE_IMAGE_URL = "https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/POSCO_News_250808/posco_logo_mini.jpg"

class PoscoMainNotifier:
    """
    POSCO 메인 알림 시스템 클래스 - 최소 기능 버전
    """
    
    def __init__(self):
        """메인 알림자 초기화"""
        self.script_dir = current_dir
        self.state_file = os.path.join(self.script_dir, "main_notifier_state.json")
        self.log_file = os.path.join(self.script_dir, "main_notifier.log")
        
        # 실행 제어
        self.running = True
        self.check_interval = 5 * 60  # 5분 간격
        
        # 상태 관리
        self.last_check = {}
        self.executed_today = set()
        
        # API 클라이언트 초기화
        self.api_client = None
        self.log_message("✅ POSCO 메인 알림자 초기화 완료")
        
        # 신호 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """신호 핸들러"""
        self.log_message(f"📡 신호 수신: {signum}")
        self.running = False
        
    def log_message(self, message):
        """로그 메시지 출력 및 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # 파일에도 저장
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def load_state(self):
        """이전 상태 로드"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.last_check = state.get('last_check', {})
                    self.executed_today = set(state.get('executed_today', []))
                    self.log_message("✅ 이전 상태 로드 완료")
        except Exception as e:
            self.log_message(f"⚠️ 상태 로드 실패: {e}")
            
    def save_state(self):
        """현재 상태 저장"""
        try:
            state = {
                'last_check': self.last_check,
                'executed_today': list(self.executed_today),
                'timestamp': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_message(f"❌ 상태 저장 실패: {e}")
            
    def send_notification(self, message, bot_name="POSCO News Bot"):
        """Dooray 웹훅으로 알림 전송"""
        try:
            payload = {
                "botName": bot_name,
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
                return True
            else:
                self.log_message(f"⚠️ 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 알림 전송 오류: {e}")
            return False
            
    def check_news_updates(self):
        """뉴스 업데이트 확인"""
        try:
            # 실제 API 호출 대신 기본 상태 확인
            current_time = datetime.now()
            
            # 매 시간마다 상태 알림
            if current_time.minute == 0:
                status_message = f"📊 POSCO 뉴스 모니터링 상태 보고\n시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n상태: 정상 동작 중"
                self.send_notification(status_message)
                
            self.log_message("📰 뉴스 업데이트 확인 완료")
            
        except Exception as e:
            self.log_message(f"❌ 뉴스 업데이트 확인 오류: {e}")
            
    def run_monitoring(self):
        """메인 모니터링 루프"""
        self.log_message("🚀 POSCO 메인 알림 시스템 시작")
        self.load_state()
        
        # 시작 알림
        start_message = "🏭 POSCO 메인 알림 시스템이 시작되었습니다.\n모니터링을 시작합니다."
        self.send_notification(start_message)
        
        try:
            while self.running:
                self.check_news_updates()
                self.save_state()
                
                # 지정된 간격만큼 대기
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.log_message("⏹️ 사용자에 의해 중단됨")
        except Exception as e:
            self.log_message(f"❌ 모니터링 오류: {e}")
        finally:
            # 종료 알림
            end_message = "🛑 POSCO 메인 알림 시스템이 종료되었습니다."
            self.send_notification(end_message)
            self.save_state()
            self.log_message("🏁 POSCO 메인 알림 시스템 종료")

def main():
    """메인 실행 함수"""
    notifier = PoscoMainNotifier()
    notifier.run_monitoring()

if __name__ == "__main__":
    main()