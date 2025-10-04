"""
POSCO 데이터 마이그레이션 스크립트

기존 POSCO 전용 시스템을 멀티 테넌트 구조로 마이그레이션
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_posco():
    """POSCO 회사 및 설정 등록"""
    
    db = get_db()
    
    logger.info("=" * 60)
    logger.info("POSCO 데이터 마이그레이션 시작")
    logger.info("=" * 60)
    
    try:
        # 1. POSCO 회사 등록
        logger.info("\n[1/4] POSCO 회사 정보 등록...")
        
        posco_company = {
            'id': 'posco',
            'name': 'POSCO',
            'display_name': '포스코',
            'logo_url': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg',
            'is_active': True
        }
        
        # 이미 존재하는지 확인
        existing = db.get_company('posco')
        if existing:
            logger.info("  ⚠️  POSCO 회사가 이미 존재합니다. 건너뜁니다.")
        else:
            company_id = db.create_company(posco_company)
            logger.info(f"  ✅ POSCO 회사 등록 완료: {company_id}")
        
        # 2. 웹훅 설정 등록
        logger.info("\n[2/4] POSCO 웹훅 설정 등록...")
        
        webhooks = [
            {
                'company_id': 'posco',
                'channel_name': 'news_main',
                'webhook_url': 'https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg',
                'bot_name': 'POSCO 뉴스 📊',
                'bot_icon': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg',
                'is_active': True
            },
            {
                'company_id': 'posco',
                'channel_name': 'watchhamster',
                'webhook_url': 'https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ',
                'bot_name': 'POSCO 워치햄스터 🎯🛡️',
                'bot_icon': 'https://raw.githubusercontent.com/shuserker/infomax_api/main/recovery_config/posco_logo_mini.jpg',
                'is_active': True
            }
        ]
        
        for webhook in webhooks:
            try:
                webhook_id = db.create_webhook_config(webhook)
                logger.info(f"  ✅ 웹훅 설정 등록: {webhook['channel_name']} (ID: {webhook_id})")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    logger.info(f"  ⚠️  웹훅 설정이 이미 존재합니다: {webhook['channel_name']}")
                else:
                    raise
        
        # 3. API 설정 등록
        logger.info("\n[3/4] POSCO API 설정 등록...")
        
        api_config = {
            'company_id': 'posco',
            'api_name': 'news_api',
            'api_url': 'https://global-api.einfomax.co.kr/apis/posco/news',
            'api_token': None,  # 실제 토큰은 별도 설정
            'config': {
                'endpoints': {
                    'newyork': '/newyork-market-watch',
                    'kospi': '/kospi-close',
                    'exchange': '/exchange-rate'
                }
            },
            'is_active': True
        }
        
        try:
            api_id = db.create_api_config(api_config)
            logger.info(f"  ✅ API 설정 등록: {api_config['api_name']} (ID: {api_id})")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                logger.info(f"  ⚠️  API 설정이 이미 존재합니다: {api_config['api_name']}")
            else:
                raise
        
        # 4. 검증
        logger.info("\n[4/4] 마이그레이션 검증...")
        
        company = db.get_company('posco')
        webhooks = db.get_webhook_configs('posco')
        api_configs = db.get_api_configs('posco')
        
        logger.info(f"  ✅ 회사: {company['name']} ({company['display_name']})")
        logger.info(f"  ✅ 웹훅 설정: {len(webhooks)}개")
        logger.info(f"  ✅ API 설정: {len(api_configs)}개")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ POSCO 데이터 마이그레이션 완료!")
        logger.info("=" * 60)
        
        logger.info("\n다음 단계:")
        logger.info("1. 서버 재시작: uvicorn main:app --reload")
        logger.info("2. API 테스트: curl http://localhost:8000/api/companies")
        logger.info("3. 웹 UI 접속: http://localhost:5173/companies")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 마이그레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_posco()
    sys.exit(0 if success else 1)
