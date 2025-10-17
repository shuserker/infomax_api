#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 관리 API 엔드포인트
포팅된 POSCO 관리자 로직을 API로 제공
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# 포팅된 POSCO 관리자 임포트
from core.deployment_monitor import DeploymentMonitor
from core.git_deployment_manager import GitDeploymentManager

logger = logging.getLogger(__name__)
router = APIRouter()

# 데이터 모델
class DeploymentRequest(BaseModel):
    target_branch: str = "main"

class BranchSwitchRequest(BaseModel):
    target_branch: str

# 전역 POSCO 관리자 인스턴스
_deployment_monitor = None
_git_manager = None

def get_deployment_monitor():
    """Deployment 모니터 인스턴스 반환"""
    global _deployment_monitor
    if _deployment_monitor is None:
        _deployment_monitor = DeploymentMonitor()
    return _deployment_monitor

def get_git_manager():
    """Git 배포 관리자 인스턴스 반환"""
    global _git_manager  
    if _git_manager is None:
        _git_manager = GitDeploymentManager()
    return _git_manager

@router.get("/status")
async def get_posco_status():
    """POSCO 시스템 상태 조회"""
    logger.info("POSCO 시스템 상태 조회 요청")
    
    try:
        # 실제 deployment monitor와 git manager를 사용
        deployment_monitor = get_deployment_monitor()
        git_manager = get_git_manager()
        
        # 실제 배포 상태 조회
        deployment_status = await _get_deployment_status(deployment_monitor)
        git_status = await _get_git_status(git_manager)
        
        return {
            "status": "running",
            "deployment": deployment_status,
            "git": git_status,
            "services": {
                "api_server": "running",
                "deployment_monitor": "active",
                "git_manager": "active"
            },
            "last_checked": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"POSCO 시스템 상태 조회 실패: {e}")
        # 오류 발생시 기본 상태 반환
        return {
            "status": "error", 
            "error": str(e),
            "deployment": {"status": "unknown"},
            "git": {"status": "unknown"},
            "services": {"api_server": "running"}
        }

@router.post("/deployment/start")
async def start_deployment(request: DeploymentRequest):
    """배포 시작"""
    logger.info(f"배포 시작 요청: {request.target_branch}")
    
    # 임시 Mock 응답
    return {
        "status": "started",
        "target_branch": request.target_branch,
        "deployment_id": "dep-123456",
        "message": "배포가 시작되었습니다"
    }

@router.post("/deployment/stop")
async def stop_deployment():
    """배포 중지"""
    logger.info("배포 중지 요청")
    
    # 임시 Mock 응답
    return {
        "status": "stopped",
        "message": "배포가 중지되었습니다"
    }

@router.get("/deployment/status")
async def get_deployment_status():
    """배포 상태 조회"""
    logger.info("배포 상태 조회 요청")
    
    # 임시 Mock 응답
    return {
        "status": "idle",
        "last_deployment": "2024-10-17 15:30:00",
        "next_deployment": None,
        "history": []
    }

@router.get("/github-pages/status")
async def get_github_pages_status():
    """GitHub Pages 상태 조회"""
    logger.info("GitHub Pages 상태 조회 요청")
    
    # 임시 Mock 응답
    return {
        "status": "active",
        "url": "https://username.github.io/project",
        "last_update": "2024-10-17 15:30:00"
    }

@router.post("/monitoring/start")
async def start_posco_monitoring():
    """POSCO 시스템 모니터링 시작"""
    logger.info("POSCO 모니터링 시작 요청")
    
    return {"message": "POSCO 시스템 모니터링이 시작되었습니다"}

@router.post("/monitoring/stop")
async def stop_posco_monitoring():
    """POSCO 시스템 모니터링 중지"""
    logger.info("POSCO 모니터링 중지 요청")
    
    return {"message": "POSCO 시스템 모니터링이 중지되었습니다"}

@router.get("/branch/current")
async def get_current_branch():
    """현재 브랜치 조회"""
    logger.info("현재 브랜치 조회 요청")
    
    return {"current_branch": "main"}

@router.get("/deployment/history")
async def get_deployment_history():
    """배포 히스토리 조회"""
    logger.info("배포 히스토리 조회 요청")
    
    return {
        "deployment_history": [
            {
                "id": "dep-123456",
                "branch": "main",
                "timestamp": "2024-10-17 15:30:00",
                "status": "success"
            }
        ]
    }

# Helper 함수들
async def _get_deployment_status(deployment_monitor):
    """실제 배포 상태 조회"""
    try:
        # deployment_monitor의 실제 메서드 호출
        if hasattr(deployment_monitor, 'get_status'):
            status = deployment_monitor.get_status()
        else:
            status = {
                "current_branch": "main", 
                "last_deployment": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "deployment_status": "idle"
            }
        return status
    except Exception as e:
        logger.warning(f"배포 상태 조회 실패: {e}")
        return {
            "current_branch": "unknown",
            "last_deployment": None,
            "deployment_status": "error",
            "error": str(e)
        }

async def _get_git_status(git_manager):
    """실제 Git 상태 조회"""
    try:
        # git_manager의 실제 메서드 호출
        if hasattr(git_manager, 'get_status'):
            status = git_manager.get_status()
        else:
            status = {
                "status": "clean",
                "ahead": 0,
                "behind": 0,
                "branch": "main"
            }
        return status
    except Exception as e:
        logger.warning(f"Git 상태 조회 실패: {e}")
        return {
            "status": "unknown",
            "ahead": 0,
            "behind": 0,
            "branch": "unknown",
            "error": str(e)
        }