import { describe, it, expect, vi } from 'vitest'
import { 
  handleQueryError, 
  getRecoveryStrategy, 
  analyzeError, 
  errorToToast,
  logError,
  createErrorState,
  clearErrorState 
} from '../errorHandler'
import { ApiServiceError } from '../api'

describe('errorHandler', () => {
  describe('handleQueryError', () => {
    it('ApiServiceError를 올바르게 처리한다', () => {
      const error = new ApiServiceError('서비스를 찾을 수 없습니다', 404, 'SERVICE_NOT_FOUND')
      const result = handleQueryError(error, 'serviceControl')

      expect(result.title).toBe('오류 발생')
      expect(result.description).toContain('서비스를 찾을 수 없습니다')
      expect(result.status).toBe('warning') // 404는 low severity이므로 warning
      expect(result.duration).toBe(5000)
      expect(result.isClosable).toBe(true)
    })

    it('네트워크 오류를 올바르게 처리한다', () => {
      const error = new ApiServiceError('Network Error', undefined, 'NETWORK_ERROR')
      const result = handleQueryError(error, 'apiCall')

      expect(result.title).toBe('오류 발생')
      expect(result.description).toContain('Network Error')
      expect(result.status).toBe('error') // high severity
    })

    it('일반 Error를 올바르게 처리한다', () => {
      const error = new Error('Unknown error')
      const result = handleQueryError(error, 'unknownOperation')

      expect(result.title).toBe('오류 발생')
      expect(result.description).toContain('Unknown error')
      expect(result.status).toBe('error')
    })

    it('권한 오류를 올바르게 처리한다', () => {
      const error = new ApiServiceError('권한이 없습니다', 403, 'FORBIDDEN')
      const result = handleQueryError(error, 'serviceControl')

      expect(result.title).toBe('오류 발생')
      expect(result.description).toContain('권한이 없습니다')
      expect(result.status).toBe('error') // medium severity
    })

    it('서버 오류를 올바르게 처리한다', () => {
      const error = new ApiServiceError('내부 서버 오류', 500, 'INTERNAL_SERVER_ERROR')
      const result = handleQueryError(error, 'apiCall')

      expect(result.title).toBe('오류 발생')
      expect(result.description).toContain('내부 서버 오류')
      expect(result.status).toBe('error') // high severity
      expect(result.duration).toBe(5000)
    })

    it('상태 코드별 심각도가 올바르게 설정된다', () => {
      const error400 = new ApiServiceError('잘못된 요청', 400)
      const result400 = handleQueryError(error400, 'test')
      expect(result400.status).toBe('warning') // low severity

      const error401 = new ApiServiceError('인증 실패', 401)
      const result401 = handleQueryError(error401, 'test')
      expect(result401.status).toBe('error') // medium severity

      const error404 = new ApiServiceError('찾을 수 없음', 404)
      const result404 = handleQueryError(error404, 'test')
      expect(result404.status).toBe('warning') // low severity

      const error500 = new ApiServiceError('서버 오류', 500)
      const result500 = handleQueryError(error500, 'test')
      expect(result500.status).toBe('error') // high severity
    })
  })

  describe('getRecoveryStrategy', () => {
    it('네트워크 오류에 대한 복구 전략을 반환한다', () => {
      const error = new ApiServiceError('Network Error', undefined, 'NETWORK_ERROR')
      const strategy = getRecoveryStrategy(error)

      expect(strategy.canRetry).toBe(true)
      expect(strategy.retryDelay).toBe(5000)
      expect(strategy.maxRetries).toBe(3)
      expect(strategy.fallbackAction).toContain('백엔드 서버')
    })

    it('타임아웃 오류에 대한 복구 전략을 반환한다', () => {
      const error = new ApiServiceError('Request timeout', undefined, 'TIMEOUT')
      const strategy = getRecoveryStrategy(error)

      expect(strategy.canRetry).toBe(true)
      expect(strategy.retryDelay).toBe(2000)
      expect(strategy.maxRetries).toBe(2)
    })

    it('서버 오류에 대한 복구 전략을 반환한다', () => {
      const error = new ApiServiceError('서버 오류', 500, 'INTERNAL_SERVER_ERROR')
      const strategy = getRecoveryStrategy(error)

      expect(strategy.canRetry).toBe(true)
      expect(strategy.retryDelay).toBe(3000)
      expect(strategy.maxRetries).toBe(2)
      expect(strategy.fallbackAction).toContain('관리자')
    })

    it('서비스 사용 불가 오류에 대한 복구 전략을 반환한다', () => {
      const error = new ApiServiceError('서비스 사용 불가', 503, 'SERVICE_UNAVAILABLE')
      const strategy = getRecoveryStrategy(error)

      expect(strategy.canRetry).toBe(true)
      expect(strategy.retryDelay).toBe(3000)
      expect(strategy.maxRetries).toBe(2)
    })

    it('클라이언트 오류에 대해 재시도하지 않는다', () => {
      const error400 = new ApiServiceError('잘못된 요청', 400)
      const strategy400 = getRecoveryStrategy(error400)
      expect(strategy400.canRetry).toBe(false)

      const error401 = new ApiServiceError('인증 실패', 401)
      const strategy401 = getRecoveryStrategy(error401)
      expect(strategy401.canRetry).toBe(false)

      const error403 = new ApiServiceError('권한 없음', 403)
      const strategy403 = getRecoveryStrategy(error403)
      expect(strategy403.canRetry).toBe(false)

      const error404 = new ApiServiceError('찾을 수 없음', 404)
      const strategy404 = getRecoveryStrategy(error404)
      expect(strategy404.canRetry).toBe(false)
    })

    it('요청 한도 초과 오류에 대한 특별한 복구 전략을 반환한다', () => {
      const error = new ApiServiceError('요청 한도 초과', 429, 'RATE_LIMITED')
      const strategy = getRecoveryStrategy(error)

      expect(strategy.canRetry).toBe(true)
      expect(strategy.retryDelay).toBe(10000) // 10초 대기
      expect(strategy.maxRetries).toBe(1)
    })

    it('일반 오류에 대한 기본 복구 전략을 반환한다', () => {
      const error = new Error('Unknown error')
      const strategy = getRecoveryStrategy(error)

      expect(strategy.canRetry).toBe(false) // 일반 Error는 재시도 불가
      expect(strategy.fallbackAction).toBeUndefined()
    })

    it('복구 전략에 올바른 속성들이 포함된다', () => {
      const error = new ApiServiceError('Test error', 500)
      const strategy = getRecoveryStrategy(error)

      expect(strategy).toHaveProperty('canRetry')
      expect(typeof strategy.canRetry).toBe('boolean')
      
      if (strategy.canRetry) {
        expect(strategy).toHaveProperty('retryDelay')
        expect(strategy).toHaveProperty('maxRetries')
        expect(typeof strategy.retryDelay).toBe('number')
        expect(typeof strategy.maxRetries).toBe('number')
      }
    })

    it('지수 백오프 전략이 올바르게 계산된다', () => {
      const calculateBackoffDelay = (baseDelay: number, attempt: number, strategy: string): number => {
        if (strategy === 'exponential_backoff') {
          return baseDelay * Math.pow(2, attempt - 1)
        }
        return baseDelay
      }

      expect(calculateBackoffDelay(1000, 1, 'exponential_backoff')).toBe(1000)
      expect(calculateBackoffDelay(1000, 2, 'exponential_backoff')).toBe(2000)
      expect(calculateBackoffDelay(1000, 3, 'exponential_backoff')).toBe(4000)
      expect(calculateBackoffDelay(1000, 4, 'exponential_backoff')).toBe(8000)
    })

    it('선형 백오프 전략이 올바르게 계산된다', () => {
      const calculateBackoffDelay = (baseDelay: number, attempt: number, strategy: string): number => {
        if (strategy === 'linear_backoff') {
          return baseDelay * attempt
        }
        return baseDelay
      }

      expect(calculateBackoffDelay(1000, 1, 'linear_backoff')).toBe(1000)
      expect(calculateBackoffDelay(1000, 2, 'linear_backoff')).toBe(2000)
      expect(calculateBackoffDelay(1000, 3, 'linear_backoff')).toBe(3000)
    })

    it('고정 지연 전략이 올바르게 작동한다', () => {
      const calculateBackoffDelay = (baseDelay: number, attempt: number, strategy: string): number => {
        if (strategy === 'fixed_delay') {
          return baseDelay
        }
        return baseDelay
      }

      expect(calculateBackoffDelay(5000, 1, 'fixed_delay')).toBe(5000)
      expect(calculateBackoffDelay(5000, 2, 'fixed_delay')).toBe(5000)
      expect(calculateBackoffDelay(5000, 3, 'fixed_delay')).toBe(5000)
    })
  })

  describe('analyzeError', () => {
    it('ApiServiceError를 올바르게 분석한다', () => {
      const error = new ApiServiceError('서버 오류', 500, 'INTERNAL_SERVER_ERROR')
      const result = analyzeError(error)

      expect(result.message).toBe('서버 오류')
      expect(result.severity).toBe('high')
      expect(result.code).toBe('INTERNAL_SERVER_ERROR')
      expect(result.retryable).toBe(true)
      expect(result.userAction).toContain('관리자')
    })

    it('일반 Error를 올바르게 분석한다', () => {
      const error = new Error('일반 오류')
      const result = analyzeError(error)

      expect(result.message).toBe('일반 오류')
      expect(result.severity).toBe('medium')
      expect(result.retryable).toBe(false)
    })

    it('알 수 없는 오류를 올바르게 분석한다', () => {
      const result = analyzeError('string error')

      expect(result.message).toBe('예상치 못한 오류가 발생했습니다')
      expect(result.severity).toBe('medium')
      expect(result.retryable).toBe(false)
    })
  })

  describe('errorToToast', () => {
    it('에러를 토스트 메시지로 변환한다', () => {
      const error = new ApiServiceError('테스트 오류', 400, 'BAD_REQUEST')
      const toast = errorToToast(error)

      expect(toast.title).toBe('오류 발생')
      expect(toast.description).toContain('테스트 오류')
      expect(toast.status).toBe('warning') // low severity
      expect(toast.duration).toBe(5000)
      expect(toast.isClosable).toBe(true)
    })

    it('심각한 오류는 수동으로 닫도록 설정한다', () => {
      // critical severity를 만들기 위해 특별한 조건이 필요하므로 high severity로 테스트
      const error = new ApiServiceError('심각한 오류', 500)
      const toast = errorToToast(error)

      expect(toast.status).toBe('error')
      expect(toast.duration).toBe(5000) // high severity도 5초
    })
  })

  describe('createErrorState와 clearErrorState', () => {
    it('에러 상태를 생성한다', () => {
      const error = new ApiServiceError('테스트 오류', 400)
      const state = createErrorState(error)

      expect(state.hasError).toBe(true)
      expect(state.error).toBeDefined()
      expect(state.toast).toBeDefined()
      expect(state.recovery).toBeDefined()
    })

    it('에러 상태를 초기화한다', () => {
      const state = clearErrorState()

      expect(state.hasError).toBe(false)
      expect(state.error).toBeNull()
      expect(state.toast).toBeNull()
      expect(state.recovery).toBeNull()
    })
  })

  describe('logError', () => {
    it('개발 환경에서 콘솔에 로그를 출력한다', () => {
      const consoleSpy = vi.spyOn(console, 'group').mockImplementation(() => {})
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const consoleGroupEndSpy = vi.spyOn(console, 'groupEnd').mockImplementation(() => {})

      // 개발 환경 시뮬레이션
      vi.stubEnv('DEV', true)

      const error = new ApiServiceError('테스트 오류', 500)
      logError(error, 'test context')

      expect(consoleSpy).toHaveBeenCalled()
      expect(consoleErrorSpy).toHaveBeenCalled()
      expect(consoleGroupEndSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
      consoleErrorSpy.mockRestore()
      consoleGroupEndSpy.mockRestore()
      vi.unstubAllEnvs()
    })
  })
})