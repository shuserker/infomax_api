import React, { useState } from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Badge,
  Button,
  VStack,
  HStack,
  IconButton,
  Tooltip,
  Divider,
  Box,
  Flex,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  Grid,
  GridItem,
  useToast,
  Skeleton,
} from '@chakra-ui/react'
import { 
  FiPlay, 
  FiSquare, 
  FiRefreshCw, 
  FiSettings, 
  FiEye,
  FiCpu,
  FiHardDrive,
  FiActivity,
  FiClock,
  FiAlertTriangle,
  FiCheckCircle,
  FiXCircle,
  FiZap
} from 'react-icons/fi'
import { useQuery } from '@tanstack/react-query'

interface ModernServiceCardProps {
  service: any
  onServiceAction: (serviceId: string, action: 'start' | 'stop' | 'restart') => Promise<void>
  onViewLogs?: (serviceId: string) => void
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'running': return 'green'
    case 'stopped': return 'gray'
    case 'starting': return 'yellow'
    case 'stopping': return 'orange'
    case 'error': return 'red'
    default: return 'gray'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'running': return FiCheckCircle
    case 'stopped': return FiXCircle
    case 'starting': return FiRefreshCw
    case 'stopping': return FiRefreshCw
    case 'error': return FiAlertTriangle
    default: return FiXCircle
  }
}

