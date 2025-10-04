/**
 * 대시보드 설정 컴포넌트
 * 상세/심플 모드 전환
 */

import React from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  VStack,
  HStack,
  Text,
  Switch,
  FormControl,
  FormLabel,
  FormHelperText,
  RadioGroup,
  Radio,
  Stack,
  Badge,
  Divider,
  useColorModeValue
} from '@chakra-ui/react';
import { useAppStore } from '../../stores/useAppStore';

export const DashboardSettings: React.FC = () => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // 설정 가져오기
  const dashboardMode = useAppStore((state) => state.settings?.dashboardMode || 'detailed');
  const setDashboardMode = useAppStore((state) => state.setDashboardMode);

  const handleModeChange = (value: string) => {
    setDashboardMode(value as 'detailed' | 'simple');
  };

  return (
    <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">📊 대시보드 설정</Heading>
          <Badge colorScheme="blue">UI</Badge>
        </HStack>
      </CardHeader>

      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 대시보드 모드 선택 */}
          <FormControl>
            <FormLabel fontWeight="bold">대시보드 모드</FormLabel>
            <RadioGroup value={dashboardMode} onChange={handleModeChange}>
              <Stack spacing={4}>
                <HStack
                  p={4}
                  borderWidth="2px"
                  borderRadius="md"
                  borderColor={dashboardMode === 'detailed' ? 'blue.500' : 'gray.200'}
                  bg={dashboardMode === 'detailed' ? 'blue.50' : 'transparent'}
                  cursor="pointer"
                  onClick={() => handleModeChange('detailed')}
                  transition="all 0.2s"
                >
                  <Radio value="detailed" colorScheme="blue" />
                  <VStack align="start" spacing={1} flex={1}>
                    <HStack>
                      <Text fontWeight="bold">상세 모드</Text>
                      <Badge colorScheme="blue">기본</Badge>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      뉴스 모니터링, 실시간 차트, 시스템 메트릭, 서비스 상태, 알림 등 모든 정보 표시
                    </Text>
                  </VStack>
                </HStack>

                <HStack
                  p={4}
                  borderWidth="2px"
                  borderRadius="md"
                  borderColor={dashboardMode === 'simple' ? 'blue.500' : 'gray.200'}
                  bg={dashboardMode === 'simple' ? 'blue.50' : 'transparent'}
                  cursor="pointer"
                  onClick={() => handleModeChange('simple')}
                  transition="all 0.2s"
                >
                  <Radio value="simple" colorScheme="blue" />
                  <VStack align="start" spacing={1} flex={1}>
                    <HStack>
                      <Text fontWeight="bold">심플 모드</Text>
                      <Badge colorScheme="green">간결</Badge>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      전체 시스템 개요와 회사별 현황만 표시 (멀티 테넌트 중심)
                    </Text>
                  </VStack>
                </HStack>
              </Stack>
            </RadioGroup>
            <FormHelperText mt={4}>
              💡 대시보드 모드는 즉시 적용됩니다. 페이지를 새로고침하세요.
            </FormHelperText>
          </FormControl>

          <Divider />

          {/* 모드별 설명 */}
          <VStack spacing={3} align="stretch">
            <Text fontWeight="bold" fontSize="sm">모드별 특징</Text>
            
            <HStack spacing={4} align="start">
              <VStack align="start" spacing={2} flex={1}>
                <Text fontSize="sm" fontWeight="bold" color="blue.500">
                  📊 상세 모드
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • POSCO 뉴스 모니터링 상태
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • 실시간 시스템 차트
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • CPU/메모리/디스크 메트릭
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • 서비스 상태 그리드
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • Git Pages 배포 상태
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • 최근 알림 위젯
                </Text>
              </VStack>

              <VStack align="start" spacing={2} flex={1}>
                <Text fontSize="sm" fontWeight="bold" color="green.500">
                  🎯 심플 모드
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • 전체 시스템 개요 (6개 지표)
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • 회사별 현황 카드
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • Git Pages 배포 상태
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • 멀티 테넌트 중심 UI
                </Text>
                <Text fontSize="xs" color="gray.600">
                  • 빠른 로딩 & 간결한 디자인
                </Text>
              </VStack>
            </HStack>
          </VStack>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default DashboardSettings;
