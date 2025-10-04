import React from 'react'
import {
  Progress,
  ProgressProps,
  Box,
  Text,
  Flex,
  useColorModeValue,
} from '@chakra-ui/react'
import { motion } from 'framer-motion'

const MotionProgress = motion(Progress)

export interface ProgressBarProps extends Omit<ProgressProps, 'value'> {
  value: number
  max?: number
  label?: string
  showPercentage?: boolean
  showValue?: boolean
  animated?: boolean
  status?: 'normal' | 'warning' | 'error' | 'success'
}

/**
 * 진행률 표시 컴포넌트
 * 작업 진행률이나 사용률을 시각적으로 표시
 */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  showPercentage = true,
  showValue = false,
  animated = true,
  status = 'normal',
  ...props
}) => {
  const percentage = Math.min((value / max) * 100, 100)
  
  const getColorScheme = () => {
    switch (status) {
      case 'success':
        return 'green'
      case 'warning':
        return 'yellow'
      case 'error':
        return 'red'
      default:
        return 'posco'
    }
  }

  const getStatusColor = () => {
    if (percentage >= 90) return 'red'
    if (percentage >= 70) return 'yellow'
    return 'green'
  }

  const colorScheme = status === 'normal' ? getStatusColor() : getColorScheme()
  const textColor = useColorModeValue('gray.600', 'gray.300')

  return (
    <Box width="100%">
      {(label || showPercentage || showValue) && (
        <Flex justify="space-between" align="center" mb={2}>
          {label && (
            <Text fontSize="sm" fontWeight="medium" color={textColor}>
              {label}
            </Text>
          )}
          <Flex align="center" gap={2}>
            {showValue && (
              <Text fontSize="sm" color={textColor}>
                {value.toLocaleString()}{max !== 100 ? ` / ${max.toLocaleString()}` : ''}
              </Text>
            )}
            {showPercentage && (
              <Text fontSize="sm" fontWeight="semibold" color={textColor}>
                {percentage.toFixed(1)}%
              </Text>
            )}
          </Flex>
        </Flex>
      )}

      <MotionProgress
        value={percentage}
        colorScheme={colorScheme}
        borderRadius="full"
        bg={useColorModeValue('gray.200', 'gray.700')}
        initial={{ width: 0 }}
        animate={{ width: '100%' }}
        transition={{ duration: animated ? 0.5 : 0 }}
        {...props}
      />
    </Box>
  )
}

export default ProgressBar