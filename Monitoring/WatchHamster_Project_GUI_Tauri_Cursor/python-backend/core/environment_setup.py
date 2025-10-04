#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 복구 - 환경 설정 복원 스크립트

정상 커밋 a763ef84의 환경 설정을 복원하는 스크립트입니다.

주요 기능:
- 환경 변수 설정
- 디렉토리 구조 생성
- 설정 파일 복원
- 권한 설정

작성자: AI Assistant
생성일: 2025-08-12
수정일: 2025-08-16 (Import 경로 수정)
"""

import os
import sys
import json
import shutil
from pathlib import Path

class EnvironmentSetup:
    """환경 설정 복원 클래스"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent
        self.settings_file = self.script_dir / "environment_settings.json"
        
        # 설정 로드
        self.load_settings()
    
    def load_settings(self):
        """설정 파일 로드"""
        try:
            # 새로운 구조에서 설정 파일 경로
            config_path = self.script_dir.parent / "config" / "environment_settings.json"
            if not config_path.exists():
                # 레거시 경로 fallback
                config_path = self.script_dir / "environment_settings.json"
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
            print("✅ 환경 설정 파일 로드 완료")
        except Exception as e:
            print(f"❌ 환경 설정 파일 로드 실패: {e}")
            sys.exit(1)
    
    def create_directory_structure(self):
        """필수 디렉토리 구조 생성"""
        directories = [
            "Monitoring/Posco_News_mini",
            "Monitoring/Posco_News_mini/core",
            "Monitoring/Posco_News_mini/reports",
            "Monitoring/Posco_News_mini/utils",
            "Monitoring/Posco_News_mini/docs",
            "logs",
            "cache",
            "reports"
        ]
        
        for directory in directories:
            dir_path = self.root_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 디렉토리 생성: {directory}")
    
    def restore_config_files(self):
        """설정 파일 복원"""
        # config.py 복원
        config_content = self.generate_config_py()
        config_path = self.root_dir / "Monitoring/Posco_News_mini/config.py"
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ config.py 복원 완료")
        
        # requirements.txt 복원
        requirements_src = self.script_dir / "original_requirements.txt"
        requirements_dst = self.root_dir / "requirements.txt"
        
        if requirements_src.exists():
            shutil.copy2(requirements_src, requirements_dst)
            print("✅ requirements.txt 복원 완료")
    
    def generate_config_py(self):
        """config.py 내용 생성"""
        api_config = self.settings['api_config']
        webhook_urls = self.settings['webhook_urls']
        monitoring_config = self.settings['monitoring_config']
        news_types = self.settings['news_types']
        
        return f'''# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 통합 설정 관리

복구된 설정 파일입니다.
원본 커밋 a763ef84의 설정을 기반으로 복원되었습니다.

작성자: AI Assistant (복구 시스템)
복원일: 2025-08-12
"""

# ==========================================
# API 연결 설정
# ==========================================
API_CONFIG = {{
    "url": "{api_config['url']}",
    "user": "{api_config['user']}",
    "password": "{api_config['password']}",
    "timeout": {api_config['timeout']}
}}

# ==========================================
# Dooray 웹훅 설정
# ==========================================
DOORAY_WEBHOOK_URL = "{webhook_urls['dooray_webhook_url']}"
WATCHHAMSTER_WEBHOOK_URL = "{webhook_urls['watchhamster_webhook_url']}"
BOT_PROFILE_IMAGE_URL = "{webhook_urls['bot_profile_image_url']}"

# ==========================================
# 모니터링 동작 설정
# ==========================================
MONITORING_CONFIG = {{
    "default_interval_minutes": {monitoring_config['default_interval_minutes']},
    "max_retry_days": {monitoring_config['max_retry_days']},
    "cache_file": "{monitoring_config['cache_file']}"
}}

# ==========================================
# 뉴스 타입별 설정
# ==========================================
NEWS_TYPES = {json.dumps(news_types, indent=4, ensure_ascii=False)}

# ==========================================
# 상태 표시 설정
# ==========================================
STATUS_CONFIG = {{
    "display_mode": "strict",
    "colors": {{
        "all_latest": "🟢",
        "partial_latest": "🟡",
        "all_old": "🔴"
    }}
}}
'''
    
    def set_file_permissions(self):
        """파일 권한 설정"""
        # 핵심 디렉토리만 대상으로 제한하여 긴 파일명 문제 회피
        target_dirs = [
            "Monitoring/Posco_News_mini",
            "recovery_config"
        ]
        
        executable_patterns = [
            "*.sh",
            "*.command",
            "*.py"
        ]
        
        for target_dir in target_dirs:
            dir_path = self.root_dir / target_dir
            if dir_path.exists():
                for pattern in executable_patterns:
                    try:
                        for file_path in dir_path.rglob(pattern):
                            if file_path.is_file():
                                # 실행 권한 추가
                                current_mode = file_path.stat().st_mode
                                file_path.chmod(current_mode | 0o755)
                    except OSError as e:
                        # 파일명이 너무 긴 경우 등의 오류는 무시
                        print(f"⚠️ 권한 설정 건너뜀 (파일명 문제): {e}")
                        continue
        
        print("✅ 파일 권한 설정 완료")
    
    def create_cache_files(self):
        """캐시 파일 초기화"""
        cache_files = [
            "posco_news_cache.json",
            "posco_news_historical_cache.json",
            "posco_business_day_mapping.json"
        ]
        
        for cache_file in cache_files:
            cache_path = self.root_dir / cache_file
            if not cache_path.exists():
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
                print(f"📄 캐시 파일 생성: {cache_file}")
    
    def run_setup(self):
        """전체 환경 설정 실행"""
        print("🔧 POSCO 시스템 환경 설정 복원 시작...")
        print("=" * 50)
        
        try:
            self.create_directory_structure()
            print()
            
            self.restore_config_files()
            print()
            
            self.set_file_permissions()
            print()
            
            self.create_cache_files()
            print()
            
            print("=" * 50)
            print("✅ 환경 설정 복원 완료!")
            print()
            print("다음 단계:")
            print("1. 핵심 로직 파일들 복원")
            print("2. 불필요한 파일들 정리")
            print("3. 시스템 테스트 실행")
            
        except Exception as e:
            print(f"❌ 환경 설정 복원 실패: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup = EnvironmentSetup()
    setup.run_setup()