/**
 * API 서비스 사용을 위한 커스텀 훅
 * 에러 처리, 로딩 상태, 토스트 알림 등을 통합 관리
 */

import { useState, useCallback } from 'react'
import { useToast } from '@chakra-ui/react'
import { apiService, ApiServiceError } from '../services/api'
import { handleQueryError, getRecoveryStrategy } from '../services/errorHandler'

// 로딩 상태 타입
interface LoadingState {
  [key: string]: boolean
}

// 에러 상태 타입
interface ErrorState {
  [key: string]: ApiServiceError | null
}

/**
 * API 서비스 통합 관리 훅
 */
export const useApiService = () => {
  const [loading, setLoading] = useState<LoadingState>({})
  const [errors, setErrors] = useState<ErrorState>({})
  const toast = useToast()

  // 로딩 상태 설정
  const setLoadingState = useCallback((key: string, isLoading: boolean) => {
    setLoading(prev => ({ ...prev, [key]: isLoading }))
  }, [])

  // 에러 상태 설정
  const setErrorState = useCallback((key: string, error: ApiServiceError | null) => {
    setErrors(prev => ({ ...prev, [key]: error }))
  }, [])

  // 에러 처리 및 토스트 표시
  const handleError = useCallback((error: unknown, context: string, showToast = true) => {
    const toastMessage = handleQueryError(error, context)
    
    if (showToast) {
      toast({
        title: toastMessage.title,
        description: toastMessage.description,
        status: toastMessage.status,
        duration: toastMessage.duration,
        isClosable: toastMessage.isClosable,
      })
    }

    if (error instanceof ApiServiceError) {
      setErrorState(context, error)
    }
  }, [toast, setErrorState])

  // 성공 토스트 표시
  const showSuccessToast = useCallback((title: string, description?: string) => {
    toast({
      title,
      description,
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
  }, [toast])

  // API 호출 래퍼 함수
  const callApi = useCallback(async <T>(
    apiCall: () => Promise<T>,
    options: {
      loadingKey: string
      successMessage?: string
      errorContext?: string
      showErrorToast?: boolean
      onSuccess?: (data: T) => void
      onError?: (error: unknown) => void
    }
  ): Promise<T | null> => {
    const {
      loadingKey,
      successMessage,
      errorContext = loadingKey,
      showErrorToast = true,
      onSuccess,
      onError
    } = options

    try {
      setLoadingState(loadingKey, true)
      setErrorState(errorContext, null)

      const result = await apiCall()

      if (successMessage) {
        showSuccessToast(successMessage)
      }

      onSuccess?.(result)
      return result

    } catch (error) {
      handleError(error, errorContext, showErrorToast)
      onError?.(error)
      return null

    } finally {
      setLoadingState(loadingKey, false)
    }
  }, [setLoadingState, setErrorState, handleError, showSuccessToast])

  // 재시도 함수
  const retry = useCallback(async <T>(
    apiCall: () => Promise<T>,
    context: string,
    maxRetries = 3
  ): Promise<T | null> => {
    let lastError: unknown = null
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall()
      } catch (error) {
        lastError = error
        
        if (attempt < maxRetries) {
          const recovery = getRecoveryStrategy(error)
          if (recovery.canRetry && recovery.retryDelay) {
            await new Promise(resolve => setTimeout(resolve, recovery.retryDelay))
          } else {
            break // 재시도 불가능한 에러
          }
        }
      }
    }

    // 모든 재시도 실패
    handleError(lastError, `${context} (${maxRetries}회 재시도 실패)`)
    return null
  }, [handleError])

  // 상태 초기화
  const clearState = useCallback((key?: string) => {
    if (key) {
      setLoadingState(key, false)
      setErrorState(key, null)
    } else {
      setLoading({})
      setErrors({})
    }
  }, [setLoadingState, setErrorState])

  return {
    // 상태
    loading,
    errors,
    
    // 유틸리티 함수
    callApi,
    retry,
    clearState,
    handleError,
    showSuccessToast,
    
    // 개별 상태 관리
    setLoadingState,
    setErrorState,
    
    // 상태 확인 헬퍼
    isLoading: (key: string) => loading[key] || false,
    hasError: (key: string) => errors[key] !== null,
    getError: (key: string) => errors[key] || null,
  }
}

/**
 * 특정 API 작업을 위한 전용 훅
 */
