import React from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Badge,
  VStack,
  HStack,
  Box,
  Icon,
  Tooltip,
  Skeleton,
  Alert,
  AlertIcon,
  Button,
  useToast,
} from '@chakra-ui/react'
import { 
  FiGitBranch, 
  FiGitCommit, 
  FiAlertTriangle, 
  FiCheck, 
  FiArrowUp, 
  FiArrowDown,
  FiRefreshCw
} from 'react-icons/fi'

interface GitStatus {
  branch: string
  lastCommit: string
  hasUncommittedChanges: boolean
  hasConflicts: boolean
  remoteStatus: 'up-to-date' | 'ahead' | 'behind' | 'diverged'
  commitHash?: string
  commitMessage?: string
  commitAuthor?: string
  commitDate?: string
  aheadCount?: number
  behindCount?: number
}

interface GitStatusWidgetProps {
  gitStatus?: GitStatus
  isLoading?: boolean
  error?: string
  onRefresh?: () => void
}

const getRemoteStatusColor = (status: string) => {
  switch (status) {
    case 'up-to-date':
      return 'green'
    case 'ahead':
      return 'blue'
    case 'behind':
      return 'orange'
    case 'diverged':
      return 'red'
    default:
      return 'gray'
  }
}

const getRemoteStatusText = (status: string) => {
  switch (status) {
    case 'up-to-date':
      return '최신 상태'
    case 'ahead':
      return '앞서 있음'
    case 'behind':
      return '뒤처져 있음'
    case 'diverged':
      return '분기됨'
    default:
      return '알 수 없음'
  }
}

const getRemoteStatusIcon = (status: string) => {
  switch (status) {
    case 'up-to-date':
      return FiCheck
    case 'ahead':
      return FiArrowUp
    case 'behind':
      return FiArrowDown
    case 'diverged':
      return FiAlertTriangle
    default:
      return FiGitBranch
  }
}

const formatCommitHash = (hash: string) => {
  return hash.slice(0, 7)
}

