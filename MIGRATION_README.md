# 🔄 POSCO 워치햄스터 v2.0 마이그레이션

## 📋 개요

이 문서는 POSCO 워치햄스터 v1.x에서 v2.0으로의 안전한 마이그레이션을 위한 가이드입니다.

## 🚀 빠른 시작

### 1단계: 요구사항 확인
```bash
./check_migration_requirements.sh
```

### 2단계: 마이그레이션 실행
```bash
./migrate_to_v2.sh
```

### 3단계: 시스템 시작
```bash
./watchhamster_control_center.sh
# 메뉴에서 "1. 🚀 워치햄스터 시작" 선택
```

## 📁 마이그레이션 스크립트

| 스크립트 | 설명 |
|---------|------|
| `check_migration_requirements.sh` | 마이그레이션 전 요구사항 확인 |
| `migrate_to_v2.sh` | 메인 마이그레이션 스크립트 |
| `rollback_migration.sh` | 마이그레이션 롤백 스크립트 |
| `convert_config.py` | 설정 파일 변환 스크립트 |

## 🔍 마이그레이션 과정

### 자동 백업
- 기존 시스템 전체 백업
- 설정 파일 백업
- 로그 파일 백업
- 데이터 파일 백업

### 시스템 업그레이드
- v2 아키텍처 컴포넌트 설치
- 설정 파일 변환 (`modules.json` 생성)
- 워치햄스터 메인 파일 업데이트
- 제어센터 스크립트 업데이트

### 검증 및 테스트
- 새로운 아키텍처 초기화 테스트
- 기본 기능 동작 확인
- 호환성 검증

## 🛡️ 안전 장치

### 자동 백업
모든 마이그레이션 전에 자동으로 백업이 생성됩니다:
```
backup_YYYYMMDD_HHMMSS/
├── Monitoring/
├── posco_control_center.sh
├── *.log
└── *.json
```

### 폴백 메커니즘
새로운 아키텍처 초기화 실패 시 자동으로 기존 방식으로 동작합니다.

### 롤백 기능
문제 발생 시 언제든지 이전 상태로 복원 가능합니다:
```bash
./rollback_migration.sh
```

## 📊 마이그레이션 전후 비교

### 기존 시스템 (v1.x)
```
📁 기존 구조
├── monitor_WatchHamster.py     # 메인 워치햄스터
├── posco_main_notifier.py      # 개별 모듈들
├── realtime_news_monitor.py
├── integrated_report_scheduler.py
└── posco_control_center.sh     # 기본 제어센터
```

### 새로운 시스템 (v2.0)
```
📁 새로운 구조
├── monitor_WatchHamster.py     # 개선된 워치햄스터
├── posco_main_notifier.py      # 기존 모듈들 (그대로 유지)
├── realtime_news_monitor.py
├── integrated_report_scheduler.py
├── posco_control_center.sh     # 개선된 제어센터
└── Posco_News_mini_v2/         # 새로운 아키텍처
    ├── core/
    │   ├── enhanced_process_manager.py
    │   ├── module_registry.py
    │   ├── notification_manager.py
    │   └── watchhamster_integration.py
    └── modules.json            # 모듈 설정
```

## 🔧 새로운 기능

### Enhanced Process Manager
- 3단계 지능적 자동 복구
- 프로세스 상태 추적
- CPU/메모리 사용률 모니터링
- 헬스체크 시스템

### Module Registry
- JSON 기반 모듈 설정
- 의존성 관리
- 동적 모듈 등록/해제
- 우선순위 기반 시작 순서

### Notification Manager
- 구조화된 알림 시스템
- 알림 템플릿 시스템
- 알림 통계 추적
- 다양한 알림 타입 지원

### 개선된 제어센터
- 워치햄스터 중심 메뉴 구조
- 개별 모듈 상태 관리
- 실시간 상태 모니터링
- 향상된 사용자 인터페이스

## 🚨 문제 해결

### 마이그레이션 실패 시
1. 로그 확인: `tail -f watchhamster.log`
2. 요구사항 재확인: `./check_migration_requirements.sh`
3. 롤백 실행: `./rollback_migration.sh`

### 일반적인 문제

#### Q: 마이그레이션 후 워치햄스터가 시작되지 않습니다.
A: 
1. Python 버전 확인: `python3 --version`
2. 필수 패키지 확인: `pip3 list | grep -E "(requests|psutil)"`
3. 로그 확인: `tail -20 watchhamster.log`

#### Q: 새로운 아키텍처가 활성화되지 않습니다.
A: 
1. v2 컴포넌트 파일 확인
2. modules.json 파일 확인
3. 폴백 메커니즘으로 기존 방식 동작 (정상)

#### Q: 기존 알림이 오지 않습니다.
A:
1. 기존 설정 파일 확인
2. 웹훅 URL 설정 확인
3. 네트워크 연결 상태 확인

## 📞 지원

### 로그 수집
문제 발생 시 다음 정보를 수집해 주세요:

```bash
# 시스템 정보
uname -a > debug_info.txt
python3 --version >> debug_info.txt

# 프로세스 상태
ps aux | grep python | grep posco >> debug_info.txt

# 최근 로그
tail -100 watchhamster.log > debug_log.txt
tail -100 Monitoring/Posco_News_mini/WatchHamster.log >> debug_log.txt

# 설정 파일
cp Monitoring/Posco_News_mini_v2/modules.json debug_config.json
```

### 연락처
- 개발팀: POSCO WatchHamster Development Team
- 문서 버전: v2.0
- 최종 업데이트: 2025-08-07

---

**⚠️ 중요**: 마이그레이션 전에 반드시 `check_migration_requirements.sh`를 실행하여 요구사항을 확인하세요.