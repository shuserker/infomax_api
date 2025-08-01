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

# 출력 버퍼링 해제 - 실시간 로그 출력을 위해
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 환경 변수로도 출력 버퍼링 비활성화
os.environ['PYTHONUNBUFFERED'] = '1'

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # 워치햄스터 2.0 시스템 import
    from newyork_monitor import NewYorkMarketMonitor
    from kospi_monitor import KospiCloseMonitor
    from exchange_monitor import ExchangeRateMonitor
    from master_news_monitor import MasterNewsMonitor
    from core.colorful_ui import ColorfulConsoleUI
    from config import DOORAY_WEBHOOK_URL, MONITORING_CONFIG
except ImportError as e:
    print(f"[ERROR] 워치햄스터 2.0 모듈 import 오류: {e}")
    print("워치햄스터 2.0 시스템이 설치되지 않았습니다.")
    print("Monitoring/Posco_News_mini 폴더에서 실행해주세요.")
    print("최적화된 모듈 구조를 사용합니다.")
    sys.exit(1)

def main():
    """
    POSCO 뉴스 모니터링 시스템 메인 함수
    
    사용자가 선택한 모드에 따라 다양한 모니터링 작업을 수행합니다.
    """
    # 컬러풀한 UI 초기화
    ui = ColorfulConsoleUI()
    
    print("[START] POSCO 뉴스 모니터 시작", flush=True)
    print("=" * 50, flush=True)
    
    # 웹훅 URL 확인
    if not DOORAY_WEBHOOK_URL or "YOUR_WEBHOOK_TOKEN_HERE" in DOORAY_WEBHOOK_URL:
        ui.print_error_message(Exception("Dooray 웹훅 URL이 설정되지 않았습니다!"))
        ui.print_info_message("설정 방법:")
        ui.print_info_message("1. Dooray에 로그인")
        ui.print_info_message("2. 프로젝트 > 설정 > 서비스 연동 > Incoming Webhook")
        ui.print_info_message("3. 새 웹훅 생성 후 URL 복사")
        ui.print_info_message("4. config.py 파일에서 DOORAY_WEBHOOK_URL 수정")
        return
    
    # 워치햄스터 2.0 모니터들 생성
    try:
        newyork_monitor = NewYorkMarketMonitor()
        kospi_monitor = KospiCloseMonitor()
        exchange_monitor = ExchangeRateMonitor()
        master_monitor = MasterNewsMonitor()
        print("✅ 워치햄스터 2.0 개별 모니터 초기화 완료", flush=True)
    except Exception as e:
        ui.print_error_message(e, "워치햄스터 2.0 초기화")
        return
    
    # 명령행 인수 확인
    if len(sys.argv) > 1:
        try:
            choice = int(sys.argv[1])
        except ValueError:
            choice = 3  # 기본값: 스마트 모니터링
    else:
        # 사용자 선택 메뉴 표시
        menu_options = [
            "📊 현재 상태 체크 (변경사항 없어도 상태 알림)",
            "📈 영업일 비교 체크 (현재 vs 직전 영업일 상세 비교)",
            "🧠 스마트 모니터링 (뉴스 발행 패턴 기반 적응형)",
            "🔄 기본 모니터링 (60분 간격 무한실행)",
            "📋 일일 요약 리포트 (오늘 발행 뉴스 요약)",
            "🧪 테스트 알림 전송",
            "📋 상세 일일 요약 (제목 + 본문 비교)",
            "📊 고급 분석 (30일 추이 + 주단위 분석 + 향후 예상)"
        ]
        ui.print_menu(menu_options, 3)
        print()
        choice = 3  # 기본값: 스마트 모니터링
    
    # 스마트 모니터링 모드 (기본값)
    if choice == 3:
        monitoring_details = {
            'title': '뉴스 발행 패턴 기반 적응형 모니터링 시작',
            'operating_hours': '07:00-18:00',
            'focus_hours': '06:00-08:00, 15:00-17:00 (20분 간격)',
            'normal_hours': '07:00-18:00 (2시간 간격)',
            'quiet_hours': '18:00-07:00 (변경사항 있을 때만 알림)',
            'special_events': '08:00 전일비교, 18:00 일일요약'
        }
        ui.print_monitoring_info("🧠 스마트 모니터링", monitoring_details)
        
        try:
            master_monitor.run_smart_monitoring()
        except KeyboardInterrupt:
            ui.print_info_message("사용자에 의해 모니터링이 중단되었습니다.")
        except Exception as e:
            ui.print_error_message(e, "스마트 모니터링")
    
    # 다른 모드들도 추가
    elif choice == 1:
        ui.print_header("[📊 현재 상태 체크] 변경사항 없어도 상태 알림", "status")
        master_monitor.run_data_status_check()
    
    elif choice == 2:
        ui.print_header("[📈 영업일 비교 체크] 현재 vs 직전 영업일 상세 비교", "status")
        master_monitor.run_business_day_comparison()
    
    elif choice == 4:
        ui.print_header("[🔄 기본 모니터링] 60분 간격 무한실행", "status")
        ui.print_info_message("중단하려면 Ctrl+C를 누르세요")
        try:
            master_monitor.run_basic_monitoring()
        except KeyboardInterrupt:
            ui.print_info_message("사용자에 의해 모니터링이 중단되었습니다.")
    
    elif choice == 5:
        ui.print_header("[📋 일일 요약 리포트] 오늘 발행 뉴스 요약", "status")
        master_monitor.run_daily_summary()
    
    elif choice == 6:
        ui.print_header("[🧪 테스트 알림 전송]", "status")
        master_monitor.run_test_notification()
    
    elif choice == 7:
        ui.print_header("[📋 상세 일일 요약] 제목 + 본문 비교", "status")
        master_monitor.run_detailed_daily_summary()
    
    elif choice == 8:
        ui.print_header("[📊 고급 분석] 30일 추이 + 주단위 분석 + 향후 예상", "status")
        master_monitor.run_advanced_analysis()
    
    else:
        ui.print_error_message(Exception(f"잘못된 선택: {choice}"), "1-8 사이의 숫자를 입력해주세요.")
        print()
        print("💡 24시간 지속 모니터링이 필요하면:")
        print("   python monitor_WatchHamster.py")

if __name__ == "__main__":
    main()