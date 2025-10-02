#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Manager
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import subprocess
import .comprehensive_repair_backup/realtime_news_monitor.py.backup_20250809_181657
import posco_news_250808_monitor.log
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from enum import Enum

class MonitorType(Enum):
    """모니터 타입 열거형"""
    NEWYORK = "newyork"
    KOSPI = "kospi"
    EXCHANGE = "exchange"
    MASTER = "master"

class ProcessStatus(Enum):
    """프로세스 상태 열거형"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"
    RECOVERING = "recovering"

class ProcessManager:
    """
    워치햄스터 프로세스 관리 클래스
    
    프로세스 시작 실패 문제를 해결하고 안정적인 모니터 관리를 제공합니다.
    """
    
    def __init__(self, script_dir: str):
        """
        ProcessManager 초기화
        
        Args:
            script_dir (str): 스크립트 디렉토리 경로
        """
        self.script_dir = script_dir
        self.logger = logging.getLogger(__name__)
        
        # 프로세스 상태 추적
self.processes:_Dict[str,_subprocess.Popen] =  {}
self.process_status:_Dict[str,_ProcessStatus] =  {}
self.last_health_check:_Dict[str,_datetime] =  {}
self.retry_counts:_Dict[str,_int] =  {}
        self.max_retries = 3
        self.health_check_interval = 30  # 30초
        
        # 모니터 설정
        self.monitor_configs = {
            MonitorType.NEWYORK.value: {
                'script': 'Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py',
                'args': ['6'],  # 테스트 알림
                'timeout': 300,
                'description': '뉴욕마켓워치 모니터'
            },
            MonitorType.KOSPI.value: {
                'script': 'Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py',
                'args': ['6'],  # 테스트 알림
                'timeout': 300,
                'description': '증시마감 모니터'
            },
            MonitorType.EXCHANGE.value: {
                'script': 'Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py',
                'args': ['6'],  # 테스트 알림
                'timeout': 300,
                'description': '서환마감 모니터'
            },
            MonitorType.MASTER.value: {
                'script': 'Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py',
                'args': ['1'],  # 상태 체크
                'timeout': 300,
                'description': '마스터 모니터'
            }
        }
        
        # 모든 모니터 상태 초기화
        for monitor_type in self.monitor_configs.keys():
            self.process_status[monitor_type] = ProcessStatus.STOPPED
            self.retry_counts[monitor_type] = 0
    
    def initialize_monitors(self) -> bool:
        """
        모든 모니터 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        self.logger.info("🚀 모니터 초기화 시작")
        
        success_count = 0
        total_count = len(self.monitor_configs)
        
        for monitor_type, config in self.monitor_configs.items():
            try:
                self.logger.info(f"🔧 {config['description']} 초기화 중...")
                
                if self.start_individual_monitor(monitor_type):
success_count_+ =  1
                    self.logger.info(f"✅ {config['description']} 초기화 성공")
                else:
                    self.logger.warning(f"⚠️ {config['description']} 초기화 실패")
                
                # 초기화 간격 (시스템 부하 방지)
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ {config['description']} 초기화 오류: {e}")
        
        success_rate = success_count / total_count
        self.logger.info(f"📊 모니터 초기화 완료: {success_count}/{total_count} ({success_rate:.1%})")
        
        # 50% 이상 성공하면 전체적으로 성공으로 간주
