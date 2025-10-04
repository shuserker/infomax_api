import React from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  VStack,
  HStack,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Switch,
  Text,
  Divider,
  Select,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Box,
  Badge,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import { AppSettings } from '../../types'

interface MonitoringSettingsProps {
  settings: AppSettings
  onSettingChange: (key: keyof AppSettings, value: any) => void
}

const MonitoringSettings: React.FC<MonitoringSettingsProps> = ({
  settings,
  onSettingChange
}) => {
  // 모니터링 설정 (실제로는 settings에서 가져와야 하지만 임시로 기본값 사용)
  const monitoringSettings = {
    checkInterval: 30, // 30초
    newsCheckInterval: 60, // 1분
    systemCheckInterval: 10, // 10초
    gitCheckInterval: 300, // 5분
    alertThresholds: {
      cpu: 80,
      memory: 85,
      disk: 90,
      responseTime: 5000, // 5초
    },
    quietHours: {
      enabled: false,
      startTime: '22:00',
      endTime: '08:00',
      weekendsOnly: false,
    },
    autoRestart: {
      enabled: true,
      maxAttempts: 3,
      cooldownMinutes: 5,
    },
    notifications: {
      systemAlerts: true,
      serviceAlerts: true,
      newsAlerts: true,
      errorAlerts: true,
      performanceAlerts: true,
    },
    ...settings.monitoring
  }

  const handleMonitoringSettingChange = (key: string, value: any) => {
    const newMonitoringSettings = { ...monitoringSettings, [key]: value }
    onSettingChange('monitoring' as keyof AppSettings, newMonitoringSettings)
  }

  const handleNestedSettingChange = (category: string, key: string, value: any) => {
    const newSettings = {
      ...monitoringSettings,
      [category]: {
        ...monitoringSettings[category as keyof typeof monitoringSettings],
        [key]: value
      }
    }
    onSettingChange('monitoring' as keyof AppSettings, newSettings)
  }

  const formatInterval = (seconds: number) => {
    if (seconds < 60) return `${seconds}초`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}분`
    return `${Math.floor(seconds / 3600)}시간 ${Math.floor((seconds % 3600) / 60)}분`
  }

  return (
    <Card>
      <CardHeader>
        <Heading size="md">모니터링 설정</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 체크 간격 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">체크 간격</Text>
            
            <HStack spacing={4}>
              <FormControl>
                <FormLabel>뉴스 체크 간격</FormLabel>
                <NumberInput
                  value={monitoringSettings.newsCheckInterval}
                  onChange={(_, value) => handleMonitoringSettingChange('newsCheckInterval', value)}
                  min={10}
                  max={3600}
                  step={10}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  {formatInterval(monitoringSettings.newsCheckInterval)}
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel>시스템 체크 간격</FormLabel>
                <NumberInput
                  value={monitoringSettings.systemCheckInterval}
                  onChange={(_, value) => handleMonitoringSettingChange('systemCheckInterval', value)}
                  min={5}
                  max={300}
                  step={5}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  {formatInterval(monitoringSettings.systemCheckInterval)}
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel>Git 체크 간격</FormLabel>
                <NumberInput
                  value={monitoringSettings.gitCheckInterval}
                  onChange={(_, value) => handleMonitoringSettingChange('gitCheckInterval', value)}
                  min={60}
                  max={3600}
                  step={60}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  {formatInterval(monitoringSettings.gitCheckInterval)}
                </Text>
              </FormControl>
            </HStack>
          </VStack>

          <Divider />

          {/* 알림 임계값 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">알림 임계값</Text>
            
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>
                  <HStack justify="space-between">
                    <Text>CPU 사용률</Text>
                    <Badge colorScheme="blue" variant="outline">
                      {monitoringSettings.alertThresholds.cpu}%
                    </Badge>
                  </HStack>
                </FormLabel>
                <Slider
                  value={monitoringSettings.alertThresholds.cpu}
                  onChange={(value) => handleNestedSettingChange('alertThresholds', 'cpu', value)}
                  min={50}
                  max={95}
                  step={5}
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb />
                </Slider>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  CPU 사용률이 이 값을 초과하면 알림을 발송합니다
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel>
                  <HStack justify="space-between">
                    <Text>메모리 사용률</Text>
                    <Badge colorScheme="green" variant="outline">
                      {monitoringSettings.alertThresholds.memory}%
                    </Badge>
                  </HStack>
                </FormLabel>
                <Slider
                  value={monitoringSettings.alertThresholds.memory}
                  onChange={(value) => handleNestedSettingChange('alertThresholds', 'memory', value)}
                  min={60}
                  max={95}
                  step={5}
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb />
                </Slider>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  메모리 사용률이 이 값을 초과하면 알림을 발송합니다
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel>
                  <HStack justify="space-between">
                    <Text>디스크 사용률</Text>
                    <Badge colorScheme="orange" variant="outline">
                      {monitoringSettings.alertThresholds.disk}%
                    </Badge>
                  </HStack>
                </FormLabel>
                <Slider
                  value={monitoringSettings.alertThresholds.disk}
                  onChange={(value) => handleNestedSettingChange('alertThresholds', 'disk', value)}
                  min={70}
                  max={98}
                  step={2}
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb />
                </Slider>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  디스크 사용률이 이 값을 초과하면 알림을 발송합니다
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel>API 응답 시간 임계값 (ms)</FormLabel>
                <NumberInput
                  value={monitoringSettings.alertThresholds.responseTime}
                  onChange={(_, value) => handleNestedSettingChange('alertThresholds', 'responseTime', value)}
                  min={1000}
                  max={30000}
                  step={1000}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  API 응답 시간이 이 값을 초과하면 알림을 발송합니다
                </Text>
              </FormControl>
            </VStack>
          </VStack>

          <Divider />

          {/* 조용한 시간 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">조용한 시간</Text>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="quiet-hours-enabled" mb="0">
                조용한 시간 활성화
              </FormLabel>
              <Switch
                id="quiet-hours-enabled"
                isChecked={monitoringSettings.quietHours.enabled}
                onChange={(e) => handleNestedSettingChange('quietHours', 'enabled', e.target.checked)}
              />
            </FormControl>

            {monitoringSettings.quietHours.enabled && (
              <VStack spacing={4} align="stretch">
                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>시작 시간</FormLabel>
                    <Select
                      value={monitoringSettings.quietHours.startTime}
                      onChange={(e) => handleNestedSettingChange('quietHours', 'startTime', e.target.value)}
                    >
                      {Array.from({ length: 24 }, (_, i) => {
                        const hour = i.toString().padStart(2, '0')
                        return (
                          <option key={hour} value={`${hour}:00`}>
                            {hour}:00
                          </option>
                        )
                      })}
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>종료 시간</FormLabel>
                    <Select
                      value={monitoringSettings.quietHours.endTime}
                      onChange={(e) => handleNestedSettingChange('quietHours', 'endTime', e.target.value)}
                    >
                      {Array.from({ length: 24 }, (_, i) => {
                        const hour = i.toString().padStart(2, '0')
                        return (
                          <option key={hour} value={`${hour}:00`}>
                            {hour}:00
                          </option>
                        )
                      })}
                    </Select>
                  </FormControl>
                </HStack>

                <FormControl display="flex" alignItems="center">
                  <FormLabel htmlFor="weekends-only" mb="0">
                    주말에만 적용
                  </FormLabel>
                  <Switch
                    id="weekends-only"
                    isChecked={monitoringSettings.quietHours.weekendsOnly}
                    onChange={(e) => handleNestedSettingChange('quietHours', 'weekendsOnly', e.target.checked)}
                  />
                </FormControl>

                <Alert status="info" size="sm">
                  <AlertIcon />
                  <Text fontSize="sm">
                    조용한 시간 동안에는 중요하지 않은 알림이 억제됩니다. 
                    오류 및 시스템 장애 알림은 계속 발송됩니다.
                  </Text>
                </Alert>
              </VStack>
            )}
          </VStack>

          <Divider />

          {/* 자동 재시작 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">자동 재시작</Text>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="auto-restart-enabled" mb="0">
                서비스 자동 재시작 활성화
              </FormLabel>
              <Switch
                id="auto-restart-enabled"
                isChecked={monitoringSettings.autoRestart.enabled}
                onChange={(e) => handleNestedSettingChange('autoRestart', 'enabled', e.target.checked)}
              />
            </FormControl>

            {monitoringSettings.autoRestart.enabled && (
              <HStack spacing={4}>
                <FormControl>
                  <FormLabel>최대 재시도 횟수</FormLabel>
                  <NumberInput
                    value={monitoringSettings.autoRestart.maxAttempts}
                    onChange={(_, value) => handleNestedSettingChange('autoRestart', 'maxAttempts', value)}
                    min={1}
                    max={10}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

                <FormControl>
                  <FormLabel>재시도 대기 시간 (분)</FormLabel>
                  <NumberInput
                    value={monitoringSettings.autoRestart.cooldownMinutes}
                    onChange={(_, value) => handleNestedSettingChange('autoRestart', 'cooldownMinutes', value)}
                    min={1}
                    max={60}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
              </HStack>
            )}
          </VStack>

          <Divider />

          {/* 알림 타입 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">알림 타입</Text>
            
            <VStack spacing={3} align="stretch">
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="system-alerts" mb="0" flex="1">
                  시스템 알림
                </FormLabel>
                <Switch
                  id="system-alerts"
                  isChecked={monitoringSettings.notifications.systemAlerts}
                  onChange={(e) => handleNestedSettingChange('notifications', 'systemAlerts', e.target.checked)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="service-alerts" mb="0" flex="1">
                  서비스 알림
                </FormLabel>
                <Switch
                  id="service-alerts"
                  isChecked={monitoringSettings.notifications.serviceAlerts}
                  onChange={(e) => handleNestedSettingChange('notifications', 'serviceAlerts', e.target.checked)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="news-alerts" mb="0" flex="1">
                  뉴스 알림
                </FormLabel>
                <Switch
                  id="news-alerts"
                  isChecked={monitoringSettings.notifications.newsAlerts}
                  onChange={(e) => handleNestedSettingChange('notifications', 'newsAlerts', e.target.checked)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="error-alerts" mb="0" flex="1">
                  오류 알림
                </FormLabel>
                <Switch
                  id="error-alerts"
                  isChecked={monitoringSettings.notifications.errorAlerts}
                  onChange={(e) => handleNestedSettingChange('notifications', 'errorAlerts', e.target.checked)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="performance-alerts" mb="0" flex="1">
                  성능 알림
                </FormLabel>
                <Switch
                  id="performance-alerts"
                  isChecked={monitoringSettings.notifications.performanceAlerts}
                  onChange={(e) => handleNestedSettingChange('notifications', 'performanceAlerts', e.target.checked)}
                />
              </FormControl>
            </VStack>
          </VStack>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default MonitoringSettings