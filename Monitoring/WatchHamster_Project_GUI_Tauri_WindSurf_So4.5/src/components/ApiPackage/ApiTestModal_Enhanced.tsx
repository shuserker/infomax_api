import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  HStack,
  Text,
  Input,
  FormControl,
  FormLabel,
  Button,
  Badge,
  Code,
  Alert,
  AlertIcon,
  AlertDescription,
  Box,
  Divider,
  Grid,
  GridItem,
  Collapse,
  useToast,
  useColorModeValue,
  IconButton,
  Tooltip,
  Flex,
  Spacer,
  Card,
  CardBody,
  CardHeader,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Switch,
  FormHelperText,
  Textarea,
  Spinner,
  Progress
} from '@chakra-ui/react';
import {
  FiPlay,
  FiCopy,
  FiDownload,
  FiSettings,
  FiCode,
  FiZap,
  FiCheck,
  FiX,
  FiEye,
  FiEyeOff,
  FiMaximize2,
  FiMinimize2
} from 'react-icons/fi';
import { parameterDefaultManager } from '../../utils/parameterDefaultManager';

interface ApiParameter {
  name: string;
  type: string;
  required: boolean;
  description?: string;
  defaultValue?: string;
}

interface ApiPackage {
  id: string;
  category: string;
  itemName: string;
  fullName: string;
  urlPath: string;
  baseUrl: string;
  fullUrl: string;
  inputs: ApiParameter[];
  description?: string;
  tags?: string[];
}

interface ApiTestModalEnhancedProps {
  isOpen: boolean;
  onClose: () => void;
  package: ApiPackage;
  apiToken: string;
}

interface TestResult {
  success: boolean;
  data?: any;
  error?: string;
  status?: number;
  url?: string;
  timestamp?: string;
  duration?: number;
}

