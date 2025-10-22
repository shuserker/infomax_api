import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { renderHook, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import { ConfirmDialog, useConfirmDialog } from '../ConfirmDialog'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('ConfirmDialog 컴포넌트', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn(),
    message: '정말로 삭제하시겠습니까?',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('기본 확인 대화상자가 렌더링된다', () => {
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} />
      </TestWrapper>
    )

    expect(screen.getByRole('heading', { name: '확인' })).toBeInTheDocument() // 기본 제목
    expect(screen.getByText('정말로 삭제하시겠습니까?')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '확인' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '취소' })).toBeInTheDocument()
  })

  it('커스텀 제목과 버튼 텍스트가 표시된다', () => {
    render(
      <TestWrapper>
        <ConfirmDialog
          {...defaultProps}
          title="서비스 중지"
          confirmText="중지"
          cancelText="돌아가기"
        />
      </TestWrapper>
    )

    expect(screen.getByText('서비스 중지')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '중지' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '돌아가기' })).toBeInTheDocument()
  })

  it('확인 버튼 클릭 시 onConfirm과 onClose가 호출된다', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} />
      </TestWrapper>
    )

    const confirmButton = screen.getByRole('button', { name: '확인' })
    await user.click(confirmButton)

    expect(defaultProps.onConfirm).toHaveBeenCalledTimes(1)
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
  })

  it('취소 버튼 클릭 시 onClose만 호출된다', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} />
      </TestWrapper>
    )

    const cancelButton = screen.getByRole('button', { name: '취소' })
    await user.click(cancelButton)

    expect(defaultProps.onConfirm).not.toHaveBeenCalled()
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
  })

  it('로딩 상태일 때 버튼이 비활성화된다', () => {
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} isLoading={true} />
      </TestWrapper>
    )

    const confirmButton = screen.getByRole('button', { name: /처리 중/ })
    const cancelButton = screen.getByRole('button', { name: '취소' })

    expect(confirmButton).toBeDisabled()
    expect(cancelButton).toBeDisabled()
  })

  it('커스텀 색상 스키마가 적용된다', () => {
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} confirmColorScheme="blue" />
      </TestWrapper>
    )

    const confirmButton = screen.getByRole('button', { name: '확인' })
    // Chakra UI는 colorScheme을 CSS 클래스로 적용하므로 클래스 확인
    expect(confirmButton).toHaveClass(/blue/)
  })

  it('ESC 키로 대화상자를 닫을 수 있다', async () => {
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} />
      </TestWrapper>
    )

    await user.keyboard('{Escape}')

    expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
  })

  it('대화상자가 닫혀있을 때는 렌더링되지 않는다', () => {
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} isOpen={false} />
      </TestWrapper>
    )

    expect(screen.queryByText('정말로 삭제하시겠습니까?')).not.toBeInTheDocument()
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    render(
      <TestWrapper>
        <ConfirmDialog {...defaultProps} />
      </TestWrapper>
    )

    const dialog = screen.getByRole('alertdialog')
    expect(dialog).toBeInTheDocument()
    expect(dialog).toHaveAttribute('aria-labelledby')
    expect(dialog).toHaveAttribute('aria-describedby')
  })
})

describe('useConfirmDialog 훅', () => {
  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() => useConfirmDialog())

    expect(result.current.isOpen).toBe(false)
    expect(result.current.dialogProps).toEqual({})
    expect(typeof result.current.onOpen).toBe('function')
    expect(typeof result.current.onClose).toBe('function')
  })

  it('대화상자를 열 때 props가 설정된다', () => {
    const { result } = renderHook(() => useConfirmDialog())

    const testProps = {
      title: '테스트 제목',
      message: '테스트 메시지',
      confirmText: '확인',
    }

    act(() => {
      result.current.onOpen(testProps)
    })

    expect(result.current.isOpen).toBe(true)
    expect(result.current.dialogProps).toEqual(testProps)
  })

  it('대화상자를 닫을 때 상태가 초기화된다', () => {
    const { result } = renderHook(() => useConfirmDialog())

    // 먼저 열기
    act(() => {
      result.current.onOpen({
        title: '테스트 제목',
        message: '테스트 메시지',
      })
    })

    expect(result.current.isOpen).toBe(true)

    // 닫기
    act(() => {
      result.current.onClose()
    })

    expect(result.current.isOpen).toBe(false)
    expect(result.current.dialogProps).toEqual({})
  })

  it('여러 번 열고 닫기를 반복할 수 있다', () => {
    const { result } = renderHook(() => useConfirmDialog())

    // 첫 번째 열기
    act(() => {
      result.current.onOpen({ message: '첫 번째 메시지' })
    })
    expect(result.current.isOpen).toBe(true)

    // 닫기
    act(() => {
      result.current.onClose()
    })
    expect(result.current.isOpen).toBe(false)

    // 두 번째 열기
    act(() => {
      result.current.onOpen({ message: '두 번째 메시지' })
    })
    expect(result.current.isOpen).toBe(true)
    expect(result.current.dialogProps.message).toBe('두 번째 메시지')
  })

  it('다른 props로 대화상자를 다시 열 수 있다', () => {
    const { result } = renderHook(() => useConfirmDialog())

    // 첫 번째 props로 열기
    act(() => {
      result.current.onOpen({
        title: '첫 번째 제목',
        message: '첫 번째 메시지',
      })
    })

    expect(result.current.dialogProps.title).toBe('첫 번째 제목')

    // 다른 props로 다시 열기
    act(() => {
      result.current.onOpen({
        title: '두 번째 제목',
        message: '두 번째 메시지',
        confirmColorScheme: 'blue',
      })
    })

    expect(result.current.dialogProps.title).toBe('두 번째 제목')
    expect(result.current.dialogProps.confirmColorScheme).toBe('blue')
  })
})

// 통합 테스트
describe('ConfirmDialog 통합 테스트', () => {
  it('훅과 컴포넌트가 함께 올바르게 작동한다', async () => {
    const TestComponent = () => {
      const { isOpen, onOpen, onClose, dialogProps } = useConfirmDialog()
      const [result, setResult] = React.useState('')

      const handleDelete = () => {
        onOpen({
          title: '삭제 확인',
          message: '정말로 삭제하시겠습니까?',
          confirmText: '삭제',
          onConfirm: () => setResult('삭제됨'),
        })
      }

      return (
        <div>
          <button onClick={handleDelete}>삭제</button>
          <div data-testid="result">{result}</div>
          <ConfirmDialog
            isOpen={isOpen}
            onClose={onClose}
            onConfirm={dialogProps.onConfirm || (() => {})}
            title={dialogProps.title}
            message={dialogProps.message || ''}
            confirmText={dialogProps.confirmText}
          />
        </div>
      )
    }

    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    )

    // 삭제 버튼 클릭
    await user.click(screen.getByText('삭제'))

    // 대화상자가 열렸는지 확인
    expect(screen.getByText('삭제 확인')).toBeInTheDocument()
    expect(screen.getByText('정말로 삭제하시겠습니까?')).toBeInTheDocument()

    // 확인 버튼 클릭
    await user.click(screen.getByRole('button', { name: '삭제' }))

    // 결과 확인
    await waitFor(() => {
      expect(screen.getByTestId('result')).toHaveTextContent('삭제됨')
    })

    // 대화상자가 닫혔는지 확인 (약간의 지연 후)
    await waitFor(() => {
      expect(screen.queryByText('삭제 확인')).not.toBeInTheDocument()
    })
  })
})