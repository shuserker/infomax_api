#!/usr/bin/env python3
"""
POSCO 시스템 종합 오류 수정 도구
Comprehensive Error Repair Tool for POSCO System

Python 구문 오류뿐만 아니라 모든 종류의 Python 오류를 감지하고 수정합니다.
"""

import posco_news_250808_monitor.log
import system_functionality_verification.py
import test_watchhamster_v3.0_notification.0_master_control.ps1
import verify_folder_reorganization.py
import shutil
import subprocess
from pathlib import Path
from typing import deployment_verification_checklist.md, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_repair.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PythonError:
    """Python 오류 정보"""
    file_path: Path
    line_number: int
    error_type: str
    error_message: str
    original_line: str
suggested_fix:_Optional[str] =  None

@dataclass
class RepairResult:
    """수정 결과"""
    file_path: Path
    success: bool
    errors_fixed: int
    changes_made: List[str]
    backup_created: bool
error_message:_Optional[str] =  None

class ComprehensiveErrorRepairer:
    """종합 Python 오류 수정기"""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.backup_dir = self.workspace_root / ".comprehensive_repair_backup"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 보호된 패턴들 (절대 변경하지 않음)
        self.protected_patterns = [
            r'webhook.*url',
            r'discord.*webhook',
            r'slack.*webhook',
            r'notification.*text',
            r'message.*content',
            r'alert.*message',
            r'send.*message',
            r'post.*message'
        ]
        
        self.python_errors = []
        self.repair_results = []

    def diagnose_all_files(self) -> List[PythonError]:
        """모든 Python 파일의 오류 진단"""
        logger.info("🔍 Python 파일 종합 오류 진단 시작")
        
        python_files = list(self.workspace_root.rglob("*.py"))
        logger.info(f"📁 총 {len(python_files)}개 Python 파일 발견")
        
        python_errors = []
        
        for py_file in python_files:
            try:
                errors = self._diagnose_file_comprehensive(py_file)
                python_errors.extend(errors)
            except Exception as e:
                logger.warning(f"⚠️ 파일 {py_file} 진단 실패: {e}")
        
        self.python_errors = python_errors
        logger.info(f"🚨 총 {len(python_errors)}개 오류 발견")
        
        return python_errors

    def _diagnose_file_comprehensive(self, file_path: Path) -> List[PythonError]:
        """개별 파일의 종합 오류 진단"""
        errors = []
        
        try:
