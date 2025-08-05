#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 과거 데이터 수집기

7월 25일부터 현재까지의 모든 뉴스 데이터를 수집하여
캐시에 저장하고 알림에서 활용할 수 있도록 합니다.

주요 기능:
- 날짜별 API 데이터 수집
- 캐시 파일 업데이트
- 영업일 기준 데이터 정리
- 직전 데이터 매핑

작성자: AI Assistant
최종 수정: 2025-08-05
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core import PoscoNewsAPIClient
    from config import API_CONFIG
except ImportError as e:
    print(f"[WARNING] 일부 모듈을 불러올 수 없습니다: {e}")
    API_CONFIG = {
        "url": "https://dev-global-api.einfomax.co.kr/apis/posco/news",
        "user": "infomax",
        "password": "infomax!",
        "timeout": 10
    }

class HistoricalDataCollector:
    """
    과거 데이터 수집기 클래스
    """
    
    def __init__(self):
        """초기화"""
        self.api_config = API_CONFIG
        self.cache_file = "../../posco_news_historical_cache.json"
        self.collected_data = {}
        
        print("📊 POSCO 과거 데이터 수집기 초기화")
    
    def get_api_data_for_date(self, date_str):
        """특정 날짜의 API 데이터 조회"""
        try:
            print(f"📅 {date_str} 데이터 조회 중...")
            
            params = {'date': date_str}
            
            response = requests.get(
                self.api_config['url'],
                auth=HTTPBasicAuth(self.api_config['user'], self.api_config['password']),
                params=params,
                timeout=self.api_config['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 데이터 유효성 확인
                valid_count = 0
                for news_type, news_data in data.items():
                    if news_data.get('title'):
                        valid_count += 1
                
                print(f"  ✅ 성공: {valid_count}/3 뉴스 데이터 획득")
                return data
            else:
                print(f"  ❌ API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ 조회 실패: {e}")
            return None
    
    def collect_historical_data(self, start_date_str, end_date_str):
        """기간별 과거 데이터 수집"""
        try:
            start_date = datetime.strptime(start_date_str, '%Y%m%d')
            end_date = datetime.strptime(end_date_str, '%Y%m%d')
            
            print(f"🔍 데이터 수집 기간: {start_date_str} ~ {end_date_str}")
            print()
            
            current_date = start_date
            total_days = (end_date - start_date).days + 1
            collected_days = 0
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y%m%d')
                
                # API에서 데이터 조회
                data = self.get_api_data_for_date(date_str)
                
                if data:
                    self.collected_data[date_str] = {
                        'date': date_str,
                        'data': data,
                        'collected_at': datetime.now().isoformat()
                    }
                    collected_days += 1
                
                current_date += timedelta(days=1)
            
            print()
            print(f"📊 수집 완료: {collected_days}/{total_days}일")
            return collected_days > 0
            
        except Exception as e:
            print(f"❌ 데이터 수집 오류: {e}")
            return False
    
    def save_to_cache(self):
        """수집된 데이터를 캐시 파일에 저장"""
        try:
            cache_data = {
                'historical_data': self.collected_data,
                'last_updated': datetime.now().isoformat(),
                'total_dates': len(self.collected_data)
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 캐시 파일 저장 완료: {self.cache_file}")
            print(f"📊 총 {len(self.collected_data)}일 데이터 저장")
            return True
            
        except Exception as e:
            print(f"❌ 캐시 저장 실패: {e}")
            return False
    
    def find_previous_business_day_data(self, target_date_str, news_type):
        """특정 날짜 이전의 영업일 데이터 찾기"""
        try:
            target_date = datetime.strptime(target_date_str, '%Y%m%d')
            
            # 최대 10일 전까지 검색
            for i in range(1, 11):
                check_date = target_date - timedelta(days=i)
                check_date_str = check_date.strftime('%Y%m%d')
                
                if check_date_str in self.collected_data:
                    data = self.collected_data[check_date_str]['data']
                    
                    # 뉴스 타입 매핑
                    api_key_mapping = {
                        'newyork': 'newyork-market-watch',
                        'kospi': 'kospi-close', 
                        'exchange': 'exchange-rate'
                    }
                    
                    api_key = api_key_mapping.get(news_type)
                    if api_key and api_key in data and data[api_key].get('title'):
                        return {
                            'date': check_date_str,
                            'data': data[api_key]
                        }
            
            return None
            
        except Exception as e:
            print(f"❌ 직전 데이터 검색 오류: {e}")
            return None
    
    def generate_business_day_mapping(self):
        """영업일 기준 직전 데이터 매핑 생성"""
        try:
            print("🔍 영업일 기준 직전 데이터 매핑 생성 중...")
            
            mapping = {}
            
            for date_str in sorted(self.collected_data.keys()):
                mapping[date_str] = {}
                
                for news_type in ['newyork', 'kospi', 'exchange']:
                    previous_data = self.find_previous_business_day_data(date_str, news_type)
                    
                    if previous_data:
                        mapping[date_str][news_type] = {
                            'previous_date': previous_data['date'],
                            'previous_title': previous_data['data'].get('title', ''),
                            'previous_time': f"{previous_data['date'][:4]}-{previous_data['date'][4:6]}-{previous_data['date'][6:8]} {previous_data['data'].get('time', '')}"
                        }
            
            # 매핑 데이터 저장
            mapping_file = "../../posco_business_day_mapping.json"
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            
            print(f"💾 영업일 매핑 저장 완료: {mapping_file}")
            return True
            
        except Exception as e:
            print(f"❌ 매핑 생성 실패: {e}")
            return False
    
    def run_collection(self):
        """전체 수집 프로세스 실행"""
        print("=" * 60)
        print("📊 POSCO 과거 데이터 수집 시작")
        print("=" * 60)
        
        # 7월 25일부터 오늘까지 수집
        start_date = "20250725"
        end_date = datetime.now().strftime('%Y%m%d')
        
        # 1. 과거 데이터 수집
        if self.collect_historical_data(start_date, end_date):
            print("✅ 과거 데이터 수집 완료")
        else:
            print("❌ 과거 데이터 수집 실패")
            return False
        
        # 2. 캐시 파일 저장
        if self.save_to_cache():
            print("✅ 캐시 파일 저장 완료")
        else:
            print("❌ 캐시 파일 저장 실패")
            return False
        
        # 3. 영업일 매핑 생성
        if self.generate_business_day_mapping():
            print("✅ 영업일 매핑 생성 완료")
        else:
            print("❌ 영업일 매핑 생성 실패")
            return False
        
        print()
        print("🎉 모든 과거 데이터 수집 및 처리 완료!")
        print()
        print("📋 생성된 파일들:")
        print(f"  • {self.cache_file} - 과거 데이터 캐시")
        print(f"  • ../../posco_business_day_mapping.json - 영업일 매핑")
        
        return True

def main():
    """메인 함수"""
    collector = HistoricalDataCollector()
    
    try:
        success = collector.run_collection()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의한 중단")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())