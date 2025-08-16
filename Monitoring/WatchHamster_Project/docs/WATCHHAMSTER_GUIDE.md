# 🐹 워치햄스터 모니터링 시스템 운영 가이드

## 🎯 개요
워치햄스터(WatchHamster)는 POSCO 시스템을 포함한 여러 프로젝트를 통합 모니터링하는 상위 레벨 시스템입니다.

## 📁 시스템 구조

```
WatchHamster_Project/
├── 🧠 core/                    # 워치햄스터 핵심 모니터링 시스템
│   ├── watchhamster_monitor.py # 메인 모니터링 엔진
│   └── git_monitor.py          # Git 저장소 모니터링
│
├── 🚀 scripts/                 # 실행 스크립트들
│   ├── start_monitoring.py     # 워치햄스터 시작
│   ├── daily_check.bat         # Windows 일일 점검
│   └── daily_check.sh          # Mac 일일 점검
│
├── 📚 docs/                    # 문서들
│   └── WATCHHAMSTER_GUIDE.md   # 이 가이드
│
└── 📦 Posco_News_Mini_Final/   # 포스코 뉴스 프로젝트 (하위 프로젝트)
    ├── core/                   # 포스코 전용 모듈들
    ├── scripts/                # 포스코 실행 스크립트들
    ├── docs/                   # 포스코 문서들
    ├── config/                 # 포스코 설정 파일들
    └── logs/                   # 포스코 로그 파일들
```

## 🖥️ 워치햄스터 실행 방법

### 🍎 Mac에서 실행

#### 1. 터미널 열기
- `Cmd + Space` → "터미널" 검색 → 엔터

#### 2. 워치햄스터 프로젝트 폴더로 이동
```bash
cd /path/to/your/project/Monitoring/WatchHamster_Project
```

#### 3. 워치햄스터 모니터 시작
```bash
# 메인 모니터링 시작 (포스코 프로젝트 자동 감지)
python3 scripts/start_monitoring.py

# 일일 점검 실행 (전체 시스템 통합 테스트)
./scripts/daily_check.sh

# 워치햄스터 핵심 기능 테스트
python3 scripts/test_watchhamster_functions.py

# 포스코 연동 통합 테스트
python3 scripts/watchhamster_posco_integration_test.py
```

### 🪟 Windows에서 실행

#### 1. 명령 프롬프트 열기
- `Win + R` → "cmd" 입력 → 엔터

#### 2. 워치햄스터 프로젝트 폴더로 이동
```cmd
cd C:\path\to\your\project\Monitoring\WatchHamster_Project
```

#### 3. 워치햄스터 모니터 시작
```cmd
# 메인 모니터링 시작 (포스코 프로젝트 자동 감지)
python scripts/start_monitoring.py

# 일일 점검 실행 (전체 시스템 통합 테스트)
scripts\daily_check.bat

# 워치햄스터 핵심 기능 테스트
python scripts/test_watchhamster_functions.py

# 포스코 연동 통합 테스트
python scripts/watchhamster_posco_integration_test.py
```

## 🔍 워치햄스터 모니터링 기능

### 1. 🧠 메인 모니터링 (watchhamster_monitor.py)
- **역할**: 전체 시스템 상태 감시
- **기능**: 
  - 하위 프로젝트들 자동 감지 (현재: Posco_News_Mini_Final)
  - 시스템 리소스 모니터링
  - 오류 상황 자동 감지 및 알림
  - 성능 지표 수집
  - 포스코 뉴스 시스템과 연동 모니터링

### 2. 📊 Git 모니터링 (git_monitor.py)
- **역할**: Git 저장소 변경사항 추적
- **기능**:
  - 커밋 변경사항 감지
  - 브랜치 상태 모니터링
  - 코드 변경 알림
  - 포스코 프로젝트 코드 변경 추적

### 3. 🔧 시스템 모니터링 (system_monitor.py)
- **역할**: 시스템 리소스 및 성능 모니터링
- **기능**:
  - CPU, 메모리, 디스크 사용률 추적
  - 네트워크 연결 상태 확인
  - 프로세스 상태 모니터링
  - 성능 임계값 알림

### 4. 📰 뉴스 데이터 파싱 (통합 모듈들)
- **integrated_news_parser.py**: 통합 뉴스 데이터 파싱
- **news_data_parser.py**: 뉴스 데이터 처리
- **exchange_rate_parser.py**: 환율 정보 파싱
- **kospi_close_parser.py**: KOSPI 종가 파싱
- **newyork_market_parser.py**: 뉴욕 시장 데이터 파싱

