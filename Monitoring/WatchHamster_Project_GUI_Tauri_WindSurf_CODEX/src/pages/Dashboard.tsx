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
  Grid,
  GridItem,
} from '@chakra-ui/react'
import { FiRefreshCw } from 'react-icons/fi'
import { useQuery } from '@tanstack/react-query'
import { MetricsGrid } from '../components/Dashboard/MetricsGrid'
import { RealtimeChart } from '../components/Dashboard/RealtimeChart'
import ServiceStatusGrid from '../components/Dashboard/ServiceStatusGrid'
import { NewsStatusCard, GitStatusWidget, RecentAlertsWidget } from '../components/Dashboard'
import { useSystemMetrics } from '../hooks/useSystemMetrics'
import { useNewsStatus } from '../hooks/useNewsStatus'
import { useGitStatus } from '../hooks/useGitStatus'
import { useRecentAlerts } from '../hooks/useRecentAlerts'
import { apiService } from '../services/api'

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

  // 뉴스 상태 데이터
  const {
    newsData,
    isLoading: newsLoading,
    error: newsError,
    refreshNews,
    isConnected: newsConnected
  } = useNewsStatus({
    refreshInterval: 30000,
    enableRealtime: true,
  })

  // Git 상태 데이터
  const {
    gitStatus,
    isLoading: gitLoading,
    error: gitError,
    refreshGitStatus,
    isConnected: gitConnected
  } = useGitStatus({
    refreshInterval: 60000,
    enableRealtime: true,
  })

  // 최근 알림 데이터
  const {
    alerts,
    isLoading: alertsLoading,
    error: alertsError,
    refreshAlerts,
    acknowledgeAlert,
    unacknowledgedCount
  } = useRecentAlerts({
    refreshInterval: 30000,
    enableRealtime: true,
    maxAlerts: 20,
  })

  // 서비스 상태 데이터 (직접 API 호출)
  const {
    data: services = [],
    isLoading: servicesLoading,
    error: servicesError,
    refetch: refreshServices
  } = useQuery({
    queryKey: ['services'],
    queryFn: async () => {
      const response = await apiService.getServices();
      return response;
    },
    refetchInterval: 5000,
    retry: 3,
    retryDelay: 1000,
  })

  const handleRefresh = async () => {
    try {
      await Promise.all([
        refreshMetrics(),
        refreshServices(),
        refreshNews(),
        refreshGitStatus(),
        refreshAlerts()
      ])
      
      toast({
        title: '대시보드 새로고침',
        description: '모든 데이터를 성공적으로 업데이트했습니다.',
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: '새로고침 실패',
        description: '일부 데이터 업데이트에 실패했습니다.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const handleServiceUpdate = (_updatedServices: any[]) => {
    // 서비스 업데이트 시 쿼리 무효화하여 새로고침
    refreshServices()
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
            <HStack spacing={4} wrap="wrap">
              <Text color="gray.600" _dark={{ color: 'gray.400' }}>
                실시간 시스템 상태 및 서비스 모니터링
              </Text>
              <Badge 
                colorScheme={isConnected && newsConnected && gitConnected ? 'green' : 'yellow'} 
                variant="subtle"
              >
                {isConnected && newsConnected && gitConnected ? '실시간 연결됨' : '일부 연결 끊김'}
              </Badge>
              {unacknowledgedCount > 0 && (
                <Badge colorScheme="red" variant="solid">
                  미확인 알림 {unacknowledgedCount}개
                </Badge>
              )}
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
            isLoading={metricsLoading || servicesLoading || newsLoading || gitLoading || alertsLoading}
            loadingText="새로고침 중"
            size="sm"
            variant="outline"
          >
            새로고침
          </Button>
        </Flex>

        {/* 뉴스 상태 카드들 */}
        <Box>
          <Heading size="md" mb={4}>
            POSCO 뉴스 모니터링
          </Heading>
          <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={4}>
            {newsData.map((news) => (
              <GridItem key={news.type}>
                <NewsStatusCard
                  newsData={news}
                  isLoading={newsLoading}
                  error={newsError}
                />
              </GridItem>
            ))}
          </Grid>
        </Box>

        {/* 시스템 메트릭 카드들 */}
        <MetricsGrid
          metrics={metrics}
          isLoading={metricsLoading}
          error={metricsError || undefined}
          showTrends={true}
          compact={false}
        />

        {/* Git 상태와 최근 알림을 나란히 배치 */}
        <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={6}>
          <GridItem>
            <GitStatusWidget
              gitStatus={gitStatus}
              isLoading={gitLoading}
              error={gitError}
              onRefresh={refreshGitStatus}
            />
          </GridItem>
          <GridItem>
            <RecentAlertsWidget
              alerts={alerts}
              isLoading={alertsLoading}
              error={alertsError}
              maxItems={10}
              onRefresh={refreshAlerts}
              onAcknowledge={acknowledgeAlert}
              showAcknowledged={false}
            />
          </GridItem>
        </Grid>

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
              colorScheme={!servicesError ? 'green' : 'red'} 
              variant="subtle"
            >
              {!servicesError ? 'API 연결됨' : 'API 연결 끊김'}
            </Badge>
          </Flex>
          <ServiceStatusGrid
            services={services}
            onServiceUpdate={handleServiceUpdate}
            loading={servicesLoading}
            error={servicesError?.message}
          />
        </Box>
      </VStack>
    </Box>
  )
}

export default Dashboard
