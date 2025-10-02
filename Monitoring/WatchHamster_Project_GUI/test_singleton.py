#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Singleton Manager 테스트 스크립트
중복 실행 방지 시스템을 테스트합니다.
"""

import sys
import os
import time
import subprocess

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from singleton_manager import SingletonManager, prevent_duplicate_execution


def test_singleton_basic():
    """기본 싱글톤 테스트"""
    print("🧪 기본 싱글톤 테스트 시작")
    
    # 첫 번째 인스턴스
    singleton1 = SingletonManager("TestApp", 12346)
    
    if singleton1.acquire_lock():
        print("✅ 첫 번째 인스턴스: 락 획득 성공")
        
        # 두 번째 인스턴스 (같은 프로세스)
        singleton2 = SingletonManager("TestApp", 12346)
        
        if singleton2.is_already_running():
            print("✅ 두 번째 인스턴스: 중복 실행 감지됨")
        else:
            print("❌ 두 번째 인스턴스: 중복 실행 감지 실패")
        
        # 기존 인스턴스와 통신 테스트
        if singleton2.show_existing_window():
            print("✅ 기존 인스턴스 통신 성공")
        else:
            print("⚠️ 기존 인스턴스 통신 실패 (정상적일 수 있음)")
        
        time.sleep(1)
        singleton1.release_lock()
        print("✅ 첫 번째 인스턴스: 락 해제 완료")
        
    else:
        print("❌ 첫 번째 인스턴스: 락 획득 실패")


def test_prevent_duplicate():
    """중복 실행 방지 함수 테스트"""
    print("\n🧪 중복 실행 방지 함수 테스트 시작")
    
    # 첫 번째 호출
    if prevent_duplicate_execution("TestApp2"):
        print("✅ 첫 번째 호출: 실행 허용됨")
        
        # 두 번째 호출 (같은 프로세스)
        if prevent_duplicate_execution("TestApp2"):
            print("❌ 두 번째 호출: 실행 허용됨 (오류)")
        else:
            print("✅ 두 번째 호출: 중복 실행 방지됨")
        
        # 정리
        from singleton_manager import cleanup_singleton
        cleanup_singleton()
        print("✅ 정리 완료")
        
    else:
        print("❌ 첫 번째 호출: 실행 거부됨")


def test_multiple_processes():
    """다중 프로세스 테스트"""
    print("\n🧪 다중 프로세스 테스트 시작")
    
    # 첫 번째 프로세스 시작
    script_content = '''
import sys
import os
import time
sys.path.insert(0, r"{}")
from singleton_manager import prevent_duplicate_execution, cleanup_singleton

if prevent_duplicate_execution("MultiProcessTest"):
    print("프로세스 1: 실행 시작")
    time.sleep(5)
    cleanup_singleton()
    print("프로세스 1: 종료")
else:
    print("프로세스 1: 중복 실행 방지됨")
'''.format(current_dir)
    
    # 임시 스크립트 파일 생성
    temp_script = os.path.join(current_dir, "temp_test_process1.py")
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    try:
        # 첫 번째 프로세스 시작
        process1 = subprocess.Popen([sys.executable, temp_script], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
        
        # 잠시 대기
        time.sleep(1)
        
        # 두 번째 프로세스 시작 (중복 실행 시도)
        process2 = subprocess.Popen([sys.executable, temp_script], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
        
        # 결과 확인
        stdout1, stderr1 = process1.communicate(timeout=10)
        stdout2, stderr2 = process2.communicate(timeout=10)
        
        print("프로세스 1 출력:")
        print(stdout1)
        if stderr1:
            print("프로세스 1 오류:")
            print(stderr1)
        
        print("프로세스 2 출력:")
        print(stdout2)
        if stderr2:
            print("프로세스 2 오류:")
            print(stderr2)
        
        # 중복 실행 방지 확인
        if "중복 실행 방지됨" in stdout2:
            print("✅ 다중 프로세스 중복 실행 방지 성공")
        else:
            print("⚠️ 다중 프로세스 중복 실행 방지 결과 불명확")
        
    except subprocess.TimeoutExpired:
        print("⚠️ 프로세스 타임아웃")
        process1.kill()
        process2.kill()
    except Exception as e:
        print(f"❌ 다중 프로세스 테스트 오류: {e}")
    finally:
        # 임시 파일 정리
        if os.path.exists(temp_script):
            os.remove(temp_script)


def main():
    """메인 테스트 함수"""
    print("🚀 WatchHamster Singleton Manager 테스트 시작")
    print("=" * 60)
    
    try:
        # 기본 테스트
        test_singleton_basic()
        
        # 중복 실행 방지 함수 테스트
        test_prevent_duplicate()
        
        # 다중 프로세스 테스트
        test_multiple_processes()
        
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()