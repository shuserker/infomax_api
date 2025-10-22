import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  Textarea,
  Select,
  FormControl,
  FormLabel,
  FormErrorMessage,
  FormHelperText,
  Card,
  CardHeader,
  CardBody,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Badge,
  IconButton,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Divider,
  Code,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Spinner,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
} from '@chakra-ui/react'
import { useForm, Controller } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import {
  FiSend,
  FiEdit,
  FiTrash2,
  FiPlus,
  FiEye,
  FiCopy,
  FiRefreshCw,
  FiCheck,
  FiX,
  FiClock,
} from 'react-icons/fi'
import { WebhookPayload, WebhookTemplate } from '../../types'
import { useWebhookManagement } from '../../hooks/useWebhookManagement'

// 웹훅 전송 폼 스키마
const webhookSendSchema = yup.object({
  url: yup.string().url('올바른 URL을 입력해주세요').required('웹훅 URL은 필수입니다'),
  message: yup.string().required('메시지는 필수입니다'),
  webhook_type: yup.string().oneOf(['discord', 'slack', 'generic']).required('웹훅 타입을 선택해주세요'),
  template_id: yup.string().optional().nullable(),
  variables: yup.object().optional(),
})

// 템플릿 생성/편집 폼 스키마
const templateSchema = yup.object({
  name: yup.string().required('템플릿 이름은 필수입니다'),
  description: yup.string().required('템플릿 설명은 필수입니다'),
  webhook_type: yup.string().oneOf(['discord', 'slack', 'generic']).required('웹훅 타입을 선택해주세요'),
  template: yup.string().required('템플릿 내용은 필수입니다'),
})

interface WebhookSendForm {
  url: string
  message: string
  webhook_type: 'discord' | 'slack' | 'generic'
  template_id?: string
  variables?: Record<string, string>
}

interface TemplateForm {
  name: string
  description: string
  webhook_type: 'discord' | 'slack' | 'generic'
  template: string
}

