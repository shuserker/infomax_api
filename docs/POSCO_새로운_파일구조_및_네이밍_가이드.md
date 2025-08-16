# POSCO 시스템 새로운 파일 구조 및 네이밍 규칙 가이드

## 📋 개요

**문서 목적**: POSCO 시스템의 새로운 파일 구조와 표준화된 네이밍 규칙을 안내  
**적용 일자**: 2025년 8월 10일부터  
**대상 사용자**: 개발자, 시스템 관리자, 사용자  
**버전**: v1.0

## 🏗️ 새로운 파일 구조

### 루트 디렉토리 구조
```
infomax_api/
├── 🎛️ 제어센터 파일들/           # 시스템 제어 파일
├── 🐹 워치햄스터 파일들/          # WatchHamster 관련 파일
├── 🚀 실행 스크립트들/           # 직접 실행 스크립트
├── 📋 문서 및 가이드/            # 사용자 문서
├── 🔧 수리 및 도구/             # 자동화 도구
├── Monitoring/                  # 모니터링 시스템
├── docs/                       # 기술 문서
├── reports/                    # 보고서
├── migration_logs/             # 마이그레이션 로그
├── migration_reports/          # 마이그레이션 보고서
├── .kiro/                      # Kiro 설정
├── .git/                       # Git 저장소
└── [백업 디렉토리들]/           # 자동 생성 백업
```

### Monitoring 디렉토리 구조
```
Monitoring/
├── POSCO_News_250808/          # POSCO 뉴스 시스템 (날짜 기반)
│   ├── core/                   # 핵심 모듈
│   │   ├── __init__.py
│   │   ├── base_monitor.py
│   │   ├── business_day_helper.py
│   │   ├── colorful_ui.py
│   │   ├── completion_notifier.py
│   │   ├── enhanced_process_manager.py
│   │   ├── historical_data_collector.py
│   │   ├── integrated_report_builder.py
│   │   ├── integrated_report_generator.py
│   │   ├── integrated_report_scheduler.py
│   │   ├── metadata_manager.py
│   │   ├── metadata_reset_manager.py
│   │   ├── notification_manager.py
│   │   ├── performance_monitor.py
│   │   ├── performance_optimizer.py
│   │   ├── process_manager.py
│   │   ├── realtime_news_monitor.py
│   │   ├── report_cleanup_manager.py
│   │   ├── report_manager.py
│   │   ├── simple_news_monitor.py
│   │   ├── state_manager.py
│   │   └── watchhamster_integration.py
│   ├── config.py               # 설정 파일
│   ├── posco_main_notifier.py  # 메인 알림자
│   ├── posco_main_notifier_minimal.py  # 최소 기능 알림자
│   ├── monitor_WatchHamster_v3.0.py    # 워치햄스터 모니터
│   ├── monitor_WatchHamster_v3.0_minimal.py  # 최소 기능 모니터
│   └── [기타 Python 스크립트들]
│
├── WatchHamster_v3.0/          # WatchHamster 시스템 (v3.0)
│   ├── core/
│   │   ├── performance_monitor.py
│   │   └── performance_optimizer.py
│   ├── modules.json
│   └── README.md
│
├── docs/                       # 공통 문서
│   ├── reports_index.json
│   └── status.json
│
├── Posco_News_mini/           # 기존 폴더 (백업용 유지)
├── Posco_News_mini_v2/        # 기존 폴더 (백업용 유지)
└── FOLDER_STRUCTURE_GUIDE.md  # 구조 가이드
```

## 📝 네이밍 규칙 (Naming Conventions)

### 1. Python 파일 네이밍

#### 1.1 모듈 파일 (snake_case)
```python
# ✅ 올바른 예시
file_renaming_system.py
naming_convention_manager.py
python_naming_standardizer.py
shell_batch_script_standardizer.py
documentation_standardizer.py
config_data_standardizer.py
system_output_message_standardizer.py
folder_structure_reorganizer.py
naming_standardization_verification_system.py

# ❌ 잘못된 예시 (구버전)
Posco_News_mini.py
POSCO_WatchHamster_v3_Final_Summary.py
```

