import React from 'react'
import { render, screen } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { vi, describe, it, expect } from 'vitest'
import { SystemMetricCard, MetricData } from '../SystemMetricCard'
import theme from '../../../theme'

const renderWithChakra = (component: React.ReactElement) => {
  return render(
    <ChakraProvider theme={theme}>
      {component}
    </ChakraProvider>
  );
};

const mockMetricData: MetricData = {
  value: 75.5,
  unit: '%',
  trend: [65, 70, 72, 75, 75.5],
  timestamp: '2024-01-01T12:00:00Z',
  status: 'warning',
  threshold: {
    warning: 70,
    critical: 90,
  },
};

describe('SystemMetricCard', () => {
  it('기본 메트릭 카드가 올바르게 렌더링된다', () => {
    renderWithChakra(
      <SystemMetricCard
        title="CPU 사용률"
        type="cpu"
        data={mockMetricData}
      />
    );

    expect(screen.getByText('CPU 사용률')).toBeInTheDocument();
    expect(screen.getByText('75.5%')).toBeInTheDocument();
    expect(screen.getByText('warning')).toBeInTheDocument();
  });

  it('컴팩트 모드에서 올바르게 렌더링된다', () => {
    renderWithChakra(
      <SystemMetricCard
        title="메모리 사용률"
        type="memory"
        data={mockMetricData}
        compact={true}
      />
    );

    expect(screen.getByText('메모리 사용률')).toBeInTheDocument();
    expect(screen.getByText('75.5%')).toBeInTheDocument();
  });

  it('로딩 상태를 올바르게 표시한다', () => {
    renderWithChakra(
      <SystemMetricCard
        title="디스크 사용률"
        type="disk"
        data={mockMetricData}
        isLoading={true}
      />
    );

    expect(screen.getByText('...')).toBeInTheDocument();
  });

  it('임계값 경고가 올바르게 표시된다', () => {
    const criticalData: MetricData = {
      ...mockMetricData,
      value: 95,
      status: 'critical',
    };

    renderWithChakra(
      <SystemMetricCard
        title="CPU 사용률"
        type="cpu"
        data={criticalData}
      />
    );

    expect(screen.getByText('임계 수준에 도달했습니다')).toBeInTheDocument();
    expect(screen.getByText('critical')).toBeInTheDocument();
  });

  it('정상 상태에서는 경고가 표시되지 않는다', () => {
    const normalData: MetricData = {
      ...mockMetricData,
      value: 50,
      status: 'normal',
    };

    renderWithChakra(
      <SystemMetricCard
        title="CPU 사용률"
        type="cpu"
        data={normalData}
      />
    );

    expect(screen.queryByText('임계 수준에 도달했습니다')).not.toBeInTheDocument();
    expect(screen.queryByText('주의가 필요합니다')).not.toBeInTheDocument();
  });

  it('트렌드 차트가 표시되지 않을 때 올바르게 처리된다', () => {
    renderWithChakra(
      <SystemMetricCard
        title="네트워크 상태"
        type="network"
        data={mockMetricData}
        showTrend={false}
      />
    );

    expect(screen.getByText('네트워크 상태')).toBeInTheDocument();
    // 차트 컨테이너가 없는지 확인
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('마지막 업데이트 시간이 올바르게 표시된다', () => {
    const testDate = new Date('2024-01-01T12:00:00Z');
    const dataWithTimestamp: MetricData = {
      ...mockMetricData,
      timestamp: testDate.toISOString(),
    };

    renderWithChakra(
      <SystemMetricCard
        title="CPU 사용률"
        type="cpu"
        data={dataWithTimestamp}
      />
    );

    expect(screen.getByText('마지막 업데이트')).toBeInTheDocument();
    // 시간 형식은 로케일에 따라 다를 수 있으므로 존재 여부만 확인
    expect(screen.getByText(testDate.toLocaleTimeString('ko-KR'))).toBeInTheDocument();
  });

  it('각 메트릭 타입에 맞는 아이콘이 표시된다', () => {
    const types = ['cpu', 'memory', 'disk', 'network'] as const;
    
    types.forEach((type) => {
      const { unmount } = renderWithChakra(
        <SystemMetricCard
          title={`${type} 테스트`}
          type={type}
          data={mockMetricData}
        />
      );
      
      // 각 타입에 맞는 아이콘이 렌더링되는지 확인
      // (실제 아이콘 요소는 테스트하기 어려우므로 컴포넌트가 에러 없이 렌더링되는지 확인)
      expect(screen.getByText(`${type} 테스트`)).toBeInTheDocument();
      
      unmount();
    });
  });

  it('임계값 정보가 툴팁으로 표시된다', () => {
    renderWithChakra(
      <SystemMetricCard
        title="CPU 사용률"
        type="cpu"
        data={mockMetricData}
      />
    );

    // 임계값 표시가 있는지 확인
    expect(screen.getByText('경고: 70%')).toBeInTheDocument();
    expect(screen.getByText('위험: 90%')).toBeInTheDocument();
  });
});