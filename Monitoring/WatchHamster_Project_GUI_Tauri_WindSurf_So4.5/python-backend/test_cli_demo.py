#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI 데모 스크립트
run_monitor.py의 주요 기능을 자동으로 시연
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ui.console_ui import ColorfulConsoleUI
from ui.status_formatter import StatusFormatter
from core.watchhamster_core import WatchHamsterCore, MonitoringMode


async def demo_cli():
    """CLI 데모"""
    ui = ColorfulConsoleUI()
    formatter = StatusFormatter()
    core = WatchHamsterCore()
    
    # 배너
    ui.clear()
    ui.print_banner("🐹 POSCO WatchHamster v3.0 - CLI 데모")
    
    # 메뉴 표시
    ui.print_header("메인 메뉴", style="info")
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
    ui.print_menu(options, current_selection=0)
    
    # 시스템 초기화
    ui.print_separator()
    ui.print_info("시스템 초기화 중...")
    success = await core.initialize()
    
    if success:
        ui.print_success("시스템 초기화 완료!")
    else:
        ui.print_error("초기화 실패")
        return
    
    # 개별 모니터 시작 데모
    ui.print_separator()
    ui.print_info("개별 모니터 시작 데모...")
    
    success = await core.start_monitoring(
        MonitoringMode.INDIVIDUAL,
        monitors=["newyork-market-watch"]
    )
    
    if success:
        # 상태 표시
        await asyncio.sleep(1)
        status = await core.get_system_status()
        
        ui.console.print("\n[bold cyan]현재 시스템 상태:[/bold cyan]")
        status_dict = {
            "시스템 상태": status.status.value,
            "모드": status.mode.value if status.mode else "N/A",
            "활성 모니터": len(status.active_monitors),
            "정상 모니터": status.healthy_monitors,
            "총 모니터": status.total_monitors,
            "가동 시간": f"{status.uptime_seconds:.1f}초",
        }
        ui.print_status(status_dict, highlight=True)
        
        # 모니터 상태 테이블
        if status.metadata.get("processes"):
            ui.console.print("\n[bold cyan]모니터 상세 상태:[/bold cyan]")
            monitors_info = status.metadata["processes"]
            monitor_table = formatter.format_monitor_table(monitors_info)
            ui.console.print(monitor_table)
        
        ui.print_success("모니터링 실행 중!")
        
        # 짧은 실행
        ui.console.print("\n[dim]3초 후 자동 중지...[/dim]")
        await asyncio.sleep(3)
        
        # 중지
        await core.stop_monitoring()
        ui.print_info("모니터링 중지 완료")
    
    # 시스템 리소스 표시
    ui.print_separator()
    ui.console.print("\n[bold cyan]시스템 리소스:[/bold cyan]")
    
    import psutil
    resources = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
    }
    resource_text = formatter.format_system_resources(resources)
    ui.console.print(resource_text)
    
    # 종료
    ui.print_separator()
    ui.print_info("시스템 종료 중...")
    await core.shutdown()
    ui.print_success("데모 완료! 👋")
    
    # 사용 방법 안내
    ui.print_separator()
    ui.console.print("\n[bold yellow]실제 사용 방법:[/bold yellow]")
    ui.console.print("1. 대화형 모드:")
    ui.console.print("   [cyan]python3 cli/run_monitor.py[/cyan]")
    ui.console.print("\n2. 24시간 서비스:")
    ui.console.print("   [cyan]python3 cli/monitor_watchhamster.py start[/cyan]")
    ui.console.print("   [cyan]python3 cli/monitor_watchhamster.py status[/cyan]")
    ui.console.print("   [cyan]python3 cli/monitor_watchhamster.py stop[/cyan]")
    ui.console.print()


async def main():
    try:
        await demo_cli()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
