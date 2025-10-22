# WatchHamster 고급 AI/ML 기능 통합 요구사항

## 📋 개요

레거시 버전들(`recovery_config`, `레거시/POSCO_News_250808`)에서 발굴된 고급 AI/ML 로직들을 최신 Tauri 버전(`Monitoring/WatchHamster_Project_GUI_Tauri`)에 통합하여 지능형 뉴스 분석, 자동 복구, 성능 최적화 기능을 구현합니다.

## 🎯 프로젝트 목표

**최신 Tauri 버전에 현재 없는** 레거시 AI/ML 기능들을 이식합니다:
- `recovery_config/ai_analysis_engine.py` (681줄) - 시장 감정 분석 + 투자 전략 생성
- `레거시/POSCO_News_250808/core/__init__.py` - TF-IDF/LDA 토픽 모델링 + 고급 감성분석
- `recovery_config/stability_manager.py` (413줄) - 자동복구 시스템 (5가지 복구 액션)
- `python-backend/utils/dynamic_data_manager.py` - 동적 데이터 관리
- `python-backend/utils/performance_optimizer.py` - 성능 최적화 엔진

## 용어 정의 (Glossary)

- **WatchHamster_Platform**: 기존 완성된 통합 플랫폼 (Tauri 4.5 버전)
- **AI_Module**: 플랫폼에 추가되는 AI/ML 기능 모듈 (신규)
- **ML_Module**: TF-IDF, LDA, K-Means 머신러닝 모듈 (신규)
- **Recovery_Module**: 자동복구 기능 모듈 (신규)
- **Performance_Module**: 성능 최적화 모듈 (신규)
- **System**: WatchHamster Platform + AI/ML 모듈 통합 시스템
- **Dooray_Webhook**: Dooray 메신저 웹훅 알림 시스템 (기존)
- **INFOMAX_API**: 뉴스 데이터 제공 외부 API (기존)

## 📊 요구사항

### Requirement 1: AI 시장 분석 엔진 통합

**User Story:** 투자 분석가로서 뉴스 데이터를 기반으로 시장 감정을 자동 분석하고 투자 전략을 추천받고 싶습니다.

#### Acceptance Criteria

1. WHEN 뉴스 데이터를 입력하면 THEN AI_Analysis_Engine SHALL 시장 감정(긍정/부정/중립)을 분석해야 합니다
2. WHEN 시장 감정이 분석되면 THEN System SHALL 투자 전략(공격적/균형/보수적)을 자동 생성해야 합니다
3. WHEN 투자 전략이 생성되면 THEN System SHALL 포트폴리오 배분(주식/채권/현금 비율)을 제안해야 합니다
4. WHEN 분석 결과가 생성되면 THEN System SHALL 동적 리포트를 생성하여 Dooray_Webhook으로 전송해야 합니다
5. WHEN 키워드 가중치를 설정하면 THEN AI_Analysis_Engine SHALL 가중치를 반영하여 분석해야 합니다

### Requirement 2: 고급 감성 분석 시스템 구현

**User Story:** 운영자로서 뉴스 제목과 내용의 감성을 정확히 파악하여 시장 동향을 예측하고 싶습니다.

#### Acceptance Criteria

1. WHEN 뉴스 텍스트를 분석하면 THEN News_Parser SHALL 6단계 감성 레벨(강한 긍정/긍정/약한 긍정/중립/부정/강한 부정)을 판단해야 합니다
2. WHEN 부정어가 포함되면 THEN System SHALL 문맥을 고려하여 감성을 역전시켜야 합니다
3. WHEN 키워드 가중치를 적용하면 THEN System SHALL 중요 키워드에 더 높은 가중치를 부여해야 합니다
4. WHEN HTML 태그가 포함되면 THEN News_Parser SHALL 자동으로 태그를 제거하고 순수 텍스트만 분석해야 합니다
5. WHEN 감성 분석 결과가 생성되면 THEN System SHALL 시각화된 차트와 함께 GUI에 표시해야 합니다

### Requirement 3: TF-IDF 및 LDA 토픽 모델링 시스템

**User Story:** 데이터 분석가로서 대량의 뉴스 데이터에서 주요 토픽과 키워드를 자동으로 추출하고 싶습니다.

#### Acceptance Criteria

1. WHEN 뉴스 데이터를 수집하면 THEN ML_Model SHALL TF-IDF 벡터화를 수행하여 중요 키워드를 추출해야 합니다
2. WHEN TF-IDF 벡터가 생성되면 THEN ML_Model SHALL LDA 토픽 모델링을 수행하여 5개 이하의 주요 토픽을 식별해야 합니다
3. WHEN 토픽이 식별되면 THEN System SHALL 각 토픽별 상위 5개 키워드를 추출해야 합니다
4. WHEN 1-gram 및 2-gram을 설정하면 THEN ML_Model SHALL 단일 단어와 2단어 조합을 모두 분석해야 합니다
5. WHEN 토픽 분석 결과가 생성되면 THEN System SHALL 토픽별 가중치와 키워드를 GUI에 시각화해야 합니다

### Requirement 4: K-Means 클러스터링 이상 탐지 시스템

**User Story:** 시스템 관리자로서 비정상적인 뉴스 패턴을 자동으로 감지하여 즉시 알림받고 싶습니다.

#### Acceptance Criteria

