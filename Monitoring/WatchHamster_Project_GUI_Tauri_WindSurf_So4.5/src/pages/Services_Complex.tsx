import React, { useState } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Grid,
  GridItem,
  Card,
  CardHeader,
  CardBody,
  HStack,
  Badge,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Divider,
  Alert,
  AlertIcon,
  useColorModeValue,
} from '@chakra-ui/react'
import {
  FiActivity,
  FiSend,
  FiNewspaper,
  FiCheckCircle,
  FiXCircle,
  FiClock,
  FiTrendingUp,
  FiAlertTriangle
} from 'react-icons/fi'
// import ServiceDependencyGraph from '../components/Services/ServiceDependencyGraph'

const Services: React.FC = () => {
  console.log('🔧 NEW Services page is rendering')

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  // 실제 데이터는 나중에 API에서 가져올 예정
  const mockData = {
    webhooks: {
      todaySuccess: 127,
      todayFailed: 3,
      successRate: 97.7,
      avgResponseTime: 245,
      lastSent: '2분 전'
    },
    newsMonitoring: {
      changesDetected: 15,
      lastCheck: '30초 전',
      alertsSent: 12,
      errorCount: 0,
      status: 'active'
    },
    services: [
      { id: 'api_server', name: 'API 서버', status: 'running', uptime: 99.8, responseTime: 45 },
      { id: 'webhook_sender', name: '웹훅 발송자', status: 'running', uptime: 99.9, responseTime: 120 },
      { id: 'watchhamster_monitor', name: 'WatchHamster 모니터', status: 'running', uptime: 99.5, responseTime: 200 },
      { id: 'infomax_client', name: 'InfoMax API 클라이언트', status: 'running', uptime: 98.9, responseTime: 300 },
      { id: 'news_parser', name: '뉴스 파서', status: 'running', uptime: 99.2, responseTime: 80 },
    ]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'green'
      case 'stopped': return 'red'
      case 'warning': return 'orange'
      default: return 'gray'
    }
  }

  const getUptimeColor = (uptime: number) => {
    if (uptime >= 99.5) return 'green'
    if (uptime >= 98.0) return 'orange'
    return 'red'
  }

  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        {/* 페이지 헤더 */}
        <Box>
          <Heading size="lg" color="blue.600" _dark={{ color: "blue.300" }}>
            🔧 서비스 관리
          </Heading>
          <Text color="gray.600" _dark={{ color: "gray.400" }} mt={2}>
            POSCO WatchHamster 시스템의 실시간 서비스 상태 및 운영 현황
          </Text>
        </Box>

        {/* 서비스 의존성 관계도 - 임시 비활성화 */}
        {/* <ServiceDependencyGraph services={mockData.services} /> */}

        {/* 메인 대시보드 그리드 */}
        <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={8}>
          
          {/* 웹훅 발송 현황 */}
          <Card bg={bgColor} borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <FiSend size={20} />
                <VStack spacing={1} align="start">
                  <Heading size="md">📊 웹훅 발송 현황</Heading>
                  <Text fontSize="sm" color="gray.500">Dooray 웹훅 실시간 통계</Text>
                </VStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <Stat>
                    <StatLabel>오늘 성공</StatLabel>
                    <StatNumber color="green.500">{mockData.webhooks.todaySuccess}</StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      전일 대비 +12%
                    </StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>오늘 실패</StatLabel>
                    <StatNumber color="red.500">{mockData.webhooks.todayFailed}</StatNumber>
                    <StatHelpText>
                      <StatArrow type="decrease" />
                      전일 대비 -50%
                    </StatHelpText>
                  </Stat>
                </Grid>

                <Divider />

                <HStack justify="space-between">
                  <VStack spacing={1} align="start">
                    <Text fontSize="sm" color="gray.600">성공률</Text>
                    <HStack>
                      <Text fontSize="2xl" fontWeight="bold" color="green.500">
                        {mockData.webhooks.successRate}%
                      </Text>
                      <FiCheckCircle color="green" />
                    </HStack>
                  </VStack>
                  <VStack spacing={1} align="end">
                    <Text fontSize="sm" color="gray.600">평균 응답시간</Text>
                    <HStack>
                      <Text fontSize="2xl" fontWeight="bold">
                        {mockData.webhooks.avgResponseTime}ms
                      </Text>
                      <FiClock />
                    </HStack>
                  </VStack>
                </HStack>

                <Progress 
                  value={mockData.webhooks.successRate} 
                  colorScheme="green" 
                  size="lg"
                  borderRadius="full"
                />

                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <Box fontSize="sm">
                    <Text fontWeight="bold">마지막 발송: {mockData.webhooks.lastSent}</Text>
                    <Text>모든 웹훅이 정상적으로 전송되고 있습니다.</Text>
                  </Box>
                </Alert>
              </VStack>
            </CardBody>
          </Card>

          {/* POSCO 뉴스 모니터링 상태 */}
          <Card bg={bgColor} borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <FiNewspaper size={20} />
                <VStack spacing={1} align="start">
                  <Heading size="md">📰 뉴스 모니터링 상태</Heading>
                  <Text fontSize="sm" color="gray.500">POSCO 뉴스 변경사항 감지 현황</Text>
                </VStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <Stat>
                    <StatLabel>오늘 감지된 변경</StatLabel>
                    <StatNumber color="blue.500">{mockData.newsMonitoring.changesDetected}</StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      평소보다 활발
                    </StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>발송된 알림</StatLabel>
                    <StatNumber color="purple.500">{mockData.newsMonitoring.alertsSent}</StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      전일 대비 +25%
                    </StatHelpText>
                  </Stat>
                </Grid>

                <Divider />

                <HStack justify="space-between">
                  <VStack spacing={1} align="start">
                    <Text fontSize="sm" color="gray.600">마지막 체크</Text>
                    <HStack>
                      <Badge colorScheme="green" variant="subtle">
                        {mockData.newsMonitoring.lastCheck}
                      </Badge>
                      <FiActivity color="green" />
                    </HStack>
                  </VStack>
                  <VStack spacing={1} align="end">
                    <Text fontSize="sm" color="gray.600">모니터링 상태</Text>
                    <HStack>
                      <Badge colorScheme="green">
                        활성
                      </Badge>
                      <FiTrendingUp color="green" />
                    </HStack>
                  </VStack>
                </HStack>

                <Alert status={mockData.newsMonitoring.errorCount > 0 ? "warning" : "success"} borderRadius="md">
                  <AlertIcon />
                  <Box fontSize="sm">
                    {mockData.newsMonitoring.errorCount > 0 ? (
                      <Text>
                        <Text as="span" fontWeight="bold">주의:</Text> {mockData.newsMonitoring.errorCount}개 오류 발생
                      </Text>
                    ) : (
                      <Text>
                        <Text as="span" fontWeight="bold">정상:</Text> 모든 뉴스 소스 모니터링 중
                      </Text>
                    )}
                  </Box>
                </Alert>
              </VStack>
            </CardBody>
          </Card>
        </Grid>

        {/* 시스템 헬스 체크 */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack>
              <FiActivity size={20} />
              <VStack spacing={1} align="start">
                <Heading size="md">🔍 시스템 헬스 체크</Heading>
                <Text fontSize="sm" color="gray.500">각 서비스별 가용성 및 성능 현황</Text>
              </VStack>
            </HStack>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={4}>
              {mockData.services.map((service) => (
                <Card key={service.id} size="sm" variant="outline">
                  <CardBody>
                    <VStack spacing={3} align="stretch">
                      <HStack justify="space-between">
                        <Text fontWeight="semibold" fontSize="sm">
                          {service.name}
                        </Text>
                        <Badge colorScheme={getStatusColor(service.status)} size="sm">
                          {service.status === 'running' ? '실행중' : '중지'}
                        </Badge>
                      </HStack>
                      
                      <VStack spacing={2} align="stretch">
                        <HStack justify="space-between">
                          <Text fontSize="xs" color="gray.600">가용성</Text>
                          <Text fontSize="xs" fontWeight="bold" color={getUptimeColor(service.uptime)}>
                            {service.uptime}%
                          </Text>
                        </HStack>
                        <Progress 
                          value={service.uptime} 
                          colorScheme={getUptimeColor(service.uptime)} 
                          size="sm"
                          borderRadius="full"
                        />
                      </VStack>

                      <HStack justify="space-between">
                        <Text fontSize="xs" color="gray.600">응답시간</Text>
                        <HStack spacing={1}>
                          <Text fontSize="xs" fontWeight="bold">
                            {service.responseTime}ms
                          </Text>
                          <FiClock size={12} />
                        </HStack>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </Grid>

            <Divider mt={6} />
            
            <HStack justify="center" mt={4}>
              <Text fontSize="sm" color="gray.500">
                시스템 전체 가용성: 
              </Text>
              <Text fontSize="sm" fontWeight="bold" color="green.500">
                99.46% (우수)
              </Text>
              <FiCheckCircle color="green" size={16} />
            </HStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}

export default Services
