/**
 * 캐시 관리자
 * API 호출 캐싱 및 디바운싱 관리
 */

interface CacheEntry<T> {
  data: T
  timestamp: number
  ttl: number
}

interface CacheConfig {
  defaultTTL: number // 기본 TTL (밀리초)
  maxSize: number    // 최대 캐시 크기
  cleanupInterval: number // 정리 간격 (밀리초)
}

export class CacheManager {
  private cache = new Map<string, CacheEntry<any>>()
  private config: CacheConfig
  private cleanupTimer?: NodeJS.Timeout
  private accessTimes = new Map<string, number>()

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      defaultTTL: 5 * 60 * 1000, // 5분
      maxSize: 100,
      cleanupInterval: 60 * 1000, // 1분
      ...config
    }

    this.startCleanupTimer()
  }

  /**
   * 캐시에서 데이터 조회
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    
    if (!entry) {
      return null
    }

    // TTL 확인
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key)
      this.accessTimes.delete(key)
      return null
    }

    // 접근 시간 업데이트 (LRU를 위해)
    this.accessTimes.set(key, Date.now())
    
    return entry.data
  }

  /**
   * 캐시에 데이터 저장
   */
  set<T>(key: string, data: T, ttl?: number): void {
    // 캐시 크기 제한 확인
    if (this.cache.size >= this.config.maxSize && !this.cache.has(key)) {
      this.evictLRU()
    }

    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.config.defaultTTL
    }

    this.cache.set(key, entry)
    this.accessTimes.set(key, Date.now())
  }

  /**
   * 캐시에서 데이터 삭제
   */
  delete(key: string): boolean {
    this.accessTimes.delete(key)
    return this.cache.delete(key)
  }

  /**
   * 캐시 전체 삭제
   */
  clear(): void {
    this.cache.clear()
    this.accessTimes.clear()
  }

  /**
   * 캐시 키 존재 여부 확인
   */
  has(key: string): boolean {
    const entry = this.cache.get(key)
    
    if (!entry) {
      return false
    }

    // TTL 확인
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key)
      this.accessTimes.delete(key)
      return false
    }

    return true
  }

  /**
   * 캐시 통계 조회
   */
  getStats() {
    const now = Date.now()
    let expiredCount = 0
    
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        expiredCount++
      }
    }

    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      expiredCount,
      hitRate: this.calculateHitRate()
    }
  }

  /**
   * 패턴으로 캐시 삭제
   */
  deleteByPattern(pattern: string | RegExp): number {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern
    let deletedCount = 0

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.delete(key)
        deletedCount++
      }
    }

    return deletedCount
  }

  /**
   * 만료된 캐시 정리
   */
  private cleanup(): void {
    const now = Date.now()
    const keysToDelete: string[] = []

    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        keysToDelete.push(key)
      }
    }

    keysToDelete.forEach(key => {
      this.cache.delete(key)
      this.accessTimes.delete(key)
    })

    if (process.env.NODE_ENV === 'development') {
      console.log(`캐시 정리 완료: ${keysToDelete.length}개 항목 삭제`)
    }
  }

  /**
   * LRU 방식으로 캐시 항목 제거
   */
  private evictLRU(): void {
    let oldestKey: string | null = null
    let oldestTime = Date.now()

    for (const [key, time] of this.accessTimes.entries()) {
      if (time < oldestTime) {
        oldestTime = time
        oldestKey = key
      }
    }

    if (oldestKey) {
      this.delete(oldestKey)
    }
  }

  /**
   * 히트율 계산
   */
  private calculateHitRate(): number {
    // 실제 구현에서는 히트/미스 카운터를 추가로 관리해야 함
    return 0
  }

  /**
   * 정리 타이머 시작
   */
  private startCleanupTimer(): void {
    this.cleanupTimer = setInterval(() => {
      this.cleanup()
    }, this.config.cleanupInterval)
  }

  /**
   * 정리 타이머 중지
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer)
    }
    this.clear()
  }
}

// 전역 캐시 인스턴스
export const globalCache = new CacheManager({
  defaultTTL: 5 * 60 * 1000, // 5분
  maxSize: 200,
  cleanupInterval: 2 * 60 * 1000 // 2분
})

// API 캐시 데코레이터
export function cached<T extends (...args: any[]) => Promise<any>>(
  ttl?: number,
  keyGenerator?: (...args: Parameters<T>) => string
) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value

    descriptor.value = async function (...args: Parameters<T>) {
      const cacheKey = keyGenerator 
        ? keyGenerator(...args)
        : `${propertyName}_${JSON.stringify(args)}`

      // 캐시에서 조회
      const cachedResult = globalCache.get(cacheKey)
      if (cachedResult !== null) {
        return cachedResult
      }

      // 캐시 미스 - 실제 메서드 호출
      const result = await method.apply(this, args)
      
      // 결과를 캐시에 저장
      globalCache.set(cacheKey, result, ttl)
      
      return result
    }

    return descriptor
  }
}

// 디바운스 관리자
export class DebounceManager {
  private timers = new Map<string, NodeJS.Timeout>()

  /**
   * 디바운스된 함수 실행
   */
  debounce<T extends (...args: any[]) => any>(
    key: string,
    fn: T,
    delay: number,
    ...args: Parameters<T>
  ): void {
    // 기존 타이머 취소
    const existingTimer = this.timers.get(key)
    if (existingTimer) {
      clearTimeout(existingTimer)
    }

    // 새 타이머 설정
    const timer = setTimeout(() => {
      fn(...args)
      this.timers.delete(key)
    }, delay)

    this.timers.set(key, timer)
  }

  /**
   * 특정 키의 디바운스 취소
   */
  cancel(key: string): void {
    const timer = this.timers.get(key)
    if (timer) {
      clearTimeout(timer)
      this.timers.delete(key)
    }
  }

  /**
   * 모든 디바운스 취소
   */
  cancelAll(): void {
    for (const timer of this.timers.values()) {
      clearTimeout(timer)
    }
    this.timers.clear()
  }

  /**
   * 정리
   */
  destroy(): void {
    this.cancelAll()
  }
}

