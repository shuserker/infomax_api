import React, { useRef, useState, useEffect } from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Heading,
  VStack,
  HStack,
  Button,
  Text,
  Divider,
  useToast,
  Alert,
  AlertIcon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  Progress,
  Box,
  Badge,
  Textarea,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  IconButton,
  Tooltip,
  Checkbox,
  CheckboxGroup,
  Stack,
  Select,
  FormControl,
  FormLabel,
  Switch
} from '@chakra-ui/react'
import { 
  FiDownload, 
  FiUpload, 
  FiRotateCcw, 
  FiSave,
  FiFileText,
  FiAlertTriangle,
  FiTrash2,
  FiRefreshCw,
  FiEye,
  FiClock,
  FiShield
} from 'react-icons/fi'
import { AppSettings } from '../../types'
import { apiService } from '../../services/api'

interface ConfigManagementProps {
  settings: AppSettings
  onSettingChange: (key: keyof AppSettings, value: any) => void
  onSaveSettings: () => Promise<boolean>
  onResetSettings: () => Promise<boolean>
}

interface BackupInfo {
  filename: string
  path: string
  type: 'regular_backup' | 'import_backup' | 'corrupted_backup'
  size: number
  created_at: string
  modified_at: string
}

interface ExportOptions {
  sections: string[]
  includeSensitive: boolean
  format: 'json' | 'yaml'
}

interface ImportOptions {
  merge: boolean
  validate: boolean
  backupBeforeImport: boolean
  sections: string[]
}

interface SettingsInfo {
  settings_file: string
  exists: boolean
  size: number
  last_modified?: string
  backup_count: number
  is_valid: boolean
}

