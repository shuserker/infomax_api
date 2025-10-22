import React from 'react'
import {
  Modal as ChakraModal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  ModalProps as ChakraModalProps,
} from '@chakra-ui/react'

export interface ModalProps extends Omit<ChakraModalProps, 'isOpen' | 'onClose'> {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  footer?: React.ReactNode
  showCloseButton?: boolean
  closeOnOverlayClick?: boolean
  closeOnEsc?: boolean
}

/**
 * 공통 모달 컴포넌트
 * 시스템 전반에서 사용되는 모달 다이얼로그
 */
export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEsc = true,
  size = 'md',
  ...props
}) => {
  return (
    <ChakraModal
      isOpen={isOpen}
      onClose={onClose}
      closeOnOverlayClick={closeOnOverlayClick}
      closeOnEsc={closeOnEsc}
      size={size}
      {...props}
    >
      <ModalOverlay />
      <ModalContent>
        {title && <ModalHeader>{title}</ModalHeader>}
        {showCloseButton && <ModalCloseButton />}
        <ModalBody>{children}</ModalBody>
        {footer && <ModalFooter>{footer}</ModalFooter>}
      </ModalContent>
    </ChakraModal>
  )
}

/**
 * 모달 상태 관리를 위한 커스텀 훅
 */
export const useModal = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()

  return {
    isOpen,
    onOpen,
    onClose,
  }
}

export default Modal
