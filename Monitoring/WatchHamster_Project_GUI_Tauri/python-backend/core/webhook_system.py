#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 시스템 및 메시지 템플릿 엔진 (포팅)
기존 WatchHamster 웹훅 및 메시지 템플릿 로직을 FastAPI 서비스로 포팅

주요 기능:
- Discord/Slack 웹훅 전송
- POSCO 스타일 메시지 템플릿 엔진
- 동적 메시지 생성
- 메시지 전송 히스토리 관리
"""

import logging
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp가 설치되지 않았습니다. 웹훅 전송 기능이 제한됩니다.")

class MessageType(Enum):
    """메시지 타입"""
    DEPLOYMENT_SUCCESS = "deployment_success"
    DEPLOYMENT_FAILURE = "deployment_failure"
    DEPLOYMENT_START = "deployment_start"
    SYSTEM_STATUS = "system_status"
    DATA_UPDATE = "data_update"
    ERROR_ALERT = "error_alert"
    MAINTENANCE = "maintenance"

class MessagePriority(Enum):
    """메시지 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class WebhookMessage:
    """웹훅 메시지"""
    id: str
    message_type: MessageType
    priority: MessagePriority
    title: str
    body: str
    timestamp: datetime
    color: str
    webhook_url: str
    sent: bool = False
    sent_at: Optional[datetime] = None
    response_status: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class MessageTemplate:
    """메시지 템플릿"""
    message_type: MessageType
    title_template: str
    body_template: str
    priority: MessagePriority
    color: str

class MessageTemplateEngine:
    """메시지 템플릿 엔진"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """메시지 템플릿 엔진 초기화"""
        self.config_dir = config_dir or os.getcwd()
        self.logger = logger
        
        # POSCO 브랜딩 설정
        self.brand_config = {
            "company_name": "POSCO",
            "system_name": "POSCO 통합 분석 시스템",
            "brand_emoji": "🏭",
            "success_emoji": "✅",
            "warning_emoji": "⚠️",
            "error_emoji": "❌",
            "info_emoji": "ℹ️",
            "chart_emoji": "📊",
            "web_emoji": "🌐",
            "time_emoji": "⏰"
        }
        
        # 기본 템플릿 로드
        self.templates = self._load_default_templates()
        
        self.logger.info("🎨 MessageTemplateEngine 초기화 완료")
    
    def _load_default_templates(self) -> Dict[MessageType, MessageTemplate]:
        """기본 메시지 템플릿 로드"""
        return {
            MessageType.DEPLOYMENT_SUCCESS: MessageTemplate(
                message_type=MessageType.DEPLOYMENT_SUCCESS,
                title_template="{brand_emoji} {company_name} 분석 리포트 업데이트 완료",
                body_template="""
{success_emoji} **배포 성공 알림**

**{system_name}**에서 최신 분석 리포트가 성공적으로 업데이트되었습니다.

{chart_emoji} **업데이트 정보**
• 배포 ID: `{deployment_id}`
• 완료 시간: {completion_time}
• 처리 단계: {steps_completed}단계 완료
• 소요 시간: {duration}

{web_emoji} **접속 정보**
• 리포트 URL: {report_url}
• 상태: {status_message}

