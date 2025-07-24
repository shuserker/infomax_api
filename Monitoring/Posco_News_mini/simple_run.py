"""
간단한 POSCO 뉴스 모니터 실행 스크립트 (Windows용)
"""

import os
import sys

# 현재 파일의 디렉토리로 작업 디렉토리 변경
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Python 경로에 현재 디렉토리 추가
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

print(f"작업 디렉토리: {os.getcwd()}")

try:
    # 모듈 import
    from posco_news_monitor import PoscoNewsMonitor
    from config import DOORAY_WEBHOOK_URL, MONITOR_CONFIG
    
    print("✅ 모듈 import 성공")
    
    # 웹훅 URL 확인
    if not DOORAY_WEBHOOK_URL or "YOUR_WEBHOOK_TOKEN_HERE" in DOORAY_WEBHOOK_URL:
        print("❌ config.py에서 DOORAY_WEBHOOK_URL을 설정해주세요!")
        input("엔터를 눌러 종료...")
        sys.exit(1)
    
    # 모니터 생성 및 테스트
    monitor = PoscoNewsMonitor(DOORAY_WEBHOOK_URL)
    print("✅ 모니터 생성 성공")
    
    # 한 번 체크 실행
    print("🔍 뉴스 데이터 체크 중...")
    monitor.check_once()
    
    input("엔터를 눌러 종료...")
    
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    print("필요한 파일들이 같은 폴더에 있는지 확인해주세요:")
    print("- posco_news_monitor.py")
    print("- config.py")
    input("엔터를 눌러 종료...")
except Exception as e:
    print(f"❌ 실행 오류: {e}")
    import traceback
    traceback.print_exc()
    input("엔터를 눌러 종료...")