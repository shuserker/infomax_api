# WatchHamster Tauri 비즈니스 로직 구현 요구사항

## 📋 개요

기존 WatchHamster_Project의 완전한 비즈니스 로직을 WatchHamster_Project_GUI_Tauri에 통합하여 실제 작동하는 Dooray 웹훅 기반 모니터링 시스템을 완성합니다.

## 🎯 프로젝트 목표

현재 UI만 구성된 Tauri 프로젝트에 기존 Python 백엔드의 모든 핵심 로직을 이식하여 완전히 작동하는 POSCO 뉴스 모니터링 및 웹훅 알림 시스템을 구축합니다.

## 📊 요구사항

### Requirement 1: 핵심 API 연동 시스템 구현

**User Story:** 시스템 관리자로서 INFOMAX API와 안정적으로 연동하여 실시간 뉴스 데이터를 수집하고 싶습니다.

#### Acceptance Criteria

1. WHEN INFOMAX API 클라이언트를 초기화하면 THEN 기존 WatchHamster_Project의 infomax_api_client.py와 동일한 기능을 제공해야 합니다
2. WHEN API 호출이 실패하면 THEN api_connection_manager.py의 재시도 메커니즘이 작동해야 합니다
3. WHEN API 응답을 받으면 THEN news_data_parser.py의 파싱 로직으로 데이터를 처리해야 합니다
4. WHEN 연결 상태가 변경되면 THEN 실시간으로 GUI에 상태가 반영되어야 합니다
5. WHEN API 설정을 변경하면 THEN 즉시 새로운 설정이 적용되어야 합니다

### Requirement 2: 뉴스 데이터 파싱 및 상태 판단 시스템

**User Story:** 운영자로서 수집된 뉴스 데이터의 상태(최신, 지연, 과거)를 정확히 파악하고 싶습니다.

#### Acceptance Criteria

1. WHEN 뉴스 데이터를 받으면 THEN exchange-rate, newyork-market-watch, kospi-close 3가지 타입을 모두 파싱해야 합니다
2. WHEN 뉴스 발행 시간을 분석하면 THEN 예상 발행 시간 대비 지연 여부를 정확히 판단해야 합니다
3. WHEN 영업일/비영업일을 확인하면 THEN 한국 공휴일 및 주말을 고려해야 합니다
4. WHEN 데이터 상태가 변경되면 THEN GUI에서 실시간으로 상태 변화를 확인할 수 있어야 합니다
5. WHEN 파싱 오류가 발생하면 THEN 적절한 오류 메시지와 함께 복구 방안을 제시해야 합니다

### Requirement 3: WatchHamster 모니터링 시스템 통합

**User Story:** 시스템 관리자로서 전체 시스템의 프로세스 상태와 리소스 사용량을 모니터링하고 싶습니다.

#### Acceptance Criteria

1. WHEN 시스템을 시작하면 THEN watchhamster_monitor.py의 모든 모니터링 기능이 활성화되어야 합니다
2. WHEN 프로세스 상태를 확인하면 THEN 5분 간격으로 자동 체크가 수행되어야 합니다
3. WHEN Git 상태를 확인하면 THEN 브랜치, 커밋, 충돌 상태를 정확히 파악해야 합니다
4. WHEN 시스템 리소스를 모니터링하면 THEN CPU, 메모리, 디스크 사용률을 실시간으로 추적해야 합니다
5. WHEN 임계값을 초과하면 THEN 자동으로 경고 알림을 생성해야 합니다

### Requirement 4: Dooray 웹훅 알림 시스템 구현

**User Story:** 운영팀으로서 시스템 상태 변화를 Dooray 메신저로 즉시 알림받고 싶습니다.

#### Acceptance Criteria

1. WHEN 뉴스 데이터 상태가 변경되면 THEN POSCO 웹훅(https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg)으로 알림을 전송해야 합니다
2. WHEN 시스템 전체 상태를 보고하면 THEN WatchHamster 웹훅(https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ)으로 종합 상태를 전송해야 합니다
3. WHEN 웹훅 메시지를 생성하면 THEN 기존 generate_dynamic_alert_message 로직과 동일한 형식을 사용해야 합니다
4. WHEN 웹훅 전송이 실패하면 THEN 재시도 메커니즘이 작동해야 합니다
5. WHEN 알림 설정을 변경하면 THEN GUI에서 실시간으로 설정을 조정할 수 있어야 합니다

### Requirement 5: 실시간 GUI 통합 및 사용자 인터페이스

**User Story:** 사용자로서 직관적인 GUI를 통해 모든 시스템 상태를 한눈에 파악하고 제어하고 싶습니다.

#### Acceptance Criteria

1. WHEN 대시보드를 열면 THEN 모든 뉴스 타입의 현재 상태를 실시간으로 표시해야 합니다
2. WHEN 서비스 관리 페이지를 열면 THEN 각 서비스의 시작/중지/재시작을 제어할 수 있어야 합니다
3. WHEN 로그 뷰어를 열면 THEN 실시간 로그 스트리밍과 필터링 기능을 제공해야 합니다
4. WHEN 설정 페이지를 열면 THEN API 설정, 웹훅 URL, 모니터링 간격을 조정할 수 있어야 합니다
5. WHEN 시스템 상태가 변경되면 THEN WebSocket을 통해 즉시 GUI가 업데이트되어야 합니다

