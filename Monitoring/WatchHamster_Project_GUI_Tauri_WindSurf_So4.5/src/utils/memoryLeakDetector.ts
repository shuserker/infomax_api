/**
 * 메모리 누수 감지 및 방지 유틸리티
 */

interface LeakDetectionConfig {
  checkInterval: number // 검사 간격 (밀리초)
  memoryThreshold: number // 메모리 임계값 (바이트)
  maxGrowthRate: number // 최대 증가율 (%)
  alertCallback?: (info: MemoryLeakInfo) => void
}

interface MemoryLeakInfo {
  type: 'threshold_exceeded' | 'rapid_growth' | 'potential_leak'
  currentUsage: number
  previousUsage: number
  growthRate: number
  timestamp: number
  details: string
}

interface ComponentMemoryTracker {
  componentName: string
  mountTime: number
  initialMemory: number
  currentMemory: number
  renderCount: number
  lastRenderTime: number
}

export class MemoryLeakDetector {
  private config: LeakDetectionConfig
  private memoryHistory: Array<{ timestamp: number; usage: number }> = []
  private componentTrackers = new Map<string, ComponentMemoryTracker>()
  private eventListeners = new Set<() => void>()
  private timers = new Set<NodeJS.Timeout>()
  private intervals = new Set<NodeJS.Timeout>()
  private observers = new Set<IntersectionObserver | MutationObserver | ResizeObserver>()
  private monitoringInterval?: NodeJS.Timeout
  private isMonitoring = false

  constructor(config: Partial<LeakDetectionConfig> = {}) {
    this.config = {
      checkInterval: 10000, // 10초
      memoryThreshold: 100 * 1024 * 1024, // 100MB
      maxGrowthRate: 50, // 50%
      ...config
    }
  }

  /**
   * 메모리 누수 모니터링 시작
   */
  startMonitoring(): void {
    if (this.isMonitoring) {
      return
    }

    this.isMonitoring = true
    this.monitoringInterval = setInterval(() => {
      this.checkMemoryUsage()
    }, this.config.checkInterval)

    // 초기 메모리 사용량 기록
    this.recordMemoryUsage()

    if (process.env.NODE_ENV === 'development') {
      console.log('메모리 누수 모니터링 시작됨')
    }
  }

