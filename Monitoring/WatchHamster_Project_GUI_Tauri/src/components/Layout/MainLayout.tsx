import React from 'react'
import { Box, Flex, useColorModeValue } from '@chakra-ui/react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import ErrorBoundary from '../Common/ErrorBoundary'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)

/**
 * 메인 레이아웃 컴포넌트
 * 애플리케이션의 전체 레이아웃 구조를 정의
 */
const MainLayout: React.FC = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900')

  return (
    <ErrorBoundary>
      <Flex h="100vh" overflow="hidden">
        {/* 사이드바 */}
        <MotionBox
          initial={{ x: -250 }}
          animate={{ x: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        >
          <Sidebar />
        </MotionBox>

        {/* 메인 콘텐츠 영역 */}
        <Flex direction="column" flex={1} overflow="hidden">
          {/* 헤더 */}
          <MotionBox
            initial={{ y: -60 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.3, ease: 'easeOut', delay: 0.1 }}
          >
            <Header />
          </MotionBox>

          {/* 페이지 콘텐츠 */}
          <Box flex={1} bg={bgColor} overflow="auto" position="relative">
            <MotionBox
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: 'easeOut', delay: 0.2 }}
              h="100%"
            >
              <ErrorBoundary>
                <Outlet />
              </ErrorBoundary>
            </MotionBox>
          </Box>
        </Flex>
      </Flex>
    </ErrorBoundary>
  )
}

export default MainLayout