## 🎯 하위 프로젝트 관리

### 현재 등록된 프로젝트
1. **Posco_News_Mini_Final**: POSCO 뉴스 모니터링 시스템

### 새로운 프로젝트 추가 방법 (확장성 가이드)

#### 📋 단계별 프로젝트 추가 절차

1. **프로젝트 폴더 구조 생성**
   ```bash
   # WatchHamster_Project 하위에 새 프로젝트 폴더 생성
   cd Monitoring/WatchHamster_Project
   mkdir New_Project_Name
   cd New_Project_Name
   
   # 표준 폴더 구조 생성
   mkdir core scripts docs config logs
   touch core/__init__.py scripts/__init__.py
   ```

2. **표준 폴더 구조 (Posco_News_Mini_Final 참조)**
   ```
   New_Project_Name/
   ├── core/                    # 프로젝트 전용 모듈들
   │   ├── __init__.py         # Python 패키지 초기화
   │   ├── environment_setup.py # 환경 설정 모듈
   │   ├── main_module.py      # 메인 기능 모듈
   │   └── data_processor.py   # 데이터 처리 모듈
   ├── scripts/                # 실행 스크립트들
   │   ├── __init__.py         # Python 패키지 초기화
   │   ├── system_test.py      # 시스템 테스트 스크립트
   │   └── start_service.py    # 서비스 시작 스크립트
   ├── docs/                   # 프로젝트 문서들
   │   ├── MONITORING_GUIDE.md # 모니터링 가이드
   │   └── QUICK_CHEAT_SHEET.md # 간단 치트시트
   ├── config/                 # 설정 파일들
   │   └── settings.json       # 프로젝트 설정
   └── logs/                   # 로그 파일들 (자동 생성)
   ```

3. **워치햄스터 연동 설정**
   ```python
   # 새 프로젝트의 core/environment_setup.py에 추가
   import sys
   import os
   
   # 워치햄스터 공통 모듈 import 경로 설정
   sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
   
   # 워치햄스터 공통 모듈 사용
   from watchhamster_monitor import WatchHamsterMonitor
   from git_monitor import GitMonitor
   from system_monitor import SystemMonitor
   ```

4. **워치햄스터 자동 감지 확인**
   ```bash
   # 워치햄스터 모니터 재시작으로 새 프로젝트 감지
   python3 scripts/start_monitoring.py --restart
   
   # 새 프로젝트가 감지되었는지 확인
   python3 scripts/start_monitoring.py --list-projects
   ```

#### 🎯 프로젝트 추가 체크리스트

- [ ] 표준 폴더 구조 생성 완료
- [ ] `__init__.py` 파일들 생성 완료
- [ ] 워치햄스터 공통 모듈 import 경로 설정 완료
- [ ] 프로젝트별 `system_test.py` 스크립트 작성 완료
- [ ] 모니터링 가이드 문서 작성 완료
- [ ] 워치햄스터에서 새 프로젝트 자동 감지 확인 완료
- [ ] 통합 테스트 실행 및 성공 확인 완료

## 📊 일일 모니터링 체크리스트

### ✅ 매일 해야 할 일 (3분 소요)

1. **워치햄스터 상태 확인**
   ```bash
   # Mac
   python3 scripts/start_monitoring.py --status
   
   # Windows
   python scripts/start_monitoring.py --status
   ```

2. **하위 프로젝트들 상태 확인**
   - 포스코 프로젝트 상태: `Posco_News_Mini_Final/scripts/system_test.py` 실행
   - 각 프로젝트별 개별 상태 점검
   - 포스코 상세 가이드: `Posco_News_Mini_Final/docs/MONITORING_GUIDE.md` 참조

3. **워치햄스터 핵심 기능 테스트**
   ```bash
   # Mac
   python3 scripts/test_watchhamster_functions.py
   
   # Windows
   python scripts/test_watchhamster_functions.py
   ```

4. **포스코 연동 통합 테스트**
   ```bash
   # Mac
   python3 scripts/watchhamster_posco_integration_test.py
   
   # Windows
   python scripts/watchhamster_posco_integration_test.py
   ```

