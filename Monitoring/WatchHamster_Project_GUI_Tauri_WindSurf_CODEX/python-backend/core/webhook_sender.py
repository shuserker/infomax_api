#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WatchHamster Tauri 웹훅 전송 시스템

기존 WatchHamster_Project의 웹훅 전송 로직을 완전히 이식한 시스템입니다.

주요 기능:
- POSCO 뉴스 알림 웹훅 (기존 URL 유지)
- WatchHamster 시스템 상태 웹훅
- generate_dynamic_alert_message 로직 완전 이식
- 웹훅 전송 실패 시 재시도 메커니즘
- 메시지 우선순위 및 큐 관리

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import os
import sys
import json
import time
import requests
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from queue import Queue, PriorityQueue
import hashlib


class MessagePriority(Enum):
    """메시지 우선순위"""
    CRITICAL = 1    # 시스템 오류, 긴급 알림
    HIGH = 2        # 지연 발행, 중요 상태 변화
    NORMAL = 3      # 정시 발행, 일반 상태
    LOW = 4         # 테스트, 정보성 메시지


class BotType(Enum):
    """BOT 타입"""
    NEWS_COMPARISON = "comparison"      # 뉴스 비교 알림
    NEWS_DELAY = "delay"               # 지연 발행 알림
    NEWS_REPORT = "report"             # 일일 통합 리포트
    NEWS_STATUS = "status"             # 정시 발행 알림
    NEWS_NO_DATA = "no_data"           # 데이터 갱신 없음
    WATCHHAMSTER_ERROR = "error"       # 워치햄스터 오류
    WATCHHAMSTER_STATUS = "watchhamster_status"  # 워치햄스터 상태
    TEST = "test"                      # 테스트 메시지


class WebhookEndpoint(Enum):
    """웹훅 엔드포인트"""
    NEWS_MAIN = "news_main"            # 뉴스 메인 채널
    WATCHHAMSTER = "watchhamster"      # 워치햄스터 채널
    TEST = "test"                      # 테스트 채널


@dataclass
class WebhookMessage:
    """웹훅 메시지 데이터 클래스"""
    id: str
    bot_type: BotType
    priority: MessagePriority
    endpoint: WebhookEndpoint
    bot_name: str
    bot_icon: str
    title: str
    content: str
    color: str
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3
    test_mode: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def __lt__(self, other):
        """우선순위 큐를 위한 비교 연산자"""
        return self.priority.value < other.priority.value


@dataclass
class WebhookSendResult:
    """웹훅 전송 결과"""
    success: bool
    message_id: str
    status_code: Optional[int]
    response_text: Optional[str]
    error_message: Optional[str]
    retry_count: int
    send_time: datetime
    processing_time: float


