import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useServiceStatus } from '../useServiceStatus'
import { ServiceInfo } from '../../types'
import { apiService } from '../../services/api'

// API 서비스 모킹
vi.mock('../../services/api', () => ({
  apiService: {
    getServices: vi.fn(),
    startService: vi.fn(),
    stopService: vi.fn(),
    restartService: vi.fn()
  }
}))

// WebSocket 훅 모킹
vi.mock('../useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    lastMessage: null,
    connectionStatus: 'connected',
    sendMessage: vi.fn(),
    disconnect: vi.fn()
  }))
}))

// 테스트용 서비스 데이터
const mockServices: ServiceInfo[] = [
  {
    id: 'posco-news',
    name: 'POSCO 뉴스',
    description: 'POSCO 뉴스 모니터링 서비스',
    status: 'running',
    uptime: 7200,
    config: {}
  },
  {
    id: 'github-pages',
    name: 'GitHub Pages',
    description: 'GitHub Pages 모니터링 서비스',
    status: 'stopped',
    config: {}
  },
  {
    id: 'cache-monitor',
    name: '캐시 모니터',
    description: '데이터 캐시 모니터링 서비스',
    status: 'error',
    last_error: '연결 시간 초과',
    config: {}
  },
  {
    id: 'webhook-service',
    name: '웹훅 서비스',
    description: '웹훅 전송 서비스',
    status: 'starting',
    config: {}
  }
]

