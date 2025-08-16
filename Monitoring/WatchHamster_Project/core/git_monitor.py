#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 모니터링 시스템
정상 커밋 a763ef84 기반 Git 저장소 상태 확인 및 자동 관리 기능
"""

import subprocess
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class GitStatus:
    """Git 상태 정보"""
    branch: str
    last_commit: str
    status: str  # "최신", "업데이트 필요", "충돌", "오류"
    error_message: Optional[str] = None
    uncommitted_changes: bool = False
    untracked_files: List[str] = None
    modified_files: List[str] = None
    ahead_commits: int = 0
    behind_commits: int = 0
    
    def __post_init__(self):
        if self.untracked_files is None:
            self.untracked_files = []
        if self.modified_files is None:
            self.modified_files = []

class GitMonitor:
    """Git 저장소 모니터링 및 관리 클래스"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('git_monitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _run_git_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """
        Git 명령어를 안전하게 실행
        
        Args:
            command: Git 명령어 리스트
            timeout: 타임아웃 (초)
            
        Returns:
            (성공여부, stdout, stderr)
        """
        try:
            # 페이저 비활성화를 위한 환경 변수 설정
            env = os.environ.copy()
            env['GIT_PAGER'] = ''
            
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Git 명령어 타임아웃: {' '.join(command)}")
            return False, "", "명령어 실행 타임아웃"
        except Exception as e:
            self.logger.error(f"Git 명령어 실행 오류: {e}")
            return False, "", str(e)
    
    def check_git_repository(self) -> bool:
        """Git 저장소 여부 확인"""
        success, _, _ = self._run_git_command(['git', 'rev-parse', '--git-dir'])
        return success
    
    def get_current_branch(self) -> Optional[str]:
        """현재 브랜치 이름 가져오기"""
        success, output, _ = self._run_git_command(['git', 'branch', '--show-current'])
        return output if success else None
    
    def get_last_commit(self) -> Optional[str]:
        """마지막 커밋 해시 가져오기"""
        success, output, _ = self._run_git_command(['git', 'rev-parse', 'HEAD'])
        return output if success else None
    
    def get_commit_info(self, commit_hash: Optional[str] = None) -> Optional[Dict]:
        """커밋 정보 가져오기"""
        cmd = ['git', 'log', '--oneline', '-1']
        if commit_hash:
            cmd.append(commit_hash)
            
        success, output, _ = self._run_git_command(cmd)
        if not success:
            return None
            
        parts = output.split(' ', 1)
        return {
            'hash': parts[0] if parts else '',
            'message': parts[1] if len(parts) > 1 else ''
        }
    
    def check_uncommitted_changes(self) -> Tuple[bool, List[str], List[str]]:
        """
        커밋되지 않은 변경사항 확인
        
        Returns:
            (변경사항 존재여부, 수정된 파일 목록, 추적되지 않은 파일 목록)
        """
        # 수정된 파일 확인
        success, modified_output, _ = self._run_git_command(['git', 'diff', '--name-only'])
        modified_files = modified_output.split('\n') if success and modified_output else []
        
        # 스테이징된 파일 확인
        success, staged_output, _ = self._run_git_command(['git', 'diff', '--cached', '--name-only'])
        staged_files = staged_output.split('\n') if success and staged_output else []
        
        # 추적되지 않은 파일 확인
        success, untracked_output, _ = self._run_git_command(['git', 'ls-files', '--others', '--exclude-standard'])
        untracked_files = untracked_output.split('\n') if success and untracked_output else []
        
        all_modified = list(set(modified_files + staged_files))
        all_modified = [f for f in all_modified if f]  # 빈 문자열 제거
        untracked_files = [f for f in untracked_files if f]  # 빈 문자열 제거
        
        has_changes = bool(all_modified or untracked_files)
        
        return has_changes, all_modified, untracked_files
    
    def check_remote_status(self) -> Tuple[int, int]:
        """
        원격 저장소와의 상태 비교
        
        Returns:
            (앞선 커밋 수, 뒤처진 커밋 수)
        """
        # 원격 저장소 정보 가져오기
        success, _, _ = self._run_git_command(['git', 'fetch', '--dry-run'])
        if not success:
            self.logger.warning("원격 저장소 정보를 가져올 수 없습니다")
            return 0, 0
        
        # 앞선 커밋 수 확인
        success, ahead_output, _ = self._run_git_command(['git', 'rev-list', '--count', 'HEAD', '^origin/HEAD'])
        ahead_count = int(ahead_output) if success and ahead_output.isdigit() else 0
        
        # 뒤처진 커밋 수 확인
        success, behind_output, _ = self._run_git_command(['git', 'rev-list', '--count', 'origin/HEAD', '^HEAD'])
        behind_count = int(behind_output) if success and behind_output.isdigit() else 0
        
        return ahead_count, behind_count
    
    def get_git_status(self) -> GitStatus:
        """전체 Git 상태 확인"""
        if not self.check_git_repository():
            return GitStatus(
                branch="",
                last_commit="",
                status="오류",
                error_message="Git 저장소가 아닙니다"
            )
        
        try:
            # 기본 정보 수집
            branch = self.get_current_branch() or "unknown"
            last_commit = self.get_last_commit() or "unknown"
            
            # 변경사항 확인
            has_changes, modified_files, untracked_files = self.check_uncommitted_changes()
            
            # 원격 저장소 상태 확인
            ahead_count, behind_count = self.check_remote_status()
            
            # 상태 결정
            if behind_count > 0:
                status = "업데이트 필요"
            elif has_changes:
                status = "변경사항 있음"
            else:
                status = "최신"
            
            return GitStatus(
                branch=branch,
                last_commit=last_commit,
                status=status,
                uncommitted_changes=has_changes,
                untracked_files=untracked_files,
                modified_files=modified_files,
                ahead_commits=ahead_count,
                behind_commits=behind_count
            )
            
        except Exception as e:
            self.logger.error(f"Git 상태 확인 중 오류: {e}")
            return GitStatus(
                branch="",
                last_commit="",
                status="오류",
                error_message=str(e)
            )
    
    def attempt_git_update(self) -> Tuple[bool, str]:
        """
        Git 업데이트 시도
        
        Returns:
            (성공여부, 메시지)
        """
        try:
            # 현재 상태 확인
            status = self.get_git_status()
            
            if status.status == "오류":
                return False, f"Git 상태 오류: {status.error_message}"
            
            # 변경사항이 있으면 스태시
            if status.uncommitted_changes:
                self.logger.info("변경사항을 임시 저장합니다...")
                success, _, error = self._run_git_command(['git', 'stash', 'push', '-m', 'Auto stash before update'])
                if not success:
                    return False, f"변경사항 임시 저장 실패: {error}"
            
            # 원격 저장소에서 가져오기
            self.logger.info("원격 저장소에서 업데이트를 가져옵니다...")
            success, output, error = self._run_git_command(['git', 'pull', '--rebase'])
            
            if not success:
                # 충돌이 발생한 경우 자동 해결 시도
                if "conflict" in error.lower() or "merge conflict" in error.lower():
                    return self._handle_merge_conflict()
                else:
                    return False, f"Git 업데이트 실패: {error}"
            
            # 스태시된 변경사항 복원
            if status.uncommitted_changes:
                self.logger.info("임시 저장된 변경사항을 복원합니다...")
                success, _, error = self._run_git_command(['git', 'stash', 'pop'])
                if not success:
                    self.logger.warning(f"변경사항 복원 실패: {error}")
                    return True, f"업데이트 성공, 하지만 변경사항 복원 실패: {error}"
            
            return True, "Git 업데이트가 성공적으로 완료되었습니다"
            
        except Exception as e:
            self.logger.error(f"Git 업데이트 중 오류: {e}")
            return False, f"업데이트 중 예외 발생: {str(e)}"
    
    def _handle_merge_conflict(self) -> Tuple[bool, str]:
        """
        병합 충돌 자동 해결 시도
        
        Returns:
            (성공여부, 메시지)
        """
        try:
            self.logger.info("병합 충돌을 자동으로 해결합니다...")
            
            # 충돌 파일 목록 확인
            success, output, _ = self._run_git_command(['git', 'diff', '--name-only', '--diff-filter=U'])
            if not success:
                return False, "충돌 파일 목록을 가져올 수 없습니다"
            
            conflict_files = [f for f in output.split('\n') if f]
            
            if not conflict_files:
                return False, "충돌 파일을 찾을 수 없습니다"
            
            self.logger.info(f"충돌 파일: {', '.join(conflict_files)}")
            
            # 간단한 자동 해결 시도 (우리 버전 선택)
            for file in conflict_files:
                success, _, error = self._run_git_command(['git', 'checkout', '--ours', file])
                if not success:
                    self.logger.warning(f"파일 {file} 자동 해결 실패: {error}")
                    continue
                
                # 파일을 스테이징
                success, _, error = self._run_git_command(['git', 'add', file])
                if not success:
                    self.logger.warning(f"파일 {file} 스테이징 실패: {error}")
            
            # 병합 완료
            success, _, error = self._run_git_command(['git', 'rebase', '--continue'])
            if success:
                return True, f"충돌이 자동으로 해결되었습니다 (파일: {', '.join(conflict_files)})"
            else:
                # 리베이스 중단
                self._run_git_command(['git', 'rebase', '--abort'])
                return False, f"충돌 해결 실패, 리베이스를 중단했습니다: {error}"
                
        except Exception as e:
            self.logger.error(f"충돌 해결 중 오류: {e}")
            # 안전을 위해 리베이스 중단
            self._run_git_command(['git', 'rebase', '--abort'])
            return False, f"충돌 해결 중 예외 발생: {str(e)}"
    
    def detect_conflicts(self) -> List[str]:
        """현재 충돌 상태인 파일들 감지"""
        success, output, _ = self._run_git_command(['git', 'diff', '--name-only', '--diff-filter=U'])
        if not success:
            return []
        
        return [f for f in output.split('\n') if f]
    
    def check_repository_health(self) -> Dict[str, any]:
        """저장소 건강 상태 종합 검사"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'repository_valid': False,
            'git_status': None,
            'conflicts': [],
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Git 저장소 유효성 확인
            if not self.check_git_repository():
                health_report['issues'].append("Git 저장소가 아닙니다")
                health_report['recommendations'].append("git init으로 저장소를 초기화하세요")
                return health_report
            
            health_report['repository_valid'] = True
            
            # Git 상태 확인
            git_status = self.get_git_status()
            health_report['git_status'] = asdict(git_status)
            
            # 충돌 확인
            conflicts = self.detect_conflicts()
            health_report['conflicts'] = conflicts
            
            if conflicts:
                health_report['issues'].append(f"병합 충돌이 있습니다: {', '.join(conflicts)}")
                health_report['recommendations'].append("충돌을 수동으로 해결하거나 자동 해결을 시도하세요")
            
            # 상태별 권장사항
            if git_status.status == "업데이트 필요":
                health_report['recommendations'].append("git pull을 실행하여 최신 버전으로 업데이트하세요")
            elif git_status.uncommitted_changes:
                health_report['recommendations'].append("변경사항을 커밋하거나 스태시하세요")
            
            # 원격 저장소 연결 확인
            success, _, _ = self._run_git_command(['git', 'remote', '-v'])
            if not success:
                health_report['issues'].append("원격 저장소 설정이 없습니다")
                health_report['recommendations'].append("원격 저장소를 추가하세요")
            
        except Exception as e:
            health_report['issues'].append(f"건강 상태 검사 중 오류: {str(e)}")
            
        return health_report
    
    def generate_alert_message(self, issue_type: str, details: Dict = None) -> str:
        """Git 관련 알림 메시지 생성"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if details is None:
            details = {}
        
        messages = {
            'update_needed': f"""
