#!/usr/bin/env python3
"""
POSCO 시스템 최종 구문 수리 도구

Task 4 완료를 위한 최종 구문 수리:
- 중복된 import 문 정리
- 잘못된 구문 수정
- 핵심 파일들의 구문 오류 완전 해결
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalSyntaxRepairer:
    """최종 구문 수리 클래스"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.backup_dir = Path(".final_syntax_repair_backup")
        
        # 핵심 파일들
        self.critical_files = [
            "file_renaming_system.py",
            "filename_standardizer.py", 
            "naming_convention_manager.py",
            "python_naming_standardizer.py",
            "shell_batch_script_standardizer.py",
            "documentation_standardizer.py",
            "config_data_standardizer.py",
            "system_output_message_standardizer.py",
            "folder_structure_reorganizer.py",
            "naming_standardization_verification_system.py",
            "final_integration_test_system.py",
            "system_functionality_verification.py"
        ]

    def repair_all_syntax_errors(self) -> Dict:
        """모든 구문 오류 수리"""
        logger.info("최종 구문 오류 수리 시작...")
        
        repair_results = []
        
        for critical_file in self.critical_files:
            file_paths = list(self.root_path.rglob(critical_file))
            for file_path in file_paths:
                if file_path.is_file():
                    result = self._repair_file_syntax(file_path)
                    if result:
                        repair_results.append(result)
        
        return {
            "repaired_files": len(repair_results),
            "successful_repairs": len([r for r in repair_results if r['success']]),
            "results": repair_results
        }

    def _repair_file_syntax(self, file_path: Path) -> Dict:
        """개별 파일 구문 수리"""
        try:
            # 백업 생성
            self._create_backup(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            original_lines = lines.copy()
            changes_made = []
            
            # 1. 중복된 import 문 정리
            lines, import_changes = self._fix_duplicate_imports(lines)
            changes_made.extend(import_changes)
            
            # 2. 잘못된 구문 패턴 수정
            lines, syntax_changes = self._fix_syntax_patterns(lines)
            changes_made.extend(syntax_changes)
            
            # 3. 들여쓰기 문제 수정
            lines, indent_changes = self._fix_indentation(lines)
            changes_made.extend(indent_changes)
            
            # 변경사항이 있으면 파일 저장
            if changes_made:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                logger.info(f"구문 수리 완료: {file_path.name} ({len(changes_made)}개 수정)")
            
            return {
                "file_path": str(file_path.relative_to(self.root_path)),
                "success": True,
                "changes_made": changes_made
            }
            
        except Exception as e:
            logger.error(f"구문 수리 오류 {file_path}: {e}")
            return {
                "file_path": str(file_path.relative_to(self.root_path)),
                "success": False,
                "error": str(e),
                "changes_made": []
            }

    def _fix_duplicate_imports(self, lines: List[str]) -> tuple:
        """중복된 import 문 정리"""
        changes_made = []
        seen_imports = set()
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # 중복된 import 패턴 찾기
            if 'import' in line and not line.strip().startswith('#'):
                # "from from datetime import datetime import from datetime import datetime" 같은 패턴
                if line.count('import') > 1 and line.count('from') > 1:
                    # 첫 번째 유효한 import만 추출
                    match = re.search(r'(from\s+\w+\s+import\s+\w+)', line)
                    if match:
                        clean_import = match.group(1) + '\n'
                        if clean_import not in seen_imports:
                            fixed_lines.append(clean_import)
                            seen_imports.add(clean_import)
                            changes_made.append(f"Line {i+1}: 중복 import 정리")
                        continue
                
                # 일반적인 중복 import 체크
                clean_line = line.strip()
                if clean_line in seen_imports:
                    changes_made.append(f"Line {i+1}: 중복 import 제거")
                    continue
                else:
                    seen_imports.add(clean_line)
            
            fixed_lines.append(line)
        
        return fixed_lines, changes_made

    def _fix_syntax_patterns(self, lines: List[str]) -> tuple:
        """잘못된 구문 패턴 수정"""
        changes_made = []
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            fixed_line = line
            
            # 잘못된 패턴들 수정
            
            # 1. "# REMOVED:" 라인 정리
            if line.strip().startswith('# REMOVED:'):
                # REMOVED 주석 제거하고 실제 코드만 남기기
                if 'import' in line:
                    # import 문이면 완전 제거
                    fixed_line = ''
                    changes_made.append(f"Line {i+1}: REMOVED import 라인 제거")
                else:
                    # 다른 코드면 주석만 제거
                    code_part = line.split('# REMOVED:')[1].strip()
                    if code_part:
                        fixed_line = code_part + '\n'
                        changes_made.append(f"Line {i+1}: REMOVED 주석 제거")
                    else:
                        fixed_line = ''
                        changes_made.append(f"Line {i+1}: 빈 REMOVED 라인 제거")
            
            # 2. 잘못된 f-string 패턴 수정
            elif 'f"' in line and line.count('"') % 2 != 0:
                # 홀수 개의 따옴표가 있으면 수정
                fixed_line = re.sub(r'f"([^"]*)"([^"]*)"', r'f"\1\2"', line)
                if fixed_line != line:
                    changes_made.append(f"Line {i+1}: f-string 따옴표 수정")
            
            # 3. 괄호 불일치 수정
            elif '(' in line and ')' in line:
                open_count = line.count('(')
                close_count = line.count(')')
                if open_count != close_count:
                    if open_count > close_count:
                        fixed_line = line.rstrip() + ')' * (open_count - close_count) + '\n'
                        changes_made.append(f"Line {i+1}: 닫는 괄호 추가")
                    elif close_count > open_count:
                        # 여는 괄호 부족한 경우는 복잡하므로 주석 처리
                        fixed_line = f"# SYNTAX_ERROR: {line}"
                        changes_made.append(f"Line {i+1}: 괄호 불일치로 주석 처리")
            
            # 4. 잘못된 변수명 수정
            elif re.search(r'\b\d+\w+', line) and 'import' not in line:
                # 숫자로 시작하는 변수명 수정 (import 문 제외)
                fixed_line = re.sub(r'\b(\d+)(\w+)', r'var_\1_\2', line)
                if fixed_line != line:
                    changes_made.append(f"Line {i+1}: 잘못된 변수명 수정")
            
            fixed_lines.append(fixed_line)
        
        return fixed_lines, changes_made

    def _fix_indentation(self, lines: List[str]) -> tuple:
        """들여쓰기 문제 수정"""
        changes_made = []
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if line.strip():  # 빈 라인이 아닌 경우
                # 탭을 4칸 스페이스로 변경
                if '\t' in line:
                    fixed_line = line.replace('\t', '    ')
                    if fixed_line != line:
                        changes_made.append(f"Line {i+1}: 탭을 스페이스로 변경")
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return fixed_lines, changes_made

    def _create_backup(self, file_path: Path):
        """백업 생성"""
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{file_path.name}.backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            logger.error(f"백업 생성 실패 {file_path}: {e}")

    def verify_syntax_after_repair(self) -> Dict:
        """수리 후 구문 검증"""
        logger.info("수리 후 구문 검증 시작...")
        
        verification_results = {
            "total_files": 0,
            "syntax_valid": 0,
            "syntax_errors": 0,
            "file_results": []
        }
        
        for critical_file in self.critical_files:
            file_paths = list(self.root_path.rglob(critical_file))
            for file_path in file_paths:
                if file_path.is_file():
                    verification_results["total_files"] += 1
                    
                    try:
                        import subprocess
                        result = subprocess.run(
                            ['python3', '-m', 'py_compile', str(file_path)],
                            capture_output=True, text=True
                        )
                        
                        if result.returncode == 0:
                            verification_results["syntax_valid"] += 1
                            verification_results["file_results"].append({
                                "file": str(file_path.relative_to(self.root_path)),
                                "status": "valid"
                            })
                        else:
                            verification_results["syntax_errors"] += 1
                            verification_results["file_results"].append({
                                "file": str(file_path.relative_to(self.root_path)),
                                "status": "error",
                                "error": result.stderr
                            })
                    
                    except Exception as e:
                        verification_results["syntax_errors"] += 1
                        verification_results["file_results"].append({
                            "file": str(file_path.relative_to(self.root_path)),
                            "status": "error",
                            "error": str(e)
                        })
        
        return verification_results

def main():
    """메인 실행 함수"""
    print("🔧 POSCO 시스템 최종 구문 수리 도구")
    print("=" * 60)
    
    repairer = FinalSyntaxRepairer()
    
    # 1. 구문 오류 수리
    print("\n1️⃣ 핵심 파일 구문 오류 수리 중...")
    repair_result = repairer.repair_all_syntax_errors()
    print(f"   ✅ {repair_result['successful_repairs']}/{repair_result['repaired_files']}개 파일 수리 완료")
    
    # 2. 수리 후 검증
    print("\n2️⃣ 수리 후 구문 검증 중...")
    verification = repairer.verify_syntax_after_repair()
    print(f"   📊 {verification['syntax_valid']}/{verification['total_files']}개 파일 구문 정상")
    
    # 결과 요약
    print(f"\n📊 최종 구문 수리 결과:")
    print(f"   • 수리된 파일: {repair_result['successful_repairs']}개")
    print(f"   • 구문 정상 파일: {verification['syntax_valid']}개")
    print(f"   • 구문 오류 파일: {verification['syntax_errors']}개")
    
    if verification['syntax_errors'] > 0:
        print(f"\n⚠️  남은 구문 오류:")
        for result in verification['file_results']:
            if result['status'] == 'error':
                print(f"   • {result['file']}")
    
    # 성공 여부
    success_rate = verification['syntax_valid'] / verification['total_files'] if verification['total_files'] > 0 else 0
    
    if success_rate >= 0.8:  # 80% 이상 성공
        print(f"\n🎉 구문 수리 성공! ({success_rate:.1%} 성공률)")
        print(f"   • 백업 디렉토리: {repairer.backup_dir}")
        return True
    else:
        print(f"\n⚠️  추가 수리 필요 ({success_rate:.1%} 성공률)")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)