5. **시스템 리소스 확인**
   - CPU 사용률 80% 이하 유지
   - 메모리 사용률 90% 이하 유지
   - 디스크 공간 10GB 이상 여유

### 📊 주간 모니터링 (5분 소요)

1. **전체 시스템 통합 테스트**
   ```bash
   # 모든 하위 프로젝트 통합 테스트
   ./scripts/daily_check.sh    # Mac
   scripts\daily_check.bat     # Windows
   ```

2. **최종 통합 테스트 실행**
   ```bash
   # 워치햄스터 + 포스코 완전 통합 테스트
   python3 scripts/final_integration_test.py    # Mac
   python scripts/final_integration_test.py     # Windows
   ```

3. **Git 저장소 상태 확인**
   - 최근 커밋 변경사항 검토
   - 브랜치 상태 확인
   - 포스코 프로젝트 코드 변경 추적

4. **성능 및 안정성 검증**
   - 워치햄스터 핵심 기능 성능 확인
   - 포스코 연동 안정성 확인
   - 시스템 리소스 사용 패턴 분석

## 🚨 문제 상황별 대응

### 🔴 긴급 상황 (즉시 대응)

#### 상황 1: 워치햄스터 모니터 중단
```
모니터링 프로세스가 응답하지 않음
```
**대응 방법:**
1. 워치햄스터 재시작
   ```bash
   python3 scripts/start_monitoring.py --restart
   ```
2. 5분 후 상태 재확인
3. 여전히 문제 시 담당자 연락

#### 상황 2: 하위 프로젝트 다중 실패
```
2개 이상의 하위 프로젝트에서 동시 오류 발생
```
**대응 방법:**
1. 시스템 리소스 확인
2. 네트워크 연결 상태 확인
3. 워치햄스터 전체 재시작
4. 즉시 담당자 연락

### 🟡 주의 상황 (관찰 필요)

#### 상황 3: 성능 저하
```
시스템 응답 시간이 평소보다 느림
```
**대응 방법:**
1. 시스템 리소스 사용률 확인
2. 불필요한 프로세스 종료
3. 다음날 재확인
4. 지속 시 담당자 연락

## 🛠️ 워치햄스터 설정 및 커스터마이징

### 모니터링 주기 설정
```python
# core/watchhamster_monitor.py에서 설정
MONITORING_INTERVAL = 60  # 초 단위 (기본: 60초)
```

### 알림 임계값 설정
```python
# 시스템 리소스 알림 임계값
CPU_THRESHOLD = 80      # CPU 사용률 80% 이상 시 알림
MEMORY_THRESHOLD = 90   # 메모리 사용률 90% 이상 시 알림
DISK_THRESHOLD = 10     # 디스크 여유공간 10GB 미만 시 알림
```

## 📈 성능 지표 및 로그

### 워치햄스터 로그 위치
- **Mac**: `~/Library/Logs/WatchHamster/`
- **Windows**: `%APPDATA%\WatchHamster\Logs\`

### 주요 성능 지표
- **모니터링 응답 시간**: 1초 이내 (정상)
- **하위 프로젝트 감지 시간**: 5초 이내 (정상)
- **시스템 리소스 수집 주기**: 60초 (기본값)

## 🎯 운영 요원 성공 팁

1. **워치햄스터 우선 확인**: 하위 프로젝트 문제 전에 워치햄스터 상태부터 확인
2. **통합 관점 유지**: 개별 프로젝트가 아닌 전체 시스템 관점에서 판단
3. **로그 활용**: 워치햄스터 로그에서 전체적인 패턴 파악
4. **확장성 고려**: 새 프로젝트 추가 시 워치햄스터 설정 검토

## 📞 연락처 및 에스컬레이션

### 워치햄스터 담당자
- **이름**: [워치햄스터 담당자명]
- **연락처**: [전화번호]
- **이메일**: [이메일주소]

### 긴급 상황 보고 양식
```
[긴급] 워치햄스터 시스템 문제 발생

발생 시간: YYYY-MM-DD HH:MM
문제 범위: 워치햄스터/하위프로젝트/전체시스템
영향받는 프로젝트: [프로젝트명들]
실행한 명령어: [명령어]
오류 메시지: [오류 내용]
현재 상태: [시스템 상태]
```

---

**🐹 워치햄스터가 건강하면 모든 프로젝트가 건강합니다!**  
**🎯 의심스러우면 워치햄스터부터 확인하세요!**