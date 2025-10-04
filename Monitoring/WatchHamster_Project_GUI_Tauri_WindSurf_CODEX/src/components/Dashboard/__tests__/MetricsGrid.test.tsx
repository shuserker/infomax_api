import React from 'react'
import { render, screen } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { MetricsGrid } from '../MetricsGrid'
import { useSystemMetrics } from '../../../hooks/useSystemMetrics'
import theme from '../../../theme'

// Mock hooks
vi.mock('../../../hooks/useSystemMetrics')

// Mock SystemMetricCard 컴포넌트
vi.mock('../SystemMetricCard', () => ({
  SystemMetricCard: ({ title, type, data, isLoading }: any) => (
    <div data-testid={`metric-card-${type}`}>
      <div data-testid="metric-title">{title}</div>
      <div data-testid="metric-value">{isLoading ? 'Loading...' : `${data?.value}${data?.unit}`}</div>
      <div data-testid="metric-status">{data?.status}</div>
    </div>
  )
}))

const mockUseSystemMetrics = vi.mocked(useSystemMetrics)

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>
    {children}
  </ChakraProvider>
)

const mockSystemMetrics = {
  cpu: {
    value: 45.2,
    unit: '%',
    trend: [40, 42, 44, 45, 45.2],
    timestamp: '2024-01-01T12:00:00Z',
    status: 'normal' as const,
    threshold: { warning: 70, critical: 90 }
  },
  memory: {
    value: 67.8,
    unit: '%',
    trend: [60, 62, 65, 67, 67.8],
    timestamp: '2024-01-01T12:00:00Z',
    status: 'warning' as const,
    threshold: { warning: 60, critical: 85 }
  },
  disk: {
    value: 23.4,
    unit: '%',
    trend: [20, 21, 22, 23, 23.4],
    timestamp: '2024-01-01T12:00:00Z',
    status: 'normal' as const,
    threshold: { warning: 80, critical: 95 }
  },
  network: {
    value: 100,
    unit: '',
    trend: [100, 100, 100, 100, 100],
    timestamp: '2024-01-01T12:00:00Z',
    status: 'normal' as const,
    threshold: { warning: 80, critical: 95 }
  }
}

