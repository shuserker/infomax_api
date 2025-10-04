import { useState, useEffect, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiService } from '../services/api'
import { NewsStatus } from '../types'
import { useWebSocket } from './useWebSocket'

interface UseNewsStatusOptions {
  refreshInterval?: number
  enableRealtime?: boolean
  newsTypes?: string[]
}

interface UseNewsStatusReturn {
  newsData: NewsStatus[]
  isLoading: boolean
  error: string | null
  lastUpdated: Date | null
  refreshNews: () => Promise<void>
  isConnected: boolean
}

export const useNewsStatus = (options: UseNewsStatusOptions = {}): UseNewsStatusReturn => {
  const {
    refreshInterval = 30000, // 30초마다 새로고침
    enableRealtime = true,
    newsTypes = ['exchange-rate', 'newyork-market-watch', 'kospi-close']
  } = options

  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  // React Query를 사용한 뉴스 상태 조회
  const {
    data: newsData = [],
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['newsStatus', newsTypes],
    queryFn: async () => {
      try {
        const response = await apiService.getNewsStatus()
        
        // 응답이 배열인지 단일 객체인지 확인
        let newsArray: NewsStatus[]
        if (Array.isArray(response)) {
          newsArray = response
        } else {
          newsArray = [response as NewsStatus]
        }

        // 요청된 뉴스 타입만 필터링
        const filteredNews = newsArray.filter(news => 
          newsTypes.includes(news.type)
        )

        // 누락된 뉴스 타입에 대해 기본값 생성
        const existingTypes = filteredNews.map(news => news.type)
        const missingTypes = newsTypes.filter(type => !existingTypes.includes(type))
        
        const defaultNews: NewsStatus[] = missingTypes.map(type => ({
          type,
          status: 'error',
          last_update: new Date().toISOString(),
          error_message: '데이터를 가져올 수 없습니다'
        }))

        const allNews = [...filteredNews, ...defaultNews]
        
        // 타입 순서대로 정렬
        const sortedNews = newsTypes.map(type => 
          allNews.find(news => news.type === type)
        ).filter(Boolean) as NewsStatus[]

        setLastUpdated(new Date())
        return sortedNews
      } catch (err) {
        console.error('뉴스 상태 조회 실패:', err)
        
        // 오류 시 기본값 반환
        const errorNews: NewsStatus[] = newsTypes.map(type => ({
          type,
          status: 'error',
          last_update: new Date().toISOString(),
          error_message: err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다'
        }))
        
        return errorNews
      }
    },
    refetchInterval: refreshInterval,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    staleTime: 10000, // 10초 동안 캐시 유지
  })

  // WebSocket을 통한 실시간 업데이트
  const { isConnected: wsConnected } = useWebSocket({
    enabled: enableRealtime,
    onMessage: useCallback((message) => {
      if (message.type === 'news_update' || message.type === 'status_update') {
        // 뉴스 업데이트 메시지를 받으면 쿼리 무효화
        refetch()
        setLastUpdated(new Date())
      }
    }, [refetch])
  })

  useEffect(() => {
    setIsConnected(wsConnected)
  }, [wsConnected])

  // 수동 새로고침 함수
  const refreshNews = useCallback(async () => {
    try {
      await refetch()
      setLastUpdated(new Date())
    } catch (err) {
      console.error('뉴스 새로고침 실패:', err)
      throw err
    }
  }, [refetch])

  return {
    newsData,
    isLoading,
    error: error?.message || null,
    lastUpdated,
    refreshNews,
    isConnected
  }
}