🔄 **Git 업데이트 필요**
⏰ 시간: {timestamp}
📍 상태: 원격 저장소에 새로운 커밋이 있습니다
🔢 뒤처진 커밋: {details.get('behind_commits', 0)}개
💡 권장사항: `git pull`을 실행하여 업데이트하세요
""",
            
            'conflict_detected': f"""
⚠️ **Git 충돌 감지**
⏰ 시간: {timestamp}
📍 상태: 병합 충돌이 발생했습니다
📁 충돌 파일: {', '.join(details.get('conflict_files', []))}
💡 권장사항: 충돌을 수동으로 해결하거나 자동 해결을 시도하세요
""",
            
            'update_success': f"""
✅ **Git 업데이트 완료**
⏰ 시간: {timestamp}
📍 상태: 성공적으로 업데이트되었습니다
📝 메시지: {details.get('message', '업데이트 완료')}
""",
            
            'update_failed': f"""
❌ **Git 업데이트 실패**
⏰ 시간: {timestamp}
📍 상태: 업데이트 중 오류가 발생했습니다
🔍 오류: {details.get('error', '알 수 없는 오류')}
💡 권장사항: 수동으로 Git 상태를 확인하세요
""",
            
            'uncommitted_changes': f"""
📝 **커밋되지 않은 변경사항**
⏰ 시간: {timestamp}
📍 상태: 작업 디렉토리에 변경사항이 있습니다
📁 수정된 파일: {len(details.get('modified_files', []))}개
📁 추적되지 않은 파일: {len(details.get('untracked_files', []))}개
💡 권장사항: 변경사항을 커밋하거나 스태시하세요
""",
            
            'repository_error': f"""
