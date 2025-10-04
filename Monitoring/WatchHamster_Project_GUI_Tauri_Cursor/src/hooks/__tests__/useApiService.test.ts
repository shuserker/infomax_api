import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { ChakraProvider, useToast } from '@chakra-ui/react'
import React from 'react'
import { useApiService, useApiOperation, useServiceControl } from '../useApiService'
import { apiService, ApiServiceError } from '../../services/api'
import { handleQueryError } from '../../services/errorHandler'
import theme from '../../theme'

// 모킹
vi.mock('@chakra-ui/react', async () => {
  const actual = await vi.importActual('@chakra-ui/react')
  return {
    ...actual,
    useToast: vi.fn(),
  }
})

vi.mock('../../services/api', () => ({
  apiService: {
    startService: vi.fn(),
    stopService: vi.fn(),
    restartService: vi.fn(),
    testConnection: vi.fn(),
    healthCheck: vi.fn(),
  },
  ApiServiceError: class extends Error {
    constructor(message: string, public status?: number, public code?: string) {
      super(message)
      this.name = 'ApiServiceError'
    }
  },
}))

vi.mock('../../services/errorHandler', () => ({
  handleQueryError: vi.fn(),
  getRecoveryStrategy: vi.fn(),
}))

const mockToast = vi.fn()
const mockHandleQueryError = vi.mocked(handleQueryError)

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return React.createElement(ChakraProvider, { theme }, children)
}

describe('useApiService 훅', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useToast as any).mockReturnValue(mockToast)
    mockHandleQueryError.mockReturnValue({
      title: '오류 발생',
      description: '테스트 오류',
      status: 'error',
      duration: 5000,
      isClosable: true,
    })
  })

  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    expect(result.current.loading).toEqual({})
    expect(result.current.errors).toEqual({})
    expect(typeof result.current.callApi).toBe('function')
    expect(typeof result.current.retry).toBe('function')
    expect(typeof result.current.clearState).toBe('function')
  })

  it('성공적인 API 호출이 올바르게 처리된다', async () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    const mockApiCall = vi.fn().mockResolvedValue('성공 결과')
    const mockOnSuccess = vi.fn()

    await act(async () => {
      const response = await result.current.callApi(mockApiCall, {
        loadingKey: 'test',
        successMessage: '성공했습니다',
        onSuccess: mockOnSuccess,
      })

      expect(response).toBe('성공 결과')
    })

    expect(mockApiCall).toHaveBeenCalledTimes(1)
    expect(mockOnSuccess).toHaveBeenCalledWith('성공 결과')
    expect(result.current.showSuccessToast).toBeDefined()
    expect(result.current.isLoading('test')).toBe(false)
  })

  it('API 호출 실패가 올바르게 처리된다', async () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    const testError = new ApiServiceError('테스트 오류', 500)
    const mockApiCall = vi.fn().mockRejectedValue(testError)
    const mockOnError = vi.fn()

    await act(async () => {
      const response = await result.current.callApi(mockApiCall, {
        loadingKey: 'test',
        errorContext: 'testError',
        onError: mockOnError,
      })

      expect(response).toBeNull()
    })

    expect(mockApiCall).toHaveBeenCalledTimes(1)
    expect(mockOnError).toHaveBeenCalledWith(testError)
    expect(mockHandleQueryError).toHaveBeenCalledWith(testError, 'testError')
    expect(mockToast).toHaveBeenCalled()
    expect(result.current.hasError('testError')).toBe(true)
  })

  it('로딩 상태가 올바르게 관리된다', async () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    const mockApiCall = vi.fn().mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve('결과'), 100))
    )

    // API 호출 시작
    act(() => {
      result.current.callApi(mockApiCall, { loadingKey: 'test' })
    })

    // 로딩 상태 확인
    expect(result.current.isLoading('test')).toBe(true)

    // API 호출 완료 대기
    await waitFor(() => {
      expect(result.current.isLoading('test')).toBe(false)
    })
  })

  it('에러 토스트 표시를 비활성화할 수 있다', async () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    const testError = new Error('테스트 오류')
    const mockApiCall = vi.fn().mockRejectedValue(testError)

    await act(async () => {
      await result.current.callApi(mockApiCall, {
        loadingKey: 'test',
        showErrorToast: false,
      })
    })

    expect(mockToast).not.toHaveBeenCalled()
  })

  it('상태를 개별적으로 지울 수 있다', () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    // 상태 설정
    act(() => {
      result.current.setLoadingState('test1', true)
      result.current.setLoadingState('test2', true)
      result.current.setErrorState('test1', new ApiServiceError('오류'))
    })

    expect(result.current.isLoading('test1')).toBe(true)
    expect(result.current.isLoading('test2')).toBe(true)
    expect(result.current.hasError('test1')).toBe(true)

    // 개별 상태 지우기
    act(() => {
      result.current.clearState('test1')
    })

    expect(result.current.isLoading('test1')).toBe(false)
    expect(result.current.isLoading('test2')).toBe(true)
    expect(result.current.hasError('test1')).toBe(false)
  })

  it('모든 상태를 지울 수 있다', () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    // 상태 설정
    act(() => {
      result.current.setLoadingState('test1', true)
      result.current.setLoadingState('test2', true)
      result.current.setErrorState('test1', new ApiServiceError('오류'))
    })

    // 모든 상태 지우기
    act(() => {
      result.current.clearState()
    })

    expect(result.current.loading).toEqual({})
    expect(result.current.errors).toEqual({})
  })

  it('재시도 기능이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useApiService(), {
      wrapper: TestWrapper,
    })

    let callCount = 0
    const mockApiCall = vi.fn().mockImplementation(() => {
      callCount++
      if (callCount < 3) {
        return Promise.reject(new Error('일시적 오류'))
      }
      return Promise.resolve('성공')
    })

    await act(async () => {
      const response = await result.current.retry(mockApiCall, 'test', 3)
      expect(response).toBe('성공')
    })

    expect(mockApiCall).toHaveBeenCalledTimes(3)
  })
})

