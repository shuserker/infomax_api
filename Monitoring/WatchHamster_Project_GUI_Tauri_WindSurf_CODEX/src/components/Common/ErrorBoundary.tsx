import React, { Component, ErrorInfo, ReactNode } from 'react'
import {
  Box,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  VStack,
  Text,
  Code,
  Collapse,
  useDisclosure,
} from '@chakra-ui/react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

/**
 * 에러 바운더리 컴포넌트
 * React 컴포넌트 트리에서 발생하는 JavaScript 에러를 포착하고 처리
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({
      error,
      errorInfo,
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onReset={this.handleReset}
        />
      )
    }

    return this.props.children
  }
}

interface ErrorFallbackProps {
  error: Error | null
  errorInfo: ErrorInfo | null
  onReset: () => void
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, errorInfo, onReset }) => {
  const { isOpen, onToggle } = useDisclosure()

  return (
    <Box p={6} maxWidth="600px" mx="auto" mt={8}>
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        <Box>
          <AlertTitle>오류가 발생했습니다!</AlertTitle>
          <AlertDescription>애플리케이션에서 예상치 못한 오류가 발생했습니다.</AlertDescription>
        </Box>
      </Alert>

      <VStack spacing={4} mt={4} align="stretch">
        <Button colorScheme="blue" onClick={onReset}>
          다시 시도
        </Button>

        <Button variant="outline" onClick={onToggle}>
          {isOpen ? '오류 정보 숨기기' : '오류 정보 보기'}
        </Button>

        <Collapse in={isOpen}>
          <Box p={4} bg="gray.50" borderRadius="md">
            {error && (
              <Box mb={4}>
                <Text fontWeight="bold" mb={2}>
                  오류 메시지:
                </Text>
                <Code p={2} display="block" whiteSpace="pre-wrap">
                  {error.message}
                </Code>
              </Box>
            )}

            {error?.stack && (
              <Box mb={4}>
                <Text fontWeight="bold" mb={2}>
                  스택 트레이스:
                </Text>
                <Code p={2} display="block" whiteSpace="pre-wrap" fontSize="xs">
                  {error.stack}
                </Code>
              </Box>
            )}

            {errorInfo?.componentStack && (
              <Box>
                <Text fontWeight="bold" mb={2}>
                  컴포넌트 스택:
                </Text>
                <Code p={2} display="block" whiteSpace="pre-wrap" fontSize="xs">
                  {errorInfo.componentStack}
                </Code>
              </Box>
            )}
          </Box>
        </Collapse>
      </VStack>
    </Box>
  )
}

export default ErrorBoundary
