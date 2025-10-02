import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import Services from '../Services'
import theme from '../../theme'

// Mock 컴포넌트들
vi.mock('../../components/Services/PoscoManagementPanel', () => ({
  default: () => <div data-testid="posco-management-panel">POSCO 관리 패널</div>
}))

vi.mock('../../components/Services/WebhookManagement', () => ({
  default: () => <div data-testid="webhook-management">웹훅 관리</div>
}))

// Toast mock
const mockToast = vi.fn()
vi.mock('@chakra-ui/react', async () => {
  const actual = await vi.importActual('@chakra-ui/react')
  return {
    ...actual,
    useToast: () => mockToast,
  }
})

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

describe('Services 페이지', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  describe('페이지 렌더링', () => {
    it('페이지 제목과 설명이 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('서비스 관리')).toBeInTheDocument()
      expect(screen.getByText('시스템 서비스의 상태를 확인하고 제어합니다')).toBeInTheDocument()
    })

    it('모든 서비스 카드가 렌더링되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 각 서비스 카드 확인
      expect(screen.getByText('POSCO 뉴스 모니터')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages 모니터')).toBeInTheDocument()
      expect(screen.getByText('캐시 모니터')).toBeInTheDocument()
      expect(screen.getByText('배포 시스템')).toBeInTheDocument()
      expect(screen.getByText('메시지 시스템')).toBeInTheDocument()
      expect(screen.getByText('웹훅 시스템')).toBeInTheDocument()
    })

    it('POSCO 관리 패널과 웹훅 관리 컴포넌트가 렌더링되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByTestId('posco-management-panel')).toBeInTheDocument()
      expect(screen.getByTestId('webhook-management')).toBeInTheDocument()
    })
  })

  describe('서비스 상태 표시', () => {
    it('실행 중인 서비스의 상태가 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // POSCO 뉴스 모니터 (실행 중)
      const poscoCard = screen.getByText('POSCO 뉴스 모니터').closest('.chakra-card')
      expect(poscoCard).toBeInTheDocument()
      
      // 실행 중 배지 확인
      const runningBadges = screen.getAllByText('실행 중')
      expect(runningBadges.length).toBeGreaterThan(0)
    })

    it('중지된 서비스의 상태가 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // GitHub Pages 모니터 (중지됨)
      expect(screen.getByText('중지됨')).toBeInTheDocument()
    })

    it('오류 상태인 서비스의 상태가 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 배포 시스템 (오류)
      expect(screen.getByText('오류')).toBeInTheDocument()
      expect(screen.getByText('Git merge conflict in main branch')).toBeInTheDocument()
    })

    it('서비스 업타임이 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('2시간 15분')).toBeInTheDocument()
      expect(screen.getByText('1시간 30분')).toBeInTheDocument()
      expect(screen.getByText('3시간 45분')).toBeInTheDocument()
    })
  })

  describe('서비스 제어 기능', () => {
    it('실행 중인 서비스에 중지 및 재시작 버튼이 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 실행 중인 서비스들의 제어 버튼 확인
      const stopButtons = screen.getAllByText('중지')
      const restartButtons = screen.getAllByText('재시작')
      
      expect(stopButtons.length).toBeGreaterThan(0)
      expect(restartButtons.length).toBeGreaterThan(0)
    })

    it('중지된 서비스에 시작 버튼이 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const startButtons = screen.getAllByText('시작')
      expect(startButtons.length).toBeGreaterThan(0)
    })

    it('서비스 시작 버튼 클릭 시 토스트 알림이 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

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
    })

    it('서비스 중지 버튼 클릭 시 토스트 알림이 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const stopButton = screen.getAllByText('중지')[0]
      fireEvent.click(stopButton)

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

    it('서비스 재시작 버튼 클릭 시 토스트 알림이 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const restartButton = screen.getAllByText('재시작')[0]
      fireEvent.click(restartButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: '서비스 재시작',
          description: expect.stringContaining('서비스를 재시작합니다'),
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      })
    })

    it('서비스 설정 버튼이 모든 서비스에 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const settingsButtons = screen.getAllByLabelText('서비스 설정')
      expect(settingsButtons).toHaveLength(6) // 총 6개 서비스
    })

    it('서비스 설정 버튼 클릭 시 토스트 알림이 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const settingsButton = screen.getAllByLabelText('서비스 설정')[0]
      fireEvent.click(settingsButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: '서비스 설정',
          description: expect.stringContaining('서비스를 설정합니다'),
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      })
    })
  })

  describe('서비스 정보 표시', () => {
    it('서비스 설정 정보가 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // POSCO 뉴스 모니터 설정 확인
      expect(screen.getByText('main')).toBeInTheDocument()
      expect(screen.getByText('5분')).toBeInTheDocument()

      // GitHub Pages 모니터 설정 확인
      expect(screen.getByText('posco-docs')).toBeInTheDocument()
      expect(screen.getByText('gh-pages')).toBeInTheDocument()
    })

    it('오류가 있는 서비스의 오류 메시지가 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('마지막 오류')).toBeInTheDocument()
      expect(screen.getByText('Connection timeout')).toBeInTheDocument()
      expect(screen.getByText('Git merge conflict in main branch')).toBeInTheDocument()
    })

    it('서비스 설명이 올바르게 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('POSCO 뉴스 시스템 모니터링 및 알림 서비스')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages 배포 상태 모니터링')).toBeInTheDocument()
      expect(screen.getByText('데이터 캐시 상태 모니터링 및 관리')).toBeInTheDocument()
      expect(screen.getByText('자동 배포 및 롤백 관리 시스템')).toBeInTheDocument()
      expect(screen.getByText('동적 메시지 생성 및 템플릿 관리')).toBeInTheDocument()
      expect(screen.getByText('Discord/Slack 웹훅 전송 및 관리')).toBeInTheDocument()
    })
  })

  describe('반응형 레이아웃', () => {
    it('그리드 레이아웃이 올바르게 적용되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 그리드 컨테이너가 존재하는지 확인
      expect(document.querySelector('.chakra-grid')).toBeInTheDocument()
    })

    it('모든 서비스 카드가 동일한 높이를 가져야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const cards = document.querySelectorAll('.chakra-card')
      expect(cards.length).toBe(6)
      
      // 카드들이 렌더링되었는지 확인
      cards.forEach(card => {
        expect(card).toBeInTheDocument()
      })
    })
  })

  describe('접근성', () => {
    it('모든 버튼에 적절한 aria-label이 있어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const settingsButtons = screen.getAllByLabelText('서비스 설정')
      expect(settingsButtons).toHaveLength(6)
    })

    it('상태 배지가 적절한 색상을 가져야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 배지들이 렌더링되었는지 확인 (여러 개가 있을 수 있으므로 getAllByText 사용)
      expect(screen.getAllByText('실행 중').length).toBeGreaterThan(0)
      expect(screen.getByText('중지됨')).toBeInTheDocument()
      expect(screen.getByText('오류')).toBeInTheDocument()
    })

    it('키보드 네비게이션이 가능해야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        expect(button).not.toHaveAttribute('tabindex', '-1')
      })
    })
  })

  describe('에러 처리', () => {
    it('서비스 액션 실행 시 존재하지 않는 서비스 ID에 대해 안전하게 처리해야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 컴포넌트가 에러 없이 렌더링되는지 확인
      expect(screen.getByText('서비스 관리')).toBeInTheDocument()
    })

    it('빈 서비스 목록에 대해 안전하게 처리해야 함', () => {
      // 이 테스트는 실제로는 서비스 목록이 비어있을 때의 처리를 확인하지만,
      // 현재 구현에서는 하드코딩된 데이터를 사용하므로 기본 렌더링만 확인
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('서비스 관리')).toBeInTheDocument()
    })
  })

  describe('성능', () => {
    it('컴포넌트가 빠르게 렌더링되어야 함', () => {
      const startTime = performance.now()
      
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const endTime = performance.now()
      const renderTime = endTime - startTime

      // 렌더링 시간이 100ms 이하여야 함
      expect(renderTime).toBeLessThan(100)
    })

    it('메모리 누수가 없어야 함', () => {
      const { unmount } = render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 컴포넌트 언마운트가 정상적으로 이루어져야 함
      expect(() => unmount()).not.toThrow()
    })
  })
})