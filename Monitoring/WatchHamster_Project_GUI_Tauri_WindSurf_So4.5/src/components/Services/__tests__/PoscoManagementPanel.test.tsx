import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import PoscoManagementPanel from '../PoscoManagementPanel';
import { useApiService } from '../../../hooks/useApiService';
import { useRealtimeMessages } from '../../../hooks/useRealtimeMessages';
import theme from '../../../theme';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { afterEach } from 'node:test';
import { beforeEach } from 'node:test';
import { describe } from 'node:test';

// Mock hooks
vi.mock('../../../hooks/useApiService');
vi.mock('../../../hooks/useRealtimeMessages');

const mockUseApiService = vi.mocked(useApiService);
const mockUseRealtimeMessages = vi.mocked(useRealtimeMessages);

// Mock data
const mockPoscoStatus = {
  current_deployment: {
    session_id: 'deploy_20241201_143000',
    status: 'building' as const,
    current_branch: 'main',
    target_branch: 'production',
    start_time: '2024-12-01T14:30:00Z',
    steps_completed: ['브랜치 전환 완료'],
    current_step: '빌드 중',
    progress_percentage: 50.0,
  },
  current_branch: 'main',
  branch_switch_status: 'completed' as const,
  github_pages_status: {
    is_accessible: true,
    last_check: '2024-12-01T14:35:00Z',
    response_time: 250.5,
    status_code: 200,
  },
  deployment_history: [
    {
      session_id: 'deploy_20241201_120000',
      status: 'success' as const,
      current_branch: 'main',
      target_branch: 'production',
      start_time: '2024-12-01T12:00:00Z',
      end_time: '2024-12-01T12:05:00Z',
      steps_completed: ['브랜치 전환 완료', '빌드 완료', '배포 완료'],
      current_step: '배포 완료',
      progress_percentage: 100.0,
    },
  ],
};

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ChakraProvider theme={theme}>
        {component}
      </ChakraProvider>
    </QueryClientProvider>
  );
};

