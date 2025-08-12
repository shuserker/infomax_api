# 🔄 POSCO 네이밍 컨벤션 표준화 마이그레이션 가이드

## 📋 개요

이 문서는 POSCO 프로젝트의 기존 네이밍 체계에서 새로운 표준화된 네이밍 컨벤션으로의 안전한 마이그레이션을 위한 종합 가이드입니다.

### 🎯 마이그레이션 목표
- **WatchHamster**: 모든 관련 파일을 `v3.0` 형식으로 통일
- **POSCO News**: 모든 관련 파일을 `250808` 형식으로 통일
- **일관성 확보**: 프로젝트 전체의 네이밍 일관성 달성
- **기능 보존**: 모든 기존 기능의 완전한 보존

### ⚠️ 중요 원칙
- **내용 보존**: 파일명, 폴더명, 변수명, 주석만 변경
- **로직 보존**: 모든 코드 로직과 알고리즘은 그대로 유지
- **기능 보존**: 변경 후에도 모든 기능이 동일하게 작동
- **데이터 호환성**: 기존 데이터 파일과의 완전한 호환성 보장

## 🚀 빠른 시작 가이드

### 1단계: 사전 준비
```bash
# 1. 전체 프로젝트 백업
cp -r . ../posco_project_backup_$(date +%Y%m%d_%H%M%S)

# 2. 현재 상태 분석
python3 posco_file_renamer.py --analyze

# 3. 시뮬레이션 실행 (안전 확인)
python3 posco_file_renamer.py --dry-run
```

### 2단계: 단계별 마이그레이션
```bash
# 1. WatchHamster 파일들 먼저 변경
python3 posco_file_renamer.py --watchhamster

# 2. POSCO News 파일들 변경
python3 posco_file_renamer.py --posco-news

# 3. 전체 검증
python3 naming_standardization_verification_system.py
```

### 3단계: 시스템 테스트
```bash
# 1. 기본 기능 테스트
./🐹WatchHamster_v3.0_Control_Center.bat

# 2. POSCO News 시스템 테스트
./Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/🚀🚀POSCO_News_250808_Start.bat

# 3. 통합 테스트
python3 run_end_to_end_tests.py
```

## 📊 변경 사항 매핑 테이블

### WatchHamster 관련 파일 변경 (v3.0)

#### 제어센터 및 실행 파일
| 기존 파일명 | 새로운 파일명 | 설명 |
|------------|-------------|------|
| `🐹워치햄스터_총괄_관리_센터_v3.bat` | `🐹WatchHamster_v3.0_Control_Center.bat` | 메인 제어센터 |
| `🐹워치햄스터_통합_관리_센터.bat` | `🐹WatchHamster_v3.0_Integrated_Center.bat` | 통합 관리센터 |
| `🎛️POSCO_제어센터_실행_v2.bat` | `🎛️WatchHamster_v3.0_Control_Panel.bat` | 제어판 |
| `🎛️POSCO_제어센터_Mac실행.command` | `🎛️WatchHamster_v3.0_Control_Panel.command` | Mac용 제어판 |

#### Python 스크립트
| 기존 파일명 | 새로운 파일명 | 설명 |
|------------|-------------|------|
| `demo_v2_integration.py` | `demo_watchhamster_v3.0_integration.py` | 통합 데모 |
| `test_v2_integration.py` | `test_watchhamster_v3.0_integration.py` | 통합 테스트 |
| `test_v2_notification_integration.py` | `test_watchhamster_v3.0_notification_integration.py` | 알림 테스트 |
| `monitor_WatchHamster.py` | `monitor_WatchHamster_v3.0.py` | 메인 모니터 |

#### 폴더 구조
| 기존 폴더명 | 새로운 폴더명 | 설명 |
|------------|-------------|------|
| `Monitoring/Posco_News_mini_v2/` | `Monitoring/WatchHamster_v3.0/` | WatchHamster 코어 |
| `.kiro/specs/posco-watchhamster-v2-integration/` | `.kiro/specs/watchhamster-v3.0-integration/` | 스펙 폴더 |

