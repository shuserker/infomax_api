#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 배포 시스템 (Integrated Deployment System)
POSCO 뉴스 시스템용 완전 독립 통합 배포 시스템

주요 기능:
- 🚀 통합 배포 파이프라인 (HTML 생성 + Git 배포 + 웹훅)
- 🔄 배포 실패 시 자동 롤백 메커니즘
- 📊 GUI에서 배포 진행 상황 실시간 모니터링
- 🛡️ 배포 상태 추적 및 복구 시스템

Requirements: 1.1, 1.4, 4.1 구현
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from .git_deployment_manager import GitDeploymentManager
    from .posco_main_notifier import PoscoMainNotifier
except ImportError:
    from git_deployment_manager import GitDeploymentManager
    from posco_main_notifier import PoscoMainNotifier


class DeploymentStatus(Enum):
    """배포 상태 열거형"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentStep:
    """배포 단계 정보"""
    step_id: str
    name: str
    status: DeploymentStatus
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    progress: int = 0
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class DeploymentSession:
    """배포 세션 정보"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    status: DeploymentStatus = DeploymentStatus.PENDING
    steps: List[DeploymentStep] = None
    total_progress: int = 0
    success_count: int = 0
    failure_count: int = 0
    rollback_available: bool = False
    rollback_data: Optional[Dict] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []


