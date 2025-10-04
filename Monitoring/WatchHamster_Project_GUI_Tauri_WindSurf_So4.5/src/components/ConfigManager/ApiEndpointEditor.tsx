import React from 'react'
import {
  VStack,
  HStack,
  FormControl,
  FormLabel,
  Input,
  Select,
  Button,
  Text,
  Code,
  Box,
  IconButton,
} from '@chakra-ui/react'
import { FiPlus, FiTrash2 } from 'react-icons/fi'

interface ApiEndpointEditorProps {
  config: any
  onChange: (config: any) => void
}

const ApiEndpointEditor: React.FC<ApiEndpointEditorProps> = ({ config, onChange }) => {
  const addHeader = () => {
    const newHeaders = { ...config.headers, '': '' }
    onChange({ ...config, headers: newHeaders })
  }

  const updateHeader = (oldKey: string, newKey: string, value: string) => {
    const newHeaders = { ...config.headers }
    if (oldKey !== newKey) {
      delete newHeaders[oldKey]
    }
    newHeaders[newKey] = value
    onChange({ ...config, headers: newHeaders })
  }

  const removeHeader = (key: string) => {
    const newHeaders = { ...config.headers }
    delete newHeaders[key]
    onChange({ ...config, headers: newHeaders })
  }

  const addParam = () => {
    const newParams = { ...config.params, '': '' }
    onChange({ ...config, params: newParams })
  }

  const updateParam = (oldKey: string, newKey: string, value: string) => {
    const newParams = { ...config.params }
    if (oldKey !== newKey) {
      delete newParams[oldKey]
    }
    newParams[newKey] = value
    onChange({ ...config, params: newParams })
  }

  const removeParam = (key: string) => {
    const newParams = { ...config.params }
    delete newParams[key]
    onChange({ ...config, params: newParams })
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* 엔드포인트 URL */}
      <FormControl isRequired>
        <FormLabel>API 엔드포인트 URL</FormLabel>
        <Input
          value={config.endpoint}
          onChange={(e) => onChange({ ...config, endpoint: e.target.value })}
          placeholder="https://api.example.com/endpoint"
        />
      </FormControl>

      {/* HTTP 메서드 */}
      <FormControl isRequired>
        <FormLabel>HTTP 메서드</FormLabel>
        <Select
          value={config.method}
          onChange={(e) => onChange({ ...config, method: e.target.value })}
        >
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
        </Select>
      </FormControl>

      {/* 인증 설정 */}
      <Box>
        <FormLabel>인증 방식</FormLabel>
        <VStack spacing={3} align="stretch">
          <Select
            value={config.auth.type}
            onChange={(e) =>
              onChange({
                ...config,
                auth: { ...config.auth, type: e.target.value },
              })
            }
          >
            <option value="none">없음</option>
            <option value="bearer">Bearer Token</option>
            <option value="apikey">API Key</option>
            <option value="basic">Basic Auth</option>
          </Select>

          {config.auth.type === 'bearer' && (
            <FormControl>
              <FormLabel fontSize="sm">Bearer 토큰</FormLabel>
              <Input
                value={config.auth.token || ''}
                onChange={(e) =>
                  onChange({
                    ...config,
                    auth: { ...config.auth, token: e.target.value },
                  })
                }
                placeholder="API 인증 토큰 입력"
              />
            </FormControl>
          )}

          {config.auth.type === 'apikey' && (
            <FormControl>
              <FormLabel fontSize="sm">API Key</FormLabel>
              <Input
                value={config.auth.apiKey || ''}
                onChange={(e) =>
                  onChange({
                    ...config,
                    auth: { ...config.auth, apiKey: e.target.value },
                  })
                }
                placeholder="API Key 입력"
              />
            </FormControl>
          )}

          {config.auth.type === 'basic' && (
            <>
              <FormControl>
                <FormLabel fontSize="sm">사용자명</FormLabel>
                <Input
                  value={config.auth.username || ''}
                  onChange={(e) =>
                    onChange({
                      ...config,
                      auth: { ...config.auth, username: e.target.value },
                    })
                  }
                />
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm">비밀번호</FormLabel>
                <Input
                  value={config.auth.password || ''}
                  onChange={(e) =>
                    onChange({
                      ...config,
                      auth: { ...config.auth, password: e.target.value },
                    })
                  }
                />
              </FormControl>
            </>
          )}
        </VStack>
      </Box>

      {/* 요청 헤더 */}
      <Box>
        <HStack justify="space-between" mb={2}>
          <FormLabel mb={0}>요청 헤더</FormLabel>
          <Button size="sm" leftIcon={<FiPlus />} onClick={addHeader}>
            헤더 추가
          </Button>
        </HStack>
        <VStack spacing={2} align="stretch">
          {Object.entries(config.headers || {}).map(([key, value]: [string, any]) => (
            <HStack key={key}>
              <Input
                placeholder="헤더 이름"
                value={key}
                onChange={(e) => updateHeader(key, e.target.value, value)}
                size="sm"
              />
              <Input
                placeholder="값"
                value={value}
                onChange={(e) => updateHeader(key, key, e.target.value)}
                size="sm"
              />
              <IconButton
                aria-label="삭제"
                icon={<FiTrash2 />}
                size="sm"
                colorScheme="red"
                variant="ghost"
                onClick={() => removeHeader(key)}
              />
            </HStack>
          ))}
        </VStack>
      </Box>

      {/* 쿼리 파라미터 */}
      <Box>
        <HStack justify="space-between" mb={2}>
          <FormLabel mb={0}>쿼리 파라미터</FormLabel>
          <Button size="sm" leftIcon={<FiPlus />} onClick={addParam}>
            파라미터 추가
          </Button>
        </HStack>
        <VStack spacing={2} align="stretch">
          {Object.entries(config.params || {}).map(([key, value]: [string, any]) => (
            <HStack key={key}>
              <Input
                placeholder="파라미터 이름"
                value={key}
                onChange={(e) => updateParam(key, e.target.value, value)}
                size="sm"
              />
              <Input
                placeholder="값 (예: {today})"
                value={value}
                onChange={(e) => updateParam(key, key, e.target.value)}
                size="sm"
              />
              <IconButton
                aria-label="삭제"
                icon={<FiTrash2 />}
                size="sm"
                colorScheme="red"
                variant="ghost"
                onClick={() => removeParam(key)}
              />
            </HStack>
          ))}
        </VStack>
        <Text fontSize="xs" color="gray.500" mt={2}>
          동적 값: <Code fontSize="xs">{'{today}'}</Code>,{' '}
          <Code fontSize="xs">{'{yesterday}'}</Code>,{' '}
          <Code fontSize="xs">{'{timestamp}'}</Code>
        </Text>
      </Box>

      {/* 타임아웃 */}
      <FormControl>
        <FormLabel>타임아웃 (초)</FormLabel>
        <Input
          type="number"
          value={config.timeout}
          onChange={(e) => onChange({ ...config, timeout: parseInt(e.target.value) })}
          min={1}
          max={300}
        />
      </FormControl>
    </VStack>
  )
}

export default ApiEndpointEditor
