/**
 * 반응형 디자인 최적화 훅
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
// import { useBreakpointValue, useMediaQuery } from '@chakra-ui/react'

// 브레이크포인트 정의
export const breakpoints = {
  xs: '320px',
  sm: '480px',
  md: '768px',
  lg: '992px',
  xl: '1200px',
  '2xl': '1536px'
} as const

export type Breakpoint = keyof typeof breakpoints

// 디바이스 타입
export type DeviceType = 'mobile' | 'tablet' | 'desktop'

// 화면 방향
export type Orientation = 'portrait' | 'landscape'

// 뷰포트 정보
export interface ViewportInfo {
  width: number
  height: number
  deviceType: DeviceType
  orientation: Orientation
  breakpoint: Breakpoint
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  isPortrait: boolean
  isLandscape: boolean
}

// 뷰포트 훅
export const useViewport = (): ViewportInfo => {
  const [viewport, setViewport] = useState<ViewportInfo>(() => {
    if (typeof window === 'undefined') {
      return {
        width: 1200,
        height: 800,
        deviceType: 'desktop',
        orientation: 'landscape',
        breakpoint: 'xl',
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        isPortrait: false,
        isLandscape: true
      }
    }

    const width = window.innerWidth
    const height = window.innerHeight
    const orientation: Orientation = width > height ? 'landscape' : 'portrait'
    
    let deviceType: DeviceType = 'desktop'
    let breakpoint: Breakpoint = 'xl'

    if (width < 768) {
      deviceType = 'mobile'
      breakpoint = width < 480 ? 'xs' : 'sm'
    } else if (width < 1200) {
      deviceType = 'tablet'
      breakpoint = width < 992 ? 'md' : 'lg'
    } else {
      breakpoint = width < 1536 ? 'xl' : '2xl'
    }

    return {
      width,
      height,
      deviceType,
      orientation,
      breakpoint,
      isMobile: deviceType === 'mobile',
      isTablet: deviceType === 'tablet',
      isDesktop: deviceType === 'desktop',
      isPortrait: orientation === 'portrait',
      isLandscape: orientation === 'landscape'
    }
  })

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth
      const height = window.innerHeight
      const orientation: Orientation = width > height ? 'landscape' : 'portrait'
      
      let deviceType: DeviceType = 'desktop'
      let breakpoint: Breakpoint = 'xl'

      if (width < 768) {
        deviceType = 'mobile'
        breakpoint = width < 480 ? 'xs' : 'sm'
      } else if (width < 1200) {
        deviceType = 'tablet'
        breakpoint = width < 992 ? 'md' : 'lg'
      } else {
        breakpoint = width < 1536 ? 'xl' : '2xl'
      }

      setViewport({
        width,
        height,
        deviceType,
        orientation,
        breakpoint,
        isMobile: deviceType === 'mobile',
        isTablet: deviceType === 'tablet',
        isDesktop: deviceType === 'desktop',
        isPortrait: orientation === 'portrait',
        isLandscape: orientation === 'landscape'
      })
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return viewport
}

// 반응형 값 훅
export const useResponsiveValue = <T>(values: Partial<Record<Breakpoint, T>>) => {
  const viewport = useViewport()
  
  return useMemo(() => {
    const breakpointOrder: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl']
    const currentIndex = breakpointOrder.indexOf(viewport.breakpoint)
    
    // 현재 브레이크포인트부터 역순으로 값 찾기
    for (let i = currentIndex; i >= 0; i--) {
      const bp = breakpointOrder[i]
      if (values[bp] !== undefined) {
        return values[bp]
      }
    }
    
    // 값이 없으면 가장 작은 브레이크포인트의 값 반환
    return values.xs
  }, [values, viewport.breakpoint])
}

// 그리드 컬럼 수 계산 훅
export const useResponsiveColumns = (
  minColumnWidth: number = 300,
  maxColumns: number = 4
) => {
  const viewport = useViewport()
  
  return useMemo(() => {
    const availableWidth = viewport.width - 32 // 패딩 고려
    const calculatedColumns = Math.floor(availableWidth / minColumnWidth)
    return Math.min(Math.max(calculatedColumns, 1), maxColumns)
  }, [viewport.width, minColumnWidth, maxColumns])
}

// 컨테이너 쿼리 훅
export const useContainerQuery = (containerRef: React.RefObject<HTMLElement>) => {
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 })

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect
        setContainerSize({ width, height })
      }
    })

    resizeObserver.observe(container)
    return () => resizeObserver.disconnect()
  }, [containerRef])

  const getContainerBreakpoint = useCallback((width: number): Breakpoint => {
    if (width < 480) return 'xs'
    if (width < 768) return 'sm'
    if (width < 992) return 'md'
    if (width < 1200) return 'lg'
    if (width < 1536) return 'xl'
    return '2xl'
  }, [])

  return {
    ...containerSize,
    breakpoint: getContainerBreakpoint(containerSize.width)
  }
}

// 터치 디바이스 감지 훅
export const useTouchDevice = () => {
  const [isTouchDevice, setIsTouchDevice] = useState(false)

  useEffect(() => {
    const checkTouchDevice = () => {
      setIsTouchDevice(
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        // @ts-ignore
        navigator.msMaxTouchPoints > 0
      )
    }

    checkTouchDevice()
    window.addEventListener('touchstart', checkTouchDevice, { once: true })
    
    return () => {
      window.removeEventListener('touchstart', checkTouchDevice)
    }
  }, [])

  return isTouchDevice
}

// 디바이스 픽셀 비율 훅
export const useDevicePixelRatio = () => {
  const [pixelRatio, setPixelRatio] = useState(
    typeof window !== 'undefined' ? window.devicePixelRatio : 1
  )

  useEffect(() => {
    const handleChange = () => {
      setPixelRatio(window.devicePixelRatio)
    }

    const mediaQuery = window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`)
    mediaQuery.addEventListener('change', handleChange)

    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return pixelRatio
}

// 네트워크 상태 훅
export const useNetworkStatus = () => {
  const [networkStatus, setNetworkStatus] = useState({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    effectiveType: '4g' as '2g' | '3g' | '4g' | 'slow-2g',
    downlink: 10,
    rtt: 50
  })

  useEffect(() => {
    const updateOnlineStatus = () => {
      setNetworkStatus(prev => ({ ...prev, isOnline: navigator.onLine }))
    }

    const updateNetworkInfo = () => {
      // @ts-ignore
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
      if (connection) {
        setNetworkStatus(prev => ({
          ...prev,
          effectiveType: connection.effectiveType || '4g',
          downlink: connection.downlink || 10,
          rtt: connection.rtt || 50
        }))
      }
    }

    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
    
    // @ts-ignore
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
    if (connection) {
      connection.addEventListener('change', updateNetworkInfo)
    }

    updateNetworkInfo()

    return () => {
      window.removeEventListener('online', updateOnlineStatus)
      window.removeEventListener('offline', updateOnlineStatus)
      if (connection) {
        connection.removeEventListener('change', updateNetworkInfo)
      }
    }
  }, [])

  return networkStatus
}

// 반응형 이미지 훅
export const useResponsiveImage = (
  baseSrc: string,
  sizes: Partial<Record<Breakpoint, string>> = {}
) => {
  const viewport = useViewport()
  const pixelRatio = useDevicePixelRatio()

  return useMemo(() => {
    const currentSize = sizes[viewport.breakpoint] || baseSrc
    const suffix = pixelRatio > 1 ? '@2x' : ''
    
    // 파일 확장자 앞에 suffix 추가
    const lastDotIndex = currentSize.lastIndexOf('.')
    if (lastDotIndex !== -1 && suffix) {
      return currentSize.slice(0, lastDotIndex) + suffix + currentSize.slice(lastDotIndex)
    }
    
    return currentSize
  }, [baseSrc, sizes, viewport.breakpoint, pixelRatio])
}

// 반응형 폰트 크기 훅
export const useResponsiveFontSize = (
  baseFontSize: number = 16
) => {
  const viewport = useViewport()

  return useMemo(() => {
    const scaleMap: Record<Breakpoint, number> = {
      xs: 0.8,
      sm: 0.9,
      md: 1,
      lg: 1.1,
      xl: 1.2,
      '2xl': 1.3
    }

    return baseFontSize * scaleMap[viewport.breakpoint]
  }, [baseFontSize, viewport.breakpoint])
}

// 반응형 간격 훅
export const useResponsiveSpacing = () => {
  const viewport = useViewport()

  return useMemo(() => {
    const spacingMap: Record<Breakpoint, { xs: number; sm: number; md: number; lg: number; xl: number }> = {
      xs: { xs: 2, sm: 4, md: 6, lg: 8, xl: 10 },
      sm: { xs: 4, sm: 6, md: 8, lg: 12, xl: 16 },
      md: { xs: 6, sm: 8, md: 12, lg: 16, xl: 20 },
      lg: { xs: 8, sm: 12, md: 16, lg: 20, xl: 24 },
      xl: { xs: 10, sm: 16, md: 20, lg: 24, xl: 32 },
      '2xl': { xs: 12, sm: 20, md: 24, lg: 32, xl: 40 }
    }

    return spacingMap[viewport.breakpoint]
  }, [viewport.breakpoint])
}

// 반응형 레이아웃 훅
export const useResponsiveLayout = () => {
  const viewport = useViewport()
  const isTouchDevice = useTouchDevice()

  return useMemo(() => {
    return {
      // 사이드바 표시 여부
      showSidebar: viewport.isDesktop,
      
      // 사이드바 위치
      sidebarPosition: viewport.isMobile ? 'overlay' : 'static' as 'overlay' | 'static',
      
      // 헤더 높이
      headerHeight: viewport.isMobile ? '56px' : '64px',
      
      // 컨테이너 패딩
      containerPadding: viewport.isMobile ? '16px' : '24px',
      
      // 그리드 간격
      gridGap: viewport.isMobile ? '12px' : '16px',
      
      // 버튼 크기
      buttonSize: isTouchDevice ? 'lg' : 'md',
      
      // 입력 필드 크기
      inputSize: isTouchDevice ? 'lg' : 'md',
      
      // 모달 크기
      modalSize: viewport.isMobile ? 'full' : 'md',
      
      // 테이블 표시 방식
      tableDisplay: viewport.isMobile ? 'cards' : 'table' as 'cards' | 'table'
    }
  }, [viewport, isTouchDevice])
}

// 반응형 성능 최적화 훅
export const useResponsivePerformance = () => {
  const viewport = useViewport()
  const networkStatus = useNetworkStatus()

  return useMemo(() => {
    const isLowEndDevice = viewport.isMobile
    const isSlowNetwork = ['2g', 'slow-2g'].includes(networkStatus.effectiveType)

    return {
      // 이미지 지연 로딩 활성화
      enableLazyLoading: isLowEndDevice || isSlowNetwork,
      
      // 애니메이션 감소
      reduceAnimations: isLowEndDevice,
      
      // 이미지 품질 조정
      imageQuality: isSlowNetwork ? 'low' : 'high' as 'low' | 'medium' | 'high',
      
      // 페이지네이션 크기
      pageSize: isLowEndDevice ? 10 : 20,
      
      // 프리로딩 비활성화
      disablePreloading: isSlowNetwork,
      
      // 캐시 전략
      cacheStrategy: isSlowNetwork ? 'aggressive' : 'normal' as 'aggressive' | 'normal'
    }
  }, [viewport.isMobile, networkStatus.effectiveType])
}

// 반응형 테이블 훅
export const useResponsiveTable = <T>(
  data: T[],
  columns: Array<{
    key: keyof T
    label: string
    priority: 'high' | 'medium' | 'low'
    minWidth?: number
  }>
) => {
  const viewport = useViewport()

  const visibleColumns = useMemo(() => {
    if (viewport.isDesktop) {
      return columns
    }

    if (viewport.isTablet) {
      return columns.filter(col => col.priority !== 'low')
    }

    // 모바일에서는 high priority만 표시
    return columns.filter(col => col.priority === 'high')
  }, [columns, viewport])

  const shouldUseCardLayout = viewport.isMobile

  return {
    visibleColumns,
    shouldUseCardLayout,
    data
  }
}

// CSS-in-JS 반응형 스타일 생성 훅
export const useResponsiveStyles = () => {
  const viewport = useViewport()

  const createResponsiveStyle = useCallback((
    styles: Partial<Record<Breakpoint, React.CSSProperties>>
  ): React.CSSProperties => {
    const breakpointOrder: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl']
    const currentIndex = breakpointOrder.indexOf(viewport.breakpoint)
    
    let mergedStyles: React.CSSProperties = {}
    
    // 현재 브레이크포인트까지의 스타일을 순서대로 병합
    for (let i = 0; i <= currentIndex; i++) {
      const bp = breakpointOrder[i]
      if (styles[bp]) {
        mergedStyles = { ...mergedStyles, ...styles[bp] }
      }
    }
    
    return mergedStyles
  }, [viewport.breakpoint])

  return { createResponsiveStyle }
}