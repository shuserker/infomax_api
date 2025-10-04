#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WatchHamster 24시간 서비스 스크립트

백그라운드에서 지속적으로 실행되는 모니터링 서비스
- 자동 시작/재시작
- 데몬 모드 지원
- 로그 파일 관리
- 시스템 트레이 통합 (선택)
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path
from datetime import datetime
import argparse

# 경로 설정
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

from core.watchhamster_core import WatchHamsterCore, MonitoringMode, SystemStatus
from ui.console_ui import ColorfulConsoleUI


class WatchHamster24HService:
    """24시간 WatchHamster 서비스"""

    def __init__(self, log_dir: Path = None):
        self.core = WatchHamsterCore()
        self.ui = ColorfulConsoleUI()
        self.running = False
        self.log_dir = log_dir or backend_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 로깅 설정
        self._setup_logging()
        
        # PID 파일
        self.pid_file = backend_dir / "data" / "watchhamster.pid"
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """로깅 설정"""
        log_file = self.log_dir / "watchhamster_24h.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)

    def write_pid(self):
        """PID 파일 작성"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        self.logger.info(f"PID {os.getpid()} written to {self.pid_file}")

    def remove_pid(self):
        """PID 파일 삭제"""
        if self.pid_file.exists():
            self.pid_file.unlink()
            self.logger.info("PID file removed")

    def is_running(self) -> bool:
        """서비스 실행 중인지 확인"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # 프로세스가 실제로 실행 중인지 확인
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            # 프로세스가 없거나 PID 파일이 잘못됨
            self.remove_pid()
            return False

    async def start_service(self):
        """서비스 시작"""
        if self.is_running():
            self.ui.print_error("서비스가 이미 실행 중입니다.")
            return False

        self.ui.print_info("24시간 WatchHamster 서비스 시작 중...")
        
        # PID 파일 작성
        self.write_pid()
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 시스템 초기화
        self.logger.info("Initializing WatchHamster Core...")
        success = await self.core.initialize()
        
        if not success:
            self.ui.print_error("시스템 초기화 실패")
            self.remove_pid()
            return False
        
        # 모니터링 시작
        self.logger.info("Starting 24h monitoring service...")
        success = await self.core.start_monitoring(MonitoringMode.SERVICE_24H)
        
        if not success:
            self.ui.print_error("모니터링 시작 실패")
            self.remove_pid()
            return False
        
        self.running = True
        self.ui.print_success(
            "24시간 서비스 시작 완료!",
            f"PID: {os.getpid()}"
        )
        
        # 메인 루프
        try:
            await self._main_loop()
        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)
        finally:
            await self.stop_service()
        
        return True

    async def _main_loop(self):
        """메인 서비스 루프"""
        self.logger.info("Entering main service loop...")
        
        check_interval = 60  # 1분마다 상태 체크
        
        while self.running:
            try:
                # 시스템 상태 확인
                status = await self.core.get_system_status()
                
                # 상태 로깅
                if status.status == SystemStatus.RUNNING:
                    self.logger.info(
                        f"Service healthy - Active monitors: {len(status.active_monitors)}, "
                        f"Healthy: {status.healthy_monitors}/{status.total_monitors}"
                    )
                else:
                    self.logger.warning(f"Service status: {status.status.value}")
                
                # 오류 체크
                if status.error_count > 0:
                    self.logger.warning(f"Error count: {status.error_count}")
                    if status.last_error:
                        self.logger.error(f"Last error: {status.last_error}")
                
                # 대기
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Service loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(check_interval)

    async def stop_service(self):
        """서비스 중지"""
        self.logger.info("Stopping 24h service...")
        self.running = False
        
        # 모니터링 중지
        await self.core.stop_monitoring()
        
        # 시스템 종료
        await self.core.shutdown()
        
        # PID 파일 삭제
        self.remove_pid()
        
        self.ui.print_success("서비스가 안전하게 중지되었습니다.")
        self.logger.info("Service stopped successfully")

    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        self.logger.info(f"Received signal {signum}")
        self.running = False

    async def status(self):
        """서비스 상태 확인"""
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            self.ui.print_success(
                "서비스 실행 중",
                f"PID: {pid}"
            )
            
            # 상태 파일에서 추가 정보 로드
            try:
                from core.state_manager import StateManager
                sm = StateManager()
                state = sm.load_state()
                
                if state:
                    self.ui.console.print("\n[bold cyan]상태 정보:[/bold cyan]")
                    status_dict = {
                        "실행 중": state.get("watchhamster_running", False),
                        "모드": state.get("mode", "N/A"),
                        "오류 카운트": state.get("error_count", 0),
                    }
                    self.ui.print_status(status_dict)
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")
        else:
            self.ui.print_warning("서비스가 실행 중이 아닙니다.")

    async def restart(self):
        """서비스 재시작"""
        self.ui.print_info("서비스 재시작 중...")
        
        if self.is_running():
            # 기존 프로세스 중지
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, signal.SIGTERM)
                self.logger.info(f"Sent SIGTERM to PID {pid}")
                
                # 프로세스가 종료될 때까지 대기
                import time
                for _ in range(10):
                    if not self.is_running():
                        break
                    time.sleep(1)
                else:
                    # 강제 종료
                    os.kill(pid, signal.SIGKILL)
                    self.logger.warning(f"Force killed PID {pid}")
            except OSError as e:
                self.logger.error(f"Failed to stop process: {e}")
        
        # 재시작
        await self.start_service()


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="WatchHamster 24시간 서비스")
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status'],
        help='서비스 명령'
    )
    parser.add_argument(
        '--log-dir',
        type=Path,
        help='로그 디렉토리 경로'
    )
    
    args = parser.parse_args()
    
    service = WatchHamster24HService(log_dir=args.log_dir)
    
    if args.command == 'start':
        await service.start_service()
    elif args.command == 'stop':
        if service.is_running():
            with open(service.pid_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                service.ui.print_success("중지 신호 전송 완료")
            except OSError as e:
                service.ui.print_error(f"중지 실패: {e}")
        else:
            service.ui.print_warning("실행 중인 서비스가 없습니다.")
    elif args.command == 'restart':
        await service.restart()
    elif args.command == 'status':
        await service.status()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
        sys.exit(0)
