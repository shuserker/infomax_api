# 📚 POSCO 네이밍 컨벤션 마이그레이션 문서 인덱스

## 📋 개요

이 문서는 POSCO 네이밍 컨벤션 표준화 마이그레이션과 관련된 모든 문서들의 인덱스입니다. 각 문서의 용도와 사용 시점을 안내합니다.

## 🗂️ 문서 구조

### 📖 주요 가이드 문서

#### 1. [POSCO 네이밍 컨벤션 마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md)
- **용도**: 전체 마이그레이션 프로세스의 종합 가이드
- **대상**: 모든 사용자 (관리자, 개발자, 사용자)
- **사용 시점**: 마이그레이션 시작 전 필수 읽기
- **주요 내용**:
  - 마이그레이션 개요 및 목표
  - 단계별 마이그레이션 절차
  - 파일명 변경 매핑 테이블
  - 안전 장치 및 백업 방법
  - 마이그레이션 후 검증 방법

#### 2. [POSCO 새로운 네이밍 컨벤션 사용 가이드](POSCO_New_Naming_Convention_Guide.md)
- **용도**: 새로운 네이밍 컨벤션 규칙 및 사용법
- **대상**: 개발자, 시스템 관리자
- **사용 시점**: 새로운 파일/코드 작성 시 참조
- **주요 내용**:
  - 파일명, 폴더명 네이밍 규칙
  - 코드 내부 네이밍 규칙 (클래스, 변수, 함수)
  - 주석 및 문서 작성 규칙
  - 실제 사용 예시

#### 3. [POSCO 네이밍 롤백 가이드](POSCO_Naming_Rollback_Guide.md)
- **용도**: 마이그레이션 문제 발생 시 이전 상태로 복원
- **대상**: 시스템 관리자, 기술 지원팀
- **사용 시점**: 마이그레이션 후 문제 발생 시
- **주요 내용**:
  - 자동 롤백 방법
  - 수동 롤백 절차
  - 시나리오별 대응 방법
  - 응급 복구 절차

#### 4. [POSCO 네이밍 문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md)
- **용도**: 일반적인 문제들의 진단 및 해결 방법
- **대상**: 기술 지원팀, 고급 사용자
- **사용 시점**: 문제 발생 시 참조
- **주요 내용**:
  - 일반적인 문제 유형별 해결 방법
  - 진단 도구 및 스크립트
  - 로그 분석 방법
  - 예방 조치

### 🔧 기술 문서

#### 5. [POSCO 네이밍 컨벤션 시스템 가이드](NAMING_CONVENTION_SYSTEM_GUIDE.md)
- **용도**: 네이밍 컨벤션 관리 시스템의 기술적 사용법
- **대상**: 개발자
- **사용 시점**: 프로그래밍 방식으로 네이밍 작업 시
- **주요 내용**:
  - NamingConventionManager 클래스 사용법
  - API 참조
  - 변환 규칙 상세 설명
  - 확장 방법

#### 6. [POSCO 파일 리네이밍 시스템 가이드](FILE_RENAMING_SYSTEM_GUIDE.md)
- **용도**: 파일 및 폴더 자동 변경 시스템 사용법
- **대상**: 시스템 관리자, 개발자
- **사용 시점**: 대량 파일 변경 작업 시
- **주요 내용**:
  - CLI 도구 사용법
  - 프로그래밍 API
  - 안전 기능 설명
  - 백업 및 롤백 시스템

## 📋 사용 시나리오별 문서 가이드

### 🚀 마이그레이션 시작 전
1. **[마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md)** - 전체 프로세스 이해
2. **[새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md)** - 새로운 규칙 학습

### 🔄 마이그레이션 진행 중
1. **[마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md)** - 단계별 절차 따르기
2. **[파일 리네이밍 시스템 가이드](FILE_RENAMING_SYSTEM_GUIDE.md)** - 도구 사용법
3. **[문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md)** - 문제 발생 시 참조

### 🚨 문제 발생 시
1. **[문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md)** - 첫 번째 참조
2. **[롤백 가이드](POSCO_Naming_Rollback_Guide.md)** - 심각한 문제 시 사용

### 📝 새로운 개발 작업 시
1. **[새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md)** - 규칙 준수
2. **[네이밍 컨벤션 시스템 가이드](NAMING_CONVENTION_SYSTEM_GUIDE.md)** - 프로그래밍 지원

## 🎯 역할별 필수 문서

### 👨‍💼 프로젝트 관리자
- **필수**: [마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md)
- **권장**: [롤백 가이드](POSCO_Naming_Rollback_Guide.md)

### 👨‍💻 개발자
- **필수**: [새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md)
- **필수**: [네이밍 컨벤션 시스템 가이드](NAMING_CONVENTION_SYSTEM_GUIDE.md)
- **권장**: [마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md)

