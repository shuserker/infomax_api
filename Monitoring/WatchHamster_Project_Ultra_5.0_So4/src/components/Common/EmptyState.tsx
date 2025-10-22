import React from 'react'
import { Box, VStack, Text, Button, Icon, useColorModeValue } from '@chakra-ui/react'
import { MdInbox, MdRefresh } from 'react-icons/md'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)
const MotionVStack = motion(VStack)

export interface EmptyStateProps {
  icon?: React.ElementType
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
  children?: React.ReactNode
}

/**
 * 빈 상태 컴포넌트
 * 데이터가 없거나 로딩 실패 시 표시되는 상태
 */
export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = MdInbox,
  title,
  description,
  actionLabel,
  onAction,
  children,
}) => {
  const iconColor = useColorModeValue('gray.400', 'gray.500')
  const titleColor = useColorModeValue('gray.600', 'gray.300')
  const descriptionColor = useColorModeValue('gray.500', 'gray.400')

  return (
    <MotionBox
      display="flex"
      alignItems="center"
      justifyContent="center"
      minHeight="300px"
      width="100%"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <MotionVStack
        spacing={6}
        textAlign="center"
        maxWidth="400px"
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <MotionBox
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Icon as={icon} boxSize={16} color={iconColor} />
        </MotionBox>

        <VStack spacing={2}>
          <Text fontSize="xl" fontWeight="semibold" color={titleColor}>
            {title}
          </Text>
          {description && (
            <Text fontSize="md" color={descriptionColor} lineHeight="1.6">
              {description}
            </Text>
          )}
        </VStack>

        {onAction && actionLabel && (
          <Button
            leftIcon={<MdRefresh />}
            colorScheme="posco"
            variant="outline"
            onClick={onAction}
            size="lg"
          >
            {actionLabel}
          </Button>
        )}

        {children && <Box>{children}</Box>}
      </MotionVStack>
    </MotionBox>
  )
}

export default EmptyState