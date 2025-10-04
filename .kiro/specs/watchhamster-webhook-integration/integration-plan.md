# WatchHamster 웹훅 시스템 통합 작업 명세서

## 📋 작업 개요

**목표**: WatchHamster_Project의 원본 웹훅 로직을 WatchHamster_Project_GUI_Tauri_WindSurf_So4.5에 완전히 통합

**작업일**: 2025-10-04  
**우선순위**: HIGH  
**예상 소요 시간**: 4-6시간

---

## 🔍 현황 분석

### 원본 프로젝트 (WatchHamster_Project)
**경로**: `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/`

**핵심 파일**:
- ✅ `webhook_sender.py` (34,427 bytes) - 완전한 웹훅 전송 시스템
- ✅ `news_message_generator.py` (59,170 bytes) - 메시지 생성 로직
- ✅ `integrated_api_module.py` (18,525 bytes) - API 통합 모듈
- ✅ `environment_setup.py` (7,617 bytes) - 환경 설정

**주요 기능**:
1. **8가지 메시지 타입** 지원
   - 영업일 비교 분석 (business_day_comparison)
   - 지연 발행 알림 (delay_notification)
   - 일일 통합 리포트 (daily_report)
   - 정시 발행 알림 (status_notification)
   - 데이터 갱신 없음 (no_data_notification)
   - 워치햄스터 오류 (watchhamster_error)
   - 워치햄스터 상태 (watchhamster_status)
   - 테스트 메시지 (test)

2. **완전한 메시지 템플릿 엔진**
   - 동적 메시지 생성
   - 시간 기반 상태 판단
   - 트리 구조 메시지 포맷팅
   - 이모지 및 색상 코드 관리

3. **우선순위 큐 시스템**
   - CRITICAL, HIGH, NORMAL, LOW 우선순위
   - 자동 재시도 메커니즘
   - 중복 메시지 방지

4. **Dooray 웹훅 통합**
   - 실제 웹훅 URL 설정
   - BOT 프로필 이미지
   - 채널별 라우팅

### 새 프로젝트 (WatchHamster_Project_GUI_Tauri_WindSurf_So4.5)
**경로**: `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/`

**현재 상태**:
- ⚠️ `api/webhooks.py` - 더미 템플릿만 존재
- ⚠️ `api/webhook_manager.py` - API 엔드포인트는 있으나 실제 로직 미연결
- ⚠️ `core/posco_original/webhook_sender.py` - 원본 복사본 존재하나 API와 미연결
- ⚠️ `core/posco_original/news_message_generator.py` - 파일 존재 여부 확인 필요

**문제점**:
1. API 엔드포인트가 더미 데이터 반환
2. 실제 메시지 생성 로직 미연결
3. 데이터베이스 로깅 불완전
4. 템플릿 엔진 미작동

---

## 🎯 작업 범위

### Phase 1: 원본 파일 완전 복사 및 경로 수정
**대상 파일**:
1. `news_message_generator.py` (59,170 bytes)
   - 원본: `WatchHamster_Project/Posco_News_Mini_Final/core/news_message_generator.py`
   - 대상: `WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/core/posco_original/news_message_generator.py`
   - 작업: import 경로 수정, 의존성 확인

2. `integrated_api_module.py` (18,525 bytes)
   - 원본: `WatchHamster_Project/Posco_News_Mini_Final/core/integrated_api_module.py`
   - 대상: `WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/core/posco_original/integrated_api_module.py`
   - 작업: API 키 관리, 환경 변수 통합

3. `environment_setup.py` (7,617 bytes)
   - 원본: `WatchHamster_Project/Posco_News_Mini_Final/core/environment_setup.py`
   - 대상: `WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/python-backend/core/posco_original/environment_setup.py`
   - 작업: 경로 설정 업데이트

### Phase 2: API 엔드포인트 실제 로직 연결
**수정 대상**: `api/webhook_manager.py`

**변경 사항**:
1. **더미 데이터 제거**
   ```python
   # 제거: webhook_logs = []
   # 추가: 실제 데이터베이스 조회
   ```

