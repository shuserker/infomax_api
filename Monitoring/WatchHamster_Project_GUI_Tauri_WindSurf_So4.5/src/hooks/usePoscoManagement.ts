import { useState, useEffect, useCallback } from 'react';
import { useApiService } from './useApiService';
import { useRealtimeMessages } from './useRealtimeMessages';

// 타입 정의
export interface DeploymentSession {
  session_id: string;
  status: 'idle' | 'preparing' | 'switching_branch' | 'building' | 'deploying' | 'success' | 'failed' | 'rolling_back';
  current_branch: string;
  target_branch: string;
  start_time: string;
  end_time?: string;
  steps_completed: string[];
  current_step: string;
  progress_percentage: number;
  error_message?: string;
}

export interface GitHubPagesStatus {
  is_accessible: boolean;
  last_check: string;
  response_time?: number;
  status_code?: number;
  error_message?: string;
}

export interface PoscoStatus {
  current_deployment?: DeploymentSession;
  current_branch: string;
  branch_switch_status: 'idle' | 'checking' | 'switching' | 'verifying' | 'completed' | 'failed';
  github_pages_status: GitHubPagesStatus;
  deployment_history: DeploymentSession[];
}

export interface DeploymentRequest {
  target_branch: string;
}

export interface UsePoscoManagementReturn {
  // 상태
  poscoStatus: PoscoStatus | null;
  isLoading: boolean;
  error: string | null;
  isMonitoring: boolean;
  
  // 액션
  fetchPoscoStatus: () => Promise<void>;
  startDeployment: (targetBranch: string) => Promise<{ success: boolean; message: string }>;
  stopDeployment: () => Promise<{ success: boolean; message: string }>;
  startMonitoring: () => Promise<void>;
  stopMonitoring: () => Promise<void>;
  toggleMonitoring: () => Promise<void>;
  getCurrentBranch: () => Promise<string>;
  getDeploymentHistory: () => Promise<DeploymentSession[]>;
  getGitHubPagesStatus: () => Promise<GitHubPagesStatus>;
  
  // 유틸리티
  getStatusColor: (status: string) => string;
  getStatusIcon: (status: string) => string;
  isDeploymentInProgress: () => boolean;
  getDeploymentDuration: (deployment: DeploymentSession) => string;
}

