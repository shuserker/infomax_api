# -*- coding: utf-8 -*-
"""
알림 전송 관련 모듈
"""

import requests
from datetime import datetime
from config import NEWS_TYPES, BOT_PROFILE_IMAGE_URL


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
            title = "⚠️ 오류 알림" if is_error else "🔔 POSCO 뉴스 알림"
            
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
        
        각 뉴스 타입별 상태, 발행 시간, 제목 미리보기 등을
        포함한 상세한 상태 정보를 Dooray로 전송합니다.
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            status_info (str): 상태 정보 문자열
        """
        message = "📊 현재 데이터 상태\n\n"
        
        if current_data:
            today_kr = datetime.now().strftime('%Y%m%d')
            news_items = []
            
            for news_type, news_data in current_data.items():
                news_config = NEWS_TYPES.get(news_type, {"display_name": news_type.upper(), "emoji": "📰"})
                emoji = news_config["emoji"]
                type_display = news_config["display_name"]
                
                news_date = news_data.get('date', '')
                news_time = news_data.get('time', '')
                news_title = news_data.get('title', '')
                
                # 요일별 발행 패턴 고려한 데이터 상태 판단
                today_weekday = datetime.now().weekday()
                publish_days = news_config.get('publish_days', [])
                weekday_names = ['월', '화', '수', '목', '금', '토', '일']
                weekday_name = weekday_names[today_weekday]
                
                if not news_date or not news_title:
                    # 오늘 요일에 발행 예상인지 확인
                    if today_weekday in publish_days:
                        status = "🔴"
                        status_text = "데이터 없음"
                        date_time_display = "데이터 없음"
                    else:
                        status = "⏸️"
                        status_text = f"{weekday_name}요일 휴무"
                        date_time_display = "미발행"
                else:
                    if news_date == today_kr:
                        status = "🟢"
                        status_text = "최신"
                    else:
                        status = "🟡"
                        status_text = "과거"
                    
                    # 시간 포맷팅
                    if news_time and len(news_time) >= 4:
                        if len(news_time) >= 6:
                            formatted_time = f"{news_time[:2]}:{news_time[2:4]}:{news_time[4:6]}"
                        elif len(news_time) == 5:
                            if news_time.startswith('6'):
                                news_time = '0' + news_time
                                formatted_time = f"{news_time[:2]}:{news_time[2:4]}:{news_time[4:6]}"
                            else:
                                formatted_time = f"{news_time[:2]}:{news_time[2:4]}:{news_time[4:5]}"
                        else:
                            formatted_time = f"{news_time[:2]}:{news_time[2:4]}"
                        
                        date_time_display = f"{news_date[:4]}-{news_date[4:6]}-{news_date[6:8]} {formatted_time}"
                    else:
                        date_time_display = f"{news_date[:4]}-{news_date[4:6]}-{news_date[6:8]}"
                
                # 제목 미리보기
                title_preview = news_title[:45] + "..." if len(news_title) > 45 else news_title
                
                # 트리 구조로 표시
                message += f"┌ {emoji} {type_display}\n"
                message += f"├ 상태: {status} {status_text}\n"
                message += f"├ 시간: {date_time_display}\n"
                message += f"└ 제목: {title_preview}\n\n"
        
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
        
        신규 입력, 제목/내용 변경, 시간 업데이트 등을 구분하여
        상세한 변경사항 정보를 Dooray로 전송합니다.
        
        Args:
            news_type (str): 뉴스 타입 (예: "exchange-rate")
            old_data (dict): 이전 뉴스 데이터
            new_data (dict): 현재 뉴스 데이터
        """
        # 뉴스 타입별 이모지 매핑
        type_emojis = {
            "exchange-rate": "💱",
            "newyork-market-watch": "🌆", 
            "kospi-close": "📈"
        }
        emoji = type_emojis.get(news_type, "📰")
        type_display = news_type.replace("-", " ").upper()

        # 변경 항목 분석
        changed_fields = []
        field_names = [
            ("title", "제목"),
            ("content", "본문"),
            ("date", "날짜"),
            ("time", "시간")
        ]
        if not old_data or not any(old_data.get(f) for f, _ in field_names):
            change_type = "🆕 신규입력"
            change_icon = "🆕"
            changed_fields = [n for _, n in field_names if new_data.get(_)]
        else:
            for f, n in field_names:
                if old_data.get(f) != new_data.get(f):
                    changed_fields.append(n)
            if changed_fields:
                change_type = f"{', '.join(changed_fields)} 변경"
                change_icon = "📝"
            else:
                change_type = "⏰ 시간 업데이트"
                change_icon = "⏰"

        message = f"{change_icon} {type_display} 업데이트\n"
        message += f"┌ 변경: {change_type}\n"

        # 최신 데이터 정보
        new_datetime = self._format_datetime(new_data.get('date', ''), new_data.get('time', ''))
        message += f"├ 시간: {new_datetime}\n"

        # 제목 정보
        new_title = new_data.get('title', '')
        if new_title:
            title_preview = new_title[:60] + "..." if len(new_title) > 60 else new_title
            message += f"├ 제목: {title_preview}\n"

        # 작성자 및 카테고리
        writers = new_data.get('writer', [])
        categories = new_data.get('category', [])
        if writers:
            message += f"├ 작성자: {', '.join(writers)}\n"
        if categories:
            message += f"└ 카테고리: {', '.join(categories[:3])}{'...' if len(categories) > 3 else ''}"
        else:
            if writers:
                message = message.rstrip('\n├ 작성자: ' + ', '.join(writers) + '\n') + f"└ 작성자: {', '.join(writers)}"
            else:
                message = message.rstrip('\n')

        payload = {
            "botName": "POSCO 뉴스 🔔",
            "botIconImage": self.bot_profile_image_url,
            "text": f"{change_icon} {type_display} 업데이트",
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
                print(f"✅ {news_type} 알림 전송 성공")
                return True
        except Exception as e:
            print(f"❌ {news_type} 알림 전송 오류: {e}")
        
        return False
    
    def send_simple_status_notification(self, current_data, status_info):
        """
        간결한 상태 알림 전송
        
        봇 이름에 상태 정보를 포함하고 "갱신 데이터 없음" 메시지만
        전송하는 간결한 형태의 알림입니다.
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            status_info (str): 상태 정보 문자열
        """
        bot_name = f"POSCO 뉴스{status_info}"
        payload = {
            "botName": bot_name,
            "botIconImage": self.bot_profile_image_url,
            "text": "갱신 데이터 없음",
            "attachments": []
        }
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ 간결 상태 알림 전송 성공")
                return True
        except Exception as e:
            print(f"❌ 간결 상태 알림 전송 오류: {e}")
        
        return False

    def send_monitoring_stopped_notification(self):
        """
        모니터링 중지 오류 알림 전송
        
        자동 모니터링 프로세스가 예기치 않게 중단되었을 때
        빨간색 오류 알림을 전송합니다.
        """
        payload = {
            "botName": "POSCO 뉴스 ❌",
            "botIconImage": self.bot_profile_image_url,
            "text": "❌ 오류",
            "attachments": [
                {
                    "color": "#ff4444",
                    "text": "자동 모니터링 프로세스 중지됨"
                }
            ]
        }
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ 모니터링 중단 알림 전송 성공")
                return True
        except Exception as e:
            print(f"❌ 모니터링 중단 알림 전송 오류: {e}")
        
        return False
    
    def send_comparison_notification(self, current_data, previous_data):
        """
        영업일 비교 알림 전송
        
        현재 데이터와 직전 영업일 데이터를 비교하여
        상세한 비교 결과를 Dooray로 전송합니다.
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            previous_data (dict): 직전 영업일 뉴스 데이터
        """
        message = "📊 영업일 비교 분석\n\n"
        
        if current_data and previous_data:
            today_kr = datetime.now().strftime('%Y%m%d')
            
            for news_type, current_news in current_data.items():
                news_config = NEWS_TYPES.get(news_type, {"display_name": news_type.upper(), "emoji": "📰"})
                emoji = news_config["emoji"]
                type_display = news_config["display_name"]
                
                previous_news = previous_data.get(news_type, {})
                
                message += f"┌ {emoji} {type_display}\n"
                
                # 현재 데이터
                current_date = current_news.get('date', '')
                current_time = current_news.get('time', '')
                current_title = current_news.get('title', '')
                
                if current_date and current_time:
                    current_datetime = self._format_datetime(current_date, current_time)
                    message += f"├ 현재: {current_datetime}\n"
                    if current_title:
                        title_preview = current_title[:40] + "..." if len(current_title) > 40 else current_title
                        message += f"├ 제목: {title_preview}\n"
                
                # 직전 데이터
                previous_date = previous_news.get('date', '')
                previous_time = previous_news.get('time', '')
                previous_title = previous_news.get('title', '')
                
                if previous_date and previous_time:
                    previous_datetime = self._format_datetime(previous_date, previous_time)
                    message += f"├ 직전: {previous_datetime}\n"
                    if previous_title:
                        title_preview = previous_title[:40] + "..." if len(previous_title) > 40 else previous_title
                        message += f"└ 제목: {title_preview}\n"
                else:
                    message += f"└ 직전: 데이터 없음\n"
                
                message += "\n"
        
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"분석 시간: {current_datetime}"
        
        payload = {
            "botName": "POSCO 뉴스 📊",
            "botIconImage": self.bot_profile_image_url,
            "text": "영업일 비교 분석 완료",
            "attachments": [{
                "color": "#17a2b8",
                "text": message
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
                print(f"✅ 비교 분석 알림 전송 성공")
                return True
        except Exception as e:
            print(f"❌ 비교 분석 알림 전송 오류: {e}")
        
        return False
    
    def _format_datetime(self, date_str, time_str):
        """
        날짜와 시간을 포맷팅
        
        Args:
            date_str (str): 날짜 문자열 (YYYYMMDD)
            time_str (str): 시간 문자열 (HHMMSS)
            
        Returns:
            str: 포맷팅된 날짜시간 문자열
        """
        if not date_str:
            return "날짜 없음"
        
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        if not time_str:
            return formatted_date
        
        if len(time_str) >= 6:
            formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
        elif len(time_str) == 5:
            if time_str.startswith('6'):
                time_str = '0' + time_str
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            else:
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:5]}"
        elif len(time_str) >= 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:4]}"
        else:
            formatted_time = time_str
        
        return f"{formatted_date} {formatted_time}"