### 🔧 시스템 관리자
- **필수**: [마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md)
- **필수**: [파일 리네이밍 시스템 가이드](FILE_RENAMING_SYSTEM_GUIDE.md)
- **필수**: [롤백 가이드](POSCO_Naming_Rollback_Guide.md)
- **필수**: [문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md)

### 🆘 기술 지원팀
- **필수**: [문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md)
- **필수**: [롤백 가이드](POSCO_Naming_Rollback_Guide.md)
- **권장**: 모든 문서

### 👤 일반 사용자
- **필수**: [마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md) (개요 부분)
- **권장**: [새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md) (기본 규칙)

## 📊 문서 우선순위

### 🔴 높음 (즉시 읽기 필요)
1. [POSCO 네이밍 컨벤션 마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md)
2. [POSCO 새로운 네이밍 컨벤션 사용 가이드](POSCO_New_Naming_Convention_Guide.md)

### 🟡 중간 (필요시 참조)
3. [POSCO 네이밍 롤백 가이드](POSCO_Naming_Rollback_Guide.md)
4. [POSCO 네이밍 문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md)

### 🟢 낮음 (기술적 세부사항)
5. [POSCO 네이밍 컨벤션 시스템 가이드](NAMING_CONVENTION_SYSTEM_GUIDE.md)
6. [POSCO 파일 리네이밍 시스템 가이드](FILE_RENAMING_SYSTEM_GUIDE.md)

## 🔄 문서 업데이트 이력

### v1.0 (2025-08-08)
- 초기 문서 세트 완성
- 6개 주요 가이드 문서 작성
- 마이그레이션 프로세스 정의
- 롤백 및 문제 해결 절차 수립

## 📞 지원 및 피드백

### 문서 관련 문의
- **개발팀**: POSCO WatchHamster Development Team
- **기술 지원**: POSCO Technical Support Team

### 문서 개선 제안
문서 개선 사항이나 추가 필요한 내용이 있으면 다음 정보와 함께 제안해 주세요:
- 문서명
- 개선이 필요한 섹션
- 구체적인 개선 내용
- 사용 시나리오

## 🔍 빠른 참조

### 긴급 상황 시 (시스템 작동 불가)
1. **즉시**: [롤백 가이드](POSCO_Naming_Rollback_Guide.md) → "응급 복구 절차"
2. **그 다음**: [문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md) → "일반적인 문제들"

### 마이그레이션 시작 시
1. **먼저**: [마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md) → "빠른 시작 가이드"
2. **그 다음**: [마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md) → "변경 사항 매핑 테이블"

### 새로운 파일 생성 시
1. **참조**: [새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md) → "파일명 네이밍 규칙"
2. **확인**: [새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md) → "네이밍 체크리스트"

### 코드 작성 시
1. **참조**: [새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md) → "코드 내부 네이밍 규칙"
2. **도구**: [네이밍 컨벤션 시스템 가이드](NAMING_CONVENTION_SYSTEM_GUIDE.md) → "사용법"

## 📋 체크리스트

### 마이그레이션 시작 전 문서 확인
- [ ] [마이그레이션 가이드](POSCO_Naming_Convention_Migration_Guide.md) 읽기 완료
- [ ] [새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md) 숙지 완료
- [ ] [롤백 가이드](POSCO_Naming_Rollback_Guide.md) 위치 확인
- [ ] [문제 해결 가이드](POSCO_Naming_Troubleshooting_Guide.md) 북마크 완료

### 개발자 온보딩 문서 확인
- [ ] [새로운 네이밍 컨벤션 가이드](POSCO_New_Naming_Convention_Guide.md) 학습 완료
- [ ] [네이밍 컨벤션 시스템 가이드](NAMING_CONVENTION_SYSTEM_GUIDE.md) API 이해
- [ ] 네이밍 체크리스트 숙지
- [ ] 실제 코드 작성 연습 완료

### 시스템 관리자 준비 문서 확인
- [ ] 모든 가이드 문서 읽기 완료
- [ ] 백업 및 롤백 절차 숙지
- [ ] 문제 해결 도구 설치 및 테스트
- [ ] 긴급 연락처 정리 완료

---

## 📚 추가 참고 자료

### 관련 시스템 문서
- `MIGRATION_README.md` - 기존 마이그레이션 문서
- `TEST_FRAMEWORK_README.md` - 테스트 프레임워크 가이드
- `END_TO_END_TEST_GUIDE.md` - 통합 테스트 가이드

### 기술 구현 파일
- `naming_convention_manager.py` - 네이밍 컨벤션 관리 시스템
- `file_renaming_system.py` - 파일 리네이밍 시스템
- `posco_file_renamer.py` - CLI 도구

---

**📖 이 인덱스를 통해 상황에 맞는 적절한 문서를 빠르게 찾아 효율적으로 마이그레이션을 진행하세요.**