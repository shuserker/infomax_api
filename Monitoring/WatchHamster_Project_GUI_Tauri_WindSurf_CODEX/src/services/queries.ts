/**
 * React Query를 위한 API 쿼리 훅들
 * API 서비스와 React Query를 연결하는 레이어
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query'
import { apiService, ApiServiceError } from './api'
import type {
  ServiceInfo,
  SystemMetrics,
  PerformanceMetrics,
  StabilityMetrics,
  WebhookTemplate,
  WebhookPayload,
  LogFilter,
  ServiceAction
} from '../types'

// ===================
// 쿼리 키 팩토리
// ===================

export const queryKeys = {
  // 서비스 관련
  services: ['services'] as const,
  service: (id: string) => ['services', id] as const,
  
  // 메트릭 관련
  systemMetrics: ['metrics', 'system'] as const,
  performanceMetrics: (timeRange?: string) => ['metrics', 'performance', timeRange] as const,
  stabilityMetrics: ['metrics', 'stability'] as const,
  metricsHistory: (params?: any) => ['metrics', 'history', params] as const,
  
  // 웹훅 관련
  webhookTemplates: (type?: string) => ['webhooks', 'templates', type] as const,
  webhookTemplate: (id: string) => ['webhooks', 'templates', id] as const,
  webhookHistory: (params?: any) => ['webhooks', 'history', params] as const,
  webhookStatus: (id: string) => ['webhooks', 'status', id] as const,
  
  // 로그 관련
  logs: (filter?: LogFilter) => ['logs', filter] as const,
  
  // POSCO 관련
  poscoStatus: ['posco', 'status'] as const,
  
  // 헬스 체크
  health: ['health'] as const,
  serverInfo: ['server', 'info'] as const,
  connection: ['connection'] as const,
} as const

// ===================
// 서비스 관련 훅
// ===================

/**
 * 모든 서비스 목록 조회
 */
export const useServices = (options?: UseQueryOptions<ServiceInfo[], ApiServiceError>) => {
  return useQuery({
    queryKey: queryKeys.services,
    queryFn: () => apiService.getServices(),
    staleTime: 30 * 1000, // 30초
    refetchInterval: 5 * 1000, // 5초마다 자동 새로고침
    ...options,
  })
}

/**
 * 특정 서비스 정보 조회
 */
export const useService = (
  serviceId: string,
  options?: UseQueryOptions<ServiceInfo, ApiServiceError>
) => {
  return useQuery({
    queryKey: queryKeys.service(serviceId),
    queryFn: () => apiService.getService(serviceId),
    enabled: !!serviceId,
    staleTime: 10 * 1000, // 10초
    ...options,
  })
}

/**
 * 서비스 시작 뮤테이션
 */
export const useStartService = (options?: UseMutationOptions<
  { message: string; service: ServiceInfo },
  ApiServiceError,
  string
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (serviceId: string) => apiService.startService(serviceId),
    onSuccess: (_, serviceId) => {
      // 서비스 목록과 개별 서비스 캐시 무효화
      queryClient.invalidateQueries({ queryKey: queryKeys.services })
      queryClient.invalidateQueries({ queryKey: queryKeys.service(serviceId) })
      
      // 시스템 메트릭도 업데이트
      queryClient.invalidateQueries({ queryKey: queryKeys.systemMetrics })
    },
    ...options,
  })
}

/**
 * 서비스 중지 뮤테이션
 */
export const useStopService = (options?: UseMutationOptions<
  { message: string; service: ServiceInfo },
  ApiServiceError,
  string
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (serviceId: string) => apiService.stopService(serviceId),
    onSuccess: (_, serviceId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.services })
      queryClient.invalidateQueries({ queryKey: queryKeys.service(serviceId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.systemMetrics })
    },
    ...options,
  })
}

/**
 * 서비스 재시작 뮤테이션
 */
export const useRestartService = (options?: UseMutationOptions<
  { message: string; service: ServiceInfo },
  ApiServiceError,
  string
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (serviceId: string) => apiService.restartService(serviceId),
    onSuccess: (_, serviceId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.services })
      queryClient.invalidateQueries({ queryKey: queryKeys.service(serviceId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.systemMetrics })
    },
    ...options,
  })
}

/**
 * 여러 서비스 일괄 제어 뮤테이션
 */
export const useControlServices = (options?: UseMutationOptions<
  { results: Array<{ service_id: string; success: boolean; message: string }> },
  ApiServiceError,
  ServiceAction[]
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (actions: ServiceAction[]) => apiService.controlServices(actions),
    onSuccess: () => {
      // 모든 서비스 관련 캐시 무효화
      queryClient.invalidateQueries({ queryKey: queryKeys.services })
      queryClient.invalidateQueries({ queryKey: queryKeys.systemMetrics })
    },
    ...options,
  })
}

