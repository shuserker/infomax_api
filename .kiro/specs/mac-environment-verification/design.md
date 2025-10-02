# 맥 환경 검증 설계

## 개요

맥 환경 이전 후 체계적인 검증을 위한 자동화된 체크리스트와 테스트 스크립트 설계

## 아키텍처

### 검증 단계
1. **환경 설정 검증**: Node.js, Python, 의존성 확인
2. **서버 실행 검증**: 프론트엔드/백엔드 서버 시작 확인
3. **기능 검증**: API, WebSocket, 실시간 기능 테스트
4. **빌드 검증**: 프로덕션 빌드 및 테스트 실행

## 구성 요소

### 1. 환경 검증 스크립트 (`verify-mac-environment.sh`)
- Node.js 버전 확인 (>= 20.19.0)
- Python 버전 확인 (>= 3.8)
- 필수 패키지 설치 상태 확인
- 포트 사용 가능성 확인 (1420, 8000)

### 2. 서버 검증 스크립트 (`verify-servers.sh`)
- 개발 서버 시작 테스트
- 백엔드 API 응답 확인
- WebSocket 연결 테스트
- 헬스체크 엔드포인트 확인

### 3. 기능 검증 스크립트 (`verify-features.js`)
- 대시보드 페이지 로딩 확인
- 실시간 데이터 수신 테스트
- API 엔드포인트 응답 확인
- 로그 스트리밍 기능 테스트

### 4. 빌드 검증 스크립트 (`verify-build.sh`)
- 프로덕션 빌드 실행
- 단위 테스트 실행
- E2E 테스트 실행
- Tauri 빌드 테스트

## 데이터 모델

### 검증 결과 구조
```json
{
  "timestamp": "2025-01-02T10:00:00Z",
  "environment": "macOS",
  "results": {
    "environment": { "status": "pass", "details": {} },
    "servers": { "status": "pass", "details": {} },
    "features": { "status": "pass", "details": {} },
    "build": { "status": "pass", "details": {} }
  },
  "overall": "pass"
}
```

## 오류 처리

### 일반적인 맥 환경 이슈
- Homebrew 설치 누락
- Xcode Command Line Tools 미설치
- 권한 문제 (chmod +x)
- 포트 충돌

### 복구 전략
- 자동 의존성 설치 시도
- 대체 포트 제안
- 상세한 오류 메시지 제공
- 해결 방법 가이드 링크

## 테스트 전략

### 자동화된 검증
- 스크립트 기반 체크리스트
- JSON 형태 결과 출력
- CI/CD 통합 가능한 형태

### 수동 검증 항목
- 브라우저 UI 확인
- 사용자 인터랙션 테스트
- 성능 체감 확인