export const WebhookManagement: React.FC = () => {
  const toast = useToast()
  const { isOpen: isTemplateModalOpen, onOpen: onTemplateModalOpen, onClose: onTemplateModalClose } = useDisclosure()
  const { isOpen: isPreviewModalOpen, onOpen: onPreviewModalOpen, onClose: onPreviewModalClose } = useDisclosure()
  
  const [selectedTemplate, setSelectedTemplate] = useState<WebhookTemplate | null>(null)
  const [previewMessage, setPreviewMessage] = useState<string>('')
  const [editingTemplate, setEditingTemplate] = useState<WebhookTemplate | null>(null)
  const [templateVariables, setTemplateVariables] = useState<Record<string, string>>({})

  const {
    templates,
    isLoadingTemplates,
    history,
    isLoadingHistory,
    isSendingWebhook,
    sendWebhook,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    refetchTemplates,
    refetchHistory,
    extractTemplateVariables,
    applyTemplateVariables,
  } = useWebhookManagement()

  // 웹훅 전송 폼
  const {
    control: sendControl,
    handleSubmit: handleSendSubmit,
    formState: { errors: sendErrors },
    reset: resetSendForm,
    watch: watchSendForm,
    setValue: setSendValue,
  } = useForm({
    resolver: yupResolver(webhookSendSchema),
    defaultValues: {
      url: '',
      message: '',
      webhook_type: 'discord',
      template_id: '',
      variables: {},
    },
  })

  // 템플릿 폼
  const {
    control: templateControl,
    handleSubmit: handleTemplateSubmit,
    formState: { errors: templateErrors },
    reset: resetTemplateForm,
    setValue: setTemplateValue,
  } = useForm({
    resolver: yupResolver(templateSchema),
    defaultValues: {
      name: '',
      description: '',
      webhook_type: 'discord',
      template: '',
    },
  })

  const watchedTemplateId = watchSendForm('template_id')
  const watchedMessage = watchSendForm('message')

  // 템플릿 변수 초기화
  useEffect(() => {
    if (selectedTemplate && extractTemplateVariables) {
      const variables = extractTemplateVariables(selectedTemplate.template)
      if (variables && Array.isArray(variables)) {
        const initialVariables: Record<string, string> = {}
        variables.forEach(variable => {
          initialVariables[variable] = templateVariables[variable] || ''
        })
        setTemplateVariables(initialVariables)
      }
    }
  }, [selectedTemplate, extractTemplateVariables])

  // 선택된 템플릿 변경 시 메시지 업데이트
  useEffect(() => {
    if (watchedTemplateId && templates.length > 0) {
      const template = templates.find(t => t.id === watchedTemplateId)
      if (template) {
        setSelectedTemplate(template)
        updateMessageFromTemplate(template)
      }
    } else {
      setSelectedTemplate(null)
    }
  }, [watchedTemplateId, templates])



  const updateMessageFromTemplate = (template: WebhookTemplate) => {
    if (applyTemplateVariables) {
      const message = applyTemplateVariables(template.template, templateVariables)
      setSendValue('message', message)
      setPreviewMessage(message)
    }
  }

  const handleVariableChange = (key: string, value: string) => {
    const newVariables = { ...templateVariables, [key]: value }
    setTemplateVariables(newVariables)
    
    if (selectedTemplate && applyTemplateVariables) {
      const message = applyTemplateVariables(selectedTemplate.template, newVariables)
      setSendValue('message', message)
      setPreviewMessage(message)
    }
  }

  const onSendWebhook = async (data: any) => {
    const payload: WebhookPayload = {
      url: data.url,
      message: data.message,
      webhook_type: data.webhook_type,
      template_id: data.template_id,
      variables: templateVariables,
    }

    await sendWebhook(payload)
    
    // 폼 초기화
    resetSendForm()
    setTemplateVariables({})
    setSelectedTemplate(null)
  }

  const onSaveTemplate = async (data: any) => {
    if (editingTemplate) {
      // 템플릿 수정
      await updateTemplate(editingTemplate.id, data)
    } else {
      // 새 템플릿 생성
      await createTemplate(data)
    }
    
    onTemplateModalClose()
    resetTemplateForm()
    setEditingTemplate(null)
  }

  const handleEditTemplate = (template: WebhookTemplate) => {
    setEditingTemplate(template)
    setTemplateValue('name', template.name)
    setTemplateValue('description', template.description)
    setTemplateValue('webhook_type', template.webhook_type)
    setTemplateValue('template', template.template)
    onTemplateModalOpen()
  }

  const handleDeleteTemplate = async (templateId: string) => {
    await deleteTemplate(templateId)
  }

  const handlePreviewMessage = () => {
    setPreviewMessage(watchedMessage)
    onPreviewModalOpen()
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: '복사 완료',
      description: '클립보드에 복사되었습니다',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'green'
      case 'failed': return 'red'
      case 'pending': return 'yellow'
      default: return 'gray'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <FiCheck />
      case 'failed': return <FiX />
      case 'pending': return <FiClock />
      default: return <FiClock />
    }
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Text fontSize="2xl" fontWeight="bold" mb={2}>
            웹훅 및 메시지 관리
          </Text>
          <Text color="gray.600">
            Discord, Slack 등으로 메시지를 전송하고 템플릿을 관리합니다
          </Text>
        </Box>

        <Tabs>
          <TabList>
            <Tab>웹훅 전송</Tab>
            <Tab>템플릿 관리</Tab>
            <Tab>전송 히스토리</Tab>
          </TabList>

          <TabPanels>
            {/* 웹훅 전송 탭 */}
            <TabPanel>
              <Card>
                <CardHeader>
                  <HStack justify="space-between">
                    <Text fontSize="lg" fontWeight="semibold">
                      웹훅 메시지 전송
                    </Text>
                    <Button
                      leftIcon={<FiEye />}
                      size="sm"
                      variant="outline"
                      onClick={handlePreviewMessage}
                      isDisabled={!watchedMessage}
                    >
                      미리보기
                    </Button>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <form onSubmit={handleSendSubmit(onSendWebhook)}>
                    <VStack spacing={4} align="stretch">
                      <HStack spacing={4}>
                        <FormControl isInvalid={!!sendErrors.webhook_type} flex={1}>
                          <FormLabel>웹훅 타입</FormLabel>
                          <Controller
                            name="webhook_type"
                            control={sendControl}
                            render={({ field }) => (
                              <Select {...field}>
                                <option value="discord">Discord</option>
                                <option value="slack">Slack</option>
                                <option value="generic">일반</option>
                              </Select>
                            )}
                          />
                          <FormErrorMessage>{sendErrors.webhook_type?.message}</FormErrorMessage>
                        </FormControl>

                        <FormControl flex={2}>
                          <FormLabel>템플릿 선택 (선택사항)</FormLabel>
                          <Controller
                            name="template_id"
                            control={sendControl}
                            render={({ field }) => (
                              <Select {...field} placeholder="템플릿을 선택하세요">
                                {templates.map((template) => (
                                  <option key={template.id} value={template.id}>
                                    {template.name}
                                  </option>
                                ))}
                              </Select>
                            )}
                          />
                        </FormControl>
                      </HStack>

                      <FormControl isInvalid={!!sendErrors.url}>
                        <FormLabel>웹훅 URL</FormLabel>
                        <Controller
                          name="url"
                          control={sendControl}
                          render={({ field }) => (
                            <Input {...field} placeholder="https://discord.com/api/webhooks/..." />
                          )}
                        />
                        <FormErrorMessage>{sendErrors.url?.message}</FormErrorMessage>
                      </FormControl>

                      {/* 템플릿 변수 입력 */}
                      {selectedTemplate && selectedTemplate.variables.length > 0 && (
                        <Box>
                          <Text fontWeight="semibold" mb={2}>템플릿 변수</Text>
                          <VStack spacing={2} align="stretch">
                            {selectedTemplate.variables.map((variable) => (
                              <FormControl key={variable}>
                                <FormLabel fontSize="sm">{variable}</FormLabel>
                                <Input
                                  size="sm"
                                  placeholder={`${variable} 값을 입력하세요`}
                                  value={templateVariables[variable] || ''}
                                  onChange={(e) => handleVariableChange(variable, e.target.value)}
                                />
                              </FormControl>
                            ))}
                          </VStack>
                        </Box>
                      )}

                      <FormControl isInvalid={!!sendErrors.message}>
                        <FormLabel>메시지 내용</FormLabel>
                        <Controller
                          name="message"
                          control={sendControl}
                          render={({ field }) => (
                            <Textarea
                              {...field}
                              placeholder="전송할 메시지를 입력하세요"
                              rows={6}
                            />
                          )}
                        />
                        <FormErrorMessage>{sendErrors.message?.message}</FormErrorMessage>
                        <FormHelperText>
                          템플릿을 선택하면 자동으로 메시지가 생성됩니다
                        </FormHelperText>
                      </FormControl>

                      <HStack justify="flex-end">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => {
                            resetSendForm()
                            setTemplateVariables({})
                            setSelectedTemplate(null)
                          }}
                        >
                          초기화
                        </Button>
                        <Button
                          type="submit"
                          colorScheme="blue"
                          leftIcon={<FiSend />}
                          isLoading={isSendingWebhook}
                          loadingText="전송 중..."
                        >
                          웹훅 전송
                        </Button>
                      </HStack>
                    </VStack>
                  </form>
                </CardBody>
              </Card>
            </TabPanel>

            {/* 템플릿 관리 탭 */}
            <TabPanel>
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Text fontSize="lg" fontWeight="semibold">
                    메시지 템플릿
                  </Text>
                  <HStack>
                    <Button
                      leftIcon={<FiRefreshCw />}
                      size="sm"
                      variant="outline"
                      onClick={refetchTemplates}
                      isLoading={isLoadingTemplates}
                    >
                      새로고침
                    </Button>
                    <Button
                      leftIcon={<FiPlus />}
                      colorScheme="blue"
                      size="sm"
                      onClick={() => {
                        setEditingTemplate(null)
                        resetTemplateForm()
                        onTemplateModalOpen()
                      }}
                    >
                      새 템플릿
                    </Button>
                  </HStack>
                </HStack>

                {isLoadingTemplates ? (
                  <Box textAlign="center" py={8}>
                    <Spinner size="lg" />
                    <Text mt={2}>템플릿을 불러오는 중...</Text>
                  </Box>
                ) : templates.length === 0 ? (
                  <Alert status="info">
                    <AlertIcon />
                    <AlertTitle>템플릿이 없습니다</AlertTitle>
                    <AlertDescription>
                      새 템플릿을 생성하여 메시지 전송을 더 쉽게 만들어보세요
                    </AlertDescription>
                  </Alert>
                ) : (
                  <VStack spacing={3} align="stretch">
                    {templates.map((template) => (
                      <Card key={template.id}>
                        <CardBody>
                          <HStack justify="space-between" align="start">
                            <VStack align="start" spacing={2} flex={1}>
                              <HStack>
                                <Text fontWeight="semibold">{template.name}</Text>
                                <Badge colorScheme="blue">{template.webhook_type}</Badge>
                              </HStack>
                              <Text fontSize="sm" color="gray.600">
                                {template.description}
                              </Text>
                              <Code fontSize="xs" p={2} borderRadius="md" maxW="100%" overflow="auto">
                                {template.template.substring(0, 100)}
                                {template.template.length > 100 && '...'}
                              </Code>
                              {template.variables.length > 0 && (
                                <HStack>
                                  <Text fontSize="xs" color="gray.500">변수:</Text>
                                  {template.variables.map((variable) => (
                                    <Badge key={variable} size="sm" variant="outline">
                                      {variable}
                                    </Badge>
                                  ))}
                                </HStack>
                              )}
                            </VStack>
                            <HStack>
                              <IconButton
                                aria-label="템플릿 복사"
                                icon={<FiCopy />}
                                size="sm"
                                variant="ghost"
                                onClick={() => copyToClipboard(template.template)}
                              />
                              <IconButton
                                aria-label="템플릿 편집"
                                icon={<FiEdit />}
                                size="sm"
                                variant="ghost"
                                onClick={() => handleEditTemplate(template)}
                              />
                              <IconButton
                                aria-label="템플릿 삭제"
                                icon={<FiTrash2 />}
                                size="sm"
                                variant="ghost"
                                colorScheme="red"
                                onClick={() => handleDeleteTemplate(template.id)}
                              />
                            </HStack>
                          </HStack>
                        </CardBody>
                      </Card>
                    ))}
                  </VStack>
                )}
              </VStack>
            </TabPanel>

            {/* 전송 히스토리 탭 */}
            <TabPanel>
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Text fontSize="lg" fontWeight="semibold">
                    전송 히스토리
                  </Text>
                  <Button
                    leftIcon={<FiRefreshCw />}
                    size="sm"
                    variant="outline"
                    onClick={refetchHistory}
                    isLoading={isLoadingHistory}
                  >
                    새로고침
                  </Button>
                </HStack>

                {history.length === 0 ? (
                  <Alert status="info">
                    <AlertIcon />
                    <AlertTitle>전송 히스토리가 없습니다</AlertTitle>
                    <AlertDescription>
                      웹훅을 전송하면 여기에 기록이 표시됩니다
                    </AlertDescription>
                  </Alert>
                ) : (
                  <TableContainer>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>상태</Th>
                          <Th>타입</Th>
                          <Th>URL</Th>
                          <Th>메시지</Th>
                          <Th>전송 시간</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {history.map((item) => (
                          <Tr key={item.id}>
                            <Td>
                              <HStack>
                                <Box color={`${getStatusColor(item.status)}.500`}>
                                  {getStatusIcon(item.status)}
                                </Box>
                                <Badge colorScheme={getStatusColor(item.status)}>
                                  {item.status}
                                </Badge>
                              </HStack>
                            </Td>
                            <Td>
                              <Badge variant="outline">{item.webhook_type}</Badge>
                            </Td>
                            <Td>
                              <Text fontSize="sm" maxW="200px" isTruncated>
                                {item.url}
                              </Text>
                            </Td>
                            <Td>
                              <Text fontSize="sm" maxW="300px" isTruncated>
                                {item.message}
                              </Text>
                            </Td>
                            <Td>
                              <Text fontSize="sm">
                                {new Date(item.sent_at).toLocaleString('ko-KR')}
                              </Text>
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </TableContainer>
                )}
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>

      {/* 템플릿 생성/편집 모달 */}
      <Modal isOpen={isTemplateModalOpen} onClose={onTemplateModalClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {editingTemplate ? '템플릿 편집' : '새 템플릿 생성'}
          </ModalHeader>
          <ModalCloseButton />
          <form onSubmit={handleTemplateSubmit(onSaveTemplate)}>
            <ModalBody>
              <VStack spacing={4} align="stretch">
                <HStack spacing={4}>
                  <FormControl isInvalid={!!templateErrors.name} flex={2}>
                    <FormLabel>템플릿 이름</FormLabel>
                    <Controller
                      name="name"
                      control={templateControl}
                      render={({ field }) => (
                        <Input {...field} placeholder="템플릿 이름을 입력하세요" />
                      )}
                    />
                    <FormErrorMessage>{templateErrors.name?.message}</FormErrorMessage>
                  </FormControl>

                  <FormControl isInvalid={!!templateErrors.webhook_type} flex={1}>
                    <FormLabel>웹훅 타입</FormLabel>
                    <Controller
                      name="webhook_type"
                      control={templateControl}
                      render={({ field }) => (
                        <Select {...field}>
                          <option value="discord">Discord</option>
                          <option value="slack">Slack</option>
                          <option value="generic">일반</option>
                        </Select>
                      )}
                    />
                    <FormErrorMessage>{templateErrors.webhook_type?.message}</FormErrorMessage>
                  </FormControl>
                </HStack>

                <FormControl isInvalid={!!templateErrors.description}>
                  <FormLabel>설명</FormLabel>
                  <Controller
                    name="description"
                    control={templateControl}
                    render={({ field }) => (
                      <Input {...field} placeholder="템플릿 설명을 입력하세요" />
                    )}
                  />
                  <FormErrorMessage>{templateErrors.description?.message}</FormErrorMessage>
                </FormControl>

                <FormControl isInvalid={!!templateErrors.template}>
                  <FormLabel>템플릿 내용</FormLabel>
                  <Controller
                    name="template"
                    control={templateControl}
                    render={({ field }) => (
                      <Textarea
                        {...field}
                        placeholder="템플릿 내용을 입력하세요. 변수는 {{변수명}} 형태로 사용하세요"
                        rows={8}
                      />
                    )}
                  />
                  <FormErrorMessage>{templateErrors.template?.message}</FormErrorMessage>
                  <FormHelperText>
                    변수는 {`{{변수명}}`} 형태로 사용하세요. 예: {`{{서비스명}}, {{상태}}, {{시간}}`}
                  </FormHelperText>
                </FormControl>

                <Alert status="info" size="sm">
                  <AlertIcon />
                  <Box>
                    <AlertTitle fontSize="sm">템플릿 변수 사용법</AlertTitle>
                    <AlertDescription fontSize="xs">
                      {`{{변수명}}`} 형태로 변수를 정의하면, 웹훅 전송 시 실제 값으로 치환됩니다.
                      예: "서비스 {`{{서비스명}}`}의 상태가 {`{{상태}}`}로 변경되었습니다."
                    </AlertDescription>
                  </Box>
                </Alert>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onTemplateModalClose}>
                취소
              </Button>
              <Button type="submit" colorScheme="blue">
                {editingTemplate ? '수정' : '생성'}
              </Button>
            </ModalFooter>
          </form>
        </ModalContent>
      </Modal>

      {/* 메시지 미리보기 모달 */}
      <Modal isOpen={isPreviewModalOpen} onClose={onPreviewModalClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>메시지 미리보기</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <Box>
                <Text fontSize="sm" color="gray.600" mb={2}>
                  전송될 메시지:
                </Text>
                <Box
                  p={4}
                  bg="gray.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="gray.200"
                  whiteSpace="pre-wrap"
                >
                  {previewMessage || '메시지가 없습니다'}
                </Box>
              </Box>
              
              <Divider />
              
              <Box>
                <Text fontSize="sm" color="gray.600" mb={2}>
                  JSON 형태:
                </Text>
                <Code
                  display="block"
                  p={3}
                  borderRadius="md"
                  fontSize="xs"
                  whiteSpace="pre-wrap"
                  overflow="auto"
                  maxH="200px"
                >
                  {JSON.stringify({ content: previewMessage }, null, 2)}
                </Code>
              </Box>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button
              variant="outline"
              mr={3}
              leftIcon={<FiCopy />}
              onClick={() => copyToClipboard(previewMessage)}
            >
              복사
            </Button>
            <Button onClick={onPreviewModalClose}>닫기</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  )
}

export default WebhookManagement