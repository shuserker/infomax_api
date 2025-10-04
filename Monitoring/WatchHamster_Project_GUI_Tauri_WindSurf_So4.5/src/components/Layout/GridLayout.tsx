import React from 'react'
import { Grid, GridItem, GridProps } from '@chakra-ui/react'
import { motion } from 'framer-motion'

const MotionGrid = motion(Grid)
const MotionGridItem = motion(GridItem)

export interface GridLayoutProps extends GridProps {
  children: React.ReactNode
  columns?: number | { base?: number; md?: number; lg?: number; xl?: number }
  spacing?: number | string
  minChildWidth?: string
  animated?: boolean
}

/**
 * 그리드 레이아웃 컴포넌트
 * 반응형 그리드 레이아웃을 쉽게 구성할 수 있는 컴포넌트
 */
export const GridLayout: React.FC<GridLayoutProps> = ({
  children,
  columns,
  spacing = 6,
  minChildWidth,
  animated = true,
  ...props
}) => {
  const getTemplateColumns = () => {
    if (minChildWidth) {
      return `repeat(auto-fit, minmax(${minChildWidth}, 1fr))`
    }
    
    if (typeof columns === 'number') {
      return `repeat(${columns}, 1fr)`
    }
    
    if (typeof columns === 'object') {
      return {
        base: `repeat(${columns.base || 1}, 1fr)`,
        md: `repeat(${columns.md || columns.base || 2}, 1fr)`,
        lg: `repeat(${columns.lg || columns.md || columns.base || 3}, 1fr)`,
        xl: `repeat(${columns.xl || columns.lg || columns.md || columns.base || 4}, 1fr)`,
      }
    }
    
    return 'repeat(auto-fit, minmax(300px, 1fr))'
  }

  const childrenArray = React.Children.toArray(children)

  return (
    <MotionGrid
      templateColumns={getTemplateColumns()}
      gap={spacing}
      initial={animated ? { opacity: 0 } : {}}
      animate={animated ? { opacity: 1 } : {}}
      transition={animated ? { duration: 0.5 } : {}}
      {...props}
    >
      {childrenArray.map((child, index) => (
        <MotionGridItem
          key={index}
          initial={animated ? { opacity: 0, y: 20 } : {}}
          animate={animated ? { opacity: 1, y: 0 } : {}}
          transition={animated ? { duration: 0.3, delay: index * 0.1 } : {}}
        >
          {child}
        </MotionGridItem>
      ))}
    </MotionGrid>
  )
}

export default GridLayout