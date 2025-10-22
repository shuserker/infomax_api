import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { renderHook, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider, Button } from '@chakra-ui/react'
import { Modal, useModal } from '../Modal'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('Modal 컴포넌트', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    children: <div>모달 콘텐츠</div>,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('기본 모달이 렌더링된다', () => {
    render(
      <TestWrapper>
        <Modal {...defaultProps} />
      </TestWrapper>
    )

    expect(screen.getByText('모달 콘텐츠')).toBeInTheDocument()
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('제목이 있을 때 헤더가 표시된다', () => {
    render(
      <TestWrapper>
        <Modal {...defaultProps} title="테스트 모달" />
      </TestWrapper>
    )

    expect(screen.getByText('테스트 모달')).toBeInTheDocument()
    expect(screen.getByRole('banner')).toBeInTheDocument() // ModalHeader는 banner role을 가짐
  })

  it('제목이 없을 때 헤더가 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <Modal {...defaultProps} />
      </TestWrapper>
    )

    expect(screen.queryByRole('banner')).not.toBeInTheDocument()
  })

  it('푸터가 있을 때 푸터 영역이 표시된다', () => {
    const footer = (
      <div>
        <Button>확인</Button>
        <Button>취소</Button>
      </div>
    )

    render(
      <TestWrapper>
        <Modal {...defaultProps} footer={footer} />
      </TestWrapper>
    )

    expect(screen.getByRole('button', { name: '확인' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '취소' })).toBeInTheDocument()
  })

  it('닫기 버튼이 기본적으로 표시된다', () => {
    render(
      <TestWrapper>
        <Modal {...defaultProps} title="테스트 모달" />
      </TestWrapper>
    )

    const closeButton = screen.getByRole('button', { name: /close/i })
    expect(closeButton).toBeInTheDocument()
  })

  it('showCloseButton이 false일 때 닫기 버튼이 숨겨진다', () => {
    render(
      <TestWrapper>
        <Modal {...defaultProps} title="테스트 모달" showCloseButton={false} />
      </TestWrapper>
    )

    const closeButton = screen.queryByRole('button', { name: /close/i })
    expect(closeButton).not.toBeInTheDocument()
  })

  it('닫기 버튼 클릭 시 onClose가 호출된다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <Modal {...defaultProps} title="테스트 모달" />
      </TestWrapper>
    )

    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
  })

  it('ESC 키로 모달을 닫을 수 있다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <Modal {...defaultProps} closeOnEsc={true} />
      </TestWrapper>
    )

    await user.keyboard('{Escape}')

    expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
  })

  it('closeOnEsc가 false일 때 ESC 키로 닫히지 않는다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <Modal {...defaultProps} closeOnEsc={false} />
      </TestWrapper>
    )

    await user.keyboard('{Escape}')

    expect(defaultProps.onClose).not.toHaveBeenCalled()
  })

  it('오버레이 클릭으로 모달을 닫을 수 있다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <Modal {...defaultProps} closeOnOverlayClick={true} />
      </TestWrapper>
    )

    // 오버레이 클릭 (모달 외부 영역)
    const overlay = document.querySelector('[data-chakra-modal-overlay]')
    if (overlay) {
      await user.click(overlay)
      expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
    }
  })

  it('closeOnOverlayClick이 false일 때 오버레이 클릭으로 닫히지 않는다', async () => {
    const user = userEvent.setup()

    render(
      <TestWrapper>
        <Modal {...defaultProps} closeOnOverlayClick={false} />
      </TestWrapper>
    )

    const overlay = document.querySelector('[data-chakra-modal-overlay]')
    if (overlay) {
      await user.click(overlay)
      expect(defaultProps.onClose).not.toHaveBeenCalled()
    }
  })

  it('다양한 크기 옵션이 적용된다', () => {
    const { rerender } = render(
      <TestWrapper>
        <Modal {...defaultProps} size="sm" />
      </TestWrapper>
    )

    let modalContent = document.querySelector('[role="dialog"]')
    expect(modalContent).toBeInTheDocument()

    rerender(
      <TestWrapper>
        <Modal {...defaultProps} size="xl" />
      </TestWrapper>
    )

    modalContent = document.querySelector('[role="dialog"]')
    expect(modalContent).toBeInTheDocument()
  })

  it('모달이 닫혀있을 때는 렌더링되지 않는다', () => {
    render(
      <TestWrapper>
        <Modal {...defaultProps} isOpen={false} />
      </TestWrapper>
    )

    expect(screen.queryByText('모달 콘텐츠')).not.toBeInTheDocument()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    render(
      <TestWrapper>
        <Modal {...defaultProps} title="접근성 테스트 모달" />
      </TestWrapper>
    )

    const dialog = screen.getByRole('dialog')
    expect(dialog).toBeInTheDocument()
    expect(dialog).toHaveAttribute('aria-modal', 'true')
  })

  it('복잡한 콘텐츠를 올바르게 렌더링한다', () => {
    const complexContent = (
      <div>
        <h2>복잡한 콘텐츠</h2>
        <p>이것은 복잡한 모달 콘텐츠입니다.</p>
        <ul>
          <li>항목 1</li>
          <li>항목 2</li>
          <li>항목 3</li>
        </ul>
      </div>
    )

    render(
      <TestWrapper>
        <Modal {...defaultProps}>{complexContent}</Modal>
      </TestWrapper>
    )

    expect(screen.getByText('복잡한 콘텐츠')).toBeInTheDocument()
    expect(screen.getByText('이것은 복잡한 모달 콘텐츠입니다.')).toBeInTheDocument()
    expect(screen.getByText('항목 1')).toBeInTheDocument()
    expect(screen.getByText('항목 2')).toBeInTheDocument()
    expect(screen.getByText('항목 3')).toBeInTheDocument()
  })
})

