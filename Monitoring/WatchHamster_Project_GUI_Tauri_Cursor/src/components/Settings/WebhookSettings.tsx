import React, { useState } from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  VStack,
  HStack,
  FormControl,
  FormLabel,
  Input,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Button,
  Text,
  Divider,
  Badge,
  useToast,
  Alert,
  AlertIcon,
  Textarea,
  Switch,
  Select,
  Box,
  IconButton,
  Tooltip,
} from '@chakra-ui/react'
import { FiSend, FiEye, FiEyeOff, FiCopy, FiCheck } from 'react-icons/fi'
import { AppSettings } from '../../types'
import { apiService } from '../../services/api'

interface WebhookSettingsProps {
  settings: AppSettings
  onSettingChange: (key: keyof AppSettings, value: any) => void
}

interface WebhookTestResult {
  success: boolean
  message: string
  responseTime?: number
}

const WebhookSettings: React.FC<WebhookSettingsProps> = ({
  settings,
  onSettingChange
}) => {
  const [testResult, setTestResult] = useState<WebhookTestResult | null>(null)
  const [isTesting, setIsTesting] = useState(false)
  const [showPoscoUrl, setShowPoscoUrl] = useState(false)
  const [showWatchhamsterUrl, setShowWatchhamsterUrl] = useState(false)
  const [testMessage, setTestMessage] = useState('테스트 메시지입니다.')
  const [selectedWebhook, setSelectedWebhook] = useState<'posco' | 'watchhamster'>('posco')
  const toast = useToast()

  // 웹훅 설정 (실제로는 settings에서 가져와야 하지만 임시로 기본값 사용)
  const webhookSettings = {
    poscoWebhookUrl: 'https://infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg',
    watchhamsterWebhookUrl: 'https://infomax.dooray.com/services/3262462484277387103/3281274580264701322/nKUfZnjtRS2rHh-E9i9uZQ',
    timeout: 30,
    retryAttempts: 3,
    retryDelay: 2000,
    enableRetry: true,
    ...settings.webhook
  }

  const handleWebhookSettingChange = (key: string, value: any) => {
    const newWebhookSettings = { ...webhookSettings, [key]: value }
    onSettingChange('webhook' as keyof AppSettings, newWebhookSettings)
  }

  const testWebhook = async () => {
    setIsTesting(true)
    setTestResult(null)

    try {
      const webhookUrl = selectedWebhook === 'posco' 
        ? webhookSettings.poscoWebhookUrl 
        : webhookSettings.watchhamsterWebhookUrl

      if (!webhookUrl.trim()) {
        throw new Error('웹훅 URL이 설정되지 않았습니다.')
      }

      const startTime = Date.now()
      const response = await apiService.testWebhook({
        url: webhookUrl,
        message: testMessage
      })
      const endTime = Date.now()

      setTestResult({
        success: response.success,
        message: response.message,
        responseTime: endTime - startTime
      })

      if (response.success) {
        toast({
          title: '웹훅 테스트 성공',
          description: `메시지가 성공적으로 전송되었습니다. (${endTime - startTime}ms)`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else {
        toast({
          title: '웹훅 테스트 실패',
          description: response.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '웹훅 테스트 중 오류가 발생했습니다'
      setTestResult({
        success: false,
        message: errorMessage
      })

      toast({
        title: '웹훅 테스트 실패',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsTesting(false)
    }
  }

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast({
        title: '복사 완료',
        description: `${label}이(가) 클립보드에 복사되었습니다.`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: '복사 실패',
        description: '클립보드 복사에 실패했습니다.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const maskUrl = (url: string) => {
    if (!url) return ''
    const parts = url.split('/')
    if (parts.length > 3) {
      return `${parts[0]}//${parts[2]}/.../${parts[parts.length - 1].slice(0, 8)}***`
    }
    return url
  }

  return (
    <Card>
      <CardHeader>
        <Heading size="md">웹훅 설정</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 웹훅 테스트 결과 */}
          {testResult && (
            <Alert status={testResult.success ? 'success' : 'error'}>
              <AlertIcon />
              <VStack align="start" spacing={1} flex="1">
                <HStack>
                  <Text fontWeight="medium">
                    {testResult.success ? '웹훅 전송 성공' : '웹훅 전송 실패'}
                  </Text>
                  {testResult.responseTime && (
                    <Badge colorScheme="green" variant="subtle">
                      {testResult.responseTime}ms
                    </Badge>
                  )}
                </HStack>
                <Text fontSize="sm">{testResult.message}</Text>
              </VStack>
            </Alert>
          )}

          {/* POSCO 뉴스 웹훅 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">POSCO 뉴스 알림 웹훅</Text>
            
            <FormControl>
              <FormLabel>
                <HStack>
                  <Text>웹훅 URL</Text>
                  <Badge colorScheme="blue" variant="subtle">POSCO 뉴스</Badge>
                </HStack>
              </FormLabel>
              <HStack>
                <Input
                  type={showPoscoUrl ? 'text' : 'password'}
                  value={webhookSettings.poscoWebhookUrl}
                  onChange={(e) => handleWebhookSettingChange('poscoWebhookUrl', e.target.value)}
                  placeholder="https://infomax.dooray.com/services/..."
                />
                <Tooltip label={showPoscoUrl ? 'URL 숨기기' : 'URL 보기'}>
                  <IconButton
                    aria-label="URL 표시 토글"
                    icon={showPoscoUrl ? <FiEyeOff /> : <FiEye />}
                    onClick={() => setShowPoscoUrl(!showPoscoUrl)}
                    variant="outline"
                    size="sm"
                  />
                </Tooltip>
                <Tooltip label="URL 복사">
                  <IconButton
                    aria-label="URL 복사"
                    icon={<FiCopy />}
                    onClick={() => copyToClipboard(webhookSettings.poscoWebhookUrl, 'POSCO 웹훅 URL')}
                    variant="outline"
                    size="sm"
                  />
                </Tooltip>
              </HStack>
              <Text fontSize="xs" color="gray.500" mt={1}>
                POSCO 뉴스 상태 변경 시 알림을 받을 Dooray 웹훅 URL
              </Text>
              {!showPoscoUrl && webhookSettings.poscoWebhookUrl && (
                <Text fontSize="xs" color="gray.400" mt={1}>
                  현재 설정: {maskUrl(webhookSettings.poscoWebhookUrl)}
                </Text>
              )}
            </FormControl>
          </VStack>

          <Divider />

          {/* WatchHamster 시스템 웹훅 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">WatchHamster 시스템 상태 웹훅</Text>
            
            <FormControl>
              <FormLabel>
                <HStack>
                  <Text>웹훅 URL</Text>
                  <Badge colorScheme="purple" variant="subtle">시스템 상태</Badge>
                </HStack>
              </FormLabel>
              <HStack>
                <Input
                  type={showWatchhamsterUrl ? 'text' : 'password'}
                  value={webhookSettings.watchhamsterWebhookUrl}
                  onChange={(e) => handleWebhookSettingChange('watchhamsterWebhookUrl', e.target.value)}
                  placeholder="https://infomax.dooray.com/services/..."
                />
                <Tooltip label={showWatchhamsterUrl ? 'URL 숨기기' : 'URL 보기'}>
                  <IconButton
                    aria-label="URL 표시 토글"
                    icon={showWatchhamsterUrl ? <FiEyeOff /> : <FiEye />}
                    onClick={() => setShowWatchhamsterUrl(!showWatchhamsterUrl)}
                    variant="outline"
                    size="sm"
                  />
                </Tooltip>
                <Tooltip label="URL 복사">
                  <IconButton
                    aria-label="URL 복사"
                    icon={<FiCopy />}
                    onClick={() => copyToClipboard(webhookSettings.watchhamsterWebhookUrl, 'WatchHamster 웹훅 URL')}
                    variant="outline"
                    size="sm"
                  />
                </Tooltip>
              </HStack>
              <Text fontSize="xs" color="gray.500" mt={1}>
                WatchHamster 시스템 상태 보고서를 받을 Dooray 웹훅 URL
              </Text>
              {!showWatchhamsterUrl && webhookSettings.watchhamsterWebhookUrl && (
                <Text fontSize="xs" color="gray.400" mt={1}>
                  현재 설정: {maskUrl(webhookSettings.watchhamsterWebhookUrl)}
                </Text>
              )}
            </FormControl>
          </VStack>

          <Divider />

          {/* 웹훅 전송 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">전송 설정</Text>
            
            <HStack spacing={4}>
              <FormControl>
                <FormLabel>타임아웃 (초)</FormLabel>
                <NumberInput
                  value={webhookSettings.timeout}
                  onChange={(_, value) => handleWebhookSettingChange('timeout', value)}
                  min={5}
                  max={120}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>

              <FormControl>
                <FormLabel>재시도 횟수</FormLabel>
                <NumberInput
                  value={webhookSettings.retryAttempts}
                  onChange={(_, value) => handleWebhookSettingChange('retryAttempts', value)}
                  min={0}
                  max={5}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>

              <FormControl>
                <FormLabel>재시도 지연 (ms)</FormLabel>
                <NumberInput
                  value={webhookSettings.retryDelay}
                  onChange={(_, value) => handleWebhookSettingChange('retryDelay', value)}
                  min={1000}
                  max={10000}
                  step={1000}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
            </HStack>

            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="enable-retry" mb="0">
                실패 시 자동 재시도
              </FormLabel>
              <Switch
                id="enable-retry"
                isChecked={webhookSettings.enableRetry}
                onChange={(e) => handleWebhookSettingChange('enableRetry', e.target.checked)}
              />
            </FormControl>
          </VStack>

          <Divider />

          {/* 웹훅 테스트 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">웹훅 테스트</Text>
            
            <FormControl>
              <FormLabel>테스트할 웹훅</FormLabel>
              <Select
                value={selectedWebhook}
                onChange={(e) => setSelectedWebhook(e.target.value as 'posco' | 'watchhamster')}
              >
                <option value="posco">POSCO 뉴스 웹훅</option>
                <option value="watchhamster">WatchHamster 시스템 웹훅</option>
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>테스트 메시지</FormLabel>
              <Textarea
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                placeholder="테스트로 전송할 메시지를 입력하세요..."
                rows={3}
              />
            </FormControl>

            <Button
              leftIcon={<FiSend />}
              onClick={testWebhook}
              isLoading={isTesting}
              loadingText="전송 중"
              colorScheme="blue"
              isDisabled={!testMessage.trim()}
            >
              테스트 메시지 전송
            </Button>
          </VStack>

          <Divider />

          {/* 웹훅 사용 가이드 */}
          <Box>
            <Text fontWeight="medium" mb={3}>웹훅 설정 가이드</Text>
            <VStack align="stretch" spacing={2}>
              <Text fontSize="sm" color="gray.600">
                • POSCO 뉴스 웹훅: 환율, 뉴욕증시, KOSPI 마감 뉴스 상태 변경 시 알림
              </Text>
              <Text fontSize="sm" color="gray.600">
                • WatchHamster 웹훅: 시스템 전체 상태, 서비스 상태, 오류 발생 시 알림
              </Text>
              <Text fontSize="sm" color="gray.600">
                • Dooray 웹훅 URL 형식: https://infomax.dooray.com/services/[ID]/[TOKEN]
              </Text>
              <Text fontSize="sm" color="gray.600">
                • 테스트 기능을 사용하여 웹훅이 정상 작동하는지 확인하세요
              </Text>
            </VStack>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default WebhookSettings