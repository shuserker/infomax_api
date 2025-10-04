import React, { useMemo } from 'react'
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Tooltip,
  useColorModeValue,
} from '@chakra-ui/react'
import { 
  FiArrowRight,
  FiDatabase,
  FiServer,
  FiGlobe,
  FiZap,
  FiMonitor,
} from 'react-icons/fi'

interface ServiceNode {
  id: string
  name: string
  type: 'core' | 'api' | 'data' | 'external'
  status: string
  dependencies: string[]
  icon: React.ComponentType
  description: string
}

interface ServiceDependencyGraphProps {
  services: any[]
}

// 서비스 의존성 정의
const SERVICE_DEPENDENCIES: ServiceNode[] = [
  {
    id: 'api_server',
    name: 'FastAPI 서버',
    type: 'core',
    status: 'running',
    dependencies: [],
    icon: FiServer,
    description: '메인 REST API 서버, 모든 요청의 진입점'
  },
  {
    id: 'watchhamster_monitor',
    name: 'WatchHamster 모니터',
    type: 'core', 
    status: 'running',
    dependencies: ['infomax_client', 'webhook_sender'],
    icon: FiMonitor,
    description: 'POSCO 뉴스 실시간 모니터링 시스템'
  },
  {
    id: 'infomax_client',
    name: 'INFOMAX API 클라이언트',
    type: 'external',
    status: 'running',
    dependencies: ['api_server'],
    icon: FiGlobe,
    description: 'POSCO 뉴스 API 연결 클라이언트'
  },
  {
    id: 'webhook_sender',
    name: '웹훅 발송자',
    type: 'api',
    status: 'running',
    dependencies: ['api_server'],
    icon: FiZap,
    description: 'Dooray 웹훅 메시지 전송 시스템'
  },
  {
    id: 'news_parser',
    name: '뉴스 데이터 파서',
    type: 'data',
    status: 'running', 
    dependencies: ['infomax_client'],
    icon: FiDatabase,
    description: '뉴스 데이터 분석 및 파싱 시스템'
  }
]

