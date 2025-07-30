#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
증시마감 뉴스 실시간 모니터링 시작 스크립트

평일 15:30부터 17:30까지 증시마감 뉴스를 집중 모니터링합니다.

실행 방법:
python start_kospi_monitoring.py

특징:
- 15:30-17:30 집중 모니터링 (1분 간격)
- 17:30 이후 일반 모니터링 (5분 간격)
- 자동 지연 알림 (16:00, 16:30, 17:00)
- 발행 즉시 알림 전송
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from monitor_kospi_close import KospiCloseMonitor

def is_intensive_monitoring_time():
    """
    집중 모니터링 시간대 확인 (평일 15:30-17:30)
    
    Returns:
        bool: 집중 모니터링 시간대 여부
    """
    now = datetime.now()
    
    # 주말 제외
    if now.weekday() >= 5:  # 토요일(5), 일요일(6)
        return False
    
    # 15:30-17:30 시간대 확인
    current_time = now.time()
    start_time = datetime.strptime("15:30", "%H:%M").time()
    end_time = datetime.strptime("17:30", "%H:%M").time()
    
    return start_time <= current_time <= end_time

def get_monitoring_interval():
    """
    현재 시간대에 맞는 모니터링 간격 반환
    
    Returns:
        int: 모니터링 간격 (초)
    """
    if is_intensive_monitoring_time():
        return 60  # 1분 간격 (집중 모니터링)
    else:
        return 300  # 5분 간격 (일반 모니터링)

def main():
    """메인 실행 함수"""
    print("📈 증시마감 뉴스 실시간 모니터링 시작")
    print("=" * 50)
    
    # 증시마감 모니터 초기화
    monitor = KospiCloseMonitor()
    
    # 현재 상태 확인
    current_time = datetime.now()
    is_intensive = is_intensive_monitoring_time()
    interval = get_monitoring_interval()
    
    print(f"📅 시작 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 모니터링 모드: {'🔥 집중 모니터링' if is_intensive else '📋 일반 모니터링'}")
    print(f"⏰ 확인 간격: {interval}초 ({interval//60}분)" if interval >= 60 else f"⏰ 확인 간격: {interval}초")
    print(f"🎯 대상: 증시마감 뉴스 (kospi-close)")
    print("=" * 50)
    
    try:
        check_count = 0
        last_interval_change = current_time
        
        while True:
            check_count += 1
            current_time = datetime.now()
            
            print(f"\n🔍 [{check_count}] {current_time.strftime('%H:%M:%S')} - 상태 확인 중...")
            
            # 단일 상태 확인 실행
            monitor.run_single_check()
            
            # 모니터링 간격 동적 조정
            new_interval = get_monitoring_interval()
            if new_interval != interval:
                interval = new_interval
                is_intensive = is_intensive_monitoring_time()
                print(f"🔄 모니터링 모드 변경: {'🔥 집중 모니터링' if is_intensive else '📋 일반 모니터링'}")
                print(f"⏰ 새로운 간격: {interval}초")
                last_interval_change = current_time
            
            # 다음 확인까지 대기
            next_check = current_time + timedelta(seconds=interval)
            print(f"⏰ 다음 확인: {next_check.strftime('%H:%M:%S')} ({interval}초 후)")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n🛑 사용자에 의해 모니터링이 중단되었습니다.")
        print(f"📊 총 확인 횟수: {check_count}")
        print(f"⏰ 실행 시간: {datetime.now() - current_time}")
        
    except Exception as e:
        print(f"\n❌ 모니터링 중 오류 발생: {e}")
        print(f"📊 총 확인 횟수: {check_count}")

if __name__ == "__main__":
    main()