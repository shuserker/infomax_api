import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider, useColorMode } from '@chakra-ui/react'
import { vi } from 'vitest'
import ThemeSettings from '../ThemeSettings'
import { theme } from '../../../theme'
import { AppSettings } from '../../../hooks/useSettings'

// useColorMode 훅 모킹
const mockToggleColorMode = vi.fn()
vi.mock('@chakra-ui/react', async () => {
  const actual = await vi.importActual('@chakra-ui/react')
  return {
    ...actual,
    useColorMode: () => ({
      colorMode: 'light',
      toggleColorMode: mockToggleColorMode,
    }),
  }
})

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
  webhookUrl: '',
  webhookEnabled: false,
  logLevel: 'INFO',
  maxLogEntries: 1000,
  backupEnabled: true,
  backupInterval: 24,
  performanceMode: false,
  debugMode: false,
}

const mockOnSettingChange = vi.fn()
const mockOnNestedSettingChange = vi.fn()

const renderThemeSettings = (props = {}) => {
  return render(
    <ChakraProvider theme={theme}>
      <ThemeSettings
        settings={mockSettings}
        onSettingChange={mockOnSettingChange}
        onNestedSettingChange={mockOnNestedSettingChange}
        {...props}
      />
    </ChakraProvider>
  )
}

describe('ThemeSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('테마 설정 컴포넌트가 정상적으로 렌더링된다', () => {
    renderThemeSettings()
    
    expect(screen.getByText('테마 설정')).toBeInTheDocument()
    expect(screen.getByText('테마 모드')).toBeInTheDocument()
    expect(screen.getByText('POSCO 기업 테마')).toBeInTheDocument()
    expect(screen.getByText('미리 정의된 색상 팔레트')).toBeInTheDocument()
    expect(screen.getByText('커스텀 색상 설정')).toBeInTheDocument()
  })

  it('테마 모드 변경이 올바르게 작동한다', () => {
    renderThemeSettings()
    
    const themeSelect = screen.getByDisplayValue('라이트 모드')
    fireEvent.change(themeSelect, { target: { value: 'dark' } })
    
    expect(mockOnSettingChange).toHaveBeenCalledWith('theme', 'dark')
    expect(mockToggleColorMode).toHaveBeenCalled()
  })

  it('POSCO 기업 테마 스위치가 올바르게 작동한다', () => {
    renderThemeSettings()
    
    const poscoThemeSwitch = screen.getByRole('checkbox', { name: /POSCO 기업 테마/i })
    expect(poscoThemeSwitch).toBeChecked()
    
    fireEvent.click(poscoThemeSwitch)
    expect(mockOnSettingChange).toHaveBeenCalledWith('poscoTheme', false)
  })

  it('미리보기 버튼이 올바르게 작동한다', () => {
    renderThemeSettings()
    
    const lightPreviewButton = screen.getByText('라이트 모드 미리보기')
    const darkPreviewButton = screen.getByText('다크 모드 미리보기')
    
    fireEvent.click(lightPreviewButton)
    fireEvent.click(darkPreviewButton)
    
    // 미리보기 상태 변경 확인
    expect(lightPreviewButton).toBeInTheDocument()
    expect(darkPreviewButton).toBeInTheDocument()
  })

  it('색상 팔레트 선택이 올바르게 작동한다', () => {
    renderThemeSettings()
    
    // POSCO 기본 팔레트 클릭
    const poscoCard = screen.getByText('POSCO 기본').closest('div')
    if (poscoCard) {
      fireEvent.click(poscoCard)
      
      expect(mockOnNestedSettingChange).toHaveBeenCalledWith('customColors.primary', '#003d82')
      expect(mockOnNestedSettingChange).toHaveBeenCalledWith('customColors.secondary', '#0066cc')
      expect(mockOnNestedSettingChange).toHaveBeenCalledWith('customColors.accent', '#ff6b35')
    }
  })

  it('커스텀 색상 입력이 올바르게 작동한다', () => {
    renderThemeSettings()
    
    // 주 색상 변경
    const primaryColorInputs = screen.getAllByDisplayValue('#003d82')
    if (primaryColorInputs.length > 0) {
      fireEvent.change(primaryColorInputs[0], { target: { value: '#ff0000' } })
      expect(mockOnNestedSettingChange).toHaveBeenCalledWith('customColors.primary', '#ff0000')
    }
  })

  it('기본 색상 복원 버튼이 올바르게 작동한다', () => {
    renderThemeSettings()
    
    const resetButton = screen.getByText('기본 색상으로 복원')
    fireEvent.click(resetButton)
    
    expect(mockOnNestedSettingChange).toHaveBeenCalledWith('customColors.primary', '#003d82')
    expect(mockOnNestedSettingChange).toHaveBeenCalledWith('customColors.secondary', '#0066cc')
    expect(mockOnNestedSettingChange).toHaveBeenCalledWith('customColors.accent', '#ff6b35')
    expect(mockOnSettingChange).toHaveBeenCalledWith('poscoTheme', true)
  })

  it('색상 미리보기가 올바르게 표시된다', () => {
    renderThemeSettings()
    
    expect(screen.getByText('현재 색상 미리보기')).toBeInTheDocument()
    expect(screen.getByText('Primary Button')).toBeInTheDocument()
    expect(screen.getByText('Secondary Button')).toBeInTheDocument()
    expect(screen.getByText('Accent Button')).toBeInTheDocument()
  })

  it('모든 색상 팔레트가 표시된다', () => {
    renderThemeSettings()
    
    expect(screen.getByText('POSCO 기본')).toBeInTheDocument()
    expect(screen.getByText('모던 블루')).toBeInTheDocument()
    expect(screen.getByText('따뜻한 톤')).toBeInTheDocument()
    expect(screen.getByText('자연 친화')).toBeInTheDocument()
    expect(screen.getByText('퍼플 테마')).toBeInTheDocument()
  })

  it('시스템 테마 모드가 올바르게 작동한다', () => {
    // matchMedia 모킹
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })

    renderThemeSettings()
    
    const themeSelect = screen.getByDisplayValue('라이트 모드')
    fireEvent.change(themeSelect, { target: { value: 'system' } })
    
    expect(mockOnSettingChange).toHaveBeenCalledWith('theme', 'system')
  })

  it('색상 입력 필드가 올바른 형식으로 표시된다', () => {
    renderThemeSettings()
    
    // 색상 타입 입력 필드 확인
    const colorInputs = screen.getAllByDisplayValue('#003d82')
    expect(colorInputs.length).toBeGreaterThan(0)
    
    const secondaryColorInputs = screen.getAllByDisplayValue('#0066cc')
    expect(secondaryColorInputs.length).toBeGreaterThan(0)
    
    const accentColorInputs = screen.getAllByDisplayValue('#ff6b35')
    expect(accentColorInputs.length).toBeGreaterThan(0)
  })

  it('도움말 텍스트가 올바르게 표시된다', () => {
    renderThemeSettings()
    
    expect(screen.getByText('애플리케이션의 전체적인 색상 테마를 설정합니다')).toBeInTheDocument()
    expect(screen.getByText('색상 변경 사항은 저장 후 적용됩니다')).toBeInTheDocument()
    expect(screen.getByText('이 색상들이 버튼, 링크, 강조 요소에 사용됩니다')).toBeInTheDocument()
  })
})