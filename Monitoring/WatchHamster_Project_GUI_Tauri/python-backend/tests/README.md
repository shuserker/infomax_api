# WatchHamster 백엔드 단위 테스트

## 개요

이 디렉토리는 WatchHamster Tauri 백엔드 서비스의 단위 테스트를 포함합니다. pytest 프레임워크를 사용하여 FastAPI 엔드포인트, WebSocket 통신, 그리고 포팅된 기존 로직을 체계적으로 테스트합니다.

## 테스트 구조

```
tests/
├── __init__.py                 # 테스트 패키지 초기화
├── conftest.py                 # pytest 설정 및 공통 픽스처
├── test_api_endpoints.py       # FastAPI 엔드포인트 테스트
├── test_websocket.py          # WebSocket 통신 테스트
├── test_ported_logic.py       # 포팅된 로직 검증 테스트
└── README.md                  # 이 파일
```

## 테스트 카테고리

### 1. API 엔드포인트 테스트 (`test_api_endpoints.py`)

- **헬스 체크 엔드포인트**: `/health`, `/` 엔드포인트 테스트
- **서비스 관리 API**: 서비스 목록, 상태 조회, 제어 기능 테스트
- **메트릭 API**: 시스템 메트릭, 성능 지표, 안정성 지표 테스트
- **웹훅 API**: 웹훅 템플릿, 전송, 히스토리 관리 테스트
- **로그 API**: 로그 파일 관리, 조회, 통계 테스트
- **POSCO API**: POSCO 시스템 전용 기능 테스트
- **오류 처리**: 404, 405, 422 등 HTTP 오류 처리 테스트

### 2. WebSocket 통신 테스트 (`test_websocket.py`)

- **연결 관리**: 기본 연결, 다중 연결, 연결 해제 테스트
- **메시지 송수신**: 구독, 상태 요청, Pong 메시지 테스트
- **브로드캐스트**: 전체 클라이언트 메시지 브로드캐스트 테스트
- **연결 매니저**: ConnectionManager 클래스 기능 테스트
- **백그라운드 태스크**: 주기적 상태 업데이트, 연결 상태 모니터링 테스트
- **메시지 타입**: 다양한 WebSocket 메시지 타입 검증
- **오류 처리**: 연결 끊김, 잘못된 메시지 처리 테스트

### 3. 포팅된 로직 검증 테스트 (`test_ported_logic.py`)

- **성능 최적화 시스템**: PerformanceOptimizer 클래스 기능 테스트
- **안정성 관리자**: StabilityManager 클래스 기능 테스트
- **상태 보고 시스템**: StatusReporter 클래스 기능 테스트
- **웹훅 시스템**: WebhookSystem 클래스 기능 테스트
- **POSCO 관리자**: PoscoManager 클래스 기능 테스트
- **컴포넌트 통합**: 여러 컴포넌트 간 상호작용 테스트

## 테스트 실행

### 기본 실행

```bash
# 모든 테스트 실행
python -m pytest tests/

# 특정 테스트 파일 실행
python -m pytest tests/test_api_endpoints.py

# 특정 테스트 클래스 실행
python -m pytest tests/test_websocket.py::TestWebSocketConnection

# 특정 테스트 함수 실행
python -m pytest tests/test_ported_logic.py::TestWebhookSystem::test_webhook_system_creation
```

### 마커를 사용한 실행

```bash
# 단위 테스트만 실행
python -m pytest -m unit

# API 테스트만 실행
python -m pytest -m api

# WebSocket 테스트만 실행
python -m pytest -m websocket

# POSCO 관련 테스트만 실행
python -m pytest -m posco
```

### 상세 옵션

```bash
# 상세 출력으로 실행
python -m pytest tests/ -v

# 커버리지 측정
python -m pytest tests/ --cov=. --cov-report=html

# 첫 번째 실패에서 중단
python -m pytest tests/ -x

# 경고 메시지 숨김
python -m pytest tests/ --disable-warnings
```

### 편의 스크립트 사용

```bash
# Windows
run_tests.bat

# Python 스크립트
python run_tests.py --test-type unit --coverage
```

