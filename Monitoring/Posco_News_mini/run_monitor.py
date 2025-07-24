# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 실행 스크립트
"""

import sys
import os

# Windows 환경에서 UTF-8 출력 설정
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from posco_news_monitor import PoscoNewsMonitor
    from config import DOORAY_WEBHOOK_URL, MONITOR_CONFIG
except ImportError as e:
    print(f"[ERROR] 모듈 import 오류: {e}")
    print("Monitoring/Posco_News_mini 폴더에서 실행해주세요.")
    sys.exit(1)

def main():
    print("[START] POSCO 뉴스 모니터 시작")
    print("=" * 50)
    
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
    
    # 모니터 생성
    monitor = PoscoNewsMonitor(DOORAY_WEBHOOK_URL)
    
    # 명령행 인수 확인
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        # 기본값: 한 번 체크
        choice = "1"
    
    print(f"실행 모드: {choice}")
    print("1. 한 번만 체크")
    print("2. 지속적 모니터링") 
    print("3. 테스트 알림 전송")
    print()
    
    try:
        if choice == "1":
            print("[CHECK] 한 번 체크 실행...")
            monitor.check_once()
            
        elif choice == "2":
            interval = MONITOR_CONFIG["check_interval_minutes"]
            print(f"[MONITOR] 지속적 모니터링 시작 ({interval}분 간격)")
            print("중단하려면 Ctrl+C를 누르세요")
            monitor.start_monitoring(interval_minutes=interval)
            
        elif choice == "3":
            print("[TEST] 테스트 알림 전송...")
            monitor.send_dooray_notification(
                "POSCO 뉴스 모니터 테스트 알림입니다.\n설정이 정상적으로 완료되었습니다!"
            )
            
        else:
            print("[ERROR] 잘못된 선택입니다.")
            print("사용법: python run_monitor.py [1|2|3]")
            
    except KeyboardInterrupt:
        print("\n\n[STOP] 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")

if __name__ == "__main__":
    main()