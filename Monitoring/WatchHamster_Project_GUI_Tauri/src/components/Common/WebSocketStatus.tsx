/**
 * WebSocket 연결 상태 표시 컴포넌트
 * 
 * 이 컴포넌트는 WebSocket 연결 상태를 시각적으로 표시하고
 * 연결 제어 기능을 제공합니다.
 */

import React from 'react'
import {
  Box,
  Badge,
  Button,
  HStack,
  VStack,
  Text,
  Tooltip,
  Icon,
  useColorModeValue,
  Collapse,
  IconButton,
} from '@chakra-ui/react'
import {
  FiWifiOff,
  FiRefreshCw,
  FiAlertCircle,
  FiCheckCircle,
  FiClock,
  FiChevronDown,
  FiChevronUp,
} from 'react-icons/fi'

interface WebSocketStatusProps {
  isConnected: boolean
  connectionStatus: string
  reconnectAttempts: number
  lastHeartbeat?: Date | null
  onReconnect?: () => void
  onDisconnect?: () => void
  showDetails?: boolean
  compact?: boolean
}

export const WebSocketStatus: React.FC<WebSocketStatusProps> = ({
  isConnected,
  connectionStatus,
  reconnectAttempts,
  lastHeartbeat,
  onReconnect,
  onDisconnect,
  showDetails = false,
  compact = false,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false)

  // 색상 테마
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  // 상태별 색상 및 아이콘
  const getStatusConfig = () => {
    switch (connectionStatus) {
      case 'connected':
        return {
          color: 'green',
          icon: FiCheckCircle,
          label: '연결됨',
          description: 'WebSocket 연결이 정상적으로 작동 중입니다.',
        }
      case 'connecting':
        return {
          color: 'yellow',
          icon: FiClock,
          label: '연결 중',
          description: 'WebSocket 서버에 연결을 시도하고 있습니다.',
        }
      case 'reconnecting':
        return {
          color: 'orange',
          icon: FiRefreshCw,
          label: '재연결 중',
          description: `재연결을 시도하고 있습니다. (${reconnectAttempts}회 시도)`,
        }
      case 'disconnected':
        return {
          color: 'gray',
          icon: FiWifiOff,
          label: '연결 해제',
          description: 'WebSocket 연결이 해제되었습니다.',
        }
      case 'error':
      case 'failed':
        return {
          color: 'red',
          icon: FiAlertCircle,
          label: '연결 실패',
          description: 'WebSocket 연결에 문제가 발생했습니다.',
        }
      default:
        return {
          color: 'gray',
          icon: FiWifiOff,
          label: '알 수 없음',
          description: '연결 상태를 확인할 수 없습니다.',
        }
    }
  }

  const statusConfig = getStatusConfig()

  // 마지막 하트비트 시간 포맷
  const formatLastHeartbeat = () => {
    if (!lastHeartbeat) return '없음'
    
    const now = new Date()
    const diff = now.getTime() - lastHeartbeat.getTime()
    
    if (diff < 60000) {
      return `${Math.floor(diff / 1000)}초 전`
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}분 전`
    } else {
      return lastHeartbeat.toLocaleTimeString()
    }
  }

  // 컴팩트 모드
  if (compact) {
    return (
      <Tooltip label={statusConfig.description}>
        <HStack spacing={2}>
          <Icon
            as={statusConfig.icon}
            color={`${statusConfig.color}.500`}
            boxSize={4}
          />
          <Badge colorScheme={statusConfig.color} variant="subtle">
            {statusConfig.label}
          </Badge>
        </HStack>
      </Tooltip>
    )
  }

  return (
    <Box
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="md"
      p={4}
      shadow="sm"
    >
      <HStack justify="space-between" align="center">
        <HStack spacing={3}>
          <Icon
            as={statusConfig.icon}
            color={`${statusConfig.color}.500`}
            boxSize={5}
            className={connectionStatus === 'connecting' || connectionStatus === 'reconnecting' ? 'animate-spin' : ''}
          />
          <VStack align="start" spacing={0}>
            <Text fontWeight="medium" fontSize="sm">
              WebSocket 연결
            </Text>
            <Badge colorScheme={statusConfig.color} variant="subtle">
              {statusConfig.label}
            </Badge>
          </VStack>
        </HStack>

        <HStack spacing={2}>
          {/* 재연결 버튼 */}
          {!isConnected && onReconnect && (
            <Button
              size="sm"
              variant="outline"
              leftIcon={<FiRefreshCw />}
              onClick={onReconnect}
              isLoading={connectionStatus === 'connecting' || connectionStatus === 'reconnecting'}
              loadingText="연결 중"
            >
              재연결
            </Button>
          )}

          {/* 연결 해제 버튼 */}
          {isConnected && onDisconnect && (
            <Button
              size="sm"
              variant="outline"
              colorScheme="red"
              leftIcon={<FiWifiOff />}
              onClick={onDisconnect}
            >
              연결 해제
            </Button>
          )}

          {/* 상세 정보 토글 */}
          {showDetails && (
            <IconButton
              aria-label="상세 정보 토글"
              icon={isExpanded ? <FiChevronUp /> : <FiChevronDown />}
              size="sm"
              variant="ghost"
              onClick={() => setIsExpanded(!isExpanded)}
            />
          )}
        </HStack>
      </HStack>

      {/* 상세 정보 */}
      {showDetails && (
        <Collapse in={isExpanded} animateOpacity>
          <VStack align="start" spacing={2} mt={4} pt={4} borderTop="1px" borderColor={borderColor}>
            <Text fontSize="sm" color="gray.600">
              {statusConfig.description}
            </Text>
            
            <HStack spacing={4} fontSize="xs" color="gray.500">
              <Text>
                <strong>재연결 시도:</strong> {reconnectAttempts}회
              </Text>
              <Text>
                <strong>마지막 하트비트:</strong> {formatLastHeartbeat()}
              </Text>
            </HStack>

            {/* 연결 상태별 추가 정보 */}
            {connectionStatus === 'error' && (
              <Text fontSize="xs" color="red.500">
                연결 오류가 발생했습니다. 네트워크 상태를 확인해주세요.
              </Text>
            )}

            {connectionStatus === 'failed' && (
              <Text fontSize="xs" color="red.500">
                최대 재연결 시도 횟수를 초과했습니다. 수동으로 재연결을 시도해주세요.
              </Text>
            )}

            {reconnectAttempts > 0 && connectionStatus !== 'connected' && (
              <Text fontSize="xs" color="orange.500">
                재연결을 시도하고 있습니다. 잠시만 기다려주세요.
              </Text>
            )}
          </VStack>
        </Collapse>
      )}
    </Box>
  )
}

export default WebSocketStatus