import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Card,
  CardHeader,
  CardBody,
  HStack,
  Badge,
  Grid,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Button,
  IconButton,
  Tooltip,
  Divider,
  Alert,
  AlertIcon,
  Switch,
  FormControl,
  FormLabel,
  useColorModeValue,
  Circle
} from '@chakra-ui/react'
import {
  FiRefreshCw,
  FiSend,
  FiFileText,
  FiActivity,
  FiCheckCircle,
  FiTrendingUp,
  FiSettings,
  FiZap
} from 'react-icons/fi'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Area,
  AreaChart
} from 'recharts'

const Services: React.FC = () => {
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [autoRefresh, setAutoRefresh] = useState(true)
  
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const successColor = useColorModeValue('green.500', 'green.300')
  const warningColor = useColorModeValue('orange.500', 'orange.300')

  // 운영 데이터 (실제 API에서 가져올 예정)
  const systemData = {
    newsMonitoring: {
      todayChanges: 15,
      lastCheck: '30초 전',
      avgInterval: 60,
      trend: '+25%',
      errors: 0,
      status: 'active'
    },
    webhookDelivery: {
      todaySuccess: 127,
      todayFailed: 3,
      successRate: 97.7,
      avgResponseTime: 245,
      lastSent: '2분 전',
      retrySuccessRate: 100
    },
    systemHealth: {
      overallUptime: 99.8,
      continuousUptime: '15일 3시간',
      avgApiResponse: 150,
      systemLoad: {
        cpu: 45,
        memory: 68,
        status: 'normal'
      }
    },
    services: {
      watchhamster_monitor: { status: 'running', enabled: true },
      webhook_sender: { status: 'running', enabled: true },
      infomax_client: { status: 'running', enabled: true },
      auto_backup: { status: 'running', enabled: false }
    }
  }

  // 차트용 데이터
  const chartData = {
    newsMonitoring: [
      { day: '월', value: 12, label: '월요일' },
      { day: '화', value: 19, value2: 15, label: '화요일' },
      { day: '수', value: 18, value2: 22, label: '수요일' },
      { day: '목', value: 25, value2: 18, label: '목요일' },
      { day: '금', value: 22, value2: 25, label: '금요일' },
      { day: '토', value: 8, value2: 12, label: '토요일' },
      { day: '일', value: 15, value2: 10, label: '일요일' },
    ],
    successRate: [
      { day: '월', rate: 98.5, label: '월요일' },
      { day: '화', rate: 99.2, label: '화요일' },
      { day: '수', rate: 95.2, label: '수요일' },
      { day: '목', rate: 97.8, label: '목요일' },
      { day: '금', rate: 99.5, label: '금요일' },
      { day: '토', rate: 98.1, label: '토요일' },
      { day: '일', rate: 97.7, label: '일요일' },
    ],
    responseTime: [
      { day: '월', time: 180, label: '월요일' },
      { day: '화', time: 165, label: '화요일' },
      { day: '수', time: 220, label: '수요일' },
      { day: '목', time: 320, label: '목요일' },
      { day: '금', time: 190, label: '금요일' },
      { day: '토', time: 175, label: '토요일' },
      { day: '일', time: 245, label: '일요일' },
    ]
  }

  // 자동 새로고침
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        setLastUpdate(new Date())
        // 여기서 실제 데이터를 새로고침할 예정
      }, 30000) // 30초마다

      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const handleManualRefresh = () => {
    setLastUpdate(new Date())
    // 수동 데이터 새로고침 로직
  }

  const handleServiceToggle = (serviceKey: string, enabled: boolean) => {
    // 서비스 ON/OFF 토글 로직
    console.log(`${serviceKey}: ${enabled ? 'ON' : 'OFF'}`)
  }

  const handleManualAction = (action: string) => {
    // 수동 액션 실행 로직
    console.log(`Manual action: ${action}`)
  }

  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        {/* 페이지 헤더 */}
        <Box>
          <HStack justify="space-between" align="start">
            <VStack spacing={2} align="start">
              <Heading size="lg" color="blue.600" _dark={{ color: "blue.300" }}>
                🔧 POSCO 서비스 관리
              </Heading>
              <Text color="gray.600" _dark={{ color: "gray.400" }}>
                WatchHamster v3.0 실시간 운영 대시보드
              </Text>
              <HStack spacing={4} fontSize="sm" color="gray.500">
                <Text>마지막 업데이트: {lastUpdate.toLocaleTimeString('ko-KR')}</Text>
                <Badge colorScheme="green" variant="subtle">실시간 연동</Badge>
              </HStack>
            </VStack>
            
            <HStack spacing={3}>
              <FormControl display="flex" alignItems="center">
                <FormLabel fontSize="sm" mb={0} mr={2}>자동 새로고침</FormLabel>
                <Switch 
                  size="sm" 
                  isChecked={autoRefresh} 
                  onChange={(e) => setAutoRefresh(e.target.checked)} 
                />
              </FormControl>
              
              <Tooltip label="수동 새로고침">
                <IconButton
                  aria-label="새로고침"
                  icon={<FiRefreshCw />}
                  size="sm"
                  onClick={handleManualRefresh}
                />
              </Tooltip>
            </HStack>
          </HStack>
        </Box>

        {/* 서비스 생태계 맵 */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack>
              <FiActivity size={20} />
              <Heading size="md">🗺️ 서비스 생태계</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <HStack spacing={8} justify="center" align="center" py={4}>
              <VStack spacing={2}>
                <Circle size="80px" bg="blue.100" _dark={{ bg: "blue.900" }}>
                  <FiFileText size={32} color="blue" />
                </Circle>
                <Text fontSize="sm" fontWeight="semibold">POSCO 뉴스</Text>
                <Badge size="sm" colorScheme="blue">외부 소스</Badge>
              </VStack>
              
              <Text fontSize="2xl" color="gray.400">→</Text>
              
              <VStack spacing={2}>
                <Circle size="80px" bg="green.100" _dark={{ bg: "green.900" }}>
                  <FiActivity size={32} color="green" />
                </Circle>
                <Text fontSize="sm" fontWeight="semibold">WatchHamster</Text>
                <Badge size="sm" colorScheme="green">모니터링</Badge>
              </VStack>
              
              <Text fontSize="2xl" color="gray.400">→</Text>
              
              <VStack spacing={2}>
                <Circle size="80px" bg="purple.100" _dark={{ bg: "purple.900" }}>
                  <FiSend size={32} color="purple" />
                </Circle>
                <Text fontSize="sm" fontWeight="semibold">Dooray 웹훅</Text>
                <Badge size="sm" colorScheme="purple">알림</Badge>
              </VStack>
              
              <Box>
                <Text fontSize="xl" color="gray.400">↓</Text>
                <VStack spacing={2} mt={4}>
                  <Circle size="60px" bg="orange.100" _dark={{ bg: "orange.900" }}>
                    <FiZap size={24} color="orange" />
                  </Circle>
                  <Text fontSize="sm" fontWeight="semibold">InfoMax API</Text>
                  <Badge size="sm" colorScheme="orange">데이터</Badge>
                </VStack>
              </Box>
            </HStack>
          </CardBody>
        </Card>

        {/* 핵심 운영 현황 */}
        <Grid templateColumns={{ base: "1fr", lg: "repeat(3, 1fr)" }} gap={6}>
          
          {/* 뉴스 모니터링 현황 */}
          <Card bg={bgColor} borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <FiFileText size={20} />
                <VStack spacing={1} align="start">
                  <Heading size="md">📰 뉴스 모니터링</Heading>
                  <Text fontSize="sm" color="gray.500">POSCO 뉴스 변경사항 감지</Text>
                </VStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <Stat>
                  <StatLabel>오늘 감지된 변경</StatLabel>
                  <StatNumber color="blue.500">{systemData.newsMonitoring.todayChanges}건</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    전일 대비 {systemData.newsMonitoring.trend}
                  </StatHelpText>
                </Stat>
                
                <Divider />
                
                <VStack spacing={3}>
                  <HStack justify="space-between" w="full">
                    <Text fontSize="sm" color="gray.600">마지막 체크</Text>
                    <Badge colorScheme="green">{systemData.newsMonitoring.lastCheck}</Badge>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text fontSize="sm" color="gray.600">평균 체크 간격</Text>
                    <Text fontSize="sm" fontWeight="bold">{systemData.newsMonitoring.avgInterval}초</Text>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text fontSize="sm" color="gray.600">오류 발생</Text>
                    <Badge colorScheme={systemData.newsMonitoring.errors > 0 ? "red" : "green"}>
                      {systemData.newsMonitoring.errors}건
                    </Badge>
                  </HStack>
                </VStack>

                <Button 
                  size="sm" 
                  leftIcon={<FiRefreshCw />} 
                  colorScheme="blue" 
                  variant="outline"
                  onClick={() => handleManualAction('manual_news_check')}
                >
                  수동 체크 실행
                </Button>
              </VStack>
            </CardBody>
          </Card>

          {/* 웹훅 발송 성과 */}
          <Card bg={bgColor} borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <FiSend size={20} />
                <VStack spacing={1} align="start">
                  <Heading size="md">📊 웹훅 발송</Heading>
                  <Text fontSize="sm" color="gray.500">Dooray 알림 발송 성과</Text>
                </VStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <Grid templateColumns="1fr 1fr" gap={4}>
                  <Stat>
                    <StatLabel fontSize="xs">성공</StatLabel>
                    <StatNumber color="green.500" fontSize="lg">{systemData.webhookDelivery.todaySuccess}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel fontSize="xs">실패</StatLabel>
                    <StatNumber color="red.500" fontSize="lg">{systemData.webhookDelivery.todayFailed}</StatNumber>
                  </Stat>
                </Grid>
                
                <Box>
                  <HStack justify="space-between">
                    <Text fontSize="sm" color="gray.600">성공률</Text>
                    <Text fontSize="lg" fontWeight="bold" color={successColor}>
                      {systemData.webhookDelivery.successRate}%
                    </Text>
                  </HStack>
                  <Progress 
                    value={systemData.webhookDelivery.successRate} 
                    colorScheme="green" 
                    size="sm"
                    borderRadius="full"
                    mt={2}
                  />
                </Box>
                
                <VStack spacing={2}>
                  <HStack justify="space-between" w="full">
                    <Text fontSize="sm" color="gray.600">평균 응답시간</Text>
                    <Text fontSize="sm" fontWeight="bold">{systemData.webhookDelivery.avgResponseTime}ms</Text>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text fontSize="sm" color="gray.600">마지막 발송</Text>
                    <Badge colorScheme="green">{systemData.webhookDelivery.lastSent}</Badge>
                  </HStack>
                </VStack>

                <Button 
                  size="sm" 
                  leftIcon={<FiSend />} 
                  colorScheme="purple" 
                  variant="outline"
                  onClick={() => handleManualAction('test_webhook')}
                >
                  테스트 웹훅 발송
                </Button>
              </VStack>
            </CardBody>
          </Card>

          {/* 시스템 안정성 */}
          <Card bg={bgColor} borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <FiCheckCircle size={20} />
                <VStack spacing={1} align="start">
                  <Heading size="md">💚 시스템 안정성</Heading>
                  <Text fontSize="sm" color="gray.500">전체 시스템 헬스 현황</Text>
                </VStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <Stat>
                  <StatLabel>전체 가용성</StatLabel>
                  <StatNumber color="green.500">{systemData.systemHealth.overallUptime}%</StatNumber>
                  <StatHelpText>
                    <FiTrendingUp />
                    우수 등급
                  </StatHelpText>
                </Stat>
                
                <VStack spacing={3}>
                  <HStack justify="space-between" w="full">
                    <Text fontSize="sm" color="gray.600">연속 가동시간</Text>
                    <Badge colorScheme="green">{systemData.systemHealth.continuousUptime}</Badge>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text fontSize="sm" color="gray.600">API 평균 응답</Text>
                    <Text fontSize="sm" fontWeight="bold">{systemData.systemHealth.avgApiResponse}ms</Text>
                  </HStack>
                </VStack>

                <Box>
                  <Text fontSize="sm" color="gray.600" mb={2}>시스템 부하</Text>
                  <VStack spacing={2}>
                    <HStack justify="space-between" w="full">
                      <Text fontSize="xs">CPU</Text>
                      <Text fontSize="xs">{systemData.systemHealth.systemLoad.cpu}%</Text>
                    </HStack>
                    <Progress 
                      value={systemData.systemHealth.systemLoad.cpu} 
                      colorScheme="blue" 
                      size="xs"
                      borderRadius="full"
                    />
                    <HStack justify="space-between" w="full">
                      <Text fontSize="xs">메모리</Text>
                      <Text fontSize="xs">{systemData.systemHealth.systemLoad.memory}%</Text>
                    </HStack>
                    <Progress 
                      value={systemData.systemHealth.systemLoad.memory} 
                      colorScheme="blue" 
                      size="xs"
                      borderRadius="full"
                    />
                  </VStack>
                </Box>

                <Button 
                  size="sm" 
                  leftIcon={<FiActivity />} 
                  colorScheme="green" 
                  variant="outline"
                  onClick={() => handleManualAction('system_health_check')}
                >
                  헬스체크 실행
                </Button>
              </VStack>
            </CardBody>
          </Card>
        </Grid>

        {/* 서비스 제어 패널 */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack>
              <FiSettings size={20} />
              <Heading size="md">🎛️ 서비스 제어 패널</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
              {Object.entries(systemData.services).map(([key, service]) => (
                <HStack key={key} justify="space-between" p={3} borderRadius="md" bg="gray.50" _dark={{ bg: "gray.700" }}>
                  <HStack>
                    <Circle size="8px" bg={service.status === 'running' ? 'green.500' : 'red.500'} />
                    <Text fontSize="sm" fontWeight="semibold">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Text>
                    <Badge size="sm" colorScheme={service.status === 'running' ? 'green' : 'red'}>
                      {service.status === 'running' ? '실행중' : '중지됨'}
                    </Badge>
                  </HStack>
                  <Switch 
                    size="sm"
                    isChecked={service.enabled}
                    onChange={(e) => handleServiceToggle(key, e.target.checked)}
                  />
                </HStack>
              ))}
            </Grid>
          </CardBody>
        </Card>

        {/* Phase 2: 실시간 알림 센터 & 트렌드 차트 */}
        <Grid templateColumns={{ base: "1fr", lg: "1fr 2fr" }} gap={6}>
          
          {/* 실시간 알림 센터 */}
          <Card bg={bgColor} borderColor={borderColor}>
            <CardHeader>
              <HStack>
                <FiActivity size={20} />
                <VStack spacing={1} align="start">
                  <Heading size="md">🚨 실시간 알림</Heading>
                  <Text fontSize="sm" color="gray.500">시스템 이벤트 및 알림</Text>
                </VStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                {/* 긴급 알림 */}
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" fontWeight="bold" color="red.600">🔴 긴급</Text>
                    <Badge colorScheme="red" variant="solid">0</Badge>
                  </HStack>
                  <Text fontSize="xs" color="gray.500">긴급한 문제가 없습니다</Text>
                </Box>

                <Divider />

                {/* 주의 알림 */}
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" fontWeight="bold" color="orange.600">🟡 주의</Text>
                    <Badge colorScheme="orange" variant="solid">3</Badge>
                  </HStack>
                  <VStack spacing={2} align="stretch">
                    <Box p={2} bg="orange.50" _dark={{ bg: "orange.900" }} borderRadius="md">
                      <Text fontSize="xs" fontWeight="semibold">InfoMax API 응답시간 증가</Text>
                      <Text fontSize="xs" color="gray.600">250ms → 320ms (5분 전)</Text>
                    </Box>
                    <Box p={2} bg="orange.50" _dark={{ bg: "orange.900" }} borderRadius="md">
                      <Text fontSize="xs" fontWeight="semibold">웹훅 재시도 3회 연속</Text>
                      <Text fontSize="xs" color="gray.600">Dooray 서버 불안정 (12분 전)</Text>
                    </Box>
                    <Box p={2} bg="orange.50" _dark={{ bg: "orange.900" }} borderRadius="md">
                      <Text fontSize="xs" fontWeight="semibold">메모리 사용량 증가</Text>
                      <Text fontSize="xs" color="gray.600">2.1GB → 2.8GB (18분 전)</Text>
                    </Box>
                  </VStack>
                </Box>

                <Divider />

                {/* 정보 알림 */}
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" fontWeight="bold" color="blue.600">🟢 정보</Text>
                    <Badge colorScheme="blue" variant="solid">5</Badge>
                  </HStack>
                  <VStack spacing={1} align="stretch">
                    <Text fontSize="xs" color="gray.600">• 오늘 뉴스 체크 1,440회 완료</Text>
                    <Text fontSize="xs" color="gray.600">• 자동 백업 성공 (03:00)</Text>
                    <Text fontSize="xs" color="gray.600">• 시스템 재시작 후 15일 경과</Text>
                    <Text fontSize="xs" color="gray.600">• 웹훅 발송 기록 신규 최고</Text>
                    <Text fontSize="xs" color="gray.600">• API 응답 성능 평균 이하</Text>
                  </VStack>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* 성능 트렌드 차트 */}
          <Card bg={bgColor} borderColor={borderColor}>
            <CardHeader>
              <HStack justify="space-between">
                <HStack>
                  <FiTrendingUp size={20} />
                  <VStack spacing={1} align="start">
                    <Heading size="md">📈 성능 트렌드</Heading>
                    <Text fontSize="sm" color="gray.500">최근 7일 운영 성과</Text>
                  </VStack>
                </HStack>
                <HStack spacing={2}>
                  <Badge colorScheme="blue" variant="outline">뉴스 감지</Badge>
                  <Badge colorScheme="green" variant="outline">성공률</Badge>
                  <Badge colorScheme="purple" variant="outline">응답시간</Badge>
                </HStack>
              </HStack>
            </CardHeader>
            <CardBody>
              {/* 실제 recharts 차트 */}
              <VStack spacing={6} align="stretch">
                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={3}>📰 뉴스 모니터링 트렌드 (일간 감지량)</Text>
                  <Box height="200px">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData.newsMonitoring} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis 
                          dataKey="day" 
                          axisLine={false}
                          tickLine={false}
                          fontSize={12}
                          stroke="#718096"
                        />
                        <YAxis 
                          axisLine={false}
                          tickLine={false}
                          fontSize={12}
                          stroke="#718096"
                        />
                        <RechartsTooltip 
                          contentStyle={{
                            backgroundColor: 'white',
                            border: '1px solid #E2E8F0',
                            borderRadius: '8px',
                            fontSize: '12px'
                          }}
                          labelFormatter={(label) => `${label}요일`}
                          formatter={(value) => [`${value}건`, '감지량']}
                        />
                        <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                  <HStack justify="space-between" mt={2} fontSize="xs" color="gray.600">
                    <Text>평균: 18.2건/일</Text>
                    <Text>최고: 25건 (금요일)</Text>
                    <Text>트렌드: ↗️ +15%</Text>
                  </HStack>
                </Box>

                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={3}>🎯 웹훅 성공률 트렌드</Text>
                  <Box height="200px">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartData.successRate} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis 
                          dataKey="day" 
                          axisLine={false}
                          tickLine={false}
                          fontSize={12}
                          stroke="#718096"
                        />
                        <YAxis 
                          domain={[85, 100]}
                          axisLine={false}
                          tickLine={false}
                          fontSize={12}
                          stroke="#718096"
                          tickFormatter={(value) => `${value}%`}
                        />
                        <RechartsTooltip 
                          contentStyle={{
                            backgroundColor: 'white',
                            border: '1px solid #E2E8F0',
                            borderRadius: '8px',
                            fontSize: '12px'
                          }}
                          labelFormatter={(label) => `${label}요일`}
                          formatter={(value) => [`${value}%`, '성공률']}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="rate" 
                          stroke="#22C55E" 
                          fill="#22C55E" 
                          fillOpacity={0.3}
                          strokeWidth={3}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Box>
                  <HStack justify="space-between" mt={2} fontSize="xs" color="gray.600">
                    <Text>평균: 98.1%</Text>
                    <Text>최저: 95.2% (수요일)</Text>
                    <Text>안정성: 🔥 매우우수</Text>
                  </HStack>
                </Box>

                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={3}>⚡ 평균 응답시간 트렌드 (ms)</Text>
                  <Box height="200px">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData.responseTime} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis 
                          dataKey="day" 
                          axisLine={false}
                          tickLine={false}
                          fontSize={12}
                          stroke="#718096"
                        />
                        <YAxis 
                          axisLine={false}
                          tickLine={false}
                          fontSize={12}
                          stroke="#718096"
                          tickFormatter={(value) => `${value}ms`}
                        />
                        <RechartsTooltip 
                          contentStyle={{
                            backgroundColor: 'white',
                            border: '1px solid #E2E8F0',
                            borderRadius: '8px',
                            fontSize: '12px'
                          }}
                          labelFormatter={(label) => `${label}요일`}
                          formatter={(value) => [`${value}ms`, '응답시간']}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="time" 
                          stroke="#8B5CF6" 
                          strokeWidth={3}
                          dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6, stroke: '#8B5CF6', strokeWidth: 2 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                  <HStack justify="space-between" mt={2} fontSize="xs" color="gray.600">
                    <Text>평균: 185ms</Text>
                    <Text>최고: 320ms (목요일)</Text>
                    <Text>개선: ↘️ -12ms</Text>
                  </HStack>
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </Grid>

        {/* Phase 3: 상세 로그 뷰어 */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <HStack>
                <FiActivity size={20} />
                <VStack spacing={1} align="start">
                  <Heading size="md">🔍 실시간 활동 로그</Heading>
                  <Text fontSize="sm" color="gray.500">최근 시스템 이벤트 및 상세 로그</Text>
                </VStack>
              </HStack>
              <HStack spacing={2}>
                <Button size="xs" variant="outline" colorScheme="blue">전체보기</Button>
                <Button size="xs" variant="outline" colorScheme="green">필터</Button>
                <IconButton
                  aria-label="로그 새로고침"
                  icon={<FiRefreshCw />}
                  size="xs"
                />
              </HStack>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={2} align="stretch" maxH="300px" overflowY="auto">
              {/* 실시간 로그 엔트리들 */}
              {[
                { time: '18:33:15', type: 'SUCCESS', icon: '✅', message: '뉴스 모니터링 체크 완료 - 변경사항 0건', source: 'watchhamster.monitor' },
                { time: '18:32:47', type: 'INFO', icon: '📤', message: 'Dooray 웹훅 발송 성공 (응답시간: 234ms)', source: 'webhook.sender' },
                { time: '18:32:23', type: 'INFO', icon: '🔄', message: 'InfoMax API 호출 성공 (환율 데이터 업데이트)', source: 'infomax.client' },
                { time: '18:31:58', type: 'SUCCESS', icon: '✅', message: '뉴스 모니터링 체크 완료 - 변경사항 1건 감지', source: 'watchhamster.monitor' },
                { time: '18:31:45', type: 'WARNING', icon: '⚠️', message: 'API 응답시간 증가 감지 (245ms → 312ms)', source: 'health.monitor' },
                { time: '18:30:33', type: 'INFO', icon: '🔧', message: '시스템 헬스체크 완료 - 모든 서비스 정상', source: 'system.health' },
                { time: '18:30:15', type: 'SUCCESS', icon: '✅', message: '뉴스 모니터링 체크 완료 - 변경사항 0건', source: 'watchhamster.monitor' },
                { time: '18:29:52', type: 'INFO', icon: '📤', message: 'Dooray 웹훅 발송 성공 (응답시간: 189ms)', source: 'webhook.sender' },
                { time: '18:29:18', type: 'SUCCESS', icon: '🎯', message: '수동 뉴스 체크 실행됨 - 변경사항 2건 감지', source: 'watchhamster.manual' },
                { time: '18:28:44', type: 'INFO', icon: '💾', message: '캐시 정리 작업 완료 (152MB 정리됨)', source: 'system.cache' },
              ].map((log, index) => (
                <HStack key={index} spacing={3} p={2} borderRadius="sm" _hover={{ bg: "gray.50", _dark: { bg: "gray.700" } }}>
                  <Text fontSize="xs" fontFamily="monospace" color="gray.500" minW="60px">
                    {log.time}
                  </Text>
                  <Text fontSize="sm" minW="20px">
                    {log.icon}
                  </Text>
                  <Badge 
                    size="sm" 
                    colorScheme={
                      log.type === 'SUCCESS' ? 'green' : 
                      log.type === 'WARNING' ? 'orange' : 
                      log.type === 'ERROR' ? 'red' : 'blue'
                    }
                    minW="60px"
                  >
                    {log.type}
                  </Badge>
                  <Text fontSize="sm" flex="1">
                    {log.message}
                  </Text>
                  <Text fontSize="xs" color="gray.500" minW="120px" textAlign="right">
                    {log.source}
                  </Text>
                </HStack>
              ))}
            </VStack>
            <Divider mt={4} />
            <HStack justify="center" mt={4} spacing={4}>
              <Text fontSize="xs" color="gray.500">
                총 2,847개 로그 엔트리 • 실시간 업데이트 중
              </Text>
              <Badge colorScheme="green" variant="subtle">
                🟢 라이브
              </Badge>
            </HStack>
          </CardBody>
        </Card>

        {/* 최종 시스템 상태 요약 */}
        <Alert status="success" borderRadius="md">
          <AlertIcon />
          <Box>
            <Text fontWeight="bold">🎉 POSCO WatchHamster v3.0 시스템 정상 가동 중</Text>
            <Text fontSize="sm">
              모든 핵심 서비스가 정상 작동하고 있으며, 성능 지표가 우수 범위 내에 있습니다. 
              실시간 모니터링, 웹훅 발송, API 연동이 안정적으로 운영되고 있습니다.
            </Text>
          </Box>
        </Alert>
      </VStack>
    </Box>
  )
}

export default Services
