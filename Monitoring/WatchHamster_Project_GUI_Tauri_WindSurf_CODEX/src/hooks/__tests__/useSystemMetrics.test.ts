import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { vi } from 'vitest';
import { useSystemMetrics } from '../useSystemMetrics';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { it } from 'zod/v4/locales';
import { beforeEach } from 'node:test';
import { describe } from 'node:test';

// API 모킹
vi.mock('../../services/api', () => ({
  apiService: {
    getSystemMetrics: vi.fn(),
  },
}));

// WebSocket 훅 모킹
vi.mock('../useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    lastMessage: null,
    isConnected: true,
  })),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );
};

describe('useSystemMetrics', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() => useSystemMetrics(), {
      wrapper: createWrapper(),
    });

    expect(result.current.metrics).toBeUndefined();
    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.lastUpdated).toBeNull();
    expect(result.current.isConnected).toBe(true);
  });

  it('refreshMetrics 함수가 존재한다', () => {
    const { result } = renderHook(() => useSystemMetrics(), {
      wrapper: createWrapper(),
    });

    expect(typeof result.current.refreshMetrics).toBe('function');
  });

  it('옵션이 올바르게 적용된다', () => {
    const { result } = renderHook(
      () => useSystemMetrics({ 
        enableRealtime: false, 
        refreshInterval: 1000,
        historySize: 10 
      }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isConnected).toBe(true); // 실시간 비활성화 시에도 true
  });

  it('기본 옵션으로 초기화된다', () => {
    const { result } = renderHook(() => useSystemMetrics(), {
      wrapper: createWrapper(),
    });

    // 기본 상태 확인
    expect(result.current.metrics).toBeUndefined();
    expect(result.current.error).toBeNull();
    expect(result.current.lastUpdated).toBeNull();
  });
});