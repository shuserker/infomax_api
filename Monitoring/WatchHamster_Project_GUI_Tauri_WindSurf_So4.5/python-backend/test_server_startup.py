#!/usr/bin/env python3
"""
서버 시작 테스트
"""

import asyncio
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

async def test_server_startup():
    """서버 시작 테스트"""
    print("🔍 서버 시작 테스트...")
    
    try:
        # 메인 모듈 임포트
        from main import app, settings, check_legacy_compatibility
        
        print(f"✅ 앱 임포트 성공: {app.title}")
        
        # 라이프사이클 함수 테스트
        await check_legacy_compatibility()
        print("✅ 호환성 체크 완료")
        
        # 라우트 확인
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(f"{route.path}")
        
        print(f"✅ 등록된 라우트: {len(routes)}개")
        for route in routes[:10]:  # 처음 10개만 표시
            print(f"   - {route}")
        
        if len(routes) > 10:
            print(f"   ... 및 {len(routes) - 10}개 더")
        
        # 설정 확인
        print(f"✅ 서버 설정:")
        print(f"   - 호스트: {settings.api_host}")
        print(f"   - 포트: {settings.api_port}")
        print(f"   - 디버그: {settings.debug}")
        print(f"   - CORS Origins: {len(settings.cors_origins_list)}개")
        
        return True
        
    except Exception as e:
        print(f"❌ 서버 시작 테스트 실패: {e}")
        return False

async def main():
    """메인 함수"""
    print("🚀 서버 시작 테스트 시작\n")
    
    success = await test_server_startup()
    
    if success:
        print("\n🎉 서버 시작 테스트 성공!")
        print("서버를 실제로 시작하려면 'python main.py'를 실행하세요.")
    else:
        print("\n❌ 서버 시작 테스트 실패")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)