### Requirement 6: 자동 복구 및 오류 처리 시스템

**User Story:** 시스템 관리자로서 장애 발생 시 자동으로 복구되거나 명확한 복구 가이드를 제공받고 싶습니다.

#### Acceptance Criteria

1. WHEN API 연결이 실패하면 THEN 자동으로 재연결을 시도해야 합니다
2. WHEN 프로세스가 중단되면 THEN 자동으로 재시작을 시도해야 합니다
3. WHEN Git 충돌이 발생하면 THEN 자동 해결 가능 여부를 판단하고 적절한 조치를 취해야 합니다
4. WHEN 시스템 리소스가 부족하면 THEN 자동으로 정리 작업을 수행해야 합니다
5. WHEN 복구가 불가능하면 THEN 명확한 수동 개입 가이드를 제공해야 합니다

### Requirement 7: 설정 관리 및 영속성

**User Story:** 시스템 관리자로서 모든 설정을 GUI에서 관리하고 재시작 후에도 설정이 유지되기를 원합니다.

#### Acceptance Criteria

1. WHEN 설정을 변경하면 THEN 즉시 파일에 저장되어야 합니다
2. WHEN 시스템을 재시작하면 THEN 이전 설정이 자동으로 복원되어야 합니다
3. WHEN 설정 파일이 손상되면 THEN 기본값으로 자동 복구되어야 합니다
4. WHEN 설정을 내보내면 THEN JSON 형식으로 백업할 수 있어야 합니다
5. WHEN 설정을 가져오면 THEN 백업 파일에서 설정을 복원할 수 있어야 합니다

### Requirement 8: 성능 최적화 및 안정성

**User Story:** 시스템 관리자로서 24시간 안정적으로 운영되는 고성능 모니터링 시스템을 원합니다.

#### Acceptance Criteria

1. WHEN 시스템을 장시간 운영하면 THEN 메모리 누수 없이 안정적으로 작동해야 합니다
2. WHEN 대량의 로그가 생성되면 THEN 자동으로 로그 로테이션이 수행되어야 합니다
3. WHEN 네트워크가 불안정하면 THEN 연결 풀과 재시도 메커니즘으로 안정성을 보장해야 합니다
4. WHEN CPU 사용률이 높으면 THEN 모니터링 간격을 자동으로 조정해야 합니다
5. WHEN 디스크 공간이 부족하면 THEN 자동으로 정리 작업을 수행해야 합니다

## 🔧 기술적 제약사항

### 아키텍처 요구사항
- Python 백엔드는 FastAPI 기반으로 유지
- 프론트엔드는 React + TypeScript + Tauri 구조 유지
- WebSocket을 통한 실시간 통신 구현
- 기존 WatchHamster_Project의 모든 로직을 완전히 이식

### 호환성 요구사항
- 기존 Dooray 웹훅 URL과 메시지 형식 완전 호환
- 기존 API 엔드포인트 및 인증 방식 유지
- 기존 설정 파일 형식과 호환성 보장
- Git 브랜치 전략 준수 (main 개발, publish 배포)

### 보안 요구사항
- API 인증 정보 안전한 저장
- 웹훅 URL 보안 관리
- 로그에서 민감 정보 마스킹
- 설정 파일 암호화 지원

## 📈 성공 기준

### 기능적 성공 기준
1. 기존 WatchHamster_Project의 모든 기능이 Tauri 버전에서 정상 작동
2. POSCO 뉴스 3가지 타입 모두 실시간 모니터링 및 알림
3. Dooray 웹훅을 통한 안정적인 알림 전송
4. 직관적인 GUI를 통한 완전한 시스템 제어

### 성능적 성공 기준
1. API 응답 시간 5초 이내
2. GUI 업데이트 지연 1초 이내
3. 메모리 사용량 500MB 이하 유지
4. 24시간 연속 운영 시 안정성 보장

### 사용성 성공 기준
1. 비개발자도 GUI를 통해 기본 운영 가능
2. 모든 설정을 GUI에서 변경 가능
3. 문제 발생 시 명확한 오류 메시지 및 해결 방안 제시
4. 실시간 상태 모니터링 및 알림 기능

## 🚀 우선순위

### High Priority (필수)
- Requirement 1: 핵심 API 연동 시스템
- Requirement 2: 뉴스 데이터 파싱 시스템
- Requirement 4: Dooray 웹훅 알림 시스템

### Medium Priority (중요)
- Requirement 3: WatchHamster 모니터링 시스템
- Requirement 5: 실시간 GUI 통합
- Requirement 7: 설정 관리 시스템

### Low Priority (선택)
- Requirement 6: 자동 복구 시스템
- Requirement 8: 성능 최적화

## 📝 참고사항

### 기존 코드 참조 위치
- `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/WatchHamster_Project/core/`
- 특히 `watchhamster_monitor.py`, `infomax_api_client.py`, `news_data_parser.py`, `api_connection_manager.py` 파일의 로직을 완전히 이식

### 웹훅 URL 정보
- POSCO 뉴스 알림: `https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg`
- WatchHamster 종합 상태: `https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ`

### API 정보
- INFOMAX API: `https://global-api.einfomax.co.kr/apis/posco/news`
- 지원 타입: `exchange-rate`, `newyork-market-watch`, `kospi-close`