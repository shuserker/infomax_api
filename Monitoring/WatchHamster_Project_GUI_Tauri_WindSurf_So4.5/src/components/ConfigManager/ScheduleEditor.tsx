import React from 'react'
import {
  VStack,
  HStack,
  FormControl,
  FormLabel,
  Input,
  Switch,
  Checkbox,
  CheckboxGroup,
  Stack,
  Text,
} from '@chakra-ui/react'

interface ScheduleEditorProps {
  config: any
  onChange: (config: any) => void
}

const ScheduleEditor: React.FC<ScheduleEditorProps> = ({ config, onChange }) => {
  const daysOfWeek = [
    { value: 0, label: '일' },
    { value: 1, label: '월' },
    { value: 2, label: '화' },
    { value: 3, label: '수' },
    { value: 4, label: '목' },
    { value: 5, label: '금' },
    { value: 6, label: '토' },
  ]

  return (
    <VStack spacing={6} align="stretch">
      {/* 실행 간격 */}
      <FormControl isRequired>
        <FormLabel>실행 간격 (분)</FormLabel>
        <Input
          type="number"
          value={config.interval}
          onChange={(e) => onChange({ ...config, interval: parseInt(e.target.value) })}
          min={1}
          max={1440}
        />
        <Text fontSize="xs" color="gray.500" mt={1}>
          1분 ~ 1440분 (24시간)
        </Text>
      </FormControl>

      {/* 실행 시간대 */}
      <FormControl>
        <FormLabel>실행 시간대 (선택사항)</FormLabel>
        <HStack>
          <Input
            type="time"
            value={config.timeRange?.start || ''}
            onChange={(e) =>
              onChange({
                ...config,
                timeRange: { ...config.timeRange, start: e.target.value },
              })
            }
            placeholder="시작 시간"
          />
          <Text>~</Text>
          <Input
            type="time"
            value={config.timeRange?.end || ''}
            onChange={(e) =>
              onChange({
                ...config,
                timeRange: { ...config.timeRange, end: e.target.value },
              })
            }
            placeholder="종료 시간"
          />
        </HStack>
        <Text fontSize="xs" color="gray.500" mt={1}>
          예: 09:00 ~ 18:00 (비워두면 24시간 실행)
        </Text>
      </FormControl>

      {/* 요일 선택 */}
      <FormControl>
        <FormLabel>실행 요일</FormLabel>
        <CheckboxGroup
          value={config.daysOfWeek || []}
          onChange={(values) =>
            onChange({ ...config, daysOfWeek: values.map(Number) })
          }
        >
          <Stack direction="row" spacing={4}>
            {daysOfWeek.map((day) => (
              <Checkbox key={day.value} value={day.value}>
                {day.label}
              </Checkbox>
            ))}
          </Stack>
        </CheckboxGroup>
        <Text fontSize="xs" color="gray.500" mt={1}>
          선택하지 않으면 매일 실행
        </Text>
      </FormControl>

      {/* 공휴일 제외 */}
      <FormControl display="flex" alignItems="center">
        <FormLabel mb="0">공휴일 제외</FormLabel>
        <Switch
          isChecked={config.excludeHolidays}
          onChange={(e) =>
            onChange({ ...config, excludeHolidays: e.target.checked })
          }
          colorScheme="blue"
        />
      </FormControl>
    </VStack>
  )
}

export default ScheduleEditor
