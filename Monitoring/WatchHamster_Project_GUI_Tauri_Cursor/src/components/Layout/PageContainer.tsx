import React from 'react'
import {
  Box,
  Container,
  Heading,
  Text,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Flex,
  useColorModeValue,
} from '@chakra-ui/react'
import { MdChevronRight } from 'react-icons/md'
import { Link as RouterLink } from 'react-router-dom'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)

export interface BreadcrumbItem {
  label: string
  href?: string
  isCurrentPage?: boolean
}

export interface PageContainerProps {
  title: string
  subtitle?: string
  breadcrumbs?: BreadcrumbItem[]
  children: React.ReactNode
  headerContent?: React.ReactNode
  maxWidth?: string
  padding?: number | string
}

/**
 * 페이지 컨테이너 컴포넌트
 * 일관된 페이지 레이아웃과 헤더를 제공
 */
export const PageContainer: React.FC<PageContainerProps> = ({
  title,
  subtitle,
  breadcrumbs,
  children,
  headerContent,
  maxWidth = 'full',
  padding = 6,
}) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  return (
    <MotionBox
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      h="100%"
      overflow="auto"
    >
      <Container maxW={maxWidth} p={padding}>
        {/* 페이지 헤더 */}
        <MotionBox
          bg={bgColor}
          borderRadius="lg"
          border="1px"
          borderColor={borderColor}
          p={6}
          mb={6}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          {/* 브레드크럼 */}
          {breadcrumbs && breadcrumbs.length > 0 && (
            <Breadcrumb
              spacing="8px"
              separator={<MdChevronRight color="gray.500" />}
              mb={4}
              fontSize="sm"
            >
              {breadcrumbs.map((item, index) => (
                <BreadcrumbItem key={index} isCurrentPage={item.isCurrentPage}>
                  {item.href && !item.isCurrentPage ? (
                    <BreadcrumbLink as={RouterLink} to={item.href}>
                      {item.label}
                    </BreadcrumbLink>
                  ) : (
                    <Text color={item.isCurrentPage ? 'posco.500' : 'gray.500'}>
                      {item.label}
                    </Text>
                  )}
                </BreadcrumbItem>
              ))}
            </Breadcrumb>
          )}

          <Flex justify="space-between" align="flex-start">
            <Box flex={1}>
              <Heading
                size="lg"
                color="gray.800"
                _dark={{ color: 'gray.100' }}
                mb={subtitle ? 2 : 0}
              >
                {title}
              </Heading>
              {subtitle && (
                <Text color="gray.600" _dark={{ color: 'gray.400' }} fontSize="md">
                  {subtitle}
                </Text>
              )}
            </Box>

            {headerContent && <Box ml={4}>{headerContent}</Box>}
          </Flex>
        </MotionBox>

        {/* 페이지 콘텐츠 */}
        <MotionBox
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          {children}
        </MotionBox>
      </Container>
    </MotionBox>
  )
}

export default PageContainer