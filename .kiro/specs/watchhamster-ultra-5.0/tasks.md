# WatchHamster Ultra 5.0 구현 작업 목록

## 📋 개요

이 작업 목록은 WatchHamster Ultra 5.0의 AI/ML 기능을 단계별로 구현하기 위한 실행 가능한 작업들입니다.
각 작업은 Requirements와 Design 문서를 기반으로 작성되었으며, 코드 작성/수정/테스트에 집중합니다.

## 🎯 작업 원칙

- **한 번에 하나의 작업만 수행**: 각 작업은 독립적으로 완료 가능
- **점진적 통합**: 기존 시스템을 유지하면서 새 기능 추가
- **테스트는 선택적**: 핵심 기능 구현 후 필요시 테스트 작성
- **Requirements 참조**: 각 작업은 관련 Requirements 명시

## 📅 Phase 1: MVP 핵심 기능 (4주)

### 🔥 HIGH PRIORITY - 즉시 시작 가능


- [x] 1. 프로젝트 환경 설정 및 의존성 설치
  - Python 백엔드에 scikit-learn==1.3.2, numpy, pandas 설치
  - requirements.txt 업데이트 및 호환성 테스트
  - 가상환경 설정 확인
  - _Requirements: 전체 시스템 기반_

- [ ] 2. AI 분석 엔진 기본 구조 구축
  - [ ] 2.1 디렉토리 구조 생성
    - `python-backend/core/ai/` 디렉토리 생성
    - `python-backend/core/ai/__init__.py` 생성
    - `python-backend/models/ai_models.py` 생성
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ] 2.2 AIAnalysisEngine 클래스 기본 구조 구현
    - `python-backend/core/ai/analysis_engine.py` 생성
    - 레거시 `recovery_config/ai_analysis_engine.py` (681줄) 참조
    - 기본 클래스 구조 및 초기화 로직 구현
    - 감정 키워드 사전 정의 (POSITIVE/NEGATIVE/NEUTRAL)
    - 발행 일정 설정 (newyork-market-watch, kospi-close 등)
    - _Requirements: 1.1, 1.2_
  
  - [ ] 2.3 시장 상황 분석 메서드 구현
    - `analyze_market_situation()` 메서드 구현
    - 뉴스 데이터 기반 시장 감정 분석 로직
    - 감정 점수 계산 (-1 ~ 1)
    - 신뢰도 계산 (0 ~ 1)
    - _Requirements: 1.1, 1.2_
  
  - [ ] 2.4 투자 전략 생성 메서드 구현
    - `generate_investment_strategy()` 메서드 구현
    - 시장 감정 기반 전략 타입 결정 (aggressive/balanced/conservative/defensive)
    - 포트폴리오 배분 계산 (주식/채권/현금 비율)
    - 단기/중기/장기 권장사항 생성
    - _Requirements: 1.3_

- [ ] 3. 고급 감성 분석 시스템 구현
  - [ ] 3.1 SentimentAnalyzer 클래스 생성
    - `python-backend/core/ai/sentiment_analyzer.py` 생성
    - 레거시 고급 감성분석 로직 참조
    - 6단계 감성 레벨 정의 (strong_positive ~ strong_negative)
    - 감성 패턴 및 가중치 시스템 구현
    - 부정어 사전 정의
    - _Requirements: 2.1, 2.3_
  
  - [ ] 3.2 HTML 태그 제거 로직 구현
    - `_clean_html_tags()` 메서드 구현
    - HTML 엔티티 디코딩
    - 정규식 기반 태그 제거
    - 연속 공백 정리
    - _Requirements: 2.4_
  
  - [ ] 3.3 문맥 기반 감성 분석 메서드 구현
    - `analyze_sentiment()` 메서드 구현
    - 부정어 처리 로직 (문맥 고려)
    - 키워드 가중치 적용
    - 감성 점수 및 신뢰도 계산
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 4. AI API 엔드포인트 구현
  - [ ] 4.1 AI 엔드포인트 파일 생성
    - `python-backend/api/ai_endpoints.py` 생성
    - FastAPI 라우터 설정
    - _Requirements: 1.1, 2.1_
  
  - [ ] 4.2 시장 분석 API 구현
    - `POST /api/ai/analyze` 엔드포인트 구현
    - AIAnalysisRequest/AIAnalysisResult 모델 정의
    - AIAnalysisEngine 호출 로직
    - 에러 처리 및 폴백 전략
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ] 4.3 감성 분석 API 구현
    - `POST /api/ai/sentiment` 엔드포인트 구현
    - SentimentRequest/SentimentResult 모델 정의
    - SentimentAnalyzer 호출 로직
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ] 4.4 main.py에 AI 라우터 추가
    - `python-backend/main.py` 수정
    - AI 라우터 import 및 등록
    - 기존 라우터와 충돌 없이 통합
    - _Requirements: 1.1, 2.1_

