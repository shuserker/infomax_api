import React, { useState, useEffect, useMemo } from 'react'
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Grid,
  GridItem,
  Select,
  Button,
  Badge,
  Flex,
  Spacer,
  IconButton,
  Tooltip,
  Switch,
  FormControl,
  FormLabel,
  useColorModeValue,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import {
  FiRefreshCw,
  FiTrendingUp,
  FiTrendingDown,
  FiActivity,
  FiCpu,
  FiHardDrive,
  FiZap,
  FiClock,
  FiBarChart3,
  FiPieChart
} from 'react-icons/fi'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

interface PerformanceMetric {
  timestamp: string
  cpu: number
  memory: number
  responseTime: number
  throughput: number
  errorRate: number
}

interface ServicePerformance {
  serviceId: string
  serviceName: string
  metrics: PerformanceMetric[]
  status: 'healthy' | 'warning' | 'critical'
}

interface PerformanceDashboardProps {
  services: any[]
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ services }) => {
  const [selectedService, setSelectedService] = useState('all')
  const [timeRange, setTimeRange] = useState('1h')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [performanceData, setPerformanceData] = useState<ServicePerformance[]>([])
  const [loading, setLoading] = useState(false)

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const chartBg = useColorModeValue('gray.50', 'gray.700')

  // 성능 데이터 생성 (실제 환경에서는 API에서 가져옴)
  const generatePerformanceData = useMemo(() => {
    const now = new Date()
    const hoursBack = timeRange === '1h' ? 1 : timeRange === '6h' ? 6 : 24
    const points = 60 // 1분마다 데이터 포인트
    
    return services.map(service => {
      const metrics: PerformanceMetric[] = []
      
      for (let i = points; i >= 0; i--) {
        const timestamp = new Date(now.getTime() - (i * hoursBack * 60000 / points))
        
        // 서비스별로 다른 패턴의 데이터 생성
        let baseCpu = 20
        let baseMemory = 40
        let baseResponseTime = 200
        
        if (service.id === 'api_server') {
          baseCpu = 35
          baseMemory = 60
          baseResponseTime = 150
        } else if (service.id === 'webhook_sender') {
          baseCpu = 15
          baseMemory = 30
          baseResponseTime = 100
        } else if (service.id === 'watchhamster_monitor') {
          baseCpu = 45
          baseMemory = 70
          baseResponseTime = 300
        }
        
        const variance = 0.3
        metrics.push({
          timestamp: timestamp.toISOString(),
          cpu: Math.max(0, Math.min(100, baseCpu + (Math.random() - 0.5) * baseCpu * variance)),
          memory: Math.max(0, Math.min(100, baseMemory + (Math.random() - 0.5) * baseMemory * variance)),
          responseTime: Math.max(0, baseResponseTime + (Math.random() - 0.5) * baseResponseTime * variance),
          throughput: Math.max(0, 50 + (Math.random() - 0.5) * 40),
          errorRate: Math.max(0, Math.min(10, 1 + (Math.random() - 0.5) * 2))
        })
      }
      
      // 서비스 상태 결정
      const avgCpu = metrics.reduce((sum, m) => sum + m.cpu, 0) / metrics.length
      const avgErrorRate = metrics.reduce((sum, m) => sum + m.errorRate, 0) / metrics.length
      
      let status: ServicePerformance['status'] = 'healthy'
      if (avgCpu > 80 || avgErrorRate > 5) {
        status = 'critical'
      } else if (avgCpu > 60 || avgErrorRate > 2) {
        status = 'warning'
      }
      
      return {
        serviceId: service.id,
        serviceName: service.name || service.display_name,
        metrics,
        status
      }
    })
  }, [services, timeRange])

  // 데이터 로드
  const loadData = async () => {
    setLoading(true)
    // 실제 API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 800))
    setPerformanceData(generatePerformanceData)
    setLoading(false)
  }

  // 자동 새로고침
  useEffect(() => {
    loadData()
    
    if (autoRefresh) {
      const interval = setInterval(loadData, 30000) // 30초마다 새로고침
      return () => clearInterval(interval)
    }
  }, [autoRefresh, generatePerformanceData])

  // 선택된 서비스 데이터
  const selectedData = useMemo(() => {
    if (selectedService === 'all') {
      // 전체 서비스의 평균 계산
      if (performanceData.length === 0) return []
      
      const allMetrics = performanceData[0].metrics.map((_, index) => {
        const timestamp = performanceData[0].metrics[index].timestamp
        const avgCpu = performanceData.reduce((sum, service) => sum + service.metrics[index].cpu, 0) / performanceData.length
        const avgMemory = performanceData.reduce((sum, service) => sum + service.metrics[index].memory, 0) / performanceData.length
        const avgResponseTime = performanceData.reduce((sum, service) => sum + service.metrics[index].responseTime, 0) / performanceData.length
        const avgThroughput = performanceData.reduce((sum, service) => sum + service.metrics[index].throughput, 0) / performanceData.length
        const avgErrorRate = performanceData.reduce((sum, service) => sum + service.metrics[index].errorRate, 0) / performanceData.length
        
        return {
          timestamp,
          cpu: avgCpu,
          memory: avgMemory,
          responseTime: avgResponseTime,
          throughput: avgThroughput,
          errorRate: avgErrorRate,
          time: new Date(timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
        }
      })
      
      return avgMetrics
    } else {
      const service = performanceData.find(s => s.serviceId === selectedService)
      return service ? service.metrics.map(m => ({
        ...m,
        time: new Date(m.timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
      })) : []
    }
  }, [performanceData, selectedService])

  // 서비스 상태별 분포 데이터
  const statusDistribution = useMemo(() => {
    const distribution = performanceData.reduce((acc, service) => {
      acc[service.status] = (acc[service.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    return Object.entries(distribution).map(([status, count]) => ({
      name: status === 'healthy' ? '정상' : status === 'warning' ? '주의' : '위험',
      value: count,
      color: status === 'healthy' ? '#00C49F' : status === 'warning' ? '#FFBB28' : '#FF8042'
    }))
  }, [performanceData])

  // 현재 평균 메트릭
  const currentMetrics = useMemo(() => {
    if (selectedData.length === 0) return null
    
    const latest = selectedData[selectedData.length - 1]
    const previous = selectedData[selectedData.length - 2] || latest
    
    return {
      cpu: {
        value: latest.cpu.toFixed(1),
        trend: latest.cpu > previous.cpu ? 'up' : latest.cpu < previous.cpu ? 'down' : 'stable',
        change: Math.abs(latest.cpu - previous.cpu).toFixed(1)
      },
      memory: {
        value: latest.memory.toFixed(1),
        trend: latest.memory > previous.memory ? 'up' : latest.memory < previous.memory ? 'down' : 'stable',
        change: Math.abs(latest.memory - previous.memory).toFixed(1)
      },
      responseTime: {
        value: latest.responseTime.toFixed(0),
        trend: latest.responseTime > previous.responseTime ? 'up' : latest.responseTime < previous.responseTime ? 'down' : 'stable',
        change: Math.abs(latest.responseTime - previous.responseTime).toFixed(0)
      },
      errorRate: {
        value: latest.errorRate.toFixed(2),
        trend: latest.errorRate > previous.errorRate ? 'up' : latest.errorRate < previous.errorRate ? 'down' : 'stable',
        change: Math.abs(latest.errorRate - previous.errorRate).toFixed(2)
      }
    }
  }, [selectedData])

  const formatXAxisTick = (tickItem: string) => {
    return tickItem
  }

  return (
    <Card>
      <CardHeader>
        <Flex justify="space-between" align="center" wrap="wrap" gap={4}>
          <VStack spacing={1} align="start">
            <Heading size="md">성능 대시보드</Heading>
            <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.400" }}>
              실시간 서비스 성능 모니터링 및 트렌드 분석
            </Text>
          </VStack>

          <HStack spacing={4}>
            <FormControl display="flex" alignItems="center">
              <FormLabel fontSize="sm" mb={0} mr={2}>자동 새로고침</FormLabel>
              <Switch size="sm" isChecked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />
            </FormControl>

            <Select size="sm" w="120px" value={selectedService} onChange={(e) => setSelectedService(e.target.value)}>
              <option value="all">전체 서비스</option>
              {services.map(service => (
                <option key={service.id} value={service.id}>
                  {service.name || service.display_name}
                </option>
              ))}
            </Select>

            <Select size="sm" w="100px" value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
              <option value="1h">1시간</option>
              <option value="6h">6시간</option>
              <option value="24h">24시간</option>
            </Select>

            <Tooltip label="새로고침">
              <IconButton
                aria-label="새로고침"
                icon={<FiRefreshCw />}
                size="sm"
                onClick={loadData}
                isLoading={loading}
              />
            </Tooltip>
          </HStack>
        </Flex>
      </CardHeader>

      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 현재 메트릭 요약 */}
          {currentMetrics && (
            <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
              <Card size="sm" bg={chartBg}>
                <CardBody>
                  <HStack justify="space-between">
                    <VStack spacing={1} align="start">
                      <HStack>
                        <FiCpu size={16} />
                        <Text fontSize="sm" color="gray.600">CPU 사용률</Text>
                      </HStack>
                      <HStack>
                        <Text fontSize="2xl" fontWeight="bold">{currentMetrics.cpu.value}%</Text>
                        <Badge 
                          size="sm" 
                          colorScheme={currentMetrics.cpu.trend === 'up' ? 'red' : currentMetrics.cpu.trend === 'down' ? 'green' : 'gray'}
                        >
                          {currentMetrics.cpu.trend === 'up' && <FiTrendingUp />}
                          {currentMetrics.cpu.trend === 'down' && <FiTrendingDown />}
                          {currentMetrics.cpu.change}%
                        </Badge>
                      </HStack>
                    </VStack>
                  </HStack>
                </CardBody>
              </Card>

              <Card size="sm" bg={chartBg}>
                <CardBody>
                  <HStack justify="space-between">
                    <VStack spacing={1} align="start">
                      <HStack>
                        <FiHardDrive size={16} />
                        <Text fontSize="sm" color="gray.600">메모리 사용률</Text>
                      </HStack>
                      <HStack>
                        <Text fontSize="2xl" fontWeight="bold">{currentMetrics.memory.value}%</Text>
                        <Badge 
                          size="sm" 
                          colorScheme={currentMetrics.memory.trend === 'up' ? 'red' : currentMetrics.memory.trend === 'down' ? 'green' : 'gray'}
                        >
                          {currentMetrics.memory.trend === 'up' && <FiTrendingUp />}
                          {currentMetrics.memory.trend === 'down' && <FiTrendingDown />}
                          {currentMetrics.memory.change}%
                        </Badge>
                      </HStack>
                    </VStack>
                  </HStack>
                </CardBody>
              </Card>

              <Card size="sm" bg={chartBg}>
                <CardBody>
                  <HStack justify="space-between">
                    <VStack spacing={1} align="start">
                      <HStack>
                        <FiClock size={16} />
                        <Text fontSize="sm" color="gray.600">응답 시간</Text>
                      </HStack>
                      <HStack>
                        <Text fontSize="2xl" fontWeight="bold">{currentMetrics.responseTime.value}ms</Text>
                        <Badge 
                          size="sm" 
                          colorScheme={currentMetrics.responseTime.trend === 'up' ? 'red' : currentMetrics.responseTime.trend === 'down' ? 'green' : 'gray'}
                        >
                          {currentMetrics.responseTime.trend === 'up' && <FiTrendingUp />}
                          {currentMetrics.responseTime.trend === 'down' && <FiTrendingDown />}
                          {currentMetrics.responseTime.change}ms
                        </Badge>
                      </HStack>
                    </VStack>
                  </HStack>
                </CardBody>
              </Card>

              <Card size="sm" bg={chartBg}>
                <CardBody>
                  <HStack justify="space-between">
                    <VStack spacing={1} align="start">
                      <HStack>
                        <FiZap size={16} />
                        <Text fontSize="sm" color="gray.600">오류율</Text>
                      </HStack>
                      <HStack>
                        <Text fontSize="2xl" fontWeight="bold">{currentMetrics.errorRate.value}%</Text>
                        <Badge 
                          size="sm" 
                          colorScheme={currentMetrics.errorRate.trend === 'up' ? 'red' : currentMetrics.errorRate.trend === 'down' ? 'green' : 'gray'}
                        >
                          {currentMetrics.errorRate.trend === 'up' && <FiTrendingUp />}
                          {currentMetrics.errorRate.trend === 'down' && <FiTrendingDown />}
                          {currentMetrics.errorRate.change}%
                        </Badge>
                      </HStack>
                    </VStack>
                  </HStack>
                </CardBody>
              </Card>
            </Grid>
          )}

          {/* 차트 섹션 */}
          <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
            {/* 메인 성능 차트 */}
            <Card>
              <CardHeader>
                <HStack>
                  <FiBarChart3 />
                  <Heading size="sm">시간별 성능 트렌드</Heading>
                </HStack>
              </CardHeader>
              <CardBody>
                <Box h="300px">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={selectedData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="time" 
                        tickFormatter={formatXAxisTick}
                        interval="preserveStartEnd"
                      />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <RechartsTooltip />
                      <Area 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="cpu" 
                        stroke="#8884d8" 
                        fill="#8884d8" 
                        fillOpacity={0.3}
                        name="CPU (%)"
                      />
                      <Area 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="memory" 
                        stroke="#82ca9d" 
                        fill="#82ca9d" 
                        fillOpacity={0.3}
                        name="메모리 (%)"
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="responseTime" 
                        stroke="#ff7300" 
                        name="응답시간 (ms)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </CardBody>
            </Card>

            {/* 서비스 상태 분포 */}
            <Card>
              <CardHeader>
                <HStack>
                  <FiPieChart />
                  <Heading size="sm">서비스 상태 분포</Heading>
                </HStack>
              </CardHeader>
              <CardBody>
                <Box h="300px">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {statusDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
                <VStack spacing={2} mt={4}>
                  {statusDistribution.map((entry, index) => (
                    <HStack key={index} justify="space-between" w="full">
                      <HStack>
                        <Box w="12px" h="12px" bg={entry.color} borderRadius="sm" />
                        <Text fontSize="sm">{entry.name}</Text>
                      </HStack>
                      <Text fontSize="sm" fontWeight="semibold">{entry.value}개</Text>
                    </HStack>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </Grid>

          {/* 경고 및 알림 */}
          {performanceData.some(s => s.status === 'critical') && (
            <Alert status="error">
              <AlertIcon />
              <Box>
                <Text fontWeight="bold">성능 이슈 감지!</Text>
                <Text fontSize="sm">
                  {performanceData.filter(s => s.status === 'critical').length}개 서비스에서 
                  성능 문제가 감지되었습니다. 즉시 확인이 필요합니다.
                </Text>
              </Box>
            </Alert>
          )}

          {performanceData.some(s => s.status === 'warning') && !performanceData.some(s => s.status === 'critical') && (
            <Alert status="warning">
              <AlertIcon />
              <Box>
                <Text fontWeight="bold">성능 주의</Text>
                <Text fontSize="sm">
                  {performanceData.filter(s => s.status === 'warning').length}개 서비스에서 
                  성능 저하가 감지되었습니다.
                </Text>
              </Box>
            </Alert>
          )}
        </VStack>
      </CardBody>
    </Card>
  )
}

export default PerformanceDashboard