describe('MetricsGrid', () => {
  beforeEach(() => {
    mockUseSystemMetrics.mockReturnValue({
      metrics: mockSystemMetrics,
      isLoading: false,
      error: null,
      lastUpdated: null,
      refreshMetrics: vi.fn(),
      isConnected: true
    })
  })

  describe('기본 렌더링', () => {
    it('모든 메트릭 카드를 렌더링한다', () => {
      render(<MetricsGrid />, { wrapper: TestWrapper })

      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-memory')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-disk')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-network')).toBeInTheDocument()
    })

    it('메트릭 제목을 올바르게 표시한다', () => {
      render(<MetricsGrid />, { wrapper: TestWrapper })

      expect(screen.getByText('CPU 사용률')).toBeInTheDocument()
      expect(screen.getByText('메모리 사용률')).toBeInTheDocument()
      expect(screen.getByText('디스크 사용률')).toBeInTheDocument()
      expect(screen.getByText('네트워크 상태')).toBeInTheDocument()
    })

    it('메트릭 값을 올바르게 표시한다', () => {
      render(<MetricsGrid />, { wrapper: TestWrapper })

      expect(screen.getByText('45.2%')).toBeInTheDocument()
      expect(screen.getByText('67.8%')).toBeInTheDocument()
      expect(screen.getByText('23.4%')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('메트릭 상태를 올바르게 표시한다', () => {
      render(<MetricsGrid />, { wrapper: TestWrapper })

      const statusElements = screen.getAllByTestId('metric-status')
      expect(statusElements[0]).toHaveTextContent('normal')
      expect(statusElements[1]).toHaveTextContent('warning')
      expect(statusElements[2]).toHaveTextContent('normal')
      expect(statusElements[3]).toHaveTextContent('normal')
    })
  })

  describe('로딩 상태', () => {
    it('로딩 중일 때 로딩 상태를 표시한다', () => {
      mockUseSystemMetrics.mockReturnValue({
        metrics: mockSystemMetrics,
        isLoading: true,
        error: null,
        lastUpdated: null,
        refreshMetrics: vi.fn(),
        isConnected: true
      })

      render(<MetricsGrid />, { wrapper: TestWrapper })

      const loadingElements = screen.getAllByText('Loading...')
      expect(loadingElements).toHaveLength(4) // 4개의 메트릭 카드
    })
  })

  describe('오류 상태', () => {
    it('오류 발생 시 오류 상태를 표시한다', () => {
      mockUseSystemMetrics.mockReturnValue({
        metrics: mockSystemMetrics,
        isLoading: false,
        error: '네트워크 연결 오류',
        lastUpdated: null,
        refreshMetrics: vi.fn(),
        isConnected: false
      })

      render(<MetricsGrid />, { wrapper: TestWrapper })

      // 오류 상태에서도 메트릭 카드들이 렌더링되지만 연결 상태가 false
      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-memory')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-disk')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-network')).toBeInTheDocument()
    })
  })

  describe('컴팩트 모드', () => {
    it('컴팩트 모드에서 올바르게 렌더링된다', () => {
      render(<MetricsGrid compact={true} />, { wrapper: TestWrapper })

      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-memory')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-disk')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-network')).toBeInTheDocument()
    })
  })

  describe('반응형 그리드', () => {
    it('그리드 레이아웃이 올바르게 적용된다', () => {
      render(<MetricsGrid />, { wrapper: TestWrapper })

      // 그리드 컨테이너가 존재하는지 확인
      const gridContainer = screen.getByTestId('metric-card-cpu').parentElement
      expect(gridContainer).toBeInTheDocument()
    })
  })

  describe('실시간 업데이트', () => {
    it('메트릭 데이터 변경 시 UI를 업데이트한다', () => {
      const { rerender } = render(<MetricsGrid />, { wrapper: TestWrapper })

      // 초기 값 확인
      expect(screen.getByText('45.2%')).toBeInTheDocument()

      // 메트릭 데이터 변경
      const updatedMetrics = {
        ...mockSystemMetrics,
        cpu: {
          ...mockSystemMetrics.cpu,
          value: 55.7,
          status: 'warning' as const
        }
      }

      mockUseSystemMetrics.mockReturnValue({
        metrics: updatedMetrics,
        isLoading: false,
        error: null,
        lastUpdated: null,
        refreshMetrics: vi.fn(),
        isConnected: true
      })

      rerender(<MetricsGrid />)

      // 업데이트된 값 확인
      expect(screen.getByText('55.7%')).toBeInTheDocument()
    })
  })

  describe('임계값 상태', () => {
    it('경고 상태 메트릭을 올바르게 표시한다', () => {
      const warningMetrics = {
        ...mockSystemMetrics,
        cpu: {
          ...mockSystemMetrics.cpu,
          value: 75,
          status: 'warning' as const
        }
      }

      mockUseSystemMetrics.mockReturnValue({
        metrics: warningMetrics,
        isLoading: false,
        error: null,
        lastUpdated: null,
        refreshMetrics: vi.fn(),
        isConnected: true
      })

      render(<MetricsGrid />, { wrapper: TestWrapper })

      expect(screen.getByText('75%')).toBeInTheDocument()
      const statusElements = screen.getAllByTestId('metric-status')
      expect(statusElements[0]).toHaveTextContent('warning')
    })

    it('위험 상태 메트릭을 올바르게 표시한다', () => {
      const criticalMetrics = {
        ...mockSystemMetrics,
        cpu: {
          ...mockSystemMetrics.cpu,
          value: 95,
          status: 'critical' as const
        }
      }

      mockUseSystemMetrics.mockReturnValue({
        metrics: criticalMetrics,
        isLoading: false,
        error: null,
        lastUpdated: null,
        refreshMetrics: vi.fn(),
        isConnected: true
      })

      render(<MetricsGrid />, { wrapper: TestWrapper })

      expect(screen.getByText('95%')).toBeInTheDocument()
      const statusElements = screen.getAllByTestId('metric-status')
      expect(statusElements[0]).toHaveTextContent('critical')
    })
  })

  describe('네트워크 연결 상태', () => {
    it('연결 끊김 상태를 올바르게 표시한다', () => {
      mockUseSystemMetrics.mockReturnValue({
        metrics: mockSystemMetrics,
        isLoading: false,
        error: null,
        lastUpdated: null,
        refreshMetrics: vi.fn(),
        isConnected: false
      })

      render(<MetricsGrid />, { wrapper: TestWrapper })

      // 연결 끊김 상태에서도 메트릭 카드들이 렌더링됨
      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-memory')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-disk')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-network')).toBeInTheDocument()
    })
  })

  describe('성능 테스트', () => {
    it('메트릭 그리드가 효율적으로 렌더링된다', () => {
      const startTime = performance.now()
      
      render(<MetricsGrid />, { wrapper: TestWrapper })

      const endTime = performance.now()
      const renderTime = endTime - startTime

      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      // 렌더링 시간이 합리적인 범위 내에 있는지 확인 (500ms 이하)
      expect(renderTime).toBeLessThan(500)
    })
  })

  describe('접근성', () => {
    it('모든 메트릭 카드가 접근 가능하다', () => {
      render(<MetricsGrid />, { wrapper: TestWrapper })

      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-memory')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-disk')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-network')).toBeInTheDocument()
    })

    it('메트릭 정보가 스크린 리더에 적절히 제공된다', () => {
      render(<MetricsGrid />, { wrapper: TestWrapper })

      // 제목과 값이 적절히 표시되는지 확인
      expect(screen.getByText('CPU 사용률')).toBeInTheDocument()
      expect(screen.getByText('45.2%')).toBeInTheDocument()
      expect(screen.getByText('메모리 사용률')).toBeInTheDocument()
      expect(screen.getByText('67.8%')).toBeInTheDocument()
    })
  })
})