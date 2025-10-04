/**
 * Git Pages 배포 상태 위젯
 * publish 브랜치의 배포 상태 표시 (main 브랜치는 비공개)
 */

import React from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Badge,
  VStack,
  HStack,
  Icon,
  Tooltip,
  Skeleton,
  Alert,
  AlertIcon,
  Button,
  Link,
  useColorModeValue
} from '@chakra-ui/react';
import {
  FiGitBranch,
  FiGlobe,
  FiCheck,
  FiClock,
  FiRefreshCw,
  FiExternalLink
} from 'react-icons/fi';

interface PublishStatus {
  branch: string;  // 'publish'
  lastDeploy: string;  // 마지막 배포 시간
  deployStatus: 'success' | 'pending' | 'failed';
  commitHash: string;
  commitMessage: string;
  commitDate: string;
  pagesUrl: string;  // GitHub Pages URL
  isPublic: boolean;
}

interface PublishStatusWidgetProps {
  status?: PublishStatus;
  isLoading?: boolean;
  error?: string;
  onRefresh?: () => void;
}

const getDeployStatusColor = (status: string) => {
  switch (status) {
    case 'success':
      return 'green';
    case 'pending':
      return 'yellow';
    case 'failed':
      return 'red';
    default:
      return 'gray';
  }
};

const getDeployStatusText = (status: string) => {
  switch (status) {
    case 'success':
      return '배포 완료';
    case 'pending':
      return '배포 중';
    case 'failed':
      return '배포 실패';
    default:
      return '알 수 없음';
  }
};

const formatCommitHash = (hash: string) => {
  return hash.slice(0, 7);
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 60) return `${minutes}분 전`;
  if (hours < 24) return `${hours}시간 전`;
  return `${days}일 전`;
};

export const PublishStatusWidget: React.FC<PublishStatusWidgetProps> = ({
  status,
  isLoading = false,
  error,
  onRefresh
}) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  if (error) {
    return (
      <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
        <CardBody>
          <Alert status="error">
            <AlertIcon />
            <Text fontSize="sm">{error}</Text>
          </Alert>
        </CardBody>
      </Card>
    );
  }

  if (isLoading || !status) {
    return (
      <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
        <CardHeader>
          <Skeleton height="20px" width="150px" />
        </CardHeader>
        <CardBody>
          <VStack spacing={3} align="stretch">
            <Skeleton height="16px" />
            <Skeleton height="16px" />
            <Skeleton height="16px" />
          </VStack>
        </CardBody>
      </Card>
    );
  }

  const deployColor = getDeployStatusColor(status.deployStatus);

  return (
    <Card
      bg={cardBg}
      borderColor={borderColor}
      borderWidth="1px"
      _hover={{ shadow: 'md' }}
      transition="all 0.2s"
    >
      <CardHeader pb={2}>
        <HStack justify="space-between">
          <HStack spacing={2}>
            <Icon as={FiGlobe} boxSize={5} color="purple.500" />
            <Heading size="sm">배포 상태</Heading>
          </HStack>
          <Badge colorScheme={deployColor}>
            {getDeployStatusText(status.deployStatus)}
          </Badge>
        </HStack>
      </CardHeader>

      <CardBody pt={0}>
        <VStack spacing={3} align="stretch">
          {/* 브랜치 정보 */}
          <HStack justify="space-between">
            <HStack spacing={2}>
              <Icon as={FiGitBranch} boxSize={4} color="blue.500" />
              <Text fontSize="sm" fontWeight="medium">배포 브랜치</Text>
            </HStack>
            <Badge colorScheme="blue" fontSize="sm">
              {status.branch}
            </Badge>
          </HStack>

          {/* 공개 상태 */}
          <HStack justify="space-between">
            <HStack spacing={2}>
              <Icon as={FiGlobe} boxSize={4} color="green.500" />
              <Text fontSize="sm" fontWeight="medium">공개 상태</Text>
            </HStack>
            <Badge colorScheme={status.isPublic ? 'green' : 'gray'} fontSize="sm">
              {status.isPublic ? '공개' : '비공개'}
            </Badge>
          </HStack>

          {/* 마지막 배포 */}
          <HStack justify="space-between">
            <HStack spacing={2}>
              <Icon as={FiClock} boxSize={4} color="orange.500" />
              <Text fontSize="sm" fontWeight="medium">마지막 배포</Text>
            </HStack>
            <Tooltip label={new Date(status.lastDeploy).toLocaleString('ko-KR')}>
              <Text fontSize="sm" color="gray.600">
                {formatDate(status.lastDeploy)}
              </Text>
            </Tooltip>
          </HStack>

          {/* 커밋 정보 */}
          <VStack spacing={1} align="stretch" pt={2}>
            <HStack justify="space-between">
              <Text fontSize="xs" color="gray.500">커밋</Text>
              <Tooltip label={status.commitHash}>
                <Text fontSize="xs" fontFamily="mono" color="gray.600">
                  {formatCommitHash(status.commitHash)}
                </Text>
              </Tooltip>
            </HStack>
            <Text fontSize="xs" color="gray.600" noOfLines={2}>
              {status.commitMessage}
            </Text>
          </VStack>

          {/* GitHub Pages 링크 */}
          {status.pagesUrl && (
            <Link href={status.pagesUrl} isExternal>
              <Button
                size="sm"
                variant="outline"
                colorScheme="purple"
                width="full"
                rightIcon={<FiExternalLink />}
              >
                배포 사이트 보기
              </Button>
            </Link>
          )}

          {/* 새로고침 버튼 */}
          {onRefresh && (
            <Button
              size="sm"
              variant="ghost"
              leftIcon={<FiRefreshCw />}
              onClick={onRefresh}
              width="full"
            >
              새로고침
            </Button>
          )}

          {/* 안내 메시지 */}
          <Text fontSize="xs" color="gray.500" pt={2}>
            💡 개발 코드(main)는 비공개입니다
          </Text>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default PublishStatusWidget;