2. **실제 메시지 생성기 연결**
   ```python
   # 현재: generator = get_message_generator() (None 반환 가능)
   # 변경: 항상 유효한 generator 인스턴스 보장
   ```

3. **모든 엔드포인트 실제 구현**
   - `/send/test` ✅ (이미 구현됨)
   - `/send/business-day-comparison` ⚠️ (구현 필요)
   - `/send/delay-notification` ⚠️ (구현 필요)
   - `/send/daily-report` ⚠️ (구현 필요)
   - `/send/status-notification` ⚠️ (구현 필요)
   - `/send/no-data-notification` ⚠️ (구현 필요)
   - `/send/watchhamster-error` ⚠️ (구현 필요)
   - `/send/watchhamster-status` ⚠️ (구현 필요)

### Phase 3: 데이터베이스 로깅 통합
**수정 대상**: `database/` 모듈

**작업**:
1. 웹훅 로그 스키마 확인
2. `save_webhook_log()` 함수 완전 구현
3. 로그 조회 API 실제 데이터베이스 연결
4. 통계 집계 로직 구현

### Phase 4: 템플릿 시스템 통합
**수정 대상**: `api/webhooks.py`

**작업**:
1. 더미 템플릿 제거
2. `NewsMessageGenerator`의 실제 템플릿 사용
3. 템플릿 변수 자동 추출 로직 개선
4. 템플릿 미리보기 기능 구현

---

## 📝 상세 작업 체크리스트

### ✅ Phase 1: 파일 복사 및 경로 수정

- [ ] **1.1** `news_message_generator.py` 복사
  - [ ] 파일 복사 실행
  - [ ] import 경로 수정 (상대 경로 → 절대 경로)
  - [ ] 의존성 파일 확인 (`integrated_news_parser`, `news_data_parser`)
  - [ ] 테스트 실행

- [ ] **1.2** `integrated_api_module.py` 복사
  - [ ] 파일 복사 실행
  - [ ] API 키 환경 변수 확인
  - [ ] 테스트 실행

- [ ] **1.3** `environment_setup.py` 복사
  - [ ] 파일 복사 실행
  - [ ] 경로 설정 업데이트
  - [ ] 테스트 실행

- [ ] **1.4** 의존성 파일 확인
  - [ ] `integrated_news_parser.py` 존재 확인
  - [ ] `news_data_parser.py` 존재 확인
  - [ ] `ai_analysis_engine.py` 존재 확인
  - [ ] 누락된 파일 복사

### ✅ Phase 2: API 엔드포인트 연결

- [ ] **2.1** `webhook_manager.py` 수정
  - [ ] `get_message_generator()` 함수 개선
  - [ ] 에러 핸들링 강화
  - [ ] 로깅 추가

- [ ] **2.2** 각 엔드포인트 실제 구현
  - [ ] `/send/business-day-comparison`
    - [ ] 요청 데이터 검증
    - [ ] `NewsMessageGenerator.generate_business_day_comparison_message()` 호출
    - [ ] 응답 포맷 표준화
  
  - [ ] `/send/delay-notification`
    - [ ] 요청 데이터 검증
    - [ ] `NewsMessageGenerator.generate_delay_notification_message()` 호출
    - [ ] 응답 포맷 표준화
  
  - [ ] `/send/daily-report`
    - [ ] 요청 데이터 검증
    - [ ] `NewsMessageGenerator.generate_daily_integrated_report_message()` 호출
    - [ ] 응답 포맷 표준화
  
  - [ ] `/send/status-notification`
    - [ ] 요청 데이터 검증
    - [ ] `NewsMessageGenerator.generate_status_notification_message()` 호출
    - [ ] 응답 포맷 표준화
  
  - [ ] `/send/no-data-notification`
    - [ ] 요청 데이터 검증
    - [ ] `NewsMessageGenerator.generate_no_data_notification_message()` 호출
    - [ ] 응답 포맷 표준화

- [ ] **2.3** 에러 처리 통합
  - [ ] 메시지 생성 실패 시 처리
  - [ ] 웹훅 전송 실패 시 처리
  - [ ] 재시도 로직 확인

### ✅ Phase 3: 데이터베이스 로깅

