/**
 * 접근성(a11y) 기능 훅
 */

import React, { useEffect, useRef, useState, useCallback } from 'react'

// 키보드 네비게이션 훅
export const useKeyboardNavigation = (
  items: string[],
  onSelect?: (item: string, index: number) => void
) => {
  const [activeIndex, setActiveIndex] = useState(-1)
  const containerRef = useRef<HTMLElement>(null)

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        setActiveIndex(prev => (prev + 1) % items.length)
        break
      case 'ArrowUp':
        event.preventDefault()
        setActiveIndex(prev => (prev - 1 + items.length) % items.length)
        break
      case 'Enter':
      case ' ':
        if (activeIndex >= 0 && onSelect) {
          event.preventDefault()
          onSelect(items[activeIndex], activeIndex)
        }
        break
      case 'Escape':
        setActiveIndex(-1)
        break
      case 'Home':
        event.preventDefault()
        setActiveIndex(0)
        break
      case 'End':
        event.preventDefault()
        setActiveIndex(items.length - 1)
        break
    }
  }, [items, activeIndex, onSelect])

  useEffect(() => {
    const container = containerRef.current
    if (container) {
      container.addEventListener('keydown', handleKeyDown)
      return () => container.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  return {
    activeIndex,
    setActiveIndex,
    containerRef,
    getItemProps: (index: number) => ({
      'aria-selected': index === activeIndex,
      tabIndex: index === activeIndex ? 0 : -1,
      role: 'option'
    })
  }
}

// 포커스 관리 훅
export const useFocusManagement = () => {
  const focusableElementsSelector = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ].join(', ')

  const trapFocus = useCallback((container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(focusableElementsSelector)
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    const handleTabKey = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault()
          lastElement?.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault()
          firstElement?.focus()
        }
      }
    }

    container.addEventListener('keydown', handleTabKey)
    firstElement?.focus()

    return () => {
      container.removeEventListener('keydown', handleTabKey)
    }
  }, [focusableElementsSelector])

  const restoreFocus = useCallback((previousElement?: HTMLElement) => {
    if (previousElement && document.contains(previousElement)) {
      previousElement.focus()
    }
  }, [])

  return { trapFocus, restoreFocus }
}

// 스크린 리더 알림 훅
export const useScreenReaderAnnouncement = () => {
  const [announcement, setAnnouncement] = useState('')
  const announcementRef = useRef<HTMLDivElement>(null)

  const announce = useCallback((message: string, _priority: 'polite' | 'assertive' = 'polite') => {
    setAnnouncement(message)
    
    // 스크린 리더가 메시지를 읽을 수 있도록 잠시 후 초기화
    setTimeout(() => {
      setAnnouncement('')
    }, 1000)
  }, [])

  const AnnouncementComponent = () => {
    return React.createElement('div', {
      ref: announcementRef,
      'aria-live': 'polite',
      'aria-atomic': 'true',
      style: {
        position: 'absolute',
        left: '-10000px',
        width: '1px',
        height: '1px',
        overflow: 'hidden'
      }
    }, announcement)
  }

  return { announce, AnnouncementComponent }
}

// 색상 대비 검사 훅
export const useColorContrast = () => {
  const checkContrast = useCallback((foreground: string, background: string): number => {
    // RGB 값을 추출하는 헬퍼 함수
    const getRGB = (color: string) => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')!
      ctx.fillStyle = color
      ctx.fillRect(0, 0, 1, 1)
      const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data
      return { r, g, b }
    }

    // 상대 휘도 계산
    const getLuminance = (r: number, g: number, b: number) => {
      const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
      })
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
    }

    try {
      const fg = getRGB(foreground)
      const bg = getRGB(background)
      
      const fgLuminance = getLuminance(fg.r, fg.g, fg.b)
      const bgLuminance = getLuminance(bg.r, bg.g, bg.b)
      
      const lighter = Math.max(fgLuminance, bgLuminance)
      const darker = Math.min(fgLuminance, bgLuminance)
      
      return (lighter + 0.05) / (darker + 0.05)
    } catch {
      return 1 // 오류 시 기본값
    }
  }, [])

  const isAccessible = useCallback((contrast: number, level: 'AA' | 'AAA' = 'AA') => {
    const threshold = level === 'AAA' ? 7 : 4.5
    return contrast >= threshold
  }, [])

  return { checkContrast, isAccessible }
}

