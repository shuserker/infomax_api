import React, { useState, useCallback, useMemo } from 'react'
import {
  Box,
  Grid,
  Card,
  CardBody,
  Text,
  Badge,
  Button,
  ButtonGroup,
  IconButton,
  Flex,
  Spacer,
  useToast,
  Tooltip,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useDisclosure,
  Spinner,
  VStack,
  HStack,
  Divider,
  useColorModeValue
} from '@chakra-ui/react'
import {
  FiPlay,
  FiSquare,
  FiRefreshCw,
  FiInfo,
  FiAlertTriangle,
  FiCheckCircle,
  FiXCircle,
  FiClock,
  FiSettings
} from 'react-icons/fi'
import { ServiceInfo, ServiceStatus } from '../../types'
import { apiService } from '../../services/api'
import { formatUptime } from '../../utils'

interface ServiceStatusGridProps {
  services: ServiceInfo[]
  onServiceUpdate?: (services: ServiceInfo[]) => void
  loading?: boolean
  error?: string
}

interface ServiceControlAction {
  action: 'start' | 'stop' | 'restart'
  serviceId: string
  serviceName: string
}

const ServiceStatusGrid: React.FC<ServiceStatusGridProps> = ({
  services,
  onServiceUpdate,
  loading = false,
  error
}) => {
  const [controllingServices, setControllingServices] = useState<Set<string>>(new Set())
  const [pendingAction, setPendingAction] = useState<ServiceControlAction | null>(null)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const cancelRef = React.useRef<HTMLButtonElement>(null)
  const toast = useToast()

  // 테마 색상
  const cardBg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const textColor = useColorModeValue('gray.600', 'gray.300')
  const mutedTextColor = useColorModeValue('gray.500', 'gray.400')

  // 서비스 상태별 색상 및 아이콘 매핑
  const getStatusConfig = useCallback((status: ServiceStatus) => {
    switch (status) {
      case 'running':
        return {
          color: 'green',
          icon: FiCheckCircle,
          label: '실행 중'
        }
      case 'stopped':
        return {
          color: 'gray',
          icon: FiSquare,
          label: '중지됨'
        }
      case 'error':
        return {
          color: 'red',
          icon: FiXCircle,
          label: '오류'
        }
      case 'starting':
        return {
          color: 'blue',
          icon: FiClock,
          label: '시작 중'
        }
      case 'stopping':
        return {
          color: 'orange',
          icon: FiClock,
          label: '중지 중'
        }
      default:
        return {
          color: 'gray',
          icon: FiInfo,
          label: '알 수 없음'
        }
    }
  }, [])

  // 서비스 제어 가능 여부 확인
  const canControlService = useCallback((service: ServiceInfo) => {
    return !controllingServices.has(service.id) && 
           !['starting', 'stopping'].includes(service.status)
  }, [controllingServices])

  // 서비스 제어 액션 실행
  const executeServiceAction = useCallback(async (action: ServiceControlAction) => {
    const { action: actionType, serviceId, serviceName } = action
    
    setControllingServices(prev => new Set(prev).add(serviceId))
    
    try {
      switch (actionType) {
        case 'start':
          await apiService.startService(serviceId)
          break
        case 'stop':
          await apiService.stopService(serviceId)
          break
        case 'restart':
          await apiService.restartService(serviceId)
          break
        default:
          throw new Error(`알 수 없는 액션: ${actionType}`)
      }

      toast({
        title: '서비스 제어 성공',
        description: `${serviceName} 서비스가 ${actionType === 'start' ? '시작' : actionType === 'stop' ? '중지' : '재시작'}되었습니다.`,
        status: 'success',
        duration: 3000,
        isClosable: true
      })

      // 서비스 목록 업데이트
      if (onServiceUpdate) {
        const updatedServices = await apiService.getServices()
        onServiceUpdate(updatedServices)
      }
    } catch (error: any) {
      console.error('서비스 제어 오류:', error)
      toast({
        title: '서비스 제어 실패',
        description: error.message || `${serviceName} 서비스 ${actionType} 중 오류가 발생했습니다.`,
        status: 'error',
        duration: 5000,
        isClosable: true
      })
    } finally {
      setControllingServices(prev => {
        const newSet = new Set(prev)
        newSet.delete(serviceId)
        return newSet
      })
    }
  }, [onServiceUpdate, toast])

  // 서비스 제어 확인 대화상자 열기
  const handleServiceAction = useCallback((action: 'start' | 'stop' | 'restart', service: ServiceInfo) => {
    setPendingAction({
      action,
      serviceId: service.id,
      serviceName: service.name
    })
    onOpen()
  }, [onOpen])

  // 확인 대화상자에서 액션 실행
  const confirmAction = useCallback(async () => {
    if (pendingAction) {
      await executeServiceAction(pendingAction)
      setPendingAction(null)
      onClose()
    }
  }, [pendingAction, executeServiceAction, onClose])

  // 서비스 카드 렌더링
  const renderServiceCard = useCallback((service: ServiceInfo) => {
    const statusConfig = getStatusConfig(service.status)
    const StatusIcon = statusConfig.icon
    const isControlling = controllingServices.has(service.id)
    const canControl = canControlService(service)

    return (
      <Card
        key={service.id}
        bg={cardBg}
        borderColor={borderColor}
        borderWidth="1px"
        shadow="sm"
        _hover={{ shadow: 'md' }}
        transition="all 0.2s"
      >
        <CardBody p={4}>
          <VStack align="stretch" spacing={3}>
            {/* 서비스 헤더 */}
            <Flex align="center">
              <HStack spacing={2}>
                <StatusIcon color={`${statusConfig.color}.500`} size="16" />
                <Text fontWeight="semibold" fontSize="sm" noOfLines={1}>
                  {service.name}
                </Text>
              </HStack>
              <Spacer />
              <Badge
                colorScheme={statusConfig.color}
                variant="subtle"
                fontSize="xs"
                px={2}
                py={1}
                borderRadius="md"
              >
                {statusConfig.label}
              </Badge>
            </Flex>

            {/* 서비스 설명 */}
            {service.description && (
              <Text fontSize="xs" color={mutedTextColor} noOfLines={2}>
                {service.description}
              </Text>
            )}

            {/* 서비스 정보 */}
            <VStack align="stretch" spacing={1}>
              {service.uptime !== undefined && service.status === 'running' && (
                <HStack justify="space-between" fontSize="xs">
                  <Text color={textColor}>업타임:</Text>
                  <Text color={textColor} fontWeight="medium">
                    {formatUptime(service.uptime)}
                  </Text>
                </HStack>
              )}
              
              {service.last_error && service.status === 'error' && (
                <Box>
                  <Text fontSize="xs" color="red.500" fontWeight="medium" mb={1}>
                    마지막 오류:
                  </Text>
                  <Text fontSize="xs" color="red.400" noOfLines={2}>
                    {service.last_error}
                  </Text>
                </Box>
              )}
            </VStack>

            <Divider />

            {/* 제어 버튼 */}
            <Flex justify="center">
              {isControlling ? (
                <HStack spacing={2}>
                  <Spinner size="sm" color="blue.500" />
                  <Text fontSize="xs" color="blue.500">
                    처리 중...
                  </Text>
                </HStack>
              ) : (
                <ButtonGroup size="sm" variant="outline" spacing={1}>
                  <Tooltip label="서비스 시작" placement="top">
                    <IconButton
                      aria-label="서비스 시작"
                      icon={<FiPlay />}
                      colorScheme="green"
                      isDisabled={!canControl || service.status === 'running'}
                      onClick={() => handleServiceAction('start', service)}
                      size="sm"
                    />
                  </Tooltip>
                  
                  <Tooltip label="서비스 중지" placement="top">
                    <IconButton
                      aria-label="서비스 중지"
                      icon={<FiSquare />}
                      colorScheme="red"
                      isDisabled={!canControl || service.status === 'stopped'}
                      onClick={() => handleServiceAction('stop', service)}
                      size="sm"
                    />
                  </Tooltip>
                  
                  <Tooltip label="서비스 재시작" placement="top">
                    <IconButton
                      aria-label="서비스 재시작"
                      icon={<FiRefreshCw />}
                      colorScheme="blue"
                      isDisabled={!canControl}
                      onClick={() => handleServiceAction('restart', service)}
                      size="sm"
                    />
                  </Tooltip>
                </ButtonGroup>
              )}
            </Flex>
          </VStack>
        </CardBody>
      </Card>
    )
  }, [
    cardBg,
    borderColor,
    textColor,
    mutedTextColor,
    getStatusConfig,
    controllingServices,
    canControlService,
    handleServiceAction
  ])

  // 서비스 통계 계산
  const serviceStats = useMemo(() => {
    const stats = {
      total: services.length,
      running: 0,
      stopped: 0,
      error: 0,
      transitioning: 0
    }

    services.forEach(service => {
      switch (service.status) {
        case 'running':
          stats.running++
          break
        case 'stopped':
          stats.stopped++
          break
        case 'error':
          stats.error++
          break
        case 'starting':
        case 'stopping':
          stats.transitioning++
          break
      }
    })

    return stats
  }, [services])

  // 로딩 상태
  if (loading) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <Spinner size="lg" color="blue.500" />
          <Text color={textColor}>서비스 상태를 불러오는 중...</Text>
        </VStack>
      </Box>
    )
  }

  // 오류 상태
  if (error) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <FiAlertTriangle size="48" color="red" />
          <Text color="red.500" textAlign="center">
            서비스 상태를 불러오는 중 오류가 발생했습니다
          </Text>
          <Text fontSize="sm" color={mutedTextColor} textAlign="center">
            {error}
          </Text>
        </VStack>
      </Box>
    )
  }

  // 서비스가 없는 경우
  if (services.length === 0) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <FiSettings size="48" color="gray" />
          <Text color={textColor} textAlign="center">
            등록된 서비스가 없습니다
          </Text>
        </VStack>
      </Box>
    )
  }

  return (
    <Box>
      {/* 서비스 통계 */}
      <Box mb={6}>
        <Text fontSize="lg" fontWeight="semibold" mb={3}>
          서비스 상태 ({serviceStats.total}개)
        </Text>
        <HStack spacing={4} wrap="wrap">
          <HStack>
            <Badge colorScheme="green" variant="subtle">
              실행 중: {serviceStats.running}
            </Badge>
          </HStack>
          <HStack>
            <Badge colorScheme="gray" variant="subtle">
              중지됨: {serviceStats.stopped}
            </Badge>
          </HStack>
          {serviceStats.error > 0 && (
            <HStack>
              <Badge colorScheme="red" variant="subtle">
                오류: {serviceStats.error}
              </Badge>
            </HStack>
          )}
          {serviceStats.transitioning > 0 && (
            <HStack>
              <Badge colorScheme="blue" variant="subtle">
                전환 중: {serviceStats.transitioning}
              </Badge>
            </HStack>
          )}
        </HStack>
      </Box>

      {/* 서비스 그리드 */}
      <Grid
        templateColumns={{
          base: '1fr',
          md: 'repeat(2, 1fr)',
          lg: 'repeat(3, 1fr)',
          xl: 'repeat(4, 1fr)'
        }}
        gap={4}
      >
        {services.map(renderServiceCard)}
      </Grid>

      {/* 서비스 제어 확인 대화상자 */}
      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
        isCentered
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              서비스 제어 확인
            </AlertDialogHeader>

            <AlertDialogBody>
              {pendingAction && (
                <Text>
                  <Text as="span" fontWeight="semibold">
                    {pendingAction.serviceName}
                  </Text>{' '}
                  서비스를{' '}
                  <Text as="span" fontWeight="semibold" color={
                    pendingAction.action === 'start' ? 'green.500' :
                    pendingAction.action === 'stop' ? 'red.500' : 'blue.500'
                  }>
                    {pendingAction.action === 'start' ? '시작' :
                     pendingAction.action === 'stop' ? '중지' : '재시작'}
                  </Text>
                  하시겠습니까?
                </Text>
              )}
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                취소
              </Button>
              <Button
                colorScheme={
                  pendingAction?.action === 'start' ? 'green' :
                  pendingAction?.action === 'stop' ? 'red' : 'blue'
                }
                onClick={confirmAction}
                ml={3}
              >
                확인
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  )
}

export default ServiceStatusGrid