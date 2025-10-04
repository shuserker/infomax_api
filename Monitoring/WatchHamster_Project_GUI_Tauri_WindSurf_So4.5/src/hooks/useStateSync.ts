/**
 * 상태 동기화 훅
 * 로컬 상태와 서버 상태 간의 동기화 관리
 */

import { useEffect, useCallback, useRef } from 'react'
import { useAppStore } from '../stores/useAppStore'
import { apiService } from '../services/api'

interface UseStateSyncOptions {
  enableAutoSync?: boolean
  syncInterval?: number
  syncOnFocus?: boolean
  syncOnVisibilityChange?: boolean
  onSyncError?: (error: any) => void
  onSyncSuccess?: () => void
}

export const useStateSync = (options: UseStateSyncOptions = {}) => {
  const {
    enableAutoSync = true,
    syncInterval = 30000, // 30초
    syncOnFocus = true,
    syncOnVisibilityChange = true,
    onSyncError,
    onSyncSuccess
  } = options

  const syncTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastSyncRef = useRef<Date | null>(null)
  const isSyncingRef = useRef(false)

  const {
    isConnected,
    settings,
    updateSystemMetrics,
    updateServices,
    updateNewsStatus,
    updateSettings,
    setLoading,
    setError,
    addNotification
  } = useAppStore()

  // 동기화 실행
  const performSync = useCallback(async (force: boolean = false) => {
    // 이미 동기화 중이거나 연결되지 않은 경우 스킵
    if (isSyncingRef.current || (!isConnected && !force)) {
      return false
    }

    // 마지막 동기화로부터 최소 간격 확인
    if (!force && lastSyncRef.current) {
      const timeSinceLastSync = Date.now() - lastSyncRef.current.getTime()
      if (timeSinceLastSync < 5000) { // 5초 미만이면 스킵
        return false
      }
    }

    isSyncingRef.current = true
    console.log('상태 동기화 시작...')

    try {
      // 병렬로 모든 데이터 동기화
      const [systemStatus, services, newsStatus, serverSettings] = await Promise.allSettled([
        apiService.getSystemStatus(),
        apiService.getServices(),
        apiService.getNewsStatus(),
        apiService.getSettings().catch(() => null) // 설정은 실패해도 계속 진행
      ])

      // 시스템 상태 업데이트
      if (systemStatus.status === 'fulfilled' && systemStatus.value?.metrics) {
        updateSystemMetrics(systemStatus.value.metrics)
      }

      // 서비스 목록 업데이트
      if (services.status === 'fulfilled' && services.value) {
        updateServices(services.value)
      }

      // 뉴스 상태 업데이트
      if (newsStatus.status === 'fulfilled' && newsStatus.value) {
        const newsArray = Array.isArray(newsStatus.value) ? newsStatus.value : [newsStatus.value]
        updateNewsStatus(newsArray)
      }

      // 서버 설정 동기화 (로컬 설정과 병합)
      if (serverSettings.status === 'fulfilled' && serverSettings.value) {
        updateSettings(serverSettings.value)
      }

      lastSyncRef.current = new Date()
      onSyncSuccess?.()
      
      console.log('상태 동기화 완료')
      return true

    } catch (error) {
      console.error('상태 동기화 실패:', error)
      
      setError('api', error instanceof Error ? error.message : '동기화 실패')
      onSyncError?.(error)
      
      return false
    } finally {
      isSyncingRef.current = false
    }
  }, [
    isConnected,
    updateSystemMetrics,
    updateServices,
    updateNewsStatus,
    updateSettings,
    setError,
    onSyncError,
    onSyncSuccess
  ])

  // 자동 동기화 스케줄링
  const scheduleSync = useCallback(() => {
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current)
    }

    if (enableAutoSync) {
      syncTimeoutRef.current = setTimeout(() => {
        performSync()
        scheduleSync() // 다음 동기화 스케줄링
      }, syncInterval)
    }
  }, [enableAutoSync, syncInterval, performSync])

  // 수동 동기화
  const manualSync = useCallback(async () => {
    setLoading('metrics', true)
    setLoading('services', true)
    setLoading('news', true)

    try {
      const success = await performSync(true)
      
      if (success) {
        addNotification({
          title: '동기화 완료',
          message: '모든 데이터가 최신 상태로 업데이트되었습니다',
          type: 'success'
        })
      }
      
      return success
    } finally {
      setLoading('metrics', false)
      setLoading('services', false)
      setLoading('news', false)
    }
  }, [performSync, setLoading, addNotification])

  // 설정 동기화 (양방향)
  const syncSettings = useCallback(async (localSettings?: any) => {
    try {
      if (localSettings) {
        // 로컬 설정을 서버로 전송
        await apiService.saveSettings(localSettings)
        console.log('설정이 서버에 저장되었습니다')
      } else {
        // 서버 설정을 로컬로 가져오기
        const serverSettings = await apiService.getSettings()
        if (serverSettings) {
          updateSettings(serverSettings)
          console.log('서버 설정이 로컬에 적용되었습니다')
        }
      }
      
      return true
    } catch (error) {
      console.error('설정 동기화 실패:', error)
      return false
    }
  }, [updateSettings])

  // 포커스 이벤트 핸들러
  const handleFocus = useCallback(() => {
    if (syncOnFocus) {
      console.log('포커스 감지 - 동기화 실행')
      performSync()
    }
  }, [syncOnFocus, performSync])

  // 가시성 변경 이벤트 핸들러
  const handleVisibilityChange = useCallback(() => {
    if (syncOnVisibilityChange && !document.hidden) {
      console.log('페이지 가시성 변경 - 동기화 실행')
      performSync()
    }
  }, [syncOnVisibilityChange, performSync])

  // 연결 상태 변경 시 동기화
  useEffect(() => {
    if (isConnected) {
      console.log('연결 복구 - 동기화 실행')
      performSync()
    }
  }, [isConnected, performSync])

  // 자동 동기화 스케줄링
  useEffect(() => {
    scheduleSync()
    
    return () => {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current)
      }
    }
  }, [scheduleSync])

  // 이벤트 리스너 등록
  useEffect(() => {
    if (syncOnFocus) {
      window.addEventListener('focus', handleFocus)
    }
    
    if (syncOnVisibilityChange) {
      document.addEventListener('visibilitychange', handleVisibilityChange)
    }

    return () => {
      if (syncOnFocus) {
        window.removeEventListener('focus', handleFocus)
      }
      
      if (syncOnVisibilityChange) {
        document.removeEventListener('visibilitychange', handleVisibilityChange)
      }
    }
  }, [syncOnFocus, syncOnVisibilityChange, handleFocus, handleVisibilityChange])

  // 동기화 상태 정보
  const getSyncInfo = useCallback(() => {
    return {
      lastSync: lastSyncRef.current,
      isSyncing: isSyncingRef.current,
      nextSync: syncTimeoutRef.current ? new Date(Date.now() + syncInterval) : null,
      autoSyncEnabled: enableAutoSync
    }
  }, [syncInterval, enableAutoSync])

  return {
    // 동기화 제어
    manualSync,
    performSync,
    syncSettings,

    // 동기화 상태
    getSyncInfo,
    isSyncing: isSyncingRef.current,
    lastSync: lastSyncRef.current,

    // 설정
    enableAutoSync,
    syncInterval
  }
}

export default useStateSync