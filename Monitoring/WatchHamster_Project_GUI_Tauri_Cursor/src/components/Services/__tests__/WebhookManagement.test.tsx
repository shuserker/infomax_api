import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import WebhookManagement from '../WebhookManagement'
import { useWebhookManagement } from '../../../hooks/useWebhookManagement'

import { vi } from 'vitest'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { afterEach } from 'node:test'
import { beforeEach } from 'node:test'
import { describe } from 'node:test'

// Mock hooks
vi.mock('../../../hooks/useWebhookManagement')

const mockUseWebhookManagement = useWebhookManagement as any

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
  {
    id: 'template2',
    name: '시스템 알림',
    description: '시스템 상태 알림 템플릿',
    webhook_type: 'slack',
    template: '시스템 {{system}}의 상태가 {{status}}로 변경되었습니다',
    variables: ['system', 'status'],
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
  {
    id: 'history2',
    url: 'https://hooks.slack.com/test',
    message: '실패한 메시지',
    webhook_type: 'slack',
    status: 'failed',
    response_code: 400,
    error_message: 'Bad Request',
    sent_at: '2024-01-01T11:00:00Z',
  },
]

const mockWebhookManagement = {
  templates: mockTemplates,
  isLoadingTemplates: false,
  history: mockHistory,
  isLoadingHistory: false,
  isSendingWebhook: false,
  sendWebhook: vi.fn(),
  createTemplate: vi.fn(),
  updateTemplate: vi.fn(),
  deleteTemplate: vi.fn(),
  refetchTemplates: vi.fn(),
  refetchHistory: vi.fn(),
  extractTemplateVariables: vi.fn((template: string) => {
    const regex = /\{\{(\w+)\}\}/g
    const variables: string[] = []
    let match
    while ((match = regex.exec(template)) !== null) {
      if (!variables.includes(match[1])) {
        variables.push(match[1])
      }
    }
    return variables
  }),
  applyTemplateVariables: vi.fn((template: string, variables: Record<string, string>) => {
    let result = template
    Object.entries(variables).forEach(([key, value]) => {
      const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g')
      result = result.replace(regex, value)
    })
    return result
  }),
}

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <ChakraProvider>
        {component}
      </ChakraProvider>
    </QueryClientProvider>
  )
}