🚨 **Git 저장소 오류**
⏰ 시간: {timestamp}
📍 상태: Git 저장소에 문제가 있습니다
🔍 오류: {details.get('error', '알 수 없는 오류')}
💡 권장사항: Git 저장소 상태를 점검하세요
"""
        }
        
        return messages.get(issue_type, f"알 수 없는 Git 이슈: {issue_type}")
    
    def monitor_and_report(self) -> Dict[str, any]:
        """Git 상태 모니터링 및 리포트 생성"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'git_status': None,
            'health_check': None,
            'alerts': [],
            'actions_taken': []
        }
        
        try:
            # Git 상태 확인
            git_status = self.get_git_status()
            report['git_status'] = asdict(git_status)
            
            # 건강 상태 검사
            health_check = self.check_repository_health()
            report['health_check'] = health_check
            
            # 상태별 알림 생성
            if git_status.status == "업데이트 필요":
                alert = self.generate_alert_message('update_needed', {
                    'behind_commits': git_status.behind_commits
                })
                report['alerts'].append(alert)
            
            elif git_status.status == "변경사항 있음":
                alert = self.generate_alert_message('uncommitted_changes', {
                    'modified_files': git_status.modified_files,
                    'untracked_files': git_status.untracked_files
                })
                report['alerts'].append(alert)
            
            elif git_status.status == "오류":
                alert = self.generate_alert_message('repository_error', {
                    'error': git_status.error_message
                })
                report['alerts'].append(alert)
            
            # 충돌 감지
            conflicts = self.detect_conflicts()
            if conflicts:
                alert = self.generate_alert_message('conflict_detected', {
                    'conflict_files': conflicts
                })
                report['alerts'].append(alert)
            
        except Exception as e:
            report['status'] = 'error'
            report['error'] = str(e)
            self.logger.error(f"Git 모니터링 중 오류: {e}")
        
        return report

def main():
    """테스트 실행"""
    monitor = GitMonitor()
    
    print("=== Git 모니터링 시스템 테스트 ===")
    
    # Git 상태 확인
    print("\n1. Git 상태 확인:")
    status = monitor.get_git_status()
    print(f"브랜치: {status.branch}")
    print(f"마지막 커밋: {status.last_commit}")
    print(f"상태: {status.status}")
    if status.error_message:
        print(f"오류: {status.error_message}")
    
    # 건강 상태 검사
    print("\n2. 저장소 건강 상태:")
    health = monitor.check_repository_health()
    print(f"저장소 유효: {health['repository_valid']}")
    if health['issues']:
        print(f"문제점: {', '.join(health['issues'])}")
    if health['recommendations']:
        print(f"권장사항: {', '.join(health['recommendations'])}")
    
    # 모니터링 리포트
    print("\n3. 종합 모니터링 리포트:")
    report = monitor.monitor_and_report()
    print(f"상태: {report['status']}")
    if report['alerts']:
        print("알림:")
        for alert in report['alerts']:
            print(alert)

if __name__ == "__main__":
    main()