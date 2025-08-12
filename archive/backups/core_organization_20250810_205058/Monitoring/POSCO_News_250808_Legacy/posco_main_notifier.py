#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Posco Main Notifier
POSCO 알림 시스템

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import system_functionality_verification.py
import .comprehensive_repair_backup/realtime_news_monitor.py.backup_20250809_181657
import requests
import test_config.json
from datetime import datetime, timedelta
import signal
import threading

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
from core import posco_news_250808_monitor.log News 250808APIClient
    from .git/config import .git/config, DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
except ImportError as e:
    print(f"[WARNING] 일부 모듈을 불러올 수 없습니다: {e}")
    print("[INFO] 기본 설정으로 동작합니다.")
    API_CONFIG = {}
    DOORAY_WEBHOOK_URL = "https:/infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"
    BOT_PROFILE_IMAGE_URL = "https:/raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/POSCO News 250808_mini/posco_logo_mini.jpg"

class PoscoMainNotifier:
    """
    POSCO 메인 알림 시스템 클래스
    
    5가지 BOT 타입의 알림을 생성합니다.
    """
    
    def __init__(self):
        """메인 알림자 초기화"""
        self.script_dir = current_dir
        self.state_file = os.path.join(self.script_dir, "main_notifier_state.json")
        self.log_file = os.path.join(self.script_dir, ".naming_backup/config_data_backup/Monitoring/Posco_News_mini/main_notifier.log")
        
        # 실행 제어
        self.running = True
        self.check_interval = 5 * 60  # 5분 간격
        
        # 테스트 모드 설정
        self.test_mode = False
        self.test_datetime = None
        
        # 뉴스 타입 정의 (기존 형식과 동일)
        self.news_types = {
            'newyork': {
                'display_name': 'NEWYORK MARKET WATCH',
                'emoji': '🌆',
                'last_title': '',
                'last_time': '',
                'status': '발행 대기',
                'api_key': 'newyork_market'
            },
            'kospi': {
                'display_name': 'KOSPI CLOSE', 
                'emoji': '📈',
                'last_title': '',
                'last_time': '',
                'status': '발행 대기',
                'api_key': 'kospi_close'
            },
            'exchange': {
                'display_name': 'EXCHANGE RATE',
                'emoji': '💱',
                'last_title': '',
                'last_time': '',
                'status': '발행 대기',
                'api_key': 'exchange_rate'
            }
        }
        
        # 스케줄 작업 시간
        self.scheduled_times = {
            'morning_status': (6, 0),      # 06:00 - 아침 현재 상태 체크
            'morning_comparison': (6, 10), # 06:10 - 영업일 비교 분석
            'evening_summary': (18, 0),    # 18:00 - 저녁 일일 요약 리포트
            'evening_detail': (18, 10),    # 18:10 - 저녁 상세 일일 요약
            'evening_analysis': (18, 20)   # 18:20 - 저녁 고급 분석
        }
        self.executed_today = set()
        
        # API 클라이언트 초기화
        try:
            self.api_client = POSCO News 250808APIClient(API_CONFIG)
            self.log_message("✅ API 클라이언트 초기화 성공")
        except Exception as e:
            self.api_client = None
            self.log_message(f"⚠️ API 클라이언트 초기화 실패: {e}, 캐시 모드로 동작")
        
        # 신호 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 이전 상태 로드
        self.load_state()
        
        self.log_message("🏭 POSCO 메인 알림 시스템 초기화 완료")
    
    def signal_handler(self, signum, frame):
        """종료 신호 처리"""
        self.log_message(f"🛑 종료 신호 수신 (신호: {signum})")
        self.running = False
    
    def log_message(self, message):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
with_open(self.log_file,_'a',_encoding = 'utf-8') as f:
                f.write(log_entry + '/n')
        except Exception as e:
            print(f"[ERROR] 로그 파일 쓰기 실패: {e}")
    
    def load_state(self):
        """이전 상태 로드"""
        try:
            if os.path.exists(self.state_file):
with_open(self.state_file,_'r',_encoding = 'utf-8') as f:
                    state_data = json.load(f)
                
                for news_type in self.news_types:
                    if news_type in state_data:
                        self.news_types[news_type].update(state_data[news_type])
                
                self.log_message("📋 이전 상태 로드 완료")
            else:
                self.log_message("📋 새로운 상태 파일 생성")
                
            # 과거 데이터 캐시 로드
            self.load_historical_cache()
                
        except Exception as e:
            self.log_message(f"❌ 상태 로드 실패: {e}")
    
    def load_historical_cache(self):
        """과거 데이터 캐시 로드"""
        try:
            # 과거 데이터 캐시 파일 확인
            historical_cache_file = "../../POSCO News 250808_historical_cache.json"
            business_mapping_file = "../../posco_business_day_mapping.json"
            
            if os.path.exists(historical_cache_file):
with_open(historical_cache_file,_'r',_encoding = 'utf-8') as f:
                    self.historical_cache = json.load(f)
                self.log_message("📋 과거 데이터 캐시 로드 완료")
            else:
                self.historical_cache = {}
                self.log_message("⚠️ 과거 데이터 캐시 없음")
                
            if os.path.exists(business_mapping_file):
