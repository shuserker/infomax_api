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
    from config import WATCHHAMSTER_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, API_CONFIG
    from core import PoscoNewsAPIClient, NewsDataProcessor, DoorayNotifier
    # 최적화된 모니터링 시스템 연결
    from newyork_monitor import NewYorkMarketMonitor
    from kospi_monitor import KospiCloseMonitor
    from exchange_monitor import ExchangeRateMonitor
    from master_news_monitor import MasterNewsMonitor
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    print("[INFO] 기본 기능으로 동작합니다.")
    # 최적화된 모니터링 시스템 없이도 동작하도록 설정
    NewYorkMarketMonitor = None
    KospiCloseMonitor = None
    ExchangeRateMonitor = None
    MasterNewsMonitor = None

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
        self.status_notification_interval = 2 * 60 * 60  # 2시간마다 정기 상태 알림
        
        # 스케줄 작업 추적
        self.last_scheduled_tasks = {
            'morning_status_check': None,
            'morning_comparison': None,
            'evening_daily_summary': None,
            'evening_detailed_summary': None,
            'evening_advanced_analysis': None,
            'hourly_status_check': None
        }
        
        # 스마트 상태 판단 시스템 초기화
        try:
            self.api_client = PoscoNewsAPIClient(API_CONFIG)
            self.data_processor = NewsDataProcessor()
            self.smart_notifier = DoorayNotifier(WATCHHAMSTER_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, self.api_client)
            self.smart_enabled = True
            self.log("🧠 스마트 상태 판단 시스템 초기화 완료")
        except Exception as e:
            self.log(f"⚠️ 스마트 상태 판단 시스템 초기화 실패: {e}")
            self.smart_enabled = False
        
        # 최적화된 개별 모니터링 시스템 초기화
        try:
            if NewYorkMarketMonitor and KospiCloseMonitor and ExchangeRateMonitor:
                self.newyork_monitor = NewYorkMarketMonitor()
                self.kospi_monitor = KospiCloseMonitor()
                self.exchange_monitor = ExchangeRateMonitor()
                self.individual_monitors_enabled = True
                self.log("🎛️ 개별 모니터링 시스템 연결 완료")
            else:
                self.individual_monitors_enabled = False
                self.log("⚠️ 개별 모니터링 시스템 비활성화 (모듈 없음)")
        except Exception as e:
            self.log(f"⚠️ 개별 모니터링 시스템 초기화 실패: {e}")
            self.individual_monitors_enabled = False
        
        # 마스터 모니터링 시스템 초기화
        try:
            if MasterNewsMonitor:
                self.master_monitor = MasterNewsMonitor()
                self.master_monitor_enabled = True
                self.log("🎛️ 마스터 모니터링 시스템 연결 완료")
            else:
                self.master_monitor_enabled = False
                self.log("⚠️ 마스터 모니터링 시스템 비활성화 (모듈 없음)")
        except Exception as e:
            self.log(f"⚠️ 마스터 모니터링 시스템 초기화 실패: {e}")
            self.master_monitor_enabled = False
        
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
    
    def execute_scheduled_task(self, task_type, task_name):
        """스케줄된 작업 실행 (최적화된 모니터링 시스템 사용)"""
        try:
            self.log(f"📅 스케줄 작업 실행: {task_name}")
            
            # 기존 run_monitor.py 대신 최적화된 모니터링 시스템 사용
            if self.individual_monitors_enabled:
                if task_type == "1":  # 상태 체크
                    self._execute_status_check_task(task_name)
                elif task_type == "2":  # 비교 분석
                    self._execute_comparison_task(task_name)
                elif task_type == "5":  # 일일 요약
                    self._execute_daily_summary_task(task_name)
                elif task_type == "7":  # 상세 요약
                    self._execute_detailed_summary_task(task_name)
                elif task_type == "8":  # 고급 분석
                    self._execute_advanced_analysis_task(task_name)
                else:
                    self.log(f"⚠️ 알 수 없는 작업 타입: {task_type} - 기존 방식 사용")
                    self._execute_legacy_task(task_type, task_name)
            else:
                # 개별 모니터 비활성화 시 기존 방식 사용
                self._execute_legacy_task(task_type, task_name)
                
        except Exception as e:
            self.log(f"❌ {task_name} 오류: {e}")
    
    def _execute_legacy_task(self, task_type, task_name):
        """기존 run_monitor.py 방식으로 작업 실행"""
        try:
            import subprocess
            result = subprocess.run(
                ["python", "run_monitor.py", task_type],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            if result.returncode == 0:
                self.log(f"✅ {task_name} 완료 (기존 방식)")
            else:
                self.log(f"❌ {task_name} 실패 (기존 방식): {result.stderr}")
                
        except Exception as e:
            self.log(f"❌ {task_name} 기존 방식 오류: {e}")
    
    def _execute_status_check_task(self, task_name):
        """상태 체크 작업 실행 (최적화된 모니터 사용)"""
        try:
            # 개별 모니터 상태 체크
            self._check_individual_monitors_status()
            
            # 마스터 모니터 상태 체크
            if self.master_monitor_enabled and hasattr(self, 'master_monitor'):
                strategy = self.master_monitor.get_current_monitoring_strategy()
                self.log(f"🎛️ 현재 모니터링 전략: {strategy['description']}")
            
            self.log(f"✅ {task_name} 완료 (최적화 방식)")
            
        except Exception as e:
            self.log(f"❌ 상태 체크 작업 오류: {e}")
    
    def _execute_comparison_task(self, task_name):
        """비교 분석 작업 실행 (최적화된 모니터 사용)"""
        try:
            # 각 뉴스별 현재 vs 이전 데이터 비교
            comparison_results = []
            
            # 뉴욕마켓워치 비교
            if hasattr(self, 'newyork_monitor'):
                ny_current = self.newyork_monitor.get_current_news_data()
                ny_analysis = self.newyork_monitor.analyze_publish_pattern(ny_current)
                comparison_results.append(f"🌆 뉴욕마켓워치: {ny_analysis.get('analysis', '분석 불가')}")
            
            # 증시마감 비교
            if hasattr(self, 'kospi_monitor'):
                kospi_current = self.kospi_monitor.get_current_news_data()
                kospi_analysis = self.kospi_monitor.analyze_publish_pattern(kospi_current)
                comparison_results.append(f"📈 증시마감: {kospi_analysis.get('analysis', '분석 불가')}")
            
            # 서환마감 비교
            if hasattr(self, 'exchange_monitor'):
                exchange_current = self.exchange_monitor.get_current_news_data()
                exchange_analysis = self.exchange_monitor.analyze_publish_pattern(exchange_current)
                comparison_results.append(f"💱 서환마감: {exchange_analysis.get('analysis', '분석 불가')}")
            
            # 비교 결과 로그
            for result in comparison_results:
                self.log(f"📊 {result}")
            
            self.log(f"✅ {task_name} 완료 (최적화 방식)")
            
        except Exception as e:
            self.log(f"❌ 비교 분석 작업 오류: {e}")
    
    def _execute_daily_summary_task(self, task_name):
        """일일 요약 작업 실행 (최적화된 모니터 사용)"""
        try:
            # 오늘 발행된 뉴스 요약
            summary_data = []
            published_count = 0
            
            # 각 뉴스별 오늘 발행 현황
            monitors = [
                ('🌆 뉴욕마켓워치', self.newyork_monitor if hasattr(self, 'newyork_monitor') else None),
                ('📈 증시마감', self.kospi_monitor if hasattr(self, 'kospi_monitor') else None),
                ('💱 서환마감', self.exchange_monitor if hasattr(self, 'exchange_monitor') else None)
            ]
            
            for name, monitor in monitors:
                if monitor:
                    try:
                        data = monitor.get_current_news_data()
                        analysis = monitor.analyze_publish_pattern(data)
                        is_published = analysis.get('is_published_today', False)
                        
                        if is_published:
                            published_count += 1
                            summary_data.append(f"{name}: ✅ {analysis.get('analysis', '발행 완료')}")
                        else:
                            summary_data.append(f"{name}: ❌ {analysis.get('analysis', '미발행')}")
                    except Exception as e:
                        summary_data.append(f"{name}: ⚠️ 분석 오류")
            
            # 일일 요약 로그
            self.log(f"📋 일일 요약 ({published_count}/3 발행 완료):")
            for summary in summary_data:
                self.log(f"   {summary}")
            
            self.log(f"✅ {task_name} 완료 (최적화 방식)")
            
        except Exception as e:
            self.log(f"❌ 일일 요약 작업 오류: {e}")
    
    def _execute_detailed_summary_task(self, task_name):
        """상세 요약 작업 실행 (최적화된 모니터 사용)"""
        try:
            # 향상된 상태 보고서 생성 및 전송
            if hasattr(self, 'send_enhanced_status_notification'):
                self.send_enhanced_status_notification()
                self.log(f"📊 향상된 상태 알림 전송 완료")
            
            self.log(f"✅ {task_name} 완료 (최적화 방식)")
            
        except Exception as e:
            self.log(f"❌ 상세 요약 작업 오류: {e}")
    
    def _execute_advanced_analysis_task(self, task_name):
        """고급 분석 작업 실행 (최적화된 모니터 사용)"""
        try:
            # 마스터 모니터링 시스템의 통합 분석 사용
            if self.master_monitor_enabled and hasattr(self, 'master_monitor'):
                results = self.master_monitor.run_integrated_check()
                
                # 분석 결과 로그
                for news_type, result in results.items():
                    analysis = result.get('analysis', {})
                    published = result.get('published_today', False)
                    status = "✅ 발행 완료" if published else "⏳ 대기 중"
                    self.log(f"🔬 {news_type}: {status} - {analysis.get('analysis', '분석 불가')}")
            
            self.log(f"✅ {task_name} 완료 (최적화 방식)")
            
        except Exception as e:
            self.log(f"❌ 고급 분석 작업 오류: {e}")
    
    def check_scheduled_tasks(self):
        """스케줄된 작업 체크 및 실행"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        today_key = current_time.strftime('%Y-%m-%d')
        
        # 매일 06:00 - 현재 상태 체크
        if current_hour == 6 and current_minute == 0:
            if self.last_scheduled_tasks['morning_status_check'] != today_key:
                self.execute_scheduled_task("1", "아침 현재 상태 체크")
                self.last_scheduled_tasks['morning_status_check'] = today_key
        
        # 매일 06:10 - 영업일 비교 분석
        if current_hour == 6 and current_minute == 10:
            if self.last_scheduled_tasks['morning_comparison'] != today_key:
                self.execute_scheduled_task("2", "아침 영업일 비교 분석")
                self.last_scheduled_tasks['morning_comparison'] = today_key
        
        # 매일 18:00 - 일일 요약 리포트
        if current_hour == 18 and current_minute == 0:
            if self.last_scheduled_tasks['evening_daily_summary'] != today_key:
                self.execute_scheduled_task("5", "저녁 일일 요약 리포트")
                self.last_scheduled_tasks['evening_daily_summary'] = today_key
        
        # 매일 18:10 - 상세 일일 요약
        if current_hour == 18 and current_minute == 10:
            if self.last_scheduled_tasks['evening_detailed_summary'] != today_key:
                self.execute_scheduled_task("7", "저녁 상세 일일 요약")
                self.last_scheduled_tasks['evening_detailed_summary'] = today_key
        
        # 매일 18:20 - 고급 분석
        if current_hour == 18 and current_minute == 20:
            if self.last_scheduled_tasks['evening_advanced_analysis'] != today_key:
                self.execute_scheduled_task("8", "저녁 고급 분석")
                self.last_scheduled_tasks['evening_advanced_analysis'] = today_key
        
        # 매일 07:00~17:30 매시간 정각 - 현재 상태 체크
        if 7 <= current_hour <= 17 and current_minute == 0:
            hourly_key = f"{today_key}-{current_hour:02d}"
            if self.last_scheduled_tasks['hourly_status_check'] != hourly_key:
                self.execute_scheduled_task("1", f"정시 상태 체크 ({current_hour}시)")
                self.last_scheduled_tasks['hourly_status_check'] = hourly_key
    
    def is_quiet_hours(self):
        """조용한 시간대 체크 (18시 이후)"""
        current_hour = datetime.now().hour
        return current_hour >= 18 or current_hour < 6
    
    def send_status_notification(self):
        """정기 상태 알림 전송 (2시간마다, 18시 이후는 조용한 모드) - 스마트 상태 판단 적용"""
        try:
            current_time = datetime.now()
            is_quiet = self.is_quiet_hours()
            
            # 모니터링 프로세스 상태 확인
            monitor_running = self.is_monitor_running()
            monitor_status = "🟢 정상 작동" if monitor_running else "🔴 중단됨"
            
            # 스마트 상태 판단 시스템 사용
            smart_status_info = None
            current_data = None
            
            if self.smart_enabled and monitor_running:
                try:
                    # 현재 뉴스 데이터 조회
                    current_data = self.api_client.get_news_data()
                    if current_data:
                        # 스마트 상태 분석
                        smart_status_info = self.data_processor.get_status_info(current_data)
                        self.log(f"🧠 스마트 상태 분석 완료: {smart_status_info.get('status_text', '알 수 없음')}")
                    else:
                        self.log("⚠️ 뉴스 데이터 조회 실패")
                except Exception as e:
                    self.log(f"⚠️ 스마트 상태 분석 실패: {e}")
            
            # API 상태 체크 개선 - 모니터링 프로세스가 실행 중이면 API도 정상으로 간주
            api_normal = True
            api_status = "🟢 API 정상"
            
            # 최적화된 모니터링 시스템으로 API 상태 체크
            if not monitor_running:
                try:
                    # 기존 run_monitor.py 대신 최적화된 개별 모니터 사용
                    if self.individual_monitors_enabled:
                        # 개별 모니터로 API 상태 확인
                        api_checks = []
                        
                        # 뉴욕마켓워치 API 체크
                        try:
                            ny_data = self.newyork_monitor.get_current_news_data()
                            api_checks.append(ny_data is not None)
                        except:
                            api_checks.append(False)
                        
                        # 증시마감 API 체크  
                        try:
                            kospi_data = self.kospi_monitor.get_current_news_data()
                            api_checks.append(kospi_data is not None)
                        except:
                            api_checks.append(False)
                        
                        # 서환마감 API 체크
                        try:
                            exchange_data = self.exchange_monitor.get_current_news_data()
                            api_checks.append(exchange_data is not None)
                        except:
                            api_checks.append(False)
                        
                        # API 상태 종합 판단
                        successful_checks = sum(api_checks)
                        total_checks = len(api_checks)
                        
                        if successful_checks == total_checks:
                            api_normal = True
                            api_status = "🟢 API 정상 (최적화 모니터 기반)"
                        elif successful_checks > 0:
                            api_normal = True
                            api_status = f"🟡 API 부분 정상 ({successful_checks}/{total_checks})"
                        else:
                            api_normal = False
                            api_status = "🔴 API 연결 실패"
                        
                        self.log(f"📡 최적화된 모니터로 API 상태 체크: {api_status}")
                    else:
                        # 개별 모니터 비활성화 시 기본 API 체크
                        api_normal = self.api_client.test_connection() if hasattr(self, 'api_client') else False
                        api_status = "🟢 API 정상 (기본 체크)" if api_normal else "🟡 API 확인 필요"
                except Exception as e:
                    api_normal = False
                    api_status = f"🟡 API 확인 불가: {str(e)[:30]}"
                    self.log(f"⚠️ API 상태 체크 오류: {e}")
            else:
                # 모니터링 프로세스가 실행 중이면 API도 정상으로 간주
                self.log("📡 모니터링 프로세스 실행 중 - API 상태 정상으로 간주")
                api_normal = True
                api_status = "🟢 API 정상 (모니터링 프로세스 기반)"
            
            # 시스템 리소스 정보 수집
            resource_normal = True
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('.')
                
                # 리소스 임계값 체크 (CPU 90%, 메모리 90%, 디스크 95%)
                resource_normal = (cpu_percent < 90 and 
                                 memory.percent < 90 and 
                                 disk.percent < 95)
                
                resource_info = (
                    f"💻 CPU 사용률: {cpu_percent:.1f}%\n"
                    f"🧠 메모리 사용률: {memory.percent:.1f}%\n"
                    f"💾 디스크 사용률: {disk.percent:.1f}%"
                )
            except:
                resource_normal = False
                resource_info = "📊 시스템 정보 수집 실패"
            
            # 조용한 시간대 체크
            if is_quiet:
                # 18시 이후: 실제 문제가 있을 때만 알림
                # 핵심 문제: 모니터링 프로세스 중단, 시스템 리소스 임계값 초과
                # API 문제는 모니터링 프로세스가 중단된 경우에만 문제로 간주
                has_problem = not monitor_running or not resource_normal
                
                if has_problem:
                    # 실제 문제 발생 시에만 알림 전송
                    problem_details = []
                    if not monitor_running:
                        problem_details.append("❌ 모니터링 프로세스 중단")
                        # 모니터링 프로세스가 중단된 경우에만 API 상태도 표시
                        if not api_normal:
                            problem_details.append("❌ API 연결 문제")
                    if not resource_normal:
                        problem_details.append("❌ 시스템 리소스 임계값 초과")
                    
                    self.send_notification(
                        f"⚠️ POSCO 워치햄스터 🛡️ 문제 감지 (야간 모드)\n\n"
                        f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"🚨 감지된 문제:\n" + "\n".join(f"   • {problem}" for problem in problem_details) + "\n\n"
                        f"🔍 상세 상태:\n"
                        f"   • 모니터링 프로세스: {monitor_status}\n"
                        f"   • API 연결: {api_status}\n"
                        f"{resource_info}\n\n"
                        f"🔧 자동 복구 시도 중...",
                        is_error=True
                    )
                    self.log("⚠️ 야간 모드 문제 알림 전송 완료")
                else:
                    # 정상 상태: 로그만 기록, 알림 없음
                    self.log(f"🌙 야간 모드 정상 상태 확인 (알림 없음) - {current_time.strftime('%H:%M:%S')}")
            else:
                # 18시 이전: 정상적인 상태 알림 전송
                if self.smart_enabled and smart_status_info and current_data:
                    # 스마트 상태 알림 전송
                    try:
                        self.smart_notifier.send_smart_status_notification(current_data, smart_status_info)
                        self.log("🧠 스마트 상태 알림 전송 완료")
                    except Exception as e:
                        self.log(f"⚠️ 스마트 상태 알림 실패, 기본 알림으로 대체: {e}")
                        # 스마트 알림 실패 시 기본 알림으로 대체
                        self._send_basic_status_notification(current_time, monitor_status, api_status, resource_info)
                else:
                    # 스마트 시스템 비활성화 또는 데이터 없음 시 기본 알림
                    self._send_basic_status_notification(current_time, monitor_status, api_status, resource_info)
                
                # 개별 모니터링 시스템 상태 추가 체크
                if self.individual_monitors_enabled:
                    self._check_individual_monitors_status()
                
                self.log("📊 정기 상태 알림 전송 완료")
            
        except Exception as e:
            self.log(f"❌ 정기 상태 알림 실패: {e}")
            # 오류 발생 시에는 시간대 관계없이 알림 전송
            self.send_notification(
                f"❌ POSCO 워치햄스터 🛡️ 상태 알림 오류\n\n"
                f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"❌ 오류: {str(e)}\n"
                f"🔧 수동 확인이 필요합니다.",
                is_error=True
            )
    
    def _send_basic_status_notification(self, current_time, monitor_status, api_status, resource_info):
        """
        기본 상태 알림 전송 (스마트 시스템 비활성화 시 사용)
        
        Args:
            current_time (datetime): 현재 시간
            monitor_status (str): 모니터링 프로세스 상태
            api_status (str): API 연결 상태
            resource_info (str): 시스템 리소스 정보
        """
        self.send_notification(
            f"🐹 POSCO 워치햄스터 🛡️ 정기 상태 보고\n\n"
            f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔍 모니터링 프로세스: {monitor_status}\n"
            f"🌐 API 연결: {api_status}\n"
            f"{resource_info}\n"
            f"⏰ 다음 보고: {(current_time + timedelta(hours=2)).strftime('%H:%M')}\n"
            f"🚀 자동 복구 기능: 활성화"
        )
    
    def _check_individual_monitors_status(self):
        """
        개별 모니터링 시스템 상태 체크 및 보고
        
        최적화된 개별 모니터링 시스템들의 상태를 확인하고
        필요시 추가 정보를 제공합니다.
        """
        try:
            current_time = datetime.now()
            individual_status = {}
            
            # 뉴욕마켓워치 상태 체크
            if hasattr(self, 'newyork_monitor'):
                try:
                    ny_data = self.newyork_monitor.get_current_news_data()
                    ny_analysis = self.newyork_monitor.analyze_publish_pattern(ny_data)
                    individual_status['newyork'] = {
                        'published': ny_analysis.get('is_published_today', False),
                        'status': ny_analysis.get('analysis', '상태 불명')
                    }
                except Exception as e:
                    individual_status['newyork'] = {'error': str(e)}
            
            # 증시마감 상태 체크
            if hasattr(self, 'kospi_monitor'):
                try:
                    kospi_data = self.kospi_monitor.get_current_news_data()
                    kospi_analysis = self.kospi_monitor.analyze_publish_pattern(kospi_data)
                    individual_status['kospi'] = {
                        'published': kospi_analysis.get('is_published_today', False),
                        'status': kospi_analysis.get('analysis', '상태 불명')
                    }
                except Exception as e:
                    individual_status['kospi'] = {'error': str(e)}
            
            # 서환마감 상태 체크
            if hasattr(self, 'exchange_monitor'):
                try:
                    exchange_data = self.exchange_monitor.get_current_news_data()
                    exchange_analysis = self.exchange_monitor.analyze_publish_pattern(exchange_data)
                    individual_status['exchange'] = {
                        'published': exchange_analysis.get('is_published_today', False),
                        'status': exchange_analysis.get('analysis', '상태 불명')
                    }
                except Exception as e:
                    individual_status['exchange'] = {'error': str(e)}
            
            # 상태 요약 로그
            published_count = sum(1 for status in individual_status.values() 
                                if status.get('published', False))
            total_count = len(individual_status)
            
            if total_count > 0:
                self.log(f"📊 개별 모니터 상태: {published_count}/{total_count} 발행 완료")
                
                # 각 뉴스별 상태 로그
                news_names = {'newyork': '🌆뉴욕마켓워치', 'kospi': '📈증시마감', 'exchange': '💱서환마감'}
                for news_type, status in individual_status.items():
                    name = news_names.get(news_type, news_type)
                    if 'error' in status:
                        self.log(f"   {name}: ❌ 오류 - {status['error']}")
                    elif status.get('published', False):
                        self.log(f"   {name}: ✅ {status.get('status', '발행 완료')}")
                    else:
                        self.log(f"   {name}: ⏳ {status.get('status', '대기 중')}")
            
        except Exception as e:
            self.log(f"⚠️ 개별 모니터 상태 체크 실패: {e}")
    
    def get_enhanced_status_report(self):
        """
        향상된 상태 보고서 생성 (개별 모니터 정보 포함)
        
        Returns:
            dict: 향상된 상태 정보
        """
        try:
            # 기본 상태 정보
            basic_status = {
                'timestamp': datetime.now().isoformat(),
                'monitor_running': self.is_monitor_running(),
                'api_status': 'normal',  # 기본값
                'individual_monitors': {}
            }
            
            # 개별 모니터 상태 추가
            if self.individual_monitors_enabled:
                if hasattr(self, 'newyork_monitor'):
                    ny_data = self.newyork_monitor.get_current_news_data()
                    ny_analysis = self.newyork_monitor.analyze_publish_pattern(ny_data)
                    basic_status['individual_monitors']['newyork'] = {
                        'name': '뉴욕마켓워치',
                        'published_today': ny_analysis.get('is_published_today', False),
                        'status': ny_analysis.get('status', 'unknown'),
                        'analysis': ny_analysis.get('analysis', '분석 불가')
                    }
                
                if hasattr(self, 'kospi_monitor'):
                    kospi_data = self.kospi_monitor.get_current_news_data()
                    kospi_analysis = self.kospi_monitor.analyze_publish_pattern(kospi_data)
                    basic_status['individual_monitors']['kospi'] = {
                        'name': '증시마감',
                        'published_today': kospi_analysis.get('is_published_today', False),
                        'status': kospi_analysis.get('status', 'unknown'),
                        'analysis': kospi_analysis.get('analysis', '분석 불가')
                    }
                
                if hasattr(self, 'exchange_monitor'):
                    exchange_data = self.exchange_monitor.get_current_news_data()
                    exchange_analysis = self.exchange_monitor.analyze_publish_pattern(exchange_data)
                    basic_status['individual_monitors']['exchange'] = {
                        'name': '서환마감',
                        'published_today': exchange_analysis.get('is_published_today', False),
                        'status': exchange_analysis.get('status', 'unknown'),
                        'analysis': exchange_analysis.get('analysis', '분석 불가')
                    }
            
            return basic_status
            
        except Exception as e:
            self.log(f"⚠️ 향상된 상태 보고서 생성 실패: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _check_master_monitor_integration(self):
        """
        마스터 모니터링 시스템과의 통합 상태 체크
        
        워치햄스터와 마스터 모니터링 시스템 간의 연동 상태를 확인하고
        필요시 조정합니다.
        """
        try:
            current_time = datetime.now()
            
            # 마스터 모니터의 현재 전략 확인
            if hasattr(self.master_monitor, 'get_current_monitoring_strategy'):
                strategy = self.master_monitor.get_current_monitoring_strategy()
                
                # 전략 변경 시 로그 기록
                if not hasattr(self, '_last_master_strategy') or self._last_master_strategy != strategy['mode']:
                    self.log(f"🎛️ 마스터 모니터링 전략 변경: {strategy['description']}")
                    self._last_master_strategy = strategy['mode']
                
                # 집중 모니터링 시간대에는 워치햄스터 체크 간격 조정
                if strategy['interval'] <= 60:  # 1분 간격 집중 모니터링
                    # 워치햄스터도 더 자주 체크하도록 조정 (하지만 너무 자주는 안 됨)
                    if not hasattr(self, '_intensive_mode') or not self._intensive_mode:
                        self.log("🔥 집중 모니터링 모드 감지 - 워치햄스터 체크 빈도 증가")
                        self._intensive_mode = True
                else:
                    if hasattr(self, '_intensive_mode') and self._intensive_mode:
                        self.log("📋 일반 모니터링 모드 복귀 - 워치햄스터 체크 빈도 정상화")
                        self._intensive_mode = False
            
        except Exception as e:
            self.log(f"⚠️ 마스터 모니터 통합 체크 실패: {e}")
    
    def send_enhanced_status_notification(self):
        """
        향상된 상태 알림 전송 (개별 모니터 정보 포함)
        
        기존 상태 알림에 개별 모니터링 시스템의 상태 정보를 추가하여
        더 상세한 정보를 제공합니다.
        """
        try:
            enhanced_status = self.get_enhanced_status_report()
            current_time = datetime.now()
            
            # 기본 상태 정보
            monitor_status = "🟢 정상 작동" if enhanced_status.get('monitor_running', False) else "🔴 중단됨"
            
            message = f"🛡️ POSCO 워치햄스터 향상된 상태 보고\n\n"
            message += f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"🔍 모니터링 프로세스: {monitor_status}\n\n"
            
            # 개별 모니터 상태 추가
            individual_monitors = enhanced_status.get('individual_monitors', {})
            if individual_monitors:
                message += f"📊 개별 뉴스 모니터 상태:\n"
                
                for news_type, info in individual_monitors.items():
                    name = info.get('name', news_type)
                    published = info.get('published_today', False)
                    analysis = info.get('analysis', '분석 불가')
                    
                    status_emoji = "✅" if published else "⏳"
                    message += f"   {status_emoji} {name}: {analysis}\n"
                
                # 전체 발행 현황
                published_count = sum(1 for info in individual_monitors.values() 
                                    if info.get('published_today', False))
                total_count = len(individual_monitors)
                message += f"\n📈 전체 발행 현황: {published_count}/{total_count} 완료\n"
            
            # 시스템 통합 상태
            if self.master_monitor_enabled:
                message += f"\n🎛️ 마스터 모니터링: 연동 활성화"
            if self.individual_monitors_enabled:
                message += f"\n🔧 개별 모니터링: 연동 활성화"
            
            message += f"\n⏰ 다음 보고: {(current_time + timedelta(hours=2)).strftime('%H:%M')}"
            
            payload = {
                "botName": "POSCO 워치햄스터 🛡️",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": "향상된 상태 보고",
                "attachments": [{
                    "color": "#17a2b8",
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
                self.log("✅ 향상된 상태 알림 전송 성공")
                return True
            else:
                self.log(f"❌ 향상된 상태 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ 향상된 상태 알림 전송 오류: {e}")
            return False
    
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
            f"📅 스케줄 작업: 06:00, 06:10, 18:00, 18:10, 18:20, 07-17시 매시간\n"
            f"🌙 조용한 모드: 18시 이후 문제 발생 시에만 알림\n"
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
                    
                    # 프로세스 중단은 항상 알림 (시간대 무관)
                    self.send_notification(
                        f"⚠️ POSCO 모니터 프로세스 중단 감지\n\n"
                        f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"🔄 자동 재시작 중...",
                        is_error=True
                    )
                    
                    if self.start_monitor_process():
                        # 복구 성공 알림 (조용한 시간대 고려)
                        if self.is_quiet_hours():
                            # 야간: 간단한 복구 알림
                            self.send_notification(
                                f"✅ POSCO 모니터 자동 복구 완료 (야간 모드)\n\n"
                                f"📅 복구 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                        else:
                            # 주간: 상세한 복구 알림
                            self.send_notification(
                                f"✅ POSCO 모니터 자동 복구 완료\n\n"
                                f"📅 복구 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                f"🚀 모니터링 재개됨"
                            )
                    else:
                        # 복구 실패는 항상 상세 알림 (시간대 무관)
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
                
                # 스케줄된 작업 체크 및 실행
                self.check_scheduled_tasks()
                
                # 정기 상태 알림 (2시간마다)
                if (current_time - self.last_status_notification).total_seconds() >= self.status_notification_interval:
                    self.send_status_notification()
                    self.last_status_notification = current_time
                
                # 마스터 모니터링 시스템 상태 체크 (필요시)
                if self.master_monitor_enabled and hasattr(self, 'master_monitor'):
                    self._check_master_monitor_integration()
                
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
    # Windows 환경에서 UTF-8 출력 설정 개선
    if sys.platform == "win32":
        import codecs
        import locale
        
        # 콘솔 코드페이지를 UTF-8로 설정
        try:
            import subprocess
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass
        
        # 표준 출력/오류를 UTF-8로 설정
        try:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
        except:
            # 이미 설정된 경우 무시
            pass
        
        # 환경 변수 설정
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    watchhamster = PoscoMonitorWatchHamster()
    watchhamster.run()