// 테스트용 래퍼 컴포넌트
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0
      },
      mutations: {
        retry: false
      }
    }
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('useServiceStatus', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // 기본 API 응답 설정
    vi.mocked(apiService.getServices).mockResolvedValue(mockServices)
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('기본 기능', () => {
    it('서비스 목록을 올바르게 로드한다', async () => {
      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      // 초기 로딩 상태 확인
      expect(result.current.isLoading).toBe(true)
      expect(result.current.services).toEqual([])

      // 데이터 로드 완료 대기
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // 서비스 목록 확인
      expect(result.current.services).toEqual(mockServices)
      expect(apiService.getServices).toHaveBeenCalledTimes(1)
    })

    it('서비스 통계를 올바르게 계산한다', async () => {
      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      const stats = result.current.serviceStats
      expect(stats.total).toBe(4)
      expect(stats.running).toBe(1)
      expect(stats.stopped).toBe(1)
      expect(stats.error).toBe(1)
      expect(stats.transitioning).toBe(1)
    })

    it('특정 서비스를 올바르게 조회한다', async () => {
      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      const service = result.current.getService('posco-news')
      expect(service).toEqual(mockServices[0])

      const nonExistentService = result.current.getService('non-existent')
      expect(nonExistentService).toBeUndefined()
    })
  })

  describe('서비스 제어', () => {
    it('서비스를 성공적으로 시작한다', async () => {
      const mockStartResponse = {
        message: '서비스가 시작되었습니다',
        service: { ...mockServices[1], status: 'running' as const }
      }
      vi.mocked(apiService.startService).mockResolvedValue(mockStartResponse)

      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      let controlResult: any
      await act(async () => {
        controlResult = await result.current.startService('github-pages')
      })

      expect(controlResult.success).toBe(true)
      expect(controlResult.message).toBe('서비스가 시작되었습니다')
      expect(apiService.startService).toHaveBeenCalledWith('github-pages')
    })

    it('서비스를 성공적으로 중지한다', async () => {
      const mockStopResponse = {
        message: '서비스가 중지되었습니다',
        service: { ...mockServices[0], status: 'stopped' as const }
      }
      vi.mocked(apiService.stopService).mockResolvedValue(mockStopResponse)

      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      let controlResult: any
      await act(async () => {
        controlResult = await result.current.stopService('posco-news')
      })

      expect(controlResult.success).toBe(true)
      expect(controlResult.message).toBe('서비스가 중지되었습니다')
      expect(apiService.stopService).toHaveBeenCalledWith('posco-news')
    })

    it('서비스를 성공적으로 재시작한다', async () => {
      const mockRestartResponse = {
        message: '서비스가 재시작되었습니다',
        service: { ...mockServices[0], status: 'running' as const }
      }
      vi.mocked(apiService.restartService).mockResolvedValue(mockRestartResponse)

      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      let controlResult: any
      await act(async () => {
        controlResult = await result.current.restartService('posco-news')
      })

      expect(controlResult.success).toBe(true)
      expect(controlResult.message).toBe('서비스가 재시작되었습니다')
      expect(apiService.restartService).toHaveBeenCalledWith('posco-news')
    })

    it('서비스 제어 실패 시 오류를 처리한다', async () => {
      const errorMessage = '서비스 시작 실패'
      vi.mocked(apiService.startService).mockRejectedValue(new Error(errorMessage))

      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      let controlResult: any
      await act(async () => {
        controlResult = await result.current.startService('github-pages')
      })

      expect(controlResult.success).toBe(false)
      expect(controlResult.message).toBe(errorMessage)
    })
  })

  describe('서비스 제어 상태 관리', () => {
    it('서비스 제어 중 상태를 올바르게 추적한다', async () => {
      // 지연된 응답을 시뮬레이션
      let resolveStart: (value: any) => void
      const startPromise = new Promise(resolve => {
        resolveStart = resolve
      })
      vi.mocked(apiService.startService).mockReturnValue(startPromise)

      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // 서비스 시작 요청
      act(() => {
        result.current.startService('github-pages')
      })

      // 제어 중 상태 확인
      await waitFor(() => {
        expect(result.current.isServiceControlling('github-pages')).toBe(true)
        expect(result.current.isStarting).toBe(true)
      })

      // 요청 완료
      act(() => {
        resolveStart({
          message: '서비스가 시작되었습니다',
          service: { ...mockServices[1], status: 'running' }
        })
      })

      // 제어 완료 상태 확인
      await waitFor(() => {
        expect(result.current.isServiceControlling('github-pages')).toBe(false)
        expect(result.current.isStarting).toBe(false)
      })
    })

    it('서비스 제어 가능 여부를 올바르게 판단한다', async () => {
      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // 일반 서비스는 제어 가능
      expect(result.current.canControlService(mockServices[0])).toBe(true)
      expect(result.current.canControlService(mockServices[1])).toBe(true)
      expect(result.current.canControlService(mockServices[2])).toBe(true)

      // 전환 중인 서비스는 제어 불가능
      expect(result.current.canControlService(mockServices[3])).toBe(false)
    })
  })

  describe('자동 새로고침', () => {
    it('자동 새로고침이 활성화되면 주기적으로 데이터를 업데이트한다', async () => {
      vi.useFakeTimers()

      const { result } = renderHook(() => useServiceStatus({
        autoRefresh: true,
        refreshInterval: 1000
      }), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // 초기 호출
      expect(apiService.getServices).toHaveBeenCalledTimes(1)

      // 1초 후 자동 새로고침
      act(() => {
        vi.advanceTimersByTime(1000)
      })

      await waitFor(() => {
        expect(apiService.getServices).toHaveBeenCalledTimes(2)
      })

      vi.useRealTimers()
    })

    it('자동 새로고침이 비활성화되면 주기적 업데이트를 하지 않는다', async () => {
      vi.useFakeTimers()

      const { result } = renderHook(() => useServiceStatus({
        autoRefresh: false
      }), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // 초기 호출
      expect(apiService.getServices).toHaveBeenCalledTimes(1)

      // 시간이 지나도 추가 호출 없음
      act(() => {
        vi.advanceTimersByTime(10000)
      })

      expect(apiService.getServices).toHaveBeenCalledTimes(1)

      vi.useRealTimers()
    })
  })

  describe('수동 새로고침', () => {
    it('수동 새로고침을 올바르게 실행한다', async () => {
      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // 초기 호출
      expect(apiService.getServices).toHaveBeenCalledTimes(1)

      // 수동 새로고침
      await act(async () => {
        await result.current.refreshServices()
      })

      expect(apiService.getServices).toHaveBeenCalledTimes(2)
    })
  })

  describe('오류 처리', () => {
    it('API 오류를 올바르게 처리한다', async () => {
      const errorMessage = '네트워크 연결 오류'
      vi.mocked(apiService.getServices).mockRejectedValue(new Error(errorMessage))

      const { result } = renderHook(() => useServiceStatus(), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.error).toBeTruthy()
      expect(result.current.error?.message).toBe(errorMessage)
      expect(result.current.services).toEqual([])
    })
  })

  describe('옵션 설정', () => {
    it('커스텀 옵션을 올바르게 적용한다', async () => {
      const { result } = renderHook(() => useServiceStatus({
        autoRefresh: false,
        refreshInterval: 10000,
        enableWebSocket: false
      }), {
        wrapper: createWrapper()
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // 기본 기능은 정상 작동
      expect(result.current.services).toEqual(mockServices)
    })
  })
})