1. WHEN 뉴스 데이터가 수집되면 THEN ML_Model SHALL K-Means 클러스터링을 수행하여 5개 클러스터로 분류해야 합니다
2. WHEN 새로운 뉴스가 입력되면 THEN System SHALL 해당 뉴스가 속한 클러스터를 예측해야 합니다
3. WHEN 클러스터 중심과의 거리를 계산하면 THEN System SHALL 임계값을 초과하는 경우 이상치로 판단해야 합니다
4. WHEN 이상치가 감지되면 THEN System SHALL 즉시 Dooray_Webhook으로 알림을 전송해야 합니다
5. WHEN 클러스터링 모델을 학습하면 THEN System SHALL 모델을 파일로 저장하여 재사용 가능하게 해야 합니다

### Requirement 5: 자동 복구 시스템 통합

**User Story:** 시스템 관리자로서 장애 발생 시 자동으로 복구 조치가 수행되어 다운타임을 최소화하고 싶습니다.

#### Acceptance Criteria

1. WHEN 서비스가 중단되면 THEN Auto_Recovery_System SHALL 자동으로 서비스를 재시작해야 합니다
2. WHEN 캐시가 손상되면 THEN Auto_Recovery_System SHALL 캐시를 자동으로 정리해야 합니다
3. WHEN 설정 파일이 손상되면 THEN Auto_Recovery_System SHALL 기본 설정으로 자동 복원해야 합니다
4. WHEN 의존성 문제가 발생하면 THEN Auto_Recovery_System SHALL 의존성을 자동으로 확인하고 복구해야 합니다
5. WHEN 리소스가 부족하면 THEN Auto_Recovery_System SHALL 자동으로 리소스를 정리해야 합니다

### Requirement 6: 성능 최적화 엔진 구현

**User Story:** 시스템 관리자로서 시스템 리소스를 실시간으로 모니터링하고 자동으로 최적화하고 싶습니다.

#### Acceptance Criteria

1. WHEN CPU 사용률을 모니터링하면 THEN Performance_Optimizer SHALL 임계값 초과 시 최적화 권장사항을 생성해야 합니다
2. WHEN 메모리 사용률이 높으면 THEN Performance_Optimizer SHALL 자동으로 메모리 정리를 수행해야 합니다
3. WHEN 디스크 공간이 부족하면 THEN Performance_Optimizer SHALL 오래된 로그와 캐시를 자동 삭제해야 합니다
4. WHEN 성능 이슈가 감지되면 THEN System SHALL 최적화 권장사항을 GUI에 표시해야 합니다
5. WHEN 최적화가 수행되면 THEN System SHALL 최적화 이력을 로그에 기록해야 합니다

### Requirement 7: Multi-LLM API 통합 시스템

**User Story:** 개발자로서 다양한 LLM API(Claude, GPT-4, Gemini)를 통합하여 AI 분석 결과를 더욱 풍부하게 만들고 싶습니다.

#### Acceptance Criteria

1. WHEN LLM API를 호출하면 THEN Multi_LLM_Manager SHALL 용도별로 최적의 모델(분석/요약/검색)을 선택해야 합니다
2. WHEN AI 분석 결과를 LLM에 전달하면 THEN Multi_LLM_Manager SHALL 컨텍스트를 포함하여 응답을 생성해야 합니다
3. WHEN LLM 응답을 받으면 THEN System SHALL 출처와 함께 인용 정보를 포함해야 합니다
4. WHEN LLM API 호출이 실패하면 THEN Multi_LLM_Manager SHALL 대체 모델로 자동 전환해야 합니다
5. WHEN LLM 응답이 생성되면 THEN System SHALL 응답을 GUI에 표시하고 Dooray_Webhook으로 전송해야 합니다

### Requirement 8: 동적 데이터 관리 시스템 통합

**User Story:** 데이터 관리자로서 데이터 품질을 자동으로 평가하고 관리하고 싶습니다.

#### Acceptance Criteria

1. WHEN 데이터를 수집하면 THEN System SHALL 데이터 품질을 5단계(우수/좋음/보통/나쁨/심각)로 평가해야 합니다
2. WHEN 뉴스 감성 데이터를 수집하면 THEN System SHALL 감성 점수(-1~1)와 주요 토픽을 저장해야 합니다
3. WHEN 데이터 품질이 낮으면 THEN System SHALL 자동으로 데이터 정리 작업을 수행해야 합니다
4. WHEN 데이터가 업데이트되면 THEN System SHALL 실시간으로 GUI에 반영해야 합니다
5. WHEN 데이터 이력을 조회하면 THEN System SHALL 시간대별 데이터 품질 변화를 차트로 표시해야 합니다

### Requirement 9: 배포 모니터링 시스템 통합

**User Story:** DevOps 엔지니어로서 배포 프로세스를 11단계로 세분화하여 모니터링하고 싶습니다.

#### Acceptance Criteria

1. WHEN 배포를 시작하면 THEN System SHALL 11단계 배포 프로세스(초기화/사전체크/백업/HTML생성/브랜치전환 등)를 순차적으로 실행해야 합니다
2. WHEN 각 단계가 완료되면 THEN System SHALL 진행 상황을 실시간으로 GUI에 표시해야 합니다
3. WHEN 배포 단계가 실패하면 THEN System SHALL 자동으로 롤백을 수행해야 합니다
4. WHEN 배포가 완료되면 THEN System SHALL 배포 통계를 생성하여 Dooray_Webhook으로 전송해야 합니다
5. WHEN 배포 이력을 조회하면 THEN System SHALL 과거 배포 기록과 성공률을 차트로 표시해야 합니다

