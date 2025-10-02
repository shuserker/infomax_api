#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 배포 관리자 (GitDeploymentManager)
POSCO 뉴스 시스템용 완전 독립 배포 시스템

주요 기능:
- 🔍 Git 상태 확인 및 충돌 감지
- 🔄 안전한 브랜치 전환 (main ↔ publish)
- 📦 자동 배포 파이프라인 (외부 의존성 없음)
- 🛡️ 로컬 변경사항 보호 (stash/commit)
- 🔄 배포 실패 시 자동 롤백

Requirements: 1.3, 3.1, 3.2 구현
"""

import os
import subprocess
import shutil
import json
import time
from datetime import datetime
from typing import Optional, Dict, List, Tuple


class GitDeploymentManager:
    """Git 배포 관리자 클래스 (완전 독립)"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Git 배포 관리자 초기화"""
        self.base_dir = base_dir or os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 로그 파일 설정
        self.log_file = os.path.join(self.script_dir, "git_deployment.log")
        
        # 배포 상태 파일
        self.state_file = os.path.join(self.script_dir, "deployment_state.json")
        
        # 브랜치 설정
        self.main_branch = "main"      # 개발용 브랜치 (비공개)
        self.publish_branch = "publish"  # 배포용 브랜치 (공개)
        
        # GitHub Pages URL 템플릿
        self.github_pages_base_url = "https://shuserker.github.io/infomax_api"
        
        # 배포 재시도 설정
        self.max_retries = 3
        self.retry_delay = 5  # 초
        
        self.log_message("🔧 Git 배포 관리자 초기화 완료 (스탠드얼론)")
    
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
    
    def run_git_command(self, command: List[str], check: bool = True) -> Tuple[bool, str]:
        """Git 명령어 실행 (안전한 실행)"""
        try:
            result = subprocess.run(
                command,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=30,  # 30초 타임아웃
                check=check
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"Git 명령 실패: {' '.join(command)} - {e.stderr.strip()}"
            self.log_message(f"❌ {error_msg}")
            return False, e.stderr.strip()
        except subprocess.TimeoutExpired:
            error_msg = f"Git 명령 타임아웃: {' '.join(command)}"
            self.log_message(f"⏰ {error_msg}")
            return False, "명령 실행 시간 초과"
        except Exception as e:
            error_msg = f"Git 명령 오류: {' '.join(command)} - {str(e)}"
            self.log_message(f"❌ {error_msg}")
            return False, str(e)
    
    def check_git_status(self) -> Dict[str, any]:
        """Git 상태 확인 및 충돌 감지 (Requirements 3.1)"""
        self.log_message("🔍 Git 상태 확인 시작...")
        
        status_info = {
            'is_git_repo': False,
            'current_branch': None,
            'has_uncommitted_changes': False,
            'has_untracked_files': False,
            'has_conflicts': False,
            'can_switch_branch': True,
            'remote_status': 'unknown',
            'error_message': None
        }
        
        try:
            # Git 저장소 확인
            success, _ = self.run_git_command(['git', 'rev-parse', '--git-dir'], check=False)
            if not success:
                status_info['error_message'] = "Git 저장소가 아닙니다"
                return status_info
            
            status_info['is_git_repo'] = True
            
            # 현재 브랜치 확인
            success, current_branch = self.run_git_command(['git', 'branch', '--show-current'])
            if success:
                status_info['current_branch'] = current_branch
                self.log_message(f"📍 현재 브랜치: {current_branch}")
            
            # 변경사항 확인
            success, git_status = self.run_git_command(['git', 'status', '--porcelain'])
            if success:
                if git_status:
                    status_info['has_uncommitted_changes'] = True
                    # 추적되지 않은 파일 확인
                    untracked_files = [line for line in git_status.split('\n') if line.startswith('??')]
                    if untracked_files:
                        status_info['has_untracked_files'] = True
                    self.log_message(f"⚠️ 커밋되지 않은 변경사항 발견: {len(git_status.split())}")
            
            # 충돌 상태 확인
            success, merge_head = self.run_git_command(['git', 'rev-parse', '--verify', 'MERGE_HEAD'], check=False)
            if success:
                status_info['has_conflicts'] = True
                self.log_message("⚠️ 병합 충돌 상태 감지")
            
            # 원격 저장소 상태 확인
            success, _ = self.run_git_command(['git', 'fetch', '--dry-run'], check=False)
            if success:
                status_info['remote_status'] = 'accessible'
            else:
                status_info['remote_status'] = 'inaccessible'
                self.log_message("⚠️ 원격 저장소 접근 불가")
            
            # 브랜치 전환 가능성 판단
            if status_info['has_conflicts']:
                status_info['can_switch_branch'] = False
                status_info['error_message'] = "병합 충돌로 인해 브랜치 전환 불가"
            
            self.log_message("✅ Git 상태 확인 완료")
            return status_info
            
        except Exception as e:
            error_msg = f"Git 상태 확인 중 오류: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            status_info['error_message'] = error_msg
            return status_info
    
    def detect_conflict_files(self) -> Dict[str, any]:
        """충돌 파일 감지 및 분석 (Requirements 3.2)"""
        self.log_message("🔍 충돌 파일 감지 시작...")
        
        conflict_info = {
            'has_conflicts': False,
            'conflict_files': [],
            'merge_in_progress': False,
            'conflict_details': {},
            'auto_resolvable': [],
            'manual_required': [],
            'error_message': None
        }
        
        try:
            # 병합 상태 확인
            success, _ = self.run_git_command(['git', 'rev-parse', '--verify', 'MERGE_HEAD'], check=False)
            if success:
                conflict_info['merge_in_progress'] = True
                self.log_message("🔄 병합 진행 중 감지")
            
            # 충돌 파일 목록 확인
            success, conflict_files = self.run_git_command(['git', 'diff', '--name-only', '--diff-filter=U'], check=False)
            if not success:
                self.log_message("✅ 충돌 파일 없음")
                return conflict_info
            
            if not conflict_files.strip():
                self.log_message("✅ 충돌 파일 없음")
                return conflict_info
            
            conflict_list = [f.strip() for f in conflict_files.split('\n') if f.strip()]
            conflict_info['has_conflicts'] = True
            conflict_info['conflict_files'] = conflict_list
            
            self.log_message(f"⚠️ 충돌 파일 발견: {len(conflict_list)}개")
            
            # 각 충돌 파일 분석
            for conflict_file in conflict_list:
                self.log_message(f"🔍 충돌 파일 분석: {conflict_file}")
                
                file_analysis = self._analyze_conflict_file(conflict_file)
                conflict_info['conflict_details'][conflict_file] = file_analysis
                
                # 자동 해결 가능성 판단
                if file_analysis['auto_resolvable']:
                    conflict_info['auto_resolvable'].append(conflict_file)
                    self.log_message(f"🤖 자동 해결 가능: {conflict_file}")
                else:
                    conflict_info['manual_required'].append(conflict_file)
                    self.log_message(f"👤 수동 해결 필요: {conflict_file}")
            
            return conflict_info
            
        except Exception as e:
            error_msg = f"충돌 파일 감지 중 오류: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            conflict_info['error_message'] = error_msg
            return conflict_info
    
    def _analyze_conflict_file(self, file_path: str) -> Dict[str, any]:
        """개별 충돌 파일 분석"""
        analysis = {
            'file_path': file_path,
            'file_type': self._get_file_type(file_path),
            'conflict_markers': 0,
            'conflict_sections': [],
            'auto_resolvable': False,
            'resolution_strategy': None,
            'file_size': 0,
            'error': None
        }
        
        try:
            full_path = os.path.join(self.base_dir, file_path)
            
            if not os.path.exists(full_path):
                analysis['error'] = "파일이 존재하지 않음"
                return analysis
            
            # 파일 크기 확인
            analysis['file_size'] = os.path.getsize(full_path)
            
            # 파일 내용 읽기 및 충돌 마커 분석
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 충돌 마커 찾기
            lines = content.split('\n')
            in_conflict = False
            current_section = None
            
            for i, line in enumerate(lines):
                if line.startswith('<<<<<<<'):
                    analysis['conflict_markers'] += 1
                    in_conflict = True
                    current_section = {
                        'start_line': i + 1,
                        'ours_content': [],
                        'theirs_content': [],
                        'separator_line': None,
                        'end_line': None
                    }
                elif line.startswith('=======') and in_conflict:
                    current_section['separator_line'] = i + 1
                elif line.startswith('>>>>>>>') and in_conflict:
                    current_section['end_line'] = i + 1
                    analysis['conflict_sections'].append(current_section)
                    in_conflict = False
                    current_section = None
                elif in_conflict and current_section:
                    if current_section['separator_line'] is None:
                        current_section['ours_content'].append(line)
                    else:
                        current_section['theirs_content'].append(line)
            
            # 자동 해결 가능성 판단
            analysis['auto_resolvable'] = self._can_auto_resolve(analysis)
            if analysis['auto_resolvable']:
                analysis['resolution_strategy'] = self._get_resolution_strategy(analysis)
            
            return analysis
            
        except Exception as e:
            analysis['error'] = f"파일 분석 중 오류: {str(e)}"
            return analysis
    
    def _get_file_type(self, file_path: str) -> str:
        """파일 타입 확인"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
            return 'code'
        elif ext in ['.html', '.htm', '.xml']:
            return 'markup'
        elif ext in ['.css', '.scss', '.sass']:
            return 'style'
        elif ext in ['.json', '.yaml', '.yml']:
            return 'config'
        elif ext in ['.md', '.txt', '.rst']:
            return 'text'
        else:
            return 'other'
    
    def _can_auto_resolve(self, analysis: Dict[str, any]) -> bool:
        """자동 해결 가능성 판단"""
        # 충돌 섹션이 너무 많으면 수동 해결
        if len(analysis['conflict_sections']) > 5:
            return False
        
        # 파일이 너무 크면 수동 해결
        if analysis['file_size'] > 100000:  # 100KB
            return False
        
        # 코드 파일의 경우 더 신중하게 판단
        if analysis['file_type'] == 'code':
            # 간단한 충돌만 자동 해결
            for section in analysis['conflict_sections']:
                ours_lines = len(section['ours_content'])
                theirs_lines = len(section['theirs_content'])
                
                # 한쪽이 비어있거나 매우 간단한 경우만 자동 해결
                if not (ours_lines == 0 or theirs_lines == 0 or (ours_lines + theirs_lines) <= 3):
                    return False
        
        return True
    
    def _get_resolution_strategy(self, analysis: Dict[str, any]) -> str:
        """해결 전략 결정"""
        if analysis['file_type'] in ['config', 'text']:
            return 'prefer_ours'  # 설정 파일은 우리 버전 우선
        elif analysis['file_type'] == 'code':
            return 'smart_merge'  # 코드는 스마트 병합 시도
        else:
            return 'prefer_ours'  # 기본적으로 우리 버전 우선
    
    def handle_git_conflicts(self, gui_callback=None) -> Dict[str, any]:
        """Git 충돌 자동 해결 시스템 (Requirements 3.2, 3.3)"""
        self.log_message("🔧 Git 충돌 해결 시스템 시작...")
        
        resolution_result = {
            'success': False,
            'conflicts_detected': False,
            'auto_resolved': [],
            'manual_required': [],
            'failed_resolutions': [],
            'resolution_summary': {},
            'gui_intervention_needed': False,
            'error_message': None
        }
        
        try:
            # 1단계: 충돌 파일 감지 및 분석
            conflict_info = self.detect_conflict_files()
            
            if conflict_info.get('error_message'):
                resolution_result['error_message'] = conflict_info['error_message']
                return resolution_result
            
            if not conflict_info['has_conflicts']:
                self.log_message("✅ 충돌 파일 없음 - 해결 완료")
                resolution_result['success'] = True
                return resolution_result
            
            resolution_result['conflicts_detected'] = True
            self.log_message(f"⚠️ 총 {len(conflict_info['conflict_files'])}개 충돌 파일 감지")
            
            # 2단계: 자동 해결 가능한 파일들 처리
            auto_resolvable = conflict_info.get('auto_resolvable', [])
            if auto_resolvable:
                self.log_message(f"🤖 자동 해결 시도: {len(auto_resolvable)}개 파일")
                
                for conflict_file in auto_resolvable:
                    if self._auto_resolve_conflict(conflict_file, conflict_info['conflict_details'][conflict_file]):
                        resolution_result['auto_resolved'].append(conflict_file)
                        self.log_message(f"✅ 자동 해결 완료: {conflict_file}")
                    else:
                        resolution_result['failed_resolutions'].append(conflict_file)
                        resolution_result['manual_required'].append(conflict_file)
                        self.log_message(f"❌ 자동 해결 실패: {conflict_file}")
            
            # 3단계: 수동 해결이 필요한 파일들 확인
            manual_required = conflict_info.get('manual_required', []) + resolution_result['failed_resolutions']
            if manual_required:
                resolution_result['manual_required'] = list(set(manual_required))  # 중복 제거
                resolution_result['gui_intervention_needed'] = True
                
                self.log_message(f"👤 수동 해결 필요: {len(resolution_result['manual_required'])}개 파일")
                
                # GUI 콜백이 있으면 수동 해결 인터페이스 호출 (Requirements 3.3)
                if gui_callback:
                    self.log_message("🖥️ GUI 수동 해결 인터페이스 호출...")
                    gui_result = gui_callback(resolution_result['manual_required'], conflict_info)
                    
                    if gui_result and gui_result.get('resolved_files'):
                        resolution_result['auto_resolved'].extend(gui_result['resolved_files'])
                        # 해결된 파일들을 수동 필요 목록에서 제거
                        for resolved_file in gui_result['resolved_files']:
                            if resolved_file in resolution_result['manual_required']:
                                resolution_result['manual_required'].remove(resolved_file)
            
            # 4단계: 모든 충돌이 해결되었는지 확인
            if not resolution_result['manual_required']:
                # 병합 커밋 완료
                if self._complete_merge_commit():
                    resolution_result['success'] = True
                    self.log_message("✅ 모든 충돌 해결 및 병합 커밋 완료")
                else:
                    resolution_result['error_message'] = "병합 커밋 실패"
                    self.log_message("❌ 병합 커밋 실패")
            else:
                self.log_message(f"⚠️ {len(resolution_result['manual_required'])}개 파일이 수동 해결 대기 중")
            
            # 5단계: 해결 요약 생성
            resolution_result['resolution_summary'] = {
                'total_conflicts': len(conflict_info['conflict_files']),
                'auto_resolved': len(resolution_result['auto_resolved']),
                'manual_required': len(resolution_result['manual_required']),
                'failed_auto_resolution': len(resolution_result['failed_resolutions'])
            }
            
            return resolution_result
            
        except Exception as e:
            error_msg = f"충돌 해결 시스템 오류: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            resolution_result['error_message'] = error_msg
            return resolution_result
    
    def _auto_resolve_conflict(self, file_path: str, file_analysis: Dict[str, any]) -> bool:
        """개별 파일 자동 충돌 해결"""
        try:
            strategy = file_analysis.get('resolution_strategy', 'prefer_ours')
            
            if strategy == 'prefer_ours':
                # 우리 버전으로 해결
                success, _ = self.run_git_command(['git', 'checkout', '--ours', file_path])
                if success:
                    success, _ = self.run_git_command(['git', 'add', file_path])
                    return success
            
            elif strategy == 'smart_merge':
                # 스마트 병합 시도
                return self._smart_merge_file(file_path, file_analysis)
            
            return False
            
        except Exception as e:
            self.log_message(f"❌ {file_path} 자동 해결 중 오류: {str(e)}")
            return False
    
    def _smart_merge_file(self, file_path: str, file_analysis: Dict[str, any]) -> bool:
        """스마트 파일 병합"""
        try:
            full_path = os.path.join(self.base_dir, file_path)
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 충돌 마커 제거 및 스마트 병합
            lines = content.split('\n')
            resolved_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                if line.startswith('<<<<<<<'):
                    # 충돌 섹션 시작
                    ours_lines = []
                    theirs_lines = []
                    
                    i += 1
                    # 우리 버전 수집
                    while i < len(lines) and not lines[i].startswith('======='):
                        ours_lines.append(lines[i])
                        i += 1
                    
                    i += 1  # ======= 건너뛰기
                    # 그들 버전 수집
                    while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                        theirs_lines.append(lines[i])
                        i += 1
                    
                    # 스마트 병합 로직
                    merged_content = self._merge_conflict_section(ours_lines, theirs_lines, file_analysis)
                    resolved_lines.extend(merged_content)
                    
                else:
                    resolved_lines.append(line)
                
                i += 1
            
            # 해결된 내용을 파일에 쓰기
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(resolved_lines))
            
            # 파일을 스테이징
            success, _ = self.run_git_command(['git', 'add', file_path])
            return success
            
        except Exception as e:
            self.log_message(f"❌ {file_path} 스마트 병합 중 오류: {str(e)}")
            return False
    
    def _merge_conflict_section(self, ours_lines: List[str], theirs_lines: List[str], file_analysis: Dict[str, any]) -> List[str]:
        """충돌 섹션 병합 로직"""
        # 간단한 병합 전략들
        
        # 한쪽이 비어있으면 다른 쪽 선택
        if not ours_lines:
            return theirs_lines
        if not theirs_lines:
            return ours_lines
        
        # 동일한 내용이면 하나만 선택
        if ours_lines == theirs_lines:
            return ours_lines
        
        # 기본적으로 우리 버전 선택 (안전한 선택)
        return ours_lines
    
    def _complete_merge_commit(self) -> bool:
        """병합 커밋 완료"""
        try:
            # 모든 충돌이 해결되었는지 확인
            success, remaining_conflicts = self.run_git_command(['git', 'diff', '--name-only', '--diff-filter=U'], check=False)
            if success and remaining_conflicts.strip():
                self.log_message(f"❌ 아직 해결되지 않은 충돌: {remaining_conflicts}")
                return False
            
            # 병합 커밋 실행
            success, _ = self.run_git_command(['git', 'commit', '--no-edit'])
            if success:
                self.log_message("✅ 병합 커밋 완료")
                return True
            else:
                # 커밋할 변경사항이 없는 경우도 성공으로 처리
                success, status = self.run_git_command(['git', 'status', '--porcelain'])
                if success and not status.strip():
                    self.log_message("✅ 커밋할 변경사항 없음 - 병합 완료")
                    return True
                
                self.log_message("❌ 병합 커밋 실패")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 병합 커밋 중 오류: {str(e)}")
            return False
    
    def get_conflict_resolution_options(self, file_path: str) -> Dict[str, any]:
        """충돌 해결 옵션 제공 (GUI용)"""
        options = {
            'file_path': file_path,
            'resolution_options': [
                {'id': 'ours', 'name': '우리 버전 사용', 'description': '현재 브랜치의 변경사항 유지'},
                {'id': 'theirs', 'name': '그들 버전 사용', 'description': '병합하려는 브랜치의 변경사항 사용'},
                {'id': 'manual', 'name': '수동 편집', 'description': '직접 파일을 편집하여 충돌 해결'}
            ],
            'file_preview': None,
            'conflict_sections': []
        }
        
        try:
            full_path = os.path.join(self.base_dir, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 파일 내용이 너무 길면 일부만 미리보기
                    if len(content) > 2000:
                        options['file_preview'] = content[:2000] + "\n... (내용 생략) ..."
                    else:
                        options['file_preview'] = content
            
            return options
            
        except Exception as e:
            self.log_message(f"❌ 충돌 해결 옵션 생성 중 오류: {str(e)}")
            return options
    
    def resolve_conflict_with_option(self, file_path: str, resolution_option: str) -> bool:
        """선택된 옵션으로 충돌 해결"""
        try:
            if resolution_option == 'ours':
                success, _ = self.run_git_command(['git', 'checkout', '--ours', file_path])
                if success:
                    success, _ = self.run_git_command(['git', 'add', file_path])
                    if success:
                        self.log_message(f"✅ {file_path} - 우리 버전으로 해결 완료")
                        return True
            
            elif resolution_option == 'theirs':
                success, _ = self.run_git_command(['git', 'checkout', '--theirs', file_path])
                if success:
                    success, _ = self.run_git_command(['git', 'add', file_path])
                    if success:
                        self.log_message(f"✅ {file_path} - 그들 버전으로 해결 완료")
                        return True
            
            elif resolution_option == 'manual':
                # 수동 해결의 경우 파일이 이미 편집되었다고 가정하고 스테이징만 수행
                success, _ = self.run_git_command(['git', 'add', file_path])
                if success:
                    self.log_message(f"✅ {file_path} - 수동 해결 완료")
                    return True
            
            self.log_message(f"❌ {file_path} - {resolution_option} 옵션으로 해결 실패")
            return False
            
        except Exception as e:
            self.log_message(f"❌ {file_path} 충돌 해결 중 오류: {str(e)}")
            return False
    
    def safe_branch_switch(self, target_branch: str, progress_callback=None) -> Dict[str, any]:
        """안전한 브랜치 전환 (Requirements 1.3)"""
        self.log_message(f"🔄 안전한 브랜치 전환 시작: {target_branch}")
        
        switch_result = {
            'success': False,
            'target_branch': target_branch,
            'original_branch': None,
            'stash_created': False,
            'stash_message': None,
            'conflicts_resolved': False,
            'branch_created': False,
            'error_message': None,
            'steps_completed': []
        }
        
        try:
            # 1단계: 현재 상태 확인
            step_msg = "Git 상태 확인 중..."
            self.log_message(f"1️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg)
            switch_result['steps_completed'].append('status_check')
            
            status_info = self.check_git_status()
            
            if not status_info['is_git_repo']:
                switch_result['error_message'] = "Git 저장소가 아닙니다"
                self.log_message("❌ Git 저장소가 아닙니다")
                return switch_result
            
            current_branch = status_info['current_branch']
            switch_result['original_branch'] = current_branch
            
            if current_branch == target_branch:
                self.log_message(f"✅ 이미 {target_branch} 브랜치에 있습니다")
                switch_result['success'] = True
                return switch_result
            
            # 2단계: 충돌 상태 확인 및 해결
            if status_info['has_conflicts']:
                step_msg = "충돌 상태 감지 - 자동 해결 시도..."
                self.log_message(f"2️⃣ {step_msg}")
                if progress_callback:
                    progress_callback(step_msg)
                switch_result['steps_completed'].append('conflict_detection')
                
                # 향상된 충돌 해결 시스템 사용
                conflict_result = self.handle_git_conflicts()
                
                if conflict_result['success']:
                    switch_result['conflicts_resolved'] = True
                    switch_result['conflict_resolution_summary'] = conflict_result['resolution_summary']
                    self.log_message("✅ 충돌 해결 완료")
                    switch_result['steps_completed'].append('conflict_resolution')
                elif conflict_result['gui_intervention_needed']:
                    # GUI 개입이 필요한 경우
                    switch_result['error_message'] = f"수동 해결 필요한 파일: {', '.join(conflict_result['manual_required'])}"
                    switch_result['manual_conflicts'] = conflict_result['manual_required']
                    switch_result['conflict_details'] = conflict_result
                    self.log_message(f"👤 수동 해결 필요: {len(conflict_result['manual_required'])}개 파일")
                    return switch_result
                else:
                    switch_result['error_message'] = conflict_result.get('error_message', '충돌 해결 실패')
                    self.log_message("❌ 충돌 해결 실패")
                    return switch_result
            
            # 3단계: 변경사항 처리 (stash) - Requirements 1.3
            if status_info['has_uncommitted_changes']:
                step_msg = "변경사항 stash 처리..."
                self.log_message(f"3️⃣ {step_msg}")
                if progress_callback:
                    progress_callback(step_msg)
                switch_result['steps_completed'].append('stash_detection')
                
                # 현재 시간으로 stash 메시지 생성
                stash_message = f"Auto-stash before switching to {target_branch} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                switch_result['stash_message'] = stash_message
                
                # 추적되지 않은 파일도 포함하여 stash
                stash_command = ['git', 'stash', 'push', '-u', '-m', stash_message]
                success, stash_output = self.run_git_command(stash_command)
                
                if success:
                    switch_result['stash_created'] = True
                    self.log_message(f"✅ 변경사항 stash 완료: {stash_message}")
                    switch_result['steps_completed'].append('stash_creation')
                else:
                    switch_result['error_message'] = f"Stash 실패: {stash_output}"
                    self.log_message(f"❌ Stash 실패: {stash_output}")
                    return switch_result
            
            # 4단계: 원격 저장소에서 최신 정보 가져오기
            step_msg = "원격 저장소 정보 업데이트..."
            self.log_message(f"4️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg)
            switch_result['steps_completed'].append('remote_fetch')
            
            success, _ = self.run_git_command(['git', 'fetch', 'origin'], check=False)
            if success:
                self.log_message("✅ 원격 저장소 정보 업데이트 완료")
            else:
                self.log_message("⚠️ 원격 저장소 정보 업데이트 실패 (계속 진행)")
            
            # 5단계: 대상 브랜치 존재 확인 및 생성/전환
            step_msg = f"{target_branch} 브랜치 확인 및 전환..."
            self.log_message(f"5️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg)
            switch_result['steps_completed'].append('branch_check')
            
            # 로컬 브랜치 존재 확인
            success, _ = self.run_git_command(['git', 'show-ref', '--verify', f'refs/heads/{target_branch}'], check=False)
            
            if not success:
                # 원격 브랜치 존재 확인
                success, _ = self.run_git_command(['git', 'show-ref', '--verify', f'refs/remotes/origin/{target_branch}'], check=False)
                
                if success:
                    # 원격 브랜치를 기반으로 로컬 브랜치 생성
                    self.log_message(f"🆕 원격 {target_branch} 브랜치를 기반으로 로컬 브랜치 생성...")
                    success, _ = self.run_git_command(['git', 'checkout', '-b', target_branch, f'origin/{target_branch}'])
                else:
                    # 새 브랜치 생성
                    self.log_message(f"🆕 새로운 {target_branch} 브랜치 생성...")
                    success, _ = self.run_git_command(['git', 'checkout', '-b', target_branch])
                
                if success:
                    switch_result['branch_created'] = True
                    self.log_message(f"✅ {target_branch} 브랜치 생성 완료")
                    switch_result['steps_completed'].append('branch_creation')
                else:
                    switch_result['error_message'] = f"{target_branch} 브랜치 생성 실패"
                    self.log_message(f"❌ {target_branch} 브랜치 생성 실패")
                    return switch_result
            else:
                # 기존 브랜치로 전환
                success, checkout_output = self.run_git_command(['git', 'checkout', target_branch])
                if success:
                    self.log_message(f"✅ {target_branch} 브랜치 전환 완료")
                    switch_result['steps_completed'].append('branch_switch')
                else:
                    switch_result['error_message'] = f"브랜치 전환 실패: {checkout_output}"
                    self.log_message(f"❌ {target_branch} 브랜치 전환 실패: {checkout_output}")
                    return switch_result
            
            # 6단계: 브랜치 전환 후 상태 확인
            step_msg = "브랜치 전환 후 상태 확인..."
            self.log_message(f"6️⃣ {step_msg}")
            if progress_callback:
                progress_callback(step_msg)
            switch_result['steps_completed'].append('final_verification')
            
            final_status = self.check_git_status()
            if final_status['current_branch'] == target_branch:
                switch_result['success'] = True
                success_msg = f"{target_branch} 브랜치 전환 성공적으로 완료"
                self.log_message(f"✅ {success_msg}")
                if progress_callback:
                    progress_callback(f"완료: {success_msg}")
            else:
                switch_result['error_message'] = f"브랜치 전환 검증 실패: 현재 브랜치 {final_status['current_branch']}"
                self.log_message(f"❌ 브랜치 전환 검증 실패")
                return switch_result
            
            return switch_result
            
        except Exception as e:
            error_msg = f"브랜치 전환 중 예외 발생: {str(e)}"
            switch_result['error_message'] = error_msg
            self.log_message(f"❌ {error_msg}")
            return switch_result
    
    def restore_stash_if_needed(self, stash_message: str) -> bool:
        """필요시 stash 복원"""
        try:
            if not stash_message:
                return True
            
            self.log_message(f"🔄 Stash 복원 시도: {stash_message}")
            
            # stash 목록 확인
            success, stash_list = self.run_git_command(['git', 'stash', 'list'])
            if not success or not stash_list:
                self.log_message("⚠️ 복원할 stash가 없습니다")
                return True
            
            # 해당 메시지의 stash 찾기
            stash_lines = stash_list.split('\n')
            target_stash = None
            
            for line in stash_lines:
                if stash_message in line:
                    target_stash = line.split(':')[0]  # stash@{0} 형태 추출
                    break
            
            if target_stash:
                # stash 복원
                success, _ = self.run_git_command(['git', 'stash', 'pop', target_stash])
                if success:
                    self.log_message(f"✅ Stash 복원 완료: {target_stash}")
                    return True
                else:
                    self.log_message(f"❌ Stash 복원 실패: {target_stash}")
                    return False
            else:
                self.log_message("⚠️ 해당 메시지의 stash를 찾을 수 없습니다")
                return True
                
        except Exception as e:
            self.log_message(f"❌ Stash 복원 중 오류: {str(e)}")
            return False


def main():
    """테스트용 메인 함수"""
    print("🧪 GitDeploymentManager 테스트 시작...")
    
    # 배포 관리자 초기화
    deployment_manager = GitDeploymentManager()
    
    # Git 상태 확인
    status = deployment_manager.check_git_status()
    print(f"📊 Git 상태: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    print("✅ GitDeploymentManager 테스트 완료")


if __name__ == "__main__":
    main()