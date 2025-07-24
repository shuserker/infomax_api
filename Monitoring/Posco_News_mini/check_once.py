# -*- coding: utf-8 -*-
"""
POSCO 뉴스 한 번 체크 (Kiro 직접 실행용)
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
    from config import DOORAY_WEBHOOK_URL
except ImportError as e:
    print(f"[ERROR] 모듈 import 오류: {e}")
    sys.exit(1)

def main():
    print("[START] POSCO 뉴스 한 번 체크")
    print("=" * 40)
    
    # 웹훅 URL 확인
    if not DOORAY_WEBHOOK_URL or "YOUR_WEBHOOK_TOKEN_HERE" in DOORAY_WEBHOOK_URL:
        print("[ERROR] config.py에서 DOORAY_WEBHOOK_URL을 설정해주세요!")
        return
    
    try:
        # 모니터 생성 및 체크
        monitor = PoscoNewsMonitor(DOORAY_WEBHOOK_URL)
        monitor.check_once()
        print("[DONE] 체크 완료")
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")

if __name__ == "__main__":
    main()