const ConfigManagement: React.FC<ConfigManagementProps> = ({
  settings,
  onSettingChange,
  onSaveSettings,
  onResetSettings
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isExporting, setIsExporting] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isResetting, setIsResetting] = useState(false)
  const [isLoadingBackups, setIsLoadingBackups] = useState(false)
  const [isCleaningUp, setIsCleaningUp] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [configPreview, setConfigPreview] = useState<string>('')
  const [backups, setBackups] = useState<BackupInfo[]>([])
  const [settingsInfo, setSettingsInfo] = useState<SettingsInfo | null>(null)
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    sections: [],
    includeSensitive: false,
    format: 'json'
  })
  const [importOptions, setImportOptions] = useState<ImportOptions>({
    merge: true,
    validate: true,
    backupBeforeImport: true,
    sections: []
  })
  
  const { 
    isOpen: isResetModalOpen, 
    onOpen: openResetModal, 
    onClose: closeResetModal 
  } = useDisclosure()
  
  const { 
    isOpen: isImportModalOpen, 
    onOpen: openImportModal, 
    onClose: closeImportModal 
  } = useDisclosure()

  const { 
    isOpen: isBackupsModalOpen, 
    onOpen: openBackupsModal, 
    onClose: closeBackupsModal 
  } = useDisclosure()

  const { 
    isOpen: isExportModalOpen, 
    onOpen: openExportModal, 
    onClose: closeExportModal 
  } = useDisclosure()

  const toast = useToast()

  // 설정 정보 및 백업 목록 로드
  useEffect(() => {
    loadSettingsInfo()
    loadBackups()
  }, [])

  const loadSettingsInfo = async () => {
    try {
      const info = await apiService.getSettingsInfo()
      setSettingsInfo(info)
    } catch (error) {
      console.error('설정 정보 로드 실패:', error)
    }
  }

  const loadBackups = async () => {
    setIsLoadingBackups(true)
    try {
      const response = await apiService.getSettingsBackups()
      setBackups(response.backups)
    } catch (error) {
      console.error('백업 목록 로드 실패:', error)
      toast({
        title: '백업 목록 로드 실패',
        description: '백업 파일 목록을 불러올 수 없습니다.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setIsLoadingBackups(false)
    }
  }

  const handleExportSettings = async () => {
    setIsExporting(true)
    try {
      // 백엔드 API를 통한 설정 내보내기
      const response = await apiService.exportSettings(
        exportOptions.sections.length > 0 ? exportOptions.sections : undefined,
        exportOptions.includeSensitive,
        exportOptions.format
      )

      // 파일 다운로드
      const blob = await apiService.downloadExportFile(
        response.download_url.split('/').pop() || 'settings.json'
      )

      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `watchhamster-settings-${new Date().toISOString().split('T')[0]}.${exportOptions.format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      closeExportModal()
      toast({
        title: '설정 내보내기 완료',
        description: '설정 파일이 다운로드되었습니다.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: '설정 내보내기 실패',
        description: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsExporting(false)
    }
  }

  const handleImportSettings = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const configData = JSON.parse(text)

      // 설정 파일 검증
      if (!configData.settings) {
        throw new Error('유효하지 않은 설정 파일입니다.')
      }

      // 백업 정보 설정
      setBackupInfo({
        timestamp: configData.timestamp || new Date().toISOString(),
        version: configData.version || 'unknown',
        size: file.size,
        checksum: btoa(text).slice(0, 8)
      })

      // 설정 미리보기
      setConfigPreview(JSON.stringify(configData.settings, null, 2))
      openImportModal()

    } catch (error) {
      toast({
        title: '설정 파일 읽기 실패',
        description: error instanceof Error ? error.message : '설정 파일을 읽을 수 없습니다.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }

    // 파일 입력 초기화
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const confirmImportSettings = async () => {
    if (!configPreview) return

    setIsImporting(true)
    setImportProgress(0)

    try {
      const configData = JSON.parse(configPreview)
      const newSettings = configData

      // 진행률 시뮬레이션
      for (let i = 0; i <= 100; i += 20) {
        setImportProgress(i)
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      // 설정 적용
      Object.keys(newSettings).forEach(key => {
        onSettingChange(key as keyof AppSettings, newSettings[key])
      })

      closeImportModal()
      toast({
        title: '설정 가져오기 완료',
        description: '설정이 성공적으로 가져와졌습니다. 저장 버튼을 눌러 적용하세요.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: '설정 가져오기 실패',
        description: error instanceof Error ? error.message : '설정을 가져오는데 실패했습니다.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsImporting(false)
      setImportProgress(0)
    }
  }

  const handleSaveSettings = async () => {
    setIsSaving(true)
    try {
      const success = await onSaveSettings()
      if (success) {
        toast({
          title: '설정 저장 완료',
          description: '모든 설정이 성공적으로 저장되었습니다.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      }
    } catch (error) {
      toast({
        title: '설정 저장 실패',
        description: error instanceof Error ? error.message : '설정 저장에 실패했습니다.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsSaving(false)
    }
  }

  const confirmResetSettings = async () => {
    setIsResetting(true)
    try {
      const success = await onResetSettings()
      if (success) {
        closeResetModal()
        toast({
          title: '설정 초기화 완료',
          description: '모든 설정이 기본값으로 초기화되었습니다.',
          status: 'info',
          duration: 3000,
          isClosable: true,
        })
      }
    } catch (error) {
      toast({
        title: '설정 초기화 실패',
        description: error instanceof Error ? error.message : '설정 초기화에 실패했습니다.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsResetting(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  }

  return (
    <>
      <Card>
        <CardHeader>
          <Heading size="md">설정 관리</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={6} align="stretch">
            {/* 설정 저장 */}
            <VStack spacing={3} align="stretch">
              <Text fontWeight="medium">설정 저장</Text>
              <Button
                leftIcon={<FiSave />}
                onClick={handleSaveSettings}
                isLoading={isSaving}
                loadingText="저장 중"
                colorScheme="blue"
                size="sm"
              >
                현재 설정 저장
              </Button>
              <Text fontSize="sm" color="gray.600">
                변경된 설정을 서버에 저장합니다.
              </Text>
            </VStack>

            <Divider />

            {/* 설정 백업/복원 */}
            <VStack spacing={3} align="stretch">
              <Text fontWeight="medium">설정 백업 및 복원</Text>
              
              <HStack spacing={3}>
                <Button
                  leftIcon={<FiDownload />}
                  onClick={handleExportSettings}
                  isLoading={isExporting}
                  loadingText="내보내는 중"
                  variant="outline"
                  size="sm"
                  flex="1"
                >
                  설정 내보내기
                </Button>
                
                <Button
                  leftIcon={<FiUpload />}
                  onClick={handleImportSettings}
                  variant="outline"
                  size="sm"
                  flex="1"
                >
                  설정 가져오기
                </Button>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".json"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </HStack>

              <Text fontSize="sm" color="gray.600">
                설정을 JSON 파일로 내보내거나 이전에 내보낸 파일에서 설정을 복원할 수 있습니다.
              </Text>
            </VStack>

            <Divider />

            {/* 설정 초기화 */}
            <VStack spacing={3} align="stretch">
              <Text fontWeight="medium">설정 초기화</Text>
              
              <Button
                leftIcon={<FiRotateCcw />}
                onClick={openResetModal}
                colorScheme="red"
                variant="outline"
                size="sm"
              >
                기본값으로 초기화
              </Button>
              
              <Alert status="warning" size="sm">
                <AlertIcon />
                <Text fontSize="sm">
                  초기화하면 모든 사용자 설정이 삭제되고 기본값으로 되돌아갑니다.
                </Text>
              </Alert>
            </VStack>

            <Divider />

            {/* 설정 정보 */}
            <VStack spacing={3} align="stretch">
              <Text fontWeight="medium">설정 정보</Text>
              
              <VStack spacing={2} align="stretch">
                <HStack justify="space-between">
                  <Text fontSize="sm">설정 파일 크기</Text>
                  <Text fontSize="sm" color="gray.600">
                    {formatFileSize(JSON.stringify(settings).length)}
                  </Text>
                </HStack>
                
                <HStack justify="space-between">
                  <Text fontSize="sm">마지막 수정</Text>
                  <Text fontSize="sm" color="gray.600">
                    {new Date().toLocaleString('ko-KR')}
                  </Text>
                </HStack>
                
                <HStack justify="space-between">
                  <Text fontSize="sm">설정 항목 수</Text>
                  <Text fontSize="sm" color="gray.600">
                    {Object.keys(settings).length}개
                  </Text>
                </HStack>
              </VStack>
            </VStack>
          </VStack>
        </CardBody>
      </Card>

      {/* 설정 초기화 확인 모달 */}
      <Modal isOpen={isResetModalOpen} onClose={closeResetModal}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>설정 초기화 확인</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <Alert status="warning">
                <AlertIcon />
                <Box>
                  <Text fontWeight="bold">주의: 되돌릴 수 없는 작업입니다</Text>
                  <Text fontSize="sm">
                    모든 사용자 설정이 삭제되고 기본값으로 초기화됩니다.
                  </Text>
                </Box>
              </Alert>
              
              <Text>
                계속하기 전에 현재 설정을 백업하는 것을 권장합니다.
                정말로 모든 설정을 초기화하시겠습니까?
              </Text>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={closeResetModal}>
              취소
            </Button>
            <Button
              colorScheme="red"
              onClick={confirmResetSettings}
              isLoading={isResetting}
              loadingText="초기화 중"
            >
              초기화
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* 설정 가져오기 미리보기 모달 */}
      <Modal isOpen={isImportModalOpen} onClose={closeImportModal} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>설정 가져오기 미리보기</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              {backupInfo && (
                <Box>
                  <Text fontWeight="medium" mb={2}>백업 파일 정보</Text>
                  <HStack spacing={4} wrap="wrap">
                    <Badge colorScheme="blue" variant="outline">
                      버전: {backupInfo.version}
                    </Badge>
                    <Badge colorScheme="green" variant="outline">
                      크기: {formatFileSize(backupInfo.size)}
                    </Badge>
                    <Badge colorScheme="purple" variant="outline">
                      체크섬: {backupInfo.checksum}
                    </Badge>
                  </HStack>
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    생성일: {new Date(backupInfo.timestamp).toLocaleString('ko-KR')}
                  </Text>
                </Box>
              )}

              {isImporting && (
                <Box>
                  <Text mb={2}>설정을 가져오는 중...</Text>
                  <Progress value={importProgress} colorScheme="blue" />
                </Box>
              )}

              <Box>
                <Text fontWeight="medium" mb={2}>설정 미리보기</Text>
                <Textarea
                  value={configPreview}
                  readOnly
                  rows={10}
                  fontSize="xs"
                  fontFamily="mono"
                />
              </Box>

              <Alert status="info" size="sm">
                <AlertIcon />
                <Text fontSize="sm">
                  이 설정을 가져오면 현재 설정이 덮어씌워집니다.
                </Text>
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={closeImportModal}>
              취소
            </Button>
            <Button
              colorScheme="blue"
              onClick={confirmImportSettings}
              isLoading={isImporting}
              loadingText="가져오는 중"
            >
              설정 가져오기
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default ConfigManagement