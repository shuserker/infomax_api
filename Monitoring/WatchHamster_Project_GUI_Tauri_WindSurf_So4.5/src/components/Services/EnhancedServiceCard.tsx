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
  Spacer,
  Progress,
  CircularProgress,
  CircularProgressLabel,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Grid,
  GridItem,
  useToast,
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
  FiXCircle
} from 'react-icons/fi'
import { useQuery } from '@tanstack/react-query'
import { apiService } from '../../services/api'

interface EnhancedServiceCardProps {
  onServiceAction: (serviceId: string, action: 'start' | 'stop' | 'restart') => Promise<void>
  onViewLogs?: (serviceId: string) => void
  isLoading?: boolean
}

const EnhancedServiceCard: React.FC<EnhancedServiceCardProps> = ({ 
  service, 
  onServiceAction, 
  onViewLogs,
  isLoading = false 
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
    lastRestart: '2024-01-15 14:30:25'
  }

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
    } catch (error) {
      toast({
        title: '서비스 제어 실패',
        description: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.',
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

  return (
    <>
      <Card h="100%" opacity={isLoading ? 0.6 : 1}>
        <CardHeader pb={3}>
          <HStack justify="space-between" align="start">
            <VStack align="start" spacing={1} flex="1" minW={0}>
              <HStack spacing={2} align="center">
                <Heading size="md" noOfLines={1}>{service.name}</Heading>
                {isLoading && <Spinner size="sm" />}
              </HStack>
              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }} noOfLines={2}>
                {service.description}
              </Text>
            </VStack>
            <VStack align="end" spacing={1}>
              <Badge
                colorScheme={getStatusColor(service.status)}
                variant="solid"
                fontSize="xs"
              >
                {getStatusText(service.status)}
              </Badge>
              {stats.pid && (
                <Text fontSize="xs" color="gray.500">
                  PID: {stats.pid}
                </Text>
              )}
            </VStack>
          </HStack>
        </CardHeader>

        <CardBody pt={0}>
          <VStack align="stretch" spacing={4}>
            {/* 기본 정보 */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" fontWeight="medium">
                  업타임
                </Text>
                <Text fontSize="sm">{formatUptime(stats.uptime)}</Text>
              </HStack>

              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" fontWeight="medium">
                  재시작 횟수
                </Text>
                <Text fontSize="sm">{stats.restartCount}회</Text>
              </HStack>

              {/* 리소스 사용량 (실행 중일 때만) */}
              {service.status === 'running' && stats.memoryUsage && (
                <>
                  <HStack justify="space-between" mb={1}>
                    <Text fontSize="sm" fontWeight="medium">
                      메모리 사용량
                    </Text>
                    <Text fontSize="sm">{formatMemory(stats.memoryUsage)}</Text>
                  </HStack>
                  <Progress 
                    value={75} 
                    size="sm" 
                    colorScheme="blue" 
                    mb={2}
                    borderRadius="md"
                  />
                </>
              )}

              {service.status === 'running' && stats.cpuUsage && (
                <>
                  <HStack justify="space-between" mb={1}>
                    <Text fontSize="sm" fontWeight="medium">
                      CPU 사용률
                    </Text>
                    <Text fontSize="sm">{stats.cpuUsage}%</Text>
                  </HStack>
                  <Progress 
                    value={stats.cpuUsage} 
                    size="sm" 
                    colorScheme="green" 
                    mb={2}
                    borderRadius="md"
                  />
                </>
              )}

              {/* 오류 정보 */}
              {service.last_error && (
                <Alert status="error" size="sm" borderRadius="md">
                  <AlertIcon />
                  <Box flex="1" minW={0}>
                    <Text fontSize="xs" noOfLines={2}>
                      {service.last_error}
                    </Text>
                  </Box>
                </Alert>
              )}
            </Box>

            {/* 확장 정보 */}
            <Box>
              <Button
                size="sm"
                variant="ghost"
                onClick={toggleExpanded}
                rightIcon={isExpanded ? <MdExpandLess /> : <MdExpandMore />}
                width="full"
                justifyContent="space-between"
              >
                <Text fontSize="sm">세부 정보</Text>
              </Button>
              
              <Collapse in={isExpanded} animateOpacity>
                <VStack align="stretch" spacing={3} mt={3}>
                  <Divider />
                  
                  {/* 설정 정보 */}
                  {service.config && Object.keys(service.config).length > 0 && (
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={2}>
                        설정
                      </Text>
                      <VStack align="stretch" spacing={1}>
                        {Object.entries(service.config).map(([key, value]) => (
                          <HStack key={key} justify="space-between">
                            <Text fontSize="xs" color="gray.600" _dark={{ color: 'gray.400' }}>
                              {key}
                            </Text>
                            <Text fontSize="xs" noOfLines={1} maxW="150px">
                              {String(value)}
                            </Text>
                          </HStack>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  {/* 마지막 재시작 시간 */}
                  {stats.lastRestart && (
                    <HStack justify="space-between">
                      <Text fontSize="sm" fontWeight="medium">
                        마지막 재시작
                      </Text>
                      <Text fontSize="sm">{stats.lastRestart}</Text>
                    </HStack>
                  )}

                  {/* 자동 재시작 설정 */}
                  <FormControl display="flex" alignItems="center">
                    <FormLabel htmlFor="auto-restart" mb="0" fontSize="sm">
                      자동 재시작
                    </FormLabel>
                    <Switch
                      id="auto-restart"
                      isChecked={autoRestart}
                      onChange={(e) => setAutoRestart(e.target.checked)}
                      size="sm"
                    />
                  </FormControl>
                </VStack>
              </Collapse>
            </Box>

            <Divider />

            {/* 제어 버튼들 */}
            <VStack spacing={2}>
              <HStack spacing={2} width="full">
                {service.status === 'running' ? (
                  <>
                    <Button
                      size="sm"
                      colorScheme="orange"
                      leftIcon={<MdStop />}
                      onClick={() => handleAction('stop')}
                      isLoading={actionLoading === 'stop'}
                      loadingText="중지 중"
                      flex="1"
                      isDisabled={isLoading}
                    >
                      중지
                    </Button>
                    <Button
                      size="sm"
                      colorScheme="blue"
                      leftIcon={<MdRefresh />}
                      onClick={() => handleAction('restart')}
                      isLoading={actionLoading === 'restart'}
                      loadingText="재시작 중"
                      flex="1"
                      isDisabled={isLoading}
                    >
                      재시작
                    </Button>
                  </>
                ) : (
                  <Button
                    size="sm"
                    colorScheme="green"
                    leftIcon={<MdPlayArrow />}
                    onClick={() => handleAction('start')}
                    isLoading={actionLoading === 'start'}
                    loadingText="시작 중"
                    flex="1"
                    isDisabled={isLoading}
                  >
                    시작
                  </Button>
                )}
              </HStack>

              {/* 추가 액션 버튼들 */}
              <HStack spacing={2} width="full">
                <Tooltip label="로그 보기">
                  <IconButton
                    size="sm"
                    aria-label="로그 보기"
                    icon={<MdVisibility />}
                    variant="outline"
                    onClick={handleViewLogs}
                    flex="1"
                    isDisabled={isLoading}
                  />
                </Tooltip>

                <Tooltip label="서비스 설정">
                  <IconButton
                    size="sm"
                    aria-label="서비스 설정"
                    icon={<MdSettings />}
                    variant="outline"
                    onClick={openSettings}
                    flex="1"
                    isDisabled={isLoading}
                  />
                </Tooltip>

                {service.status === 'error' && (
                  <Tooltip label="오류 진단">
                    <IconButton
                      size="sm"
                      aria-label="오류 진단"
                      icon={<MdBugReport />}
                      variant="outline"
                      colorScheme="red"
                      flex="1"
                      isDisabled={isLoading}
                    />
                  </Tooltip>
                )}
              </HStack>
            </VStack>
          </VStack>
        </CardBody>
      </Card>

      {/* 설정 모달 */}
      <Modal isOpen={isSettingsOpen} onClose={closeSettings} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{service.name} 설정</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack align="stretch" spacing={4}>
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-restart-modal" mb="0">
                  자동 재시작 활성화
                </FormLabel>
                <Switch
                  id="auto-restart-modal"
                  isChecked={autoRestart}
                  onChange={(e) => setAutoRestart(e.target.checked)}
                />
              </FormControl>

              <Box>
                <Text fontWeight="medium" mb={2}>현재 설정</Text>
                {service.config && Object.keys(service.config).length > 0 ? (
                  <VStack align="stretch" spacing={2}>
                    {Object.entries(service.config).map(([key, value]) => (
                      <HStack key={key} justify="space-between">
                        <Text fontSize="sm" color="gray.600">
                          {key}
                        </Text>
                        <Text fontSize="sm" fontWeight="medium">
                          {String(value)}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                ) : (
                  <Text fontSize="sm" color="gray.500">
                    설정 정보가 없습니다.
                  </Text>
                )}
              </Box>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={closeSettings}>
              취소
            </Button>
            <Button colorScheme="blue" onClick={closeSettings}>
              저장
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default EnhancedServiceCard