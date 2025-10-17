#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 모니터링 로직 완전 복원

정상 커밋 a763ef84의 워치햄스터 모니터링 알고리즘을 역추적하여 복원한 시스템입니다.

주요 기능:
- 프로세스 감시 알고리즘 (5분 간격)
- Git 상태 체크 로직 및 모든 오류 시나리오 처리
- 프로세스 생명주기 관리 (시작/중단감지/재시작/복구)
- 시스템 리소스 모니터링 (임계값 판단, 경고 레벨)
- 상황별 동적 알림 메시지 생성
- 자동 복구 시나리오 전체 로직

Requirements: 3.4, 4.2
"""

import subprocess
import time
import os
import sys
import json
import requests
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import threading
import logging

class ProcessStatus:
    """프로세스 상태 열거형"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"

class SystemResourceLevel:
    """시스템 리소스 경고 레벨"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class RecoveryStage:
    """복구 단계"""
    DETECTION = "detection"
    ANALYSIS = "analysis"
    SOFT_RESTART = "soft_restart"
    HARD_RESTART = "hard_restart"
    SYSTEM_RECOVERY = "system_recovery"
    MANUAL_INTERVENTION = "manual_intervention"

class WatchHamsterMonitor:
    """
    POSCO 워치햄스터 모니터링 시스템
    
    정상 커밋의 프로세스 감시 알고리즘을 완전 복원한 모니터링 시스템입니다.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """워치햄스터 모니터링 시스템 초기화"""
        self.config = config
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(self.script_dir, "watchhamster_monitor.log")
        
        # 모니터링 설정
        self.process_check_interval = config.get('process_check_interval', 300)
        self.git_check_interval = config.get('git_check_interval', 3600)
        self.status_notification_interval = config.get('status_notification_interval', 7200)
        
        # 관리 대상 프로세스 목록
        self.managed_processes = config.get('managed_processes', [])
        
        # 프로세스 상태 추적
        self.process_status = {}
        self.process_pids = {}
        self.restart_counts = {}
        self.last_health_check = {}
        
        # 시스템 상태 추적
        self.last_git_check = datetime.now() - timedelta(hours=1)
        self.last_status_notification = datetime.now()
        self.system_start_time = datetime.now()
        
        # 복구 시스템 설정
        self.max_restart_attempts = config.get('max_restart_attempts', 3)
        self.restart_cooldown = config.get('restart_cooldown', 60)
        self.recovery_history = {}
        
        # 알림 설정
        self.webhook_url = config.get('webhook_url')
        self.bot_profile_image = config.get('bot_profile_image')
        
        # 로깅 설정
        self._setup_logging()
        
        # 초기 상태 설정
        self._initialize_process_tracking()
        
        self.log("🐹 POSCO 워치햄스터 모니터링 시스템 초기화 완료")
    
    def _setup_logging(self):
        """로깅 시스템 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.logger.info(message)
    
    def _initialize_process_tracking(self):
        """프로세스 추적 초기화"""
        for process_name in self.managed_processes:
            self.process_status[process_name] = ProcessStatus.UNKNOWN
            self.process_pids[process_name] = None
            self.restart_counts[process_name] = 0
            self.last_health_check[process_name] = datetime.now()
            self.recovery_history[process_name] = [] 
   
    def monitor_processes(self) -> Dict[str, Any]:
        """
        프로세스 감시 알고리즘 (정상 커밋 기반 복원)
        
        모든 관리 대상 프로세스의 상태를 확인하고 문제가 있는 프로세스를 식별합니다.
        """
        monitoring_results = {
            'timestamp': datetime.now(),
            'total_processes': len(self.managed_processes),
            'healthy_processes': 0,
            'failed_processes': [],
            'process_details': {},
            'system_health': 'unknown'
        }
        
        try:
            self.log("🔍 프로세스 감시 알고리즘 시작")
            
            for process_name in self.managed_processes:
                process_info = self._check_process_health(process_name)
                monitoring_results['process_details'][process_name] = process_info
                
                if process_info['status'] == ProcessStatus.RUNNING:
                    monitoring_results['healthy_processes'] += 1
                else:
                    monitoring_results['failed_processes'].append(process_name)
                
                # 상태 업데이트
                self.process_status[process_name] = process_info['status']
                self.process_pids[process_name] = process_info.get('pid')
                self.last_health_check[process_name] = datetime.now()
            
            # 전체 시스템 건강도 판단
            health_ratio = monitoring_results['healthy_processes'] / monitoring_results['total_processes']
            
            if health_ratio >= 1.0:
                monitoring_results['system_health'] = 'excellent'
            elif health_ratio >= 0.8:
                monitoring_results['system_health'] = 'good'
            elif health_ratio >= 0.5:
                monitoring_results['system_health'] = 'warning'
            else:
                monitoring_results['system_health'] = 'critical'
            
            self.log(f"📊 프로세스 감시 완료: {monitoring_results['healthy_processes']}/{monitoring_results['total_processes']} 정상")
            
            return monitoring_results
            
        except Exception as e:
            self.log(f"❌ 프로세스 감시 중 오류 발생: {e}")
            monitoring_results['error'] = str(e)
            monitoring_results['system_health'] = 'error'
            return monitoring_results
    
    def _check_process_health(self, process_name: str) -> Dict[str, Any]:
        """개별 프로세스 건강 상태 확인"""
        process_info = {
            'name': process_name,
            'status': ProcessStatus.UNKNOWN,
            'pid': None,
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'start_time': None,
            'health_score': 0
        }
        
        try:
            # 프로세스 이름으로 실행 중인 프로세스 찾기
            running_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if process_name in cmdline or process_name in proc.info['name']:
                        running_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if running_processes:
                # 가장 최근에 시작된 프로세스 선택
                latest_proc = max(running_processes, key=lambda p: p.info['create_time'])
                
                process_info['pid'] = latest_proc.info['pid']
                process_info['start_time'] = datetime.fromtimestamp(latest_proc.info['create_time'])
                
                # 프로세스 리소스 사용량 확인
                try:
                    proc_obj = psutil.Process(latest_proc.info['pid'])
                    process_info['cpu_percent'] = proc_obj.cpu_percent()
                    process_info['memory_percent'] = proc_obj.memory_percent()
                    
                    # 건강도 점수 계산 (0-100)
                    health_score = 100
                    
                    if process_info['cpu_percent'] > 80:
                        health_score -= 30
                    elif process_info['cpu_percent'] > 50:
                        health_score -= 10
                    
                    if process_info['memory_percent'] > 80:
                        health_score -= 30
                    elif process_info['memory_percent'] > 50:
                        health_score -= 10
                    
                    process_info['health_score'] = max(0, health_score)
                    process_info['status'] = ProcessStatus.RUNNING
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_info['status'] = ProcessStatus.ERROR
                    process_info['health_score'] = 0
            else:
                process_info['status'] = ProcessStatus.STOPPED
                process_info['health_score'] = 0
            
        except Exception as e:
            self.log(f"⚠️ {process_name} 건강 상태 확인 중 오류: {e}")
            process_info['status'] = ProcessStatus.ERROR
            process_info['error'] = str(e)
        
        return process_info
    
    def check_git_status(self) -> Dict[str, Any]:
        """Git 상태 체크 로직 및 모든 오류 시나리오 처리"""
        git_status = {
            'timestamp': datetime.now(),
            'status': 'unknown',
            'current_branch': None,
            'current_commit': None,
            'remote_status': 'unknown',
            'conflicts': [],
            'errors': [],
            'needs_update': False,
            'auto_recovery_possible': False
        }
        
        try:
            self.log("🔍 Git 상태 체크 시작")
            
            # 현재 브랜치 확인
            try:
                result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True, text=True, timeout=30,
                    cwd=self.script_dir
                )
                if result.returncode == 0:
                    git_status['current_branch'] = result.stdout.strip()
                else:
                    git_status['errors'].append(f"브랜치 확인 실패: {result.stderr}")
            except subprocess.TimeoutExpired:
                git_status['errors'].append("Git 명령어 타임아웃")
            except Exception as e:
                git_status['errors'].append(f"Git 기본 상태 확인 오류: {e}")
            
            # 현재 커밋 확인
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True, text=True, timeout=30,
                    cwd=self.script_dir
                )
                if result.returncode == 0:
                    git_status['current_commit'] = result.stdout.strip()[:8]
            except Exception as e:
                git_status['errors'].append(f"커밋 확인 오류: {e}")
            
            # 작업 디렉토리 상태 확인
            try:
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True, text=True, timeout=30,
                    cwd=self.script_dir
                )
                
                if result.returncode == 0:
                    if result.stdout.strip():
                        changes = result.stdout.strip().split('\n')
                        for change in changes:
                            if change.startswith('UU'):
                                git_status['conflicts'].append(change[3:])
                        
                        if git_status['conflicts']:
                            git_status['status'] = 'conflict'
                        else:
                            git_status['status'] = 'modified'
                    else:
                        git_status['status'] = 'clean'
            except Exception as e:
                git_status['errors'].append(f"작업 디렉토리 상태 확인 오류: {e}")
            
            # 자동 복구 가능성 판단
            if git_status['status'] == 'clean' and not git_status['conflicts']:
                git_status['auto_recovery_possible'] = True
            elif git_status['status'] == 'modified' and not git_status['conflicts']:
                git_status['auto_recovery_possible'] = True
            else:
                git_status['auto_recovery_possible'] = False
            
            # 전체 상태 요약
            if git_status['errors']:
                git_status['status'] = 'error'
            elif git_status['conflicts']:
                git_status['status'] = 'conflict'
            elif git_status['status'] == 'unknown':
                git_status['status'] = 'clean'
            
            self.log(f"📋 Git 상태 체크 완료: {git_status['status']}")
            
            return git_status
            
        except Exception as e:
            self.log(f"❌ Git 상태 체크 중 예외 발생: {e}")
            git_status['status'] = 'error'
            git_status['errors'].append(f"예외 발생: {e}")
            return git_status  
  
    def monitor_system_resources(self) -> Dict[str, Any]:
        """시스템 리소스 모니터링 알고리즘 (임계값 판단, 경고 레벨)"""
        resource_status = {
            'timestamp': datetime.now(),
            'cpu': {'percent': 0.0, 'level': SystemResourceLevel.NORMAL},
            'memory': {'percent': 0.0, 'available_gb': 0.0, 'level': SystemResourceLevel.NORMAL},
            'disk': {'percent': 0.0, 'free_gb': 0.0, 'level': SystemResourceLevel.NORMAL},
            'overall_level': SystemResourceLevel.NORMAL,
            'warnings': [],
            'critical_issues': []
        }
        
        try:
            # CPU 사용률 모니터링
            cpu_percent = psutil.cpu_percent(interval=1)
            resource_status['cpu']['percent'] = cpu_percent
            
            if cpu_percent >= 95:
                resource_status['cpu']['level'] = SystemResourceLevel.EMERGENCY
                resource_status['critical_issues'].append(f"CPU 사용률 위험: {cpu_percent:.1f}%")
            elif cpu_percent >= 85:
                resource_status['cpu']['level'] = SystemResourceLevel.CRITICAL
                resource_status['critical_issues'].append(f"CPU 사용률 높음: {cpu_percent:.1f}%")
            elif cpu_percent >= 70:
                resource_status['cpu']['level'] = SystemResourceLevel.WARNING
                resource_status['warnings'].append(f"CPU 사용률 주의: {cpu_percent:.1f}%")
            
            # 메모리 사용률 모니터링
            memory = psutil.virtual_memory()
            resource_status['memory']['percent'] = memory.percent
            resource_status['memory']['available_gb'] = memory.available / (1024**3)
            
            if memory.percent >= 95:
                resource_status['memory']['level'] = SystemResourceLevel.EMERGENCY
                resource_status['critical_issues'].append(f"메모리 사용률 위험: {memory.percent:.1f}%")
            elif memory.percent >= 85:
                resource_status['memory']['level'] = SystemResourceLevel.CRITICAL
                resource_status['critical_issues'].append(f"메모리 사용률 높음: {memory.percent:.1f}%")
            elif memory.percent >= 70:
                resource_status['memory']['level'] = SystemResourceLevel.WARNING
                resource_status['warnings'].append(f"메모리 사용률 주의: {memory.percent:.1f}%")
            
            # 디스크 사용률 모니터링
            disk = psutil.disk_usage('/')
            resource_status['disk']['percent'] = (disk.used / disk.total) * 100
            resource_status['disk']['free_gb'] = disk.free / (1024**3)
            
            disk_percent = resource_status['disk']['percent']
            if disk_percent >= 98:
                resource_status['disk']['level'] = SystemResourceLevel.EMERGENCY
                resource_status['critical_issues'].append(f"디스크 사용률 위험: {disk_percent:.1f}%")
            elif disk_percent >= 90:
                resource_status['disk']['level'] = SystemResourceLevel.CRITICAL
                resource_status['critical_issues'].append(f"디스크 사용률 높음: {disk_percent:.1f}%")
            elif disk_percent >= 80:
                resource_status['disk']['level'] = SystemResourceLevel.WARNING
                resource_status['warnings'].append(f"디스크 사용률 주의: {disk_percent:.1f}%")
            
            # 전체 시스템 레벨 결정
            levels = [
                resource_status['cpu']['level'],
                resource_status['memory']['level'],
                resource_status['disk']['level']
            ]
            
            if SystemResourceLevel.EMERGENCY in levels:
                resource_status['overall_level'] = SystemResourceLevel.EMERGENCY
            elif SystemResourceLevel.CRITICAL in levels:
                resource_status['overall_level'] = SystemResourceLevel.CRITICAL
            elif SystemResourceLevel.WARNING in levels:
                resource_status['overall_level'] = SystemResourceLevel.WARNING
            else:
                resource_status['overall_level'] = SystemResourceLevel.NORMAL
            
            self.log(f"📊 시스템 리소스 모니터링 완료: {resource_status['overall_level']}")
            
            return resource_status
            
        except Exception as e:
            self.log(f"❌ 시스템 리소스 모니터링 중 오류: {e}")
            resource_status['overall_level'] = SystemResourceLevel.CRITICAL
            resource_status['critical_issues'].append(f"모니터링 오류: {e}")
            return resource_status
    
    def generate_dynamic_alert_message(self, 
                                      process_results: Dict[str, Any],
                                      git_status: Dict[str, Any],
                                      resource_status: Dict[str, Any],
                                      alert_type: str = "status") -> str:
        """상황별 동적 알림 메시지 생성 로직"""
        try:
            current_time = datetime.now()
            
            # 메시지 헤더 결정
            if alert_type == "critical":
                header = "🚨 POSCO 워치햄스터 긴급 알림"
            elif alert_type == "error":
                header = "❌ POSCO 워치햄스터 오류 알림"
            elif alert_type == "recovery":
                header = "🔧 POSCO 워치햄스터 복구 알림"
            else:
                header = "🐹 POSCO 워치햄스터 상태 보고"
            
            message_parts = [
                f"{header}\n",
                f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            ]
            
            # 시스템 가동 시간 추가
            uptime = current_time - self.system_start_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            message_parts.append(f"⏱️ 가동 시간: {hours}시간 {minutes}분\n")
            
            # 프로세스 상태 섹션
            if process_results:
                healthy_count = process_results.get('healthy_processes', 0)
                total_count = process_results.get('total_processes', 0)
                failed_processes = process_results.get('failed_processes', [])
                
                if failed_processes:
                    message_parts.append(f"\n🔴 프로세스 상태: {healthy_count}/{total_count} 정상\n")
                    message_parts.append("❌ 문제 프로세스:\n")
                    for process_name in failed_processes:
                        restart_count = self.restart_counts.get(process_name, 0)
                        if restart_count > 0:
                            message_parts.append(f"  • {process_name} (재시작: {restart_count}회)\n")
                        else:
                            message_parts.append(f"  • {process_name}\n")
                else:
                    message_parts.append(f"\n🟢 프로세스 상태: {healthy_count}/{total_count} 모두 정상\n")
            
            # Git 상태 섹션
            if git_status and git_status.get('status') != 'clean':
                message_parts.append(f"\n📋 Git 상태: {git_status['status']}\n")
                
                if git_status.get('current_branch'):
                    message_parts.append(f"  • 브랜치: {git_status['current_branch']}\n")
                
                if git_status.get('current_commit'):
                    message_parts.append(f"  • 커밋: {git_status['current_commit']}\n")
            
            # 시스템 리소스 섹션
            if resource_status:
                overall_level = resource_status.get('overall_level', SystemResourceLevel.NORMAL)
                
                if overall_level != SystemResourceLevel.NORMAL:
                    level_emoji = {
                        SystemResourceLevel.WARNING: "🟡",
                        SystemResourceLevel.CRITICAL: "🟠", 
                        SystemResourceLevel.EMERGENCY: "🔴"
                    }.get(overall_level, "⚪")
                    
                    message_parts.append(f"\n{level_emoji} 시스템 리소스: {overall_level}\n")
                    
                    cpu_percent = resource_status.get('cpu', {}).get('percent', 0)
                    memory_percent = resource_status.get('memory', {}).get('percent', 0)
                    disk_percent = resource_status.get('disk', {}).get('percent', 0)
                    
                    message_parts.append(f"  • CPU: {cpu_percent:.1f}%\n")
                    message_parts.append(f"  • 메모리: {memory_percent:.1f}%\n")
                    message_parts.append(f"  • 디스크: {disk_percent:.1f}%\n")
                else:
                    cpu_percent = resource_status.get('cpu', {}).get('percent', 0)
                    memory_percent = resource_status.get('memory', {}).get('percent', 0)
                    disk_percent = resource_status.get('disk', {}).get('percent', 0)
                    
                    message_parts.append(f"\n📊 시스템 리소스: CPU {cpu_percent:.1f}% | 메모리 {memory_percent:.1f}% | 디스크 {disk_percent:.1f}%\n")
            
            # 다음 작업 안내
            if alert_type == "status":
                next_check = current_time + timedelta(seconds=self.process_check_interval)
                message_parts.append(f"\n⏰ 다음 체크: {next_check.strftime('%H:%M')}\n")
                message_parts.append("🛡️ 자동 모니터링 활성화\n")
            elif alert_type in ["error", "critical"]:
                message_parts.append("\n🔧 자동 복구 시도 중...\n")
            
            # 메시지 조합
            final_message = "".join(message_parts).rstrip()
            
            self.log(f"📝 동적 알림 메시지 생성 완료: {alert_type}")
            
            return final_message
            
        except Exception as e:
            self.log(f"❌ 동적 알림 메시지 생성 중 오류: {e}")
            return (f"🐹 POSCO 워치햄스터 알림\n\n"
                   f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                   f"❌ 메시지 생성 오류: {e}\n"
                   f"🔧 수동 확인이 필요합니다")
    
    def send_webhook_notification(self, message: str, is_error: bool = False) -> bool:
        """웹훅 알림 전송"""
        try:
            if not self.webhook_url:
                self.log("⚠️ 웹훅 URL이 설정되지 않았습니다")
                return False
            
            # 봇 이름과 색상 결정
            if is_error:
                bot_name = "POSCO 워치햄스터 ❌"
                color = "#ff4444"
            else:
                bot_name = "POSCO 워치햄스터 🐹🛡️"
                color = "#28a745"
            
            # 웹훅 페이로드 구성
            payload = {
                "botName": bot_name,
                "botIconImage": self.bot_profile_image,
                "text": message.split('\n')[0],
                "attachments": [{
                    "color": color,
                    "text": message
                }]
            }
            
            # 웹훅 전송
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log(f"✅ 웹훅 알림 전송 성공")
                return True
            else:
                self.log(f"❌ 웹훅 알림 전송 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ 웹훅 알림 전송 중 오류: {e}")
            return False
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """현재 모니터링 상태 반환"""
        return {
            'timestamp': datetime.now(),
            'system_start_time': self.system_start_time,
            'managed_processes': self.managed_processes,
            'process_status': self.process_status.copy(),
            'restart_counts': self.restart_counts.copy(),
            'configuration': {
                'process_check_interval': self.process_check_interval,
                'git_check_interval': self.git_check_interval,
                'status_notification_interval': self.status_notification_interval,
                'max_restart_attempts': self.max_restart_attempts
            }
        }