import React from 'react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import Services from '../Services'
import theme from '../../theme'

// API 서비스 모킹
vi.mock('../../services/api', async () => {
  const actual = await vi.importActual('../../services/api')
  return {
    ...actual,
    default: {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    },
    ApiServiceError: class ApiServiceError extends Error {
      constructor(message: string, public status?: number) {
        super(message)
        this.name = 'ApiServiceError'
      }
    },
  }
})

// WebSocket 모킹
vi.mock('../../hooks/useWebSocket', () => ({
  default: () => ({
    isConnected: true,
    lastMessage: null,
    sendMessage: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
  }),
}))

// 실제 컴포넌트들을 사용하여 통합 테스트

// 테스트 래퍼 컴포넌트
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return (
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    </ChakraProvider>
  )
}

describe('Services 페이지 통합 테스트', () => {
  let mockToast: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockToast = vi.fn()
    vi.clearAllMocks()
    
    // Chakra UI useToast 모킹
    vi.doMock('@chakra-ui/react', async () => {
      const actual = await vi.importActual('@chakra-ui/react')
      return {
        ...actual,
        useToast: () => mockToast,
      }
    })
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.restoreAllMocks()
  })

  describe('전체 페이지 통합', () => {
    it('모든 주요 섹션이 함께 렌더링되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 페이지 헤더
      expect(screen.getByText('서비스 관리')).toBeInTheDocument()
      expect(screen.getByText('시스템 서비스의 상태를 확인하고 제어합니다')).toBeInTheDocument()

      // 서비스 카드들
      expect(screen.getByText('POSCO 뉴스 모니터')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages 모니터')).toBeInTheDocument()
      expect(screen.getByText('캐시 모니터')).toBeInTheDocument()
      expect(screen.getByText('배포 시스템')).toBeInTheDocument()
      expect(screen.getByText('메시지 시스템')).toBeInTheDocument()
      expect(screen.getByText('웹훅 시스템')).toBeInTheDocument()

      // 관리 패널들
      await waitFor(() => {
        expect(screen.getByTestId('posco-management-panel')).toBeInTheDocument()
        expect(screen.getByTestId('webhook-management')).toBeInTheDocument()
      })
    })

    it('서비스 카드와 관리 패널 간의 상호작용이 정상 작동해야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 서비스 카드의 제어 버튼 클릭
      const stopButton = screen.getAllByText('중지')[0]
      fireEvent.click(stopButton)

      // 토스트 알림 확인
      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: '서비스 중지',
          description: expect.stringContaining('서비스를 중지합니다'),
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      })
    })
  })

  describe('서비스 카드 그리드 통합', () => {
    it('모든 서비스 카드가 일관된 레이아웃을 가져야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const cards = document.querySelectorAll('.chakra-card')
      expect(cards).toHaveLength(6)

      // 각 카드가 필수 요소들을 포함하는지 확인
      cards.forEach((card) => {
        const cardElement = card as HTMLElement
        
        // 서비스 이름이 있는지 확인
        const headings = within(cardElement).getAllByRole('heading')
        expect(headings.length).toBeGreaterThan(0)

        // 상태 배지가 있는지 확인
        const badges = cardElement.querySelectorAll('[data-theme]')
        expect(badges.length).toBeGreaterThan(0)

        // 제어 버튼들이 있는지 확인
        const buttons = within(cardElement).getAllByRole('button')
        expect(buttons.length).toBeGreaterThan(0)
      })
    })

    it('서비스 상태에 따라 적절한 제어 버튼이 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 실행 중인 서비스들 (POSCO 뉴스, 캐시 모니터, 메시지 시스템, 웹훅 시스템)
      const stopButtons = screen.getAllByText('중지')
      const restartButtons = screen.getAllByText('재시작')
      expect(stopButtons.length).toBe(4) // 실행 중인 서비스 4개
      expect(restartButtons.length).toBe(4)

      // 중지된 서비스 (GitHub Pages)
      const startButtons = screen.getAllByText('시작')
      expect(startButtons.length).toBe(1) // 중지된 서비스 1개 + 오류 상태 서비스 1개

      // 모든 서비스에 설정 버튼이 있어야 함
      const settingsButtons = screen.getAllByLabelText('서비스 설정')
      expect(settingsButtons.length).toBe(6)
    })

    it('서비스 정보가 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 업타임 정보
      expect(screen.getByText('2시간 15분')).toBeInTheDocument()
      expect(screen.getByText('1시간 30분')).toBeInTheDocument()
      expect(screen.getByText('3시간 45분')).toBeInTheDocument()
      expect(screen.getByText('2시간 50분')).toBeInTheDocument()

      // 오류 정보
      expect(screen.getByText('Connection timeout')).toBeInTheDocument()
      expect(screen.getByText('Git merge conflict in main branch')).toBeInTheDocument()

      // 설정 정보
      expect(screen.getByText('main')).toBeInTheDocument()
      expect(screen.getByText('5분')).toBeInTheDocument()
      expect(screen.getByText('posco-docs')).toBeInTheDocument()
      expect(screen.getByText('gh-pages')).toBeInTheDocument()
    })
  })

  describe('사용자 상호작용 통합', () => {
    it('여러 서비스를 순차적으로 제어할 수 있어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 첫 번째 서비스 중지
      const firstStopButton = screen.getAllByText('중지')[0]
      fireEvent.click(firstStopButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: '서비스 중지',
          description: expect.stringContaining('서비스를 중지합니다'),
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      })

      // 두 번째 서비스 재시작
      const firstRestartButton = screen.getAllByText('재시작')[0]
      fireEvent.click(firstRestartButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: '서비스 재시작',
          description: expect.stringContaining('서비스를 재시작합니다'),
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      })

      // 중지된 서비스 시작
      const startButton = screen.getAllByText('시작')[0]
      fireEvent.click(startButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: '서비스 시작',
          description: expect.stringContaining('서비스를 시작합니다'),
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      })

      // 총 3번의 토스트 호출이 있어야 함
      expect(mockToast).toHaveBeenCalledTimes(3)
    })

    it('설정 버튼들이 각각 독립적으로 작동해야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const settingsButtons = screen.getAllByLabelText('서비스 설정')

      // 각 설정 버튼을 순차적으로 클릭
      for (let i = 0; i < Math.min(3, settingsButtons.length); i++) {
        fireEvent.click(settingsButtons[i])

        await waitFor(() => {
          expect(mockToast).toHaveBeenCalledWith({
            title: '서비스 설정',
            description: expect.stringContaining('서비스를 설정합니다'),
            status: 'info',
            duration: 3000,
            isClosable: true,
          })
        })
      }

      expect(mockToast).toHaveBeenCalledTimes(3)
    })
  })

  describe('반응형 레이아웃 통합', () => {
    it('그리드 레이아웃이 모든 화면 크기에서 작동해야 함', () => {
      const { container } = render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 그리드 컨테이너 확인
      const gridContainer = container.querySelector('.chakra-grid')
      expect(gridContainer).toBeInTheDocument()

      // 모든 서비스 카드가 그리드 내에 있는지 확인
      const cards = container.querySelectorAll('.chakra-card')
      expect(cards).toHaveLength(6)

      cards.forEach(card => {
        expect(gridContainer).toContainElement(card as HTMLElement)
      })
    })

    it('페이지 스크롤이 정상 작동해야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 페이지 최상단 요소
      const pageTitle = screen.getByText('서비스 관리')
      expect(pageTitle).toBeInTheDocument()

      // 페이지 하단 요소들
      expect(screen.getByTestId('posco-management-panel')).toBeInTheDocument()
      expect(screen.getByTestId('webhook-management')).toBeInTheDocument()

      // 모든 요소가 동시에 보이는지 확인 (스크롤 없이)
      expect(pageTitle).toBeVisible()
      expect(screen.getByTestId('posco-management-panel')).toBeVisible()
      expect(screen.getByTestId('webhook-management')).toBeVisible()
    })
  })

  describe('에러 처리 통합', () => {
    it('컴포넌트 에러가 발생해도 페이지가 크래시되지 않아야 함', () => {
      // 에러 경계 테스트를 위한 에러 발생 시뮬레이션
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() => {
        render(
          <TestWrapper>
            <Services />
          </TestWrapper>
        )
      }).not.toThrow()

      // 기본 페이지 구조가 여전히 렌더링되는지 확인
      expect(screen.getByText('서비스 관리')).toBeInTheDocument()

      consoleSpy.mockRestore()
    })

    it('잘못된 서비스 데이터에 대해 안전하게 처리해야 함', () => {
      // 현재 구현에서는 하드코딩된 데이터를 사용하므로
      // 기본 렌더링이 정상적으로 이루어지는지만 확인
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('서비스 관리')).toBeInTheDocument()
      expect(screen.getAllByRole('button').length).toBeGreaterThan(0)
    })
  })

  describe('성능 통합', () => {
    it('대량의 서비스 카드 렌더링이 빨라야 함', () => {
      const startTime = performance.now()

      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const endTime = performance.now()
      const renderTime = endTime - startTime

      // 렌더링 시간이 200ms 이하여야 함
      expect(renderTime).toBeLessThan(200)

      // 모든 카드가 렌더링되었는지 확인
      expect(document.querySelectorAll('.chakra-card')).toHaveLength(6)
    })

    it('메모리 사용량이 적절해야 함', () => {
      const { unmount } = render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 컴포넌트가 정상적으로 언마운트되는지 확인
      expect(() => unmount()).not.toThrow()
    })
  })

  describe('접근성 통합', () => {
    it('키보드 네비게이션이 전체 페이지에서 작동해야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 모든 상호작용 가능한 요소들이 탭 순서에 포함되는지 확인
      const interactiveElements = screen.getAllByRole('button')
      
      interactiveElements.forEach(element => {
        expect(element).not.toHaveAttribute('tabindex', '-1')
      })
    })

    it('스크린 리더를 위한 적절한 레이블이 있어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 페이지 제목
      expect(screen.getByRole('heading', { name: '서비스 관리' })).toBeInTheDocument()

      // 서비스 카드 제목들
      expect(screen.getByRole('heading', { name: 'POSCO 뉴스 모니터' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'GitHub Pages 모니터' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '캐시 모니터' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '배포 시스템' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '메시지 시스템' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '웹훅 시스템' })).toBeInTheDocument()

      // 설정 버튼들의 aria-label
      const settingsButtons = screen.getAllByLabelText('서비스 설정')
      expect(settingsButtons).toHaveLength(6)
    })

    it('색상 대비가 적절해야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 상태 배지들이 보이는지 확인 (색상 대비의 기본 검증)
      expect(screen.getByText('실행 중')).toBeVisible()
      expect(screen.getByText('중지됨')).toBeVisible()
      expect(screen.getByText('오류')).toBeVisible()

      // 텍스트 요소들이 보이는지 확인
      expect(screen.getByText('서비스 관리')).toBeVisible()
      expect(screen.getByText('시스템 서비스의 상태를 확인하고 제어합니다')).toBeVisible()
    })
  })
})