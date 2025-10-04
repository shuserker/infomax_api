import React, { useState, useEffect } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Box,
  Text,
  VStack,
  HStack,
  Button,
  Input,
  Select,
  Switch,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  FormControl,
  FormLabel,
  FormHelperText,
  Divider,
  Badge,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardHeader,
  CardBody,
  Heading,
  useToast,
  IconButton,
  Tooltip,
  Textarea,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  useColorModeValue,
} from '@chakra-ui/react'
import {
  FiSave,
  FiRefreshCw,
  FiSettings,
  FiServer,
  FiShield,
  FiClock,
  FiDatabase,
  FiGlobe,
  FiZap,
  FiAlertTriangle
} from 'react-icons/fi'

interface ServiceConfig {
  [key: string]: any
}

interface ServiceConfigManagerProps {
  isOpen: boolean
  onClose: () => void
  serviceId: string
  serviceName: string
}

// 서비스별 설정 스키마 정의
const SERVICE_CONFIG_SCHEMAS = {
  api_server: {
    general: {
      port: { type: 'number', default: 8000, min: 1000, max: 65535, description: 'API 서버 포트' },
      host: { type: 'string', default: '127.0.0.1', description: '바인딩 호스트' },
      workers: { type: 'number', default: 1, min: 1, max: 8, description: '워커 프로세스 수' },
      debug: { type: 'boolean', default: false, description: '디버그 모드' }
    },
    security: {
      cors_enabled: { type: 'boolean', default: true, description: 'CORS 활성화' },
      rate_limit: { type: 'number', default: 100, min: 1, max: 1000, description: '분당 요청 한도' },
      timeout: { type: 'number', default: 30, min: 5, max: 300, description: '요청 타임아웃 (초)' },
      max_request_size: { type: 'number', default: 16, min: 1, max: 100, description: '최대 요청 크기 (MB)' }
    },
    performance: {
      connection_pool_size: { type: 'number', default: 20, min: 5, max: 100, description: '연결 풀 크기' },
      keep_alive_timeout: { type: 'number', default: 5, min: 1, max: 30, description: 'Keep-Alive 타임아웃' },
      max_concurrent_requests: { type: 'number', default: 1000, min: 100, max: 10000, description: '최대 동시 요청' }
    }
  },
  webhook_sender: {
    general: {
      retry_count: { type: 'number', default: 3, min: 0, max: 10, description: '재시도 횟수' },
      retry_delay: { type: 'number', default: 1000, min: 100, max: 10000, description: '재시도 지연 (ms)' },
      timeout: { type: 'number', default: 5000, min: 1000, max: 30000, description: '요청 타임아웃 (ms)' },
      batch_size: { type: 'number', default: 10, min: 1, max: 100, description: '배치 크기' }
    },
    webhooks: {
      dooray_webhook_url: { type: 'string', default: '', description: 'Dooray 웹훅 URL' },
      webhook_enabled: { type: 'boolean', default: true, description: '웹훅 활성화' },
      include_metadata: { type: 'boolean', default: true, description: '메타데이터 포함' },
      format_messages: { type: 'boolean', default: true, description: '메시지 포맷팅' }
    },
    monitoring: {
      log_all_requests: { type: 'boolean', default: true, description: '모든 요청 로그' },
      track_response_times: { type: 'boolean', default: true, description: '응답 시간 추적' },
      alert_on_failure: { type: 'boolean', default: true, description: '실패 시 알림' }
    }
  },
  watchhamster_monitor: {
    general: {
      monitoring_interval: { type: 'number', default: 60, min: 10, max: 3600, description: '모니터링 간격 (초)' },
      max_news_items: { type: 'number', default: 100, min: 10, max: 1000, description: '최대 뉴스 항목 수' },
      cache_ttl: { type: 'number', default: 300, min: 60, max: 7200, description: '캐시 TTL (초)' }
    },
    detection: {
      change_threshold: { type: 'number', default: 0.1, min: 0.01, max: 1.0, step: 0.01, description: '변경 감지 임계값' },
      ignore_minor_changes: { type: 'boolean', default: true, description: '소규모 변경 무시' },
      deep_comparison: { type: 'boolean', default: false, description: '상세 비교' }
    },
    notifications: {
      send_notifications: { type: 'boolean', default: true, description: '알림 전송' },
      notification_types: { type: 'multi-select', options: ['news', 'errors', 'status'], default: ['news', 'errors'], description: '알림 타입' },
      quiet_hours: { type: 'string', default: '22:00-06:00', description: '알림 중지 시간' }
    }
  },
  infomax_client: {
    general: {
      base_url: { type: 'string', default: 'https://global-api.einfomax.co.kr/apis/posco/news', description: 'API 기본 URL' },
      timeout: { type: 'number', default: 30, min: 5, max: 120, description: '요청 타임아웃 (초)' },
      retry_attempts: { type: 'number', default: 3, min: 0, max: 10, description: '재시도 횟수' }
    },
    connection: {
      connection_pool_size: { type: 'number', default: 10, min: 1, max: 50, description: '연결 풀 크기' },
      keep_alive: { type: 'boolean', default: true, description: 'Keep-Alive 사용' },
      verify_ssl: { type: 'boolean', default: true, description: 'SSL 인증서 검증' }
    }
  },
  news_parser: {
    general: {
      supported_types: { 
        type: 'multi-select', 
        options: ['exchange-rate', 'newyork-market-watch', 'kospi-close', 'company-news'],
        default: ['exchange-rate', 'newyork-market-watch', 'kospi-close'],
        description: '지원되는 뉴스 타입'
      },
      max_parse_time: { type: 'number', default: 10, min: 1, max: 60, description: '최대 파싱 시간 (초)' }
    },
    processing: {
      normalize_text: { type: 'boolean', default: true, description: '텍스트 정규화' },
      extract_entities: { type: 'boolean', default: false, description: '엔티티 추출' },
      sentiment_analysis: { type: 'boolean', default: false, description: '감정 분석' }
    }
  }
}

