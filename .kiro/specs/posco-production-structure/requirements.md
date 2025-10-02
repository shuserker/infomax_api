# Requirements Document

## Introduction

POSCO 시스템의 복잡한 recovery_config 폴더에서 운영에 필요한 최종 파일들만 선별하여 프로그램 하이어라키에 맞는 깔끔한 운영 구조로 복사 배치합니다. 기존 레거시 파일들은 참고용으로 보존하고, 새로운 구조에서는 워치햄스터(상위 모니터링 시스템)와 포스코(하위 프로젝트)를 명확히 분리하여 향후 확장성을 확보합니다.

## Requirements

### Requirement 1

**User Story:** 시스템 아키텍트로서, 워치햄스터 모니터링 시스템과 포스코 뉴스 프로젝트를 계층적으로 분리하여 향후 다른 프로젝트 추가 시에도 확장 가능한 구조를 만들고 싶습니다.

#### Acceptance Criteria

1. WHEN 폴더 구조를 생성할 때 THEN 시스템은 Monitoring/WatchHamster_Project 상위 구조를 생성해야 합니다
2. WHEN 워치햄스터 모듈을 배치할 때 THEN 시스템은 공통 모니터링 기능들을 WatchHamster_Project/core에 배치해야 합니다
3. WHEN 포스코 프로젝트를 배치할 때 THEN 시스템은 WatchHamster_Project/Posco_News_Mini_Final 하위에 독립적으로 배치해야 합니다
4. WHEN 새로운 프로젝트를 추가할 때 THEN 시스템은 Posco_News_Mini_Final과 동일한 구조로 확장 가능해야 합니다

### Requirement 2

**User Story:** 운영 관리자로서, 레거시 파일들은 보존하면서 운영에 필요한 최종 파일들만 새로운 구조로 복사하여 깔끔하게 관리하고 싶습니다.

#### Acceptance Criteria

1. WHEN 파일을 복사할 때 THEN 시스템은 기존 recovery_config 폴더를 그대로 보존해야 합니다
2. WHEN 핵심 파일을 선별할 때 THEN 시스템은 운영에 필요한 최종 버전 파일들만 복사해야 합니다
3. WHEN 새로운 구조를 확인할 때 THEN 시스템은 워치햄스터 3개 + 포스코 4개 = 총 7개의 핵심 모듈만 포함해야 합니다
4. WHEN 테스트 파일들을 처리할 때 THEN 시스템은 개발용 테스트 파일들은 복사하지 않아야 합니다

### Requirement 3

**User Story:** 모니터링 요원으로서, 새로운 깔끔한 구조에서 기존과 동일한 성능으로 시스템을 운영하고 싶습니다.

#### Acceptance Criteria

1. WHEN 새로운 구조에서 실행할 때 THEN 시스템은 기존과 동일한 100% 성공률(8/8)을 달성해야 합니다
2. WHEN 워치햄스터 모니터를 시작할 때 THEN 시스템은 포스코 프로젝트를 자동으로 감지하고 모니터링해야 합니다
3. WHEN 포스코 시스템 테스트를 실행할 때 THEN 시스템은 워치햄스터 공통 모듈을 정상적으로 참조해야 합니다
4. WHEN 실행 스크립트를 사용할 때 THEN 시스템은 Mac/Windows 모두에서 새로운 경로로 정상 작동해야 합니다

### Requirement 4

**User Story:** 개발자로서, 새로운 구조에서도 기존 기능들이 완벽하게 작동하고 코드 유지보수가 쉬워지기를 원합니다.

#### Acceptance Criteria

1. WHEN import 경로를 수정할 때 THEN 시스템은 워치햄스터 공통 모듈과 포스코 전용 모듈을 명확히 구분해야 합니다
2. WHEN 포스코 모듈에서 워치햄스터 모듈을 참조할 때 THEN 시스템은 상위 패키지 경로로 정확히 import해야 합니다
3. WHEN 새로운 구조에서 테스트할 때 THEN 시스템은 모든 API 연동, 메시지 생성, 웹훅 전송 기능이 정상 작동해야 합니다
4. WHEN 모니터링 가이드를 업데이트할 때 THEN 시스템은 새로운 경로와 확장성 정보를 포함해야 합니다