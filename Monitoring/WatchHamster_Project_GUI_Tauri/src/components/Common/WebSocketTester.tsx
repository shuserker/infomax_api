/**
 * WebSocket 테스트 도구 컴포넌트
 * 
 * 개발 중 WebSocket 연결과 메시지 송수신을 테스트하기 위한 도구입니다.
 */

import React, { useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  Textarea,
  Select,
  Badge,
  Divider,
  useToast,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Code,
  useColorModeValue,
} from '@chakra-ui/react'
import { FiSend, FiTrash2, FiCopy } from 'react-icons/fi'
import { useRealtimeMessages } from '../../hooks/useRealtimeMessages'

interface MessageLog {
  id: string
  type: 'sent' | 'received'
  timestamp: string
  data: any
}

export const WebSocketTester: React.FC = () => {
  const toast = useToast()
  const [messageType, setMessageType] = useState('ping')
  const [messageData, setMessageData] = useState('{}')
  const [messageLogs, setMessageLogs] = useState<MessageLog[]>([])

  // 색상 테마
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  // 실시간 메시지 훅 사용
  const {
    isConnected,
    connectionStatus,
    sendMessage,
    connect,
    disconnect,
    reconnect,
    subscribe,
    requestStatus,
  } = useRealtimeMessages({
    autoSubscribe: false, // 수동으로 구독 관리
  })

  // 메시지 로그 추가
  const addMessageLog = (type: 'sent' | 'received', data: any) => {
    const log: MessageLog = {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      timestamp: new Date().toISOString(),
      data,
    }
    
    setMessageLogs(prev => [log, ...prev.slice(0, 49)]) // 최대 50개 유지
  }

  // 메시지 전송
  const handleSendMessage = () => {
    try {
      const data = messageData ? JSON.parse(messageData) : {}
      const success = sendMessage(messageType, data)
      
      if (success) {
        addMessageLog('sent', { type: messageType, data })
        toast({
          title: '메시지 전송 완료',
          status: 'success',
          duration: 2000,
        })
      } else {
        toast({
          title: '메시지 전송 실패',
          description: 'WebSocket 연결을 확인해주세요.',
          status: 'error',
          duration: 3000,
        })
      }
    } catch (error) {
      toast({
        title: 'JSON 파싱 오류',
        description: '메시지 데이터 형식을 확인해주세요.',
        status: 'error',
        duration: 3000,
      })
    }
  }

  // 미리 정의된 메시지 템플릿
  const messageTemplates = {
    ping: '{}',
    request_status: '{}',
    subscribe: '{"subscription": "all"}',
    unsubscribe: '{"subscription": "all"}',
    service_control: '{"service_id": "posco_news", "action": "start"}',
    webhook_test: '{"url": "https://discord.com/api/webhooks/...", "message": "테스트 메시지"}',
  }

  // 템플릿 선택 시 데이터 업데이트
  const handleTemplateChange = (template: string) => {
    setMessageType(template)
    setMessageData(messageTemplates[template as keyof typeof messageTemplates] || '{}')
  }

  // 로그 복사
  const copyLog = (log: MessageLog) => {
    const text = JSON.stringify(log, null, 2)
    navigator.clipboard.writeText(text)
    toast({
      title: '로그 복사됨',
      status: 'success',
      duration: 1000,
    })
  }

  // 로그 지우기
  const clearLogs = () => {
    setMessageLogs([])
    toast({
      title: '로그 지워짐',
      status: 'info',
      duration: 1000,
    })
  }

  return (
    <Box
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="md"
      p={6}
      shadow="sm"
    >
      <VStack spacing={6} align="stretch">
        {/* 헤더 */}
        <HStack justify="space-between">
          <Text fontSize="lg" fontWeight="bold">
            WebSocket 테스트 도구
          </Text>
          <Badge
            colorScheme={isConnected ? 'green' : 'red'}
            variant="subtle"
          >
            {connectionStatus}
          </Badge>
        </HStack>

        {/* 연결 제어 */}
        <HStack spacing={3}>
          <Button
            size="sm"
            colorScheme="blue"
            onClick={connect}
            isDisabled={isConnected}
          >
            연결
          </Button>
          <Button
            size="sm"
            colorScheme="red"
            onClick={disconnect}
            isDisabled={!isConnected}
          >
            연결 해제
          </Button>
          <Button
            size="sm"
            colorScheme="orange"
            onClick={reconnect}
          >
            재연결
          </Button>
          <Button
            size="sm"
            colorScheme="green"
            onClick={() => subscribe('all')}
            isDisabled={!isConnected}
          >
            전체 구독
          </Button>
          <Button
            size="sm"
            colorScheme="purple"
            onClick={requestStatus}
            isDisabled={!isConnected}
          >
            상태 요청
          </Button>
        </HStack>

        <Divider />

        {/* 메시지 전송 */}
        <VStack spacing={4} align="stretch">
          <Text fontWeight="medium">메시지 전송</Text>
          
          <HStack spacing={3}>
            <Select
              value={messageType}
              onChange={(e) => handleTemplateChange(e.target.value)}
              maxW="200px"
            >
              <option value="ping">Ping</option>
              <option value="request_status">상태 요청</option>
              <option value="subscribe">구독</option>
              <option value="unsubscribe">구독 해제</option>
              <option value="service_control">서비스 제어</option>
              <option value="webhook_test">웹훅 테스트</option>
            </Select>
            
            <Input
              placeholder="메시지 타입"
              value={messageType}
              onChange={(e) => setMessageType(e.target.value)}
              maxW="200px"
            />
          </HStack>

          <Textarea
            placeholder="메시지 데이터 (JSON 형식)"
            value={messageData}
            onChange={(e) => setMessageData(e.target.value)}
            rows={4}
            fontFamily="mono"
          />

          <Button
            leftIcon={<FiSend />}
            colorScheme="blue"
            onClick={handleSendMessage}
            isDisabled={!isConnected}
          >
            메시지 전송
          </Button>
        </VStack>

        <Divider />

        {/* 메시지 로그 */}
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between">
            <Text fontWeight="medium">메시지 로그 ({messageLogs.length})</Text>
            <Button
              size="sm"
              leftIcon={<FiTrash2 />}
              variant="outline"
              onClick={clearLogs}
            >
              로그 지우기
            </Button>
          </HStack>

          <Box maxH="400px" overflowY="auto">
            <Accordion allowMultiple>
              {messageLogs.map((log) => (
                <AccordionItem key={log.id}>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      <HStack spacing={3}>
                        <Badge
                          colorScheme={log.type === 'sent' ? 'blue' : 'green'}
                          variant="subtle"
                        >
                          {log.type === 'sent' ? '전송' : '수신'}
                        </Badge>
                        <Text fontSize="sm">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </Text>
                        <Text fontSize="sm" fontWeight="medium">
                          {log.data.type || 'unknown'}
                        </Text>
                      </HStack>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel pb={4}>
                    <VStack align="stretch" spacing={2}>
                      <HStack justify="space-between">
                        <Text fontSize="xs" color="gray.500">
                          {log.timestamp}
                        </Text>
                        <Button
                          size="xs"
                          leftIcon={<FiCopy />}
                          variant="ghost"
                          onClick={() => copyLog(log)}
                        >
                          복사
                        </Button>
                      </HStack>
                      <Code
                        p={3}
                        borderRadius="md"
                        fontSize="xs"
                        whiteSpace="pre-wrap"
                        wordBreak="break-all"
                      >
                        {JSON.stringify(log.data, null, 2)}
                      </Code>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>

            {messageLogs.length === 0 && (
              <Text textAlign="center" color="gray.500" py={8}>
                메시지 로그가 없습니다.
              </Text>
            )}
          </Box>
        </VStack>
      </VStack>
    </Box>
  )
}

export default WebSocketTester