export const useApiOperation = <T, P = void>(
  apiCall: (params: P) => Promise<T>,
  options?: {
    successMessage?: string
    errorContext?: string
    showErrorToast?: boolean
    onSuccess?: (data: T, params: P) => void
    onError?: (error: unknown, params: P) => void
  }
) => {
  const { callApi, isLoading, hasError, getError } = useApiService()
  const operationKey = options?.errorContext || 'operation'

  const execute = useCallback(async (params: P): Promise<T | null> => {
    return callApi(
      () => apiCall(params),
      {
        loadingKey: operationKey,
        successMessage: options?.successMessage,
        errorContext: options?.errorContext || operationKey,
        showErrorToast: options?.showErrorToast,
        onSuccess: options?.onSuccess ? (data) => options.onSuccess!(data, params) : undefined,
        onError: options?.onError ? (error) => options.onError!(error, params) : undefined,
      }
    )
  }, [callApi, apiCall, operationKey, options])

  return {
    execute,
    isLoading: isLoading(operationKey),
    hasError: hasError(operationKey),
    error: getError(operationKey),
  }
}

/**
 * 서비스 제어를 위한 전용 훅
 */
export const useServiceControl = () => {
  const startService = useApiOperation(
    (serviceId: string) => apiService.startService(serviceId),
    {
      successMessage: '서비스가 성공적으로 시작되었습니다',
      errorContext: 'startService',
    }
  )

  const stopService = useApiOperation(
    (serviceId: string) => apiService.stopService(serviceId),
    {
      successMessage: '서비스가 성공적으로 중지되었습니다',
      errorContext: 'stopService',
    }
  )

  const restartService = useApiOperation(
    (serviceId: string) => apiService.restartService(serviceId),
    {
      successMessage: '서비스가 성공적으로 재시작되었습니다',
      errorContext: 'restartService',
    }
  )

  return {
    startService,
    stopService,
    restartService,
  }
}

/**
 * 웹훅 관리를 위한 전용 훅
 */
export const useWebhookControl = () => {
  const sendWebhook = useApiOperation(
    (payload: Parameters<typeof apiService.sendWebhook>[0]) => apiService.sendWebhook(payload),
    {
      successMessage: '웹훅이 성공적으로 전송되었습니다',
      errorContext: 'sendWebhook',
    }
  )

  const createTemplate = useApiOperation(
    (template: Parameters<typeof apiService.createWebhookTemplate>[0]) => apiService.createWebhookTemplate(template),
    {
      successMessage: '웹훅 템플릿이 생성되었습니다',
      errorContext: 'createWebhookTemplate',
    }
  )

  const updateTemplate = useApiOperation(
    ({ templateId, template }: { templateId: string; template: Parameters<typeof apiService.updateWebhookTemplate>[1] }) => 
      apiService.updateWebhookTemplate(templateId, template),
    {
      successMessage: '웹훅 템플릿이 수정되었습니다',
      errorContext: 'updateWebhookTemplate',
    }
  )

  const deleteTemplate = useApiOperation(
    (templateId: string) => apiService.deleteWebhookTemplate(templateId),
    {
      successMessage: '웹훅 템플릿이 삭제되었습니다',
      errorContext: 'deleteWebhookTemplate',
    }
  )

  return {
    sendWebhook,
    createTemplate,
    updateTemplate,
    deleteTemplate,
  }
}

/**
 * POSCO 시스템 제어를 위한 전용 훅
 */
export const usePoscoControl = () => {
  const switchBranch = useApiOperation(
    (branch: string) => apiService.switchPoscoBranch(branch),
    {
      successMessage: '브랜치가 성공적으로 전환되었습니다',
      errorContext: 'switchPoscoBranch',
    }
  )

  const deploy = useApiOperation(
    (options?: Parameters<typeof apiService.deployPosco>[0]) => apiService.deployPosco(options),
    {
      successMessage: '배포가 시작되었습니다',
      errorContext: 'deployPosco',
    }
  )

  return {
    switchBranch,
    deploy,
  }
}

/**
 * 연결 상태 확인을 위한 훅
 */
export const useConnectionStatus = () => {
  const testConnection = useApiOperation(
    () => apiService.testConnection(),
    {
      errorContext: 'connectionTest',
      showErrorToast: false, // 연결 테스트는 조용히 실행
    }
  )

  const healthCheck = useApiOperation(
    () => apiService.healthCheck(),
    {
      errorContext: 'healthCheck',
      showErrorToast: false, // 헬스 체크는 조용히 실행
    }
  )

  return {
    testConnection,
    healthCheck,
  }
}