/**
 * 성능 최적화 훅
 * React 컴포넌트 메모이제이션 및 성능 최적화 유틸리티
 */

import { useCallback, useMemo, useRef, useEffect, useState } from 'react'

// 간단한 디바운스 구현
const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): T & { cancel: () => void } => {
  let timeout: NodeJS.Timeout | null = null

  const debounced = ((...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }) as T & { cancel: () => void }

  debounced.cancel = () => {
    if (timeout) {
      clearTimeout(timeout)
      timeout = null
    }
  }

  return debounced
}

// 간단한 스로틀 구현
const throttle = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): T & { cancel: () => void } => {
  let timeout: NodeJS.Timeout | null = null
  let previous = 0

  const throttled = ((...args: Parameters<T>) => {
    const now = Date.now()
    const remaining = wait - (now - previous)

    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout)
        timeout = null
      }
      previous = now
      func(...args)
    } else if (!timeout) {
      timeout = setTimeout(() => {
        previous = Date.now()
        timeout = null
        func(...args)
      }, remaining)
    }
  }) as T & { cancel: () => void }

  throttled.cancel = () => {
    if (timeout) {
      clearTimeout(timeout)
      timeout = null
    }
    previous = 0
  }

  return throttled
}

// 디바운스 훅
export const useDebounce = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T => {
  const debouncedCallback = useMemo(
    () => debounce(callback, delay),
    [callback, delay]
  )

  useEffect(() => {
    return () => {
      debouncedCallback.cancel()
    }
  }, [debouncedCallback])

  return debouncedCallback as T
}

// 스로틀 훅
export const useThrottle = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T => {
  const throttledCallback = useMemo(
    () => throttle(callback, delay),
    [callback, delay]
  )

  useEffect(() => {
    return () => {
      throttledCallback.cancel()
    }
  }, [throttledCallback])

  return throttledCallback as T
}

// 메모이제이션된 값 훅
export const useMemoizedValue = <T>(
  factory: () => T,
  deps: React.DependencyList
): T => {
  return useMemo(factory, deps)
}

// 안정적인 콜백 훅
export const useStableCallback = <T extends (...args: any[]) => any>(
  callback: T
): T => {
  const callbackRef = useRef(callback)
  
  useEffect(() => {
    callbackRef.current = callback
  })

  return useCallback((...args: any[]) => {
    return callbackRef.current(...args)
  }, []) as T
}

// 이전 값 추적 훅
export const usePrevious = <T>(value: T): T | undefined => {
  const ref = useRef<T>()
  
  useEffect(() => {
    ref.current = value
  })
  
  return ref.current
}

// 변경 감지 훅
export const useDeepCompareEffect = (
  callback: React.EffectCallback,
  deps: React.DependencyList
) => {
  const ref = useRef<React.DependencyList>()
  
  if (!ref.current || !deepEqual(deps, ref.current)) {
    ref.current = deps
  }
  
  useEffect(callback, ref.current)
}

// 깊은 비교 함수
const deepEqual = (a: any, b: any): boolean => {
  if (a === b) return true
  
  if (a == null || b == null) return false
  
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false
    for (let i = 0; i < a.length; i++) {
      if (!deepEqual(a[i], b[i])) return false
    }
    return true
  }
  
  if (typeof a === 'object' && typeof b === 'object') {
    const keysA = Object.keys(a)
    const keysB = Object.keys(b)
    
    if (keysA.length !== keysB.length) return false
    
    for (const key of keysA) {
      if (!keysB.includes(key)) return false
      if (!deepEqual(a[key], b[key])) return false
    }
    return true
  }
  
  return false
}

// 렌더링 최적화 훅
export const useRenderOptimization = () => {
  const renderCount = useRef(0)
  const lastRenderTime = useRef(Date.now())
  
  useEffect(() => {
    renderCount.current += 1
    const now = Date.now()
    const timeSinceLastRender = now - lastRenderTime.current
    lastRenderTime.current = now
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`렌더링 #${renderCount.current}, 간격: ${timeSinceLastRender}ms`)
    }
  })
  
  return {
    renderCount: renderCount.current,
    resetRenderCount: () => {
      renderCount.current = 0
    }
  }
}

