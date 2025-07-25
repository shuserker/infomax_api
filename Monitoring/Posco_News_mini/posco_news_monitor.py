import requests
from requests.auth import HTTPBasicAuth
import json
import time
import hashlib
from datetime import datetime, timedelta
import os

class PoscoNewsMonitor:
    def __init__(self, dooray_webhook_url):
        self.api_url = "https://dev-global-api.einfomax.co.kr/apis/posco/news"
        self.api_user = "infomax"
        self.api_pwd = "infomax!"
        self.dooray_webhook = dooray_webhook_url
        self.last_hash = None
        self.cache_file = "posco_news_cache.json"
    
    def format_datetime(self, date_str, time_str):
        """날짜 시간 포맷 변환: 20250724 163916 -> 2025_07_24 16:39:19"""
        try:
            # 날짜 포맷: YYYYMMDD -> YYYY_MM_DD
            formatted_date = f"{date_str[:4]}_{date_str[4:6]}_{date_str[6:8]}"
            
            # 시간 포맷 처리
            if len(time_str) >= 6:
                # 정상적인 HHMMSS 형식
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            elif len(time_str) == 5:
                # 5자리인 경우 (예: 61844 -> 06:18:44)
                if time_str.startswith('6'):
                    # 6으로 시작하는 경우 0을 앞에 붙여서 처리
                    time_str = '0' + time_str
                    formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                else:
                    # 다른 5자리 형식 처리
                    formatted_time = f"0{time_str[:1]}:{time_str[1:3]}:{time_str[3:5]}"
            elif len(time_str) == 4:
                # 4자리인 경우 (예: 1234 -> 12:34:00)
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:00"
            else:
                # 기타 형식은 그대로 표시
                formatted_time = time_str
            
            return f"{formatted_date} {formatted_time}"
        except:
            return f"{date_str} {time_str}"
    
    def get_previous_date(self, date_str):
        """최신 날짜에서 1일을 뺀 날짜 계산"""
        try:
            # YYYYMMDD 형식을 datetime으로 변환
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            # 1일 빼기
            prev_date = date_obj - timedelta(days=1)
            # 다시 YYYYMMDD 형식으로 변환
            return prev_date.strftime("%Y%m%d")
        except:
            return date_str
        
    def get_news_data(self, date=None):
        """POSCO 뉴스 데이터 가져오기"""
        try:
            params = {}
            if date:
                params['date'] = date
                
            resp = requests.get(
                self.api_url,
                auth=HTTPBasicAuth(self.api_user, self.api_pwd),
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ API 호출 오류: {e}")
            return None
    
    def get_data_hash(self, data):
        """데이터의 해시값 계산"""
        if not data:
            return None
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def load_cache(self):
        """캐시된 데이터 로드"""
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
        """캐시 저장"""
        cache = {
            'last_hash': data_hash,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    
    def send_dooray_notification(self, message, is_error=False):
        """Dooray 웹훅으로 알림 전송"""
        try:
            color = "#ff4444" if is_error else "#0066cc"
            title = "⚠️ 오류 알림" if is_error else "🔔 POSCO 뉴스 알림"
            
            # 미리보기용 botName 생성
            if is_error:
                bot_name = "POSCO 뉴스 ❌"
            else:
                # 메시지에서 핵심 정보 추출
                if "변경 감지" in message:
                    bot_name = "POSCO 뉴스 🔔"
                elif "시작" in message:
                    bot_name = "POSCO 뉴스 🚀"
                elif "중단" in message:
                    bot_name = "POSCO 뉴스 🛑"
                else:
                    bot_name = "POSCO 뉴스 📢"
            
            # 미리보기용 짧은 텍스트 추출
            preview_text = message.split('\n')[0] if '\n' in message else message[:50]
            
            # 상세 내용에서 첫 줄 제거 (중복 방지)
            lines = message.split('\n')
            detail_message = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            payload = {
                "botName": bot_name,
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
    
    def send_news_type_notification(self, news_type, change_detail, news_data, old_data=None):
        """뉴스 타입별 개별 알림 전송 (이전 데이터 포함)"""
        title_emoji = {
            "exchange-rate": "💱",
            "newyork-market-watch": "🗽", 
            "kospi-close": "📈"
        }
        
        emoji = title_emoji.get(news_type, "📰")
        title = f"{emoji} {news_type.upper()} 업데이트"
        
        if change_detail["change_type"] == "new":
            message = f"새로운 뉴스가 추가되었습니다.\n\n"
            message += f"제목: {change_detail['title']}\n"
            message += f"최신 데이터: {self.format_datetime(change_detail['date'], change_detail['time'])}"
        else:
            message = f"변경사항: {', '.join(change_detail['changes'])}\n\n"
            
            # 이전 데이터 정보 추가
            if old_data and news_type in old_data:
                old_news = old_data[news_type]
                message += f"📅 직전 데이터: {self.format_datetime(old_news['date'], old_news['time'])}\n"
                message += f"📅 최신 데이터: {self.format_datetime(change_detail['date'], change_detail['time'])}\n\n"
            else:
                message += f"📅 최신 데이터: {self.format_datetime(change_detail['date'], change_detail['time'])}\n\n"
            
            if "제목" in change_detail['changes']:
                message += f"📰 이전 제목: {change_detail['old_title']}\n"
                message += f"📰 새 제목: {change_detail['new_title']}\n\n"
            else:
                message += f"📰 제목: {change_detail['new_title']}\n\n"
            
            message += f"✍️ 작성자: {', '.join(news_data['writer'])}\n"
            message += f"🏷️ 카테고리: {', '.join(news_data['category'])}"
        
        # 개별 알림 전송
        # 미리보기용 짧은 텍스트 (첫 줄만)
        preview_text = message.split('\n')[0] if '\n' in message else message[:50]
        
        # 상세 내용에서 첫 줄 제거 (중복 방지)
        lines = message.split('\n')
        detail_message = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        payload = {
            "botName": f"POSCO 뉴스 🔔",
            "text": preview_text,
            "attachments": [{
                "color": "#0066cc",
                "text": detail_message
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
    
    def send_general_notification(self, change_result, current_data):
        """일반 알림 전송 (새 데이터 등) - send_no_change_notification과 동일한 형태"""
        message = f"📊 갱신 정보:\n"
        
        # 각 타입별 최신 갱신 정보 추가 (send_no_change_notification과 동일한 로직)
        if current_data:
            title_emoji = {
                "exchange-rate": "💱",
                "newyork-market-watch": "🗽", 
                "kospi-close": "📈"
            }
            
            # 오늘 날짜 (한국 시간 기준)
            today_kr = datetime.now().strftime('%Y%m%d')
            
            news_items = []
            for news_type, news_data in current_data.items():
                emoji = title_emoji.get(news_type, "📰")
                
                # 날짜와 시간 분리
                news_date = news_data['date']
                news_time = news_data['time']
                
                # 날짜 포맷팅 (YYYY-MM-DD) - 빈 데이터 처리
                if news_date and news_date.strip() and len(news_date) >= 8:
                    formatted_date = f"{news_date[:4]}-{news_date[4:6]}-{news_date[6:8]}"
                else:
                    formatted_date = "데이터 없음"
                
                # 시간 포맷팅 (HH:MM:SS) - 빈 데이터 처리
                if news_time and news_time.strip() and len(news_time) >= 4:
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
                
                # 오늘 날짜인지 체크
                status = "🟢" if news_date == today_kr else "🔴"
                
                # 빈 데이터 처리
                if formatted_date == "데이터 없음" and formatted_time == "":
                    date_time_display = "데이터 없음"
                elif formatted_time == "":
                    date_time_display = formatted_date
                else:
                    date_time_display = f"{formatted_date}  ·  {formatted_time}"
                
                news_items.append(f"{emoji}{status} {news_type.upper()}\n    {date_time_display}")
            
            # 각 뉴스 항목을 개별 줄에 표시 (구분선 포함)
            for i, item in enumerate(news_items):
                message += f"{item}\n"
                if i < len(news_items) - 1:  # 마지막 항목이 아니면 구분선 추가
                    message += "─────────────────────\n"
        
        # 현재 시간
        now = datetime.now()
        current_datetime = now.strftime('%Y-%m-%d  ·  %H:%M:%S')
        message += f"\n최종 확인: {current_datetime}"
        
        # 미리보기용 요약 정보 생성
        preview_info = ""
        if current_data:
            status_count = sum(1 for _, news_data in current_data.items() 
                             if news_data['date'] == datetime.now().strftime('%Y%m%d'))
            total_count = len(current_data)
            if status_count > 0:
                preview_info = f" 🟢{status_count}/{total_count}"
            else:
                preview_info = f" 🔴{total_count}개 과거"
        
        # 미리보기용 짧은 텍스트
        preview_text = "데이터 갱신 없음"
        
        # 상세 내용에서 첫 줄 제거 (중복 방지)
        detail_message = message.replace("📊 갱신 정보:\n", "")
        
        # 상세 내용은 attachments에
        payload = {
            "botName": f"POSCO 뉴스{preview_info}",
            "text": preview_text,
            "attachments": [{
                "color": "#28a745",
                "text": detail_message
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
                print(f"✅ 일반 알림 전송 성공")
        except Exception as e:
            print(f"❌ 일반 알림 전송 오류: {e}")
    
    def send_no_change_notification(self, current_data=None):
        """변경사항 없음 알림 (각 타입별 최신 갱신 정보 포함)"""
        message = f"📊 갱신 정보:\n\n"
        
        # 각 타입별 최신 갱신 정보를 한 줄에 모두 표시
        if current_data:
            title_emoji = {
                "exchange-rate": "💱",
                "newyork-market-watch": "🗽", 
                "kospi-close": "📈"
            }
            
            # 오늘 날짜 (한국 시간 기준)
            today_kr = datetime.now().strftime('%Y%m%d')
            
            news_items = []
            for news_type, news_data in current_data.items():
                emoji = title_emoji.get(news_type, "📰")
                
                # 날짜와 시간 분리
                news_date = news_data['date']
                news_time = news_data['time']
                
                # 날짜 포맷팅 (YYYY-MM-DD) - 빈 데이터 처리
                if news_date and news_date.strip() and len(news_date) >= 8:
                    formatted_date = f"{news_date[:4]}-{news_date[4:6]}-{news_date[6:8]}"
                else:
                    formatted_date = "데이터 없음"
                
                # 시간 포맷팅 (HH:MM:SS) - 빈 데이터 처리
                if news_time and news_time.strip() and len(news_time) >= 4:
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
                
                # 오늘 날짜인지 체크
                status = "🟢" if news_date == today_kr else "🔴"
                
                # 빈 데이터 처리
                if formatted_date == "데이터 없음" and formatted_time == "":
                    date_time_display = "데이터 없음"
                elif formatted_time == "":
                    date_time_display = formatted_date
                else:
                    date_time_display = f"{formatted_date}  ·  {formatted_time}"
                
                news_items.append(f"{emoji}{status} {news_type.upper()}\n    {date_time_display}")
            
            # 각 뉴스 항목을 개별 줄에 표시 (구분선 포함)
            for i, item in enumerate(news_items):
                message += f"{item}\n"
                if i < len(news_items) - 1:  # 마지막 항목이 아니면 구분선 추가
                    message += "─────────────────────\n"
        
        # 현재 시간
        now = datetime.now()
        current_datetime = now.strftime('%Y-%m-%d  ·  %H:%M:%S')
        message += f"\n최종 확인: {current_datetime}"
        
        # 미리보기용 요약 정보 생성
        preview_info = ""
        if current_data:
            status_count = sum(1 for _, news_data in current_data.items() 
                             if news_data['date'] == datetime.now().strftime('%Y%m%d'))
            total_count = len(current_data)
            if status_count > 0:
                preview_info = f" 🟢{status_count}/{total_count}"
            else:
                preview_info = f" 🔴{total_count}개 과거"
        
        # 미리보기용 짧은 텍스트
        preview_text = "데이터 갱신 없음."
        
        # 상세 내용에서 첫 줄 제거 (중복 방지)
        detail_message = message.replace("데이터 갱신 없음.\n\n", "")
        
        # 상세 내용은 attachments에
        payload = {
            "botName": f"POSCO 뉴스{preview_info}",
            "text": preview_text,
            "attachments": [{
                "color": "#28a745",
                "text": detail_message
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
    

    
    def detect_changes(self, old_data, new_data):
        """변경사항 감지 및 상세 분석"""
        if not old_data:
            return {"type": "new", "changes": [], "summary": "새로운 데이터가 감지되었습니다."}
        
        changes = []
        detailed_changes = {}
        
        for news_type in new_data:
            if news_type not in old_data:
                changes.append(f"새로운 뉴스 타입 추가: {news_type}")
                detailed_changes[news_type] = {
                    "change_type": "new",
                    "title": new_data[news_type]['title'],
                    "date": new_data[news_type]['date'],
                    "time": new_data[news_type]['time']
                }
            else:
                old_item = old_data[news_type]
                new_item = new_data[news_type]
                item_changes = []
                
                if old_item['title'] != new_item['title']:
                    changes.append(f"{news_type} 제목 변경")
                    item_changes.append("제목")
                    
                if old_item['content'] != new_item['content']:
                    changes.append(f"{news_type} 내용 업데이트")
                    item_changes.append("내용")
                    
                if old_item['date'] != new_item['date'] or old_item['time'] != new_item['time']:
                    changes.append(f"{news_type} 날짜/시간 변경")
                    item_changes.append("날짜/시간")
                
                if item_changes:
                    detailed_changes[news_type] = {
                        "change_type": "update",
                        "changes": item_changes,
                        "old_title": old_item['title'][:50] + "..." if len(old_item['title']) > 50 else old_item['title'],
                        "new_title": new_item['title'][:50] + "..." if len(new_item['title']) > 50 else new_item['title'],
                        "date": new_item['date'],
                        "time": new_item['time']
                    }
        
        return {
            "type": "update" if changes else "none",
            "changes": changes,
            "detailed": detailed_changes,
            "summary": "\n".join(changes) if changes else "변경사항 없음"
        }
    
    def check_once(self):
        """한 번 체크"""
        print(f"🔍 뉴스 데이터 체크 중... {datetime.now()}")
        
        # 현재 데이터 가져오기
        current_data = self.get_news_data()
        if not current_data:
            self.send_dooray_notification("API 호출 실패", is_error=True)
            return False
        
        # 해시 계산
        current_hash = self.get_data_hash(current_data)
        
        # 캐시된 데이터 로드
        cached_data = self.load_cache()
        
        # 변경사항 확인
        if self.last_hash != current_hash:
            print("📢 데이터 변경 감지!")
            
            # 변경사항 분석
            change_result = self.detect_changes(cached_data, current_data)
            
            if change_result["type"] == "changed":
                # 각 뉴스 타입별로 개별 알림 전송 (이전 데이터 포함)
                for news_type, change_detail in change_result["changes"].items():
                    self.send_news_type_notification(news_type, change_detail, current_data[news_type], cached_data)
            else:
                # 새로운 데이터인 경우 전체 알림
                self.send_general_notification(change_result, current_data)
            
            # 캐시 업데이트
            self.save_cache(current_data, current_hash)
            self.last_hash = current_hash
            
            return True
        else:
            print("📝 변경사항 없음")
            # 변경사항 없음 알림 전송 (현재 데이터 포함)
            self.send_no_change_notification(current_data)
            return False
    
    def start_monitoring(self, interval_minutes=5):
        """모니터링 시작"""
        print(f"🚀 POSCO 뉴스 모니터링 시작 (체크 간격: {interval_minutes}분)")
        
        # 초기 캐시 로드
        self.load_cache()
        
        # 시작 알림
        self.send_dooray_notification(
            f"🚀 POSCO 뉴스 모니터링 시작\n체크 간격: {interval_minutes}분"
        )
        
        try:
            while True:
                self.check_once()
                print(f"⏰ {interval_minutes}분 후 다시 체크...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 모니터링 중단")
            self.send_dooray_notification("🛑 POSCO 뉴스 모니터링 중단", is_error=True)
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")
            self.send_dooray_notification(f"모니터링 오류 발생: {e}", is_error=True)
    
    def check_basic(self):
        """기본 확인 - 변경사항 있을 때만 알림"""
        print(f"🔍 뉴스 데이터 체크 중... {datetime.now()}")
        
        # 현재 데이터 가져오기
        current_data = self.get_news_data()
        if not current_data:
            self.send_dooray_notification("API 호출 실패", is_error=True)
            return False
        
        # 해시 계산
        current_hash = self.get_data_hash(current_data)
        
        # 캐시된 데이터 로드
        cached_data = self.load_cache()
        
        # 변경사항 확인
        if self.last_hash != current_hash:
            print("📢 데이터 변경 감지!")
            
            # 변경사항 분석
            change_result = self.detect_changes(cached_data, current_data)
            
            if change_result["type"] == "changed":
                # 각 뉴스 타입별로 개별 알림 전송 (이전 데이터 포함)
                for news_type, change_detail in change_result["changes"].items():
                    self.send_news_type_notification(news_type, change_detail, current_data[news_type], cached_data)
            else:
                # 새로운 데이터인 경우 전체 알림
                self.send_general_notification(change_result, current_data)
            
            # 캐시 업데이트
            self.save_cache(current_data, current_hash)
            self.last_hash = current_hash
            
            return True
        else:
            print("📝 변경사항 없음 - 알림 전송하지 않음")
            return False
    
    def check_extended(self):
        """확장 확인 - 현재/이전 데이터 상세 표시"""
        print(f"🔍 확장 뉴스 데이터 체크 중... {datetime.now()}")
        
        # 현재 데이터 가져오기
        current_data = self.get_news_data()
        if not current_data:
            self.send_dooray_notification("API 호출 실패", is_error=True)
            return False
        
        # 해시 계산
        current_hash = self.get_data_hash(current_data)
        
        # 캐시된 데이터 로드
        cached_data = self.load_cache()
        
        # 항상 상세 정보 전송 (변경사항 유무와 관계없이)
        if self.last_hash != current_hash:
            print("📢 데이터 변경 감지!")
            
            # 변경사항 분석
            change_result = self.detect_changes(cached_data, current_data)
            
            if change_result["type"] == "changed":
                # 각 뉴스 타입별로 개별 알림 전송
                for news_type, change_detail in change_result["changes"].items():
                    self.send_news_type_notification(news_type, change_detail, current_data[news_type], cached_data)
            else:
                # 새로운 데이터인 경우 전체 알림
                self.send_general_notification(change_result, current_data)
            
            # 캐시 업데이트
            self.save_cache(current_data, current_hash)
            self.last_hash = current_hash
        else:
            print("📝 변경사항 없음 - 현재 상태 상세 표시")
            # 변경사항이 없어도 현재 상태와 1일 전 데이터 비교 표시
            self.cached_data = cached_data  # 임시 저장
            self.send_detailed_comparison(current_data)
        
        return True
    

    def get_previous_day_data(self, current_data):
        """영업일 기준으로 실제 다른 데이터가 있는 직전 날짜 조회"""
        previous_data = {}
        
        for news_type, news_data in current_data.items():
            current_date = news_data['date']
            current_time = news_data['time']
            current_title = news_data['title']
            
            print(f"📅 {news_type}: 최신 {self.format_datetime(current_date, current_time)}")
            print(f"📅 {news_type}: 직전 영업일 데이터 검색 중...")
            
            # 최대 10일까지 역순으로 검색하여 다른 데이터 찾기
            found_different_data = False
            for days_back in range(1, 11):  # 1일 전부터 10일 전까지
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
                        prev_time = prev_item.get('time', '')
                        
                        # 빈 데이터가 아니고 제목이 다르면 실제 다른 데이터로 판단
                        if prev_title and prev_title != current_title:
                            previous_data[news_type] = prev_item
                            print(f"📅 {news_type}: 직전 데이터 발견 ({days_back}일 전) {self.format_datetime(prev_date, prev_time)}")
                            found_different_data = True
                            break
                        elif prev_title == current_title:
                            print(f"📅 {news_type}: {days_back}일 전 - 동일한 제목 (영업일 아님)")
                        else:
                            print(f"📅 {news_type}: {days_back}일 전 - 빈 데이터")
                    else:
                        print(f"📅 {news_type}: {days_back}일 전 - 데이터 없음")
                        
                except Exception as e:
                    print(f"❌ {news_type}: {days_back}일 전 데이터 조회 오류 - {e}")
                    continue
            
            if not found_different_data:
                print(f"📅 {news_type}: 10일 내 직전 데이터를 찾을 수 없음")
                previous_data[news_type] = None
        
        return previous_data
    
    def send_detailed_comparison(self, current_data):
        """현재 데이터와 실제 1일 전 데이터 상세 비교 알림"""
        previous_data = self.get_previous_day_data(current_data)
        
        for news_type, current_news in current_data.items():
            title_emoji = {
                "exchange-rate": "💱",
                "newyork-market-watch": "🗽", 
                "kospi-close": "📈"
            }
            
            emoji = title_emoji.get(news_type, "📰")
            title = f"{emoji} {news_type.upper()} 상세 비교"
            
            message = f"📊 현재 vs 직전 영업일 데이터 비교\n\n"
            
            # 최신 데이터
            message += f"📅 최신 데이터: {self.format_datetime(current_news['date'], current_news['time'])}\n"
            message += f"📰 최신 제목: {current_news['title'][:50]}{'...' if len(current_news['title']) > 50 else ''}\n\n"
            
            # 직전 영업일 데이터
            if previous_data.get(news_type):
                prev_news = previous_data[news_type]
                
                # 날짜 차이 계산
                try:
                    current_date_obj = datetime.strptime(current_news['date'], "%Y%m%d")
                    prev_date_obj = datetime.strptime(prev_news['date'], "%Y%m%d")
                    days_diff = (current_date_obj - prev_date_obj).days
                except:
                    days_diff = "?"
                
                message += f"📅 직전 영업일: {self.format_datetime(prev_news['date'], prev_news['time'])} ({days_diff}일 전)\n"
                message += f"📰 직전 제목: {prev_news['title'][:50]}{'...' if len(prev_news['title']) > 50 else ''}\n\n"
                
                # 변경사항 분석
                if current_news['title'] != prev_news['title']:
                    message += f"🔄 제목 변경됨 (영업일 기준)\n"
                elif current_news['time'] != prev_news['time']:
                    message += f"🔄 시간 변경됨\n"
                else:
                    message += f"✅ 제목 동일 (시간만 다름)\n"
            else:
                message += f"📅 직전 영업일: 데이터 없음\n\n"
                message += f"ℹ️ 10일 내 직전 영업일 데이터를 찾을 수 없습니다\n"
            
            message += f"\n✍️ 작성자: {', '.join(current_news['writer'])}\n"
            message += f"🏷️ 카테고리: {', '.join(current_news['category'])}"
            
            # 개별 알림 전송
            # 미리보기용 짧은 텍스트
            preview_text = message.split('\n')[0] if '\n' in message else message[:50]
            
            # 상세 내용에서 첫 줄 제거 (중복 방지)
            lines = message.split('\n')
            detail_message = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            payload = {
                "botName": f"POSCO 뉴스 📊",
                "text": preview_text,
                "attachments": [{
                    "color": "#6f42c1",
                    "text": detail_message
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
                    print(f"✅ {news_type} 상세 비교 전송 성공")
            except Exception as e:
                print(f"❌ {news_type} 상세 비교 전송 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # Dooray 웹훅 URL을 여기에 입력하세요
    DOORAY_WEBHOOK_URL = "YOUR_DOORAY_WEBHOOK_URL_HERE"
    
    if DOORAY_WEBHOOK_URL == "YOUR_DOORAY_WEBHOOK_URL_HERE":
        print("❌ Dooray 웹훅 URL을 설정해주세요!")
        print("사용법:")
        print("1. Dooray에서 웹훅 URL 생성")
        print("2. 코드에서 DOORAY_WEBHOOK_URL 변수 수정")
        print("3. python posco_news_monitor.py 실행")
    else:
        monitor = PoscoNewsMonitor(DOORAY_WEBHOOK_URL)
        
        # 한 번만 체크
        # monitor.check_once()
        
        # 지속적 모니터링 (5분 간격)
        monitor.start_monitoring(interval_minutes=5)