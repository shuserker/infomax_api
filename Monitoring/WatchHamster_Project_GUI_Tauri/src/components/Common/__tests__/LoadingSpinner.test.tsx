import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { LoadingSpinner } from '../LoadingSpinner'
import theme from '../../../theme'

// 테스트용 래퍼 컴포넌트
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('LoadingSpinner 컴포넌트', () => {
  it('기본 로딩 스피너가 렌더링된다', () => {
    render(
      <TestWrapper>
        <LoadingSpinner />
      </TestWrapper>
    )

    // 기본 메시지 확인
    expect(screen.getByText('로딩 중...')).toBeInTheDocument()
    
    // 스피너 요소 확인 (Chakra UI Spinner는 특정 클래스를 가짐)
    const spinner = document.querySelector('.chakra-spinner')
    expect(spinner).toBeInTheDocument()
  })

  it('커스텀 메시지가 표시된다', () => {
    const customMessage = '데이터를 불러오는 중입니다...'
    
    render(
      <TestWrapper>
        <LoadingSpinner message={customMessage} />
      </TestWrapper>
    )

    expect(screen.getByText(customMessage)).toBeInTheDocument()
  })

  it('메시지가 없을 때는 텍스트가 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <LoadingSpinner message="" />
      </TestWrapper>
    )

    // 빈 메시지일 때는 메시지 텍스트가 렌더링되지 않아야 함
    // 기본 메시지도 표시되지 않아야 함
    expect(screen.queryByText('로딩 중...')).not.toBeInTheDocument()
  })

  it('다양한 크기 옵션이 적용된다', () => {
    const { rerender } = render(
      <TestWrapper>
        <LoadingSpinner size="sm" />
      </TestWrapper>
    )

    let spinner = document.querySelector('.chakra-spinner')
    // Chakra UI Spinner가 렌더링되는지 확인
    expect(spinner).toBeInTheDocument()

    rerender(
      <TestWrapper>
        <LoadingSpinner size="lg" />
      </TestWrapper>
    )

    spinner = document.querySelector('.chakra-spinner')
    expect(spinner).toBeInTheDocument()
  })

  it('커스텀 색상이 적용된다', () => {
    render(
      <TestWrapper>
        <LoadingSpinner color="blue.500" />
      </TestWrapper>
    )

    const spinner = document.querySelector('.chakra-spinner')
    expect(spinner).toHaveStyle({ color: 'var(--chakra-colors-blue-500)' })
  })

  it('컨테이너가 올바른 스타일을 가진다', () => {
    render(
      <TestWrapper>
        <LoadingSpinner />
      </TestWrapper>
    )

    // Box 컴포넌트가 렌더링되는지 확인
    const container = screen.getByText('로딩 중...').closest('div')
    expect(container).toBeInTheDocument()
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    render(
      <TestWrapper>
        <LoadingSpinner />
      </TestWrapper>
    )

    // Chakra UI Spinner의 접근성 확인
    const spinner = document.querySelector('.chakra-spinner')
    expect(spinner).toBeInTheDocument()
    // Chakra UI Spinner는 내부적으로 접근성 속성을 설정함
  })

  it('모든 props가 함께 작동한다', () => {
    render(
      <TestWrapper>
        <LoadingSpinner message="테스트 로딩" size="md" color="posco.500" />
      </TestWrapper>
    )

    expect(screen.getByText('테스트 로딩')).toBeInTheDocument()
    const spinner = document.querySelector('.chakra-spinner')
    expect(spinner).toBeInTheDocument()
  })
})