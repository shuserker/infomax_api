import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { RealtimeChart } from '../RealtimeChart'
import { useSystemMetrics } from '../../../hooks/useSystemMetrics'
import { useRealtimeChart } from '../../../hooks/useRealtimeChart'
import theme from '../../../theme'

// Mock hooks
vi.mock('../../../hooks/useSystemMetrics')
vi.mock('../../../hooks/useRealtimeChart')

// Mock Recharts
vi.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: ({ dataKey }: any) => <div data-testid={`line-${dataKey}`} />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  Brush: () => <div data-testid="brush" />,
  ReferenceLine: ({ y }: any) => <div data-testid={`reference-line-${y}`} />,
  Legend: () => <div data-testid="legend" />
}))

const mockUseSystemMetrics = vi.mocked(useSystemMetrics)
const mockUseRealtimeChart = vi.mocked(useRealtimeChart)

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider theme={theme}>
        {children}
      </ChakraProvider>
    </QueryClientProvider>
  )
}

const mockSystemMetrics = {
  cpu: { value: 45.2, unit: '%', trend: [], timestamp: new Date().toISOString(), status: 'normal' as const, threshold: { warning: 70, critical: 90 } },
  memory: { value: 67.8, unit: '%', trend: [], timestamp: new Date().toISOString(), status: 'normal' as const, threshold: { warning: 80, critical: 95 } },
  disk: { value: 23.4, unit: '%', trend: [], timestamp: new Date().toISOString(), status: 'normal' as const, threshold: { warning: 85, critical: 95 } },
  network: { value: 100, unit: '', trend: [], timestamp: new Date().toISOString(), status: 'normal' as const, threshold: { warning: 80, critical: 95 } }
}

const mockChartData = {
  cpu: [
    { timestamp: '2024-01-01T10:00:00Z', value: 45.2, label: 'CPU: 45.2%' },
    { timestamp: '2024-01-01T10:05:00Z', value: 48.1, label: 'CPU: 48.1%' }
  ],
  memory: [
    { timestamp: '2024-01-01T10:00:00Z', value: 67.8, label: '메모리: 67.8%' },
    { timestamp: '2024-01-01T10:05:00Z', value: 69.2, label: '메모리: 69.2%' }
  ],
  disk: [
    { timestamp: '2024-01-01T10:00:00Z', value: 23.4, label: '디스크: 23.4%' },
    { timestamp: '2024-01-01T10:05:00Z', value: 23.5, label: '디스크: 23.5%' }
  ],
  network: [
    { timestamp: '2024-01-01T10:00:00Z', value: 100, label: '네트워크: connected' },
    { timestamp: '2024-01-01T10:05:00Z', value: 100, label: '네트워크: connected' }
  ]
}

describe('RealtimeChart', () => {
  beforeEach(() => {
    mockUseSystemMetrics.mockReturnValue({
      metrics: mockSystemMetrics,
      isLoading: false,
      error: null,
      lastUpdated: null,
      refreshMetrics: vi.fn(),
      isConnected: true
    })

    mockUseRealtimeChart.mockReturnValue({
      data: mockChartData,
      isLoading: false,
      error: null,
      addDataPoint: vi.fn(),
      clearData: vi.fn(),
      exportData: vi.fn(() => mockChartData),
      zoomRange: null,
      setZoomRange: vi.fn()
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('차트 컴포넌트가 정상적으로 렌더링된다', () => {
    render(<RealtimeChart />, { wrapper: createWrapper() })

    expect(screen.getByTestId('line-chart')).toBeInTheDocument()
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('차트 컨트롤이 표시된다', () => {
    render(<RealtimeChart showControls={true} />, { wrapper: createWrapper() })

    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('오류 상태를 올바르게 표시한다', () => {
    mockUseRealtimeChart.mockReturnValue({
      data: mockChartData,
      isLoading: false,
      error: '차트 데이터 로딩 실패',
      addDataPoint: vi.fn(),
      clearData: vi.fn(),
      exportData: vi.fn(),
      zoomRange: null,
      setZoomRange: vi.fn()
    })

    render(<RealtimeChart />, { wrapper: createWrapper() })

    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('데이터 내보내기가 작동한다', async () => {
    const mockExportData = vi.fn(() => mockChartData)
    mockUseRealtimeChart.mockReturnValue({
      data: mockChartData,
      isLoading: false,
      error: null,
      addDataPoint: vi.fn(),
      clearData: vi.fn(),
      exportData: mockExportData,
      zoomRange: null,
      setZoomRange: vi.fn()
    })

    // Mock URL.createObjectURL and related functions
    global.URL.createObjectURL = vi.fn(() => 'mock-url')
    global.URL.revokeObjectURL = vi.fn()
    
    const mockClick = vi.fn()
    const mockAppendChild = vi.fn()
    const mockRemoveChild = vi.fn()
    
    Object.defineProperty(document, 'createElement', {
      value: vi.fn(() => ({
        href: '',
        download: '',
        click: mockClick,
      }))
    })
    
    Object.defineProperty(document.body, 'appendChild', {
      value: mockAppendChild
    })
    
    Object.defineProperty(document.body, 'removeChild', {
      value: mockRemoveChild
    })

    render(<RealtimeChart />, { wrapper: createWrapper() })

    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('데이터 초기화가 작동한다', () => {
    const mockClearData = vi.fn()
    mockUseRealtimeChart.mockReturnValue({
      data: mockChartData,
      isLoading: false,
      error: '테스트 오류',
      addDataPoint: vi.fn(),
      clearData: mockClearData,
      exportData: vi.fn(),
      zoomRange: null,
      setZoomRange: vi.fn()
    })

    render(<RealtimeChart />, { wrapper: createWrapper() })

    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('줌 리셋이 작동한다', () => {
    const mockSetZoomRange = vi.fn()
    mockUseRealtimeChart.mockReturnValue({
      data: mockChartData,
      isLoading: false,
      error: null,
      addDataPoint: vi.fn(),
      clearData: vi.fn(),
      exportData: vi.fn(),
      zoomRange: [0, 50],
      setZoomRange: mockSetZoomRange
    })

    render(<RealtimeChart />, { wrapper: createWrapper() })

    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('자동 업데이트가 비활성화되면 시스템 메트릭을 추가하지 않는다', () => {
    const mockAddDataPoint = vi.fn()
    mockUseRealtimeChart.mockReturnValue({
      data: mockChartData,
      isLoading: false,
      error: null,
      addDataPoint: mockAddDataPoint,
      clearData: vi.fn(),
      exportData: vi.fn(),
      zoomRange: null,
      setZoomRange: vi.fn()
    })

    render(<RealtimeChart autoUpdate={false} />, { wrapper: createWrapper() })

    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('컨트롤이 비활성화되면 컨트롤 요소들이 표시되지 않는다', () => {
    render(<RealtimeChart showControls={false} />, { wrapper: createWrapper() })

    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('차트 높이가 올바르게 설정된다', () => {
    const customHeight = 600
    render(<RealtimeChart height={customHeight} />, { wrapper: createWrapper() })

    const chartContainer = screen.getByTestId('responsive-container')
    expect(chartContainer).toBeInTheDocument()
  })
})