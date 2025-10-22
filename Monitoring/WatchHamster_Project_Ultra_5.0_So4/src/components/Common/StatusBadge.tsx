import React from 'react'
import { Badge, BadgeProps, Icon } from '@chakra-ui/react'
import { MdCheckCircle, MdError, MdWarning, MdInfo, MdPause } from 'react-icons/md'
import { motion } from 'framer-motion'

const MotionBadge = motion(Badge)

export type StatusType = 'success' | 'error' | 'warning' | 'info' | 'neutral' | 'loading'

export interface StatusBadgeProps extends Omit<BadgeProps, 'colorScheme'> {
  status: StatusType
  text?: string
  showIcon?: boolean
  pulse?: boolean
}

/**
 * 상태 배지 컴포넌트
 * 시스템 상태를 시각적으로 표시하는 배지
 */
export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  text,
  showIcon = true,
  pulse = false,
  ...props
}) => {
  const getStatusConfig = (status: StatusType) => {
    switch (status) {
      case 'success':
        return {
          colorScheme: 'green',
          icon: MdCheckCircle,
          defaultText: '정상',
        }
      case 'error':
        return {
          colorScheme: 'red',
          icon: MdError,
          defaultText: '오류',
        }
      case 'warning':
        return {
          colorScheme: 'yellow',
          icon: MdWarning,
          defaultText: '경고',
        }
      case 'info':
        return {
          colorScheme: 'blue',
          icon: MdInfo,
          defaultText: '정보',
        }
      case 'neutral':
        return {
          colorScheme: 'gray',
          icon: MdPause,
          defaultText: '중지',
        }
      case 'loading':
        return {
          colorScheme: 'blue',
          icon: MdInfo,
          defaultText: '로딩',
        }
      default:
        return {
          colorScheme: 'gray',
          icon: MdInfo,
          defaultText: '알 수 없음',
        }
    }
  }

  const config = getStatusConfig(status)
  const displayText = text || config.defaultText

  return (
    <MotionBadge
      colorScheme={config.colorScheme}
      display="flex"
      alignItems="center"
      gap={1}
      animate={pulse ? { scale: [1, 1.05, 1] } : {}}
      transition={pulse ? { duration: 2, repeat: Infinity } : {}}
      {...props}
    >
      {showIcon && <Icon as={config.icon} boxSize={3} />}
      {displayText}
    </MotionBadge>
  )
}

export default StatusBadge