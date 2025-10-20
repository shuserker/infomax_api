import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardBody,
  VStack,
  HStack,
  Text,
  Badge,
  Button,
  IconButton,
  Tooltip,
  Tag,
  TagLabel,
  Collapse,
  useColorModeValue,
  Flex,
  Spacer,
  Code,
  Grid,
  GridItem,
  Spinner,
  useToast
} from '@chakra-ui/react';
import { 
  FiStar, 
  FiInfo, 
  FiChevronDown, 
  FiChevronUp,
  FiClock,
  FiZap,
  FiSettings,
  FiBookOpen,
  FiCheckCircle,
  FiAlertTriangle,
  FiXCircle,
  FiCopy
} from 'react-icons/fi';

interface ApiParameter {
  name: string;
  type: string;
  required: boolean;
  description?: string;
  defaultValue?: string;
}

interface ApiPackage {
  id: string;
  category: string;
  itemName: string;
  fullName: string;
  urlPath: string;
  baseUrl: string;
  fullUrl: string;
  inputs: ApiParameter[];
  outputs: string[];
  description?: string;
  tags?: string[];
  isFavorite?: boolean;
  lastUsed?: string;
  usageCount?: number;
  status: 'active' | 'inactive';
}

interface ApiPackageCardProps {
  package: ApiPackage;
  onTest: (pkg: ApiPackage) => void;
  onToggleFavorite: (pkg: ApiPackage) => void;
  viewMode?: 'grid' | 'list';
  globalHealthStatus?: {
    status: 'checking' | 'online' | 'warning' | 'offline' | 'unknown';
    lastChecked: number;
    error?: string;
  };
  onHealthStatusUpdate?: (pkgId: string, status: 'checking' | 'online' | 'warning' | 'offline' | 'unknown', error?: string) => void;
}

