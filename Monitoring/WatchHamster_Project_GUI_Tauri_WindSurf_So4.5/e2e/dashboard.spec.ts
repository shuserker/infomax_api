import { test, expect } from '@playwright/test'

test.describe('대시보드 페이지', () => {
  test.beforeEach(async ({ page }) => {
    // 백엔드 API 모킹
    await page.route('**/api/metrics', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            cpu_percent: 45.2,
            memory_percent: 67.8,
            disk_usage: 23.1,
            network_status: 'connected',
            uptime: 86400,
            active_services: 6,
            timestamp: new Date().toISOString(),
          },
          status: 'success',
          timestamp: new Date().toISOString(),
        }),
      })
    })

    await page.route('**/api/services', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: [
            {
              id: 'posco_news',
              name: 'POSCO 뉴스 모니터',
              description: 'POSCO 뉴스 시스템 모니터링',
              status: 'running',
              uptime: 3600,
            },
            {
              id: 'github_pages',
              name: 'GitHub Pages 모니터',
              description: 'GitHub Pages 배포 상태 모니터링',
              status: 'stopped',
              uptime: 0,
            },
          ],
          status: 'success',
          timestamp: new Date().toISOString(),
        }),
      })
    })

    // WebSocket 연결 모킹
    await page.addInitScript(() => {
      class MockWebSocket {
        static CONNECTING = 0
        static OPEN = 1
        static CLOSING = 2
        static CLOSED = 3

        readyState = MockWebSocket.OPEN
        url: string

        constructor(url: string) {
          this.url = url
          setTimeout(() => {
            this.onopen?.(new Event('open'))
          }, 100)
        }

        onopen: ((event: Event) => void) | null = null
        onclose: ((event: CloseEvent) => void) | null = null
        onmessage: ((event: MessageEvent) => void) | null = null
        onerror: ((event: Event) => void) | null = null

        send() {}
        close() {}
        addEventListener() {}
        removeEventListener() {}
        dispatchEvent() { return true }
      }

      // @ts-ignore
      window.WebSocket = MockWebSocket
    })

    await page.goto('/')
  })

  test('페이지가 올바르게 로드된다', async ({ page }) => {
    await expect(page.locator('h1, h2')).toContainText('시스템 대시보드')
  })

  test('시스템 메트릭 카드들이 표시된다', async ({ page }) => {
    // CPU 메트릭 카드 확인
    await expect(page.locator('[data-testid="metric-card-cpu"]')).toBeVisible()
    
    // 메모리 메트릭 카드 확인
    await expect(page.locator('[data-testid="metric-card-memory"]')).toBeVisible()
    
    // 디스크 메트릭 카드 확인
    await expect(page.locator('[data-testid="metric-card-disk"]')).toBeVisible()
    
    // 네트워크 메트릭 카드 확인
    await expect(page.locator('[data-testid="metric-card-network"]')).toBeVisible()
  })

  test('실시간 성능 차트가 표시된다', async ({ page }) => {
    await expect(page.locator('[data-testid="realtime-chart"]')).toBeVisible()
  })

  test('서비스 상태 그리드가 표시된다', async ({ page }) => {
    await expect(page.locator('[data-testid="service-status-grid"]')).toBeVisible()
    
    // 서비스 카드들이 표시되는지 확인
    await expect(page.locator('[data-testid="service-card"]')).toHaveCount(2)
  })

  test('새로고침 버튼이 작동한다', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("새로고침")')
    await expect(refreshButton).toBeVisible()
    
    await refreshButton.click()
    
    // 토스트 알림이 표시되는지 확인
    await expect(page.locator('.chakra-toast')).toBeVisible()
  })

  test('연결 상태 배지가 표시된다', async ({ page }) => {
    // 실시간 연결 상태 배지 확인
    await expect(page.locator('[data-testid="connection-status"]')).toBeVisible()
  })

  test('최근 활동 섹션이 표시된다', async ({ page }) => {
    await expect(page.locator('h2:has-text("최근 활동")')).toBeVisible()
    
    // 활동 항목들이 표시되는지 확인
    await expect(page.locator('[data-testid="activity-item"]')).toHaveCount(4)
  })

  test('반응형 디자인이 작동한다', async ({ page }) => {
    // 데스크톱 뷰 확인
    await page.setViewportSize({ width: 1200, height: 800 })
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible()

    // 모바일 뷰 확인
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible()
  })
})

test.describe('대시보드 상호작용', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('네비게이션이 작동한다', async ({ page }) => {
    // 서비스 관리 페이지로 이동
    await page.click('a:has-text("서비스 관리")')
    await expect(page).toHaveURL('/services')

    // 로그 뷰어 페이지로 이동
    await page.click('a:has-text("로그 뷰어")')
    await expect(page).toHaveURL('/logs')

    // 설정 페이지로 이동
    await page.click('a:has-text("설정")')
    await expect(page).toHaveURL('/settings')

    // 대시보드로 돌아가기
    await page.click('a:has-text("대시보드")')
    await expect(page).toHaveURL('/')
  })

  test('다크 모드 전환이 작동한다', async ({ page }) => {
    // 다크 모드 토글 버튼 찾기
    const themeToggle = page.locator('[data-testid="theme-toggle"]')
    
    if (await themeToggle.isVisible()) {
      await themeToggle.click()
      
      // 다크 모드 클래스가 적용되었는지 확인
      await expect(page.locator('body')).toHaveClass(/chakra-ui-dark/)
    }
  })

  test('키보드 네비게이션이 작동한다', async ({ page }) => {
    // Tab 키로 네비게이션
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    
    // Enter 키로 선택
    await page.keyboard.press('Enter')
    
    // 포커스가 올바르게 이동하는지 확인
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  })
})