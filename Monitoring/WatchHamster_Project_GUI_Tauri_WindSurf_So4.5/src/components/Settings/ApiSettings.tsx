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
  Spinner,
  Tooltip,
  Switch,
} from '@chakra-ui/react'
import { FiActivity, FiCheck, FiX } from 'react-icons/fi'
import { AppSettings } from '../../types'
import { apiService } from '../../services/api'

interface ApiSettingsProps {
  settings: AppSettings
  onSettingChange: (key: keyof AppSettings, value: any) => void
}

interface ApiTestResult {
  connected: boolean
  latency: number
  version: string
  error?: string
}

const ApiSettings: React.FC<ApiSettingsProps> = ({
  settings,
  onSettingChange
}) => {
  const [testResult, setTestResult] = useState<ApiTestResult | null>(null)
  const [isTesting, setIsTesting] = useState(false)
  const toast = useToast()

  // API 설정 (실제로는 settings에서 가져와야 하지만 임시로 기본값 사용)
  const apiSettings = {
    infomaxApiUrl: 'https://global-api.einfomax.co.kr/apis/posco/news',
    timeout: 30,
    retryAttempts: 3,
    retryDelay: 1000,
    enableCache: true,
    cacheTimeout: 300, // 5분
    ...settings.api
  }

  const handleApiSettingChange = (key: string, value: any) => {
    const newApiSettings = { ...apiSettings, [key]: value }
    onSettingChange('api' as keyof AppSettings, newApiSettings)
  }

  const testApiConnection = async () => {
    setIsTesting(true)
    setTestResult(null)

    try {
      const startTime = Date.now()
      const response = await apiService.testConnection()
      const endTime = Date.now()

      setTestResult({
        connected: response.connected,
        latency: endTime - startTime,
        version: response.version
      })

      if (response.connected) {
        toast({
          title: 'API 연결 테스트 성공',
          description: `응답 시간: ${endTime - startTime}ms`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else {
        toast({
          title: 'API 연결 테스트 실패',
          description: 'API 서버에 연결할 수 없습니다.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'API 연결 테스트 중 오류가 발생했습니다'
      setTestResult({
        connected: false,
        latency: 0,
        version: 'unknown',
        error: errorMessage
      })

      toast({
        title: 'API 연결 테스트 실패',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsTesting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">API 설정</Heading>
          <Button
            size="sm"
            leftIcon={<FiActivity />}
            onClick={testApiConnection}
            isLoading={isTesting}
            loadingText="테스트 중"
            variant="outline"
          >
            연결 테스트
          </Button>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 연결 테스트 결과 */}
          {testResult && (
            <Alert status={testResult.connected ? 'success' : 'error'}>
              <AlertIcon />
              <VStack align="start" spacing={1} flex="1">
                <HStack>
                  <Text fontWeight="medium">
                    {testResult.connected ? 'API 연결 성공' : 'API 연결 실패'}
                  </Text>
                  {testResult.connected && (
                    <Badge colorScheme="green" variant="subtle">
                      {testResult.latency}ms
                    </Badge>
                  )}
                </HStack>
                {testResult.error && (
                  <Text fontSize="sm">{testResult.error}</Text>
                )}
                {testResult.connected && (
                  <Text fontSize="sm" color="gray.600">
                    서버 버전: {testResult.version}
                  </Text>
                )}
              </VStack>
            </Alert>
          )}

          {/* INFOMAX API 설정 */}
          <VStack spacing={4} align="stretch">
            <Text fontWeight="medium" fontSize="lg">INFOMAX API</Text>
            
            <FormControl>
              <FormLabel>API URL</FormLabel>
              <Input
                value={apiSettings.infomaxApiUrl}
                onChange={(e) => handleApiSettingChange('infomaxApiUrl', e.target.value)}
                placeholder="https://global-api.einfomax.co.kr/apis/posco/news"
              />
              <Text fontSize="xs" color="gray.500" mt={1}>
                POSCO 뉴스 데이터를 가져올 API 엔드포인트
              </Text>
            </FormControl>

            <HStack spacing={4}>
              <FormControl>
                <FormLabel>타임아웃 (초)</FormLabel>
                <NumberInput
                  value={apiSettings.timeout}
                  onChange={(_, value) => handleApiSettingChange('timeout', value)}
                  min={5}
                  max={300}
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
                  value={apiSettings.retryAttempts}
                  onChange={(_, value) => handleApiSettingChange('retryAttempts', value)}
                  min={0}
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
                <FormLabel>재시도 지연 (ms)</FormLabel>
                <NumberInput
                  value={apiSettings.retryDelay}
                  onChange={(_, value) => handleApiSettingChange('retryDelay', value)}
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
              </FormControl>
            </HStack>

            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="enable-cache" mb="0">
                캐시 활성화
              </FormLabel>
              <Switch
                id="enable-cache"
                isChecked={apiSettings.enableCache}
                onChange={(e) => handleApiSettingChange('enableCache', e.target.checked)}
              />
            </FormControl>

            {apiSettings.enableCache && (
              <FormControl>
                <FormLabel>캐시 유효 시간 (초)</FormLabel>
                <NumberInput
                  value={apiSettings.cacheTimeout}
                  onChange={(_, value) => handleApiSettingChange('cacheTimeout', value)}
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
                  API 응답을 캐시할 시간 (60초 ~ 1시간)
                </Text>
              </FormControl>
            )}
          </VStack>

          <Divider />

          {/* 지원하는 뉴스 타입 */}
          <VStack spacing={3} align="stretch">
            <Text fontWeight="medium">지원하는 뉴스 타입</Text>
            <HStack spacing={2} wrap="wrap">
              <Badge colorScheme="blue" variant="outline">exchange-rate</Badge>
              <Badge colorScheme="green" variant="outline">newyork-market-watch</Badge>
              <Badge colorScheme="purple" variant="outline">kospi-close</Badge>
            </HStack>
            <Text fontSize="sm" color="gray.600">
              현재 시스템에서 모니터링하는 뉴스 타입들입니다.
            </Text>
          </VStack>

          <Divider />

          {/* API 상태 정보 */}
          <VStack spacing={3} align="stretch">
            <Text fontWeight="medium">API 상태 정보</Text>
            <HStack justify="space-between">
              <Text fontSize="sm">마지막 연결 테스트</Text>
              <Text fontSize="sm" color="gray.600">
                {testResult ? new Date().toLocaleString('ko-KR') : '테스트하지 않음'}
              </Text>
            </HStack>
            <HStack justify="space-between">
              <Text fontSize="sm">연결 상태</Text>
              <HStack>
                {testResult ? (
                  testResult.connected ? (
                    <>
                      <FiCheck color="green" />
                      <Text fontSize="sm" color="green.500">연결됨</Text>
                    </>
                  ) : (
                    <>
                      <FiX color="red" />
                      <Text fontSize="sm" color="red.500">연결 실패</Text>
                    </>
                  )
                ) : (
                  <Text fontSize="sm" color="gray.500">알 수 없음</Text>
                )}
              </HStack>
            </HStack>
            {testResult?.connected && (
              <HStack justify="space-between">
                <Text fontSize="sm">응답 시간</Text>
                <Text fontSize="sm" color="gray.600">{testResult.latency}ms</Text>
              </HStack>
            )}
          </VStack>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default ApiSettings