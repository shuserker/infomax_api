import React from 'react'
import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Button,
  useDisclosure,
} from '@chakra-ui/react'

export interface ConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmColorScheme?: string
  isLoading?: boolean
}

/**
 * 확인 대화상자 컴포넌트
 * 중요한 작업 수행 전 사용자 확인을 받는 다이얼로그
 */
export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title = '확인',
  message,
  confirmText = '확인',
  cancelText = '취소',
  confirmColorScheme = 'red',
  isLoading = false,
}) => {
  const cancelRef = React.useRef<HTMLButtonElement>(null)

  const handleConfirm = () => {
    onConfirm()
    onClose()
  }

  return (
    <AlertDialog isOpen={isOpen} leastDestructiveRef={cancelRef} onClose={onClose}>
      <AlertDialogOverlay>
        <AlertDialogContent>
          <AlertDialogHeader fontSize="lg" fontWeight="bold">
            {title}
          </AlertDialogHeader>

          <AlertDialogBody>{message}</AlertDialogBody>

          <AlertDialogFooter>
            <Button ref={cancelRef} onClick={onClose} disabled={isLoading}>
              {cancelText}
            </Button>
            <Button
              colorScheme={confirmColorScheme}
              onClick={handleConfirm}
              ml={3}
              isLoading={isLoading}
              loadingText="처리 중..."
            >
              {confirmText}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  )
}

/**
 * 확인 대화상자 상태 관리를 위한 커스텀 훅
 */
export const useConfirmDialog = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [dialogProps, setDialogProps] = React.useState<Partial<ConfirmDialogProps>>({})

  const openConfirmDialog = (props: Partial<ConfirmDialogProps>) => {
    setDialogProps(props)
    onOpen()
  }

  const closeConfirmDialog = () => {
    onClose()
    setDialogProps({})
  }

  return {
    isOpen,
    onOpen: openConfirmDialog,
    onClose: closeConfirmDialog,
    dialogProps,
  }
}

export default ConfirmDialog