- [ ] 5. Dooray 웹훅 동적 리포트 생성 시스템
  - [ ] 5.1 DynamicReportGenerator 클래스 생성
    - `python-backend/core/webhook/dynamic_report_generator.py` 생성
    - 리포트 구조 생성 로직
    - 데이터 상태에 따른 섹션 변화 구현
    - _Requirements: 1.4_
  
  - [ ] 5.2 Dooray 메시지 포맷 구현
    - `_format_dooray_message()` 메서드 구현
    - 감성 분석 섹션 포맷
    - 투자 전략 섹션 포맷
    - 토픽 섹션 포맷 (조건부)
    - 이상 탐지 섹션 포맷 (조건부)
    - _Requirements: 1.4_
  
  - [ ] 5.3 AI 분석 API에 웹훅 전송 통합
    - `POST /api/ai/analyze` 엔드포인트 수정
    - 분석 완료 후 자동 웹훅 전송
    - _Requirements: 1.4_

- [ ] 6. 자동 복구 시스템 통합
  - [ ] 6.1 StabilityManager 클래스 포팅
    - `python-backend/core/recovery/` 디렉토리 생성
    - `python-backend/core/recovery/stability_manager.py` 생성
    - 레거시 `recovery_config/stability_manager.py` (413줄) 참조
    - 5가지 복구 액션 메서드 구현
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 6.2 복구 액션 메서드 구현
    - `_restart_service()` 구현 (서비스 재시작)
    - `_clear_cache()` 구현 (캐시 정리)
    - `_reset_config()` 구현 (설정 복원)
    - `_check_dependencies()` 구현 (의존성 확인)
    - `_cleanup_resources()` 구현 (리소스 정리)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 6.3 자동 복구 트리거 로직 구현
    - `auto_recovery()` 메서드 구현
    - 에러 타입별 복구 액션 매핑
    - 복구 성공/실패 로깅
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 6.4 Recovery API 엔드포인트 구현
    - `python-backend/api/recovery_endpoints.py` 생성
    - `POST /api/recovery/trigger` 엔드포인트 구현
    - `GET /api/recovery/actions` 엔드포인트 구현
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. 성능 최적화 엔진 구현
  - [ ] 7.1 PerformanceOptimizer 클래스 생성
    - `python-backend/utils/performance_optimizer.py` 생성
    - CPU/메모리 모니터링 로직
    - 임계값 설정 (CPU 80%, 메모리 800MB)
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ] 7.2 성능 메트릭 수집 메서드 구현
    - `get_current_metrics()` 메서드 구현
    - psutil 사용하여 CPU/메모리/디스크 사용률 수집
    - _Requirements: 6.1_
  
  - [ ] 7.3 최적화 권장사항 생성 로직 구현
    - `generate_recommendations()` 메서드 구현
    - 임계값 초과 시 권장사항 생성
    - _Requirements: 6.1, 6.4_
  
  - [ ] 7.4 자동 최적화 실행 메서드 구현
    - `cleanup_memory()` 메서드 구현 (메모리 정리)
    - `cleanup_disk()` 메서드 구현 (디스크 정리)
    - 최적화 이력 로깅
    - _Requirements: 6.2, 6.3, 6.5_
  
  - [ ] 7.5 Performance API 엔드포인트 구현
    - `python-backend/api/performance_endpoints.py` 생성
    - `GET /api/performance/metrics` 엔드포인트 구현
    - `GET /api/performance/optimize` 엔드포인트 구현
    - `POST /api/performance/optimize/execute` 엔드포인트 구현
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 8. React UI 통합 - AI 분석 위젯
  - [ ] 8.1 TypeScript 타입 정의
    - `src/types/ai.ts` 생성
    - AIAnalysisResult, SentimentAnalysis, InvestmentStrategy 인터페이스 정의
    - SentimentLevel, InvestmentStrategyType 타입 정의
    - _Requirements: 1.1, 2.1_
  
  - [ ] 8.2 useAIAnalysis 커스텀 훅 생성
    - `src/hooks/useAIAnalysis.ts` 생성
    - AI 분석 API 호출 로직
    - 로딩/에러 상태 관리
    - WebSocket 실시간 업데이트 연동
    - _Requirements: 1.1, 2.1_
  
  - [ ] 8.3 AIAnalysisWidget 컴포넌트 생성
    - `src/components/AI/AIAnalysisWidget.tsx` 생성
    - Chakra UI Card 레이아웃
    - 로딩/에러 상태 표시
    - 하위 컴포넌트 통합 (SentimentChart, InvestmentStrategyCard, TopicCloud)
    - _Requirements: 1.1, 2.1_
  
  - [ ] 8.4 SentimentChart 컴포넌트 생성
    - `src/components/AI/SentimentChart.tsx` 생성
    - 감성 점수 프로그레스 바 (Chakra UI Progress)
    - 감성 레벨별 색상 매핑
    - 신뢰도 표시
    - 키워드 태그 표시 (Chakra UI Tag)
    - _Requirements: 2.1, 2.5_
  
  - [ ] 8.5 InvestmentStrategyCard 컴포넌트 생성
    - `src/components/AI/InvestmentStrategyCard.tsx` 생성
    - 포트폴리오 파이 차트 (Recharts)
    - 전략 타입 표시
    - 단기/중기/장기 권장사항 표시
    - _Requirements: 1.3_
  
  - [ ] 8.6 Dashboard에 AI 위젯 추가
    - `src/pages/Dashboard.tsx` 수정
    - AIAnalysisWidget 컴포넌트 import 및 배치
    - 기존 컴포넌트와 레이아웃 조정
    - _Requirements: 1.1, 2.1_

