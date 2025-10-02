# 📋 POSCO 뉴스 시스템 모니터링 가이드

## 🎯 개요
이 가이드는 POSCO 뉴스 시스템을 모니터링하는 운영 요원을 위한 실용적인 매뉴얼입니다.

## 📁 핵심 파일 구조

```
Monitoring/WatchHamster_Project/Posco_News_Mini_Final/
├── 🚀 scripts/
│   └── system_test.py                     # 전체 시스템 테스트
│
├── ⚙️ core/
│   ├── environment_setup.py              # 환경 설정
│   ├── integrated_api_module.py          # API 연동
│   ├── news_message_generator.py         # 메시지 생성
│   └── webhook_sender.py                 # 웹훅 전송
│
├── 📊 config/
│   └── environment_settings.json         # 환경 설정 파일
│
└── 📚 docs/
    ├── MONITORING_GUIDE.md               # 이 가이드
    └── QUICK_CHEAT_SHEET.md              # 간단 치트시트
```

## 🖥️ 실행 방법

### 🍎 Mac에서 실행

#### 1. 터미널 열기
- `Cmd + Space` → "터미널" 검색 → 엔터

#### 2. 포스코 프로젝트 폴더로 이동
```bash
cd /path/to/your/project/Monitoring/WatchHamster_Project/Posco_News_Mini_Final
```

#### 3. 주요 명령어들
```bash
# 전체 시스템 테스트 (가장 중요! - 100% 성공률 목표)
python3 scripts/system_test.py

# 간단한 통합 테스트
python3 scripts/simple_integration_test.py

# 포스코 모듈들 개별 테스트
python3 scripts/test_posco_modules.py

# 환경 설정 확인
python3 core/environment_setup.py

# 개별 모듈 테스트
python3 core/integrated_api_module.py
python3 core/news_message_generator.py
python3 core/webhook_sender.py
```

### 🪟 Windows에서 실행

#### 1. 명령 프롬프트 열기
- `Win + R` → "cmd" 입력 → 엔터

#### 2. 포스코 프로젝트 폴더로 이동
```cmd
cd C:\path\to\your\project\Monitoring\WatchHamster_Project\Posco_News_Mini_Final
```

#### 3. 주요 명령어들
```cmd
# 전체 시스템 테스트 (가장 중요! - 100% 성공률 목표)
python scripts/system_test.py

# 간단한 통합 테스트
python scripts/simple_integration_test.py

# 포스코 모듈들 개별 테스트
python scripts/test_posco_modules.py

# 환경 설정 확인
python core/environment_setup.py

# 개별 모듈 테스트
python core/integrated_api_module.py
python core/news_message_generator.py
python core/webhook_sender.py
```

## 🔍 일일 모니터링 체크리스트

### ✅ 매일 해야 할 일 (5분 소요)

1. **전체 시스템 테스트 실행 (최우선)**
   ```bash
   # Mac
   python3 scripts/system_test.py
   
   # Windows
   python scripts/system_test.py
   ```
   - ✅ 결과: "🎯 100.0% (8/8)" 나오면 정상
   - ❌ 실패 시: 즉시 담당자에게 연락

2. **간단한 통합 테스트 실행**
   ```bash
   # Mac
   python3 scripts/simple_integration_test.py
   
   # Windows
   python scripts/simple_integration_test.py
   ```
   - ✅ 결과: 모든 모듈 로드 성공 시 정상
   - ❌ 실패 시: 모듈별 개별 테스트 진행

3. **포스코 모듈별 개별 테스트**
   ```bash
   # Mac
   python3 scripts/test_posco_modules.py
   
   # Windows
   python scripts/test_posco_modules.py
   ```
   - ✅ 결과: 4개 모듈 모두 정상 로드 시 정상
   - ❌ 실패 시: 실패한 모듈 개별 점검

4. **Discord 채널 확인**
   - 뉴스 메시지가 정상적으로 올라오는지 확인
   - 오류 메시지가 없는지 확인
   - 메시지 형식이 올바른지 확인

5. **워치햄스터 연동 상태 확인**
   - 상위 워치햄스터 시스템에서 포스코 프로젝트 감지 여부 확인
   - 워치햄스터 공통 모듈 사용 상태 확인

6. **시스템 리소스 확인**
   - CPU 사용률 80% 이하 유지
   - 메모리 사용률 90% 이하 유지
   - 디스크 공간 10GB 이상 여유

### 📊 주간 모니터링 (10분 소요)

