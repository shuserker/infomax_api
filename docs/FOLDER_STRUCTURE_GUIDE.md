# POSCO 프로젝트 표준화된 폴더 구조

## 개요
POSCO 네이밍 컨벤션 표준화에 따른 새로운 폴더 구조입니다.

## 폴더 구조

```
Monitoring/
├── POSCO_News_250808/          # POSCO 뉴스 시스템 (날짜 기반 버전)
│   ├── core/                   # 핵심 모듈
│   ├── docs/                   # 문서
│   ├── reports/                # 보고서
│   ├── utils/                  # 유틸리티
│   └── *.py                    # Python 스크립트들
│
├── WatchHamster_v3.0/          # 워치햄스터 시스템 (v3.0)
│   ├── core/                   # 핵심 모듈
│   └── *.py                    # Python 스크립트들
│
└── docs/                       # 공통 문서
    └── *.json                  # 설정 및 인덱스 파일들
```

## 변경 사항

### 이전 구조 → 새로운 구조
- `Posco_News_mini/` → `POSCO_News_250808/`
- `Posco_News_mini_v2/` → `WatchHamster_v3.0/`

## 버전 체계
- **POSCO News**: 날짜 기반 (250808 = 2025년 8월 8일)
- **WatchHamster**: 메이저.마이너 (v3.0)

## 호환성
모든 상대 경로 참조가 자동으로 업데이트되어 기존 기능과의 호환성을 유지합니다.
