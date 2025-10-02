import { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import { listen } from '@tauri-apps/api/event'

// 레이아웃 컴포넌트
import { MainLayout } from '@/components/Layout'
import { ErrorBoundary, useCustomToast } from '@/components/Common'

// 페이지 컴포넌트
import Dashboard from '@/pages/Dashboard'
import Services from '@/pages/Services'
import Logs from '@/pages/Logs'
import Settings from '@/pages/Settings'

// 타입 정의
interface BackendEvent {
  payload: string
}

function App() {
  const { showInfo, showSuccess, showError } = useCustomToast()

  useEffect(() => {
    // Tauri 이벤트 리스너 설정
    const setupEventListeners = async () => {
      // 백엔드 상태 이벤트
      await listen<BackendEvent>('backend-status', event => {
        showInfo('백엔드 상태', String(event.payload))
      })

      // 백엔드 재시작 이벤트
      await listen<BackendEvent>('backend-restarted', event => {
        showSuccess('백엔드 재시작', String(event.payload))
      })

      // 백엔드 오류 이벤트
      await listen<BackendEvent>('backend-error', event => {
        showError('백엔드 오류', String(event.payload))
      })
    }

    setupEventListeners().catch(console.error)
  }, [showInfo, showSuccess, showError])

  return (
    <ErrorBoundary>
      <Box minH="100vh" bg="gray.50" _dark={{ bg: 'gray.900' }}>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="services" element={<Services />} />
            <Route path="logs" element={<Logs />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </Box>
    </ErrorBoundary>
  )
}

export default App
