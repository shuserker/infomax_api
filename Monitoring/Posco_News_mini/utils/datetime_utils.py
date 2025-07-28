# -*- coding: utf-8 -*-
"""
날짜/시간 관련 유틸리티 함수들
"""

from datetime import datetime


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