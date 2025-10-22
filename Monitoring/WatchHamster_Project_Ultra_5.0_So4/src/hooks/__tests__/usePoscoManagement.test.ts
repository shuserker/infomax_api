import { renderHook, act, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { usePoscoManagement } from '../usePoscoManagement';
import { useApiService } from '../useApiService';
import { useRealtimeMessages } from '../useRealtimeMessages';
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
vi.mock('../useApiService');
vi.mock('../useRealtimeMessages');

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

describe('usePoscoManagement', () => {
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

    mockCallApi.mockResolvedValue(mockPoscoStatus);

    // 타이머 모킹
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() => usePoscoManagement());

    expect(result.current.poscoStatus).toBeNull();
    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.isMonitoring).toBe(false);
  });

  it('POSCO 상태를 성공적으로 가져온다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.poscoStatus).toEqual(mockPoscoStatus);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    expect(mockCallApi).toHaveBeenCalled();
  });

  it('배포를 성공적으로 시작한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    let deploymentResult: any;
    await act(async () => {
      deploymentResult = await result.current.startDeployment('develop');
    });

    expect(deploymentResult).toEqual({
      success: true,
      message: '성공',
    });

    expect(mockCallApi).toHaveBeenCalled();
  });

  it('배포를 성공적으로 중지한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    let stopResult: any;
    await act(async () => {
      stopResult = await result.current.stopDeployment();
    });

    expect(stopResult).toEqual({
      success: true,
      message: '성공',
    });

    expect(mockCallApi).toHaveBeenCalled();
  });

  it('모니터링을 성공적으로 시작한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.startMonitoring();
    });

    expect(result.current.isMonitoring).toBe(true);
    expect(mockCallApi).toHaveBeenCalled();
  });

  it('모니터링을 성공적으로 중지한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 먼저 모니터링 시작
    await act(async () => {
      await result.current.startMonitoring();
    });

    // 모니터링 중지
    await act(async () => {
      await result.current.stopMonitoring();
    });

    expect(result.current.isMonitoring).toBe(false);
    expect(mockCallApi).toHaveBeenCalled();
  });

  it('모니터링을 토글한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 모니터링 시작
    await act(async () => {
      await result.current.toggleMonitoring();
    });

    expect(result.current.isMonitoring).toBe(true);

    // 모니터링 중지
    await act(async () => {
      await result.current.toggleMonitoring();
    });

    expect(result.current.isMonitoring).toBe(false);
  });

  it('현재 브랜치를 성공적으로 가져온다', async () => {
    mockCallApi.mockResolvedValueOnce({ current_branch: 'develop' });

    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    let currentBranch: string;
    await act(async () => {
      currentBranch = await result.current.getCurrentBranch();
    });

    expect(currentBranch!).toBe('develop');
    expect(mockCallApi).toHaveBeenCalled();
  });

  it('배포 히스토리를 성공적으로 가져온다', async () => {
    const mockHistory = [mockPoscoStatus.deployment_history[0]];
    mockCallApi.mockResolvedValueOnce({ deployment_history: mockHistory });

    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    let history: any;
    await act(async () => {
      history = await result.current.getDeploymentHistory();
    });

    expect(history).toEqual(mockHistory);
    expect(mockCallApi).toHaveBeenCalled();
  });

  it('GitHub Pages 상태를 성공적으로 가져온다', async () => {
    const mockGitHubStatus = mockPoscoStatus.github_pages_status;
    mockCallApi.mockResolvedValueOnce(mockGitHubStatus);

    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    let githubStatus: any;
    await act(async () => {
      githubStatus = await result.current.getGitHubPagesStatus();
    });

    expect(githubStatus).toEqual(mockGitHubStatus);
    expect(mockCallApi).toHaveBeenCalled();
  });

  it('상태 색상을 올바르게 반환한다', () => {
    const { result } = renderHook(() => usePoscoManagement());

    expect(result.current.getStatusColor('success')).toBe('green');
    expect(result.current.getStatusColor('completed')).toBe('green');
    expect(result.current.getStatusColor('failed')).toBe('red');
    expect(result.current.getStatusColor('building')).toBe('blue');
    expect(result.current.getStatusColor('idle')).toBe('gray');
    expect(result.current.getStatusColor('unknown')).toBe('gray');
  });

  it('상태 아이콘을 올바르게 반환한다', () => {
    const { result } = renderHook(() => usePoscoManagement());

    expect(result.current.getStatusIcon('success')).toBe('FaCheckCircle');
    expect(result.current.getStatusIcon('failed')).toBe('FaExclamationTriangle');
    expect(result.current.getStatusIcon('building')).toBe('FaSync');
    expect(result.current.getStatusIcon('idle')).toBe('FaClock');
  });

  it('배포 진행 중 여부를 올바르게 판단한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.poscoStatus).toEqual(mockPoscoStatus);
    });

    expect(result.current.isDeploymentInProgress()).toBe(true);
  });

  it('배포 소요 시간을 올바르게 계산한다', () => {
    const { result } = renderHook(() => usePoscoManagement());

    const deployment = {
      ...mockPoscoStatus.deployment_history[0],
      start_time: '2024-12-01T12:00:00Z',
      end_time: '2024-12-01T12:03:30Z',
    };

    const duration = result.current.getDeploymentDuration(deployment);
    expect(duration).toBe('3분 30초');
  });

  it('실시간 연결 상태를 처리한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockCallApi).toHaveBeenCalled();
  });

  it('API 오류를 올바르게 처리한다', async () => {
    mockCallApi.mockResolvedValue(null); // API 호출 실패 시뮬레이션

    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('배포 시작 오류를 올바르게 처리한다', async () => {
    mockCallApi.mockResolvedValue(null); // API 호출 실패 시뮬레이션

    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    let deploymentResult: any;
    await act(async () => {
      deploymentResult = await result.current.startDeployment('develop');
    });

    expect(deploymentResult.success).toBe(false);
  });

  it('주기적으로 상태를 업데이트한다', async () => {
    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 초기 호출
    expect(mockCallApi).toHaveBeenCalled();

    // 10초 후
    act(() => {
      vi.advanceTimersByTime(10000);
    });

    await waitFor(() => {
      expect(mockCallApi).toHaveBeenCalledTimes(2);
    });
  });

  it('에러가 자동으로 클리어된다', async () => {
    const errorMessage = 'API 오류';
    mockGet.mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => usePoscoManagement());

    await waitFor(() => {
      expect(result.current.error).toBe(errorMessage);
    });

    // 10초 후 에러 클리어
    act(() => {
      vi.advanceTimersByTime(10000);
    });

    await waitFor(() => {
      expect(result.current.error).toBeNull();
    });
  });
});