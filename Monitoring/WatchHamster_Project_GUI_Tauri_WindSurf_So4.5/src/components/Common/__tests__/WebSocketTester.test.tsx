/**
 * WebSocketTester 컴포넌트 테스트
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { WebSocketTester } from '../WebSocketTester'

// useRealtimeMessages 훅 모킹
const mockUseRealtimeMessages = {
  isConnected: false,
  connectionStatus: 'disconnected',
  sendMessage: vi.fn(),
  connect: vi.fn(),
  disconnect: vi.fn(),
  reconnect: vi.fn(),
  subscribe: vi.fn(),
  requestStatus: vi.fn(),
}

vi.mock('../../hooks/useRealtimeMessages', () => ({
  useRealtimeMessages: () => mockUseRealtimeMessages,
}))

const renderWithChakra = (component: React.ReactElement) => {
  return render(
    <ChakraProvider>
      {component}
    </ChakraProvider>
  )
}

describe('WebSocketTester', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseRealtimeMessages.isConnected = false
    mockUseRealtimeMessages.connectionStatus = 'disconnected'
  })

  it('기본 UI 요소들이 렌더링되어야 함', () => {
    renderWithChakra(<WebSocketTester />)

    expect(screen.getByText('WebSocket 테스트 도구')).toBeInTheDocument()
    expect(screen.getByText('연결')).toBeInTheDocument()
    expect(screen.getByText('연결 해제')).toBeInTheDocument()
    expect(screen.getByText('재연결')).toBeInTheDocument()
    expect(screen.getByText('전체 구독')).toBeInTheDocument()
    expect(screen.getByText('상태 요청')).toBeInTheDocument()
    expect(screen.getByText('메시지 전송')).toBeInTheDocument()
  })

  it('연결 상태에 따라 버튼이 활성화/비활성화되어야 함', () => {
    renderWithChakra(<WebSocketTester />)

    // 연결되지 않은 상태
    expect(screen.getByText('연결')).not.toBeDisabled()
    expect(screen.getByText('연결 해제')).toBeDisabled()
    expect(screen.getByText('전체 구독')).toBeDisabled()
    expect(screen.getByText('상태 요청')).toBeDisabled()
    expect(screen.getByText('메시지 전송')).toBeDisabled()
  })

  it('연결된 상태에서 버튼이 올바르게 활성화되어야 함', () => {
    mockUseRealtimeMessages.isConnected = true
    mockUseRealtimeMessages.connectionStatus = 'connected'

    renderWithChakra(<WebSocketTester />)

    expect(screen.getByText('연결')).toBeDisabled()
    expect(screen.getByText('연결 해제')).not.toBeDisabled()
    expect(screen.getByText('전체 구독')).not.toBeDisabled()
    expect(screen.getByText('상태 요청')).not.toBeDisabled()
    expect(screen.getByText('메시지 전송')).not.toBeDisabled()
  })

  it('연결 버튼을 클릭하면 connect 함수가 호출되어야 함', () => {
    renderWithChakra(<WebSocketTester />)

    const connectButton = screen.getByText('연결')
    fireEvent.click(connectButton)

    expect(mockUseRealtimeMessages.connect).toHaveBeenCalled()
  })

  it('연결 해제 버튼을 클릭하면 disconnect 함수가 호출되어야 함', () => {
    mockUseRealtimeMessages.isConnected = true
    mockUseRealtimeMessages.connectionStatus = 'connected'

    renderWithChakra(<WebSocketTester />)

    const disconnectButton = screen.getByText('연결 해제')
    fireEvent.click(disconnectButton)

    expect(mockUseRealtimeMessages.disconnect).toHaveBeenCalled()
  })

  it('재연결 버튼을 클릭하면 reconnect 함수가 호출되어야 함', () => {
    renderWithChakra(<WebSocketTester />)

    const reconnectButton = screen.getByText('재연결')
    fireEvent.click(reconnectButton)

    expect(mockUseRealtimeMessages.reconnect).toHaveBeenCalled()
  })

  it('전체 구독 버튼을 클릭하면 subscribe 함수가 호출되어야 함', () => {
    mockUseRealtimeMessages.isConnected = true
    mockUseRealtimeMessages.connectionStatus = 'connected'

    renderWithChakra(<WebSocketTester />)

    const subscribeButton = screen.getByText('전체 구독')
    fireEvent.click(subscribeButton)

    expect(mockUseRealtimeMessages.subscribe).toHaveBeenCalledWith('all')
  })

  it('상태 요청 버튼을 클릭하면 requestStatus 함수가 호출되어야 함', () => {
    mockUseRealtimeMessages.isConnected = true
    mockUseRealtimeMessages.connectionStatus = 'connected'

    renderWithChakra(<WebSocketTester />)

    const statusButton = screen.getByText('상태 요청')
    fireEvent.click(statusButton)

    expect(mockUseRealtimeMessages.requestStatus).toHaveBeenCalled()
  })

  it('메시지 타입을 선택할 수 있어야 함', () => {
    renderWithChakra(<WebSocketTester />)

    const select = screen.getByDisplayValue('Ping')
    fireEvent.change(select, { target: { value: 'subscribe' } })

    expect(select).toHaveValue('subscribe')
  })

  it('메시지 데이터를 입력할 수 있어야 함', () => {
    renderWithChakra(<WebSocketTester />)

    const textarea = screen.getByPlaceholderText('메시지 데이터 (JSON 형식)')
    fireEvent.change(textarea, { target: { value: '{"test": "data"}' } })

    expect(textarea).toHaveValue('{"test": "data"}')
  })

  it('메시지 전송 버튼을 클릭하면 sendMessage 함수가 호출되어야 함', async () => {
    mockUseRealtimeMessages.isConnected = true
    mockUseRealtimeMessages.connectionStatus = 'connected'
    mockUseRealtimeMessages.sendMessage.mockReturnValue(true)

    renderWithChakra(<WebSocketTester />)

    // 메시지 데이터 입력
    const textarea = screen.getByPlaceholderText('메시지 데이터 (JSON 형식)')
    fireEvent.change(textarea, { target: { value: '{"test": "data"}' } })

    // 메시지 전송
    const sendButton = screen.getByText('메시지 전송')
    fireEvent.click(sendButton)

    expect(mockUseRealtimeMessages.sendMessage).toHaveBeenCalledWith(
      'ping',
      { test: 'data' }
    )
  })

  it('잘못된 JSON 형식일 때 에러 토스트가 표시되어야 함', async () => {
    mockUseRealtimeMessages.isConnected = true
    mockUseRealtimeMessages.connectionStatus = 'connected'

    renderWithChakra(<WebSocketTester />)

    // 잘못된 JSON 데이터 입력
    const textarea = screen.getByPlaceholderText('메시지 데이터 (JSON 형식)')
    fireEvent.change(textarea, { target: { value: 'invalid json' } })

    // 메시지 전송 시도
    const sendButton = screen.getByText('메시지 전송')
    fireEvent.click(sendButton)

    // sendMessage가 호출되지 않아야 함
    expect(mockUseRealtimeMessages.sendMessage).not.toHaveBeenCalled()
  })

  it('로그 지우기 버튼이 작동해야 함', () => {
    renderWithChakra(<WebSocketTester />)

    const clearButton = screen.getByText('로그 지우기')
    fireEvent.click(clearButton)

    // 로그가 지워졌는지 확인
    expect(screen.getByText('메시지 로그가 없습니다.')).toBeInTheDocument()
  })

  it('연결 상태 배지가 올바르게 표시되어야 함', () => {
    mockUseRealtimeMessages.connectionStatus = 'connected'
    
    renderWithChakra(<WebSocketTester />)

    expect(screen.getByText('connected')).toBeInTheDocument()
  })

  it('템플릿 선택 시 메시지 데이터가 업데이트되어야 함', () => {
    renderWithChakra(<WebSocketTester />)

    const select = screen.getByDisplayValue('Ping')
    fireEvent.change(select, { target: { value: 'subscribe' } })

    const textarea = screen.getByPlaceholderText('메시지 데이터 (JSON 형식)')
    expect(textarea).toHaveValue('{"subscription": "all"}')
  })
})