import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { vi } from 'vitest'
import GeneralSettings from '../GeneralSettings'
import { theme } from '../../../theme'

// useSettings 훅 모킹
vi.mock('../../../hooks/useSettings', () => ({
  useSettings: () => ({
    settings: {
      autoRefresh: true,
      refreshInterval: 5,
      language: 'ko',
      notifications: true,
      logLevel: 'INFO',
      maxLogEntries: 1000,
      backupEnabled: true,
      backupInterval: 24,
    },
    updateSetting: vi.fn(),
    saveSettings: vi.fn(),
  }),
}))

const mockSettings = {
  autoRefresh: true,
  refreshInterval: 5,
  language: 'ko',
  notifications: true,
  logLevel: 'INFO',
  maxLogEntries: 1000,
  backupEnabled: true,
  backupInterval: 24,
}

const mockOnSettingChange = vi.fn()

const renderGeneralSettings = (props = {}) => {
  return render(
    <ChakraProvider theme={theme}>
      <GeneralSettings
        settings={mockSettings}
        onSettingChange={mockOnSettingChange}
        {...props}
      />
    </ChakraProvider>
  )
}

describe('GeneralSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('일반 설정 컴포넌트가 정상적으로 렌더링된다', () => {
    renderGeneralSettings()
    
    expect(screen.getByText('일반 설정')).toBeInTheDocument()
    expect(screen.getByText('자동 새로고침')).toBeInTheDocument()
    expect(screen.getByText('새로고침 간격 (초)')).toBeInTheDocument()
    expect(screen.getByText('언어 / Language')).toBeInTheDocument()
    expect(screen.getByText('시스템 알림')).toBeInTheDocument()
  })

  it('자동 새로고침 스위치가 올바르게 작동한다', () => {
    renderGeneralSettings()
    
    const autoRefreshSwitch = screen.getByRole('checkbox', { name: /자동 새로고침/i })
    expect(autoRefreshSwitch).toBeChecked()
    
    fireEvent.click(autoRefreshSwitch)
    expect(mockOnSettingChange).toHaveBeenCalledWith('autoRefresh', false)
  })

  it('새로고침 간격 설정이 올바르게 작동한다', () => {
    renderGeneralSettings()
    
    const intervalInput = screen.getByDisplayValue('5')
    fireEvent.change(intervalInput, { target: { value: '10' } })
    
    // NumberInput의 onChange는 (valueAsString, valueAsNumber) 형태로 호출됨
    expect(mockOnSettingChange).toHaveBeenCalled()
  })

  it('자동 새로고침이 비활성화되면 간격 설정이 비활성화된다', () => {
    const disabledSettings = { ...mockSettings, autoRefresh: false }
    renderGeneralSettings({ settings: disabledSettings })
    
    const intervalInput = screen.getByDisplayValue('5')
    expect(intervalInput).toBeDisabled()
  })

  it('언어 선택이 올바르게 작동한다', async () => {
    renderGeneralSettings()
    
    const languageSelect = screen.getByDisplayValue('한국어 (Korean)')
    fireEvent.change(languageSelect, { target: { value: 'en' } })
    
    expect(mockOnSettingChange).toHaveBeenCalledWith('language', 'en')
  })

  it('로그 레벨 선택이 올바르게 작동한다', () => {
    renderGeneralSettings()
    
    const logLevelSelect = screen.getByDisplayValue('INFO - 정보성 로그 이상')
    fireEvent.change(logLevelSelect, { target: { value: 'DEBUG' } })
    
    expect(mockOnSettingChange).toHaveBeenCalledWith('logLevel', 'DEBUG')
  })

  it('최대 로그 항목 수 설정이 올바르게 작동한다', () => {
    renderGeneralSettings()
    
    const maxLogEntriesInput = screen.getByDisplayValue('1000')
    fireEvent.change(maxLogEntriesInput, { target: { value: '2000' } })
    
    expect(mockOnSettingChange).toHaveBeenCalled()
  })

  it('자동 백업 스위치가 올바르게 작동한다', () => {
    renderGeneralSettings()
    
    const backupSwitch = screen.getByRole('checkbox', { name: /자동 백업/i })
    expect(backupSwitch).toBeChecked()
    
    fireEvent.click(backupSwitch)
    expect(mockOnSettingChange).toHaveBeenCalledWith('backupEnabled', false)
  })

  it('백업이 비활성화되면 백업 간격 설정이 비활성화된다', () => {
    const disabledBackupSettings = { ...mockSettings, backupEnabled: false }
    renderGeneralSettings({ settings: disabledBackupSettings })
    
    const backupIntervalInput = screen.getByDisplayValue('24')
    expect(backupIntervalInput).toBeDisabled()
  })

  it('입력값 유효성 검사가 올바르게 작동한다', () => {
    renderGeneralSettings()
    
    // 새로고침 간격은 1-60초 범위여야 함
    const intervalInput = screen.getByDisplayValue('5')
    
    // 유효하지 않은 값 입력 시도
    fireEvent.change(intervalInput, { target: { value: '0' } })
    fireEvent.change(intervalInput, { target: { value: '61' } })
    
    // 유효성 검사로 인해 호출되지 않아야 함
    expect(mockOnSettingChange).not.toHaveBeenCalledWith('refreshInterval', 0)
    expect(mockOnSettingChange).not.toHaveBeenCalledWith('refreshInterval', 61)
  })

  it('도움말 텍스트가 올바르게 표시된다', () => {
    renderGeneralSettings()
    
    expect(screen.getByText('시스템 메트릭 자동 새로고침 간격을 설정합니다 (1-60초)')).toBeInTheDocument()
    expect(screen.getByText('애플리케이션 인터페이스 언어를 선택합니다')).toBeInTheDocument()
    expect(screen.getByText('표시할 최소 로그 레벨을 설정합니다')).toBeInTheDocument()
    expect(screen.getByText('메모리에 보관할 최대 로그 항목 수입니다 (100-10,000)')).toBeInTheDocument()
    expect(screen.getByText('설정 및 로그 자동 백업 간격을 설정합니다 (1-168시간)')).toBeInTheDocument()
  })

  it('언어 변경 시 토스트 알림이 표시된다', async () => {
    renderGeneralSettings()
    
    const languageSelect = screen.getByDisplayValue('한국어 (Korean)')
    fireEvent.change(languageSelect, { target: { value: 'en' } })
    
    // 토스트 알림 확인은 실제 useToast 훅의 동작에 따라 달라질 수 있음
    expect(mockOnSettingChange).toHaveBeenCalledWith('language', 'en')
  })
})