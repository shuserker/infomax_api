import { useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@chakra-ui/react'
import { WebhookPayload, WebhookTemplate, WebhookHistory } from '../types'
import { apiService } from '../services/api'

interface WebhookTemplateCreate {
  name: string
  description: string
  webhook_type: 'discord' | 'slack' | 'generic'
  template: string
}

interface UseWebhookManagementReturn {
  // 템플릿 관련
  templates: WebhookTemplate[]
  isLoadingTemplates: boolean
  templatesError: Error | null
  createTemplate: (template: WebhookTemplateCreate) => Promise<void>
  updateTemplate: (id: string, template: WebhookTemplateCreate) => Promise<void>
  deleteTemplate: (id: string) => Promise<void>
  refetchTemplates: () => void

  // 웹훅 전송 관련
  sendWebhook: (payload: WebhookPayload) => Promise<void>
  isSendingWebhook: boolean

  // 히스토리 관련
  history: WebhookHistory[]
  isLoadingHistory: boolean
  historyError: Error | null
  refetchHistory: () => void

  // 유틸리티 함수
  extractTemplateVariables: (template: string) => string[]
  applyTemplateVariables: (template: string, variables: Record<string, string>) => string
}

export const useWebhookManagement = (): UseWebhookManagementReturn => {
  const queryClient = useQueryClient()
  const toast = useToast()

  // 템플릿 목록 조회
  const {
    data: templates = [],
    isLoading: isLoadingTemplates,
    error: templatesError,
    refetch: refetchTemplates,
  } = useQuery({
    queryKey: ['webhook-templates'],
    queryFn: async () => {
      return await apiService.getWebhookTemplates()
    },
    staleTime: 5 * 60 * 1000, // 5분
  })

  // 히스토리 조회
  const {
    data: history = [],
    isLoading: isLoadingHistory,
    error: historyError,
    refetch: refetchHistory,
  } = useQuery({
    queryKey: ['webhook-history'],
    queryFn: async () => {
      return await apiService.getWebhookHistory()
    },
    staleTime: 1 * 60 * 1000, // 1분
  })

  // 웹훅 전송 뮤테이션
  const sendWebhookMutation = useMutation({
    mutationFn: async (payload: WebhookPayload) => {
      return await apiService.sendWebhook(payload)
    },
    onSuccess: () => {
      toast({
        title: '웹훅 전송 성공',
        description: '메시지가 성공적으로 전송되었습니다',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      // 히스토리 새로고침
      queryClient.invalidateQueries({ queryKey: ['webhook-history'] })
    },
    onError: (error: any) => {
      toast({
        title: '웹훅 전송 실패',
        description: error.response?.data?.detail || '메시지 전송에 실패했습니다',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    },
  })

  // 템플릿 생성 뮤테이션
  const createTemplateMutation = useMutation({
    mutationFn: async (template: WebhookTemplateCreate) => {
      const templateWithVariables = {
        ...template,
        variables: extractTemplateVariables(template.template),
      }
      return await apiService.createWebhookTemplate(templateWithVariables)
    },
    onSuccess: () => {
      toast({
        title: '템플릿 생성 완료',
        description: '새 템플릿이 성공적으로 생성되었습니다',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      queryClient.invalidateQueries({ queryKey: ['webhook-templates'] })
    },
    onError: (error: any) => {
      toast({
        title: '템플릿 생성 실패',
        description: error.response?.data?.detail || '템플릿 생성에 실패했습니다',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    },
  })

  // 템플릿 수정 뮤테이션
  const updateTemplateMutation = useMutation({
    mutationFn: async ({ id, template }: { id: string; template: WebhookTemplateCreate }) => {
      const templateWithVariables = {
        ...template,
        variables: extractTemplateVariables(template.template),
      }
      return await apiService.updateWebhookTemplate(id, templateWithVariables)
    },
    onSuccess: () => {
      toast({
        title: '템플릿 수정 완료',
        description: '템플릿이 성공적으로 수정되었습니다',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      queryClient.invalidateQueries({ queryKey: ['webhook-templates'] })
    },
    onError: (error: any) => {
      toast({
        title: '템플릿 수정 실패',
        description: error.response?.data?.detail || '템플릿 수정에 실패했습니다',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    },
  })

  // 템플릿 삭제 뮤테이션
  const deleteTemplateMutation = useMutation({
    mutationFn: async (id: string) => {
      return await apiService.deleteWebhookTemplate(id)
    },
    onSuccess: () => {
      toast({
        title: '템플릿 삭제 완료',
        description: '템플릿이 성공적으로 삭제되었습니다',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      queryClient.invalidateQueries({ queryKey: ['webhook-templates'] })
    },
    onError: (error: any) => {
      toast({
        title: '템플릿 삭제 실패',
        description: error.response?.data?.detail || '템플릿 삭제에 실패했습니다',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    },
  })

  // 템플릿 변수 추출 함수
  const extractTemplateVariables = useCallback((template: string): string[] => {
    const regex = /\{\{(\w+)\}\}/g
    const variables: string[] = []
    let match

    while ((match = regex.exec(template)) !== null) {
      if (!variables.includes(match[1])) {
        variables.push(match[1])
      }
    }

    return variables
  }, [])

  // 템플릿 변수 적용 함수
  const applyTemplateVariables = useCallback(
    (template: string, variables: Record<string, string>): string => {
      let result = template

      Object.entries(variables).forEach(([key, value]) => {
        const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g')
        result = result.replace(regex, value)
      })

      return result
    },
    []
  )

  // 래퍼 함수들
  const sendWebhook = useCallback(
    async (payload: WebhookPayload) => {
      await sendWebhookMutation.mutateAsync(payload)
    },
    [sendWebhookMutation]
  )

  const createTemplate = useCallback(
    async (template: WebhookTemplateCreate) => {
      await createTemplateMutation.mutateAsync(template)
    },
    [createTemplateMutation]
  )

  const updateTemplate = useCallback(
    async (id: string, template: WebhookTemplateCreate) => {
      await updateTemplateMutation.mutateAsync({ id, template })
    },
    [updateTemplateMutation]
  )

  const deleteTemplate = useCallback(
    async (id: string) => {
      if (!confirm('정말로 이 템플릿을 삭제하시겠습니까?')) {
        return
      }
      await deleteTemplateMutation.mutateAsync(id)
    },
    [deleteTemplateMutation]
  )

  return {
    // 템플릿 관련
    templates,
    isLoadingTemplates,
    templatesError,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    refetchTemplates,

    // 웹훅 전송 관련
    sendWebhook,
    isSendingWebhook: sendWebhookMutation.isPending,

    // 히스토리 관련
    history,
    isLoadingHistory,
    historyError,
    refetchHistory,

    // 유틸리티 함수
    extractTemplateVariables,
    applyTemplateVariables,
  }
}