# 맥 환경 이전 후 검증 요구사항

## 개요

WatchHamster Tauri 프로젝트를 윈도우에서 맥으로 이전한 후 모든 기능이 정상 작동하는지 검증하는 체크리스트

## 요구사항

### 요구사항 1

**사용자 스토리:** 개발자로서 맥 환경에서 개발 서버가 정상 실행되기를 원한다

#### 수락 기준
1. WHEN `npm run dev` 실행 THEN 개발 서버가 정상 시작되어야 함
2. WHEN 서버 시작 THEN http://localhost:1420 접속이 가능해야 함
3. WHEN 브라우저 접속 THEN WatchHamster 대시보드가 표시되어야 함

### 요구사항 2

**사용자 스토리:** 개발자로서 백엔드 API가 맥에서 정상 작동하기를 원한다

#### 수락 기준
1. WHEN Python 백엔드 시작 THEN http://localhost:8000 접속이 가능해야 함
2. WHEN API 문서 접속 THEN http://localhost:8000/docs가 표시되어야 함
3. WHEN 헬스체크 호출 THEN /health 엔드포인트가 응답해야 함

### 요구사항 3

**사용자 스토리:** 개발자로서 크로스 플랫폼 스크립트가 맥에서 작동하기를 원한다

#### 수락 기준
1. WHEN `./setup.sh` 실행 THEN 모든 의존성이 설치되어야 함
2. WHEN `./run-dev.sh` 실행 THEN 개발 서버가 시작되어야 함
3. WHEN `./stop.sh` 실행 THEN 모든 프로세스가 종료되어야 함

### 요구사항 4

**사용자 스토리:** 개발자로서 실시간 기능이 맥에서 정상 작동하기를 원한다

#### 수락 기준
1. WHEN WebSocket 연결 THEN 실시간 데이터가 수신되어야 함
2. WHEN 대시보드 접속 THEN 실시간 차트가 업데이트되어야 함
3. WHEN 로그 페이지 접속 THEN 실시간 로그가 표시되어야 함

### 요구사항 5

**사용자 스토리:** 개발자로서 빌드 프로세스가 맥에서 정상 작동하기를 원한다

#### 수락 기준
1. WHEN `npm run build` 실행 THEN 프로덕션 빌드가 성공해야 함
2. WHEN `npm run test` 실행 THEN 모든 테스트가 통과해야 함
3. WHEN Tauri 빌드 실행 THEN 네이티브 앱이 생성되어야 함