### Requirement 10: 백업 및 복구 시스템 강화

**User Story:** 시스템 관리자로서 설정과 데이터를 자동으로 백업하고 필요 시 즉시 복구하고 싶습니다.

#### Acceptance Criteria

1. WHEN 설정이 변경되면 THEN System SHALL 자동으로 백업을 생성해야 합니다
2. WHEN 백업을 생성하면 THEN System SHALL 최대 50개의 백업을 유지하고 오래된 백업을 자동 삭제해야 합니다
3. WHEN 설정 파일이 손상되면 THEN System SHALL 최신 백업에서 자동으로 복구해야 합니다
4. WHEN 백업을 복원하면 THEN System SHALL 복원 전 현재 설정을 백업해야 합니다
5. WHEN 백업 목록을 조회하면 THEN System SHALL 백업 날짜, 크기, 설명을 GUI에 표시해야 합니다

### Requirement 11: 암호화 및 보안 시스템 강화

**User Story:** 보안 관리자로서 민감한 데이터를 AES-256으로 암호화하고 키 로테이션을 자동화하고 싶습니다.

#### Acceptance Criteria

1. WHEN API 키를 저장하면 THEN System SHALL AES-256 알고리즘으로 암호화해야 합니다
2. WHEN 웹훅 URL을 저장하면 THEN System SHALL 암호화하여 설정 파일에 저장해야 합니다
3. WHEN 키 로테이션 주기가 도래하면 THEN System SHALL 자동으로 암호화 키를 갱신해야 합니다
4. WHEN 로그를 기록하면 THEN System SHALL 민감한 정보(API 키, 비밀번호)를 자동으로 마스킹해야 합니다
5. WHEN 설정을 내보내면 THEN System SHALL 민감한 데이터를 제거하거나 암호화하여 내보내야 합니다

### Requirement 12: 실시간 이상 탐지 스트리밍 시스템

**User Story:** 실시간 분석가로서 스트리밍 데이터에서 이상 패턴을 즉시 감지하고 알림받고 싶습니다.

#### Acceptance Criteria

1. WHEN 뉴스 데이터가 실시간으로 수집되면 THEN System SHALL 스트리밍 분석을 수행해야 합니다
2. WHEN 이상 패턴이 감지되면 THEN System SHALL 즉시 ML 추론을 수행하여 이상 여부를 판단해야 합니다
3. WHEN 이상이 확인되면 THEN System SHALL 1초 이내에 Dooray_Webhook으로 알림을 전송해야 합니다
4. WHEN 스트리밍 데이터를 처리하면 THEN System SHALL 메모리 사용량을 최소화하여 장시간 운영을 보장해야 합니다
5. WHEN 스트리밍 상태를 조회하면 THEN System SHALL 처리량, 지연시간, 이상 감지 횟수를 GUI에 표시해야 합니다

## 🔧 기술적 제약사항

### 아키텍처 요구사항
- Python 백엔드에 scikit-learn, numpy, pandas 패키지 추가
- TF-IDF, LDA, K-Means 모델을 위한 ML 파이프라인 구축
- 모델 학습 및 추론을 위한 비동기 처리 구현
- 학습된 모델을 파일로 저장하고 재사용 가능하게 구현
- Tauri Python 프로세스 메모리 제한 (2GB) 고려

### 호환성 요구사항
- 기존 WatchHamster Tauri 프로젝트 구조 유지
- 기존 API 엔드포인트와 호환성 보장
- 기존 Dooray 웹훅 형식 유지
- 기존 설정 파일 형식과 호환
- scikit-learn 1.3.x와 기존 pandas/numpy 호환성 확인

### 성능 요구사항
- AI 분석 응답 시간 3초 이내
- ML 모델 추론 시간 1초 이내
- 실시간 스트리밍 처리 지연 1초 이내
- 메모리 사용량 1GB 이하 유지
- AI 분석 동시 요청 최대 10개
- ML 모델 학습은 1개씩 순차 처리

### 보안 요구사항
- LLM API 키 AES-256 암호화 저장
- 민감한 데이터 로그 자동 마스킹
- 모델 파일 무결성 검증
- 외부 API 호출 시 TLS 1.3 사용

### 폴백 전략 (Fallback Strategy)
- AI 분석 실패 시 → 레거시 통계 분석으로 자동 대체
- LLM API 실패 시 → 템플릿 기반 응답으로 자동 대체
- ML 모델 로드 실패 시 → 규칙 기반 분석으로 자동 대체
- 메모리 부족 시 → 배치 크기 자동 축소 및 순차 처리

## 📈 성공 기준

### 기능적 성공 기준
1. 681줄 AI 분석 엔진 완전 이식 및 작동
2. TF-IDF + LDA 토픽 모델링 정상 작동
3. K-Means 클러스터링 이상 탐지 정상 작동
4. 자동 복구 시스템 5가지 복구 액션 모두 작동
5. Multi-LLM API 통합 및 응답 생성 정상 작동

### 성능적 성공 기준
1. AI 분석 응답 시간 3초 이내
2. ML 모델 추론 시간 1초 이내
3. 메모리 사용량 1GB 이하
4. 24시간 연속 운영 시 안정성 보장

