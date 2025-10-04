# WatchHamster Tauri 비즈니스 로직 구현 작업 계획

## 📋 구현 작업 목록

- [x] 1. 백엔드 핵심 모듈 이식 및 구현
  - [x] 1.1 INFOMAX API 클라이언트 모듈 구현
    - 기존 `infomax_api_client.py`의 모든 기능을 `python-backend/core/infomax_client.py`로 이식
    - 비동기 처리 및 연결 풀 관리 구현
    - API 상태 체크 및 재시도 메커니즘 구현
    - _Requirements: 1.1, 1.2, 1.5_

  - [x] 1.2 뉴스 데이터 파싱 시스템 통합 구현
    - `news_data_parser.py`, `exchange_rate_parser.py`, `newyork_market_parser.py`, `kospi_close_parser.py`를 통합하여 `python-backend/core/news_parser.py` 구현
    - 3가지 뉴스 타입별 파싱 로직 구현
    - 뉴스 상태 판단 알고리즘 (최신/지연/과거) 구현
    - 영업일/비영업일 판단 로직 구현
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

  - [x] 1.3 WatchHamster 모니터링 시스템 이식
    - 기존 `watchhamster_monitor.py`의 모든 기능을 `python-backend/core/watchhamster_monitor.py`로 이식
    - Git 상태 모니터링 (`git_monitor.py` 이식)
    - 시스템 리소스 모니터링 구현
    - 프로세스 상태 체크 및 자동 재시작 로직 구현
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 1.4 Dooray 웹훅 시스템 구현
    - 기존 웹훅 전송 로직을 `python-backend/core/webhook_sender.py`로 이식
    - POSCO 뉴스 알림 웹훅 구현 (기존 URL 유지)
    - WatchHamster 시스템 상태 웹훅 구현
    - `generate_dynamic_alert_message` 로직 완전 이식
    - 웹훅 전송 실패 시 재시도 메커니즘 구현
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 2. FastAPI 서버 및 API 엔드포인트 구현
  - [x] 2.1 FastAPI 메인 서버 구조 구현
    - `python-backend/main.py`에 FastAPI 앱 설정
    - CORS 미들웨어 및 보안 설정 구현
    - WebSocket 연결 관리자 구현
    - 서버 시작/중지 로직 구현
    - _Requirements: 5.5, 7.1_

  - [x] 2.2 시스템 제어 API 엔드포인트 구현
    - `/api/system/start` - 전체 시스템 시작
    - `/api/system/stop` - 전체 시스템 중지
    - `/api/system/restart` - 시스템 재시작
    - `/api/system/status` - 시스템 상태 조회
    - _Requirements: 5.2, 3.1_

  - [x] 2.3 뉴스 모니터링 API 엔드포인트 구현
    - `/api/news/status` - 뉴스 상태 조회
    - `/api/news/refresh` - 뉴스 데이터 수동 갱신
    - `/api/news/history` - 뉴스 이력 조회
    - _Requirements: 2.4, 5.1_

  - [x] 2.4 설정 관리 API 엔드포인트 구현
    - `/api/settings` - 설정 조회/업데이트
    - `/api/settings/export` - 설정 내보내기
    - `/api/settings/import` - 설정 가져오기
    - `/api/settings/reset` - 기본값 복원
    - _Requirements: 7.1, 7.2, 7.4, 7.5_

  - [x] 2.5 로그 관리 API 엔드포인트 구현
    - `/api/logs` - 로그 조회 (필터링 지원)
    - `/api/logs/export` - 로그 내보내기
    - `/api/logs/clear` - 로그 정리
    - _Requirements: 5.3, 8.2_

- [x] 3. WebSocket 실시간 통신 구현
  - [x] 3.1 WebSocket 서버 구현
    - `/ws` 엔드포인트 구현
    - 클라이언트 연결 관리 및 브로드캐스트 기능
    - 연결 상태 모니터링 및 자동 재연결 처리
    - _Requirements: 5.5_

  - [x] 3.2 실시간 상태 업데이트 시스템 구현
    - 뉴스 상태 변경 시 실시간 알림
    - 시스템 리소스 변화 실시간 전송
    - 서비스 상태 변경 즉시 알림
    - Git 상태 변화 실시간 업데이트
    - _Requirements: 1.4, 2.4, 3.5, 5.5_

