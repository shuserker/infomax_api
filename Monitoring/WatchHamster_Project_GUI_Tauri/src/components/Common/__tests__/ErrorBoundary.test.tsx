import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import ErrorBoundary from '../ErrorBoundary'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

// 에러를 발생시키는 테스트 컴포넌트
const ThrowError: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = false }) => {
  if (shouldThrow) {
    throw new Error('테스트 에러입니다')
  }
  return <div>정상 컴포넌트</div>
}

// 콘솔 에러 모킹
const originalError = console.error
beforeEach(() => {
  console.error = vi.fn()
})

afterEach(() => {
  console.error = originalError
})

describe('ErrorBoundary 컴포넌트', () => {
  it('에러가 없을 때 자식 컴포넌트를 정상적으로 렌더링한다', () => {
    render(
      <TestWrapper>
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      </TestWrapper>
    )

    expect(screen.getByText('정상 컴포넌트')).toBeInTheDocument()
  })

  it('에러가 발생했을 때 에러 UI를 표시한다', () => {
    render(
      <TestWrapper>
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      </TestWrapper>
    )

    expect(screen.getByText('오류가 발생했습니다!')).toBeInTheDocument()
    expect(screen.getByText('애플리케이션에서 예상치 못한 오류가 발생했습니다.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '다시 시도' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '오류 정보 보기' })).toBeInTheDocument()
  })

  it('커스텀 fallback UI를 사용할 수 있다', () => {
    const customFallback = <div>커스텀 에러 UI</div>

    render(
      <TestWrapper>
        <ErrorBoundary fallback={customFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      </TestWrapper>
    )

    expect(screen.getByText('커스텀 에러 UI')).toBeInTheDocument()
    expect(screen.queryByText('오류가 발생했습니다!')).not.toBeInTheDocument()
  })

  it('다시 시도 버튼을 클릭하면 에러 상태가 초기화된다', async () => {
    const user = userEvent.setup()
    let shouldThrow = true

    const TestComponent = () => {
      const [throwError, setThrowError] = React.useState(shouldThrow)
      
      React.useEffect(() => {
        shouldThrow = throwError
      }, [throwError])

      return (
        <TestWrapper>
          <button onClick={() => setThrowError(false)}>에러 해결</button>
          <ErrorBoundary>
            <ThrowError shouldThrow={throwError} />
          </ErrorBoundary>
        </TestWrapper>
      )
    }

    render(<TestComponent />)

    // 에러 UI가 표시되는지 확인
    expect(screen.getByText('오류가 발생했습니다!')).toBeInTheDocument()

    // 에러를 해결하고 다시 시도
    await user.click(screen.getByText('에러 해결'))
    await user.click(screen.getByRole('button', { name: '다시 시도' }))

    // 정상 컴포넌트가 다시 렌더링되는지 확인
    expect(screen.queryByText('오류가 발생했습니다!')).not.toBeInTheDocument()
  })

  it('오류 정보 보기 버튼을 클릭하면 상세 정보가 표시된다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      </TestWrapper>
    )

    // 오류 정보 보기 클릭
    await user.click(screen.getByRole('button', { name: '오류 정보 보기' }))

    // 오류 정보가 표시됨
    expect(screen.getByText('오류 메시지:')).toBeInTheDocument()
    expect(screen.getByText('테스트 에러입니다')).toBeInTheDocument()
    expect(screen.getByText('스택 트레이스:')).toBeInTheDocument()

    // 버튼 텍스트가 변경됨
    expect(screen.getByRole('button', { name: '오류 정보 숨기기' })).toBeInTheDocument()
  })

  it('오류 정보 숨기기 버튼을 클릭하면 상세 정보가 숨겨진다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      </TestWrapper>
    )

    // 오류 정보 보기
    await user.click(screen.getByRole('button', { name: '오류 정보 보기' }))
    expect(screen.getByText('오류 메시지:')).toBeInTheDocument()

    // 오류 정보 숨기기
    await user.click(screen.getByRole('button', { name: '오류 정보 숨기기' }))
    
    // 버튼 텍스트가 다시 변경되었는지 확인
    expect(screen.getByRole('button', { name: '오류 정보 보기' })).toBeInTheDocument()
  })

  it('componentDidCatch에서 에러를 콘솔에 로그한다', () => {
    render(
      <TestWrapper>
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      </TestWrapper>
    )

    expect(console.error).toHaveBeenCalledWith(
      'ErrorBoundary caught an error:',
      expect.any(Error),
      expect.any(Object)
    )
  })

  it('에러 메시지와 스택 트레이스가 올바르게 표시된다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      </TestWrapper>
    )

    await user.click(screen.getByRole('button', { name: '오류 정보 보기' }))

    // 에러 메시지 확인
    expect(screen.getByText('테스트 에러입니다')).toBeInTheDocument()
    
    // 스택 트레이스 섹션 확인
    expect(screen.getByText('스택 트레이스:')).toBeInTheDocument()
    
    // 컴포넌트 스택 섹션 확인 (있는 경우)
    const componentStackElement = screen.queryByText('컴포넌트 스택:')
    if (componentStackElement) {
      expect(componentStackElement).toBeInTheDocument()
    }
  })

  it('여러 번 에러가 발생해도 올바르게 처리한다', async () => {
    const user = userEvent.setup()
    
    const MultiErrorComponent = () => {
      const [errorCount, setErrorCount] = React.useState(0)
      
      if (errorCount > 0) {
        throw new Error(`에러 ${errorCount}번째`)
      }
      
      return (
        <button onClick={() => setErrorCount(1)}>
          에러 발생시키기
        </button>
      )
    }

    render(
      <TestWrapper>
        <ErrorBoundary>
          <MultiErrorComponent />
        </ErrorBoundary>
      </TestWrapper>
    )

    // 첫 번째 에러 발생
    await user.click(screen.getByText('에러 발생시키기'))
    expect(screen.getByText('오류가 발생했습니다!')).toBeInTheDocument()

    // 다시 시도
    await user.click(screen.getByRole('button', { name: '다시 시도' }))
    
    // 에러 상태가 초기화되어야 함
    expect(screen.queryByText('오류가 발생했습니다!')).not.toBeInTheDocument()
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    render(
      <TestWrapper>
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      </TestWrapper>
    )

    // Alert 컴포넌트의 role 확인
    const alert = screen.getByRole('alert')
    expect(alert).toBeInTheDocument()
    
    // 버튼들의 접근성 확인
    expect(screen.getByRole('button', { name: '다시 시도' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '오류 정보 보기' })).toBeInTheDocument()
  })
})