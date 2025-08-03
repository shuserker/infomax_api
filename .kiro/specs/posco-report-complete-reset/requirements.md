# Requirements Document

## Introduction

POSCO 리포트 시스템을 완전히 초기화하고 7월 25일부터 새로운 통합 리포트만으로 재구성하는 기능입니다. 기존의 모든 개별 리포트(exchange-rate, kospi-close, newyork-market-watch)를 완전히 제거하고, 통합 리포트(integrated) 타입만으로 시스템을 재구축합니다.

## Requirements

### Requirement 1

**User Story:** 시스템 관리자로서, 기존의 모든 리포트를 완전히 제거하여 깨끗한 상태에서 새로운 시스템을 시작하고 싶습니다.

#### Acceptance Criteria

1. WHEN 리포트 초기화를 실행하면 THEN 시스템은 docs/reports/ 폴더의 모든 HTML 파일을 제거해야 합니다
2. WHEN 리포트 초기화를 실행하면 THEN 시스템은 Monitoring/Posco_News_mini/reports/ 폴더의 모든 HTML 파일을 제거해야 합니다  
3. WHEN 리포트 초기화를 실행하면 THEN 시스템은 reports_index.json을 완전히 빈 상태로 초기화해야 합니다
4. WHEN 초기화가 완료되면 THEN 시스템은 제거된 파일 수와 결과를 로그로 출력해야 합니다

### Requirement 2

**User Story:** 시스템 관리자로서, 7월 25일부터 현재까지의 기간에 대해 새로운 통합 리포트만을 생성하고 싶습니다.

#### Acceptance Criteria

1. WHEN 통합 리포트 재생성을 실행하면 THEN 시스템은 2025-07-25부터 현재 날짜까지 각 날짜별로 통합 리포트를 생성해야 합니다
2. WHEN 각 날짜의 리포트를 생성할 때 THEN 시스템은 해당 날짜에 맞는 현실적인 뉴스 데이터를 생성해야 합니다
3. WHEN 뉴스 데이터를 생성할 때 THEN 시스템은 요일별로 다른 시장 시나리오(상승/하락/혼조/안정)를 적용해야 합니다
4. WHEN 통합 리포트를 생성할 때 THEN 시스템은 exchange-rate, kospi-close, newyork-market-watch 3개 뉴스 타입을 모두 포함해야 합니다

### Requirement 3

**User Story:** 시스템 관리자로서, 생성된 모든 통합 리포트가 메타데이터에 정확히 등록되어 대시보드에서 확인할 수 있기를 원합니다.

#### Acceptance Criteria

1. WHEN 통합 리포트가 생성되면 THEN 시스템은 해당 리포트를 reports_index.json에 자동으로 등록해야 합니다
2. WHEN 메타데이터에 등록할 때 THEN 시스템은 리포트 타입을 "integrated"로 설정해야 합니다
3. WHEN 메타데이터에 등록할 때 THEN 시스템은 올바른 GitHub Pages URL을 생성해야 합니다
4. WHEN 모든 리포트 생성이 완료되면 THEN 시스템은 성공률과 생성된 리포트 목록을 요약해서 출력해야 합니다

### Requirement 4

**User Story:** 시스템 관리자로서, 작업 완료 후 Dooray를 통해 결과 알림을 받고 싶습니다.

#### Acceptance Criteria

1. WHEN 모든 작업이 완료되면 THEN 시스템은 Dooray 웹훅을 통해 완료 알림을 전송해야 합니다
2. WHEN 알림을 전송할 때 THEN 시스템은 제거된 기존 리포트 수와 새로 생성된 리포트 수를 포함해야 합니다
3. WHEN 알림을 전송할 때 THEN 시스템은 대시보드 링크와 최신 리포트 링크를 포함해야 합니다
4. WHEN 알림 전송에 실패하면 THEN 시스템은 오류를 로그에 기록하고 계속 진행해야 합니다

### Requirement 5

**User Story:** 개발자로서, 향후 유지보수를 위해 개별 리포트 생성 기능을 완전히 비활성화하고 싶습니다.

#### Acceptance Criteria

1. WHEN 시스템을 재구성할 때 THEN 개별 모니터링 스크립트(exchange-rate, kospi-close, newyork-market-watch)는 비활성화되어야 합니다
2. WHEN 스케줄러를 확인할 때 THEN 통합 리포트 스케줄러만 활성화되어 있어야 합니다
3. WHEN 새로운 리포트가 생성될 때 THEN 반드시 통합 리포트 타입이어야 합니다
4. IF 개별 리포트 생성이 시도되면 THEN 시스템은 이를 거부하고 통합 리포트 사용을 안내해야 합니다