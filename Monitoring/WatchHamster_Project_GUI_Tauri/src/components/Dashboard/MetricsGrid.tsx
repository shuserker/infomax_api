import React from 'react';
import {
  SimpleGrid,
  Box,
  Skeleton,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  VStack,
} from '@chakra-ui/react';
import { SystemMetricCard, MetricData } from './SystemMetricCard';

export interface SystemMetrics {
  cpu: MetricData;
  memory: MetricData;
  disk: MetricData;
  network: MetricData;
}

export interface MetricsGridProps {
  metrics?: SystemMetrics;
  isLoading?: boolean;
  error?: string;
  compact?: boolean;
  showTrends?: boolean;
  refreshInterval?: number;
}

const defaultMetricData: MetricData = {
  value: 0,
  unit: '%',
  trend: [],
  timestamp: new Date().toISOString(),
  status: 'normal',
  threshold: {
    warning: 70,
    critical: 90,
  },
};

export const MetricsGrid: React.FC<MetricsGridProps> = ({
  metrics,
  isLoading = false,
  error,
  compact = false,
  showTrends = true,
}) => {
  const renderError = () => {
    if (!error) return null;

    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        <Box>
          <AlertTitle>메트릭 데이터 로드 실패</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Box>
      </Alert>
    );
  };

  const renderLoadingSkeleton = () => {
    return (
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
        {Array.from({ length: 4 }).map((_, index) => (
          <Skeleton
            key={index}
            height={compact ? "100px" : "200px"}
            borderRadius="md"
          />
        ))}
      </SimpleGrid>
    );
  };

  const renderMetrics = () => {
    const metricsData = metrics || {
      cpu: { ...defaultMetricData, unit: '%' },
      memory: { ...defaultMetricData, unit: '%' },
      disk: { ...defaultMetricData, unit: '%' },
      network: { 
        ...defaultMetricData, 
        unit: 'Mbps',
        threshold: { warning: 80, critical: 95 }
      },
    };

    return (
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
        <SystemMetricCard
          title="CPU 사용률"
          type="cpu"
          data={metricsData.cpu}
          isLoading={isLoading}
          showTrend={showTrends}
          compact={compact}
        />
        <SystemMetricCard
          title="메모리 사용률"
          type="memory"
          data={metricsData.memory}
          isLoading={isLoading}
          showTrend={showTrends}
          compact={compact}
        />
        <SystemMetricCard
          title="디스크 사용률"
          type="disk"
          data={metricsData.disk}
          isLoading={isLoading}
          showTrend={showTrends}
          compact={compact}
        />
        <SystemMetricCard
          title="네트워크 상태"
          type="network"
          data={metricsData.network}
          isLoading={isLoading}
          showTrend={showTrends}
          compact={compact}
        />
      </SimpleGrid>
    );
  };

  if (error) {
    return (
      <VStack spacing={4}>
        {renderError()}
        {renderMetrics()}
      </VStack>
    );
  }

  if (isLoading && !metrics) {
    return renderLoadingSkeleton();
  }

  return renderMetrics();
};

export default MetricsGrid;