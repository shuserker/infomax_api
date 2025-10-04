import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { renderHook, act } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { useCustomToast, ToastProvider } from '../Toast'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>
    <ToastProvider>{children}</ToastProvider>
  </ChakraProvider>
)

// useToast 모킹
const mockToast = vi.fn()
vi.mock('@chakra-ui/react', async () => {
  const actual = await vi.importActual('@chakra-ui/react')
  return {
    ...actual,
    useToast: () => mockToast,
  }
})

describe('useCustomToast 훅', () => {
  beforeEach(() => {
    mockToast.mockClear()
  })

  it('기본 토스트가 올바른 옵션으로 호출된다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    act(() => {
      result.current.showToast({
        title: '테스트 메시지',
        description: '테스트 설명',
      })
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: '테스트 메시지',
      description: '테스트 설명',
      duration: 5000,
      isClosable: true,
      position: 'top-right',
      status: 'info',
    })
  })

  it('성공 토스트가 올바르게 호출된다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    act(() => {
      result.current.showSuccess('성공 메시지', '성공 설명')
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: '성공 메시지',
      description: '성공 설명',
      status: 'success',
      duration: 5000,
      isClosable: true,
      position: 'top-right',
    })
  })

  it('에러 토스트가 더 긴 지속시간으로 호출된다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    act(() => {
      result.current.showError('에러 메시지', '에러 설명')
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: '에러 메시지',
      description: '에러 설명',
      status: 'error',
      duration: 8000, // 에러는 더 오래 표시
      isClosable: true,
      position: 'top-right',
    })
  })

  it('경고 토스트가 올바르게 호출된다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    act(() => {
      result.current.showWarning('경고 메시지', '경고 설명')
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: '경고 메시지',
      description: '경고 설명',
      status: 'warning',
      duration: 5000,
      isClosable: true,
      position: 'top-right',
    })
  })

  it('정보 토스트가 올바르게 호출된다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    act(() => {
      result.current.showInfo('정보 메시지', '정보 설명')
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: '정보 메시지',
      description: '정보 설명',
      status: 'info',
      duration: 5000,
      isClosable: true,
      position: 'top-right',
    })
  })

  it('커스텀 옵션이 기본값을 덮어쓴다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    act(() => {
      result.current.showToast({
        title: '커스텀 토스트',
        status: 'success',
        duration: 3000,
        position: 'bottom-left',
        isClosable: false,
      })
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: '커스텀 토스트',
      status: 'success',
      duration: 3000,
      position: 'bottom-left',
      isClosable: false,
    })
  })

  it('설명 없이 제목만으로 토스트를 호출할 수 있다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    act(() => {
      result.current.showSuccess('제목만 있는 토스트')
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: '제목만 있는 토스트',
      description: undefined,
      status: 'success',
      duration: 5000,
      isClosable: true,
      position: 'top-right',
    })
  })

  it('모든 토스트 타입이 올바른 반환값을 가진다', () => {
    const { result } = renderHook(() => useCustomToast(), {
      wrapper: TestWrapper,
    })

    // 모든 함수가 존재하는지 확인
    expect(typeof result.current.showToast).toBe('function')
    expect(typeof result.current.showSuccess).toBe('function')
    expect(typeof result.current.showError).toBe('function')
    expect(typeof result.current.showWarning).toBe('function')
    expect(typeof result.current.showInfo).toBe('function')
  })
})

describe('ToastProvider 컴포넌트', () => {
  it('자식 컴포넌트를 올바르게 렌더링한다', () => {
    const TestChild = () => <div>테스트 자식</div>
    
    const { container } = render(
      <TestWrapper>
        <ToastProvider>
          <TestChild />
        </ToastProvider>
      </TestWrapper>
    )

    expect(container.textContent).toContain('테스트 자식')
  })
})