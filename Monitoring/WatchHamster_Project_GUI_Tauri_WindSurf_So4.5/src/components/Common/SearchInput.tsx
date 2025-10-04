import React, { useState, useCallback } from 'react'
import {
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  IconButton,
  useColorModeValue,
  InputProps,
} from '@chakra-ui/react'
import { MdSearch, MdClear } from 'react-icons/md'
import { motion } from 'framer-motion'

const MotionInputGroup = motion(InputGroup)

export interface SearchInputProps extends Omit<InputProps, 'onChange'> {
  onSearch?: (value: string) => void
  onClear?: () => void
  debounceMs?: number
  showClearButton?: boolean
}

/**
 * 검색 입력 컴포넌트
 * 디바운싱 기능이 포함된 검색 입력 필드
 */
export const SearchInput: React.FC<SearchInputProps> = ({
  onSearch,
  onClear,
  debounceMs = 300,
  showClearButton = true,
  placeholder = '검색어를 입력하세요...',
  ...props
}) => {
  const [value, setValue] = useState('')
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null)
  
  const bgColor = useColorModeValue('white', 'gray.700')
  const borderColor = useColorModeValue('gray.300', 'gray.600')

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value
      setValue(newValue)

      // 기존 타이머 클리어
      if (debounceTimer) {
        clearTimeout(debounceTimer)
      }

      // 새 타이머 설정
      const timer = setTimeout(() => {
        onSearch?.(newValue)
      }, debounceMs)

      setDebounceTimer(timer)
    },
    [onSearch, debounceMs, debounceTimer]
  )

  const handleClear = useCallback(() => {
    setValue('')
    onSearch?.('')
    onClear?.()
    
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
  }, [onSearch, onClear, debounceTimer])

  const handleKeyPress = useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter') {
        if (debounceTimer) {
          clearTimeout(debounceTimer)
        }
        onSearch?.(value)
      }
    },
    [onSearch, value, debounceTimer]
  )

  return (
    <MotionInputGroup
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      <InputLeftElement pointerEvents="none">
        <MdSearch color="gray.400" />
      </InputLeftElement>
      
      <Input
        value={value}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        bg={bgColor}
        borderColor={borderColor}
        _hover={{ borderColor: 'posco.300' }}
        _focus={{ borderColor: 'posco.500', boxShadow: '0 0 0 1px var(--chakra-colors-posco-500)' }}
        {...props}
      />
      
      {showClearButton && value && (
        <InputRightElement>
          <IconButton
            aria-label="검색어 지우기"
            icon={<MdClear />}
            size="sm"
            variant="ghost"
            onClick={handleClear}
            _hover={{ bg: 'gray.100', _dark: { bg: 'gray.600' } }}
          />
        </InputRightElement>
      )}
    </MotionInputGroup>
  )
}

export default SearchInput