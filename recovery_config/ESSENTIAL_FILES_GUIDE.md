# 🎯 POSCO 시스템 필수 파일 가이드

## 📁 실제 운영에 필요한 핵심 파일들만!

### 🚀 운영 필수 파일 (8개만!)

```
recovery_config/
├── 🔧 핵심 시스템 (5개)
│   ├── environment_setup.py              # 환경 설정
│   ├── integrated_api_module.py          # API 연동
│   ├── news_message_generator.py         # 메시지 생성
│   ├── webhook_sender.py                 # 웹훅 전송
│   └── watchhamster_monitor.py           # 시스템 감시
│
├── 🎮 실행 파일 (2개)
│   ├── start_watchhamster_monitor.py     # 모니터 시작
│   └── comprehensive_system_integration_test.py  # 전체 테스트
│
└── 📋 모니터링 가이드 (1개)
    └── MONITORING_GUIDE_FOR_OPERATORS.md # 운영 매뉴얼
```

### 🗑️ 정리 대상 파일들

**테스트 파일들 (20+개)**
- `test_*.py` - 개발/검증용, 운영에는 불필요
- `*_test.py` - 개발/검증용, 운영에는 불필요

**리포트 파일들 (15+개)**
- `task*_completion_report.md` - 개발 과정 기록, 운영에는 불필요
- `*_summary.md` - 개발 과정 기록, 운영에는 불필요

**중복/백업 파일들**
- `*_simple.py` - 단순 버전, 통합 버전으로 대체됨
- `*_demo.py` - 데모용, 운영에는 불필요

## 🎯 제안: 깔끔한 운영 폴더 구조

```
posco_system/                    ← 새로운 깔끔한 폴더
├── core/                        ← 핵심 시스템 파일들
│   ├── environment_setup.py
│   ├── integrated_api_module.py
│   ├── news_message_generator.py
│   ├── webhook_sender.py
│   └── watchhamster_monitor.py
│
├── scripts/                     ← 실행 스크립트들
│   ├── start_monitoring.py
│   ├── daily_check.py
│   ├── daily_check.bat         ← Windows용
│   └── daily_check.sh          ← Mac용
│
├── docs/                        ← 문서들
│   ├── MONITORING_GUIDE.md
│   └── QUICK_CHEAT_SHEET.md
│
└── logs/                        ← 로그 파일들
    └── (자동 생성됨)
```

## 💡 정리 후 혜택

1. **파일 수 대폭 감소**: 60+ → 10개
2. **명확한 구조**: 용도별 폴더 분리
3. **쉬운 관리**: 필요한 파일만 남김
4. **빠른 찾기**: 직관적인 폴더명

## 🤔 정리 진행할까요?

**옵션 1**: 새로운 깔끔한 폴더 생성 (추천)
**옵션 2**: 현재 폴더에서 불필요한 파일들만 삭제
**옵션 3**: 현재 상태 유지

어떤 방식으로 정리하시겠어요?