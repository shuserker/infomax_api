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
        """날짜 시간 포맷 변환"""
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
            
            bot_name = "POSCO 뉴스 ❌" if is_error else "POSCO 뉴스 🔔"
            preview_text = message.split('\n')[0] if '\n' in message else message[:50]
            
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
    
    def send_status_notification(self, current_data):
        """상태 알림 전송 (개선된 가독성)"""
        message = "📊 현재 데이터 상태\n\n"
        
        if current_data:
            today_kr = datetime.now().strftime('%Y%m%d')
            news_items = []
            
            # 뉴스 타입별 이모지 매핑
            type_emojis = {
                "exchange-rate": "",
                "newyork-market-watch": "", 
                "kospi-close": ""
            }
            
            for news_type, news_data in current_data.items():
                emoji = type_emojis.get(news_type, "📰")
                type_display = news_type.replace("-", " ").upper()
                
                news_date = news_data.get('date', '')
                news_time = news_data.get('time', '')
                news_title = news_data.get('title', '')
                
                # 데이터 상태 판단
                if not news_date or not news_title:
                    status = "🔴"
                    status_text = "데이터 없음"
                    date_time_display = "데이터 없음"
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
                    title_preview = f"\n📰 제목: {news_title[:45]}{'...' if len(news_title) > 45 else ''}"
                
                news_items.append(f"{status} {type_display} ({status_text})\n📅 시간: {date_time_display}{title_preview}")
            
            # 각 뉴스 항목을 구분선으로 분리
            for i, item in enumerate(news_items):
                message += f"{item}\n"
                if i < len(news_items) - 1:  # 마지막 항목이 아니면 구분선 추가
                    message += "━━━━━━━━━━━━━━━━━━━━━\n"
        
        current_datetime = datetime.now().strftime('%Y-%m-%d  ·  %H:%M:%S')
        message += f"\n최종 확인: {current_datetime}"
        
        preview_info = ""
        if current_data:
            status_count = sum(1 for _, news_data in current_data.items() 
                             if news_data.get('date') == datetime.now().strftime('%Y%m%d'))
            total_count = len(current_data)
            if status_count > 0:
                preview_info = f" 🟢{status_count}/{total_count}"
            else:
                preview_info = f" 🔴{total_count}개 과거"
        
        payload = {
            "botName": f"POSCO 뉴스{preview_info}",
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
        """변경사항 알림 전송 (신규입력/파라미터별 변경 상세 표기)"""
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
        """변경사항 감지"""
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
        """간결 상태 알림 전송 (ex: POSCO 뉴스 🟢2/3 + 갱신 데이터 없음)"""
        today_kr = datetime.now().strftime('%Y%m%d')
        status_count = sum(1 for _, news_data in current_data.items() 
                         if news_data.get('date') == today_kr)
        total_count = len(current_data) if current_data else 0
        if status_count == total_count:
            status_emoji = '🟢'
        elif status_count > 0:
            status_emoji = '🟡'
        else:
            status_emoji = '🔴'
        bot_name = f"POSCO 뉴스 {status_emoji}{status_count}/{total_count}"
        payload = {
            "botName": bot_name,
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
        """자동 모니터링 프로세스 중지 알림 (오류/빨간칸)"""
        payload = {
            "botName": "POSCO 뉴스 ❌",
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
        """한 번 체크 (simple_status=True면 간결 알림)"""
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
    
    def check_basic(self):
        """기본 확인 - 변경사항 있을 때만 알림"""
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
            print("📝 변경사항 없음 - 알림 전송하지 않음")
            return False
    
    def get_previous_day_data(self, current_data):
        """영업일 기준으로 실제 다른 데이터가 있는 직전 날짜 조회"""
        previous_data = {}
        
        for news_type, news_data in current_data.items():
            current_date = news_data.get('date', '')
            current_title = news_data.get('title', '')
            
            if not current_date or not current_title:
                previous_data[news_type] = None
                continue
            
            print(f"📅 {news_type}: 직전 영업일 데이터 검색 중...")
            
            # 최대 10일까지 역순으로 검색하여 다른 데이터 찾기
            found_different_data = False
            for days_back in range(1, 11):
                try:
                    # N일 전 날짜 계산
                    check_date_obj = datetime.strptime(current_date, "%Y%m%d") - timedelta(days=days_back)
                    check_date = check_date_obj.strftime("%Y%m%d")
                    
                    # API에서 해당 날짜 데이터 조회
                    prev_api_data = self.get_news_data(date=check_date)
                    
                    if prev_api_data and news_type in prev_api_data:
                        prev_item = prev_api_data[news_type]
                        prev_title = prev_item.get('title', '')
                        
                        # 빈 데이터가 아니고 제목이 다르면 실제 다른 데이터로 판단
                        if prev_title and prev_title != current_title:
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
        """현재 vs 직전 영업일 데이터 비교 알림 (개선된 가독성)"""
        previous_data = self.get_previous_day_data(current_data)
        
        message = "📊 현재 vs 직전 영업일 데이터 비교\n"
        comparison_items = []
        
        # 뉴스 타입별 이모지 매핑
        type_emojis = {
            "exchange-rate": "",
            "newyork-market-watch": "", 
            "kospi-close": ""
        }
        
        for news_type, current_news in current_data.items():
            emoji = type_emojis.get(news_type, "📰")
            type_display = news_type.replace("-", " ").upper()
            
            # 현재 데이터 상태 확인
            current_date = current_news.get('date', '')
            current_time = current_news.get('time', '')
            current_title = current_news.get('title', '')
            
            # 데이터 유무에 따른 상태 표시
            if not current_date or not current_title:
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
        """확장 확인 - 현재/이전 데이터 상세 비교"""
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
    
    def start_monitoring(self, interval_minutes=5):
        """모니터링 시작 (08, 16, 17시 전일비교 자동 알림 포함)"""
        import pytz
        KST = pytz.timezone('Asia/Seoul')
        print(f"🚀 POSCO 뉴스 모니터링 시작 (체크 간격: {interval_minutes}분)")
        self.load_cache()
        self.send_dooray_notification(
            f"🚀 POSCO 뉴스 모니터링 시작\n체크 간격: {interval_minutes}분"
        )
        last_comparison_sent = None
        last_status_sent = None  # 상태 알림 중복 방지
        last_extended_sent = None  # 확장확인 중복 방지
        comparison_hours = {8, 16, 17}
        status_hours = {11, 13, 15, 17}
        extended_hours = {11, 13, 15, 17}
        try:
            while True:
                now_kst = datetime.now(KST)
                hour = now_kst.hour
                minute = now_kst.minute
                # 11시~17시(포함)만 동작
                if 11 <= hour <= 17:
                    self.check_once(simple_status=True)
                    key = f"{now_kst.strftime('%Y%m%d')}-{hour}"
                    # 비교 알림
                    if hour in comparison_hours and minute == 0:
                        if last_comparison_sent != key:
                            print(f"[전일비교] {hour}시 자동 알림 발송")
                            current_data = self.get_news_data()
                            if current_data:
                                self.send_comparison_notification(current_data)
                            last_comparison_sent = key
                    # 상태 알림
                    if hour in status_hours and minute == 0:
                        if last_status_sent != key:
                            print(f"[상태알림] {hour}시 정각 상태 알림 발송")
                            current_data = self.get_news_data()
                            if current_data:
                                self.send_status_notification(current_data)
                            last_status_sent = key
                    # 확장 확인
                    if hour in extended_hours and minute == 0:
                        if last_extended_sent != key:
                            print(f"[확장확인] {hour}시 정각 확장 확인 실행")
                            self.check_extended()
                            last_extended_sent = key
                    print(f"⏰ {interval_minutes}분 후 다시 체크...")
                    time.sleep(interval_minutes * 60)
                else:
                    # 17시 이후 또는 11시 이전이면 다음 11시까지 대기
                    if hour < 11:
                        next_run = now_kst.replace(hour=11, minute=0, second=0, microsecond=0)
                    else:
                        next_run = (now_kst + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0)
                    wait_seconds = (next_run - now_kst).total_seconds()
                    print(f"⏸️ 모니터링 시간대(11~17시)가 아님. 다음 11시까지 대기: {int(wait_seconds//3600)}시간 {int((wait_seconds%3600)//60)}분")
                    time.sleep(wait_seconds)
        except KeyboardInterrupt:
            print("\n🛑 모니터링 중단")
            self.send_monitoring_stopped_notification()
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")
            self.send_dooray_notification(f"모니터링 오류 발생: {e}", is_error=True)

# 사용 예시
if __name__ == "__main__":
    DOORAY_WEBHOOK_URL = "YOUR_DOORAY_WEBHOOK_URL_HERE"
    
    if DOORAY_WEBHOOK_URL == "YOUR_DOORAY_WEBHOOK_URL_HERE":
        print("❌ Dooray 웹훅 URL을 설정해주세요!")
        print("사용법:")
        print("1. Dooray에서 웹훅 URL 생성")
        print("2. 코드에서 DOORAY_WEBHOOK_URL 변수 수정")
        print("3. python posco_news_monitor.py 실행")
    else:
        monitor = PoscoNewsMonitor(DOORAY_WEBHOOK_URL)
        monitor.start_monitoring(interval_minutes=5)