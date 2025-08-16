# POSCO WatchHamster v3.0 종합 테스트 프레임워크

## 개요

POSCO WatchHamster v3.0 통합 및 테스트를 위한 종합적인 테스트 프레임워크입니다.

### 구현된 테스트 요구사항

- ✅ **5.1**: v2 컴포넌트 초기화를 위한 단위 테스트
- ✅ **5.2**: WatchHamster-v2 컴포넌트 통신을 위한 통합 테스트  
- ✅ **5.3**: 시작/중지/재시작 시나리오를 위한 프로세스 생명주기 테스트
- ✅ **5.4**: 자동 복구 시뮬레이션 및 검증 테스트

## 테스트 구조

### 1. 핵심 테스트 스크립트

#### `test_v2_integration.py`
- **목적**: v2 컴포넌트 초기화 및 통합 테스트
- **테스트 클래스**:
  - `TestV2ComponentInitialization`: v2 컴포넌트 초기화 단위 테스트
  - `TestWatchHamster v3.0Communication`: WatchHamster-v2 컴포넌트 통신 테스트
- **주요 테스트**:
  - v2 컴포넌트 파일 구조 검증
  - WatchHamster 초기화 테스트
  - v2 폴백 메커니즘 테스트
  - 프로세스 관리 통합 테스트
  - 3단계 지능적 복구 시스템 테스트

#### `test_process_lifecycle.py`
- **목적**: 프로세스 생명주기 관리 테스트
- **주요 기능**:
  - 정상 프로세스 생명주기 테스트
  - 크래시 복구 시뮬레이션
  - 다중 프로세스 관리 테스트
  - 리소스 모니터링 테스트
- **테스트 시나리오**:
  - 정상 시작/중지 시나리오
  - 프로세스 크래시 및 복구
  - 다중 프로세스 동시 관리
  - CPU/메모리 사용량 모니터링

#### `test_control_center_integration.py`
- **목적**: 제어센터 통합 기능 테스트
- **검증 항목**:
  - 스크립트 존재 및 권한 확인
  - Bash 문법 검사
  - 필수 함수 존재 확인
  - 의존성 스크립트 확인
  - 메뉴 구조 검증
  - 오류 처리 확인

### 2. 테스트 실행 도구

#### `run_comprehensive_tests.py`
- **목적**: 모든 테스트를 통합 실행하고 결과 분석
- **기능**:
  - 순차적 테스트 실행
  - 실시간 진행 상황 표시
  - 상세 결과 분석 및 보고서 생성
  - JSON 형태의 결과 저장

#### `test_runner.sh`
- **목적**: 사용자 친화적인 테스트 실행 인터페이스
- **명령어**:
  - `./test_runner.sh all`: 모든 테스트 실행
  - `./test_runner.sh v2`: v2 통합 테스트만 실행
  - `./test_runner.sh lifecycle`: 프로세스 생명주기 테스트만 실행
  - `./test_runner.sh control`: 제어센터 테스트만 실행
  - `./test_runner.sh check`: 환경 확인
  - `./test_runner.sh results`: 테스트 결과 확인
  - `./test_runner.sh cleanup`: 로그 정리

## 사용 방법

### 1. 빠른 시작

```bash
# 모든 테스트 실행
./test_runner.sh

# 또는 직접 Python 스크립트 실행
python3 run_comprehensive_tests.py
```

### 2. 개별 테스트 실행

```bash
# v2 통합 테스트만 실행
./test_runner.sh v2

# 프로세스 생명주기 테스트만 실행
./test_runner.sh lifecycle

# 제어센터 테스트만 실행
./test_runner.sh control
```

### 3. 환경 확인

```bash
# 테스트 환경 확인
./test_runner.sh check
```

### 4. 결과 확인

```bash
# 테스트 결과 확인
./test_runner.sh results

# 상세 결과 파일 확인
cat test_results.json
```

## 테스트 결과 해석

### 성공 기준

