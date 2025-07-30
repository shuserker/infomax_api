# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 일회성 작업 실행 스크립트

워치햄스터 2.0 시스템의 개별 모니터들을 사용하여 일회성 작업을 수행하는 스크립트입니다.
24시간 지속 서비스는 monitor_WatchHamster.py를 사용하세요.

🎯 역할 구분:
    - run_monitor.py: 일회성 작업 (상태 체크, 요약, 분석 등)
    - monitor_WatchHamster.py: 24시간 워치햄스터 서비스

사용법:
    python run_monitor.py [옵션번호]
    
옵션 상세:
    1 (기본값): 📊 현재 상태 체크 - 빠른 일회성 상태 확인
    2: 📈 영업일 비교 분석 - 현재 vs 직전 영업일 상세 비교
    3: 📋 일일 요약 리포트 - 오늘 발행 뉴스 종합 요약
    4: 📊 상세 분석 리포트 - 각 뉴스별 상세 분석
    5: 🔍 고급 분석 리포트 - 30일 추이 및 패턴 분석
    6: 🧪 알림 테스트 - 워치햄스터 2.0 알림 시스템 테스트
    7: 🎛️ 마스터 모니터 통합 체크 - 전체 시스템 종합 분석
    8: 🌆📈💱 개별 모니터 체크 - 각 뉴스별 전용 모니터 실행

💡 24시간 지속 모니터링이 필요하면:
    python monitor_WatchHamster.py

