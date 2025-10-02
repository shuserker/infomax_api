import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { ServiceCard } from '../ServiceCard'
import { ServiceInfo } from '../../../types'
import theme from '../../../theme'

// 테스트용 래퍼 컴포넌트
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

// 테스트용 서비스 데이터
const mockService: ServiceInfo = {
  id: 'test-service-1',
  name: '테스트 서비스',
  description: '테스트용 서비스입니다',
  status: 'running',
  uptime: 3661, // 1시간 1분 1초
}

const mockServiceWithError: ServiceInfo = {
  id: 'error-service',
  name: '오류 서비스',
  description: '오류가 발생한 서비스입니다',
  status: 'error',
  uptime: 120,
  last_error: '연결 시간 초과: 서버에 연결할 수 없습니다',
  config: {
    port: 8080,
    timeout: 30,
    retries: 3,
  },
}

describe('ServiceCard', () => {
  it('서비스 기본 정보를 올바르게 렌더링한다', () => {
    render(
      <TestWrapper>
        <ServiceCard service={mockService} />
      </TestWrapper>
    )

    expect(screen.getByText('테스트 서비스')).toBeInTheDocument()
    expect(screen.getByText('테스트용 서비스입니다')).toBeInTheDocument()
    expect(screen.getByText('test-service-1')).toBeInTheDocument()
    expect(screen.getByText('실행 중')).toBeInTheDocument()
  })

  it('업타임을 올바른 형식으로 표시한다', () => {
    render(
      <TestWrapper>
        <ServiceCard service={mockService} />
      </TestWrapper>
    )

    expect(screen.getByText('1시간 1분')).toBeInTheDocument()
  })

  it('서비스 상태에 따라 올바른 배지를 표시한다', () => {
    const stoppedService = { ...mockService, status: 'stopped' as const }
    const { rerender } = render(
      <TestWrapper>
        <ServiceCard service={stoppedService} />
      </TestWrapper>
    )

    expect(screen.getByText('중지됨')).toBeInTheDocument()

    const errorService = { ...mockService, status: 'error' as const }
    rerender(
      <TestWrapper>
        <ServiceCard service={errorService} />
      </TestWrapper>
    )

    expect(screen.getByText('오류')).toBeInTheDocument()
  })

  it('오류 정보가 있을 때 오류 섹션을 표시한다', () => {
    render(
      <TestWrapper>
        <ServiceCard service={mockServiceWithError} />
      </TestWrapper>
    )

    expect(screen.getByText('마지막 오류:')).toBeInTheDocument()
    expect(
      screen.getByText('연결 시간 초과: 서버에 연결할 수 없습니다')
    ).toBeInTheDocument()
  })

  it('설정 정보가 있을 때 설정 섹션을 표시한다', () => {
    render(
      <TestWrapper>
        <ServiceCard service={mockServiceWithError} />
      </TestWrapper>
    )

    expect(screen.getByText('설정:')).toBeInTheDocument()
    expect(screen.getByText('port: 8080')).toBeInTheDocument()
    expect(screen.getByText('timeout: 30')).toBeInTheDocument()
    expect(screen.getByText('retries: 3')).toBeInTheDocument()
  })

  it('클릭 핸들러가 올바르게 호출된다', () => {
    const mockOnClick = vi.fn()
    render(
      <TestWrapper>
        <ServiceCard service={mockService} onClick={mockOnClick} />
      </TestWrapper>
    )

    const card = screen.getByRole('button')
    fireEvent.click(card)

    expect(mockOnClick).toHaveBeenCalledWith(mockService)
  })

  it('선택된 상태일 때 다른 스타일을 적용한다', () => {
    const { container } = render(
      <TestWrapper>
        <ServiceCard service={mockService} isSelected={true} />
      </TestWrapper>
    )

    const card = container.querySelector('[data-testid="service-card"]')
    expect(card).toHaveStyle({ borderColor: expect.any(String) })
  })

  it('업타임이 없을 때 "알 수 없음"을 표시한다', () => {
    const serviceWithoutUptime = { ...mockService, uptime: undefined }
    render(
      <TestWrapper>
        <ServiceCard service={serviceWithoutUptime} />
      </TestWrapper>
    )

    expect(screen.getByText('알 수 없음')).toBeInTheDocument()
  })

  it('짧은 업타임을 올바르게 포맷한다', () => {
    const shortUptimeService = { ...mockService, uptime: 45 }
    render(
      <TestWrapper>
        <ServiceCard service={shortUptimeService} />
      </TestWrapper>
    )

    expect(screen.getByText('45초')).toBeInTheDocument()
  })

  it('분 단위 업타임을 올바르게 포맷한다', () => {
    const minuteUptimeService = { ...mockService, uptime: 150 } // 2분 30초
    render(
      <TestWrapper>
        <ServiceCard service={minuteUptimeService} />
      </TestWrapper>
    )

    expect(screen.getByText('2분 30초')).toBeInTheDocument()
  })

  it('설정이 3개 이상일 때 "더 보기" 메시지를 표시한다', () => {
    const serviceWithManyConfigs = {
      ...mockService,
      config: {
        port: 8080,
        timeout: 30,
        retries: 3,
        maxConnections: 100,
        bufferSize: 1024,
      },
    }

    render(
      <TestWrapper>
        <ServiceCard service={serviceWithManyConfigs} />
      </TestWrapper>
    )

    expect(screen.getByText('... 및 2개 더')).toBeInTheDocument()
  })

  it('시작 중 상태를 올바르게 표시한다', () => {
    const startingService = { ...mockService, status: 'starting' as const }
    render(
      <TestWrapper>
        <ServiceCard service={startingService} />
      </TestWrapper>
    )

    expect(screen.getByText('시작 중')).toBeInTheDocument()
  })

  it('중지 중 상태를 올바르게 표시한다', () => {
    const stoppingService = { ...mockService, status: 'stopping' as const }
    render(
      <TestWrapper>
        <ServiceCard service={stoppingService} />
      </TestWrapper>
    )

    expect(screen.getByText('중지 중')).toBeInTheDocument()
  })

  it('onClick이 없을 때 클릭할 수 없다', () => {
    const { container } = render(
      <TestWrapper>
        <ServiceCard service={mockService} />
      </TestWrapper>
    )

    const card = container.firstChild as HTMLElement
    expect(card).toHaveStyle({ cursor: 'default' })
  })

  it('onClick이 있을 때 클릭할 수 있다', () => {
    const mockOnClick = vi.fn()
    const { container } = render(
      <TestWrapper>
        <ServiceCard service={mockService} onClick={mockOnClick} />
      </TestWrapper>
    )

    const card = container.firstChild as HTMLElement
    expect(card).toHaveStyle({ cursor: 'pointer' })
  })
})