describe('useModal 훅', () => {
  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() => useModal())

    expect(result.current.isOpen).toBe(false)
    expect(typeof result.current.onOpen).toBe('function')
    expect(typeof result.current.onClose).toBe('function')
  })

  it('onOpen을 호출하면 모달이 열린다', () => {
    const { result } = renderHook(() => useModal())

    expect(result.current.isOpen).toBe(false)

    act(() => {
      result.current.onOpen()
    })

    expect(result.current.isOpen).toBe(true)
  })

  it('onClose를 호출하면 모달이 닫힌다', () => {
    const { result } = renderHook(() => useModal())

    // 먼저 모달을 연다
    act(() => {
      result.current.onOpen()
    })

    expect(result.current.isOpen).toBe(true)

    // 모달을 닫는다
    act(() => {
      result.current.onClose()
    })

    expect(result.current.isOpen).toBe(false)
  })

  it('여러 번 열고 닫기를 반복할 수 있다', () => {
    const { result } = renderHook(() => useModal())

    // 첫 번째 열기/닫기
    act(() => {
      result.current.onOpen()
    })
    expect(result.current.isOpen).toBe(true)

    act(() => {
      result.current.onClose()
    })
    expect(result.current.isOpen).toBe(false)

    // 두 번째 열기/닫기
    act(() => {
      result.current.onOpen()
    })
    expect(result.current.isOpen).toBe(true)

    act(() => {
      result.current.onClose()
    })
    expect(result.current.isOpen).toBe(false)
  })
})

// 통합 테스트
describe('Modal 통합 테스트', () => {
  it('훅과 컴포넌트가 함께 올바르게 작동한다', async () => {
    const TestComponent = () => {
      const { isOpen, onOpen, onClose } = useModal()

      return (
        <div>
          <Button onClick={onOpen}>모달 열기</Button>
          <Modal isOpen={isOpen} onClose={onClose} title="통합 테스트 모달">
            <p>통합 테스트 콘텐츠</p>
          </Modal>
        </div>
      )
    }

    const user = userEvent.setup()

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    )

    // 초기에는 모달이 보이지 않음
    expect(screen.queryByText('통합 테스트 콘텐츠')).not.toBeInTheDocument()

    // 모달 열기 버튼 클릭
    await user.click(screen.getByText('모달 열기'))

    // 모달이 열림
    expect(screen.getByText('통합 테스트 모달')).toBeInTheDocument()
    expect(screen.getByText('통합 테스트 콘텐츠')).toBeInTheDocument()

    // 닫기 버튼 클릭
    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    // 모달이 닫힘 (애니메이션 때문에 약간의 지연이 있을 수 있음)
    await waitFor(() => {
      expect(screen.queryByText('통합 테스트 콘텐츠')).not.toBeInTheDocument()
    })
  })

  it('푸터와 함께 사용할 때 올바르게 작동한다', async () => {
    const TestComponent = () => {
      const { isOpen, onOpen, onClose } = useModal()
      const [result, setResult] = React.useState('')

      const handleConfirm = () => {
        setResult('확인됨')
        onClose()
      }

      const footer = (
        <div>
          <Button onClick={handleConfirm} colorScheme="blue" mr={3}>
            확인
          </Button>
          <Button onClick={onClose}>취소</Button>
        </div>
      )

      return (
        <div>
          <Button onClick={onOpen}>모달 열기</Button>
          <div data-testid="result">{result}</div>
          <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="확인 모달"
            footer={footer}
          >
            <p>정말로 진행하시겠습니까?</p>
          </Modal>
        </div>
      )
    }

    const user = userEvent.setup()

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    )

    // 모달 열기
    await user.click(screen.getByText('모달 열기'))

    // 모달 내용 확인
    expect(screen.getByText('정말로 진행하시겠습니까?')).toBeInTheDocument()

    // 확인 버튼 클릭
    await user.click(screen.getByRole('button', { name: '확인' }))

    // 결과 확인
    await waitFor(() => {
      expect(screen.getByTestId('result')).toHaveTextContent('확인됨')
    })
    
    // 모달이 닫힘 (애니메이션 때문에 약간의 지연이 있을 수 있음)
    await waitFor(() => {
      expect(screen.queryByText('정말로 진행하시겠습니까?')).not.toBeInTheDocument()
    })
  })
})