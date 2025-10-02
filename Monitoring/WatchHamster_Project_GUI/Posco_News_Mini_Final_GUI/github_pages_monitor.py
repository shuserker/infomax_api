#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 접근성 확인 시스템 (GitHub Pages Monitor)
POSCO 뉴스 시스템용 완전 독립 GitHub Pages 모니터링 시스템

주요 기능:
- 🌐 배포 완료 후 실제 URL 접근 가능성 검증
- 📊 HTTP 상태 코드 확인 및 응답 시간 측정
- 🚨 접근 실패 시 GUI 알림 및 자동 재배포 옵션 제공
- 📈 GUI에서 GitHub Pages 상태 실시간 모니터링

Requirements: 1.2, 5.4 구현
"""

import os
import json
import time
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urljoin, urlparse


class PageStatus(Enum):
    """페이지 상태 열거형"""
    UNKNOWN = "unknown"
    CHECKING = "checking"
    ACCESSIBLE = "accessible"
    INACCESSIBLE = "inaccessible"
    ERROR = "error"
    TIMEOUT = "timeout"


class MonitoringMode(Enum):
    """모니터링 모드 열거형"""
    SINGLE_CHECK = "single_check"
    CONTINUOUS = "continuous"
    POST_DEPLOYMENT = "post_deployment"


@dataclass
class AccessibilityCheck:
    """접근성 확인 결과"""
    timestamp: str
    url: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    accessible: bool = False
    error_message: Optional[str] = None
    content_length: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    page_title: Optional[str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


@dataclass
class MonitoringSession:
    """모니터링 세션 정보"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    mode: MonitoringMode = MonitoringMode.SINGLE_CHECK
    target_url: str = ""
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    average_response_time: float = 0.0
    checks: List[AccessibilityCheck] = None
    is_active: bool = False
    
    def __post_init__(self):
        if self.checks is None:
            self.checks = []


