# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 복원된 통합 설정

정상 커밋 a763ef84에서 복원된 설정 파일입니다.

복원일: 2025-08-12
복원 기준: 커밋 a763ef84be08b5b1dab0c0ba20594b141baec7ab
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
WATCHHAMSTER_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"
BOT_PROFILE_IMAGE_URL = "https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg"

# ==========================================
# 뉴스 타입별 설정
# ==========================================
NEWS_TYPES = {
    "newyork-market-watch": {
        "display_name": "NEWYORK MARKET WATCH", 
        "emoji": "🌆",
        "publish_days": [0, 1, 2, 3, 4, 5]
    },
    "kospi-close": {
        "display_name": "KOSPI CLOSE",
        "emoji": "📈",
        "publish_days": [0, 1, 2, 3, 4]
    },
    "exchange-rate": {
        "display_name": "EXCHANGE RATE",
        "emoji": "💱",
        "publish_days": [0, 1, 2, 3, 4]
    }
}

# ==========================================
# 모니터링 동작 설정
# ==========================================
MONITORING_CONFIG = {
    "default_interval_minutes": 60,
    "max_retry_days": 10,
    "cache_file": "posco_news_cache.json"
}

# ==========================================
# 상태 표시 설정
# ==========================================
STATUS_CONFIG = {
    "display_mode": "strict",
    "colors": {
        "all_latest": "🟢",
        "partial_latest": "🟡", 
        "all_old": "🔴"
    }
}
