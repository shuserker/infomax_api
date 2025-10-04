import { useState, useEffect, useCallback, useRef } from 'react'
import { SystemMetrics, ChartDataPoint } from '../types'

export interface RealtimeChartData {
  cpu: ChartDataPoint[]
  memory: ChartDataPoint[]
  disk: ChartDataPoint[]
  network: ChartDataPoint[]
}

export interface UseRealtimeChartOptions {
  maxDataPoints?: number
  updateInterval?: number
  enableCaching?: boolean
  cacheKey?: string
}

export interface UseRealtimeChartReturn {
  data: RealtimeChartData
  isLoading: boolean
  error: string | null
  addDataPoint: (metrics: SystemMetrics) => void
  clearData: () => void
  exportData: () => RealtimeChartData
  zoomRange: [number, number] | null
  setZoomRange: (range: [number, number] | null) => void
}

const DEFAULT_OPTIONS: Required<UseRealtimeChartOptions> = {
  maxDataPoints: 100,
  updateInterval: 5000,
  enableCaching: true,
  cacheKey: 'realtime-chart-data'
}

export const useRealtimeChart = (
  options: UseRealtimeChartOptions = {}
): UseRealtimeChartReturn => {
  const opts = { ...DEFAULT_OPTIONS, ...options }
  const [data, setData] = useState<RealtimeChartData>({
    cpu: [],
    memory: [],
    disk: [],
    network: []
  })
  const [isLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [zoomRange, setZoomRange] = useState<[number, number] | null>(null)
  
  const dataRef = useRef<RealtimeChartData>(data)
  const cacheTimeoutRef = useRef<NodeJS.Timeout>()

  // 캐시에서 데이터 로드
  useEffect(() => {
    if (opts.enableCaching) {
      try {
        const cachedData = localStorage.getItem(opts.cacheKey)
        if (cachedData) {
          const parsed = JSON.parse(cachedData) as RealtimeChartData
          setData(parsed)
          dataRef.current = parsed
        }
      } catch (err) {
        console.warn('캐시된 차트 데이터 로드 실패:', err)
      }
    }
  }, [opts.enableCaching, opts.cacheKey])

  // 데이터 캐싱 (디바운스)
  const cacheData = useCallback((newData: RealtimeChartData) => {
    if (!opts.enableCaching) return

    if (cacheTimeoutRef.current) {
      clearTimeout(cacheTimeoutRef.current)
    }

    cacheTimeoutRef.current = setTimeout(() => {
      try {
        localStorage.setItem(opts.cacheKey, JSON.stringify(newData))
      } catch (err) {
        console.warn('차트 데이터 캐싱 실패:', err)
      }
    }, 1000)
  }, [opts.enableCaching, opts.cacheKey])

  // 네트워크 상태를 숫자로 변환
  const getNetworkValue = (status: string): number => {
    switch (status) {
      case 'connected': return 100
      case 'limited': return 50
      case 'disconnected': return 0
      default: return 0
    }
  }

  // 새 데이터 포인트 추가
  const addDataPoint = useCallback((metrics: SystemMetrics) => {
    setError(null)
    
    try {
      const timestamp = new Date(metrics.timestamp).toISOString()
      const newPoint = {
        timestamp,
        cpu: {
          timestamp,
          value: metrics.cpu_percent,
          label: `CPU: ${metrics.cpu_percent.toFixed(1)}%`
        },
        memory: {
          timestamp,
          value: metrics.memory_percent,
          label: `메모리: ${metrics.memory_percent.toFixed(1)}%`
        },
        disk: {
          timestamp,
          value: metrics.disk_usage,
          label: `디스크: ${metrics.disk_usage.toFixed(1)}%`
        },
        network: {
          timestamp,
          value: getNetworkValue(metrics.network_status),
          label: `네트워크: ${metrics.network_status}`
        }
      }

      setData(prevData => {
        const newData = {
          cpu: [...prevData.cpu, newPoint.cpu].slice(-opts.maxDataPoints),
          memory: [...prevData.memory, newPoint.memory].slice(-opts.maxDataPoints),
          disk: [...prevData.disk, newPoint.disk].slice(-opts.maxDataPoints),
          network: [...prevData.network, newPoint.network].slice(-opts.maxDataPoints)
        }
        
        dataRef.current = newData
        cacheData(newData)
        return newData
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '데이터 추가 중 오류 발생'
      setError(errorMessage)
      console.error('차트 데이터 추가 실패:', err)
    }
  }, [opts.maxDataPoints, cacheData])

  // 데이터 초기화
  const clearData = useCallback(() => {
    const emptyData = {
      cpu: [],
      memory: [],
      disk: [],
      network: []
    }
    
    setData(emptyData)
    dataRef.current = emptyData
    setError(null)
    
    if (opts.enableCaching) {
      try {
        localStorage.removeItem(opts.cacheKey)
      } catch (err) {
        console.warn('캐시 데이터 삭제 실패:', err)
      }
    }
  }, [opts.enableCaching, opts.cacheKey])

  // 데이터 내보내기
  const exportData = useCallback((): RealtimeChartData => {
    return JSON.parse(JSON.stringify(dataRef.current))
  }, [])

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (cacheTimeoutRef.current) {
        clearTimeout(cacheTimeoutRef.current)
      }
    }
  }, [])

  return {
    data,
    isLoading,
    error,
    addDataPoint,
    clearData,
    exportData,
    zoomRange,
    setZoomRange
  }
}

// 차트 데이터 유틸리티 함수들
export const chartUtils = {
  // 시간 범위 필터링
  filterByTimeRange: (
    data: ChartDataPoint[],
    startTime: string,
    endTime: string
  ): ChartDataPoint[] => {
    const start = new Date(startTime).getTime()
    const end = new Date(endTime).getTime()
    
    return data.filter(point => {
      const pointTime = new Date(point.timestamp).getTime()
      return pointTime >= start && pointTime <= end
    })
  },

  // 데이터 다운샘플링 (성능 최적화)
  downsample: (
    data: ChartDataPoint[],
    targetPoints: number
  ): ChartDataPoint[] => {
    if (data.length <= targetPoints) return data
    
    const step = Math.floor(data.length / targetPoints)
    const result: ChartDataPoint[] = []
    
    for (let i = 0; i < data.length; i += step) {
      result.push(data[i])
    }
    
    return result
  },

  // 평균값 계산
  calculateAverage: (data: ChartDataPoint[]): number => {
    if (data.length === 0) return 0
    const sum = data.reduce((acc, point) => acc + point.value, 0)
    return sum / data.length
  },

  // 최대/최소값 찾기
  findMinMax: (data: ChartDataPoint[]): { min: number; max: number } => {
    if (data.length === 0) return { min: 0, max: 0 }
    
    let min = data[0].value
    let max = data[0].value
    
    for (const point of data) {
      if (point.value < min) min = point.value
      if (point.value > max) max = point.value
    }
    
    return { min, max }
  },

  // 시간 포맷팅
  formatTime: (timestamp: string): string => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  },

  // 날짜 포맷팅
  formatDate: (timestamp: string): string => {
    const date = new Date(timestamp)
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}