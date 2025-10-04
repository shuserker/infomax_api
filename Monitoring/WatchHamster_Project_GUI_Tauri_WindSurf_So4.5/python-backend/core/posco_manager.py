#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 시스템 관리자 (포팅)
기존 POSCO GUI 관리자 로직을 API 엔드포인트로 변환

주요 기능:
- POSCO 뉴스 시스템 관리
- Git 브랜치 전환 및 배포 관리
- GitHub Pages 모니터링
- 실시간 상태 업데이트
"""

import logging
import asyncio
import json
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    """배포 상태"""
    IDLE = "idle"
    PREPARING = "preparing"
    SWITCHING_BRANCH = "switching_branch"
    BUILDING = "building"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"

class BranchSwitchStatus(Enum):
    """브랜치 전환 상태"""
    IDLE = "idle"
    CHECKING = "checking"
    SWITCHING = "switching"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class DeploymentSession:
    """배포 세션 정보"""
    session_id: str
    status: DeploymentStatus
    current_branch: str
    target_branch: str
    start_time: datetime
    end_time: Optional[datetime] = None
    steps_completed: List[str] = None
    current_step: str = ""
    progress_percentage: float = 0.0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []

@dataclass
class GitHubPagesStatus:
    """GitHub Pages 상태"""
    is_accessible: bool
    last_check: datetime
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None

class PoscoManager:
    """POSCO 시스템 관리자"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """POSCO 시스템 관리자 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.logger = logger
        
        # 현재 배포 세션
        self.current_deployment: Optional[DeploymentSession] = None
        self.deployment_history: List[DeploymentSession] = []
        
        # Git 상태
        self.current_branch = "main"
        self.branch_switch_status = BranchSwitchStatus.IDLE
        
        # GitHub Pages 상태
        self.github_pages_status = GitHubPagesStatus(
            is_accessible=False,
            last_check=datetime.now()
        )
        
        # 모니터링 상태
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        self.logger.info("🏭 PoscoManager 초기화 완료")
    
    async def start_monitoring(self):
        """POSCO 시스템 모니터링 시작"""
        if self.monitoring_active:
            self.logger.warning("POSCO 모니터링이 이미 실행 중입니다")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("🏭 POSCO 시스템 모니터링 시작")
    
    async def stop_monitoring(self):
        """POSCO 시스템 모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("🏭 POSCO 시스템 모니터링 중지")
    
    async def _monitoring_loop(self):
        """모니터링 메인 루프"""
        while self.monitoring_active:
            try:
                # GitHub Pages 상태 체크
                await self._check_github_pages_status()
                
                # Git 상태 체크
                await self._check_git_status()
                
                # 배포 세션 상태 체크
                if self.current_deployment:
                    await self._check_deployment_progress()
                
                # 30초마다 체크
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"POSCO 모니터링 중 오류: {e}")
                await asyncio.sleep(30)
    
    async def _check_github_pages_status(self):
        """GitHub Pages 상태 체크"""
        try:
            import aiohttp
            import time
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        "https://your-github-pages-url.github.io",  # 실제 URL로 변경
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        response_time = time.time() - start_time
                        
                        self.github_pages_status = GitHubPagesStatus(
                            is_accessible=response.status == 200,
                            last_check=datetime.now(),
                            response_time=response_time,
                            status_code=response.status
                        )
                        
                except Exception as e:
                    self.github_pages_status = GitHubPagesStatus(
                        is_accessible=False,
                        last_check=datetime.now(),
                        error_message=str(e)
                    )
                    
        except Exception as e:
            self.logger.error(f"GitHub Pages 상태 체크 실패: {e}")
    
    async def _check_git_status(self):
        """Git 상태 체크"""
        try:
            # 현재 브랜치 확인
            result = await self._run_git_command(["branch", "--show-current"])
            if result and result.strip():
                self.current_branch = result.strip()
                
        except Exception as e:
            self.logger.error(f"Git 상태 체크 실패: {e}")
    
    async def _check_deployment_progress(self):
        """배포 진행 상태 체크"""
        try:
            if not self.current_deployment:
                return
            
            # 배포 타임아웃 체크 (30분)
            if (datetime.now() - self.current_deployment.start_time).total_seconds() > 1800:
                self.current_deployment.status = DeploymentStatus.FAILED
                self.current_deployment.error_message = "배포 타임아웃"
                self.current_deployment.end_time = datetime.now()
                
                self.logger.error(f"배포 타임아웃: {self.current_deployment.session_id}")
                
        except Exception as e:
            self.logger.error(f"배포 진행 상태 체크 실패: {e}")
    
    async def start_deployment(self, target_branch: str = "main") -> Dict[str, Any]:
        """배포 시작"""
        try:
            if self.current_deployment and self.current_deployment.status in [
                DeploymentStatus.PREPARING, DeploymentStatus.SWITCHING_BRANCH,
                DeploymentStatus.BUILDING, DeploymentStatus.DEPLOYING
            ]:
                return {
                    "success": False,
                    "message": "이미 진행 중인 배포가 있습니다",
                    "current_deployment": asdict(self.current_deployment)
                }
            
            # 새 배포 세션 생성
            session_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_deployment = DeploymentSession(
                session_id=session_id,
                status=DeploymentStatus.PREPARING,
                current_branch=self.current_branch,
                target_branch=target_branch,
                start_time=datetime.now(),
                current_step="배포 준비 중"
            )
            
            # 백그라운드에서 배포 실행
            asyncio.create_task(self._execute_deployment())
            
            self.logger.info(f"배포 시작: {session_id} ({self.current_branch} -> {target_branch})")
            
            return {
                "success": True,
                "message": "배포가 시작되었습니다",
                "deployment_session": asdict(self.current_deployment)
            }
            
        except Exception as e:
            self.logger.error(f"배포 시작 실패: {e}")
            return {
                "success": False,
                "message": f"배포 시작 실패: {str(e)}"
            }
    
    async def _execute_deployment(self):
        """배포 실행"""
        try:
            if not self.current_deployment:
                return
            
            deployment = self.current_deployment
            
            # 1단계: 브랜치 전환
            deployment.status = DeploymentStatus.SWITCHING_BRANCH
            deployment.current_step = "브랜치 전환 중"
            deployment.progress_percentage = 20.0
            
            success = await self._switch_branch(deployment.target_branch)
            if not success:
                deployment.status = DeploymentStatus.FAILED
                deployment.error_message = "브랜치 전환 실패"
                deployment.end_time = datetime.now()
                return
            
            deployment.steps_completed.append("브랜치 전환 완료")
            
            # 2단계: 빌드
            deployment.status = DeploymentStatus.BUILDING
            deployment.current_step = "빌드 중"
            deployment.progress_percentage = 50.0
            
            success = await self._build_project()
            if not success:
                deployment.status = DeploymentStatus.FAILED
                deployment.error_message = "빌드 실패"
                deployment.end_time = datetime.now()
                return
            
            deployment.steps_completed.append("빌드 완료")
            
            # 3단계: 배포
            deployment.status = DeploymentStatus.DEPLOYING
            deployment.current_step = "배포 중"
            deployment.progress_percentage = 80.0
            
            success = await self._deploy_to_github_pages()
            if not success:
                deployment.status = DeploymentStatus.FAILED
                deployment.error_message = "배포 실패"
                deployment.end_time = datetime.now()
                return
            
            deployment.steps_completed.append("배포 완료")
            
            # 4단계: 완료
            deployment.status = DeploymentStatus.SUCCESS
            deployment.current_step = "배포 완료"
            deployment.progress_percentage = 100.0
            deployment.end_time = datetime.now()
            
            # 배포 히스토리에 추가
            self.deployment_history.append(deployment)
            
            self.logger.info(f"배포 완료: {deployment.session_id}")
            
        except Exception as e:
            if self.current_deployment:
                self.current_deployment.status = DeploymentStatus.FAILED
                self.current_deployment.error_message = str(e)
                self.current_deployment.end_time = datetime.now()
            
            self.logger.error(f"배포 실행 실패: {e}")
    
    async def _switch_branch(self, target_branch: str) -> bool:
        """브랜치 전환"""
        try:
            self.branch_switch_status = BranchSwitchStatus.CHECKING
            
            # 브랜치 존재 확인
            result = await self._run_git_command(["branch", "-a"])
            if target_branch not in result:
                self.logger.error(f"브랜치를 찾을 수 없습니다: {target_branch}")
                self.branch_switch_status = BranchSwitchStatus.FAILED
                return False
            
            # 브랜치 전환
            self.branch_switch_status = BranchSwitchStatus.SWITCHING
            result = await self._run_git_command(["checkout", target_branch])
            
            if "error" in result.lower():
                self.logger.error(f"브랜치 전환 실패: {result}")
                self.branch_switch_status = BranchSwitchStatus.FAILED
                return False
            
            # 최신 변경사항 가져오기
            await self._run_git_command(["pull", "origin", target_branch])
            
            self.branch_switch_status = BranchSwitchStatus.COMPLETED
            self.current_branch = target_branch
            
            return True
            
        except Exception as e:
            self.logger.error(f"브랜치 전환 실패: {e}")
            self.branch_switch_status = BranchSwitchStatus.FAILED
            return False
    
    async def _build_project(self) -> bool:
        """프로젝트 빌드"""
        try:
            # 실제 빌드 명령어 실행 (예: npm run build)
            # 여기서는 시뮬레이션
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"프로젝트 빌드 실패: {e}")
            return False
    
    async def _deploy_to_github_pages(self) -> bool:
        """GitHub Pages 배포"""
        try:
            # 실제 GitHub Pages 배포 명령어 실행
            # 여기서는 시뮬레이션
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            self.logger.error(f"GitHub Pages 배포 실패: {e}")
            return False
    
    async def _run_git_command(self, args: List[str]) -> str:
        """Git 명령어 실행"""
        try:
            cmd = ["git"] + args
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.base_dir
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                self.logger.error(f"Git 명령어 실패: {' '.join(args)} - {error_msg}")
                return error_msg
            
            return stdout.decode('utf-8', errors='ignore')
            
        except Exception as e:
            self.logger.error(f"Git 명령어 실행 실패: {e}")
            return f"error: {str(e)}"
    
    async def get_deployment_status(self) -> Dict[str, Any]:
        """배포 상태 조회"""
        try:
            return {
                "current_deployment": asdict(self.current_deployment) if self.current_deployment else None,
                "current_branch": self.current_branch,
                "branch_switch_status": self.branch_switch_status.value,
                "github_pages_status": asdict(self.github_pages_status),
                "deployment_history": [asdict(d) for d in self.deployment_history[-5:]]  # 최근 5개
            }
            
        except Exception as e:
            self.logger.error(f"배포 상태 조회 실패: {e}")
            return {}
    
    async def stop_deployment(self) -> Dict[str, Any]:
        """배포 중지"""
        try:
            if not self.current_deployment or self.current_deployment.status in [
                DeploymentStatus.SUCCESS, DeploymentStatus.FAILED
            ]:
                return {
                    "success": False,
                    "message": "중지할 배포가 없습니다"
                }
            
            self.current_deployment.status = DeploymentStatus.FAILED
            self.current_deployment.error_message = "사용자에 의해 중지됨"
            self.current_deployment.end_time = datetime.now()
            
            self.logger.info(f"배포 중지: {self.current_deployment.session_id}")
            
            return {
                "success": True,
                "message": "배포가 중지되었습니다"
            }
            
        except Exception as e:
            self.logger.error(f"배포 중지 실패: {e}")
            return {
                "success": False,
                "message": f"배포 중지 실패: {str(e)}"
            }