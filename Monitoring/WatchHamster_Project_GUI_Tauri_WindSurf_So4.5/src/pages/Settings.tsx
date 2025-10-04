import React from 'react'
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react'
import { useSettings } from '../hooks/useSettings'
import GeneralSettings from '../components/Settings/GeneralSettings'
import ThemeSettings from '../components/Settings/ThemeSettings'
import NotificationSettings from '../components/Settings/NotificationSettings'
import ApiSettings from '../components/Settings/ApiSettings'
import WebhookSettings from '../components/Settings/WebhookSettings'
import MonitoringSettings from '../components/Settings/MonitoringSettings'
import ConfigManagement from '../components/Settings/ConfigManagement'
import DiagnosticsPanel from '../components/Settings/DiagnosticsPanel'

const Settings: React.FC = () => {
  const {
    settings,
    isLoading,
    isSaving,
    updateSetting,
    updateNestedSetting,
    saveSettings,
    resetSettings,
    exportSettings,
    importSettings,
    testWebhook,
  } = useSettings()

  if (isLoading) {
    return (
      <Box className="fade-in" display="flex" justifyContent="center" alignItems="center" minH="400px">
        <VStack spacing={4}>
          <Spinner size="xl" color="posco.500" />
          <Text>설정을 불러오는 중...</Text>
        </VStack>
      </Box>
    )
  }

  return (
    <Box className="fade-in" data-testid="settings-page">
      <VStack spacing={6} align="stretch">
        {/* 페이지 헤더 */}
        <Box>
          <Heading size="lg" mb={2}>
            설정
          </Heading>
          <Text color="gray.600" _dark={{ color: 'gray.400' }}>
            애플리케이션 설정을 관리합니다
          </Text>
        </Box>

        {/* 설정 저장 상태 알림 */}
        {isSaving && (
          <Alert status="info">
            <AlertIcon />
            <AlertTitle>설정 저장 중...</AlertTitle>
            <AlertDescription>잠시만 기다려주세요.</AlertDescription>
          </Alert>
        )}

        {/* 시스템 진단 */}
        <DiagnosticsPanel />

        {/* API 설정 */}
        <ApiSettings
          settings={settings}
          onSettingChange={updateSetting}
        />

        {/* 웹훅 설정 */}
        <WebhookSettings
          settings={settings}
          onSettingChange={updateSetting}
        />

        {/* 모니터링 설정 */}
        <MonitoringSettings
          settings={settings}
          onSettingChange={updateSetting}
        />

        {/* 일반 설정 */}
        <GeneralSettings
          settings={settings}
          onSettingChange={updateSetting}
        />

        {/* 테마 설정 */}
        <ThemeSettings
          settings={settings}
          onSettingChange={updateSetting}
          onNestedSettingChange={updateNestedSetting}
        />

        {/* 알림 설정 */}
        <NotificationSettings
          settings={settings}
          onSettingChange={updateSetting}
          onNestedSettingChange={updateNestedSetting}
          onTestWebhook={testWebhook}
        />

        {/* 설정 관리 */}
        <ConfigManagement
          settings={settings}
          onSettingChange={updateSetting}
          onSaveSettings={saveSettings}
          onResetSettings={resetSettings}
        />
      </VStack>
    </Box>
  )
}

export default Settings