const ServiceDependencyGraph: React.FC<ServiceDependencyGraphProps> = ({ services }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const arrowColor = useColorModeValue('gray.400', 'gray.500')

  // 실제 서비스 상태와 병합
  const serviceNodes = useMemo(() => {
    return SERVICE_DEPENDENCIES.map(node => {
      const actualService = services.find(s => s.id === node.id)
      return {
        ...node,
        status: actualService?.status || node.status
      }
    })
  }, [services])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'green'
      case 'stopped': return 'gray'
      case 'error': return 'red'
      case 'starting': return 'yellow'
      default: return 'gray'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'core': return 'blue'
      case 'api': return 'purple'
      case 'data': return 'teal'
      case 'external': return 'orange'
      default: return 'gray'
    }
  }

  const renderServiceNode = (node: ServiceNode, level: number = 0) => {
    const IconComponent = node.icon
    const statusColor = getStatusColor(node.status)
    const typeColor = getTypeColor(node.type)

    return (
      <Tooltip key={node.id} label={node.description} placement="top">
        <Card
          size="sm"
          variant="outline"
          bg={bgColor}
          borderColor={borderColor}
          shadow="sm"
          _hover={{ shadow: "md" }}
          transition="all 0.2s"
          ml={level * 8}
          minW="200px"
        >
          <CardBody p={3}>
            <VStack spacing={2} align="center">
              <HStack spacing={2} justify="center" w="full">
                <Box
                  p={2}
                  bg={`${statusColor}.100`}
                  _dark={{ bg: `${statusColor}.900` }}
                  borderRadius="md"
                >
                  <Box as={IconComponent} w="16px" h="16px" />
                </Box>
                <Badge
                  size="sm"
                  colorScheme={statusColor}
                  variant="subtle"
                >
                  {node.status.toUpperCase()}
                </Badge>
              </HStack>
              
              <VStack spacing={1} align="center">
                <Text fontSize="sm" fontWeight="semibold" textAlign="center" lineHeight="1.2">
                  {node.name}
                </Text>
                <Badge size="xs" colorScheme={typeColor} variant="outline">
                  {node.type}
                </Badge>
              </VStack>
            </VStack>
          </CardBody>
        </Card>
      </Tooltip>
    )
  }

  const renderDependencyArrow = (fromLevel: number, toLevel: number) => {
    return (
      <HStack key={`arrow-${fromLevel}-${toLevel}`} spacing={1} align="center" mx={2}>
        <Box w="16px" h="1px" bg={arrowColor} />
        <FiArrowRight size={12} color={arrowColor} />
        <Box w="16px" h="1px" bg={arrowColor} />
      </HStack>
    )
  }

  // 의존성 레벨별로 그룹핑
  const getLeveledNodes = () => {
    const levels: ServiceNode[][] = []
    const processed = new Set<string>()

    // Level 0: 의존성이 없는 노드들
    const rootNodes = serviceNodes.filter(node => node.dependencies.length === 0)
    levels[0] = rootNodes
    rootNodes.forEach(node => processed.add(node.id))

    // Level 1+: 의존성이 있는 노드들을 레벨별로 배치
    let currentLevel = 1
    while (processed.size < serviceNodes.length && currentLevel < 10) {
      const levelNodes = serviceNodes.filter(node => 
        !processed.has(node.id) && 
        node.dependencies.every(depId => processed.has(depId))
      )
      
      if (levelNodes.length === 0) break
      
      levels[currentLevel] = levelNodes
      levelNodes.forEach(node => processed.add(node.id))
      currentLevel++
    }

    return levels.filter(level => level && level.length > 0)
  }

  const leveledNodes = getLeveledNodes()

  return (
    <Card>
      <CardHeader>
        <VStack spacing={2} align="start">
          <Heading size="md">서비스 의존성 관계</Heading>
          <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.400" }}>
            시스템 내 서비스들의 의존성과 연결 관계를 보여줍니다
          </Text>
        </VStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {leveledNodes.map((levelNodes, levelIndex) => (
            <VStack key={`level-${levelIndex}`} spacing={4} align="center">
              {/* 레벨 제목 */}
              <Text fontSize="xs" color="gray.500" fontWeight="semibold">
                Level {levelIndex} {levelIndex === 0 ? '(Core Services)' : levelIndex === 1 ? '(Dependent Services)' : '(Sub Services)'}
              </Text>
              
              {/* 해당 레벨의 노드들 */}
              <HStack spacing={4} justify="center" flexWrap="wrap">
                {levelNodes.map(node => renderServiceNode(node))}
              </HStack>
              
              {/* 다음 레벨로의 화살표 */}
              {levelIndex < leveledNodes.length - 1 && (
                <VStack spacing={2} align="center">
                  {renderDependencyArrow(levelIndex, levelIndex + 1)}
                  <Text fontSize="xs" color="gray.400">
                    depends on
                  </Text>
                </VStack>
              )}
            </VStack>
          ))}
          
          {/* 범례 */}
          <Box mt={6} p={4} bg="gray.50" _dark={{ bg: "gray.700" }} borderRadius="md">
            <Text fontSize="sm" fontWeight="semibold" mb={3}>범례</Text>
            <HStack spacing={6} flexWrap="wrap">
              <HStack spacing={2}>
                <Badge colorScheme="blue" variant="outline">core</Badge>
                <Text fontSize="xs">핵심 서비스</Text>
              </HStack>
              <HStack spacing={2}>
                <Badge colorScheme="purple" variant="outline">api</Badge>
                <Text fontSize="xs">API 서비스</Text>
              </HStack>
              <HStack spacing={2}>
                <Badge colorScheme="teal" variant="outline">data</Badge>
                <Text fontSize="xs">데이터 처리</Text>
              </HStack>
              <HStack spacing={2}>
                <Badge colorScheme="orange" variant="outline">external</Badge>
                <Text fontSize="xs">외부 연동</Text>
              </HStack>
            </HStack>
          </Box>

          {/* 통계 */}
          <Box mt={4} p={4} bg="blue.50" _dark={{ bg: "blue.900" }} borderRadius="md">
            <HStack spacing={8} justify="center">
              <VStack spacing={1}>
                <Text fontSize="lg" fontWeight="bold" color="blue.600" _dark={{ color: "blue.300" }}>
                  {serviceNodes.length}
                </Text>
                <Text fontSize="xs" color="gray.600" _dark={{ color: "gray.400" }}>
                  총 서비스
                </Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="lg" fontWeight="bold" color="green.600" _dark={{ color: "green.300" }}>
                  {serviceNodes.filter(s => s.status === 'running').length}
                </Text>
                <Text fontSize="xs" color="gray.600" _dark={{ color: "gray.400" }}>
                  실행 중
                </Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="lg" fontWeight="bold" color="purple.600" _dark={{ color: "purple.300" }}>
                  {serviceNodes.reduce((acc, node) => acc + node.dependencies.length, 0)}
                </Text>
                <Text fontSize="xs" color="gray.600" _dark={{ color: "gray.400" }}>
                  총 의존성
                </Text>
              </VStack>
            </HStack>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default ServiceDependencyGraph
