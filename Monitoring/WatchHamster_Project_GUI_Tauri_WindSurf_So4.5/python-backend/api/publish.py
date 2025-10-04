"""
Git Pages 배포 상태 API
publish 브랜치의 배포 상태 조회 (main 브랜치는 비공개)
"""

import logging
import subprocess
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class PublishStatus(BaseModel):
    """배포 상태"""
    branch: str
    last_deploy: str
    deploy_status: str
    commit_hash: str
    commit_message: str
    commit_date: str
    pages_url: str
    is_public: bool


def run_git_command(command: list) -> str:
    """Git 명령 실행"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Git 명령 실패: {e}")
        return ""


@router.get("/status", response_model=PublishStatus)
async def get_publish_status():
    """publish 브랜치 배포 상태 조회"""
    try:
        # publish 브랜치 최신 커밋 정보
        commit_hash = run_git_command(['git', 'rev-parse', 'origin/publish'])
        commit_message = run_git_command(['git', 'log', 'origin/publish', '-1', '--pretty=%s'])
        commit_date = run_git_command(['git', 'log', 'origin/publish', '-1', '--pretty=%ci'])
        
        # 배포 상태 (최근 커밋 시간으로 판단)
        try:
            commit_datetime = datetime.strptime(commit_date.split()[0], '%Y-%m-%d')
            days_ago = (datetime.now() - commit_datetime).days
            
            if days_ago < 7:
                deploy_status = 'success'
            elif days_ago < 30:
                deploy_status = 'pending'
            else:
                deploy_status = 'failed'
        except:
            deploy_status = 'success'
        
        # GitHub Pages URL
        pages_url = "https://shuserker.github.io/infomax_api/"
        
        return PublishStatus(
            branch="publish",
            last_deploy=commit_date if commit_date else datetime.now().isoformat(),
            deploy_status=deploy_status,
            commit_hash=commit_hash if commit_hash else "unknown",
            commit_message=commit_message if commit_message else "배포 정보 없음",
            commit_date=commit_date if commit_date else datetime.now().isoformat(),
            pages_url=pages_url,
            is_public=True
        )
        
    except Exception as e:
        logger.error(f"배포 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_publish_info():
    """배포 정보 간단 조회"""
    try:
        commit_hash = run_git_command(['git', 'rev-parse', 'origin/publish'])
        commit_message = run_git_command(['git', 'log', 'origin/publish', '-1', '--pretty=%s'])
        
        return {
            "branch": "publish",
            "commit": commit_hash[:7] if commit_hash else "unknown",
            "message": commit_message if commit_message else "배포 정보 없음",
            "url": "https://shuserker.github.io/infomax_api/",
            "is_public": True
        }
        
    except Exception as e:
        logger.error(f"배포 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