export const usePoscoManagement = (): UsePoscoManagementReturn => {
  const [poscoStatus, setPoscoStatus] = useState<PoscoStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  
  const { callApi } = useApiService();
  const { isConnected } = useRealtimeMessages();

  // POSCO 상태 조회
  const fetchPoscoStatus = useCallback(async () => {
    await callApi(
      async () => {
        const res = await fetch('/api/posco/status');
        if (!res.ok) throw new Error('POSCO 상태 조회 실패');
        return res.json();
      },
      {
        loadingKey: 'poscoStatus',
        errorContext: 'POSCO 상태 조회',
        showErrorToast: false,
        onSuccess: (data) => {
          setPoscoStatus(data);
          setError(null);
          setIsLoading(false);
        },
        onError: (err: any) => {
          const errorMessage = err.message || 'POSCO 상태 조회 실패';
          setError(errorMessage);
          setIsLoading(false);
        }
      }
    );
  }, [callApi]);

  // 배포 시작
  const startDeployment = useCallback(async (targetBranch: string) => {
    const response = await callApi(
      async () => {
        const res = await fetch('/api/posco/deployment/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ target_branch: targetBranch })
        });
        if (!res.ok) throw new Error('배포 시작 실패');
        return res.json();
      },
      {
        loadingKey: 'startDeployment',
        errorContext: '배포 시작',
        showErrorToast: false,
        onSuccess: () => {
          setError(null);
          fetchPoscoStatus();
        },
        onError: (err: any) => {
          const errorMessage = err.message || '배포 시작 실패';
          setError(errorMessage);
        }
      }
    );
    
    return {
      success: response !== null,
      message: response ? '배포가 시작되었습니다.' : error || '배포 시작 실패'
    };
  }, [callApi, fetchPoscoStatus, error]);

  // 배포 중지
  const stopDeployment = useCallback(async () => {
    const response = await callApi(
      async () => {
        const res = await fetch('/api/posco/deployment/stop', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error('배포 중지 실패');
        return res.json();
      },
      {
        loadingKey: 'stopDeployment',
        errorContext: '배포 중지',
        showErrorToast: false,
        onSuccess: () => {
          setError(null);
          fetchPoscoStatus();
        },
        onError: (err: any) => {
          const errorMessage = err.message || '배포 중지 실패';
          setError(errorMessage);
        }
      }
    );
    
    return {
      success: response !== null,
      message: response ? '배포가 중지되었습니다.' : error || '배포 중지 실패'
    };
  }, [callApi, fetchPoscoStatus, error]);

  // 모니터링 시작
  const startMonitoring = useCallback(async () => {
    await callApi(
      async () => {
        const res = await fetch('/api/posco/monitoring/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error('모니터링 시작 실패');
        return res.json();
      },
      {
        loadingKey: 'startMonitoring',
        errorContext: '모니터링 시작',
        showErrorToast: false,
        onSuccess: () => {
          setError(null);
          setIsMonitoring(true);
        },
        onError: (err: any) => {
          const errorMessage = err.message || '모니터링 시작 실패';
          setError(errorMessage);
          throw new Error(errorMessage);
        }
      }
    );
  }, [callApi]);

  // 모니터링 중지
  const stopMonitoring = useCallback(async () => {
    await callApi(
      async () => {
        const res = await fetch('/api/posco/monitoring/stop', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error('모니터링 중지 실패');
        return res.json();
      },
      {
        loadingKey: 'stopMonitoring',
        errorContext: '모니터링 중지',
        showErrorToast: false,
        onSuccess: () => {
          setError(null);
          setIsMonitoring(false);
        },
        onError: (err: any) => {
          const errorMessage = err.message || '모니터링 중지 실패';
          setError(errorMessage);
          throw new Error(errorMessage);
        }
      }
    );
  }, [callApi]);

  // 모니터링 토글
  const toggleMonitoring = useCallback(async () => {
    if (isMonitoring) {
      await stopMonitoring();
    } else {
      await startMonitoring();
    }
  }, [isMonitoring, startMonitoring, stopMonitoring]);

  // 현재 브랜치 조회
  const getCurrentBranch = useCallback(async (): Promise<string> => {
    const response = await callApi(
      async () => {
        const res = await fetch('/api/posco/branch/current');
        if (!res.ok) throw new Error('현재 브랜치 조회 실패');
        return res.json();
      },
      {
        loadingKey: 'getCurrentBranch',
        errorContext: '현재 브랜치 조회',
        showErrorToast: false
      }
    );
    
    return response?.current_branch || 'unknown';
  }, [callApi]);

  // 배포 히스토리 조회
  const getDeploymentHistory = useCallback(async (): Promise<DeploymentSession[]> => {
    const response = await callApi(
      async () => {
        const res = await fetch('/api/posco/deployment/history');
        if (!res.ok) throw new Error('배포 히스토리 조회 실패');
        return res.json();
      },
      {
        loadingKey: 'getDeploymentHistory',
        errorContext: '배포 히스토리 조회',
        showErrorToast: false
      }
    );
    
    return response?.deployment_history || [];
  }, [callApi]);

  // GitHub Pages 상태 조회
  const getGitHubPagesStatus = useCallback(async (): Promise<GitHubPagesStatus> => {
    const response = await callApi(
      async () => {
        const res = await fetch('/api/posco/github-pages/status');
        if (!res.ok) throw new Error('GitHub Pages 상태 조회 실패');
        return res.json();
      },
      {
        loadingKey: 'getGitHubPagesStatus',
        errorContext: 'GitHub Pages 상태 조회',
        showErrorToast: false
      }
    );
    
    return response || {
      is_accessible: false,
      last_check: new Date().toISOString(),
      error_message: '상태 조회 실패'
    };
  }, [callApi]);

  // 상태 배지 색상 결정
  const getStatusColor = useCallback((status: string): string => {
    switch (status) {
      case 'success':
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      case 'preparing':
      case 'switching_branch':
      case 'building':
      case 'deploying':
      case 'switching':
      case 'checking':
        return 'blue';
      case 'idle':
        return 'gray';
      default:
        return 'gray';
    }
  }, []);

  // 상태 아이콘 결정
  const getStatusIcon = useCallback((status: string): string => {
    switch (status) {
      case 'success':
      case 'completed':
        return 'FaCheckCircle';
      case 'failed':
        return 'FaExclamationTriangle';
      case 'preparing':
      case 'switching_branch':
      case 'building':
      case 'deploying':
      case 'switching':
      case 'checking':
        return 'FaSync';
      default:
        return 'FaClock';
    }
  }, []);

  // 배포 진행 중 여부 확인
  const isDeploymentInProgress = useCallback((): boolean => {
    if (!poscoStatus?.current_deployment) return false;
    
    const inProgressStatuses = ['preparing', 'switching_branch', 'building', 'deploying'];
    return inProgressStatuses.includes(poscoStatus.current_deployment.status);
  }, [poscoStatus]);

  // 배포 소요 시간 계산
  const getDeploymentDuration = useCallback((deployment: DeploymentSession): string => {
    const startTime = new Date(deployment.start_time);
    const endTime = deployment.end_time ? new Date(deployment.end_time) : new Date();
    
    const durationMs = endTime.getTime() - startTime.getTime();
    const durationMinutes = Math.floor(durationMs / (1000 * 60));
    const durationSeconds = Math.floor((durationMs % (1000 * 60)) / 1000);
    
    if (durationMinutes > 0) {
      return `${durationMinutes}분 ${durationSeconds}초`;
    } else {
      return `${durationSeconds}초`;
    }
  }, []);

  // 실시간 연결 상태 처리
  useEffect(() => {
    if (isConnected && poscoStatus === null) {
      fetchPoscoStatus();
    }
  }, [isConnected, poscoStatus, fetchPoscoStatus]);

  // 초기 데이터 로드 및 주기적 업데이트
  useEffect(() => {
    fetchPoscoStatus();
    
    // 10초마다 상태 업데이트 (배포 진행 중일 때는 5초마다)
    const getInterval = () => {
      return isDeploymentInProgress() ? 5000 : 10000;
    };
    
    const interval = setInterval(() => {
      fetchPoscoStatus();
    }, getInterval());
    
    return () => clearInterval(interval);
  }, [fetchPoscoStatus, isDeploymentInProgress]);

  // 에러 자동 클리어
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 10000); // 10초 후 에러 메시지 자동 클리어
      
      return () => clearTimeout(timer);
    }
  }, [error]);

  return {
    // 상태
    poscoStatus,
    isLoading,
    error,
    isMonitoring,
    
    // 액션
    fetchPoscoStatus,
    startDeployment,
    stopDeployment,
    startMonitoring,
    stopMonitoring,
    toggleMonitoring,
    getCurrentBranch,
    getDeploymentHistory,
    getGitHubPagesStatus,
    
    // 유틸리티
    getStatusColor,
    getStatusIcon,
    isDeploymentInProgress,
    getDeploymentDuration
  };
};