#### 문서 파일
| 기존 파일명 | 새로운 파일명 | 설명 |
|------------|-------------|------|
| `📋POSCO_워치햄스터_v2_사용자_가이드.md` | `📋POSCO_워치햄스터_v3.0_사용자_가이드.md` | 사용자 가이드 |
| `📋POSCO_워치햄스터_v2_프로젝트_완료_보고서.md` | `📋POSCO_워치햄스터_v3.0_프로젝트_완료_보고서.md` | 완료 보고서 |
| `🔍POSCO_워치햄스터_v2_전체_재검수_보고서.md` | `🔍POSCO_워치햄스터_v3.0_전체_재검수_보고서.md` | 재검수 보고서 |

### POSCO News 관련 파일 변경 (250808)

#### 메인 스크립트
| 기존 파일명 | 새로운 파일명 | 설명 |
|------------|-------------|------|
| `Posco_News_mini.py` | `POSCO_News_250808.py` | 메인 스크립트 |
| `posco_main_notifier.py` | `posco_news_250808_notifier.py` | 메인 알림기 |
| `posco_continuous_monitor.py` | `posco_news_250808_monitor.py` | 연속 모니터 |

#### 데이터 파일
| 기존 파일명 | 새로운 파일명 | 설명 |
|------------|-------------|------|
| `posco_news_data.json` | `posco_news_250808_data.json` | 뉴스 데이터 |
| `posco_news_cache.json` | `posco_news_250808_cache.json` | 캐시 데이터 |
| `posco_news_historical_cache.json` | `posco_news_250808_historical.json` | 히스토리 데이터 |

#### 폴더 구조
| 기존 폴더명 | 새로운 폴더명 | 설명 |
|------------|-------------|------|
| `Monitoring/Posco_News_mini/` | `Monitoring/POSCO_News_250808/` | POSCO News 메인 |

## 🛠️ 마이그레이션 도구 사용법

### 1. 네이밍 컨벤션 매니저
```python
# BROKEN_REF: from naming_convention_manager.py.py import NamingConventionManager

# 매니저 초기화
manager = NamingConventionManager()

# 파일명 표준화 확인
# BROKEN_REF: result = manager.standardize_filename("demo_v2_integration.py")
print(f"{result.original} → {result.converted}")
# 출력: demo_v2_integration.py → demo_watchhamster_v3.0_integration.py

# 컴포넌트 타입 확인
component = manager.detect_component_type(".naming_backup/config_data_backup/watchhamster.log")
print(f"컴포넌트: {component}")  # ComponentType.WATCHHAMSTER
```

### 2. 파일 리네이밍 시스템
```bash
# 현재 상태 분석
python3 posco_file_renamer.py --analyze

# 시뮬레이션 (드라이 런)
python3 posco_file_renamer.py --dry-run

# WatchHamster 파일만 변경
python3 posco_file_renamer.py --watchhamster

# POSCO News 파일만 변경
python3 posco_file_renamer.py --posco-news

# 모든 파일 변경
python3 posco_file_renamer.py --all

# 변경 사항 롤백
python3 posco_file_renamer.py --rollback
```

### 3. 검증 시스템
```bash
# 네이밍 표준화 검증
python3 naming_standardization_verification_system.py

# 전체 시스템 검증
python3 final_system_integration_verification.py
```

## 🔧 코드 내부 변경 사항

### Python 클래스명 변경
```python
# 기존
class PoscoMonitorWatchHamster:
    pass

class EnhancedProcessManager:
    pass

# 새로운
class WatchHamsterV30Monitor:
    pass

class WatchHamsterV30ProcessManager:
    pass
```

### 변수명 및 상수 변경
```python
# 기존
WATCHHAMSTER_VERSION = "v2.0"
posco_news_version = "mini_v2"

# 새로운
WATCHHAMSTER_VERSION = "v3.0"
POSCO_NEWS_VERSION = "250808"
```

### 주석 및 문서 변경
```python
# 기존
"""
POSCO WatchHamster v2.0 Integration
워치햄스터 v2 통합 시스템
"""

# 새로운
"""
POSCO WatchHamster v3.0 Integration
워치햄스터 v3.0 통합 시스템
POSCO News 250808 호환
"""
```

## 🛡️ 안전 장치 및 백업

### 자동 백업 시스템
모든 마이그레이션 작업 전에 자동으로 백업이 생성됩니다:

