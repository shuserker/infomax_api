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
import ConfigManager from '@/pages/ConfigManager'
import WebhookManager from '@/pages/WebhookManager'
import CompanyManager from '@/pages/CompanyManager'
import ApiPackageManagement from '@/pages/ApiPackageManagement'
import NotFound from '@/pages/NotFound'

interface BackendEvent {
  payload: string
}

function App() {
  const showToast = useCustomToast()

  useEffect(() => {
    // Tauri 이벤트 리스너 설정
    const setupEventListeners = async () => {
      // 백엔드 상태 이벤트
      await listen<BackendEvent>('backend-status', event => {
        showToast.showToast({
          title: '백엔드 상태',
          description: String(event.payload),
          status: 'info'
        })
      })

      // 백엔드 재시작 이벤트
      await listen<BackendEvent>('backend-restarted', event => {
        showToast.showSuccess('백엔드 재시작', String(event.payload))
      })

      // 백엔드 오류 이벤트
      await listen<BackendEvent>('backend-error', event => {
        showToast.showError('백엔드 오류', String(event.payload))
      })
    }

    setupEventListeners().catch(console.error)
  }, [showToast])

  return (
    <ErrorBoundary>
      <Box minH="100vh" bg="gray.50" _dark={{ bg: 'gray.900' }}>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="companies" element={<CompanyManager />} />
            <Route path="services" element={<Services />} />
            <Route path="api-packages" element={<ApiPackageManagement />} />
            <Route path="logs" element={<Logs />} />
            <Route path="settings" element={<Settings />} />
            <Route path="config" element={<ConfigManager />} />
            <Route path="webhooks" element={<WebhookManager />} />
          </Route>
          {/* 404 페이지 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Box>
    </ErrorBoundary>
  )
}

export default App
