import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Badge,
  Progress,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,

  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Select,
  Spinner,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  List,
  ListItem,
  ListIcon,
  Icon,
  Flex,
  Spacer
} from '@chakra-ui/react';
import {
  FaRocket,
  FaStop,
  FaSync,
  FaGithub,
  FaCheckCircle,
  FaExclamationTriangle,
  FaClock,
  FaPlay,
  FaPause,
  FaHistory,
  FaEye,
  FaCodeBranch,
  FaServer
} from 'react-icons/fa';
import { useApiService } from '../../hooks/useApiService';
import { useRealtimeMessages } from '../../hooks/useRealtimeMessages';

// 타입 정의
interface DeploymentSession {
  session_id: string;
  status: 'idle' | 'preparing' | 'switching_branch' | 'building' | 'deploying' | 'success' | 'failed' | 'rolling_back';
  current_branch: string;
  target_branch: string;
  start_time: string;
  end_time?: string;
  steps_completed: string[];
  current_step: string;
  progress_percentage: number;
  error_message?: string;
}

interface GitHubPagesStatus {
  is_accessible: boolean;
  last_check: string;
  response_time?: number;
  status_code?: number;
  error_message?: string;
}

interface PoscoStatus {
  current_deployment?: DeploymentSession;
  current_branch: string;
  branch_switch_status: 'idle' | 'checking' | 'switching' | 'verifying' | 'completed' | 'failed';
  github_pages_status: GitHubPagesStatus;
  deployment_history: DeploymentSession[];
}

