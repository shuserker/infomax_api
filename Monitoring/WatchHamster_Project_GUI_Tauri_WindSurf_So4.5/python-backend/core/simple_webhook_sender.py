#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 웹훅 전송 시스템 (의존성 제거 버전)
기존 WatchHamster_Project의 핵심 로직만 이식
"""

import requests
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class SimpleWebhookSender:
    """간단한 Dooray 웹훅 발송 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 웹훅 URL (기존 프로젝트에서 복사)
        self.news_webhook_url = "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"
        self.watchhamster_webhook_url = "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"
        
        # BOT 프로필 이미지
        self.bot_icon = "https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg"
        
        self.logger.info("SimpleWebhookSender 초기화 완료")
    
    def send_test_message(self, test_content: str, channel: str = "news") -> Optional[str]:
        """
        테스트 메시지 발송
        
        Args:
            test_content: 테스트 내용
            channel: 발송 채널 ("news" 또는 "watchhamster")
        
        Returns:
            메시지 ID (성공 시) 또는 None (실패 시)
        """
        try:
            current_time = datetime.now()
            
            # 채널에 따라 웹훅 URL 선택
            if channel == "watchhamster":
                webhook_url = self.watchhamster_webhook_url
                bot_name = "POSCO 워치햄스터 🎯🛡️"
            else:
                webhook_url = self.news_webhook_url
                bot_name = "[TEST] POSCO 시스템"
            
            # 메시지 포맷팅 (기존 프로젝트 포맷)
            formatted_message = f"""🧪 [TEST] POSCO 시스템 테스트

📅 테스트 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
📋 테스트 내용: {test_content}

✅ 웹훅 전송 시스템이 정상적으로 작동합니다."""
            
            # Dooray 웹훅 페이로드 (기존 포맷)
            payload = {
                "botName": bot_name,
                "botIconImage": self.bot_icon,
                "text": "🧪 [TEST] 시스템 테스트",
                "attachments": [{
                    "color": "#6c757d",  # 회색
                    "text": formatted_message
                }]
            }
            
            # HTTP 요청 전송
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            
            message_id = f"test_{int(current_time.timestamp())}"
            self.logger.info(f"테스트 메시지 전송 성공: {message_id}")
            
            return message_id
            
        except Exception as e:
            self.logger.error(f"테스트 메시지 전송 실패: {e}")
            return None
    
    def send_news_message(self, title: str, content: str, color: str = "#28a745") -> Optional[str]:
        """
        뉴스 메시지 발송
        
        Args:
            title: 메시지 제목
            content: 메시지 내용
            color: 메시지 색상 (기본: 녹색)
        
        Returns:
            메시지 ID (성공 시) 또는 None (실패 시)
        """
        try:
            current_time = datetime.now()
            
            # Dooray 웹훅 페이로드
            payload = {
                "botName": "POSCO 뉴스 📊",
                "botIconImage": self.bot_icon,
                "text": title,
                "attachments": [{
                    "color": color,
                    "text": content
                }]
            }
            
            # HTTP 요청 전송
            response = requests.post(
                self.news_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            
            message_id = f"news_{int(current_time.timestamp())}"
            self.logger.info(f"뉴스 메시지 전송 성공: {message_id}")
            
            return message_id
            
        except Exception as e:
            self.logger.error(f"뉴스 메시지 전송 실패: {e}")
            return None
    
    def send_custom_message(self, webhook_url: str, bot_name: str, title: str, 
                          content: str, color: str = "#28a745") -> Optional[str]:
        """
        커스텀 메시지 발송 (URL 직접 지정)
        
        Args:
            webhook_url: Dooray 웹훅 URL
            bot_name: BOT 이름
            title: 메시지 제목
            content: 메시지 내용
            color: 메시지 색상
        
        Returns:
            메시지 ID (성공 시) 또는 None (실패 시)
        """
        try:
            current_time = datetime.now()
            
            # Dooray 웹훅 페이로드
            payload = {
                "botName": bot_name,
                "botIconImage": self.bot_icon,
                "text": title,
                "attachments": [{
                    "color": color,
                    "text": content
                }]
            }
            
            # HTTP 요청 전송
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            
            message_id = f"custom_{int(current_time.timestamp())}"
            self.logger.info(f"커스텀 메시지 전송 성공: {message_id}")
            
            return message_id
            
        except Exception as e:
            self.logger.error(f"커스텀 메시지 전송 실패: {e}")
            return None
