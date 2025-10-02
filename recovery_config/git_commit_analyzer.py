#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 커밋 분석 도구
정상 커밋과 현재 상태를 비교하여 핵심 로직 파일들을 식별하고 변경사항을 분석합니다.
"""

import os
import subprocess
import json
import logging
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
import re

class GitCommitAnalyzer:
    """Git 커밋 분석 및 파일 변경사항 추적 클래스"""
    
    def __init__(self, repo_path: str = "."):
        """
        Git 커밋 분석기 초기화
        
        Args:
            repo_path: Git 저장소 경로
        """
        self.repo_path = Path(repo_path).resolve()
        self.logger = self._setup_logger()
        
        # 정상 커밋 해시 (요구사항에서 명시된 정상 버전)
        self.target_commit = "a763ef84be08b5b1dab0c0ba20594b141baec7ab"
        
        # 핵심 로직 파일 패턴들
        self.core_logic_patterns = [
            r".*posco.*\.py$",
            r".*news.*\.py$", 
            r".*monitor.*\.py$",
            r".*webhook.*\.py$",
            r".*api.*\.py$",
            r".*infomax.*\.py$",
            r".*watchhamster.*\.py$",
            r".*\.bat$",
            r".*\.sh$",
            r".*\.command$"
        ]
        
        # 제외할 파일 패턴들
        self.exclude_patterns = [
            r".*\.backup.*",
            r".*backup.*",
            r".*\.log$",
            r".*__pycache__.*",
            r".*\.pyc$",
            r".*\.git.*",
            r".*test.*\.py$",
            r".*\.md$"
        ]
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger("GitCommitAnalyzer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def execute_git_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """
        Git 명령어를 안전하게 실행
        
        Args:
            command: 실행할 Git 명령어 리스트
            timeout: 타임아웃 시간 (초)
            
        Returns:
            (성공여부, stdout, stderr) 튜플
        """
        try:
            # 페이저 비활성화를 위한 환경 변수 설정
            env = os.environ.copy()
            env['GIT_PAGER'] = ''
            env['PAGER'] = ''
            
            # Git 명령어에 --no-pager 옵션 추가
            if command[0] == 'git' and '--no-pager' not in command:
                command.insert(1, '--no-pager')
            
            self.logger.info(f"Git 명령어 실행: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            success = result.returncode == 0
            if not success:
                self.logger.warning(f"Git 명령어 실행 실패: {result.stderr}")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Git 명령어 타임아웃: {' '.join(command)}")
            return False, "", "명령어 실행 타임아웃"
        except Exception as e:
            self.logger.error(f"Git 명령어 실행 오류: {e}")
            return False, "", str(e)
    
    def get_current_commit(self) -> Optional[str]:
        """현재 커밋 해시 가져오기"""
        success, stdout, stderr = self.execute_git_command(['git', 'rev-parse', 'HEAD'])
        if success:
            return stdout.strip()
        return None
    
    def get_commit_info(self, commit_hash: str) -> Optional[Dict]:
        """
        특정 커밋의 정보 가져오기
        
        Args:
            commit_hash: 커밋 해시
            
        Returns:
            커밋 정보 딕셔너리
        """
        success, stdout, stderr = self.execute_git_command([
            'git', 'log', '--format=%H|%an|%ae|%ad|%s', '-1', commit_hash
        ])
        
        if not success:
            return None
        
        try:
            parts = stdout.strip().split('|')
            return {
                'hash': parts[0],
                'author': parts[1],
                'email': parts[2],
                'date': parts[3],
                'message': parts[4]
            }
        except Exception as e:
            self.logger.error(f"커밋 정보 파싱 오류: {e}")
            return None
    
    def get_file_changes_between_commits(self, commit1: str, commit2: str) -> Dict[str, List[str]]:
        """
        두 커밋 간의 파일 변경사항 분석
        
        Args:
            commit1: 비교 기준 커밋 (정상 커밋)
            commit2: 비교 대상 커밋 (현재 커밋)
            
        Returns:
            변경사항 딕셔너리 {'added': [], 'modified': [], 'deleted': []}
        """
        success, stdout, stderr = self.execute_git_command([
            'git', 'diff', '--name-status', commit1, commit2
        ])
        
        changes = {'added': [], 'modified': [], 'deleted': []}
        
        if not success:
            self.logger.error(f"파일 변경사항 분석 실패: {stderr}")
            return changes
        
        for line in stdout.strip().split('\n'):
            if not line:
                continue
                
            parts = line.split('\t')
            if len(parts) < 2:
                continue
                
            status = parts[0]
            filename = parts[1]
            
            if status == 'A':
                changes['added'].append(filename)
            elif status == 'M':
                changes['modified'].append(filename)
            elif status == 'D':
                changes['deleted'].append(filename)
        
        return changes
    
    def identify_core_logic_files(self, file_list: List[str]) -> List[str]:
        """
        핵심 로직 파일들 자동 식별
        
        Args:
            file_list: 분석할 파일 목록
            
        Returns:
            핵심 로직 파일 목록
        """
        core_files = []
        
        for file_path in file_list:
            # 제외 패턴 확인
            if any(re.match(pattern, file_path, re.IGNORECASE) for pattern in self.exclude_patterns):
                continue
            
            # 핵심 로직 패턴 확인
            if any(re.match(pattern, file_path, re.IGNORECASE) for pattern in self.core_logic_patterns):
                core_files.append(file_path)
        
        return core_files
    
    def get_files_in_commit(self, commit_hash: str) -> List[str]:
        """
        특정 커밋의 파일 목록 가져오기
        
        Args:
            commit_hash: 커밋 해시
            
        Returns:
            파일 목록
        """
        success, stdout, stderr = self.execute_git_command([
            'git', 'ls-tree', '-r', '--name-only', commit_hash
        ])
        
        if not success:
            self.logger.error(f"커밋 파일 목록 가져오기 실패: {stderr}")
            return []
        
        return [line.strip() for line in stdout.strip().split('\n') if line.strip()]
    
    def analyze_target_commit(self) -> Dict:
        """
        정상 커밋 (a763ef84) 분석
        
        Returns:
            분석 결과 딕셔너리
        """
        self.logger.info(f"정상 커밋 {self.target_commit} 분석 시작")
        
        # 커밋 정보 가져오기
        commit_info = self.get_commit_info(self.target_commit)
        if not commit_info:
            return {'error': '정상 커밋 정보를 가져올 수 없습니다'}
        
        # 커밋의 파일 목록 가져오기
        files = self.get_files_in_commit(self.target_commit)
        if not files:
            return {'error': '정상 커밋의 파일 목록을 가져올 수 없습니다'}
        
        # 핵심 로직 파일 식별
        core_files = self.identify_core_logic_files(files)
        
        analysis_result = {
            'commit_info': commit_info,
            'total_files': len(files),
            'core_logic_files': core_files,
            'core_files_count': len(core_files),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"정상 커밋 분석 완료: 총 {len(files)}개 파일, 핵심 로직 {len(core_files)}개 파일")
        
        return analysis_result
    
    def compare_with_current(self) -> Dict:
        """
        정상 커밋과 현재 상태 비교 분석
        
        Returns:
            비교 분석 결과
        """
        self.logger.info("정상 커밋과 현재 상태 비교 분석 시작")
        
        # 현재 커밋 정보
        current_commit = self.get_current_commit()
        if not current_commit:
            return {'error': '현재 커밋 정보를 가져올 수 없습니다'}
        
        current_info = self.get_commit_info(current_commit)
        
        # 파일 변경사항 분석
        changes = self.get_file_changes_between_commits(self.target_commit, current_commit)
        
        # 현재 상태의 핵심 로직 파일들
        current_files = self.get_files_in_commit(current_commit)
        current_core_files = self.identify_core_logic_files(current_files)
        
        # 정상 커밋의 핵심 로직 파일들
        target_files = self.get_files_in_commit(self.target_commit)
        target_core_files = self.identify_core_logic_files(target_files)
        
        # 핵심 로직 파일 변경사항 분석
        core_changes = {
            'added_core_files': [f for f in changes['added'] if f in current_core_files],
            'modified_core_files': [f for f in changes['modified'] if f in current_core_files or f in target_core_files],
            'deleted_core_files': [f for f in changes['deleted'] if f in target_core_files]
        }
        
        comparison_result = {
            'target_commit': {
                'hash': self.target_commit,
                'total_files': len(target_files),
                'core_files': target_core_files,
                'core_files_count': len(target_core_files)
            },
            'current_commit': {
                'hash': current_commit,
                'info': current_info,
                'total_files': len(current_files),
                'core_files': current_core_files,
                'core_files_count': len(current_core_files)
            },
            'changes': changes,
            'core_logic_changes': core_changes,
            'file_count_difference': len(current_files) - len(target_files),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"비교 분석 완료: 파일 수 차이 {comparison_result['file_count_difference']}개")
        
        return comparison_result
    
    def save_analysis_report(self, analysis_data: Dict, output_file: str = "git_analysis_report.json"):
        """
        분석 결과를 파일로 저장
        
        Args:
            analysis_data: 분석 결과 데이터
            output_file: 출력 파일명
        """
        try:
            output_path = self.repo_path / "recovery_config" / output_file
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"분석 결과 저장 완료: {output_path}")
            
        except Exception as e:
            self.logger.error(f"분석 결과 저장 실패: {e}")
    
    def generate_recovery_plan(self, comparison_data: Dict) -> Dict:
        """
        비교 분석 결과를 바탕으로 복구 계획 생성
        
        Args:
            comparison_data: 비교 분석 결과
            
        Returns:
            복구 계획 딕셔너리
        """
        recovery_plan = {
            'priority_files': [],
            'files_to_restore': [],
            'files_to_remove': [],
            'recommendations': []
        }
        
        # 삭제된 핵심 파일들 - 최우선 복구 대상
        deleted_core = comparison_data['core_logic_changes']['deleted_core_files']
        if deleted_core:
            recovery_plan['priority_files'].extend(deleted_core)
            recovery_plan['recommendations'].append(
                f"삭제된 핵심 로직 파일 {len(deleted_core)}개를 정상 커밋에서 복원해야 합니다"
            )
        
        # 수정된 핵심 파일들 - 검토 및 복원 필요
        modified_core = comparison_data['core_logic_changes']['modified_core_files']
        if modified_core:
            recovery_plan['files_to_restore'].extend(modified_core)
            recovery_plan['recommendations'].append(
                f"수정된 핵심 로직 파일 {len(modified_core)}개를 정상 커밋 버전으로 복원 검토가 필요합니다"
            )
        
        # 과도한 파일 증가 - 정리 필요
        file_diff = comparison_data['file_count_difference']
        if file_diff > 1000:  # 1000개 이상 증가한 경우
            recovery_plan['recommendations'].append(
                f"파일 수가 {file_diff}개 증가했습니다. 불필요한 백업 파일들을 정리해야 합니다"
            )
        
        # 새로 추가된 파일들 중 불필요한 것들 식별
        added_files = comparison_data['changes']['added']
        unnecessary_files = [f for f in added_files if any(
            pattern in f.lower() for pattern in ['backup', 'repair', 'migration', '.log']
        )]
        
        if unnecessary_files:
            recovery_plan['files_to_remove'].extend(unnecessary_files)
            recovery_plan['recommendations'].append(
                f"불필요한 백업/로그 파일 {len(unnecessary_files)}개를 제거해야 합니다"
            )
        
        return recovery_plan


def main():
    """메인 실행 함수"""
    print("🔍 Git 커밋 분석 도구 시작")
    
    analyzer = GitCommitAnalyzer()
    
    # 1. 정상 커밋 분석
    print("\n📋 1단계: 정상 커밋 분석")
    target_analysis = analyzer.analyze_target_commit()
    
    if 'error' in target_analysis:
        print(f"❌ 오류: {target_analysis['error']}")
        return
    
    print(f"✅ 정상 커밋 분석 완료:")
    print(f"   - 총 파일 수: {target_analysis['total_files']}개")
    print(f"   - 핵심 로직 파일: {target_analysis['core_files_count']}개")
    
    # 2. 현재 상태와 비교
    print("\n🔄 2단계: 현재 상태와 비교 분석")
    comparison = analyzer.compare_with_current()
    
    if 'error' in comparison:
        print(f"❌ 오류: {comparison['error']}")
        return
    
    print(f"✅ 비교 분석 완료:")
    print(f"   - 현재 파일 수: {comparison['current_commit']['total_files']}개")
    print(f"   - 파일 수 차이: {comparison['file_count_difference']}개")
    print(f"   - 추가된 파일: {len(comparison['changes']['added'])}개")
    print(f"   - 수정된 파일: {len(comparison['changes']['modified'])}개")
    print(f"   - 삭제된 파일: {len(comparison['changes']['deleted'])}개")
    
    # 3. 복구 계획 생성
    print("\n📝 3단계: 복구 계획 생성")
    recovery_plan = analyzer.generate_recovery_plan(comparison)
    
    print("✅ 복구 계획 생성 완료:")
    for recommendation in recovery_plan['recommendations']:
        print(f"   - {recommendation}")
    
    # 4. 결과 저장
    print("\n💾 4단계: 분석 결과 저장")
    full_report = {
        'target_analysis': target_analysis,
        'comparison': comparison,
        'recovery_plan': recovery_plan
    }
    
    analyzer.save_analysis_report(full_report, "git_commit_analysis_report.json")
    print("✅ 분석 결과 저장 완료")
    
    print("\n🎉 Git 커밋 분석 도구 실행 완료!")


if __name__ == "__main__":
    main()