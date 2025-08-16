# 원본 로직 추출 요약 보고서

## 추출 정보
- **대상 커밋**: a763ef84be08b5b1dab0c0ba20594b141baec7ab
- **추출 시간**: 2025-08-12T13:15:09.817865
- **총 파일 수**: 268개
- **핵심 파일 수**: 46개

## 분석 결과

### Python 모듈 (16개)

#### temp_config
- **파일 경로**: Monitoring/Posco_News_mini/config.py
- **함수 수**: 0개
- **클래스 수**: 0개
- **의존성**: 0개

#### temp_state_manager
- **파일 경로**: Monitoring/Posco_News_mini/core/state_manager.py
- **함수 수**: 0개
- **클래스 수**: 1개
- **의존성**: 5개
- **클래스**:
  - `StateManager` (메서드 11개)

#### temp_integrated_report_builder
- **파일 경로**: Monitoring/Posco_News_mini/integrated_report_builder.py
- **함수 수**: 1개
- **클래스 수**: 1개
- **의존성**: 7개
- **주요 함수**:
  - `main()`
- **클래스**:
  - `IntegratedReportBuilder` (메서드 9개)

#### temp_integrated_report_scheduler
- **파일 경로**: Monitoring/Posco_News_mini/integrated_report_scheduler.py
- **함수 수**: 1개
- **클래스 수**: 1개
- **의존성**: 13개
- **주요 함수**:
  - `main()`
- **클래스**:
  - `IntegratedReportScheduler` (메서드 7개)

#### temp_metadata_reset_manager
- **파일 경로**: Monitoring/Posco_News_mini/metadata_reset_manager.py
- **함수 수**: 1개
- **클래스 수**: 1개
- **의존성**: 8개
- **주요 함수**:
  - `main()`
- **클래스**:
  - `MetadataResetManager` (메서드 13개)

#### temp_posco_report_system_reset
- **파일 경로**: Monitoring/Posco_News_mini/posco_report_system_reset.py
- **함수 수**: 1개
- **클래스 수**: 1개
- **의존성**: 13개
- **주요 함수**:
  - `main()`
- **클래스**:
  - `PoscoReportSystemReset` (메서드 9개)

#### temp_report_cleanup_manager
- **파일 경로**: Monitoring/Posco_News_mini/report_cleanup_manager.py
- **함수 수**: 1개
- **클래스 수**: 1개
- **의존성**: 7개
- **주요 함수**:
  - `main()`
- **클래스**:
  - `ReportCleanupManager` (메서드 7개)

#### temp_report_manager
- **파일 경로**: Monitoring/Posco_News_mini/reports/report_manager.py
- **함수 수**: 0개
- **클래스 수**: 1개
- **의존성**: 4개
- **클래스**:
  - `ReportManager` (메서드 6개)

#### temp___init__
- **파일 경로**: Monitoring/Posco_News_mini/utils/__init__.py
- **함수 수**: 0개
- **클래스 수**: 0개
- **의존성**: 0개

#### temp_business_day_helper
- **파일 경로**: Monitoring/Posco_News_mini/utils/business_day_helper.py
- **함수 수**: 0개
- **클래스 수**: 1개
- **의존성**: 6개
- **클래스**:
  - `BusinessDayHelper` (메서드 6개)

#### temp___init__
- **파일 경로**: Monitoring/Posco_News_mini_v2/core/__init__.py
- **함수 수**: 0개
- **클래스 수**: 0개
- **의존성**: 3개

#### temp_enhanced_process_manager
- **파일 경로**: Monitoring/Posco_News_mini_v2/core/enhanced_process_manager.py
- **함수 수**: 0개
- **클래스 수**: 3개
- **의존성**: 11개
- **클래스**:
  - `ProcessStatus` (메서드 0개)
  - `ProcessInfo` (메서드 0개)
  - `ProcessManager` (메서드 13개)

#### temp_performance_optimizer
- **파일 경로**: Monitoring/Posco_News_mini_v2/core/performance_optimizer.py
- **함수 수**: 0개
- **클래스 수**: 5개
- **의존성**: 9개
- **클래스**:
  - `OptimizationCategory` (메서드 0개)
  - `OptimizationPriority` (메서드 0개)
  - `OptimizationRecommendation` (메서드 0개)
  - `PerformanceIssue` (메서드 0개)
  - `PerformanceOptimizer` (메서드 11개)

#### temp_demo_performance_monitoring
- **파일 경로**: demo_performance_monitoring.py
- **함수 수**: 3개
- **클래스 수**: 0개
- **의존성**: 7개
- **주요 함수**:
  - `print_header(title)`
  - `print_section(title)`
  - `demo_performance_monitoring()`

#### temp_posco_continuous_monitor
- **파일 경로**: posco_continuous_monitor.py
- **함수 수**: 1개
- **클래스 수**: 1개
- **의존성**: 6개
- **주요 함수**:
  - `main()`
- **클래스**:
  - `PoscoContinuousMonitor` (메서드 5개)

#### temp_posco_news_viewer
- **파일 경로**: posco_news_viewer.py
- **함수 수**: 1개
- **클래스 수**: 0개
- **의존성**: 3개
- **주요 함수**:
  - `generate_html_report()`