- [x] 4. 프론트엔드 서비스 레이어 구현
  - [x] 4.1 API 서비스 클래스 구현
    - `src/services/api.ts`에 모든 백엔드 API 호출 로직 구현
    - 에러 처리 및 재시도 메커니즘 구현
    - 타입 안전성 보장을 위한 TypeScript 인터페이스 정의
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 4.2 WebSocket 서비스 구현
    - `src/services/websocket.ts`에 실시간 통신 로직 구현
    - 이벤트 구독/해제 시스템 구현
    - 연결 상태 관리 및 자동 재연결 구현
    - _Requirements: 5.5_

  - [x] 4.3 상태 관리 시스템 구현
    - React Context 또는 Zustand를 활용한 전역 상태 관리
    - 뉴스 상태, 시스템 상태, 설정 상태 관리
    - 실시간 업데이트 반영 로직 구현
    - _Requirements: 5.1, 5.4, 7.2_

- [x] 5. UI 페이지 기능 보강 및 통합
  - [x] 5.1 Dashboard 페이지 기능 보강
    - 실시간 뉴스 상태 카드 (exchange-rate, newyork-market, kospi-close) 구현
    - 시스템 리소스 모니터링 차트 (CPU, 메모리, 디스크) 추가
    - Git 상태 표시 위젯 구현
    - 최근 알림 로그 표시 영역 추가
    - _Requirements: 5.1, 3.4_

  - [x] 5.2 Services 페이지 기능 보강
    - 개별 서비스 제어 버튼 (시작/중지/재시작) 구현
    - 서비스 상태 실시간 표시 (PID, 업타임, 재시작 횟수)
    - 자동 재시작 설정 UI 구현
    - 서비스 로그 빠른 보기 기능 추가
    - _Requirements: 5.2, 3.1, 3.2_

  - [x] 5.3 Settings 페이지 기능 보강
    - API 설정 섹션 (INFOMAX API URL, 타임아웃, 재시도 설정)
    - 웹훅 설정 섹션 (Dooray 웹훅 URL, 타임아웃 설정)
    - 모니터링 설정 섹션 (체크 간격, 알림 임계값, 조용한 시간)
    - 설정 백업/복원 기능 UI 구현
    - _Requirements: 5.4, 7.1, 7.4, 7.5_

  - [x] 5.4 Logs 페이지 기능 보강
    - 실시간 로그 스트리밍 구현
    - 로그 레벨별 필터링 (DEBUG, INFO, WARNING, ERROR)
    - 날짜 범위 및 검색어 필터링 구현
    - 로그 내보내기 기능 (TXT, JSON 형식)
    - 자동 스크롤 및 최대 라인 수 제한 설정
    - _Requirements: 5.3, 8.2_

- [x] 6. 데이터 모델 및 타입 정의
  - [x] 6.1 TypeScript 타입 정의 구현
    - `src/types/`에 모든 데이터 모델 인터페이스 정의
    - NewsStatus, SystemStatus, Settings 등 핵심 타입 구현
    - API 요청/응답 타입 정의
    - _Requirements: 모든 요구사항_

  - [x] 6.2 Python 데이터 모델 구현
    - `python-backend/models/`에 Pydantic 모델 정의
    - 데이터 검증 및 직렬화 로직 구현
    - API 스키마 자동 생성 설정
    - _Requirements: 모든 요구사항_