### 사용성 성공 기준
1. GUI에서 AI 분석 결과 시각화
2. 실시간 이상 탐지 알림 수신
3. 자동 복구 작업 로그 확인 가능
4. 성능 최적화 권장사항 GUI 표시

## 🚀 우선순위 (현실적 단계별 구현)

### 🔥 Phase 1: MVP 핵심 기능 (4주) - HIGH PRIORITY
- **Requirement 1**: AI 시장 분석 엔진 통합 (이미 681줄 완성, 포팅만 필요)
- **Requirement 2**: 고급 감성 분석 시스템 (이미 구현됨, 포팅만 필요)
- **Requirement 5**: 자동 복구 시스템 통합 (운영 안정성 필수)
- **Requirement 6**: 성능 최적화 엔진 (24시간 운영 필수)

**목표**: 기존 레거시 로직 완전 이식 + 안정적 운영 기반 구축

### ⚡ Phase 2: ML 기능 확장 (6주) - MEDIUM PRIORITY
- **Requirement 3**: TF-IDF 및 LDA 토픽 모델링
- **Requirement 4**: K-Means 클러스터링 이상 탐지
- **Requirement 8**: 동적 데이터 관리 시스템

**목표**: 머신러닝 기반 지능형 분석 기능 추가

### 🚀 Phase 3: 고급 기능 (8주) - LOW PRIORITY
- **Requirement 7**: Multi-LLM API 통합
- **Requirement 9**: 배포 모니터링 시스템
- **Requirement 10**: 백업 및 복구 시스템 강화
- **Requirement 11**: 암호화 및 보안 시스템 강화
- **Requirement 12**: 실시간 이상 탐지 스트리밍 (⚠️ High Risk)

**목표**: 차세대 AI 기능 및 엔터프라이즈 기능 추가

## 📝 참고사항

### 기존 코드 참조 위치
- `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/레거시/POSCO_News_250808/core/__init__.py` (고급 감성분석)
- `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/recovery_config/ai_analysis_engine.py` (681줄 AI 엔진)
- `/Users/jy_lee/Desktop/GIT_DEV/infomax_api/Monitoring/WatchHamster_Project/core/` (자동복구 시스템)

### 발굴된 핵심 로직
- **AI 분석 엔진**: 681줄, 시장 감정 분석 + 투자 전략 생성
- **TF-IDF + LDA**: scikit-learn 기반 실제 ML 구현
- **고급 감성분석**: 가중치 + 부정어 처리
- **자동복구 시스템**: 5가지 복구 액션 (재시작/캐시정리/설정복원/의존성체크/리소스정리)
- **성능 최적화**: CPU/메모리 모니터링 + 최적화 권장

### 추가 구현 필요 사항
- K-Means 클러스터링 (기존 TF-IDF에 추가)
- Multi-LLM API 통합 (Claude, GPT-4, Gemini)
- React UI 연결 (백엔드 API → 프론트엔드)


## ⚠️ 리스크 분석 및 완화 방안

### High Risk 항목

#### 1. Requirement 12 (실시간 스트리밍) - 🔴 높음
**리스크**: 메모리 누수, 무한 스트림 처리, 장시간 운영 시 불안정

**완화 방안**:
- 슬라이딩 윈도우 적용 (최대 1000개 버퍼)
- 배치 처리 (100개 단위)
- 메모리 사용량 실시간 모니터링
- 임계값 초과 시 자동 버퍼 정리

#### 2. Requirement 7 (Multi-LLM API) - 🟡 중간
**리스크**: API 비용 폭발, 레이트 리미팅, 응답 지연

**완화 방안**:
- 일일 비용 제한 ($100/일)
- 응답 캐싱 (동일 쿼리 재사용)
- 스마트 라우팅 (용도별 최적 모델 선택)
- 폴백 전략 (API 실패 시 템플릿 응답)

#### 3. Requirement 4 (K-Means 클러스터링) - 🟡 중간
**리스크**: 초기 학습 데이터 부족, 클러스터 수 결정 어려움

**완화 방안**:
- 최소 100개 데이터 수집 후 학습 시작
- Elbow Method로 최적 클러스터 수 자동 결정
- 주기적 재학습 (주 1회)
- 이상치 임계값 동적 조정

### Medium Risk 항목

#### 4. Requirement 3 (TF-IDF + LDA) - 🟢 낮음
**리스크**: 한국어 토큰화 품질, 토픽 해석 어려움

**완화 방안**:
- 형태소 분석기 사용 (KoNLPy)
- 불용어 사전 구축
- 토픽 키워드 자동 라벨링
- 전문가 검증 프로세스

## 🧪 테스트 전략

### High Priority 테스트 (Phase 1)
1. **AI 분석 엔진 단위 테스트**
   - 681줄 로직 완전 검증
   - 기존 레거시 결과와 100% 일치 확인
   - 엣지 케이스 처리 검증

2. **감성분석 정확도 테스트**
   - 기존 결과와 비교 (정확도 95% 이상)
   - 가중치 시스템 검증
   - 부정어 처리 검증

3. **자동복구 시스템 시나리오 테스트**
   - 5가지 복구 액션 모두 검증
   - 복구 실패 시 폴백 전략 검증
   - 연쇄 장애 시나리오 테스트

4. **성능 목표 달성 검증**
   - AI 분석 응답 시간 3초 이내
   - 메모리 사용량 1GB 이하
   - 24시간 연속 운영 안정성

