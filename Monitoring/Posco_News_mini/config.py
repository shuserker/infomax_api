# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 통합 설정 관리

모든 설정값을 중앙 집중식으로 관리하는 설정 파일입니다.

주요 설정 그룹:
- API_CONFIG: 뉴스 API 연결 설정
- MONITORING_CONFIG: 모니터링 동작 설정
- STATUS_CONFIG: 상태 표시 설정 (색상, 이모지)
- NEWS_TYPES: 뉴스 타입별 설정 (발행 요일, 표시명)
- DOORAY_WEBHOOK_URL: Dooray 알림 웹훅 URL

작성자: AI Assistant
최종 수정: 2025-07-27
"""

# ==========================================
# API 연결 설정
# ==========================================
API_CONFIG = {
    "url": "https://dev-global-api.einfomax.co.kr/apis/posco/news",
    "user": "infomax",
    "password": "infomax!",
    "timeout": 10
}

# ==========================================
# Dooray 웹훅 설정
# ==========================================
DOORAY_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"

# ==========================================
# 모니터링 동작 설정
# ==========================================
MONITORING_CONFIG = {
    "default_interval_minutes": 60,    # 기본 모니터링 간격 (분)
    "max_retry_days": 10,              # 직전 데이터 검색 최대 일수
    "cache_file": "posco_news_cache.json"  # 캐시 파일명
}

# ==========================================
# 상태 표시 설정
# ==========================================
STATUS_CONFIG = {
    "display_mode": "strict",  # "strict" (엄격) or "lenient" (관대)
    "colors": {
        "all_latest": "🟢",    # 모든 데이터가 최신 (오늘 발행)
        "partial_latest": "🟡", # 일부만 최신 (일부 오늘 발행)
        "all_old": "🔴"        # 모든 데이터가 과거 (오늘 미발행)
    }
}

# ==========================================
# 뉴스 타입별 설정
# ==========================================
NEWS_TYPES = {
    "exchange-rate": {
        "display_name": "EXCHANGE RATE",        # 알림에 표시될 이름
        "emoji": "",                          # 뉴스 타입 이모지
        "publish_days": [0, 1, 2, 3, 4]        # 발행 요일 (월-금)
    },
    "newyork-market-watch": {
        "display_name": "NEWYORK MARKET WATCH", 
        "emoji": "",
        "publish_days": [0, 1, 2, 3, 4, 5]     # 발행 요일 (월-토)
    },
    "kospi-close": {
        "display_name": "KOSPI CLOSE",
        "emoji": "",
        "publish_days": [0, 1, 2, 3, 4]        # 발행 요일 (월-금)
    }
}

# 요일 코드: 0=월요일, 1=화요일, 2=수요일, 3=목요일, 4=금요일, 5=토요일, 6=일요일