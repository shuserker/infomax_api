/**
 * API 에러 처리 유틸리티
 * 에러 타입별 처리 로직과 사용자 친화적 메시지 제공
 */

import { ApiServiceError } from './api'
import type { ToastMessage } from '../types'

// 에러 타입별 기본 메시지 (향후 사용 예정)
// const ERROR_MESSAGES: Record<string, string> = {
//   NETWORK_ERROR: '네트워크 연결을 확인해주세요',
//   TIMEOUT: '요청 시간이 초과되었습니다',
//   BAD_REQUEST: '잘못된 요청입니다',
//   UNAUTHORIZED: '인증이 필요합니다',
//   FORBIDDEN: '접근 권한이 없습니다',
//   NOT_FOUND: '요청한 리소스를 찾을 수 없습니다',
//   VALIDATION_ERROR: '입력 데이터를 확인해주세요',
//   RATE_LIMITED: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요',
//   INTERNAL_SERVER_ERROR: '서버 내부 오류가 발생했습니다',
//   BAD_GATEWAY: '게이트웨이 오류가 발생했습니다',
//   SERVICE_UNAVAILABLE: '서비스를 일시적으로 사용할 수 없습니다',
//   GATEWAY_TIMEOUT: '게이트웨이 시간 초과가 발생했습니다',
//   UNKNOWN_ERROR: '알 수 없는 오류가 발생했습니다',
// }

// 에러 심각도 레벨
export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical'

// 에러 정보 인터페이스
export interface ErrorInfo {
  message: string
  severity: ErrorSeverity
  code?: string
  details?: any
  retryable: boolean
  userAction?: string
}

/**
 * API 에러를 분석하여 사용자 친화적 정보로 변환
 */
export const analyzeError = (error: unknown): ErrorInfo => {
  // ApiServiceError 처리
  if (error instanceof ApiServiceError) {
    const severity = getSeverityFromError(error)
    const retryable = isRetryableError(error)
    const userAction = getUserActionFromError(error)

    return {
      message: error.message,
      severity,
      code: error.code,
      details: error.details,
      retryable,
      userAction,
    }
  }

  // 일반 Error 처리
  if (error instanceof Error) {
    return {
      message: error.message || '알 수 없는 오류가 발생했습니다',
      severity: 'medium',
      retryable: false,
    }
  }

  // 기타 에러 처리
  return {
    message: '예상치 못한 오류가 발생했습니다',
    severity: 'medium',
    retryable: false,
  }
}

/**
 * 에러 심각도 결정
 */
const getSeverityFromError = (error: ApiServiceError): ErrorSeverity => {
  if (!error.status) {
    // 네트워크 에러는 높은 심각도
    if (error.code === 'NETWORK_ERROR') return 'high'
    return 'medium'
  }

  switch (error.status) {
    case 400:
    case 422:
      return 'low' // 클라이언트 입력 오류
    case 401:
    case 403:
      return 'medium' // 인증/권한 오류
    case 404:
      return 'low' // 리소스 없음
    case 429:
      return 'medium' // 레이트 리미팅
    case 500:
    case 502:
    case 503:
    case 504:
      return 'high' // 서버 오류
    default:
      return 'medium'
  }
}

/**
 * 재시도 가능한 에러인지 확인
 */
const isRetryableError = (error: ApiServiceError): boolean => {
  if (error.code === 'NETWORK_ERROR') return true
  if (error.code === 'TIMEOUT') return true
  
  if (error.status) {
    // 서버 오류는 재시도 가능
    return [408, 429, 500, 502, 503, 504].includes(error.status)
  }
  
  return false
}

/**
 * 사용자 액션 제안
 */
const getUserActionFromError = (error: ApiServiceError): string | undefined => {
  switch (error.code) {
    case 'NETWORK_ERROR':
      return '백엔드 서버가 실행 중인지 확인하고 네트워크 연결을 점검해주세요'
    case 'TIMEOUT':
      return '잠시 후 다시 시도해주세요'
    case 'BAD_REQUEST':
    case 'VALIDATION_ERROR':
      return '입력 정보를 다시 확인해주세요'
    case 'UNAUTHORIZED':
      return '로그인이 필요합니다'
    case 'FORBIDDEN':
      return '관리자에게 권한을 요청해주세요'
    case 'NOT_FOUND':
      return '요청한 항목이 존재하는지 확인해주세요'
    case 'RATE_LIMITED':
      return '잠시 후 다시 시도해주세요'
    case 'INTERNAL_SERVER_ERROR':
    case 'BAD_GATEWAY':
    case 'SERVICE_UNAVAILABLE':
    case 'GATEWAY_TIMEOUT':
      return '관리자에게 문의하거나 잠시 후 다시 시도해주세요'
    default:
      return undefined
  }
}