// ===================
// 메트릭 관련 훅
// ===================

/**
 * 시스템 메트릭 조회
 */
export const useSystemMetrics = (options?: UseQueryOptions<SystemMetrics, ApiServiceError>) => {
  return useQuery({
    queryKey: queryKeys.systemMetrics,
    queryFn: () => apiService.getSystemMetrics(),
    staleTime: 5 * 1000, // 5초
    refetchInterval: 5 * 1000, // 5초마다 자동 새로고침
    ...options,
  })
}

/**
 * 성능 메트릭 조회
 */
export const usePerformanceMetrics = (
  timeRange?: '1h' | '6h' | '24h' | '7d',
  options?: UseQueryOptions<PerformanceMetrics, ApiServiceError>
) => {
  return useQuery({
    queryKey: queryKeys.performanceMetrics(timeRange),
    queryFn: () => apiService.getPerformanceMetrics(timeRange),
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30 * 1000, // 30초마다 자동 새로고침
    ...options,
  })
}

/**
 * 안정성 메트릭 조회
 */
export const useStabilityMetrics = (options?: UseQueryOptions<StabilityMetrics, ApiServiceError>) => {
  return useQuery({
    queryKey: queryKeys.stabilityMetrics,
    queryFn: () => apiService.getStabilityMetrics(),
    staleTime: 60 * 1000, // 1분
    refetchInterval: 60 * 1000, // 1분마다 자동 새로고침
    ...options,
  })
}

/**
 * 메트릭 히스토리 조회
 */
export const useMetricsHistory = (
  params?: {
    limit?: number
    start_time?: string
    end_time?: string
    metrics?: string[]
  },
  options?: UseQueryOptions<any, ApiServiceError>
) => {
  return useQuery({
    queryKey: queryKeys.metricsHistory(params),
    queryFn: () => apiService.getMetricsHistory(params),
    staleTime: 5 * 60 * 1000, // 5분
    ...options,
  })
}

// ===================
// 웹훅 관련 훅
// ===================

/**
 * 웹훅 템플릿 목록 조회
 */
export const useWebhookTemplates = (
  webhookType?: string,
  options?: UseQueryOptions<WebhookTemplate[], ApiServiceError>
) => {
  return useQuery({
    queryKey: queryKeys.webhookTemplates(webhookType),
    queryFn: () => apiService.getWebhookTemplates(webhookType),
    staleTime: 5 * 60 * 1000, // 5분
    ...options,
  })
}

/**
 * 특정 웹훅 템플릿 조회
 */
export const useWebhookTemplate = (
  templateId: string,
  options?: UseQueryOptions<WebhookTemplate, ApiServiceError>
) => {
  return useQuery({
    queryKey: queryKeys.webhookTemplate(templateId),
    queryFn: () => apiService.getWebhookTemplate(templateId),
    enabled: !!templateId,
    staleTime: 5 * 60 * 1000, // 5분
    ...options,
  })
}

/**
 * 웹훅 전송 뮤테이션
 */
export const useSendWebhook = (options?: UseMutationOptions<
  { message: string; webhook_id: string; status: 'success' | 'failed' },
  ApiServiceError,
  WebhookPayload
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (payload: WebhookPayload) => apiService.sendWebhook(payload),
    onSuccess: () => {
      // 웹훅 히스토리 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ['webhooks', 'history'] })
    },
    ...options,
  })
}

/**
 * 웹훅 템플릿 생성 뮤테이션
 */
export const useCreateWebhookTemplate = (options?: UseMutationOptions<
  WebhookTemplate,
  ApiServiceError,
  Omit<WebhookTemplate, 'id' | 'created_at' | 'updated_at'>
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (template) => apiService.createWebhookTemplate(template),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks', 'templates'] })
    },
    ...options,
  })
}

/**
 * 웹훅 템플릿 수정 뮤테이션
 */
export const useUpdateWebhookTemplate = (options?: UseMutationOptions<
  WebhookTemplate,
  ApiServiceError,
  { templateId: string; template: Partial<Omit<WebhookTemplate, 'id' | 'created_at' | 'updated_at'>> }
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ templateId, template }) => apiService.updateWebhookTemplate(templateId, template),
    onSuccess: (_, { templateId }) => {
      queryClient.invalidateQueries({ queryKey: ['webhooks', 'templates'] })
      queryClient.invalidateQueries({ queryKey: queryKeys.webhookTemplate(templateId) })
    },
    ...options,
  })
}