  /**
   * 메모리 누수 모니터링 중지
   */
  stopMonitoring(): void {
    if (!this.isMonitoring) {
      return
    }

    this.isMonitoring = false
    
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = undefined
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('메모리 누수 모니터링 중지됨')
    }
  }

  /**
   * 컴포넌트 메모리 추적 시작
   */
  trackComponent(componentName: string): () => void {
    const initialMemory = this.getCurrentMemoryUsage()
    
    const tracker: ComponentMemoryTracker = {
      componentName,
      mountTime: Date.now(),
      initialMemory,
      currentMemory: initialMemory,
      renderCount: 0,
      lastRenderTime: Date.now()
    }

    this.componentTrackers.set(componentName, tracker)

    // 정리 함수 반환
    return () => {
      this.componentTrackers.delete(componentName)
    }
  }

  /**
   * 컴포넌트 렌더링 기록
   */
  recordComponentRender(componentName: string): void {
    const tracker = this.componentTrackers.get(componentName)
    if (tracker) {
      tracker.renderCount++
      tracker.lastRenderTime = Date.now()
      tracker.currentMemory = this.getCurrentMemoryUsage()
    }
  }

  /**
   * 이벤트 리스너 추적
   */
  trackEventListener(cleanup: () => void): void {
    this.eventListeners.add(cleanup)
  }

  /**
   * 타이머 추적
   */
  trackTimer(timer: NodeJS.Timeout): void {
    this.timers.add(timer)
  }

  /**
   * 인터벌 추적
   */
  trackInterval(interval: NodeJS.Timeout): void {
    this.intervals.add(interval)
  }

  /**
   * 옵저버 추적
   */
  trackObserver(observer: IntersectionObserver | MutationObserver | ResizeObserver): void {
    this.observers.add(observer)
  }

  /**
   * 메모리 사용량 검사
   */
  private checkMemoryUsage(): void {
    const currentUsage = this.getCurrentMemoryUsage()
    this.recordMemoryUsage()

    // 임계값 검사
    if (currentUsage > this.config.memoryThreshold) {
      this.reportLeak({
        type: 'threshold_exceeded',
        currentUsage,
        previousUsage: 0,
        growthRate: 0,
        timestamp: Date.now(),
        details: `메모리 사용량이 임계값(${this.formatBytes(this.config.memoryThreshold)})을 초과했습니다.`
      })
    }

    // 증가율 검사
    if (this.memoryHistory.length >= 2) {
      const previous = this.memoryHistory[this.memoryHistory.length - 2]
      const growthRate = ((currentUsage - previous.usage) / previous.usage) * 100

      if (growthRate > this.config.maxGrowthRate) {
        this.reportLeak({
          type: 'rapid_growth',
          currentUsage,
          previousUsage: previous.usage,
          growthRate,
          timestamp: Date.now(),
          details: `메모리 사용량이 급격히 증가했습니다 (${growthRate.toFixed(2)}%).`
        })
      }
    }

    // 컴포넌트별 메모리 누수 검사
    this.checkComponentLeaks()
  }

  /**
   * 컴포넌트별 메모리 누수 검사
   */
  private checkComponentLeaks(): void {
    for (const [componentName, tracker] of this.componentTrackers.entries()) {
      const memoryGrowth = tracker.currentMemory - tracker.initialMemory
      const timeAlive = Date.now() - tracker.mountTime

      // 컴포넌트가 오래 살아있으면서 메모리가 계속 증가하는 경우
      if (timeAlive > 60000 && memoryGrowth > 10 * 1024 * 1024) { // 1분 이상, 10MB 이상 증가
        this.reportLeak({
          type: 'potential_leak',
          currentUsage: tracker.currentMemory,
          previousUsage: tracker.initialMemory,
          growthRate: (memoryGrowth / tracker.initialMemory) * 100,
          timestamp: Date.now(),
          details: `컴포넌트 ${componentName}에서 잠재적 메모리 누수가 감지되었습니다. 렌더링 횟수: ${tracker.renderCount}`
        })
      }
    }
  }

  /**
   * 현재 메모리 사용량 조회
   */
  private getCurrentMemoryUsage(): number {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize
    }
    return 0
  }

  /**
   * 메모리 사용량 기록
   */
  private recordMemoryUsage(): void {
    const usage = this.getCurrentMemoryUsage()
    this.memoryHistory.push({
      timestamp: Date.now(),
      usage
    })

    // 오래된 기록 제거 (최근 100개만 유지)
    if (this.memoryHistory.length > 100) {
      this.memoryHistory.shift()
    }
  }

  /**
   * 메모리 누수 보고
   */
  private reportLeak(info: MemoryLeakInfo): void {
    if (process.env.NODE_ENV === 'development') {
      console.warn('메모리 누수 감지:', info)
    }

    if (this.config.alertCallback) {
      this.config.alertCallback(info)
    }
  }

  /**
   * 바이트를 읽기 쉬운 형태로 포맷
   */
  private formatBytes(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 Bytes'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  /**
   * 메모리 통계 조회
   */
  getMemoryStats() {
    const currentUsage = this.getCurrentMemoryUsage()
    const componentStats = Array.from(this.componentTrackers.entries()).map(([name, tracker]) => ({
      name,
      memoryGrowth: tracker.currentMemory - tracker.initialMemory,
      renderCount: tracker.renderCount,
      timeAlive: Date.now() - tracker.mountTime
    }))

    return {
      currentUsage: this.formatBytes(currentUsage),
      trackedComponents: componentStats.length,
      trackedEventListeners: this.eventListeners.size,
      trackedTimers: this.timers.size,
      trackedIntervals: this.intervals.size,
      trackedObservers: this.observers.size,
      componentStats,
      memoryHistory: this.memoryHistory.slice(-10) // 최근 10개 기록
    }
  }

  /**
   * 강제 정리 실행
   */
  forceCleanup(): void {
    // 이벤트 리스너 정리
    this.eventListeners.forEach(cleanup => {
      try {
        cleanup()
      } catch (error) {
        console.error('이벤트 리스너 정리 중 오류:', error)
      }
    })
    this.eventListeners.clear()

    // 타이머 정리
    this.timers.forEach(timer => {
      clearTimeout(timer)
    })
    this.timers.clear()

    // 인터벌 정리
    this.intervals.forEach(interval => {
      clearInterval(interval)
    })
    this.intervals.clear()

    // 옵저버 정리
    this.observers.forEach(observer => {
      observer.disconnect()
    })
    this.observers.clear()

    // 가비지 컬렉션 제안 (브라우저가 지원하는 경우)
    if ('gc' in window && typeof (window as any).gc === 'function') {
      (window as any).gc()
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('강제 정리 완료')
    }
  }

  /**
   * 정리
   */
  destroy(): void {
    this.stopMonitoring()
    this.forceCleanup()
    this.componentTrackers.clear()
    this.memoryHistory = []
  }
}

