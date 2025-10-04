import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChakraProvider } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Logs } from '../Logs';
import { LogEntry } from '../../types/logs';
import { vi } from 'vitest';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

// API 모킹
vi.mock('../../services/api', () => ({
  api: {
    getLogs: vi.fn(),
    exportLogs: vi.fn(),
    getLogStats: vi.fn(),
  },
}));

// WebSocket 모킹
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(public url: string) {
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 100);
  }

  send(data: string) {}
  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close', { code, reason, wasClean: true }));
  }

  simulateMessage(data: any) {
    if (this.readyState === MockWebSocket.OPEN) {
      this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
    }
  }
}

(global as any).WebSocket = MockWebSocket;

// react-window 모킹
vi.mock('react-window', () => ({
  FixedSizeList: ({ children, itemData, itemCount }: any) => (
    <div data-testid="virtualized-list">
      {Array.from({ length: Math.min(itemCount, 10) }, (_, index) => (
        <div key={index}>
          {children({ index, style: {}, data: itemData })}
        </div>
      ))}
    </div>
  ),
}));

const mockLogs: LogEntry[] = [
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
  },
  {
    id: '3',
    timestamp: '2024-01-15T14:33:00.012Z',
    level: 'WARN',
    source: 'deployment',
    message: 'Git merge conflict detected in main branch',
    metadata: { branch: 'main', conflict_files: ['config.py'] }
  }
];

const mockLogStats = {
  total: 500,
  byLevel: {
    DEBUG: 100,
    INFO: 200,
    WARN: 100,
    ERROR: 80,
    CRITICAL: 20
  },
  bySource: {
    posco_news: 100,
    github_pages: 80,
    deployment: 90,
    webhook_system: 70,
    cache_monitor: 85,
    message_system: 75
  }
};

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <ChakraProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ChakraProvider>
  );
};

