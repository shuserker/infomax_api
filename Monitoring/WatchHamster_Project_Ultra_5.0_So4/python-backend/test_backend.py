#!/usr/bin/env python3
"""
백엔드 서비스 테스트 스크립트
의존성 설치 및 기본 기능 확인
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Python 버전 확인"""
    print("Python 버전 확인 중...")
    version = sys.version_info
    print(f"현재 Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 이상이 필요합니다.")
        return False
    
    print("✅ Python 버전 확인 완료")
    return True

def check_dependencies():
    """필수 의존성 확인"""
    print("\n의존성 확인 중...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'psutil',
        'httpx',
        'websockets'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
            print(f"❌ {package} 누락")
        else:
            print(f"✅ {package} 설치됨")
    
    if missing_packages:
        print(f"\n누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 모든 의존성 확인 완료")
    return True

def test_imports():
    """모듈 임포트 테스트"""
    print("\n모듈 임포트 테스트 중...")
    
    try:
        from api import services, metrics, webhooks, websocket
        print("✅ API 모듈 임포트 성공")
    except ImportError as e:
        print(f"❌ API 모듈 임포트 실패: {e}")
        return False
    
    try:
        from models import system, services as service_models, webhooks as webhook_models
        print("✅ 모델 모듈 임포트 성공")
    except ImportError as e:
        print(f"❌ 모델 모듈 임포트 실패: {e}")
        return False
    
    try:
        from utils import config, logger
        print("✅ 유틸리티 모듈 임포트 성공")
    except ImportError as e:
        print(f"❌ 유틸리티 모듈 임포트 실패: {e}")
        return False
    
    return True

def test_basic_functionality():
    """기본 기능 테스트"""
    print("\n기본 기능 테스트 중...")
    
    try:
        # 설정 로드 테스트
        from utils.config import get_settings
        settings = get_settings()
        print(f"✅ 설정 로드 성공: {settings.app_name}")
    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
        return False
    
    try:
        # 로거 테스트
        from utils.logger import get_logger
        logger = get_logger()
        logger.info("로거 테스트 메시지")
        print("✅ 로거 테스트 성공")
    except Exception as e:
        print(f"❌ 로거 테스트 실패: {e}")
        return False
    
    try:
        # 시스템 메트릭 테스트
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        print(f"✅ 시스템 메트릭 테스트 성공 (CPU: {cpu_percent}%, 메모리: {memory.percent}%)")
    except Exception as e:
        print(f"❌ 시스템 메트릭 테스트 실패: {e}")
        return False
    
    return True

def main():
    """메인 테스트 함수"""
    print("========================================")
    print("WatchHamster 백엔드 테스트 스크립트")
    print("========================================")
    
    # 테스트 실행
    tests = [
        ("Python 버전", check_python_version),
        ("의존성", check_dependencies),
        ("모듈 임포트", test_imports),
        ("기본 기능", test_basic_functionality)
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            failed_tests.append(test_name)
    
    print("\n========================================")
    print("테스트 결과")
    print("========================================")
    
    if failed_tests:
        print(f"❌ 실패한 테스트: {', '.join(failed_tests)}")
        print("\n문제 해결 방법:")
        print("1. pip install -r requirements.txt")
        print("2. Python 3.9+ 설치 확인")
        print("3. 가상환경 활성화 확인")
        return 1
    else:
        print("✅ 모든 테스트 통과!")
        print("\n백엔드 서버를 시작할 준비가 되었습니다:")
        print("python main.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())