// 전역 디바운스 관리자
export const globalDebounce = new DebounceManager()

// 스로틀 관리자
export class ThrottleManager {
  private lastExecution = new Map<string, number>()

  /**
   * 스로틀된 함수 실행
   */
  throttle<T extends (...args: any[]) => any>(
    key: string,
    fn: T,
    delay: number,
    ...args: Parameters<T>
  ): boolean {
    const now = Date.now()
    const lastTime = this.lastExecution.get(key) || 0

    if (now - lastTime >= delay) {
      fn(...args)
      this.lastExecution.set(key, now)
      return true
    }

    return false
  }

  /**
   * 특정 키의 스로틀 리셋
   */
  reset(key: string): void {
    this.lastExecution.delete(key)
  }

  /**
   * 모든 스로틀 리셋
   */
  resetAll(): void {
    this.lastExecution.clear()
  }
}

// 전역 스로틀 관리자
export const globalThrottle = new ThrottleManager()

// 요청 중복 제거 관리자
export class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>()

  /**
   * 중복 요청 제거
   */
  async deduplicate<T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    // 이미 진행 중인 요청이 있는지 확인
    const existingRequest = this.pendingRequests.get(key)
    if (existingRequest) {
      return existingRequest
    }

    // 새 요청 시작
    const request = requestFn()
    this.pendingRequests.set(key, request)

    try {
      const result = await request
      return result
    } finally {
      // 요청 완료 후 정리
      this.pendingRequests.delete(key)
    }
  }

  /**
   * 특정 키의 요청 취소
   */
  cancel(key: string): void {
    this.pendingRequests.delete(key)
  }

  /**
   * 모든 요청 취소
   */
  cancelAll(): void {
    this.pendingRequests.clear()
  }

  /**
   * 진행 중인 요청 수 조회
   */
  getPendingCount(): number {
    return this.pendingRequests.size
  }
}

// 전역 요청 중복 제거 관리자
export const globalDeduplicator = new RequestDeduplicator()

// 메모리 사용량 모니터링
export class MemoryMonitor {
  private measurements: Array<{
    timestamp: number
    usedJSHeapSize: number
    totalJSHeapSize: number
  }> = []

  private maxMeasurements = 100

  /**
   * 메모리 사용량 측정
   */
  measure(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      
      this.measurements.push({
        timestamp: Date.now(),
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize
      })

      // 오래된 측정값 제거
      if (this.measurements.length > this.maxMeasurements) {
        this.measurements.shift()
      }
    }
  }

  /**
   * 메모리 사용량 통계 조회
   */
  getStats() {
    if (this.measurements.length === 0) {
      return null
    }

    const latest = this.measurements[this.measurements.length - 1]
    const oldest = this.measurements[0]

    const usedSizes = this.measurements.map(m => m.usedJSHeapSize)
    const avgUsed = usedSizes.reduce((a, b) => a + b, 0) / usedSizes.length
    const maxUsed = Math.max(...usedSizes)
    const minUsed = Math.min(...usedSizes)

    return {
      current: {
        usedJSHeapSize: latest.usedJSHeapSize,
        totalJSHeapSize: latest.totalJSHeapSize,
        usagePercent: (latest.usedJSHeapSize / latest.totalJSHeapSize) * 100
      },
      trend: {
        change: latest.usedJSHeapSize - oldest.usedJSHeapSize,
        changePercent: ((latest.usedJSHeapSize - oldest.usedJSHeapSize) / oldest.usedJSHeapSize) * 100
      },
      statistics: {
        average: avgUsed,
        maximum: maxUsed,
        minimum: minUsed
      }
    }
  }

  /**
   * 자동 모니터링 시작
   */
  startMonitoring(interval = 5000): NodeJS.Timeout {
    return setInterval(() => {
      this.measure()
    }, interval)
  }
}

// 전역 메모리 모니터
export const globalMemoryMonitor = new MemoryMonitor()