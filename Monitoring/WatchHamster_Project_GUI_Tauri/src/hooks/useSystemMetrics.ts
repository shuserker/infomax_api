import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useWebSocket } from './useWebSocket';
import { apiService } from '../services/api';
import { SystemMetrics } from '../components/Dashboard/MetricsGrid';
import { MetricData } from '../components/Dashboard/SystemMetricCard';

export interface UseSystemMetricsOptions {
  refreshInterval?: number;
  enableRealtime?: boolean;
  historySize?: number;
}

export interface SystemMetricsHook {
  metrics: SystemMetrics | undefined;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  refreshMetrics: () => void;
  isConnected: boolean;
}

const DEFAULT_THRESHOLDS = {
  cpu: { warning: 70, critical: 90 },
  memory: { warning: 80, critical: 95 },
  disk: { warning: 85, critical: 95 },
  network: { warning: 80, critical: 95 },
};

const getMetricStatus = (value: number, threshold: { warning: number; critical: number }): 'normal' | 'warning' | 'critical' => {
  if (value >= threshold.critical) return 'critical';
  if (value >= threshold.warning) return 'warning';
  return 'normal';
};

export const useSystemMetrics = (options: UseSystemMetricsOptions = {}): SystemMetricsHook => {
  const {
    refreshInterval = 5000,
    enableRealtime = true,
    historySize = 20,
  } = options;

  const [metrics, setMetrics] = useState<SystemMetrics | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const historyRef = useRef<Map<string, number[]>>(new Map([
    ['cpu', []],
    ['memory', []],
    ['disk', []],
    ['network', []],
  ]));

  // REST API를 통한 메트릭 조회
  const {
    data: apiMetrics,
    isLoading: isApiLoading,
    error: apiError,
    refetch,
  } = useQuery({
    queryKey: ['system-metrics'],
    queryFn: async () => {
      try {
        const response = await apiService.getSystemMetrics();
        return response;
      } catch (err) {
        console.error('메트릭 API 호출 실패:', err);
        throw err;
      }
    },
    refetchInterval: enableRealtime ? false : refreshInterval,
    retry: 3,
    retryDelay: 1000,
  });

  // WebSocket을 통한 실시간 업데이트
  const webSocketOptions = enableRealtime ? {
    url: 'ws://localhost:8000/ws',
    enableReconnect: true,
    maxReconnectAttempts: 5,
    reconnectInterval: 3000,
  } : null;

  const { lastMessage, isConnected } = webSocketOptions 
    ? useWebSocket(webSocketOptions)
    : { lastMessage: null, isConnected: false };

  // 히스토리 데이터 업데이트
  const updateHistory = useCallback((metricType: string, value: number) => {
    const history = historyRef.current.get(metricType) || [];
    const newHistory = [...history, value];
    
    if (newHistory.length > historySize) {
      newHistory.shift();
    }
    
    historyRef.current.set(metricType, newHistory);
  }, [historySize]);

  // 메트릭 데이터 변환
  const transformMetricData = useCallback((rawData: any): SystemMetrics => {
    const timestamp = new Date().toISOString();
    
    const cpu: MetricData = {
      value: rawData.cpu_percent || 0,
      unit: '%',
      trend: historyRef.current.get('cpu') || [],
      timestamp,
      status: getMetricStatus(rawData.cpu_percent || 0, DEFAULT_THRESHOLDS.cpu),
      threshold: DEFAULT_THRESHOLDS.cpu,
    };

    const memory: MetricData = {
      value: rawData.memory_percent || 0,
      unit: '%',
      trend: historyRef.current.get('memory') || [],
      timestamp,
      status: getMetricStatus(rawData.memory_percent || 0, DEFAULT_THRESHOLDS.memory),
      threshold: DEFAULT_THRESHOLDS.memory,
    };

    const disk: MetricData = {
      value: rawData.disk_usage || 0,
      unit: '%',
      trend: historyRef.current.get('disk') || [],
      timestamp,
      status: getMetricStatus(rawData.disk_usage || 0, DEFAULT_THRESHOLDS.disk),
      threshold: DEFAULT_THRESHOLDS.disk,
    };

    const networkValue = rawData.network_status === 'connected' ? 100 : 0;
    const network: MetricData = {
      value: networkValue,
      unit: '%',
      trend: historyRef.current.get('network') || [],
      timestamp,
      status: rawData.network_status === 'connected' ? 'normal' : 'critical',
      threshold: DEFAULT_THRESHOLDS.network,
    };

    // 히스토리 업데이트
    updateHistory('cpu', cpu.value);
    updateHistory('memory', memory.value);
    updateHistory('disk', disk.value);
    updateHistory('network', network.value);

    return { cpu, memory, disk, network };
  }, [updateHistory]);

  // API 데이터 처리
  useEffect(() => {
    if (apiMetrics) {
      try {
        const transformedMetrics = transformMetricData(apiMetrics);
        setMetrics(transformedMetrics);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        console.error('메트릭 데이터 변환 실패:', err);
        setError('메트릭 데이터 처리 중 오류가 발생했습니다.');
      }
    }
  }, [apiMetrics, transformMetricData]);

  // WebSocket 메시지 처리
  useEffect(() => {
    if (lastMessage && enableRealtime) {
      try {
        const message = JSON.parse(lastMessage.data);
        
        if (message.type === 'metrics_update' && message.data) {
          const transformedMetrics = transformMetricData(message.data);
          setMetrics(transformedMetrics);
          setLastUpdated(new Date());
          setError(null);
        }
      } catch (err) {
        console.error('WebSocket 메시지 처리 실패:', err);
        // WebSocket 오류는 무시하고 API 폴링으로 대체
      }
    }
  }, [lastMessage, enableRealtime, transformMetricData]);

  // API 오류 처리
  useEffect(() => {
    if (apiError) {
      const errorMessage = apiError instanceof Error 
        ? apiError.message 
        : '메트릭 데이터를 가져올 수 없습니다.';
      setError(errorMessage);
    }
  }, [apiError]);

  const refreshMetrics = useCallback(() => {
    refetch();
  }, [refetch]);

  return {
    metrics,
    isLoading: isApiLoading && !metrics,
    error,
    lastUpdated,
    refreshMetrics,
    isConnected: enableRealtime ? isConnected : true,
  };
};