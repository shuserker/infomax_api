import React, { useState, useCallback } from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Button,
  useColorModeValue,
  Badge,
  Divider,
  Switch,
  FormControl,
  FormLabel,
  Alert,
  AlertIcon,
  Card,
  CardBody,
} from '@chakra-ui/react';
import { LogViewer } from '../components/Logs/LogViewer';
import { useLogViewer, useLogStream } from '../hooks/useLogViewer';
import { LogFilter } from '../types/logs';

const Logs: React.FC = () => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  const [isStreamMode, setIsStreamMode] = useState(false);
  
  // 일반 로그 뷰어 훅
  const {
    logs: staticLogs,
    total,
    hasMore,
    isLoading: isStaticLoading,
    error: staticError,
    filter,
    setFilter,
    loadMore,
    refresh,
    clearLogs,
  } = useLogViewer({
    autoRefresh: !isStreamMode,
    refreshInterval: 5000,
    pageSize: 100,
    maxEntries: 1000,
  });

  // 실시간 로그 스트림 훅
  const {
    logs: streamLogs,
    isConnected,
    error: streamError,
    clearStream,
  } = useLogStream();

  const handleFilterChange = useCallback((newFilter: LogFilter) => {
    setFilter(newFilter);
  }, [setFilter]);

  const handleModeToggle = useCallback((checked: boolean) => {
    setIsStreamMode(checked);
    if (checked) {
      clearLogs();
    } else {
      clearStream();
    }
  }, [clearLogs, clearStream]);

  const currentLogs = isStreamMode ? streamLogs : staticLogs;
  const currentError = isStreamMode ? streamError : staticError;
  const isLoading = !isStreamMode && isStaticLoading;

  // 로그 통계 계산
  const logStats = React.useMemo(() => {
    const stats = {
      total: currentLogs.length,
      error: 0,
      warn: 0,
      info: 0,
      debug: 0,
      critical: 0,
    };

    currentLogs.forEach(log => {
      switch (log.level) {
        case 'ERROR':
          stats.error++;
          break;
        case 'WARN':
          stats.warn++;
          break;
        case 'INFO':
          stats.info++;
          break;
        case 'DEBUG':
          stats.debug++;
          break;
        case 'CRITICAL':
          stats.critical++;
          break;
      }
    });

    return stats;
  }, [currentLogs]);

  return (
    <Box className="fade-in" p={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>로그 뷰어</Heading>
          <Text color="gray.600">시스템 로그를 실시간으로 모니터링하고 관리합니다</Text>
        </Box>

        {/* 모드 전환 및 상태 */}
        <Card>
          <CardBody>
            <HStack justify="space-between" align="center">
              <HStack spacing={4}>
                <FormControl display="flex" alignItems="center">
                  <FormLabel htmlFor="stream-mode" mb="0" fontSize="sm">
                    실시간 스트리밍
                  </FormLabel>
                  <Switch
                    id="stream-mode"
                    isChecked={isStreamMode}
                    onChange={(e) => handleModeToggle(e.target.checked)}
                  />
                </FormControl>
                
                {isStreamMode && (
                  <HStack spacing={2}>
                    <Badge colorScheme={isConnected ? 'green' : 'red'}>
                      {isConnected ? '연결됨' : '연결 끊김'}
                    </Badge>
                    <Text fontSize="sm" color="gray.600">
                      실시간 로그 스트림
                    </Text>
                  </HStack>
                )}
              </HStack>

              <HStack spacing={2}>
                {!isStreamMode && (
                  <Button size="sm" onClick={refresh} isLoading={isLoading}>
                    새로고침
                  </Button>
                )}
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={isStreamMode ? clearStream : clearLogs}
                >
                  로그 지우기
                </Button>
              </HStack>
            </HStack>
          </CardBody>
        </Card>

        {/* 오류 표시 */}
        {currentError && (
          <Alert status="error">
            <AlertIcon />
            {currentError}
          </Alert>
        )}

        {/* 로그 뷰어 */}
        <Card>
          <CardBody p={0}>
            <LogViewer
              logs={currentLogs}
              isLoading={isLoading}
              onLoadMore={isStreamMode ? undefined : loadMore}
              hasMore={isStreamMode ? false : hasMore}
              filter={filter}
              onFilterChange={handleFilterChange}
              height={600}
            />
          </CardBody>
        </Card>

        {/* 로그 통계 */}
        <Card>
          <CardBody>
            <Text fontWeight="bold" mb={3}>로그 통계</Text>
            <HStack spacing={6} flexWrap="wrap">
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="red.700">
                  {logStats.critical}
                </Text>
                <Text fontSize="sm" color="gray.600">심각</Text>
              </VStack>
              <Divider orientation="vertical" h="50px" />
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="red.500">
                  {logStats.error}
                </Text>
                <Text fontSize="sm" color="gray.600">오류</Text>
              </VStack>
              <Divider orientation="vertical" h="50px" />
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="yellow.500">
                  {logStats.warn}
                </Text>
                <Text fontSize="sm" color="gray.600">경고</Text>
              </VStack>
              <Divider orientation="vertical" h="50px" />
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  {logStats.info}
                </Text>
                <Text fontSize="sm" color="gray.600">정보</Text>
              </VStack>
              <Divider orientation="vertical" h="50px" />
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="gray.500">
                  {logStats.debug}
                </Text>
                <Text fontSize="sm" color="gray.600">디버그</Text>
              </VStack>
              <Divider orientation="vertical" h="50px" />
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                  {logStats.total}
                </Text>
                <Text fontSize="sm" color="gray.600">전체</Text>
              </VStack>
            </HStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
};

export default Logs;