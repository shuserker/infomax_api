#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 - 워치햄스터 🛡️ (WatchHamster)

모니터링 프로세스를 감시하고 자동으로 재시작하는 워치햄스터 🛡️ 시스템
- 프로세스 상태 감시
- 자동 Git 업데이트 체크
- 오류 시 자동 복구
- 상태 알림 전송
"""

import subprocess
import time
import os
import sys
import json
import requests
from datetime import datetime, timedelta
import psutil

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config import WATCHHAMSTER_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
except ImportError:
    print("[ERROR] config.py를 찾을 수 없습니다.")
    sys.exit(1)

class PoscoMonitorWatchdog:
    """
    POSCO 뉴스 모니터링 워치햄스터 🛡️ 클래스
    
    주요 기능:
    - 모니터링 프로세스 상태 감시
    - 자동 Git 업데이트 체크 및 적용
    - 프로세스 오류 시 자동 재시작
    - 상태 알림 전송
    """
    
    def __init__(self):
        self.script_dir = current_dir
        self.monitor_script = os.path.join(self.script_dir, "run_monitor.py")
        self.log_file = os.path.join(self.script_dir, "WatchHamster.log")
        self.status_file = os.path.join(self.script_dir, "WatchHamster_status.json")
        self.monitor_process = None
        self.last_git_check = datetime.now() - timedelta(hours=1)  # 초기 체크 강제
        self.git_check_interval = 60  # 1시간마다 Git 체크 (POSCO 뉴스 특성상 급한 업데이트 드뭄)
        self.process_check_interval = 300  # 5분마다 프로세스 체크 (뉴스 발행 간격 고려)
        
    def log(self, message):
        """로그 메시지 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def send_notification(self, message, is_error=False):
        """Dooray 알림 전송"""
        try:
            color = "#ff4444" if is_error else "#28a745"
            bot_name = "POSCO 워치햄스터 ❌" if is_error else "POSCO 워치햄스터 🐹🛡️"
            
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": message.split('\n')[0],
                "attachments": [{
                    "color": color,
                    "text": message
                }]
            }
            
            response = requests.post(
                WATCHHAMSTER_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log(f"✅ 알림 전송 성공: {message.split(chr(10))[0]}")
            else:
                self.log(f"❌ 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ 알림 전송 오류: {e}")
    
    def check_git_updates(self):
        """Git 저장소 업데이트 체크"""
        try:
            # 원격 저장소 정보 가져오기
            result = subprocess.run(
                ["git", "fetch", "origin", "main"],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.log(f"❌ Git fetch 실패: {result.stderr}")
                return False
            
            # 로컬과 원격 비교
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                commits_behind = int(result.stdout.strip())
                if commits_behind > 0:
                    self.log(f"🔄 새로운 업데이트 발견: {commits_behind}개 커밋")
                    return True
                else:
                    self.log("✅ Git 저장소 최신 상태")
                    return False
            else:
                self.log(f"❌ Git 상태 체크 실패: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Git 업데이트 체크 오류: {e}")
            return False
    
    def apply_git_update(self):
        """Git 업데이트 적용"""
        try:
            self.log("🔄 Git 업데이트 적용 중...")
            
            # 현재 모니터링 프로세스 중지
            if self.monitor_process and self.monitor_process.poll() is None:
                self.log("⏹️ 현재 모니터링 프로세스 중지 중...")
                self.stop_monitor_process()
                time.sleep(3)
            
            # Git pull 실행
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log("✅ Git 업데이트 완료")
                self.send_notification(
                    f"🔄 POSCO 모니터 자동 업데이트 완료\n\n"
                    f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🔄 변경사항: Git pull 성공\n"
                    f"🚀 모니터링 자동 재시작 중..."
                )
                
                # 모니터링 프로세스 재시작
                time.sleep(2)
                self.start_monitor_process()
                return True
            else:
                self.log(f"❌ Git pull 실패: {result.stderr}")
                self.send_notification(
                    f"❌ POSCO 모니터 업데이트 실패\n\n"
                    f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"❌ 오류: {result.stderr}\n"
                    f"🔧 수동 확인이 필요합니다.",
                    is_error=True
                )
                return False
                
        except Exception as e:
            self.log(f"❌ Git 업데이트 적용 오류: {e}")
            self.send_notification(
                f"❌ POSCO 모니터 업데이트 오류\n\n"
                f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"❌ 오류: {str(e)}\n"
                f"🔧 수동 확인이 필요합니다.",
                is_error=True
            )
            return False
    
    def is_monitor_running(self):
        """모니터링 프로세스 실행 상태 확인"""
        try:
            if self.monitor_process and self.monitor_process.poll() is None:
                return True
            
            # 프로세스 목록에서 확인
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                        cmdline = proc.info['cmdline']
                        if cmdline and 'run_monitor.py' in ' '.join(cmdline) and '3' in cmdline:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
            
        except Exception as e:
            self.log(f"❌ 프로세스 상태 확인 오류: {e}")
            return False
    
    def start_monitor_process(self):
        """모니터링 프로세스 시작"""
        try:
            if self.is_monitor_running():
                self.log("✅ 모니터링 프로세스가 이미 실행 중입니다.")
                return True
            
            self.log("🚀 모니터링 프로세스 시작 중...")
            
            # Python 스크립트 실행
            self.monitor_process = subprocess.Popen(
                [sys.executable, self.monitor_script, "3"],
                cwd=self.script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            time.sleep(5)  # 프로세스 시작 대기
            
            if self.monitor_process.poll() is None:
                self.log("✅ 모니터링 프로세스 시작 성공")
                return True
            else:
                self.log("❌ 모니터링 프로세스 시작 실패")
                return False
                
        except Exception as e:
            self.log(f"❌ 모니터링 프로세스 시작 오류: {e}")
            return False
    
    def stop_monitor_process(self):
        """모니터링 프로세스 중지"""
        try:
            # 실행 중인 모든 관련 프로세스 종료
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                        cmdline = proc.info['cmdline']
                        if cmdline and 'run_monitor.py' in ' '.join(cmdline):
                            proc.terminate()
                            self.log(f"⏹️ 프로세스 종료: PID {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if self.monitor_process:
                self.monitor_process = None
                
            time.sleep(2)
            self.log("✅ 모니터링 프로세스 중지 완료")
            
        except Exception as e:
            self.log(f"❌ 모니터링 프로세스 중지 오류: {e}")
    
    def save_status(self):
        """현재 상태 저장"""
        try:
            status = {
                "last_check": datetime.now().isoformat(),
                "monitor_running": self.is_monitor_running(),
                "last_git_check": self.last_git_check.isoformat(),
                "watchdog_pid": os.getpid()
            }
            
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.log(f"❌ 상태 저장 오류: {e}")
    
    def run(self):
        """워치햄스터 🛡️ 메인 실행 루프"""
        self.log("POSCO 뉴스 모니터 워치햄스터 시작")
        self.send_notification(
            f"🐹 POSCO 모니터 워치햄스터 🛡️ 시작\n\n"
            f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔍 프로세스 감시: {self.process_check_interval}초 간격\n"
            f"🔄 Git 업데이트 체크: {self.git_check_interval}분 간격\n"
            f"🚀 자동 복구 기능 활성화"
        )
        
        # 초기 모니터링 프로세스 시작
        if not self.is_monitor_running():
            self.start_monitor_process()
        
        try:
            while True:
                current_time = datetime.now()
                
                # 프로세스 상태 체크
                if not self.is_monitor_running():
                    self.log("❌ 모니터링 프로세스가 중단됨 - 자동 재시작 중...")
                    self.send_notification(
                        f"⚠️ POSCO 모니터 프로세스 중단 감지\n\n"
                        f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"🔄 자동 재시작 중...",
                        is_error=True
                    )
                    
                    if self.start_monitor_process():
                        self.send_notification(
                            f"✅ POSCO 모니터 자동 복구 완료\n\n"
                            f"📅 복구 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"🚀 모니터링 재개됨"
                        )
                    else:
                        self.send_notification(
                            f"❌ POSCO 모니터 자동 복구 실패\n\n"
                            f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"🔧 수동 확인이 필요합니다.",
                            is_error=True
                        )
                
                # Git 업데이트 체크
                if (current_time - self.last_git_check).total_seconds() >= (self.git_check_interval * 60):
                    self.log("🔍 Git 업데이트 체크 중...")
                    if self.check_git_updates():
                        self.apply_git_update()
                    self.last_git_check = current_time
                
                # 상태 저장
                self.save_status()
                
                # 대기
                time.sleep(self.process_check_interval)
                
        except KeyboardInterrupt:
            self.log("🛑 워치햄스터 🛡️ 중단 요청 받음")
            self.send_notification(
                f"🛑 POSCO 모니터 워치햄스터 🛡️ 중단\n\n"
                f"📅 중단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⚠️ 자동 복구 기능이 비활성화됩니다."
            )
        except Exception as e:
            self.log(f"❌ 워치햄스터 🛡️ 오류: {e}")
            self.send_notification(
                f"❌ POSCO 모니터 워치햄스터 🛡️ 오류\n\n"
                f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"❌ 오류: {str(e)}\n"
                f"🔧 수동 확인이 필요합니다.",
                is_error=True
            )

if __name__ == "__main__":
    # Windows 환경에서 UTF-8 출력 설정
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    
    watchdog = PoscoMonitorWatchdog()
    watchdog.run()