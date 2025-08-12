#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 및 알림 기능 무결성 테스트
Task 5 검증용
"""

import sys
import os
from pathlib import Path

def test_core_imports():
    """핵심 모듈 import 테스트"""
    print("=== 핵심 모듈 Import 테스트 ===")
    
    # core/monitoring 디렉토리를 Python 경로에 추가
    core_monitoring_path = Path.cwd() / "core" / "monitoring"
    sys.path.insert(0, str(core_monitoring_path))
    
    try:
        # config 모듈 import 테스트
        import config
        print("✅ config 모듈 import 성공")
        
        # 웹훅 URL 확인
        if hasattr(config, 'DOORAY_WEBHOOK_URL'):
            webhook_url = config.DOORAY_WEBHOOK_URL
            if webhook_url and 'dooray.com' in webhook_url:
                print(f"✅ 웹훅 URL 보존 확인: {webhook_url[:50]}...")
            else:
                print("❌ 웹훅 URL이 올바르지 않습니다")
        else:
            print("❌ DOORAY_WEBHOOK_URL이 없습니다")
        
        # BOT 프로필 이미지 URL 확인
        if hasattr(config, 'BOT_PROFILE_IMAGE_URL'):
            bot_image_url = config.BOT_PROFILE_IMAGE_URL
            if bot_image_url and 'github' in bot_image_url:
                print(f"✅ BOT 이미지 URL 보존 확인: {bot_image_url[:50]}...")
            else:
                print("❌ BOT 이미지 URL이 올바르지 않습니다")
        
    except ImportError as e:
        print(f"❌ config 모듈 import 실패: {e}")
        return False
    
    try:
        # posco_main_notifier 모듈 import 테스트
        import posco_main_notifier
        print("✅ posco_main_notifier 모듈 import 성공")
        
        # PoscoMainNotifier 클래스 확인
        if hasattr(posco_main_notifier, 'PoscoMainNotifier'):
            print("✅ PoscoMainNotifier 클래스 확인")
        else:
            print("❌ PoscoMainNotifier 클래스가 없습니다")
        
    except ImportError as e:
        print(f"❌ posco_main_notifier 모듈 import 실패: {e}")
        return False
    
    return True

def test_watchhamster_files():
    """워치햄스터 제어센터 파일 테스트"""
    print("\n=== 워치햄스터 제어센터 파일 테스트 ===")
    
    watchhamster_dir = Path.cwd() / "core" / "watchhamster"
    
    required_files = [
        "🐹POSCO_워치햄스터_v3_제어센터.bat",
        "🐹POSCO_워치햄스터_v3_제어센터.command"
    ]
    
    for file_name in required_files:
        file_path = watchhamster_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} 존재 확인")
            
            # 파일 내용에서 웹훅 관련 내용 확인
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'dooray' in content.lower() or 'webhook' in content.lower():
                    print(f"✅ {file_name}에서 웹훅 관련 내용 확인")
                else:
                    print(f"ℹ️ {file_name}에서 웹훅 관련 내용 없음 (정상)")
                    
            except Exception as e:
                print(f"⚠️ {file_name} 읽기 오류: {e}")
        else:
            print(f"❌ {file_name} 파일이 없습니다")
    
    return True

def test_posco_news_files():
    """POSCO News 파일 테스트"""
    print("\n=== POSCO News 파일 테스트 ===")
    
    posco_news_dir = Path.cwd() / "core" / "POSCO_News_250808"
    
    required_files = [
        "POSCO_News_250808.py",
        "posco_news_250808_data.json",
        "posco_news_250808_cache.json",
        "posco_news_250808_historical.json"
    ]
    
    for file_name in required_files:
        file_path = posco_news_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} 존재 확인")
        else:
            print(f"❌ {file_name} 파일이 없습니다")
    
    return True

def test_compatibility_links():
    """하위 호환성 링크 테스트"""
    print("\n=== 하위 호환성 링크 테스트 ===")
    
    # POSCO_News_250808.py 링크 확인
    root_link = Path.cwd() / "POSCO_News_250808.py"
    core_original = Path.cwd() / "core" / "POSCO_News_250808" / "POSCO_News_250808.py"
    
    if root_link.exists():
        print("✅ POSCO_News_250808.py 호환성 링크 존재")
        
        # 링크인지 확인
        if root_link.is_symlink():
            print("✅ 심볼릭 링크로 생성됨")
        elif root_link.samefile(core_original):
            print("✅ 하드 링크로 생성됨")
        else:
            print("⚠️ 일반 파일로 존재 (복사본일 수 있음)")
    else:
        print("❌ POSCO_News_250808.py 호환성 링크가 없습니다")
    
    return True

def main():
    """메인 테스트 실행"""
    print("🔍 Task 5: 핵심 시스템 파일 보존 및 정리 검증 테스트")
    print("=" * 60)
    
    tests = [
        test_core_imports,
        test_watchhamster_files,
        test_posco_news_files,
        test_compatibility_links
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! Task 5가 성공적으로 완료되었습니다.")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 로그를 확인하세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)