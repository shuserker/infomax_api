import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Card,
  CardHeader,
  CardBody,
  HStack,
  Badge,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  useDisclosure,
  useToast,
  Alert,
  AlertIcon,
  Flex,
  Spacer,
  Code,
  Tag,
  TagLabel,
  Divider,
  useColorModeValue,
  InputGroup,
  InputRightElement,
  Spinner,
  Collapse,
  AlertDescription
} from '@chakra-ui/react'
import { FiPlus, FiEdit, FiTrash2, FiCode, FiGlobe, FiBookOpen, FiKey, FiPlay, FiEye, FiEyeOff } from 'react-icons/fi'
import ApiTestModal from '../components/ApiPackage/ApiTestModal'

// API 패키지 데이터 타입 정의
interface ApiPackage {
  id: string
  category: string // 대분류
  itemName: string // 항목명
  fullName: string // 풀네임
  urlPath: string // URL 경로
  baseUrl: string // 공통 호출용 URL
  fullUrl: string // 실제 호출 URL (computed)
  inputs: ApiParameter[]
  outputs: string[]
  description?: string
  status: 'active' | 'inactive' | 'deprecated'
  createdAt: string
  updatedAt: string
}

interface ApiParameter {
  name: string
  type: 'String' | 'Number' | 'Boolean' | 'Date'
  required: boolean
  description?: string
  defaultValue?: string
}

