import React from 'react'
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Button,
  VStack,
  HStack,
  IconButton,
  useToast,
  Tooltip,
  Divider,
} from '@chakra-ui/react'
import { MdPlayArrow, MdStop, MdRefresh, MdSettings } from 'react-icons/md'
import PoscoManagementPanel from '../components/Services/PoscoManagementPanel'
import WebhookManagement from '../components/Services/WebhookManagement'

const Services: React.FC = () => {
  const toast = useToast()

  // 임시 서비스 데이터
  const services = [
    {
      id: 'posco_news',
      name: 'POSCO 뉴스 모니터',
      description: 'POSCO 뉴스 시스템 모니터링 및 알림 서비스',
      status: 'running',
      uptime: '2시간 15분',
      lastError: null,
      config: { branch: 'main', interval: '5분' },
    },
    {
      id: 'github_pages',
      name: 'GitHub Pages 모니터',
      description: 'GitHub Pages 배포 상태 모니터링',
      status: 'stopped',
      uptime: '-',
      lastError: 'Connection timeout',
      config: { repository: 'posco-docs', branch: 'gh-pages' },
    },
    {
      id: 'cache_monitor',
      name: '캐시 모니터',
      description: '데이터 캐시 상태 모니터링 및 관리',
      status: 'running',
      uptime: '1시간 30분',
      lastError: null,
      config: { cache_size: '500MB', ttl: '1시간' },
    },
    {
      id: 'deployment',
      name: '배포 시스템',
      description: '자동 배포 및 롤백 관리 시스템',
      status: 'error',
      uptime: '-',
      lastError: 'Git merge conflict in main branch',
      config: { auto_deploy: true, rollback_enabled: true },
    },
    {
      id: 'message_system',
      name: '메시지 시스템',
      description: '동적 메시지 생성 및 템플릿 관리',
      status: 'running',
      uptime: '3시간 45분',
      lastError: null,
      config: { template_count: 15, cache_enabled: true },
    },
    {
      id: 'webhook_system',
      name: '웹훅 시스템',
      description: 'Discord/Slack 웹훅 전송 및 관리',
      status: 'running',
      uptime: '2시간 50분',
      lastError: null,
      config: { discord_enabled: true, slack_enabled: true },
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'green'
      case 'stopped':
        return 'gray'
      case 'error':
        return 'red'
      case 'starting':
        return 'blue'
      case 'stopping':
        return 'orange'
      default:
        return 'gray'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return '실행 중'
      case 'stopped':
        return '중지됨'
      case 'error':
        return '오류'
      case 'starting':
        return '시작 중'
      case 'stopping':
        return '중지 중'
      default:
        return '알 수 없음'
    }
  }

  const handleServiceAction = (serviceId: string, action: string) => {
    const service = services.find(s => s.id === serviceId)
    if (!service) return

    toast({
      title: `서비스 ${action}`,
      description: `${service.name} 서비스를 ${action}합니다.`,
      status: 'info',
      duration: 3000,
      isClosable: true,
    })

    // 실제로는 API 호출
    console.log(`${action} service: ${serviceId}`)
  }

  return (
    <Box className="fade-in">
      <VStack spacing={6} align="stretch">
        {/* 페이지 헤더 */}
        <Box>
          <Heading size="lg" mb={2}>
            서비스 관리
          </Heading>
          <Text color="gray.600" _dark={{ color: 'gray.400' }}>
            시스템 서비스의 상태를 확인하고 제어합니다
          </Text>
        </Box>

        {/* 서비스 카드 그리드 */}
        <Grid templateColumns="repeat(auto-fit, minmax(400px, 1fr))" gap={6}>
          {services.map(service => (
            <GridItem key={service.id}>
              <Card h="100%">
                <CardHeader pb={3}>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex="1">
                      <Heading size="md">{service.name}</Heading>
                      <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                        {service.description}
                      </Text>
                    </VStack>
                    <Badge
                      colorScheme={getStatusColor(service.status)}
                      variant="solid"
                      fontSize="xs"
                    >
                      {getStatusText(service.status)}
                    </Badge>
                  </HStack>
                </CardHeader>

                <CardBody pt={0}>
                  <VStack align="stretch" spacing={4}>
                    {/* 서비스 정보 */}
                    <Box>
                      <HStack justify="space-between" mb={2}>
                        <Text fontSize="sm" fontWeight="medium">
                          업타임
                        </Text>
                        <Text fontSize="sm">{service.uptime}</Text>
                      </HStack>

                      {service.lastError && (
                        <Box>
                          <Text fontSize="sm" fontWeight="medium" color="red.500" mb={1}>
                            마지막 오류
                          </Text>
                          <Text fontSize="xs" color="red.600" _dark={{ color: 'red.400' }}>
                            {service.lastError}
                          </Text>
                        </Box>
                      )}
                    </Box>

                    <Divider />

                    {/* 설정 정보 */}
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={2}>
                        설정
                      </Text>
                      <VStack align="stretch" spacing={1}>
                        {Object.entries(service.config).map(([key, value]) => (
                          <HStack key={key} justify="space-between">
                            <Text fontSize="xs" color="gray.600" _dark={{ color: 'gray.400' }}>
                              {key}
                            </Text>
                            <Text fontSize="xs">{String(value)}</Text>
                          </HStack>
                        ))}
                      </VStack>
                    </Box>

                    <Divider />

                    {/* 제어 버튼들 */}
                    <HStack spacing={2}>
                      {service.status === 'running' ? (
                        <>
                          <Button
                            size="sm"
                            colorScheme="orange"
                            leftIcon={<MdStop />}
                            onClick={() => handleServiceAction(service.id, '중지')}
                            flex="1"
                          >
                            중지
                          </Button>
                          <Button
                            size="sm"
                            colorScheme="blue"
                            leftIcon={<MdRefresh />}
                            onClick={() => handleServiceAction(service.id, '재시작')}
                            flex="1"
                          >
                            재시작
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          colorScheme="green"
                          leftIcon={<MdPlayArrow />}
                          onClick={() => handleServiceAction(service.id, '시작')}
                          flex="1"
                        >
                          시작
                        </Button>
                      )}

                      <Tooltip label="서비스 설정">
                        <IconButton
                          size="sm"
                          aria-label="서비스 설정"
                          icon={<MdSettings />}
                          variant="outline"
                          onClick={() => handleServiceAction(service.id, '설정')}
                        />
                      </Tooltip>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            </GridItem>
          ))}
        </Grid>

        {/* POSCO 시스템 전용 관리 패널 */}
        <PoscoManagementPanel />

        {/* 웹훅 및 메시지 관리 */}
        <WebhookManagement />
      </VStack>
    </Box>
  )
}

export default Services
