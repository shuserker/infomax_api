import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { BrowserRouter } from 'react-router-dom'
import { PageContainer, BreadcrumbItem } from '../PageContainer'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ChakraProvider theme={theme}>{children}</ChakraProvider>
  </BrowserRouter>
)

describe('PageContainer 컴포넌트', () => {
  it('기본 페이지 컨테이너가 렌더링된다', () => {
    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지">
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByRole('heading', { name: '테스트 페이지' })).toBeInTheDocument()
    expect(screen.getByText('페이지 콘텐츠')).toBeInTheDocument()
  })

  it('부제목이 표시된다', () => {
    render(
      <TestWrapper>
        <PageContainer title="메인 제목" subtitle="부제목입니다">
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByText('부제목입니다')).toBeInTheDocument()
  })

  it('브레드크럼이 표시된다', () => {
    const breadcrumbs: BreadcrumbItem[] = [
      { label: '홈', href: '/' },
      { label: '대시보드', href: '/dashboard' },
      { label: '현재 페이지', isCurrentPage: true },
    ]

    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지" breadcrumbs={breadcrumbs}>
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByText('홈')).toBeInTheDocument()
    expect(screen.getByText('대시보드')).toBeInTheDocument()
    expect(screen.getByText('현재 페이지')).toBeInTheDocument()
  })

  it('브레드크럼 링크가 올바르게 작동한다', () => {
    const breadcrumbs: BreadcrumbItem[] = [
      { label: '홈', href: '/' },
      { label: '대시보드', href: '/dashboard' },
      { label: '현재 페이지', isCurrentPage: true },
    ]

    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지" breadcrumbs={breadcrumbs}>
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    // 링크가 있는 브레드크럼 항목들 확인
    const homeLink = screen.getByRole('link', { name: '홈' })
    const dashboardLink = screen.getByRole('link', { name: '대시보드' })
    
    expect(homeLink).toHaveAttribute('href', '/')
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    
    // 현재 페이지는 링크가 아님
    expect(screen.queryByRole('link', { name: '현재 페이지' })).not.toBeInTheDocument()
  })

  it('헤더 콘텐츠가 표시된다', () => {
    const headerContent = (
      <div>
        <button>액션 버튼</button>
        <span>추가 정보</span>
      </div>
    )

    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지" headerContent={headerContent}>
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByRole('button', { name: '액션 버튼' })).toBeInTheDocument()
    expect(screen.getByText('추가 정보')).toBeInTheDocument()
  })

  it('빈 브레드크럼 배열일 때 브레드크럼이 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지" breadcrumbs={[]}>
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    // 브레드크럼 네비게이션이 없어야 함
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument()
  })

  it('브레드크럼이 없을 때 브레드크럼이 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지">
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.queryByRole('navigation')).not.toBeInTheDocument()
  })

  it('커스텀 maxWidth가 적용된다', () => {
    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지" maxWidth="md">
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    // Container 컴포넌트가 렌더링되는지 확인
    expect(screen.getByText('페이지 콘텐츠')).toBeInTheDocument()
  })

  it('커스텀 padding이 적용된다', () => {
    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지" padding={8}>
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByText('페이지 콘텐츠')).toBeInTheDocument()
  })

  it('복잡한 콘텐츠를 올바르게 렌더링한다', () => {
    const complexContent = (
      <div>
        <h2>섹션 제목</h2>
        <p>섹션 내용</p>
        <ul>
          <li>항목 1</li>
          <li>항목 2</li>
        </ul>
        <button>액션 버튼</button>
      </div>
    )

    render(
      <TestWrapper>
        <PageContainer title="복잡한 페이지">
          {complexContent}
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByText('섹션 제목')).toBeInTheDocument()
    expect(screen.getByText('섹션 내용')).toBeInTheDocument()
    expect(screen.getByText('항목 1')).toBeInTheDocument()
    expect(screen.getByText('항목 2')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '액션 버튼' })).toBeInTheDocument()
  })

  it('모든 props가 함께 사용될 수 있다', () => {
    const breadcrumbs: BreadcrumbItem[] = [
      { label: '홈', href: '/' },
      { label: '현재 페이지', isCurrentPage: true },
    ]

    const headerContent = <button>헤더 버튼</button>

    render(
      <TestWrapper>
        <PageContainer
          title="전체 기능 페이지"
          subtitle="모든 기능을 포함한 페이지"
          breadcrumbs={breadcrumbs}
          headerContent={headerContent}
          maxWidth="lg"
          padding={4}
        >
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByRole('heading', { name: '전체 기능 페이지' })).toBeInTheDocument()
    expect(screen.getByText('모든 기능을 포함한 페이지')).toBeInTheDocument()
    expect(screen.getByText('홈')).toBeInTheDocument()
    expect(screen.getByText('현재 페이지')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '헤더 버튼' })).toBeInTheDocument()
    expect(screen.getByText('페이지 콘텐츠')).toBeInTheDocument()
  })

  it('href가 없는 브레드크럼 항목은 링크가 아니다', () => {
    const breadcrumbs: BreadcrumbItem[] = [
      { label: '홈', href: '/' },
      { label: '중간 페이지' }, // href 없음
      { label: '현재 페이지', isCurrentPage: true },
    ]

    render(
      <TestWrapper>
        <PageContainer title="테스트 페이지" breadcrumbs={breadcrumbs}>
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByRole('link', { name: '홈' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: '중간 페이지' })).not.toBeInTheDocument()
    expect(screen.getByText('중간 페이지')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: '현재 페이지' })).not.toBeInTheDocument()
  })

  it('제목만 있고 다른 헤더 요소가 없을 때도 올바르게 렌더링된다', () => {
    render(
      <TestWrapper>
        <PageContainer title="단순한 페이지">
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    expect(screen.getByRole('heading', { name: '단순한 페이지' })).toBeInTheDocument()
    expect(screen.getByText('페이지 콘텐츠')).toBeInTheDocument()
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument()
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    const breadcrumbs: BreadcrumbItem[] = [
      { label: '홈', href: '/' },
      { label: '현재 페이지', isCurrentPage: true },
    ]

    render(
      <TestWrapper>
        <PageContainer title="접근성 테스트 페이지" breadcrumbs={breadcrumbs}>
          <div>페이지 콘텐츠</div>
        </PageContainer>
      </TestWrapper>
    )

    // 제목이 heading 역할을 가지는지 확인
    expect(screen.getByRole('heading', { name: '접근성 테스트 페이지' })).toBeInTheDocument()
    
    // 브레드크럼이 navigation 역할을 가지는지 확인
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })
})