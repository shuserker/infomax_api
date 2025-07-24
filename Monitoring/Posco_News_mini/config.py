# POSCO 뉴스 모니터 설정 파일

# Dooray 웹훅 URL (Dooray에서 생성한 웹훅 URL을 여기에 입력)
DOORAY_WEBHOOK_URL = "https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ"

# API 설정
API_CONFIG = {
    "url": "https://dev-global-api.einfomax.co.kr/apis/posco/news",
    "username": "infomax",
    "password": "infomax!",
    "timeout": 10
}

# 모니터링 설정
MONITOR_CONFIG = {
    "check_interval_minutes": 5,  # 체크 간격 (분)
    "cache_file": "posco_news_cache.json",
    "enable_startup_notification": True,  # 시작 알림 여부
    "enable_error_notification": True     # 오류 알림 여부
}