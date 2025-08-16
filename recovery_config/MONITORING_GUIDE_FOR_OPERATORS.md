# 📋 POSCO 시스템 모니터링 요원 가이드

## 🎯 개요
이 가이드는 POSCO 시스템을 모니터링하는 운영 요원을 위한 실용적인 매뉴얼입니다.

## 📁 핵심 파일 구조

```
recovery_config/
├── 🚀 실행 파일들
│   ├── start_watchhamster_monitor.py      # 워치햄스터 모니터 시작
│   ├── comprehensive_system_integration_test.py  # 전체 시스템 테스트
│   └── practical_stability_verification.py       # 안정성 검증
│
├── ⚙️ 핵심 시스템 파일들
│   ├── environment_setup.py              # 환경 설정
│   ├── integrated_api_module.py          # API 연동
│   ├── news_message_generator.py         # 메시지 생성
│   ├── webhook_sender.py                 # 웹훅 전송
│   └── watchhamster_monitor.py           # 시스템 감시
│
└── 📊 리포트 파일들
    ├── task15_perfect_completion_summary.md     # 완료 요약
    └── POSCO_SYSTEM_RECOVERY_PROJECT_COMPLETION_REPORT.md  # 최종 리포트
```

## 🖥️ 실행 방법

### 🍎 Mac에서 실행

#### 1. 터미널 열기
- `Cmd + Space` → "터미널" 검색 → 엔터

#### 2. 프로젝트 폴더로 이동
```bash
cd /path/to/your/project/recovery_config
```

#### 3. 주요 명령어들
```bash
# 전체 시스템 테스트 (가장 중요!)
python3 comprehensive_system_integration_test.py

# 워치햄스터 모니터 시작
python3 start_watchhamster_monitor.py

# 안정성 검증
python3 practical_stability_verification.py

# 환경 설정 확인
python3 environment_setup.py
```

### 🪟 Windows에서 실행

#### 1. 명령 프롬프트 열기
- `Win + R` → "cmd" 입력 → 엔터

#### 2. 프로젝트 폴더로 이동
```cmd
cd C:\path\to\your\project\recovery_config
```

#### 3. 주요 명령어들
```cmd
# 전체 시스템 테스트 (가장 중요!)
python comprehensive_system_integration_test.py

# 워치햄스터 모니터 시작
python start_watchhamster_monitor.py

# 안정성 검증
python practical_stability_verification.py

# 환경 설정 확인
python environment_setup.py
```

## 🔍 일일 모니터링 체크리스트

### ✅ 매일 해야 할 일 (5분 소요)

1. **전체 시스템 테스트 실행**
   ```bash
   # Mac
   python3 comprehensive_system_integration_test.py
   
   # Windows
   python comprehensive_system_integration_test.py
   ```
   - ✅ 결과: "🎯 100.0% (8/8)" 나오면 정상
   - ❌ 실패 시: 즉시 담당자에게 연락

2. **Discord 채널 확인**
   - 뉴스 메시지가 정상적으로 올라오는지 확인
   - 오류 메시지가 없는지 확인

3. **시스템 리소스 확인**
   - CPU 사용률 80% 이하 유지
   - 메모리 사용률 90% 이하 유지
   - 디스크 공간 10GB 이상 여유

### 📊 주간 모니터링 (10분 소요)

1. **안정성 검증 실행**
   ```bash
   # Mac
   python3 practical_stability_verification.py
   
   # Windows
   python practical_stability_verification.py
   ```
   - ✅ 결과: 80점 이상이면 정상
   - ⚠️ 70-80점: 주의 관찰
   - ❌ 70점 미만: 즉시 점검 필요

2. **로그 파일 확인**
   - `stability_test.log` 파일 검토
   - 반복되는 오류 패턴 확인

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
1. 워치햄스터 모니터 재시작
   ```bash
   python3 start_watchhamster_monitor.py
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
[긴급] POSCO 시스템 문제 발생

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
# recovery_config 폴더에 있는지 확인
pwd  # Mac
cd   # Windows

# 올바른 폴더로 이동
cd recovery_config
```

### Q3: "권한이 없습니다"
**A3:**
- Mac: `sudo python3 [파일명]`
- Windows: 관리자 권한으로 명령 프롬프트 실행

### Q4: Discord에 메시지가 안 올라옴
**A4:**
1. 인터넷 연결 확인
2. 워치햄스터 모니터 재시작
3. 웹훅 URL 설정 확인

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

---

**📞 문제 발생 시 주저하지 말고 즉시 연락하세요!**  
**🎯 시스템이 정상 작동할 때는 아무것도 건드리지 마세요!**