### 설정 파일 (15개)

#### settings.json
- **타입**: json
- **변수 수**: 6개
- **경로**: .vscode/settings.json

#### config.py
- **타입**: python
- **변수 수**: 7개
- **경로**: Monitoring/Posco_News_mini/config.py

#### modules.json
- **타입**: json
- **변수 수**: 91개
- **경로**: Monitoring/Posco_News_mini_v2/modules.json

#### reports_index.json
- **타입**: json
- **변수 수**: 3개
- **경로**: Monitoring/docs/reports_index.json

#### status.json
- **타입**: json
- **변수 수**: 37개
- **경로**: Monitoring/docs/status.json

#### reports_index.json
- **타입**: json
- **변수 수**: 3개
- **경로**: docs/reports_index.json

#### status.json
- **타입**: json
- **변수 수**: 37개
- **경로**: docs/status.json

#### optimization_history.json
- **타입**: json
- **변수 수**: 9개
- **경로**: optimization_history.json

#### performance_data_20250808_105531.json
- **타입**: json
- **변수 수**: 54개
- **경로**: performance_data_20250808_105531.json

#### performance_data_20250808_112257.json
- **타입**: json
- **변수 수**: 54개
- **경로**: performance_data_20250808_112257.json

#### posco_business_day_mapping.json
- **타입**: json
- **변수 수**: 105개
- **경로**: posco_business_day_mapping.json

#### posco_news_cache.json
- **타입**: json
- **변수 수**: 0개
- **경로**: posco_news_cache.json

#### posco_news_historical_cache.json
- **타입**: json
- **변수 수**: 0개
- **경로**: posco_news_historical_cache.json

#### reports_index.json
- **타입**: json
- **변수 수**: 7개
- **경로**: reports_index.json

#### system_optimization_data.json
- **타입**: json
- **변수 수**: 42개
- **경로**: system_optimization_data.json


### 스크립트 파일 (13개)

#### posco_control_center.sh
- **타입**: .sh
- **명령어 수**: 58개
- **변수 수**: 4개

#### check_migration_requirements.sh
- **타입**: .sh
- **명령어 수**: 33개
- **변수 수**: 17개

#### cleanup_old_files.sh
- **타입**: .sh
- **명령어 수**: 30개
- **변수 수**: 9개

#### lib_wt_common.bat
- **타입**: .bat
- **명령어 수**: 88개
- **변수 수**: 43개

#### lib_wt_common.sh
- **타입**: .sh
- **명령어 수**: 61개
- **변수 수**: 31개

#### migrate_to_v2.sh
- **타입**: .sh
- **명령어 수**: 38개
- **변수 수**: 12개

#### rollback_migration.sh
- **타입**: .sh
- **명령어 수**: 31개
- **변수 수**: 8개

#### run_migration_verification.sh
- **타입**: .sh
- **명령어 수**: 89개
- **변수 수**: 18개

#### test_control_center_functions.sh
- **타입**: .sh
- **명령어 수**: 28개
- **변수 수**: 7개

#### test_runner.sh
- **타입**: .sh
- **명령어 수**: 37개
- **변수 수**: 10개

#### verify_task6_implementation.sh
- **타입**: .sh
- **명령어 수**: 37개
- **변수 수**: 1개

#### watchhamster_control_center.sh
- **타입**: .sh
- **명령어 수**: 117개
- **변수 수**: 10개

#### watchhamster_master_control.sh
- **타입**: .sh
- **명령어 수**: 141개
- **변수 수**: 2개


### 의존성 분석
- **총 모듈 수**: 16개
- **외부 의존성**: 35개
- **내부 연결**: 0개
- **순환 의존성**: 0개

#### 외부 의존성 목록
- completion_notifier
- config
- core
- dataclasses
- datetime
- enhanced_process_manager
- enum
- exchange_monitor
- hashlib
- integrated_report_builder
- json
- kospi_monitor
- legacy_system_disabler
- logging
- metadata_reset_manager
- module_registry
- newyork_monitor
- notification_manager
- os
- pathlib
- psutil
- re
- report_cleanup_manager
- reports
- requests
- schedule
- shutil
- signal
- statistics
- subprocess
- sys
- threading
- time
- traceback
- typing


## 파일 구조 분석
- **디렉토리 수**: 34개
- **파일 타입별 분포**:
  - .bat: 1개
  - .bat": 17개
  - .command": 1개
  - .css: 1개
  - .db: 1개
  - .html: 28개
  - .ipynb": 3개
  - .jpg: 1개
  - .js: 13개
  - .json: 24개
  - .log: 4개
  - .md: 40개
  - .md": 42개
  - .ps1: 3개
  - .py: 61개
  - .pyc: 2개
  - .sh: 13개
  - .sh": 2개
  - .txt: 5개


## 다음 단계
1. 추출된 로직을 기반으로 핵심 모듈 복원
2. 설정 파일들을 현재 환경에 맞게 조정
3. 의존성 문제 해결
4. 통합 테스트 실행

---
*이 보고서는 자동으로 생성되었습니다.*
