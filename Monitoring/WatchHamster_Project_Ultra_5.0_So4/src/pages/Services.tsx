import React, { useState } from 'react'
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  VStack,
  HStack,
  Button,
  useToast,
  Flex,
  Spacer,
  Badge,
  Alert,
  AlertIcon,
  Spinner,
} from '@chakra-ui/react'
import { FiRefreshCw } from 'react-icons/fi'
import { useQuery } from '@tanstack/react-query'
import PoscoManagementPanel from '../components/Services/PoscoManagementPanel'
import WebhookManagement from '../components/Services/WebhookManagement'
import EnhancedServiceCard from '../components/Services/EnhancedServiceCard'
import ServiceLogViewer from '../components/Services/ServiceLogViewer'
import { apiService } from '../services/api'
import { ServiceInfo } from '../types'

const Services: React.FC = () => {
  const toast = useToast()
  const [selectedServiceForLogs, setSelectedServiceForLogs] = useState<{
    id: string
    name: string
  } | null>(null)

  // 실제 서비스 데이터 조회
  const {
    data: services = [],
    isLoading,
    error,
    refetch: refreshServices
  } = useQuery({
    queryKey: ['services'],
    queryFn: async () => {
      const response = await apiService.getServices()
      return response
    },
    refetchInterval: 10000, // 10초마다 새로고침
    retry: 3,
    retryDelay: 1000,
  })

  // 서비스 제어 함수
  const handleServiceAction = async (serviceId: string, action: 'start' | 'stop' | 'restart') => {
    try {
      let response
      switch (action) {
        case 'start':
          response = await apiService.startService(serviceId)
          break
        case 'stop':
          response = await apiService.stopService(serviceId)
          break
        case 'restart':
          response = await apiService.restartService(serviceId)
          break
      }

      toast({
        title: '서비스 제어 성공',
        description: response.message,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })

      // 서비스 목록 새로고침
      setTimeout(() => {
        refreshServices()
      }, 1000)

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '서비스 제어에 실패했습니다'
      toast({
        title: '서비스 제어 실패',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  // 로그 뷰어 열기
  const handleViewLogs = (serviceId: string) => {
    const service = services.find(s => s.id === serviceId)
    if (service) {
      setSelectedServiceForLogs({
        id: serviceId,
        name: service.name
      })
    }
  }

  // 전체 새로고침
  const handleRefreshAll = async () => {
    await refreshServices()
    toast({
      title: '서비스 목록 새로고침',
      description: '모든 서비스 상태를 업데이트했습니다.',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  // 서비스 상태 통계
  const serviceStats = {
    total: services.length,
    running: services.filter(s => s.status === 'running').length,
    stopped: services.filter(s => s.status === 'stopped').length,
    error: services.filter(s => s.status === 'error').length,
  }

  return (
    <Box className="fade-in">
      <VStack spacing={6} align="stretch">
        {/* 페이지 헤더 */}
        <Flex align="center" mb={6}>
          <Box>
            <Heading size="lg" mb={2}>
              서비스 관리
            </Heading>
            <HStack spacing={4} wrap="wrap">
              <Text color="gray.600" _dark={{ color: 'gray.400' }}>
                시스템 서비스의 상태를 확인하고 제어합니다
              </Text>
              <HStack spacing={2}>
                <Badge colorScheme="green" variant="subtle">
                  실행 중 {serviceStats.running}개
                </Badge>
                <Badge colorScheme="gray" variant="subtle">
                  중지됨 {serviceStats.stopped}개
                </Badge>
                {serviceStats.error > 0 && (
                  <Badge colorScheme="red" variant="subtle">
                    오류 {serviceStats.error}개
                  </Badge>
                )}
              </HStack>
            </HStack>
          </Box>
          <Spacer />
          <Button
            leftIcon={<FiRefreshCw />}
            onClick={handleRefreshAll}
            isLoading={isLoading}
            loadingText="새로고침 중"
            size="sm"
            variant="outline"
          >
            전체 새로고침
          </Button>
        </Flex>

        {/* 로딩 상태 */}
        {isLoading && services.length === 0 && (
          <VStack spacing={4} py={8}>
            <Spinner size="lg" />
            <Text>서비스 목록을 불러오는 중...</Text>
          </VStack>
        )}

        {/* 오류 상태 */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            <Box>
              <Text fontWeight="bold">서비스 목록을 불러오는데 실패했습니다</Text>
              <Text fontSize="sm">{error.message}</Text>
            </Box>
          </Alert>
        )}

        {/* 서비스 카드 그리드 */}
        {services.length > 0 && (
          <Grid templateColumns="repeat(auto-fit, minmax(400px, 1fr))" gap={6}>
            {services.map(service => (
              <GridItem key={service.id}>
                <EnhancedServiceCard
                  service={service}
                  onServiceAction={handleServiceAction}
                  onViewLogs={handleViewLogs}
                  isLoading={isLoading}
                />
              </GridItem>
            ))}
          </Grid>
        )}

        {/* 서비스가 없는 경우 */}
        {!isLoading && !error && services.length === 0 && (
          <VStack spacing={4} py={8}>
            <Text fontSize="lg" color="gray.500">
              등록된 서비스가 없습니다
            </Text>
            <Text fontSize="sm" color="gray.400">
              시스템에 서비스를 등록하면 여기에 표시됩니다
            </Text>
          </VStack>
        )}

        {/* POSCO 시스템 전용 관리 패널 */}
        <PoscoManagementPanel />

        {/* 웹훅 및 메시지 관리 */}
        <WebhookManagement />
      </VStack>

      {/* 서비스 로그 뷰어 */}
      {selectedServiceForLogs && (
        <ServiceLogViewer
          isOpen={!!selectedServiceForLogs}
          onClose={() => setSelectedServiceForLogs(null)}
          serviceId={selectedServiceForLogs.id}
          serviceName={selectedServiceForLogs.name}
        />
      )}
    </Box>
  )
}

export default Services
