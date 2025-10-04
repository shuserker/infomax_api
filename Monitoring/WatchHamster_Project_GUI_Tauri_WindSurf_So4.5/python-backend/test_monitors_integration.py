#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모니터 통합 테스트
개별 모니터와 WatchHamsterCore 통합 확인
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ui.console_ui import ColorfulConsoleUI
from ui.status_formatter import StatusFormatter
from core.watchhamster_core import WatchHamsterCore, MonitoringMode
from core.monitors import NewYorkMarketMonitor, KospiCloseMonitor, ExchangeRateMonitor


async def test_individual_monitors():
    """개별 모니터 테스트"""
    ui = ColorfulConsoleUI()
    
    ui.print_banner("🧪 개별 모니터 테스트")
    
    monitors = [
        ("뉴욕마켓워치", NewYorkMarketMonitor()),
        ("증시마감", KospiCloseMonitor()),
        ("서환마감", ExchangeRateMonitor())
    ]
    
    for name, monitor in monitors:
        ui.print_separator()
        ui.print_info(f"{name} 모니터 테스트 중...")
        
        try:
            result = await monitor.run()
            
            if result["success"]:
                ui.print_success(
                    f"{name} 모니터 성공!",
                    f"데이터: {result['data'].get('title', 'N/A')}"
                )
                
                # 데이터 표시
                if result["data"]:
                    ui.console.print("\n[bold cyan]파싱 결과:[/bold cyan]")
                    for key, value in list(result["data"].items())[:5]:
                        ui.console.print(f"  • {key}: {value}")
            else:
                ui.print_error(
                    f"{name} 모니터 실패",
                    result.get("error", "Unknown error")
                )
        except Exception as e:
            ui.print_error(f"{name} 모니터 오류", str(e))
    
    return True


async def test_core_integration():
    """Core 통합 테스트"""
    ui = ColorfulConsoleUI()
    formatter = StatusFormatter()
    
    ui.print_separator("=")
    ui.print_banner("🧪 WatchHamsterCore 통합 테스트")
    
    core = WatchHamsterCore()
    
    # 초기화
    ui.print_info("시스템 초기화 중...")
    success = await core.initialize()
    
    if not success:
        ui.print_error("초기화 실패")
        return False
    
    ui.print_success("초기화 완료!")
    
    # 개별 모니터 시작
    ui.print_separator()
    ui.print_info("개별 모니터 시작 중...")
    
    success = await core.start_monitoring(
        MonitoringMode.INDIVIDUAL,
        monitors=["newyork-market-watch", "kospi-close"]
    )
    
    if success:
        ui.print_success("모니터링 시작 완료!")
        
        # 상태 확인
        await asyncio.sleep(2)
        status = await core.get_system_status()
        
        ui.console.print("\n[bold cyan]시스템 상태:[/bold cyan]")
        status_dict = {
            "시스템 상태": status.status.value,
            "모드": status.mode.value if status.mode else "N/A",
            "활성 모니터": len(status.active_monitors),
            "정상 모니터": status.healthy_monitors,
            "총 모니터": status.total_monitors,
            "가동 시간": f"{status.uptime_seconds:.1f}초",
        }
        ui.print_status(status_dict, highlight=True)
        
        # 모니터 상세 상태
        if status.metadata.get("processes"):
            ui.console.print("\n[bold cyan]모니터 상세:[/bold cyan]")
            monitors_info = status.metadata["processes"]
            monitor_table = formatter.format_monitor_table(monitors_info)
            ui.console.print(monitor_table)
        
        # 5초 실행
        ui.console.print("\n[dim]5초 동안 실행 후 자동 중지...[/dim]")
        await asyncio.sleep(5)
        
        # 중지
        await core.stop_monitoring()
        ui.print_info("모니터링 중지 완료")
    else:
        ui.print_error("모니터링 시작 실패")
    
    # 종료
    await core.shutdown()
    ui.print_success("시스템 종료 완료")
    
    return success


async def main():
    """메인 테스트"""
    ui = ColorfulConsoleUI()
    
    ui.clear()
    ui.print_banner("🚀 WatchHamster 모니터 통합 테스트")
    
    results = []
    
    try:
        # 개별 모니터 테스트
        ui.console.print("\n[bold yellow]Phase 1: 개별 모니터 테스트[/bold yellow]")
        result1 = await test_individual_monitors()
        results.append(("개별 모니터", result1))
        
        # Core 통합 테스트
        ui.console.print("\n[bold yellow]Phase 2: Core 통합 테스트[/bold yellow]")
        result2 = await test_core_integration()
        results.append(("Core 통합", result2))
        
    except Exception as e:
        ui.print_error(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 결과 요약
    ui.print_separator("=")
    ui.console.print("\n[bold cyan]📊 테스트 결과 요약[/bold cyan]\n")
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        ui.console.print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    ui.print_separator("=")
    if all_passed:
        ui.print_success("🎉 모든 통합 테스트 통과!")
    else:
        ui.print_warning("⚠️  일부 테스트 실패")
    
    return all_passed


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