### Medium Priority 테스트 (Phase 2)
5. **ML 모델 추론 정확도 검증**
   - TF-IDF 키워드 추출 정확도
   - LDA 토픽 분류 정확도
   - K-Means 이상 탐지 정확도

6. **24시간 연속 운영 스트레스 테스트**
   - 메모리 누수 모니터링
   - CPU 사용률 추이 분석
   - 자동 복구 작동 횟수 측정

7. **통합 테스트**
   - 백엔드-프론트엔드 연동
   - WebSocket 실시간 업데이트
   - Dooray 웹훅 전송 검증

### Low Priority 테스트 (Phase 3)
8. **LLM API 통합 테스트**
9. **보안 및 암호화 테스트**
10. **배포 및 롤백 테스트**

## 📊 성공 지표 (KPI)

### 정량적 지표
- **응답 속도**: AI 분석 3초 이내 (목표: 2초)
- **메모리 사용량**: 1GB 이하 (목표: 800MB)
- **정확도**: 감성분석 95% 이상
- **가용성**: 99.9% 이상 (월 43분 이하 다운타임)
- **자동 복구율**: 장애의 80% 이상 자동 복구

### 정성적 지표
- **사용자 만족도**: 운영자 피드백 4.5/5.0 이상
- **운영 편의성**: 수동 개입 횟수 50% 감소
- **분석 품질**: 투자 전략 정확도 전문가 검증 통과

### 비즈니스 지표
- **업무 자동화 효과**: 뉴스 분석 시간 90% 단축
- **장애 감소율**: 시스템 장애 70% 감소
- **의사결정 속도**: 투자 전략 수립 시간 80% 단축

## 💡 구현 권장사항

### 즉시 조치 필요
1. **Requirement 5 (자동복구)를 Phase 1로 상향**
   - 운영 안정성의 핵심이므로 최우선 구현

2. **단계적 구현 전략 채택**
   - Phase 1: 기존 로직 포팅 (4주)
   - Phase 2: ML 기능 추가 (6주)
   - Phase 3: 고급 기능 (8주)

3. **에러 처리 표준화**
   ```python
   class AIAnalysisError(Exception):
       """AI 분석 실패 시 폴백 전략"""
       def __init__(self, message, fallback_result=None):
           self.fallback_result = fallback_result or "기본 통계 분석 결과"
   ```

4. **메모리 관리 강화**
   ```python
   class MemoryManager:
       def __init__(self, max_memory_gb=1):
           self.max_memory = max_memory_gb * 1024**3
           self.cleanup_threshold = 0.8  # 80% 도달 시 정리
   ```

### 기술적 개선사항
- 동시성 제어: AI 분석 요청 큐 관리
- 캐싱 전략: 동일 쿼리 결과 재사용
- 로깅 강화: 구조화된 로그 (JSON 형식)
- 모니터링: Prometheus + Grafana 연동 고려


## 📡 API 엔드포인트 설계 (기존 구조 확장)

### 기존 API (유지)
```python
# 기존 플랫폼 API - 변경 없음
GET  /api/metrics          # 시스템 메트릭 조회
GET  /api/services         # 서비스 상태 조회
POST /api/news/status      # 뉴스 상태 조회
GET  /api/system/status    # 시스템 상태 조회
```

### Phase 1 신규 AI API (추가)
```python
# AI 분석 API (신규)
POST /api/ai/analyze
- Request: { "news_data": {...}, "analysis_type": "market_sentiment" }
- Response: { "sentiment": {...}, "investment_strategy": {...}, "confidence": 0.85 }

# 감성분석 API (신규)
POST /api/ai/sentiment
- Request: { "text": "뉴스 제목 및 내용", "options": {...} }
- Response: { "score": 0.7, "level": "positive", "keywords": [...] }

# 자동복구 API (신규)
POST /api/recovery/trigger
- Request: { "action": "restart_service", "target": "infomax_monitor" }
- Response: { "success": true, "recovery_log": [...] }

# 성능 최적화 API (신규)
GET /api/performance/optimize
- Response: { "recommendations": [...], "current_metrics": {...} }
```

### Phase 2 확장 API
```python
# TF-IDF + LDA 토픽 추출 API
POST /api/ml/topics
- Request: { "news_texts": [...], "n_topics": 5 }
- Response: { "topics": [{"id": 1, "keywords": [...], "weight": 0.8}] }

# K-Means 이상탐지 API
POST /api/ml/anomaly
- Request: { "news_data": {...} }
- Response: { "is_anomaly": false, "distance": 1.2, "cluster_id": 3 }
```

### Phase 3 고급 API
```python
# Multi-LLM 쿼리 API
POST /api/llm/query
- Request: { "query": "시장 분석 요약", "model": "claude-3-sonnet" }
- Response: { "response": "...", "citations": [...], "cost": 0.05 }
```

## 🗂️ 데이터 모델 정의

### TypeScript 타입 정의 (프론트엔드)
```typescript
// src/types/ai.ts

interface AIAnalysisResult {
  timestamp: string;
  sentiment: {
    score: number;           // -1 ~ 1
    level: SentimentLevel;   // 'strong_positive' | 'positive' | 'weak_positive' | 'neutral' | 'negative' | 'strong_negative'
    confidence: number;      // 0 ~ 1
    keywords: string[];
  };
  investment_strategy: {
    type: 'aggressive' | 'balanced' | 'conservative' | 'defensive';
    confidence: number;
    portfolio: {
      stocks: number;
      bonds: number;
      cash: number;
    };
    recommendations: {
      short_term: string[];
      medium_term: string[];
      long_term: string[];
    };
  };
  topics?: Topic[];
  anomaly_detected?: boolean;
}

interface Topic {
  id: number;
  keywords: string[];
  weight: number;
  label?: string;
}

interface PerformanceMetrics {
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  uptime: number;
  error_count: number;
}
```