/**
 * 에러를 토스트 메시지로 변환
 */
export const errorToToast = (error: unknown): ToastMessage => {
  const errorInfo = analyzeError(error)
  
  let status: ToastMessage['status'] = 'error'
  
  // 심각도에 따른 토스트 타입 결정
  switch (errorInfo.severity) {
    case 'low':
      status = 'warning'
      break
    case 'medium':
      status = 'error'
      break
    case 'high':
    case 'critical':
      status = 'error'
      break
  }

  return {
    title: '오류 발생',
    description: errorInfo.message + (errorInfo.userAction ? `\n\n${errorInfo.userAction}` : ''),
    status,
    duration: errorInfo.severity === 'critical' ? undefined : 5000, // critical 에러는 수동으로 닫기
    isClosable: true,
  }
}

/**
 * 에러 로깅 유틸리티
 */
export const logError = (error: unknown, context?: string) => {
  const errorInfo = analyzeError(error)
  
  const logData = {
    timestamp: new Date().toISOString(),
    context: context || 'Unknown',
    error: {
      message: errorInfo.message,
      code: errorInfo.code,
      severity: errorInfo.severity,
      details: errorInfo.details,
    },
    userAgent: navigator.userAgent,
    url: window.location.href,
  }

  // 개발 환경에서는 콘솔에 출력
  if (import.meta.env.DEV) {
    console.group(`🚨 Error Log - ${errorInfo.severity.toUpperCase()}`)
    console.error('Message:', errorInfo.message)
    console.error('Code:', errorInfo.code)
    console.error('Context:', context)
    console.error('Details:', errorInfo.details)
    console.error('Full Log:', logData)
    console.groupEnd()
  }

  // 프로덕션 환경에서는 에러 리포팅 서비스로 전송
  // TODO: 실제 에러 리포팅 서비스 연동 (예: Sentry, LogRocket 등)
  if (import.meta.env.PROD && errorInfo.severity === 'critical') {
    // sendToErrorReportingService(logData)
  }
}

/**
 * React Query 에러 처리 헬퍼
 */
export const handleQueryError = (error: unknown, context: string) => {
  logError(error, `React Query - ${context}`)
  return errorToToast(error)
}

/**
 * 뮤테이션 에러 처리 헬퍼
 */
export const handleMutationError = (error: unknown, context: string) => {
  logError(error, `Mutation - ${context}`)
  return errorToToast(error)
}

/**
 * 에러 복구 전략 제안
 */
export const getRecoveryStrategy = (error: unknown): {
  canRetry: boolean
  retryDelay?: number
  maxRetries?: number
  fallbackAction?: string
} => {
  const errorInfo = analyzeError(error)
  
  if (!errorInfo.retryable) {
    return {
      canRetry: false,
      fallbackAction: errorInfo.userAction,
    }
  }

  // 에러 타입별 복구 전략
  switch (errorInfo.code) {
    case 'NETWORK_ERROR':
      return {
        canRetry: true,
        retryDelay: 5000, // 5초 후 재시도
        maxRetries: 3,
        fallbackAction: '백엔드 서버 상태를 확인해주세요',
      }
    case 'TIMEOUT':
      return {
        canRetry: true,
        retryDelay: 2000, // 2초 후 재시도
        maxRetries: 2,
      }
    case 'RATE_LIMITED':
      return {
        canRetry: true,
        retryDelay: 10000, // 10초 후 재시도
        maxRetries: 1,
      }
    case 'INTERNAL_SERVER_ERROR':
    case 'BAD_GATEWAY':
    case 'SERVICE_UNAVAILABLE':
    case 'GATEWAY_TIMEOUT':
      return {
        canRetry: true,
        retryDelay: 3000, // 3초 후 재시도
        maxRetries: 2,
        fallbackAction: '문제가 지속되면 관리자에게 문의해주세요',
      }
    default:
      return {
        canRetry: true,
        retryDelay: 1000,
        maxRetries: 1,
      }
  }
}

/**
 * 에러 상태 관리를 위한 커스텀 훅에서 사용할 유틸리티
 */
export const createErrorState = (error: unknown) => ({
  hasError: true,
  error: analyzeError(error),
  toast: errorToToast(error),
  recovery: getRecoveryStrategy(error),
})

/**
 * 에러 초기화
 */
export const clearErrorState = () => ({
  hasError: false,
  error: null,
  toast: null,
  recovery: null,
})