// 키보드 전용 사용자 감지 훅
export const useKeyboardUser = () => {
  const [isKeyboardUser, setIsKeyboardUser] = useState(false)

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        setIsKeyboardUser(true)
      }
    }

    const handleMouseDown = () => {
      setIsKeyboardUser(false)
    }

    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('mousedown', handleMouseDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleMouseDown)
    }
  }, [])

  return isKeyboardUser
}

// 미디어 쿼리 접근성 훅
export const useAccessibilityPreferences = () => {
  const [preferences, setPreferences] = useState({
    prefersReducedMotion: false,
    prefersHighContrast: false,
    prefersColorScheme: 'light' as 'light' | 'dark'
  })

  useEffect(() => {
    const updatePreferences = () => {
      setPreferences({
        prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        prefersHighContrast: window.matchMedia('(prefers-contrast: high)').matches,
        prefersColorScheme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      })
    }

    updatePreferences()

    const mediaQueries = [
      window.matchMedia('(prefers-reduced-motion: reduce)'),
      window.matchMedia('(prefers-contrast: high)'),
      window.matchMedia('(prefers-color-scheme: dark)')
    ]

    mediaQueries.forEach(mq => mq.addEventListener('change', updatePreferences))

    return () => {
      mediaQueries.forEach(mq => mq.removeEventListener('change', updatePreferences))
    }
  }, [])

  return preferences
}

// 텍스트 크기 조정 훅
export const useTextScaling = () => {
  const [scale, setScale] = useState(1)

  const increaseTextSize = useCallback(() => {
    setScale(prev => Math.min(prev + 0.1, 2))
  }, [])

  const decreaseTextSize = useCallback(() => {
    setScale(prev => Math.max(prev - 0.1, 0.8))
  }, [])

  const resetTextSize = useCallback(() => {
    setScale(1)
  }, [])

  useEffect(() => {
    document.documentElement.style.fontSize = `${scale * 16}px`
  }, [scale])

  return {
    scale,
    increaseTextSize,
    decreaseTextSize,
    resetTextSize
  }
}

// ARIA 라이브 리전 훅
export const useAriaLiveRegion = () => {
  const [messages, setMessages] = useState<Array<{
    id: string
    message: string
    priority: 'polite' | 'assertive'
  }>>([])

  const announce = useCallback((
    message: string, 
    priority: 'polite' | 'assertive' = 'polite'
  ) => {
    const id = Date.now().toString()
    setMessages(prev => [...prev, { id, message, priority }])

    // 메시지를 일정 시간 후 제거
    setTimeout(() => {
      setMessages(prev => prev.filter(msg => msg.id !== id))
    }, 3000)
  }, [])

  const LiveRegion = () => {
    return React.createElement(React.Fragment, null,
      messages.map(({ id, message, priority }) =>
        React.createElement('div', {
          key: id,
          'aria-live': priority,
          'aria-atomic': 'true',
          style: {
            position: 'absolute',
            left: '-10000px',
            width: '1px',
            height: '1px',
            overflow: 'hidden'
          }
        }, message)
      )
    )
  }

  return { announce, LiveRegion }
}

