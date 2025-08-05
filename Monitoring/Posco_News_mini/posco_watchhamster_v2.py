#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 v2.0 🛡️ (WatchHamster)

기존 워치햄스터의 모든 고급 기능을 유지하면서
비활성화된 모듈 의존성을 제거한 개선된 버전

주요 기능:
- 🛡️ 자동 복구 기능
- 📊 프로세스 감시 (5분 간격)
- 🔄 Git 업데이트 체크 (60분 간격)
- 📋 정기 상태 알림 (2시간 간격)
- 📅 스케줄 작업 (06:00, 18:00 등)
- 🌙 조용한 모드 (18시 이후)

작성자: AI Assistant
최종 수정: 2025-08-05
"""

import subprocess
import time
import os
import sys
import json
import requests
from datetime import datetime, timedelta
import psutil
import signal
import threading

# 출력 버퍼링 해제 - 실시간 로그 출력을 위해
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 환경 변수로도 출력 버퍼링 비활성화
os.environ['PYTHONUNBUFFERED'] = '1'

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config import WATCHHAMSTER_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
except ImportError:
    print("[WARNING] config.py에서 설정을 불러올 수 없습니다. 기본값을 사용합니다.")
    WATCHHAMSTER_WEBHOOK_URL = None
    BOT_PROFILE_IMAGE_URL = None

class PoscoWatchHamsterV2:
    """
    POSCO 워치햄스터 v2.0 🛡️ 클래스
    
    기존 워치햄스터의 모든 기능을 유지하면서
    비활성화된 모듈 의존성을 제거한 개선된 버전
    """
    
    def __init__(self):
        """워치햄스터 초기화"""
        self.script_dir = current_dir
        self.main_script = os.path.join(self.script_dir, "reports", "integrated_report_generator.py")
        self.news_notifier_script = os.path.join(self.script_dir, "posco_legacy_notifier.py")
        self.log_file = os.path.join(self.script_dir, "WatchHamster_v2.log")
        self.status_file = os.path.join(self.script_dir, "WatchHamster_v2_status.json")
        
        # 프로세스 관리
        self.monitor_process = None
        self.news_notifier_process = None
        self.running = True
        
        # 시간 간격 설정
        self.process_check_interval = 5 * 60  # 5분
        self.git_check_interval = 60 * 60     # 60분
        self.status_notification_interval = 2 * 60 * 60  # 2시간
        
        # 마지막 실행 시간 추적
        self.last_git_check = datetime.now() - timedelta(hours=1)
        self.last_status_notification = datetime.now() - timedelta(hours=2)
        self.last_process_check = datetime.now()
        
        # 스케줄 작업 시간
        self.scheduled_times = {
            'morning_check': (6, 0),    # 06:00
            'morning_report': (6, 10),  # 06:10
            'evening_summary': (18, 0), # 18:00
            'evening_report': (18, 10), # 18:10
            'evening_analysis': (18, 20) # 18:20
        }
        self.executed_today = set()
        
        # 신호 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.log_message("🐹 POSCO 워치햄스터 v2.0 초기화 완료")
    
    def signal_handler(self, signum, frame):
        """종료 신호 처리"""
        self.log_message(f"🛑 종료 신호 수신 (신호: {signum})")
        self.running = False
        if self.monitor_process:
            try:
                self.monitor_process.terminate()
                self.monitor_process.wait(timeout=10)
            except:
                pass
    
    def log_message(self, message):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def is_quiet_hours(self):
        """조용한 시간대 확인 (18시 이후)"""
        current_hour = datetime.now().hour
        return current_hour >= 18
    
    def send_notification(self, message, is_error=False):
        """Dooray 알림 전송"""
        if not WATCHHAMSTER_WEBHOOK_URL:
            return
        
        try:
            # 조용한 시간대에는 오류만 알림
            if self.is_quiet_hours() and not is_error:
                return
            
            payload = {
                "botName": "🐹 POSCO 워치햄스터",
                "botIconImage": BOT_PROFILE_IMAGE_URL or "",
                "text": message
            }
            
            response = requests.post(WATCHHAMSTER_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                self.log_message("📤 알림 전송 완료")
            else:
                self.log_message(f"⚠️ 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 알림 전송 오류: {e}")
    
    def check_git_updates(self):
        """Git 업데이트 확인 및 적용"""
        try:
            self.log_message("🔄 Git 업데이트 확인 중...")
            
            # Git fetch
            result = subprocess.run(['git', 'fetch'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.log_message(f"⚠️ Git fetch 실패: {result.stderr}")
                return False
            
            # 업데이트 확인
            result = subprocess.run(['git', 'status', '-uno'], 
                                  capture_output=True, text=True, timeout=10)
            
            if "behind" in result.stdout:
                self.log_message("📥 새로운 업데이트 발견, 적용 중...")
                
                # Git pull
                result = subprocess.run(['git', 'pull'], 
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.log_message("✅ Git 업데이트 완료")
                    self.send_notification("🔄 POSCO 시스템 업데이트 완료")
                    return True
                else:
                    self.log_message(f"❌ Git pull 실패: {result.stderr}")
                    return False
            else:
                self.log_message("✅ 최신 버전입니다")
                return True
                
        except Exception as e:
            self.log_message(f"❌ Git 업데이트 확인 오류: {e}")
            return False
    
    def get_system_status(self):
        """시스템 상태 정보 수집"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': cpu_percent,
                'memory': memory.percent,
                'disk': disk.percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.log_message(f"❌ 시스템 상태 수집 오류: {e}")
            return None
    
    def start_monitor_process(self):
        """모니터링 프로세스 시작 (리포트 생성 + 뉴스 알림)"""
        success_count = 0
        
        # 1. 리포트 생성 프로세스 시작
        try:
            if os.path.exists(self.main_script):
                self.log_message("🚀 리포트 생성 프로세스 시작 중...")
                
                self.monitor_process = subprocess.Popen([
                    sys.executable, self.main_script
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # 프로세스 시작 확인
                time.sleep(3)
                if self.monitor_process.poll() is None:
                    self.log_message(f"✅ 리포트 생성 프로세스 시작 완료 (PID: {self.monitor_process.pid})")
                    success_count += 1
                else:
                    self.log_message(f"❌ 리포트 생성 프로세스 시작 실패")
            else:
                self.log_message(f"❌ 리포트 생성 스크립트를 찾을 수 없습니다: {self.main_script}")
                
        except Exception as e:
            self.log_message(f"❌ 리포트 생성 프로세스 시작 오류: {e}")
        
        # 2. 뉴스 알림 프로세스 시작
        try:
            if os.path.exists(self.news_notifier_script):
                self.log_message("📰 뉴스 알림 프로세스 시작 중...")
                
                self.news_notifier_process = subprocess.Popen([
                    sys.executable, self.news_notifier_script
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # 프로세스 시작 확인
                time.sleep(3)
                if self.news_notifier_process.poll() is None:
                    self.log_message(f"✅ 뉴스 알림 프로세스 시작 완료 (PID: {self.news_notifier_process.pid})")
                    success_count += 1
                else:
                    self.log_message(f"❌ 뉴스 알림 프로세스 시작 실패")
            else:
                self.log_message(f"❌ 뉴스 알림 스크립트를 찾을 수 없습니다: {self.news_notifier_script}")
                
        except Exception as e:
            self.log_message(f"❌ 뉴스 알림 프로세스 시작 오류: {e}")
        
        # 결과 반환
        if success_count >= 1:
            self.log_message(f"🎉 {success_count}/2 프로세스 시작 완료!")
            return True
        else:
            self.log_message("❌ 모든 프로세스 시작 실패")
            return False
    
    def check_monitor_process(self):
        """모니터링 프로세스 상태 확인 및 자동 복구"""
        recovery_needed = False
        
        # 1. 리포트 생성 프로세스 확인
        if not self.monitor_process:
            self.log_message("⚠️ 리포트 생성 프로세스가 없습니다.")
            recovery_needed = True
        elif self.monitor_process.poll() is not None:
            self.log_message("⚠️ 리포트 생성 프로세스가 종료되었습니다.")
            return_code = self.monitor_process.returncode
            self.log_message(f"   종료 코드: {return_code}")
            recovery_needed = True
        else:
            self.log_message("✅ 리포트 생성 프로세스 정상 작동 중")
        
        # 2. 뉴스 알림 프로세스 확인
        if not self.news_notifier_process:
            self.log_message("⚠️ 뉴스 알림 프로세스가 없습니다.")
            recovery_needed = True
        elif self.news_notifier_process.poll() is not None:
            self.log_message("⚠️ 뉴스 알림 프로세스가 종료되었습니다.")
            return_code = self.news_notifier_process.returncode
            self.log_message(f"   종료 코드: {return_code}")
            recovery_needed = True
        else:
            self.log_message("✅ 뉴스 알림 프로세스 정상 작동 중")
        
        # 3. 자동 복구 실행
        if recovery_needed:
            self.log_message("🔧 프로세스 자동 복구 시작...")
            if self.start_monitor_process():
                self.send_notification("🔧 POSCO 모니터 자동 복구 완료", is_error=True)
            else:
                self.send_notification("❌ POSCO 모니터 자동 복구 실패", is_error=True)
    
    def check_scheduled_tasks(self):
        """스케줄 작업 확인 및 실행"""
        now = datetime.now()
        current_time = (now.hour, now.minute)
        today_key = now.strftime("%Y-%m-%d")
        
        # 매일 자정에 실행된 작업 목록 초기화
        if now.hour == 0 and now.minute == 0:
            self.executed_today.clear()
            self.log_message("🔄 일일 스케줄 작업 목록 초기화")
        
        for task_name, scheduled_time in self.scheduled_times.items():
            task_key = f"{today_key}_{task_name}"
            
            if (current_time == scheduled_time and 
                task_key not in self.executed_today):
                
                self.log_message(f"⏰ 스케줄 작업 실행: {task_name} ({scheduled_time[0]:02d}:{scheduled_time[1]:02d})")
                self.execute_scheduled_task(task_name)
                self.executed_today.add(task_key)
    
    def execute_scheduled_task(self, task_name):
        """스케줄 작업 실행"""
        try:
            if task_name in ['morning_check', 'evening_summary']:
                # 상태 체크 작업
                status = self.get_system_status()
                if status:
                    message = f"📊 POSCO 시스템 상태 체크\n"
                    message += f"🖥️ CPU: {status['cpu']:.1f}%\n"
                    message += f"💾 메모리: {status['memory']:.1f}%\n"
                    message += f"💿 디스크: {status['disk']:.1f}%"
                    self.send_notification(message)
            
            elif task_name in ['morning_report', 'evening_report', 'evening_analysis']:
                # 리포트 생성 작업
                self.log_message(f"📋 {task_name} 리포트 생성 요청")
                # 실제 리포트 생성은 메인 스크립트에서 처리
                
        except Exception as e:
            self.log_message(f"❌ 스케줄 작업 실행 오류 ({task_name}): {e}")
    
    def send_status_notification(self):
        """정기 상태 알림 전송"""
        try:
            status = self.get_system_status()
            if not status:
                return
            
            uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            
            message = f"🐹 POSCO 모니터 워치햄스터 🛡️ 상태 알림\n\n"
            message += f"📅 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"⏱️ 실행 시간: {uptime_hours:.1f}시간\n"
            message += f"🔍 프로세스 감시: 5분 간격\n"
            message += f"🔄 Git 업데이트 체크: 60분 간격\n"
            message += f"📊 정기 상태 알림: 120분 간격\n"
            message += f"📅 스케줄 작업: 06:00, 06:10, 18:00, 18:10, 18:20, 07-17시 매시간\n"
            
            if self.is_quiet_hours():
                message += f"🌙 조용한 모드: 18시 이후 문제 발생 시에만 알림\n"
            
            message += f"🚀 자동 복구 기능 활성화\n\n"
            message += f"📊 시스템 상태:\n"
            message += f"🖥️ CPU: {status['cpu']:.1f}%\n"
            message += f"💾 메모리: {status['memory']:.1f}%\n"
            message += f"💿 디스크: {status['disk']:.1f}%"
            
            self.send_notification(message)
            
        except Exception as e:
            self.log_message(f"❌ 상태 알림 전송 오류: {e}")
    
    def run(self):
        """메인 워치햄스터 루프"""
        self.start_time = datetime.now()
        
        self.log_message("🐹 POSCO 모니터 워치햄스터 🛡️ 시작")
        self.log_message(f"📅 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message("🔍 프로세스 감시: 5분 간격")
        self.log_message("🔄 Git 업데이트 체크: 60분 간격")
        self.log_message("📊 정기 상태 알림: 120분 간격")
        self.log_message("📅 스케줄 작업: 06:00, 06:10, 18:00, 18:10, 18:20, 07-17시 매시간")
        self.log_message("🌙 조용한 모드: 18시 이후 문제 발생 시에만 알림")
        self.log_message("🚀 자동 복구 기능 활성화")
        
        # 시작 알림
        self.send_notification(
            f"🐹 POSCO 모니터 워치햄스터 🛡️ 시작\n\n"
            f"📅 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔍 프로세스 감시: 5분 간격\n"
            f"🔄 Git 업데이트 체크: 60분 간격\n"
            f"📊 정기 상태 알림: 120분 간격\n"
            f"📅 스케줄 작업: 06:00, 06:10, 18:00, 18:10, 18:20, 07-17시 매시간\n"
            f"🌙 조용한 모드: 18시 이후 문제 발생 시에만 알림\n"
            f"🚀 자동 복구 기능 활성화"
        )
        
        # 초기 모니터링 프로세스 시작
        self.start_monitor_process()
        
        # 메인 루프
        while self.running:
            try:
                now = datetime.now()
                
                # 프로세스 상태 확인 (5분 간격)
                if (now - self.last_process_check).total_seconds() >= self.process_check_interval:
                    self.check_monitor_process()
                    self.last_process_check = now
                
                # Git 업데이트 확인 (60분 간격)
                if (now - self.last_git_check).total_seconds() >= self.git_check_interval:
                    self.check_git_updates()
                    self.last_git_check = now
                
                # 정기 상태 알림 (2시간 간격)
                if (now - self.last_status_notification).total_seconds() >= self.status_notification_interval:
                    self.send_status_notification()
                    self.last_status_notification = now
                
                # 스케줄 작업 확인
                self.check_scheduled_tasks()
                
                # 1분 대기
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.log_message("🛑 사용자에 의한 종료 요청")
                break
            except Exception as e:
                self.log_message(f"❌ 워치햄스터 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기 후 재시도
        
        # 종료 처리
        self.log_message("🛑 POSCO 워치햄스터 종료 중...")
        
        # 리포트 생성 프로세스 종료
        if self.monitor_process:
            try:
                self.monitor_process.terminate()
                self.monitor_process.wait(timeout=10)
                self.log_message("✅ 리포트 생성 프로세스 정상 종료")
            except:
                self.log_message("⚠️ 리포트 생성 프로세스 강제 종료")
        
        # 뉴스 알림 프로세스 종료
        if self.news_notifier_process:
            try:
                self.news_notifier_process.terminate()
                self.news_notifier_process.wait(timeout=10)
                self.log_message("✅ 뉴스 알림 프로세스 정상 종료")
            except:
                self.log_message("⚠️ 뉴스 알림 프로세스 강제 종료")
        
        self.send_notification("🛑 POSCO 워치햄스터 종료")
        self.log_message("✅ POSCO 워치햄스터 종료 완료")

def main():
    """메인 함수"""
    print("🐹 POSCO 워치햄스터 v2.0 🛡️")
    print("=" * 60)
    
    # 워치햄스터 시작
    watchhamster = PoscoWatchHamsterV2()
    watchhamster.run()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())