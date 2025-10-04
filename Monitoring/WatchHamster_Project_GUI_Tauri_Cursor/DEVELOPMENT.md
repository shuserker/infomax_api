# WatchHamster Tauri 개발 가이드

## 🚀 빠른 시작

### 1. 개발 환경 설정

```bash
# 프로젝트 클론 후
cd Monitoring/WatchHamster_Project_GUI_Tauri

# 개발 환경 자동 설정
npm run setup

# 개발 서버 시작
npm run dev
```

### 2. 개별 서비스 실행

```bash
# 프론트엔드만 실행
npm run dev:frontend

# 백엔드만 실행
npm run dev:backend

# Tauri 앱과 함께 실행
npm run dev:tauri
```

## 📋 시스템 요구사항

### 필수 요구사항
- **Node.js**: 18.0.0 이상
- **Python**: 3.8 이상
- **Rust**: 1.70 이상 (Tauri 빌드용)
- **Git**: 최신 버전

### 권장 도구
- **VS Code**: 개발 환경 설정 포함
- **Chrome/Edge**: 개발자 도구 사용

## 🛠️ 개발 환경 구성

### 프로젝트 구조
```
WatchHamster_Project_GUI_Tauri/
├── src/                    # React 프론트엔드
├── src-tauri/             # Rust Tauri 백엔드
├── python-backend/        # Python FastAPI 서비스
├── scripts/               # 개발 도구 스크립트
├── e2e/                   # E2E 테스트
├── docs/                  # 문서
└── .vscode/               # VS Code 설정
```

### 환경 변수 설정

#### 프론트엔드 (.env.development)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_DEBUG_MODE=true
```

#### 백엔드 (python-backend/.env.development)
```env
DEBUG=true
HOST=localhost
PORT=8000
LOG_LEVEL=debug
```

## 🔧 개발 도구

### 스크립트 명령어

#### 기본 개발
```bash
npm run dev              # 전체 개발 서버 시작
npm run dev:frontend     # React 개발 서버만
npm run dev:backend      # Python 백엔드만
npm run dev:tauri        # Tauri 앱 포함 전체 실행
```

#### 테스트
```bash
npm run test             # 단위 테스트 실행
npm run test:watch       # 테스트 감시 모드
npm run test:e2e         # E2E 테스트
npm run test:integration # 통합 테스트
```

#### 빌드
```bash
npm run build            # 프론트엔드 빌드
npm run build:tauri      # Tauri 앱 빌드
```

#### 디버깅
```bash
npm run debug            # 디버깅 도구
npm run debug:full       # 전체 시스템 진단
npm run debug:monitor    # 실시간 로그 모니터링
```

#### 유지보수
```bash
npm run setup            # 개발 환경 재설정
npm run clean            # 빌드 파일 정리
npm run clean:all        # 모든 의존성 정리
npm run health           # 시스템 상태 확인
```

### VS Code 설정

#### 권장 확장 프로그램
- **ESLint**: 코드 품질 검사
- **Prettier**: 코드 포맷팅
- **Python**: Python 개발 지원
- **Rust Analyzer**: Rust 개발 지원
- **Tauri**: Tauri 개발 지원
- **Playwright**: E2E 테스트 지원

#### 디버깅 설정
- **F5**: 전체 개발 환경 시작
- **Ctrl+Shift+P** → "Tasks: Run Task" → 원하는 작업 선택

## 🧪 테스트 가이드

### 테스트 구조
```
src/
├── components/
│   └── __tests__/         # 컴포넌트 테스트
├── hooks/
│   └── __tests__/         # 커스텀 훅 테스트
├── services/
│   └── __tests__/         # 서비스 레이어 테스트
└── test/
    ├── integration/       # 통합 테스트
    └── performance/       # 성능 테스트

e2e/                       # E2E 테스트
python-backend/tests/      # Python 백엔드 테스트
```

### 테스트 실행

#### 단위 테스트
```bash
# 모든 테스트 실행
npm run test