- [-] 7. 설정 관리 및 영속성 구현
  - [x] 7.1 설정 파일 관리 시스템 구현
    - JSON 형식 설정 파일 읽기/쓰기 구현
    - 설정 검증 및 기본값 처리 로직
    - 설정 변경 시 즉시 저장 메커니즘
    - _Requirements: 7.1, 7.2_

  - [ ] 7.2 설정 백업/복원 시스템 구현
    - 설정 내보내기 (JSON 파일로 저장)
    - 설정 가져오기 (파일에서 복원)
    - 설정 파일 손상 시 자동 복구 로직
    - _Requirements: 7.3, 7.4, 7.5_

- [ ] 8. 오류 처리 및 복구 시스템 구현
  - [ ] 8.1 API 연결 오류 처리 구현
    - 연결 실패 시 자동 재시도 메커니즘
    - 대체 엔드포인트 시도 로직
    - 오프라인 모드 전환 및 복구
    - _Requirements: 6.1, 6.5_

  - [ ] 8.2 자동 복구 시스템 구현
    - 프로세스 중단 시 자동 재시작
    - Git 충돌 자동 해결 시도
    - 시스템 리소스 부족 시 정리 작업
    - _Requirements: 6.2, 6.3, 6.4_

- [ ] 9. 성능 최적화 및 안정성 구현
  - [ ] 9.1 메모리 관리 및 최적화
    - 메모리 누수 방지 로직 구현
    - 가비지 컬렉션 최적화
    - 장시간 운영 시 안정성 보장
    - _Requirements: 8.1_

  - [ ] 9.2 로그 관리 및 로테이션 구현
    - 자동 로그 로테이션 시스템
    - 로그 파일 크기 제한 및 정리
    - 구조화된 로깅 (JSON 형식) 구현
    - _Requirements: 8.2_

  - [ ] 9.3 성능 모니터링 시스템 구현
    - CPU 사용률 모니터링 및 자동 조정
    - 네트워크 연결 풀 관리
    - 디스크 공간 모니터링 및 정리
    - _Requirements: 8.3, 8.4, 8.5_

- [ ] 10. 보안 강화 구현
  - [ ] 10.1 API 보안 구현
    - API 키 안전한 저장 (환경변수 또는 암호화)
    - 입력 데이터 검증 및 새니타이징
    - 요청 제한 (Rate Limiting) 구현
    - _Requirements: 보안 요구사항_

  - [ ] 10.2 웹훅 보안 구현
    - 웹훅 URL 암호화 저장
    - 로그에서 민감 정보 마스킹
    - 전송 데이터 검증 및 암호화
    - _Requirements: 보안 요구사항_

- [ ] 11. 테스트 구현
  - [ ]* 11.1 백엔드 단위 테스트 작성
    - 각 핵심 모듈별 단위 테스트
    - API 엔드포인트 테스트
    - 데이터 파서 정확성 테스트
    - _Requirements: 모든 요구사항_

  - [ ]* 11.2 프론트엔드 컴포넌트 테스트 작성
    - React 컴포넌트 단위 테스트
    - 서비스 레이어 테스트
    - WebSocket 통신 테스트
    - _Requirements: 모든 요구사항_

  - [ ]* 11.3 통합 테스트 구현
    - 백엔드-프론트엔드 통합 테스트
    - 외부 API 연동 테스트 (모킹)
    - 전체 워크플로우 E2E 테스트
    - _Requirements: 모든 요구사항_

- [ ] 12. 최종 통합 및 검증
  - [ ] 12.1 전체 시스템 통합 테스트
    - 모든 기능이 연동되어 정상 작동하는지 검증
    - 기존 WatchHamster_Project와 동일한 기능 수행 확인
    - POSCO 뉴스 3가지 타입 모니터링 및 알림 검증
    - Dooray 웹훅 전송 정상 작동 확인
    - _Requirements: 모든 요구사항_

  - [ ] 12.2 성능 및 안정성 검증
    - 24시간 연속 운영 테스트
    - 메모리 사용량 및 성능 지표 확인
    - 장애 상황 시뮬레이션 및 복구 테스트
    - _Requirements: 8.1, 8.3, 8.4, 8.5_

  - [ ] 12.3 사용자 인터페이스 최종 검증
    - 모든 UI 페이지 기능 정상 작동 확인
    - 실시간 업데이트 및 WebSocket 통신 검증
    - 설정 변경 및 저장 기능 확인
    - 직관적인 사용성 검증
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

