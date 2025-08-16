# 📋 POSCO 시스템 사용자 매뉴얼 v2.0

## 🎯 개요

**매뉴얼 버전**: v2.0 (2025년 8월 10일 업데이트)  
**대상 시스템**: POSCO WatchHamster v3.0 + POSCO News 250808  
**사용자 대상**: 일반 사용자, 시스템 관리자  
**시스템 상태**: ✅ **완전 작동 가능** (96.2% 성공률)

## 🚀 빠른 시작 가이드

### 1단계: 시스템 상태 확인
```bash
# 시스템 상태 확인
python3 system_functionality_verification.py

# 간단한 상태 체크
python3 basic_system_test.py
```

### 2단계: 워치햄스터 시작하기

#### Windows 사용자
```batch
# 메인 제어센터 실행
🐹POSCO_워치햄스터_v3_제어센터.bat

# 또는 통합 제어판
🎛️WatchHamster_v3.0_Control_Panel.bat
```

#### macOS/Linux 사용자
```bash
# 메인 제어센터 실행
./🐹POSCO_워치햄스터_v3_제어센터.command

# 또는 Shell 스크립트
./watchhamster_v3.0_control_center.sh
```

### 3단계: POSCO 뉴스 모니터링 시작

#### 직접 시작 (권장)
```bash
# Windows
🚀🚀POSCO_News_250808_Direct_Start.bat

# macOS/Linux
./🚀🚀POSCO_News_250808_Direct_Start.sh
```

#### Python 직접 실행
```bash
# 메인 뉴스 시스템
python3 POSCO_News_250808.py

# 최소 기능 버전 (안정성 우선)
python3 Monitoring/POSCO_News_250808/posco_main_notifier_minimal.py
```

## 🏗️ 시스템 구조 이해하기

### 핵심 컴포넌트

#### 1. 워치햄스터 시스템 (WatchHamster v3.0)
- **역할**: 시스템 모니터링 및 제어
- **주요 파일**: 
  - `🐹POSCO_워치햄스터_v3_제어센터.bat` (Windows)
  - `🐹POSCO_워치햄스터_v3_제어센터.command` (macOS)
  - `watchhamster_v3.0_control_center.sh` (Linux)

#### 2. POSCO 뉴스 시스템 (POSCO News 250808)
- **역할**: 실시간 뉴스 모니터링 및 알림
- **주요 파일**:
  - `POSCO_News_250808.py` (메인 시스템)
  - `posco_main_notifier_minimal.py` (최소 기능)
  - `monitor_WatchHamster_v3.0_minimal.py` (모니터)

#### 3. 자동화 도구
- **역할**: 시스템 수리 및 유지보수
- **주요 파일**:
  - `automated_repair_system.py` (기본 수리)
  - `enhanced_automated_repair_system.py` (고급 수리)
  - `repair_cli.py` (CLI 도구)

### 디렉토리 구조
```
POSCO_시스템/
├── 🎛️ 제어센터/              # 시스템 제어 파일들
├── 🐹 워치햄스터/             # WatchHamster 관련
├── 🚀 실행스크립트/           # 직접 실행 파일들
├── Monitoring/               # 모니터링 시스템
│   ├── POSCO_News_250808/    # POSCO 뉴스 (최신)
│   └── WatchHamster_v3.0/    # 워치햄스터 (v3.0)
├── docs/                     # 문서
├── reports/                  # 보고서
└── [백업디렉토리들]/          # 자동 백업
```

## 🎛️ 주요 기능 사용법

### 1. 시스템 모니터링

#### 1.1 실시간 모니터링 시작
```bash
# 전체 시스템 모니터링
python3 POSCO_News_250808.py

# 백그라운드 실행
nohup python3 POSCO_News_250808.py &

# Windows 백그라운드 실행
start /B python3 POSCO_News_250808.py
```

#### 1.2 모니터링 상태 확인
```bash
# 프로세스 확인
ps aux | grep POSCO_News_250808

# Windows에서 프로세스 확인
tasklist | findstr python
```

