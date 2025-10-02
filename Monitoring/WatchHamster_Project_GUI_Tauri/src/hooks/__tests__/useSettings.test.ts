import { renderHook, act, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { useSettings, AppSettings } from '../useSettings'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { it } from 'date-fns/locale'
import { beforeEach } from 'node:test'
import { describe } from 'node:test'

// localStorage 모킹
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
}

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
})

// API 모킹
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

// useToast 모킹
const mockToast = vi.fn()
vi.mock('@chakra-ui/react', () => ({
  useToast: () => mockToast,
}))

describe('useSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLocalStorage.getItem.mockReturnValue(null)
  })

  it('기본 설정으로 초기화된다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.settings.autoRefresh).toBe(true)
    expect(result.current.settings.refreshInterval).toBe(5)
    expect(result.current.settings.language).toBe('ko')
    expect(result.current.settings.theme).toBe('light')
  })

  it('로컬 스토리지에서 설정을 로드한다', async () => {
    const savedSettings = {
      autoRefresh: false,
      refreshInterval: 10,
      language: 'en',
    }
    mockLocalStorage.getItem.mockReturnValue(JSON.stringify(savedSettings))

    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.settings.autoRefresh).toBe(false)
    expect(result.current.settings.refreshInterval).toBe(10)
    expect(result.current.settings.language).toBe('en')
  })

  it('개별 설정을 업데이트할 수 있다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    act(() => {
      result.current.updateSetting('autoRefresh', false)
    })

    expect(result.current.settings.autoRefresh).toBe(false)
  })

  it('중첩된 설정을 업데이트할 수 있다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    act(() => {
      result.current.updateNestedSetting('customColors.primary', '#ff0000')
    })

    expect(result.current.settings.customColors.primary).toBe('#ff0000')
  })

  it('설정을 저장할 수 있다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    let saveResult: boolean | undefined

    await act(async () => {
      saveResult = await result.current.saveSettings()
    })

    expect(saveResult).toBe(true)
    expect(mockLocalStorage.setItem).toHaveBeenCalled()
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '설정 저장됨',
        status: 'success',
      })
    )
  })

  it('설정을 초기화할 수 있다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // 먼저 설정 변경
    act(() => {
      result.current.updateSetting('autoRefresh', false)
    })

    expect(result.current.settings.autoRefresh).toBe(false)

    // 초기화
    let resetResult: boolean | undefined

    await act(async () => {
      resetResult = await result.current.resetSettings()
    })

    expect(resetResult).toBe(true)
    expect(result.current.settings.autoRefresh).toBe(true)
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('watchhamster-settings')
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '설정 초기화됨',
        status: 'info',
      })
    )
  })

  it('설정을 내보낼 수 있다', async () => {
    // Blob과 URL 모킹
    global.Blob = vi.fn().mockImplementation((content, options) => ({
      content,
      options,
    }))

    global.URL = {
      createObjectURL: vi.fn().mockReturnValue('mock-url'),
      revokeObjectURL: vi.fn(),
    } as any

    // DOM 요소 모킹
    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    }
    const mockCreateElement = vi.fn().mockReturnValue(mockLink)
    const mockAppendChild = vi.fn()
    const mockRemoveChild = vi.fn()

    Object.defineProperty(document, 'createElement', {
      value: mockCreateElement,
    })
    Object.defineProperty(document.body, 'appendChild', {
      value: mockAppendChild,
    })
    Object.defineProperty(document.body, 'removeChild', {
      value: mockRemoveChild,
    })

    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    act(() => {
      result.current.exportSettings()
    })

    expect(mockCreateElement).toHaveBeenCalledWith('a')
    expect(mockLink.click).toHaveBeenCalled()
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '설정 내보내기 완료',
        status: 'success',
      })
    )
  })

  it('설정을 가져올 수 있다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const mockFile = new File(
      [JSON.stringify({ autoRefresh: false, language: 'en' })],
      'settings.json',
      { type: 'application/json' }
    )

    let importResult: boolean | undefined

    await act(async () => {
      importResult = await result.current.importSettings(mockFile)
    })

    expect(importResult).toBe(true)
    expect(result.current.settings.autoRefresh).toBe(false)
    expect(result.current.settings.language).toBe('en')
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '설정 가져오기 완료',
        status: 'success',
      })
    )
  })

  it('잘못된 설정 파일 가져오기 시 오류를 처리한다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const mockFile = new File(['invalid json'], 'settings.json', {
      type: 'application/json',
    })

    let importResult: boolean | undefined

    await act(async () => {
      importResult = await result.current.importSettings(mockFile)
    })

    expect(importResult).toBe(false)
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '설정 가져오기 실패',
        status: 'error',
      })
    )
  })

  it('웹훅 테스트를 수행할 수 있다', async () => {
    const api = await import('../../services/api')
    vi.mocked(api.default.post).mockResolvedValue({ data: { success: true } })

    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // 웹훅 URL 설정
    act(() => {
      result.current.updateSetting('webhookUrl', 'https://discord.com/api/webhooks/123/abc')
    })

    let testResult: boolean | undefined

    await act(async () => {
      testResult = await result.current.testWebhook()
    })

    expect(testResult).toBe(true)
    expect(api.default.post).toHaveBeenCalledWith('/api/webhook/test', {
      url: 'https://discord.com/api/webhooks/123/abc',
      message: 'WatchHamster 웹훅 테스트 메시지입니다.',
    })
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '웹훅 테스트 성공',
        status: 'success',
      })
    )
  })

  it('웹훅 URL이 없을 때 테스트 시 경고를 표시한다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    let testResult: boolean | undefined

    await act(async () => {
      testResult = await result.current.testWebhook()
    })

    expect(testResult).toBe(false)
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '웹훅 URL 없음',
        status: 'warning',
      })
    )
  })

  it('저장 중 상태를 올바르게 관리한다', async () => {
    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.isSaving).toBe(false)

    const savePromise = act(async () => {
      return result.current.saveSettings()
    })

    // 저장 중에는 isSaving이 true여야 함
    expect(result.current.isSaving).toBe(true)

    await savePromise

    // 저장 완료 후에는 isSaving이 false여야 함
    expect(result.current.isSaving).toBe(false)
  })
})