#### 1.2 메인 실행 파일 (PascalCase + 날짜/버전)
```python
# ✅ 올바른 예시
POSCO_News_250808.py           # POSCO 뉴스 (2025년 8월 8일 버전)
WatchHamster_v3.0_Monitor.py   # 워치햄스터 v3.0 모니터

# ❌ 잘못된 예시 (구버전)
Posco_News_mini.py
POSCO_WatchHamster_v3_Monitor.py
```

#### 1.3 테스트 파일 (test_ prefix)
```python
# ✅ 올바른 예시
test_automated_repair_system.py
test_file_renaming_system.py
test_naming_convention_manager.py
test_comprehensive_test_system.py

# ❌ 잘못된 예시
automated_repair_system_test.py
FileRenamingSystemTest.py
```

### 2. 스크립트 파일 네이밍

#### 2.1 Shell 스크립트 (.sh)
```bash
# ✅ 올바른 예시
watchhamster_v3.0_control_center.sh
watchhamster_v3.0_master_control.sh
posco_news_250808_control_mac.sh
migrate_to_v2.sh
run_migration_verification.sh

# ❌ 잘못된 예시
WatchHamster-v3.0-Control-Center.sh
POSCO_News_250808_Control_Mac.SH
```

#### 2.2 배치 파일 (.bat)
```batch
# ✅ 올바른 예시 (이모지 + 설명적 이름)
🐹POSCO_워치햄스터_v3_제어센터.bat
🎛️WatchHamster_v3.0_Control_Panel.bat
🚀🚀POSCO_News_250808_Direct_Start.bat
PowerShell_진단.bat

# ❌ 잘못된 예시
posco-watchhamster-v3-control-center.bat
WatchHamster_v3.0_Control_Panel.BAT
```

#### 2.3 PowerShell 스크립트 (.ps1)
```powershell
# ✅ 올바른 예시
watchhamster_v3.0_control_center.ps1
watchhamster_v3.0_master_control.ps1
lib_wt_common.ps1

# ❌ 잘못된 예시
WatchHamster-v3.0-Control-Center.ps1
LibWtCommon.ps1
```

### 3. 문서 파일 네이밍

#### 3.1 마크다운 문서 (.md)
```markdown
# ✅ 올바른 예시 (이모지 + 설명적 이름)
📋POSCO_워치햄스터_v2_사용자_가이드.md
🔧POSCO_워치햄스터_문제해결_가이드.md
🛠️POSCO_워치햄스터_개발자_가이드.md
🔄POSCO_워치햄스터_마이그레이션_가이드.md

# 기술 문서 (영문)
README.md
MIGRATION_README.md
END_TO_END_TEST_GUIDE.md
FILE_RENAMING_SYSTEM_GUIDE.md
NAMING_CONVENTION_SYSTEM_GUIDE.md
TEST_FRAMEWORK_README.md

# 보고서 (영문 + 날짜)
task8_final_integration_test_completion_report.md
task5_system_execution_verification_report.md
task4_final_completion_report.md

# ❌ 잘못된 예시
posco_watchhamster_v2_user_guide.md
POSCO-WatchHamster-v2-User-Guide.md
PoscoWatchHamsterV2UserGuide.md
```

#### 3.2 보고서 파일
```
# ✅ 올바른 예시
comprehensive_repair_report.md
system_optimization_report.md
final_integration_summary.md
deployment_verification_checklist.md

# JSON 보고서
enhanced_final_integration_test_results.json
comprehensive_system_execution_test_results.json
file_reference_validation_report.json

# ❌ 잘못된 예시
ComprehensiveRepairReport.md
system-optimization-report.md
FinalIntegrationSummary.MD
```

### 4. 설정 및 데이터 파일

#### 4.1 JSON 설정 파일
```json
# ✅ 올바른 예시
test_config.json
comprehensive_test_config.json
repair_config.json
posco_news_250808_data.json
posco_business_day_mapping.json

# ❌ 잘못된 예시
TestConfig.json
test-config.json
TEST_CONFIG.JSON
```

