import React from 'react'
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Box,
  Text,
  Flex,
  IconButton,
  useColorModeValue,
  Skeleton,
} from '@chakra-ui/react'
import { MdSort, MdSortByAlpha } from 'react-icons/md'
import { motion } from 'framer-motion'

const MotionTr = motion(Tr)

export interface Column<T = any> {
  key: string
  header: string
  accessor?: keyof T | ((item: T) => React.ReactNode)
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
}

export interface DataTableProps<T = any> {
  data: T[]
  columns: Column<T>[]
  isLoading?: boolean
  emptyMessage?: string
  onSort?: (key: string, direction: 'asc' | 'desc') => void
  sortKey?: string
  sortDirection?: 'asc' | 'desc'
  rowKey?: keyof T | ((item: T, index: number) => string | number)
  onRowClick?: (item: T, index: number) => void
  striped?: boolean
  hover?: boolean
}

/**
 * 데이터 테이블 컴포넌트
 * 정렬, 로딩 상태, 빈 상태를 지원하는 테이블
 */
export const DataTable = <T extends Record<string, any>>({
  data,
  columns,
  isLoading = false,
  emptyMessage = '데이터가 없습니다',
  onSort,
  sortKey,
  sortDirection,
  rowKey = 'id',
  onRowClick,
  striped = true,
  hover = true,
}: DataTableProps<T>) => {
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const stripedBg = useColorModeValue('gray.50', 'gray.800')
  const hoverBg = useColorModeValue('gray.100', 'gray.700')

  const getRowKey = (item: T, index: number): string | number => {
    if (typeof rowKey === 'function') {
      return rowKey(item, index)
    }
    return item[rowKey] || index
  }

  const getCellValue = (item: T, column: Column<T>) => {
    if (typeof column.accessor === 'function') {
      return column.accessor(item)
    }
    if (column.accessor) {
      return item[column.accessor]
    }
    return item[column.key]
  }

  const handleSort = (key: string) => {
    if (!onSort) return
    
    const newDirection = sortKey === key && sortDirection === 'asc' ? 'desc' : 'asc'
    onSort(key, newDirection)
  }

  const renderSortIcon = (column: Column<T>) => {
    if (!column.sortable || !onSort) return null

    const isActive = sortKey === column.key
    const icon = isActive && sortDirection === 'desc' ? MdSortByAlpha : MdSort

    return (
      <IconButton
        aria-label={`${column.header} 정렬`}
        icon={React.createElement(icon)}
        size="xs"
        variant="ghost"
        ml={2}
        opacity={isActive ? 1 : 0.5}
        _hover={{ opacity: 1 }}
        onClick={() => handleSort(column.key)}
      />
    )
  }

  if (isLoading) {
    return (
      <TableContainer>
        <Table variant="simple">
          <Thead>
            <Tr>
              {columns.map((column) => (
                <Th key={column.key} width={column.width} textAlign={column.align}>
                  {column.header}
                </Th>
              ))}
            </Tr>
          </Thead>
          <Tbody>
            {Array.from({ length: 5 }).map((_, index) => (
              <Tr key={index}>
                {columns.map((column) => (
                  <Td key={column.key}>
                    <Skeleton height="20px" />
                  </Td>
                ))}
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    )
  }

  if (data.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Text color="gray.500" fontSize="lg">
          {emptyMessage}
        </Text>
      </Box>
    )
  }

  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            {columns.map((column) => (
              <Th
                key={column.key}
                width={column.width}
                textAlign={column.align}
                borderColor={borderColor}
              >
                <Flex align="center" justify={column.align === 'center' ? 'center' : 'flex-start'}>
                  {column.header}
                  {renderSortIcon(column)}
                </Flex>
              </Th>
            ))}
          </Tr>
        </Thead>
        <Tbody>
          {data.map((item, index) => (
            <MotionTr
              key={getRowKey(item, index)}
              bg={striped && index % 2 === 1 ? stripedBg : 'transparent'}
              _hover={hover ? { bg: hoverBg } : {}}
              cursor={onRowClick ? 'pointer' : 'default'}
              onClick={() => onRowClick?.(item, index)}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
            >
              {columns.map((column) => (
                <Td
                  key={column.key}
                  textAlign={column.align}
                  borderColor={borderColor}
                >
                  {getCellValue(item, column)}
                </Td>
              ))}
            </MotionTr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  )
}

export default DataTable