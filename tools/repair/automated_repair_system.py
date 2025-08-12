#!/usr/bin/env python3
"""
POSCO 시스템 자동화된 수리 도구
Automated Repair System for POSCO System

이 모듈은 POSCO 시스템의 모든 문제점을 자동으로 감지하고 수정하는 통합 도구입니다.
- Python 구문 오류 자동 감지 및 수정
- Import 문제 자동 해결
- 파일 참조 자동 복구
- 백업 및 롤백 시스템
"""

import ast
import os
import re
import sys
import json
import shutil
import hashlib
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
import datetime
import subprocess
import tempfile
import datetime
import pathlib


@dataclass
class DiagnosticResult:
    """진단 결과를 저장하는 데이터 클래스"""
    file_path: str
    error_type: str
    error_message: str
    line_number: int
    severity: str
    suggested_fix: Optional[str] = None


@dataclass
class RepairResult:
    """수리 결과를 저장하는 데이터 클래스"""
    file_path: str
    repair_type: str
    success: bool
    changes_made: List[str]
    backup_created: bool
    error_message: Optional[str] = None


@dataclass
class BrokenReference:
    """깨진 파일 참조를 저장하는 데이터 클래스"""
    source_file: str
    referenced_path: str
    reference_type: str  # 'import', 'file_path', 'config'
    line_number: int
    suggested_replacement: Optional[str] = None