- [ ] 9. Phase 1 통합 테스트 및 검증
  - [ ] 9.1 AI 분석 엔드투엔드 테스트
    - 뉴스 데이터 입력 → AI 분석 → 웹훅 전송 → UI 표시 전체 플로우 검증
    - 응답 시간 3초 이내 확인
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ] 9.2 감성 분석 정확도 검증
    - 레거시 결과와 비교 (95% 이상 일치)
    - HTML 태그 제거 검증
    - 부정어 처리 검증
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ] 9.3 자동 복구 시나리오 테스트
    - 5가지 복구 액션 모두 검증
    - 복구 실패 시 폴백 전략 검증
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 9.4 성능 목표 달성 검증
    - 메모리 사용량 800MB 이하 확인
    - CPU 사용률 모니터링
    - 24시간 연속 운영 안정성 테스트
    - _Requirements: 6.1, 6.2, 6.3_



## 📅 Phase 2: ML 기능 확장 (6주)

### ⚡ MEDIUM PRIORITY - Phase 1 완료 후 시작

- [ ] 10. TF-IDF 및 LDA 토픽 모델링 시스템
  - [ ] 10.1 TopicModelingEngine 클래스 생성
    - `python-backend/core/ml/` 디렉토리 생성
    - `python-backend/core/ml/topic_modeling.py` 생성
    - scikit-learn TfidfVectorizer 설정
    - LatentDirichletAllocation 설정
    - _Requirements: 3.1, 3.2_
  
  - [ ] 10.2 TF-IDF 벡터화 구현
    - `extract_topics()` 메서드 구현
    - 1-gram 및 2-gram 설정
    - 최대 1000개 특징 추출
    - _Requirements: 3.1, 3.4_
  
  - [ ] 10.3 LDA 토픽 모델링 구현
    - LDA 학습 로직
    - 5개 이하 주요 토픽 식별
    - 각 토픽별 상위 5개 키워드 추출
    - _Requirements: 3.2, 3.3_
  
  - [ ] 10.4 모델 캐싱 시스템 구현
    - 학습된 모델 파일 저장 (joblib)
    - 모델 로드 및 재사용 로직
    - 메모리 캐시 관리
    - _Requirements: 3.2_
  
  - [ ] 10.5 Topic API 엔드포인트 구현
    - `python-backend/api/ml_endpoints.py` 생성
    - `POST /api/ml/topics` 엔드포인트 구현
    - TopicRequest/TopicResult 모델 정의
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ] 10.6 TopicCloud UI 컴포넌트 생성
    - `src/components/AI/TopicCloud.tsx` 생성
    - 토픽별 키워드 표시 (Chakra UI Badge)
    - 가중치에 따른 폰트 크기 조정
    - _Requirements: 3.5_

