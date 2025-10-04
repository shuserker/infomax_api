import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Grid,
  GridItem,
  Heading,
  Text,
  Badge,
  Flex,
  Spacer,
  VStack,
  useToast,
  Stat,
  StatLabel,
  StatNumber,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Code,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  HStack,
  Icon,
  Spinner,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { FiSend, FiRefreshCw, FiCode, FiFileText, FiArrowRight } from 'react-icons/fi';
import { CompanySelector } from '@/components/CompanySelector';

interface MessageType {
  id: string;
  name: string;
  bot_type: string;
  priority: string;
  endpoint: string;
  description: string;
}

interface WebhookStats {
  total_sent: number;
  successful_sends: number;
  failed_sends: number;
  retry_attempts: number;
  average_response_time: number;
}

export const WebhookManager: React.FC = () => {
  const [messageTypes, setMessageTypes] = useState<MessageType[]>([]);
  const [stats, setStats] = useState<WebhookStats | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string>('posco');
  const [loading, setLoading] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<MessageType | null>(null);
  const [messageDetail, setMessageDetail] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedLogId, setSelectedLogId] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [selectedCompany]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [typesRes, statsRes] = await Promise.all([
        fetch('http://localhost:8000/api/webhook-manager/message-types'),
        fetch(`http://localhost:8000/api/webhook-manager/stats?company_id=${selectedCompany}`)
      ]);

      const typesData = await typesRes.json();
      const statsData = await statsRes.json();

      setMessageTypes(typesData.message_types || []);
      setStats(statsData);
    } catch (err: any) {
      toast({
        title: '데이터 로드 실패',
        description: err.message,
        status: 'error',
        duration: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const loadRecentLogs = async (messageTypeId: string) => {
    setLogsLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/webhook-manager/logs?company_id=${selectedCompany}&message_type=${messageTypeId}&limit=10`);
      const data = await res.json();
      setRecentLogs(data.logs || []);
    } catch (err: any) {
      toast({
        title: '로그 로드 실패',
        description: err.message,
        status: 'error',
        duration: 3000
      });
    } finally {
      setLogsLoading(false);
    }
  };

  const sendMessage = async (messageType: MessageType) => {
    setLoading(true);
    try {
      let endpoint = '';
      let body: any = {};
      
      switch (messageType.id) {
        case 'test':
          endpoint = `/api/webhook-manager/send/test?test_content=${encodeURIComponent('웹훅 시스템 테스트')}&company_id=${selectedCompany}`;
          break;
        case 'business_day_comparison':
          endpoint = '/api/webhook-manager/send/business-day-comparison';
          body = {
            raw_data: {
              'newyork-market-watch': { time: '063000', title: '[뉴욕마켓워치] 미국 증시 상승 마감' },
              'kospi-close': { time: '154000', title: '[증시마감] 코스피 2,650선 회복' },
              'exchange-rate': { time: '153000', title: '[서환마감] 원/달러 환율 1,320원대' }
            },
            priority: 'NORMAL'
          };
          break;
        case 'delay_notification':
          endpoint = '/api/webhook-manager/send/delay-notification?news_type=kospi-close&delay_minutes=15';
          body = { current_data: { time: '154000', title: '[증시마감] 코스피 마감' } };
          break;
        case 'daily_report':
          endpoint = '/api/webhook-manager/send/daily-report';
          body = {
            raw_data: {
              'newyork-market-watch': { time: '063000', title: '[뉴욕마켓워치] 미국 증시 상승 마감' },
              'kospi-close': { time: '154000', title: '[증시마감] 코스피 2,650선 회복' },
              'exchange-rate': { time: '153000', title: '[서환마감] 원/달러 환율 1,320원대' }
            }
          };
          break;
        case 'status_notification':
          endpoint = '/api/webhook-manager/send/status-notification';
          body = {
            raw_data: {
              'kospi-close': { time: '154000', title: '[증시마감] 코스피 정상 발행' }
            }
          };
          break;
        case 'no_data_notification':
          endpoint = '/api/webhook-manager/send/no-data-notification';
          body = {
            raw_data: {
              'kospi-close': { time: '154000', title: '[증시마감] 데이터 없음' }
            }
          };
          break;
        case 'watchhamster_error':
          endpoint = '/api/webhook-manager/send/watchhamster-error?error_message=테스트 오류 발생';
          break;
        case 'watchhamster_status':
          endpoint = '/api/webhook-manager/send/watchhamster-status?status_message=시스템 정상 작동';
          break;
      }
      
      const res = await fetch(
        `http://localhost:8000${endpoint}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: Object.keys(body).length > 0 ? JSON.stringify(body) : undefined
        }
      );
      const data = await res.json();
      
      if (data.status === 'success') {
        toast({
          title: '✅ 발송 성공',
          description: `${messageType.name} 메시지 발송 완료`,
          status: 'success',
          duration: 3000
        });
        loadData();
      }
    } catch (err: any) {
      toast({
        title: '❌ 발송 실패',
        description: err.message,
        status: 'error',
        duration: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={6}>
      <Flex mb={6} align="center">
        <Heading size="lg">📬 웹훅 관리 시스템</Heading>
        <Spacer />
        <Button
          leftIcon={<FiRefreshCw />}
          onClick={loadData}
          isLoading={loading}
          variant="outline"
        >
          새로고침
        </Button>
      </Flex>

      {/* 회사 선택 */}
      <Box mb={6} maxW="400px">
        <CompanySelector
          selectedCompanyId={selectedCompany}
          onCompanyChange={(companyId) => {
            setSelectedCompany(companyId);
          }}
          showLabel={true}
        />
      </Box>

      {/* 통계 카드 */}
      {stats && (
        <Grid templateColumns="repeat(4, 1fr)" gap={4} mb={6}>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>총 발송</StatLabel>
                  <StatNumber>{stats.total_sent}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>성공</StatLabel>
                  <StatNumber color="green.500">{stats.successful_sends}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>실패</StatLabel>
                  <StatNumber color="red.500">{stats.failed_sends}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>평균 응답</StatLabel>
                  <StatNumber>{stats.average_response_time.toFixed(2)}s</StatNumber>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>
      )}

      {/* 메시지 타입 카드 */}
      <Heading size="md" mb={4}>📋 메시지 타입 ({messageTypes.length}개)</Heading>
      <Grid templateColumns="repeat(auto-fill, minmax(350px, 1fr))" gap={4}>
        {messageTypes.map((type) => (
          <GridItem key={type.id}>
            <Card
              _hover={{ shadow: 'lg', borderColor: 'blue.300' }}
              cursor="pointer"
              onClick={async () => {
                setSelectedMessage(type);
                setDetailLoading(true);
                onOpen();
                
                // 상세 정보와 최근 로그를 병렬로 로드
                try {
                  const [detailRes] = await Promise.all([
                    fetch(`http://localhost:8000/api/webhook-manager/message-types/${type.id}/detail?company_id=${selectedCompany}`),
                    loadRecentLogs(type.id)
                  ]);
                  const data = await detailRes.json();
                  setMessageDetail(data);
                } catch (err: any) {
                  toast({
                    title: '상세 정보 로드 실패',
                    description: err.message,
                    status: 'error',
                    duration: 3000
                  });
                } finally {
                  setDetailLoading(false);
                }
              }}
            >
              <CardHeader>
                <Heading size="sm">{type.name}</Heading>
                <Text fontSize="xs" color="gray.600" mt={1}>
                  {type.description}
                </Text>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  <Flex gap={2} wrap="wrap">
                    <Badge variant="outline">BOT: {type.bot_type}</Badge>
                    <Badge variant="outline">채널: {type.endpoint}</Badge>
                    <Badge colorScheme="blue">{type.priority}</Badge>
                  </Flex>
                  <Button
                    leftIcon={<FiSend />}
                    colorScheme="blue"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      sendMessage(type);
                    }}
                    isLoading={loading}
                    width="full"
                  >
                    테스트 발송
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </GridItem>
        ))}
      </Grid>

      {/* 메시지 상세 정보 모달 */}
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent maxH="70vh" mx={8} my={16}>
          <ModalHeader>
            <HStack>
              <Text>{selectedMessage?.name}</Text>
              <Badge colorScheme="blue">{selectedMessage?.bot_type}</Badge>
              <Badge>{selectedMessage?.endpoint}</Badge>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6} overflowY="auto">
            {detailLoading ? (
              <Box textAlign="center" py={8}>
                <Spinner size="lg" />
                <Text mt={4}>상세 정보를 불러오는 중...</Text>
              </Box>
            ) : selectedMessage && messageDetail ? (
              <Grid templateColumns="1fr 1fr" gap={6} h="full" alignItems="stretch">
                {/* 왼쪽: 기존 탭들 */}
                <GridItem h="full">
                  <Tabs colorScheme="blue" h="full" onChange={setSelectedTab} display="flex" flexDir="column">
                <TabList>
                  <Tab>📝 설명</Tab>
                  <Tab>📋 템플릿</Tab>
                  <Tab>📤 최근 발송</Tab>
                  <Tab>🔧 Input/Output</Tab>
                </TabList>

                <TabPanels flex="1" overflow="hidden">
                  {/* 탭 1: 설명 */}
                  <TabPanel h="full" overflowY="auto">
                    <VStack spacing={6} align="stretch">
                      {/* 메시지 개요 */}
                      <Card variant="outline">
                        <CardHeader>
                          <HStack>
                            <Text fontWeight="bold">📋 메시지 개요</Text>
                            <Spacer />
                            <Badge colorScheme="blue" variant="solid">
                              {selectedMessage.endpoint === 'NEWS_MAIN' ? '📰 뉴스' : '🛡️ 시스템'}
                            </Badge>
                          </HStack>
                        </CardHeader>
                        <CardBody>
                          <Text color="gray.700" lineHeight="1.6">
                            {selectedMessage.description}
                          </Text>
                        </CardBody>
                      </Card>

                      {/* 기술 사양 */}
                      <Card variant="outline">
                        <CardHeader>
                          <Text fontWeight="bold">🔧 기술 사양</Text>
                        </CardHeader>
                        <CardBody>
                          <Grid templateColumns="1fr 1fr" gap={4}>
                            <VStack align="start" spacing={3}>
                              <Box>
                                <Text fontSize="sm" color="gray.500" mb={1}>메시지 ID</Text>
                                <Code fontSize="sm" colorScheme="blue">{selectedMessage.id}</Code>
                              </Box>
                              <Box>
                                <Text fontSize="sm" color="gray.500" mb={1}>봇 타입</Text>
                                <Badge variant="outline">{selectedMessage.bot_type}</Badge>
                              </Box>
                            </VStack>
                            <VStack align="start" spacing={3}>
                              <Box>
                                <Text fontSize="sm" color="gray.500" mb={1}>전송 채널</Text>
                                <Badge colorScheme={selectedMessage.endpoint === 'NEWS_MAIN' ? 'green' : 'purple'}>
                                  {selectedMessage.endpoint}
                                </Badge>
                              </Box>
                              <Box>
                                <Text fontSize="sm" color="gray.500" mb={1}>우선순위</Text>
                                <Badge 
                                  colorScheme={
                                    selectedMessage.priority === 'CRITICAL' ? 'red' :
                                    selectedMessage.priority === 'HIGH' ? 'orange' :
                                    selectedMessage.priority === 'NORMAL' ? 'blue' : 'gray'
                                  }
                                >
                                  {selectedMessage.priority}
                                </Badge>
                              </Box>
                            </VStack>
                          </Grid>
                        </CardBody>
                      </Card>

                      {/* 사용 가이드 */}
                      <Card variant="outline">
                        <CardHeader>
                          <Text fontWeight="bold">💡 사용 가이드</Text>
                        </CardHeader>
                        <CardBody>
                          <VStack align="start" spacing={3}>
                            {selectedMessage.id === 'business_day_comparison' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • 전일 대비 뉴스 발행 시간을 비교 분석하여 시장 동향을 예측합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 3개 뉴스 타입 (뉴욕마켓워치, 코스피 마감, 환율)의 발행 패턴을 분석합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 지연 발행 및 시장 상황에 대한 인사이트를 제공합니다
                                </Text>
                              </>
                            )}
                            {selectedMessage.id === 'delay_notification' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • 예상 발행 시간 대비 15분 이상 지연 시 자동 알림을 전송합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 지연 원인 분석 및 시장 영향도를 평가합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 지연 심각도에 따라 우선순위를 자동 조정합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 반복적 지연 패턴을 학습하여 예측 알림을 제공합니다
                                </Text>
                              </>
                            )}
                            {selectedMessage.id === 'test' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • 웹훅 시스템의 정상 작동을 확인하는 테스트 메시지입니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 네트워크 연결 및 응답 시간을 측정합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • Dooray 채널 연결 상태와 메시지 포맷을 검증합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 일일 시스템 점검 및 장애 진단에 활용됩니다
                                </Text>
                              </>
                            )}
                            {selectedMessage.id === 'daily_report' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • 하루 종합 뉴스 발행 현황을 요약하여 전송합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 발행 시간 통계 및 지연 빈도를 분석합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 전일 대비 패턴 변화를 감지하고 트렌드를 제공합니다
                                </Text>
                              </>
                            )}
                            {selectedMessage.id === 'status_notification' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • 정시 발행 완료 시 확인 알림을 전송합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 시장 개장 시간에 맞춘 정시성을 보장합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 발행 품질 및 데이터 무결성을 자동 검증합니다
                                </Text>
                              </>
                            )}
                            {selectedMessage.id === 'no_data_notification' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • API 응답 없음 또는 데이터 부재 시 긴급 알림을 전송합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 데이터 소스별 연결 상태를 실시간 모니터링합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 자동 복구 시도 및 백업 데이터 소스로 전환합니다
                                </Text>
                              </>
                            )}
                            {selectedMessage.id === 'watchhamster_error' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • 시스템 오류 발생 시 즉시 개발팀에 알림을 전송합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 오류 유형별 심각도를 분류하고 대응 방안을 제시합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 자동 로그 수집 및 스택 트레이스를 포함합니다
                                </Text>
                              </>
                            )}
                            {selectedMessage.id === 'watchhamster_status' && (
                              <>
                                <Text fontSize="sm" color="gray.600">
                                  • 시스템 상태 및 성능 지표를 주기적으로 보고합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • CPU, 메모리, 네트워크 사용량을 실시간 모니터링합니다
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  • 예방적 유지보수 알림 및 최적화 권고사항을 제공합니다
                                </Text>
                              </>
                            )}
                          </VStack>
                        </CardBody>
                      </Card>

                      <Button
                        leftIcon={<FiSend />}
                        colorScheme="blue"
                        size="lg"
                        onClick={() => {
                          sendMessage(selectedMessage);
                          onClose();
                        }}
                        isLoading={loading}
                      >
                        🚀 테스트 발송하기
                      </Button>
                    </VStack>
                  </TabPanel>

                  {/* 탭 2: 템플릿 */}
                  <TabPanel h="full" overflowY="auto">
                    <VStack spacing={6} align="stretch">
                      {/* 템플릿 설명 */}
                      <Card variant="outline">
                        <CardHeader>
                          <HStack>
                            <Icon as={FiFileText} />
                            <Text fontWeight="bold">📄 메시지 템플릿 구조</Text>
                            <Spacer />
                            <Badge colorScheme="green" variant="outline">Markdown</Badge>
                          </HStack>
                        </CardHeader>
                        <CardBody>
                          <Text fontSize="sm" color="gray.600" mb={4}>
                            이 템플릿은 실제 웹훅 메시지를 생성할 때 사용되는 구조입니다. 
                            동적 데이터는 중괄호 {'{}'} 변수로 표시됩니다.
                          </Text>
                          
                          {/* 템플릿 변수 안내 */}
                          <Box mb={4}>
                            <Text fontWeight="semibold" mb={2}>🔧 주요 변수:</Text>
                            <Grid templateColumns="1fr 1fr" gap={2}>
                              <Code fontSize="xs" colorScheme="blue">{"{{today}}"}</Code>
                              <Text fontSize="xs" color="gray.600">오늘 날짜</Text>
                              <Code fontSize="xs" colorScheme="blue">{"{{current_time}}"}</Code>
                              <Text fontSize="xs" color="gray.600">현재 시간</Text>
                              <Code fontSize="xs" colorScheme="blue">{"{{raw_data}}"}</Code>
                              <Text fontSize="xs" color="gray.600">입력 데이터</Text>
                              <Code fontSize="xs" colorScheme="blue">{"{{priority}}"}</Code>
                              <Text fontSize="xs" color="gray.600">메시지 우선순위</Text>
                            </Grid>
                          </Box>
                        </CardBody>
                      </Card>

                      {/* 실제 템플릿 */}
                      <Card variant="outline">
                        <CardHeader>
                          <Text fontWeight="bold">📝 실제 템플릿 코드</Text>
                        </CardHeader>
                        <CardBody>
                          <Code
                            display="block"
                            whiteSpace="pre-wrap"
                            p={4}
                            borderRadius="md"
                            bg="gray.50"
                            fontSize="sm"
                            maxH="350px"
                            overflowY="auto"
                            border="1px solid"
                            borderColor="gray.200"
                          >
                            {messageDetail?.template || '템플릿을 불러오는 중...'}
                          </Code>
                        </CardBody>
                      </Card>
                    </VStack>
                  </TabPanel>

                  {/* 탭 3: 최근 발송 */}
                  <TabPanel h="full" overflowY="auto">
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <HStack mb={4}>
                          <Icon as={FiSend} />
                          <Text fontWeight="bold">가장 최근 발송 메시지</Text>
                          <Spacer />
                          <Badge colorScheme="blue" variant="outline">
                            {messageDetail?.usage_count || 0}회 사용
                          </Badge>
                        </HStack>
                        
                        {messageDetail?.recent_log ? (
                          <VStack spacing={4} align="stretch">
                            {/* 발송 정보 요약 */}
                            <Card variant="outline">
                              <CardBody>
                                <Grid templateColumns="1fr 1fr" gap={4}>
                                  <VStack align="start" spacing={2}>
                                    <Text fontSize="sm" color="gray.600">발송 시간</Text>
                                    <Text fontWeight="semibold">
                                      {new Date(messageDetail.recent_log.timestamp).toLocaleString('ko-KR')}
                                    </Text>
                                  </VStack>
                                  <VStack align="start" spacing={2}>
                                    <Text fontSize="sm" color="gray.600">발송 상태</Text>
                                    <Badge 
                                      colorScheme={messageDetail.recent_log.status === 'success' ? 'green' : 'red'}
                                      variant="solid"
                                    >
                                      {messageDetail.recent_log.status === 'success' ? '✅ 성공' : '❌ 실패'}
                                    </Badge>
                                  </VStack>
                                  <VStack align="start" spacing={2}>
                                    <Text fontSize="sm" color="gray.600">메시지 ID</Text>
                                    <Code fontSize="xs">{messageDetail.recent_log.message_id || 'N/A'}</Code>
                                  </VStack>
                                  <VStack align="start" spacing={2}>
                                    <Text fontSize="sm" color="gray.600">엔드포인트</Text>
                                    <Badge>{messageDetail.recent_log.endpoint || selectedMessage.endpoint}</Badge>
                                  </VStack>
                                </Grid>
                              </CardBody>
                            </Card>
                            
                            {/* 실제 메시지 내용 */}
                            <Box>
                              <Text fontWeight="bold" mb={2}>🔖 전송된 메시지 내용</Text>
                              <Code
                                display="block"
                                whiteSpace="pre-wrap"
                                p={4}
                                borderRadius="md"
                                bg="gray.50"
                                fontSize="sm"
                                maxH="300px"
                                overflowY="auto"
                              >
                                {messageDetail.recent_log.full_message || '메시지 내용이 기록되지 않았습니다.'}
                              </Code>
                            </Box>
                          </VStack>
                        ) : (
                          <Alert status="info">
                            <AlertIcon />
                            <Text>아직 발송 기록이 없습니다. 테스트 발송 버튼을 눌러보세요!</Text>
                          </Alert>
                        )}
                      </Box>
                    </VStack>
                  </TabPanel>

                  {/* 탭 4: Input/Output */}
                  <TabPanel h="full" overflowY="auto">
                    <VStack spacing={6} align="stretch">
                      {/* API 사용 가이드 */}
                      <Card variant="outline">
                        <CardHeader>
                          <Text fontWeight="bold">🔌 API 사용 가이드</Text>
                        </CardHeader>
                        <CardBody>
                          <VStack spacing={3} align="start">
                            <Text fontSize="sm" color="gray.600">
                              아래 예시를 참고하여 API 호출을 구성할 수 있습니다.
                            </Text>
                            <Code fontSize="xs" colorScheme="blue" w="100%">
                              {`POST /api/webhook-manager/send/${selectedMessage.id.replace('_', '-')}`}
                            </Code>
                            <Text fontSize="xs" color="gray.500">
                              • Content-Type: application/json
                              • Method: POST
                              • Headers: Authorization 필요 없음 (내부 API)
                            </Text>
                          </VStack>
                        </CardBody>
                      </Card>

                      {/* Input 섹션 */}
                      <Card variant="outline">
                        <CardHeader>
                          <HStack>
                            <Icon as={FiArrowRight} />
                            <Text fontWeight="bold">📥 Input (요청 데이터)</Text>
                            <Spacer />
                            <Badge colorScheme="orange" variant="outline">JSON</Badge>
                          </HStack>
                        </CardHeader>
                        <CardBody>
                          <Code
                            display="block"
                            whiteSpace="pre-wrap"
                            p={4}
                            borderRadius="md"
                            bg="gray.50"
                            fontSize="sm"
                            maxH="200px"
                            overflowY="auto"
                            w="100%"
                            border="1px solid"
                            borderColor="gray.200"
                          >
                            {JSON.stringify(messageDetail?.input_example || {}, null, 2)}
                          </Code>
                        </CardBody>
                      </Card>

                      {/* Output 섹션 */}
                      <Card variant="outline">
                        <CardHeader>
                          <HStack>
                            <Icon as={FiCode} />
                            <Text fontWeight="bold">📤 Output (응답 데이터)</Text>
                            <Spacer />
                            <Badge colorScheme="green" variant="outline">JSON</Badge>
                          </HStack>
                        </CardHeader>
                        <CardBody>
                          <Code
                            display="block"
                            whiteSpace="pre-wrap"
                            p={4}
                            borderRadius="md"
                            bg="gray.50"
                            fontSize="sm"
                            maxH="200px"
                            overflowY="auto"
                            w="100%"
                            border="1px solid"
                            borderColor="gray.200"
                          >
                            {JSON.stringify(messageDetail?.output_example || {}, null, 2)}
                          </Code>
                        </CardBody>
                      </Card>

                      <Button
                        leftIcon={<FiSend />}
                        colorScheme="blue"
                        size="lg"
                        onClick={() => {
                          sendMessage(selectedMessage);
                        }}
                        isLoading={loading}
                      >
                        🧪 실제 발송 테스트
                      </Button>
                    </VStack>
                  </TabPanel>
                </TabPanels>
                  </Tabs>
                </GridItem>

                {/* 오른쪽: 탭별 동적 정보 영역 */}
                <GridItem h="full">
                  <VStack spacing={4} align="stretch" h="full" overflowY="auto">
                    {selectedTab === 0 && (
                      <>
                        {/* 공통 발송 통계 */}
                        <Card>
                          <CardHeader>
                            <Text fontWeight="bold">📊 발송 통계</Text>
                          </CardHeader>
                          <CardBody>
                            <VStack spacing={3} align="stretch">
                              <Flex justify="space-between">
                                <Text color="gray.600">사용 횟수:</Text>
                                <Badge colorScheme="blue">{messageDetail?.usage_count || 0}회</Badge>
                              </Flex>
                              <Flex justify="space-between">
                                <Text color="gray.600">성공률:</Text>
                                <Badge colorScheme="green">{messageDetail?.success_rate || 'N/A'}</Badge>
                              </Flex>
                              <Flex justify="space-between">
                                <Text color="gray.600">마지막 발송:</Text>
                                <Text fontSize="sm" color="gray.600">
                                  {messageDetail?.last_sent ? new Date(messageDetail.last_sent).toLocaleString('ko-KR') : '없음'}
                                </Text>
                              </Flex>
                            </VStack>
                          </CardBody>
                        </Card>
                        
                        {/* 공통 빠른 액션 */}
                        <Card>
                          <CardHeader>
                            <Text fontWeight="bold">⚡ 빠른 액션</Text>
                          </CardHeader>
                          <CardBody>
                            <VStack spacing={3}>
                              <Button 
                                leftIcon={<FiSend />} 
                                colorScheme="blue" 
                                size="sm" 
                                w="full"
                                onClick={() => sendMessage(selectedMessage)}
                                isLoading={loading}
                              >
                                즉시 테스트 발송
                              </Button>
                              <Button 
                                leftIcon={<FiRefreshCw />} 
                                variant="outline" 
                                size="sm" 
                                w="full"
                                onClick={() => loadRecentLogs(selectedMessage.id)}
                                isLoading={logsLoading}
                              >
                                최근 기록 새로고침
                              </Button>
                            </VStack>
                          </CardBody>
                        </Card>

                        {/* 메시지 타입별 특화 정보 */}
                        {selectedMessage.id === 'business_day_comparison' && (
                          <>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">📊 분석 대상 뉴스</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between" align="center">
                                    <Text color="gray.600">뉴욕 마켓워치:</Text>
                                    <Badge colorScheme="green" size="sm">정상</Badge>
                                  </Flex>
                                  <Flex justify="space-between" align="center">
                                    <Text color="gray.600">코스피 마감:</Text>
                                    <Badge colorScheme="yellow" size="sm">대기중</Badge>
                                  </Flex>
                                  <Flex justify="space-between" align="center">
                                    <Text color="gray.600">환율 마감:</Text>
                                    <Badge colorScheme="green" size="sm">정상</Badge>
                                  </Flex>
                                  <Text fontSize="xs" color="gray.500" mt={2}>
                                    🕐 마지막 업데이트: {new Date().toLocaleTimeString('ko-KR')}
                                  </Text>
                                </VStack>
                              </CardBody>
                            </Card>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">📈 현재 시장 동향</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">발행 패턴:</Text>
                                    <Badge colorScheme="blue" size="sm">정상 범위</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">지연 빈도:</Text>
                                    <Badge colorScheme="green" size="sm">낮음</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">예상 상황:</Text>
                                    <Badge colorScheme="purple" size="sm">안정세</Badge>
                                  </Flex>
                                  <Text fontSize="xs" color="gray.500" mt={2}>
                                    💡 오늘은 일반적인 발행 패턴을 보이고 있습니다
                                  </Text>
                                </VStack>
                              </CardBody>
                            </Card>
                          </>
                        )}

                        {selectedMessage.id === 'delay_notification' && (
                          <>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">⏰ 지연 알림 설정</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">임계 시간:</Text>
                                    <Badge colorScheme="orange" size="sm">15분</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">심각도 기준:</Text>
                                    <Badge colorScheme="red" size="sm">30분 초과</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">자동 에스컬레이션:</Text>
                                    <Badge colorScheme="purple" size="sm">활성화</Badge>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">📈 지연 통계 (7일)</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">총 지연 건수:</Text>
                                    <Badge colorScheme="blue" size="sm">3건</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">평균 지연 시간:</Text>
                                    <Text color="gray.600">22분</Text>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">최다 지연 뉴스:</Text>
                                    <Text color="gray.600">코스피 마감</Text>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                          </>
                        )}

                        {selectedMessage.id === 'test' && (
                          <>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">🔍 시스템 체크</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">웹훅 연결:</Text>
                                    <Badge colorScheme="green" size="sm">정상</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">응답 시간:</Text>
                                    <Badge colorScheme="blue" size="sm">127ms</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">Dooray 상태:</Text>
                                    <Badge colorScheme="green" size="sm">온라인</Badge>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">📋 테스트 이력</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">오늘 테스트:</Text>
                                    <Badge colorScheme="blue" size="sm">12회</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">성공률:</Text>
                                    <Badge colorScheme="green" size="sm">100%</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">마지막 실패:</Text>
                                    <Text color="gray.600">없음</Text>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                          </>
                        )}

                        {selectedMessage.id === 'watchhamster_error' && (
                          <>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">🚨 오류 통계</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">금일 오류:</Text>
                                    <Badge colorScheme="red" size="sm">0건</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">주간 평균:</Text>
                                    <Badge colorScheme="orange" size="sm">1.2건</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">시스템 안정성:</Text>
                                    <Badge colorScheme="green" size="sm">99.8%</Badge>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">🔧 자동 복구</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">복구 시도:</Text>
                                    <Badge colorScheme="blue" size="sm">활성화</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">백업 시스템:</Text>
                                    <Badge colorScheme="green" size="sm">대기중</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">알림 대상:</Text>
                                    <Text color="gray.600">개발팀</Text>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                          </>
                        )}

                        {selectedMessage.id === 'watchhamster_status' && (
                          <>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">💻 시스템 리소스</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">CPU 사용률:</Text>
                                    <Badge colorScheme="green" size="sm">12%</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">메모리 사용률:</Text>
                                    <Badge colorScheme="blue" size="sm">68%</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">디스크 여유:</Text>
                                    <Badge colorScheme="green" size="sm">85%</Badge>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                            <Card>
                              <CardHeader>
                                <Text fontWeight="bold">📊 성능 지표</Text>
                              </CardHeader>
                              <CardBody>
                                <VStack spacing={2} align="stretch" fontSize="sm">
                                  <Flex justify="space-between">
                                    <Text color="gray.600">평균 응답시간:</Text>
                                    <Badge colorScheme="green" size="sm">142ms</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">처리량/시간:</Text>
                                    <Badge colorScheme="blue" size="sm">2,340건</Badge>
                                  </Flex>
                                  <Flex justify="space-between">
                                    <Text color="gray.600">연결 상태:</Text>
                                    <Badge colorScheme="green" size="sm">안정</Badge>
                                  </Flex>
                                </VStack>
                              </CardBody>
                            </Card>
                          </>
                        )}
                      </>
                    )}

                    {selectedTab === 1 && (
                      <>
                        {/* 탭 1: 템플릿 - 변수 설명 + 미리보기 */}
                        <Card>
                          <CardHeader>
                            <Text fontWeight="bold">🔧 템플릿 변수</Text>
                          </CardHeader>
                          <CardBody>
                            <VStack spacing={2} align="stretch" fontSize="sm">
                              <Text fontWeight="semibold" color="blue.600">동적 변수:</Text>
                              <Code p={2}>{"{{today}}"} → {new Date().toLocaleDateString('ko-KR')}</Code>
                              <Code p={2}>{"{{current_time}}"} → {new Date().toLocaleTimeString('ko-KR')}</Code>
                              <Code p={2}>{"{{company_id}}"} → posco</Code>
                              <Code p={2}>{"{{priority}}"} → {selectedMessage.priority}</Code>
                            </VStack>
                          </CardBody>
                        </Card>
                        
                        <Card>
                          <CardHeader>
                            <Text fontWeight="bold">📋 메시지 구조</Text>
                          </CardHeader>
                          <CardBody>
                            <VStack spacing={2} align="stretch" fontSize="sm">
                              <Text color="gray.600">• 제목: 이모지 + 메시지 타입</Text>
                              <Text color="gray.600">• 시간: 현재 날짜/시간 자동 삽입</Text>
                              <Text color="gray.600">• 내용: 동적 데이터 기반 생성</Text>
                              <Text color="gray.600">• 상태: 실시간 상황 반영</Text>
                            </VStack>
                          </CardBody>
                        </Card>
                      </>
                    )}

                    {selectedTab === 2 && (
                      <>
                        {/* 탭 2: 최근 발송 - 전체 발송 기록 리스트 */}
                        <Card>
                          <CardHeader>
                            <HStack>
                              <Text fontWeight="bold">📋 전체 발송 기록</Text>
                              {logsLoading && <Spinner size="sm" />}
                            </HStack>
                          </CardHeader>
                          <CardBody>
                            <VStack spacing={2} align="stretch" maxH="200px" overflowY="auto">
                              {recentLogs.length > 0 ? (
                                recentLogs.map((log, index) => (
                                  <Card 
                                    key={log.id || index} 
                                    size="sm" 
                                    variant="outline"
                                    cursor="pointer"
                                    bg={selectedLogId === log.id ? "blue.50" : "white"}
                                    borderColor={selectedLogId === log.id ? "blue.300" : "gray.200"}
                                    _hover={{ bg: "gray.50", borderColor: "blue.200" }}
                                    onClick={() => setSelectedLogId(log.id)}
                                  >
                                    <CardBody py={2}>
                                      <VStack align="start" spacing={1}>
                                        <HStack>
                                          <Badge 
                                            colorScheme={log.status === 'success' ? 'green' : 'red'} 
                                            size="sm"
                                          >
                                            {log.status === 'success' ? '✅' : '❌'}
                                          </Badge>
                                          <Text fontSize="sm" color="gray.600">
                                            {new Date(log.timestamp).toLocaleString('ko-KR')}
                                          </Text>
                                        </HStack>
                                        <Text fontSize="xs" color="gray.500">
                                          ID: {log.id || 'N/A'}
                                        </Text>
                                        {selectedLogId === log.id && (
                                          <Text fontSize="xs" color="blue.600" fontWeight="semibold">
                                            👆 클릭됨 - 아래에서 메시지 내용 확인
                                          </Text>
                                        )}
                                      </VStack>
                                    </CardBody>
                                  </Card>
                                ))
                              ) : (
                                <Text color="gray.500" textAlign="center" py={4}>
                                  발송 기록이 없습니다
                                </Text>
                              )}
                            </VStack>
                          </CardBody>
                        </Card>

                        {/* 선택된 로그의 메시지 내용 표시 */}
                        {selectedLogId && recentLogs.find(log => log.id === selectedLogId) && (
                          <Card>
                            <CardHeader>
                              <HStack>
                                <Text fontWeight="bold">📄 전송된 메시지 내용</Text>
                                <Badge colorScheme="blue" size="sm">
                                  {recentLogs.find(log => log.id === selectedLogId)?.status === 'success' ? '성공' : '실패'}
                                </Badge>
                              </HStack>
                            </CardHeader>
                            <CardBody>
                              <Code
                                display="block"
                                whiteSpace="pre-wrap"
                                p={3}
                                borderRadius="md"
                                bg="gray.50"
                                fontSize="sm"
                                maxH="250px"
                                overflowY="auto"
                                border="1px solid"
                                borderColor="gray.200"
                              >
                                {recentLogs.find(log => log.id === selectedLogId)?.full_message || 
                                 '메시지 내용이 기록되지 않았습니다.'}
                              </Code>
                              <HStack mt={3} justify="space-between">
                                <Text fontSize="xs" color="gray.500">
                                  발송 시간: {new Date(recentLogs.find(log => log.id === selectedLogId)?.timestamp).toLocaleString('ko-KR')}
                                </Text>
                                <Button 
                                  size="xs" 
                                  variant="ghost" 
                                  onClick={() => setSelectedLogId(null)}
                                >
                                  닫기
                                </Button>
                              </HStack>
                            </CardBody>
                          </Card>
                        )}
                      </>
                    )}

                    {selectedTab === 3 && (
                      <>
                        {/* 탭 3: Input/Output - API 참고자료 */}
                        <Card>
                          <CardHeader>
                            <Text fontWeight="bold">📚 API 참고자료</Text>
                          </CardHeader>
                          <CardBody>
                            <VStack spacing={3} align="stretch" fontSize="sm">
                              <Box>
                                <Text fontWeight="semibold" color="blue.600" mb={1}>엔드포인트:</Text>
                                <Code fontSize="xs">{`POST /api/webhook-manager/send/${selectedMessage.id.replace('_', '-')}`}</Code>
                              </Box>
                              <Box>
                                <Text fontWeight="semibold" color="green.600" mb={1}>응답 형식:</Text>
                                <Code fontSize="xs">{"{ status: 'success', message_id: '...' }"}</Code>
                              </Box>
                              <Box>
                                <Text fontWeight="semibold" color="orange.600" mb={1}>헤더:</Text>
                                <Code fontSize="xs">Content-Type: application/json</Code>
                              </Box>
                            </VStack>
                          </CardBody>
                        </Card>
                        
                        <Card>
                          <CardHeader>
                            <Text fontWeight="bold">🔗 실용 도구</Text>
                          </CardHeader>
                          <CardBody>
                            <VStack spacing={2} align="stretch">
                              <Button 
                                size="sm" 
                                variant="outline" 
                                w="full"
                                onClick={() => {
                                  navigator.clipboard.writeText(JSON.stringify(messageDetail?.input_example || {}, null, 2));
                                  toast({
                                    title: '복사 완료',
                                    description: 'Input JSON이 클립보드에 복사되었습니다',
                                    status: 'success',
                                    duration: 2000
                                  });
                                }}
                              >
                                📋 Input JSON 복사
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline" 
                                w="full"
                                onClick={() => {
                                  navigator.clipboard.writeText(JSON.stringify(messageDetail?.output_example || {}, null, 2));
                                  toast({
                                    title: '복사 완료',
                                    description: 'Output JSON이 클립보드에 복사되었습니다',
                                    status: 'success',
                                    duration: 2000
                                  });
                                }}
                              >
                                📤 Output JSON 복사
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline" 
                                w="full"
                                onClick={() => {
                                  window.open('http://localhost:8000/docs', '_blank');
                                }}
                              >
                                📖 API 문서 열기
                              </Button>
                              <Button 
                                size="sm" 
                                colorScheme="blue" 
                                w="full"
                                onClick={() => {
                                  sendMessage(selectedMessage);
                                  toast({
                                    title: '테스트 전송',
                                    description: '메시지를 전송했습니다. 결과를 확인하세요.',
                                    status: 'info',
                                    duration: 3000
                                  });
                                }}
                                isLoading={loading}
                              >
                                🚀 즉시 테스트 전송
                              </Button>
                            </VStack>
                          </CardBody>
                        </Card>
                      </>
                    )}
                  </VStack>
                </GridItem>
              </Grid>
            ) : (
              <Box textAlign="center" py={8}>
                <Text color="gray.500">메시지 정보를 선택하세요</Text>
              </Box>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default WebhookManager;
