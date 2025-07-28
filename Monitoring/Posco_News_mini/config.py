# -*- coding: utf-8 -*-
"""
POSCO 뉴스 모니터링 시스템 - 통합 설정 관리

모든 설정값을 중앙 집중식으로 관리하는 설정 파일입니다.

주요 설정 그룹:
- API_CONFIG: 뉴스 API 연결 설정 (인증, URL, 타임아웃)
- MONITORING_CONFIG: 모니터링 동작 설정 (간격, 재시도, 캐시)
- STATUS_CONFIG: 상태 표시 설정 (색상, 이모지, 표시 모드)
- NEWS_TYPES: 뉴스 타입별 설정 (발행 요일, 표시명, 이모지)
- DOORAY_WEBHOOK_URL: Dooray 알림 웹훅 URL

설정 변경 시 주의사항:
- API 설정 변경 후 연결 테스트 권장
- 웹훅 URL 변경 시 알림 테스트 권장
- 뉴스 타입 설정 변경 시 발행 요일 확인

작성자: AI Assistant
최종 수정: 2025-07-28 (최적화)
"""

# ==========================================
# API 연결 설정
# ==========================================
API_CONFIG = {
    # POSCO 뉴스 API 엔드포인트 URL
    "url": "https://dev-global-api.einfomax.co.kr/apis/posco/news",
    
    # API 인증 정보
    "user": "infomax",
    "password": "infomax!",
    
    # 요청 타임아웃 (초) - 네트워크 지연 시 조정
    "timeout": 10
}

# ==========================================
# Dooray 웹훅 설정
# ==========================================
# POSCO 뉴스 알림용 웹훅 (뉴스 변경사항, 상태 알림)
DOORAY_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"

# 워치햄스터 전용 웹훅 (시스템 상태, 오류, 업데이트 알림)
WATCHHAMSTER_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"

# 봇 프로필 이미지 URL (POSCO 로고)
# GitHub Raw URL 사용 - 로고 변경 시 이 URL 업데이트
BOT_PROFILE_IMAGE_URL = "https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco_logo_mini.jpg"

# ==========================================
# 모니터링 동작 설정
# ==========================================
MONITORING_CONFIG = {
    # 기본 모니터링 간격 (분) - run_monitor.py 4번 옵션에서 사용
    "default_interval_minutes": 60,
    
    # 직전 데이터 검색 최대 일수 - 영업일 비교 시 과거 데이터 검색 범위
    "max_retry_days": 10,
    
    # 캐시 파일명 - 뉴스 데이터 캐싱용
    "cache_file": "posco_news_cache.json"
}

# ==========================================
# 상태 표시 설정
# ==========================================
STATUS_CONFIG = {
    # 상태 판단 모드
    # "strict": 엄격 모드 (모든 뉴스가 오늘 발행되어야 최신)
    # "lenient": 관대 모드 (일부 뉴스만 오늘 발행되어도 최신)
    "display_mode": "strict",
    
    # 상태별 색상 및 이모지
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
    # 환율 관련 뉴스
    "exchange-rate": {
        "display_name": "EXCHANGE RATE",        # 알림에 표시될 이름
        "emoji": "",                          # 뉴스 타입 이모지
        "publish_days": [0, 1, 2, 3, 4]        # 발행 요일 (월-금)
    },
    
    # 뉴욕 시장 동향 뉴스
    "newyork-market-watch": {
        "display_name": "NEWYORK MARKET WATCH", 
        "emoji": "",
        "publish_days": [0, 1, 2, 3, 4, 5]     # 발행 요일 (월-토)
    },
    
    # 코스피 마감 뉴스
    "kospi-close": {
        "display_name": "KOSPI CLOSE",
        "emoji": "",
        "publish_days": [0, 1, 2, 3, 4]        # 발행 요일 (월-금)
    }
}

# 요일 코드 참조:
# 0=월요일, 1=화요일, 2=수요일, 3=목요일, 4=금요일, 5=토요일, 6=일요일