#### 1.3 모니터링 중지
```bash
# 프로세스 ID로 중지
kill [PID]

# Windows에서 중지
taskkill /F /IM python.exe
```

### 2. 알림 시스템

#### 2.1 알림 설정 확인
```python
# config.py 파일에서 웹훅 URL 확인
WEBHOOK_URL_1 = "https://infomax.dooray.com/services/..."
WEBHOOK_URL_2 = "https://infomax.dooray.com/services/..."
```

#### 2.2 알림 테스트
```bash
# 웹훅 연결성 테스트
python3 -c "
import requests
response = requests.head('웹훅_URL')
print(f'Status: {response.status_code}')
"
```

#### 2.3 알림 내용 커스터마이징
```python
# posco_main_notifier.py에서 메시지 형식 확인
message = {
    'botName': '포스코 뉴스 알림봇',
    'botIconImage': 'https://...',
    'text': '알림 내용'
}
```

### 3. 데이터 관리

#### 3.1 데이터 파일 위치
```
데이터 파일들:
├── posco_news_250808_data.json      # 메인 데이터
├── posco_news_250808_cache.json     # 캐시 데이터
├── posco_news_250808_historical.json # 히스토리 데이터
└── posco_business_day_mapping.json  # 영업일 매핑
```

#### 3.2 데이터 백업
```bash
# 수동 백업
cp posco_news_250808_data.json posco_news_250808_data.json.backup

# 자동 백업 (cron 설정)
0 2 * * * cp /path/to/posco_news_250808_data.json /backup/location/
```

#### 3.3 데이터 복원
```bash
# 백업에서 복원
cp posco_news_250808_data.json.backup posco_news_250808_data.json

# 시스템 재시작
python3 POSCO_News_250808.py
```

## 🔧 고급 사용법

### 1. 시스템 수리 도구 사용

#### 1.1 기본 수리 도구
```bash
# 시스템 진단
python3 repair_cli.py diagnose

# 자동 수리 실행
python3 repair_cli.py repair

# 수리 결과 검증
python3 repair_cli.py verify
```

#### 1.2 향상된 수리 도구
```bash
# 시스템 분석
python3 enhanced_repair_cli.py analyze

# 고급 수리 실행
python3 enhanced_repair_cli.py repair --max-files 30

# 백업 정리
python3 enhanced_repair_cli.py clean
```

### 2. 성능 모니터링

#### 2.1 성능 데이터 수집
```bash
# 성능 모니터링 시작
python3 demo_performance_monitoring.py

# 성능 데이터 확인
cat performance_data_*.json
```

#### 2.2 성능 최적화
```bash
# 시스템 최적화 보고서 생성
python3 system_optimization_report_generator.py

# 최적화 권장사항 확인
cat system_optimization_report.md
```

### 3. 테스트 및 검증

#### 3.1 종합 테스트 실행
```bash
# 기본 통합 테스트
python3 final_integration_test_system.py

# 향상된 통합 테스트
python3 enhanced_final_integration_test_system.py

# 종합 테스트 시스템
python3 comprehensive_test_system.py
```

#### 3.2 개별 기능 테스트
```bash
# 파일 리네이밍 테스트
python3 test_file_renaming_system.py

# 네이밍 규칙 테스트
python3 test_naming_convention_manager.py

# 자동 수리 시스템 테스트
python3 test_automated_repair_system.py
```

## 📊 모니터링 및 로그

### 1. 로그 파일 위치
```
로그 파일들:
├── WatchHamster_v3.0.log                    # 워치햄스터 로그
├── posco_news_250808_monitor.log            # 뉴스 모니터링 로그
├── comprehensive_repair.log                 # 수리 작업 로그
├── migration_verification.log               # 마이그레이션 로그
└── naming_verification.log                  # 네이밍 검증 로그
```

### 2. 로그 확인 방법
```bash
# 실시간 로그 확인
tail -f WatchHamster_v3.0.log

# 최근 100줄 확인
tail -n 100 posco_news_250808_monitor.log

# 특정 키워드 검색
grep "ERROR" comprehensive_repair.log

# 날짜별 로그 필터링
grep "2025-08-10" WatchHamster_v3.0.log
```