const PoscoManagementPanel: React.FC = () => {
  const [poscoStatus, setPoscoStatus] = useState<PoscoStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [availableBranches] = useState(['main', 'develop', 'staging', 'production']);
  const [isMonitoring, setIsMonitoring] = useState(false);
  
  const { isOpen: isDeployModalOpen, onOpen: onDeployModalOpen, onClose: onDeployModalClose } = useDisclosure();
  const { isOpen: isHistoryModalOpen, onOpen: onHistoryModalOpen, onClose: onHistoryModalClose } = useDisclosure();
  

  const { callApi } = useApiService();
  const { isConnected } = useRealtimeMessages();

  // POSCO 상태 조회
  const fetchPoscoStatus = async () => {
    await callApi(
      async () => {
        const res = await fetch('/api/posco/status');
        if (!res.ok) throw new Error('POSCO 상태 조회 실패');
        return res.json();
      },
      {
        loadingKey: 'poscoStatus',
        errorContext: 'POSCO 상태 조회',
        onSuccess: (data) => {
          setPoscoStatus(data);
          setIsLoading(false);
        },
        onError: () => {
          setIsLoading(false);
        }
      }
    );
  };

  // 배포 시작
  const handleStartDeployment = async () => {
    await callApi(
      async () => {
        const res = await fetch('/api/posco/deployment/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ target_branch: selectedBranch })
        });
        if (!res.ok) throw new Error('배포 시작 실패');
        return res.json();
      },
      {
        loadingKey: 'startDeployment',
        successMessage: `${selectedBranch} 브랜치로 배포가 시작되었습니다.`,
        errorContext: '배포 시작',
        onSuccess: () => {
          onDeployModalClose();
          fetchPoscoStatus();
        }
      }
    );
  };

  // 배포 중지
  const handleStopDeployment = async () => {
    await callApi(
      async () => {
        const res = await fetch('/api/posco/deployment/stop', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error('배포 중지 실패');
        return res.json();
      },
      {
        loadingKey: 'stopDeployment',
        successMessage: '배포가 중지되었습니다.',
        errorContext: '배포 중지',
        onSuccess: () => {
          fetchPoscoStatus();
        }
      }
    );
  };

  // 모니터링 시작/중지
  const handleToggleMonitoring = async () => {
    const endpoint = isMonitoring ? '/api/posco/monitoring/stop' : '/api/posco/monitoring/start';
    await callApi(
      async () => {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error('모니터링 제어 실패');
        return res.json();
      },
      {
        loadingKey: 'toggleMonitoring',
        successMessage: `POSCO 시스템 모니터링이 ${isMonitoring ? '중지' : '시작'}되었습니다.`,
        errorContext: '모니터링 제어',
        onSuccess: () => {
          setIsMonitoring(!isMonitoring);
        }
      }
    );
  };

  // 상태 배지 색상 결정
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      case 'preparing':
      case 'switching_branch':
      case 'building':
      case 'deploying':
      case 'switching':
      case 'checking':
        return 'blue';
      case 'idle':
        return 'gray';
      default:
        return 'gray';
    }
  };

  // 상태 아이콘 결정
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
      case 'completed':
        return FaCheckCircle;
      case 'failed':
        return FaExclamationTriangle;
      case 'preparing':
      case 'switching_branch':
      case 'building':
      case 'deploying':
      case 'switching':
      case 'checking':
        return FaSync;
      default:
        return FaClock;
    }
  };

  // 실시간 연결 상태 처리
  useEffect(() => {
    if (isConnected && poscoStatus === null) {
      fetchPoscoStatus();
    }
  }, [isConnected]);

  // 초기 데이터 로드
  useEffect(() => {
    fetchPoscoStatus();
    const interval = setInterval(fetchPoscoStatus, 10000); // 10초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <Box p={6} textAlign="center">
        <Spinner size="xl" color="posco.500" />
        <Text mt={4}>POSCO 시스템 상태를 불러오는 중...</Text>
      </Box>
    );
  }

  if (!poscoStatus) {
    return (
      <Alert status="error">
        <AlertIcon />
        <AlertTitle>POSCO 시스템 연결 실패</AlertTitle>
        <AlertDescription>
          POSCO 시스템에 연결할 수 없습니다. 백엔드 서비스를 확인해주세요.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* 헤더 */}
        <Flex align="center">
          <HStack>
            <Icon as={FaServer} color="posco.500" boxSize={6} />
            <Heading size="lg" color="posco.500">POSCO 시스템 관리</Heading>
          </HStack>
          <Spacer />
          <HStack>
            <Button
              leftIcon={isMonitoring ? <FaPause /> : <FaPlay />}
              colorScheme={isMonitoring ? "red" : "green"}
              size="sm"
              onClick={handleToggleMonitoring}
            >
              {isMonitoring ? '모니터링 중지' : '모니터링 시작'}
            </Button>
            <Button
              leftIcon={<FaHistory />}
              variant="outline"
              size="sm"
              onClick={onHistoryModalOpen}
            >
              배포 히스토리
            </Button>
          </HStack>
        </Flex>

        {/* 현재 상태 개요 */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>현재 브랜치</StatLabel>
                  <StatNumber>
                    <HStack>
                      <Icon as={FaCodeBranch} />
                      <Text>{poscoStatus.current_branch}</Text>
                    </HStack>
                  </StatNumber>
                  <StatHelpText>
                    <Badge colorScheme={getStatusColor(poscoStatus.branch_switch_status)}>
                      {poscoStatus.branch_switch_status}
                    </Badge>
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>GitHub Pages</StatLabel>
                  <StatNumber>
                    <HStack>
                      <Icon as={FaGithub} />
                      <Text>{poscoStatus.github_pages_status.is_accessible ? '정상' : '오류'}</Text>
                    </HStack>
                  </StatNumber>
                  <StatHelpText>
                    {poscoStatus.github_pages_status.response_time && (
                      <>
                        <StatArrow type="increase" />
                        {poscoStatus.github_pages_status.response_time.toFixed(2)}ms
                      </>
                    )}
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>배포 상태</StatLabel>
                  <StatNumber>
                    <HStack>
                      <Icon as={FaRocket} />
                      <Text>
                        {poscoStatus.current_deployment ? poscoStatus.current_deployment.status : '대기 중'}
                      </Text>
                    </HStack>
                  </StatNumber>
                  <StatHelpText>
                    {poscoStatus.current_deployment && (
                      <Badge colorScheme={getStatusColor(poscoStatus.current_deployment.status)}>
                        {poscoStatus.current_deployment.current_step}
                      </Badge>
                    )}
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>

        {/* 현재 배포 세션 */}
        {poscoStatus.current_deployment && (
          <Card>
            <CardHeader>
              <HStack>
                <Icon as={FaRocket} color="blue.500" />
                <Heading size="md">현재 배포 진행 상황</Heading>
                <Spacer />
                <Badge colorScheme={getStatusColor(poscoStatus.current_deployment.status)} fontSize="sm">
                  {poscoStatus.current_deployment.status}
                </Badge>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <HStack>
                  <Text fontWeight="bold">세션 ID:</Text>
                  <Text>{poscoStatus.current_deployment.session_id}</Text>
                  <Spacer />
                  <Text fontWeight="bold">브랜치:</Text>
                  <Text>{poscoStatus.current_deployment.current_branch} → {poscoStatus.current_deployment.target_branch}</Text>
                </HStack>

                <Box>
                  <HStack mb={2}>
                    <Text fontWeight="bold">진행률:</Text>
                    <Text>{poscoStatus.current_deployment.progress_percentage.toFixed(1)}%</Text>
                  </HStack>
                  <Progress 
                    value={poscoStatus.current_deployment.progress_percentage} 
                    colorScheme="blue" 
                    size="lg"
                    hasStripe
                    isAnimated
                  />
                </Box>

                <Box>
                  <Text fontWeight="bold" mb={2}>현재 단계:</Text>
                  <Text color="blue.600">{poscoStatus.current_deployment.current_step}</Text>
                </Box>

                {poscoStatus.current_deployment.steps_completed.length > 0 && (
                  <Box>
                    <Text fontWeight="bold" mb={2}>완료된 단계:</Text>
                    <List spacing={1}>
                      {poscoStatus.current_deployment.steps_completed.map((step, index) => (
                        <ListItem key={index}>
                          <ListIcon as={FaCheckCircle} color="green.500" />
                          {step}
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {poscoStatus.current_deployment.error_message && (
                  <Alert status="error">
                    <AlertIcon />
                    <AlertTitle>오류 발생</AlertTitle>
                    <AlertDescription>{poscoStatus.current_deployment.error_message}</AlertDescription>
                  </Alert>
                )}

                <HStack>
                  {['preparing', 'switching_branch', 'building', 'deploying'].includes(poscoStatus.current_deployment.status) && (
                    <Button
                      leftIcon={<FaStop />}
                      colorScheme="red"
                      onClick={handleStopDeployment}
                    >
                      배포 중지
                    </Button>
                  )}
                  <Button
                    leftIcon={<FaSync />}
                    variant="outline"
                    onClick={fetchPoscoStatus}
                  >
                    상태 새로고침
                  </Button>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        )}

        {/* 배포 제어 */}
        <Card>
          <CardHeader>
            <HStack>
              <Icon as={FaRocket} color="green.500" />
              <Heading size="md">배포 제어</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text>새로운 배포를 시작하거나 현재 배포를 관리할 수 있습니다.</Text>
              
              <HStack>
                <Button
                  leftIcon={<FaRocket />}
                  colorScheme="green"
                  onClick={onDeployModalOpen}
                  isDisabled={poscoStatus.current_deployment && 
                    ['preparing', 'switching_branch', 'building', 'deploying'].includes(poscoStatus.current_deployment.status)}
                >
                  새 배포 시작
                </Button>
                
                <Button
                  leftIcon={<FaEye />}
                  variant="outline"
                  onClick={() => window.open('https://your-github-pages-url.github.io', '_blank')}
                >
                  GitHub Pages 확인
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* GitHub Pages 상태 */}
        <Card>
          <CardHeader>
            <HStack>
              <Icon as={FaGithub} color="gray.700" />
              <Heading size="md">GitHub Pages 상태</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
              <GridItem>
                <VStack align="start">
                  <Text fontWeight="bold">접근 상태</Text>
                  <Badge colorScheme={poscoStatus.github_pages_status.is_accessible ? 'green' : 'red'}>
                    {poscoStatus.github_pages_status.is_accessible ? '정상' : '오류'}
                  </Badge>
                </VStack>
              </GridItem>
              
              {poscoStatus.github_pages_status.response_time && (
                <GridItem>
                  <VStack align="start">
                    <Text fontWeight="bold">응답 시간</Text>
                    <Text>{poscoStatus.github_pages_status.response_time.toFixed(2)}ms</Text>
                  </VStack>
                </GridItem>
              )}
              
              {poscoStatus.github_pages_status.status_code && (
                <GridItem>
                  <VStack align="start">
                    <Text fontWeight="bold">상태 코드</Text>
                    <Badge colorScheme={poscoStatus.github_pages_status.status_code === 200 ? 'green' : 'red'}>
                      {poscoStatus.github_pages_status.status_code}
                    </Badge>
                  </VStack>
                </GridItem>
              )}
              
              <GridItem>
                <VStack align="start">
                  <Text fontWeight="bold">마지막 확인</Text>
                  <Text fontSize="sm" color="gray.600">
                    {new Date(poscoStatus.github_pages_status.last_check).toLocaleString()}
                  </Text>
                </VStack>
              </GridItem>
            </Grid>
            
            {poscoStatus.github_pages_status.error_message && (
              <Alert status="error" mt={4}>
                <AlertIcon />
                <AlertDescription>{poscoStatus.github_pages_status.error_message}</AlertDescription>
              </Alert>
            )}
          </CardBody>
        </Card>
      </VStack>

      {/* 배포 시작 모달 */}
      <Modal isOpen={isDeployModalOpen} onClose={onDeployModalClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>새 배포 시작</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <Text>배포할 브랜치를 선택해주세요:</Text>
              <Select value={selectedBranch} onChange={(e) => setSelectedBranch(e.target.value)}>
                {availableBranches.map(branch => (
                  <option key={branch} value={branch}>{branch}</option>
                ))}
              </Select>
              <Alert status="info">
                <AlertIcon />
                <AlertDescription>
                  선택한 브랜치로 전환하고 GitHub Pages에 배포됩니다.
                </AlertDescription>
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onDeployModalClose}>
              취소
            </Button>
            <Button colorScheme="green" onClick={handleStartDeployment}>
              배포 시작
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* 배포 히스토리 모달 */}
      <Modal isOpen={isHistoryModalOpen} onClose={onHistoryModalClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>배포 히스토리</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {poscoStatus.deployment_history.length === 0 ? (
              <Text textAlign="center" color="gray.500">배포 히스토리가 없습니다.</Text>
            ) : (
              <VStack spacing={3} align="stretch">
                {poscoStatus.deployment_history.map((deployment) => (
                  <Card key={deployment.session_id} size="sm">
                    <CardBody>
                      <HStack>
                        <Icon as={getStatusIcon(deployment.status)} 
                              color={`${getStatusColor(deployment.status)}.500`} />
                        <VStack align="start" spacing={1} flex={1}>
                          <HStack>
                            <Text fontWeight="bold">{deployment.session_id}</Text>
                            <Badge colorScheme={getStatusColor(deployment.status)}>
                              {deployment.status}
                            </Badge>
                          </HStack>
                          <Text fontSize="sm" color="gray.600">
                            {deployment.current_branch} → {deployment.target_branch}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {new Date(deployment.start_time).toLocaleString()}
                            {deployment.end_time && ` - ${new Date(deployment.end_time).toLocaleString()}`}
                          </Text>
                        </VStack>
                        <Text fontSize="sm" color="gray.600">
                          {deployment.progress_percentage.toFixed(1)}%
                        </Text>
                      </HStack>
                    </CardBody>
                  </Card>
                ))}
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button onClick={onHistoryModalClose}>닫기</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default PoscoManagementPanel;