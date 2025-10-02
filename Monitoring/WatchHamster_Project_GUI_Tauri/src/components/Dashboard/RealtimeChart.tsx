import React, { useMemo, useState, useCallback } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  ButtonGroup,
  Select,
  Switch,
  FormControl,
  FormLabel,
  Tooltip,
  IconButton,
  useColorModeValue,
  Flex,
  Badge,
  Divider
} from '@chakra-ui/react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Brush,
  ReferenceLine,
  Legend
} from 'recharts'
import { FiRefreshCw, FiDownload, FiZoomOut, FiMaximize2 } from 'react-icons/fi'
import { useRealtimeChart, chartUtils } from '../../hooks/useRealtimeChart'
import { useSystemMetrics } from '../../hooks/useSystemMetrics'

export interface RealtimeChartProps {
  height?: number
  showControls?: boolean
  autoUpdate?: boolean
  maxDataPoints?: number
  className?: string
}

type MetricType = 'cpu' | 'memory' | 'disk' | 'network'

interface ChartMetricConfig {
  key: MetricType
  name: string
  color: string
  unit: string
  enabled: boolean
}

const DEFAULT_METRICS: ChartMetricConfig[] = [
  { key: 'cpu', name: 'CPU 사용률', color: '#3182CE', unit: '%', enabled: true },
  { key: 'memory', name: '메모리 사용률', color: '#38A169', unit: '%', enabled: true },
  { key: 'disk', name: '디스크 사용률', color: '#D69E2E', unit: '%', enabled: true },
  { key: 'network', name: '네트워크 상태', color: '#9F7AEA', unit: '', enabled: false }
]

