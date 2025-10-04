import React from 'react'
import {
  VStack,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  Button,
  useToast,
} from '@chakra-ui/react'
import { FiSend } from 'react-icons/fi'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface WebhookEditorProps {
  config: any
  onChange: (config: any) => void
}

const WebhookEditor: React.FC<WebhookEditorProps> = ({ config, onChange }) => {
  const toast = useToast()

  const testWebhook = async () => {
    try {
      await axios.post(`${API_BASE}/api/diagnostics/test-webhook?webhook_url=${encodeURIComponent(config.url)}`)
      toast({
        title: '웹훅 테스트 성공',
        description: 'Dooray에 메시지가 발송되었습니다',
        status: 'success',
        duration: 3000,
      })
    } catch (error: any) {
      toast({
        title: '웹훅 테스트 실패',
        description: error.response?.data?.detail || '웹훅 URL을 확인해주세요',
        status: 'error',
        duration: 5000,
      })
    }
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* 웹훅 활성화 */}
      <FormControl display="flex" alignItems="center">
        <FormLabel mb="0">웹훅 활성화</FormLabel>
        <Switch
          isChecked={config.enabled}
          onChange={(e) => onChange({ ...config, enabled: e.target.checked })}
          colorScheme="green"
        />
      </FormControl>

      {/* 웹훅 URL */}
      <FormControl isRequired={config.enabled}>
        <FormLabel>Dooray 웹훅 URL</FormLabel>
        <Input
          value={config.url}
          onChange={(e) => onChange({ ...config, url: e.target.value })}
          placeholder="https://hook.dooray.com/services/..."
          isDisabled={!config.enabled}
        />
      </FormControl>

      {/* 발송 조건 */}
      <FormControl isRequired={config.enabled}>
        <FormLabel>발송 조건</FormLabel>
        <Select
          value={config.condition}
          onChange={(e) => onChange({ ...config, condition: e.target.value })}
          isDisabled={!config.enabled}
        >
          <option value="always">항상 발송</option>
          <option value="on_change">변경 감지 시</option>
          <option value="on_error">오류 발생 시</option>
        </Select>
      </FormControl>

      {/* 템플릿 */}
      <FormControl>
        <FormLabel>메시지 템플릿</FormLabel>
        <Select
          value={config.templateId}
          onChange={(e) => onChange({ ...config, templateId: e.target.value })}
          isDisabled={!config.enabled}
        >
          <option value="default">기본 템플릿</option>
          <option value="detailed">상세 템플릿</option>
          <option value="simple">간단 템플릿</option>
        </Select>
      </FormControl>

      {/* 타임아웃 */}
      <FormControl>
        <FormLabel>타임아웃 (초)</FormLabel>
        <Input
          type="number"
          value={config.timeout}
          onChange={(e) => onChange({ ...config, timeout: parseInt(e.target.value) })}
          min={1}
          max={60}
          isDisabled={!config.enabled}
        />
      </FormControl>

      {/* 테스트 버튼 */}
      <Button
        leftIcon={<FiSend />}
        colorScheme="blue"
        onClick={testWebhook}
        isDisabled={!config.enabled || !config.url}
      >
        웹훅 테스트 발송
      </Button>
    </VStack>
  )
}

export default WebhookEditor
