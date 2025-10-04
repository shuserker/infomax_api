import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

// 테마 설정
const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: true,
}

// POSCO 브랜드 컬러 팔레트
const colors = {
  posco: {
    50: '#f0f4ff',
    100: '#e0e7ff',
    200: '#c7d2fe',
    300: '#a5b4fc',
    400: '#818cf8',
    500: '#003d82', // POSCO 메인 컬러
    600: '#002d61',
    700: '#001e41',
    800: '#001020',
    900: '#000510',
  },
  brand: {
    50: '#f8f9fa',
    100: '#e9ecef',
    200: '#dee2e6',
    300: '#ced4da',
    400: '#adb5bd',
    500: '#6c757d',
    600: '#495057',
    700: '#343a40',
    800: '#212529',
    900: '#000000',
  },
  success: {
    50: '#f0fff4',
    100: '#c6f6d5',
    200: '#9ae6b4',
    300: '#68d391',
    400: '#48bb78',
    500: '#38a169',
    600: '#2f855a',
    700: '#276749',
    800: '#22543d',
    900: '#1a202c',
  },
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
  },
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },
}

// 컴포넌트 스타일 커스터마이징
const components = {
  Button: {
    variants: {
      posco: {
        bg: 'posco.500',
        color: 'white',
        _hover: {
          bg: 'posco.600',
          transform: 'translateY(-1px)',
          boxShadow: 'lg',
        },
        _active: {
          bg: 'posco.700',
          transform: 'translateY(0)',
        },
      },
      success: {
        bg: 'success.500',
        color: 'white',
        _hover: {
          bg: 'success.600',
        },
      },
      warning: {
        bg: 'warning.500',
        color: 'white',
        _hover: {
          bg: 'warning.600',
        },
      },
      error: {
        bg: 'error.500',
        color: 'white',
        _hover: {
          bg: 'error.600',
        },
      },
    },
  },
  Card: {
    baseStyle: {
      container: {
        borderRadius: 'lg',
        boxShadow: 'sm',
        _hover: {
          boxShadow: 'md',
          transform: 'translateY(-1px)',
        },
        transition: 'all 0.2s',
      },
    },
  },
  Badge: {
    variants: {
      running: {
        bg: 'success.500',
        color: 'white',
      },
      stopped: {
        bg: 'error.500',
        color: 'white',
      },
      warning: {
        bg: 'warning.500',
        color: 'white',
      },
    },
  },
}

// 글로벌 스타일
const styles = {
  global: (props: any) => ({
    body: {
      bg: props.colorMode === 'dark' ? 'gray.900' : 'gray.50',
      color: props.colorMode === 'dark' ? 'white' : 'gray.800',
    },
    '*::placeholder': {
      color: props.colorMode === 'dark' ? 'gray.400' : 'gray.500',
    },
    '*, *::before, &::after': {
      borderColor: props.colorMode === 'dark' ? 'gray.700' : 'gray.200',
    },
  }),
}

// 폰트 설정
const fonts = {
  heading: `'Noto Sans KR', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"`,
  body: `'Noto Sans KR', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"`,
  mono: `'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace`,
}

// 반응형 브레이크포인트
const breakpoints = {
  sm: '30em',
  md: '48em',
  lg: '62em',
  xl: '80em',
  '2xl': '96em',
}

// 테마 확장
const theme = extendTheme({
  config,
  colors,
  components,
  styles,
  fonts,
  breakpoints,
  space: {
    '4.5': '1.125rem',
    '5.5': '1.375rem',
    '6.5': '1.625rem',
  },
  sizes: {
    '4.5': '1.125rem',
    '5.5': '1.375rem',
    '6.5': '1.625rem',
  },
})

export default theme
