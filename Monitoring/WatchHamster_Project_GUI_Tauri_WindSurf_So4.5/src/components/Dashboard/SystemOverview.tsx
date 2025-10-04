/**
 * 전체 시스템 개요 컴포넌트
 * 멀티 테넌트 시스템의 전체 통계 표시
 */

import React from 'react';
import {
  Box,
  Card,
  CardBody,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  HStack,
  Icon,
  Badge,
  Tooltip,
  useColorModeValue
} from '@chakra-ui/react';
import {
  FiHome,
  FiBell,
  FiCheckCircle,
  FiZap,
  FiClock,
  FiActivity
} from 'react-icons/fi';

interface SystemOverviewProps {
  data: {
    total_companies: number;
    active_companies: number;
    total_webhooks_sent: number;
    success_rate: number;
    failed_today: number;
    system_health: string;
    api_response_time_ms: number;
    uptime_seconds: number;
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
  };
  isLoading?: boolean;
}

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) return `${days}일 ${hours}시간`;
  if (hours > 0) return `${hours}시간 ${minutes}분`;
  return `${minutes}분`;
};

const getHealthColor = (health: string) => {
  switch (health) {
    case 'healthy': return 'green';
    case 'warning': return 'yellow';
    case 'critical': return 'red';
    default: return 'gray';
  }
};

const getHealthLabel = (health: string) => {
  switch (health) {
    case 'healthy': return '정상';
    case 'warning': return '주의';
    case 'critical': return '위험';
    default: return '알 수 없음';
  }
};

export const SystemOverview: React.FC<SystemOverviewProps> = ({ data, isLoading = false }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const healthColor = getHealthColor(data.system_health);

  return (
    <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" shadow="md">
      <CardBody>
        <Grid templateColumns="repeat(6, 1fr)" gap={4}>
          {/* 등록된 회사 */}
          <GridItem>
            <Stat>
              <HStack spacing={2} mb={1}>
                <Icon as={FiHome} color="blue.500" />
                <StatLabel fontSize="sm">등록된 회사</StatLabel>
              </HStack>
              <StatNumber fontSize="2xl">{data.total_companies}개</StatNumber>
              <StatHelpText fontSize="xs">
                활성: {data.active_companies}개
              </StatHelpText>
            </Stat>
          </GridItem>

          {/* 총 웹훅 발송 */}
          <GridItem>
            <Stat>
              <HStack spacing={2} mb={1}>
                <Icon as={FiBell} color="purple.500" />
                <StatLabel fontSize="sm">총 웹훅 발송</StatLabel>
              </HStack>
              <StatNumber fontSize="2xl">
                {data.total_webhooks_sent.toLocaleString()}
              </StatNumber>
              <StatHelpText fontSize="xs">
                오늘 실패: {data.failed_today}건
              </StatHelpText>
            </Stat>
          </GridItem>

          {/* 성공률 */}
          <GridItem>
            <Stat>
              <HStack spacing={2} mb={1}>
                <Icon as={FiCheckCircle} color="green.500" />
                <StatLabel fontSize="sm">성공률</StatLabel>
              </HStack>
              <StatNumber fontSize="2xl" color="green.500">
                {data.success_rate.toFixed(1)}%
              </StatNumber>
              <StatHelpText fontSize="xs">
                {data.total_webhooks_sent > 0 ? '정상 작동' : '데이터 없음'}
              </StatHelpText>
            </Stat>
          </GridItem>

          {/* 시스템 상태 */}
          <GridItem>
            <Stat>
              <HStack spacing={2} mb={1}>
                <Icon as={FiActivity} color={`${healthColor}.500`} />
                <StatLabel fontSize="sm">시스템 상태</StatLabel>
              </HStack>
              <HStack spacing={2}>
                <Badge colorScheme={healthColor} fontSize="lg" px={3} py={1}>
                  {getHealthLabel(data.system_health)}
                </Badge>
              </HStack>
              <StatHelpText fontSize="xs">
                CPU {data.cpu_usage}% / 메모리 {data.memory_usage}%
              </StatHelpText>
            </Stat>
          </GridItem>

          {/* API 응답 시간 */}
          <GridItem>
            <Stat>
              <HStack spacing={2} mb={1}>
                <Icon as={FiZap} color="yellow.500" />
                <StatLabel fontSize="sm">API 응답</StatLabel>
              </HStack>
              <StatNumber fontSize="2xl">
                {data.api_response_time_ms.toFixed(1)}ms
              </StatNumber>
              <StatHelpText fontSize="xs">
                매우 빠름
              </StatHelpText>
            </Stat>
          </GridItem>

          {/* 업타임 */}
          <GridItem>
            <Stat>
              <HStack spacing={2} mb={1}>
                <Icon as={FiClock} color="cyan.500" />
                <StatLabel fontSize="sm">업타임</StatLabel>
              </HStack>
              <Tooltip label={`${data.uptime_seconds.toLocaleString()}초`}>
                <StatNumber fontSize="2xl">
                  {formatUptime(data.uptime_seconds)}
                </StatNumber>
              </Tooltip>
              <StatHelpText fontSize="xs">
                안정적
              </StatHelpText>
            </Stat>
          </GridItem>
        </Grid>
      </CardBody>
    </Card>
  );
};

export default SystemOverview;