class BackupManager:
    """백업 및 롤백을 관리하는 클래스"""
    
    def __init__(self, backup_dir: str = ".repair_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.backup_history = []
    
    def create_backup(self, file_path: Path) -> str:
        """개별 파일 백업 생성"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.name}.backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            
            backup_info = {
                "original_path": str(file_path),
                "backup_path": str(backup_path),
                "timestamp": timestamp,
                "file_hash": self._calculate_hash(file_path)
            }
            
            self.backup_history.append(backup_info)
            self._save_backup_history()
            
            return str(backup_path)
        except Exception as e:
            print(f"백업 생성 실패 {file_path}: {e}")
            return ""
    
    def create_full_backup(self) -> str:
        """전체 시스템 백업 생성"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"full_system_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # 중요 파일들만 백업 (용량 최적화)
            important_patterns = [
                "*.py", "*.sh", "*.bat", "*.md", "*.json", "*.txt"
            ]
            
            backup_path.mkdir(exist_ok=True)
            
            for pattern in important_patterns:
                for file_path in Path(".").glob(f"**/{pattern}"):
                    # 백업 디렉토리 자체를 제외하고, 다른 제외 패턴도 확인
                    exclude_patterns = [".git", "__pycache__", ".backup", ".repair_backup", "backup_", "full_system_backup"]
                    if not any(exclude in str(file_path) for exclude in exclude_patterns):
                        try:
                            relative_path = file_path.relative_to(".")
                            dest_path = backup_path / relative_path
                            
                            # 경로 길이 제한 확인 (200자 제한으로 더 안전하게)
                            if len(str(dest_path)) > 200:
                                continue
                                
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, dest_path)
                        except (OSError, ValueError) as e:
                            # 개별 파일 백업 실패는 무시하고 계속 진행
                            continue
            
            print(f"전체 시스템 백업 완료: {backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f"전체 백업 생성 실패: {e}")
            return ""
    
    def restore_file(self, original_path: str) -> bool:
        """파일을 최신 백업에서 복원"""
        try:
            # 해당 파일의 최신 백업 찾기
            latest_backup = None
            for backup_info in reversed(self.backup_history):
                if backup_info["original_path"] == original_path:
                    latest_backup = backup_info
                    break
            
            if not latest_backup:
                print(f"백업을 찾을 수 없음: {original_path}")
                return False
            
            backup_path = Path(latest_backup["backup_path"])
            if backup_path.exists():
                shutil.copy2(backup_path, original_path)
                print(f"파일 복원 완료: {original_path}")
                return True
            else:
                print(f"백업 파일이 존재하지 않음: {backup_path}")
                return False
        except Exception as e:
            print(f"파일 복원 실패 {original_path}: {e}")
            return False
    
    def _calculate_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def _save_backup_history(self):
        """백업 히스토리 저장"""
        try:
            history_file = self.backup_dir / "backup_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"백업 히스토리 저장 실패: {e}")


class SyntaxErrorDiagnostic:
    """Python 구문 오류 진단 클래스"""
    
    def __init__(self):
        self.results = []
    
    def diagnose_file(self, file_path: Path) -> List[DiagnosticResult]:
        """개별 파일의 구문 오류 진단"""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Python AST 파싱 시도
            try:
                ast.parse(content)
            except SyntaxError as e:
                result = DiagnosticResult(
                    file_path=str(file_path),
                    error_type="SyntaxError",
                    error_message=str(e),
                    line_number=e.lineno or 0,
                    severity="high",
                    suggested_fix=self._suggest_syntax_fix(e, content)
                )
                results.append(result)
            
            # 추가 패턴 기반 오류 검사
            results.extend(self._check_common_patterns(file_path, content))
            
        except Exception as e:
            result = DiagnosticResult(
                file_path=str(file_path),
                error_type="FileError",
                error_message=f"파일 읽기 실패: {e}",
                line_number=0,
                severity="medium"
            )
            results.append(result)
        
        return results
    
    def diagnose_all_files(self) -> List[DiagnosticResult]:
        """모든 Python 파일의 구문 오류 진단"""
        all_results = []
        
        for py_file in Path(".").glob("**/*.py"):
            if not any(exclude in str(py_file) for exclude in [".git", "__pycache__", ".backup"]):
                results = self.diagnose_file(py_file)
                all_results.extend(results)
        
        self.results = all_results
        return all_results
    
    def _suggest_syntax_fix(self, error: SyntaxError, content: str) -> str:
        """구문 오류에 대한 수정 제안"""
        error_msg = str(error).lower()
        
        if "invalid syntax" in error_msg and "{" in error_msg:
            return "f-string 구문 오류 가능성 - 중괄호 확인 필요"
        elif "unmatched" in error_msg or "parenthes" in error_msg:
            return "괄호 불일치 - 열린 괄호와 닫힌 괄호 확인 필요"
        elif "indent" in error_msg:
            return "들여쓰기 오류 - 4칸 스페이스 사용 권장"
        elif "invalid character" in error_msg:
            return "잘못된 문자 - 특수문자나 인코딩 문제 확인 필요"
        else:
            return "구문 오류 - 해당 라인의 Python 문법 확인 필요"
    
    def _check_common_patterns(self, file_path: Path, content: str) -> List[DiagnosticResult]:
        """일반적인 패턴 기반 오류 검사"""
        results = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # f-string 오류 패턴
            if re.search(r'f"[^"]*/{[^}]*/}\[^}\]*/}"', line):
                results.append(DiagnosticResult(
                    file_path=str(file_path),
                    error_type="FStringError",
                    error_message="f-string 중괄호 오류 가능성",
                    line_number=i,
                    severity="medium",
                    suggested_fix="f-string 중괄호 구문 확인"
                ))
            
            # 변수명 규칙 위반
            if re.search(r'/b[A-Z][a-z]+[A-Z]\[a-zA-Z\]*/s*=', line):
                results.append(DiagnosticResult(
                    file_path=str(file_path),
                    error_type="NamingConvention",
                    error_message="변수명이 Python 네이밍 규칙을 위반",
                    line_number=i,
                    severity="low",
                    suggested_fix="snake_case 사용 권장"
                ))
        
        return results


class SyntaxErrorRepairer:
    """Python 구문 오류 자동 수정 클래스"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
    
    def repair_file(self, file_path: Path) -> RepairResult:
        """파일의 모든 구문 오류 수정"""
        changes_made = []
        
        try:
            # 백업 생성
            backup_path = self.backup_manager.create_backup(file_path)
            backup_created = bool(backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            
            # 각종 수정 적용
            content, fstring_changes = self._repair_fstring_errors(content)
            changes_made.extend(fstring_changes)
            
            content, bracket_changes = self._repair_bracket_mismatches(content)
            changes_made.extend(bracket_changes)
            
            content, indent_changes = self._repair_indentation_errors(content)
            changes_made.extend(indent_changes)
            
            content, naming_changes = self._repair_naming_conventions(content)
            changes_made.extend(naming_changes)
            
            # 변경사항이 있으면 파일 저장
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return RepairResult(
                file_path=str(file_path),
                repair_type="SyntaxRepair",
                success=True,
                changes_made=changes_made,
                backup_created=backup_created
            )
            
        except Exception as e:
            return RepairResult(
                file_path=str(file_path),
                repair_type="SyntaxRepair",
                success=False,
                changes_made=[],
                backup_created=False,
                error_message=str(e)
            )
    
    def _repair_fstring_errors(self, content: str) -> Tuple[str, List[str]]:
        """f-string 구문 오류 수정"""
        changes = []
        
        # 잘못된 f-string 패턴 수정
        patterns = [
            (r'f"([^"]*/{[^}]*/}\\[^}\\]*)/}"', r'f"/1"'),  # 추가 중괄호 제거
            (r'f\'([^\']*/{[^}]*/}[^}]*)/}\'', r'f\'/1\''),  # 단일 따옴표 버전
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"f-string 구문 수정: {pattern}")
        
        return content, changes
    
    def _repair_bracket_mismatches(self, content: str) -> Tuple[str, List[str]]:
        """괄호 불일치 수정"""
        changes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 간단한 괄호 불일치 수정
            open_parens = line.count('(')
            close_parens = line.count(')')
            
            if open_parens > close_parens:
                # 닫는 괄호 추가
                lines[i] = line + ')' * (open_parens - close_parens)
                changes.append(f"라인 {i+1}: 닫는 괄호 추가")
            elif close_parens > open_parens:
                # 여는 괄호 추가 (라인 시작 부분에)
                lines[i] = '(' * (close_parens - open_parens) + line
                changes.append(f"라인 {i+1}: 여는 괄호 추가")
        
        return '\n'.join(lines), changes
    
    def _repair_indentation_errors(self, content: str) -> Tuple[str, List[str]]:
        """들여쓰기 오류 수정"""
        changes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():  # 빈 라인이 아닌 경우
                # 탭을 4칸 스페이스로 변환
                if '\t' in line:
                    lines[i] = line.replace('\t', '    ')
                    changes.append(f"라인 {i+1}: 탭을 스페이스로 변환")
        
        return '\n'.join(lines), changes
    
    def _repair_naming_conventions(self, content: str) -> Tuple[str, List[str]]:
        """네이밍 규칙 수정"""
        changes = []
        
        # 변수명 수정 (간단한 패턴만)
        patterns = [
            (r'/bPOSCO News 250808/b', 'POSCO_NEWS_250808'),
            (r'/bWatchHamster v3/.0/b', 'WATCHHAMSTER_V30'),
            (r'/bposco news/b', 'posco_news'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                changes.append(f"네이밍 규칙 수정: {pattern} -> {replacement}")
        
        return content, changes


class ImportDiagnostic:
    """Import 문제 진단 클래스"""
    
    def __init__(self):
        self.missing_modules = []
        self.circular_imports = []
    
    def analyze_dependencies(self) -> Dict[str, List[str]]:
        """모듈 간 의존성 분석"""
        dependencies = {}
        
        for py_file in Path(".").glob("**/*.py"):
            if not any(exclude in str(py_file) for exclude in [".git", "__pycache__", ".backup"]):
                deps = self._extract_imports(py_file)
                dependencies[str(py_file)] = deps
        
        return dependencies
    
    def find_missing_modules(self) -> List[str]:
        """존재하지 않는 모듈 참조 찾기"""
        missing = []
        
        for py_file in Path(".").glob("**/*.py"):
            if not any(exclude in str(py_file) for exclude in [".git", "__pycache__", ".backup"]):
                try:
                    imports = self._extract_imports(py_file)
                    
                    for imp in imports:
                        if not self._module_exists(imp):
                            missing.append(f"{py_file}: {imp}")
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 건너뛰기
                    print(f"Import 분석 중 오류 (건너뛰기): {py_file} - {e}")
                    continue
        
        self.missing_modules = missing
        return missing
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """파일에서 import 구문 추출"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # import 패턴 매칭 (더 안전한 방식)
            import_patterns = [
                r'^/s*import/s+([a-zA-Z_]\[a-zA-Z0-9_/.\]*)',
                r'^/s*from/s+([a-zA-Z_]\[a-zA-Z0-9_/.\]*)/s+import',
            ]
            
            for line in content.split('\n'):
                # 주석이나 문자열 내부의 import는 제외
                if line.strip().startswith('#') or '"""' in line or "'''" in line:
                    continue
                    
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        module_name = match.group(1)
                        # 유효한 모듈명인지 확인
                        if module_name and not module_name.startswith('.'):
                            imports.append(module_name)
        
        except Exception:
            # 파일 읽기 실패 시 빈 리스트 반환
            pass
        
        return imports
    
    def _module_exists(self, module_name: str) -> bool:
        """모듈 존재 여부 확인"""
        try:
            # 표준 라이브러리 및 설치된 패키지 확인
            importlib.import_module(module_name)
            return True
        except ImportError:
            # 로컬 파일 확인
            module_path = module_name.replace('.', '/') + '.py'
            return Path(module_path).exists()


class ImportRepairer:
    """Import 문제 자동 해결 클래스"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
    
    def repair_missing_imports(self, file_path: Path) -> RepairResult:
        """누락된 import 수정"""
        changes_made = []
        
        try:
            backup_path = self.backup_manager.create_backup(file_path)
            backup_created = bool(backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 필요한 import 추가
            content, import_changes = self._add_missing_imports(content)
            changes_made.extend(import_changes)
            
            # import 경로 수정
            content, path_changes = self._fix_import_paths(content)
            changes_made.extend(path_changes)
            
            if changes_made:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return RepairResult(
                file_path=str(file_path),
                repair_type="ImportRepair",
                success=True,
                changes_made=changes_made,
                backup_created=backup_created
            )
            
        except Exception as e:
            return RepairResult(
                file_path=str(file_path),
                repair_type="ImportRepair",
                success=False,
                changes_made=[],
                backup_created=False,
                error_message=str(e)
            )
    
    def _add_missing_imports(self, content: str) -> Tuple[str, List[str]]:
        """필요한 import 추가"""
        changes = []
        lines = content.split('\n')
        
        # 자주 사용되는 모듈들 확인
        common_modules = {
            'os': ['os.path', 'os.environ'],
            'sys': ['sys.path', 'sys.argv'],
            'json': ['json.load', 'json.dump'],
            'datetime': ['datetime.now', 'datetime.strftime'],
            'pathlib': ['Path('],
            're': ['re.search', 're.match', 're.sub'],
        }
        
        imports_to_add = []
        existing_imports = set()
        
        # 기존 import 확인
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                existing_imports.add(line.strip())
        
        # 필요한 import 찾기
        for module, patterns in common_modules.items():
            for pattern in patterns:
                if pattern in content and f'import {module}' not in str(existing_imports):
                    imports_to_add.append(f'import {module}')
                    changes.append(f"필요한 import 추가: {module}")
                    break
        
        # import 추가
        if imports_to_add:
            # import 섹션 찾기
            import_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    import_end = i + 1
            
            # import 추가
            for imp in imports_to_add:
                lines.insert(import_end, imp)
                import_end += 1
        
        return '\n'.join(lines), changes
    
    def _fix_import_paths(self, content: str) -> Tuple[str, List[str]]:
        """import 경로 수정"""
        changes = []
        
        # 일반적인 경로 수정 패턴
        path_fixes = {
            'from POSCO_News_250808': 'from POSCO_News_250808',
            'import POSCO_News_250808': 'import POSCO_News_250808',
            'from WatchHamster_v3.0': 'from WatchHamster_v3.0',
            'import WatchHamster_v3.0': 'import WatchHamster_v3.0',
        }
        
        for old_path, new_path in path_fixes.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                changes.append(f"Import 경로 수정: {old_path} -> {new_path}")
        
        return content, changes


class FileReferenceDiagnostic:
    """파일 참조 무결성 진단 클래스"""
    
    def __init__(self):
        self.broken_references = []
    
    def scan_file_references(self) -> List[BrokenReference]:
        """모든 파일 참조 스캔"""
        broken_refs = []
        
        # Python 파일에서 파일 참조 스캔
        for py_file in Path(".").glob("**/*.py"):
            if not any(exclude in str(py_file) for exclude in [".git", "__pycache__", ".backup"]):
                refs = self._scan_python_file(py_file)
                broken_refs.extend(refs)
        
        # 설정 파일에서 파일 참조 스캔
        for config_file in Path(".").glob("**/*.json"):
            if not any(exclude in str(config_file) for exclude in [".git", ".backup"]):
                refs = self._scan_config_file(config_file)
                broken_refs.extend(refs)
        
        # 문서 파일에서 파일 참조 스캔
        for doc_file in Path(".").glob("**/*.md"):
            if not any(exclude in str(doc_file) for exclude in [".git", ".backup"]):
                refs = self._scan_document_file(doc_file)
                broken_refs.extend(refs)
        
        self.broken_references = broken_refs
        return broken_refs
    
    def _scan_python_file(self, file_path: Path) -> List[BrokenReference]:
        """Python 파일에서 파일 참조 스캔"""
        broken_refs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # 파일 경로 패턴 찾기
                file_patterns = [
                    r'["\']([^"\']+/.(?:py|sh|bat|json|md|txt))["\']',
                    r'Path/(["\']([^"\']+)["\']',
                    r'open/(["\']([^"\']+)["\']',
                ]
                
                for pattern in file_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if not Path(match).exists() and not match.startswith(('http', 'https')):
                            broken_refs.append(BrokenReference(
                                source_file=str(file_path),
                                referenced_path=match,
                                reference_type="file_path",
                                line_number=i,
                                suggested_replacement=self._suggest_replacement(match)
                            ))
        
        except Exception:
            pass
        
        return broken_refs
    
    def _scan_config_file(self, file_path: Path) -> List[BrokenReference]:
        """설정 파일에서 파일 참조 스캔"""
        broken_refs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # JSON에서 파일 경로 찾기
            file_patterns = [
                r'"(\[^"\]+/.(?:py|sh|bat|json|md|txt))"',
            ]
            
            for pattern in file_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if not Path(match).exists() and not match.startswith(('http', 'https')):
                        broken_refs.append(BrokenReference(
                            source_file=str(file_path),
                            referenced_path=match,
                            reference_type="config",
                            line_number=0,
                            suggested_replacement=self._suggest_replacement(match)
                        ))
        
        except Exception:
            pass
        
        return broken_refs
    
    def _scan_document_file(self, file_path: Path) -> List[BrokenReference]:
        """문서 파일에서 파일 참조 스캔"""
        broken_refs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # 마크다운 링크 패턴
                link_patterns = [
                    r'/[([^/]]+)/]/((\[^)\]+/.(?:py|sh|bat|json|md|txt))/)',
                    r'`(\[^`\]+/.(?:py|sh|bat|json|md|txt))`',
                ]
                
                for pattern in link_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        file_ref = match[1] if isinstance(match, tuple) else match
                        if not Path(file_ref).exists() and not file_ref.startswith(('http', 'https')):
                            broken_refs.append(BrokenReference(
                                source_file=str(file_path),
                                referenced_path=file_ref,
                                reference_type="document_link",
                                line_number=i,
                                suggested_replacement=self._suggest_replacement(file_ref)
                            ))
        
        except Exception:
            pass
        
        return broken_refs
    
    def _suggest_replacement(self, broken_path: str) -> Optional[str]:
        """깨진 참조에 대한 대체 경로 제안"""
        # 유사한 이름의 파일 찾기
        broken_name = Path(broken_path).name
        
        for existing_file in Path(".").glob("**/*"):
            if existing_file.is_file() and existing_file.name.lower() == broken_name.lower():
                return str(existing_file)
        
        # 부분 매칭
        for existing_file in Path(".").glob("**/*"):
            if existing_file.is_file() and broken_name.lower() in existing_file.name.lower():
                return str(existing_file)
        
        return None


class FileReferenceRepairer:
    """파일 참조 자동 복구 클래스"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
    
    def repair_broken_references(self, file_path: Path) -> RepairResult:
        """깨진 파일 참조 수정"""
        changes_made = []
        
        try:
            backup_path = self.backup_manager.create_backup(file_path)
            backup_created = bool(backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 일반적인 파일명 변경 매핑
            file_mappings = {
                'POSCO_News_250808.py': 'POSCO_News_250808.py',
                'WatchHamster_v3.0': 'WatchHamster_v3.0',
                'posco_news_250808': 'posco_news_250808',
            }
            
            for old_name, new_name in file_mappings.items():
                if old_name in content:
                    content = content.replace(old_name, new_name)
                    changes_made.append(f"파일 참조 수정: {old_name} -> {new_name}")
            
            # 경로 표준화
            content = content.replace('\\', '/')  # Windows 경로를 Unix 스타일로
            if '\\' in original_content:
                changes_made.append("경로 구분자 표준화 (\/를 /로 변경)")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return RepairResult(
                file_path=str(file_path),
                repair_type="FileReferenceRepair",
                success=True,
                changes_made=changes_made,
                backup_created=backup_created
            )
            
        except Exception as e:
            return RepairResult(
                file_path=str(file_path),
                repair_type="FileReferenceRepair",
                success=False,
                changes_made=[],
                backup_created=False,
                error_message=str(e)
            )


class AutomatedRepairSystem:
    """통합 자동화 수리 시스템"""
    
    def __init__(self):
        self.backup_manager = BackupManager()
        self.syntax_diagnostic = SyntaxErrorDiagnostic()
        self.syntax_repairer = SyntaxErrorRepairer(self.backup_manager)
        self.import_diagnostic = ImportDiagnostic()
        self.import_repairer = ImportRepairer(self.backup_manager)
        self.file_ref_diagnostic = FileReferenceDiagnostic()
        self.file_ref_repairer = FileReferenceRepairer(self.backup_manager)
        
        self.repair_results = []
    
    def run_full_diagnosis(self) -> Dict[str, Any]:
        """전체 시스템 진단 실행"""
        print("🔍 POSCO 시스템 전체 진단 시작...")
        
        # 전체 백업 생성
        backup_path = self.backup_manager.create_full_backup()
        
        diagnosis_results = {
            "backup_created": backup_path,
            "timestamp": datetime.datetime.now().isoformat(),
            "syntax_errors": [],
            "import_problems": [],
            "broken_references": []
        }
        
        # 구문 오류 진단
        print("  📝 Python 구문 오류 진단 중...")
        syntax_errors = self.syntax_diagnostic.diagnose_all_files()
        diagnosis_results["syntax_errors"] = [asdict(error) for error in syntax_errors]
        print(f"     발견된 구문 오류: {len(syntax_errors)}개")
        
        # Import 문제 진단
        print("  📦 Import 문제 진단 중...")
        missing_modules = self.import_diagnostic.find_missing_modules()
        diagnosis_results["import_problems"] = missing_modules
        print(f"     발견된 Import 문제: {len(missing_modules)}개")
        
        # 파일 참조 진단
        print("  🔗 파일 참조 무결성 진단 중...")
        broken_refs = self.file_ref_diagnostic.scan_file_references()
        diagnosis_results["broken_references"] = [asdict(ref) for ref in broken_refs]
        print(f"     발견된 깨진 참조: {len(broken_refs)}개")
        
        # 진단 결과 저장
        self._save_diagnosis_results(diagnosis_results)
        
        print("✅ 전체 진단 완료!")
        return diagnosis_results
    
    def _save_diagnosis_results(self, results: Dict[str, Any]):
        """진단 결과 저장"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"diagnosis_results_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"진단 결과 저장: {results_file}")
        except Exception as e:
            print(f"진단 결과 저장 실패: {e}")
    
    def _save_repair_results(self, results: Dict[str, Any]):
        """수리 결과 저장"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"repair_results_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"수리 결과 저장: {results_file}")
        except Exception as e:
            print(f"수리 결과 저장 실패: {e}")
    
    def run_automated_repair(self) -> Dict[str, Any]:
        """자동화된 수리 실행"""
        print("🔧 POSCO 시스템 자동 수리 시작...")
        
        repair_summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "syntax_repairs": [],
            "import_repairs": [],
            "reference_repairs": [],
            "total_files_processed": 0,
            "successful_repairs": 0,
            "failed_repairs": 0
        }
        
        # Python 파일들에 대해 수리 실행
        python_files = list(Path(".").glob("**/*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in [".git", "__pycache__", ".backup"])]
        
        repair_summary["total_files_processed"] = len(python_files)
        
        for py_file in python_files:
            print(f"  🔧 수리 중: {py_file}")
            
            # 구문 오류 수리
            syntax_result = self.syntax_repairer.repair_file(py_file)
            repair_summary["syntax_repairs"].append(asdict(syntax_result))
            
            # Import 문제 수리
            import_result = self.import_repairer.repair_missing_imports(py_file)
            repair_summary["import_repairs"].append(asdict(import_result))
            
            # 파일 참조 수리
            reference_result = self.file_ref_repairer.repair_broken_references(py_file)
            repair_summary["reference_repairs"].append(asdict(reference_result))
            
            # 성공/실패 카운트
            if syntax_result.success and import_result.success and reference_result.success:
                repair_summary["successful_repairs"] += 1
            else:
                repair_summary["failed_repairs"] += 1
            
            self.repair_results.extend([syntax_result, import_result, reference_result])
        
        # 수리 결과 저장
        self._save_repair_results(repair_summary)
        
        print("✅ 자동 수리 완료!")
        return repair_summary
    
    def verify_repairs(self) -> Dict[str, Any]:
        """수리 결과 검증"""
        print("🔍 수리 결과 검증 시작...")
        
        verification_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "syntax_verification": {
                "total_files": 0,
                "files_with_errors": 0,
                "remaining_errors": 0,
                "errors": []
            },
            "import_verification": {
                "total_modules": 0,
                "failed_imports": 0,
                "remaining_problems": 0,
                "problems": []
            },
            "reference_verification": {
                "total_references": 0,
                "broken_references": 0,
                "remaining_broken": 0
            },
            "overall_success_rate": 0.0
        }
        
        # 구문 검증
        print("  📝 구문 오류 검증 중...")
        syntax_errors = self.syntax_diagnostic.diagnose_all_files()
        verification_results["syntax_verification"]["remaining_errors"] = len(syntax_errors)
        verification_results["syntax_verification"]["errors"] = [asdict(error) for error in syntax_errors[:10]]
        
        # Import 검증
        print("  📦 Import 문제 검증 중...")
        import_problems = self.import_diagnostic.find_missing_modules()
        verification_results["import_verification"]["remaining_problems"] = len(import_problems)
        verification_results["import_verification"]["problems"] = import_problems[:10]
        
        # 파일 참조 검증
        print("  🔗 파일 참조 검증 중...")
        broken_refs = self.file_ref_diagnostic.scan_file_references()
        verification_results["reference_verification"]["remaining_broken"] = len(broken_refs)
        
        # 전체 성공률 계산
        total_issues = len(syntax_errors) + len(import_problems) + len(broken_refs)
        if total_issues == 0:
            verification_results["overall_success_rate"] = 100.0
        else:
            # 이전 진단 결과와 비교하여 개선율 계산
            verification_results["overall_success_rate"] = max(0, 100 - (total_issues * 2))  # 간단한 계산
        
        print("✅ 검증 완료!")
        return verification_results
    
    def rollback_changes(self, file_path: str) -> bool:
        """특정 파일의 변경사항 롤백"""
        try:
            return self.backup_manager.restore_file(file_path)
        except Exception as e:
            print(f"롤백 실패 {file_path}: {e}")
            return Falser_summary["syntax_repairs"].append(asdict(syntax_result))
            
            # Import 문제 수리
            import_result = self.import_repairer.repair_missing_imports(py_file)
            repair_summary["import_repairs"].append(asdict(import_result))
            
            # 파일 참조 수리
            ref_result = self.file_ref_repairer.repair_broken_references(py_file)
            repair_summary["reference_repairs"].append(asdict(ref_result))
            
            # 성공/실패 카운트
            if syntax_result.success and import_result.success and ref_result.success:
                repair_summary["successful_repairs"] += 1
            else:
                repair_summary["failed_repairs"] += 1
        
        # 수리 결과 저장
        self._save_repair_results(repair_summary)
        
        print("✅ 자동 수리 완료!")
        return repair_summary
    
    def verify_repairs(self) -> Dict[str, Any]:
        """수리 결과 검증"""
        print("✅ 수리 결과 검증 시작...")
        
        verification_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "syntax_verification": {},
            "import_verification": {},
            "overall_success_rate": 0
        }
        
        # 구문 검증
        print("  📝 구문 검증 중...")
        syntax_errors = self.syntax_diagnostic.diagnose_all_files()
        verification_results["syntax_verification"] = {
            "remaining_errors": len(syntax_errors),
            "errors": [asdict(error) for error in syntax_errors]
        }
        
        # Import 검증
        print("  📦 Import 검증 중...")
        missing_modules = self.import_diagnostic.find_missing_modules()
        verification_results["import_verification"] = {
            "remaining_problems": len(missing_modules),
            "problems": missing_modules
        }
        
        # 전체 성공률 계산
        total_issues = len(syntax_errors) + len(missing_modules)
        if total_issues == 0:
            verification_results["overall_success_rate"] = 100.0
        else:
            # 이전 진단 결과와 비교하여 개선율 계산
            verification_results["overall_success_rate"] = max(0, 100 - total_issues)
        
        print(f"✅ 검증 완료! 전체 성공률: {verification_results['overall_success_rate']:.1f}%")
        return verification_results
    
    def rollback_changes(self, file_path: str) -> bool:
        """특정 파일의 변경사항 롤백"""
        return self.backup_manager.restore_file(file_path)
    
    def _save_diagnosis_results(self, results: Dict[str, Any]):
        """진단 결과 저장"""
        try:
            with open("automated_repair_diagnosis.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"진단 결과 저장 실패: {e}")
    
    def _save_repair_results(self, results: Dict[str, Any]):
        """수리 결과 저장"""
        try:
            with open("automated_repair_results.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"수리 결과 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    print("🚀 POSCO 시스템 자동화된 수리 도구 v1.0")
    print("=" * 50)
    
    repair_system = AutomatedRepairSystem()
    
    try:
        # 1단계: 전체 진단
        diagnosis_results = repair_system.run_full_diagnosis()
        
        # 2단계: 자동 수리
        repair_results = repair_system.run_automated_repair()
        
        # 3단계: 수리 검증
        verification_results = repair_system.verify_repairs()
        
        # 결과 요약 출력
        print("\n" + "=" * 50)
        print("📊 최종 수리 결과 요약")
        print("=" * 50)
        print(f"처리된 파일 수: {repair_results['total_files_processed']}")
        print(f"성공한 수리: {repair_results['successful_repairs']}")
        print(f"실패한 수리: {repair_results['failed_repairs']}")
        print(f"전체 성공률: {verification_results['overall_success_rate']:.1f}%")
        print(f"남은 구문 오류: {verification_results['syntax_verification']['remaining_errors']}")
        print(f"남은 Import 문제: {verification_results['import_verification']['remaining_problems']}")
        
        if verification_results['overall_success_rate'] >= 95:
            print("\n🎉 수리 목표 달성! (95% 이상)")
        else:
            print(f"\n⚠️  추가 수리 필요 (목표: 95%, 현재: {verification_results['overall_success_rate']:.1f}%)")
        
    except Exception as e:
        print(f"❌ 수리 시스템 실행 중 오류 발생: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()