describe('useApiOperation 훅', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useToast as any).mockReturnValue(mockToast)
  })

  it('API 작업이 올바르게 실행된다', async () => {
    const mockApiCall = vi.fn().mockResolvedValue('작업 결과')
    
    const { result } = renderHook(
      () => useApiOperation(mockApiCall, {
        successMessage: '작업 완료',
        errorContext: 'testOperation',
      }),
      { wrapper: TestWrapper }
    )

    await act(async () => {
      const response = await result.current.execute('테스트 파라미터')
      expect(response).toBe('작업 결과')
    })

    expect(mockApiCall).toHaveBeenCalledWith('테스트 파라미터')
    expect(result.current.isLoading).toBe(false)
    expect(result.current.hasError).toBe(false)
  })

  it('API 작업 실패가 올바르게 처리된다', async () => {
    const testError = new ApiServiceError('작업 실패')
    const mockApiCall = vi.fn().mockRejectedValue(testError)
    
    const { result } = renderHook(
      () => useApiOperation(mockApiCall, {
        errorContext: 'testOperation',
      }),
      { wrapper: TestWrapper }
    )

    await act(async () => {
      const response = await result.current.execute('테스트 파라미터')
      expect(response).toBeNull()
    })

    expect(result.current.hasError).toBe(true)
    expect(result.current.error).toBeInstanceOf(ApiServiceError)
  })
})

describe('useServiceControl 훅', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useToast as any).mockReturnValue(mockToast)
  })

  it('서비스 시작이 올바르게 작동한다', async () => {
    const mockStartService = vi.mocked(apiService.startService)
    mockStartService.mockResolvedValue({ success: true, message: '시작됨' })

    const { result } = renderHook(() => useServiceControl(), {
      wrapper: TestWrapper,
    })

    await act(async () => {
      const response = await result.current.startService.execute('test-service')
      expect(response).toEqual({ success: true, message: '시작됨' })
    })

    expect(mockStartService).toHaveBeenCalledWith('test-service')
    expect(result.current.startService.isLoading).toBe(false)
  })

  it('서비스 중지가 올바르게 작동한다', async () => {
    const mockStopService = vi.mocked(apiService.stopService)
    mockStopService.mockResolvedValue({ success: true, message: '중지됨' })

    const { result } = renderHook(() => useServiceControl(), {
      wrapper: TestWrapper,
    })

    await act(async () => {
      const response = await result.current.stopService.execute('test-service')
      expect(response).toEqual({ success: true, message: '중지됨' })
    })

    expect(mockStopService).toHaveBeenCalledWith('test-service')
  })

  it('서비스 재시작이 올바르게 작동한다', async () => {
    const mockRestartService = vi.mocked(apiService.restartService)
    mockRestartService.mockResolvedValue({ success: true, message: '재시작됨' })

    const { result } = renderHook(() => useServiceControl(), {
      wrapper: TestWrapper,
    })

    await act(async () => {
      const response = await result.current.restartService.execute('test-service')
      expect(response).toEqual({ success: true, message: '재시작됨' })
    })

    expect(mockRestartService).toHaveBeenCalledWith('test-service')
  })

  it('서비스 제어 실패가 올바르게 처리된다', async () => {
    const mockStartService = vi.mocked(apiService.startService)
    const testError = new ApiServiceError('서비스 시작 실패', 500)
    mockStartService.mockRejectedValue(testError)

    const { result } = renderHook(() => useServiceControl(), {
      wrapper: TestWrapper,
    })

    await act(async () => {
      const response = await result.current.startService.execute('test-service')
      expect(response).toBeNull()
    })

    expect(result.current.startService.hasError).toBe(true)
    expect(result.current.startService.error).toBeInstanceOf(ApiServiceError)
  })

  it('여러 서비스 작업을 동시에 실행할 수 있다', async () => {
    const mockStartService = vi.mocked(apiService.startService)
    const mockStopService = vi.mocked(apiService.stopService)
    
    mockStartService.mockResolvedValue({ success: true, message: '시작됨' })
    mockStopService.mockResolvedValue({ success: true, message: '중지됨' })

    const { result } = renderHook(() => useServiceControl(), {
      wrapper: TestWrapper,
    })

    await act(async () => {
      const [startResult, stopResult] = await Promise.all([
        result.current.startService.execute('service1'),
        result.current.stopService.execute('service2'),
      ])

      expect(startResult).toEqual({ success: true, message: '시작됨' })
      expect(stopResult).toEqual({ success: true, message: '중지됨' })
    })

    expect(mockStartService).toHaveBeenCalledWith('service1')
    expect(mockStopService).toHaveBeenCalledWith('service2')
  })
})