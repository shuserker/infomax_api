"""
설정 관리 유틸리티
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버 설정
    app_name: str = "WatchHamster Backend"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API 설정
    api_host: str = "127.0.0.1"
    api_port: int = 9001
    api_prefix: str = "/api"
    
    # CORS 설정 (환경별로 설정 가능)
    cors_origins: str = os.getenv("CORS_ORIGINS", 
        "http://localhost:1420,http://localhost:3000,http://localhost:9001,http://127.0.0.1:9001,tauri://localhost,https://tauri.localhost")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins를 리스트로 반환"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "watchhamster-backend.log"
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # 데이터베이스 설정 (향후 사용)
    database_url: str = "sqlite:///./watchhamster.db"
    
    # 보안 설정
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # 외부 서비스 설정
    webhook_timeout: int = 30
    max_webhook_retries: int = 3
    
    # 모니터링 설정
    metrics_retention_hours: int = 24
    health_check_interval: int = 60
    
    # 기존 WatchHamster 설정 (마이그레이션용)
    legacy_config_path: str = "../../config"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# 전역 설정 인스턴스
_settings = None

def get_settings() -> Settings:
    """설정 인스턴스 반환 (싱글톤)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings():
    """설정 다시 로드"""
    global _settings
    _settings = None
    return get_settings()