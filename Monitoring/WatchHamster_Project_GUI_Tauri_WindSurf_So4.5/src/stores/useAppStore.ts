/**
 * WatchHamster 애플리케이션 전역 상태 관리
 * Zustand를 사용한 중앙집중식 상태 관리
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type { 
  SystemMetrics, 
  ServiceInfo, 
  NewsStatus, 
  LogEntry, 
  AppSettings,
  WebhookHistory,
  AlertMessage
} from '../types'

// 상태 인터페이스 정의
interface AppState {
  // 연결 상태
  isConnected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error'
  lastHeartbeat: Date | null

  // 시스템 데이터
  systemMetrics: SystemMetrics | null
  services: ServiceInfo[]
  newsStatus: NewsStatus[]
  recentLogs: LogEntry[]
  alerts: AlertMessage[]
  webhookHistory: WebhookHistory[]

  // UI 상태
  settings: AppSettings
  notifications: Array<{
    id: string
    title: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    timestamp: Date
    read: boolean
  }>
  
  // 로딩 상태
  loading: {
    services: boolean
    metrics: boolean
    news: boolean
    logs: boolean
    settings: boolean
  }

  // 에러 상태
  errors: {
    connection: string | null
    api: string | null
    websocket: string | null
  }
}

// 액션 인터페이스 정의
interface AppActions {
  // 연결 상태 관리
  setConnectionStatus: (status: AppState['connectionStatus']) => void
  setConnected: (connected: boolean) => void
  setLastHeartbeat: (heartbeat: Date | null) => void

  // 시스템 데이터 업데이트
  updateSystemMetrics: (metrics: SystemMetrics) => void
  updateServices: (services: ServiceInfo[]) => void
  updateService: (serviceId: string, updates: Partial<ServiceInfo>) => void
  updateNewsStatus: (newsStatus: NewsStatus[]) => void
  updateSingleNewsStatus: (newsType: string, status: Partial<NewsStatus>) => void
  addLogEntry: (log: LogEntry) => void
  setRecentLogs: (logs: LogEntry[]) => void
  addAlert: (alert: AlertMessage) => void
  removeAlert: (alertId: string) => void
  clearAlerts: () => void
  addWebhookHistory: (webhook: WebhookHistory) => void

  // 설정 관리
  updateSettings: (settings: Partial<AppSettings>) => void
  resetSettings: () => void

  // 알림 관리
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp' | 'read'>) => void
  markNotificationRead: (id: string) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void

  // 로딩 상태 관리
  setLoading: (key: keyof AppState['loading'], loading: boolean) => void

  // 에러 상태 관리
  setError: (key: keyof AppState['errors'], error: string | null) => void
  clearErrors: () => void

  // 유틸리티 액션
  reset: () => void
  getServiceById: (id: string) => ServiceInfo | undefined
  getNewsStatusByType: (type: string) => NewsStatus | undefined
}

// 기본 설정
const defaultSettings: AppSettings = {
  autoRefresh: true,
  refreshInterval: 5000,
  language: 'ko',
  notifications: true,
  theme: 'light',
  poscoTheme: true,
  systemAlerts: true,
  serviceAlerts: true,
  errorAlerts: true,
  webhookUrl: '',
  logLevel: 'INFO',
  maxLogEntries: 1000,
  dashboardMode: 'detailed',  // 대시보드 모드 추가
  backupEnabled: false,
  backupInterval: 24
}

// 초기 상태
const initialState: AppState = {
  // 연결 상태
  isConnected: false,
  connectionStatus: 'disconnected',
  lastHeartbeat: null,

  // 시스템 데이터
  systemMetrics: null,
  services: [],
  newsStatus: [],
  recentLogs: [],
  alerts: [],
  webhookHistory: [],

  // UI 상태
  settings: defaultSettings,
  notifications: [],

  // 로딩 상태
  loading: {
    services: false,
    metrics: false,
    news: false,
    logs: false,
    settings: false
  },

  // 에러 상태
  errors: {
    connection: null,
    api: null,
    websocket: null
  }
}

// Zustand 스토어 생성
export const useAppStore = create<AppState & AppActions>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // 연결 상태 관리
        setConnectionStatus: (status) => 
          set({ connectionStatus: status }, false, 'setConnectionStatus'),

        setConnected: (connected) => 
          set({ isConnected: connected }, false, 'setConnected'),

        setLastHeartbeat: (heartbeat) => 
          set({ lastHeartbeat: heartbeat }, false, 'setLastHeartbeat'),

        // 시스템 데이터 업데이트
        updateSystemMetrics: (metrics) => 
          set({ systemMetrics: metrics }, false, 'updateSystemMetrics'),

        updateServices: (services) => 
          set({ services }, false, 'updateServices'),

        updateService: (serviceId, updates) => 
          set((state) => ({
            services: state.services.map(service =>
              service.id === serviceId ? { ...service, ...updates } : service
            )
          }), false, 'updateService'),

        updateNewsStatus: (newsStatus) => 
          set({ newsStatus }, false, 'updateNewsStatus'),

        updateSingleNewsStatus: (newsType, status) =>
          set((state) => ({
            newsStatus: state.newsStatus.map(news =>
              news.type === newsType ? { ...news, ...status } : news
            )
          }), false, 'updateSingleNewsStatus'),

        addLogEntry: (log) =>
          set((state) => ({
            recentLogs: [log, ...state.recentLogs.slice(0, state.settings.maxLogEntries - 1)]
          }), false, 'addLogEntry'),

        setRecentLogs: (logs) => 
          set({ recentLogs: logs }, false, 'setRecentLogs'),

        addAlert: (alert) =>
          set((state) => ({
            alerts: [alert, ...state.alerts.slice(0, 19)] // 최대 20개 유지
          }), false, 'addAlert'),

        removeAlert: (alertId) =>
          set((state) => ({
            alerts: state.alerts.filter(alert => alert.data.timestamp !== alertId)
          }), false, 'removeAlert'),

        clearAlerts: () => 
          set({ alerts: [] }, false, 'clearAlerts'),

        addWebhookHistory: (webhook) =>
          set((state) => ({
            webhookHistory: [webhook, ...state.webhookHistory.slice(0, 99)] // 최대 100개 유지
          }), false, 'addWebhookHistory'),

        // 설정 관리
        updateSettings: (newSettings) =>
          set((state) => ({
            settings: { ...state.settings, ...newSettings }
          }), false, 'updateSettings'),

        resetSettings: () => 
          set({ settings: defaultSettings }, false, 'resetSettings'),

        // 알림 관리
        addNotification: (notification) =>
          set((state) => ({
            notifications: [{
              ...notification,
              id: `notif_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
              timestamp: new Date(),
              read: false
            }, ...state.notifications.slice(0, 49)] // 최대 50개 유지
          }), false, 'addNotification'),

        markNotificationRead: (id) =>
          set((state) => ({
            notifications: state.notifications.map(notif =>
              notif.id === id ? { ...notif, read: true } : notif
            )
          }), false, 'markNotificationRead'),

        removeNotification: (id) =>
          set((state) => ({
            notifications: state.notifications.filter(notif => notif.id !== id)
          }), false, 'removeNotification'),

        clearNotifications: () => 
          set({ notifications: [] }, false, 'clearNotifications'),

        // 로딩 상태 관리
        setLoading: (key, loading) =>
          set((state) => ({
            loading: { ...state.loading, [key]: loading }
          }), false, 'setLoading'),

        // 에러 상태 관리
        setError: (key, error) =>
          set((state) => ({
            errors: { ...state.errors, [key]: error }
          }), false, 'setError'),

        clearErrors: () => 
          set({ errors: { connection: null, api: null, websocket: null } }, false, 'clearErrors'),

        // 유틸리티 액션
        reset: () => 
          set(initialState, false, 'reset'),

        getServiceById: (id) => {
          const state = get()
          return state.services.find(service => service.id === id)
        },

        getNewsStatusByType: (type) => {
          const state = get()
          return state.newsStatus.find(news => news.type === type)
        }
      }),
      {
        name: 'watchhamster-app-store',
        partialize: (state) => ({
          // 지속성이 필요한 상태만 저장
          settings: state.settings,
          notifications: state.notifications.filter(n => !n.read) // 읽지 않은 알림만 저장
        })
      }
    ),
    {
      name: 'WatchHamster App Store'
    }
  )
)

// 선택자 함수들 (성능 최적화를 위한)
export const useConnectionState = () => useAppStore((state) => ({
  isConnected: state.isConnected,
  connectionStatus: state.connectionStatus,
  lastHeartbeat: state.lastHeartbeat
}))

export const useSystemData = () => useAppStore((state) => ({
  systemMetrics: state.systemMetrics,
  services: state.services,
  newsStatus: state.newsStatus
}))

export const useAppSettings = () => useAppStore((state) => ({
  settings: state.settings,
  updateSettings: state.updateSettings,
  resetSettings: state.resetSettings
}))

export const useNotifications = () => useAppStore((state) => ({
  notifications: state.notifications,
  addNotification: state.addNotification,
  markNotificationRead: state.markNotificationRead,
  removeNotification: state.removeNotification,
  clearNotifications: state.clearNotifications
}))

export const useLoadingState = () => useAppStore((state) => ({
  loading: state.loading,
  setLoading: state.setLoading
}))

export const useErrorState = () => useAppStore((state) => ({
  errors: state.errors,
  setError: state.setError,
  clearErrors: state.clearErrors
}))

// 계산된 값들을 위한 선택자
export const useSystemHealth = () => useAppStore((state) => {
  if (!state.systemMetrics) return 'unknown'
  
  const { cpu_percent, memory_percent, disk_usage } = state.systemMetrics
  
  if (cpu_percent > 90 || memory_percent > 95 || disk_usage > 95) {
    return 'critical'
  } else if (cpu_percent > 70 || memory_percent > 80 || disk_usage > 80) {
    return 'warning'
  } else {
    return 'healthy'
  }
})

export const useServiceStats = () => useAppStore((state) => {
  const total = state.services.length
  const running = state.services.filter(s => s.status === 'running').length
  const stopped = state.services.filter(s => s.status === 'stopped').length
  const error = state.services.filter(s => s.status === 'error').length
  
  return { total, running, stopped, error }
})

export const useNewsStats = () => useAppStore((state) => {
  const total = state.newsStatus.length
  const latest = state.newsStatus.filter(n => n.status === 'latest').length
  const delayed = state.newsStatus.filter(n => n.status === 'delayed').length
  const error = state.newsStatus.filter(n => n.status === 'error').length
  
  return { total, latest, delayed, error }
})

export const useUnreadNotificationCount = () => useAppStore((state) => 
  state.notifications.filter(n => !n.read).length
)

export default useAppStore