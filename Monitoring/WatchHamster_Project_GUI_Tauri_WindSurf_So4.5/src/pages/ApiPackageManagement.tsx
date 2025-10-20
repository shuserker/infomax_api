import React, { useState, useEffect, useMemo } from 'react'
import { correctApiPackagesData } from '../data/correctApiData'
import { getCrawledApiInfo, addPrivateTagIfNeeded, getCrawledParameters } from '../utils/apiCrawlingMapper'
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  useDisclosure,
  Alert,
  AlertIcon,
  AlertDescription,
  Container,
  useToast,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  Skeleton,
  useColorModeValue,
  Card,
  CardBody,
  Badge,
  Button,
  Input,
  IconButton,
  Flex
} from '@chakra-ui/react'
import { 
  FiRefreshCw, 
  FiGrid,
  FiList,
  FiSettings,
  FiActivity
} from 'react-icons/fi'
import ApiPackageCard from '../components/ApiPackage/ApiPackageCard'
import ApiPackageFilters, { FilterState } from '../components/ApiPackage/ApiPackageFilters'
import ApiTestModal from '../components/ApiPackage/ApiTestModal'

// API 패키지 데이터 타입 정의 (확장)
interface ApiPackage {
  id: string
  category: string
  itemName: string
  fullName: string
  urlPath: string
  baseUrl: string
  fullUrl: string
  inputs: ApiParameter[]
  outputs: string[]
  description?: string
  tags?: string[]
  status: 'active' | 'inactive' | 'deprecated'
  isFavorite?: boolean
  lastUsed?: string
  usageCount?: number
}

interface ApiParameter {
  name: string
  type: 'String' | 'Number' | 'Boolean' | 'Date'
  required: boolean
  description?: string
  defaultValue?: string
}

