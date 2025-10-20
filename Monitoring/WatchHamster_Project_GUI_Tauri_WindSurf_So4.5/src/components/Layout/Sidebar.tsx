import React from 'react'
import {
  Box,
  VStack,
  Text,
  Icon,
  Flex,
  useColorModeValue,
  Divider,
  Badge,
  Tooltip,
  IconButton,
  useBreakpointValue,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
} from '@chakra-ui/react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  MdDashboard,
  MdSettings,
  MdList,
  MdDescription,
  MdMonitor,
  MdBusiness,
  MdMenu,
  MdTune,
  MdWebhook,
  MdCorporateFare,
  MdApi,
} from 'react-icons/md'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)
const MotionFlex = motion(Flex)

interface NavItem {
  name: string
  path: string
  icon: React.ElementType
  badge?: string
  tooltip?: string
}

const navItems: NavItem[] = [
  {
    name: '전체 대시보드',
    path: '/',
    icon: MdDashboard,
    tooltip: '모든 회사의 상태를 한눈에 확인',
  },
  {
    name: '회사 관리',
    path: '/companies',
    icon: MdCorporateFare,
    tooltip: '회사 추가, 수정, 삭제 및 관리',
  },
  {
    name: '서비스 관리',
    path: '/services',
    icon: MdList,
    tooltip: '시스템 서비스 제어 및 관리',
  },
  {
    name: 'API 패키지 관리',
    path: '/api-packages',
    icon: MdApi,
    tooltip: 'REST API 패키지 정보 관리 및 문서화',
    badge: 'NEW',
  },
  {
    name: 'API 설정',
    path: '/config',
    icon: MdTune,
    tooltip: 'API 호출 설정 및 웹훅 관리',
  },
  {
    name: '웹훅 관리',
    path: '/webhooks',
    icon: MdWebhook,
    tooltip: '웹훅 발송 관리 및 풀텍스트 로그',
  },
  {
    name: '로그 뷰어',
    path: '/logs',
    icon: MdDescription,
    tooltip: '실시간 로그 모니터링 및 분석',
  },
  {
    name: '설정',
    path: '/settings',
    icon: MdSettings,
    tooltip: '애플리케이션 설정 및 환경 구성',
  },
]

interface SidebarProps {
  onClose?: () => void
}

const SidebarContent: React.FC<SidebarProps> = ({ onClose }) => {
  const location = useLocation()
  const bgColor = useColorModeValue('white', 'gray.800')

  return (
    <Box w="250px" h="100%" bg={bgColor} p={4}>
      {/* 로고 영역 */}
      <MotionFlex
        align="center"
        mb={8}
        px={2}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <MotionBox
          w={10}
          h={10}
          bg="posco.500"
          borderRadius="lg"
          mr={3}
          display="flex"
          alignItems="center"
          justifyContent="center"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          boxShadow="md"
        >
          <Icon as={MdMonitor} color="white" fontSize="xl" />
        </MotionBox>
        <Box>
          <Text fontSize="lg" fontWeight="bold" color="posco.500" lineHeight="1.2">
            WatchHamster
          </Text>
          <Text fontSize="xs" color="gray.500" _dark={{ color: 'gray.400' }}>
            Base: WH v4.5
          </Text>
        </Box>
      </MotionFlex>

      <Divider mb={6} />

      {/* 네비게이션 메뉴 */}
      <VStack spacing={1} align="stretch">
        {navItems.map((item, index) => {
          const isActive = location.pathname === item.path

          return (
            <MotionBox
              key={item.path}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.1 * index }}
            >
              <Tooltip label={item.tooltip} placement="right" hasArrow isDisabled={!item.tooltip}>
                <Box>
                  <NavLink to={item.path} onClick={onClose}>
                    <MotionFlex
                      align="center"
                      p={3}
                      borderRadius="lg"
                      cursor="pointer"
                      bg={isActive ? 'posco.50' : 'transparent'}
                      color={isActive ? 'posco.600' : 'gray.600'}
                      _dark={{
                        bg: isActive ? 'posco.900' : 'transparent',
                        color: isActive ? 'posco.200' : 'gray.300',
                      }}
                      _hover={{
                        bg: isActive ? 'posco.100' : 'gray.50',
                        _dark: {
                          bg: isActive ? 'posco.800' : 'gray.700',
                        },
                        transform: 'translateX(4px)',
                      }}
                      transition="all 0.2s"
                      position="relative"
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {/* 활성 상태 인디케이터 */}
                      {isActive && (
                        <MotionBox
                          position="absolute"
                          left={0}
                          top="50%"
                          w={1}
                          h={6}
                          bg="posco.500"
                          borderRadius="full"
                          initial={{ scaleY: 0 }}
                          animate={{ scaleY: 1 }}
                          style={{ translateY: '-50%' }}
                        />
                      )}

                      <Icon as={item.icon} mr={3} fontSize="lg" />
                      <Text fontWeight={isActive ? 'semibold' : 'medium'} flex={1}>
                        {item.name}
                      </Text>

                      {/* 배지 표시 */}
                      {item.badge && (
                        <Badge
                          colorScheme="red"
                          borderRadius="full"
                          fontSize="xs"
                          minW="18px"
                          h="18px"
                          display="flex"
                          alignItems="center"
                          justifyContent="center"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </MotionFlex>
                  </NavLink>
                </Box>
              </Tooltip>
            </MotionBox>
          )
        })}
      </VStack>

      {/* 하단 정보 */}
      <Box mt="auto" pt={8}>
        <Divider mb={4} />
        <MotionBox
          p={4}
          bg="gray.50"
          borderRadius="lg"
          fontSize="sm"
          border="1px"
          borderColor="gray.200"
          _dark={{ bg: 'gray.700', borderColor: 'gray.600' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <Flex align="center" mb={2}>
            <Icon as={MdBusiness} color="posco.500" mr={2} />
            <Text fontWeight="semibold" color="posco.600" _dark={{ color: 'posco.300' }}>
              POSCO WatchHamster
            </Text>
          </Flex>
          <Text color="gray.500" _dark={{ color: 'gray.400' }} fontSize="xs">
            WatchHamster v4.5 WindSurf Edition
          </Text>
          <Flex align="center" mt={2}>
            <Box w={2} h={2} bg="green.400" borderRadius="full" mr={2} className="pulse" />
            <Text fontSize="xs" color="green.600" _dark={{ color: 'green.300' }}>
              시스템 정상 운영 중
            </Text>
          </Flex>
        </MotionBox>
      </Box>
    </Box>
  )
}

const Sidebar: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const isDesktop = useBreakpointValue({ base: false, lg: true })
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  if (isDesktop) {
    // 데스크톱: 고정 사이드바
    return (
      <Box w="250px" h="100vh" bg={bgColor} borderRight="1px" borderColor={borderColor}>
        <SidebarContent />
      </Box>
    )
  }

  // 모바일: 드로어 사이드바
  return (
    <>
      <IconButton
        aria-label="메뉴 열기"
        icon={<MdMenu />}
        onClick={onOpen}
        position="fixed"
        top={4}
        left={4}
        zIndex={1000}
        size="md"
        colorScheme="posco"
        variant="solid"
        boxShadow="lg"
      />
      
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="sm">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>WatchHamster</DrawerHeader>
          <DrawerBody p={0}>
            <SidebarContent onClose={onClose} />
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  )
}

export default Sidebar
