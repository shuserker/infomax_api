import React, { useState } from 'react';
import {
  Box,
  HStack,
  VStack,
  Input,
  InputGroup,
  InputLeftElement,
  Button,
  ButtonGroup,
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
  Stack,
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
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

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
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="xl"
      p={4}
      mb={6}
    >
      <VStack spacing={4} align="stretch">
        
        {/* 상단: 검색 및 기본 필터 */}
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

        {/* 고급 필터 */}
        {isAdvancedOpen && (
          <Box
            p={4}
            bg={useColorModeValue('gray.50', 'gray.700')}
            borderRadius="lg"
            border="1px"
            borderColor={borderColor}
          >
            <VStack spacing={4} align="stretch">
              
              {/* 카테고리 필터 */}
              <Box>
                <Text fontWeight="semibold" mb={2} fontSize="sm">
                  📊 카테고리
                </Text>
                <CheckboxGroup
                  value={filters.categories}
                  onChange={(values) => updateFilters({ categories: values as string[] })}
                >
                  <Wrap spacing={3}>
                    {availableCategories.map(category => (
                      <WrapItem key={category}>
                        <Checkbox value={category} colorScheme="blue">
                          {category}
                        </Checkbox>
                      </WrapItem>
                    ))}
                  </Wrap>
                </CheckboxGroup>
              </Box>

              {/* 헬스체크 오류 분류 필터 */}
              <Box>
                <Text fontWeight="semibold" mb={2} fontSize="sm">
                  🔍 헬스체크 오류 분류
                </Text>
                <CheckboxGroup
                  value={filters.healthErrorType}
                  onChange={(values) => updateFilters({ healthErrorType: values as string[] })}
                >
                  <VStack spacing={3} align="stretch">
                    {/* 정상 상태 */}
                    <Checkbox value="online" colorScheme="green">
                      <Badge colorScheme="green" variant="outline" mr={2}>정상</Badge>
                      API 정상 작동
                    </Checkbox>
                    
                    {/* 경고 상태 세부 분류 */}
                    <Box>
                      <Text fontSize="xs" color="orange.600" fontWeight="bold" mb={1}>⚠️ 경고 상태:</Text>
                      <Stack direction="row" spacing={4} flexWrap="wrap">
                        <Checkbox value="파라미터 오류" colorScheme="yellow" size="sm">
                          파라미터 오류
                        </Checkbox>
                        <Checkbox value="인증 오류" colorScheme="yellow" size="sm">
                          인증 오류
                        </Checkbox>
                        <Checkbox value="권한 없음" colorScheme="yellow" size="sm">
                          권한 없음
                        </Checkbox>
                        <Checkbox value="데이터 없음" colorScheme="yellow" size="sm">
                          데이터 없음
                        </Checkbox>
                        <Checkbox value="API 없음" colorScheme="yellow" size="sm">
                          API 없음
                        </Checkbox>
                        <Checkbox value="요청 초과" colorScheme="yellow" size="sm">
                          요청 초과
                        </Checkbox>
                        <Checkbox value="응답 구조 이상" colorScheme="yellow" size="sm">
                          응답 구조 이상
                        </Checkbox>
                      </Stack>
                    </Box>

                    {/* 오프라인 상태 세부 분류 */}
                    <Box>
                      <Text fontSize="xs" color="red.600" fontWeight="bold" mb={1}>🔴 오프라인 상태:</Text>
                      <Stack direction="row" spacing={4} flexWrap="wrap">
                        <Checkbox value="서버 오류" colorScheme="red" size="sm">
                          서버 오류
                        </Checkbox>
                        <Checkbox value="게이트웨이 오류" colorScheme="red" size="sm">
                          게이트웨이 오류
                        </Checkbox>
                        <Checkbox value="서비스 중단" colorScheme="red" size="sm">
                          서비스 중단
                        </Checkbox>
                        <Checkbox value="응답 지연" colorScheme="red" size="sm">
                          응답 지연
                        </Checkbox>
                        <Checkbox value="연결 실패" colorScheme="red" size="sm">
                          연결 실패
                        </Checkbox>
                        <Checkbox value="네트워크 오류" colorScheme="red" size="sm">
                          네트워크 오류
                        </Checkbox>
                        <Checkbox value="알 수 없는 오류" colorScheme="red" size="sm">
                          알 수 없는 오류
                        </Checkbox>
                      </Stack>
                    </Box>

                    {/* 기타 상태 */}
                    <Stack direction="row" spacing={6}>
                      <Checkbox value="checking" colorScheme="blue">
                        <Badge colorScheme="blue" variant="outline" mr={2}>확인중</Badge>
                        헬스체크 진행 중
                      </Checkbox>
                      <Checkbox value="unknown" colorScheme="gray">
                        <Badge colorScheme="gray" variant="outline" mr={2}>미확인</Badge>
                        헬스체크 미실행
                      </Checkbox>
                    </Stack>
                  </VStack>
                </CheckboxGroup>
              </Box>

              {/* 빠른 필터 프리셋 */}
              <Box>
                <Text fontWeight="semibold" mb={2} fontSize="sm">
                  🚀 빠른 필터
                </Text>
                <ButtonGroup size="sm" variant="outline" spacing={2}>
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
                </ButtonGroup>
              </Box>
            </VStack>
          </Box>
        )}

        {/* 하단: 결과 통계 및 활성 필터 태그 */}
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
      </VStack>
    </Box>
  );
};

export default ApiPackageFilters;
