/**
 * WatchHamster 시스템 Context Provider
 * 전체 애플리케이션에서 WatchHamster 시스템 상태와 기능을 제공
 */

import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { useWatchHamsterSystem } from '../hooks/useWatchHamsterSystem'
import { useAppStore } from '../stores/useAppStore'
import type { 
  SystemMetrics, 
  ServiceInfo, 
  NewsStatus 
} from '../types'

// Context 타입 정의
interface WatchHamsterContextType {
  // 상태
  isConnected: boolean
  connectionStatus: string
  systemMetrics: SystemMetrics | null
  services: ServiceInfo[]
  newsStatus: NewsStatus[]
  loading: Record<string, boolean>
  errors: Record<string, string | null>

  // 시스템 제어
  startSystem: () => Promise<any>
  stopSystem: () => Promise<any>
  restartSystem: () => Promise<any>

  // 서비스 제어
  startService: (serviceId: string) => Promise<any>
  stopService: (serviceId: string) => Promise<any>
  restartService: (serviceId: string) => Promise<any>

  // 뉴스 관리
  refreshNewsData: (newsTypes?: string[], force?: boolean) => Promise<any>

  // 데이터 새로고침
  refreshAllData: () => Promise<void>
  fetchSystemStatus: () => Promise<any>
  fetchServices: () => Promise<any>
  fetchNewsStatus: () => Promise<any>

  // WebSocket 제어
  reconnectWebSocket: () => void

  // 유틸리티
  getServiceById: (id: string) => ServiceInfo | undefined
  getNewsStatusByType: (type: string) => NewsStatus | undefined
}

// Context 생성
const WatchHamsterContext = createContext<WatchHamsterContextType | null>(null)

// Provider Props
interface WatchHamsterProviderProps {
  children: ReactNode
  autoConnect?: boolean
  enableNotifications?: boolean
}

// Provider 컴포넌트
export const WatchHamsterProvider: React.FC<WatchHamsterProviderProps> = ({
  children,
  enableNotifications = true
}) => {
  // WatchHamster 시스템 훅 사용
  const watchHamsterSystem = useWatchHamsterSystem()
  
  // 스토어에서 유틸리티 함수들 가져오기
  const { getServiceById, getNewsStatusByType } = useAppStore()

  // 알림 권한 요청 (브라우저 알림)
  useEffect(() => {
    if (enableNotifications && 'Notification' in window) {
      if (Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
          console.log('알림 권한:', permission)
        })
      }
    }
  }, [enableNotifications])

  // Context 값 구성
  const contextValue: WatchHamsterContextType = {
    ...watchHamsterSystem,
    getServiceById,
    getNewsStatusByType
  }

  return (
    <WatchHamsterContext.Provider value={contextValue}>
      {children}
    </WatchHamsterContext.Provider>
  )
}

// Context 사용을 위한 커스텀 훅
export const useWatchHamster = (): WatchHamsterContextType => {
  const context = useContext(WatchHamsterContext)
  
  if (!context) {
    throw new Error('useWatchHamster는 WatchHamsterProvider 내부에서 사용되어야 합니다')
  }
  
  return context
}

// 개별 기능별 훅들 (성능 최적화)
export const useSystemControl = () => {
  const { startSystem, stopSystem, restartSystem, systemMetrics, loading } = useWatchHamster()
  
  return {
    startSystem,
    stopSystem,
    restartSystem,
    systemMetrics,
    isLoading: loading.metrics
  }
}

export const useServiceControl = () => {
  const { 
    services, 
    startService, 
    stopService, 
    restartService, 
    getServiceById,
    loading 
  } = useWatchHamster()
  
  return {
    services,
    startService,
    stopService,
    restartService,
    getServiceById,
    isLoading: loading.services
  }
}

export const useNewsControl = () => {
  const { 
    newsStatus, 
    refreshNewsData, 
    getNewsStatusByType,
    loading 
  } = useWatchHamster()
  
  return {
    newsStatus,
    refreshNewsData,
    getNewsStatusByType,
    isLoading: loading.news
  }
}

export const useConnectionStatus = () => {
  const { 
    isConnected, 
    connectionStatus, 
    reconnectWebSocket,
    errors 
  } = useWatchHamster()
  
  return {
    isConnected,
    connectionStatus,
    reconnectWebSocket,
    hasError: !!errors.connection || !!errors.websocket,
    errors
  }
}

// 고차 컴포넌트 (HOC) - WatchHamster 기능이 필요한 컴포넌트를 래핑
export const withWatchHamster = <P extends object>(
  Component: React.ComponentType<P>
) => {
  const WrappedComponent: React.FC<P> = (props) => {
    return (
      <WatchHamsterProvider>
        <Component {...props} />
      </WatchHamsterProvider>
    )
  }
  
  WrappedComponent.displayName = `withWatchHamster(${Component.displayName || Component.name})`
  
  return WrappedComponent
}

export default WatchHamsterProvider