import React, { useState } from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Badge,
  VStack,
  HStack,
  Box,
  Icon,
  Skeleton,
  Alert,
  AlertIcon,
  Button,
  Collapse,
  useDisclosure,
  Tooltip,
  Divider,
} from '@chakra-ui/react'
import { 
  FiBell, 
  FiInfo, 
  FiAlertTriangle, 
  FiAlertCircle, 
  FiX,
  FiChevronDown,
  FiChevronUp,
  FiRefreshCw,
  FiClock
} from 'react-icons/fi'

interface AlertEntry {
  id: string
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
  service: string
  message: string
  details?: string
  acknowledged?: boolean
}

interface RecentAlertsWidgetProps {
  alerts?: AlertEntry[]
  isLoading?: boolean
  error?: string
  maxItems?: number
  onRefresh?: () => void
  onAcknowledge?: (alertId: string) => void
  showAcknowledged?: boolean
}

const getAlertIcon = (level: string) => {
  switch (level) {
    case 'INFO':
      return FiInfo
    case 'WARN':
      return FiAlertTriangle
    case 'ERROR':
    case 'CRITICAL':
      return FiAlertCircle
    default:
      return FiInfo
  }
}

const getAlertColor = (level: string) => {
  switch (level) {
    case 'INFO':
      return 'blue'
    case 'WARN':
      return 'yellow'
    case 'ERROR':
      return 'red'
    case 'CRITICAL':
      return 'red'
    default:
      return 'gray'
  }
}

const formatRelativeTime = (timestamp: string) => {
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return '방금 전'
    if (diffMins < 60) return `${diffMins}분 전`
    if (diffHours < 24) return `${diffHours}시간 전`
    if (diffDays < 7) return `${diffDays}일 전`
    
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return timestamp
  }
}

const AlertItem: React.FC<{
  alert: AlertEntry
  onAcknowledge?: (alertId: string) => void
}> = ({ alert, onAcknowledge }) => {
  const { isOpen, onToggle } = useDisclosure()
  const AlertIcon = getAlertIcon(alert.level)
  const alertColor = getAlertColor(alert.level)

  return (
    <Box>
      <HStack spacing={3} align="start">
        <Icon 
          as={AlertIcon} 
          boxSize={4} 
          color={`${alertColor}.500`}
          mt={0.5}
          opacity={alert.acknowledged ? 0.5 : 1}
        />
        <Box flex={1} minW={0}>
          <HStack justify="space-between" align="start" mb={1}>
            <VStack align="start" spacing={0} flex={1} minW={0}>
              <HStack spacing={2} wrap="wrap">
                <Badge 
                  colorScheme={alertColor} 
                  variant={alert.acknowledged ? 'outline' : 'subtle'}
                  size="sm"
                >
                  {alert.level}
                </Badge>
                <Badge variant="outline" size="sm">
                  {alert.service}
                </Badge>
                {alert.acknowledged && (
                  <Badge colorScheme="gray" variant="subtle" size="sm">
                    확인됨
                  </Badge>
                )}
              </HStack>
              <Text 
                fontSize="sm" 
                noOfLines={2}
                opacity={alert.acknowledged ? 0.7 : 1}
              >
                {alert.message}
              </Text>
            </VStack>
            <VStack align="end" spacing={1}>
              <HStack spacing={1}>
                <Tooltip label={new Date(alert.timestamp).toLocaleString('ko-KR')}>
                  <Text 
                    fontSize="xs" 
                    color="gray.500" 
                    cursor="help"
                    whiteSpace="nowrap"
                  >
                    {formatRelativeTime(alert.timestamp)}
                  </Text>
                </Tooltip>
                {onAcknowledge && !alert.acknowledged && (
                  <Button
                    size="xs"
                    variant="ghost"
                    onClick={() => onAcknowledge(alert.id)}
                    title="확인 처리"
                  >
                    <Icon as={FiX} boxSize={3} />
                  </Button>
                )}
              </HStack>
              {alert.details && (
                <Button
                  size="xs"
                  variant="ghost"
                  onClick={onToggle}
                  title={isOpen ? '세부사항 숨기기' : '세부사항 보기'}
                >
                  <Icon as={isOpen ? FiChevronUp : FiChevronDown} boxSize={3} />
                </Button>
              )}
            </VStack>
          </HStack>
          
          {alert.details && (
            <Collapse in={isOpen} animateOpacity>
              <Box 
                mt={2} 
                p={2} 
                bg="gray.50" 
                _dark={{ bg: 'gray.700' }} 
                borderRadius="md"
                fontSize="xs"
              >
                <Text fontFamily="mono" whiteSpace="pre-wrap">
                  {alert.details}
                </Text>
              </Box>
            </Collapse>
          )}
        </Box>
      </HStack>
    </Box>
  )
}