with_open(business_mapping_file,_'r',_encoding = 'utf-8') as f:
                    self.business_day_mapping = json.load(f)
                self.log_message("📋 영업일 매핑 로드 완료")
            else:
                self.business_day_mapping = {}
                self.log_message("⚠️ 영업일 매핑 없음")
                
        except Exception as e:
            self.log_message(f"❌ 과거 데이터 캐시 로드 오류: {e}")
            self.historical_cache = {}
            self.business_day_mapping = {}
    
    def format_time_string(self, time_str):
        """시간 문자열을 일관된 형식으로 변환"""
        if not time_str:
            return '시간 정보 없음'
        
        # 이미 올바른 형식인지 확인 (YYYY-MM-DD HH:MM:SS)
        if len(time_str) >= 16 and '-' in time_str and ':' in time_str:
            return time_str
        
        # YYYYMMDDHHMMSS 형식을 YYYY-MM-DD HH:MM:SS로 변환
        if len(time_str) >= 14 and time_str.isdigit():
            try:
                year = time_str[:4]
                month = time_str[4:6]
                day = time_str[6:8]
                hour = time_str[8:10]
                minute = time_str[10:12]
                second = time_str[12:14] if len(time_str) >= 14 else '00'
                return f"{year}-{month}-{day} {hour}:{minute}:{second}"
            except:
                pass
        
        # YYYYMMDD HHMMSS 형식 처리
        if ' ' in time_str:
            parts = time_str.split(' ')
            if len(parts) == 2:
                date_part = parts[0]
                time_part = parts[1]
                
                if len(date_part) == 8 and date_part.isdigit():
                    year = date_part[:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    
                    if len(time_part) >= 6 and time_part.isdigit():
                        hour = time_part[:2]
                        minute = time_part[2:4]
                        second = time_part[4:6] if len(time_part) >= 6 else '00'
                        return f"{year}-{month}-{day} {hour}:{minute}:{second}"
        
        return time_str

    def get_previous_business_day_data(self, news_type):
        """영업일 기준 직전 데이터 가져오기"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            
            # 영업일 매핑에서 직전 데이터 찾기
            if today in self.business_day_mapping:
                mapping_data = self.business_day_mapping[today]
                
                # 뉴스 타입별 매핑 확인
                type_mapping = {
                    'exchange': 'exchange',
                    'kospi': 'kospi', 
                    'newyork': 'newyork'
                }
                
                mapped_type = type_mapping.get(news_type)
                if mapped_type and mapped_type in mapping_data:
                    previous_info = mapping_data[mapped_type]
                    return {
                        'title': previous_info.get('previous_title', ''),
                        'time': self.format_time_string(previous_info.get('previous_time', ''))
                    }
            
            # 매핑이 없으면 과거 캐시에서 직접 찾기
            if hasattr(self, 'historical_cache') and 'historical_data' in self.historical_cache:
                # 최근 7일간 데이터에서 찾기
                for i in range(1, 8):
                    check_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                    
                    if check_date in self.historical_cache['historical_data']:
                        day_data = self.historical_cache['historical_data'][check_date]
                        
                        # 뉴스 타입별 데이터 확인
                        type_mapping = {
                            'exchange': 'exchange-rate',
                            'kospi': 'kospi-close',
                            'newyork': 'newyork-market-watch'
                        }
                        
                        api_type = type_mapping.get(news_type)
                        if api_type and 'data' in day_data and api_type in day_data['data']:
                            cached_data = day_data['data'][api_type]
                            if cached_data.get('title'):
                                time_str = cached_data.get('time', '00:00:00')
                                formatted_time = f"{check_date[:4]}-{check_date[4:6]}-{check_date[6:8]} {time_str}"
                                return {
                                    'title': cached_data['title'],
                                    'time': self.format_time_string(formatted_time)
                                }
            
            return None
            
        except Exception as e:
            self.log_message(f"❌ 직전 데이터 조회 오류: {e}")
            return None
    
    def generate_html_report(self):
        """HTML 통합 리포트 생성"""
        try:
            # 통합 리포트 빌더 사용
# REMOVED:             from Monitoring/POSCO_News_250808/integrated_report_builder.py import IntegratedReportBuilder
            
            builder = IntegratedReportBuilder()
            
            # 오늘 날짜로 리포트 생성
            today = datetime.now().strftime('%Y-%m-%d')
            reports = builder.generate_date_range_reports(start_date=today, end_date=today)
            
            if reports and len(reports) > 0:
                report_info = reports[0]
                report_path = report_info.get('file_path')
            else:
                report_path = None
            
            if report_path and os.path.exists(report_path):
                # GitHub Pages URL 생성 (실제 배포된 경우)
                filename = os.path.basename(report_path)
                github_url = f"https:/shuserker.github.io/infomax_api/Monitoring/POSCO News 250808_mini/reports/{filename}"
                
                self.log_message(f"✅ HTML 리포트 생성 완료: {filename}")
                return github_url
            else:
                self.log_message("⚠️ HTML 리포트 생성 실패")
                return None
                
        except ImportError:
            self.log_message("⚠️ 통합 리포트 빌더 모듈 없음")
            return None
        except Exception as e:
            self.log_message(f"❌ HTML 리포트 생성 오류: {e}")
            return None
    
    def save_state(self):
        """현재 상태 저장"""
        try:
with_open(self.state_file,_'w',_encoding = 'utf-8') as f:
json.dump(self.news_types,_f,_ensure_ascii = False, indent=2)
            
        except Exception as e:
            self.log_message(f"❌ 상태 저장 실패: {e}")
    
    def get_news_data(self, news_type):
        """뉴스 데이터 가져오기"""
        try:
            # API에서 데이터 가져오기 시도
            if self.api_client:
                # API 클라이언트로 최신 데이터 가져오기
                response = self.api_client.get_news_data()  # 최신 데이터 요청
                
                if response and isinstance(response, dict):
                    # 뉴스 타입 매핑
                    api_key_mapping = {
                        'newyork': 'newyork-market-watch',
                        'kospi': 'kospi-close', 
                        'exchange': 'exchange-rate'
                    }
                    
                    api_key = api_key_mapping.get(news_type)
                    if api_key and api_key in response:
                        data = response[api_key]
                        
                        # 시간 정보 포맷팅
                        date_str = data.get('date', '')
                        time_str = data.get('time', '')
                        
                        if date_str and time_str:
                            try:
                                if len(date_str) == 8:  # YYYYMMDD
                                    year = date_str[:4]
                                    month = date_str[4:6]
                                    day = date_str[6:8]
                                    
                                    if len(time_str) >= 4:  # HHMMSS 또는 HHMM
                                        if len(time_str) == 5:  # HMMSS 형태 (예: 61938)
                                            hour = time_str[0]
                                            minute = time_str[1:3]
                                            second = time_str[3:5]
                                        elif len(time_str) == 6:  # HHMMSS 형태
                                            hour = time_str[:2]
                                            minute = time_str[2:4]
                                            second = time_str[4:6]
                                        else:  # HHMM 형태
                                            hour = time_str[:2]
                                            minute = time_str[2:4]
                                            second = "00"
                                        
                                        # 시간 값 검증 및 보정
                                        hour = hour.zfill(2)
                                        if int(hour) > 23:
                                            hour = "06"  # 기본값으로 설정
                                        if int(minute) > 59:
                                            minute = "19"  # 기본값으로 설정
                                        if int(second) > 59:
                                            second = "38"  # 기본값으로 설정
                                            
                                        publish_time = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                                    else:
                                        publish_time = f"{year}-{month}-{day}"
                                else:
                                    publish_time = f"{date_str} {time_str}"
                            except:
                                publish_time = f"{date_str} {time_str}"
                        elif date_str:
                            publish_time = date_str
                        else:
                            publish_time = '시간 정보 없음'
                        
                        # API 데이터가 있고 제목이 있으면 반환
                        if data.get('title') and data.get('title').strip():
                            self.log_message(f"✅ {news_type} API 데이터 획득: {data.get('title')[:30]}...")
                            return {
                                'title': data.get('title', ''),
                                'publish_time': publish_time,
                                'content': data.get('content', ''),
                                'url': data.get('url', '')
                            }
                        else:
                            # API에서 빈 데이터가 온 경우 캐시로 넘어감
                            self.log_message(f"⚠️ {news_type} API 데이터 비어있음, 캐시 확인 중...")
            
            # API 실패 시 캐시에서 가져오기 (루트 폴더와 현재 폴더 모두 확인)
            cache_files = [
# REMOVED:                 '../../POSCO News 250808_cache.json',  # 루트 폴더
# REMOVED:                 '../POSCO News 250808_cache.json',     # 상위 폴더
# REMOVED:                 'POSCO News 250808_cache.json'         # 현재 폴더
            ]
            
            for cache_file in cache_files:
                if os.path.exists(cache_file):
                    self.log_message(f"📋 캐시 파일 발견: {cache_file}")
with_open(cache_file,_'r',_encoding = 'utf-8') as f:
                        cache_data = json.load(f)
                    
                    # 캐시 데이터 구조 확인
                    if 'data' in cache_data and isinstance(cache_data['data'], dict):
                        # 새로운 캐시 구조
                        news_data = cache_data['data']
                        
                        # 뉴스 타입 매핑
                        cache_key_mapping = {
                            'newyork': 'newyork-market-watch',
                            'kospi': 'kospi-close', 
                            'exchange': 'exchange-rate'
                        }
                        
                        cache_key = cache_key_mapping.get(news_type)
                        if cache_key and cache_key in news_data:
                            data = news_data[cache_key]
                            
                            # 제목이 있는지 확인
                            if not data.get('title') or not data.get('title').strip():
                                continue  # 빈 데이터면 다음 캐시 파일 확인
                            
                            # 시간 정보 포맷팅
                            date_str = data.get('date', '')
                            time_str = data.get('time', '')
                            
                            if date_str and time_str:
                                # 날짜와 시간을 조합하여 publish_time 생성
                                try:
                                    if len(date_str) == 8:  # YYYYMMDD
                                        year = date_str[:4]
                                        month = date_str[4:6]
                                        day = date_str[6:8]
                                        
                                        if len(time_str) >= 4:  # HHMMSS 또는 HHMM
                                            hour = time_str[:2]
                                            minute = time_str[2:4]
                                            second = time_str[4:6] if len(time_str) >= 6 else "00"
                                            publish_time = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                                        else:
                                            publish_time = f"{year}-{month}-{day}"
                                    else:
                                        publish_time = f"{date_str} {time_str}"
                                except:
                                    publish_time = f"{date_str} {time_str}"
                            else:
                                publish_time = '시간 정보 없음'
                            
                            # 오늘 날짜인지 확인
                            if self.is_today_news(publish_time):
                                return {
                                    'title': data.get('title', ''),
                                    'publish_time': publish_time,
                                    'content': data.get('content', ''),
                                    'url': data.get('url', '')
                                }
                            else:
                                # 오늘 날짜가 아니면 과거 데이터이므로 무시하고 계속 찾기
                                self.log_message(f"⚠️ {news_type} 캐시 데이터가 과거 데이터임: {publish_time}")
                                continue
                    
                    elif news_type in cache_data:
                        # 기존 캐시 구조
                        data = cache_data[news_type]
                        return {
                            'title': data.get('title', ''),
                            'publish_time': data.get('publish_time', ''),
                            'content': data.get('content', ''),
                            'url': data.get('url', '')
                        }
                    
                    break
            
            self.log_message(f"⚠️ {news_type} 캐시 데이터를 찾을 수 없습니다")
            return None
            
        except Exception as e:
            self.log_message(f"❌ {news_type} 데이터 가져오기 실패: {e}")
            return None
    
    def get_news_status_with_time_check(self, news_type, current_data):
        """뉴스 상태를 시간 기준으로 판단"""
        # 뉴스 타입별 예상 발행 시간
        expected_times = {
            'newyork': (6, 0, 7, 0),    # 06:00-07:00
            'kospi': (15, 30, 16, 0),   # 15:30-16:00  
            'exchange': (16, 0, 17, 0)  # 16:00-17:00
        }
        
        if news_type not in expected_times:
            return "⏳ 발행 대기", "발행 대기"
        
        # 현재 시간 (테스트 모드면 테스트 시간 사용)
        current_time = self.test_datetime if self.test_mode else datetime.now()
        
start_hour,_start_min,_end_hour,_end_min =  expected_times[news_type]
        expected_start = current_time.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
        expected_end = current_time.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
        
        # 현재 데이터가 있고 오늘 발행된 경우
        if current_data and current_data.get('title') and self.is_today_news(current_data.get('publish_time', '')):
            return "🟢 최신", "최신"
        
        # 현재 데이터가 없거나 과거 데이터인 경우
        if current_time < expected_start:
            # 예상 발행 시간 전
            return "⏳ 발행 전", "발행 대기"
        elif current_time <= expected_end:
            # 예상 발행 시간 범위 내
            return "⏳ 발행 대기", "발행 대기"
        else:
            # 예상 발행 시간 지남
            return "🔴 발행 지연", "발행 지연"

    def send_business_day_comparison(self):
        """영업일 비교 분석 알림 (첫 번째 캡쳐 형식)"""
        try:
            self.log_message("📊 영업일 비교 분석 알림 생성 중...")
            
            # 각 뉴스 타입별 데이터 수집
            comparison_data = {}
            for news_type, info in self.news_types.items():
                data = self.get_news_data(news_type)
                comparison_data[news_type] = {
                    'current_data': data,
                    'display_name': info['display_name'],
                    'last_title': info['last_title'],
                    'last_time': info['last_time']
                }
            
            # 메시지 구성
            message = "📊 영업일 비교 분석/n/n"
            
            for news_type, data in comparison_data.items():
                display_name = data['display_name']
                current = data['current_data']
                
                message += f"[{display_name}]/n"
                
                # 시간 기준 상태 판단
status_display,_status_value =  self.get_news_status_with_time_check(news_type, current)
                
                if current and current.get('title') and self.is_today_news(current.get('publish_time', '')):
                    # 오늘 발행된 최신 데이터
                    publish_time = current.get('publish_time', '시간 정보 없음')
                    title = current.get('title', '제목 없음')
                    
                    message += f"├ 현재: {publish_time} {status_display}/n"
                    message += f"└ 제목: {title}/n/n"
                    
                    # 상태 업데이트
                    self.news_types[news_type]['last_title'] = title
                    self.news_types[news_type]['last_time'] = publish_time
                    self.news_types[news_type]['status'] = status_value
                    
                else:
                    # 현재 데이터가 없거나 과거 데이터인 경우
                    message += f"├ 현재: {status_display}/n"
                    
                    # 과거 데이터 표시
                    if current and current.get('title'):
                        # API에서 가져온 과거 데이터
                        publish_time = current.get('publish_time', '시간 정보 없음')
                        title = current.get('title', '제목 없음')
                        message += f"├ 직전: {publish_time}/n"
                        message += f"└ 제목: {title}/n/n"
                        
                        self.news_types[news_type]['last_title'] = title
                        self.news_types[news_type]['last_time'] = publish_time
                    else:
                        # 캐시에서 직전 데이터 찾기
                        previous_data = self.get_previous_business_day_data(news_type)
                        
                        if previous_data:
                            message += f"├ 직전: 🔄 {previous_data['time']}/n"
                            message += f"└ 제목: {previous_data['title']}/n/n"
                            
                            self.news_types[news_type]['last_title'] = previous_data['title']
                            self.news_types[news_type]['last_time'] = previous_data['time']
                        elif data['last_time']:
                            formatted_time = self.format_time_string(data['last_time'])
                            message += f"├ 직전: 🔄 {formatted_time}/n"
                            message += f"└ 제목: {data['last_title']}/n/n"
                        else:
                            message += f"└ 직전: ❌ 데이터 없음/n/n"
                    
                    self.news_types[news_type]['status'] = status_value
            
            # 테스트 모드일 때 메시지 수정
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준/n/n" + message.strip()
                bot_name = "[TEST] POSCO News 250808 알림"
                text_title = "[TEST] 📊 영업일 비교 분석"
            else:
                bot_name = "POSCO News 250808 알림"
                text_title = "📊 영업일 비교 분석"
            
            # Dooray 알림 전송
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": text_title,
                "attachments": [{
                    "color": "#007bff",
                    "text": message.strip()
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 영업일 비교 분석 알림 전송 성공")
                self.save_state()
            else:
                self.log_message(f"❌ 영업일 비교 분석 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 영업일 비교 분석 알림 오류: {e}")
    
    def send_delay_notification(self, news_type, expected_time, actual_time, title):
        """지연 발행 알림 (두 번째 캡쳐 형식)"""
        try:
            display_name = self.news_types[news_type]['display_name']
            emoji = self.news_types[news_type]['emoji']
            
            # 지연 시간 계산
            expected_dt = datetime.strptime(expected_time, "%H:%M")
            actual_dt = datetime.strptime(actual_time, "%H:%M")
            delay_minutes = int((actual_dt - expected_dt).total_seconds() / 60)
            
            # 지연 정도에 따른 신호등 이모지
            if delay_minutes <= 15:
                delay_status = "🟡"  # 노랑불: 경미한 지연
            elif delay_minutes <= 60:
                delay_status = "🟠"  # 주황불: 중간 지연  
            else:
                delay_status = "🔴"  # 빨강불: 심각한 지연
            
            message = f"{delay_status} {display_name.lower()} 지연 발행/n/n"
            # 테스트 모드일 때는 테스트 날짜 사용, 아니면 현재 날짜 사용
            publish_date = self.test_datetime.strftime('%Y-%m-%d') if self.test_mode else datetime.now().strftime('%Y-%m-%d')
            message += f"📅 발행 시간: {publish_date} {actual_time}:00/n"
            message += f"📊 패턴 분석: ⏱️ {delay_minutes}분 지연 발행 ({actual_time})/n"
            message += f"⏰ 예상: {expected_time} → 실제: {actual_time}/n"
            message += f"📋 제목: {title}/n/n"
            message += f"🔔 지연 알림이 초기화되었습니다."
            
            # 테스트 모드일 때 메시지 수정
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준/n/n" + message
                bot_name = "[TEST] POSCO 뉴스 ⏰"
                text_title = f"[TEST] ⏰ {display_name.lower()} 지연 발행"
            else:
                bot_name = "POSCO 뉴스 ⏰"
                text_title = f"⏰ {display_name.lower()} 지연 발행"
            
            # Dooray 알림 전송
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": text_title,
                "attachments": [{
                    "color": "#ffc107",
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message(f"✅ {display_name} 지연 발행 알림 전송 성공")
            else:
                self.log_message(f"❌ {display_name} 지연 발행 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 지연 발행 알림 오류: {e}")
    
    def send_daily_integrated_report(self):
        """일일 통합 분석 리포트 (세 번째 캡쳐 형식)"""
        try:
            self.log_message("📊 일일 통합 분석 리포트 생성 중...")
            
            # 실제 HTML 리포트 생성
            report_url = self.generate_html_report()
            
            # 발행 현황 확인
            published_count = 0
            total_count = 3
            
            if report_url:
                message = f"📊 POSCO 뉴스 일일 통합 분석 리포트 | [📊 통합 리포트 보기]({report_url})/n/n"
            else:
                message = "📊 POSCO 뉴스 일일 통합 분석 리포트 | 📊 통합 리포트 보기/n/n"
            
            # 발행 현황 체크
            for news_type, info in self.news_types.items():
                if info['status'] == '최신':
published_count_+ =  1
            
            # 발행 현황에 신호등 이모지 적용
            if published_count == 0:
                status_emoji = "🔴"  # 빨강불: 발행 없음
                message += f"{status_emoji} 오늘의 뉴스 발행 현황/n"
                message += f"📊 뉴스 발행 부족 ({published_count}/{total_count})/n/n"
            elif published_count == total_count:
                status_emoji = "🟢"  # 초록불: 모든 뉴스 발행
                message += f"{status_emoji} 오늘의 뉴스 발행 현황/n"
                message += f"📊 뉴스 발행 완료 ({published_count}/{total_count})/n/n"
            else:
                status_emoji = "🟡"  # 노랑불: 일부 발행
                message += f"{status_emoji} 오늘의 뉴스 발행 현황/n"
                message += f"📊 뉴스 발행 진행 중 ({published_count}/{total_count})/n/n"
            
            # 각 뉴스별 상태 (시간 기준 상태 판단 적용)
            exchange_current = self.get_news_data('exchange')
            kospi_current = self.get_news_data('kospi')
            newyork_current = self.get_news_data('newyork')
            
exchange_status,__ =  self.get_news_status_with_time_check('exchange', exchange_current)
kospi_status,__ =  self.get_news_status_with_time_check('kospi', kospi_current)
newyork_status,__ =  self.get_news_status_with_time_check('newyork', newyork_current)
            
            message += f"💱 $₩ 서환마감: {exchange_status}/n"
            message += f"📈 📊 증시마감: {kospi_status}/n"
            message += f"🏙️ 뉴욕마켓워치: {newyork_status}/n/n"
            
            message += f"🎯 통합 분석 완료/n"
            message += f"📈 모든 발행된 뉴스를 종합하여 시장 분석, 투자 전략, 리스크 분석을 제공합니다."
            
            # 테스트 모드일 때 메시지 수정
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준/n/n" + message
                bot_name = "[TEST] POSCO 뉴스 📊"
                text_title = "[TEST] 📊 POSCO 뉴스 일일 통합 분석 리포트 | 📊 통합 리포트 보기"
            else:
                bot_name = "POSCO 뉴스 📊"
                text_title = "📊 POSCO 뉴스 일일 통합 분석 리포트 | 📊 통합 리포트 보기"
            
            # Dooray 알림 전송
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": text_title,
                "attachments": [{
                    "color": "#28a745" if published_count > 0 else "#dc3545",
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 일일 통합 분석 리포트 알림 전송 성공")
            else:
                self.log_message(f"❌ 일일 통합 분석 리포트 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 일일 통합 분석 리포트 알림 오류: {e}")
    
    def send_timely_publication_notification(self, news_type, publish_time, title):
        """정시 발행 알림 (네 번째 캡쳐 형식)"""
        try:
            display_name = self.news_types[news_type]['display_name']
            
            message = f"🟢 {display_name.lower()} 정시 발행/n/n"
            message += f"📅 발행 시간: {publish_time}/n"
            message += f"📊 패턴 분석: ✅ 정시 발행 ({publish_time.split()[1][:5]})/n"
            message += f"⏰ 예상: 06:00-07:00 → 실제: {publish_time.split()[1][:5]}/n"
            message += f"📋 제목: {title}/n/n"
            message += f"🔔 지연 알림이 초기화되었습니다."
            
            # 테스트 모드일 때 메시지 수정
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준/n/n" + message
                bot_name = "[TEST] POSCO 뉴스 ✅"
                text_title = f"[TEST] ✅ {display_name.lower()} 정시 발행"
            else:
                bot_name = "POSCO 뉴스 ✅"
                text_title = f"✅ {display_name.lower()} 정시 발행"
            
            # Dooray 알림 전송
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": text_title,
                "attachments": [{
                    "color": "#28a745",
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message(f"✅ {display_name} 정시 발행 알림 전송 성공")
            else:
                self.log_message(f"❌ {display_name} 정시 발행 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 정시 발행 알림 오류: {e}")
    
    def send_data_update_status(self):
        """데이터 갱신 상태 알림 (동적 제목)"""
        try:
            self.log_message("🔔 데이터 갱신 상태 알림 생성 중...")
            
            # 실시간으로 최신 데이터 확인
            updated_count = 0
            total_count = 3
            status_details = []
            
            for news_type, info in self.news_types.items():
                display_name = info['display_name']
                
                # 실시간 데이터 확인
                current_data = self.get_news_data(news_type)
                
                # 시간 기준 상태 판단
status_display,_status_value =  self.get_news_status_with_time_check(news_type, current_data)
                
                if current_data and current_data.get('title') and self.is_today_news(current_data.get('publish_time', '')):
                    # 오늘 발행된 최신 데이터
updated_count_+ =  1
                    publish_time = current_data.get('publish_time', '')
                    status_details.append({
                        'name': display_name,
                        'status': status_display,
                        'time': publish_time,
                        'title': current_data.get('title', '')
                    })
                    
                    # 상태 업데이트
                    info['status'] = status_value
                    info['last_title'] = current_data.get('title', '')
                    info['last_time'] = publish_time
                    
                else:
                    # 현재 데이터가 없거나 과거 데이터인 경우
                    if current_data and current_data.get('title'):
                        # 과거 데이터가 있는 경우
                        publish_time = current_data.get('publish_time', '')
                        status_details.append({
                            'name': display_name,
                            'status': status_display,
                            'time': f"과거 데이터: {publish_time}",
                            'title': f"[과거] {current_data.get('title', '')}"
                        })
                    else:
                        # 데이터가 아예 없는 경우
                        status_details.append({
                            'name': display_name,
                            'status': status_display,
                            'time': '데이터 없음',
                            'title': '제목 없음'
                        })
                    
                    info['status'] = status_value
            
            # 동적 제목 생성
            if updated_count == 0:
                alert_title = "🔔 데이터 갱신 없음"
                alert_emoji = "🔔"
                color = "#6c757d"
            elif updated_count == total_count:
                alert_title = "✅ 모든 데이터 최신"
                alert_emoji = "✅"
                color = "#28a745"
            else:
                alert_title = f"📊 데이터 부분 갱신 ({updated_count}/{total_count})"
                alert_emoji = "📊"
                color = "#ffc107"
            
            # 메시지 구성
            message = f"{alert_emoji} {alert_title.split(' ', 1)[1]}/n/n"
            
            for detail in status_details:
                message += f"├ {detail['name']}/n"
                message += f"├ 상태: {detail['status']}/n"
                message += f"├ 시간: {detail['time']}/n"
                message += f"└ 제목: {detail['title']}/n/n"
            
            message += f"🔍 최종 확인: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 테스트 모드일 때 메시지 수정
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준/n/n" + message
                bot_name = "[TEST] POSCO 뉴스 🔔"
                text_title = f"[TEST] {alert_title}"
            else:
                bot_name = "POSCO 뉴스 🔔"
                text_title = alert_title
            
            # Dooray 알림 전송
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": text_title,
                "attachments": [{
                    "color": color,
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message(f"✅ 데이터 갱신 상태 알림 전송 성공: {alert_title}")
                self.save_state()  # 상태 저장
            else:
                self.log_message(f"❌ 데이터 갱신 상태 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 데이터 갱신 상태 알림 오류: {e}")
    
    def check_scheduled_tasks(self):
        """스케줄 작업 확인 및 실행"""
        now = datetime.now()
        current_time = (now.hour, now.minute)
        today_key = now.strftime("%Y-%m-%d")
        
        # 매일 자정에 실행된 작업 목록 초기화
        if now.hour == 0 and now.minute == 0:
            self.executed_today.clear()
            self.log_message("🔄 일일 스케줄 작업 목록 초기화")
        
        for task_name, scheduled_time in self.scheduled_times.items():
            task_key = f"{today_key}_{task_name}"
            
            if (current_time == scheduled_time and 
                task_key not in self.executed_today):
                
                self.log_message(f"⏰ 스케줄 작업 실행: {task_name} ({scheduled_time[0]:02d}:{scheduled_time[1]:02d})")
                self.execute_scheduled_task(task_name)
                self.executed_today.add(task_key)
    
    def execute_scheduled_task(self, task_name):
        """스케줄 작업 실행"""
        try:
            if task_name == 'morning_status':
                self.send_data_update_status()
            elif task_name == 'morning_comparison':
                self.send_business_day_comparison()
            elif task_name == 'evening_summary':
                self.send_daily_integrated_report()
            elif task_name == 'evening_detail':
                self.send_data_update_status()
            elif task_name == 'evening_analysis':
                self.send_business_day_comparison()
                
        except Exception as e:
            self.log_message(f"❌ 스케줄 작업 실행 오류 ({task_name}): {e}")
    
    def check_for_new_news(self):
        """새로운 뉴스 확인 및 실시간 알림 발송"""
        new_news_found = False
        current_time = datetime.now()
        
        for news_type, info in self.news_types.items():
            try:
                # 최신 데이터 가져오기
                data = self.get_news_data(news_type)
                
                if data and data.get('title'):
                    current_title = data['title'].strip()
                    current_publish_time = data.get('publish_time', '')
                    
                    # 새로운 뉴스인지 확인 (제목과 발행시간 모두 체크)
                    if (info['last_title'] != current_title and current_title and
info['last_time']_! =  current_publish_time):
                        
                        self.log_message(f"🆕 새 뉴스 발견: {info['display_name']} - {current_title[:50]}...")
                        
                        # 오늘 발행된 뉴스만 알림 발송
                        if self.is_today_news(current_publish_time):
                            self.analyze_and_send_publication_alert(news_type, data)
                        else:
                            self.log_message(f"⚠️ 과거 데이터이므로 알림 생략: {current_publish_time}")
                        
                        # 상태 업데이트
                        info['last_title'] = current_title
                        info['last_time'] = current_publish_time
                        info['status'] = '최신' if self.is_today_news(current_publish_time) else '과거 데이터'
                        info['last_check'] = current_time.isoformat()
                        
                        new_news_found = True
                    else:
                        # 동일한 뉴스 - 체크 시간만 업데이트
                        info['last_check'] = current_time.isoformat()
                        
                else:
                    info['last_check'] = current_time.isoformat()
                    
            except Exception as e:
                self.log_message(f"❌ {info['display_name']} 체크 실패: {e}")
                info['last_check'] = current_time.isoformat()
        
        # 새 뉴스가 있으면 상태 저장
        if new_news_found:
            self.save_state()
        
        return new_news_found
    
    def is_today_news(self, publish_time_str):
        """오늘 발행된 뉴스인지 확인"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            return today in publish_time_str
        except:
            return False
    
    def analyze_and_send_publication_alert(self, news_type, data):
        """발행 패턴 분석 후 적절한 알림 발송 (오늘 뉴스만)"""
        try:
            publish_time_str = data.get('publish_time', '')
            title = data.get('title', '')
            
            if not publish_time_str or not title:
                return
            
            # 발행 시간 파싱
            try:
                if len(publish_time_str) >= 16:  # YYYY-MM-DD HH:MM 형식
                    publish_time = datetime.strptime(publish_time_str[:16], '%Y-%m-%d %H:%M')
                else:
                    return
            except:
                return
            
            # 뉴스 타입별 예상 발행 시간
            expected_times = {
                'newyork': (6, 0, 7, 0),    # 06:00-07:00
                'kospi': (15, 30, 16, 0),   # 15:30-16:00  
                'exchange': (16, 0, 17, 0)  # 16:00-17:00
            }
            
            if news_type not in expected_times:
                return
                
start_hour,_start_min,_end_hour,_end_min =  expected_times[news_type]
            
            # 예상 시간 범위 생성
            expected_start = publish_time.replace(hour=start_hour, minute=start_min, second=0)
            expected_end = publish_time.replace(hour=end_hour, minute=end_min, second=0)
            
            # 발행 패턴 분석
            if expected_start <= publish_time <= expected_end:
                # 정시 발행
                self.send_timely_publication_notification(news_type, publish_time_str, title)
            elif publish_time > expected_end:
                # 지연 발행
                expected_time = f"{start_hour:02d}:{start_min:02d}"
                actual_time = f"{publish_time.hour:02d}:{publish_time.minute:02d}"
                self.send_delay_notification(news_type, expected_time, actual_time, title)
            else:
                # 조기 발행 (일반 알림)
                self.log_message(f"📰 {self.news_types[news_type]['display_name']} 조기 발행: {title[:30]}...")
                
        except Exception as e:
            self.log_message(f"❌ 발행 패턴 분석 오류: {e}")
    
    def send_shutdown_notification(self):
        """시스템 종료 알림 전송"""
        try:
            end_time = datetime.now()
            
            message = f"🛑 POSCO 메인 알림 시스템 종료/n/n"
            message += f"📅 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"🔄 시스템이 정상적으로 종료되었습니다./n/n"
            message += f"📊 종료 전 상태:/n"
            
            # 각 뉴스 타입별 마지막 상태 표시
            for news_type, info in self.news_types.items():
                status_emoji = "🟢" if info['status'] == '최신' else "⏳"
                message += f"├ {info['display_name']}: {status_emoji} {info['status']}/n"
            
            message += f"/n💡 시스템을 다시 시작하려면 제어센터를 사용하세요."
            
            # 테스트 모드일 때 메시지 수정
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준/n/n" + message
                bot_name = "[TEST] POSCO 시스템 🛑"
                text_title = "[TEST] 🛑 POSCO 메인 알림 시스템 종료"
            else:
                bot_name = "POSCO 시스템 🛑"
                text_title = "🛑 POSCO 메인 알림 시스템 종료"
            
            # Dooray 알림 전송
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": text_title,
                "attachments": [{
                    "color": "#dc3545",  # 빨간색 (종료)
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 시스템 종료 알림 전송 성공")
            else:
                self.log_message(f"❌ 시스템 종료 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 시스템 종료 알림 오류: {e}")

    def send_startup_notification(self, start_time):
        """시스템 시작 알림 전송"""
        try:
            message = f"🚀 POSCO 메인 알림 시스템 시작/n/n"
            message += f"📅 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}/n"
            message += f"🛡️ 24시간 모니터링 모드 활성화/n"
            message += f"📊 실시간 뉴스 체크: 1분 간격/n"
            message += f"🔔 스케줄 알림: 아침 6시, 저녁 6시/n"
            message += f"📈 5가지 BOT 타입 알림 제공/n"
            message += f"⚙️ 영업일 비교, 지연발행, 통합리포트, 정시발행, 데이터상태/n/n"
            message += f"🎯 모니터링 대상:/n"
            message += f"├ 💱 서환마감 (16:00-17:00)/n"
            message += f"├ 📈 증시마감 (15:30-16:00)/n"
            message += f"└ 🏙️ 뉴욕마켓워치 (06:00-07:00)/n/n"
            message += f"🔄 시스템이 정상적으로 시작되었습니다."
            
            # 테스트 모드일 때 메시지 수정
            if self.test_mode:
                test_time_str = self.test_datetime.strftime('%Y-%m-%d %H:%M')
                message = f"🧪 [TEST] {test_time_str} 기준/n/n" + message
                bot_name = "[TEST] POSCO 시스템 🚀"
                text_title = "[TEST] 🚀 POSCO 메인 알림 시스템 시작"
            else:
                bot_name = "POSCO 시스템 🚀"
                text_title = "🚀 POSCO 메인 알림 시스템 시작"
            
            # Dooray 알림 전송
            payload = {
                "botName": bot_name,
                "botIconImage": BOT_PROFILE_IMAGE_URL,
                "text": text_title,
                "attachments": [{
                    "color": "#28a745",  # 초록색 (성공)
                    "text": message
                }]
            }
            
            response = requests.post(
                DOORAY_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_message("✅ 시스템 시작 알림 전송 성공")
            else:
                self.log_message(f"❌ 시스템 시작 알림 전송 실패: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ 시스템 시작 알림 오류: {e}")

    def run(self):
        """메인 알림 루프"""
        start_time = datetime.now()
        
        self.log_message("🏭 POSCO 메인 알림 시스템 시작")
        self.log_message(f"📅 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message("📊 5가지 BOT 타입 알림 제공")
        self.log_message("🛑 종료하려면 Ctrl+C를 누르세요")
        
        # 시작 알림 전송
        self.send_startup_notification(start_time)
        
        # 메인 루프
        while self.running:
            try:
                current_time = datetime.now()
                
                # 스케줄 작업 확인
                self.check_scheduled_tasks()
                
                # 실시간 뉴스 확인 (1분마다)
                if current_time.second == 0:
                    self.log_message("🔍 실시간 뉴스 확인 중...")
                    self.check_for_new_news()
                
                # 30초 대기 (더 빠른 응답)
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.log_message("🛑 사용자에 의한 종료 요청")
                break
            except Exception as e:
                self.log_message(f"❌ 메인 알림 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기 후 재시도
        
        # 종료 처리
        self.log_message("🛑 POSCO 메인 알림 시스템 종료 중...")
        self.send_shutdown_notification()
        self.save_state()
        self.log_message("✅ POSCO 메인 알림 시스템 종료 완료")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='POSCO 메인 알림 시스템')
parser.add_argument('--test',_action = 'store_true', help='테스트 모드 (한 번만 실행)')
parser.add_argument('--test-type',_choices = ['business', 'delay', 'report', 'timely', 'status', 'gitpage', 'all'], 
                       help='테스트할 알림 타입 (business: 영업일비교, delay: 지연발행, report: 통합리포트, timely: 정시발행, status: 데이터상태, gitpage: Git Pages 리포트, all: 전체)')
parser.add_argument('--test-date',_help = '테스트 날짜 (YYYY-MM-DD 형식)')
parser.add_argument('--test-time',_help = '테스트 시간 (HH:MM 형식)')
parser.add_argument('--debug',_action = 'store_true', help='디버그 모드 (상세 로그 출력)')
parser.add_argument('--check-now',_action = 'store_true', help='즉시 뉴스 체크 실행')
    args = parser.parse_args()
    
    print("🏭 POSCO 메인 알림 시스템 v1.0")
    print("=" * 60)
    
    notifier = PoscoMainNotifier()
    
    if args.test:
        print("🧪 테스트 모드 실행")
        return test_mode(notifier, args.test_type, args.test_date, args.test_time)
    else:
        print("🔄 24시간 모니터링 모드")
        notifier.run()
    
    return 0

def test_git_pages_report(notifier, test_datetime):
    """Git Pages 리포트 생성 테스트"""
    try:
        print("📊 Git Pages 통합 리포트 생성 중...")
        
        # 리포트 생성 전 상태 확인
        print("🔍 리포트 생성 환경 체크:")
        
        # integrated_report_builder 모듈 확인
        try:
# REMOVED:             from Monitoring/POSCO_News_250808/integrated_report_builder.py import IntegratedReportBuilder
            print("├ ✅ integrated_report_builder 모듈 로드 성공")
        except ImportError:
            print("├ ❌ integrated_report_builder 모듈 로드 실패")
            return
        
        # Git 상태 확인
        import subprocess
        try:
            git_status = subprocess.run(['git', 'status', '--porcelain'], 
                                      capture_output=True, text=True, cwd='.')
            if git_status.stdout.strip():
                print("├ ⚠️ Git 작업 디렉토리에 변경사항 있음 (배포 제한 가능)")
            else:
                print("├ ✅ Git 작업 디렉토리 깨끗함")
        except:
            print("├ ⚠️ Git 상태 확인 불가")
        
        print("└ 🚀 리포트 생성 시작.../n")
        
        # HTML 리포트 생성
        report_url = notifier.generate_html_report()
        
        print("/n📊 리포트 생성 결과:")
        if report_url:
            print(f"✅ 리포트 생성 성공!")
            print(f"🔗 리포트 URL: {report_url}")
            
            # URL 분석
            if "shuserker.github.io" in report_url:
                print("✅ Git Pages URL 형식 확인됨")
                
                # 파일명에서 정보 추출
                import verify_folder_reorganization.py
                filename_match = re.search(r'naming_verification_report_20250809_171232.html', report_url)
                if filename_match:
                    report_date = filename_match.group(1)
                    report_time = filename_match.group(2)
                    formatted_date = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}"
                    formatted_time = f"{report_time[:2]}:{report_time[2:4]}:{report_time[4:6]}"
                    print(f"📅 리포트 생성: {formatted_date} {formatted_time}")
                
                # 접근성 테스트 (간단한 HTTP 요청)
                try:
                    import requests
                    response = requests.head(report_url, timeout=10)
                    if response.status_code == 200:
                        print("✅ 리포트 URL 접근 가능")
                    else:
                        print(f"⚠️ 리포트 URL 접근 불가 (HTTP {response.status_code})")
                except:
                    print("⚠️ 리포트 URL 접근성 테스트 실패 (네트워크 또는 배포 지연)")
                    
            else:
                print("⚠️ 예상과 다른 URL 형식")
                
        else:
            print("❌ 리포트 생성 실패")
            print("⚠️ generate_html_report() 함수에서 None 반환")
            
        # Git Pages 기능 상세 정보
        print("/n📋 Git Pages 리포트 시스템 정보:")
        print("├ 📊 통합 리포트 빌더: 뉴스 데이터 종합 분석")
        print("├ 🌐 GitHub Pages: 웹 접근 가능한 HTML 리포트")
        print("├ 📈 시각화: 차트 및 그래프로 데이터 표현")
        print("├ 📚 히스토리: 과거 리포트 아카이브 관리")
        print("├ 🔄 자동 배포: Git 브랜치 전환을 통한 배포")
        print("└ 📱 반응형: 모바일/데스크톱 호환 디자인")
        
        # 배포 상태 분석
        print("/n🚀 배포 상태 분석:")
        if "GitHub 배포 실패" in str(report_url) or not report_url:
            print("├ ⚠️ Git 브랜치 전환 실패로 인한 배포 제한")
            print("├ 💡 해결방법: git stash 또는 commit 후 재시도")
            print("└ 📝 로컬 HTML 파일은 정상 생성됨")
        else:
            print("├ ✅ 리포트 생성 및 URL 제공 완료")
            print("└ 🌐 웹에서 접근 가능한 상태")
        
    except ImportError as e:
        print(f"❌ 모듈 임포트 오류: {e}")
        print("⚠️ integrated_report_builder 모듈 설치 또는 경로 확인 필요")
    except Exception as e:
        print(f"❌ Git Pages 리포트 테스트 오류: {e}")
        print("⚠️ 리포트 생성 시스템에 문제가 발생했습니다")

def test_mode(notifier, test_type=None, test_date=None, test_time=None):
    """테스트 모드 실행"""
    print(f"🧪 테스트 모드: {test_type or 'all'}")
    print("=" * 40)
    
    # 테스트 날짜/시간 입력받기
    if not test_date:
        test_date = input("/n📅 테스트 날짜를 입력하세요 (YYYY-MM-DD, 엔터시 오늘): ").strip()
        if not test_date:
            test_date = datetime.now().strftime('%Y-%m-%d')
    
    if not test_time:
        test_time = input("🕐 테스트 시간을 입력하세요 (HH:MM, 엔터시 현재시간): ").strip()
        if not test_time:
            test_time = datetime.now().strftime('%H:%M')
    
    # 날짜/시간 검증
    try:
        test_datetime = datetime.strptime(f"{test_date} {test_time}", '%Y-%m-%d %H:%M')
        print(f"/n🎯 테스트 기준 시점: {test_datetime.strftime('%Y년 %m월 %d일 %H시 %M분')}")
        print("📝 모든 알림에 [TEST] 태그가 추가됩니다.")
        print("=" * 50)
    except ValueError as e:
        print(f"❌ 날짜/시간 형식 오류: {e}")
        return 1
    
    # 테스트 모드 설정
    notifier.test_mode = True
    notifier.test_datetime = test_datetime
    
    try:
        if test_type == 'business' or test_type == 'all':
            print("/n1️⃣ 영업일 비교 분석 테스트")
            notifier.send_business_day_comparison()
            
        if test_type == 'delay' or test_type == 'all':
            print("/n2️⃣ 지연 발행 알림 테스트")
            # 현실적인 지연 시나리오 생성
            test_hour = test_datetime.hour
            
            if test_hour < 8:  # 오전 8시 이전이면 뉴욕 마켓워치 지연 시뮬레이션
                expected_time = '06:30'
                actual_time = test_datetime.strftime('%H:%M')
                news_type = 'newyork'
                title = '[뉴욕마켓워치] 테스트 제목'
            elif test_hour >= 16:  # 오후 4시 이후면 코스피 지연 시뮬레이션
                expected_time = '15:30'
                actual_time = test_datetime.strftime('%H:%M')
                news_type = 'kospi'
                title = '[증시-마감] 테스트 제목'
            else:  # 그 외 시간대는 가상의 지연 시나리오 (16:00 기준)
                expected_time = '15:30'
                # 16시 이후로 가정하여 지연 시뮬레이션
                virtual_delay_time = datetime.strptime('16:00', '%H:%M')
                actual_time = virtual_delay_time.strftime('%H:%M')
                news_type = 'kospi'
                title = '[증시-마감] 테스트 제목 (가상 시나리오)'
            
            notifier.send_delay_notification(news_type, expected_time, actual_time, title)
            
        if test_type == 'report' or test_type == 'all':
            print("/n3️⃣ 일일 통합 분석 리포트 테스트")
            notifier.send_daily_integrated_report()
            
        if test_type == 'timely' or test_type == 'all':
            print("/n4️⃣ 정시 발행 알림 테스트")
            test_publish_time = f"{test_date} {test_time}:00"
            notifier.send_timely_publication_notification('newyork', test_publish_time, '[뉴욕마켓워치] 테스트 제목')
            
        if test_type == 'status' or test_type == 'all':
            print("/n5️⃣ 데이터 갱신 상태 테스트")
            notifier.send_data_update_status()
            
        if test_type == 'gitpage' or test_type == 'all':
            print("/n6️⃣ Git Pages 리포트 생성 테스트")
            test_git_pages_report(notifier, test_datetime)
            
        print("/n✅ 테스트 완료!")
        return 0
        
    except Exception as e:
        print(f"/n❌ 테스트 오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())