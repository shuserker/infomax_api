# POSCO 시스템 자동화된 수리 도구 가이드

## 개요

POSCO 시스템의 Python 구문 오류, Import 문제, 파일 참조 오류를 자동으로 감지하고 수정하는 통합 도구입니다.

## 주요 기능

### 1. 구문 오류 자동 감지 및 수정
- Python AST 파싱을 통한 구문 오류 감지
- f-string 구문 오류 수정
- 괄호 불일치 수정
- 들여쓰기 오류 수정 (탭 → 4칸 스페이스)
- 변수명 네이밍 규칙 적용

### 2. Import 문제 자동 해결
- 존재하지 않는 모듈 참조 감지
- 순환 import 문제 해결
- 누락된 import 자동 추가
- Import 경로 표준화

### 3. 파일 참조 자동 복구
- 깨진 파일 참조 감지
- 파일명 변경에 따른 참조 업데이트
- 경로 구분자 표준화 (\ → /)
- 레거시 파일명 표준화

### 4. 백업 및 롤백 시스템
- 수정 전 자동 백업 생성
- 파일별 백업 히스토리 관리
- 실패 시 자동 롤백
- 백업 파일 정리 기능

## 사용 방법

### 기본 CLI 도구

#### 1. 시스템 상태 확인
```bash
python3 repair_cli.py status
```

#### 2. 시스템 진단
```bash
# 기본 진단
python3 repair_cli.py diagnose

# 상세 진단
python3 repair_cli.py diagnose --detailed

# 보고서 저장
python3 repair_cli.py diagnose --save-report
```

#### 3. 자동 수리 실행
```bash
# 기본 수리 (확인 후 실행)
python3 repair_cli.py repair

# 강제 실행 (확인 없이)
python3 repair_cli.py repair --force

# 진단 건너뛰고 수리
python3 repair_cli.py repair --skip-diagnosis
```

#### 4. 수리 결과 검증
```bash
# 기본 검증
python3 repair_cli.py verify

# 상세 검증
python3 repair_cli.py verify --detailed
```

#### 5. 파일 롤백
```bash
python3 repair_cli.py rollback <파일경로>
```

### 향상된 CLI 도구

#### 1. 시스템 분석
```bash
# 기본 분석
python3 enhanced_repair_cli.py analyze

# 상세 분석
python3 enhanced_repair_cli.py analyze --detailed

# 보고서 저장
python3 enhanced_repair_cli.py analyze --save-report
```

#### 2. 향상된 수리 실행
```bash
# 기본 수리 (최대 20개 파일)
python3 enhanced_repair_cli.py repair

# 더 많은 파일 수리
python3 enhanced_repair_cli.py repair --max-files 50

# 강제 실행
python3 enhanced_repair_cli.py repair --force
```

#### 3. 시스템 상태 확인
```bash
python3 enhanced_repair_cli.py status
```

#### 4. 백업 파일 정리
```bash
# 확인 후 정리
python3 enhanced_repair_cli.py clean

# 강제 정리
python3 enhanced_repair_cli.py clean --force
```

### Python API 사용

#### 기본 수리 시스템
```python
from automated_repair_system import AutomatedRepairSystem

# 수리 시스템 초기화
repair_system = AutomatedRepairSystem()

# 전체 진단
diagnosis_results = repair_system.run_full_diagnosis()

# 자동 수리
repair_results = repair_system.run_automated_repair()

# 수리 검증
verification_results = repair_system.verify_repairs()
```

#### 향상된 수리 시스템
```python
from enhanced_automated_repair_system import EnhancedAutomatedRepairSystem

# 향상된 수리 시스템 초기화
repair_system = EnhancedAutomatedRepairSystem()

# 시스템 분석
analysis_results = repair_system.analyze_system()

# 수리 실행 (최대 30개 파일)
execution_results = repair_system.execute_repairs(max_files=30)

# 검증
verification_results = repair_system.verify_repairs()
```

## 설정 파일

### repair_config.json
수리 시스템의 동작을 제어하는 설정 파일입니다.

```json
{
  "repair_settings": {
    "syntax_repair": {
      "enabled": true,
      "fix_indentation": true,
      "fix_fstring_errors": true,
      "fix_bracket_mismatches": true,
      "standardize_naming": true,
      "indentation_spaces": 4
    },
    "import_repair": {
      "enabled": true,
      "add_missing_imports": true,
      "fix_import_paths": true,
      "remove_unused_imports": false
    },
    "file_reference_repair": {
      "enabled": true,
      "fix_broken_references": true,
      "standardize_path_separators": true,
      "update_legacy_names": true
    }
  },
  "file_mappings": {
    "legacy_to_standard": {
      "Posco_News_mini.py": "POSCO_News_250808.py",
      "POSCO_WatchHamster_v3": "WatchHamster_v3.0"
    }
  },
  "backup_settings": {
    "create_backups": true,
    "backup_directory": ".repair_backups",
    "max_backup_age_days": 30
  }
}
```

## 수리 작업 유형

### 1. 구문 오류 수정 (Syntax Repair)
- **f-string 오류**: `f"text {var}}"` → `f"text {var}"`
- **괄호 불일치**: `function(arg1, arg2` → `function(arg1, arg2)`
- **들여쓰기**: 탭을 4칸 스페이스로 변환
- **네이밍**: `POSCO News 250808` → `POSCO_NEWS_250808`

