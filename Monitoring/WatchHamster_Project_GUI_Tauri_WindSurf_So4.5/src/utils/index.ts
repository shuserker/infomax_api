/**
 * 유틸리티 함수들
 */

// 날짜 포맷팅
export const formatDate = (date: Date | string): string => {
  const d = new Date(date)
  return d.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// 타임스탬프 포맷팅 (formatDate와 동일하지만 명시적으로 분리)
export const formatTimestamp = (timestamp: Date | string): string => {
  return formatDate(timestamp)
}

// 상대 시간 포맷팅
export const formatRelativeTime = (date: Date | string): string => {
  const now = new Date()
  const target = new Date(date)
  const diffMs = now.getTime() - target.getTime()

  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) return `${diffSeconds}초 전`
  if (diffMinutes < 60) return `${diffMinutes}분 전`
  if (diffHours < 24) return `${diffHours}시간 전`
  return `${diffDays}일 전`
}

// 바이트 크기 포맷팅
export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 업타임 포맷팅
export const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (days > 0) return `${days}일 ${hours}시간 ${minutes}분`
  if (hours > 0) return `${hours}시간 ${minutes}분`
  return `${minutes}분`
}

// 퍼센트 포맷팅
export const formatPercent = (value: number): string => {
  return `${value.toFixed(1)}%`
}

// 색상 유틸리티
export const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'running':
      return 'green'
    case 'stopped':
      return 'gray'
    case 'error':
      return 'red'
    case 'warning':
      return 'yellow'
    case 'starting':
      return 'blue'
    case 'stopping':
      return 'orange'
    default:
      return 'gray'
  }
}

// 로그 레벨 색상
export const getLogLevelColor = (level: string): string => {
  switch (level.toUpperCase()) {
    case 'ERROR':
      return 'red'
    case 'WARN':
      return 'yellow'
    case 'INFO':
      return 'blue'
    case 'DEBUG':
      return 'gray'
    default:
      return 'gray'
  }
}

// 디바운스 함수
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout

  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

// 스로틀 함수
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// 로컬 스토리지 유틸리티
export const storage = {
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue || null
    } catch {
      return defaultValue || null
    }
  },

  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('로컬 스토리지 저장 실패:', error)
    }
  },

  remove: (key: string): void => {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error('로컬 스토리지 삭제 실패:', error)
    }
  },
}

// URL 검증
export const isValidUrl = (string: string): boolean => {
  try {
    new URL(string)
    return true
  } catch {
    return false
  }
}

// 깊은 복사
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj))
}

// 객체 비교
export const isEqual = (a: any, b: any): boolean => {
  return JSON.stringify(a) === JSON.stringify(b)
}
