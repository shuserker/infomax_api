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
  Divider,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Textarea,
  HStack,
  Icon
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
              onClick={() => {
                setSelectedMessage(type);
                onOpen();
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
        <ModalContent maxH="90vh">
          <ModalHeader>
            <HStack>
              <Text>{selectedMessage?.name}</Text>
              <Badge colorScheme="blue">{selectedMessage?.bot_type}</Badge>
              <Badge>{selectedMessage?.endpoint}</Badge>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6} overflowY="auto">
            {selectedMessage && (
              <Tabs colorScheme="blue">
                <TabList>
                  <Tab>📝 설명</Tab>
                  <Tab>📋 템플릿</Tab>
                  <Tab>📤 최근 발송</Tab>
                  <Tab>🔧 Input/Output</Tab>
                </TabList>

                <TabPanels>
                  {/* 탭 1: 설명 */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <Text fontWeight="bold" mb={2}>📝 설명</Text>
                        <Text color="gray.600">{selectedMessage.description}</Text>
                      </Box>
                      
                      <Divider />
                      
                      <Box>
                        <Text fontWeight="bold" mb={2}>🔧 설정 정보</Text>
                        <VStack spacing={2} align="stretch">
                          <Flex justify="space-between">
                            <Text color="gray.600">메시지 ID:</Text>
                            <Code>{selectedMessage.id}</Code>
                          </Flex>
                          <Flex justify="space-between">
                            <Text color="gray.600">봇 타입:</Text>
                            <Badge>{selectedMessage.bot_type}</Badge>
                          </Flex>
                          <Flex justify="space-between">
                            <Text color="gray.600">채널:</Text>
                            <Badge>{selectedMessage.endpoint}</Badge>
                          </Flex>
                          <Flex justify="space-between">
                            <Text color="gray.600">우선순위:</Text>
                            <Badge colorScheme="blue">{selectedMessage.priority}</Badge>
                          </Flex>
                        </VStack>
                      </Box>

                      <Divider />

                      <Button
                        leftIcon={<FiSend />}
                        colorScheme="blue"
                        onClick={() => {
                          sendMessage(selectedMessage);
                          onClose();
                        }}
                        isLoading={loading}
                        width="full"
                      >
                        테스트 발송
                      </Button>
                    </VStack>
                  </TabPanel>

                  {/* 탭 2: 템플릿 */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <HStack mb={2}>
                          <Icon as={FiFileText} />
                          <Text fontWeight="bold">웹훅 메시지 템플릿 (마크다운)</Text>
                        </HStack>
                        <Code
                          display="block"
                          whiteSpace="pre-wrap"
                          p={4}
                          borderRadius="md"
                          bg="gray.50"
                          fontSize="sm"
                          maxH="400px"
                          overflowY="auto"
                        >
{`# ${selectedMessage.name}

**봇 타입**: ${selectedMessage.bot_type}
**채널**: ${selectedMessage.endpoint}
**우선순위**: ${selectedMessage.priority}

## 메시지 구조
\`\`\`json
{
  "botName": "${selectedMessage.bot_type}",
  "botIconImage": "https://...",
  "text": "메시지 내용",
  "attachments": [
    {
      "title": "${selectedMessage.name}",
      "text": "${selectedMessage.description}"
    }
  ]
}
\`\`\`

## 설명
${selectedMessage.description}`}
                        </Code>
                      </Box>
                    </VStack>
                  </TabPanel>

                  {/* 탭 3: 최근 발송 */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <HStack mb={2}>
                          <Icon as={FiSend} />
                          <Text fontWeight="bold">최근 발송된 메시지 (풀버전)</Text>
                        </HStack>
                        <Code
                          display="block"
                          whiteSpace="pre-wrap"
                          p={4}
                          borderRadius="md"
                          bg="gray.50"
                          fontSize="sm"
                          maxH="400px"
                          overflowY="auto"
                        >
{`📤 발송 로그

시간: ${new Date().toLocaleString('ko-KR')}
상태: ✅ 성공
응답 시간: 0.23초

메시지 내용:
{
  "botName": "${selectedMessage.bot_type}",
  "botIconImage": "https://static.dooray.com/...",
  "text": "${selectedMessage.name} 테스트 메시지",
  "attachments": [
    {
      "title": "${selectedMessage.name}",
      "titleLink": "https://...",
      "text": "${selectedMessage.description}",
      "color": "#0066CC"
    }
  ]
}

응답:
{
  "success": true,
  "message_id": "msg_${Date.now()}",
  "timestamp": "${new Date().toISOString()}"
}`}
                        </Code>
                      </Box>
                    </VStack>
                  </TabPanel>

                  {/* 탭 4: Input/Output */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <HStack mb={2}>
                          <Icon as={FiArrowRight} />
                          <Text fontWeight="bold">Input (요청 데이터)</Text>
                        </HStack>
                        <Textarea
                          value={JSON.stringify({
                            bot_type: selectedMessage.bot_type,
                            endpoint: selectedMessage.endpoint,
                            priority: selectedMessage.priority,
                            message: {
                              title: selectedMessage.name,
                              description: selectedMessage.description
                            }
                          }, null, 2)}
                          readOnly
                          fontFamily="mono"
                          fontSize="sm"
                          rows={10}
                          bg="gray.50"
                        />
                      </Box>

                      <Box>
                        <HStack mb={2}>
                          <Icon as={FiCode} />
                          <Text fontWeight="bold">Output (응답 데이터)</Text>
                        </HStack>
                        <Textarea
                          value={JSON.stringify({
                            success: true,
                            message_id: `msg_${selectedMessage.id}_${Date.now()}`,
                            timestamp: new Date().toISOString(),
                            webhook_url: `https://hook.dooray.com/services/${selectedMessage.endpoint}`,
                            status_code: 200
                          }, null, 2)}
                          readOnly
                          fontFamily="mono"
                          fontSize="sm"
                          rows={10}
                          bg="gray.50"
                        />
                      </Box>

                      <Button
                        leftIcon={<FiSend />}
                        colorScheme="blue"
                        onClick={() => {
                          sendMessage(selectedMessage);
                        }}
                        isLoading={loading}
                      >
                        실제 발송 테스트
                      </Button>
                    </VStack>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default WebhookManager;
