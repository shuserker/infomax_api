#!/usr/bin/env python3
"""
POSCO 시스템 파일 참조 최종 정리 도구

남은 문제들을 해결:
1. 와일드카드 패턴 정확성 개선
2. 상대 경로 참조 정확성 향상
3. BROKEN_REF 주석 정리
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalReferenceCleanup:
    """파일 참조 최종 정리 클래스"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.backup_dir = Path(".final_reference_cleanup_backup")
        self.fixes_applied = 0

    def cleanup_all_references(self):
        """모든 참조 정리"""
        logger.info("파일 참조 최종 정리 시작...")
        
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        # 1. BROKEN_REF 주석 정리
        self._cleanup_broken_ref_comments()
        
        # 2. 와일드카드 패턴 정리
        self._fix_wildcard_patterns()
        
        # 3. 상대 경로 정리
        self._fix_relative_paths()
        
        logger.info(f"총 {self.fixes_applied}개 수정 완료")

    def _cleanup_broken_ref_comments(self):
        """BROKEN_REF 주석 정리"""
        logger.info("BROKEN_REF 주석 정리 중...")
        
        for py_file in self.root_path.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                modified = False
                new_lines = []
                
                for line in lines:
                    # BROKEN_REF 주석이 있는 라인 처리
" in line:
                        # 주석을 제거하고 원래 코드 복원 시도
                        original_line = line.replace("", "")
                        
                        # 유효한 Python 코드인지 간단히 확인
                        if self._is_valid_python_line(original_line.strip()):
                            new_lines.append(original_line)
                            modified = True
                            self.fixes_applied += 1
                        else:
                            # 유효하지 않으면 완전히 주석 처리
                            new_lines.append(f"# REMOVED: {original_line}")
                            modified = True
                    else:
                        new_lines.append(line)
                
                if modified:
                    self._backup_and_write_file(py_file, new_lines)
                    
            except Exception as e:
                logger.error(f"BROKEN_REF 정리 오류 {py_file}: {e}")

    def _fix_wildcard_patterns(self):
        """와일드카드 패턴 수정"""
        logger.info("와일드카드 패턴 수정 중...")
        
        for py_file in self.root_path.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # 일반적인 glob 패턴 수정
                patterns_to_fix = [
                    (r'/.rglob/([\'"]([^\'"]*/*[^\'"]*)[\'"]', self._fix_glob_pattern),
                    (r'/.glob/([\'"]([^\'"]*/*[^\'"]*)[\'"]', self._fix_glob_pattern),
                ]
                
                for pattern, fix_func in patterns_to_fix:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        old_pattern = match.group(1)
                        new_pattern = fix_func(old_pattern)
                        if new_pattern != old_pattern:
                            content = content.replace(f'"{old_pattern}"', f'"{new_pattern}"')
                            content = content.replace(f"'{old_pattern}'", f"'{new_pattern}'")
                            self.fixes_applied += 1
                
                if content != original_content:
                    self._backup_and_write_file(py_file, content)
                    
            except Exception as e:
                logger.error(f"와일드카드 패턴 수정 오류 {py_file}: {e}")

    def _fix_relative_paths(self):
        """상대 경로 수정"""
        logger.info("상대 경로 수정 중...")
        
        for py_file in self.root_path.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # 파일 경로 참조 찾기 및 수정
                file_patterns = [
                    r'[\'"]([^\'"/s]+/.(py|json|sh|bat|md|txt|log))[\'"]'
                ]
                
                for pattern in file_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        file_ref = match.group(1)
                        
                        # 존재하지 않는 파일 참조인 경우
                        if not self._file_exists(file_ref, py_file):
                            # 유사한 파일 찾기
                            similar_file = self._find_similar_file(file_ref)
                            if similar_file:
                                content = content.replace(f'"{file_ref}"', f'"{similar_file}"')
                                content = content.replace(f"'{file_ref}'", f"'{similar_file}'")
                                self.fixes_applied += 1
                
                if content != original_content:
                    self._backup_and_write_file(py_file, content)
                    
            except Exception as e:
                logger.error(f"상대 경로 수정 오류 {py_file}: {e}")

    def _is_valid_python_line(self, line: str) -> bool:
        """유효한 Python 라인인지 확인"""
        if not line or line.isspace():
            return False
        
        # 기본적인 Python 구문 패턴 확인
        valid_patterns = [
            r'^import/s+/w+',
            r'^from/s+/w+/s+import',
            r'^/w+/s*=',
            r'^def/s+/w+',
            r'^class/s+/w+',
            r'^if/s+',
            r'^for/s+',
            r'^while/s+',
            r'^try:',
            r'^except',
            r'^with/s+',
            r'^/s*#',  # 주석
            r'^/s*$'   # 빈 라인
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, line.strip()):
                return True
        
        return False

    def _fix_glob_pattern(self, pattern: str) -> str:
        """glob 패턴 수정"""
        # 일반적인 파일 확장자 패턴으로 수정
        if pattern == "*.py":
            return "*.py"
        elif pattern == "*.sh":
            return "*.sh"
        elif pattern == "*.bat":
            return "*.bat"
        elif pattern == "*.json":
            return "*.json"
        elif pattern == "*.md":
            return "*.md"
        elif pattern == "*.txt":
            return "*.txt"
        elif pattern == "*.log":
            return "*.log"
        else:
            # 복잡한 패턴은 단순화
            if "*" in pattern:
                ext = Path(pattern).suffix
                if ext:
                    return f"*{ext}"
        
        return pattern

    def _file_exists(self, file_ref: str, source_file: Path) -> bool:
        """파일이 존재하는지 확인"""
        # 절대 경로
        if os.path.isabs(file_ref):
            return Path(file_ref).exists()
        
        # 상대 경로 (소스 파일 기준)
        source_dir = source_file.parent
        relative_path = source_dir / file_ref
        if relative_path.exists():
            return True
        
        # 루트 기준 경로
        root_path = self.root_path / file_ref
        return root_path.exists()

    def _find_similar_file(self, file_ref: str) -> str:
        """유사한 파일 찾기"""
        filename = Path(file_ref).name
        
        # 정확한 파일명 매칭
        for existing_file in self.root_path.rglob("*"):
            if existing_file.is_file() and existing_file.name == filename:
                return str(existing_file.relative_to(self.root_path))
        
        # 유사한 파일명 찾기
        best_match = None
        best_score = 0
        
        for existing_file in self.root_path.rglob("*"):
            if existing_file.is_file():
                existing_name = existing_file.name.lower()
                filename_lower = filename.lower()
                
                # 유사도 계산
                if filename_lower in existing_name or existing_name in filename_lower:
                    score = len(set(filename_lower) & set(existing_name))
                    if score > best_score:
                        best_score = score
                        best_match = str(existing_file.relative_to(self.root_path))
        
        return best_match

    def _backup_and_write_file(self, file_path: Path, content):
        """파일 백업 후 쓰기"""
        try:
            # 백업 생성
            backup_path = self.backup_dir / f"{file_path.name}.backup_{self._get_timestamp()}"
            shutil.copy2(file_path, backup_path)
            
            # 파일 쓰기
            if isinstance(content, list):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(content)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
        except Exception as e:
            logger.error(f"파일 쓰기 오류 {file_path}: {e}")

    def _get_timestamp(self) -> str:
        """타임스탬프 생성"""
        from datetime import datetime
import datetime
import pathlib
        return datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    """메인 실행 함수"""
    print("🧹 POSCO 시스템 파일 참조 최종 정리 도구")
    print("=" * 50)
    
    cleanup = FinalReferenceCleanup()
    
    print("\n🔧 파일 참조 최종 정리 중...")
    cleanup.cleanup_all_references()
    
    print(f"\n✅ 최종 정리 완료!")
    print(f"   • 수정된 항목: {cleanup.fixes_applied}개")
    print(f"   • 백업 디렉토리: {cleanup.backup_dir}")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)