const formatUptime = (seconds: number): string => {
  if (!seconds) return '0초'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}시간 ${minutes}분`
  } else if (minutes > 0) {
    return `${minutes}분 ${secs}초`
  } else {
    return `${secs}초`
  }
}

const ModernServiceCard: React.FC<ModernServiceCardProps> = ({ 
  service, 
  onServiceAction, 
  onViewLogs
}) => {
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const toast = useToast()

  // 실제 서비스 메트릭 조회
  const { data: metrics, isLoading: metricsLoading, refetch: refetchMetrics } = useQuery({
    queryKey: ['service-metrics', service.id],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/services/${service.id}/metrics`)
        if (response.ok) {
          return await response.json()
        }
        return null
      } catch (error) {
        console.warn(`메트릭 조회 실패 (${service.id}):`, error)
        return null
      }
    },
    refetchInterval: 10000, // 10초마다 새로고침
    retry: 1
  })

  const handleAction = async (action: 'start' | 'stop' | 'restart') => {
    setActionLoading(action)
    try {
      await onServiceAction(service.id, action)
      toast({
        title: '서비스 제어 성공',
        description: `${service.name} 서비스를 ${action === 'start' ? '시작' : action === 'stop' ? '중지' : '재시작'}했습니다.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      // 메트릭 새로고침
      setTimeout(() => {
        refetchMetrics()
      }, 1000)
    } catch (error) {
      toast({
        title: '서비스 제어 실패',
        description: `서비스 제어 중 오류가 발생했습니다: ${error}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleViewLogs = () => {
    if (onViewLogs) {
      onViewLogs(service.id)
    }
  }

  const StatusIcon = getStatusIcon(service.status)
  const statusColor = getStatusColor(service.status)
  const metricsData = metrics?.metrics || {}

  return (
    <Card 
      variant="outline" 
      bg="white" 
      _dark={{ bg: "gray.800" }}
      shadow="sm"
      _hover={{ shadow: "md" }}
      transition="shadow 0.2s"
    >
      <CardHeader pb={3}>
        <Flex align="center" justify="space-between">
          <HStack spacing={3}>
            <Box
              p={2}
              bg={`${statusColor}.100`}
              _dark={{ bg: `${statusColor}.900` }}
              borderRadius="md"
            >
              <StatusIcon 
                size={20} 
                color={statusColor === 'green' ? '#22C55E' : statusColor === 'red' ? '#EF4444' : '#6B7280'} 
              />
            </Box>
            <Box>
              <Heading size="md" fontWeight="semibold">
                {service.name || service.display_name}
              </Heading>
              <Text fontSize="sm" color="gray.500" _dark={{ color: "gray.400" }}>
                {service.description}
              </Text>
            </Box>
          </HStack>
          <Badge 
            colorScheme={statusColor} 
            variant="subtle" 
            fontSize="xs"
            px={2} 
            py={1}
            borderRadius="full"
          >
            {service.status.toUpperCase()}
          </Badge>
        </Flex>
      </CardHeader>

      <CardBody pt={0}>
        <VStack spacing={4} align="stretch">
          {/* 메트릭 그리드 */}
          <Grid 
            templateColumns={service.id === 'webhook_sender' ? "repeat(2, 1fr)" : "repeat(2, 1fr)"} 
            gap={4}
          >
            <GridItem>
              <Stat size="sm">
                <StatLabel fontSize="xs" color="gray.500">
                  <HStack spacing={1}>
                    <FiCpu size={12} />
                    <Text>CPU 사용률</Text>
                  </HStack>
                </StatLabel>
                <StatNumber fontSize="lg">
                  {metricsLoading ? (
                    <Skeleton height="20px" width="40px" />
                  ) : (
                    `${metricsData.cpu_percent?.toFixed(1) || 0}%`
                  )}
                </StatNumber>
                {!metricsLoading && metricsData.cpu_percent && (
                  <Progress 
                    value={metricsData.cpu_percent} 
                    size="sm" 
                    colorScheme={metricsData.cpu_percent > 80 ? "red" : metricsData.cpu_percent > 50 ? "yellow" : "green"}
                    mt={1}
                  />
                )}
              </Stat>
            </GridItem>

            <GridItem>
              <Stat size="sm">
                <StatLabel fontSize="xs" color="gray.500">
                  <HStack spacing={1}>
                    <FiHardDrive size={12} />
                    <Text>메모리</Text>
                  </HStack>
                </StatLabel>
                <StatNumber fontSize="lg">
                  {metricsLoading ? (
                    <Skeleton height="20px" width="60px" />
                  ) : (
                    `${metricsData.process_memory_mb?.toFixed(0) || 0}MB`
                  )}
                </StatNumber>
                {!metricsLoading && metricsData.memory_percent && (
                  <Progress 
                    value={metricsData.memory_percent} 
                    size="sm" 
                    colorScheme={metricsData.memory_percent > 80 ? "red" : metricsData.memory_percent > 50 ? "yellow" : "green"}
                    mt={1}
                  />
                )}
              </Stat>
            </GridItem>

            {/* 서비스별 특화 메트릭 */}
            {service.id === 'webhook_sender' && (
              <>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiZap size={12} />
                        <Text>오늘 발송</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="30px" />
                      ) : (
                        `${metricsData.today_sent || 0}건`
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiCheckCircle size={12} />
                        <Text>성공률</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="40px" />
                      ) : (
                        `${metricsData.success_rate || 0}%`
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiActivity size={12} />
                        <Text>주간 발송</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="40px" />
                      ) : (
                        `${metricsData.weekly_sent || 0}건`
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiClock size={12} />
                        <Text>평균 응답</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="50px" />
                      ) : (
                        `${metricsData.avg_response_time_ms || 0}ms`
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
              </>
            )}

            {service.id === 'api_server' && (
              <>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiActivity size={12} />
                        <Text>연결 수</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="30px" />
                      ) : (
                        `${metricsData.connections || 0}`
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiSettings size={12} />
                        <Text>포트</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="40px" />
                      ) : (
                        `:${metricsData.port || 8000}`
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
              </>
            )}

            {service.id === 'watchhamster_monitor' && (
              <>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiActivity size={12} />
                        <Text>모니터링</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="40px" />
                      ) : metricsData.monitoring_active ? (
                        <Badge colorScheme="green" size="sm">활성</Badge>
                      ) : (
                        <Badge colorScheme="gray" size="sm">비활성</Badge>
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiClock size={12} />
                        <Text>마지막 체크</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="50px" />
                      ) : (
                        <Text fontSize="sm">{metricsData.last_check || 'N/A'}</Text>
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
              </>
            )}

            {service.id === 'infomax_client' && (
              <>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiCheckCircle size={12} />
                        <Text>API 연결</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="lg">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="40px" />
                      ) : metricsData.api_connected ? (
                        <Badge colorScheme="green" size="sm">연결됨</Badge>
                      ) : (
                        <Badge colorScheme="red" size="sm">연결안됨</Badge>
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat size="sm">
                    <StatLabel fontSize="xs" color="gray.500">
                      <HStack spacing={1}>
                        <FiSettings size={12} />
                        <Text>엔드포인트</Text>
                      </HStack>
                    </StatLabel>
                    <StatNumber fontSize="xs">
                      {metricsLoading ? (
                        <Skeleton height="20px" width="80px" />
                      ) : (
                        <Text fontSize="xs" color="blue.500">
                          {metricsData.base_url ? 'POSCO API' : 'N/A'}
                        </Text>
                      )}
                    </StatNumber>
                  </Stat>
                </GridItem>
              </>
            )}
          </Grid>

          {/* 추가 정보 */}
          <VStack spacing={2} align="stretch">
            {/* 업타임 정보 */}
            {service.uptime && (
              <Box>
                <Text fontSize="xs" color="gray.500" mb={1}>
                  <FiClock size={10} style={{ display: 'inline', marginRight: '4px' }} />
                  업타임: {formatUptime(service.uptime)}
                </Text>
              </Box>
            )}
            
            {/* 웹훅 발송자 전용 정보 */}
            {service.id === 'webhook_sender' && metricsData.top_message_type && (
              <Box>
                <Text fontSize="xs" color="gray.500">
                  <FiZap size={10} style={{ display: 'inline', marginRight: '4px' }} />
                  인기 메시지: 
                  <Badge ml={2} size="sm" colorScheme="purple" variant="subtle">
                    {metricsData.top_message_type}
                  </Badge>
                </Text>
              </Box>
            )}
            
            {/* WatchHamster 모니터 전용 정보 */}
            {service.id === 'watchhamster_monitor' && metricsData.monitoring_active && (
              <Box>
                <Text fontSize="xs" color="green.600">
                  <FiActivity size={10} style={{ display: 'inline', marginRight: '4px' }} />
                  실시간 모니터링 중...
                </Text>
              </Box>
            )}
            
            {/* INFOMAX API 클라이언트 정보 */}
            {service.id === 'infomax_client' && metricsData.base_url && (
              <Box>
                <Text fontSize="xs" color="blue.600">
                  <FiSettings size={10} style={{ display: 'inline', marginRight: '4px' }} />
                  POSCO API 연결됨
                </Text>
              </Box>
            )}
          </VStack>

          <Divider />

          {/* 액션 버튼 */}
          <HStack spacing={2} justify="flex-end">
            {onViewLogs && (
              <Tooltip label="로그 보기">
                <IconButton
                  aria-label="로그 보기"
                  icon={<FiEye />}
                  size="sm"
                  variant="ghost"
                  onClick={handleViewLogs}
                />
              </Tooltip>
            )}

            <Tooltip label="새로고침">
              <IconButton
                aria-label="새로고침"
                icon={<FiRefreshCw />}
                size="sm"
                variant="ghost"
                onClick={() => refetchMetrics()}
                isLoading={metricsLoading}
              />
            </Tooltip>

            {service.status === 'running' ? (
              <>
                <Button
                  leftIcon={<FiRefreshCw />}
                  size="sm"
                  variant="outline"
                  colorScheme="orange"
                  onClick={() => handleAction('restart')}
                  isLoading={actionLoading === 'restart'}
                  loadingText="재시작 중"
                >
                  재시작
                </Button>
                <Button
                  leftIcon={<FiSquare />}
                  size="sm"
                  variant="outline"
                  colorScheme="red"
                  onClick={() => handleAction('stop')}
                  isLoading={actionLoading === 'stop'}
                  loadingText="중지 중"
                  isDisabled={service.id === 'api_server'} // API 서버는 중지할 수 없음
                >
                  중지
                </Button>
              </>
            ) : (
              <Button
                leftIcon={<FiPlay />}
                size="sm"
                colorScheme="green"
                onClick={() => handleAction('start')}
                isLoading={actionLoading === 'start'}
                loadingText="시작 중"
              >
                시작
              </Button>
            )}
          </HStack>

          {/* 오류 메시지 */}
          {service.last_error && (
            <Box
              p={3}
              bg="red.50"
              _dark={{ bg: "red.900" }}
              borderRadius="md"
              borderLeft="4px solid"
              borderLeftColor="red.500"
            >
              <HStack>
                <FiAlertTriangle color="#EF4444" size={16} />
                <Text fontSize="sm" color="red.700" _dark={{ color: "red.300" }}>
                  {service.last_error}
                </Text>
              </HStack>
            </Box>
          )}
        </VStack>
      </CardBody>
    </Card>
  )
}

export default ModernServiceCard
