/**
 * 회사 상태 카드 컴포넌트
 * 각 회사의 요약 정보 표시
 */

import React from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  VStack,
  HStack,
  Heading,
  Text,
  Badge,
  Icon,
  Button,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorModeValue
} from '@chakra-ui/react';
import {
  FiHome,
  FiBell,
  FiCheckCircle,
  FiAlertCircle,
  FiActivity
} from 'react-icons/fi';

interface CompanyStatusCardProps {
  company: {
    id: string;
    name: string;
    display_name: string;
    is_active: boolean;
    webhook_count: number;
    total_sent: number;
    success_rate: number;
    last_activity: string;
    news_monitors: number;
    news_status: string;
  };
  onClick: () => void;
}

const getNewsStatusInfo = (status: string) => {
  switch (status) {
    case 'all_ok':
      return { icon: FiCheckCircle, color: 'green', label: '모두 정상' };
    case 'some_delayed':
      return { icon: FiAlertCircle, color: 'yellow', label: '일부 지연' };
    case 'error':
      return { icon: FiAlertCircle, color: 'red', label: '오류 발생' };
    default:
      return { icon: FiActivity, color: 'gray', label: '모니터링 없음' };
  }
};

export const CompanyStatusCard: React.FC<CompanyStatusCardProps> = ({ company, onClick }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  
  const newsStatus = getNewsStatusInfo(company.news_status);

  return (
    <Card
      bg={cardBg}
      borderColor={borderColor}
      borderWidth="2px"
      cursor="pointer"
      onClick={onClick}
      _hover={{
        shadow: 'xl',
        borderColor: 'blue.400',
        bg: hoverBg,
        transform: 'translateY(-4px)'
      }}
      transition="all 0.2s"
    >
      <CardHeader pb={2}>
        <HStack justify="space-between">
          <HStack spacing={2}>
            <Icon as={FiHome} boxSize={5} color="blue.500" />
            <Heading size="md">{company.display_name}</Heading>
          </HStack>
          <Badge colorScheme={company.is_active ? 'green' : 'gray'}>
            {company.is_active ? '활성' : '비활성'}
          </Badge>
        </HStack>
      </CardHeader>

      <CardBody pt={0}>
        <VStack spacing={4} align="stretch">
          {/* 웹훅 통계 */}
          <VStack spacing={2} align="stretch">
            <HStack justify="space-between">
              <HStack spacing={2}>
                <Icon as={FiBell} boxSize={4} color="purple.500" />
                <Text fontSize="sm" fontWeight="medium">웹훅</Text>
              </HStack>
              <Text fontSize="sm" fontWeight="bold">{company.webhook_count}개</Text>
            </HStack>
            
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600">총 발송</Text>
              <Text fontSize="sm" fontWeight="bold">
                {company.total_sent.toLocaleString()}건
              </Text>
            </HStack>
            
            {company.total_sent > 0 && (
              <HStack justify="space-between">
                <Text fontSize="sm" color="gray.600">성공률</Text>
                <Text fontSize="sm" fontWeight="bold" color="green.500">
                  {company.success_rate.toFixed(1)}%
                </Text>
              </HStack>
            )}
          </VStack>

          {/* 뉴스 모니터링 */}
          {company.news_monitors > 0 && (
            <VStack spacing={2} align="stretch">
              <HStack justify="space-between">
                <HStack spacing={2}>
                  <Icon as={FiActivity} boxSize={4} color="cyan.500" />
                  <Text fontSize="sm" fontWeight="medium">뉴스 모니터링</Text>
                </HStack>
                <Text fontSize="sm" fontWeight="bold">{company.news_monitors}개</Text>
              </HStack>
              
              <HStack justify="space-between">
                <Text fontSize="sm" color="gray.600">상태</Text>
                <HStack spacing={1}>
                  <Icon as={newsStatus.icon} boxSize={4} color={`${newsStatus.color}.500`} />
                  <Text fontSize="sm" fontWeight="bold" color={`${newsStatus.color}.500`}>
                    {newsStatus.label}
                  </Text>
                </HStack>
              </HStack>
            </VStack>
          )}

          {/* 마지막 활동 */}
          <Text fontSize="xs" color="gray.500">
            마지막 활동: {new Date(company.last_activity).toLocaleString('ko-KR')}
          </Text>

          {/* 상세보기 버튼 */}
          <Button
            size="sm"
            colorScheme="blue"
            variant="outline"
            width="full"
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
          >
            상세 보기
          </Button>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default CompanyStatusCard;