{info_emoji} **주요 내용**
{content_summary}

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                priority=MessagePriority.NORMAL,
                color="#28a745"
            ),
            
            MessageType.DEPLOYMENT_FAILURE: MessageTemplate(
                message_type=MessageType.DEPLOYMENT_FAILURE,
                title_template="{brand_emoji} {company_name} 시스템 배포 실패 알림",
                body_template="""
{error_emoji} **배포 실패 알림**

**{system_name}**에서 리포트 배포 중 문제가 발생했습니다.

{chart_emoji} **실패 정보**
• 배포 ID: `{deployment_id}`
• 실패 시간: {failure_time}
• 오류 단계: {failed_step}
• 롤백 상태: {rollback_status}

{warning_emoji} **오류 내용**
```
{error_message}
```

{info_emoji} **조치 사항**
• 시스템 관리자가 자동으로 알림을 받았습니다
• 문제 해결 후 자동으로 재배포됩니다
• 긴급한 경우 시스템 관리자에게 연락하세요

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                priority=MessagePriority.HIGH,
                color="#dc3545"
            ),
            
            MessageType.SYSTEM_STATUS: MessageTemplate(
                message_type=MessageType.SYSTEM_STATUS,
                title_template="{brand_emoji} {company_name} 시스템 상태 보고",
                body_template="""
{info_emoji} **시스템 상태 보고**

**{system_name}** 현재 상태를 보고드립니다.

{chart_emoji} **시스템 메트릭**
• CPU 사용률: {cpu_usage}%
• 메모리 사용률: {memory_usage}%
• 디스크 사용률: {disk_usage}%
• 활성 서비스: {active_services}개

{web_emoji} **서비스 상태**
{service_status}

{time_emoji} **업타임**: {uptime}

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                priority=MessagePriority.NORMAL,
                color="#17a2b8"
            ),
            
            MessageType.ERROR_ALERT: MessageTemplate(
                message_type=MessageType.ERROR_ALERT,
                title_template="{brand_emoji} {company_name} 시스템 오류 알림",
                body_template="""
{error_emoji} **시스템 오류 알림**

**{system_name}**에서 오류가 감지되었습니다.

{warning_emoji} **오류 정보**
• 오류 유형: {error_type}
• 발생 시간: {error_time}
• 영향 범위: {affected_components}
• 심각도: {severity}

{chart_emoji} **오류 내용**
```
{error_message}
```

{info_emoji} **조치 사항**
{recovery_actions}

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                priority=MessagePriority.CRITICAL,
                color="#dc3545"
            )
        }
    
    def generate_message(self, message_type: MessageType, data: Dict[str, Any]) -> Dict[str, Any]:
        """메시지 생성"""
        try:
            if message_type not in self.templates:
                raise ValueError(f"지원하지 않는 메시지 타입: {message_type}")
            
            template = self.templates[message_type]
            
            # 브랜딩 데이터와 사용자 데이터 병합
            template_data = {**self.brand_config, **data}
            
            # 템플릿 렌더링
            title = template.title_template.format(**template_data)
            body = template.body_template.format(**template_data)
            
            return {
                "message_type": message_type.value,
                "priority": template.priority.value,
                "title": title,
                "body": body,
                "color": template.color,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"메시지 생성 실패: {e}")
            return {
                "message_type": "error",
                "priority": "high",
                "title": "메시지 생성 오류",
                "body": f"메시지 생성 중 오류가 발생했습니다: {str(e)}",
                "color": "#dc3545",
                "timestamp": datetime.now().isoformat()
            }

class WebhookSystem:
    """웹훅 시스템"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """웹훅 시스템 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.logger = logger
        
        # 메시지 템플릿 엔진
        self.template_engine = MessageTemplateEngine()
        
        # 웹훅 설정
        self.webhook_urls = {
            "default": None,
            "posco": None,
            "alerts": None
        }
        
        # 메시지 히스토리
        self.message_history: List[WebhookMessage] = []
        
        # 전송 통계
        self.send_stats = {
            "total_sent": 0,
            "successful_sent": 0,
            "failed_sent": 0,
            "last_sent": None
        }
        
        # 웹훅 설정 로드
        self._load_webhook_config()
        
        self.logger.info("🔗 WebhookSystem 초기화 완료")
    
    def _load_webhook_config(self):
        """웹훅 설정 로드"""
        try:
            config_file = os.path.join(self.base_dir, "config", "webhook_config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.webhook_urls.update(config.get("webhook_urls", {}))
                self.logger.info("웹훅 설정 로드 완료")
            else:
                self.logger.warning("웹훅 설정 파일을 찾을 수 없습니다")
                
        except Exception as e:
            self.logger.error(f"웹훅 설정 로드 실패: {e}")
    
    async def send_message(self, message_type: MessageType, data: Dict[str, Any], 
                          webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """메시지 전송"""
        try:
            # 웹훅 URL 결정
            url = webhook_url or self.webhook_urls.get("default")
            if not url:
                return {
                    "success": False,
                    "message": "웹훅 URL이 설정되지 않았습니다"
                }
            
            # 메시지 생성
            message_data = self.template_engine.generate_message(message_type, data)
            
            # 웹훅 메시지 객체 생성
            message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            webhook_message = WebhookMessage(
                id=message_id,
                message_type=message_type,
                priority=MessagePriority(message_data["priority"]),
                title=message_data["title"],
                body=message_data["body"],
                timestamp=datetime.now(),
                color=message_data["color"],
                webhook_url=url
            )
            
            # 웹훅 전송
            success, status_code, error_msg = await self._send_webhook(url, message_data)
            
            # 전송 결과 업데이트
            webhook_message.sent = success
            webhook_message.sent_at = datetime.now()
            webhook_message.response_status = status_code
            webhook_message.error_message = error_msg
            
            # 히스토리에 추가
            self.message_history.append(webhook_message)
            
            # 통계 업데이트
            self.send_stats["total_sent"] += 1
            if success:
                self.send_stats["successful_sent"] += 1
            else:
                self.send_stats["failed_sent"] += 1
            self.send_stats["last_sent"] = datetime.now()
            
            # 히스토리 크기 제한 (최근 100개만 유지)
            if len(self.message_history) > 100:
                self.message_history = self.message_history[-100:]
            
            self.logger.info(f"웹훅 메시지 전송: {message_id} - {'성공' if success else '실패'}")
            
            return {
                "success": success,
                "message_id": message_id,
                "message": "메시지 전송 완료" if success else f"메시지 전송 실패: {error_msg}",
                "webhook_message": asdict(webhook_message)
            }
            
        except Exception as e:
            self.logger.error(f"메시지 전송 실패: {e}")
            return {
                "success": False,
                "message": f"메시지 전송 실패: {str(e)}"
            }
    
    async def _send_webhook(self, url: str, message_data: Dict[str, Any]) -> tuple[bool, Optional[int], Optional[str]]:
        """실제 웹훅 전송"""
        if not AIOHTTP_AVAILABLE:
            return False, None, "aiohttp가 설치되지 않았습니다"
            
        try:
            # Discord/Slack 웹훅 페이로드 생성
            payload = {
                "embeds": [{
                    "title": message_data["title"],
                    "description": message_data["body"],
                    "color": int(message_data["color"].replace("#", ""), 16),
                    "timestamp": message_data["timestamp"],
                    "footer": {
                        "text": "POSCO WatchHamster System"
                    }
                }]
            }
            
            # HTTP 요청 전송
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200 or response.status == 204:
                        return True, response.status, None
                    else:
                        error_text = await response.text()
                        return False, response.status, f"HTTP {response.status}: {error_text}"
                        
        except asyncio.TimeoutError:
            return False, None, "요청 타임아웃"
        except Exception as e:
            return False, None, str(e)
    
    async def send_deployment_success(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """배포 성공 메시지 전송"""
        return await self.send_message(MessageType.DEPLOYMENT_SUCCESS, deployment_data)
    
    async def send_deployment_failure(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """배포 실패 메시지 전송"""
        return await self.send_message(MessageType.DEPLOYMENT_FAILURE, deployment_data)
    
    async def send_system_status(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """시스템 상태 메시지 전송"""
        return await self.send_message(MessageType.SYSTEM_STATUS, status_data)
    
    async def send_error_alert(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """오류 알림 메시지 전송"""
        return await self.send_message(MessageType.ERROR_ALERT, error_data)
    
    def get_message_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """메시지 히스토리 조회"""
        try:
            recent_messages = self.message_history[-limit:] if limit > 0 else self.message_history
            return [asdict(msg) for msg in recent_messages]
        except Exception as e:
            self.logger.error(f"메시지 히스토리 조회 실패: {e}")
            return []
    
    def get_send_statistics(self) -> Dict[str, Any]:
        """전송 통계 조회"""
        try:
            success_rate = 0
            if self.send_stats["total_sent"] > 0:
                success_rate = (self.send_stats["successful_sent"] / self.send_stats["total_sent"]) * 100
            
            return {
                **self.send_stats,
                "success_rate": round(success_rate, 2),
                "last_sent": self.send_stats["last_sent"].isoformat() if self.send_stats["last_sent"] else None
            }
        except Exception as e:
            self.logger.error(f"전송 통계 조회 실패: {e}")
            return {}
    
    def update_webhook_url(self, webhook_type: str, url: str):
        """웹훅 URL 업데이트"""
        try:
            self.webhook_urls[webhook_type] = url
            self.logger.info(f"웹훅 URL 업데이트: {webhook_type}")
        except Exception as e:
            self.logger.error(f"웹훅 URL 업데이트 실패: {e}")
    
    async def test_webhook_connection(self, webhook_url: str) -> Dict[str, Any]:
        """웹훅 연결 테스트"""
        try:
            test_data = {
                "deployment_id": "test_connection",
                "completion_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "steps_completed": 3,
                "duration": "테스트",
                "report_url": "https://test.example.com",
                "status_message": "연결 테스트",
                "content_summary": "웹훅 연결 테스트 메시지입니다."
            }
            
            result = await self.send_message(
                MessageType.DEPLOYMENT_SUCCESS,
                test_data,
                webhook_url
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"웹훅 연결 테스트 실패: {e}")
            return {
                "success": False,
                "message": f"웹훅 연결 테스트 실패: {str(e)}"
            }