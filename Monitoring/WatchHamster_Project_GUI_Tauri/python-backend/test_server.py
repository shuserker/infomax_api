#!/usr/bin/env python3
"""
FastAPI 서버 기본 구조 테스트
"""

import asyncio
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

async def test_imports():
    """필수 모듈 임포트 테스트"""
    print("🔍 모듈 임포트 테스트 시작...")
    
    try:
        # 기본 라이브러리 테스트
        import fastapi
        import uvicorn
        import pydantic
        print("✅ FastAPI 관련 라이브러리 임포트 성공")
        
        # 설정 모듈 테스트
        from utils.config import get_settings
        settings = get_settings()
        print(f"✅ 설정 모듈 임포트 성공 - 앱 이름: {settings.app_name}")
        
        # 로거 모듈 테스트
        from utils.logger import get_logger
        logger = get_logger("test")
        logger.info("로거 테스트 메시지")
        print("✅ 로거 모듈 임포트 성공")
        
        # 미들웨어 모듈 테스트
        from utils.middleware import TimingMiddleware, SecurityHeadersMiddleware
        print("✅ 미들웨어 모듈 임포트 성공")
        
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

async def test_app_creation():
    """FastAPI 앱 생성 테스트"""
    print("\n🔍 FastAPI 앱 생성 테스트 시작...")
    
    try:
        # 메인 앱 임포트
        from main import app, settings
        
        # 앱 기본 정보 확인
        print(f"✅ 앱 제목: {app.title}")
        print(f"✅ 앱 버전: {app.version}")
        print(f"✅ 디버그 모드: {settings.debug}")
        print(f"✅ API 포트: {settings.api_port}")
        
        # 라우터 확인
        routes = [route.path for route in app.routes]
        print(f"✅ 등록된 라우트 수: {len(routes)}")
        print(f"✅ 기본 라우트: {[r for r in routes if r in ['/', '/health', '/docs', '/redoc']]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 앱 생성 테스트 실패: {e}")
        return False

async def test_configuration():
    """설정 테스트"""
    print("\n🔍 설정 테스트 시작...")
    
    try:
        from utils.config import get_settings
        settings = get_settings()
        
        # 필수 설정 확인
        assert settings.app_name, "앱 이름이 설정되지 않음"
        assert settings.api_port > 0, "유효하지 않은 포트 번호"
        assert settings.cors_origins_list, "CORS origins가 설정되지 않음"
        
        print(f"✅ 앱 이름: {settings.app_name}")
        print(f"✅ API 호스트: {settings.api_host}")
        print(f"✅ API 포트: {settings.api_port}")
        print(f"✅ CORS Origins: {settings.cors_origins_list}")
        print(f"✅ 로그 레벨: {settings.log_level}")
        print(f"✅ 로그 파일: {settings.log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 테스트 실패: {e}")
        return False

async def test_logging():
    """로깅 시스템 테스트"""
    print("\n🔍 로깅 시스템 테스트 시작...")
    
    try:
        from utils.logger import get_logger
        
        # 로거 생성 및 테스트
        logger = get_logger("test_logger")
        
        logger.debug("디버그 메시지 테스트")
        logger.info("정보 메시지 테스트")
        logger.warning("경고 메시지 테스트")
        logger.error("오류 메시지 테스트")
        
        print("✅ 로깅 시스템 정상 작동")
        
        # 로그 파일 생성 확인
        from utils.config import get_settings
        settings = get_settings()
        log_file = Path(settings.log_file)
        
        if log_file.exists():
            print(f"✅ 로그 파일 생성 확인: {log_file}")
        else:
            print(f"⚠️ 로그 파일이 아직 생성되지 않음: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 로깅 시스템 테스트 실패: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 FastAPI 서버 기본 구조 테스트 시작\n")
    
    tests = [
        ("모듈 임포트", test_imports),
        ("FastAPI 앱 생성", test_app_creation),
        ("설정", test_configuration),
        ("로깅 시스템", test_logging)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n총 테스트: {len(results)}")
    print(f"통과: {passed}")
    print(f"실패: {failed}")
    
    if failed == 0:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return True
    else:
        print(f"\n⚠️ {failed}개의 테스트가 실패했습니다.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)