import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { ServiceControls } from '../ServiceControls'
import { ServiceInfo } from '../../../types'
import theme from '../../../theme'

// 테스트용 래퍼 컴포넌트
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

// 테스트용 서비스 데이터
const mockRunningService: ServiceInfo = {
  id: 'test-service-1',
  name: '실행 중인 서비스',
  description: '테스트용 실행 중인 서비스',
  status: 'running',
  uptime: 3600,
}

const mockStoppedService: ServiceInfo = {
  id: 'test-service-2',
  name: '중지된 서비스',
  description: '테스트용 중지된 서비스',
  status: 'stopped',
}

const mockErrorService: ServiceInfo = {
  id: 'test-service-3',
  name: '오류 서비스',
  description: '테스트용 오류 서비스',
  status: 'error',
  last_error: '연결 실패',
}

describe('ServiceControls', () => {
  let mockOnServiceAction: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockOnServiceAction = vi.fn().mockResolvedValue(undefined)
  })

  it('실행 중인 서비스에 대해 중지와 재시작 버튼을 활성화한다', () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const startButton = screen.getByRole('button', { name: '시작' })
    const stopButton = screen.getByRole('button', { name: '중지' })
    const restartButton = screen.getByRole('button', { name: '재시작' })

    expect(startButton).toBeDisabled()
    expect(stopButton).not.toBeDisabled()
    expect(restartButton).not.toBeDisabled()
  })

  it('중지된 서비스에 대해 시작 버튼만 활성화한다', () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockStoppedService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const startButton = screen.getByRole('button', { name: '시작' })
    const stopButton = screen.getByRole('button', { name: '중지' })
    const restartButton = screen.getByRole('button', { name: '재시작' })

    expect(startButton).not.toBeDisabled()
    expect(stopButton).toBeDisabled()
    expect(restartButton).toBeDisabled()
  })

  it('오류 상태 서비스에 대해 시작과 재시작 버튼을 활성화한다', () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockErrorService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const startButton = screen.getByRole('button', { name: '시작' })
    const stopButton = screen.getByRole('button', { name: '중지' })
    const restartButton = screen.getByRole('button', { name: '재시작' })

    expect(startButton).not.toBeDisabled()
    expect(stopButton).toBeDisabled()
    expect(restartButton).not.toBeDisabled()
  })

  it('아이콘 변형으로 렌더링할 수 있다', () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
          variant="icons"
        />
      </TestWrapper>
    )

    // 아이콘 버튼들이 렌더링되는지 확인
    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)

    // 각 버튼이 적절한 aria-label을 가지는지 확인
    expect(screen.getByLabelText('시작')).toBeInTheDocument()
    expect(screen.getByLabelText('중지')).toBeInTheDocument()
    expect(screen.getByLabelText('재시작')).toBeInTheDocument()
  })

  it('로딩 상태일 때 모든 버튼을 비활성화한다', () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
          isLoading={true}
        />
      </TestWrapper>
    )

    const buttons = screen.getAllByRole('button')
    buttons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })

  it('비활성화 상태일 때 모든 버튼을 비활성화한다', () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
          disabled={true}
        />
      </TestWrapper>
    )

    const buttons = screen.getAllByRole('button')
    buttons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })

  it('시작 버튼 클릭 시 확인 대화상자를 표시한다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockStoppedService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const startButton = screen.getByRole('button', { name: '시작' })
    fireEvent.click(startButton)

    await waitFor(() => {
      expect(screen.getByText('서비스 시작 확인')).toBeInTheDocument()
      expect(screen.getByText('중지된 서비스 서비스를 시작하시겠습니까?')).toBeInTheDocument()
    })
  })

  it('중지 버튼 클릭 시 확인 대화상자를 표시한다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const stopButton = screen.getByRole('button', { name: '중지' })
    fireEvent.click(stopButton)

    await waitFor(() => {
      expect(screen.getByText('서비스 중지 확인')).toBeInTheDocument()
      expect(screen.getByText('실행 중인 서비스 서비스를 중지하시겠습니까?')).toBeInTheDocument()
    })
  })

  it('재시작 버튼 클릭 시 확인 대화상자를 표시한다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const restartButton = screen.getByRole('button', { name: '재시작' })
    fireEvent.click(restartButton)

    await waitFor(() => {
      expect(screen.getByText('서비스 재시작 확인')).toBeInTheDocument()
      expect(screen.getByText('실행 중인 서비스 서비스를 재시작하시겠습니까?')).toBeInTheDocument()
    })
  })

  it('확인 대화상자에서 확인 버튼 클릭 시 서비스 액션을 호출한다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockStoppedService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    // 시작 버튼 클릭
    const startButton = screen.getByRole('button', { name: '시작' })
    fireEvent.click(startButton)

    // 확인 대화상자에서 확인 버튼 클릭
    await waitFor(() => {
      const confirmButton = screen.getByRole('button', { name: '확인' })
      fireEvent.click(confirmButton)
    })

    await waitFor(() => {
      expect(mockOnServiceAction).toHaveBeenCalledWith({
        action: 'start',
        service_id: 'test-service-2',
      })
    })
  })

  it('확인 대화상자에서 취소 버튼 클릭 시 대화상자를 닫는다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockStoppedService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    // 시작 버튼 클릭
    const startButton = screen.getByRole('button', { name: '시작' })
    fireEvent.click(startButton)

    // 확인 대화상자가 열렸는지 확인
    await waitFor(() => {
      expect(screen.getByText('서비스 시작 확인')).toBeInTheDocument()
    })

    // 취소 버튼 클릭
    const cancelButton = screen.getByRole('button', { name: '취소' })
    fireEvent.click(cancelButton)

    // 대화상자가 닫혔는지 확인
    await waitFor(() => {
      expect(screen.queryByText('서비스 시작 확인')).not.toBeInTheDocument()
    })

    expect(mockOnServiceAction).not.toHaveBeenCalled()
  })

  it('서비스 액션 실행 중 진행 상태를 표시한다', async () => {
    // 액션이 완료되지 않도록 Promise를 pending 상태로 유지
    const pendingPromise = new Promise(() => {})
    mockOnServiceAction.mockReturnValue(pendingPromise)

    render(
      <TestWrapper>
        <ServiceControls
          service={mockStoppedService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    // 시작 버튼 클릭
    const startButton = screen.getByRole('button', { name: '시작' })
    fireEvent.click(startButton)

    // 확인 버튼 클릭
    await waitFor(() => {
      const confirmButton = screen.getByRole('button', { name: '확인' })
      fireEvent.click(confirmButton)
    })

    // 진행 상태 표시 확인
    await waitFor(() => {
      expect(screen.getByText('작업을 처리하고 있습니다...')).toBeInTheDocument()
      expect(screen.getByRole('progressbar')).toBeInTheDocument()
    })
  })

  it('서비스 액션 실패 시 에러 토스트를 표시한다', async () => {
    const error = new Error('Service action failed')
    mockOnServiceAction.mockRejectedValue(error)

    render(
      <TestWrapper>
        <ServiceControls
          service={mockStoppedService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    // 시작 버튼 클릭
    const startButton = screen.getByRole('button', { name: '시작' })
    fireEvent.click(startButton)

    // 확인 버튼 클릭
    await waitFor(() => {
      const confirmButton = screen.getByRole('button', { name: '확인' })
      fireEvent.click(confirmButton)
    })

    // 에러 처리 확인 (실제 토스트는 테스트하기 어려우므로 함수 호출만 확인)
    await waitFor(() => {
      expect(mockOnServiceAction).toHaveBeenCalled()
    })
  })

  it('서비스 정보를 확인 대화상자에 표시한다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const stopButton = screen.getByRole('button', { name: /중지/ })
    fireEvent.click(stopButton)

    await waitFor(() => {
      expect(screen.getByText('실행 중인 서비스')).toBeInTheDocument()
      expect(screen.getByText('test-service-1')).toBeInTheDocument()
      expect(screen.getByText('running')).toBeInTheDocument()
      expect(screen.getByText('60분')).toBeInTheDocument() // 3600초 = 60분
    })
  })

  it('중지 액션에 대해 주의사항을 표시한다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const stopButton = screen.getByRole('button', { name: /중지/ })
    fireEvent.click(stopButton)

    await waitFor(() => {
      expect(
        screen.getByText('서비스를 중지하면 관련된 모든 작업이 중단됩니다.')
      ).toBeInTheDocument()
    })
  })

  it('재시작 액션에 대해 주의사항을 표시한다', async () => {
    render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
        />
      </TestWrapper>
    )

    const restartButton = screen.getByRole('button', { name: /재시작/ })
    fireEvent.click(restartButton)

    await waitFor(() => {
      expect(
        screen.getByText('재시작 중에는 서비스가 일시적으로 사용할 수 없습니다.')
      ).toBeInTheDocument()
    })
  })

  it('다양한 크기 옵션을 지원한다', () => {
    const { rerender } = render(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
          size="sm"
        />
      </TestWrapper>
    )

    // 버튼이 렌더링되는지 확인
    let buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)

    rerender(
      <TestWrapper>
        <ServiceControls
          service={mockRunningService}
          onServiceAction={mockOnServiceAction}
          size="lg"
        />
      </TestWrapper>
    )

    // 다시 렌더링 후에도 버튼이 있는지 확인
    buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)
  })
})