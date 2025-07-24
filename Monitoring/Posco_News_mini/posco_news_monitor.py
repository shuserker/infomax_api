import requests
from requests.auth import HTTPBasicAuth
import json
import time
import hashlib
from datetime import datetime
import os

class PoscoNewsMonitor:
    def __init__(self, dooray_webhook_url):
        self.api_url = "https://dev-global-api.einfomax.co.kr/apis/posco/news"
        self.api_user = "infomax"
        self.api_pwd = "infomax!"
        self.dooray_webhook = dooray_webhook_url
        self.last_hash = None
        self.cache_file = "posco_news_cache.json"
        
    def get_news_data(self):
        """POSCO 뉴스 데이터 가져오기"""
        try:
            resp = requests.get(
                self.api_url,
                auth=HTTPBasicAuth(self.api_user, self.api_pwd),
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
            
            payload = {
                "botName": "POSCO 뉴스 모니터",
                "botIconImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAaVBMVEUAWJEAVpAAUo4ATYsAS4oAUY0AT4xwk7WpvdHCzty0w9SIpMATX5UASIl+nrz///8AR4jk7PL1+fwAQoZGeaXL2OQwa50AVI9Ofadjiq+UrcY6caC4ydmctMvm7fKOqcQnZ5rW4OoAWpLTJOO6AAAAwUlEQVR4AWKgPQC0PhcGEMJAEACJ4uzhrv33+O7+wMUzUcaFFIq9NC1My3ZcT74wP8AxHP20maw9hNG+4g+m9vsCojgJgZTujIkIyMSul/s7LfJbzEugksduDTTiFnULeOzYjzuE/i0KB9AnlCkiesTzTgpf7OyPF+UZYMtHxKD3RiNQ5k+IknzKdjaS8YyIxm5fT+wJexwjZXt7QJ27dpq29fGlDzjlSkp5/O0znvr/oXI/INMjjPchivyDMmPF2AKOpw0Hjgjp3QAAAABJRU5ErkJggg==",
                "attachments": [{
                    "color": color,
                    "title": title,
                    "text": message,
                    "ts": int(time.time())
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
    
    def send_news_type_notification(self, news_type, change_detail, news_data):
        """뉴스 타입별 개별 알림 전송"""
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
            message += f"날짜: {change_detail['date']} {change_detail['time']}"
        else:
            message = f"변경사항: {', '.join(change_detail['changes'])}\n\n"
            
            if "제목" in change_detail['changes']:
                message += f"이전 제목: {change_detail['old_title']}\n"
                message += f"새 제목: {change_detail['new_title']}\n\n"
            else:
                message += f"제목: {change_detail['new_title']}\n\n"
            
            message += f"날짜: {change_detail['date']} {change_detail['time']}\n"
            message += f"작성자: {', '.join(news_data['writer'])}\n"
            message += f"카테고리: {', '.join(news_data['category'])}"
        
        # 개별 알림 전송
        payload = {
            "botName": "POSCO 뉴스 모니터",
            "botIconImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAaVBMVEUAWJEAVpAAUo4ATYsAS4oAUY0AT4xwk7WpvdHCzty0w9SIpMATX5UASIl+nrz///8AR4jk7PL1+fwAQoZGeaXL2OQwa50AVI9Ofadjiq+UrcY6caC4ydmctMvm7fKOqcQnZ5rW4OoAWpLTJOO6AAAAwUlEQVR4AWKgPQC0PhcGEMJAEACJ4uzhrv33+O7+wMUzUcaFFIq9NC1My3ZcT74wP8AxHP20maw9hNG+4g+m9vsCojgJgZTujIkIyMSul/s7LfJbzEugksduDTTiFnULeOzYjzuE/i0KB9AnlCkiesTzTgpf7OyPF+UZYMtHxKD3RiNQ5k+IknzKdjaS8YyIxm5fT+wJexwjZXt7QJ27dpq29fGlDzjlSkp5/O0znvr/oXI/INMjjPchivyDMmPF2AKOpw0Hjgjp3QAAAABJRU5ErkJggg==",
            "attachments": [{
                "color": "#0066cc",
                "title": title,
                "text": message,
                "ts": int(time.time())
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
        """일반 알림 전송 (새 데이터 등)"""
        message = f"{change_result['summary']}\n\n"
        
        for news_type, news_data in current_data.items():
            title = news_data['title'][:50] + "..." if len(news_data['title']) > 50 else news_data['title']
            message += f"📰 {news_type.upper()}\n"
            message += f"제목: {title}\n"
            message += f"날짜: {news_data['date']} {news_data['time']}\n\n"
        
        message += f"업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_dooray_notification(message)
    
    def send_no_change_notification(self):
        """변경사항 없음 알림"""
        message = f"변경사항이 없습니다.\n\n"
        message += f"체크 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        payload = {
            "botName": "POSCO 뉴스 모니터",
            "botIconImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAaVBMVEUAWJEAVpAAUo4ATYsAS4oAUY0AT4xwk7WpvdHCzty0w9SIpMATX5UASIl+nrz///8AR4jk7PL1+fwAQoZGeaXL2OQwa50AVI9Ofadjiq+UrcY6caC4ydmctMvm7fKOqcQnZ5rW4OoAWpLTJOO6AAAAwUlEQVR4AWKgPQC0PhcGEMJAEACJ4uzhrv33+O7+wMUzUcaFFIq9NC1My3ZcT74wP8AxHP20maw9hNG+4g+m9vsCojgJgZTujIkIyMSul/s7LfJbzEugksduDTTiFnULeOzYjzuE/i0KB9AnlCkiesTzTgpf7OyPF+UZYMtHxKD3RiNQ5k+IknzKdjaS8YyIxm5fT+wJexwjZXt7QJ27dpq29fGlDzjlSkp5/O0znvr/oXI/INMjjPchivyDMmPF2AKOpw0Hjgjp3QAAAABJRU5ErkJggg==",
            "attachments": [{
                "color": "#28a745",  # 녹색
                "title": "✅ 상태 정상",
                "text": message,
                "ts": int(time.time())
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
    
    def format_news_summary(self, data):
        """뉴스 요약 포맷팅"""
        summary = "📰 **POSCO 뉴스 업데이트**\n\n"
        
        for news_type, news_data in data.items():
            title = news_data['title'][:50] + "..." if len(news_data['title']) > 50 else news_data['title']
            summary += f"🔹 **{news_type.upper()}**\n"
            summary += f"   제목: {title}\n"
            summary += f"   날짜: {news_data['date']} {news_data['time']}\n"
            summary += f"   작성자: {', '.join(news_data['writer'])}\n"
            summary += f"   카테고리: {', '.join(news_data['category'])}\n\n"
        
        summary += f"⏰ 업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return summary
    
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
                # 각 뉴스 타입별로 개별 알림 전송
                for news_type, change_detail in change_result["changes"].items():
                    self.send_news_type_notification(news_type, change_detail, current_data[news_type])
            else:
                # 새로운 데이터인 경우 전체 알림
                self.send_general_notification(change_result, current_data)
            
            # 캐시 업데이트
            self.save_cache(current_data, current_hash)
            self.last_hash = current_hash
            
            return True
        else:
            print("📝 변경사항 없음")
            # 변경사항 없음 알림 전송
            self.send_no_change_notification()
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