### Python 데이터 모델 (백엔드)
```python
# python-backend/models/ai.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class SentimentLevel(str, Enum):
    STRONG_POSITIVE = "strong_positive"
    POSITIVE = "positive"
    WEAK_POSITIVE = "weak_positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    STRONG_NEGATIVE = "strong_negative"

class InvestmentStrategyType(str, Enum):
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    DEFENSIVE = "defensive"

class SentimentAnalysis(BaseModel):
    score: float = Field(..., ge=-1, le=1)
    level: SentimentLevel
    confidence: float = Field(..., ge=0, le=1)
    keywords: List[str]

class PortfolioAllocation(BaseModel):
    stocks: float = Field(..., ge=0, le=1)
    bonds: float = Field(..., ge=0, le=1)
    cash: float = Field(..., ge=0, le=1)

class InvestmentStrategy(BaseModel):
    type: InvestmentStrategyType
    confidence: float
    portfolio: PortfolioAllocation
    recommendations: Dict[str, List[str]]

class AIAnalysisResult(BaseModel):
    timestamp: str
    sentiment: SentimentAnalysis
    investment_strategy: InvestmentStrategy
    topics: Optional[List[Dict]] = None
    anomaly_detected: Optional[bool] = None
```

## ⚙️ 환경 변수 및 설정 관리

### .env 파일 구성 (기존에 추가)
```bash
# 기존 설정 (유지)
PORT=9001
SECRET_KEY=dev-secret-key
DEBUG=true

# AI/ML 설정 (신규 추가)
SCIKIT_LEARN_VERSION=1.3.2
AI_ANALYSIS_TIMEOUT=3000  # 3초 (밀리초)
ML_MODEL_CACHE_DIR=./models
ML_MODEL_AUTO_RELOAD=true

# 성능 제한 (신규 추가)
PERFORMANCE_MEMORY_LIMIT=800  # 800MB (안전 마진 고려)
PERFORMANCE_CPU_THRESHOLD=80  # 80% 초과 시 경고
AI_CONCURRENT_REQUESTS=10  # 동시 요청 최대 10개

# LLM API 설정 (Phase 3, 신규 추가)
LLM_DAILY_COST_LIMIT=100  # $100/일
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600  # 1시간

# 자동복구 설정 (신규 추가)
AUTO_RECOVERY_ENABLED=true
AUTO_RECOVERY_MAX_ATTEMPTS=3
AUTO_RECOVERY_RETRY_DELAY=5  # 5초

# 로깅 설정 (신규 추가)
LOG_AI_ANALYSIS=true
```

## 🔧 메모리 사용량 최적화 전략

### 예상 메모리 사용량
```python
MEMORY_BREAKDOWN = {
    "AI_ENGINE": 200,           # MB (681줄 로직)
    "SCIKIT_LEARN_MODELS": 150, # MB (TF-IDF + LDA + K-Means)
    "NEWS_DATA_BUFFER": 100,    # MB (실시간 데이터)
    "PYTHON_OVERHEAD": 200,     # MB (인터프리터 등)
    "SAFETY_MARGIN": 150,       # MB (안전 여유분)
    "TOTAL_TARGET": 800         # MB (1GB 목표에서 안전 마진 고려)
}
```

### 최적화 기법
```python
# 1. 모델 캐싱 (메모리에 모델 상주)
class ModelCache:
    def __init__(self, max_memory_mb=150):
        self.cache = {}
        self.max_memory = max_memory_mb * 1024 * 1024
    
    def load_model(self, model_name):
        if model_name not in self.cache:
            # 메모리 체크 후 로드
            if self._check_memory():
                self.cache[model_name] = joblib.load(f"./models/{model_name}.pkl")
        return self.cache[model_name]

# 2. 배치 처리 (뉴스 데이터 100개씩 묶어서 처리)
class BatchProcessor:
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
    
    async def process_news_batch(self, news_list):
        for i in range(0, len(news_list), self.batch_size):
            batch = news_list[i:i+self.batch_size]
            await self._process_batch(batch)

# 3. 압축 저장 (모델 파일 gzip 압축)
import gzip
import joblib

def save_compressed_model(model, filename):
    with gzip.open(f"{filename}.pkl.gz", 'wb') as f:
        joblib.dump(model, f, compress=('gzip', 3))
```

## 🚧 예상 병목지점 및 해결책

### 병목지점 식별
```python
BOTTLENECKS = {
    "파일 I/O": {
        "문제": "모델 로딩 시 디스크 읽기 지연",
        "해결": "모델 캐싱, 압축 저장, SSD 사용"
    },
    "CPU 집약": {
        "문제": "TF-IDF 벡터화 + LDA 학습 시간 소요",
        "해결": "병렬 처리, 배치 크기 조정, 사전 학습 모델 사용"
    },
    "메모리": {
        "문제": "대량 뉴스 데이터 처리 시 메모리 부족",
        "해결": "스트리밍 처리, 배치 처리, 가비지 컬렉션 강화"
    },
    "네트워크": {
        "문제": "LLM API 호출 지연 (Phase 3)",
        "해결": "응답 캐싱, 타임아웃 설정, 비동기 호출"
    }
}
```