/**
 * 웹훅 템플릿 삭제 뮤테이션
 */
export const useDeleteWebhookTemplate = (options?: UseMutationOptions<
  { message: string },
  ApiServiceError,
  string
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (templateId: string) => apiService.deleteWebhookTemplate(templateId),
    onSuccess: (_, templateId) => {
      queryClient.invalidateQueries({ queryKey: ['webhooks', 'templates'] })
      queryClient.removeQueries({ queryKey: queryKeys.webhookTemplate(templateId) })
    },
    ...options,
  })
}

/**
 * 웹훅 히스토리 조회
 */
export const useWebhookHistory = (
  params?: {
    limit?: number
    page?: number
    webhook_type?: string
    status?: 'success' | 'failed' | 'pending'
    start_date?: string
    end_date?: string
  },
  options?: UseQueryOptions<any, ApiServiceError>
) => {
  return useQuery({
    queryKey: queryKeys.webhookHistory(params),
    queryFn: () => apiService.getWebhookHistory(params),
    staleTime: 30 * 1000, // 30초
    ...options,
  })
}

// ===================
// 로그 관련 훅
// ===================

/**
 * 로그 조회
 */
export const useLogs = (
  filter?: LogFilter & { limit?: number; page?: number },
  options?: UseQueryOptions<any, ApiServiceError>
) => {
  return useQuery({
    queryKey: queryKeys.logs(filter),
    queryFn: () => apiService.getLogs(filter),
    staleTime: 10 * 1000, // 10초
    ...options,
  })
}

// ===================
// POSCO 시스템 관련 훅
// ===================

/**
 * POSCO 시스템 상태 조회
 */
export const usePoscoStatus = (options?: UseQueryOptions<any, ApiServiceError>) => {
  return useQuery({
    queryKey: queryKeys.poscoStatus,
    queryFn: () => apiService.getPoscoStatus(),
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30 * 1000, // 30초마다 자동 새로고침
    ...options,
  })
}

/**
 * POSCO 브랜치 전환 뮤테이션
 */
export const useSwitchPoscoBranch = (options?: UseMutationOptions<
  { message: string; current_branch: string },
  ApiServiceError,
  string
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (branch: string) => apiService.switchPoscoBranch(branch),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.poscoStatus })
    },
    ...options,
  })
}

/**
 * POSCO 배포 뮤테이션
 */
export const useDeployPosco = (options?: UseMutationOptions<
  { message: string; deployment_id: string },
  ApiServiceError,
  { force?: boolean; backup?: boolean } | undefined
>) => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (deployOptions) => apiService.deployPosco(deployOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.poscoStatus })
      queryClient.invalidateQueries({ queryKey: queryKeys.services })
    },
    ...options,
  })
}

// ===================
// 헬스 체크 및 유틸리티 훅
// ===================

/**
 * 헬스 체크
 */
export const useHealthCheck = (options?: UseQueryOptions<any, ApiServiceError>) => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiService.healthCheck(),
    staleTime: 30 * 1000, // 30초
    refetchInterval: 60 * 1000, // 1분마다 자동 새로고침
    retry: 1, // 헬스 체크는 재시도 최소화
    ...options,
  })
}

/**
 * 연결 테스트
 */
export const useConnectionTest = (options?: UseQueryOptions<any, ApiServiceError>) => {
  return useQuery({
    queryKey: queryKeys.connection,
    queryFn: () => apiService.testConnection(),
    staleTime: 10 * 1000, // 10초
    retry: 1, // 연결 테스트는 재시도 최소화
    ...options,
  })
}

/**
 * 서버 정보 조회
 */
export const useServerInfo = (options?: UseQueryOptions<any, ApiServiceError>) => {
  return useQuery({
    queryKey: queryKeys.serverInfo,
    queryFn: () => apiService.getServerInfo(),
    staleTime: 5 * 60 * 1000, // 5분
    ...options,
  })
}

// ===================
// 유틸리티 함수
// ===================

/**
 * 모든 캐시 무효화
 */
export const useInvalidateAllQueries = () => {
  const queryClient = useQueryClient()
  
  return () => {
    queryClient.invalidateQueries()
  }
}

/**
 * 특정 쿼리 캐시 제거
 */
export const useRemoveQueries = () => {
  const queryClient = useQueryClient()
  
  return (queryKey: any[]) => {
    queryClient.removeQueries({ queryKey })
  }
}

/**
 * 쿼리 캐시 수동 업데이트
 */
export const useUpdateQueryData = () => {
  const queryClient = useQueryClient()
  
  return <T>(queryKey: any[], updater: (oldData: T | undefined) => T) => {
    queryClient.setQueryData(queryKey, updater)
  }
}