describe('PoscoManagementPanel', () => {
  const mockCallApi = vi.fn();

  beforeEach(() => {
    mockUseApiService.mockReturnValue({
      callApi: mockCallApi,
      loading: {},
      errors: {},
      retry: vi.fn(),
      clearState: vi.fn(),
      handleError: vi.fn(),
      showSuccessToast: vi.fn(),
      setLoadingState: vi.fn(),
      setErrorState: vi.fn(),
      isLoading: vi.fn(),
      hasError: vi.fn(),
      getError: vi.fn(),
    });

    mockUseRealtimeMessages.mockReturnValue({
      isConnected: true,
      connectionStatus: 'connected',
      reconnectAttempts: 0,
      isLoading: false,
      systemMetrics: null,
      services: [],
      alerts: [],
      events: [],
      logs: [],
      stats: {
        totalServices: 0,
        runningServices: 0,
        stoppedServices: 0,
        errorServices: 0,
        totalAlerts: 0,
        errorAlerts: 0,
        warningAlerts: 0,
        totalEvents: 0,
        totalLogs: 0,
        errorLogs: 0,
      },
      systemHealth: 'healthy',
      getServiceById: vi.fn(),
      getServicesByStatus: vi.fn(),
      addAlert: vi.fn(),
      dismissAlert: vi.fn(),
      clearAllAlerts: vi.fn(),
      clearEvents: vi.fn(),
      clearLogs: vi.fn(),
      sendMessage: vi.fn(),
      subscribe: vi.fn(),
      unsubscribe: vi.fn(),
      requestStatus: vi.fn(),
      connect: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    });

    // callApi가 성공 콜백을 즉시 호출하도록 설정
    mockCallApi.mockImplementation((apiCall, options) => {
      const result = mockPoscoStatus;
      if (options?.onSuccess) {
        options.onSuccess(result);
      }
      return Promise.resolve(result);
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('POSCO 관리 패널이 정상적으로 렌더링된다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('POSCO 시스템 관리')).toBeInTheDocument();
    });

    expect(screen.getByText('현재 브랜치')).toBeInTheDocument();
    expect(screen.getByText('GitHub Pages')).toBeInTheDocument();
    expect(screen.getByText('배포 상태')).toBeInTheDocument();
  });

  it('현재 배포 진행 상황을 표시한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('현재 배포 진행 상황')).toBeInTheDocument();
    });

    expect(screen.getByText('deploy_20241201_143000')).toBeInTheDocument();
    expect(screen.getByText('main → production')).toBeInTheDocument();
    expect(screen.getByText('빌드 중')).toBeInTheDocument();
    expect(screen.getByText('50.0%')).toBeInTheDocument();
  });

  it('배포 시작 모달이 정상적으로 작동한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('새 배포 시작')).toBeInTheDocument();
    });

    // 배포 시작 버튼 클릭
    fireEvent.click(screen.getByText('새 배포 시작'));

    await waitFor(() => {
      expect(screen.getByText('배포할 브랜치를 선택해주세요:')).toBeInTheDocument();
    });

    // 브랜치 선택
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'develop' } });

    // 배포 시작 확인
    const startButton = screen.getByRole('button', { name: '배포 시작' });
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockCallApi).toHaveBeenCalled();
    });
  });

  it('배포 중지 기능이 정상적으로 작동한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('배포 중지')).toBeInTheDocument();
    });

    // 배포 중지 버튼 클릭
    fireEvent.click(screen.getByText('배포 중지'));

    await waitFor(() => {
      expect(mockCallApi).toHaveBeenCalled();
    });
  });

  it('모니터링 시작/중지 기능이 정상적으로 작동한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('모니터링 시작')).toBeInTheDocument();
    });

    // 모니터링 시작 버튼 클릭
    fireEvent.click(screen.getByText('모니터링 시작'));

    await waitFor(() => {
      expect(mockCallApi).toHaveBeenCalled();
    });
  });

  it('배포 히스토리 모달이 정상적으로 작동한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('배포 히스토리')).toBeInTheDocument();
    });

    // 배포 히스토리 버튼 클릭
    fireEvent.click(screen.getByText('배포 히스토리'));

    await waitFor(() => {
      expect(screen.getByText('deploy_20241201_120000')).toBeInTheDocument();
    });

    expect(screen.getByText('main → production')).toBeInTheDocument();
    expect(screen.getByText('100.0%')).toBeInTheDocument();
  });

  it('GitHub Pages 상태를 정확히 표시한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('GitHub Pages 상태')).toBeInTheDocument();
    });

    expect(screen.getByText('정상')).toBeInTheDocument();
    expect(screen.getByText('250.50ms')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
  });

  it('실시간 연결 상태를 처리한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(mockCallApi).toHaveBeenCalled();
    });
  });

  it('로딩 상태를 표시한다', () => {
    mockCallApi.mockImplementation(() => new Promise(() => {})); // 무한 대기

    renderWithProviders(<PoscoManagementPanel />);

    expect(screen.getByText('POSCO 시스템 상태를 불러오는 중...')).toBeInTheDocument();
  });

  it('에러 상태를 표시한다', async () => {
    mockCallApi.mockResolvedValue(null); // API 호출 실패 시뮬레이션

    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('POSCO 시스템 연결 실패')).toBeInTheDocument();
    });

    expect(screen.getByText('POSCO 시스템에 연결할 수 없습니다. 백엔드 서비스를 확인해주세요.')).toBeInTheDocument();
  });

  it('배포가 진행 중일 때 새 배포 시작 버튼이 비활성화된다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      const startButton = screen.getByText('새 배포 시작');
      expect(startButton).toBeDisabled();
    });
  });

  it('상태 새로고침 기능이 정상적으로 작동한다', async () => {
    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('상태 새로고침')).toBeInTheDocument();
    });

    // 상태 새로고침 버튼 클릭
    fireEvent.click(screen.getByText('상태 새로고침'));

    await waitFor(() => {
      expect(mockCallApi).toHaveBeenCalled();
    });
  });

  it('GitHub Pages 확인 링크가 정상적으로 작동한다', async () => {
    // window.open 모킹
    const mockOpen = vi.fn();
    Object.defineProperty(window, 'open', {
      value: mockOpen,
      writable: true,
    });

    renderWithProviders(<PoscoManagementPanel />);

    await waitFor(() => {
      expect(screen.getByText('GitHub Pages 확인')).toBeInTheDocument();
    });

    // GitHub Pages 확인 버튼 클릭
    fireEvent.click(screen.getByText('GitHub Pages 확인'));

    expect(mockOpen).toHaveBeenCalledWith('https://your-github-pages-url.github.io', '_blank');
  });
});