작성자: AI Assistant
최종 수정: 2025-07-30 (역할 분리 완료)
"""

import sys
import os

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # 워치햄스터 2.0 시스템 import
    from newyork_monitor import NewYorkMarketMonitor
    from kospi_monitor import KospiCloseMonitor
    from exchange_monitor import ExchangeRateMonitor
    from master_news_monitor import MasterNewsMonitor
    from config import DOORAY_WEBHOOK_URL, MONITORING_CONFIG
except ImportError as e:
    print(f"[ERROR] 워치햄스터 2.0 모듈 import 오류: {e}")
    print("워치햄스터 2.0 시스템이 설치되지 않았습니다.")
    print("Monitoring/Posco_News_mini 폴더에서 실행해주세요.")
    print("최적화된 모듈 구조를 사용합니다.")
    sys.exit(1)

def main():
    """
    일회성 작업 실행 함수
    
    워치햄스터 2.0의 개별 모니터들을 사용하여 일회성 작업을 수행합니다.
    24시간 지속 서비스는 monitor_WatchHamster.py를 사용하세요.
    """
    print("[START] POSCO 뉴스 모니터 - 일회성 작업")
    print("=" * 60)
    print("💡 24시간 지속 모니터링: python monitor_WatchHamster.py")
    print("🚀 일회성 작업: python run_monitor.py [옵션]")
    print()
    
    # 웹훅 URL 확인
    if not DOORAY_WEBHOOK_URL or "YOUR_WEBHOOK_TOKEN_HERE" in DOORAY_WEBHOOK_URL:
        print("[ERROR] Dooray 웹훅 URL이 설정되지 않았습니다!")
        print()
        print("설정 방법:")
        print("1. Dooray에 로그인")
        print("2. 프로젝트 > 설정 > 서비스 연동 > Incoming Webhook")
        print("3. 새 웹훅 생성 후 URL 복사")
        print("4. config.py 파일에서 DOORAY_WEBHOOK_URL 수정")
        print()
        return
    
    # 워치햄스터 2.0 모니터들 생성
    try:
        newyork_monitor = NewYorkMarketMonitor()
        kospi_monitor = KospiCloseMonitor()
        exchange_monitor = ExchangeRateMonitor()
        master_monitor = MasterNewsMonitor()
        print("✅ 워치햄스터 2.0 개별 모니터 초기화 완료")
    except Exception as e:
        print(f"❌ 워치햄스터 2.0 초기화 실패: {e}")
        return
    
    # 명령행 인수 확인
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        # 기본값: 현재 상태 체크 (가장 유용한 옵션)
        choice = "1"
    
    print(f"🚀 일회성 작업 실행 모드: {choice}")
    print("1. 📊 현재 상태 체크 (빠른 일회성 상태 확인)")
    print("2. 📈 영업일 비교 분석 (현재 vs 직전 영업일 상세 비교)")
    print("3. 📋 일일 요약 리포트 (오늘 발행 뉴스 종합 요약)")
    print("4. 📊 상세 분석 리포트 (각 뉴스별 상세 분석)")
    print("5. 🔍 고급 분석 리포트 (30일 추이 및 패턴 분석)")
    print("6. 🧪 알림 테스트 (워치햄스터 2.0 알림 시스템 테스트)")
    print("7. 🎛️ 마스터 모니터 통합 체크 (전체 시스템 종합 분석)")
    print("8. 🌆📈💱 개별 모니터 체크 (각 뉴스별 전용 모니터 실행)")
    print("8. 📊 고급 분석 (마스터 모니터 고급 분석)")
    print()
    
    try:
        if choice == "1":
            print("[📊 현재 상태 체크] 빠른 일회성 상태 확인...")
            print("🌆 뉴욕마켓워치, 📈 증시마감, 💱 서환마감 개별 모니터로 현재 상태 체크")
            
            # 개별 모니터로 현재 상태 체크
            ny_result = newyork_monitor.run_single_check()
            kospi_result = kospi_monitor.run_single_check()
            exchange_result = exchange_monitor.run_single_check()
            
            print("✅ 현재 상태 체크 완료")
            
        elif choice == "2":
            print("[📈 영업일 비교 분석] 현재 vs 직전 영업일 상세 비교...")
            print("마스터 모니터의 통합 분석으로 영업일 비교 수행")
            
            comparison_result = master_monitor.run_integrated_check()
            print("✅ 영업일 비교 분석 완료")
            
        elif choice == "3":
            print("[📋 일일 요약 리포트] 오늘 발행 뉴스 종합 요약...")
            print("개별 모니터 + 마스터 모니터 통합 분석으로 완전한 일일 요약")
            
            # 마스터 모니터의 일일 요약
            master_monitor.generate_daily_summary()
            print("✅ 일일 요약 리포트 완료")
            
        elif choice == "4":
            print("[📊 상세 분석 리포트] 각 뉴스별 상세 분석...")
            print("각 뉴스별 전용 모니터의 상세 분석 결과")
            
            # 개별 모니터의 상세 분석
            newyork_monitor.generate_detailed_analysis()
            kospi_monitor.generate_detailed_analysis()
            exchange_monitor.generate_detailed_analysis()
            
            print("✅ 상세 분석 리포트 완료")
            
        elif choice == "5":
            print("[🔍 고급 분석 리포트] 30일 추이 및 패턴 분석...")
            print("마스터 모니터의 통합 고급 분석 (30일 추이, 패턴 분석, 예측)")
            
            # 마스터 모니터의 고급 분석
            master_monitor.generate_advanced_analysis()
            print("✅ 고급 분석 리포트 완료")
            
        elif choice == "6":
            print("[🧪 알림 테스트] 워치햄스터 2.0 알림 시스템 테스트...")
            
            # 각 개별 모니터의 알림 테스트
            newyork_monitor.send_test_notification()
            kospi_monitor.send_test_notification()
            exchange_monitor.send_test_notification()
            master_monitor.send_test_notification()
            
            print("✅ 모든 알림 시스템 테스트 완료")
            
        elif choice == "7":
            print("[🎛️ 마스터 모니터 통합 체크] 전체 시스템 종합 분석...")
            print("마스터 모니터의 통합 체크로 전체 시스템 상태 분석")
            
            # 마스터 모니터의 통합 체크
            integrated_result = master_monitor.run_integrated_check()
            print("✅ 마스터 모니터 통합 체크 완료")
            
        elif choice == "8":
            print("[🌆📈💱 개별 모니터 체크] 각 뉴스별 전용 모니터 실행...")
            print("각 뉴스별 전용 모니터를 개별적으로 실행하여 상세 정보 확인")
            
            print("🌆 뉴욕마켓워치 모니터 실행...")
            newyork_monitor.run_single_check()
            
            print("📈 증시마감 모니터 실행...")
            kospi_monitor.run_single_check()
            
            print("💱 서환마감 모니터 실행...")
            exchange_monitor.run_single_check()
            
            print("✅ 모든 개별 모니터 체크 완료")
            
        else:
            print("[ERROR] 잘못된 선택입니다.")
            print("사용법: python run_monitor.py [1|2|3|4|5|6|7|8]")
            print()
            print("💡 24시간 지속 모니터링이 필요하면:")
            print("   python monitor_WatchHamster.py")
            
    except KeyboardInterrupt:
        print("\n\n[STOP] 일회성 작업이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n[ERROR] 일회성 작업 오류 발생: {e}")

if __name__ == "__main__":
    main()