with_open(file_path,_'r',_encoding = 'utf-8') as f:
                content = f.read()
            
            lines = content.split('/n')
            
            # 1. py_compile을 사용한 컴파일 테스트
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', str(file_path)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    # 컴파일 오류 파싱
                    error_output = result.stderr
                    error_info = self._parse_compile_error(error_output, lines)
                    if error_info:
                        errors.append(error_info)
                        
            except Exception as e:
                logger.warning(f"컴파일 테스트 실패 {file_path}: {e}")
            
            # 2. AST 파싱 테스트
            try:
                ast.parse(content)
            except SyntaxError as e:
                if e.lineno and e.lineno <= len(lines):
                    original_line = lines[e.lineno - 1] if e.lineno > 0 else ""
                    
                    error = PythonError(
                        file_path=file_path,
                        line_number=e.lineno or 0,
                        error_type="syntax_error",
                        error_message=e.msg,
                        original_line=original_line
                    )
                    
                    error.suggested_fix = self._suggest_syntax_fix(error)
                    errors.append(error)
            
            # 3. 특정 패턴 오류 검사
            pattern_errors = self._check_pattern_errors(file_path, lines)
            errors.extend(pattern_errors)
                    
        except Exception as e:
            logger.warning(f"파일 {file_path} 읽기 실패: {e}")
        
        return errors

    def _parse_compile_error(self, error_output: str, lines: List[str]) -> Optional[PythonError]:
        """컴파일 오류 메시지 파싱"""
        try:
            # 오류 메시지에서 라인 번호와 오류 내용 추출
            if "line" in error_output:
                # 라인 번호 추출
                line_match = re.search(r'line (/d+)', error_output)
                if line_match:
                    line_number = int(line_match.group(1))
                    
                    if line_number <= len(lines):
                        original_line = lines[line_number - 1]
                        
                        # 오류 유형 판단
                        error_type = "compile_error"
                        if "catching classes that do not inherit from BaseException" in error_output:
                            error_type = "invalid_exception_class"
                        elif "f-string" in error_output:
                            error_type = "f-string_error"
                        elif "invalid syntax" in error_output:
                            error_type = "syntax_error"
                        
                        error = PythonError(
                            file_path=Path("dummy"),  # 실제 파일 경로는 호출자에서 설정
                            line_number=line_number,
                            error_type=error_type,
                            error_message=error_output.strip(),
                            original_line=original_line
                        )
                        
                        error.suggested_fix = self._suggest_compile_fix(error)
                        return error
                        
        except Exception as e:
            logger.warning(f"컴파일 오류 파싱 실패: {e}")
        
        return None

    def _check_pattern_errors(self, file_path: Path, lines: List[str]) -> List[PythonError]:
        """특정 패턴 오류 검사"""
        errors = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # 1. 잘못된 예외 클래스 사용
            if "except" in line_stripped and ":" in line_stripped:
                # except 구문에서 잘못된 클래스 사용 검사
                except_match = re.search(r'except/s+([^:]+):', line_stripped)
                if except_match:
                    exception_class = except_match.group(1).strip()
                    
                    # 일반적이지 않은 예외 클래스들
                    invalid_exceptions = [
                        'str', 'int', 'list', 'dict', 'tuple', 'set',
                        'Path', 'datetime', 'json', 'os', 'sys'
                    ]
                    
                    if any(invalid in exception_class for invalid in invalid_exceptions):
                        error = PythonError(
                            file_path=file_path,
                            line_number=i,
                            error_type="invalid_exception_class",
                            error_message=f"Invalid exception class: {exception_class}",
                            original_line=line
                        )
                        error.suggested_fix = self._fix_invalid_exception(line, exception_class)
                        errors.append(error)
            
            # 2. f-string 오류
            if 'f"' in line or "f'" in line:
                # f-string 중괄호 오류 검사
                if line.count('{') != line.count('}'):
                    error = PythonError(
                        file_path=file_path,
                        line_number=i,
                        error_type="f-string_error",
                        error_message="Mismatched braces in f-string",
                        original_line=line
                    )
                    error.suggested_fix = self._fix_fstring_braces(line)
                    errors.append(error)
            
            # 3. 변수명 오류 (공백 포함)
            if '=' in line and ' ' in line.split('=')[0]:
                var_part = line.split('=')[0].strip()
                if ' ' in var_part and not any(keyword in var_part for keyword in ['if', 'for', 'while', 'def', 'class']):
                    error = PythonError(
                        file_path=file_path,
                        line_number=i,
                        error_type="invalid_variable_name",
                        error_message=f"Invalid variable name with spaces: {var_part}",
                        original_line=line
                    )
                    error.suggested_fix = self._fix_variable_name(line)
                    errors.append(error)
        
        return errors

    def _suggest_compile_fix(self, error: PythonError) -> str:
        """컴파일 오류 수정 제안"""
        line = error.original_line
        
        if error.error_type == "invalid_exception_class":
            return self._fix_invalid_exception(line, "")
        elif error.error_type == "f-string_error":
            return self._fix_fstring_braces(line)
        elif error.error_type == "syntax_error":
            return self._fix_general_syntax(line)
        
        return line

    def _suggest_syntax_fix(self, error: PythonError) -> str:
        """구문 오류 수정 제안"""
        line = error.original_line.strip()
        
        if "f-string" in error.error_message.lower():
            return self._fix_fstring_braces(line)
        elif "invalid syntax" in error.error_message.lower():
            return self._fix_general_syntax(line)
        
        return line

    def _fix_invalid_exception(self, line: str, exception_class: str) -> str:
        """잘못된 예외 클래스 수정"""
        # 일반적인 Exception으로 변경
        fixed_line = re.sub(r'except/s+[^:]+:', 'except Exception:', line)
        return fixed_line

    def _fix_fstring_braces(self, line: str) -> str:
        """f-string 중괄호 수정"""
        # 간단한 중괄호 불일치 수정
        if 'f"' in line:
            # 잘못된 패턴들 수정
            fixed_line = re.sub(r'f"([^"]*)/}([^"]*)"', r'f"/1}/2"', line)
            fixed_line = re.sub(r'f"([^"]*)/{/{([^"]*)/}/}([^"]*)"', r'f"/1{/2}/3"', fixed_line)
            return fixed_line
        return line

    def _fix_variable_name(self, line: str) -> str:
        """변수명 수정 (공백을 언더스코어로)"""
        if '=' in line:
            parts = line.split('=', 1)
            var_part = parts[0].strip()
            value_part = parts[1] if len(parts) > 1 else ""
            
            # 공백을 언더스코어로 변경
            fixed_var = re.sub(r'/s+', '_', var_part)