#### 4.2 로그 파일
```
# ✅ 올바른 예시
comprehensive_repair.log
WatchHamster_v3.0.log
migration_verification.log
naming_verification.log

# ❌ 잘못된 예시
ComprehensiveRepair.log
watchhamster-v3.0.log
MIGRATION_VERIFICATION.LOG
```

### 5. 백업 디렉토리 네이밍

#### 5.1 자동 생성 백업 디렉토리
```
# ✅ 올바른 예시
.repair_backups/
.enhanced_repair_backups/
.focused_file_reference_backup/
.final_file_reference_cleanup_backup/
.final_syntax_repair_backup/
.aggressive_syntax_repair_backup/

# ❌ 잘못된 예시
repair-backups/
RepairBackups/
REPAIR_BACKUPS/
```

#### 5.2 백업 파일 네이밍
```
# ✅ 올바른 예시 (원본파일명.backup_YYYYMMDD_HHMMSS)
naming_convention_manager.py.backup_20250810_175726
file_renaming_system.py.backup_20250809_182827
comprehensive_error_repairer.py.backup_20250810_175836

# ❌ 잘못된 예시
naming_convention_manager_backup.py
file_renaming_system.py.bak
comprehensive_error_repairer.py.old
```

## 🔄 버전 관리 규칙

### 1. 소프트웨어 버전 표기
```
# ✅ 올바른 예시
WatchHamster_v3.0          # 메이저.마이너 버전
POSCO_News_250808          # 날짜 기반 버전 (YYMMDD)
WatchHamster_v3.0_Final    # 버전 + 상태

# ❌ 잘못된 예시
WatchHamster_v3            # 마이너 버전 누락
POSCO_News_mini            # 버전 정보 없음
WatchHamster_version_3.0   # 불필요한 단어
```

### 2. 날짜 기반 버전 표기
```
# ✅ 올바른 예시
POSCO_News_250808          # 2025년 8월 8일
posco_news_250808_data.json
posco_news_250808_control_mac.sh

# ❌ 잘못된 예시
POSCO_News_20250808        # 4자리 연도
POSCO_News_08082025        # 미국식 날짜
POSCO_News_2025_08_08      # 구분자 사용
```

## 🎯 특수 파일 네이밍 규칙

### 1. 이모지 사용 규칙

#### 1.1 제어센터 파일 (🎛️, 🐹)
```
🎛️WatchHamster_v3.0_Control_Panel.bat      # 제어판
🐹POSCO_워치햄스터_v3_제어센터.bat           # 워치햄스터 제어센터
🐹WatchHamster_v3.0_Control_Center.bat      # 영문 제어센터
```

#### 1.2 실행 스크립트 (🚀)
```
🚀🚀POSCO_News_250808_Direct_Start.bat      # 직접 시작
🚀🚀POSCO_News_250808_Direct_Start.sh       # 직접 시작 (Shell)
```

#### 1.3 문서 파일 이모지
```
📋 - 사용자 가이드, 매뉴얼
🔧 - 문제해결, 트러블슈팅
🛠️ - 개발자 가이드, 기술 문서
🔄 - 마이그레이션, 업그레이드
🔍 - 검수, 검증 보고서
🔔 - 알림, 노티피케이션
🗂️ - 정리, 분류 가이드
🎨 - UI, 디자인 관련
```

### 2. 언어별 네이밍 규칙

#### 2.1 한글 파일명
```
# ✅ 올바른 예시 (언더스코어 사용)
📋POSCO_워치햄스터_v2_사용자_가이드.md
🔧POSCO_워치햄스터_문제해결_가이드.md
워치햄스터_시스템_재구축_완료_보고서_v4.md

# ❌ 잘못된 예시
POSCO 워치햄스터 v2 사용자 가이드.md      # 공백 사용
POSCO-워치햄스터-v2-사용자-가이드.md      # 하이픈 사용
```

