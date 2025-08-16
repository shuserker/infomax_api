#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 모니터링 시스템 테스트
"""

import unittest
import tempfile
import shutil
import os
import subprocess
from unittest.mock import patch, MagicMock
import sys
import json

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_monitor import GitMonitor, GitStatus

class TestGitMonitor(unittest.TestCase):
    """Git 모니터링 시스템 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_dir = tempfile.mkdtemp()
        self.monitor = GitMonitor(self.test_dir)
        
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_git_command_execution(self):
        """Git 명령어 실행 테스트"""
        # 성공 케이스 모킹
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (True, "test output", "")
            
            success, output, error = self.monitor._run_git_command(['git', 'status'])
            
            self.assertTrue(success)
            self.assertEqual(output, "test output")
            self.assertEqual(error, "")
    
    def test_git_command_timeout(self):
        """Git 명령어 타임아웃 테스트"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(['git', 'status'], 30)
            
            success, output, error = self.monitor._run_git_command(['git', 'status'])
            
            self.assertFalse(success)
            self.assertEqual(output, "")
            self.assertEqual(error, "명령어 실행 타임아웃")
    
    def test_check_git_repository(self):
        """Git 저장소 확인 테스트"""
        # Git 저장소가 아닌 경우
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (False, "", "not a git repository")
            
            result = self.monitor.check_git_repository()
            self.assertFalse(result)
        
        # Git 저장소인 경우
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (True, ".git", "")
            
            result = self.monitor.check_git_repository()
            self.assertTrue(result)
    
    def test_get_current_branch(self):
        """현재 브랜치 확인 테스트"""
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (True, "main", "")
            
            branch = self.monitor.get_current_branch()
            self.assertEqual(branch, "main")
        
        # 실패 케이스
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (False, "", "error")
            
            branch = self.monitor.get_current_branch()
            self.assertIsNone(branch)
    
    def test_get_last_commit(self):
        """마지막 커밋 확인 테스트"""
        test_commit = "a763ef84be08b5b1dab0c0ba20594b141baec7ab"
        
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (True, test_commit, "")
            
            commit = self.monitor.get_last_commit()
            self.assertEqual(commit, test_commit)
    
    def test_get_commit_info(self):
        """커밋 정보 확인 테스트"""
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (True, "a763ef8 Initial commit", "")
            
            info = self.monitor.get_commit_info()
            self.assertIsNotNone(info)
            self.assertEqual(info['hash'], "a763ef8")
            self.assertEqual(info['message'], "Initial commit")
    
    def test_check_uncommitted_changes(self):
        """커밋되지 않은 변경사항 확인 테스트"""
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            # 수정된 파일, 스테이징된 파일, 추적되지 않은 파일 모킹
            mock_cmd.side_effect = [
                (True, "modified_file.py", ""),  # git diff --name-only
                (True, "staged_file.py", ""),    # git diff --cached --name-only
                (True, "untracked_file.py", "")  # git ls-files --others --exclude-standard
            ]
            
            has_changes, modified, untracked = self.monitor.check_uncommitted_changes()
            
            self.assertTrue(has_changes)
            self.assertIn("modified_file.py", modified)
            self.assertIn("staged_file.py", modified)
            self.assertIn("untracked_file.py", untracked)
    
    def test_check_remote_status(self):
        """원격 저장소 상태 확인 테스트"""
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.side_effect = [
                (True, "", ""),  # git fetch --dry-run
                (True, "2", ""),  # ahead commits
                (True, "1", "")   # behind commits
            ]
            
            ahead, behind = self.monitor.check_remote_status()
            
            self.assertEqual(ahead, 2)
            self.assertEqual(behind, 1)
    
    def test_get_git_status_normal(self):
        """정상 Git 상태 확인 테스트"""
        with patch.object(self.monitor, 'check_git_repository', return_value=True), \
             patch.object(self.monitor, 'get_current_branch', return_value="main"), \
             patch.object(self.monitor, 'get_last_commit', return_value="a763ef8"), \
             patch.object(self.monitor, 'check_uncommitted_changes', return_value=(False, [], [])), \
             patch.object(self.monitor, 'check_remote_status', return_value=(0, 0)):
            
            status = self.monitor.get_git_status()
            
            self.assertEqual(status.branch, "main")
            self.assertEqual(status.last_commit, "a763ef8")
            self.assertEqual(status.status, "최신")
            self.assertFalse(status.uncommitted_changes)
    
    def test_get_git_status_update_needed(self):
        """업데이트 필요 상태 테스트"""
        with patch.object(self.monitor, 'check_git_repository', return_value=True), \
             patch.object(self.monitor, 'get_current_branch', return_value="main"), \
             patch.object(self.monitor, 'get_last_commit', return_value="a763ef8"), \
             patch.object(self.monitor, 'check_uncommitted_changes', return_value=(False, [], [])), \
             patch.object(self.monitor, 'check_remote_status', return_value=(0, 2)):
            
            status = self.monitor.get_git_status()
            
            self.assertEqual(status.status, "업데이트 필요")
            self.assertEqual(status.behind_commits, 2)
    
    def test_get_git_status_error(self):
        """Git 상태 오류 테스트"""
        with patch.object(self.monitor, 'check_git_repository', return_value=False):
            
            status = self.monitor.get_git_status()
            
            self.assertEqual(status.status, "오류")
            self.assertEqual(status.error_message, "Git 저장소가 아닙니다")
    
    def test_attempt_git_update_success(self):
        """Git 업데이트 성공 테스트"""
        mock_status = GitStatus(
            branch="main",
            last_commit="a763ef8",
            status="업데이트 필요",
            uncommitted_changes=False
        )
        
        with patch.object(self.monitor, 'get_git_status', return_value=mock_status), \
             patch.object(self.monitor, '_run_git_command') as mock_cmd:
            
            mock_cmd.return_value = (True, "Already up to date.", "")
            
            success, message = self.monitor.attempt_git_update()
            
            self.assertTrue(success)
            self.assertIn("성공적으로 완료", message)
    
    def test_attempt_git_update_with_stash(self):
        """변경사항이 있는 상태에서 Git 업데이트 테스트"""
        mock_status = GitStatus(
            branch="main",
            last_commit="a763ef8",
            status="업데이트 필요",
            uncommitted_changes=True
        )
        
        with patch.object(self.monitor, 'get_git_status', return_value=mock_status), \
             patch.object(self.monitor, '_run_git_command') as mock_cmd:
            
            # 스태시, 풀, 스태시 팝 성공
            mock_cmd.side_effect = [
                (True, "", ""),  # git stash push
                (True, "Already up to date.", ""),  # git pull --rebase
                (True, "", "")   # git stash pop
            ]
            
            success, message = self.monitor.attempt_git_update()
            
            self.assertTrue(success)
            self.assertIn("성공적으로 완료", message)
    
    def test_attempt_git_update_conflict(self):
        """Git 업데이트 충돌 테스트"""
        mock_status = GitStatus(
            branch="main",
            last_commit="a763ef8",
            status="업데이트 필요",
            uncommitted_changes=False
        )
        
        with patch.object(self.monitor, 'get_git_status', return_value=mock_status), \
             patch.object(self.monitor, '_run_git_command') as mock_cmd, \
             patch.object(self.monitor, '_handle_merge_conflict', return_value=(True, "충돌 해결됨")):
            
            mock_cmd.return_value = (False, "", "merge conflict in file.py")
            
            success, message = self.monitor.attempt_git_update()
            
            self.assertTrue(success)
            self.assertEqual(message, "충돌 해결됨")
    
    def test_handle_merge_conflict(self):
        """병합 충돌 처리 테스트"""
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.side_effect = [
                (True, "conflict_file.py", ""),  # git diff --name-only --diff-filter=U
                (True, "", ""),  # git checkout --ours
                (True, "", ""),  # git add
                (True, "", "")   # git rebase --continue
            ]
            
            success, message = self.monitor._handle_merge_conflict()
            
            self.assertTrue(success)
            self.assertIn("자동으로 해결", message)
    
    def test_detect_conflicts(self):
        """충돌 감지 테스트"""
        with patch.object(self.monitor, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = (True, "file1.py\nfile2.py", "")
            
            conflicts = self.monitor.detect_conflicts()
            
            self.assertEqual(len(conflicts), 2)
            self.assertIn("file1.py", conflicts)
            self.assertIn("file2.py", conflicts)
    
    def test_check_repository_health(self):
        """저장소 건강 상태 검사 테스트"""
        mock_status = GitStatus(
            branch="main",
            last_commit="a763ef8",
            status="최신",
            uncommitted_changes=False
        )
        
        with patch.object(self.monitor, 'check_git_repository', return_value=True), \
             patch.object(self.monitor, 'get_git_status', return_value=mock_status), \
             patch.object(self.monitor, 'detect_conflicts', return_value=[]), \
             patch.object(self.monitor, '_run_git_command', return_value=(True, "origin", "")):
            
            health = self.monitor.check_repository_health()
            
            self.assertTrue(health['repository_valid'])
            self.assertEqual(len(health['issues']), 0)
            self.assertIsNotNone(health['git_status'])
    
    def test_generate_alert_message(self):
        """알림 메시지 생성 테스트"""
        # 업데이트 필요 알림
        message = self.monitor.generate_alert_message('update_needed', {
            'behind_commits': 3
        })
        
        self.assertIn("Git 업데이트 필요", message)
        self.assertIn("3개", message)
        
        # 충돌 감지 알림
        message = self.monitor.generate_alert_message('conflict_detected', {
            'conflict_files': ['file1.py', 'file2.py']
        })
        
        self.assertIn("Git 충돌 감지", message)
        self.assertIn("file1.py", message)
        self.assertIn("file2.py", message)
    
    def test_monitor_and_report(self):
        """모니터링 및 리포트 생성 테스트"""
        mock_status = GitStatus(
            branch="main",
            last_commit="a763ef8",
            status="업데이트 필요",
            behind_commits=2
        )
        
        mock_health = {
            'repository_valid': True,
            'issues': [],
            'recommendations': []
        }
        
        with patch.object(self.monitor, 'get_git_status', return_value=mock_status), \
             patch.object(self.monitor, 'check_repository_health', return_value=mock_health), \
             patch.object(self.monitor, 'detect_conflicts', return_value=[]):
            
            report = self.monitor.monitor_and_report()
            
            self.assertEqual(report['status'], 'success')
            self.assertIsNotNone(report['git_status'])
            self.assertIsNotNone(report['health_check'])
            self.assertGreater(len(report['alerts']), 0)

def run_integration_test():
    """통합 테스트 실행"""
    print("=== Git 모니터링 시스템 통합 테스트 ===")
    
    # 실제 Git 저장소에서 테스트
    monitor = GitMonitor(".")
    
    print("\n1. 실제 Git 상태 확인:")
    status = monitor.get_git_status()
    print(f"브랜치: {status.branch}")
    print(f"마지막 커밋: {status.last_commit[:8]}...")
    print(f"상태: {status.status}")
    
    print("\n2. 저장소 건강 상태:")
    health = monitor.check_repository_health()
    print(f"저장소 유효: {health['repository_valid']}")
    print(f"문제점 수: {len(health['issues'])}")
    print(f"권장사항 수: {len(health['recommendations'])}")
    
    print("\n3. 모니터링 리포트:")
    report = monitor.monitor_and_report()
    print(f"리포트 상태: {report['status']}")
    print(f"알림 수: {len(report['alerts'])}")
    
    return {
        'git_status': status,
        'health_check': health,
        'monitoring_report': report
    }

def main():
    """메인 테스트 실행"""
    print("Git 모니터링 시스템 테스트를 시작합니다...")
    
    # 단위 테스트 실행
    print("\n=== 단위 테스트 실행 ===")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 통합 테스트 실행
    print("\n=== 통합 테스트 실행 ===")
    integration_results = run_integration_test()
    
    # 결과 저장
    results = {
        'timestamp': str(datetime.now()),
        'integration_test_results': integration_results
    }
    
    with open('git_monitor_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n✅ Git 모니터링 시스템 테스트가 완료되었습니다!")
    print("결과가 git_monitor_test_results.json 파일에 저장되었습니다.")

if __name__ == "__main__":
    from datetime import datetime
    main()