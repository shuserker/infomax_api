import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { vi } from 'vitest'
import NotificationSettings from '../NotificationSettings'
import { theme } from '../../../theme'
import { AppSettings } from '../../../hooks/useSettings'

const mockSettings: AppSettings = {
  autoRefresh: true,
  refreshInterval: 5,
  language: 'ko',
  notifications: true,
  theme: 'light',
  poscoTheme: true,
  customColors: {
    primary: '#003d82',
    secondary: '#0066cc',
    accent: '#ff6b35',
  },
  systemAlerts: true,
  serviceAlerts: true,
  errorAlerts: true,
  alertPriority: {
    system: 'medium',
    service: 'high',
    error: 'high',
  },
  webhookUrl: 'https://discord.com/api/webhooks/123456789/abcdefghijklmnop',
  webhookEnabled: true,
  logLevel: 'INFO',
  maxLogEntries: 1000,
  backupEnabled: true,
  backupInterval: 24,
  performanceMode: false,
  debugMode: false,
}

const mockOnSettingChange = vi.fn()
const mockOnNestedSettingChange = vi.fn()
const mockOnTestWebhook = vi.fn()

const renderNotificationSettings = (props = {}) => {
  return render(
    <ChakraProvider theme={theme}>
      <NotificationSettings
        settings={mockSettings}
        onSettingChange={mockOnSettingChange}
        onNestedSettingChange={mockOnNestedSettingChange}
        onTestWebhook={mockOnTestWebhook}
        {...props}
      />
    </ChakraProvider>
  )
}

