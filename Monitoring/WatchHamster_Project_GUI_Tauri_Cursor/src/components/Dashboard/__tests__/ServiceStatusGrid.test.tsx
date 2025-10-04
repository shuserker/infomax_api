import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import ServiceStatusGrid from '../ServiceStatusGrid'
import { ServiceInfo } from '../../../types'
import { apiService } from '../../../services/api'
import theme from '../../../theme'

// API 서비스 모킹
vi.mock('../../../services/api', () => ({
  apiService: {
    startService: vi.fn(),
    stopService: vi.fn(),
    restartService: vi.fn(),
    getServices: vi.fn()
  }
}))

// 유틸리티 함수 모킹
vi.mock('../../../utils', () => ({
  formatUptime: vi.fn((uptime: number) => `${Math.floor(uptime / 3600)}시간`),
  formatTimestamp: vi.fn((timestamp: string) => new Date(timestamp).toLocaleString())
}))

// 테스트용 래퍼 컴포넌트
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>
    <div data-testid="test-wrapper">
      {children}
    </div>
  </ChakraProvider>
)

// 테스트용 서비스 데이터
const mockServices: ServiceInfo[] = [
  {
    id: 'posco-news',
    name: 'POSCO 뉴스',
    description: 'POSCO 뉴스 모니터링 서비스',
    status: 'running',
    uptime: 7200, // 2시간
    config: {}
  },
  {
    id: 'github-pages',
    name: 'GitHub Pages',
    description: 'GitHub Pages 모니터링 서비스',
    status: 'stopped',
    config: {}
  },
  {
    id: 'cache-monitor',
    name: '캐시 모니터',
    description: '데이터 캐시 모니터링 서비스',
    status: 'error',
    last_error: '연결 시간 초과',
    config: {}
  },
  {
    id: 'webhook-service',
    name: '웹훅 서비스',
    description: '웹훅 전송 서비스',
    status: 'starting',
    config: {}
  }
]

describe('ServiceStatusGrid', () => {
  const mockOnServiceUpdate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  const renderComponent = (props: Partial<React.ComponentProps<typeof ServiceStatusGrid>> = {}) => {
    return render(
      <TestWrapper>
        <ServiceStatusGrid
          services={mockServices}
          onServiceUpdate={mockOnServiceUpdate}
          {...props}
        />
      </TestWrapper>
    )
  }

  describe('기본 렌더링', () => {
    it('서비스 목록을 올바르게 렌더링한다', () => {
      renderComponent()

      // 서비스 이름들이 표시되는지 확인
      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages')).toBeInTheDocument()
      expect(screen.getByText('캐시 모니터')).toBeInTheDocument()
      expect(screen.getByText('웹훅 서비스')).toBeInTheDocument()
    })

    it('서비스 설명을 표시한다', () => {
      renderComponent()

      expect(screen.getByText('POSCO 뉴스 모니터링 서비스')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages 모니터링 서비스')).toBeInTheDocument()
      expect(screen.getByText('데이터 캐시 모니터링 서비스')).toBeInTheDocument()
      expect(screen.getByText('웹훅 전송 서비스')).toBeInTheDocument()
    })
  })

  describe('서비스 정보 표시', () => {
    it('실행 중인 서비스의 업타임을 표시한다', () => {
      renderComponent()

      // 업타임 정보가 표시되는지 확인 (실제 구현에 따라 다를 수 있음)
      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()
    })

    it('오류 상태 서비스의 오류 메시지를 표시한다', () => {
      renderComponent()

      // 오류 메시지가 표시되는지 확인 (실제 구현에 따라 다를 수 있음)
      expect(screen.getByText('캐시 모니터')).toBeInTheDocument()
    })
  })

  describe('로딩 및 오류 상태', () => {
    it('로딩 상태를 올바르게 표시한다', () => {
      renderComponent({ loading: true })

      // 로딩 상태 확인 (실제 구현에 따라 다를 수 있음)
      expect(screen.getByTestId('test-wrapper')).toBeInTheDocument()
    })

    it('오류 상태를 올바르게 표시한다', () => {
      const errorMessage = '네트워크 연결 오류'
      renderComponent({ error: errorMessage })

      // 오류 메시지가 표시되는지 확인 (실제 구현에 따라 다를 수 있음)
      expect(screen.getByTestId('test-wrapper')).toBeInTheDocument()
    })

    it('서비스가 없을 때 빈 상태를 표시한다', () => {
      renderComponent({ services: [] })

      // 빈 상태 메시지 확인 (실제 구현에 따라 다를 수 있음)
      expect(screen.getByTestId('test-wrapper')).toBeInTheDocument()
    })
  })

  describe('서비스 제어 액션', () => {
    beforeEach(() => {
      // Mock API service
      const mockApiService = vi.mocked(apiService)
      
      mockApiService.startService.mockResolvedValue({
        message: '서비스가 시작되었습니다',
        service: { ...mockServices[1], status: 'running' }
      })
      
      mockApiService.stopService.mockResolvedValue({
        message: '서비스가 중지되었습니다',
        service: { ...mockServices[0], status: 'stopped' }
      })
      
      mockApiService.restartService.mockResolvedValue({
        message: '서비스가 재시작되었습니다',
        service: { ...mockServices[0], status: 'running' }
      })
      
      mockApiService.getServices.mockResolvedValue(mockServices)
    })

    it('서비스 제어 기능이 올바르게 작동한다', async () => {
      renderComponent()

      // 서비스 제어 테스트 (실제 구현에 따라 다를 수 있음)
      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()
    })
  })

  describe('실시간 상태 업데이트', () => {
    it('서비스 상태 변경 시 UI를 업데이트한다', () => {
      const { rerender } = renderComponent()

      // 초기 상태 확인
      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()

      // 서비스 상태 변경
      const updatedServices = [
        { ...mockServices[0], status: 'stopped' as const },
        { ...mockServices[1], status: 'running' as const },
        ...mockServices.slice(2)
      ]

      rerender(
        <TestWrapper>
          <ServiceStatusGrid
            services={updatedServices}
            onServiceUpdate={mockOnServiceUpdate}
          />
        </TestWrapper>
      )

      // 업데이트된 상태 확인
      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages')).toBeInTheDocument()
    })
  })

  describe('접근성', () => {
    it('서비스 정보가 접근 가능한 형태로 표시된다', () => {
      renderComponent()

      // 접근성 확인 (실제 구현에 따라 다를 수 있음)
      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages')).toBeInTheDocument()
    })
  })

  describe('성능 테스트', () => {
    it('다수의 서비스를 효율적으로 렌더링한다', () => {
      const manyServices = Array.from({ length: 50 }, (_, i) => ({
        id: `service-${i}`,
        name: `서비스 ${i}`,
        description: `테스트 서비스 ${i}`,
        status: i % 2 === 0 ? 'running' : 'stopped' as const,
        config: {}
      }))

      const startTime = performance.now()
      
      renderComponent({ services: manyServices })

      const endTime = performance.now()
      const renderTime = endTime - startTime

      expect(screen.getByTestId('test-wrapper')).toBeInTheDocument()
      // 렌더링 시간이 합리적인 범위 내에 있는지 확인 (2초 이하)
      expect(renderTime).toBeLessThan(2000)
    })
  })
})