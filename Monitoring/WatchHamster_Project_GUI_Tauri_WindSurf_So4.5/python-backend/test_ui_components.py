#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 컴포넌트 테스트 스크립트
ColorfulConsoleUI, StatusFormatter, ProgressIndicator 동작 확인
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from ui.console_ui import ColorfulConsoleUI
from ui.status_formatter import StatusFormatter
from ui.progress_indicator import ProgressIndicator


def test_console_ui():
    """ColorfulConsoleUI 테스트"""
    print("\n" + "="*60)
    print("🧪 ColorfulConsoleUI 테스트")
    print("="*60 + "\n")
    
    ui = ColorfulConsoleUI()
    
    # 배너
    ui.print_banner("🎨 WatchHamster UI 테스트")
    
    # 헤더
    ui.print_header("시스템 상태", style="success", subtitle="모든 시스템 정상 작동 중")
    
    # 상태 출력
    status_data = {
        "시스템 상태": "running",
        "활성 모니터": 3,
        "헬스 체크": "healthy",
        "오류 카운트": 0,
    }
    ui.print_status(status_data, highlight=True)
    
    # 메뉴
    ui.print_menu([
        "뉴욕마켓워치 모니터링",
        "증시마감 모니터링",
        "서환마감 모니터링",
        "통합 모니터링",
        "종료"
    ], current_selection=0)
    
    # 메시지들
    ui.print_success("모니터링 시작 성공!", "모든 프로세스가 정상적으로 시작되었습니다.")
    ui.print_warning("CPU 사용률 높음", "현재 CPU 사용률: 85%")
    ui.print_info("다음 체크 예정", "5분 후 자동 체크가 실행됩니다.")
    
    # 테이블
    ui.print_table(
        headers=["모니터", "상태", "헬스", "오류"],
        rows=[
            ["뉴욕마켓워치", "running", "healthy", "0"],
            ["증시마감", "running", "healthy", "0"],
            ["서환마감", "stopped", "unknown", "2"],
        ],
        title="모니터 현황",
        highlight_row=0
    )
    
    # 진행 상황
    ui.print_progress_summary(75, 100, "데이터 처리 중...")
    
    return True


def test_status_formatter():
    """StatusFormatter 테스트"""
    print("\n" + "="*60)
    print("🧪 StatusFormatter 테스트")
    print("="*60 + "\n")
    
    formatter = StatusFormatter()
    console = ColorfulConsoleUI().console
    
    # 모니터 상태 포맷팅
    monitors = {
        "newyork-market": {
            "status": "running",
            "health": "healthy",
            "restart_count": 0,
            "error_count": 0,
            "last_check": datetime.now()
        },
        "kospi-close": {
            "status": "stopped",
            "health": "unknown",
            "restart_count": 2,
            "error_count": 3,
            "last_check": datetime.now() - timedelta(hours=1)
        }
    }
    
    console.print("\n[bold cyan]모니터 상태 (텍스트):[/bold cyan]")
    status_text = formatter.format_monitor_status(monitors)
    console.print(status_text)
    
    console.print("\n[bold cyan]모니터 상태 (테이블):[/bold cyan]")
    status_table = formatter.format_monitor_table(monitors)
    console.print(status_table)
    
    # 시간 정보
    console.print("\n[bold cyan]시간 정보:[/bold cyan]")
    time_info = formatter.format_time_info(
        datetime.now(),
        datetime.now() + timedelta(minutes=30)
    )
    console.print(time_info)
    
    # 시스템 리소스
    console.print("\n[bold cyan]시스템 리소스:[/bold cyan]")
    resources = {
        "cpu_percent": 45.2,
        "memory_percent": 62.8,
        "disk_percent": 78.5,
    }
    resource_text = formatter.format_system_resources(resources)
    console.print(resource_text)
    
    # 성공 메시지
    console.print("\n[bold cyan]성공 메시지:[/bold cyan]")
    success_msg = formatter.format_success_message(
        "모니터링 시작",
        {"모니터 수": 3, "시작 시간": "12:30:45"}
    )
    console.print(success_msg)
    
    return True


async def test_progress_indicator():
    """ProgressIndicator 테스트"""
    print("\n" + "="*60)
    print("🧪 ProgressIndicator 테스트")
    print("="*60 + "\n")
    
    indicator = ProgressIndicator()
    
    # 단계별 진행
    print("\n[단계별 진행 표시]")
    for i in range(1, 6):
        indicator.print_step(i, 5, f"단계 {i} 처리 중...")
        await asyncio.sleep(0.3)
    
    # 완료 메시지
    indicator.print_completion("모든 단계 완료", elapsed_time=1.5)
    
    # 프로그레스 바
    print("\n[프로그레스 바 테스트]")
    
    async def dummy_task():
        await asyncio.sleep(0.2)
    
    tasks = [dummy_task() for _ in range(5)]
    await indicator.show_progress(tasks, "작업 처리 중...", show_time=False)
    
    print("\n✅ ProgressIndicator 테스트 완료")
    
    return True


async def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("🚀 WatchHamster UI 컴포넌트 테스트 시작")
    print("="*60)
    
    results = []
    
    try:
        results.append(("ColorfulConsoleUI", test_console_ui()))
        results.append(("StatusFormatter", test_status_formatter()))
        results.append(("ProgressIndicator", await test_progress_indicator()))
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 모든 UI 테스트 통과!")
    else:
        print("⚠️  일부 테스트 실패")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