#### 2.2 영문 파일명
```
# ✅ 올바른 예시 (snake_case 또는 PascalCase)
comprehensive_repair_report.md
WatchHamster_v3.0_Complete_Guide.md
AUTOMATED_REPAIR_SYSTEM_GUIDE.md

# ❌ 잘못된 예시
comprehensive-repair-report.md             # 하이픈 사용
Comprehensive Repair Report.md             # 공백 사용
comprehensiveRepairReport.md               # camelCase
```

## 🔍 파일 분류 체계

### 1. 기능별 분류

#### 1.1 시스템 핵심 파일
```
# 모니터링 시스템
POSCO_News_250808.py
monitor_WatchHamster_v3.0.py
posco_main_notifier.py

# 제어 시스템
🐹POSCO_워치햄스터_v3_제어센터.bat
🎛️WatchHamster_v3.0_Control_Panel.bat
watchhamster_v3.0_control_center.sh
```

#### 1.2 자동화 도구
```
# 수리 도구
automated_repair_system.py
enhanced_automated_repair_system.py
repair_cli.py
enhanced_repair_cli.py

# 표준화 도구
file_renaming_system.py
naming_convention_manager.py
python_naming_standardizer.py
```

#### 1.3 테스트 및 검증
```
# 테스트 시스템
comprehensive_test_system.py
enhanced_final_integration_test_system.py
system_functionality_verification.py

# 개별 테스트
test_automated_repair_system.py
test_file_renaming_system.py
test_naming_convention_manager.py
```

### 2. 상태별 분류

#### 2.1 프로덕션 파일 (Production)
```
# 메인 시스템
POSCO_News_250808.py                    # 프로덕션 뉴스 시스템
🐹POSCO_워치햄스터_v3_제어센터.bat        # 프로덕션 제어센터

# 안정화된 도구
file_renaming_system.py                 # 안정화된 파일 리네이밍
filename_standardizer.py                # 안정화된 파일명 표준화
```

#### 2.2 최소 기능 파일 (Minimal)
```
# 최소 기능 버전
posco_main_notifier_minimal.py          # 최소 기능 알림자
monitor_WatchHamster_v3.0_minimal.py    # 최소 기능 모니터
```

#### 2.3 개발/테스트 파일 (Development)
```
# 개발 중인 파일
enhanced_automated_repair_system.py     # 향상된 수리 시스템
comprehensive_test_system.py            # 종합 테스트 시스템

# 실험적 파일
aggressive_syntax_repair.py             # 공격적 구문 수리
focused_integration_repair_system.py    # 집중 통합 수리
```

## 📁 디렉토리 구조 모범 사례

### 1. 계층적 구조
```
프로젝트_루트/
├── 실행_파일들/              # 사용자가 직접 실행하는 파일
├── 핵심_모듈들/              # 시스템 핵심 기능
├── 도구_및_유틸리티/         # 개발 및 관리 도구
├── 테스트_및_검증/           # 테스트 관련 파일
├── 문서_및_가이드/           # 사용자 문서
├── 설정_및_데이터/           # 설정 파일 및 데이터
├── 로그_및_보고서/           # 로그 파일 및 보고서
└── 백업_및_히스토리/         # 백업 파일 및 히스토리
```

### 2. 기능별 그룹화
```
Monitoring/
├── POSCO_News_250808/        # POSCO 뉴스 관련 모든 파일
├── WatchHamster_v3.0/        # 워치햄스터 관련 모든 파일
├── docs/                     # 모니터링 관련 문서
└── reports/                  # 모니터링 보고서
```

## 🚀 마이그레이션 가이드

### 1. 기존 파일명에서 새 규칙으로 변경

#### 1.1 Python 파일 마이그레이션
```python
# 변경 전 → 변경 후
Posco_News_mini.py → POSCO_News_250808.py
POSCO_WatchHamster_v3_Final_Summary.py → WatchHamster_v3.0_Final_Summary.py
posco_main_notifier.py → posco_main_notifier.py (변경 없음 - 이미 올바름)
```

#### 1.2 문서 파일 마이그레이션
```markdown
# 변경 전 → 변경 후
POSCO_WatchHamster_v3_Complete_Guide.md → WatchHamster_v3.0_Complete_Guide.md
POSCO_WatchHamster_v3_CrossPlatform_Guide.md → WatchHamster_v3.0_CrossPlatform_Guide.md
```