describe('WebhookManagement', () => {
  beforeEach(() => {
    mockUseWebhookManagement.mockReturnValue(mockWebhookManagement)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('컴포넌트가 정상적으로 렌더링된다', async () => {
    renderWithProviders(<WebhookManagement />)

    expect(screen.getByText('웹훅 및 메시지 관리')).toBeInTheDocument()
    expect(screen.getByText('Discord, Slack 등으로 메시지를 전송하고 템플릿을 관리합니다')).toBeInTheDocument()

    // 탭들이 표시되는지 확인
    expect(screen.getByText('웹훅 전송')).toBeInTheDocument()
    expect(screen.getByText('템플릿 관리')).toBeInTheDocument()
    expect(screen.getByText('전송 히스토리')).toBeInTheDocument()
  })

  it('웹훅 전송 폼이 정상적으로 작동한다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 웹훅 전송 탭이 기본으로 선택되어 있어야 함
    expect(screen.getByText('웹훅 메시지 전송')).toBeInTheDocument()

    // 폼 필드들이 표시되는지 확인
    expect(screen.getByLabelText('웹훅 타입')).toBeInTheDocument()
    expect(screen.getByLabelText('웹훅 URL')).toBeInTheDocument()
    expect(screen.getByLabelText('메시지 내용')).toBeInTheDocument()

    // 폼 입력
    await user.type(screen.getByLabelText('웹훅 URL'), 'https://discord.com/api/webhooks/test')
    await user.type(screen.getByLabelText('메시지 내용'), '테스트 메시지입니다')

    // 전송 버튼 클릭
    const sendButton = screen.getByText('웹훅 전송')
    await user.click(sendButton)

    await waitFor(() => {
      expect(mockWebhookManagement.sendWebhook).toHaveBeenCalledWith({
        url: 'https://discord.com/api/webhooks/test',
        message: '테스트 메시지입니다',
        webhook_type: 'discord',
        variables: {},
      })
    })
  })

  it('템플릿 선택 시 메시지가 자동으로 업데이트된다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 템플릿이 이미 로드되어 있음

    // 템플릿 선택
    const templateSelect = screen.getByLabelText('템플릿 선택 (선택사항)')
    await user.selectOptions(templateSelect, 'template1')

    // 템플릿 변수 입력 필드가 나타나는지 확인
    await waitFor(() => {
      expect(screen.getByLabelText('name')).toBeInTheDocument()
      expect(screen.getByLabelText('message')).toBeInTheDocument()
    })

    // 변수 값 입력
    await user.type(screen.getByLabelText('name'), '홍길동')
    await user.type(screen.getByLabelText('message'), '반갑습니다')

    // 메시지 필드에 템플릿이 적용되었는지 확인
    const messageTextarea = screen.getByLabelText('메시지 내용') as HTMLTextAreaElement
    expect(messageTextarea.value).toContain('안녕하세요 홍길동님! 반갑습니다')
  })

  it('템플릿 관리 탭에서 템플릿 목록을 표시한다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 템플릿 관리 탭 클릭
    await user.click(screen.getByText('템플릿 관리'))

    await waitFor(() => {
      expect(screen.getByText('테스트 템플릿')).toBeInTheDocument()
      expect(screen.getByText('시스템 알림')).toBeInTheDocument()
    })

    // 템플릿 정보가 표시되는지 확인
    expect(screen.getByText('테스트용 템플릿입니다')).toBeInTheDocument()
    expect(screen.getByText('시스템 상태 알림 템플릿')).toBeInTheDocument()
  })

  it('새 템플릿 생성 모달이 정상적으로 작동한다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 템플릿 관리 탭으로 이동
    await user.click(screen.getByText('템플릿 관리'))

    // 새 템플릿 버튼 클릭
    await user.click(screen.getByText('새 템플릿'))

    // 모달이 열렸는지 확인
    expect(screen.getByText('새 템플릿 생성')).toBeInTheDocument()

    // 폼 필드들이 표시되는지 확인
    expect(screen.getByLabelText('템플릿 이름')).toBeInTheDocument()
    expect(screen.getByLabelText('설명')).toBeInTheDocument()
    expect(screen.getByLabelText('템플릿 내용')).toBeInTheDocument()

    // 폼 입력
    await user.type(screen.getByLabelText('템플릿 이름'), '새 템플릿')
    await user.type(screen.getByLabelText('설명'), '새로운 템플릿입니다')
    await user.type(screen.getByLabelText('템플릿 내용'), '새 메시지: {{content}}')

    // 생성 버튼 클릭
    await user.click(screen.getByText('생성'))

    await waitFor(() => {
      expect(mockWebhookManagement.createTemplate).toHaveBeenCalledWith({
        name: '새 템플릿',
        description: '새로운 템플릿입니다',
        webhook_type: 'discord',
        template: '새 메시지: {{content}}',
      })
    })
  })

  it('템플릿 편집이 정상적으로 작동한다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 템플릿 관리 탭으로 이동
    await user.click(screen.getByText('템플릿 관리'))

    await waitFor(() => {
      expect(screen.getByText('테스트 템플릿')).toBeInTheDocument()
    })

    // 편집 버튼 클릭 (첫 번째 템플릿)
    const editButtons = screen.getAllByLabelText('템플릿 편집')
    await user.click(editButtons[0])

    // 편집 모달이 열렸는지 확인
    expect(screen.getByText('템플릿 편집')).toBeInTheDocument()

    // 기존 값이 채워져 있는지 확인
    expect(screen.getByDisplayValue('테스트 템플릿')).toBeInTheDocument()
    expect(screen.getByDisplayValue('테스트용 템플릿입니다')).toBeInTheDocument()

    // 값 수정
    const nameInput = screen.getByDisplayValue('테스트 템플릿')
    await user.clear(nameInput)
    await user.type(nameInput, '수정된 템플릿')

    // 수정 버튼 클릭
    await user.click(screen.getByText('수정'))

    await waitFor(() => {
      expect(mockWebhookManagement.updateTemplate).toHaveBeenCalledWith('template1', {
        name: '수정된 템플릿',
        description: '테스트용 템플릿입니다',
        webhook_type: 'discord',
        template: '안녕하세요 {{name}}님! {{message}}',
      })
    })
  })

  it('템플릿 삭제가 정상적으로 작동한다', async () => {
    const user = userEvent.setup()
    
    // confirm 모킹
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    
    renderWithProviders(<WebhookManagement />)

    // 템플릿 관리 탭으로 이동
    await user.click(screen.getByText('템플릿 관리'))

    await waitFor(() => {
      expect(screen.getByText('테스트 템플릿')).toBeInTheDocument()
    })

    // 삭제 버튼 클릭 (첫 번째 템플릿)
    const deleteButtons = screen.getAllByLabelText('템플릿 삭제')
    await user.click(deleteButtons[0])

    await waitFor(() => {
      expect(mockWebhookManagement.deleteTemplate).toHaveBeenCalledWith('template1')
    })

    confirmSpy.mockRestore()
  })

  it('전송 히스토리 탭에서 히스토리를 표시한다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 전송 히스토리 탭 클릭
    await user.click(screen.getByText('전송 히스토리'))

    // 히스토리가 이미 로드되어 있음

    // 히스토리 항목들이 표시되는지 확인
    expect(screen.getByText('테스트 메시지')).toBeInTheDocument()
    expect(screen.getByText('실패한 메시지')).toBeInTheDocument()

    // 상태 배지가 표시되는지 확인
    expect(screen.getByText('success')).toBeInTheDocument()
    expect(screen.getByText('failed')).toBeInTheDocument()
  })

  it('메시지 미리보기가 정상적으로 작동한다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 메시지 입력
    await user.type(screen.getByLabelText('메시지 내용'), '미리보기 테스트 메시지')

    // 미리보기 버튼 클릭
    await user.click(screen.getByText('미리보기'))

    // 미리보기 모달이 열렸는지 확인
    expect(screen.getByText('메시지 미리보기')).toBeInTheDocument()
    expect(screen.getByText('미리보기 테스트 메시지')).toBeInTheDocument()
  })

  it('폼 유효성 검사가 정상적으로 작동한다', async () => {
    const user = userEvent.setup()
    renderWithProviders(<WebhookManagement />)

    // 빈 폼으로 전송 시도
    await user.click(screen.getByText('웹훅 전송'))

    // 오류 메시지가 표시되는지 확인
    await waitFor(() => {
      expect(screen.getByText('웹훅 URL은 필수입니다')).toBeInTheDocument()
      expect(screen.getByText('메시지는 필수입니다')).toBeInTheDocument()
    })

    // 잘못된 URL 입력
    await user.type(screen.getByLabelText('웹훅 URL'), 'invalid-url')
    await user.click(screen.getByText('웹훅 전송'))

    await waitFor(() => {
      expect(screen.getByText('올바른 URL을 입력해주세요')).toBeInTheDocument()
    })
  })

  it('로딩 상태가 정상적으로 표시된다', () => {
    mockUseWebhookManagement.mockReturnValue({
      ...mockWebhookManagement,
      isLoadingTemplates: true,
    })

    renderWithProviders(<WebhookManagement />)

    // 컴포넌트가 정상적으로 렌더링되는지 확인
    expect(screen.getByText('웹훅 및 메시지 관리')).toBeInTheDocument()
  })

  it('에러 상태가 정상적으로 처리된다', async () => {
    mockUseWebhookManagement.mockReturnValue({
      ...mockWebhookManagement,
      templates: [],
      history: [],
    })

    renderWithProviders(<WebhookManagement />)

    // 컴포넌트가 에러 없이 렌더링되는지 확인
    expect(screen.getByText('웹훅 및 메시지 관리')).toBeInTheDocument()
  })
})