const ApiTestModalEnhanced: React.FC<ApiTestModalEnhancedProps> = ({
  isOpen,
  onClose,
  package: pkg,
  apiToken
}) => {
  const [inputValues, setInputValues] = useState<{[key: string]: string}>({});
  const [isLoading, setIsLoading] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [error, setError] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [autoFillEnabled, setAutoFillEnabled] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showRawResponse, setShowRawResponse] = useState(false);

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const codeBg = useColorModeValue('gray.50', 'gray.700');

  // 모달이 열릴 때 기본값 로드
  useEffect(() => {
    if (pkg && isOpen) {
      const defaultValues: {[key: string]: string} = {};
      const apiDefaults = parameterDefaultManager.getApiDefaults(pkg.urlPath);
      
      pkg.inputs.forEach(input => {
        const savedDefault = apiDefaults[input.name];
        if (savedDefault !== undefined) {
          defaultValues[input.name] = savedDefault;
        } else {
          defaultValues[input.name] = input.defaultValue || getSmartDefault(pkg.urlPath, input.name);
        }
      });
      
      setInputValues(defaultValues);
      setTestResult(null);
      setError('');
    }
  }, [pkg, isOpen]);

  // 스마트 기본값 생성
  const getSmartDefault = (apiPath: string, paramName: string): string => {
    if (paramName === 'stdcd') return 'KR101501DA32';
    if (paramName === 'code') return '005930';
    if (paramName === 'bonddate') return new Date().toISOString().slice(0, 10).replace(/-/g, '');
    if (paramName === 'startDate' || paramName === 'endDate') {
      const date = new Date();
      date.setDate(date.getDate() - 1);
      return date.toISOString().slice(0, 10).replace(/-/g, '');
    }
    return '';
  };

  const handleInputChange = (paramName: string, value: string) => {
    setInputValues(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleApiTest = async () => {
    if (!pkg || !apiToken) {
      toast({
        title: '❌ 토큰 오류',
        description: 'API 토큰을 먼저 설정해주세요.',
        status: 'error',
        duration: 3000
      });
      return;
    }

    setIsLoading(true);
    setError('');
    setTestResult(null);
    
    const startTime = Date.now();

    try {
      // 파라미터 처리
      const params: {[key: string]: string} = {};
      
      pkg.inputs.forEach(input => {
        const value = inputValues[input.name];
        
        if (pkg.urlPath === 'bond/market/mn_hist' || pkg.urlPath.includes('code') || pkg.urlPath.includes('search')) {
          params[input.name] = value || '';
        } else {
          if (value?.trim()) {
            params[input.name] = value.trim();
          }
        }
      });

      // 로컬 프록시 URL 구성
      const localProxyUrl = `http://localhost:8001/api/infomax/${pkg.urlPath}`;
      const searchParams = new URLSearchParams();
      
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });

      const finalUrl = searchParams.toString() 
        ? `${localProxyUrl}?${searchParams.toString()}`
        : localProxyUrl;

      console.log('🚀 API 호출:', { url: finalUrl, params });

      const response = await fetch(finalUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorMessage;
        } catch {
          // JSON 파싱 실패 시 기본 에러 메시지 사용
        }
        throw new Error(errorMessage);
      }

      const responseData = await response.json();
      const duration = Date.now() - startTime;

      setTestResult({
        success: true,
        data: responseData,
        status: response.status,
        url: finalUrl,
        timestamp: new Date().toLocaleString('ko-KR'),
        duration
      });
      
      toast({
        title: '✅ API 호출 성공!',
        description: `${pkg.fullName} (${duration}ms)`,
        status: 'success',
        duration: 3000
      });

    } catch (err) {
      const duration = Date.now() - startTime;
      let errorMessage = '알 수 없는 오류가 발생했습니다.';
      
      if (err instanceof TypeError && err.message.includes('Failed to fetch')) {
        errorMessage = '🔌 로컬 서버 연결 실패! localhost:8001이 실행 중인지 확인하세요.';
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setTestResult({
        success: false,
        error: errorMessage,
        duration
      });
      
      toast({
        title: '❌ API 호출 실패',
        description: errorMessage,
        status: 'error',
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      toast({
        title: '📋 복사 완료',
        description: '클립보드에 복사되었습니다.',
        status: 'success',
        duration: 2000
      });
    });
  };

  const downloadResult = () => {
    if (!testResult?.data) return;
    
    const dataStr = JSON.stringify(testResult.data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${pkg.itemName}_result_${new Date().toISOString().slice(0, 19)}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    
    toast({
      title: '📥 다운로드 완료',
      status: 'success',
      duration: 2000
    });
  };

  const generatePythonCode = (): string => {
    const params = Object.entries(inputValues)
      .filter(([_, value]) => value.trim())
      .map(([key, value]) => `    "${key}": "${value}"`)
      .join(',\n');

    return `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoMax API 호출: ${pkg.fullName}
Generated: ${new Date().toLocaleString('ko-KR')}
"""

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# SSL 경고 비활성화
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# API 설정
API_URL = '${pkg.fullUrl}'
API_TOKEN = '${apiToken ? apiToken.slice(0, 6) + '...' : 'YOUR_TOKEN_HERE'}'

# 파라미터 설정
params = {
${params}
}

# 요청 헤더
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

try:
    print(f"🚀 API 호출: {API_URL}")
    print(f"📋 파라미터: {params}")
    
    response = requests.get(API_URL, params=params, headers=headers, verify=False)
    
    print(f"📊 응답 상태: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 응답 데이터:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 오류: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"❌ 예외 발생: {str(e)}")`;
  };

  if (!pkg) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      size={isFullscreen ? "full" : "4xl"}
      scrollBehavior="inside"
    >
      <ModalOverlay />
      <ModalContent 
        maxH={isFullscreen ? "100vh" : "90vh"}
        bg={bgColor}
      >
        <ModalHeader borderBottom="1px" borderColor={borderColor}>
          <HStack justify="space-between" w="full">
            <VStack spacing={1} align="start">
              <HStack>
                <Badge colorScheme="blue" variant="solid">
                  {pkg.category}
                </Badge>
                <Text fontSize="xl" fontWeight="bold">
                  {pkg.itemName}
                </Text>
              </HStack>
              <Text fontSize="sm" color="gray.600">
                {pkg.fullName}
              </Text>
            </VStack>
            
            <HStack spacing={2}>
              <Tooltip label="전체화면 토글">
                <IconButton
                  icon={isFullscreen ? <FiMinimize2 /> : <FiMaximize2 />}
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  aria-label="전체화면"
                />
              </Tooltip>
              <Tooltip label="파라미터 기본값 관리">
                <IconButton
                  icon={<FiSettings />}
                  size="sm"
                  variant="ghost"
                  aria-label="설정"
                />
              </Tooltip>
            </HStack>
          </HStack>
        </ModalHeader>
        
        <ModalCloseButton />

        <ModalBody p={6}>
          <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
            
            {/* 왼쪽: 파라미터 입력 */}
            <GridItem>
              <Card>
                <CardHeader>
                  <HStack justify="space-between">
                    <Text fontSize="lg" fontWeight="bold">
                      📋 파라미터 설정
                    </Text>
                    <HStack>
                      <Text fontSize="sm">자동완성</Text>
                      <Switch
                        size="sm"
                        isChecked={autoFillEnabled}
                        onChange={(e) => setAutoFillEnabled(e.target.checked)}
                      />
                    </HStack>
                  </HStack>
                </CardHeader>
                
                <CardBody>
                  <VStack spacing={4} align="stretch">
                    {pkg.inputs.length === 0 ? (
                      <Alert status="info">
                        <AlertIcon />
                        <AlertDescription>
                          이 API는 파라미터가 필요하지 않습니다.
                        </AlertDescription>
                      </Alert>
                    ) : (
                      pkg.inputs.map(input => (
                        <FormControl key={input.name}>
                          <FormLabel fontSize="sm">
                            <HStack>
                              <Text>{input.name}</Text>
                              {input.required && (
                                <Badge colorScheme="red" size="sm">필수</Badge>
                              )}
                              <Badge 
                                colorScheme="gray" 
                                size="sm" 
                                variant="outline"
                              >
                                {input.type}
                              </Badge>
                            </HStack>
                          </FormLabel>
                          
                          <Input
                            value={inputValues[input.name] || ''}
                            onChange={(e) => handleInputChange(input.name, e.target.value)}
                            placeholder={input.description || `${input.name} 값을 입력하세요`}
                            size="sm"
                          />
                          
                          {input.description && (
                            <FormHelperText fontSize="xs">
                              {input.description}
                            </FormHelperText>
                          )}
                        </FormControl>
                      ))
                    )}

                    {/* 실행 버튼 */}
                    <Button
                      leftIcon={isLoading ? <Spinner size="sm" /> : <FiZap />}
                      colorScheme="blue"
                      onClick={handleApiTest}
                      isLoading={isLoading}
                      loadingText="실행 중..."
                      size="lg"
                      w="full"
                    >
                      API 실행
                    </Button>
                  </VStack>
                </CardBody>
              </Card>

              {/* Python 코드 생성 */}
              <Card mt={4}>
                <CardHeader>
                  <HStack justify="space-between">
                    <Text fontSize="md" fontWeight="bold">
                      🐍 Python 코드
                    </Text>
                    <Button
                      leftIcon={<FiCopy />}
                      size="xs"
                      variant="outline"
                      onClick={() => copyToClipboard(generatePythonCode())}
                    >
                      복사
                    </Button>
                  </HStack>
                </CardHeader>
                
                <CardBody>
                  <Code
                    display="block"
                    whiteSpace="pre"
                    fontSize="xs"
                    p={3}
                    bg={codeBg}
                    borderRadius="md"
                    maxH="200px"
                    overflowY="auto"
                  >
                    {generatePythonCode()}
                  </Code>
                </CardBody>
              </Card>
            </GridItem>

            {/* 오른쪽: 결과 표시 */}
            <GridItem>
              <Card h="fit-content">
                <CardHeader>
                  <HStack justify="space-between">
                    <Text fontSize="lg" fontWeight="bold">
                      📊 실행 결과
                    </Text>
                    {testResult && (
                      <HStack spacing={2}>
                        <Button
                          leftIcon={<FiCopy />}
                          size="xs"
                          variant="outline"
                          onClick={() => copyToClipboard(JSON.stringify(testResult.data, null, 2))}
                        >
                          복사
                        </Button>
                        <Button
                          leftIcon={<FiDownload />}
                          size="xs"
                          variant="outline"
                          onClick={downloadResult}
                        >
                          다운로드
                        </Button>
                      </HStack>
                    )}
                  </HStack>
                </CardHeader>
                
                <CardBody>
                  {isLoading && (
                    <VStack spacing={3}>
                      <Spinner size="lg" color="blue.500" />
                      <Text>API 호출 중...</Text>
                      <Progress size="sm" isIndeterminate colorScheme="blue" w="full" />
                    </VStack>
                  )}

                  {error && (
                    <Alert status="error" borderRadius="md">
                      <AlertIcon />
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="bold">오류 발생</Text>
                        <Text fontSize="sm" whiteSpace="pre-wrap">
                          {error}
                        </Text>
                      </VStack>
                    </Alert>
                  )}

                  {testResult && (
                    <VStack spacing={4} align="stretch">
                      {/* 성공/실패 상태 */}
                      <HStack>
                        {testResult.success ? (
                          <Badge colorScheme="green" p={2}>
                            <HStack>
                              <FiCheck />
                              <Text>성공</Text>
                            </HStack>
                          </Badge>
                        ) : (
                          <Badge colorScheme="red" p={2}>
                            <HStack>
                              <FiX />
                              <Text>실패</Text>
                            </HStack>
                          </Badge>
                        )}
                        
                        {testResult.status && (
                          <Badge variant="outline">
                            HTTP {testResult.status}
                          </Badge>
                        )}
                        
                        {testResult.duration && (
                          <Badge variant="outline">
                            {testResult.duration}ms
                          </Badge>
                        )}
                      </HStack>

                      {/* 응답 데이터 */}
                      {testResult.success && testResult.data && (
                        <Box>
                          <HStack justify="space-between" mb={2}>
                            <Text fontSize="sm" fontWeight="bold">응답 데이터</Text>
                            <Button
                              leftIcon={showRawResponse ? <FiEyeOff /> : <FiEye />}
                              size="xs"
                              variant="ghost"
                              onClick={() => setShowRawResponse(!showRawResponse)}
                            >
                              {showRawResponse ? '정리뷰' : '원본뷰'}
                            </Button>
                          </HStack>
                          
                          <Code
                            display="block"
                            whiteSpace="pre-wrap"
                            fontSize="xs"
                            p={3}
                            bg={codeBg}
                            borderRadius="md"
                            maxH="400px"
                            overflowY="auto"
                            w="full"
                          >
                            {showRawResponse 
                              ? JSON.stringify(testResult.data, null, 2)
                              : JSON.stringify(testResult.data, null, 2).slice(0, 1000) + 
                                (JSON.stringify(testResult.data).length > 1000 ? '\n...(더보기)' : '')
                            }
                          </Code>
                        </Box>
                      )}

                      {/* 메타정보 */}
                      {testResult.timestamp && (
                        <Text fontSize="xs" color="gray.500">
                          실행시간: {testResult.timestamp}
                        </Text>
                      )}
                    </VStack>
                  )}

                  {!isLoading && !testResult && !error && (
                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      <AlertDescription>
                        파라미터를 설정하고 API 실행 버튼을 클릭하세요.
                      </AlertDescription>
                    </Alert>
                  )}
                </CardBody>
              </Card>
            </GridItem>
          </Grid>
        </ModalBody>

        <ModalFooter borderTop="1px" borderColor={borderColor}>
          <HStack spacing={3}>
            <Text fontSize="sm" color="gray.500">
              📡 {pkg.fullUrl}
            </Text>
            <Spacer />
            <Button variant="ghost" onClick={onClose}>
              닫기
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ApiTestModalEnhanced;
