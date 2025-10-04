import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  HStack,
  Heading,
  Text,
  Stepper,
  Step,
  StepIndicator,
  StepStatus,
  StepIcon,
  StepNumber,
  StepTitle,
  StepDescription,
  StepSeparator,
  useSteps,
  Alert,
  AlertIcon,
  Code,
  Checkbox,
  CheckboxGroup,
  Stack,
  Divider,
  useToast
} from '@chakra-ui/react';
import { FiCheck, FiArrowRight, FiArrowLeft } from 'react-icons/fi';

interface CompanyFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

interface FormData {
  id: string;
  name: string;
  display_name: string;
  logo_url: string;
  webhooks: {
    news_main: {
      url: string;
      bot_name: string;
      bot_icon: string;
    };
    watchhamster: {
      url: string;
      bot_name: string;
      bot_icon: string;
    };
  };
  api_config: {
    news_api: {
      url: string;
      token: string;
    };
  };
  message_types: string[];
}

const steps = [
  { title: '기본 정보', description: '회사 정보 입력' },
  { title: '웹훅 설정', description: 'Dooray 웹훅 URL' },
  { title: 'API 설정', description: 'API 연동 정보' },
  { title: '완료', description: '설정 확인' }
];

const availableMessageTypes = [
  { id: 'business_day_comparison', name: '영업일 비교 분석' },
  { id: 'delay_notification', name: '지연 발행 알림' },
  { id: 'daily_report', name: '일일 통합 리포트' },
  { id: 'status_notification', name: '정시 발행 알림' },
  { id: 'no_data_notification', name: '데이터 갱신 없음' }
];

