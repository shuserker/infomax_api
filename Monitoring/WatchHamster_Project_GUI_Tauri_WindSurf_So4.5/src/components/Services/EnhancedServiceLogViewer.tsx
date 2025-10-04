import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Box,
  Text,
  VStack,
  HStack,
  Button,
  Select,
  Input,
  Badge,
  Divider,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Switch,
  FormControl,
  FormLabel,
  IconButton,
  Tooltip,
  Flex,
  Spacer,
  Code,
  useColorModeValue,
} from '@chakra-ui/react'
import { 
  FiRefreshCw, 
  FiDownload, 
  FiTrash2, 
  FiPause, 
  FiPlay,
  FiArrowDown,
  FiSearch,
  FiFilter,
  FiClock
} from 'react-icons/fi'

interface LogEntry {
  id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
  message: string
  service: string
  source?: string
  metadata?: Record<string, any>
}

interface EnhancedServiceLogViewerProps {
  isOpen: boolean
  onClose: () => void
  serviceId: string
  serviceName: string
}

const formatLogLevel = (level: string) => {
  switch (level) {
    case 'DEBUG':
      return { color: 'gray', text: 'DEBUG' }
    case 'INFO':
      return { color: 'blue', text: 'INFO' }
    case 'WARN':
      return { color: 'orange', text: 'WARN' }
    case 'ERROR':
      return { color: 'red', text: 'ERROR' }
    case 'CRITICAL':
      return { color: 'red', text: 'CRIT' }
    default:
      return { color: 'gray', text: 'UNKNOWN' }
  }
}

