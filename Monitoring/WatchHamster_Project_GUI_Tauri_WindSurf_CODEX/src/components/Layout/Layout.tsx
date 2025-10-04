import React from 'react'
import { Box, Flex } from '@chakra-ui/react'
import Sidebar from './Sidebar'
import Header from './Header'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Flex h="100vh" bg="gray.50" _dark={{ bg: 'gray.900' }}>
      {/* 사이드바 */}
      <Sidebar />

      {/* 메인 콘텐츠 영역 */}
      <Flex direction="column" flex="1" overflow="hidden">
        {/* 헤더 */}
        <Header />

        {/* 페이지 콘텐츠 */}
        <Box flex="1" overflow="auto" p={6} bg="gray.50" _dark={{ bg: 'gray.900' }}>
          {children}
        </Box>
      </Flex>
    </Flex>
  )
}

export default Layout