- [ ] **3.1** 로그 스키마 확인
  - [ ] `webhook_logs` 테이블 구조 확인
  - [ ] 필요한 컬럼 추가

- [ ] **3.2** `save_webhook_log()` 구현
  - [ ] 데이터베이스 연결 확인
  - [ ] 로그 저장 로직 구현
  - [ ] 에러 핸들링

- [ ] **3.3** 로그 조회 API 구현
  - [ ] `/logs` 엔드포인트 실제 DB 연결
  - [ ] `/logs/{log_id}` 엔드포인트 실제 DB 연결
  - [ ] 필터링 및 페이지네이션

- [ ] **3.4** 통계 API 구현
  - [ ] `/stats` 엔드포인트 실제 DB 연결
  - [ ] 집계 쿼리 최적화

### ✅ Phase 4: 템플릿 시스템

- [ ] **4.1** `api/webhooks.py` 수정
  - [ ] 더미 템플릿 제거
  - [ ] `NewsMessageGenerator` 템플릿 사용

- [ ] **4.2** 템플릿 미리보기 구현
  - [ ] `/message-types/{message_type_id}/detail` 개선
  - [ ] 실제 생성된 메시지 표시

---

## 🧪 테스트 계획

### 단위 테스트
1. **메시지 생성 테스트**
   - [ ] 각 메시지 타입별 생성 테스트
   - [ ] 에러 케이스 테스트
   - [ ] 템플릿 변수 치환 테스트

2. **웹훅 전송 테스트**
   - [ ] 실제 Dooray 웹훅 전송 테스트
   - [ ] 재시도 메커니즘 테스트
   - [ ] 우선순위 큐 테스트

3. **데이터베이스 테스트**
   - [ ] 로그 저장 테스트
   - [ ] 로그 조회 테스트
   - [ ] 통계 집계 테스트

### 통합 테스트
1. **전체 플로우 테스트**
   - [ ] API 요청 → 메시지 생성 → 웹훅 전송 → 로그 저장
   - [ ] 에러 발생 시 복구 테스트
   - [ ] 동시 요청 처리 테스트

2. **UI 연동 테스트**
   - [ ] 프론트엔드에서 API 호출 테스트
   - [ ] 로그 조회 UI 테스트
   - [ ] 통계 대시보드 테스트

---

## 🚨 주의사항

1. **API 키 보안**
   - 웹훅 URL은 환경 변수로 관리
   - 코드에 하드코딩 금지

2. **하위 호환성**
   - 기존 API 엔드포인트 유지
   - 점진적 마이그레이션

3. **에러 처리**
   - 모든 외부 호출에 try-catch
   - 명확한 에러 메시지

4. **로깅**
   - 모든 주요 작업 로깅
   - 디버깅 정보 포함

---

## 📊 진행 상황 추적

| Phase | 작업 | 상태 | 완료일 | 비고 |
|-------|------|------|--------|------|
| 1 | 파일 복사 및 경로 수정 | ⏳ 대기 | - | - |
| 2 | API 엔드포인트 연결 | ⏳ 대기 | - | - |
| 3 | 데이터베이스 로깅 통합 | ⏳ 대기 | - | - |
| 4 | 템플릿 시스템 통합 | ⏳ 대기 | - | - |
| 5 | 테스트 및 검증 | ⏳ 대기 | - | - |

---

## 📚 참고 자료

- 원본 프로젝트: `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/WatchHamster_Project/`
- 새 프로젝트: `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/WatchHamster_Project_GUI_Tauri_WindSurf_So4.5/`
- 커밋 해시: `a763ef84be08b5b1dab0c0ba20594b141baec7ab`

---

## ✅ 완료 기준

1. ✅ 모든 웹훅 API 엔드포인트가 실제 로직과 연결됨
2. ✅ 메시지 생성이 원본과 동일하게 작동함
3. ✅ 데이터베이스 로깅이 정상 작동함
4. ✅ 모든 단위 테스트 통과
5. ✅ 통합 테스트 통과
6. ✅ UI에서 정상 작동 확인

---

**작성자**: Cascade AI  
**최종 수정일**: 2025-10-04
