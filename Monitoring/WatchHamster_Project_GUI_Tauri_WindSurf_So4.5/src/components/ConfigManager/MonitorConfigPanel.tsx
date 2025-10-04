import React, { useState, useEffect } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Button,
  VStack,
  HStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  FormControl,
  FormLabel,
  Input,
  Switch,
  Textarea,
  useToast,
  Spinner,
  Text,
} from '@chakra-ui/react'
import { FiSave, FiX } from 'react-icons/fi'
import axios from 'axios'
import ApiEndpointEditor from './ApiEndpointEditor'
import ScheduleEditor from './ScheduleEditor'
import WebhookEditor from './WebhookEditor'

const API_BASE = 'http://localhost:8000'

interface MonitorConfigPanelProps {
  isOpen: boolean
  onClose: () => void
  monitorName: string
}

const MonitorConfigPanel: React.FC<MonitorConfigPanelProps> = ({
  isOpen,
  onClose,
  monitorName,
}) => {
  const [config, setConfig] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const toast = useToast()

  useEffect(() => {
    if (isOpen && monitorName !== 'new') {
      loadConfig()
    } else if (monitorName === 'new') {
      // 새 모니터 기본 설정
      setConfig({
        name: '',
        display_name: '',
        enabled: true,
        description: '',
        api: {
          endpoint: '',
          method: 'GET',
          auth: { type: 'bearer', token: '' },
          headers: {},
          params: {},
          timeout: 30,
        },
        schedule: {
          interval: 5,
          timeRange: { start: '09:00', end: '18:00' },
          daysOfWeek: [1, 2, 3, 4, 5],
          excludeHolidays: true,
        },
        retry: {
          maxAttempts: 3,
          delayMs: 1000,
          backoff: 'exponential',
        },
        parsing: {
          type: 'json',
          rules: [],
          validation: [],
        },
        webhook: {
          enabled: true,
          url: '',
          templateId: 'default',
          condition: 'on_change',
          timeout: 10,
        },
        metadata: {
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          version: '1.0.0',
        },
      })
      setIsLoading(false)
    }
  }, [isOpen, monitorName])

  const loadConfig = async () => {
    setIsLoading(true)
    try {
      const res = await axios.get(`${API_BASE}/api/config/monitors/${monitorName}`)
      setConfig(res.data)
    } catch (error) {
      console.error('설정 로드 실패:', error)
      toast({
        title: '설정 로드 실패',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      if (monitorName === 'new') {
        await axios.post(`${API_BASE}/api/config/monitors`, config)
        toast({
          title: '모니터 생성 완료',
          status: 'success',
          duration: 3000,
        })
      } else {
        await axios.put(`${API_BASE}/api/config/monitors/${monitorName}`, config)
        toast({
          title: '설정 저장 완료',
          status: 'success',
          duration: 3000,
        })
      }
      onClose()
    } catch (error: any) {
      console.error('설정 저장 실패:', error)
      toast({
        title: '설정 저장 실패',
        description: error.response?.data?.detail || '알 수 없는 오류',
        status: 'error',
        duration: 5000,
      })
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent>
          <ModalBody py={10}>
            <VStack>
              <Spinner size="xl" />
              <Text>설정을 불러오는 중...</Text>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    )
  }

  if (!config) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>
          {monitorName === 'new' ? '새 모니터 추가' : `${config.display_name} 설정`}
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody overflowY="auto">
          <Tabs colorScheme="blue">
            <TabList>
              <Tab>기본 정보</Tab>
              <Tab>API 설정</Tab>
              <Tab>스케줄</Tab>
              <Tab>웹훅</Tab>
            </TabList>

            <TabPanels>
              {/* 기본 정보 */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <FormControl isRequired>
                    <FormLabel>모니터 ID</FormLabel>
                    <Input
                      value={config.name}
                      onChange={(e) => setConfig({ ...config, name: e.target.value })}
                      placeholder="kospi-close"
                      isDisabled={monitorName !== 'new'}
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>표시 이름</FormLabel>
                    <Input
                      value={config.display_name}
                      onChange={(e) => setConfig({ ...config, display_name: e.target.value })}
                      placeholder="코스피 마감"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>설명</FormLabel>
                    <Textarea
                      value={config.description}
                      onChange={(e) => setConfig({ ...config, description: e.target.value })}
                      placeholder="모니터 설명"
                      rows={3}
                    />
                  </FormControl>

                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">활성화</FormLabel>
                    <Switch
                      isChecked={config.enabled}
                      onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                      colorScheme="green"
                    />
                  </FormControl>
                </VStack>
              </TabPanel>

              {/* API 설정 */}
              <TabPanel>
                <ApiEndpointEditor
                  config={config.api}
                  onChange={(apiConfig) => setConfig({ ...config, api: apiConfig })}
                />
              </TabPanel>

              {/* 스케줄 */}
              <TabPanel>
                <ScheduleEditor
                  config={config.schedule}
                  onChange={(scheduleConfig) => setConfig({ ...config, schedule: scheduleConfig })}
                />
              </TabPanel>

              {/* 웹훅 */}
              <TabPanel>
                <WebhookEditor
                  config={config.webhook}
                  onChange={(webhookConfig) => setConfig({ ...config, webhook: webhookConfig })}
                />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            <Button
              leftIcon={<FiX />}
              onClick={onClose}
              variant="ghost"
            >
              취소
            </Button>
            <Button
              leftIcon={<FiSave />}
              colorScheme="blue"
              onClick={handleSave}
              isLoading={isSaving}
              loadingText="저장 중"
            >
              저장
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default MonitorConfigPanel
