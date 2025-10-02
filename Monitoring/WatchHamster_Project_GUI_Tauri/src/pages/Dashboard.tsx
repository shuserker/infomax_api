import React from 'react'
import {
  Box,
  Heading,
  Text,
  Card,
  CardBody,
  Badge,
  VStack,
  HStack,
  Button,
  useToast,
  Flex,
  Spacer,
} from '@chakra-ui/react'
import { FiRefreshCw } from 'react-icons/fi'
import { MetricsGrid } from '../components/Dashboard/MetricsGrid'
import { RealtimeChart } from '../components/Dashboard/RealtimeChart'
import ServiceStatusGrid from '../components/Dashboard/ServiceStatusGrid'
import { useSystemMetrics } from '../hooks/useSystemMetrics'
import { useServiceStatus } from '../hooks/useServiceStatus'

const Dashboard: React.FC = () => {
  const toast = useToast()
  
  // 실시간 시스템 메트릭 데이터
  const {
    metrics,
    isLoading: metricsLoading,
    error: metricsError,
    lastUpdated,
    refreshMetrics,
    isConnected,
  } = useSystemMetrics({
    refreshInterval: 5000,
    enableRealtime: true,
    historySize: 20,
  })

  // 서비스 상태 데이터
  const {
    services,
    isLoading: servicesLoading,
    error: servicesError,
    refreshServices,
    connectionStatus
  } = useServiceStatus({
    autoRefresh: true,
    refreshInterval: 5000,
    enableWebSocket: true
  })

  const handleRefresh = async () => {
    await Promise.all([
      refreshMetrics(),
      refreshServices()
    ])
    
    toast({
      title: '대시보드 새로고침',
      description: '시스템 메트릭과 서비스 상태를 업데이트했습니다.',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const handleServiceUpdate = (_updatedServices: any[]) => {
    // 서비스 업데이트는 useServiceStatus 훅에서 자동으로 처리됨
    toast({
      title: '서비스 상태 업데이트',
      description: '서비스 상태가 업데이트되었습니다.',
      status: 'info',
      duration: 2000,
      isClosable: true,
    })
  }

  return (
    <Box className="fade-in">
      <VStack spacing={6} align="stretch">
        {/* 페이지 헤더 */}
        <Flex align="center" mb={6}>
          <Box>
            <Heading size="lg" mb={2}>
              시스템 대시보드
            </Heading>
            <HStack spacing={4}>
              <Text color="gray.600" _dark={{ color: 'gray.400' }}>
                실시간 시스템 상태 및 서비스 모니터링
              </Text>
              <Badge 
                colorScheme={isConnected ? 'green' : 'red'} 
                variant="subtle"
              >
                {isConnected ? '실시간 연결됨' : '연결 끊김'}
              </Badge>
              {lastUpdated && (
                <Text fontSize="sm" color="gray.500">
                  마지막 업데이트: {lastUpdated.toLocaleTimeString('ko-KR')}
                </Text>
              )}
            </HStack>
          </Box>
          <Spacer />
          <Button
            leftIcon={<FiRefreshCw />}
            onClick={handleRefresh}
            isLoading={metricsLoading || servicesLoading}
            loadingText="새로고침 중"
            size="sm"
            variant="outline"
          >
            새로고침
          </Button>
        </Flex>

        {/* 시스템 메트릭 카드들 */}
        <MetricsGrid
          metrics={metrics}
          isLoading={metricsLoading}
          error={metricsError || undefined}
          showTrends={true}
          compact={false}
        />

        {/* 실시간 성능 차트 */}
        <Box>
          <Heading size="md" mb={4}>
            실시간 성능 모니터링
          </Heading>
          <RealtimeChart
            height={400}
            showControls={true}
            autoUpdate={true}
            maxDataPoints={100}
          />
        </Box>

        {/* 서비스 상태 그리드 */}
        <Box>
          <Flex align="center" mb={4}>
            <Heading size="md">
              서비스 상태
            </Heading>
            <Spacer />
            <Badge 
              colorScheme={connectionStatus === 'connected' ? 'green' : 'red'} 
              variant="subtle"
            >
              {connectionStatus === 'connected' ? 'WebSocket 연결됨' : 'WebSocket 연결 끊김'}
            </Badge>
          </Flex>
          <ServiceStatusGrid
            services={services}
            onServiceUpdate={handleServiceUpdate}
            loading={servicesLoading}
            error={servicesError?.message}
          />
        </Box>

        {/* 최근 활동 */}
        <Box>
          <Heading size="md" mb={4}>
            최근 활동
          </Heading>
          <Card>
            <CardBody>
              <VStack align="stretch" spacing={3}>
                <HStack>
                  <Badge colorScheme="green">INFO</Badge>
                  <Text fontSize="sm">POSCO 뉴스 서비스가 시작되었습니다</Text>
                  <Text fontSize="xs" color="gray.500" ml="auto">
                    2분 전
                  </Text>
                </HStack>
                <HStack>
                  <Badge colorScheme="red">ERROR</Badge>
                  <Text fontSize="sm">배포 시스템에서 Git 충돌이 발생했습니다</Text>
                  <Text fontSize="xs" color="gray.500" ml="auto">
                    5분 전
                  </Text>
                </HStack>
                <HStack>
                  <Badge colorScheme="blue">INFO</Badge>
                  <Text fontSize="sm">웹훅 시스템이 Discord에 메시지를 전송했습니다</Text>
                  <Text fontSize="xs" color="gray.500" ml="auto">
                    8분 전
                  </Text>
                </HStack>
                <HStack>
                  <Badge colorScheme="yellow">WARN</Badge>
                  <Text fontSize="sm">GitHub Pages 모니터 연결이 끊어졌습니다</Text>
                  <Text fontSize="xs" color="gray.500" ml="auto">
                    12분 전
                  </Text>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        </Box>
      </VStack>
    </Box>
  )
}

export default Dashboard
