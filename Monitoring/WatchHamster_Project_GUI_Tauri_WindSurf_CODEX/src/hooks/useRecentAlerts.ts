import { useState, useEffect, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiService } from '../services/api'
import { LogEntry } from '../types'
import { useWebSocket } from './useWebSocket'

interface AlertEntry {
  id: string
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
  service: string
  message: string
  details?: string
  acknowledged?: boolean
}

interface UseRecentAlertsOptions {
  refreshInterval?: number
  enableRealtime?: boolean
  maxAlerts?: number
  alertLevels?: string[]
}

interface UseRecentAlertsReturn {
  alerts: AlertEntry[]
  isLoading: boolean
  error: string | null
  lastUpdated: Date | null
  refreshAlerts: () => Promise<void>
  acknowledgeAlert: (alertId: string) => void
  isConnected: boolean
  unacknowledgedCount: number
}

export const useRecentAlerts = (options: UseRecentAlertsOptions = {}): UseRecentAlertsReturn => {
  const {
    refreshInterval = 30000, // 30초마다 새로고침
    enableRealtime = true,
    maxAlerts = 50,
    alertLevels = ['INFO', 'WARN', 'ERROR', 'CRITICAL']
  } = options

  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState<Set<string>>(new Set())

  // React Query를 사용한 최근 로그 조회 (알림으로 변환)
  const {
    data: rawAlerts = [],
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['recentAlerts', maxAlerts, alertLevels],
    queryFn: async () => {
      try {
        // 최근 로그를 가져와서 알림으로 변환
        const response = await apiService.getLogs({
          limit: maxAlerts.toString(),
          levels: alertLevels.join(','),
          page: '1'
        })
        
        const alerts: AlertEntry[] = response.logs.map((log: LogEntry) => ({
          id: log.id,
          timestamp: log.timestamp,
          level: log.level as 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL',
          service: log.service || 'system',
          message: log.message,
          details: log.details ? JSON.stringify(log.details, null, 2) : undefined,
          acknowledged: acknowledgedAlerts.has(log.id)
        }))

        // 시간순으로 정렬 (최신순)
        alerts.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        
        setLastUpdated(new Date())
        return alerts
      } catch (err) {
        console.error('최근 알림 조회 실패:', err)
        return []
      }
    },
    refetchInterval: refreshInterval,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
    staleTime: 15000, // 15초 동안 캐시 유지
  })

  // 확인된 알림 상태를 반영한 최종 알림 목록
  const alerts = rawAlerts.map(alert => ({
    ...alert,
    acknowledged: acknowledgedAlerts.has(alert.id)
  }))

  // WebSocket을 통한 실시간 업데이트
  const { isConnected: wsConnected } = useWebSocket({
    enabled: enableRealtime,
    onMessage: useCallback((message) => {
      if (message.type === 'log_update' || message.type === 'alert' || message.type === 'system_alert') {
        // 새로운 로그나 알림이 오면 쿼리 무효화
        refetch()
        setLastUpdated(new Date())
      }
    }, [refetch])
  })

  useEffect(() => {
    setIsConnected(wsConnected)
  }, [wsConnected])

  // 수동 새로고침 함수
  const refreshAlerts = useCallback(async () => {
    try {
      await refetch()
      setLastUpdated(new Date())
    } catch (err) {
      console.error('알림 새로고침 실패:', err)
      throw err
    }
  }, [refetch])

  // 알림 확인 처리
  const acknowledgeAlert = useCallback((alertId: string) => {
    setAcknowledgedAlerts(prev => new Set([...prev, alertId]))
  }, [])

  // 확인되지 않은 알림 개수
  const unacknowledgedCount = alerts.filter(alert => !alert.acknowledged).length

  // 로컬 스토리지에서 확인된 알림 목록 복원
  useEffect(() => {
    try {
      const stored = localStorage.getItem('acknowledgedAlerts')
      if (stored) {
        const alertIds = JSON.parse(stored)
        setAcknowledgedAlerts(new Set(alertIds))
      }
    } catch (err) {
      console.error('확인된 알림 목록 복원 실패:', err)
    }
  }, [])

  // 확인된 알림 목록을 로컬 스토리지에 저장
  useEffect(() => {
    try {
      const alertIds = Array.from(acknowledgedAlerts)
      localStorage.setItem('acknowledgedAlerts', JSON.stringify(alertIds))
    } catch (err) {
      console.error('확인된 알림 목록 저장 실패:', err)
    }
  }, [acknowledgedAlerts])

  // 오래된 확인 상태 정리 (24시간 이상 된 것들)
  useEffect(() => {
    const cleanup = () => {
      const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
      const validAlertIds = alerts
        .filter(alert => new Date(alert.timestamp) > oneDayAgo)
        .map(alert => alert.id)
      
      setAcknowledgedAlerts(prev => {
        const filtered = Array.from(prev).filter(id => validAlertIds.includes(id))
        return new Set(filtered)
      })
    }

    // 1시간마다 정리
    const interval = setInterval(cleanup, 60 * 60 * 1000)
    return () => clearInterval(interval)
  }, [alerts])

  return {
    alerts,
    isLoading,
    error: error?.message || null,
    lastUpdated,
    refreshAlerts,
    acknowledgeAlert,
    isConnected,
    unacknowledgedCount
  }
}