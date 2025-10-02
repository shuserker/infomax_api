import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { 
  useServices, 
  useSystemMetrics, 
  useLogs,
  useWebhookTemplates,
  usePoscoStatus 
} from '../queries'
import { apiService } from '../api'

// API 서비스 모킹
vi.mock('../api', () => ({
  apiService: {
    getServices: vi.fn(),
    getSystemMetrics: vi.fn(),
    getLogs: vi.fn(),
    getWebhookTemplates: vi.fn(),
    getPoscoStatus: vi.fn(),
  },
}))

const mockApiService = vi.mocked(apiService)

// 테스트용 QueryClient 생성
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false, // 테스트에서는 재시도 비활성화
      gcTime: 0, // 가비지 컬렉션 즉시 실행
    },
  },
})

// 테스트용 래퍼 컴포넌트
const createWrapper = (queryClient: QueryClient) => {
  return ({ children }: { children: React.ReactNode }) => {
    return React.createElement(QueryClientProvider, { client: queryClient }, children)
  }
}

describe('React Query 훅들', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    vi.clearAllMocks()
    queryClient = createTestQueryClient()
  })

  describe('useServices', () => {
    it('서비스 목록을 성공적으로 가져온다', async () => {
      const mockServices = [
        {
          id: 'service1',
          name: 'POSCO 뉴스',
          status: 'running' as const,
          uptime: 3600,
          description: '뉴스 모니터링 서비스',
        },
        {
          id: 'service2',
          name: 'GitHub Pages',
          status: 'stopped' as const,
          uptime: 0,
          description: 'GitHub Pages 모니터링',
        },
      ]

      mockApiService.getServices.mockResolvedValue(mockServices)

      const { result } = renderHook(() => useServices(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockServices)
      expect(mockApiService.getServices).toHaveBeenCalledTimes(1)
    })

    it('서비스 목록 가져오기 실패를 처리한다', async () => {
      const mockError = new Error('서비스 목록을 가져올 수 없습니다')
      mockApiService.getServices.mockRejectedValue(mockError)

      const { result } = renderHook(() => useServices(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toEqual(mockError)
      expect(result.current.data).toBeUndefined()
    })
  })

  describe('useSystemMetrics', () => {
    it('시스템 메트릭을 성공적으로 가져온다', async () => {
      const mockMetrics = {
        cpu_percent: 45.2,
        memory_percent: 67.8,
        disk_usage: 23.4,
        network_status: 'connected',
        connection_count: 5,
        uptime: 3600,
        active_services: 3,
        timestamp: '2024-01-01T12:00:00Z',
      }

      mockApiService.getSystemMetrics.mockResolvedValue(mockMetrics)

      const { result } = renderHook(() => useSystemMetrics(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockMetrics)
      expect(mockApiService.getSystemMetrics).toHaveBeenCalledTimes(1)
    })

    it('시스템 메트릭 가져오기 실패를 처리한다', async () => {
      const mockError = new Error('메트릭을 가져올 수 없습니다')
      mockApiService.getSystemMetrics.mockRejectedValue(mockError)

      const { result } = renderHook(() => useSystemMetrics(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toEqual(mockError)
    })
  })

  describe('useLogs', () => {
    it('로그를 성공적으로 가져온다', async () => {
      const mockLogs = {
        items: [
          {
            level: 'info' as const,
            message: '서비스 시작됨',
            timestamp: '2024-01-01T12:00:00Z',
            source: 'system',
          },
          {
            level: 'warning' as const,
            message: '메모리 사용량 높음',
            timestamp: '2024-01-01T12:01:00Z',
            source: 'monitor',
          },
        ],
        total: 2,
        page: 1,
        size: 50,
        pages: 1,
      }

      mockApiService.getLogs.mockResolvedValue(mockLogs)

      const { result } = renderHook(() => useLogs({ limit: 50, level: 'info' }), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockLogs)
      expect(mockApiService.getLogs).toHaveBeenCalledWith({ limit: 50, level: 'info' })
    })

    it('빈 필터로도 작동한다', async () => {
      const mockLogs = { items: [], total: 0, page: 1, size: 50, pages: 0 }
      mockApiService.getLogs.mockResolvedValue(mockLogs)

      const { result } = renderHook(() => useLogs(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(mockApiService.getLogs).toHaveBeenCalledWith({})
    })
  })

  describe('useWebhookTemplates', () => {
    it('웹훅 템플릿을 성공적으로 가져온다', async () => {
      const mockTemplates = [
        {
          id: 'template1',
          name: '서비스 알림',
          description: '서비스 상태 알림 템플릿',
          webhook_type: 'discord',
          template: '서비스 {{service_name}}이 {{status}}되었습니다.',
          created_at: '2024-01-01T12:00:00Z',
          updated_at: '2024-01-01T12:00:00Z',
        },
        {
          id: 'template2',
          name: '시스템 경고',
          description: '시스템 리소스 경고 템플릿',
          webhook_type: 'slack',
          template: '시스템 리소스 사용량이 {{threshold}}%를 초과했습니다.',
          created_at: '2024-01-01T12:00:00Z',
          updated_at: '2024-01-01T12:00:00Z',
        },
      ]

      mockApiService.getWebhookTemplates.mockResolvedValue(mockTemplates)

      const { result } = renderHook(() => useWebhookTemplates(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockTemplates)
      expect(mockApiService.getWebhookTemplates).toHaveBeenCalledTimes(1)
    })

    it('웹훅 템플릿 가져오기 실패를 처리한다', async () => {
      const mockError = new Error('템플릿을 가져올 수 없습니다')
      mockApiService.getWebhookTemplates.mockRejectedValue(mockError)

      const { result } = renderHook(() => useWebhookTemplates(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toEqual(mockError)
    })
  })

  describe('usePoscoStatus', () => {
    it('POSCO 상태를 성공적으로 가져온다', async () => {
      const mockStatus = {
        current_branch: 'main',
        last_deployment: '2024-01-01T12:00:00Z',
        deployment_status: 'success',
        git_status: {
          ahead: 0,
          behind: 0,
          modified: [],
          untracked: [],
        },
        services: {
          news_monitor: 'running',
          deployment_service: 'idle',
        },
      }

      mockApiService.getPoscoStatus.mockResolvedValue(mockStatus)

      const { result } = renderHook(() => usePoscoStatus(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toEqual(mockStatus)
      expect(mockApiService.getPoscoStatus).toHaveBeenCalledTimes(1)
    })

    it('POSCO 상태 가져오기 실패를 처리한다', async () => {
      const mockError = new Error('POSCO 상태를 가져올 수 없습니다')
      mockApiService.getPoscoStatus.mockRejectedValue(mockError)

      const { result } = renderHook(() => usePoscoStatus(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toEqual(mockError)
    })
  })

  describe('기본 기능 테스트', () => {
    it('쿼리 데이터를 수동으로 설정할 수 있다', () => {
      const testData = [{ id: 'test', name: '테스트', status: 'running' as const, uptime: 0, description: '테스트' }]
      
      queryClient.setQueryData(['services'], testData)

      const { result } = renderHook(() => useServices(), {
        wrapper: createWrapper(queryClient),
      })

      expect(result.current.data).toEqual(testData)
      expect(result.current.isSuccess).toBe(true)
    })

    it('에러 상태에서 재시도할 수 있다', async () => {
      const mockError = new Error('일시적 오류')
      mockApiService.getServices
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce([])

      const { result } = renderHook(() => useServices(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      // 재시도
      result.current.refetch()

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(mockApiService.getServices).toHaveBeenCalledTimes(2)
    })
  })
})