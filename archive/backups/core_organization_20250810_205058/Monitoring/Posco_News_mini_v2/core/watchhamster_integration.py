#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watchhamster Integration
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import system_functionality_verification.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 새로운 컴포넌트들 import
# REMOVED: from Monitoring/POSCO_News_250808/core/process_manager.py import ProcessManager, ProcessInfo, ProcessStatus
from Monitoring/WatchHamster_v3.0/core/module_registry.py import ModuleRegistry_Integration_Summary.md, ModuleConfig, ModuleStatus
# REMOVED: from Monitoring/WatchHamster_v3.0/core/notification_manager.py import NotificationManager, SystemStatus, NotificationType

# 기존 컴포넌트들 import
try:
# REMOVED:     from Monitoring/POSCO_News_250808/core/state_manager.py import StateManager
except ImportError:
    StateManager = None

class EnhancedWatchHamster:
    """
    Enhanced WatchHamster with New Architecture
    
    새로운 아키텍처를 적용한 향상된 워치햄스터 클래스
    기존 기능을 모두 보존하면서 새로운 컴포넌트들을 통합
    """
    
    def __init__(self, script_dir: str, webhook_url: str, bot_profile_url: str):
        """
        Enhanced WatchHamster 초기화
        
        Args:
            script_dir (str): 스크립트 디렉토리 경로
            webhook_url (str): Dooray 웹훅 URL
            bot_profile_url (str): 봇 프로필 이미지 URL
        """
        self.script_dir = script_dir
        self.logger = logging.getLogger(__name__)
        
        # 새로운 컴포넌트들 초기화
        self.process_manager = ProcessManager(script_dir)
        self.module_registry = ModuleRegistry(os.path.join(script_dir, ".naming_backup/config_data_backup/Monitoring/Posco_News_mini/modules.json"))
        self.notification_manager = NotificationManager(webhook_url, bot_profile_url)
        
        # 기존 컴포넌트 초기화 (호환성)
        if StateManager:
            status_file = os.path.join(script_dir, ".naming_backup/config_data_backup/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster_status.json")
            self.state_manager = StateManager(status_file)
        else:
            self.state_manager = None
        
        # 시스템 상태
        self.start_time = datetime.now()
        self.last_health_check = datetime.now()
        self.last_status_notification = None
        self.last_git_check = datetime.now() - timedelta(hours=1)
        
        # 설정
        self.health_check_interval = 300  # 5분
        self.status_notification_interval = 7200  # 2시간
        self.git_check_interval = 3600  # 1시간
        
        self.logger.info("🔧 Enhanced WatchHamster 초기화 완료")
    
    def start_all_processes(self) -> bool:
        """
        모든 프로세스 시작
        
        Returns:
            bool: 시작 성공 여부
        """
        try:
            self.logger.info("🚀 모든 프로세스 시작 중...")
            
            # 모듈 레지스트리에서 시작 순서 가져오기
            startup_order = self.module_registry.get_startup_order()
            dependency_order = self.module_registry.get_modules_by_dependency_order()
            
            # 의존성 순서를 우선으로 하되, 우선순위도 고려
            final_order = []
            for module_name in dependency_order:
                if module_name in startup_order:
                    final_order.append(module_name)
            
            self.logger.info(f"📋 시작 순서: {final_order}")
            
            # 프로세스 시작
            started_processes = []
            for module_name in final_order:
                module_config = self.module_registry.get_module_config(module_name)
                if module_config and module_config.auto_start:
                    success = self.process_manager.start_process(
                        name=module_name,
                        script_path=module_config.script_path,
                        args=[]
                    )
                    
                    if success:
                        started_processes.append(module_name)
                        self.module_registry.update_module_status(module_name, ModuleStatus.ACTIVE)
                        self.logger.info(f"✅ {module_name} 시작 성공")
                    else:
                        self.module_registry.update_module_status(module_name, ModuleStatus.ERROR)
                        self.logger.error(f"❌ {module_name} 시작 실패")
                    
                    # 프로세스 간 시작 간격
                    import .comprehensive_repair_backup/realtime_news_monitor.py.backup_20250809_181657
                    time.sleep(2)
            
            # 시작 알림 전송
            if started_processes:
                self.notification_manager.send_startup_notification(started_processes)
            
            success_rate = len(started_processes) / len(final_order) if final_order else 0
            self.logger.info(f"📊 프로세스 시작 완료: {len(started_processes)}/{len(final_order)} ({success_rate:.1%})")
            
            return success_rate > 0.5  # 50% 이상 성공하면 전체적으로 성공
            
        except Exception as e:
            self.logger.error(f"❌ 모든 프로세스 시작 오류: {e}")
            return False
    
    def stop_all_processes(self) -> bool:
        """
        모든 프로세스 중지
        
        Returns:
            bool: 중지 성공 여부
        """
        try:
            self.logger.info("🛑 모든 프로세스 중지 중...")
            
            # 실행 중인 프로세스 목록
            running_processes = []
            for name, info in self.process_manager.process_info.items():
                if info.status == ProcessStatus.RUNNING:
                    running_processes.append(name)
            
            # 프로세스 중지
            stopped_processes = []
            for process_name in running_processes:
                if self.process_manager.stop_process(process_name):
                    stopped_processes.append(process_name)
                    self.module_registry.update_module_status(process_name, ModuleStatus.INACTIVE)
            
            # 종료 알림 전송
            uptime = datetime.now() - self.start_time
            shutdown_status = {
                'uptime': uptime,
                'stopped_processes': stopped_processes,
                'total_restarts': self.process_manager.total_restarts
            }
            
            self.notification_manager.send_shutdown_notification(shutdown_status)
            
            self.logger.info(f"✅ 프로세스 중지 완료: {len(stopped_processes)}개")