const EnhancedServiceLogViewer: React.FC<EnhancedServiceLogViewerProps> = ({ 
  isOpen, 
  onClose, 
  serviceId, 
  serviceName 
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null)
  const [logLevel, setLogLevel] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [followTail, setFollowTail] = useState(true)
  const [maxLines, setMaxLines] = useState('1000')
  
  const logContainerRef = useRef<HTMLDivElement>(null)
  const toast = useToast()
  
  const bgColor = useColorModeValue('white', 'gray.800')
  const logBgColor = useColorModeValue('gray.50', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  // 로그 데이터 생성 (실제 환경에서는 API 호출)
  const generateMockLogs = useCallback((count: number = 50): LogEntry[] => {
    const levels: LogEntry['level'][] = ['DEBUG', 'INFO', 'WARN', 'ERROR']
    const messages = [
      'Service started successfully',
      'Processing request from client',
      'Database connection established',
      'API call completed',
      'Memory usage: 67%',
      'New webhook received',
      'Configuration updated',
      'Health check passed',
      'Error connecting to external API',
      'Retrying failed operation',
      'Cache cleared successfully',
      'User authentication successful',
      'Background task completed',
      'System resource warning',
      'Connection pool exhausted'
    ]
    
    return Array.from({ length: count }, (_, i) => ({
      id: `log-${Date.now()}-${i}`,
      timestamp: new Date(Date.now() - (count - i) * 1000).toISOString(),
      level: levels[Math.floor(Math.random() * levels.length)],
      message: messages[Math.floor(Math.random() * messages.length)] + ` (${i + 1})`,
      service: serviceId,
      source: `${serviceId}.main`,
      metadata: {
        thread: `thread-${Math.floor(Math.random() * 4) + 1}`,
        requestId: `req-${Math.random().toString(36).substr(2, 9)}`
      }
    }))
  }, [serviceId])

  // 로그 필터링
  const filterLogs = useCallback(() => {
    let filtered = logs

    // 레벨 필터링
    if (logLevel !== 'ALL') {
      filtered = filtered.filter(log => log.level === logLevel)
    }

    // 검색 쿼리 필터링
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(query) ||
        log.level.toLowerCase().includes(query) ||
        (log.source && log.source.toLowerCase().includes(query))
      )
    }

    setFilteredLogs(filtered)
  }, [logs, logLevel, searchQuery])

  // 로그 로드
  const loadLogs = useCallback(async () => {
    setLoading(true)
    try {
      // 실제 API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 500))
      const newLogs = generateMockLogs(parseInt(maxLines))
      setLogs(newLogs)
    } catch (error) {
      toast({
        title: '로그 로드 실패',
        description: '로그를 불러오는 중 오류가 발생했습니다.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }, [generateMockLogs, maxLines, toast])

  // 자동 새로고침
  useEffect(() => {
    if (autoRefresh && isOpen) {
      const interval = setInterval(loadLogs, 2000) // 2초마다 새로고침
      setRefreshInterval(interval)
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval)
        setRefreshInterval(null)
      }
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    }
  }, [autoRefresh, isOpen, loadLogs, refreshInterval])

  // 로그 필터링 적용
  useEffect(() => {
    filterLogs()
  }, [filterLogs])

  // 초기 로드
  useEffect(() => {
    if (isOpen) {
      loadLogs()
    }
  }, [isOpen, loadLogs])

  // 자동 스크롤
  useEffect(() => {
    if (followTail && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [filteredLogs, followTail])

  // 로그 다운로드
  const downloadLogs = () => {
    const logData = filteredLogs.map(log => 
      `[${log.timestamp}] [${log.level}] ${log.message}`
    ).join('\n')
    
    const blob = new Blob([logData], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${serviceId}-logs-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast({
      title: '로그 다운로드',
      description: '로그 파일이 다운로드되었습니다.',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  // 로그 지우기
  const clearLogs = () => {
    setLogs([])
    setFilteredLogs([])
    toast({
      title: '로그 삭제',
      description: '모든 로그가 삭제되었습니다.',
      status: 'info',
      duration: 2000,
      isClosable: true,
    })
  }

  // 하단으로 스크롤
  const scrollToBottom = () => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>
          <Flex align="center" justify="space-between">
            <VStack spacing={1} align="start">
              <Text fontWeight="bold">{serviceName} 로그 뷰어</Text>
              <HStack spacing={2}>
                <Badge colorScheme="blue" variant="subtle">
                  {filteredLogs.length}개 로그
                </Badge>
                {autoRefresh && (
                  <Badge colorScheme="green" variant="subtle">
                    실시간 업데이트
                  </Badge>
                )}
              </HStack>
            </VStack>
            <ModalCloseButton />
          </Flex>
        </ModalHeader>

        <ModalBody pb={6}>
          <VStack spacing={4} align="stretch">
            {/* 컨트롤 패널 */}
            <Box p={4} bg={logBgColor} borderRadius="md" border="1px solid" borderColor={borderColor}>
              <VStack spacing={4}>
                {/* 상단 컨트롤 */}
                <Flex w="full" gap={4} align="end" flexWrap="wrap">
                  <FormControl maxW="150px">
                    <FormLabel fontSize="sm">로그 레벨</FormLabel>
                    <Select size="sm" value={logLevel} onChange={(e) => setLogLevel(e.target.value)}>
                      <option value="ALL">전체</option>
                      <option value="DEBUG">DEBUG</option>
                      <option value="INFO">INFO</option>
                      <option value="WARN">WARN</option>
                      <option value="ERROR">ERROR</option>
                      <option value="CRITICAL">CRITICAL</option>
                    </Select>
                  </FormControl>

                  <FormControl maxW="120px">
                    <FormLabel fontSize="sm">최대 라인</FormLabel>
                    <Select size="sm" value={maxLines} onChange={(e) => setMaxLines(e.target.value)}>
                      <option value="100">100</option>
                      <option value="500">500</option>
                      <option value="1000">1000</option>
                      <option value="5000">5000</option>
                    </Select>
                  </FormControl>

                  <FormControl flex="1" minW="200px">
                    <FormLabel fontSize="sm">검색</FormLabel>
                    <Input
                      size="sm"
                      placeholder="로그 메시지 검색..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      leftElement={<FiSearch />}
                    />
                  </FormControl>
                </Flex>

                {/* 하단 컨트롤 */}
                <Flex w="full" justify="space-between" align="center" gap={4} flexWrap="wrap">
                  <HStack spacing={4}>
                    <FormControl display="flex" alignItems="center">
                      <FormLabel fontSize="sm" mb={0} mr={2}>자동 새로고침</FormLabel>
                      <Switch size="sm" isChecked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />
                    </FormControl>

                    <FormControl display="flex" alignItems="center">
                      <FormLabel fontSize="sm" mb={0} mr={2}>자동 스크롤</FormLabel>
                      <Switch size="sm" isChecked={followTail} onChange={(e) => setFollowTail(e.target.checked)} />
                    </FormControl>
                  </HStack>

                  <HStack spacing={2}>
                    <Tooltip label="새로고침">
                      <IconButton
                        aria-label="새로고침"
                        icon={<FiRefreshCw />}
                        size="sm"
                        onClick={loadLogs}
                        isLoading={loading}
                      />
                    </Tooltip>

                    <Tooltip label={autoRefresh ? "자동 새로고침 중지" : "자동 새로고침 시작"}>
                      <IconButton
                        aria-label="자동 새로고침 토글"
                        icon={autoRefresh ? <FiPause /> : <FiPlay />}
                        size="sm"
                        onClick={() => setAutoRefresh(!autoRefresh)}
                        colorScheme={autoRefresh ? "orange" : "green"}
                      />
                    </Tooltip>

                    <Tooltip label="로그 지우기">
                      <IconButton
                        aria-label="로그 지우기"
                        icon={<FiTrash2 />}
                        size="sm"
                        onClick={clearLogs}
                        colorScheme="red"
                        variant="outline"
                      />
                    </Tooltip>

                    <Tooltip label="로그 다운로드">
                      <IconButton
                        aria-label="로그 다운로드"
                        icon={<FiDownload />}
                        size="sm"
                        onClick={downloadLogs}
                        colorScheme="blue"
                        variant="outline"
                      />
                    </Tooltip>

                    <Tooltip label="하단으로 스크롤">
                      <IconButton
                        aria-label="하단으로 스크롤"
                        icon={<FiArrowDown />}
                        size="sm"
                        onClick={scrollToBottom}
                      />
                    </Tooltip>
                  </HStack>
                </Flex>
              </VStack>
            </Box>

            {/* 로그 컨테이너 */}
            <Box 
              ref={logContainerRef}
              h="400px" 
              bg={logBgColor}
              border="1px solid" 
              borderColor={borderColor}
              borderRadius="md"
              overflow="auto"
              fontFamily="mono"
              fontSize="sm"
              position="relative"
            >
              {loading && (
                <Flex justify="center" align="center" h="full">
                  <VStack spacing={2}>
                    <Spinner />
                    <Text fontSize="sm" color="gray.500">로그를 불러오는 중...</Text>
                  </VStack>
                </Flex>
              )}

              {!loading && filteredLogs.length === 0 && (
                <Flex justify="center" align="center" h="full">
                  <VStack spacing={2}>
                    <FiSearch size={32} color="gray" />
                    <Text fontSize="sm" color="gray.500">
                      {searchQuery ? '검색 결과가 없습니다' : '로그가 없습니다'}
                    </Text>
                  </VStack>
                </Flex>
              )}

              {!loading && filteredLogs.length > 0 && (
                <VStack spacing={0} align="stretch" p={2}>
                  {filteredLogs.map((log, index) => {
                    const levelInfo = formatLogLevel(log.level)
                    return (
                      <HStack 
                        key={log.id}
                        spacing={3} 
                        py={1} 
                        px={2}
                        borderRadius="sm"
                        _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
                        fontSize="xs"
                        align="start"
                      >
                        <Text color="gray.500" minW="140px" fontFamily="mono">
                          {new Date(log.timestamp).toLocaleTimeString('ko-KR')}
                        </Text>
                        <Badge 
                          colorScheme={levelInfo.color} 
                          size="sm" 
                          minW="50px"
                          textAlign="center"
                        >
                          {levelInfo.text}
                        </Badge>
                        <Text flex="1" color={levelInfo.color === 'red' ? 'red.500' : 'inherit'}>
                          {log.message}
                        </Text>
                        {log.source && (
                          <Text color="gray.400" fontSize="xs" minW="80px">
                            [{log.source}]
                          </Text>
                        )}
                      </HStack>
                    )
                  })}
                </VStack>
              )}
            </Box>

            {/* 통계 정보 */}
            <HStack spacing={6} justify="center" p={2} bg={logBgColor} borderRadius="md">
              <VStack spacing={1}>
                <Text fontSize="sm" fontWeight="semibold" color="blue.600">
                  {logs.filter(l => l.level === 'INFO').length}
                </Text>
                <Text fontSize="xs" color="gray.500">INFO</Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="sm" fontWeight="semibold" color="orange.600">
                  {logs.filter(l => l.level === 'WARN').length}
                </Text>
                <Text fontSize="xs" color="gray.500">WARN</Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="sm" fontWeight="semibold" color="red.600">
                  {logs.filter(l => l.level === 'ERROR').length}
                </Text>
                <Text fontSize="xs" color="gray.500">ERROR</Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="sm" fontWeight="semibold" color="gray.600">
                  {logs.filter(l => l.level === 'DEBUG').length}
                </Text>
                <Text fontSize="xs" color="gray.500">DEBUG</Text>
              </VStack>
            </HStack>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}

export default EnhancedServiceLogViewer
