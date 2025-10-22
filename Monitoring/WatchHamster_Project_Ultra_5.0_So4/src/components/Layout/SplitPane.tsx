import React, { useState, useCallback } from 'react'
import { Box, Flex, useColorModeValue } from '@chakra-ui/react'
import { motion } from 'framer-motion'

const MotionBox = motion(Box)

export interface SplitPaneProps {
  left: React.ReactNode
  right: React.ReactNode
  defaultSize?: number
  minSize?: number
  maxSize?: number
  disabled?: boolean
  direction?: 'horizontal' | 'vertical'
  onResize?: (size: number) => void
}

/**
 * 분할 패널 컴포넌트
 * 크기 조절 가능한 두 개의 패널로 구성된 레이아웃
 */
export const SplitPane: React.FC<SplitPaneProps> = ({
  left,
  right,
  defaultSize = 50,
  minSize = 20,
  maxSize = 80,
  disabled = false,
  direction = 'horizontal',
  onResize,
}) => {
  const [size, setSize] = useState(defaultSize)
  const [isDragging, setIsDragging] = useState(false)
  
  const resizerBg = useColorModeValue('gray.300', 'gray.600')
  const resizerHoverBg = useColorModeValue('posco.400', 'posco.500')

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (disabled) return
    
    e.preventDefault()
    setIsDragging(true)

    const startPos = direction === 'horizontal' ? e.clientX : e.clientY
    const startSize = size

    const handleMouseMove = (e: MouseEvent) => {
      const currentPos = direction === 'horizontal' ? e.clientX : e.clientY
      const delta = currentPos - startPos
      const containerSize = direction === 'horizontal' 
        ? window.innerWidth 
        : window.innerHeight
      
      const newSize = Math.min(
        Math.max(startSize + (delta / containerSize) * 100, minSize),
        maxSize
      )
      
      setSize(newSize)
      onResize?.(newSize)
    }

    const handleMouseUp = () => {
      setIsDragging(false)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }, [disabled, direction, size, minSize, maxSize, onResize])

  const isHorizontal = direction === 'horizontal'

  return (
    <Flex
      direction={isHorizontal ? 'row' : 'column'}
      h="100%"
      w="100%"
      overflow="hidden"
    >
      {/* 첫 번째 패널 */}
      <MotionBox
        flex={`0 0 ${size}%`}
        overflow="hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {left}
      </MotionBox>

      {/* 리사이저 */}
      {!disabled && (
        <Box
          w={isHorizontal ? '4px' : '100%'}
          h={isHorizontal ? '100%' : '4px'}
          bg={isDragging ? resizerHoverBg : resizerBg}
          cursor={isHorizontal ? 'col-resize' : 'row-resize'}
          _hover={{ bg: resizerHoverBg }}
          onMouseDown={handleMouseDown}
          position="relative"
          zIndex={10}
          transition="background-color 0.2s"
        >
          {/* 리사이저 핸들 */}
          <Box
            position="absolute"
            top="50%"
            left="50%"
            transform="translate(-50%, -50%)"
            w={isHorizontal ? '4px' : '20px'}
            h={isHorizontal ? '20px' : '4px'}
            bg={isDragging ? resizerHoverBg : 'transparent'}
            borderRadius="full"
            transition="background-color 0.2s"
          />
        </Box>
      )}

      {/* 두 번째 패널 */}
      <MotionBox
        flex={`1 1 ${100 - size}%`}
        overflow="hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        {right}
      </MotionBox>
    </Flex>
  )
}

export default SplitPane