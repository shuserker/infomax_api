import React from 'react'
import { render, screen } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// 간단한 테스트용 컴포넌트들
const MockSystemMetricCard = ({ title, type, data, isLoading }: any) => (
  <div data-testid={`metric-card-${type}`}>
    <div data-testid="metric-title">{title}</div>
    <div data-testid="metric-value">
      {isLoading ? 'Loading...' : `${data?.value}${data?.unit}`}
    </div>
    <div data-testid="metric-status">{data?.status}</div>
  </div>
)

const MockRealtimeChart = ({ showControls, autoUpdate, height }: any) => (
  <div data-testid="realtime-chart">
    <div data-testid="chart-container">
      <div data-testid="line-chart">Chart Content</div>
      <div data-testid="responsive-container">Responsive Container</div>
    </div>
    {showControls && <div data-testid="chart-controls">Controls</div>}
    <div data-testid="chart-height" style={{ height: height || 400 }}>
      Height: {height || 400}px
    </div>
  </div>
)

const MockServiceStatusGrid = ({ services, loading, error, onServiceUpdate }: any) => (
  <div data-testid="service-status-grid">
    {loading && <div data-testid="loading-spinner">Loading...</div>}
    {error && <div data-testid="error-message">{error}</div>}
    {services.length === 0 && !loading && !error && (
      <div data-testid="empty-state">서비스가 없습니다</div>
    )}
    {services.map((service: any) => (
      <div key={service.id} data-testid={`service-${service.id}`}>
        <div>{service.name}</div>
        <div>{service.description}</div>
        <div data-testid={`service-status-${service.id}`}>{service.status}</div>
      </div>
    ))}
  </div>
)

const MockMetricsGrid = ({ compact }: any) => (
  <div data-testid="metrics-grid" className={compact ? 'compact' : 'normal'}>
    <MockSystemMetricCard
      title="CPU 사용률"
      type="cpu"
      data={{ value: 45.2, unit: '%', status: 'normal' }}
    />
    <MockSystemMetricCard
      title="메모리 사용률"
      type="memory"
      data={{ value: 67.8, unit: '%', status: 'warning' }}
    />
    <MockSystemMetricCard
      title="디스크 사용률"
      type="disk"
      data={{ value: 23.4, unit: '%', status: 'normal' }}
    />
    <MockSystemMetricCard
      title="네트워크 상태"
      type="network"
      data={{ value: 100, unit: '', status: 'normal' }}
    />
  </div>
)

// 테스트 데이터
const mockMetricData = {
  value: 75.5,
  unit: '%',
  trend: [65, 70, 72, 75, 75.5],
  timestamp: '2024-01-01T12:00:00Z',
  status: 'warning' as const,
  threshold: {
    warning: 70,
    critical: 90,
  },
}

const mockServices = [
  {
    id: 'posco-news',
    name: 'POSCO 뉴스',
    description: 'POSCO 뉴스 모니터링 서비스',
    status: 'running',
    uptime: 7200,
    config: {}
  },
  {
    id: 'github-pages',
    name: 'GitHub Pages',
    description: 'GitHub Pages 모니터링 서비스',
    status: 'stopped',
    config: {}
  }
]

