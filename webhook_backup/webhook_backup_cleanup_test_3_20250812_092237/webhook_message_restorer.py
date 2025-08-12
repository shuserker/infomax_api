#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 웹훅 메시지 복원 시스템
WebhookMessageRestorer 클래스 구현

Created: 2025-01-06
Updated: 2025-01-06
Author: POSCO 시스템 관리자

Requirements: 2.1, 2.2
- 원본 커밋에서 웹훅 관련 함수 자동 추출 기능 개발
- 현재 파일에서 웹훅 섹션 식별 로직 구현
"""

import os
import sys
import json
import shutil
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

class WebhookMessageRestorer:
    """
    웹훅 메시지 복원 전담 클래스
    
    원본 커밋(a763ef8)에서 웹훅 관련 함수들을 추출하여
    현재 파일의 손상된 웹훅 기능을 완전히 복원합니다.
    """
    
    def __init__(self, target_file_path: str, source_commit: str = "a763ef8"):
        """
        WebhookMessageRestorer 초기화
        
        Args:
            target_file_path (str): 복원 대상 파일 경로
            source_commit (str): 원본 커밋 해시
        """
        self.target_file = target_file_path
        self.source_commit = source_commit
        self.backup_created = False
        self.backup_path = None
        
        # 원본 커밋에서의 파일 경로 (다를 수 있음)
        self.source_file_path = "Monitoring/Posco_News_mini/monitor_WatchHamster.py"
        
        # 웹훅 관련 함수 목록 (Requirements 2.1, 2.2에 따라 확장)
        self.webhook_functions = [
            "send_status_notification",
            "send_notification", 
            "send_status_report_v2",
            "send_startup_notification_v2"
        ]
        
        # 웹훅 관련 상수 및 설정 목록
        self.webhook_constants = [
            "DOORAY_WEBHOOK_URL",
            "WATCHHAMSTER_WEBHOOK_URL", 
            "BOT_PROFILE_IMAGE_URL"
        ]
        
        # 추출된 함수 내용 저장
        self.extracted_functions = {}
        self.extracted_constants = {}
        
        # 웹훅 섹션 식별 결과 저장
        self.identified_sections = {}
        
        # 로그 파일 설정
        self.log_file = "webhook_restoration.log"
        
        # 복원 통계
        self.restoration_stats = {
            'functions_extracted': 0,
            'functions_restored': 0,
            'constants_extracted': 0,
            'constants_restored': 0,
            'errors': []
        }
        
        print(f"[INFO] WebhookMessageRestorer 초기화 완료")
        print(f"[INFO] 대상 파일: {self.target_file}")
        print(f"[INFO] 원본 커밋: {self.source_commit}")
        print(f"[INFO] 웹훅 함수 목록: {', '.join(self.webhook_functions)}")
        print(f"[INFO] 웹훅 상수 목록: {', '.join(self.webhook_constants)}")
    
    def log(self, message: str):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        print(log_message)
        
        # 로그 파일에 저장
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"[WARNING] 로그 파일 저장 실패: {e}")
    
    def create_backup(self) -> bool:
        """
        현재 파일 백업 생성
        
        Returns:
            bool: 백업 성공 여부
        """
        try:
            if not os.path.exists(self.target_file):
                self.log(f"[ERROR] 대상 파일이 존재하지 않습니다: {self.target_file}")
                return False
            
            # 백업 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{os.path.basename(self.target_file)}.backup_{timestamp}"
            backup_dir = os.path.join(os.path.dirname(self.target_file), ".webhook_restoration_backup")
            
            # 백업 디렉토리 생성
            os.makedirs(backup_dir, exist_ok=True)
            
            self.backup_path = os.path.join(backup_dir, backup_filename)
            
            # 파일 복사
            shutil.copy2(self.target_file, self.backup_path)
            
            self.backup_created = True
            self.log(f"[SUCCESS] 백업 파일 생성 완료: {self.backup_path}")
            
            return True
            
        except Exception as e:
            self.log(f"[ERROR] 백업 생성 실패: {e}")
            return False
    
    def extract_webhook_functions(self) -> bool:
        """
        원본 커밋에서 웹훅 관련 함수들 자동 추출
        Requirements: 2.1 - 원본 커밋에서 웹훅 관련 함수 자동 추출 기능 개발
        
        Returns:
            bool: 추출 성공 여부
        """
        try:
            self.log("[INFO] 원본 커밋에서 웹훅 함수 자동 추출 시작...")
            
            # Git을 통해 원본 파일 내용 가져오기
            cmd = f"git show {self.source_commit}:{self.source_file_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                self.log(f"[ERROR] Git 명령 실행 실패: {result.stderr}")
                # 대안 경로 시도
                alternative_paths = [
                    "monitor_WatchHamster.py",
                    "Monitoring/monitor_WatchHamster.py",
                    "core/monitoring/monitor_WatchHamster_v3.0.py"
                ]
                
                for alt_path in alternative_paths:
                    self.log(f"[INFO] 대안 경로 시도: {alt_path}")
                    cmd = f"git show {self.source_commit}:{alt_path}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
                    if result.returncode == 0:
                        self.source_file_path = alt_path
                        break
                else:
                    self.log("[ERROR] 모든 경로에서 원본 파일을 찾을 수 없습니다")
                    return False
            
            source_content = result.stdout
            self.log(f"[SUCCESS] 원본 파일 내용 추출 완료 ({len(source_content)} 문자)")
            
            # 웹훅 관련 함수들을 자동으로 식별하고 추출
            self._auto_identify_webhook_functions(source_content)
            
            # 각 웹훅 함수 추출
            for func_name in self.webhook_functions:
                extracted_func = self._extract_function_from_content(source_content, func_name)
                if extracted_func:
                    self.extracted_functions[func_name] = extracted_func
                    self.restoration_stats['functions_extracted'] += 1
                    self.log(f"[SUCCESS] {func_name} 함수 추출 완료 ({len(extracted_func.split(chr(10)))} 줄)")
                else:
                    self.log(f"[WARNING] {func_name} 함수를 찾을 수 없습니다")
                    self.restoration_stats['errors'].append(f"{func_name} 함수 추출 실패")
            
            # 웹훅 관련 상수들도 추출
            self._extract_webhook_constants(source_content)
            
            self.log(f"[INFO] 총 {len(self.extracted_functions)}개 함수, {len(self.extracted_constants)}개 상수 추출 완료")
            return len(self.extracted_functions) > 0
            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 함수 추출 실패: {e}")
            self.restoration_stats['errors'].append(f"함수 추출 실패: {str(e)}")
            return False
    
    def _auto_identify_webhook_functions(self, content: str) -> None:
        """
        소스 코드에서 웹훅 관련 함수들을 자동으로 식별
        Requirements: 2.1 - 웹훅 관련 함수 자동 추출 기능
        
        Args:
            content (str): 소스 코드 내용
        """
        try:
            self.log("[INFO] 웹훅 관련 함수 자동 식별 시작...")
            
            # 웹훅 관련 키워드 패턴
            webhook_patterns = [
                r'def\s+(\w*notification\w*)\s*\(',
                r'def\s+(\w*webhook\w*)\s*\(',
                r'def\s+(\w*dooray\w*)\s*\(',
                r'def\s+(send_\w+)\s*\(',
                r'def\s+(\w*status\w*notification\w*)\s*\('
            ]
            
            identified_functions = set()
            
            for pattern in webhook_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    func_name = match.group(1)
                    if func_name not in identified_functions:
                        identified_functions.add(func_name)
                        self.log(f"[FOUND] 웹훅 관련 함수 발견: {func_name}")
            
            # 기존 목록에 새로 발견된 함수들 추가
            for func_name in identified_functions:
                if func_name not in self.webhook_functions:
                    self.webhook_functions.append(func_name)
                    self.log(f"[ADDED] 웹훅 함수 목록에 추가: {func_name}")
            
            self.log(f"[INFO] 총 {len(identified_functions)}개 웹훅 관련 함수 자동 식별 완료")
            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 함수 자동 식별 실패: {e}")
    
    def _extract_webhook_constants(self, content: str) -> None:
        """
        웹훅 관련 상수들 추출
        Requirements: 2.2 - 웹훅 URL 및 설정 복원
        
        Args:
            content (str): 소스 코드 내용
        """
        try:
            self.log("[INFO] 웹훅 관련 상수 추출 시작...")
            
            for const_name in self.webhook_constants:
                # 상수 정의 패턴 찾기
                patterns = [
                    rf'{const_name}\s*=\s*["\']([^"\']+)["\']',
                    rf'{const_name}\s*=\s*([^#\n]+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        const_value = match.group(1).strip()
                        self.extracted_constants[const_name] = const_value
                        self.restoration_stats['constants_extracted'] += 1
                        self.log(f"[SUCCESS] {const_name} 상수 추출 완료")
                        break
                else:
                    self.log(f"[WARNING] {const_name} 상수를 찾을 수 없습니다")
            
            self.log(f"[INFO] 총 {len(self.extracted_constants)}개 상수 추출 완료")
            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 상수 추출 실패: {e}")
    
    def _extract_function_from_content(self, content: str, func_name: str) -> Optional[str]:
        """
        파일 내용에서 특정 함수 추출
        
        Args:
            content (str): 파일 내용
            func_name (str): 추출할 함수명
            
        Returns:
            Optional[str]: 추출된 함수 내용 (실패 시 None)
        """
        try:
            lines = content.split('\n')
            func_start = None
            func_lines = []
            indent_level = None
            
            # 함수 시작점 찾기
            for i, line in enumerate(lines):
                if f"def {func_name}(" in line:
                    func_start = i
                    indent_level = len(line) - len(line.lstrip())
                    func_lines.append(line)
                    break
            
            if func_start is None:
                return None
            
            # 함수 끝점 찾기 (들여쓰기 기준)
            for i in range(func_start + 1, len(lines)):
                line = lines[i]
                
                # 빈 줄은 포함
                if not line.strip():
                    func_lines.append(line)
                    continue
                
                # 현재 함수의 들여쓰기보다 작거나 같으면 함수 끝
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and line.strip():
                    break
                
                func_lines.append(line)
            
            return '\n'.join(func_lines)
            
        except Exception as e:
            self.log(f"[ERROR] {func_name} 함수 추출 중 오류: {e}")
            return None
    
    def identify_webhook_sections(self) -> Dict[str, Tuple[int, int]]:
        """
        현재 파일에서 웹훅 섹션 식별 로직 구현
        Requirements: 2.2 - 현재 파일에서 웹훅 섹션 식별 로직 구현
        
        Returns:
            Dict[str, Tuple[int, int]]: 함수명과 (시작줄, 끝줄) 매핑
        """
        try:
            self.log("[INFO] 현재 파일에서 웹훅 섹션 식별 시작...")
            
            if not os.path.exists(self.target_file):
                self.log(f"[ERROR] 대상 파일이 존재하지 않습니다: {self.target_file}")
                return {}
            
            with open(self.target_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            webhook_sections = {}
            
            # 웹훅 관련 함수들 식별
            for func_name in self.webhook_functions:
                section = self._find_function_section(lines, func_name)
                if section:
                    webhook_sections[func_name] = section
                    self.log(f"[SUCCESS] {func_name} 섹션 발견: 줄 {section[0]+1}-{section[1]+1}")
                else:
                    self.log(f"[WARNING] {func_name} 섹션을 찾을 수 없습니다")
            
            # 웹훅 관련 상수들도 식별
            self._identify_webhook_constants_in_file(lines)
            
            # 웹훅 관련 import 문들 식별
            self._identify_webhook_imports(lines)
            
            # 식별 결과 저장
            self.identified_sections = webhook_sections
            
            self.log(f"[INFO] 총 {len(webhook_sections)}개 웹훅 섹션 식별 완료")
            return webhook_sections
            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 섹션 식별 실패: {e}")
            self.restoration_stats['errors'].append(f"섹션 식별 실패: {str(e)}")
            return {}
    
    def _identify_webhook_constants_in_file(self, lines: List[str]) -> None:
        """
        현재 파일에서 웹훅 관련 상수들 식별
        
        Args:
            lines (List[str]): 파일 내용 (줄별)
        """
        try:
            self.log("[INFO] 현재 파일에서 웹훅 상수 식별 중...")
            
            for i, line in enumerate(lines):
                for const_name in self.webhook_constants:
                    if const_name in line and '=' in line:
                        self.log(f"[FOUND] {const_name} 상수 발견: 줄 {i+1}")
                        
        except Exception as e:
            self.log(f"[ERROR] 웹훅 상수 식별 실패: {e}")
    
    def _identify_webhook_imports(self, lines: List[str]) -> None:
        """
        웹훅 관련 import 문들 식별
        
        Args:
            lines (List[str]): 파일 내용 (줄별)
        """
        try:
            webhook_import_patterns = [
                'requests',
                'json',
                'dooray',
                'webhook'
            ]
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    for pattern in webhook_import_patterns:
                        if pattern in line.lower():
                            self.log(f"[FOUND] 웹훅 관련 import 발견: 줄 {i+1} - {line.strip()}")
                            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 import 식별 실패: {e}")
    
    def _find_function_section(self, lines: List[str], func_name: str) -> Optional[Tuple[int, int]]:
        """
        파일에서 특정 함수의 시작과 끝 줄 번호 찾기
        
        Args:
            lines (List[str]): 파일 내용 (줄별)
            func_name (str): 찾을 함수명
            
        Returns:
            Optional[Tuple[int, int]]: (시작줄, 끝줄) 또는 None
        """
        try:
            func_start = None
            indent_level = None
            
            # 함수 시작점 찾기
            for i, line in enumerate(lines):
                if f"def {func_name}(" in line:
                    func_start = i
                    indent_level = len(line) - len(line.lstrip())
                    break
            
            if func_start is None:
                return None
            
            # 함수 끝점 찾기
            func_end = len(lines) - 1  # 기본값: 파일 끝
            
            for i in range(func_start + 1, len(lines)):
                line = lines[i]
                
                # 빈 줄은 건너뛰기
                if not line.strip():
                    continue
                
                # 현재 함수의 들여쓰기보다 작거나 같으면 함수 끝
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level:
                    func_end = i - 1
                    break
            
            return (func_start, func_end)
            
        except Exception as e:
            self.log(f"[ERROR] {func_name} 섹션 찾기 실패: {e}")
            return None
    
    def restore_webhook_messages(self) -> bool:
        """
        웹훅 메시지들을 원본으로 완전 복원
        Requirements: 2.1, 2.2 - 웹훅 관련 함수 및 설정 복원
        
        Returns:
            bool: 복원 성공 여부
        """
        try:
            self.log("[INFO] 웹훅 메시지 완전 복원 시작...")
            
            if not self.extracted_functions:
                self.log("[ERROR] 추출된 함수가 없습니다. extract_webhook_functions()를 먼저 실행하세요.")
                return False
            
            # 현재 파일 읽기
            with open(self.target_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # 현재 웹훅 섹션 식별
            current_sections = self.identify_webhook_sections()
            
            # 복원 작업 수행
            restored_content = current_content
            
            # 1. 웹훅 함수들 복원
            restored_content = self._restore_webhook_functions(restored_content, current_sections)
            
            # 2. 웹훅 상수들 복원
            restored_content = self._restore_webhook_constants(restored_content)
            
            # 3. 메시지 포맷 정확성 검증
            self._verify_message_formats(restored_content)
            
            # 복원된 내용을 파일에 저장
            with open(self.target_file, 'w', encoding='utf-8') as f:
                f.write(restored_content)
            
            # 복원 통계 업데이트
            self.restoration_stats['functions_restored'] = len(self.extracted_functions)
            self.restoration_stats['constants_restored'] = len(self.extracted_constants)
            
            self.log(f"[SUCCESS] 웹훅 메시지 완전 복원 완료!")
            self.log(f"[STATS] 함수 {self.restoration_stats['functions_restored']}개, 상수 {self.restoration_stats['constants_restored']}개 복원")
            
            return True
            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 메시지 복원 실패: {e}")
            self.restoration_stats['errors'].append(f"복원 실패: {str(e)}")
            return False
    
    def _restore_webhook_functions(self, content: str, current_sections: Dict[str, Tuple[int, int]]) -> str:
        """
        웹훅 함수들을 원본으로 복원
        
        Args:
            content (str): 현재 파일 내용
            current_sections (Dict[str, Tuple[int, int]]): 현재 섹션 정보
            
        Returns:
            str: 함수가 복원된 파일 내용
        """
        try:
            restored_content = content
            
            for func_name, original_func in self.extracted_functions.items():
                if func_name in current_sections:
                    # 기존 함수 교체
                    restored_content = self._replace_function_in_content(
                        restored_content, func_name, original_func, current_sections[func_name]
                    )
                    self.log(f"[SUCCESS] {func_name} 함수 교체 완료")
                else:
                    # 새로운 함수 추가
                    restored_content = self._add_function_to_content(restored_content, func_name, original_func)
                    self.log(f"[SUCCESS] {func_name} 함수 추가 완료")
            
            return restored_content
            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 함수 복원 실패: {e}")
            return content
    
    def _restore_webhook_constants(self, content: str) -> str:
        """
        웹훅 관련 상수들을 원본으로 복원
        
        Args:
            content (str): 현재 파일 내용
            
        Returns:
            str: 상수가 복원된 파일 내용
        """
        try:
            restored_content = content
            
            for const_name, const_value in self.extracted_constants.items():
                # 상수가 이미 존재하는지 확인
                pattern = rf'{const_name}\s*=.*'
                if re.search(pattern, restored_content):
                    # 기존 상수 교체
                    new_line = f'{const_name} = "{const_value}"'
                    restored_content = re.sub(pattern, new_line, restored_content)
                    self.log(f"[SUCCESS] {const_name} 상수 교체 완료")
                else:
                    # 새로운 상수 추가 (import 섹션 뒤에)
                    import_end = self._find_import_section_end(restored_content)
                    if import_end:
                        lines = restored_content.split('\n')
                        new_line = f'{const_name} = "{const_value}"'
                        lines.insert(import_end + 1, new_line)
                        restored_content = '\n'.join(lines)
                        self.log(f"[SUCCESS] {const_name} 상수 추가 완료")
            
            return restored_content
            
        except Exception as e:
            self.log(f"[ERROR] 웹훅 상수 복원 실패: {e}")
            return content
    
    def _verify_message_formats(self, content: str) -> None:
        """
        복원된 메시지 포맷 정확성 검증
        
        Args:
            content (str): 복원된 파일 내용
        """
        try:
            self.log("[INFO] 메시지 포맷 정확성 검증 시작...")
            
            # 줄바꿈 문자 검증 (\n vs /n)
            if '/n' in content:
                self.log("[WARNING] 잘못된 줄바꿈 문자 '/n' 발견됨")
                self.restoration_stats['errors'].append("잘못된 줄바꿈 문자 발견")
            
            # POSCO 워치햄스터 제품명 검증
            product_names = ['POSCO 워치햄스터', 'POSCO WatchHamster', '워치햄스터']
            found_names = []
            for name in product_names:
                if name in content:
                    found_names.append(name)
            
            if found_names:
                self.log(f"[SUCCESS] 제품명 확인됨: {', '.join(found_names)}")
            else:
                self.log("[WARNING] 제품명을 찾을 수 없습니다")
                self.restoration_stats['errors'].append("제품명 누락")
            
            # 웹훅 URL 형식 검증
            webhook_url_pattern = r'https://[^/]+\.dooray\.com/services/\d+/\d+/[A-Za-z0-9_-]+'
            if re.search(webhook_url_pattern, content):
                self.log("[SUCCESS] 웹훅 URL 형식 확인됨")
            else:
                self.log("[WARNING] 올바른 웹훅 URL 형식을 찾을 수 없습니다")
            
            self.log("[INFO] 메시지 포맷 검증 완료")
            
        except Exception as e:
            self.log(f"[ERROR] 메시지 포맷 검증 실패: {e}")
    
    def _find_import_section_end(self, content: str) -> Optional[int]:
        """
        import 섹션의 끝 줄 번호 찾기
        
        Args:
            content (str): 파일 내용
            
        Returns:
            Optional[int]: import 섹션 끝 줄 번호
        """
        try:
            lines = content.split('\n')
            last_import_line = -1
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    last_import_line = i
            
            return last_import_line if last_import_line >= 0 else None
            
        except Exception as e:
            self.log(f"[ERROR] import 섹션 찾기 실패: {e}")
            return None
    
    def _replace_function_in_content(self, content: str, func_name: str, new_func: str, section: Tuple[int, int]) -> str:
        """
        파일 내용에서 특정 함수를 새로운 함수로 교체
        
        Args:
            content (str): 원본 파일 내용
            func_name (str): 교체할 함수명
            new_func (str): 새로운 함수 내용
            section (Tuple[int, int]): 교체할 섹션 (시작줄, 끝줄)
            
        Returns:
            str: 교체된 파일 내용
        """
        try:
            lines = content.split('\n')
            start_line, end_line = section
            
            # 기존 함수 제거하고 새 함수 삽입
            new_lines = lines[:start_line] + new_func.split('\n') + lines[end_line + 1:]
            
            return '\n'.join(new_lines)
            
        except Exception as e:
            self.log(f"[ERROR] {func_name} 함수 교체 실패: {e}")
            return content
    
    def _add_function_to_content(self, content: str, func_name: str, new_func: str) -> str:
        """
        파일 내용에 새로운 함수 추가
        
        Args:
            content (str): 원본 파일 내용
            func_name (str): 추가할 함수명
            new_func (str): 새로운 함수 내용
            
        Returns:
            str: 함수가 추가된 파일 내용
        """
        try:
            # 클래스 끝부분에 함수 추가 (간단한 구현)
            # 더 정교한 위치 찾기는 필요에 따라 개선 가능
            
            lines = content.split('\n')
            
            # 클래스 내부의 적절한 위치 찾기 (마지막 메서드 뒤)
            insert_position = len(lines)
            
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line.startswith('def ') and not line.startswith('def __'):
                    # 마지막 메서드 뒤에 삽입
                    insert_position = i + 1
                    # 메서드 끝까지 찾기
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith('    '):
                            insert_position = j
                            break
                    break
            
            # 새 함수 삽입
            new_lines = lines[:insert_position] + [''] + new_func.split('\n') + [''] + lines[insert_position:]
            
            return '\n'.join(new_lines)
            
        except Exception as e:
            self.log(f"[ERROR] {func_name} 함수 추가 실패: {e}")
            return content
    
    def generate_restoration_report(self) -> str:
        """
        상세한 복원 작업 보고서 생성
        Requirements: 4.3 - 복원된 내용과 손상된 버전 간의 상세 차이점 문서화
        
        Returns:
            str: 상세 보고서 내용
        """
        try:
            report_lines = [
                "=" * 80,
                "POSCO 워치햄스터 웹훅 메시지 복원 상세 보고서",
                "=" * 80,
                f"복원 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"대상 파일: {self.target_file}",
                f"원본 커밋: {self.source_commit}",
                f"원본 파일 경로: {self.source_file_path}",
                f"백업 파일: {self.backup_path if self.backup_created else '생성되지 않음'}",
                "",
                "📊 복원 통계:",
                "-" * 40,
                f"• 추출된 함수: {self.restoration_stats['functions_extracted']}개",
                f"• 복원된 함수: {self.restoration_stats['functions_restored']}개", 
                f"• 추출된 상수: {self.restoration_stats['constants_extracted']}개",
                f"• 복원된 상수: {self.restoration_stats['constants_restored']}개",
                f"• 발생한 오류: {len(self.restoration_stats['errors'])}개",
                ""
            ]
            
            # 복원된 함수 상세 정보
            if self.extracted_functions:
                report_lines.extend([
                    "🔧 복원된 웹훅 함수 목록:",
                    "-" * 40
                ])
                
                for i, (func_name, func_content) in enumerate(self.extracted_functions.items(), 1):
                    lines_count = len(func_content.split('\n'))
                    first_line = func_content.split('\n')[0].strip()
                    
                    report_lines.extend([
                        f"{i}. {func_name}",
                        f"   • 함수 길이: {lines_count} 줄",
                        f"   • 함수 정의: {first_line}",
                        f"   • 복원 상태: {'✅ 성공' if func_name in self.identified_sections else '🆕 신규 추가'}",
                        ""
                    ])
            
            # 복원된 상수 정보
            if self.extracted_constants:
                report_lines.extend([
                    "⚙️ 복원된 웹훅 상수 목록:",
                    "-" * 40
                ])
                
                for const_name, const_value in self.extracted_constants.items():
                    # 민감한 정보 마스킹
                    masked_value = const_value[:20] + "..." if len(const_value) > 20 else const_value
                    report_lines.extend([
                        f"• {const_name}: {masked_value}",
                        ""
                    ])
            
            # 오류 및 경고 사항
            if self.restoration_stats['errors']:
                report_lines.extend([
                    "⚠️ 발생한 오류 및 경고:",
                    "-" * 40
                ])
                
                for i, error in enumerate(self.restoration_stats['errors'], 1):
                    report_lines.append(f"{i}. {error}")
                
                report_lines.append("")
            
            # 복원 작업 요약
            report_lines.extend([
                "📋 복원 작업 요약:",
                "-" * 40,
                f"• 대상 파일: {os.path.basename(self.target_file)}",
                f"• 원본 커밋: {self.source_commit}",
                f"• 백업 생성: {'✅ 성공' if self.backup_created else '❌ 실패'}",
                f"• 전체 성공률: {self._calculate_success_rate():.1f}%",
                "",
                "🔍 검증 권장사항:",
                "-" * 40,
                "1. 복원 후 시스템 테스트 수행",
                "2. 웹훅 메시지 전송 테스트",
                "3. Dooray 알림 수신 확인",
                "4. 줄바꿈 문자(\\n) 정확성 확인",
                "5. POSCO 워치햄스터 제품명 표시 확인",
                "",
                "🚨 문제 발생 시 대응방안:",
                "-" * 40,
                f"• 백업 파일로 롤백: {self.backup_path}",
                "• 수동 검토 및 수정 필요",
                "• 원본 커밋과 비교 분석",
                "",
                "=" * 80
            ])
            
            return '\n'.join(report_lines)
            
        except Exception as e:
            return f"상세 보고서 생성 실패: {e}"
    
    def _calculate_success_rate(self) -> float:
        """
        복원 작업 성공률 계산
        
        Returns:
            float: 성공률 (0-100)
        """
        try:
            total_items = (len(self.webhook_functions) + len(self.webhook_constants))
            if total_items == 0:
                return 0.0
            
            successful_items = (self.restoration_stats['functions_restored'] + 
                              self.restoration_stats['constants_restored'])
            
            return (successful_items / total_items) * 100
            
        except Exception:
            return 0.0


    def get_restoration_statistics(self) -> Dict:
        """
        복원 작업 통계 정보 반환
        
        Returns:
            Dict: 복원 통계 정보
        """
        return {
            'functions_extracted': self.restoration_stats['functions_extracted'],
            'functions_restored': self.restoration_stats['functions_restored'],
            'constants_extracted': self.restoration_stats['constants_extracted'],
            'constants_restored': self.restoration_stats['constants_restored'],
            'errors_count': len(self.restoration_stats['errors']),
            'success_rate': self._calculate_success_rate(),
            'backup_created': self.backup_created,
            'backup_path': self.backup_path
        }


def main():
    """
    메인 실행 함수 - 웹훅 메시지 복원 도구 구현
    Requirements: 2.1, 2.2 완전 구현
    """
    print("🐹 POSCO 워치햄스터 웹훅 메시지 복원 시스템 v2.0")
    print("=" * 60)
    print("Requirements: 2.1, 2.2 - 웹훅 관련 함수 자동 추출 및 섹션 식별")
    print("=" * 60)
    
    # 대상 파일 경로
    target_file = "core/monitoring/monitor_WatchHamster_v3.0.py"
    
    if not os.path.exists(target_file):
        print(f"❌ [ERROR] 대상 파일을 찾을 수 없습니다: {target_file}")
        return False
    
    # 복원 시스템 초기화
    print(f"\n🔧 복원 시스템 초기화 중...")
    restorer = WebhookMessageRestorer(target_file)
    
    try:
        # 1. 백업 생성
        print("\n📦 1단계: 현재 파일 백업 생성...")
        if not restorer.create_backup():
            print("❌ [ERROR] 백업 생성 실패")
            return False
        print("✅ 백업 생성 완료")
        
        # 2. 원본 함수 자동 추출 (Requirements 2.1)
        print("\n🔍 2단계: 원본 커밋에서 웹훅 함수 자동 추출...")
        if not restorer.extract_webhook_functions():
            print("❌ [ERROR] 웹훅 함수 추출 실패")
            return False
        print(f"✅ 웹훅 함수 추출 완료 ({restorer.restoration_stats['functions_extracted']}개)")
        
        # 3. 현재 파일 웹훅 섹션 식별 (Requirements 2.2)
        print("\n🎯 3단계: 현재 파일에서 웹훅 섹션 식별...")
        sections = restorer.identify_webhook_sections()
        print(f"✅ 웹훅 섹션 식별 완료 ({len(sections)}개)")
        
        # 4. 웹훅 메시지 완전 복원
        print("\n🔧 4단계: 웹훅 메시지 완전 복원 수행...")
        if not restorer.restore_webhook_messages():
            print("❌ [ERROR] 웹훅 메시지 복원 실패")
            return False
        print("✅ 웹훅 메시지 복원 완료")
        
        # 5. 상세 복원 보고서 생성
        print("\n📊 5단계: 상세 복원 보고서 생성...")
        report = restorer.generate_restoration_report()
        
        # 보고서 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"webhook_restoration_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 복원 통계 출력
        stats = restorer.get_restoration_statistics()
        
        print("\n" + "=" * 60)
        print("🎉 웹훅 메시지 복원 작업 완료!")
        print("=" * 60)
        print(f"📈 복원 통계:")
        print(f"   • 추출된 함수: {stats['functions_extracted']}개")
        print(f"   • 복원된 함수: {stats['functions_restored']}개")
        print(f"   • 추출된 상수: {stats['constants_extracted']}개")
        print(f"   • 복원된 상수: {stats['constants_restored']}개")
        print(f"   • 성공률: {stats['success_rate']:.1f}%")
        print(f"   • 오류 수: {stats['errors_count']}개")
        print(f"\n📁 생성된 파일:")
        print(f"   • 복원 보고서: {report_file}")
        print(f"   • 로그 파일: {restorer.log_file}")
        print(f"   • 백업 파일: {stats['backup_path']}")
        
        if stats['errors_count'] > 0:
            print(f"\n⚠️ 주의: {stats['errors_count']}개의 오류가 발생했습니다. 보고서를 확인하세요.")
        
        print("\n🔍 다음 단계:")
        print("   1. 복원된 파일의 웹훅 기능 테스트")
        print("   2. Dooray 알림 전송 확인")
        print("   3. 메시지 포맷 정확성 검증")
        
        return True
        
    except Exception as e:
        print(f"\n❌ [CRITICAL ERROR] 복원 작업 중 예외 발생: {e}")
        print(f"🔄 백업 파일로 롤백하세요: {restorer.backup_path}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)