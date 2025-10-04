import React, { useState, useEffect } from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  Alert,
  AlertIcon,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Code,
  Box,
} from '@chakra-ui/react'
import { FiActivity, FiCheck, FiX, FiRefreshCw, FiEye } from 'react-icons/fi'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface ApiConnection {
  name: string
  url: string
  status: string
  last_check: string
  response_time_ms: number
  error_message?: string
}

interface WebhookLog {
  timestamp: string
  webhook_url: string
  news_type: string
  status: string
  response_code?: number
  error_message?: string
  payload_preview?: string
}

interface ConfigInfo {
  key: string
  value: string
  is_sensitive: boolean
  description?: string
}

interface MonitorExecutionLog {
  id: string
  monitor_name: string
  timestamp: string
  duration_ms: number
  status: string
  api_endpoint: string
  api_method: string
  input_params: Record<string, any>
  output_status_code: number
  output_data: Record<string, any>
  parsed_data?: Record<string, any>
  webhook_sent: boolean
  error_message?: string
}

const DiagnosticsPanel: React.FC = () => {
  const [apiConnections, setApiConnections] = useState<ApiConnection[]>([])
  const [webhookLogs, setWebhookLogs] = useState<WebhookLog[]>([])
  const [configInfo, setConfigInfo] = useState<ConfigInfo[]>([])
  const [monitorLogs, setMonitorLogs] = useState<MonitorExecutionLog[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const toast = useToast()

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [connectionsRes, logsRes, configRes, monitorLogsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/diagnostics/api-connections`),
        axios.get(`${API_BASE}/api/diagnostics/webhook-logs?limit=20`),
        axios.get(`${API_BASE}/api/diagnostics/config-info`),
        axios.get(`${API_BASE}/api/monitor-logs/executions?limit=20`),
      ])

      setApiConnections(connectionsRes.data)
      setWebhookLogs(logsRes.data)
      setConfigInfo(configRes.data)
      setMonitorLogs(monitorLogsRes.data)
    } catch (error) {
      console.error('진단 데이터 로드 실패:', error)
      toast({
        title: '데이터 로드 실패',
        description: '진단 정보를 불러올 수 없습니다.',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const testWebhook = async () => {
    try {
      const res = await axios.post(`${API_BASE}/api/diagnostics/test-webhook`)
      toast({
        title: '웹훅 테스트 성공',
        description: res.data.message,
        status: 'success',
        duration: 3000,
      })
      loadData() // 로그 새로고침
    } catch (error) {
      toast({
        title: '웹훅 테스트 실패',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const executeMonitor = async (monitorName: string) => {
    try {
      const res = await axios.post(`${API_BASE}/api/monitor-logs/execute/${monitorName}`)
      toast({
        title: '모니터 실행 완료',
        description: res.data.message,
        status: 'success',
        duration: 3000,
      })
      loadData() // 로그 새로고침
    } catch (error) {
      toast({
        title: '모니터 실행 실패',
        status: 'error',
        duration: 3000,
      })
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <VStack py={8}>
            <Spinner size="lg" />
            <Text>진단 정보 로드 중...</Text>
          </VStack>
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">🔍 시스템 진단</Heading>
          <Button
            size="sm"
            leftIcon={<FiRefreshCw />}
            onClick={loadData}
            variant="outline"
          >
            새로고침
          </Button>
        </HStack>
      </CardHeader>
      <CardBody>
        <Tabs colorScheme="posco">
          <TabList>
            <Tab>API 연결 상태</Tab>
            <Tab>모니터 실행 로그</Tab>
            <Tab>웹훅 로그</Tab>
            <Tab>설정 정보</Tab>
          </TabList>

          <TabPanels>
            {/* API 연결 상태 */}
            <TabPanel>
              <VStack align="stretch" spacing={4}>
                {apiConnections.map((conn, idx) => (
                  <Box
                    key={idx}
                    p={4}
                    borderWidth="1px"
                    borderRadius="md"
                    bg={conn.status === 'connected' ? 'green.50' : 'red.50'}
                    _dark={{
                      bg: conn.status === 'connected' ? 'green.900' : 'red.900',
                    }}
                  >
                    <HStack justify="space-between" mb={2}>
                      <HStack>
                        {conn.status === 'connected' ? (
                          <FiCheck color="green" />
                        ) : (
                          <FiX color="red" />
                        )}
                        <Text fontWeight="bold">{conn.name}</Text>
                      </HStack>
                      <Badge
                        colorScheme={conn.status === 'connected' ? 'green' : 'red'}
                      >
                        {conn.status}
                      </Badge>
                    </HStack>
                    <VStack align="start" spacing={1} fontSize="sm">
                      <Text>
                        <strong>URL:</strong> <Code>{conn.url}</Code>
                      </Text>
                      <Text>
                        <strong>응답 시간:</strong> {conn.response_time_ms}ms
                      </Text>
                      <Text>
                        <strong>마지막 체크:</strong>{' '}
                        {new Date(conn.last_check).toLocaleString('ko-KR')}
                      </Text>
                      {conn.error_message && (
                        <Alert status="error" size="sm">
                          <AlertIcon />
                          {conn.error_message}
                        </Alert>
                      )}
                    </VStack>
                  </Box>
                ))}
              </VStack>
            </TabPanel>

            {/* 모니터 실행 로그 */}
            <TabPanel>
              <VStack align="stretch" spacing={4}>
                <HStack justify="space-between">
                  <Text fontSize="sm" color="gray.600">
                    최근 20개 모니터 실행 기록 (Input/Output 포함)
                  </Text>
                  <HStack>
                    <Button
                      size="sm"
                      colorScheme="blue"
                      onClick={() => executeMonitor('kospi-close')}
                    >
                      코스피 실행
                    </Button>
                    <Button
                      size="sm"
                      colorScheme="green"
                      onClick={() => executeMonitor('newyork-market-watch')}
                    >
                      뉴욕증시 실행
                    </Button>
                    <Button
                      size="sm"
                      colorScheme="purple"
                      onClick={() => executeMonitor('exchange-rate')}
                    >
                      환율 실행
                    </Button>
                  </HStack>
                </HStack>

                {monitorLogs.length === 0 ? (
                  <Alert status="info">
                    <AlertIcon />
                    아직 모니터 실행 기록이 없습니다.
                  </Alert>
                ) : (
                  <VStack align="stretch" spacing={3}>
                    {monitorLogs.map((log, idx) => (
                      <Box
                        key={idx}
                        p={4}
                        borderWidth="1px"
                        borderRadius="md"
                        bg={log.status === 'success' ? 'green.50' : 'red.50'}
                        _dark={{
                          bg: log.status === 'success' ? 'green.900' : 'red.900',
                        }}
                      >
                        <HStack justify="space-between" mb={2}>
                          <HStack>
                            <Badge colorScheme="purple">{log.monitor_name}</Badge>
                            <Badge
                              colorScheme={log.status === 'success' ? 'green' : 'red'}
                            >
                              {log.status}
                            </Badge>
                            <Text fontSize="sm">
                              {new Date(log.timestamp).toLocaleString('ko-KR')}
                            </Text>
                          </HStack>
                          <Text fontSize="sm" color="gray.600">
                            {log.duration_ms}ms
                          </Text>
                        </HStack>

                        <VStack align="start" spacing={2} fontSize="sm">
                          {/* API 호출 정보 */}
                          <Box w="full">
                            <Text fontWeight="bold" mb={1}>
                              📡 API 호출
                            </Text>
                            <Code fontSize="xs" p={2} borderRadius="md" w="full">
                              {log.api_method} {log.api_endpoint}
                            </Code>
                          </Box>

                          {/* Input 파라미터 */}
                          <Box w="full">
                            <Text fontWeight="bold" mb={1}>
                              📥 Input 파라미터
                            </Text>
                            <Code fontSize="xs" p={2} borderRadius="md" w="full" display="block" whiteSpace="pre-wrap">
                              {JSON.stringify(log.input_params, null, 2)}
                            </Code>
                          </Box>

                          {/* Output 데이터 */}
                          <Box w="full">
                            <Text fontWeight="bold" mb={1}>
                              📤 Output 데이터 (HTTP {log.output_status_code})
                            </Text>
                            <Code fontSize="xs" p={2} borderRadius="md" w="full" display="block" whiteSpace="pre-wrap" maxH="200px" overflowY="auto">
                              {JSON.stringify(log.output_data, null, 2)}
                            </Code>
                          </Box>

                          {/* 파싱 결과 */}
                          {log.parsed_data && (
                            <Box w="full">
                              <Text fontWeight="bold" mb={1}>
                                🔍 파싱 결과
                              </Text>
                              <Code fontSize="xs" p={2} borderRadius="md" w="full" display="block" whiteSpace="pre-wrap">
                                {JSON.stringify(log.parsed_data, null, 2)}
                              </Code>
                            </Box>
                          )}

                          {/* 웹훅 발송 여부 */}
                          <HStack>
                            <Text fontWeight="bold">📨 웹훅 발송:</Text>
                            <Badge colorScheme={log.webhook_sent ? 'green' : 'gray'}>
                              {log.webhook_sent ? '발송 완료' : '미발송'}
                            </Badge>
                          </HStack>

                          {/* 에러 메시지 */}
                          {log.error_message && (
                            <Alert status="error" size="sm">
                              <AlertIcon />
                              {log.error_message}
                            </Alert>
                          )}
                        </VStack>
                      </Box>
                    ))}
                  </VStack>
                )}
              </VStack>
            </TabPanel>

            {/* 웹훅 로그 */}
            <TabPanel>
              <VStack align="stretch" spacing={4}>
                <HStack justify="space-between">
                  <Text fontSize="sm" color="gray.600">
                    최근 20개 웹훅 발송 기록
                  </Text>
                  <Button size="sm" onClick={testWebhook} colorScheme="blue">
                    테스트 발송
                  </Button>
                </HStack>

                {webhookLogs.length === 0 ? (
                  <Alert status="info">
                    <AlertIcon />
                    아직 웹훅 발송 기록이 없습니다.
                  </Alert>
                ) : (
                  <Table size="sm" variant="simple">
                    <Thead>
                      <Tr>
                        <Th>시간</Th>
                        <Th>뉴스 타입</Th>
                        <Th>상태</Th>
                        <Th>응답 코드</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {webhookLogs.map((log, idx) => (
                        <Tr key={idx}>
                          <Td>
                            {new Date(log.timestamp).toLocaleString('ko-KR')}
                          </Td>
                          <Td>
                            <Badge>{log.news_type}</Badge>
                          </Td>
                          <Td>
                            <Badge
                              colorScheme={
                                log.status === 'success' ? 'green' : 'red'
                              }
                            >
                              {log.status}
                            </Badge>
                          </Td>
                          <Td>{log.response_code || 'N/A'}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                )}
              </VStack>
            </TabPanel>

            {/* 설정 정보 */}
            <TabPanel>
              <VStack align="stretch" spacing={3}>
                {configInfo.map((config, idx) => (
                  <Box
                    key={idx}
                    p={3}
                    borderWidth="1px"
                    borderRadius="md"
                    bg="gray.50"
                    _dark={{ bg: 'gray.800' }}
                  >
                    <HStack justify="space-between" mb={1}>
                      <Text fontWeight="bold">{config.key}</Text>
                      {config.is_sensitive && (
                        <Badge colorScheme="orange">민감정보</Badge>
                      )}
                    </HStack>
                    <Code fontSize="sm" p={2} borderRadius="md" w="full">
                      {config.value}
                    </Code>
                    {config.description && (
                      <Text fontSize="xs" color="gray.600" mt={1}>
                        {config.description}
                      </Text>
                    )}
                  </Box>
                ))}
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </CardBody>
    </Card>
  )
}

export default DiagnosticsPanel
