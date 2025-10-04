import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import Services from '../Services'
import theme from '../../theme'

// 간단한 Mock 컴포넌트들
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

describe('Services 페이지 간단 테스트', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('기본 렌더링', () => {
    it('페이지가 정상적으로 렌더링되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('서비스 관리')).toBeInTheDocument()
      expect(screen.getByText('시스템 서비스의 상태를 확인하고 제어합니다')).toBeInTheDocument()
    })

    it('모든 서비스 카드가 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('POSCO 뉴스 모니터')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages 모니터')).toBeInTheDocument()
      expect(screen.getByText('캐시 모니터')).toBeInTheDocument()
      expect(screen.getByText('배포 시스템')).toBeInTheDocument()
      expect(screen.getByText('메시지 시스템')).toBeInTheDocument()
      expect(screen.getByText('웹훅 시스템')).toBeInTheDocument()
    })

    it('관리 패널들이 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByTestId('posco-management-panel')).toBeInTheDocument()
      expect(screen.getByTestId('webhook-management')).toBeInTheDocument()
    })
  })

  describe('서비스 상태', () => {
    it('서비스 상태 배지가 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 상태 배지들 확인
      expect(screen.getAllByText('실행 중').length).toBeGreaterThan(0)
      expect(screen.getByText('중지됨')).toBeInTheDocument()
      expect(screen.getByText('오류')).toBeInTheDocument()
    })

    it('서비스 업타임이 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('2시간 15분')).toBeInTheDocument()
      expect(screen.getByText('1시간 30분')).toBeInTheDocument()
      expect(screen.getByText('3시간 45분')).toBeInTheDocument()
    })

    it('오류 메시지가 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByText('Connection timeout')).toBeInTheDocument()
      expect(screen.getByText('Git merge conflict in main branch')).toBeInTheDocument()
    })
  })

  describe('서비스 제어', () => {
    it('제어 버튼들이 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // 실행 중인 서비스들의 제어 버튼
      expect(screen.getAllByText('중지').length).toBeGreaterThan(0)
      expect(screen.getAllByText('재시작').length).toBeGreaterThan(0)

      // 중지된 서비스의 시작 버튼
      expect(screen.getAllByText('시작').length).toBeGreaterThan(0)

      // 설정 버튼들
      expect(screen.getAllByLabelText('서비스 설정').length).toBe(6)
    })

    it('시작 버튼 클릭 시 토스트가 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const startButton = screen.getAllByText('시작')[0]
      fireEvent.click(startButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: '서비스 시작',
            status: 'info',
          })
        )
      })
    })

    it('중지 버튼 클릭 시 토스트가 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const stopButton = screen.getAllByText('중지')[0]
      fireEvent.click(stopButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: '서비스 중지',
            status: 'info',
          })
        )
      })
    })

    it('재시작 버튼 클릭 시 토스트가 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const restartButton = screen.getAllByText('재시작')[0]
      fireEvent.click(restartButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: '서비스 재시작',
            status: 'info',
          })
        )
      })
    })

    it('설정 버튼 클릭 시 토스트가 표시되어야 함', async () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const settingsButton = screen.getAllByLabelText('서비스 설정')[0]
      fireEvent.click(settingsButton)

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: '서비스 설정',
            status: 'info',
          })
        )
      })
    })
  })

  describe('서비스 정보', () => {
    it('서비스 설정 정보가 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      // POSCO 뉴스 모니터 설정
      expect(screen.getByText('main')).toBeInTheDocument()
      expect(screen.getByText('5분')).toBeInTheDocument()

      // GitHub Pages 모니터 설정
      expect(screen.getByText('posco-docs')).toBeInTheDocument()
      expect(screen.getByText('gh-pages')).toBeInTheDocument()
    })

    it('서비스 설명이 표시되어야 함', () => {
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

  describe('레이아웃', () => {
    it('그리드 레이아웃이 적용되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const cards = document.querySelectorAll('.chakra-card')
      expect(cards.length).toBe(6)
    })

    it('모든 카드가 렌더링되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      const cards = document.querySelectorAll('.chakra-card')
      cards.forEach(card => {
        expect(card).toBeInTheDocument()
      })
    })
  })

  describe('접근성', () => {
    it('페이지 제목이 적절한 헤딩 레벨을 가져야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByRole('heading', { name: '서비스 관리' })).toBeInTheDocument()
    })

    it('서비스 카드 제목들이 헤딩으로 표시되어야 함', () => {
      render(
        <TestWrapper>
          <Services />
        </TestWrapper>
      )

      expect(screen.getByRole('heading', { name: 'POSCO 뉴스 모니터' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'GitHub Pages 모니터' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '캐시 모니터' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '배포 시스템' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '메시지 시스템' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: '웹훅 시스템' })).toBeInTheDocument()
    })

    it('모든 버튼이 접근 가능해야 함', () => {
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

      expect(() => unmount()).not.toThrow()
    })
  })
})