### 성능 목표 재조정
```python
# 현실적 성능 목표
PERFORMANCE_TARGETS = {
    "AI 분석 (Phase 1)": {
        "목표": "3초",
        "예상": "2-3초",
        "최적화 후": "1.5-2초"
    },
    "TF-IDF + LDA (Phase 2)": {
        "목표": "1초",
        "예상": "1-2초",
        "최적화 후": "0.5-1초"
    },
    "K-Means 추론 (Phase 2)": {
        "목표": "1초",
        "예상": "0.5초",
        "최적화 후": "0.3초"
    },
    "메모리 사용량": {
        "목표": "800MB",
        "예상": "750MB",
        "최대": "1GB"
    }
}
```

## 📅 주차별 상세 실행 계획 (Phase 1)

### Week 1: 환경 설정 및 AI 엔진 포팅
```yaml
Day 1-2 (월-화):
  - scikit-learn==1.3.2 설치 및 호환성 테스트
  - 기존 numpy/pandas 버전과 충돌 확인
  - 가상환경 설정 및 requirements.txt 업데이트

Day 3-5 (수-금):
  - recovery_config/ai_analysis_engine.py (681줄) 복사
  - python-backend/core/ai_analysis_engine.py로 포팅 시작
  - 기본 클래스 구조 및 초기화 로직 구현
```

### Week 2: 감성분석 및 API 구현
```yaml
Day 1-3 (월-수):
  - 레거시 감성분석 로직 포팅
  - sentiment_analyzer.py 구현
  - 가중치 시스템 및 부정어 처리 로직 이식

Day 4-5 (목-금):
  - 첫 번째 API 엔드포인트 구현 (/api/ai/analyze)
  - FastAPI 라우터 설정
  - React에서 테스트 호출 가능하도록 설정
```

### Week 3: 자동복구 시스템 및 UI 연동
```yaml
Day 1-3 (월-수):
  - recovery_config/stability_manager.py (413줄) 포팅
  - 5가지 복구 액션 구현
  - 자동복구 트리거 로직 구현

Day 4-5 (목-금):
  - React UI에 AI 분석 결과 표시 컴포넌트 개발
  - 실시간 WebSocket 업데이트 연동
  - 대시보드에 AI 분석 위젯 추가
```

### Week 4: 성능 최적화 및 통합 테스트
```yaml
Day 1-2 (월-화):
  - performance_optimizer.py 포팅
  - CPU/메모리 모니터링 구현
  - 최적화 권장사항 생성 로직 구현

Day 3-5 (수-금):
  - 통합 테스트 (AI 분석 → 감성분석 → 자동복구 → 성능최적화)
  - 버그 수정 및 성능 튜닝
  - Phase 1 완료 검증 (응답시간 3초, 메모리 800MB)
```


## 🏗️ 디렉토리 구조 (Option A: 점진적 확장)

### 현실적 구조 (기존 유지 + AI 추가)
```bash
python-backend/
├── api/                      # 기존 API (유지)
│   ├── metrics.py           # 기존
│   ├── services.py          # 기존
│   ├── news.py              # 기존
│   ├── system.py            # 기존
│   ├── settings.py          # 기존
│   ├── webhooks.py          # 기존
│   ├── websocket.py         # 기존
│   └── ai_endpoints.py      # ⭐ 신규 추가
│
├── core/                     # 기존 핵심 로직 (유지)
│   ├── ai/                  # ⭐ 신규 추가
│   │   ├── __init__.py
│   │   ├── analysis_engine.py    # 681줄 포팅
│   │   └── sentiment_analyzer.py # 고급 감성분석
│   │
│   ├── ml/                  # ⭐ 신규 추가
│   │   ├── __init__.py
│   │   ├── topic_modeling.py     # TF-IDF + LDA
│   │   └── anomaly_detector.py   # K-Means
│   │
│   ├── recovery/            # ⭐ 신규 추가
│   │   ├── __init__.py
│   │   └── stability_manager.py  # 413줄 포팅
│   │
│   ├── infomax_client.py    # 기존
│   ├── news_parser.py       # 기존
│   ├── watchhamster_monitor.py  # 기존
│   ├── webhook_sender.py    # 기존
│   └── system_monitor.py    # 기존
│
├── models/                   # 기존 데이터 모델 (유지)
│   ├── news.py              # 기존
│   ├── metrics.py           # 기존
│   ├── services.py          # 기존
│   ├── system.py            # 기존
│   ├── settings.py          # 기존
│   ├── webhooks.py          # 기존
│   └── ai_models.py         # ⭐ 신규 추가
│
├── utils/                    # 기존 유틸 (유지)
│   ├── config.py            # 기존
│   ├── logger.py            # 기존
│   ├── middleware.py        # 기존
│   └── performance_optimizer.py  # ⭐ 신규 추가
│
└── main.py                   # 기존 (AI 라우터만 추가)
```

### 장점
- ✅ **기존 코드 안정성 유지**: 검증된 구조 그대로 사용
- ✅ **개발 속도 최적화**: 리팩토링 없이 AI 기능 바로 추가
- ✅ **팀 학습 곡선 최소화**: 기존 구조에 익숙한 개발자 바로 투입
- ✅ **롤백 용이성**: AI 폴더만 제거하면 기존 시스템으로 복귀

