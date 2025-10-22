import React from 'react'
import { Spinner, Box, Text, VStack, useColorModeValue, Progress } from '@chakra-ui/react'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)
const MotionVStack = motion(VStack)

export interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  message?: string
  color?: string
  variant?: 'spinner' | 'dots' | 'pulse' | 'progress'
  progress?: number
  overlay?: boolean
  fullScreen?: boolean
}

/**
 * 로딩 스피너 컴포넌트
 * 시스템 전반에서 사용되는 공통 로딩 인디케이터
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message = '로딩 중...',
  color = 'posco.500',
  variant = 'spinner',
  progress,
  overlay = false,
  fullScreen = false,
}) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const textColor = useColorModeValue('gray.600', 'gray.300')
  const overlayBg = useColorModeValue('rgba(255, 255, 255, 0.9)', 'rgba(0, 0, 0, 0.9)')

  const renderLoadingIndicator = () => {
    switch (variant) {
      case 'dots':
        return (
          <MotionBox display="flex" gap={2}>
            {[0, 1, 2].map((i) => (
              <MotionBox
                key={i}
                w={3}
                h={3}
                bg={color}
                borderRadius="full"
                animate={{ y: [0, -10, 0] }}
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  delay: i * 0.2,
                }}
              />
            ))}
          </MotionBox>
        )
      
      case 'pulse':
        return (
          <MotionBox
            w={12}
            h={12}
            bg={color}
            borderRadius="full"
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )
      
      case 'progress':
        return (
          <Box w="200px">
            <Progress
              value={progress || 0}
              colorScheme="posco"
              borderRadius="full"
              isIndeterminate={progress === undefined}
            />
            {progress !== undefined && (
              <Text fontSize="sm" textAlign="center" mt={2} color={textColor}>
                {Math.round(progress)}%
              </Text>
            )}
          </Box>
        )
      
      default:
        return (
          <Spinner
            thickness="4px"
            speed="0.65s"
            emptyColor="gray.200"
            color={color}
            size={size}
          />
        )
    }
  }

  const content = (
    <MotionVStack
      spacing={4}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {renderLoadingIndicator()}
      {message && (
        <Text fontSize="sm" color={textColor} textAlign="center" maxW="300px">
          {message}
        </Text>
      )}
    </MotionVStack>
  )

  if (overlay || fullScreen) {
    return (
      <MotionBox
        position={fullScreen ? 'fixed' : 'absolute'}
        top={0}
        left={0}
        right={0}
        bottom={0}
        bg={overlayBg}
        display="flex"
        alignItems="center"
        justifyContent="center"
        zIndex={9999}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.2 }}
      >
        <Box
          bg={bgColor}
          p={8}
          borderRadius="lg"
          boxShadow="xl"
          border="1px"
          borderColor="gray.200"
          _dark={{ borderColor: 'gray.700' }}
        >
          {content}
        </Box>
      </MotionBox>
    )
  }

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="200px"
      width="100%"
    >
      {content}
    </Box>
  )
}

export default LoadingSpinner
