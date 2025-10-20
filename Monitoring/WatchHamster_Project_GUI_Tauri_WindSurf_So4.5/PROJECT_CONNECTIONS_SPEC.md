# 🔗 WatchHamster 프로젝트 연결포인트 명세서

## 📋 개요
이 문서는 WatchHamster 프로젝트의 모든 연결포인트(URL, 토큰, API 키 등)와 설정값들을 정리한 명세서입니다.

---

## 🌐 현재 포트 구성

### ✅ 활성 포트
- **Frontend (Vite)**: `http://localhost:1420`
- **Backend (FastAPI)**: `http://localhost:9001` 
- **WebSocket**: `ws://localhost:9001/ws`
- **API Docs**: `http://localhost:9001/docs`

### ✅ 구형/비활성 포트 정리 완료  
- 모든 설정 파일에서 `9001` 포트로 통일 완료

---

## 🔧 환경변수 및 설정 파일

### 프론트엔드 환경변수
| 파일 | 상태 | 설정값 | 문제점 |
|------|------|--------|---------|
| `.env.example` | ✅ | `VITE_API_BASE_URL=http://localhost:9001` | 수정 완료 |
| `.env.development` | ✅ | `VITE_API_BASE_URL=http://localhost:9001` | 수정 완료 |
| `src/services/apiClient.ts` | ✅ | `baseURL: 'http://localhost:9001'` | 정상 |

### 백엔드 환경변수  
| 파일 | 상태 | 설정값 | 문제점 |
|------|------|--------|---------|
| `python-backend/.env.development` | ✅ | `PORT=9001` | 수정 완료 |
| `python-backend/utils/config.py` | ✅ | `api_port: int = 9001` | 정상 |

---

## 🔑 API 키 및 토큰

### 🚨 더미/플레이스홀더 값들
| 위치 | 값 | 상태 | 조치 필요 |
|------|-----|------|----------|
| `.env.example` | `SECRET_KEY=your-secret-key-here` | ❌ | 실제 값 설정 필요 |
| `python-backend/.env.development` | `SECRET_KEY=dev-secret-key-change-in-production` | ❌ | 실제 값 설정 필요 |

### InfoMax API 관련
| 항목 | 위치 | 상태 | 비고 |
|------|------|------|------|
| API 키 저장소 | `localStorage` (브라우저) | ⚠️ | 사용자 입력 의존 |
| API 베이스 URL | `https://global-api.einfomax.co.kr/apis/posco/news` | ✅ | 하드코딩됨 |

---

## 🔗 중요 연결포인트 점검

### REST API 엔드포인트
| 엔드포인트 | URL | 상태 | 테스트 결과 |
|------------|-----|------|-------------|
| 시스템 메트릭 | `GET /api/metrics/` | ✅ | 200 OK - 실데이터 반환 |
| 서비스 목록 | `GET /api/services/` | ✅ | 200 OK - 실데이터 반환 |
| 뉴스 상태 | `GET /api/news/status` | ✅ | 200 OK - 실데이터 반환 |
| 헬스체크 | `GET /health` | ✅ | 200 OK |

### WebSocket 연결
| 엔드포인트 | URL | 상태 | 기능 |
|------------|-----|------|------|
| 메인 WebSocket | `ws://localhost:9001/ws/` | ✅ | 실시간 상태 업데이트 |
| 로그 스트리밍 | `ws://localhost:9001/ws/logs` | ✅ | 실시간 로그 |

---

## 📂 설정 파일들

### Vite 설정
| 파일 | 상태 | 프록시 설정 |
|------|------|-------------|
| `vite.config.ts` | ✅ | `/api` → `http://localhost:9001` |
| | ✅ | `/ws` → `ws://localhost:9001` |

### 개발 서버 스크립트
| 파일 | 상태 | 포트 설정 |
|------|------|-----------|
| `scripts/dev-server.js` | ✅ | 9001 포트 사용 |
| `package.json` | ✅ | 개발 스크립트 정상 |

---

## ❌ 발견된 문제점들

### 1. 포트 불일치 문제 ✅ 해결완료
```yaml
상태: ✅ 수정 완료
조치 내용:
  - .env.example: VITE_API_BASE_URL=http://localhost:9001 ✅
  - .env.development: VITE_API_BASE_URL=http://localhost:9001 ✅
  - python-backend/.env.development: PORT=9001 ✅
```

### 2. 더미 시크릿 키
```yaml
문제: 프로덕션에서 사용하면 안 되는 개발용 시크릿 키
위치:
  - .env.example: SECRET_KEY=your-secret-key-here
  - python-backend/.env.development: SECRET_KEY=dev-secret-key-change-in-production
조치: 실제 보안 키로 교체 필요
```

### 3. 프론트엔드 데이터 연동 실패
```yaml
문제: API는 정상 작동하지만 UI에 0% 표시
원인: 스키마/타입 불일치로 추정
위치: src/hooks/useSystemMetrics.ts의 transformMetricData()
```

---

## ✅ 정상 작동 확인된 부분들

### API 응답
- ✅ `curl localhost:9001/api/metrics/` → 실시간 CPU/메모리 데이터
- ✅ `curl localhost:9001/api/services/` → 서비스 목록  
- ✅ `curl localhost:9001/api/news/status` → 뉴스 상태
- ✅ WebSocket 라우터 등록 완료

### 설정
- ✅ 백엔드 포트: 9001로 통일
- ✅ 프론트엔드 API 클라이언트: 9001 사용
- ✅ Vite 프록시: 9001로 설정
- ✅ WebSocket URL: ws://localhost:9001/ws

---

## 🔧 수정이 필요한 파일들

### ✅ 수정 완료
1. `.env.example` → `VITE_API_BASE_URL=http://localhost:9001` ✅
2. `.env.development` → `VITE_API_BASE_URL=http://localhost:9001` ✅ 
3. `python-backend/.env.development` → `PORT=9001` ✅

### 보안 관련 (프로덕션 배포 전)
1. 모든 `.env` 파일의 `SECRET_KEY` 실제 값으로 교체
2. InfoMax API 키 관리 방식 검토

### 데이터 연동 (UI 수정)
1. `src/types/system.ts` - SystemMetricsSchema 업데이트
2. `src/hooks/useSystemMetrics.ts` - 필드명 매핑 수정

---

## 📞 연락처 및 참조

- **API 문서**: http://localhost:9001/docs
- **WebSocket 테스트**: 브라우저 개발자 도구 → Network → WS 탭
- **로그 확인**: 윈드서프 터미널에서 실시간 로그 스트리밍

---

**📝 마지막 업데이트**: 2025-10-17 16:26 KST  
**🔍 상태**: 연결포인트 정리 완료, 포트 통일 완료 ✅