const ApiPackageCard: React.FC<ApiPackageCardProps> = ({
  package: pkg,
  onTest,
  onToggleFavorite,
  viewMode = 'grid',
  globalHealthStatus,
  onHealthStatusUpdate
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'checking' | 'online' | 'warning' | 'offline' | 'unknown'>('unknown');
  const [healthError, setHealthError] = useState<string>('');
  const toast = useToast();
  
  const cardBg = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const headerBg = useColorModeValue('blue.50', 'blue.900');
  
  // 카테고리별 색상
  const getCategoryColor = (category: string) => {
    const colorMap: {[key: string]: string} = {
      '채권': 'blue',
      '주식': 'green', 
      '지수': 'purple',
      'ETF': 'orange',
      '파생': 'red',
      '외환': 'teal',
      '뉴스': 'yellow'
    };
    return colorMap[category] || 'gray';
  };

  // API 헬스체크 상태 반환 (구체적인 오류 정보 포함)
  const getHealthStatusInfo = () => {
    switch (healthStatus) {
      case 'online': 
        return { 
          color: 'green', 
          text: '정상', 
          icon: FiCheckCircle,
          bgColor: 'green.50',
          borderColor: 'green.200'
        };
      case 'warning': 
        return { 
          color: 'orange', 
          text: healthError || '경고', 
          icon: FiAlertTriangle,
          bgColor: 'orange.50',
          borderColor: 'orange.200'
        };
      case 'offline': 
        return { 
          color: 'red', 
          text: healthError || '오프라인', 
          icon: FiXCircle,
          bgColor: 'red.50',
          borderColor: 'red.200'
        };
      case 'unknown':
        return { 
          color: 'gray', 
          text: '미확인', 
          icon: null,
          bgColor: 'gray.50',
          borderColor: 'gray.200'
        };
      default: 
        return { 
          color: 'gray', 
          text: '확인중', 
          icon: null,
          bgColor: 'gray.50',
          borderColor: 'gray.200'
        };
    }
  };

  // API 테스트 모달과 동일한 로직으로 헬스체크 (이미 검증된 인프라 재사용)
  const performHealthCheck = async () => {
    try {
      setHealthStatus('checking');
      setHealthError('');
      
      const apiToken = localStorage.getItem('infomax_api_token');
      if (!apiToken) {
        setHealthStatus('warning');
        setHealthError('토큰 없음');
        return;
      }

      // 기본 파라미터 구성 (API 테스트 모달과 동일한 로직)
      const params: Record<string, string> = {};
      pkg.inputs.forEach(input => {
        if (pkg.urlPath === 'bond/market/mn_hist' || pkg.urlPath.includes('code') || pkg.urlPath.includes('search')) {
          params[input.name] = input.defaultValue || '';
        } else {
          if (input.defaultValue?.trim()) {
            params[input.name] = input.defaultValue.trim();
          }
        }
      });

      // API 테스트 모달과 동일한 URL 구성
      const localProxyUrl = `http://localhost:9001/api/infomax/${pkg.urlPath}`;
      const searchParams = new URLSearchParams();
      
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });

      const finalUrl = searchParams.toString() 
        ? `${localProxyUrl}?${searchParams.toString()}`
        : localProxyUrl;

      // API 테스트 모달과 동일한 요청
      const response = await fetch(finalUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        
        // InfoMax API 응답 구조 상세 분석
        if (result.success && result.data) {
          // 데이터 내부의 success 상태도 확인
          if (result.data.success === false) {
            // InfoMax API 내부에서 실패한 경우
            let errorMsg = '내부 오류';
            
            if (result.data.message?.errmsg) {
              const errMsg = result.data.message.errmsg;
              if (errMsg.includes('error params') || errMsg.includes('parameter')) {
                errorMsg = '파라미터 오류';
              } else if (errMsg.includes('auth') || errMsg.includes('token')) {
                errorMsg = '인증 오류';
              } else if (errMsg.includes('permission') || errMsg.includes('access')) {
                errorMsg = '권한 없음';
              } else {
                errorMsg = `API 오류: ${errMsg}`;
              }
            } else if (result.data.message?.desc) {
              const desc = result.data.message.desc;
              if (desc.includes('파라미터') || desc.includes('parameter')) {
                errorMsg = '파라미터 누락';
              } else if (desc.includes('인증') || desc.includes('토큰')) {
                errorMsg = '인증 오류';
              } else {
                errorMsg = `${desc.substring(0, 10)}...`;
              }
            }
            
            const status = 'warning';
            setHealthStatus(status);
            setHealthError(errorMsg);
            onHealthStatusUpdate?.(pkg.id, status, errorMsg);
          } else if (result.data.results && Array.isArray(result.data.results) && result.data.results.length > 0) {
            // 실제 데이터가 있는 경우만 정상
            const status = 'online';
            setHealthStatus(status);
            setHealthError('');
            onHealthStatusUpdate?.(pkg.id, status);
          } else {
            const status = 'warning';
            const error = '데이터 없음';
            setHealthStatus(status);
            setHealthError(error);
            onHealthStatusUpdate?.(pkg.id, status, error);
          }
        } else {
          const status = 'warning';
          const error = '응답 구조 이상';
          setHealthStatus(status);
          setHealthError(error);
          onHealthStatusUpdate?.(pkg.id, status, error);
        }
      } else {
        // 구체적인 HTTP 상태 코드별 오류 메시지
        let errorMessage = '';
        switch (response.status) {
          case 400:
            errorMessage = '파라미터 오류';
            break;
          case 401:
            errorMessage = '인증 오류';
            break;
          case 403:
            errorMessage = '권한 없음';
            break;
          case 404:
            errorMessage = 'API 없음';
            break;
          case 429:
            errorMessage = '요청 초과';
            break;
          case 500:
            errorMessage = '서버 오류';
            break;
          case 502:
            errorMessage = '게이트웨이 오류';
            break;
          case 503:
            errorMessage = '서비스 중단';
            break;
          case 504:
            errorMessage = '응답 지연';
            break;
          default:
            errorMessage = `HTTP ${response.status}`;
        }
        
        if (response.status >= 400 && response.status < 500) {
          const status = 'warning';
          setHealthStatus(status);
          setHealthError(errorMessage);
          onHealthStatusUpdate?.(pkg.id, status, errorMessage);
        } else {
          const status = 'offline';
          setHealthStatus(status);
          setHealthError(errorMessage);
          onHealthStatusUpdate?.(pkg.id, status, errorMessage);
        }
      }
    } catch (error) {
      console.log(`Health check failed for ${pkg.itemName}:`, error);
      
      // 네트워크 오류 타입별 구체적인 메시지
      let errorMessage = '';
      if (error instanceof TypeError) {
        if (error.message.includes('Failed to fetch') || error.message.includes('Load failed')) {
          errorMessage = '연결 실패';
        } else if (error.message.includes('NetworkError') || error.message.includes('ERR_NETWORK')) {
          errorMessage = '네트워크 오류';
        } else {
          errorMessage = '요청 오류';
        }
      } else if (error instanceof Error && error.name === 'AbortError') {
        errorMessage = '응답 지연';
      } else {
        errorMessage = '알 수 없는 오류';
      }
      
      const status = 'offline';
      setHealthStatus(status);
      setHealthError(errorMessage);
      onHealthStatusUpdate?.(pkg.id, status, errorMessage);
    }
  };

  // 자동 헬스체크 제거 - 수동 실행으로 변경
  
  // 전역 헬스체크 상태와 동기화 (캐시 및 중복 방지)
  useEffect(() => {
    if (globalHealthStatus) {
      // 캐시된 결과가 있고 최근 5분 이내인 경우 재사용
      const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
      const isCacheValid = globalHealthStatus.lastChecked > fiveMinutesAgo;
      
      if (globalHealthStatus.status !== healthStatus) {
        console.log(`🔄 상태 업데이트: ${pkg.itemName} ${healthStatus} → ${globalHealthStatus.status}`);
        
        // 유효한 캐시가 있으면 바로 적용
        if (isCacheValid && globalHealthStatus.status !== 'checking' && globalHealthStatus.status !== 'unknown') {
          console.log(`📋 캐시 사용: ${pkg.itemName} (${Math.round((Date.now() - globalHealthStatus.lastChecked) / 1000)}초 전)`);
          setHealthStatus(globalHealthStatus.status);
          if (globalHealthStatus.error) {
            setHealthError(globalHealthStatus.error);
          }
        }
        // 캐시가 없거나 checking 상태이고 현재가 unknown일 때만 헬스체크 실행
        else if (globalHealthStatus.status === 'checking' && healthStatus === 'unknown') {
          console.log(`🔥 헬스체크 시작: ${pkg.itemName}`);
          setHealthStatus('checking');
          performHealthCheck();
        }
        // 다른 확정된 상태는 바로 동기화
        else if (globalHealthStatus.status !== 'checking') {
          setHealthStatus(globalHealthStatus.status);
          if (globalHealthStatus.error) {
            setHealthError(globalHealthStatus.error);
          }
        }
      }
    }
  }, [globalHealthStatus?.status, globalHealthStatus?.lastChecked]); // lastChecked 추가로 캐시 체크


  const healthInfo = getHealthStatusInfo();

  // 리스트뷰일 때는 완전히 다른 레이아웃
  if (viewMode === 'list') {
    return (
      <Box
        bg={cardBg}
        borderRadius="lg"
        p={3}
        border="1px solid"
        borderColor={useColorModeValue('gray.200', 'gray.700')}
        _hover={{
          bg: hoverBg,
          borderColor: useColorModeValue('blue.300', 'blue.600'),
          boxShadow: 'md'
        }}
        transition="all 0.2s"
        mb={2}
      >
        <Flex 
          align="center" 
          gap={4} 
          onClick={(e) => {
            console.log('Flex 클릭됨 - 전파 차단');
            e.stopPropagation();
          }}
          onMouseDown={(e) => e.stopPropagation()}
        >
          {/* 헬스 상태 - 실제 Button 컴포넌트 사용 */}
          <Button
            px={2}
            py={1}
            h="32px"
            minW="80px"
            size="sm"
            variant="outline"
            colorScheme={healthInfo.color}
            bg={healthInfo.bgColor}
            borderColor={healthInfo.borderColor}
            isLoading={healthStatus === 'checking'}
            loadingText={healthInfo.text}
            onClick={(e) => {
              console.log('🔥 헬스체크 실행:', pkg.itemName);
              e.stopPropagation();
              performHealthCheck();
            }}
            _hover={{
              bg: `${healthInfo.color}.100`,
              borderColor: `${healthInfo.color}.300`,
              transform: 'scale(1.05)'
            }}
            _active={{
              transform: 'scale(0.95)'
            }}
            title="클릭하여 헬스체크 실행"
          >
            <HStack spacing={1}>
              {healthStatus !== 'checking' && healthInfo.icon && (
                <Box as={healthInfo.icon} w={3} h={3} />
              )}
              <Text fontSize="xs" fontWeight="semibold">
                {healthInfo.text}
              </Text>
            </HStack>
          </Button>

          {/* 카테고리 */}
          <Badge
            colorScheme={getCategoryColor(pkg.category)}
            variant="subtle"
            fontSize="xs"
            minW="60px"
            textAlign="center"
          >
            {pkg.category}
          </Badge>

          {/* API 정보 */}
          <Box flex={1}>
            <HStack spacing={3} align="center" justify="space-between">
              <VStack spacing={0} align="start" flex={1}>
                <HStack spacing={2} align="center">
                  <Text fontWeight="bold" fontSize="md" color="blue.600">
                    {pkg.itemName}
                  </Text>
                  {pkg.isFavorite && (
                    <Box as={FiStar} color="gold" w={3} h={3} />
                  )}
                </HStack>
                <Text fontSize="xs" color="gray.500" noOfLines={1}>
                  {pkg.fullName}
                </Text>
              </VStack>
              
              {/* URL 경로를 오른쪽으로 이동하여 가독성 향상 */}
              <Box
                px={2}
                py={1}
                bg={useColorModeValue('gray.100', 'gray.700')}
                borderRadius="md"
                minW="120px"
              >
                <Text fontSize="xs" fontFamily="mono" color="gray.600" textAlign="center">
                  {pkg.urlPath}
                </Text>
              </Box>
            </HStack>
          </Box>

          {/* 파라미터 수 */}
          <VStack spacing={0} minW="60px" textAlign="center">
            <Text fontSize="lg" fontWeight="bold" color="blue.500">
              {pkg.inputs.length}
            </Text>
            <Text fontSize="xs" color="gray.500">파라미터</Text>
          </VStack>

          {/* 필수 파라미터 수 */}
          <VStack spacing={0} minW="60px" textAlign="center">
            <Text fontSize="lg" fontWeight="bold" color="red.500">
              {pkg.inputs.filter(input => input.required).length}
            </Text>
            <Text fontSize="xs" color="gray.500">필수</Text>
          </VStack>

          {/* 마지막 사용 */}
          <VStack spacing={0} minW="80px" textAlign="center">
            <HStack spacing={1}>
              <Box as={FiClock} w={3} h={3} color="gray.400" />
              <Text fontSize="xs" color="gray.500">
                {pkg.lastUsed || '미사용'}
              </Text>
            </HStack>
            <Text fontSize="xs" color="gray.400">
              {pkg.usageCount || 0}회 사용
            </Text>
          </VStack>

          {/* 액션 버튼들 - 공간 효율적으로 재배치 */}
          <HStack spacing={2} minW="180px">
            {/* 즐겨찾기 */}
            <Tooltip label="즐겨찾기 토글">
              <IconButton
                icon={<FiStar />}
                size="sm"
                variant={pkg.isFavorite ? "solid" : "outline"}
                colorScheme={pkg.isFavorite ? "yellow" : "gray"}
                onClick={() => onToggleFavorite(pkg)}
                aria-label="즐겨찾기"
              />
            </Tooltip>
            
            {/* URL 복사 버튼 추가 */}
            <Tooltip label="API URL 복사">
              <IconButton
                icon={<FiCopy />}
                size="sm"
                variant="outline"
                colorScheme="gray"
                onClick={() => {
                  navigator.clipboard.writeText(pkg.fullUrl);
                  toast({
                    title: "URL 복사 완료",
                    description: `${pkg.itemName} API URL이 클립보드에 복사되었습니다.`,
                    status: "success",
                    duration: 2000,
                    isClosable: true,
                    position: "top"
                  });
                }}
                aria-label="URL 복사"
              />
            </Tooltip>
            
            {/* 테스트 버튼 */}
            <Button
              leftIcon={<FiZap />}
              colorScheme="blue"
              size="sm"
              onClick={() => onTest(pkg)}
              bgGradient="linear(to-r, blue.400, blue.600)"
              _hover={{
                bgGradient: "linear(to-r, blue.500, blue.700)",
                transform: "translateY(-1px)",
              }}
              borderRadius="md"
              minW="80px"
            >
              테스트
            </Button>
          </HStack>
        </Flex>
      </Box>
    );
  }

  // 기존 카드뷰
  return (
    <Card
      bg={cardBg}
      borderRadius="xl"
      _hover={{ 
        bg: hoverBg,
        transform: 'translateY(-2px)',
        boxShadow: 'xl'
      }}
      transition="all 0.2s"
      overflow="hidden"
      boxShadow="md"
    >
      {/* 헤더 */}
      <Box bg={headerBg} px={4} py={3}>
        <Flex align="center">
          <HStack spacing={3} flex={1}>
            <Badge 
              colorScheme={getCategoryColor(pkg.category)} 
              variant="solid" 
              borderRadius="full"
              px={3}
              py={1}
              fontWeight="bold"
            >
              {pkg.category}
            </Badge>
            
            {pkg.isFavorite && (
              <FiStar color="gold" />
            )}
            
            {/* 개선된 헬스체크 배지 - 클릭 가능한 Button으로 변경 */}
            <Button
              px={3}
              py={1.5}
              h="auto"
              size="sm"
              variant="outline"
              colorScheme={healthInfo.color}
              bg={healthInfo.bgColor}
              borderColor={healthInfo.borderColor}
              borderRadius="full"
              isLoading={healthStatus === 'checking'}
              loadingText={healthInfo.text}
              onClick={(e) => {
                console.log('🔥 카드뷰 헬스체크 실행:', pkg.itemName);
                e.stopPropagation();
                performHealthCheck();
              }}
              _hover={{ 
                bg: `${healthInfo.color}.100`,
                borderColor: `${healthInfo.color}.300`,
                transform: 'scale(1.05)', 
                boxShadow: 'md' 
              }}
              _active={{
                transform: 'scale(0.95)'
              }}
              title="클릭하여 헬스체크 실행"
            >
              <HStack spacing={1.5} align="center">
                {healthStatus !== 'checking' && healthInfo.icon && (
                  <Box as={healthInfo.icon} w={3} h={3} />
                )}
                <Text 
                  fontSize="xs" 
                  fontWeight="semibold"
                  lineHeight={1}
                >
                  {healthInfo.text}
                </Text>
              </HStack>
            </Button>
          </HStack>
        </Flex>
      </Box>

      <CardBody p={4}>
        <VStack spacing={4} align="stretch">
          
          {/* 제목 및 설명 */}
          <Box>
            <Text 
              fontSize="lg" 
              fontWeight="bold" 
              color="blue.500" 
              mb={1}
              cursor="pointer"
              _hover={{ 
                color: "blue.600", 
                textDecoration: "underline" 
              }}
              onClick={() => onTest(pkg)}
            >
              {pkg.fullName}
            </Text>
            <Text 
              fontSize="sm" 
              color="gray.600" 
              mb={2}
              cursor="pointer"
              _hover={{ 
                color: "gray.700" 
              }}
              onClick={() => onTest(pkg)}
            >
              {pkg.itemName}
            </Text>
            <Code fontSize="xs" p={1} borderRadius="md" bg="gray.100">
              {pkg.urlPath}
            </Code>
          </Box>

          {/* 통계 정보 */}
          <Grid templateColumns="repeat(3, 1fr)" gap={3}>
            <GridItem>
              <VStack spacing={1}>
                <Text fontSize="lg" fontWeight="bold" color="blue.500">
                  {pkg.inputs.length}
                </Text>
                <Text fontSize="xs" color="gray.500">파라미터</Text>
              </VStack>
            </GridItem>
            
            <GridItem>
              <VStack spacing={1}>
                <Text fontSize="lg" fontWeight="bold" color="green.500">
                  {pkg.inputs.filter(i => i.required).length}
                </Text>
                <Text fontSize="xs" color="gray.500">필수</Text>
              </VStack>
            </GridItem>
            
            <GridItem>
              <VStack spacing={1}>
                <HStack>
                  <FiClock size="14" />
                  <Text fontSize="xs" color="gray.500">
                    {pkg.lastUsed ? '최근 사용' : '미사용'}
                  </Text>
                </HStack>
                <Text fontSize="xs" color="gray.400">
                  {pkg.lastUsed || '-'}
                </Text>
              </VStack>
            </GridItem>
          </Grid>

          {/* 태그 */}
          {pkg.tags && pkg.tags.length > 0 && (
            <HStack wrap="wrap" spacing={2}>
              {pkg.tags.map(tag => (
                <Tag key={tag} size="sm" variant="outline" colorScheme="blue">
                  <TagLabel>{tag}</TagLabel>
                </Tag>
              ))}
            </HStack>
          )}

          {/* 액션 버튼 */}
          <HStack spacing={2}>
            <Button
              leftIcon={<FiZap />}
              colorScheme="blue"
              size="sm"
              onClick={() => onTest(pkg)}
              bgGradient="linear(to-r, blue.400, blue.600)"
              _hover={{
                bgGradient: "linear(to-r, blue.500, blue.700)",
                transform: "translateY(-1px)",
                boxShadow: "md"
              }}
              _active={{
                transform: "translateY(0)",
                boxShadow: "sm"
              }}
              fontWeight="semibold"
              borderRadius="lg"
              minW="100px"
            >
              API 테스트
            </Button>
            
            <Tooltip label="파라미터 상세보기">
              <IconButton
                icon={isExpanded ? <FiChevronUp /> : <FiChevronDown />}
                size="sm"
                variant="outline"
                onClick={() => setIsExpanded(!isExpanded)}
                aria-label="상세보기"
              />
            </Tooltip>
            
            <Tooltip label="API 문서">
              <IconButton
                icon={<FiBookOpen />}
                size="sm"
                variant="outline"
                aria-label="문서보기"
              />
            </Tooltip>
            
            <Tooltip label="즐겨찾기 토글">
              <IconButton
                icon={<FiStar />}
                size="sm"
                variant={pkg.isFavorite ? "solid" : "outline"}
                colorScheme={pkg.isFavorite ? "yellow" : "gray"}
                onClick={() => onToggleFavorite(pkg)}
                aria-label="즐겨찾기"
              />
            </Tooltip>
          </HStack>

          {/* 파라미터 상세 정보 */}
          <Collapse in={isExpanded}>
            <Box
              mt={3}
              p={3}
              bg={useColorModeValue('gray.50', 'gray.700')}
              borderRadius="md"
            >
              <Text fontWeight="semibold" mb={2} fontSize="sm">
                📋 파라미터 목록 ({pkg.inputs.length}개)
              </Text>
              
              <VStack spacing={2} align="stretch">
                {pkg.inputs.map(input => (
                  <Box key={input.name} p={2} bg={cardBg} borderRadius="md" boxShadow="sm">
                    <Flex align="center" mb={1}>
                      <Text fontWeight="medium" fontSize="sm" color="blue.600">
                        {input.name}
                      </Text>
                      <Spacer />
                      <Badge 
                        size="xs" 
                        colorScheme={input.required ? 'red' : 'green'}
                        variant={input.required ? 'solid' : 'outline'}
                      >
                        {input.required ? '필수' : '선택'}
                      </Badge>
                    </Flex>
                    
                    <HStack spacing={2} mb={1}>
                      <Badge size="xs" variant="outline">
                        {input.type}
                      </Badge>
                      {input.defaultValue && (
                        <Code fontSize="xs" p={1}>
                          기본: {input.defaultValue}
                        </Code>
                      )}
                    </HStack>
                    
                    {input.description && (
                      <Text fontSize="xs" color="gray.500">
                        {input.description}
                      </Text>
                    )}
                  </Box>
                ))}
              </VStack>
              
              {/* 빠른 액션 */}
              <HStack mt={3} spacing={2}>
                <Button
                  leftIcon={<FiSettings />}
                  size="xs"
                  variant="outline"
                  colorScheme="gray"
                >
                  기본값 설정
                </Button>
                <Button
                  leftIcon={<FiInfo />}
                  size="xs"
                  variant="outline"
                  colorScheme="blue"
                >
                  예제 보기
                </Button>
              </HStack>
            </Box>
          </Collapse>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default ApiPackageCard;