### 2. Import 문제 해결 (Import Repair)
- **경로 수정**: `from Posco_News_mini` → `from POSCO_News_250808`
- **누락 import**: `os.path` 사용 시 `import os` 자동 추가
- **순환 import**: 공통 모듈 분리 또는 지연 import

### 3. 파일 참조 복구 (Reference Repair)
- **파일명 변경**: `Posco_News_mini.py` → `POSCO_News_250808.py`
- **경로 표준화**: `path\to\file` → `path/to/file`
- **깨진 링크**: 유사한 파일로 자동 매핑

## 백업 시스템

### 백업 디렉토리
- **기본 시스템**: `.repair_backups/`
- **향상된 시스템**: `.enhanced_repair_backups/`

### 백업 파일 명명 규칙
```
원본파일명.backup_YYYYMMDD_HHMMSS
```

### 백업 관리
- 파일당 최대 5개 백업 유지
- 30일 이상 된 백업 자동 삭제
- 백업 히스토리 JSON 파일로 관리

## 보고서 및 로그

### 진단 보고서
```json
{
  "timestamp": "2025-08-10T17:30:00",
  "syntax_errors": [
    {
      "file_path": "example.py",
      "error_type": "SyntaxError",
      "line_number": 10,
      "error_message": "invalid syntax"
    }
  ],
  "import_problems": [
    "example.py: nonexistent_module"
  ],
  "broken_references": [
    {
      "source_file": "example.py",
      "referenced_path": "missing_file.txt",
      "line_number": 5
    }
  ]
}
```

### 수리 결과 보고서
```json
{
  "timestamp": "2025-08-10T17:35:00",
  "total_files_processed": 20,
  "successful_repairs": 18,
  "failed_repairs": 2,
  "total_execution_time": 45.2,
  "overall_success_rate": 90.0
}
```

## 성능 최적화

### 처리 제한
- **파일 크기**: 10MB 이하만 처리
- **동시 처리**: 최대 4개 프로세스
- **타임아웃**: 파일당 60초 제한
- **메모리**: 512MB 제한

### 제외 패턴
```
.git/**
__pycache__/**
*.pyc
.backup/**
node_modules/**
.vscode/**
```

## 안전장치

### 수정 전 검증
- 파일 크기 확인
- 백업 생성 확인
- 구문 유효성 검사

### 수정 후 검증
- AST 파싱 성공 확인
- Import 가능성 확인
- 파일 참조 유효성 확인

### 롤백 조건
- 구문 오류 발생 시
- Import 실패 시
- 사용자 요청 시

## 문제 해결

### 일반적인 문제

#### 1. 백업 생성 실패
```bash
# 권한 확인
ls -la .repair_backups/

# 디스크 공간 확인
df -h

# 수동 백업 디렉토리 생성
mkdir -p .repair_backups
```

#### 2. 구문 오류 수정 실패
```bash
# 수동 구문 검사
python3 -m py_compile 파일명.py

# 상세 오류 확인
python3 repair_cli.py diagnose --detailed
```

#### 3. Import 문제 지속
```bash
# Python 경로 확인
python3 -c "import sys; print(sys.path)"

# 모듈 존재 확인
python3 -c "import 모듈명"
```

### 로그 확인
```bash
# 수리 로그 확인
tail -f repair_system.log

# 백업 히스토리 확인
cat .repair_backups/backup_history.json
```

## 고급 사용법

### 커스텀 수리 규칙
```python
# 커스텀 패턴 추가
repair_system.syntax_repairer.common_fixes.update({
    r'old_pattern': 'new_replacement'
})

# 커스텀 파일 매핑 추가
repair_system.reference_repairer.reference_mappings.update({
    'old_file.py': 'new_file.py'
})
```

### 배치 처리
```python
# 특정 디렉토리만 처리
repair_system = AutomatedRepairSystem()
for py_file in Path("specific_dir").glob("**/*.py"):
    result = repair_system.syntax_repairer.repair_file(py_file)
    print(f"{py_file}: {result.success}")
```

### 통계 수집
```python
# 수리 통계 수집
stats = {
    'total_files': 0,
    'syntax_fixes': 0,
    'import_fixes': 0,
    'reference_fixes': 0
}

for result in repair_system.repair_results:
    stats['total_files'] += 1
    if 'syntax' in result.repair_type.lower():
        stats['syntax_fixes'] += 1
    # ... 기타 통계
```

## 테스트

### 단위 테스트 실행
```bash
python3 test_automated_repair_system.py
```

### 통합 테스트 실행
```bash
python3 -m pytest test_automated_repair_system.py -v
```

### 성능 테스트
```bash
time python3 enhanced_automated_repair_system.py
```

## 기여 가이드

### 새로운 수리 규칙 추가
1. `EnhancedSyntaxRepairer` 클래스에 새 메서드 추가
2. `common_fixes` 딕셔너리에 패턴 추가
3. 테스트 케이스 작성
4. 문서 업데이트

### 새로운 진단 기능 추가
1. 해당 `Diagnostic` 클래스에 메서드 추가
2. 결과 데이터 클래스 정의
3. CLI 인터페이스 업데이트
4. 테스트 및 문서 작성

## 라이선스

이 도구는 POSCO 시스템 전용으로 개발되었습니다.

## 지원

문제 발생 시 다음 정보와 함께 문의하세요:
- 오류 메시지
- 수리 대상 파일
- 시스템 환경 (OS, Python 버전)
- 수리 로그 파일