1. **안정성 검증 실행**
   ```bash
   # Mac
   python3 scripts/system_test.py --stability
   
   # Windows
   python scripts/system_test.py --stability
   ```
   - ✅ 결과: 80점 이상이면 정상
   - ⚠️ 70-80점: 주의 관찰
   - ❌ 70점 미만: 즉시 점검 필요

2. **워치햄스터 연동 통합 테스트**
   ```bash
   # 워치햄스터 프로젝트 루트에서 실행
   cd ../..
   python3 scripts/watchhamster_posco_integration_test.py
   ```
   - ✅ 결과: 워치햄스터-포스코 연동 성공 시 정상
   - ❌ 실패 시: 연동 설정 점검 필요

3. **로그 파일 확인**
   - `logs/` 폴더의 로그 파일들 검토
   - 반복되는 오류 패턴 확인
   - 워치햄스터 로그와 연관성 분석

## 🚨 문제 상황별 대응

### 🔴 긴급 상황 (즉시 대응)

#### 상황 1: 전체 시스템 테스트 실패
```
❌ 결과: 실패 (0/8 또는 낮은 성공률)
```
**대응 방법:**
1. 5분 후 다시 테스트 실행
2. 여전히 실패 시 담당자 즉시 연락
3. Discord 채널에서 메시지 전송 중단 여부 확인

#### 상황 2: Discord 메시지 전송 중단
```
뉴스 메시지가 30분 이상 올라오지 않음
```
**대응 방법:**
1. 웹훅 모듈 재시작
   ```bash
   python3 core/webhook_sender.py --test
   ```
2. 5분 후 메시지 전송 재개 확인
3. 여전히 문제 시 담당자 연락

### 🟡 주의 상황 (관찰 필요)

#### 상황 3: 안정성 점수 하락
```
안정성 점수: 70-80점
```
**대응 방법:**
1. 다음날 재검증
2. 3일 연속 80점 미만 시 담당자 연락
3. 시스템 리소스 사용률 확인

#### 상황 4: 메시지 지연
```
뉴스 메시지가 10-30분 지연
```
**대응 방법:**
1. 시스템 리소스 확인
2. 네트워크 연결 상태 확인
3. 지속 시 담당자 연락

## 📞 연락처 및 에스컬레이션

### 1차 담당자
- **이름**: [담당자명]
- **연락처**: [전화번호]
- **이메일**: [이메일주소]

### 2차 담당자 (1차 연락 불가 시)
- **이름**: [부담당자명]
- **연락처**: [전화번호]
- **이메일**: [이메일주소]

### 긴급 상황 보고 양식
```
[긴급] POSCO 뉴스 시스템 문제 발생

발생 시간: YYYY-MM-DD HH:MM
문제 상황: [구체적 설명]
실행한 명령어: [명령어]
오류 메시지: [오류 내용]
현재 상태: [시스템 상태]
```

## 🛠️ 자주 발생하는 문제 해결

### Q1: "python 명령어를 찾을 수 없습니다"
**A1:** 
- Mac: `python3` 사용
- Windows: Python 설치 확인 후 `python` 사용

### Q2: "모듈을 찾을 수 없습니다"
**A2:**
```bash
# Posco_News_Mini_Final 폴더에 있는지 확인
pwd  # Mac
cd   # Windows

# 올바른 폴더로 이동
cd Monitoring/WatchHamster_Project/Posco_News_Mini_Final
```

### Q3: "권한이 없습니다"
**A3:**
- Mac: `sudo python3 [파일명]`
- Windows: 관리자 권한으로 명령 프롬프트 실행

### Q4: Discord에 메시지가 안 올라옴
**A4:**
1. 인터넷 연결 확인
2. 웹훅 모듈 테스트
   ```bash
   python3 core/webhook_sender.py --test
   ```
3. 웹훅 URL 설정 확인 (`config/environment_settings.json`)

## 📈 성능 지표 이해

### 정상 상태 지표
- **전체 시스템 테스트**: 100% (8/8)
- **안정성 점수**: 90점 이상
- **메시지 생성 시간**: 1초 이내
- **Discord 전송**: 실시간

### 주의 상태 지표
- **전체 시스템 테스트**: 75-99% (6-7/8)
- **안정성 점수**: 70-89점
- **메시지 생성 시간**: 1-5초
- **Discord 전송**: 5분 이내 지연

### 위험 상태 지표
- **전체 시스템 테스트**: 75% 미만 (5/8 이하)
- **안정성 점수**: 70점 미만
- **메시지 생성 시간**: 5초 이상
- **Discord 전송**: 30분 이상 지연

## 🎯 모니터링 요원 성공 팁