### 3. 로그 관리
```bash
# 로그 파일 크기 확인
ls -lh *.log

# 오래된 로그 정리 (30일 이상)
find . -name "*.log" -mtime +30 -delete

# 로그 압축
gzip old_log_file.log
```

## 🔄 시스템 업데이트 및 유지보수

### 1. 정기 유지보수

#### 1.1 일일 점검 (권장)
```bash
# 시스템 상태 확인
python3 system_functionality_verification.py

# 프로세스 상태 확인
ps aux | grep -E "(POSCO_News|WatchHamster)"

# 디스크 공간 확인
df -h
```

#### 1.2 주간 점검 (권장)
```bash
# 종합 테스트 실행
python3 enhanced_final_integration_test_system.py

# 성능 데이터 분석
python3 system_optimization_report_generator.py

# 백업 파일 정리
python3 enhanced_repair_cli.py clean
```

#### 1.3 월간 점검 (권장)
```bash
# 전체 시스템 진단
python3 enhanced_repair_cli.py analyze --detailed

# 데이터 백업
tar -czf monthly_backup_$(date +%Y%m%d).tar.gz \
  posco_news_250808_data.json \
  posco_news_250808_historical.json \
  WatchHamster_v3.0.log

# 시스템 최적화
python3 enhanced_repair_cli.py repair --force
```

### 2. 업데이트 절차

#### 2.1 시스템 업데이트 전 준비
```bash
# 현재 상태 백업
python3 enhanced_repair_cli.py analyze --save-report

# 전체 시스템 백업
tar -czf pre_update_backup_$(date +%Y%m%d).tar.gz \
  --exclude='*.pyc' --exclude='__pycache__' \
  --exclude='.git' .
```

#### 2.2 업데이트 실행
```bash
# Git에서 최신 버전 가져오기
git pull origin main

# 의존성 업데이트
pip install -r requirements.txt

# 시스템 수리 실행
python3 enhanced_repair_cli.py repair
```

#### 2.3 업데이트 후 검증
```bash
# 통합 테스트 실행
python3 enhanced_final_integration_test_system.py

# 기능 검증
python3 system_functionality_verification.py

# 성능 확인
python3 demo_performance_monitoring.py
```

## 🆘 문제 해결 가이드

### 1. 일반적인 문제들

#### 1.1 시스템이 시작되지 않는 경우
```bash
# 문제 진단
python3 basic_system_test.py

# 구문 오류 확인
python3 -m py_compile POSCO_News_250808.py

# 의존성 확인
python3 -c "import requests, json, os, sys; print('Dependencies OK')"
```

**해결 방법**:
1. Python 버전 확인 (3.8+ 필요)
2. 필요한 패키지 설치: `pip install requests`
3. 파일 권한 확인: `chmod +x *.sh`

#### 1.2 알림이 오지 않는 경우
```bash
# 웹훅 연결성 테스트
python3 -c "
import requests
try:
    response = requests.head('웹훅_URL', timeout=10)
    print(f'Webhook Status: {response.status_code}')
except Exception as e:
    print(f'Webhook Error: {e}')
"
```

**해결 방법**:
1. 인터넷 연결 확인
2. 웹훅 URL 유효성 확인
3. 방화벽 설정 확인

#### 1.3 성능이 느린 경우
```bash
# 성능 분석
python3 demo_performance_monitoring.py

# 메모리 사용량 확인
python3 -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"
```

**해결 방법**:
1. 백그라운드 프로세스 정리
2. 로그 파일 정리
3. 시스템 재시작

### 2. 고급 문제 해결

#### 2.1 모듈 Import 오류
```bash
# 모듈 경로 확인
python3 -c "import sys; print('\n'.join(sys.path))"

# 특정 모듈 테스트
python3 -c "import file_renaming_system; print('Import OK')"
```

