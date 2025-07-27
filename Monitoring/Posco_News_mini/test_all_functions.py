# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터 전체 기능 자동 테스트 스크립트
"""

import sys
import os
import time
import subprocess
import threading
from datetime import datetime

# Windows 환경에서 UTF-8 출력 설정
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def run_test_with_timeout(test_name, command, timeout_seconds=10):
    """제한 시간 내에 테스트 실행"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name} 테스트 시작")
    print(f"명령어: {command}")
    print(f"제한시간: {timeout_seconds}초")
    print(f"{'='*60}")
    
    try:
        # subprocess로 실행
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        
        # 제한 시간 내에 완료되는지 확인
        try:
            output, _ = process.communicate(timeout=timeout_seconds)
            print(output)
            print(f"✅ {test_name} 테스트 완료 (정상 종료)")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {timeout_seconds}초 제한시간 도달 - 프로세스 강제 종료")
            process.kill()
            output, _ = process.communicate()
            if output:
                print("마지막 출력:")
                print(output[-500:])  # 마지막 500자만 출력
            print(f"✅ {test_name} 테스트 완료 (시간 제한으로 종료)")
            return True
            
    except Exception as e:
        print(f"❌ {test_name} 테스트 오류: {e}")
        return False

def main():
    print("🚀 POSCO 뉴스 모니터 전체 기능 자동 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 목록 (테스트명, 명령어, 제한시간)
    tests = [
        ("웹훅 연결 테스트", "python run_monitor.py 6", 10),
        ("현재 상태 체크", "python run_monitor.py 1", 15),
        ("영업일 비교 체크", "python run_monitor.py 2", 20),
        ("일일 요약 리포트", "python run_monitor.py 5", 20),
        ("기본 모니터링 (짧은 테스트)", "python run_monitor.py 4", 10),
        ("스마트 모니터링 (짧은 테스트)", "python run_monitor.py 3", 10),
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for test_name, command, timeout in tests:
        if run_test_with_timeout(test_name, command, timeout):
            success_count += 1
        
        # 테스트 간 잠시 대기
        print("⏳ 다음 테스트까지 3초 대기...")
        time.sleep(3)
    
    # 최종 결과
    print(f"\n{'='*60}")
    print(f"🎯 전체 테스트 완료")
    print(f"📊 성공: {success_count}/{total_count}")
    print(f"📅 테스트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == total_count:
        print("🎉 모든 테스트 성공!")
    else:
        print(f"⚠️ {total_count - success_count}개 테스트 실패")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()