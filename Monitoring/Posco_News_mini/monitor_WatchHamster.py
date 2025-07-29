#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 - 워치햄스터 🛡️ (WatchHamster)

모니터링 프로세스를 감시하고 자동으로 재시작하는 워치햄스터 🛡️ 시스템

주요 기능:
- 프로세스 상태 감시 및 자동 재시작
- Git 저장소 업데이트 자동 체크 및 적용
- 시스템 오류 시 자동 복구
- Dooray를 통한 상태 알림 전송
- 로그 파일 관리 및 상태 저장

설계 원칙:
- 안정성 우선: 프로세스 크래시 시 즉시 복구
- 자동화: 수동 개입 최소화
- 모니터링: 모든 상태 변화 추적
- 알림: 중요한 이벤트 즉시 전달

작성자: AI Assistant
최종 수정: 2025-07-28 (최적화)
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

class PoscoMonitorWatchHamster:
    """
    POSCO 뉴스 모니터링 워치햄스터 🛡️ 클래스
    
    모니터링 프로세스의 안정성을 보장하는 자동 복구 시스템입니다.
    
    주요 기능:
    - 모니터링 프로세스 상태 감시 (5분 간격)
    - 자동 Git 업데이트 체크 (1시간 간격)
    - 프로세스 오류 시 자동 재시작
    - Dooray를 통한 상태 알림 전송
    - 로그 파일 관리 및 상태 저장
    
    Attributes:
        script_dir (str): 스크립트 디렉토리 경로
        monitor_script (str): 모니터링 스크립트 경로
        log_file (str): 로그 파일 경로
        status_file (str): 상태 파일 경로
        monitor_process (subprocess.Popen): 모니터링 프로세스 객체
        last_git_check (datetime): 마지막 Git 체크 시간
        git_check_interval (int): Git 체크 간격 (초)
        process_check_interval (int): 프로세스 체크 간격 (초)
    """
    
    def __init__(self):
        """
        워치햄스터 초기화
        
        파일 경로, 체크 간격, 초기 상태를 설정합니다.
        """
        self.script_dir = current_dir
        self.monitor_script = os.path.join(self.script_dir, "run_monitor.py")
        self.log_file = os.path.join(self.script_dir, "WatchHamster.log")
        self.status_file = os.path.join(self.script_dir, "WatchHamster_status.json")
        self.monitor_process = None
        self.last_git_check = datetime.now() - timedelta(hours=1)  # 초기 체크 강제
        self.last_status_notification = datetime.now()  # 마지막 상태 알림 시간
        self.git_check_interval = 60 * 60  # 1시간마다 Git 체크 (POSCO 뉴스 특성상 급한 업데이트 드뭄)
        self.process_check_interval = 5 * 60  # 5분마다 프로세스 체크 (뉴스 발행 간격 고려)
        self.status_notification_interval = 60 * 60  # 1시간마다 정기 상태 알림
        
    def log(self, message):
        """
        로그 메시지 기록
        
        콘솔과 로그 파일에 타임스탬프와 함께 메시지를 기록합니다.
        Windows 콘솔 인코딩 문제를 해결합니다.
        
        Args:
            message (str): 기록할 로그 메시지
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # Windows 콘솔 출력 시 인코딩 문제 해결
        try:
            print(log_message)
        except UnicodeEncodeError:
            # 콘솔에서 한글 출력 실패 시 영어로 대체
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            print(f"[{timestamp}] {safe_message}")
        
        # 로그 파일에는 항상 UTF-8로 저장
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def send_notification(self, message, is_error=False):
        """
        Dooray 알림 전송
        
        워치햄스터 상태나 중요한 이벤트를 Dooray로 전송합니다.
        
        Args:
            message (str): 전송할 메시지
            is_error (bool): 오류 알림 여부 (색상과 봇명 변경)
        """
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
        """
        Git 저장소 업데이트 체크
        
        원격 저장소와 로컬 저장소를 비교하여 업데이트가 있는지 확인합니다.
        
        Returns:
            bool: 업데이트가 있으면 True, 없으면 False
        """
        try:
            # 원격 저장소 정보 가져오기
            result = subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.log(f"⚠️ Git fetch 실패: {result.stderr}")
                return False
            
            # 로컬과 원격 비교
            result = subprocess.run(
                ['git', 'rev-list', 'HEAD..origin/main', '--count'],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                commit_count = int(result.stdout.strip())
                if commit_count > 0:
                    self.log(f"🔄 Git 업데이트 발견: {commit_count}개 커밋")
                    return True
                else:
                    self.log("📋 Git 업데이트 없음")
                    return False
            else:
                self.log(f"⚠️ Git 비교 실패: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("⚠️ Git 체크 타임아웃")
            return False
        except Exception as e:
            self.log(f"❌ Git 체크 오류: {e}")
            return False
    
    def apply_git_update(self):
        """Git 업데이트 적용 - 성능 최적화"""
        try:
            self.log("🔄 Git 업데이트 적용 중...")
            
            # 현재 프로세스 중지
            self.stop_monitor_process()
            
            # Git pull 실행 (shallow fetch로 성능 향상)
            result = subprocess.run(
                ["git", "pull", "--depth=1", "origin", "main"],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=30  # 타임아웃 단축
            )
            
            if result.returncode == 0:
                self.log("✅ Git 업데이트 성공")
                self.send_notification(
                    f"🔄 POSCO 모니터 Git 업데이트 완료\n\n"
                    f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"📝 변경사항: {result.stdout.strip()}\n"
                    f"🚀 모니터링 재시작 중..."
                )
                
                # 모니터링 프로세스 재시작
                time.sleep(3)
                if self.start_monitor_process():
                    self.send_notification(
                        f"✅ POSCO 모니터 업데이트 후 재시작 완료\n\n"
                        f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"🔄 최신 코드로 모니터링 재개됨"
                    )
                else:
                    self.send_notification(
                        f"❌ POSCO 모니터 업데이트 후 재시작 실패\n\n"
                        f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"🔧 수동 확인이 필요합니다.",
                        is_error=True
                    )
            else:
                self.log(f"❌ Git 업데이트 실패: {result.stderr}")
                self.send_notification(
                    f"❌ POSCO 모니터 Git 업데이트 실패\n\n"
                    f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"❌ 오류: {result.stderr.strip()}\n"
                    f"🔧 수동 확인이 필요합니다.",
                    is_error=True
                )
                
                # 실패 시 모니터링 프로세스 재시작
                self.start_monitor_process()
                
        except subprocess.TimeoutExpired:
            self.log("❌ Git 업데이트 타임아웃")
            self.start_monitor_process()
        except Exception as e:
            self.log(f"❌ Git 업데이트 오류: {e}")
            self.start_monitor_process()
    
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
            
            # Python 스크립트 실행 (콘솔 출력 허용)
            if os.name == 'nt':  # Windows
                self.monitor_process = subprocess.Popen(
                    [sys.executable, self.monitor_script, "3"],
                    cwd=self.script_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # macOS/Linux
                self.monitor_process = subprocess.Popen(
                    [sys.executable, self.monitor_script, "3"],
                    cwd=self.script_dir
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
    
    def send_status_notification(self):
        """정기 상태 알림 전송 (1시간마다)"""
        try:
            current_time = datetime.now()
            monitor_status = "🟢 정상 작동" if self.is_monitor_running() else "🔴 중단됨"
            
            # 간단한 상태 체크 실행
            try:
                import subprocess
                result = subprocess.run(
                    ["python", "run_monitor.py", "1"],
                    cwd=self.script_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                api_status = "🟢 API 정상" if result.returncode == 0 else "🟡 API 확인 필요"
            except:
                api_status = "🟡 API 확인 불가"
            
            # 시스템 리소스 정보 수집
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('.')
                
                resource_info = (
                    f"💻 CPU 사용률: {cpu_percent:.1f}%\n"
                    f"🧠 메모리 사용률: {memory.percent:.1f}%\n"
                    f"💾 디스크 사용률: {disk.percent:.1f}%"
                )
            except:
                resource_info = "📊 시스템 정보 수집 실패"
            
            self.send_notification(
                f"🐹 POSCO 워치햄스터 🛡️ 정기 상태 보고\n\n"
                f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"🔍 모니터링 프로세스: {monitor_status}\n"
                f"🌐 API 연결: {api_status}\n"
                f"{resource_info}\n"
                f"⏰ 다음 보고: {(current_time + timedelta(hours=1)).strftime('%H:%M')}\n"
                f"🚀 자동 복구 기능: 활성화"
            )
            
            self.log("📊 정기 상태 알림 전송 완료")
            
        except Exception as e:
            self.log(f"❌ 정기 상태 알림 실패: {e}")
    
    def manage_log_file(self):
        """로그 파일 크기 관리 - 10MB 초과 시 백업 후 새로 시작"""
        try:
            if os.path.exists(self.log_file):
                file_size = os.path.getsize(self.log_file)
                max_size = 10 * 1024 * 1024  # 10MB
                
                if file_size > max_size:
                    # 백업 파일명 생성
                    backup_name = f"WatchHamster_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    backup_path = os.path.join(self.script_dir, backup_name)
                    
                    # 기존 로그 파일을 백업으로 이동
                    os.rename(self.log_file, backup_path)
                    
                    self.log(f"📁 로그 파일 백업 완료: {backup_name}")
                    
        except Exception as e:
            print(f"[ERROR] 로그 파일 관리 실패: {e}")
    
    def save_status(self):
        """현재 상태 저장"""
        try:
            # 로그 파일 크기 관리
            self.manage_log_file()
            
            status = {
                "last_check": datetime.now().isoformat(),
                "monitor_running": self.is_monitor_running(),
                "last_git_check": self.last_git_check.isoformat(),
                "last_status_notification": self.last_status_notification.isoformat(),
                "watchhamster_pid": os.getpid()
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
            f"🔍 프로세스 감시: {self.process_check_interval//60}분 간격\n"
            f"🔄 Git 업데이트 체크: {self.git_check_interval//60}분 간격\n"
            f"📊 정기 상태 알림: {self.status_notification_interval//60}분 간격\n"
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
                if (current_time - self.last_git_check).total_seconds() >= (self.git_check_interval):
                    self.log("🔍 Git 업데이트 체크 중...")
                    if self.check_git_updates():
                        self.apply_git_update()
                    self.last_git_check = current_time
                
                # 정기 상태 알림 (1시간마다)
                if (current_time - self.last_status_notification).total_seconds() >= self.status_notification_interval:
                    self.send_status_notification()
                    self.last_status_notification = current_time
                
                # 상태 저장 (메모리 최적화)
                self.save_status()
                
                # 메모리 정리 (가비지 컬렉션)
                import gc
                gc.collect()
                
                # 대기 (CPU 사용률 최적화)
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
    
    watchhamster = PoscoMonitorWatchHamster()
    watchhamster.run()