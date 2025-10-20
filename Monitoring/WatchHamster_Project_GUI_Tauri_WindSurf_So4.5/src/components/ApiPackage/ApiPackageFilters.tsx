import React, { useState } from 'react';
import {
  Box,
  HStack,
  VStack,
  Input,
  InputGroup,
  InputLeftElement,
  Button,
  Badge,
  Wrap,
  WrapItem,
  Menu,
  MenuButton,
  MenuList,
  MenuItemOption,
  Text,
  Checkbox,
  CheckboxGroup,
  useColorModeValue,
  Flex,
  Spacer
} from '@chakra-ui/react';
import {
  FiSearch,
  FiFilter,
  FiChevronDown,
  FiX,
  FiStar,
  FiClock,
  FiTrendingUp
} from 'react-icons/fi';

export interface FilterState {
  searchTerm: string;
  categories: string[];
  healthErrorType: string[];
  showFavoritesOnly: boolean;
  sortBy: 'name' | 'category' | 'lastUsed' | 'popularity';
  sortOrder: 'asc' | 'desc';
}

interface ApiPackageFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  availableCategories: string[];
  totalCount: number;
  filteredCount: number;
}

const ApiPackageFilters: React.FC<ApiPackageFiltersProps> = ({
  filters,
  onFiltersChange,
  availableCategories,
  totalCount,
  filteredCount
}) => {
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  
  // 모든 color mode values를 최상위에서 선언
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const advancedBgColor = useColorModeValue('gray.50', 'gray.700');
  const cardBgColor = useColorModeValue('white', 'gray.800');
  const shadowColor = useColorModeValue('xl', 'dark-lg');

  const updateFilters = (updates: Partial<FilterState>) => {
    onFiltersChange({ ...filters, ...updates });
  };

  const clearAllFilters = () => {
    onFiltersChange({
      searchTerm: '',
      categories: [],
      healthErrorType: [],
      showFavoritesOnly: false,
      sortBy: 'name',
      sortOrder: 'asc'
    });
  };

  const activeFilterCount = 
    (filters.categories.length > 0 ? 1 : 0) +
    (filters.healthErrorType.length > 0 ? 1 : 0) +
    (filters.showFavoritesOnly ? 1 : 0) +
    (filters.searchTerm.length > 0 ? 1 : 0);

  return (
    <Box
      bg={cardBgColor}
      borderRadius="xl"
      boxShadow={shadowColor}
      border="1px"
      borderColor={borderColor}
      overflow="hidden"
      mb={6}
    >
      <VStack spacing={0} align="stretch">
        {/* 상단: 검색 및 기본 필터 */}
        <Box p={6} borderBottom="1px" borderBottomColor={borderColor}>
          <HStack spacing={4}>
          {/* 검색 */}
          <InputGroup maxW="400px" flex={1}>
            <InputLeftElement>
              <FiSearch color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="API 이름, 카테고리, 태그로 검색..."
              value={filters.searchTerm}
              onChange={(e) => updateFilters({ searchTerm: e.target.value })}
            />
          </InputGroup>

          {/* 즐겨찾기 토글 */}
          <Button
            leftIcon={<FiStar />}
            variant={filters.showFavoritesOnly ? 'solid' : 'outline'}
            colorScheme={filters.showFavoritesOnly ? 'yellow' : 'gray'}
            onClick={() => updateFilters({ showFavoritesOnly: !filters.showFavoritesOnly })}
            size="md"
          >
            즐겨찾기
          </Button>

          {/* 정렬 */}
          <Menu>
            <MenuButton as={Button} rightIcon={<FiChevronDown />} variant="outline">
              {
                filters.sortBy === 'name' ? '이름순' :
                filters.sortBy === 'category' ? '카테고리순' :
                filters.sortBy === 'lastUsed' ? '최근사용순' : '인기순'
              }
            </MenuButton>
            <MenuList>
              <MenuItemOption
                value="name"
                isChecked={filters.sortBy === 'name'}
                onClick={() => updateFilters({ sortBy: 'name' })}
              >
                이름순
              </MenuItemOption>
              <MenuItemOption
                value="category"
                isChecked={filters.sortBy === 'category'}
                onClick={() => updateFilters({ sortBy: 'category' })}
              >
                카테고리순
              </MenuItemOption>
              <MenuItemOption
                value="lastUsed"
                isChecked={filters.sortBy === 'lastUsed'}
                onClick={() => updateFilters({ sortBy: 'lastUsed' })}
              >
                <HStack>
                  <FiClock />
                  <Text>최근사용순</Text>
                </HStack>
              </MenuItemOption>
              <MenuItemOption
                value="popularity"
                isChecked={filters.sortBy === 'popularity'}
                onClick={() => updateFilters({ sortBy: 'popularity' })}
              >
                <HStack>
                  <FiTrendingUp />
                  <Text>인기순</Text>
                </HStack>
              </MenuItemOption>
            </MenuList>
          </Menu>

          {/* 고급 필터 토글 */}
          <Button
            leftIcon={<FiFilter />}
            variant="outline"
            onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
            colorScheme={activeFilterCount > 0 ? 'blue' : 'gray'}
          >
            필터 {activeFilterCount > 0 && `(${activeFilterCount})`}
          </Button>

          {/* 필터 초기화 */}
          {activeFilterCount > 0 && (
            <Button
              leftIcon={<FiX />}
              variant="ghost"
              colorScheme="red"
              onClick={clearAllFilters}
              size="sm"
            >
              초기화
            </Button>
          )}
          </HStack>
        </Box>

        {/* 고급 필터 */}
        {isAdvancedOpen && (
          <Box
            p={6}
            bg={advancedBgColor}
          >
            <VStack spacing={6} align="stretch">
              
              {/* 카테고리 필터 */}
              <Box>
                <Text fontWeight="bold" mb={4} fontSize="md" color="gray.700">
                  📊 카테고리
                </Text>
                <CheckboxGroup
                  value={filters.categories}
                  onChange={(values) => updateFilters({ categories: values as string[] })}
                >
                  <Wrap spacing={4}>
                    {availableCategories.map(category => (
                      <WrapItem key={category}>
                        <Checkbox 
                          value={category} 
                          colorScheme="blue"
                          size="md"
                          borderRadius="md"
                          _checked={{
                            bg: 'blue.500',
                            borderColor: 'blue.500',
                            color: 'white'
                          }}
                        >
                          <Text fontSize="sm" fontWeight="medium">{category}</Text>
                        </Checkbox>
                      </WrapItem>
                    ))}
                  </Wrap>
                </CheckboxGroup>
              </Box>

              {/* 헬스체크 오류 분류 필터 */}
              <Box>
                <Text fontWeight="bold" mb={4} fontSize="md" color="gray.700">
                  🔍 헬스체크 상태 필터
                </Text>
                <CheckboxGroup
                  value={filters.healthErrorType}
                  onChange={(values) => updateFilters({ healthErrorType: values as string[] })}
                >
                  <VStack spacing={4} align="stretch">
                    {/* 정상 상태 */}
                    <Box p={4} bg={cardBgColor} borderRadius="lg" border="1px" borderColor="green.200">
                      <Checkbox value="online" colorScheme="green" size="md">
                        <HStack>
                          <Badge colorScheme="green" variant="solid" fontSize="xs">정상</Badge>
                          <Text fontSize="sm" fontWeight="medium">API 정상 작동</Text>
                        </HStack>
                      </Checkbox>
                    </Box>
                    
                    {/* 경고 상태 세부 분류 */}
                    <Box p={4} bg={cardBgColor} borderRadius="lg" border="1px" borderColor="yellow.200">
                      <Text fontSize="sm" color="yellow.600" fontWeight="bold" mb={3}>⚠️ 경고 상태</Text>
                      <Wrap spacing={3}>
                        {['파라미터 오류', '인증 오류', '권한 없음', '데이터 없음', 'API 없음', '요청 초과', '응답 구조 이상'].map(errorType => (
                          <WrapItem key={errorType}>
                            <Checkbox value={errorType} colorScheme="yellow" size="sm">
                              <Text fontSize="xs">{errorType}</Text>
                            </Checkbox>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>

                    {/* 오프라인 상태 세부 분류 */}
                    <Box p={4} bg={cardBgColor} borderRadius="lg" border="1px" borderColor="red.200">
                      <Text fontSize="sm" color="red.600" fontWeight="bold" mb={3}>🔴 오프라인 상태</Text>
                      <Wrap spacing={3}>
                        {['서버 오류', '게이트웨이 오류', '서비스 중단', '응답 지연', '연결 실패', '네트워크 오류', '알 수 없는 오류'].map(errorType => (
                          <WrapItem key={errorType}>
                            <Checkbox value={errorType} colorScheme="red" size="sm">
                              <Text fontSize="xs">{errorType}</Text>
                            </Checkbox>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>

                    {/* 기타 상태 */}
                    <HStack spacing={4}>
                      <Box p={4} bg={cardBgColor} borderRadius="lg" border="1px" borderColor="blue.200" flex={1}>
                        <Checkbox value="checking" colorScheme="blue" size="md">
                          <HStack>
                            <Badge colorScheme="blue" variant="solid" fontSize="xs">확인중</Badge>
                            <Text fontSize="sm" fontWeight="medium">헬스체크 진행 중</Text>
                          </HStack>
                        </Checkbox>
                      </Box>
                      <Box p={4} bg={cardBgColor} borderRadius="lg" border="1px" borderColor="gray.200" flex={1}>
                        <Checkbox value="unknown" colorScheme="gray" size="md">
                          <HStack>
                            <Badge colorScheme="gray" variant="solid" fontSize="xs">미확인</Badge>
                            <Text fontSize="sm" fontWeight="medium">헬스체크 미실행</Text>
                          </HStack>
                        </Checkbox>
                      </Box>
                    </HStack>
                  </VStack>
                </CheckboxGroup>
              </Box>

              {/* 빠른 필터 프리셋 */}
              <Box>
                <Text fontWeight="bold" mb={4} fontSize="md" color="gray.700">
                  🚀 빠른 필터
                </Text>
                <Wrap spacing={3}>
                  <Button
                    onClick={() => updateFilters({ categories: ['채권'] })}
                    colorScheme="blue"
                  >
                    채권 API만
                  </Button>
                  <Button
                    onClick={() => updateFilters({ categories: ['주식'] })}
                    colorScheme="green"
                  >
                    주식 API만
                  </Button>
                  <Button
                    onClick={() => updateFilters({ healthErrorType: ['online'] })}
                    colorScheme="green"
                  >
                    정상 API만
                  </Button>
                  <Button
                    onClick={() => updateFilters({ healthErrorType: ['파라미터 오류', '인증 오류'] })}
                    colorScheme="yellow"
                  >
                    파라미터/인증 오류
                  </Button>
                  <Button
                    onClick={() => updateFilters({ healthErrorType: ['데이터 없음'] })}
                    colorScheme="orange"
                  >
                    데이터 없음
                  </Button>
                  <Button
                    onClick={() => updateFilters({ healthErrorType: ['서버 오류', '연결 실패', '네트워크 오류'] })}
                    colorScheme="red"
                  >
                    연결/서버 문제
                  </Button>
                  <Button
                    onClick={() => updateFilters({ 
                      sortBy: 'lastUsed',
                      sortOrder: 'desc'
                    })}
                    colorScheme="purple"
                  >
                    최근 사용
                  </Button>
                </Wrap>
              </Box>
            </VStack>
          </Box>
        )}

        {/* 하단: 결과 통계 및 활성 필터 태그 */}
        <Box p={6} borderTop="1px" borderTopColor={borderColor}>
          <Flex align="center" wrap="wrap" gap={2}>
          <Text fontSize="sm" color="gray.600">
            전체 {totalCount}개 중 <Text as="span" fontWeight="bold" color="blue.500">{filteredCount}개</Text> 표시
          </Text>
          
          <Spacer />
          
          {/* 활성 필터 태그 */}
          <Wrap spacing={1}>
            {filters.categories.map(category => (
              <WrapItem key={category}>
                <Badge
                  colorScheme="blue"
                  variant="solid"
                  cursor="pointer"
                  onClick={() => updateFilters({ 
                    categories: filters.categories.filter(c => c !== category) 
                  })}
                  _hover={{ opacity: 0.8 }}
                >
                  {category} ✕
                </Badge>
              </WrapItem>
            ))}
            
            {filters.healthErrorType.map(healthType => {
              // 에러 타입별 색상 결정
              const getColorScheme = (type: string) => {
                if (type === 'online') return 'green';
                if (type === 'checking') return 'blue';
                if (type === 'unknown') return 'gray';
                
                // 경고 상태 에러들
                const warningErrors = ['파라미터 오류', '인증 오류', '권한 없음', '데이터 없음', 'API 없음', '요청 초과', '응답 구조 이상'];
                if (warningErrors.includes(type)) return 'yellow';
                
                // 오프라인 상태 에러들
                const offlineErrors = ['서버 오류', '게이트웨이 오류', '서비스 중단', '응답 지연', '연결 실패', '네트워크 오류', '알 수 없는 오류'];
                if (offlineErrors.includes(type)) return 'red';
                
                return 'gray';
              };

              // 표시할 라벨 결정 (상태는 그대로, 에러는 약간 축약)
              const getDisplayLabel = (type: string) => {
                if (type === 'online') return '정상';
                if (type === 'checking') return '확인중';
                if (type === 'unknown') return '미확인';
                return type; // 나머지는 원본 그대로
              };

              return (
                <WrapItem key={healthType}>
                  <Badge
                    colorScheme={getColorScheme(healthType)}
                    variant="solid"
                    cursor="pointer"
                    onClick={() => updateFilters({ 
                      healthErrorType: filters.healthErrorType.filter(c => c !== healthType) 
                    })}
                    _hover={{ opacity: 0.8 }}
                  >
                    {getDisplayLabel(healthType)} ✕
                  </Badge>
                </WrapItem>
              );
            })}
            
            {filters.showFavoritesOnly && (
              <WrapItem>
                <Badge
                  colorScheme="yellow"
                  variant="solid"
                  cursor="pointer"
                  onClick={() => updateFilters({ showFavoritesOnly: false })}
                  _hover={{ opacity: 0.8 }}
                >
                  ⭐ 즐겨찾기 ✕
                </Badge>
              </WrapItem>
            )}
          </Wrap>
          </Flex>
        </Box>
      </VStack>
    </Box>
  );
};

export default ApiPackageFilters;
