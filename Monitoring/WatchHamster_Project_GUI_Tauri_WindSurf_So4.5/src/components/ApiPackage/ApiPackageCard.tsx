import React, { useState } from 'react';
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
  GridItem
} from '@chakra-ui/react';
import { 
  FiPlay, 
  FiStar, 
  FiInfo, 
  FiChevronDown, 
  FiChevronUp,
  FiClock,
  FiZap,
  FiSettings,
  FiBookOpen
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
  
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
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

  // API 복잡도 계산
  const getComplexity = () => {
    const requiredParams = pkg.inputs.filter(input => input.required).length;
    if (requiredParams === 0) return { level: 'simple', color: 'green', text: '간단' };
    if (requiredParams <= 2) return { level: 'medium', color: 'yellow', text: '보통' };
    return { level: 'complex', color: 'red', text: '복잡' };
  };

  const complexity = getComplexity();

  return (
    <Card
      bg={cardBg}
      border="1px"
      borderColor={borderColor}
      borderRadius="xl"
      _hover={{ 
        bg: hoverBg,
        transform: 'translateY(-2px)',
        boxShadow: 'lg'
      }}
      transition="all 0.2s"
      overflow="hidden"
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
            
            <Badge 
              colorScheme={complexity.color} 
              variant="outline"
              size="sm"
            >
              {complexity.text}
            </Badge>
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
              {pkg.itemName}
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
              {pkg.fullName}
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
                  <Box key={input.name} p={2} bg={cardBg} borderRadius="md" border="1px" borderColor={borderColor}>
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
