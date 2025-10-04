/**
 * 로딩 상태 및 에러 상태 UI 컴포넌트
 */

import React from 'react'
import {
  Box,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  VStack,
  HStack,
  Text,
  Progress,
  Skeleton,
  SkeletonText,
  useColorModeValue,
  Flex,
  Icon,
  CircularProgress,
  CircularProgressLabel
} from '@chakra-ui/react'
import { FiRefreshCw, FiAlertTriangle, FiWifiOff } from 'react-icons/fi'

// 로딩 상태 타입
export interface LoadingState {
  isLoading: boolean
  progress?: number
  message?: string
  type?: 'spinner' | 'progress' | 'skeleton' | 'circular'
}

// 에러 상태 타입
export interface ErrorState {
  hasError: boolean
  error?: Error | string
  title?: string
  description?: string
  canRetry?: boolean
  onRetry?: () => void
  type?: 'network' | 'server' | 'client' | 'unknown'
}

// 기본 로딩 스피너
export const LoadingSpinner: React.FC<{
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  message?: string
  color?: string
}> = ({ size = 'md', message, color }) => {
  return (
    <VStack spacing={4} py={8}>
      <Spinner
        size={size}
        color={color || 'blue.500'}
        thickness="4px"
        speed="0.65s"
        emptyColor="gray.200"
      />
      {message && (
        <Text fontSize="sm" color="gray.600">
          {message}
        </Text>
      )}
    </VStack>
  )
}

// 진행률 표시 로딩
export const ProgressLoading: React.FC<{
  progress: number
  message?: string
  showPercentage?: boolean
}> = ({ progress, message, showPercentage = true }) => {
  return (
    <VStack spacing={4} py={8} px={4}>
      <Progress
        value={progress}
        size="lg"
        colorScheme="blue"
        width="100%"
        borderRadius="md"
        hasStripe
        isAnimated
      />
      <HStack justify="space-between" width="100%">
        {message && (
          <Text fontSize="sm" color="gray.600">
            {message}
          </Text>
        )}
        {showPercentage && (
          <Text fontSize="sm" fontWeight="bold" color="blue.600">
            {Math.round(progress)}%
          </Text>
        )}
      </HStack>
    </VStack>
  )
}

// 원형 진행률 로딩
export const CircularLoading: React.FC<{
  progress?: number
  size?: string
  message?: string
  isIndeterminate?: boolean
}> = ({ progress, size = '60px', message, isIndeterminate = false }) => {
  return (
    <VStack spacing={4} py={8}>
      <CircularProgress
        value={progress}
        size={size}
        color="blue.400"
        isIndeterminate={isIndeterminate}
      >
        {progress !== undefined && (
          <CircularProgressLabel>{Math.round(progress)}%</CircularProgressLabel>
        )}
      </CircularProgress>
      {message && (
        <Text fontSize="sm" color="gray.600" textAlign="center">
          {message}
        </Text>
      )}
    </VStack>
  )
}

// 스켈레톤 로딩
export const SkeletonLoading: React.FC<{
  lines?: number
  height?: string
  spacing?: number
}> = ({ lines = 3, height = '20px', spacing = 4 }) => {
  return (
    <VStack spacing={spacing} py={4}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton key={index} height={height} width="100%" />
      ))}
    </VStack>
  )
}

// 카드 스켈레톤 로딩
export const CardSkeletonLoading: React.FC<{
  count?: number
  hasAvatar?: boolean
}> = ({ count = 1, hasAvatar = false }) => {
  return (
    <VStack spacing={4}>
      {Array.from({ length: count }).map((_, index) => (
        <Box key={index} p={4} borderWidth="1px" borderRadius="md" width="100%">
          <HStack spacing={4}>
            {hasAvatar && <Skeleton height="40px" width="40px" borderRadius="full" />}
            <VStack align="start" flex={1} spacing={2}>
              <Skeleton height="20px" width="60%" />
              <SkeletonText noOfLines={2} spacing="2" />
            </VStack>
          </HStack>
        </Box>
      ))}
    </VStack>
  )
}

// 통합 로딩 컴포넌트
export const LoadingComponent: React.FC<LoadingState> = ({
  isLoading,
  progress,
  message,
  type = 'spinner'
}) => {
  if (!isLoading) return null

  switch (type) {
    case 'progress':
      return <ProgressLoading progress={progress || 0} message={message} />
    case 'circular':
      return <CircularLoading progress={progress} message={message} />
    case 'skeleton':
      return <SkeletonLoading />
    default:
      return <LoadingSpinner message={message} />
  }
}

// 에러 아이콘 매핑
const getErrorIcon = (type: ErrorState['type']) => {
  switch (type) {
    case 'network':
      return FiWifiOff
    case 'server':
      return FiAlertTriangle
    default:
      return FiAlertTriangle
  }
}

