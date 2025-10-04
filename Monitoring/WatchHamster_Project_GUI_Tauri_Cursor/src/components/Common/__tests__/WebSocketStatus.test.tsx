/**
 * WebSocketStatus 컴포넌트 테스트
 */

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { describe, it, expect, vi } from 'vitest'
import { WebSocketStatus } from '../WebSocketStatus'

const renderWithChakra = (component: React.ReactElement) => {
  return render(
    <ChakraProvider>
      {component}
    </ChakraProvider>
  )
}

describe('WebSocketStatus', () => {
  it('연결된 상태를 올바르게 표시해야 함', () => {
    renderWithChakra(
      <WebSocketStatus
        isConnected={true}
        connectionStatus="connected"
        reconnectAttempts={0}
      />
    )

    expect(screen.getByText('연결됨')).toBeInTheDocument()
    expect(screen.getByText('WebSocket 연결')).toBeInTheDocument()
  })

  it('연결 해제된 상태를 올바르게 표시해야 함', () => {
    renderWithChakra(
      <WebSocketStatus
        isConnected={false}
        connectionStatus="disconnected"
        reconnectAttempts={0}
      />
    )

    expect(screen.getByText('연결 해제')).toBeInTheDocument()
  })

  it('재연결 중 상태를 올바르게 표시해야 함', () => {
    renderWithChakra(
      <WebSocketStatus
        isConnected={false}
        connectionStatus="reconnecting"
        reconnectAttempts={2}
      />
    )

    expect(screen.getByText('재연결 중')).toBeInTheDocument()
  })

  it('재연결 버튼이 작동해야 함', () => {
    const onReconnect = vi.fn()
    
    renderWithChakra(
      <WebSocketStatus
        isConnected={false}
        connectionStatus="disconnected"
        reconnectAttempts={0}
        onReconnect={onReconnect}
      />
    )

    const reconnectButton = screen.getByText('재연결')
    fireEvent.click(reconnectButton)

    expect(onReconnect).toHaveBeenCalled()
  })

  it('연결 해제 버튼이 작동해야 함', () => {
    const onDisconnect = vi.fn()
    
    renderWithChakra(
      <WebSocketStatus
        isConnected={true}
        connectionStatus="connected"
        reconnectAttempts={0}
        onDisconnect={onDisconnect}
      />
    )

    const disconnectButton = screen.getByText('연결 해제')
    fireEvent.click(disconnectButton)

    expect(onDisconnect).toHaveBeenCalled()
  })

  it('컴팩트 모드에서 올바르게 렌더링되어야 함', () => {
    renderWithChakra(
      <WebSocketStatus
        isConnected={true}
        connectionStatus="connected"
        reconnectAttempts={0}
        compact={true}
      />
    )

    expect(screen.getByText('연결됨')).toBeInTheDocument()
    // 컴팩트 모드에서는 상세 정보가 표시되지 않음
    expect(screen.queryByText('WebSocket 연결')).not.toBeInTheDocument()
  })

  it('상세 정보를 토글할 수 있어야 함', () => {
    renderWithChakra(
      <WebSocketStatus
        isConnected={true}
        connectionStatus="connected"
        reconnectAttempts={1}
        showDetails={true}
        lastHeartbeat={new Date()}
      />
    )

    // 상세 정보 토글 버튼 클릭
    const toggleButton = screen.getByLabelText('상세 정보 토글')
    fireEvent.click(toggleButton)

    // 상세 정보가 표시되는지 확인
    expect(screen.getByText(/재연결 시도:/)).toBeInTheDocument()
    expect(screen.getByText(/마지막 하트비트:/)).toBeInTheDocument()
  })

  it('에러 상태를 올바르게 표시해야 함', () => {
    renderWithChakra(
      <WebSocketStatus
        isConnected={false}
        connectionStatus="error"
        reconnectAttempts={0}
        showDetails={true}
      />
    )

    expect(screen.getByText('연결 실패')).toBeInTheDocument()
  })

  it('마지막 하트비트 시간을 포맷팅해야 함', () => {
    const lastHeartbeat = new Date(Date.now() - 30000) // 30초 전
    
    renderWithChakra(
      <WebSocketStatus
        isConnected={true}
        connectionStatus="connected"
        reconnectAttempts={0}
        showDetails={true}
        lastHeartbeat={lastHeartbeat}
      />
    )

    // 상세 정보 토글
    const toggleButton = screen.getByLabelText('상세 정보 토글')
    fireEvent.click(toggleButton)

    expect(screen.getByText(/30초 전/)).toBeInTheDocument()
  })
})