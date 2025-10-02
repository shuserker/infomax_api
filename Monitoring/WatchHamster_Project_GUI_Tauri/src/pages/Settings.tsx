import React, { useRef } from 'react'
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  Button,
  Divider,
  useToast,
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

  const fileInputRef = useRef<HTMLInputElement>(null)
  const toast = useToast()

  const handleSaveSettings = async () => {
    const success = await saveSettings()
    if (success) {
      toast({
        title: '설정 저장 완료',
        description: '모든 설정이 성공적으로 저장되었습니다',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const handleResetSettings = async () => {
    const success = await resetSettings()
    if (success) {
      toast({
        title: '설정 초기화 완료',
        description: '모든 설정이 기본값으로 초기화되었습니다',
        status: 'info',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const handleExportSettings = () => {
    exportSettings()
  }

  const handleImportSettings = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const success = await importSettings(file)
      if (success) {
        toast({
          title: '설정 가져오기 완료',
          description: '설정이 성공적으로 가져와졌습니다',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      }
    }
    // 파일 입력 초기화
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

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

        {/* 설정 관리 버튼들 */}
        <Card>
          <CardHeader>
            <Heading size="md">설정 관리</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack spacing={4} justify="space-between" wrap="wrap">
                <HStack spacing={3}>
                  <Button
                    variant="outline"
                    onClick={handleExportSettings}
                    size="sm"
                  >
                    설정 내보내기
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleImportSettings}
                    size="sm"
                  >
                    설정 가져오기
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".json"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />
                </HStack>

                <HStack spacing={3}>
                  <Button
                    variant="outline"
                    onClick={handleResetSettings}
                    isDisabled={isSaving}
                  >
                    기본값으로 초기화
                  </Button>
                  <Button
                    colorScheme="posco"
                    onClick={handleSaveSettings}
                    isLoading={isSaving}
                    loadingText="저장 중..."
                  >
                    설정 저장
                  </Button>
                </HStack>
              </HStack>

              <Divider />

              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                • 설정 내보내기: 현재 설정을 JSON 파일로 저장합니다<br />
                • 설정 가져오기: 이전에 내보낸 설정 파일을 불러옵니다<br />
                • 기본값으로 초기화: 모든 설정을 초기 상태로 되돌립니다
              </Text>
            </VStack>
          </CardBody>
        </Card>

        {/* 시스템 정보 */}
        <Card>
          <CardHeader>
            <Heading size="md">시스템 정보</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              <HStack justify="space-between">
                <Text fontWeight="medium">애플리케이션 버전</Text>
                <Text>v1.0.0 Tauri Edition</Text>
              </HStack>
              <Divider />
              <HStack justify="space-between">
                <Text fontWeight="medium">플랫폼</Text>
                <Text>Windows 11</Text>
              </HStack>
              <Divider />
              <HStack justify="space-between">
                <Text fontWeight="medium">백엔드 상태</Text>
                <Text color="green.500">연결됨</Text>
              </HStack>
              <Divider />
              <HStack justify="space-between">
                <Text fontWeight="medium">마지막 업데이트</Text>
                <Text>{new Date().toLocaleString('ko-KR')}</Text>
              </HStack>
              <Divider />
              <HStack justify="space-between">
                <Text fontWeight="medium">설정 파일 위치</Text>
                <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                  로컬 스토리지
                </Text>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}

export default Settings