// 전역 메모리 누수 감지기
export const globalMemoryLeakDetector = new MemoryLeakDetector({
  checkInterval: 15000, // 15초
  memoryThreshold: 150 * 1024 * 1024, // 150MB
  maxGrowthRate: 30, // 30%
  alertCallback: (info) => {
    if (process.env.NODE_ENV === 'development') {
      console.group('🚨 메모리 누수 경고')
      console.log('타입:', info.type)
      console.log('현재 사용량:', (info.currentUsage / 1024 / 1024).toFixed(2) + 'MB')
      console.log('이전 사용량:', (info.previousUsage / 1024 / 1024).toFixed(2) + 'MB')
      console.log('증가율:', info.growthRate.toFixed(2) + '%')
      console.log('세부사항:', info.details)
      console.groupEnd()
    }
  }
})

import React from 'react'

// React 컴포넌트용 메모리 추적 훅
export const useMemoryTracking = (componentName: string) => {
  const [memoryInfo, setMemoryInfo] = React.useState<{
    initialMemory: number
    currentMemory: number
    renderCount: number
  } | null>(null)

  React.useEffect(() => {
    const cleanup = globalMemoryLeakDetector.trackComponent(componentName)
    
    // 초기 메모리 정보 설정
    const initialMemory = globalMemoryLeakDetector['getCurrentMemoryUsage']()
    setMemoryInfo({
      initialMemory,
      currentMemory: initialMemory,
      renderCount: 0
    })

    return cleanup
  }, [componentName])

  React.useEffect(() => {
    globalMemoryLeakDetector.recordComponentRender(componentName)
    
    if (memoryInfo) {
      const currentMemory = globalMemoryLeakDetector['getCurrentMemoryUsage']()
      setMemoryInfo(prev => prev ? {
        ...prev,
        currentMemory,
        renderCount: prev.renderCount + 1
      } : null)
    }
  })

  return memoryInfo
}

// 안전한 이벤트 리스너 추가 함수
export const addSafeEventListener = <K extends keyof WindowEventMap>(
  target: EventTarget,
  type: K,
  listener: (this: Window, ev: WindowEventMap[K]) => any,
  options?: boolean | AddEventListenerOptions
): (() => void) => {
  target.addEventListener(type, listener, options)
  
  const cleanup = () => {
    target.removeEventListener(type, listener, options)
  }
  
  globalMemoryLeakDetector.trackEventListener(cleanup)
  
  return cleanup
}

// 안전한 타이머 함수
export const setSafeTimeout = (callback: () => void, delay: number): NodeJS.Timeout => {
  const timer = setTimeout(callback, delay)
  globalMemoryLeakDetector.trackTimer(timer)
  return timer
}

// 안전한 인터벌 함수
export const setSafeInterval = (callback: () => void, delay: number): NodeJS.Timeout => {
  const interval = setInterval(callback, delay)
  globalMemoryLeakDetector.trackInterval(interval)
  return interval
}

// 안전한 옵저버 생성 함수
export const createSafeIntersectionObserver = (
  callback: IntersectionObserverCallback,
  options?: IntersectionObserverInit
): IntersectionObserver => {
  const observer = new IntersectionObserver(callback, options)
  globalMemoryLeakDetector.trackObserver(observer)
  return observer
}

// 메모리 사용량 모니터링 컴포넌트 (별도 파일로 분리 권장)
export const createMemoryMonitorComponent = () => {
  return {
    getStats: () => globalMemoryLeakDetector.getMemoryStats(),
    formatForDisplay: (showDetails = false) => {
      const stats = globalMemoryLeakDetector.getMemoryStats()
      
      if (!showDetails) {
        return `메모리: ${stats.currentUsage}`
      }
      
      return {
        currentUsage: stats.currentUsage,
        trackedComponents: stats.trackedComponents,
        trackedEventListeners: stats.trackedEventListeners,
        trackedTimers: stats.trackedTimers,
        trackedIntervals: stats.trackedIntervals,
        trackedObservers: stats.trackedObservers
      }
    }
  }
}