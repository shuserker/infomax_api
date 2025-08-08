# Requirements Document

## Introduction

현재 POSCO 모니터링 시스템은 워치햄스터(WatchHamster)가 최상위 관리자 역할을 해야 하는데, 제어센터에서는 개별 뉴스 알림 시스템만 실행하는 구조적 문제가 있습니다. 이로 인해 시스템 계층 구조가 뒤바뀌어 있고, 워치햄스터의 핵심 기능인 프로세스 감시와 자동 복구가 제대로 작동하지 않고 있습니다.

올바른 시스템 아키텍처는 워치햄스터가 최상위에서 모든 하위 뉴스 모니터링 프로세스들을 관리하고, 제어센터는 워치햄스터를 통해 전체 시스템을 제어하는 구조여야 합니다.

## Requirements

### Requirement 1

**User Story:** 시스템 관리자로서, 제어센터에서 워치햄스터를 실행하면 모든 하위 뉴스 모니터링 시스템이 자동으로 관리되기를 원한다.

#### Acceptance Criteria

1. WHEN 제어센터에서 "시스템 시작"을 선택 THEN 워치햄스터가 최상위 프로세스로 실행 SHALL 된다
2. WHEN 워치햄스터가 시작 THEN 모든 하위 뉴스 모니터링 프로세스들을 자동으로 시작 SHALL 한다
3. WHEN 워치햄스터가 실행 중 THEN 하위 프로세스들의 헬스체크를 지속적으로 수행 SHALL 한다
4. IF 하위 프로세스가 중단 THEN 워치햄스터가 자동으로 재시작 SHALL 한다

### Requirement 2

**User Story:** 시스템 관리자로서, 워치햄스터가 모든 뉴스 모니터링 프로세스의 상태를 통합 관리하기를 원한다.

#### Acceptance Criteria

1. WHEN 워치햄스터가 실행 THEN 다음 하위 프로세스들을 관리 SHALL 한다:
   - posco_main_notifier.py (메인 뉴스 알림)
   - 기타 개별 뉴스 모니터링 프로세스들
2. WHEN 하위 프로세스 상태 변화 발생 THEN 워치햄스터가 상태를 추적하고 로그에 기록 SHALL 한다
3. WHEN 프로세스 복구 완료 THEN 워치햄스터가 복구 완료 알림을 전송 SHALL 한다
4. WHEN 시스템 종료 요청 THEN 워치햄스터가 모든 하위 프로세스를 안전하게 종료 SHALL 한다

### Requirement 3

**User Story:** 시스템 관리자로서, 제어센터의 메뉴 구조가 실제 시스템 아키텍처를 반영하기를 원한다.

#### Acceptance Criteria

1. WHEN 제어센터 메뉴 표시 THEN "워치햄스터 시작/중지/재시작" 옵션이 최상위에 위치 SHALL 한다
2. WHEN "워치햄스터 시작" 선택 THEN 워치햄스터와 모든 하위 시스템이 통합 실행 SHALL 된다
3. WHEN "개별 시스템 관리" 메뉴 접근 THEN 워치햄스터 실행 상태를 먼저 확인 SHALL 한다
4. IF 워치햄스터가 실행 중이 아님 THEN 개별 시스템 실행을 제한하고 워치햄스터 실행을 권장 SHALL 한다

### Requirement 4

**User Story:** 시스템 관리자로서, 워치햄스터의 알림 시스템이 전체 시스템 상태를 포괄적으로 보고하기를 원한다.

#### Acceptance Criteria

1. WHEN 워치햄스터 시작 THEN 시작 알림과 함께 관리 대상 프로세스 목록을 포함 SHALL 한다
2. WHEN 정기 상태 보고 THEN 모든 하위 프로세스의 상태를 통합하여 보고 SHALL 한다
3. WHEN 프로세스 문제 발생 THEN 문제 프로세스 식별 정보와 복구 시도 상태를 알림 SHALL 한다
4. WHEN 시스템 종료 THEN 모든 하위 프로세스 종료 상태를 포함한 종료 알림을 전송 SHALL 한다

### Requirement 5

**User Story:** 개발자로서, 새로운 뉴스 모니터링 모듈을 추가할 때 워치햄스터에 쉽게 등록할 수 있기를 원한다.

#### Acceptance Criteria

1. WHEN 새 모니터링 모듈 추가 THEN 설정 파일에 모듈 정보만 추가하면 워치햄스터가 자동 인식 SHALL 한다
2. WHEN 모듈 설정 변경 THEN 워치햄스터 재시작 없이 설정을 다시 로드 SHALL 할 수 있다
3. WHEN 모듈 제거 THEN 워치햄스터가 해당 프로세스를 안전하게 종료하고 관리 목록에서 제거 SHALL 한다
4. WHEN 모듈 상태 확인 THEN 각 모듈별 개별 상태와 전체 통합 상태를 구분하여 제공 SHALL 한다

### Requirement 6

**User Story:** 시스템 관리자로서, 워치햄스터의 자동 복구 기능이 지능적으로 작동하기를 원한다.

#### Acceptance Criteria

1. WHEN 프로세스 크래시 감지 THEN 즉시 1차 재시작을 시도 SHALL 한다
2. IF 1차 재시작 실패 THEN 5분 후 2차 재시작을 시도 SHALL 한다
3. IF 연속 3회 재시작 실패 THEN 해당 프로세스를 비활성화하고 관리자에게 긴급 알림을 전송 SHALL 한다
4. WHEN Git 업데이트 감지 THEN 모든 프로세스를 안전하게 재시작하여 업데이트를 적용 SHALL 한다

### Requirement 7

**User Story:** 시스템 관리자로서, 제어센터와 워치햄스터 간의 통신이 안정적이기를 원한다.

#### Acceptance Criteria

1. WHEN 제어센터에서 워치햄스터 상태 조회 THEN 실시간 상태 정보를 정확하게 반환 SHALL 한다
2. WHEN 제어센터에서 워치햄스터 제어 명령 전송 THEN 명령 실행 결과를 확인할 수 있는 피드백을 제공 SHALL 한다
3. WHEN 워치햄스터와 제어센터 간 통신 오류 THEN 오류 상황을 명확하게 표시하고 복구 방법을 안내 SHALL 한다
4. WHEN 제어센터 종료 THEN 워치햄스터는 독립적으로 계속 실행 SHALL 된다