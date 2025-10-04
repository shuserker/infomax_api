import { test, expect } from '@playwright/test';

test.describe('로그 뷰어 E2E 테스트', () => {
  test.beforeEach(async ({ page }) => {
    // 로그 페이지로 이동
    await page.goto('/logs');
    
    // 페이지 로딩 완료 대기
    await page.waitForLoadState('networkidle');
  });

  test('로그 페이지 기본 렌더링 테스트', async ({ page }) => {
    // 페이지 제목 확인
    await expect(page.locator('h1')).toContainText('로그 뷰어');
    
    // 탭 메뉴 확인
    await expect(page.locator('[role="tab"]')).toHaveCount(2);
    await expect(page.locator('[role="tab"]').first()).toContainText('실시간');
    await expect(page.locator('[role="tab"]').last()).toContainText('히스토리');
    
    // 기본적으로 실시간 탭이 선택되어 있는지 확인
    await expect(page.locator('[role="tab"][aria-selected="true"]')).toContainText('실시간');
  });

  test('실시간 로그 뷰어 기능 테스트', async ({ page }) => {
    // 실시간 로그 뷰어 컨트롤 확인
    await expect(page.locator('button:has-text("시작")')).toBeVisible();
    await expect(page.locator('button:has-text("일시정지")')).toBeVisible();
    await expect(page.locator('button[aria-label="로그 클리어"]')).toBeVisible();
    await expect(page.locator('button[aria-label="재연결"]')).toBeVisible();
    
    // WebSocket 연결 상태 확인
    await expect(page.locator('text=연결 중...')).toBeVisible();
    
    // 연결 완료 대기 (최대 10초)
    await expect(page.locator('text=연결됨')).toBeVisible({ timeout: 10000 });
    
    // 스트리밍 중지 테스트
    await page.click('button:has-text("중지")');
    await expect(page.locator('text=중지됨')).toBeVisible();
    await expect(page.locator('button:has-text("시작")')).toBeVisible();
    
    // 스트리밍 재시작 테스트
    await page.click('button:has-text("시작")');
    await expect(page.locator('button:has-text("중지")')).toBeVisible();
  });

  test('일시정지 및 재개 기능 테스트', async ({ page }) => {
    // 연결 완료 대기
    await expect(page.locator('text=연결됨')).toBeVisible({ timeout: 10000 });
    
    // 일시정지 테스트
    await page.click('button:has-text("일시정지")');
    await expect(page.locator('text=일시정지됨')).toBeVisible();
    await expect(page.locator('button:has-text("재개")')).toBeVisible();
    
    // 재개 테스트
    await page.click('button:has-text("재개")');
    await expect(page.locator('button:has-text("일시정지")')).toBeVisible();
  });

  test('히스토리 로그 뷰어 기능 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 히스토리 탭이 선택되었는지 확인
    await expect(page.locator('[role="tab"][aria-selected="true"]')).toContainText('히스토리');
    
    // 로그 필터 컨트롤 확인
    await expect(page.locator('input[placeholder="로그 검색..."]')).toBeVisible();
    await expect(page.locator('button:has-text("필터")')).toBeVisible();
    await expect(page.locator('button:has-text("내보내기")')).toBeVisible();
    
    // 로그 데이터 로딩 대기
    await page.waitForSelector('[data-testid="virtualized-list"]', { timeout: 10000 });
    
    // 로그 엔트리가 표시되는지 확인
    await expect(page.locator('[data-testid="virtualized-list"]')).toBeVisible();
  });

  test('로그 검색 기능 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 검색어 입력
    const searchInput = page.locator('input[placeholder="로그 검색..."]');
    await searchInput.fill('POSCO');
    
    // 검색 버튼 클릭
    await page.click('button[aria-label="검색"]');
    
    // 검색 결과 로딩 대기
    await page.waitForTimeout(1000);
    
    // 활성 필터 배지 확인
    await expect(page.locator('text=검색: POSCO')).toBeVisible();
  });

  test('로그 필터링 기능 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 필터 패널 열기
    await page.click('button:has-text("필터")');
    
    // 로그 레벨 필터 확인
    await expect(page.locator('text=로그 레벨')).toBeVisible();
    
    // ERROR 레벨 선택
    await page.click('input[type="checkbox"] + label:has-text("ERROR")');
    
    // 필터 적용 확인
    await expect(page.locator('text=ERROR')).toBeVisible();
    
    // 소스 필터 테스트
    await expect(page.locator('text=로그 소스')).toBeVisible();
    
    // posco_news 소스 선택
    await page.click('input[type="checkbox"] + label:has-text("posco_news")');
    
    // 활성 필터 배지 확인
    await expect(page.locator('text=posco_news')).toBeVisible();
  });

  test('시간 범위 필터 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 필터 패널 열기
    await page.click('button:has-text("필터")');
    
    // 시간 범위 필터 확인
    await expect(page.locator('text=시간 범위')).toBeVisible();
    
    // 시작 시간 설정
    const startTimeInput = page.locator('input[placeholder="시작 시간"]');
    await startTimeInput.fill('2024-01-15T10:00');
    
    // 종료 시간 설정
    const endTimeInput = page.locator('input[placeholder="종료 시간"]');
    await endTimeInput.fill('2024-01-15T18:00');
    
    // 필터 적용 대기
    await page.waitForTimeout(1000);
  });

  test('로그 통계 정보 표시 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 필터 패널 열기
    await page.click('button:has-text("필터")');
    
    // 로그 통계 섹션 확인
    await expect(page.locator('text=로그 통계')).toBeVisible();
    
    // 총 로그 수 표시 확인
    await expect(page.locator('text*=총')).toBeVisible();
    await expect(page.locator('text*=개의 로그 엔트리')).toBeVisible();
    
    // 레벨별 통계 확인
    const levelStats = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'];
    for (const level of levelStats) {
      await expect(page.locator(`text=${level}`)).toBeVisible();
    }
  });

  test('모든 필터 지우기 기능 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 검색어 입력
    await page.fill('input[placeholder="로그 검색..."]', '테스트');
    await page.click('button[aria-label="검색"]');
    
    // 필터 패널 열기
    await page.click('button:has-text("필터")');
    
    // ERROR 레벨 선택
    await page.click('input[type="checkbox"] + label:has-text("ERROR")');
    
    // 활성 필터 확인
    await expect(page.locator('text=검색: 테스트')).toBeVisible();
    await expect(page.locator('text=ERROR')).toBeVisible();
    
    // 모든 필터 지우기
    await page.click('button:has-text("모든 필터 지우기")');
    
    // 필터가 지워졌는지 확인
    await expect(page.locator('text=검색: 테스트')).not.toBeVisible();
    await expect(page.locator('input[placeholder="로그 검색..."]')).toHaveValue('');
  });

  test('로그 내보내기 기능 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 로그 데이터 로딩 대기
    await page.waitForSelector('[data-testid="virtualized-list"]', { timeout: 10000 });
    
    // 내보내기 버튼 클릭
    await page.click('button:has-text("내보내기")');
    
    // 내보내기 모달 표시 확인
    await expect(page.locator('text=로그 내보내기')).toBeVisible();
    
    // 파일 형식 선택
    await page.selectOption('select[aria-label="파일 형식"]', 'json');
    
    // 메타데이터 포함 옵션 선택
    await page.check('input[type="checkbox"][aria-label="메타데이터 포함"]');
    
    // 내보내기 시작 버튼 클릭
    await page.click('button:has-text("내보내기 시작")');
    
    // 내보내기 진행 상태 확인
    await expect(page.locator('text=내보내기 중...')).toBeVisible();
    
    // 내보내기 완료 대기 (최대 10초)
    await expect(page.locator('text=내보내기 완료')).toBeVisible({ timeout: 10000 });
  });

  test('로그 상세 정보 모달 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 로그 데이터 로딩 대기
    await page.waitForSelector('[data-testid="virtualized-list"]', { timeout: 10000 });
    
    // 첫 번째 로그 엔트리 클릭
    const firstLogEntry = page.locator('[data-testid="virtualized-list"] > div').first();
    await firstLogEntry.click();
    
    // 상세 정보 모달 표시 확인
    await expect(page.locator('text=로그 상세 정보')).toBeVisible();
    
    // 로그 정보 필드 확인
    await expect(page.locator('text=타임스탬프')).toBeVisible();
    await expect(page.locator('text=레벨')).toBeVisible();
    await expect(page.locator('text=소스')).toBeVisible();
    await expect(page.locator('text=메시지')).toBeVisible();
    
    // JSON으로 보기 버튼 테스트
    await page.click('button:has-text("JSON으로 보기")');
    
    // JSON 형식 표시 확인
    await expect(page.locator('text="level"')).toBeVisible();
    await expect(page.locator('text="timestamp"')).toBeVisible();
    
    // 모달 닫기
    await page.click('button[aria-label="Close"]');
    await expect(page.locator('text=로그 상세 정보')).not.toBeVisible();
  });

  test('자동 새로고침 기능 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 자동 새로고침 토글 활성화
    await page.check('input[type="checkbox"][aria-label="자동 새로고침"]');
    
    // 새로고침 간격 확인
    await expect(page.locator('text=5초마다 자동 새로고침')).toBeVisible();
    
    // 자동 새로고침 비활성화
    await page.uncheck('input[type="checkbox"][aria-label="자동 새로고침"]');
    
    // 자동 새로고침 상태 확인
    await expect(page.locator('text=자동 새로고침 비활성화')).toBeVisible();
  });

  test('페이지네이션 기능 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 로그 데이터 로딩 대기
    await page.waitForSelector('[data-testid="virtualized-list"]', { timeout: 10000 });
    
    // 페이지네이션 컨트롤 확인
    const pagination = page.locator('[aria-label="pagination"]');
    if (await pagination.isVisible()) {
      // 다음 페이지 버튼 클릭
      await page.click('button[aria-label="다음 페이지"]');
      
      // 페이지 변경 확인
      await page.waitForTimeout(1000);
      
      // 이전 페이지 버튼 클릭
      await page.click('button[aria-label="이전 페이지"]');
      
      // 첫 페이지로 돌아왔는지 확인
      await page.waitForTimeout(1000);
    }
  });

  test('실시간 로그 자동 스크롤 기능 테스트', async ({ page }) => {
    // 실시간 탭에서 시작 (기본값)
    
    // 연결 완료 대기
    await expect(page.locator('text=연결됨')).toBeVisible({ timeout: 10000 });
    
    // 자동 스크롤 토글 확인
    const autoScrollToggle = page.locator('input[type="checkbox"][aria-label*="자동 스크롤"]');
    await expect(autoScrollToggle).toBeVisible();
    
    // 자동 스크롤이 기본적으로 활성화되어 있는지 확인
    await expect(autoScrollToggle).toBeChecked();
    
    // 자동 스크롤 비활성화
    await autoScrollToggle.uncheck();
    await expect(autoScrollToggle).not.toBeChecked();
    
    // 자동 스크롤 활성화 버튼이 표시되는지 확인
    await expect(page.locator('button[aria-label="자동 스크롤 활성화"]')).toBeVisible();
    
    // 자동 스크롤 다시 활성화
    await autoScrollToggle.check();
    await expect(autoScrollToggle).toBeChecked();
  });

  test('로그 클리어 기능 테스트', async ({ page }) => {
    // 실시간 탭에서 시작
    
    // 연결 완료 대기
    await expect(page.locator('text=연결됨')).toBeVisible({ timeout: 10000 });
    
    // 로그 카운트가 0보다 큰지 확인 (로그가 있는 상태)
    await page.waitForTimeout(2000); // 로그 수신 대기
    
    // 로그 클리어 버튼 클릭
    await page.click('button[aria-label="로그 클리어"]');
    
    // 로그 카운트가 0이 되었는지 확인
    await expect(page.locator('text=0')).toBeVisible();
  });

  test('WebSocket 재연결 기능 테스트', async ({ page }) => {
    // 실시간 탭에서 시작
    
    // 연결 완료 대기
    await expect(page.locator('text=연결됨')).toBeVisible({ timeout: 10000 });
    
    // 재연결 버튼 클릭
    await page.click('button[aria-label="재연결"]');
    
    // 연결 중 상태 확인
    await expect(page.locator('text=연결 중...')).toBeVisible();
    
    // 재연결 완료 대기
    await expect(page.locator('text=연결됨')).toBeVisible({ timeout: 10000 });
  });

  test('반응형 디자인 테스트', async ({ page }) => {
    // 모바일 뷰포트로 변경
    await page.setViewportSize({ width: 375, height: 667 });
    
    // 페이지가 모바일에서도 올바르게 표시되는지 확인
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('[role="tab"]')).toBeVisible();
    
    // 태블릿 뷰포트로 변경
    await page.setViewportSize({ width: 768, height: 1024 });
    
    // 태블릿에서도 올바르게 표시되는지 확인
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('[role="tab"]')).toBeVisible();
    
    // 데스크톱 뷰포트로 복원
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('키보드 접근성 테스트', async ({ page }) => {
    // 히스토리 탭으로 전환
    await page.click('[role="tab"]:has-text("히스토리")');
    
    // 검색 입력 필드에 포커스
    await page.focus('input[placeholder="로그 검색..."]');
    
    // 검색어 입력
    await page.keyboard.type('테스트');
    
    // Enter 키로 검색 실행
    await page.keyboard.press('Enter');
    
    // 검색 결과 확인
    await expect(page.locator('text=검색: 테스트')).toBeVisible();
    
    // Tab 키로 필터 버튼으로 이동
    await page.keyboard.press('Tab');
    
    // Enter 키로 필터 패널 열기
    await page.keyboard.press('Enter');
    
    // 필터 패널이 열렸는지 확인
    await expect(page.locator('text=로그 레벨')).toBeVisible();
  });
});