import React from 'react'
import {
  Box,
  BoxProps,
  useColorModeValue,
  Heading,
  Text,
  Flex,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react'
import { MdMoreVert } from 'react-icons/md'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)

export interface CardAction {
  label: string
  onClick: () => void
  icon?: React.ElementType
  colorScheme?: string
}

export interface CardProps extends Omit<BoxProps, 'title'> {
  title?: string
  subtitle?: string
  children: React.ReactNode
  actions?: CardAction[]
  headerContent?: React.ReactNode
  isLoading?: boolean
  hover?: boolean
}

/**
 * 공통 카드 컴포넌트
 * 콘텐츠를 카드 형태로 감싸는 컨테이너
 */
export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  actions,
  headerContent,
  isLoading = false,
  hover = true,
  ...props
}) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const shadowColor = useColorModeValue('rgba(0, 0, 0, 0.1)', 'rgba(0, 0, 0, 0.3)')

  return (
    <MotionBox
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="lg"
      p={6}
      boxShadow={`0 2px 8px ${shadowColor}`}
      position="relative"
      overflow="hidden"
      whileHover={hover ? { y: -2, boxShadow: `0 4px 16px ${shadowColor}` } : {}}
      transition={{ duration: 0.2 }}
      {...props}
    >
      {/* 로딩 오버레이 */}
      {isLoading && (
        <Box
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bg="rgba(255, 255, 255, 0.8)"
          _dark={{ bg: 'rgba(0, 0, 0, 0.8)' }}
          display="flex"
          alignItems="center"
          justifyContent="center"
          zIndex={10}
        >
          <Text>로딩 중...</Text>
        </Box>
      )}

      {/* 헤더 영역 */}
      {(title || subtitle || actions || headerContent) && (
        <Flex justify="space-between" align="flex-start" mb={4}>
          <Box flex={1}>
            {title && (
              <Heading size="md" mb={1} color="gray.800" _dark={{ color: 'gray.100' }}>
                {title}
              </Heading>
            )}
            {subtitle && (
              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                {subtitle}
              </Text>
            )}
            {headerContent && <Box mt={2}>{headerContent}</Box>}
          </Box>

          {/* 액션 메뉴 */}
          {actions && actions.length > 0 && (
            <Menu>
              <MenuButton
                as={IconButton}
                aria-label="카드 액션"
                icon={<MdMoreVert />}
                variant="ghost"
                size="sm"
                ml={2}
              />
              <MenuList>
                {actions.map((action, index) => (
                  <MenuItem
                    key={index}
                    onClick={action.onClick}
                    icon={action.icon ? <action.icon /> : undefined}
                  >
                    {action.label}
                  </MenuItem>
                ))}
              </MenuList>
            </Menu>
          )}
        </Flex>
      )}

      {/* 콘텐츠 영역 */}
      <Box>{children}</Box>
    </MotionBox>
  )
}

export default Card