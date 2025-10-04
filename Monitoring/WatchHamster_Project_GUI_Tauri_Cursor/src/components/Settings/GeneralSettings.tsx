import React from 'react'
import {
  VStack,
  FormControl,
  FormLabel,
  FormHelperText,
  Switch,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Card,
  CardHeader,
  CardBody,
  Heading,
  useToast,
} from '@chakra-ui/react'
// import { useSettings } from '../../hooks/useSettings'

interface GeneralSettingsProps {
  settings: {
    autoRefresh: boolean
    refreshInterval: number
    language: string
    notifications: boolean
    logLevel: string
    maxLogEntries: number
    backupEnabled: boolean
    backupInterval: number
  }
  onSettingChange: (key: keyof GeneralSettingsProps['settings'], value: any) => void
}

const GeneralSettings: React.FC<GeneralSettingsProps> = ({
  settings,
  onSettingChange,
}) => {
  const toast = useToast()

  const handleLanguageChange = (language: string) => {
    onSettingChange('language', language)
    
    // 언어 변경 알림
    toast({
      title: language === 'ko' ? '언어가 변경되었습니다' : 'Language changed',
      description: language === 'ko' 
        ? '한국어로 설정되었습니다' 
        : 'Set to English',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const handleRefreshIntervalChange = (value: number) => {
    if (value >= 1 && value <= 60) {
      onSettingChange('refreshInterval', value)
    }
  }

  const handleMaxLogEntriesChange = (value: number) => {
    if (value >= 100 && value <= 10000) {
      onSettingChange('maxLogEntries', value)
    }
  }

  const handleBackupIntervalChange = (value: number) => {
    if (value >= 1 && value <= 168) {
      onSettingChange('backupInterval', value)
    }
  }

  return (
    <Card data-testid="settings-card">
      <CardHeader>
        <Heading size="md">일반 설정</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 자동 새로고침 설정 */}
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="auto-refresh" mb="0" flex="1">
              자동 새로고침
            </FormLabel>
            <Switch
              id="auto-refresh"
              data-testid="auto-refresh-switch"
              isChecked={settings.autoRefresh}
              onChange={e => onSettingChange('autoRefresh', e.target.checked)}
              colorScheme="posco"
            />
          </FormControl>

          {/* 새로고침 간격 설정 */}
          <FormControl>
            <FormLabel>새로고침 간격 (초)</FormLabel>
            <NumberInput
              value={settings.refreshInterval}
              onChange={(_, value) => handleRefreshIntervalChange(value)}
              min={1}
              max={60}
              isDisabled={!settings.autoRefresh}
            >
              <NumberInputField data-testid="refresh-interval-input" />
              <NumberInputStepper>
                <NumberIncrementStepper />
                <NumberDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
            <FormHelperText>
              시스템 메트릭 자동 새로고침 간격을 설정합니다 (1-60초)
            </FormHelperText>
          </FormControl>

          {/* 언어 설정 */}
          <FormControl>
            <FormLabel>언어 / Language</FormLabel>
            <Select
              value={settings.language}
              onChange={e => handleLanguageChange(e.target.value)}
              data-testid="language-select"
            >
              <option value="ko">한국어 (Korean)</option>
              <option value="en">English</option>
            </Select>
            <FormHelperText>
              애플리케이션 인터페이스 언어를 선택합니다
            </FormHelperText>
          </FormControl>

          {/* 시스템 알림 설정 */}
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="notifications" mb="0" flex="1">
              시스템 알림
            </FormLabel>
            <Switch
              id="notifications"
              isChecked={settings.notifications}
              onChange={e => onSettingChange('notifications', e.target.checked)}
              colorScheme="posco"
            />
          </FormControl>

          {/* 로그 레벨 설정 */}
          <FormControl>
            <FormLabel>로그 레벨</FormLabel>
            <Select
              value={settings.logLevel}
              onChange={e => onSettingChange('logLevel', e.target.value)}
            >
              <option value="DEBUG">DEBUG - 모든 로그 표시</option>
              <option value="INFO">INFO - 정보성 로그 이상</option>
              <option value="WARN">WARN - 경고 로그 이상</option>
              <option value="ERROR">ERROR - 오류 로그만</option>
            </Select>
            <FormHelperText>
              표시할 최소 로그 레벨을 설정합니다
            </FormHelperText>
          </FormControl>

          {/* 최대 로그 항목 수 설정 */}
          <FormControl>
            <FormLabel>최대 로그 항목 수</FormLabel>
            <NumberInput
              value={settings.maxLogEntries}
              onChange={(_, value) => handleMaxLogEntriesChange(value)}
              min={100}
              max={10000}
              step={100}
            >
              <NumberInputField />
              <NumberInputStepper>
                <NumberIncrementStepper />
                <NumberDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
            <FormHelperText>
              메모리에 보관할 최대 로그 항목 수입니다 (100-10,000)
            </FormHelperText>
          </FormControl>

          {/* 자동 백업 설정 */}
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="backup-enabled" mb="0" flex="1">
              자동 백업
            </FormLabel>
            <Switch
              id="backup-enabled"
              isChecked={settings.backupEnabled}
              onChange={e => onSettingChange('backupEnabled', e.target.checked)}
              colorScheme="posco"
            />
          </FormControl>

          {/* 백업 간격 설정 */}
          <FormControl>
            <FormLabel>백업 간격 (시간)</FormLabel>
            <NumberInput
              value={settings.backupInterval}
              onChange={(_, value) => handleBackupIntervalChange(value)}
              min={1}
              max={168}
              isDisabled={!settings.backupEnabled}
            >
              <NumberInputField />
              <NumberInputStepper>
                <NumberIncrementStepper />
                <NumberDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
            <FormHelperText>
              설정 및 로그 자동 백업 간격을 설정합니다 (1-168시간)
            </FormHelperText>
          </FormControl>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default GeneralSettings