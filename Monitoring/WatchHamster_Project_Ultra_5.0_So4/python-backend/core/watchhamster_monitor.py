# -*- coding: utf-8 -*-
"""
WatchHamster 모니터링 시스템

기존 WatchHamster_Project의 watchhamster_monitor.py, git_monitor.py, system_monitor.py를 
통합하여 비동기 처리를 지원하는 모던한 모니터링 시스템입니다.

주요 기능:
- 프로세스 감시 및 자동 재시작
- Git 상태 모니터링 및 자동 복구
- 시스템 리소스 모니터링 (CPU, 메모리, 디스크)
- 실시간 상태 업데이트 및 알림
- 자동 복구 시나리오 처리

작성자: AI Assistant
작성 일시: 2025-01-02
기반: WatchHamster_Project/core/watchhamster_monitor.py, git_monitor.py, system_monitor.py
"""

import asyncio
import subprocess
import psutil
import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class ProcessStatus(Enum):
    """프로세스 상태 열거형"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"


class SystemResourceLevel(Enum):
    """시스템 리소스 경고 레벨"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class GitStatus(Enum):
    """Git 상태 열거형"""
    CLEAN = "clean"
    MODIFIED = "modified"
    CONFLICT = "conflict"
    ERROR = "error"
    UPDATE_NEEDED = "update_needed"


@dataclass
class ProcessInfo:
    """프로세스 정보"""
    name: str
    status: ProcessStatus
    pid: Optional[int] = None
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    start_time: Optional[datetime] = None
    restart_count: int = 0
    health_score: int = 100
    error_message: Optional[str] = None


