import { renderHook, act } from '@testing-library/react'
import { useRealtimeChart, chartUtils } from '../useRealtimeChart'
import { SystemMetrics } from '../../types'

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
})

import { vi } from 'vitest'
import { it } from 'zod/v4/locales'
import { describe } from 'node:test'
import { it } from 'zod/v4/locales'
import { describe } from 'node:test'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { describe } from 'node:test'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { describe } from 'node:test'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { describe } from 'node:test'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { describe } from 'node:test'
import { describe } from 'node:test'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { it } from 'zod/v4/locales'
import { afterEach } from 'node:test'
import { beforeEach } from 'node:test'
import { describe } from 'node:test'

// Mock setTimeout and clearTimeout
vi.useFakeTimers()

const mockSystemMetrics: SystemMetrics = {
  cpu_percent: 45.2,
  memory_percent: 67.8,
  disk_usage: 23.4,
  network_status: 'connected',
  uptime: 3600,
  active_services: 5,
  timestamp: '2024-01-01T10:00:00Z'
}

describe('useRealtimeChart', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLocalStorage.getItem.mockReturnValue(null)
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  it('초기 상태가 올바르게 설정된다', () => {
    const { result } = renderHook(() => useRealtimeChart())

    expect(result.current.data).toEqual({
      cpu: [],
      memory: [],
      disk: [],
      network: []
    })
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe(null)
    expect(result.current.zoomRange).toBe(null)
  })

  it('캐시된 데이터를 로드한다', () => {
    const cachedData = {
      cpu: [{ timestamp: '2024-01-01T10:00:00Z', value: 50, label: 'CPU: 50%' }],
      memory: [{ timestamp: '2024-01-01T10:00:00Z', value: 60, label: '메모리: 60%' }],
      disk: [{ timestamp: '2024-01-01T10:00:00Z', value: 30, label: '디스크: 30%' }],
      network: [{ timestamp: '2024-01-01T10:00:00Z', value: 100, label: '네트워크: connected' }]
    }

    mockLocalStorage.getItem.mockReturnValue(JSON.stringify(cachedData))

    const { result } = renderHook(() => useRealtimeChart({
      enableCaching: true,
      cacheKey: 'test-cache'
    }))

    expect(result.current.data).toEqual(cachedData)
  })

  it('잘못된 캐시 데이터를 무시한다', () => {
    mockLocalStorage.getItem.mockReturnValue('invalid-json')
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation()

    const { result } = renderHook(() => useRealtimeChart())

    expect(result.current.data).toEqual({
      cpu: [],
      memory: [],
      disk: [],
      network: []
    })
    expect(consoleSpy).toHaveBeenCalledWith('캐시된 차트 데이터 로드 실패:', expect.any(Error))

    consoleSpy.mockRestore()
  })

  it('새 데이터 포인트를 올바르게 추가한다', () => {
    const { result } = renderHook(() => useRealtimeChart())

    act(() => {
      result.current.addDataPoint(mockSystemMetrics)
    })

    expect(result.current.data.cpu).toHaveLength(1)
    expect(result.current.data.cpu[0]).toEqual({
      timestamp: '2024-01-01T10:00:00Z',
      value: 45.2,
      label: 'CPU: 45.2%'
    })

    expect(result.current.data.memory[0]).toEqual({
      timestamp: '2024-01-01T10:00:00Z',
      value: 67.8,
      label: '메모리: 67.8%'
    })

    expect(result.current.data.disk[0]).toEqual({
      timestamp: '2024-01-01T10:00:00Z',
      value: 23.4,
      label: '디스크: 23.4%'
    })

    expect(result.current.data.network[0]).toEqual({
      timestamp: '2024-01-01T10:00:00Z',
      value: 100,
      label: '네트워크: connected'
    })
  })

  it('네트워크 상태를 올바르게 숫자로 변환한다', () => {
    const { result } = renderHook(() => useRealtimeChart())

    const testCases = [
      { status: 'connected', expected: 100 },
      { status: 'limited', expected: 50 },
      { status: 'disconnected', expected: 0 },
      { status: 'unknown', expected: 0 }
    ]

    testCases.forEach(({ status, expected }) => {
      const metrics = { ...mockSystemMetrics, network_status: status as any }
      
      act(() => {
        result.current.addDataPoint(metrics)
      })

      const lastNetworkPoint = result.current.data.network[result.current.data.network.length - 1]
      expect(lastNetworkPoint.value).toBe(expected)
    })
  })

  it('최대 데이터 포인트 수를 제한한다', () => {
    const { result } = renderHook(() => useRealtimeChart({ maxDataPoints: 2 }))

    // 3개의 데이터 포인트 추가
    act(() => {
      result.current.addDataPoint({ ...mockSystemMetrics, timestamp: '2024-01-01T10:00:00Z' })
      result.current.addDataPoint({ ...mockSystemMetrics, timestamp: '2024-01-01T10:05:00Z' })
      result.current.addDataPoint({ ...mockSystemMetrics, timestamp: '2024-01-01T10:10:00Z' })
    })

    // 최대 2개만 유지되어야 함
    expect(result.current.data.cpu).toHaveLength(2)
    expect(result.current.data.cpu[0].timestamp).toBe('2024-01-01T10:05:00Z')
    expect(result.current.data.cpu[1].timestamp).toBe('2024-01-01T10:10:00Z')
  })

  it('데이터를 캐시에 저장한다', () => {
    const { result } = renderHook(() => useRealtimeChart({
      enableCaching: true,
      cacheKey: 'test-cache'
    }))

    act(() => {
      result.current.addDataPoint(mockSystemMetrics)
    })

    // 디바운스 타이머 실행
    act(() => {
      vi.advanceTimersByTime(1000)
    })

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      'test-cache',
      expect.stringContaining('"cpu"')
    )
  })

  it('캐싱이 비활성화되면 캐시에 저장하지 않는다', () => {
    const { result } = renderHook(() => useRealtimeChart({ enableCaching: false }))

    act(() => {
      result.current.addDataPoint(mockSystemMetrics)
    })

    act(() => {
      vi.advanceTimersByTime(1000)
    })

    expect(mockLocalStorage.setItem).not.toHaveBeenCalled()
  })

  it('데이터를 초기화한다', () => {
    const { result } = renderHook(() => useRealtimeChart({
      enableCaching: true,
      cacheKey: 'test-cache'
    }))

    // 데이터 추가
    act(() => {
      result.current.addDataPoint(mockSystemMetrics)
    })

    expect(result.current.data.cpu).toHaveLength(1)

    // 데이터 초기화
    act(() => {
      result.current.clearData()
    })

    expect(result.current.data).toEqual({
      cpu: [],
      memory: [],
      disk: [],
      network: []
    })
    expect(result.current.error).toBe(null)
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('test-cache')
  })

  it('데이터를 내보낸다', () => {
    const { result } = renderHook(() => useRealtimeChart())

    act(() => {
      result.current.addDataPoint(mockSystemMetrics)
    })

    const exportedData = result.current.exportData()
    
    expect(exportedData).toEqual(result.current.data)
    expect(exportedData).not.toBe(result.current.data) // 깊은 복사 확인
  })

  it('줌 범위를 설정한다', () => {
    const { result } = renderHook(() => useRealtimeChart())

    act(() => {
      result.current.setZoomRange([0, 50])
    })

    expect(result.current.zoomRange).toEqual([0, 50])

    act(() => {
      result.current.setZoomRange(null)
    })

    expect(result.current.zoomRange).toBe(null)
  })

  it('데이터 추가 중 오류를 처리한다', () => {
    const { result } = renderHook(() => useRealtimeChart())
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    // 잘못된 타임스탬프로 오류 유발
    const invalidMetrics = { ...mockSystemMetrics, timestamp: 'invalid-date' }

    act(() => {
      result.current.addDataPoint(invalidMetrics)
    })

    expect(result.current.error).toBeTruthy()
    expect(consoleSpy).toHaveBeenCalled()

    consoleSpy.mockRestore()
  })

  it('컴포넌트 언마운트 시 타이머를 정리한다', () => {
    const { result, unmount } = renderHook(() => useRealtimeChart({ enableCaching: true }))

    act(() => {
      result.current.addDataPoint(mockSystemMetrics)
    })

    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')
    
    unmount()

    expect(clearTimeoutSpy).toHaveBeenCalled()
    clearTimeoutSpy.mockRestore()
  })
})