- [ ] 11. K-Means 클러스터링 이상 탐지 시스템
  - [ ] 11.1 AnomalyDetector 클래스 생성
    - `python-backend/core/ml/anomaly_detector.py` 생성
    - scikit-learn KMeans 설정 (5개 클러스터)
    - 임계값 설정 (2.0)
    - _Requirements: 4.1_
  
  - [ ] 11.2 클러스터링 학습 메서드 구현
    - `train_and_save()` 메서드 구현
    - 뉴스 데이터 기반 클러스터링 학습
    - 모델 파일 저장 (./models/kmeans_model.pkl)
    - _Requirements: 4.1, 4.5_
  
  - [ ] 11.3 이상 탐지 메서드 구현
    - `detect_anomaly()` 메서드 구현
    - 새로운 뉴스의 클러스터 예측
    - 클러스터 중심과의 거리 계산
    - 임계값 초과 시 이상치 판단
    - _Requirements: 4.2, 4.3_
  
  - [ ] 11.4 Anomaly API 엔드포인트 구현
    - `POST /api/ml/anomaly` 엔드포인트 구현
    - `POST /api/ml/models/train` 엔드포인트 구현
    - AnomalyRequest/AnomalyResult 모델 정의
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 11.5 이상 탐지 시 Dooray 알림 통합
    - 이상치 감지 시 즉시 웹훅 전송
    - 알림 메시지 포맷 구현
    - _Requirements: 4.4_

- [ ] 12. 동적 데이터 관리 시스템 통합
  - [ ] 12.1 DynamicDataManager 클래스 생성
    - `python-backend/core/data/` 디렉토리 생성
    - `python-backend/core/data/dynamic_data_manager.py` 생성
    - DataQuality Enum 정의 (5단계)
    - 품질 임계값 설정
    - _Requirements: 8.1_
  
  - [ ] 12.2 데이터 품질 평가 메서드 구현
    - `evaluate_data_quality()` 메서드 구현
    - 완성도/정확도/적시성 계산
    - 전체 품질 점수 계산
    - 품질 등급 결정
    - _Requirements: 8.1_
  
  - [ ] 12.3 뉴스 감성 데이터 수집 메서드 구현
    - `fetch_news_sentiment_data()` 메서드 구현
    - 감성 점수 (-1 ~ 1) 저장
    - 주요 토픽 저장
    - _Requirements: 8.2_
  
  - [ ] 12.4 저품질 데이터 자동 정리 구현
    - `cleanup_low_quality_data()` 메서드 구현
    - 품질 임계값 이하 데이터 제거
    - 정리 이력 로깅
    - _Requirements: 8.3_
  
  - [ ] 12.5 Data Management API 엔드포인트 구현
    - `python-backend/api/data_endpoints.py` 생성
    - `GET /api/data/quality` 엔드포인트 구현
    - `GET /api/data/sentiment-data` 엔드포인트 구현
    - `POST /api/data/cleanup` 엔드포인트 구현
    - `GET /api/data/quality/history` 엔드포인트 구현
    - _Requirements: 8.1, 8.2, 8.3, 8.5_
  
  - [ ] 12.6 데이터 품질 차트 UI 컴포넌트 생성
    - `src/components/Data/DataQualityChart.tsx` 생성
    - 시간대별 품질 변화 차트 (Recharts Line Chart)
    - 품질 등급별 색상 표시
    - _Requirements: 8.5_

