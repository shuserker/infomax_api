#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
중복 실행 방지 테스트 스크립트
실제 GUI 없이 중복 실행 방지만 테스트합니다.
"""

import sys
import os
import time

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from singleton_manager import prevent_duplicate_execution, cleanup_singleton


def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🧪 WatchHamster 중복 실행 방지 테스트")
    print("=" * 60)
    
    # 중복 실행 방지 체크
    if not prevent_duplicate_execution("WatchHamster"):
        print("[INFO] WatchHamster가 이미 실행 중입니다.")
        print("이 메시지가 보이면 중복 실행 방지가 정상 작동하는 것입니다!")
        return
    
    print("[SUCCESS] 첫 번째 인스턴스로 실행됩니다.")
    print("이제 다른 터미널에서 이 스크립트를 다시 실행해보세요.")
    print("중복 실행 방지 메시지가 나타나야 합니다.")
    print("")
    print("10초 후 자동으로 종료됩니다...")
    
    try:
        for i in range(10, 0, -1):
            print(f"남은 시간: {i}초", end="\r")
            time.sleep(1)
        
        print("\n[INFO] 테스트 완료!")
        
    except KeyboardInterrupt:
        print("\n[INFO] 사용자에 의해 중단되었습니다.")
    finally:
        cleanup_singleton()
        print("[INFO] 정리 완료")


if __name__ == "__main__":
    main()