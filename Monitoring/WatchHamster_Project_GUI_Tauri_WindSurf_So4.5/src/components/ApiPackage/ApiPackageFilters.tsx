import React, { useState } from 'react';
import {
  Box,
  HStack,
  VStack,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Button,
  ButtonGroup,
  Badge,
  Wrap,
  WrapItem,
  Menu,
  MenuButton,
  MenuList,
  MenuOptionGroup,
  MenuItemOption,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverBody,
  PopoverArrow,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
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
  FiTrendingUp,
  FiSettings
} from 'react-icons/fi';

export interface FilterState {
  searchTerm: string;
  categories: string[];
  complexity: string[];
  showFavoritesOnly: boolean;
  sortBy: 'name' | 'category' | 'lastUsed' | 'popularity';
  sortOrder: 'asc' | 'desc';
  parameterCount: [number, number];
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
      complexity: [],
      showFavoritesOnly: false,
      sortBy: 'name',
      sortOrder: 'asc',
      parameterCount: [0, 20]
    });
  };

  const activeFilterCount = 
    (filters.categories.length > 0 ? 1 : 0) +
    (filters.complexity.length > 0 ? 1 : 0) +
    (filters.showFavoritesOnly ? 1 : 0) +
    (filters.searchTerm.length > 0 ? 1 : 0) +
    (filters.parameterCount[0] > 0 || filters.parameterCount[1] < 20 ? 1 : 0);

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

              {/* 복잡도 필터 */}
              <Box>
                <Text fontWeight="semibold" mb={2} fontSize="sm">
                  🎯 복잡도
                </Text>
                <CheckboxGroup
                  value={filters.complexity}
                  onChange={(values) => updateFilters({ complexity: values as string[] })}
                >
                  <Stack direction="row" spacing={6}>
                    <Checkbox value="simple" colorScheme="green">
                      <Badge colorScheme="green" variant="outline" mr={2}>간단</Badge>
                      필수 파라미터 없음
                    </Checkbox>
                    <Checkbox value="medium" colorScheme="yellow">
                      <Badge colorScheme="yellow" variant="outline" mr={2}>보통</Badge>
                      필수 파라미터 1-2개
                    </Checkbox>
                    <Checkbox value="complex" colorScheme="red">
                      <Badge colorScheme="red" variant="outline" mr={2}>복잡</Badge>
                      필수 파라미터 3개 이상
                    </Checkbox>
                  </Stack>
                </CheckboxGroup>
              </Box>

              {/* 파라미터 개수 범위 */}
              <Box>
                <HStack justify="space-between" mb={2}>
                  <Text fontWeight="semibold" fontSize="sm">
                    📋 파라미터 개수
                  </Text>
                  <Text fontSize="sm" color="gray.500">
                    {filters.parameterCount[0]} - {filters.parameterCount[1]}개
                  </Text>
                </HStack>
                <Slider
                  min={0}
                  max={20}
                  step={1}
                  value={filters.parameterCount}
                  onChange={(value) => updateFilters({ parameterCount: value as [number, number] })}
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb boxSize={4} index={0} />
                  <SliderThumb boxSize={4} index={1} />
                </Slider>
                <HStack justify="space-between" mt={1}>
                  <Text fontSize="xs" color="gray.400">0개</Text>
                  <Text fontSize="xs" color="gray.400">20개+</Text>
                </HStack>
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
                    onClick={() => updateFilters({ complexity: ['simple'] })}
                    colorScheme="green"
                  >
                    간단한 API만
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
            
            {filters.complexity.map(complexity => (
              <WrapItem key={complexity}>
                <Badge
                  colorScheme={
                    complexity === 'simple' ? 'green' :
                    complexity === 'medium' ? 'yellow' : 'red'
                  }
                  variant="solid"
                  cursor="pointer"
                  onClick={() => updateFilters({ 
                    complexity: filters.complexity.filter(c => c !== complexity) 
                  })}
                  _hover={{ opacity: 0.8 }}
                >
                  {complexity === 'simple' ? '간단' :
                   complexity === 'medium' ? '보통' : '복잡'} ✕
                </Badge>
              </WrapItem>
            ))}
            
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