export const CompanyForm: React.FC<CompanyFormProps> = ({ onSuccess, onCancel }) => {
  const { activeStep, goToNext, goToPrevious } = useSteps({
    index: 0,
    count: steps.length
  });
  
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    id: '',
    name: '',
    display_name: '',
    logo_url: '',
    webhooks: {
      news_main: {
        url: '',
        bot_name: '',
        bot_icon: ''
      },
      watchhamster: {
        url: '',
        bot_name: '',
        bot_icon: ''
      }
    },
    api_config: {
      news_api: {
        url: '',
        token: ''
      }
    },
    message_types: ['business_day_comparison', 'delay_notification', 'daily_report']
  });
  
  const toast = useToast();

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/companies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await res.json();
      
      if (res.ok) {
        toast({
          title: '✅ 회사 추가 완료',
          description: `${formData.display_name}이(가) 추가되었습니다.`,
          status: 'success',
          duration: 3000
        });
        onSuccess();
      } else {
        throw new Error(data.detail || '회사 추가 실패');
      }
    } catch (err: any) {
      toast({
        title: '❌ 회사 추가 실패',
        description: err.message,
        status: 'error',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const isStepValid = () => {
    switch (activeStep) {
      case 0:
        return formData.id && formData.name && formData.display_name;
      case 1:
        return formData.webhooks.news_main.url && formData.webhooks.news_main.bot_name;
      case 2:
        return formData.api_config.news_api.url;
      case 3:
        return true;
      default:
        return false;
    }
  };

  return (
    <Box>
      {/* Stepper */}
      <Stepper index={activeStep} mb={8}>
        {steps.map((step, index) => (
          <Step key={index}>
            <StepIndicator>
              <StepStatus
                complete={<StepIcon />}
                incomplete={<StepNumber />}
                active={<StepNumber />}
              />
            </StepIndicator>

            <Box flexShrink="0">
              <StepTitle>{step.title}</StepTitle>
              <StepDescription>{step.description}</StepDescription>
            </Box>

            <StepSeparator />
          </Step>
        ))}
      </Stepper>

      {/* Step 0: 기본 정보 */}
      {activeStep === 0 && (
        <VStack spacing={4} align="stretch">
          <Heading size="md">📋 기본 정보</Heading>
          
          <FormControl isRequired>
            <FormLabel>회사 ID</FormLabel>
            <Input
              placeholder="company2 (영문 소문자, 숫자, 하이픈만)"
              value={formData.id}
              onChange={(e) => setFormData({ ...formData, id: e.target.value.toLowerCase() })}
            />
            <Text fontSize="xs" color="gray.600" mt={1}>
              예: posco, company2, samsung-electronics
            </Text>
          </FormControl>

          <FormControl isRequired>
            <FormLabel>회사명 (영문)</FormLabel>
            <Input
              placeholder="Company2"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </FormControl>

          <FormControl isRequired>
            <FormLabel>표시명 (한글)</FormLabel>
            <Input
              placeholder="회사2 주식회사"
              value={formData.display_name}
              onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
            />
          </FormControl>

          <FormControl>
            <FormLabel>로고 URL</FormLabel>
            <Input
              placeholder="https://company2.com/logo.png"
              value={formData.logo_url}
              onChange={(e) => setFormData({ ...formData, logo_url: e.target.value })}
            />
          </FormControl>
        </VStack>
      )}

      {/* Step 1: 웹훅 설정 */}
      {activeStep === 1 && (
        <VStack spacing={6} align="stretch">
          <Box>
            <Heading size="md" mb={4}>📬 메인 채널 웹훅 (뉴스 알림용)</Heading>
            
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel>Dooray 웹훅 URL</FormLabel>
                <Input
                  placeholder="https://company.dooray.com/services/.../..."
                  value={formData.webhooks.news_main.url}
                  onChange={(e) => setFormData({
                    ...formData,
                    webhooks: {
                      ...formData.webhooks,
                      news_main: { ...formData.webhooks.news_main, url: e.target.value }
                    }
                  })}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>BOT 이름</FormLabel>
                <Input
                  placeholder="회사2 뉴스 📊"
                  value={formData.webhooks.news_main.bot_name}
                  onChange={(e) => setFormData({
                    ...formData,
                    webhooks: {
                      ...formData.webhooks,
                      news_main: { ...formData.webhooks.news_main, bot_name: e.target.value }
                    }
                  })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>BOT 아이콘 URL</FormLabel>
                <Input
                  placeholder="https://company2.com/bot_icon.png"
                  value={formData.webhooks.news_main.bot_icon}
                  onChange={(e) => setFormData({
                    ...formData,
                    webhooks: {
                      ...formData.webhooks,
                      news_main: { ...formData.webhooks.news_main, bot_icon: e.target.value }
                    }
                  })}
                />
              </FormControl>
            </VStack>
          </Box>

          <Divider />

          <Box>
            <Heading size="md" mb={4}>📬 알림 채널 웹훅 (워치햄스터 알림용)</Heading>
            
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Dooray 웹훅 URL</FormLabel>
                <Input
                  placeholder="https://company.dooray.com/services/.../..."
                  value={formData.webhooks.watchhamster.url}
                  onChange={(e) => setFormData({
                    ...formData,
                    webhooks: {
                      ...formData.webhooks,
                      watchhamster: { ...formData.webhooks.watchhamster, url: e.target.value }
                    }
                  })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>BOT 이름</FormLabel>
                <Input
                  placeholder="회사2 워치햄스터 🎯"
                  value={formData.webhooks.watchhamster.bot_name}
                  onChange={(e) => setFormData({
                    ...formData,
                    webhooks: {
                      ...formData.webhooks,
                      watchhamster: { ...formData.webhooks.watchhamster, bot_name: e.target.value }
                    }
                  })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>BOT 아이콘 URL</FormLabel>
                <Input
                  placeholder="https://company2.com/bot_icon.png"
                  value={formData.webhooks.watchhamster.bot_icon}
                  onChange={(e) => setFormData({
                    ...formData,
                    webhooks: {
                      ...formData.webhooks,
                      watchhamster: { ...formData.webhooks.watchhamster, bot_icon: e.target.value }
                    }
                  })}
                />
              </FormControl>
            </VStack>
          </Box>
        </VStack>
      )}

      {/* Step 2: API 설정 */}
      {activeStep === 2 && (
        <VStack spacing={6} align="stretch">
          <Heading size="md">🔌 API 설정</Heading>
          
          <FormControl isRequired>
            <FormLabel>API URL</FormLabel>
            <Input
              placeholder="https://api.company2.com/news"
              value={formData.api_config.news_api.url}
              onChange={(e) => setFormData({
                ...formData,
                api_config: {
                  ...formData.api_config,
                  news_api: { ...formData.api_config.news_api, url: e.target.value }
                }
              })}
            />
          </FormControl>

          <FormControl>
            <FormLabel>API 토큰</FormLabel>
            <Input
              type="password"
              placeholder="YOUR_API_TOKEN"
              value={formData.api_config.news_api.token}
              onChange={(e) => setFormData({
                ...formData,
                api_config: {
                  ...formData.api_config,
                  news_api: { ...formData.api_config.news_api, token: e.target.value }
                }
              })}
            />
            <Text fontSize="xs" color="gray.600" mt={1}>
              선택사항: 나중에 설정할 수 있습니다
            </Text>
          </FormControl>

          <Divider />

          <FormControl>
            <FormLabel>사용할 메시지 타입</FormLabel>
            <CheckboxGroup
              value={formData.message_types}
              onChange={(values) => setFormData({ ...formData, message_types: values as string[] })}
            >
              <Stack spacing={2}>
                {availableMessageTypes.map((type) => (
                  <Checkbox key={type.id} value={type.id}>
                    {type.name}
                  </Checkbox>
                ))}
              </Stack>
            </CheckboxGroup>
          </FormControl>
        </VStack>
      )}

      {/* Step 3: 완료 */}
      {activeStep === 3 && (
        <VStack spacing={6} align="stretch">
          <Heading size="md">✅ 설정 확인</Heading>
          
          <Alert status="info">
            <AlertIcon />
            <Text>아래 정보를 확인하고 "완료" 버튼을 클릭하세요.</Text>
          </Alert>

          <Box>
            <Text fontWeight="bold" mb={2}>📋 기본 정보</Text>
            <VStack spacing={2} align="stretch" pl={4}>
              <HStack>
                <Text fontSize="sm" color="gray.600" w="100px">회사 ID:</Text>
                <Code fontSize="sm">{formData.id}</Code>
              </HStack>
              <HStack>
                <Text fontSize="sm" color="gray.600" w="100px">회사명:</Text>
                <Text fontSize="sm">{formData.name}</Text>
              </HStack>
              <HStack>
                <Text fontSize="sm" color="gray.600" w="100px">표시명:</Text>
                <Text fontSize="sm">{formData.display_name}</Text>
              </HStack>
              {formData.logo_url && (
                <HStack>
                  <Text fontSize="sm" color="gray.600" w="100px">로고:</Text>
                  <Code fontSize="xs">{formData.logo_url}</Code>
                </HStack>
              )}
            </VStack>
          </Box>

          <Box>
            <Text fontWeight="bold" mb={2}>📬 웹훅 설정</Text>
            <VStack spacing={3} align="stretch" pl={4}>
              <Box>
                <Text fontSize="sm" fontWeight="bold">메인 채널</Text>
                <Text fontSize="xs" color="gray.600">BOT: {formData.webhooks.news_main.bot_name}</Text>
                <Code fontSize="xs" display="block" mt={1}>
                  {formData.webhooks.news_main.url}
                </Code>
              </Box>
              {formData.webhooks.watchhamster.url && (
                <Box>
                  <Text fontSize="sm" fontWeight="bold">알림 채널</Text>
                  <Text fontSize="xs" color="gray.600">BOT: {formData.webhooks.watchhamster.bot_name}</Text>
                  <Code fontSize="xs" display="block" mt={1}>
                    {formData.webhooks.watchhamster.url}
                  </Code>
                </Box>
              )}
            </VStack>
          </Box>

          <Box>
            <Text fontWeight="bold" mb={2}>🔌 API 설정</Text>
            <VStack spacing={2} align="stretch" pl={4}>
              <HStack>
                <Text fontSize="sm" color="gray.600" w="100px">API URL:</Text>
                <Code fontSize="xs">{formData.api_config.news_api.url}</Code>
              </HStack>
              <HStack>
                <Text fontSize="sm" color="gray.600" w="100px">API 토큰:</Text>
                <Text fontSize="xs">{formData.api_config.news_api.token ? '설정됨' : '미설정'}</Text>
              </HStack>
            </VStack>
          </Box>

          <Box>
            <Text fontWeight="bold" mb={2}>📋 메시지 타입 ({formData.message_types.length}개)</Text>
            <Stack spacing={1} pl={4}>
              {formData.message_types.map((typeId) => {
                const type = availableMessageTypes.find(t => t.id === typeId);
                return type ? (
                  <Text key={typeId} fontSize="sm">
                    ✓ {type.name}
                  </Text>
                ) : null;
              })}
            </Stack>
          </Box>
        </VStack>
      )}

      {/* 버튼 */}
      <HStack spacing={4} mt={8} justify="flex-end">
        <Button onClick={onCancel} variant="ghost">
          취소
        </Button>
        
        {activeStep > 0 && (
          <Button
            leftIcon={<FiArrowLeft />}
            onClick={goToPrevious}
            variant="outline"
          >
            이전
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button
            rightIcon={<FiArrowRight />}
            onClick={goToNext}
            colorScheme="blue"
            isDisabled={!isStepValid()}
          >
            다음
          </Button>
        ) : (
          <Button
            leftIcon={<FiCheck />}
            onClick={handleSubmit}
            colorScheme="green"
            isLoading={loading}
          >
            완료
          </Button>
        )}
      </HStack>
    </Box>
  );
};

export default CompanyForm;
