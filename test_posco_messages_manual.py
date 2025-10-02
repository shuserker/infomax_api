#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포스코 메인 알림 시스템 수동 테스트
2025-08-06 19:00 기준 모든 메시지 타입 테스트
"""

import sys
import os
from datetime import datetime

# 프로젝트 루트 추가
sys.path.insert(0, '.')

try:
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.scripts.posco_main_notifier import PoscoMainNotifier
    from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.webhook_sender import MessagePriority
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

class ManualTestNotifier(PoscoMainNotifier):
    """수동 테스트용 포스코 알림 시스템"""
    
    def __init__(self):
        super().__init__()
        # 테스트 모드 활성화
        self.test_mode = True
        self.test_datetime = datetime(2025, 8, 6, 19, 0, 0)  # 2025-08-06 19:00
        
        print(f"🧪 테스트 모드 활성화: {self.test_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def create_test_news_data(self):
        """테스트용 뉴스 데이터 생성"""
        return {
            'newyork-market': {
                'title': '[뉴욕마켓워치] 미국 증시 상승 마감, 기술주 강세',
                'date': '20250806',
                'time': '190000',
                'content': '미국 주요 지수가 기술주 강세에 힘입어 상승 마감했습니다.'
            },
            'kospi-close': {
                'title': '[증시마감] 코스피 2,650선 회복, 외국인 순매수',
                'date': '20250806',
                'time': '153000',
                'content': '코스피가 외국인 순매수에 힘입어 2,650선을 회복했습니다.'
            },
            'exchange-rate': {
                'title': '[서환마감] 원/달러 환율 1,320원대 중반',
                'date': '20250806',
                'time': '154500',
                'content': '원/달러 환율이 1,320원대 중반에서 거래를 마감했습니다.'
            }
        }
    
    def test_startup_notification(self):
        """시작 알림 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트 1: 시작 알림")
        print("="*60)
        
        try:
            self.send_startup_notification()
            print("✅ 시작 알림 테스트 완료")
        except Exception as e:
            print(f"❌ 시작 알림 테스트 실패: {e}")
    
    def test_news_publication_alerts(self):
        """뉴스 발행 알림 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트 2: 뉴스 발행 알림")
        print("="*60)
        
        test_data = self.create_test_news_data()
        
        for news_type, news_data in test_data.items():
            try:
                print(f"\n📰 {news_type} 발행 알림 테스트...")
                
                # 뉴스 타입 매핑
                type_mapping = {
                    'newyork-market': 'newyork',
                    'kospi-close': 'kospi', 
                    'exchange-rate': 'exchange'
                }
                
                mapped_type = type_mapping.get(news_type, news_type)
                if mapped_type in self.news_types:
                    self.send_news_publication_alert(mapped_type, news_data)
                    print(f"✅ {news_type} 발행 알림 전송 완료")
                else:
                    print(f"⚠️ {news_type} 타입 매핑 실패")
                    
            except Exception as e:
                print(f"❌ {news_type} 발행 알림 실패: {e}")
    
    def test_delay_notifications(self):
        """지연 발행 알림 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트 3: 지연 발행 알림")
        print("="*60)
        
        for news_type, info in self.news_types.items():
            try:
                print(f"\n⏰ {info['display_name']} 지연 알림 테스트...")
                self.send_delay_notification(news_type, info)
                print(f"✅ {info['display_name']} 지연 알림 전송 완료")
            except Exception as e:
                print(f"❌ {info['display_name']} 지연 알림 실패: {e}")
    
    def test_business_day_comparison(self):
        """영업일 비교 분석 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트 4: 영업일 비교 분석")
        print("="*60)
        
        try:
            self.send_business_day_comparison()
            print("✅ 영업일 비교 분석 전송 완료")
        except Exception as e:
            print(f"❌ 영업일 비교 분석 실패: {e}")
    
    def test_daily_report(self):
        """일일 리포트 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트 5: 일일 리포트")
        print("="*60)
        
        try:
            self.send_daily_report()
            print("✅ 일일 리포트 전송 완료")
        except Exception as e:
            print(f"❌ 일일 리포트 실패: {e}")
    
    def test_status_reports(self):
        """상태 리포트 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트 6: 상태 리포트")
        print("="*60)
        
        status_tasks = ['morning_status', 'evening_detail', 'evening_analysis']
        
        for task in status_tasks:
            try:
                print(f"\n📊 {task} 상태 리포트 테스트...")
                self.send_status_report(task)
                print(f"✅ {task} 상태 리포트 전송 완료")
            except Exception as e:
                print(f"❌ {task} 상태 리포트 실패: {e}")
    
    def test_no_update_notification(self):
        """데이터 갱신 없음 알림 테스트"""
        print("\n" + "="*60)
        print("🧪 테스트 7: 데이터 갱신 없음 알림")
        print("="*60)
        
        try:
            self.send_no_update_notification()
            print("✅ 데이터 갱신 없음 알림 전송 완료")
        except Exception as e:
            print(f"❌ 데이터 갱신 없음 알림 실패: {e}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🎯 POSCO 메인 알림 시스템 전체 메시지 테스트 시작")
        print(f"📅 테스트 기준 시간: {self.test_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 모든 테스트 실행
        self.test_startup_notification()
        self.test_news_publication_alerts()
        self.test_delay_notifications()
        self.test_business_day_comparison()
        self.test_daily_report()
        self.test_status_reports()
        self.test_no_update_notification()
        
        print("\n" + "="*80)
        print("🎉 모든 메시지 타입 테스트 완료!")
        print("📡 두레이 웹훅으로 전송된 메시지들을 확인해보세요.")
        print("="*80)

def main():
    """메인 함수"""
    try:
        tester = ManualTestNotifier()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()