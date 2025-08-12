# POSCO 네이밍 컨벤션 표준화 구현 계획

## 개요

POSCO 프로젝트의 모든 파일, 폴더, 코드 내부 네이밍을 일관된 규칙으로 표준화하는 작업 계획

**버전 체계**:
- **워치햄스터**: `v3.0` (메이저.마이너)
- **포스코 뉴스**: `250808` (날짜 기반)

## 🚨 중요 제약사항

### 변경 금지 영역
- **코드 로직**: 모든 알고리즘과 비즈니스 로직은 그대로 유지
- **기능 동작**: 기존 기능의 동작 방식은 절대 변경하지 않음
- **사용자 메시지**: UI에 표시되는 텍스트 내용은 보존
- **데이터 구조**: 기존 데이터 파일 형식과 호환성 유지

### 변경 허용 영역
- **파일명/폴더명**: 네이밍 규칙에 따른 변경
- **변수명/클래스명**: 코드 내부 식별자 이름
- **주석/문서**: 버전 정보 및 설명 텍스트
- **설정값**: 버전 정보 관련 설정

## 구현 작업

- [x] 1. 네이밍 컨벤션 관리 시스템 구현
  - 버전 체계 정의 및 네이밍 규칙 클래스 생성
  - 워치햄스터 v3.0 및 포스코 뉴스 250808 표준 정의
  - 파일명, 폴더명, 클래스명, 변수명 변환 함수 구현
  - _요구사항: 1.1, 2.1, 4.1_

- [x] 2. 파일 및 폴더명 자동 변경 시스템 구현
  - 기존 파일들의 네이밍 패턴 분석 및 매핑 테이블 생성
  - 워치햄스터 관련 파일들을 v3.0 형식으로 일괄 변경
  - 포스코 뉴스 관련 파일들을 250808 형식으로 일괄 변경
  - 변경 작업 로그 및 롤백 기능 구현
  - _요구사항: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_

- [x] 3. Python 코드 내부 네이밍 표준화
  - 클래스명을 WatchHamsterV30*, PoscoNews250808* 형식으로 변경
  - 변수명 및 상수명을 통일된 규칙으로 변경
  - 함수명에 포함된 버전 정보 표준화
# BROKEN_REF:   - import 구문 및 모듈 참조 업데이트
  - _요구사항: 4.1, 4.2, 4.3_

- [x] 4. Shell/Batch 스크립트 네이밍 표준화
  - 스크립트 파일명을 표준 규칙으로 변경
  - 스크립트 내부 변수명 및 함수명 표준화
  - 파일 경로 참조 업데이트
  - 실행 권한 및 호환성 유지
  - _요구사항: 1.1, 4.2_

- [x] 5. 주석 및 문서 표준화
  - Python, Shell, Batch 파일의 헤더 주석 표준화
  - 마크다운 문서의 제목 및 내용 표준화
  - README 파일들의 버전 정보 통일
  - 사용자 가이드 문서의 제품명 및 버전 표기 통일
  - _요구사항: 3.1, 3.2, 3.3, 5.1, 5.2, 5.3_

- [x] 6. 설정 파일 및 데이터 파일 표준화
  - JSON 설정 파일의 버전 정보 필드 표준화
  - 환경 변수명 통일 및 표준화
  - 로그 파일명 및 데이터 파일명 표준화
  - 설정 파일 내부 주석 및 설명 표준화
  - _요구사항: 7.1, 7.2, 7.3_

- [x] 7. 시스템 출력 메시지 표준화
  - 시작/종료 메시지의 버전 정보 표준화
  - 로그 메시지의 제품명 및 버전 표기 통일
  - 에러 메시지 및 알림 메시지 표준화
  - 사용자 인터페이스 텍스트 표준화
  - _요구사항: 6.1, 6.2, 6.3_

- [x] 8. 폴더 구조 재구성 및 표준화
  - Monitoring 폴더 하위 구조 표준화
  - WatchHamster_v3.0 및 POSCO_News_250808 폴더 생성
  - 기존 파일들의 새로운 폴더로 이동
  - 상대 경로 참조 업데이트
  - _요구사항: 2.1, 2.2, 2.3_

- [x] 9. 네이밍 표준화 검증 시스템 구현
  - 모든 파일명이 규칙에 맞는지 자동 검증
  - 코드 내부 네이밍 일관성 검사
  - 문서 및 주석의 표준화 검증
  - 검증 결과 보고서 생성
  - _요구사항: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1_

