import React from 'react'
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Badge,
  VStack,
  HStack,
  Flex,
  Icon,
  Tooltip,
  useColorModeValue,
} from '@chakra-ui/react'
import {
  FaPlay,
  FaStop,
  FaExclamationTriangle,
  FaClock,
  FaInfoCircle,
} from 'react-icons/fa'
import { ServiceInfo, ServiceStatus } from '../../types'

export interface ServiceCardProps {
  service: ServiceInfo
  onClick?: (service: ServiceInfo) => void
  isSelected?: boolean
}

/**
 * 개별 서비스 정보를 표시하는 카드 컴포넌트
 * 서비스 상태, 업타임, 오류 정보 등을 시각적으로 표현
 */
export const ServiceCard: React.FC<ServiceCardProps> = ({
  service,
  onClick,
  isSelected = false,
}) => {
  // 테마 색상 설정
  const cardBg = useColorModeValue('white', 'gray.800')
  const selectedBg = useColorModeValue('blue.50', 'blue.900')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const selectedBorderColor = useColorModeValue('blue.300', 'blue.500')
  const textColor = useColorModeValue('gray.600', 'gray.300')
  const errorColor = useColorModeValue('red.500', 'red.300')

  // 서비스 상태에 따른 배지 설정
  const getStatusBadge = (status: ServiceStatus) => {
    const statusConfig = {
      running: {
        colorScheme: 'green',
        icon: FaPlay,
        label: '실행 중',
      },
      stopped: {
        colorScheme: 'gray',
        icon: FaStop,
        label: '중지됨',
      },
      error: {
        colorScheme: 'red',
        icon: FaExclamationTriangle,
        label: '오류',
      },
      starting: {
        colorScheme: 'yellow',
        icon: FaClock,
        label: '시작 중',
      },
      stopping: {
        colorScheme: 'orange',
        icon: FaClock,
        label: '중지 중',
      },
    }

    const config = statusConfig[status]
    return (
      <Badge
        colorScheme={config.colorScheme}
        variant="solid"
        display="flex"
        alignItems="center"
        gap={1}
        px={2}
        py={1}
        borderRadius="md"
      >
        <Icon as={config.icon} boxSize={3} />
        {config.label}
      </Badge>
    )
  }

  // 업타임 포맷팅
  const formatUptime = (uptime?: number): string => {
    if (!uptime) return '알 수 없음'

    const hours = Math.floor(uptime / 3600)
    const minutes = Math.floor((uptime % 3600) / 60)
    const seconds = uptime % 60

    if (hours > 0) {
      return `${hours}시간 ${minutes}분`
    } else if (minutes > 0) {
      return `${minutes}분 ${seconds}초`
    } else {
      return `${seconds}초`
    }
  }

  // 카드 클릭 핸들러
  const handleCardClick = () => {
    if (onClick) {
      onClick(service)
    }
  }

  return (
    <Card
      bg={isSelected ? selectedBg : cardBg}
      borderColor={isSelected ? selectedBorderColor : borderColor}
      borderWidth="2px"
      cursor={onClick ? 'pointer' : 'default'}
      onClick={handleCardClick}
      transition="all 0.2s"
      _hover={
        onClick
          ? {
              transform: 'translateY(-2px)',
              shadow: 'lg',
              borderColor: selectedBorderColor,
            }
          : {}
      }
      minH="200px"
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      data-testid="service-card"
    >
      <CardHeader pb={2}>
        <Flex justify="space-between" align="flex-start">
          <VStack align="flex-start" spacing={1} flex={1}>
            <Heading size="md" color={textColor}>
              {service.name}
            </Heading>
            <Text fontSize="sm" color={textColor} noOfLines={2}>
              {service.description}
            </Text>
          </VStack>
          {getStatusBadge(service.status)}
        </Flex>
      </CardHeader>

      <CardBody pt={0}>
        <VStack align="stretch" spacing={3}>
          {/* 업타임 정보 */}
          <HStack justify="space-between">
            <HStack>
              <Icon as={FaClock} color={textColor} boxSize={4} />
              <Text fontSize="sm" color={textColor}>
                업타임:
              </Text>
            </HStack>
            <Text fontSize="sm" fontWeight="medium">
              {formatUptime(service.uptime)}
            </Text>
          </HStack>

          {/* 서비스 ID */}
          <HStack justify="space-between">
            <HStack>
              <Icon as={FaInfoCircle} color={textColor} boxSize={4} />
              <Text fontSize="sm" color={textColor}>
                서비스 ID:
              </Text>
            </HStack>
            <Text fontSize="sm" fontFamily="mono" color={textColor}>
              {service.id}
            </Text>
          </HStack>

          {/* 마지막 오류 정보 */}
          {service.last_error && (
            <Box>
              <HStack mb={1}>
                <Icon as={FaExclamationTriangle} color={errorColor} boxSize={4} />
                <Text fontSize="sm" color={errorColor} fontWeight="medium">
                  마지막 오류:
                </Text>
              </HStack>
              <Tooltip label={service.last_error} placement="top">
                <Text
                  fontSize="xs"
                  color={errorColor}
                  noOfLines={2}
                  cursor="help"
                  bg={useColorModeValue('red.50', 'red.900')}
                  p={2}
                  borderRadius="md"
                  border="1px solid"
                  borderColor={useColorModeValue('red.200', 'red.700')}
                >
                  {service.last_error}
                </Text>
              </Tooltip>
            </Box>
          )}

          {/* 설정 정보 (있는 경우) */}
          {service.config && Object.keys(service.config).length > 0 && (
            <Box>
              <Text fontSize="sm" color={textColor} mb={1}>
                설정:
              </Text>
              <Box
                bg={useColorModeValue('gray.50', 'gray.700')}
                p={2}
                borderRadius="md"
                fontSize="xs"
                fontFamily="mono"
              >
                {Object.entries(service.config)
                  .slice(0, 3)
                  .map(([key, value]) => (
                    <Text key={key} noOfLines={1}>
                      {key}: {String(value)}
                    </Text>
                  ))}
                {Object.keys(service.config).length > 3 && (
                  <Text color={textColor}>
                    ... 및 {Object.keys(service.config).length - 3}개 더
                  </Text>
                )}
              </Box>
            </Box>
          )}
        </VStack>
      </CardBody>
    </Card>
  )
}

export default ServiceCard