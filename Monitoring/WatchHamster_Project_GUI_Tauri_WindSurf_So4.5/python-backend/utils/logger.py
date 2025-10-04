"""
로깅 유틸리티
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .config import get_settings

def setup_logging(
    name: Optional[str] = None,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """로깅 설정"""
    settings = get_settings()
    
    # 로거 생성
    logger = logging.getLogger(name or settings.app_name)
    
    # 로그 레벨 설정
    log_level = getattr(logging, (level or settings.log_level).upper())
    logger.setLevel(log_level)
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 포맷터 생성
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    if log_file or settings.log_file:
        log_path = Path(log_file or settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=settings.log_max_size,
            backupCount=settings.log_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 전파 방지 (루트 로거와 중복 방지)
    logger.propagate = False
    
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """로거 인스턴스 반환"""
    settings = get_settings()
    logger_name = name or settings.app_name
    
    # 이미 설정된 로거가 있으면 반환
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
    
    # 새로운 로거 설정
    return setup_logging(logger_name)

# 기본 로거 인스턴스
default_logger = get_logger()