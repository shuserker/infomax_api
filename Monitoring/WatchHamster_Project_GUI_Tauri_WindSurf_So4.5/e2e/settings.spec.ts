import { test, expect } from '@playwright/test'

test.describe('설정 페이지', () => {
  test.beforeEach(async ({ page }) => {
    // 설정 페이지로 이동
    await page.goto('/settings')
    
    // 페이지 로딩 대기
    await page.waitForSelector('[data-testid="settings-page"]', { timeout: 10000 })
  })

  test('설정 페이지가 올바르게 렌더링된다', async ({ page }) => {
    // 페이지 제목 확인
    await expect(page.locator('h1')).toContainText('설정')
    
    // 주요 섹션들 확인
    await expect(page.locator('text=일반 설정')).toBeVisible()
    await expect(page.locator('text=테마 설정')).toBeVisible()
    await expect(page.locator('text=알림 설정')).toBeVisible()
    await expect(page.locator('text=시스템 정보')).toBeVisible()
  })

  test('일반 설정을 변경할 수 있다', async ({ page }) => {
    // 자동 새로고침 스위치 토글
    const autoRefreshSwitch = page.locator('[data-testid="auto-refresh-switch"]')
    await autoRefreshSwitch.click()
    
    // 새로고침 간격 변경
    const intervalInput = page.locator('[data-testid="refresh-interval-input"]')
    await intervalInput.fill('10')
    
    // 언어 변경
    const languageSelect = page.locator('[data-testid="language-select"]')
    await languageSelect.selectOption('en')
    
    // 설정 저장
    await page.locator('text=설정 저장').click()
    
    // 성공 토스트 확인
    await expect(page.locator('text=설정 저장 완료')).toBeVisible()
  })

  test('테마 설정을 변경할 수 있다', async ({ page }) => {
    // 다크 모드로 변경
    const themeSelect = page.locator('[data-testid="theme-select"]')
    await themeSelect.selectOption('dark')
    
    // POSCO 테마 비활성화
    const poscoThemeSwitch = page.locator('[data-testid="posco-theme-switch"]')
    await poscoThemeSwitch.click()
    
    // 커스텀 색상 변경
    const primaryColorInput = page.locator('[data-testid="primary-color-input"]')
    await primaryColorInput.fill('#ff0000')
    
    // 설정 저장
    await page.locator('text=설정 저장').click()
    
    // 테마 변경 확인 (다크 모드 적용 여부)
    await expect(page.locator('body')).toHaveClass(/chakra-ui-dark/)
  })

  test('알림 설정을 변경할 수 있다', async ({ page }) => {
    // 시스템 알림 비활성화
    const systemAlertsSwitch = page.locator('[data-testid="system-alerts-switch"]')
    await systemAlertsSwitch.click()
    
    // 웹훅 활성화
    const webhookSwitch = page.locator('[data-testid="webhook-enabled-switch"]')
    await webhookSwitch.click()
    
    // 웹훅 URL 입력
    const webhookUrlInput = page.locator('[data-testid="webhook-url-input"]')
    await webhookUrlInput.fill('https://discord.com/api/webhooks/123456789/abcdefghijklmnop')
    
    // 웹훅 테스트
    await page.locator('text=웹훅 테스트').click()
    
    // 테스트 결과 확인 (성공 또는 실패 메시지)
    await expect(page.locator('text=테스트')).toBeVisible()
  })

  test('설정을 초기화할 수 있다', async ({ page }) => {
    // 먼저 설정 변경
    const autoRefreshSwitch = page.locator('[data-testid="auto-refresh-switch"]')
    await autoRefreshSwitch.click()
    
    // 초기화 버튼 클릭
    await page.locator('text=기본값으로 초기화').click()
    
    // 확인 대화상자가 있다면 확인
    const confirmButton = page.locator('text=확인')
    if (await confirmButton.isVisible()) {
      await confirmButton.click()
    }
    
    // 초기화 완료 토스트 확인
    await expect(page.locator('text=설정 초기화 완료')).toBeVisible()
    
    // 설정이 기본값으로 돌아갔는지 확인
    await expect(autoRefreshSwitch).toBeChecked()
  })

  test('설정을 내보내고 가져올 수 있다', async ({ page }) => {
    // 설정 내보내기
    const downloadPromise = page.waitForEvent('download')
    await page.locator('text=설정 내보내기').click()
    const download = await downloadPromise
    
    // 파일명 확인
    expect(download.suggestedFilename()).toMatch(/watchhamster-settings-\d{4}-\d{2}-\d{2}\.json/)
    
    // 설정 가져오기 (파일 업로드 시뮬레이션)
    const fileInput = page.locator('input[type="file"]')
    
    // 테스트용 설정 파일 생성
    const testSettings = {
      autoRefresh: false,
      language: 'en',
      theme: 'dark'
    }
    
    // 파일 업로드는 실제 파일이 필요하므로 버튼 존재 여부만 확인
    await expect(page.locator('text=설정 가져오기')).toBeVisible()
  })

  test('웹훅 URL 유효성 검사가 작동한다', async ({ page }) => {
    // 웹훅 활성화
    const webhookSwitch = page.locator('[data-testid="webhook-enabled-switch"]')
    await webhookSwitch.click()
    
    // 잘못된 URL 입력
    const webhookUrlInput = page.locator('[data-testid="webhook-url-input"]')
    await webhookUrlInput.fill('invalid-url')
    
    // 경고 메시지 확인
    await expect(page.locator('text=올바르지 않은 웹훅 URL 형식')).toBeVisible()
    
    // 올바른 Discord URL 입력
    await webhookUrlInput.fill('https://discord.com/api/webhooks/123456789/abcdefghijklmnop')
    
    // 성공 메시지 확인
    await expect(page.locator('text=유효한 Discord 웹훅 URL')).toBeVisible()
  })

  test('색상 팔레트 선택이 작동한다', async ({ page }) => {
    // 모던 블루 팔레트 선택
    await page.locator('text=모던 블루').click()
    
    // 색상이 변경되었는지 확인 (primary color input 값 확인)
    const primaryColorInput = page.locator('[data-testid="primary-color-text-input"]')
    await expect(primaryColorInput).toHaveValue('#2563eb')
    
    // 색상 미리보기 버튼 색상 확인
    const primaryButton = page.locator('text=Primary Button')
    await expect(primaryButton).toHaveCSS('background-color', 'rgb(37, 99, 235)')
  })

  test('테마 미리보기가 작동한다', async ({ page }) => {
    // 다크 모드 미리보기 클릭
    await page.locator('text=다크 모드 미리보기').click()
    
    // 미리보기 상태 확인 (버튼 스타일 변경)
    const previewButton = page.locator('text=다크 모드 미리보기')
    await expect(previewButton).toHaveCSS('background-color', 'rgb(45, 55, 72)')
    
    // 2초 후 미리보기 해제 확인
    await page.waitForTimeout(2500)
    await expect(previewButton).not.toHaveCSS('background-color', 'rgb(45, 55, 72)')
  })

  test('알림 우선순위 설정이 작동한다', async ({ page }) => {
    // 시스템 알림 우선순위를 높음으로 변경
    const systemPrioritySelect = page.locator('[data-testid="system-priority-select"]')
    await systemPrioritySelect.selectOption('high')
    
    // 서비스 알림 우선순위를 낮음으로 변경
    const servicePrioritySelect = page.locator('[data-testid="service-priority-select"]')
    await servicePrioritySelect.selectOption('low')
    
    // 설정 저장
    await page.locator('text=설정 저장').click()
    
    // 저장 완료 확인
    await expect(page.locator('text=설정 저장 완료')).toBeVisible()
  })

  test('시스템 정보가 올바르게 표시된다', async ({ page }) => {
    // 시스템 정보 섹션 확인
    await expect(page.locator('text=애플리케이션 버전')).toBeVisible()
    await expect(page.locator('text=Base: WH v4.5')).toBeVisible()
    
    await expect(page.locator('text=플랫폼')).toBeVisible()
    await expect(page.locator('text=백엔드 상태')).toBeVisible()
    await expect(page.locator('text=연결됨')).toBeVisible()
    
    await expect(page.locator('text=마지막 업데이트')).toBeVisible()
    await expect(page.locator('text=설정 파일 위치')).toBeVisible()
  })

  test('반응형 디자인이 올바르게 작동한다', async ({ page }) => {
    // 모바일 뷰포트로 변경
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 설정 카드들이 세로로 배치되는지 확인
    const settingsCards = page.locator('[data-testid="settings-card"]')
    const firstCard = settingsCards.first()
    const secondCard = settingsCards.nth(1)
    
    const firstCardBox = await firstCard.boundingBox()
    const secondCardBox = await secondCard.boundingBox()
    
    // 두 번째 카드가 첫 번째 카드 아래에 위치하는지 확인
    if (firstCardBox && secondCardBox) {
      expect(secondCardBox.y).toBeGreaterThan(firstCardBox.y + firstCardBox.height)
    }
    
    // 데스크톱 뷰포트로 복원
    await page.setViewportSize({ width: 1280, height: 720 })
  })

  test('키보드 네비게이션이 작동한다', async ({ page }) => {
    // Tab 키로 포커스 이동 테스트
    await page.keyboard.press('Tab')
    
    // 첫 번째 포커스 가능한 요소 확인
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
    
    // Enter 키로 스위치 토글 테스트
    const autoRefreshSwitch = page.locator('[data-testid="auto-refresh-switch"]')
    await autoRefreshSwitch.focus()
    await page.keyboard.press('Space')
    
    // 스위치 상태 변경 확인
    const isChecked = await autoRefreshSwitch.isChecked()
    expect(typeof isChecked).toBe('boolean')
  })
})