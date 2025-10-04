#!/usr/bin/env python3
"""
InfoMax API 프록시 서버 시작 스크립트
워치햄스터 시스템과 함께 백그라운드에서 자동 실행되는 프록시 서버
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python 패스에 추가
sys.path.insert(0, str(Path(__file__).parent))

try:
    import uvicorn
    from main import app
    from utils.logger import get_logger
    from utils.config import get_settings
except ImportError as e:
    print(f"❌ 필수 모듈을 가져올 수 없습니다: {e}")
    print("pip install -r requirements.txt 를 실행하세요.")
    sys.exit(1)

logger = get_logger(__name__)
settings = get_settings()


def check_port_available(port: int) -> bool:
    """포트 사용 가능 여부 확인"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False


def main():
    """InfoMax API 프록시 서버 시작"""
    
    print("🚀 InfoMax API 프록시 서버 시작 중...")
    
    # 포트 설정 (8000이 사용 중이면 8001 사용)
    port = 8001
    if not check_port_available(port):
        print(f"❌ 포트 {port}가 이미 사용 중입니다.")
        print("기존 서버를 종료하거나 다른 포트를 사용하세요.")
        return
    
    # 환경 설정
    os.environ.setdefault("FASTAPI_ENV", "development")
    
    print(f"🔧 서버 설정:")
    print(f"   - 포트: {port}")
    print(f"   - 디버그 모드: {settings.debug}")
    print(f"   - InfoMax 프록시: 활성화")
    print(f"   - 로그 레벨: INFO")
    
    try:
        # UV(i)corn 서버 실행
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=settings.debug,
            access_log=True,
            log_level="info",
            server_header=False,
            date_header=False
        )
    except KeyboardInterrupt:
        print("\n🛑 서버가 사용자에 의해 종료되었습니다.")
    except Exception as e:
        logger.error(f"❌ 서버 실행 오류: {e}")
        print(f"❌ 서버 실행 중 오류가 발생했습니다: {e}")
    finally:
        print("🏁 InfoMax API 프록시 서버가 종료되었습니다.")


if __name__ == "__main__":
    main()
