import React from 'react'
import {
  Box,
  Flex,
  Text,
  IconButton,
  useColorMode,
  useColorModeValue,
  Badge,
  HStack,
  Tooltip,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Avatar,
} from '@chakra-ui/react'
import {
  MdLightMode,
  MdDarkMode,
  MdNotifications,
  MdRefresh,
  MdFullscreen,
  MdFullscreenExit,
  MdSettings,
  MdInfo,
} from 'react-icons/md'
import { useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)
const MotionFlex = motion(Flex)

const Header: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode()
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const location = useLocation()
  const [isFullscreen, setIsFullscreen] = React.useState(false)

  // 페이지 제목 매핑
  const getPageTitle = (pathname: string) => {
    switch (pathname) {
      case '/':
        return { title: '대시보드', subtitle: '시스템 전체 상태를 실시간으로 모니터링합니다' }
      case '/services':
        return { title: '서비스 관리', subtitle: 'POSCO 시스템 서비스를 제어하고 관리합니다' }
      case '/logs':
        return { title: '로그 뷰어', subtitle: '실시간 로그를 모니터링하고 분석합니다' }
      case '/settings':
        return { title: '설정', subtitle: '애플리케이션 설정 및 환경을 구성합니다' }
      default:
        return {
          title: '시스템 모니터링',
          subtitle: 'POSCO 시스템 상태를 실시간으로 모니터링합니다',
        }
    }
  }

  const { title, subtitle } = getPageTitle(location.pathname)

  const handleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const handleRefresh = () => {
    window.location.reload()
  }

  return (
    <MotionBox
      bg={bgColor}
      borderBottom="1px"
      borderColor={borderColor}
      px={6}
      py={4}
      boxShadow="sm"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Flex justify="space-between" align="center">
        {/* 페이지 제목 및 브레드크럼 영역 */}
        <MotionBox
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Text fontSize="2xl" fontWeight="bold" color="posco.600" _dark={{ color: 'posco.300' }}>
            {title}
          </Text>
          <Text fontSize="sm" color="gray.500" _dark={{ color: 'gray.400' }} mt={1}>
            {subtitle}
          </Text>
        </MotionBox>

        {/* 우측 액션 버튼들 */}
        <MotionFlex
          align="center"
          spacing={2}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <HStack spacing={2}>
            {/* 새로고침 버튼 */}
            <Tooltip label="새로고침" placement="bottom">
              <IconButton
                aria-label="새로고침"
                icon={<MdRefresh />}
                variant="ghost"
                size="sm"
                colorScheme="gray"
                onClick={handleRefresh}
                _hover={{ transform: 'rotate(180deg)', transition: 'transform 0.3s' }}
              />
            </Tooltip>

            {/* 전체화면 토글 */}
            <Tooltip label={isFullscreen ? '전체화면 해제' : '전체화면'} placement="bottom">
              <IconButton
                aria-label="전체화면"
                icon={isFullscreen ? <MdFullscreenExit /> : <MdFullscreen />}
                variant="ghost"
                size="sm"
                colorScheme="gray"
                onClick={handleFullscreen}
              />
            </Tooltip>

            {/* 알림 메뉴 */}
            <Menu>
              <MenuButton
                as={IconButton}
                aria-label="알림"
                icon={<MdNotifications />}
                variant="ghost"
                size="sm"
                colorScheme="gray"
                position="relative"
              >
                <Badge
                  position="absolute"
                  top="-1"
                  right="-1"
                  colorScheme="red"
                  borderRadius="full"
                  fontSize="xs"
                  minW="16px"
                  h="16px"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  3
                </Badge>
              </MenuButton>
              <MenuList>
                <MenuItem>
                  <Box>
                    <Text fontWeight="semibold">서비스 재시작 완료</Text>
                    <Text fontSize="sm" color="gray.500">
                      POSCO 뉴스 서비스가 재시작되었습니다
                    </Text>
                  </Box>
                </MenuItem>
                <MenuItem>
                  <Box>
                    <Text fontWeight="semibold">메모리 사용량 경고</Text>
                    <Text fontSize="sm" color="gray.500">
                      시스템 메모리 사용량이 80%를 초과했습니다
                    </Text>
                  </Box>
                </MenuItem>
                <MenuItem>
                  <Box>
                    <Text fontWeight="semibold">배포 완료</Text>
                    <Text fontSize="sm" color="gray.500">
                      GitHub Pages 배포가 성공적으로 완료되었습니다
                    </Text>
                  </Box>
                </MenuItem>
                <MenuDivider />
                <MenuItem>
                  <Text fontSize="sm" color="posco.500">
                    모든 알림 보기
                  </Text>
                </MenuItem>
              </MenuList>
            </Menu>

            {/* 다크모드 토글 */}
            <Tooltip label={colorMode === 'light' ? '다크 모드' : '라이트 모드'} placement="bottom">
              <IconButton
                aria-label="테마 변경"
                icon={colorMode === 'light' ? <MdDarkMode /> : <MdLightMode />}
                onClick={toggleColorMode}
                variant="ghost"
                size="sm"
                colorScheme="gray"
              />
            </Tooltip>

            {/* 사용자 메뉴 */}
            <Menu>
              <MenuButton
                as={IconButton}
                aria-label="사용자 메뉴"
                icon={<Avatar size="sm" name="POSCO Admin" bg="posco.500" />}
                variant="ghost"
                size="sm"
                borderRadius="full"
              />
              <MenuList>
                <MenuItem icon={<MdSettings />}>설정</MenuItem>
                <MenuItem icon={<MdInfo />}>정보</MenuItem>
                <MenuDivider />
                <MenuItem>로그아웃</MenuItem>
              </MenuList>
            </Menu>
          </HStack>

          {/* 연결 상태 표시 */}
          <Flex
            align="center"
            ml={4}
            px={3}
            py={1}
            bg="green.50"
            _dark={{ bg: 'green.900' }}
            borderRadius="full"
          >
            <MotionBox
              w={2}
              h={2}
              bg="green.400"
              borderRadius="full"
              mr={2}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <Text
              fontSize="sm"
              color="green.600"
              _dark={{ color: 'green.300' }}
              fontWeight="medium"
            >
              연결됨
            </Text>
          </Flex>
        </MotionFlex>
      </Flex>
    </MotionBox>
  )
}

export default Header
