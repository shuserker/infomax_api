#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 관리 API 엔드포인트
포팅된 POSCO 관리자 로직을 API로 제공
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# 포팅된 POSCO 관리자 임포트
from core.posco_manager import PoscoManager

logger = logging.getLogger(__name__)
router = APIRouter()

# 데이터 모델
class DeploymentRequest(BaseModel):
    target_branch: str = "main"

class BranchSwitchRequest(BaseModel):
    target_branch: str

# 전역 POSCO 관리자 인스턴스
_posco_manager = None

def get_posco_manager():
    """POSCO 관리자 인스턴스 반환"""
    global _posco_manager
    if _posco_manager is None:
        _posco_manager = PoscoManager()
    return _posco_manager

@router.get("/status")
async def get_posco_status(posco_manager = Depends(get_posco_manager)):
    """POSCO 시스템 상태 조회"""
    logger.info("POSCO 시스템 상태 조회 요청")
    
    try:
        status = await posco_manager.get_deployment_status()
        return status
    except Exception as e:
        logger.error(f"POSCO 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="POSCO 상태 조회 중 오류가 발생했습니다")

@router.post("/deployment/start")
async def start_deployment(request: DeploymentRequest, 
                          posco_manager = Depends(get_posco_manager)):
    """배포 시작"""
    logger.info(f"배포 시작 요청: {request.target_branch}")
    
    try:
        result = await posco_manager.start_deployment(request.target_branch)
        return result
    except Exception as e:
        logger.error(f"배포 시작 실패: {e}")
        raise HTTPException(status_code=500, detail="배포 시작 중 오류가 발생했습니다")

@router.post("/deployment/stop")
async def stop_deployment(posco_manager = Depends(get_posco_manager)):
    """배포 중지"""
    logger.info("배포 중지 요청")
    
    try:
        result = await posco_manager.stop_deployment()
        return result
    except Exception as e:
        logger.error(f"배포 중지 실패: {e}")
        raise HTTPException(status_code=500, detail="배포 중지 중 오류가 발생했습니다")

@router.get("/deployment/status")
async def get_deployment_status(posco_manager = Depends(get_posco_manager)):
    """배포 상태 조회"""
    logger.info("배포 상태 조회 요청")
    
    try:
        status = await posco_manager.get_deployment_status()
        return status
    except Exception as e:
        logger.error(f"배포 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="배포 상태 조회 중 오류가 발생했습니다")

@router.get("/github-pages/status")
async def get_github_pages_status(posco_manager = Depends(get_posco_manager)):
    """GitHub Pages 상태 조회"""
    logger.info("GitHub Pages 상태 조회 요청")
    
    try:
        status = await posco_manager.get_deployment_status()
        github_pages_status = status.get('github_pages_status', {})
        return github_pages_status
    except Exception as e:
        logger.error(f"GitHub Pages 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="GitHub Pages 상태 조회 중 오류가 발생했습니다")

@router.post("/monitoring/start")
async def start_posco_monitoring(posco_manager = Depends(get_posco_manager)):
    """POSCO 시스템 모니터링 시작"""
    logger.info("POSCO 모니터링 시작 요청")
    
    try:
        await posco_manager.start_monitoring()
        return {"message": "POSCO 시스템 모니터링이 시작되었습니다"}
    except Exception as e:
        logger.error(f"POSCO 모니터링 시작 실패: {e}")
        raise HTTPException(status_code=500, detail="POSCO 모니터링 시작 중 오류가 발생했습니다")

@router.post("/monitoring/stop")
async def stop_posco_monitoring(posco_manager = Depends(get_posco_manager)):
    """POSCO 시스템 모니터링 중지"""
    logger.info("POSCO 모니터링 중지 요청")
    
    try:
        await posco_manager.stop_monitoring()
        return {"message": "POSCO 시스템 모니터링이 중지되었습니다"}
    except Exception as e:
        logger.error(f"POSCO 모니터링 중지 실패: {e}")
        raise HTTPException(status_code=500, detail="POSCO 모니터링 중지 중 오류가 발생했습니다")

@router.get("/branch/current")
async def get_current_branch(posco_manager = Depends(get_posco_manager)):
    """현재 브랜치 조회"""
    logger.info("현재 브랜치 조회 요청")
    
    try:
        status = await posco_manager.get_deployment_status()
        return {"current_branch": status.get('current_branch', 'unknown')}
    except Exception as e:
        logger.error(f"현재 브랜치 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="현재 브랜치 조회 중 오류가 발생했습니다")

@router.get("/deployment/history")
async def get_deployment_history(posco_manager = Depends(get_posco_manager)):
    """배포 히스토리 조회"""
    logger.info("배포 히스토리 조회 요청")
    
    try:
        status = await posco_manager.get_deployment_status()
        return {"deployment_history": status.get('deployment_history', [])}
    except Exception as e:
        logger.error(f"배포 히스토리 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="배포 히스토리 조회 중 오류가 발생했습니다")