export const RealtimeChart: React.FC<RealtimeChartProps> = ({
  height = 400,
  showControls = true,
  autoUpdate = true,
  maxDataPoints = 100,
  className
}) => {
  const { metrics: systemMetrics } = useSystemMetrics()
  const {
    data: chartData,
    isLoading,
    error,
    addDataPoint,
    clearData,
    exportData,
    zoomRange,
    setZoomRange
  } = useRealtimeChart({ maxDataPoints })

  const [metrics, setMetrics] = useState<ChartMetricConfig[]>(DEFAULT_METRICS)
  const [timeRange, setTimeRange] = useState<string>('all')
  const [showBrush, setShowBrush] = useState(true)
  const [showGrid, setShowGrid] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // 색상 테마
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const textColor = useColorModeValue('gray.600', 'gray.300')
  const gridColor = useColorModeValue('#f0f0f0', '#2d3748')

  // 시스템 메트릭 업데이트 시 차트 데이터 추가
  React.useEffect(() => {
    if (autoUpdate && systemMetrics) {
      // MetricsGrid의 SystemMetrics를 types의 SystemMetrics로 변환
      const networkStatus: 'connected' | 'limited' | 'disconnected' = 
        systemMetrics.network.value > 80 ? 'connected' : 
        systemMetrics.network.value > 40 ? 'limited' : 'disconnected'
      
      const convertedMetrics = {
        cpu_percent: systemMetrics.cpu.value,
        memory_percent: systemMetrics.memory.value,
        disk_usage: systemMetrics.disk.value,
        network_status: networkStatus,
        uptime: 0,
        active_services: 0,
        timestamp: systemMetrics.cpu.timestamp
      }
      addDataPoint(convertedMetrics)
    }
  }, [systemMetrics, autoUpdate, addDataPoint])

  // 차트 데이터 변환
  const chartDataPoints = useMemo(() => {
    const enabledMetrics = metrics.filter(m => m.enabled)
    if (enabledMetrics.length === 0) return []

    // 모든 메트릭의 타임스탬프를 수집
    const allTimestamps = new Set<string>()
    enabledMetrics.forEach(metric => {
      chartData[metric.key].forEach(point => {
        allTimestamps.add(point.timestamp)
      })
    })

    // 타임스탬프별로 데이터 포인트 생성
    const sortedTimestamps = Array.from(allTimestamps).sort()
    
    return sortedTimestamps.map(timestamp => {
      const dataPoint: any = {
        timestamp,
        time: chartUtils.formatTime(timestamp)
      }

      enabledMetrics.forEach(metric => {
        const point = chartData[metric.key].find(p => p.timestamp === timestamp)
        dataPoint[metric.key] = point?.value ?? null
      })

      return dataPoint
    })
  }, [chartData, metrics])

  // 시간 범위 필터링
  const filteredData = useMemo(() => {
    if (timeRange === 'all') return chartDataPoints

    const now = new Date()
    let startTime: Date

    switch (timeRange) {
      case '1h':
        startTime = new Date(now.getTime() - 60 * 60 * 1000)
        break
      case '6h':
        startTime = new Date(now.getTime() - 6 * 60 * 60 * 1000)
        break
      case '24h':
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000)
        break
      default:
        return chartDataPoints
    }

    return chartDataPoints.filter(point => 
      new Date(point.timestamp) >= startTime
    )
  }, [chartDataPoints, timeRange])

  // 메트릭 활성화/비활성화
  const toggleMetric = useCallback((metricKey: MetricType) => {
    setMetrics(prev => prev.map(metric => 
      metric.key === metricKey 
        ? { ...metric, enabled: !metric.enabled }
        : metric
    ))
  }, [])

  // 데이터 내보내기
  const handleExport = useCallback(() => {
    const data = exportData()
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `performance-data-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [exportData])

  // 줌 리셋
  const resetZoom = useCallback(() => {
    setZoomRange(null)
  }, [setZoomRange])

  // 커스텀 툴팁
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null

    return (
      <Box
        bg={bgColor}
        border="1px solid"
        borderColor={borderColor}
        borderRadius="md"
        p={3}
        shadow="lg"
      >
        <Text fontSize="sm" fontWeight="bold" mb={2}>
          {chartUtils.formatDate(label)}
        </Text>
        {payload.map((entry: any, index: number) => {
          const metric = metrics.find(m => m.key === entry.dataKey)
          if (!metric) return null

          return (
            <HStack key={index} spacing={2}>
              <Box w={3} h={3} bg={entry.color} borderRadius="sm" />
              <Text fontSize="sm">
                {metric.name}: {entry.value?.toFixed(1)}{metric.unit}
              </Text>
            </HStack>
          )
        })}
      </Box>
    )
  }

  // 통계 정보 계산
  const statistics = useMemo(() => {
    const enabledMetrics = metrics.filter(m => m.enabled)
    return enabledMetrics.map(metric => {
      const data = chartData[metric.key]
      const avg = chartUtils.calculateAverage(data)
      const minMaxResult = chartUtils.findMinMax(data)
      const { min, max } = minMaxResult || { min: 0, max: 0 }
      
      return {
        ...metric,
        average: avg,
        min,
        max,
        current: data[data.length - 1]?.value ?? 0
      }
    })
  }, [chartData, metrics])

  if (error) {
    return (
      <Box
        p={6}
        bg={bgColor}
        border="1px solid"
        borderColor="red.200"
        borderRadius="lg"
        textAlign="center"
      >
        <Text color="red.500" fontSize="lg" fontWeight="bold" mb={2}>
          차트 로딩 오류
        </Text>
        <Text color={textColor} mb={4}>
          {error}
        </Text>
        <Button colorScheme="red" variant="outline" onClick={clearData}>
          데이터 초기화
        </Button>
      </Box>
    )
  }

  return (
    <Box
      className={className}
      bg={bgColor}
      border="1px solid"
      borderColor={borderColor}
      borderRadius="lg"
      p={4}
      h={isFullscreen ? '100vh' : 'auto'}
      position={isFullscreen ? 'fixed' : 'relative'}
      top={isFullscreen ? 0 : 'auto'}
      left={isFullscreen ? 0 : 'auto'}
      right={isFullscreen ? 0 : 'auto'}
      bottom={isFullscreen ? 0 : 'auto'}
      zIndex={isFullscreen ? 9999 : 'auto'}
    >
      <VStack spacing={4} align="stretch">
        {/* 헤더 */}
        <Flex justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Text fontSize="lg" fontWeight="bold">
              실시간 성능 모니터링
            </Text>
            <HStack spacing={4}>
              {statistics.map(stat => (
                <Badge
                  key={stat.key}
                  colorScheme={stat.current > 80 ? 'red' : stat.current > 60 ? 'yellow' : 'green'}
                  variant="subtle"
                >
                  {stat.name}: {stat.current.toFixed(1)}{stat.unit}
                </Badge>
              ))}
            </HStack>
          </VStack>

          {showControls && (
            <HStack spacing={2}>
              <Tooltip label="새로고침">
                <IconButton
                  aria-label="새로고침"
                  icon={<FiRefreshCw />}
                  size="sm"
                  variant="ghost"
                  onClick={() => window.location.reload()}
                  isLoading={isLoading}
                />
              </Tooltip>
              <Tooltip label="데이터 내보내기">
                <IconButton
                  aria-label="데이터 내보내기"
                  icon={<FiDownload />}
                  size="sm"
                  variant="ghost"
                  onClick={handleExport}
                />
              </Tooltip>
              <Tooltip label="줌 리셋">
                <IconButton
                  aria-label="줌 리셋"
                  icon={<FiZoomOut />}
                  size="sm"
                  variant="ghost"
                  onClick={resetZoom}
                  isDisabled={!zoomRange}
                />
              </Tooltip>
              <Tooltip label={isFullscreen ? '전체화면 해제' : '전체화면'}>
                <IconButton
                  aria-label="전체화면"
                  icon={<FiMaximize2 />}
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsFullscreen(!isFullscreen)}
                />
              </Tooltip>
            </HStack>
          )}
        </Flex>

        {/* 컨트롤 패널 */}
        {showControls && (
          <HStack spacing={4} wrap="wrap">
            <FormControl w="auto">
              <FormLabel fontSize="sm">시간 범위</FormLabel>
              <Select
                size="sm"
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                w="120px"
              >
                <option value="all">전체</option>
                <option value="1h">1시간</option>
                <option value="6h">6시간</option>
                <option value="24h">24시간</option>
              </Select>
            </FormControl>

            <FormControl w="auto">
              <FormLabel fontSize="sm">브러시</FormLabel>
              <Switch
                size="sm"
                isChecked={showBrush}
                onChange={(e) => setShowBrush(e.target.checked)}
              />
            </FormControl>

            <FormControl w="auto">
              <FormLabel fontSize="sm">격자</FormLabel>
              <Switch
                size="sm"
                isChecked={showGrid}
                onChange={(e) => setShowGrid(e.target.checked)}
              />
            </FormControl>

            <Divider orientation="vertical" h="40px" />

            <VStack align="start" spacing={1}>
              <Text fontSize="sm" fontWeight="medium">메트릭 선택</Text>
              <ButtonGroup size="xs" variant="outline">
                {metrics.map(metric => (
                  <Button
                    key={metric.key}
                    colorScheme={metric.enabled ? 'blue' : 'gray'}
                    variant={metric.enabled ? 'solid' : 'outline'}
                    onClick={() => toggleMetric(metric.key)}
                    leftIcon={
                      <Box
                        w={2}
                        h={2}
                        bg={metric.color}
                        borderRadius="full"
                      />
                    }
                  >
                    {metric.name}
                  </Button>
                ))}
              </ButtonGroup>
            </VStack>
          </HStack>
        )}

        {/* 차트 */}
        <Box h={height}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={filteredData}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              {showGrid && (
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke={gridColor}
                  opacity={0.5}
                />
              )}
              <XAxis
                dataKey="time"
                tick={{ fontSize: 12, fill: textColor }}
                axisLine={{ stroke: borderColor }}
                tickLine={{ stroke: borderColor }}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 12, fill: textColor }}
                axisLine={{ stroke: borderColor }}
                tickLine={{ stroke: borderColor }}
                label={{
                  value: '사용률 (%)',
                  angle: -90,
                  position: 'insideLeft',
                  style: { textAnchor: 'middle', fill: textColor }
                }}
              />
              <RechartsTooltip content={<CustomTooltip />} />
              <Legend />

              {/* 경고선 */}
              <ReferenceLine
                y={80}
                stroke="red"
                strokeDasharray="5 5"
                opacity={0.6}
                label={{ value: "위험", position: "top" }}
              />
              <ReferenceLine
                y={60}
                stroke="orange"
                strokeDasharray="5 5"
                opacity={0.6}
                label={{ value: "주의", position: "top" }}
              />

              {/* 메트릭 라인들 */}
              {metrics
                .filter(metric => metric.enabled)
                .map(metric => (
                  <Line
                    key={metric.key}
                    type="monotone"
                    dataKey={metric.key}
                    stroke={metric.color}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, stroke: metric.color, strokeWidth: 2 }}
                    name={metric.name}
                    connectNulls={false}
                  />
                ))}

              {/* 브러시 (확대/축소) */}
              {showBrush && filteredData.length > 20 && (
                <Brush
                  dataKey="time"
                  height={30}
                  stroke={borderColor}
                  fill={bgColor}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </Box>

        {/* 통계 정보 */}
        {showControls && statistics.length > 0 && (
          <HStack spacing={6} wrap="wrap">
            {statistics.map(stat => (
              <VStack key={stat.key} align="start" spacing={1}>
                <HStack>
                  <Box w={3} h={3} bg={stat.color} borderRadius="sm" />
                  <Text fontSize="sm" fontWeight="medium">
                    {stat.name}
                  </Text>
                </HStack>
                <HStack spacing={4} fontSize="xs" color={textColor}>
                  <Text>평균: {stat.average.toFixed(1)}{stat.unit}</Text>
                  <Text>최소: {stat.min.toFixed(1)}{stat.unit}</Text>
                  <Text>최대: {stat.max.toFixed(1)}{stat.unit}</Text>
                </HStack>
              </VStack>
            ))}
          </HStack>
        )}
      </VStack>
    </Box>
  )
}

export default RealtimeChart