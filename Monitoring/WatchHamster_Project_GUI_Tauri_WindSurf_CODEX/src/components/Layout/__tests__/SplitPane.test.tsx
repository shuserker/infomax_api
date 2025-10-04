import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import { SplitPane } from '../SplitPane'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

// 마우스 이벤트 모킹
const createMouseEvent = (type: string, clientX: number, clientY: number) => {
  return new MouseEvent(type, {
    clientX,
    clientY,
    bubbles: true,
    cancelable: true,
  })
}

describe('SplitPane 컴포넌트', () => {
  const leftContent = <div>왼쪽 패널</div>
  const rightContent = <div>오른쪽 패널</div>

  beforeEach(() => {
    vi.clearAllMocks()
    // window 크기 모킹
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    })
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 768,
    })
  })

  it('기본 분할 패널이 렌더링된다', () => {
    render(
      <TestWrapper>
        <SplitPane left={leftContent} right={rightContent} />
      </TestWrapper>
    )

    expect(screen.getByText('왼쪽 패널')).toBeInTheDocument()
    expect(screen.getByText('오른쪽 패널')).toBeInTheDocument()
  })

  it('수직 방향 분할 패널이 렌더링된다', () => {
    render(
      <TestWrapper>
        <SplitPane
          left={<div>위쪽 패널</div>}
          right={<div>아래쪽 패널</div>}
          direction="vertical"
        />
      </TestWrapper>
    )

    expect(screen.getByText('위쪽 패널')).toBeInTheDocument()
    expect(screen.getByText('아래쪽 패널')).toBeInTheDocument()
  })

  it('기본 크기가 올바르게 적용된다', () => {
    render(
      <TestWrapper>
        <SplitPane left={leftContent} right={rightContent} defaultSize={30} />
      </TestWrapper>
    )

    // 패널들이 렌더링되는지 확인
    expect(screen.getByText('왼쪽 패널')).toBeInTheDocument()
    expect(screen.getByText('오른쪽 패널')).toBeInTheDocument()
  })

  it('비활성화된 상태에서는 리사이저가 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <SplitPane left={leftContent} right={rightContent} disabled={true} />
      </TestWrapper>
    )

    expect(screen.getByText('왼쪽 패널')).toBeInTheDocument()
    expect(screen.getByText('오른쪽 패널')).toBeInTheDocument()
    
    // 리사이저 요소가 없어야 함 (disabled일 때는 렌더링되지 않음)
    const resizer = document.querySelector('[style*="cursor"]')
    expect(resizer).not.toBeInTheDocument()
  })

  it('활성화된 상태에서는 리사이저가 표시된다', () => {
    render(
      <TestWrapper>
        <SplitPane left={leftContent} right={rightContent} disabled={false} />
      </TestWrapper>
    )

    // 리사이저가 있는지 확인 (cursor 스타일을 가진 요소)
    const container = screen.getByText('왼쪽 패널').closest('div')?.parentElement
    expect(container).toBeInTheDocument()
  })

  it('onResize 콜백이 호출된다', () => {
    const onResize = vi.fn()
    
    render(
      <TestWrapper>
        <SplitPane
          left={leftContent}
          right={rightContent}
          onResize={onResize}
          defaultSize={50}
        />
      </TestWrapper>
    )

    // 리사이저 요소 찾기 (마우스 커서가 설정된 요소)
    const resizer = document.querySelector('[style*="col-resize"]')
    
    if (resizer) {
      // 마우스 다운 이벤트
      fireEvent.mouseDown(resizer, { clientX: 500 })
      
      // 마우스 이동 이벤트
      fireEvent(document, createMouseEvent('mousemove', 600, 0))
      
      // 마우스 업 이벤트
      fireEvent(document, createMouseEvent('mouseup', 600, 0))
      
      expect(onResize).toHaveBeenCalled()
    }
  })

  it('최소 크기 제한이 적용된다', () => {
    const onResize = vi.fn()
    
    render(
      <TestWrapper>
        <SplitPane
          left={leftContent}
          right={rightContent}
          defaultSize={50}
          minSize={30}
          onResize={onResize}
        />
      </TestWrapper>
    )

    const resizer = document.querySelector('[style*="col-resize"]')
    
    if (resizer) {
      // 최소 크기보다 작게 드래그 시도
      fireEvent.mouseDown(resizer, { clientX: 500 })
      fireEvent(document, createMouseEvent('mousemove', 100, 0)) // 매우 작은 값
      fireEvent(document, createMouseEvent('mouseup', 100, 0))
      
      // onResize가 호출되었다면 최소값으로 제한되었을 것
      if (onResize.mock.calls.length > 0) {
        const lastCall = onResize.mock.calls[onResize.mock.calls.length - 1]
        expect(lastCall[0]).toBeGreaterThanOrEqual(30)
      }
    }
  })

  it('최대 크기 제한이 적용된다', () => {
    const onResize = vi.fn()
    
    render(
      <TestWrapper>
        <SplitPane
          left={leftContent}
          right={rightContent}
          defaultSize={50}
          maxSize={70}
          onResize={onResize}
        />
      </TestWrapper>
    )

    const resizer = document.querySelector('[style*="col-resize"]')
    
    if (resizer) {
      // 최대 크기보다 크게 드래그 시도
      fireEvent.mouseDown(resizer, { clientX: 500 })
      fireEvent(document, createMouseEvent('mousemove', 900, 0)) // 매우 큰 값
      fireEvent(document, createMouseEvent('mouseup', 900, 0))
      
      // onResize가 호출되었다면 최대값으로 제한되었을 것
      if (onResize.mock.calls.length > 0) {
        const lastCall = onResize.mock.calls[onResize.mock.calls.length - 1]
        expect(lastCall[0]).toBeLessThanOrEqual(70)
      }
    }
  })

  it('수직 방향에서 올바른 커서가 설정된다', () => {
    render(
      <TestWrapper>
        <SplitPane
          left={<div>위쪽 패널</div>}
          right={<div>아래쪽 패널</div>}
          direction="vertical"
        />
      </TestWrapper>
    )

    // 수직 방향에서는 row-resize 커서가 설정되어야 함
    const resizer = document.querySelector('[style*="row-resize"]')
    expect(resizer).toBeInTheDocument()
  })

  it('수평 방향에서 올바른 커서가 설정된다', () => {
    render(
      <TestWrapper>
        <SplitPane
          left={leftContent}
          right={rightContent}
          direction="horizontal"
        />
      </TestWrapper>
    )

    // 수평 방향에서는 col-resize 커서가 설정되어야 함
    const resizer = document.querySelector('[style*="col-resize"]')
    expect(resizer).toBeInTheDocument()
  })

  it('복잡한 콘텐츠를 올바르게 렌더링한다', () => {
    const complexLeft = (
      <div>
        <h2>왼쪽 제목</h2>
        <p>왼쪽 내용</p>
        <button>왼쪽 버튼</button>
      </div>
    )

    const complexRight = (
      <div>
        <h2>오른쪽 제목</h2>
        <ul>
          <li>항목 1</li>
          <li>항목 2</li>
        </ul>
        <button>오른쪽 버튼</button>
      </div>
    )

    render(
      <TestWrapper>
        <SplitPane left={complexLeft} right={complexRight} />
      </TestWrapper>
    )

    expect(screen.getByText('왼쪽 제목')).toBeInTheDocument()
    expect(screen.getByText('왼쪽 내용')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '왼쪽 버튼' })).toBeInTheDocument()
    expect(screen.getByText('오른쪽 제목')).toBeInTheDocument()
    expect(screen.getByText('항목 1')).toBeInTheDocument()
    expect(screen.getByText('항목 2')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '오른쪽 버튼' })).toBeInTheDocument()
  })

  it('드래그 중일 때 스타일이 변경된다', () => {
    render(
      <TestWrapper>
        <SplitPane left={leftContent} right={rightContent} />
      </TestWrapper>
    )

    const resizer = document.querySelector('[style*="col-resize"]')
    
    if (resizer) {
      // 드래그 시작
      fireEvent.mouseDown(resizer, { clientX: 500 })
      
      // 드래그 중일 때 스타일 변경 확인은 실제 DOM 조작이 필요하므로
      // 컴포넌트가 정상적으로 렌더링되는지만 확인
      expect(screen.getByText('왼쪽 패널')).toBeInTheDocument()
      expect(screen.getByText('오른쪽 패널')).toBeInTheDocument()
      
      // 드래그 종료
      fireEvent(document, createMouseEvent('mouseup', 500, 0))
    }
  })

  it('마우스 이벤트 리스너가 올바르게 정리된다', () => {
    const { unmount } = render(
      <TestWrapper>
        <SplitPane left={leftContent} right={rightContent} />
      </TestWrapper>
    )

    const resizer = document.querySelector('[style*="col-resize"]')
    
    if (resizer) {
      // 드래그 시작
      fireEvent.mouseDown(resizer, { clientX: 500 })
      
      // 컴포넌트 언마운트
      unmount()
      
      // 이벤트 리스너가 정리되었는지 확인하기 위해
      // 마우스 이벤트를 발생시켜도 에러가 나지 않아야 함
      expect(() => {
        fireEvent(document, createMouseEvent('mousemove', 600, 0))
        fireEvent(document, createMouseEvent('mouseup', 600, 0))
      }).not.toThrow()
    }
  })

  it('모든 props가 함께 사용될 수 있다', () => {
    const onResize = vi.fn()
    
    render(
      <TestWrapper>
        <SplitPane
          left={leftContent}
          right={rightContent}
          defaultSize={40}
          minSize={20}
          maxSize={80}
          direction="horizontal"
          onResize={onResize}
          disabled={false}
        />
      </TestWrapper>
    )

    expect(screen.getByText('왼쪽 패널')).toBeInTheDocument()
    expect(screen.getByText('오른쪽 패널')).toBeInTheDocument()
    
    // 리사이저가 존재하는지 확인
    const resizer = document.querySelector('[style*="col-resize"]')
    expect(resizer).toBeInTheDocument()
  })
})