return_len(stopped_processes) = = len(running_processes)
            
        except Exception as e:
            self.logger.error(f"❌ 모든 프로세스 중지 오류: {e}")
            return False
    
    def restart_process(self, process_name: str) -> bool:
        """
        개별 프로세스 재시작
        
        Args:
            process_name (str): 프로세스 이름
            
        Returns:
            bool: 재시작 성공 여부
        """
        try:
            self.logger.info(f"🔄 {process_name} 프로세스 재시작")
            
            # 프로세스 재시작
            success = self.process_manager.restart_process(process_name)
            
            if success:
                # 복구 성공 알림
                process_info = self.process_manager.get_process_info(process_name)
                recovery_details = {
                    'recovery_stage': f"{process_info.restart_count}차 재시작 성공",
                    'recovery_time': 5,  # 대략적인 재시작 시간
                    'new_pid': process_info.pid
                }
                
                self.notification_manager.send_recovery_success(process_name, recovery_details)
                self.module_registry.update_module_status(process_name, ModuleStatus.ACTIVE)
            else:
                # 재시작 실패 알림
                process_info = self.process_manager.get_process_info(process_name)
                error_details = {
                    'error_message': process_info.last_error or '재시작 실패',
                    'restart_count': process_info.restart_count,
                    'max_attempts': self.process_manager.max_restart_attempts,
                    'auto_recovery_enabled': True
                }
                
                self.notification_manager.send_process_error(process_name, error_details)
                self.module_registry.update_module_status(process_name, ModuleStatus.ERROR)
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ {process_name} 프로세스 재시작 오류: {e}")
            return False
    
    def get_process_status(self, process_name: str) -> Optional[Dict[str, Any]]:
        """
        프로세스 상태 조회
        
        Args:
            process_name (str): 프로세스 이름
            
        Returns:
            Optional[Dict[str, Any]]: 프로세스 상태 정보
        """
        try:
            process_info = self.process_manager.get_process_info(process_name)
            module_status = self.module_registry.get_module_status(process_name)
            
            if process_info:
                return {
                    'name': process_info.name,
                    'pid': process_info.pid,
                    'status': process_info.status.value,
                    'module_status': module_status.value if module_status else 'unknown',
                    'start_time': process_info.start_time.isoformat() if process_info.start_time else None,
                    'restart_count': process_info.restart_count,
                    'cpu_usage': process_info.cpu_usage,
                    'memory_usage': process_info.memory_usage,
                    'last_error': process_info.last_error
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ {process_name} 상태 조회 오류: {e}")
            return None
    
    def perform_health_check(self) -> Dict[str, bool]:
        """
        모든 프로세스 헬스체크 수행
        
        Returns:
            Dict[str, bool]: 프로세스별 헬스체크 결과
        """
        try:
            self.logger.info("🔍 헬스체크 수행 중...")
            
            # ProcessManager의 헬스체크 수행
            health_results = self.process_manager.perform_health_check()
            
            # 실패한 프로세스 자동 복구
            for process_name, is_healthy in health_results.items():
                if not is_healthy:
                    process_info = self.process_manager.get_process_info(process_name)
                    if (process_info and 
                        process_info.status == ProcessStatus.FAILED and
                        process_info.restart_count < self.process_manager.max_restart_attempts):
                        
                        self.logger.warning(f"⚠️ {process_name} 자동 복구 시작")
                        self.auto_recovery(process_name)
            
            self.last_health_check = datetime.now()
            return health_results
            
        except Exception as e:
            self.logger.error(f"❌ 헬스체크 오류: {e}")
            return {}
    
    def auto_recovery(self, failed_process: str) -> bool:
        """
        실패한 프로세스 자동 복구
        
        Args:
            failed_process (str): 실패한 프로세스 이름
            
        Returns:
            bool: 복구 성공 여부
        """
        try:
            self.logger.info(f"🔧 {failed_process} 자동 복구 시작")
            
            # ProcessManager의 자동 복구 수행
            success = self.process_manager.auto_recovery(failed_process)
            
            if success:
                self.logger.info(f"✅ {failed_process} 자동 복구 성공")
            else:
                # 복구 실패 시 긴급 알림
                self.notification_manager.send_critical_alert(
                    f"{failed_process} 복구 실패 - 수동 개입 필요",
                    {
                        'process_name': failed_process,
                        'max_attempts_reached': True,
                        'action_required': '수동 재시작 또는 시스템 점검'
                    }
                )
                self.logger.error(f"❌ {failed_process} 자동 복구 실패")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ {failed_process} 자동 복구 오류: {e}")
            return False
    
    def send_status_report(self) -> bool:
        """
        정기 상태 보고 전송
        
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 시스템 상태 수집
            system_status_data = self.process_manager.get_system_status()
            
            # SystemStatus 객체 생성
            system_status = SystemStatus(
                timestamp=datetime.now(),
                uptime=datetime.now() - self.start_time,
                total_processes=system_status_data['total_processes'],
                running_processes=system_status_data['running_processes'],
                failed_processes=system_status_data['failed_processes'],
                process_details=system_status_data['process_details'],
                system_metrics=system_status_data['system_metrics'],
                last_git_update=self.last_git_check,
                next_status_report=datetime.now() + timedelta(seconds=self.status_notification_interval)
            )
            
            # 상태 보고 전송
            success = self.notification_manager.send_status_report(system_status)
            
            if success:
                self.last_status_notification = datetime.now()
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ 상태 보고 전송 오류: {e}")
            return False
    
    def register_module(self, module_config: ModuleConfig) -> bool:
        """
        새로운 모듈 등록
        
        Args:
            module_config (ModuleConfig): 모듈 설정
            
        Returns:
            bool: 등록 성공 여부
        """
        try:
            success = self.module_registry.register_module(module_config.name, module_config)
            
            if success:
                self.logger.info(f"✅ 모듈 등록 성공: {module_config.name}")
                
                # 자동 시작이 설정된 경우 즉시 시작
                if module_config.auto_start:
                    self.process_manager.start_process(
                        name=module_config.name,
                        script_path=module_config.script_path,
                        args=[]
                    )
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ 모듈 등록 오류: {e}")
            return False
    
    def unregister_module(self, module_name: str) -> bool:
        """
        모듈 등록 해제
        
        Args:
            module_name (str): 모듈 이름
            
        Returns:
            bool: 해제 성공 여부
        """
        try:
            # 실행 중인 프로세스 중지
            if self.process_manager.is_process_running(module_name):
                self.process_manager.stop_process(module_name)
            
            # 모듈 등록 해제
            success = self.module_registry.unregister_module(module_name)
            
            if success:
                self.logger.info(f"✅ 모듈 등록 해제 성공: {module_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ 모듈 등록 해제 오류: {e}")
            return False
    
    def reload_module_config(self) -> bool:
        """
        모듈 설정 다시 로드
        
        Returns:
            bool: 로드 성공 여부
        """
        try:
            success = self.module_registry.reload_config()
            
            if success:
                self.logger.info("✅ 모듈 설정 다시 로드 완료")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ 모듈 설정 다시 로드 오류: {e}")
            return False
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        시스템 전체 개요 조회
        
        Returns:
            Dict[str, Any]: 시스템 개요 정보
        """
        try:
            # 프로세스 상태
            system_status = self.process_manager.get_system_status()
            
            # 모듈 상태
            module_list = self.module_registry.list_modules()
            
            # 알림 통계
            notification_stats = self.notification_manager.get_notification_stats()
            
            return {
                'system_info': {
                    'start_time': self.start_time.isoformat(),
                    'uptime': (datetime.now() - self.start_time).total_seconds(),
                    'last_health_check': self.last_health_check.isoformat(),
                    'last_status_notification': self.last_status_notification.isoformat() if self.last_status_notification else None
                },
                'process_status': system_status,
                'module_registry': {
                    'total_modules': len(module_list),
                    'modules': module_list
                },
                'notification_stats': notification_stats
            }
            
        except Exception as e:
            self.logger.error(f"❌ 시스템 개요 조회 오류: {e}")
            return {'error': str(e)}
    
    def save_state(self) -> bool:
        """
        현재 상태 저장
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            if not self.state_manager:
                return True  # StateManager가 없으면 성공으로 처리
            
            state_data = {
                'last_check': datetime.now(),
                'start_time': self.start_time,
                'last_health_check': self.last_health_check,
                'last_status_notification': self.last_status_notification,
                'last_git_check': self.last_git_check,
                'process_info': {
                    name: {
                        'status': info.status.value,
                        'restart_count': info.restart_count,
                        'last_error': info.last_error
                    } for name, info in self.process_manager.process_info.items()
                },
                'notification_stats': self.notification_manager.get_notification_stats()
            }
            
            return self.state_manager.save_state(state_data)
            
        except Exception as e:
            self.logger.error(f"❌ 상태 저장 오류: {e}")
            return False