const RecentAlertsWidget: React.FC<RecentAlertsWidgetProps> = ({
  alerts = [],
  isLoading = false,
  error,
  maxItems = 10,
  onRefresh,
  onAcknowledge,
  showAcknowledged = true
}) => {
  const [showAll, setShowAll] = useState(false)

  // 필터링된 알림 목록
  const filteredAlerts = showAcknowledged 
    ? alerts 
    : alerts.filter(alert => !alert.acknowledged)

  // 표시할 알림 목록
  const displayAlerts = showAll 
    ? filteredAlerts 
    : filteredAlerts.slice(0, maxItems)

  const unacknowledgedCount = alerts.filter(alert => !alert.acknowledged).length

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton height="20px" width="120px" />
        </CardHeader>
        <CardBody>
          <VStack align="stretch" spacing={3}>
            {Array.from({ length: 3 }).map((_, index) => (
              <HStack key={index} spacing={3}>
                <Skeleton boxSize={4} />
                <VStack align="start" flex={1} spacing={1}>
                  <Skeleton height="16px" width="60%" />
                  <Skeleton height="14px" width="80%" />
                </VStack>
                <Skeleton height="12px" width="40px" />
              </HStack>
            ))}
          </VStack>
        </CardBody>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiBell} boxSize={5} />
              <Heading size="sm">최근 알림</Heading>
            </HStack>
            {onRefresh && (
              <Button size="xs" variant="ghost" onClick={onRefresh}>
                <Icon as={FiRefreshCw} />
              </Button>
            )}
          </HStack>
        </CardHeader>
        <CardBody>
          <Alert status="error" size="sm">
            <AlertIcon />
            <Text fontSize="sm">{error}</Text>
          </Alert>
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader pb={2}>
        <HStack justify="space-between">
          <HStack>
            <Icon as={FiBell} boxSize={5} color="orange.500" />
            <Heading size="sm">최근 알림</Heading>
            {unacknowledgedCount > 0 && (
              <Badge colorScheme="red" variant="solid" borderRadius="full">
                {unacknowledgedCount}
              </Badge>
            )}
          </HStack>
          <HStack spacing={2}>
            {!showAcknowledged && (
              <Button
                size="xs"
                variant="ghost"
                onClick={() => setShowAll(!showAll)}
              >
                {showAll ? '접기' : `모두 보기 (${filteredAlerts.length})`}
              </Button>
            )}
            {onRefresh && (
              <Button size="xs" variant="ghost" onClick={onRefresh}>
                <Icon as={FiRefreshCw} />
              </Button>
            )}
          </HStack>
        </HStack>
      </CardHeader>
      <CardBody pt={0}>
        {displayAlerts.length === 0 ? (
          <VStack spacing={3} py={4}>
            <Icon as={FiClock} boxSize={8} color="gray.400" />
            <Text fontSize="sm" color="gray.500" textAlign="center">
              {showAcknowledged ? '최근 알림이 없습니다' : '확인되지 않은 알림이 없습니다'}
            </Text>
          </VStack>
        ) : (
          <VStack align="stretch" spacing={3}>
            {displayAlerts.map((alert, index) => (
              <React.Fragment key={alert.id}>
                <AlertItem 
                  alert={alert} 
                  onAcknowledge={onAcknowledge}
                />
                {index < displayAlerts.length - 1 && <Divider />}
              </React.Fragment>
            ))}
            
            {!showAll && filteredAlerts.length > maxItems && (
              <Box pt={2}>
                <Button
                  size="sm"
                  variant="ghost"
                  width="full"
                  onClick={() => setShowAll(true)}
                >
                  {filteredAlerts.length - maxItems}개 더 보기
                </Button>
              </Box>
            )}
          </VStack>
        )}
      </CardBody>
    </Card>
  )
}

export default RecentAlertsWidget