# POSCO 통합 리포트 시스템 가이드

## 📋 개요

POSCO 리포트 시스템이 **개별 리포트 시스템**에서 **통합 리포트 시스템**으로 완전히 전환되었습니다.

### 🔄 주요 변경사항

| 구분 | 기존 시스템 | 새로운 시스템 |
|------|-------------|---------------|
| **리포트 타입** | 개별 리포트 3개 | 통합 리포트 1개 |
| **생성 방식** | 각각 별도 생성 | 3개 뉴스 타입 통합 |
| **모니터링** | 개별 모니터 스크립트 | 통합 스케줄러 |
| **메타데이터** | 분산 관리 | 중앙 집중 관리 |

## 🚀 새로운 시스템 사용법

### 1. 통합 리포트 수동 생성

```bash
# 현재 날짜 통합 리포트 생성
python3 reports/integrated_report_generator.py

# 특정 날짜 범위 통합 리포트 생성
python3 integrated_report_builder.py
```

### 2. 자동 스케줄링

```bash
# 통합 리포트 스케줄러 실행
python3 integrated_report_scheduler.py
```

### 3. 메타데이터 관리

```bash
# 메타데이터 초기화 및 재구성
python3 metadata_reset_manager.py

# 기존 리포트 스캔 및 등록
python3 metadata_reset_manager.py
```

### 4. 시스템 완전 재구축

```bash
# 전체 시스템 재구축 (주의: 기존 리포트 모두 제거)
python3 posco_report_system_reset.py
```

## 📊 통합 리포트 특징

### 🎯 포함 내용

1. **💱 서환마감** - 원/달러 환율 동향
2. **📈 증시마감** - KOSPI 지수 및 철강업종 동향  
3. **🌆 뉴욕마켓워치** - 글로벌 시장 및 철강 관련 동향

### 🎨 요일별 시나리오

- **월요일**: 주초 상승세 (긍정적 분위기)
- **화요일**: 조정 국면 (신중한 분위기)
- **수요일**: 중간 조정 (우려 분위기)
- **목요일**: 회복 신호 (회복세 분위기)
- **금요일**: 주말 앞 상승 (낙관적 분위기)
- **토/일요일**: 주말 안정/마감 (평온한 분위기)

## 🚫 비활성화된 기능

### 개별 모니터 스크립트

다음 스크립트들은 **비활성화**되었으며, 실행 시 안내 메시지가 표시됩니다:

- `exchange_monitor.py` → 리다이렉트 메시지
- `kospi_monitor.py` → 리다이렉트 메시지  
- `newyork_monitor.py` → 리다이렉트 메시지

### 개별 리포트 생성

개별 리포트 생성 기능은 더 이상 지원되지 않습니다. 모든 리포트는 **통합 리포트**로만 생성됩니다.

## 🔧 시스템 구성 요소

### 핵심 컴포넌트

1. **IntegratedReportGenerator** - 통합 리포트 생성 엔진
2. **IntegratedReportBuilder** - 날짜 범위별 리포트 생성
3. **MetadataResetManager** - 메타데이터 관리 시스템
4. **ReportCleanupManager** - 리포트 정리 도구
5. **LegacySystemDisabler** - 레거시 시스템 비활성화
6. **CompletionNotifier** - Dooray 알림 시스템

### 파일 구조

```
Monitoring/POSCO News/
├── reports/
│   ├── integrated_report_generator.py    # 통합 리포트 생성기
│   └── metadata_manager.py               # 메타데이터 관리자
├── integrated_report_builder.py          # 날짜별 리포트 빌더
├── integrated_report_scheduler.py        # 자동 스케줄러
├── metadata_reset_manager.py             # 메타데이터 리셋 관리자
├── report_cleanup_manager.py             # 리포트 정리 관리자
├── legacy_system_disabler.py             # 레거시 시스템 비활성화
├── completion_notifier.py                # 완료 알림자
├── posco_report_system_reset.py          # 메인 실행 스크립트
└── system_status.json                    # 시스템 상태 파일
```

## 📱 알림 시스템

### Dooray 웹훅 알림

- **완료 알림**: 시스템 재구축 완료 시
- **오류 알림**: 시스템 오류 발생 시  
- **진행 알림**: 주요 단계 진행 시

### 알림 내용

- 제거된 기존 리포트 수
- 새로 생성된 통합 리포트 수
- 성공률 및 처리 시간
- 대시보드 및 리포트 링크

## 🔗 접근 링크

### 대시보드 및 API

- **📊 메인 대시보드**: https://shuserker.github.io/infomax_api/
- **📋 리포트 API**: https://shuserker.github.io/infomax_api/docs/reports_index.json
- **📁 리포트 폴더**: https://shuserker.github.io/infomax_api/reports/

### GitHub 저장소

- **메인 저장소**: https://github.com/shuserker/infomax_api
- **모니터링 시스템**: https://github.com/shuserker/infomax_api/tree/main/Monitoring/POSCO News

## ⚠️ 주의사항

### 시스템 재구축 시

1. **데이터 백업**: 자동으로 백업이 생성되지만, 중요한 데이터는 별도 백업 권장
2. **실행 권한**: 스크립트 실행 시 적절한 권한 필요
3. **네트워크 연결**: GitHub Pages 배포를 위한 인터넷 연결 필요
4. **Dooray 웹훅**: 알림 전송을 위한 웹훅 URL 설정 확인

### 개발 및 유지보수

1. **코드 수정**: 통합 리포트 생성 로직만 수정
2. **스케줄링**: integrated_report_scheduler.py만 사용
3. **메타데이터**: metadata_reset_manager.py로 관리
4. **문제 해결**: 로그 파일 및 system_status.json 확인

## 🆘 문제 해결

### 자주 발생하는 문제

#### 1. 리포트 생성 실패

```bash
# 메타데이터 재구성
python3 metadata_reset_manager.py

# 수동 리포트 생성 테스트
python3 reports/integrated_report_generator.py
```

#### 2. 개별 모니터 스크립트 실행 시

**현상**: "이 스크립트는 비활성화되었습니다" 메시지
**해결**: 통합 리포트 시스템 사용

```bash
# 올바른 사용법
python3 integrated_report_scheduler.py
```

#### 3. 메타데이터 불일치

```bash
# 메타데이터 완전 재구성
python3 metadata_reset_manager.py
```

#### 4. GitHub Pages 배포 실패

**현상**: "publish 브랜치로 전환 실패" 메시지
**해결**: Git 상태 정리 후 재시도

```bash
git add -A
git commit -m "Update reports"
git push origin main
```

### 로그 확인

- **시스템 로그**: 각 스크립트 실행 시 콘솔 출력
- **시스템 상태**: `system_status.json` 파일 확인
- **백업 파일**: `backup_before_reset_*` 디렉토리

## 📞 지원 및 문의

### 개발팀 연락처

- **시스템 관리**: AI Assistant
- **기술 지원**: GitHub Issues
- **긴급 상황**: Dooray 알림 시스템

### 추가 자료

- **README.md**: 전체 시스템 개요
- **API 문서**: 리포트 API 사용법
- **GitHub Wiki**: 상세 기술 문서

---

## 📝 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2025-08-03 | 1.0 | 통합 리포트 시스템으로 완전 전환 |
| 2025-08-03 | 1.0 | 개별 리포트 시스템 비활성화 |
| 2025-08-03 | 1.0 | 메타데이터 시스템 재구성 |

**🎉 POSCO 통합 리포트 시스템을 이용해 주셔서 감사합니다!**