// 메모리 사용량 모니터링 훅
export const useMemoryMonitoring = () => {
  const [memoryInfo, setMemoryInfo] = useState<{
    usedJSHeapSize?: number
    totalJSHeapSize?: number
    jsHeapSizeLimit?: number
  }>({})
  
  useEffect(() => {
    const updateMemoryInfo = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory
        setMemoryInfo({
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit
        })
      }
    }
    
    updateMemoryInfo()
    const interval = setInterval(updateMemoryInfo, 5000) // 5초마다 업데이트
    
    return () => clearInterval(interval)
  }, [])
  
  return memoryInfo
}

// 가상화 최적화 훅
export const useVirtualization = <T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) => {
  const [scrollTop, setScrollTop] = useState(0)
  
  const visibleRange = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight)
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    )
    
    return { startIndex, endIndex }
  }, [scrollTop, itemHeight, containerHeight, items.length])
  
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex)
  }, [items, visibleRange])
  
  const totalHeight = items.length * itemHeight
  const offsetY = visibleRange.startIndex * itemHeight
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    setScrollTop,
    visibleRange
  }
}

// 이미지 지연 로딩 훅
export const useLazyLoading = (threshold = 0.1) => {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<HTMLElement>(null)
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold }
    )
    
    if (ref.current) {
      observer.observe(ref.current)
    }
    
    return () => observer.disconnect()
  }, [threshold])
  
  return { ref, isVisible }
}

// 배치 업데이트 훅
export const useBatchUpdates = <T>(initialValue: T) => {
  const [value, setValue] = useState(initialValue)
  const batchedUpdates = useRef<T[]>([])
  const timeoutRef = useRef<NodeJS.Timeout>()
  
  const batchUpdate = useCallback((newValue: T) => {
    batchedUpdates.current.push(newValue)
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    
    timeoutRef.current = setTimeout(() => {
      const latestValue = batchedUpdates.current[batchedUpdates.current.length - 1]
      setValue(latestValue)
      batchedUpdates.current = []
    }, 16) // 다음 프레임에서 업데이트
  }, [])
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])
  
  return [value, batchUpdate] as const
}

// 컴포넌트 성능 측정 훅
export const usePerformanceMeasure = (componentName: string) => {
  const startTimeRef = useRef<number>()
  
  useEffect(() => {
    startTimeRef.current = performance.now()
    
    return () => {
      if (startTimeRef.current) {
        const duration = performance.now() - startTimeRef.current
        if (process.env.NODE_ENV === 'development') {
          console.log(`${componentName} 렌더링 시간: ${duration.toFixed(2)}ms`)
        }
      }
    }
  })
  
  const measureFunction = useCallback(<T extends (...args: any[]) => any>(
    fn: T,
    functionName: string
  ): T => {
    return ((...args: any[]) => {
      const start = performance.now()
      const result = fn(...args)
      const end = performance.now()
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`${componentName}.${functionName} 실행 시간: ${(end - start).toFixed(2)}ms`)
      }
      
      return result
    }) as T
  }, [componentName])
  
  return { measureFunction }
}

// 리소스 정리 훅
export const useCleanup = (cleanup: () => void) => {
  useEffect(() => {
    return cleanup
  }, [cleanup])
}

// 메모리 누수 방지 훅
export const useMemoryLeakPrevention = () => {
  const subscriptions = useRef<(() => void)[]>([])
  const timeouts = useRef<NodeJS.Timeout[]>([])
  const intervals = useRef<NodeJS.Timeout[]>([])
  
  const addSubscription = useCallback((unsubscribe: () => void) => {
    subscriptions.current.push(unsubscribe)
  }, [])
  
  const addTimeout = useCallback((timeout: NodeJS.Timeout) => {
    timeouts.current.push(timeout)
  }, [])
  
  const addInterval = useCallback((interval: NodeJS.Timeout) => {
    intervals.current.push(interval)
  }, [])
  
  useEffect(() => {
    return () => {
      // 모든 구독 해제
      subscriptions.current.forEach(unsubscribe => unsubscribe())
      
      // 모든 타임아웃 정리
      timeouts.current.forEach(timeout => clearTimeout(timeout))
      
      // 모든 인터벌 정리
      intervals.current.forEach(interval => clearInterval(interval))
    }
  }, [])
  
  return {
    addSubscription,
    addTimeout,
    addInterval
  }
}