// 에러 상태 컴포넌트
export const ErrorComponent: React.FC<ErrorState> = ({
  hasError,
  error,
  title,
  description,
  canRetry = true,
  onRetry,
  type = 'unknown'
}) => {
  const bgColor = useColorModeValue('red.50', 'red.900')
  const borderColor = useColorModeValue('red.200', 'red.700')

  if (!hasError) return null

  const errorMessage = typeof error === 'string' ? error : error?.message
  const ErrorIcon = getErrorIcon(type)

  return (
    <Alert
      status="error"
      variant="subtle"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      textAlign="center"
      height="200px"
      bg={bgColor}
      borderColor={borderColor}
      borderWidth="1px"
      borderRadius="md"
    >
      <Icon as={ErrorIcon} boxSize="40px" color="red.500" mb={4} />
      
      <AlertTitle mt={4} mb={1} fontSize="lg">
        {title || '오류가 발생했습니다'}
      </AlertTitle>
      
      <AlertDescription maxWidth="sm" mb={4}>
        {description || errorMessage || '알 수 없는 오류가 발생했습니다.'}
      </AlertDescription>

      {canRetry && onRetry && (
        <Button
          leftIcon={<FiRefreshCw />}
          colorScheme="red"
          variant="outline"
          onClick={onRetry}
          size="sm"
        >
          다시 시도
        </Button>
      )}
    </Alert>
  )
}

// 네트워크 상태 표시 컴포넌트
export const NetworkStatus: React.FC<{
  isOnline: boolean
  onReconnect?: () => void
}> = ({ isOnline, onReconnect }) => {
  if (isOnline) return null

  return (
    <Alert status="warning" variant="solid">
      <AlertIcon as={FiWifiOff} />
      <Box flex="1">
        <AlertTitle>네트워크 연결 끊김</AlertTitle>
        <AlertDescription display="block">
          인터넷 연결을 확인해주세요.
        </AlertDescription>
      </Box>
      {onReconnect && (
        <Button size="sm" variant="outline" onClick={onReconnect}>
          재연결
        </Button>
      )}
    </Alert>
  )
}

// 빈 상태 컴포넌트
export const EmptyState: React.FC<{
  title: string
  description?: string
  icon?: React.ComponentType
  action?: {
    label: string
    onClick: () => void
  }
}> = ({ title, description, icon: IconComponent, action }) => {
  return (
    <VStack spacing={4} py={12} textAlign="center">
      {IconComponent && (
        <Icon as={IconComponent} boxSize="48px" color="gray.400" />
      )}
      <VStack spacing={2}>
        <Text fontSize="lg" fontWeight="semibold" color="gray.600">
          {title}
        </Text>
        {description && (
          <Text fontSize="sm" color="gray.500" maxWidth="md">
            {description}
          </Text>
        )}
      </VStack>
      {action && (
        <Button colorScheme="blue" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </VStack>
  )
}

// 상태별 래퍼 컴포넌트
export const StateWrapper: React.FC<{
  loading?: LoadingState
  error?: ErrorState
  isEmpty?: boolean
  emptyState?: {
    title: string
    description?: string
    icon?: React.ComponentType
    action?: { label: string; onClick: () => void }
  }
  children: React.ReactNode
}> = ({ loading, error, isEmpty, emptyState, children }) => {
  // 로딩 상태
  if (loading?.isLoading) {
    return <LoadingComponent {...loading} />
  }

  // 에러 상태
  if (error?.hasError) {
    return <ErrorComponent {...error} />
  }

  // 빈 상태
  if (isEmpty && emptyState) {
    return <EmptyState {...emptyState} />
  }

  // 정상 상태
  return <>{children}</>
}

// 지연 로딩 래퍼
export const DelayedLoading: React.FC<{
  delay?: number
  children: React.ReactNode
}> = ({ delay = 200, children }) => {
  const [showLoading, setShowLoading] = React.useState(false)

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setShowLoading(true)
    }, delay)

    return () => clearTimeout(timer)
  }, [delay])

  if (!showLoading) return null

  return <>{children}</>
}

// 인라인 로딩 컴포넌트
export const InlineLoading: React.FC<{
  isLoading: boolean
  size?: 'xs' | 'sm' | 'md'
  text?: string
}> = ({ isLoading, size = 'sm', text }) => {
  if (!isLoading) return null

  return (
    <HStack spacing={2}>
      <Spinner size={size} />
      {text && <Text fontSize="sm">{text}</Text>}
    </HStack>
  )
}

// 버튼 로딩 상태
export const LoadingButton: React.FC<{
  isLoading: boolean
  loadingText?: string
  children: React.ReactNode
  [key: string]: any
}> = ({ isLoading, loadingText, children, ...props }) => {
  return (
    <Button
      isLoading={isLoading}
      loadingText={loadingText}
      spinner={<Spinner size="sm" />}
      {...props}
    >
      {children}
    </Button>
  )
}

// 페이지 로딩 오버레이
export const PageLoadingOverlay: React.FC<{
  isLoading: boolean
  message?: string
}> = ({ isLoading, message }) => {
  if (!isLoading) return null

  return (
    <Flex
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      bg="blackAlpha.600"
      zIndex={9999}
      align="center"
      justify="center"
    >
      <VStack
        bg="white"
        p={8}
        borderRadius="md"
        boxShadow="xl"
        spacing={4}
      >
        <Spinner size="xl" color="blue.500" thickness="4px" />
        {message && (
          <Text fontSize="lg" fontWeight="medium">
            {message}
          </Text>
        )}
      </VStack>
    </Flex>
  )
}