# 수리 도구 (Repair Tools)

POSCO 시스템의 다양한 오류를 자동으로 수리하는 도구들입니다.

## 주요 도구

### 구문 수리 도구
- `syntax_error_repairer.py` - 기본 구문 오류 수리
- `aggressive_syntax_repair.py` - 공격적 구문 수리 (주의 필요)
- `final_syntax_repair.py` - 최종 구문 수리
- `emergency_syntax_repair.py` - 응급 구문 수리
- `quick_syntax_fixer.py` - 빠른 구문 수정
- `indentation_fixer.py` - 들여쓰기 수정

### 파일 참조 수리 도구
- `file_reference_repairer.py` - 기본 파일 참조 수리
- `comprehensive_file_reference_repairer.py` - 종합 파일 참조 수리
- `critical_file_reference_fixer.py` - 중요 파일 참조 수정
- `focused_file_reference_repairer.py` - 집중 파일 참조 수리
- `refined_file_reference_repairer.py` - 정제된 파일 참조 수리

### 통합 수리 시스템
- `automated_repair_system.py` - 자동화된 수리 시스템
- `enhanced_automated_repair_system.py` - 향상된 자동 수리 시스템
- `comprehensive_error_repairer.py` - 종합 오류 수리
- `focused_integration_repair_system.py` - 집중 통합 수리 시스템

### CLI 도구
- `repair_cli.py` - 기본 수리 CLI
- `enhanced_repair_cli.py` - 향상된 수리 CLI

## 사용법

```bash
# 기본 구문 수리
python tools/repair/syntax_error_repairer.py

# 파일 참조 수리
python tools/repair/file_reference_repairer.py

# 자동화된 전체 수리
python tools/repair/automated_repair_system.py

# CLI를 통한 수리
python tools/repair/repair_cli.py --help
```

## 주의사항

⚠️ **중요**: 수리 도구 사용 전 반드시 백업을 생성하세요!

- `aggressive_syntax_repair.py`는 신중하게 사용하세요
- 수리 후 반드시 테스트를 실행하세요
- 중요한 파일은 수동으로 검토하세요