- [ ] 13. Phase 2 통합 테스트 및 검증
  - [ ] 13.1 TF-IDF + LDA 토픽 추출 정확도 검증
    - 실제 뉴스 데이터로 토픽 추출 테스트
    - 토픽 키워드 의미 검증
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ] 13.2 K-Means 이상 탐지 정확도 검증
    - 정상 데이터와 이상 데이터 구분 테스트
    - False Positive/Negative 비율 측정
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 13.3 데이터 품질 평가 시스템 검증
    - 다양한 품질 수준의 데이터로 테스트
    - 자동 정리 기능 검증
    - _Requirements: 8.1, 8.3_



## 📅 Phase 3: 고급 기능 (8주)

### 🚀 LOW PRIORITY - Phase 2 완료 후 시작

- [ ] 14. Multi-LLM API 통합 시스템
  - [ ] 14.1 MultiLLMManager 클래스 생성
    - `python-backend/core/llm/` 디렉토리 생성
    - `python-backend/core/llm/multi_llm_manager.py` 생성
    - 모델 라우팅 설정 (analysis/summary/search)
    - 일일 비용 제한 설정 ($100/일)
    - _Requirements: 7.1_
  
  - [ ] 14.2 LLM API 클라이언트 구현
    - Claude API 클라이언트 (`_call_claude()`)
    - OpenAI API 클라이언트 (`_call_openai()`)
    - Gemini API 클라이언트 (`_call_gemini()`)
    - _Requirements: 7.1_
  
  - [ ] 14.3 응답 캐싱 시스템 구현
    - 캐시 키 생성 로직
    - 캐시 저장/조회 로직
    - TTL 관리 (1시간)
    - _Requirements: 7.1_
  
  - [ ] 14.4 AI 분석 결과 컨텍스트 통합
    - `generate_response_with_citations()` 메서드 구현
    - AI 분석 결과를 LLM 프롬프트에 포함
    - 출처 정보 포함
    - _Requirements: 7.2, 7.3_
  
  - [ ] 14.5 폴백 전략 구현
    - 비용 초과 시 템플릿 응답
    - API 실패 시 대체 모델 전환
    - _Requirements: 7.4_
  
  - [ ] 14.6 LLM API 엔드포인트 구현
    - `python-backend/api/llm_endpoints.py` 생성
    - `POST /api/llm/query` 엔드포인트 구현
    - `GET /api/llm/cost/status` 엔드포인트 구현
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 14.7 LLM 응답 UI 컴포넌트 생성
    - `src/components/LLM/LLMResponseCard.tsx` 생성
    - 응답 텍스트 표시
    - 출처 정보 표시
    - 비용 정보 표시
    - _Requirements: 7.5_

