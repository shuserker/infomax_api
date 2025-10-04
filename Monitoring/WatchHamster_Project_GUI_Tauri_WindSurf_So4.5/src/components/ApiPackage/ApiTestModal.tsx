import React, { useState, useEffect } from 'react'
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
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Spinner,
  useToast,
  Grid,
  GridItem,
  Card,
  CardBody,
  Flex,
  Spacer,
  useColorModeValue,
  Switch,
  Select
} from '@chakra-ui/react'
import { FiCopy, FiDownload, FiPlay } from 'react-icons/fi'
import { parameterDefaultManager } from '../../utils/parameterDefaultManager'
import { getCrawledPythonCode } from '../../utils/apiCrawlingMapper'

interface ApiPackage {
  id: string
  category: string
  itemName: string
  fullName: string
  urlPath: string
  baseUrl: string
  fullUrl: string
  inputs: ApiParameter[]
  outputs: string[]
  description?: string
  tags?: string[]
  status: 'active' | 'inactive' | 'deprecated'
  isFavorite?: boolean
  lastUsed?: string
  usageCount?: number
}

interface ApiParameter {
  name: string
  type: 'String' | 'Number' | 'Boolean' | 'Date'
  required: boolean
  description?: string
  defaultValue?: string
}

interface ApiTestModalProps {
  isOpen: boolean
  onClose: () => void
  package: ApiPackage | null
  apiToken: string
}

