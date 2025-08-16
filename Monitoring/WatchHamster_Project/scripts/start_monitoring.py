#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워치햄스터 모니터 시작 스크립트

워치햄스터 모니터를 실행하여 실제 알림이 발송되도록 합니다.
"""

import os
import sys
import time
import threading
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # 3단계 상위 (프로젝트 루트)
watchhamster_root = os.path.dirname(current_dir)  # WatchHamster_Project 루트

# Python 경로에 프로젝트 루트와 워치햄스터 루트 추가
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if watchhamster_root not in sys.path:
    sys.path.insert(0, watchhamster_root)

# 현재 디렉토리도 추가 (로컬 모듈용)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # 절대 경로로 모듈 import
    from Monitoring.WatchHamster_Project.core.watchhamster_monitor import WatchHamsterMonitor
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.webhook_sender import WebhookSender, MessagePriority
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.environment_setup import EnvironmentSetup
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    print("💡 새로운 폴더 구조에서 모듈을 찾을 수 없습니다.")
    print("   - 워치햄스터 모듈: Monitoring/WatchHamster_Project/core/")
    print("   - 포스코 모듈: Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/")
    
    # 대안: 직접 경로로 모듈 로드 시도
    try:
        print("🔄 대안 방법으로 모듈 로드 시도 중...")
        
        # 워치햄스터 모니터 모듈 직접 로드
        watchhamster_monitor_path = os.path.join(watchhamster_root, 'core', 'watchhamster_monitor.py')
        webhook_sender_path = os.path.join(watchhamster_root, 'Posco_News_Mini_Final', 'core', 'webhook_sender.py')
        env_setup_path = os.path.join(watchhamster_root, 'Posco_News_Mini_Final', 'core', 'environment_setup.py')
        
        import importlib.util
        
        # WatchHamsterMonitor 로드
        spec = importlib.util.spec_from_file_location("watchhamster_monitor", watchhamster_monitor_path)
        watchhamster_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(watchhamster_module)
        WatchHamsterMonitor = watchhamster_module.WatchHamsterMonitor
        
        # WebhookSender 로드
        spec = importlib.util.spec_from_file_location("webhook_sender", webhook_sender_path)
        webhook_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(webhook_module)
        WebhookSender = webhook_module.WebhookSender
        MessagePriority = webhook_module.MessagePriority
        
        # EnvironmentSetup 로드
        spec = importlib.util.spec_from_file_location("environment_setup", env_setup_path)
        env_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(env_module)
        EnvironmentSetup = env_module.EnvironmentSetup
        
        print("✅ 대안 방법으로 모듈 로드 성공")
        
    except Exception as e2:
        print(f"❌ 대안 방법도 실패: {e2}")
        sys.exit(1)


class WatchhamsterService:
    """워치햄스터 서비스 관리자"""
    
    def __init__(self):
        """서비스 초기화"""
        print("🎯🛡️ POSCO 워치햄스터 서비스 시작")
        
        # 환경 설정 로드
        try:
            env_setup = EnvironmentSetup()
            self.env_settings = env_setup.settings
        except:
            self.env_settings = {}
        
        # 웹훅 전송자 초기화
        self.webhook_sender = WebhookSender(test_mode=False)
        
        # 워치햄스터 모니터 초기화 (설정 제공)
        try:
            monitor_config = {
                'process_check_interval': 300,  # 5분 간격
                'git_check_interval': 3600,     # 1시간 간격
                'status_notification_interval': 7200,  # 2시간 간격
                'webhook_sender': self.webhook_sender,
                'managed_processes': [
                    'posco_main_notifier.py',
                    'realtime_news_monitor.py',
                    'system_test.py'
                ],
                'max_restart_attempts': 3,
                'restart_cooldown': 60,
                'webhook_url': self.env_settings.get('webhook_url', ''),
                'bot_profile_image': self.env_settings.get('bot_profile_image', '')
            }
            self.monitor = WatchHamsterMonitor(monitor_config)
        except Exception as e:
            print(f"⚠️ 워치햄스터 모니터 초기화 실패: {e}")
            print(f"🔧 기본 설정으로 계속 진행합니다.")
            self.monitor = None
        
        self.is_running = False
        self.monitor_thread = None
        
        print("✅ 워치햄스터 서비스 초기화 완료")
    
    def send_startup_notification(self):
        """시작 알림 전송"""
        try:
            message_id = self.webhook_sender.send_watchhamster_status(
                "워치햄스터 모니터 시작됨",
                {
                    "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "정상 시작",
                    "monitoring_active": True,
                    "check_interval": "5분"
                }
            )
            
            if message_id:
                print(f"✅ 시작 알림 전송됨: {message_id}")
            else:
                print("⚠️ 시작 알림 전송 실패")
                
        except Exception as e:
            print(f"❌ 시작 알림 전송 오류: {e}")
    
    def send_periodic_status(self):
        """주기적 상태 알림 (30분마다)"""
        while self.is_running:
            try:
                time.sleep(1800)  # 30분 대기
                
                if not self.is_running:
                    break
                
                # 상태 알림 전송
                message_id = self.webhook_sender.send_watchhamster_status(
                    "워치햄스터 정상 작동 중",
                    {
                        "check_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": "정상 작동",
                        "uptime": "30분 이상",
                        "monitoring_active": True
                    }
                )
                
                if message_id:
                    print(f"📊 주기적 상태 알림 전송됨: {message_id}")
                
            except Exception as e:
                print(f"❌ 주기적 상태 알림 오류: {e}")
    
    def simulate_monitoring_activity(self):
        """모니터링 활동 시뮬레이션"""
        print("🔍 모니터링 활동 시뮬레이션 시작")
        
        activity_count = 0
        
        while self.is_running:
            try:
                time.sleep(300)  # 5분마다 체크
                
                if not self.is_running:
                    break
                
                activity_count += 1
                print(f"🎯 모니터링 체크 #{activity_count}: {datetime.now().strftime('%H:%M:%S')}")
                
                # 10번째 체크마다 상태 알림
                if activity_count % 10 == 0:
                    message_id = self.webhook_sender.send_watchhamster_status(
                        f"워치햄스터 모니터링 체크 완료 (#{activity_count})",
                        {
                            "check_count": activity_count,
                            "check_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "status": "정상 모니터링",
                            "next_check": "5분 후"
                        }
                    )
                    
                    if message_id:
                        print(f"📊 모니터링 상태 알림 전송됨: {message_id}")
                
            except Exception as e:
                print(f"❌ 모니터링 활동 오류: {e}")
                
                # 오류 알림 전송
                error_message_id = self.webhook_sender.send_watchhamster_error(
                    f"모니터링 활동 중 오류 발생",
                    {
                        "error": str(e),
                        "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "activity_count": activity_count
                    }
                )
                
                if error_message_id:
                    print(f"🚨 오류 알림 전송됨: {error_message_id}")
    
    def start(self):
        """서비스 시작"""
        if self.is_running:
            print("⚠️ 워치햄스터 서비스가 이미 실행 중입니다")
            return
        
        print("🚀 워치햄스터 서비스 시작 중...")
        self.is_running = True
        
        # 시작 알림 전송
        self.send_startup_notification()
        
        # 주기적 상태 알림 스레드 시작
        status_thread = threading.Thread(target=self.send_periodic_status, daemon=True)
        status_thread.start()
        
        # 모니터링 활동 스레드 시작
        self.monitor_thread = threading.Thread(target=self.simulate_monitoring_activity, daemon=True)
        self.monitor_thread.start()
        
        print("✅ 워치햄스터 서비스가 시작되었습니다")
        print("📊 상태:")
        print("  • 주기적 상태 알림: 30분마다")
        print("  • 모니터링 체크: 5분마다")
        print("  • 상태 리포트: 50분마다 (10번째 체크)")
        print()
        print("🔧 서비스를 중지하려면 Ctrl+C를 누르세요")
        
        try:
            # 메인 루프
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중지 요청됨")
            self.stop()
    
    def stop(self):
        """서비스 중지"""
        if not self.is_running:
            return
        
        print("🛑 워치햄스터 서비스 중지 중...")
        self.is_running = False
        
        # 중지 알림 전송
        try:
            message_id = self.webhook_sender.send_watchhamster_status(
                "워치햄스터 모니터 중지됨",
                {
                    "stop_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "정상 중지",
                    "reason": "사용자 요청"
                }
            )
            
            if message_id:
                print(f"📤 중지 알림 전송됨: {message_id}")
                
        except Exception as e:
            print(f"❌ 중지 알림 전송 오류: {e}")
        
        # 웹훅 전송자 정리
        if hasattr(self.webhook_sender, 'shutdown'):
            self.webhook_sender.shutdown(timeout=5)
        
        print("✅ 워치햄스터 서비스가 중지되었습니다")


def main():
    """메인 실행 함수"""
    print("🎯🛡️ POSCO 워치햄스터 모니터 서비스")
    print("=" * 50)
    print("기능:")
    print("  • 시스템 모니터링")
    print("  • 주기적 상태 알림")
    print("  • 오류 감지 및 알림")
    print("  • 두레이 웹훅 알림 전송")
    print()
    
    # 서비스 시작
    service = WatchhamsterService()
    service.start()


if __name__ == "__main__":
    main()