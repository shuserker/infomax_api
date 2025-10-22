#!/usr/bin/env python3
"""
WebSocket 실시간 통신 테스트
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketTester:
    def __init__(self, url: str = "ws://localhost:8000/ws"):
        self.url = url
        self.websocket = None
        self.is_connected = False
        self.received_messages = []
        
    async def connect(self):
        """WebSocket 서버에 연결"""
        try:
            logger.info(f"WebSocket 서버 연결 시도: {self.url}")
            self.websocket = await websockets.connect(self.url)
            self.is_connected = True
            logger.info("WebSocket 연결 성공")
            return True
        except Exception as e:
            logger.error(f"WebSocket 연결 실패: {e}")
            return False
    
    async def disconnect(self):
        """WebSocket 연결 해제"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("WebSocket 연결 해제")
    
    async def send_message(self, message: Dict[str, Any]):
        """메시지 전송"""
        if not self.is_connected or not self.websocket:
            logger.error("WebSocket이 연결되지 않음")
            return False
        
        try:
            message_str = json.dumps(message, default=str, ensure_ascii=False)
            await self.websocket.send(message_str)
            logger.info(f"메시지 전송: {message['type']}")
            return True
        except Exception as e:
            logger.error(f"메시지 전송 실패: {e}")
            return False
    
    async def receive_messages(self, duration: int = 10):
        """메시지 수신 (지정된 시간 동안)"""
        if not self.is_connected or not self.websocket:
            logger.error("WebSocket이 연결되지 않음")
            return
        
        logger.info(f"{duration}초 동안 메시지 수신 대기...")
        end_time = asyncio.get_event_loop().time() + duration
        
        try:
            while asyncio.get_event_loop().time() < end_time:
                try:
                    # 1초 타임아웃으로 메시지 수신
                    message = await asyncio.wait_for(
                        self.websocket.recv(), 
                        timeout=1.0
                    )
                    
                    # JSON 파싱
                    try:
                        parsed_message = json.loads(message)
                        self.received_messages.append(parsed_message)
                        
                        logger.info(f"메시지 수신: {parsed_message.get('type', 'unknown')}")
                        self._print_message_details(parsed_message)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"JSON 파싱 실패: {message}")
                        
                except asyncio.TimeoutError:
                    # 타임아웃은 정상적인 상황 (메시지가 없을 때)
                    continue
                    
        except Exception as e:
            logger.error(f"메시지 수신 중 오류: {e}")
    
    def _print_message_details(self, message: Dict[str, Any]):
        """메시지 상세 정보 출력"""
        msg_type = message.get('type', 'unknown')
        timestamp = message.get('timestamp', 'unknown')
        data = message.get('data', {})
        
        print(f"  📨 타입: {msg_type}")
        print(f"  🕐 시간: {timestamp}")
        
        if msg_type == 'metrics_update':
            print(f"  💻 CPU: {data.get('cpu_percent', 0):.1f}%")
            print(f"  🧠 메모리: {data.get('memory_percent', 0):.1f}%")
            print(f"  💾 디스크: {data.get('disk_usage', 0):.1f}%")
            print(f"  🌐 네트워크: {data.get('network_status', 'unknown')}")
            print(f"  🔗 연결 수: {data.get('connection_count', 0)}")
            
        elif msg_type == 'services_update':
            services = data.get('services', [])
            print(f"  🔧 서비스 수: {len(services)}")
            for service in services:
                status_emoji = {
                    'running': '🟢',
                    'stopped': '🔴', 
                    'error': '❌',
                    'idle': '🟡'
                }.get(service.get('status', 'unknown'), '⚪')
                print(f"    {status_emoji} {service.get('name', service.get('id', 'unknown'))}: {service.get('status', 'unknown')}")
                
        elif msg_type == 'service_event':
            service_id = data.get('service_id', 'unknown')
            event_type = data.get('event_type', 'unknown')
            message_text = data.get('message', '')
            print(f"  🔧 서비스: {service_id}")
            print(f"  📋 이벤트: {event_type}")
            print(f"  💬 메시지: {message_text}")
            
        elif msg_type == 'alert':
            alert_type = data.get('alert_type', 'unknown')
            severity = data.get('severity', 'info')
            message_text = data.get('message', '')
            severity_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌'
            }.get(severity, 'ℹ️')
            print(f"  {severity_emoji} 알림: {alert_type}")
            print(f"  💬 메시지: {message_text}")
            
        print()  # 빈 줄 추가
    
    def get_message_summary(self):
        """수신된 메시지 요약"""
        if not self.received_messages:
            return "수신된 메시지가 없습니다"
        
        message_types = {}
        for msg in self.received_messages:
            msg_type = msg.get('type', 'unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        summary = f"총 {len(self.received_messages)}개 메시지 수신:\n"
        for msg_type, count in message_types.items():
            summary += f"  - {msg_type}: {count}개\n"
        
        return summary

async def test_basic_connection():
    """기본 연결 테스트"""
    print("🔗 기본 WebSocket 연결 테스트")
    print("=" * 50)
    
    tester = WebSocketTester()
    
    # 연결 테스트
    if not await tester.connect():
        print("❌ 연결 실패")
        return False
    
    # 10초 동안 메시지 수신
    await tester.receive_messages(10)
    
    # 연결 해제
    await tester.disconnect()
    
    # 결과 요약
    print("\n📊 테스트 결과:")
    print(tester.get_message_summary())
    
    return True

async def test_client_messages():
    """클라이언트 메시지 전송 테스트"""
    print("\n📤 클라이언트 메시지 전송 테스트")
    print("=" * 50)
    
    tester = WebSocketTester()
    
    if not await tester.connect():
        print("❌ 연결 실패")
        return False
    
    # 다양한 메시지 전송 테스트
    test_messages = [
        {
            "type": "subscribe",
            "subscription": "metrics",
            "timestamp": datetime.now().isoformat()
        },
        {
            "type": "request_status",
            "timestamp": datetime.now().isoformat()
        },
        {
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    for message in test_messages:
        await tester.send_message(message)
        await asyncio.sleep(1)  # 1초 대기
    
    # 응답 메시지 수신
    await tester.receive_messages(5)
    
    await tester.disconnect()
    
    print("\n📊 테스트 결과:")
    print(tester.get_message_summary())
    
    return True

async def test_multiple_clients():
    """다중 클라이언트 연결 테스트"""
    print("\n👥 다중 클라이언트 연결 테스트")
    print("=" * 50)
    
    # 3개의 클라이언트 생성
    clients = []
    for i in range(3):
        client = WebSocketTester(f"ws://localhost:8000/ws?client_id=test_client_{i+1}")
        clients.append(client)
    
    # 모든 클라이언트 연결
    connected_clients = []
    for i, client in enumerate(clients):
        if await client.connect():
            connected_clients.append(client)
            print(f"✅ 클라이언트 {i+1} 연결 성공")
        else:
            print(f"❌ 클라이언트 {i+1} 연결 실패")
    
    if not connected_clients:
        print("❌ 연결된 클라이언트가 없습니다")
        return False
    
    # 각 클라이언트에서 메시지 수신
    tasks = []
    for client in connected_clients:
        task = asyncio.create_task(client.receive_messages(8))
        tasks.append(task)
    
    # 모든 태스크 완료 대기
    await asyncio.gather(*tasks)
    
    # 모든 클라이언트 연결 해제
    for client in connected_clients:
        await client.disconnect()
    
    # 결과 요약
    print("\n📊 다중 클라이언트 테스트 결과:")
    for i, client in enumerate(connected_clients):
        print(f"클라이언트 {i+1}:")
        print(f"  {client.get_message_summary()}")
    
    return True

async def main():
    """메인 테스트 함수"""
    print("🚀 WebSocket 실시간 통신 테스트 시작")
    print("=" * 60)
    
    try:
        # 기본 연결 테스트
        await test_basic_connection()
        
        await asyncio.sleep(2)
        
        # 클라이언트 메시지 전송 테스트
        await test_client_messages()
        
        await asyncio.sleep(2)
        
        # 다중 클라이언트 테스트
        await test_multiple_clients()
        
        print("\n✅ 모든 WebSocket 테스트 완료")
        
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 테스트 중단")
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        logger.error(f"테스트 오류: {e}", exc_info=True)

if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(main())