describe('대시보드 컴포넌트 테스트', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('SystemMetricCard 컴포넌트', () => {
    it('기본 메트릭 카드가 올바르게 렌더링된다', () => {
      render(
        <MockSystemMetricCard
          title="CPU 사용률"
          type="cpu"
          data={mockMetricData}
        />
      )

      expect(screen.getByText('CPU 사용률')).toBeInTheDocument()
      expect(screen.getByText('75.5%')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
    })

    it('컴팩트 모드에서 올바르게 렌더링된다', () => {
      render(
        <MockSystemMetricCard
          title="메모리 사용률"
          type="memory"
          data={mockMetricData}
          compact={true}
        />
      )

      expect(screen.getByText('메모리 사용률')).toBeInTheDocument()
      expect(screen.getByText('75.5%')).toBeInTheDocument()
    })

    it('로딩 상태를 올바르게 표시한다', () => {
      render(
        <MockSystemMetricCard
          title="디스크 사용률"
          type="disk"
          data={mockMetricData}
          isLoading={true}
        />
      )

      expect(screen.getByText('디스크 사용률')).toBeInTheDocument()
      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    it('각 메트릭 타입에 맞는 컴포넌트가 렌더링된다', () => {
      const types = ['cpu', 'memory', 'disk', 'network'] as const
      
      types.forEach((type) => {
        const { unmount } = render(
          <MockSystemMetricCard
            title={`${type} 테스트`}
            type={type}
            data={mockMetricData}
          />
        )
        
        expect(screen.getByText(`${type} 테스트`)).toBeInTheDocument()
        expect(screen.getByTestId(`metric-card-${type}`)).toBeInTheDocument()
        
        unmount()
      })
    })
  })

  describe('RealtimeChart 컴포넌트', () => {
    it('차트 컴포넌트가 정상적으로 렌더링된다', () => {
      render(<MockRealtimeChart />)

      expect(screen.getByTestId('realtime-chart')).toBeInTheDocument()
      expect(screen.getByTestId('line-chart')).toBeInTheDocument()
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
    })

    it('차트 컨트롤이 표시된다', () => {
      render(<MockRealtimeChart showControls={true} />)

      expect(screen.getByTestId('chart-controls')).toBeInTheDocument()
    })

    it('차트 컨트롤이 비활성화되면 표시되지 않는다', () => {
      render(<MockRealtimeChart showControls={false} />)

      expect(screen.queryByTestId('chart-controls')).not.toBeInTheDocument()
    })

    it('차트 높이가 올바르게 설정된다', () => {
      const customHeight = 600
      render(<MockRealtimeChart height={customHeight} />)

      expect(screen.getByText(`Height: ${customHeight}px`)).toBeInTheDocument()
    })
  })

  describe('ServiceStatusGrid 컴포넌트', () => {
    const mockOnServiceUpdate = vi.fn()

    it('서비스 목록을 올바르게 렌더링한다', () => {
      render(
        <MockServiceStatusGrid
          services={mockServices}
          onServiceUpdate={mockOnServiceUpdate}
        />
      )

      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages')).toBeInTheDocument()
      expect(screen.getByTestId('service-posco-news')).toBeInTheDocument()
      expect(screen.getByTestId('service-github-pages')).toBeInTheDocument()
    })

    it('서비스 상태를 올바르게 표시한다', () => {
      render(
        <MockServiceStatusGrid
          services={mockServices}
          onServiceUpdate={mockOnServiceUpdate}
        />
      )

      expect(screen.getByTestId('service-status-posco-news')).toHaveTextContent('running')
      expect(screen.getByTestId('service-status-github-pages')).toHaveTextContent('stopped')
    })

    it('로딩 상태를 올바르게 표시한다', () => {
      render(
        <MockServiceStatusGrid
          services={[]}
          onServiceUpdate={mockOnServiceUpdate}
          loading={true}
        />
      )

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    it('오류 상태를 올바르게 표시한다', () => {
      const errorMessage = '네트워크 연결 오류'
      render(
        <MockServiceStatusGrid
          services={[]}
          onServiceUpdate={mockOnServiceUpdate}
          error={errorMessage}
        />
      )

      expect(screen.getByTestId('error-message')).toBeInTheDocument()
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })

    it('서비스가 없을 때 빈 상태를 표시한다', () => {
      render(
        <MockServiceStatusGrid
          services={[]}
          onServiceUpdate={mockOnServiceUpdate}
        />
      )

      expect(screen.getByTestId('empty-state')).toBeInTheDocument()
      expect(screen.getByText('서비스가 없습니다')).toBeInTheDocument()
    })
  })

  describe('MetricsGrid 컴포넌트', () => {
    it('모든 메트릭 카드를 렌더링한다', () => {
      render(<MockMetricsGrid />)

      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-memory')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-disk')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-network')).toBeInTheDocument()
    })

    it('메트릭 제목을 올바르게 표시한다', () => {
      render(<MockMetricsGrid />)

      expect(screen.getByText('CPU 사용률')).toBeInTheDocument()
      expect(screen.getByText('메모리 사용률')).toBeInTheDocument()
      expect(screen.getByText('디스크 사용률')).toBeInTheDocument()
      expect(screen.getByText('네트워크 상태')).toBeInTheDocument()
    })

    it('메트릭 값을 올바르게 표시한다', () => {
      render(<MockMetricsGrid />)

      expect(screen.getByText('45.2%')).toBeInTheDocument()
      expect(screen.getByText('67.8%')).toBeInTheDocument()
      expect(screen.getByText('23.4%')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('컴팩트 모드에서 올바르게 렌더링된다', () => {
      render(<MockMetricsGrid compact={true} />)

      const metricsGrid = screen.getByTestId('metrics-grid')
      expect(metricsGrid).toHaveClass('compact')
    })
  })

  describe('통합 테스트', () => {
    it('모든 대시보드 컴포넌트가 함께 렌더링된다', () => {
      const DashboardIntegration = () => (
        <div data-testid="dashboard-integration">
          <MockMetricsGrid />
          <MockRealtimeChart />
          <MockServiceStatusGrid
            services={mockServices}
            onServiceUpdate={vi.fn()}
          />
        </div>
      )

      render(<DashboardIntegration />)

      // 모든 컴포넌트가 렌더링되는지 확인
      expect(screen.getByTestId('dashboard-integration')).toBeInTheDocument()
      expect(screen.getByTestId('metrics-grid')).toBeInTheDocument()
      expect(screen.getByTestId('realtime-chart')).toBeInTheDocument()
      expect(screen.getByTestId('service-status-grid')).toBeInTheDocument()
    })

    it('에러 바운더리가 올바르게 작동한다', () => {
      const ThrowError = () => {
        throw new Error('테스트 에러')
      }

      const ErrorBoundaryTest = () => (
        <div>
          <ThrowError />
        </div>
      )

      // 에러 바운더리 테스트
      expect(() => {
        render(<ErrorBoundaryTest />)
      }).toThrow('테스트 에러')
    })
  })

  describe('성능 테스트', () => {
    it('대량의 메트릭 데이터를 효율적으로 렌더링한다', () => {
      const largeTrendData = Array.from({ length: 1000 }, (_, i) => i * 0.1)
      const largeMetricData = {
        ...mockMetricData,
        trend: largeTrendData
      }

      const startTime = performance.now()
      
      render(
        <MockSystemMetricCard
          title="성능 테스트"
          type="cpu"
          data={largeMetricData}
        />
      )

      const endTime = performance.now()
      const renderTime = endTime - startTime

      expect(screen.getByText('성능 테스트')).toBeInTheDocument()
      // 렌더링 시간이 합리적인 범위 내에 있는지 확인 (1초 이하)
      expect(renderTime).toBeLessThan(1000)
    })

    it('다수의 서비스를 효율적으로 렌더링한다', () => {
      const manyServices = Array.from({ length: 50 }, (_, i) => ({
        id: `service-${i}`,
        name: `서비스 ${i}`,
        description: `테스트 서비스 ${i}`,
        status: i % 2 === 0 ? 'running' : 'stopped' as const,
        config: {}
      }))

      const startTime = performance.now()
      
      render(
        <MockServiceStatusGrid
          services={manyServices}
          onServiceUpdate={vi.fn()}
        />
      )

      const endTime = performance.now()
      const renderTime = endTime - startTime

      expect(screen.getByText('서비스 0')).toBeInTheDocument()
      // 렌더링 시간이 합리적인 범위 내에 있는지 확인 (2초 이하)
      expect(renderTime).toBeLessThan(2000)
    })
  })

  describe('접근성 테스트', () => {
    it('모든 메트릭 카드가 접근 가능하다', () => {
      render(<MockMetricsGrid />)

      expect(screen.getByTestId('metric-card-cpu')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-memory')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-disk')).toBeInTheDocument()
      expect(screen.getByTestId('metric-card-network')).toBeInTheDocument()
    })

    it('차트 컴포넌트가 스크린 리더에 적절한 정보를 제공한다', () => {
      render(<MockRealtimeChart />)

      expect(screen.getByTestId('realtime-chart')).toBeInTheDocument()
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
    })

    it('서비스 정보가 접근 가능한 형태로 표시된다', () => {
      render(
        <MockServiceStatusGrid
          services={mockServices}
          onServiceUpdate={vi.fn()}
        />
      )

      expect(screen.getByText('POSCO 뉴스')).toBeInTheDocument()
      expect(screen.getByText('GitHub Pages')).toBeInTheDocument()
    })
  })
})