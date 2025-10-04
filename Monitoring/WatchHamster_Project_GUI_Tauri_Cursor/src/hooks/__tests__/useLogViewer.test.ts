import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useLogViewer, useLogStream } from '../useLogViewer';
import apiClient from '../../services/api';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import React from 'react';

// API 클라이언트 모킹
vi.mock('../../services/api');
const mockedApiClient = apiClient as any;

// WebSocket 모킹
const mockWebSocket = {
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  close: vi.fn(),
  send: vi.fn(),
  readyState: WebSocket.OPEN,
};

(global as any).WebSocket = vi.fn(() => mockWebSocket);

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  // eslint-disable-next-line react/display-name
  return ({ children }: { children: React.ReactNode }) => {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
};

const mockLogResponse = {
  logs: [
    {
      id: '1',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'posco_news',
      message: 'POSCO 뉴스 모니터링 서비스가 시작되었습니다',
      metadata: { service_version: '1.0.0' }
    },
    {
      id: '2',
      timestamp: '2024-01-15T14:32:15.789Z',
      level: 'ERROR',
      source: 'github_pages',
      message: 'GitHub Pages 연결 실패: Connection timeout after 30 seconds',
      metadata: { timeout: 30, retry_count: 3 }
    }
  ],
  total: 2,
  hasMore: false
};

describe('useLogViewer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedApiClient.get = vi.fn().mockResolvedValue({ data: mockLogResponse });
  });

  it('초기 로그 데이터를 올바르게 로드한다', async () => {
    const { result } = renderHook(() => useLogViewer(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.logs).toHaveLength(2);
    });

    expect(result.current.logs[0].id).toBe('1');
    expect(result.current.logs[1].id).toBe('2');
    expect(result.current.total).toBe(2);
    expect(result.current.hasMore).toBe(false);
  });

  it('필터 변경 시 새로운 데이터를 요청한다', async () => {
    const { result } = renderHook(() => useLogViewer(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.logs).toHaveLength(2);
    });

    // 필터 변경
    result.current.setFilter({ level: ['ERROR'] });

    await waitFor(() => {
      expect(mockedApiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('levels=ERROR')
      );
    });
  });

  it('더 많은 로그 로드 기능이 작동한다', async () => {
    const mockResponseWithMore = {
      ...mockLogResponse,
      hasMore: true
    };

    mockedApiClient.get = vi.fn().mockResolvedValue({ data: mockResponseWithMore });

    const { result } = renderHook(() => useLogViewer(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.hasMore).toBe(true);
    });

    // 더 많은 로그 로드
    result.current.loadMore();

    await waitFor(() => {
      expect(mockedApiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('page=1')
      );
    });
  });

  it('새로고침 기능이 작동한다', async () => {
    const { result } = renderHook(() => useLogViewer(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.logs).toHaveLength(2);
    });

    // 새로고침
    result.current.refresh();

    await waitFor(() => {
      expect(mockedApiClient.get).toHaveBeenCalledTimes(2);
    });
  });

  it('로그 클리어 기능이 작동한다', async () => {
    const { result } = renderHook(() => useLogViewer(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.logs).toHaveLength(2);
    });

    // 로그 클리어
    result.current.clearLogs();

    expect(result.current.logs).toHaveLength(0);
  });

  it('자동 새로고침 옵션이 올바르게 작동한다', async () => {
    const { result } = renderHook(() => useLogViewer({
      autoRefresh: true,
      refreshInterval: 1000
    }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.logs).toHaveLength(2);
    });

    // 1초 후 자동 새로고침 확인
    await waitFor(() => {
      expect(mockedApiClient.get).toHaveBeenCalledTimes(2);
    }, { timeout: 2000 });
  });

  it('최대 엔트리 수 제한이 작동한다', async () => {
    const manyLogs = Array.from({ length: 1500 }, (_, i) => ({
      id: `${i + 1}`,
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'test',
      message: `Test message ${i + 1}`,
      metadata: {}
    }));

    mockedApiClient.get = vi.fn().mockResolvedValue({
      data: { logs: manyLogs, total: 1500, hasMore: false }
    });

    const { result } = renderHook(() => useLogViewer({
      maxEntries: 1000
    }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.logs.length).toBeLessThanOrEqual(1000);
    });
  });

  it('API 오류를 올바르게 처리한다', async () => {
    const error = new Error('API 오류');
    mockedApiClient.get = vi.fn().mockRejectedValue(error);

    const { result } = renderHook(() => useLogViewer(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
    });
  });
});