const ApiPackageManagement: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()
  const [packages, setPackages] = useState<ApiPackage[]>([])
  const [editingPackage, setEditingPackage] = useState<ApiPackage | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  
  // TOKEN 관리 상태
  const [apiToken, setApiToken] = useState<string>('')
  const [showToken, setShowToken] = useState(false)
  const [testResults, setTestResults] = useState<{[key: string]: any}>({})
  const [testingPackage, setTestingPackage] = useState<string>('')

  // API 테스트 모달 상태
  const { 
    isOpen: isTestModalOpen, 
    onOpen: onTestModalOpen, 
    onClose: onTestModalClose 
  } = useDisclosure()
  const [selectedPackageForTest, setSelectedPackageForTest] = useState<ApiPackage | null>(null)

  // 토큰 저장/불러오기 함수
  const saveTokenToStorage = (token: string) => {
    try {
      localStorage.setItem('infomax_api_token', token)
    } catch (error) {
      console.error('토큰 저장 실패:', error)
    }
  }

  const loadTokenFromStorage = (): string => {
    try {
      return localStorage.getItem('infomax_api_token') || ''
    } catch (error) {
      console.error('토큰 불러오기 실패:', error)
      return ''
    }
  }

  const clearTokenFromStorage = () => {
    try {
      localStorage.removeItem('infomax_api_token')
    } catch (error) {
      console.error('토큰 삭제 실패:', error)
    }
  }

  // 토큰 변경 핸들러
  const handleTokenChange = (newToken: string) => {
    setApiToken(newToken)
    if (newToken.trim()) {
      saveTokenToStorage(newToken.trim())
    } else {
      clearTokenFromStorage()
    }
  }

  // 색상 테마
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  // 초기 데이터 (전체 API 패키지들)
  useEffect(() => {
    const allPackagesData = [
      // 기존 패키지들
      ['채권/금리', '종목별 시가평가', 'bond/marketvaluation', '채권-종목별 시가평가'],
      ['채권 통합 일중/일별 체결정보', '체결정보', 'bond/market/mn_hist', '채권 통합 일중/일별 체결정보'],
      
      // 새로 추가되는 패키지들
      ['KRX-증시-ETF', 'i-NAV (일중)', 'etf/intra', '국내주식-ETF-일중 NAV'],
      ['KRX-증시-ETF', 'PDF', 'etf/port', '국내주식-ETF-PDF'],
      ['KRX-증시-ETF', '일별 NAV', 'etf/hist', '국내주식-ETF-일별 NAV'],
      ['KRX-증시-ETF', '종목 보유 ETF 검색', 'etf/search', '국내주식-종목 ETF 검색'],
      ['KRX-증시-ETP', 'ETP 추가정보', 'etp', '국내주식-ETP 추가 정보'],
      ['KRX-증시-ETP', 'ETP-상세검색', 'etp/list', '국내주식-ETP 상세 검색'],
      ['KRX-증시-주식', '코드 검색/리스트', 'stock/code', '국내주식-코드 검색/리스트'],
      ['KRX-증시-주식', '기본', 'stock/info', '국내주식-기본'],
      ['KRX-증시-주식', '일별', 'stock/hist', '국내주식-일별'],
      ['KRX-증시-주식', '체결(정규장)', 'stock/tick', '국내주식-체결(정규장)'],
      ['KRX-증시-주식', '외국인 지분율', 'stock/foreign', '국내주식-외국인 지분율'],
      ['KRX-증시-주식', '순위', 'stock/rank', '국내주식-순위'],
      ['KRX-증시-주식', '투자자-일별', 'stock/investor', '국내주식-투자자-일별'],
      ['KRX-증시-주식', '체결(정규장 외)', 'stock/tick_etc', '국내주식-체결(정규장 외)'],
      ['KRX-증시-주식', '신용 거래', 'stock/lending', '국내주식-신용 거래'],
      ['KRX-증시-주식', '대차 거래', 'stock/borrowing', '국내주식-대차 거래'],
      ['KRX-증시-주식', '폐지종목', 'stock/expired', '국내주식-폐지종목'],
      ['KRX-증시-지수', '코드 검색/리스트', 'index/code', 'KRX지수-코드 검색/리스트'],
      ['KRX-증시-지수', '기본', 'index/info', 'KRX지수-기본'],
      ['KRX-증시-지수', '일별', 'index/hist', 'KRX지수-일별'],
      ['KRX-증시-지수', '투자자-일중', 'index/investor/intra', 'KRX지수-투자자-일중'],
      ['KRX-증시-지수', '투자자-일별', 'index/investor/hist', 'KRX지수-투자자-일별'],
      ['KRX-증시-지수', '구성 종목', 'index/constituents', 'KRX지수-구성 종목'],
      ['KRX-파생-선물', '코드 검색/리스트', 'future/code', 'KRX파생-선물-코드 검색/리스트'],
      ['KRX-파생-선물', '기본', 'future/info', 'KRX파생-선물-기본'],
      ['KRX-파생-선물', '일별', 'future/hist', 'KRX파생-선물-일별'],
      ['KRX-파생-선물', '체결', 'future/tick', 'KRX파생-선물-체결'],
      ['KRX-파생-선물', '투자자-일별', 'future/investor/hist', 'KRX파생-선물-투자자-일별'],
      ['KRX-파생-선물', '투자자-일중', 'future/investor/intra', 'KRX파생-선물-투자자-일중'],
      ['KRX-파생-선물', '기초자산코드', 'future/underlying', 'KRX파생-선물-기초자산코드'],
      ['KRX-파생-선물', '연결 선물', 'future/active', 'KRX파생-선물-연결 선물'],
      ['KRX-파생-선물', '과거물 코드', 'future/expired', 'KRX파생-선물-과거물 코드(전체 상품)'],
      ['KRX-파생-선물', '차근월물 연결', 'future/2active', 'KRX파생-선물-차근월물 연결'],
      ['KRX-파생-옵션', '코드 검색/리스트', 'option/code', 'KRX파생-옵션-코드 검색/리스트'],
      ['KRX-파생-옵션', '기본', 'option/info', 'KRX파생-옵션-기본(개별/월물)'],
      ['KRX-파생-옵션', '일별', 'option/hist', 'KRX파생-옵션-일별'],
      ['KRX-파생-옵션', '체결', 'option/tick', 'KRX파생-옵션-체결'],
      ['KRX-파생-옵션', '민감도-일중', 'option/greeks/intra', 'KRX파생-옵션-민감도-일중'],
      ['KRX-파생-옵션', '민감도-일별', 'option/greeks/hist', 'KRX파생-옵션-민감도-일별'],
      ['KRX-파생-옵션', '투자자-일중', 'option/investor/intra', 'KRX파생-옵션-투자자-일중'],
      ['KRX-파생-옵션', '투자자-일별', 'option/investor/hist', 'KRX파생-옵션-투자자-일별'],
      ['KRX-파생-옵션', '연결ATM', 'option/active', 'KRX파생-옵션-연결ATM'],
      ['KRX-파생-옵션', '기초자산코드', 'option/underlying', 'KRX파생-옵션-기초자산코드'],
      ['경제지표', '히스토리-내부용', 'eco/hist', '경제지표-수치화-내부용'],
      ['기업정보', '개요 및 재무상태표', 'stock/comp', '기업정보-개요 및 재무상태표'],
      ['기업정보-한국', '상장기업 검색', 'company/listed', '기업정보-상장기업 검색'],
      ['기업정보-한국', '외감기업 검색', 'company/external', '기업정보-외감기업 검색'],
      ['기업정보-한국', '상세 재무계정코드', 'company/detailaccout', '기업정보-상세 재무계정코드'],
      ['기업정보-한국', '공통 재무계정코드', 'company/accout', '기업정보-공통 재무계정코드'],
      ['뉴스', '리스트', 'news/search', '뉴스-검색'],
      ['뉴스', '뉴스 내용', 'news/view', '뉴스-내용'],
      ['리서치리포트', '리스트', 'report/list', '리서치리포트-리스트'],
      ['리서치리포트', '국내주식', 'report/korea', '리서치리포트-국내주식'],
      ['외환', '고시환율-일중', 'fx/exchangerate/intra', '외환-고시환율-일중'],
      ['외환', '고시환율-일별', 'fx/exchangerate/hist', '외환-고시환율-일별'],
      ['외환', '이종통화-기본', 'fx/info', '외환-이종통화-기본'],
      ['외환', '이종통화-일별', 'fx/hist', '외환-이종통화-일별'],
      ['외환', '국가별 통화코드', 'fx/code', '외환-국가별 통화코드'],
      ['외환', '이종통화-일중', 'fx/intra', '외환-이종통화-일중'],
      ['외환', '매매기준율', 'fx/mar', '외환-매매기준율'],
      ['외환-CNHKRW', '서울외환(SMB)', 'cnhkrw/smb', '외환-CNHKRW-서울외환(SMB)'],
      ['외환-CNHKRW', '한국자금(KMB)', 'cnhkrw/kmb', '외환-CNHKRW-한국자금(KMB)'],
      ['외환-CNHKRW', '체결/호가(기업용)', 'cnhkrw/tick', '외환-CNHKRW-체결/호가(기업용)'],
      ['외환-USDKRW', '서울외환(SMB) 익일 02:00', 'usdkrw/smb', '외환-USDKRW-서울외환(SMB) 익일 02:00'],
      ['외환-USDKRW', '한국자금(KMB) 익일 02:00', 'usdkrw/kmb', '외환-USDKRW-한국자금(KMB) 익일 02:00'],
      ['외환-USDKRW', '한국자금(KMB)-시간대별 거래량', 'usdkrw/kmb/volumeattime', '외환-USDKRW-한국자금(KMB)-시간대별 거래량'],
      ['외환-USDKRW', '시간대별 최우선 호가', 'usdkrw/bestattime', '외환-USDKRW-시간대별 최우선 호가'],
      ['외환-USDKRW', '서울외환(SMB)-시간대별 거래량', 'usdkrw/smb/volumeattime', '외환-USDKRW-서울외환(SMB)-시간대별 거래량'],
      ['외환-USDKRW', '체결/호가(기업용)', 'usdkrw/tick', '외환-USDKRW-체결/호가(기업용)'],
      ['외환-USDKRW', '서울외환(SMB) 15:30', 'usdkrw/smb1530', '외환-USDKRW-서울외환(SMB) 15:30'],
      ['외환-USDKRW', '한국자금(KMB) 15:30', 'usdkrw/kmb1530', '외환-USDKRW-한국자금(KMB) 15:30'],
      ['외환-USDKRW 비공개', '서울외환(SMB)체결/호가 비공개', 'usdkrw/smb/tick', '외환-USDKRW(비공개)-서울외환(SMB) 체결/호가 비공개'],
      ['외환-USDKRW 비공개', '한국자금(KMB)체결/호가 비공개', 'usdkrw/kmb/tick', '외환-USDKRW(비공개)-한국자금(KMB) 체결/호가 비공개'],
      ['외환-USDKRW포워드', '체결/호가(포워드 종합)', 'usdkrwforward/tick', '외환-USDKRW포워드-체결/호가(포워드 종합)'],
      ['차트', '차트-전체-스마트코드', 'chart/all', '차트데이터-전체-스마트코드'],
      ['채권', '발행정보', 'bond/basic_info', '채권-발행정보'],
      ['채권', '종목별 시가평가_평가사별', 'bond/marketvalue', '채권-종목별 시가평가(평가사별)'],
      ['채권', '현금흐름', 'bond/cashflow', '채권-현금흐름'],
      ['채권 - 발행기관 관련 (코드, 사명 한/영)', '채권 - 발행기관 관련 (코드, 사명 한/영)', 'bond/corp_name', '채권-발행기관 관련 (코드/사명 한·영)'],
      ['채권-금리/수익률', '주요금리 및 수익률 정보', 'bond/rate/ir_yield', '주요금리 및 수익률 정보'],
      ['채권-발행정보', '리그테이블 인수&주관', 'bond/league', '리그테이블 인수&주관'],
      ['채권-장내국채', '장내국채-일중', 'bond/jang/1', '채권-장내국채-일중'],
      ['채권-장내국채', '장내국채-일별', 'bond/market/gov_hist', '채권-장내국채-정부지표'],
      ['채권-장내국채', '장내국채-호가정보 (1분 단위)', 'bond/market/hoga_info', '채권-장내국채-호가정보(1분)'],
      ['채권-장내국채', '장내국채-코드정보', 'bond/market/code_info', '채권-장내국채-코드정보'],
      ['채권-장내국채', '장내국채-실시간체결', 'bond/market/tick_info', '채권-장내국채-실시간체결'],
      ['채권-장내국채', '장내국채-실시간호가', 'bond/market/hoga_real', '채권-장내국채-실시간호가'],
      ['채권-해외채권', 'KP물', 'bond/foreign/kp', '해외채권-KP물'],
      ['파생-국채선물', '바스켓 채권', 'future/basket', '국채선물-바스켓채권']
    ]

    // 패키지 데이터를 ApiPackage 객체로 변환
    const initialPackages: ApiPackage[] = allPackagesData.map(([category, itemName, urlPath, fullName], index) => {
      const baseUrl = 'https://infomaxy.einfomax.co.kr/api'
      const fullUrl = `${baseUrl}/${urlPath}`
      
      // 입력 파라미터 자동 설정
      const inputs: ApiParameter[] = []
      
      // 실제 API 문서 기반 파라미터 설정
      if (urlPath === 'bond/market/mn_hist') {
        // 채권 체결정보
        inputs.push(
          { name: 'stdcd', type: 'String', required: false, description: '표준코드 [KR6460409D60 등]', defaultValue: '' },
          { name: 'market', type: 'String', required: false, description: '시장구분 [0:통합(전체), 1:장내국채, 2:장내일반, 3:장내소액, 5:장외]', defaultValue: '' },
          { name: 'startDate', type: 'String', required: false, description: '조회 시작일 (미 입력 시 당일) [20240301 등]', defaultValue: '' },
          { name: 'endDate', type: 'String', required: false, description: '조회 종료일 (미 입력 시 당일) [20240301 등]', defaultValue: '' },
          { name: 'aclassnm', type: 'String', required: false, description: '대분류 [국채, 지방채, 공사공단채, 통안증권, 금융채, 회사채, ELS/DLS, 기타]', defaultValue: '' },
          { name: 'volume', type: 'String', required: false, description: '거래량 [>= 1000 등 (천 단위)]', defaultValue: '' },
          { name: 'allcrdtrate', type: 'String', required: false, description: '신용등급 [AAA, BBB+ 등]', defaultValue: '' },
          { name: 'yld', type: 'String', required: false, description: '거래수익률 [7.51 등]', defaultValue: '' },
          { name: 'estyld', type: 'String', required: false, description: '민평수익률 [3.652 등]', defaultValue: '' }
        )
      } else if (urlPath === 'bond/marketvaluation') {
        // 채권 종목별 시가평가
        inputs.push(
          { name: 'stdcd', type: 'String', required: true, description: '표준코드', defaultValue: '' },
          { name: 'bonddate', type: 'String', required: false, description: '일자 (미 입력 시 당일)', defaultValue: '' }
        )
      } else if (urlPath === 'stock/hist') {
        // 주식 일별 정보
        inputs.push(
          { name: 'code', type: 'String', required: true, description: '6자리 종목코드 or ISIN 코드', defaultValue: '' },
          { name: 'endDate', type: 'Number', required: false, description: '조회 종료일 (YYYYMMDD) 미입력시 today', defaultValue: '' },
          { name: 'startDate', type: 'Number', required: false, description: '조회 시작일 (YYYYMMDD) 미입력시 endDate-30', defaultValue: '' }
        )
      } else if (urlPath === 'stock/code') {
        // 주식 코드 검색/리스트
        inputs.push(
          { name: 'search', type: 'String', required: false, description: '통합검색 (미입력시 전체 표시)', defaultValue: '' },
          { name: 'code', type: 'String', required: false, description: '6자리 종목코드 검색', defaultValue: '' },
          { name: 'name', type: 'String', required: false, description: '종목명 검색', defaultValue: '' },
          { name: 'isin', type: 'String', required: false, description: 'ISIN코드 검색', defaultValue: '' },
          { name: 'market', type: 'String', required: false, description: '시장 구분 [1:거래소 2:거래소 기타 5:KRX 7:코스닥 8:코스닥 기타]', defaultValue: '' },
          { name: 'type', type: 'String', required: false, description: '종목 구분 [ST:주식, MF:뮤추얼종목, RT:리츠, EW:ELW, EF:ETF, EN:ETN 등]', defaultValue: '' }
        )
      } else {
        // 기타 API들의 일반적인 패턴
        if (urlPath.includes('stock/') && !urlPath.includes('code')) {
          // 주식 관련 API (code 제외)
          inputs.push({
            name: 'code',
            type: 'String',
            required: true,
            description: '6자리 종목코드 or ISIN 코드'
          })
          
          if (urlPath.includes('hist')) {
            inputs.push(
              { name: 'endDate', type: 'Number', required: false, description: '조회 종료일 (YYYYMMDD) 미입력시 today' },
              { name: 'startDate', type: 'Number', required: false, description: '조회 시작일 (YYYYMMDD) 미입력시 endDate-30' }
            )
          }
        } else if (urlPath.includes('bond/') && !urlPath.includes('code') && !urlPath.includes('list')) {
          // 채권 관련 API
          inputs.push({
            name: 'stdcd',
            type: 'String',
            required: true,
            description: '표준코드'
          })
          
          if (urlPath.includes('hist')) {
            inputs.push(
              { name: 'startDate', type: 'String', required: false, description: '시작일자 (YYYYMMDD)' },
              { name: 'endDate', type: 'String', required: false, description: '종료일자 (YYYYMMDD)' }
            )
          } else {
            inputs.push({
              name: 'bonddate',
              type: 'String',
              required: false,
              description: '기준일자 (미 입력 시 당일)'
            })
          }
        } else if (urlPath.includes('code') || urlPath.includes('list') || urlPath.includes('search')) {
          // 코드/리스트/검색 API는 파라미터 없음 또는 검색 파라미터만
          if (urlPath.includes('stock/code')) {
            // 이미 위에서 처리됨
          } else {
            inputs.push({
              name: 'search',
              type: 'String',
              required: false,
              description: '검색어 (미입력시 전체 표시)'
            })
          }
        } else {
          // 기본적으로 stdcd 필요한 API
          inputs.push({
            name: 'stdcd',
            type: 'String',
            required: true,
            description: '표준코드'
          })
        }
      }
      
      // 기본 출력 필드
      const outputs = ['stdcd', 'data', 'timestamp']
      
      return {
        id: `api_package_${(index + 1).toString().padStart(3, '0')}`,
        category: category as string,
        itemName: itemName as string,
        fullName: fullName as string,
        urlPath: urlPath as string,
        baseUrl,
        fullUrl,
        inputs,
        outputs,
        description: `${fullName} 정보를 조회하는 API`,
        status: 'active' as const,
        createdAt: '2025-10-04',
        updatedAt: '2025-10-04'
      }
    })
    
    setPackages(initialPackages)
    
    // 저장된 토큰 불러오기
    const savedToken = loadTokenFromStorage()
    if (savedToken) {
      setApiToken(savedToken)
    }
  }, [])

  // 폼 초기값
  const getEmptyPackage = (): ApiPackage => ({
    id: `pkg_${Date.now()}`,
    category: '',
    itemName: '',
    fullName: '',
    urlPath: '',
    baseUrl: 'https://infomaxy.einfomax.co.kr/api',
    fullUrl: '',
    inputs: [],
    outputs: [],
    description: '',
    status: 'active',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  })

  // 패키지 추가/수정 핸들러
  const handleSave = (packageData: ApiPackage) => {
    if (isEditing && editingPackage) {
      // 수정
      setPackages(prev => prev.map(pkg => 
        pkg.id === editingPackage.id ? { ...packageData, id: editingPackage.id } : pkg
      ))
      toast({
        title: '패키지 수정 완료',
        description: `${packageData.fullName} 패키지가 수정되었습니다.`,
        status: 'success',
        duration: 3000
      })
    } else {
      // 추가
      setPackages(prev => [...prev, packageData])
      toast({
        title: '패키지 추가 완료',
        description: `${packageData.fullName} 패키지가 추가되었습니다.`,
        status: 'success',
        duration: 3000
      })
    }
    closeModal()
  }

  // 패키지 삭제 핸들러
  const handleDelete = (id: string) => {
    setPackages(prev => prev.filter(pkg => pkg.id !== id))
    toast({
      title: '패키지 삭제 완료',
      description: '선택한 패키지가 삭제되었습니다.',
      status: 'info',
      duration: 3000
    })
  }

  // 모달 열기/닫기 핸들러
  const openAddModal = () => {
    setEditingPackage(getEmptyPackage())
    setIsEditing(false)
    onOpen()
  }

  const openEditModal = (pkg: ApiPackage) => {
    setEditingPackage(pkg)
    setIsEditing(true)
    onOpen()
  }

  const closeModal = () => {
    setEditingPackage(null)
    setIsEditing(false)
    onClose()
  }

  // 테스트 모달 열기
  const openTestModal = (pkg: ApiPackage) => {
    setSelectedPackageForTest(pkg)
    onTestModalOpen()
  }

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green'
      case 'inactive': return 'gray'
      case 'deprecated': return 'red'
      default: return 'gray'
    }
  }

  // API 호출 테스트 함수
  const testApiCall = async (pkg: ApiPackage) => {
    if (!apiToken) {
      toast({
        title: '토큰 오류',
        description: 'API 토큰을 먼저 입력해주세요.',
        status: 'warning',
        duration: 3000
      })
      return
    }

    setTestingPackage(pkg.id)
    
    try {
      // 기본 테스트 파라미터 생성 (실제 환경에서는 사용자가 입력)
      const testParams: {[key: string]: string} = {}
      pkg.inputs.forEach(input => {
        if (input.name === 'stdcd') {
          testParams[input.name] = 'KR101501DA32'  // 예시값
        } else if (input.name === 'bonddate') {
          testParams[input.name] = '20250401'  // 예시값
        } else if (input.name === 'startDate') {
          testParams[input.name] = '20250930'  // 요청한 값
        } else if (input.name === 'endDate') {
          testParams[input.name] = '20250930'  // 요청한 값
        } else if (input.required) {
          testParams[input.name] = input.defaultValue || 'test_value'
        }
      })

      // URL에 쿼리 파라미터 추가
      const urlWithParams = Object.keys(testParams).length > 0
        ? `${pkg.fullUrl}?${new URLSearchParams(testParams).toString()}`
        : pkg.fullUrl

      const response = await fetch(urlWithParams, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
          'Content-Type': 'application/json'
        }
      })

      const responseData = await response.json()
      
      if (response.ok) {
        setTestResults(prev => ({
          ...prev,
          [pkg.id]: {
            success: true,
            data: responseData,
            status: response.status,
            timestamp: new Date().toLocaleString('ko-KR')
          }
        }))
        
        toast({
          title: 'API 호출 성공',
          description: `${pkg.fullName} API가 성공적으로 호출되었습니다.`,
          status: 'success',
          duration: 3000
        })
      } else {
        throw new Error(`HTTP ${response.status}: ${responseData.message || '호출 실패'}`)
      }
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [pkg.id]: {
          success: false,
          error: error instanceof Error ? error.message : '알 수 없는 오류',
          timestamp: new Date().toLocaleString('ko-KR')
        }
      }))
      
      toast({
        title: 'API 호출 실패',
        description: error instanceof Error ? error.message : '호출 중 오류가 발생했습니다.',
        status: 'error',
        duration: 5000
      })
    } finally {
      setTestingPackage('')
    }
  }

  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        
        {/* 페이지 헤더 */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <Flex align="center">
              <HStack spacing={3}>
                <FiCode size={24} />
                <VStack spacing={1} align="start">
                  <Heading size="lg" color="blue.600" _dark={{ color: "blue.300" }}>
                    📦 API 패키지 관리
                  </Heading>
                  <Text color="gray.600" _dark={{ color: "gray.400" }}>
                    REST API 패키지들의 정보 관리 및 문서화
                  </Text>
                </VStack>
              </HStack>
              <Spacer />
              <Button
                leftIcon={<FiPlus />}
                colorScheme="blue"
                onClick={openAddModal}
                size="md"
              >
                새 패키지 추가
              </Button>
            </Flex>
          </CardHeader>
        </Card>

        {/* API TOKEN 관리 */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack>
              <FiKey size={20} />
              <VStack spacing={1} align="start">
                <Heading size="md">🔐 API 인증 토큰</Heading>
                <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.400" }}>
                  모든 API 호출에 사용될 Bearer 토큰을 설정하세요
                </Text>
              </VStack>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Bearer Token</FormLabel>
                <InputGroup>
                  <Input
                    type={showToken ? "text" : "password"}
                    value={apiToken}
                    onChange={(e) => handleTokenChange(e.target.value)}
                    placeholder="API 토큰을 입력하세요..."
                    pr="8rem"
                  />
                  <InputRightElement width="7rem">
                    <HStack spacing={1}>
                      <IconButton
                        aria-label={showToken ? "토큰 숨기기" : "토큰 보기"}
                        h="1.5rem"
                        size="xs"
                        icon={showToken ? <FiEyeOff /> : <FiEye />}
                        onClick={() => setShowToken(!showToken)}
                        variant="ghost"
                      />
                      {apiToken && (
                        <IconButton
                          aria-label="토큰 삭제"
                          h="1.5rem"
                          size="xs"
                          icon={<FiTrash2 />}
                          onClick={() => {
                            handleTokenChange('')
                            toast({
                              title: '토큰 삭제',
                              description: '저장된 토큰이 삭제되었습니다.',
                              status: 'info',
                              duration: 2000
                            })
                          }}
                          variant="ghost"
                          colorScheme="red"
                        />
                      )}
                    </HStack>
                  </InputRightElement>
                </InputGroup>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  예시: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
                </Text>
              </FormControl>
              
              {apiToken && (
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <AlertDescription fontSize="sm">
                    토큰이 설정되어 브라우저에 저장되었습니다. 이제 API 호출 테스트를 진행할 수 있습니다.
                  </AlertDescription>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* 통계 요약 */}
        <HStack spacing={6}>
          <Card bg={bgColor} borderColor={borderColor} flex="1">
            <CardBody>
              <HStack>
                <Box>
                  <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                    {packages.length}
                  </Text>
                  <Text fontSize="sm" color="gray.600">총 패키지</Text>
                </Box>
                <Spacer />
                <FiBookOpen size={24} color="#3B82F6" />
              </HStack>
            </CardBody>
          </Card>
          
          <Card bg={bgColor} borderColor={borderColor} flex="1">
            <CardBody>
              <HStack>
                <Box>
                  <Text fontSize="2xl" fontWeight="bold" color="green.500">
                    {packages.filter(p => p.status === 'active').length}
                  </Text>
                  <Text fontSize="sm" color="gray.600">활성 상태</Text>
                </Box>
                <Spacer />
                <FiGlobe size={24} color="#22C55E" />
              </HStack>
            </CardBody>
          </Card>

          <Card bg={bgColor} borderColor={borderColor} flex="1">
            <CardBody>
              <HStack>
                <Box>
                  <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                    {packages.reduce((sum, pkg) => sum + pkg.inputs.length, 0)}
                  </Text>
                  <Text fontSize="sm" color="gray.600">총 입력 파라미터</Text>
                </Box>
                <Spacer />
                <FiCode size={24} color="#8B5CF6" />
              </HStack>
            </CardBody>
          </Card>
        </HStack>

        {/* API 패키지 목록 */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">📋 등록된 API 패키지 목록</Heading>
          </CardHeader>
          <CardBody>
            {packages.length === 0 ? (
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                <Text>등록된 API 패키지가 없습니다. 새 패키지를 추가해보세요.</Text>
              </Alert>
            ) : (
              <TableContainer>
                <Table variant="simple" size="md">
                  <Thead>
                    <Tr>
                      <Th>대분류</Th>
                      <Th>항목명</Th>
                      <Th>풀네임</Th>
                      <Th>URL 경로</Th>
                      <Th>상태</Th>
                      <Th>입력 파라미터</Th>
                      <Th>출력 필드</Th>
                      <Th>액션</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {packages.map((pkg) => (
                      <React.Fragment key={pkg.id}>
                        <Tr>
                          <Td>
                            <Badge colorScheme="blue" variant="subtle">
                              {pkg.category}
                            </Badge>
                          </Td>
                          <Td>
                            <Text 
                              fontWeight="semibold"
                              color="blue.600"
                              _hover={{ color: "blue.800", cursor: "pointer" }}
                              onClick={() => openTestModal(pkg)}
                            >
                              {pkg.itemName}
                            </Text>
                          </Td>
                          <Td>{pkg.fullName}</Td>
                          <Td>
                            <Code fontSize="xs" colorScheme="gray">
                              /{pkg.urlPath}
                            </Code>
                          </Td>
                          <Td>
                            <Badge colorScheme={getStatusColor(pkg.status)}>
                              {pkg.status.toUpperCase()}
                            </Badge>
                          </Td>
                          <Td>
                            <HStack spacing={1} flexWrap="wrap">
                              {pkg.inputs.map((input, idx) => (
                                <Tag key={idx} size="sm" colorScheme={input.required ? "red" : "gray"}>
                                  <TagLabel>{input.name}</TagLabel>
                                </Tag>
                              ))}
                            </HStack>
                          </Td>
                          <Td>
                            <Text fontSize="xs" color="gray.600">
                              {pkg.outputs.length}개 필드
                            </Text>
                          </Td>
                          <Td>
                            <HStack spacing={2}>
                              <IconButton
                                aria-label="API 테스트"
                                icon={<FiPlay />}
                                size="sm"
                                variant="ghost"
                                colorScheme="green"
                                onClick={() => openTestModal(pkg)}
                                title="API 호출 테스트"
                              />
                              <IconButton
                                aria-label="수정"
                                icon={<FiEdit />}
                                size="sm"
                                variant="ghost"
                                colorScheme="blue"
                                onClick={() => openEditModal(pkg)}
                              />
                              <IconButton
                                aria-label="삭제"
                                icon={<FiTrash2 />}
                                size="sm"
                                variant="ghost"
                                colorScheme="red"
                                onClick={() => handleDelete(pkg.id)}
                              />
                            </HStack>
                          </Td>
                        </Tr>
                      </React.Fragment>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
            )}
          </CardBody>
        </Card>

      </VStack>

      {/* 패키지 추가/수정 모달 */}
      <PackageModal
        isOpen={isOpen}
        onClose={closeModal}
        onSave={handleSave}
        package={editingPackage}
        isEditing={isEditing}
      />

      {/* API 테스트 모달 */}
      <ApiTestModal
        isOpen={isTestModalOpen}
        onClose={onTestModalClose}
        package={selectedPackageForTest}
        apiToken={apiToken}
      />
    </Box>
  )
}

// 패키지 추가/수정 모달 컴포넌트
interface PackageModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (pkg: ApiPackage) => void
  package: ApiPackage | null
  isEditing: boolean
}

const PackageModal: React.FC<PackageModalProps> = ({
  isOpen,
  onClose,
  onSave,
  package: pkg,
  isEditing
}) => {
  const [formData, setFormData] = useState<ApiPackage | null>(null)

  useEffect(() => {
    if (pkg) {
      setFormData({ ...pkg })
    }
  }, [pkg])

  if (!formData) return null

  const updateFullUrl = (baseUrl: string, urlPath: string) => {
    const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl
    const cleanPath = urlPath.startsWith('/') ? urlPath.slice(1) : urlPath
    return `${cleanBase}/${cleanPath}`
  }

  const handleInputChange = (field: keyof ApiPackage, value: any) => {
    setFormData(prev => {
      if (!prev) return null
      
      const updated = { ...prev, [field]: value }
      
      // URL 경로가 변경되면 전체 URL도 업데이트
      if (field === 'urlPath' || field === 'baseUrl') {
        updated.fullUrl = updateFullUrl(
          field === 'baseUrl' ? value : prev.baseUrl,
          field === 'urlPath' ? value : prev.urlPath
        )
      }
      
      return updated
    })
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {isEditing ? '📝 API 패키지 수정' : '➕ 새 API 패키지 추가'}
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <VStack spacing={4}>
            {/* 기본 정보 */}
            <Box w="100%">
              <Text fontWeight="bold" mb={2}>📋 기본 정보</Text>
              <VStack spacing={3}>
                <FormControl>
                  <FormLabel>대분류</FormLabel>
                  <Input
                    value={formData.category}
                    onChange={(e) => handleInputChange('category', e.target.value)}
                    placeholder="예: 채권/금리"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>항목명</FormLabel>
                  <Input
                    value={formData.itemName}
                    onChange={(e) => handleInputChange('itemName', e.target.value)}
                    placeholder="예: 종목별 시가평가"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>풀네임</FormLabel>
                  <Input
                    value={formData.fullName}
                    onChange={(e) => handleInputChange('fullName', e.target.value)}
                    placeholder="예: 채권-종목별 시가평가"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>상태</FormLabel>
                  <Select
                    value={formData.status}
                    onChange={(e) => handleInputChange('status', e.target.value as any)}
                  >
                    <option value="active">활성</option>
                    <option value="inactive">비활성</option>
                    <option value="deprecated">지원 중단</option>
                  </Select>
                </FormControl>
              </VStack>
            </Box>

            <Divider />

            {/* URL 정보 */}
            <Box w="100%">
              <Text fontWeight="bold" mb={2}>🌐 URL 정보</Text>
              <VStack spacing={3}>
                <FormControl>
                  <FormLabel>기본 URL</FormLabel>
                  <Input
                    value={formData.baseUrl}
                    onChange={(e) => handleInputChange('baseUrl', e.target.value)}
                    placeholder="https://infomaxy.einfomax.co.kr/api"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>URL 경로</FormLabel>
                  <Input
                    value={formData.urlPath}
                    onChange={(e) => handleInputChange('urlPath', e.target.value)}
                    placeholder="bond/marketvaluation"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>실제 호출 URL (자동 생성)</FormLabel>
                  <Code p={2} w="100%" bg="gray.50" _dark={{ bg: "gray.700" }}>
                    {formData.fullUrl}
                  </Code>
                </FormControl>
              </VStack>
            </Box>

            <Divider />

            {/* 입력 파라미터 */}
            <Box w="100%">
              <Text fontWeight="bold" mb={2}>⚡ 입력 파라미터</Text>
              <Textarea
                value={formData.inputs.map(input => 
                  `${input.name} (${input.type}${input.required ? ', 필수' : ''})${input.description ? ' - ' + input.description : ''}`
                ).join('\n')}
                onChange={(e) => {
                  const lines = e.target.value.split('\n').filter(line => line.trim())
                  const inputs = lines.map(line => {
                    const match = line.match(/^(\w+)\s*\((\w+)(?:,\s*필수)?\)(?:\s*-\s*(.+))?$/)
                    if (match) {
                      return {
                        name: match[1],
                        type: match[2] as any,
                        required: line.includes('필수'),
                        description: match[3] || ''
                      }
                    }
                    return {
                      name: line.split(' ')[0] || '',
                      type: 'String' as any,
                      required: false,
                      description: ''
                    }
                  })
                  handleInputChange('inputs', inputs)
                }}
                placeholder="stdcd (String, 필수) - 표준코드&#10;bonndate (String) - 기준일자"
                rows={4}
              />
              <Text fontSize="xs" color="gray.500" mt={1}>
                한 줄에 하나씩, 형식: 파라미터명 (타입, 필수) - 설명
              </Text>
            </Box>

            {/* 출력 필드 */}
            <Box w="100%">
              <Text fontWeight="bold" mb={2}>📤 출력 필드</Text>
              <Textarea
                value={formData.outputs.join('\n')}
                onChange={(e) => {
                  const outputs = e.target.value.split('\n').filter(line => line.trim())
                  handleInputChange('outputs', outputs)
                }}
                placeholder="stdcd&#10;bonddate&#10;estyld_3avg"
                rows={3}
              />
              <Text fontSize="xs" color="gray.500" mt={1}>
                한 줄에 하나씩 필드명 입력
              </Text>
            </Box>

            {/* 설명 */}
            <FormControl>
              <FormLabel>설명</FormLabel>
              <Textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="API 패키지에 대한 간단한 설명을 입력하세요."
                rows={2}
              />
            </FormControl>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            취소
          </Button>
          <Button 
            colorScheme="blue" 
            onClick={() => onSave(formData)}
            isDisabled={!formData.category || !formData.itemName || !formData.urlPath}
          >
            {isEditing ? '수정' : '추가'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default ApiPackageManagement