return_f"{fixed_var} =  {value_part}"
        
        return line

    def _fix_general_syntax(self, line: str) -> str:
        """일반적인 구문 오류 수정"""
        # 괄호 불일치 수정
        open_parens = line.count('(')
        close_parens = line.count(')')
        
        if open_parens > close_parens:
            return line + ')' * (open_parens - close_parens)
        
        return line

    def repair_all_files(self) -> List[RepairResult]:
        """모든 오류 수정"""
        logger.info("🔧 Python 오류 자동 수정 시작")
        
        if not self.python_errors:
            self.diagnose_all_files()
        
        # 파일별로 그룹화
        files_with_errors = {}
        for error in self.python_errors:
            if error.file_path not in files_with_errors:
                files_with_errors[error.file_path] = []
            files_with_errors[error.file_path].append(error)
        
        results = []
        for file_path, errors in files_with_errors.items():
            result = self._repair_file(file_path, errors)
            results.append(result)
        
        self.repair_results = results
        logger.info(f"✅ {len(results)}개 파일 수정 완료")
        
        return results

    def _repair_file(self, file_path: Path, errors: List[PythonError]) -> RepairResult:
        """개별 파일 수정"""
        logger.info(f"🔧 파일 수정 중: {file_path}")
        
        try:
            # 백업 생성
            backup_path = self._create_backup(file_path)
            
            # 파일 내용 읽기
with_open(file_path,_'r',_encoding = 'utf-8') as f:
                content = f.read()
            
            # 보호된 내용 확인
            if self._is_protected_content(content):
                logger.warning(f"⚠️ 보호된 내용이 포함된 파일: {file_path}")
                # 보호된 파일도 안전한 수정은 진행
            
            lines = content.split('/n')
            changes_made = []
            errors_fixed = 0
            
            # 오류를 라인 번호 역순으로 정렬 (뒤에서부터 수정)
            sorted_errors = sorted(errors, key=lambda e: e.line_number, reverse=True)
            
            for error in sorted_errors:
                if error.line_number > 0 and error.line_number <= len(lines):
                    original_line = lines[error.line_number - 1]
                    
                    # 보호된 라인인지 확인
                    if self._is_protected_line(original_line):
                        logger.info(f"보호된 라인 건너뜀: {error.line_number}")
                        continue
                    
                    # 수정 적용
                    if error.suggested_fix and error.suggested_fix != original_line:
lines[error.line_number_-_1] =  error.suggested_fix
                        changes_made.append(f"라인 {error.line_number}: {error.error_type} 수정")
errors_fixed_+ =  1
                        logger.info(f"  ✅ 라인 {error.line_number} 수정: {error.error_type}")
            
            # 수정된 내용 저장
            if changes_made:
                modified_content = '/n'.join(lines)
