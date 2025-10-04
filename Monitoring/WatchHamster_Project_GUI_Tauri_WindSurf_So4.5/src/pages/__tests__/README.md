# 서비스 관리 페이지 테스트

이 디렉토리는 서비스 관리 페이지의 다양한 테스트를 포함합니다.

## 테스트 파일 구조

### 1. Services.test.tsx
- **목적**: 기본 단위 테스트
- **범위**: 개별 컴포넌트 기능 테스트
- **특징**: 
  - Mock 컴포넌트 사용
  - 빠른 실행 속도
  - 기본 렌더링 및 상호작용 테스트

### 2. Services.simple.test.tsx
- **목적**: 간소화된 통합 테스트
- **범위**: 페이지 전체 기능 테스트
- **특징**:
  - 실제 컴포넌트 사용 (일부 Mock)
  - 사용자 상호작용 시나리오 테스트
  - 접근성 및 성능 테스트 포함

### 3. Services.integration.test.tsx
- **목적**: 완전한 통합 테스트
- **범위**: 모든 컴포넌트 간 상호작용 테스트
- **특징**:
  - 실제 API 호출 시뮬레이션
  - 복잡한 사용자 워크플로우 테스트
  - 에러 처리 및 엣지 케이스 테스트

## 테스트 실행 방법

### 개별 테스트 실행
```bash
# 간단한 테스트만 실행
npx vitest run src/pages/__tests__/Services.simple.test.tsx

# 기본 단위 테스트 실행
npx vitest run src/pages/__tests__/Services.test.tsx

# 통합 테스트 실행 (문제 해결 후)
npx vitest run src/pages/__tests__/Services.integration.test.tsx
```

### 모든 서비스 페이지 테스트 실행
```bash
npm run test:services
```

### 특정 테스트 그룹 실행
```bash
# 서비스 제어 기능만 테스트
npx vitest run --grep "서비스 제어"

# 접근성 테스트만 실행
npx vitest run --grep "접근성"

# 성능 테스트만 실행
npx vitest run --grep "성능"
```

## 테스트 커버리지

### 현재 테스트 범위
- ✅ 페이지 기본 렌더링
- ✅ 서비스 카드 표시
- ✅ 서비스 상태 표시
- ✅ 서비스 제어 버튼 기능
- ✅ 토스트 알림 표시
- ✅ 서비스 정보 표시
- ✅ 그리드 레이아웃
- ✅ 접근성 기능
- ✅ 성능 테스트
- ✅ 관리 패널 렌더링

### 테스트되는 주요 기능
1. **서비스 카드 렌더링**
   - 6개 서비스 카드 표시
   - 서비스 이름, 설명, 상태 표시
   - 업타임 및 오류 정보 표시

2. **서비스 제어**
   - 시작/중지/재시작 버튼
   - 설정 버튼
   - 토스트 알림 표시

3. **상태 표시**
   - 실행 중, 중지됨, 오류 상태 배지
   - 상태별 적절한 제어 버튼 표시

4. **사용자 인터페이스**
   - 반응형 그리드 레이아웃
   - 접근성 준수
   - 키보드 네비게이션

5. **통합 기능**
   - POSCO 관리 패널 연동
   - 웹훅 관리 패널 연동

## 테스트 모킹 전략

### Mock 컴포넌트
- `PoscoManagementPanel`: 간단한 테스트 ID로 대체
- `WebhookManagement`: 간단한 테스트 ID로 대체

### Mock 서비스
- `useToast`: 토스트 호출 추적을 위한 Mock 함수
- API 서비스: HTTP 요청 시뮬레이션

### Mock 브라우저 API
- `matchMedia`: 반응형 디자인 테스트
- `localStorage`: 설정 저장 테스트
- `WebSocket`: 실시간 통신 테스트

## 테스트 데이터

### 서비스 목록
테스트에서 사용하는 6개의 모의 서비스:

1. **POSCO 뉴스 모니터** (실행 중)
2. **GitHub Pages 모니터** (중지됨)
3. **캐시 모니터** (실행 중)
4. **배포 시스템** (오류)
5. **메시지 시스템** (실행 중)
6. **웹훅 시스템** (실행 중)

### 테스트 시나리오
- 정상 상태 서비스 제어
- 오류 상태 서비스 복구
- 중지된 서비스 시작
- 설정 변경 및 저장

## 문제 해결

### 일반적인 테스트 오류

1. **Chakra UI 색상 모드 오류**
   ```
   TypeError: Cannot read properties of undefined (reading 'addListener')
   ```
   - 해결: `src/test/setup.ts`에서 `matchMedia` Mock 확인

2. **API Mock 오류**
   ```
   No "ApiServiceError" export is defined
   ```
   - 해결: API Mock에서 모든 필요한 export 포함

3. **중복 텍스트 선택 오류**
   ```
   Found multiple elements with the text: 실행 중
   ```
   - 해결: `getAllByText()` 사용 또는 더 구체적인 선택자 사용

### 성능 최적화

- 테스트 실행 시간 단축을 위해 불필요한 Mock 제거
- 복잡한 통합 테스트는 별도 파일로 분리
- 테스트 데이터 최소화

## 향후 개선 사항

1. **E2E 테스트 추가**
   - Playwright를 사용한 브라우저 테스트
   - 실제 사용자 시나리오 테스트

2. **시각적 회귀 테스트**
   - 스크린샷 비교 테스트
   - UI 변경 사항 자동 감지

3. **성능 벤치마크**
   - 렌더링 성능 측정
   - 메모리 사용량 모니터링

4. **접근성 테스트 강화**
   - axe-core 통합
   - 스크린 리더 호환성 테스트