## ⚠️ 전체 공통 규칙 - 하드코딩 더미값 제거 및 실제 연결

### 🔍 모든 작업 단계에서 필수 확인 사항

**각 작업을 수행하기 전에 반드시 다음을 확인하고 수정해야 합니다:**

#### 1. 하드코딩된 더미값 식별 및 제거
- **더미 데이터 패턴 확인**:
  - 고정된 문자열 값 (예: `"dummy_value"`, `"test_data"`, `"placeholder"`)
  - 하드코딩된 숫자 값 (예: `status: "running"` 항상 고정)
  - 임시 배열/객체 데이터 (예: `[{id: 1, name: "test"}]`)
  - 시뮬레이션 로직 (예: `await asyncio.sleep(2)` 후 성공 반환)

#### 2. 실제 core 모듈과의 연결 확인
- **core 모듈 임포트 확인**:
  ```python
  # ❌ 잘못된 예시
  DUMMY_DATA = {"status": "running"}
  
  # ✅ 올바른 예시  
  from core.watchhamster_monitor import WatchHamsterMonitor
  monitor = WatchHamsterMonitor()
  status = monitor.get_status()
  ```

#### 3. 환경변수 및 설정 파일 연동
- **하드코딩된 URL/키 제거**:
  ```python
  # ❌ 잘못된 예시
  webhook_url = "https://hardcoded-webhook-url.com"
  
  # ✅ 올바른 예시
  webhook_url = os.getenv("WEBHOOK_URL") or settings.webhook.url
  ```

#### 4. 실제 데이터 소스 연결
- **API 클라이언트**: 실제 INFOMAX API 호출
- **뉴스 파서**: 실제 뉴스 데이터 파싱
- **시스템 모니터**: 실제 시스템 리소스 조회
- **웹훅 발송**: 실제 Dooray 웹훅 전송

#### 5. 상태 관리 실제 연동
- **서비스 상태**: 실제 프로세스/인스턴스 상태 반영
- **시스템 메트릭**: 실제 CPU/메모리/디스크 사용량
- **뉴스 상태**: 실제 뉴스 데이터 기반 상태 판단

#### 6. 인터페이스 호환성 검증
- **생성자 호환성**: 클래스 초기화 시 매개변수 일치 확인
- **메서드 시그니처**: 호출하는 쪽과 구현하는 쪽의 메서드 시그니처 일치
- **반환 타입**: 예상되는 반환 타입과 실제 반환 타입 일치
- **의존성 주입**: 필요한 의존성이 올바르게 주입되는지 확인

### 🛠️ 작업 시 체크리스트

**각 파일 수정 시 다음을 확인:**

1. **[ ] 더미 데이터 제거**: 모든 하드코딩된 값을 실제 데이터로 교체
2. **[ ] 실제 모듈 연결**: core 모듈의 실제 인스턴스 사용
3. **[ ] 인터페이스 호환성**: 생성자, 메서드 시그니처, 반환 타입 일치 확인
4. **[ ] 의존성 주입**: 필요한 매개변수와 설정이 올바르게 전달되는지 확인
5. **[ ] 오류 처리**: 실제 연결 실패 시 적절한 오류 처리
6. **[ ] 설정 연동**: 환경변수나 설정 파일에서 값 로드
7. **[ ] 로깅 추가**: 실제 작업 수행 시 적절한 로그 출력
8. **[ ] 타입 안전성**: TypeScript/Python 타입 정의 정확성
9. **[ ] 테스트 가능성**: 실제 기능이 테스트 가능한 형태인지 확인

### 🚨 특별 주의사항

#### 기존 Tauri 프로젝트의 일반적인 더미값 패턴:
- **프론트엔드**: `src/` 디렉토리의 모든 컴포넌트
- **백엔드**: `python-backend/api/` 디렉토리의 모든 API
- **설정**: 하드코딩된 URL, 키, 임계값들
- **상태 관리**: 고정된 상태값들
- **WebSocket**: 시뮬레이션 데이터 전송

