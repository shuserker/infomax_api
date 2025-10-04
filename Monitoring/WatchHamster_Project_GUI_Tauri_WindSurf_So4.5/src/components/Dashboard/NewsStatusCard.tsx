import React from 'react'
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
  Tooltip,
  Skeleton,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import { FiTrendingUp, FiDollarSign, FiBarChart, FiClock, FiAlertTriangle } from 'react-icons/fi'
import { NewsStatus } from '../../types'

interface NewsStatusCardProps {
  newsData: NewsStatus
  isLoading?: boolean
  error?: string
}

const getNewsIcon = (type: string) => {
  switch (type) {
    case 'exchange-rate':
      return FiDollarSign
    case 'newyork-market-watch':
      return FiTrendingUp
    case 'kospi-close':
      return FiBarChart
    default:
      return FiBarChart
  }
}

const getNewsTitle = (type: string) => {
  switch (type) {
    case 'exchange-rate':
      return '환율 정보'
    case 'newyork-market-watch':
      return '뉴욕 증시'
    case 'kospi-close':
      return 'KOSPI 마감'
    default:
      return '뉴스 정보'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'latest':
      return 'green'
    case 'delayed':
      return 'yellow'
    case 'outdated':
      return 'orange'
    case 'error':
      return 'red'
    default:
      return 'gray'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'latest':
      return '최신'
    case 'delayed':
      return '지연'
    case 'outdated':
      return '과거'
    case 'error':
      return '오류'
    default:
      return '알 수 없음'
  }
}

const formatTime = (timeString: string) => {
  try {
    const date = new Date(timeString)
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return timeString
  }
}

const NewsStatusCard: React.FC<NewsStatusCardProps> = ({
  newsData,
  isLoading = false,
  error
}) => {
  const IconComponent = getNewsIcon(newsData.type)
  const title = getNewsTitle(newsData.type)
  const statusColor = getStatusColor(newsData.status)
  const statusText = getStatusText(newsData.status)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton height="20px" width="120px" />
        </CardHeader>
        <CardBody>
          <VStack align="stretch" spacing={3}>
            <Skeleton height="16px" width="80px" />
            <Skeleton height="14px" width="100%" />
            <Skeleton height="14px" width="60%" />
          </VStack>
        </CardBody>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <HStack>
            <Icon as={IconComponent} boxSize={5} />
            <Heading size="sm">{title}</Heading>
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
            <Icon as={IconComponent} boxSize={5} color="blue.500" />
            <Heading size="sm">{title}</Heading>
          </HStack>
          <Badge colorScheme={statusColor} variant="subtle">
            {statusText}
          </Badge>
        </HStack>
      </CardHeader>
      <CardBody pt={0}>
        <VStack align="stretch" spacing={3}>
          {/* 마지막 업데이트 시간 */}
          <HStack justify="space-between">
            <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
              마지막 업데이트
            </Text>
            <Text fontSize="sm" fontWeight="medium">
              {formatTime(newsData.last_update)}
            </Text>
          </HStack>

          {/* 예상 시간 (있는 경우) */}
          {newsData.expected_time && (
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                예상 시간
              </Text>
              <Text fontSize="sm">
                {formatTime(newsData.expected_time)}
              </Text>
            </HStack>
          )}

          {/* 지연 시간 (있는 경우) */}
          {newsData.delay_minutes !== undefined && newsData.delay_minutes > 0 && (
            <HStack justify="space-between">
              <HStack>
                <Icon as={FiClock} boxSize={3} color="orange.500" />
                <Text fontSize="sm" color="orange.500">
                  지연 시간
                </Text>
              </HStack>
              <Text fontSize="sm" color="orange.500" fontWeight="medium">
                {newsData.delay_minutes}분
              </Text>
            </HStack>
          )}

          {/* 오류 메시지 (있는 경우) */}
          {newsData.error_message && (
            <Box>
              <HStack mb={1}>
                <Icon as={FiAlertTriangle} boxSize={3} color="red.500" />
                <Text fontSize="sm" color="red.500" fontWeight="medium">
                  오류 정보
                </Text>
              </HStack>
              <Tooltip label={newsData.error_message} placement="top">
                <Text 
                  fontSize="xs" 
                  color="red.500" 
                  noOfLines={2}
                  cursor="help"
                >
                  {newsData.error_message}
                </Text>
              </Tooltip>
            </Box>
          )}

          {/* 데이터 미리보기 (있는 경우) */}
          {newsData.data && typeof newsData.data === 'object' && (
            <Box>
              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }} mb={1}>
                데이터 미리보기
              </Text>
              <Box 
                bg="gray.50" 
                _dark={{ bg: 'gray.700' }} 
                p={2} 
                borderRadius="md"
                fontSize="xs"
              >
                <Text noOfLines={3} fontFamily="mono">
                  {JSON.stringify(newsData.data, null, 2).slice(0, 100)}
                  {JSON.stringify(newsData.data).length > 100 && '...'}
                </Text>
              </Box>
            </Box>
          )}
        </VStack>
      </CardBody>
    </Card>
  )
}

export default NewsStatusCard