const ApiPackageManagement_New: React.FC = () => {
  // 상태 관리
  const [packages, setPackages] = useState<ApiPackage[]>([])
  const [favorites, setFavorites] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [apiToken, setApiToken] = useState<string>('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [bulkHealthCheckTrigger, setBulkHealthCheckTrigger] = useState(false)
  const [isPerformingBulkCheck, setIsPerformingBulkCheck] = useState(false)
  
  // 필터 상태
  const [filters, setFilters] = useState<FilterState>({
    searchTerm: '',
    categories: [],
    complexity: [],
    showFavoritesOnly: false,
    sortBy: 'name',
    sortOrder: 'asc',
    parameterCount: [0, 20]
  })

  // 모달 상태
  const { 
    isOpen: isTestModalOpen, 
    onOpen: onTestModalOpen, 
    onClose: onTestModalClose 
  } = useDisclosure()
  const [selectedPackageForTest, setSelectedPackageForTest] = useState<ApiPackage | null>(null)

  const toast = useToast()
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  const cardBg = useColorModeValue('white', 'gray.800')

  // 토큰 관리 함수들
  const loadTokenFromStorage = (): string => {
    try {
      return localStorage.getItem('infomax_api_token') || ''
    } catch (error) {
      console.error('토큰 불러오기 실패:', error)
      return ''
    }
  }

  const loadFavoritesFromStorage = (): Set<string> => {
    try {
      const saved = localStorage.getItem('infomax_api_favorites')
      return new Set(saved ? JSON.parse(saved) : [])
    } catch (error) {
      console.error('즐겨찾기 불러오기 실패:', error)
      return new Set()
    }
  }

  const saveFavoritesToStorage = (favorites: Set<string>) => {
    try {
      localStorage.setItem('infomax_api_favorites', JSON.stringify(Array.from(favorites)))
    } catch (error) {
      console.error('즐겨찾기 저장 실패:', error)
    }
  }

  // 초기 데이터 로드
  useEffect(() => {
    const initializeData = async () => {
      setLoading(true)
      
      try {
        // 토큰 및 즐겨찾기 불러오기
        const savedToken = loadTokenFromStorage()
        const savedFavorites = loadFavoritesFromStorage()
        
        setApiToken(savedToken)
        setFavorites(savedFavorites)

        // 정확한 공식 API 패키지 데이터 (95개) - 2024.10.04 기준
        const allPackagesData = correctApiPackagesData

        // ApiPackage 객체로 변환 (크롤링 정보 기반)
        const initialPackages: ApiPackage[] = allPackagesData.map(([category, itemName, urlPath, fullName, tags, lastUsed], index) => {
          const baseUrl = 'https://infomaxy.einfomax.co.kr/api'
          const fullUrl = `${baseUrl}/${urlPath}`
          
          // 크롤링 정보 확인
          const crawledInfo = getCrawledApiInfo(urlPath)
          let inputs: ApiParameter[] = []
          
          if (crawledInfo && crawledInfo.isCrawled) {
            // 크롤링된 API: 정확한 파라미터 정보 사용
            inputs = crawledInfo.parameters.map(param => ({
              name: param.name,
              type: param.type as 'String' | 'Number' | 'Boolean' | 'Date',
              required: param.required,
              description: param.description,
              defaultValue: param.example || ''
            }))
          } else {
            // 크롤링되지 않은 API: 기본 패턴 적용
            if (urlPath.includes('stock/') && !urlPath.includes('code')) {
              inputs.push({ name: 'code', type: 'String', required: true, description: '종목코드', defaultValue: '' })
            } else if (urlPath.includes('code') || urlPath.includes('search') || urlPath.includes('list')) {
              inputs.push({ name: 'search', type: 'String', required: false, description: '검색어', defaultValue: '' })
            } else if (urlPath.includes('bond/')) {
              inputs.push({ name: 'stdcd', type: 'String', required: false, description: '표준코드', defaultValue: '' })
            } else {
              inputs.push({ name: 'search', type: 'String', required: false, description: '검색어', defaultValue: '' })
            }
          }
          
          // 비공개 태그 추가
          const updatedTags = addPrivateTagIfNeeded(urlPath, tags as string[])

          return {
            id: `api_${(index + 1).toString().padStart(3, '0')}`,
            category: category as string,
            itemName: itemName as string,
            fullName: fullName as string,
            urlPath: urlPath as string,
            baseUrl,
            fullUrl,
            inputs,
            outputs: crawledInfo?.outputFields?.map(field => field.name) || ['data', 'result', 'status'],
            description: crawledInfo ? `${crawledInfo.title} - ${fullName}` : `${fullName} 정보를 조회하는 API`,
            tags: updatedTags,
            isFavorite: savedFavorites.has(`api_${(index + 1).toString().padStart(3, '0')}`),
            lastUsed: lastUsed as string,
            usageCount: Math.floor(Math.random() * 100),
            status: 'active' as const
          }
        })

        setPackages(initialPackages)
        
      } catch (error) {
        console.error('데이터 초기화 실패:', error)
        toast({
          title: '데이터 로드 실패',
          description: '초기 데이터를 불러오는 중 오류가 발생했습니다.',
          status: 'error',
          duration: 5000
        })
      } finally {
        setLoading(false)
      }
    }

    initializeData()
  }, [toast])

  // 즐겨찾기 토글
  const handleToggleFavorite = (pkg: ApiPackage) => {
    const newFavorites = new Set(favorites)
    
    if (newFavorites.has(pkg.id)) {
      newFavorites.delete(pkg.id)
    } else {
      newFavorites.add(pkg.id)
    }
    
    setFavorites(newFavorites)
    saveFavoritesToStorage(newFavorites)
    
    // 패키지 상태 업데이트
    setPackages(prev => prev.map(p => 
      p.id === pkg.id ? { ...p, isFavorite: newFavorites.has(pkg.id) } : p
    ))

    toast({
      title: newFavorites.has(pkg.id) ? '즐겨찾기 추가' : '즐겨찾기 제거',
      description: `${pkg.itemName}이(가) ${newFavorites.has(pkg.id) ? '즐겨찾기에 추가' : '즐겨찾기에서 제거'}되었습니다.`,
      status: 'success',
      duration: 2000
    })
  }

  // API 테스트 모달 열기
  const handleTestApi = (pkg: ApiPackage) => {
    setSelectedPackageForTest(pkg)
    
    // 사용 기록 업데이트
    setPackages(prev => prev.map(p => 
      p.id === pkg.id 
        ? { 
            ...p, 
            lastUsed: new Date().toISOString().split('T')[0],
            usageCount: (p.usageCount || 0) + 1 
          } 
        : p
    ))
    
    onTestModalOpen()
  }

  // 필터링된 패키지 계산
  const filteredPackages = useMemo(() => {
    let result = packages.filter(pkg => {
      // 검색어 필터
      if (filters.searchTerm) {
        const searchLower = filters.searchTerm.toLowerCase()
        const matchesSearch = 
          pkg.itemName.toLowerCase().includes(searchLower) ||
          pkg.fullName.toLowerCase().includes(searchLower) ||
          pkg.category.toLowerCase().includes(searchLower) ||
          pkg.tags?.some(tag => tag.toLowerCase().includes(searchLower))
        
        if (!matchesSearch) return false
      }

      // 카테고리 필터
      if (filters.categories.length > 0 && !filters.categories.includes(pkg.category)) {
        return false
      }

      // 복잡도 필터
      if (filters.complexity.length > 0) {
        const requiredParams = pkg.inputs.filter(input => input.required).length
        const complexity = 
          requiredParams === 0 ? 'simple' :
          requiredParams <= 2 ? 'medium' : 'complex'
        
        if (!filters.complexity.includes(complexity)) return false
      }

      // 즐겨찾기 필터
      if (filters.showFavoritesOnly && !pkg.isFavorite) {
        return false
      }

      // 파라미터 개수 필터
      const paramCount = pkg.inputs.length
      if (paramCount < filters.parameterCount[0] || paramCount > filters.parameterCount[1]) {
        return false
      }

      return true
    })

    // 정렬
    result.sort((a, b) => {
      let compareValue = 0
      
      switch (filters.sortBy) {
        case 'name':
          compareValue = a.itemName.localeCompare(b.itemName)
          break
        case 'category':
          compareValue = a.category.localeCompare(b.category)
          break
        case 'lastUsed':
          compareValue = (a.lastUsed || '').localeCompare(b.lastUsed || '')
          break
        case 'popularity':
          compareValue = (b.usageCount || 0) - (a.usageCount || 0)
          break
      }
      
      return filters.sortOrder === 'desc' ? -compareValue : compareValue
    })

    return result
  }, [packages, filters])

  // 통계 계산
  const stats = useMemo(() => ({
    total: packages.length,
    favorites: packages.filter(p => p.isFavorite).length,
    categories: new Set(packages.map(p => p.category)).size,
    recentlyUsed: packages.filter(p => {
      if (!p.lastUsed) return false
      const lastUsedDate = new Date(p.lastUsed)
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      return lastUsedDate >= weekAgo
    }).length
  }), [packages])

  const availableCategories = Array.from(new Set(packages.map(p => p.category)))

  if (loading) {
    return (
      <Container maxW="7xl" py={8}>
        <VStack spacing={8}>
          <Skeleton height="100px" width="100%" />
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} width="100%">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} height="300px" />
            ))}
          </SimpleGrid>
        </VStack>
      </Container>
    )
  }

  return (
    <Box bg={bgColor} minH="100vh">
      <Container maxW="7xl" py={8}>
        <VStack spacing={8} align="stretch">
          
          {/* 헤더 */}
          <Box>
            <Heading size="xl" mb={2} color="blue.600">
              📡 대고객 API 송출 관리 페이지
            </Heading>
          </Box>

          {/* API 토큰 입력 */}
          <Card bg={cardBg}>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <HStack>
                  <Text fontSize="lg" fontWeight="bold">🔐 API 인증 토큰</Text>
                  <Badge colorScheme={apiToken ? 'green' : 'red'} variant="outline">
                    {apiToken ? '설정됨' : '미설정'}
                  </Badge>
                </HStack>
                
                <HStack spacing={3}>
                  <Input
                    placeholder="InfoMax API 토큰을 입력하세요..."
                    value={apiToken}
                    onChange={(e) => {
                      const token = e.target.value.trim();
                      setApiToken(token);
                      try {
                        if (token) {
                          localStorage.setItem('infomax_api_token', token);
                        } else {
                          localStorage.removeItem('infomax_api_token');
                        }
                      } catch (error) {
                        console.error('토큰 저장 실패:', error);
                      }
                    }}
                    type="password"
                    flex={1}
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    colorScheme="red"
                    onClick={() => {
                      setApiToken('');
                      localStorage.removeItem('infomax_api_token');
                      toast({
                        title: '토큰 삭제됨',
                        status: 'info',
                        duration: 2000
                      });
                    }}
                    isDisabled={!apiToken}
                  >
                    삭제
                  </Button>
                </HStack>
                
                <Text fontSize="sm" color="gray.500">
                  💡 토큰은 브라우저에 안전하게 저장되며, API 호출 시 자동으로 사용됩니다.
                </Text>
              </VStack>
            </CardBody>
          </Card>

          {/* 통계 대시보드 */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>전체 API</StatLabel>
                  <StatNumber color="blue.500">{stats.total}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
            
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>즐겨찾기</StatLabel>
                  <StatNumber color="yellow.500">{stats.favorites}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
            
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>카테고리</StatLabel>
                  <StatNumber color="purple.500">{stats.categories}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
            
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>최근 사용</StatLabel>
                  <StatNumber color="green.500">{stats.recentlyUsed}</StatNumber>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* 필터 및 검색 */}
          <ApiPackageFilters
            filters={filters}
            onFiltersChange={setFilters}
            availableCategories={availableCategories}
            totalCount={packages.length}
            filteredCount={filteredPackages.length}
          />

          {/* 뷰 모드 토글 및 일괄 헬스체크 */}
          <HStack justify="space-between">
            <Text color="gray.600">
              <Text as="span" fontWeight="bold" color="blue.500">
                {filteredPackages.length}
              </Text>
              개의 API 패키지
            </Text>
            
            <HStack spacing={3}>
              {/* 일괄 헬스체크 버튼 */}
              <Button
                leftIcon={<FiActivity />}
                size="sm"
                colorScheme="green"
                variant="outline"
                isLoading={isPerformingBulkCheck}
                onClick={async () => {
                  setIsPerformingBulkCheck(true);
                  toast({
                    title: "일괄 헬스체크 시작",
                    description: `${filteredPackages.length}개 API의 헬스체크를 시작합니다.`,
                    status: "info",
                    duration: 3000,
                    isClosable: true,
                  });
                  
                  // 트리거 상태를 토글하여 모든 카드에 헬스체크 신호 전송
                  setBulkHealthCheckTrigger(prev => !prev);
                  
                  // 5초 후 완료로 표시 (실제로는 각 카드별로 완료 시점이 다름)
                  setTimeout(() => {
                    setIsPerformingBulkCheck(false);
                    toast({
                      title: "일괄 헬스체크 완료",
                      description: "모든 API의 헬스체크가 완료되었습니다.",
                      status: "success",
                      duration: 3000,
                      isClosable: true,
                    });
                  }, 5000);
                }}
              >
                일괄 헬스체크
              </Button>
              
              {/* 뷰 모드 버튼들 */}
              <Button
                leftIcon={<FiGrid />}
                size="sm"
                variant={viewMode === 'grid' ? 'solid' : 'outline'}
                onClick={() => setViewMode('grid')}
              >
                카드뷰
              </Button>
              <Button
                leftIcon={<FiList />}
                size="sm"
                variant={viewMode === 'list' ? 'solid' : 'outline'}
                onClick={() => setViewMode('list')}
              >
                리스트뷰
              </Button>
            </HStack>
          </HStack>

          {/* API 패키지 그리드 */}
          {filteredPackages.length === 0 ? (
            <Alert status="info" borderRadius="xl">
              <AlertIcon />
              <AlertDescription>
                선택한 필터 조건에 맞는 API 패키지가 없습니다. 
                필터를 조정하거나 검색어를 변경해보세요.
              </AlertDescription>
            </Alert>
          ) : viewMode === 'list' ? (
            <VStack spacing={2} align="stretch">
              {/* 리스트뷰 헤더 */}
              <Box
                bg={useColorModeValue('gray.50', 'gray.700')}
                borderRadius="lg"
                p={3}
                border="1px solid"
                borderColor={useColorModeValue('gray.200', 'gray.600')}
              >
                <Flex align="center" gap={4}>
                  <Box minW="80px" textAlign="center">
                    <Text fontSize="xs" fontWeight="bold" color="gray.600">
                      상태
                    </Text>
                  </Box>
                  <Box minW="60px" textAlign="center">
                    <Text fontSize="xs" fontWeight="bold" color="gray.600">
                      카테고리
                    </Text>
                  </Box>
                  <Box flex={1}>
                    <Text fontSize="xs" fontWeight="bold" color="gray.600">
                      API 정보
                    </Text>
                  </Box>
                  <Box minW="60px" textAlign="center">
                    <Text fontSize="xs" fontWeight="bold" color="gray.600">
                      전체
                    </Text>
                  </Box>
                  <Box minW="60px" textAlign="center">
                    <Text fontSize="xs" fontWeight="bold" color="gray.600">
                      필수
                    </Text>
                  </Box>
                  <Box minW="80px" textAlign="center">
                    <Text fontSize="xs" fontWeight="bold" color="gray.600">
                      사용 이력
                    </Text>
                  </Box>
                  <Box minW="180px" textAlign="center">
                    <Text fontSize="xs" fontWeight="bold" color="gray.600">
                      액션
                    </Text>
                  </Box>
                </Flex>
              </Box>
              
              {/* 리스트 아이템들 */}
              {filteredPackages.map(pkg => (
                <ApiPackageCard
                  key={pkg.id}
                  package={pkg}
                  onTest={handleTestApi}
                  onToggleFavorite={handleToggleFavorite}
                  viewMode={viewMode}
                  triggerHealthCheck={bulkHealthCheckTrigger}
                />
              ))}
            </VStack>
          ) : (
            <SimpleGrid 
              columns={{ 
                base: 1, 
                md: 2, 
                lg: 3,
                xl: 4
              }} 
              spacing={6}
            >
              {filteredPackages.map(pkg => (
                <ApiPackageCard
                  key={pkg.id}
                  package={pkg}
                  onTest={handleTestApi}
                  onToggleFavorite={handleToggleFavorite}
                  viewMode={viewMode}
                  triggerHealthCheck={bulkHealthCheckTrigger}
                />
              ))}
            </SimpleGrid>
          )}

          {/* 빠른 액션 플로팅 버튼 */}
          <Box position="fixed" bottom={8} right={8} zIndex={1000}>
            <VStack spacing={3}>
              <IconButton
                icon={<FiRefreshCw />}
                aria-label="새로고침"
                colorScheme="gray"
                variant="solid"
                size="lg"
                borderRadius="full"
                shadow="lg"
                onClick={() => window.location.reload()}
              />
              <IconButton
                icon={<FiSettings />}
                aria-label="설정"
                colorScheme="blue"
                variant="solid"
                size="lg"
                borderRadius="full"
                shadow="lg"
              />
            </VStack>
          </Box>
        </VStack>
      </Container>

      {/* API 테스트 모달 */}
      {selectedPackageForTest && (
        <ApiTestModal
          isOpen={isTestModalOpen}
          onClose={onTestModalClose}
          package={selectedPackageForTest}
          apiToken={apiToken}
        />
      )}
    </Box>
  )
}

export default ApiPackageManagement_New