- [x] 10. 호환성 유지 및 마이그레이션 가이드 작성
  - 기존 사용자를 위한 마이그레이션 가이드 작성
  - 변경된 파일명 및 경로 매핑 테이블 제공
  - 롤백 절차 및 문제 해결 가이드 작성
  - 새로운 네이밍 컨벤션 사용법 문서화
  - _요구사항: 5.1, 5.2, 5.3_

- [x] 11. 최종 통합 테스트 및 검증
  - 변경된 시스템의 전체 기능 테스트
  - 모든 스크립트 및 프로그램 정상 동작 확인
  - 네이밍 일관성 최종 검증
  - 사용자 가이드 및 문서 최종 검토
  - _요구사항: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1_

## 변경 대상 파일 목록

### 워치햄스터 관련 파일들 (v3.0 적용)

#### 제어센터 파일들
```
🐹워치햄스터_총괄_관리_센터_v3.bat → 🐹WatchHamster_v3.0_Control_Center.bat
🐹워치햄스터_통합_관리_센터.bat → 🐹WatchHamster_v3.0_Integrated_Center.bat
🎛️POSCO_제어센터_실행_v2.bat → 🎛️WatchHamster_v3.0_Control_Panel.bat
🎛️POSCO_제어센터_Mac실행.command → 🎛️WatchHamster_v3.0_Control_Panel.command
watchhamster_control_center.sh → watchhamster_v3.0_control_center.sh
watchhamster_master_control.sh → watchhamster_v3.0_master_control.sh
```

#### Python 스크립트들
```
monitor_WatchHamster.py → monitor_WatchHamster_v3.0.py
demo_v2_integration.py → demo_watchhamster_v3.0_integration.py
test_v2_integration.py → test_watchhamster_v3.0_integration.py
test_v2_notification_integration.py → test_watchhamster_v3.0_notification.py
```

#### 폴더 구조
```
Monitoring/Posco_News_mini_v2/ → Monitoring/WatchHamster_v3.0/
.kiro/specs/posco-watchhamster-v2-integration/ → .kiro/specs/watchhamster-v3.0-integration/
```

### 포스코 뉴스 관련 파일들 (250808 적용)

#### 메인 스크립트들
```
Posco_News_mini.py → POSCO_News_250808.py
posco_main_notifier.py → posco_news_250808_notifier.py
posco_continuous_monitor.py → posco_news_250808_monitor.py
```

#### 데이터 파일들
```
posco_news_data.json → posco_news_250808_data.json
posco_news_cache.json → posco_news_250808_cache.json
posco_news_historical_cache.json → posco_news_250808_historical.json
```

#### 폴더 구조
```
Monitoring/Posco_News_mini/ → Monitoring/POSCO_News_250808/
```

### 문서 파일들
```
📋POSCO_워치햄스터_v2_사용자_가이드.md → 📋WatchHamster_v3.0_User_Guide.md
🔄POSCO_워치햄스터_마이그레이션_가이드.md → 🔄WatchHamster_v3.0_Migration_Guide.md
🛠️POSCO_워치햄스터_개발자_가이드.md → 🛠️WatchHamster_v3.0_Developer_Guide.md
```

## 구현 우선순위

### High Priority (즉시 실행)
1. 네이밍 컨벤션 관리 시스템 구현
2. 파일 및 폴더명 자동 변경 시스템
3. Python 코드 내부 네이밍 표준화

### Medium Priority (1주일 내)
4. Shell/Batch 스크립트 네이밍 표준화
5. 주석 및 문서 표준화
6. 설정 파일 및 데이터 파일 표준화

### Low Priority (2주일 내)
7. 시스템 출력 메시지 표준화
8. 폴더 구조 재구성
9. 네이밍 표준화 검증 시스템

### Final Phase (완료 후)
10. 호환성 유지 및 마이그레이션 가이드
11. 최종 통합 테스트 및 검증

## 성공 기준

- [ ] 모든 워치햄스터 관련 파일이 v3.0 형식으로 통일됨
- [ ] 모든 포스코 뉴스 관련 파일이 250808 형식으로 통일됨
- [ ] 코드 내부 클래스명, 변수명이 표준 규칙을 따름
- [ ] 모든 문서와 주석이 일관된 버전 표기를 사용함
- [ ] 변경 후에도 모든 기능이 정상 동작함
- [ ] 사용자가 새로운 네이밍 규칙을 쉽게 이해할 수 있음