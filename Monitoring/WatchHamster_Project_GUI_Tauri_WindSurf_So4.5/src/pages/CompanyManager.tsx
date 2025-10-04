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
  HStack,
  Avatar,
  IconButton,
  useToast,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Divider,
  Alert,
  AlertIcon,
  Stat,
  StatLabel,
  StatNumber,
  Code
} from '@chakra-ui/react';
import { FiPlus, FiEdit2, FiTrash2, FiActivity, FiBarChart2, FiRefreshCw } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { CompanyForm } from '@/components/CompanyForm';

interface Company {
  id: string;
  name: string;
  display_name: string;
  logo_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface CompanyDetail {
  company: Company;
  webhooks: any[];
  api_configs: any[];
  stats: {
    total_sent: number;
    successful_sends: number;
    failed_sends: number;
  };
  last_activity?: string;
}

export const CompanyManager: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<CompanyDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isAddOpen, onOpen: onAddOpen, onClose: onAddClose } = useDisclosure();
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/companies');
      const data = await res.json();
      setCompanies(data);
    } catch (err: any) {
      toast({
        title: '회사 목록 로드 실패',
        description: err.message,
        status: 'error',
        duration: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const viewCompanyDetail = async (companyId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/companies/${companyId}`);
      const data = await res.json();
      setSelectedCompany(data);
      onOpen();
    } catch (err: any) {
      toast({
        title: '회사 정보 로드 실패',
        description: err.message,
        status: 'error',
        duration: 3000
      });
    }
  };

  const deleteCompany = async (companyId: string, companyName: string) => {
    if (!confirm(`${companyName}을(를) 삭제하시겠습니까?\n\n모든 웹훅 설정, API 설정, 로그가 함께 삭제됩니다.`)) {
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/api/companies/${companyId}`, {
        method: 'DELETE'
      });
      
      if (res.ok) {
        toast({
          title: '삭제 완료',
          description: `${companyName}이(가) 삭제되었습니다.`,
          status: 'success',
          duration: 3000
        });
        loadCompanies();
      }
    } catch (err: any) {
      toast({
        title: '삭제 실패',
        description: err.message,
        status: 'error',
        duration: 3000
      });
    }
  };

  return (
    <Box p={6}>
      <Flex mb={6} align="center">
        <Heading size="lg">🏢 회사 관리</Heading>
        <Spacer />
        <Button
          leftIcon={<FiRefreshCw />}
          onClick={loadCompanies}
          isLoading={loading}
          variant="outline"
          mr={2}
        >
          새로고침
        </Button>
        <Button
          leftIcon={<FiPlus />}
          colorScheme="blue"
          onClick={onAddOpen}
        >
          회사 추가
        </Button>
      </Flex>

      {/* 회사 목록 */}
      <Grid templateColumns="repeat(auto-fill, minmax(400px, 1fr))" gap={6}>
        {companies.map((company) => (
          <GridItem key={company.id}>
            <Card
              cursor="pointer"
              _hover={{ shadow: 'lg', borderColor: 'blue.300' }}
              onClick={() => viewCompanyDetail(company.id)}
            >
              <CardHeader>
                <Flex align="center" gap={3}>
                  <Avatar
                    size="md"
                    src={company.logo_url}
                    name={company.name}
                  />
                  <Box flex={1}>
                    <Heading size="md">{company.display_name}</Heading>
                    <Text fontSize="sm" color="gray.600">
                      {company.name}
                    </Text>
                  </Box>
                  <Badge colorScheme={company.is_active ? 'green' : 'gray'}>
                    {company.is_active ? '활성' : '비활성'}
                  </Badge>
                </Flex>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch">
                  <Divider />
                  
                  <HStack justify="space-between">
                    <Text fontSize="sm" color="gray.600">등록일</Text>
                    <Text fontSize="sm" fontWeight="bold">
                      {new Date(company.created_at).toLocaleDateString('ko-KR')}
                    </Text>
                  </HStack>
                  
                  <HStack justify="space-between">
                    <Text fontSize="sm" color="gray.600">마지막 수정</Text>
                    <Text fontSize="sm">
                      {new Date(company.updated_at).toLocaleDateString('ko-KR')}
                    </Text>
                  </HStack>

                  <Divider />
                  
                  <HStack spacing={2}>
                    <Button
                      size="sm"
                      leftIcon={<FiActivity />}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/webhooks?company=${company.id}`);
                      }}
                      flex={1}
                    >
                      웹훅 관리
                    </Button>
                    <Button
                      size="sm"
                      leftIcon={<FiBarChart2 />}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/dashboard?company=${company.id}`);
                      }}
                      flex={1}
                    >
                      대시보드
                    </Button>
                  </HStack>
                  
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="수정"
                      icon={<FiEdit2 />}
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        toast({
                          title: '준비 중',
                          description: '회사 수정 기능은 곧 구현됩니다',
                          status: 'info',
                          duration: 2000
                        });
                      }}
                      flex={1}
                    />
                    <IconButton
                      aria-label="삭제"
                      icon={<FiTrash2 />}
                      colorScheme="red"
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteCompany(company.id, company.display_name);
                      }}
                      flex={1}
                    />
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          </GridItem>
        ))}
      </Grid>

      {companies.length === 0 && !loading && (
        <Alert status="info">
          <AlertIcon />
          <Text>등록된 회사가 없습니다. "회사 추가" 버튼을 클릭하여 새 회사를 추가하세요.</Text>
        </Alert>
      )}

      {/* 회사 상세 모달 */}
      <Modal isOpen={isOpen} onClose={onClose} size="4xl">
        <ModalOverlay />
        <ModalContent maxH="90vh">
          <ModalHeader>
            <Flex align="center" gap={3}>
              {selectedCompany?.company.logo_url && (
                <Avatar
                  size="sm"
                  src={selectedCompany.company.logo_url}
                  name={selectedCompany.company.name}
                />
              )}
              <Box>
                <Text>{selectedCompany?.company.display_name}</Text>
                <Text fontSize="sm" color="gray.600" fontWeight="normal">
                  {selectedCompany?.company.name}
                </Text>
              </Box>
            </Flex>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody overflowY="auto">
            {selectedCompany && (
              <VStack spacing={6} align="stretch">
                {/* 통계 */}
                <Box>
                  <Heading size="sm" mb={3}>📊 웹훅 통계</Heading>
                  <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                    <Card>
                      <CardBody>
                        <Stat>
                          <StatLabel>총 발송</StatLabel>
                          <StatNumber>{selectedCompany.stats.total_sent}</StatNumber>
                        </Stat>
                      </CardBody>
                    </Card>
                    <Card>
                      <CardBody>
                        <Stat>
                          <StatLabel>성공</StatLabel>
                          <StatNumber color="green.500">
                            {selectedCompany.stats.successful_sends}
                          </StatNumber>
                        </Stat>
                      </CardBody>
                    </Card>
                    <Card>
                      <CardBody>
                        <Stat>
                          <StatLabel>실패</StatLabel>
                          <StatNumber color="red.500">
                            {selectedCompany.stats.failed_sends}
                          </StatNumber>
                        </Stat>
                      </CardBody>
                    </Card>
                  </Grid>
                </Box>

                {/* 웹훅 설정 */}
                <Box>
                  <Heading size="sm" mb={3}>📬 웹훅 설정 ({selectedCompany.webhooks.length}개)</Heading>
                  <VStack spacing={3} align="stretch">
                    {selectedCompany.webhooks.map((webhook: any) => (
                      <Card key={webhook.id}>
                        <CardBody>
                          <Flex justify="space-between" align="start">
                            <Box flex={1}>
                              <Text fontWeight="bold" mb={1}>{webhook.bot_name}</Text>
                              <Text fontSize="xs" color="gray.600" mb={2}>
                                채널: {webhook.channel_name}
                              </Text>
                              <Code fontSize="xs" display="block" p={2} borderRadius="md">
                                {webhook.webhook_url}
                              </Code>
                            </Box>
                            <Badge colorScheme="green" ml={2}>활성</Badge>
                          </Flex>
                        </CardBody>
                      </Card>
                    ))}
                  </VStack>
                </Box>

                {/* API 설정 */}
                <Box>
                  <Heading size="sm" mb={3}>🔌 API 설정 ({selectedCompany.api_configs.length}개)</Heading>
                  <VStack spacing={3} align="stretch">
                    {selectedCompany.api_configs.map((api: any) => (
                      <Card key={api.id}>
                        <CardBody>
                          <Flex justify="space-between" align="start">
                            <Box flex={1}>
                              <Text fontWeight="bold" mb={1}>{api.api_name}</Text>
                              <Code fontSize="xs" display="block" p={2} borderRadius="md" mb={2}>
                                {api.api_url}
                              </Code>
                              {api.config && (
                                <Box mt={2}>
                                  <Text fontSize="xs" color="gray.600" mb={1}>엔드포인트:</Text>
                                  <Code fontSize="xs" display="block" p={2} borderRadius="md">
                                    {JSON.stringify(api.config, null, 2)}
                                  </Code>
                                </Box>
                              )}
                            </Box>
                            <Badge colorScheme="blue" ml={2}>활성</Badge>
                          </Flex>
                        </CardBody>
                      </Card>
                    ))}
                  </VStack>
                </Box>

                {/* 기본 정보 */}
                <Box>
                  <Heading size="sm" mb={3}>ℹ️ 기본 정보</Heading>
                  <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                    <Box>
                      <Text fontSize="sm" color="gray.600">회사 ID</Text>
                      <Code fontSize="sm">{selectedCompany.company.id}</Code>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">상태</Text>
                      <Badge colorScheme={selectedCompany.company.is_active ? 'green' : 'gray'}>
                        {selectedCompany.company.is_active ? '활성' : '비활성'}
                      </Badge>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">등록일</Text>
                      <Text fontSize="sm">
                        {new Date(selectedCompany.company.created_at).toLocaleString('ko-KR')}
                      </Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">마지막 수정</Text>
                      <Text fontSize="sm">
                        {new Date(selectedCompany.company.updated_at).toLocaleString('ko-KR')}
                      </Text>
                    </Box>
                  </Grid>
                </Box>
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button
              colorScheme="blue"
              mr={3}
              onClick={() => {
                if (selectedCompany) {
                  navigate(`/webhooks?company=${selectedCompany.company.id}`);
                  onClose();
                }
              }}
            >
              웹훅 관리
            </Button>
            <Button onClick={onClose}>닫기</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* 회사 추가 모달 */}
      <Modal isOpen={isAddOpen} onClose={onAddClose} size="4xl">
        <ModalOverlay />
        <ModalContent maxH="90vh">
          <ModalHeader>🏢 신규 회사 추가</ModalHeader>
          <ModalCloseButton />
          <ModalBody overflowY="auto">
            <CompanyForm
              onSuccess={() => {
                onAddClose();
                loadCompanies();
              }}
              onCancel={onAddClose}
            />
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default CompanyManager;
