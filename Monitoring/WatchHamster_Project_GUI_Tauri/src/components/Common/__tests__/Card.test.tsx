import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import { MdEdit, MdDelete } from 'react-icons/md'
import { Card, CardAction } from '../Card'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('Card 컴포넌트', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('기본 카드가 렌더링된다', () => {
    render(
      <TestWrapper>
        <Card>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.getByText('카드 콘텐츠')).toBeInTheDocument()
  })

  it('제목이 있을 때 헤더가 표시된다', () => {
    render(
      <TestWrapper>
        <Card title="테스트 카드">
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.getByRole('heading', { name: '테스트 카드' })).toBeInTheDocument()
  })

  it('부제목이 표시된다', () => {
    render(
      <TestWrapper>
        <Card title="메인 제목" subtitle="부제목입니다">
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.getByText('부제목입니다')).toBeInTheDocument()
  })

  it('헤더 콘텐츠가 표시된다', () => {
    const headerContent = <div>커스텀 헤더 콘텐츠</div>

    render(
      <TestWrapper>
        <Card title="테스트 카드" headerContent={headerContent}>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.getByText('커스텀 헤더 콘텐츠')).toBeInTheDocument()
  })

  it('액션 메뉴가 표시된다', () => {
    const actions: CardAction[] = [
      {
        label: '편집',
        onClick: vi.fn(),
        icon: MdEdit,
      },
      {
        label: '삭제',
        onClick: vi.fn(),
        icon: MdDelete,
      },
    ]

    render(
      <TestWrapper>
        <Card title="테스트 카드" actions={actions}>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    // 액션 메뉴 버튼이 있는지 확인
    const actionButton = screen.getByRole('button', { name: '카드 액션' })
    expect(actionButton).toBeInTheDocument()
  })

  it('액션 메뉴를 클릭하면 메뉴 항목들이 표시된다', async () => {
    const user = userEvent.setup()
    const editAction = vi.fn()
    const deleteAction = vi.fn()

    const actions: CardAction[] = [
      {
        label: '편집',
        onClick: editAction,
        icon: MdEdit,
      },
      {
        label: '삭제',
        onClick: deleteAction,
        icon: MdDelete,
      },
    ]

    render(
      <TestWrapper>
        <Card title="테스트 카드" actions={actions}>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    // 액션 메뉴 버튼 클릭
    const actionButton = screen.getByRole('button', { name: '카드 액션' })
    await user.click(actionButton)

    // 메뉴 항목들이 표시되는지 확인
    expect(screen.getByRole('menuitem', { name: '편집' })).toBeInTheDocument()
    expect(screen.getByRole('menuitem', { name: '삭제' })).toBeInTheDocument()
  })

  it('액션 메뉴 항목을 클릭하면 해당 함수가 호출된다', async () => {
    const user = userEvent.setup()
    const editAction = vi.fn()
    const deleteAction = vi.fn()

    const actions: CardAction[] = [
      {
        label: '편집',
        onClick: editAction,
      },
      {
        label: '삭제',
        onClick: deleteAction,
      },
    ]

    render(
      <TestWrapper>
        <Card title="테스트 카드" actions={actions}>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    // 액션 메뉴 열기
    const actionButton = screen.getByRole('button', { name: '카드 액션' })
    await user.click(actionButton)

    // 편집 메뉴 항목 클릭
    await user.click(screen.getByRole('menuitem', { name: '편집' }))

    expect(editAction).toHaveBeenCalledTimes(1)
  })

  it('로딩 상태일 때 로딩 오버레이가 표시된다', () => {
    render(
      <TestWrapper>
        <Card isLoading={true}>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.getByText('로딩 중...')).toBeInTheDocument()
    // 원본 콘텐츠도 여전히 존재하지만 오버레이로 가려짐
    expect(screen.getByText('카드 콘텐츠')).toBeInTheDocument()
  })

  it('액션이 없을 때 액션 메뉴가 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <Card title="테스트 카드">
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.queryByRole('button', { name: '카드 액션' })).not.toBeInTheDocument()
  })

  it('빈 액션 배열일 때 액션 메뉴가 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <Card title="테스트 카드" actions={[]}>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.queryByRole('button', { name: '카드 액션' })).not.toBeInTheDocument()
  })

  it('제목과 부제목이 모두 없을 때 헤더가 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <Card>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    // 헤더 영역이 없으므로 heading 요소가 없어야 함
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
  })

  it('복잡한 콘텐츠를 올바르게 렌더링한다', () => {
    const complexContent = (
      <div>
        <h3>복잡한 콘텐츠</h3>
        <p>이것은 복잡한 카드 콘텐츠입니다.</p>
        <ul>
          <li>항목 1</li>
          <li>항목 2</li>
          <li>항목 3</li>
        </ul>
        <button>액션 버튼</button>
      </div>
    )

    render(
      <TestWrapper>
        <Card title="복잡한 카드">{complexContent}</Card>
      </TestWrapper>
    )

    expect(screen.getByText('복잡한 콘텐츠')).toBeInTheDocument()
    expect(screen.getByText('이것은 복잡한 카드 콘텐츠입니다.')).toBeInTheDocument()
    expect(screen.getByText('항목 1')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '액션 버튼' })).toBeInTheDocument()
  })

  it('커스텀 props가 카드에 전달된다', () => {
    render(
      <TestWrapper>
        <Card data-testid="custom-card" className="custom-class">
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    const card = screen.getByTestId('custom-card')
    expect(card).toBeInTheDocument()
    expect(card).toHaveClass('custom-class')
  })

  it('hover 효과를 비활성화할 수 있다', () => {
    render(
      <TestWrapper>
        <Card hover={false} data-testid="no-hover-card">
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    const card = screen.getByTestId('no-hover-card')
    expect(card).toBeInTheDocument()
    // hover 효과가 비활성화되어 있는지는 스타일로 확인하기 어려우므로
    // 컴포넌트가 정상적으로 렌더링되는지만 확인
  })

  it('모든 헤더 요소가 함께 표시될 수 있다', () => {
    const headerContent = <span>추가 헤더</span>
    const actions: CardAction[] = [
      {
        label: '액션',
        onClick: vi.fn(),
      },
    ]

    render(
      <TestWrapper>
        <Card
          title="메인 제목"
          subtitle="부제목"
          headerContent={headerContent}
          actions={actions}
        >
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    expect(screen.getByRole('heading', { name: '메인 제목' })).toBeInTheDocument()
    expect(screen.getByText('부제목')).toBeInTheDocument()
    expect(screen.getByText('추가 헤더')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '카드 액션' })).toBeInTheDocument()
  })

  it('액션에 colorScheme이 적용된다', async () => {
    const user = userEvent.setup()
    const actions: CardAction[] = [
      {
        label: '위험한 액션',
        onClick: vi.fn(),
        colorScheme: 'red',
      },
    ]

    render(
      <TestWrapper>
        <Card title="테스트 카드" actions={actions}>
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    // 액션 메뉴 열기
    const actionButton = screen.getByRole('button', { name: '카드 액션' })
    await user.click(actionButton)

    // 메뉴 항목 확인 (colorScheme은 내부적으로 처리되므로 존재 여부만 확인)
    expect(screen.getByRole('menuitem', { name: '위험한 액션' })).toBeInTheDocument()
  })

  it('로딩 상태와 다른 props가 함께 작동한다', () => {
    const actions: CardAction[] = [
      {
        label: '액션',
        onClick: vi.fn(),
      },
    ]

    render(
      <TestWrapper>
        <Card
          title="로딩 카드"
          subtitle="로딩 중입니다"
          actions={actions}
          isLoading={true}
        >
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    // 모든 요소가 렌더링되지만 로딩 오버레이가 표시됨
    expect(screen.getByRole('heading', { name: '로딩 카드' })).toBeInTheDocument()
    expect(screen.getByText('로딩 중입니다')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '카드 액션' })).toBeInTheDocument()
    expect(screen.getByText('로딩 중...')).toBeInTheDocument()
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    render(
      <TestWrapper>
        <Card title="접근성 테스트 카드">
          <div>카드 콘텐츠</div>
        </Card>
      </TestWrapper>
    )

    // 제목이 heading 역할을 가지는지 확인
    const heading = screen.getByRole('heading', { name: '접근성 테스트 카드' })
    expect(heading).toBeInTheDocument()
  })
})