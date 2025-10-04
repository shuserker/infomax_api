import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ChakraProvider } from '@chakra-ui/react'
import React from 'react'
import { useWebhookManagement } from '../useWebhookManagement'
import { useApiService } from '../useApiService'

// Mock hooks
jest.mock('../useApiService')

const mockUseApiService = useApiService as jest.MockedFunction<typeof useApiService>

// Mock data
const mockTemplates = [
  {
    id: 'template1',
    name: '테스트 템플릿',
    description: '테스트용 템플릿입니다',
    webhook_type: 'discord',
    template: '안녕하세요 {{name}}님! {{message}}',
    variables: ['name', 'message'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
]

const mockHistory = [
  {
    id: 'history1',
    url: 'https://discord.com/api/webhooks/test',
    message: '테스트 메시지',
    webhook_type: 'discord',
    status: 'success',
    response_code: 200,
    sent_at: '2024-01-01T12:00:00Z',
  },
]

const mockApiService = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
}

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider>
        {children}
      </ChakraProvider>
    </QueryClientProvider>
  )
}

describe('useWebhookManagement', () => {
  beforeEach(() => {
    mockUseApiService.mockReturnValue({
      apiService: mockApiService,
      isLoading: false,
      error: null,
    })

    mockApiService.get.mockImplementation((url: string) => {
      if (url === '/api/webhook/templates') {
        return Promise.resolve({ data: mockTemplates })
      }
      if (url === '/api/webhook/history') {
        return Promise.resolve({ data: mockHistory })
      }
      return Promise.resolve({ data: [] })
    })

    mockApiService.post.mockResolvedValue({ data: { message: '성공' } })
    mockApiService.put.mockResolvedValue({ data: { message: '수정됨' } })
    mockApiService.delete.mockResolvedValue({ data: { message: '삭제됨' } })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('초기 상태가 올바르게 설정된다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    // 초기 로딩 상태 확인
    expect(result.current.isLoadingTemplates).toBe(true)
    expect(result.current.isLoadingHistory).toBe(true)
    expect(result.current.isSendingWebhook).toBe(false)

    // 데이터 로드 완료 대기
    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
      expect(result.current.isLoadingHistory).toBe(false)
    })

    // 데이터가 올바르게 로드되었는지 확인
    expect(result.current.templates).toEqual(mockTemplates)
    expect(result.current.history).toEqual(mockHistory)
  })

  it('템플릿 변수 추출이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
    })

    // 템플릿 변수 추출 테스트
    const variables = result.current.extractTemplateVariables('안녕하세요 {{name}}님! {{message}}를 확인해주세요.')
    expect(variables).toEqual(['name', 'message'])

    // 중복 변수 제거 테스트
    const duplicateVariables = result.current.extractTemplateVariables('{{name}} {{name}} {{age}}')
    expect(duplicateVariables).toEqual(['name', 'age'])

    // 변수가 없는 경우 테스트
    const noVariables = result.current.extractTemplateVariables('일반 텍스트입니다')
    expect(noVariables).toEqual([])
  })

  it('템플릿 변수 적용이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
    })

    // 템플릿 변수 적용 테스트
    const template = '안녕하세요 {{name}}님! {{message}}를 확인해주세요.'
    const variables = { name: '홍길동', message: '중요한 알림' }
    const result_text = result.current.applyTemplateVariables(template, variables)
    
    expect(result_text).toBe('안녕하세요 홍길동님! 중요한 알림를 확인해주세요.')

    // 일부 변수만 있는 경우 테스트
    const partialVariables = { name: '홍길동' }
    const partialResult = result.current.applyTemplateVariables(template, partialVariables)
    expect(partialResult).toBe('안녕하세요 홍길동님! {{message}}를 확인해주세요.')
  })

  it('웹훅 전송이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
    })

    const webhookPayload = {
      url: 'https://discord.com/api/webhooks/test',
      message: '테스트 메시지',
      webhook_type: 'discord' as const,
      variables: { name: '테스트' },
    }

    // 웹훅 전송
    await result.current.sendWebhook(webhookPayload)

    expect(mockApiService.post).toHaveBeenCalledWith('/api/webhook/send', webhookPayload)
  })

  it('템플릿 생성이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
    })

    const newTemplate = {
      name: '새 템플릿',
      description: '새로운 템플릿입니다',
      webhook_type: 'discord' as const,
      template: '새 메시지: {{content}}',
    }

    // 템플릿 생성
    await result.current.createTemplate(newTemplate)

    expect(mockApiService.post).toHaveBeenCalledWith('/api/webhook/templates', newTemplate)
  })

  it('템플릿 수정이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
    })

    const updatedTemplate = {
      name: '수정된 템플릿',
      description: '수정된 설명',
      webhook_type: 'slack' as const,
      template: '수정된 메시지: {{content}}',
    }

    // 템플릿 수정
    await result.current.updateTemplate('template1', updatedTemplate)

    expect(mockApiService.put).toHaveBeenCalledWith('/api/webhook/templates/template1', updatedTemplate)
  })

  it('템플릿 삭제가 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
    })

    // confirm 모킹
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true)

    // 템플릿 삭제
    await result.current.deleteTemplate('template1')

    expect(confirmSpy).toHaveBeenCalledWith('정말로 이 템플릿을 삭제하시겠습니까?')
    expect(mockApiService.delete).toHaveBeenCalledWith('/api/webhook/templates/template1')

    confirmSpy.mockRestore()
  })

  it('템플릿 삭제 취소가 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
    })

    // confirm 모킹 (취소)
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false)

    // 템플릿 삭제 시도
    await result.current.deleteTemplate('template1')

    expect(confirmSpy).toHaveBeenCalledWith('정말로 이 템플릿을 삭제하시겠습니까?')
    expect(mockApiService.delete).not.toHaveBeenCalled()

    confirmSpy.mockRestore()
  })

  it('데이터 새로고침이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
      expect(result.current.isLoadingHistory).toBe(false)
    })

    // 초기 호출 확인
    expect(mockApiService.get).toHaveBeenCalledWith('/api/webhook/templates')
    expect(mockApiService.get).toHaveBeenCalledWith('/api/webhook/history')

    // 새로고침 실행
    result.current.refetchTemplates()
    result.current.refetchHistory()

    // 추가 호출이 있었는지 확인
    await waitFor(() => {
      expect(mockApiService.get).toHaveBeenCalledTimes(4) // 초기 2번 + 새로고침 2번
    })
  })

  it('API 오류가 올바르게 처리된다', async () => {
    // API 오류 모킹
    mockApiService.get.mockRejectedValue(new Error('API 오류'))

    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
      expect(result.current.isLoadingHistory).toBe(false)
    })

    // 오류 상태 확인
    expect(result.current.templatesError).toBeTruthy()
    expect(result.current.historyError).toBeTruthy()

    // 빈 배열이 반환되는지 확인
    expect(result.current.templates).toEqual([])
    expect(result.current.history).toEqual([])
  })

  it('로딩 상태가 올바르게 관리된다', async () => {
    const { result } = renderHook(() => useWebhookManagement(), {
      wrapper: createWrapper(),
    })

    // 초기 로딩 상태
    expect(result.current.isLoadingTemplates).toBe(true)
    expect(result.current.isLoadingHistory).toBe(true)
    expect(result.current.isSendingWebhook).toBe(false)

    // 로딩 완료 대기
    await waitFor(() => {
      expect(result.current.isLoadingTemplates).toBe(false)
      expect(result.current.isLoadingHistory).toBe(false)
    })

    // 웹훅 전송 시 로딩 상태는 별도로 테스트하기 어려움 (매우 빠르게 완료됨)
    expect(result.current.isSendingWebhook).toBe(false)
  })
})