# 특정 파일 테스트
npm run test -- src/components/Dashboard

# 감시 모드
npm run test:watch
```

#### 통합 테스트
```bash
# API 통합 테스트
npm run test:integration

# 서비스별 통합 테스트
npm run test:services:integration
```

#### E2E 테스트
```bash
# 헤드리스 모드
npm run test:e2e

# UI 모드 (브라우저 표시)
npm run test:e2e:ui
```

### 테스트 작성 가이드

#### React 컴포넌트 테스트
```typescript
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { MyComponent } from './MyComponent';

test('컴포넌트가 올바르게 렌더링됨', () => {
  render(
    <ChakraProvider>
      <MyComponent />
    </ChakraProvider>
  );
  
  expect(screen.getByText('예상 텍스트')).toBeInTheDocument();
});
```

#### API 테스트
```typescript
import { describe, it, expect } from 'vitest';
import { apiClient } from '../services/api';

describe('API 클라이언트', () => {
  it('서비스 목록을 가져옴', async () => {
    const services = await apiClient.getServices();
    expect(services).toBeDefined();
    expect(Array.isArray(services)).toBe(true);
  });
});
```

## 🔍 디버깅 가이드

### 개발 도구 사용

#### 시스템 진단
```bash
# 전체 시스템 상태 확인
npm run debug:full

# 네트워크 연결 테스트
npm run health

# 실시간 로그 모니터링
npm run debug:monitor
```

#### 개별 컴포넌트 디버깅
```bash
# 포트 사용 상태 확인
node scripts/debug-tools.js ports

# 프로세스 상태 확인
node scripts/debug-tools.js processes

# 의존성 상태 확인
node scripts/debug-tools.js deps
```

### 일반적인 문제 해결

#### 1. 포트 충돌
```bash
# 포트 사용 상태 확인
npm run debug ports

# 프로세스 종료 (Windows)
taskkill /f /im python.exe
taskkill /f /im node.exe

# 프로세스 종료 (macOS/Linux)
pkill -f python
pkill -f node
```

#### 2. 의존성 문제
```bash
# 의존성 재설치
npm run clean:all
npm run setup
```

#### 3. Python 환경 문제
```bash
# 가상환경 재생성
cd python-backend
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. Rust/Tauri 문제
```bash
# Rust 의존성 재빌드
cd src-tauri
cargo clean
cargo build
```

## 🚀 성능 최적화

### 개발 중 성능 모니터링
```bash
# 성능 테스트 실행
npm run test:performance

# 메모리 사용량 모니터링
npm run debug:monitor
```

### 빌드 최적화
```bash
# 프로덕션 빌드 분석
npm run build -- --analyze

# 번들 크기 확인
npm run build && ls -la dist/
```

## 📚 추가 리소스

### 문서
- [API 참조](./docs/API_REFERENCE.md)
- [마이그레이션 가이드](./docs/MIGRATION_GUIDE.md)
- [배포 가이드](./docs/DEPLOYMENT.md)

### 외부 문서
- [Tauri 공식 문서](https://tauri.app/)
- [React 공식 문서](https://react.dev/)
- [Chakra UI 문서](https://chakra-ui.com/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

## 🤝 기여 가이드

### 코드 스타일
- **ESLint + Prettier** 설정 준수
- **TypeScript** 타입 안정성 유지
- **테스트 커버리지** 80% 이상 유지

### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 프로세스 또는 보조 도구 변경
```

### Pull Request 절차
1. 기능 브랜치 생성
2. 개발 및 테스트
3. 코드 리뷰 요청
4. 승인 후 메인 브랜치 병합

---

## 🆘 도움이 필요한 경우

1. **시스템 진단 실행**: `npm run debug:full`
2. **로그 확인**: `npm run debug:monitor`
3. **이슈 리포트**: GitHub Issues에 진단 결과와 함께 문제 보고

개발 중 문제가 발생하면 언제든지 도움을 요청하세요! 🚀