const ServiceConfigManager: React.FC<ServiceConfigManagerProps> = ({
  isOpen,
  onClose,
  serviceId,
  serviceName
}) => {
  const [config, setConfig] = useState<ServiceConfig>({})
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const [activeTab, setActiveTab] = useState(0)
  
  const toast = useToast()
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  const configSchema = SERVICE_CONFIG_SCHEMAS[serviceId as keyof typeof SERVICE_CONFIG_SCHEMAS] || {}
  const configCategories = Object.keys(configSchema)

  // 설정 로드
  const loadConfig = async () => {
    setLoading(true)
    try {
      // 실제 API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // 기본값으로 설정 초기화
      const defaultConfig: ServiceConfig = {}
      Object.entries(configSchema).forEach(([category, categoryConfig]) => {
        defaultConfig[category] = {}
        Object.entries(categoryConfig as any).forEach(([key, fieldConfig]) => {
          defaultConfig[category][key] = (fieldConfig as any).default
        })
      })
      
      setConfig(defaultConfig)
      setHasChanges(false)
    } catch (error) {
      toast({
        title: '설정 로드 실패',
        description: '서비스 설정을 불러오는데 실패했습니다.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  // 설정 저장
  const saveConfig = async () => {
    setSaving(true)
    try {
      // 실제 API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast({
        title: '설정 저장 완료',
        description: `${serviceName} 서비스 설정이 성공적으로 저장되었습니다.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      
      setHasChanges(false)
    } catch (error) {
      toast({
        title: '설정 저장 실패',
        description: '서비스 설정 저장 중 오류가 발생했습니다.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setSaving(false)
    }
  }

  // 설정 값 변경
  const updateConfig = (category: string, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
    setHasChanges(true)
  }

  // 설정 초기화
  const resetConfig = () => {
    loadConfig()
  }

  // 컴포넌트가 열릴 때 설정 로드
  useEffect(() => {
    if (isOpen) {
      loadConfig()
    }
  }, [isOpen, serviceId])

  // 필드 렌더링
  const renderField = (category: string, key: string, fieldConfig: any) => {
    const value = config[category]?.[key] ?? fieldConfig.default

    switch (fieldConfig.type) {
      case 'string':
        return fieldConfig.key === 'dooray_webhook_url' ? (
          <Textarea
            value={value || ''}
            onChange={(e) => updateConfig(category, key, e.target.value)}
            placeholder={fieldConfig.description}
            size="sm"
            rows={2}
          />
        ) : (
          <Input
            value={value || ''}
            onChange={(e) => updateConfig(category, key, e.target.value)}
            placeholder={fieldConfig.description}
            size="sm"
          />
        )

      case 'number':
        return fieldConfig.step ? (
          <NumberInput
            value={value}
            onChange={(_, val) => updateConfig(category, key, isNaN(val) ? fieldConfig.default : val)}
            min={fieldConfig.min}
            max={fieldConfig.max}
            step={fieldConfig.step}
            size="sm"
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        ) : (
          <VStack spacing={2} align="stretch">
            <NumberInput
              value={value}
              onChange={(_, val) => updateConfig(category, key, isNaN(val) ? fieldConfig.default : val)}
              min={fieldConfig.min}
              max={fieldConfig.max}
              size="sm"
            >
              <NumberInputField />
              <NumberInputStepper>
                <NumberIncrementStepper />
                <NumberDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
            <Slider
              value={value}
              onChange={(val) => updateConfig(category, key, val)}
              min={fieldConfig.min}
              max={fieldConfig.max}
              size="sm"
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb />
            </Slider>
          </VStack>
        )

      case 'boolean':
        return (
          <Switch
            isChecked={value}
            onChange={(e) => updateConfig(category, key, e.target.checked)}
            size="sm"
          />
        )

      case 'multi-select':
        return (
          <VStack spacing={2} align="stretch">
            {fieldConfig.options.map((option: string) => (
              <HStack key={option} justify="space-between">
                <Text fontSize="sm">{option}</Text>
                <Switch
                  size="sm"
                  isChecked={Array.isArray(value) && value.includes(option)}
                  onChange={(e) => {
                    const newValue = Array.isArray(value) ? [...value] : []
                    if (e.target.checked) {
                      if (!newValue.includes(option)) {
                        newValue.push(option)
                      }
                    } else {
                      const index = newValue.indexOf(option)
                      if (index > -1) {
                        newValue.splice(index, 1)
                      }
                    }
                    updateConfig(category, key, newValue)
                  }}
                />
              </HStack>
            ))}
          </VStack>
        )

      default:
        return (
          <Input
            value={value || ''}
            onChange={(e) => updateConfig(category, key, e.target.value)}
            size="sm"
          />
        )
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'general': return FiSettings
      case 'security': return FiShield
      case 'performance': return FiZap
      case 'webhooks': return FiGlobe
      case 'monitoring': return FiClock
      case 'detection': return FiAlertTriangle
      case 'notifications': return FiZap
      case 'connection': return FiDatabase
      case 'processing': return FiServer
      default: return FiSettings
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>
          <HStack>
            <FiSettings />
            <VStack spacing={1} align="start">
              <Text fontWeight="bold">{serviceName} 설정 관리</Text>
              <Text fontSize="sm" color="gray.500" fontWeight="normal">
                서비스 런타임 설정을 조정할 수 있습니다
              </Text>
            </VStack>
            {hasChanges && (
              <Badge colorScheme="orange" ml="auto">
                변경사항 있음
              </Badge>
            )}
          </HStack>
          <ModalCloseButton />
        </ModalHeader>

        <ModalBody>
          {loading ? (
            <VStack py={10} spacing={4}>
              <Text>설정을 불러오는 중...</Text>
            </VStack>
          ) : configCategories.length === 0 ? (
            <Alert status="info">
              <AlertIcon />
              <Box>
                <Text fontWeight="bold">설정 없음</Text>
                <Text fontSize="sm">이 서비스에 대한 설정 스키마가 정의되지 않았습니다.</Text>
              </Box>
            </Alert>
          ) : (
            <Tabs index={activeTab} onChange={setActiveTab}>
              <TabList>
                {configCategories.map((category) => {
                  const Icon = getCategoryIcon(category)
                  return (
                    <Tab key={category}>
                      <HStack spacing={2}>
                        <Icon size={14} />
                        <Text textTransform="capitalize">
                          {category === 'general' ? '일반' :
                           category === 'security' ? '보안' :
                           category === 'performance' ? '성능' :
                           category === 'webhooks' ? '웹훅' :
                           category === 'monitoring' ? '모니터링' :
                           category === 'detection' ? '감지' :
                           category === 'notifications' ? '알림' :
                           category === 'connection' ? '연결' :
                           category === 'processing' ? '처리' :
                           category}
                        </Text>
                      </HStack>
                    </Tab>
                  )
                })}
              </TabList>

              <TabPanels>
                {configCategories.map((category) => (
                  <TabPanel key={category} px={0}>
                    <VStack spacing={4} align="stretch">
                      {Object.entries(configSchema[category] as any).map(([key, fieldConfig]) => (
                        <FormControl key={key}>
                          <HStack justify="space-between" align="start">
                            <VStack spacing={1} align="start" flex="1">
                              <FormLabel fontSize="sm" mb={0} fontWeight="semibold">
                                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </FormLabel>
                              <FormHelperText mt={0} fontSize="xs">
                                {(fieldConfig as any).description}
                              </FormHelperText>
                            </VStack>
                            <Box minW="200px">
                              {renderField(category, key, fieldConfig)}
                            </Box>
                          </HStack>
                        </FormControl>
                      ))}
                    </VStack>
                  </TabPanel>
                ))}
              </TabPanels>
            </Tabs>
          )}
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            <Button variant="ghost" onClick={resetConfig} disabled={loading}>
              <FiRefreshCw />
              <Text ml={2}>초기화</Text>
            </Button>
            
            <Button variant="outline" onClick={onClose}>
              취소
            </Button>
            
            <Button 
              colorScheme="blue" 
              onClick={saveConfig}
              isLoading={saving}
              loadingText="저장 중"
              disabled={!hasChanges || loading}
            >
              <FiSave />
              <Text ml={2}>저장</Text>
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default ServiceConfigManager
