import { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { LogEntry, LogFilter } from '../types/logs';
import { logsApiClient } from '../services/api';

interface UseLogViewerOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  pageSize?: number;
  maxEntries?: number;
}

interface LogResponse {
  logs: LogEntry[];
  total: number;
  hasMore: boolean;
}

/**
 * 로그 뷰어를 위한 커스텀 훅
 */
export const useLogViewer = (options: UseLogViewerOptions = {}) => {
  const {
    autoRefresh = true,
    refreshInterval = 5000,
    pageSize = 100,
    maxEntries = 1000,
  } = options;

  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<LogFilter>({});
  const [page, setPage] = useState(0);
  const [allLogs, setAllLogs] = useState<LogEntry[]>([]);

  // 로그 데이터 쿼리
  const {
    data: logResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['logs', filter, page],
    queryFn: async (): Promise<LogResponse> => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: pageSize.toString(),
      });

      // 필터 파라미터 추가
      if (filter.level && filter.level.length > 0) {
        params.append('levels', filter.level.join(','));
      }
      if (filter.source && filter.source.length > 0) {
        params.append('sources', filter.source.join(','));
      }
      if (filter.search) {
        params.append('search', filter.search);
      }
      if (filter.startTime) {
        params.append('start_time', filter.startTime);
      }
      if (filter.endTime) {
        params.append('end_time', filter.endTime);
      }

      const response = await logsApiClient.get(`/api/logs?${params.toString()}`);
      return response.data;
    },
    refetchInterval: autoRefresh ? refreshInterval : false,
    staleTime: 1000,
  });

  // 로그 데이터 누적
  useEffect(() => {
    if (logResponse) {
      if (page === 0) {
        // 첫 페이지이거나 필터가 변경된 경우 새로 시작
        setAllLogs(logResponse.logs);
      } else {
        // 추가 페이지 로드
        setAllLogs(prev => {
          const newLogs = [...prev, ...logResponse.logs];
          // 최대 엔트리 수 제한
          return newLogs.slice(0, maxEntries);
        });
      }
    }
  }, [logResponse, page, maxEntries]);

  // 필터 변경 처리
  const handleFilterChange = useCallback((newFilter: LogFilter) => {
    setFilter(newFilter);
    setPage(0); // 필터 변경 시 첫 페이지로 리셋
    setAllLogs([]); // 기존 로그 클리어
  }, []);

  // 더 많은 로그 로드
  const loadMore = useCallback(() => {
    if (logResponse?.hasMore && !isLoading) {
      setPage(prev => prev + 1);
    }
  }, [logResponse?.hasMore, isLoading]);

  // 수동 새로고침
  const refresh = useCallback(() => {
    setPage(0);
    setAllLogs([]);
    refetch();
  }, [refetch]);

  // 로그 클리어
  const clearLogs = useCallback(() => {
    setAllLogs([]);
    setPage(0);
    queryClient.removeQueries({ queryKey: ['logs'] });
  }, [queryClient]);

  // 자동 새로고침 토글
  const toggleAutoRefresh = useCallback(() => {
    queryClient.setQueryDefaults(['logs'], {
      refetchInterval: autoRefresh ? false : refreshInterval,
    });
  }, [autoRefresh, refreshInterval, queryClient]);

  const hasMore = useMemo(() => {
    return logResponse?.hasMore && allLogs.length < maxEntries;
  }, [logResponse?.hasMore, allLogs.length, maxEntries]);

  return {
    // 데이터
    logs: allLogs,
    total: logResponse?.total || 0,
    hasMore,
    
    // 상태
    isLoading,
    error,
    filter,
    
    // 액션
    setFilter: handleFilterChange,
    loadMore,
    refresh,
    clearLogs,
    toggleAutoRefresh,
  };
};

/**
 * 실시간 로그 스트리밍을 위한 커스텀 훅
 */
