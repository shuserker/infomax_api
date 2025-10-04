import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Card,
  CardBody,
  Badge,
  Spinner,
  useToast,
  useDisclosure,
} from '@chakra-ui/react'
import { FiPlus, FiRefreshCw } from 'react-icons/fi'
import axios from 'axios'
import MonitorConfigPanel from '../components/ConfigManager/MonitorConfigPanel'

const API_BASE = 'http://localhost:8000'

interface MonitorSummary {
  name: string
  display_name: string
  enabled: boolean
  description: string
  last_updated: string
}

const ConfigManager: React.FC = () => {
  const [monitors, setMonitors] = useState<MonitorSummary[]>([])
  const [selectedMonitor, setSelectedMonitor] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()

  const loadMonitors = async () => {
    setIsLoading(true)
    try {
      const res = await axios.get(`${API_BASE}/api/config/monitors`)
      setMonitors(res.data)
    } catch (error) {
      console.error('모니터 목록 로드 실패:', error)
      toast({
        title: '모니터 목록 로드 실패',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadMonitors()
  }, [])

  const handleEdit = (monitorName: string) => {
    setSelectedMonitor(monitorName)
    onOpen()
  }

  const handleClose = () => {
    setSelectedMonitor(null)
    onClose()
    loadMonitors()
  }

  if (isLoading) {
    return (
      <Box className="fade-in" display="flex" justifyContent="center" alignItems="center" minH="400px">
        <VStack spacing={4}>
          <Spinner size="xl" color="posco.500" />
          <Text>모니터 설정을 불러오는 중...</Text>
        </VStack>
      </Box>
    )
  }

  return (
    <Box className="fade-in" data-testid="config-manager-page">
      <VStack spacing={6} align="stretch">
        {/* 페이지 헤더 */}
        <HStack justify="space-between">
          <Box>
            <Heading size="lg" mb={2}>
              ⚙️ API 설정 관리
            </Heading>
            <Text color="gray.600" _dark={{ color: 'gray.400' }}>
              각 모니터의 API 호출 설정, 스케줄, 웹훅을 관리합니다
            </Text>
          </Box>
          <HStack>
            <Button
              leftIcon={<FiRefreshCw />}
              onClick={loadMonitors}
              variant="outline"
            >
              새로고침
            </Button>
            <Button
              leftIcon={<FiPlus />}
              colorScheme="blue"
              onClick={() => {
                setSelectedMonitor('new')
                onOpen()
              }}
            >
              새 모니터 추가
            </Button>
          </HStack>
        </HStack>

        {/* 모니터 목록 */}
        <VStack spacing={4} align="stretch">
          {monitors.length === 0 ? (
            <Card>
              <CardBody>
                <Text textAlign="center" color="gray.500">
                  등록된 모니터가 없습니다. 새 모니터를 추가하세요.
                </Text>
              </CardBody>
            </Card>
          ) : (
            monitors.map((monitor) => (
              <Card
                key={monitor.name}
                _hover={{ shadow: 'md', transform: 'translateY(-2px)' }}
                transition="all 0.2s"
                cursor="pointer"
                onClick={() => handleEdit(monitor.name)}
              >
                <CardBody>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={2} flex="1">
                      <HStack>
                        <Heading size="md">{monitor.display_name}</Heading>
                        <Badge
                          colorScheme={monitor.enabled ? 'green' : 'gray'}
                          fontSize="sm"
                        >
                          {monitor.enabled ? '활성화' : '비활성화'}
                        </Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        {monitor.description}
                      </Text>
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>ID: {monitor.name}</Text>
                        {monitor.last_updated && (
                          <Text>
                            마지막 수정: {new Date(monitor.last_updated).toLocaleString('ko-KR')}
                          </Text>
                        )}
                      </HStack>
                    </VStack>
                    <Button
                      colorScheme="blue"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleEdit(monitor.name)
                      }}
                    >
                      편집
                    </Button>
                  </HStack>
                </CardBody>
              </Card>
            ))
          )}
        </VStack>
      </VStack>

      {/* 설정 편집 모달 */}
      {selectedMonitor && (
        <MonitorConfigPanel
          isOpen={isOpen}
          onClose={handleClose}
          monitorName={selectedMonitor}
        />
      )}
    </Box>
  )
}

export default ConfigManager
