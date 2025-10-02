import React from 'react';
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Progress,
  HStack,
  VStack,
  Icon,
  Badge,
  Tooltip,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
} from '@chakra-ui/react';
import {
  FiCpu,
  FiHardDrive,
  FiActivity,
  FiWifi,
  FiAlertTriangle,
} from 'react-icons/fi';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis } from 'recharts';

export interface MetricData {
  value: number;
  unit: string;
  trend: number[];
  timestamp: string;
  status: 'normal' | 'warning' | 'critical';
  threshold?: {
    warning: number;
    critical: number;
  };
}

export interface SystemMetricCardProps {
  title: string;
  type: 'cpu' | 'memory' | 'disk' | 'network';
  data: MetricData;
  isLoading?: boolean;
  showTrend?: boolean;
  compact?: boolean;
}

const getMetricIcon = (type: string) => {
  switch (type) {
    case 'cpu':
      return FiCpu;
    case 'memory':
      return FiActivity;
    case 'disk':
      return FiHardDrive;
    case 'network':
      return FiWifi;
    default:
      return FiActivity;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'normal':
      return 'green';
    case 'warning':
      return 'yellow';
    case 'critical':
      return 'red';
    default:
      return 'gray';
  }
};

const getProgressColor = (value: number, threshold?: { warning: number; critical: number }) => {
  if (!threshold) return 'blue';
  
  if (value >= threshold.critical) return 'red';
  if (value >= threshold.warning) return 'yellow';
  return 'green';
};

export const SystemMetricCard: React.FC<SystemMetricCardProps> = ({
  title,
  type,
  data,
  isLoading = false,
  showTrend = true,
  compact = false,
}) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const valueColor = useColorModeValue('gray.900', 'white');

  const IconComponent = getMetricIcon(type);
  const statusColor = getStatusColor(data.status);
  const progressColor = getProgressColor(data.value, data.threshold);

  // 트렌드 데이터를 차트용으로 변환
  const trendData = data.trend.map((value, index) => ({
    index,
    value,
  }));

  const renderAlert = () => {
    if (data.status === 'normal') return null;

    const alertStatus = data.status === 'critical' ? 'error' : 'warning';
    const alertMessage = data.status === 'critical' 
      ? '임계 수준에 도달했습니다' 
      : '주의가 필요합니다';

    return (
      <Alert status={alertStatus} size="sm" borderRadius="md" mb={2}>
        <AlertIcon />
        <AlertTitle fontSize="sm">{alertMessage}</AlertTitle>
      </Alert>
    );
  };

  const renderTrendChart = () => {
    if (!showTrend || data.trend.length === 0) return null;

    return (
      <Box height="60px" mt={2}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trendData}>
            <XAxis hide />
            <YAxis hide />
            <Line
              type="monotone"
              dataKey="value"
              stroke={`var(--chakra-colors-${progressColor}-500)`}
              strokeWidth={2}
              dot={false}
              animationDuration={300}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    );
  };

  if (compact) {
    return (
      <Card
        bg={cardBg}
        borderColor={borderColor}
        borderWidth="1px"
        size="sm"
        _hover={{ shadow: 'md' }}
        transition="all 0.2s"
      >
        <CardBody p={3}>
          <HStack spacing={3}>
            <Icon
              as={IconComponent}
              boxSize={5}
              color={`${statusColor}.500`}
            />
            <VStack spacing={0} align="start" flex={1}>
              <Text fontSize="sm" color={textColor} fontWeight="medium">
                {title}
              </Text>
              <HStack spacing={2}>
                <Text fontSize="lg" fontWeight="bold" color={valueColor}>
                  {data.value.toFixed(1)}{data.unit}
                </Text>
                <Badge colorScheme={statusColor} size="sm">
                  {data.status}
                </Badge>
              </HStack>
            </VStack>
          </HStack>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card
      bg={cardBg}
      borderColor={borderColor}
      borderWidth="1px"
      _hover={{ shadow: 'lg' }}
      transition="all 0.2s"
    >
      <CardHeader pb={2}>
        <HStack justify="space-between">
          <HStack spacing={3}>
            <Icon
              as={IconComponent}
              boxSize={6}
              color={`${statusColor}.500`}
            />
            <Heading size="md" color={valueColor}>
              {title}
            </Heading>
          </HStack>
          <Badge colorScheme={statusColor} variant="subtle">
            {data.status}
          </Badge>
        </HStack>
      </CardHeader>

      <CardBody pt={0}>
        <VStack spacing={4} align="stretch">
          {renderAlert()}
          
          <VStack spacing={2} align="stretch">
            <HStack justify="space-between">
              <Text fontSize="2xl" fontWeight="bold" color={valueColor}>
                {isLoading ? '...' : `${data.value.toFixed(1)}${data.unit}`}
              </Text>
              {data.threshold && (
                <Tooltip
                  label={`경고: ${data.threshold.warning}${data.unit}, 위험: ${data.threshold.critical}${data.unit}`}
                  placement="top"
                >
                  <Icon as={FiAlertTriangle} color="gray.400" />
                </Tooltip>
              )}
            </HStack>

            <Progress
              value={data.value}
              max={100}
              colorScheme={progressColor}
              size="lg"
              borderRadius="md"
              isAnimated
              hasStripe={data.status !== 'normal'}
            />

            {data.threshold && (
              <HStack justify="space-between" fontSize="xs" color={textColor}>
                <Text>0{data.unit}</Text>
                <Text>경고: {data.threshold.warning}{data.unit}</Text>
                <Text>위험: {data.threshold.critical}{data.unit}</Text>
                <Text>100{data.unit}</Text>
              </HStack>
            )}
          </VStack>

          {renderTrendChart()}

          <HStack justify="space-between" fontSize="sm" color={textColor}>
            <Text>마지막 업데이트</Text>
            <Text>{new Date(data.timestamp).toLocaleTimeString('ko-KR')}</Text>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default SystemMetricCard;