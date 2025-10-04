import React, { useState, useCallback, useEffect } from 'react'
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Button,
  Badge,
  Divider,
  Switch,
  FormControl,
  FormLabel,
  Alert,
  AlertIcon,
  Card,
  CardBody,
  Flex,
  Spacer,
  useToast,
  Spinner,
} from '@chakra-ui/react'
import { FiRefreshCw, FiSettings, FiDownload } from 'react-icons/fi'
import { useQuery } from '@tanstack/react-query'
import EnhancedLogViewer from '../components/Logs/EnhancedLogViewer'
import { LogEntry } from '../types'
import { apiService } from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'

const Logs: React.FC = () => {
  const [isStreamMode, setIsStreamMode] = useState(false)
  const [streamLogs, setStreamLogs] = useState<LogEntry[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const toast = useToast()

  // 정적 로그 데이터 조회
  const {
    data: staticLogs = [],
    isLoading: isStaticLoading,
    error: staticError,
    refetch: refreshStaticLogs
  } = useQuery({
    queryKey: ['logs'],
    queryFn: async () => {
      const response = await apiService.getLogs({
        limit: '1000',
        page: '1'
      })
      return response.logs || []
    },
    refetchInterval: isStreamMode ? false : 30000, // 스트림 모드가 아닐 때만 자동 새로고침
    retry: 3,
    retryDelay: 1000,
  })

  // WebSocket을 통한 실시간 로그 스트림
  const { isConnected: wsConnected } = useWebSocket({
    enabled: isStreamMode,
    onMessage: useCallback((message) => {
      if (message.type === 'log_update' && message.data) {
        const newLog: LogEntry = message.data
        setStreamLogs(prev => [...prev.slice(-999), newLog]) // 최대 1000개 유지
      }
    }, [])
  })

  useEffect(() => {
    setIsConnected(wsConnected)
  }, [wsConnected])

  const handleModeToggle = useCallback((checked: boolean) => {
    setIsStreamMode(checked)
    if (checked) {
      setStreamLogs([])
      toast({
        title: '실시간 모드 활성화',
        description: '실시간 로그 스트리밍이 시작되었습니다.',
        status: 'info',
        duration: 3000,
        isClosable: true,
      })
    } else {
      toast({
        title: '정적 모드 활성화',
        description: '정적 로그 뷰어로 전환되었습니다.',
        status: 'info',
        duration: 3000,
        isClosable: true,
      })
    }
  }, [toast])

  const handleRefresh = useCallback(async () => {
    if (isStreamMode) {
      setStreamLogs([])
    } else {
      await refreshStaticLogs()
    }
    toast({
      title: '로그 새로고침',
      description: '로그 데이터를 업데이트했습니다.',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }, [isStreamMode, refreshStaticLogs, toast])

  const handleClear = useCallback(() => {
    if (isStreamMode) {
      setStreamLogs([])
    } else {
      // 정적 모드에서는 화면만 지우기 (실제 로그는 유지)
    }
    toast({
      title: '로그 지움',
      description: '화면의 로그를 지웠습니다.',
      status: 'info',
      duration: 2000,
      isClosable: true,
    })
  }, [isStreamMode, toast])

  const currentLogs = isStreamMode ? streamLogs : staticLogs
  const currentError = isStreamMode ? null : staticError
  const isLoading = !isStreamMode && isStaticLoading

  // 로그 통계 계산
  const logStats = React.useMemo(() => {
    const stats = {
      total: currentLogs.length,
      error: 0,
      warn: 0,
      info: 0,
      debug: 0,
      critical: 0,
    }

    currentLogs.forEach(log => {
      switch (log.level) {
        case 'ERROR':
          stats.error++
          break
        case 'WARN':
          stats.warn++
          break
        case 'INFO':
          stats.info++
          break
        case 'DEBUG':
          stats.debug++
          break
        case 'CRITICAL':
          stats.critical++
          break
      }
    })

    return stats
  }, [currentLogs])

  return (
    <Box className="fade-in">
      <VStack spacing={6} align="stretch">
        {/* 페이지 헤더 */}
        <Flex align="center" mb={6}>
          <Box>
            <Heading size="lg" mb={2}>로그 뷰어</Heading>
            <HStack spacing={4} wrap="wrap">
              <Text color="gray.600" _dark={{ color: 'gray.400' }}>
                시스템 로그를 실시간으로 모니터링하고 관리합니다
              </Text>
              <HStack spacing={2}>
                <Badge colorScheme="blue" variant="subtle">
                  전체 {logStats.total}개
                </Badge>
                {logStats.error > 0 && (
                  <Badge colorScheme="red" variant="subtle">
                    오류 {logStats.error}개
                  </Badge>
                )}
                {logStats.warn > 0 && (
                  <Badge colorScheme="yellow" variant="subtle">
                    경고 {logStats.warn}개
                  </Badge>
                )}
              </HStack>
            </HStack>
          </Box>
          <Spacer />
          <Button
            leftIcon={<FiRefreshCw />}
            onClick={handleRefresh}
            isLoading={isLoading}
            loadingText="새로고침 중"
            size="sm"
            variant="outline"
          >
            새로고침
          </Button>
        </Flex>

        {/* 모드 전환 및 상태 */}
        <Card>
          <CardBody>
            <Flex align="center" justify="space-between">
              <HStack spacing={6}>
                <FormControl display="flex" alignItems="center">
                  <FormLabel htmlFor="stream-mode" mb="0" fontSize="sm">
                    실시간 스트리밍
                  </FormLabel>
                  <Switch
                    id="stream-mode"
                    isChecked={isStreamMode}
                    onChange={(e) => handleModeToggle(e.target.checked)}
                  />
                </FormControl>
                
                {isStreamMode && (
                  <HStack spacing={2}>
                    <Badge colorScheme={isConnected ? 'green' : 'red'} variant="subtle">
                      {isConnected ? '연결됨' : '연결 끊김'}
                    </Badge>
                    <Text fontSize="sm" color="gray.600">
                      WebSocket 연결 상태
                    </Text>
                  </HStack>
                )}

                {!isStreamMode && (
                  <HStack spacing={2}>
                    <Badge colorScheme="blue" variant="subtle">
                      정적 모드
                    </Badge>
                    <Text fontSize="sm" color="gray.600">
                      30초마다 자동 새로고침
                    </Text>
                  </HStack>
                )}
              </HStack>

              <HStack spacing={2}>
                <Text fontSize="sm" color="gray.500">
                  마지막 업데이트: {new Date().toLocaleTimeString('ko-KR')}
                </Text>
              </HStack>
            </Flex>
          </CardBody>
        </Card>

        {/* 오류 표시 */}
        {currentError && (
          <Alert status="error">
            <AlertIcon />
            <Box>
              <Text fontWeight="bold">로그 로드 실패</Text>
              <Text fontSize="sm">{currentError.message}</Text>
            </Box>
          </Alert>
        )}

        {/* 로딩 상태 */}
        {isLoading && currentLogs.length === 0 && (
          <VStack spacing={4} py={8}>
            <Spinner size="lg" />
            <Text>로그를 불러오는 중...</Text>
          </VStack>
        )}

        {/* 로그 뷰어 */}
        <Card>
          <CardBody p={4}>
            <EnhancedLogViewer
              logs={currentLogs}
              isLoading={isLoading}
              isRealtime={isStreamMode}
              onRefresh={handleRefresh}
              onClear={handleClear}
              height={600}
            />
          </CardBody>
        </Card>

        {/* 로그 통계 */}
        <Card>
          <CardBody>
            <Text fontWeight="bold" mb={4}>로그 통계</Text>
            <HStack spacing={8} flexWrap="wrap" justify="center">
              <VStack>
                <Text fontSize="3xl" fontWeight="bold" color="red.700">
                  {logStats.critical}
                </Text>
                <Text fontSize="sm" color="gray.600">심각</Text>
              </VStack>
              <Divider orientation="vertical" h="60px" />
              <VStack>
                <Text fontSize="3xl" fontWeight="bold" color="red.500">
                  {logStats.error}
                </Text>
                <Text fontSize="sm" color="gray.600">오류</Text>
              </VStack>
              <Divider orientation="vertical" h="60px" />
              <VStack>
                <Text fontSize="3xl" fontWeight="bold" color="yellow.500">
                  {logStats.warn}
                </Text>
                <Text fontSize="sm" color="gray.600">경고</Text>
              </VStack>
              <Divider orientation="vertical" h="60px" />
              <VStack>
                <Text fontSize="3xl" fontWeight="bold" color="blue.500">
                  {logStats.info}
                </Text>
                <Text fontSize="sm" color="gray.600">정보</Text>
              </VStack>
              <Divider orientation="vertical" h="60px" />
              <VStack>
                <Text fontSize="3xl" fontWeight="bold" color="gray.500">
                  {logStats.debug}
                </Text>
                <Text fontSize="sm" color="gray.600">디버그</Text>
              </VStack>
              <Divider orientation="vertical" h="60px" />
              <VStack>
                <Text fontSize="3xl" fontWeight="bold" color="purple.500">
                  {logStats.total}
                </Text>
                <Text fontSize="sm" color="gray.600">전체</Text>
              </VStack>
            </HStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}

export default Logs;