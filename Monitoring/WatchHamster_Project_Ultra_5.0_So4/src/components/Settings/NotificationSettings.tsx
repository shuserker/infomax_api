import React, { useState } from 'react'
import {
  VStack,
  HStack,
  FormControl,
  FormLabel,
  FormHelperText,
  Switch,
  Select,
  Input,
  Button,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  Box,
  Badge,
  Divider,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  Spinner,
  Grid,
  GridItem,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react'
import { AppSettings } from '../../hooks/useSettings'

interface NotificationSettingsProps {
  settings: AppSettings
  onSettingChange: (key: keyof AppSettings, value: any) => void
  onNestedSettingChange: (path: string, value: any) => void
  onTestWebhook: () => Promise<boolean>
}

const NotificationSettings: React.FC<NotificationSettingsProps> = ({
  settings,
  onSettingChange,
  onNestedSettingChange,
  onTestWebhook,
}) => {
  const [isTestingWebhook, setIsTestingWebhook] = useState(false)
  const [webhookTestResult, setWebhookTestResult] = useState<'success' | 'error' | null>(null)
  const toast = useToast()

  const handleWebhookTest = async () => {
    if (!settings.webhookUrl.trim()) {
      toast({
        title: '웹훅 URL 필요',
        description: '먼저 웹훅 URL을 입력해주세요',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setIsTestingWebhook(true)
    setWebhookTestResult(null)

    try {
      const success = await onTestWebhook()
      setWebhookTestResult(success ? 'success' : 'error')
    } catch (error) {
      setWebhookTestResult('error')
    } finally {
      setIsTestingWebhook(false)
    }
  }

  const handleWebhookUrlChange = (url: string) => {
    onSettingChange('webhookUrl', url)
    setWebhookTestResult(null) // URL 변경 시 테스트 결과 초기화
  }

  const validateWebhookUrl = (url: string): boolean => {
    if (!url) return false
    
    // Discord 웹훅 URL 패턴
    const discordPattern = /^https:\/\/discord\.com\/api\/webhooks\/\d+\/[\w-]+$/
    // Slack 웹훅 URL 패턴
    const slackPattern = /^https:\/\/hooks\.slack\.com\/services\/[A-Z0-9]+\/[A-Z0-9]+\/[\w]+$/
    
    return discordPattern.test(url) || slackPattern.test(url)
  }

  const getWebhookType = (url: string): string => {
    if (url.includes('discord.com')) return 'Discord'
    if (url.includes('slack.com')) return 'Slack'
    return '알 수 없음'
  }

  const priorityOptions = [
    { value: 'high', label: '높음', color: 'red' },
    { value: 'medium', label: '보통', color: 'yellow' },
    { value: 'low', label: '낮음', color: 'green' },
  ]

  return (
    <Card>
      <CardHeader>
        <Heading size="md">알림 설정</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 기본 알림 설정 */}
          <Box>
            <Text fontWeight="medium" mb={4}>기본 알림 설정</Text>
            <VStack spacing={4} align="stretch">
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="system-alerts" mb="0" flex="1">
                  시스템 알림
                  <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                    CPU, 메모리, 디스크 사용량 경고
                  </Text>
                </FormLabel>
                <Switch
                  id="system-alerts"
                  isChecked={settings.systemAlerts}
                  onChange={e => onSettingChange('systemAlerts', e.target.checked)}
                  colorScheme="posco"
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="service-alerts" mb="0" flex="1">
                  서비스 알림
                  <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                    서비스 시작, 중지, 오류 알림
                  </Text>
                </FormLabel>
                <Switch
                  id="service-alerts"
                  isChecked={settings.serviceAlerts}
                  onChange={e => onSettingChange('serviceAlerts', e.target.checked)}
                  colorScheme="posco"
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="error-alerts" mb="0" flex="1">
                  오류 알림
                  <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                    시스템 오류 및 예외 상황 알림
                  </Text>
                </FormLabel>
                <Switch
                  id="error-alerts"
                  isChecked={settings.errorAlerts}
                  onChange={e => onSettingChange('errorAlerts', e.target.checked)}
                  colorScheme="posco"
                />
              </FormControl>
            </VStack>
          </Box>

          <Divider />

          {/* 알림 우선순위 설정 */}
          <Box>
            <Text fontWeight="medium" mb={4}>알림 우선순위 설정</Text>
            <Grid templateColumns="repeat(3, 1fr)" gap={4}>
              <GridItem>
                <FormControl>
                  <FormLabel fontSize="sm">시스템 알림 우선순위</FormLabel>
                  <Select
                    value={settings.alertPriority.system}
                    onChange={e => onNestedSettingChange('alertPriority.system', e.target.value)}
                    size="sm"
                  >
                    {priorityOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel fontSize="sm">서비스 알림 우선순위</FormLabel>
                  <Select
                    value={settings.alertPriority.service}
                    onChange={e => onNestedSettingChange('alertPriority.service', e.target.value)}
                    size="sm"
                  >
                    {priorityOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel fontSize="sm">오류 알림 우선순위</FormLabel>
                  <Select
                    value={settings.alertPriority.error}
                    onChange={e => onNestedSettingChange('alertPriority.error', e.target.value)}
                    size="sm"
                  >
                    {priorityOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </GridItem>
            </Grid>

            <Box mt={3} p={3} bg="blue.50" _dark={{ bg: 'blue.900' }} borderRadius="md">
              <Text fontSize="sm" color="blue.700" _dark={{ color: 'blue.200' }}>
                <strong>우선순위 설명:</strong><br />
                • 높음: 즉시 알림, 소리 포함<br />
                • 보통: 일반 알림, 소리 없음<br />
                • 낮음: 조용한 알림, 로그만 기록
              </Text>
            </Box>
          </Box>

          <Divider />

          {/* 웹훅 설정 */}
          <Box>
            <HStack justify="space-between" mb={4}>
              <Text fontWeight="medium">웹훅 설정</Text>
              <Switch
                isChecked={settings.webhookEnabled}
                onChange={e => onSettingChange('webhookEnabled', e.target.checked)}
                colorScheme="posco"
              />
            </HStack>

            <VStack spacing={4} align="stretch" opacity={settings.webhookEnabled ? 1 : 0.5}>
              <FormControl>
                <FormLabel>웹훅 URL</FormLabel>
                <Input
                  placeholder="https://discord.com/api/webhooks/... 또는 https://hooks.slack.com/services/..."
                  value={settings.webhookUrl}
                  onChange={e => handleWebhookUrlChange(e.target.value)}
                  isDisabled={!settings.webhookEnabled}
                />
                <FormHelperText>
                  Discord 또는 Slack 웹훅 URL을 입력하세요
                </FormHelperText>
              </FormControl>

              {/* 웹훅 URL 유효성 표시 */}
              {settings.webhookUrl && (
                <Box>
                  {validateWebhookUrl(settings.webhookUrl) ? (
                    <Alert status="success" size="sm">
                      <AlertIcon />
                      <AlertTitle fontSize="sm">유효한 {getWebhookType(settings.webhookUrl)} 웹훅 URL</AlertTitle>
                    </Alert>
                  ) : (
                    <Alert status="warning" size="sm">
                      <AlertIcon />
                      <AlertTitle fontSize="sm">올바르지 않은 웹훅 URL 형식</AlertTitle>
                    </Alert>
                  )}
                </Box>
              )}

              {/* 웹훅 테스트 */}
              <HStack>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleWebhookTest}
                  isLoading={isTestingWebhook}
                  loadingText="테스트 중..."
                  isDisabled={!settings.webhookEnabled || !settings.webhookUrl}
                  leftIcon={isTestingWebhook ? <Spinner size="xs" /> : undefined}
                >
                  웹훅 테스트
                </Button>

                {webhookTestResult && (
                  <Badge
                    colorScheme={webhookTestResult === 'success' ? 'green' : 'red'}
                    variant="subtle"
                  >
                    {webhookTestResult === 'success' ? '테스트 성공' : '테스트 실패'}
                  </Badge>
                )}
              </HStack>

              {/* 웹훅 설정 가이드 */}
              <Accordion allowToggle size="sm">
                <AccordionItem>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      <Text fontSize="sm" fontWeight="medium">웹훅 설정 가이드</Text>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel pb={4}>
                    <VStack spacing={3} align="stretch">
                      <Box>
                        <Text fontSize="sm" fontWeight="medium" mb={2}>Discord 웹훅 설정:</Text>
                        <Text fontSize="xs" color="gray.600" _dark={{ color: 'gray.400' }}>
                          1. Discord 서버 → 채널 설정 → 연동 → 웹훅<br />
                          2. "새 웹훅" 클릭 → 이름 설정 → "웹훅 URL 복사"<br />
                          3. 복사한 URL을 위 입력란에 붙여넣기
                        </Text>
                      </Box>
                      
                      <Divider />
                      
                      <Box>
                        <Text fontSize="sm" fontWeight="medium" mb={2}>Slack 웹훅 설정:</Text>
                        <Text fontSize="xs" color="gray.600" _dark={{ color: 'gray.400' }}>
                          1. Slack 앱 → 워크스페이스 → 앱 추가<br />
                          2. "Incoming Webhooks" 검색 → 설치<br />
                          3. 채널 선택 → "웹훅 URL 복사"<br />
                          4. 복사한 URL을 위 입력란에 붙여넣기
                        </Text>
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              </Accordion>
            </VStack>
          </Box>

          <Divider />

          {/* 고급 알림 설정 */}
          <Box>
            <Text fontWeight="medium" mb={4}>고급 알림 설정</Text>
            <VStack spacing={4} align="stretch">
              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <GridItem>
                  <FormControl>
                    <FormLabel fontSize="sm">알림 지연 시간 (초)</FormLabel>
                    <Select size="sm" defaultValue="0">
                      <option value="0">즉시</option>
                      <option value="30">30초</option>
                      <option value="60">1분</option>
                      <option value="300">5분</option>
                    </Select>
                    <FormHelperText fontSize="xs">
                      연속 알림 방지를 위한 지연 시간
                    </FormHelperText>
                  </FormControl>
                </GridItem>

                <GridItem>
                  <FormControl>
                    <FormLabel fontSize="sm">최대 알림 횟수</FormLabel>
                    <Select size="sm" defaultValue="10">
                      <option value="5">5회</option>
                      <option value="10">10회</option>
                      <option value="20">20회</option>
                      <option value="-1">무제한</option>
                    </Select>
                    <FormHelperText fontSize="xs">
                      동일 알림의 최대 전송 횟수
                    </FormHelperText>
                  </FormControl>
                </GridItem>
              </Grid>

              <FormControl>
                <FormLabel fontSize="sm">조용한 시간대</FormLabel>
                <HStack>
                  <Input
                    type="time"
                    defaultValue="22:00"
                    size="sm"
                    w="auto"
                  />
                  <Text fontSize="sm">부터</Text>
                  <Input
                    type="time"
                    defaultValue="08:00"
                    size="sm"
                    w="auto"
                  />
                  <Text fontSize="sm">까지</Text>
                </HStack>
                <FormHelperText fontSize="xs">
                  이 시간대에는 중요하지 않은 알림이 전송되지 않습니다
                </FormHelperText>
              </FormControl>
            </VStack>
          </Box>

          {/* 알림 미리보기 */}
          <Box>
            <Text fontWeight="medium" mb={3}>알림 미리보기</Text>
            <Card size="sm" bg="gray.50" _dark={{ bg: 'gray.700' }}>
              <CardBody>
                <VStack spacing={2} align="stretch">
                  <HStack justify="space-between">
                    <Text fontSize="sm" fontWeight="medium">WatchHamster 알림</Text>
                    <Badge colorScheme="blue" size="sm">시스템</Badge>
                  </HStack>
                  <Text fontSize="sm">
                    CPU 사용률이 85%를 초과했습니다. 현재 사용률: 87%
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    2024-01-15 14:30:25
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default NotificationSettings