#### 우선 교체 대상:
1. **웹훅 URL**: 환경변수로 이동
2. **API 엔드포인트**: 설정 파일로 이동  
3. **서비스 상태**: 실제 인스턴스 상태 반영
4. **시스템 메트릭**: 실제 시스템 데이터 사용
5. **뉴스 데이터**: 실제 API 호출 결과 사용
6. **클래스 생성자**: 매개변수 호환성 확인 및 수정
7. **메서드 호출**: 시그니처 일치 확인

### 📋 검증 방법

**각 작업 완료 후:**
1. **기능 테스트**: 실제 데이터로 정상 작동하는지 확인
2. **인터페이스 테스트**: 클래스 생성 및 메서드 호출이 정상 작동하는지 확인
3. **오류 시나리오**: 연결 실패 시 적절히 처리되는지 확인  
4. **로그 확인**: 실제 작업이 로그에 기록되는지 확인
5. **설정 변경**: 설정 변경 시 즉시 반영되는지 확인
6. **타입 검증**: IDE에서 타입 오류가 없는지 확인

---

## 📝 구현 우선순위

### Phase 1: 핵심 로직 이식 (High Priority)
- Task 1: 백엔드 핵심 모듈 이식 및 구현
- Task 2: FastAPI 서버 및 API 엔드포인트 구현
- Task 6: 데이터 모델 및 타입 정의

### Phase 2: 실시간 통신 및 UI 통합 (High Priority)
- Task 3: WebSocket 실시간 통신 구현
- Task 4: 프론트엔드 서비스 레이어 구현
- Task 5: UI 페이지 기능 보강 및 통합

### Phase 3: 안정성 및 최적화 (Medium Priority)
- Task 7: 설정 관리 및 영속성 구현
- Task 8: 오류 처리 및 복구 시스템 구현
- Task 9: 성능 최적화 및 안정성 구현

### Phase 4: 보안 및 검증 (Medium Priority)
- Task 10: 보안 강화 구현
- Task 12: 최종 통합 및 검증

### Phase 5: 테스트 (Low Priority - Optional)
- Task 11: 테스트 구현

## 🎯 성공 기준

### 기능적 성공 기준
1. ✅ 기존 WatchHamster_Project의 모든 기능이 Tauri 버전에서 정상 작동
2. ✅ POSCO 뉴스 3가지 타입 모두 실시간 모니터링 및 알림
3. ✅ Dooray 웹훅을 통한 안정적인 알림 전송
4. ✅ 직관적인 GUI를 통한 완전한 시스템 제어

### 성능적 성공 기준
1. ✅ API 응답 시간 5초 이내
2. ✅ GUI 업데이트 지연 1초 이내
3. ✅ 메모리 사용량 500MB 이하 유지
4. ✅ 24시간 연속 운영 시 안정성 보장

### 사용성 성공 기준
1. ✅ 비개발자도 GUI를 통해 기본 운영 가능
2. ✅ 모든 설정을 GUI에서 변경 가능
3. ✅ 문제 발생 시 명확한 오류 메시지 및 해결 방안 제시
4. ✅ 실시간 상태 모니터링 및 알림 기능

## 📚 참고사항

### 기존 코드 참조
- 기존 WatchHamster_Project의 `core/` 디렉토리 모든 파일
- 특히 `watchhamster_monitor.py`, `infomax_api_client.py`, `news_data_parser.py` 완전 이식 필요

### 개발 환경
- Python 3.9+ (FastAPI, Pydantic, asyncio)
- Node.js 18+ (React, TypeScript, Tauri)
- 기존 Dooray 웹훅 URL 및 INFOMAX API 엔드포인트 유지

### 배포 전략
- 개발: `main` 브랜치에서 개발
- 배포: `publish` 브랜치로 배포
- 기존 Git 브랜치 전략 준수