import React from 'react'
import {
  useToast,
  UseToastOptions,
  Box,
  Text,
  Icon,
  Flex,
  CloseButton,
  useColorModeValue,
} from '@chakra-ui/react'
import { MdCheckCircle, MdError, MdWarning, MdInfo } from 'react-icons/md'

export type ToastStatus = 'success' | 'error' | 'warning' | 'info'

export interface ToastOptions extends Omit<UseToastOptions, 'status'> {
  status?: ToastStatus
  action?: {
    label: string
    onClick: () => void
  }
}

/**
 * 커스텀 토스트 컴포넌트
 */
const CustomToast: React.FC<{
  title: string
  description?: string
  status: ToastStatus
  onClose: () => void
  action?: { label: string; onClick: () => void }
}> = ({ title, description, status, onClose, action }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const getStatusConfig = () => {
    switch (status) {
      case 'success':
        return { icon: MdCheckCircle, color: 'green.500' }
      case 'error':
        return { icon: MdError, color: 'red.500' }
      case 'warning':
        return { icon: MdWarning, color: 'yellow.500' }
      default:
        return { icon: MdInfo, color: 'blue.500' }
    }
  }

  const config = getStatusConfig()

  return (
    <Box
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="lg"
      p={4}
      boxShadow="lg"
      minW="300px"
      maxW="500px"
    >
      <Flex align="flex-start">
        <Icon as={config.icon} color={config.color} boxSize={5} mt={0.5} mr={3} />
        
        <Box flex={1}>
          <Text fontWeight="semibold" fontSize="sm" mb={description ? 1 : 0}>
            {title}
          </Text>
          {description && (
            <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
              {description}
            </Text>
          )}
          
          {action && (
            <Text
              as="button"
              fontSize="sm"
              color={config.color}
              fontWeight="medium"
              mt={2}
              onClick={action.onClick}
              _hover={{ textDecoration: 'underline' }}
            >
              {action.label}
            </Text>
          )}
        </Box>
        
        <CloseButton size="sm" onClick={onClose} ml={2} />
      </Flex>
    </Box>
  )
}

/**
 * 토스트 알림을 위한 커스텀 훅
 * Chakra UI의 useToast를 래핑하여 일관된 스타일과 기본값 제공
 */
export const useCustomToast = () => {
  const toast = useToast()

  const showToast = (options: ToastOptions) => {
    const { action, ...toastOptions } = options
    
    const defaultOptions: UseToastOptions = {
      duration: 5000,
      isClosable: true,
      position: 'top-right',
      status: 'info',
      ...toastOptions,
      render: ({ onClose }) => (
        <CustomToast
          title={options.title as string}
          description={options.description as string}
          status={options.status || 'info'}
          onClose={onClose}
          action={action}
        />
      ),
    }

    return toast(defaultOptions)
  }

  const showSuccess = (title: string, description?: string, action?: ToastOptions['action']) => {
    return showToast({
      title,
      description,
      status: 'success',
      action,
    })
  }

  const showError = (title: string, description?: string, action?: ToastOptions['action']) => {
    return showToast({
      title,
      description,
      status: 'error',
      duration: 8000, // 에러는 조금 더 오래 표시
      action,
    })
  }

  const showWarning = (title: string, description?: string, action?: ToastOptions['action']) => {
    return showToast({
      title,
      description,
      status: 'warning',
      action,
    })
  }

  const showInfo = (title: string, description?: string, action?: ToastOptions['action']) => {
    return showToast({
      title,
      description,
      status: 'info',
      action,
    })
  }

  const showLoading = (title: string, description?: string) => {
    return showToast({
      title,
      description,
      status: 'info',
      duration: null, // 수동으로 닫을 때까지 표시
    })
  }

  return {
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showLoading,
  }
}

/**
 * 토스트 알림 컴포넌트
 * 시스템 전반에서 사용되는 알림 메시지 표시
 */
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>
}

export default useCustomToast