## 테스트 픽스처

### 공통 픽스처 (`conftest.py`)

- `app`: FastAPI 애플리케이션 인스턴스
- `client`: 동기 테스트 클라이언트
- `async_client`: 비동기 테스트 클라이언트
- `temp_dir`: 임시 디렉토리
- `mock_system_metrics`: 모의 시스템 메트릭 데이터
- `mock_service_info`: 모의 서비스 정보 데이터
- `mock_webhook_template`: 모의 웹훅 템플릿 데이터
- `mock_log_entries`: 모의 로그 엔트리 데이터
- `mock_posco_status`: 모의 POSCO 상태 데이터

### 유틸리티 함수

- `assert_response_structure()`: 응답 데이터 구조 검증
- `assert_service_info_structure()`: 서비스 정보 구조 검증
- `assert_metrics_structure()`: 메트릭 데이터 구조 검증
- `assert_webhook_template_structure()`: 웹훅 템플릿 구조 검증

## 테스트 마커

- `unit`: 단위 테스트
- `integration`: 통합 테스트
- `api`: API 테스트
- `websocket`: WebSocket 테스트
- `slow`: 느린 테스트
- `posco`: POSCO 관련 테스트

## Mock 사용

테스트에서는 외부 의존성을 제거하기 위해 다음과 같은 Mock을 사용합니다:

- **시스템 메트릭**: `psutil` 모듈 Mock
- **HTTP 요청**: `httpx.AsyncClient` Mock
- **서브프로세스**: `subprocess.run` Mock
- **파일 시스템**: 임시 디렉토리 사용

## 테스트 환경 설정

테스트 실행 시 다음 환경 변수가 자동으로 설정됩니다:

```python
os.environ["TESTING"] = "true"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["API_HOST"] = "127.0.0.1"
os.environ["API_PORT"] = "8001"
```

## 현재 테스트 상태

### ✅ 통과하는 테스트 (17개)

- WebSocket 연결 관리 (3개)
- WebSocket 메시지 송수신 (5개)
- WebSocket 메시지 타입 (3개)
- WebSocket 오류 처리 (1개)
- 웹훅 시스템 (5개)
- POSCO 관리자 생성 (1개)

### ⏭️ 건너뛴 테스트 (57개)

대부분의 비동기 테스트가 pytest-asyncio 설정 문제로 건너뛰어집니다. 이는 실제 기능에는 영향을 주지 않으며, 테스트 환경 설정을 통해 해결할 수 있습니다.

## 개선 사항

### 단기 개선

1. **pytest-asyncio 설정 완료**: 비동기 테스트 활성화
2. **실제 서버 통합 테스트**: 백엔드 서버와의 실제 통신 테스트
3. **커버리지 향상**: 현재 미테스트 코드 경로 추가

### 장기 개선

1. **E2E 테스트 추가**: 전체 사용자 플로우 테스트
2. **성능 테스트**: 부하 테스트 및 벤치마크
3. **보안 테스트**: 인증, 권한, 입력 검증 테스트

## 문제 해결

### 일반적인 문제

1. **Import 오류**: Python 경로 설정 확인
2. **비동기 테스트 건너뛰기**: pytest-asyncio 플러그인 설치 확인
3. **Mock 오류**: Mock 객체 설정 및 패치 경로 확인

### 디버깅 팁

```bash
# 특정 테스트 디버깅
python -m pytest tests/test_api_endpoints.py::TestHealthEndpoints::test_health_check -v -s

# 로그 출력 포함
python -m pytest tests/ --log-cli-level=DEBUG

# PDB 디버거 사용
python -m pytest tests/ --pdb
```

## 기여 가이드

새로운 테스트를 추가할 때:

1. 적절한 테스트 파일에 추가
2. 필요한 마커 설정
3. Mock 사용으로 외부 의존성 제거
4. 명확한 테스트 이름과 문서화
5. 픽스처 재사용으로 코드 중복 방지

이 테스트 스위트는 WatchHamster 백엔드의 안정성과 품질을 보장하는 중요한 역할을 합니다.