// 스킵 링크 훅
export const useSkipLinks = () => {
  const skipLinks = [
    { href: '#main-content', label: '메인 콘텐츠로 건너뛰기' },
    { href: '#navigation', label: '네비게이션으로 건너뛰기' },
    { href: '#sidebar', label: '사이드바로 건너뛰기' }
  ]

  const SkipLinks = () => {
    return React.createElement('div', {
      style: {
        position: 'absolute',
        top: '-40px',
        left: '6px',
        zIndex: 1000
      }
    }, skipLinks.map(link => 
      React.createElement('a', {
        key: link.href,
        href: link.href,
        style: {
          position: 'absolute',
          left: '-10000px',
          top: 'auto',
          width: '1px',
          height: '1px',
          overflow: 'hidden',
          background: '#000',
          color: '#fff',
          padding: '8px 16px',
          textDecoration: 'none',
          borderRadius: '4px'
        },
        onFocus: (e: React.FocusEvent<HTMLAnchorElement>) => {
          const target = e.target as HTMLElement
          target.style.position = 'static'
          target.style.left = 'auto'
          target.style.width = 'auto'
          target.style.height = 'auto'
          target.style.overflow = 'visible'
        },
        onBlur: (e: React.FocusEvent<HTMLAnchorElement>) => {
          const target = e.target as HTMLElement
          target.style.position = 'absolute'
          target.style.left = '-10000px'
          target.style.width = '1px'
          target.style.height = '1px'
          target.style.overflow = 'hidden'
        }
      }, link.label)
    ))
  }

  return { SkipLinks }
}

// 접근성 검사 훅
export const useAccessibilityChecker = () => {
  const checkElement = useCallback((element: HTMLElement) => {
    const issues: string[] = []

    // 이미지 alt 텍스트 검사
    const images = element.querySelectorAll('img')
    images.forEach(img => {
      if (!img.alt && !img.getAttribute('aria-label')) {
        issues.push(`이미지에 대체 텍스트가 없습니다: ${img.src}`)
      }
    })

    // 버튼 라벨 검사
    const buttons = element.querySelectorAll('button')
    buttons.forEach(button => {
      const hasText = button.textContent?.trim()
      const hasAriaLabel = button.getAttribute('aria-label')
      const hasAriaLabelledBy = button.getAttribute('aria-labelledby')
      
      if (!hasText && !hasAriaLabel && !hasAriaLabelledBy) {
        issues.push('버튼에 접근 가능한 이름이 없습니다')
      }
    })

    // 폼 라벨 검사
    const inputs = element.querySelectorAll('input, textarea, select')
    inputs.forEach(input => {
      const id = input.id
      const hasLabel = id && element.querySelector(`label[for="${id}"]`)
      const hasAriaLabel = input.getAttribute('aria-label')
      const hasAriaLabelledBy = input.getAttribute('aria-labelledby')
      
      if (!hasLabel && !hasAriaLabel && !hasAriaLabelledBy) {
        issues.push('폼 요소에 라벨이 없습니다')
      }
    })

    // 헤딩 구조 검사
    const headings = Array.from(element.querySelectorAll('h1, h2, h3, h4, h5, h6'))
    let previousLevel = 0
    
    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1))
      if (level > previousLevel + 1) {
        issues.push(`헤딩 레벨이 건너뛰어졌습니다: ${heading.tagName}`)
      }
      previousLevel = level
    })

    return issues
  }, [])

  return { checkElement }
}

// 접근성 설정 컨텍스트용 타입
export interface AccessibilitySettings {
  highContrast: boolean
  reducedMotion: boolean
  textScale: number
  keyboardNavigation: boolean
}

// 접근성 설정 훅
export const useAccessibilitySettings = () => {
  const [settings, setSettings] = useState<AccessibilitySettings>({
    highContrast: false,
    reducedMotion: false,
    textScale: 1,
    keyboardNavigation: true
  })

  const updateSetting = useCallback(<K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }, [])

  // 설정을 CSS 변수로 적용
  useEffect(() => {
    const root = document.documentElement
    
    root.style.setProperty('--text-scale', settings.textScale.toString())
    root.classList.toggle('high-contrast', settings.highContrast)
    root.classList.toggle('reduced-motion', settings.reducedMotion)
    
    if (settings.reducedMotion) {
      root.style.setProperty('--animation-duration', '0s')
      root.style.setProperty('--transition-duration', '0s')
    } else {
      root.style.removeProperty('--animation-duration')
      root.style.removeProperty('--transition-duration')
    }
  }, [settings])

  return {
    settings,
    updateSetting
  }
}