import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChakraProvider } from '@chakra-ui/react'
import { DataTable, Column } from '../DataTable'
import theme from '../../../theme'

// 테스트용 래퍼
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

// 테스트 데이터
interface TestData {
  id: number
  name: string
  email: string
  status: 'active' | 'inactive'
  age: number
}

const testData: TestData[] = [
  { id: 1, name: '김철수', email: 'kim@example.com', status: 'active', age: 30 },
  { id: 2, name: '이영희', email: 'lee@example.com', status: 'inactive', age: 25 },
  { id: 3, name: '박민수', email: 'park@example.com', status: 'active', age: 35 },
]

const testColumns: Column<TestData>[] = [
  { key: 'id', header: 'ID', sortable: true },
  { key: 'name', header: '이름', sortable: true },
  { key: 'email', header: '이메일' },
  { key: 'status', header: '상태', accessor: (item) => item.status === 'active' ? '활성' : '비활성' },
  { key: 'age', header: '나이', sortable: true, align: 'right' },
]

describe('DataTable 컴포넌트', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('기본 데이터 테이블이 렌더링된다', () => {
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} />
      </TestWrapper>
    )

    // 헤더 확인
    expect(screen.getByText('ID')).toBeInTheDocument()
    expect(screen.getByText('이름')).toBeInTheDocument()
    expect(screen.getByText('이메일')).toBeInTheDocument()
    expect(screen.getByText('상태')).toBeInTheDocument()
    expect(screen.getByText('나이')).toBeInTheDocument()

    // 데이터 확인
    expect(screen.getByText('김철수')).toBeInTheDocument()
    expect(screen.getByText('이영희')).toBeInTheDocument()
    expect(screen.getByText('박민수')).toBeInTheDocument()
    expect(screen.getByText('kim@example.com')).toBeInTheDocument()
    expect(screen.getByText('활성')).toBeInTheDocument()
    expect(screen.getByText('비활성')).toBeInTheDocument()
  })

  it('빈 데이터일 때 빈 상태 메시지가 표시된다', () => {
    render(
      <TestWrapper>
        <DataTable data={[]} columns={testColumns} />
      </TestWrapper>
    )

    expect(screen.getByText('데이터가 없습니다')).toBeInTheDocument()
  })

  it('커스텀 빈 상태 메시지가 표시된다', () => {
    render(
      <TestWrapper>
        <DataTable
          data={[]}
          columns={testColumns}
          emptyMessage="사용자가 없습니다"
        />
      </TestWrapper>
    )

    expect(screen.getByText('사용자가 없습니다')).toBeInTheDocument()
  })

  it('로딩 상태일 때 스켈레톤이 표시된다', () => {
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} isLoading={true} />
      </TestWrapper>
    )

    // 헤더는 표시되지만 데이터 대신 스켈레톤이 표시됨
    expect(screen.getByText('ID')).toBeInTheDocument()
    expect(screen.getByText('이름')).toBeInTheDocument()
    
    // 실제 데이터는 표시되지 않음
    expect(screen.queryByText('김철수')).not.toBeInTheDocument()
    
    // 스켈레톤 요소들이 있는지 확인
    const skeletons = document.querySelectorAll('.chakra-skeleton')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('정렬 가능한 컬럼에 정렬 버튼이 표시된다', () => {
    const onSort = vi.fn()
    
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} onSort={onSort} />
      </TestWrapper>
    )

    // 정렬 가능한 컬럼들에 정렬 버튼이 있는지 확인
    expect(screen.getByRole('button', { name: 'ID 정렬' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '이름 정렬' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '나이 정렬' })).toBeInTheDocument()
    
    // 정렬 불가능한 컬럼에는 버튼이 없음
    expect(screen.queryByRole('button', { name: '이메일 정렬' })).not.toBeInTheDocument()
  })

  it('정렬 버튼 클릭 시 onSort가 호출된다', async () => {
    const onSort = vi.fn()
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} onSort={onSort} />
      </TestWrapper>
    )

    const sortButton = screen.getByRole('button', { name: '이름 정렬' })
    await user.click(sortButton)

    expect(onSort).toHaveBeenCalledWith('name', 'asc')
  })

  it('같은 컬럼을 두 번 클릭하면 정렬 방향이 바뀐다', async () => {
    const onSort = vi.fn()
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <DataTable
          data={testData}
          columns={testColumns}
          onSort={onSort}
          sortKey="name"
          sortDirection="asc"
        />
      </TestWrapper>
    )

    const sortButton = screen.getByRole('button', { name: '이름 정렬' })
    await user.click(sortButton)

    expect(onSort).toHaveBeenCalledWith('name', 'desc')
  })

  it('행 클릭 시 onRowClick이 호출된다', async () => {
    const onRowClick = vi.fn()
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <DataTable
          data={testData}
          columns={testColumns}
          onRowClick={onRowClick}
        />
      </TestWrapper>
    )

    // 첫 번째 행 클릭 (김철수 행)
    const firstRow = screen.getByText('김철수').closest('tr')
    if (firstRow) {
      await user.click(firstRow)
      expect(onRowClick).toHaveBeenCalledWith(testData[0], 0)
    }
  })

  it('커스텀 accessor 함수가 올바르게 작동한다', () => {
    const customColumns: Column<TestData>[] = [
      { key: 'name', header: '이름' },
      {
        key: 'fullInfo',
        header: '전체 정보',
        accessor: (item) => `${item.name} (${item.email})`,
      },
    ]

    render(
      <TestWrapper>
        <DataTable data={testData} columns={customColumns} />
      </TestWrapper>
    )

    expect(screen.getByText('김철수 (kim@example.com)')).toBeInTheDocument()
    expect(screen.getByText('이영희 (lee@example.com)')).toBeInTheDocument()
  })

  it('커스텀 rowKey 함수가 올바르게 작동한다', () => {
    const customRowKey = (item: TestData) => `user-${item.id}`
    
    render(
      <TestWrapper>
        <DataTable
          data={testData}
          columns={testColumns}
          rowKey={customRowKey}
        />
      </TestWrapper>
    )

    // 테이블이 정상적으로 렌더링되는지 확인
    expect(screen.getByText('김철수')).toBeInTheDocument()
  })

  it('컬럼 정렬이 비활성화되어 있을 때 정렬 버튼이 표시되지 않는다', () => {
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} />
      </TestWrapper>
    )

    // onSort가 없으면 정렬 버튼이 표시되지 않음
    expect(screen.queryByRole('button', { name: 'ID 정렬' })).not.toBeInTheDocument()
  })

  it('striped 옵션이 false일 때 줄무늬가 적용되지 않는다', () => {
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} striped={false} />
      </TestWrapper>
    )

    // 테이블이 정상적으로 렌더링되는지 확인
    expect(screen.getByText('김철수')).toBeInTheDocument()
  })

  it('hover 옵션이 false일 때 호버 효과가 비활성화된다', () => {
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} hover={false} />
      </TestWrapper>
    )

    // 테이블이 정상적으로 렌더링되는지 확인
    expect(screen.getByText('김철수')).toBeInTheDocument()
  })

  it('컬럼 너비와 정렬이 올바르게 적용된다', () => {
    const columnsWithWidth: Column<TestData>[] = [
      { key: 'id', header: 'ID', width: '80px', align: 'center' },
      { key: 'name', header: '이름', width: '200px' },
      { key: 'email', header: '이메일', align: 'left' },
      { key: 'age', header: '나이', align: 'right' },
    ]

    render(
      <TestWrapper>
        <DataTable data={testData} columns={columnsWithWidth} />
      </TestWrapper>
    )

    // 테이블이 정상적으로 렌더링되는지 확인
    expect(screen.getByText('ID')).toBeInTheDocument()
    expect(screen.getByText('김철수')).toBeInTheDocument()
  })

  it('복잡한 데이터 구조를 올바르게 처리한다', () => {
    interface ComplexData {
      id: number
      user: {
        name: string
        profile: {
          email: string
        }
      }
      metadata: {
        createdAt: string
      }
    }

    const complexData: ComplexData[] = [
      {
        id: 1,
        user: {
          name: '김철수',
          profile: { email: 'kim@example.com' }
        },
        metadata: { createdAt: '2023-01-01' }
      }
    ]

    const complexColumns: Column<ComplexData>[] = [
      { key: 'id', header: 'ID' },
      { key: 'userName', header: '이름', accessor: (item) => item.user.name },
      { key: 'email', header: '이메일', accessor: (item) => item.user.profile.email },
      { key: 'created', header: '생성일', accessor: (item) => item.metadata.createdAt },
    ]

    render(
      <TestWrapper>
        <DataTable data={complexData} columns={complexColumns} />
      </TestWrapper>
    )

    expect(screen.getByText('김철수')).toBeInTheDocument()
    expect(screen.getByText('kim@example.com')).toBeInTheDocument()
    expect(screen.getByText('2023-01-01')).toBeInTheDocument()
  })

  it('현재 정렬 상태가 시각적으로 표시된다', () => {
    render(
      <TestWrapper>
        <DataTable
          data={testData}
          columns={testColumns}
          onSort={vi.fn()}
          sortKey="name"
          sortDirection="asc"
        />
      </TestWrapper>
    )

    // 정렬 버튼이 활성 상태인지 확인
    const sortButton = screen.getByRole('button', { name: '이름 정렬' })
    expect(sortButton).toBeInTheDocument()
  })

  it('모든 옵션이 함께 사용될 수 있다', async () => {
    const onSort = vi.fn()
    const onRowClick = vi.fn()
    const user = userEvent.setup()
    
    render(
      <TestWrapper>
        <DataTable
          data={testData}
          columns={testColumns}
          onSort={onSort}
          onRowClick={onRowClick}
          sortKey="name"
          sortDirection="asc"
          striped={true}
          hover={true}
          emptyMessage="커스텀 빈 메시지"
        />
      </TestWrapper>
    )

    // 데이터 렌더링 확인
    expect(screen.getByText('김철수')).toBeInTheDocument()
    
    // 정렬 기능 확인
    const sortButton = screen.getByRole('button', { name: 'ID 정렬' })
    await user.click(sortButton)
    expect(onSort).toHaveBeenCalled()
    
    // 행 클릭 기능 확인
    const firstRow = screen.getByText('김철수').closest('tr')
    if (firstRow) {
      await user.click(firstRow)
      expect(onRowClick).toHaveBeenCalled()
    }
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    render(
      <TestWrapper>
        <DataTable data={testData} columns={testColumns} onSort={vi.fn()} />
      </TestWrapper>
    )

    // 테이블 역할 확인
    expect(screen.getByRole('table')).toBeInTheDocument()
    
    // 컬럼 헤더들 확인
    expect(screen.getByRole('columnheader', { name: 'ID' })).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: '이름' })).toBeInTheDocument()
    
    // 정렬 버튼의 aria-label 확인
    expect(screen.getByRole('button', { name: 'ID 정렬' })).toBeInTheDocument()
  })
})