const formatCommitDate = (dateString: string) => {
  try {
    const date = new Date(dateString)
    return date.toLocaleString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

const GitStatusWidget: React.FC<GitStatusWidgetProps> = ({
  gitStatus,
  isLoading = false,
  error,
  onRefresh
}) => {
  const toast = useToast()

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh()
      toast({
        title: 'Git 상태 새로고침',
        description: 'Git 상태 정보를 업데이트했습니다.',
        status: 'info',
        duration: 2000,
        isClosable: true,
      })
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Skeleton height="20px" width="100px" />
            <Skeleton height="20px" width="60px" />
          </HStack>
        </CardHeader>
        <CardBody>
          <VStack align="stretch" spacing={3}>
            <Skeleton height="16px" width="80%" />
            <Skeleton height="16px" width="60%" />
            <Skeleton height="16px" width="90%" />
          </VStack>
        </CardBody>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiGitBranch} boxSize={5} />
              <Heading size="sm">Git 상태</Heading>
            </HStack>
            {onRefresh && (
              <Button size="xs" variant="ghost" onClick={handleRefresh}>
                <Icon as={FiRefreshCw} />
              </Button>
            )}
          </HStack>
        </CardHeader>
        <CardBody>
          <Alert status="error" size="sm">
            <AlertIcon />
            <Text fontSize="sm">{error}</Text>
          </Alert>
        </CardBody>
      </Card>
    )
  }

  if (!gitStatus) {
    return (
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiGitBranch} boxSize={5} />
              <Heading size="sm">Git 상태</Heading>
            </HStack>
            {onRefresh && (
              <Button size="xs" variant="ghost" onClick={handleRefresh}>
                <Icon as={FiRefreshCw} />
              </Button>
            )}
          </HStack>
        </CardHeader>
        <CardBody>
          <Text fontSize="sm" color="gray.500">
            Git 상태 정보를 사용할 수 없습니다.
          </Text>
        </CardBody>
      </Card>
    )
  }

  const RemoteStatusIcon = getRemoteStatusIcon(gitStatus.remoteStatus)
  const remoteStatusColor = getRemoteStatusColor(gitStatus.remoteStatus)
  const remoteStatusText = getRemoteStatusText(gitStatus.remoteStatus)

  return (
    <Card>
      <CardHeader pb={2}>
        <HStack justify="space-between">
          <HStack>
            <Icon as={FiGitBranch} boxSize={5} color="purple.500" />
            <Heading size="sm">Git 상태</Heading>
          </HStack>
          <HStack spacing={2}>
            <Badge colorScheme={remoteStatusColor} variant="subtle">
              <HStack spacing={1}>
                <Icon as={RemoteStatusIcon} boxSize={3} />
                <Text>{remoteStatusText}</Text>
              </HStack>
            </Badge>
            {onRefresh && (
              <Button size="xs" variant="ghost" onClick={handleRefresh}>
                <Icon as={FiRefreshCw} />
              </Button>
            )}
          </HStack>
        </HStack>
      </CardHeader>
      <CardBody pt={0}>
        <VStack align="stretch" spacing={3}>
          {/* 현재 브랜치 */}
          <HStack justify="space-between">
            <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
              현재 브랜치
            </Text>
            <Badge colorScheme="blue" variant="outline">
              {gitStatus.branch}
            </Badge>
          </HStack>

          {/* 마지막 커밋 */}
          <Box>
            <HStack justify="space-between" mb={1}>
              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                마지막 커밋
              </Text>
              {gitStatus.commitHash && (
                <Text fontSize="xs" fontFamily="mono" color="gray.500">
                  {formatCommitHash(gitStatus.commitHash)}
                </Text>
              )}
            </HStack>
            <Tooltip label={gitStatus.commitMessage || gitStatus.lastCommit} placement="top">
              <Text fontSize="sm" noOfLines={1} cursor="help">
                {gitStatus.commitMessage || gitStatus.lastCommit}
              </Text>
            </Tooltip>
            {gitStatus.commitAuthor && gitStatus.commitDate && (
              <HStack justify="space-between" mt={1}>
                <Text fontSize="xs" color="gray.500">
                  {gitStatus.commitAuthor}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {formatCommitDate(gitStatus.commitDate)}
                </Text>
              </HStack>
            )}
          </Box>

          {/* 원격 저장소 상태 세부 정보 */}
          {(gitStatus.aheadCount !== undefined || gitStatus.behindCount !== undefined) && (
            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                원격 저장소
              </Text>
              <HStack spacing={2}>
                {gitStatus.aheadCount !== undefined && gitStatus.aheadCount > 0 && (
                  <Badge colorScheme="blue" variant="subtle" size="sm">
                    <HStack spacing={1}>
                      <Icon as={FiArrowUp} boxSize={2} />
                      <Text>{gitStatus.aheadCount}</Text>
                    </HStack>
                  </Badge>
                )}
                {gitStatus.behindCount !== undefined && gitStatus.behindCount > 0 && (
                  <Badge colorScheme="orange" variant="subtle" size="sm">
                    <HStack spacing={1}>
                      <Icon as={FiArrowDown} boxSize={2} />
                      <Text>{gitStatus.behindCount}</Text>
                    </HStack>
                  </Badge>
                )}
              </HStack>
            </HStack>
          )}

          {/* 경고 상태들 */}
          {(gitStatus.hasUncommittedChanges || gitStatus.hasConflicts) && (
            <VStack align="stretch" spacing={2}>
              {gitStatus.hasUncommittedChanges && (
                <HStack>
                  <Icon as={FiAlertTriangle} boxSize={3} color="yellow.500" />
                  <Text fontSize="sm" color="yellow.600" _dark={{ color: 'yellow.400' }}>
                    커밋되지 않은 변경사항이 있습니다
                  </Text>
                </HStack>
              )}
              {gitStatus.hasConflicts && (
                <HStack>
                  <Icon as={FiAlertTriangle} boxSize={3} color="red.500" />
                  <Text fontSize="sm" color="red.600" _dark={{ color: 'red.400' }}>
                    병합 충돌이 발생했습니다
                  </Text>
                </HStack>
              )}
            </VStack>
          )}

          {/* 정상 상태 표시 */}
          {!gitStatus.hasUncommittedChanges && !gitStatus.hasConflicts && gitStatus.remoteStatus === 'up-to-date' && (
            <HStack>
              <Icon as={FiCheck} boxSize={3} color="green.500" />
              <Text fontSize="sm" color="green.600" _dark={{ color: 'green.400' }}>
                모든 변경사항이 동기화되었습니다
              </Text>
            </HStack>
          )}
        </VStack>
      </CardBody>
    </Card>
  )
}

export default GitStatusWidget