#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WatchHamster 모니터링 실행 스크립트 (CLI 모드)

기존 WatchHamster_Project의 로직을 활용한 컬러풀한 CLI 인터페이스
- 옵션 1-8 지원
- 컬러풀한 메뉴 UI
- 실시간 상태 표시
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# 경로 설정
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

# 기존 WatchHamster_Project 경로 추가
watchhamster_project = Path(__file__).parents[4] / "WatchHamster_Project"
if watchhamster_project.exists():
    sys.path.insert(0, str(watchhamster_project))

from ui.console_ui import ColorfulConsoleUI
from ui.status_formatter import StatusFormatter
from ui.progress_indicator import ProgressIndicator
from core.watchhamster_core import WatchHamsterCore, MonitoringMode


class WatchHamsterCLI:
    """WatchHamster CLI 인터페이스"""

    def __init__(self):
        self.ui = ColorfulConsoleUI()
        self.formatter = StatusFormatter()
        self.indicator = ProgressIndicator()
        self.core = WatchHamsterCore()
        self.running = False

    def clear_screen(self):
        """화면 지우기"""
        self.ui.clear()

    def print_banner(self):
        """배너 출력"""
        self.ui.print_banner("🐹 POSCO WatchHamster v3.0")
        self.ui.console.print(
            f"[dim]현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}[/dim]\n"
        )

    def print_main_menu(self):
        """메인 메뉴 출력"""
        self.ui.print_header("메인 메뉴", style="info")
        
        options = [
            "🌐 뉴욕마켓워치 모니터링",
            "📈 증시마감 모니터링",
            "💱 서환마감 모니터링",
            "🔄 통합 모니터링 (1회 실행)",
            "🤖 스마트 모니터링 (시간대별)",
            "🚀 24시간 서비스 시작",
            "⚙️  설정 관리",
            "🚪 종료"
        ]
        
        self.ui.print_menu(options)

    async def run_individual_monitor(self, monitor_type: str):
        """개별 모니터 실행"""
        self.ui.print_info(f"{monitor_type} 모니터링 시작...")
        
        # 시스템 초기화
        if not self.core._initialized:
            with self.indicator.start_spinner_sync("시스템 초기화 중...", style="dots"):
                success = await self.core.initialize()
            
            if not success:
                self.ui.print_error("시스템 초기화 실패")
                return False

        # 모니터링 시작
        self.indicator.print_step(1, 3, "모니터링 프로세스 시작 중...")
        success = await self.core.start_monitoring(
            MonitoringMode.INDIVIDUAL,
            monitors=[monitor_type]
        )
        
        if success:
            self.indicator.print_step(2, 3, "모니터 상태 확인 중...")
            await asyncio.sleep(1)
            
            # 상태 표시
            status = await self.core.get_system_status()
            self.indicator.print_step(3, 3, "모니터링 실행 중...")
            
            self.ui.console.print("\n[bold cyan]현재 상태:[/bold cyan]")
            status_dict = {
                "시스템 상태": status.status.value,
                "모드": status.mode.value if status.mode else "N/A",
                "활성 모니터": len(status.active_monitors),
                "정상 모니터": status.healthy_monitors,
            }
            self.ui.print_status(status_dict, highlight=True)
            
            self.ui.print_success(
                f"{monitor_type} 모니터링 시작 완료!",
                "백그라운드에서 실행 중입니다."
            )
            
            # 실시간 모니터링 (간단한 데모)
            self.ui.console.print("\n[dim]Ctrl+C를 눌러 중지하세요...[/dim]\n")
            try:
                for i in range(10):
                    await asyncio.sleep(2)
                    self.ui.console.print(f"[dim]{datetime.now().strftime('%H:%M:%S')}[/dim] - 모니터링 중... {i+1}/10")
            except KeyboardInterrupt:
                self.ui.console.print("\n[yellow]사용자가 중지했습니다.[/yellow]")
            
            # 중지
            await self.core.stop_monitoring()
            self.indicator.print_completion("모니터링 완료")
            
        else:
            self.ui.print_error("모니터링 시작 실패")
        
        return success

    async def run_integrated_monitoring(self):
        """통합 모니터링 (1회)"""
        self.ui.print_info("통합 모니터링 시작 (1회 실행)...")
        
        if not self.core._initialized:
            await self.core.initialize()
        
        success = await self.core.start_monitoring(MonitoringMode.INTEGRATED)
        
        if success:
            self.ui.print_success("통합 모니터링 완료!")
            await self.core.stop_monitoring()
        else:
            self.ui.print_error("통합 모니터링 실패")
        
        return success

    async def run_smart_monitoring(self):
        """스마트 모니터링 (시간대별)"""
        self.ui.print_info("스마트 모니터링 시작...")
        self.ui.print_warning(
            "시간대별 자동 실행",
            "운영시간: 09:00-18:00 | 집중시간: 14:00-16:00"
        )
        
        if not self.core._initialized:
            await self.core.initialize()
        
        success = await self.core.start_monitoring(MonitoringMode.SMART)
        
        if success:
            self.ui.print_success("스마트 모니터링 시작 완료!")
            
            # 데모용 실행
            try:
                for i in range(5):
                    await asyncio.sleep(3)
                    time_info = self.formatter.format_time_info(
                        datetime.now(),
                        datetime.now()
                    )
                    self.ui.console.print(time_info)
            except KeyboardInterrupt:
                self.ui.console.print("\n[yellow]중지됨[/yellow]")
            
            await self.core.stop_monitoring()
        else:
            self.ui.print_error("스마트 모니터링 시작 실패")
        
        return success

    async def start_24h_service(self):
        """24시간 서비스 시작"""
        self.ui.print_warning(
            "24시간 서비스 모드",
            "이 모드는 백그라운드에서 지속 실행됩니다."
        )
        
        self.ui.console.print("\n[bold yellow]주의:[/bold yellow]")
        self.ui.console.print("- 시스템이 재부팅되면 자동으로 재시작됩니다.")
        self.ui.console.print("- 중지하려면 'monitor_watchhamster.py stop' 명령을 사용하세요.")
        
        confirm = input("\n계속하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            self.ui.console.print("[dim]취소됨[/dim]")
            return False
        
        if not self.core._initialized:
            await self.core.initialize()
        
        success = await self.core.start_monitoring(MonitoringMode.SERVICE_24H)
        
        if success:
            self.ui.print_success(
                "24시간 서비스 시작 완료!",
                "백그라운드에서 실행 중입니다."
            )
        else:
            self.ui.print_error("24시간 서비스 시작 실패")
        
        return success

    def show_settings(self):
        """설정 표시"""
        self.ui.print_header("시스템 설정", style="info")
        
        settings = {
            "프로젝트 경로": str(backend_dir),
            "상태 파일": "data/watchhamster_state.json",
            "로그 파일": "logs/watchhamster.log",
            "헬스 체크 간격": "5초",
        }
        
        self.ui.print_status(settings)
        
        self.ui.console.print("\n[dim]설정 변경은 추후 구현 예정입니다.[/dim]")

    async def handle_menu_choice(self, choice: str):
        """메뉴 선택 처리"""
        if choice == "1":
            await self.run_individual_monitor("newyork-market-watch")
        elif choice == "2":
            await self.run_individual_monitor("kospi-close")
        elif choice == "3":
            await self.run_individual_monitor("exchange-rate")
        elif choice == "4":
            await self.run_integrated_monitoring()
        elif choice == "5":
            await self.run_smart_monitoring()
        elif choice == "6":
            await self.start_24h_service()
        elif choice == "7":
            self.show_settings()
        elif choice == "8" or choice == "0":
            return False
        else:
            self.ui.print_error("잘못된 선택입니다.")
        
        return True

    async def run(self):
        """메인 실행 루프"""
        self.running = True
        
        # 시스템 초기화
        self.clear_screen()
        self.print_banner()
        
        with self.indicator.start_spinner_sync("시스템 초기화 중...", style="dots"):
            await self.core.initialize()
        
        self.ui.print_success("시스템 초기화 완료!")
        
        # 메인 루프
        while self.running:
            try:
                self.ui.print_separator()
                self.print_main_menu()
                
                choice = input("\n선택하세요 (1-8): ").strip()
                
                if not await self.handle_menu_choice(choice):
                    break
                
                input("\n계속하려면 Enter를 누르세요...")
                self.clear_screen()
                self.print_banner()
                
            except KeyboardInterrupt:
                self.ui.console.print("\n\n[yellow]중단됨[/yellow]")
                break
            except Exception as e:
                self.ui.print_error(f"오류 발생: {e}")
                import traceback
                traceback.print_exc()
                input("\n계속하려면 Enter를 누르세요...")
        
        # 종료
        self.ui.print_info("시스템 종료 중...")
        await self.core.shutdown()
        self.ui.print_success("안전하게 종료되었습니다. 👋")


async def main():
    """메인 함수"""
    cli = WatchHamsterCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
        sys.exit(0)
