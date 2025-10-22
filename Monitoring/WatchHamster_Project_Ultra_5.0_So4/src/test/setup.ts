import '@testing-library/jest-dom'
import { vi } from 'vitest'
import './vitest.d.ts'

// afterEach를 전역으로 사용할 수 있도록 설정
// globalThis.afterEach = afterEach

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any

// Mock matchMedia
const mockMediaQueryList = {
  matches: false,
  media: '',
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    ...mockMediaQueryList,
    media: query,
  })),
})

// Mock for Chakra UI ColorModeProvider
Object.defineProperty(window, 'addEventListener', {
  writable: true,
  value: vi.fn(),
})

Object.defineProperty(window, 'removeEventListener', {
  writable: true,
  value: vi.fn(),
})



// Mock for color mode detection
Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    getPropertyValue: () => '',
  }),
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
}

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

// Mock sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: localStorageMock,
  writable: true,
})

// Mock Tauri API
const mockTauri = {
  invoke: vi.fn().mockResolvedValue({}),
  listen: vi.fn().mockResolvedValue(() => {}),
  emit: vi.fn().mockResolvedValue(undefined),
  convertFileSrc: vi.fn().mockReturnValue(''),
}

// @ts-expect-error - Tauri global is not defined in test environment
global.__TAURI__ = mockTauri

// Mock @tauri-apps/api modules
vi.mock('@tauri-apps/api/tauri', () => ({
  invoke: mockTauri.invoke,
}))

vi.mock('@tauri-apps/api/event', () => ({
  listen: mockTauri.listen,
  emit: mockTauri.emit,
}))

vi.mock('@tauri-apps/api/path', () => ({
  convertFileSrc: mockTauri.convertFileSrc,
}))

// Mock environment variables
vi.mock('import.meta', () => ({
  env: {
    VITE_API_BASE_URL: 'http://localhost:8000',
    VITE_BACKEND_PORT: '8000',
    DEV: true,
    PROD: false,
  },
}))

// Mock axios for API calls
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn().mockResolvedValue({ data: {} }),
      post: vi.fn().mockResolvedValue({ data: {} }),
      put: vi.fn().mockResolvedValue({ data: {} }),
      delete: vi.fn().mockResolvedValue({ data: {} }),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} }),
  },
}))

// Mock React Query
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn().mockReturnValue({
    data: null,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useMutation: vi.fn().mockReturnValue({
    mutate: vi.fn(),
    isLoading: false,
    error: null,
  }),
  QueryClient: vi.fn().mockImplementation(() => ({
    setQueryData: vi.fn(),
    getQueryData: vi.fn(),
    invalidateQueries: vi.fn(),
  })),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock Framer Motion
vi.mock('framer-motion', () => ({
  motion: {
    div: 'div',
    span: 'span',
    button: 'button',
    form: 'form',
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock React Router
vi.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => children,
  Routes: ({ children }: { children: React.ReactNode }) => children,
  Route: ({ children }: { children: React.ReactNode }) => children,
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
  NavLink: ({ children, to }: { children: React.ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/' }),
  Outlet: () => null,
}))

// Mock React Icons
vi.mock('react-icons/fi', () => ({
  FiHome: () => 'FiHome',
  FiSettings: () => 'FiSettings',
  FiRefreshCw: () => 'FiRefreshCw',
  FiAlertTriangle: () => 'FiAlertTriangle',
}))

vi.mock('react-icons/md', () => ({
  MdDashboard: () => 'MdDashboard',
  MdSettings: () => 'MdSettings',
  MdList: () => 'MdList',
  MdDescription: () => 'MdDescription',
  MdMonitor: () => 'MdMonitor',
  MdBusiness: () => 'MdBusiness',
  MdMenu: () => 'MdMenu',
  MdPlayArrow: () => 'MdPlayArrow',
  MdStop: () => 'MdStop',
  MdRefresh: () => 'MdRefresh',
}))

// Mock Recharts
vi.mock('recharts', () => ({
  LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
}))

// Mock react-window
vi.mock('react-window', () => ({
  FixedSizeList: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="fixed-size-list">{children}</div>
  ),
}))

// Console 경고 억제 (테스트 중 불필요한 로그 제거)
const originalConsoleWarn = console.warn
const originalConsoleError = console.error

console.warn = (...args: any[]) => {
  // Chakra UI 관련 경고 억제
  if (
    args[0]?.includes?.('Warning: ReactDOM.render') ||
    args[0]?.includes?.('Warning: componentWillReceiveProps') ||
    args[0]?.includes?.('color mode')
  ) {
    return
  }
  originalConsoleWarn(...args)
}

console.error = (...args: any[]) => {
  // React 18 관련 경고 억제
  if (
    args[0]?.includes?.('Warning: ReactDOM.render') ||
    args[0]?.includes?.('act()')
  ) {
    return
  }
  originalConsoleError(...args)
}

// Mock WebSocket
global.WebSocket = class WebSocket {
  constructor(url: string) {
    this.url = url
  }

  url: string
  readyState = WebSocket.CONNECTING

  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  send = vi.fn()
  close = vi.fn()
  addEventListener = vi.fn()
  removeEventListener = vi.fn()
  dispatchEvent = vi.fn()
} as any