- [ ] 15. 배포 모니터링 시스템 통합
  - [ ] 15.1 DeploymentMonitor 클래스 생성
    - `python-backend/core/deployment/` 디렉토리 생성
    - `python-backend/core/deployment/deployment_monitor.py` 생성
    - DeploymentPhase Enum 정의 (11단계)
    - _Requirements: 9.1_
  
  - [ ] 15.2 배포 단계별 실행 메서드 구현
    - `_execute_phase()` 메서드 구현
    - 11단계 순차 실행 로직
    - 각 단계별 성공/실패 판단
    - _Requirements: 9.1_
  
  - [ ] 15.3 실시간 진행 상황 전송 구현
    - WebSocket을 통한 실시간 업데이트
    - 단계별 진행률 계산
    - _Requirements: 9.2_
  
  - [ ] 15.4 자동 롤백 시스템 구현
    - `_rollback()` 메서드 구현
    - 실패 단계 이전으로 복원
    - 롤백 로그 기록
    - _Requirements: 9.3_
  
  - [ ] 15.5 배포 통계 생성 및 웹훅 전송
    - `_generate_deployment_statistics()` 메서드 구현
    - 총 소요 시간, 성공률 계산
    - Dooray 웹훅으로 통계 전송
    - _Requirements: 9.4_
  
  - [ ] 15.6 Deployment API 엔드포인트 구현
    - `python-backend/api/deployment_endpoints.py` 생성
    - `POST /api/deployment/start` 엔드포인트 구현
    - `GET /api/deployment/status` 엔드포인트 구현
    - `GET /api/deployment/history` 엔드포인트 구현
    - _Requirements: 9.1, 9.2, 9.5_
  
  - [ ] 15.7 배포 진행 상황 UI 컴포넌트 생성
    - `src/components/Deployment/DeploymentProgress.tsx` 생성
    - 11단계 프로그레스 바
    - 각 단계별 상태 표시 (pending/running/success/failed)
    - _Requirements: 9.2_

- [ ] 16. 백업 및 복구 시스템 강화
  - [ ] 16.1 BackupManager 클래스 생성
    - `python-backend/core/backup/` 디렉토리 생성
    - `python-backend/core/backup/backup_manager.py` 생성
    - 백업 디렉토리 설정
    - 최대 백업 수 설정 (50개)
    - _Requirements: 10.1, 10.2_
  
  - [ ] 16.2 자동 백업 메서드 구현
    - `auto_backup_on_change()` 메서드 구현
    - 설정 변경 시 자동 백업 생성
    - 타임스탬프 기반 파일명 생성
    - _Requirements: 10.1_
  
  - [ ] 16.3 오래된 백업 정리 메서드 구현
    - `_cleanup_old_backups()` 메서드 구현
    - 최대 50개 유지
    - 90일 이상 백업 자동 삭제
    - _Requirements: 10.2_
  
  - [ ] 16.4 백업 복원 메서드 구현
    - `restore_from_backup()` 메서드 구현
    - 복원 전 현재 설정 백업
    - 백업 파일에서 설정 로드
    - _Requirements: 10.3, 10.4_
  
  - [ ] 16.5 Backup API 엔드포인트 구현
    - `python-backend/api/backup_endpoints.py` 생성
    - `POST /api/backup/create` 엔드포인트 구현
    - `GET /api/backup/list` 엔드포인트 구현
    - `POST /api/backup/restore` 엔드포인트 구현
    - _Requirements: 10.1, 10.4, 10.5_
  
  - [ ] 16.6 백업 관리 UI 컴포넌트 생성
    - `src/components/Backup/BackupManager.tsx` 생성
    - 백업 목록 표시 (날짜, 크기, 설명)
    - 백업 생성/복원 버튼
    - _Requirements: 10.5_

