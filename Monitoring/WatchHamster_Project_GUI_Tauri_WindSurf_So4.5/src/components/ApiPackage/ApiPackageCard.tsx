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
  Spinner
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
  FiXCircle
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
  description?: string;
  tags?: string[];
  isFavorite?: boolean;
  lastUsed?: string;
  usageCount?: number;
}

interface ApiPackageCardProps {
  package: ApiPackage;
  onTest: (pkg: ApiPackage) => void;
  onToggleFavorite: (pkg: ApiPackage) => void;
}

const ApiPackageCard: React.FC<ApiPackageCardProps> = ({
  package: pkg,
  onTest,
  onToggleFavorite
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'checking' | 'online' | 'warning' | 'offline'>('checking');
  const [healthError, setHealthError] = useState<string>('');
  
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
            
            setHealthStatus('warning');
            setHealthError(errorMsg);
          } else if (result.data.results && Array.isArray(result.data.results) && result.data.results.length > 0) {
            // 실제 데이터가 있는 경우만 정상
            setHealthStatus('online');
            setHealthError('');
          } else {
            setHealthStatus('warning');
            setHealthError('데이터 없음');
          }
        } else {
          setHealthStatus('warning');
          setHealthError('응답 구조 이상');
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
          setHealthStatus('warning');
          setHealthError(errorMessage);
        } else {
          setHealthStatus('offline');
          setHealthError(errorMessage);
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
      
      setHealthStatus('offline');
      setHealthError(errorMessage);
    }
  };

  // 컴포넌트 마운트 시 헬스체크 실행
  useEffect(() => {
    // 2-5초 랜덤 딜레이로 동시 호출 방지
    const delay = 2000 + Math.random() * 3000;
    const timer = setTimeout(performHealthCheck, delay);
    
    return () => clearTimeout(timer);
  }, [pkg.fullUrl]); // eslint-disable-line react-hooks/exhaustive-deps


  const healthInfo = getHealthStatusInfo();

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
            
            {/* 개선된 헬스체크 배지 */}
            <Box
              px={3}
              py={1.5}
              borderRadius="full"
              bg={healthInfo.bgColor}
              border="1px solid"
              borderColor={healthInfo.borderColor}
              transition="all 0.2s"
              _hover={{ transform: 'scale(1.05)', boxShadow: 'md' }}
            >
              <HStack spacing={1.5} align="center">
                {healthStatus === 'checking' ? (
                  <Spinner size="xs" color={`${healthInfo.color}.500`} />
                ) : healthInfo.icon ? (
                  <Box as={healthInfo.icon} w={3} h={3} color={`${healthInfo.color}.600`} />
                ) : null}
                <Text 
                  fontSize="xs" 
                  fontWeight="semibold" 
                  color={`${healthInfo.color}.700`}
                  lineHeight={1}
                >
                  {healthInfo.text}
                </Text>
              </HStack>
            </Box>
          </HStack>
          
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
              flex={1}
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
            >
              🚀 API 테스트
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