1. **매일 같은 시간에 체크**: 오전 9시 권장
2. **결과를 간단히 기록**: 날짜, 시간, 결과만
3. **의심스러우면 재실행**: 1-2회 더 테스트
4. **Discord 채널 즐겨찾기**: 빠른 확인을 위해
5. **담당자 연락처 저장**: 긴급 상황 대비

## 📝 일일 체크 기록 양식

```
날짜: 2025-MM-DD
시간: HH:MM

[ ] 전체 시스템 테스트: ___/8 (___%)
[ ] Discord 메시지 확인: 정상/지연/중단
[ ] 시스템 리소스: CPU ___%, 메모리 ___%
[ ] 특이사항: ________________

담당자: [이름]
```

## 🚀 확장성 및 새 프로젝트 추가 안내

### 📋 포스코 프로젝트 구조 이해
현재 포스코 뉴스 시스템은 워치햄스터 모니터링 시스템의 하위 프로젝트로 구성되어 있습니다:

```
WatchHamster_Project/                    # 상위 모니터링 시스템
├── core/                               # 워치햄스터 공통 모듈들
│   ├── watchhamster_monitor.py         # 전체 시스템 모니터링
│   ├── git_monitor.py                  # Git 모니터링 (공통)
│   └── system_monitor.py               # 시스템 리소스 모니터링 (공통)
└── Posco_News_Mini_Final/              # 포스코 뉴스 프로젝트 (하위)
    ├── core/                           # 포스코 전용 모듈들
    ├── scripts/                        # 포스코 실행 스크립트들
    └── docs/                           # 포스코 문서들
```

### 🎯 새로운 POSCO 프로젝트 추가 시 고려사항

#### 1. 워치햄스터 공통 모듈 활용
새로운 POSCO 프로젝트를 추가할 때는 워치햄스터의 공통 모듈들을 재사용할 수 있습니다:
- `watchhamster_monitor.py`: 전체 시스템 모니터링
- `git_monitor.py`: Git 저장소 모니터링
- `system_monitor.py`: 시스템 리소스 모니터링

#### 2. 표준 프로젝트 구조 준수
```
WatchHamster_Project/
└── New_Posco_Project/                  # 새로운 POSCO 프로젝트
    ├── core/                           # 프로젝트 전용 모듈들
    │   ├── __init__.py
    │   ├── environment_setup.py        # 환경 설정 (필수)
    │   ├── main_module.py              # 메인 기능 모듈
    │   └── data_processor.py           # 데이터 처리 모듈
    ├── scripts/                        # 실행 스크립트들
    │   ├── __init__.py
    │   ├── system_test.py              # 시스템 테스트 (필수)
    │   └── test_modules.py             # 모듈 테스트
    ├── docs/                           # 프로젝트 문서들
    │   ├── MONITORING_GUIDE.md         # 모니터링 가이드 (필수)
    │   └── QUICK_CHEAT_SHEET.md        # 간단 치트시트
    ├── config/                         # 설정 파일들
    │   └── settings.json               # 프로젝트 설정
    └── logs/                           # 로그 파일들 (자동 생성)
```

#### 3. 워치햄스터 연동 설정
새 프로젝트에서 워치햄스터 공통 모듈을 사용하려면:
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

### 📊 프로젝트 추가 후 검증 절차

1. **워치햄스터에서 새 프로젝트 감지 확인**
   ```bash
   cd ../../  # WatchHamster_Project 루트로 이동
   python3 scripts/start_monitoring.py --list-projects
   ```

2. **새 프로젝트 개별 테스트**
   ```bash
   cd New_Posco_Project
   python3 scripts/system_test.py
   ```

3. **워치햄스터 통합 테스트**
   ```bash
   cd ../../  # WatchHamster_Project 루트로 이동
   python3 scripts/final_integration_test.py
   ```

### 🎯 운영 요원을 위한 다중 프로젝트 관리 팁

1. **우선순위 관리**: 워치햄스터 상태 → 개별 프로젝트 상태 순으로 확인
2. **통합 모니터링**: 워치햄스터 대시보드에서 모든 프로젝트 상태 한눈에 파악
3. **문제 격리**: 한 프로젝트 문제가 다른 프로젝트에 영향 주지 않도록 독립성 유지
4. **확장성 고려**: 새 프로젝트 추가 시 기존 운영 절차 최대한 재사용

---

**📞 문제 발생 시 주저하지 말고 즉시 연락하세요!**  
**🎯 시스템이 정상 작동할 때는 아무것도 건드리지 마세요!**  
**🚀 새 프로젝트 추가 시 워치햄스터 구조를 활용하세요!**