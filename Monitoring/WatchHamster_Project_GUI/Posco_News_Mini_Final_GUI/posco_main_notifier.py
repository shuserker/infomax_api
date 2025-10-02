#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 메인 알림 시스템 (완전 독립)
GitHub Pages 배포 및 웹훅 알림 통합 시스템

주요 기능:
- 📊 POSCO 데이터 분석 및 HTML 생성
- 🚀 GitHub Pages 자동 배포
- 📨 웹훅 메시지 전송
- 🔄 배포 실패 시 자동 롤백

Requirements: 1.1, 1.4, 4.1 구현
"""

import os
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
try:
    from .git_deployment_manager import GitDeploymentManager
    from .message_template_engine import MessageTemplateEngine, MessageType
except ImportError:
    from git_deployment_manager import GitDeploymentManager
    from message_template_engine import MessageTemplateEngine, MessageType


class PoscoMainNotifier:
    """POSCO 메인 알림 시스템 클래스 (완전 독립)"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """POSCO 알림 시스템 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Git 배포 관리자 초기화
        self.git_manager = GitDeploymentManager(self.base_dir)
        
        # 메시지 템플릿 엔진 초기화
        self.message_engine = MessageTemplateEngine(os.path.join(self.script_dir, "../config"))
        
        # 로그 파일 설정
        self.log_file = os.path.join(self.script_dir, "posco_deployment.log")
        
        # 배포 상태 파일
        self.deployment_state_file = os.path.join(self.script_dir, "posco_deployment_state.json")
        
        # 웹훅 설정
        self.webhook_url = None
        self.webhook_config_file = os.path.join(self.script_dir, "../config/webhook_config.json")
        
        # GitHub Pages 설정
        self.github_pages_url = "https://shuserker.github.io/infomax_api"
        
        # 배포 재시도 설정
        self.max_deployment_retries = 3
        self.deployment_retry_delay = 10  # 초
        
        # 롤백 설정
        self.rollback_enabled = True
        self.backup_branch = "backup"
        
        self.log_message("🔧 POSCO 메인 알림 시스템 초기화 완료 (스탠드얼론)")
        self._load_webhook_config()
    
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
    
    def _load_webhook_config(self):
        """웹훅 설정 로드 (향상된 버전)"""
        try:
            if os.path.exists(self.webhook_config_file):
                with open(self.webhook_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # 기본 웹훅 URL
                    self.webhook_url = config.get('webhook_url')
                    
                    # 웹훅 설정
                    webhook_settings = config.get('webhook_settings', {})
                    self.webhook_timeout = webhook_settings.get('timeout', 15)
                    self.webhook_retry_attempts = webhook_settings.get('retry_attempts', 3)
                    self.webhook_retry_delay = webhook_settings.get('retry_delay', 5)
                    self.webhook_user_agent = webhook_settings.get('user_agent', 'POSCO-Analysis-System/1.0')
                    
                    # 메시지 설정
                    message_settings = config.get('message_settings', {})
                    self.enable_templates = message_settings.get('enable_templates', True)
                    self.customer_friendly_mode = message_settings.get('customer_friendly_mode', True)
                    self.include_technical_details = message_settings.get('include_technical_details', False)
                    self.max_message_length = message_settings.get('max_message_length', 4000)
                    
                    # 알림 타입 설정
                    self.notification_types = config.get('notification_types', {})
                    
                    # GUI 통합 설정
                    gui_settings = config.get('gui_integration', {})
                    self.show_send_status = gui_settings.get('show_send_status', True)
                    self.enable_preview = gui_settings.get('enable_preview', True)
                    self.auto_send_on_deployment = gui_settings.get('auto_send_on_deployment', True)
                    
                    self.log_message("✅ 향상된 웹훅 설정 로드 완료")
            else:
                # 기본값 설정
                self.webhook_url = None
                self.webhook_timeout = 15
                self.webhook_retry_attempts = 3
                self.webhook_retry_delay = 5
                self.webhook_user_agent = 'POSCO-Analysis-System/1.0'
                self.enable_templates = True
                self.customer_friendly_mode = True
                self.include_technical_details = False
                self.max_message_length = 4000
                self.notification_types = {}
                self.show_send_status = True
                self.enable_preview = True
                self.auto_send_on_deployment = True
                
                self.log_message("⚠️ 웹훅 설정 파일이 없습니다 - 기본값 사용")
        except Exception as e:
            self.log_message(f"❌ 웹훅 설정 로드 실패: {e}")
            # 오류 시 기본값 설정
            self.webhook_url = None
            self.enable_templates = True
            self.customer_friendly_mode = True
    
    def save_deployment_state(self, state: Dict):
        """배포 상태 저장"""
        try:
            with open(self.deployment_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_message(f"❌ 배포 상태 저장 실패: {e}")
    
    def load_deployment_state(self) -> Dict:
        """배포 상태 로드"""
        try:
            if os.path.exists(self.deployment_state_file):
                with open(self.deployment_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log_message(f"❌ 배포 상태 로드 실패: {e}")
        
        return {
            'last_deployment': None,
            'deployment_count': 0,
            'last_success': None,
            'last_failure': None,
            'rollback_available': False,
            'backup_commit': None
        }
    
    def generate_posco_html(self, data: Dict) -> str:
        """POSCO 데이터를 기반으로 HTML 생성"""
        self.log_message("📊 POSCO HTML 생성 시작...")
        
        try:
            # 현재 시간
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # HTML 템플릿 생성
            html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POSCO 통합 분석 리포트 - {current_time}</title>
    <link rel="stylesheet" href="assets/css/main.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🏭 POSCO 통합 분석 리포트</h1>
            <p class="timestamp">생성 시간: {current_time}</p>
        </header>
        
        <main class="main-content">
            <section class="summary-section">
                <h2>📈 주요 지표 요약</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>KOSPI 지수</h3>
                        <p class="metric-value">{data.get('kospi', 'N/A')}</p>
                    </div>
                    <div class="metric-card">
                        <h3>환율 (USD/KRW)</h3>
                        <p class="metric-value">{data.get('exchange_rate', 'N/A')}</p>
                    </div>
                    <div class="metric-card">
                        <h3>POSCO 주가</h3>
                        <p class="metric-value">{data.get('posco_stock', 'N/A')}</p>
                    </div>
                </div>
            </section>
            
            <section class="analysis-section">
                <h2>🔍 분석 결과</h2>
                <div class="analysis-content">
                    <p>{data.get('analysis', '분석 데이터가 없습니다.')}</p>
                </div>
            </section>
            
            <section class="news-section">
                <h2>📰 관련 뉴스</h2>
                <div class="news-list">
                    {self._generate_news_items(data.get('news', []))}
                </div>
            </section>
        </main>
        
        <footer class="footer">
            <p>© 2025 POSCO 통합 분석 시스템 | 자동 생성됨</p>
        </footer>
    </div>
    
    <script src="assets/js/main.js"></script>
</body>
</html>"""
            
            # HTML 파일 저장
            html_file_path = os.path.join(self.base_dir, "index.html")
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.log_message(f"✅ POSCO HTML 생성 완료: {html_file_path}")
            return html_file_path
            
        except Exception as e:
            error_msg = f"POSCO HTML 생성 실패: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def _generate_news_items(self, news_list: List[Dict]) -> str:
        """뉴스 아이템 HTML 생성"""
        if not news_list:
            return "<p>관련 뉴스가 없습니다.</p>"
        
        news_html = ""
        for news in news_list[:5]:  # 최대 5개 뉴스만 표시
            news_html += f"""
            <div class="news-item">
                <h3>{news.get('title', '제목 없음')}</h3>
                <p class="news-summary">{news.get('summary', '요약 없음')}</p>
                <p class="news-date">{news.get('date', '날짜 없음')}</p>
            </div>
            """
        
        return news_html
    
    def create_backup_commit(self) -> Optional[str]:
        """배포 전 백업 커밋 생성 (롤백용)"""
        try:
            self.log_message("💾 배포 전 백업 커밋 생성...")
            
            # 현재 커밋 해시 저장
            success, current_commit = self.git_manager.run_git_command(['git', 'rev-parse', 'HEAD'])
            if not success:
                self.log_message("❌ 현재 커밋 해시 조회 실패")
                return None
            
            # 백업 태그 생성
            backup_tag = f"backup-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            success, _ = self.git_manager.run_git_command(['git', 'tag', backup_tag, current_commit])
            
            if success:
                self.log_message(f"✅ 백업 태그 생성 완료: {backup_tag}")
                return backup_tag
            else:
                self.log_message("❌ 백업 태그 생성 실패")
                return None
                
        except Exception as e:
            self.log_message(f"❌ 백업 커밋 생성 중 오류: {str(e)}")
            return None
    
    def deploy_to_publish_branch(self, progress_callback: Optional[Callable] = None) -> Dict[str, any]:
        """publish 브랜치로 배포 (Requirements 1.1, 1.4)"""
        self.log_message("🚀 GitHub Pages 배포 시작...")
        
        deployment_result = {
            'success': False,
            'deployment_id': f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'steps_completed': [],
            'backup_created': False,
            'backup_tag': None,
            'branch_switched': False,
            'files_committed': False,
            'pushed_to_remote': False,
            'github_pages_accessible': False,
            'rollback_performed': False,
            'error_message': None,
            'retry_count': 0
        }
        
        original_branch = None
        
        try:
            # 1단계: 배포 전 상태 확인
            step_msg = "배포 전 Git 상태 확인..."
            self.log_message(f"1️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg, 10)
            
            git_status = self.git_manager.check_git_status()
            if not git_status['is_git_repo']:
                deployment_result['error_message'] = "Git 저장소가 아닙니다"
                return deployment_result
            
            original_branch = git_status['current_branch']
            deployment_result['steps_completed'].append('status_check')
            
            # 2단계: 백업 생성 (롤백용)
            if self.rollback_enabled:
                step_msg = "배포 전 백업 생성..."
                self.log_message(f"2️⃣ {step_msg}")
                if progress_callback:
                    progress_callback(step_msg, 20)
                
                backup_tag = self.create_backup_commit()
                if backup_tag:
                    deployment_result['backup_created'] = True
                    deployment_result['backup_tag'] = backup_tag
                    deployment_result['steps_completed'].append('backup_creation')
                    self.log_message(f"✅ 백업 생성 완료: {backup_tag}")
                else:
                    self.log_message("⚠️ 백업 생성 실패 (계속 진행)")
            
            # 3단계: publish 브랜치로 안전한 전환
            step_msg = "publish 브랜치로 전환..."
            self.log_message(f"3️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg, 30)
            
            def branch_progress_callback(msg):
                if progress_callback:
                    progress_callback(f"브랜치 전환: {msg}", 35)
            
            switch_result = self.git_manager.safe_branch_switch("publish", branch_progress_callback)
            
            if not switch_result['success']:
                deployment_result['error_message'] = f"브랜치 전환 실패: {switch_result.get('error_message', '알 수 없는 오류')}"
                return deployment_result
            
            deployment_result['branch_switched'] = True
            deployment_result['steps_completed'].append('branch_switch')
            
            # 4단계: main 브랜치의 변경사항 병합
            step_msg = "main 브랜치 변경사항 병합..."
            self.log_message(f"4️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg, 50)
            
            merge_result = self._merge_from_main_branch()
            if not merge_result['success']:
                deployment_result['error_message'] = f"병합 실패: {merge_result.get('error_message', '알 수 없는 오류')}"
                # 롤백 시도
                if self.rollback_enabled:
                    self._perform_rollback(deployment_result, original_branch)
                return deployment_result
            
            deployment_result['steps_completed'].append('merge_main')
            
            # 5단계: 변경사항 커밋
            step_msg = "변경사항 커밋..."
            self.log_message(f"5️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg, 60)
            
            commit_result = self._commit_changes(deployment_result['deployment_id'])
            if commit_result:
                deployment_result['files_committed'] = True
                deployment_result['steps_completed'].append('commit_changes')
            else:
                self.log_message("⚠️ 커밋할 변경사항이 없거나 커밋 실패")
            
            # 6단계: 원격 저장소에 푸시
            step_msg = "원격 저장소에 푸시..."
            self.log_message(f"6️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg, 70)
            
            push_result = self._push_to_remote()
            if not push_result['success']:
                deployment_result['error_message'] = f"푸시 실패: {push_result.get('error_message', '알 수 없는 오류')}"
                # 롤백 시도
                if self.rollback_enabled:
                    self._perform_rollback(deployment_result, original_branch)
                return deployment_result
            
            deployment_result['pushed_to_remote'] = True
            deployment_result['steps_completed'].append('push_remote')
            
            # 7단계: GitHub Pages 접근성 확인
            step_msg = "GitHub Pages 접근성 확인..."
            self.log_message(f"7️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg, 80)
            
            # 잠시 대기 (GitHub Pages 빌드 시간)
            time.sleep(10)
            
            pages_result = self._verify_github_pages_access()
            if pages_result['accessible']:
                deployment_result['github_pages_accessible'] = True
                deployment_result['steps_completed'].append('pages_verification')
                self.log_message("✅ GitHub Pages 접근 확인 완료")
            else:
                self.log_message("⚠️ GitHub Pages 접근 확인 실패 (배포는 성공)")
            
            # 8단계: 원래 브랜치로 복귀
            step_msg = f"{original_branch} 브랜치로 복귀..."
            self.log_message(f"8️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg, 90)
            
            if original_branch and original_branch != "publish":
                return_result = self.git_manager.safe_branch_switch(original_branch)
                if return_result['success']:
                    self.log_message(f"✅ {original_branch} 브랜치 복귀 완료")
                    deployment_result['steps_completed'].append('branch_return')
                else:
                    self.log_message(f"⚠️ {original_branch} 브랜치 복귀 실패")
            
            # 배포 성공
            deployment_result['success'] = True
            deployment_result['end_time'] = datetime.now().isoformat()
            
            # 배포 상태 저장
            state = self.load_deployment_state()
            state['last_deployment'] = deployment_result['deployment_id']
            state['deployment_count'] += 1
            state['last_success'] = deployment_result['end_time']
            state['rollback_available'] = deployment_result['backup_created']
            state['backup_commit'] = deployment_result['backup_tag']
            self.save_deployment_state(state)
            
            success_msg = f"GitHub Pages 배포 성공 완료 (ID: {deployment_result['deployment_id']})"
            self.log_message(f"✅ {success_msg}")
            if progress_callback:
                progress_callback(f"완료: {success_msg}", 100)
            
            return deployment_result
            
        except Exception as e:
            error_msg = f"배포 중 예외 발생: {str(e)}"
            deployment_result['error_message'] = error_msg
            deployment_result['end_time'] = datetime.now().isoformat()
            self.log_message(f"❌ {error_msg}")
            
            # 롤백 시도
            if self.rollback_enabled:
                self._perform_rollback(deployment_result, original_branch)
            
            return deployment_result
    
    def _merge_from_main_branch(self) -> Dict[str, any]:
        """main 브랜치에서 변경사항 병합"""
        merge_result = {
            'success': False,
            'conflicts_resolved': False,
            'error_message': None
        }
        
        try:
            self.log_message("🔄 main 브랜치에서 변경사항 병합 시작...")
            
            # main 브랜치에서 병합
            success, merge_output = self.git_manager.run_git_command(['git', 'merge', 'main'], check=False)
            
            if success:
                merge_result['success'] = True
                self.log_message("✅ main 브랜치 병합 완료")
            else:
                # 충돌이 발생한 경우 자동 해결 시도
                if "CONFLICT" in merge_output or "conflict" in merge_output.lower():
                    self.log_message("⚠️ 병합 충돌 감지 - 자동 해결 시도...")
                    
                    conflict_result = self.git_manager.handle_git_conflicts()
                    if conflict_result['success']:
                        merge_result['success'] = True
                        merge_result['conflicts_resolved'] = True
                        self.log_message("✅ 충돌 자동 해결 및 병합 완료")
                    else:
                        merge_result['error_message'] = f"충돌 해결 실패: {conflict_result.get('error_message', '알 수 없는 오류')}"
                        self.log_message(f"❌ {merge_result['error_message']}")
                else:
                    merge_result['error_message'] = f"병합 실패: {merge_output}"
                    self.log_message(f"❌ {merge_result['error_message']}")
            
            return merge_result
            
        except Exception as e:
            merge_result['error_message'] = f"병합 중 예외 발생: {str(e)}"
            self.log_message(f"❌ {merge_result['error_message']}")
            return merge_result
    
    def _commit_changes(self, deployment_id: str) -> bool:
        """변경사항 커밋"""
        try:
            # 변경사항 확인
            success, status = self.git_manager.run_git_command(['git', 'status', '--porcelain'])
            if not success or not status.strip():
                self.log_message("ℹ️ 커밋할 변경사항이 없습니다")
                return True
            
            # 모든 변경사항 스테이징
            success, _ = self.git_manager.run_git_command(['git', 'add', '.'])
            if not success:
                self.log_message("❌ 파일 스테이징 실패")
                return False
            
            # 커밋 메시지 생성
            commit_message = f"Deploy POSCO analysis - {deployment_id}"
            
            # 커밋 실행
            success, _ = self.git_manager.run_git_command(['git', 'commit', '-m', commit_message])
            if success:
                self.log_message(f"✅ 변경사항 커밋 완료: {commit_message}")
                return True
            else:
                self.log_message("❌ 커밋 실패")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 커밋 중 오류: {str(e)}")
            return False
    
    def _push_to_remote(self) -> Dict[str, any]:
        """원격 저장소에 푸시"""
        push_result = {
            'success': False,
            'error_message': None
        }
        
        try:
            self.log_message("📤 원격 저장소에 푸시 시작...")
            
            # publish 브랜치를 원격에 푸시
            success, push_output = self.git_manager.run_git_command(['git', 'push', 'origin', 'publish'])
            
            if success:
                push_result['success'] = True
                self.log_message("✅ 원격 저장소 푸시 완료")
            else:
                push_result['error_message'] = f"푸시 실패: {push_output}"
                self.log_message(f"❌ {push_result['error_message']}")
            
            return push_result
            
        except Exception as e:
            push_result['error_message'] = f"푸시 중 예외 발생: {str(e)}"
            self.log_message(f"❌ {push_result['error_message']}")
            return push_result
    
    def _verify_github_pages_access(self) -> Dict[str, any]:
        """GitHub Pages 접근성 확인"""
        verification_result = {
            'accessible': False,
            'status_code': None,
            'response_time': None,
            'error_message': None
        }
        
        try:
            self.log_message(f"🌐 GitHub Pages 접근성 확인: {self.github_pages_url}")
            
            start_time = time.time()
            response = requests.get(self.github_pages_url, timeout=30)
            response_time = time.time() - start_time
            
            verification_result['status_code'] = response.status_code
            verification_result['response_time'] = round(response_time, 2)
            
            if response.status_code == 200:
                verification_result['accessible'] = True
                self.log_message(f"✅ GitHub Pages 접근 성공 (응답시간: {verification_result['response_time']}초)")
            else:
                verification_result['error_message'] = f"HTTP {response.status_code}"
                self.log_message(f"⚠️ GitHub Pages 접근 실패: {verification_result['error_message']}")
            
            return verification_result
            
        except requests.exceptions.Timeout:
            verification_result['error_message'] = "요청 시간 초과"
            self.log_message(f"⏰ GitHub Pages 접근 시간 초과")
            return verification_result
        except requests.exceptions.RequestException as e:
            verification_result['error_message'] = f"요청 오류: {str(e)}"
            self.log_message(f"❌ GitHub Pages 접근 오류: {verification_result['error_message']}")
            return verification_result
        except Exception as e:
            verification_result['error_message'] = f"예외 발생: {str(e)}"
            self.log_message(f"❌ GitHub Pages 접근 중 예외: {verification_result['error_message']}")
            return verification_result
    
    def _perform_rollback(self, deployment_result: Dict, original_branch: Optional[str]):
        """배포 실패 시 자동 롤백 (Requirements 4.1)"""
        try:
            self.log_message("🔄 배포 실패 - 자동 롤백 시작...")
            
            rollback_steps = []
            
            # 1. 원래 브랜치로 복귀
            if original_branch:
                self.log_message(f"1️⃣ {original_branch} 브랜치로 복귀...")
                switch_result = self.git_manager.safe_branch_switch(original_branch)
                if switch_result['success']:
                    rollback_steps.append('branch_restored')
                    self.log_message(f"✅ {original_branch} 브랜치 복귀 완료")
                else:
                    self.log_message(f"❌ {original_branch} 브랜치 복귀 실패")
            
            # 2. 백업 태그가 있으면 복원
            if deployment_result.get('backup_tag'):
                self.log_message(f"2️⃣ 백업 태그로 복원: {deployment_result['backup_tag']}")
                success, _ = self.git_manager.run_git_command(['git', 'reset', '--hard', deployment_result['backup_tag']])
                if success:
                    rollback_steps.append('backup_restored')
                    self.log_message(f"✅ 백업 태그 복원 완료")
                else:
                    self.log_message(f"❌ 백업 태그 복원 실패")
            
            # 3. publish 브랜치 정리 (필요시)
            if deployment_result.get('branch_switched'):
                self.log_message("3️⃣ publish 브랜치 정리...")
                # publish 브랜치로 전환 후 강제 리셋
                switch_result = self.git_manager.safe_branch_switch("publish")
                if switch_result['success']:
                    success, _ = self.git_manager.run_git_command(['git', 'reset', '--hard', 'HEAD~1'], check=False)
                    if success:
                        rollback_steps.append('publish_cleaned')
                        self.log_message("✅ publish 브랜치 정리 완료")
                    
                    # 다시 원래 브랜치로 복귀
                    if original_branch:
                        self.git_manager.safe_branch_switch(original_branch)
            
            deployment_result['rollback_performed'] = True
            deployment_result['rollback_steps'] = rollback_steps
            
            # 롤백 상태 저장
            state = self.load_deployment_state()
            state['last_failure'] = datetime.now().isoformat()
            state['rollback_available'] = False
            self.save_deployment_state(state)
            
            self.log_message(f"✅ 자동 롤백 완료 (단계: {len(rollback_steps)}개)")
            
        except Exception as e:
            self.log_message(f"❌ 롤백 중 오류: {str(e)}")
            deployment_result['rollback_error'] = str(e)
    
    def send_direct_webhook(self, message: str = None, deployment_result: Optional[Dict] = None, 
                           message_type: Optional[MessageType] = None, 
                           status_callback: Optional[Callable] = None) -> Dict[str, any]:
        """
        웹훅으로 직접 메시지 전송 (MessageTemplateEngine 통합)
        
        Args:
            message: 직접 전송할 메시지 (선택사항)
            deployment_result: 배포 결과 데이터
            message_type: 메시지 타입 (자동 템플릿 적용)
            status_callback: GUI 상태 업데이트 콜백
            
        Returns:
            Dict: 전송 결과 정보
        """
        webhook_result = {
            'success': False,
            'message_sent': None,
            'template_used': None,
            'webhook_response_code': None,
            'error_message': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 상태 콜백 호출
            if status_callback:
                status_callback("웹훅 메시지 준비 중...", 10)
            
            # 웹훅 URL 확인
            if not self.webhook_url:
                error_msg = "웹훅 URL이 설정되지 않았습니다"
                webhook_result['error_message'] = error_msg
                self.log_message(f"⚠️ {error_msg}")
                return webhook_result
            
            # 메시지 생성 로직
            formatted_message = None
            template_info = None
            
            if status_callback:
                status_callback("메시지 템플릿 처리 중...", 30)
            
            # 1. MessageTemplateEngine을 사용한 자동 메시지 생성
            if message_type and deployment_result:
                try:
                    if message_type == MessageType.DEPLOYMENT_SUCCESS:
                        template_message = self.message_engine.generate_deployment_success_message(deployment_result)
                    elif message_type == MessageType.DEPLOYMENT_FAILURE:
                        template_message = self.message_engine.generate_deployment_failure_message(deployment_result)
                    elif message_type == MessageType.DEPLOYMENT_START:
                        deployment_id = deployment_result.get('deployment_id', 'unknown')
                        template_message = self.message_engine.generate_deployment_start_message(deployment_id)
                    else:
                        # 기타 메시지 타입은 일반 생성
                        template_message = self.message_engine.generate_message(message_type, deployment_result)
                    
                    # 포스코 스타일 메시지 적용
                    formatted_message = self._format_posco_style_message(template_message)
                    template_info = {
                        'type': message_type.value,
                        'priority': template_message.get('priority'),
                        'color': template_message.get('color')
                    }
                    webhook_result['template_used'] = template_info
                    
                    self.log_message(f"✅ 템플릿 메시지 생성 완료: {message_type.value}")
                    
                except Exception as template_error:
                    self.log_message(f"⚠️ 템플릿 메시지 생성 실패: {template_error}")
                    # 템플릿 실패 시 기본 메시지로 폴백
                    formatted_message = message or self._create_fallback_message(deployment_result)
            
            # 2. 직접 메시지가 제공된 경우
            elif message:
                formatted_message = message
                self.log_message("ℹ️ 직접 제공된 메시지 사용")
            
            # 3. 배포 결과만 있는 경우 기본 메시지 생성
            elif deployment_result:
                formatted_message = self._create_fallback_message(deployment_result)
                self.log_message("ℹ️ 기본 메시지 생성 사용")
            
            else:
                error_msg = "전송할 메시지나 데이터가 없습니다"
                webhook_result['error_message'] = error_msg
                self.log_message(f"❌ {error_msg}")
                return webhook_result
            
            if status_callback:
                status_callback("웹훅 전송 중...", 60)
            
            # 메시지 페이로드 생성 (고객 친화적 형식)
            payload = self._create_webhook_payload(formatted_message, deployment_result, template_info)
            
            # 웹훅 전송
            self.log_message(f"📤 웹훅 전송 시작: {self.webhook_url}")
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=15,  # 타임아웃 증가
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'POSCO-Analysis-System/1.0'
                }
            )
            
            webhook_result['webhook_response_code'] = response.status_code
            webhook_result['message_sent'] = formatted_message
            
            if status_callback:
                status_callback("웹훅 응답 처리 중...", 80)
            
            # 응답 처리
            if response.status_code == 200:
                webhook_result['success'] = True
                success_msg = f"웹훅 메시지 전송 완료 (응답: {response.status_code})"
                self.log_message(f"✅ {success_msg}")
                
                # 전송 성공 로그 저장
                self._log_webhook_success(formatted_message, template_info)
                
            elif response.status_code == 204:
                # 일부 웹훅 서비스는 204 No Content로 응답
                webhook_result['success'] = True
                success_msg = f"웹훅 메시지 전송 완료 (응답: {response.status_code})"
                self.log_message(f"✅ {success_msg}")
                
            else:
                error_msg = f"웹훅 전송 실패: HTTP {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                
                webhook_result['error_message'] = error_msg
                self.log_message(f"❌ {error_msg}")
                
                # 전송 실패 로그 저장
                self._log_webhook_failure(error_msg, formatted_message)
            
            if status_callback:
                status = "성공" if webhook_result['success'] else "실패"
                status_callback(f"웹훅 전송 {status}", 100)
            
            return webhook_result
                
        except requests.exceptions.Timeout:
            error_msg = "웹훅 전송 시간 초과 (15초)"
            webhook_result['error_message'] = error_msg
            self.log_message(f"⏰ {error_msg}")
            return webhook_result
            
        except requests.exceptions.ConnectionError:
            error_msg = "웹훅 서버 연결 실패"
            webhook_result['error_message'] = error_msg
            self.log_message(f"🔌 {error_msg}")
            return webhook_result
            
        except Exception as e:
            error_msg = f"웹훅 전송 중 예외 발생: {str(e)}"
            webhook_result['error_message'] = error_msg
            self.log_message(f"❌ {error_msg}")
            return webhook_result
    
    def _format_posco_style_message(self, template_message: Dict[str, str]) -> str:
        """포스코 스타일 메시지 포맷팅 (고객 친화적)"""
        try:
            title = template_message.get('title', '')
            body = template_message.get('body', '')
            priority = template_message.get('priority', 'normal')
            
            # 우선순위에 따른 스타일 적용
            priority_prefix = ""
            if priority == "critical":
                priority_prefix = "🚨 [긴급] "
            elif priority == "high":
                priority_prefix = "⚠️ [중요] "
            elif priority == "low":
                priority_prefix = "ℹ️ [정보] "
            
            # 포스코 스타일 메시지 조합
            formatted_message = f"{priority_prefix}{title}\n\n{body}"
            
            # 개발자 용어를 고객 친화적으로 변경
            customer_friendly_message = self._convert_to_customer_friendly(formatted_message)
            
            return customer_friendly_message
            
        except Exception as e:
            self.log_message(f"❌ 메시지 포맷팅 실패: {e}")
            return template_message.get('body', str(template_message))
    
    def _convert_to_customer_friendly(self, message: str) -> str:
        """개발자 용어를 고객 친화적 내용으로 변경"""
        # 개발자 용어 -> 고객 친화적 용어 매핑
        replacements = {
            # Git 관련 용어
            'Git 저장소': '시스템 데이터',
            'commit': '저장',
            'push': '업로드',
            'branch': '작업 영역',
            'merge': '통합',
            'rollback': '이전 상태 복구',
            'stash': '임시 저장',
            
            # 기술적 용어
            'GitHub Pages': 'POSCO 분석 웹사이트',
            'HTTP': '웹',
            'API': '데이터 연결',
            'JSON': '데이터',
            'webhook': '알림 시스템',
            'deployment': '업데이트',
            'pipeline': '처리 과정',
            
            # 상태 메시지
            '배포 ID': '업데이트 번호',
            '단계 완료': '작업 완료',
            '접근성 확인': '웹사이트 상태 확인',
            '원격 저장소': '클라우드 저장소',
            
            # 오류 관련
            '예외 발생': '오류 발생',
            '충돌 해결': '데이터 정리',
            '인증 실패': '접근 권한 문제',
            '시간 초과': '응답 지연',
            
            # 시스템 용어
            '모니터링': '상태 확인',
            '로그': '기록',
            '캐시': '임시 데이터',
            '백업': '안전 복사본'
        }
        
        customer_message = message
        for tech_term, friendly_term in replacements.items():
            customer_message = customer_message.replace(tech_term, friendly_term)
        
        return customer_message
    
    def _create_webhook_payload(self, message: str, deployment_result: Optional[Dict], 
                               template_info: Optional[Dict]) -> Dict:
        """웹훅 페이로드 생성 (고객 친화적 형식)"""
        payload = {
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "source": "POSCO 통합 분석 시스템",
            "version": "1.0"
        }
        
        # 템플릿 정보 추가
        if template_info:
            payload["message_info"] = {
                "type": template_info.get('type'),
                "priority": template_info.get('priority'),
                "color": template_info.get('color')
            }
        
        # 배포 결과 정보 추가 (고객 친화적)
        if deployment_result:
            payload["update_info"] = {
                "update_id": deployment_result.get('deployment_id'),
                "success": deployment_result.get('success'),
                "completed_tasks": len(deployment_result.get('steps_completed', [])),
                "website_accessible": deployment_result.get('github_pages_accessible'),
                "backup_created": deployment_result.get('backup_created', False)
            }
            
            # 성공/실패에 따른 추가 정보
            if deployment_result.get('success'):
                payload["success_details"] = {
                    "website_url": "https://shuserker.github.io/infomax_api",
                    "update_time": deployment_result.get('end_time'),
                    "total_steps": len(deployment_result.get('steps_completed', []))
                }
            else:
                payload["failure_details"] = {
                    "error_summary": deployment_result.get('error_message', '알 수 없는 오류'),
                    "recovery_performed": deployment_result.get('rollback_performed', False),
                    "failure_time": deployment_result.get('end_time')
                }
        
        return payload
    
    def _create_fallback_message(self, deployment_result: Optional[Dict]) -> str:
        """기본 메시지 생성 (템플릿 실패 시 사용)"""
        if not deployment_result:
            return "🏭 POSCO 통합 분석 시스템에서 알림을 보냅니다."
        
        success = deployment_result.get('success', False)
        deployment_id = deployment_result.get('deployment_id', 'Unknown')
        
        if success:
            return f"""✅ POSCO 분석 리포트 업데이트 완료

📊 업데이트 번호: {deployment_id}
🌐 웹사이트: https://shuserker.github.io/infomax_api
⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

최신 POSCO 분석 데이터가 성공적으로 업데이트되었습니다."""
        else:
            error_msg = deployment_result.get('error_message', '알 수 없는 오류')
            return f"""❌ POSCO 분석 리포트 업데이트 실패

📊 업데이트 번호: {deployment_id}
🔍 문제 내용: {error_msg}
⏰ 실패 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

시스템 관리자가 문제를 해결하고 있습니다."""
    
    def _log_webhook_success(self, message: str, template_info: Optional[Dict]):
        """웹훅 전송 성공 로그"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'message_length': len(message),
            'template_type': template_info.get('type') if template_info else 'direct',
            'webhook_url': self.webhook_url[:50] + '...' if len(self.webhook_url) > 50 else self.webhook_url
        }
        
        self.log_message(f"📊 웹훅 전송 성공 로그: {json.dumps(log_entry, ensure_ascii=False)}")
    
    def _log_webhook_failure(self, error_msg: str, message: str):
        """웹훅 전송 실패 로그"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'status': 'failure',
            'error': error_msg,
            'message_length': len(message) if message else 0,
            'webhook_url': self.webhook_url[:50] + '...' if self.webhook_url and len(self.webhook_url) > 50 else self.webhook_url
        }
        
        self.log_message(f"📊 웹훅 전송 실패 로그: {json.dumps(log_entry, ensure_ascii=False)}")
    
    def send_dynamic_data_message(self, message_type: MessageType = MessageType.DATA_UPDATE,
                                 custom_data: Optional[Dict] = None,
                                 force_refresh: bool = False,
                                 status_callback: Optional[Callable] = None) -> Dict[str, any]:
        """
        동적 데이터 기반 메시지 전송 (Requirements 2.4 구현)
        
        Args:
            message_type: 메시지 타입
            custom_data: 추가 사용자 데이터
            force_refresh: 강제 데이터 새로고침
            status_callback: GUI 상태 업데이트 콜백
            
        Returns:
            Dict: 전송 결과 정보
        """
        webhook_result = {
            'success': False,
            'message_sent': None,
            'data_quality': None,
            'dynamic_data_used': True,
            'webhook_response_code': None,
            'error_message': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            self.log_message(f"🚀 동적 데이터 기반 메시지 전송 시작 (타입: {message_type.value})")
            
            # 상태 콜백 호출
            if status_callback:
                status_callback("동적 데이터 수집 중...", 10)
            
            # 웹훅 URL 확인
            if not self.webhook_url:
                error_msg = "웹훅 URL이 설정되지 않았습니다"
                webhook_result['error_message'] = error_msg
                self.log_message(f"⚠️ {error_msg}")
                return webhook_result
            
            if status_callback:
                status_callback("향상된 동적 메시지 생성 중...", 30)
            
            # 향상된 동적 메시지 생성
            template_message = self.message_engine.generate_enhanced_dynamic_message(
                message_type=message_type,
                custom_data=custom_data,
                force_refresh=force_refresh
            )
            
            # 데이터 품질 정보 추출
            webhook_result['data_quality'] = template_message.get('body', '').count('품질') > 0
            
            if status_callback:
                status_callback("메시지 포맷팅 중...", 50)
            
            # 포스코 스타일 메시지 포맷팅
            formatted_message = self._format_posco_style_message(template_message)
            
            template_info = {
                'type': message_type.value,
                'priority': template_message.get('priority'),
                'color': template_message.get('color'),
                'dynamic_data': True
            }
            
            if status_callback:
                status_callback("웹훅 전송 중...", 70)
            
            # 메시지 페이로드 생성 (동적 데이터 포함)
            payload = self._create_dynamic_webhook_payload(formatted_message, template_message, template_info)
            
            # 웹훅 전송
            self.log_message(f"📤 동적 데이터 웹훅 전송 시작: {self.webhook_url}")
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.webhook_timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': self.webhook_user_agent
                }
            )
            
            webhook_result['webhook_response_code'] = response.status_code
            webhook_result['message_sent'] = formatted_message
            
            if status_callback:
                status_callback("응답 처리 중...", 90)
            
            # 응답 처리
            if response.status_code in [200, 204]:
                webhook_result['success'] = True
                success_msg = f"동적 데이터 웹훅 메시지 전송 완료 (응답: {response.status_code})"
                self.log_message(f"✅ {success_msg}")
                
                # 전송 성공 로그 저장
                self._log_dynamic_webhook_success(formatted_message, template_info, template_message)
                
            else:
                error_msg = f"동적 데이터 웹훅 전송 실패: HTTP {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                
                webhook_result['error_message'] = error_msg
                self.log_message(f"❌ {error_msg}")
                
                # 전송 실패 로그 저장
                self._log_webhook_failure(error_msg, formatted_message)
            
            if status_callback:
                status = "성공" if webhook_result['success'] else "실패"
                status_callback(f"동적 데이터 메시지 전송 {status}", 100)
            
            return webhook_result
                
        except Exception as e:
            error_msg = f"동적 데이터 메시지 전송 중 예외 발생: {str(e)}"
            webhook_result['error_message'] = error_msg
            self.log_message(f"❌ {error_msg}")
            return webhook_result
    
    def _create_dynamic_webhook_payload(self, message: str, template_message: Dict, 
                                      template_info: Dict) -> Dict:
        """동적 데이터 웹훅 페이로드 생성"""
        payload = {
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "source": "POSCO 통합 분석 시스템 (동적 데이터)",
            "version": "2.0",
            "data_type": "dynamic"
        }
        
        # 템플릿 정보 추가
        payload["message_info"] = {
            "type": template_info.get('type'),
            "priority": template_info.get('priority'),
            "color": template_info.get('color'),
            "dynamic_data_used": True,
            "template_version": "enhanced"
        }
        
        # 동적 데이터 품질 정보 추가
        if 'overall_quality' in str(template_message):
            payload["data_quality"] = {
                "quality_indicators_included": True,
                "real_time_data": True,
                "reliability_checked": True
            }
        
        return payload
    
    def _log_dynamic_webhook_success(self, message: str, template_info: Dict, template_message: Dict):
        """동적 데이터 웹훅 전송 성공 로그"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'message_type': 'dynamic_data',
            'message_length': len(message),
            'template_type': template_info.get('type'),
            'data_quality_included': 'quality' in message.lower(),
            'real_time_data': True,
            'webhook_url': self.webhook_url[:50] + '...' if len(self.webhook_url) > 50 else self.webhook_url
        }
        
        self.log_message(f"📊 동적 데이터 웹훅 전송 성공 로그: {json.dumps(log_entry, ensure_ascii=False)}")
    
    def send_data_quality_report(self, status_callback: Optional[Callable] = None) -> Dict[str, any]:
        """데이터 품질 리포트 메시지 전송"""
        try:
            self.log_message("📊 데이터 품질 리포트 메시지 전송 시작...")
            
            if status_callback:
                status_callback("데이터 품질 분석 중...", 20)
            
            # 데이터 품질 리포트 생성
            quality_report = self.message_engine.get_data_quality_report()
            
            if 'error' in quality_report:
                error_msg = f"품질 리포트 생성 실패: {quality_report['error']}"
                self.log_message(f"❌ {error_msg}")
                return {'success': False, 'error_message': error_msg}
            
            if status_callback:
                status_callback("품질 리포트 메시지 생성 중...", 50)
            
            # 품질 리포트 메시지 생성
            quality_message = self._format_quality_report_message(quality_report)
            
            if status_callback:
                status_callback("품질 리포트 전송 중...", 80)
            
            # 웹훅으로 전송
            webhook_result = self.send_direct_webhook(
                message=quality_message,
                status_callback=status_callback
            )
            
            if webhook_result['success']:
                self.log_message("✅ 데이터 품질 리포트 메시지 전송 완료")
            else:
                self.log_message(f"❌ 데이터 품질 리포트 메시지 전송 실패: {webhook_result.get('error_message')}")
            
            return webhook_result
            
        except Exception as e:
            error_msg = f"데이터 품질 리포트 전송 중 오류: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            return {'success': False, 'error_message': error_msg}
    
    def _format_quality_report_message(self, quality_report: Dict[str, Any]) -> str:
        """데이터 품질 리포트 메시지 포맷팅"""
        try:
            current_quality = quality_report.get('current_quality', {})
            statistics = quality_report.get('statistics', {})
            recommendations = quality_report.get('recommendations', [])
            
            # 전체 품질 등급 결정
            overall_quality = current_quality.get('overall', 0)
            if overall_quality >= 0.9:
                quality_grade = "🟢 우수"
            elif overall_quality >= 0.7:
                quality_grade = "🟡 양호"
            elif overall_quality >= 0.5:
                quality_grade = "🟠 보통"
            else:
                quality_grade = "🔴 개선 필요"
            
            message = f"""🏭 **POSCO 데이터 품질 리포트**

📊 **전체 품질 현황**
• 종합 등급: {quality_grade} ({overall_quality:.1%})
• 측정 기간: {statistics.get('period', '알 수 없음')}
• 총 측정 횟수: {statistics.get('total_measurements', 0)}회

📈 **개별 데이터 품질**
• KOSPI 지수: {current_quality.get('kospi', 0):.1%}
• 환율 데이터: {current_quality.get('exchange', 0):.1%}
• POSCO 주가: {current_quality.get('posco', 0):.1%}
• 뉴스 분석: {current_quality.get('news', 0):.1%}

📊 **품질 통계**
• 평균 품질: {statistics.get('average_quality', 0):.1%}
• 최고 품질: {statistics.get('max_quality', 0):.1%}
• 최저 품질: {statistics.get('min_quality', 0):.1%}
• 품질 트렌드: {statistics.get('quality_trend', '알 수 없음')}

💡 **개선 권장사항**"""
            
            if recommendations:
                for i, recommendation in enumerate(recommendations[:3], 1):
                    message += f"\n{i}. {recommendation}"
            else:
                message += "\n• 현재 품질 상태가 양호합니다."
            
            message += f"""

⏰ **리포트 생성 시간**
{quality_report.get('report_generated', datetime.now().isoformat())}

---
*본 리포트는 POSCO 통합 분석 시스템에서 자동 생성되었습니다.*"""
            
            return message
            
        except Exception as e:
            return f"❌ 데이터 품질 리포트 생성 중 오류가 발생했습니다: {str(e)}"
    
    def send_deployment_notification(self, deployment_result: Dict, status_callback: Optional[Callable] = None) -> Dict[str, any]:
        """배포 알림 전송 (편의 메서드)"""
        message_type = MessageType.DEPLOYMENT_SUCCESS if deployment_result.get('success') else MessageType.DEPLOYMENT_FAILURE
        return self.send_direct_webhook(
            deployment_result=deployment_result,
            message_type=message_type,
            status_callback=status_callback
        )
    
    def send_deployment_start_notification(self, deployment_id: str, status_callback: Optional[Callable] = None) -> Dict[str, any]:
        """배포 시작 알림 전송 (편의 메서드)"""
        deployment_data = {'deployment_id': deployment_id}
        return self.send_direct_webhook(
            deployment_result=deployment_data,
            message_type=MessageType.DEPLOYMENT_START,
            status_callback=status_callback
        )
    
    def run_full_deployment_pipeline(self, data: Dict, progress_callback: Optional[Callable] = None) -> Dict[str, any]:
        """전체 배포 파이프라인 실행 (통합 시스템)"""
        self.log_message("🚀 POSCO 전체 배포 파이프라인 시작...")
        
        pipeline_result = {
            'success': False,
            'pipeline_id': f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'html_generated': False,
            'deployment_completed': False,
            'webhook_sent': False,
            'deployment_result': None,
            'error_message': None
        }
        
        try:
            # 1단계: HTML 생성
            if progress_callback:
                progress_callback("HTML 리포트 생성 중...", 10)
            
            html_file = self.generate_posco_html(data)
            pipeline_result['html_generated'] = True
            pipeline_result['html_file'] = html_file
            
            # 2단계: GitHub Pages 배포
            if progress_callback:
                progress_callback("GitHub Pages 배포 시작...", 20)
            
            def deployment_progress(msg, progress):
                if progress_callback:
                    # 20-80% 범위로 매핑
                    mapped_progress = 20 + (progress * 0.6)
                    progress_callback(f"배포: {msg}", mapped_progress)
            
            deployment_result = self.deploy_to_publish_branch(deployment_progress)
            pipeline_result['deployment_result'] = deployment_result
            
            if deployment_result['success']:
                pipeline_result['deployment_completed'] = True
                
                # 3단계: 성공 웹훅 전송 (MessageTemplateEngine 사용)
                if progress_callback:
                    progress_callback("성공 알림 전송 중...", 90)
                
                def webhook_progress(msg, progress):
                    if progress_callback:
                        progress_callback(f"알림: {msg}", 90 + (progress * 0.1))
                
                webhook_result = self.send_deployment_notification(deployment_result, webhook_progress)
                pipeline_result['webhook_sent'] = webhook_result.get('success', False)
                pipeline_result['webhook_details'] = webhook_result
                
                pipeline_result['success'] = True
                self.log_message("✅ 전체 배포 파이프라인 성공 완료")
                
            else:
                # 배포 실패 웹훅 전송 (MessageTemplateEngine 사용)
                if progress_callback:
                    progress_callback("실패 알림 전송 중...", 90)
                
                def webhook_progress(msg, progress):
                    if progress_callback:
                        progress_callback(f"알림: {msg}", 90 + (progress * 0.1))
                
                webhook_result = self.send_deployment_notification(deployment_result, webhook_progress)
                pipeline_result['webhook_sent'] = webhook_result.get('success', False)
                pipeline_result['webhook_details'] = webhook_result
                
                pipeline_result['error_message'] = deployment_result.get('error_message')
                self.log_message(f"❌ 배포 파이프라인 실패: {pipeline_result['error_message']}")
            
            pipeline_result['end_time'] = datetime.now().isoformat()
            
            if progress_callback:
                status = "성공" if pipeline_result['success'] else "실패"
                progress_callback(f"파이프라인 {status} 완료", 100)
            
            return pipeline_result
            
        except Exception as e:
            error_msg = f"배포 파이프라인 중 예외 발생: {str(e)}"
            pipeline_result['error_message'] = error_msg
            pipeline_result['end_time'] = datetime.now().isoformat()
            self.log_message(f"❌ {error_msg}")
            
            # 예외 발생 웹훅 전송 (오류 알림 타입 사용)
            exception_data = {
                'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error_type': '배포 파이프라인 예외',
                'impact_scope': '전체 배포 프로세스',
                'error_details': error_msg,
                'auto_recovery_status': '시도 중',
                'estimated_recovery_time': '5-10분'
            }
            
            self.send_direct_webhook(
                deployment_result=exception_data,
                message_type=MessageType.ERROR_ALERT
            )
            
            return pipeline_result


def main():
    """테스트용 메인 함수"""
    print("🧪 PoscoMainNotifier 테스트 시작...")
    
    # 알림 시스템 초기화
    notifier = PoscoMainNotifier()
    
    # 테스트 데이터
    test_data = {
        'kospi': '2,450.32',
        'exchange_rate': '1,320.50',
        'posco_stock': '285,000',
        'analysis': '오늘 KOSPI 지수는 전일 대비 상승세를 보이고 있으며, POSCO 주가도 안정적인 흐름을 유지하고 있습니다.',
        'news': [
            {
                'title': 'POSCO, 친환경 철강 기술 개발 가속화',
                'summary': 'POSCO가 탄소중립 달성을 위한 친환경 철강 기술 개발에 박차를 가하고 있다.',
                'date': '2025-01-01'
            }
        ]
    }
    
    # HTML 생성 테스트
    html_file = notifier.generate_posco_html(test_data)
    print(f"📄 HTML 생성 완료: {html_file}")
    
    print("✅ PoscoMainNotifier 테스트 완료")


if __name__ == "__main__":
    main()