1. **중요 테스트 (Critical Tests)**:
   - v2 Integration Tests
   - Process Lifecycle Tests
   
2. **일반 테스트 (General Tests)**:
   - Control Center Integration Tests

### 결과 분석

- **전체 성공**: 모든 중요 테스트가 통과
- **부분 성공**: 중요 테스트는 통과, 일반 테스트 일부 실패
- **실패**: 중요 테스트 중 하나 이상 실패

### 출력 예시

```
🎯 POSCO WatchHamster v3.0 종합 테스트 결과 보고서
================================================================================

📊 전체 실행 통계
• 실행 시간: 45.23초
• 테스트 스크립트: 3개
• 성공한 스크립트: 3개
• 실패한 스크립트: 0개
• 스크립트 성공률: 100.0%

📈 개별 테스트 통계
• 총 개별 테스트: 15개
• 통과한 테스트: 15개
• 실패한 테스트: 0개
• 개별 테스트 성공률: 100.0%
```

## 테스트 커버리지

### v2 컴포넌트 초기화 테스트
- ✅ Enhanced ProcessManager 초기화
- ✅ ModuleRegistry 초기화
- ✅ NotificationManager 초기화
- ✅ 컴포넌트 상태 검증
- ✅ 폴백 메커니즘 검증

### WatchHamster-v2 통신 테스트
- ✅ 컴포넌트 간 통신 검증
- ✅ 상태 정보 교환 테스트
- ✅ 알림 시스템 통합 테스트
- ✅ 통합 상태 보고 테스트

### 프로세스 생명주기 테스트
- ✅ 정상 시작/중지 시나리오
- ✅ 프로세스 재시작 시나리오
- ✅ 다중 프로세스 관리
- ✅ 리소스 모니터링

### 자동 복구 시뮬레이션 테스트
- ✅ 3단계 복구 시스템 시뮬레이션
- ✅ 복구 성공 시나리오
- ✅ 복구 실패 시나리오
- ✅ 복구 알림 시스템 테스트

### 제어센터 통합 테스트
- ✅ 스크립트 문법 검사
- ✅ 필수 함수 존재 확인
- ✅ 메뉴 구조 검증
- ✅ 오류 처리 확인

## 문제 해결

### 일반적인 문제

1. **Python 모듈 누락**
   ```bash
   pip3 install psutil requests
   ```

2. **권한 문제**
   ```bash
   chmod +x test_runner.sh
   chmod +x watchhamster_control_center.sh
   ```

3. **테스트 스크립트 누락**
   - 모든 테스트 파일이 같은 디렉토리에 있는지 확인

### 디버깅

1. **상세 로그 확인**
   ```bash
# BROKEN_REF:    python3 test_v2_integration.py -v
   ```

2. **개별 테스트 실행**
   ```bash
   python3 -m unittest test_v2_integration.TestV2ComponentInitialization.test_v2_components_import
   ```

3. **결과 파일 분석**
   ```bash
   cat test_results.json | jq '.results'
   ```

## 확장 가능성

### 새로운 테스트 추가

1. **새 테스트 클래스 생성**
   ```python
   class TestNewFeature(unittest.TestCase):
       def test_new_functionality(self):
           # 테스트 구현
           pass
   ```

2. **테스트 러너에 등록**
   ```python
   # run_comprehensive_tests.py에 추가
   test_classes.append(TestNewFeature)
   ```

### 테스트 설정 커스터마이징

- `run_comprehensive_tests.py`의 `test_scripts` 리스트 수정
- 타임아웃, 중요도 등 설정 조정 가능

## 기여 가이드라인

1. **테스트 명명 규칙**: `test_<기능명>_<시나리오>`
2. **문서화**: 각 테스트에 명확한 docstring 추가
3. **오류 처리**: 예상 가능한 오류에 대한 적절한 처리
4. **정리**: `setUp()`과 `tearDown()` 메서드로 테스트 환경 관리

## 라이선스

이 테스트 프레임워크는 POSCO WatchHamster 프로젝트의 일부입니다.