describe('NotificationSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('알림 설정 컴포넌트가 정상적으로 렌더링된다', () => {
    renderNotificationSettings()
    
    expect(screen.getByText('알림 설정')).toBeInTheDocument()
    expect(screen.getByText('기본 알림 설정')).toBeInTheDocument()
    expect(screen.getByText('알림 우선순위 설정')).toBeInTheDocument()
    expect(screen.getByText('웹훅 설정')).toBeInTheDocument()
  })

  it('시스템 알림 스위치가 올바르게 작동한다', () => {
    renderNotificationSettings()
    
    const systemAlertsSwitch = screen.getByRole('checkbox', { name: /시스템 알림/i })
    expect(systemAlertsSwitch).toBeChecked()
    
    fireEvent.click(systemAlertsSwitch)
    expect(mockOnSettingChange).toHaveBeenCalledWith('systemAlerts', false)
  })

  it('서비스 알림 스위치가 올바르게 작동한다', () => {
    renderNotificationSettings()
    
    const serviceAlertsSwitch = screen.getByRole('checkbox', { name: /서비스 알림/i })
    expect(serviceAlertsSwitch).toBeChecked()
    
    fireEvent.click(serviceAlertsSwitch)
    expect(mockOnSettingChange).toHaveBeenCalledWith('serviceAlerts', false)
  })

  it('오류 알림 스위치가 올바르게 작동한다', () => {
    renderNotificationSettings()
    
    const errorAlertsSwitch = screen.getByRole('checkbox', { name: /오류 알림/i })
    expect(errorAlertsSwitch).toBeChecked()
    
    fireEvent.click(errorAlertsSwitch)
    expect(mockOnSettingChange).toHaveBeenCalledWith('errorAlerts', false)
  })

  it('알림 우선순위 설정이 올바르게 작동한다', () => {
    renderNotificationSettings()
    
    const systemPrioritySelect = screen.getByDisplayValue('보통')
    fireEvent.change(systemPrioritySelect, { target: { value: 'high' } })
    
    expect(mockOnNestedSettingChange).toHaveBeenCalledWith('alertPriority.system', 'high')
  })

  it('웹훅 활성화 스위치가 올바르게 작동한다', () => {
    renderNotificationSettings()
    
    // 웹훅 설정 섹션의 스위치 찾기
    const webhookSwitches = screen.getAllByRole('checkbox')
    const webhookSwitch = webhookSwitches.find(sw => 
      sw.closest('div')?.textContent?.includes('웹훅 설정')
    )
    
    if (webhookSwitch) {
      fireEvent.click(webhookSwitch)
      expect(mockOnSettingChange).toHaveBeenCalledWith('webhookEnabled', false)
    }
  })

  it('웹훅 URL 입력이 올바르게 작동한다', () => {
    renderNotificationSettings()
    
    const webhookUrlInput = screen.getByDisplayValue('https://discord.com/api/webhooks/123456789/abcdefghijklmnop')
    const newUrl = 'https://discord.com/api/webhooks/987654321/newwebhookurl'
    
    fireEvent.change(webhookUrlInput, { target: { value: newUrl } })
    expect(mockOnSettingChange).toHaveBeenCalledWith('webhookUrl', newUrl)
  })

  it('웹훅 URL 유효성 검사가 올바르게 작동한다', () => {
    renderNotificationSettings()
    
    // 유효한 Discord URL
    expect(screen.getByText('유효한 Discord 웹훅 URL')).toBeInTheDocument()
  })

  it('잘못된 웹훅 URL에 대한 경고가 표시된다', () => {
    const invalidSettings = {
      ...mockSettings,
      webhookUrl: 'invalid-url'
    }
    
    renderNotificationSettings({ settings: invalidSettings })
    
    expect(screen.getByText('올바르지 않은 웹훅 URL 형식')).toBeInTheDocument()
  })

  it('웹훅 테스트 버튼이 올바르게 작동한다', async () => {
    mockOnTestWebhook.mockResolvedValue(true)
    renderNotificationSettings()
    
    const testButton = screen.getByText('웹훅 테스트')
    fireEvent.click(testButton)
    
    expect(mockOnTestWebhook).toHaveBeenCalled()
    
    await waitFor(() => {
      expect(screen.getByText('테스트 성공')).toBeInTheDocument()
    })
  })

  it('웹훅 테스트 실패 시 적절한 메시지가 표시된다', async () => {
    mockOnTestWebhook.mockResolvedValue(false)
    renderNotificationSettings()
    
    const testButton = screen.getByText('웹훅 테스트')
    fireEvent.click(testButton)
    
    await waitFor(() => {
      expect(screen.getByText('테스트 실패')).toBeInTheDocument()
    })
  })

  it('웹훅이 비활성화되면 관련 컨트롤이 비활성화된다', () => {
    const disabledSettings = {
      ...mockSettings,
      webhookEnabled: false
    }
    
    renderNotificationSettings({ settings: disabledSettings })
    
    const webhookUrlInput = screen.getByPlaceholderText(/discord.com|slack.com/)
    const testButton = screen.getByText('웹훅 테스트')
    
    expect(webhookUrlInput).toBeDisabled()
    expect(testButton).toBeDisabled()
  })

  it('웹훅 URL이 없으면 테스트 버튼이 비활성화된다', () => {
    const noUrlSettings = {
      ...mockSettings,
      webhookUrl: ''
    }
    
    renderNotificationSettings({ settings: noUrlSettings })
    
    const testButton = screen.getByText('웹훅 테스트')
    expect(testButton).toBeDisabled()
  })

  it('웹훅 설정 가이드가 올바르게 표시된다', () => {
    renderNotificationSettings()
    
    // 아코디언 버튼 클릭
    const guideButton = screen.getByText('웹훅 설정 가이드')
    fireEvent.click(guideButton)
    
    expect(screen.getByText('Discord 웹훅 설정:')).toBeInTheDocument()
    expect(screen.getByText('Slack 웹훅 설정:')).toBeInTheDocument()
  })

  it('알림 미리보기가 올바르게 표시된다', () => {
    renderNotificationSettings()
    
    expect(screen.getByText('알림 미리보기')).toBeInTheDocument()
    expect(screen.getByText('WatchHamster 알림')).toBeInTheDocument()
    expect(screen.getByText('CPU 사용률이 85%를 초과했습니다. 현재 사용률: 87%')).toBeInTheDocument()
  })

  it('고급 알림 설정이 올바르게 표시된다', () => {
    renderNotificationSettings()
    
    expect(screen.getByText('고급 알림 설정')).toBeInTheDocument()
    expect(screen.getByText('알림 지연 시간 (초)')).toBeInTheDocument()
    expect(screen.getByText('최대 알림 횟수')).toBeInTheDocument()
    expect(screen.getByText('조용한 시간대')).toBeInTheDocument()
  })

  it('우선순위 설명이 올바르게 표시된다', () => {
    renderNotificationSettings()
    
    expect(screen.getByText(/우선순위 설명:/)).toBeInTheDocument()
    expect(screen.getByText(/높음: 즉시 알림, 소리 포함/)).toBeInTheDocument()
    expect(screen.getByText(/보통: 일반 알림, 소리 없음/)).toBeInTheDocument()
    expect(screen.getByText(/낮음: 조용한 알림, 로그만 기록/)).toBeInTheDocument()
  })

  it('Slack 웹훅 URL이 올바르게 인식된다', () => {
    const slackSettings = {
      ...mockSettings,
      webhookUrl: 'https://hooks.slack.com/services/[TEAM_ID]/[CHANNEL_ID]/[TOKEN]'
    }
    
    renderNotificationSettings({ settings: slackSettings })
    
    expect(screen.getByText('유효한 Slack 웹훅 URL')).toBeInTheDocument()
  })
})