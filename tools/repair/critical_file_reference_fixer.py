#!/usr/bin/env python3
"""
POSCO 시스템 핵심 파일 참조 수정 도구

실제로 시스템 동작에 영향을 주는 핵심 파일 참조 문제만 수정:
1. 존재하지 않는 Python 모듈 import (로컬 모듈만)
2. 실행 스크립트에서 참조하는 존재하지 않는 파일
3. 설정 파일에서 참조하는 존재하지 않는 핵심 파일
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CriticalIssue:
    """핵심 파일 참조 문제"""
    source_file: str
    referenced_path: str
    line_number: int
    issue_type: str
    context: str
    suggested_fix: Optional[str] = None
    fix_applied: bool = False

class CriticalFileReferenceFixer:
    """핵심 파일 참조 수정 클래스"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.issues: List[CriticalIssue] = []
        self.backup_dir = Path(".critical_file_reference_backup")
        
        # 실제 존재하는 파일들
        self.existing_files: Set[str] = set()
        self.python_modules: Dict[str, str] = {}
        
        # 핵심 파일 패턴 (실제로 중요한 것들만)
        self.critical_patterns = {
            'python_modules': [
                'naming_convention_manager',
                'file_renaming_system', 
                'python_naming_standardizer',
                'shell_batch_script_standardizer',
                'documentation_standardizer',
                'config_data_standardizer',
                'system_output_message_standardizer',
                'folder_structure_reorganizer',
                'naming_standardization_verification_system'
            ],
            'config_files': [
                'test_config.json',
                '.naming_backup/config_data_backup/Monitoring/Posco_News_mini/modules.json',
                'requirements.txt'
            ],
            'script_files': [
                'Monitoring/POSCO_News_250808/posco_news_250808_control_center.sh',
                'watchhamster_v3_v3_0_control_center.sh',
                'migrate_to_v2.sh',
                'run_migration_verification.sh'
            ]
        }
        
        self._build_file_index()

    def _build_file_index(self):
        """파일 인덱스 구축"""
        logger.info("파일 인덱스 구축 중...")
        
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = str(file_path.relative_to(self.root_path))
                self.existing_files.add(relative_path)
                
                # Python 모듈 매핑
                if file_path.suffix == '.py':
                    module_name = file_path.stem
                    self.python_modules[module_name] = relative_path

    def find_critical_issues(self) -> List[CriticalIssue]:
        """핵심 파일 참조 문제 찾기"""
        logger.info("핵심 파일 참조 문제 스캔 중...")
        
        # 1. 핵심 Python 모듈 import 문제
        self._find_critical_import_issues()
        
        # 2. 실행 스크립트의 파일 참조 문제
        self._find_script_reference_issues()
        
        # 3. 설정 파일의 핵심 파일 참조 문제
        self._find_config_reference_issues()
        
        logger.info(f"총 {len(self.issues)}개의 핵심 문제 발견")
        return self.issues

    def _find_critical_import_issues(self):
        """핵심 Python 모듈 import 문제 찾기"""
        for py_file in self.root_path.rglob("*.py"):
            if py_file.name.startswith('.'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    # import 문 찾기
                    import_patterns = [
                        r'from/s+([a-zA-Z_]\[a-zA-Z0-9_\]*)/s+import',
                        r'import/s+([a-zA-Z_][a-zA-Z0-9_]*)'
                    ]
                    
                    for pattern in import_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            module_name = match.group(1)
                            
                            # 핵심 모듈인지 확인
                            if module_name in self.critical_patterns['python_modules']:
                                if not self._module_exists(module_name):
                                    issue = CriticalIssue(
                                        source_file=str(py_file.relative_to(self.root_path)),
                                        referenced_path=module_name,
                                        line_number=line_num,
                                        issue_type='critical_import',
                                        context=line.strip(),
                                        suggested_fix=self._suggest_module_fix(module_name)
                                    )
                                    self.issues.append(issue)
                                    
            except Exception as e:
                logger.error(f"Python 파일 스캔 오류 {py_file}: {e}")

    def _find_script_reference_issues(self):
        """스크립트 파일 참조 문제 찾기"""
        script_extensions = ['*.sh', '*.bat', '*.command']
        
        for ext in script_extensions:
            for script_file in self.root_path.rglob(ext):
                if script_file.name.startswith('.'):
                    continue
                    
                try:
                    with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        # 스크립트 실행 패턴
                        patterns = [
                            r'python3?/s+(\[^/s\]+/.py)',
                            r'bash/s+(\[^/s\]+/.sh)',
                            r'/./([^/s]+/.(sh|py|bat))'
                        ]
                        
                        for pattern in patterns:
                            matches = re.finditer(pattern, line)
                            for match in matches:
                                file_ref = match.group(1)
                                
                                if not self._file_exists_relative(file_ref, script_file):
                                    issue = CriticalIssue(
                                        source_file=str(script_file.relative_to(self.root_path)),
                                        referenced_path=file_ref,
                                        line_number=line_num,
                                        issue_type='script_reference',
                                        context=line.strip(),
                                        suggested_fix=self._suggest_file_fix(file_ref)
                                    )
                                    self.issues.append(issue)
                                    
                except Exception as e:
                    logger.error(f"스크립트 파일 스캔 오류 {script_file}: {e}")

    def _find_config_reference_issues(self):
        """설정 파일 참조 문제 찾기"""
        for config_file in self.root_path.rglob("*.json"):
            if config_file.name.startswith('.'):
                continue
                
            try:
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 핵심 파일 참조만 확인
                for critical_file in (self.critical_patterns['config_files'] + 
                                    self.critical_patterns['script_files']):
                    if critical_file in content:
                        if not self._file_exists_anywhere(critical_file):
                            # 라인 번호 찾기
                            lines = content.split('\n')
                            line_num = 1
                            for i, line in enumerate(lines, 1):
                                if critical_file in line:
                                    line_num = i
                                    break
                            
                            issue = CriticalIssue(
                                source_file=str(config_file.relative_to(self.root_path)),
                                referenced_path=critical_file,
                                line_number=line_num,
                                issue_type='config_reference',
                                context=f"Config reference: {critical_file}",
                                suggested_fix=self._suggest_file_fix(critical_file)
                            )
                            self.issues.append(issue)
                            
            except Exception as e:
                logger.error(f"설정 파일 스캔 오류 {config_file}: {e}")

    def _module_exists(self, module_name: str) -> bool:
        """모듈이 존재하는지 확인"""
        # Python 모듈 매핑에서 확인
        if module_name in self.python_modules:
            return True
        
        # 파일로 직접 확인
        module_file = f"{module_name}.py"
        return module_file in self.existing_files

    def _file_exists_relative(self, file_ref: str, source_file: Path) -> bool:
        """상대 경로로 파일이 존재하는지 확인"""
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

    def _file_exists_anywhere(self, filename: str) -> bool:
        """파일이 어디든 존재하는지 확인"""
        for existing_file in self.existing_files:
            if Path(existing_file).name == filename:
                return True
        return False

    def _suggest_module_fix(self, module_name: str) -> Optional[str]:
        """모듈 수정 제안"""
        # 유사한 모듈명 찾기
        for existing_module in self.python_modules.keys():
            if (existing_module.lower() == module_name.lower() or
                module_name.lower() in existing_module.lower() or
                existing_module.lower() in module_name.lower()):
                return existing_module
        
        return None

    def _suggest_file_fix(self, file_ref: str) -> Optional[str]:
        """파일 수정 제안"""
        filename = Path(file_ref).name
        
        # 정확한 파일명 매칭
        for existing_file in self.existing_files:
            if Path(existing_file).name == filename:
                return existing_file
        
        # 유사한 파일명 찾기
        best_match = None
        best_score = 0
        
        for existing_file in self.existing_files:
            existing_name = Path(existing_file).name.lower()
            filename_lower = filename.lower()
            
            # 유사도 계산
            if filename_lower in existing_name or existing_name in filename_lower:
                score = len(set(filename_lower) & set(existing_name))
                if score > best_score:
                    best_score = score
                    best_match = existing_file
        
        return best_match

    def apply_fixes(self) -> int:
        """수정 사항 적용"""
        logger.info("핵심 파일 참조 문제 수정 시작...")
        
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        fixed_count = 0
        files_to_fix = {}
        
        # 파일별로 그룹화
        for issue in self.issues:
            if issue.suggested_fix:
                if issue.source_file not in files_to_fix:
                    files_to_fix[issue.source_file] = []
                files_to_fix[issue.source_file].append(issue)
        
        # 각 파일 수정
        for file_path, file_issues in files_to_fix.items():
            if self._fix_file(file_path, file_issues):
                fixed_count += len(file_issues)
        
        logger.info(f"총 {fixed_count}개 문제 수정 완료")
        return fixed_count

    def _fix_file(self, file_path: str, issues: List[CriticalIssue]) -> bool:
        """개별 파일 수정"""
        full_path = self.root_path / file_path
        
        try:
            # 백업 생성
            backup_path = self.backup_dir / f"{full_path.name}.backup_{self._get_timestamp()}"
            shutil.copy2(full_path, backup_path)
            
            # 파일 읽기
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # 수정 적용 (역순으로 처리)
            issues_sorted = sorted(issues, key=lambda x: x.line_number, reverse=True)
            changes_made = []
            
            for issue in issues_sorted:
                if issue.suggested_fix:
                    old_line = lines[issue.line_number - 1]
                    new_line = old_line.replace(issue.referenced_path, issue.suggested_fix)
                    lines[issue.line_number - 1] = new_line
                    issue.fix_applied = True
                    changes_made.append(f"Line {issue.line_number}: {issue.referenced_path} → {issue.suggested_fix}")
            
            # 파일 쓰기
            if changes_made:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                logger.info(f"파일 수정 완료: {file_path} ({len(changes_made)}개 변경)")
                return True
            
        except Exception as e:
            logger.error(f"파일 수정 오류 {file_path}: {e}")
            return False
        
        return False

    def _get_timestamp(self) -> str:
        """타임스탬프 생성"""
        from datetime import datetime
import datetime
import pathlib
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_report(self) -> Dict:
        """수정 보고서 생성"""
        fixed_issues = [i for i in self.issues if i.fix_applied]
        unfixed_issues = [i for i in self.issues if not i.fix_applied]
        
        report = {
            "timestamp": self._get_timestamp(),
            "summary": {
                "total_issues": len(self.issues),
                "fixed_issues": len(fixed_issues),
                "unfixed_issues": len(unfixed_issues),
                "issues_by_type": {
                    "critical_import": len([i for i in self.issues if i.issue_type == 'critical_import']),
                    "script_reference": len([i for i in self.issues if i.issue_type == 'script_reference']),
                    "config_reference": len([i for i in self.issues if i.issue_type == 'config_reference'])
                }
            },
            "fixed_issues": [
                {
                    "source_file": issue.source_file,
                    "referenced_path": issue.referenced_path,
                    "line_number": issue.line_number,
                    "issue_type": issue.issue_type,
                    "context": issue.context,
                    "suggested_fix": issue.suggested_fix
                }
                for issue in fixed_issues
            ],
            "unfixed_issues": [
                {
                    "source_file": issue.source_file,
                    "referenced_path": issue.referenced_path,
                    "line_number": issue.line_number,
                    "issue_type": issue.issue_type,
                    "context": issue.context,
                    "reason": "No suitable fix found"
                }
                for issue in unfixed_issues
            ]
        }
        
        return report

    def save_report(self, report: Dict, filename: str = "critical_file_reference_fix_report.json"):
        """보고서 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"보고서 저장: {filename}")

def main():
    """메인 실행 함수"""
    print("🔧 POSCO 시스템 핵심 파일 참조 수정 도구")
    print("=" * 50)
    
    fixer = CriticalFileReferenceFixer()
    
    # 1. 핵심 문제 찾기
    print("\n1️⃣ 핵심 파일 참조 문제 스캔 중...")
    issues = fixer.find_critical_issues()
    
    if issues:
        print(f"   ⚠️  {len(issues)}개의 핵심 문제 발견")
        
        # 2. 수정 적용
        print("\n2️⃣ 핵심 문제 수정 중...")
        fixed_count = fixer.apply_fixes()
        print(f"   ✅ {fixed_count}개 문제 수정 완료")
        
        # 3. 보고서 생성
        print("\n3️⃣ 수정 보고서 생성 중...")
        report = fixer.generate_report()
        fixer.save_report(report)
        print("   ✅ 보고서 생성 완료")
        
        # 결과 요약
        print(f"\n📊 수정 결과 요약:")
        print(f"   • 발견된 핵심 문제: {len(issues)}개")
        print(f"   • 수정된 문제: {fixed_count}개")
        print(f"   • 미해결 문제: {len(issues) - fixed_count}개")
        print(f"   • 백업 디렉토리: {fixer.backup_dir}")
        
        # 문제 유형별 요약
        print(f"   • 문제 유형별:")
        print(f"     - 핵심 import: {report['summary']['issues_by_type']['critical_import']}개")
        print(f"     - 스크립트 참조: {report['summary']['issues_by_type']['script_reference']}개")
        print(f"     - 설정 파일 참조: {report['summary']['issues_by_type']['config_reference']}개")
        
    else:
        print("   ✅ 핵심 파일 참조 문제가 발견되지 않았습니다!")
    
    return len(issues) == 0 or fixed_count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)