### 2. 참조 업데이트 방법

#### 2.1 Import 구문 업데이트
```python
# 변경 전
from Posco_News_mini import *
import POSCO_WatchHamster_v3_Monitor

# 변경 후
from POSCO_News_250808 import *
import WatchHamster_v3.0_Monitor
```

#### 2.2 설정 파일 업데이트
```json
{
  "old_references": {
    "main_script": "Posco_News_mini.py",
    "monitor_script": "POSCO_WatchHamster_v3_Monitor.py"
  },
  "new_references": {
    "main_script": "POSCO_News_250808.py",
    "monitor_script": "WatchHamster_v3.0_Monitor.py"
  }
}
```

## 🔧 자동화 도구 활용

### 1. 파일명 표준화 도구
```bash
# 파일명 표준화 실행
python3 filename_standardizer.py

# 특정 디렉토리만 표준화
python3 filename_standardizer.py --directory Monitoring/

# 시뮬레이션 모드 (실제 변경 없이 미리보기)
python3 filename_standardizer.py --simulate
```

### 2. 참조 업데이트 도구
```bash
# 파일 참조 자동 업데이트
python3 file_reference_repairer.py

# 특정 파일 타입만 업데이트
python3 file_reference_repairer.py --file-types py,md,json

# 백업 생성 후 업데이트
python3 file_reference_repairer.py --create-backup
```

## ✅ 규칙 준수 체크리스트

### 새 파일 생성 시 확인사항
- [ ] 파일명이 해당 타입의 네이밍 규칙을 따르는가?
- [ ] 버전 정보가 올바르게 표기되었는가?
- [ ] 특수문자나 공백이 포함되지 않았는가?
- [ ] 이모지 사용이 적절한가? (해당하는 경우)
- [ ] 언어별 규칙을 준수했는가?

### 파일 수정 시 확인사항
- [ ] 파일명 변경 시 모든 참조를 업데이트했는가?
- [ ] Import 구문이 올바르게 수정되었는가?
- [ ] 설정 파일의 경로가 업데이트되었는가?
- [ ] 문서 내 파일명 참조가 수정되었는가?
- [ ] 백업이 생성되었는가?

### 디렉토리 구조 확인사항
- [ ] 파일이 적절한 디렉토리에 위치하는가?
- [ ] 기능별 그룹화가 올바른가?
- [ ] 계층 구조가 논리적인가?
- [ ] 백업 디렉토리가 적절히 분리되었는가?

## 🆘 문제 해결

### 자주 발생하는 문제들

#### 1. 파일명 변경 후 Import 오류
```python
# 문제: ModuleNotFoundError
# 해결: Import 경로 업데이트
from POSCO_News_250808 import main_function
```

#### 2. 경로 참조 오류
```python
# 문제: FileNotFoundError
# 해결: 상대 경로를 절대 경로로 변경
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
```

#### 3. 백업 파일 충돌
```bash
# 문제: 백업 파일명 중복
# 해결: 타임스탬프 확인 후 수동 정리
ls -la .repair_backups/ | grep "파일명"
```

## 📞 지원 및 문의

### 자동화 도구 사용 문의
- **파일명 표준화**: `filename_standardizer.py` 실행
- **참조 업데이트**: `file_reference_repairer.py` 실행
- **종합 수리**: `enhanced_repair_cli.py` 실행

### 수동 작업 가이드
- **네이밍 규칙 확인**: 이 문서의 해당 섹션 참조
- **디렉토리 구조**: 파일 분류 체계 섹션 참조
- **마이그레이션**: 마이그레이션 가이드 섹션 참조

---

**📅 문서 작성일**: 2025년 8월 10일  
**👨‍💻 작성자**: Kiro AI Assistant  
**📊 문서 버전**: v1.0  
**🔄 다음 업데이트**: 필요시 수시 업데이트  
**📞 지원**: 24/7 기술 지원 가능