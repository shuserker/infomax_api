#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 뉴스 마스터 모니터링 시스템 🎛️

서환마감과 증시마감 뉴스를 통합 관리하는 마스터 컨트롤러

주요 기능:
- 서환마감 + 증시마감 동시 모니터링
- 시간대별 적응형 모니터링 전략
- 통합 대시보드 및 상태 보고
- 자동 알림 및 지연 감지
- 발행 패턴 비교 분석

실행 방법:
python master_news_monitor.py

작성자: AI Assistant
최종 수정: 2025-07-30
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta
import argparse

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from exchange_monitor import ExchangeRateMonitor
    from kospi_monitor import KospiCloseMonitor
    from newyork_monitor import NewYorkMarketMonitor
    from core import DoorayNotifier
    from config import DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL, MASTER_MONITORING_STRATEGY
except ImportError as e:
    print(f"[ERROR] 필수 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class MasterNewsMonitor:
    """
    POSCO 뉴스 마스터 모니터링 클래스
    
    서환마감과 증시마감 뉴스를 통합 관리하는 시스템입니다.
    """
    
    def __init__(self):
        """마스터 모니터 초기화"""
        self.exchange_monitor = ExchangeRateMonitor()
        self.kospi_monitor = KospiCloseMonitor()
        self.newyork_monitor = NewYorkMarketMonitor()
        self.notifier = DoorayNotifier(DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL)
        
        # 모니터링 상태 추적
        self.monitoring_active = False
        self.last_status_report = datetime.now()
        self.status_report_interval = 3600  # 1시간마다 상태 보고
        
        print("🎛️ POSCO 뉴스 마스터 모니터링 시스템 초기화 완료")
        print("   🌆 뉴욕마켓워치 모니터: 준비 완료")
        print("   📈 증시마감 모니터: 준비 완료")
        print("   💱 서환마감 모니터: 준비 완료")
    
    def get_current_monitoring_strategy(self):
        """
        현재 시간대에 맞는 모니터링 전략 결정
        
        Returns:
            dict: 모니터링 전략 정보
        """
        now = datetime.now()
        current_time = now.time()
        
        # 주말 체크
        if now.weekday() >= 5:
            return {
                'mode': 'weekend',
                'interval': 1800,  # 30분
                'description': '주말 모드 (최소 모니터링)',
                'targets': []
            }
        
        # 설정 기반 시간대별 전략 결정
        current_time_str = current_time.strftime('%H%M%S')
        
        # 각 전략의 시간 범위 확인
        for strategy_name, strategy_config in MASTER_MONITORING_STRATEGY.items():
            if 'time_range' in strategy_config:
                start_time = strategy_config['time_range']['start']
                end_time = strategy_config['time_range']['end']
                
                if start_time <= current_time_str <= end_time:
                    return {
                        'mode': strategy_name,
                        'interval': strategy_config['interval'],
                        'description': strategy_config['description'],
                        'targets': strategy_config['targets']
                    }
        
        # 기본 전략 (일반 모니터링)
        return {
            'mode': 'normal',
            'interval': MASTER_MONITORING_STRATEGY['normal']['interval'],
            'description': MASTER_MONITORING_STRATEGY['normal']['description'],
            'targets': MASTER_MONITORING_STRATEGY['normal']['targets']
        }
    
    def run_integrated_check(self):
        """통합 상태 확인 실행"""
        current_time = datetime.now()
        strategy = self.get_current_monitoring_strategy()
        
        print(f"\n🔍 [{current_time.strftime('%H:%M:%S')}] 통합 상태 확인")
        print(f"📊 모드: {strategy['description']}")
        
        results = {}
        
        # 뉴욕마켓워치 확인
        if 'newyork-market-watch' in strategy['targets'] or strategy['mode'] == 'normal':
            print("🌆 뉴욕마켓워치 확인 중...")
            self.newyork_monitor.run_single_check()
            newyork_data = self.newyork_monitor.get_current_news_data()
            newyork_analysis = self.newyork_monitor.analyze_publish_pattern(newyork_data)
            results['newyork'] = {
                'data': newyork_data,
                'analysis': newyork_analysis,
                'published_today': newyork_analysis.get('is_published_today', False)
            }
        
        # 증시마감 확인
        if 'kospi-close' in strategy['targets'] or strategy['mode'] == 'normal':
            print("📈 증시마감 확인 중...")
            self.kospi_monitor.run_single_check()
            kospi_data = self.kospi_monitor.get_current_news_data()
            kospi_analysis = self.kospi_monitor.analyze_publish_pattern(kospi_data)
            results['kospi'] = {
                'data': kospi_data,
                'analysis': kospi_analysis,
                'published_today': kospi_analysis.get('is_published_today', False)
            }
        
        # 서환마감 확인
        if 'exchange-rate' in strategy['targets'] or strategy['mode'] == 'normal':
            print("💱 서환마감 확인 중...")
            self.exchange_monitor.run_single_check()
            exchange_data = self.exchange_monitor.get_current_news_data()
            exchange_analysis = self.exchange_monitor.analyze_publish_pattern(exchange_data)
            results['exchange'] = {
                'data': exchange_data,
                'analysis': exchange_analysis,
                'published_today': exchange_analysis.get('is_published_today', False)
            }
        
        return results
    
    def send_integrated_status_report(self, results):
        """통합 상태 보고서 전송"""
        current_time = datetime.now()
        
        # 전체 상태 요약
        newyork_status = results.get('newyork', {})
        kospi_status = results.get('kospi', {})
        exchange_status = results.get('exchange', {})
        
        newyork_published = newyork_status.get('published_today', False)
        kospi_published = kospi_status.get('published_today', False)
        exchange_published = exchange_status.get('published_today', False)
        
        # 상태 이모지 결정 (3개 뉴스 기준)
        published_count = sum([newyork_published, kospi_published, exchange_published])
        
        if published_count == 3:
            status_emoji = "🟢"
            status_text = "모든 뉴스 발행 완료"
        elif published_count >= 1:
            status_emoji = "🟡"
            status_text = f"일부 뉴스 발행 완료 ({published_count}/3)"
        else:
            status_emoji = "🔴"
            status_text = "뉴스 발행 대기 중"
        
        message = f"{status_emoji} POSCO 뉴스 통합 상태 보고\n\n"
        message += f"📅 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"📊 전체 상태: {status_text}\n\n"
        
        # 뉴욕마켓워치 상태
        if 'newyork' in results:
            newyork_analysis = newyork_status.get('analysis', {})
            newyork_emoji = "✅" if newyork_published else "❌"
            message += f"🌆 뉴욕마켓워치: {newyork_emoji} {newyork_analysis.get('analysis', '상태 불명')}\n"
        
        # 증시마감 상태
        if 'kospi' in results:
            kospi_analysis = kospi_status.get('analysis', {})
            kospi_emoji = "✅" if kospi_published else "❌"
            message += f"📈 증시마감: {kospi_emoji} {kospi_analysis.get('analysis', '상태 불명')}\n"
        
        # 서환마감 상태
        if 'exchange' in results:
            exchange_analysis = exchange_status.get('analysis', {})
            exchange_emoji = "✅" if exchange_published else "❌"
            message += f"💱 서환마감: {exchange_emoji} {exchange_analysis.get('analysis', '상태 불명')}\n"
        
        # 다음 보고 시간
        next_report = current_time + timedelta(seconds=self.status_report_interval)
        message += f"\n⏰ 다음 보고: {next_report.strftime('%H:%M')}"
        
        payload = {
            "botName": f"POSCO 뉴스 {status_emoji}",
            "botIconImage": BOT_PROFILE_IMAGE_URL,
            "text": "통합 상태 보고",
            "attachments": [{
                "color": "#17a2b8",
                "text": message
            }]
        }
        
        # DoorayNotifier를 사용하여 알림 전송
        try:
            success = self.notifier.send_notification(message, is_error=False)
            if success:
                print("✅ 통합 상태 보고서 전송 성공")
                self.last_status_report = current_time
                return True
            else:
                print("❌ 통합 상태 보고서 전송 실패")
                return False
                
        except Exception as e:
            print(f"❌ 통합 상태 보고서 전송 오류: {e}")
            return False
    
    def show_integrated_dashboard(self):
        """통합 대시보드 표시"""
        print("\n🎛️ POSCO 뉴스 통합 대시보드")
        print("=" * 60)
        
        current_time = datetime.now()
        strategy = self.get_current_monitoring_strategy()
        
        print(f"📅 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 모니터링 모드: {strategy['description']}")
        print(f"⏰ 확인 간격: {strategy['interval']}초")
        print(f"🎯 대상: {', '.join(strategy['targets']) if strategy['targets'] else '없음'}")
        print()
        
        # 현재 상태 확인
        results = self.run_integrated_check()
        
        # 결과 요약 표시
        print("\n📊 현재 상태 요약:")
        if 'newyork' in results:
            newyork_analysis = results['newyork']['analysis']
            newyork_emoji = "✅" if results['newyork']['published_today'] else "❌"
            print(f"   🌆 뉴욕마켓워치: {newyork_emoji} {newyork_analysis.get('analysis', '상태 불명')}")
        
        if 'kospi' in results:
            kospi_analysis = results['kospi']['analysis']
            kospi_emoji = "✅" if results['kospi']['published_today'] else "❌"
            print(f"   📈 증시마감: {kospi_emoji} {kospi_analysis.get('analysis', '상태 불명')}")
        
        if 'exchange' in results:
            exchange_analysis = results['exchange']['analysis']
            exchange_emoji = "✅" if results['exchange']['published_today'] else "❌"
            print(f"   💱 서환마감: {exchange_emoji} {exchange_analysis.get('analysis', '상태 불명')}")
        
        print("\n" + "=" * 60)
    
    def run_continuous_monitoring(self):
        """연속 통합 모니터링 실행"""
        print("🚀 POSCO 뉴스 통합 모니터링 시작")
        print("=" * 60)
        
        self.monitoring_active = True
        check_count = 0
        
        try:
            while self.monitoring_active:
                check_count += 1
                current_time = datetime.now()
                strategy = self.get_current_monitoring_strategy()
                
                print(f"\n🔍 [{check_count}] {current_time.strftime('%H:%M:%S')} - 통합 확인")
                print(f"📊 모드: {strategy['description']}")
                
                # 통합 상태 확인
                results = self.run_integrated_check()
                
                # 정기 상태 보고 (1시간마다)
                if (current_time - self.last_status_report).total_seconds() >= self.status_report_interval:
                    print("📋 정기 상태 보고서 전송 중...")
                    self.send_integrated_status_report(results)
                
                # 다음 확인까지 대기
                interval = strategy['interval']
                next_check = current_time + timedelta(seconds=interval)
                print(f"⏰ 다음 확인: {next_check.strftime('%H:%M:%S')} ({interval}초 후)")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 사용자에 의해 모니터링이 중단되었습니다.")
            print(f"📊 총 확인 횟수: {check_count}")
            
        except Exception as e:
            print(f"\n❌ 모니터링 중 오류 발생: {e}")
            print(f"📊 총 확인 횟수: {check_count}")
        
        finally:
            self.monitoring_active = False
    
    def run_status_check(self):
        """현재 상태 체크 (변경사항 없어도 상태 알림)"""
        print("📊 현재 상태 체크 실행 중...")
        results = self.run_integrated_check()
        self.send_integrated_status_report(results)
        print("✅ 상태 체크 완료")
    
    def run_business_day_comparison(self):
        """영업일 비교 체크 - 실제 데이터 기반"""
        print("📈 영업일 비교 분석 실행 중...")
        
        # 실제 데이터 조회
        newyork_data = self.newyork_monitor.get_current_news_data()
        kospi_data = self.kospi_monitor.get_current_news_data()
        exchange_data = self.exchange_monitor.get_current_news_data()
        
        comparison_message = "📊 영업일 비교 분석\n\n"
        
        # EXCHANGE RATE 비교
        comparison_message += "┌  EXCHANGE RATE\n"
        if exchange_data:
            exchange_datetime = self.exchange_monitor._format_news_datetime(
                exchange_data.get('date', ''), 
                exchange_data.get('time', ''),
                self.exchange_monitor.analyze_publish_pattern(exchange_data)
            )
            comparison_message += f"├ 현재: {exchange_datetime}\n"
            comparison_message += f"└ 제목: {exchange_data.get('title', '제목 없음')}\n\n"
        else:
            comparison_message += "├ 현재: 데이터 없음\n"
            comparison_message += "└ 제목: 데이터를 가져올 수 없습니다\n\n"
        
        # NEWYORK MARKET WATCH 비교
        comparison_message += "┌  NEWYORK MARKET WATCH\n"
        if newyork_data:
            newyork_analysis = self.newyork_monitor.analyze_publish_pattern(newyork_data)
            newyork_datetime = self.newyork_monitor._format_news_datetime(
                newyork_data.get('date', ''), 
                newyork_data.get('time', ''),
                newyork_analysis
            )
            comparison_message += f"├ 현재: {newyork_datetime}\n"
            comparison_message += f"└ 제목: {newyork_data.get('title', '제목 없음')}\n\n"
        else:
            comparison_message += "├ 현재: 데이터 없음\n"
            comparison_message += "└ 제목: 데이터를 가져올 수 없습니다\n\n"
        
        # KOSPI CLOSE 비교
        comparison_message += "┌  KOSPI CLOSE\n"
        if kospi_data:
            kospi_datetime = self.kospi_monitor._format_news_datetime(
                kospi_data.get('date', ''), 
                kospi_data.get('time', ''),
                self.kospi_monitor.analyze_publish_pattern(kospi_data)
            )
            comparison_message += f"├ 현재: {kospi_datetime}\n"
            comparison_message += f"└ 제목: {kospi_data.get('title', '제목 없음')}\n\n"
        else:
            comparison_message += "├ 현재: 데이터 없음\n"
            comparison_message += "└ 제목: 데이터를 가져올 수 없습니다\n\n"
        
        comparison_message += f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 알림 전송
        self.notifier.send_notification(comparison_message, is_error=False)
        print("✅ 영업일 비교 분석 완료")
    
    def run_smart_monitoring(self):
        """스마트 모니터링 (뉴스 발행 패턴 기반 적응형)"""
        print("🧠 스마트 모니터링 시작...")
        self.run_continuous_monitoring()
    
    def run_basic_monitoring(self):
        """기본 모니터링 (60분 간격 무한실행)"""
        print("🔄 기본 모니터링 시작...")
        # 기본 간격으로 연속 모니터링 실행
        original_interval = self.status_report_interval
        self.status_report_interval = 3600  # 60분
        try:
            self.run_continuous_monitoring()
        finally:
            self.status_report_interval = original_interval
    
    def run_daily_summary(self):
        """일일 요약 리포트 - 실제 데이터 기반"""
        print("📋 일일 요약 리포트 생성 중...")
        
        # 실제 데이터 조회
        newyork_data = self.newyork_monitor.get_current_news_data()
        kospi_data = self.kospi_monitor.get_current_news_data()
        exchange_data = self.exchange_monitor.get_current_news_data()
        
        # 오늘 발행된 뉴스 개수 계산
        today_date = datetime.now().strftime('%Y%m%d')
        published_count = 0
        
        if newyork_data and newyork_data.get('date') == today_date:
            published_count += 1
        if kospi_data and kospi_data.get('date') == today_date:
            published_count += 1
        if exchange_data and exchange_data.get('date') == today_date:
            published_count += 1
        
        summary_message = f"📅 오늘 발행 뉴스 ({published_count}개)\n"
        summary_message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # 오늘 발행된 뉴스들
        if newyork_data and newyork_data.get('date') == today_date:
            newyork_analysis = self.newyork_monitor.analyze_publish_pattern(newyork_data)
            summary_message += "┌  NEWYORK MARKET WATCH\n"
            summary_message += f"├ 시간: {newyork_analysis.get('formatted_time', '시간 정보 없음')}\n"
            summary_message += f"└ 제목: {newyork_data.get('title', '제목 없음')}\n\n"
        
        if kospi_data and kospi_data.get('date') == today_date:
            kospi_analysis = self.kospi_monitor.analyze_publish_pattern(kospi_data)
            summary_message += "┌  KOSPI CLOSE\n"
            summary_message += f"├ 시간: {kospi_analysis.get('actual_time', '시간 정보 없음')}\n"
            summary_message += f"└ 제목: {kospi_data.get('title', '제목 없음')}\n\n"
        
        if exchange_data and exchange_data.get('date') == today_date:
            exchange_analysis = self.exchange_monitor.analyze_publish_pattern(exchange_data)
            summary_message += "┌  EXCHANGE RATE\n"
            summary_message += f"├ 시간: {exchange_analysis.get('actual_time', '시간 정보 없음')}\n"
            summary_message += f"└ 제목: {exchange_data.get('title', '제목 없음')}\n\n"
        
        # 발행되지 않은 뉴스가 있으면 표시
        if published_count == 0:
            summary_message += "📝 오늘 발행된 뉴스가 없습니다.\n\n"
        
        summary_message += f"📝 리포트 생성: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 알림 전송
        self.notifier.send_notification(summary_message, is_error=False)
        print("✅ 일일 요약 리포트 완료")
    
    def run_data_status_check(self):
        """데이터 갱신 상태 체크 - 발행 패턴 고려한 정교한 분석"""
        print("📊 데이터 갱신 상태 체크 중...")
        
        # 실제 데이터 조회
        newyork_data = self.newyork_monitor.get_current_news_data()
        kospi_data = self.kospi_monitor.get_current_news_data()
        exchange_data = self.exchange_monitor.get_current_news_data()
        
        # 각 뉴스별 분석
        newyork_analysis = self.newyork_monitor.analyze_publish_pattern(newyork_data)
        kospi_analysis = self.kospi_monitor.analyze_publish_pattern(kospi_data)
        exchange_analysis = self.exchange_monitor.analyze_publish_pattern(exchange_data)
        
        # 현재 시간 정보
        now = datetime.now()
        current_time = now.strftime('%H%M%S')
        today_date = now.strftime('%Y%m%d')
        
        # 캡처와 동일한 형태의 알림 생성
        status_message = "데이터 갱신 없음\n\n"
        
        # EXCHANGE RATE 상태 (16:30 발행 예정)
        status_message += "┌  EXCHANGE RATE\n"
        if exchange_data:
            # 발행 패턴 기반 상태 판단
            if exchange_analysis.get('is_published_today', False):
                status_message += "├ 상태: 🟢 최신\n"
            elif current_time < "163000":  # 16:30 이전
                status_message += "├ 상태: ⏳ 발행 대기\n"
            elif current_time < "180000":  # 18:00 이전
                status_message += "├ 상태: 🟡 지연 의심\n"
            else:
                status_message += "├ 상태: 🔴 미발행 의심\n"
            
            exchange_datetime = self.exchange_monitor._format_news_datetime(
                exchange_data.get('date', ''), 
                exchange_data.get('time', ''),
                exchange_analysis
            )
            status_message += f"├ 시간: {exchange_datetime}\n"
            status_message += f"└ 제목: {exchange_data.get('title', '제목 없음')}\n\n"
        else:
            if current_time < "163000":
                status_message += "├ 상태: ⏳ 발행 대기\n"
            else:
                status_message += "├ 상태: 🔴 데이터 없음\n"
            status_message += "├ 시간: 데이터 없음\n"
            status_message += "└ 제목:\n\n"
        
        # NEWYORK MARKET WATCH 상태 (06:00-07:00 발행 예정)
        status_message += "┌  NEWYORK MARKET WATCH\n"
        if newyork_data:
            if newyork_analysis.get('is_published_today', False):
                status_message += "├ 상태: 🟢 최신\n"
            elif current_time < "060000":  # 06:00 이전
                status_message += "├ 상태: ⏳ 발행 대기\n"
            elif current_time < "080000":  # 08:00 이전
                status_message += "├ 상태: 🟡 지연 의심\n"
            else:
                status_message += "├ 상태: 🟡 이전 데이터\n"
            
            newyork_datetime = self.newyork_monitor._format_news_datetime(
                newyork_data.get('date', ''), 
                newyork_data.get('time', ''),
                newyork_analysis
            )
            status_message += f"├ 시간: {newyork_datetime}\n"
            status_message += f"└ 제목: {newyork_data.get('title', '제목 없음')}\n\n"
        else:
            if current_time < "060000":
                status_message += "├ 상태: ⏳ 발행 대기\n"
            else:
                status_message += "├ 상태: 🔴 데이터 없음\n"
            status_message += "├ 시간: 데이터 없음\n"
            status_message += "└ 제목:\n\n"
        
        # KOSPI CLOSE 상태 (15:40 발행 예정)
        status_message += "┌  KOSPI CLOSE\n"
        if kospi_data:
            if kospi_analysis.get('is_published_today', False):
                status_message += "├ 상태: 🟢 최신\n"
            elif current_time < "154000":  # 15:40 이전
                status_message += "├ 상태: ⏳ 발행 대기\n"
            elif current_time < "170000":  # 17:00 이전
                status_message += "├ 상태: 🟡 지연 의심\n"
            else:
                status_message += "├ 상태: 🟡 이전 데이터\n"
            
            kospi_datetime = self.kospi_monitor._format_news_datetime(
                kospi_data.get('date', ''), 
                kospi_data.get('time', ''),
                kospi_analysis
            )
            status_message += f"├ 시간: {kospi_datetime}\n"
            status_message += f"└ 제목: {kospi_data.get('title', '제목 없음')}\n\n"
        else:
            if current_time < "154000":
                status_message += "├ 상태: ⏳ 발행 대기\n"
            else:
                status_message += "├ 상태: 🔴 데이터 없음\n"
            status_message += "├ 시간: 데이터 없음\n"
            status_message += "└ 제목:\n\n"
        
        status_message += f"최종 확인: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 알림 전송
        self.notifier.send_notification(status_message, is_error=False)
        print("✅ 데이터 갱신 상태 체크 완료")

    def run_test_notification(self):
        """테스트 알림 전송"""
        print("🧪 테스트 알림 전송 중...")
        test_message = f"🧪 POSCO 뉴스 마스터 모니터링 테스트\n\n📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ 시스템 정상 작동 중"
        
        # DoorayNotifier를 사용하여 알림 전송
        try:
            success = self.notifier.send_notification(test_message, is_error=False)
            if success:
                print("✅ 테스트 알림 전송 성공")
            else:
                print("❌ 테스트 알림 전송 실패")
        except Exception as e:
            print(f"❌ 테스트 알림 전송 오류: {e}")
    
    def run_detailed_daily_summary(self):
        """상세 일일 요약 (제목 + 본문 비교)"""
        print("📋 상세 일일 요약 생성 중...")
        # 개별 모니터의 단일 체크로 대체 (함수가 없으므로)
        print("🌆 뉴욕마켓워치 상세 요약...")
        self.newyork_monitor.run_single_check()
        
        print("📈 증시마감 상세 요약...")
        self.kospi_monitor.run_single_check()
        
        print("💱 서환마감 상세 요약...")
        self.exchange_monitor.run_single_check()
        
        print("✅ 상세 일일 요약 완료")
    
    def run_advanced_analysis(self):
        """고급 분석 (30일 추이 + 주단위 분석 + 향후 예상)"""
        print("📊 고급 분석 실행 중...")
        # 개별 모니터의 단일 체크로 대체 (함수가 없으므로)
        print("🌆 뉴욕마켓워치 고급 분석...")
        self.newyork_monitor.run_single_check()
        
        print("📈 증시마감 고급 분석...")
        self.kospi_monitor.run_single_check()
        
        print("💱 서환마감 고급 분석...")
        self.exchange_monitor.run_single_check()
        
        print("✅ 고급 분석 완료")
    
    def run_smart_monitoring(self):
        """스마트 모니터링 (뉴스 발행 패턴 기반 적응형)"""
        print("🧠 스마트 모니터링 시작...")
        self.run_continuous_monitoring()
    
    def run_basic_monitoring(self):
        """기본 모니터링 (60분 간격 무한실행)"""
        print("🔄 기본 모니터링 시작...")
        # 기본 간격으로 연속 모니터링 실행
        original_interval = self.status_report_interval
        self.status_report_interval = 3600  # 60분
        try:
            self.run_continuous_monitoring()
        finally:
            self.status_report_interval = original_interval

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='POSCO 뉴스 마스터 모니터링 시스템')
    parser.add_argument('--mode', choices=['dashboard', 'monitor'], default='dashboard',
                       help='실행 모드: dashboard(대시보드) 또는 monitor(연속 모니터링)')
    
    args = parser.parse_args()
    
    # 마스터 모니터 초기화
    master_monitor = MasterNewsMonitor()
    
    if args.mode == 'dashboard':
        master_monitor.show_integrated_dashboard()
    else:
        master_monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()