export const useLogStream = (options: {
  fileName?: string;
  level?: string;
  maxBufferSize?: number;
  autoScroll?: boolean;
  reconnectInterval?: number;
} = {}) => {
  const {
    fileName = 'watchhamster.log',
    level,
    maxBufferSize = 1000,
    autoScroll = true,
    reconnectInterval = 3000,
  } = options;

  const [streamLogs, setStreamLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(autoScroll);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [lastMessageTime, setLastMessageTime] = useState<Date | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const bufferRef = useRef<LogEntry[]>([]);

  // 로그 버퍼 관리
  const addLogToBuffer = useCallback((logEntry: LogEntry) => {
    bufferRef.current = [logEntry, ...bufferRef.current.slice(0, maxBufferSize - 1)];
    setStreamLogs([...bufferRef.current]);
    setLastMessageTime(new Date());
  }, [maxBufferSize]);

  // WebSocket 연결
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = new URL(`ws://localhost:8000/api/logs/ws`);
      wsUrl.searchParams.set('file_name', fileName);
      if (level) {
        wsUrl.searchParams.set('level', level);
      }

      const ws = new WebSocket(wsUrl.toString());
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('로그 스트림 WebSocket 연결됨');
        setIsConnected(true);
        setError(null);
        setConnectionAttempts(0);
        
        // 연결 확인 메시지 전송
        ws.send(JSON.stringify({ type: 'ping' }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // 로그 엔트리 처리
          if (data.timestamp && data.level && data.message) {
            const logEntry: LogEntry = {
              id: `${Date.now()}-${Math.random()}`,
              timestamp: data.timestamp,
              level: data.level,
              source: data.logger_name || 'unknown',
              message: data.message,
              service: data.module || 'unknown',
              lineNumber: data.line_number,
              threadId: data.thread_id,
            };
            
            // 레벨 필터 적용
            if (!level || logEntry.level.toLowerCase() === level.toLowerCase()) {
              addLogToBuffer(logEntry);
            }
          }
        } catch (err) {
          console.error('로그 스트림 메시지 파싱 오류:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('로그 스트림 WebSocket 오류:', event);
        setError('WebSocket 연결 오류가 발생했습니다.');
      };

      ws.onclose = (event) => {
        console.log('로그 스트림 WebSocket 연결 종료:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;

        // 자동 재연결 (정상 종료가 아닌 경우)
        if (!event.wasClean && connectionAttempts < 10) {
          const delay = Math.min(reconnectInterval * Math.pow(1.5, connectionAttempts), 30000);
          console.log(`로그 스트림 재연결 시도 ${connectionAttempts + 1}/10 (${delay}ms 후)`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setConnectionAttempts(prev => prev + 1);
            connect();
          }, delay);
        } else if (connectionAttempts >= 10) {
          setError('최대 재연결 시도 횟수를 초과했습니다.');
        }
      };

    } catch (err) {
      console.error('WebSocket 연결 시작 실패:', err);
      setError('WebSocket 연결을 시작할 수 없습니다.');
      setIsConnected(false);
    }
  }, [fileName, level, reconnectInterval, connectionAttempts, addLogToBuffer]);

  // 연결 해제
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnectionAttempts(0);
    setError(null);
  }, []);

  // 로그 스트림 클리어
  const clearStream = useCallback(() => {
    bufferRef.current = [];
    setStreamLogs([]);
    setLastMessageTime(null);
  }, []);

  // 자동 스크롤 토글
  const toggleAutoScroll = useCallback(() => {
    setIsAutoScrollEnabled(prev => !prev);
  }, []);

  // 수동 재연결
  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(connect, 1000);
  }, [disconnect, connect]);

  // 연결 상태 확인
  const getConnectionStatus = useCallback(() => {
    if (!wsRef.current) return 'disconnected';
    
    switch (wsRef.current.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }, []);

  // 컴포넌트 마운트 시 연결
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // 파일명이나 레벨이 변경되면 재연결
  useEffect(() => {
    if (isConnected) {
      disconnect();
      setTimeout(connect, 500);
    }
  }, [fileName, level]);

  return {
    // 데이터
    logs: streamLogs,
    lastMessageTime,
    
    // 상태
    isConnected,
    error,
    connectionAttempts,
    isAutoScrollEnabled,
    connectionStatus: getConnectionStatus(),
    
    // 액션
    connect,
    disconnect,
    reconnect,
    clearStream,
    toggleAutoScroll,
    
    // 설정
    fileName,
    level,
    maxBufferSize,
  };
};