# -*- coding: utf-8 -*-
"""
캐시 관리 유틸리티 함수들
"""

import json
import os
import hashlib
from datetime import datetime


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