import { useState, useEffect, useCallback, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ServiceInfo, ServiceStatus, WSMessage } from '../types'
import { apiService } from '../services/api'
import { useWebSocket } from './useWebSocket'

interface UseServiceStatusOptions {
  autoRefresh?: boolean
  refreshInterval?: number
  enableWebSocket?: boolean
}

interface ServiceControlResult {
  success: boolean
  message: string
  service?: ServiceInfo
}

export const useServiceStatus = (options: UseServiceStatusOptions = {}) => {
  const {
    autoRefresh = true,
    refreshInterval = 5000,
    enableWebSocket = true
  } = options

  const queryClient = useQueryClient()
  const [controllingServices, setControllingServices] = useState<Set<string>>(new Set())
  const lastUpdateRef = useRef<number>(Date.now())

  // 서비스 목록 조회 쿼리
  const {
    data: services = [],
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['services'],
    queryFn: apiService.getServices,
    refetchInterval: autoRefresh ? refreshInterval : false,
    staleTime: 1000,
    gcTime: 5 * 60 * 1000, // 5분
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  })

  // WebSocket 연결
  const { lastMessage, connectionStatus } = useWebSocket({
    url: 'ws://localhost:8000/ws',
    enableReconnect: enableWebSocket,
    maxReconnectAttempts: 5,
    reconnectInterval: 3000
  })

  // WebSocket 메시지 처리
  useEffect(() => {
    if (!lastMessage) return

    try {
      const message: WSMessage = typeof lastMessage === 'string' 
        ? JSON.parse(lastMessage) 
        : lastMessage

      // 서비스 이벤트 처리
      if (message.type === 'service_event' || message.type === 'status_update') {
        const now = Date.now()
        
        // 중복 업데이트 방지 (1초 이내 중복 업데이트 무시)
        if (now - lastUpdateRef.current < 1000) {
          return
        }
        
        lastUpdateRef.current = now

        // 서비스 목록 무효화 및 재조회
        queryClient.invalidateQueries({ queryKey: ['services'] })
      }
    } catch (error) {
      console.warn('WebSocket 메시지 파싱 오류:', error)
    }
  }, [lastMessage, queryClient])

  // 서비스 시작 뮤테이션
  const startServiceMutation = useMutation({
    mutationFn: (serviceId: string) => apiService.startService(serviceId),
    onMutate: async (serviceId) => {
      // 낙관적 업데이트
      setControllingServices(prev => new Set(prev).add(serviceId))
      
      await queryClient.cancelQueries({ queryKey: ['services'] })
      
      const previousServices = queryClient.getQueryData<ServiceInfo[]>(['services'])
      
      if (previousServices) {
        const updatedServices = previousServices.map(service =>
          service.id === serviceId
            ? { ...service, status: 'starting' as ServiceStatus }
            : service
        )
        queryClient.setQueryData(['services'], updatedServices)
      }
      
      return { previousServices }
    },
    onSuccess: () => {
      // 성공 시 서비스 목록 업데이트
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
    onError: (_error, _serviceId, context) => {
      // 오류 시 이전 상태로 롤백
      if (context?.previousServices) {
        queryClient.setQueryData(['services'], context.previousServices)
      }
    },
    onSettled: (_data, _error, serviceId) => {
      // 제어 상태 해제
      setControllingServices(prev => {
        const newSet = new Set(prev)
        newSet.delete(serviceId)
        return newSet
      })
    }
  })

  // 서비스 중지 뮤테이션
  const stopServiceMutation = useMutation({
    mutationFn: (serviceId: string) => apiService.stopService(serviceId),
    onMutate: async (serviceId) => {
      setControllingServices(prev => new Set(prev).add(serviceId))
      
      await queryClient.cancelQueries({ queryKey: ['services'] })
      
      const previousServices = queryClient.getQueryData<ServiceInfo[]>(['services'])
      
      if (previousServices) {
        const updatedServices = previousServices.map(service =>
          service.id === serviceId
            ? { ...service, status: 'stopping' as ServiceStatus }
            : service
        )
        queryClient.setQueryData(['services'], updatedServices)
      }
      
      return { previousServices }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
    onError: (_error, _serviceId, context) => {
      if (context?.previousServices) {
        queryClient.setQueryData(['services'], context.previousServices)
      }
    },
    onSettled: (_data, _error, serviceId) => {
      setControllingServices(prev => {
        const newSet = new Set(prev)
        newSet.delete(serviceId)
        return newSet
      })
    }
  })

  // 서비스 재시작 뮤테이션
  const restartServiceMutation = useMutation({
    mutationFn: (serviceId: string) => apiService.restartService(serviceId),
    onMutate: async (serviceId) => {
      setControllingServices(prev => new Set(prev).add(serviceId))
      
      await queryClient.cancelQueries({ queryKey: ['services'] })
      
      const previousServices = queryClient.getQueryData<ServiceInfo[]>(['services'])
      
      if (previousServices) {
        const updatedServices = previousServices.map(service =>
          service.id === serviceId
            ? { ...service, status: 'stopping' as ServiceStatus }
            : service
        )
        queryClient.setQueryData(['services'], updatedServices)
      }
      
      return { previousServices }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
    onError: (_error, _serviceId, context) => {
      if (context?.previousServices) {
        queryClient.setQueryData(['services'], context.previousServices)
      }
    },
    onSettled: (_data, _error, serviceId) => {
      setControllingServices(prev => {
        const newSet = new Set(prev)
        newSet.delete(serviceId)
        return newSet
      })
    }
  })

  // 서비스 제어 함수들
  const startService = useCallback(async (serviceId: string): Promise<ServiceControlResult> => {
    try {
      const result = await startServiceMutation.mutateAsync(serviceId)
      return {
        success: true,
        message: result.message,
        service: result.service
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '서비스 시작 중 오류가 발생했습니다'
      }
    }
  }, [startServiceMutation])

  const stopService = useCallback(async (serviceId: string): Promise<ServiceControlResult> => {
    try {
      const result = await stopServiceMutation.mutateAsync(serviceId)
      return {
        success: true,
        message: result.message,
        service: result.service
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '서비스 중지 중 오류가 발생했습니다'
      }
    }
  }, [stopServiceMutation])

  const restartService = useCallback(async (serviceId: string): Promise<ServiceControlResult> => {
    try {
      const result = await restartServiceMutation.mutateAsync(serviceId)
      return {
        success: true,
        message: result.message,
        service: result.service
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '서비스 재시작 중 오류가 발생했습니다'
      }
    }
  }, [restartServiceMutation])

  // 서비스 상태 확인 함수
  const isServiceControlling = useCallback((serviceId: string): boolean => {
    return controllingServices.has(serviceId)
  }, [controllingServices])

  const canControlService = useCallback((service: ServiceInfo): boolean => {
    return !controllingServices.has(service.id) && 
           !['starting', 'stopping'].includes(service.status)
  }, [controllingServices])

  // 서비스 통계 계산
  const serviceStats = useCallback(() => {
    const stats = {
      total: services.length,
      running: 0,
      stopped: 0,
      error: 0,
      transitioning: 0
    }

    services.forEach(service => {
      switch (service.status) {
        case 'running':
          stats.running++
          break
        case 'stopped':
          stats.stopped++
          break
        case 'error':
          stats.error++
          break
        case 'starting':
        case 'stopping':
          stats.transitioning++
          break
      }
    })

    return stats
  }, [services])

  // 특정 서비스 조회
  const getService = useCallback((serviceId: string): ServiceInfo | undefined => {
    return services.find(service => service.id === serviceId)
  }, [services])

  // 서비스 목록 새로고침
  const refreshServices = useCallback(() => {
    return refetch()
  }, [refetch])

  return {
    // 데이터
    services,
    serviceStats: serviceStats(),
    
    // 상태
    isLoading,
    error: error as Error | null,
    connectionStatus,
    controllingServices: Array.from(controllingServices),
    
    // 제어 함수
    startService,
    stopService,
    restartService,
    refreshServices,
    
    // 유틸리티 함수
    isServiceControlling,
    canControlService,
    getService,
    
    // 뮤테이션 상태
    isStarting: startServiceMutation.isPending,
    isStopping: stopServiceMutation.isPending,
    isRestarting: restartServiceMutation.isPending,
    
    // 뮤테이션 오류
    startError: startServiceMutation.error as Error | null,
    stopError: stopServiceMutation.error as Error | null,
    restartError: restartServiceMutation.error as Error | null
  }
}