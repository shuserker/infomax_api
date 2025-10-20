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
  cpu: { warning: 60, critical: 80 },
  memory: { warning: 70, critical: 85 },
  disk: { warning: 80, critical: 90 },
  network: { warning: 70, critical: 85 },
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
    refetchInterval: refreshInterval, // WebSocket 대신 폴링 사용
    retry: 3,
    retryDelay: 1000,
  });

  // WebSocket을 통한 실시간 업데이트 (임시로 비활성화)
  const webSocketOptions = null; // enableRealtime ? {
  //   url: 'ws://localhost:8000/ws/',
  //   enableReconnect: true,
  //   maxReconnectAttempts: 5,
  //   reconnectInterval: 3000,
  // } : null;

  const { lastMessage } = webSocketOptions 
    ? useWebSocket(webSocketOptions)
    : { lastMessage: null };

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
      // 추가 디스크 정보
      used_gb: rawData.disk_used_gb || 0,
      total_gb: rawData.disk_total_gb || 0,
      free_gb: rawData.disk_free_gb || 0,
    };

    // 네트워크 실제 사용률 표시
    const networkUsage = rawData.network_usage || 0;
    const networkStatus = rawData.network_status || 'unknown';
    
    const network: MetricData = {
      value: networkUsage, // 실제 네트워크 사용률 (%)
      unit: '%',
      trend: historyRef.current.get('network') || [],
      timestamp,
      status: networkStatus === 'active' ? 'normal' : 
              networkUsage > 80 ? 'critical' : 
              networkUsage > 60 ? 'warning' : 'normal',
      threshold: DEFAULT_THRESHOLDS.network,
    };

    // 히스토리 업데이트
    updateHistory('cpu', cpu.value);
    updateHistory('memory', memory.value);
    updateHistory('disk', disk.value);
    updateHistory('network', networkUsage); // 네트워크는 실제 사용률로 트렌드 표시

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

  // 연결 상태 확인: API가 정상 작동하면 연결된 것으로 간주
  const actualConnectionStatus = !apiError && !!apiMetrics;

  return {
    metrics,
    isLoading: isApiLoading && !metrics,
    error,
    lastUpdated,
    refreshMetrics,
    isConnected: actualConnectionStatus,
  };
};