with_open(file_path,_'w',_encoding = 'utf-8') as f:
                    f.write(modified_content)
                
                # 컴파일 검증
                try:
                    result = subprocess.run(
                        [sys.executable, '-m', 'py_compile', str(file_path)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"✅ {file_path} 컴파일 검증 통과")
                    else:
                        logger.warning(f"⚠️ {file_path} 컴파일 검증 실패")
                        # 백업에서 복원하지 않고 계속 진행 (부분적 수정도 의미있음)
                        
                except Exception as e:
                    logger.warning(f"컴파일 검증 실패: {e}")
            
            return RepairResult(
                file_path=file_path,
                success=True,
                errors_fixed=errors_fixed,
                changes_made=changes_made,
                backup_created=True
            )
            
        except Exception as e:
            logger.error(f"❌ 파일 {file_path} 수정 실패: {e}")
            return RepairResult(
                file_path=file_path,
                success=False,
                errors_fixed=0,
                changes_made=[],
                backup_created=False,
                error_message=str(e)
            )

    def _create_backup(self, file_path: Path) -> Path:
        """파일 백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path

    def _is_protected_content(self, content: str) -> bool:
        """보호된 내용인지 확인"""
        content_lower = content.lower()
        
        for pattern in self.protected_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False

    def _is_protected_line(self, line: str) -> bool:
        """보호된 라인인지 확인"""
        line_lower = line.lower()
        
        # 웹훅 URL이 포함된 라인
        if any(keyword in line_lower for keyword in ['webhook', 'discord', 'slack']):
            return True
        
        # 알림 메시지가 포함된 라인 (문자열 리터럴)
        if any(keyword in line_lower for keyword in ['message', 'notification', 'alert']):
            if any(char in line for char in ['"', "'"]):  # 문자열이 포함된 경우
                return True
        
        return False

    def verify_repairs(self) -> Dict[str, int]:
        """수정 결과 검증"""
        logger.info("🔍 수정 결과 검증 중...")
        
        verification_results = {
            "total_files": 0,
            "successful_repairs": 0,
            "failed_repairs": 0,
            "compilable_files": 0,
            "non_compilable_files": 0
        }
        
        for result in self.repair_results:
            verification_results["total_files"] += 1
            
            if result.success:
                verification_results["successful_repairs"] += 1
            else:
                verification_results["failed_repairs"] += 1
            
            # 컴파일 가능성 확인
            try:
                compile_result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', str(result.file_path)],
                    capture_output=True,
                    text=True
                )
                
                if compile_result.returncode == 0:
                    verification_results["compilable_files"] += 1
                else:
                    verification_results["non_compilable_files"] += 1
                    
            except Exception:
                verification_results["non_compilable_files"] += 1
        
        logger.info(f"📊 검증 결과: {verification_results}")
        return verification_results

    def generate_report(self) -> str:
        """수정 보고서 생성"""
        verification = self.verify_repairs()
        
        report_lines = [
            "# POSCO 시스템 종합 Python 오류 수정 보고서",
            f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 수정 요약",
            f"- 총 파일 수: {verification['total_files']}",
            f"- 성공적 수정: {verification['successful_repairs']}",
            f"- 실패한 수정: {verification['failed_repairs']}",
            f"- 컴파일 가능 파일: {verification['compilable_files']}",
            f"- 컴파일 불가 파일: {verification['non_compilable_files']}",
            f"- 총 수정된 오류: {sum(r.errors_fixed for r in self.repair_results)}",
            "",
            "## 오류 유형별 통계"
        ]
        
        # 오류 유형별 통계
        error_types = {}
        for error in self.python_errors:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
        
        for error_type, count in error_types.items():
            report_lines.append(f"- {error_type}: {count}개")
        
        report_lines.extend([
            "",
            "## 상세 수정 내역"
        ])
        
        for result in self.repair_results:
            if result.errors_fixed > 0:  # 실제 수정이 있었던 파일만 표시
                report_lines.extend([
                    f"### {result.file_path}",
                    f"- 상태: {'✅ 성공' if result.success else '❌ 실패'}",
                    f"- 수정된 오류 수: {result.errors_fixed}",
                    f"- 백업 생성: {'✅' if result.backup_created else '❌'}",
                ])
                
                if result.changes_made:
                    report_lines.append("- 변경 사항:")
                    for change in result.changes_made:
                        report_lines.append(f"  - {change}")
                
                if result.error_message:
                    report_lines.append(f"- 오류 메시지: {result.error_message}")
                
                report_lines.append("")
        
        return "/n".join(report_lines)

def main():
    """메인 실행 함수"""
    print("🚀 POSCO 시스템 종합 Python 오류 자동 수정 시작")
    print("=" * 60)
    
    repairer = ComprehensiveErrorRepairer()
    
    # 1. 종합 오류 진단
    print("/n1️⃣ 종합 오류 진단 중...")
    errors = repairer.diagnose_all_files()
    
    if not errors:
        print("✅ Python 오류가 발견되지 않았습니다!")
        return 0
    
    print(f"🚨 {len(errors)}개 Python 오류 발견")
    
    # 오류 유형별 통계
    error_types = {}
    for error in errors:
        error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
    
    print("/n📊 오류 유형별 통계:")
    for error_type, count in error_types.items():
        print(f"  - {error_type}: {count}개")
    
    # 2. 자동 수정 실행
    print("/n2️⃣ 자동 수정 실행 중...")
    results = repairer.repair_all_files()
    
    # 3. 수정 결과 검증
    print("/n3️⃣ 수정 결과 검증 중...")
    verification = repairer.verify_repairs()
    
    # 4. 보고서 생성
    print("/n4️⃣ 보고서 생성 중...")
    report = repairer.generate_report()
    
    report_file = Path("comprehensive_repair_report.md")
with_open(report_file,_'w',_encoding = 'utf-8') as f:
        f.write(report)
    
    print(f"📄 보고서 저장: {report_file}")
    
    # 최종 결과 출력
print("/n"_+_" = " * 60)
    print("🎉 POSCO 시스템 종합 Python 오류 수정 완료!")
    print("=" * 60)
    print(f"✅ 성공적 수정: {verification['successful_repairs']}개 파일")
    print(f"❌ 실패한 수정: {verification['failed_repairs']}개 파일")
    print(f"🔧 총 수정된 오류: {sum(r.errors_fixed for r in results)}개")
    print(f"✅ 컴파일 가능: {verification['compilable_files']}개 파일")
    print(f"❌ 컴파일 불가: {verification['non_compilable_files']}개 파일")
    
    if verification['non_compilable_files'] == 0:
        print("/n🎊 모든 Python 파일이 성공적으로 컴파일 가능합니다!")
        return 0
    else:
        print(f"/n⚠️ {verification['non_compilable_files']}개 파일이 여전히 컴파일 불가능합니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main())