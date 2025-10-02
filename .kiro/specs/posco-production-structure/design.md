# Design Document

## Overview

POSCO 시스템의 recovery_config 폴더에서 운영에 필요한 최종 파일들만 선별하여 프로그램 하이어라키에 맞는 깔끔한 운영 구조로 복사 배치하는 설계입니다. 워치햄스터 모니터링 시스템을 상위 레벨로, 포스코 뉴스를 하위 프로젝트로 분리하여 확장 가능한 구조를 구축합니다. 기존 레거시 파일들은 참고용으로 보존합니다.

## Architecture

### 새로운 폴더 구조
```
Monitoring/
└── WatchHamster_Project/
    ├── core/                        # 워치햄스터 핵심 모니터링 시스템
    │   ├── watchhamster_monitor.py  # 워치햄스터 메인 모니터링
    │   ├── git_monitor.py           # Git 모니터링 (공통)
    │   └── system_monitor.py        # 시스템 리소스 모니터링 (공통)
    ├── scripts/                     # 워치햄스터 실행 스크립트들
    │   ├── start_monitoring.py      # 워치햄스터 시작
    │   ├── daily_check.bat          # Windows 일일 점검
    │   └── daily_check.sh           # Mac 일일 점검
    ├── docs/                        # 워치햄스터 문서
    │   └── WATCHHAMSTER_GUIDE.md    # 워치햄스터 운영 가이드
    └── Posco_News_Mini_Final/       # 포스코 뉴스 하위 프로젝트
        ├── core/                    # 포스코 뉴스 전용 모듈들
        │   ├── environment_setup.py # 포스코 환경 설정
        │   ├── integrated_api_module.py # INFOMAX API 연동
        │   ├── news_message_generator.py # 뉴스 메시지 생성
        │   └── webhook_sender.py    # Discord 웹훅 전송
        ├── scripts/                 # 포스코 뉴스 실행 스크립트들
        │   └── system_test.py       # 포스코 시스템 테스트
        ├── docs/                    # 포스코 뉴스 문서
        │   ├── MONITORING_GUIDE.md  # 포스코 모니터링 가이드
        │   └── QUICK_CHEAT_SHEET.md # 포스코 간단 치트시트
        ├── config/                  # 포스코 설정 파일들
        │   └── environment_settings.json
        └── logs/                    # 포스코 로그 파일들 (자동 생성)
```

### 파일 분류 기준
- **워치햄스터 레벨**: 공통 모니터링 시스템, 여러 프로젝트에서 재사용 가능
- **프로젝트 레벨**: 각 프로젝트별 전용 모듈들 (포스코, 향후 다른 프로젝트들)
- **확장성**: 새로운 프로젝트 추가 시 Posco_News_Mini_Final과 동일한 구조로 추가

## Components and Interfaces

### 워치햄스터 레벨 모듈들 (3개)
1. `watchhamster_monitor.py` - 워치햄스터 메인 모니터링 시스템
2. `git_monitor.py` - Git 모니터링 (공통 모듈)
3. `system_monitor.py` - 시스템 리소스 모니터링 (공통 모듈)

### 포스코 프로젝트 모듈들 (4개)
1. `environment_setup.py` - 포스코 환경 설정 관리
2. `integrated_api_module.py` - INFOMAX API 연동
3. `news_message_generator.py` - 뉴스 메시지 생성
4. `webhook_sender.py` - Discord 웹훅 전송

### 워치햄스터 Scripts (3개)
1. `start_monitoring.py` - 워치햄스터 모니터 시작
2. `daily_check.bat` - Windows 일일 점검
3. `daily_check.sh` - Mac 일일 점검

### 포스코 Scripts (1개)
1. `system_test.py` - 포스코 시스템 테스트

### 문서들
- 워치햄스터: `WATCHHAMSTER_GUIDE.md` - 워치햄스터 운영 가이드
- 포스코: `MONITORING_GUIDE.md`, `QUICK_CHEAT_SHEET.md` - 포스코 전용 가이드

### 설정 파일
- 포스코: `environment_settings.json` - 포스코 환경 설정

## Data Models

