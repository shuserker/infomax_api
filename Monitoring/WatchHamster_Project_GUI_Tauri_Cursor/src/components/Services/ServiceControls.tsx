import React, { useState } from 'react'
import {
  HStack,
  Button,
  IconButton,
  Tooltip,
  useToast,
  Text,
  VStack,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Progress,
  useColorModeValue,
} from '@chakra-ui/react'
import {
  FaPlay,
  FaStop,
  FaRedo,
} from 'react-icons/fa'
import { ServiceInfo, ServiceAction } from '../../types'
import { Modal, useModal } from '../Common/Modal'

export interface ServiceControlsProps {
  service: ServiceInfo
  onServiceAction: (action: ServiceAction) => Promise<void>
  isLoading?: boolean
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
  variant?: 'buttons' | 'icons'
}

interface ConfirmationState {
  action: ServiceAction['action'] | null
  isProcessing: boolean
}

/**
 * 서비스 제어 컴포넌트
 * 시작/중지/재시작 버튼과 확인 대화상자를 제공
 */
export const ServiceControls: React.FC<ServiceControlsProps> = ({
  service,
  onServiceAction,
  isLoading = false,
  disabled = false,
  size = 'md',
  variant = 'buttons',
}) => {
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useModal()
  const [confirmation, setConfirmation] = useState<ConfirmationState>({
    action: null,
    isProcessing: false,
  })

  // 테마 색상
  const alertBg = useColorModeValue('yellow.50', 'yellow.900')
  const alertBorder = useColorModeValue('yellow.200', 'yellow.700')

  // 액션별 설정
  const getActionConfig = (action: ServiceAction['action']) => {
    const configs = {
      start: {
        label: '시작',
        icon: FaPlay,
        colorScheme: 'green',
        description: '서비스를 시작합니다.',
        confirmTitle: '서비스 시작 확인',
        confirmMessage: `${service.name} 서비스를 시작하시겠습니까?`,
        successMessage: '서비스가 성공적으로 시작되었습니다.',
        errorMessage: '서비스 시작에 실패했습니다.',
      },
      stop: {
        label: '중지',
        icon: FaStop,
        colorScheme: 'red',
        description: '서비스를 중지합니다.',
        confirmTitle: '서비스 중지 확인',
        confirmMessage: `${service.name} 서비스를 중지하시겠습니까?`,
        successMessage: '서비스가 성공적으로 중지되었습니다.',
        errorMessage: '서비스 중지에 실패했습니다.',
      },
      restart: {
        label: '재시작',
        icon: FaRedo,
        colorScheme: 'orange',
        description: '서비스를 재시작합니다.',
        confirmTitle: '서비스 재시작 확인',
        confirmMessage: `${service.name} 서비스를 재시작하시겠습니까?`,
        successMessage: '서비스가 성공적으로 재시작되었습니다.',
        errorMessage: '서비스 재시작에 실패했습니다.',
      },
    }
    return configs[action]
  }

  // 액션 가능 여부 확인
  const isActionAvailable = (action: ServiceAction['action']): boolean => {
    if (disabled || isLoading) return false

    switch (action) {
      case 'start':
        return service.status === 'stopped' || service.status === 'error'
      case 'stop':
        return service.status === 'running'
      case 'restart':
        return service.status === 'running' || service.status === 'error'
      default:
        return false
    }
  }

  // 확인 대화상자 열기
  const handleActionClick = (action: ServiceAction['action']) => {
    setConfirmation({ action, isProcessing: false })
    onOpen()
  }

  // 액션 실행
  const handleConfirmAction = async () => {
    if (!confirmation.action) return

    const config = getActionConfig(confirmation.action)
    setConfirmation(prev => ({ ...prev, isProcessing: true }))

    try {
      await onServiceAction({
        action: confirmation.action,
        service_id: service.id,
      })

      toast({
        title: '성공',
        description: config.successMessage,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })

      onClose()
    } catch (error) {
      console.error('Service action failed:', error)
      toast({
        title: '오류',
        description: config.errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setConfirmation({ action: null, isProcessing: false })
    }
  }

  // 대화상자 닫기
  const handleCloseDialog = () => {
    if (!confirmation.isProcessing) {
      setConfirmation({ action: null, isProcessing: false })
      onClose()
    }
  }

  // 버튼 렌더링
  const renderButton = (action: ServiceAction['action']) => {
    const config = getActionConfig(action)
    const available = isActionAvailable(action)

    if (variant === 'icons') {
      return (
        <Tooltip
          key={action}
          label={available ? config.description : '사용할 수 없음'}
          placement="top"
        >
          <IconButton
            aria-label={config.label}
            icon={<config.icon />}
            colorScheme={config.colorScheme}
            size={size}
            isDisabled={!available}
            isLoading={isLoading}
            onClick={() => handleActionClick(action)}
          />
        </Tooltip>
      )
    }

    return (
      <Button
        key={action}
        leftIcon={<config.icon />}
        colorScheme={config.colorScheme}
        size={size}
        isDisabled={!available}
        isLoading={isLoading}
        onClick={() => handleActionClick(action)}
      >
        {config.label}
      </Button>
    )
  }

  const actions: ServiceAction['action'][] = ['start', 'stop', 'restart']
  const currentConfig = confirmation.action ? getActionConfig(confirmation.action) : null

  return (
    <>
      <HStack spacing={2}>
        {actions.map(renderButton)}
      </HStack>

      {/* 확인 대화상자 */}
      <Modal
        isOpen={isOpen}
        onClose={handleCloseDialog}
        title={currentConfig?.confirmTitle}
        closeOnOverlayClick={!confirmation.isProcessing}
        closeOnEsc={!confirmation.isProcessing}
        size="md"
        footer={
          <HStack spacing={3} width="100%">
            <Button
              variant="ghost"
              onClick={handleCloseDialog}
              isDisabled={confirmation.isProcessing}
              flex={1}
            >
              취소
            </Button>
            <Button
              colorScheme={currentConfig?.colorScheme}
              onClick={handleConfirmAction}
              isLoading={confirmation.isProcessing}
              loadingText="처리 중..."
              flex={1}
            >
              확인
            </Button>
          </HStack>
        }
      >
        <VStack spacing={4} align="stretch">
          {/* 경고 메시지 */}
          <Alert
            status="warning"
            bg={alertBg}
            borderColor={alertBorder}
            borderWidth="1px"
            borderRadius="md"
          >
            <AlertIcon />
            <VStack align="flex-start" spacing={1} flex={1}>
              <AlertTitle fontSize="sm">작업 확인</AlertTitle>
              <AlertDescription fontSize="sm">
                {currentConfig?.confirmMessage}
              </AlertDescription>
            </VStack>
          </Alert>

          {/* 서비스 정보 */}
          <VStack align="flex-start" spacing={2}>
            <Text fontSize="sm" fontWeight="medium">
              서비스 정보:
            </Text>
            <VStack align="flex-start" spacing={1} pl={4}>
              <Text fontSize="sm">
                <strong>이름:</strong> {service.name}
              </Text>
              <Text fontSize="sm">
                <strong>ID:</strong> {service.id}
              </Text>
              <Text fontSize="sm">
                <strong>현재 상태:</strong> {service.status}
              </Text>
              {service.uptime && (
                <Text fontSize="sm">
                  <strong>업타임:</strong> {Math.floor(service.uptime / 60)}분
                </Text>
              )}
            </VStack>
          </VStack>

          {/* 진행 상태 */}
          {confirmation.isProcessing && (
            <VStack spacing={2}>
              <Text fontSize="sm" color="gray.600">
                작업을 처리하고 있습니다...
              </Text>
              <Progress
                size="sm"
                isIndeterminate
                colorScheme={currentConfig?.colorScheme}
                borderRadius="md"
              />
            </VStack>
          )}

          {/* 주의사항 */}
          {confirmation.action === 'stop' && service.status === 'running' && (
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <AlertDescription fontSize="sm">
                서비스를 중지하면 관련된 모든 작업이 중단됩니다.
              </AlertDescription>
            </Alert>
          )}

          {confirmation.action === 'restart' && (
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <AlertDescription fontSize="sm">
                재시작 중에는 서비스가 일시적으로 사용할 수 없습니다.
              </AlertDescription>
            </Alert>
          )}
        </VStack>
      </Modal>
    </>
  )
}

export default ServiceControls