## 🔄 기존 시스템과의 통합 방식

### FastAPI 라우터 추가 (main.py)
```python
# 기존 라우터 (유지)
from api.services import router as services_router
from api.news import router as news_router
from api.system import router as system_router

app.include_router(services_router, prefix="/api/services")
app.include_router(news_router, prefix="/api/news")
app.include_router(system_router, prefix="/api/system")

# AI 라우터 추가 (신규)
from api.ai_endpoints import router as ai_router
app.include_router(ai_router, prefix="/api/ai")
```

### React 컴포넌트 추가 (Dashboard.tsx)
```typescript
// 기존 컴포넌트 (유지)
<Dashboard>
  <SystemMetrics />        {/* 기존 */}
  <ServiceStatus />        {/* 기존 */}
  <NewsStatusCards />      {/* 기존 */}
  <GitStatusWidget />      {/* 기존 */}
  
  {/* AI 컴포넌트 추가 (신규) */}
  <AIAnalysisWidget />     {/* 신규 */}
  <SentimentChart />       {/* 신규 */}
  <InvestmentStrategy />   {/* 신규 */}
</Dashboard>
```

### 데이터베이스 테이블 추가 (기존 DB 확장)
```sql
-- 기존 테이블 (유지)
services, news_status, metrics, system_logs...

-- AI 테이블 추가 (신규)
CREATE TABLE ai_analysis_results (
    id INTEGER PRIMARY KEY,
    news_id TEXT,
    sentiment_score REAL,
    investment_strategy TEXT,
    confidence REAL,
    created_at TIMESTAMP
);

CREATE TABLE ml_model_cache (
    id INTEGER PRIMARY KEY,
    model_type TEXT,
    model_data BLOB,
    trained_at TIMESTAMP
);

CREATE TABLE recovery_logs (
    id INTEGER PRIMARY KEY,
    action_type TEXT,
    success BOOLEAN,
    details TEXT,
    executed_at TIMESTAMP
);
```

## 📅 현실적 개발 일정 (Option A 기반)

### Week 1: AI 모듈 기반 구축
```yaml
Day 1 (월):
  - python-backend/core/ai/ 디렉토리 생성
  - scikit-learn==1.3.2 설치 및 호환성 테스트
  - requirements.txt 업데이트

Day 2-3 (화-수):
  - recovery_config/ai_analysis_engine.py → core/ai/analysis_engine.py 포팅
  - 기본 클래스 구조 및 초기화 로직 구현
  - 시장 감정 분석 로직 이식

Day 4-5 (목-금):
  - 고급 감성분석 로직 포팅 (core/ai/sentiment_analyzer.py)
  - 가중치 시스템 및 부정어 처리 구현
  - 단위 테스트 작성
```

### Week 2: API 및 UI 통합
```yaml
Day 1-2 (월-화):
  - api/ai_endpoints.py 생성
  - POST /api/ai/analyze 엔드포인트 구현
  - POST /api/ai/sentiment 엔드포인트 구현
  - models/ai_models.py 데이터 모델 정의

Day 3-4 (수-목):
  - React AI 컴포넌트 개발 (AIAnalysisWidget.tsx)
  - 실시간 WebSocket 업데이트 연동
  - 대시보드에 AI 위젯 추가

Day 5 (금):
  - 통합 테스트 (백엔드 ↔ 프론트엔드)
  - 버그 수정 및 성능 튜닝
```

### Week 3: 자동복구 및 성능 최적화
```yaml
Day 1-3 (월-수):
  - core/recovery/ 디렉토리 생성
  - stability_manager.py (413줄) 포팅
  - 5가지 복구 액션 구현
  - POST /api/recovery/trigger 엔드포인트 추가

Day 4-5 (목-금):
  - utils/performance_optimizer.py 구현
  - CPU/메모리 모니터링 로직 추가
  - GET /api/performance/optimize 엔드포인트 추가
```

### Week 4: ML 모델 및 최종 통합
```yaml
Day 1-2 (월-화):
  - core/ml/ 디렉토리 생성
  - topic_modeling.py (TF-IDF + LDA) 구현
  - anomaly_detector.py (K-Means) 구현

Day 3-4 (수-목):
  - 전체 시스템 통합 테스트
  - 성능 목표 달성 검증 (응답 3초, 메모리 800MB)
  - 버그 수정 및 최적화

Day 5 (금):
  - Phase 1 완료 검증
  - 문서화 및 배포 준비
```

## 🎯 성공 기준 (Option A 기반)

### 기존 플랫폼 안정성 (최우선)
- ✅ 기존 76개 API 성능 영향 0%
- ✅ 기존 기능 정상 작동 100%
- ✅ 기존 데이터베이스 무결성 유지
- ✅ 기존 WebSocket 연결 안정성 유지

### AI 모듈 성능 (신규)
- ✅ AI 분석 응답 시간 3초 이내
- ✅ 메모리 사용량 800MB 이하
- ✅ 자동복구 성공률 80% 이상
- ✅ 감성분석 정확도 95% 이상

### 통합 시스템 안정성
- ✅ AI 모듈 장애 시 기존 플랫폼 무영향
- ✅ 24시간 연속 운영 안정성
- ✅ 롤백 시간 5분 이내 (AI 폴더만 제거)
