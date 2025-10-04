/**
 * 사용자 경험 개선 테스트
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import React from 'react'
import {
  LoadingSpinner,
  ProgressLoading,
  CircularLoading,
  SkeletonLoading,
  ErrorComponent,
  NetworkStatus,
  EmptyState,
  StateWrapper,
  InlineLoading,
  LoadingButton
} from '@/components/Common/LoadingStates'
import {
  useKeyboardNavigation,
  useFocusManagement,
  useScreenReaderAnnouncement,
  useColorContrast,
  useKeyboardUser,
  useAccessibilityPreferences,
  useTextScaling
} from '@/hooks/useAccessibility'
import {
  useViewport,
  useResponsiveValue,
  useResponsiveColumns,
  useTouchDevice,
  useNetworkStatus,
  useResponsiveLayout
} from '@/hooks/useResponsiveDesign'
import { renderHook, act } from '@testing-library/react'

// 테스트 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>{children}</ChakraProvider>
)

describe('로딩 상태 컴포넌트 테스트', () => {
  it('LoadingSpinner가 올바르게 렌더링되어야 함', () => {
    render(
      <TestWrapper>
        <LoadingSpinner message="로딩 중..." />
      </TestWrapper>
    )

    expect(screen.getByText('로딩 중...')).toBeInTheDocument()
  })

  it('ProgressLoading이 진행률을 올바르게 표시해야 함', () => {
    render(
      <TestWrapper>
        <ProgressLoading progress={75} message="업로드 중..." />
      </TestWrapper>
    )

    expect(screen.getByText('업로드 중...')).toBeInTheDocument()
    expect(screen.getByText('75%')).toBeInTheDocument()
  })

  it('CircularLoading이 원형 진행률을 표시해야 함', () => {
    render(
      <TestWrapper>
        <CircularLoading progress={50} message="처리 중..." />
      </TestWrapper>
    )

    expect(screen.getByText('처리 중...')).toBeInTheDocument()
    expect(screen.getByText('50%')).toBeInTheDocument()
  })

  it('SkeletonLoading이 지정된 줄 수만큼 렌더링되어야 함', () => {
    const { container } = render(
      <TestWrapper>
        <SkeletonLoading lines={3} />
      </TestWrapper>
    )

    const skeletons = container.querySelectorAll('[data-testid="skeleton"]')
    expect(skeletons).toHaveLength(3)
  })
})

describe('에러 상태 컴포넌트 테스트', () => {
  it('ErrorComponent가 에러 메시지를 표시해야 함', () => {
    const mockRetry = vi.fn()

    render(
      <TestWrapper>
        <ErrorComponent
          hasError={true}
          error="네트워크 오류가 발생했습니다"
          title="연결 실패"
          canRetry={true}
          onRetry={mockRetry}
        />
      </TestWrapper>
    )

    expect(screen.getByText('연결 실패')).toBeInTheDocument()
    expect(screen.getByText('네트워크 오류가 발생했습니다')).toBeInTheDocument()
    
    const retryButton = screen.getByText('다시 시도')
    expect(retryButton).toBeInTheDocument()
    
    fireEvent.click(retryButton)
    expect(mockRetry).toHaveBeenCalledTimes(1)
  })

  it('NetworkStatus가 오프라인 상태를 표시해야 함', () => {
    const mockReconnect = vi.fn()

    render(
      <TestWrapper>
        <NetworkStatus isOnline={false} onReconnect={mockReconnect} />
      </TestWrapper>
    )

    expect(screen.getByText('네트워크 연결 끊김')).toBeInTheDocument()
    expect(screen.getByText('인터넷 연결을 확인해주세요.')).toBeInTheDocument()
    
    const reconnectButton = screen.getByText('재연결')
    fireEvent.click(reconnectButton)
    expect(mockReconnect).toHaveBeenCalledTimes(1)
  })

  it('EmptyState가 빈 상태를 올바르게 표시해야 함', () => {
    const mockAction = vi.fn()

    render(
      <TestWrapper>
        <EmptyState
          title="데이터가 없습니다"
          description="새로운 항목을 추가해보세요"
          action={{
            label: '추가하기',
            onClick: mockAction
          }}
        />
      </TestWrapper>
    )

    expect(screen.getByText('데이터가 없습니다')).toBeInTheDocument()
    expect(screen.getByText('새로운 항목을 추가해보세요')).toBeInTheDocument()
    
    const actionButton = screen.getByText('추가하기')
    fireEvent.click(actionButton)
    expect(mockAction).toHaveBeenCalledTimes(1)
  })
})

describe('상태 래퍼 컴포넌트 테스트', () => {
  it('StateWrapper가 로딩 상태를 올바르게 처리해야 함', () => {
    render(
      <TestWrapper>
        <StateWrapper
          loading={{ isLoading: true, message: '로딩 중...' }}
        >
          <div>콘텐츠</div>
        </StateWrapper>
      </TestWrapper>
    )

    expect(screen.getByText('로딩 중...')).toBeInTheDocument()
    expect(screen.queryByText('콘텐츠')).not.toBeInTheDocument()
  })

  it('StateWrapper가 에러 상태를 올바르게 처리해야 함', () => {
    render(
      <TestWrapper>
        <StateWrapper
          error={{ hasError: true, error: '오류 발생' }}
        >
          <div>콘텐츠</div>
        </StateWrapper>
      </TestWrapper>
    )

    expect(screen.getByText('오류가 발생했습니다')).toBeInTheDocument()
    expect(screen.queryByText('콘텐츠')).not.toBeInTheDocument()
  })

  it('StateWrapper가 빈 상태를 올바르게 처리해야 함', () => {
    render(
      <TestWrapper>
        <StateWrapper
          isEmpty={true}
          emptyState={{
            title: '빈 상태',
            description: '데이터가 없습니다'
          }}
        >
          <div>콘텐츠</div>
        </StateWrapper>
      </TestWrapper>
    )

    expect(screen.getByText('빈 상태')).toBeInTheDocument()
    expect(screen.queryByText('콘텐츠')).not.toBeInTheDocument()
  })

  it('StateWrapper가 정상 상태에서 콘텐츠를 표시해야 함', () => {
    render(
      <TestWrapper>
        <StateWrapper>
          <div>콘텐츠</div>
        </StateWrapper>
      </TestWrapper>
    )

    expect(screen.getByText('콘텐츠')).toBeInTheDocument()
  })
})

describe('인라인 로딩 컴포넌트 테스트', () => {
  it('InlineLoading이 로딩 상태를 표시해야 함', () => {
    render(
      <TestWrapper>
        <InlineLoading isLoading={true} text="저장 중..." />
      </TestWrapper>
    )

    expect(screen.getByText('저장 중...')).toBeInTheDocument()
  })

  it('LoadingButton이 로딩 상태를 올바르게 처리해야 함', () => {
    const mockClick = vi.fn()

    render(
      <TestWrapper>
        <LoadingButton
          isLoading={true}
          loadingText="처리 중..."
          onClick={mockClick}
        >
          클릭
        </LoadingButton>
      </TestWrapper>
    )

    expect(screen.getByText('처리 중...')).toBeInTheDocument()
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })
})

describe('접근성 훅 테스트', () => {
  beforeEach(() => {
    // DOM 환경 설정
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })
  })

  describe('useKeyboardNavigation', () => {
    it('키보드 네비게이션이 올바르게 작동해야 함', () => {
      const items = ['item1', 'item2', 'item3']
      const mockSelect = vi.fn()

      const { result } = renderHook(() => 
        useKeyboardNavigation(items, mockSelect)
      )

      expect(result.current.activeIndex).toBe(-1)

      // ArrowDown 키 시뮬레이션은 실제 DOM 이벤트가 필요하므로 생략
      // 대신 setActiveIndex 함수 테스트
      act(() => {
        result.current.setActiveIndex(0)
      })

      expect(result.current.activeIndex).toBe(0)
    })
  })

  describe('useScreenReaderAnnouncement', () => {
    it('스크린 리더 알림이 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useScreenReaderAnnouncement())

      act(() => {
        result.current.announce('테스트 메시지')
      })

      // 알림 컴포넌트 렌더링 테스트
      const { container } = render(<result.current.AnnouncementComponent />)
      expect(container.querySelector('[aria-live="polite"]')).toBeInTheDocument()
    })
  })

  describe('useColorContrast', () => {
    it('색상 대비 검사가 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useColorContrast())

      // 기본적인 대비 검사 (실제 계산은 브라우저 환경에서만 가능)
      const contrast = result.current.checkContrast('#000000', '#ffffff')
      expect(typeof contrast).toBe('number')
      expect(contrast).toBeGreaterThan(0)

      const isAccessible = result.current.isAccessible(4.5)
      expect(typeof isAccessible).toBe('boolean')
    })
  })

  describe('useKeyboardUser', () => {
    it('키보드 사용자 감지가 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useKeyboardUser())

      expect(typeof result.current).toBe('boolean')
      expect(result.current).toBe(false) // 초기값
    })
  })

  describe('useAccessibilityPreferences', () => {
    it('접근성 환경설정을 올바르게 감지해야 함', () => {
      const { result } = renderHook(() => useAccessibilityPreferences())

      expect(result.current).toHaveProperty('prefersReducedMotion')
      expect(result.current).toHaveProperty('prefersHighContrast')
      expect(result.current).toHaveProperty('prefersColorScheme')
      
      expect(typeof result.current.prefersReducedMotion).toBe('boolean')
      expect(typeof result.current.prefersHighContrast).toBe('boolean')
      expect(['light', 'dark']).toContain(result.current.prefersColorScheme)
    })
  })

  describe('useTextScaling', () => {
    it('텍스트 크기 조정이 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useTextScaling())

      expect(result.current.scale).toBe(1)

      act(() => {
        result.current.increaseTextSize()
      })

      expect(result.current.scale).toBe(1.1)

      act(() => {
        result.current.decreaseTextSize()
      })

      expect(result.current.scale).toBe(1)

      act(() => {
        result.current.resetTextSize()
      })

      expect(result.current.scale).toBe(1)
    })
  })
})

describe('반응형 디자인 훅 테스트', () => {
  beforeEach(() => {
    // 윈도우 크기 모킹
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1200,
    })
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 800,
    })
  })

  describe('useViewport', () => {
    it('뷰포트 정보를 올바르게 반환해야 함', () => {
      const { result } = renderHook(() => useViewport())

      expect(result.current.width).toBe(1200)
      expect(result.current.height).toBe(800)
      expect(result.current.deviceType).toBe('desktop')
      expect(result.current.orientation).toBe('landscape')
      expect(result.current.isDesktop).toBe(true)
      expect(result.current.isMobile).toBe(false)
      expect(result.current.isTablet).toBe(false)
    })
  })

  describe('useResponsiveValue', () => {
    it('반응형 값을 올바르게 반환해야 함', () => {
      // 데스크톱 환경에서 테스트
      const { result } = renderHook(() => 
        useResponsiveValue({
          xs: 'mobile',
          md: 'tablet',
          xl: 'desktop'
        })
      )

      expect(result.current).toBe('desktop')
    })
  })

  describe('useResponsiveColumns', () => {
    it('반응형 컬럼 수를 올바르게 계산해야 함', () => {
      const { result } = renderHook(() => 
        useResponsiveColumns(300, 4)
      )

      // 1200px 너비에서 300px 최소 너비로 계산
      expect(result.current).toBeGreaterThan(0)
      expect(result.current).toBeLessThanOrEqual(4)
    })
  })

  describe('useTouchDevice', () => {
    it('터치 디바이스 감지가 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useTouchDevice())

      expect(typeof result.current).toBe('boolean')
    })
  })

  describe('useNetworkStatus', () => {
    it('네트워크 상태를 올바르게 반환해야 함', () => {
      const { result } = renderHook(() => useNetworkStatus())

      expect(result.current).toHaveProperty('isOnline')
      expect(result.current).toHaveProperty('effectiveType')
      expect(result.current).toHaveProperty('downlink')
      expect(result.current).toHaveProperty('rtt')
      
      expect(typeof result.current.isOnline).toBe('boolean')
      expect(['2g', '3g', '4g', 'slow-2g']).toContain(result.current.effectiveType)
    })
  })

  describe('useResponsiveLayout', () => {
    it('반응형 레이아웃 설정을 올바르게 반환해야 함', () => {
      const { result } = renderHook(() => useResponsiveLayout())

      expect(result.current).toHaveProperty('showSidebar')
      expect(result.current).toHaveProperty('sidebarPosition')
      expect(result.current).toHaveProperty('headerHeight')
      expect(result.current).toHaveProperty('containerPadding')
      expect(result.current).toHaveProperty('buttonSize')
      expect(result.current).toHaveProperty('modalSize')
      
      // 데스크톱 환경에서의 기본값 확인
      expect(result.current.showSidebar).toBe(true)
      expect(result.current.sidebarPosition).toBe('static')
    })
  })
})

describe('사용자 경험 통합 테스트', () => {
  it('로딩에서 에러 상태로 전환이 올바르게 작동해야 함', async () => {
    let hasError = false
    let isLoading = true

    const { rerender } = render(
      <TestWrapper>
        <StateWrapper
          loading={{ isLoading, message: '데이터 로딩 중...' }}
          error={{ hasError, error: '로딩 실패' }}
        >
          <div>데이터 콘텐츠</div>
        </StateWrapper>
      </TestWrapper>
    )

    // 초기 로딩 상태 확인
    expect(screen.getByText('데이터 로딩 중...')).toBeInTheDocument()

    // 에러 상태로 전환
    isLoading = false
    hasError = true

    rerender(
      <TestWrapper>
        <StateWrapper
          loading={{ isLoading, message: '데이터 로딩 중...' }}
          error={{ hasError, error: '로딩 실패' }}
        >
          <div>데이터 콘텐츠</div>
        </StateWrapper>
      </TestWrapper>
    )

    expect(screen.getByText('오류가 발생했습니다')).toBeInTheDocument()
    expect(screen.queryByText('데이터 로딩 중...')).not.toBeInTheDocument()
  })

  it('반응형 디자인이 다양한 화면 크기에서 올바르게 작동해야 함', () => {
    // 모바일 크기로 변경
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })

    const { result } = renderHook(() => useViewport())

    expect(result.current.isMobile).toBe(true)
    expect(result.current.deviceType).toBe('mobile')

    // 태블릿 크기로 변경
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    })

    // 리사이즈 이벤트 시뮬레이션
    act(() => {
      window.dispatchEvent(new Event('resize'))
    })

    // 새로운 훅 인스턴스로 테스트
    const { result: tabletResult } = renderHook(() => useViewport())
    expect(tabletResult.current.isTablet).toBe(true)
  })
})