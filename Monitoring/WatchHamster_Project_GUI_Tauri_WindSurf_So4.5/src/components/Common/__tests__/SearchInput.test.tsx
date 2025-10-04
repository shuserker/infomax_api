import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import { SearchInput } from '../SearchInput'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

// 타이머 모킹
vi.useFakeTimers()

describe('SearchInput 컴포넌트', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.clearAllTimers()
  })

  afterEach(() => {
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
    vi.useFakeTimers()
  })

  it('기본 검색 입력이 렌더링된다', () => {
    render(
      <TestWrapper>
        <SearchInput />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    expect(input).toBeInTheDocument()
    
    // 검색 아이콘이 있는지 확인
    const searchIcon = document.querySelector('svg')
    expect(searchIcon).toBeInTheDocument()
  })

  it('커스텀 placeholder가 표시된다', () => {
    render(
      <TestWrapper>
        <SearchInput placeholder="사용자를 검색하세요..." />
      </TestWrapper>
    )

    expect(screen.getByPlaceholderText('사용자를 검색하세요...')).toBeInTheDocument()
  })

  it('입력 시 디바운싱이 적용된다', async () => {
    const onSearch = vi.fn()
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput onSearch={onSearch} debounceMs={300} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    
    // 빠르게 여러 글자 입력
    await user.type(input, 'test')
    
    // 디바운스 시간 전에는 호출되지 않음
    expect(onSearch).not.toHaveBeenCalled()
    
    // 디바운스 시간 경과
    vi.advanceTimersByTime(300)
    
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test')
      expect(onSearch).toHaveBeenCalledTimes(1)
    })
  })

  it('Enter 키 입력 시 즉시 검색이 실행된다', async () => {
    const onSearch = vi.fn()
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput onSearch={onSearch} debounceMs={300} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    
    await user.type(input, 'test')
    await user.keyboard('{Enter}')
    
    // Enter 키로 즉시 실행되므로 디바운스 시간을 기다리지 않음
    expect(onSearch).toHaveBeenCalledWith('test')
  })

  it('지우기 버튼이 입력값이 있을 때만 표시된다', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput />
      </TestWrapper>
    )

    // 초기에는 지우기 버튼이 없음
    expect(screen.queryByRole('button', { name: '검색어 지우기' })).not.toBeInTheDocument()

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    await user.type(input, 'test')

    // 입력 후에는 지우기 버튼이 표시됨
    expect(screen.getByRole('button', { name: '검색어 지우기' })).toBeInTheDocument()
  })

  it('지우기 버튼 클릭 시 입력값이 초기화된다', async () => {
    const onSearch = vi.fn()
    const onClear = vi.fn()
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput onSearch={onSearch} onClear={onClear} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    
    // 텍스트 입력
    await user.type(input, 'test')
    expect(input).toHaveValue('test')

    // 지우기 버튼 클릭
    const clearButton = screen.getByRole('button', { name: '검색어 지우기' })
    await user.click(clearButton)

    // 입력값이 초기화됨
    expect(input).toHaveValue('')
    expect(onSearch).toHaveBeenCalledWith('')
    expect(onClear).toHaveBeenCalled()
  })

  it('showClearButton이 false일 때 지우기 버튼이 표시되지 않는다', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput showClearButton={false} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    await user.type(input, 'test')

    // 입력값이 있어도 지우기 버튼이 표시되지 않음
    expect(screen.queryByRole('button', { name: '검색어 지우기' })).not.toBeInTheDocument()
  })

  it('커스텀 디바운스 시간이 적용된다', async () => {
    const onSearch = vi.fn()
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput onSearch={onSearch} debounceMs={500} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    await user.type(input, 'test')

    // 300ms 후에는 아직 호출되지 않음
    vi.advanceTimersByTime(300)
    expect(onSearch).not.toHaveBeenCalled()

    // 500ms 후에 호출됨
    vi.advanceTimersByTime(200)
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test')
    })
  })

  it('연속 입력 시 이전 타이머가 취소된다', async () => {
    const onSearch = vi.fn()
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput onSearch={onSearch} debounceMs={300} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    
    // 첫 번째 입력
    await user.type(input, 'te')
    
    // 100ms 후 추가 입력 (타이머 리셋)
    vi.advanceTimersByTime(100)
    await user.type(input, 'st')
    
    // 첫 번째 타이머 시간이 지나도 호출되지 않음
    vi.advanceTimersByTime(200)
    expect(onSearch).not.toHaveBeenCalled()
    
    // 두 번째 타이머 완료 후 호출됨
    vi.advanceTimersByTime(100)
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test')
      expect(onSearch).toHaveBeenCalledTimes(1)
    })
  })

  it('추가 Input props가 전달된다', () => {
    render(
      <TestWrapper>
        <SearchInput
          size="lg"
          variant="filled"
          data-testid="search-input"
          isDisabled
        />
      </TestWrapper>
    )

    const input = screen.getByTestId('search-input')
    expect(input).toBeInTheDocument()
    expect(input).toBeDisabled()
  })

  it('onSearch 콜백이 없어도 정상 작동한다', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    
    // 에러 없이 입력 가능
    await user.type(input, 'test')
    expect(input).toHaveValue('test')
    
    // Enter 키도 에러 없이 처리
    await user.keyboard('{Enter}')
  })

  it('onClear 콜백이 없어도 지우기 버튼이 작동한다', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    await user.type(input, 'test')
    
    const clearButton = screen.getByRole('button', { name: '검색어 지우기' })
    await user.click(clearButton)
    
    expect(input).toHaveValue('')
  })

  it('컴포넌트 언마운트 시 타이머가 정리된다', () => {
    const onSearch = vi.fn()
    
    const { unmount } = render(
      <TestWrapper>
        <SearchInput onSearch={onSearch} debounceMs={300} />
      </TestWrapper>
    )

    // 컴포넌트 언마운트
    unmount()
    
    // 타이머가 실행되어도 에러가 발생하지 않아야 함
    expect(() => {
      vi.advanceTimersByTime(300)
    }).not.toThrow()
  })

  it('빈 문자열 검색이 가능하다', async () => {
    const onSearch = vi.fn()
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })

    render(
      <TestWrapper>
        <SearchInput onSearch={onSearch} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    
    // 텍스트 입력 후 모두 삭제
    await user.type(input, 'test')
    await user.clear(input)
    
    vi.advanceTimersByTime(300)
    
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('')
    })
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    render(
      <TestWrapper>
        <SearchInput />
      </TestWrapper>
    )

    const input = screen.getByRole('textbox')
    expect(input).toBeInTheDocument()
    
    // 지우기 버튼의 aria-label 확인을 위해 텍스트 입력
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    user.type(input, 'test').then(() => {
      const clearButton = screen.queryByRole('button', { name: '검색어 지우기' })
      if (clearButton) {
        expect(clearButton).toHaveAttribute('aria-label', '검색어 지우기')
      }
    })
  })
})