class IntegratedDeploymentSystem:
    """통합 배포 시스템 클래스 (완전 독립)"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """통합 배포 시스템 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 하위 시스템 초기화
        self.git_manager = GitDeploymentManager(self.base_dir)
        self.posco_notifier = PoscoMainNotifier(self.base_dir)
        
        # 로그 파일 설정
        self.log_file = os.path.join(self.script_dir, "integrated_deployment.log")
        
        # 배포 세션 관리
        self.sessions_file = os.path.join(self.script_dir, "deployment_sessions.json")
        self.current_session: Optional[DeploymentSession] = None
        self.session_lock = threading.Lock()
        
        # GUI 콜백 함수들
        self.progress_callbacks: List[Callable] = []
        self.status_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # 배포 설정
        self.max_retry_attempts = 3
        self.retry_delay = 15  # 초
        self.rollback_timeout = 300  # 5분
        
        # 모니터링 설정
        self.monitoring_enabled = True
        self.monitoring_interval = 2  # 초
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        
        self.log_message("🔧 통합 배포 시스템 초기화 완료 (스탠드얼론)")
    
    def log_message(self, message: str):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
            # 로그 디렉토리 생성
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"❌ 로그 파일 쓰기 실패: {e}")
    
    def register_progress_callback(self, callback: Callable[[str, int], None]):
        """진행 상황 콜백 등록 (GUI용)"""
        self.progress_callbacks.append(callback)
    
    def register_status_callback(self, callback: Callable[[DeploymentSession], None]):
        """상태 변경 콜백 등록 (GUI용)"""
        self.status_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable[[str, Dict], None]):
        """오류 콜백 등록 (GUI용)"""
        self.error_callbacks.append(callback)
    
    def _notify_progress(self, message: str, progress: int):
        """진행 상황 알림"""
        for callback in self.progress_callbacks:
            try:
                callback(message, progress)
            except Exception as e:
                self.log_message(f"❌ 진행 상황 콜백 오류: {e}")
    
    def _notify_status_change(self, session: DeploymentSession):
        """상태 변경 알림"""
        for callback in self.status_callbacks:
            try:
                callback(session)
            except Exception as e:
                self.log_message(f"❌ 상태 변경 콜백 오류: {e}")
    
    def _notify_error(self, error_message: str, error_details: Dict):
        """오류 알림"""
        for callback in self.error_callbacks:
            try:
                callback(error_message, error_details)
            except Exception as e:
                self.log_message(f"❌ 오류 콜백 오류: {e}")
    
    def save_session(self, session: DeploymentSession):
        """배포 세션 저장"""
        try:
            with self.session_lock:
                # 기존 세션들 로드
                sessions = self.load_all_sessions()
                
                # 현재 세션을 JSON 직렬화 가능한 형태로 변환
                session_dict = asdict(session)
                
                # Enum 값들을 문자열로 변환
                session_dict['status'] = session.status.value
                for step_dict in session_dict['steps']:
                    step_dict['status'] = step_dict['status'].value
                
                sessions[session.session_id] = session_dict
                
                # 파일에 저장
                with open(self.sessions_file, 'w', encoding='utf-8') as f:
                    json.dump(sessions, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            self.log_message(f"❌ 세션 저장 실패: {e}")
    
    def load_all_sessions(self) -> Dict[str, Dict]:
        """모든 배포 세션 로드"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log_message(f"❌ 세션 로드 실패: {e}")
        
        return {}
    
    def get_session_by_id(self, session_id: str) -> Optional[DeploymentSession]:
        """세션 ID로 배포 세션 조회"""
        try:
            sessions = self.load_all_sessions()
            if session_id in sessions:
                session_data = sessions[session_id]
                # DeploymentStep 객체들 복원
                steps = []
                for step_data in session_data.get('steps', []):
                    step = DeploymentStep(**step_data)
                    step.status = DeploymentStatus(step.status)
                    steps.append(step)
                
                session = DeploymentSession(
                    session_id=session_data['session_id'],
                    start_time=session_data['start_time'],
                    end_time=session_data.get('end_time'),
                    status=DeploymentStatus(session_data['status']),
                    steps=steps,
                    total_progress=session_data.get('total_progress', 0),
                    success_count=session_data.get('success_count', 0),
                    failure_count=session_data.get('failure_count', 0),
                    rollback_available=session_data.get('rollback_available', False),
                    rollback_data=session_data.get('rollback_data'),
                    error_message=session_data.get('error_message')
                )
                return session
        except Exception as e:
            self.log_message(f"❌ 세션 조회 실패: {e}")
        
        return None
    
    def create_deployment_session(self) -> DeploymentSession:
        """새 배포 세션 생성"""
        session_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 배포 단계 정의
        steps = [
            DeploymentStep("pre_check", "배포 전 상태 확인", DeploymentStatus.PENDING),
            DeploymentStep("backup", "백업 생성", DeploymentStatus.PENDING),
            DeploymentStep("html_generation", "HTML 리포트 생성", DeploymentStatus.PENDING),
            DeploymentStep("branch_switch", "브랜치 전환", DeploymentStatus.PENDING),
            DeploymentStep("merge_changes", "변경사항 병합", DeploymentStatus.PENDING),
            DeploymentStep("commit_changes", "변경사항 커밋", DeploymentStatus.PENDING),
            DeploymentStep("push_remote", "원격 저장소 푸시", DeploymentStatus.PENDING),
            DeploymentStep("verify_pages", "GitHub Pages 확인", DeploymentStatus.PENDING),
            DeploymentStep("send_notification", "알림 전송", DeploymentStatus.PENDING),
            DeploymentStep("cleanup", "정리 작업", DeploymentStatus.PENDING)
        ]
        
        session = DeploymentSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            status=DeploymentStatus.PENDING,
            steps=steps
        )
        
        return session
    
    def update_step_status(self, session: DeploymentSession, step_id: str, 
                          status: DeploymentStatus, progress: int = 0, 
                          error_message: Optional[str] = None, 
                          details: Optional[Dict] = None):
        """배포 단계 상태 업데이트"""
        try:
            for step in session.steps:
                if step.step_id == step_id:
                    step.status = status
                    step.progress = progress
                    
                    if status == DeploymentStatus.RUNNING and not step.start_time:
                        step.start_time = datetime.now().isoformat()
                    elif status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED]:
                        step.end_time = datetime.now().isoformat()
                    
                    if error_message:
                        step.error_message = error_message
                    
                    if details:
                        step.details.update(details)
                    
                    break
            
            # 전체 진행률 계산
            total_steps = len(session.steps)
            completed_steps = sum(1 for step in session.steps if step.status == DeploymentStatus.SUCCESS)
            session.total_progress = int((completed_steps / total_steps) * 100)
            
            # 성공/실패 카운트 업데이트
            session.success_count = sum(1 for step in session.steps if step.status == DeploymentStatus.SUCCESS)
            session.failure_count = sum(1 for step in session.steps if step.status == DeploymentStatus.FAILED)
            
            # 세션 저장 및 알림
            self.save_session(session)
            self._notify_status_change(session)
            
        except Exception as e:
            self.log_message(f"❌ 단계 상태 업데이트 실패: {e}")
    
    def start_monitoring(self, session: DeploymentSession):
        """배포 모니터링 시작"""
        if not self.monitoring_enabled or self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(session,),
            daemon=True
        )
        self.monitoring_thread.start()
        self.log_message("📊 배포 모니터링 시작")
    
    def stop_monitoring(self):
        """배포 모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        self.log_message("📊 배포 모니터링 중지")
    
    def _monitoring_loop(self, session: DeploymentSession):
        """모니터링 루프"""
        try:
            while self.monitoring_active and session.status == DeploymentStatus.RUNNING:
                # 현재 실행 중인 단계 찾기
                current_step = None
                for step in session.steps:
                    if step.status == DeploymentStatus.RUNNING:
                        current_step = step
                        break
                
                if current_step:
                    # 진행 상황 알림
                    self._notify_progress(
                        f"{current_step.name} 진행 중... ({current_step.progress}%)",
                        session.total_progress
                    )
                
                time.sleep(self.monitoring_interval)
                
        except Exception as e:
            self.log_message(f"❌ 모니터링 루프 오류: {e}")
    
    def execute_integrated_deployment(self, data: Dict, retry_on_failure: bool = True) -> DeploymentSession:
        """통합 배포 시스템 실행 (Requirements 1.1, 1.4, 4.1)"""
        self.log_message("🚀 통합 배포 시스템 실행 시작...")
        
        # 새 배포 세션 생성
        session = self.create_deployment_session()
        session.status = DeploymentStatus.RUNNING
        self.current_session = session
        
        # 모니터링 시작
        self.start_monitoring(session)
        
        try:
            self.log_message(f"📋 배포 세션 시작: {session.session_id}")
            self._notify_progress("배포 시작...", 0)
            
            # 1단계: 배포 전 상태 확인
            self._execute_pre_check(session)
            
            # 2단계: 백업 생성 (롤백용)
            self._execute_backup_creation(session)
            
            # 3단계: HTML 리포트 생성
            self._execute_html_generation(session, data)
            
            # 4단계: 브랜치 전환
            self._execute_branch_switch(session)
            
            # 5단계: 변경사항 병합
            self._execute_merge_changes(session)
            
            # 6단계: 변경사항 커밋
            self._execute_commit_changes(session)
            
            # 7단계: 원격 저장소 푸시
            self._execute_push_remote(session)
            
            # 8단계: GitHub Pages 확인
            self._execute_verify_pages(session)
            
            # 9단계: 알림 전송
            self._execute_send_notification(session)
            
            # 10단계: 정리 작업
            self._execute_cleanup(session)
            
            # 배포 성공
            session.status = DeploymentStatus.SUCCESS
            session.end_time = datetime.now().isoformat()
            
            self.log_message(f"✅ 통합 배포 성공 완료: {session.session_id}")
            self._notify_progress("배포 성공 완료!", 100)
            
        except Exception as e:
            error_msg = f"통합 배포 중 오류: {str(e)}"
            session.error_message = error_msg
            session.status = DeploymentStatus.FAILED
            session.end_time = datetime.now().isoformat()
            
            self.log_message(f"❌ {error_msg}")
            self._notify_error(error_msg, {"session_id": session.session_id})
            
            # 자동 롤백 시도
            if session.rollback_available:
                self.log_message("🔄 자동 롤백 시작...")
                rollback_result = self.execute_rollback(session)
                if rollback_result:
                    self.log_message("✅ 자동 롤백 완료")
                else:
                    self.log_message("❌ 자동 롤백 실패")
            
            # 재시도 로직
            if retry_on_failure and session.failure_count < self.max_retry_attempts:
                self.log_message(f"🔄 배포 재시도 ({session.failure_count + 1}/{self.max_retry_attempts})")
                time.sleep(self.retry_delay)
                return self.execute_integrated_deployment(data, retry_on_failure=False)
        
        finally:
            # 모니터링 중지
            self.stop_monitoring()
            
            # 세션 저장
            self.save_session(session)
            self._notify_status_change(session)
        
        return session
    
    def _execute_pre_check(self, session: DeploymentSession):
        """배포 전 상태 확인 실행"""
        step_id = "pre_check"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 10)
        
        try:
            # Git 상태 확인
            git_status = self.git_manager.check_git_status()
            
            if not git_status['is_git_repo']:
                raise Exception("Git 저장소가 아닙니다")
            
            if git_status['has_conflicts']:
                raise Exception("해결되지 않은 Git 충돌이 있습니다")
            
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100, 
                                  details={"git_status": git_status})
            
        except Exception as e:
            self.update_step_status(session, step_id, DeploymentStatus.FAILED, 0, str(e))
            raise
    
    def _execute_backup_creation(self, session: DeploymentSession):
        """백업 생성 실행"""
        step_id = "backup"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 20)
        
        try:
            # 백업 태그 생성
            backup_tag = self.posco_notifier.create_backup_commit()
            
            if backup_tag:
                session.rollback_available = True
                session.rollback_data = {
                    "backup_tag": backup_tag,
                    "original_branch": self.git_manager.check_git_status()['current_branch']
                }
                
                self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                      details={"backup_tag": backup_tag})
            else:
                # 백업 실패해도 계속 진행 (경고만)
                self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                      details={"warning": "백업 생성 실패"})
                self.log_message("⚠️ 백업 생성 실패 (계속 진행)")
            
        except Exception as e:
            # 백업 실패해도 계속 진행
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"warning": f"백업 생성 오류: {str(e)}"})
            self.log_message(f"⚠️ 백업 생성 오류 (계속 진행): {e}")
    
    def _execute_html_generation(self, session: DeploymentSession, data: Dict):
        """HTML 생성 실행"""
        step_id = "html_generation"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 30)
        
        try:
            html_file = self.posco_notifier.generate_posco_html(data)
            
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"html_file": html_file})
            
        except Exception as e:
            self.update_step_status(session, step_id, DeploymentStatus.FAILED, 0, str(e))
            raise
    
    def _execute_branch_switch(self, session: DeploymentSession):
        """브랜치 전환 실행"""
        step_id = "branch_switch"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 40)
        
        try:
            def progress_callback(msg, progress):
                self.update_step_status(session, step_id, DeploymentStatus.RUNNING, progress)
            
            switch_result = self.git_manager.safe_branch_switch("publish", progress_callback)
            
            if switch_result['success']:
                self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                      details=switch_result)
            else:
                raise Exception(switch_result.get('error_message', '브랜치 전환 실패'))
            
        except Exception as e:
            self.update_step_status(session, step_id, DeploymentStatus.FAILED, 0, str(e))
            raise
    
    def _execute_merge_changes(self, session: DeploymentSession):
        """변경사항 병합 실행"""
        step_id = "merge_changes"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 50)
        
        try:
            merge_result = self.posco_notifier._merge_from_main_branch()
            
            if merge_result['success']:
                self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                      details=merge_result)
            else:
                raise Exception(merge_result.get('error_message', '병합 실패'))
            
        except Exception as e:
            self.update_step_status(session, step_id, DeploymentStatus.FAILED, 0, str(e))
            raise
    
    def _execute_commit_changes(self, session: DeploymentSession):
        """변경사항 커밋 실행"""
        step_id = "commit_changes"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 60)
        
        try:
            commit_result = self.posco_notifier._commit_changes(session.session_id)
            
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"committed": commit_result})
            
        except Exception as e:
            self.update_step_status(session, step_id, DeploymentStatus.FAILED, 0, str(e))
            raise
    
    def _execute_push_remote(self, session: DeploymentSession):
        """원격 저장소 푸시 실행"""
        step_id = "push_remote"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 70)
        
        try:
            push_result = self.posco_notifier._push_to_remote()
            
            if push_result['success']:
                self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                      details=push_result)
            else:
                raise Exception(push_result.get('error_message', '푸시 실패'))
            
        except Exception as e:
            self.update_step_status(session, step_id, DeploymentStatus.FAILED, 0, str(e))
            raise
    
    def _execute_verify_pages(self, session: DeploymentSession):
        """GitHub Pages 확인 실행 (Requirements 1.2, 5.4)"""
        step_id = "verify_pages"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 80)
        
        try:
            # GitHub Pages 모니터링 시스템 사용
            try:
                from .github_pages_monitor import GitHubPagesMonitor
                pages_monitor = GitHubPagesMonitor()
                
                # GitHub Pages URL 가져오기
                pages_url = getattr(self.posco_notifier, 'github_pages_url', 'https://username.github.io/repository')
                
                self.log_message(f"🌐 GitHub Pages 접근성 검증 시작: {pages_url}")
                
                # 배포 후 접근성 검증 (최대 5분 대기)
                verification_result = pages_monitor.verify_github_pages_deployment(pages_url, max_wait_time=300)
                
                if verification_result['deployment_successful'] and verification_result['final_accessible']:
                    # 접근 성공
                    self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                          details={
                                              "accessible": True,
                                              "url": pages_url,
                                              "checks_performed": verification_result['checks_performed'],
                                              "total_wait_time": verification_result['total_wait_time'],
                                              "final_check": verification_result['checks'][-1] if verification_result['checks'] else None
                                          })
                    
                    self.log_message(f"✅ GitHub Pages 접근 성공: {pages_url} (대기시간: {verification_result['total_wait_time']:.1f}초)")
                    
                else:
                    # 접근 실패 - 경고로 처리하되 배포는 성공으로 간주
                    self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                          details={
                                              "accessible": False,
                                              "url": pages_url,
                                              "checks_performed": verification_result['checks_performed'],
                                              "total_wait_time": verification_result['total_wait_time'],
                                              "error_message": verification_result.get('error_message'),
                                              "warning": "GitHub Pages 접근 실패 - 자동 재배포 옵션 사용 가능"
                                          })
                    
                    self.log_message(f"⚠️ GitHub Pages 접근 실패: {pages_url} - {verification_result.get('error_message', '알 수 없는 오류')}")
                    
                    # 접근 실패 시 GUI 알림 (콜백을 통해)
                    self._notify_error(
                        f"GitHub Pages 접근 실패: {pages_url}",
                        {
                            "url": pages_url,
                            "wait_time": verification_result['total_wait_time'],
                            "checks_performed": verification_result['checks_performed'],
                            "auto_redeploy_available": True,
                            "verification_result": verification_result
                        }
                    )
                
            except ImportError:
                # GitHub Pages 모니터를 사용할 수 없는 경우 기존 방식 사용
                self.log_message("⚠️ GitHub Pages 모니터 모듈을 찾을 수 없음, 기본 확인 방식 사용")
                
                # GitHub Pages 빌드 대기
                time.sleep(15)
                
                pages_result = self.posco_notifier._verify_github_pages_access()
                
                # 접근 실패해도 배포는 성공으로 처리 (경고만)
                if pages_result['accessible']:
                    self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                          details=pages_result)
                else:
                    self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                          details={**pages_result, "warning": "GitHub Pages 접근 실패"})
                    self.log_message("⚠️ GitHub Pages 접근 실패 (배포는 성공)")
            
        except Exception as e:
            # Pages 확인 실패해도 계속 진행
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"warning": f"Pages 확인 오류: {str(e)}"})
            self.log_message(f"⚠️ Pages 확인 오류 (계속 진행): {e}")
    
    def _execute_send_notification(self, session: DeploymentSession):
        """알림 전송 실행"""
        step_id = "send_notification"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 90)
        
        try:
            # 성공 메시지 생성
            message = f"🎉 POSCO 통합 배포 성공!\n" \
                     f"📊 세션 ID: {session.session_id}\n" \
                     f"🌐 URL: {self.posco_notifier.github_pages_url}\n" \
                     f"⏱️ 완료 단계: {session.success_count}/{len(session.steps)}"
            
            webhook_sent = self.posco_notifier.send_direct_webhook(message)
            
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"webhook_sent": webhook_sent})
            
        except Exception as e:
            # 알림 실패해도 계속 진행
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"warning": f"알림 전송 오류: {str(e)}"})
            self.log_message(f"⚠️ 알림 전송 오류 (계속 진행): {e}")
    
    def _execute_cleanup(self, session: DeploymentSession):
        """정리 작업 실행"""
        step_id = "cleanup"
        self.update_step_status(session, step_id, DeploymentStatus.RUNNING, 95)
        
        try:
            # 원래 브랜치로 복귀
            if session.rollback_data and session.rollback_data.get('original_branch'):
                original_branch = session.rollback_data['original_branch']
                if original_branch != "publish":
                    switch_result = self.git_manager.safe_branch_switch(original_branch)
                    if switch_result['success']:
                        self.log_message(f"✅ {original_branch} 브랜치 복귀 완료")
                    else:
                        self.log_message(f"⚠️ {original_branch} 브랜치 복귀 실패")
            
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"cleanup_completed": True})
            
        except Exception as e:
            # 정리 실패해도 계속 진행
            self.update_step_status(session, step_id, DeploymentStatus.SUCCESS, 100,
                                  details={"warning": f"정리 작업 오류: {str(e)}"})
            self.log_message(f"⚠️ 정리 작업 오류 (계속 진행): {e}")
    
    def execute_rollback(self, session: DeploymentSession) -> bool:
        """배포 롤백 실행 (Requirements 4.1)"""
        if not session.rollback_available or not session.rollback_data:
            self.log_message("❌ 롤백 데이터가 없습니다")
            return False
        
        self.log_message(f"🔄 배포 롤백 시작: {session.session_id}")
        session.status = DeploymentStatus.ROLLING_BACK
        
        try:
            rollback_data = session.rollback_data
            
            # 1. 원래 브랜치로 복귀
            if rollback_data.get('original_branch'):
                original_branch = rollback_data['original_branch']
                self.log_message(f"1️⃣ {original_branch} 브랜치로 복귀...")
                
                switch_result = self.git_manager.safe_branch_switch(original_branch)
                if not switch_result['success']:
                    self.log_message(f"❌ {original_branch} 브랜치 복귀 실패")
                    return False
            
            # 2. 백업 태그로 복원
            if rollback_data.get('backup_tag'):
                backup_tag = rollback_data['backup_tag']
                self.log_message(f"2️⃣ 백업 태그로 복원: {backup_tag}")
                
                success, _ = self.git_manager.run_git_command(['git', 'reset', '--hard', backup_tag])
                if not success:
                    self.log_message(f"❌ 백업 태그 복원 실패: {backup_tag}")
                    return False
            
            # 3. publish 브랜치 정리
            self.log_message("3️⃣ publish 브랜치 정리...")
            switch_result = self.git_manager.safe_branch_switch("publish")
            if switch_result['success']:
                # 강제 리셋으로 이전 상태로 되돌리기
                success, _ = self.git_manager.run_git_command(['git', 'reset', '--hard', 'HEAD~1'], check=False)
                if success:
                    # 원격에도 강제 푸시
                    success, _ = self.git_manager.run_git_command(['git', 'push', '--force', 'origin', 'publish'], check=False)
                    if success:
                        self.log_message("✅ publish 브랜치 정리 완료")
                    else:
                        self.log_message("⚠️ 원격 publish 브랜치 정리 실패")
                
                # 다시 원래 브랜치로 복귀
                if rollback_data.get('original_branch'):
                    self.git_manager.safe_branch_switch(rollback_data['original_branch'])
            
            # 롤백 완료
            session.status = DeploymentStatus.ROLLED_BACK
            session.end_time = datetime.now().isoformat()
            
            # 롤백 알림 전송
            rollback_message = f"🔄 POSCO 배포 롤백 완료\n" \
                             f"📊 세션 ID: {session.session_id}\n" \
                             f"🏷️ 백업 태그: {rollback_data.get('backup_tag', 'N/A')}\n" \
                             f"⏱️ 롤백 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.posco_notifier.send_direct_webhook(rollback_message)
            
            self.log_message(f"✅ 배포 롤백 완료: {session.session_id}")
            return True
            
        except Exception as e:
            error_msg = f"롤백 중 오류: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            session.error_message = error_msg
            return False
        
        finally:
            self.save_session(session)
            self._notify_status_change(session)
    
    def get_deployment_history(self, limit: int = 10) -> List[DeploymentSession]:
        """배포 히스토리 조회"""
        try:
            sessions = self.load_all_sessions()
            
            # 시간순 정렬 (최신순)
            sorted_sessions = sorted(
                sessions.values(),
                key=lambda x: x['start_time'],
                reverse=True
            )
            
            # DeploymentSession 객체로 변환
            history = []
            for session_data in sorted_sessions[:limit]:
                session = self.get_session_by_id(session_data['session_id'])
                if session:
                    history.append(session)
            
            return history
            
        except Exception as e:
            self.log_message(f"❌ 배포 히스토리 조회 실패: {e}")
            return []
    
    def get_deployment_statistics(self) -> Dict[str, Any]:
        """배포 통계 조회"""
        try:
            sessions = self.load_all_sessions()
            
            total_deployments = len(sessions)
            successful_deployments = sum(1 for s in sessions.values() if s['status'] == 'success')
            failed_deployments = sum(1 for s in sessions.values() if s['status'] == 'failed')
            rolled_back_deployments = sum(1 for s in sessions.values() if s['status'] == 'rolled_back')
            
            # 최근 24시간 배포 수
            recent_threshold = datetime.now() - timedelta(hours=24)
            recent_deployments = 0
            
            for session_data in sessions.values():
                try:
                    session_time = datetime.fromisoformat(session_data['start_time'])
                    if session_time > recent_threshold:
                        recent_deployments += 1
                except:
                    pass
            
            success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
            
            return {
                'total_deployments': total_deployments,
                'successful_deployments': successful_deployments,
                'failed_deployments': failed_deployments,
                'rolled_back_deployments': rolled_back_deployments,
                'recent_deployments_24h': recent_deployments,
                'success_rate': round(success_rate, 2),
                'rollback_available': self.current_session.rollback_available if self.current_session else False
            }
            
        except Exception as e:
            self.log_message(f"❌ 배포 통계 조회 실패: {e}")
            return {}


def main():
    """테스트용 메인 함수"""
    print("🧪 IntegratedDeploymentSystem 테스트 시작...")
    
    # 통합 배포 시스템 초기화
    deployment_system = IntegratedDeploymentSystem()
    
    # 테스트 데이터
    test_data = {
        'kospi': '2,450.32',
        'exchange_rate': '1,320.50',
        'posco_stock': '285,000',
        'analysis': '테스트 분석 데이터입니다.',
        'news': [
            {
                'title': '테스트 뉴스',
                'summary': '테스트 뉴스 요약',
                'date': '2025-01-01'
            }
        ]
    }
    
    # 진행 상황 콜백 등록
    def progress_callback(message, progress):
        print(f"📊 진행 상황: {message} ({progress}%)")
    
    deployment_system.register_progress_callback(progress_callback)
    
    # 배포 통계 조회
    stats = deployment_system.get_deployment_statistics()
    print(f"📈 배포 통계: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    
    print("✅ IntegratedDeploymentSystem 테스트 완료")


if __name__ == "__main__":
    main()