describe('chartUtils', () => {
  const testData = [
    { timestamp: '2024-01-01T10:00:00Z', value: 10, label: 'Test 1' },
    { timestamp: '2024-01-01T10:05:00Z', value: 20, label: 'Test 2' },
    { timestamp: '2024-01-01T10:10:00Z', value: 30, label: 'Test 3' },
    { timestamp: '2024-01-01T10:15:00Z', value: 40, label: 'Test 4' },
    { timestamp: '2024-01-01T10:20:00Z', value: 50, label: 'Test 5' }
  ]

  describe('filterByTimeRange', () => {
    it('시간 범위로 데이터를 필터링한다', () => {
      const filtered = chartUtils.filterByTimeRange(
        testData,
        '2024-01-01T10:05:00Z',
        '2024-01-01T10:15:00Z'
      )

      expect(filtered).toHaveLength(3)
      expect(filtered[0].value).toBe(20)
      expect(filtered[2].value).toBe(40)
    })

    it('범위 밖의 데이터를 제외한다', () => {
      const filtered = chartUtils.filterByTimeRange(
        testData,
        '2024-01-01T10:30:00Z',
        '2024-01-01T10:35:00Z'
      )

      expect(filtered).toHaveLength(0)
    })
  })

  describe('downsample', () => {
    it('데이터를 다운샘플링한다', () => {
      const downsampled = chartUtils.downsample(testData, 3)

      expect(downsampled).toHaveLength(3)
      expect(downsampled[0].value).toBe(10)
      expect(downsampled[1].value).toBe(20)
      expect(downsampled[2].value).toBe(30)
    })

    it('타겟 포인트보다 적은 데이터는 그대로 반환한다', () => {
      const downsampled = chartUtils.downsample(testData, 10)

      expect(downsampled).toEqual(testData)
    })
  })

  describe('calculateAverage', () => {
    it('평균값을 계산한다', () => {
      const average = chartUtils.calculateAverage(testData)

      expect(average).toBe(30) // (10+20+30+40+50)/5 = 30
    })

    it('빈 배열의 평균은 0이다', () => {
      const average = chartUtils.calculateAverage([])

      expect(average).toBe(0)
    })
  })

  describe('findMinMax', () => {
    it('최소/최대값을 찾는다', () => {
      const { min, max } = chartUtils.findMinMax(testData)

      expect(min).toBe(10)
      expect(max).toBe(50)
    })

    it('빈 배열의 최소/최대값은 0이다', () => {
      const { min, max } = chartUtils.findMinMax([])

      expect(min).toBe(0)
      expect(max).toBe(0)
    })

    it('단일 요소의 최소/최대값은 동일하다', () => {
      const singleData = [{ timestamp: '2024-01-01T10:00:00Z', value: 25, label: 'Test' }]
      const { min, max } = chartUtils.findMinMax(singleData)

      expect(min).toBe(25)
      expect(max).toBe(25)
    })
  })

  describe('formatTime', () => {
    it('시간을 한국어 형식으로 포맷한다', () => {
      const formatted = chartUtils.formatTime('2024-01-01T10:30:45Z')

      expect(formatted).toMatch(/\d{2}:\d{2}:\d{2}/)
    })
  })

  describe('formatDate', () => {
    it('날짜를 한국어 형식으로 포맷한다', () => {
      const formatted = chartUtils.formatDate('2024-01-01T10:30:45Z')

      expect(formatted).toContain('1')
      expect(formatted).toMatch(/\d{2}:\d{2}/)
    })
  })
})