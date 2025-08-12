#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Manager
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

class NotificationType(Enum):
    """알림 타입 열거형"""
    STARTUP = "startup"
    STATUS = "status"
    ERROR = "error"
    RECOVERY = "recovery"
    SHUTDOWN = "shutdown"
    CRITICAL = "critical"

@dataclass
class SystemStatus:
    """시스템 상태 정보"""
    timestamp: datetime
    uptime: timedelta
    total_processes: int
    running_processes: int
    failed_processes: int
    process_details: Dict[str, Any]
    system_metrics: Dict[str, Any]
last_git_update:_Optional[datetime] =  None
next_status_report:_Optional[datetime] =  None

class NotificationManager:
    """
    WatchHamster v3.0 알림 관리 클래스
    
    기존 send_notification 함수의 모든 기능을 보존하면서
    다양한 알림 타입별로 메서드를 분리하여 관리
    """
    
    def __init__(self, webhook_url: str, bot_profile_url: str):
        """
        NotificationManager 초기화
        
        Args:
            webhook_url (str): Dooray 웹훅 URL
            bot_profile_url (str): 봇 프로필 이미지 URL
        """
        self.webhook_url = webhook_url
        self.bot_profile_url = bot_profile_url
        self.logger = logging.getLogger(__name__)
        
        # 알림 설정
        self.timeout = 10
        self.retry_count = 3
        
        # 알림 통계
        self.total_notifications = 0
        self.failed_notifications = 0
        
        self.logger.info("🔔 NotificationManager 초기화 완료")
    
    def send_notification(self, message: str, is_error: bool = False) -> bool:
        """
        기본 알림 전송 (기존 send_notification 함수와 동일)
        
        기존 텍스트 내용을 완전히 보존하는 호환성 메서드
        
        Args:
            message (str): 전송할 메시지
            is_error (bool): 오류 알림 여부 (색상과 봇명 변경)
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            color = "#ff4444" if is_error else "#28a745"
            bot_name = "POSCO WatchHamster v3.0 ❌" if is_error else "POSCO WatchHamster v3.0 🐹🛡️"
            
            payload = {
                "botName": bot_name,
                "botIconImage": self.bot_profile_url,
                "text": message.split('/n')[0],
                "attachments": [{
                    "color": color,
                    "text": message
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            self.total_notifications += 1
            
            if response.status_code == 200:
                self.logger.info(f"✅ 알림 전송 성공: {message.split(chr(10))[0]}")
                return True
            else:
                self.failed_notifications += 1
                self.logger.error(f"❌ 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            self.failed_notifications += 1
            self.logger.error(f"❌ 알림 전송 오류: {e}")
            return False
    
    def send_startup_notification(self, managed_processes: List[str]) -> bool:
        """
        시작 알림 전송
        
        Args:
            managed_processes (List[str]): 관리 대상 프로세스 목록
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            current_time = datetime.now()
            
            # 기존 WatchHamster v3.0 알림 텍스트 보존
            message = f"🐹 POSCO WatchHamster v3.0 시작/n/n"
            message += f"📅 시작 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"🛡️ 관리 대상 프로세스: {len(managed_processes)}개/n/n"
            
            message += f"📊 관리 중인 모듈:/n"
            for process in managed_processes:
                # 프로세스명에 따른 설명 매핑
                descriptions = {
                    'POSCO News 250808 알림',
'realtime_news_monitor': '실시간 모니터링',
                    'integrated_report_scheduler': '리포트 스케줄러',
                    'historical_data_collector': '데이터 수집기'
                }
                desc = descriptions.get(process, process)
                message += f"  ✅ {process} ({desc})/n"
            
            message += f"/n🔄 모니터링 설정:/n"
            message += f"  • 헬스체크: 5분 간격/n"
            message += f"  • 상태 보고: 2시간 간격/n"
            message += f"  • 자동 복구: 활성화/n"
            message += f"  • Git 업데이트: 60분 간격/n/n"
            message += f"🚀 전체 시스템이 정상적으로 초기화되었습니다."
            
            return self._send_with_template(
                message=message,
                bot_name="POSCO WatchHamster v3.0 🐹🛡️",
                color="#28a745",
                notification_type=NotificationType.STARTUP
            )
            
        except Exception as e:
            self.logger.error(f"❌ 시작 알림 전송 오류: {e}")
            return False
    
    def send_shutdown_notification(self, shutdown_status: Dict[str, Any]) -> bool:
        """
        종료 알림 전송
        
        Args:
            shutdown_status (Dict[str, Any]): 종료 상태 정보
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            current_time = datetime.now()
            uptime = shutdown_status.get('uptime', timedelta(0))
            
            message = f"🛑 POSCO WatchHamster v3.0 시스템 종료/n/n"
            message += f"📅 종료 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"⏱️ 총 가동 시간: {self._format_timedelta(uptime)}/n/n"
            
            # 프로세스 종료 상태
            stopped_processes = shutdown_status.get('stopped_processes', [])
            if stopped_processes:
                message += f"⏹️ 종료된 프로세스 ({len(stopped_processes)}개):/n"
                for process in stopped_processes:
                    message += f"  ✅ {process}/n"
            
            # 통계 정보
            total_restarts = shutdown_status.get('total_restarts', 0)
            if total_restarts > 0:
                message += f"/n📊 운영 통계:/n"
                message += f"  • 총 재시작 횟수: {total_restarts}회/n"
                message += f"  • 알림 전송: {self.total_notifications}회/n"
            
            message += f"/n🔒 모든 프로세스가 안전하게 종료되었습니다."
            
            return self._send_with_template(
                message=message,
                bot_name="POSCO WatchHamster v3.0 🛑",
                color="#6c757d",
                notification_type=NotificationType.SHUTDOWN
            )
            
        except Exception as e:
            self.logger.error(f"❌ 종료 알림 전송 오류: {e}")
            return False
    
    def send_status_report(self, system_status: SystemStatus) -> bool:
        """
        정기 상태 보고 알림 전송
        
        Args:
            system_status (SystemStatus): 시스템 상태 정보
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            current_time = system_status.timestamp
            
            # 기존 정기 상태 보고 텍스트 보존
            message = f"📊 POSCO WatchHamster v3.0 정기 상태 보고/n/n"
            message += f"📅 보고 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"⏱️ 가동 시간: {self._format_timedelta(system_status.uptime)}/n/n"
            
            # 프로세스 상태
            running = system_status.running_processes
            total = system_status.total_processes
            failed = system_status.failed_processes
            
            if failed == 0:
                message += f"🟢 정상 프로세스 ({running}/{total}):/n"
                for name, details in system_status.process_details.items():
                    if details.get('status') == 'running':
                        pid = details.get('pid', 'N/A')
                        message += f"  ✅ {name} - 정상 (PID: {pid})/n"
            else:
                message += f"🟢 정상 프로세스 ({running}/{total}):/n"
                for name, details in system_status.process_details.items():
                    if details.get('status') == 'running':
                        pid = details.get('pid', 'N/A')
                        message += f"  ✅ {name} - 정상 (PID: {pid})/n"
                
                message += f"/n🟡 문제 프로세스 ({failed}/{total}):/n"
                for name, details in system_status.process_details.items():
                    if details.get('status') != 'running':
                        restart_count = details.get('restart_count', 0)
                        status = details.get('status', 'unknown')
                        if status == 'recovering':
                            message += f"  ⚠️ {name} - 재시작 중 (시도: {restart_count}/3)/n"
                        else:
                            message += f"  ❌ {name} - {status}/n"
            
            # 시스템 성능
            metrics = system_status.system_metrics
            message += f"/n📈 시스템 성능:/n"
            message += f"  • CPU 사용률: {metrics.get('cpu_percent', 0):.0f}%/n"
            message += f"  • 메모리 사용률: {metrics.get('memory_percent', 0):.0f}%/n"
            message += f"  • 디스크 사용률: {metrics.get('disk_percent', 0):.0f}%/n"
            
            # 다음 보고 시간
            if system_status.next_status_report:
                next_time = system_status.next_status_report.strftime('%H:%M')
                message += f"/n🔄 다음 상태 보고: {next_time}"
            
            # 색상 결정 (문제가 있으면 주황색, 없으면 녹색)
            color = "#ffc107" if failed > 0 else "#28a745"
            
            return self._send_with_template(
                message=message,
                bot_name="POSCO WatchHamster v3.0 📊",
                color=color,
                notification_type=NotificationType.STATUS
            )
            
        except Exception as e:
            self.logger.error(f"❌ 상태 보고 알림 전송 오류: {e}")
            return False
    
    def send_process_error(self, process_name: str, error_details: Dict[str, Any]) -> bool:
        """
        프로세스 오류 알림 전송
        
        Args:
            process_name (str): 프로세스 이름
            error_details (Dict[str, Any]): 오류 상세 정보
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            current_time = datetime.now()
            
            message = f"❌ POSCO WatchHamster v3.0 프로세스 오류/n/n"
            message += f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"🔧 문제 프로세스: {process_name}/n/n"
            
            # 오류 정보
            error_msg = error_details.get('error_message', '알 수 없는 오류')
            message += f"❌ 오류 내용: {error_msg}/n"
            
            # 재시작 시도 정보
            restart_count = error_details.get('restart_count', 0)
            max_attempts = error_details.get('max_attempts', 3)
            
            if restart_count > 0:
                message += f"🔄 재시작 시도: {restart_count}/{max_attempts}회/n"
            
            # 자동 복구 상태
            auto_recovery = error_details.get('auto_recovery_enabled', True)
            if auto_recovery and restart_count < max_attempts:
                message += f"/n🔧 자동 복구 시도 중..."
            elif restart_count >= max_attempts:
                message += f"/n🚨 최대 재시작 횟수 초과 - 수동 개입 필요"
            else:
                message += f"/n⚠️ 자동 복구 비활성화 - 수동 확인 필요"
            
            return self._send_with_template(
                message=message,
                bot_name="POSCO WatchHamster v3.0 ❌",
                color="#dc3545",
                notification_type=NotificationType.ERROR
            )
            
        except Exception as e:
            self.logger.error(f"❌ 프로세스 오류 알림 전송 오류: {e}")
            return False
    
    def send_recovery_success(self, process_name: str, recovery_details: Dict[str, Any]) -> bool:
        """
        복구 성공 알림 전송
        
        Args:
            process_name (str): 프로세스 이름
            recovery_details (Dict[str, Any]): 복구 상세 정보
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            current_time = datetime.now()
            
            message = f"✅ POSCO WatchHamster v3.0 프로세스 복구 완료/n/n"
            message += f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"🔧 복구된 프로세스: {process_name}/n/n"
            
            # 복구 정보
            recovery_stage = recovery_details.get('recovery_stage', '알 수 없음')
            recovery_time = recovery_details.get('recovery_time', 0)
            
            message += f"🔄 복구 단계: {recovery_stage}/n"
            if recovery_time > 0:
                message += f"⏱️ 복구 소요 시간: {recovery_time}초/n"
            
            # 새 프로세스 정보
            new_pid = recovery_details.get('new_pid')
            if new_pid:
                message += f"🆔 새 프로세스 ID: {new_pid}/n"
            
            message += f"/n🚀 프로세스가 정상적으로 복구되어 모니터링을 재개합니다."
            
            return self._send_with_template(
                message=message,
                bot_name="POSCO WatchHamster v3.0 ✅",
                color="#28a745",
                notification_type=NotificationType.RECOVERY
            )
            
        except Exception as e:
            self.logger.error(f"❌ 복구 성공 알림 전송 오류: {e}")
            return False
    
    def send_critical_alert(self, alert_message: str, additional_info: Dict[str, Any] = None) -> bool:
        """
        긴급 알림 전송
        
        Args:
            alert_message (str): 긴급 알림 메시지
            additional_info (Dict[str, Any]): 추가 정보
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            current_time = datetime.now()
            
            message = f"🚨 POSCO WatchHamster v3.0 긴급 알림/n/n"
            message += f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"🚨 긴급 상황: {alert_message}/n/n"
            
            if additional_info:
                message += f"📋 추가 정보:/n"
                for key, value in additional_info.items():
                    message += f"  • {key}: {value}/n"
                message += "/n"
            
            message += f"🔧 즉시 수동 확인이 필요합니다."
            
            return self._send_with_template(
                message=message,
                bot_name="POSCO WatchHamster v3.0 🚨",
                color="#dc3545",
                notification_type=NotificationType.CRITICAL
            )
            
        except Exception as e:
            self.logger.error(f"❌ 긴급 알림 전송 오류: {e}")
            return False
    
    def _send_with_template(self, message: str, bot_name: str, color: str, 
                           notification_type: NotificationType) -> bool:
        """
        템플릿을 사용한 알림 전송
        
        Args:
            message (str): 메시지 내용
            bot_name (str): 봇 이름
            color (str): 색상 코드
            notification_type (NotificationType): 알림 타입
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            payload = {
                "botName": bot_name,
                "botIconImage": self.bot_profile_url,
                "text": message.split('/n')[0],
                "attachments": [{
                    "color": color,
                    "text": message
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            self.total_notifications += 1
            
            if response.status_code == 200:
                self.logger.info(f"✅ {notification_type.value} 알림 전송 성공")
                return True
            else:
                self.failed_notifications += 1
                self.logger.error(f"❌ {notification_type.value} 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            self.failed_notifications += 1
            self.logger.error(f"❌ {notification_type.value} 알림 전송 오류: {e}")
            return False
    
    def _format_timedelta(self, td: timedelta) -> str:
        """
        timedelta를 읽기 쉬운 형태로 포맷
        
        Args:
            td (timedelta): 시간 간격
            
        Returns:
            str: 포맷된 시간 문자열
        """
        total_seconds = int(td.total_seconds())
hours,_remainder =  divmod(total_seconds, 3600)
minutes,_seconds =  divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}시간 {minutes}분"
        elif minutes > 0:
            return f"{minutes}분 {seconds}초"
        else:
            return f"{seconds}초"
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """
        알림 통계 조회
        
        Returns:
            Dict[str, Any]: 알림 통계 정보
        """
        success_rate = 0
        if self.total_notifications > 0:
            success_rate = ((self.total_notifications - self.failed_notifications) / 
                          self.total_notifications) * 100
        
        return {
            'total_notifications': self.total_notifications,
            'failed_notifications': self.failed_notifications,
            'success_rate': round(success_rate, 2),
            'webhook_url': self.webhook_url,
            'timeout': self.timeout
        }