class GitHubPagesMonitor:
    """GitHub Pages 접근성 확인 시스템 클래스 (완전 독립)"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """GitHub Pages 모니터 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # logs 폴더 설정
        self.logs_dir = os.path.join(os.path.dirname(self.script_dir), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 로그 파일들
        self.monitor_log = os.path.join(self.logs_dir, "github_pages_monitor.log")
        self.accessibility_log = os.path.join(self.logs_dir, "pages_accessibility.json")
        self.monitoring_sessions_log = os.path.join(self.logs_dir, "monitoring_sessions.json")
        
        # 현재 모니터링 세션
        self.current_session: Optional[MonitoringSession] = None
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_lock = threading.Lock()
        
        # GUI 콜백 함수들 (실시간 표시용)
        self.status_callbacks: List[Callable[[str, PageStatus, Dict], None]] = []
        self.accessibility_callbacks: List[Callable[[AccessibilityCheck], None]] = []
        self.alert_callbacks: List[Callable[[str, Dict], None]] = []
        self.redeploy_callbacks: List[Callable[[str], bool]] = []
        
        # 모니터링 설정
        self.check_interval = 30  # 30초마다 확인
        self.timeout = 30  # 30초 타임아웃
        self.max_retries = 3
        self.retry_delay = 10  # 10초 재시도 간격
        
        # 성능 임계값
        self.response_time_warning = 5.0  # 5초 이상 시 경고
        self.response_time_critical = 10.0  # 10초 이상 시 심각
        
        # 기본 GitHub Pages URL (설정에서 로드)
        self.default_pages_url = self._load_pages_url()
        
        # HTTP 세션 (연결 재사용)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'POSCO-News-Monitor/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.log_message("🔧 GitHub Pages 모니터링 시스템 초기화 완료 (스탠드얼론)")
    
    def log_message(self, message: str, level: str = "INFO"):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        try:
            with open(self.monitor_log, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"❌ 로그 파일 쓰기 실패: {e}")
    
    def _load_pages_url(self) -> str:
        """설정에서 GitHub Pages URL 로드"""
        try:
            config_file = os.path.join(os.path.dirname(self.script_dir), "config", "gui_config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('github_pages_url', 'https://username.github.io/repository')
        except Exception as e:
            self.log_message(f"⚠️ 설정 파일 로드 실패: {e}", "WARNING")
        
        return 'https://username.github.io/repository'  # 기본값
    
    def register_status_callback(self, callback: Callable[[str, PageStatus, Dict], None]):
        """상태 변경 콜백 등록 (GUI용)"""
        self.status_callbacks.append(callback)
    
    def register_accessibility_callback(self, callback: Callable[[AccessibilityCheck], None]):
        """접근성 확인 콜백 등록 (GUI용)"""
        self.accessibility_callbacks.append(callback)
    
    def register_alert_callback(self, callback: Callable[[str, Dict], None]):
        """알림 콜백 등록 (GUI용)"""
        self.alert_callbacks.append(callback)
    
    def register_redeploy_callback(self, callback: Callable[[str], bool]):
        """재배포 콜백 등록 (GUI용)"""
        self.redeploy_callbacks.append(callback)
    
    def _notify_status_change(self, url: str, status: PageStatus, details: Dict):
        """상태 변경 알림"""
        for callback in self.status_callbacks:
            try:
                callback(url, status, details)
            except Exception as e:
                self.log_message(f"❌ 상태 변경 콜백 오류: {e}", "ERROR")
    
    def _notify_accessibility_check(self, check: AccessibilityCheck):
        """접근성 확인 알림"""
        for callback in self.accessibility_callbacks:
            try:
                callback(check)
            except Exception as e:
                self.log_message(f"❌ 접근성 확인 콜백 오류: {e}", "ERROR")
    
    def _notify_alert(self, message: str, details: Dict):
        """알림 발송"""
        for callback in self.alert_callbacks:
            try:
                callback(message, details)
            except Exception as e:
                self.log_message(f"❌ 알림 콜백 오류: {e}", "ERROR")
    
    def _request_redeploy(self, reason: str) -> bool:
        """재배포 요청"""
        for callback in self.redeploy_callbacks:
            try:
                return callback(reason)
            except Exception as e:
                self.log_message(f"❌ 재배포 콜백 오류: {e}", "ERROR")
        return False
    
    def check_page_accessibility(self, url: str, timeout: Optional[int] = None) -> AccessibilityCheck:
        """단일 페이지 접근성 확인 (Requirements 1.2, 5.4)"""
        if timeout is None:
            timeout = self.timeout
        
        check = AccessibilityCheck(
            timestamp=datetime.now().isoformat(),
            url=url
        )
        
        try:
            self.log_message(f"🌐 페이지 접근성 확인 시작: {url}")
            
            # HTTP 요청 실행
            start_time = time.time()
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            end_time = time.time()
            
            # 응답 시간 계산
            check.response_time = end_time - start_time
            check.status_code = response.status_code
            check.content_length = len(response.content) if response.content else 0
            check.headers = dict(response.headers)
            
            # 페이지 제목 추출
            try:
                if 'text/html' in response.headers.get('content-type', ''):
                    import re
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
                    if title_match:
                        check.page_title = title_match.group(1).strip()
            except Exception:
                pass  # 제목 추출 실패는 무시
            
            # 접근성 판단
            if response.status_code == 200:
                check.accessible = True
                self.log_message(f"✅ 페이지 접근 성공: {url} (응답시간: {check.response_time:.2f}초)")
                
                # 응답 시간 경고
                if check.response_time > self.response_time_critical:
                    self.log_message(f"🚨 응답 시간 심각: {check.response_time:.2f}초", "CRITICAL")
                elif check.response_time > self.response_time_warning:
                    self.log_message(f"⚠️ 응답 시간 경고: {check.response_time:.2f}초", "WARNING")
                
            else:
                check.accessible = False
                check.error_message = f"HTTP {response.status_code}: {response.reason}"
                self.log_message(f"❌ 페이지 접근 실패: {url} - {check.error_message}")
            
        except requests.exceptions.Timeout:
            check.accessible = False
            check.error_message = f"타임아웃 ({timeout}초)"
            self.log_message(f"⏰ 페이지 접근 타임아웃: {url}")
            
        except requests.exceptions.ConnectionError as e:
            check.accessible = False
            check.error_message = f"연결 오류: {str(e)}"
            self.log_message(f"🔌 페이지 연결 오류: {url} - {str(e)}")
            
        except requests.exceptions.RequestException as e:
            check.accessible = False
            check.error_message = f"요청 오류: {str(e)}"
            self.log_message(f"❌ 페이지 요청 오류: {url} - {str(e)}")
            
        except Exception as e:
            check.accessible = False
            check.error_message = f"예상치 못한 오류: {str(e)}"
            self.log_message(f"💥 예상치 못한 오류: {url} - {str(e)}", "ERROR")
        
        # 접근성 확인 알림
        self._notify_accessibility_check(check)
        
        return check
    
    def verify_github_pages_deployment(self, url: Optional[str] = None, 
                                     max_wait_time: int = 300) -> Dict[str, Any]:
        """GitHub Pages 배포 후 접근성 검증 (Requirements 1.2, 5.4)"""
        if url is None:
            url = self.default_pages_url
        
        self.log_message(f"🚀 GitHub Pages 배포 검증 시작: {url}")
        
        verification_result = {
            "url": url,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_wait_time": 0,
            "checks_performed": 0,
            "final_accessible": False,
            "deployment_successful": False,
            "checks": [],
            "error_message": None
        }
        
        start_time = time.time()
        
        try:
            # GitHub Pages 빌드 대기 (초기 대기)
            self.log_message("⏳ GitHub Pages 빌드 대기 중... (30초)")
            time.sleep(30)
            
            # 접근성 확인 반복
            while time.time() - start_time < max_wait_time:
                current_wait_time = time.time() - start_time
                verification_result["total_wait_time"] = current_wait_time
                verification_result["checks_performed"] += 1
                
                self.log_message(f"🔍 접근성 확인 시도 #{verification_result['checks_performed']} (대기시간: {current_wait_time:.1f}초)")
                
                # 접근성 확인
                check = self.check_page_accessibility(url)
                verification_result["checks"].append(asdict(check))
                
                if check.accessible:
                    # 접근 성공
                    verification_result["final_accessible"] = True
                    verification_result["deployment_successful"] = True
                    verification_result["end_time"] = datetime.now().isoformat()
                    
                    self.log_message(f"✅ GitHub Pages 배포 검증 성공: {url}")
                    self._notify_status_change(url, PageStatus.ACCESSIBLE, {
                        "response_time": check.response_time,
                        "status_code": check.status_code,
                        "wait_time": current_wait_time
                    })
                    
                    break
                else:
                    # 접근 실패 - 재시도
                    self.log_message(f"⏳ 접근 실패, 재시도 대기... ({self.retry_delay}초)")
                    self._notify_status_change(url, PageStatus.CHECKING, {
                        "attempt": verification_result["checks_performed"],
                        "error": check.error_message,
                        "wait_time": current_wait_time
                    })
                    
                    time.sleep(self.retry_delay)
            
            # 최대 대기 시간 초과
            if not verification_result["final_accessible"]:
                verification_result["error_message"] = f"최대 대기 시간 초과 ({max_wait_time}초)"
                verification_result["end_time"] = datetime.now().isoformat()
                
                self.log_message(f"⏰ GitHub Pages 배포 검증 타임아웃: {url}")
                self._notify_status_change(url, PageStatus.TIMEOUT, {
                    "max_wait_time": max_wait_time,
                    "total_checks": verification_result["checks_performed"]
                })
                
                # 접근 실패 알림
                self._notify_alert(
                    f"GitHub Pages 접근 실패: {url}",
                    {
                        "url": url,
                        "wait_time": verification_result["total_wait_time"],
                        "checks_performed": verification_result["checks_performed"],
                        "auto_redeploy_available": True
                    }
                )
        
        except Exception as e:
            verification_result["error_message"] = f"검증 중 오류: {str(e)}"
            verification_result["end_time"] = datetime.now().isoformat()
            
            self.log_message(f"❌ GitHub Pages 배포 검증 오류: {str(e)}", "ERROR")
            self._notify_status_change(url, PageStatus.ERROR, {"error": str(e)})
        
        # 검증 결과 저장
        self._save_accessibility_result(verification_result)
        
        return verification_result
    
    def start_continuous_monitoring(self, url: Optional[str] = None, 
                                  check_interval: Optional[int] = None) -> str:
        """지속적인 모니터링 시작 (Requirements 5.4)"""
        if url is None:
            url = self.default_pages_url
        
        if check_interval is None:
            check_interval = self.check_interval
        
        with self.monitoring_lock:
            if self.monitoring_active:
                self.log_message("⚠️ 이미 모니터링이 진행 중입니다", "WARNING")
                return self.current_session.session_id if self.current_session else ""
            
            # 새 모니터링 세션 생성
            session_id = f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_session = MonitoringSession(
                session_id=session_id,
                start_time=datetime.now().isoformat(),
                mode=MonitoringMode.CONTINUOUS,
                target_url=url,
                is_active=True
            )
            
            self.monitoring_active = True
            
            # 모니터링 스레드 시작
            self.monitoring_thread = threading.Thread(
                target=self._continuous_monitoring_loop,
                args=(url, check_interval),
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.log_message(f"📊 지속적인 모니터링 시작: {url} (간격: {check_interval}초)")
            self._notify_status_change(url, PageStatus.CHECKING, {
                "session_id": session_id,
                "mode": "continuous",
                "interval": check_interval
            })
            
            return session_id
    
    def stop_continuous_monitoring(self):
        """지속적인 모니터링 중지"""
        with self.monitoring_lock:
            if not self.monitoring_active:
                return
            
            self.monitoring_active = False
            
            if self.current_session:
                self.current_session.is_active = False
                self.current_session.end_time = datetime.now().isoformat()
                
                # 평균 응답 시간 계산
                if self.current_session.checks:
                    response_times = [
                        check.response_time for check in self.current_session.checks 
                        if check.response_time is not None
                    ]
                    if response_times:
                        self.current_session.average_response_time = sum(response_times) / len(response_times)
                
                # 세션 저장
                self._save_monitoring_session(self.current_session)
                
                session_id = self.current_session.session_id
                url = self.current_session.target_url
                
                self.log_message(f"📊 지속적인 모니터링 중지: {session_id}")
                self._notify_status_change(url, PageStatus.UNKNOWN, {
                    "session_id": session_id,
                    "mode": "stopped"
                })
            
            # 모니터링 스레드 종료 대기
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
    
    def _continuous_monitoring_loop(self, url: str, check_interval: int):
        """지속적인 모니터링 루프"""
        try:
            while self.monitoring_active and self.current_session:
                # 접근성 확인
                check = self.check_page_accessibility(url)
                
                # 세션에 결과 추가
                self.current_session.checks.append(check)
                self.current_session.total_checks += 1
                
                if check.accessible:
                    self.current_session.successful_checks += 1
                    self._notify_status_change(url, PageStatus.ACCESSIBLE, {
                        "response_time": check.response_time,
                        "status_code": check.status_code,
                        "check_count": self.current_session.total_checks
                    })
                else:
                    self.current_session.failed_checks += 1
                    self._notify_status_change(url, PageStatus.INACCESSIBLE, {
                        "error": check.error_message,
                        "check_count": self.current_session.total_checks
                    })
                    
                    # 연속 실패 시 알림
                    recent_checks = self.current_session.checks[-5:]  # 최근 5���
                    if len(recent_checks) >= 3 and all(not c.accessible for c in recent_checks):
                        self._notify_alert(
                            f"GitHub Pages 연속 접근 실패: {url}",
                            {
                                "url": url,
                                "consecutive_failures": len([c for c in recent_checks if not c.accessible]),
                                "auto_redeploy_available": True
                            }
                        )
                
                # 다음 확인까지 대기
                time.sleep(check_interval)
                
        except Exception as e:
            self.log_message(f"❌ 지속적인 모니터링 루프 오류: {str(e)}", "ERROR")
        finally:
            self.monitoring_active = False
    
    def request_auto_redeploy(self, reason: str) -> bool:
        """자동 재배포 요청 (Requirements 1.2)"""
        self.log_message(f"🔄 자동 재배포 요청: {reason}")
        
        try:
            # 재배포 콜백 호출
            redeploy_success = self._request_redeploy(reason)
            
            if redeploy_success:
                self.log_message("✅ 자동 재배포 요청 성공")
                self._notify_alert(
                    "자동 재배포 시작됨",
                    {
                        "reason": reason,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                return True
            else:
                self.log_message("❌ 자동 재배포 요청 실패")
                self._notify_alert(
                    "자동 재배포 실패",
                    {
                        "reason": reason,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                return False
                
        except Exception as e:
            error_msg = f"자동 재배포 요청 중 오류: {str(e)}"
            self.log_message(f"❌ {error_msg}", "ERROR")
            self._notify_alert(error_msg, {"reason": reason})
            return False
    
    def _save_accessibility_result(self, result: Dict[str, Any]):
        """접근성 확인 결과 저장"""
        try:
            # 기존 결과들 로드
            existing_results = []
            if os.path.exists(self.accessibility_log):
                with open(self.accessibility_log, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
            
            # 새 결과 추가
            existing_results.append(result)
            
            # 최근 100개 결과만 유지
            if len(existing_results) > 100:
                existing_results = existing_results[-100:]
            
            # 파일에 저장
            with open(self.accessibility_log, 'w', encoding='utf-8') as f:
                json.dump(existing_results, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.log_message(f"❌ 접근성 결과 저장 실패: {str(e)}", "ERROR")
    
    def _save_monitoring_session(self, session: MonitoringSession):
        """모니터링 세션 저장"""
        try:
            # 기존 세션들 로드
            existing_sessions = []
            if os.path.exists(self.monitoring_sessions_log):
                with open(self.monitoring_sessions_log, 'r', encoding='utf-8') as f:
                    existing_sessions = json.load(f)
            
            # 세션을 JSON 직렬화 가능한 형태로 변환
            session_dict = asdict(session)
            session_dict['mode'] = session.mode.value
            
            # 새 세션 추가
            existing_sessions.append(session_dict)
            
            # 최근 50개 세션만 유지
            if len(existing_sessions) > 50:
                existing_sessions = existing_sessions[-50:]
            
            # 파일에 저장
            with open(self.monitoring_sessions_log, 'w', encoding='utf-8') as f:
                json.dump(existing_sessions, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.log_message(f"❌ 모니터링 세션 저장 실패: {str(e)}", "ERROR")
    
    def get_current_status(self) -> Dict[str, Any]:
        """현재 모니터링 상태 조회 (GUI용)"""
        try:
            if not self.current_session:
                return {
                    "monitoring_active": False,
                    "session_id": None,
                    "target_url": None,
                    "mode": None,
                    "total_checks": 0,
                    "successful_checks": 0,
                    "failed_checks": 0,
                    "success_rate": 0.0,
                    "average_response_time": 0.0,
                    "last_check": None
                }
            
            # 성공률 계산
            success_rate = 0.0
            if self.current_session.total_checks > 0:
                success_rate = (self.current_session.successful_checks / self.current_session.total_checks) * 100
            
            # 마지막 확인 결과
            last_check = None
            if self.current_session.checks:
                last_check_obj = self.current_session.checks[-1]
                last_check = {
                    "timestamp": last_check_obj.timestamp,
                    "accessible": last_check_obj.accessible,
                    "response_time": last_check_obj.response_time,
                    "status_code": last_check_obj.status_code,
                    "error_message": last_check_obj.error_message
                }
            
            return {
                "monitoring_active": self.monitoring_active,
                "session_id": self.current_session.session_id,
                "target_url": self.current_session.target_url,
                "mode": self.current_session.mode.value,
                "total_checks": self.current_session.total_checks,
                "successful_checks": self.current_session.successful_checks,
                "failed_checks": self.current_session.failed_checks,
                "success_rate": success_rate,
                "average_response_time": self.current_session.average_response_time,
                "last_check": last_check
            }
            
        except Exception as e:
            self.log_message(f"❌ 현재 상태 조회 실패: {str(e)}", "ERROR")
            return {"error": str(e)}
    
    def get_accessibility_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """접근성 확인 히스토리 조회"""
        try:
            if not os.path.exists(self.accessibility_log):
                return []
            
            with open(self.accessibility_log, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
            
            # 최신순으로 정렬하여 반환
            return sorted(all_results, key=lambda x: x.get('start_time', ''), reverse=True)[:limit]
            
        except Exception as e:
            self.log_message(f"❌ 접근성 히스토리 조회 실패: {str(e)}", "ERROR")
            return []
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """모니터링 통계 조회"""
        try:
            # 접근성 결과 통계
            accessibility_stats = {"total_checks": 0, "successful_checks": 0, "failed_checks": 0}
            if os.path.exists(self.accessibility_log):
                with open(self.accessibility_log, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    
                    for result in results:
                        accessibility_stats["total_checks"] += result.get("checks_performed", 0)
                        if result.get("final_accessible", False):
                            accessibility_stats["successful_checks"] += 1
                        else:
                            accessibility_stats["failed_checks"] += 1
            
            # 모니터링 세션 통계
            session_stats = {"total_sessions": 0, "active_sessions": 0}
            if os.path.exists(self.monitoring_sessions_log):
                with open(self.monitoring_sessions_log, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
                    session_stats["total_sessions"] = len(sessions)
                    session_stats["active_sessions"] = sum(1 for s in sessions if s.get("is_active", False))
            
            # 성공률 계산
            success_rate = 0.0
            if accessibility_stats["total_checks"] > 0:
                success_rate = (accessibility_stats["successful_checks"] / accessibility_stats["total_checks"]) * 100
            
            return {
                "accessibility": accessibility_stats,
                "sessions": session_stats,
                "success_rate": success_rate,
                "current_monitoring": self.monitoring_active,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log_message(f"❌ 모니터링 통계 조회 실패: {str(e)}", "ERROR")
            return {"error": str(e)}
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """오래된 로그 파일 정리"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            cutoff_timestamp = cutoff_time.isoformat()
            
            # 접근성 로그 정리
            if os.path.exists(self.accessibility_log):
                with open(self.accessibility_log, 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
                
                recent_results = [
                    r for r in all_results 
                    if r.get('start_time', '') > cutoff_timestamp
                ]
                
                if len(recent_results) != len(all_results):
                    with open(self.accessibility_log, 'w', encoding='utf-8') as f:
                        json.dump(recent_results, f, ensure_ascii=False, indent=2)
                    
                    removed_count = len(all_results) - len(recent_results)
                    self.log_message(f"🧹 오래된 접근성 로그 {removed_count}개 정리 완료")
            
            # 모니터링 세션 로그 정리
            if os.path.exists(self.monitoring_sessions_log):
                with open(self.monitoring_sessions_log, 'r', encoding='utf-8') as f:
                    all_sessions = json.load(f)
                
                recent_sessions = [
                    s for s in all_sessions 
                    if s.get('start_time', '') > cutoff_timestamp
                ]
                
                if len(recent_sessions) != len(all_sessions):
                    with open(self.monitoring_sessions_log, 'w', encoding='utf-8') as f:
                        json.dump(recent_sessions, f, ensure_ascii=False, indent=2)
                    
                    removed_count = len(all_sessions) - len(recent_sessions)
                    self.log_message(f"🧹 오래된 모니터링 세션 {removed_count}개 정리 완료")
            
        except Exception as e:
            self.log_message(f"❌ 로그 정리 중 오류: {str(e)}", "ERROR")


# 편의 함수들
def create_github_pages_monitor(base_dir: Optional[str] = None) -> GitHubPagesMonitor:
    """GitHub Pages 모니터 인스턴스 생성"""
    return GitHubPagesMonitor(base_dir)


def quick_accessibility_check(url: str, timeout: int = 30) -> bool:
    """빠른 접근성 확인 (단순 True/False 반환)"""
    monitor = create_github_pages_monitor()
    check = monitor.check_page_accessibility(url, timeout)
    return check.accessible


if __name__ == "__main__":
    # 테스트 코드
    print("🔧 GitHub Pages 모니터링 시스템 테스트")
    
    monitor = create_github_pages_monitor()
    
    # 테스트 URL
    test_url = "https://httpbin.org/status/200"  # 테스트용 URL
    
    # 단일 접근성 확인 테스트
    print(f"\n1️⃣ 단일 접근성 확인 테스트: {test_url}")
    check_result = monitor.check_page_accessibility(test_url)
    print(f"✅ 접근 가능: {check_result.accessible}")
    print(f"📊 응답 시간: {check_result.response_time:.2f}초")
    print(f"🔢 상태 코드: {check_result.status_code}")
    
    # 배포 검증 테스트
    print(f"\n2️⃣ 배포 검증 테스트: {test_url}")
    verification_result = monitor.verify_github_pages_deployment(test_url, max_wait_time=60)
    print(f"✅ 배포 성공: {verification_result['deployment_successful']}")
    print(f"📊 총 확인 횟수: {verification_result['checks_performed']}")
    print(f"⏱️ 총 대기 시간: {verification_result['total_wait_time']:.1f}초")
    
    # 현재 상태 조회 테스트
    print(f"\n3️⃣ 현재 상태 조회 테스트")
    current_status = monitor.get_current_status()
    print(f"📊 모니터링 활성: {current_status['monitoring_active']}")
    
    # 통계 조회 테스트
    print(f"\n4️⃣ 통계 조회 테스트")
    stats = monitor.get_monitoring_statistics()
    print(f"📈 성공률: {stats['success_rate']:.1f}%")
    
    print("\n✅ 테스트 완료")