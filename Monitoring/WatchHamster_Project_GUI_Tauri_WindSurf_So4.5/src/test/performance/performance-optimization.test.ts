/**
 * 성능 최적화 테스트
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { 
  useDebounce, 
  useThrottle, 
  useMemoizedValue, 
  useStableCallback,
  usePrevious,
  useVirtualization,
  usePerformanceMeasure
} from '@/hooks/usePerformanceOptimization'
import { 
  CacheManager, 
  DebounceManager, 
  ThrottleManager, 
  RequestDeduplicator,
  MemoryMonitor 
} from '@/services/cacheManager'
import { 
  MemoryLeakDetector,
  addSafeEventListener,
  setSafeTimeout,
  setSafeInterval
} from '@/utils/memoryLeakDetector'

describe('성능 최적화 훅 테스트', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('useDebounce', () => {
    it('디바운스 기능이 정상 작동해야 함', async () => {
      const mockCallback = vi.fn()
      const { result } = renderHook(() => useDebounce(mockCallback, 500))

      // 여러 번 호출
      act(() => {
        result.current('test1')
        result.current('test2')
        result.current('test3')
      })

      // 아직 호출되지 않아야 함
      expect(mockCallback).not.toHaveBeenCalled()

      // 시간 경과
      act(() => {
        vi.advanceTimersByTime(500)
      })

      // 마지막 호출만 실행되어야 함
      expect(mockCallback).toHaveBeenCalledTimes(1)
      expect(mockCallback).toHaveBeenCalledWith('test3')
    })

    it('디바운스 취소가 정상 작동해야 함', () => {
      const mockCallback = vi.fn()
      const { result, unmount } = renderHook(() => useDebounce(mockCallback, 500))

      act(() => {
        result.current('test')
      })

      // 컴포넌트 언마운트
      unmount()

      act(() => {
        vi.advanceTimersByTime(500)
      })

      // 호출되지 않아야 함
      expect(mockCallback).not.toHaveBeenCalled()
    })
  })

  describe('useThrottle', () => {
    it('스로틀 기능이 정상 작동해야 함', () => {
      const mockCallback = vi.fn()
      const { result } = renderHook(() => useThrottle(mockCallback, 500))

      // 첫 번째 호출
      act(() => {
        result.current('test1')
      })

      expect(mockCallback).toHaveBeenCalledTimes(1)
      expect(mockCallback).toHaveBeenCalledWith('test1')

      // 즉시 다시 호출 (무시되어야 함)
      act(() => {
        result.current('test2')
      })

      expect(mockCallback).toHaveBeenCalledTimes(1)

      // 시간 경과 후 호출
      act(() => {
        vi.advanceTimersByTime(500)
        result.current('test3')
      })

      expect(mockCallback).toHaveBeenCalledTimes(2)
      expect(mockCallback).toHaveBeenLastCalledWith('test3')
    })
  })

  describe('useMemoizedValue', () => {
    it('의존성이 변경되지 않으면 같은 값을 반환해야 함', () => {
      const expensiveCalculation = vi.fn(() => ({ result: 'calculated' }))
      let deps = [1, 2, 3]

      const { result, rerender } = renderHook(() => 
        useMemoizedValue(expensiveCalculation, deps)
      )

      const firstResult = result.current
      expect(expensiveCalculation).toHaveBeenCalledTimes(1)

      // 리렌더링 (의존성 동일)
      rerender()
      expect(result.current).toBe(firstResult)
      expect(expensiveCalculation).toHaveBeenCalledTimes(1)

      // 의존성 변경
      deps = [1, 2, 4]
      rerender()
      expect(result.current).not.toBe(firstResult)
      expect(expensiveCalculation).toHaveBeenCalledTimes(2)
    })
  })

  describe('useStableCallback', () => {
    it('콜백 참조가 안정적이어야 함', () => {
      let callback = vi.fn()
      const { result, rerender } = renderHook(() => useStableCallback(callback))

      const firstCallback = result.current

      // 콜백 함수 변경
      callback = vi.fn()
      rerender()

      // 참조는 동일해야 함
      expect(result.current).toBe(firstCallback)

      // 하지만 새로운 콜백이 호출되어야 함
      result.current('test')
      expect(callback).toHaveBeenCalledWith('test')
    })
  })

  describe('usePrevious', () => {
    it('이전 값을 올바르게 추적해야 함', () => {
      let value = 'initial'
      const { result, rerender } = renderHook(() => usePrevious(value))

      // 초기값은 undefined
      expect(result.current).toBeUndefined()

      // 값 변경
      value = 'updated'
      rerender()

      // 이전 값 반환
      expect(result.current).toBe('initial')

      // 다시 변경
      value = 'final'
      rerender()

      expect(result.current).toBe('updated')
    })
  })

  describe('useVirtualization', () => {
    it('가상화 계산이 올바르게 작동해야 함', () => {
      const items = Array.from({ length: 1000 }, (_, i) => `Item ${i}`)
      const itemHeight = 50
      const containerHeight = 400

      const { result } = renderHook(() => 
        useVirtualization(items, itemHeight, containerHeight)
      )

      // 초기 상태
      expect(result.current.visibleItems.length).toBeLessThan(items.length)
      expect(result.current.totalHeight).toBe(items.length * itemHeight)
      expect(result.current.offsetY).toBe(0)

      // 스크롤 시뮬레이션
      act(() => {
        result.current.setScrollTop(500)
      })

      expect(result.current.offsetY).toBeGreaterThan(0)
      expect(result.current.visibleRange.startIndex).toBeGreaterThan(0)
    })
  })

  describe('usePerformanceMeasure', () => {
    it('성능 측정이 정상 작동해야 함', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      
      const { result } = renderHook(() => usePerformanceMeasure('TestComponent'))

      const mockFunction = vi.fn(() => 'result')
      const measuredFunction = result.current.measureFunction(mockFunction, 'testMethod')

      const returnValue = measuredFunction('arg1', 'arg2')

      expect(mockFunction).toHaveBeenCalledWith('arg1', 'arg2')
      expect(returnValue).toBe('result')

      consoleSpy.mockRestore()
    })
  })
})

describe('캐시 관리자 테스트', () => {
  let cacheManager: CacheManager

  beforeEach(() => {
    cacheManager = new CacheManager({
      defaultTTL: 1000,
      maxSize: 3,
      cleanupInterval: 500
    })
  })

  afterEach(() => {
    cacheManager.destroy()
  })

  it('캐시 저장 및 조회가 정상 작동해야 함', () => {
    cacheManager.set('key1', 'value1')
    expect(cacheManager.get('key1')).toBe('value1')
    expect(cacheManager.has('key1')).toBe(true)
  })

  it('TTL이 만료되면 캐시가 삭제되어야 함', () => {
    vi.useFakeTimers()
    
    cacheManager.set('key1', 'value1', 500)
    expect(cacheManager.get('key1')).toBe('value1')

    vi.advanceTimersByTime(600)
    expect(cacheManager.get('key1')).toBeNull()
    expect(cacheManager.has('key1')).toBe(false)

    vi.useRealTimers()
  })

  it('최대 크기 제한이 작동해야 함', () => {
    cacheManager.set('key1', 'value1')
    cacheManager.set('key2', 'value2')
    cacheManager.set('key3', 'value3')
    cacheManager.set('key4', 'value4') // 최대 크기 초과

    // LRU에 의해 가장 오래된 항목이 제거되어야 함
    expect(cacheManager.has('key1')).toBe(false)
    expect(cacheManager.has('key4')).toBe(true)
  })

  it('패턴으로 캐시 삭제가 작동해야 함', () => {
    cacheManager.set('user:1', 'user1')
    cacheManager.set('user:2', 'user2')
    cacheManager.set('post:1', 'post1')

    const deletedCount = cacheManager.deleteByPattern(/^user:/)
    expect(deletedCount).toBe(2)
    expect(cacheManager.has('user:1')).toBe(false)
    expect(cacheManager.has('user:2')).toBe(false)
    expect(cacheManager.has('post:1')).toBe(true)
  })
})

describe('디바운스 관리자 테스트', () => {
  let debounceManager: DebounceManager

  beforeEach(() => {
    debounceManager = new DebounceManager()
    vi.useFakeTimers()
  })

  afterEach(() => {
    debounceManager.destroy()
    vi.useRealTimers()
  })

  it('디바운스가 정상 작동해야 함', () => {
    const mockFn = vi.fn()

    debounceManager.debounce('test', mockFn, 500, 'arg1')
    debounceManager.debounce('test', mockFn, 500, 'arg2')
    debounceManager.debounce('test', mockFn, 500, 'arg3')

    expect(mockFn).not.toHaveBeenCalled()

    vi.advanceTimersByTime(500)

    expect(mockFn).toHaveBeenCalledTimes(1)
    expect(mockFn).toHaveBeenCalledWith('arg3')
  })

  it('디바운스 취소가 작동해야 함', () => {
    const mockFn = vi.fn()

    debounceManager.debounce('test', mockFn, 500, 'arg1')
    debounceManager.cancel('test')

    vi.advanceTimersByTime(500)

    expect(mockFn).not.toHaveBeenCalled()
  })
})

describe('스로틀 관리자 테스트', () => {
  let throttleManager: ThrottleManager

  beforeEach(() => {
    throttleManager = new ThrottleManager()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('스로틀이 정상 작동해야 함', () => {
    const mockFn = vi.fn()

    // 첫 번째 호출은 즉시 실행
    const result1 = throttleManager.throttle('test', mockFn, 500, 'arg1')
    expect(result1).toBe(true)
    expect(mockFn).toHaveBeenCalledWith('arg1')

    // 두 번째 호출은 무시
    const result2 = throttleManager.throttle('test', mockFn, 500, 'arg2')
    expect(result2).toBe(false)
    expect(mockFn).toHaveBeenCalledTimes(1)

    // 시간 경과 후 호출
    vi.advanceTimersByTime(500)
    const result3 = throttleManager.throttle('test', mockFn, 500, 'arg3')
    expect(result3).toBe(true)
    expect(mockFn).toHaveBeenCalledWith('arg3')
  })
})

describe('요청 중복 제거 관리자 테스트', () => {
  let deduplicator: RequestDeduplicator

  beforeEach(() => {
    deduplicator = new RequestDeduplicator()
  })

  it('중복 요청이 제거되어야 함', async () => {
    const mockRequest = vi.fn().mockResolvedValue('result')

    // 동시에 같은 키로 요청
    const promise1 = deduplicator.deduplicate('test', mockRequest)
    const promise2 = deduplicator.deduplicate('test', mockRequest)
    const promise3 = deduplicator.deduplicate('test', mockRequest)

    const results = await Promise.all([promise1, promise2, promise3])

    // 요청 함수는 한 번만 호출되어야 함
    expect(mockRequest).toHaveBeenCalledTimes(1)
    
    // 모든 프로미스가 같은 결과를 반환해야 함
    expect(results).toEqual(['result', 'result', 'result'])
  })

  it('다른 키의 요청은 독립적으로 실행되어야 함', async () => {
    const mockRequest1 = vi.fn().mockResolvedValue('result1')
    const mockRequest2 = vi.fn().mockResolvedValue('result2')

    const promise1 = deduplicator.deduplicate('key1', mockRequest1)
    const promise2 = deduplicator.deduplicate('key2', mockRequest2)

    const results = await Promise.all([promise1, promise2])

    expect(mockRequest1).toHaveBeenCalledTimes(1)
    expect(mockRequest2).toHaveBeenCalledTimes(1)
    expect(results).toEqual(['result1', 'result2'])
  })
})

describe('메모리 모니터 테스트', () => {
  let memoryMonitor: MemoryMonitor

  beforeEach(() => {
    memoryMonitor = new MemoryMonitor()
    
    // performance.memory 모킹
    Object.defineProperty(performance, 'memory', {
      value: {
        usedJSHeapSize: 10000000,
        totalJSHeapSize: 20000000,
        jsHeapSizeLimit: 100000000
      },
      configurable: true
    })
  })

  it('메모리 측정이 정상 작동해야 함', () => {
    memoryMonitor.measure()
    const stats = memoryMonitor.getStats()

    expect(stats).not.toBeNull()
    expect(stats?.current.usedJSHeapSize).toBe(10000000)
    expect(stats?.current.totalJSHeapSize).toBe(20000000)
  })

  it('메모리 사용량 변화를 추적해야 함', () => {
    memoryMonitor.measure()

    // 메모리 사용량 변경 시뮬레이션
    Object.defineProperty(performance, 'memory', {
      value: {
        usedJSHeapSize: 15000000,
        totalJSHeapSize: 20000000,
        jsHeapSizeLimit: 100000000
      },
      configurable: true
    })

    memoryMonitor.measure()
    const stats = memoryMonitor.getStats()

    expect(stats?.trend.change).toBe(5000000)
    expect(stats?.trend.changePercent).toBe(50)
  })
})

describe('메모리 누수 감지기 테스트', () => {
  let detector: MemoryLeakDetector

  beforeEach(() => {
    detector = new MemoryLeakDetector({
      checkInterval: 1000,
      memoryThreshold: 50000000, // 50MB
      maxGrowthRate: 20
    })

    // performance.memory 모킹
    Object.defineProperty(performance, 'memory', {
      value: {
        usedJSHeapSize: 10000000,
        totalJSHeapSize: 20000000,
        jsHeapSizeLimit: 100000000
      },
      configurable: true
    })
  })

  afterEach(() => {
    detector.destroy()
  })

  it('컴포넌트 추적이 정상 작동해야 함', () => {
    const cleanup = detector.trackComponent('TestComponent')
    
    detector.recordComponentRender('TestComponent')
    detector.recordComponentRender('TestComponent')

    const stats = detector.getMemoryStats()
    expect(stats.trackedComponents).toBe(1)
    expect(stats.componentStats[0].renderCount).toBe(2)

    cleanup()
    
    const statsAfterCleanup = detector.getMemoryStats()
    expect(statsAfterCleanup.trackedComponents).toBe(0)
  })

  it('이벤트 리스너 추적이 정상 작동해야 함', () => {
    const mockElement = document.createElement('div')
    const mockListener = vi.fn()

    const cleanup = addSafeEventListener(mockElement, 'click', mockListener)
    
    const stats = detector.getMemoryStats()
    expect(stats.trackedEventListeners).toBe(1)

    cleanup()
    
    const statsAfterCleanup = detector.getMemoryStats()
    expect(statsAfterCleanup.trackedEventListeners).toBe(0)
  })

  it('타이머 추적이 정상 작동해야 함', () => {
    vi.useFakeTimers()

    const timer = setSafeTimeout(() => {}, 1000)
    
    const stats = detector.getMemoryStats()
    expect(stats.trackedTimers).toBe(1)

    clearTimeout(timer)
    detector.forceCleanup()
    
    const statsAfterCleanup = detector.getMemoryStats()
    expect(statsAfterCleanup.trackedTimers).toBe(0)

    vi.useRealTimers()
  })

  it('인터벌 추적이 정상 작동해야 함', () => {
    vi.useFakeTimers()

    const interval = setSafeInterval(() => {}, 1000)
    
    const stats = detector.getMemoryStats()
    expect(stats.trackedIntervals).toBe(1)

    clearInterval(interval)
    detector.forceCleanup()
    
    const statsAfterCleanup = detector.getMemoryStats()
    expect(statsAfterCleanup.trackedIntervals).toBe(0)

    vi.useRealTimers()
  })
})