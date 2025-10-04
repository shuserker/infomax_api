"""
회사 관리 API
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database import get_db
from database.models import (
    Company, CompanyCreate, CompanyUpdate, CompanyDetail,
    WebhookConfig, APIConfig
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=dict)
async def create_company(company: CompanyCreate):
    """
    신규 회사 추가
    
    - UI에서 폼 작성 후 호출
    - 회사 정보 + 웹훅 설정 + API 설정 일괄 등록
    """
    db = get_db()
    
    try:
        # 1. 회사 기본 정보 저장
        company_data = {
            'id': company.id,
            'name': company.name,
            'display_name': company.display_name,
            'logo_url': company.logo_url,
            'is_active': company.is_active
        }
        
        company_id = db.create_company(company_data)
        logger.info(f"회사 생성: {company_id}")
        
        # 2. 웹훅 설정 저장
        webhook_ids = []
        for channel_name, webhook_data in company.webhooks.items():
            webhook_config = {
                'company_id': company_id,
                'channel_name': channel_name,
                'webhook_url': webhook_data['url'],
                'bot_name': webhook_data['bot_name'],
                'bot_icon': webhook_data['bot_icon'],
                'is_active': True
            }
            webhook_id = db.create_webhook_config(webhook_config)
            webhook_ids.append(webhook_id)
            logger.info(f"웹훅 설정 생성: {channel_name} (ID: {webhook_id})")
        
        # 3. API 설정 저장
        api_ids = []
        for api_name, api_data in company.api_config.items():
            api_config = {
                'company_id': company_id,
                'api_name': api_name,
                'api_url': api_data['url'],
                'api_token': api_data.get('token'),
                'config': api_data.get('config', {}),
                'is_active': True
            }
            api_id = db.create_api_config(api_config)
            api_ids.append(api_id)
            logger.info(f"API 설정 생성: {api_name} (ID: {api_id})")
        
        return {
            'status': 'success',
            'company_id': company_id,
            'message': f'{company.name} 추가 완료',
            'webhook_count': len(webhook_ids),
            'api_count': len(api_ids)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"회사 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"회사 생성 실패: {str(e)}")


@router.get("", response_model=List[Company])
async def get_companies(active_only: bool = Query(False, description="활성 회사만 조회")):
    """
    전체 회사 목록 조회
    
    - 회사 관리 페이지에서 사용
    - 회사 선택 드롭다운에서 사용
    """
    db = get_db()
    
    try:
        companies = db.get_all_companies(active_only=active_only)
        return companies
        
    except Exception as e:
        logger.error(f"회사 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"회사 목록 조회 실패: {str(e)}")


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(company_id: str):
    """
    회사 상세 정보 조회
    
    - 회사별 대시보드에서 사용
    - 회사 수정 폼에서 사용
    """
    db = get_db()
    
    try:
        # 회사 기본 정보
        company = db.get_company(company_id)
        if not company:
            raise HTTPException(status_code=404, detail=f"회사를 찾을 수 없습니다: {company_id}")
        
        # 웹훅 설정
        webhooks = db.get_webhook_configs(company_id)
        
        # API 설정
        api_configs = db.get_api_configs(company_id)
        
        # 통계
        stats = db.get_webhook_stats(company_id)
        
        # 마지막 활동
        logs = db.get_webhook_logs(company_id=company_id, limit=1)
        last_activity = logs[0]['timestamp'] if logs else None
        
        return {
            'company': company,
            'webhooks': webhooks,
            'api_configs': api_configs,
            'stats': stats,
            'last_activity': last_activity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회사 상세 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"회사 상세 조회 실패: {str(e)}")


@router.put("/{company_id}", response_model=dict)
async def update_company(company_id: str, company_update: CompanyUpdate):
    """
    회사 정보 수정
    
    - 회사 관리 페이지에서 사용
    """
    db = get_db()
    
    try:
        # 회사 존재 확인
        company = db.get_company(company_id)
        if not company:
            raise HTTPException(status_code=404, detail=f"회사를 찾을 수 없습니다: {company_id}")
        
        # 수정할 데이터만 추출
        update_data = company_update.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 데이터가 없습니다")
        
        # 업데이트 실행
        success = db.update_company(company_id, update_data)
        
        if success:
            return {
                'status': 'success',
                'company_id': company_id,
                'message': f'{company_id} 수정 완료'
            }
        else:
            raise HTTPException(status_code=400, detail="회사 수정 실패")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회사 수정 실패: {e}")
        raise HTTPException(status_code=500, detail=f"회사 수정 실패: {str(e)}")


@router.delete("/{company_id}", response_model=dict)
async def delete_company(company_id: str):
    """
    회사 삭제
    
    - 회사 관리 페이지에서 사용
    - CASCADE로 웹훅 설정, API 설정, 로그도 함께 삭제
    """
    db = get_db()
    
    try:
        # 회사 존재 확인
        company = db.get_company(company_id)
        if not company:
            raise HTTPException(status_code=404, detail=f"회사를 찾을 수 없습니다: {company_id}")
        
        # 삭제 실행
        success = db.delete_company(company_id)
        
        if success:
            logger.info(f"회사 삭제 완료: {company_id}")
            return {
                'status': 'success',
                'company_id': company_id,
                'message': f'{company["name"]} 삭제 완료'
            }
        else:
            raise HTTPException(status_code=400, detail="회사 삭제 실패")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회사 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"회사 삭제 실패: {str(e)}")


@router.get("/{company_id}/webhooks")
async def get_company_webhooks(company_id: str):
    """
    회사별 웹훅 설정 조회
    """
    db = get_db()
    
    try:
        webhooks = db.get_webhook_configs(company_id)
        return webhooks
        
    except Exception as e:
        logger.error(f"웹훅 설정 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"웹훅 설정 조회 실패: {str(e)}")


@router.get("/{company_id}/api-configs")
async def get_company_api_configs(company_id: str):
    """
    회사별 API 설정 조회
    """
    db = get_db()
    
    try:
        api_configs = db.get_api_configs(company_id)
        return api_configs
        
    except Exception as e:
        logger.error(f"API 설정 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"API 설정 조회 실패: {str(e)}")


@router.get("/{company_id}/stats", response_model=dict)
async def get_company_stats(company_id: str):
    """
    회사별 통계 조회
    
    - 회사별 대시보드에서 사용
    """
    db = get_db()
    
    try:
        stats = db.get_webhook_stats(company_id)
        return stats
        
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
