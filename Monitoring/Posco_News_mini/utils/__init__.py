# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 통합 유틸리티 모듈

로깅, 캐시 관리, 날짜/시간 처리 등의 유틸리티 함수들을 통합하여 제공합니다.
"""

import json
import os
import hashlib
import logging
import sys
from datetime import datetime


# ============================================================================
# 로깅 유틸리티
# ============================================================================

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
        level (str): 로그 레벨 ("INFO", "ERROR", "WARNING", "SUCCESS")
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


# ============================================================================
# 캐시 관리 유틸리티
# ============================================================================

def get_data_hash(data):
    """
    데이터의 MD5 해시값 계산 (변경사항 감지용)
    
    Args:
        data (dict): 해시값을 계산할 데이터
        
    Returns:
        str: MD5 해시값 (32자리 16진수)
             데이터가 None이면 None 반환
    """
    if not data:
        return None
    data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()


def load_cache(cache_file):
    """
    캐시 파일에서 이전 데이터 로드
    
    Args:
        cache_file (str): 캐시 파일 경로
        
    Returns:
        tuple: (cached_data, last_hash)
               캐시 파일이 없거나 읽기 실패 시 (None, None) 반환
    """
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                return cache.get('data'), cache.get('last_hash')
        except Exception as e:
            print(f"❌ 캐시 로드 오류: {e}")
    return None, None


def save_cache(cache_file, data, data_hash):
    """
    현재 데이터를 캐시 파일에 저장
    
    Args:
        cache_file (str): 캐시 파일 경로
        data (dict): 저장할 뉴스 데이터
        data_hash (str): 데이터의 해시값
    """
    try:
        cache = {
            'last_hash': data_hash,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ 캐시 저장 오류: {e}")


# ============================================================================
# 날짜/시간 유틸리티
# ============================================================================

def format_datetime(date_str, time_str):
    """
    API 날짜/시간 문자열을 읽기 쉬운 형태로 변환
    
    Args:
        date_str (str): 날짜 문자열 (YYYYMMDD 형식)
        time_str (str): 시간 문자열 (HHMMSS 또는 변형 형식)
        
    Returns:
        str: 포맷된 날짜시간 문자열 (YYYY-MM-DD HH:MM:SS)
             데이터가 없거나 오류 시 적절한 메시지 반환
    """
    if not date_str or not time_str:
        return "데이터 없음"
        
    try:
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        if len(time_str) >= 6:
            formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
        elif len(time_str) == 5:
            if time_str.startswith('6'):
                time_str = '0' + time_str
                formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            else:
                formatted_time = f"0{time_str[:1]}:{time_str[1:3]}:{time_str[3:5]}"
        elif len(time_str) == 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:4]}:00"
        else:
            formatted_time = time_str
        
        return f"{formatted_date} {formatted_time}"
    except:
        return "데이터 오류"


def get_today_info():
    """
    오늘 날짜 정보 반환
    
    Returns:
        dict: 오늘 날짜 정보 (kr_format, weekday, weekday_name 등)
    """
    now = datetime.now()
    return {
        'date': now.date(),
        'kr_format': now.strftime('%Y%m%d'),
        'weekday': now.weekday(),
        'weekday_name': ['월', '화', '수', '목', '금', '토', '일'][now.weekday()],
        'datetime': now
    }


def get_weekday_display():
    """
    현재 요일을 한글로 반환
    
    Returns:
        str: 요일 문자열 ('월', '화', '수', '목', '금', '토', '일')
    """
    return get_today_info()['weekday_name']


# ============================================================================
# 내보낼 함수들
# ============================================================================

__all__ = [
    # 로깅
    'setup_logger',
    'log_with_timestamp',
    
    # 캐시 관리
    'get_data_hash',
    'load_cache',
    'save_cache',
    
    # 날짜/시간
    'format_datetime',
    'get_today_info',
    'get_weekday_display'
]