describe('Logs 페이지', () => {
  let mockWebSocket: MockWebSocket;

  beforeEach(() => {
    const { api } = require('../../services/api');
    api.getLogs.mockResolvedValue({ data: mockLogs, total: mockLogs.length });
    api.getLogStats.mockResolvedValue(mockLogStats);
    api.exportLogs.mockResolvedValue({ success: true });

    // WebSocket 인스턴스 추적
    const OriginalWebSocket = (global as any).WebSocket;
    (global as any).WebSocket = class extends OriginalWebSocket {
      constructor(url: string) {
        super(url);
        mockWebSocket = this as any;
      }
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
    if (mockWebSocket) {
      mockWebSocket.close();
    }
  });

  it('로그 페이지가 정상적으로 렌더링된다', () => {
    render(<Logs />, { wrapper: createWrapper() });
    
    expect(screen.getByText('로그 뷰어')).toBeInTheDocument();
    expect(screen.getByText('실시간')).toBeInTheDocument();
    expect(screen.getByText('히스토리')).toBeInTheDocument();
  });

  it('실시간 탭과 히스토리 탭 전환이 작동한다', async () => {
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 기본적으로 실시간 탭이 선택되어 있음
    expect(screen.getByRole('tab', { selected: true })).toHaveTextContent('실시간');
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    expect(screen.getByRole('tab', { selected: true })).toHaveTextContent('히스토리');
  });

  it('실시간 로그 뷰어가 올바르게 표시된다', async () => {
    render(<Logs />, { wrapper: createWrapper() });
    
    // 실시간 로그 뷰어 컨트롤들이 표시되는지 확인
    expect(screen.getByText('시작')).toBeInTheDocument();
    expect(screen.getByText('일시정지')).toBeInTheDocument();
    expect(screen.getByLabelText('로그 클리어')).toBeInTheDocument();
    expect(screen.getByLabelText('재연결')).toBeInTheDocument();
  });

  it('히스토리 로그 뷰어가 올바르게 표시된다', async () => {
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 로그 필터와 가상화된 뷰어가 표시되는지 확인
    await waitFor(() => {
      expect(screen.getByPlaceholderText('로그 검색...')).toBeInTheDocument();
    });
  });

  it('로그 필터링이 올바르게 작동한다', async () => {
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 검색어 입력
    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText('로그 검색...');
      expect(searchInput).toBeInTheDocument();
    });
    
    const searchInput = screen.getByPlaceholderText('로그 검색...');
    await user.type(searchInput, 'POSCO');
    
    const searchButton = screen.getByLabelText('검색');
    await user.click(searchButton);
    
    // API가 필터와 함께 호출되었는지 확인
    const { api } = require('../../services/api');
    expect(api.getLogs).toHaveBeenCalledWith(
      expect.objectContaining({
        search: 'POSCO'
      })
    );
  });

  it('로그 레벨 필터가 작동한다', async () => {
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 필터 패널 열기
    await waitFor(() => {
      const filterButton = screen.getByText('필터');
      expect(filterButton).toBeInTheDocument();
    });
    
    const filterButton = screen.getByText('필터');
    await user.click(filterButton);
    
    // ERROR 레벨 선택
    const errorCheckbox = screen.getByRole('checkbox', { name: /ERROR/ });
    await user.click(errorCheckbox);
    
    // API가 레벨 필터와 함께 호출되었는지 확인
    const { api } = require('../../services/api');
    expect(api.getLogs).toHaveBeenCalledWith(
      expect.objectContaining({
        level: ['ERROR']
      })
    );
  });

  it('로그 내보내기 기능이 작동한다', async () => {
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 로그 내보내기 버튼 클릭
    await waitFor(() => {
      const exportButton = screen.getByText('내보내기');
      expect(exportButton).toBeInTheDocument();
    });
    
    const exportButton = screen.getByText('내보내기');
    await user.click(exportButton);
    
    // 내보내기 모달이 표시되는지 확인
    expect(screen.getByText('로그 내보내기')).toBeInTheDocument();
  });

  it('실시간 로그 메시지 수신이 작동한다', async () => {
    render(<Logs />, { wrapper: createWrapper() });
    
    // WebSocket 연결 완료 대기
    await waitFor(() => {
      expect(screen.getByText('연결됨')).toBeInTheDocument();
    });
    
    // 테스트 로그 메시지 전송
    const testLog = {
      timestamp: new Date().toISOString(),
      level: 'INFO',
      logger_name: 'test',
      message: '실시간 테스트 로그 메시지',
    };
    
    mockWebSocket.simulateMessage(testLog);
    
    // 로그 메시지가 표시되는지 확인
    await waitFor(() => {
      expect(screen.getByText('실시간 테스트 로그 메시지')).toBeInTheDocument();
    });
  });

  it('로그 상세 정보 모달이 작동한다', async () => {
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 로그 엔트리가 로드될 때까지 대기
    await waitFor(() => {
      expect(screen.getByText('POSCO 뉴스 모니터링 서비스가 시작되었습니다')).toBeInTheDocument();
    });
    
    // 로그 엔트리 클릭
    const logEntry = screen.getByText('POSCO 뉴스 모니터링 서비스가 시작되었습니다');
    await user.click(logEntry);
    
    // 상세 정보 모달이 표시되는지 확인
    expect(screen.getByText('로그 상세 정보')).toBeInTheDocument();
  });

  it('페이지네이션이 올바르게 작동한다', async () => {
    const user = userEvent.setup();
    
    // 많은 로그가 있는 상황 시뮬레이션
    const { api } = require('../../services/api');
    api.getLogs.mockResolvedValue({ 
      data: mockLogs, 
      total: 150,
      page: 1,
      pageSize: 50
    });
    
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 페이지네이션 컨트롤이 표시되는지 확인
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });

  it('로딩 상태가 올바르게 표시된다', async () => {
    const { api } = require('../../services/api');
    
    // API 응답을 지연시켜 로딩 상태 테스트
    api.getLogs.mockImplementation(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({ data: mockLogs, total: mockLogs.length }), 1000)
      )
    );
    
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 로딩 스피너가 표시되는지 확인
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('에러 상태가 올바르게 처리된다', async () => {
    const { api } = require('../../services/api');
    
    // API 에러 시뮬레이션
    api.getLogs.mockRejectedValue(new Error('서버 연결 실패'));
    
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 에러 메시지가 표시되는지 확인
    await waitFor(() => {
      expect(screen.getByText(/로그를 불러오는 중 오류가 발생했습니다/)).toBeInTheDocument();
    });
  });

  it('자동 새로고침 기능이 작동한다', async () => {
    const user = userEvent.setup();
    render(<Logs />, { wrapper: createWrapper() });
    
    // 히스토리 탭으로 전환
    const historyTab = screen.getByText('히스토리');
    await user.click(historyTab);
    
    // 자동 새로고침 토글 활성화
    await waitFor(() => {
      const autoRefreshToggle = screen.getByLabelText('자동 새로고침');
      expect(autoRefreshToggle).toBeInTheDocument();
    });
    
    const autoRefreshToggle = screen.getByLabelText('자동 새로고침');
    await user.click(autoRefreshToggle);
    
    // 일정 시간 후 API가 다시 호출되는지 확인
    const { api } = require('../../services/api');
    const initialCallCount = api.getLogs.mock.calls.length;
    
    // 5초 대기 (자동 새로고침 간격)
    await new Promise(resolve => setTimeout(resolve, 5100));
    
    expect(api.getLogs.mock.calls.length).toBeGreaterThan(initialCallCount);
  });
});