const ApiTestModal: React.FC<ApiTestModalProps> = ({
  isOpen,
  onClose,
  package: pkg,
  apiToken
}) => {
  const [inputValues, setInputValues] = useState<{[key: string]: string}>({})
  const [isLoading, setIsLoading] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const toast = useToast()
  const codeColor = useColorModeValue('gray.50', 'gray.700')

  // 모달이 열릴 때 기본값 설정 (기본값 관리자 사용)
  useEffect(() => {
    if (pkg && isOpen) {
      const defaultValues: {[key: string]: string} = {}
      
      // 기본값 관리자에서 저장된 기본값 로드
      const apiDefaults = parameterDefaultManager.getApiDefaults(pkg.urlPath)
      
      pkg.inputs.forEach(input => {
        // 저장된 기본값이 있으면 사용, 없으면 기본값 사용
        const savedDefault = apiDefaults[input.name]
        if (savedDefault !== undefined) {
          defaultValues[input.name] = savedDefault
        } else {
          // 기존 하드코딩된 기본값을 fallback으로 사용
          defaultValues[input.name] = input.defaultValue || getDefaultValue(pkg.urlPath, input.name)
        }
      })
      
      setInputValues(defaultValues)
      setTestResult(null)
      setError('')
    }
  }, [pkg, isOpen, refreshTrigger])

  // 기존 하드코딩된 기본값 (fallback용)
  const getDefaultValue = (apiPath: string, paramName: string): string => {
    if (apiPath === 'bond/market/mn_hist') {
      switch (paramName) {
        case 'stdcd': return 'KR103502GE97';
        case 'market': return '장외';
        case 'startDate': return '20250401';
        case 'endDate': return '20250401';
        default: return '';
      }
    } else {
      switch (paramName) {
        case 'stdcd': return 'KR101501DA32';
        case 'code': return '005930';
        case 'type': return 'EF';
        case 'bonddate': return '20250401';
        default: return '';
      }
    }
  }

  const handleInputChange = (paramName: string, value: string) => {
    setInputValues(prev => ({
      ...prev,
      [paramName]: value
    }))
  }

  const handleApiTest = async () => {
    if (!pkg || !apiToken) {
      toast({
        title: '설정 오류',
        description: 'API 패키지 정보 또는 토큰이 없습니다.',
        status: 'warning',
        duration: 3000
      })
      return
    }

    setIsLoading(true)
    setError('')
    setTestResult(null)

    try {
      // 필수 파라미터 체크
      const missingParams = pkg.inputs
        .filter(input => input.required && !inputValues[input.name]?.trim())
        .map(input => input.name)

      if (missingParams.length > 0) {
        throw new Error(`필수 파라미터가 누락되었습니다: ${missingParams.join(', ')}`)
      }

      // 패턴별 파라미터 포함 규칙
      const params: {[key: string]: string} = {}
      Object.entries(inputValues).forEach(([key, value]) => {
        if (pkg.urlPath === 'bond/market/mn_hist' || pkg.urlPath === 'stock/code') {
          // 채권 체결정보, 주식 코드 검색은 모든 파라미터 포함 (빈 문자열도)
          params[key] = value || ''
        } else {
          // 다른 API는 값이 있는 것만 포함
          if (value?.trim()) {
            params[key] = value.trim()
          }
        }
      })

      // 로컬 Python 백엔드 서버를 통한 프록시 호출
      const localProxyUrl = `http://localhost:8001/api/infomax/${pkg.urlPath}`
      
      console.log('🚀 로컬 Python 서버를 통한 API 호출:', {
        proxyUrl: localProxyUrl,
        targetApi: pkg.fullUrl,
        params,
        token: apiToken ? `${apiToken.slice(0, 6)}...` : 'None'
      })

      // URLSearchParams로 쿼리 파라미터 생성
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value))
        }
      })

      const finalUrl = searchParams.toString() 
        ? `${localProxyUrl}?${searchParams.toString()}`
        : localProxyUrl

      const response = await fetch(finalUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      })

      console.log('📊 응답 상태:', response.status, response.statusText)

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.message || errorData.error || errorMessage
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      const responseData = await response.json()
      console.log('✅ API 응답 데이터:', responseData)

      setTestResult({
        success: true,
        data: responseData,
        status: response.status,
        url: finalUrl,
        timestamp: new Date().toLocaleString('ko-KR')
      })
      
      toast({
        title: '🎉 Python 실행 성공!',
        description: `${pkg.fullName} API가 성공적으로 실행되었습니다.`,
        status: 'success',
        duration: 3000
      })
    } catch (err) {
      let errorMessage = '알 수 없는 오류가 발생했습니다.'
      
      if (err instanceof TypeError) {
        if (err.message.includes('Failed to fetch') || err.message.includes('Load failed')) {
          errorMessage = '🔌 로컬 Python 서버 연결 실패!\n\n해결 방법:\n1. 워치햄스터 백엔드 서버가 실행 중인지 확인\n2. http://localhost:8001 접속 가능한지 확인\n3. 서버 재시작 후 다시 시도\n\n💡 백엔드 서버를 먼저 실행해주세요!'
        } else {
          errorMessage = `네트워크 오류: ${err.message}`
        }
      } else if (err instanceof Error) {
        errorMessage = err.message
      }
      
      console.error('❌ 로컬 Python 서버 호출 오류:', err)
      setError(errorMessage)
      
      toast({
        title: '🔌 로컬 서버 연결 실패',
        description: err instanceof TypeError && err.message.includes('Failed to fetch') 
          ? '워치햄스터 백엔드 서버(localhost:8001)에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요!'
          : errorMessage,
        status: 'error',
        duration: 7000
      })
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      toast({
        title: '복사 완료',
        description: '클립보드에 복사되었습니다.',
        status: 'success',
        duration: 2000
      })
    })
  }

  // 파이썬 코드 생성 함수 (크롤링 정보 활용)
  const generatePythonCode = () => {
    if (!pkg) return ''
    
    // 크롤링된 Python 코드 확인
    const crawledCode = getCrawledPythonCode(pkg.urlPath)
    
    if (crawledCode) {
      // 크롤링된 코드가 있는 경우, 파라미터 값만 실제 입력값으로 교체
      let updatedCode = crawledCode
      
      // 토큰 교체
      if (apiToken) {
        updatedCode = updatedCode.replace('bearer TOKEN', `bearer ${apiToken}`)
        updatedCode = updatedCode.replace('TOKEN', apiToken)
      }
      
      // 파라미터 값들 교체
      Object.entries(inputValues).forEach(([key, value]) => {
        if (value?.trim()) {
          const pattern = new RegExp(`"${key}"\\s*:\\s*"[^"]*"`, 'g')
          updatedCode = updatedCode.replace(pattern, `"${key}":"${value}"`)
        }
      })
      
      return updatedCode
    }
    
    // 크롤링된 코드가 없는 경우, 기본 코드 생성
    const params: {[key: string]: string} = {}
    Object.entries(inputValues).forEach(([key, value]) => {
      if (pkg.urlPath === 'bond/market/mn_hist' || pkg.urlPath === 'stock/code') {
        // 채권 체결정보 API와 주식 코드 검색은 모든 파라미터 포함 (빈 문자열도)
        params[key] = value || ''
      } else {
        // 다른 API는 값이 있는 것만 포함
        if (value?.trim()) {
          params[key] = value.trim()
        }
      }
    })

    // 파라미터 문자열 생성 (가독성 좋은 멀티라인 포맷)
    const paramEntries = Object.entries(params)
    let paramStr = ''
    if (paramEntries.length > 0) {
      if (paramEntries.length === 1) {
        paramStr = `"${paramEntries[0][0]}": "${paramEntries[0][1]}"`
      } else {
        const paramLines = paramEntries.map(([key, value]) => `    "${key}": "${value}"`)
        paramStr = '\n' + paramLines.join(',\n') + '\n'
      }
    }

    const pythonCode = `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoMax API 호출 스크립트
API: ${pkg.fullName}
URL: ${pkg.fullUrl}
Generated: ${new Date().toLocaleString('ko-KR')}
"""

import sys
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# SSL 경고 비활성화
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# API 설정
API_URL = '${pkg.fullUrl}'
API_TOKEN = '${apiToken || 'YOUR_API_TOKEN_HERE'}'

# 세션 설정
session = requests.Session()
session.verify = False  # SSL 인증 무시 (개발/테스트용)

# 요청 파라미터
params = {${paramStr}}

# 요청 헤더
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json',
    'User-Agent': 'InfoMax-API-Client/1.0'
}

try:
    print(f"🚀 API 호출 시작: {API_URL}")
    print(f"📤 파라미터: {json.dumps(params, ensure_ascii=False, indent=2)}")
    print("-" * 50)
    
    # API 호출
    response = session.get(API_URL, params=params, headers=headers, timeout=30)
    
    # 응답 상태 확인
    print(f"📊 응답 상태: {response.status_code} {response.reason}")
    
    if response.status_code == 200:
        # 성공 응답 처리
        data = response.json()
        print("✅ API 호출 성공!")
        print("📥 응답 데이터:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 결과 요약
        if isinstance(data, dict) and 'results' in data:
            results = data.get('results', [])
            if isinstance(results, list):
                print(f"\\n📈 결과 요약: 총 {len(results)}개 항목 조회됨")
    else:
        # 오류 응답 처리
        print("❌ API 호출 실패!")
        try:
            error_data = response.json()
            print("🔍 오류 상세:")
            print(json.dumps(error_data, ensure_ascii=False, indent=2))
        except:
            print(f"🔍 오류 내용: {response.text}")

except requests.exceptions.Timeout:
    print("⏰ 요청 시간 초과 (30초)")
except requests.exceptions.ConnectionError:
    print("🔌 연결 오류 - 네트워크를 확인해주세요")
except requests.exceptions.RequestException as e:
    print(f"🚫 요청 오류: {e}")
except json.JSONDecodeError:
    print("📄 JSON 파싱 오류 - 응답이 올바른 JSON 형식이 아닙니다")
except Exception as e:
    print(f"🔥 예상치 못한 오류: {e}")
finally:
    session.close()
    print("\\n🏁 API 호출 완료")`

    return pythonCode
  }

  const downloadResult = () => {
    if (!testResult?.data || !pkg) return
    
    const blob = new Blob([JSON.stringify(testResult.data, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${pkg.itemName}_result_${new Date().getTime()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: '다운로드 완료',
      description: 'JSON 파일이 다운로드되었습니다.',
      status: 'success',
      duration: 2000
    })
  }

  if (!pkg) return null

  return (
    <>
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>
          <VStack spacing={2} align="start">
            <HStack justify="space-between" w="full">
              <HStack>
                <Badge colorScheme="blue" variant="subtle">{pkg.category}</Badge>
                <Text fontSize="lg" fontWeight="bold">{pkg.fullName}</Text>
              </HStack>
            </HStack>
            <Text fontSize="sm" color="gray.600">
              {pkg.description || 'API 테스트 및 결과 확인'}
            </Text>
            <Code fontSize="xs" p={1} borderRadius="md">
              {pkg.fullUrl}
            </Code>
          </VStack>
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          <Tabs variant="enclosed" colorScheme="blue">
            <TabList>
              <Tab>⚙️ 파라미터 설정</Tab>
              <Tab>🐍 파이썬 코드</Tab>
              <Tab>🚀 Python 실행</Tab>
              <Tab>📤 응답 결과</Tab>
              <Tab>📋 요청 정보</Tab>
            </TabList>

            <TabPanels>
              {/* 파라미터 설정 탭 */}
              <TabPanel>
                <VStack spacing={6} align="stretch">
                  <Card>
                    <CardBody>
                      <VStack spacing={4} align="stretch">
                        <Text fontWeight="bold" fontSize="md">📝 입력 파라미터</Text>
                        
                        {pkg.inputs.length === 0 ? (
                          <Alert status="info">
                            <AlertIcon />
                            이 API는 입력 파라미터가 필요하지 않습니다.
                          </Alert>
                        ) : (
                          <VStack spacing={4} align="stretch">
                            {pkg.inputs.map((input, index) => {
                              const paramDefault = parameterDefaultManager.getParameterDefault(pkg.urlPath, input.name);
                              const autoRule = parameterDefaultManager.getAllDefaults()?.[pkg.urlPath]?.[input.name]?.autoUpdateRule;
                              const isAutoManaged = parameterDefaultManager.getAllDefaults()?.[pkg.urlPath]?.[input.name]?.isAutoManaged || false;
                              
                              return (
                                <Box key={index} p={4} border="1px" borderColor="gray.200" borderRadius="md">
                                  <Grid templateColumns="1fr" gap={4} alignItems="start">
                                    {/* 기본 파라미터 입력 */}
                                    <GridItem>
                                      <FormControl isRequired={input.required}>
                                        <FormLabel fontSize="sm">
                                          <HStack spacing={2}>
                                            <Text>{input.name}</Text>
                                            <Badge 
                                              size="xs" 
                                              colorScheme={input.required ? 'red' : 'gray'}
                                            >
                                              {input.type}
                                            </Badge>
                                            {input.required && (
                                              <Badge size="xs" colorScheme="red">필수</Badge>
                                            )}
                                            {isAutoManaged && (
                                              <Badge size="xs" colorScheme="green" variant="subtle">자동관리</Badge>
                                            )}
                                          </HStack>
                                        </FormLabel>
                                        <Input
                                          size="sm"
                                          value={inputValues[input.name] || ''}
                                          onChange={(e) => handleInputChange(input.name, e.target.value)}
                                          placeholder={input.description || `${input.name} 입력`}
                                        />
                                        {input.description && (
                                          <Text fontSize="xs" color="gray.500" mt={1}>
                                            {input.description}
                                          </Text>
                                        )}
                                      </FormControl>
                                    </GridItem>
                                    
                                    {/* 자동갱신 설정 */}
                                    <GridItem>
                                      <VStack spacing={2} align="stretch">
                                        <HStack justify="space-between">
                                          <Text fontSize="xs" color="gray.600">자동갱신</Text>
                                          <Switch 
                                            size="sm"
                                            isChecked={isAutoManaged}
                                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                              const newAutoManaged = e.target.checked;
                                              if (newAutoManaged) {
                                                parameterDefaultManager.setParameterDefault(
                                                  pkg.urlPath,
                                                  input.name,
                                                  inputValues[input.name] || '',
                                                  true,
                                                  {
                                                    enabled: true,
                                                    schedule: { daysOfWeek: [1, 2, 3, 4, 5], timeHour: 1, timeMinute: 0 },
                                                    updateLogic: 'current_date_minus_1'
                                                  }
                                                );
                                                setRefreshTrigger(prev => prev + 1);
                                              } else {
                                                parameterDefaultManager.setParameterDefault(
                                                  pkg.urlPath,
                                                  input.name,
                                                  inputValues[input.name] || '',
                                                  false
                                                );
                                                setRefreshTrigger(prev => prev + 1);
                                              }
                                            }}
                                          />
                                        </HStack>
                                        
                                        {isAutoManaged && (
                                          <VStack spacing={3} align="stretch" p={3} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                                            {/* 0️⃣ 교체할 값 선택 */}
                                            <VStack spacing={2} align="stretch">
                                              <Text fontSize="xs" fontWeight="bold" color="red.700">📝 교체할 값 (YYYYMMDD)</Text>
                                              <HStack spacing={2}>
                                                <Input
                                                  size="xs"
                                                  placeholder="D-1"
                                                  value={(() => {
                                                    const logic = autoRule?.updateLogic || 'current_date_minus_1';
                                                    if (logic === 'current_date') return 'D+0';
                                                    if (logic.startsWith('current_date_minus_')) return `D-${logic.split('_')[3]}`;
                                                    if (logic.startsWith('current_date_plus_')) return `D+${logic.split('_')[3]}`;
                                                    return 'D-1';
                                                  })()}
                                                  onChange={(e) => {
                                                    const value = e.target.value.trim();
                                                    let updateLogic = 'current_date_minus_1';
                                                    
                                                    // D+n 또는 D-n 형태 파싱
                                                    const match = value.match(/^D([+-])(\d+)$/i);
                                                    if (match) {
                                                      const sign = match[1];
                                                      const days = match[2];
                                                      if (sign === '+' && days === '0') {
                                                        updateLogic = 'current_date';
                                                      } else if (sign === '+') {
                                                        updateLogic = `current_date_plus_${days}`;
                                                      } else if (sign === '-') {
                                                        updateLogic = `current_date_minus_${days}`;
                                                      }
                                                    }
                                                    
                                                    const currentDefaults = parameterDefaultManager.getAllDefaults()?.[pkg.urlPath]?.[input.name];
                                                    if (currentDefaults?.autoUpdateRule) {
                                                      parameterDefaultManager.setParameterDefault(
                                                        pkg.urlPath,
                                                        input.name,
                                                        inputValues[input.name] || '',
                                                        true,
                                                        {
                                                          ...currentDefaults.autoUpdateRule,
                                                          updateLogic: updateLogic as any
                                                        }
                                                      );
                                                      setRefreshTrigger(prev => prev + 1);
                                                    }
                                                  }}
                                                  w="80px"
                                                />
                                                <Text fontSize="xs" color="gray.500">
                                                  예: D-1 (어제), D+0 (오늘), D+7 (일주일 후)
                                                </Text>
                                              </HStack>
                                            </VStack>

                                            {/* 1️⃣ 주기 선택 */}
                                            <VStack spacing={2} align="stretch">
                                              <Text fontSize="xs" fontWeight="bold" color="blue.700">1️⃣ 갱신 주기</Text>
                                              <Select
                                                size="xs"
                                                value={(() => {
                                                  const logic = autoRule?.updateLogic;
                                                  if (!logic || logic.includes('current_date')) return 'daily';
                                                  if (logic.includes('week')) return 'weekly';
                                                  if (logic.includes('month')) return 'monthly';
                                                  if (logic.includes('quarter')) return 'quarterly';
                                                  if (logic.includes('year')) return 'yearly';
                                                  return 'daily';
                                                })()}
                                                onChange={(e) => {
                                                  const currentDefaults = parameterDefaultManager.getAllDefaults()?.[pkg.urlPath]?.[input.name];
                                                  if (currentDefaults) {
                                                    let newLogic = 'current_date_minus_1';
                                                    let newSchedule = { daysOfWeek: [1, 2, 3, 4, 5], timeHour: 1, timeMinute: 0 };
                                                    
                                                    switch (e.target.value) {
                                                      case 'daily':
                                                        newLogic = 'current_date_minus_1';
                                                        newSchedule.daysOfWeek = [0, 1, 2, 3, 4, 5, 6];
                                                        break;
                                                      case 'weekly':
                                                        newLogic = 'last_week_start';
                                                        newSchedule.daysOfWeek = [1];
                                                        break;
                                                      case 'monthly':
                                                        newLogic = 'last_month_start';
                                                        newSchedule.daysOfWeek = [1];
                                                        break;
                                                      case 'quarterly':
                                                        newLogic = 'last_quarter_start';
                                                        newSchedule.daysOfWeek = [1];
                                                        break;
                                                      case 'yearly':
                                                        newLogic = 'last_year_start';
                                                        newSchedule.daysOfWeek = [1];
                                                        break;
                                                    }
                                                    
                                                    parameterDefaultManager.setParameterDefault(
                                                      pkg.urlPath,
                                                      input.name,
                                                      inputValues[input.name] || '',
                                                      true,
                                                      {
                                                        enabled: true,
                                                        schedule: newSchedule,
                                                        updateLogic: newLogic as any
                                                      }
                                                    );
                                                    setRefreshTrigger(prev => prev + 1);
                                                  }
                                                }}
                                              >
                                                <option value="daily">📅 일 (매일)</option>
                                                <option value="weekly">📅 주 (매주)</option>
                                                <option value="monthly">📅 월 (매월)</option>
                                                <option value="quarterly">📅 분기 (분기별)</option>
                                                <option value="yearly">📅 연간 (매년)</option>
                                              </Select>
                                            </VStack>

                                            {/* 2️⃣ 세부 설정 - 요일 선택 */}
                                            <VStack spacing={2} align="stretch">
                                              <Text fontSize="xs" fontWeight="bold" color="green.700">2️⃣ 세부 설정</Text>
                                              <HStack wrap="wrap" spacing={1}>
                                                {[1, 2, 3, 4, 5, 6, 0].map((dayNum) => {
                                                  const dayNames = ['일', '월', '화', '수', '목', '금', '토'];
                                                  const isSelected = autoRule?.schedule.daysOfWeek.includes(dayNum) || false;
                                                  const isDaily = !autoRule?.updateLogic || autoRule.updateLogic.includes('current_date');
                                                  
                                                  return (
                                                    <Button
                                                      key={dayNum}
                                                      size="xs"
                                                      variant={isSelected ? 'solid' : 'outline'}
                                                      colorScheme={isSelected ? 'blue' : 'gray'}
                                                      isDisabled={isDaily}
                                                      onClick={() => {
                                                        if (isDaily) return;
                                                        
                                                        const currentDefaults = parameterDefaultManager.getAllDefaults()?.[pkg.urlPath]?.[input.name];
                                                        if (currentDefaults?.autoUpdateRule) {
                                                          const currentDays = currentDefaults.autoUpdateRule.schedule.daysOfWeek;
                                                          const newDays = currentDays.includes(dayNum)
                                                            ? currentDays.filter(d => d !== dayNum)
                                                            : [...currentDays, dayNum];
                                                          
                                                          parameterDefaultManager.setParameterDefault(
                                                            pkg.urlPath,
                                                            input.name,
                                                            inputValues[input.name] || '',
                                                            true,
                                                            {
                                                              ...currentDefaults.autoUpdateRule,
                                                              schedule: {
                                                                ...currentDefaults.autoUpdateRule.schedule,
                                                                daysOfWeek: newDays
                                                              }
                                                            }
                                                          );
                                                          setRefreshTrigger(prev => prev + 1);
                                                        }
                                                      }}
                                                    >
                                                      {dayNames[dayNum]}
                                                    </Button>
                                                  );
                                                })}
                                              </HStack>
                                              {((() => {
                                                const logic = autoRule?.updateLogic;
                                                return !logic || logic.includes('current_date');
                                              })()) && (
                                                <Text fontSize="xs" color="orange.600">📌 일 단위는 매일 실행되므로 요일 조정이 불가합니다</Text>
                                              )}
                                            </VStack>

                                            {/* 3️⃣ 시간 설정 */}
                                            <VStack spacing={2} align="stretch">
                                              <Text fontSize="xs" fontWeight="bold" color="purple.700">3️⃣ 실행 시간</Text>
                                              <HStack>
                                                <Select
                                                  size="xs"
                                                  flex={1}
                                                  value={autoRule?.schedule.timeHour || 1}
                                                  onChange={(e) => {
                                                    const currentDefaults = parameterDefaultManager.getAllDefaults()?.[pkg.urlPath]?.[input.name];
                                                    if (currentDefaults?.autoUpdateRule) {
                                                      parameterDefaultManager.setParameterDefault(
                                                        pkg.urlPath,
                                                        input.name,
                                                        inputValues[input.name] || '',
                                                        true,
                                                        {
                                                          ...currentDefaults.autoUpdateRule,
                                                          schedule: {
                                                            ...currentDefaults.autoUpdateRule.schedule,
                                                            timeHour: parseInt(e.target.value)
                                                          }
                                                        }
                                                      );
                                                      setRefreshTrigger(prev => prev + 1);
                                                    }
                                                  }}
                                                >
                                                  {Array.from({length: 24}, (_, i) => (
                                                    <option key={i} value={i}>{String(i).padStart(2, '0')}시</option>
                                                  ))}
                                                </Select>
                                                <Select
                                                  size="xs"
                                                  flex={1}
                                                  value={autoRule?.schedule.timeMinute || 0}
                                                  onChange={(e) => {
                                                    const currentDefaults = parameterDefaultManager.getAllDefaults()?.[pkg.urlPath]?.[input.name];
                                                    if (currentDefaults?.autoUpdateRule) {
                                                      parameterDefaultManager.setParameterDefault(
                                                        pkg.urlPath,
                                                        input.name,
                                                        inputValues[input.name] || '',
                                                        true,
                                                        {
                                                          ...currentDefaults.autoUpdateRule,
                                                          schedule: {
                                                            ...currentDefaults.autoUpdateRule.schedule,
                                                            timeMinute: parseInt(e.target.value)
                                                          }
                                                        }
                                                      );
                                                      setRefreshTrigger(prev => prev + 1);
                                                    }
                                                  }}
                                                >
                                                  {[0, 15, 30, 45].map(minute => (
                                                    <option key={minute} value={minute}>{String(minute).padStart(2, '0')}분</option>
                                                  ))}
                                                </Select>
                                              </HStack>
                                            </VStack>
                                            
                                            <Text fontSize="xs" color="gray.500">
                                              {autoRule?.updateLogic === 'auto_smart_date' && '🤖 시간과 요일에 따라 자동 선택'}
                                              {autoRule?.updateLogic === 'rotate_keywords' && '🔁 키워드를 매일 순환'}
                                              {autoRule?.updateLogic === 'last_week_start' && '📅 매주 월요일에 갱신'}
                                            </Text>
                                          </VStack>
                                        )}
                                      </VStack>
                                    </GridItem>
                                  </Grid>
                                </Box>
                              );
                            })}
                          </VStack>
                        )}
                      </VStack>
                    </CardBody>
                  </Card>

                  <Flex>
                    <Button
                      leftIcon={isLoading ? <Spinner size="xs" /> : <FiPlay />}
                      colorScheme="blue"
                      onClick={handleApiTest}
                      isLoading={isLoading}
                      loadingText="호출 중..."
                      size="lg"
                      isDisabled={!apiToken}
                    >
                      API 호출 테스트
                    </Button>
                    <Spacer />
                    {!apiToken && (
                      <Alert status="warning" size="sm" maxW="400px">
                        <AlertIcon />
                        <Text fontSize="xs">API 토큰을 먼저 설정해주세요.</Text>
                      </Alert>
                    )}
                  </Flex>
                </VStack>
              </TabPanel>

              {/* 파이썬 코드 탭 */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between">
                    <HStack spacing={2}>
                      <Text fontWeight="bold" fontSize="md">🐍 생성된 파이썬 코드</Text>
                      <Badge colorScheme="orange" variant="outline">바로 실행 가능</Badge>
                    </HStack>
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        leftIcon={<FiCopy />}
                        onClick={() => copyToClipboard(generatePythonCode())}
                        colorScheme="blue"
                      >
                        코드 복사
                      </Button>
                      <Button
                        size="sm"
                        leftIcon={<FiDownload />}
                        onClick={() => {
                          const blob = new Blob([generatePythonCode()], { type: 'text/plain' })
                          const url = URL.createObjectURL(blob)
                          const a = document.createElement('a')
                          a.href = url
                          a.download = `${pkg?.itemName || 'api'}_test.py`
                          document.body.appendChild(a)
                          a.click()
                          document.body.removeChild(a)
                          URL.revokeObjectURL(url)
                          toast({
                            title: '다운로드 완료',
                            description: 'Python 파일이 다운로드되었습니다.',
                            status: 'success',
                            duration: 2000
                          })
                        }}
                      >
                        .py 다운로드
                      </Button>
                    </HStack>
                  </HStack>

                  <Alert status="info" borderRadius="md">
                    <AlertIcon />
                    <VStack spacing={1} align="start" fontSize="sm">
                      <Text><strong>사용법:</strong></Text>
                      <Text>1. 아래 코드를 복사하여 Jupyter Lab, VS Code, PyCharm 등에서 실행</Text>
                      <Text>2. requests 라이브러리 필요: <code>pip install requests</code></Text>
                      <Text>3. SSL 인증 무효화로 HTTPS 문제 해결</Text>
                    </VStack>
                  </Alert>

                  <Box
                    bg={codeColor}
                    p={4}
                    borderRadius="md"
                    border="1px solid"
                    borderColor="gray.200"
                    _dark={{ borderColor: "gray.600" }}
                    maxH="500px"
                    overflowY="auto"
                  >
                    <Code
                      fontSize="sm"
                      whiteSpace="pre-wrap"
                      bg="transparent"
                      p={0}
                      w="100%"
                      display="block"
                      fontFamily="'Monaco', 'Menlo', 'Ubuntu Mono', monospace"
                      overflowX="auto"
                      wordBreak="break-word"
                      lineHeight="1.5"
                    >
                      {generatePythonCode()}
                    </Code>
                  </Box>

                  <Alert status="success" borderRadius="md">
                    <AlertIcon />
                    <Text fontSize="sm">
                      이 코드는 파라미터 값이 변경될 때마다 자동으로 업데이트됩니다. 
                      Jupyter Lab에서 실행하면 즉시 결과를 확인할 수 있습니다! 🚀
                    </Text>
                  </Alert>
                </VStack>
              </TabPanel>

              {/* Python 실행 탭 */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between">
                    <HStack spacing={2}>
                      <Text fontWeight="bold" fontSize="md">🚀 브라우저에서 Python 실행</Text>
                      <Badge colorScheme="green" variant="solid">실시간 실행</Badge>
                    </HStack>
                    <Button
                      leftIcon={<FiPlay />}
                      onClick={handleApiTest}
                      colorScheme="green"
                      isLoading={isLoading}
                      loadingText="실행 중..."
                    >
                      Python 코드 실행
                    </Button>
                  </HStack>

                  <Alert status="success" borderRadius="md">
                    <AlertIcon />
                    <VStack spacing={1} align="start">
                      <Text fontSize="sm" fontWeight="bold">
                        🚀 로컬 Python 서버를 통한 실행
                      </Text>
                      <Text fontSize="xs">
                        워치햄스터 백엔드 서버(localhost:8001)를 통해 CORS 문제 없이 안전하게 API를 호출합니다!
                      </Text>
                    </VStack>
                  </Alert>

                  {/* Python 코드 미리보기 */}
                  <Box
                    bg="gray.50"
                    _dark={{ bg: "gray.800" }}
                    p={3}
                    borderRadius="md"
                    border="1px dashed"
                    borderColor="gray.300"
                    _dark={{ borderColor: "gray.600" }}
                  >
                    <Text fontSize="xs" color="gray.600" _dark={{ color: "gray.400" }} mb={2}>
                      실행될 Python 코드:
                    </Text>
                    <Code 
                      fontSize="xs" 
                      whiteSpace="pre-wrap" 
                      bg="transparent" 
                      p={0}
                      overflowX="auto"
                      wordBreak="break-word"
                      lineHeight="1.4"
                    >
                      {generatePythonCode().split('\n').slice(0, 8).join('\n')}...
                    </Code>
                  </Box>

                  {/* 실행 결과 */}
                  {testResult && (
                    <VStack spacing={3} align="stretch">
                      <HStack>
                        <Text fontWeight="bold" fontSize="md">📊 Python 실행 결과:</Text>
                        <Badge colorScheme="green" variant="solid">SUCCESS</Badge>
                      </HStack>
                      
                      <Alert status="success" borderRadius="md">
                        <AlertIcon />
                        <Text fontSize="sm">
                          Python 코드가 성공적으로 실행되었습니다! 아래는 실제 결과입니다.
                        </Text>
                      </Alert>

                      <Box
                        bg={codeColor}
                        p={4}
                        borderRadius="md"
                        border="1px solid"
                        borderColor="green.200"
                        _dark={{ borderColor: "green.600" }}
                        maxH="400px"
                        overflowY="auto"
                      >
                        <Code
                          fontSize="sm"
                          whiteSpace="pre-wrap"
                          bg="transparent"
                          p={0}
                          w="100%"
                          display="block"
                          fontFamily="'Monaco', 'Menlo', 'Ubuntu Mono', monospace"
                          color="green.800"
                          _dark={{ color: "green.200" }}
                          overflowX="auto"
                          wordBreak="break-word"
                          lineHeight="1.5"
                        >
                          {JSON.stringify(testResult.data, null, 2)}
                        </Code>
                      </Box>
                    </VStack>
                  )}

                  {error && (
                    <Alert status="error" borderRadius="md">
                      <AlertIcon />
                      <VStack spacing={1} align="start">
                        <Text fontWeight="bold">Python 실행 오류:</Text>
                        <Text fontSize="sm">{error}</Text>
                      </VStack>
                    </Alert>
                  )}
                </VStack>
              </TabPanel>

              {/* 응답 결과 탭 */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  {error ? (
                    <Alert status="error">
                      <AlertIcon />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  ) : testResult ? (
                    <VStack spacing={4} align="stretch">
                      <HStack justify="space-between">
                        <HStack spacing={2}>
                          <Badge colorScheme="green" variant="solid">성공</Badge>
                          <Text fontSize="sm" color="gray.600">
                            {testResult.timestamp}
                          </Text>
                          <Badge variant="outline">HTTP {testResult.status}</Badge>
                        </HStack>
                        <HStack spacing={2}>
                          <Button
                            size="xs"
                            leftIcon={<FiCopy />}
                            onClick={() => copyToClipboard(JSON.stringify(testResult.data, null, 2))}
                          >
                            복사
                          </Button>
                          <Button
                            size="xs"
                            leftIcon={<FiDownload />}
                            onClick={downloadResult}
                          >
                            다운로드
                          </Button>
                        </HStack>
                      </HStack>

                      <Box
                        bg={codeColor}
                        p={4}
                        borderRadius="md"
                        maxH="500px"
                        overflowY="auto"
                      >
                        <Code
                          fontSize="sm"
                          whiteSpace="pre-wrap"
                          bg="transparent"
                          p={0}
                          w="100%"
                          display="block"
                        >
                          {JSON.stringify(testResult.data, null, 2)}
                        </Code>
                      </Box>
                    </VStack>
                  ) : (
                    <Alert status="info">
                      <AlertIcon />
                      API를 호출하면 여기에 결과가 표시됩니다.
                    </Alert>
                  )}
                </VStack>
              </TabPanel>

              {/* 요청 정보 탭 */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <Card>
                    <CardBody>
                      <VStack spacing={3} align="stretch">
                        <Text fontWeight="bold">🌐 요청 URL</Text>
                        <Code p={2} borderRadius="md">
                          {pkg.fullUrl}
                        </Code>
                        
                        <Text fontWeight="bold">📋 현재 파라미터</Text>
                        <Box bg={codeColor} p={3} borderRadius="md">
                          {Object.keys(inputValues).length === 0 ? (
                            <Text fontSize="sm" color="gray.500">설정된 파라미터가 없습니다.</Text>
                          ) : (
                            <Code 
                              fontSize="sm" 
                              bg="transparent" 
                              whiteSpace="pre-wrap"
                              overflowX="auto"
                              wordBreak="break-word"
                              lineHeight="1.5"
                            >
                              {JSON.stringify(inputValues, null, 2)}
                            </Code>
                          )}
                        </Box>

                        <Text fontWeight="bold">🔒 인증 헤더</Text>
                        <Code p={2} borderRadius="md">
                          Authorization: Bearer {apiToken ? '***' + apiToken.slice(-6) : '(토큰 없음)'}
                        </Code>

                        <Text fontWeight="bold">📤 예상 출력 필드</Text>
                        <HStack spacing={2} wrap="wrap">
                          {pkg.outputs.map((output, index) => (
                            <Badge key={index} variant="outline" fontSize="xs">
                              {output}
                            </Badge>
                          ))}
                        </HStack>
                      </VStack>
                    </CardBody>
                  </Card>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            닫기
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  </>
  )
}

export default ApiTestModal