- [ ] 17. 암호화 및 보안 시스템 강화
  - [ ] 17.1 EncryptionManager 클래스 생성
    - `python-backend/core/security/` 디렉토리 생성
    - `python-backend/core/security/encryption_manager.py` 생성
    - Fernet (AES-256) 설정
    - 키 로테이션 주기 설정 (90일)
    - _Requirements: 11.1, 11.2_
  
  - [ ] 17.2 암호화 키 생성 및 로드 구현
    - `_load_or_generate_key()` 메서드 구현
    - 키 파일 존재 확인
    - 없으면 새 키 생성 및 저장
    - _Requirements: 11.1_
  
  - [ ] 17.3 API 키 암호화/복호화 메서드 구현
    - `encrypt_api_key()` 메서드 구현
    - `decrypt_api_key()` 메서드 구현
    - Base64 인코딩/디코딩
    - _Requirements: 11.1, 11.2_
  
  - [ ] 17.4 키 로테이션 메서드 구현
    - `rotate_encryption_key()` 메서드 구현
    - 새 키 생성
    - 모든 암호화된 데이터 재암호화
    - 키 저장
    - _Requirements: 11.3_
  
  - [ ] 17.5 로그 민감 정보 마스킹 구현
    - `mask_sensitive_data()` 메서드 구현
    - 정규식 패턴 정의 (api_key, password, token, webhook_url)
    - 민감 정보 자동 마스킹
    - _Requirements: 11.4_
  
  - [ ] 17.6 설정 내보내기 보안 처리 구현
    - `secure_export_settings()` 메서드 구현
    - 민감 데이터 포함 시 전체 암호화
    - 민감 데이터 제외 시 필드 제거
    - _Requirements: 11.5_

- [ ] 18. 실시간 이상 탐지 스트리밍 시스템
  - [ ] 18.1 StreamProcessor 클래스 생성
    - `python-backend/core/streaming/` 디렉토리 생성
    - `python-backend/core/streaming/stream_processor.py` 생성
    - 슬라이딩 윈도우 설정 (1000개)
    - 배치 크기 설정 (100개)
    - _Requirements: 12.1, 12.4_
  
  - [ ] 18.2 스트리밍 처리 메서드 구현
    - `process_stream()` 메서드 구현
    - 비동기 스트림 처리
    - 배치 단위 처리
    - 메모리 사용량 체크
    - _Requirements: 12.1, 12.4_
  
  - [ ] 18.3 배치 처리 및 이상 탐지 구현
    - `_process_batch()` 메서드 구현
    - ML 추론 (1초 이내)
    - 이상 감지 시 즉시 알림
    - _Requirements: 12.2, 12.3_
  
  - [ ] 18.4 메모리 관리 메서드 구현
    - `_check_memory_usage()` 메서드 구현
    - `_cleanup_buffer()` 메서드 구현
    - 메모리 부족 시 버퍼 정리
    - _Requirements: 12.4_
  
  - [ ] 18.5 Streaming API 엔드포인트 구현
    - `python-backend/api/streaming_endpoints.py` 생성
    - `WebSocket /api/streaming/anomaly` 엔드포인트 구현
    - `GET /api/streaming/status` 엔드포인트 구현
    - _Requirements: 12.1, 12.5_
  
  - [ ] 18.6 실시간 이상 탐지 UI 컴포넌트 생성
    - `src/components/Streaming/RealtimeAnomalyMonitor.tsx` 생성
    - WebSocket 연결 관리
    - 실시간 이상 탐지 알림 표시
    - 처리량/지연시간/이상 감지 횟수 표시
    - _Requirements: 12.5_

- [ ] 19. Phase 3 통합 테스트 및 검증
  - [ ] 19.1 Multi-LLM API 통합 테스트
    - Claude, GPT-4, Gemini 모두 호출 테스트
    - 비용 제한 검증
    - 폴백 전략 검증
    - _Requirements: 7.1, 7.4_
  
  - [ ] 19.2 배포 모니터링 시스템 테스트
    - 11단계 배포 프로세스 전체 검증
    - 실패 시 롤백 검증
    - 통계 생성 및 웹훅 전송 검증
    - _Requirements: 9.1, 9.3, 9.4_
  
  - [ ] 19.3 백업 및 복구 시스템 테스트
    - 자동 백업 생성 검증
    - 오래된 백업 정리 검증
    - 백업 복원 검증
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ] 19.4 암호화 시스템 테스트
    - API 키 암호화/복호화 검증
    - 키 로테이션 검증
    - 로그 마스킹 검증
    - _Requirements: 11.1, 11.3, 11.4_
  
  - [ ] 19.5 실시간 스트리밍 시스템 테스트
    - 장시간 운영 안정성 테스트 (24시간)
    - 메모리 누수 검증
    - 이상 탐지 정확도 검증
    - _Requirements: 12.1, 12.2, 12.3, 12.4_