### 파일 복사 매핑 (레거시 보존)
```python
file_copy_mapping = {
    # 워치햄스터 레벨 (공통 모니터링) - recovery_config에서 복사
    'recovery_config/watchhamster_monitor.py': 'Monitoring/WatchHamster_Project/core/watchhamster_monitor.py',
    'recovery_config/git_monitor.py': 'Monitoring/WatchHamster_Project/core/git_monitor.py',
    'recovery_config/start_watchhamster_monitor.py': 'Monitoring/WatchHamster_Project/scripts/start_monitoring.py',
    
    # 포스코 프로젝트 레벨 - recovery_config에서 복사
    'recovery_config/environment_setup.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/environment_setup.py',
    'recovery_config/integrated_api_module.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/integrated_api_module.py',
    'recovery_config/news_message_generator.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/news_message_generator.py',
    'recovery_config/webhook_sender.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/webhook_sender.py',
    
    # 포스코 Scripts - recovery_config에서 복사
    'recovery_config/comprehensive_system_integration_test.py': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/scripts/system_test.py',
    
    # 포스코 Docs - recovery_config에서 복사
    'recovery_config/MONITORING_GUIDE_FOR_OPERATORS.md': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/docs/MONITORING_GUIDE.md',
    'recovery_config/QUICK_MONITORING_CHEAT_SHEET.md': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/docs/QUICK_CHEAT_SHEET.md',
    
    # 포스코 Config - recovery_config에서 복사
    'recovery_config/environment_settings.json': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config/environment_settings.json',
    
    # 실행 스크립트들 - recovery_config에서 복사
    'recovery_config/daily_check.bat': 'Monitoring/WatchHamster_Project/scripts/daily_check.bat',
    'recovery_config/daily_check.sh': 'Monitoring/WatchHamster_Project/scripts/daily_check.sh'
}

# 레거시 보존: recovery_config 폴더는 그대로 유지
legacy_preservation = {
    'recovery_config/': '참고용 보존 (60+ 파일)',
    'action': 'copy_only',  # 이동이 아닌 복사만 수행
    'reason': '개발 과정 기록 및 향후 참고용'
}
```

### Import 경로 수정 규칙
```python
import_updates = {
    # 워치햄스터 공통 모듈 import
    'from recovery_config.watchhamster_monitor': 'from Monitoring.WatchHamster_Project.core.watchhamster_monitor',
    'from recovery_config.git_monitor': 'from Monitoring.WatchHamster_Project.core.git_monitor',
    
    # 포스코 프로젝트 모듈 import
    'from recovery_config.': 'from Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.',
    'import recovery_config.': 'import Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core.',
}
```

## Error Handling

### 파일 복사 오류 처리
- 원본 파일이 존재하지 않을 경우 경고 메시지 출력 후 계속 진행
- 대상 폴더가 없을 경우 자동 생성
- 권한 오류 시 사용자에게 안내
- 복사 실패 시 원본 파일 보존 확인

### Import 경로 수정 오류 처리
- 복사된 파일에서만 import 경로 수정 (원본 보존)
- 수정 전 복사본 백업 생성
- 구문 오류 발생 시 백업에서 복원
- 수정 결과 검증 후 적용

### 레거시 보존 검증
- recovery_config 폴더 무결성 확인
- 복사 과정에서 원본 파일 변경 방지
- 복사 완료 후 원본과 복사본 비교 검증

## Testing Strategy

### 레거시 보존 검증
1. recovery_config 폴더 원본 무결성 확인
2. 복사 과정에서 원본 파일 변경 없음 확인
3. 복사된 파일과 원본 파일 내용 일치 확인

### 새로운 구조 검증
1. 모든 핵심 파일 올바른 위치에 복사 확인
2. 워치햄스터 3개 + 포스코 4개 = 총 7개 핵심 모듈 확인
3. 폴더 구조 계층 정확성 확인
4. __init__.py 파일 자동 생성 확인

### Import 경로 수정 검증
1. 워치햄스터 공통 모듈 import 경로 확인
2. 포스코에서 워치햄스터 모듈 참조 경로 확인
3. 포스코 내부 모듈 간 import 경로 확인
4. Python 구문 오류 없음 확인

### 기능 유지 검증
1. 새로운 구조에서 system_test.py 실행 → 100% 성공률(8/8) 달성
2. 워치햄스터 모니터 시작 → 포스코 프로젝트 자동 감지
3. API 연동, 메시지 생성, 웹훅 전송 기능 정상 작동
4. 모니터링 스크립트 정상 실행

### 확장성 검증
1. 새로운 프로젝트 추가 시뮬레이션
2. 워치햄스터 공통 모듈 재사용 가능성 확인
3. 프로젝트 간 독립성 확인

### 플랫폼별 테스트
1. Mac에서 새로운 경로 실행 스크립트 테스트
2. Windows에서 새로운 경로 실행 스크립트 테스트
3. 경로 구분자 호환성 확인