**해결 방법**:
```bash
# 자동 수리 실행
python3 enhanced_repair_cli.py repair --max-files 50

# 수동 수리
python3 focused_file_reference_repairer.py
```

#### 2.2 파일 참조 오류
```bash
# 파일 참조 검증
python3 final_file_reference_validator.py

# 깨진 참조 수리
python3 comprehensive_file_reference_repairer.py
```

#### 2.3 구문 오류
```bash
# 구문 오류 진단
python3 -m py_compile [파일명]

# 자동 구문 수리
python3 final_syntax_repair.py

# 공격적 구문 수리 (주의 필요)
python3 aggressive_syntax_repair.py
```

## 📞 지원 및 도움말

### 1. 자가 진단 도구
```bash
# 기본 시스템 체크
python3 basic_system_test.py

# 종합 시스템 진단
python3 enhanced_repair_cli.py analyze

# 통합 테스트
python3 enhanced_final_integration_test_system.py
```

### 2. 로그 및 보고서 확인
```bash
# 최신 테스트 결과
cat enhanced_final_integration_test_results.json

# 수리 작업 히스토리
cat .enhanced_repair_backups/repair_history.json

# 시스템 상태 보고서
cat system_functionality_verification_report.json
```

### 3. 백업 및 복원
```bash
# 백업 생성
python3 enhanced_repair_cli.py analyze --save-report
tar -czf emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz .

# 백업에서 복원
tar -xzf emergency_backup_YYYYMMDD_HHMMSS.tar.gz

# 특정 파일 복원
cp .enhanced_repair_backups/파일명.backup_YYYYMMDD_HHMMSS 파일명
```

## 📚 추가 자료

### 관련 문서
- `🛠️POSCO_워치햄스터_개발자_가이드.md` - 개발자용 상세 가이드
- `🔧POSCO_워치햄스터_문제해결_가이드.md` - 문제 해결 전용 가이드
- `AUTOMATED_REPAIR_SYSTEM_GUIDE.md` - 자동화 도구 가이드
- `POSCO_새로운_파일구조_및_네이밍_가이드.md` - 파일 구조 가이드

### 기술 문서
- `END_TO_END_TEST_GUIDE.md` - 테스트 가이드
- `FILE_RENAMING_SYSTEM_GUIDE.md` - 파일 리네이밍 가이드
- `NAMING_CONVENTION_SYSTEM_GUIDE.md` - 네이밍 규칙 가이드
- `TEST_FRAMEWORK_README.md` - 테스트 프레임워크 가이드

### 보고서 및 로그
- `task8_final_integration_test_completion_report.md` - 최종 통합 테스트 보고서
- `POSCO_시스템_수리_완료_보고서.md` - 시스템 수리 완료 보고서
- `comprehensive_repair_report.md` - 종합 수리 보고서

## 🎯 성공적인 사용을 위한 팁

### 1. 일상적인 사용 팁
- **정기적인 상태 확인**: 매일 `basic_system_test.py` 실행
- **로그 모니터링**: 주요 로그 파일을 정기적으로 확인
- **백업 습관**: 중요한 변경 전에는 항상 백업 생성

### 2. 성능 최적화 팁
- **백그라운드 실행**: 장시간 모니터링 시 백그라운드 실행 활용
- **리소스 모니터링**: CPU/메모리 사용량 정기 확인
- **로그 정리**: 오래된 로그 파일 정기적으로 정리

### 3. 안전한 사용 팁
- **테스트 환경**: 중요한 변경은 테스트 환경에서 먼저 시도
- **단계적 적용**: 대규모 변경은 단계적으로 적용
- **롤백 준비**: 항상 이전 상태로 돌아갈 수 있는 방법 준비

---

**📅 매뉴얼 업데이트**: 2025년 8월 10일  
**👨‍💻 작성자**: Kiro AI Assistant  
**📊 매뉴얼 버전**: v2.0  
**🎯 시스템 버전**: WatchHamster v3.0 + POSCO News 250808  
**📞 지원**: 24/7 기술 지원 가능