return_success_rate_> =  0.5
    
    def start_individual_monitor(self, monitor_type: str) -> bool:
        """
        개별 모니터 시작
        
        Args:
            monitor_type (str): 모니터 타입
            
        Returns:
            bool: 시작 성공 여부
        """
        if monitor_type not in self.monitor_configs:
            self.logger.error(f"❌ 알 수 없는 모니터 타입: {monitor_type}")
            return False
        
        config = self.monitor_configs[monitor_type]
        
        try:
            # 이미 실행 중인 프로세스가 있으면 종료
            if monitor_type in self.processes:
                self.stop_individual_monitor(monitor_type)
            
            # 상태 업데이트
            self.process_status[monitor_type] = ProcessStatus.STARTING
            
            # 프로세스 시작
            script_path = os.path.join(self.script_dir, config['script'])
            cmd = ['python', script_path] + config['args']
            
            self.logger.debug(f"🚀 명령어 실행: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                cwd=self.script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # 프로세스 등록
            self.processes[monitor_type] = process
            self.last_health_check[monitor_type] = datetime.now()
            
            # 짧은 대기 후 상태 확인
            time.sleep(2)
            
            if self.check_monitor_health(monitor_type):
                self.process_status[monitor_type] = ProcessStatus.RUNNING
                self.retry_counts[monitor_type] = 0
                return True
            else:
                self.process_status[monitor_type] = ProcessStatus.FAILED
                return False
                
        except Exception as e:
            self.logger.error(f"❌ {config['description']} 시작 오류: {e}")
            self.process_status[monitor_type] = ProcessStatus.FAILED
            return False
    
    def stop_individual_monitor(self, monitor_type: str) -> bool:
        """
        개별 모니터 중지
        
        Args:
            monitor_type (str): 모니터 타입
            
        Returns:
            bool: 중지 성공 여부
        """
        if monitor_type not in self.processes:
            return True
        
        try:
            process = self.processes[monitor_type]
            
            # 프로세스가 살아있는지 확인
            if process.poll() is None:
                # 정상 종료 시도
                process.terminate()
                
                # 5초 대기
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 강제 종료
                    process.kill()
                    process.wait()
            
            # 프로세스 제거
            del self.processes[monitor_type]
            self.process_status[monitor_type] = ProcessStatus.STOPPED
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 모니터 중지 오류 ({monitor_type}): {e}")
            return False
    
    def check_monitor_health(self, monitor_type: str) -> bool:
        """
        모니터 헬스 체크
        
        Args:
            monitor_type (str): 모니터 타입
            
        Returns:
            bool: 헬스 체크 성공 여부
        """
        if monitor_type not in self.processes:
            return False
        
        try:
            process = self.processes[monitor_type]
            
            # 프로세스가 종료되었는지 확인
            if process.poll() is not None:
                return False
            
            # 프로세스 ID로 실제 실행 여부 확인
            try:
                psutil_process = psutil.Process(process.pid)
                if psutil_process.is_running():
                    self.last_health_check[monitor_type] = datetime.now()
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ 헬스 체크 오류 ({monitor_type}): {e}")
            return False
    
    def restart_failed_monitor(self, monitor_type: str) -> bool:
        """
        실패한 모니터 재시작
        
        Args:
            monitor_type (str): 모니터 타입
            
        Returns:
            bool: 재시작 성공 여부
        """
        if monitor_type not in self.monitor_configs:
            return False
        
        config = self.monitor_configs[monitor_type]
        
        # 재시도 횟수 확인
        if self.retry_counts[monitor_type] >= self.max_retries:
            self.logger.warning(f"⚠️ {config['description']} 최대 재시도 횟수 초과")
            return False
        
self.retry_counts[monitor_type]_+ =  1
        self.process_status[monitor_type] = ProcessStatus.RECOVERING
        
        self.logger.info(f"🔄 {config['description']} 재시작 시도 ({self.retry_counts[monitor_type]}/{self.max_retries})")
        
        # 기존 프로세스 정리
        self.stop_individual_monitor(monitor_type)
        
        # 잠시 대기
        time.sleep(3)
        
        # 재시작 시도
        if self.start_individual_monitor(monitor_type):
            self.logger.info(f"✅ {config['description']} 재시작 성공")
            return True
        else:
            self.logger.error(f"❌ {config['description']} 재시작 실패")
            return False
    
    def get_all_monitor_status(self) -> Dict[str, Dict]:
        """
        모든 모니터 상태 조회
        
        Returns:
            Dict[str, Dict]: 모니터별 상태 정보
        """
        status_info = {}
        
        for monitor_type, config in self.monitor_configs.items():
            status_info[monitor_type] = {
                'description': config['description'],
                'status': self.process_status[monitor_type].value,
                'retry_count': self.retry_counts[monitor_type],
                'last_health_check': self.last_health_check.get(monitor_type),
                'is_running': self.check_monitor_health(monitor_type),
                'pid': self.processes[monitor_type].pid if monitor_type in self.processes else None
            }
        
        return status_info
    
    def perform_health_checks(self) -> Tuple[int, int]:
        """
        모든 모니터에 대한 헬스 체크 수행
        
        Returns:
            Tuple[int, int]: (정상 모니터 수, 전체 모니터 수)
        """
        healthy_count = 0
        total_count = len(self.monitor_configs)
        
        for monitor_type in self.monitor_configs.keys():
            if self.check_monitor_health(monitor_type):
healthy_count_+ =  1
                self.process_status[monitor_type] = ProcessStatus.RUNNING
            else:
                # 실패한 모니터 자동 복구 시도
                if self.process_status[monitor_type] == ProcessStatus.RUNNING:
                    self.logger.warning(f"⚠️ {self.monitor_configs[monitor_type]['description']} 헬스 체크 실패")
                    self.process_status[monitor_type] = ProcessStatus.FAILED
                    
                    # 자동 복구 시도
                    if self.retry_counts[monitor_type] < self.max_retries:
                        self.restart_failed_monitor(monitor_type)
        
        return healthy_count, total_count
    
    def stop_all_monitors(self) -> bool:
        """
        모든 모니터 중지
        
        Returns:
            bool: 중지 성공 여부
        """
        self.logger.info("🛑 모든 모니터 중지 시작")
        
        success_count = 0
        total_count = len(self.processes)
        
        for monitor_type in list(self.processes.keys()):
            if self.stop_individual_monitor(monitor_type):
success_count_+ =  1
        
        self.logger.info(f"📊 모니터 중지 완료: {success_count}/{total_count}")
return_success_count = = total_count
    
    def get_system_resource_info(self) -> Dict[str, any]:
        """
        시스템 리소스 정보 조회
        
        Returns:
            Dict[str, any]: 시스템 리소스 정보
        """
        try:
            # CPU 및 메모리 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # 워치햄스터 프로세스들의 리소스 사용량
            total_memory_mb = 0
            process_count = 0
            
            for process in self.processes.values():
                try:
                    psutil_process = psutil.Process(process.pid)
                    memory_info = psutil_process.memory_info()
total_memory_mb_+ =  memory_info.rss / 1024 / 1024
process_count_+ =  1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / 1024 / 1024 / 1024,
                'watchhamster_memory_mb': total_memory_mb,
                'active_processes': process_count,
                'total_processes': len(self.processes)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 시스템 리소스 정보 조회 실패: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'memory_available_gb': 0,
                'watchhamster_memory_mb': 0,
                'active_processes': 0,
                'total_processes': 0
            }
    
    def reset_retry_counts(self):
        """재시도 카운트 초기화"""
        for monitor_type in self.retry_counts.keys():
            self.retry_counts[monitor_type] = 0
        self.logger.info("🔄 재시도 카운트 초기화 완료")