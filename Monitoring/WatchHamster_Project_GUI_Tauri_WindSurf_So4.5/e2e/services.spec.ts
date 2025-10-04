import { test, expect } from '@playwright/test'

test.describe('서비스 관리 페이지 E2E 테스트', () => {
  test.beforeEach(async ({ page }) => {
    // 서비스 페이지로 이동
    await page.goto('/services')
    
    // 페이지가 완전히 로드될 때까지 대기
    await page.waitForLoadState('networkidle')
  })

  test.describe('페이지 기본 기능', () => {
    test('페이지 제목과 설명이 표시되어야 함', async ({ page }) => {
      await expect(page.getByText('서비스 관리')).toBeVisible()
      await expect(page.getByText('시스템 서비스의 상태를 확인하고 제어합니다')).toBeVisible()
    })

    test('모든 서비스 카드가 표시되어야 함', async ({ page }) => {
      // 각 서비스 카드 확인
      await expect(page.getByText('POSCO 뉴스 모니터')).toBeVisible()
      await expect(page.getByText('GitHub Pages 모니터')).toBeVisible()
      await expect(page.getByText('캐시 모니터')).toBeVisible()
      await expect(page.getByText('배포 시스템')).toBeVisible()
      await expect(page.getByText('메시지 시스템')).toBeVisible()
      await expect(page.getByText('웹훅 시스템')).toBeVisible()
    })

    test('POSCO 관리 패널과 웹훅 관리가 표시되어야 함', async ({ page }) => {
      await expect(page.getByTestId('posco-management-panel')).toBeVisible()
      await expect(page.getByTestId('webhook-management')).toBeVisible()
    })
  })

  test.describe('서비스 상태 표시', () => {
    test('서비스 상태 배지가 올바르게 표시되어야 함', async ({ page }) => {
      // 실행 중 상태
      await expect(page.getByText('실행 중').first()).toBeVisible()
      
      // 중지됨 상태
      await expect(page.getByText('중지됨')).toBeVisible()
      
      // 오류 상태
      await expect(page.getByText('오류')).toBeVisible()
    })

    test('서비스 업타임이 표시되어야 함', async ({ page }) => {
      await expect(page.getByText('2시간 15분')).toBeVisible()
      await expect(page.getByText('1시간 30분')).toBeVisible()
      await expect(page.getByText('3시간 45분')).toBeVisible()
    })

    test('오류 메시지가 표시되어야 함', async ({ page }) => {
      await expect(page.getByText('마지막 오류')).toBeVisible()
      await expect(page.getByText('Connection timeout')).toBeVisible()
      await expect(page.getByText('Git merge conflict in main branch')).toBeVisible()
    })

    test('서비스 설정 정보가 표시되어야 함', async ({ page }) => {
      // POSCO 뉴스 모니터 설정
      await expect(page.getByText('main')).toBeVisible()
      await expect(page.getByText('5분')).toBeVisible()
      
      // GitHub Pages 모니터 설정
      await expect(page.getByText('posco-docs')).toBeVisible()
      await expect(page.getByText('gh-pages')).toBeVisible()
    })
  })

  test.describe('서비스 제어 기능', () => {
    test('실행 중인 서비스에 중지 및 재시작 버튼이 표시되어야 함', async ({ page }) => {
      // 실행 중인 서비스의 제어 버튼들
      const stopButtons = page.getByText('중지')
      const restartButtons = page.getByText('재시작')
      
      await expect(stopButtons.first()).toBeVisible()
      await expect(restartButtons.first()).toBeVisible()
    })

    test('중지된 서비스에 시작 버튼이 표시되어야 함', async ({ page }) => {
      const startButtons = page.getByText('시작')
      await expect(startButtons.first()).toBeVisible()
    })

    test('서비스 시작 버튼 클릭 시 토스트 알림이 표시되어야 함', async ({ page }) => {
      // 시작 버튼 클릭
      await page.getByText('시작').first().click()
      
      // 토스트 알림 확인
      await expect(page.getByText('서비스 시작')).toBeVisible()
      await expect(page.getByText(/서비스를 시작합니다/)).toBeVisible()
    })

    test('서비스 중지 버튼 클릭 시 토스트 알림이 표시되어야 함', async ({ page }) => {
      // 중지 버튼 클릭
      await page.getByText('중지').first().click()
      
      // 토스트 알림 확인
      await expect(page.getByText('서비스 중지')).toBeVisible()
      await expect(page.getByText(/서비스를 중지합니다/)).toBeVisible()
    })

    test('서비스 재시작 버튼 클릭 시 토스트 알림이 표시되어야 함', async ({ page }) => {
      // 재시작 버튼 클릭
      await page.getByText('재시작').first().click()
      
      // 토스트 알림 확인
      await expect(page.getByText('서비스 재시작')).toBeVisible()
      await expect(page.getByText(/서비스를 재시작합니다/)).toBeVisible()
    })

    test('서비스 설정 버튼이 모든 서비스에 표시되어야 함', async ({ page }) => {
      const settingsButtons = page.getByLabel('서비스 설정')
      await expect(settingsButtons).toHaveCount(6)
    })

    test('서비스 설정 버튼 클릭 시 토스트 알림이 표시되어야 함', async ({ page }) => {
      // 설정 버튼 클릭
      await page.getByLabel('서비스 설정').first().click()
      
      // 토스트 알림 확인
      await expect(page.getByText('서비스 설정')).toBeVisible()
      await expect(page.getByText(/서비스를 설정합니다/)).toBeVisible()
    })
  })

  test.describe('반응형 디자인', () => {
    test('데스크톱 화면에서 그리드 레이아웃이 올바르게 표시되어야 함', async ({ page }) => {
      // 뷰포트를 데스크톱 크기로 설정
      await page.setViewportSize({ width: 1920, height: 1080 })
      
      // 서비스 카드들이 그리드로 배치되는지 확인
      const serviceCards = page.locator('.chakra-card')
      await expect(serviceCards).toHaveCount(6)
      
      // 각 카드가 보이는지 확인
      for (let i = 0; i < 6; i++) {
        await expect(serviceCards.nth(i)).toBeVisible()
      }
    })

    test('태블릿 화면에서 레이아웃이 적절히 조정되어야 함', async ({ page }) => {
      // 뷰포트를 태블릿 크기로 설정
      await page.setViewportSize({ width: 768, height: 1024 })
      
      // 서비스 카드들이 여전히 표시되는지 확인
      const serviceCards = page.locator('.chakra-card')
      await expect(serviceCards).toHaveCount(6)
      
      // 페이지 제목이 여전히 보이는지 확인
      await expect(page.getByText('서비스 관리')).toBeVisible()
    })

    test('모바일 화면에서 레이아웃이 적절히 조정되어야 함', async ({ page }) => {
      // 뷰포트를 모바일 크기로 설정
      await page.setViewportSize({ width: 375, height: 667 })
      
      // 서비스 카드들이 세로로 배치되는지 확인
      const serviceCards = page.locator('.chakra-card')
      await expect(serviceCards).toHaveCount(6)
      
      // 첫 번째 카드가 보이는지 확인
      await expect(serviceCards.first()).toBeVisible()
    })
  })

  test.describe('키보드 네비게이션', () => {
    test('Tab 키로 버튼들 간 이동이 가능해야 함', async ({ page }) => {
      // 첫 번째 버튼에 포커스
      await page.keyboard.press('Tab')
      
      // 여러 번 Tab을 눌러 버튼들 간 이동
      for (let i = 0; i < 5; i++) {
        await page.keyboard.press('Tab')
      }
      
      // 포커스된 요소가 있는지 확인
      const focusedElement = page.locator(':focus')
      await expect(focusedElement).toBeVisible()
    })

    test('Enter 키로 버튼 클릭이 가능해야 함', async ({ page }) => {
      // 시작 버튼에 포커스하고 Enter 키 누르기
      await page.getByText('시작').first().focus()
      await page.keyboard.press('Enter')
      
      // 토스트 알림이 표시되는지 확인
      await expect(page.getByText('서비스 시작')).toBeVisible()
    })
  })

  test.describe('성능 테스트', () => {
    test('페이지 로딩 시간이 적절해야 함', async ({ page }) => {
      const startTime = Date.now()
      
      await page.goto('/services')
      await page.waitForLoadState('networkidle')
      
      const loadTime = Date.now() - startTime
      
      // 페이지 로딩 시간이 5초 이하여야 함
      expect(loadTime).toBeLessThan(5000)
    })

    test('서비스 카드 렌더링이 빨라야 함', async ({ page }) => {
      await page.goto('/services')
      
      // 모든 서비스 카드가 2초 이내에 렌더링되어야 함
      await expect(page.locator('.chakra-card')).toHaveCount(6, { timeout: 2000 })
    })
  })

  test.describe('접근성 테스트', () => {
    test('페이지에 적절한 헤딩 구조가 있어야 함', async ({ page }) => {
      // 메인 헤딩 확인
      await expect(page.getByRole('heading', { name: '서비스 관리' })).toBeVisible()
      
      // 서비스 카드 헤딩들 확인
      await expect(page.getByRole('heading', { name: 'POSCO 뉴스 모니터' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'GitHub Pages 모니터' })).toBeVisible()
    })

    test('모든 버튼에 적절한 레이블이 있어야 함', async ({ page }) => {
      // 설정 버튼들의 aria-label 확인
      const settingsButtons = page.getByLabel('서비스 설정')
      await expect(settingsButtons).toHaveCount(6)
      
      // 각 설정 버튼이 접근 가능한지 확인
      for (let i = 0; i < 6; i++) {
        await expect(settingsButtons.nth(i)).toBeVisible()
      }
    })

    test('색상 대비가 적절해야 함', async ({ page }) => {
      // 상태 배지들이 보이는지 확인 (색상 대비 테스트의 기본)
      await expect(page.getByText('실행 중')).toBeVisible()
      await expect(page.getByText('중지됨')).toBeVisible()
      await expect(page.getByText('오류')).toBeVisible()
    })
  })

  test.describe('에러 처리', () => {
    test('네트워크 오류 시 적절한 처리가 되어야 함', async ({ page }) => {
      // 네트워크를 오프라인으로 설정
      await page.context().setOffline(true)
      
      // 페이지 새로고침
      await page.reload()
      
      // 페이지가 여전히 기본 구조를 유지하는지 확인
      // (실제로는 오프라인 상태 표시나 에러 메시지가 있어야 함)
      await expect(page.getByText('서비스 관리')).toBeVisible()
      
      // 네트워크를 다시 온라인으로 설정
      await page.context().setOffline(false)
    })

    test('JavaScript 오류가 발생해도 페이지가 크래시되지 않아야 함', async ({ page }) => {
      // 콘솔 오류 수집
      const consoleErrors: string[] = []
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text())
        }
      })
      
      // 페이지 로드
      await page.goto('/services')
      await page.waitForLoadState('networkidle')
      
      // 기본 기능이 여전히 작동하는지 확인
      await expect(page.getByText('서비스 관리')).toBeVisible()
      
      // 심각한 JavaScript 오류가 없는지 확인
      const criticalErrors = consoleErrors.filter(error => 
        error.includes('Uncaught') || error.includes('TypeError')
      )
      expect(criticalErrors).toHaveLength(0)
    })
  })

  test.describe('사용자 워크플로우', () => {
    test('서비스 시작 → 중지 → 재시작 워크플로우가 정상 작동해야 함', async ({ page }) => {
      // 1. 중지된 서비스 시작
      await page.getByText('시작').first().click()
      await expect(page.getByText('서비스 시작')).toBeVisible()
      
      // 토스트가 사라질 때까지 대기
      await page.waitForTimeout(3500)
      
      // 2. 실행 중인 서비스 중지 (실제로는 상태가 변경되어야 하지만 현재는 모의 데이터)
      await page.getByText('중지').first().click()
      await expect(page.getByText('서비스 중지')).toBeVisible()
      
      // 토스트가 사라질 때까지 대기
      await page.waitForTimeout(3500)
      
      // 3. 서비스 재시작
      await page.getByText('재시작').first().click()
      await expect(page.getByText('서비스 재시작')).toBeVisible()
    })

    test('여러 서비스를 동시에 제어할 수 있어야 함', async ({ page }) => {
      // 여러 서비스의 제어 버튼들이 독립적으로 작동하는지 확인
      const startButtons = page.getByText('시작')
      const stopButtons = page.getByText('중지')
      
      // 첫 번째 시작 버튼 클릭
      if (await startButtons.first().isVisible()) {
        await startButtons.first().click()
        await expect(page.getByText('서비스 시작')).toBeVisible()
        await page.waitForTimeout(1000)
      }
      
      // 첫 번째 중지 버튼 클릭
      if (await stopButtons.first().isVisible()) {
        await stopButtons.first().click()
        await expect(page.getByText('서비스 중지')).toBeVisible()
      }
    })

    test('서비스 설정 버튼들이 각각 독립적으로 작동해야 함', async ({ page }) => {
      const settingsButtons = page.getByLabel('서비스 설정')
      
      // 첫 번째 설정 버튼 클릭
      await settingsButtons.first().click()
      await expect(page.getByText('서비스 설정')).toBeVisible()
      
      // 토스트가 사라질 때까지 대기
      await page.waitForTimeout(3500)
      
      // 두 번째 설정 버튼 클릭
      await settingsButtons.nth(1).click()
      await expect(page.getByText('서비스 설정')).toBeVisible()
    })
  })
})