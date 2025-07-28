# -*- coding: utf-8 -*-
"""
로깅 관련 유틸리티 함수들
"""

import logging
import sys
from datetime import datetime


def setup_logger(name, log_file=None, level=logging.INFO):
    """
    로거 설정
    
    Args:
        name (str): 로거 이름
        log_file (str, optional): 로그 파일 경로
        level (int): 로그 레벨
        
    Returns:
        logging.Logger: 설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (선택사항)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_with_timestamp(message, level="INFO"):
    """
    타임스탬프와 함께 로그 메시지 출력
    
    Args:
        message (str): 로그 메시지
        level (str): 로그 레벨 ("INFO", "ERROR", "WARNING")
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level_emoji = {
        "INFO": "ℹ️",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "SUCCESS": "✅"
    }
    emoji = level_emoji.get(level, "📝")
    print(f"[{timestamp}] {emoji} {message}")