```
.naming_backup/
├── mapping_table.json              # 파일 매핑 테이블
├── operations_log.json             # 작업 로그
├── config_data_backup/             # 설정 데이터 백업
│   ├── posco_news_250808_data.json
│   ├── posco_news_250808_cache.json
│   └── ...
└── scripts/                        # 스크립트 백업
    ├── 🐹POSCO_워치햄스터_v3_제어센터.bat
    ├── 🎛️POSCO_제어센터_실행_v2.bat
    └── ...
```

### 롤백 기능
문제 발생 시 언제든지 이전 상태로 복원할 수 있습니다:

```bash
# 전체 롤백
python3 posco_file_renamer.py --rollback

# 특정 작업만 롤백 (프로그래밍 방식)
# BROKEN_REF: from file_renaming_system.py.py import FileRenamingSystem
system = FileRenamingSystem(".")
system.rollback_operations(operation_id="specific_operation_id")
```

### 검증 및 테스트
```bash
# 네이밍 일관성 검증
python3 naming_standardization_verification_system.py

# 시스템 기능 테스트
python3 run_end_to_end_tests.py

# 성능 테스트
python3 test_performance_monitoring.py
```

## 🚨 문제 해결 가이드

### 일반적인 문제들

#### 1. 파일이 사용 중인 경우
**증상**: `[Errno 16] Device or resource busy`
**해결방법**:
```bash
# 1. 실행 중인 프로세스 확인
ps aux | grep python | grep posco

# 2. 프로세스 종료
pkill -f "posco_main_notifier"
pkill -f "monitor_WatchHamster"

# 3. 재시도
python3 posco_file_renamer.py --watchhamster
```

#### 2. 권한 문제
**증상**: `[Errno 13] Permission denied`
**해결방법**:
```bash
# 1. 파일 권한 확인
ls -la *.bat *.py

# 2. 권한 수정
chmod +x *.sh
chmod 644 *.py *.json

# 3. 관리자 권한으로 실행 (필요시)
sudo python3 posco_file_renamer.py --all
```

#### 3. 백업 공간 부족
**증상**: `No space left on device`
**해결방법**:
```bash
# 1. 디스크 사용량 확인
df -h

# 2. 불필요한 파일 정리
rm -rf __pycache__/
rm -f *.log.old

# 3. 백업 디렉토리 정리
rm -rf .naming_backup/old_backups/
```

#### 4. 네이밍 컨벤션 감지 실패
**증상**: `Unknown component type`
**해결방법**:
```python
# 1. 컴포넌트 감지 확인
# BROKEN_REF: from naming_convention_manager.py.py import NamingConventionManager
manager = NamingConventionManager()
component = manager.detect_component_type("your_filename")
print(f"감지된 컴포넌트: {component}")

# 2. 수동으로 컴포넌트 지정
result = manager.standardize_filename("your_filename", force_component="watchhamster")
```

### 로그 확인 방법
```bash
# 시스템 로그 확인
tail -f file_renaming.log

# 작업 로그 확인
cat .naming_backup/operations_log.json | jq '.'

# 검증 로그 확인
tail -f naming_verification.log
```

### 복구 절차
```bash
# 1. 백업에서 복구
cp .naming_backup/config_data_backup/* .

# 2. 스크립트 복구
cp .naming_backup/scripts/* .

# 3. 시스템 재시작
./🐹WatchHamster_v3.0_Control_Center.bat
```

## 📈 마이그레이션 후 검증

### 1. 파일명 일관성 검증
```bash
# 네이밍 표준화 검증 실행
python3 naming_standardization_verification_system.py

# 검증 보고서 확인
cat naming_verification_report_*.html
```

### 2. 시스템 기능 테스트
```bash
# WatchHamster 기능 테스트
python3 test_watchhamster_v3.0_integration.py

# POSCO News 기능 테스트
python3 test_end_to_end_integration.py

# 성능 모니터링 테스트
python3 test_performance_monitoring.py
```

### 3. 사용자 인터페이스 확인
```bash
# 제어센터 실행 테스트
./🐹WatchHamster_v3.0_Control_Center.bat

# POSCO News 시작 테스트
./Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/🚀🚀POSCO_News_250808_Start.bat

# Mac 환경 테스트
./WatchHamster_v3.0.log
```

