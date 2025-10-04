import React, { useState, useEffect, useRef } from 'react'
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
} from '@chakra-ui/react'
import { 
  MdRefresh, 
  MdDownload, 
  MdClear, 
  MdPause, 
  MdPlayArrow,
  MdVerticalAlignBottom
} from 'react-icons/md'
import { LogEntry } from '../../types'
import { apiService } from '../../services/api'

interface ServiceLogViewerProps {
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
      return { color: 'yellow', text: 'WARN' }
    case 'ERROR':
      return { color: 'red', text: 'ERROR' }
    default:
      return { color: 'gray', text: level }
  }
}

const formatTimestamp = (timestamp: string) => {
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return timestamp
  }
}

const ServiceLogViewer: React.FC<ServiceLogViewerProps> = ({
  isOpen,
  onClose,
  serviceId,
  serviceName
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [logLevel, setLogLevel] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [autoScroll, setAutoScroll] = useState(true)
  const [isPaused, setIsPaused] = useState(false)
  const [maxLines, setMaxLines] = useState(1000)
  
  const logContainerRef = useRef<HTMLDivElement>(null)
  const toast = useToast()

  // 로그 필터링
  const filteredLogs = logs.filter(log => {
    const levelMatch = logLevel === 'all' || log.level === logLevel
    const searchMatch = !searchQuery || 
      log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.service.toLowerCase().includes(searchQuery.toLowerCase())
    const serviceMatch = log.service === serviceId || log.service.includes(serviceId)
    
    return levelMatch && searchMatch && serviceMatch
  }).slice(-maxLines)

  // 로그 데이터 로드
  const loadLogs = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiService.getLogs({
        sources: serviceId,
        limit: maxLines.toString(),
        page: '1'
      })
      
      setLogs(response.logs || [])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '로그를 불러오는데 실패했습니다'
      setError(errorMessage)
      toast({
        title: '로그 로드 실패',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  // 자동 스크롤
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [filteredLogs, autoScroll])

  // 실시간 로그 업데이트 (폴링)
  useEffect(() => {
    if (!isOpen || isPaused) return

    const interval = setInterval(() => {
      loadLogs()
    }, 5000) // 5초마다 업데이트

    return () => clearInterval(interval)
  }, [isOpen, isPaused, serviceId, maxLines])

  // 모달이 열릴 때 초기 로드
  useEffect(() => {
    if (isOpen) {
      loadLogs()
    }
  }, [isOpen, serviceId])

  const handleRefresh = () => {
    loadLogs()
  }

  const handleClear = () => {
    setLogs([])
    toast({
      title: '로그 지움',
      description: '화면의 로그를 지웠습니다.',
      status: 'info',
      duration: 2000,
      isClosable: true,
    })
  }

  const handleExport = async () => {
    try {
      const blob = await apiService.exportLogs({
        logs: filteredLogs,
        format: 'txt',
        include_metadata: true,
        custom_filename: `${serviceId}_logs_${new Date().toISOString().split('T')[0]}`
      })
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${serviceId}_logs.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast({
        title: '로그 내보내기 완료',
        description: '로그 파일이 다운로드되었습니다.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (err) {
      toast({
        title: '로그 내보내기 실패',
        description: err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

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
          <HStack justify="space-between">
            <Text>{serviceName} 로그</Text>
            <HStack spacing={2}>
              <Badge colorScheme={isPaused ? 'red' : 'green'} variant="subtle">
                {isPaused ? '일시정지' : '실시간'}
              </Badge>
              <Badge variant="outline">
                {filteredLogs.length}개 항목
              </Badge>
            </HStack>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody pb={6}>
          <VStack align="stretch" spacing={4} h="70vh">
            {/* 제어 패널 */}
            <HStack spacing={4} wrap="wrap">
              <HStack spacing={2}>
                <Text fontSize="sm" fontWeight="medium">레벨:</Text>
                <Select 
                  size="sm" 
                  value={logLevel} 
                  onChange={(e) => setLogLevel(e.target.value)}
                  w="120px"
                >
                  <option value="all">전체</option>
                  <option value="DEBUG">DEBUG</option>
                  <option value="INFO">INFO</option>
                  <option value="WARN">WARN</option>
                  <option value="ERROR">ERROR</option>
                </Select>
              </HStack>

              <HStack spacing={2}>
                <Text fontSize="sm" fontWeight="medium">검색:</Text>
                <Input
                  size="sm"
                  placeholder="메시지 검색..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  w="200px"
                />
              </HStack>

              <HStack spacing={2}>
                <Text fontSize="sm" fontWeight="medium">최대 라인:</Text>
                <Select 
                  size="sm" 
                  value={maxLines} 
                  onChange={(e) => setMaxLines(Number(e.target.value))}
                  w="100px"
                >
                  <option value={100}>100</option>
                  <option value={500}>500</option>
                  <option value={1000}>1000</option>
                  <option value={5000}>5000</option>
                </Select>
              </HStack>

              <FormControl display="flex" alignItems="center" w="auto">
                <FormLabel htmlFor="auto-scroll" mb="0" fontSize="sm">
                  자동 스크롤
                </FormLabel>
                <Switch
                  id="auto-scroll"
                  size="sm"
                  isChecked={autoScroll}
                  onChange={(e) => setAutoScroll(e.target.checked)}
                />
              </FormControl>
            </HStack>

            {/* 액션 버튼들 */}
            <HStack spacing={2}>
              <Button
                size="sm"
                leftIcon={<MdRefresh />}
                onClick={handleRefresh}
                isLoading={isLoading}
                loadingText="새로고침"
              >
                새로고침
              </Button>

              <Button
                size="sm"
                leftIcon={isPaused ? <MdPlayArrow /> : <MdPause />}
                onClick={() => setIsPaused(!isPaused)}
                colorScheme={isPaused ? 'green' : 'orange'}
              >
                {isPaused ? '재개' : '일시정지'}
              </Button>

              <Button
                size="sm"
                leftIcon={<MdClear />}
                onClick={handleClear}
                variant="outline"
              >
                화면 지우기
              </Button>

              <Button
                size="sm"
                leftIcon={<MdDownload />}
                onClick={handleExport}
                variant="outline"
              >
                내보내기
              </Button>

              <Tooltip label="맨 아래로 스크롤">
                <IconButton
                  size="sm"
                  aria-label="맨 아래로"
                  icon={<MdVerticalAlignBottom />}
                  onClick={scrollToBottom}
                  variant="outline"
                />
              </Tooltip>
            </HStack>

            <Divider />

            {/* 로그 내용 */}
            <Box
              ref={logContainerRef}
              flex="1"
              overflowY="auto"
              bg="gray.50"
              _dark={{ bg: 'gray.800' }}
              p={3}
              borderRadius="md"
              fontFamily="mono"
              fontSize="sm"
            >
              {isLoading && logs.length === 0 ? (
                <VStack spacing={3} py={8}>
                  <Spinner />
                  <Text>로그를 불러오는 중...</Text>
                </VStack>
              ) : error ? (
                <Alert status="error">
                  <AlertIcon />
                  {error}
                </Alert>
              ) : filteredLogs.length === 0 ? (
                <VStack spacing={3} py={8}>
                  <Text color="gray.500">표시할 로그가 없습니다.</Text>
                  {searchQuery && (
                    <Text fontSize="xs" color="gray.400">
                      검색어: "{searchQuery}"
                    </Text>
                  )}
                </VStack>
              ) : (
                <VStack align="stretch" spacing={1}>
                  {filteredLogs.map((log, index) => {
                    const levelInfo = formatLogLevel(log.level)
                    return (
                      <HStack
                        key={`${log.id}-${index}`}
                        align="start"
                        spacing={3}
                        p={2}
                        borderRadius="sm"
                        _hover={{ bg: 'gray.100', _dark: { bg: 'gray.700' } }}
                      >
                        <Text
                          fontSize="xs"
                          color="gray.500"
                          minW="80px"
                          fontFamily="mono"
                        >
                          {formatTimestamp(log.timestamp)}
                        </Text>
                        <Badge
                          colorScheme={levelInfo.color}
                          variant="subtle"
                          fontSize="xs"
                          minW="50px"
                          textAlign="center"
                        >
                          {levelInfo.text}
                        </Badge>
                        <Text
                          flex="1"
                          whiteSpace="pre-wrap"
                          wordBreak="break-word"
                        >
                          {log.message}
                        </Text>
                      </HStack>
                    )
                  })}
                </VStack>
              )}
            </Box>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}

export default ServiceLogViewer