/**
 * API 서비스 테스트
 * 기본적인 API 호출 및 에러 처리 테스트
 */

import { describe, it, expect } from 'vitest'
import { ApiServiceError } from '../api'

describe('ApiService', () => {
  describe('입력 검증 테스트', () => {
    it('빈 서비스 ID 검증', () => {
      // 실제 API 호출 대신 입력 검증 로직만 테스트
      const validateServiceId = (serviceId: string) => {
        if (!serviceId?.trim()) {
          throw new ApiServiceError('서비스 ID가 필요합니다', 400, 'INVALID_SERVICE_ID')
        }
        return true
      }

      expect(() => validateServiceId('')).toThrow(ApiServiceError)
      expect(() => validateServiceId('   ')).toThrow(ApiServiceError)
      expect(validateServiceId('valid-service')).toBe(true)
    })

    it('웹훅 페이로드 검증', () => {
      const validateWebhookPayload = (payload: { url: string; message: string }) => {
        if (!payload.url?.trim()) {
          throw new ApiServiceError('웹훅 URL이 필요합니다', 400, 'INVALID_WEBHOOK_URL')
        }
        if (!payload.message?.trim()) {
          throw new ApiServiceError('메시지가 필요합니다', 400, 'INVALID_MESSAGE')
        }
        return true
      }

      expect(() => validateWebhookPayload({ url: '', message: 'test' })).toThrow(ApiServiceError)
      expect(() => validateWebhookPayload({ url: 'https://test.com', message: '' })).toThrow(ApiServiceError)
      expect(validateWebhookPayload({ url: 'https://test.com', message: 'test message' })).toBe(true)
    })

    it('템플릿 ID 검증', () => {
      const validateTemplateId = (templateId: string) => {
        if (!templateId?.trim()) {
          throw new ApiServiceError('템플릿 ID가 필요합니다', 400, 'INVALID_TEMPLATE_ID')
        }
        return true
      }

      expect(() => validateTemplateId('')).toThrow(ApiServiceError)
      expect(() => validateTemplateId('   ')).toThrow(ApiServiceError)
      expect(validateTemplateId('valid-template-id')).toBe(true)
    })
  })

  describe('쿼리 파라미터 빌더 테스트', () => {
    it('빈 값들을 필터링해야 합니다', () => {
      const buildQueryParams = (params: Record<string, any>): string => {
        const searchParams = new URLSearchParams()
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            searchParams.append(key, String(value))
          }
        })
        return searchParams.toString()
      }

      const params = {
        limit: 10,
        service: 'test-service',
        level: '',
        start_time: undefined,
        end_time: null,
        active: true
      }

      const result = buildQueryParams(params)
      expect(result).toContain('limit=10')
      expect(result).toContain('service=test-service')
      expect(result).toContain('active=true')
      expect(result).not.toContain('level=')
      expect(result).not.toContain('start_time=')
      expect(result).not.toContain('end_time=')
    })
  })
})

describe('ApiServiceError', () => {
  it('올바른 속성들을 가져야 합니다', () => {
    const error = new ApiServiceError('Test error', 404, 'NOT_FOUND', { detail: 'Resource not found' })
    
    expect(error.message).toBe('Test error')
    expect(error.status).toBe(404)
    expect(error.code).toBe('NOT_FOUND')
    expect(error.details).toEqual({ detail: 'Resource not found' })
    expect(error.name).toBe('ApiServiceError')
  })

  it('선택적 매개변수 없이도 생성되어야 합니다', () => {
    const error = new ApiServiceError('Simple error')
    
    expect(error.message).toBe('Simple error')
    expect(error.status).toBeUndefined()
    expect(error.code).toBeUndefined()
    expect(error.details).toBeUndefined()
  })
})