class DoorayWebhookSender:
    """
    Dooray 웹훅 전송 시스템
    
    기존 WatchHamster_Project의 웹훅 전송 로직을 완전히 이식한 시스템입니다.
    """
    
    def __init__(self, test_mode: bool = False):
        """
        웹훅 전송자 초기화
        
        Args:
            test_mode (bool): 테스트 모드 활성화 여부
        """
        self.logger = logging.getLogger(__name__)
        self.test_mode = test_mode
        
        # 웹훅 URL 설정 (기존 URL 유지)
        self.webhook_urls = {
            WebhookEndpoint.NEWS_MAIN: "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg",
            WebhookEndpoint.WATCHHAMSTER: "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ",
            WebhookEndpoint.TEST: "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"  # 테스트용은 메인과 동일
        }
        
        # BOT 프로필 이미지 URL
        self.bot_profile_image = "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg"
        
        # BOT 타입별 라우팅 설정
        self.bot_routing = {
            BotType.NEWS_COMPARISON: WebhookEndpoint.NEWS_MAIN,
            BotType.NEWS_DELAY: WebhookEndpoint.NEWS_MAIN,
            BotType.NEWS_REPORT: WebhookEndpoint.NEWS_MAIN,
            BotType.NEWS_STATUS: WebhookEndpoint.NEWS_MAIN,
            BotType.NEWS_NO_DATA: WebhookEndpoint.NEWS_MAIN,
            BotType.WATCHHAMSTER_ERROR: WebhookEndpoint.WATCHHAMSTER,
            BotType.WATCHHAMSTER_STATUS: WebhookEndpoint.WATCHHAMSTER,
            BotType.TEST: WebhookEndpoint.TEST
        }
        
        # 메시지 큐 시스템
        self.message_queue = PriorityQueue()
        self.processing_queue = Queue()
        self.failed_messages = []
        
        # 전송 통계
        self.send_statistics = {
            'total_sent': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'retry_attempts': 0,
            'last_send_time': None,
            'average_response_time': 0.0
        }
        
        # 중복 방지를 위한 메시지 해시 캐시
        self.message_hash_cache = set()
        self.cache_cleanup_interval = 3600  # 1시간마다 캐시 정리
        self.last_cache_cleanup = datetime.now()
        
        # 전송 제어
        self.is_running = True
        self.send_lock = threading.Lock()
        self.queue_processor_thread = None
        
        # 큐 처리 스레드 시작
        self._start_queue_processor()
        
        self.logger.info("Dooray 웹훅 전송 시스템 초기화 완료")
    
    def _start_queue_processor(self):
        """큐 처리 스레드 시작"""
        self.queue_processor_thread = threading.Thread(
            target=self._process_message_queue,
            daemon=True
        )
        self.queue_processor_thread.start()
        self.logger.info("메시지 큐 처리 스레드 시작됨")
    
    def _process_message_queue(self):
        """메시지 큐 처리 (백그라운드 스레드)"""
        while self.is_running:
            try:
                # 우선순위 큐에서 메시지 가져오기 (타임아웃 1초)
                if not self.message_queue.empty():
                    message = self.message_queue.get(timeout=1)
                    
                    # 메시지 전송 시도
                    result = self._send_single_message(message)
                    
                    # 전송 실패 시 재시도 처리
                    if not result.success and message.retry_count < message.max_retries:
                        message.retry_count += 1
                        self.send_statistics['retry_attempts'] += 1
                        
                        # 테스트 모드에서는 재시도 지연 단축
                        if self.test_mode:
                            retry_delay = min(0.5 * (2 ** message.retry_count), 2)  # 최대 2초
                        else:
                            retry_delay = min(2 ** message.retry_count, 60)  # 최대 60초
                        
                        time.sleep(retry_delay)
                        
                        # 다시 큐에 추가
                        self.message_queue.put(message)
                        self.logger.warning(f"메시지 재시도 예약: {message.id} (시도 {message.retry_count}/{message.max_retries})")
                    elif not result.success:
                        # 최대 재시도 횟수 초과
                        self.failed_messages.append((message, result))
                        self.logger.error(f"메시지 전송 최종 실패: {message.id}")
                    
                    self.message_queue.task_done()
                else:
                    # 큐가 비어있으면 잠시 대기 (테스트 모드에서는 더 짧게)
                    sleep_time = 0.05 if self.test_mode else 0.1
                    time.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.error(f"큐 처리 중 오류: {e}")
                sleep_time = 0.1 if self.test_mode else 1
                time.sleep(sleep_time)
    
    def generate_dynamic_alert_message(self, data: Dict[str, Any], 
                                     message_type: str = "news_alert") -> str:
        """
        동적 알림 메시지 생성 (기존 generate_dynamic_alert_message 로직 이식)
        
        Args:
            data (dict): 뉴스 데이터 또는 시스템 상태 데이터
            message_type (str): 메시지 타입 ("news_alert", "system_status", "error_alert")
        
        Returns:
            str: 생성된 메시지
        """
        try:
            current_time = datetime.now()
            
            if message_type == "news_alert":
                return self._generate_news_alert_message(data, current_time)
            elif message_type == "system_status":
                return self._generate_system_status_message(data, current_time)
            elif message_type == "error_alert":
                return self._generate_error_alert_message(data, current_time)
            else:
                return self._generate_generic_message(data, current_time)
                
        except Exception as e:
            self.logger.error(f"동적 메시지 생성 오류: {e}")
            return f"메시지 생성 중 오류가 발생했습니다: {e}"
    
    def _generate_news_alert_message(self, data: Dict[str, Any], current_time: datetime) -> str:
        """뉴스 알림 메시지 생성"""
        news_type = data.get('news_type', '알 수 없음')
        status = data.get('status', '알 수 없음')
        last_update = data.get('last_update', current_time)
        delay_minutes = data.get('delay_minutes', 0)
        
        # 뉴스 타입별 이모지 설정
        type_emoji = {
            'exchange-rate': '💱',
            'newyork-market-watch': '🗽',
            'kospi-close': '📈'
        }.get(news_type, '📰')
        
        # 상태별 메시지 생성
        if status == 'delayed':
            message = f"""{type_emoji} POSCO 뉴스 지연 알림

📅 확인 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📰 뉴스 타입: {news_type}
⏰ 지연 시간: {delay_minutes}분
📊 마지막 업데이트: {last_update}

🚨 예상 발행 시간을 {delay_minutes}분 초과했습니다.
📞 필요시 담당자에게 문의하세요."""
            
        elif status == 'latest':
            message = f"""{type_emoji} POSCO 뉴스 정시 발행 완료

📅 발행 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📰 뉴스 타입: {news_type}
📊 업데이트: {last_update}

✅ 뉴스가 정상적으로 발행되었습니다."""
            
        elif status == 'no_data':
            message = f"""{type_emoji} POSCO 뉴스 데이터 갱신 없음

📅 확인 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📰 뉴스 타입: {news_type}
📊 마지막 데이터: {last_update}

💡 현재 새로운 데이터가 확인되지 않았습니다."""
            
        else:
            message = f"""{type_emoji} POSCO 뉴스 상태 알림

📅 확인 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📰 뉴스 타입: {news_type}
📊 상태: {status}
📊 업데이트: {last_update}"""
        
        return message
    
    def _generate_system_status_message(self, data: Dict[str, Any], current_time: datetime) -> str:
        """시스템 상태 메시지 생성"""
        system_status = data.get('status', '알 수 없음')
        cpu_usage = data.get('cpu_usage', 0)
        memory_usage = data.get('memory_usage', 0)
        disk_usage = data.get('disk_usage', 0)
        uptime = data.get('uptime', '알 수 없음')
        
        # 상태별 이모지 설정
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '🚨'
        }.get(system_status, '📊')
        
        message = f"""{status_emoji} POSCO 워치햄스터 시스템 상태

📅 보고 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
🖥️ 시스템 상태: {system_status}
⏱️ 가동 시간: {uptime}

📊 리소스 사용률:
  • CPU: {cpu_usage}%
  • 메모리: {memory_usage}%
  • 디스크: {disk_usage}%

🎯 모든 모니터링 서비스가 정상 작동 중입니다."""
        
        return message
    
    def _generate_error_alert_message(self, data: Dict[str, Any], current_time: datetime) -> str:
        """오류 알림 메시지 생성"""
        error_type = data.get('error_type', '알 수 없는 오류')
        error_message = data.get('error_message', '상세 정보 없음')
        component = data.get('component', '시스템')
        
        message = f"""🚨 POSCO 워치햄스터 오류 발생

📅 발생 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
🔧 구성요소: {component}
⚠️ 오류 타입: {error_type}
📋 오류 내용: {error_message}

🔄 자동 복구를 시도합니다.
📞 문제가 지속되면 담당자에게 문의하세요."""
        
        return message
    
    def _generate_generic_message(self, data: Dict[str, Any], current_time: datetime) -> str:
        """일반 메시지 생성"""
        title = data.get('title', 'POSCO 시스템 알림')
        content = data.get('content', '내용 없음')
        
        message = f"""📢 {title}

📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📋 내용: {content}"""
        
        return message
    
    async def send_posco_news_alert(self, news_data: Dict[str, Any], 
                                  priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """
        POSCO 뉴스 알림 전송
        
        Args:
            news_data (dict): 뉴스 데이터
            priority (MessagePriority): 메시지 우선순위
        
        Returns:
            str: 메시지 ID
        """
        try:
            self.logger.info("POSCO 뉴스 알림 전송 시작")
            
            # 동적 메시지 생성
            message_content = self.generate_dynamic_alert_message(news_data, "news_alert")
            
            # 상태에 따른 색상 설정
            status = news_data.get('status', 'unknown')
            color_map = {
                'latest': '#28a745',    # 초록색 (정상)
                'delayed': '#ffc107',   # 노란색 (지연)
                'no_data': '#6c757d',   # 회색 (정보)
                'error': '#dc3545'      # 빨간색 (오류)
            }
            color = color_map.get(status, '#007bff')  # 기본 파란색
            
            # 뉴스 타입에 따른 BOT 이름 설정
            news_type = news_data.get('news_type', 'news')
            bot_name = f"POSCO 뉴스 {news_type.upper()} 📰"
            
            # 웹훅 메시지 객체 생성
            message = self._create_webhook_message(
                bot_type=BotType.NEWS_STATUS,
                priority=priority,
                bot_name=bot_name,
                title=f"📰 POSCO 뉴스 알림 - {news_type}",
                content=message_content,
                color=color,
                test_mode=self.test_mode
            )
            
            # 큐에 추가
            return self._enqueue_message(message)
            
        except Exception as e:
            self.logger.error(f"POSCO 뉴스 알림 전송 오류: {e}")
            return None
    
    async def send_system_status_report(self, system_status: Dict[str, Any],
                                      priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """
        WatchHamster 시스템 상태 보고서 전송
        
        Args:
            system_status (dict): 시스템 상태 데이터
            priority (MessagePriority): 메시지 우선순위
        
        Returns:
            str: 메시지 ID
        """
        try:
            self.logger.info("WatchHamster 시스템 상태 보고서 전송 시작")
            
            # 동적 메시지 생성
            message_content = self.generate_dynamic_alert_message(system_status, "system_status")
            
            # 상태에 따른 색상 설정
            status = system_status.get('status', 'unknown')
            color_map = {
                'healthy': '#28a745',   # 초록색 (정상)
                'warning': '#ffc107',   # 노란색 (경고)
                'critical': '#dc3545'  # 빨간색 (위험)
            }
            color = color_map.get(status, '#007bff')  # 기본 파란색
            
            # 웹훅 메시지 객체 생성
            message = self._create_webhook_message(
                bot_type=BotType.WATCHHAMSTER_STATUS,
                priority=priority,
                bot_name="POSCO 워치햄스터 🎯🛡️",
                title="🎯🛡️ 시스템 상태 보고",
                content=message_content,
                color=color,
                test_mode=self.test_mode
            )
            
            # 큐에 추가
            return self._enqueue_message(message)
            
        except Exception as e:
            self.logger.error(f"시스템 상태 보고서 전송 오류: {e}")
            return None
    
    async def send_error_alert(self, error_data: Dict[str, Any],
                             priority: MessagePriority = MessagePriority.CRITICAL) -> str:
        """
        오류 알림 전송
        
        Args:
            error_data (dict): 오류 데이터
            priority (MessagePriority): 메시지 우선순위
        
        Returns:
            str: 메시지 ID
        """
        try:
            self.logger.info("오류 알림 전송 시작")
            
            # 동적 메시지 생성
            message_content = self.generate_dynamic_alert_message(error_data, "error_alert")
            
            # 웹훅 메시지 객체 생성
            message = self._create_webhook_message(
                bot_type=BotType.WATCHHAMSTER_ERROR,
                priority=priority,
                bot_name="POSCO 워치햄스터 🚨",
                title="🚨 시스템 오류 발생",
                content=message_content,
                color="#dc3545",  # 빨간색
                test_mode=self.test_mode
            )
            
            # 큐에 추가
            return self._enqueue_message(message)
            
        except Exception as e:
            self.logger.error(f"오류 알림 전송 오류: {e}")
            return None
    
    async def send_test_message(self, test_content: str, 
                              priority: MessagePriority = MessagePriority.LOW) -> str:
        """
        테스트 메시지 전송
        
        Args:
            test_content (str): 테스트 내용
            priority (MessagePriority): 메시지 우선순위
        
        Returns:
            str: 메시지 ID
        """
        try:
            self.logger.info("테스트 메시지 전송 시작")
            
            # 테스트 메시지 포맷팅
            current_time = datetime.now()
            formatted_message = f"""🧪 [TEST] POSCO 시스템 테스트

📅 테스트 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📋 테스트 내용: {test_content}

✅ 웹훅 전송 시스템이 정상적으로 작동합니다."""
            
            # 웹훅 메시지 객체 생성
            message = self._create_webhook_message(
                bot_type=BotType.TEST,
                priority=priority,
                bot_name="[TEST] POSCO 시스템",
                title="🧪 [TEST] 시스템 테스트",
                content=formatted_message,
                color="#6c757d",  # 회색
                test_mode=True
            )
            
            # 큐에 추가
            return self._enqueue_message(message)
            
        except Exception as e:
            self.logger.error(f"테스트 메시지 전송 오류: {e}")
            return None
    
    def _create_webhook_message(self, bot_type: BotType, priority: MessagePriority,
                              bot_name: str, title: str, content: str, color: str,
                              test_mode: bool = False) -> WebhookMessage:
        """웹훅 메시지 객체 생성"""
        # 메시지 ID 생성 (타임스탬프 + 해시)
        timestamp = datetime.now()
        message_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        # 엔드포인트 결정
        endpoint = self.bot_routing.get(bot_type, WebhookEndpoint.NEWS_MAIN)
        
        return WebhookMessage(
            id=message_id,
            bot_type=bot_type,
            priority=priority,
            endpoint=endpoint,
            bot_name=bot_name,
            bot_icon=self.bot_profile_image,
            title=title,
            content=content,
            color=color,
            timestamp=timestamp,
            test_mode=test_mode
        )
    
    def _enqueue_message(self, message: WebhookMessage) -> str:
        """메시지를 큐에 추가"""
        try:
            # 중복 메시지 확인
            message_hash = self._generate_message_hash(message)
            if message_hash in self.message_hash_cache:
                self.logger.warning(f"중복 메시지 감지, 전송 건너뜀: {message.id}")
                return None
            
            # 캐시에 추가
            self.message_hash_cache.add(message_hash)
            
            # 큐에 추가
            self.message_queue.put(message)
            self.logger.info(f"메시지 큐에 추가됨: {message.id} (우선순위: {message.priority.name})")
            
            # 캐시 정리 (필요시)
            self._cleanup_cache_if_needed()
            
            return message.id
            
        except Exception as e:
            self.logger.error(f"메시지 큐 추가 오류: {e}")
            return None
    
    def _generate_message_hash(self, message: WebhookMessage) -> str:
        """메시지 해시 생성 (중복 방지용)"""
        hash_content = f"{message.bot_type.value}_{message.title}_{message.content[:100]}"
        return hashlib.md5(hash_content.encode()).hexdigest()
    
    def _cleanup_cache_if_needed(self):
        """필요시 캐시 정리"""
        current_time = datetime.now()
        if (current_time - self.last_cache_cleanup).total_seconds() >= self.cache_cleanup_interval:
            # 캐시 크기 제한 (최대 1000개)
            if len(self.message_hash_cache) > 1000:
                # 오래된 해시들 제거 (간단히 절반 제거)
                cache_list = list(self.message_hash_cache)
                self.message_hash_cache = set(cache_list[len(cache_list)//2:])
                self.logger.info(f"메시지 해시 캐시 정리 완료: {len(self.message_hash_cache)}개 유지")
            
            self.last_cache_cleanup = current_time
    
    def _send_single_message(self, message: WebhookMessage) -> WebhookSendResult:
        """단일 메시지 전송"""
        start_time = time.time()
        
        try:
            # 웹훅 URL 가져오기
            webhook_url = self.webhook_urls.get(message.endpoint)
            if not webhook_url:
                return WebhookSendResult(
                    success=False,
                    message_id=message.id,
                    status_code=None,
                    response_text=None,
                    error_message=f"알 수 없는 엔드포인트: {message.endpoint}",
                    retry_count=message.retry_count,
                    send_time=datetime.now(),
                    processing_time=time.time() - start_time
                )
            
            # Dooray 웹훅 페이로드 구성
            payload = {
                "botName": message.bot_name,
                "botIconImage": message.bot_icon,
                "text": message.title,
                "attachments": [{
                    "color": message.color,
                    "text": message.content
                }]
            }
            
            # HTTP 요청 전송
            with self.send_lock:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            processing_time = time.time() - start_time
            
            # 응답 처리
            if response.status_code == 200:
                # 전송 성공
                self.send_statistics['successful_sends'] += 1
                self.send_statistics['total_sent'] += 1
                self.send_statistics['last_send_time'] = datetime.now()
                
                # 평균 응답 시간 업데이트
                if self.send_statistics['average_response_time'] == 0:
                    self.send_statistics['average_response_time'] = processing_time
                else:
                    self.send_statistics['average_response_time'] = (
                        self.send_statistics['average_response_time'] * 0.9 + processing_time * 0.1
                    )
                
                self.logger.info(f"메시지 전송 성공: {message.id} ({processing_time:.3f}초)")
                
                return WebhookSendResult(
                    success=True,
                    message_id=message.id,
                    status_code=response.status_code,
                    response_text=response.text,
                    error_message=None,
                    retry_count=message.retry_count,
                    send_time=datetime.now(),
                    processing_time=processing_time
                )
            else:
                # 전송 실패
                self.send_statistics['failed_sends'] += 1
                self.send_statistics['total_sent'] += 1
                
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.warning(f"메시지 전송 실패: {message.id} - {error_msg}")
                
                return WebhookSendResult(
                    success=False,
                    message_id=message.id,
                    status_code=response.status_code,
                    response_text=response.text,
                    error_message=error_msg,
                    retry_count=message.retry_count,
                    send_time=datetime.now(),
                    processing_time=processing_time
                )
                
        except requests.exceptions.Timeout:
            error_msg = "요청 타임아웃"
            self.logger.warning(f"메시지 전송 타임아웃: {message.id}")
            
        except requests.exceptions.ConnectionError:
            error_msg = "연결 오류"
            self.logger.warning(f"메시지 전송 연결 오류: {message.id}")
            
        except Exception as e:
            error_msg = f"예상치 못한 오류: {e}"
            self.logger.error(f"메시지 전송 중 오류: {message.id} - {e}")
        
        # 오류 발생 시 실패 결과 반환
        self.send_statistics['failed_sends'] += 1
        self.send_statistics['total_sent'] += 1
        
        return WebhookSendResult(
            success=False,
            message_id=message.id,
            status_code=None,
            response_text=None,
            error_message=error_msg,
            retry_count=message.retry_count,
            send_time=datetime.now(),
            processing_time=time.time() - start_time
        )
    
    def get_queue_status(self) -> Dict[str, Any]:
        """큐 상태 조회"""
        return {
            'timestamp': datetime.now(),
            'queue_size': self.message_queue.qsize(),
            'failed_messages_count': len(self.failed_messages),
            'cache_size': len(self.message_hash_cache),
            'is_running': self.is_running,
            'statistics': self.send_statistics.copy()
        }
    
    def get_send_statistics(self) -> Dict[str, Any]:
        """전송 통계 조회"""
        stats = self.send_statistics.copy()
        
        # 성공률 계산
        if stats['total_sent'] > 0:
            stats['success_rate'] = stats['successful_sends'] / stats['total_sent']
        else:
            stats['success_rate'] = 0.0
        
        # 실패율 계산
        if stats['total_sent'] > 0:
            stats['failure_rate'] = stats['failed_sends'] / stats['total_sent']
        else:
            stats['failure_rate'] = 0.0
        
        return stats
    
    def clear_failed_messages(self):
        """실패한 메시지 목록 정리"""
        cleared_count = len(self.failed_messages)
        self.failed_messages.clear()
        self.logger.info(f"실패한 메시지 {cleared_count}개 정리됨")
    
    def shutdown(self, timeout: int = 10):
        """웹훅 전송 시스템 종료"""
        self.logger.info("웹훅 전송 시스템 종료 시작")
        
        self.is_running = False
        
        # 큐에 남은 메시지들 처리 대기 (타임아웃 적용)
        if not self.message_queue.empty():
            queue_size = self.message_queue.qsize()
            self.logger.info(f"큐에 남은 메시지 {queue_size}개 처리 대기 중... (최대 {timeout}초)")
            
            # 타임아웃과 함께 큐 처리 대기
            start_time = time.time()
            while not self.message_queue.empty() and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.message_queue.empty():
                remaining = self.message_queue.qsize()
                self.logger.warning(f"타임아웃으로 인해 {remaining}개 메시지가 처리되지 않고 종료됩니다")
        
        # 스레드 종료 대기
        if self.queue_processor_thread and self.queue_processor_thread.is_alive():
            self.queue_processor_thread.join(timeout=3)
            if self.queue_processor_thread.is_alive():
                self.logger.warning("큐 처리 스레드가 정상 종료되지 않았습니다")
        
        self.logger.info("웹훅 전송 시스템 종료 완료")


# 편의를 위한 별칭
WebhookSender = DoorayWebhookSender


if __name__ == "__main__":
    # 테스트 코드
    import logging
    import asyncio
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    async def test_webhook_sender():
        """웹훅 전송자 테스트"""
        # 웹훅 전송자 생성
        webhook_sender = DoorayWebhookSender(test_mode=True)
        
        # 테스트 메시지 전송
        test_message_id = await webhook_sender.send_test_message("웹훅 전송 시스템 테스트")
        print(f"테스트 메시지 ID: {test_message_id}")
        
        # 뉴스 알림 테스트
        news_data = {
            'news_type': 'exchange-rate',
            'status': 'latest',
            'last_update': datetime.now(),
            'delay_minutes': 0
        }
        news_message_id = await webhook_sender.send_posco_news_alert(news_data)
        print(f"뉴스 알림 메시지 ID: {news_message_id}")
        
        # 시스템 상태 보고서 테스트
        system_status = {
            'status': 'healthy',
            'cpu_usage': 25,
            'memory_usage': 45,
            'disk_usage': 60,
            'uptime': '2일 3시간 15분'
        }
        status_message_id = await webhook_sender.send_system_status_report(system_status)
        print(f"상태 보고서 메시지 ID: {status_message_id}")
        
        # 잠시 대기 (전송 완료 대기)
        await asyncio.sleep(2)
        
        # 상태 확인
        status = webhook_sender.get_queue_status()
        print(f"큐 상태: {status}")
        
        statistics = webhook_sender.get_send_statistics()
        print(f"전송 통계: {statistics}")
        
        # 종료
        webhook_sender.shutdown()
    
    # 테스트 실행
    asyncio.run(test_webhook_sender())