@dataclass
class SystemResourceInfo:
    """시스템 리소스 정보"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    available_memory_gb: float
    free_disk_gb: float
    level: SystemResourceLevel
    warnings: List[str]
    critical_issues: List[str]


@dataclass
class GitStatusInfo:
    """Git 상태 정보"""
    status: GitStatus
    current_branch: Optional[str] = None
    current_commit: Optional[str] = None
    uncommitted_changes: bool = False
    conflicts: List[str] = None
    ahead_commits: int = 0
    behind_commits: int = 0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []


@dataclass
class MonitoringStatus:
    """전체 모니터링 상태"""
    timestamp: datetime
    processes: Dict[str, ProcessInfo]
    system_resources: SystemResourceInfo
    git_status: GitStatusInfo
    overall_health: str
    uptime: timedelta
    alerts: List[str]


class WatchHamsterMonitor:
    """
    WatchHamster 통합 모니터링 시스템
    
    프로세스, Git, 시스템 리소스를 통합 모니터링하고
    자동 복구 기능을 제공하는 비동기 모니터링 시스템입니다.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """모니터링 시스템 초기화"""
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # 모니터링 설정
        self.process_check_interval = config.get('process_check_interval', 300)  # 5분
        self.git_check_interval = config.get('git_check_interval', 3600)  # 1시간
        self.resource_check_interval = config.get('resource_check_interval', 60)  # 1분
        
        # 관리 대상 프로세스
        self.managed_processes = config.get('managed_processes', [])
        
        # 상태 추적
        self.process_status: Dict[str, ProcessInfo] = {}
        self.system_start_time = datetime.now()
        self.last_git_check = datetime.now() - timedelta(hours=1)
        self.last_resource_check = datetime.now()
        
        # 복구 설정
        self.max_restart_attempts = config.get('max_restart_attempts', 3)
        self.restart_cooldown = config.get('restart_cooldown', 60)
        
        # 리소스 임계값
        self.cpu_warning_threshold = config.get('cpu_warning_threshold', 70.0)
        self.cpu_critical_threshold = config.get('cpu_critical_threshold', 85.0)
        self.memory_warning_threshold = config.get('memory_warning_threshold', 70.0)
        self.memory_critical_threshold = config.get('memory_critical_threshold', 85.0)
        self.disk_warning_threshold = config.get('disk_warning_threshold', 80.0)
        self.disk_critical_threshold = config.get('disk_critical_threshold', 90.0)
        
        # 콜백 함수들
        self.on_status_change: Optional[Callable[[MonitoringStatus], None]] = None
        self.on_alert: Optional[Callable[[str, str], None]] = None
        self.on_recovery: Optional[Callable[[str], None]] = None
        
        # 모니터링 루프 제어
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # 프로세스 상태 초기화
        self._initialize_process_tracking()
        
        self.logger.info("WatchHamster 모니터링 시스템 초기화 완료")
    
    def _setup_logging(self) -> logging.Logger:
        """로깅 시스템 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 파일 핸들러
            log_file = os.path.join(os.path.dirname(__file__), '../../logs/watchhamster_monitor.log')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 콘솔 핸들러
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 포매터
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_process_tracking(self):
        """프로세스 추적 초기화"""
        for process_name in self.managed_processes:
            self.process_status[process_name] = ProcessInfo(
                name=process_name,
                status=ProcessStatus.UNKNOWN,
                restart_count=0
            )
    
    async def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            self.logger.warning("이미 모니터링이 실행 중입니다")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("WatchHamster 모니터링 시작")
    
    async def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("WatchHamster 모니터링 중지")
    
    async def _monitoring_loop(self):
        """메인 모니터링 루프"""
        while self.is_monitoring:
            try:
                # 전체 상태 확인
                status = await self.get_monitoring_status()
                
                # 상태 변경 콜백 호출
                if self.on_status_change:
                    try:
                        self.on_status_change(status)
                    except Exception as e:
                        self.logger.error(f"상태 변경 콜백 오류: {e}")
                
                # 알림 처리
                await self._process_alerts(status)
                
                # 자동 복구 시도
                await self._attempt_auto_recovery(status)
                
                # 다음 체크까지 대기
                await asyncio.sleep(min(
                    self.process_check_interval,
                    self.resource_check_interval
                ))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기
    
    async def get_monitoring_status(self) -> MonitoringStatus:
        """현재 모니터링 상태 조회"""
        timestamp = datetime.now()
        
        # 프로세스 상태 확인
        await self._check_processes()
        
        # 시스템 리소스 확인
        system_resources = await self._check_system_resources()
        
        # Git 상태 확인 (주기적으로)
        git_status = await self._check_git_status()
        
        # 전체 건강도 판단
        overall_health = self._determine_overall_health(system_resources)
        
        # 알림 수집
        alerts = self._collect_alerts(system_resources, git_status)
        
        # 가동 시간 계산
        uptime = timestamp - self.system_start_time
        
        return MonitoringStatus(
            timestamp=timestamp,
            processes=self.process_status.copy(),
            system_resources=system_resources,
            git_status=git_status,
            overall_health=overall_health,
            uptime=uptime,
            alerts=alerts
        )
    
    async def _check_processes(self):
        """프로세스 상태 확인"""
        for process_name in self.managed_processes:
            try:
                process_info = await self._check_single_process(process_name)
                self.process_status[process_name] = process_info
            except Exception as e:
                self.logger.error(f"프로세스 {process_name} 확인 중 오류: {e}")
                self.process_status[process_name].status = ProcessStatus.ERROR
                self.process_status[process_name].error_message = str(e)
    
    async def _check_single_process(self, process_name: str) -> ProcessInfo:
        """개별 프로세스 상태 확인"""
        process_info = self.process_status.get(process_name, ProcessInfo(name=process_name, status=ProcessStatus.UNKNOWN))
        
        try:
            # 프로세스 검색
            running_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if process_name in cmdline or process_name in proc.info['name']:
                        running_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if running_processes:
                # 가장 최근 프로세스 선택
                latest_proc = max(running_processes, key=lambda p: p.info['create_time'])
                
                process_info.pid = latest_proc.info['pid']
                process_info.start_time = datetime.fromtimestamp(latest_proc.info['create_time'])
                process_info.status = ProcessStatus.RUNNING
                
                # 리소스 사용량 확인
                try:
                    proc_obj = psutil.Process(latest_proc.info['pid'])
                    process_info.cpu_percent = proc_obj.cpu_percent()
                    process_info.memory_percent = proc_obj.memory_percent()
                    
                    # 건강도 점수 계산
                    health_score = 100
                    if process_info.cpu_percent > 80:
                        health_score -= 30
                    elif process_info.cpu_percent > 50:
                        health_score -= 10
                    
                    if process_info.memory_percent > 80:
                        health_score -= 30
                    elif process_info.memory_percent > 50:
                        health_score -= 10
                    
                    process_info.health_score = max(0, health_score)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_info.status = ProcessStatus.ERROR
                    process_info.health_score = 0
            else:
                process_info.status = ProcessStatus.STOPPED
                process_info.pid = None
                process_info.health_score = 0
            
        except Exception as e:
            process_info.status = ProcessStatus.ERROR
            process_info.error_message = str(e)
            process_info.health_score = 0
        
        return process_info
    
    async def _check_system_resources(self) -> SystemResourceInfo:
        """시스템 리소스 확인"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 정보
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_memory_gb = memory.available / (1024**3)
            
            # 디스크 정보
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            free_disk_gb = disk.free / (1024**3)
            
            # 경고 및 중요 이슈 수집
            warnings = []
            critical_issues = []
            
            # CPU 경고
            if cpu_percent >= 95:
                critical_issues.append(f"CPU 사용률 위험: {cpu_percent:.1f}%")
            elif cpu_percent >= self.cpu_critical_threshold:
                critical_issues.append(f"CPU 사용률 높음: {cpu_percent:.1f}%")
            elif cpu_percent >= self.cpu_warning_threshold:
                warnings.append(f"CPU 사용률 주의: {cpu_percent:.1f}%")
            
            # 메모리 경고
            if memory_percent >= 95:
                critical_issues.append(f"메모리 사용률 위험: {memory_percent:.1f}%")
            elif memory_percent >= self.memory_critical_threshold:
                critical_issues.append(f"메모리 사용률 높음: {memory_percent:.1f}%")
            elif memory_percent >= self.memory_warning_threshold:
                warnings.append(f"메모리 사용률 주의: {memory_percent:.1f}%")
            
            # 디스크 경고
            if disk_percent >= 98:
                critical_issues.append(f"디스크 사용률 위험: {disk_percent:.1f}%")
            elif disk_percent >= self.disk_critical_threshold:
                critical_issues.append(f"디스크 사용률 높음: {disk_percent:.1f}%")
            elif disk_percent >= self.disk_warning_threshold:
                warnings.append(f"디스크 사용률 주의: {disk_percent:.1f}%")
            
            # 전체 레벨 결정
            if critical_issues:
                if any("위험" in issue for issue in critical_issues):
                    level = SystemResourceLevel.EMERGENCY
                else:
                    level = SystemResourceLevel.CRITICAL
            elif warnings:
                level = SystemResourceLevel.WARNING
            else:
                level = SystemResourceLevel.NORMAL
            
            return SystemResourceInfo(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                available_memory_gb=available_memory_gb,
                free_disk_gb=free_disk_gb,
                level=level,
                warnings=warnings,
                critical_issues=critical_issues
            )
            
        except Exception as e:
            self.logger.error(f"시스템 리소스 확인 중 오류: {e}")
            return SystemResourceInfo(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                available_memory_gb=0.0,
                free_disk_gb=0.0,
                level=SystemResourceLevel.CRITICAL,
                warnings=[],
                critical_issues=[f"시스템 모니터링 오류: {str(e)}"]
            )
    
    async def _check_git_status(self) -> GitStatusInfo:
        """Git 상태 확인"""
        now = datetime.now()
        
        # 주기적으로만 Git 상태 확인
        if (now - self.last_git_check).total_seconds() < self.git_check_interval:
            # 이전 상태 반환 (캐시된 상태가 있다면)
            return getattr(self, '_cached_git_status', GitStatusInfo(status=GitStatus.CLEAN))
        
        self.last_git_check = now
        
        try:
            # Git 저장소 확인
            result = await self._run_git_command(['git', 'rev-parse', '--git-dir'])
            if not result[0]:
                git_status = GitStatusInfo(
                    status=GitStatus.ERROR,
                    error_message="Git 저장소가 아닙니다"
                )
                self._cached_git_status = git_status
                return git_status
            
            # 현재 브랜치 확인
            result = await self._run_git_command(['git', 'branch', '--show-current'])
            current_branch = result[1] if result[0] else None
            
            # 현재 커밋 확인
            result = await self._run_git_command(['git', 'rev-parse', 'HEAD'])
            current_commit = result[1][:8] if result[0] else None
            
            # 작업 디렉토리 상태 확인
            result = await self._run_git_command(['git', 'status', '--porcelain'])
            uncommitted_changes = bool(result[1]) if result[0] else False
            
            # 충돌 확인
            conflicts = []
            if result[0] and result[1]:
                for line in result[1].split('\n'):
                    if line.startswith('UU'):
                        conflicts.append(line[3:])
            
            # 상태 결정
            if conflicts:
                status = GitStatus.CONFLICT
            elif uncommitted_changes:
                status = GitStatus.MODIFIED
            else:
                status = GitStatus.CLEAN
            
            git_status = GitStatusInfo(
                status=status,
                current_branch=current_branch,
                current_commit=current_commit,
                uncommitted_changes=uncommitted_changes,
                conflicts=conflicts
            )
            
            self._cached_git_status = git_status
            return git_status
            
        except Exception as e:
            self.logger.error(f"Git 상태 확인 중 오류: {e}")
            git_status = GitStatusInfo(
                status=GitStatus.ERROR,
                error_message=str(e)
            )
            self._cached_git_status = git_status
            return git_status
    
    async def _run_git_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str]:
        """Git 명령어 비동기 실행"""
        try:
            # 페이저 비활성화를 위한 환경 변수 설정
            env = os.environ.copy()
            env['GIT_PAGER'] = ''
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=os.path.dirname(__file__)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            success = process.returncode == 0
            output = stdout.decode('utf-8').strip()
            
            return success, output
            
        except asyncio.TimeoutError:
            self.logger.error(f"Git 명령어 타임아웃: {' '.join(command)}")
            return False, ""
        except Exception as e:
            self.logger.error(f"Git 명령어 실행 오류: {e}")
            return False, ""
    
    def _determine_overall_health(self, system_resources: SystemResourceInfo) -> str:
        """전체 건강도 판단"""
        # 프로세스 상태 확인
        running_processes = sum(1 for p in self.process_status.values() 
                              if p.status == ProcessStatus.RUNNING)
        total_processes = len(self.process_status)
        
        process_health_ratio = running_processes / total_processes if total_processes > 0 else 0
        
        # 시스템 리소스 상태
        resource_level = system_resources.level
        
        # 종합 판단
        if resource_level == SystemResourceLevel.EMERGENCY or process_health_ratio < 0.5:
            return "critical"
        elif resource_level == SystemResourceLevel.CRITICAL or process_health_ratio < 0.8:
            return "warning"
        elif resource_level == SystemResourceLevel.WARNING or process_health_ratio < 1.0:
            return "degraded"
        else:
            return "healthy"
    
    def _collect_alerts(self, system_resources: SystemResourceInfo, git_status: GitStatusInfo) -> List[str]:
        """알림 수집"""
        alerts = []
        
        # 시스템 리소스 알림
        alerts.extend(system_resources.critical_issues)
        alerts.extend(system_resources.warnings)
        
        # 프로세스 알림
        failed_processes = [name for name, info in self.process_status.items() 
                          if info.status != ProcessStatus.RUNNING]
        if failed_processes:
            alerts.append(f"중단된 프로세스: {', '.join(failed_processes)}")
        
        # Git 알림
        if git_status.status == GitStatus.CONFLICT:
            alerts.append(f"Git 충돌 발생: {', '.join(git_status.conflicts)}")
        elif git_status.status == GitStatus.ERROR:
            alerts.append(f"Git 오류: {git_status.error_message}")
        
        return alerts
    
    async def _process_alerts(self, status: MonitoringStatus):
        """알림 처리"""
        if not status.alerts:
            return
        
        # 중요도별 알림 분류
        critical_alerts = [alert for alert in status.alerts 
                         if any(keyword in alert.lower() for keyword in ['위험', '중단', '충돌', '오류'])]
        warning_alerts = [alert for alert in status.alerts if alert not in critical_alerts]
        
        # 알림 콜백 호출
        if self.on_alert:
            try:
                if critical_alerts:
                    self.on_alert("critical", "; ".join(critical_alerts))
                elif warning_alerts:
                    self.on_alert("warning", "; ".join(warning_alerts))
            except Exception as e:
                self.logger.error(f"알림 콜백 오류: {e}")
    
    async def _attempt_auto_recovery(self, status: MonitoringStatus):
        """자동 복구 시도"""
        # 중단된 프로세스 재시작 시도
        for name, process_info in status.processes.items():
            if (process_info.status == ProcessStatus.STOPPED and 
                process_info.restart_count < self.max_restart_attempts):
                
                try:
                    await self._restart_process(name)
                    if self.on_recovery:
                        self.on_recovery(f"프로세스 {name} 자동 재시작")
                except Exception as e:
                    self.logger.error(f"프로세스 {name} 자동 재시작 실패: {e}")
        
        # Git 충돌 자동 해결 시도
        if status.git_status.status == GitStatus.CONFLICT:
            try:
                success = await self._attempt_git_recovery()
                if success and self.on_recovery:
                    self.on_recovery("Git 충돌 자동 해결")
            except Exception as e:
                self.logger.error(f"Git 자동 복구 실패: {e}")
    
    async def _restart_process(self, process_name: str):
        """프로세스 재시작"""
        process_info = self.process_status[process_name]
        
        # 재시작 쿨다운 확인
        if process_info.start_time:
            time_since_start = (datetime.now() - process_info.start_time).total_seconds()
            if time_since_start < self.restart_cooldown:
                self.logger.warning(f"프로세스 {process_name} 재시작 쿨다운 중")
                return
        
        # 기존 프로세스 종료
        if process_info.pid:
            try:
                proc = psutil.Process(process_info.pid)
                proc.terminate()
                await asyncio.sleep(5)  # 정상 종료 대기
                if proc.is_running():
                    proc.kill()  # 강제 종료
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 새 프로세스 시작 (구체적인 시작 로직은 설정에 따라)
        start_command = self.config.get('process_commands', {}).get(process_name)
        if start_command:
            try:
                process = await asyncio.create_subprocess_exec(*start_command.split())
                process_info.restart_count += 1
                process_info.status = ProcessStatus.STARTING
                self.logger.info(f"프로세스 {process_name} 재시작 시도 ({process_info.restart_count}회)")
            except Exception as e:
                self.logger.error(f"프로세스 {process_name} 시작 실패: {e}")
                process_info.status = ProcessStatus.ERROR
                process_info.error_message = str(e)
    
    async def _attempt_git_recovery(self) -> bool:
        """Git 자동 복구 시도"""
        try:
            # 충돌 파일 목록 확인
            result = await self._run_git_command(['git', 'diff', '--name-only', '--diff-filter=U'])
            if not result[0]:
                return False
            
            conflict_files = [f for f in result[1].split('\n') if f]
            if not conflict_files:
                return False
            
            # 간단한 자동 해결 시도 (우리 버전 선택)
            for file in conflict_files:
                await self._run_git_command(['git', 'checkout', '--ours', file])
                await self._run_git_command(['git', 'add', file])
            
            # 병합 완료
            result = await self._run_git_command(['git', 'rebase', '--continue'])
            if result[0]:
                self.logger.info(f"Git 충돌 자동 해결 완료: {', '.join(conflict_files)}")
                return True
            else:
                # 리베이스 중단
                await self._run_git_command(['git', 'rebase', '--abort'])
                return False
                
        except Exception as e:
            self.logger.error(f"Git 자동 복구 중 오류: {e}")
            # 안전을 위해 리베이스 중단
            await self._run_git_command(['git', 'rebase', '--abort'])
            return False
    
    def generate_status_message(self, status: MonitoringStatus, message_type: str = "status") -> str:
        """상태 메시지 생성"""
        try:
            timestamp = status.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # 메시지 헤더
            if message_type == "critical":
                header = "🚨 WatchHamster 긴급 알림"
            elif message_type == "warning":
                header = "⚠️ WatchHamster 경고"
            else:
                header = "🐹 WatchHamster 상태 보고"
            
            message_parts = [
                f"{header}\n",
                f"📅 시간: {timestamp}\n",
                f"⏱️ 가동 시간: {self._format_timedelta(status.uptime)}\n",
                f"🎯 전체 상태: {status.overall_health}\n\n"
            ]
            
            # 프로세스 상태
            running_count = sum(1 for p in status.processes.values() 
                              if p.status == ProcessStatus.RUNNING)
            total_count = len(status.processes)
            
            if running_count == total_count:
                message_parts.append(f"🟢 프로세스: {running_count}/{total_count} 모두 정상\n")
            else:
                message_parts.append(f"🔴 프로세스: {running_count}/{total_count} 정상\n")
                failed_processes = [name for name, info in status.processes.items() 
                                  if info.status != ProcessStatus.RUNNING]
                for process_name in failed_processes:
                    restart_count = status.processes[process_name].restart_count
                    message_parts.append(f"  ❌ {process_name} (재시작: {restart_count}회)\n")
            
            # 시스템 리소스
            resources = status.system_resources
            level_emoji = {
                SystemResourceLevel.NORMAL: "🟢",
                SystemResourceLevel.WARNING: "🟡",
                SystemResourceLevel.CRITICAL: "🟠",
                SystemResourceLevel.EMERGENCY: "🔴"
            }.get(resources.level, "⚪")
            
            message_parts.append(f"\n{level_emoji} 시스템 리소스:\n")
            message_parts.append(f"  💻 CPU: {resources.cpu_percent:.1f}%\n")
            message_parts.append(f"  🧠 메모리: {resources.memory_percent:.1f}% ({resources.available_memory_gb:.1f}GB 사용가능)\n")
            message_parts.append(f"  💾 디스크: {resources.disk_percent:.1f}% ({resources.free_disk_gb:.1f}GB 여유)\n")
            
            # Git 상태
            if status.git_status.status != GitStatus.CLEAN:
                git_emoji = {
                    GitStatus.MODIFIED: "📝",
                    GitStatus.CONFLICT: "⚠️",
                    GitStatus.ERROR: "❌",
                    GitStatus.UPDATE_NEEDED: "🔄"
                }.get(status.git_status.status, "📋")
                
                message_parts.append(f"\n{git_emoji} Git 상태: {status.git_status.status.value}\n")
                if status.git_status.current_branch:
                    message_parts.append(f"  🌿 브랜치: {status.git_status.current_branch}\n")
                if status.git_status.current_commit:
                    message_parts.append(f"  📝 커밋: {status.git_status.current_commit}\n")
            
            # 알림 사항
            if status.alerts:
                message_parts.append(f"\n🔔 알림 ({len(status.alerts)}개):\n")
                for alert in status.alerts[:5]:  # 최대 5개만 표시
                    message_parts.append(f"  • {alert}\n")
            
            return "".join(message_parts).rstrip()
            
        except Exception as e:
            self.logger.error(f"상태 메시지 생성 중 오류: {e}")
            return (f"🐹 WatchHamster 상태 보고\n\n"
                   f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                   f"❌ 메시지 생성 오류: {e}")
    
    def _format_timedelta(self, td: timedelta) -> str:
        """시간 간격을 읽기 쉬운 형태로 포맷"""
        total_seconds = int(td.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}일 {hours}시간 {minutes}분"
        elif hours > 0:
            return f"{hours}시간 {minutes}분"
        else:
            return f"{minutes}분"
    
    def get_process_info(self, process_name: str) -> Optional[ProcessInfo]:
        """특정 프로세스 정보 조회"""
        return self.process_status.get(process_name)
    
    def get_all_process_info(self) -> Dict[str, ProcessInfo]:
        """모든 프로세스 정보 조회"""
        return self.process_status.copy()
    
    async def restart_process_manually(self, process_name: str) -> bool:
        """수동 프로세스 재시작"""
        if process_name not in self.managed_processes:
            self.logger.error(f"관리되지 않는 프로세스: {process_name}")
            return False
        
        try:
            await self._restart_process(process_name)
            return True
        except Exception as e:
            self.logger.error(f"수동 프로세스 재시작 실패: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """현재 설정 반환"""
        return {
            'process_check_interval': self.process_check_interval,
            'git_check_interval': self.git_check_interval,
            'resource_check_interval': self.resource_check_interval,
            'managed_processes': self.managed_processes,
            'max_restart_attempts': self.max_restart_attempts,
            'restart_cooldown': self.restart_cooldown,
            'thresholds': {
                'cpu_warning': self.cpu_warning_threshold,
                'cpu_critical': self.cpu_critical_threshold,
                'memory_warning': self.memory_warning_threshold,
                'memory_critical': self.memory_critical_threshold,
                'disk_warning': self.disk_warning_threshold,
                'disk_critical': self.disk_critical_threshold
            }
        }


# 팩토리 함수
def create_monitor(config: Dict[str, Any]) -> WatchHamsterMonitor:
    """모니터 팩토리 함수"""
    return WatchHamsterMonitor(config)


if __name__ == "__main__":
    # 테스트 코드
    import asyncio
    
    async def test_monitor():
        """모니터 테스트"""
        config = {
            'managed_processes': ['python', 'node'],
            'process_check_interval': 10,
            'git_check_interval': 60,
            'resource_check_interval': 5,
            'max_restart_attempts': 3,
            'restart_cooldown': 30
        }
        
        monitor = WatchHamsterMonitor(config)
        
        # 콜백 함수 설정
        def on_status_change(status):
            print(f"상태 변경: {status.overall_health}")
        
        def on_alert(level, message):
            print(f"알림 [{level}]: {message}")
        
        def on_recovery(message):
            print(f"복구: {message}")
        
        monitor.on_status_change = on_status_change
        monitor.on_alert = on_alert
        monitor.on_recovery = on_recovery
        
        print("=== WatchHamster 모니터링 시스템 테스트 ===")
        
        # 상태 확인 테스트
        status = await monitor.get_monitoring_status()
        print(f"전체 상태: {status.overall_health}")
        print(f"프로세스 수: {len(status.processes)}")
        print(f"시스템 리소스 레벨: {status.system_resources.level.value}")
        print(f"Git 상태: {status.git_status.status.value}")
        
        # 상태 메시지 생성 테스트
        message = monitor.generate_status_message(status)
        print(f"\n상태 메시지:\n{message}")
        
        # 짧은 모니터링 테스트
        print("\n모니터링 시작 (10초)...")
        await monitor.start_monitoring()
        await asyncio.sleep(10)
        await monitor.stop_monitoring()
        print("모니터링 중지")
    
    # 테스트 실행
    asyncio.run(test_monitor())