describe('useLogStream', () => {
  let mockWebSocketInstance: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockWebSocketInstance = {
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      close: vi.fn(),
      send: vi.fn(),
      readyState: WebSocket.OPEN,
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global as any).WebSocket = vi.fn(() => mockWebSocketInstance);
  });

  it('WebSocket 연결을 올바르게 설정한다', () => {
    const { result } = renderHook(() => useLogStream());

    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8000/ws/logs');
    expect(result.current.logs).toHaveLength(0);
    expect(result.current.isConnected).toBe(false);
  });

  it('WebSocket 연결 성공 시 상태를 업데이트한다', () => {
    const { result } = renderHook(() => useLogStream());

    // onopen 이벤트 시뮬레이션
    if (mockWebSocketInstance.onopen) {
      mockWebSocketInstance.onopen();
    }

    expect(result.current.isConnected).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('새로운 로그 메시지를 올바르게 처리한다', () => {
    const { result } = renderHook(() => useLogStream());

    const mockLogEntry = {
      id: '1',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'test',
      message: 'Test log message',
      metadata: {}
    };

    const mockMessage = {
      data: JSON.stringify({
        type: 'log_entry',
        data: mockLogEntry
      })
    };

    // onmessage 이벤트 시뮬레이션
    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage(mockMessage);
    }

    expect(result.current.logs).toHaveLength(1);
    expect(result.current.logs[0]).toEqual(mockLogEntry);
  });

  it('WebSocket 오류를 올바르게 처리한다', () => {
    const { result } = renderHook(() => useLogStream());

    // onerror 이벤트 시뮬레이션
    if (mockWebSocketInstance.onerror) {
      mockWebSocketInstance.onerror(new Event('error'));
    }

    expect(result.current.error).toBe('WebSocket 연결 오류가 발생했습니다.');
    expect(result.current.isConnected).toBe(false);
  });

  it('WebSocket 연결 종료를 올바르게 처리한다', () => {
    const { result } = renderHook(() => useLogStream());

    // 연결 상태를 먼저 true로 설정
    if (mockWebSocketInstance.onopen) {
      mockWebSocketInstance.onopen();
    }

    expect(result.current.isConnected).toBe(true);

    // onclose 이벤트 시뮬레이션
    if (mockWebSocketInstance.onclose) {
      mockWebSocketInstance.onclose();
    }

    expect(result.current.isConnected).toBe(false);
  });

  it('로그 스트림 클리어 기능이 작동한다', () => {
    const { result } = renderHook(() => useLogStream());

    // 먼저 로그 추가
    const mockLogEntry = {
      id: '1',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'test',
      message: 'Test log message',
      metadata: {}
    };

    const mockMessage = {
      data: JSON.stringify({
        type: 'log_entry',
        data: mockLogEntry
      })
    };

    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage(mockMessage);
    }

    expect(result.current.logs).toHaveLength(1);

    // 스트림 클리어
    result.current.clearStream();

    expect(result.current.logs).toHaveLength(0);
  });

  it('연결 해제 기능이 작동한다', () => {
    const { result } = renderHook(() => useLogStream());

    result.current.disconnect();

    expect(result.current.isConnected).toBe(false);
    expect(result.current.logs).toHaveLength(0);
  });

  it('최대 로그 수 제한이 작동한다', () => {
    const { result } = renderHook(() => useLogStream());

    // 1001개의 로그 메시지 전송 (최대 1000개 제한)
    for (let i = 0; i < 1001; i++) {
      const mockLogEntry = {
        id: `${i + 1}`,
        timestamp: '2024-01-15T14:30:25.123Z',
        level: 'INFO',
        source: 'test',
        message: `Test log message ${i + 1}`,
        metadata: {}
      };

      const mockMessage = {
        data: JSON.stringify({
          type: 'log_entry',
          data: mockLogEntry
        })
      };

      if (mockWebSocketInstance.onmessage) {
        mockWebSocketInstance.onmessage(mockMessage);
      }
    }

    expect(result.current.logs.length).toBeLessThanOrEqual(1000);
  });

  it('잘못된 JSON 메시지를 무시한다', () => {
    const { result } = renderHook(() => useLogStream());

    const mockMessage = {
      data: 'invalid json'
    };

    // 오류가 발생해도 앱이 크래시되지 않아야 함
    expect(() => {
      if (mockWebSocketInstance.onmessage) {
        mockWebSocketInstance.onmessage(mockMessage);
      }
    }).not.toThrow();

    expect(result.current.logs).toHaveLength(0);
  });

  it('레벨 필터가 실시간 로그에 적용된다', () => {
    const { result } = renderHook(() => useLogStream({
      levelFilter: ['ERROR', 'CRITICAL']
    }));

    // INFO 레벨 로그 (필터링되어야 함)
    const infoLog = {
      id: '1',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'test',
      message: 'Info message',
      metadata: {}
    };

    // ERROR 레벨 로그 (표시되어야 함)
    const errorLog = {
      id: '2',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'ERROR',
      source: 'test',
      message: 'Error message',
      metadata: {}
    };

    // INFO 로그 전송
    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({
        data: JSON.stringify({
          type: 'log_entry',
          data: infoLog
        })
      });
    }

    expect(result.current.logs).toHaveLength(0); // 필터링됨

    // ERROR 로그 전송
    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({
        data: JSON.stringify({
          type: 'log_entry',
          data: errorLog
        })
      });
    }

    expect(result.current.logs).toHaveLength(1); // 표시됨
    expect(result.current.logs[0].level).toBe('ERROR');
  });

  it('소스 필터가 실시간 로그에 적용된다', () => {
    const { result } = renderHook(() => useLogStream({
      sourceFilter: ['posco_news', 'github_pages']
    }));

    // deployment 소스 로그 (필터링되어야 함)
    const deploymentLog = {
      id: '1',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'deployment',
      message: 'Deployment message',
      metadata: {}
    };

    // posco_news 소스 로그 (표시되어야 함)
    const poscoLog = {
      id: '2',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'posco_news',
      message: 'POSCO message',
      metadata: {}
    };

    // deployment 로그 전송
    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({
        data: JSON.stringify({
          type: 'log_entry',
          data: deploymentLog
        })
      });
    }

    expect(result.current.logs).toHaveLength(0); // 필터링됨

    // posco_news 로그 전송
    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({
        data: JSON.stringify({
          type: 'log_entry',
          data: poscoLog
        })
      });
    }

    expect(result.current.logs).toHaveLength(1); // 표시됨
    expect(result.current.logs[0].source).toBe('posco_news');
  });

  it('일시정지 상태에서는 로그를 버퍼링한다', () => {
    const { result } = renderHook(() => useLogStream());

    // 일시정지
    result.current.pause();
    expect(result.current.isPaused).toBe(true);

    // 일시정지 상태에서 로그 전송
    const mockLogEntry = {
      id: '1',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'test',
      message: 'Paused message',
      metadata: {}
    };

    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({
        data: JSON.stringify({
          type: 'log_entry',
          data: mockLogEntry
        })
      });
    }

    // 일시정지 상태에서는 로그가 표시되지 않음
    expect(result.current.logs).toHaveLength(0);

    // 재개
    result.current.resume();
    expect(result.current.isPaused).toBe(false);

    // 재개 후 버퍼링된 로그가 표시됨
    expect(result.current.logs).toHaveLength(1);
    expect(result.current.logs[0].message).toBe('Paused message');
  });

  it('자동 재연결 기능이 작동한다', async () => {
    const { result } = renderHook(() => useLogStream({
      autoReconnect: true,
      reconnectInterval: 100
    }));

    // 연결 종료 시뮬레이션
    if (mockWebSocketInstance.onclose) {
      mockWebSocketInstance.onclose();
    }

    expect(result.current.isConnected).toBe(false);

    // 자동 재연결 시도 확인 (100ms 후)
    await waitFor(() => {
      expect(WebSocket).toHaveBeenCalledTimes(2); // 초기 연결 + 재연결
    }, { timeout: 200 });
  });

  it('연결 상태 변경 콜백이 호출된다', () => {
    const onConnectionChange = vi.fn();
    
    renderHook(() => useLogStream({
      onConnectionChange
    }));

    // 연결 성공 시뮬레이션
    if (mockWebSocketInstance.onopen) {
      mockWebSocketInstance.onopen();
    }

    expect(onConnectionChange).toHaveBeenCalledWith(true);

    // 연결 종료 시뮬레이션
    if (mockWebSocketInstance.onclose) {
      mockWebSocketInstance.onclose();
    }

    expect(onConnectionChange).toHaveBeenCalledWith(false);
  });

  it('새 로그 수신 콜백이 호출된다', () => {
    const onNewLog = vi.fn();
    
    renderHook(() => useLogStream({
      onNewLog
    }));

    const mockLogEntry = {
      id: '1',
      timestamp: '2024-01-15T14:30:25.123Z',
      level: 'INFO',
      source: 'test',
      message: 'Test message',
      metadata: {}
    };

    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({
        data: JSON.stringify({
          type: 'log_entry',
          data: mockLogEntry
        })
      });
    }

    expect(onNewLog).toHaveBeenCalledWith(mockLogEntry);
  });

  it('통계 업데이트 메시지를 처리한다', () => {
    const { result } = renderHook(() => useLogStream());

    const statsUpdate = {
      total: 1500,
      byLevel: {
        DEBUG: 300,
        INFO: 600,
        WARN: 300,
        ERROR: 250,
        CRITICAL: 50
      },
      bySource: {
        posco_news: 400,
        github_pages: 300,
        deployment: 350,
        webhook_system: 250,
        cache_monitor: 200
      }
    };

    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({
        data: JSON.stringify({
          type: 'stats_update',
          data: statsUpdate
        })
      });
    }

    expect(result.current.stats).toEqual(statsUpdate);
  });
});