## 📚 새로운 네이밍 컨벤션 사용법

### 파일 생성 시 네이밍 규칙

#### WatchHamster 관련 파일
```bash
# Python 스크립트
new_watchhamster_v3.0_feature.py

# 배치 파일
🐹WatchHamster_v3.0_New_Feature.bat

# 설정 파일
watchhamster_v3.0_config.json

# 문서 파일
📋WatchHamster_v3.0_Feature_Guide.md
```

#### POSCO News 관련 파일
```bash
# Python 스크립트
posco_news_250808_new_feature.py

# 데이터 파일
posco_news_250808_new_data.json

# 문서 파일
📋POSCO_News_250808_Feature_Guide.md
```

### 코드 작성 시 네이밍 규칙

#### 클래스명
```python
# WatchHamster 관련
class WatchHamsterV30NewFeature:
    pass

# POSCO News 관련
class PoscoNews250808NewFeature:
    pass
```

#### 변수명
```python
# WatchHamster 관련
watchhamster_v3_0_config = {}
WATCHHAMSTER_V3_0_VERSION = "v3.0"

# POSCO News 관련
posco_news_250808_data = {}
POSCO_NEWS_250808_VERSION = "250808"
```

#### 함수명
```python
# WatchHamster 관련
def initialize_watchhamster_v3_0():
    pass

# POSCO News 관련
def start_posco_news_250808_monitor():
    pass
```

## 🔄 지속적인 유지보수

### 정기 검증
```bash
# 월간 네이밍 일관성 검증
python3 naming_standardization_verification_system.py --monthly-check

# 분기별 전체 시스템 검증
python3 final_system_integration_verification.py --quarterly-check
```

### 새로운 파일 추가 시
```bash
# 새 파일의 네이밍 검증
# BROKEN_REF: python3 naming_convention_manager.py --validate-new-file "new_file.py"

# 자동 네이밍 제안
# BROKEN_REF: python3 naming_convention_manager.py --suggest-name "my_new_feature.py"
```

### 문서 업데이트
- 새로운 기능 추가 시 관련 문서의 버전 정보 업데이트
- 사용자 가이드의 파일명 및 경로 정보 최신화
- API 문서의 클래스명 및 함수명 업데이트

## 📞 지원 및 문의

### 로그 수집 (문제 발생 시)
```bash
# 시스템 정보 수집
uname -a > debug_info.txt
python3 --version >> debug_info.txt

# 프로세스 상태 수집
ps aux | grep python | grep posco >> debug_info.txt

# 로그 파일 수집
tar -czf debug_logs.tar.gz \
    file_renaming.log \
    naming_verification.log \
    .naming_backup/operations_log.json \
    WatchHamster_v3.0.log
```

### 연락처
- **개발팀**: POSCO WatchHamster Development Team
- **문서 버전**: v3.0
- **최종 업데이트**: 2025-08-08

---

## 📋 체크리스트

### 마이그레이션 전 체크리스트
- [ ] 전체 프로젝트 백업 완료
- [ ] 현재 실행 중인 프로세스 종료
- [ ] 디스크 공간 충분 확인 (최소 1GB)
- [ ] 시뮬레이션 실행 및 결과 확인
- [ ] 중요 데이터 파일 별도 백업

### 마이그레이션 중 체크리스트
- [ ] WatchHamster 파일 변경 완료
- [ ] POSCO News 파일 변경 완료
- [ ] 폴더 구조 재구성 완료
- [ ] 코드 내부 네이밍 업데이트 완료
- [ ] 문서 및 주석 표준화 완료

### 마이그레이션 후 체크리스트
- [ ] 네이밍 일관성 검증 통과
- [ ] WatchHamster 기능 테스트 통과
- [ ] POSCO News 기능 테스트 통과
- [ ] 사용자 인터페이스 정상 동작 확인
- [ ] 성능 테스트 통과
- [ ] 문서 업데이트 완료

---

**⚠️ 중요**: 이 마이그레이션은 파일명, 폴더명, 변수명, 주석만 변경하며, 모든 기존 기능과 데이터는 완전히 보존됩니다. 안전한 마이그레이션을 위해 반드시 백업을 생성하고 시뮬레이션을 먼저 실행하세요.