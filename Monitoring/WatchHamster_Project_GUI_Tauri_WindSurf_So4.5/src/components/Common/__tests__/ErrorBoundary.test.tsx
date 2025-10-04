import { render, screen } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { describe, it, expect, vi } from 'vitest'
import ErrorBoundary from '../ErrorBoundary'

// 에러를 발생시키는 테스트 컴포넌트
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('테스트 에러')
  }
  return <div>정상 컴포넌트</div>
}

const renderWithChakra = (component: React.ReactElement) => {
  return render(
    <ChakraProvider>
      {component}
    </ChakraProvider>
  )
}

describe('ErrorBoundary', () => {
  // 콘솔 에러 억제
  const originalConsoleError = console.error
  beforeEach(() => {
    console.error = vi.fn()
  })

  afterEach(() => {
    console.error = originalConsoleError
  })

  it('정상적인 컴포넌트를 렌더링한다', () => {
    renderWithChakra(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    )

    expect(screen.getByText('정상 컴포넌트')).toBeInTheDocument()
  })

  it('에러가 발생하면 에러 UI를 표시한다', () => {
    renderWithChakra(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('문제가 발생했습니다')).toBeInTheDocument()
    expect(screen.getByText('페이지를 새로고침하거나 잠시 후 다시 시도해주세요.')).toBeInTheDocument()
  })

  it('새로고침 버튼이 표시된다', () => {
    renderWithChakra(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    const refreshButton = screen.getByRole('button', { name: /페이지 새로고침/i })
    expect(refreshButton).toBeInTheDocument()
  })

  it('에러 세부사항 토글 버튼이 표시된다', () => {
    renderWithChakra(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    const detailsButton = screen.getByRole('button', { name: /에러 세부사항/i })
    expect(detailsButton).toBeInTheDocument()
  })
})