## 📊 작업 통계

### Phase 1 (MVP 핵심 기능)
- **총 작업 수**: 9개 메인 작업
- **예상 기간**: 4주
- **우선순위**: HIGH
- **핵심 Requirements**: 1, 2, 5, 6

### Phase 2 (ML 기능 확장)
- **총 작업 수**: 4개 메인 작업
- **예상 기간**: 6주
- **우선순위**: MEDIUM
- **핵심 Requirements**: 3, 4, 8

### Phase 3 (고급 기능)
- **총 작업 수**: 6개 메인 작업
- **예상 기간**: 8주
- **우선순위**: LOW
- **핵심 Requirements**: 7, 9, 10, 11, 12

### 전체 통계
- **총 메인 작업**: 19개
- **총 서브 작업**: 약 100개
- **전체 예상 기간**: 18주 (약 4.5개월)
- **Requirements 커버리지**: 12/12 (100%)

## 🎯 작업 실행 가이드

### 작업 시작 전 체크리스트
1. ✅ Requirements 문서 읽기 완료
2. ✅ Design 문서 읽기 완료
3. ✅ 해당 작업의 Requirements 확인
4. ✅ 관련 레거시 코드 참조 (있는 경우)

### 작업 실행 원칙
- **한 번에 하나씩**: 각 작업은 독립적으로 완료
- **점진적 통합**: 기존 시스템을 유지하면서 추가
- **즉시 검증**: 작업 완료 후 바로 테스트
- **문서 참조**: Requirements와 Design 문서 항상 참조

### 작업 완료 기준
- ✅ 코드 작성 완료
- ✅ 기본 동작 검증 완료
- ✅ 기존 시스템과 충돌 없음
- ✅ Requirements 충족 확인

## 🚨 주의사항

### 필수 확인 사항
1. **메모리 제한**: 800MB 이하 유지
2. **응답 시간**: AI 분석 3초 이내
3. **기존 시스템**: 76개 기존 API 영향 없음
4. **폴백 전략**: 모든 AI/ML 기능에 폴백 구현

### 리스크 관리
- **High Risk**: Requirement 12 (실시간 스트리밍) - 메모리 관리 주의
- **Medium Risk**: Requirement 7 (Multi-LLM) - 비용 제한 필수
- **Low Risk**: Phase 1 작업들 - 레거시 코드 참조 가능

## 📝 참고 문서

### 레거시 코드 참조
- `recovery_config/ai_analysis_engine.py` (681줄) → Task 2
- `recovery_config/stability_manager.py` (413줄) → Task 6
- `레거시/POSCO_News_250808/core/__init__.py` → Task 3

### 관련 문서
- `.kiro/specs/watchhamster-ultra-5.0/requirements.md` - 전체 요구사항
- `.kiro/specs/watchhamster-ultra-5.0/design.md` - 상세 설계
- `python-backend/README.md` - 백엔드 구조 (기존)
- `src/README.md` - 프론트엔드 구조 (기존)

## 🎉 완료 후 기대 효과

### 정량적 효과
- **뉴스 분석 시간**: 90% 단축
- **시스템 장애**: 70% 감소
- **의사결정 속도**: 80% 향상
- **자동 복구율**: 80% 이상

### 정성적 효과
- **지능형 분석**: AI 기반 시장 감정 분석
- **자동화**: 장애 자동 복구 및 성능 최적화
- **예측 가능성**: 이상 패턴 사전 감지
- **운영 편의성**: 수동 개입 50% 감소

---

**작업을 시작하려면 tasks.md 파일을 열고 "Start task" 버튼을 클릭하세요!**

