# -*- coding: utf-8 -*-
"""
알림 전송 관련 모듈
"""

import requests
from datetime import datetime


class DoorayNotifier:
    """
    Dooray 웹훅 알림 전송 클래스
    """
    
    def __init__(self, webhook_url, bot_profile_image_url):
        """
        알림 전송기 초기화
        
        Args:
            webhook_url (str): Dooray 웹훅 URL
            bot_profile_image_url (str): 봇 프로필 이미지 URL
        """
        self.webhook_url = webhook_url
        self.bot_profile_image_url = bot_profile_image_url
    
    def send_notification(self, message, is_error=False, bot_name_suffix=""):
        """
        Dooray 웹훅으로 알림 메시지 전송
        
        Args:
            message (str): 전송할 메시지 내용
            is_error (bool): 오류 알림 여부 (색상 및 제목 변경)
            bot_name_suffix (str): 봇 이름에 추가할 접미사
        """
        try:
            color = "#ff4444" if is_error else "#0066cc"
            bot_name = f"POSCO 뉴스 {'❌' if is_error else '🔔'}{bot_name_suffix}"
            preview_text = message.split('\n')[0] if '\n' in message else message[:50]
            
            lines = message.split('\n')
            detail_message = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            payload = {
                "botName": bot_name,
                "botIconImage": self.bot_profile_image_url,
                "text": preview_text,
                "attachments": [{
                    "color": color,
                    "text": detail_message
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Dooray 알림 전송 성공: {datetime.now()}")
                return True
            else:
                print(f"❌ Dooray 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Dooray 웹훅 오류: {e}")
            return False
    
    def send_status_notification(self, current_data, status_info):
        """
        현재 상태 상세 알림 전송
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            status_info (str): 상태 정보 문자열
        """
        message = "📊 현재 데이터 상태\n\n"
        
        if current_data:
            # 상태 정보 구성 로직은 기존과 동일
            # 여기서는 간단한 버전으로 구현
            for news_type, news_data in current_data.items():
                title = news_data.get('title', '제목 없음')[:45]
                date = news_data.get('date', '')
                time = news_data.get('time', '')
                
                if date and time:
                    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                    formatted_time = f"{time[:2]}:{time[2:4]}" if len(time) >= 4 else time
                    datetime_str = f"{formatted_date} {formatted_time}"
                else:
                    datetime_str = "데이터 없음"
                
                message += f"📰 {news_type.upper()}\n"
                message += f"📅 시간: {datetime_str}\n"
                message += f"📝 제목: {title}\n\n"
        
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"최종 확인: {current_datetime}"
        
        payload = {
            "botName": f"POSCO 뉴스{status_info}",
            "botIconImage": self.bot_profile_image_url,
            "text": "데이터 갱신 없음",
            "attachments": [{
                "color": "#28a745",
                "text": message.replace("📊 현재 데이터 상태\n\n", "")
            }]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ 상태 알림 전송 성공")
                return True
        except Exception as e:
            print(f"❌ 상태 알림 전송 오류: {e}")
        
        return False
    
    def send_change_notification(self, news_type, old_data, new_data):
        """
        뉴스 변경사항 알림 전송
        
        Args:
            news_type (str): 뉴스 타입
            old_data (dict): 이전 뉴스 데이터
            new_data (dict): 현재 뉴스 데이터
        """
        # 변경 타입 분석
        if not old_data or not any(old_data.get(f) for f in ['title', 'content', 'date', 'time']):
            change_type = "🆕 신규입력"
            change_icon = "🆕"
        else:
            change_type = "📝 업데이트"
            change_icon = "📝"
        
        message = f"{change_icon} {news_type.upper()} {change_type}\n"
        
        # 최신 데이터 정보
        new_title = new_data.get('title', '')
        new_date = new_data.get('date', '')
        new_time = new_data.get('time', '')
        
        if new_date and new_time:
            formatted_date = f"{new_date[:4]}-{new_date[4:6]}-{new_date[6:8]}"
            formatted_time = f"{new_time[:2]}:{new_time[2:4]}" if len(new_time) >= 4 else new_time
            message += f"📅 시간: {formatted_date} {formatted_time}\n"
        
        if new_title:
            title_preview = new_title[:60] + "..." if len(new_title) > 60 else new_title
            message += f"📝 제목: {title_preview}\n"
        
        # 작성자 및 카테고리
        writers = new_data.get('writer', [])
        categories = new_data.get('category', [])
        if writers:
            message += f"✍️ 작성자: {', '.join(writers)}\n"
        if categories:
            message += f"🏷️ 카테고리: {', '.join(categories[:3])}"
        
        payload = {
            "botName": "POSCO 뉴스 🔔",
            "botIconImage": self.bot_profile_image_url,
            "text": f"{change_icon} {news_type.upper()} {change_type}",
            "attachments": [{
                "color": "#0066cc",
                "text": message.split('\n', 1)[1] if '\n' in message else message
            }]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ {news_type} 변경 알림 전송 성공")
                return True
        except Exception as e:
            print(f"❌ {news_type} 변경 알림 전송 오류: {e}")
        
        return False