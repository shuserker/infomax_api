# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 핵심 모니터링 로직

주요 기능:
- 스마트 모니터링: 뉴스 발행 패턴 기반 적응형 간격 모니터링
- 현재 상태 체크: 실시간 뉴스 상태 확인 및 알림
- 영업일 비교: 현재 vs 직전 영업일 데이터 상세 비교
- 일일 요약: 오늘 발행 뉴스 + 직전 데이터 비교 요약
- 야간 조용한 모드: 변경사항 있을 때만 알림으로 수면 방해 없음

작성자: AI Assistant
최종 수정: 2025-07-27
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import time
import hashlib
from datetime import datetime, timedelta
import os

from config import API_CONFIG, MONITORING_CONFIG, STATUS_CONFIG, NEWS_TYPES, BOT_PROFILE_IMAGE_URL


class PoscoNewsMonitor:
    """
    POSCO 뉴스 모니터링 시스템 메인 클래스
    
    뉴스 발행 패턴을 분석하여 적응형 간격으로 모니터링하고,
    변경사항을 Dooray로 실시간 알림하는 시스템입니다.
    
    주요 모니터링 모드:
    - 스마트 모니터링: 시간대별 적응형 간격 (추천)
    - 현재 상태 체크: 일회성 상태 확인
    - 영업일 비교: 상세 데이터 비교 분석
    - 일일 요약: 하루 뉴스 요약 리포트
    """
    
    def __init__(self, dooray_webhook_url):
        """
        모니터링 시스템 초기화
        
        Args:
            dooray_webhook_url (str): Dooray 웹훅 URL
        """
        self.api_url = API_CONFIG["url"]
        self.api_user = API_CONFIG["user"]
        self.api_pwd = API_CONFIG["password"]
        self.api_timeout = API_CONFIG["timeout"]
        self.dooray_webhook = dooray_webhook_url
        self.last_hash = None
        self.cache_file = MONITORING_CONFIG["cache_file"]
        self.max_retry_days = MONITORING_CONFIG["max_retry_days"]
    
    def _get_today_info(self):
        """
        오늘 날짜 정보 캐싱 (성능 최적화)
        
        Returns:
            dict: 오늘 날짜 정보 (kr_format, weekday, weekday_name 등)
        """
        if not hasattr(self, '_today_cache') or self._today_cache['date'] != datetime.now().date():
            now = datetime.now()
            self._today_cache = {
                'date': now.date(),
                'kr_format': now.strftime('%Y%m%d'),
                'weekday': now.weekday(),
                'weekday_name': ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
            }
        return self._today_cache
    
    def _get_status_info(self, current_data):
        """
        상태 정보 계산 (요일별 예상 뉴스 수 고려)
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            
        Returns:
            str: 상태 표시 문자열 (예: " 🟢1 of 1", " 🔵휴일")
        """
        if not current_data:
            return " 🔴데이터 없음"
            
        today_info = self._get_today_info()
        today_kr = today_info['kr_format']
        today_weekday = today_info['weekday']
        
        # 오늘 발행된 뉴스 수
        today_count = 0
        expected_today = 0
        
        for news_type, news_data in current_data.items():
            # 오늘 발행 여부 확인
            if news_data.get('date') == today_kr:
                today_count += 1
            
            # 오늘 요일에 발행 예상 여부 확인
            news_config = NEWS_TYPES.get(news_type, {})
            if today_weekday in news_config.get('publish_days', []):
                expected_today += 1
        
        colors = STATUS_CONFIG["colors"]
        
        # 예상 뉴스 수 기준으로 상태 판단 (간결한 표기)
        if today_count == expected_today and expected_today > 0:
            return f" {colors['all_latest']}{today_count} of {expected_today}"
        elif today_count > 0:
            return f" {colors['partial_latest']}{today_count} of {expected_today}"
        else:
            if expected_today == 0:
                return f" 🔵휴일"
            else:
                return f" {colors['all_old']}{expected_today}개 대기"
    
    def _get_status_emoji(self, current_data):
        """
        현재 데이터 상태에 따른 이모지 반환
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            
        Returns:
            str: 상태 이모지 (🟢/🟡/🔴)
        """
        if not current_data:
            return STATUS_CONFIG["colors"]["all_old"]
            
        today_kr = datetime.now().strftime('%Y%m%d')
        status_count = sum(1 for _, news_data in current_data.items() 
                         if news_data.get('date') == today_kr)
        total_count = len(current_data)
    
    def get_expected_news_count_today(self):
        """
        오늘 요일에 예상되는 뉴스 수 계산
        
        NEWS_TYPES 설정의 publish_days를 기반으로 
        오늘 요일에 발행 예상되는 뉴스 개수를 계산합니다.
        
        Returns:
            int: 예상 뉴스 개수
        """
        today_info = self._get_today_info()
        expected_count = 0
        
        for news_type, config in NEWS_TYPES.items():
            if today_info['weekday'] in config.get('publish_days', []):
                expected_count += 1
        
        return expected_count
    
    def get_weekday_display(self):
        """
        현재 요일을 한글로 반환
        
        Returns:
            str: 요일 문자열 ('월', '화', '수', '목', '금', '토', '일')
        """
        return self._get_today_info()['weekday_name']
        
        colors = STATUS_CONFIG["colors"]
        
        if status_count == total_count and total_count > 0:
            return colors["all_latest"]
        elif status_count > 0:
            return colors["partial_latest"]
        else:
            return colors["all_old"]

    def format_datetime(self, date_str, time_str):
        """
        API 날짜/시간 문자열을 읽기 쉬운 형태로 변환
        
        Args:
            date_str (str): 날짜 문자열 (YYYYMMDD 형식)
            time_str (str): 시간 문자열 (HHMMSS 또는 변형 형식)
            
        Returns:
            str: 포맷된 날짜시간 문자열 (YYYY-MM-DD HH:MM:SS)
                 데이터가 없거나 오류 시 적절한 메시지 반환
        """
        if not date_str or not time_str:
            return "데이터 없음"
            
        try:
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            if len(time_str) >= 6:
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            elif len(time_str) == 5:
                if time_str.startswith('6'):
                    time_str = '0' + time_str
                    formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                else:
                    formatted_time = f"0{time_str[:1]}:{time_str[1:3]}:{time_str[3:5]}"
            elif len(time_str) == 4:
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:00"
            else:
                formatted_time = time_str
            
            return f"{formatted_date} {formatted_time}"
        except:
            return "데이터 오류"
        
    def get_news_data(self, date=None):
        """
        POSCO 뉴스 API에서 데이터 조회
        
        Args:
            date (str, optional): 조회할 날짜 (YYYYMMDD 형식)
                                 None이면 최신 데이터 조회
        
        Returns:
            dict: 뉴스 타입별 데이터 딕셔너리
                  API 호출 실패 시 None 반환
        """
        try:
            params = {}
            if date:
                params['date'] = date
                
            resp = requests.get(
                self.api_url,
                auth=HTTPBasicAuth(self.api_user, self.api_pwd),
                params=params,
                timeout=self.api_timeout
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ API 호출 오류: {e}")
            return None
    
    def get_data_hash(self, data):
        """
        데이터의 MD5 해시값 계산 (변경사항 감지용)
        
        Args:
            data (dict): 해시값을 계산할 데이터
            
        Returns:
            str: MD5 해시값 (32자리 16진수)
                 데이터가 None이면 None 반환
        """
        if not data:
            return None
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def load_cache(self):
        """
        캐시 파일에서 이전 데이터 로드
        
        Returns:
            dict: 캐시된 뉴스 데이터
                  캐시 파일이 없거나 읽기 실패 시 None 반환
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    self.last_hash = cache.get('last_hash')
                    return cache.get('data')
            except:
                pass
        return None
    
    def save_cache(self, data, data_hash):
        """
        현재 데이터를 캐시 파일에 저장
        
        Args:
            data (dict): 저장할 뉴스 데이터
            data_hash (str): 데이터의 해시값
        """
        cache = {
            'last_hash': data_hash,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    
    def send_dooray_notification(self, message, is_error=False):
        """
        Dooray 웹훅으로 알림 메시지 전송
        
        Args:
            message (str): 전송할 메시지 내용
            is_error (bool): 오류 알림 여부 (색상 및 제목 변경)
        """
        try:
            color = "#ff4444" if is_error else "#0066cc"
            title = "⚠️ 오류 알림" if is_error else "🔔 POSCO 뉴스 알림"
            
            bot_name = "POSCO 뉴스 ❌" if is_error else "POSCO 뉴스 🔔"
            preview_text = message.split('\n')[0] if '\n' in message else message[:50]
            
            lines = message.split('\n')
            detail_message = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": preview_text,
                "attachments": [{
                    "color": color,
                    "text": detail_message
                }]
            }
            
            response = requests.post(
                self.dooray_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Dooray 알림 전송 성공: {datetime.now()}")
            else:
                print(f"❌ Dooray 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Dooray 웹훅 오류: {e}")
    
    def send_status_notification(self, current_data):
        """
        현재 상태 상세 알림 전송
        
        각 뉴스 타입별 상태, 발행 시간, 제목 미리보기 등을
        포함한 상세한 상태 정보를 Dooray로 전송합니다.
        
        Args:
            current_data (dict): 현재 뉴스 데이터
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
                weekday_name = self.get_weekday_display()
                
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
                        status = "�"
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
                                formatted_time = f"0{news_time[:1]}:{news_time[1:3]}:{news_time[3:5]}"
                        elif len(news_time) == 4:
                            formatted_time = f"{news_time[:2]}:{news_time[2:4]}:00"
                        else:
                            formatted_time = news_time
                    else:
                        formatted_time = ""
                    
                    formatted_date = f"{news_date[:4]}-{news_date[4:6]}-{news_date[6:8]}"
                    date_time_display = f"{formatted_date}  ·  {formatted_time}" if formatted_time else formatted_date
                
                # 제목 미리보기 (있는 경우만)
                title_preview = ""
                if news_title:
                    title_preview = f"\n제목: {news_title[:45]}{'...' if len(news_title) > 45 else ''}"
                
                news_items.append(f"{status} {type_display} ({status_text})\n📅 시간: {date_time_display}{title_preview}")
            
            # 각 뉴스 항목을 구분선으로 분리
            for i, item in enumerate(news_items):
                message += f"{item}\n"
                if i < len(news_items) - 1:  # 마지막 항목이 아니면 구분선 추가
                    message += "━━━━━━━━━━━━━━━━━━━━━\n"
        
        current_datetime = datetime.now().strftime('%Y-%m-%d  ·  %H:%M:%S')
        message += f"\n최종 확인: {current_datetime}"
        
        preview_info = self._get_status_info(current_data)
        
        payload = {
            "botName": f"POSCO 뉴스{preview_info}",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": "데이터 갱신 없음",
            "attachments": [{
                "color": "#28a745",
                "text": message.replace("📊 갱신 정보:\n", "")
            }]
        }
        
        try:
            response = requests.post(
                self.dooray_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ 상태 정상 알림 전송 성공")
        except Exception as e:
            print(f"❌ 상태 알림 전송 오류: {e}")
    
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
            "exchange-rate": "",
            "newyork-market-watch": "", 
            "kospi-close": ""
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
        new_datetime = self.format_datetime(new_data.get('date', ''), new_data.get('time', ''))
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
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": f"{change_icon} {type_display} 업데이트",
            "attachments": [{
                "color": "#0066cc",
                "text": message.split('\n', 1)[1] if '\n' in message else message
            }]
        }
        try:
            response = requests.post(
                self.dooray_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ {news_type} 알림 전송 성공")
        except Exception as e:
            print(f"❌ {news_type} 알림 전송 오류: {e}")
    
    def detect_changes(self, old_data, new_data):
        """
        이전 데이터와 현재 데이터 간의 변경사항 감지
        
        Args:
            old_data (dict): 이전 뉴스 데이터
            new_data (dict): 현재 뉴스 데이터
            
        Returns:
            dict: 변경사항 정보
                  - type: "new", "update", "none"
                  - changes: 변경된 뉴스 타입 리스트
        """
        if not old_data:
            return {"type": "new", "changes": []}
        
        changes = []
        for news_type in new_data:
            if news_type not in old_data:
                changes.append(news_type)
            else:
                old_item = old_data[news_type]
                new_item = new_data[news_type]
                
                if (old_item.get('title') != new_item.get('title') or 
                    old_item.get('content') != new_item.get('content') or
                    old_item.get('date') != new_item.get('date') or 
                    old_item.get('time') != new_item.get('time')):
                    changes.append(news_type)
        
        return {
            "type": "update" if changes else "none",
            "changes": changes
        }
    
    def send_simple_status_notification(self, current_data):
        """
        간결한 상태 알림 전송
        
        봇 이름에 상태 정보를 포함하고 "갱신 데이터 없음" 메시지만
        전송하는 간결한 형태의 알림입니다.
        
        Args:
            current_data (dict): 현재 뉴스 데이터
        """
        status_info = self._get_status_info(current_data)
        bot_name = f"POSCO 뉴스{status_info}"
        payload = {
            "botName": bot_name,
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": "갱신 데이터 없음",
            "attachments": []
        }
        try:
            response = requests.post(
                self.dooray_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ 간결 상태 알림 전송 성공")
        except Exception as e:
            print(f"❌ 간결 상태 알림 전송 오류: {e}")

    def send_monitoring_stopped_notification(self):
        """
        모니터링 중지 오류 알림 전송
        
        자동 모니터링 프로세스가 예기치 않게 중단되었을 때
        빨간색 오류 알림을 전송합니다.
        """
        payload = {
            "botName": "POSCO 뉴스 ❌",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
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
                self.dooray_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ 모니터링 중단 알림 전송 성공")
        except Exception as e:
            print(f"❌ 모니터링 중단 알림 전송 오류: {e}")

    def check_once(self, simple_status=False):
        """
        일회성 뉴스 상태 체크
        
        현재 뉴스 상태를 확인하고 변경사항이 있으면 변경 알림을,
        없으면 상태 알림을 전송합니다.
        
        Args:
            simple_status (bool): True면 간결한 상태 알림 전송
            
        Returns:
            bool: 변경사항 발견 여부
        """
        print(f"🔍 뉴스 데이터 체크 중... {datetime.now()}")
        current_data = self.get_news_data()
        if not current_data:
            self.send_dooray_notification("API 호출 실패", is_error=True)
            return False
        current_hash = self.get_data_hash(current_data)
        cached_data = self.load_cache()
        if self.last_hash != current_hash:
            print("📢 데이터 변경 감지!")
            change_result = self.detect_changes(cached_data, current_data)
            if change_result["changes"]:
                for news_type in change_result["changes"]:
                    old_item = cached_data.get(news_type) if cached_data else None
                    new_item = current_data[news_type]
                    self.send_change_notification(news_type, old_item, new_item)
            self.save_cache(current_data, current_hash)
            self.last_hash = current_hash
            return True
        else:
            print("📝 변경사항 없음")
            if simple_status:
                self.send_simple_status_notification(current_data)
            else:
                self.send_status_notification(current_data)
            return False
    
    def check_silent(self):
        """
        조용한 모드 체크 - 변경사항 있을 때만 알림 전송
        
        야간 시간대나 휴무일에 사용하여 불필요한 알림을 방지합니다.
        변경사항이 없으면 콘솔 로그만 출력하고 알림은 전송하지 않습니다.
        
        Returns:
            bool: 변경사항 발견 여부
        """
        print(f"🔍 뉴스 데이터 체크 중... {datetime.now()}")
        
        current_data = self.get_news_data()
        if not current_data:
            # API 오류도 야간에는 조용히 처리
            print("❌ API 호출 실패 (야간 모드 - 알림 없음)")
            return False
        
        current_hash = self.get_data_hash(current_data)
        cached_data = self.load_cache()
        
        if self.last_hash != current_hash:
            print("📢 데이터 변경 감지! (야간에도 알림 전송)")
            
            change_result = self.detect_changes(cached_data, current_data)
            
            if change_result["changes"]:
                for news_type in change_result["changes"]:
                    old_item = cached_data.get(news_type) if cached_data else None
                    new_item = current_data[news_type]
                    self.send_change_notification(news_type, old_item, new_item)
            
            self.save_cache(current_data, current_hash)
            self.last_hash = current_hash
            return True
        else:
            print("📝 변경사항 없음 - 야간 모드로 알림 없음")
            return False
    
    def get_previous_day_data(self, current_data):
        """
        직전 영업일 데이터 조회 (캐시 활용)
        
        현재 데이터와 실제로 다른 내용을 가진 직전 영업일 데이터를
        최대 10일 전까지 역순으로 검색하여 반환합니다.
        
        Args:
            current_data (dict): 현재 뉴스 데이터
            
        Returns:
            dict: 뉴스 타입별 직전 영업일 데이터
                  찾지 못한 경우 해당 타입은 None
        """
        previous_data = {}
        cached_data = self.load_cache()
        
        for news_type, news_data in current_data.items():
            current_date = news_data.get('date', '')
            current_title = news_data.get('title', '')
            
            # 현재 데이터가 비어있으면 캐시에서 최근 데이터를 가져와서 사용
            if not current_date or not current_title:
                if cached_data and news_type in cached_data:
                    cached_item = cached_data[news_type]
                    if cached_item.get('date') and cached_item.get('title'):
                        print(f"📅 {news_type}: 현재 데이터 없음, 캐시에서 최근 데이터 사용")
                        current_date = cached_item['date']
                        current_title = cached_item['title']
                    else:
                        print(f"📅 {news_type}: 현재 데이터와 캐시 모두 비어있음, 최근 데이터 직접 조회")
                        # 최근 5일간 데이터를 조회해서 가장 최근 데이터 찾기
                        for days_back in range(0, 6):
                            try:
                                check_date_obj = datetime.now() - timedelta(days=days_back)
                                check_date = check_date_obj.strftime("%Y%m%d")
                                recent_data = self.get_news_data(date=check_date)
                                if recent_data and news_type in recent_data:
                                    recent_item = recent_data[news_type]
                                    if recent_item.get('title') and recent_item.get('date'):
                                        current_date = recent_item['date']
                                        current_title = recent_item['title']
                                        print(f"📅 {news_type}: {days_back}일 전({check_date}) 데이터 발견")
                                        break
                            except Exception as e:
                                continue
                        
                        if not current_date or not current_title:
                            print(f"📅 {news_type}: 최근 5일 내 데이터 없음")
                            previous_data[news_type] = None
                            continue
                else:
                    print(f"📅 {news_type}: 현재 데이터 없고 캐시도 없음, 최근 데이터 직접 조회")
                    # 최근 5일간 데이터를 조회해서 가장 최근 데이터 찾기
                    for days_back in range(0, 6):
                        try:
                            check_date_obj = datetime.now() - timedelta(days=days_back)
                            check_date = check_date_obj.strftime("%Y%m%d")
                            recent_data = self.get_news_data(date=check_date)
                            if recent_data and news_type in recent_data:
                                recent_item = recent_data[news_type]
                                if recent_item.get('title') and recent_item.get('date'):
                                    current_date = recent_item['date']
                                    current_title = recent_item['title']
                                    print(f"📅 {news_type}: {days_back}일 전({check_date}) 데이터 발견")
                                    break
                        except Exception as e:
                            continue
                    
                    if not current_date or not current_title:
                        print(f"📅 {news_type}: 최근 5일 내 데이터 없음")
                        previous_data[news_type] = None
                        continue
            
            print(f"📅 {news_type}: 직전 영업일 데이터 검색 중...")
            
            # 최대 설정된 일수까지 역순으로 검색하여 다른 데이터 찾기
            found_different_data = False
            for days_back in range(1, self.max_retry_days + 1):
                try:
                    # N일 전 날짜 계산
                    check_date_obj = datetime.strptime(current_date, "%Y%m%d") - timedelta(days=days_back)
                    check_date = check_date_obj.strftime("%Y%m%d")
                    
                    # API에서 해당 날짜 데이터 조회
                    prev_api_data = self.get_news_data(date=check_date)
                    
                    if prev_api_data and news_type in prev_api_data:
                        prev_item = prev_api_data[news_type]
                        prev_title = prev_item.get('title', '')
                        prev_date = prev_item.get('date', '')
                        
                        print(f"📅 {news_type}: {days_back}일 전({check_date}) 조회 - 제목: {prev_title[:30]}{'...' if len(prev_title) > 30 else ''}")
                        
                        # 빈 데이터가 아니고 (제목이 다르거나 날짜가 다르면) 실제 다른 데이터로 판단
                        if prev_title and (prev_title != current_title or prev_date != current_date):
                            previous_data[news_type] = prev_item
                            print(f"📅 {news_type}: 직전 데이터 발견 ({days_back}일 전)")
                            found_different_data = True
                            break
                        
                except Exception as e:
                    print(f"❌ {news_type}: {days_back}일 전 데이터 조회 오류 - {e}")
                    continue
            
            if not found_different_data:
                print(f"📅 {news_type}: 10일 내 직전 데이터를 찾을 수 없음")
                previous_data[news_type] = None
        
        return previous_data
    
    def send_comparison_notification(self, current_data):
        """
        현재 vs 직전 영업일 데이터 비교 알림 전송
        
        요일별 발행 패턴을 고려하여 현재 데이터와 직전 영업일 데이터를
        상세 비교한 결과를 Dooray로 전송합니다.
        주말의 경우 별도의 현황 알림을 전송합니다.
        
        Args:
            current_data (dict): 현재 뉴스 데이터
        """
        today_weekday = datetime.now().weekday()
        weekday_name = self.get_weekday_display()
        expected_today = self.get_expected_news_count_today()
        
        # 주말이거나 예상 뉴스가 적은 경우 다른 방식으로 처리
        if expected_today <= 1:  # 토요일, 일요일 등
            message = f"📊 {weekday_name}요일 뉴스 현황\n"
            message += f"🎯 {weekday_name}요일 예상 뉴스: {expected_today}개\n\n"
            
            today_kr = datetime.now().strftime('%Y%m%d')
            news_items = []
            
            for news_type, news_data in current_data.items():
                news_config = NEWS_TYPES.get(news_type, {"display_name": news_type.upper()})
                type_display = news_config["display_name"]
                publish_days = news_config.get('publish_days', [])
                
                news_date = news_data.get('date', '')
                news_time = news_data.get('time', '')
                news_title = news_data.get('title', '')
                
                if today_weekday in publish_days:
                    # 오늘 발행 예상 뉴스
                    if news_date == today_kr and news_title:
                        status = "🟢"
                        status_text = "오늘 발행"
                        time_display = self.format_datetime(news_date, news_time)
                        title_preview = f"\n제목: {news_title[:50]}{'...' if len(news_title) > 50 else ''}"
                    else:
                        status = "🔴"
                        status_text = "미발행"
                        time_display = "대기 중"
                        title_preview = ""
                else:
                    # 오늘 휴무 뉴스
                    status = "⏸️"
                    status_text = f"{weekday_name}요일 휴무"
                    time_display = "미발행"
                    title_preview = ""
                
                news_items.append(f"{status} {type_display} ({status_text})\n📅 {time_display}{title_preview}")
            
            # 각 뉴스 항목을 구분선으로 분리
            for i, item in enumerate(news_items):
                message += f"{item}\n"
                if i < len(news_items) - 1:
                    message += "━━━━━━━━━━━━━━━━━━━━━\n"
            
            current_datetime = datetime.now().strftime('%Y-%m-%d  ·  %H:%M:%S')
            message += f"\n최종 확인: {current_datetime}"
            
            # 주말용 알림 전송
            status_info = self._get_status_info(current_data)
            payload = {
                "botName": f"POSCO 뉴스{status_info}",
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "attachments": [{
                    "color": "#17a2b8",
                    "text": message
                }]
            }
            
            try:
                response = requests.post(
                    self.dooray_webhook,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ 주말 뉴스 현황 알림 전송 성공")
            except Exception as e:
                print(f"❌ 주말 뉴스 현황 알림 전송 오류: {e}")
            
            return
        
        # 평일인 경우 기존 영업일 비교 로직 실행
        previous_data = self.get_previous_day_data(current_data)
        
        message = "📊 현재 vs 직전 영업일 데이터 비교\n"
        comparison_items = []
        
        # 뉴스 타입별 이모지 매핑
        type_emojis = {
            "exchange-rate": "",
            "newyork-market-watch": "", 
            "kospi-close": ""
        }
        
        cached_data = self.load_cache()
        
        for news_type, current_news in current_data.items():
            emoji = type_emojis.get(news_type, "📰")
            type_display = news_type.replace("-", " ").upper()
            
            # 현재 데이터 상태 확인
            current_date = current_news.get('date', '')
            current_time = current_news.get('time', '')
            current_title = current_news.get('title', '')
            
            # 현재 데이터가 비어있으면 캐시에서 가져오기
            if not current_date or not current_title:
                if cached_data and news_type in cached_data:
                    cached_item = cached_data[news_type]
                    if cached_item.get('date') and cached_item.get('title'):
                        current_date = cached_item['date']
                        current_time = cached_item['time']
                        current_title = cached_item['title']
                        status_icon = "🟡"
                        current_status = "캐시 데이터"
                        current_display = f"{self.format_datetime(current_date, current_time)} (캐시)"
                    else:
                        status_icon = "🔴"
                        current_status = "데이터 없음"
                        current_display = "데이터 없음"
                else:
                    status_icon = "🔴"
                    current_status = "데이터 없음"
                    current_display = "데이터 없음"
            else:
                today_kr = datetime.now().strftime('%Y%m%d')
                status_icon = "🟢" if current_date == today_kr else "🟡"
                current_status = "최신" if current_date == today_kr else "과거"
                current_display = self.format_datetime(current_date, current_time)
            
            item_message = f"{status_icon} {type_display}\n"
            item_message += f"📅 현재: {current_display}\n"
            
            if current_title:
                # 제목을 적절한 길이로 자르기 (더 여유있게)
                title_preview = current_title[:50] + "..." if len(current_title) > 50 else current_title
                item_message += f"📰 현재 제목: {title_preview}\n\n"
            else:
                item_message += "\n"
            
            # 직전 영업일 데이터
            if previous_data.get(news_type):
                prev_news = previous_data[news_type]
                prev_date = prev_news.get('date', '')
                prev_time = prev_news.get('time', '')
                prev_title = prev_news.get('title', '')
                
                prev_display = self.format_datetime(prev_date, prev_time)
                
                # 날짜 차이 계산
                try:
                    current_date_obj = datetime.strptime(current_date, "%Y%m%d")
                    prev_date_obj = datetime.strptime(prev_date, "%Y%m%d")
                    days_diff = (current_date_obj - prev_date_obj).days
                    gap_text = f"{days_diff}일 전"
                except:
                    gap_text = "날짜 불명"
                
                item_message += f"📅 직전: {prev_display} ({gap_text})\n"
                
                if prev_title:
                    prev_title_preview = prev_title[:50] + "..." if len(prev_title) > 50 else prev_title
                    item_message += f"📰 직전 제목: {prev_title_preview}\n\n"
                
                # 변경사항 분석 (더 적절한 메시지로)
                if current_title and prev_title:
                    if current_title != prev_title:
                        item_message += "📝 새로운 뉴스로 업데이트됨"
                    elif current_time != prev_time:
                        item_message += "⏰ 동일 뉴스, 시간만 갱신됨"
                    else:
                        item_message += "✅ 이전과 동일한 뉴스"
                else:
                    item_message += "❓ 비교 데이터 부족"
            else:
                item_message += f"📅 직전: 데이터 없음\n\n"
                item_message += "ℹ️ 10일 내 이전 데이터를 찾을 수 없습니다"
            
            comparison_items.append(item_message)
        
        # 각 뉴스 타입을 구분선으로 분리 (더 깔끔한 구분선)
        for i, item in enumerate(comparison_items):
            message += f"{item}\n"
            if i < len(comparison_items) - 1:  # 마지막 항목이 아니면 구분선 추가
                message += "━━━━━━━━━━━━━━━━━━━━━\n"
        
        payload = {
            "botName": "POSCO 뉴스 📊",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": "현재 vs 직전 영업일 데이터 비교",
            "attachments": [{
                "color": "#6f42c1",
                "text": message.replace("📊 현재 vs 직전 영업일 데이터 비교\n", "")
            }]
        }
        
        try:
            response = requests.post(
                self.dooray_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ 비교 데이터 알림 전송 성공")
        except Exception as e:
            print(f"❌ 비교 데이터 알림 전송 오류: {e}")
    
    def check_extended(self):
        """
        영업일 비교 체크 - 현재 vs 직전 영업일 데이터 상세 비교
        
        평일에는 상세 비교를, 주말에는 해당 요일 뉴스 현황을 표시합니다.
        스마트 모니터링에서 매일 08:00에 자동 실행됩니다.
        
        Returns:
            bool: 성공 여부
        """
        print(f"🔍 확장 뉴스 데이터 체크 중... {datetime.now()}")
        
        current_data = self.get_news_data()
        if not current_data:
            self.send_dooray_notification("API 호출 실패", is_error=True)
            return False
        
        current_hash = self.get_data_hash(current_data)
        cached_data = self.load_cache()
        
        if self.last_hash != current_hash:
            print("📢 데이터 변경 감지!")
            
            change_result = self.detect_changes(cached_data, current_data)
            
            if change_result["changes"]:
                for news_type in change_result["changes"]:
                    old_item = cached_data.get(news_type) if cached_data else None
                    new_item = current_data[news_type]
                    self.send_change_notification(news_type, old_item, new_item)
            
            self.save_cache(current_data, current_hash)
            self.last_hash = current_hash
        else:
            print("📝 변경사항 없음 - 현재 상태 상세 표시")
            # 변경사항이 없어도 현재 vs 직전 영업일 비교 표시
            self.send_comparison_notification(current_data)
        
        return True
    
    def get_smart_interval(self, current_hour):
        """
        시간대별 스마트 모니터링 간격 계산
        
        뉴스 발행 패턴을 분석하여 시간대별로 최적화된 모니터링 간격을 제공합니다.
        
        Args:
            current_hour (int): 현재 시간 (0-23)
            
        Returns:
            int: 모니터링 간격 (분 단위)
                - 집중시간 (06:00-08:00, 15:00-17:00): 20분
                - 일반시간 (07:00-18:00): 2시간 (120분)
                - 야간시간 (18:00-07:00): 4시간 (240분)
                - 완전휴무 (일요일): 4시간 (240분)
        """
        today_weekday = datetime.now().weekday()
        expected_today = self.get_expected_news_count_today()
        
        # 완전 휴무일 (일요일)
        if expected_today == 0:
            return 240  # 4시간 간격 (거의 대기 모드)
        
        # 뉴스 발행 집중 시간대
        if 6 <= current_hour <= 8:    # Exchange-rate 발행 시간 (평일만)
            if today_weekday < 5:  # 월-금
                return 20  # 20분 간격
            else:
                return 120  # 주말은 2시간
        elif 15 <= current_hour <= 17:  # Kospi-close, Newyork-market-watch 발행 시간
            return 20  # 20분 간격
        # 일반 업무 시간
        elif 7 <= current_hour <= 18:   
            return 120  # 2시간 간격
        else:
            return 240  # 4시간 간격 (야간)

    def start_smart_monitoring(self):
        """
        스마트 모니터링 시작 - 모든 기능을 통합한 완전 자동화 모니터링
        
        주요 기능:
        - 시간대별 적응형 간격 모니터링 (현재 상태 체크)
        - 매일 08:00 영업일 비교 리포트 자동 발송
        - 매일 18:00 일일 요약 리포트 자동 발송
        - 야간 조용한 모드 (변경사항 있을 때만 알림)
        
        모니터링 패턴:
        - 집중시간: 06:00-08:00, 15:00-17:00 (20분 간격)
        - 일반시간: 07:00-18:00 (2시간 간격)
        - 야간시간: 18:00-07:00 (조용한 모드)
        
        중단: Ctrl+C
        """
        import pytz
        KST = pytz.timezone('Asia/Seoul')
        
        print("🧠 POSCO 뉴스 스마트 모니터링 시작")
        print("📅 운영 시간: 07:00-18:00 (뉴스 발행 패턴 기반)")
        print("⚡ 집중 모니터링: 06:00-08:00, 15:00-17:00 (20분 간격)")
        print("📊 일반 모니터링: 07:00-18:00 (2시간 간격)")
        print("💤 야간 조용한 모드: 18:00-07:00 (변경사항 있을 때만 알림)")
        
        self.load_cache()
        self.send_dooray_notification(
            "🧠 POSCO 뉴스 스마트 모니터링 시작\n뉴스 발행 패턴 기반 적응형 간격"
        )
        
        last_daily_summary = None
        last_comparison_sent = None
        
        try:
            while True:
                now_kst = datetime.now(KST)
                hour = now_kst.hour
                minute = now_kst.minute
                
                # 현재 시간대에 맞는 간격 계산
                current_interval = self.get_smart_interval(hour)
                
                # 운영 시간대 체크 (07:00-18:00)
                if 7 <= hour <= 18:
                    print(f"🔍 [{hour:02d}:{minute:02d}] 모니터링 실행 (다음: {current_interval}분 후)")
                    
                    # 기본 체크
                    self.check_once()
                    
                    # 특별 이벤트 처리
                    key = f"{now_kst.strftime('%Y%m%d')}-{hour}"
                    
                    # 1) 아침 8시 - 전일 비교 리포트
                    if hour == 8 and minute == 0 and last_comparison_sent != key:
                        print("📈 [08:00] 전일 비교 리포트 발송")
                        self.check_extended()
                        last_comparison_sent = key
                    
                    # 2) 오후 6시 - 일일 요약 리포트  
                    elif hour == 18 and minute == 0 and last_daily_summary != key:
                        print("📋 [18:00] 일일 요약 리포트 발송")
                        self.send_daily_summary()
                        last_daily_summary = key
                    
                    # 다음 체크까지 대기
                    time.sleep(current_interval * 60)
                    
                else:
                    # 야간 시간대 (18:00-07:00) - 조용한 모드
                    if hour >= 18:
                        next_run = (now_kst + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
                    else:  # hour < 7
                        next_run = now_kst.replace(hour=7, minute=0, second=0, microsecond=0)
                    
                    wait_seconds = (next_run - now_kst).total_seconds()
                    wait_hours = int(wait_seconds // 3600)
                    wait_minutes = int((wait_seconds % 3600) // 60)
                    
                    print(f"💤 야간 조용한 모드 - 다음 07시까지: {wait_hours}시간 {wait_minutes}분 (변경사항 있을 때만 알림)")
                    
                    # 야간에는 조용한 체크 (변경사항 있을 때만 알림)
                    self.check_silent()
                    
                    # 다음 07시까지 대기
                    time.sleep(wait_seconds)
                        
        except KeyboardInterrupt:
            print("\n🛑 모니터링 중단")
            self.send_monitoring_stopped_notification()
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")
            self.send_dooray_notification(f"모니터링 오류 발생: {e}", is_error=True)

    def start_monitoring(self, interval_minutes=60):
        """
        기본 모니터링 시작 (고정 간격)
        
        지정된 간격으로 무한 반복하여 뉴스 상태를 체크합니다.
        변경사항이 없어도 매번 상태 알림을 전송합니다.
        
        Args:
            interval_minutes (int): 체크 간격 (분 단위, 기본값 60분)
        """
        print(f"🔄 POSCO 뉴스 기본 모니터링 시작 ({interval_minutes}분 간격)")
        
        self.load_cache()
        self.send_dooray_notification(
            f"🔄 POSCO 뉴스 기본 모니터링 시작\n{interval_minutes}분 간격으로 체크합니다."
        )
        
        try:
            while True:
                current_time = datetime.now().strftime('%H:%M')
                print(f"🔍 [{current_time}] 모니터링 실행 (다음: {interval_minutes}분 후)")
                
                # 기본 체크 실행
                self.check_once()
                
                # 다음 체크까지 대기
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 모니터링 중단")
            self.send_monitoring_stopped_notification()
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")
            self.send_dooray_notification(f"모니터링 오류 발생: {e}", is_error=True)

    def send_daily_summary(self):
        """일일 요약 리포트 전송 - 오늘 뉴스 + 전일 비교"""
        print("📋 일일 요약 리포트 생성 중...")
        
        today_kr = datetime.now().strftime('%Y%m%d')
        today_display = f"{today_kr[:4]}-{today_kr[4:6]}-{today_kr[6:8]}"
        weekday = self.get_weekday_display()
        expected_today = self.get_expected_news_count_today()
        
        # 현재 뉴스 데이터 가져오기
        current_data = self.get_news_data()
        if not current_data:
            print("❌ 뉴스 데이터를 가져올 수 없습니다.")
            return
        
        # 전일 데이터 가져오기
        previous_data = self.get_previous_day_data(current_data)
        
        # 오늘 발행된 뉴스 수집
        today_news = []
        comparison_items = []
        
        for news_type, news_data in current_data.items():
            news_config = NEWS_TYPES.get(news_type, {"display_name": news_type.upper()})
            type_display = news_config["display_name"]
            publish_days = news_config.get('publish_days', [])
            today_weekday = datetime.now().weekday()
            
            news_date = news_data.get('date', '')
            news_time = news_data.get('time', '')
            news_title = news_data.get('title', '')
            
            # 오늘 뉴스 상태
            if news_date == today_kr and news_title:
                today_news.append({
                    'type': news_type,
                    'data': news_data,
                    'type_display': type_display
                })
                status = "🟢 오늘 발행"
                today_info = f"📅 오늘: {self.format_datetime(news_date, news_time)}\n📝 제목: {news_title[:60]}{'...' if len(news_title) > 60 else ''}"
                print(f"✅ {news_type}: 오늘 뉴스 발견")
            elif today_weekday in publish_days:
                status = "🔴 미발행"
                today_info = "📅 오늘: 발행 대기 중"
                print(f"❌ {news_type}: 오늘 뉴스 대기 중")
            else:
                status = f"⏸️ {weekday}요일 휴무"
                today_info = f"📅 오늘: {weekday}요일 휴무"
                print(f"⏸️ {news_type}: {weekday}요일 휴무")
            
            # 직전 데이터와 비교
            prev_info = ""
            if previous_data.get(news_type):
                prev_news = previous_data[news_type]
                prev_date = prev_news.get('date', '')
                prev_time = prev_news.get('time', '')
                prev_title = prev_news.get('title', '')
                
                if prev_title and prev_date:
                    # 날짜 차이 계산 (개선된 로직)
                    try:
                        today_date_obj = datetime.strptime(today_kr, "%Y%m%d")
                        prev_date_obj = datetime.strptime(prev_date, "%Y%m%d")
                        days_diff = (today_date_obj - prev_date_obj).days
                        
                        if days_diff == 0:
                            gap_text = "오늘"
                        elif days_diff == 1:
                            gap_text = "1일 전"
                        else:
                            gap_text = f"{days_diff}일 전"
                    except Exception as e:
                        print(f"날짜 계산 오류: {e}, prev_date={prev_date}, today={today_kr}")
                        gap_text = "날짜 계산 오류"
                    
                    prev_info = f"📅 직전: {self.format_datetime(prev_date, prev_time)} ({gap_text})\n"
                    prev_info += f"📝 제목: {prev_title[:60]}{'...' if len(prev_title) > 60 else ''}"
                else:
                    prev_info = "📅 직전: 데이터 없음"
            else:
                prev_info = "📅 직전: 데이터 없음"
            
            # 비교 항목 생성 (가독성 개선)
            if status.startswith("⏸️") or status.startswith("🔴"):
                # 휴무나 미발행인 경우 더 명확하게 표시
                item_text = f"📰 {type_display} ({status})\n📅 오늘: 미발행\n{prev_info}"
            else:
                # 발행된 경우
                item_text = f"📰 {type_display} ({status})\n{today_info}\n{prev_info}"
            
            comparison_items.append(item_text)
        
        # 메시지 생성
        message = f"📋 {today_display}({weekday}) 일일 뉴스 요약\n"
        message += f"🎯 오늘 발행: {len(today_news)}/{expected_today}개\n\n"
        
        # 각 뉴스 비교 정보
        for i, item in enumerate(comparison_items):
            message += f"{item}\n"
            if i < len(comparison_items) - 1:
                message += "━━━━━━━━━━━━━━━━━━━━━\n"
        
        # 요약 정보
        if expected_today == 0:
            summary_text = f"🔵 {weekday}요일 완전 휴무"
        elif len(today_news) == expected_today:
            summary_text = f"🟢 예상 뉴스 모두 발행"
        elif len(today_news) > 0:
            summary_text = f"🟡 일부 뉴스만 발행"
        else:
            summary_text = f"🔴 발행 대기 중"
        
        message += f"\n📊 {summary_text} | ⏰ {datetime.now().strftime('%H:%M')}"
        
        # Dooray 전송
        payload = {
            "botName": "POSCO 뉴스 📋 일일요약",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "attachments": [{
                "color": "#9c27b0",
                "text": message
            }]
        }
        
        try:
            response = requests.post(
                self.dooray_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print("✅ 일일 요약 리포트 전송 성공")
            else:
                print(f"❌ 일일 요약 리포트 전송 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 일일 요약 리포트 전송 오류: {e}")
    
    def get_news_by_date(self, news_type, date_str):
        """
        특정 날짜의 특정 뉴스 타입 데이터 조회
        
        Args:
            news_type (str): 뉴스 타입
            date_str (str): 조회할 날짜 (YYYYMMDD 형식)
            
        Returns:
            dict: 해당 날짜의 뉴스 데이터
                  조회 실패 시 None 반환
        """
        try:
            params = {
                'user': self.api_user,
                'password': self.api_pwd,
                'news_type': news_type,
                'date': date_str
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=self.api_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"❌ {news_type} 뉴스 조회 오류: {e}")
            return None

    def check_extended(self):
        """영업일 비교 체크 - 현재 vs 직전 영업일 상세 비교"""
        print(f"🔍 현재 vs 직전 영업일 데이터 비교 중... {datetime.now()}")
        
        current_data = self.get_news_data()
        if not current_data:
            self.send_dooray_notification("API 호출 실패", is_error=True)
            return
        
        # 오늘 기준 직전 영업일 데이터 조회
        previous_data = {}
        today_obj = datetime.now()
        
        for news_type, current_item in current_data.items():
            news_config = NEWS_TYPES.get(news_type, {})
            publish_days = news_config.get('publish_days', [])
            type_display = news_config.get('display_name', news_type.upper())
            
            print(f"📅 {type_display}: 직전 영업일 데이터 검색 중...")
            
            found_previous_data = False
            for days_back in range(1, 8):
                try:
                    check_date_obj = today_obj - timedelta(days=days_back)
                    check_weekday = check_date_obj.weekday()
                    check_date = check_date_obj.strftime("%Y%m%d")
                    
                    if check_weekday in publish_days:
                        prev_api_data = self.get_news_data(date=check_date)
                        
                        if prev_api_data and news_type in prev_api_data:
                            prev_item = prev_api_data[news_type]
                            prev_title = prev_item.get('title', '')
                            prev_date = prev_item.get('date', '')
                            
                            print(f"📅 {type_display}: {days_back}일 전({check_date}) 조회 - 제목: {prev_title[:30]}{'...' if len(prev_title) > 30 else ''}")
                            
                            if prev_title and prev_date:
                                previous_data[news_type] = prev_item
                                print(f"📅 {type_display}: 직전 영업일 데이터 발견 ({days_back}일 전, {['월','화','수','목','금','토','일'][check_weekday]}요일)")
                                found_previous_data = True
                                break
                        else:
                            print(f"📅 {type_display}: {days_back}일 전({check_date}) 데이터 없음")
                    
                except Exception as e:
                    print(f"❌ {type_display}: {days_back}일 전 데이터 조회 오류 - {e}")
                    continue
            
            if not found_previous_data:
                print(f"📅 {type_display}: 1주일 내 직전 영업일 데이터를 찾을 수 없음")
                previous_data[news_type] = None
        
        # 비교 메시지 생성
        message = "📊 현재 vs 직전 영업일 데이터 비교\n\n"
        
        today_kr = datetime.now().strftime('%Y%m%d')
        today_weekday = datetime.now().weekday()
        weekday_name = self.get_weekday_display()
        comparison_items = []
        
        for news_type, current_item in current_data.items():
            news_config = NEWS_TYPES.get(news_type, {"display_name": news_type.upper()})
            type_display = news_config["display_name"]
            publish_days = news_config.get('publish_days', [])
            
            current_date = current_item.get('date', '')
            current_time = current_item.get('time', '')
            current_title = current_item.get('title', '')
            
            if not current_date or not current_title:
                if today_weekday in publish_days:
                    current_status = "🔴"
                    current_status_text = "데이터 없음"
                    current_info = "📅 현재: 데이터 없음"
                else:
                    current_status = "⏸️"
                    current_status_text = f"{weekday_name}요일 휴무"
                    current_info = "📅 현재: 미발행"
            else:
                if current_date == today_kr:
                    current_status = "🟢"
                    current_status_text = "최신"
                else:
                    current_status = "🟡"
                    current_status_text = "과거"
                
                current_datetime = self.format_datetime(current_date, current_time)
                current_info = f"📅 현재: {current_datetime}\n📝 현재 제목: {current_title[:45]}{'...' if len(current_title) > 45 else ''}"
            
            previous_item = previous_data.get(news_type)
            if previous_item:
                prev_date = previous_item.get('date', '')
                prev_time = previous_item.get('time', '')
                prev_title = previous_item.get('title', '')
                
                if prev_date and prev_title:
                    try:
                        prev_date_obj = datetime.strptime(prev_date, "%Y%m%d")
                        today_obj = datetime.strptime(today_kr, "%Y%m%d")
                        days_diff = (today_obj - prev_date_obj).days
                        gap_text = "오늘" if days_diff == 0 else f"{days_diff}일 전"
                    except:
                        gap_text = "날짜 불명"
                    
                    prev_datetime = self.format_datetime(prev_date, prev_time)
                    prev_info = f"\n\n📅 직전: {prev_datetime} ({gap_text})\n📝 직전 제목: {prev_title[:45]}{'...' if len(prev_title) > 45 else ''}"
                else:
                    prev_info = "\n\n📅 직전: 데이터 없음"
            else:
                prev_info = "\n\n📅 직전: 데이터 없음"
            
            item_text = f"{current_status} {type_display} ({current_status_text})\n{current_info}{prev_info}"
            comparison_items.append(item_text)
        
        for i, item in enumerate(comparison_items):
            message += f"{item}\n"
            if i < len(comparison_items) - 1:
                message += "━━━━━━━━━━━━━━━━━━━━━\n"
        
        message += f"\n최종 확인: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        payload = {
            "botName": "POSCO 뉴스 📊",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": "현재 vs 직전 영업일 데이터 비교",
            "attachments": [{"color": "#ff9800", "text": message}]
        }
        
        try:
            response = requests.post(self.dooray_webhook, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            if response.status_code == 200:
                print("✅ 영업일 비교 알림 전송 성공")
            else:
                print(f"❌ 영업일 비교 알림 전송 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 영업일 비교 알림 전송 오류: {e}")

# 이 파일은 모듈로만 사용됩니다. 실행은 run_monitor.py를 사용하세요.