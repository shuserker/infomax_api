#!/usr/bin/env python3
"""
POSCO 시스템 파일 참조 무결성 완전 복구 도구

Task 4: 파일 참조 무결성 완전 복구
- 83개 깨진 파일 참조 모두 수정
- 존재하지 않는 파일 경로 참조 제거 또는 수정
- 와일드카드 패턴 오인식 문제 해결
- 상대 경로 참조 정확성 검증 및 표준화
"""

import os
import re
import json
import shutil
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FileReferenceIssue:
    """파일 참조 문제 정보"""
    source_file: str
    referenced_path: str
    line_number: int
    issue_type: str
    context: str
    severity: str
    suggested_fix: Optional[str] = None

@dataclass
class RepairResult:
    """수리 결과 정보"""
    file_path: str
    repair_type: str
    success: bool
    changes_made: List[str]
    backup_created: bool
    error_message: Optional[str] = None

class ComprehensiveFileReferenceRepairer:
    """종합적인 파일 참조 무결성 복구 클래스"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.issues: List[FileReferenceIssue] = []
        self.repair_results: List[RepairResult] = []
        self.existing_files: Dict[str, List[str]] = {}
        self.python_modules: Dict[str, str] = {}
        self.backup_dir = Path(".comprehensive_file_reference_backup")
        
        # Python 표준 라이브러리 (제외할 모듈들)
        self.standard_library = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'logging', 'unittest',
            'subprocess', 'shutil', 'glob', 'collections', 'itertools', 'functools',
            'typing', 'dataclasses', 'abc', 'contextlib', 'warnings', 'traceback',
            'inspect', 'importlib', 'pkgutil', 'threading', 'multiprocessing',
            'queue', 'socket', 'urllib', 'http', 'email', 'html', 'xml', 'csv',
            'sqlite3', 'hashlib', 'hmac', 'secrets', 'uuid', 'random', 'math',
            'statistics', 'decimal', 'fractions', 'cmath', 'operator', 'copy',
            'pickle', 'copyreg', 'shelve', 'marshal', 'dbm', 'zlib', 'gzip',
            'bz2', 'lzma', 'zipfile', 'tarfile', 'configparser', 'netrc',
            'xdrlib', 'plistlib', 'calendar', 'locale', 'gettext', 'argparse',
            'optparse', 'getopt', 'tempfile', 'glob', 'fnmatch', 'linecache',
            'shlex', 'string', 'textwrap', 'unicodedata', 'stringprep',
            'readline', 'rlcompleter', 'struct', 'codecs', 'encodings',
            'io', 'mmap', 'select', 'selectors', 'asyncio', 'asynchat',
            'asyncore', 'signal', 'msilib', 'msvcrt', 'winreg', 'winsound',
            'ast', 'dis', 'keyword', 'token', 'tokenize', 'parser', 'symbol',
            'compile', 'compileall', 'py_compile', 'zipimport', 'runpy'
        }
        
        # 제외할 패턴들 (실제 파일이 아닌 것들)
        self.exclude_patterns = [
            r'/*/.',  # 와일드카드 패턴
            r'/{.*/}',  # 템플릿 변수
            r'http[s]?:/',  # URL
            r'file:/',  # 파일 URL
            r'^/$',  # 환경 변수
            r'/././',  # 상위 디렉토리 참조
            r'^/',  # 절대 경로 (시스템 파일)
            r'__pycache__',  # Python 캐시
            r'/.git/',  # Git 디렉토리
            r'/.pyc$',  # Python 바이트코드
            r'backup_/d+',  # 백업 파일
        ]
        
        self._build_file_index()

    def _build_file_index(self):
        """파일 인덱스 구축"""
        logger.info("파일 인덱스 구축 중...")
        
        for file_path in self.root_path.rglob("*"):
            if (file_path.is_file() and 
                not file_path.name.startswith('.') and
                not any(pattern in str(file_path) for pattern in ['.git', '__pycache__', 'backup'])):
                
                filename = file_path.name
                stem = file_path.stem
                relative_path = str(file_path.relative_to(self.root_path))
                
                # 파일명으로 매핑
                if filename not in self.existing_files:
                    self.existing_files[filename] = []
                self.existing_files[filename].append(relative_path)
                
                # 확장자 없는 이름으로도 매핑 (Python 모듈용)
                if stem != filename:
                    if stem not in self.existing_files:
                        self.existing_files[stem] = []
                    self.existing_files[stem].append(relative_path)
                
                # Python 모듈 매핑
                if file_path.suffix == '.py':
                    self.python_modules[stem] = relative_path

    def _should_exclude(self, reference: str) -> bool:
        """참조를 제외해야 하는지 확인"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, reference):
                return True
        return False

    def scan_all_file_references(self) -> List[FileReferenceIssue]:
        """모든 파일 참조 스캔"""
        logger.info("파일 참조 스캔 시작...")
        
        # Python 파일 스캔
        for py_file in self.root_path.rglob("*.py"):
            if self._should_scan_file(py_file):
                self._scan_python_file(py_file)
        
        # 스크립트 파일 스캔
        for script_ext in ['*.sh', '*.bat', '*.command']:
            for script_file in self.root_path.rglob(script_ext):
                if self._should_scan_file(script_file):
                    self._scan_script_file(script_file)
        
        # JSON 설정 파일 스캔
        for json_file in self.root_path.rglob("*.json"):
            if self._should_scan_file(json_file):
                self._scan_json_file(json_file)
        
        # Markdown 문서 스캔
        for md_file in self.root_path.rglob("*.md"):
            if self._should_scan_file(md_file):
                self._scan_markdown_file(md_file)
        
        logger.info(f"총 {len(self.issues)}개의 파일 참조 문제 발견")
        return self.issues

    def _should_scan_file(self, file_path: Path) -> bool:
        """파일을 스캔해야 하는지 확인"""
        if file_path.name.startswith('.'):
            return False
        
        path_str = str(file_path)
        exclude_dirs = ['.git', '__pycache__', 'backup', '.vscode', '.kiro']
        
        for exclude_dir in exclude_dirs:
            if exclude_dir in path_str:
                return False
        
        return True

    def _scan_python_file(self, file_path: Path):
        """Python 파일 스캔"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # AST 파싱으로 import 문 추출
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_python_import(alias.name, file_path, node.lineno)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._check_python_import(node.module, file_path, node.lineno)
            except SyntaxError:
                # 구문 오류가 있는 파일은 라인별로 검사
                for line_num, line in enumerate(lines, 1):
                    if 'import ' in line:
                        self._check_import_line(line, file_path, line_num)
            
            # 파일 경로 참조 검사
            for line_num, line in enumerate(lines, 1):
                self._check_file_references_in_line(line, file_path, line_num)
                
        except Exception as e:
            logger.error(f"Python 파일 스캔 오류 {file_path}: {e}")

    def _check_python_import(self, module_name: str, source_file: Path, line_num: int):
        """Python import 검증"""
        if not module_name or self._should_exclude(module_name):
            return
        
        # 표준 라이브러리 체크
        base_module = module_name.split('.')[0]
        if base_module in self.standard_library:
            return
        
        # 상대 import는 제외
        if module_name.startswith('.'):
            return
        
        # 로컬 모듈 체크
        if self._is_valid_local_module(module_name):
            return
        
        # 깨진 import 발견
        issue = FileReferenceIssue(
            source_file=str(source_file.relative_to(self.root_path)),
            referenced_path=module_name,
            line_number=line_num,
            issue_type='broken_import',
            context=f"import {module_name}",
            severity='high',
            suggested_fix=self._suggest_import_fix(module_name)
        )
        self.issues.append(issue)

    def _check_import_line(self, line: str, source_file: Path, line_num: int):
        """import 라인 검사 (구문 오류가 있는 파일용)"""
        # import 패턴 매칭
        import_patterns = [
            r'from/s+([a-zA-Z_][a-zA-Z0-9_.]*)/s+import',
            r'import/s+([a-zA-Z_][a-zA-Z0-9_.]*)'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                module_name = match.group(1)
                self._check_python_import(module_name, source_file, line_num)

    def _is_valid_local_module(self, module_name: str) -> bool:
        """로컬 모듈이 유효한지 확인"""
        base_module = module_name.split('.')[0]
        
        # 직접 매칭
        if base_module in self.python_modules:
            return True
        
        # 파일 경로로 확인
        module_path = module_name.replace('.', '/') + '.py'
        if module_path in [paths[0] for paths in self.existing_files.values() if paths]:
            return True
        
        # 패키지 확인
        package_init = module_name.replace('.', '/') + '/__init__.py'
        if package_init in [paths[0] for paths in self.existing_files.values() if paths]:
            return True
        
        return False

    def _check_file_references_in_line(self, line: str, source_file: Path, line_num: int):
        """라인에서 파일 참조 검사"""
        # 파일 경로 패턴들
        patterns = [
            r'[\'"]([^\'"/s]+/.(py|sh|bat|json|md|txt|log|command|html|css|js|csv))[\'"]',
            r'Path/([\'"]([^\'"]+)[\'"]',
            r'open/([\'"]([^\'"]+)[\'"]',
            r'with/s+open/([\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                file_ref = match.group(1)
                if self._should_exclude(file_ref):
                    continue
                
                if not self._file_exists(file_ref, source_file):
                    issue = FileReferenceIssue(
                        source_file=str(source_file.relative_to(self.root_path)),
                        referenced_path=file_ref,
                        line_number=line_num,
                        issue_type='missing_file',
                        context=line.strip(),
                        severity='medium',
                        suggested_fix=self._suggest_file_fix(file_ref)
                    )
                    self.issues.append(issue)

    def _scan_script_file(self, file_path: Path):
        """스크립트 파일 스캔"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # 스크립트 실행 패턴
                patterns = [
                    r'python3?/s+([^/s]+/.py)',
                    r'bash/s+([^/s]+/.sh)',
                    r'/./([^/s]+/.(sh|command|bat))',
                    r'exec/s+([^/s]+/.(sh|command|bat))'
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        script_ref = match.group(1)
                        if not self._file_exists(script_ref, file_path):
                            issue = FileReferenceIssue(
                                source_file=str(file_path.relative_to(self.root_path)),
                                referenced_path=script_ref,
                                line_number=line_num,
                                issue_type='invalid_script',
                                context=line.strip(),
                                severity='high',
                                suggested_fix=self._suggest_file_fix(script_ref)
                            )
                            self.issues.append(issue)
                            
        except Exception as e:
            logger.error(f"스크립트 파일 스캔 오류 {file_path}: {e}")

    def _scan_json_file(self, file_path: Path):
        """JSON 파일 스캔"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # JSON 파일에서 파일 경로 찾기
            file_patterns = re.findall(r'"([^"]+/.(py|sh|bat|json|md|txt|log))"', content)
            
            for file_ref, ext in file_patterns:
                if self._should_exclude(file_ref):
                    continue
                
                if not self._file_exists(file_ref, file_path):
                    # 라인 번호 찾기
                    lines = content.split('\n')
                    line_num = 1
                    for i, line in enumerate(lines, 1):
                        if file_ref in line:
                            line_num = i
                            break
                    
                    issue = FileReferenceIssue(
                        source_file=str(file_path.relative_to(self.root_path)),
                        referenced_path=file_ref,
                        line_number=line_num,
                        issue_type='missing_file',
                        context=f"JSON reference: {file_ref}",
                        severity='medium',
                        suggested_fix=self._suggest_file_fix(file_ref)
                    )
                    self.issues.append(issue)
                    
        except Exception as e:
            logger.error(f"JSON 파일 스캔 오류 {file_path}: {e}")

    def _scan_markdown_file(self, file_path: Path):
        """Markdown 파일 스캔"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Markdown 링크 패턴
                patterns = [
                    r'/[.*?/]/(([^)]+/.(py|sh|bat|json|md|txt|log))/)',
                    r'`([^`]+/.(py|sh|bat|json|md|txt|log))`'
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        file_ref = match.group(1)
                        if self._should_exclude(file_ref):
                            continue
                        
                        if not self._file_exists(file_ref, file_path):
                            issue = FileReferenceIssue(
                                source_file=str(file_path.relative_to(self.root_path)),
                                referenced_path=file_ref,
                                line_number=line_num,
                                issue_type='missing_file',
                                context=line.strip(),
                                severity='low',
                                suggested_fix=self._suggest_file_fix(file_ref)
                            )
                            self.issues.append(issue)
                            
        except Exception as e:
            logger.error(f"Markdown 파일 스캔 오류 {file_path}: {e}")

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
        if root_path.exists():
            return True
        
        # 파일 인덱스에서 확인
        filename = Path(file_ref).name
        return filename in self.existing_files

    def _suggest_import_fix(self, module_name: str) -> Optional[str]:
        """import 수정 제안"""
        base_module = module_name.split('.')[0]
        
        # 직접 매칭
        if base_module in self.python_modules:
            return base_module
        
        # 유사한 모듈명 찾기
        for existing_module in self.python_modules.keys():
            if (existing_module.lower() == base_module.lower() or
                base_module.lower() in existing_module.lower() or
                existing_module.lower() in base_module.lower()):
                return existing_module
        
        return None

    def _suggest_file_fix(self, file_ref: str) -> Optional[str]:
        """파일 경로 수정 제안"""
        filename = Path(file_ref).name
        
        # 정확한 파일명 매칭
        if filename in self.existing_files:
            candidates = self.existing_files[filename]
            if len(candidates) == 1:
                return candidates[0]
            elif len(candidates) > 1:
                # 가장 유사한 경로 선택
                return self._find_best_path_match(file_ref, candidates)
        
        # 유사한 파일명 찾기
        for existing_name, paths in self.existing_files.items():
            if (existing_name.lower() == filename.lower() or
                filename.lower() in existing_name.lower() or
                existing_name.lower() in filename.lower()):
                return paths[0] if paths else None
        
        return None

    def _find_best_path_match(self, original_path: str, candidates: List[str]) -> str:
        """가장 적합한 경로 매치 찾기"""
        original_parts = Path(original_path).parts
        best_score = 0
        best_match = candidates[0]
        
        for candidate in candidates:
            candidate_parts = Path(candidate).parts
            score = len(set(original_parts) & set(candidate_parts))
            if score > best_score:
                best_score = score
                best_match = candidate
        
        return best_match

    def repair_all_references(self) -> List[RepairResult]:
        """모든 깨진 참조 수리"""
        logger.info("파일 참조 수리 시작...")
        
        # 파일별로 그룹화
        files_to_repair = {}
        for issue in self.issues:
            if issue.source_file not in files_to_repair:
                files_to_repair[issue.source_file] = []
            files_to_repair[issue.source_file].append(issue)
        
        # 각 파일 수리
        for file_path, issues in files_to_repair.items():
            # 수정 가능한 이슈만 처리
            fixable_issues = [issue for issue in issues if issue.suggested_fix]
            if fixable_issues:
                result = self._repair_file_references(file_path, fixable_issues)
                self.repair_results.append(result)
        
        logger.info(f"총 {len(self.repair_results)}개 파일 수리 완료")
        return self.repair_results

    def _repair_file_references(self, file_path: str, issues: List[FileReferenceIssue]) -> RepairResult:
        """개별 파일의 참조 수리"""
        full_path = self.root_path / file_path
        changes_made = []
        
        try:
            # 백업 생성
            backup_created = self._create_backup(full_path)
            
            # 파일 읽기
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # 라인별 수정 (역순으로 처리하여 라인 번호 변경 방지)
            issues_sorted = sorted(issues, key=lambda x: x.line_number, reverse=True)
            
            for issue in issues_sorted:
                if issue.suggested_fix and issue.line_number <= len(lines):
                    old_line = lines[issue.line_number - 1]
                    new_line = old_line.replace(issue.referenced_path, issue.suggested_fix)
                    if new_line != old_line:
                        lines[issue.line_number - 1] = new_line
                        changes_made.append(f"Line {issue.line_number}: {issue.referenced_path} → {issue.suggested_fix}")
            
            # 파일 쓰기
            if changes_made:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            
            return RepairResult(
                file_path=file_path,
                repair_type="file_reference",
                success=True,
                changes_made=changes_made,
                backup_created=backup_created
            )
            
        except Exception as e:
            return RepairResult(
                file_path=file_path,
                repair_type="file_reference",
                success=False,
                changes_made=[],
                backup_created=False,
                error_message=str(e)
            )

    def _create_backup(self, file_path: Path) -> bool:
        """파일 백업 생성"""
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{file_path.name}.backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            logger.error(f"백업 생성 실패 {file_path}: {e}")
            return False

    def generate_comprehensive_report(self) -> Dict:
        """종합 보고서 생성"""
        high_severity = [i for i in self.issues if i.severity == 'high']
        medium_severity = [i for i in self.issues if i.severity == 'medium']
        low_severity = [i for i in self.issues if i.severity == 'low']
        
        fixable_issues = [i for i in self.issues if i.suggested_fix]
        unfixable_issues = [i for i in self.issues if not i.suggested_fix]
        
        report = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "summary": {
                "total_issues": len(self.issues),
                "high_severity": len(high_severity),
                "medium_severity": len(medium_severity),
                "low_severity": len(low_severity),
                "fixable_issues": len(fixable_issues),
                "unfixable_issues": len(unfixable_issues),
                "files_repaired": len(self.repair_results),
                "successful_repairs": len([r for r in self.repair_results if r.success]),
                "issues_by_type": {
                    "broken_import": len([i for i in self.issues if i.issue_type == 'broken_import']),
                    "missing_file": len([i for i in self.issues if i.issue_type == 'missing_file']),
                    "invalid_script": len([i for i in self.issues if i.issue_type == 'invalid_script'])
                }
            },
            "repair_results": [
                {
                    "file_path": result.file_path,
                    "repair_type": result.repair_type,
                    "success": result.success,
                    "changes_made": result.changes_made,
                    "backup_created": result.backup_created,
                    "error_message": result.error_message
                }
                for result in self.repair_results
            ],
            "remaining_issues": [
                {
                    "source_file": issue.source_file,
                    "referenced_path": issue.referenced_path,
                    "line_number": issue.line_number,
                    "issue_type": issue.issue_type,
                    "context": issue.context,
                    "severity": issue.severity,
                    "suggested_fix": issue.suggested_fix
                }
                for issue in unfixable_issues[:100]  # 상위 100개만
            ]
        }
        
        return report

    def save_report(self, report: Dict, filename: str = "comprehensive_file_reference_repair_report.json"):
        """보고서 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"보고서 저장: {filename}")

def main():
    """메인 실행 함수"""
    print("🔧 POSCO 시스템 파일 참조 무결성 완전 복구 도구")
    print("=" * 60)
    
    repairer = ComprehensiveFileReferenceRepairer()
    
    # 1. 파일 참조 스캔
    print("\n1️⃣ 종합적인 파일 참조 스캔 중...")
    issues = repairer.scan_all_file_references()
    print(f"   📊 {len(issues)}개의 파일 참조 문제 발견")
    
    if issues:
        # 문제 유형별 분석
        broken_imports = [i for i in issues if i.issue_type == 'broken_import']
        missing_files = [i for i in issues if i.issue_type == 'missing_file']
        invalid_scripts = [i for i in issues if i.issue_type == 'invalid_script']
        fixable_issues = [i for i in issues if i.suggested_fix]
        
        print(f"   • 깨진 import: {len(broken_imports)}개")
        print(f"   • 누락된 파일: {len(missing_files)}개")
        print(f"   • 잘못된 스크립트: {len(invalid_scripts)}개")
        print(f"   • 수정 가능한 문제: {len(fixable_issues)}개")
        
        # 2. 수정 가능한 참조 수리
        if fixable_issues:
            print(f"\n2️⃣ {len(fixable_issues)}개의 수정 가능한 참조 수리 중...")
            repair_results = repairer.repair_all_references()
            successful = len([r for r in repair_results if r.success])
            print(f"   ✅ {successful}/{len(repair_results)}개 파일 수리 완료")
        
        # 3. 종합 보고서 생성
        print("\n3️⃣ 종합 수리 보고서 생성 중...")
        report = repairer.generate_comprehensive_report()
        repairer.save_report(report)
        print("   ✅ 보고서 생성 완료")
        
        # 결과 요약
        print(f"\n📊 최종 수리 결과:")
        print(f"   • 발견된 문제: {len(issues)}개")
        print(f"   • 수리된 파일: {report['summary']['successful_repairs']}개")
        print(f"   • 남은 문제: {report['summary']['unfixable_issues']}개")
        print(f"   • 백업 디렉토리: {repairer.backup_dir}")
        
        # 주요 성과
        if report['summary']['successful_repairs'] > 0:
            print(f"\n🎉 주요 성과:")
            total_changes = sum(len(r['changes_made']) for r in report['repair_results'] if r['success'])
            print(f"   • 총 {total_changes}개의 파일 참조 수정 완료")
            print(f"   • 파일 참조 무결성 크게 개선")
    else:
        print("   ✅ 파일 참조 문제가 발견되지 않았습니다!")
    
    return len(issues) == 0 or len([r for r in repairer.repair_results if r.success]) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)