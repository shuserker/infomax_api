import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  VStack,
  HStack,
  Text,
  Input,
  FormControl,
  FormLabel,
  Switch,
  Badge,
  Box,
  Divider,
  Select,
  Grid,
  GridItem,
  Alert,
  AlertIcon,
  AlertDescription,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  IconButton,
  useToast,
  useColorModeValue
} from '@chakra-ui/react';
import { FiSave, FiRefreshCw, FiTrash2, FiClock, FiSettings } from 'react-icons/fi';
import { parameterDefaultManager, ParameterDefaults, AutoUpdateRule } from '../../utils/parameterDefaultManager';

interface ParameterDefaultsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ParameterDefaultsModal: React.FC<ParameterDefaultsModalProps> = ({
  isOpen,
  onClose
}) => {
  const [defaults, setDefaults] = useState<ParameterDefaults>({});
  const [editingParam, setEditingParam] = useState<{
    apiPath: string;
    paramName: string;
    value: string;
    isAutoManaged: boolean;
    autoUpdateRule?: AutoUpdateRule;
  } | null>(null);
  
  const toast = useToast();
  const bgColor = useColorModeValue('gray.50', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // 모달이 열릴 때 기본값 로드
  useEffect(() => {
    if (isOpen) {
      loadDefaults();
    }
  }, [isOpen]);

  const loadDefaults = () => {
    const allDefaults = parameterDefaultManager.getAllDefaults();
    setDefaults(allDefaults);
  };

  const handleSaveParameter = () => {
    if (!editingParam) return;

    parameterDefaultManager.setParameterDefault(
      editingParam.apiPath,
      editingParam.paramName,
      editingParam.value,
      editingParam.isAutoManaged,
      editingParam.autoUpdateRule
    );

    loadDefaults();
    setEditingParam(null);
    
    toast({
      title: '✅ 저장 완료',
      description: `${editingParam.apiPath}.${editingParam.paramName} 기본값이 저장되었습니다.`,
      status: 'success',
      duration: 3000
    });
  };

  const handleDeleteParameter = (apiPath: string, paramName: string) => {
    parameterDefaultManager.removeParameterDefault(apiPath, paramName);
    loadDefaults();
    
    toast({
      title: '🗑️ 삭제 완료',
      description: `${apiPath}.${paramName} 기본값이 삭제되었습니다.`,
      status: 'info',
      duration: 3000
    });
  };

  const handleResetAll = () => {
    parameterDefaultManager.resetAllDefaults();
    loadDefaults();
    
    toast({
      title: '🔄 초기화 완료',
      description: '모든 파라미터 기본값이 초기값으로 복원되었습니다.',
      status: 'success',
      duration: 3000
    });
  };

  const formatLastUpdated = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ko-KR');
  };

  const getDayName = (day: number) => {
    const days = ['일', '월', '화', '수', '목', '금', '토'];
    return days[day];
  };

  const renderAutoUpdateSchedule = (rule?: AutoUpdateRule) => {
    if (!rule?.enabled) return null;

    const daysText = rule.schedule.daysOfWeek.map(getDayName).join(', ');
    const timeText = `${String(rule.schedule.timeHour).padStart(2, '0')}:${String(rule.schedule.timeMinute).padStart(2, '0')}`;
    
    return (
      <Badge colorScheme="green" variant="subtle" fontSize="xs">
        🕐 매주 {daysText} {timeText}
      </Badge>
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>
          <HStack>
            <FiSettings />
            <Text>파라미터 기본값 관리</Text>
            <Badge colorScheme="blue" variant="outline">
              {Object.keys(defaults).length}개 API
            </Badge>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />

        <ModalBody overflow="auto">
          <VStack spacing={4} align="stretch">
            
            {/* 상단 안내 메시지 */}
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <AlertDescription fontSize="sm">
                API 파라미터의 기본값을 설정하고 자동 갱신 규칙을 관리할 수 있습니다. 
                자동 갱신은 지정된 스케줄에 따라 백그라운드에서 실행됩니다.
              </AlertDescription>
            </Alert>

            {/* 전체 작업 버튼 */}
            <HStack justify="space-between">
              <HStack>
                <Button
                  leftIcon={<FiRefreshCw />}
                  onClick={loadDefaults}
                  size="sm"
                  variant="outline"
                >
                  새로고침
                </Button>
                <Button
                  leftIcon={<FiTrash2 />}
                  onClick={handleResetAll}
                  size="sm"
                  colorScheme="orange"
                  variant="outline"
                >
                  전체 초기화
                </Button>
              </HStack>
              
              <Text fontSize="sm" color="gray.500">
                마지막 자동 갱신 체크: {formatLastUpdated(localStorage.getItem('infomax_auto_update_last_check') || new Date().toISOString())}
              </Text>
            </HStack>

            <Divider />

            {/* API별 파라미터 목록 */}
            <Accordion allowMultiple>
              {Object.entries(defaults).map(([apiPath, apiDefaults]) => (
                <AccordionItem key={apiPath} border="1px" borderColor={borderColor} borderRadius="md" mb={2}>
                  <h3>
                    <AccordionButton bg={bgColor} _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}>
                      <Box flex="1" textAlign="left">
                        <HStack>
                          <Text fontWeight="bold">{apiPath}</Text>
                          <Badge variant="outline">{Object.keys(apiDefaults).length}개</Badge>
                        </HStack>
                      </Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h3>
                  
                  <AccordionPanel pb={4}>
                    <VStack spacing={3} align="stretch">
                      {Object.entries(apiDefaults).map(([paramName, paramDefault]) => (
                        <Box key={paramName} p={3} border="1px" borderColor={borderColor} borderRadius="md">
                          <Grid templateColumns="1fr 1fr 200px 120px" gap={4} alignItems="center">
                            
                            {/* 파라미터 이름 */}
                            <GridItem>
                              <VStack align="start" spacing={1}>
                                <Text fontWeight="medium">{paramName}</Text>
                                {paramDefault.isAutoManaged && (
                                  <Badge colorScheme="purple" variant="subtle" size="sm">
                                    자동 관리
                                  </Badge>
                                )}
                              </VStack>
                            </GridItem>

                            {/* 현재 값 */}
                            <GridItem>
                              <VStack align="start" spacing={1}>
                                <Text fontSize="sm" fontFamily="mono" bg={bgColor} px={2} py={1} borderRadius="md">
                                  {paramDefault.value}
                                </Text>
                                <Text fontSize="xs" color="gray.500">
                                  {formatLastUpdated(paramDefault.lastUpdated)}
                                </Text>
                              </VStack>
                            </GridItem>

                            {/* 자동 갱신 스케줄 */}
                            <GridItem>
                              {renderAutoUpdateSchedule(paramDefault.autoUpdateRule)}
                            </GridItem>

                            {/* 작업 버튼 */}
                            <GridItem>
                              <HStack>
                                <IconButton
                                  icon={<FiSettings />}
                                  size="sm"
                                  variant="outline"
                                  aria-label="편집"
                                  onClick={() => setEditingParam({
                                    apiPath,
                                    paramName,
                                    value: paramDefault.value,
                                    isAutoManaged: paramDefault.isAutoManaged,
                                    autoUpdateRule: paramDefault.autoUpdateRule
                                  })}
                                />
                                <IconButton
                                  icon={<FiTrash2 />}
                                  size="sm"
                                  colorScheme="red"
                                  variant="outline"
                                  aria-label="삭제"
                                  onClick={() => handleDeleteParameter(apiPath, paramName)}
                                />
                              </HStack>
                            </GridItem>
                          </Grid>
                        </Box>
                      ))}
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>

            {Object.keys(defaults).length === 0 && (
              <Box textAlign="center" py={8}>
                <Text color="gray.500">설정된 파라미터 기본값이 없습니다.</Text>
                <Button mt={2} onClick={handleResetAll} size="sm">
                  기본값 생성
                </Button>
              </Box>
            )}
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            닫기
          </Button>
        </ModalFooter>
      </ModalContent>

      {/* 파라미터 편집 모달 */}
      {editingParam && (
        <Modal isOpen={true} onClose={() => setEditingParam(null)} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              파라미터 편집: {editingParam.apiPath}.{editingParam.paramName}
            </ModalHeader>
            <ModalCloseButton />

            <ModalBody>
              <VStack spacing={4} align="stretch">
                {/* 기본값 */}
                <FormControl>
                  <FormLabel>기본값</FormLabel>
                  <Input
                    value={editingParam.value}
                    onChange={(e) => setEditingParam({
                      ...editingParam,
                      value: e.target.value
                    })}
                    placeholder="기본값을 입력하세요"
                  />
                </FormControl>

                {/* 자동 관리 설정 */}
                <FormControl>
                  <HStack justify="space-between">
                    <FormLabel mb={0}>자동 갱신</FormLabel>
                    <Switch
                      isChecked={editingParam.isAutoManaged}
                      onChange={(e) => {
                        const newAutoManaged = e.target.checked;
                        setEditingParam({
                          ...editingParam,
                          isAutoManaged: newAutoManaged,
                          autoUpdateRule: newAutoManaged ? {
                            enabled: true,
                            schedule: {
                              daysOfWeek: [1, 2], // 월, 화
                              timeHour: 4,
                              timeMinute: 0
                            },
                            updateLogic: 'current_date_minus_1'
                          } : undefined
                        });
                      }}
                    />
                  </HStack>
                </FormControl>

                {/* 자동 갱신 상세 설정 */}
                {editingParam.isAutoManaged && (
                  <Box p={4} border="1px" borderColor={borderColor} borderRadius="md">
                    <Text fontWeight="medium" mb={3}>자동 갱신 설정</Text>
                    
                    {/* 갱신 요일 */}
                    <FormControl mb={3}>
                      <FormLabel fontSize="sm">갱신 요일</FormLabel>
                      <HStack wrap="wrap">
                        {[0, 1, 2, 3, 4, 5, 6].map(day => (
                          <Button
                            key={day}
                            size="sm"
                            variant={editingParam.autoUpdateRule?.schedule.daysOfWeek.includes(day) ? 'solid' : 'outline'}
                            colorScheme={editingParam.autoUpdateRule?.schedule.daysOfWeek.includes(day) ? 'blue' : 'gray'}
                            onClick={() => {
                              if (!editingParam.autoUpdateRule) return;
                              
                              const currentDays = editingParam.autoUpdateRule.schedule.daysOfWeek;
                              const newDays = currentDays.includes(day)
                                ? currentDays.filter(d => d !== day)
                                : [...currentDays, day];
                              
                              setEditingParam({
                                ...editingParam,
                                autoUpdateRule: {
                                  ...editingParam.autoUpdateRule,
                                  schedule: {
                                    ...editingParam.autoUpdateRule.schedule,
                                    daysOfWeek: newDays
                                  }
                                }
                              });
                            }}
                          >
                            {getDayName(day)}
                          </Button>
                        ))}
                      </HStack>
                    </FormControl>

                    {/* 갱신 시간 */}
                    <HStack>
                      <FormControl>
                        <FormLabel fontSize="sm">시간</FormLabel>
                        <Select
                          value={editingParam.autoUpdateRule?.schedule.timeHour || 4}
                          onChange={(e) => {
                            if (!editingParam.autoUpdateRule) return;
                            setEditingParam({
                              ...editingParam,
                              autoUpdateRule: {
                                ...editingParam.autoUpdateRule,
                                schedule: {
                                  ...editingParam.autoUpdateRule.schedule,
                                  timeHour: parseInt(e.target.value)
                                }
                              }
                            });
                          }}
                          size="sm"
                        >
                          {Array.from({length: 24}, (_, i) => (
                            <option key={i} value={i}>{String(i).padStart(2, '0')}시</option>
                          ))}
                        </Select>
                      </FormControl>
                      
                      <FormControl>
                        <FormLabel fontSize="sm">분</FormLabel>
                        <Select
                          value={editingParam.autoUpdateRule?.schedule.timeMinute || 0}
                          onChange={(e) => {
                            if (!editingParam.autoUpdateRule) return;
                            setEditingParam({
                              ...editingParam,
                              autoUpdateRule: {
                                ...editingParam.autoUpdateRule,
                                schedule: {
                                  ...editingParam.autoUpdateRule.schedule,
                                  timeMinute: parseInt(e.target.value)
                                }
                              }
                            });
                          }}
                          size="sm"
                        >
                          {[0, 15, 30, 45].map(minute => (
                            <option key={minute} value={minute}>{String(minute).padStart(2, '0')}분</option>
                          ))}
                        </Select>
                      </FormControl>
                    </HStack>

                    {/* 갱신 로직 */}
                    <FormControl>
                      <FormLabel fontSize="sm">갱신 로직</FormLabel>
                      <Select
                        value={editingParam.autoUpdateRule?.updateLogic || 'current_date_minus_1'}
                        onChange={(e) => {
                          if (!editingParam.autoUpdateRule) return;
                          setEditingParam({
                            ...editingParam,
                            autoUpdateRule: {
                              ...editingParam.autoUpdateRule,
                              updateLogic: e.target.value as any
                            }
                          });
                        }}
                        size="sm"
                        maxH="200px"
                        overflowY="auto"
                      >
                        <optgroup label="기본 날짜">
                          <option value="current_date">📅 오늘 날짜</option>
                          <option value="current_date_minus_1">📅 어제 날짜 (당일-1)</option>
                          <option value="current_date_minus_2">📅 그제 날짜 (당일-2)</option>
                          <option value="current_date_minus_3">📅 3일 전</option>
                        </optgroup>
                        
                        <optgroup label="주간 단위">
                          <option value="last_week_start">📅 지난주 월요일</option>
                          <option value="last_week_end">📅 지난주 금요일</option>
                          <option value="current_week_start">📅 이번주 월요일</option>
                          <option value="current_week_end">📅 이번주 금요일</option>
                          <option value="last_business_day">💼 최근 영업일</option>
                        </optgroup>
                        
                        <optgroup label="월간 단위">
                          <option value="current_month_start">📅 이번달 1일</option>
                          <option value="current_month_end">📅 이번달 말일</option>
                          <option value="last_month_start">📅 지난달 1일</option>
                          <option value="last_month_end">📅 지난달 말일</option>
                          <option value="next_month_start">📅 다음달 1일</option>
                        </optgroup>
                        
                        <optgroup label="분기 단위">
                          <option value="current_quarter_start">📅 이번 분기 시작일</option>
                          <option value="current_quarter_end">📅 이번 분기 종료일</option>
                          <option value="last_quarter_start">📅 지난 분기 시작일</option>
                          <option value="last_quarter_end">📅 지난 분기 종료일</option>
                        </optgroup>
                        
                        <optgroup label="년간 단위">
                          <option value="current_year_start">📅 올해 1월 1일</option>
                          <option value="current_year_end">📅 올해 12월 31일</option>
                          <option value="last_year_start">📅 작년 1월 1일</option>
                          <option value="last_year_end">📅 작년 12월 31일</option>
                        </optgroup>
                        
                        <optgroup label="상대적 날짜">
                          <option value="days_ago_7">📅 1주일 전</option>
                          <option value="days_ago_30">📅 1개월 전</option>
                          <option value="days_ago_90">📅 3개월 전</option>
                          <option value="days_ago_180">📅 6개월 전</option>
                          <option value="days_ago_365">📅 1년 전</option>
                        </optgroup>
                        
                        <optgroup label="특수 로직">
                          <option value="auto_smart_date">🤖 스마트 자동 날짜</option>
                          <option value="last_business_day">💼 최근 영업일</option>
                          <option value="trading_market_priority">💹 거래시장 우선순위</option>
                          <option value="rotate_keywords">🔁 키워드 로테이션</option>
                          <option value="next_future_month">📊 다음 선물 만료월</option>
                        </optgroup>
                      </Select>
                      
                      {/* 각 로직에 대한 설명 */}
                      <Text fontSize="xs" color="gray.500" mt={1}>
                        {editingParam.autoUpdateRule?.updateLogic === 'auto_smart_date' && '시간과 요일에 따라 자동으로 적절한 날짜 선택'}
                        {editingParam.autoUpdateRule?.updateLogic === 'trading_market_priority' && '장중은 코스피, 장후는 코스닥 우선'}
                        {editingParam.autoUpdateRule?.updateLogic === 'rotate_keywords' && '삼성전자, SK하이닉스 등 주요 키워드 순환'}
                        {editingParam.autoUpdateRule?.updateLogic === 'last_business_day' && '토,일 제외하고 가장 최근 영업일'}
                        {editingParam.autoUpdateRule?.updateLogic === 'next_future_month' && '선물 만료월 (3,6,9,12월 사이클) 자동 계산'}
                      </Text>
                    </FormControl>
                  </Box>
                )}
              </VStack>
            </ModalBody>

            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={() => setEditingParam(null)}>
                취소
              </Button>
              <Button
                leftIcon={<FiSave />}
                colorScheme="blue"
                onClick={handleSaveParameter}
              >
                저장
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}
    </Modal>
  );
};

export default ParameterDefaultsModal;
