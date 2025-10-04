import { useState, useEffect, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiService } from '../services/api'
import { useWebSocket } from './useWebSocket'

interface GitStatus {
  branch: string
  lastCommit: string
  hasUncommittedChanges: boolean
  hasConflicts: boolean
  remoteStatus: 'up-to-date' | 'ahead' | 'behind' | 'diverged'
  commitHash?: string
  commitMessage?: string
  commitAuthor?: string
  commitDate?: string
  aheadCount?: number
  behindCount?: number
}

interface UseGitStatusOptions {
  refreshInterval?: number
  enableRealtime?: boolean
}

interface UseGitStatusReturn {
  gitStatus: GitStatus | null
  isLoading: boolean
  error: string | null
  lastUpdated: Date | null
  refreshGitStatus: () => Promise<void>
  isConnected: boolean
}

export const useGitStatus = (options: UseGitStatusOptions = {}): UseGitStatusReturn => {
  const {
    refreshInterval = 60000, // 1분마다 새로고침
    enableRealtime = true
  } = options

  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  // React Query를 사용한 Git 상태 조회
  const {
    data: gitStatus = null,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['gitStatus'],
    queryFn: async () => {
      try {
        // POSCO 시스템 상태에서 Git 정보 가져오기
        const response = await apiService.getPoscoStatus()
        
        if (response.git_status) {
          const gitData = response.git_status
          
          const status: GitStatus = {
            branch: gitData.current_branch || response.current_branch || 'unknown',
            lastCommit: gitData.last_commit || gitData.commit_message || 'No commits',
            hasUncommittedChanges: gitData.has_uncommitted_changes || false,
            hasConflicts: gitData.has_conflicts || false,
            remoteStatus: gitData.remote_status || 'up-to-date',
            commitHash: gitData.commit_hash,
            commitMessage: gitData.commit_message,
            commitAuthor: gitData.commit_author,
            commitDate: gitData.commit_date,
            aheadCount: gitData.ahead_count,
            behindCount: gitData.behind_count
          }
          
          setLastUpdated(new Date())
          return status
        }
        
        // Git 상태가 없는 경우 기본값 반환
        return {
          branch: response.current_branch || 'main',
          lastCommit: 'Git 정보를 가져올 수 없습니다',
          hasUncommittedChanges: false,
          hasConflicts: false,
          remoteStatus: 'up-to-date' as const
        }
      } catch (err) {
        console.error('Git 상태 조회 실패:', err)
        
        // 오류 시 null 반환 (컴포넌트에서 오류 상태 처리)
        return null
      }
    },
    refetchInterval: refreshInterval,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
    staleTime: 30000, // 30초 동안 캐시 유지
  })

  // WebSocket을 통한 실시간 업데이트
  const { isConnected: wsConnected } = useWebSocket({
    enabled: enableRealtime,
    onMessage: useCallback((message) => {
      if (message.type === 'git_update' || message.type === 'system_update') {
        // Git 업데이트 메시지를 받으면 쿼리 무효화
        refetch()
        setLastUpdated(new Date())
      }
    }, [refetch])
  })

  useEffect(() => {
    setIsConnected(wsConnected)
  }, [wsConnected])

  // 수동 새로고침 함수
  const refreshGitStatus = useCallback(async () => {
    try {
      await refetch()
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Git 상태 새로고침 실패:', err)
      throw err
    }
  }, [refetch])

  return {
    gitStatus,
    isLoading,
    error: error?.message || null,
    lastUpdated,
    refreshGitStatus,
    isConnected
  }
}