import { useState, useEffect, useCallback } from 'react'
import { useToast } from '@chakra-ui/react'
import { apiService } from '../services/api'

export interface AppSettings {
  // 일반 설정
  autoRefresh: boolean
  refreshInterval: number
  language: string
  notifications: boolean

  // 테마 설정
  theme: 'light' | 'dark' | 'system'
  poscoTheme: boolean
  customColors: {
    primary: string
    secondary: string
    accent: string
  }

  // 알림 설정
  systemAlerts: boolean
  serviceAlerts: boolean
  errorAlerts: boolean
  alertPriority: {
    system: 'high' | 'medium' | 'low'
    service: 'high' | 'medium' | 'low'
    error: 'high' | 'medium' | 'low'
  }
  webhookUrl: string
  webhookEnabled: boolean

  // 고급 설정
  logLevel: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  maxLogEntries: number
  backupEnabled: boolean
  backupInterval: number
  performanceMode: boolean
  debugMode: boolean
}

const defaultSettings: AppSettings = {
  // 일반 설정
  autoRefresh: true,
  refreshInterval: 5,
  language: 'ko',
  notifications: true,

  // 테마 설정
  theme: 'light',
  poscoTheme: true,
  customColors: {
    primary: '#003d82',
    secondary: '#0066cc',
    accent: '#ff6b35',
  },

  // 알림 설정
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

  // 고급 설정
  logLevel: 'INFO',
  maxLogEntries: 1000,
  backupEnabled: true,
  backupInterval: 24,
  performanceMode: false,
  debugMode: false,
}

export const useSettings = () => {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const toast = useToast()

  // 설정 로드
  const loadSettings = useCallback(async () => {
    try {
      setIsLoading(true)
      
      // 로컬 스토리지에서 설정 로드
      const savedSettings = localStorage.getItem('watchhamster-settings')
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings)
        setSettings({ ...defaultSettings, ...parsed })
      }

      // 서버에서 설정 동기화 (선택적)
      try {
        const response = await apiService.getSettings()
        if (response) {
          setSettings(prev => ({ ...prev, ...response }))
        }
      } catch (error) {
        console.warn('서버 설정 로드 실패:', error)
      }
    } catch (error) {
      console.error('설정 로드 오류:', error)
      toast({
        title: '설정 로드 실패',
        description: '기본 설정을 사용합니다',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }, [toast])

  // 설정 저장
  const saveSettings = useCallback(async (newSettings?: Partial<AppSettings>) => {
    try {
      setIsSaving(true)
      
      const settingsToSave = newSettings ? { ...settings, ...newSettings } : settings
      
      // 로컬 스토리지에 저장
      localStorage.setItem('watchhamster-settings', JSON.stringify(settingsToSave))
      
      // 서버에 저장 (선택적)
      try {
        await apiService.saveSettings(settingsToSave)
      } catch (error) {
        console.warn('서버 설정 저장 실패:', error)
      }

      if (newSettings) {
        setSettings(settingsToSave)
      }

      toast({
        title: '설정 저장됨',
        description: '모든 설정이 성공적으로 저장되었습니다',
        status: 'success',
        duration: 2000,
        isClosable: true,
      })

      return true
    } catch (error) {
      console.error('설정 저장 오류:', error)
      toast({
        title: '설정 저장 실패',
        description: '설정을 저장하는 중 오류가 발생했습니다',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return false
    } finally {
      setIsSaving(false)
    }
  }, [settings, toast])

  // 개별 설정 업데이트
  const updateSetting = useCallback((key: keyof AppSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }))
  }, [])

  // 중첩된 설정 업데이트 (예: customColors.primary)
  const updateNestedSetting = useCallback((path: string, value: any) => {
    setSettings(prev => {
      const keys = path.split('.')
      const newSettings = { ...prev }
      let current: any = newSettings

      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] }
        current = current[keys[i]]
      }

      current[keys[keys.length - 1]] = value
      return newSettings
    })
  }, [])

  // 설정 초기화
  const resetSettings = useCallback(async () => {
    try {
      setSettings(defaultSettings)
      localStorage.removeItem('watchhamster-settings')
      
      // 서버에서도 초기화
      try {
        await apiService.resetSettings()
      } catch (error) {
        console.warn('서버 설정 초기화 실패:', error)
      }

      toast({
        title: '설정 초기화됨',
        description: '모든 설정이 기본값으로 초기화되었습니다',
        status: 'info',
        duration: 3000,
        isClosable: true,
      })

      return true
    } catch (error) {
      console.error('설정 초기화 오류:', error)
      toast({
        title: '설정 초기화 실패',
        description: '설정을 초기화하는 중 오류가 발생했습니다',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return false
    }
  }, [toast])

  // 설정 내보내기
  const exportSettings = useCallback(() => {
    try {
      const dataStr = JSON.stringify(settings, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `watchhamster-settings-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)

      toast({
        title: '설정 내보내기 완료',
        description: '설정 파일이 다운로드되었습니다',
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (error) {
      console.error('설정 내보내기 오류:', error)
      toast({
        title: '설정 내보내기 실패',
        description: '설정을 내보내는 중 오류가 발생했습니다',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }, [settings, toast])

  // 설정 가져오기
  const importSettings = useCallback((file: File) => {
    return new Promise<boolean>((resolve) => {
      const reader = new FileReader()
      
      reader.onload = async (e) => {
        try {
          const content = e.target?.result as string
          const importedSettings = JSON.parse(content)
          
          // 설정 유효성 검사
          const validatedSettings = { ...defaultSettings, ...importedSettings }
          
          setSettings(validatedSettings)
          await saveSettings(validatedSettings)
          
          toast({
            title: '설정 가져오기 완료',
            description: '설정이 성공적으로 가져와졌습니다',
            status: 'success',
            duration: 2000,
            isClosable: true,
          })
          
          resolve(true)
        } catch (error) {
          console.error('설정 가져오기 오류:', error)
          toast({
            title: '설정 가져오기 실패',
            description: '올바른 설정 파일이 아닙니다',
            status: 'error',
            duration: 3000,
            isClosable: true,
          })
          resolve(false)
        }
      }
      
      reader.readAsText(file)
    })
  }, [saveSettings, toast])

  // 웹훅 테스트
  const testWebhook = useCallback(async () => {
    if (!settings.webhookUrl) {
      toast({
        title: '웹훅 URL 없음',
        description: '먼저 웹훅 URL을 설정해주세요',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return false
    }

    try {
      await apiService.testWebhook({
        url: settings.webhookUrl,
        message: 'WatchHamster 웹훅 테스트 메시지입니다.',
      })

      toast({
        title: '웹훅 테스트 성공',
        description: '웹훅이 정상적으로 전송되었습니다',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })

      return true
    } catch (error) {
      console.error('웹훅 테스트 오류:', error)
      toast({
        title: '웹훅 테스트 실패',
        description: '웹훅 전송에 실패했습니다',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return false
    }
  }, [settings.webhookUrl, toast])

  // 컴포넌트 마운트 시 설정 로드
  useEffect(() => {
    loadSettings()
  }, [loadSettings])

  return {
    settings,
    isLoading,
    isSaving,
    updateSetting,
    updateNestedSetting,
    saveSettings,
    resetSettings,
    exportSettings,
    importSettings,
    testWebhook,
    loadSettings,
  }
}